"""Cut-scoped diagnostic subtitle-overlay visual proof.

This generator stays inside the existing OUT-01 diagnostic render boundary and
updates the R3 visual-proof readback consumed by ED-10d. It does not approve
production render, subtitle design, creative use, publishing, or rights.
"""

from __future__ import annotations

import copy
import json
import subprocess
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny
from src.pipeline.edit_pack import load_edit_pack, validate_edit_pack
from src.pipeline.material_ledger import load_ledger
from src.pipeline.text_measure import measure_subtitle

SCHEMA_VERSION = "v1"
REPORT_KIND = "subtitle_overlay_visual_proof_report"
DEFAULT_SOURCE_VIDEO_MATERIAL_ID = "src_video_jp_pilot01"
DEFAULT_SOURCE_AUDIO_MATERIAL_ID = "src_audio_jp_pilot01"
DEFAULT_REVIEW_DIR_NAME = "jp_pilot01r3_cut_review"
RENDERABLE_SUBTITLE_STATUSES = {"included", "clamped_to_render_window"}
DIAGNOSTIC_STYLE_DIRECTION_NAME = "jp_clip_readable_v1"
LINE_WIDTH_WATCH_EAW = 40
DEFAULT_CANDIDATE_ID = "jp_clip_dialogue_badge_left_v0"
DEFAULT_CONTRACT_ID = "jp_clip_dialogue_reference_v0"
SAMPLE_FRAME_LABELS = (
    "sample_early",
    "sample_middle",
    "sample_response_referral",
    "sample_final",
)


class SubtitleOverlayVisualProofError(Exception):
    """Raised when the subtitle-overlay proof cannot be built safely."""


def build_subtitle_overlay_visual_proof(
    *,
    episode_dir: Path,
    review_dir: Path | None = None,
    target_cut_ids: list[str] | tuple[str, ...] | None = None,
    edit_pack_path: Path | None = None,
    material_ledger_path: Path | None = None,
    source_video_material_id: str = DEFAULT_SOURCE_VIDEO_MATERIAL_ID,
    source_audio_material_id: str = DEFAULT_SOURCE_AUDIO_MATERIAL_ID,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    container: str = "mp4",
    dry_run: bool = False,
    base_dir: Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
) -> dict[str, Any]:
    """Generate or plan diagnostic overlay proof for explicit target cuts."""

    base = base_dir or Path.cwd()
    review_dir = review_dir or episode_dir / "review" / DEFAULT_REVIEW_DIR_NAME
    edit_pack_path = edit_pack_path or episode_dir / "edit_pack.json"
    material_ledger_path = material_ledger_path or episode_dir / "material_ledger.json"
    target_cut_ids = tuple(target_cut_ids or ())
    if not target_cut_ids:
        raise SubtitleOverlayVisualProofError("at least one --target-cut is required")

    edit_pack = load_edit_pack(edit_pack_path)
    issues = validate_edit_pack(edit_pack)
    if issues:
        raise SubtitleOverlayVisualProofError(
            "edit_pack invalid: "
            + ", ".join(f"{issue.code}@{issue.field}" for issue in issues)
        )
    material_ledger = load_ledger(material_ledger_path)
    representative_path = review_dir / "representative_visual_proof_report.json"
    representative_report = _load_required_json(representative_path)

    source_media = _source_media_status(
        material_ledger=material_ledger,
        source_video_material_id=source_video_material_id,
        source_audio_material_id=source_audio_material_id,
        base=base,
    )
    if source_media["status"] != "available_from_material_ledger":
        raise SubtitleOverlayVisualProofError("source media is missing from material_ledger paths")

    cuts = _cut_index(edit_pack)
    subtitles = _subtitle_index(edit_pack)
    output_paths = _output_paths(review_dir=review_dir)
    cut_reports: list[dict[str, Any]] = []
    for cut_id in target_cut_ids:
        cut = cuts.get(cut_id)
        if cut is None:
            raise SubtitleOverlayVisualProofError(f"target cut missing from edit_pack: {cut_id}")
        cut_reports.append(
            _build_cut_proof(
                episode_id=str(edit_pack.get("episode_id") or episode_dir.name),
                cut=cut,
                subtitles=subtitles.get(cut_id) or [],
                source_media=source_media,
                output_paths=output_paths,
                ffmpeg_path=ffmpeg_path,
                ffprobe_path=ffprobe_path,
                container=container,
                dry_run=dry_run,
                base=base,
                runner=runner,
            )
        )

    report_path = review_dir / "subtitle_overlay_visual_proof_report.json"
    report_html_path = review_dir / "subtitle_overlay_visual_proof_report.html"
    updated_representative_path = representative_path
    updated_representative_html_path = review_dir / "representative_visual_proof_report.html"
    report = _report_payload(
        episode_id=str(edit_pack.get("episode_id") or episode_dir.name),
        target_cut_ids=target_cut_ids,
        source_media=source_media,
        cut_reports=cut_reports,
        representative_report_path=representative_path,
        representative_report=representative_report,
        report_path=report_path,
        report_html_path=report_html_path,
        base=base,
        dry_run=dry_run,
    )

    updated_representative = _updated_representative_report(
        representative_report=representative_report,
        overlay_report=report,
        cut_reports=cut_reports,
        base=base,
    )
    if not dry_run:
        review_dir.mkdir(parents=True, exist_ok=True)
        _write_json(report, report_path)
        report_html_path.write_text(_overlay_report_html(report), encoding="utf-8")
        _write_json(updated_representative, updated_representative_path)
        updated_representative_html_path.write_text(
            _representative_report_html(updated_representative),
            encoding="utf-8",
        )

    visual_proof_status = _aggregate_visual_proof_status(
        updated_representative.get("per_cut_visual_assessment") or [],
        target_cut_ids=target_cut_ids,
    )
    return {
        "report": report,
        "representative_visual_proof_report": updated_representative,
        "report_path": report_path,
        "report_html_path": report_html_path,
        "representative_visual_proof_report_path": updated_representative_path,
        "representative_visual_proof_report_html_path": updated_representative_html_path,
        "visual_proof_status": visual_proof_status,
        "dry_run": dry_run,
    }


