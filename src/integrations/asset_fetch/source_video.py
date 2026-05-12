"""Source-video acquisition adapter.

This module is limited to acquiring/registering source video material for
future timeline/render work. The local-media path copies an existing video file
into the episode material directory and probes metadata. It does not cut,
concatenate, render, encode, run STT, or decide creative/publishing acceptance.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Protocol

from . import ffmpeg_audio

SUBKIND = "source_video_original"
PROVIDER = "local-media"
RETRIEVAL_METHOD = "asset_fetch_local_media_video"
FFPROBE_ENV_VAR = "CLIPPIPE_FFPROBE"
COMMAND_TIMEOUT_SECONDS = 120
VERSION_TIMEOUT_SECONDS = 15

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mkv",
    ".webm",
    ".avi",
    ".m4v",
}


class SourceVideoError(Exception):
    """Raised when source-video acquisition or metadata probing fails."""


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
class ProbePlan:
    ffprobe_path: str | None
    ffprobe_path_source: str | None
    input_path: str
    command: list[str] | None
    command_summary: str | None
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ffprobe_path": self.ffprobe_path,
            "ffprobe_path_source": self.ffprobe_path_source,
            "input_path": self.input_path,
            "command": self.command,
            "command_summary": self.command_summary,
            "metadata_fields": [
                "duration_seconds",
                "container",
                "video_codec",
                "audio_codec",
                "resolution",
                "fps",
                "stream_count",
            ],
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class ProbeResult:
    ffprobe_path: str
    ffprobe_path_source: str
    ffprobe_version: str
    command: list[str]
    command_summary: str
    exit_code: int
    stderr_digest: dict[str, Any]
    metadata: dict[str, Any]
    warnings: list[str]


@dataclass(frozen=True)
class LocalVideoResult:
    source_path: str
    output_path: str
    copied: bool
    byte_size: int
    probe_result: ProbeResult
    warnings: list[str]

    @property
    def metadata(self) -> dict[str, Any]:
        return self.probe_result.metadata


def output_filename_for(source_path: str | Path) -> str:
    suffix = Path(source_path).suffix.lower()
    if suffix not in VIDEO_EXTENSIONS:
        suffix = ".mp4"
    return f"source_video{suffix}"


def discover_ffprobe(
    *,
    ffprobe_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Resolve FFprobe path without executing it.

    Order: explicit --ffprobe-path, CLIPPIPE_FFPROBE, PATH.
    """
    if ffprobe_path:
        return str(ffprobe_path), "argument"
    lookup_env = env if env is not None else os.environ
    env_path = lookup_env.get(FFPROBE_ENV_VAR)
    if env_path:
        return env_path, f"env:{FFPROBE_ENV_VAR}"
    path = shutil.which("ffprobe", path=lookup_env.get("PATH"))
    if path:
        return path, "PATH"
    return None, None


