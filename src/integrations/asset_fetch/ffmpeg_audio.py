"""FFmpeg adapter for INT-02c local-media-audio normalization.

This module is the only place that should call FFmpeg for asset_fetch. It
normalizes an existing local media file into the source-audio contract. It does
not download, cut, concatenate, render, encode final videos, run STT, or make
editing decisions.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from . import fake_audio

SUBKIND = fake_audio.SUBKIND
PROVIDER = "local-media"
RETRIEVAL_METHOD = "asset_fetch_local_media_audio"
FFMPEG_ENV_VAR = "CLIPPIPE_FFMPEG"
COMMAND_TIMEOUT_SECONDS = 600
VERSION_TIMEOUT_SECONDS = 15
STDERR_TAIL_CHARS = 800


class FfmpegError(Exception):
    """Raised when FFmpeg discovery or normalization fails."""


class Runner(Protocol):
    def __call__(
        self,
        args: list[str],
        *,
        capture_output: bool,
        text: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        ...


@dataclass(frozen=True)
class FfmpegPlan:
    ffmpeg_path: str | None
    path_source: str | None
    input_path: str
    output_path: str
    command: list[str] | None
    command_summary: str | None
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ffmpeg_path": self.ffmpeg_path,
            "path_source": self.path_source,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "command": self.command,
            "command_summary": self.command_summary,
            "audio_format": audio_format(),
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class NormalizeResult:
    ffmpeg_path: str
    ffmpeg_path_source: str
    ffmpeg_version: str
    command: list[str]
    command_summary: str
    exit_code: int
    stderr_digest: dict[str, Any] | None
    duration_seconds: float | None
    warnings: list[str]


def audio_format() -> dict[str, Any]:
    return {
        "container": "wav",
        "codec": "pcm_s16le",
        "sample_rate_hz": fake_audio.SAMPLE_RATE_HZ,
        "channels": fake_audio.CHANNELS,
        "sample_width_bytes": fake_audio.SAMPLE_WIDTH_BYTES,
        "duration_seconds": None,
    }


def build_plan(
    *,
    input_path: str | Path,
    output_path: str | Path,
    ffmpeg_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> FfmpegPlan:
    """Build a dry-run-safe FFmpeg command plan without spawning subprocesses."""
    resolved, source = discover_ffmpeg(ffmpeg_path=ffmpeg_path, env=env)
    warnings = [
        "input duration is not probed in INT-02c; "
        "output WAV duration is read after normalization"
    ]
    input_display = str(input_path).replace("\\", "/")
    output_display = str(output_path).replace("\\", "/")
    if resolved is None:
        warnings.append(
            f"ffmpeg not found via --ffmpeg-path, {FFMPEG_ENV_VAR}, or PATH"
        )
        return FfmpegPlan(
            ffmpeg_path=None,
            path_source=None,
            input_path=input_display,
            output_path=output_display,
            command=None,
            command_summary=None,
            warnings=warnings,
        )
    command = _normalize_command(resolved, input_path, output_path)
    return FfmpegPlan(
        ffmpeg_path=resolved,
        path_source=source,
        input_path=input_display,
        output_path=output_display,
        command=command,
        command_summary=_command_summary(command),
        warnings=warnings,
    )


def discover_ffmpeg(
    *,
    ffmpeg_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Resolve FFmpeg path without executing it.

    Order: explicit --ffmpeg-path, CLIPPIPE_FFMPEG, PATH.
    """
    if ffmpeg_path:
        return str(ffmpeg_path), "argument"
    lookup_env = env if env is not None else os.environ
    env_path = lookup_env.get(FFMPEG_ENV_VAR)
    if env_path:
        return env_path, "env:CLIPPIPE_FFMPEG"
    path = shutil.which("ffmpeg", path=lookup_env.get("PATH"))
    if path:
        return path, "PATH"
    return None, None