def _build_cut_proof(
    *,
    episode_id: str,
    cut: dict[str, Any],
    subtitles: list[dict[str, Any]],
    source_media: dict[str, Any],
    output_paths: dict[str, Any],
    ffmpeg_path: str | Path | None,
    ffprobe_path: str | Path | None,
    container: str,
    dry_run: bool,
    base: Path,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    cut_id = str(cut.get("id") or "")
    start_seconds = _required_float(cut.get("start_seconds"), f"{cut_id}.start_seconds")
    end_seconds = _required_float(cut.get("end_seconds"), f"{cut_id}.end_seconds")
    duration = round(end_seconds - start_seconds, 3)
    if duration <= 0:
        raise SubtitleOverlayVisualProofError(f"target cut duration must be positive: {cut_id}")

    items = _subtitle_items_for_cut(
        cut_id=cut_id,
        cut_start_seconds=start_seconds,
        cut_end_seconds=end_seconds,
        subtitles=subtitles,
    )
    renderable_items = [
        item for item in items if item.get("status") in RENDERABLE_SUBTITLE_STATUSES
    ]
    cut_paths = output_paths["cuts"][cut_id]
    if dry_run:
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            source_media=source_media,
            cut_paths=cut_paths,
            overlay_present=False,
            status="planned",
            output_metadata={},
            selected_profile=None,
            fallback_used=None,
            attempted_render_profiles=[],
            attempts=[],
            frame_extract=None,
            sample_frame_extracts=None,
            error=None,
            base=base,
        )

    if not renderable_items:
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            source_media=source_media,
            cut_paths=cut_paths,
            overlay_present=False,
            status="failed_no_renderable_subtitles",
            output_metadata={},
            selected_profile=None,
            fallback_used=None,
            attempted_render_profiles=[],
            attempts=[],
            frame_extract=None,
            sample_frame_extracts=None,
            error="no renderable subtitle items for target cut",
            base=base,
        )

    cut_paths["output_dir"].mkdir(parents=True, exist_ok=True)
    _write_srt(cut_paths["subtitle_file"], renderable_items)
    try:
        render_result = ffmpeg_tiny.render_tiny_proof(
            source_video_path=source_media["source_video"]["resolved_path"],
            source_audio_path=source_media["source_audio"]["resolved_path"],
            output_path=cut_paths["video"],
            start_seconds=start_seconds,
            duration_seconds=duration,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            container=container,
            subtitle_file_path=cut_paths["subtitle_file"],
            runner=runner,
        )
        video_path = Path(render_result.output_path)
        frame_extract = _extract_frame(
            video_path=video_path,
            frame_path=cut_paths["frame"],
            seconds=_representative_frame_seconds(renderable_items, duration),
            ffmpeg_path=render_result.ffmpeg_path,
            runner=runner,
        )
        sample_plan = _sample_frame_plan(renderable_items, duration)
        sample_frame_extracts = _extract_sample_frames(
            video_path=video_path,
            sample_paths=cut_paths["sample_frames"],
            sample_plan=sample_plan,
            ffmpeg_path=render_result.ffmpeg_path,
            runner=runner,
        )
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            source_media=source_media,
            cut_paths={**cut_paths, "video": video_path},
            overlay_present=True,
            status="available_diagnostic_subtitle_overlay",
            output_metadata=render_result.metadata,
            selected_profile=render_result.selected_profile.to_dict(),
            fallback_used=render_result.fallback_used,
            attempted_render_profiles=[attempt.to_dict() for attempt in render_result.attempts],
            attempts=[attempt.to_dict() for attempt in render_result.attempts],
            frame_extract=frame_extract,
            sample_frame_extracts=sample_frame_extracts,
            error=None,
            base=base,
        )
    except (OSError, ffmpeg_tiny.TinyRenderError) as exc:
        failure_reason = getattr(exc, "failure_reason", "subtitle_overlay_render_failed")
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            source_media=source_media,
            cut_paths=cut_paths,
            overlay_present=False,
            status="failed_subtitle_overlay_generation",
            output_metadata={},
            selected_profile=None,
            fallback_used=None,
            attempted_render_profiles=[
                attempt.to_dict() for attempt in getattr(exc, "attempts", [])
            ],
            attempts=[attempt.to_dict() for attempt in getattr(exc, "attempts", [])],
            frame_extract=None,
            sample_frame_extracts=None,
            error=f"{failure_reason}: {exc}",
            base=base,
        )


def _cut_report(
    *,
    episode_id: str,
    cut: dict[str, Any],
    items: list[dict[str, Any]],
    source_media: dict[str, Any],
    cut_paths: dict[str, Path],
    overlay_present: bool,
    status: str,
    output_metadata: dict[str, Any],
    selected_profile: dict[str, Any] | None,
    fallback_used: bool | None,
    attempted_render_profiles: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    frame_extract: dict[str, Any] | None,
    sample_frame_extracts: list[dict[str, Any]] | None,
    error: str | None,
    base: Path,
) -> dict[str, Any]:
    cut_id = str(cut.get("id") or "")
    start_seconds = _required_float(cut.get("start_seconds"), f"{cut_id}.start_seconds")
    end_seconds = _required_float(cut.get("end_seconds"), f"{cut_id}.end_seconds")
    renderable_items = [
        item for item in items if item.get("status") in RENDERABLE_SUBTITLE_STATUSES
    ]
    sample_frame_paths = cut_paths.get("sample_frames") or {}
    return {
        "episode_id": episode_id,
        "cut_id": cut_id,
        "visual_proof_status": status,
        "subtitle_overlay_present": bool(overlay_present),
        "overlay_presence_method": (
            "successful_ffmpeg_subtitles_filter_with_non_empty_srt; not OCR verified"
            if overlay_present
            else "not_generated_or_failed"
        ),
        "source_used": "diagnostic_subtitle_overlay_render_from_material_ledger",
        "source_media": {
            "source_video": _source_media_public(source_media["source_video"]),
            "source_audio": _source_media_public(source_media["source_audio"]),
        },
        "subtitle_source": {
            "source_type": _single_or_mixed(
                [str(item.get("subtitle_source_type") or "") for item in items]
            ),
            "subtitle_source_types": _unique_strings(
                item.get("subtitle_source_type") for item in items
            ),
            "subtitle_ids": [item.get("subtitle_id") for item in items if item.get("subtitle_id")],
            "rendered_subtitle_ids": [
                item.get("subtitle_id") for item in renderable_items if item.get("subtitle_id")
            ],
            "item_count": len(items),
            "renderable_item_count": len(renderable_items),
            "source_segment_ids": _unique_strings(
                segment_id
                for item in items
                for segment_id in item.get("source_segment_ids", [])
            ),
        },
        "style_direction": _diagnostic_style_direction(),
        "style_parameters": _style_parameter_readback(items),
        "line_width_readback": _line_width_readback(items),
        "timing_window": {
            "source_start_seconds": start_seconds,
            "source_end_seconds": end_seconds,
            "duration_seconds": round(end_seconds - start_seconds, 3),
            "render_start_seconds": 0.0,
            "render_end_seconds": round(end_seconds - start_seconds, 3),
        },
        "subtitle_timing": {
            "items": items,
            "status_counts": _status_counts(items),
        },
        "generated_artifacts": {
            "video": _display_path(cut_paths["video"], base),
            "frame": _display_path(cut_paths["frame"], base),
            "sample_frames": {
                label: _display_path(path, base)
                for label, path in sample_frame_paths.items()
            },
            "diagnostic_subtitle_file": _display_path(cut_paths["subtitle_file"], base),
        },
        "artifact_exists": {
            "video": cut_paths["video"].exists(),
            "frame": cut_paths["frame"].exists(),
            "sample_frames": {
                label: path.exists() for label, path in sample_frame_paths.items()
            },
            "diagnostic_subtitle_file": cut_paths["subtitle_file"].exists(),
        },
        "output_metadata": output_metadata,
        "selected_render_profile": selected_profile,
        "fallback_used": fallback_used,
        "attempted_render_profiles": attempted_render_profiles,
        "attempts": attempts,
        "frame_extract": frame_extract or {},
        "sample_selection_policy": (
            "sample frames are selected only from renderable subtitle cue midpoints"
        ),
        "sample_frame_plan": _sample_frame_plan(renderable_items, round(end_seconds - start_seconds, 3)),
        "sample_frame_extracts": sample_frame_extracts or [],
        "typography_status": (
            "diagnostic_overlay_visible_human_review_required"
            if overlay_present
            else "visual_proof_required_no_subtitle_overlay"
        ),
        "safe_area_status": (
            "diagnostic_overlay_visible_human_review_required"
            if overlay_present
            else "visual_proof_required_no_subtitle_overlay"
        ),
        "line_wrapping_status": (
            "diagnostic_overlay_generated_human_review_required"
            if overlay_present
            else "line_wrap_visual_review_required"
        ),
        "timing_sync_status": (
            "diagnostic_timing_overlay_generated_human_review_required"
            if overlay_present
            else "timing_visual_audio_review_required"
        ),
        "limitations": [
            "diagnostic subtitle overlay only; not production subtitle design",
            "FFmpeg default subtitle styling is used; typography polish is not claimed",
            "safe-area, line wrapping, readability, and timing sync still require human review",
            "overlay presence is inferred from successful subtitle filter/render and generated SRT, not OCR",
            "sidecar SRT is reference-only and is not the review surface by itself",
            "rights_status=pending; production/public usage is not allowed",
        ],
        "production_candidate": False,
        "rights_status": "pending",
        "production_usage_allowed": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "error": error,
    }


