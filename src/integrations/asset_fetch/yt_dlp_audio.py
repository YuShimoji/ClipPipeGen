"""yt-dlp source-audio URL fetch adapter for INT-02e.

This module is the only place that should call yt-dlp for source audio. It
downloads one temporary media file, asks the existing FFmpeg adapter to
normalize it to source.wav, and then lets the temporary media disappear. It
does not fetch source video, run STT, cut, concatenate, render, encode, or make
creative / rights decisions.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol
from urllib.parse import urlsplit

from . import ffmpeg_audio

SUBKIND = ffmpeg_audio.SUBKIND
PROVIDER = "yt-dlp"
RETRIEVAL_METHOD = "asset_fetch_yt_dlp_audio"
YTDLP_ENV_VAR = "CLIPPIPE_YTDLP"
COMMAND_TIMEOUT_SECONDS = 1800
VERSION_TIMEOUT_SECONDS = 15


class YtDlpAudioError(Exception):
    """Raised when yt-dlp discovery, download, or normalization orchestration fails."""


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
class YtDlpAudioPlan:
    yt_dlp_path: str | None
    yt_dlp_path_source: str | None
    ffmpeg_plan: ffmpeg_audio.FfmpegPlan
    source_url: str
    output_path: str
    intermediate_template: str
    yt_dlp_command: list[str] | None
    yt_dlp_command_summary: str | None
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "yt_dlp_path": self.yt_dlp_path,
            "yt_dlp_path_source": self.yt_dlp_path_source,
            "ffmpeg_plan": self.ffmpeg_plan.to_dict(),
            "source_url": scrub_url_for_readback(self.source_url),
            "output_path": self.output_path,
            "intermediate_template": self.intermediate_template,
            "yt_dlp_command": _scrub_command_for_readback(self.yt_dlp_command),
            "yt_dlp_command_summary": self.yt_dlp_command_summary,
            "audio_format": audio_format(),
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class YtDlpAudioResult:
    yt_dlp_path: str
    yt_dlp_path_source: str
    yt_dlp_version: str
    yt_dlp_command: list[str]
    yt_dlp_command_summary: str
    yt_dlp_exit_code: int
    yt_dlp_stderr_digest: dict[str, Any]
    downloaded_intermediate_name: str
    downloaded_intermediate_byte_size: int
    intermediate_retained: bool
    ffmpeg_result: ffmpeg_audio.NormalizeResult
    stderr_digest: dict[str, Any]
    warnings: list[str]


def audio_format() -> dict[str, Any]:
    return ffmpeg_audio.audio_format()


def scrub_url_for_readback(url: str | None) -> str | None:
    """Return a URL suitable for receipts/logs without query secrets."""
    if not url:
        return url
    try:
        parts = urlsplit(url)
    except ValueError:
        return _scrub_secretish_text(url)
    if parts.scheme not in {"http", "https"}:
        return _scrub_secretish_text(url)

    netloc = parts.netloc
    if "@" in netloc:
        netloc = "<userinfo:redacted>@" + netloc.rsplit("@", 1)[1]
    out = f"{parts.scheme}://{netloc}{parts.path}"
    if parts.query:
        out += "?<query:redacted>"
    if parts.fragment:
        out += "#<fragment:redacted>"
    return _scrub_secretish_text(out)


def discover_yt_dlp(
    *,
    yt_dlp_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Resolve yt-dlp path without executing it.

    Order: explicit --yt-dlp-path, CLIPPIPE_YTDLP, PATH.
    """
    if yt_dlp_path:
        return str(yt_dlp_path), "argument"
    lookup_env = env if env is not None else os.environ
    env_path = lookup_env.get(YTDLP_ENV_VAR)
    if env_path:
        return env_path, "env:CLIPPIPE_YTDLP"
    path = shutil.which("yt-dlp", path=lookup_env.get("PATH"))
    if path:
        return path, "PATH"
    return None, None


