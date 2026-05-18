"""yt-dlp source-video URL fetch adapter for INT-02h.

This module is the only place that should call yt-dlp for source video. It
downloads one media file from a URL into the episode material directory as
``source_video.<ext>`` and asks the existing FFprobe adapter to read back
metadata. It does not normalize, cut, concatenate, render, encode, run STT, or
make creative / rights decisions. INT-02g (`docs/YTDLP_VIDEO_SPEC.md`) fixes
the contract this adapter implements.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from . import ffmpeg_audio
from . import source_video as source_video_adapter
from .yt_dlp_audio import scrub_url_for_readback

SUBKIND = source_video_adapter.SUBKIND
PROVIDER = "yt-dlp"
RETRIEVAL_METHOD = "asset_fetch_yt_dlp_video"
YTDLP_ENV_VAR = "CLIPPIPE_YTDLP"
COMMAND_TIMEOUT_SECONDS = 1800
VERSION_TIMEOUT_SECONDS = 15

ALLOWED_CONTAINERS: tuple[str, ...] = ("mp4", "mkv", "webm")
DEFAULT_FORMAT_SELECTOR = (
    "best[ext=mp4]/best[ext=mkv]/best[ext=webm]/best"
)
OUTPUT_BASENAME = "source_video"
OUTPUT_TEMPLATE_SUFFIX = "source_video.%(ext)s"
CHOSEN_FORMAT_SEPARATOR = "\t"
CHOSEN_FORMAT_MARKER = "[clippipegen:chosen-format]"
CHOSEN_FORMAT_FIELDS = (
    "format_id",
    "ext",
    "vcodec",
    "acodec",
    "width",
    "height",
    "fps",
    "filesize",
    "format_note",
)
CHOSEN_FORMAT_PRINT_TEMPLATE = (
    f"after_video:{CHOSEN_FORMAT_MARKER}{CHOSEN_FORMAT_SEPARATOR}"
    + CHOSEN_FORMAT_SEPARATOR.join(f"%({field})s" for field in CHOSEN_FORMAT_FIELDS)
)


class YtDlpVideoError(Exception):
    """Raised when yt-dlp video discovery, download, or probing orchestration fails."""


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
class YtDlpVideoPlan:
    yt_dlp_path: str | None
    yt_dlp_path_source: str | None
    ffprobe_path: str | None
    ffprobe_path_source: str | None
    source_url: str
    output_dir: str
    output_template: str
    format_selector: str
    allowed_containers: tuple[str, ...]
    yt_dlp_command: list[str] | None
    yt_dlp_command_summary: str | None
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "yt_dlp_path": self.yt_dlp_path,
            "yt_dlp_path_source": self.yt_dlp_path_source,
            "ffprobe_path": self.ffprobe_path,
            "ffprobe_path_source": self.ffprobe_path_source,
            "source_url": scrub_url_for_readback(self.source_url),
            "output_dir": self.output_dir,
            "output_template": self.output_template,
            "format_selector": self.format_selector,
            "allowed_containers": list(self.allowed_containers),
            "yt_dlp_command": _scrub_command_for_readback(self.yt_dlp_command),
            "yt_dlp_command_summary": self.yt_dlp_command_summary,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class YtDlpVideoResult:
    yt_dlp_path: str
    yt_dlp_path_source: str
    yt_dlp_version: str
    yt_dlp_command: list[str]
    yt_dlp_command_summary: str
    yt_dlp_exit_code: int
    yt_dlp_stderr_digest: dict[str, Any]
    format_selector: str
    chosen_format: dict[str, Any]
    output_path: Path
    output_byte_size: int
    container: str
    probe_result: source_video_adapter.ProbeResult
    intermediate_retained: bool
    warnings: list[str]
    stderr_digest: dict[str, Any]

    @property
    def metadata(self) -> dict[str, Any]:
        return self.probe_result.metadata


def discover_yt_dlp(
    *,
    yt_dlp_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Resolve yt-dlp path without executing it.

    Order: explicit ``--yt-dlp-path``, ``CLIPPIPE_YTDLP``, then PATH.
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
    output_dir: str | Path,
    yt_dlp_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    format_selector: str = DEFAULT_FORMAT_SELECTOR,
    allowed_containers: tuple[str, ...] = ALLOWED_CONTAINERS,
    env: Mapping[str, str] | None = None,
) -> YtDlpVideoPlan:
    """Build a dry-run-safe command plan without spawning subprocesses or network."""
    resolved_ytdlp, ytdlp_source = discover_yt_dlp(yt_dlp_path=yt_dlp_path, env=env)
    resolved_ffprobe, ffprobe_source = source_video_adapter.discover_ffprobe(
        ffprobe_path=ffprobe_path,
        env=env,
    )
    output_dir_display = str(output_dir).replace("\\", "/")
    output_template = f"{output_dir_display}/{OUTPUT_TEMPLATE_SUFFIX}"
    warnings: list[str] = [
        "yt-dlp-video dry-run does not call network or subprocesses",
        "downloaded yt-dlp output is the source_video itself; no separate intermediate is retained",
        "ffprobe metadata readback only; this does not render or encode video",
    ]
    if resolved_ytdlp is None:
        warnings.append(
            f"yt-dlp not found via --yt-dlp-path, {YTDLP_ENV_VAR}, or PATH"
        )
    if resolved_ffprobe is None:
        warnings.append(
            "ffprobe not found via --ffprobe-path, "
            f"{source_video_adapter.FFPROBE_ENV_VAR}, or PATH"
        )

    if resolved_ytdlp is None:
        return YtDlpVideoPlan(
            yt_dlp_path=None,
            yt_dlp_path_source=None,
            ffprobe_path=resolved_ffprobe,
            ffprobe_path_source=ffprobe_source,
            source_url=source_url,
            output_dir=output_dir_display,
            output_template=output_template,
            format_selector=format_selector,
            allowed_containers=tuple(allowed_containers),
            yt_dlp_command=None,
            yt_dlp_command_summary=None,
            warnings=warnings,
        )
    command = _download_command(
        resolved_ytdlp,
        source_url,
        output_template,
        format_selector,
    )
    return YtDlpVideoPlan(
        yt_dlp_path=resolved_ytdlp,
        yt_dlp_path_source=ytdlp_source,
        ffprobe_path=resolved_ffprobe,
        ffprobe_path_source=ffprobe_source,
        source_url=source_url,
        output_dir=output_dir_display,
        output_template=output_template,
        format_selector=format_selector,
        allowed_containers=tuple(allowed_containers),
        yt_dlp_command=command,
        yt_dlp_command_summary=_command_summary(command),
        warnings=warnings,
    )


def fetch_url_video(
    *,
    source_url: str,
    output_dir: str | Path,
    yt_dlp_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    format_selector: str = DEFAULT_FORMAT_SELECTOR,
    allowed_containers: tuple[str, ...] = ALLOWED_CONTAINERS,
    runner: Runner = subprocess.run,
    env: Mapping[str, str] | None = None,
) -> YtDlpVideoResult:
    """Fetch one URL with yt-dlp and probe its metadata with ffprobe."""
    _validate_source_url(source_url)
    out_dir = Path(output_dir)
    plan = build_plan(
        source_url=source_url,
        output_dir=out_dir,
        yt_dlp_path=yt_dlp_path,
        ffprobe_path=ffprobe_path,
        format_selector=format_selector,
        allowed_containers=allowed_containers,
        env=env,
    )
    if plan.yt_dlp_path is None:
        raise YtDlpVideoError("yt-dlp not found")
    if plan.ffprobe_path is None:
        raise YtDlpVideoError("ffprobe not found")

    ytdlp_version = _read_ytdlp_version(plan.yt_dlp_path, runner=runner)
    warnings = list(plan.warnings)

    out_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing_source_video_files(out_dir)
    if existing:
        raise YtDlpVideoError(
            "output_dir already contains source_video.* files; refusing to download: "
            + ", ".join(sorted(p.name for p in existing))
        )

    output_template = f"{out_dir.as_posix()}/{OUTPUT_TEMPLATE_SUFFIX}"
    command = _download_command(
        plan.yt_dlp_path,
        source_url,
        output_template,
        format_selector,
    )

    try:
        download_result = runner(
            command,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        _cleanup_source_video_outputs(out_dir)
        raise YtDlpVideoError(
            f"yt-dlp download failed before exit code: {exc}"
        ) from exc

    ytdlp_digest = ffmpeg_audio.build_stderr_digest(download_result.stderr)
    if download_result.returncode != 0:
        _cleanup_source_video_outputs(out_dir)
        raise YtDlpVideoError(
            "yt-dlp download failed: "
            f"exit_code={download_result.returncode}; "
            f"stderr_sha256={ytdlp_digest['sha256']}"
        )

    produced = _existing_source_video_files(out_dir)
    if not produced:
        raise YtDlpVideoError(
            "yt-dlp reported success but no source_video.* file was created"
        )
    if len(produced) > 1:
        for path in produced:
            _delete_quiet(path)
        raise YtDlpVideoError(
            "yt-dlp produced multiple source_video.* files; refusing to choose one: "
            + ", ".join(sorted(p.name for p in produced))
        )
    output_file = produced[0]
    container = output_file.suffix.lstrip(".").lower()
    if container not in allowed_containers:
        produced_name = output_file.name
        _delete_quiet(output_file)
        raise YtDlpVideoError(
            "yt-dlp chose an unsupported container "
            f"(produced {produced_name!r}, allowed {list(allowed_containers)})"
        )

    try:
        probe_result = source_video_adapter.probe_video(
            input_path=output_file,
            ffprobe_path=plan.ffprobe_path,
            ffprobe_path_source=plan.ffprobe_path_source or "unknown",
            runner=runner,
        )
    except source_video_adapter.SourceVideoError as exc:
        _delete_quiet(output_file)
        raise YtDlpVideoError(f"ffprobe metadata read failed: {exc}") from exc

    if probe_result.metadata.get("stream_counts", {}).get("video", 0) <= 0:
        _delete_quiet(output_file)
        raise YtDlpVideoError("ffprobe found no video stream in source video")

    chosen_format = _parse_chosen_format(download_result.stdout)
    warnings.extend(probe_result.warnings)
    warnings.append(
        "source video URL fetch is not production/creative/publish acceptance"
    )

    combined_digest = ffmpeg_audio.build_stderr_digest(
        "yt-dlp:\n"
        + (download_result.stderr or "")
        + "\nffprobe:\n"
        + str(probe_result.stderr_digest.get("tail") or "")
    )

    return YtDlpVideoResult(
        yt_dlp_path=plan.yt_dlp_path,
        yt_dlp_path_source=plan.yt_dlp_path_source or "unknown",
        yt_dlp_version=ytdlp_version,
        yt_dlp_command=command,
        yt_dlp_command_summary=_command_summary(command),
        yt_dlp_exit_code=download_result.returncode,
        yt_dlp_stderr_digest=ytdlp_digest,
        format_selector=format_selector,
        chosen_format=chosen_format,
        output_path=output_file,
        output_byte_size=output_file.stat().st_size,
        container=container,
        probe_result=probe_result,
        intermediate_retained=False,
        warnings=warnings,
        stderr_digest=combined_digest,
    )


def _validate_source_url(source_url: str) -> None:
    if not re.match(r"^https?://", source_url):
        raise YtDlpVideoError("--source-url must be an http(s) URL for yt-dlp-video")


def _read_ytdlp_version(ytdlp_path: str, *, runner: Runner) -> str:
    try:
        result = runner(
            [ytdlp_path, "--version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise YtDlpVideoError(
            f"yt-dlp version check failed before exit code: {exc}"
        ) from exc
    if result.returncode != 0:
        digest = ffmpeg_audio.build_stderr_digest(result.stderr)
        raise YtDlpVideoError(
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
    output_template: str,
    format_selector: str,
) -> list[str]:
    return [
        yt_dlp_path,
        "--no-playlist",
        "--no-progress",
        "-f",
        format_selector,
        "--print",
        CHOSEN_FORMAT_PRINT_TEMPLATE,
        "-o",
        output_template,
        source_url,
    ]


def _existing_source_video_files(out_dir: Path) -> list[Path]:
    if not out_dir.exists():
        return []
    return sorted(
        p
        for p in out_dir.iterdir()
        if p.is_file()
        and p.stem == OUTPUT_BASENAME
        and not p.name.endswith((".part", ".ytdl"))
    )


def _cleanup_source_video_outputs(out_dir: Path) -> None:
    if not out_dir.exists():
        return
    for p in out_dir.iterdir():
        if not p.is_file():
            continue
        if p.stem == OUTPUT_BASENAME or p.name.startswith(f"{OUTPUT_BASENAME}."):
            _delete_quiet(p)


def _delete_quiet(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def _parse_chosen_format(stdout: str | None) -> dict[str, Any]:
    if not stdout:
        return {}
    for raw_line in reversed(stdout.splitlines()):
        line = raw_line.strip()
        if not line.startswith(CHOSEN_FORMAT_MARKER):
            continue
        parts = line.split(CHOSEN_FORMAT_SEPARATOR)
        # First field is the marker itself; remaining align with CHOSEN_FORMAT_FIELDS.
        values = parts[1:]
        chosen: dict[str, Any] = {}
        for idx, name in enumerate(CHOSEN_FORMAT_FIELDS):
            raw = values[idx] if idx < len(values) else None
            chosen[name] = _coerce_format_value(name, raw)
        return chosen
    return {}


def _coerce_format_value(name: str, raw: str | None) -> Any:
    if raw is None:
        return None
    text = raw.strip()
    if text in {"", "NA", "None"}:
        return None
    if name in {"width", "height", "filesize"}:
        try:
            return int(text)
        except ValueError:
            return text
    if name == "fps":
        try:
            return float(text)
        except ValueError:
            return text
    return text


def _command_summary(command: list[str]) -> str:
    return " ".join(_summary_part(p) for p in command)


def _scrub_command_for_readback(command: list[str] | None) -> list[str] | None:
    if command is None:
        return None
    return [
        scrub_url_for_readback(p) or ""
        if re.match(r"https?://", p)
        else p
        for p in command
    ]


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