def _report_payload(
    *,
    episode_id: str,
    target_cut_ids: tuple[str, ...],
    source_media: dict[str, Any],
    cut_reports: list[dict[str, Any]],
    representative_report_path: Path,
    representative_report: dict[str, Any],
    report_path: Path,
    report_html_path: Path,
    base: Path,
    dry_run: bool,
) -> dict[str, Any]:
    success_count = sum(
        1 for item in cut_reports if item.get("subtitle_overlay_present") is True
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "report_kind": REPORT_KIND,
        "created_at": _now(),
        "episode_id": episode_id,
        "scope": "cut_scoped_subtitle_overlay_visual_proof",
        "target_cuts": list(target_cut_ids),
        "dry_run": dry_run,
        "source_media_status": source_media["status"],
        "source_media": {
            "source_video": _source_media_public(source_media["source_video"]),
            "source_audio": _source_media_public(source_media["source_audio"]),
        },
        "style_direction": _diagnostic_style_direction(),
        "style_parameters": _report_style_parameter_summary(cut_reports),
        "cut_results": cut_reports,
        "aggregate_summary": {
            "target_cut_count": len(target_cut_ids),
            "subtitle_overlay_available_count": success_count,
            "failed_count": len(cut_reports) - success_count,
            "all_target_cuts_have_overlay": success_count == len(target_cut_ids),
        },
        "representative_visual_proof_report": _display_path(representative_report_path, base),
        "related_visual_artifacts": _related_visual_artifacts(representative_report),
        "review_surface": _review_surface_readback(report_html_path=report_html_path, base=base),
        "outputs": {
            "json": _display_path(report_path, base),
            "html": _display_path(report_html_path, base),
        },
        "production_candidate": False,
        "rights_status": "pending",
        "production_usage_allowed": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "warnings": [
            "Diagnostic overlay proof only; production render acceptance is not claimed.",
            "Production subtitle design, creative acceptance, publishing acceptance, and rights approval are out of scope.",
            "Sidecar SRT is reference-only; human review must use visible subtitle-bearing frames/video.",
            "Generated artifacts are local review artifacts and must not be staged from episodes/.",
        ],
    }


def _review_surface_readback(*, report_html_path: Path, base: Path) -> dict[str, Any]:
    return {
        "candidate_id": DEFAULT_CANDIDATE_ID,
        "contract_id": DEFAULT_CONTRACT_ID,
        "sidecar_srt_reference_only": True,
        "production_subtitle_design_acceptance": False,
        "minimum_human_review_file": _display_path(report_html_path, base),
    }


def _diagnostic_style_direction() -> dict[str, Any]:
    return {
        "preset_name": DIAGNOSTIC_STYLE_DIRECTION_NAME,
        "contract_status": "diagnostic_direction_readback",
        "target_viewing_context": "smartphone_readable_japanese_clip_subtitle",
        "visual_weight": "larger_and_more_assertive_than_restrained_film_or_news_subtitles",
        "reaction_caption_tolerance": "short_reaction_captions_may_carry_stronger_visual_weight",
        "long_line_policy": (
            "long captions must be watched for excessive horizontal spread; "
            "wrapping/layout is not accepted by this diagnostic proof"
        ),
        "review_status": "diagnostic_human_review_required",
        "not_acceptance": [
            "not_production_subtitle_design_acceptance",
            "not_production_render_acceptance",
            "not_creative_acceptance",
            "not_rights_approval",
            "not_public_use_permission",
        ],
    }


def _style_parameter_readback(items: list[dict[str, Any]]) -> dict[str, Any]:
    style_slots = _unique_strings(item.get("style_slot") for item in items)
    return {
        "renderer": "ffmpeg_subtitles_filter_srt",
        "style_slot": _single_or_mixed(style_slots) or "subtitle.default",
        "style_slots": style_slots or ["subtitle.default"],
        "explicit_ass_force_style": False,
        "font_size": {
            "value": None,
            "unit": "ass_points",
            "source": "not_explicitly_pinned_in_this_proof",
            "readback": "FFmpeg/libass SRT default; accepted direction is tracked separately",
        },
        "outline": {
            "value": None,
            "unit": "ass_outline_units",
            "source": "not_explicitly_pinned_in_this_proof",
            "readback": "FFmpeg/libass SRT default",
        },
        "margin_v": {
            "value": None,
            "unit": "ass_pixels_or_script_units",
            "source": "not_explicitly_pinned_in_this_proof",
            "readback": "FFmpeg/libass SRT default",
        },
        "alignment": {
            "value": "bottom_center_fixed",
            "source": "diagnostic SRT overlay uses bottom subtitle placement",
        },
        "wrapping": {
            "policy": "preserve_existing_newlines_only",
            "automatic_wrap_applied_by_overlay_generator": False,
            "available_proxy_wrap_eaw": LINE_WIDTH_WATCH_EAW,
            "watch_item": (
                "Long subtitle line width may require a later clip subtitle "
                "layout preset or wrapping policy."
            ),
        },
    }


