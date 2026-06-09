"""Cut-scoped diagnostic subtitle-overlay visual proof.

This generator stays inside the existing OUT-01 diagnostic render boundary and
updates the R3 visual-proof readback consumed by ED-10d. It does not approve
production render, subtitle design, creative use, publishing, or rights.
"""

from __future__ import annotations

import copy
import json
import shutil
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
SUBTITLE_PRESENTATION_CONTRACT_ID = "jp_clip_dialogue_reference_v0"
LINE_WIDTH_WATCH_EAW = 40
PRESENTATION_WRAP_EAW = 28
RESPONSE_REFERRAL_SUBTITLE_IDS = {f"sub_{index:03d}" for index in range(25, 30)}
ASS_DIALOGUE_STYLE_NAME = "ClipPipeDialogueLeft"
ASS_SPEAKER_BADGE_STYLE_NAME = "ClipPipeSpeakerBadge"
DEFAULT_FRAME_WIDTH = 1920
DEFAULT_FRAME_HEIGHT = 1080
DEFAULT_PRESENTATION_MODE = "badge_left_dialogue"
SUPPORTED_PRESENTATION_MODES = ("badge_left_dialogue", "bottom_center_emphasis")
LAYOUT_RATIOS = {
    "font_size_to_frame_height": 0.115,
    "outline_to_font_size": 0.096,
    "shadow_to_font_size": 0.018,
    "horizontal_margin_to_frame_width": 0.055,
    "bottom_margin_to_frame_height": 0.09,
    "badge_width_to_font_size": 1.0,
    "badge_height_to_font_size": 0.7,
    "badge_font_size_to_font_size": 0.44,
    "badge_text_gap_to_font_size": 0.3,
    "line_height_to_font_size": 1.15,
    "first_line_optical_center_to_line_height": 0.52,
    "two_line_block_reserved_lines": 2,
    "bottom_center_font_size_to_frame_height": 0.125,
    "bottom_center_bottom_margin_to_frame_height": 0.085,
}
DIAGNOSTIC_ASS_STYLE = {
    "candidate_id": "jp_clip_dialogue_badge_left_v0",
    "font_name": "Yu Gothic",
    "primary_colour": "&H00FFFFFF",
    "secondary_colour": "&H00FFFFFF",
    "outline_colour": "&H00000000",
    "back_colour": "&H80000000",
    "border_style": 1,
    "speaker_badge_label": "SPK",
    "speaker_accent_colour": "&H0000D7FF",
    "speaker_badge_back_colour": "&H90202020",
}


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
    layout = _subtitle_layout_contract(
        frame_width=DEFAULT_FRAME_WIDTH,
        frame_height=DEFAULT_FRAME_HEIGHT,
        mode=DEFAULT_PRESENTATION_MODE,
        dimension_source="default_only_no_probe_performed",
    )
    if dry_run:
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            presentation_items=[],
            layout=layout,
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
            sample_frame_extracts=[],
            error=None,
            legacy_autoload_srt=None,
            previous_proof_artifacts=None,
            base=base,
        )

    if not renderable_items:
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            presentation_items=[],
            layout=layout,
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
            sample_frame_extracts=[],
            error="no renderable subtitle items for target cut",
            legacy_autoload_srt=None,
            previous_proof_artifacts=None,
            base=base,
        )

    cut_paths["output_dir"].mkdir(parents=True, exist_ok=True)
    cut_paths["reference_dir"].mkdir(parents=True, exist_ok=True)
    previous_proof_artifacts = _archive_existing_proof_artifacts(cut_paths)
    legacy_autoload_srt = _mitigate_legacy_autoload_srt(cut_paths)
    layout = _probed_subtitle_layout_contract(
        source_video_path=source_media["source_video"]["resolved_path"],
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    presentation_items = _presentation_items(renderable_items, layout=layout)
    _write_srt(cut_paths["sidecar_srt_reference"], renderable_items)
    _write_ass(cut_paths["burned_in_subtitle_file"], presentation_items, layout=layout)
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
            subtitle_file_path=cut_paths["burned_in_subtitle_file"],
            runner=runner,
        )
        video_path = Path(render_result.output_path)
        frame_extract = _extract_frame(
            video_path=video_path,
            frame_path=cut_paths["frame"],
            seconds=_representative_frame_seconds(presentation_items, duration),
            ffmpeg_path=render_result.ffmpeg_path,
            runner=runner,
        )
        sample_frame_extracts = _extract_sample_frames(
            video_path=video_path,
            cut_paths=cut_paths,
            sample_specs=_sample_frame_specs(presentation_items, duration),
            ffmpeg_path=render_result.ffmpeg_path,
            runner=runner,
        )
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            presentation_items=presentation_items,
            layout=layout,
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
            legacy_autoload_srt=legacy_autoload_srt,
            previous_proof_artifacts=previous_proof_artifacts,
            error=None,
            base=base,
        )
    except (OSError, ffmpeg_tiny.TinyRenderError) as exc:
        failure_reason = getattr(exc, "failure_reason", "subtitle_overlay_render_failed")
        return _cut_report(
            episode_id=episode_id,
            cut=cut,
            items=items,
            presentation_items=locals().get("presentation_items", []),
            layout=locals().get("layout", layout),
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
            sample_frame_extracts=[],
            legacy_autoload_srt=locals().get("legacy_autoload_srt"),
            previous_proof_artifacts=locals().get("previous_proof_artifacts"),
            error=f"{failure_reason}: {exc}",
            base=base,
        )


