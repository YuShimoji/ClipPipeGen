"""FFmpeg adapter for OUT-01 tiny render proof.

This module is intentionally small and diagnostic. It renders one selected cut
range from an existing source video plus source audio into a single video file,
then probes the output for readback metadata. It does not choose creative cuts,
burn subtitles, fetch URLs, upload, or claim production readiness.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Protocol

FFMPEG_ENV_VAR = "CLIPPIPE_FFMPEG"
FFPROBE_ENV_VAR = "CLIPPIPE_FFPROBE"
COMMAND_TIMEOUT_SECONDS = 900
VERSION_TIMEOUT_SECONDS = 15
STDERR_TAIL_CHARS = 1000


class TinyRenderError(Exception):
    """Raised when tiny render proof cannot be produced or probed."""

    def __init__(
        self,
        message: str,
        *,
        failure_reason: str = "code_bug_or_unexpected_exception",
        preflight: dict[str, Any] | None = None,
        attempts: list["CommandAttempt"] | None = None,
        selected_profile: "RenderProfile | None" = None,
    ) -> None:
        super().__init__(message)
        self.failure_reason = failure_reason
        self.preflight = preflight
        self.attempts = attempts or []
        self.selected_profile = selected_profile


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
class RenderProfile:
    profile_id: str
    container: str
    video_codec: str
    audio_codec: str
    output_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "container": self.container,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "output_path": self.output_path,
        }


@dataclass(frozen=True)
class RenderPlan:
    ffmpeg_path: str | None
    ffmpeg_path_source: str | None
    ffprobe_path: str | None
    ffprobe_path_source: str | None
    source_video_path: str
    source_audio_path: str
    output_path: str
    start_seconds: float
    duration_seconds: float
    container: str
    video_codec: str
    audio_codec: str
    command: list[str] | None
    command_summary: str | None
    render_profiles: list[RenderProfile]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ffmpeg_path": self.ffmpeg_path,
            "ffmpeg_path_source": self.ffmpeg_path_source,
            "ffprobe_path": self.ffprobe_path,
            "ffprobe_path_source": self.ffprobe_path_source,
            "source_video_path": self.source_video_path,
            "source_audio_path": self.source_audio_path,
            "output_path": self.output_path,
            "start_seconds": self.start_seconds,
            "duration_seconds": self.duration_seconds,
            "container": self.container,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "command": self.command,
            "command_summary": self.command_summary,
            "render_profiles": [profile.to_dict() for profile in self.render_profiles],
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class CommandAttempt:
    profile: RenderProfile
    command: list[str]
    command_summary: str
    status: str
    exit_code: int
    stderr_digest: dict[str, Any]
    failure_reason: str | None
    selected: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "summary": self.command_summary,
            "status": self.status,
            "exit_code": self.exit_code,
            "stderr_digest": self.stderr_digest,
            "failure_reason": self.failure_reason,
            "selected": self.selected,
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "ffprobe_path": self.ffprobe_path,
            "ffprobe_path_source": self.ffprobe_path_source,
            "ffprobe_version": self.ffprobe_version,
            "command_summary": self.command_summary,
            "exit_code": self.exit_code,
            "stderr_digest": self.stderr_digest,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class RenderResult:
    ffmpeg_path: str
    ffmpeg_path_source: str
    ffmpeg_version: str
    ffprobe_path: str
    ffprobe_path_source: str
    ffprobe_version: str
    command: list[str]
    command_summary: str
    attempts: list[CommandAttempt]
    selected_profile: RenderProfile
    fallback_used: bool
    output_path: str
    metadata: dict[str, Any]
    probe_result: ProbeResult
    preflight: dict[str, Any]
    warnings: list[str]


def build_plan(
    *,
    source_video_path: str | Path,
    source_audio_path: str | Path,
    output_path: str | Path,
    start_seconds: float,
    duration_seconds: float,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    container: str = "mp4",
    video_codec: str = "auto",
    audio_codec: str = "auto",
    env: Mapping[str, str] | None = None,
) -> RenderPlan:
    """Build a dry-run-safe render command plan without spawning subprocesses."""
    resolved_ffmpeg, ffmpeg_source = discover_ffmpeg(ffmpeg_path=ffmpeg_path, env=env)
    resolved_ffprobe, ffprobe_source = discover_ffprobe(ffprobe_path=ffprobe_path, env=env)
    warnings = [
        "OUT-01 tiny render proof is diagnostic and not production/creative/publish acceptance",
        "subtitle burn-in is intentionally disabled",
    ]
    if resolved_ffmpeg is None:
        warnings.append(f"ffmpeg not found via --ffmpeg-path, {FFMPEG_ENV_VAR}, or PATH")
    if resolved_ffprobe is None:
        warnings.append(f"ffprobe not found via --ffprobe-path, {FFPROBE_ENV_VAR}, or PATH")

    profiles = _render_profiles(
        output_path=output_path,
        container=container,
        video_codec=video_codec,
        audio_codec=audio_codec,
    )
    command: list[str] | None = None
    command_summary: str | None = None
    if resolved_ffmpeg is not None:
        first_profile = profiles[0]
        command = _render_command(
            ffmpeg_path=resolved_ffmpeg,
            source_video_path=source_video_path,
            source_audio_path=source_audio_path,
            output_path=first_profile.output_path,
            start_seconds=start_seconds,
            duration_seconds=duration_seconds,
            video_codec=first_profile.video_codec,
            audio_codec=first_profile.audio_codec,
        )
        command_summary = _command_summary(command)

    return RenderPlan(
        ffmpeg_path=resolved_ffmpeg,
        ffmpeg_path_source=ffmpeg_source,
        ffprobe_path=resolved_ffprobe,
        ffprobe_path_source=ffprobe_source,
        source_video_path=str(source_video_path).replace("\\", "/"),
        source_audio_path=str(source_audio_path).replace("\\", "/"),
        output_path=str(output_path).replace("\\", "/"),
        start_seconds=float(start_seconds),
        duration_seconds=float(duration_seconds),
        container=container,
        video_codec=video_codec,
        audio_codec=audio_codec,
        command=command,
        command_summary=command_summary,
        render_profiles=profiles,
        warnings=warnings,
    )


def discover_ffmpeg(
    *,
    ffmpeg_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    return _discover_tool("ffmpeg", explicit_path=ffmpeg_path, env_var=FFMPEG_ENV_VAR, env=env)


def discover_ffprobe(
    *,
    ffprobe_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    return _discover_tool("ffprobe", explicit_path=ffprobe_path, env_var=FFPROBE_ENV_VAR, env=env)


def preflight_tools(
    *,
    ffmpeg_path: str | Path | None = None,
    ffmpeg_path_source: str | None = None,
    ffprobe_path: str | Path | None = None,
    ffprobe_path_source: str | None = None,
    runner: Runner = subprocess.run,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Check render tool availability before attempting the render."""
    resolved_ffmpeg, discovered_ffmpeg_source = (
        (str(ffmpeg_path), ffmpeg_path_source or "argument")
        if ffmpeg_path
        else discover_ffmpeg(env=env)
    )
    resolved_ffprobe, discovered_ffprobe_source = (
        (str(ffprobe_path), ffprobe_path_source or "argument")
        if ffprobe_path
        else discover_ffprobe(env=env)
    )
    ffmpeg = _tool_preflight(
        tool_name="ffmpeg",
        path=resolved_ffmpeg,
        path_source=discovered_ffmpeg_source,
        missing_reason="environment_missing_ffmpeg",
        runner=runner,
    )
    ffprobe = _tool_preflight(
        tool_name="ffprobe",
        path=resolved_ffprobe,
        path_source=discovered_ffprobe_source,
        missing_reason="environment_missing_ffprobe",
        runner=runner,
    )
    failure_reason = None
    if not ffmpeg["available"]:
        failure_reason = "environment_missing_ffmpeg"
    elif not ffprobe["available"]:
        failure_reason = "environment_missing_ffprobe"
    return {
        "status": "passed" if failure_reason is None else "failed",
        "failure_reason": failure_reason,
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
    }