def _line_width_readback(items: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for item in items:
        text = str(item.get("text") or "")
        raw = measure_subtitle(text)
        wrapped = measure_subtitle(text, wrap_eaw=LINE_WIDTH_WATCH_EAW)
        rows.append(
            {
                "subtitle_id": item.get("subtitle_id"),
                "status": item.get("status"),
                "raw_longest_line_eaw": raw.longest_line_eaw,
                "raw_line_count": len(raw.lines),
                "watch_wrap_eaw": LINE_WIDTH_WATCH_EAW,
                "would_wrap_at_watch_eaw": wrapped.needs_wrap,
                "wrapped_line_count": len(wrapped.lines),
                "max_wrapped_line_eaw": wrapped.longest_line_eaw,
            }
        )
    return {
        "measurement_kind": "east_asian_width_proxy",
        "policy_status": "watch_only_no_layout_engine_change",
        "watch_wrap_eaw": LINE_WIDTH_WATCH_EAW,
        "subtitle_count_measured": len(rows),
        "max_raw_line_eaw": max((row["raw_longest_line_eaw"] for row in rows), default=0),
        "needs_wrap_count": sum(1 for row in rows if row["would_wrap_at_watch_eaw"]),
        "items": rows,
        "known_limitation": (
            "This is a text-width proxy only; it does not prove rendered pixel width, "
            "kinsoku behavior, safe-area, or final layout."
        ),
    }


def _report_style_parameter_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    style_slots = _unique_strings(
        slot
        for cut in cut_reports
        for slot in (cut.get("style_parameters") or {}).get("style_slots", [])
    )
    long_line_count = sum(
        int((cut.get("line_width_readback") or {}).get("needs_wrap_count") or 0)
        for cut in cut_reports
    )
    return {
        **_style_parameter_readback([]),
        "style_slot": _single_or_mixed(style_slots) or "subtitle.default",
        "style_slots": style_slots or ["subtitle.default"],
        "per_cut": {
            str(cut.get("cut_id")): cut.get("style_parameters") or {}
            for cut in cut_reports
        },
        "line_width_watch_summary": {
            "watch_wrap_eaw": LINE_WIDTH_WATCH_EAW,
            "cuts_measured": len(cut_reports),
            "subtitle_items_needing_wrap_watch": long_line_count,
            "policy_status": "watch_only_no_layout_engine_change",
        },
    }


def _related_visual_artifacts(representative_report: dict[str, Any]) -> dict[str, Any]:
    outputs = representative_report.get("outputs") if isinstance(representative_report, dict) else {}
    contact_sheet = None
    representative_html = None
    if isinstance(outputs, dict):
        contact_sheet = outputs.get("contact_sheet") or outputs.get("visual_proof_contact_sheet_png")
        representative_html = (
            outputs.get("representative_visual_proof_report_html") or outputs.get("html")
        )
    return {
        "representative_visual_proof_report_html": representative_html,
        "contact_sheet": contact_sheet,
    }


def _updated_representative_report(
    *,
    representative_report: dict[str, Any],
    overlay_report: dict[str, Any],
    cut_reports: list[dict[str, Any]],
    base: Path,
) -> dict[str, Any]:
    updated = copy.deepcopy(representative_report)
    updated["updated_at"] = _now()
    updated["production_candidate"] = False
    updated["creative_acceptance"] = False
    updated["publish_acceptance"] = False
    updated["rights_status"] = "pending"
    updated["production_usage_allowed"] = False
    updated["diagnostic_style_direction"] = overlay_report["style_direction"]
    updated["diagnostic_style_parameters"] = overlay_report["style_parameters"]
    updated["review_surface"] = overlay_report["review_surface"]
    updated["subtitle_overlay_visual_proof"] = {
        "report": overlay_report["outputs"]["json"],
        "target_cuts": overlay_report["target_cuts"],
        "all_target_cuts_have_overlay": overlay_report["aggregate_summary"][
            "all_target_cuts_have_overlay"
        ],
        "style_direction": overlay_report["style_direction"],
        "style_parameters": overlay_report["style_parameters"],
    }
    by_cut = {str(item.get("cut_id")): item for item in cut_reports}
    assessments = updated.get("per_cut_visual_assessment") or []
    for assessment in assessments:
        cut_id = str(assessment.get("cut_id") or "")
        proof = by_cut.get(cut_id)
        if not proof or proof.get("subtitle_overlay_present") is not True:
            continue
        previous_path = assessment.get("visual_proof_artifact_path")
        previous_status = assessment.get("visual_proof_status")
        assessment["previous_source_frame_artifact_path"] = previous_path
        assessment["previous_visual_proof_status"] = previous_status
        assessment["visual_proof_status"] = "available_diagnostic_subtitle_overlay"
        assessment["visual_proof_artifact_path"] = proof["generated_artifacts"]["frame"]
        assessment["visual_proof_video_artifact_path"] = proof["generated_artifacts"]["video"]
        assessment["subtitle_overlay_sample_frames"] = proof["generated_artifacts"].get(
            "sample_frames"
        )
        assessment["diagnostic_subtitle_file_path"] = proof["generated_artifacts"][
            "diagnostic_subtitle_file"
        ]
        assessment["subtitle_overlay_present"] = True
        assessment["overlay_presence_method"] = proof["overlay_presence_method"]
        assessment["source_used"] = proof["source_used"]
        assessment["typography_status"] = proof["typography_status"]
        assessment["safe_area_status"] = proof["safe_area_status"]
        assessment["line_wrapping_status"] = proof["line_wrapping_status"]
        assessment["timing_sync_status"] = proof["timing_sync_status"]
        assessment["style_direction"] = proof["style_direction"]
        assessment["style_parameters"] = proof["style_parameters"]
        assessment["line_width_readback"] = proof["line_width_readback"]
        assessment["proof_limitations"] = proof["limitations"]
        assessment["recommended_next_action"] = [
            f"human_review_{cut_id}_diagnostic_subtitle_overlay_for_readability_safe_area_line_wrapping_and_timing",
            "keep_production_candidate_false_until_visual_proof_human_review_and_rights_are_resolved",
        ]
        assessment["subtitle_overlay_readback"] = {
            "report": overlay_report["outputs"]["json"],
            "style_direction": proof["style_direction"],
            "style_parameters": proof["style_parameters"],
            "line_width_readback": proof["line_width_readback"],
            "timing_window": proof["timing_window"],
            "subtitle_source": proof["subtitle_source"],
            "artifact_exists": proof["artifact_exists"],
            "sample_selection_policy": proof["sample_selection_policy"],
            "sample_frame_plan": proof["sample_frame_plan"],
            "sample_frame_extracts": proof["sample_frame_extracts"],
        }
    updated["aggregate_summary"] = _representative_aggregate(assessments)
    outputs = updated.get("outputs")
    if not isinstance(outputs, dict):
        updated["outputs"] = {}
    updated["outputs"]["json"] = _display_path(
        Path(overlay_report["representative_visual_proof_report"]), base
    )
    return updated


def _representative_aggregate(assessments: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str(item.get("visual_proof_status") or "") for item in assessments]
    return {
        "target_cut_count": len(assessments),
        "visual_proof_available_count": sum(
            1 for status in statuses if status and status != "missing"
        ),
        "subtitle_overlay_visual_proof_available_count": sum(
            1
            for status in statuses
            if status in {"available_diagnostic_subtitle_overlay", "available_diagnostic_render_frame"}
        ),
        "visual_proof_missing_count": sum(1 for status in statuses if status == "missing"),
        "source_frame_only_count": sum(1 for status in statuses if "source_frame_only" in status),
        "visual_proof_required_count": len(assessments),
        "retained_context_risk_count": sum(
            1 for item in assessments if item.get("retained_context_risk") is True
        ),
        "rights_blocker_present": True,
        "production_candidate_transition_allowed": False,
    }


def _aggregate_visual_proof_status(
    assessments: list[dict[str, Any]],
    *,
    target_cut_ids: tuple[str, ...],
) -> str:
    target = [
        item for item in assessments if str(item.get("cut_id") or "") in set(target_cut_ids)
    ]
    if any(str(item.get("visual_proof_status") or "") == "missing" for item in target):
        return "blocked_missing_visual_proof"
    if any(
        "no_subtitle_overlay" in str(item.get("visual_proof_status") or "")
        or "visual_proof_required" in str(item.get("typography_status") or "")
        or "visual_proof_required" in str(item.get("safe_area_status") or "")
        for item in target
    ):
        return "blocked_no_cut_002_cut_003_overlay_proof"
    return "available_requires_human_review"


def _source_media_status(
    *,
    material_ledger: dict[str, Any],
    source_video_material_id: str,
    source_audio_material_id: str,
    base: Path,
) -> dict[str, Any]:
    materials = {
        str(item.get("id")): item
        for item in material_ledger.get("materials") or []
        if isinstance(item, dict) and item.get("id")
    }
    video = _material_status(materials.get(source_video_material_id), base=base)
    audio = _material_status(materials.get(source_audio_material_id), base=base)
    available = bool(video["ledger_entry_exists"] and video["exists"] and audio["ledger_entry_exists"] and audio["exists"])
    return {
        "status": "available_from_material_ledger" if available else "missing_source_media",
        "source_video": {**video, "material_id": source_video_material_id},
        "source_audio": {**audio, "material_id": source_audio_material_id},
        "note": (
            "current source of truth is material_ledger paths"
            if available
            else "source media is missing or not readable from material_ledger paths"
        ),
    }


def _material_status(material: dict[str, Any] | None, *, base: Path) -> dict[str, Any]:
    file_path = material.get("file_path") if material else None
    resolved = _resolve_existing_path(file_path, base=base) if file_path else None
    return {
        "ledger_entry_exists": bool(material),
        "path": str(file_path).replace("\\", "/") if file_path else None,
        "resolved_path": resolved,
        "exists": bool(resolved and resolved.exists()),
        "byte_size": resolved.stat().st_size if resolved and resolved.exists() else None,
        "sha256": material.get("hash_sha256") if material else None,
    }


def _source_media_public(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "material_id": source.get("material_id"),
        "path": source.get("path"),
        "exists": source.get("exists"),
        "byte_size": source.get("byte_size"),
        "sha256": source.get("sha256"),
    }


def _cut_index(edit_pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("id")): item
        for item in edit_pack.get("cut_candidates") or []
        if isinstance(item, dict) and item.get("id")
    }