def _cut_report(
    *,
    episode_id: str,
    cut: dict[str, Any],
    items: list[dict[str, Any]],
    presentation_items: list[dict[str, Any]],
    layout: dict[str, Any],
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
    sample_frame_extracts: list[dict[str, Any]],
    error: str | None,
    legacy_autoload_srt: dict[str, Any] | None,
    previous_proof_artifacts: dict[str, Path] | None,
    base: Path,
) -> dict[str, Any]:
    cut_id = str(cut.get("id") or "")
    start_seconds = _required_float(cut.get("start_seconds"), f"{cut_id}.start_seconds")
    end_seconds = _required_float(cut.get("end_seconds"), f"{cut_id}.end_seconds")
    renderable_items = [
        item for item in items if item.get("status") in RENDERABLE_SUBTITLE_STATUSES
    ]
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
        "subtitle_presentation_contract": _subtitle_presentation_contract_readback(layout),
        "speaker_identity_presentation": _speaker_identity_presentation_readback(layout),
        "replacement_behavior": _replacement_behavior_readback(presentation_items),
        "renderer_path_audit": _renderer_path_audit_readback(),
        "sample_frame_selection": _sample_frame_selection_readback(sample_frame_extracts),
        "style_direction": _diagnostic_style_direction(),
        "style_parameters": _style_parameter_readback(items, layout=layout),
        "burned_in_subtitle_style": _burned_in_subtitle_style_readback(layout),
        "layout_contract": layout,
        "sidecar_srt_reference": _sidecar_srt_reference_readback(
            cut_paths=cut_paths,
            base=base,
            legacy_autoload_srt=legacy_autoload_srt,
        ),
        "previous_proof_artifacts": _previous_proof_artifacts_readback(
            previous_proof_artifacts or {},
            base=base,
        ),
        "review_warning": _review_warning_readback(),
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
        "subtitle_presentation_timing": {
            "items": presentation_items,
            "timing_source": "derived_from_renderable_subtitles_for_diagnostic_ASS_only",
            "source_transcript_or_official_subtitles_mutated": False,
        },
        "generated_artifacts": {
            "video": _display_path(cut_paths["video"], base),
            "frame": _display_path(cut_paths["frame"], base),
            "sample_frames": [
                {
                    **extract,
                    "path": _display_path(Path(str(extract.get("path") or "")), base),
                }
                for extract in sample_frame_extracts
            ],
            "diagnostic_subtitle_file": _display_path(
                cut_paths["burned_in_subtitle_file"], base
            ),
            "burned_in_subtitle_file": _display_path(
                cut_paths["burned_in_subtitle_file"], base
            ),
            "sidecar_srt_reference": _display_path(
                cut_paths["sidecar_srt_reference"], base
            ),
        },
        "artifact_exists": {
            "video": cut_paths["video"].exists(),
            "frame": cut_paths["frame"].exists(),
            "sample_frames": {
                str(extract.get("role") or extract.get("sample_id") or ""): Path(
                    str(extract.get("path") or "")
                ).exists()
                for extract in sample_frame_extracts
            },
            "diagnostic_subtitle_file": cut_paths["burned_in_subtitle_file"].exists(),
            "burned_in_subtitle_file": cut_paths["burned_in_subtitle_file"].exists(),
            "sidecar_srt_reference": cut_paths["sidecar_srt_reference"].exists(),
            "legacy_autoload_srt": cut_paths["legacy_autoload_srt"].exists(),
        },
        "output_metadata": output_metadata,
        "selected_render_profile": selected_profile,
        "fallback_used": fallback_used,
        "attempted_render_profiles": attempted_render_profiles,
        "attempts": attempts,
        "frame_extract": frame_extract or {},
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
            "diagnostic ASS style candidate is used for burned-in review subtitles; production typography polish is not claimed",
            "speaker face icon assets were not available in the current material ledger; the diagnostic candidate uses a speaker badge placeholder fallback",
            "sample frames are subtitle-bearing timing probes only and are not OCR verification",
            "sidecar SRT is reference-only and stored away from the video basename to avoid VLC auto-display confusion",
            "safe-area, line wrapping, readability, and timing sync still require human review",
            "overlay presence is inferred from successful subtitle filter/render and generated subtitle files, not OCR",
            "rights_status=pending; production/public usage is not allowed",
        ],
        "production_subtitle_design_acceptance": False,
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
        "subtitle_presentation_contract": _report_contract_summary(cut_reports),
        "speaker_identity_presentation": _report_speaker_identity_summary(cut_reports),
        "replacement_behavior": _report_replacement_behavior_summary(cut_reports),
        "renderer_path_audit": _renderer_path_audit_readback(),
        "sample_frame_selection": _report_sample_frame_selection_summary(cut_reports),
        "burned_in_subtitle_style": _report_burned_in_style_summary(cut_reports),
        "sidecar_srt_reference": _report_sidecar_srt_reference_summary(cut_reports),
        "review_warning": _review_warning_readback(),
        "cut_results": cut_reports,
        "aggregate_summary": {
            "target_cut_count": len(target_cut_ids),
            "subtitle_overlay_available_count": success_count,
            "failed_count": len(cut_reports) - success_count,
            "all_target_cuts_have_overlay": success_count == len(target_cut_ids),
        },
        "representative_visual_proof_report": _display_path(representative_report_path, base),
        "related_visual_artifacts": _related_visual_artifacts(representative_report),
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
            "Generated artifacts are local review artifacts and must not be staged from episodes/.",
            "Burned-in subtitles are inside the proof video; sidecar SRT files are reference-only and should not be enabled as a VLC subtitle track during embedded-subtitle review.",
        ],
    }


