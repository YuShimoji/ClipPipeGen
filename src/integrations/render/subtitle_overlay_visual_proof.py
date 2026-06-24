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
from src.integrations.render import subtitle_style_spike
from src.pipeline.edit_pack import load_edit_pack, validate_edit_pack
from src.pipeline.material_ledger import load_ledger
from src.pipeline.text_measure import measure_subtitle

SCHEMA_VERSION = "v1"
REPORT_KIND = "subtitle_overlay_visual_proof_report"
DEFAULT_SUBTITLE_OVERLAY_PROOF_PROFILE = "default"
ED10P_KEIFONT_LEAD_REPRESENTATIVE_PROOF_PROFILE = (
    "ed10p_keifont_lead_representative_proof"
)
ED10R_KEIFONT_DENSE_STRESS_PROOF_PROFILE = "ed10r_keifont_dense_stress_proof"
ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE = (
    "ed10w_subtitle_presentation_review_pack"
)
ED10Y_CANDIDATE2_CARRY_FORWARD_PROFILE = "ed10y_candidate2_carry_forward"
ED10Z_TINY_RENDER_PATH_NEARER_PROBE_PROFILE = (
    "ed10z_tiny_render_path_nearer_probe"
)
SUBTITLE_OVERLAY_PROOF_PROFILES = (
    DEFAULT_SUBTITLE_OVERLAY_PROOF_PROFILE,
    ED10P_KEIFONT_LEAD_REPRESENTATIVE_PROOF_PROFILE,
    ED10R_KEIFONT_DENSE_STRESS_PROOF_PROFILE,
    ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE,
    ED10Y_CANDIDATE2_CARRY_FORWARD_PROFILE,
    ED10Z_TINY_RENDER_PATH_NEARER_PROBE_PROFILE,
)
ED10L_KEIFONT_CANDIDATE_ID = "ed10l_keifont_pop_dialogue_candidate"
ED10W_CANDIDATE0_BASELINE_ID = "ed10w_current_pass_reference"
ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID = "ed10w_lighter_outline_shadow_pressure"
ED10W_CANDIDATE2_BADGE_PRESSURE_ID = "ed10w_badge_label_pressure_adjustment"
ED10W_CANDIDATE3_BALANCED_ID = "ed10w_balanced_combined_low_risk"
DEFAULT_SOURCE_VIDEO_MATERIAL_ID = "src_video_jp_pilot01"
DEFAULT_SOURCE_AUDIO_MATERIAL_ID = "src_audio_jp_pilot01"
DEFAULT_REVIEW_DIR_NAME = "jp_pilot01r3_cut_review"
RENDERABLE_SUBTITLE_STATUSES = {"included", "clamped_to_render_window"}
DIAGNOSTIC_STYLE_DIRECTION_NAME = "jp_clip_readable_v1"
SUBTITLE_PRESENTATION_CONTRACT_ID = "jp_clip_dialogue_reference_v0"
LINE_WIDTH_WATCH_EAW = 40
PRESENTATION_WRAP_EAW = 28
FONT_BBOX_WRAP_AUTHORITY = "font_bbox_pixel_measurement_not_grid_cell_count"
FONT_BBOX_WRAP_SOURCE = "subtitle_style_spike._wrap_text_to_width"
RESPONSE_REFERRAL_SUBTITLE_IDS = {f"sub_{index:03d}" for index in range(25, 30)}
MAX_MULTILINE_WRAP_EVIDENCE_SAMPLES = 4
ASS_DIALOGUE_STYLE_NAME = "ClipPipeDialogueLeft"
ASS_SPEAKER_BADGE_STYLE_NAME = "ClipPipeSpeakerBadge"
ASS_REVIEW_LABEL_STYLE_NAME = "ClipPipeReviewLabel"
ED10W_REVIEWABLE_OUTLINE_REDUCTION_PX = 2
ED10W_REVIEWABLE_SHADOW_REDUCTION_PX = 1
ED10W_REVIEWABLE_BADGE_TEXT_ALPHA = 0x90
ED10W_REVIEWABLE_BADGE_BACKGROUND_ALPHA = 0xE0
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


def typography_decoration_candidate_ids() -> tuple[str, ...]:
    return tuple(
        candidate.candidate_id
        for candidate in subtitle_style_spike.TYPOGRAPHY_DECORATION_CANDIDATES
    )


def subtitle_overlay_proof_profiles() -> tuple[str, ...]:
    return SUBTITLE_OVERLAY_PROOF_PROFILES


def _is_candidate2_lead_probe_profile(profile: str | None) -> bool:
    return str(profile or "") in {
        ED10Y_CANDIDATE2_CARRY_FORWARD_PROFILE,
        ED10Z_TINY_RENDER_PATH_NEARER_PROBE_PROFILE,
    }


def _is_tiny_render_path_probe_profile(profile: str | None) -> bool:
    return str(profile or "") == ED10Z_TINY_RENDER_PATH_NEARER_PROBE_PROFILE


def _is_candidate2_lead_probe_state(state: str | None) -> bool:
    return str(state or "") in {
        "candidate2_carry_forward_ready",
        "tiny_render_path_nearer_probe_ready",
    }


class SubtitleOverlayVisualProofError(Exception):
    """Raised when the subtitle-overlay proof cannot be built safely."""


def _diagnostic_ass_style_for_candidate(
    candidate_id: str | None,
) -> dict[str, Any]:
    if not candidate_id:
        return {
            **DIAGNOSTIC_ASS_STYLE,
            "selection_source": "legacy_overlay_default",
            "typography_decoration_candidate_id": None,
            "ed10g_small_adjustment_selected": False,
            "ed10i_kirinuki_gothic_balance_candidate": False,
            "ed10j_kirinuki_font_audit_candidate": False,
            "display_name": "JP clip dialogue badge left v0",
            "decoration_note": "existing diagnostic ASS subtitle proof style",
            "body_weight_note": "legacy overlay default",
            "outline_balance_role": "legacy overlay default",
            "emoji_evaluation_scope": "not_evaluated",
            "requested_font_family": DIAGNOSTIC_ASS_STYLE["font_name"],
            "resolved_font_family": DIAGNOSTIC_ASS_STYLE["font_name"],
            "resolved_font_file": None,
            "font_file_status": "legacy_overlay_default_not_resolved",
            "font_paths": [],
            "stroke_ratio": LAYOUT_RATIOS["outline_to_font_size"],
            "shadow_offset_ratio": LAYOUT_RATIOS["shadow_to_font_size"],
            "text_fill": "#ffffff",
            "stroke_fill": "#000000",
            "shadow_fill": "#000000",
            "badge_fill": "#ffd700",
            "badge_outline": "#202020",
        }

    candidate = _typography_decoration_candidate(candidate_id)
    resolved_family, resolved_font_file, font_status = _resolve_candidate_font(candidate)
    return {
        "candidate_id": candidate.candidate_id,
        "font_name": resolved_family,
        "primary_colour": _ass_colour(candidate.text_fill),
        "secondary_colour": _ass_colour(candidate.text_fill),
        "outline_colour": _ass_colour(candidate.stroke_fill),
        "back_colour": _ass_colour(candidate.shadow_fill, alpha=0x80),
        "border_style": 1,
        "speaker_badge_label": "SPK",
        "speaker_accent_colour": _ass_colour(candidate.badge_fill),
        "speaker_badge_back_colour": _ass_colour(candidate.badge_outline, alpha=0x90),
        "selection_source": "typography_decoration_candidate",
        "typography_decoration_candidate_id": candidate.candidate_id,
        "ed10g_small_adjustment_selected": candidate.candidate_id
        == "noto_sans_jp_clean_outline",
        "ed10i_kirinuki_gothic_balance_candidate": candidate.candidate_id.startswith(
            "ed10i_"
        ),
        "ed10j_kirinuki_font_audit_candidate": candidate.candidate_id.startswith(
            "ed10j_"
        ),
        "display_name": candidate.display_name,
        "decoration_note": candidate.decoration_note,
        "body_weight_note": candidate.body_weight_note,
        "outline_balance_role": candidate.outline_balance_role,
        "emoji_evaluation_scope": candidate.emoji_evaluation_scope,
        "requested_font_family": candidate.fallback_family,
        "resolved_font_family": resolved_family,
        "resolved_font_file": resolved_font_file,
        "font_file_status": font_status,
        "font_paths": [str(path).replace("\\", "/") for path in candidate.font_paths],
        "stroke_ratio": candidate.stroke_ratio,
        "shadow_offset_ratio": candidate.shadow_offset_ratio,
        "text_fill": subtitle_style_spike._rgb_hex(candidate.text_fill),
        "stroke_fill": subtitle_style_spike._rgb_hex(candidate.stroke_fill),
        "shadow_fill": subtitle_style_spike._rgb_hex(candidate.shadow_fill),
        "badge_fill": subtitle_style_spike._rgb_hex(candidate.badge_fill),
        "badge_outline": subtitle_style_spike._rgb_hex(candidate.badge_outline),
    }


def _typography_decoration_candidate(
    candidate_id: str,
) -> subtitle_style_spike.TypographyDecorationCandidate:
    for candidate in subtitle_style_spike.TYPOGRAPHY_DECORATION_CANDIDATES:
        if candidate.candidate_id == candidate_id:
            return candidate
    known = ", ".join(typography_decoration_candidate_ids())
    raise SubtitleOverlayVisualProofError(
        f"unknown typography decoration candidate: {candidate_id}; known={known}"
    )


def _resolve_candidate_font(
    candidate: subtitle_style_spike.TypographyDecorationCandidate,
) -> tuple[str, str | None, str]:
    for index, path in enumerate(candidate.font_paths):
        if path.exists():
            family = candidate.fallback_family if index == 0 else _font_family_for_path(path)
            status = (
                "candidate_primary_font_file_found"
                if index == 0
                else "candidate_primary_missing_used_candidate_fallback_font_file"
            )
            return family, str(path), status

    family, font_file, status = subtitle_style_spike._select_font()
    if font_file:
        return (
            _font_family_for_path(Path(font_file)),
            font_file,
            f"candidate_font_paths_missing_used_global_fallback: {status}",
        )
    return (
        candidate.fallback_family,
        None,
        "candidate_font_paths_missing_renderer_font_provider_fallback",
    )


def _font_family_for_path(path: Path) -> str:
    name = path.name.lower()
    if "keifont" in name:
        return "Keifont"
    if "851chikara-yowaku" in name:
        return "851 Chikara Yowaku"
    if "mplus" in name or "m plus" in name:
        return "M+ FONTS"
    if "yasashisagothic" in name:
        return "Yasashisa Gothic"
    if "noto" in name and "jp" in name:
        return "Noto Sans JP"
    if "yugoth" in name:
        return "Yu Gothic"
    if "meiryo" in name:
        return "Meiryo"
    if "msgothic" in name or "ms gothic" in name:
        return "MS Gothic"
    return path.stem


def _ass_colour(value: tuple[int, int, int], *, alpha: int = 0) -> str:
    r, g, b = (max(0, min(255, int(component))) for component in value)
    alpha = max(0, min(255, int(alpha)))
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


def _layout_style(layout: dict[str, Any]) -> dict[str, Any]:
    style = layout.get("diagnostic_ass_style")
    if isinstance(style, dict):
        return style
    return _diagnostic_ass_style_for_candidate(None)