def _subtitle_index(edit_pack: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for item in edit_pack.get("subtitles") or []:
        if not isinstance(item, dict):
            continue
        cut_id = item.get("cut_id")
        if cut_id:
            index.setdefault(str(cut_id), []).append(item)
    return index


def _subtitle_items_for_cut(
    *,
    cut_id: str,
    cut_start_seconds: float,
    cut_end_seconds: float,
    subtitles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for subtitle in subtitles:
        text = str(subtitle.get("text") or "").strip()
        source_start = _optional_float(subtitle.get("start_seconds"))
        source_end = _optional_float(subtitle.get("end_seconds"))
        status = "included"
        skip_reason = None
        render_start = None
        render_end = None
        if not text:
            status = "empty_text"
            skip_reason = "subtitle text is empty after trimming"
        elif source_start is None or source_end is None or source_end <= source_start:
            status = "invalid_timing"
            skip_reason = "subtitle timing must have numeric start/end with end greater than start"
        elif source_end <= cut_start_seconds:
            status = "skipped_before_render_window"
            skip_reason = "subtitle ends before the target cut starts"
        elif source_start >= cut_end_seconds:
            status = "skipped_after_render_window"
            skip_reason = "subtitle starts after the target cut ends"
        else:
            overlap_start = max(source_start, cut_start_seconds)
            overlap_end = min(source_end, cut_end_seconds)
            render_start = round(overlap_start - cut_start_seconds, 3)
            render_end = round(overlap_end - cut_start_seconds, 3)
            if source_start < cut_start_seconds or source_end > cut_end_seconds:
                status = "clamped_to_render_window"
        items.append(
            {
                "subtitle_id": subtitle.get("id"),
                "cut_id": cut_id,
                "subtitle_source_type": subtitle.get("source_type"),
                "source_segment_ids": _entry_source_segment_ids(subtitle),
                "source_start_seconds": source_start,
                "source_end_seconds": source_end,
                "render_start_seconds": render_start,
                "render_end_seconds": render_end,
                "status": status,
                "skip_reason": skip_reason,
                "text": text,
                "style_slot": subtitle.get("style_slot"),
                "draft": subtitle.get("draft"),
                "diagnostic": subtitle.get("diagnostic"),
                "not_production_subtitle_design": subtitle.get("not_production_subtitle_design"),
            }
        )
    return items


def _entry_source_segment_ids(entry: dict[str, Any]) -> list[str]:
    raw = entry.get("source_segment_ids")
    values = raw if isinstance(raw, list) else []
    if entry.get("source_segment_id"):
        values = [*values, entry.get("source_segment_id")]
    return _unique_strings(values)


def _output_paths(*, review_dir: Path) -> dict[str, Any]:
    cuts: dict[str, dict[str, Path]] = {}

    def for_cut(cut_id: str) -> dict[str, Path]:
        if cut_id not in cuts:
            stem = f"subtitle_overlay_visual_proof_{cut_id}"
            cuts[cut_id] = {
                "output_dir": review_dir,
                "video": review_dir / f"{stem}.mp4",
                "frame": review_dir / f"{stem}.png",
                "sample_frames": {
                    label: review_dir / f"{stem}.{label}.png"
                    for label in SAMPLE_FRAME_LABELS
                },
                "subtitle_file": review_dir / f"{stem}.srt",
            }
        return cuts[cut_id]

    return {"cuts": _LazyCutPaths(for_cut)}


class _LazyCutPaths(dict):
    def __init__(self, factory):
        super().__init__()
        self._factory = factory

    def __missing__(self, key):
        value = self._factory(key)
        self[key] = value
        return value


def _write_srt(path: Path, items: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    for idx, item in enumerate(items, start=1):
        lines.append(str(idx))
        lines.append(
            f"{_srt_time(float(item['render_start_seconds']))} --> {_srt_time(float(item['render_end_seconds']))}"
        )
        lines.extend(str(item.get("text") or "").splitlines() or [""])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _extract_frame(
    *,
    video_path: Path,
    frame_path: Path,
    seconds: float,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    frame_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_path,
        "-y",
        "-ss",
        str(round(seconds, 3)),
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        str(frame_path),
    ]
    result = runner(command, capture_output=True, text=True, timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS)
    digest = ffmpeg_tiny.build_stderr_digest(result.stderr)
    return {
        "status": "succeeded" if result.returncode == 0 and frame_path.exists() else "failed",
        "exit_code": result.returncode,
        "frame_seconds": round(seconds, 3),
        "path": str(frame_path).replace("\\", "/"),
        "stderr_digest": digest,
    }


def _extract_sample_frames(
    *,
    video_path: Path,
    sample_paths: dict[str, Path],
    sample_plan: list[dict[str, Any]],
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> list[dict[str, Any]]:
    extracts: list[dict[str, Any]] = []
    plan_by_label = {str(item.get("label")): item for item in sample_plan}
    for label in SAMPLE_FRAME_LABELS:
        plan = plan_by_label.get(label)
        frame_path = sample_paths.get(label)
        if not plan or frame_path is None:
            continue
        extract = _extract_frame(
            video_path=video_path,
            frame_path=frame_path,
            seconds=float(plan["frame_seconds"]),
            ffmpeg_path=ffmpeg_path,
            runner=runner,
        )
        extracts.append({**plan, **extract})
    return extracts


def _representative_frame_seconds(items: list[dict[str, Any]], duration: float) -> float:
    renderable = [item for item in items if item.get("status") in RENDERABLE_SUBTITLE_STATUSES]
    if not renderable:
        return 0.0
    first = renderable[0]
    start = _optional_float(first.get("render_start_seconds")) or 0.0
    end = _optional_float(first.get("render_end_seconds")) or min(duration, start + 0.5)
    midpoint = start + max(0.1, min(0.5, (end - start) / 2))
    return max(0.0, min(duration, midpoint))


def _sample_frame_plan(items: list[dict[str, Any]], duration: float) -> list[dict[str, Any]]:
    renderable = [
        item for item in items if item.get("status") in RENDERABLE_SUBTITLE_STATUSES
    ]
    if not renderable:
        return []
    choices = {
        "sample_early": renderable[0],
        "sample_middle": _nearest_subtitle_item(renderable, duration / 2),
        "sample_response_referral": _response_referral_sample_item(renderable, duration),
        "sample_final": renderable[-1],
    }
    plan: list[dict[str, Any]] = []
    for label in SAMPLE_FRAME_LABELS:
        item = choices[label]
        plan.append(
            {
                "label": label,
                "frame_seconds": _subtitle_midpoint_seconds(item, duration),
                "subtitle_id": item.get("subtitle_id"),
                "source_segment_ids": item.get("source_segment_ids") or [],
                "render_start_seconds": item.get("render_start_seconds"),
                "render_end_seconds": item.get("render_end_seconds"),
                "selection_basis": _sample_selection_basis(label),
            }
        )
    return plan


def _nearest_subtitle_item(items: list[dict[str, Any]], target_seconds: float) -> dict[str, Any]:
    return min(
        items,
        key=lambda item: abs(_subtitle_midpoint_seconds(item, target_seconds) - target_seconds),
    )


def _response_referral_sample_item(items: list[dict[str, Any]], duration: float) -> dict[str, Any]:
    explicit_response_items = [
        item
        for item in items
        if _numeric_suffix(item.get("subtitle_id")) >= 25
        or any(_numeric_suffix(segment_id) >= 25 for segment_id in item.get("source_segment_ids") or [])
    ]
    if explicit_response_items:
        return explicit_response_items[0]
    late_items = [
        item for item in items if _subtitle_midpoint_seconds(item, duration) >= duration * 0.72
    ]
    if late_items:
        return late_items[0]
    return items[min(len(items) - 1, max(0, int(len(items) * 0.75)))]


def _subtitle_midpoint_seconds(item: dict[str, Any], duration: float) -> float:
    start = _optional_float(item.get("render_start_seconds"))
    end = _optional_float(item.get("render_end_seconds"))
    if start is None or end is None or end <= start:
        return round(max(0.0, min(duration, 0.0)), 3)
    return round(max(0.0, min(duration, start + ((end - start) / 2))), 3)


def _sample_selection_basis(label: str) -> str:
    return {
        "sample_early": "first renderable subtitle cue midpoint",
        "sample_middle": "renderable subtitle cue midpoint nearest cut midpoint",
        "sample_response_referral": (
            "sub_025+ or late renderable subtitle cue midpoint for response/referral review"
        ),
        "sample_final": "last renderable subtitle cue midpoint",
    }.get(label, "renderable subtitle cue midpoint")


def _numeric_suffix(value: Any) -> int:
    text = str(value or "")
    digits = ""
    for char in reversed(text):
        if not char.isdigit():
            break
        digits = char + digits
    return int(digits) if digits else -1


def _status_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        status = str(item.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _load_required_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SubtitleOverlayVisualProofError(f"required JSON not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _overlay_report_html(report: dict[str, Any]) -> str:
    rows = "\n".join(_overlay_cut_row(item) for item in report.get("cut_results") or [])
    style_summary = _style_summary_html(
        report.get("style_direction") or {},
        report.get("style_parameters") or {},
    )
    related_visuals = _related_visuals_html(report.get("related_visual_artifacts") or {})
    review_surface = _review_surface_html(report.get("review_surface") or {})
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Subtitle Overlay Visual Proof</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; line-height: 1.5; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
    th {{ background: #f3f3f3; }}
    .warn {{ color: #8a4b00; }}
    .proof-frame {{ max-width: 360px; width: 100%; border: 1px solid #ccc; display: block; margin-bottom: 8px; }}
    .contact-sheet {{ max-width: 100%; border: 1px solid #ccc; display: block; margin: 8px 0 16px; }}
    .sample-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin-bottom: 10px; }}
    .sample-card {{ margin: 0; }}
    .sample-card img {{ width: 100%; border: 1px solid #aaa; display: block; }}
    .sample-card figcaption {{ font-size: 12px; color: #333; margin-top: 3px; }}
    video {{ max-width: 360px; width: 100%; display: block; margin-top: 8px; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; }}
    dt {{ font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Subtitle Overlay Visual Proof</h1>
  <p class="warn">Diagnostic only. Not production render, subtitle design acceptance, creative acceptance, publishing acceptance, or rights approval.</p>
  <p>episode: {escape(str(report.get("episode_id", "")))}</p>
  <p>target cuts: {escape(", ".join(report.get("target_cuts") or []))}</p>
  <p>rights_status: {escape(str(report.get("rights_status", "")))} / production_candidate: {escape(str(report.get("production_candidate", "")))}</p>
{review_surface}
  <section>
    <h2>Diagnostic Style Direction</h2>
{style_summary}
  </section>
{related_visuals}
  <table>
    <tr><th>cut</th><th>status</th><th>visual</th><th>artifacts</th><th>style readback</th><th>review statuses</th><th>limitations</th></tr>
    {rows}
  </table>
</body>
</html>
"""


def _overlay_cut_row(item: dict[str, Any]) -> str:
    artifacts = item.get("generated_artifacts") or {}
    limitations = "<br>".join(escape(str(value)) for value in item.get("limitations") or [])
    artifact_text = _artifact_links_html(artifacts)
    sample_visual = _sample_frames_embed_html(
        sample_frames=artifacts.get("sample_frames"),
        sample_plan=item.get("sample_frame_plan"),
        alt_prefix=str(item.get("cut_id", "")),
    )
    main_visual = _visual_embed_html(
        frame=artifacts.get("frame"),
        video=artifacts.get("video"),
        alt=f"{item.get('cut_id', '')} subtitle-overlay proof frame",
    )
    visual = "<br>".join(chunk for chunk in [sample_visual, main_visual] if chunk)
    style_text = _style_cut_html(
        item.get("style_direction") or {},
        item.get("style_parameters") or {},
        item.get("line_width_readback") or {},
    )
    statuses = "<br>".join(
        [
            f"typography: {escape(str(item.get('typography_status', '')))}",
            f"safe-area: {escape(str(item.get('safe_area_status', '')))}",
            f"line-wrap: {escape(str(item.get('line_wrapping_status', '')))}",
            f"timing: {escape(str(item.get('timing_sync_status', '')))}",
        ]
    )
    return (
        "<tr>"
        f"<td>{escape(str(item.get('cut_id', '')))}</td>"
        f"<td>{escape(str(item.get('visual_proof_status', '')))}<br>overlay_present={escape(str(item.get('subtitle_overlay_present', '')))}</td>"
        f"<td>{visual}</td>"
        f"<td>{artifact_text}</td>"
        f"<td>{style_text}</td>"
        f"<td>{statuses}</td>"
        f"<td>{limitations}</td>"
        "</tr>"
    )


def _representative_report_html(report: dict[str, Any]) -> str:
    rows = "\n".join(
        _representative_cut_row(item) for item in report.get("per_cut_visual_assessment") or []
    )
    style_summary = _style_summary_html(
        report.get("diagnostic_style_direction") or {},
        report.get("diagnostic_style_parameters") or {},
    )
    related_visuals = _related_visuals_html(report.get("outputs") or {})
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Representative Visual Proof Report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; line-height: 1.5; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
    th {{ background: #f3f3f3; }}
    .warn {{ color: #8a4b00; }}
    .proof-frame {{ max-width: 360px; width: 100%; border: 1px solid #ccc; display: block; margin-bottom: 8px; }}
    .contact-sheet {{ max-width: 100%; border: 1px solid #ccc; display: block; margin: 8px 0 16px; }}
    video {{ max-width: 360px; width: 100%; display: block; margin-top: 8px; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; }}
    dt {{ font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Representative Visual Proof Report</h1>
  <p class="warn">Diagnostic only. Human review is still required. production_candidate=false, rights_status=pending.</p>
  <p>episode: {escape(str(report.get("episode_id", "")))}</p>
  <section>
    <h2>Diagnostic Style Direction</h2>
{style_summary}
  </section>
{related_visuals}
  <table>
    <tr><th>cut</th><th>visual proof</th><th>visual</th><th>artifacts</th><th>style readback</th><th>review status</th><th>limitations</th></tr>
    {rows}
  </table>
</body>
</html>
"""


def _representative_cut_row(item: dict[str, Any]) -> str:
    artifacts = [
        ("frame", item.get("visual_proof_artifact_path")),
        ("video", item.get("visual_proof_video_artifact_path")),
        ("previous_source_frame", item.get("previous_source_frame_artifact_path")),
    ]
    artifact_text = _artifact_links_html({label: value for label, value in artifacts if value})
    sample_visual = _sample_frames_embed_html(
        sample_frames=item.get("subtitle_overlay_sample_frames"),
        sample_plan=(item.get("subtitle_overlay_readback") or {}).get("sample_frame_plan"),
        alt_prefix=str(item.get("cut_id", "")),
    )
    main_visual = _visual_embed_html(
        frame=item.get("visual_proof_artifact_path"),
        video=item.get("visual_proof_video_artifact_path"),
        alt=f"{item.get('cut_id', '')} representative visual proof",
    )
    visual = "<br>".join(chunk for chunk in [sample_visual, main_visual] if chunk)
    style_text = _style_cut_html(
        item.get("style_direction") or {},
        item.get("style_parameters") or {},
        item.get("line_width_readback") or {},
    )
    limitations = "<br>".join(escape(str(value)) for value in item.get("proof_limitations") or [])
    statuses = "<br>".join(
        [
            f"typography: {escape(str(item.get('typography_status', '')))}",
            f"safe-area: {escape(str(item.get('safe_area_status', '')))}",
            f"line-wrap: {escape(str(item.get('line_wrapping_status', '')))}",
            f"timing: {escape(str(item.get('timing_sync_status', '')))}",
        ]
    )
    return (
        "<tr>"
        f"<td>{escape(str(item.get('cut_id', '')))}</td>"
        f"<td>{escape(str(item.get('visual_proof_status', '')))}</td>"
        f"<td>{visual}</td>"
        f"<td>{artifact_text}</td>"
        f"<td>{style_text}</td>"
        f"<td>{statuses}</td>"
        f"<td>{limitations}</td>"
        "</tr>"
    )


def _review_surface_html(review_surface: dict[str, Any]) -> str:
    if not review_surface:
        return ""
    return (
        "  <section>"
        "<h2>Review Surface Contract</h2>"
        f"<p>candidate_id: {escape(str(review_surface.get('candidate_id', '')))} / "
        f"contract_id: {escape(str(review_surface.get('contract_id', '')))}</p>"
        f"<p>sidecar_srt_reference_only: {escape(str(review_surface.get('sidecar_srt_reference_only', '')))} / "
        "production_subtitle_design_acceptance: "
        f"{escape(str(review_surface.get('production_subtitle_design_acceptance', '')))}</p>"
        f"<p>minimum_human_review_file: {escape(str(review_surface.get('minimum_human_review_file', '')))}</p>"
        "  </section>"
    )


def _style_summary_html(direction: dict[str, Any], parameters: dict[str, Any]) -> str:
    if not direction and not parameters:
        return "    <p>No diagnostic style direction is recorded for this report.</p>"
    font_size = parameters.get("font_size") or {}
    outline = parameters.get("outline") or {}
    margin_v = parameters.get("margin_v") or {}
    alignment = parameters.get("alignment") or {}
    wrapping = parameters.get("wrapping") or {}
    line_summary = parameters.get("line_width_watch_summary") or {}
    return (
        "    <dl>"
        f"<dt>preset</dt><dd>{escape(str(direction.get('preset_name', '')))}</dd>"
        f"<dt>intent</dt><dd>{escape(str(direction.get('target_viewing_context', '')))}; "
        f"{escape(str(direction.get('visual_weight', '')))}</dd>"
        f"<dt>long-line policy</dt><dd>{escape(str(direction.get('long_line_policy', '')))}</dd>"
        f"<dt>font size</dt><dd>{escape(str(font_size.get('value')))} "
        f"({escape(str(font_size.get('source', '')))}; {escape(str(font_size.get('readback', '')))})</dd>"
        f"<dt>outline</dt><dd>{escape(str(outline.get('value')))} "
        f"({escape(str(outline.get('source', '')))}; {escape(str(outline.get('readback', '')))})</dd>"
        f"<dt>margin_v</dt><dd>{escape(str(margin_v.get('value')))} "
        f"({escape(str(margin_v.get('source', '')))}; {escape(str(margin_v.get('readback', '')))})</dd>"
        f"<dt>alignment</dt><dd>{escape(str(alignment.get('value', '')))}</dd>"
        f"<dt>wrapping</dt><dd>{escape(str(wrapping.get('policy', '')))}; "
        f"watch_eaw={escape(str(wrapping.get('available_proxy_wrap_eaw', '')))}</dd>"
        f"<dt>line-width watch</dt><dd>subtitle_items_needing_wrap_watch="
        f"{escape(str(line_summary.get('subtitle_items_needing_wrap_watch', '')))}</dd>"
        "    </dl>"
    )


def _style_cut_html(
    direction: dict[str, Any],
    parameters: dict[str, Any],
    line_width: dict[str, Any],
) -> str:
    if not direction and not parameters and not line_width:
        return ""
    font_size = parameters.get("font_size") or {}
    outline = parameters.get("outline") or {}
    margin_v = parameters.get("margin_v") or {}
    alignment = parameters.get("alignment") or {}
    return "<br>".join(
        [
            f"preset: {escape(str(direction.get('preset_name', '')))}",
            f"style_slot: {escape(str(parameters.get('style_slot', '')))}",
            f"font_size: {escape(str(font_size.get('value')))} ({escape(str(font_size.get('source', '')))})",
            f"outline: {escape(str(outline.get('value')))} ({escape(str(outline.get('source', '')))})",
            f"margin_v: {escape(str(margin_v.get('value')))} ({escape(str(margin_v.get('source', '')))})",
            f"alignment: {escape(str(alignment.get('value', '')))}",
            f"max_raw_eaw: {escape(str(line_width.get('max_raw_line_eaw', '')))}",
            f"needs_wrap_watch: {escape(str(line_width.get('needs_wrap_count', '')))}",
        ]
    )


def _related_visuals_html(artifacts: dict[str, Any]) -> str:
    contact_sheet = artifacts.get("contact_sheet")
    representative_html = artifacts.get("representative_visual_proof_report_html") or artifacts.get("html")
    chunks: list[str] = []
    if contact_sheet:
        href = _artifact_href(contact_sheet)
        chunks.append(
            "  <section><h2>Contact Sheet</h2>"
            f"<a href=\"{href}\"><img class=\"contact-sheet\" src=\"{href}\" alt=\"visual proof contact sheet\"></a>"
            "</section>"
        )
    if representative_html:
        href = _artifact_href(representative_html)
        chunks.append(
            f"  <p>Representative report: <a href=\"{href}\">{escape(str(representative_html))}</a></p>"
        )
    return "\n".join(chunks)


def _visual_embed_html(*, frame: Any, video: Any, alt: str) -> str:
    chunks: list[str] = []
    if frame:
        href = _artifact_href(frame)
        chunks.append(
            f"<a href=\"{href}\"><img class=\"proof-frame\" src=\"{href}\" alt=\"{escape(alt)}\"></a>"
        )
    if video:
        href = _artifact_href(video)
        chunks.append(
            f"<a href=\"{href}\">video</a><video controls preload=\"metadata\" src=\"{href}\"></video>"
        )
    return "<br>".join(chunks)


def _sample_frames_embed_html(*, sample_frames: Any, sample_plan: Any, alt_prefix: str) -> str:
    if not isinstance(sample_frames, dict) or not sample_frames:
        return ""
    plan_by_label = {
        str(item.get("label")): item
        for item in (sample_plan or [])
        if isinstance(item, dict) and item.get("label")
    }
    cards: list[str] = []
    for label in SAMPLE_FRAME_LABELS:
        path = sample_frames.get(label)
        if not path:
            continue
        href = _artifact_href(path)
        plan = plan_by_label.get(label) or {}
        caption_parts = [label]
        if plan.get("frame_seconds") is not None:
            caption_parts.append(f"t={escape(str(plan.get('frame_seconds')))}s")
        if plan.get("subtitle_id"):
            caption_parts.append(escape(str(plan.get("subtitle_id"))))
        caption = " / ".join(caption_parts)
        cards.append(
            "<figure class=\"sample-card\">"
            f"<a href=\"{href}\"><img src=\"{href}\" alt=\"{escape(alt_prefix)} {escape(label)} subtitle-bearing sample frame\"></a>"
            f"<figcaption>{caption}</figcaption>"
            "</figure>"
        )
    if not cards:
        return ""
    return "<div class=\"sample-grid\">" + "".join(cards) + "</div>"


def _artifact_links_html(artifacts: dict[str, Any]) -> str:
    links: list[str] = []
    for key, value in artifacts.items():
        if not value:
            continue
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                if not child_value:
                    continue
                href = _artifact_href(child_value)
                label = f"{key}.{child_key}"
                links.append(f"{escape(str(label))}: <a href=\"{href}\">{escape(str(child_value))}</a>")
            continue
        href = _artifact_href(value)
        links.append(f"{escape(str(key))}: <a href=\"{href}\">{escape(str(value))}</a>")
    return "<br>".join(links)


def _artifact_href(value: Any) -> str:
    text = str(value).replace("\\", "/")
    if text.startswith(("http://", "https://")):
        return escape(text, quote=True)
    return escape(Path(text).name, quote=True)


def _resolve_existing_path(value: Any, *, base: Path) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    if path.is_absolute():
        return path
    return base / path


def _required_float(value: Any, field: str) -> float:
    number = _optional_float(value)
    if number is None:
        raise SubtitleOverlayVisualProofError(f"{field} must be numeric")
    return number


def _optional_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _single_or_mixed(values: list[str]) -> str | None:
    unique = _unique_strings(values)
    if not unique:
        return None
    if len(unique) == 1:
        return unique[0]
    return "mixed"


def _unique_strings(values) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value is None:
            continue
        text = str(value)
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def _srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    mins = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def _display_path(path: Path, base: Path) -> str:
    try:
        text = path.resolve().relative_to(base.resolve())
    except ValueError:
        text = path
    return str(text).replace("\\", "/")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