def _diagnostic_style_direction() -> dict[str, Any]:
    return {
        "preset_name": DIAGNOSTIC_STYLE_DIRECTION_NAME,
        "presentation_contract_id": SUBTITLE_PRESENTATION_CONTRACT_ID,
        "contract_status": "diagnostic_direction_readback",
        "target_viewing_context": "smartphone_readable_japanese_clip_subtitle",
        "visual_weight": "large_heavily_outlined_clip_dialogue_not_restrained_movie_subtitles",
        "preferred_non_pov_pattern": "face_icon_plus_left_aligned_subtitle",
        "implemented_pattern": "speaker_badge_placeholder_plus_left_aligned_subtitle",
        "supported_presentation_modes": list(SUPPORTED_PRESENTATION_MODES),
        "left_alignment_scope": (
            "conditional to badge_left_dialogue mode; not all subtitles are forced left"
        ),
        "reaction_caption_tolerance": "short_reaction_captions_may_carry_stronger_visual_weight",
        "long_line_policy": (
            "diagnostic ASS wraps dialogue text at the presentation contract proxy width; "
            "rendered pixel fit still requires human review"
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


def _probed_subtitle_layout_contract(
    *,
    source_video_path: Path,
    ffprobe_path: str | Path | None,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    probe = ffmpeg_tiny.probe_media(
        input_path=source_video_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    width = int(probe.metadata.get("width") or DEFAULT_FRAME_WIDTH)
    height = int(probe.metadata.get("height") or DEFAULT_FRAME_HEIGHT)
    return _subtitle_layout_contract(
        frame_width=width,
        frame_height=height,
        mode=DEFAULT_PRESENTATION_MODE,
        dimension_source="ffprobe_source_video",
    )


def _subtitle_layout_contract(
    *,
    frame_width: int,
    frame_height: int,
    mode: str,
    dimension_source: str,
) -> dict[str, Any]:
    if mode not in SUPPORTED_PRESENTATION_MODES:
        raise SubtitleOverlayVisualProofError(f"unsupported presentation mode: {mode}")
    width = max(1, int(frame_width))
    height = max(1, int(frame_height))
    if mode == "bottom_center_emphasis":
        font_size = _layout_round(height * LAYOUT_RATIOS["bottom_center_font_size_to_frame_height"])
    else:
        font_size = _layout_round(height * LAYOUT_RATIOS["font_size_to_frame_height"])
    outline = max(2, _layout_round(font_size * LAYOUT_RATIOS["outline_to_font_size"]))
    shadow = max(1, _layout_round(font_size * LAYOUT_RATIOS["shadow_to_font_size"]))
    margin_l = _layout_round(width * LAYOUT_RATIOS["horizontal_margin_to_frame_width"])
    margin_r = margin_l
    bottom_margin_ratio = (
        LAYOUT_RATIOS["bottom_center_bottom_margin_to_frame_height"]
        if mode == "bottom_center_emphasis"
        else LAYOUT_RATIOS["bottom_margin_to_frame_height"]
    )
    bottom_margin = _layout_round(height * bottom_margin_ratio)
    line_height = _layout_round(font_size * LAYOUT_RATIOS["line_height_to_font_size"])
    badge_width = _layout_round(font_size * LAYOUT_RATIOS["badge_width_to_font_size"])
    badge_height = _layout_round(font_size * LAYOUT_RATIOS["badge_height_to_font_size"])
    badge_font_size = _layout_round(font_size * LAYOUT_RATIOS["badge_font_size_to_font_size"])
    badge_text_gap = _layout_round(font_size * LAYOUT_RATIOS["badge_text_gap_to_font_size"])
    reserved_lines = int(LAYOUT_RATIOS["two_line_block_reserved_lines"])
    dialogue_x = margin_l + badge_width + badge_text_gap
    dialogue_y_for_two_line_block = max(
        0,
        height - bottom_margin - (line_height * reserved_lines),
    )
    first_line_center_offset = _layout_round(
        line_height * LAYOUT_RATIOS["first_line_optical_center_to_line_height"]
    )
    badge_center_x = margin_l + _layout_round(badge_width / 2)
    badge_center_y_for_two_line_block = dialogue_y_for_two_line_block + first_line_center_offset
    bottom_center_y = height - bottom_margin
    formulas = {
        "font_size": (
            f"round(frame_height * {LAYOUT_RATIOS['font_size_to_frame_height']})"
            if mode == "badge_left_dialogue"
            else f"round(frame_height * {LAYOUT_RATIOS['bottom_center_font_size_to_frame_height']})"
        ),
        "outline": f"max(2, round(font_size * {LAYOUT_RATIOS['outline_to_font_size']}))",
        "shadow": f"max(1, round(font_size * {LAYOUT_RATIOS['shadow_to_font_size']}))",
        "horizontal_margin": (
            f"round(frame_width * {LAYOUT_RATIOS['horizontal_margin_to_frame_width']})"
        ),
        "bottom_margin": f"round(frame_height * {bottom_margin_ratio})",
        "badge_width": f"round(font_size * {LAYOUT_RATIOS['badge_width_to_font_size']})",
        "badge_height": f"round(font_size * {LAYOUT_RATIOS['badge_height_to_font_size']})",
        "badge_font_size": (
            f"round(font_size * {LAYOUT_RATIOS['badge_font_size_to_font_size']})"
        ),
        "badge_text_gap": f"round(font_size * {LAYOUT_RATIOS['badge_text_gap_to_font_size']})",
        "line_height": f"round(font_size * {LAYOUT_RATIOS['line_height_to_font_size']})",
        "badge_vertical_alignment": (
            "badge_center_y = dialogue_y + "
            f"round(line_height * {LAYOUT_RATIOS['first_line_optical_center_to_line_height']})"
        ),
        "dialogue_y": (
            "frame_height - bottom_margin - line_height * wrapped_line_count"
        ),
    }
    return {
        "contract_id": SUBTITLE_PRESENTATION_CONTRACT_ID,
        "mode": mode,
        "supported_modes": list(SUPPORTED_PRESENTATION_MODES),
        "mode_policy": {
            "badge_left_dialogue": (
                "non-POV dialogue with speaker identity element when coherent for the cut"
            ),
            "bottom_center_emphasis": (
                "emphasis or generic subtitle moments where a speaker badge/left anchor is not appropriate"
            ),
        },
        "selected_mode_reason": (
            "cut_003 is still treated as coherent non-POV dialogue for this diagnostic proof"
        ),
        "left_alignment_scope": (
            "conditional: badge_left_dialogue mode only; bottom_center_emphasis is also supported"
        ),
        "frame": {
            "width": width,
            "height": height,
            "dimension_source": dimension_source,
        },
        "alignment": (
            "speaker_badge_left_aligned_dialogue"
            if mode == "badge_left_dialogue"
            else "bottom_center_emphasis"
        ),
        "badge_vertical_alignment_rule": (
            "Align badge center to the first subtitle line optical center; "
            "for multi-line text, move the text block upward but keep the badge on the first-line center."
        ),
        "formulas": formulas,
        "ratios": LAYOUT_RATIOS,
        "values": {
            "font_size": font_size,
            "outline": outline,
            "shadow": shadow,
            "margin_l": margin_l,
            "margin_r": margin_r,
            "bottom_margin": bottom_margin,
            "line_height": line_height,
            "badge_width": badge_width,
            "badge_height": badge_height,
            "badge_font_size": badge_font_size,
            "badge_text_gap": badge_text_gap,
            "badge_center_x": badge_center_x,
            "badge_center_y_for_two_line_block": badge_center_y_for_two_line_block,
            "dialogue_x": dialogue_x,
            "dialogue_y_for_two_line_block": dialogue_y_for_two_line_block,
            "bottom_center_x": _layout_round(width / 2),
            "bottom_center_y": bottom_center_y,
            "dialogue_wrap_eaw": PRESENTATION_WRAP_EAW,
        },
    }


def _item_layout(layout: dict[str, Any], *, wrapped_line_count: int) -> dict[str, int]:
    values = layout["values"]
    line_count = max(1, int(wrapped_line_count or 1))
    if layout["mode"] == "bottom_center_emphasis":
        return {
            "dialogue_x": values["bottom_center_x"],
            "dialogue_y": values["bottom_center_y"],
            "badge_center_x": values["bottom_center_x"],
            "badge_center_y": values["bottom_center_y"],
        }
    dialogue_y = max(
        0,
        layout["frame"]["height"] - values["bottom_margin"] - (values["line_height"] * line_count),
    )
    badge_center_y = dialogue_y + _layout_round(
        values["line_height"] * LAYOUT_RATIOS["first_line_optical_center_to_line_height"]
    )
    return {
        "dialogue_x": values["dialogue_x"],
        "dialogue_y": dialogue_y,
        "badge_center_x": values["badge_center_x"],
        "badge_center_y": badge_center_y,
    }


def _layout_round(value: float) -> int:
    return int(round(float(value)))


def _style_parameter_readback(
    items: list[dict[str, Any]],
    *,
    layout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    style_slots = _unique_strings(item.get("style_slot") for item in items)
    style = DIAGNOSTIC_ASS_STYLE
    layout = layout or _subtitle_layout_contract(
        frame_width=DEFAULT_FRAME_WIDTH,
        frame_height=DEFAULT_FRAME_HEIGHT,
        mode=DEFAULT_PRESENTATION_MODE,
        dimension_source="default_style_readback",
    )
    values = layout["values"]
    return {
        "renderer": "ffmpeg_subtitles_filter_ass",
        "style_slot": _single_or_mixed(style_slots) or "subtitle.default",
        "style_slots": style_slots or ["subtitle.default"],
        "style_candidate_id": style["candidate_id"],
        "presentation_mode": layout["mode"],
        "supported_presentation_modes": list(SUPPORTED_PRESENTATION_MODES),
        "layout_values": values,
        "layout_formulas": layout["formulas"],
        "left_alignment_scope": layout["left_alignment_scope"],
        "explicit_ass_style_file": True,
        "explicit_ass_force_style": False,
        "font_name": {
            "value": style["font_name"],
            "source": "explicit_diagnostic_ass_style_candidate",
            "readback": "ASS style file font name; actual glyph fallback remains renderer/font-provider dependent",
        },
        "font_size": {
            "value": values["font_size"],
            "unit": "ass_points",
            "source": "formula_from_frame_height",
            "readback": layout["formulas"]["font_size"],
        },
        "outline": {
            "value": values["outline"],
            "unit": "ass_outline_units",
            "source": "formula_from_font_size",
            "readback": layout["formulas"]["outline"],
        },
        "margin_v": {
            "value": values["bottom_margin"],
            "unit": "ass_pixels_or_script_units",
            "source": "formula_from_frame_height",
            "readback": layout["formulas"]["bottom_margin"],
        },
        "alignment": {
            "value": layout["alignment"],
            "source": "selected diagnostic presentation mode, not a universal subtitle rule",
        },
        "wrapping": {
            "policy": "wrap_dialogue_text_for_diagnostic_ass_candidate",
            "automatic_wrap_applied_by_overlay_generator": True,
            "available_proxy_wrap_eaw": values["dialogue_wrap_eaw"],
            "watch_width_eaw": LINE_WIDTH_WATCH_EAW,
            "watch_item": (
                "Rendered visual review is still required after formula-based "
                "diagnostic wrapping."
            ),
        },
        "positioning": {
            "dialogue_x": values["dialogue_x"],
            "dialogue_y_for_two_line_block": values["dialogue_y_for_two_line_block"],
            "speaker_badge_x": values["badge_center_x"],
            "speaker_badge_y_for_two_line_block": values["badge_center_y_for_two_line_block"],
            "badge_text_gap": values["badge_text_gap"],
            "badge_width": values["badge_width"],
            "badge_height": values["badge_height"],
            "line_height": values["line_height"],
            "play_res_x": layout["frame"]["width"],
            "play_res_y": layout["frame"]["height"],
            "badge_vertical_alignment_rule": layout["badge_vertical_alignment_rule"],
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
        "policy_status": "diagnostic_ass_wrap_applied_still_requires_rendered_visual_review",
        "watch_wrap_eaw": LINE_WIDTH_WATCH_EAW,
        "presentation_wrap_eaw": PRESENTATION_WRAP_EAW,
        "subtitle_count_measured": len(rows),
        "max_raw_line_eaw": max((row["raw_longest_line_eaw"] for row in rows), default=0),
        "needs_wrap_count": sum(1 for row in rows if row["would_wrap_at_watch_eaw"]),
        "items": rows,
        "known_limitation": (
            "This is a text-width proxy only; it does not prove rendered pixel width, "
            "kinsoku behavior, safe-area, or final layout."
        ),
    }


def _burned_in_subtitle_style_readback(layout: dict[str, Any]) -> dict[str, Any]:
    style = DIAGNOSTIC_ASS_STYLE
    values = layout["values"]
    return {
        "style_candidate_id": style["candidate_id"],
        "preset_name": DIAGNOSTIC_STYLE_DIRECTION_NAME,
        "presentation_mode": layout["mode"],
        "supported_presentation_modes": list(SUPPORTED_PRESENTATION_MODES),
        "renderer_input": "ASS style file consumed by FFmpeg subtitles filter",
        "comparison_baseline": "previous FFmpeg/libass SRT/default-centered proof looked too small and movie-subtitle-like for YouTube review",
        "intended_design_target": "reference-driven non-POV speaker badge plus large left-aligned Japanese clip dialogue subtitle",
        "font_name": style["font_name"],
        "font_size": values["font_size"],
        "outline": values["outline"],
        "shadow": values["shadow"],
        "margin_v": values["bottom_margin"],
        "horizontal_margin": values["margin_l"],
        "badge_size": {
            "width": values["badge_width"],
            "height": values["badge_height"],
            "font_size": values["badge_font_size"],
        },
        "badge_text_gap": values["badge_text_gap"],
        "line_height": values["line_height"],
        "alignment": layout["alignment"],
        "left_alignment_scope": layout["left_alignment_scope"],
        "badge_vertical_alignment_rule": layout["badge_vertical_alignment_rule"],
        "layout_formulas": layout["formulas"],
        "speaker_badge_label": style["speaker_badge_label"],
        "dialogue_wrap_eaw": values["dialogue_wrap_eaw"],
        "production_subtitle_design_acceptance": False,
        "human_review_required": True,
    }


def _report_burned_in_style_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    if cut_reports:
        return cut_reports[0].get("burned_in_subtitle_style") or {}
    return _burned_in_subtitle_style_readback(
        _subtitle_layout_contract(
            frame_width=DEFAULT_FRAME_WIDTH,
            frame_height=DEFAULT_FRAME_HEIGHT,
            mode=DEFAULT_PRESENTATION_MODE,
            dimension_source="default_report_summary",
        )
    )


def _review_warning_readback() -> dict[str, Any]:
    return {
        "vlc_sidecar_srt_auto_display": "can_confuse_review",
        "embedded_burned_in_subtitle": "review_the_subtitle_visible_inside_the_video_frame",
        "sidecar_srt_reference": "reference_text_only_do_not_enable_as_player_subtitle_track_when_judging_burned_in_style",
        "production_subtitle_design_acceptance": False,
    }


def _sidecar_srt_reference_readback(
    *,
    cut_paths: dict[str, Path],
    base: Path,
    legacy_autoload_srt: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "role": "reference_text_only_not_burned_in_subtitle_rendering",
        "path": _display_path(cut_paths["sidecar_srt_reference"], base),
        "autoload_prevention": (
            "stored_under_subtitle_overlay_reference_with_non_matching_video_basename"
        ),
        "vlc_warning": (
            "Do not enable this SRT as a player subtitle track when reviewing "
            "the embedded burned-in proof subtitle."
        ),
        "legacy_autoload_srt": legacy_autoload_srt
        or {
            "status": "not_checked_or_not_applicable",
            "path": _display_path(cut_paths["legacy_autoload_srt"], base),
        },
    }


def _report_sidecar_srt_reference_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "role": "reference_text_only_not_burned_in_subtitle_rendering",
        "autoload_prevention": (
            "reference SRT files are not stored beside the proof video with "
            "the same basename"
        ),
        "vlc_review_warning": (
            "disable player subtitle tracks when judging embedded burned-in "
            "subtitle style"
        ),
        "per_cut": {
            str(cut.get("cut_id")): cut.get("sidecar_srt_reference") or {}
            for cut in cut_reports
        },
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
    base_parameters = (
        (cut_reports[0].get("style_parameters") or {})
        if cut_reports
        else _style_parameter_readback([])
    )
    return {
        **base_parameters,
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


def _subtitle_presentation_contract_readback(layout: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": SUBTITLE_PRESENTATION_CONTRACT_ID,
        "contract_doc": "docs/SUBTITLE_PRESENTATION_CONTRACT.md",
        "dialogue_subtitle_style": "large_heavily_outlined_clip_dialogue",
        "selected_presentation_mode": layout["mode"],
        "supported_presentation_modes": list(SUPPORTED_PRESENTATION_MODES),
        "left_alignment_is_universal": False,
        "left_alignment_scope": layout["left_alignment_scope"],
        "layout_formulas": layout["formulas"],
        "layout_values": layout["values"],
        "frame": layout["frame"],
        "preferred_non_pov_speaker_identity": "face_icon_plus_left_aligned_subtitle",
        "implemented_diagnostic_pattern": "speaker_badge_placeholder_plus_left_aligned_subtitle",
        "alternative_mode": "bottom_center_emphasis",
        "future_explanatory_caption_style": "explicitly_deferred",
        "replacement_behavior_expectation": "previous_line_disappears_when_next_subtitle_appears",
        "multi_speaker_icon_stack": "deferred_advanced_pattern",
        "emotion_specific_font_switching": "deferred",
        "production_subtitle_design_acceptance": False,
        "production_render_acceptance": False,
        "creative_acceptance": False,
        "rights_approval": False,
        "publishing_or_public_use_permission": False,
    }


def _report_contract_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    if cut_reports:
        return cut_reports[0].get("subtitle_presentation_contract") or {}
    return _subtitle_presentation_contract_readback(
        _subtitle_layout_contract(
            frame_width=DEFAULT_FRAME_WIDTH,
            frame_height=DEFAULT_FRAME_HEIGHT,
            mode=DEFAULT_PRESENTATION_MODE,
            dimension_source="default_report_summary",
        )
    )


def _speaker_identity_presentation_readback(layout: dict[str, Any]) -> dict[str, Any]:
    values = layout["values"]
    return {
        "preferred_pattern": "face_icon_plus_left_aligned_subtitle",
        "implemented_pattern": "speaker_badge_placeholder_plus_left_aligned_subtitle",
        "presentation_mode": layout["mode"],
        "pattern_status": "approximated_with_fallback_speaker_badge_no_face_icon_assets",
        "real_face_icon_assets_available": False,
        "fallback_used": True,
        "fallback_kind": "speaker_badge_placeholder",
        "fallback_label": DIAGNOSTIC_ASS_STYLE["speaker_badge_label"],
        "fallback_badge_size": {
            "width": values["badge_width"],
            "height": values["badge_height"],
            "font_size": values["badge_font_size"],
            "formula": "badge_width=round(font_size*1.0), badge_height=round(font_size*0.7), badge_font_size=round(font_size*0.44)",
        },
        "badge_vertical_alignment_rule": layout["badge_vertical_alignment_rule"],
        "future_asset_slot": {
            "x": values["badge_center_x"],
            "y_for_two_line_block": values["badge_center_y_for_two_line_block"],
            "purpose": "future real speaker face icon can replace the badge without changing dialogue anchor",
        },
    }


def _report_speaker_identity_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    if cut_reports:
        return cut_reports[0].get("speaker_identity_presentation") or {}
    return _speaker_identity_presentation_readback(
        _subtitle_layout_contract(
            frame_width=DEFAULT_FRAME_WIDTH,
            frame_height=DEFAULT_FRAME_HEIGHT,
            mode=DEFAULT_PRESENTATION_MODE,
            dimension_source="default_report_summary",
        )
    )


def _replacement_behavior_readback(presentation_items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "mode": "replace_on_next_subtitle_start",
        "fixed_linger_extension": False,
        "presentation_item_count": len(presentation_items),
        "items_truncated_by_next_subtitle": sum(
            1 for item in presentation_items if item.get("replacement_applied") is True
        ),
        "source_transcript_or_official_subtitles_mutated": False,
        "items": [
            {
                "subtitle_id": item.get("subtitle_id"),
                "render_start_seconds": item.get("render_start_seconds"),
                "render_end_seconds": item.get("render_end_seconds"),
                "display_start_seconds": item.get("display_start_seconds"),
                "display_end_seconds": item.get("display_end_seconds"),
                "replacement_applied": item.get("replacement_applied"),
                "replacement_end_source": item.get("replacement_end_source"),
            }
            for item in presentation_items
        ],
    }


def _report_replacement_behavior_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    per_cut = {
        str(cut.get("cut_id")): cut.get("replacement_behavior") or {}
        for cut in cut_reports
    }
    return {
        "mode": "replace_on_next_subtitle_start",
        "fixed_linger_extension": False,
        "per_cut": per_cut,
        "source_transcript_or_official_subtitles_mutated": False,
    }


def _renderer_path_audit_readback() -> dict[str, Any]:
    return {
        "renderer": "ffmpeg_subtitles_filter_ass",
        "actual_renderer_path_configured": True,
        "actual_render_verified_by": "ffmpeg_success_and_subtitle_bearing_frame_extracts_not_ocr",
        "renderer_path_limitations_detected": False,
        "play_res_source": "formula_layout_frame_dimensions",
        "play_res_mismatch_detected": False,
        "old_candidate_insufficiency": {
            "renderer_path_limitations": False,
            "scaling_or_playres_mismatch": False,
            "insufficient_style_difference": True,
            "sample_selection_weakness": True,
            "reason": (
                "The previous candidate changed ASS parameters but kept a restrained "
                "movie-subtitle-like centered pattern and sampled only one cue, so it "
                "did not prove the reference-driven YouTube clip subtitle direction."
            ),
        },
    }


def _sample_frame_selection_readback(sample_frame_extracts: list[dict[str, Any]]) -> dict[str, Any]:
    roles = [str(item.get("role") or "") for item in sample_frame_extracts]
    subtitle_ids = [str(item.get("subtitle_id") or "") for item in sample_frame_extracts]
    return {
        "policy": "subtitle_bearing_active_cues_only",
        "roles": roles,
        "subtitle_ids": subtitle_ids,
        "includes_response_referral_block": any(
            subtitle_id in RESPONSE_REFERRAL_SUBTITLE_IDS for subtitle_id in subtitle_ids
        ),
        "sample_count": len(sample_frame_extracts),
        "ocr_verified": False,
        "human_visual_review_required": True,
    }


def _report_sample_frame_selection_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "policy": "subtitle_bearing_active_cues_only",
        "required_roles": ["early", "middle", "response_referral", "final"],
        "per_cut": {
            str(cut.get("cut_id")): cut.get("sample_frame_selection") or {}
            for cut in cut_reports
        },
    }


def _related_visual_artifacts(representative_report: dict[str, Any]) -> dict[str, Any]:
    outputs = representative_report.get("outputs") if isinstance(representative_report, dict) else {}
    contact_sheet = outputs.get("contact_sheet") if isinstance(outputs, dict) else None
    return {
        "representative_visual_proof_report_html": outputs.get("html") if isinstance(outputs, dict) else None,
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
    updated["subtitle_presentation_contract"] = overlay_report.get(
        "subtitle_presentation_contract"
    ) or {}
    updated["speaker_identity_presentation"] = overlay_report.get(
        "speaker_identity_presentation"
    ) or {}
    updated["replacement_behavior"] = overlay_report.get("replacement_behavior") or {}
    updated["renderer_path_audit"] = overlay_report.get("renderer_path_audit") or {}
    updated["sample_frame_selection"] = overlay_report.get("sample_frame_selection") or {}
    updated["burned_in_subtitle_style"] = overlay_report.get("burned_in_subtitle_style") or {}
    updated["sidecar_srt_reference"] = overlay_report.get("sidecar_srt_reference") or {}
    updated["review_warning"] = overlay_report.get("review_warning") or {}
    updated["subtitle_overlay_visual_proof"] = {
        "report": overlay_report["outputs"]["json"],
        "target_cuts": overlay_report["target_cuts"],
        "all_target_cuts_have_overlay": overlay_report["aggregate_summary"][
            "all_target_cuts_have_overlay"
        ],
        "style_direction": overlay_report["style_direction"],
        "style_parameters": overlay_report["style_parameters"],
        "subtitle_presentation_contract": overlay_report.get(
            "subtitle_presentation_contract"
        ) or {},
        "speaker_identity_presentation": overlay_report.get(
            "speaker_identity_presentation"
        ) or {},
        "replacement_behavior": overlay_report.get("replacement_behavior") or {},
        "renderer_path_audit": overlay_report.get("renderer_path_audit") or {},
        "sample_frame_selection": overlay_report.get("sample_frame_selection") or {},
        "burned_in_subtitle_style": overlay_report.get("burned_in_subtitle_style") or {},
        "sidecar_srt_reference": overlay_report.get("sidecar_srt_reference") or {},
        "review_warning": overlay_report.get("review_warning") or {},
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
        assessment["subtitle_presentation_contract"] = proof.get(
            "subtitle_presentation_contract"
        ) or {}
        assessment["speaker_identity_presentation"] = proof.get(
            "speaker_identity_presentation"
        ) or {}
        assessment["replacement_behavior"] = proof.get("replacement_behavior") or {}
        assessment["renderer_path_audit"] = proof.get("renderer_path_audit") or {}
        assessment["sample_frame_selection"] = proof.get("sample_frame_selection") or {}
        assessment["burned_in_subtitle_style"] = proof.get("burned_in_subtitle_style") or {}
        assessment["sidecar_srt_reference"] = proof.get("sidecar_srt_reference") or {}
        assessment["previous_proof_artifacts"] = proof.get("previous_proof_artifacts") or {}
        assessment["review_warning"] = proof.get("review_warning") or {}
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
            "subtitle_presentation_contract": proof.get(
                "subtitle_presentation_contract"
            ) or {},
            "speaker_identity_presentation": proof.get("speaker_identity_presentation") or {},
            "replacement_behavior": proof.get("replacement_behavior") or {},
            "renderer_path_audit": proof.get("renderer_path_audit") or {},
            "sample_frame_selection": proof.get("sample_frame_selection") or {},
            "burned_in_subtitle_style": proof.get("burned_in_subtitle_style") or {},
            "sidecar_srt_reference": proof.get("sidecar_srt_reference") or {},
            "previous_proof_artifacts": proof.get("previous_proof_artifacts") or {},
            "review_warning": proof.get("review_warning") or {},
            "line_width_readback": proof["line_width_readback"],
            "timing_window": proof["timing_window"],
            "subtitle_source": proof["subtitle_source"],
            "artifact_exists": proof["artifact_exists"],
            "sample_frames": (proof.get("generated_artifacts") or {}).get("sample_frames")
            or [],
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
            reference_dir = review_dir / "subtitle_overlay_reference"
            cuts[cut_id] = {
                "stem": stem,
                "output_dir": review_dir,
                "reference_dir": reference_dir,
                "video": review_dir / f"{stem}.mp4",
                "frame": review_dir / f"{stem}.png",
                "legacy_autoload_srt": review_dir / f"{stem}.srt",
                "burned_in_subtitle_file": reference_dir / f"{stem}.burned_in.ass",
                "sidecar_srt_reference": reference_dir / f"{stem}.reference.srt",
                "legacy_autoload_srt_archive": reference_dir / f"{stem}.legacy_autoload.srt",
                "previous_proof_video": reference_dir / f"{stem}.previous_style.mp4",
                "previous_proof_frame": reference_dir / f"{stem}.previous_style.png",
                "previous_autoload_srt": reference_dir / f"{stem}.previous_autoload.srt",
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


def _mitigate_legacy_autoload_srt(cut_paths: dict[str, Path]) -> dict[str, Any]:
    legacy_path = cut_paths["legacy_autoload_srt"]
    archive_path = cut_paths["legacy_autoload_srt_archive"]
    if not legacy_path.exists():
        return {
            "status": "not_present",
            "path": str(legacy_path).replace("\\", "/"),
            "autoload_risk_after_run": False,
        }
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    legacy_path.replace(archive_path)
    return {
        "status": "renamed_to_reference_directory",
        "path": str(legacy_path).replace("\\", "/"),
        "archived_as": str(archive_path).replace("\\", "/"),
        "autoload_risk_after_run": False,
    }


def _archive_existing_proof_artifacts(cut_paths: dict[str, Path]) -> dict[str, Path]:
    archived: dict[str, Path] = {}
    candidates = {
        "previous_proof_video": (cut_paths["video"], cut_paths["previous_proof_video"]),
        "previous_proof_frame": (cut_paths["frame"], cut_paths["previous_proof_frame"]),
        "previous_autoload_srt": (
            cut_paths["legacy_autoload_srt"],
            cut_paths["previous_autoload_srt"],
        ),
    }
    for key, (source, target) in candidates.items():
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        archived[key] = target
    return archived


def _previous_proof_artifacts_readback(
    artifacts: dict[str, Path],
    *,
    base: Path,
) -> dict[str, Any]:
    if not artifacts:
        return {
            "status": "not_available",
            "role": "previous proof artifacts were not present before this run",
        }
    return {
        "status": "archived_before_overwrite",
        "role": "previous diagnostic proof for visual comparison only",
        "not_acceptance": "previous proof is not production subtitle design acceptance",
        "artifacts": {
            key: _display_path(value, base)
            for key, value in artifacts.items()
        },
    }


def _presentation_items(
    items: list[dict[str, Any]],
    *,
    layout: dict[str, Any],
) -> list[dict[str, Any]]:
    renderable = [
        item
        for item in items
        if item.get("status") in RENDERABLE_SUBTITLE_STATUSES
    ]
    renderable.sort(
        key=lambda item: (
            float(item.get("render_start_seconds") or 0.0),
            float(item.get("render_end_seconds") or 0.0),
            str(item.get("subtitle_id") or ""),
        )
    )
    presentation: list[dict[str, Any]] = []
    for index, item in enumerate(renderable):
        start = float(item["render_start_seconds"])
        source_end = float(item["render_end_seconds"])
        next_start = (
            float(renderable[index + 1]["render_start_seconds"])
            if index + 1 < len(renderable)
            else None
        )
        display_end = source_end
        replacement_applied = False
        replacement_end_source = "source_subtitle_end"
        if next_start is not None and start < next_start < source_end:
            display_end = next_start
            replacement_applied = True
            replacement_end_source = "next_subtitle_start"
        if display_end <= start:
            display_end = min(source_end, start + 0.2)
            replacement_end_source = "minimum_visible_window"
        wrapped = measure_subtitle(
            str(item.get("text") or ""),
            wrap_eaw=layout["values"]["dialogue_wrap_eaw"],
        )
        item_layout = _item_layout(layout, wrapped_line_count=len(wrapped.lines))
        presentation.append(
            {
                **item,
                "display_start_seconds": round(start, 3),
                "display_end_seconds": round(display_end, 3),
                "replacement_applied": replacement_applied,
                "replacement_end_source": replacement_end_source,
                "wrapped_text": "\n".join(line.text for line in wrapped.lines),
                "wrapped_line_count": len(wrapped.lines),
                "max_wrapped_line_eaw": wrapped.longest_line_eaw,
                "presentation_mode": layout["mode"],
                "layout": item_layout,
            }
        )
    return presentation


def _write_ass(path: Path, items: list[dict[str, Any]], *, layout: dict[str, Any]) -> None:
    style = DIAGNOSTIC_ASS_STYLE
    values = layout["values"]
    dialogue_alignment = "2" if layout["mode"] == "bottom_center_emphasis" else "7"
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {layout['frame']['width']}",
        f"PlayResY: {layout['frame']['height']}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        (
            f"Style: {ASS_DIALOGUE_STYLE_NAME},{style['font_name']},{values['font_size']},"
            f"{style['primary_colour']},{style['secondary_colour']},"
            f"{style['outline_colour']},{style['back_colour']},"
            "0,0,0,0,100,100,0,0,"
            f"{style['border_style']},{values['outline']},{values['shadow']},"
            f"{dialogue_alignment},"
            f"{values['margin_l']},{values['margin_r']},"
            f"{values['bottom_margin']},1"
        ),
        (
            f"Style: {ASS_SPEAKER_BADGE_STYLE_NAME},{style['font_name']},"
            f"{values['badge_font_size']},"
            f"{style['primary_colour']},{style['secondary_colour']},"
            f"{style['speaker_accent_colour']},{style['speaker_badge_back_colour']},"
            "1,0,0,0,100,100,0,0,"
            "3,3,0,5,0,0,0,1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for item in items:
        start = _ass_time(float(item["display_start_seconds"]))
        end = _ass_time(float(item["display_end_seconds"]))
        badge = _ass_text(str(style["speaker_badge_label"]))
        text = _ass_text(str(item.get("wrapped_text") or item.get("text") or ""))
        item_layout = item.get("layout") or _item_layout(
            layout,
            wrapped_line_count=int(item.get("wrapped_line_count") or 1),
        )
        if layout["mode"] == "bottom_center_emphasis":
            dialogue_override = (
                f"{{\\an2\\pos({item_layout['dialogue_x']},{item_layout['dialogue_y']})}}"
            )
            lines.append(
                f"Dialogue: 0,{start},{end},{ASS_DIALOGUE_STYLE_NAME},,0,0,0,,"
                f"{dialogue_override}{text}"
            )
            continue
        badge_override = (
            f"{{\\an5\\pos({item_layout['badge_center_x']},{item_layout['badge_center_y']})}}"
        )
        dialogue_override = (
            f"{{\\an7\\pos({item_layout['dialogue_x']},{item_layout['dialogue_y']})}}"
        )
        lines.append(
            f"Dialogue: 0,{start},{end},{ASS_SPEAKER_BADGE_STYLE_NAME},,0,0,0,,"
            f"{badge_override}{badge}"
        )
        lines.append(
            f"Dialogue: 1,{start},{end},{ASS_DIALOGUE_STYLE_NAME},,0,0,0,,"
            f"{dialogue_override}{text}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ass_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\N")
    )


def _ass_time(seconds: float) -> str:
    total_cs = max(0, int(round(seconds * 100)))
    cs = total_cs % 100
    total_seconds = total_cs // 100
    sec = total_seconds % 60
    minutes_total = total_seconds // 60
    minute = minutes_total % 60
    hour = minutes_total // 60
    return f"{hour}:{minute:02d}:{sec:02d}.{cs:02d}"


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
    cut_paths: dict[str, Path],
    sample_specs: list[dict[str, Any]],
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> list[dict[str, Any]]:
    extracts: list[dict[str, Any]] = []
    for spec in sample_specs:
        role = str(spec["role"])
        frame_path = cut_paths["reference_dir"] / f"{cut_paths['stem']}.sample_{role}.png"
        extract = _extract_frame(
            video_path=video_path,
            frame_path=frame_path,
            seconds=float(spec["frame_seconds"]),
            ffmpeg_path=ffmpeg_path,
            runner=runner,
        )
        extracts.append(
            {
                **extract,
                "sample_id": spec["sample_id"],
                "role": role,
                "subtitle_id": spec.get("subtitle_id"),
                "frame_selection_reason": spec.get("frame_selection_reason"),
                "subtitle_bearing_expected": True,
            }
        )
    return extracts


def _sample_frame_specs(items: list[dict[str, Any]], duration: float) -> list[dict[str, Any]]:
    if not items:
        return []
    candidates: list[tuple[str, dict[str, Any], str]] = [
        ("early", items[0], "first active subtitle cue"),
        ("middle", items[len(items) // 2], "middle active subtitle cue"),
    ]
    response_item = next(
        (item for item in items if item.get("subtitle_id") in RESPONSE_REFERRAL_SUBTITLE_IDS),
        None,
    )
    if response_item is not None:
        candidates.append(
            (
                "response_referral",
                response_item,
                "first active cue inside required response/referral block sub_025..sub_029",
            )
        )
    else:
        candidates.append(
            (
                "response_referral",
                items[-1],
                "fallback final cue because response/referral block is not present for this cut",
            )
        )
    candidates.append(("final", items[-1], "final active subtitle cue"))

    specs: list[dict[str, Any]] = []
    for role, item, reason in candidates:
        specs.append(
            {
                "sample_id": f"{role}:{item.get('subtitle_id')}",
                "role": role,
                "subtitle_id": item.get("subtitle_id"),
                "frame_seconds": _subtitle_frame_seconds(item, duration),
                "display_start_seconds": item.get("display_start_seconds"),
                "display_end_seconds": item.get("display_end_seconds"),
                "frame_selection_reason": reason,
            }
        )
    return specs


def _representative_frame_seconds(items: list[dict[str, Any]], duration: float) -> float:
    renderable = [item for item in items if item.get("status") in RENDERABLE_SUBTITLE_STATUSES]
    if not renderable:
        return 0.0
    return _subtitle_frame_seconds(renderable[0], duration)


def _subtitle_frame_seconds(item: dict[str, Any], duration: float) -> float:
    start = (
        _optional_float(item.get("display_start_seconds"))
        if item.get("display_start_seconds") is not None
        else _optional_float(item.get("render_start_seconds"))
    ) or 0.0
    end = (
        _optional_float(item.get("display_end_seconds"))
        if item.get("display_end_seconds") is not None
        else _optional_float(item.get("render_end_seconds"))
    ) or min(duration, start + 0.5)
    window = max(0.0, end - start)
    if window <= 0.0:
        return max(0.0, min(duration, start))
    midpoint = start + min(max(window / 2, 0.08), 0.55)
    if midpoint >= end:
        midpoint = start + (window / 2)
    return max(0.0, min(duration, midpoint))


def _sample_frames_html(sample_frames: list[dict[str, Any]]) -> str:
    if not sample_frames:
        return ""
    chunks = ["<div class=\"sample-grid\">"]
    for sample in sample_frames:
        path = sample.get("path")
        if not path:
            continue
        href = _artifact_href(path)
        label = (
            f"{sample.get('role', '')} / {sample.get('subtitle_id', '')} / "
            f"{sample.get('frame_seconds', '')}s"
        )
        chunks.append(
            "<figure>"
            f"<a href=\"{href}\"><img class=\"proof-frame\" src=\"{href}\" alt=\"{escape(str(label))}\"></a>"
            f"<figcaption>{escape(str(label))}</figcaption>"
            "</figure>"
        )
    chunks.append("</div>")
    return "".join(chunks)


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
    review_warning = _review_warning_html(report.get("review_warning") or {})
    related_visuals = _related_visuals_html(report.get("related_visual_artifacts") or {})
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
    .sample-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; }}
    figure {{ margin: 0; }}
    figcaption {{ font-size: 12px; color: #444; }}
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
{review_warning}
  <section>
    <h2>Diagnostic Style Direction</h2>
{style_summary}
  </section>
{related_visuals}
  <table>
    <tr><th>cut</th><th>status</th><th>visual</th><th>subtitle-bearing samples</th><th>artifacts</th><th>style readback</th><th>review statuses</th><th>limitations</th></tr>
    {rows}
  </table>
</body>
</html>
"""


def _overlay_cut_row(item: dict[str, Any]) -> str:
    artifacts = item.get("generated_artifacts") or {}
    limitations = "<br>".join(escape(str(value)) for value in item.get("limitations") or [])
    previous = (item.get("previous_proof_artifacts") or {}).get("artifacts") or {}
    artifact_text = _artifact_links_html(
        {key: value for key, value in artifacts.items() if key != "sample_frames"}
    )
    if previous:
        artifact_text = (
            f"{artifact_text}<br><strong>previous proof for comparison</strong><br>"
            f"{_artifact_links_html(previous)}"
        )
    visual = _visual_embed_html(
        frame=artifacts.get("frame"),
        video=artifacts.get("video"),
        alt=f"{item.get('cut_id', '')} subtitle-overlay proof frame",
    )
    sample_visuals = _sample_frames_html(artifacts.get("sample_frames") or [])
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
        f"<td>{sample_visuals}</td>"
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
    review_warning = _review_warning_html(report.get("review_warning") or {})
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
    .sample-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; }}
    figure {{ margin: 0; }}
    figcaption {{ font-size: 12px; color: #444; }}
    video {{ max-width: 360px; width: 100%; display: block; margin-top: 8px; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; }}
    dt {{ font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Representative Visual Proof Report</h1>
  <p class="warn">Diagnostic only. Human review is still required. production_candidate=false, rights_status=pending.</p>
  <p>episode: {escape(str(report.get("episode_id", "")))}</p>
{review_warning}
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
    visual = _visual_embed_html(
        frame=item.get("visual_proof_artifact_path"),
        video=item.get("visual_proof_video_artifact_path"),
        alt=f"{item.get('cut_id', '')} representative visual proof",
    )
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


def _style_summary_html(direction: dict[str, Any], parameters: dict[str, Any]) -> str:
    if not direction and not parameters:
        return "    <p>No diagnostic style direction is recorded for this report.</p>"
    font_name = parameters.get("font_name") or {}
    font_size = parameters.get("font_size") or {}
    outline = parameters.get("outline") or {}
    margin_v = parameters.get("margin_v") or {}
    alignment = parameters.get("alignment") or {}
    wrapping = parameters.get("wrapping") or {}
    layout_values = parameters.get("layout_values") or {}
    layout_formulas = parameters.get("layout_formulas") or {}
    line_summary = parameters.get("line_width_watch_summary") or {}
    return (
        "    <dl>"
        f"<dt>preset</dt><dd>{escape(str(direction.get('preset_name', '')))}</dd>"
        f"<dt>contract</dt><dd>{escape(str(direction.get('presentation_contract_id', '')))}</dd>"
        f"<dt>renderer</dt><dd>{escape(str(parameters.get('renderer', '')))}</dd>"
        f"<dt>candidate_id</dt><dd>{escape(str(parameters.get('style_candidate_id', '')))}</dd>"
        f"<dt>mode</dt><dd>{escape(str(parameters.get('presentation_mode', '')))}</dd>"
        f"<dt>supported modes</dt><dd>{escape(', '.join(parameters.get('supported_presentation_modes') or []))}</dd>"
        f"<dt>left alignment</dt><dd>{escape(str(parameters.get('left_alignment_scope', '')))}</dd>"
        f"<dt>intent</dt><dd>{escape(str(direction.get('target_viewing_context', '')))}; "
        f"{escape(str(direction.get('visual_weight', '')))}</dd>"
        f"<dt>pattern</dt><dd>{escape(str(direction.get('implemented_pattern', '')))}</dd>"
        f"<dt>long-line policy</dt><dd>{escape(str(direction.get('long_line_policy', '')))}</dd>"
        f"<dt>font name</dt><dd>{escape(str(font_name.get('value', '')))} "
        f"({escape(str(font_name.get('source', '')))}; {escape(str(font_name.get('readback', '')))})</dd>"
        f"<dt>font size</dt><dd>{escape(str(font_size.get('value')))} "
        f"({escape(str(font_size.get('source', '')))}; {escape(str(font_size.get('readback', '')))})</dd>"
        f"<dt>outline</dt><dd>{escape(str(outline.get('value')))} "
        f"({escape(str(outline.get('source', '')))}; {escape(str(outline.get('readback', '')))})</dd>"
        f"<dt>margin_v</dt><dd>{escape(str(margin_v.get('value')))} "
        f"({escape(str(margin_v.get('source', '')))}; {escape(str(margin_v.get('readback', '')))})</dd>"
        f"<dt>alignment</dt><dd>{escape(str(alignment.get('value', '')))}</dd>"
        f"<dt>badge size</dt><dd>{escape(str(layout_values.get('badge_width', '')))}x"
        f"{escape(str(layout_values.get('badge_height', '')))}; font="
        f"{escape(str(layout_values.get('badge_font_size', '')))}</dd>"
        f"<dt>line height</dt><dd>{escape(str(layout_values.get('line_height', '')))}</dd>"
        f"<dt>badge alignment rule</dt><dd>{escape(str((parameters.get('positioning') or {}).get('badge_vertical_alignment_rule', '')))}</dd>"
        f"<dt>font formula</dt><dd>{escape(str(layout_formulas.get('font_size', '')))}</dd>"
        f"<dt>outline formula</dt><dd>{escape(str(layout_formulas.get('outline', '')))}</dd>"
        f"<dt>margin formula</dt><dd>{escape(str(layout_formulas.get('bottom_margin', '')))}</dd>"
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
    positioning = parameters.get("positioning") or {}
    return "<br>".join(
        [
            f"preset: {escape(str(direction.get('preset_name', '')))}",
            f"contract: {escape(str(direction.get('presentation_contract_id', '')))}",
            f"candidate_id: {escape(str(parameters.get('style_candidate_id', '')))}",
            f"mode: {escape(str(parameters.get('presentation_mode', '')))}",
            f"renderer: {escape(str(parameters.get('renderer', '')))}",
            f"style_slot: {escape(str(parameters.get('style_slot', '')))}",
            f"font_size: {escape(str(font_size.get('value')))} ({escape(str(font_size.get('source', '')))})",
            f"outline: {escape(str(outline.get('value')))} ({escape(str(outline.get('source', '')))})",
            f"margin_v: {escape(str(margin_v.get('value')))} ({escape(str(margin_v.get('source', '')))})",
            f"alignment: {escape(str(alignment.get('value', '')))}",
            f"dialogue_pos_two_line: {escape(str(positioning.get('dialogue_x', '')))}, {escape(str(positioning.get('dialogue_y_for_two_line_block', '')))}",
            f"badge_pos_two_line: {escape(str(positioning.get('speaker_badge_x', '')))}, {escape(str(positioning.get('speaker_badge_y_for_two_line_block', '')))}",
            f"badge_size: {escape(str(positioning.get('badge_width', '')))}x{escape(str(positioning.get('badge_height', '')))}",
            f"line_height: {escape(str(positioning.get('line_height', '')))}",
            f"max_raw_eaw: {escape(str(line_width.get('max_raw_line_eaw', '')))}",
            f"needs_wrap_watch: {escape(str(line_width.get('needs_wrap_count', '')))}",
        ]
    )


def _review_warning_html(warning: dict[str, Any]) -> str:
    if not warning:
        return ""
    return (
        "  <section class=\"warn\"><h2>Burned-in vs Sidecar SRT</h2>"
        "<p>The subtitle to review is the embedded burned-in subtitle visible "
        "inside the proof video frame. Sidecar SRT files are reference text "
        "only; disable player subtitle tracks in VLC when judging the burned-in "
        "subtitle style.</p>"
        "<dl>"
        f"<dt>VLC sidecar SRT</dt><dd>{escape(str(warning.get('vlc_sidecar_srt_auto_display', '')))}</dd>"
        f"<dt>embedded subtitle</dt><dd>{escape(str(warning.get('embedded_burned_in_subtitle', '')))}</dd>"
        f"<dt>sidecar SRT role</dt><dd>{escape(str(warning.get('sidecar_srt_reference', '')))}</dd>"
        f"<dt>production_subtitle_design_acceptance</dt><dd>{escape(str(warning.get('production_subtitle_design_acceptance', '')))}</dd>"
        f"<dt>production subtitle design acceptance</dt><dd>{escape(str(warning.get('production_subtitle_design_acceptance', '')))}</dd>"
        "</dl></section>"
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


def _artifact_links_html(artifacts: dict[str, Any]) -> str:
    links: list[str] = []
    for key, value in artifacts.items():
        if not value:
            continue
        href = _artifact_href(value)
        links.append(f"{escape(str(key))}: <a href=\"{href}\">{escape(str(value))}</a>")
    return "<br>".join(links)


def _artifact_href(value: Any) -> str:
    text = str(value).replace("\\", "/")
    if text.startswith(("http://", "https://")):
        return escape(text, quote=True)
    parts = [part for part in text.split("/") if part]
    if "subtitle_overlay_reference" in parts:
        index = parts.index("subtitle_overlay_reference")
        return escape("/".join(parts[index:]), quote=True)
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