def build_probe_plan(
    *,
    input_path: str | Path,
    ffprobe_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> ProbePlan:
    resolved, source = discover_ffprobe(ffprobe_path=ffprobe_path, env=env)
    input_display = str(input_path).replace("\\", "/")
    warnings = [
        "ffprobe metadata readback only; this does not render or encode video",
    ]
    if resolved is None:
        warnings.append(
            f"ffprobe not found via --ffprobe-path, {FFPROBE_ENV_VAR}, or PATH"
        )
        return ProbePlan(
            ffprobe_path=None,
            ffprobe_path_source=None,
            input_path=input_display,
            command=None,
            command_summary=None,
            warnings=warnings,
        )
    command = _probe_command(resolved, input_path)
    return ProbePlan(
        ffprobe_path=resolved,
        ffprobe_path_source=source,
        input_path=input_display,
        command=command,
        command_summary=_command_summary(command),
        warnings=warnings,
    )


def copy_local_media_video(
    *,
    input_path: str | Path,
    output_path: str | Path,
    ffprobe_path: str | Path | None = None,
    runner: Runner = subprocess.run,
    env: Mapping[str, str] | None = None,
) -> LocalVideoResult:
    """Copy one existing local video into the episode material directory."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    if not input_file.exists() or not input_file.is_file():
        raise SourceVideoError(f"local video file not found: {input_file}")

    plan = build_probe_plan(
        input_path=input_file,
        ffprobe_path=ffprobe_path,
        env=env,
    )
    if plan.ffprobe_path is None:
        raise SourceVideoError("ffprobe not found")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(input_file, output_file)
    except OSError as exc:
        if output_file.exists():
            output_file.unlink()
        raise SourceVideoError(f"source video copy failed: {exc}") from exc

    try:
        probe_result = probe_video(
            input_path=output_file,
            ffprobe_path=plan.ffprobe_path,
            ffprobe_path_source=plan.ffprobe_path_source or "unknown",
            runner=runner,
        )
    except SourceVideoError:
        if output_file.exists():
            output_file.unlink()
        raise

    if probe_result.metadata.get("stream_counts", {}).get("video", 0) <= 0:
        if output_file.exists():
            output_file.unlink()
        raise SourceVideoError("ffprobe found no video stream in source video")

    warnings = [
        "local-media-video copies the source file without render/encode",
        "source video acquisition is not production/creative/publish acceptance",
        *probe_result.warnings,
    ]
    return LocalVideoResult(
        source_path=str(input_file).replace("\\", "/"),
        output_path=str(output_file).replace("\\", "/"),
        copied=True,
        byte_size=output_file.stat().st_size,
        probe_result=probe_result,
        warnings=warnings,
    )


def probe_video(
    *,
    input_path: str | Path,
    ffprobe_path: str,
    ffprobe_path_source: str,
    runner: Runner = subprocess.run,
) -> ProbeResult:
    version = _read_ffprobe_version(ffprobe_path, runner=runner)
    command = _probe_command(ffprobe_path, input_path)
    try:
        result = runner(
            command,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SourceVideoError(f"ffprobe failed before exit code: {exc}") from exc
    stderr_digest = ffmpeg_audio.build_stderr_digest(result.stderr)
    if result.returncode != 0:
        raise SourceVideoError(
            "ffprobe metadata read failed: "
            f"exit_code={result.returncode}; stderr_sha256={stderr_digest['sha256']}"
        )
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise SourceVideoError(f"ffprobe returned invalid JSON: {exc}") from exc

    metadata, warnings = _metadata_from_ffprobe(payload)
    return ProbeResult(
        ffprobe_path=ffprobe_path,
        ffprobe_path_source=ffprobe_path_source,
        ffprobe_version=version,
        command=command,
        command_summary=_command_summary(command),
        exit_code=result.returncode,
        stderr_digest=stderr_digest,
        metadata=metadata,
        warnings=warnings,
    )


def _read_ffprobe_version(ffprobe_path: str, *, runner: Runner) -> str:
    try:
        result = runner(
            [ffprobe_path, "-version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SourceVideoError(
            f"ffprobe version check failed before exit code: {exc}"
        ) from exc
    if result.returncode != 0:
        digest = ffmpeg_audio.build_stderr_digest(result.stderr)
        raise SourceVideoError(
            "ffprobe version check failed: "
            f"exit_code={result.returncode}; stderr_sha256={digest['sha256']}"
        )
    first_line = (result.stdout or "").splitlines()[0:1]
    return first_line[0].strip() if first_line else "unknown"


def _probe_command(ffprobe_path: str, input_path: str | Path) -> list[str]:
    return [
        ffprobe_path,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(input_path),
    ]


def _metadata_from_ffprobe(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    streams = payload.get("streams") if isinstance(payload.get("streams"), list) else []
    fmt = payload.get("format") if isinstance(payload.get("format"), dict) else {}
    video_streams = [s for s in streams if isinstance(s, dict) and s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if isinstance(s, dict) and s.get("codec_type") == "audio"]
    video = video_streams[0] if video_streams else {}
    audio = audio_streams[0] if audio_streams else {}
    width = _int_or_none(video.get("width"))
    height = _int_or_none(video.get("height"))
    duration = _float_or_none(fmt.get("duration")) or _float_or_none(video.get("duration"))
    frame_rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
    fps = _fps_from_rate(frame_rate)
    metadata = {
        "duration_seconds": duration,
        "container": fmt.get("format_name") or None,
        "container_long_name": fmt.get("format_long_name") or None,
        "video_codec": video.get("codec_name") or None,
        "video_codec_long_name": video.get("codec_long_name") or None,
        "audio_codec": audio.get("codec_name") or None,
        "audio_codec_long_name": audio.get("codec_long_name") or None,
        "width": width,
        "height": height,
        "resolution": f"{width}x{height}" if width and height else None,
        "fps": fps,
        "frame_rate": frame_rate or None,
        "stream_count": len(streams),
        "stream_counts": {
            "video": len(video_streams),
            "audio": len(audio_streams),
            "other": max(0, len(streams) - len(video_streams) - len(audio_streams)),
        },
    }
    warnings: list[str] = []
    for field in (
        "duration_seconds",
        "container",
        "video_codec",
        "resolution",
        "fps",
    ):
        if metadata.get(field) in {None, ""}:
            warnings.append(f"video metadata field missing: {field}")
    if not audio_streams:
        warnings.append("source video has no audio stream")
    return metadata, warnings


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _fps_from_rate(value: Any) -> float | None:
    if not isinstance(value, str) or not value or value == "0/0":
        return None
    try:
        rate = Fraction(value)
    except (ValueError, ZeroDivisionError):
        return None
    if rate.denominator == 0:
        return None
    return round(float(rate), 6)


def _command_summary(command: list[str]) -> str:
    return " ".join(_summary_part(part) for part in command)


def _summary_part(part: str) -> str:
    if re.match(r"https?://", part):
        return "<url>"
    return str(part).replace("\\", "/")