def _subtitle_overlay_proof_profile(
    *,
    proof_profile: str | None,
    target_cut_ids: tuple[str, ...],
    typography_decoration_candidate_id: str | None,
) -> dict[str, Any]:
    profile = proof_profile or DEFAULT_SUBTITLE_OVERLAY_PROOF_PROFILE
    if profile == DEFAULT_SUBTITLE_OVERLAY_PROOF_PROFILE:
        return {
            "proof_profile": DEFAULT_SUBTITLE_OVERLAY_PROOF_PROFILE,
            "artifact_id": None,
        }
    if profile == ED10P_KEIFONT_LEAD_REPRESENTATIVE_PROOF_PROFILE:
        if typography_decoration_candidate_id != ED10L_KEIFONT_CANDIDATE_ID:
            raise SubtitleOverlayVisualProofError(
                "ed10p_keifont_lead_representative_proof requires "
                f"--typography-decoration-candidate-id {ED10L_KEIFONT_CANDIDATE_ID}"
            )
        return {
            "proof_profile": ED10P_KEIFONT_LEAD_REPRESENTATIVE_PROOF_PROFILE,
            "artifact_id": "clip-ed10p-keifont-lead-representative-proof-001",
            "source_review_artifact_id": "clip-ed10o-multifont-focused-review-001",
            "source_proof_artifact_id": "clip-ed10n-keifont-overlay-proof-001",
            "source_comparison_artifact_id": "clip-ed10l-known-kirinuki-font-pack-001",
            "target_cuts": list(target_cut_ids),
            "current_lead_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
            "review_surface_direction": {
                "status": "accepted_as_review_direction_not_production_acceptance",
                "accepted_surface_artifact_id": "clip-ed10o-multifont-focused-review-001",
                "accepted_surface": "same-line multi-font focused matrix",
                "confidence": "high",
                "not_accepted": [
                    "final normal-dialogue baseline",
                    "production subtitle design",
                    "production render",
                    "creative acceptance",
                    "rights approval",
                    "publishing",
                    "public use",
                ],
            },
            "candidate_state": {
                "keifont_lead_confidence": "medium_high",
                "keifont_is_provisional_lead": True,
                "alternates_preserved": [
                    "ed10l_851_chikara_yowaku_dialogue_candidate",
                    "ed10l_yasashisa_gothic_goodfreefonts_candidate",
                ],
                "excluded_until_weight_style_pinned": [
                    "ed10l_m_plus_fonts_dialogue_candidate"
                ],
            },
            "focused_proof_review": {
                "status": "representative_keifont_lead_proof_ready",
                "target": "Keifont lead normal-dialogue representative proof",
                "input_mode": "freeform",
                "current_lead_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
                "target_cuts": list(target_cut_ids),
                "source_review_artifact_id": "clip-ed10o-multifont-focused-review-001",
                "source_review_surface": "ED-10o focused matrix accepted as easier to see",
                "ed10o_reference_report": (
                    "episodes/jp_pilot01_hololive_bancho_20260525/review/"
                    "jp_pilot01r3_cut_review/subtitle_multifont_focused_review/"
                    "subtitle_multifont_focused_review_report.html"
                ),
                "look_for": [
                    "whether Keifont works beyond the easy initial sample",
                    "whether body thickness and outline pressure are acceptable",
                    "whether dense/stress-like lines in the current representative proof remain readable",
                    "whether the focused proof page remains easy to judge",
                ],
                "completion_signal": (
                    "any concrete impression, concern, approval, or adjustment request"
                ),
            },
            "review_debt": [
                {
                    "debt_id": "cut_008_dense_stress_proof",
                    "status": "deferred_not_blocking_ed10p",
                    "reason": (
                        "cut_008 is the known dense/stress representative target, "
                        "but tracked/current decision state still treats it as "
                        "needs_adjustment before production-adjacent promotion."
                    ),
                    "next_action": (
                        "create a dedicated dense/stress proof after cut_008 "
                        "context/boundary handling is explicitly accepted or scoped"
                    ),
                }
            ],
            "production_candidate": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        }
    if profile == ED10R_KEIFONT_DENSE_STRESS_PROOF_PROFILE:
        if typography_decoration_candidate_id != ED10L_KEIFONT_CANDIDATE_ID:
            raise SubtitleOverlayVisualProofError(
                "ed10r_keifont_dense_stress_proof requires "
                f"--typography-decoration-candidate-id {ED10L_KEIFONT_CANDIDATE_ID}"
            )
        if tuple(target_cut_ids) != ("cut_008",):
            raise SubtitleOverlayVisualProofError(
                "ed10r_keifont_dense_stress_proof requires exactly "
                "--target-cut cut_008; do not replay cut_002/cut_003 general "
                "Keifont acceptance review"
            )
        return {
            "proof_profile": ED10R_KEIFONT_DENSE_STRESS_PROOF_PROFILE,
            "artifact_id": "clip-ed10r-keifont-dense-stress-proof-001",
            "source_review_artifact_id": "clip-ed10p-keifont-lead-representative-proof-001",
            "source_proof_artifact_id": "clip-ed10p-keifont-lead-representative-proof-001",
            "source_comparison_artifact_id": "clip-ed10o-multifont-focused-review-001",
            "target_cuts": list(target_cut_ids),
            "current_lead_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
            "review_surface_direction": {
                "status": "keifont_provisional_baseline_not_general_acceptance_replay",
                "accepted_surface_artifact_id": "clip-ed10o-multifont-focused-review-001",
                "accepted_surface": "same-line multi-font focused matrix",
                "consumed_review_history": [
                    "ED-10n Keifont proof judged clearly improved and video-usable",
                    "ED-10o focused review surface judged easier to see",
                    "ED-10q was a page-format regression fix, not font-quality review",
                ],
                "not_reopened": [
                    "cut_002 general Keifont acceptance",
                    "cut_003 general Keifont acceptance",
                ],
                "not_accepted": [
                    "production subtitle design",
                    "production render",
                    "creative acceptance",
                    "rights approval",
                    "publishing",
                    "public use",
                ],
            },
            "candidate_state": {
                "keifont_baseline_confidence": "provisional",
                "keifont_is_diagnostic_representative_normal_dialogue_provisional_baseline": True,
                "keifont_general_acceptance_reopened": False,
                "baseline_scope": "diagnostic_representative_normal_dialogue",
                "dense_stress_scope": "current_proof_target_only",
                "alternates_preserved": [
                    "ed10l_851_chikara_yowaku_dialogue_candidate",
                    "ed10l_yasashisa_gothic_goodfreefonts_candidate",
                ],
                "excluded_until_weight_style_pinned": [
                    "ed10l_m_plus_fonts_dialogue_candidate"
                ],
            },
            "review_memory": {
                "subject": "Keifont normal-dialogue subtitle direction",
                "prior_review_count": "2+",
                "accepted_scope": [
                    "diagnostic_representative_review",
                    "provisional_normal_dialogue_baseline",
                ],
                "not_accepted_scope": [
                    "production_subtitle_design",
                    "production_render",
                    "creative_acceptance",
                    "rights",
                    "publishing",
                    "public_use",
                ],
                "next_nonredundant_axis": "dense_stress",
                "repeated_general_review": False,
                "review_reset_trigger_active": ["new_dense_stress_sample"],
                "current_blocker": "font_evidence_fallback",
            },
            "focused_proof_review": {
                "status": "dense_stress_keifont_proof_ready",
                "target": (
                    "cut_008 dense/stress diagnostic proof using Keifont as the "
                    "normal-dialogue provisional baseline"
                ),
                "input_mode": "dense_stress_diagnostic_review",
                "current_lead_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
                "target_cuts": list(target_cut_ids),
                "source_review_artifact_id": "clip-ed10p-keifont-lead-representative-proof-001",
                "source_review_surface": (
                    "ED-10n/ED-10o Keifont review history consumed; ED-10q page "
                    "regression fix is not treated as font-quality feedback"
                ),
                "ed10o_reference_report": (
                    "episodes/jp_pilot01_hololive_bancho_20260525/review/"
                    "jp_pilot01r3_cut_review/subtitle_multifont_focused_review/"
                    "subtitle_multifont_focused_review_report.html"
                ),
                "look_for": [
                    "cut_008 dense subtitle wrapping and safe-area behavior",
                    "rapid cue replacement readability under Keifont",
                    "outline, shadow, and badge pressure only as bounded adjustment candidates",
                    "whether any dense/stress issue blocks moving from proof debt into a bounded adjustment slice",
                    "do not re-decide general Keifont acceptance from cut_002/cut_003",
                ],
                "completion_signal": (
                    "dense/stress pass, concrete dense/stress concern, or a bounded "
                    "adjustment request for outline/shadow/badge handling"
                ),
            },
            "review_debt": [
                {
                    "debt_id": "cut_008_dense_stress_proof",
                    "status": "current_target",
                    "reason": (
                        "Keifont normal-dialogue review history is already consumed; "
                        "the remaining review debt is dense/stress behavior."
                    ),
                    "next_action": (
                        "review cut_008 only for dense/stress readability, "
                        "wrapping, timing replacement, and bounded style "
                        "adjustment needs"
                    ),
                }
            ],
            "production_candidate": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        }
    if profile == ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE:
        if typography_decoration_candidate_id != ED10L_KEIFONT_CANDIDATE_ID:
            raise SubtitleOverlayVisualProofError(
                "ed10w_subtitle_presentation_review_pack requires "
                f"--typography-decoration-candidate-id {ED10L_KEIFONT_CANDIDATE_ID}"
            )
        if tuple(target_cut_ids) != ("cut_008",):
            raise SubtitleOverlayVisualProofError(
                "ed10w_subtitle_presentation_review_pack requires exactly "
                "--target-cut cut_008; do not replay cut_002/cut_003 general "
                "Keifont acceptance review"
            )
        return {
            "proof_profile": ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE,
            "artifact_id": "clip-ed10w-subtitle-presentation-review-pack-001",
            "source_review_artifact_id": "clip-ed10r-keifont-dense-stress-proof-001",
            "source_proof_artifact_id": "clip-ed10r-keifont-dense-stress-proof-001",
            "source_comparison_artifact_id": "clip-ed10o-multifont-focused-review-001",
            "target_cuts": list(target_cut_ids),
            "current_lead_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
            "review_surface_direction": {
                "status": "new_axis_after_ed10v_pass",
                "accepted_surface_artifact_id": "clip-ed10r-keifont-dense-stress-proof-001",
                "accepted_surface": "ED-10u corrected cut_008 multiline evidence consumed as ED-10v pass",
                "not_reopened": [
                    "cut_002 general Keifont acceptance",
                    "cut_003 general Keifont acceptance",
                    "same cut_008 dense/multiline pass",
                ],
                "not_accepted": [
                    "production subtitle design",
                    "production render",
                    "creative acceptance",
                    "rights approval",
                    "publishing",
                    "public use",
                ],
            },
            "candidate_state": {
                "keifont_is_diagnostic_representative_normal_dialogue_provisional_baseline": True,
                "ed10v_dense_stress_pass_consumed": True,
                "ed10w_axis": "bounded_decoration_adjustment + render_path_readiness",
                "font_family_changed": False,
                "broad_style_gallery": False,
            },
            "review_memory": {
                "subject": "Keifont subtitle direction",
                "prior_review_count": "3+",
                "accepted_scope": [
                    "diagnostic_representative_review",
                    "provisional_normal_dialogue_baseline",
                    "diagnostic_dense_stress_pass",
                    "diagnostic_multiline_wrap_pass",
                ],
                "not_accepted_scope": [
                    "production_subtitle_design",
                    "production_render",
                    "creative_acceptance",
                    "rights",
                    "publishing",
                    "public_use",
                ],
                "next_nonredundant_axis": [
                    "bounded_decoration_adjustment",
                    "render_path_probe",
                    "future_shared_subtitle_layout_policy",
                ],
                "repeated_general_review": False,
                "repeated_cut_008_review_allowed": False,
                "current_blocker": "none_for_ed10w_review_pack",
            },
            "focused_proof_review": {
                "status": "subtitle_presentation_review_pack_ready",
                "target": "one-pass subtitle presentation review pack",
                "input_mode": "freeform",
                "current_lead_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
                "target_cuts": list(target_cut_ids),
                "source_review_artifact_id": "clip-ed10r-keifont-dense-stress-proof-001",
                "source_review_surface": "ED-10v consumed Keifont dense/stress multiline proof as pass",
                "ed10o_reference_report": (
                    "episodes/jp_pilot01_hololive_bancho_20260525/review/"
                    "jp_pilot01r3_cut_review/subtitle_multifont_focused_review/"
                    "subtitle_multifont_focused_review_report.html"
                ),
                "look_for": [
                    "whether to keep current passed baseline decoration",
                    "whether a lighter outline/shadow pressure candidate is preferred",
                    "whether SPK badge/label pressure should be reduced",
                    "whether the render-path decision card is enough to start the next tiny diagnostic probe",
                    "do not re-accept Keifont, cut_002/cut_003, or the same cut_008 dense/multiline pass",
                ],
                "completion_signal": (
                    "user chooses pass, a bounded adjustment candidate, a "
                    "render-path next route, or names a concern"
                ),
            },
            "review_debt": [
                {
                    "debt_id": "render_path_readiness_probe",
                    "status": "decision_card_included",
                    "reason": (
                        "ED-10w keeps render-path work to a tiny diagnostic "
                        "decision surface instead of expanding into production render."
                    ),
                    "next_action": (
                        "choose whether the next slice should run a final-path-nearer "
                        "diagnostic probe; do not claim production render acceptance"
                    ),
                }
            ],
            "production_candidate": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        }
    if _is_candidate2_lead_probe_profile(profile):
        if typography_decoration_candidate_id != ED10L_KEIFONT_CANDIDATE_ID:
            raise SubtitleOverlayVisualProofError(
                f"{profile} requires "
                f"--typography-decoration-candidate-id {ED10L_KEIFONT_CANDIDATE_ID}"
            )
        if tuple(target_cut_ids) != ("cut_008",):
            raise SubtitleOverlayVisualProofError(
                f"{profile} requires exactly "
                "--target-cut cut_008; do not replay cut_002/cut_003 general "
                "Keifont acceptance review"
            )
        is_ed10z = profile == ED10Z_TINY_RENDER_PATH_NEARER_PROBE_PROFILE
        artifact_id = (
            "clip-ed10z-tiny-render-path-nearer-probe-001"
            if is_ed10z
            else "clip-ed10y-candidate2-carry-forward-001"
        )
        source_review_artifact_id = (
            "clip-ed10y-candidate2-carry-forward-001"
            if is_ed10z
            else "clip-ed10w-subtitle-presentation-review-pack-001"
        )
        axis = (
            "tiny_render_path_nearer_probe"
            if is_ed10z
            else "candidate2_carry_forward + render_path_nearer_probe"
        )
        focused_status = (
            "tiny_render_path_nearer_probe_completed"
            if is_ed10z
            else "candidate2_carry_forward_ready"
        )
        current_blocker = (
            "none_for_tiny_render_path_nearer_probe"
            if is_ed10z
            else "none_for_candidate2_carry_forward"
        )
        return {
            "proof_profile": profile,
            "artifact_id": artifact_id,
            "source_review_artifact_id": source_review_artifact_id,
            "source_previous_artifact_id": "clip-ed10y-candidate2-carry-forward-001",
            "source_proof_artifact_id": "clip-ed10r-keifont-dense-stress-proof-001",
            "source_comparison_artifact_id": "clip-ed10o-multifont-focused-review-001",
            "target_cuts": list(target_cut_ids),
            "current_lead_candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
            "fallback_reference_candidate_id": ED10W_CANDIDATE0_BASELINE_ID,
            "held_reference_candidate_ids": [
                ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID,
                ED10W_CANDIDATE3_BALANCED_ID,
            ],
            "selected_typography_base": ED10L_KEIFONT_CANDIDATE_ID,
            "review_surface_direction": {
                "status": (
                    "candidate2_tiny_render_path_nearer_probe_completed"
                    if is_ed10z
                    else "latest_review_consumed_candidate2_carry_forward"
                ),
                "accepted_surface_artifact_id": source_review_artifact_id,
                "accepted_surface": (
                    "ED-10y Candidate 2 carry-forward source state; Candidate "
                    "2 is the bounded-decoration lead and Candidate 0 is "
                    "fallback."
                    if is_ed10z
                    else "ED-10w/ED-10x crop-first pack reviewed; Candidate 2 is "
                    "the bounded-decoration lead and Candidate 0 is fallback."
                ),
                "not_reopened": [
                    "Candidate 0-3 comparison review",
                    "cut_002 general Keifont acceptance",
                    "cut_003 general Keifont acceptance",
                    "same cut_008 dense/multiline pass",
                ],
                "not_accepted": [
                    "production subtitle design",
                    "production render",
                    "creative acceptance",
                    "rights approval",
                    "publishing",
                    "public use",
                ],
            },
            "candidate_state": {
                "keifont_is_diagnostic_representative_normal_dialogue_provisional_baseline": True,
                "ed10v_dense_stress_pass_consumed": True,
                "ed10w_review_consumed": True,
                "ed10y_review_consumed": True,
                "ed10z_probe_axis": axis,
                "lead_bounded_decoration_candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
                "lead_candidate_label": "Candidate 2 / SPK badge / label pressure adjustment",
                "fallback_reference_candidate_id": ED10W_CANDIDATE0_BASELINE_ID,
                "fallback_reference_label": "Candidate 0 / current passed baseline",
                "held_reference_candidate_ids": [
                    ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID,
                    ED10W_CANDIDATE3_BALANCED_ID,
                ],
                "held_reference_reason": (
                    "latest review says Candidate 1 and Candidate 3 read too "
                    "thin compared with Candidate 0 and Candidate 2"
                ),
                "font_family_changed": False,
                "broad_style_gallery": False,
                "same_candidate_comparison_review_allowed": False,
                "user_review_required_now": False,
            },
            "review_memory": {
                "subject": "ED-10w bounded subtitle presentation candidates",
                "latest_freeform_review_consumed": True,
                "latest_freeform_review_summary": (
                    "Candidate 0 and Candidate 2 are acceptable/good; "
                    "Candidate 1 and Candidate 3 look too thin; full-frame "
                    "context was still somewhat small."
                ),
                "lead_candidate": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
                "fallback_reference": ED10W_CANDIDATE0_BASELINE_ID,
                "held_references": [
                    {
                        "candidate_id": ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID,
                        "reason": "too_thin_compared_with_0_and_2",
                    },
                    {
                        "candidate_id": ED10W_CANDIDATE3_BALANCED_ID,
                        "reason": "too_thin_compared_with_0_and_2",
                    },
                ],
                "accepted_scope": [
                    "diagnostic_representative_review",
                    "provisional_normal_dialogue_baseline",
                    "diagnostic_dense_stress_pass",
                    "diagnostic_multiline_wrap_pass",
                    "candidate2_bounded_badge_pressure_adjustment_lead",
                    "tiny_render_path_nearer_probe_readback",
                ],
                "not_accepted_scope": [
                    "production_subtitle_design",
                    "production_render",
                    "creative_acceptance",
                    "rights",
                    "publishing",
                    "public_use",
                ],
                "next_nonredundant_axis": [
                    "production_limitation_lift",
                    "final_render_path_probe",
                    "future_shared_subtitle_layout_policy",
                ],
                "repeated_general_review": False,
                "repeated_cut_008_review_allowed": False,
                "same_candidate_comparison_review_allowed": False,
                "current_blocker": current_blocker,
            },
            "focused_proof_review": {
                "status": focused_status,
                "target": (
                    "Candidate 2 tiny render-path-nearer diagnostic probe"
                    if is_ed10z
                    else "Candidate 2 lead carry-forward proof surface"
                ),
                "input_mode": "none_latest_review_already_consumed",
                "current_lead_candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
                "fallback_reference_candidate_id": ED10W_CANDIDATE0_BASELINE_ID,
                "target_cuts": list(target_cut_ids),
                "source_review_artifact_id": source_review_artifact_id,
                "source_review_surface": (
                    "ED-10y Candidate 2 carry-forward consumed the latest user "
                    "freeform review and is now the source state"
                    if is_ed10z
                    else "ED-10w/ED-10x crop-first candidate pack consumed by "
                    "latest user freeform review"
                ),
                "look_for": [
                    "Candidate 2 is passed through the current FFmpeg/libass diagnostic path",
                    "Candidate 0 remains fallback/reference only",
                    "Candidate 1 and Candidate 3 remain held because they read too thin",
                    "do not ask for another Candidate 0-3 comparison review",
                ],
                "completion_signal": (
                    "tracked state records Candidate 2 tiny render-path-nearer "
                    "probe readback without production acceptance"
                ),
            },
            "review_debt": [
                {
                    "debt_id": (
                        "production_limitation_lift"
                        if is_ed10z
                        else "render_path_nearer_probe"
                    ),
                    "status": (
                        "not_started_after_tiny_probe"
                        if is_ed10z
                        else "candidate2_tiny_diagnostic_probe_included"
                    ),
                    "reason": (
                        "Candidate 2 is rendered through the current FFmpeg/libass "
                        "diagnostic path as a tiny path-nearer probe."
                    ),
                    "next_action": (
                        "start a separate limitation-lift/final render-path route "
                        "only after explicit acceptance scope is opened"
                        if is_ed10z
                        else "use the Candidate 2 probe readback as diagnostic evidence "
                        "only; production render acceptance remains separate"
                    ),
                }
            ],
            "production_candidate": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        }

    if profile not in SUBTITLE_OVERLAY_PROOF_PROFILES:
        known = ", ".join(SUBTITLE_OVERLAY_PROOF_PROFILES)
        raise SubtitleOverlayVisualProofError(
            f"unknown subtitle overlay proof profile: {profile}; known={known}"
        )
    raise SubtitleOverlayVisualProofError(f"unhandled subtitle overlay proof profile: {profile}")


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
    typography_decoration_candidate_id: str | None = None,
    proof_profile: str | None = None,
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

    diagnostic_ass_style = _diagnostic_ass_style_for_candidate(
        typography_decoration_candidate_id
    )
    proof_profile_data = _subtitle_overlay_proof_profile(
        proof_profile=proof_profile,
        target_cut_ids=target_cut_ids,
        typography_decoration_candidate_id=typography_decoration_candidate_id,
    )
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
                diagnostic_ass_style=diagnostic_ass_style,
                proof_profile_id=str(proof_profile_data.get("proof_profile") or ""),
                dry_run=dry_run,
                base=base,
                runner=runner,
            )
        )

    report_path = review_dir / "subtitle_overlay_visual_proof_report.json"
    report_html_path = review_dir / "subtitle_overlay_visual_proof_report.html"
    focused_review_html_path = review_dir / "current_proof_focused_review.html"
    presentation_review_pack_path = review_dir / "subtitle_presentation_review_pack.json"
    presentation_review_pack_html_path = review_dir / "subtitle_presentation_review_pack.html"
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
        focused_review_html_path=focused_review_html_path,
        base=base,
        dry_run=dry_run,
        diagnostic_ass_style=diagnostic_ass_style,
        proof_profile=proof_profile_data,
    )

    updated_representative = _updated_representative_report(
        representative_report=representative_report,
        overlay_report=report,
        cut_reports=cut_reports,
        base=base,
        proof_profile=proof_profile_data,
    )
    visual_proof_status = _aggregate_visual_proof_status(
        updated_representative.get("per_cut_visual_assessment") or [],
        target_cut_ids=target_cut_ids,
    )
    if (
        report.get("font_visual_evidence", {}).get(
            "valid_requested_font_visual_evidence"
        )
        is False
    ):
        visual_proof_status = "blocked_invalid_requested_font_visual_evidence"
        report["review_card_status"] = "withheld_font_visual_evidence_invalid"
        updated_representative[
            "review_card_status"
        ] = "withheld_font_visual_evidence_invalid"
    elif (
        proof_profile_data.get("proof_profile")
        == ED10R_KEIFONT_DENSE_STRESS_PROOF_PROFILE
        and (report.get("multiline_wrap_evidence") or {}).get("status")
        != "multiline_wrap_evidence_surfaced"
    ):
        visual_proof_status = "blocked_missing_multiline_wrap_evidence"
        report["review_card_status"] = "withheld_multiline_wrap_evidence_missing"
        updated_representative[
            "review_card_status"
        ] = "withheld_multiline_wrap_evidence_missing"
    elif _is_candidate2_lead_probe_profile(
        str(proof_profile_data.get("proof_profile") or "")
    ):
        review_card_status = (
            "withheld_tiny_render_path_nearer_probe_completed"
            if _is_tiny_render_path_probe_profile(
                str(proof_profile_data.get("proof_profile") or "")
            )
            else "withheld_review_already_consumed_candidate2_promoted"
        )
        report["review_card_status"] = review_card_status
        updated_representative["review_card_status"] = review_card_status
    else:
        report["review_card_status"] = "review_card_allowed_after_scope_checks"
        updated_representative[
            "review_card_status"
        ] = "review_card_allowed_after_scope_checks"
    updated_representative.setdefault("subtitle_overlay_visual_proof", {})[
        "review_card_status"
    ] = updated_representative["review_card_status"]
    report["visual_proof_status"] = visual_proof_status
    updated_representative["visual_proof_status"] = visual_proof_status
    presentation_review_pack = None
    if (
        proof_profile_data.get("proof_profile")
        in {
            ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE,
            ED10Y_CANDIDATE2_CARRY_FORWARD_PROFILE,
            ED10Z_TINY_RENDER_PATH_NEARER_PROBE_PROFILE,
        }
    ):
        presentation_review_pack = _subtitle_presentation_review_pack(
            report=report,
            pack_path=presentation_review_pack_path,
            pack_html_path=presentation_review_pack_html_path,
            base=base,
        )
        report["subtitle_presentation_review_pack"] = {
            "json": _display_path(presentation_review_pack_path, base),
            "html": _display_path(presentation_review_pack_html_path, base),
            "artifact_id": presentation_review_pack["artifact_id"],
        }
        report.setdefault("outputs", {})["subtitle_presentation_review_pack"] = (
            _display_path(presentation_review_pack_path, base)
        )
        report.setdefault("outputs", {})["subtitle_presentation_review_pack_html"] = (
            _display_path(presentation_review_pack_html_path, base)
        )
    if not dry_run:
        review_dir.mkdir(parents=True, exist_ok=True)
        _write_json(report, report_path)
        report_html_path.write_text(_overlay_report_html(report), encoding="utf-8")
        focused_review_html_path.write_text(
            _focused_current_proof_html(report),
            encoding="utf-8",
        )
        if presentation_review_pack is not None:
            _write_json(presentation_review_pack, presentation_review_pack_path)
            presentation_review_pack_html_path.write_text(
                _subtitle_presentation_review_pack_html(presentation_review_pack),
                encoding="utf-8",
            )
        _write_json(updated_representative, updated_representative_path)
        updated_representative_html_path.write_text(
            _representative_report_html(updated_representative),
            encoding="utf-8",
        )

    return {
        "report": report,
        "representative_visual_proof_report": updated_representative,
        "report_path": report_path,
        "report_html_path": report_html_path,
        "focused_review_html_path": focused_review_html_path,
        "subtitle_presentation_review_pack_path": presentation_review_pack_path,
        "subtitle_presentation_review_pack_html_path": presentation_review_pack_html_path,
        "subtitle_presentation_review_pack": presentation_review_pack,
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
    diagnostic_ass_style: dict[str, Any],
    proof_profile_id: str,
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
        diagnostic_ass_style=diagnostic_ass_style,
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
            candidate_visuals=[],
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
            candidate_visuals=[],
            base=base,
        )

    cut_paths["output_dir"].mkdir(parents=True, exist_ok=True)
    cut_paths["reference_dir"].mkdir(parents=True, exist_ok=True)
    previous_proof_artifacts = _archive_existing_proof_artifacts(cut_paths)
    legacy_autoload_srt = _mitigate_legacy_autoload_srt(cut_paths)
    layout = _probed_subtitle_layout_contract(
        source_video_path=source_media["source_video"]["resolved_path"],
        ffprobe_path=ffprobe_path,
        diagnostic_ass_style=diagnostic_ass_style,
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
            sample_specs=_sample_frame_specs(
                presentation_items,
                duration,
                include_multiline_wrap_evidence=proof_profile_id
                in {
                    ED10R_KEIFONT_DENSE_STRESS_PROOF_PROFILE,
                    ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE,
                }
                or _is_candidate2_lead_probe_profile(proof_profile_id),
            ),
            ffmpeg_path=render_result.ffmpeg_path,
            runner=runner,
        )
        candidate_visuals = (
            _render_ed10w_candidate_visuals(
                source_media=source_media,
                cut=cut,
                renderable_items=renderable_items,
                base_layout=layout,
                cut_paths=cut_paths,
                ffmpeg_path=render_result.ffmpeg_path,
                ffprobe_path=ffprobe_path,
                container=container,
                base=base,
                runner=runner,
            )
            if proof_profile_id
            in {
                ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE,
            }
            or _is_candidate2_lead_probe_profile(proof_profile_id)
            else []
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
            candidate_visuals=candidate_visuals,
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
            candidate_visuals=locals().get("candidate_visuals", []),
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
    candidate_visuals: list[dict[str, Any]],
    base: Path,
) -> dict[str, Any]:
    cut_id = str(cut.get("id") or "")
    start_seconds = _required_float(cut.get("start_seconds"), f"{cut_id}.start_seconds")
    end_seconds = _required_float(cut.get("end_seconds"), f"{cut_id}.end_seconds")
    renderable_items = [
        item for item in items if item.get("status") in RENDERABLE_SUBTITLE_STATUSES
    ]
    font_bbox_wrap = _font_bbox_wrap_summary(presentation_items)
    multiline_wrap_evidence = _multiline_wrap_evidence_readback(
        presentation_items=presentation_items,
        sample_frame_extracts=sample_frame_extracts,
        base=base,
    )
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
        "multiline_wrap_evidence": multiline_wrap_evidence,
        "style_direction": _diagnostic_style_direction(_layout_style(layout)),
        "style_parameters": _style_parameter_readback(
            items,
            layout=layout,
            presentation_items=presentation_items,
        ),
        "font_bbox_wrap_readback": font_bbox_wrap,
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
            "ed10w_candidate_visuals": candidate_visuals,
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
            "ed10w_candidate_visuals": {
                str(item.get("candidate_number")): Path(
                    str(item.get("image_path") or "")
                ).exists()
                for item in candidate_visuals
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
            "japanese_font_bbox_wrapping_applied_human_review_required"
            if (
                overlay_present
                and font_bbox_wrap.get("all_renderable_items_applied_to_proof_text") is True
                and font_bbox_wrap.get("one_character_orphan_present") is not True
            )
            else "diagnostic_overlay_generated_human_review_required"
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
    focused_review_html_path: Path,
    base: Path,
    dry_run: bool,
    diagnostic_ass_style: dict[str, Any],
    proof_profile: dict[str, Any],
) -> dict[str, Any]:
    success_count = sum(
        1 for item in cut_reports if item.get("subtitle_overlay_present") is True
    )
    style_parameters = _report_style_parameter_summary(cut_reports)
    font_visual_evidence = _font_visual_evidence_readback(
        proof_profile=proof_profile,
        style_parameters=style_parameters,
    )
    review_memory = copy.deepcopy(proof_profile.get("review_memory"))
    if isinstance(review_memory, dict) and (
        font_visual_evidence.get("valid_requested_font_visual_evidence") is True
    ):
        if review_memory.get("current_blocker") == "font_evidence_fallback":
            review_memory["current_blocker"] = "none_for_font_evidence"
        review_memory["font_evidence_gate"] = "valid_requested_keifont_visual_evidence"
    elif isinstance(review_memory, dict) and (
        font_visual_evidence.get("valid_requested_font_visual_evidence") is False
    ):
        review_memory["font_evidence_gate"] = "blocked_requested_keifont_font_missing_uses_fallback"
    warnings = [
        "Diagnostic overlay proof only; production render acceptance is not claimed.",
        "Production subtitle design, creative acceptance, publishing acceptance, and rights approval are out of scope.",
        "Generated artifacts are local review artifacts and must not be staged from episodes/.",
        "Burned-in subtitles are inside the proof video; sidecar SRT files are reference-only and should not be enabled as a VLC subtitle track during embedded-subtitle review.",
    ]
    if font_visual_evidence.get("valid_requested_font_visual_evidence") is False:
        warnings.append(str(font_visual_evidence.get("warning") or "requested font visual evidence is not valid"))
    return {
        "schema_version": SCHEMA_VERSION,
        "report_kind": REPORT_KIND,
        "artifact_id": proof_profile.get("artifact_id"),
        "proof_profile": proof_profile.get("proof_profile"),
        "source_review_artifact_id": proof_profile.get("source_review_artifact_id"),
        "source_previous_artifact_id": proof_profile.get("source_previous_artifact_id"),
        "source_proof_artifact_id": proof_profile.get("source_proof_artifact_id"),
        "source_comparison_artifact_id": proof_profile.get(
            "source_comparison_artifact_id"
        ),
        "current_lead_candidate_id": proof_profile.get("current_lead_candidate_id"),
        "fallback_reference_candidate_id": proof_profile.get(
            "fallback_reference_candidate_id"
        ),
        "held_reference_candidate_ids": proof_profile.get(
            "held_reference_candidate_ids", []
        ),
        "selected_typography_base": proof_profile.get("selected_typography_base"),
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
        "style_direction": _diagnostic_style_direction(diagnostic_ass_style),
        "style_parameters": style_parameters,
        "font_visual_evidence": font_visual_evidence,
        "review_surface_direction": proof_profile.get("review_surface_direction"),
        "candidate_state": proof_profile.get("candidate_state"),
        "review_memory": review_memory,
        "focused_proof_review": proof_profile.get("focused_proof_review"),
        "review_debt": proof_profile.get("review_debt", []),
        "multiline_wrap_evidence": _report_multiline_wrap_evidence_summary(
            cut_reports
        ),
        "font_bbox_wrap_readback": _report_font_bbox_wrap_summary(cut_reports),
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
            "focused_review_html": _display_path(focused_review_html_path, base),
        },
        "production_candidate": False,
        "rights_status": "pending",
        "production_usage_allowed": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "warnings": warnings,
    }