def render_tiny_proof(
    *,
    source_video_path: str | Path,
    source_audio_path: str | Path,
    output_path: str | Path,
    start_seconds: float,
    duration_seconds: float,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    container: str = "mp4",
    video_codec: str = "auto",
    audio_codec: str = "auto",
    runner: Runner = subprocess.run,
    env: Mapping[str, str] | None = None,
) -> RenderResult:
    """Render and probe one tiny diagnostic output artifact."""
    source_video = Path(source_video_path)
    source_audio = Path(source_audio_path)
    output = Path(output_path)
    plan = build_plan(
        source_video_path=source_video,
        source_audio_path=source_audio,
        output_path=output,
        start_seconds=start_seconds,
        duration_seconds=duration_seconds,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        container=container,
        video_codec=video_codec,
        audio_codec=audio_codec,
        env=env,
    )
    preflight = preflight_tools(
        ffmpeg_path=plan.ffmpeg_path,
        ffmpeg_path_source=plan.ffmpeg_path_source,
        ffprobe_path=plan.ffprobe_path,
        ffprobe_path_source=plan.ffprobe_path_source,
        runner=runner,
        env=env,
    )
    if preflight["failure_reason"] is not None:
        raise TinyRenderError(
            f"render preflight failed: {preflight['failure_reason']}",
            failure_reason=preflight["failure_reason"],
            preflight=preflight,
        )
    if not source_video.exists():
        raise TinyRenderError(
            f"source video not found: {source_video}",
            failure_reason="input_video_missing",
            preflight=preflight,
        )
    if not source_audio.exists():
        raise TinyRenderError(
            f"source audio not found: {source_audio}",
            failure_reason="input_audio_missing",
            preflight=preflight,
        )
    if duration_seconds <= 0:
        raise TinyRenderError(
            "duration_seconds must be positive",
            failure_reason="duration_or_timeline_mismatch",
            preflight=preflight,
        )

    ffmpeg_version = preflight["ffmpeg"]["version"] or "unknown"
    ffprobe_version = preflight["ffprobe"]["version"] or "unknown"

    attempts: list[CommandAttempt] = []
    last_error = "no render attempts were built"
    selected_command: list[str] | None = None
    selected_profile: RenderProfile | None = None
    selected_output: Path | None = None
    for profile in plan.render_profiles:
        output = Path(profile.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = _render_command(
            ffmpeg_path=plan.ffmpeg_path,
            source_video_path=source_video,
            source_audio_path=source_audio,
            output_path=output,
            start_seconds=start_seconds,
            duration_seconds=duration_seconds,
            video_codec=profile.video_codec,
            audio_codec=profile.audio_codec,
        )
        try:
            result = runner(
                command,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            if output.exists():
                output.unlink()
            failure_reason = (
                "environment_missing_ffmpeg"
                if isinstance(exc, FileNotFoundError)
                else "ffmpeg_command_failed"
            )
            last_error = f"ffmpeg render failed before exit code: {exc}"
            attempts.append(
                CommandAttempt(
                    profile=profile,
                    command=command,
                    command_summary=_command_summary(command),
                    status="failed",
                    exit_code=-1,
                    stderr_digest=build_stderr_digest(str(exc)),
                    failure_reason=failure_reason,
                    selected=False,
                )
            )
            continue

        digest = build_stderr_digest(result.stderr)
        success = result.returncode == 0 and output.exists()
        attempts.append(
            CommandAttempt(
                profile=profile,
                command=command,
                command_summary=_command_summary(command),
                status="succeeded" if success else "failed",
                exit_code=result.returncode,
                stderr_digest=digest,
                failure_reason=None if success else _classify_ffmpeg_failure(result.stderr),
                selected=success,
            )
        )
        if success:
            selected_command = command
            selected_profile = profile
            selected_output = output
            break
        if output.exists():
            output.unlink()
        last_error = (
            "ffmpeg render failed: "
            f"exit_code={result.returncode}; stderr_sha256={digest['sha256']}"
        )

    if selected_command is None or selected_profile is None or selected_output is None:
        last_reason = (
            attempts[-1].failure_reason
            if attempts and attempts[-1].failure_reason
            else "ffmpeg_command_failed"
        )
        raise TinyRenderError(
            last_error,
            failure_reason=last_reason,
            preflight=preflight,
            attempts=attempts,
        )

    try:
        probe = probe_media(
            input_path=selected_output,
            ffprobe_path=plan.ffprobe_path,
            runner=runner,
            ffprobe_version=ffprobe_version,
            ffprobe_path_source=plan.ffprobe_path_source or "unknown",
        )
    except TinyRenderError as exc:
        raise TinyRenderError(
            str(exc),
            failure_reason=exc.failure_reason or "metadata_probe_failed",
            preflight=preflight,
            attempts=attempts,
            selected_profile=selected_profile,
        ) from exc
    warnings = list(plan.warnings)
    failed_attempts = [attempt for attempt in attempts if not attempt.selected]
    if failed_attempts:
        warnings.append(
            f"{len(failed_attempts)} render profile fallback attempt(s) failed before selected profile {selected_profile.profile_id}"
        )

    return RenderResult(
        ffmpeg_path=plan.ffmpeg_path,
        ffmpeg_path_source=plan.ffmpeg_path_source or "unknown",
        ffmpeg_version=ffmpeg_version,
        ffprobe_path=plan.ffprobe_path,
        ffprobe_path_source=plan.ffprobe_path_source or "unknown",
        ffprobe_version=ffprobe_version,
        command=selected_command,
        command_summary=_command_summary(selected_command),
        attempts=attempts,
        selected_profile=selected_profile,
        fallback_used=bool(failed_attempts),
        output_path=str(selected_output).replace("\\", "/"),
        metadata=probe.metadata,
        probe_result=probe,
        preflight=preflight,
        warnings=warnings,
    )


def probe_media(
    *,
    input_path: str | Path,
    ffprobe_path: str | Path | None = None,
    runner: Runner = subprocess.run,
    ffprobe_version: str | None = None,
    ffprobe_path_source: str | None = None,
    env: Mapping[str, str] | None = None,
) -> ProbeResult:
    resolved, source = (
        (str(ffprobe_path), ffprobe_path_source or "argument")
        if ffprobe_path
        else discover_ffprobe(env=env)
    )
    if resolved is None:
        raise TinyRenderError("ffprobe not found", failure_reason="environment_missing_ffprobe")
    version = ffprobe_version or _read_tool_version(resolved, tool_name="ffprobe", runner=runner)
    command = _probe_command(resolved, input_path)
    try:
        result = runner(
            command,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise TinyRenderError(
            f"ffprobe failed before exit code: {exc}",
            failure_reason="metadata_probe_failed",
        ) from exc
    digest = build_stderr_digest(result.stderr)
    if result.returncode != 0:
        raise TinyRenderError(
            "ffprobe metadata read failed: "
            f"exit_code={result.returncode}; stderr_sha256={digest['sha256']}",
            failure_reason="metadata_probe_failed",
        )
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise TinyRenderError(
            f"ffprobe returned invalid JSON: {exc}",
            failure_reason="metadata_probe_failed",
        ) from exc
    return ProbeResult(
        ffprobe_path=resolved,
        ffprobe_path_source=source or "unknown",
        ffprobe_version=version,
        command=command,
        command_summary=_command_summary(command),
        exit_code=result.returncode,
        stderr_digest=digest,
        metadata=metadata_from_ffprobe(payload),
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


def _tool_preflight(
    *,
    tool_name: str,
    path: str | None,
    path_source: str | None,
    missing_reason: str,
    runner: Runner,
) -> dict[str, Any]:
    if path is None:
        return {
            "name": tool_name,
            "path": None,
            "path_source": None,
            "available": False,
            "version": None,
            "status": "failed",
            "failure_reason": missing_reason,
            "stderr_digest": None,
        }
    command = [path, "-version"]
    try:
        result = runner(
            command,
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "name": tool_name,
            "path": path,
            "path_source": path_source or "unknown",
            "available": False,
            "version": None,
            "status": "failed",
            "failure_reason": missing_reason,
            "stderr_digest": build_stderr_digest(str(exc)),
            "command_summary": _command_summary(command),
        }
    digest = build_stderr_digest(result.stderr)
    if result.returncode != 0:
        return {
            "name": tool_name,
            "path": path,
            "path_source": path_source or "unknown",
            "available": False,
            "version": None,
            "status": "failed",
            "failure_reason": missing_reason,
            "stderr_digest": digest,
            "command_summary": _command_summary(command),
            "exit_code": result.returncode,
        }
    first_line = (result.stdout or "").splitlines()[0:1]
    return {
        "name": tool_name,
        "path": path,
        "path_source": path_source or "unknown",
        "available": True,
        "version": first_line[0].strip() if first_line else "unknown",
        "status": "passed",
        "failure_reason": None,
        "stderr_digest": digest,
        "command_summary": _command_summary(command),
        "exit_code": result.returncode,
    }


def metadata_from_ffprobe(payload: dict[str, Any]) -> dict[str, Any]:
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
    return {
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
        "fps": _fps_from_rate(frame_rate),
        "frame_rate": frame_rate or None,
        "stream_count": len(streams),
        "stream_counts": {
            "video": len(video_streams),
            "audio": len(audio_streams),
            "other": max(0, len(streams) - len(video_streams) - len(audio_streams)),
        },
    }


def _discover_tool(
    tool_name: str,
    *,
    explicit_path: str | Path | None,
    env_var: str,
    env: Mapping[str, str] | None,
) -> tuple[str | None, str | None]:
    if explicit_path:
        return str(explicit_path), "argument"
    lookup_env = env if env is not None else os.environ
    env_path = lookup_env.get(env_var)
    if env_path:
        return env_path, f"env:{env_var}"
    path = shutil.which(tool_name, path=lookup_env.get("PATH"))
    if path:
        return path, "PATH"
    return None, None


def _read_tool_version(tool_path: str, *, tool_name: str, runner: Runner) -> str:
    try:
        result = runner(
            [tool_path, "-version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise TinyRenderError(
            f"{tool_name} version check failed before exit code: {exc}"
        ) from exc
    if result.returncode != 0:
        digest = build_stderr_digest(result.stderr)
        raise TinyRenderError(
            f"{tool_name} version check failed: "
            f"exit_code={result.returncode}; stderr_sha256={digest['sha256']}"
        )
    first_line = (result.stdout or "").splitlines()[0:1]
    return first_line[0].strip() if first_line else "unknown"


def _codec_candidates(
    *,
    container: str,
    video_codec: str,
    audio_codec: str,
) -> list[tuple[str, str]]:
    if video_codec != "auto" or audio_codec != "auto":
        resolved_video = "libopenh264" if video_codec == "auto" else video_codec
        resolved_audio = "aac" if audio_codec == "auto" else audio_codec
        return [(resolved_video, resolved_audio)]
    if container == "mkv":
        return [("libx264", "aac"), ("libopenh264", "aac"), ("mpeg4", "pcm_s16le")]
    return [("libx264", "aac"), ("libopenh264", "aac"), ("mpeg4", "aac")]


def _render_profiles(
    *,
    output_path: str | Path,
    container: str,
    video_codec: str,
    audio_codec: str,
) -> list[RenderProfile]:
    output = Path(output_path)
    if video_codec != "auto" or audio_codec != "auto":
        resolved_video = "libx264" if video_codec == "auto" else video_codec
        resolved_audio = "aac" if audio_codec == "auto" else audio_codec
        return [
            RenderProfile(
                profile_id=_profile_id(container, resolved_video, resolved_audio),
                container=container,
                video_codec=resolved_video,
                audio_codec=resolved_audio,
                output_path=str(_output_path_for_container(output, container)).replace("\\", "/"),
            )
        ]

    if container == "mkv":
        candidates = [
            ("mkv", "libx264", "aac"),
            ("mkv", "libopenh264", "aac"),
            ("mkv", "mpeg4", "pcm_s16le"),
            ("mp4", "libx264", "aac"),
        ]
    else:
        candidates = [
            ("mp4", "libx264", "aac"),
            ("mp4", "libopenh264", "aac"),
            ("mp4", "mpeg4", "aac"),
            ("mkv", "libx264", "aac"),
            ("mkv", "mpeg4", "pcm_s16le"),
        ]
    return [
        RenderProfile(
            profile_id=_profile_id(candidate_container, candidate_video, candidate_audio),
            container=candidate_container,
            video_codec=candidate_video,
            audio_codec=candidate_audio,
            output_path=str(_output_path_for_container(output, candidate_container)).replace("\\", "/"),
        )
        for candidate_container, candidate_video, candidate_audio in candidates
    ]


def _output_path_for_container(output_path: Path, container: str) -> Path:
    return output_path.with_suffix(f".{container}")


def _profile_id(container: str, video_codec: str, audio_codec: str) -> str:
    video = {"libx264": "h264", "libopenh264": "openh264"}.get(video_codec, video_codec)
    audio = audio_codec.replace("-", "_")
    return f"{container}_{video}_{audio}"


def _classify_ffmpeg_failure(stderr: str | None) -> str:
    text = (stderr or "").lower()
    if any(
        marker in text
        for marker in (
            "unknown encoder",
            "encoder not found",
            "error initializing output stream",
            "could not write header",
            "codec not currently supported",
            "requested output format",
            "invalid argument",
        )
    ):
        return "codec_or_container_unsupported"
    if any(
        marker in text
        for marker in (
            "no such file or directory",
            "error opening input",
            "invalid data found when processing input",
            "stream specifier",
            "matches no streams",
        )
    ):
        return "input_stream_invalid"
    return "ffmpeg_command_failed"


def _render_command(
    *,
    ffmpeg_path: str,
    source_video_path: str | Path,
    source_audio_path: str | Path,
    output_path: str | Path,
    start_seconds: float,
    duration_seconds: float,
    video_codec: str,
    audio_codec: str,
) -> list[str]:
    return [
        ffmpeg_path,
        "-y",
        "-ss",
        _seconds(start_seconds),
        "-t",
        _seconds(duration_seconds),
        "-i",
        str(source_video_path),
        "-ss",
        _seconds(start_seconds),
        "-t",
        _seconds(duration_seconds),
        "-i",
        str(source_audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
        "-c:v",
        video_codec,
        "-c:a",
        audio_codec,
        "-shortest",
        str(output_path),
    ]


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


def _command_summary(command: list[str]) -> str:
    return " ".join(_summary_part(part) for part in command)


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


def _seconds(value: float) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".")

