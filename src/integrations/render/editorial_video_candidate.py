"""OUT-13 explicit editorial-plan real-video candidate pipeline."""

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

from src.integrations.render import ffmpeg_tiny
from src.integrations.render import real_video_pipeline as out12
from src.integrations.render.subtitle_overlay_visual_proof import (
    ED10L_KEIFONT_CANDIDATE_ID,
    _diagnostic_ass_style_for_candidate,
    _presentation_items,
    _subtitle_layout_contract,
    _write_ass,
)
from src.integrations.render.subtitle_preset_selector import select_subtitle_preset
from src.pipeline.transcript import validate_transcript

SCHEMA_VERSION = "clippipegen.out13.editorial_video_candidate.v2"
PLAN_SCHEMA_VERSION = "clippipegen.out13.editorial_plan.v2"
TIMELINE_SCHEMA_VERSION = "clippipegen.timeline_ir.v1"
SUBTITLE_READBACK_SCHEMA_VERSION = "clippipegen.out13.subtitle_presentation.v1"
MANIFEST_SCHEMA_VERSION = "clippipegen.out13.run_manifest.v2"
PIPELINE_VERSION = "out13-editorial-video-candidate-v2"
# Historical default retained only so old reports/tests can identify artifact 001.
# New CLI runs must pass an explicit immutable artifact identity.
ARTIFACT_ID = "clip-out13-editorial-video-candidate-v1-001"
ARTIFACT_ID_PATTERN = re.compile(r"^clip-out13-editorial-video-candidate-v1-\d{3}$")
SUPPORTED_TRANSITIONS = frozenset({"sequence_start", "hard_cut"})
READY_STATE = "OUT13_EVIDENCE_BOUND_REVIEWABLE_ON_THANK_V1"
DEFAULT_REVIEW_PORT = 8076
MIN_OUTPUT_SECONDS = 60.0
MAX_OUTPUT_SECONDS = 180.0
MIN_SELECTED_CUTS = 3
MIN_INTENTIONAL_OMITTED_SPANS = 2
MAX_SOURCE_UTILIZATION_RATIO = 0.90
EDITORIAL_FONT_SIZE_TO_FRAME_HEIGHT = 0.093


class EditorialVideoCandidateError(Exception):
    """Raised when an OUT-13 stage cannot produce reviewable evidence."""

    def __init__(self, message: str, *, stage: str = "unknown") -> None:
        super().__init__(message)
        self.stage = stage


