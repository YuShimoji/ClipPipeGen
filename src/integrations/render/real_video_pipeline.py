"""Reusable OUT-12 one-command real-video automation pipeline.

The pipeline consumes an existing real source file or a material-ledger
identity, keeps source chronology, builds a traceable Timeline IR, remaps
caption authority, renders one source-native H.264/AAC MP4, validates it, and
writes a compact localhost review package.  It is an internal operational
artifact path: rights, production, publishing, and public acceptance stay
separate gates.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import time
import uuid
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from src.integrations.render import ffmpeg_tiny
from src.integrations.render.complete_narrative_short import (
    _canonical_manifest_self_hash,
)
from src.integrations.render.second_source_short_repeatability import (
    _run_signal_qa,
)
from src.integrations.render.vertical_short_candidate import (
    _faststart_readback,
    _measure_loudness,
)


SCHEMA_VERSION = "clippipegen.out12.real_video_pipeline.v1"
TIMELINE_SCHEMA_VERSION = "clippipegen.timeline_ir.v1"
EDIT_PACK_SCHEMA_VERSION = "clippipegen.out12.edit_pack.v1"
CAPTION_SCHEMA_VERSION = "clippipegen.out12.caption_readback.v1"
VALIDATION_SCHEMA_VERSION = "clippipegen.out12.validation_readback.v1"
PIPELINE_VERSION = "out12-one-command-real-video-v1"
READY_STATE = "AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1"
PROFILE_LONG_FORM = "long-form"
MIN_LONG_FORM_SECONDS = 180.0
MIN_CUT_SECONDS = 5.0
MAX_CUTS = 20
MIN_CUTS = 8
DEFAULT_REVIEW_PORT = 8075
COMMAND_TIMEOUT_SECONDS = 1800


class RealVideoPipelineError(Exception):
    """Raised when an OUT-12 stage cannot complete objectively."""

    def __init__(self, message: str, *, stage: str = "unknown") -> None:
        super().__init__(message)
        self.stage = stage


def build_real_video(
    *,
    output_dir: Path,
    source_path: Path | None = None,
    intake_identity: str | None = None,
    source_identity: str | None = None,
    rights_manifest_path: Path | None = None,
    caption_track_path: Path | None = None,
    authority_readback_path: Path | None = None,
    caption_mode: str = "auto",
    profile: str = PROFILE_LONG_FORM,
    target_duration_seconds: float = 300.0,
    resume: bool = False,
    force: bool = False,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    review_port: int = DEFAULT_REVIEW_PORT,
    base_dir: Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
) -> dict[str, Any]:
    """Run source resolution through review-package generation in one call."""

    started = time.monotonic()
    root = (base_dir or Path.cwd()).resolve()
    output = _resolved(root, output_dir)
    prior_failure_count = sum(
        1
        for item in output.parent.glob(f".{output.name}.failed-*")
        if item.is_dir()
    ) + (1 if (output / "pipeline_failure.json").is_file() else 0)
    current_stage = "source_resolution"
    stage: Path | None = None
    fingerprint: str | None = None
    try:
        if profile != PROFILE_LONG_FORM:
            raise RealVideoPipelineError(
                f"unsupported profile: {profile}", stage=current_stage
            )
        if target_duration_seconds <= 0:
            raise RealVideoPipelineError(
                "target duration must be positive", stage=current_stage
            )
        if resume and force:
            raise RealVideoPipelineError(
                "--resume and --force are mutually exclusive", stage=current_stage
            )
        if not 1 <= int(review_port) <= 65535:
            raise RealVideoPipelineError(
                "review port must be between 1 and 65535", stage=current_stage
            )
        tools = ffmpeg_tiny.preflight_tools(
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        if tools.get("status") != "passed":
            raise RealVideoPipelineError(
                f"FFmpeg preflight failed: {tools.get('failure_reason')}",
                stage=current_stage,
            )
        ffmpeg = str(tools["ffmpeg"]["path"])
        ffprobe = str(tools["ffprobe"]["path"])
        resolved = resolve_source(
            root=root,
            source_path=source_path,
            intake_identity=intake_identity,
            source_identity=source_identity,
            rights_manifest_path=rights_manifest_path,
            caption_track_path=caption_track_path,
            authority_readback_path=authority_readback_path,
            caption_mode=caption_mode,
        )
        source_probe = probe_media_detail(
            resolved["source_path"], ffprobe_path=ffprobe, runner=runner
        )
        if source_probe["video_stream_count"] != 1 or source_probe["audio_stream_count"] != 1:
            raise RealVideoPipelineError(
                "source must contain exactly one primary video and audio stream",
                stage=current_stage,
            )
        fingerprint_payload = {
            "pipeline_version": PIPELINE_VERSION,
            "profile": profile,
            "target_duration_seconds": float(target_duration_seconds),
            "source_identity": resolved["source_identity"],
            "source_sha256": resolved["source_sha256"],
            "source_byte_size": resolved["source_byte_size"],
            "source_probe": source_probe,
            "rights_sha256": resolved.get("rights_sha256"),
            "caption_sha256": resolved.get("caption_sha256"),
            "caption_mode": resolved["caption_mode"],
            "review_port": int(review_port),
        }
        fingerprint = content_fingerprint(fingerprint_payload)
        if resume:
            resumed = resume_existing_output(
                output_dir=output,
                input_fingerprint=fingerprint,
                root=root,
            )
            resumed["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return resumed
        if output.exists() and not force:
            raise RealVideoPipelineError(
                "output directory already exists; use --resume or --force",
                stage=current_stage,
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        stage = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
        stage.mkdir()
        _write_json(
            stage / "provenance_snapshot.json",
            {
                "schema_version": SCHEMA_VERSION,
                "source_identity": resolved["source_identity"],
                "source_path": _display_path(resolved["source_path"], root),
                "source_sha256": resolved["source_sha256"],
                "source_byte_size": resolved["source_byte_size"],
                "source_probe": source_probe,
                "resolution_mode": resolved["resolution_mode"],
                "rights": resolved["rights"],
                "caption_authority": resolved["caption_authority"],
                "closed_gates": _closed_gates(),
            },
        )

        current_stage = "content_analysis"
        analysis = analyze_source(
            source_path=resolved["source_path"],
            duration_seconds=source_probe["duration_seconds"],
            ffmpeg_path=ffmpeg,
            runner=runner,
        )
        analysis["stage_fingerprint"] = content_fingerprint(
            {
                "input_fingerprint": fingerprint,
                "stage": current_stage,
                "scene_threshold": analysis["scene_threshold"],
            }
        )
        _write_json(stage / "analysis_readback.json", analysis)

        current_stage = "timeline_selection"
        timeline = plan_timeline(
            source_identity=resolved["source_identity"],
            source_duration_seconds=source_probe["duration_seconds"],
            scene_boundaries=analysis["scene_boundaries_seconds"],
            target_duration_seconds=float(target_duration_seconds),
        )
        caption_events = load_caption_events(resolved.get("caption_track_path"))
        caption_rows = remap_caption_events(caption_events, timeline["cuts"])
        _attach_caption_ids(timeline["cuts"], caption_rows)
        validate_timeline_ir(timeline)
        _write_json(stage / "timeline_ir.json", timeline)
        edit_pack = build_edit_pack(timeline, resolved)
        _write_json(stage / "edit_pack.json", edit_pack)
        caption_readback = build_caption_readback(
            caption_mode=resolved["caption_mode"],
            caption_authority=resolved["caption_authority"],
            caption_rows=caption_rows,
            source_caption_sha256=resolved.get("caption_sha256"),
            timeline_duration_seconds=timeline["output_duration_seconds"],
        )
        _write_json(stage / "caption_readback.json", caption_readback)
        if resolved["caption_mode"] == "official_sidecar":
            _write_text(stage / "captions.srt", render_srt(caption_rows))

        current_stage = "render"
        final_video = stage / "final_video.mp4"
        render = render_timeline(
            source_path=resolved["source_path"],
            video_path=final_video,
            cuts=timeline["cuts"],
            ffmpeg_path=ffmpeg,
            runner=runner,
        )
        if prior_failure_count:
            render["execution_count"] = prior_failure_count + 1
            render["corrective_pass_count"] = prior_failure_count

        current_stage = "media_validation"
        validation = validate_rendered_video(
            video_path=final_video,
            timeline=timeline,
            caption_readback=caption_readback,
            source_probe=source_probe,
            ffmpeg_path=ffmpeg,
            ffprobe_path=ffprobe,
            runner=runner,
        )
        validation["render"] = render
        validation["input_fingerprint"] = fingerprint
        _write_json(stage / "validation_readback.json", validation)
        if validation["status"] != "passed":
            raise RealVideoPipelineError(
                "rendered media validation failed", stage=current_stage
            )

        current_stage = "review_package"
        review = build_review_package(
            stage=stage,
            timeline=timeline,
            resolved=resolved,
            validation=validation,
            review_port=int(review_port),
            ffmpeg_path=ffmpeg,
            runner=runner,
        )
        pipeline_state = {
            "schema_version": SCHEMA_VERSION,
            "state": READY_STATE,
            "ready": True,
            "failure_stage": None,
            "input_fingerprint": fingerprint,
            "source_identity": resolved["source_identity"],
            "final_video_sha256": _sha256(final_video),
            "output_duration_seconds": validation["media"]["duration_seconds"],
            "cut_count": len(timeline["cuts"]),
            "review_entrypoint": "review/index.html",
            "closed_gates": _closed_gates(),
        }
        _write_json(stage / "pipeline_state.json", pipeline_state)

        current_stage = "manifest"
        stage_rows = [
            {
                "stage": name,
                "status": "completed",
                "cache": "written",
                "fingerprint": content_fingerprint(
                    {"input_fingerprint": fingerprint, "stage": name}
                ),
            }
            for name in (
                "source_resolution",
                "provenance_snapshot",
                "content_analysis",
                "timeline_selection",
                "caption_remap",
                "render",
                "media_validation",
                "review_package",
            )
        ]
        manifest = build_run_manifest(
            stage=stage,
            input_fingerprint=fingerprint,
            resolved=resolved,
            timeline=timeline,
            validation=validation,
            review=review,
            stages=stage_rows,
        )
        _write_json(stage / "run_manifest.json", manifest)
        validate_run_manifest(stage, manifest)
        promote_output(stage=stage, output=output, force=force)
        stage = None
        return {
            "artifact_id": "clip-out12-one-command-real-video-automation-v1-001",
            "state": READY_STATE,
            "output_dir": output,
            "final_video": output / "final_video.mp4",
            "timeline_ir": output / "timeline_ir.json",
            "edit_pack": output / "edit_pack.json",
            "caption_readback": output / "caption_readback.json",
            "run_manifest": output / "run_manifest.json",
            "validation_readback": output / "validation_readback.json",
            "review_index": output / "review" / "index.html",
            "review_url": f"http://127.0.0.1:{review_port}/review/index.html",
            "open_command": str(output / "review" / "open_preview.ps1"),
            "source_identity": resolved["source_identity"],
            "duration_seconds": validation["media"]["duration_seconds"],
            "cut_count": len(timeline["cuts"]),
            "video_sha256": _sha256(output / "final_video.mp4"),
            "resume": False,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:
        failure_evidence_dir: Path | None = None
        if stage is not None and stage.exists():
            failure_evidence_dir = (
                output.parent / f".{output.name}.failed-{uuid.uuid4().hex}"
            )
            stage.replace(failure_evidence_dir)
        error = exc if isinstance(exc, RealVideoPipelineError) else RealVideoPipelineError(
            str(exc), stage=current_stage
        )
        write_failure_state(
            output_dir=output,
            stage=error.stage,
            message=str(error),
            input_fingerprint=fingerprint,
            failure_evidence_dir=failure_evidence_dir,
        )
        raise error


def resolve_source(
    *,
    root: Path,
    source_path: Path | None,
    intake_identity: str | None,
    source_identity: str | None,
    rights_manifest_path: Path | None,
    caption_track_path: Path | None,
    authority_readback_path: Path | None,
    caption_mode: str,
) -> dict[str, Any]:
    if (source_path is None) == (intake_identity is None):
        raise RealVideoPipelineError(
            "provide exactly one of source path or intake identity",
            stage="source_resolution",
        )
    authority: dict[str, Any] | None = None
    authority_path: Path | None = None
    if authority_readback_path is not None:
        authority_path = _resolved(root, authority_readback_path)
        authority = _read_json(authority_path, "authority readback")
    episode: Path | None = None
    resolution_mode = "direct_real_source"
    if intake_identity is not None:
        episode_text, separator, material_id = intake_identity.partition("#")
        if separator != "#" or not episode_text or not material_id:
            raise RealVideoPipelineError(
                "intake identity must be <episode-dir>#<material-id>",
                stage="source_resolution",
            )
        episode = _resolved(root, Path(episode_text))
        ledger = _read_json(episode / "material_ledger.json", "material ledger")
        material = next(
            (
                row
                for row in ledger.get("materials") or []
                if isinstance(row, dict)
                and row.get("id") == material_id
                and row.get("kind") == "source_video"
            ),
            None,
        )
        if material is None:
            raise RealVideoPipelineError(
                "source-video material identity was not found",
                stage="source_resolution",
            )
        source = _resolved(root, Path(str(material.get("file_path") or "")))
        resolution_mode = "content_addressed_intake_reuse"
    else:
        source = _resolved(root, source_path or Path())
        episode = _infer_episode_dir(source)
    if not source.is_file():
        raise RealVideoPipelineError(
            f"real source file not found: {source}", stage="source_resolution"
        )
    source_sha = _sha256(source)

    if authority is not None:
        identity = authority.get("source_identity") or {}
        source_identity = source_identity or str(identity.get("identity") or "")
        if rights_manifest_path is None:
            rights_manifest_path = _authority_input_path(authority, "rights_manifest")
        if caption_track_path is None:
            caption_track_path = _authority_input_path(authority, "source_caption_track")
    rights_path = (
        _resolved(root, rights_manifest_path)
        if rights_manifest_path is not None
        else (episode / "rights_manifest.json" if episode is not None else None)
    )
    rights: dict[str, Any]
    rights_sha: str | None = None
    if rights_path is not None and rights_path.is_file():
        rights_payload = _read_json(rights_path, "rights manifest")
        rights_sha = _sha256(rights_path)
        rights = {
            "path": _display_path(rights_path, root),
            "sha256": rights_sha,
            "status": str(
                (rights_payload.get("compliance_check") or {}).get("status")
                or "unknown"
            ),
            "snapshot_only": True,
        }
        source_identity = source_identity or _identity_from_rights(rights_payload)
    else:
        rights = {
            "path": None,
            "sha256": None,
            "status": "unknown",
            "snapshot_only": True,
        }
    identity_value = (source_identity or f"local:{source_sha[:16]}").strip()

    caption_path = (
        _resolved(root, caption_track_path)
        if caption_track_path is not None
        else _discover_caption_track(episode, identity_value)
    )
    if caption_path is not None and not caption_path.is_file():
        raise RealVideoPipelineError(
            f"caption track not found: {caption_path}", stage="source_resolution"
        )
    authority_caption_mode = str((authority or {}).get("caption", {}).get("mode") or "")
    normalized_caption_mode = normalize_caption_mode(
        requested=caption_mode,
        authority_mode=authority_caption_mode,
        has_caption_track=caption_path is not None,
    )
    caption_sha = _sha256(caption_path) if caption_path is not None else None
    caption_authority = {
        "mode": normalized_caption_mode,
        "source": "official_json3" if caption_path is not None else "none",
        "track_path": _display_path(caption_path, root) if caption_path else None,
        "track_sha256": caption_sha,
        "native_pixels_preserved": normalized_caption_mode == "native_baked",
        "overlay_burn_in_applied": False,
        "duplicate_overlay_rejected": normalized_caption_mode == "native_baked",
        "semantic_claims": "authority_timing_and_text_only_no_speaker_or_lyric_inference",
    }
    return {
        "source_path": source,
        "source_identity": identity_value,
        "source_sha256": source_sha,
        "source_byte_size": source.stat().st_size,
        "resolution_mode": resolution_mode,
        "episode_dir": episode,
        "rights_path": rights_path,
        "rights_sha256": rights_sha,
        "rights": rights,
        "caption_track_path": caption_path,
        "caption_sha256": caption_sha,
        "caption_mode": normalized_caption_mode,
        "caption_authority": caption_authority,
        "authority_readback_path": authority_path,
    }


def normalize_caption_mode(
    *, requested: str, authority_mode: str, has_caption_track: bool
) -> str:
    allowed = {"auto", "native", "sidecar", "none"}
    if requested not in allowed:
        raise RealVideoPipelineError(
            f"unsupported caption mode: {requested}", stage="source_resolution"
        )
    if requested == "native":
        return "native_baked"
    if requested == "sidecar":
        if not has_caption_track:
            raise RealVideoPipelineError(
                "sidecar caption mode requires a caption track",
                stage="source_resolution",
            )
        return "official_sidecar"
    if requested == "none":
        return "none"
    if authority_mode == "native_baked_caption_only":
        return "native_baked"
    if has_caption_track:
        return "official_sidecar"
    return "none"


def probe_media_detail(
    source_path: Path, *, ffprobe_path: str, runner: ffmpeg_tiny.Runner
) -> dict[str, Any]:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(source_path),
    ]
    result = _run(command, runner=runner, stage="source_resolution")
    try:
        payload = json.loads(result.stdout or "{}")
        streams = [row for row in payload.get("streams") or [] if isinstance(row, dict)]
        video = next(row for row in streams if row.get("codec_type") == "video")
        audio = next(row for row in streams if row.get("codec_type") == "audio")
        fmt = payload.get("format") or {}
        duration = float(fmt.get("duration") or video.get("duration") or 0.0)
        width = int(video.get("width") or 0)
        height = int(video.get("height") or 0)
    except (json.JSONDecodeError, StopIteration, TypeError, ValueError) as exc:
        raise RealVideoPipelineError(
            f"invalid source probe: {exc}", stage="source_resolution"
        ) from exc
    if duration <= 0 or width <= 0 or height <= 0:
        raise RealVideoPipelineError(
            "source duration or resolution is invalid", stage="source_resolution"
        )
    return {
        "duration_seconds": round(duration, 6),
        "container": fmt.get("format_name"),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"),
        "width": width,
        "height": height,
        "resolution": f"{width}x{height}",
        "aspect_ratio": round(width / height, 6),
        "pixel_format": video.get("pix_fmt"),
        "frame_rate": video.get("avg_frame_rate") or video.get("r_frame_rate"),
        "video_start_seconds": float(video.get("start_time") or 0.0),
        "audio_start_seconds": float(audio.get("start_time") or 0.0),
        "video_duration_seconds": float(video.get("duration") or duration),
        "audio_duration_seconds": float(audio.get("duration") or duration),
        "video_stream_count": sum(1 for row in streams if row.get("codec_type") == "video"),
        "audio_stream_count": sum(1 for row in streams if row.get("codec_type") == "audio"),
    }


def analyze_source(
    *,
    source_path: Path,
    duration_seconds: float,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    threshold = 0.30
    scene_command = [
        ffmpeg_path,
        "-hide_banner",
        "-nostats",
        "-i",
        str(source_path),
        "-filter:v",
        f"select='gt(scene,{threshold})',showinfo",
        "-an",
        "-f",
        "null",
        os.devnull,
    ]
    scene_result = _run(scene_command, runner=runner, stage="content_analysis")
    scene_points = sorted(
        {
            round(float(value), 3)
            for value in re.findall(r"pts_time:([0-9.]+)", scene_result.stderr or "")
            if 0.0 < float(value) < duration_seconds
        }
    )
    black_command = [
        ffmpeg_path,
        "-hide_banner",
        "-nostats",
        "-i",
        str(source_path),
        "-vf",
        "blackdetect=d=0.5:pix_th=0.10",
        "-an",
        "-f",
        "null",
        os.devnull,
    ]
    black_result = _run(black_command, runner=runner, stage="content_analysis")
    black_rows = [
        {
            "start_seconds": float(start),
            "end_seconds": float(end),
            "duration_seconds": float(duration),
        }
        for start, end, duration in re.findall(
            r"black_start:([0-9.]+).*?black_end:([0-9.]+).*?black_duration:([0-9.]+)",
            black_result.stderr or "",
        )
    ]
    silence_command = [
        ffmpeg_path,
        "-hide_banner",
        "-nostats",
        "-i",
        str(source_path),
        "-af",
        "silencedetect=noise=-50dB:d=1.0",
        "-vn",
        "-f",
        "null",
        os.devnull,
    ]
    silence_result = _run(silence_command, runner=runner, stage="content_analysis")
    silence_starts = [
        float(value)
        for value in re.findall(r"silence_start: ([0-9.]+)", silence_result.stderr or "")
    ]
    silence_ends = [
        (float(end), float(duration))
        for end, duration in re.findall(
            r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)",
            silence_result.stderr or "",
        )
    ]
    silence_rows = []
    for index, (end, duration) in enumerate(silence_ends):
        start = silence_starts[index] if index < len(silence_starts) else end - duration
        silence_rows.append(
            {
                "start_seconds": round(start, 6),
                "end_seconds": round(end, 6),
                "duration_seconds": round(duration, 6),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "source_duration_seconds": duration_seconds,
        "scene_threshold": threshold,
        "scene_boundary_count": len(scene_points),
        "scene_boundaries_seconds": scene_points,
        "black_intervals": black_rows,
        "silence_intervals": silence_rows,
        "selection_policy": "chronological_scene_boundary_partition_no_semantic_invention",
    }


def plan_timeline(
    *,
    source_identity: str,
    source_duration_seconds: float,
    scene_boundaries: list[float],
    target_duration_seconds: float,
) -> dict[str, Any]:
    if source_duration_seconds <= 0 or target_duration_seconds <= 0:
        raise RealVideoPipelineError(
            "timeline durations must be positive", stage="timeline_selection"
        )
    desired = min(source_duration_seconds, target_duration_seconds)
    source_constraint = source_duration_seconds < target_duration_seconds
    cut_count = max(MIN_CUTS, min(MAX_CUTS, int(round(desired / 24.0))))
    if desired / cut_count < MIN_CUT_SECONDS:
        cut_count = max(1, int(desired // MIN_CUT_SECONDS))
    if cut_count <= 0:
        raise RealVideoPipelineError(
            "source is too short for timeline selection", stage="timeline_selection"
        )
    clean_scene_points = sorted(
        {
            round(float(value), 6)
            for value in scene_boundaries
            if 0.0 < float(value) < source_duration_seconds
        }
    )
    cuts: list[dict[str, Any]] = []
    if desired >= source_duration_seconds - 0.05:
        boundaries = [0.0]
        previous = 0.0
        for index in range(1, cut_count):
            target = source_duration_seconds * index / cut_count
            point = _nearest_boundary(
                clean_scene_points,
                target=target,
                minimum=previous + MIN_CUT_SECONDS,
                maximum=source_duration_seconds - (cut_count - index) * MIN_CUT_SECONDS,
            )
            boundaries.append(point)
            previous = point
        boundaries.append(source_duration_seconds)
        ranges = list(zip(boundaries[:-1], boundaries[1:]))
        selection_mode = "full_source_scene_boundary_partition"
    else:
        slot = source_duration_seconds / cut_count
        segment = desired / cut_count
        ranges = []
        previous_end = 0.0
        for index in range(cut_count):
            center = (index + 0.5) * slot
            start = max(previous_end, center - segment / 2.0)
            end = min(source_duration_seconds, start + segment)
            if end - start < MIN_CUT_SECONDS:
                start = max(previous_end, end - MIN_CUT_SECONDS)
            ranges.append((start, end))
            previous_end = end
        selection_mode = "chronological_uniform_semantic_thread_sampling"
    output_cursor = 0.0
    for index, (start, end) in enumerate(ranges, start=1):
        duration = end - start
        if duration <= 0:
            raise RealVideoPipelineError(
                "timeline produced an empty cut", stage="timeline_selection"
            )
        section_index = min(2, int((index - 1) * 3 / len(ranges)))
        section = ("opening", "development", "resolution")[section_index]
        output_end = output_cursor + duration
        cuts.append(
            {
                "cut_id": f"cut_{index:03d}",
                "cut_order": index,
                "section": section,
                "source_identity": source_identity,
                "source_in_seconds": round(start, 6),
                "source_out_seconds": round(end, 6),
                "output_in_seconds": round(output_cursor, 6),
                "output_out_seconds": round(output_end, 6),
                "duration_seconds": round(duration, 6),
                "selection_reason": (
                    "chronological source interval partitioned at nearest detected scene boundary"
                    if selection_mode == "full_source_scene_boundary_partition"
                    else "chronological interval sampled across the source while preserving order"
                ),
                "continuity_context": (
                    "source_start"
                    if index == 1
                    else "chronological continuation from previous selected interval"
                ),
                "transition": "sequence_start" if index == 1 else "hard_cut",
                "caption_ids": [],
            }
        )
        output_cursor = output_end
    result = {
        "schema_version": TIMELINE_SCHEMA_VERSION,
        "source_identity": source_identity,
        "source_duration_seconds": round(source_duration_seconds, 6),
        "requested_target_duration_seconds": round(target_duration_seconds, 6),
        "output_duration_seconds": round(output_cursor, 6),
        "source_duration_constraint": source_constraint,
        "selection_mode": selection_mode,
        "chronology_preserved": True,
        "causal_order_preserved": True,
        "semantic_section_count": len({cut["section"] for cut in cuts}),
        "cut_count": len(cuts),
        "cuts": cuts,
    }
    validate_timeline_ir(result)
    return result


def validate_timeline_ir(timeline: dict[str, Any]) -> None:
    cuts = timeline.get("cuts")
    if timeline.get("schema_version") != TIMELINE_SCHEMA_VERSION or not isinstance(cuts, list):
        raise RealVideoPipelineError(
            "invalid Timeline IR schema", stage="timeline_selection"
        )
    if len(cuts) < 1 or timeline.get("cut_count") != len(cuts):
        raise RealVideoPipelineError(
            "Timeline IR cut count mismatch", stage="timeline_selection"
        )
    output_cursor = 0.0
    previous_source_end = -1.0
    for index, cut in enumerate(cuts, start=1):
        source_in = float(cut["source_in_seconds"])
        source_out = float(cut["source_out_seconds"])
        output_in = float(cut["output_in_seconds"])
        output_out = float(cut["output_out_seconds"])
        if (
            cut.get("cut_order") != index
            or source_in < previous_source_end - 0.001
            or source_out <= source_in
            or abs(output_in - output_cursor) > 0.002
            or output_out <= output_in
            or abs((source_out - source_in) - (output_out - output_in)) > 0.003
        ):
            raise RealVideoPipelineError(
                f"invalid Timeline IR cut: {cut.get('cut_id')}",
                stage="timeline_selection",
            )
        previous_source_end = source_out
        output_cursor = output_out
    if abs(output_cursor - float(timeline.get("output_duration_seconds") or 0.0)) > 0.003:
        raise RealVideoPipelineError(
            "Timeline IR output duration mismatch", stage="timeline_selection"
        )
    if len({cut.get("section") for cut in cuts}) < min(3, len(cuts)):
        raise RealVideoPipelineError(
            "Timeline IR semantic sections are incomplete", stage="timeline_selection"
        )


def load_caption_events(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = _read_json(path, "caption track")
    events: list[dict[str, Any]] = []
    for index, row in enumerate(payload.get("events") or []):
        if not isinstance(row, dict):
            continue
        text = "".join(
            str(segment.get("utf8") or "")
            for segment in row.get("segs") or []
            if isinstance(segment, dict)
        )
        text = _normalize_caption_text(text)
        duration = float(row.get("dDurationMs") or 0.0) / 1000.0
        if not text or duration <= 0:
            continue
        start = float(row.get("tStartMs") or 0.0) / 1000.0
        events.append(
            {
                "event_id": f"event_{index:06d}",
                "source_start_seconds": round(start, 6),
                "source_end_seconds": round(start + duration, 6),
                "text": text,
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )
    return events


def remap_caption_events(
    events: list[dict[str, Any]], cuts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    for event in events:
        event_start = float(event["source_start_seconds"])
        event_end = float(event["source_end_seconds"])
        for cut in cuts:
            source_in = float(cut["source_in_seconds"])
            source_out = float(cut["source_out_seconds"])
            overlap_start = max(event_start, source_in)
            overlap_end = min(event_end, source_out)
            if overlap_end - overlap_start <= 0.02:
                continue
            output_start = float(cut["output_in_seconds"]) + overlap_start - source_in
            output_end = float(cut["output_in_seconds"]) + overlap_end - source_in
            raw.append(
                {
                    "caption_id": str(event["event_id"]),
                    "cut_id": str(cut["cut_id"]),
                    "source_start_seconds": round(overlap_start, 6),
                    "source_end_seconds": round(overlap_end, 6),
                    "output_start_seconds": round(output_start, 6),
                    "output_end_seconds": round(output_end, 6),
                    "text": str(event.get("text") or ""),
                    "text_sha256": str(event["text_sha256"]),
                    "split_at_cut_boundary": (
                        overlap_start > event_start + 0.001
                        or overlap_end < event_end - 0.001
                    ),
                }
            )
    raw.sort(key=lambda row: (row["output_start_seconds"], row["output_end_seconds"]))
    merged: list[dict[str, Any]] = []
    for row in raw:
        if (
            merged
            and merged[-1]["caption_id"] == row["caption_id"]
            and abs(merged[-1]["output_end_seconds"] - row["output_start_seconds"]) <= 0.003
            and abs(merged[-1]["source_end_seconds"] - row["source_start_seconds"]) <= 0.003
        ):
            merged[-1]["source_end_seconds"] = row["source_end_seconds"]
            merged[-1]["output_end_seconds"] = row["output_end_seconds"]
            merged[-1]["cut_id"] = f"{merged[-1]['cut_id']}+{row['cut_id']}"
            merged[-1]["split_at_cut_boundary"] = True
        else:
            merged.append(dict(row))
    normalized: list[dict[str, Any]] = []
    previous_end = 0.0
    for row in merged:
        start = float(row["output_start_seconds"])
        end = float(row["output_end_seconds"])
        adjustment: str | None = None
        if start < previous_end:
            start = previous_end
            adjustment = "overlap_clipped_to_previous_output_end"
        if end - start <= 0.05:
            continue
        row["output_start_seconds"] = round(start, 6)
        row["output_end_seconds"] = round(end, 6)
        row["adjustment"] = adjustment
        row["caption_id"] = f"caption_{len(normalized) + 1:04d}"
        normalized.append(row)
        previous_end = end
    return normalized


def build_caption_readback(
    *,
    caption_mode: str,
    caption_authority: dict[str, Any],
    caption_rows: list[dict[str, Any]],
    source_caption_sha256: str | None,
    timeline_duration_seconds: float,
) -> dict[str, Any]:
    safe_rows = []
    for row in caption_rows:
        item = {key: value for key, value in row.items() if key != "text"}
        if caption_mode == "official_sidecar":
            item["text"] = row.get("text")
        safe_rows.append(item)
    overlap_count = sum(
        1
        for previous, current in zip(safe_rows, safe_rows[1:])
        if float(current["output_start_seconds"])
        < float(previous["output_end_seconds"]) - 0.001
    )
    negative_count = sum(
        1
        for row in safe_rows
        if float(row["output_start_seconds"]) < 0
        or float(row["output_end_seconds"]) <= float(row["output_start_seconds"])
    )
    orphan_count = sum(
        1
        for row in safe_rows
        if float(row["output_end_seconds"]) > timeline_duration_seconds + 0.01
    )
    status = "passed" if overlap_count == negative_count == orphan_count == 0 else "failed"
    return {
        "schema_version": CAPTION_SCHEMA_VERSION,
        "status": status,
        "mode": caption_mode,
        "authority": caption_authority,
        "source_caption_sha256": source_caption_sha256,
        "output_artifact": (
            "source_native_pixels_and_machine_readable_timing_readback"
            if caption_mode == "native_baked"
            else "captions.srt"
            if caption_mode == "official_sidecar"
            else "no_caption_authority_available"
        ),
        "cue_count": len(safe_rows),
        "overlap_count": overlap_count,
        "negative_duration_count": negative_count,
        "orphan_cue_count": orphan_count,
        "double_display_rejected": caption_mode == "native_baked",
        "items": safe_rows,
    }


def render_srt(caption_rows: list[dict[str, Any]]) -> str:
    blocks = []
    for index, row in enumerate(caption_rows, start=1):
        blocks.append(
            f"{index}\n{_srt_time(float(row['output_start_seconds']))} --> "
            f"{_srt_time(float(row['output_end_seconds']))}\n"
            f"{row.get('text') or ''}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def build_edit_pack(
    timeline: dict[str, Any], resolved: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": EDIT_PACK_SCHEMA_VERSION,
        "source_identity": resolved["source_identity"],
        "profile": PROFILE_LONG_FORM,
        "selected_cut_ids": [cut["cut_id"] for cut in timeline["cuts"]],
        "cut_candidates": [
            {
                "id": cut["cut_id"],
                "decision": "selected_by_out12_automation",
                "section": cut["section"],
                "source_start_seconds": cut["source_in_seconds"],
                "source_end_seconds": cut["source_out_seconds"],
                "output_start_seconds": cut["output_in_seconds"],
                "output_end_seconds": cut["output_out_seconds"],
                "reason": cut["selection_reason"],
                "caption_ids": cut["caption_ids"],
            }
            for cut in timeline["cuts"]
        ],
        "caption_authority": resolved["caption_authority"],
        "production_candidate": False,
        "rights_status": resolved["rights"]["status"],
    }


def render_timeline(
    *,
    source_path: Path,
    video_path: Path,
    cuts: list[dict[str, Any]],
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    work = video_path.parent / ".render_work"
    work.mkdir()
    filter_path = work / "filter_complex.txt"
    filter_text = render_filter_complex(cuts)
    _write_text(filter_path, filter_text)
    attempts = []
    for codec in ("libx264", "libopenh264"):
        command = [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-i",
            str(source_path),
            "-filter_complex_script",
            str(filter_path),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            codec,
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(video_path),
        ]
        result = _run(
            command,
            runner=runner,
            stage="render",
            allow_failure=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
        passed = result.returncode == 0 and video_path.is_file()
        attempts.append(
            {
                "codec": codec,
                "status": "passed" if passed else "failed",
                "exit_code": result.returncode,
                "stderr_sha256": hashlib.sha256(
                    (result.stderr or "").encode("utf-8")
                ).hexdigest(),
            }
        )
        if passed:
            shutil.rmtree(work)
            return {
                "status": "passed",
                "selected_video_encoder": codec,
                "audio_encoder": "aac",
                "attempts": attempts,
                "execution_count": 1,
                "corrective_pass_count": 0,
            }
        if video_path.exists():
            video_path.unlink()
    shutil.rmtree(work)
    raise RealVideoPipelineError(
        "FFmpeg timeline render failed for all H.264 profiles", stage="render"
    )


def render_filter_complex(cuts: list[dict[str, Any]]) -> str:
    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, cut in enumerate(cuts):
        start = _seconds(float(cut["source_in_seconds"]))
        end = _seconds(float(cut["source_out_seconds"]))
        filters.append(
            f"[0:v:0]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{index}]"
        )
        filters.append(
            f"[0:a:0]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{index}]"
        )
        concat_inputs.extend((f"[v{index}]", f"[a{index}]"))
    filters.append(
        f"{''.join(concat_inputs)}concat=n={len(cuts)}:v=1:a=1[vcat][acat]"
    )
    filters.append("[vcat]format=yuv420p[vout]")
    filters.append("[acat]loudnorm=I=-15:TP=-2.0:LRA=11[aout]")
    return ";\n".join(filters) + "\n"


def validate_rendered_video(
    *,
    video_path: Path,
    timeline: dict[str, Any],
    caption_readback: dict[str, Any],
    source_probe: dict[str, Any],
    ffmpeg_path: str,
    ffprobe_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    media = probe_media_detail(video_path, ffprobe_path=ffprobe_path, runner=runner)
    detail_command = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=pix_fmt,profile,level",
        "-of",
        "json",
        str(video_path),
    ]
    detail_result = _run(detail_command, runner=runner, stage="media_validation")
    detail = json.loads(detail_result.stdout or "{}").get("streams", [{}])[0]
    media.update(
        {
            "pixel_format": detail.get("pix_fmt"),
            "video_profile": detail.get("profile"),
            "video_level": detail.get("level"),
            "sha256": _sha256(video_path),
            "byte_size": video_path.stat().st_size,
        }
    )
    decode = _run(
        [
            ffmpeg_path,
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(video_path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-f",
            "null",
            os.devnull,
        ],
        runner=runner,
        stage="media_validation",
        allow_failure=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )
    full_decode = {
        "status": "passed" if decode.returncode == 0 else "failed",
        "exit_code": decode.returncode,
        "stderr_empty": not bool((decode.stderr or "").strip()),
    }
    faststart = _faststart_readback(video_path)
    timestamp_readback = validate_packet_timestamps(
        video_path=video_path, ffprobe_path=ffprobe_path, runner=runner
    )
    av_sync_delta = abs(
        float(media["video_duration_seconds"])
        - float(media["audio_duration_seconds"])
    )
    av_start_delta = abs(
        float(media["video_start_seconds"]) - float(media["audio_start_seconds"])
    )
    loudness = _measure_loudness(
        ffmpeg_path=ffmpeg_path,
        input_path=video_path,
        timeline=None,
        runner=runner,
    )
    signal = _run_signal_qa(
        video_path=video_path,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    cut_loudness = measure_cut_loudness(
        video_path=video_path,
        cuts=timeline["cuts"],
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    duration_delta = abs(
        float(media["duration_seconds"])
        - float(timeline["output_duration_seconds"])
    )
    aspect_preserved = (
        media["width"] == source_probe["width"]
        and media["height"] == source_probe["height"]
    )
    checks = {
        "shipping_codec": media["video_codec"] == "h264"
        and media["audio_codec"] == "aac",
        "source_native_aspect": aspect_preserved,
        "duration": duration_delta <= 0.75,
        "stream_start": av_start_delta <= 0.05,
        "monotonic_timestamps": timestamp_readback["status"] == "passed",
        "faststart": faststart["status"] == "passed",
        "full_decode": full_decode["status"] == "passed",
        "av_sync": av_sync_delta <= 0.10,
        "loudness": -16.0 <= loudness["integrated_lufs"] <= -12.0
        and loudness["true_peak_dbtp"] <= -1.0,
        "cut_loudness_delta": cut_loudness["maximum_adjacent_delta_lu"] <= 6.0,
        "black_silence": signal["status"] == "passed",
        "caption_containment": caption_readback["status"] == "passed",
        "source_mapping_coverage": validate_mapping_coverage(timeline),
    }
    status = "passed" if all(checks.values()) else "failed"
    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "status": status,
        "state": READY_STATE if status == "passed" else "OUT12_VALIDATION_FAILED",
        "checks": checks,
        "media": media,
        "expected_duration_seconds": timeline["output_duration_seconds"],
        "duration_delta_seconds": round(duration_delta, 6),
        "full_decode": full_decode,
        "faststart": faststart,
        "timestamp_readback": timestamp_readback,
        "av_sync": {
            "duration_delta_seconds": round(av_sync_delta, 6),
            "start_delta_seconds": round(av_start_delta, 6),
        },
        "loudness": loudness,
        "cut_loudness": cut_loudness,
        "signal_qa": signal,
        "caption_validation": {
            "status": caption_readback["status"],
            "cue_count": caption_readback["cue_count"],
            "overlap_count": caption_readback["overlap_count"],
            "negative_duration_count": caption_readback["negative_duration_count"],
            "orphan_cue_count": caption_readback["orphan_cue_count"],
        },
        "mapping_coverage": mapping_coverage(timeline),
        "closed_gates": _closed_gates(),
    }


def validate_packet_timestamps(
    *, video_path: Path, ffprobe_path: str, runner: ffmpeg_tiny.Runner
) -> dict[str, Any]:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-show_packets",
        "-show_entries",
        "packet=stream_index,dts_time",
        "-of",
        "json",
        str(video_path),
    ]
    result = _run(command, runner=runner, stage="media_validation")
    payload = json.loads(result.stdout or "{}")
    previous: dict[int, float] = {}
    regressions = 0
    packet_count = 0
    for row in payload.get("packets") or []:
        if not isinstance(row, dict) or row.get("dts_time") in (None, "N/A"):
            continue
        stream = int(row.get("stream_index") or 0)
        value = float(row["dts_time"])
        if stream in previous and value < previous[stream] - 0.000001:
            regressions += 1
        previous[stream] = value
        packet_count += 1
    return {
        "status": "passed" if packet_count > 0 and regressions == 0 else "failed",
        "packet_count": packet_count,
        "regression_count": regressions,
    }


def measure_cut_loudness(
    *,
    video_path: Path,
    cuts: list[dict[str, Any]],
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    rows = []
    for cut in cuts:
        start = float(cut["output_in_seconds"])
        duration = float(cut["duration_seconds"])
        command = [
            ffmpeg_path,
            "-hide_banner",
            "-nostats",
            "-ss",
            _seconds(start),
            "-t",
            _seconds(duration),
            "-i",
            str(video_path),
            "-map",
            "0:a:0",
            "-af",
            "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            os.devnull,
        ]
        result = _run(command, runner=runner, stage="media_validation")
        match = re.search(r"\{\s*\"input_i\".*?\}", result.stderr or "", flags=re.DOTALL)
        if match is None:
            raise RealVideoPipelineError(
                "cut loudness JSON was not found", stage="media_validation"
            )
        payload = json.loads(match.group(0))
        rows.append(
            {
                "cut_id": cut["cut_id"],
                "integrated_lufs": float(payload["input_i"]),
                "true_peak_dbtp": float(payload["input_tp"]),
            }
        )
    deltas = [
        abs(current["integrated_lufs"] - previous["integrated_lufs"])
        for previous, current in zip(rows, rows[1:])
    ]
    return {
        "status": "passed" if max(deltas, default=0.0) <= 6.0 else "failed",
        "rows": rows,
        "maximum_adjacent_delta_lu": round(max(deltas, default=0.0), 3),
    }


def mapping_coverage(timeline: dict[str, Any]) -> dict[str, Any]:
    total = sum(float(cut["duration_seconds"]) for cut in timeline["cuts"])
    output = float(timeline["output_duration_seconds"])
    return {
        "mapped_seconds": round(total, 6),
        "output_seconds": round(output, 6),
        "coverage_ratio": round(total / output, 9) if output else 0.0,
        "unmapped_output_seconds": round(max(0.0, output - total), 6),
    }


def validate_mapping_coverage(timeline: dict[str, Any]) -> bool:
    coverage = mapping_coverage(timeline)
    return (
        coverage["coverage_ratio"] >= 0.999999
        and coverage["unmapped_output_seconds"] <= 0.003
    )


def build_review_package(
    *,
    stage: Path,
    timeline: dict[str, Any],
    resolved: dict[str, Any],
    validation: dict[str, Any],
    review_port: int,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    review = stage / "review"
    evidence = review / "evidence"
    evidence.mkdir(parents=True)
    duration = float(validation["media"]["duration_seconds"])
    boundary_times = [
        float(cut["output_out_seconds"])
        for cut in timeline["cuts"][:-1]
    ]
    first_middle_last = [0.5, duration / 2.0, max(0.0, duration - 0.5)]
    contact = evidence / "first_middle_last_contact_sheet.jpg"
    render_contact_sheet(
        video_path=stage / "final_video.mp4",
        output_path=contact,
        sample_times=first_middle_last,
        fps=_frame_rate_float(validation["media"].get("frame_rate")),
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    boundary_samples = []
    for value in boundary_times:
        boundary_samples.extend((max(0.0, value - 0.12), min(duration - 0.02, value + 0.12)))
    boundary_contact = evidence / "cut_boundary_contact_sheet.jpg"
    render_contact_sheet(
        video_path=stage / "final_video.mp4",
        output_path=boundary_contact,
        sample_times=boundary_samples,
        fps=_frame_rate_float(validation["media"].get("frame_rate")),
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    waveform = evidence / "waveform.png"
    waveform_result = _run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-i",
            str(stage / "final_video.mp4"),
            "-filter_complex",
            "aformat=channel_layouts=mono,showwavespic=s=1600x320:colors=0x38BDF8",
            "-frames:v",
            "1",
            str(waveform),
        ],
        runner=runner,
        stage="review_package",
        allow_failure=True,
    )
    if waveform_result.returncode != 0 or not waveform.is_file():
        raise RealVideoPipelineError(
            "review waveform generation failed", stage="review_package"
        )
    _write_text(review / "index.html", render_review_html(timeline, resolved, validation))
    _write_text(review / "serve_preview.ps1", render_serve_script(review_port))
    _write_text(review / "open_preview.ps1", render_open_script(review_port))
    return {
        "index": "review/index.html",
        "open_command": "review/open_preview.ps1",
        "clean_url": f"http://127.0.0.1:{review_port}/review/index.html",
        "first_middle_last_contact_sheet": "review/evidence/first_middle_last_contact_sheet.jpg",
        "cut_boundary_contact_sheet": "review/evidence/cut_boundary_contact_sheet.jpg",
        "waveform": "review/evidence/waveform.png",
    }


def render_contact_sheet(
    *,
    video_path: Path,
    output_path: Path,
    sample_times: list[float],
    fps: float,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> None:
    unique_frames = sorted({max(0, int(round(value * fps))) for value in sample_times})
    if not unique_frames:
        raise RealVideoPipelineError(
            "contact sheet has no samples", stage="review_package"
        )
    columns = min(4, len(unique_frames))
    rows = int(math.ceil(len(unique_frames) / columns))
    expression = "+".join(f"eq(n\\,{value})" for value in unique_frames)
    vf = (
        f"select='{expression}',scale=480:-2,"
        f"tile={columns}x{rows}:padding=8:margin=8:color=0x111827"
    )
    result = _run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-i",
            str(video_path),
            "-vf",
            vf,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ],
        runner=runner,
        stage="review_package",
        allow_failure=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )
    if result.returncode != 0 or not output_path.is_file():
        raise RealVideoPipelineError(
            "contact sheet generation failed", stage="review_package"
        )


def render_review_html(
    timeline: dict[str, Any], resolved: dict[str, Any], validation: dict[str, Any]
) -> str:
    rows = []
    for cut in timeline["cuts"]:
        rows.append(
            "<tr>"
            f"<td>{escape(cut['cut_id'])}</td>"
            f"<td>{escape(cut['section'])}</td>"
            f"<td>{float(cut['source_in_seconds']):.3f}–{float(cut['source_out_seconds']):.3f}</td>"
            f"<td>{float(cut['output_in_seconds']):.3f}–{float(cut['output_out_seconds']):.3f}</td>"
            f"<td><button type=\"button\" data-seek=\"{float(cut['output_in_seconds']):.3f}\">seek</button></td>"
            "</tr>"
        )
    checks = "".join(
        f"<li>{escape(name)}: {'pass' if value else 'fail'}</li>"
        for name, value in validation["checks"].items()
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-12 real video review</title>
<style>body{{margin:0;background:#0b1020;color:#e5edf8;font-family:system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:24px;box-sizing:border-box}}video{{display:block;width:100%;max-height:70vh;background:#000}}table{{display:block;width:100%;max-width:100%;overflow-x:auto;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #334155;text-align:left;white-space:nowrap}}code{{overflow-wrap:anywhere}}details{{margin-top:18px}}img{{width:100%;height:auto}}button{{padding:6px 10px}}</style></head>
<body><main><h1>OUT-12 One-Command Real Video Automation v1</h1>
<p>{escape(resolved['source_identity'])} · {float(validation['media']['duration_seconds']):.3f}s · {len(timeline['cuts'])} cuts · {validation['media']['resolution']}</p>
<video id="finalVideo" controls muted preload="metadata" playsinline src="../final_video.mp4"></video>
<p>SHA-256 <code>{escape(validation['media']['sha256'])}</code></p>
<h2>Section / cut map</h2><table><thead><tr><th>cut</th><th>section</th><th>source</th><th>output</th><th></th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<details><summary>検証証拠</summary><ul>{checks}</ul><p>caption authority: {escape(resolved['caption_mode'])}; rights: {escape(resolved['rights']['status'])}; production/public acceptance: closed.</p>
<img src="evidence/first_middle_last_contact_sheet.jpg" alt="first middle last contact sheet"><img src="evidence/cut_boundary_contact_sheet.jpg" alt="cut boundary contact sheet"><img src="evidence/waveform.png" alt="waveform"></details>
</main><script>const v=document.getElementById('finalVideo');v.autoplay=false;v.muted=true;v.volume=0.25;v.currentTime=0;document.querySelectorAll('[data-seek]').forEach(b=>b.addEventListener('click',()=>{{v.pause();v.currentTime=Number(b.dataset.seek);}}));</script></body></html>
"""