def normalize_local_media_audio(
    *,
    input_path: str | Path,
    output_path: str | Path,
    ffmpeg_path: str | Path | None = None,
    runner: Runner = subprocess.run,
    env: Mapping[str, str] | None = None,
) -> NormalizeResult:
    """Normalize one local media file to source.wav using FFmpeg."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    if not input_file.exists():
        raise FfmpegError(f"local media file not found: {input_file}")

    plan = build_plan(
        input_path=input_file,
        output_path=output_file,
        ffmpeg_path=ffmpeg_path,
        env=env,
    )
    if plan.ffmpeg_path is None or plan.command is None:
        raise FfmpegError("ffmpeg not found")

    version = _read_ffmpeg_version(plan.ffmpeg_path, runner=runner)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = runner(
            plan.command,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        if output_file.exists():
            output_file.unlink()
        raise FfmpegError(
            f"ffmpeg normalization failed before exit code: {exc}"
        ) from exc
    stderr_digest = build_stderr_digest(result.stderr)
    if result.returncode != 0:
        if output_file.exists():
            output_file.unlink()
        raise FfmpegError(
            "ffmpeg normalization failed: "
            f"exit_code={result.returncode}; stderr_sha256={stderr_digest['sha256']}"
        )
    if not output_file.exists():
        raise FfmpegError("ffmpeg reported success but output file was not created")

    duration = _read_wav_duration(output_file)
    warnings = list(plan.warnings)
    if duration is None:
        warnings.append("output WAV duration could not be read")

    return NormalizeResult(
        ffmpeg_path=plan.ffmpeg_path,
        ffmpeg_path_source=plan.path_source or "unknown",
        ffmpeg_version=version,
        command=plan.command,
        command_summary=plan.command_summary or _command_summary(plan.command),
        exit_code=result.returncode,
        stderr_digest=stderr_digest,
        duration_seconds=duration,
        warnings=warnings,
    )


def build_stderr_digest(stderr: str | None) -> dict[str, Any]:
    scrubbed = _scrub_secretish_text(stderr or "")
    tail = scrubbed[-STDERR_TAIL_CHARS:]
    return {
        "algorithm": "sha256",
        "sha256": hashlib.sha256(scrubbed.encode("utf-8")).hexdigest(),
        "tail": tail,
        "tail_chars": STDERR_TAIL_CHARS,
        "truncated": len(scrubbed) > STDERR_TAIL_CHARS,
    }


def _read_ffmpeg_version(ffmpeg_path: str, *, runner: Runner) -> str:
    try:
        result = runner(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise FfmpegError(
            f"ffmpeg version check failed before exit code: {exc}"
        ) from exc
    if result.returncode != 0:
        digest = build_stderr_digest(result.stderr)
        raise FfmpegError(
            "ffmpeg version check failed: "
            f"exit_code={result.returncode}; stderr_sha256={digest['sha256']}"
        )
    first_line = (result.stdout or "").splitlines()[0:1]
    if not first_line:
        return "unknown"
    return first_line[0].strip() or "unknown"


def _normalize_command(
    ffmpeg_path: str,
    input_path: str | Path,
    output_path: str | Path,
) -> list[str]:
    return [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        str(fake_audio.CHANNELS),
        "-ar",
        str(fake_audio.SAMPLE_RATE_HZ),
        "-sample_fmt",
        "s16",
        "-acodec",
        "pcm_s16le",
        str(output_path),
    ]


def _command_summary(command: list[str]) -> str:
    return " ".join(_summary_part(p) for p in command)


def _summary_part(part: str) -> str:
    if re.match(r"https?://", part):
        return "<url>"
    return str(part).replace("\\", "/")


def _scrub_secretish_text(text: str) -> str:
    out = re.sub(r"https?://\S+", "<url>", text)
    out = re.sub(
        r"(?i)(token|api[_-]?key|authorization|password)=\S+",
        r"\1=<redacted>",
        out,
    )
    out = re.sub(r"(?i)(bearer)\s+[A-Za-z0-9._\-]+", r"\1 <redacted>", out)
    return out


def _read_wav_duration(path: Path) -> float | None:
    try:
        with wave.open(str(path), "rb") as wav:
            framerate = wav.getframerate()
            if framerate <= 0:
                return None
            return wav.getnframes() / float(framerate)
    except (wave.Error, OSError, EOFError):
        return None