def _font_visual_evidence_readback(
    *,
    proof_profile: dict[str, Any],
    style_parameters: dict[str, Any],
) -> dict[str, Any]:
    route = style_parameters.get("font_family_route") or {}
    profile = str(proof_profile.get("proof_profile") or "")
    requested = str(route.get("requested") or "")
    resolved = str(route.get("resolved") or "")
    font_file_status = str(route.get("font_file_status") or "")
    resolved_font_file = route.get("resolved_font_file")
    requires_keifont = profile in {
        ED10P_KEIFONT_LEAD_REPRESENTATIVE_PROOF_PROFILE,
        ED10R_KEIFONT_DENSE_STRESS_PROOF_PROFILE,
        ED10W_SUBTITLE_PRESENTATION_REVIEW_PACK_PROFILE,
        ED10Y_CANDIDATE2_CARRY_FORWARD_PROFILE,
        ED10Z_TINY_RENDER_PATH_NEARER_PROBE_PROFILE,
    }
    valid_keifont = (
        requested == "Keifont"
        and resolved == "Keifont"
        and font_file_status.startswith("candidate_primary_font_file_found")
    )
    if requires_keifont and not valid_keifont:
        return {
            "status": "blocked_requested_keifont_font_missing_uses_fallback",
            "valid_requested_font_visual_evidence": False,
            "requested_font_family": requested,
            "resolved_font_family": resolved,
            "resolved_font_file": resolved_font_file,
            "font_file_status": font_file_status,
            "review_implication": (
                "Do not treat this generated proof as Keifont visual evidence until "
                "the Keifont font file resolves on this Windows profile."
            ),
            "warning": (
                "Keifont proof profile is active, but the requested Keifont font "
                "file was not found and the renderer fell back to another font."
            ),
        }
    if requires_keifont:
        return {
            "status": "valid_requested_keifont_visual_evidence",
            "valid_requested_font_visual_evidence": True,
            "requested_font_family": requested,
            "resolved_font_family": resolved,
            "resolved_font_file": resolved_font_file,
            "font_file_status": font_file_status,
            "review_implication": "The proof can be reviewed as Keifont visual evidence.",
        }
    return {
        "status": "not_required_for_profile",
        "valid_requested_font_visual_evidence": None,
        "requested_font_family": requested,
        "resolved_font_family": resolved,
        "resolved_font_file": resolved_font_file,
        "font_file_status": font_file_status,
    }


def _diagnostic_style_direction(
    diagnostic_ass_style: dict[str, Any] | None = None,
) -> dict[str, Any]:
    style = diagnostic_ass_style or _diagnostic_ass_style_for_candidate(None)
    return {
        "preset_name": DIAGNOSTIC_STYLE_DIRECTION_NAME,
        "presentation_contract_id": SUBTITLE_PRESENTATION_CONTRACT_ID,
        "contract_status": "diagnostic_direction_readback",
        "typography_decoration_candidate_id": style.get(
            "typography_decoration_candidate_id"
        ),
        "style_candidate_id": style.get("candidate_id"),
        "style_selection_source": style.get("selection_source"),
        "ed10g_small_adjustment_selected": style.get(
            "ed10g_small_adjustment_selected"
        ),
        "ed10i_kirinuki_gothic_balance_candidate": style.get(
            "ed10i_kirinuki_gothic_balance_candidate"
        ),
        "ed10j_kirinuki_font_audit_candidate": style.get(
            "ed10j_kirinuki_font_audit_candidate"
        ),
        "font_family_route": {
            "requested": style.get("requested_font_family"),
            "resolved": style.get("resolved_font_family"),
            "resolved_font_file": style.get("resolved_font_file"),
            "font_file_status": style.get("font_file_status"),
        },
        "decoration_route": {
            "display_name": style.get("display_name"),
            "note": style.get("decoration_note"),
            "stroke_ratio": style.get("stroke_ratio"),
            "shadow_offset_ratio": style.get("shadow_offset_ratio"),
            "text_fill": style.get("text_fill"),
            "stroke_fill": style.get("stroke_fill"),
            "shadow_fill": style.get("shadow_fill"),
            "badge_fill": style.get("badge_fill"),
            "badge_outline": style.get("badge_outline"),
            "body_weight_note": style.get("body_weight_note"),
            "outline_balance_role": style.get("outline_balance_role"),
            "emoji_evaluation_scope": style.get("emoji_evaluation_scope"),
        },
        "target_viewing_context": "smartphone_readable_japanese_clip_subtitle",
        "visual_weight": "large_heavily_outlined_clip_dialogue_not_restrained_movie_subtitles",
        "preferred_non_pov_pattern": "face_icon_plus_left_aligned_subtitle",
        "implemented_pattern": "speaker_badge_placeholder_plus_left_aligned_subtitle",
        "supported_presentation_modes": list(SUPPORTED_PRESENTATION_MODES),
        "mode_semantics": {
            "badge_left_dialogue": "recommended for normal speaker-identified dialogue in the current proof",
            "bottom_center_emphasis": "supported for emphasized dialogue or strong one-liners; comparison/support mode here",
            "reaction_caption": "tracked in subtitle_style_spike for punchline, surprise, or instant reaction such as 来ねぇ！！",
            "speaker_badge_stack": "tracked in subtitle_style_spike as a comparison-only placeholder stack for future face-icon/nameplate work",
            "repeated_text_across_modes": "intentional comparison in reports, not a universal style rule",
        },
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
    diagnostic_ass_style: dict[str, Any] | None = None,
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
        diagnostic_ass_style=diagnostic_ass_style,
    )