def build_editorial_video_candidate(
    *,
    artifact_id: str,
    source_path: Path,
    editorial_plan_path: Path,
    transcript_path: Path,
    caption_track_path: Path,
    rights_manifest_path: Path,
    output_dir: Path,
    source_identity: str | None = None,
    resume: bool = False,
    force: bool = False,
    review_port: int = DEFAULT_REVIEW_PORT,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
) -> dict[str, Any]:
    """Build one caption-evidence-bound editorial representative video."""

    started = time.monotonic()
    root = (base_dir or Path.cwd()).resolve()
    output = _resolved(root, output_dir)
    stage: Path | None = None
    fingerprint: str | None = None
    current_stage = "source_resolution"
    try:
        _validate_artifact_id(artifact_id)
        if resume and force:
            raise EditorialVideoCandidateError(
                "--resume and --force are mutually exclusive", stage=current_stage
            )
        if not 1 <= int(review_port) <= 65535:
            raise EditorialVideoCandidateError(
                "review port must be between 1 and 65535", stage=current_stage
            )
        tools = ffmpeg_tiny.preflight_tools(
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        if tools.get("status") != "passed":
            raise EditorialVideoCandidateError(
                f"FFmpeg preflight failed: {tools.get('failure_reason')}",
                stage=current_stage,
            )
        ffmpeg = str(tools["ffmpeg"]["path"])
        ffprobe = str(tools["ffprobe"]["path"])
        source = _resolved(root, source_path)
        plan_path = _resolved(root, editorial_plan_path)
        transcript = _resolved(root, transcript_path)
        caption_track = _resolved(root, caption_track_path)
        rights_manifest = _resolved(root, rights_manifest_path)
        resolved = out12.resolve_source(
            root=root,
            source_path=source,
            intake_identity=None,
            source_identity=source_identity,
            rights_manifest_path=rights_manifest,
            caption_track_path=caption_track,
            authority_readback_path=None,
            caption_mode="sidecar",
        )
        if resolved["caption_track_path"] is None:
            raise EditorialVideoCandidateError(
                "OUT-13 requires a provider/provenance-bound sidecar caption track",
                stage=current_stage,
            )
        source_probe = out12.probe_media_detail(
            resolved["source_path"], ffprobe_path=ffprobe, runner=runner
        )
        if source_probe["video_stream_count"] != 1 or source_probe["audio_stream_count"] != 1:
            raise EditorialVideoCandidateError(
                "source must contain exactly one primary video and audio stream",
                stage=current_stage,
            )
        plan = _read_json(plan_path, "editorial plan")
        transcript_payload = _read_json(transcript, "transcript")
        transcript_issues = validate_transcript(transcript_payload)
        if transcript_issues:
            issue = transcript_issues[0]
            raise EditorialVideoCandidateError(
                f"canonical transcript validation failed: {issue.code} ({issue.field})",
                stage=current_stage,
            )
        caption_events = out12.load_caption_events(resolved["caption_track_path"])
        authority_binding = _validate_authority_binding(
            root=root,
            plan=plan,
            artifact_id=artifact_id,
            resolved=resolved,
            transcript_path=transcript,
            transcript=transcript_payload,
            caption_track_path=caption_track,
            rights_manifest_path=rights_manifest,
        )
        timeline = build_editorial_timeline(
            plan=plan,
            source_identity=resolved["source_identity"],
            source_sha256=resolved["source_sha256"],
            source_duration_seconds=float(source_probe["duration_seconds"]),
            transcript=transcript_payload,
            caption_events=caption_events,
        )
        style = _diagnostic_ass_style_for_candidate(ED10L_KEIFONT_CANDIDATE_ID)
        font_file = Path(str(style.get("resolved_font_file") or ""))
        font_sha256 = _sha256(font_file) if font_file.is_file() else None
        _validate_font_binding(
            plan=plan,
            artifact_id=artifact_id,
            style=style,
            font_sha256=font_sha256,
        )
        fingerprint_payload = {
            "artifact_id": artifact_id,
            "pipeline_version": PIPELINE_VERSION,
            "source_identity": resolved["source_identity"],
            "source_sha256": resolved["source_sha256"],
            "source_probe": source_probe,
            "editorial_plan_sha256": _sha256(plan_path),
            "transcript_sha256": _sha256(transcript),
            "caption_sha256": resolved["caption_sha256"],
            "rights_sha256": resolved["rights_sha256"],
            "typography_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
            "resolved_font_file_sha256": font_sha256,
            "authority_binding": authority_binding,
            "review_port": int(review_port),
        }
        fingerprint = out12.content_fingerprint(fingerprint_payload)
        if resume:
            resumed = resume_existing_output(
                output_dir=output,
                input_fingerprint=fingerprint,
                artifact_id=artifact_id,
            )
            resumed["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return resumed
        _validate_output_allocation(output=output, artifact_id=artifact_id, force=force)
        output.parent.mkdir(parents=True, exist_ok=True)
        stage = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
        stage.mkdir()

        _write_json(stage / "editorial_plan.json", plan)
        _write_json(stage / "timeline_ir.json", timeline)
        _write_json(
            stage / "provenance_snapshot.json",
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": artifact_id,
                "source_identity": resolved["source_identity"],
                "provider_locator": (plan.get("source") or {}).get("provider_locator"),
                "source_path": _display_path(resolved["source_path"], root),
                "source_sha256": resolved["source_sha256"],
                "source_byte_size": resolved["source_byte_size"],
                "source_probe": source_probe,
                "caption_authority": {
                    **authority_binding["caption"],
                    "overlay_burn_in_applied": True,
                    "native_dialogue_caption_pixels_observed_in_selected_ranges": None,
                    "double_display_status": "unverified",
                },
                "transcript": {
                    "path": _display_path(transcript, root),
                    "sha256": _sha256(transcript),
                    "engine": (transcript_payload.get("stt") or {}).get("engine"),
                    "selected_segment_count": len(_selected_transcript_segments(timeline)),
                },
                "rights": resolved["rights"],
                "authority_binding": authority_binding,
                "visual_observation": {
                    "status": "unverified",
                    "observation_class": "none",
                    "machine_validation_passed": False,
                    "note": "No visual observation result is inferred from machine validation.",
                },
                "closed_gates": _closed_gates(),
            },
        )
        _write_json(stage / "authority_binding.json", authority_binding)
        _write_json(
            stage / "transcript_authority_snapshot.json",
            {
                "schema_version": SCHEMA_VERSION,
                "source_transcript_sha256": _sha256(transcript),
                "segments": _selected_transcript_segments(timeline),
                "authority_scope": "caption_text_and_timing_only_no_speaker_or_lyric_inference",
            },
        )

        current_stage = "caption_remap_and_presentation"
        caption_rows = out12.remap_caption_events(caption_events, timeline["cuts"])
        _attach_caption_ids(timeline["cuts"], caption_rows)
        out12.validate_timeline_ir(timeline)
        _write_json(stage / "timeline_ir.json", timeline)
        caption_authority = {
            **authority_binding["caption"],
            "overlay_burn_in_applied": True,
            "duplicate_overlay_rejected": False,
            "native_pixels_preserved": False,
            "double_display_status": "unverified",
        }
        caption_readback = out12.build_caption_readback(
            caption_mode="official_sidecar",
            caption_authority=caption_authority,
            caption_rows=caption_rows,
            source_caption_sha256=resolved["caption_sha256"],
            timeline_duration_seconds=float(timeline["output_duration_seconds"]),
        )
        _apply_out13_caption_integrity(
            caption_readback=caption_readback,
            caption_rows=caption_rows,
            caption_events=caption_events,
            cuts=timeline["cuts"],
        )
        _write_json(stage / "caption_readback.json", caption_readback)
        _write_text(stage / "captions.srt", out12.render_srt(caption_rows))
        layout = _editorial_subtitle_layout_contract(
            frame_width=int(source_probe["width"]),
            frame_height=int(source_probe["height"]),
            dimension_source="ffprobe_source_video",
            diagnostic_ass_style=style,
        )
        raw_subtitle_items = [
            {
                "subtitle_id": row["caption_id"],
                "cut_id": row["cut_id"],
                "status": "included",
                "render_start_seconds": row["output_start_seconds"],
                "render_end_seconds": row["output_end_seconds"],
                "text": _caption_text_for_presentation(row["text"]),
                "authority_text": row["text"],
                "source_type": authority_binding["caption"]["classification"],
                "source_segment_ids": _transcript_ids_for_caption_row(
                    row, timeline["cuts"]
                ),
            }
            for row in caption_rows
        ]
        presentation_items = _presentation_items(raw_subtitle_items, layout=layout)
        selector = select_subtitle_preset(
            {
                "speaker_id": "unknown",
                "speaker_role": "unknown",
                "emotion": "neutral",
                "intensity": 0,
                "utterance_role": "dialogue",
                "readability_priority": "maximum",
            }
        )
        subtitle_readback = build_subtitle_presentation_readback(
            layout=layout,
            presentation_items=presentation_items,
            selector=selector,
            caption_readback=caption_readback,
            font_sha256=font_sha256,
        )
        _write_json(stage / "subtitle_presentation_readback.json", subtitle_readback)
        if subtitle_readback["status"] != "passed":
            raise EditorialVideoCandidateError(
                "subtitle presentation validation failed: "
                f"{len(subtitle_readback['violations'])} violation(s)",
                stage=current_stage,
            )
        ass_path = stage / "editorial_subtitles.ass"
        _write_ass(ass_path, presentation_items, layout=layout, review_label=None)

        current_stage = "render"
        final_video = stage / "final_video.mp4"
        render = render_editorial_timeline(
            source_path=resolved["source_path"],
            video_path=final_video,
            cuts=timeline["cuts"],
            ass_path=ass_path,
            font_file=font_file,
            ffmpeg_path=ffmpeg,
            runner=runner,
        )

        current_stage = "media_validation"
        validation = out12.validate_rendered_video(
            video_path=final_video,
            timeline=timeline,
            caption_readback=caption_readback,
            source_probe=source_probe,
            ffmpeg_path=ffmpeg,
            ffprobe_path=ffprobe,
            runner=runner,
        )
        validation["schema_version"] = SCHEMA_VERSION
        validation["state"] = READY_STATE if validation["status"] == "passed" else "OUT13_VALIDATION_FAILED"
        validation["render"] = render
        validation["input_fingerprint"] = fingerprint
        validation["caption_validation"].update(
            {
                "split_at_cut_boundary_count": caption_readback[
                    "split_at_cut_boundary_count"
                ],
                "duplicate_cue_count": caption_readback["duplicate_cue_count"],
                "mapping_coverage_ratio": caption_readback[
                    "mapping_coverage_ratio"
                ],
            }
        )
        validation["authority_binding"] = {
            "status": authority_binding["status"],
            "artifact_id": artifact_id,
            "source_sha256": authority_binding["source_sha256"],
            "transcript_sha256": authority_binding["transcript_sha256"],
            "caption_sha256": authority_binding["caption_sha256"],
            "rights_sha256": authority_binding["rights_sha256"],
            "resolved_font_file_sha256": font_sha256,
        }
        validation["visual_observation"] = {
            "status": "unverified",
            "observation_class": "none",
            "double_display_status": "unverified",
        }
        validation["editorial_checks"] = {
            "explicit_plan": timeline["selection_mode"]
            == "explicit_caption_evidence_editorial_plan",
            "selected_cut_count": timeline["cut_count"] >= MIN_SELECTED_CUTS,
            "intentional_omitted_spans": timeline["intentional_omitted_span_count"]
            >= MIN_INTENTIONAL_OMITTED_SPANS,
            "source_shortening": timeline["source_utilization_ratio"]
            <= MAX_SOURCE_UTILIZATION_RATIO,
            "caption_evidence_bound": all(
                bool(cut.get("transcript_segment_ids")) for cut in timeline["cuts"]
            ),
            "caption_boundary_integrity": caption_readback["split_at_cut_boundary_count"]
            == 0,
            "caption_mapping_complete": caption_readback["mapping_coverage_ratio"] == 1.0,
            "duplicate_cues": caption_readback["duplicate_cue_count"] == 0,
            "authority_binding": authority_binding["status"] == "passed",
            "subtitle_presentation": subtitle_readback["status"] == "passed",
        }
        if not all(validation["editorial_checks"].values()):
            validation["status"] = "failed"
        _write_json(stage / "validation_readback.json", validation)
        if validation["status"] != "passed":
            raise EditorialVideoCandidateError(
                "rendered editorial media validation failed",
                stage=current_stage,
            )

        current_stage = "review_package"
        review = build_review_package(
            artifact_id=artifact_id,
            plan_sha256=_sha256(plan_path),
            stage=stage,
            timeline=timeline,
            resolved=resolved,
            validation=validation,
            subtitle_readback=subtitle_readback,
            source_probe=source_probe,
            review_port=int(review_port),
            ffmpeg_path=ffmpeg,
            runner=runner,
        )
        pipeline_state = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": artifact_id,
            "state": READY_STATE,
            "ready": True,
            "input_fingerprint": fingerprint,
            "source_identity": resolved["source_identity"],
            "source_sha256": resolved["source_sha256"],
            "final_video_sha256": validation["media"]["sha256"],
            "source_duration_seconds": source_probe["duration_seconds"],
            "output_duration_seconds": validation["media"]["duration_seconds"],
            "source_utilization_ratio": timeline["source_utilization_ratio"],
            "cut_count": timeline["cut_count"],
            "omitted_span_count": len(timeline["omitted_ranges"]),
            "review_entrypoint": "review/index.html",
            "closed_gates": _closed_gates(),
        }
        _write_json(stage / "pipeline_state.json", pipeline_state)

        current_stage = "manifest"
        manifest = build_run_manifest(
            artifact_id=artifact_id,
            stage=stage,
            input_fingerprint=fingerprint,
            resolved=resolved,
            source_probe=source_probe,
            timeline=timeline,
            subtitle_readback=subtitle_readback,
            validation=validation,
            review=review,
            plan_sha256=_sha256(plan_path),
            transcript_sha256=_sha256(transcript),
        )
        _write_json(stage / "run_manifest.json", manifest)
        validate_run_manifest(stage, manifest, expected_artifact_id=artifact_id)
        out12.promote_output(stage=stage, output=output, force=force)
        stage = None
        return {
            "artifact_id": artifact_id,
            "state": READY_STATE,
            "output_dir": output,
            "final_video": output / "final_video.mp4",
            "editorial_plan": output / "editorial_plan.json",
            "timeline_ir": output / "timeline_ir.json",
            "caption_readback": output / "caption_readback.json",
            "subtitle_presentation_readback": output
            / "subtitle_presentation_readback.json",
            "validation_readback": output / "validation_readback.json",
            "run_manifest": output / "run_manifest.json",
            "review_index": output / "review" / "index.html",
            "review_url": f"http://127.0.0.1:{review_port}/review/index.html",
            "open_command": str(output / "review" / "open_preview.ps1"),
            "source_identity": resolved["source_identity"],
            "source_sha256": resolved["source_sha256"],
            "source_duration_seconds": source_probe["duration_seconds"],
            "duration_seconds": validation["media"]["duration_seconds"],
            "cut_count": timeline["cut_count"],
            "omitted_span_count": len(timeline["omitted_ranges"]),
            "video_sha256": validation["media"]["sha256"],
            "manifest_sha256": manifest["manifest_self_integrity"]["sha256"],
            "resolved_font_family": style.get("resolved_font_family"),
            "resolved_font_file": style.get("resolved_font_file"),
            "resume": False,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:
        failure_evidence_dir: Path | None = None
        if stage is not None and stage.exists():
            failure_evidence_dir = output.parent / f".{output.name}.failed-{uuid.uuid4().hex}"
            stage.replace(failure_evidence_dir)
        error = (
            exc
            if isinstance(exc, EditorialVideoCandidateError)
            else EditorialVideoCandidateError(str(exc), stage=current_stage)
        )
        write_failure_state(
            artifact_id=artifact_id,
            output_dir=output,
            stage=error.stage,
            message=str(error),
            input_fingerprint=fingerprint,
            failure_evidence_dir=failure_evidence_dir,
        )
        raise error


def build_editorial_timeline(
    *,
    plan: dict[str, Any],
    source_identity: str,
    source_sha256: str,
    source_duration_seconds: float,
    transcript: dict[str, Any],
    caption_events: list[dict[str, Any]],
) -> dict[str, Any]:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise EditorialVideoCandidateError(
            "editorial plan schema mismatch", stage="timeline_selection"
        )
    source = plan.get("source") or {}
    if source.get("identity") != source_identity or source.get("sha256") != source_sha256:
        raise EditorialVideoCandidateError(
            "editorial plan source identity or SHA does not match input",
            stage="timeline_selection",
        )
    planned_duration = float(source.get("duration_seconds") or 0.0)
    if abs(planned_duration - source_duration_seconds) > 0.1:
        raise EditorialVideoCandidateError(
            "editorial plan source duration does not match input",
            stage="timeline_selection",
        )
    transcript_rows = {
        str(row.get("id")): row
        for row in transcript.get("segments") or []
        if isinstance(row, dict) and row.get("id")
    }
    cuts_in = plan.get("cuts") or []
    if not isinstance(cuts_in, list) or len(cuts_in) < MIN_SELECTED_CUTS:
        raise EditorialVideoCandidateError(
            "editorial plan requires at least three selected cuts",
            stage="timeline_selection",
        )
    cuts: list[dict[str, Any]] = []
    output_cursor = 0.0
    previous_source_end = 0.0
    for order, row in enumerate(cuts_in, start=1):
        if not isinstance(row, dict) or int(row.get("output_order") or 0) != order:
            raise EditorialVideoCandidateError(
                "editorial plan output_order must be contiguous",
                stage="timeline_selection",
            )
        start = float(row.get("source_in_seconds") or 0.0)
        end = float(row.get("source_out_seconds") or 0.0)
        if start < previous_source_end - 0.001 or end <= start or end > source_duration_seconds + 0.05:
            raise EditorialVideoCandidateError(
                f"invalid chronological range for cut {order}",
                stage="timeline_selection",
            )
        segment_ids = [
            str(value) for value in row.get("direct_evidence_segment_ids") or []
        ]
        if not segment_ids or any(value not in transcript_rows for value in segment_ids):
            raise EditorialVideoCandidateError(
                f"cut {order} has missing direct transcript evidence",
                stage="timeline_selection",
            )
        eligible_segment_ids = [
            segment_id
            for segment_id, segment in transcript_rows.items()
            if float(segment.get("start_seconds") or 0.0) >= start - 0.001
            and float(segment.get("end_seconds") or 0.0) <= end + 0.001
            and float(segment.get("end_seconds") or 0.0)
            > float(segment.get("start_seconds") or 0.0)
        ]
        if segment_ids != eligible_segment_ids:
            raise EditorialVideoCandidateError(
                f"cut {order} direct transcript evidence must exactly match the selected range",
                stage="timeline_selection",
            )
        split_segment_ids = [
            segment_id
            for segment_id, segment in transcript_rows.items()
            if _ranges_overlap(
                start,
                end,
                float(segment.get("start_seconds") or 0.0),
                float(segment.get("end_seconds") or 0.0),
            )
            and segment_id not in eligible_segment_ids
        ]
        if split_segment_ids:
            raise EditorialVideoCandidateError(
                f"cut {order} splits transcript utterance(s): {', '.join(split_segment_ids)}",
                stage="timeline_selection",
            )
        context = row.get("context_evidence") or {}
        context_segment_ids = [
            str(value) for value in context.get("segment_ids") or []
        ]
        if (
            not str(row.get("section") or "").strip()
            or not str(row.get("selection_reason") or "").strip()
            or not str(row.get("editorial_role") or "").strip()
            or not str(context.get("continuity_note") or "").strip()
            or any(value not in transcript_rows for value in context_segment_ids)
        ):
            raise EditorialVideoCandidateError(
                f"cut {order} is missing semantic/context evidence",
                stage="timeline_selection",
            )
        transition = str(row.get("transition") or "")
        if transition not in SUPPORTED_TRANSITIONS or (
            order == 1 and transition != "sequence_start"
        ) or (order > 1 and transition != "hard_cut"):
            raise EditorialVideoCandidateError(
                f"unsupported transition for cut {order}: {transition or '<missing>'}",
                stage="timeline_selection",
            )
        eligible_caption_ids = _eligible_caption_event_ids(
            caption_events, start=start, end=end
        )
        split_caption_ids = _split_caption_event_ids(
            caption_events, start=start, end=end
        )
        if split_caption_ids:
            raise EditorialVideoCandidateError(
                f"cut {order} splits caption cue(s): {', '.join(split_caption_ids)}",
                stage="timeline_selection",
            )
        if not eligible_caption_ids:
            raise EditorialVideoCandidateError(
                f"cut {order} has no eligible caption mapping",
                stage="timeline_selection",
            )
        duration = end - start
        output_end = output_cursor + duration
        cuts.append(
            {
                "cut_id": str(row.get("cut_id") or f"cut_{order:03d}"),
                "cut_order": order,
                "section": str(row["section"]),
                "editorial_role": str(row["editorial_role"]),
                "source_identity": source_identity,
                "source_in_seconds": round(start, 6),
                "source_out_seconds": round(end, 6),
                "output_in_seconds": round(output_cursor, 6),
                "output_out_seconds": round(output_end, 6),
                "duration_seconds": round(duration, 6),
                "selection_reason": str(row["selection_reason"]),
                "continuity_context": str(context["continuity_note"]),
                "context_evidence": context,
                "transcript_segment_ids": segment_ids,
                "direct_evidence_segment_ids": segment_ids,
                "context_segment_ids": context_segment_ids,
                "eligible_caption_event_ids": eligible_caption_ids,
                "transition": transition,
                "caption_ids": [],
            }
        )
        output_cursor = output_end
        previous_source_end = end
    if not MIN_OUTPUT_SECONDS <= output_cursor <= MAX_OUTPUT_SECONDS:
        raise EditorialVideoCandidateError(
            "editorial output duration must be between 60 and 180 seconds",
            stage="timeline_selection",
        )
    utilization = output_cursor / source_duration_seconds
    if utilization > MAX_SOURCE_UTILIZATION_RATIO:
        raise EditorialVideoCandidateError(
            "editorial output is not clearly shorter than the source",
            stage="timeline_selection",
        )
    omitted = _validate_omitted_ranges(
        plan.get("omitted_ranges") or [],
        cuts=cuts,
        source_duration_seconds=source_duration_seconds,
        transcript_rows=transcript_rows,
    )
    intentional = [row for row in omitted if row.get("intentional_editorial_omission")]
    if len(intentional) < MIN_INTENTIONAL_OMITTED_SPANS:
        raise EditorialVideoCandidateError(
            "editorial plan requires at least two intentional omitted spans",
            stage="timeline_selection",
        )
    if len({cut["section"] for cut in cuts}) < 3:
        raise EditorialVideoCandidateError(
            "editorial plan requires at least three evidence-bound sections",
            stage="timeline_selection",
        )
    if not caption_events:
        raise EditorialVideoCandidateError(
            "editorial plan requires caption events", stage="timeline_selection"
        )
    timeline = {
        "schema_version": TIMELINE_SCHEMA_VERSION,
        "out13_schema_version": SCHEMA_VERSION,
        "source_identity": source_identity,
        "source_sha256": source_sha256,
        "source_duration_seconds": round(source_duration_seconds, 6),
        "output_duration_seconds": round(output_cursor, 6),
        "source_utilization_ratio": round(utilization, 6),
        "selection_mode": "explicit_caption_evidence_editorial_plan",
        "chronology_preserved": True,
        "causal_order_preserved": True,
        "uniform_sampling_used": False,
        "arbitrary_thirds_used": False,
        "semantic_section_count": len({cut["section"] for cut in cuts}),
        "cut_count": len(cuts),
        "intentional_omitted_span_count": len(intentional),
        "omitted_ranges": omitted,
        "cuts": cuts,
    }
    out12.validate_timeline_ir(timeline)
    return timeline


def _validate_omitted_ranges(
    rows: list[dict[str, Any]],
    *,
    cuts: list[dict[str, Any]],
    source_duration_seconds: float,
    transcript_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise EditorialVideoCandidateError(
            "omitted_ranges must be a list", stage="timeline_selection"
        )
    normalized: list[dict[str, Any]] = []
    expected_complement = _source_complement(
        cuts=cuts, source_duration_seconds=source_duration_seconds
    )
    if len(rows) != len(expected_complement):
        raise EditorialVideoCandidateError(
            "omitted ranges must exactly describe the source complement",
            stage="timeline_selection",
        )
    previous_end = -1.0
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise EditorialVideoCandidateError(
                f"invalid omitted range {index}", stage="timeline_selection"
            )
        start = float(row.get("source_in_seconds") or 0.0)
        end = float(row.get("source_out_seconds") or 0.0)
        expected_start, expected_end = expected_complement[index - 1]
        if (
            end <= start
            or start < previous_end - 0.001
            or start < 0
            or end > source_duration_seconds + 0.05
            or abs(start - expected_start) > 0.002
            or abs(end - expected_end) > 0.002
        ):
            raise EditorialVideoCandidateError(
                f"omitted range {index} is unsorted or differs from the source complement",
                stage="timeline_selection",
            )
        if any(
            min(end, float(cut["source_out_seconds"]))
            - max(start, float(cut["source_in_seconds"]))
            > 0.02
            for cut in cuts
        ):
            raise EditorialVideoCandidateError(
                f"omitted range {index} overlaps a selected cut",
                stage="timeline_selection",
            )
        segment_ids = [str(value) for value in row.get("transcript_segment_ids") or []]
        if any(value not in transcript_rows for value in segment_ids):
            raise EditorialVideoCandidateError(
                f"omitted range {index} references a missing transcript segment",
                stage="timeline_selection",
            )
        eligible_segment_ids = [
            segment_id
            for segment_id, segment in transcript_rows.items()
            if float(segment.get("start_seconds") or 0.0) >= start - 0.001
            and float(segment.get("end_seconds") or 0.0) <= end + 0.001
            and float(segment.get("end_seconds") or 0.0)
            > float(segment.get("start_seconds") or 0.0)
        ]
        if segment_ids != eligible_segment_ids:
            raise EditorialVideoCandidateError(
                f"omitted range {index} transcript ledger mismatch",
                stage="timeline_selection",
            )
        if not str(row.get("omission_reason") or "").strip():
            raise EditorialVideoCandidateError(
                f"omitted range {index} has no reason", stage="timeline_selection"
            )
        normalized.append(
            {
                **row,
                "omitted_id": str(row.get("omitted_id") or f"omit_{index:03d}"),
                "source_in_seconds": round(start, 6),
                "source_out_seconds": round(end, 6),
                "duration_seconds": round(end - start, 6),
                "transcript_segment_ids": segment_ids,
                "intentional_editorial_omission": bool(
                    row.get("intentional_editorial_omission")
                ),
            }
        )
        previous_end = end
    return normalized


def build_subtitle_presentation_readback(
    *,
    layout: dict[str, Any],
    presentation_items: list[dict[str, Any]],
    selector: dict[str, Any],
    caption_readback: dict[str, Any],
    font_sha256: str | None,
) -> dict[str, Any]:
    values = layout["values"]
    style = layout["diagnostic_ass_style"]
    safe_width = int(layout["frame"]["width"]) - int(values["margin_l"]) - int(values["margin_r"])
    rows = []
    violations = []
    for item in presentation_items:
        bbox = item.get("font_bbox_wrap_readback") or {}
        selected = bbox.get("selected_measurement") or {}
        measured_widths = [
            float(value)
            for value in bbox.get("measured_width_by_line") or []
            if isinstance(value, (int, float))
        ]
        measured_width = float(
            selected.get("width")
            or (bbox.get("wrap_algorithm") or {}).get("selected_max_line_width")
            or max(measured_widths, default=0.0)
            or 0.0
        )
        line_count = int(item.get("wrapped_line_count") or 1)
        duration = float(item["display_end_seconds"]) - float(item["display_start_seconds"])
        row = {
            "subtitle_id": item["subtitle_id"],
            "display_start_seconds": item["display_start_seconds"],
            "display_end_seconds": item["display_end_seconds"],
            "duration_seconds": round(duration, 6),
            "wrapped_lines": item.get("wrapped_lines") or [],
            "wrapped_line_count": line_count,
            "measured_width_pixels": round(measured_width, 3),
            "safe_width_pixels": safe_width,
            "orphan_prevention_applied": bool(item.get("orphan_prevention_applied")),
            "suspicious_tail_line_present": bool(
                item.get("suspicious_tail_line_present")
            ),
        }
        if line_count > 2:
            violations.append(f"{item['subtitle_id']}:more_than_two_lines")
        if measured_width > safe_width + 1:
            violations.append(f"{item['subtitle_id']}:safe_width_overflow")
        if duration <= 0:
            violations.append(f"{item['subtitle_id']}:nonpositive_duration")
        if row["suspicious_tail_line_present"]:
            violations.append(f"{item['subtitle_id']}:suspicious_tail_line")
        rows.append(row)
    status = (
        "passed"
        if presentation_items
        and not violations
        and caption_readback.get("status") == "passed"
        else "failed"
    )
    return {
        "schema_version": SUBTITLE_READBACK_SCHEMA_VERSION,
        "status": status,
        "renderer": "ffmpeg_ass_libass",
        "typography_decoration_candidate_id": style.get(
            "typography_decoration_candidate_id"
        ),
        "requested_font_family": style.get("requested_font_family"),
        "resolved_font_family": style.get("resolved_font_family"),
        "resolved_font_file": style.get("resolved_font_file"),
        "resolved_font_file_sha256": font_sha256,
        "font_file_status": style.get("font_file_status"),
        "typography": {
            "font_size_pixels": values["font_size"],
            "line_height_pixels": values["line_height"],
            "presentation_mode": layout["mode"],
            "size_policy": "editorial_readability_two_line_maximum",
        },
        "body_text": {
            "fill": style.get("text_fill"),
            "stable_policy_token": selector["style_tokens"]["body_text_color_token"],
        },
        "badge_accent": {
            "speaker_identity_verified": False,
            "badge_rendered": False,
            "badge_omission_reason": "speaker identity is not inferred from caption text",
            "resolved_badge_fill": style.get("badge_fill"),
            "resolved_badge_outline": style.get("badge_outline"),
            "selector_badge_token": selector["style_tokens"]["badge_color_token"],
            "selector_accent_token": selector["style_tokens"]["accent_color_token"],
        },
        "outline_shadow": {
            "outline_pixels": values["outline"],
            "shadow_pixels": values["shadow"],
            "outline_colour": style.get("stroke_fill"),
            "shadow_colour": style.get("shadow_fill"),
            "selector_strength_token": selector["style_tokens"][
                "outline_shadow_strength"
            ],
        },
        "safe_area": {
            "frame_width": layout["frame"]["width"],
            "frame_height": layout["frame"]["height"],
            "margin_left": values["margin_l"],
            "margin_right": values["margin_r"],
            "bottom_margin": values["bottom_margin"],
            "safe_width_pixels": safe_width,
            "overflow_count": sum("overflow" in value for value in violations),
        },
        "line_break": {
            "algorithm": "existing_pillow_font_bbox_japanese_wrap",
            "authority_whitespace_policy": (
                "provider sidecar line breaks are normalized to spaces before "
                "measured wrapping; wording and timing remain unchanged"
            ),
            "selector_token": selector["style_tokens"][
                "safe_area_line_break_behavior"
            ],
            "maximum_lines": max(
                (int(row["wrapped_line_count"]) for row in rows), default=0
            ),
            "multi_line_cue_count": sum(
                int(row["wrapped_line_count"]) > 1 for row in rows
            ),
        },
        "cue_count": len(rows),
        "overlap_count": caption_readback.get("overlap_count"),
        "negative_duration_count": caption_readback.get("negative_duration_count"),
        "orphan_cue_count": caption_readback.get("orphan_cue_count"),
        "violations": violations,
        "items": rows,
        "closed_gates": _closed_gates(),
    }


def _caption_text_for_presentation(value: str) -> str:
    """Normalize provider layout whitespace without changing caption wording."""

    return " ".join(str(value).split())


def _editorial_subtitle_layout_contract(
    *,
    frame_width: int,
    frame_height: int,
    dimension_source: str,
    diagnostic_ass_style: dict[str, Any],
) -> dict[str, Any]:
    """Derive the OUT-13 two-line editorial layout from the proven ASS contract."""

    layout = _subtitle_layout_contract(
        frame_width=frame_width,
        frame_height=frame_height,
        mode="bottom_center_emphasis",
        dimension_source=dimension_source,
        diagnostic_ass_style=diagnostic_ass_style,
    )
    ratios = layout["ratios"]
    values = layout["values"]
    font_size = max(24, int(round(frame_height * EDITORIAL_FONT_SIZE_TO_FRAME_HEIGHT)))
    values.update(
        {
            "font_size": font_size,
            "line_height": int(round(font_size * float(ratios["line_height_to_font_size"]))),
            "badge_width": int(round(font_size * float(ratios["badge_width_to_font_size"]))),
            "badge_height": int(round(font_size * float(ratios["badge_height_to_font_size"]))),
            "badge_font_size": int(
                round(font_size * float(ratios["badge_font_size_to_font_size"]))
            ),
            "badge_text_gap": int(
                round(font_size * float(ratios["badge_text_gap_to_font_size"]))
            ),
        }
    )
    layout["formulas"]["font_size"] = (
        f"round(frame_height * {EDITORIAL_FONT_SIZE_TO_FRAME_HEIGHT})"
    )
    layout["ratios"]["editorial_font_size_to_frame_height"] = (
        EDITORIAL_FONT_SIZE_TO_FRAME_HEIGHT
    )
    layout["selected_mode_reason"] = (
        "unknown speaker identity requires badge omission; bottom-center dialogue uses "
        "a measured two-line maximum across the complete official caption track"
    )
    return layout


def render_editorial_timeline(
    *,
    source_path: Path,
    video_path: Path,
    cuts: list[dict[str, Any]],
    ass_path: Path,
    font_file: Path,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    work = video_path.parent / ".render_work"
    work.mkdir()
    filter_path = work / "filter_complex.txt"
    filter_text = render_editorial_filter_complex(
        cuts=cuts, ass_path=ass_path, font_file=font_file
    )
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
            "-ar",
            "48000",
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
            timeout=out12.COMMAND_TIMEOUT_SECONDS,
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
                "subtitle_renderer": "ffmpeg_ass_libass",
                "attempts": attempts,
                "execution_count": 1,
                "corrective_pass_count": 0,
            }
        if video_path.exists():
            video_path.unlink()
    shutil.rmtree(work)
    raise EditorialVideoCandidateError(
        "FFmpeg editorial render failed for all H.264 profiles", stage="render"
    )


def render_editorial_filter_complex(
    *, cuts: list[dict[str, Any]], ass_path: Path, font_file: Path
) -> str:
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
    ass_filter = f"ass=filename='{_escape_filter_path(ass_path)}'"
    if font_file.is_file():
        ass_filter += f":fontsdir='{_escape_filter_path(font_file.parent)}'"
    filters.append(f"[vcat]{ass_filter},format=yuv420p[vout]")
    filters.append("[acat]loudnorm=I=-15:TP=-2.0:LRA=11[aout]")
    return ";\n".join(filters) + "\n"


def build_review_package(
    *,
    artifact_id: str,
    plan_sha256: str,
    stage: Path,
    timeline: dict[str, Any],
    resolved: dict[str, Any],
    validation: dict[str, Any],
    subtitle_readback: dict[str, Any],
    source_probe: dict[str, Any],
    review_port: int,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    review = out12.build_review_package(
        stage=stage,
        timeline=timeline,
        resolved=resolved,
        validation=validation,
        review_port=review_port,
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    evidence_dir = stage / "review" / "evidence"
    source_times = [
        (float(cut["source_in_seconds"]) + float(cut["source_out_seconds"])) / 2.0
        for cut in timeline["cuts"]
    ]
    out12.render_contact_sheet(
        video_path=resolved["source_path"],
        output_path=evidence_dir / "source_selected_ranges_contact_sheet.jpg",
        sample_times=source_times,
        fps=out12._frame_rate_float(source_probe.get("frame_rate")),
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    sample_specs = select_subtitle_evidence_samples(subtitle_readback)
    output_times = [float(row["frame_seconds"]) for row in sample_specs]
    out12.render_contact_sheet(
        video_path=stage / "final_video.mp4",
        output_path=evidence_dir / "subtitle_presentation_contact_sheet.jpg",
        sample_times=output_times,
        fps=out12._frame_rate_float(validation["media"].get("frame_rate")),
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    frame_rows = []
    for spec in sample_specs:
        frame = evidence_dir / f"subtitle_{spec['role']}.png"
        result = _run(
            [
                ffmpeg_path,
                "-y",
                "-ss",
                _seconds(float(spec["frame_seconds"])),
                "-i",
                str(stage / "final_video.mp4"),
                "-frames:v",
                "1",
                str(frame),
            ],
            runner=runner,
            stage="review_package",
            allow_failure=True,
        )
        if result.returncode != 0 or not frame.is_file():
            raise EditorialVideoCandidateError(
                f"subtitle evidence frame failed: {spec['role']}",
                stage="review_package",
            )
        frame_rows.append(
            {
                **spec,
                "path": f"review/evidence/{frame.name}",
                "sha256": _sha256(frame),
            }
        )
    review_readback = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "source_identity": resolved["source_identity"],
        "source_sha256": resolved["source_sha256"],
        "editorial_plan_sha256": plan_sha256,
        "authority_binding": _read_json(
            stage / "authority_binding.json", "authority binding"
        ),
        "final_video_sha256": validation["media"]["sha256"],
        "final_video_byte_size": validation["media"]["byte_size"],
        "source_duration_seconds": source_probe["duration_seconds"],
        "output_duration_seconds": validation["media"]["duration_seconds"],
        "source_utilization_ratio": timeline["source_utilization_ratio"],
        "selected_cut_count": timeline["cut_count"],
        "omitted_ranges": timeline["omitted_ranges"],
        "subtitle_evidence_frames": frame_rows,
        "initial_media_state": "paused_muted_time_zero",
        "visual_observation": {
            "status": "unverified",
            "observation_class": "none",
            "double_display_status": "unverified",
            "note": "Machine checks do not substitute for Worker or human visual observation.",
        },
        "closed_gates": _closed_gates(),
    }
    _write_json(stage / "review" / "review_readback.json", review_readback)
    _write_text(
        stage / "review" / "index.html",
        render_review_html(
            timeline=timeline,
            resolved=resolved,
            validation=validation,
            subtitle_readback=subtitle_readback,
            review_readback=review_readback,
        ),
    )
    return {
        **review,
        "source_selected_ranges_contact_sheet": "review/evidence/source_selected_ranges_contact_sheet.jpg",
        "subtitle_presentation_contact_sheet": "review/evidence/subtitle_presentation_contact_sheet.jpg",
        "review_readback": "review/review_readback.json",
        "subtitle_evidence_frames": frame_rows,
    }


def select_subtitle_evidence_samples(
    subtitle_readback: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = list(subtitle_readback.get("items") or [])
    if not rows:
        raise EditorialVideoCandidateError(
            "subtitle evidence requires cues", stage="review_package"
        )
    normal = max(
        rows,
        key=lambda row: (
            int(row.get("wrapped_line_count") or 1) == 1,
            float(row.get("duration_seconds") or 0.0),
        ),
    )
    multiline = max(
        rows,
        key=lambda row: (
            int(row.get("wrapped_line_count") or 1),
            len("".join(row.get("wrapped_lines") or [])),
        ),
    )
    short = min(
        (row for row in rows if float(row.get("duration_seconds") or 0.0) >= 0.2),
        key=lambda row: float(row.get("duration_seconds") or 0.0),
        default=rows[0],
    )
    selected = [("normal_dialogue", normal), ("multiline_or_long", multiline), ("short_cue", short)]
    return [
        {
            "role": role,
            "subtitle_id": row["subtitle_id"],
            "frame_seconds": round(
                (
                    float(row["display_start_seconds"])
                    + float(row["display_end_seconds"])
                )
                / 2.0,
                6,
            ),
            "wrapped_line_count": row["wrapped_line_count"],
            "duration_seconds": row["duration_seconds"],
        }
        for role, row in selected
    ]


def render_review_html(
    *,
    timeline: dict[str, Any],
    resolved: dict[str, Any],
    validation: dict[str, Any],
    subtitle_readback: dict[str, Any],
    review_readback: dict[str, Any],
) -> str:
    cut_rows = "".join(
        "<tr>"
        f"<td>{escape(str(cut['cut_id']))}</td>"
        f"<td>{escape(str(cut['section']))}<br><small>{escape(str(cut['editorial_role']))}</small></td>"
        f"<td>{float(cut['source_in_seconds']):.3f}–{float(cut['source_out_seconds']):.3f}</td>"
        f"<td>{float(cut['output_in_seconds']):.3f}–{float(cut['output_out_seconds']):.3f}</td>"
        f"<td>{escape(str(cut['selection_reason']))}</td>"
        f"<td>{escape(', '.join(cut['transcript_segment_ids']))}</td>"
        f"<td><button type=\"button\" data-seek=\"{max(0.0, float(cut['output_in_seconds']) - 0.25):.3f}\">before</button> "
        f"<button type=\"button\" data-seek=\"{min(float(timeline['output_duration_seconds']), float(cut['output_in_seconds']) + 0.25):.3f}\">after</button></td>"
        "</tr>"
        for cut in timeline["cuts"]
    )
    omitted_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['omitted_id']))}</td>"
        f"<td>{float(row['source_in_seconds']):.3f}–{float(row['source_out_seconds']):.3f}</td>"
        f"<td>{float(row['duration_seconds']):.3f}s</td>"
        f"<td>{escape(str(row['omission_reason']))}</td>"
        "</tr>"
        for row in timeline["omitted_ranges"]
    )
    checks = "".join(
        f"<li>{escape(name)}: {'pass' if value else 'fail'}</li>"
        for name, value in {
            **validation["checks"],
            **validation["editorial_checks"],
        }.items()
    )
    style = (
        f"{subtitle_readback['resolved_font_family']} / "
        f"{subtitle_readback['outline_shadow']['outline_pixels']}px outline / "
        f"{subtitle_readback['outline_shadow']['shadow_pixels']}px shadow / "
        f"max {subtitle_readback['line_break']['maximum_lines']} lines"
    )
    authority = review_readback["authority_binding"]
    caption_authority = authority["caption"]
    observation = review_readback["visual_observation"]
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,">
<title>OUT-13 editorial representative video review</title>
<style>*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:#080d18;color:#e7eef9;font-family:system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:24px}}.summary{{background:#111a2d;border:1px solid #293957;border-radius:12px;padding:16px}}video{{display:block;width:100%;max-height:72vh;background:#000;border-radius:10px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:16px 0}}.metric{{background:#15223a;padding:12px;border-radius:10px}}.table-wrap{{width:100%;overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{padding:9px;border-bottom:1px solid #334155;text-align:left;vertical-align:top}}small{{color:#9fb0c8}}code{{overflow-wrap:anywhere}}img{{width:100%;height:auto;margin-top:12px;border-radius:10px}}button{{padding:7px 12px}}details{{margin-top:18px}}.gate{{color:#f6c177}}@media(max-width:520px){{main{{padding:12px}}h1{{font-size:1.35rem}}}}</style></head>
<body><main><section class="summary"><p>OUT-13 · EDITORIAL REPRESENTATIVE VIDEO</p><h1>編集構成・字幕presentation・画面/音声品質を同一MP4で判断</h1>
<video id="finalVideo" controls muted preload="metadata" playsinline src="../final_video.mp4"></video>
<div class="metrics"><div class="metric">source<br><strong>{float(review_readback['source_duration_seconds']):.3f}s</strong></div><div class="metric">output<br><strong>{float(review_readback['output_duration_seconds']):.3f}s</strong></div><div class="metric">utilization<br><strong>{float(review_readback['source_utilization_ratio'])*100:.1f}%</strong></div><div class="metric">cuts / omissions<br><strong>{timeline['cut_count']} / {len(timeline['omitted_ranges'])}</strong></div></div>
<p>candidate <code>{escape(review_readback['artifact_id'])}</code><br>source <code>{escape(resolved['source_identity'])}</code> · source SHA <code>{escape(resolved['source_sha256'])}</code><br>plan SHA <code>{escape(review_readback['editorial_plan_sha256'])}</code><br>output SHA <code>{escape(validation['media']['sha256'])}</code> · {int(validation['media']['byte_size'])} bytes</p>
<p>caption authority: {escape(caption_authority['classification'])} / {escape(caption_authority['provider'])}; rights: {escape(authority['rights']['status'])} snapshot; visual observation: {escape(observation['status'])}; style: {escape(style)}</p></section>
<h2>Selected editorial timeline</h2><div class="table-wrap"><table><thead><tr><th>cut</th><th>section / role</th><th>source</th><th>output</th><th>reason</th><th>evidence</th><th></th></tr></thead><tbody>{cut_rows}</tbody></table></div>
<h2>Omitted source ranges</h2><div class="table-wrap"><table><thead><tr><th>id</th><th>source</th><th>duration</th><th>reason</th></tr></thead><tbody>{omitted_rows}</tbody></table></div>
<details><summary>字幕・映像証拠</summary><p>上: source selected ranges。下: burn-in後の通常発話、長文/複数行、短時間cue。視覚判断は machine validation と分離され、現時点では unverified。</p><img src="evidence/source_selected_ranges_contact_sheet.jpg" alt="source selected ranges"><img src="evidence/subtitle_presentation_contact_sheet.jpg" alt="subtitle presentation evidence"><img src="evidence/cut_boundary_contact_sheet.jpg" alt="cut boundary evidence"><img src="evidence/waveform.png" alt="waveform"></details>
<details><summary>Machine validation</summary><ul>{checks}</ul></details>
<p class="gate">Internal editorial review only. Production, rights, thumbnail, publishing, public readiness, and upload remain closed.</p>
</main><script>const v=document.getElementById('finalVideo');v.autoplay=false;v.muted=true;v.volume=0.25;v.currentTime=0;document.querySelectorAll('[data-seek]').forEach(b=>b.addEventListener('click',()=>{{v.pause();v.currentTime=Number(b.dataset.seek);}}));</script></body></html>
"""


def build_run_manifest(
    *,
    artifact_id: str,
    stage: Path,
    input_fingerprint: str,
    resolved: dict[str, Any],
    source_probe: dict[str, Any],
    timeline: dict[str, Any],
    subtitle_readback: dict[str, Any],
    validation: dict[str, Any],
    review: dict[str, Any],
    plan_sha256: str,
    transcript_sha256: str,
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
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "state": READY_STATE,
        "input_fingerprint": input_fingerprint,
        "source": {
            "identity": resolved["source_identity"],
            "sha256": resolved["source_sha256"],
            "byte_size": resolved["source_byte_size"],
            "duration_seconds": source_probe["duration_seconds"],
            "resolution": source_probe["resolution"],
        },
        "authorities": {
            "editorial_plan_sha256": plan_sha256,
            "transcript_sha256": transcript_sha256,
            "caption_track_sha256": resolved["caption_sha256"],
            "rights_snapshot_sha256": resolved["rights_sha256"],
            "caption_mode": "provider_json3_sidecar",
            "authority_binding_status": "passed",
            "authority_binding_path": "authority_binding.json",
        },
        "editorial": {
            "selection_mode": timeline["selection_mode"],
            "cut_count": timeline["cut_count"],
            "section_count": timeline["semantic_section_count"],
            "omitted_ranges": timeline["omitted_ranges"],
            "source_utilization_ratio": timeline["source_utilization_ratio"],
            "mapping_coverage": validation["mapping_coverage"],
        },
        "subtitle_presentation": {
            "status": subtitle_readback["status"],
            "cue_count": subtitle_readback["cue_count"],
            "typography_decoration_candidate_id": subtitle_readback[
                "typography_decoration_candidate_id"
            ],
            "resolved_font_family": subtitle_readback["resolved_font_family"],
            "resolved_font_file_sha256": subtitle_readback[
                "resolved_font_file_sha256"
            ],
            "outline_shadow": subtitle_readback["outline_shadow"],
            "safe_area": subtitle_readback["safe_area"],
            "line_break": subtitle_readback["line_break"],
        },
        "final_video": {
            "path": "final_video.mp4",
            "sha256": validation["media"]["sha256"],
            "byte_size": validation["media"]["byte_size"],
            "duration_seconds": validation["media"]["duration_seconds"],
            "resolution": validation["media"]["resolution"],
        },
        "validation_status": validation["status"],
        "visual_observation": validation.get(
            "visual_observation",
            {
                "status": "unverified",
                "observation_class": "none",
                "double_display_status": "unverified",
            },
        ),
        "review": review,
        "files": files,
        "file_count": len(files),
        "closed_gates": _closed_gates(),
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    manifest["manifest_self_integrity"]["sha256"] = _manifest_self_hash(manifest)
    return manifest


def validate_run_manifest(
    stage: Path,
    manifest: dict[str, Any],
    *,
    expected_artifact_id: str,
) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise EditorialVideoCandidateError(
            "run manifest schema mismatch", stage="manifest"
        )
    _validate_artifact_id(expected_artifact_id)
    if (
        manifest.get("artifact_id") != expected_artifact_id
        or manifest.get("state") != READY_STATE
    ):
        raise EditorialVideoCandidateError(
            "run manifest identity mismatch", stage="manifest"
        )
    rows = manifest.get("files") or []
    if manifest.get("file_count") != len(rows):
        raise EditorialVideoCandidateError(
            "run manifest file count mismatch", stage="manifest"
        )
    for row in rows:
        path = stage / str(row.get("repo_relative_path") or "")
        if (
            not path.is_file()
            or path.stat().st_size != int(row.get("byte_size") or -1)
            or _sha256(path) != row.get("sha256")
        ):
            raise EditorialVideoCandidateError(
                f"run manifest payload mismatch: {row.get('repo_relative_path')}",
                stage="manifest",
            )
    if manifest.get("manifest_self_integrity", {}).get("sha256") != _manifest_self_hash(
        manifest
    ):
        raise EditorialVideoCandidateError(
            "run manifest self-integrity mismatch", stage="manifest"
        )


def resume_existing_output(
    *, output_dir: Path, input_fingerprint: str, artifact_id: str
) -> dict[str, Any]:
    manifest_path = output_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise EditorialVideoCandidateError(
            "resume requires a successful run_manifest.json",
            stage="source_resolution",
        )
    manifest = _read_json(manifest_path, "run manifest")
    if manifest.get("artifact_id") != artifact_id:
        raise EditorialVideoCandidateError(
            "resume artifact identity mismatch; refusing cross-candidate reuse",
            stage="source_resolution",
        )
    if manifest.get("input_fingerprint") != input_fingerprint:
        raise EditorialVideoCandidateError(
            "resume fingerprint mismatch; refusing stale output reuse",
            stage="source_resolution",
        )
    validate_run_manifest(
        output_dir, manifest, expected_artifact_id=artifact_id
    )
    final_video = output_dir / "final_video.mp4"
    if _sha256(final_video) != manifest["final_video"]["sha256"]:
        raise EditorialVideoCandidateError(
            "resume final video SHA mismatch", stage="source_resolution"
        )
    readback = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "state": READY_STATE,
        "input_fingerprint": input_fingerprint,
        "render_executed": False,
        "cache_hits": [
            "editorial_plan",
            "caption_presentation",
            "render",
            "media_validation",
            "review_package",
        ],
        "final_video_sha256": manifest["final_video"]["sha256"],
        "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
    }
    _write_json(output_dir / "resume_readback.json", readback)
    return {
        "artifact_id": artifact_id,
        "state": READY_STATE,
        "output_dir": output_dir,
        "final_video": final_video,
        "editorial_plan": output_dir / "editorial_plan.json",
        "timeline_ir": output_dir / "timeline_ir.json",
        "caption_readback": output_dir / "caption_readback.json",
        "subtitle_presentation_readback": output_dir
        / "subtitle_presentation_readback.json",
        "validation_readback": output_dir / "validation_readback.json",
        "run_manifest": manifest_path,
        "review_index": output_dir / "review" / "index.html",
        "review_url": manifest["review"]["clean_url"],
        "open_command": str(output_dir / "review" / "open_preview.ps1"),
        "source_identity": manifest["source"]["identity"],
        "source_sha256": manifest["source"]["sha256"],
        "source_duration_seconds": manifest["source"]["duration_seconds"],
        "duration_seconds": manifest["final_video"]["duration_seconds"],
        "cut_count": manifest["editorial"]["cut_count"],
        "omitted_span_count": len(manifest["editorial"]["omitted_ranges"]),
        "video_sha256": manifest["final_video"]["sha256"],
        "manifest_sha256": manifest["manifest_self_integrity"]["sha256"],
        "resolved_font_family": manifest["subtitle_presentation"][
            "resolved_font_family"
        ],
        "resolved_font_file": None,
        "resume": True,
    }


def write_failure_state(
    *,
    artifact_id: str,
    output_dir: Path,
    stage: str,
    message: str,
    input_fingerprint: str | None,
    failure_evidence_dir: Path | None,
) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "state": "OUT13_PIPELINE_FAILED",
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
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_json(output_dir / "pipeline_failure.json", payload)
    except OSError:
        pass


def _validate_artifact_id(artifact_id: str) -> None:
    if not ARTIFACT_ID_PATTERN.fullmatch(str(artifact_id or "")):
        raise EditorialVideoCandidateError(
            "artifact identity must match clip-out13-editorial-video-candidate-v1-NNN",
            stage="source_resolution",
        )


def _validate_output_allocation(
    *, output: Path, artifact_id: str, force: bool
) -> None:
    if not output.exists():
        return
    manifest_path = output / "run_manifest.json"
    if manifest_path.is_file():
        manifest = _read_json(manifest_path, "existing run manifest")
        existing_id = str(manifest.get("artifact_id") or "")
        if existing_id != artifact_id:
            raise EditorialVideoCandidateError(
                "output belongs to a different immutable candidate identity",
                stage="source_resolution",
            )
        if manifest.get("state") == READY_STATE:
            raise EditorialVideoCandidateError(
                "successful candidate output is immutable; allocate the next identity",
                stage="source_resolution",
            )
    if not force:
        raise EditorialVideoCandidateError(
            "output directory already exists; use --resume or allocate a new identity",
            stage="source_resolution",
        )


def _validate_authority_binding(
    *,
    root: Path,
    plan: dict[str, Any],
    artifact_id: str,
    resolved: dict[str, Any],
    transcript_path: Path,
    transcript: dict[str, Any],
    caption_track_path: Path,
    rights_manifest_path: Path,
) -> dict[str, Any]:
    if plan.get("artifact_id") != artifact_id:
        raise EditorialVideoCandidateError(
            "editorial plan artifact identity mismatch", stage="source_resolution"
        )
    binding = plan.get("authority_binding")
    if not isinstance(binding, dict):
        raise EditorialVideoCandidateError(
            "editorial plan requires authority_binding", stage="source_resolution"
        )
    actual = {
        "source_identity": resolved["source_identity"],
        "source_sha256": resolved["source_sha256"],
        "transcript_sha256": _sha256(transcript_path),
        "caption_sha256": _sha256(caption_track_path),
        "rights_sha256": _sha256(rights_manifest_path)
        if rights_manifest_path.is_file()
        else None,
    }
    if not rights_manifest_path.is_file() or resolved.get("rights_sha256") is None:
        raise EditorialVideoCandidateError(
            "rights manifest is required and must parse", stage="source_resolution"
        )
    for key, value in actual.items():
        if binding.get(key) != value:
            raise EditorialVideoCandidateError(
                f"authority binding mismatch: {key}", stage="source_resolution"
            )

    evidence = binding.get("evidence") or {}
    source_receipt_path, source_receipt = _read_bound_evidence(
        root, evidence.get("source_receipt"), "source receipt"
    )
    ledger_path, ledger = _read_bound_evidence(
        root, evidence.get("material_ledger"), "material ledger"
    )
    caption_evidence_path, caption_evidence = _read_bound_evidence(
        root, evidence.get("caption_provenance"), "caption provenance"
    )
    receipt_source_path = _resolved(
        root, Path(str(source_receipt.get("output_path") or ""))
    )
    if (
        source_receipt.get("sha256") != actual["source_sha256"]
        or receipt_source_path != Path(resolved["source_path"]).resolve()
    ):
        raise EditorialVideoCandidateError(
            "source receipt does not bind the selected source bytes",
            stage="source_resolution",
        )
    material_id = str(binding.get("source_material_id") or "")
    material = next(
        (
            row
            for row in ledger.get("materials") or []
            if isinstance(row, dict) and row.get("id") == material_id
        ),
        None,
    )
    if (
        material is None
        or material.get("kind") != "source_video"
        or material.get("hash_sha256") != actual["source_sha256"]
        or _resolved(root, Path(str(material.get("file_path") or "")))
        != Path(resolved["source_path"]).resolve()
    ):
        raise EditorialVideoCandidateError(
            "material ledger does not bind the selected source bytes",
            stage="source_resolution",
        )

    source_audio = transcript.get("source_audio") or {}
    source_audio_path = _resolved(
        root, Path(str(source_audio.get("path") or ""))
    )
    if (
        not source_audio_path.is_file()
        or _sha256(source_audio_path) != source_audio.get("sha256")
    ):
        raise EditorialVideoCandidateError(
            "transcript source-audio lineage mismatch", stage="source_resolution"
        )
    stt = transcript.get("stt") or {}
    transcript_caption_path = _resolved(
        root, Path(str(stt.get("model") or ""))
    )
    exported_transcript = (caption_evidence.get("source_refs") or {}).get(
        "transcript"
    ) or {}
    exported_caption_path = _resolved(
        root, Path(str(exported_transcript.get("model") or ""))
    )
    classification = str(binding.get("caption_classification") or "")
    if (
        classification != "provider_json3_sidecar"
        or stt.get("provider") != "youtube_subtitles"
        or stt.get("engine_version") != "youtube-json3"
        or transcript_caption_path != caption_track_path.resolve()
        or exported_caption_path != caption_track_path.resolve()
        or exported_transcript.get("provider") != "youtube_subtitles"
    ):
        raise EditorialVideoCandidateError(
            "caption provenance is not established as a provider JSON3 sidecar",
            stage="source_resolution",
        )

    rights = _read_json(rights_manifest_path, "rights manifest")
    source_url = str((rights.get("source_video") or {}).get("url") or "")
    if actual["source_identity"].partition(":")[2] not in source_url:
        raise EditorialVideoCandidateError(
            "rights snapshot source identity mismatch", stage="source_resolution"
        )
    return {
        "schema_version": "clippipegen.out13.authority_binding.v1",
        "status": "passed",
        "artifact_id": artifact_id,
        **actual,
        "source_material_id": material_id,
        "source_receipt": {
            "path": _display_path(source_receipt_path, root),
            "sha256": _sha256(source_receipt_path),
        },
        "material_ledger": {
            "path": _display_path(ledger_path, root),
            "sha256": _sha256(ledger_path),
        },
        "transcript": {
            "path": _display_path(transcript_path, root),
            "sha256": actual["transcript_sha256"],
            "canonical_schema_validation": "passed",
            "source_audio_path": _display_path(source_audio_path, root),
            "source_audio_sha256": source_audio["sha256"],
        },
        "caption": {
            "classification": classification,
            "provider": "youtube_subtitles",
            "format": "youtube-json3",
            "track_path": _display_path(caption_track_path, root),
            "track_sha256": actual["caption_sha256"],
            "provenance_evidence_path": _display_path(
                caption_evidence_path, root
            ),
            "provenance_evidence_sha256": _sha256(caption_evidence_path),
            "official_authorship_claim": False,
            "semantic_claims": (
                "provider timing and text only; no speaker, lyric, rights, or "
                "production acceptance inference"
            ),
        },
        "rights": {
            "path": _display_path(rights_manifest_path, root),
            "sha256": actual["rights_sha256"],
            "status": str((rights.get("compliance_check") or {}).get("status") or "unknown"),
            "snapshot_only": True,
        },
    }


def _read_bound_evidence(
    root: Path, value: Any, label: str
) -> tuple[Path, dict[str, Any]]:
    if not isinstance(value, dict):
        raise EditorialVideoCandidateError(
            f"authority binding requires {label}", stage="source_resolution"
        )
    path = _resolved(root, Path(str(value.get("path") or "")))
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise EditorialVideoCandidateError(
            f"{label} must be project-local", stage="source_resolution"
        ) from exc
    if not path.is_file() or _sha256(path) != value.get("sha256"):
        raise EditorialVideoCandidateError(
            f"{label} hash mismatch", stage="source_resolution"
        )
    return path, _read_json(path, label)


def _validate_font_binding(
    *,
    plan: dict[str, Any],
    artifact_id: str,
    style: dict[str, Any],
    font_sha256: str | None,
) -> None:
    binding = plan.get("typography_binding")
    if not isinstance(binding, dict):
        raise EditorialVideoCandidateError(
            "editorial plan requires typography_binding", stage="source_resolution"
        )
    actual = {
        "artifact_id": artifact_id,
        "typography_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
        "requested_font_family": style.get("requested_font_family"),
        "resolved_font_family": style.get("resolved_font_family"),
        "resolved_font_file_sha256": font_sha256,
    }
    if any(binding.get(key) != value for key, value in actual.items()):
        raise EditorialVideoCandidateError(
            "typography binding mismatch or font fallback detected",
            stage="source_resolution",
        )
    if (
        not font_sha256
        or style.get("requested_font_family") != style.get("resolved_font_family")
        or style.get("font_file_status") != "candidate_primary_font_file_found"
    ):
        raise EditorialVideoCandidateError(
            "typography identity cannot use an unbound fallback font",
            stage="source_resolution",
        )


def _ranges_overlap(
    left_start: float, left_end: float, right_start: float, right_end: float
) -> bool:
    return min(left_end, right_end) - max(left_start, right_start) > 0.001


def _eligible_caption_event_ids(
    events: list[dict[str, Any]], *, start: float, end: float
) -> list[str]:
    return [
        str(row["event_id"])
        for row in events
        if float(row["source_start_seconds"]) >= start - 0.001
        and float(row["source_end_seconds"]) <= end + 0.001
    ]


def _split_caption_event_ids(
    events: list[dict[str, Any]], *, start: float, end: float
) -> list[str]:
    eligible = set(_eligible_caption_event_ids(events, start=start, end=end))
    return [
        str(row["event_id"])
        for row in events
        if _ranges_overlap(
            start,
            end,
            float(row["source_start_seconds"]),
            float(row["source_end_seconds"]),
        )
        and str(row["event_id"]) not in eligible
    ]


def _source_complement(
    *, cuts: list[dict[str, Any]], source_duration_seconds: float
) -> list[tuple[float, float]]:
    gaps: list[tuple[float, float]] = []
    cursor = 0.0
    for cut in cuts:
        start = float(cut["source_in_seconds"])
        end = float(cut["source_out_seconds"])
        if start - cursor > 0.001:
            gaps.append((round(cursor, 6), round(start, 6)))
        cursor = end
    if source_duration_seconds - cursor > 0.001:
        gaps.append((round(cursor, 6), round(source_duration_seconds, 6)))
    return gaps


def _apply_out13_caption_integrity(
    *,
    caption_readback: dict[str, Any],
    caption_rows: list[dict[str, Any]],
    caption_events: list[dict[str, Any]],
    cuts: list[dict[str, Any]],
) -> None:
    expected = {
        (
            round(float(event["source_start_seconds"]), 6),
            round(float(event["source_end_seconds"]), 6),
            str(event["text_sha256"]),
        )
        for event in caption_events
        if any(
            float(event["source_start_seconds"])
            >= float(cut["source_in_seconds"]) - 0.001
            and float(event["source_end_seconds"])
            <= float(cut["source_out_seconds"]) + 0.001
            for cut in cuts
        )
    }
    actual_rows = [
        (
            round(float(row["source_start_seconds"]), 6),
            round(float(row["source_end_seconds"]), 6),
            str(row["text_sha256"]),
        )
        for row in caption_rows
    ]
    actual = set(actual_rows)
    split_count = sum(bool(row.get("split_at_cut_boundary")) for row in caption_rows)
    duplicate_count = len(actual_rows) - len(actual)
    missing_count = len(expected - actual)
    unexpected_count = len(actual - expected)
    coverage = 1.0 if not expected else len(expected & actual) / len(expected)
    caption_readback.update(
        {
            "mode": "provider_sidecar",
            "output_artifact": "captions.srt",
            "split_at_cut_boundary_count": split_count,
            "duplicate_cue_count": duplicate_count,
            "expected_eligible_cue_count": len(expected),
            "missing_eligible_cue_count": missing_count,
            "unexpected_cue_count": unexpected_count,
            "mapping_coverage_ratio": round(coverage, 6),
            "double_display_rejected": False,
            "double_display_status": "unverified",
        }
    )
    if split_count or duplicate_count or missing_count or unexpected_count:
        caption_readback["status"] = "failed"


def _selected_transcript_segments(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cut in timeline["cuts"]:
        for segment_id in cut["transcript_segment_ids"]:
            rows.append(
                {
                    "segment_id": segment_id,
                    "cut_id": cut["cut_id"],
                    "section": cut["section"],
                }
            )
    return rows


def _transcript_ids_for_caption_row(
    row: dict[str, Any], cuts: list[dict[str, Any]]
) -> list[str]:
    cut_ids = set(str(row.get("cut_id") or "").split("+"))
    values: list[str] = []
    for cut in cuts:
        if cut["cut_id"] in cut_ids:
            values.extend(cut.get("transcript_segment_ids") or [])
    return list(dict.fromkeys(values))


def _attach_caption_ids(
    cuts: list[dict[str, Any]], caption_rows: list[dict[str, Any]]
) -> None:
    for cut in cuts:
        cut["caption_ids"] = [
            row["caption_id"]
            for row in caption_rows
            if cut["cut_id"] in str(row.get("cut_id") or "").split("+")
        ]


def _closed_gates() -> dict[str, Any]:
    return {
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "rights_status": "pending_or_snapshot_only",
        "thumbnail_acceptance": False,
        "public_or_publishing_acceptance": False,
        "upload_attempted": False,
    }


def _manifest_self_hash(manifest: dict[str, Any]) -> str:
    payload = json.loads(json.dumps(manifest, ensure_ascii=False))
    payload.setdefault("manifest_self_integrity", {})["sha256"] = None
    return out12.content_fingerprint(payload)


def _escape_filter_path(path: Path) -> str:
    value = path.resolve().as_posix().replace("\\", "/")
    return value.replace(":", r"\:").replace("'", r"\'")


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EditorialVideoCandidateError(
            f"invalid {label}: {exc}", stage="source_resolution"
        ) from exc
    if not isinstance(payload, dict):
        raise EditorialVideoCandidateError(
            f"{label} must be an object", stage="source_resolution"
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
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
    timeout: int = out12.COMMAND_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[str]:
    try:
        result = runner(command, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        raise EditorialVideoCandidateError(
            f"external command failed before exit: {exc}", stage=stage
        ) from exc
    if result.returncode != 0 and not allow_failure:
        digest = hashlib.sha256((result.stderr or "").encode("utf-8")).hexdigest()
        raise EditorialVideoCandidateError(
            f"external command failed: exit={result.returncode}; stderr_sha256={digest}",
            stage=stage,
        )
    return result


def _seconds(value: float) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".")