def render_serve_script(port: int) -> str:
    return f"""param([int]$Port = {port})
$reviewDir = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$outputDir = (Resolve-Path -LiteralPath (Join-Path $reviewDir '..')).Path
$cursor = Get-Item -LiteralPath $outputDir
while ($null -ne $cursor -and -not (Test-Path -LiteralPath (Join-Path $cursor.FullName 'src\\cli\\main.py'))) {{ $cursor = $cursor.Parent }}
if ($null -eq $cursor) {{ throw 'ClipPipeGen repository root not found' }}
Push-Location $cursor.FullName
try {{ uvx python -m src.cli.serve_review --root $outputDir --port $Port }} finally {{ Pop-Location }}
"""


def render_open_script(port: int) -> str:
    return f"""param([int]$Port = {port})
$url = "http://127.0.0.1:$Port/review/index.html"
Start-Process $url
& (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
"""


def build_run_manifest(
    *,
    stage: Path,
    input_fingerprint: str,
    resolved: dict[str, Any],
    timeline: dict[str, Any],
    validation: dict[str, Any],
    review: dict[str, Any],
    stages: list[dict[str, Any]],
) -> dict[str, Any]:
    files = []
    for path in sorted(item for item in stage.rglob("*") if item.is_file()):
        if path.name == "run_manifest.json" or ".render_work" in path.parts:
            continue
        files.append(
            {
                "repo_relative_path": path.relative_to(stage).as_posix(),
                "sha256": _sha256(path),
                "byte_size": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": "clip-out12-one-command-real-video-automation-v1-001",
        "state": READY_STATE,
        "input_fingerprint": input_fingerprint,
        "source_identity": resolved["source_identity"],
        "source_sha256": resolved["source_sha256"],
        "profile": PROFILE_LONG_FORM,
        "final_video": {
            "path": "final_video.mp4",
            "sha256": validation["media"]["sha256"],
            "byte_size": validation["media"]["byte_size"],
            "duration_seconds": validation["media"]["duration_seconds"],
            "resolution": validation["media"]["resolution"],
            "cut_count": timeline["cut_count"],
        },
        "caption_authority": resolved["caption_authority"],
        "stages": stages,
        "review": review,
        "validation_status": validation["status"],
        "files": files,
        "file_count": len(files),
        "closed_gates": _closed_gates(),
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    manifest["manifest_self_integrity"]["sha256"] = _canonical_manifest_self_hash(
        manifest
    )
    return manifest


def validate_run_manifest(stage: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise RealVideoPipelineError(
            "run manifest schema mismatch", stage="manifest"
        )
    rows = manifest.get("files") or []
    if manifest.get("file_count") != len(rows):
        raise RealVideoPipelineError(
            "run manifest file count mismatch", stage="manifest"
        )
    for row in rows:
        path = (stage / str(row.get("repo_relative_path") or "")).resolve()
        try:
            path.relative_to(stage.resolve())
        except ValueError as exc:
            raise RealVideoPipelineError(
                "run manifest path leaves package", stage="manifest"
            ) from exc
        if (
            not path.is_file()
            or _sha256(path) != row.get("sha256")
            or path.stat().st_size != int(row.get("byte_size") or -1)
        ):
            raise RealVideoPipelineError(
                f"run manifest payload mismatch: {row.get('repo_relative_path')}",
                stage="manifest",
            )
    if (manifest.get("manifest_self_integrity") or {}).get(
        "sha256"
    ) != _canonical_manifest_self_hash(manifest):
        raise RealVideoPipelineError(
            "run manifest self-integrity mismatch", stage="manifest"
        )


def resume_existing_output(
    *, output_dir: Path, input_fingerprint: str, root: Path
) -> dict[str, Any]:
    manifest_path = output_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise RealVideoPipelineError(
            "resume requested but run_manifest.json is missing", stage="resume"
        )
    manifest = _read_json(manifest_path, "run manifest")
    if manifest.get("input_fingerprint") != input_fingerprint:
        raise RealVideoPipelineError(
            "resume input fingerprint mismatch; use --force for a new run",
            stage="resume",
        )
    validate_run_manifest(output_dir, manifest)
    video = output_dir / "final_video.mp4"
    if _sha256(video) != (manifest.get("final_video") or {}).get("sha256"):
        raise RealVideoPipelineError(
            "resume final video hash mismatch", stage="resume"
        )
    high_cost = ("content_analysis", "caption_remap", "render", "media_validation")
    readback = {
        "schema_version": SCHEMA_VERSION,
        "state": READY_STATE,
        "input_fingerprint": input_fingerprint,
        "resume": True,
        "cache_hits": list(high_cost),
        "skipped_stages": list(high_cost),
        "render_executed": False,
        "final_video_sha256": _sha256(video),
        "verified_manifest_self_sha256": (
            manifest.get("manifest_self_integrity") or {}
        ).get("sha256"),
    }
    _write_json(output_dir / "resume_readback.json", readback)
    return {
        "artifact_id": manifest["artifact_id"],
        "state": READY_STATE,
        "output_dir": output_dir,
        "final_video": video,
        "timeline_ir": output_dir / "timeline_ir.json",
        "edit_pack": output_dir / "edit_pack.json",
        "caption_readback": output_dir / "caption_readback.json",
        "run_manifest": manifest_path,
        "validation_readback": output_dir / "validation_readback.json",
        "review_index": output_dir / "review" / "index.html",
        "source_identity": manifest["source_identity"],
        "duration_seconds": manifest["final_video"]["duration_seconds"],
        "cut_count": manifest["final_video"]["cut_count"],
        "video_sha256": manifest["final_video"]["sha256"],
        "resume": True,
        "cache_hits": list(high_cost),
        "render_executed": False,
        "resume_readback": output_dir / "resume_readback.json",
    }


def promote_output(*, stage: Path, output: Path, force: bool) -> None:
    backup: Path | None = None
    if output.exists():
        if not force:
            raise RealVideoPipelineError(
                "output already exists", stage="manifest"
            )
        if not (
            (output / "run_manifest.json").is_file()
            or (output / "pipeline_failure.json").is_file()
        ):
            raise RealVideoPipelineError(
                "refusing to replace an unrecognized output directory",
                stage="manifest",
            )
        backup = output.parent / f".{output.name}.backup-{uuid.uuid4().hex}"
        output.replace(backup)
    try:
        stage.replace(output)
    except Exception:
        if backup is not None and backup.exists() and not output.exists():
            backup.replace(output)
        raise
    if backup is not None and backup.exists():
        shutil.rmtree(backup)


def write_failure_state(
    *,
    output_dir: Path,
    stage: str,
    message: str,
    input_fingerprint: str | None,
    failure_evidence_dir: Path | None = None,
) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "state": "OUT12_PIPELINE_FAILED",
        "ready": False,
        "failure_stage": stage,
        "message": message,
        "input_fingerprint": input_fingerprint,
        "failure_evidence_dir": (
            str(failure_evidence_dir).replace("\\", "/")
            if failure_evidence_dir is not None
            else None
        ),
    }
    try:
        if output_dir.exists() and (output_dir / "run_manifest.json").is_file():
            _write_json(output_dir.parent / f".{output_dir.name}.failure.json", payload)
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            _write_json(output_dir / "pipeline_failure.json", payload)
    except OSError:
        pass


def content_fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _nearest_boundary(
    points: list[float], *, target: float, minimum: float, maximum: float
) -> float:
    eligible = [value for value in points if minimum <= value <= maximum]
    if eligible:
        nearest = min(eligible, key=lambda value: (abs(value - target), value))
        if abs(nearest - target) <= 8.0:
            return nearest
    return min(max(target, minimum), maximum)


def _attach_caption_ids(
    cuts: list[dict[str, Any]], caption_rows: list[dict[str, Any]]
) -> None:
    for cut in cuts:
        output_in = float(cut["output_in_seconds"])
        output_out = float(cut["output_out_seconds"])
        cut["caption_ids"] = [
            row["caption_id"]
            for row in caption_rows
            if float(row["output_end_seconds"]) > output_in
            and float(row["output_start_seconds"]) < output_out
        ]


def _authority_input_path(payload: dict[str, Any], role: str) -> Path | None:
    for row in payload.get("input_integrity") or []:
        if isinstance(row, dict) and row.get("role") == role and row.get("path"):
            return Path(str(row["path"]))
    return None


def _identity_from_rights(payload: dict[str, Any]) -> str | None:
    url = str((payload.get("source_video") or {}).get("url") or "")
    if not url:
        return None
    parsed = urlparse(url)
    provider_id = (parse_qs(parsed.query).get("v") or [None])[0]
    if provider_id:
        return f"youtube:{provider_id}"
    return None


def _discover_caption_track(episode: Path | None, source_identity: str) -> Path | None:
    if episode is None:
        return None
    source_subs = episode / "source_subs"
    if not source_subs.is_dir():
        return None
    provider_id = source_identity.partition(":")[2]
    matches = sorted(source_subs.glob(f"{provider_id}.*.json3")) if provider_id else []
    if len(matches) == 1:
        return matches[0]
    all_tracks = sorted(source_subs.glob("*.json3"))
    return all_tracks[0] if len(all_tracks) == 1 else None


def _infer_episode_dir(source: Path) -> Path | None:
    parents = list(source.parents)
    for parent in parents:
        if parent.name == "materials" and parent.parent.is_dir():
            return parent.parent
    return None


def _closed_gates() -> dict[str, Any]:
    return {
        "rights_status": "pending_or_snapshot_only",
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "thumbnail_acceptance": False,
        "winner_selected": False,
        "public_or_publishing_acceptance": False,
        "upload_attempted": False,
    }


def _display_path(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RealVideoPipelineError(
            f"invalid {label}: {exc}", stage="source_resolution"
        ) from exc
    if not isinstance(payload, dict):
        raise RealVideoPipelineError(
            f"{label} must be an object", stage="source_resolution"
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(
    command: list[str],
    *,
    runner: ffmpeg_tiny.Runner,
    stage: str,
    allow_failure: bool = False,
    timeout: int = COMMAND_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[str]:
    try:
        result = runner(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RealVideoPipelineError(
            f"external command failed before exit: {exc}", stage=stage
        ) from exc
    if result.returncode != 0 and not allow_failure:
        digest = hashlib.sha256((result.stderr or "").encode("utf-8")).hexdigest()
        raise RealVideoPipelineError(
            f"external command failed: exit={result.returncode}; stderr_sha256={digest}",
            stage=stage,
        )
    return result


def _normalize_caption_text(value: str) -> str:
    return (
        value.replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u2060", "")
        .replace("\ufeff", "")
        .strip()
    )


def _frame_rate_float(value: Any) -> float:
    text = str(value or "30/1")
    numerator, separator, denominator = text.partition("/")
    try:
        return float(numerator) / float(denominator) if separator else float(text)
    except (TypeError, ValueError, ZeroDivisionError):
        return 30.0


def _srt_time(value: float) -> str:
    milliseconds = max(0, int(round(value * 1000.0)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def _seconds(value: float) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".")