def _subtitle_layout_contract(
    *,
    frame_width: int,
    frame_height: int,
    mode: str,
    dimension_source: str,
    diagnostic_ass_style: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if mode not in SUPPORTED_PRESENTATION_MODES:
        raise SubtitleOverlayVisualProofError(f"unsupported presentation mode: {mode}")
    width = max(1, int(frame_width))
    height = max(1, int(frame_height))
    style = diagnostic_ass_style or _diagnostic_ass_style_for_candidate(None)
    outline_ratio = float(style.get("stroke_ratio") or LAYOUT_RATIOS["outline_to_font_size"])
    shadow_ratio = float(style.get("shadow_offset_ratio") or LAYOUT_RATIOS["shadow_to_font_size"])
    if mode == "bottom_center_emphasis":
        font_size = _layout_round(height * LAYOUT_RATIOS["bottom_center_font_size_to_frame_height"])
    else:
        font_size = _layout_round(height * LAYOUT_RATIOS["font_size_to_frame_height"])
    outline_override = style.get("outline_px_override")
    shadow_override = style.get("shadow_px_override")
    outline = (
        max(1, _layout_round(float(outline_override)))
        if outline_override is not None
        else max(2, _layout_round(font_size * outline_ratio))
    )
    shadow = (
        max(0, _layout_round(float(shadow_override)))
        if shadow_override is not None
        else max(1, _layout_round(font_size * shadow_ratio))
    )
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
        "outline": f"max(2, round(font_size * {outline_ratio}))",
        "shadow": f"max(1, round(font_size * {shadow_ratio}))",
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
        "ratios": {
            **LAYOUT_RATIOS,
            "outline_to_font_size": outline_ratio,
            "shadow_to_font_size": shadow_ratio,
        },
        "diagnostic_ass_style": style,
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
    presentation_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    style_slots = _unique_strings(item.get("style_slot") for item in items)
    layout = layout or _subtitle_layout_contract(
        frame_width=DEFAULT_FRAME_WIDTH,
        frame_height=DEFAULT_FRAME_HEIGHT,
        mode=DEFAULT_PRESENTATION_MODE,
        dimension_source="default_style_readback",
    )
    style = _layout_style(layout)
    values = layout["values"]
    font_bbox_wrap = _font_bbox_wrap_summary(presentation_items or [])
    return {
        "renderer": "ffmpeg_subtitles_filter_ass",
        "style_slot": _single_or_mixed(style_slots) or "subtitle.default",
        "style_slots": style_slots or ["subtitle.default"],
        "style_candidate_id": style["candidate_id"],
        "typography_decoration_candidate_id": style.get(
            "typography_decoration_candidate_id"
        ),
        "style_selection_source": style.get("selection_source"),
        "ed10g_small_adjustment_selected": style.get(
            "ed10g_small_adjustment_selected"
        ),
        "ed10i_kirinuki_gothic_balance_candidate": style.get(
            "ed10i_kirinuki_gothic_balance_candidate"
        ),
        "ed10j_kirinuki_font_audit_candidate": style.get(
            "ed10j_kirinuki_font_audit_candidate"
        ),
        "typography_decoration_candidate": {
            "candidate_id": style.get("typography_decoration_candidate_id"),
            "display_name": style.get("display_name"),
            "decoration_note": style.get("decoration_note"),
            "body_weight_note": style.get("body_weight_note"),
            "outline_balance_role": style.get("outline_balance_role"),
            "emoji_evaluation_scope": style.get("emoji_evaluation_scope"),
            "requested_font_family": style.get("requested_font_family"),
            "resolved_font_family": style.get("resolved_font_family"),
            "resolved_font_file": style.get("resolved_font_file"),
            "font_file_status": style.get("font_file_status"),
            "stroke_ratio": style.get("stroke_ratio"),
            "shadow_offset_ratio": style.get("shadow_offset_ratio"),
            "text_fill": style.get("text_fill"),
            "stroke_fill": style.get("stroke_fill"),
            "shadow_fill": style.get("shadow_fill"),
            "badge_fill": style.get("badge_fill"),
            "badge_outline": style.get("badge_outline"),
        },
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
        "font_family_route": {
            "requested": style.get("requested_font_family"),
            "resolved": style.get("resolved_font_family"),
            "resolved_font_file": style.get("resolved_font_file"),
            "font_file_status": style.get("font_file_status"),
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
            "wrap_algorithm": font_bbox_wrap["wrap_algorithm"],
            "wrapping_authority": FONT_BBOX_WRAP_AUTHORITY,
            "font_bbox_applied_to_proof_text": font_bbox_wrap.get(
                "all_renderable_items_applied_to_proof_text"
            ),
            "explicit_line_breaks_passed_to_ass": font_bbox_wrap.get(
                "explicit_line_breaks_passed_to_ass"
            ),
            "one_character_orphan_present": font_bbox_wrap.get(
                "one_character_orphan_present"
            ),
            "watch_item": (
                "Rendered visual review is still required after formula-based "
                "diagnostic wrapping."
            ),
        },
        "font_bbox_wrap_readback": font_bbox_wrap,
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
    style = _layout_style(layout)
    values = layout["values"]
    return {
        "style_candidate_id": style["candidate_id"],
        "typography_decoration_candidate_id": style.get(
            "typography_decoration_candidate_id"
        ),
        "style_selection_source": style.get("selection_source"),
        "ed10g_small_adjustment_selected": style.get(
            "ed10g_small_adjustment_selected"
        ),
        "ed10i_kirinuki_gothic_balance_candidate": style.get(
            "ed10i_kirinuki_gothic_balance_candidate"
        ),
        "ed10j_kirinuki_font_audit_candidate": style.get(
            "ed10j_kirinuki_font_audit_candidate"
        ),
        "preset_name": DIAGNOSTIC_STYLE_DIRECTION_NAME,
        "presentation_mode": layout["mode"],
        "supported_presentation_modes": list(SUPPORTED_PRESENTATION_MODES),
        "renderer_input": "ASS style file consumed by FFmpeg subtitles filter",
        "comparison_baseline": "previous FFmpeg/libass SRT/default-centered proof looked too small and movie-subtitle-like for YouTube review",
        "intended_design_target": "reference-driven non-POV speaker badge plus large left-aligned Japanese clip dialogue subtitle",
        "font_name": style["font_name"],
        "font_family_route": {
            "requested": style.get("requested_font_family"),
            "resolved": style.get("resolved_font_family"),
            "resolved_font_file": style.get("resolved_font_file"),
            "font_file_status": style.get("font_file_status"),
        },
        "font_size": values["font_size"],
        "outline": values["outline"],
        "shadow": values["shadow"],
        "decoration_route": {
            "display_name": style.get("display_name"),
            "note": style.get("decoration_note"),
            "stroke_ratio": style.get("stroke_ratio"),
            "shadow_offset_ratio": style.get("shadow_offset_ratio"),
            "text_fill": style.get("text_fill"),
            "stroke_fill": style.get("stroke_fill"),
            "shadow_fill": style.get("shadow_fill"),
            "badge_fill": style.get("badge_fill"),
            "badge_outline": style.get("badge_outline"),
            "body_weight_note": style.get("body_weight_note"),
            "outline_balance_role": style.get("outline_balance_role"),
            "emoji_evaluation_scope": style.get("emoji_evaluation_scope"),
        },
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


def _report_font_bbox_wrap_summary(cut_reports: list[dict[str, Any]]) -> dict[str, Any]:
    per_cut = {
        str(cut.get("cut_id")): cut.get("font_bbox_wrap_readback") or {}
        for cut in cut_reports
    }
    cut_readbacks = [value for value in per_cut.values() if value]
    if not cut_readbacks:
        return _font_bbox_wrap_summary([])
    first = cut_readbacks[0]
    return {
        "wrap_algorithm": first.get("wrap_algorithm") or {},
        "wrapping_authority": FONT_BBOX_WRAP_AUTHORITY,
        "measurement_renderer": "Pillow ImageDraw.multiline_textbbox",
        "proof_renderer": "ffmpeg_subtitles_filter_ass",
        "renderer_gap": _font_bbox_renderer_gap(),
        "typography_decoration_candidate_id": _single_or_mixed(
            [str(item.get("typography_decoration_candidate_id") or "") for item in cut_readbacks]
        ),
        "style_selection_source": _single_or_mixed(
            [str(item.get("style_selection_source") or "") for item in cut_readbacks]
        ),
        "font_family": _single_or_mixed(
            [str(item.get("font_family") or "") for item in cut_readbacks]
        ),
        "font_file_status": _single_or_mixed(
            [str(item.get("font_file_status") or "") for item in cut_readbacks]
        ),
        "font_fallback_status": _single_or_mixed(
            [str(item.get("font_fallback_status") or "") for item in cut_readbacks]
        ),
        "cut_count": len(cut_readbacks),
        "all_renderable_items_applied_to_proof_text": all(
            item.get("all_renderable_items_applied_to_proof_text") is True
            for item in cut_readbacks
        ),
        "explicit_line_breaks_passed_to_ass": all(
            item.get("explicit_line_breaks_passed_to_ass") is True
            for item in cut_readbacks
        ),
        "orphan_prevention_applied_count": sum(
            int(item.get("orphan_prevention_applied_count") or 0)
            for item in cut_readbacks
        ),
        "suffix_tail_prevention_applied_count": sum(
            int(item.get("suffix_tail_prevention_applied_count") or 0)
            for item in cut_readbacks
        ),
        "suspicious_tail_line_present": any(
            item.get("suspicious_tail_line_present") is True for item in cut_readbacks
        ),
        "one_character_orphan_present": any(
            item.get("one_character_orphan_present") is True for item in cut_readbacks
        ),
        "orphan_prevention_examples": [
            example
            for item in cut_readbacks
            for example in item.get("orphan_prevention_examples") or []
        ][:8],
        "suffix_tail_prevention_examples": [
            example
            for item in cut_readbacks
            for example in item.get("suffix_tail_prevention_examples") or []
        ][:8],
        "suspicious_tail_lines": [
            line
            for item in cut_readbacks
            for line in item.get("suspicious_tail_lines") or []
        ],
        "measured_bbox_provenance": first.get("measured_bbox_provenance") or {},
        "per_cut": per_cut,
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
        "mode_semantics": {
            "badge_left_dialogue": "normal speaker-identified dialogue",
            "bottom_center_emphasis": "emphasized dialogue or strong one-liner",
            "reaction_caption": "punchline, surprise, or instant reaction; tracked in subtitle_style_spike",
            "speaker_badge_stack": "comparison-only placeholder stack for future face-icon/nameplate work",
            "repeated_text_across_modes": "intentional comparison, not a universal style rule",
        },
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
    style = _layout_style(layout)
    return {
        "preferred_pattern": "face_icon_plus_left_aligned_subtitle",
        "implemented_pattern": "speaker_badge_placeholder_plus_left_aligned_subtitle",
        "presentation_mode": layout["mode"],
        "pattern_status": "approximated_with_fallback_speaker_badge_no_face_icon_assets",
        "real_face_icon_assets_available": False,
        "fallback_used": True,
        "fallback_kind": "speaker_badge_placeholder",
        "fallback_label": style["speaker_badge_label"],
        "placeholder_badge_decoration": {
            "candidate_id": style.get("typography_decoration_candidate_id"),
            "badge_fill": style.get("badge_fill"),
            "badge_outline": style.get("badge_outline"),
            "selection_source": style.get("selection_source"),
        },
        "fallback_human_review_note": (
            "SPK/A/B badges are temporary speaker badge placeholders, not real "
            "face icons and not production speaker identity design. Real face "
            "icon asset intake is a separate future slice."
        ),
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
    multiline_roles = [
        role for role in roles if role.startswith("multiline_wrap_")
    ]
    return {
        "policy": "subtitle_bearing_active_cues_only",
        "roles": roles,
        "subtitle_ids": subtitle_ids,
        "multiline_wrap_roles": multiline_roles,
        "has_multiline_wrap_screenshot": bool(multiline_roles),
        "includes_response_referral_block": any(
            subtitle_id in RESPONSE_REFERRAL_SUBTITLE_IDS for subtitle_id in subtitle_ids
        ),
        "sample_count": len(sample_frame_extracts),
        "ocr_verified": False,
        "human_visual_review_required": True,
    }


def _multiline_wrap_evidence_readback(
    *,
    presentation_items: list[dict[str, Any]],
    sample_frame_extracts: list[dict[str, Any]],
    base: Path,
) -> dict[str, Any]:
    multiline_items = [
        item
        for item in presentation_items
        if int(item.get("wrapped_line_count") or 0) > 1
    ]
    screenshots_by_subtitle: dict[str, dict[str, Any]] = {}
    for extract in sample_frame_extracts:
        role = str(extract.get("role") or "")
        subtitle_id = str(extract.get("subtitle_id") or "")
        if role.startswith("multiline_wrap_") and subtitle_id:
            screenshots_by_subtitle[subtitle_id] = extract
    evidence_items: list[dict[str, Any]] = []
    for item in multiline_items[:MAX_MULTILINE_WRAP_EVIDENCE_SAMPLES]:
        subtitle_id = str(item.get("subtitle_id") or "")
        screenshot = screenshots_by_subtitle.get(subtitle_id)
        evidence_items.append(
            {
                "subtitle_id": subtitle_id,
                "display_start_seconds": item.get("display_start_seconds"),
                "display_end_seconds": item.get("display_end_seconds"),
                "wrapped_line_count": item.get("wrapped_line_count"),
                "wrapped_lines": item.get("wrapped_lines") or [],
                "text": item.get("text"),
                "selected_break_reason": item.get("selected_break_reason"),
                "screenshot_role": screenshot.get("role") if screenshot else None,
                "screenshot_frame_seconds": (
                    screenshot.get("frame_seconds") if screenshot else None
                ),
                "screenshot_path": (
                    _display_path(Path(str(screenshot.get("path") or "")), base)
                    if screenshot
                    else None
                ),
            }
        )
    screenshot_count = len(
        [
            extract
            for extract in sample_frame_extracts
            if str(extract.get("role") or "").startswith("multiline_wrap_")
        ]
    )
    if multiline_items and screenshot_count:
        status = "multiline_wrap_evidence_surfaced"
    elif multiline_items:
        status = "multiline_wrap_cues_present_but_screenshots_missing"
    else:
        status = "no_multiline_wrap_cues_detected"
    return {
        "status": status,
        "has_multiline_wrapped_cues": bool(multiline_items),
        "multiline_item_count": len(multiline_items),
        "max_wrapped_line_count": max(
            (int(item.get("wrapped_line_count") or 0) for item in multiline_items),
            default=0,
        ),
        "screenshot_count": screenshot_count,
        "evidence_items": evidence_items,
        "review_implication": (
            "Review multiline readability from the compact screenshot evidence."
            if status == "multiline_wrap_evidence_surfaced"
            else "Do not treat this focused proof as multiline/wrap review-ready."
        ),
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


def _report_multiline_wrap_evidence_summary(
    cut_reports: list[dict[str, Any]]
) -> dict[str, Any]:
    per_cut = {
        str(cut.get("cut_id")): cut.get("multiline_wrap_evidence") or {}
        for cut in cut_reports
    }
    total_multiline = sum(
        int((evidence or {}).get("multiline_item_count") or 0)
        for evidence in per_cut.values()
    )
    total_screenshots = sum(
        int((evidence or {}).get("screenshot_count") or 0)
        for evidence in per_cut.values()
    )
    if total_multiline and total_screenshots:
        status = "multiline_wrap_evidence_surfaced"
    elif total_multiline:
        status = "multiline_wrap_cues_present_but_screenshots_missing"
    else:
        status = "no_multiline_wrap_cues_detected"
    return {
        "status": status,
        "has_multiline_wrapped_cues": total_multiline > 0,
        "multiline_item_count": total_multiline,
        "screenshot_count": total_screenshots,
        "per_cut": per_cut,
        "review_implication": (
            "The focused review can ask about multiline readability."
            if status == "multiline_wrap_evidence_surfaced"
            else "Withhold dense/stress Review Card until multiline evidence is surfaced."
        ),
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
    proof_profile: dict[str, Any],
) -> dict[str, Any]:
    updated = copy.deepcopy(representative_report)
    updated["updated_at"] = _now()
    updated["active_overlay_artifact_id"] = proof_profile.get("artifact_id")
    updated["proof_profile"] = proof_profile.get("proof_profile")
    updated["source_review_artifact_id"] = proof_profile.get("source_review_artifact_id")
    updated["source_proof_artifact_id"] = proof_profile.get("source_proof_artifact_id")
    updated["source_comparison_artifact_id"] = proof_profile.get(
        "source_comparison_artifact_id"
    )
    updated["review_surface_direction"] = proof_profile.get("review_surface_direction")
    updated["candidate_state"] = proof_profile.get("candidate_state")
    updated["review_memory"] = overlay_report.get("review_memory") or proof_profile.get(
        "review_memory"
    )
    updated["focused_proof_review"] = proof_profile.get("focused_proof_review")
    updated["review_debt"] = proof_profile.get("review_debt", [])
    updated["multiline_wrap_evidence"] = (
        overlay_report.get("multiline_wrap_evidence") or {}
    )
    updated["production_candidate"] = False
    updated["creative_acceptance"] = False
    updated["publish_acceptance"] = False
    updated["rights_status"] = "pending"
    updated["production_usage_allowed"] = False
    updated["diagnostic_style_direction"] = overlay_report["style_direction"]
    updated["diagnostic_style_parameters"] = overlay_report["style_parameters"]
    updated["font_visual_evidence"] = overlay_report.get("font_visual_evidence") or {}
    updated["font_bbox_wrap_readback"] = overlay_report.get("font_bbox_wrap_readback") or {}
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
        "font_visual_evidence": overlay_report.get("font_visual_evidence") or {},
        "multiline_wrap_evidence": overlay_report.get("multiline_wrap_evidence")
        or {},
        "font_bbox_wrap_readback": overlay_report.get("font_bbox_wrap_readback") or {},
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
        "review_card_status": overlay_report.get("review_card_status"),
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
        assessment["font_bbox_wrap_readback"] = proof.get("font_bbox_wrap_readback") or {}
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
            "font_bbox_wrap_readback": proof.get("font_bbox_wrap_readback") or {},
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
        if set(target_cut_ids) != {"cut_002", "cut_003"}:
            return "blocked_no_target_overlay_proof"
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
        raw_text = str(item.get("text") or "")
        proxy_wrapped = measure_subtitle(
            raw_text,
            wrap_eaw=layout["values"]["dialogue_wrap_eaw"],
        )
        proxy_lines = [line.text for line in proxy_wrapped.lines] or [raw_text]
        font_bbox_wrap = _font_bbox_wrap_readback(
            text=raw_text,
            layout=layout,
            proxy_wrapped_lines=proxy_lines,
            proxy_longest_line_eaw=proxy_wrapped.longest_line_eaw,
        )
        font_bbox_wrap = {
            **font_bbox_wrap,
            "subtitle_id": item.get("subtitle_id"),
            "subtitle_item_status": item.get("status"),
        }
        wrapped_lines = font_bbox_wrap["selected_wrapped_lines"] or proxy_lines
        wrapped_text = "\n".join(wrapped_lines)
        item_layout = _item_layout(layout, wrapped_line_count=len(wrapped_lines))
        presentation.append(
            {
                **item,
                "display_start_seconds": round(start, 3),
                "display_end_seconds": round(display_end, 3),
                "replacement_applied": replacement_applied,
                "replacement_end_source": replacement_end_source,
                "wrapped_text": wrapped_text,
                "wrapped_lines": wrapped_lines,
                "wrapped_line_count": len(wrapped_lines),
                "max_wrapped_line_eaw": max(
                    (measure_subtitle(line).longest_line_eaw for line in wrapped_lines),
                    default=proxy_wrapped.longest_line_eaw,
                ),
                "wrap_algorithm": font_bbox_wrap["wrap_algorithm"],
                "candidate_breaks": font_bbox_wrap["candidate_breaks"],
                "selected_break_reason": font_bbox_wrap["selected_break_reason"],
                "selected_breaks": font_bbox_wrap["selected_breaks"],
                "orphan_prevention_applied": font_bbox_wrap[
                    "orphan_prevention_applied"
                ],
                "suffix_tail_prevention_applied": font_bbox_wrap[
                    "suffix_tail_prevention_applied"
                ],
                "suspicious_tail_line_present": font_bbox_wrap[
                    "suspicious_tail_line_present"
                ],
                "font_bbox_wrap_readback": font_bbox_wrap,
                "presentation_mode": layout["mode"],
                "layout": item_layout,
            }
        )
    return presentation


def _font_bbox_wrap_readback(
    *,
    text: str,
    layout: dict[str, Any],
    proxy_wrapped_lines: list[str],
    proxy_longest_line_eaw: int,
) -> dict[str, Any]:
    values = layout["values"]
    style = _layout_style(layout)
    max_width = _font_bbox_max_text_width(layout)
    font_size = int(values["font_size"])
    stroke_width = int(values["outline"])
    spacing = max(0, int(values["line_height"]) - font_size)
    base = {
        "wrap_algorithm": {
            "name": subtitle_style_spike.JAPANESE_WRAP_ALGORITHM,
            "source_function": FONT_BBOX_WRAP_SOURCE,
            "authority": FONT_BBOX_WRAP_AUTHORITY,
            "not_character_count_only": True,
            "not_grid_based": True,
            "max_text_width": max_width,
            "candidate_break_strategy": (
                "Japanese punctuation, particle, and phrase-boundary candidates are "
                "preferred only after the candidate prefix passes Pillow font bbox "
                "pixel-width measurement."
            ),
            "orphan_prevention": (
                "When a greedy measured break would leave a single visible Japanese "
                "character or kana on the next line, the wrapper uses an earlier "
                "measured-valid break if one exists."
            ),
            "suffix_tail_prevention": (
                "When a measured break would isolate a short Japanese sentence "
                "suffix such as ます or か plus punctuation, the wrapper prefers "
                "a nearby measured-valid break when one exists."
            ),
        },
        "wrapping_authority": FONT_BBOX_WRAP_AUTHORITY,
        "measurement_renderer": "Pillow ImageDraw.multiline_textbbox",
        "proof_renderer": "ffmpeg_subtitles_filter_ass",
        "renderer_gap": _font_bbox_renderer_gap(),
        "proof_font_name": style["font_name"],
        "typography_decoration_candidate_id": style.get(
            "typography_decoration_candidate_id"
        ),
        "style_selection_source": style.get("selection_source"),
        "presentation_mode": layout["mode"],
        "mode_purpose": _presentation_mode_purpose(layout["mode"]),
        "style_token_readback": _style_token_readback(layout),
        "font_size": font_size,
        "stroke_width": stroke_width,
        "spacing": spacing,
        "candidate_breaks": [],
        "selected_breaks": [],
        "selected_break_reason": "font_bbox_measurement_unavailable",
        "selected_wrapped_lines": list(proxy_wrapped_lines),
        "wrapped_text": "\n".join(proxy_wrapped_lines),
        "orphan_prevention_applied": False,
        "orphan_prevention_examples": [],
        "suffix_tail_prevention_applied": False,
        "suffix_tail_prevention_examples": [],
        "suspicious_tail_line_present": False,
        "suspicious_tail_lines": [],
        "one_character_orphan_present": _has_one_character_orphan(proxy_wrapped_lines),
        "one_character_orphan_lines": _one_character_orphan_lines(proxy_wrapped_lines),
        "explicit_line_breaks_passed_to_ass": False,
        "applied_to_proof_text": False,
        "fallback_wrap_algorithm": "east_asian_width_proxy",
        "fallback_wrapped_lines": list(proxy_wrapped_lines),
        "fallback_longest_line_eaw": proxy_longest_line_eaw,
        "measured_width_by_line": [],
        "measured_bbox_provenance": _font_bbox_provenance(
            status="measurement_unavailable",
            measured_bbox=None,
        ),
    }
    if subtitle_style_spike.Image is None or subtitle_style_spike.ImageDraw is None:
        return {
            **base,
            "status": "unavailable_missing_pillow_optional_dependency",
            "font_family": None,
            "font_file": None,
            "font_file_status": "unavailable_missing_pillow_optional_dependency",
            "font_fallback_status": "unavailable_missing_pillow_optional_dependency",
            "limitation": (
                "Pillow is optional in the normal project environment; run with "
                "Pillow installed to carry font-bbox wrapped_lines into the ASS proof."
            ),
        }

    font_family, font_file, font_file_status = _select_font_for_layout(layout)
    try:
        font = subtitle_style_spike._load_font(font_file, font_size)
    except Exception as exc:  # pragma: no cover - depends on local font files
        return {
            **base,
            "status": "unavailable_font_load_failed",
            "font_family": font_family,
            "font_file": font_file,
            "font_file_status": font_file_status,
            "font_fallback_status": f"font_load_failed: {exc}",
            "limitation": "Pillow was available, but the selected measurement font failed to load.",
        }

    image = subtitle_style_spike.Image.new(
        "RGB",
        (int(layout["frame"]["width"]), int(layout["frame"]["height"])),
        (0, 0, 0),
    )
    draw = subtitle_style_spike.ImageDraw.Draw(image)
    wrap_result = subtitle_style_spike._wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    wrapped_lines = wrap_result.lines or [text]
    wrapped_text = "\n".join(wrapped_lines)
    measured_bbox = subtitle_style_spike._text_bbox_at_origin(
        draw=draw,
        text=wrapped_text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    return {
        **base,
        "status": "applied_to_ass_dialogue_text",
        "font_family": font_family,
        "font_file": font_file,
        "font_file_status": font_file_status,
        "font_fallback_status": font_file_status,
        "selected_break_reason": wrap_result.selected_break_reason,
        "candidate_breaks": wrap_result.candidate_breaks,
        "selected_breaks": wrap_result.selected_breaks,
        "selected_wrapped_lines": wrapped_lines,
        "wrapped_text": wrapped_text,
        "orphan_prevention_applied": wrap_result.orphan_prevention_applied,
        "orphan_prevention_examples": _orphan_prevention_examples(
            wrap_result.candidate_breaks
        ),
        "suffix_tail_prevention_applied": wrap_result.suffix_tail_prevention_applied,
        "suffix_tail_prevention_examples": _suffix_tail_prevention_examples(
            wrap_result.candidate_breaks
        ),
        "suspicious_tail_line_present": wrap_result.suspicious_tail_line_present,
        "suspicious_tail_lines": wrap_result.suspicious_tail_lines,
        "one_character_orphan_present": _has_one_character_orphan(wrapped_lines),
        "one_character_orphan_lines": _one_character_orphan_lines(wrapped_lines),
        "explicit_line_breaks_passed_to_ass": True,
        "applied_to_proof_text": True,
        "fallback_wrap_algorithm": None,
        "measured_width_by_line": wrap_result.measured_width_by_line,
        "measured_bbox_provenance": _font_bbox_provenance(
            status="systematic_measured_readback_for_wrap_decision",
            measured_bbox=_bbox_dict(measured_bbox),
        ),
    }


def _font_bbox_max_text_width(layout: dict[str, Any]) -> int:
    values = layout["values"]
    frame_width = int(layout["frame"]["width"])
    if layout["mode"] == "bottom_center_emphasis":
        return max(120, frame_width - int(values["margin_l"]) - int(values["margin_r"]))
    return max(
        120,
        frame_width - int(values["dialogue_x"]) - int(values["margin_r"]),
    )


def _font_bbox_provenance(
    *,
    status: str,
    measured_bbox: dict[str, int] | None,
) -> dict[str, Any]:
    return {
        "status": status,
        "measurement_method": "Pillow ImageDraw.multiline_textbbox before ASS emission",
        "source_function": "draw.multiline_textbbox",
        "manual_override": False,
        "hardcoded_per_sample": False,
        "design_target": False,
        "measured_bbox": measured_bbox,
        "human_review_note": (
            "This bbox is measurement support for choosing explicit line breaks. "
            "It is not a claim that FFmpeg/libass, YMM4, or Premiere will render "
            "the same glyph bbox."
        ),
    }


def _font_bbox_renderer_gap() -> dict[str, Any]:
    return {
        "exists": True,
        "classification": "controlled_line_breaks_carried_renderer_bbox_not_claimed",
        "reason": (
            "Pillow font-bbox measurement selects wrapped_lines that are passed to "
            "ASS as explicit line breaks, but final glyph rasterization and bbox "
            "still belong to FFmpeg/libass and can differ from Pillow."
        ),
        "production_typography_readiness_claimed": False,
    }


def _select_font_for_layout(layout: dict[str, Any]) -> tuple[str, str | None, str]:
    style = _layout_style(layout)
    resolved_font_file = style.get("resolved_font_file")
    if resolved_font_file and Path(str(resolved_font_file)).exists():
        return (
            str(style.get("resolved_font_family") or style.get("font_name") or ""),
            str(resolved_font_file),
            str(style.get("font_file_status") or "font_file_found"),
        )
    if style.get("ed10g_small_adjustment_selected") is True:
        family, font_file, status = subtitle_style_spike._select_font()
        return (
            family,
            font_file,
            f"selected_candidate_font_unavailable_used_global_fallback: {status}",
        )
    return subtitle_style_spike._select_font()


def _presentation_mode_purpose(mode: str) -> str:
    if mode == "bottom_center_emphasis":
        return "short emphasis or retort without speaker identity"
    return "normal dialogue with speaker identity badge"


def _style_token_readback(layout: dict[str, Any]) -> dict[str, Any]:
    values = layout["values"]
    style = _layout_style(layout)
    return {
        "mode": layout["mode"],
        "mode_purpose": _presentation_mode_purpose(layout["mode"]),
        "typography_decoration_candidate_id": style.get(
            "typography_decoration_candidate_id"
        ),
        "style_selection_source": style.get("selection_source"),
        "font": {
            "proof_font_name": style["font_name"],
            "requested_font_family": style.get("requested_font_family"),
            "resolved_font_family": style.get("resolved_font_family"),
            "resolved_font_file": style.get("resolved_font_file"),
            "font_file_status": style.get("font_file_status"),
            "font_size": values["font_size"],
            "formula": layout["formulas"]["font_size"],
        },
        "outline": {
            "value": values["outline"],
            "formula": layout["formulas"]["outline"],
        },
        "safe_area_margin": {
            "x": values["margin_l"],
            "y": values["bottom_margin"],
            "source": "formula_from_frame_dimensions",
        },
        "line_height": {
            "value": values["line_height"],
            "formula": layout["formulas"]["line_height"],
        },
        "badge": {
            "badge_width": values["badge_width"],
            "badge_height": values["badge_height"],
            "badge_text_gap": values["badge_text_gap"],
            "production_identity_asset": False,
        },
    }


def _orphan_prevention_examples(candidate_breaks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    selected_by_line = {
        int(candidate.get("line_number") or 0): candidate
        for candidate in candidate_breaks
        if candidate.get("selected") is True
    }
    for candidate in candidate_breaks:
        if candidate.get("would_leave_one_character_orphan") is not True:
            continue
        selected = selected_by_line.get(int(candidate.get("line_number") or 0))
        examples.append(
            {
                "line_number": candidate.get("line_number"),
                "prevented_break": {
                    "line_text": candidate.get("line_text"),
                    "remaining_text": candidate.get("remaining_text"),
                    "break_index": candidate.get("break_index"),
                    "measured_width": candidate.get("measured_width"),
                    "reason": candidate.get("reason"),
                },
                "selected_break": {
                    "line_text": selected.get("line_text") if selected else None,
                    "remaining_text": selected.get("remaining_text") if selected else None,
                    "break_index": selected.get("break_index") if selected else None,
                    "selection_reason": (
                        selected.get("selection_reason") if selected else None
                    ),
                },
            }
        )
    return examples


def _suffix_tail_prevention_examples(candidate_breaks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    selected_by_line = {
        int(candidate.get("line_number") or 0): candidate
        for candidate in candidate_breaks
        if candidate.get("selected") is True
    }
    for candidate in candidate_breaks:
        if candidate.get("would_leave_suspicious_tail_line") is not True:
            continue
        selected = selected_by_line.get(int(candidate.get("line_number") or 0))
        examples.append(
            {
                "line_number": candidate.get("line_number"),
                "prevented_break": {
                    "line_text": candidate.get("line_text"),
                    "remaining_text": candidate.get("remaining_text"),
                    "break_index": candidate.get("break_index"),
                    "measured_width": candidate.get("measured_width"),
                    "reason": candidate.get("reason"),
                    "tail_line_status": candidate.get("tail_line_status"),
                },
                "selected_break": {
                    "line_text": selected.get("line_text") if selected else None,
                    "remaining_text": selected.get("remaining_text") if selected else None,
                    "break_index": selected.get("break_index") if selected else None,
                    "selection_reason": (
                        selected.get("selection_reason") if selected else None
                    ),
                },
            }
        )
    return examples


def _has_one_character_orphan(lines: list[str]) -> bool:
    return bool(_one_character_orphan_lines(lines))


def _one_character_orphan_lines(lines: list[str]) -> list[str]:
    return [
        line
        for line in lines
        if subtitle_style_spike._visible_char_count(str(line)) == 1
    ]


def _font_bbox_wrap_summary(presentation_items: list[dict[str, Any]]) -> dict[str, Any]:
    readbacks = [
        item.get("font_bbox_wrap_readback") or {}
        for item in presentation_items
        if item.get("font_bbox_wrap_readback")
    ]
    if not readbacks:
        return {
            "wrap_algorithm": {
                "name": subtitle_style_spike.JAPANESE_WRAP_ALGORITHM,
                "source_function": FONT_BBOX_WRAP_SOURCE,
                "authority": FONT_BBOX_WRAP_AUTHORITY,
            },
            "wrapping_authority": FONT_BBOX_WRAP_AUTHORITY,
            "measurement_renderer": "Pillow ImageDraw.multiline_textbbox",
            "proof_renderer": "ffmpeg_subtitles_filter_ass",
            "renderer_gap": _font_bbox_renderer_gap(),
            "status": "no_presentation_items",
            "suffix_tail_prevention_applied_count": 0,
            "suspicious_tail_line_present": False,
            "suspicious_tail_lines": [],
            "items": [],
        }
    first = readbacks[0]
    return {
        "wrap_algorithm": first.get("wrap_algorithm") or {},
        "wrapping_authority": FONT_BBOX_WRAP_AUTHORITY,
        "measurement_renderer": "Pillow ImageDraw.multiline_textbbox",
        "proof_renderer": "ffmpeg_subtitles_filter_ass",
        "renderer_gap": _font_bbox_renderer_gap(),
        "typography_decoration_candidate_id": _single_or_mixed(
            [str(item.get("typography_decoration_candidate_id") or "") for item in readbacks]
        ),
        "style_selection_source": _single_or_mixed(
            [str(item.get("style_selection_source") or "") for item in readbacks]
        ),
        "font_family": _single_or_mixed(
            [str(item.get("font_family") or "") for item in readbacks]
        ),
        "font_file_status": _single_or_mixed(
            [str(item.get("font_file_status") or "") for item in readbacks]
        ),
        "font_fallback_status": _single_or_mixed(
            [str(item.get("font_fallback_status") or "") for item in readbacks]
        ),
        "applied_to_proof_text_count": sum(
            1 for item in readbacks if item.get("applied_to_proof_text") is True
        ),
        "all_renderable_items_applied_to_proof_text": all(
            item.get("applied_to_proof_text") is True for item in readbacks
        ),
        "explicit_line_breaks_passed_to_ass": all(
            item.get("explicit_line_breaks_passed_to_ass") is True
            for item in readbacks
        ),
        "orphan_prevention_applied_count": sum(
            1 for item in readbacks if item.get("orphan_prevention_applied") is True
        ),
        "suffix_tail_prevention_applied_count": sum(
            1 for item in readbacks if item.get("suffix_tail_prevention_applied") is True
        ),
        "suspicious_tail_line_present": any(
            item.get("suspicious_tail_line_present") is True for item in readbacks
        ),
        "one_character_orphan_present": any(
            item.get("one_character_orphan_present") is True for item in readbacks
        ),
        "orphan_prevention_examples": [
            example
            for item in readbacks
            for example in item.get("orphan_prevention_examples") or []
        ][:8],
        "suffix_tail_prevention_examples": [
            example
            for item in readbacks
            for example in item.get("suffix_tail_prevention_examples") or []
        ][:8],
        "suspicious_tail_lines": [
            line
            for item in readbacks
            for line in item.get("suspicious_tail_lines") or []
        ],
        "measured_bbox_provenance": first.get("measured_bbox_provenance") or {},
        "items": [
            {
                "subtitle_id": item.get("subtitle_id"),
                "subtitle_item_status": item.get("subtitle_item_status"),
                "selected_wrapped_lines": item.get("selected_wrapped_lines"),
                "selected_break_reason": item.get("selected_break_reason"),
                "orphan_prevention_applied": item.get("orphan_prevention_applied"),
                "suffix_tail_prevention_applied": item.get("suffix_tail_prevention_applied"),
                "suspicious_tail_line_present": item.get("suspicious_tail_line_present"),
                "suspicious_tail_lines": item.get("suspicious_tail_lines"),
                "one_character_orphan_present": item.get("one_character_orphan_present"),
                "applied_to_proof_text": item.get("applied_to_proof_text"),
                "candidate_break_count": len(item.get("candidate_breaks") or []),
                "candidate_breaks": item.get("candidate_breaks") or [],
            }
            for item in readbacks
        ],
    }


def _bbox_dict(bbox: tuple[int, int, int, int] | None) -> dict[str, int] | None:
    if bbox is None:
        return None
    left, top, right, bottom = bbox
    return {
        "left": int(left),
        "top": int(top),
        "right": int(right),
        "bottom": int(bottom),
        "width": int(right - left),
        "height": int(bottom - top),
    }


def _write_ass(
    path: Path,
    items: list[dict[str, Any]],
    *,
    layout: dict[str, Any],
    review_label: str | None = None,
) -> None:
    style = _layout_style(layout)
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
        (
            f"Style: {ASS_REVIEW_LABEL_STYLE_NAME},Arial,"
            f"{max(18, round(values['font_size'] * 0.28))},"
            "&H00FFFFFF,&H00FFFFFF,&H00333A42,&HCC1F2933,"
            "1,0,0,0,100,100,0,0,"
            "3,2,0,7,0,0,0,1"
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
    if review_label:
        label = _ass_text(review_label)
        label_end = max(
            (float(item.get("display_end_seconds") or 0.0) for item in items),
            default=1.0,
        )
        lines.append(
            f"Dialogue: 20,{_ass_time(0.0)},{_ass_time(label_end)},"
            f"{ASS_REVIEW_LABEL_STYLE_NAME},,0,0,0,,"
            f"{{\\an7\\pos(32,28)}}{label}"
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
                "display_start_seconds": spec.get("display_start_seconds"),
                "display_end_seconds": spec.get("display_end_seconds"),
                "wrapped_line_count": spec.get("wrapped_line_count"),
                "wrapped_lines": spec.get("wrapped_lines"),
                "text": spec.get("text"),
                "selected_break_reason": spec.get("selected_break_reason"),
                "frame_selection_reason": spec.get("frame_selection_reason"),
                "subtitle_bearing_expected": True,
            }
        )
    return extracts


def _render_ed10w_candidate_visuals(
    *,
    source_media: dict[str, Any],
    cut: dict[str, Any],
    renderable_items: list[dict[str, Any]],
    base_layout: dict[str, Any],
    cut_paths: dict[str, Path],
    ffmpeg_path: str,
    ffprobe_path: str | Path | None,
    container: str,
    base: Path,
    runner: ffmpeg_tiny.Runner,
) -> list[dict[str, Any]]:
    cut_id = str(cut.get("id") or "")
    start_seconds = _required_float(cut.get("start_seconds"), f"{cut_id}.start_seconds")
    end_seconds = _required_float(cut.get("end_seconds"), f"{cut_id}.end_seconds")
    duration = round(end_seconds - start_seconds, 3)
    base_style = _layout_style(base_layout)
    base_candidates = _ed10w_bounded_decoration_candidates(
        style={
            "outline": base_layout["values"].get("outline"),
            "shadow": base_layout["values"].get("shadow"),
            "speaker_badge": {"label": base_style.get("speaker_badge_label") or "SPK"},
        }
    )
    visuals: list[dict[str, Any]] = []
    for candidate in base_candidates:
        candidate_number = int(candidate["candidate_number"])
        candidate_id = str(candidate["candidate_id"])
        candidate_style = _ed10w_candidate_ass_style(
            base_style=base_style,
            base_layout=base_layout,
            candidate=candidate,
        )
        layout = _subtitle_layout_contract(
            frame_width=int(base_layout["frame"]["width"]),
            frame_height=int(base_layout["frame"]["height"]),
            mode=str(base_layout["mode"]),
            dimension_source="ed10w_candidate_visual_same_probe_frame",
            diagnostic_ass_style=candidate_style,
        )
        presentation_items = _presentation_items(renderable_items, layout=layout)
        frame_spec = _ed10w_candidate_visual_frame_spec(presentation_items, duration)
        stem = (
            f"{cut_paths['stem']}.ed10w_candidate_"
            f"{candidate_number}_{candidate_id}"
        )
        ass_path = cut_paths["reference_dir"] / f"{stem}.burned_in.ass"
        video_path = cut_paths["reference_dir"] / f"{stem}.{container}"
        frame_path = cut_paths["reference_dir"] / f"{stem}.png"
        review_label = (
            f"Candidate {candidate_number}: {candidate['label']}\n"
            f"{candidate['changes_from_ed10v']}"
        )
        _write_ass(
            ass_path,
            presentation_items,
            layout=layout,
            review_label=review_label,
        )
        render_result = ffmpeg_tiny.render_tiny_proof(
            source_video_path=source_media["source_video"]["resolved_path"],
            source_audio_path=source_media["source_audio"]["resolved_path"],
            output_path=video_path,
            start_seconds=start_seconds,
            duration_seconds=duration,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            container=container,
            subtitle_file_path=ass_path,
            runner=runner,
        )
        extract = _extract_frame(
            video_path=Path(render_result.output_path),
            frame_path=frame_path,
            seconds=float(frame_spec["frame_seconds"]),
            ffmpeg_path=render_result.ffmpeg_path,
            runner=runner,
        )
        crop_images = _extract_ed10w_candidate_crops(
            frame_path=frame_path,
            layout=layout,
            frame_spec=frame_spec,
            presentation_items=presentation_items,
            ffmpeg_path=render_result.ffmpeg_path,
            runner=runner,
            base=base,
        )
        style_delta_readback = _ed10w_candidate_style_delta_readback(
            candidate=candidate,
            base_layout=base_layout,
            base_style=base_style,
            candidate_layout=layout,
            candidate_style=candidate_style,
        )
        visuals.append(
            {
                "candidate_number": candidate_number,
                "candidate_id": candidate_id,
                "label": candidate["label"],
                "changes_from_ed10v": candidate["changes_from_ed10v"],
                "source_cut": cut_id,
                "source_subtitle_id": frame_spec.get("subtitle_id"),
                "frame_seconds": frame_spec.get("frame_seconds"),
                "same_frame_basis": frame_spec.get("frame_selection_reason"),
                "visual_label_baked_in": True,
                "compact_initial_display": True,
                "image_status": extract.get("status"),
                "image_path": _display_path(frame_path, base),
                "video_path": _display_path(Path(render_result.output_path), base),
                "ass_path": _display_path(ass_path, base),
                "crop_images": crop_images,
                "style_delta_readback": style_delta_readback,
                "style_readback": {
                    "outline": layout["values"].get("outline"),
                    "shadow": layout["values"].get("shadow"),
                    "badge_pressure": candidate.get("badge_pressure"),
                    "badge_text_colour": style_delta_readback["actual"].get(
                        "badge_text_colour"
                    ),
                    "badge_text_opacity": style_delta_readback["actual"].get(
                        "badge_text_opacity"
                    ),
                    "badge_background_colour": style_delta_readback["actual"].get(
                        "badge_background_colour"
                    ),
                    "badge_background_opacity": style_delta_readback["actual"].get(
                        "badge_background_opacity"
                    ),
                    "font_family": style_delta_readback["actual"].get("font_family"),
                    "font_size": style_delta_readback["actual"].get("font_size"),
                    "font_family_changed": False,
                },
                "visual_delta_status": style_delta_readback.get(
                    "visual_delta_status"
                ),
                "production_subtitle_design_acceptance": False,
                "production_render_acceptance": False,
                "production_candidate": False,
                "rights_status": "pending",
            }
        )
    return visuals


def _extract_ed10w_candidate_crops(
    *,
    frame_path: Path,
    layout: dict[str, Any],
    frame_spec: dict[str, Any],
    presentation_items: list[dict[str, Any]],
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
    base: Path,
) -> dict[str, Any]:
    crop_specs = _ed10w_candidate_crop_specs(
        layout=layout,
        frame_spec=frame_spec,
        presentation_items=presentation_items,
    )
    crops: dict[str, Any] = {}
    for crop_id, spec in crop_specs.items():
        crop_path = frame_path.with_name(f"{frame_path.stem}.crop_{crop_id}.png")
        extract = _extract_image_crop(
            image_path=frame_path,
            crop_path=crop_path,
            crop=spec["crop"],
            ffmpeg_path=ffmpeg_path,
            runner=runner,
        )
        crops[crop_id] = {
            **extract,
            "label": spec["label"],
            "role": crop_id,
            "image_path": _display_path(crop_path, base),
            "compact_initial_display": True,
        }
    return crops


def _ed10w_candidate_crop_specs(
    *,
    layout: dict[str, Any],
    frame_spec: dict[str, Any],
    presentation_items: list[dict[str, Any]],
) -> dict[str, Any]:
    frame_width = int(layout["frame"]["width"])
    frame_height = int(layout["frame"]["height"])
    values = layout["values"]
    target_subtitle_id = frame_spec.get("subtitle_id")
    target_item = next(
        (
            item
            for item in presentation_items
            if item.get("subtitle_id") == target_subtitle_id
        ),
        presentation_items[0] if presentation_items else {},
    )
    line_count = max(1, int(target_item.get("wrapped_line_count") or 1))
    item_layout = _item_layout(layout, wrapped_line_count=line_count)
    font_size = int(values["font_size"])
    line_height = int(values["line_height"])
    outline = int(values["outline"])
    subtitle_pad_x = max(24, font_size // 2)
    subtitle_pad_y = max(18, font_size // 3 + outline)
    badge_pad_x = max(18, font_size // 3)
    badge_pad_y = max(14, font_size // 4)
    subtitle_crop = _bounded_crop(
        left=int(item_layout["dialogue_x"]) - subtitle_pad_x,
        top=int(item_layout["dialogue_y"]) - subtitle_pad_y,
        right=frame_width - int(values["margin_r"]) + subtitle_pad_x,
        bottom=(
            int(item_layout["dialogue_y"])
            + (line_height * line_count)
            + subtitle_pad_y
        ),
        frame_width=frame_width,
        frame_height=frame_height,
    )
    badge_crop = _bounded_crop(
        left=(
            int(item_layout["badge_center_x"])
            - int(values["badge_width"])
            // 2
            - badge_pad_x
        ),
        top=(
            int(item_layout["badge_center_y"])
            - int(values["badge_height"])
            // 2
            - badge_pad_y
        ),
        right=(
            int(item_layout["badge_center_x"])
            + int(values["badge_width"])
            // 2
            + badge_pad_x
        ),
        bottom=(
            int(item_layout["badge_center_y"])
            + int(values["badge_height"])
            // 2
            + badge_pad_y
        ),
        frame_width=frame_width,
        frame_height=frame_height,
    )
    return {
        "subtitle_body": {
            "label": "subtitle body crop",
            "crop": subtitle_crop,
        },
        "spk_badge": {
            "label": "SPK badge crop",
            "crop": badge_crop,
        },
    }


def _bounded_crop(
    *,
    left: int,
    top: int,
    right: int,
    bottom: int,
    frame_width: int,
    frame_height: int,
) -> dict[str, int]:
    x = max(0, min(frame_width - 1, int(left)))
    y = max(0, min(frame_height - 1, int(top)))
    bounded_right = max(x + 1, min(frame_width, int(right)))
    bounded_bottom = max(y + 1, min(frame_height, int(bottom)))
    return {
        "x": x,
        "y": y,
        "width": bounded_right - x,
        "height": bounded_bottom - y,
    }


def _extract_image_crop(
    *,
    image_path: Path,
    crop_path: Path,
    crop: dict[str, int],
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    crop_path.parent.mkdir(parents=True, exist_ok=True)
    crop_filter = (
        f"crop={int(crop['width'])}:{int(crop['height'])}:"
        f"{int(crop['x'])}:{int(crop['y'])}"
    )
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(image_path),
        "-vf",
        crop_filter,
        "-frames:v",
        "1",
        str(crop_path),
    ]
    result = runner(
        command,
        capture_output=True,
        text=True,
        timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
    )
    return {
        "status": "succeeded"
        if result.returncode == 0 and crop_path.exists()
        else "failed",
        "exit_code": result.returncode,
        "crop": crop,
        "path": str(crop_path).replace("\\", "/"),
        "stderr_digest": ffmpeg_tiny.build_stderr_digest(result.stderr),
    }


def _ed10w_candidate_style_delta_readback(
    *,
    candidate: dict[str, Any],
    base_layout: dict[str, Any],
    base_style: dict[str, Any],
    candidate_layout: dict[str, Any],
    candidate_style: dict[str, Any],
) -> dict[str, Any]:
    baseline = _ed10w_style_parameter_snapshot(base_layout, base_style)
    actual = _ed10w_style_parameter_snapshot(candidate_layout, candidate_style)
    baseline_badge_text_opacity = float(baseline.get("badge_text_opacity") or 0.0)
    actual_badge_text_opacity = float(actual.get("badge_text_opacity") or 0.0)
    baseline_badge_background_opacity = float(
        baseline.get("badge_background_opacity") or 0.0
    )
    actual_badge_background_opacity = float(
        actual.get("badge_background_opacity") or 0.0
    )
    delta = {
        "outline_px": int(actual["outline"] or 0) - int(baseline["outline"] or 0),
        "shadow_px": int(actual["shadow"] or 0) - int(baseline["shadow"] or 0),
        "badge_text_opacity": round(
            actual_badge_text_opacity - baseline_badge_text_opacity,
            3,
        ),
        "badge_background_opacity": round(
            actual_badge_background_opacity - baseline_badge_background_opacity,
            3,
        ),
        "font_family_changed": actual["font_family"] != baseline["font_family"],
        "font_size_px": int(actual["font_size"] or 0) - int(baseline["font_size"] or 0),
    }
    axes: list[str] = []
    if delta["outline_px"] or delta["shadow_px"]:
        axes.append("outline_shadow")
    if delta["badge_text_opacity"] or delta["badge_background_opacity"]:
        axes.append("badge_pressure")
    return {
        "candidate_number": candidate.get("candidate_number"),
        "candidate_id": candidate.get("candidate_id"),
        "label": candidate.get("label"),
        "intended_change": candidate.get("changes_from_ed10v"),
        "baseline": baseline,
        "actual": actual,
        "delta": delta,
        "visual_delta_axes": axes,
        "visual_delta_status": _ed10w_visual_delta_status(
            candidate=candidate,
            delta=delta,
        ),
        "bounded_diagnostic_only": True,
        "production_subtitle_design_acceptance": False,
        "production_render_acceptance": False,
        "rights_status": "pending",
    }


def _ed10w_style_parameter_snapshot(
    layout: dict[str, Any],
    style: dict[str, Any],
) -> dict[str, Any]:
    values = layout["values"]
    badge_text = _ass_colour_readback(style.get("speaker_accent_colour"))
    badge_background = _ass_colour_readback(style.get("speaker_badge_back_colour"))
    return {
        "font_family": style.get("font_name"),
        "font_size": values.get("font_size"),
        "outline": values.get("outline"),
        "shadow": values.get("shadow"),
        "badge_label": style.get("speaker_badge_label"),
        "badge_text_colour": badge_text.get("rgb_hex"),
        "badge_text_ass_colour": badge_text.get("ass_colour"),
        "badge_text_alpha": badge_text.get("alpha"),
        "badge_text_opacity": badge_text.get("opacity"),
        "badge_background_colour": badge_background.get("rgb_hex"),
        "badge_background_ass_colour": badge_background.get("ass_colour"),
        "badge_background_alpha": badge_background.get("alpha"),
        "badge_background_opacity": badge_background.get("opacity"),
    }


def _ass_colour_readback(value: Any) -> dict[str, Any]:
    text = str(value or "").strip()
    if text.startswith("&H") and len(text) == 10:
        try:
            alpha = int(text[2:4], 16)
            blue = int(text[4:6], 16)
            green = int(text[6:8], 16)
            red = int(text[8:10], 16)
        except ValueError:
            return {
                "ass_colour": text,
                "alpha": None,
                "opacity": None,
                "rgb_hex": None,
            }
        return {
            "ass_colour": text,
            "alpha": alpha,
            "opacity": round((255 - alpha) / 255, 3),
            "rgb_hex": f"#{red:02x}{green:02x}{blue:02x}",
        }
    return {
        "ass_colour": text,
        "alpha": None,
        "opacity": None,
        "rgb_hex": None,
    }


def _ed10w_visual_delta_status(
    *,
    candidate: dict[str, Any],
    delta: dict[str, Any],
) -> str:
    if int(candidate.get("candidate_number") or 0) == 0:
        return "not visible"
    outline_visible = abs(int(delta.get("outline_px") or 0)) >= 2
    shadow_visible = abs(int(delta.get("shadow_px") or 0)) >= 1
    badge_visible = (
        abs(float(delta.get("badge_text_opacity") or 0.0)) >= 0.25
        or abs(float(delta.get("badge_background_opacity") or 0.0)) >= 0.2
    )
    if outline_visible or shadow_visible or badge_visible:
        return "visible"
    if any(
        [
            delta.get("outline_px"),
            delta.get("shadow_px"),
            delta.get("badge_text_opacity"),
            delta.get("badge_background_opacity"),
        ]
    ):
        return "subtle"
    return "not visible"


def _ed10w_candidate_visual_frame_spec(
    items: list[dict[str, Any]],
    duration: float,
) -> dict[str, Any]:
    target = next(
        (
            item
            for item in items
            if item.get("subtitle_id") == "sub_096"
            and int(item.get("wrapped_line_count") or 1) >= 2
        ),
        None,
    )
    if target is None:
        target = next(
            (
                item
                for item in items
                if int(item.get("wrapped_line_count") or 1) >= 2
            ),
            None,
        )
    if target is not None:
        start = float(target.get("display_start_seconds") or 0.0)
        end = float(target.get("display_end_seconds") or start)
        frame_seconds = min(max(start + 0.55, 0.05), max(0.05, end - 0.05))
        return {
            "subtitle_id": target.get("subtitle_id"),
            "frame_seconds": round(min(frame_seconds, max(0.05, duration - 0.05)), 3),
            "frame_selection_reason": (
                "same cut_008/sub_096 multiline cue when available"
            ),
        }
    return {
        "subtitle_id": None,
        "frame_seconds": round(_representative_frame_seconds(items, duration), 3),
        "frame_selection_reason": "same representative baseline frame fallback",
    }


def _ed10w_candidate_ass_style(
    *,
    base_style: dict[str, Any],
    base_layout: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    style = copy.deepcopy(base_style)
    candidate_id = str(candidate.get("candidate_id") or "")
    font_size = max(1, int(base_layout["values"].get("font_size") or 1))
    outline = max(2, int(base_layout["values"].get("outline") or 2))
    shadow = max(1, int(base_layout["values"].get("shadow") or 1))
    if candidate_id in {
        ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID,
        ED10W_CANDIDATE3_BALANCED_ID,
    }:
        target_outline = max(1, outline - ED10W_REVIEWABLE_OUTLINE_REDUCTION_PX)
        target_shadow = max(0, shadow - ED10W_REVIEWABLE_SHADOW_REDUCTION_PX)
        style["outline_px_override"] = target_outline
        style["shadow_px_override"] = target_shadow
        style["stroke_ratio"] = target_outline / font_size
        style["shadow_offset_ratio"] = target_shadow / font_size
    if candidate_id in {
        ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
        ED10W_CANDIDATE3_BALANCED_ID,
    }:
        badge_fill = _rgb_from_hex(style.get("badge_fill"), fallback=(236, 70, 88))
        badge_outline = _rgb_from_hex(
            style.get("badge_outline"),
            fallback=(58, 14, 24),
        )
        style["speaker_accent_colour"] = _ass_colour(
            badge_fill,
            alpha=ED10W_REVIEWABLE_BADGE_TEXT_ALPHA,
        )
        style["speaker_badge_back_colour"] = _ass_colour(
            badge_outline,
            alpha=ED10W_REVIEWABLE_BADGE_BACKGROUND_ALPHA,
        )
    return style


def _rgb_from_hex(value: Any, *, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    text = str(value or "").strip()
    if text.startswith("#") and len(text) == 7:
        try:
            return (
                int(text[1:3], 16),
                int(text[3:5], 16),
                int(text[5:7], 16),
            )
        except ValueError:
            return fallback
    return fallback


def _sample_frame_specs(
    items: list[dict[str, Any]],
    duration: float,
    *,
    include_multiline_wrap_evidence: bool = False,
) -> list[dict[str, Any]]:
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

    if include_multiline_wrap_evidence:
        multiline_items = [
            item
            for item in items
            if int(item.get("wrapped_line_count") or 0) > 1
        ][:MAX_MULTILINE_WRAP_EVIDENCE_SAMPLES]
        for index, item in enumerate(multiline_items, start=1):
            candidates.append(
                (
                    f"multiline_wrap_{index}",
                    item,
                    (
                        "font-bbox multiline wrap evidence; this screenshot "
                        "is the dense/stress cue that proves the proof contains "
                        "multi-line subtitle behavior"
                    ),
                )
            )

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
                "wrapped_line_count": item.get("wrapped_line_count"),
                "wrapped_lines": item.get("wrapped_lines"),
                "text": item.get("text"),
                "selected_break_reason": item.get("selected_break_reason"),
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
        json.dump(payload, f, ensure_ascii=True, indent=2)
        f.write("\n")


def _overlay_report_html(report: dict[str, Any]) -> str:
    rows = "\n".join(_overlay_cut_row(item) for item in report.get("cut_results") or [])
    style_summary = _style_summary_html(
        report.get("style_direction") or {},
        report.get("style_parameters") or {},
    )
    proof_focus = _proof_focus_html(report)
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
  <p class="warn">Mode semantics: badge_left_dialogue is the recommended current proof mode for normal speaker-identified dialogue; bottom_center_emphasis is for emphasized dialogue or strong one-liners; reaction_caption is for punchline, surprise, or instant reaction such as 来ねぇ！！; speaker_badge_stack is comparison-only placeholder stack work for future face-icon/nameplate design. Repeated text across modes is intentional comparison, not a universal style rule.</p>
  <p class="warn">SPK/A/B are temporary speaker badge placeholders. They are not real face icons and not production speaker identity design. Real face icon asset intake is a separate future slice.</p>
  <p>episode: {escape(str(report.get("episode_id", "")))}</p>
  <p>target cuts: {escape(", ".join(report.get("target_cuts") or []))}</p>
  <p>rights_status: {escape(str(report.get("rights_status", "")))} / production_candidate: {escape(str(report.get("production_candidate", "")))}</p>
{review_warning}
{proof_focus}
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
    proof_focus = _proof_focus_html(report)
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
  <p class="warn">Mode semantics: badge_left_dialogue is the current proof mode for normal speaker-identified dialogue; bottom_center_emphasis is for emphasized dialogue or strong one-liners; reaction_caption and speaker_badge_stack remain comparison/deferred mode readbacks. Repeated text across modes is intentional comparison, not a universal style rule.</p>
  <p class="warn">SPK/A/B are temporary speaker badge placeholders. They are not real face icons and not production speaker identity design. Real face icon asset intake is a separate future slice.</p>
  <p>episode: {escape(str(report.get("episode_id", "")))}</p>
{review_warning}
{proof_focus}
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


def _subtitle_presentation_review_pack(
    *,
    report: dict[str, Any],
    pack_path: Path,
    pack_html_path: Path,
    base: Path,
) -> dict[str, Any]:
    evidence = _subtitle_presentation_pack_evidence(report)
    artifact_id = str(
        report.get("artifact_id") or "clip-ed10w-subtitle-presentation-review-pack-001"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "report_kind": "subtitle_presentation_review_pack",
        "artifact_id": artifact_id,
        "source_artifact_id": report.get("artifact_id"),
        "source_review_artifact_id": report.get("source_review_artifact_id"),
        "source_previous_artifact_id": report.get("source_previous_artifact_id"),
        "created_at": _now(),
        "episode_id": report.get("episode_id"),
        "axis": (
            "tiny_render_path_nearer_probe"
            if _is_tiny_render_path_probe_profile(report.get("proof_profile"))
            else "bounded_decoration_adjustment + render_path_readiness"
        ),
        "state": _subtitle_presentation_pack_state(report),
        "target_cuts": report.get("target_cuts") or [],
        "review_consumption": _subtitle_presentation_review_consumption(report),
        "lead_fallback_readback": _subtitle_presentation_lead_fallback_readback(report),
        "prior_review": {
            "prior_review_count": "3+",
            "prior_signal_summary": (
                "Keifont normal-dialogue and dense/multiline routes have "
                "passed diagnostic review."
            ),
            "accepted_scope": [
                "diagnostic_representative_review",
                "provisional_normal_dialogue_baseline",
                "diagnostic_dense_stress_pass",
                "diagnostic_multiline_wrap_pass",
            ],
            "not_accepted_scope": [
                "production_subtitle_design",
                "production_render",
                "creative_acceptance",
                "rights",
                "publishing",
                "public_use",
            ],
        },
        "review_card": _subtitle_presentation_review_card(report),
        "operator_observation_card": _subtitle_presentation_operator_observation_card(
            report
        ),
        "bounded_decoration_candidates": _bounded_decoration_candidates(report),
        "candidate_visual_evidence": _subtitle_presentation_candidate_visual_evidence(
            report
        ),
        "candidate_delta_readback": _subtitle_presentation_candidate_delta_readback(
            report
        ),
        "render_path_readiness": _render_path_decision_card(report),
        "evidence": evidence,
        "outputs": {
            "json": _display_path(pack_path, base),
            "html": _display_path(pack_html_path, base),
            "source_focused_review_html": (
                report.get("outputs") or {}
            ).get("focused_review_html"),
        },
        "production_subtitle_design_acceptance": False,
        "production_render_acceptance": False,
        "creative_acceptance": False,
        "rights_status": "pending",
        "production_candidate": False,
        "production_usage_allowed": False,
        "publishing_acceptance": False,
        "public_use_permission": False,
    }


def _subtitle_presentation_pack_state(report: dict[str, Any]) -> str:
    if _is_tiny_render_path_probe_profile(report.get("proof_profile")):
        return "tiny_render_path_nearer_probe_ready"
    if report.get("proof_profile") == ED10Y_CANDIDATE2_CARRY_FORWARD_PROFILE:
        return "candidate2_carry_forward_ready"
    return "one_pass_review_pending"


def _subtitle_presentation_review_consumption(report: dict[str, Any]) -> dict[str, Any]:
    if not _is_candidate2_lead_probe_profile(report.get("proof_profile")):
        return {
            "latest_review_consumed": False,
            "user_review_required_now": True,
            "same_candidate_comparison_review_allowed": True,
        }
    review_memory = report.get("review_memory") or {}
    return {
        "latest_review_consumed": True,
        "source_review": review_memory.get("latest_freeform_review_summary"),
        "lead_candidate": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
        "fallback_reference": ED10W_CANDIDATE0_BASELINE_ID,
        "held_references": [
            ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID,
            ED10W_CANDIDATE3_BALANCED_ID,
        ],
        "user_review_required_now": False,
        "same_candidate_comparison_review_allowed": False,
        "review_card_reemitted": False,
        "tiny_render_path_nearer_probe_completed": _is_tiny_render_path_probe_profile(
            report.get("proof_profile")
        ),
    }


def _subtitle_presentation_lead_fallback_readback(
    report: dict[str, Any],
) -> dict[str, Any]:
    if not _is_candidate2_lead_probe_profile(report.get("proof_profile")):
        return {
            "lead_candidate": None,
            "fallback_reference": None,
            "held_references": [],
            "status": "not_promoted_yet",
        }
    return {
        "status": (
            "candidate2_promoted_to_tiny_render_path_nearer_probe_lead"
            if _is_tiny_render_path_probe_profile(report.get("proof_profile"))
            else "candidate2_promoted_to_provisional_bounded_decoration_lead"
        ),
        "lead_candidate": {
            "candidate_number": 2,
            "candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
            "label": "SPK badge / label pressure adjustment",
            "reason": "latest review says Candidate 0 and Candidate 2 are acceptable/good",
        },
        "fallback_reference": {
            "candidate_number": 0,
            "candidate_id": ED10W_CANDIDATE0_BASELINE_ID,
            "label": "current passed baseline reference",
            "reason": "latest review keeps Candidate 0 acceptable as fallback/reference",
        },
        "held_references": [
            {
                "candidate_number": 1,
                "candidate_id": ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID,
                "reason": "too_thin_compared_with_0_and_2",
            },
            {
                "candidate_number": 3,
                "candidate_id": ED10W_CANDIDATE3_BALANCED_ID,
                "reason": "too_thin_compared_with_0_and_2",
            },
        ],
    }


def _subtitle_presentation_review_card(report: dict[str, Any]) -> dict[str, Any]:
    artifact_id = str(
        report.get("artifact_id") or "clip-ed10w-subtitle-presentation-review-pack-001"
    )
    if _is_candidate2_lead_probe_profile(report.get("proof_profile")):
        is_ed10z = _is_tiny_render_path_probe_profile(report.get("proof_profile"))
        return {
            "target": artifact_id,
            "status": "withheld_latest_review_already_consumed",
            "action_type": "NO_REVIEW_CARD_REVIEW_CONSUMED",
            "axis": (
                "tiny_render_path_nearer_probe"
                if is_ed10z
                else "candidate2_carry_forward + render_path_nearer_probe"
            ),
            "reason": (
                "Candidate 2 has already been carried forward and this ED-10z "
                "surface only records the tiny render-path-nearer probe; "
                "repeating the same Candidate 0-3 review is disallowed."
                if is_ed10z
                else "The latest freeform review already selected Candidate 2 as "
                "lead and kept Candidate 0 as fallback; repeating the same "
                "Candidate 0-3 review is disallowed."
            ),
            "not_asking": [
                "Candidate 0-3 comparison review",
                "general Keifont acceptance",
                "cut_002 / cut_003 review",
                "same cut_008 dense/multiline pass",
                "production subtitle design acceptance",
            ],
            "input_mode": "none",
            "completion_signal": "review memory consumed; proceed from Candidate 2 lead",
        }
    return {
        "target": artifact_id,
        "status": "emitted_nonredundant_new_axis",
        "action_type": "ONE_REVIEW_CARD_NEW_AXIS",
        "axis": "bounded_decoration_adjustment + render_path_readiness",
        "prior_review_count": "3+",
        "prior_signal_summary": (
            "Keifont normal-dialogue and dense/multiline route passed "
            "diagnostically."
        ),
        "what_changed": (
            "Candidate deltas are now reviewable with compact subtitle/body "
            "crops, SPK badge crops, and actual style delta readback; the "
            "render-path readiness decision card remains diagnostic."
        ),
        "what_this_review_decides": [
            "whether Candidate 0 current baseline remains best",
            "whether Candidate 1 lighter outline/shadow is preferable",
            "whether Candidate 2 badge pressure adjustment is preferable",
            "whether Candidate 3 combined adjustment is preferable",
            "whether render-path probe should proceed after this",
        ],
        "not_asking": [
            "general Keifont acceptance",
            "cut_002 / cut_003 review",
            "same cut_008 dense/multiline pass",
            "production subtitle design acceptance",
        ],
        "input_mode": "freeform",
        "completion_signal": (
            "user chooses pass, an adjustment candidate, a render-path next "
            "route, or names a concern"
        ),
    }


def _subtitle_presentation_operator_observation_card(
    report: dict[str, Any],
) -> dict[str, Any]:
    if not _is_candidate2_lead_probe_profile(report.get("proof_profile")):
        return {
            "status": "not_needed_review_card_emitted",
            "reason": "ED-10w still needs one bounded presentation review.",
        }
    is_ed10z = _is_tiny_render_path_probe_profile(report.get("proof_profile"))
    return {
        "status": "no_user_action_required",
        "reason": (
            "Latest user review is already consumed; this ED-10z surface records "
            "the tiny diagnostic render-path-nearer probe, not another decision "
            "request."
            if is_ed10z
            else "Latest user review is already consumed; this surface is a "
            "carry-forward/readback and tiny diagnostic probe, not another "
            "Candidate 0-3 review request."
        ),
        "observe": [
            "Candidate 2 is the provisional bounded-decoration lead",
            "Candidate 0 remains fallback/reference",
            "Candidate 1 and Candidate 3 are held because they read too thin",
            "production/public/rights gates remain closed",
        ],
    }


def _subtitle_presentation_candidate_visual_evidence(
    report: dict[str, Any],
) -> list[dict[str, Any]]:
    cut_results = (
        report.get("cut_results") if isinstance(report.get("cut_results"), list) else []
    )
    if not cut_results:
        return []
    artifacts = cut_results[0].get("generated_artifacts") or {}
    visuals = artifacts.get("ed10w_candidate_visuals") or []
    return [
        _with_ed10y_candidate_role(item, report=report)
        for item in visuals
        if isinstance(item, dict)
    ]


def _subtitle_presentation_candidate_delta_readback(
    report: dict[str, Any],
) -> list[dict[str, Any]]:
    visuals = _subtitle_presentation_candidate_visual_evidence(report)
    return [
        _with_ed10y_candidate_role(item["style_delta_readback"], report=report)
        for item in visuals
        if isinstance(item.get("style_delta_readback"), dict)
    ]


def _subtitle_presentation_pack_evidence(report: dict[str, Any]) -> dict[str, Any]:
    cut_results = (
        report.get("cut_results") if isinstance(report.get("cut_results"), list) else []
    )
    cut = cut_results[0] if cut_results else {}
    artifacts = cut.get("generated_artifacts") if isinstance(cut, dict) else {}
    multiline = report.get("multiline_wrap_evidence") or {}
    first_wrap: dict[str, Any] = {}
    per_cut = (
        multiline.get("per_cut") if isinstance(multiline.get("per_cut"), dict) else {}
    )
    for cut_evidence in per_cut.values():
        if not isinstance(cut_evidence, dict):
            continue
        items = cut_evidence.get("evidence_items") or []
        if items:
            first_wrap = items[0]
            break
    return {
        "source_cut": cut.get("cut_id") if isinstance(cut, dict) else None,
        "baseline_frame": artifacts.get("frame") if isinstance(artifacts, dict) else None,
        "baseline_video": artifacts.get("video") if isinstance(artifacts, dict) else None,
        "multiline_screenshot": first_wrap.get("screenshot_path"),
        "multiline_subtitle_id": first_wrap.get("subtitle_id"),
        "multiline_timing": {
            "display_start_seconds": first_wrap.get("display_start_seconds"),
            "display_end_seconds": first_wrap.get("display_end_seconds"),
            "screenshot_frame_seconds": first_wrap.get("screenshot_frame_seconds"),
        },
        "wrapped_lines": first_wrap.get("wrapped_lines") or [],
        "selected_break_reason": first_wrap.get("selected_break_reason"),
        "multiline_wrap_evidence_status": multiline.get("status"),
    }


def _bounded_decoration_candidates(report: dict[str, Any]) -> list[dict[str, Any]]:
    style = report.get("style_parameters") or {}
    return [
        _with_ed10y_candidate_role(candidate, report=report)
        for candidate in _ed10w_bounded_decoration_candidates(style=style)
    ]


def _with_ed10y_candidate_role(
    item: dict[str, Any],
    *,
    report: dict[str, Any],
) -> dict[str, Any]:
    if not _is_candidate2_lead_probe_profile(report.get("proof_profile")):
        return item
    candidate_number = int(item.get("candidate_number") or 0)
    role = _ed10y_candidate_role(candidate_number)
    updated = copy.deepcopy(item)
    updated.update(role)
    return updated


def _ed10y_candidate_role(candidate_number: int) -> dict[str, Any]:
    roles = {
        0: {
            "role_in_current_path": "fallback_reference",
            "current_path_status": "retained_as_acceptable_fallback",
            "review_consumed_reason": "Candidate 0 is acceptable/good but no longer the lead",
            "display_priority": 2,
        },
        1: {
            "role_in_current_path": "held_reference",
            "current_path_status": "held_too_thin_for_current_path",
            "review_consumed_reason": "Candidate 1 looked too thin compared with 0 and 2",
            "display_priority": 3,
        },
        2: {
            "role_in_current_path": "provisional_bounded_decoration_lead",
            "current_path_status": "promoted_to_candidate2_lead",
            "review_consumed_reason": "Candidate 2 is acceptable/good and carries the badge-pressure adjustment forward",
            "display_priority": 1,
        },
        3: {
            "role_in_current_path": "held_reference",
            "current_path_status": "held_too_thin_for_current_path",
            "review_consumed_reason": "Candidate 3 looked too thin compared with 0 and 2",
            "display_priority": 4,
        },
    }
    return roles.get(
        candidate_number,
        {
            "role_in_current_path": "unknown",
            "current_path_status": "unknown",
            "review_consumed_reason": "",
            "display_priority": 99,
        },
    )


def _ed10w_bounded_decoration_candidates(
    *,
    style: dict[str, Any],
) -> list[dict[str, Any]]:
    outline_raw = style.get("outline")
    shadow_raw = style.get("shadow")
    outline = (
        outline_raw.get("value")
        if isinstance(outline_raw, dict)
        else outline_raw
    )
    shadow = (
        shadow_raw.get("value")
        if isinstance(shadow_raw, dict)
        else shadow_raw
    )
    badge = (style.get("speaker_badge") or {}).get("label") or "SPK"
    return [
        {
            "candidate_number": 0,
            "candidate_id": ED10W_CANDIDATE0_BASELINE_ID,
            "label": "Current passed baseline reference",
            "changes_from_ed10v": "none",
            "outline_pressure": "current",
            "shadow_pressure": "current",
            "badge_pressure": "current",
            "font_family_changed": False,
            "deterministic": True,
            "recommended_when": "current pass already feels balanced",
            "readback": {"outline": outline, "shadow": shadow, "badge_label": badge},
        },
        {
            "candidate_number": 1,
            "candidate_id": ED10W_CANDIDATE1_LIGHTER_OUTLINE_ID,
            "label": "Lighter outline / shadow pressure",
            "changes_from_ed10v": (
                "reduce outline by two bounded pixels and shadow by one bounded pixel "
                "for reviewable diagnostic contrast"
            ),
            "outline_pressure": "reviewably_lighter",
            "shadow_pressure": "reviewably_lighter",
            "badge_pressure": "current",
            "font_family_changed": False,
            "deterministic": True,
            "recommended_when": (
                "current baseline feels a little heavy or black-pressure dominant"
            ),
            "readback": {
                "outline_delta_px": -ED10W_REVIEWABLE_OUTLINE_REDUCTION_PX,
                "shadow_delta_px": -ED10W_REVIEWABLE_SHADOW_REDUCTION_PX,
            },
        },
        {
            "candidate_number": 2,
            "candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
            "label": "SPK badge / label pressure adjustment",
            "changes_from_ed10v": (
                "keep subtitle text treatment and visibly reduce placeholder badge "
                "text/background pressure"
            ),
            "outline_pressure": "current",
            "shadow_pressure": "current",
            "badge_pressure": "reviewably_lighter_placeholder",
            "font_family_changed": False,
            "deterministic": True,
            "recommended_when": "text is acceptable but SPK placeholder draws too much attention",
            "readback": {
                "badge_label": badge,
                "badge_text_alpha": ED10W_REVIEWABLE_BADGE_TEXT_ALPHA,
                "badge_background_alpha": ED10W_REVIEWABLE_BADGE_BACKGROUND_ALPHA,
            },
        },
        {
            "candidate_number": 3,
            "candidate_id": ED10W_CANDIDATE3_BALANCED_ID,
            "label": "Balanced combined low-risk adjustment",
            "changes_from_ed10v": (
                "combine reviewably lighter outline/shadow with visibly lighter "
                "placeholder badge pressure"
            ),
            "outline_pressure": "reviewably_lighter",
            "shadow_pressure": "reviewably_lighter",
            "badge_pressure": "reviewably_lighter_placeholder",
            "font_family_changed": False,
            "deterministic": True,
            "recommended_when": (
                "both outline pressure and placeholder badge pressure feel slightly high"
            ),
            "readback": {
                "outline_delta_px": -ED10W_REVIEWABLE_OUTLINE_REDUCTION_PX,
                "shadow_delta_px": -ED10W_REVIEWABLE_SHADOW_REDUCTION_PX,
                "badge_text_alpha": ED10W_REVIEWABLE_BADGE_TEXT_ALPHA,
                "badge_background_alpha": ED10W_REVIEWABLE_BADGE_BACKGROUND_ALPHA,
            },
        },
    ]


def _render_path_decision_card(report: dict[str, Any]) -> dict[str, Any]:
    renderer = report.get("renderer_path_audit") or {}
    if _is_candidate2_lead_probe_profile(report.get("proof_profile")):
        is_ed10z = _is_tiny_render_path_probe_profile(report.get("proof_profile"))
        lead_visual = next(
            (
                item
                for item in _subtitle_presentation_candidate_visual_evidence(report)
                if int(item.get("candidate_number") or 0) == 2
            ),
            {},
        )
        return {
            "status": (
                "ed10z_tiny_render_path_nearer_probe_completed"
                if is_ed10z
                else "candidate2_tiny_render_path_nearer_diagnostic_probe_completed"
            ),
            "safe_existing_path_available": True,
            "current_renderer_path": (
                renderer.get("renderer_path") or "ffmpeg_libass_diagnostic_overlay"
            ),
            "recommended_minimal_next_route": (
                "separate_production_limitation_lift_or_final_render_path_route"
                if is_ed10z
                else "candidate2_probe_completed_no_production_claim"
            ),
            "artifact_id": report.get("artifact_id"),
            "source_previous_artifact_id": report.get("source_previous_artifact_id"),
            "candidate2_probe": {
                "candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
                "source_cut": lead_visual.get("source_cut"),
                "source_subtitle_id": lead_visual.get("source_subtitle_id"),
                "video_path": lead_visual.get("video_path"),
                "image_path": lead_visual.get("image_path"),
                "crop_images": lead_visual.get("crop_images") or {},
                "image_status": lead_visual.get("image_status"),
                "style_delta_readback": lead_visual.get("style_delta_readback") or {},
            },
            "next_route": (
                "open_separate_scope_for_limitation_lift_or_final_render_path_only"
                if is_ed10z
                else "production_limitation_lift_or_final_render_path_probe_only_after_explicit_acceptance"
            ),
            "explicitly_not_accepted": [
                "production subtitle design acceptance",
                "production render acceptance",
                "creative acceptance",
                "rights clearance",
                "publishing acceptance",
                "public-use permission",
            ],
        }
    return {
        "status": "decision_card_included_no_production_claim",
        "safe_existing_path_available": True,
        "current_renderer_path": (
            renderer.get("renderer_path") or "ffmpeg_libass_diagnostic_overlay"
        ),
        "recommended_minimal_next_route": "tiny_final_path_nearer_diagnostic_probe",
        "candidate_routes": [
            {
                "route_id": "reuse_current_ffmpeg_libass_probe",
                "what_it_would_prove": (
                    "diagnostic overlay timing, line breaks, and exported "
                    "frame/video readback remain stable"
                ),
                "not_accepted": "production render acceptance",
            },
            {
                "route_id": "nle_or_ymm4_path_probe_later",
                "what_it_would_prove": (
                    "whether the accepted policy survives the intended editor/render path"
                ),
                "not_accepted": "upload, publishing, public use, or rights approval",
            },
        ],
        "explicitly_not_accepted": [
            "production subtitle design acceptance",
            "production render acceptance",
            "creative acceptance",
            "rights clearance",
            "publishing acceptance",
            "public-use permission",
        ],
    }


def _subtitle_presentation_review_pack_html(pack: dict[str, Any]) -> str:
    evidence = pack.get("evidence") or {}
    candidates = pack.get("bounded_decoration_candidates") or []
    candidate_visuals = pack.get("candidate_visual_evidence") or []
    candidate_delta_readback = pack.get("candidate_delta_readback") or []
    review_card = pack.get("review_card") or {}
    render_card = pack.get("render_path_readiness") or {}
    pack_state = str(pack.get("state") or "")
    if pack_state == "tiny_render_path_nearer_probe_ready":
        title = "Tiny Render-Path Nearer Probe"
    elif pack_state == "candidate2_carry_forward_ready":
        title = "Candidate 2 Carry-Forward Pack"
    else:
        title = "Subtitle Presentation Review Pack"
    baseline_frame = evidence.get("baseline_frame")
    multiline_frame = evidence.get("multiline_screenshot")
    candidate_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('candidate_number') if item.get('candidate_number') is not None else ''))}</td>"
        f"<td>{escape(str(item.get('candidate_id') or ''))}</td>"
        f"<td>{escape(str(item.get('label') or ''))}</td>"
        f"<td>{escape(str(item.get('changes_from_ed10v') or ''))}</td>"
        f"<td>{escape(str(item.get('recommended_when') or ''))}</td>"
        "</tr>"
        for item in candidates
    )
    not_asking = "\n".join(
        f"<li>{escape(str(item))}</li>" for item in review_card.get("not_asking") or []
    )
    decides = "\n".join(
        f"<li>{escape(str(item))}</li>"
        for item in review_card.get("what_this_review_decides") or []
    )
    routes = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('route_id') or ''))}</td>"
        f"<td>{escape(str(item.get('what_it_would_prove') or ''))}</td>"
        f"<td>{escape(str(item.get('not_accepted') or ''))}</td>"
        "</tr>"
        for item in render_card.get("candidate_routes") or []
    )
    baseline_img = (
        f'<a href="{_artifact_href(baseline_frame)}"><img class="proof" src="{_artifact_href(baseline_frame)}" alt="baseline frame"></a>'
        if baseline_frame
        else "<p>No baseline frame recorded.</p>"
    )
    multiline_img = (
        f'<a href="{_artifact_href(multiline_frame)}"><img class="proof compact" src="{_artifact_href(multiline_frame)}" alt="multiline wrap evidence"></a>'
        if multiline_frame
        else "<p>No multiline screenshot recorded.</p>"
    )
    wrapped_lines = "<br>".join(
        escape(str(line)) for line in evidence.get("wrapped_lines") or []
    )
    candidate_visual_grid = _subtitle_presentation_candidate_visuals_html(
        candidate_visuals
    )
    candidate_visual_intro = _subtitle_presentation_candidate_visual_intro(pack)
    candidate_delta_rows = _subtitle_presentation_candidate_delta_readback_html(
        candidate_delta_readback
    )
    review_action_section = _subtitle_presentation_review_action_section_html(pack)
    lead_summary = _subtitle_presentation_lead_summary_html(pack)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; line-height: 1.5; color: #1f2933; background: #f7f8fa; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #d8dde6; border-radius: 8px; padding: 16px; margin: 0 0 16px; }}
    .hero {{ border-left: 6px solid #2f6f9f; }}
    .warning {{ color: #8a4b00; }}
    .evidence-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
    .proof {{ max-width: 480px; width: 100%; border: 1px solid #c7ced8; display: block; }}
    .compact {{ max-width: 220px; }}
    .lead-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; align-items: start; }}
    .lead-tile {{ border-left: 5px solid #306c46; background: #f8fcf9; padding: 10px; }}
    .candidate-visual-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; align-items: start; }}
    .candidate-visual {{ margin: 0; padding: 8px; border-left: 4px solid #2f6f9f; background: #fbfcfe; }}
    .candidate-visual.provisional_bounded_decoration_lead {{ border-left-color: #306c46; background: #f8fcf9; }}
    .candidate-visual.fallback_reference {{ border-left-color: #6b7280; }}
    .candidate-visual.held_reference {{ border-left-color: #b7791f; background: #fffaf0; }}
    .candidate-visual h3 {{ margin: 0 0 6px; font-size: 16px; line-height: 1.3; }}
    .candidate-crop-grid {{ display: grid; grid-template-columns: repeat(2, minmax(110px, 1fr)); gap: 8px; align-items: start; }}
    .candidate-crop {{ max-width: 100%; width: 100%; border: 1px solid #c7ced8; display: block; background: #fff; }}
    .candidate-proof {{ max-width: 720px; width: 100%; border: 1px solid #c7ced8; display: block; }}
    .candidate-change {{ margin: 6px 0 0; font-size: 12px; color: #52616f; }}
    .secondary-frame {{ margin-top: 8px; }}
    .delta-status {{ font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d8dde6; padding: 8px; vertical-align: top; }}
    th {{ background: #eef2f6; text-align: left; }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>{escape(title)}</h1>
    <p>Artifact: {escape(str(pack.get("artifact_id") or ""))}</p>
    <p>Axis: {escape(str(pack.get("axis") or ""))}</p>
    <p class="warning">Diagnostic review only. This page does not approve production subtitle design, production render, creative use, rights, publishing, or public use.</p>
  </section>
{review_action_section}
{lead_summary}
  <section>
    <h2>Evidence</h2>
    <div class="evidence-grid">
      <figure>{baseline_img}<figcaption>Current passed baseline frame</figcaption></figure>
      <figure>{multiline_img}<figcaption>{escape(str(evidence.get("multiline_subtitle_id") or ""))}: {wrapped_lines}</figcaption></figure>
    </div>
  </section>
  <section>
    <h2>Candidate Visual Evidence</h2>
    <p>{escape(candidate_visual_intro)}</p>
    <div class="candidate-visual-grid">
{candidate_visual_grid}
    </div>
  </section>
  <section>
    <h2>Candidate Delta Readback</h2>
    <table>
      <tr><th>#</th><th>intended change</th><th>actual outline / shadow delta</th><th>badge opacity delta</th><th>font</th><th>visual delta status</th></tr>
{candidate_delta_rows}
    </table>
  </section>
  <section>
    <h2>Bounded Decoration Candidates</h2>
    <table>
      <tr><th>#</th><th>candidate</th><th>label</th><th>change</th><th>use when</th></tr>
{candidate_rows}
    </table>
  </section>
  <section>
    <h2>Render Path Decision Card</h2>
    <p>Status: {escape(str(render_card.get("status") or ""))}</p>
    <p>Recommended next route: {escape(str(render_card.get("recommended_minimal_next_route") or ""))}</p>
    <table>
      <tr><th>route</th><th>what it would prove</th><th>not accepted</th></tr>
{routes}
    </table>
  </section>
</main>
</body>
</html>
"""


def _subtitle_presentation_review_action_section_html(pack: dict[str, Any]) -> str:
    review_card = pack.get("review_card") or {}
    not_asking = "\n".join(
        f"<li>{escape(str(item))}</li>" for item in review_card.get("not_asking") or []
    )
    if _is_candidate2_lead_probe_state(pack.get("state")):
        observation = pack.get("operator_observation_card") or {}
        observe = "\n".join(
            f"<li>{escape(str(item))}</li>" for item in observation.get("observe") or []
        )
        return f"""  <section>
    <h2>Review Consumed / Operator Observation</h2>
    <p><strong>Status:</strong> {escape(str(review_card.get("status") or ""))}</p>
    <p>{escape(str(review_card.get("reason") or observation.get("reason") or ""))}</p>
    <h3>Current readback</h3>
    <ul>{observe}</ul>
    <h3>Not asking</h3>
    <ul>{not_asking}</ul>
  </section>"""
    decides = "\n".join(
        f"<li>{escape(str(item))}</li>"
        for item in review_card.get("what_this_review_decides") or []
    )
    return f"""  <section>
    <h2>Non-Redundant Review Card</h2>
    <p><strong>What changed:</strong> {escape(str(review_card.get("what_changed") or ""))}</p>
    <p><strong>Completion signal:</strong> {escape(str(review_card.get("completion_signal") or ""))}</p>
    <h3>This review decides</h3>
    <ul>{decides}</ul>
    <h3>Not asking</h3>
    <ul>{not_asking}</ul>
  </section>"""


def _subtitle_presentation_lead_summary_html(pack: dict[str, Any]) -> str:
    if not _is_candidate2_lead_probe_state(pack.get("state")):
        return ""
    readback = pack.get("lead_fallback_readback") or {}
    visuals = {
        int(item.get("candidate_number") or 0): item
        for item in pack.get("candidate_visual_evidence") or []
        if isinstance(item, dict)
    }
    lead = readback.get("lead_candidate") or {}
    fallback = readback.get("fallback_reference") or {}
    held = readback.get("held_references") or []
    held_items = "\n".join(
        "<li>"
        f"Candidate {escape(str(item.get('candidate_number')))} / "
        f"{escape(str(item.get('candidate_id') or ''))}: "
        f"{escape(str(item.get('reason') or ''))}"
        "</li>"
        for item in held
        if isinstance(item, dict)
    )
    return f"""  <section>
    <h2>Candidate 2 Lead / Candidate 0 Fallback</h2>
    <div class="lead-grid">
{_subtitle_presentation_lead_tile_html(lead, visuals.get(2), role="Lead")}
{_subtitle_presentation_lead_tile_html(fallback, visuals.get(0), role="Fallback")}
    </div>
    <h3>Held references</h3>
    <ul>{held_items}</ul>
  </section>"""


def _subtitle_presentation_lead_tile_html(
    readback: dict[str, Any],
    visual: dict[str, Any] | None,
    *,
    role: str,
) -> str:
    crop_images = (visual or {}).get("crop_images") or {}
    crops = _subtitle_presentation_candidate_crop_images_html(crop_images)
    return (
        '      <article class="lead-tile">'
        f"<h3>{escape(role)}: Candidate {escape(str(readback.get('candidate_number') or ''))}</h3>"
        f"<p>{escape(str(readback.get('label') or readback.get('candidate_id') or ''))}</p>"
        f"<p class=\"candidate-change\">{escape(str(readback.get('reason') or ''))}</p>"
        f"{crops}"
        "</article>"
    )


def _subtitle_presentation_candidate_visual_intro(pack: dict[str, Any]) -> str:
    if pack.get("state") == "tiny_render_path_nearer_probe_ready":
        return (
            "Candidate 2 is the lead treatment passed through the current "
            "diagnostic render path. Candidate 0 remains fallback/reference; "
            "Candidate 1 and Candidate 3 stay held from the consumed review."
        )
    if pack.get("state") == "candidate2_carry_forward_ready":
        return (
            "Candidate 2 is the lead treatment and Candidate 0 is the fallback "
            "reference. Compact crops are shown first; full-frame context is "
            "available at a larger size inside each details block."
        )
    return (
        "Same cut/cue comparison for the bounded decoration candidates. Compact "
        "crops are the default evidence; full-frame context stays behind "
        "click-through detail."
    )


def _subtitle_presentation_candidate_visuals_html(
    candidate_visuals: list[dict[str, Any]],
) -> str:
    if not candidate_visuals:
        return (
            '<p class="warning">Candidate visual evidence was not generated. '
            "Bounded decoration candidates still require image evidence before "
            "one-pass review acceptance.</p>"
        )
    cards: list[str] = []
    for item in sorted(
        candidate_visuals,
        key=lambda visual: (
            int(visual.get("display_priority") or 100),
            int(visual.get("candidate_number") or 0),
        ),
    ):
        candidate_number = item.get("candidate_number")
        label = str(item.get("label") or "")
        change = str(item.get("changes_from_ed10v") or "")
        role = str(item.get("role_in_current_path") or "")
        current_path_status = str(item.get("current_path_status") or "")
        role_class = f" {role}" if role else ""
        image_path = item.get("image_path")
        image_html = (
            f'<a href="{_artifact_href(image_path)}"><img class="candidate-proof" '
            f'src="{_artifact_href(image_path)}" '
            f'alt="Candidate {escape(str(candidate_number))}: {escape(label)}"></a>'
            if image_path
            else "<p>No candidate screenshot recorded.</p>"
        )
        crop_images = item.get("crop_images") if isinstance(item.get("crop_images"), dict) else {}
        crop_html = _subtitle_presentation_candidate_crop_images_html(crop_images)
        cue = item.get("source_subtitle_id") or "representative frame"
        cards.append(
            f"      <article class=\"candidate-visual{escape(role_class)}\">"
            f"<h3>Candidate {escape(str(candidate_number))}: {escape(label)}</h3>"
            f"{crop_html}"
            f"<p class=\"candidate-change\">{escape(current_path_status)}</p>"
            f"<p class=\"candidate-change\">{escape(str(cue))} / {escape(str(item.get('same_frame_basis') or 'same frame comparison'))}</p>"
            f"<p class=\"candidate-change\">{escape(change)}</p>"
            "<details class=\"secondary-frame\"><summary>Full-frame context</summary>"
            f"{image_html}"
            "</details>"
            "</article>"
        )
    return "\n".join(cards)


def _subtitle_presentation_candidate_crop_images_html(
    crop_images: dict[str, Any],
) -> str:
    if not crop_images:
        return "<p>No compact crops recorded.</p>"
    chunks = ['<div class="candidate-crop-grid">']
    for crop_id in ("subtitle_body", "spk_badge"):
        crop = crop_images.get(crop_id) or {}
        image_path = crop.get("image_path")
        label = crop.get("label") or crop_id
        if image_path:
            href = _artifact_href(image_path)
            chunks.append(
                "<figure>"
                f'<a href="{href}"><img class="candidate-crop" '
                f'src="{href}" alt="{escape(str(label))}"></a>'
                f"<figcaption>{escape(str(label))}</figcaption>"
                "</figure>"
            )
        else:
            chunks.append(
                "<figure>"
                "<p>No crop image.</p>"
                f"<figcaption>{escape(str(label))}</figcaption>"
                "</figure>"
            )
    chunks.append("</div>")
    return "".join(chunks)


def _subtitle_presentation_candidate_delta_readback_html(
    readbacks: list[dict[str, Any]],
) -> str:
    if not readbacks:
        return (
            '<tr><td colspan="6">No candidate delta readback was recorded.</td></tr>'
        )
    rows: list[str] = []
    for item in sorted(
        readbacks,
        key=lambda readback: int(readback.get("candidate_number") or 0),
    ):
        delta = item.get("delta") if isinstance(item.get("delta"), dict) else {}
        actual = item.get("actual") if isinstance(item.get("actual"), dict) else {}
        rows.append(
            "<tr>"
            f"<td>{escape(str(item.get('candidate_number')))}</td>"
            f"<td>{escape(str(item.get('intended_change') or ''))}</td>"
            f"<td>outline {escape(str(delta.get('outline_px')))}px / shadow {escape(str(delta.get('shadow_px')))}px</td>"
            f"<td>text {escape(str(delta.get('badge_text_opacity')))} / background {escape(str(delta.get('badge_background_opacity')))}</td>"
            f"<td>{escape(str(actual.get('font_family') or ''))} / {escape(str(actual.get('font_size') or ''))}px</td>"
            f"<td><span class=\"delta-status\">{escape(str(item.get('visual_delta_status') or ''))}</span></td>"
            "</tr>"
        )
    return "\n".join(rows)


def _focused_current_proof_html(report: dict[str, Any]) -> str:
    proof_focus = _proof_focus_html(report)
    multiline_evidence = _focused_multiline_wrap_evidence_html(report)
    cut_evidence = _focused_cut_evidence_html(report)
    detail_links = _focused_detail_links_html(report)
    style = report.get("style_parameters") or {}
    font_name = style.get("font_name") or {}
    font_route = style.get("font_family_route") or {}
    aggregate = report.get("aggregate_summary") or {}
    focus = report.get("focused_proof_review") or {}
    focus_target = focus.get("target") if isinstance(focus, dict) else None
    intro = (
        f"Use this page for {focus_target}. Detailed diagnostic tables are linked below, not used as the first review surface."
        if focus_target
        else "Use this page for the current focused proof review. Detailed diagnostic tables are linked below, not used as the first review surface."
    )
    font_evidence_warning = _font_visual_evidence_warning_html(report)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Current Proof Focused Review</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; line-height: 1.5; color: #1f2933; background: #f7f8fa; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin-top: 0; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; }}
    th, td {{ border: 1px solid #d8dde6; padding: 8px; vertical-align: top; }}
    th {{ background: #eef2f6; text-align: left; }}
    .hero, .review-focus, .evidence, .wrap-evidence, .details, .boundary {{ background: #fff; border: 1px solid #d8dde6; border-radius: 8px; padding: 16px; margin: 0 0 16px; }}
    .hero {{ border-left: 6px solid #2f6f9f; }}
    .warn {{ color: #8a4b00; }}
    .font-warning {{ background: #fff7ed; border: 1px solid #f59e0b; border-left: 6px solid #f59e0b; border-radius: 8px; padding: 12px; margin-top: 12px; }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px 16px; margin-top: 12px; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; }}
    dt {{ font-weight: 700; }}
    .cut-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
    .cut-card {{ border: 1px solid #d8dde6; border-radius: 8px; padding: 12px; background: #fff; }}
    .proof-frame {{ max-width: 520px; width: 100%; border: 1px solid #c7ced8; display: block; margin-bottom: 8px; }}
    .wrap-evidence-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 240px)); gap: 12px; align-items: start; }}
    .wrap-evidence-card {{ border: 1px solid #d8dde6; border-radius: 6px; padding: 8px; background: #fbfcfe; }}
    .wrap-evidence-frame {{ max-width: 220px; width: 100%; border: 1px solid #c7ced8; display: block; margin-bottom: 6px; }}
    .wrap-lines {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; white-space: pre-line; font-size: 12px; }}
    .sample-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin-top: 8px; }}
    figure {{ margin: 0; }}
    figcaption {{ font-size: 12px; color: #52616f; }}
    video {{ max-width: 100%; width: 100%; display: block; margin-top: 8px; }}
    .detail-links {{ display: grid; gap: 6px; }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>Review Focus: Current Proof</h1>
    <p>{escape(intro)}</p>
    <div class="meta">
      <div><strong>artifact</strong><br>{escape(str(report.get("artifact_id") or ""))}</div>
      <div><strong>candidate</strong><br>{escape(str(style.get("typography_decoration_candidate_id") or style.get("style_candidate_id") or ""))}</div>
      <div><strong>font</strong><br>{escape(str(font_name.get("value") or font_route.get("resolved") or ""))}</div>
      <div><strong>target cuts</strong><br>{escape(", ".join(report.get("target_cuts") or []))}</div>
      <div><strong>overlays available</strong><br>{escape(str(aggregate.get("subtitle_overlay_available_count") or ""))}</div>
      <div><strong>rights / production</strong><br>{escape(str(report.get("rights_status") or ""))} / production_candidate={escape(str(report.get("production_candidate")))}</div>
    </div>
{font_evidence_warning}
  </section>
{proof_focus}
{multiline_evidence}
{cut_evidence}
{detail_links}
  <section class="boundary warn">
    <h2>Boundary</h2>
    <p>Diagnostic review only. This page does not grant production subtitle design acceptance, production render acceptance, rights approval, publishing acceptance, or public-use permission.</p>
  </section>
</main>
</body>
</html>
"""


def _font_visual_evidence_warning_html(report: dict[str, Any]) -> str:
    evidence = report.get("font_visual_evidence")
    if not isinstance(evidence, dict):
        return ""
    if evidence.get("valid_requested_font_visual_evidence") is not False:
        return ""
    warning = evidence.get("warning") or "Requested font visual evidence is not valid."
    implication = evidence.get("review_implication") or ""
    requested = evidence.get("requested_font_family") or ""
    resolved = evidence.get("resolved_font_family") or ""
    status = evidence.get("font_file_status") or ""
    return f"""    <div class="font-warning">
      <strong>Font evidence warning</strong>
      <p>{escape(str(warning))}</p>
      <p>{escape(str(implication))}</p>
      <p>requested={escape(str(requested))}; resolved={escape(str(resolved))}; status={escape(str(status))}</p>
    </div>"""


def _focused_multiline_wrap_evidence_html(report: dict[str, Any]) -> str:
    evidence = report.get("multiline_wrap_evidence")
    if not isinstance(evidence, dict):
        return ""
    status = str(evidence.get("status") or "")
    has_evidence = status == "multiline_wrap_evidence_surfaced"
    intro = (
        "This proof includes visible multiline subtitle evidence. Review the compact screenshots below before judging wrapping and dense readability."
        if has_evidence
        else "This proof does not currently surface multiline screenshot evidence; do not use it for multiline/wrap judgement yet."
    )
    cards: list[str] = []
    per_cut = evidence.get("per_cut") if isinstance(evidence.get("per_cut"), dict) else {}
    for cut_id, cut_evidence in per_cut.items():
        if not isinstance(cut_evidence, dict):
            continue
        for item in cut_evidence.get("evidence_items") or []:
            screenshot_path = item.get("screenshot_path")
            if not screenshot_path:
                continue
            href = _artifact_href(screenshot_path)
            wrapped_lines = "\n".join(str(line) for line in item.get("wrapped_lines") or [])
            caption = (
                f"{cut_id} / {item.get('subtitle_id')} / "
                f"{item.get('screenshot_frame_seconds')}s"
            )
            cards.append(
                '<figure class="wrap-evidence-card">'
                f'<a href="{href}"><img class="wrap-evidence-frame" src="{href}" alt="{escape(caption)}"></a>'
                f"<figcaption><strong>{escape(caption)}</strong><br>"
                f"display={escape(str(item.get('display_start_seconds')))}-{escape(str(item.get('display_end_seconds')))}s; "
                f"lines={escape(str(item.get('wrapped_line_count')))}; "
                f"break={escape(str(item.get('selected_break_reason') or ''))}"
                f'<div class="wrap-lines">{escape(wrapped_lines)}</div>'
                "</figcaption></figure>"
            )
    grid = (
        '<div class="wrap-evidence-grid">' + "\n".join(cards) + "</div>"
        if cards
        else "<p>No compact multiline screenshots were generated.</p>"
    )
    return f"""  <section class="wrap-evidence">
    <h2>Multiline / Wrap Evidence</h2>
    <p>{escape(intro)}</p>
    <dl>
      <dt>status</dt><dd>{escape(status)}</dd>
      <dt>multiline cues</dt><dd>{escape(str(evidence.get("multiline_item_count") or 0))}</dd>
      <dt>screenshots</dt><dd>{escape(str(evidence.get("screenshot_count") or 0))}</dd>
    </dl>
{grid}
  </section>
"""


def _focused_cut_evidence_html(report: dict[str, Any]) -> str:
    cut_results = report.get("cut_results")
    if not isinstance(cut_results, list) or not cut_results:
        return ""
    cards = "\n".join(_focused_cut_card_html(item) for item in cut_results)
    return f"""  <section class="evidence">
    <h2>Subtitle-Area Evidence</h2>
    <div class="cut-grid">
{cards}
    </div>
  </section>
"""


def _focused_cut_card_html(item: dict[str, Any]) -> str:
    artifacts = item.get("generated_artifacts") or {}
    visual = _visual_embed_html(
        frame=artifacts.get("frame"),
        video=artifacts.get("video"),
        alt=f"{item.get('cut_id', '')} focused current proof",
    )
    samples = _sample_frames_html(artifacts.get("sample_frames") or [])
    timing = item.get("subtitle_timing") or {}
    items = timing.get("items") if isinstance(timing, dict) else []
    renderable = [
        subtitle
        for subtitle in items
        if str(subtitle.get("status") or "") in RENDERABLE_SUBTITLE_STATUSES
    ] if isinstance(items, list) else []
    line_count = len(renderable)
    return f"""      <article class="cut-card">
        <h3>{escape(str(item.get("cut_id") or ""))}</h3>
        <p>status: {escape(str(item.get("visual_proof_status") or ""))}; overlay_present={escape(str(item.get("subtitle_overlay_present") or ""))}; target_lines={escape(str(line_count))}</p>
        {visual}
        <h4>Subtitle-bearing samples</h4>
        {samples or "<p>No sample frames recorded.</p>"}
      </article>"""


def _focused_detail_links_html(report: dict[str, Any]) -> str:
    focus = report.get("focused_proof_review") or {}
    outputs = report.get("outputs") or {}
    reference = focus.get("ed10o_reference_report") if isinstance(focus, dict) else ""
    links: list[tuple[str, Any]] = [
        ("ED-10o focused comparison reference", reference),
        ("Detailed subtitle overlay proof report", outputs.get("html")),
        ("Representative visual proof report", "representative_visual_proof_report.html"),
        ("Machine-readable proof JSON", outputs.get("json")),
    ]
    rows = "\n".join(
        f'      <a href="{_review_dir_relative_href(value)}">{escape(label)}</a>'
        for label, value in links
        if value
    )
    return f"""  <section class="details">
    <h2>Detailed Reports</h2>
    <div class="detail-links">
{rows}
    </div>
  </section>
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


def _proof_focus_html(report: dict[str, Any]) -> str:
    focus = report.get("focused_proof_review")
    if not isinstance(focus, dict) or not focus:
        return ""
    look_for = "\n".join(
        f"      <li>{escape(str(item))}</li>" for item in focus.get("look_for") or []
    )
    review_debt = _review_debt_html(report.get("review_debt") or [])
    target_lines = _target_lines_html(report)
    reference = str(focus.get("ed10o_reference_report") or "")
    reference_html = (
        f'<p>ED-10o reference: <a href="{_review_dir_relative_href(reference)}">{escape(reference)}</a></p>'
        if reference
        else ""
    )
    return f"""  <section class="review-focus">
    <h2>Review Focus</h2>
    <dl>
      <dt>artifact</dt><dd>{escape(str(report.get("artifact_id") or ""))}</dd>
      <dt>source review</dt><dd>{escape(str(focus.get("source_review_artifact_id") or report.get("source_review_artifact_id") or ""))}</dd>
      <dt>target</dt><dd>{escape(str(focus.get("target") or ""))}</dd>
      <dt>current lead</dt><dd>{escape(str(focus.get("current_lead_candidate_id") or ""))}</dd>
      <dt>input mode</dt><dd>{escape(str(focus.get("input_mode") or ""))}</dd>
      <dt>completion signal</dt><dd>{escape(str(focus.get("completion_signal") or ""))}</dd>
    </dl>
    <h3>Look For</h3>
    <ul>
{look_for}
    </ul>
{reference_html}
{review_debt}
{target_lines}
  </section>
"""


def _review_debt_html(review_debt: list[dict[str, Any]]) -> str:
    if not review_debt:
        return ""
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('debt_id') or ''))}</td>"
        f"<td>{escape(str(item.get('status') or ''))}</td>"
        f"<td>{escape(str(item.get('reason') or ''))}</td>"
        f"<td>{escape(str(item.get('next_action') or ''))}</td>"
        "</tr>"
        for item in review_debt
    )
    return (
        "    <h3>Review Debt</h3>\n"
        "    <table>\n"
        "      <tr><th>debt</th><th>status</th><th>reason</th><th>next action</th></tr>\n"
        f"{rows}\n"
        "    </table>\n"
    )


def _target_lines_html(report: dict[str, Any]) -> str:
    cut_results = report.get("cut_results")
    if not isinstance(cut_results, list) or not cut_results:
        return ""
    rows: list[str] = []
    for cut in cut_results:
        cut_id = str(cut.get("cut_id") or "")
        timing = cut.get("subtitle_timing") or {}
        items = timing.get("items") if isinstance(timing, dict) else []
        if not isinstance(items, list):
            continue
        renderable = [
            item
            for item in items
            if str(item.get("status") or "") in RENDERABLE_SUBTITLE_STATUSES
        ]
        for item in renderable[:8]:
            rows.append(
                "<tr>"
                f"<td>{escape(cut_id)}</td>"
                f"<td>{escape(str(item.get('subtitle_id') or ''))}</td>"
                f"<td>{escape(str(item.get('render_start_seconds') or ''))}-"
                f"{escape(str(item.get('render_end_seconds') or ''))}</td>"
                f"<td>{escape(str(item.get('text') or ''))}</td>"
                "</tr>"
            )
        if len(renderable) > 8:
            rows.append(
                "<tr>"
                f"<td>{escape(cut_id)}</td>"
                "<td colspan=\"3\">"
                f"{escape(str(len(renderable) - 8))} more subtitle cues in this cut; "
                "see the cut table below for the full timing readback."
                "</td>"
                "</tr>"
            )
    if not rows:
        return ""
    return (
        "    <h3>Target Lines</h3>\n"
        "    <table>\n"
        "      <tr><th>cut</th><th>subtitle</th><th>render time</th><th>text</th></tr>\n"
        f"{''.join(rows)}\n"
        "    </table>\n"
    )


def _style_summary_html(direction: dict[str, Any], parameters: dict[str, Any]) -> str:
    if not direction and not parameters:
        return "    <p>No diagnostic style direction is recorded for this report.</p>"
    font_name = parameters.get("font_name") or {}
    font_route = parameters.get("font_family_route") or {}
    font_size = parameters.get("font_size") or {}
    outline = parameters.get("outline") or {}
    margin_v = parameters.get("margin_v") or {}
    alignment = parameters.get("alignment") or {}
    wrapping = parameters.get("wrapping") or {}
    font_bbox_wrap = parameters.get("font_bbox_wrap_readback") or {}
    wrap_algorithm = font_bbox_wrap.get("wrap_algorithm") or wrapping.get("wrap_algorithm") or {}
    renderer_gap = font_bbox_wrap.get("renderer_gap") or {}
    layout_values = parameters.get("layout_values") or {}
    layout_formulas = parameters.get("layout_formulas") or {}
    line_summary = parameters.get("line_width_watch_summary") or {}
    mode_semantics = direction.get("mode_semantics") or {}
    return (
        "    <dl>"
        f"<dt>preset</dt><dd>{escape(str(direction.get('preset_name', '')))}</dd>"
        f"<dt>contract</dt><dd>{escape(str(direction.get('presentation_contract_id', '')))}</dd>"
        f"<dt>renderer</dt><dd>{escape(str(parameters.get('renderer', '')))}</dd>"
        f"<dt>candidate_id</dt><dd>{escape(str(parameters.get('style_candidate_id', '')))}</dd>"
        f"<dt>typography candidate</dt><dd>{escape(str(parameters.get('typography_decoration_candidate_id', '')))}</dd>"
        f"<dt>mode</dt><dd>{escape(str(parameters.get('presentation_mode', '')))}</dd>"
        f"<dt>supported modes</dt><dd>{escape(', '.join(parameters.get('supported_presentation_modes') or []))}</dd>"
        f"<dt>mode semantics</dt><dd>{escape(json.dumps(mode_semantics, ensure_ascii=False))}</dd>"
        f"<dt>left alignment</dt><dd>{escape(str(parameters.get('left_alignment_scope', '')))}</dd>"
        f"<dt>intent</dt><dd>{escape(str(direction.get('target_viewing_context', '')))}; "
        f"{escape(str(direction.get('visual_weight', '')))}</dd>"
        f"<dt>pattern</dt><dd>{escape(str(direction.get('implemented_pattern', '')))}</dd>"
        f"<dt>long-line policy</dt><dd>{escape(str(direction.get('long_line_policy', '')))}</dd>"
        f"<dt>font name</dt><dd>{escape(str(font_name.get('value', '')))} "
        f"({escape(str(font_name.get('source', '')))}; {escape(str(font_name.get('readback', '')))})</dd>"
        f"<dt>font route</dt><dd>requested={escape(str(font_route.get('requested', '')))}; "
        f"resolved={escape(str(font_route.get('resolved', '')))}; "
        f"font_file_status={escape(str(font_route.get('font_file_status', '')))}</dd>"
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
        f"<dt>wrap algorithm</dt><dd>{escape(str(wrap_algorithm.get('name', '')))}; "
        f"{escape(str(font_bbox_wrap.get('wrapping_authority', '')))}</dd>"
        f"<dt>font bbox carry-over</dt><dd>applied_to_ass="
        f"{escape(str(font_bbox_wrap.get('all_renderable_items_applied_to_proof_text', '')))}; "
        f"explicit_line_breaks={escape(str(font_bbox_wrap.get('explicit_line_breaks_passed_to_ass', '')))}; "
        f"orphan_prevention_count={escape(str(font_bbox_wrap.get('orphan_prevention_applied_count', '')))}; "
        f"suffix_tail_prevention_count={escape(str(font_bbox_wrap.get('suffix_tail_prevention_applied_count', '')))}; "
        f"suspicious_tail_line_present={escape(str(font_bbox_wrap.get('suspicious_tail_line_present', '')))}; "
        f"one_char_orphan={escape(str(font_bbox_wrap.get('one_character_orphan_present', '')))}</dd>"
        f"<dt>measurement/proof renderer gap</dt><dd>{escape(str(renderer_gap.get('classification', '')))}; "
        f"exists={escape(str(renderer_gap.get('exists', '')))}</dd>"
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
    font_route = parameters.get("font_family_route") or {}
    outline = parameters.get("outline") or {}
    margin_v = parameters.get("margin_v") or {}
    alignment = parameters.get("alignment") or {}
    positioning = parameters.get("positioning") or {}
    font_bbox_wrap = parameters.get("font_bbox_wrap_readback") or {}
    wrap_algorithm = font_bbox_wrap.get("wrap_algorithm") or {}
    renderer_gap = font_bbox_wrap.get("renderer_gap") or {}
    return "<br>".join(
        [
            f"preset: {escape(str(direction.get('preset_name', '')))}",
            f"contract: {escape(str(direction.get('presentation_contract_id', '')))}",
            f"candidate_id: {escape(str(parameters.get('style_candidate_id', '')))}",
            f"typography_candidate: {escape(str(parameters.get('typography_decoration_candidate_id', '')))}",
            f"mode: {escape(str(parameters.get('presentation_mode', '')))}",
            f"renderer: {escape(str(parameters.get('renderer', '')))}",
            f"style_slot: {escape(str(parameters.get('style_slot', '')))}",
            f"font_route: requested={escape(str(font_route.get('requested', '')))}, resolved={escape(str(font_route.get('resolved', '')))}, status={escape(str(font_route.get('font_file_status', '')))}",
            f"font_size: {escape(str(font_size.get('value')))} ({escape(str(font_size.get('source', '')))})",
            f"outline: {escape(str(outline.get('value')))} ({escape(str(outline.get('source', '')))})",
            f"margin_v: {escape(str(margin_v.get('value')))} ({escape(str(margin_v.get('source', '')))})",
            f"alignment: {escape(str(alignment.get('value', '')))}",
            f"dialogue_pos_two_line: {escape(str(positioning.get('dialogue_x', '')))}, {escape(str(positioning.get('dialogue_y_for_two_line_block', '')))}",
            f"badge_pos_two_line: {escape(str(positioning.get('speaker_badge_x', '')))}, {escape(str(positioning.get('speaker_badge_y_for_two_line_block', '')))}",
            f"badge_size: {escape(str(positioning.get('badge_width', '')))}x{escape(str(positioning.get('badge_height', '')))}",
            f"line_height: {escape(str(positioning.get('line_height', '')))}",
            f"wrap_algorithm: {escape(str(wrap_algorithm.get('name', '')))}",
            f"font_bbox_applied: {escape(str(font_bbox_wrap.get('all_renderable_items_applied_to_proof_text', '')))}",
            f"explicit_ass_line_breaks: {escape(str(font_bbox_wrap.get('explicit_line_breaks_passed_to_ass', '')))}",
            f"orphan_prevention_count: {escape(str(font_bbox_wrap.get('orphan_prevention_applied_count', '')))}",
            f"suffix_tail_prevention_count: {escape(str(font_bbox_wrap.get('suffix_tail_prevention_applied_count', '')))}",
            f"suspicious_tail_line_present: {escape(str(font_bbox_wrap.get('suspicious_tail_line_present', '')))}",
            f"one_char_orphan: {escape(str(font_bbox_wrap.get('one_character_orphan_present', '')))}",
            f"renderer_gap: {escape(str(renderer_gap.get('classification', '')))}",
            f"wrap_items: {escape(json.dumps(font_bbox_wrap.get('items') or [], ensure_ascii=False))}",
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


def _review_dir_relative_href(value: Any) -> str:
    text = str(value).replace("\\", "/")
    if text.startswith(("http://", "https://")):
        return escape(text, quote=True)
    marker = "jp_pilot01r3_cut_review/"
    if marker in text:
        text = text.split(marker, 1)[1]
    elif "/" in text:
        parts = [part for part in text.split("/") if part]
        if parts:
            text = parts[-1]
    return escape(text, quote=True)


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