def build_plan(
    *,
    source_url: str,
    output_path: str | Path,
    yt_dlp_path: str | Path | None = None,
    ffmpeg_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> YtDlpAudioPlan:
    """Build a dry-run-safe command plan without spawning subprocesses."""
    resolved_ytdlp, ytdlp_source = discover_yt_dlp(
        yt_dlp_path=yt_dlp_path,
        env=env,
    )
    intermediate_template = "<temporary-directory>/source.%(ext)s"
    output_display = str(output_path).replace("\\", "/")
    ffmpeg_plan = ffmpeg_audio.build_plan(
        input_path="<downloaded-intermediate>",
        output_path=output_path,
        ffmpeg_path=ffmpeg_path,
        env=env,
    )
    warnings = [
        "yt-dlp-audio dry-run does not call network or subprocesses",
        "downloaded intermediate media is temporary and retained=false",
    ]
    if resolved_ytdlp is None:
        warnings.append(
            f"yt-dlp not found via --yt-dlp-path, {YTDLP_ENV_VAR}, or PATH"
        )
        return YtDlpAudioPlan(
            yt_dlp_path=None,
            yt_dlp_path_source=None,
            ffmpeg_plan=ffmpeg_plan,
            source_url=source_url,
            output_path=output_display,
            intermediate_template=intermediate_template,
            yt_dlp_command=None,
            yt_dlp_command_summary=None,
            warnings=warnings,
        )
    command = _download_command(
        resolved_ytdlp,
        source_url,
        intermediate_template,
    )
    return YtDlpAudioPlan(
        yt_dlp_path=resolved_ytdlp,
        yt_dlp_path_source=ytdlp_source,
        ffmpeg_plan=ffmpeg_plan,
        source_url=source_url,
        output_path=output_display,
        intermediate_template=intermediate_template,
        yt_dlp_command=command,
        yt_dlp_command_summary=_command_summary(command),
        warnings=warnings,
    )


def fetch_url_audio(
    *,
    source_url: str,
    output_path: str | Path,
    yt_dlp_path: str | Path | None = None,
    ffmpeg_path: str | Path | None = None,
    runner: Runner = subprocess.run,
    env: Mapping[str, str] | None = None,
) -> YtDlpAudioResult:
    """Fetch one URL with yt-dlp and normalize it to source.wav."""
    _validate_source_url(source_url)
    output_file = Path(output_path)
    plan = build_plan(
        source_url=source_url,
        output_path=output_file,
        yt_dlp_path=yt_dlp_path,
        ffmpeg_path=ffmpeg_path,
        env=env,
    )
    if plan.yt_dlp_path is None:
        raise YtDlpAudioError("yt-dlp not found")
    if plan.ffmpeg_plan.ffmpeg_path is None:
        raise ffmpeg_audio.FfmpegError("ffmpeg not found")

    ytdlp_version = _read_ytdlp_version(plan.yt_dlp_path, runner=runner)
    warnings = list(plan.warnings)

    with tempfile.TemporaryDirectory(prefix="clippipegen_ytdlp_audio_") as tmp:
        tmp_dir = Path(tmp)
        intermediate_template = str(tmp_dir / "source.%(ext)s")
        command = _download_command(plan.yt_dlp_path, source_url, intermediate_template)
        try:
            download_result = runner(
                command,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            if output_file.exists():
                output_file.unlink()
            raise YtDlpAudioError(
                f"yt-dlp download failed before exit code: {exc}"
            ) from exc

        ytdlp_digest = ffmpeg_audio.build_stderr_digest(download_result.stderr)
        if download_result.returncode != 0:
            if output_file.exists():
                output_file.unlink()
            raise YtDlpAudioError(
                "yt-dlp download failed: "
                f"exit_code={download_result.returncode}; "
                f"stderr_sha256={ytdlp_digest['sha256']}"
            )

        intermediate, selection_warnings = _select_intermediate_file(tmp_dir)
        warnings.extend(selection_warnings)
        intermediate_name = intermediate.name
        intermediate_byte_size = intermediate.stat().st_size

        normalize_result = ffmpeg_audio.normalize_local_media_audio(
            input_path=intermediate,
            output_path=output_file,
            ffmpeg_path=ffmpeg_path,
            runner=runner,
            env=env,
        )
        warnings.extend(normalize_result.warnings)
        warnings.append("downloaded intermediate media deleted after normalization")

    ffmpeg_tail = ""
    if normalize_result.stderr_digest:
        ffmpeg_tail = str(normalize_result.stderr_digest.get("tail") or "")
    combined_digest = ffmpeg_audio.build_stderr_digest(
        f"yt-dlp:\n{download_result.stderr or ''}\nffmpeg:\n{ffmpeg_tail}"
    )

    return YtDlpAudioResult(
        yt_dlp_path=plan.yt_dlp_path,
        yt_dlp_path_source=plan.yt_dlp_path_source or "unknown",
        yt_dlp_version=ytdlp_version,
        yt_dlp_command=command,
        yt_dlp_command_summary=_command_summary(command),
        yt_dlp_exit_code=download_result.returncode,
        yt_dlp_stderr_digest=ytdlp_digest,
        downloaded_intermediate_name=intermediate_name,
        downloaded_intermediate_byte_size=intermediate_byte_size,
        intermediate_retained=False,
        ffmpeg_result=normalize_result,
        stderr_digest=combined_digest,
        warnings=warnings,
    )


def _validate_source_url(source_url: str) -> None:
    if not re.match(r"^https?://", source_url):
        raise YtDlpAudioError("--source-url must be an http(s) URL for yt-dlp-audio")


def _read_ytdlp_version(ytdlp_path: str, *, runner: Runner) -> str:
    try:
        result = runner(
            [ytdlp_path, "--version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise YtDlpAudioError(
            f"yt-dlp version check failed before exit code: {exc}"
        ) from exc
    if result.returncode != 0:
        digest = ffmpeg_audio.build_stderr_digest(result.stderr)
        raise YtDlpAudioError(
            "yt-dlp version check failed: "
            f"exit_code={result.returncode}; stderr_sha256={digest['sha256']}"
        )
    first_line = (result.stdout or "").splitlines()[0:1]
    if not first_line:
        return "unknown"
    return first_line[0].strip() or "unknown"


def _download_command(
    yt_dlp_path: str,
    source_url: str,
    output_template: str | Path,
) -> list[str]:
    return [
        yt_dlp_path,
        "--no-playlist",
        "--no-progress",
        "-f",
        "bestaudio/best",
        "-o",
        str(output_template),
        source_url,
    ]


def _select_intermediate_file(tmp_dir: Path) -> tuple[Path, list[str]]:
    candidates = [
        p
        for p in tmp_dir.rglob("*")
        if p.is_file() and not p.name.endswith((".part", ".ytdl"))
    ]
    if not candidates:
        raise YtDlpAudioError("yt-dlp reported success but no intermediate media file was created")
    if len(candidates) == 1:
        return candidates[0], []
    chosen = max(candidates, key=lambda p: (p.stat().st_size, p.stat().st_mtime))
    return chosen, [
        "yt-dlp produced multiple files; selected the largest/newest intermediate for normalization"
    ]


def _command_summary(command: list[str]) -> str:
    return " ".join(_summary_part(p) for p in command)


def _scrub_command_for_readback(command: list[str] | None) -> list[str] | None:
    if command is None:
        return None
    return [scrub_url_for_readback(p) or "" if re.match(r"https?://", p) else p for p in command]


def _summary_part(part: str) -> str:
    if re.match(r"https?://", part):
        return "<url>"
    normalized = str(part).replace("\\", "/")
    return _scrub_secretish_text(normalized)


def _scrub_secretish_text(text: str) -> str:
    out = re.sub(
        r"(?i)(token|api[_-]?key|authorization|password|signature|sig)=\S+",
        r"\1=<redacted>",
        text,
    )
    out = re.sub(r"(?i)(bearer)\s+[A-Za-z0-9._\-]+", r"\1 <redacted>", out)
    return out
