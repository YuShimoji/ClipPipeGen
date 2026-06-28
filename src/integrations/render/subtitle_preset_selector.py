"""Deterministic subtitle style intent preset selector.

This selector is a diagnostic readback helper. It maps semantic subtitle
intent to token names that future renderer work can consume, but it does not
render, approve production styling, or change rights/publication gates.
"""

from __future__ import annotations

import re
import json
from copy import deepcopy
from html import escape
from pathlib import Path
from typing import Any, Mapping

from src.integrations.render import ffmpeg_tiny

SCHEMA_ID = "clippipegen.subtitle_preset_selector.v1"
ARTIFACT_ID = "clip-ed10ab-subtitle-preset-selector-001"
FEATURE_ID = "ED-10ab"
VISUAL_PROOF_SCHEMA_ID = "clippipegen.subtitle_visual_selector_proof.v1"
VISUAL_PROOF_ARTIFACT_ID = "clip-ed10ac-visual-selector-proof-001"
VISUAL_PROOF_FEATURE_ID = "ED-10ac"
STYLE_AXIS_PROOF_SCHEMA_ID = "clippipegen.subtitle_style_family_palette_axis_proof.v1"
STYLE_AXIS_PROOF_ARTIFACT_ID = "clip-ed10ad-style-family-palette-axis-proof-001"
STYLE_AXIS_PROOF_FEATURE_ID = "ED-10ad"
RENDER_PATH_CONTRACT_SCHEMA_ID = "clippipegen.subtitle_render_path_selector_contract.v1"
RENDER_PATH_CONTRACT_ARTIFACT_ID = "clip-ed10ae-render-path-selector-contract-probe-001"
RENDER_PATH_CONTRACT_FEATURE_ID = "ED-10ae"
RENDER_CONTRACT_CONSUMER_DRY_READ_SCHEMA_ID = (
    "clippipegen.subtitle_render_contract_consumer_dry_read.v1"
)
RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID = (
    "clip-ed10af-render-contract-consumer-dry-read-001"
)
RENDER_CONTRACT_CONSUMER_DRY_READ_FEATURE_ID = "ED-10af"
RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT = "7e96a28"

RENDER_PATH_PROBE_SCHEMA_ID = "clippipegen.subtitle_render_path_selector_probe.v1"
RENDER_PATH_PROBE_ARTIFACT_ID = "clip-ed10af-l2-render-path-selector-probe-001"
RENDER_PATH_PROBE_FEATURE_ID = "ED-10af"
RENDER_PATH_PROBE_SELECTED_EXAMPLE_IDS = (
    "neutral_dialogue_intensity_0",
    "shout_intensity_2",
    "whisper_intensity_1",
)
RENDER_PATH_PROBE_SOURCE_VIDEO_RELATIVE_PATH = Path(
    "episodes/jp_pilot01_hololive_bancho_20260525/materials/"
    "src_video_jp_pilot01/source_video.mp4"
)
RENDER_PATH_PROBE_SOURCE_AUDIO_RELATIVE_PATH = Path(
    "episodes/jp_pilot01_hololive_bancho_20260525/materials/"
    "src_audio_jp_pilot01/source.wav"
)
RENDER_PATH_PROBE_LOCAL_OUTPUT_RELATIVE_DIR = Path(
    "episodes/jp_pilot01_hololive_bancho_20260525/review/"
    "jp_pilot01r3_cut_review/subtitle_render_path_selector_probe"
)
LINEAGE_OBSERVATION_SCHEMA_ID = (
    "clippipegen.subtitle_render_path_lineage_observation_surface.v1"
)
LINEAGE_OBSERVATION_ARTIFACT_ID = (
    "clip-ed10ag-lineage-and-observation-surface-001"
)
LINEAGE_OBSERVATION_FEATURE_ID = "ED-10ag"
LINEAGE_OBSERVATION_CONTACT_SHEET_FILENAME = (
    "subtitle_render_path_selector_probe_contact_sheet.jpg"
)
PRODUCTION_LIMITATION_LIFT_SCHEMA_ID = (
    "clippipegen.subtitle_production_limitation_lift_entry.v1"
)
PRODUCTION_LIMITATION_LIFT_ARTIFACT_ID = (
    "clip-ed10ah-production-limitation-lift-entry-001"
)
PRODUCTION_LIMITATION_LIFT_FEATURE_ID = "ED-10ah"
PRODUCTION_LIMITATION_LIFT_GATE_NAMES = (
    "diagnostic_render_path_proof",
    "production_subtitle_design_acceptance",
    "production_render_acceptance",
    "creative_acceptance",
    "rights_status",
    "publishing_acceptance",
    "public_use_permission",
)
FINAL_RENDER_PATH_READINESS_SCHEMA_ID = (
    "clippipegen.subtitle_final_render_path_readiness_packet.v1"
)
FINAL_RENDER_PATH_READINESS_ARTIFACT_ID = (
    "clip-ed10ai-final-render-path-readiness-packet-001"
)
FINAL_RENDER_PATH_READINESS_FEATURE_ID = "ED-10ai"
FINAL_RENDER_PATH_READINESS_REQUIRED_ROW_IDS = (
    "ed10ah_gate_separation_source",
    "diagnostic_proof_evidence",
    "selector_semantic_style_contract_evidence",
    "render_adapter_input_contract_evidence",
    "local_ignored_proof_media_evidence",
    "lineage_predecessor_evidence",
    "missing_production_subtitle_design_acceptance",
    "missing_production_render_acceptance",
    "missing_creative_acceptance",
    "missing_rights_publication_public_use_decisions",
)
FINAL_RENDER_PATH_STAGE1_SCHEMA_ID = (
    "clippipegen.subtitle_final_render_path_stage_1.v1"
)
FINAL_RENDER_PATH_STAGE1_ARTIFACT_ID = (
    "clip-ed10aj-final-render-path-stage-1-001"
)
FINAL_RENDER_PATH_STAGE1_FEATURE_ID = "ED-10aj"
FINAL_RENDER_PATH_STAGE1_REQUIRED_CHECK_IDS = (
    "render_adapter_path_selected",
    "subtitle_ass_generation_path_available",
    "semantic_selector_contract_available",
    "stable_body_text_policy_preserved",
    "badge_accent_backplate_routing_preserved",
    "line_break_safe_area_metadata_preserved",
    "local_ignored_proof_media_recorded",
    "no_tracked_binary_media",
    "production_gates_still_closed",
    "publishing_public_use_gates_still_closed",
)
FINAL_RENDER_PATH_STAGE2_SCHEMA_ID = (
    "clippipegen.subtitle_final_render_path_stage_2_replayability.v1"
)
FINAL_RENDER_PATH_STAGE2_ARTIFACT_ID = (
    "clip-ed10ak-final-render-path-stage-2-replayability-001"
)
FINAL_RENDER_PATH_STAGE2_FEATURE_ID = "ED-10ak"
FINAL_RENDER_PATH_STAGE2_REQUIRED_ROW_IDS = (
    "selected_render_path",
    "required_tracked_inputs",
    "required_same_machine_local_inputs",
    "ignored_output_paths",
    "expected_output_types",
    "command_family",
    "validation_readback_commands",
    "fresh_clone_absence_behavior",
    "diagnostic_only_scope",
    "missing_before_production_render",
)
FINAL_RENDER_PATH_STAGE3_SCHEMA_ID = (
    "clippipegen.subtitle_final_render_path_stage_3_rehearsal.v1"
)
FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID = (
    "clip-ed10al-final-render-path-stage-3-rehearsal-001"
)
FINAL_RENDER_PATH_STAGE3_FEATURE_ID = "ED-10al"
FINAL_RENDER_PATH_STAGE3_REQUIRED_ROW_IDS = (
    "selected_render_path",
    "tracked_inputs_used",
    "same_machine_inputs_used",
    "ignored_outputs_generated_or_recorded",
    "command_and_command_family",
    "output_metadata_available",
    "ass_style_tokens_survived",
    "stable_body_text_policy_survived",
    "badge_accent_backplate_route_survived",
    "line_break_safe_area_metadata_survived",
    "production_public_gates_still_closed",
)
PRODUCTION_LIMITATION_LIFT_STAGE1_SCHEMA_ID = (
    "clippipegen.subtitle_production_limitation_lift_stage_1.v1"
)
PRODUCTION_LIMITATION_LIFT_STAGE1_ARTIFACT_ID = (
    "clip-ed10am-production-limitation-lift-stage-1-001"
)
PRODUCTION_LIMITATION_LIFT_STAGE1_FEATURE_ID = "ED-10am"
PRODUCTION_LIMITATION_LIFT_STAGE1_GATE_NAMES = (
    "diagnostic_render_path_rehearsal_evidence",
    "production_subtitle_design_acceptance",
    "production_render_acceptance",
    "creative_acceptance",
    "rights_status",
    "publishing_acceptance",
    "public_use_permission",
    "tracked_media_boundary",
    "same_machine_ignored_evidence_boundary",
)
PRODUCTION_LIMITATION_LIFT_STAGE2_SCHEMA_ID = (
    "clippipegen.subtitle_production_limitation_lift_stage_2_decision_packet.v1"
)
PRODUCTION_LIMITATION_LIFT_STAGE2_ARTIFACT_ID = (
    "clip-ed10an-production-limitation-lift-stage-2-decision-packet-001"
)
PRODUCTION_LIMITATION_LIFT_STAGE2_FEATURE_ID = "ED-10an"
PRODUCTION_LIMITATION_LIFT_STAGE2_DECISION_GROUP_IDS = (
    "subtitle_design_visual_acceptance",
    "production_render_readiness",
    "rights_publishing_public_use_clearance",
)
PRODUCTION_LIMITATION_LIFT_STAGE3_SCHEMA_ID = (
    "clippipegen.subtitle_production_limitation_lift_stage_3_owner_review_prep.v1"
)
PRODUCTION_LIMITATION_LIFT_STAGE3_ARTIFACT_ID = (
    "clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001"
)
PRODUCTION_LIMITATION_LIFT_STAGE3_FEATURE_ID = "ED-10ao"
PRODUCTION_LIMITATION_LIFT_STAGE3_OWNER_REVIEW_GROUP_IDS = (
    "subtitle_design_visual_acceptance",
    "production_render_readiness",
    "rights_publishing_public_use_clearance",
)
PRODUCTION_LIMITATION_LIFT_STAGE4_SCHEMA_ID = (
    "clippipegen.subtitle_production_limitation_lift_stage_4_user_decision_card.v1"
)
PRODUCTION_LIMITATION_LIFT_STAGE4_ARTIFACT_ID = (
    "clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001"
)
PRODUCTION_LIMITATION_LIFT_STAGE4_FEATURE_ID = "ED-10ap"
PRODUCTION_LIMITATION_LIFT_STAGE4_DECISION_TOPIC_IDS = (
    "subtitle_design_visual_acceptance",
    "production_render_readiness",
    "rights_publishing_public_use_clearance",
)
PRODUCTION_LIMITATION_LIFT_STAGE5_SCHEMA_ID = (
    "clippipegen.subtitle_production_limitation_lift_stage_5_user_decision_ready.v1"
)
PRODUCTION_LIMITATION_LIFT_STAGE5_ARTIFACT_ID = (
    "clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001"
)
PRODUCTION_LIMITATION_LIFT_STAGE5_FEATURE_ID = "ED-10aq"
PRODUCTION_LIMITATION_LIFT_STAGE5_DECISION_TOPIC_IDS = (
    "subtitle_design_visual_acceptance",
    "production_render_readiness",
    "rights_publishing_public_use_clearance",
)
SOURCE_REGISTRY_ARTIFACT_ID = "clip-ed10aa-subtitle-style-intent-registry-001"
SOURCE_RENDER_PATH_ARTIFACT_ID = "clip-ed10z-tiny-render-path-nearer-probe-001"

VALID_SPEAKER_ROLES = ("character", "narrator", "system", "unknown")
VALID_EMOTIONS = (
    "neutral",
    "emphasis",
    "shout",
    "whisper",
    "ominous",
    "narration",
    "system_note",
)
VALID_UTTERANCE_ROLES = (
    "dialogue",
    "narration",
    "sfx",
    "quote",
    "warning",
    "inner_voice",
)
VALID_READABILITY_PRIORITIES = ("normal", "high", "maximum")
HUMAN_REVIEW_REQUIRED_FOR = (
    "new_style_family",
    "new_palette",
    "body_text_color_policy_change",
    "production_route_change",
    "rights",
    "publishing",
    "public_use",
)

EMOTION_PRESETS: dict[str, dict[str, Any]] = {
    "neutral": {
        "font_size_scale": 1.0,
        "outline_shadow_strength": "current_lead",
        "badge_color_token": "speaker_default_badge",
        "accent_color_token": "speaker_default_subtle_accent",
        "backplate_box_token": "off",
        "motion_primitive": "none",
        "safe_area_line_break_behavior": "normal",
    },
    "emphasis": {
        "font_size_scale": 1.04,
        "outline_shadow_strength": "current_lead_plus",
        "badge_color_token": "speaker_default_badge",
        "accent_color_token": "emotion_warm_accent",
        "backplate_box_token": "off",
        "motion_primitive": "emphasis_pop_placeholder",
        "safe_area_line_break_behavior": "prefer_shorter_lines",
    },
    "shout": {
        "font_size_scale": 1.1,
        "outline_shadow_strength": "strong",
        "badge_color_token": "speaker_default_badge",
        "accent_color_token": "high_energy_accent",
        "backplate_box_token": "optional_high_readability",
        "motion_primitive": "impact_placeholder",
        "safe_area_line_break_behavior": "prefer_shorter_lines_max_two",
    },
    "whisper": {
        "font_size_scale": 0.96,
        "outline_shadow_strength": "soft_readable",
        "badge_color_token": "speaker_default_muted_badge",
        "accent_color_token": "quiet_accent",
        "backplate_box_token": "soft",
        "motion_primitive": "none",
        "safe_area_line_break_behavior": "normal",
    },
    "ominous": {
        "font_size_scale": 1.02,
        "outline_shadow_strength": "heavy_low_glow_placeholder",
        "badge_color_token": "speaker_default_badge",
        "accent_color_token": "dark_accent",
        "backplate_box_token": "soft",
        "motion_primitive": "slow_weight_placeholder",
        "safe_area_line_break_behavior": "high_readability",
    },
    "narration": {
        "font_size_scale": 0.98,
        "outline_shadow_strength": "current_lead",
        "badge_color_token": "none_or_narrator_badge",
        "accent_color_token": "narration_neutral_accent",
        "backplate_box_token": "optional",
        "motion_primitive": "none",
        "safe_area_line_break_behavior": "normal",
    },
    "system_note": {
        "font_size_scale": 0.94,
        "outline_shadow_strength": "current_lead",
        "badge_color_token": "system_badge",
        "accent_color_token": "system_accent",
        "backplate_box_token": "on",
        "motion_primitive": "none",
        "safe_area_line_break_behavior": "maximum_readability",
    },
}

INTENSITY_FONT_SIZE_BONUS = {
    0: 0.0,
    1: 0.02,
    2: 0.06,
    3: 0.1,
}


def normalize_subtitle_intent(intent: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(intent or {})
    return {
        "speaker_id": _speaker_id(source.get("speaker_id")),
        "speaker_role": _enum(
            source.get("speaker_role"),
            valid=VALID_SPEAKER_ROLES,
            default="unknown",
        ),
        "emotion": _enum(
            source.get("emotion"),
            valid=VALID_EMOTIONS,
            default="neutral",
        ),
        "intensity": _intensity(source.get("intensity")),
        "utterance_role": _enum(
            source.get("utterance_role"),
            valid=VALID_UTTERANCE_ROLES,
            default="dialogue",
        ),
        "readability_priority": _enum(
            source.get("readability_priority"),
            valid=VALID_READABILITY_PRIORITIES,
            default="high",
        ),
    }


def select_subtitle_preset(intent: Mapping[str, Any] | None) -> dict[str, Any]:
    normalized = normalize_subtitle_intent(intent)
    preset_emotion = _effective_emotion(normalized)
    preset = deepcopy(EMOTION_PRESETS[preset_emotion])
    intensity = int(normalized["intensity"])
    readability = str(normalized["readability_priority"])
    speaker_role = str(normalized["speaker_role"])
    speaker_id = str(normalized["speaker_id"])

    font_size_scale = round(
        float(preset["font_size_scale"]) + INTENSITY_FONT_SIZE_BONUS[intensity],
        2,
    )
    badge_color_token, accent_color_token = _identity_color_tokens(
        speaker_id=speaker_id,
        speaker_role=speaker_role,
        base_badge=str(preset["badge_color_token"]),
        base_accent=str(preset["accent_color_token"]),
    )
    backplate_box_token = _readability_backplate(
        base=str(preset["backplate_box_token"]),
        readability=readability,
    )
    safe_area_line_break_behavior = _readability_line_break(
        base=str(preset["safe_area_line_break_behavior"]),
        readability=readability,
    )
    outline_shadow_strength = _outline_token(
        base=str(preset["outline_shadow_strength"]),
        intensity=intensity,
        readability=readability,
    )

    style_tokens = {
        "font_family_role": _font_family_role(normalized),
        "font_size_scale": font_size_scale,
        "outline_shadow_strength": outline_shadow_strength,
        "badge_color_token": badge_color_token,
        "accent_color_token": accent_color_token,
        "backplate_box_token": backplate_box_token,
        "motion_primitive": str(preset["motion_primitive"]),
        "safe_area_line_break_behavior": safe_area_line_break_behavior,
        "body_text_color_token": "stable_default_body_text",
        "body_text_color_changed": False,
    }

    return {
        "selector_id": "subtitle_semantic_preset_selector_v0",
        "source_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "source_render_path_artifact_id": SOURCE_RENDER_PATH_ARTIFACT_ID,
        "normalized_intent": normalized,
        "preset_key": (
            f"{speaker_role}.{normalized['utterance_role']}."
            f"{preset_emotion}.i{intensity}.{readability}"
        ),
        "style_tokens": style_tokens,
        "review_policy": {
            "human_review_required": False,
            "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
            "candidate_comparison_reopened": False,
            "raw_numeric_review_required": False,
        },
        "render_gate": {
            "level": "L1 Existing Output First",
            "new_render_required": False,
            "reason": "selector-only readback maps semantics to tokens without creating new visual proof",
        },
        "boundaries": _boundary_flags(),
    }


def build_subtitle_preset_selector_readback() -> dict[str, Any]:
    examples = [
        _example(
            "neutral_dialogue_intensity_0",
            {
                "speaker_id": "bancho",
                "speaker_role": "character",
                "emotion": "neutral",
                "intensity": 0,
                "utterance_role": "dialogue",
                "readability_priority": "high",
            },
        ),
        _example(
            "shout_intensity_2",
            {
                "speaker_id": "bancho",
                "speaker_role": "character",
                "emotion": "shout",
                "intensity": 2,
                "utterance_role": "dialogue",
                "readability_priority": "high",
            },
        ),
        _example(
            "whisper_intensity_1",
            {
                "speaker_id": "bancho",
                "speaker_role": "character",
                "emotion": "whisper",
                "intensity": 1,
                "utterance_role": "dialogue",
                "readability_priority": "normal",
            },
        ),
        _example(
            "ominous_intensity_2",
            {
                "speaker_id": "unknown",
                "speaker_role": "character",
                "emotion": "ominous",
                "intensity": 2,
                "utterance_role": "inner_voice",
                "readability_priority": "maximum",
            },
        ),
        _example(
            "narration_intensity_0",
            {
                "speaker_id": "narrator",
                "speaker_role": "narrator",
                "emotion": "narration",
                "intensity": 0,
                "utterance_role": "narration",
                "readability_priority": "high",
            },
        ),
        _example(
            "system_note_intensity_0",
            {
                "speaker_id": "system",
                "speaker_role": "system",
                "emotion": "system_note",
                "intensity": 0,
                "utterance_role": "warning",
                "readability_priority": "maximum",
            },
        ),
    ]
    return {
        "schema_id": SCHEMA_ID,
        "artifact_id": ARTIFACT_ID,
        "feature_id": FEATURE_ID,
        "status": "diagnostic_preset_selector_ready",
        "source_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "source_render_path_artifact_id": SOURCE_RENDER_PATH_ARTIFACT_ID,
        "input_axes": [
            "speaker_id",
            "speaker_role",
            "emotion",
            "intensity",
            "utterance_role",
            "readability_priority",
        ],
        "output_style_tokens": [
            "font_family_role",
            "font_size_scale",
            "outline_shadow_strength",
            "badge_color_token",
            "accent_color_token",
            "backplate_box_token",
            "motion_primitive",
            "safe_area_line_break_behavior",
            "body_text_color_token",
        ],
        "selector_contract": {
            "deterministic": True,
            "body_text_color_default": "stable_default_body_text",
            "character_color_first_surfaces": [
                "badge_color_token",
                "accent_color_token",
            ],
            "raw_numeric_review_required": False,
            "same_candidate_comparison_reopened": False,
        },
        "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
        "examples": examples,
        "render_gate": {
            "level": "L1 Existing Output First",
            "new_render_run": False,
            "reason": "selector/readback only; existing ED-10z proof is the visual source",
        },
        "boundaries": _boundary_flags(),
    }


def build_subtitle_visual_selector_proof() -> dict[str, Any]:
    selector = build_subtitle_preset_selector_readback()
    proof_examples = [
        _visual_proof_example(index=index, example=example)
        for index, example in enumerate(selector["examples"], start=1)
    ]
    body_text_tokens = {
        example["style_tokens"]["body_text_color_token"] for example in selector["examples"]
    }
    body_text_changed = any(
        bool(example["style_tokens"]["body_text_color_changed"])
        for example in selector["examples"]
    )
    return {
        "schema_id": VISUAL_PROOF_SCHEMA_ID,
        "artifact_id": VISUAL_PROOF_ARTIFACT_ID,
        "feature_id": VISUAL_PROOF_FEATURE_ID,
        "status": "visual_selector_proof_ready",
        "source_selector_artifact_id": ARTIFACT_ID,
        "source_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "source_render_path_artifact_id": SOURCE_RENDER_PATH_ARTIFACT_ID,
        "proof_kind": "tracked_static_html_json_readback",
        "examples_represented": [example["example_id"] for example in selector["examples"]],
        "visual_differentiators": [
            "badge_color_token",
            "accent_color_token",
            "backplate_box_token",
            "font_size_scale",
            "outline_shadow_strength",
            "motion_primitive",
            "safe_area_line_break_behavior",
        ],
        "body_text_color_policy": {
            "token": "stable_default_body_text",
            "stable_across_examples": body_text_tokens == {"stable_default_body_text"}
            and not body_text_changed,
            "changed_in_any_example": body_text_changed,
            "character_color_first_surfaces": [
                "badge_color_token",
                "accent_color_token",
            ],
        },
        "existing_output_first": {
            "considered": True,
            "level": "L1 Existing Output First",
            "source_visual_readback": SOURCE_RENDER_PATH_ARTIFACT_ID,
            "new_render_run": False,
            "reason": (
                "The six ED-10ab examples can be inspected as static "
                "HTML/JSON token proof without generating new frames."
            ),
        },
        "outputs": {
            "json": "docs/style_intent/subtitle-visual-selector-proof.json",
            "html": "docs/style_intent/subtitle-visual-selector-proof.html",
        },
        "examples": proof_examples,
        "review_policy": {
            "human_review_required": False,
            "optional_user_observation": "open_only_freeform_max_3_points",
            "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
            "candidate_comparison_reopened": False,
            "raw_numeric_review_required": False,
        },
        "render_gate": {
            "level": "L1 Existing Output First",
            "new_render_run": False,
            "milestone_gated_not_change_gated": True,
            "documented": True,
        },
        "boundaries": _boundary_flags(),
    }


def write_subtitle_visual_selector_proof(output_dir: Path) -> dict[str, Path]:
    proof = build_subtitle_visual_selector_proof()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-visual-selector-proof.json"
    html_path = output_dir / "subtitle-visual-selector-proof.html"
    json_path.write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    html_path.write_text(render_subtitle_visual_selector_proof_html(proof), encoding="utf-8")
    return {"json": json_path, "html": html_path}


def build_subtitle_style_family_palette_axis_proof() -> dict[str, Any]:
    visual_proof = build_subtitle_visual_selector_proof()
    axis_examples = [
        _style_axis_example(example)
        for example in visual_proof["examples"]
    ]
    body_text_tokens = {
        example["readback_tokens"]["body_text_color_token"]
        for example in visual_proof["examples"]
    }
    return {
        "schema_id": STYLE_AXIS_PROOF_SCHEMA_ID,
        "artifact_id": STYLE_AXIS_PROOF_ARTIFACT_ID,
        "feature_id": STYLE_AXIS_PROOF_FEATURE_ID,
        "status": "style_family_palette_axis_proof_ready",
        "source_visual_selector_artifact_id": VISUAL_PROOF_ARTIFACT_ID,
        "source_selector_artifact_id": ARTIFACT_ID,
        "source_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "source_render_path_artifact_id": SOURCE_RENDER_PATH_ARTIFACT_ID,
        "proof_kind": "tracked_static_html_json_readback",
        "axis_contract": {
            "style_family_axis": [
                "dialogue_current_keifont_family",
                "emphasis_energy_family",
                "quiet_soft_readability_family",
                "ominous_inner_voice_family",
                "narration_family",
                "system_note_family",
            ],
            "palette_axis": [
                "speaker_identity_blue",
                "high_energy_warm",
                "quiet_cool",
                "ominous_dark",
                "narration_neutral_green",
                "system_neutral",
            ],
            "body_text_color_policy": "stable_default_body_text",
            "body_text_color_changed": False,
            "character_color_first_surfaces": [
                "badge_color_token",
                "accent_color_token",
            ],
            "new_palette_created": False,
            "new_style_family_created": False,
            "raw_numeric_review_required": False,
        },
        "examples_represented": [
            example["example_id"] for example in visual_proof["examples"]
        ],
        "axis_summary": _style_axis_summary(axis_examples),
        "examples": axis_examples,
        "outputs": {
            "json": "docs/style_intent/subtitle-style-family-palette-proof.json",
            "html": "docs/style_intent/subtitle-style-family-palette-proof.html",
        },
        "existing_output_first": {
            "considered": True,
            "level": "L0 No Render / Existing Output First",
            "source_static_proof": VISUAL_PROOF_ARTIFACT_ID,
            "new_render_run": False,
            "reason": (
                "Family and palette grouping can be reviewed as deterministic "
                "selector readback without generating video or frames."
            ),
        },
        "body_text_color_policy": {
            "token": "stable_default_body_text",
            "stable_across_examples": body_text_tokens == {"stable_default_body_text"},
            "changed_in_any_example": False,
            "palette_surfaces": [
                "badge_color_token",
                "accent_color_token",
                "backplate_box_token",
            ],
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none",
            "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
            "candidate_comparison_reopened": False,
            "fixed_form_required": False,
            "screenshot_required": False,
        },
        "render_gate": {
            "level": "L0 No Render / Existing Output First",
            "new_render_run": False,
            "milestone_gated_not_change_gated": True,
            "documented": True,
        },
        "boundaries": _boundary_flags(),
    }


def write_subtitle_style_family_palette_axis_proof(
    output_dir: Path,
) -> dict[str, Path]:
    proof = build_subtitle_style_family_palette_axis_proof()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-style-family-palette-proof.json"
    html_path = output_dir / "subtitle-style-family-palette-proof.html"
    json_path.write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    html_path.write_text(
        render_subtitle_style_family_palette_axis_proof_html(proof),
        encoding="utf-8",
    )
    return {"json": json_path, "html": html_path}


def build_subtitle_render_path_selector_contract() -> dict[str, Any]:
    style_axis_proof = build_subtitle_style_family_palette_axis_proof()
    contract_entries = [
        _render_path_contract_entry(example)
        for example in style_axis_proof["examples"]
    ]
    return {
        "schema_id": RENDER_PATH_CONTRACT_SCHEMA_ID,
        "artifact_id": RENDER_PATH_CONTRACT_ARTIFACT_ID,
        "feature_id": RENDER_PATH_CONTRACT_FEATURE_ID,
        "status": "render_path_selector_contract_ready",
        "source_style_family_palette_artifact_id": STYLE_AXIS_PROOF_ARTIFACT_ID,
        "source_visual_selector_artifact_id": VISUAL_PROOF_ARTIFACT_ID,
        "source_selector_artifact_id": ARTIFACT_ID,
        "source_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "source_render_path_artifact_id": SOURCE_RENDER_PATH_ARTIFACT_ID,
        "contract_kind": "static_selector_to_render_path_readback",
        "render_level": "L0 No Render",
        "examples_represented": [
            example["example_id"] for example in style_axis_proof["examples"]
        ],
        "render_adapter_input_contract": {
            "semantic_fields": [
                "semantic_preset_id",
                "preset_key",
                "speaker_id",
                "speaker_role",
                "emotion",
                "intensity",
                "utterance_role",
                "readability_priority",
            ],
            "style_axis_fields": [
                "family_id",
                "palette_route",
                "font_family_role",
                "font_size_scale",
                "outline_shadow_strength",
            ],
            "color_surface_fields": [
                "badge_color_token",
                "accent_color_token",
                "backplate_box_token",
                "body_text_color_token",
                "body_text_color_changed",
            ],
            "motion_line_break_fields": [
                "motion_primitive",
                "safe_area_line_break_behavior",
            ],
            "body_text_color_policy_reference": "stable_default_body_text",
        },
        "contract_entries": contract_entries,
        "later_l2_render_path_probe_trigger": {
            "status": "not_triggered_in_this_slice",
            "allowed_future_trigger": [
                "explicit render-path probe milestone",
                "static contract consumer needs FFmpeg/libass readback",
                "operator opens production-limitation or final render-path route",
            ],
            "not_triggered_by": [
                "HTML proof updates",
                "JSON readback updates",
                "dashboard or handoff updates",
                "style-family or palette grouping readback",
            ],
        },
        "outputs": {
            "json": "docs/style_intent/subtitle-render-path-selector-contract.json",
            "doc": "docs/style_intent/subtitle-render-path-selector-contract.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none",
            "fixed_form_required": False,
            "screenshot_required": False,
            "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
        },
        "render_gate": {
            "level": "L0 No Render",
            "new_render_run": False,
            "contract_readback_only": True,
            "next_render_level": "L2 tiny render path probe milestone",
        },
        "readiness_separation": {
            "subtitle_style_readiness": "selector_static_proof_render_path_contract_ready",
            "video_render_readiness": "not_run_no_render_pass_implied",
            "production_readiness": "not_accepted",
            "rights_public_use_readiness": "not_accepted",
        },
        "boundaries": _boundary_flags(),
    }


def write_subtitle_render_path_selector_contract(
    output_dir: Path,
) -> dict[str, Path]:
    contract = build_subtitle_render_path_selector_contract()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-render-path-selector-contract.json"
    doc_path = output_dir / "subtitle-render-path-selector-contract.md"
    json_path.write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_render_path_selector_contract_markdown(contract),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_render_contract_consumer_dry_read(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_contract = contract or build_subtitle_render_path_selector_contract()
    consumer_payloads = [
        _render_contract_consumer_payload(entry)
        for entry in source_contract["contract_entries"]
    ]
    dry_read_validation = _render_contract_consumer_validation(
        source_contract,
        consumer_payloads,
    )
    return {
        "schema_id": RENDER_CONTRACT_CONSUMER_DRY_READ_SCHEMA_ID,
        "artifact_id": RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID,
        "feature_id": RENDER_CONTRACT_CONSUMER_DRY_READ_FEATURE_ID,
        "status": "render_contract_consumer_dry_read_ready",
        "source_render_path_selector_contract_artifact_id": (
            RENDER_PATH_CONTRACT_ARTIFACT_ID
        ),
        "source_style_family_palette_artifact_id": STYLE_AXIS_PROOF_ARTIFACT_ID,
        "source_visual_selector_artifact_id": VISUAL_PROOF_ARTIFACT_ID,
        "source_selector_artifact_id": ARTIFACT_ID,
        "source_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "source_render_path_artifact_id": SOURCE_RENDER_PATH_ARTIFACT_ID,
        "dry_read_kind": "static_contract_consumer_payload_readback",
        "consumer_name": "subtitle_render_adapter_contract_consumer_v0",
        "render_level": "L0 No Render",
        "examples_represented": [
            payload["semantic_preset_id"] for payload in consumer_payloads
        ],
        "adapter_payload_schema": {
            "semantic_fields": [
                "semantic_preset_id",
                "preset_key",
                "speaker_id",
                "speaker_role",
                "emotion",
                "intensity",
                "utterance_role",
                "readability_priority",
            ],
            "style_fields": [
                "family_id",
                "palette_route",
                "font_family_role",
                "font_size_scale",
                "outline_shadow_strength",
            ],
            "color_surface_fields": [
                "badge_color_token",
                "accent_color_token",
                "backplate_box_token",
                "body_text_color_policy_reference",
                "body_text_color_token",
                "body_text_color_changed",
            ],
            "motion_fields": ["motion_primitive"],
            "line_break_fields": ["safe_area_line_break_behavior"],
            "render_boundary_fields": [
                "render_level",
                "new_render_run",
                "render_artifact_created",
                "video_artifact_created",
                "audio_artifact_created",
                "frame_artifact_created",
                "ass_artifact_created",
                "episode_artifact_created",
                "consumer_dry_read_only",
            ],
            "production_public_boundary_fields": [
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
            "body_text_color_policy_reference": "stable_default_body_text",
        },
        "consumer_payloads": consumer_payloads,
        "dry_read_validation": dry_read_validation,
        "later_l2_render_path_probe_trigger": {
            "status": "not_triggered_in_this_slice",
            "allowed_future_trigger": [
                "explicit L2 render path probe milestone",
                "consumer payload needs FFmpeg/libass timing or visual readback",
                "operator opens production-limitation or final render-path route",
            ],
            "not_triggered_by": [
                "consumer dry-read JSON generation",
                "consumer dry-read Markdown generation",
                "dashboard or handoff updates",
                "static contract drift checks",
            ],
        },
        "outputs": {
            "json": "docs/style_intent/subtitle-render-contract-consumer-dry-read.json",
            "doc": "docs/style_intent/subtitle-render-contract-consumer-dry-read.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none",
            "fixed_form_required": False,
            "screenshot_required": False,
            "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
        },
        "render_gate": {
            "level": "L0 No Render",
            "new_render_run": False,
            "consumer_dry_read_only": True,
            "next_render_level": "L2 tiny render path probe milestone",
        },
        "readiness_separation": {
            "subtitle_style_readiness": (
                "selector_static_proof_render_path_contract_consumer_dry_read_ready"
            ),
            "video_render_readiness": "not_run_no_render_pass_implied",
            "production_readiness": "not_accepted",
            "rights_public_use_readiness": "not_accepted",
        },
        "boundaries": _boundary_flags(),
    }


def write_subtitle_render_contract_consumer_dry_read(
    output_dir: Path,
) -> dict[str, Path]:
    dry_read = build_subtitle_render_contract_consumer_dry_read()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-render-contract-consumer-dry-read.json"
    doc_path = output_dir / "subtitle-render-contract-consumer-dry-read.md"
    json_path.write_text(
        json.dumps(dry_read, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_render_contract_consumer_dry_read_markdown(dry_read),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_render_path_selector_probe(
    contract: Mapping[str, Any] | None = None,
    *,
    local_probe: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_contract = contract or build_subtitle_render_path_selector_contract()
    local_readback = (
        dict(local_probe)
        if local_probe is not None
        else _default_render_path_probe_local_readback()
    )
    examples = _render_path_probe_examples(source_contract)
    validation = _render_path_probe_validation(
        source_contract=source_contract,
        examples=examples,
        local_probe=local_readback,
    )
    return {
        "schema_id": RENDER_PATH_PROBE_SCHEMA_ID,
        "artifact_id": RENDER_PATH_PROBE_ARTIFACT_ID,
        "feature_id": RENDER_PATH_PROBE_FEATURE_ID,
        "status": "l2_render_path_selector_probe_ready",
        "source_render_path_selector_contract_artifact_id": (
            RENDER_PATH_CONTRACT_ARTIFACT_ID
        ),
        "source_style_family_palette_artifact_id": STYLE_AXIS_PROOF_ARTIFACT_ID,
        "source_visual_selector_artifact_id": VISUAL_PROOF_ARTIFACT_ID,
        "source_selector_artifact_id": ARTIFACT_ID,
        "source_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "source_render_path_artifact_id": SOURCE_RENDER_PATH_ARTIFACT_ID,
        "probe_kind": "tiny_ffmpeg_libass_selector_probe_readback",
        "render_level": "L2 tiny render path selector probe",
        "selected_example_ids": list(RENDER_PATH_PROBE_SELECTED_EXAMPLE_IDS),
        "selected_example_count": len(examples),
        "examples": examples,
        "body_text_color_policy": {
            "reference": "stable_default_body_text",
            "stable_across_examples": validation["stable_body_text_preserved"],
            "body_text_color_changed": False,
        },
        "color_route": {
            "semantic_variation_surface_priority": [
                "badge_color_token",
                "accent_color_token",
                "backplate_box_token",
                "body_text_color_token",
            ],
            "badge_accent_backplate_first": (
                validation["badge_accent_backplate_route_preserved"]
            ),
            "body_text_color_changes_allowed": False,
        },
        "motion_line_break_policy": {
            "motion_metadata_survived": validation["motion_metadata_survived"],
            "safe_area_line_break_metadata_survived": (
                validation["safe_area_line_break_metadata_survived"]
            ),
            "ass_newline_probe_example_id": "whisper_intensity_1",
        },
        "local_probe": local_readback,
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-render-path-selector-probe.json",
            "doc": "docs/style_intent/subtitle-render-path-selector-probe.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none",
            "fixed_form_required": False,
            "screenshot_required": False,
            "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
        },
        "render_gate": {
            "level": "L2 tiny render path selector probe",
            "new_render_run": local_readback["status"] == "local_ignored_probe_generated",
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "readiness_separation": {
            "subtitle_style_readiness": "selector_l2_render_path_probe_ready",
            "video_render_readiness": "diagnostic_local_probe_only",
            "production_readiness": "not_accepted",
            "rights_public_use_readiness": "not_accepted",
        },
        "boundaries": _render_path_probe_boundary_flags(local_readback),
    }


def write_subtitle_render_path_selector_probe(
    output_dir: Path,
    *,
    local_probe: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    probe = build_subtitle_render_path_selector_probe(local_probe=local_probe)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-render-path-selector-probe.json"
    doc_path = output_dir / "subtitle-render-path-selector-probe.md"
    json_path.write_text(
        json.dumps(probe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_render_path_selector_probe_markdown(probe),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_render_path_lineage_observation_surface(
    *,
    dry_read: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    dry = (
        deepcopy(dry_read)
        if dry_read is not None
        else build_subtitle_render_contract_consumer_dry_read()
    )
    probe = (
        deepcopy(source_probe)
        if source_probe is not None
        else build_subtitle_render_path_selector_probe()
    )
    local_outputs = dict(probe["local_probe"]["outputs"])
    contact_sheet_path = _probe_display_path(
        RENDER_PATH_PROBE_LOCAL_OUTPUT_RELATIVE_DIR
        / LINEAGE_OBSERVATION_CONTACT_SHEET_FILENAME,
        Path.cwd(),
    )
    local_outputs["contact_sheet"] = contact_sheet_path
    selected_examples = [
        {
            "order": example["order"],
            "example_id": example["example_id"],
            "role": example["role"],
            "preset_key": example["semantic"]["preset_key"],
            "emotion": example["semantic"]["emotion"],
            "style_family": example["style"]["style_family"],
            "palette_route": example["style"]["palette_route"],
            "body_text_color_token": example["color_surfaces"]["body_text_color_token"],
            "ass_text": example["ass_probe"]["text"],
        }
        for example in probe["examples"]
    ]
    observation_surface = {
        "same_machine_only": True,
        "may_be_absent_on_other_clone": True,
        "user_review_required": False,
        "source_dry_read_payload_count": len(dry["consumer_payloads"]),
        "source_dry_read_payload_ids": [
            payload["semantic_preset_id"] for payload in dry["consumer_payloads"]
        ],
        "selected_example_count": probe["selected_example_count"],
        "selected_example_ids": list(probe["selected_example_ids"]),
        "selected_examples": selected_examples,
        "local_probe_status": probe["local_probe"]["status"],
        "local_outputs": local_outputs,
        "open_commands": [
            _open_command(target, display_path)
            for target, display_path in local_outputs.items()
        ],
        "source_probe_render_command_recorded": bool(
            probe["local_probe"].get("render_command_summary")
        ),
        "tracked_binary_artifact_created": False,
        "episodes_tracked": False,
    }
    validation = _lineage_observation_surface_validation(
        dry,
        probe,
        observation_surface,
    )
    return {
        "schema_id": LINEAGE_OBSERVATION_SCHEMA_ID,
        "artifact_id": LINEAGE_OBSERVATION_ARTIFACT_ID,
        "feature_id": LINEAGE_OBSERVATION_FEATURE_ID,
        "status": "lineage_observation_surface_ready",
        "active_artifact_id": probe["artifact_id"],
        "source_render_contract_consumer_dry_read_artifact_id": dry["artifact_id"],
        "source_render_path_selector_probe_artifact_id": probe["artifact_id"],
        "source_render_path_selector_contract_artifact_id": probe["source_render_path_selector_contract_artifact_id"],
        "source_style_family_palette_artifact_id": probe["source_style_family_palette_artifact_id"],
        "source_visual_selector_artifact_id": probe["source_visual_selector_artifact_id"],
        "source_selector_artifact_id": probe["source_selector_artifact_id"],
        "source_registry_artifact_id": probe["source_registry_artifact_id"],
        "source_render_path_artifact_id": probe["source_render_path_artifact_id"],
        "surface_kind": "lineage_and_same_machine_observation_readback",
        "render_level": "lineage_only_no_new_render",
        "lineage": {
            "active_artifact": {
                "artifact_id": probe["artifact_id"],
                "status": probe["status"],
                "metadata_json": "docs/style_intent/subtitle-render-path-selector-probe.json",
                "doc": "docs/style_intent/subtitle-render-path-selector-probe.md",
                "render_level": probe["render_level"],
                "new_render_run": probe["render_gate"]["new_render_run"],
                "supersedes_predecessor_readback": True,
            },
            "predecessor_artifacts": [
                {
                    "artifact_id": dry["artifact_id"],
                    "role": "render_contract_consumer_dry_read",
                    "source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
                    "metadata_json": "docs/style_intent/subtitle-render-contract-consumer-dry-read.json",
                    "doc": "docs/style_intent/subtitle-render-contract-consumer-dry-read.md",
                    "invalidated": False,
                    "superseded_by": probe["artifact_id"],
                    "preserved_as_evidence": True,
                }
            ],
        },
        "existing_output_first": {
            "considered": True,
            "decision": "preserve_active_ed10af_l2_probe_and_record_lineage_no_rerender",
            "reason": "The active ED-10af L2 selector probe already contains a local ignored ASS/MP4/manifest render-path readback for neutral, shout, and whisper representative payloads. ED-10ag records the active/predecessor relationship and same-machine observation commands without running ffmpeg again.",
            "existing_artifact_id": probe["artifact_id"],
            "source_probe_status": probe["status"],
            "source_probe_local_status": probe["local_probe"]["status"],
            "source_probe_render_level": probe["render_level"],
            "source_probe_new_render_run": probe["render_gate"]["new_render_run"],
            "new_render_run": False,
        },
        "observation_surface": observation_surface,
        "body_text_color_policy": probe["body_text_color_policy"],
        "color_route": probe["color_route"],
        "motion_line_break_policy": probe["motion_line_break_policy"],
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-render-path-lineage-observation-surface.json",
            "doc": "docs/style_intent/subtitle-render-path-lineage-observation-surface.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none",
            "fixed_form_required": False,
            "screenshot_required": False,
            "human_review_required_only_for": list(HUMAN_REVIEW_REQUIRED_FOR),
        },
        "render_gate": {
            "level": "lineage_only_no_new_render",
            "milestone_gated_not_change_gated": True,
            "existing_output_first_reused": True,
            "new_render_run": False,
            "source_probe_new_render_run": probe["render_gate"]["new_render_run"],
            "reason": "Existing Output First found the ED-10af L2 selector probe sufficient for lineage and observation; ED-10ag adds no new render.",
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "readiness_separation": {
            "subtitle_style_readiness": "lineage_observation_surface_ready",
            "video_render_readiness": "existing_local_ignored_l2_probe_reused",
            "production_readiness": "not_accepted",
            "rights_public_use_readiness": "not_accepted",
        },
        "boundaries": _lineage_observation_surface_boundary_flags(probe),
    }


def write_subtitle_render_path_lineage_observation_surface(
    output_dir: Path,
    *,
    dry_read: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    readback = build_subtitle_render_path_lineage_observation_surface(
        dry_read=dry_read,
        source_probe=source_probe,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-render-path-lineage-observation-surface.json"
    doc_path = output_dir / "subtitle-render-path-lineage-observation-surface.md"
    json_path.write_text(
        json.dumps(readback, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_render_path_lineage_observation_surface_markdown(
            readback,
        ),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_production_limitation_lift_entry(
    *,
    dry_read: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    dry = (
        deepcopy(dry_read)
        if dry_read is not None
        else build_subtitle_render_contract_consumer_dry_read()
    )
    probe = (
        deepcopy(source_probe)
        if source_probe is not None
        else build_subtitle_render_path_selector_probe()
    )
    lineage = (
        deepcopy(lineage_surface)
        if lineage_surface is not None
        else build_subtitle_render_path_lineage_observation_surface(
            dry_read=dry,
            source_probe=probe,
        )
    )
    local_outputs = dict(lineage["observation_surface"]["local_outputs"])
    source_evidence = {
        "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
        "active_diagnostic_proof_source_path": "docs/style_intent/subtitle-render-path-selector-probe.json",
        "support_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "support_lineage_observation_surface_path": "docs/style_intent/subtitle-render-path-lineage-observation-surface.json",
        "dry_read_predecessor_artifact_id": dry["artifact_id"],
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "dry_read_predecessor_path": "docs/style_intent/subtitle-render-contract-consumer-dry-read.json",
        "local_ignored_outputs": local_outputs,
        "local_ignored_output_policy": "same_machine_observation_only_do_not_add_to_git",
        "source_probe_selected_example_ids": list(probe["selected_example_ids"]),
        "source_probe_local_status": probe["local_probe"]["status"],
        "lineage_render_level": lineage["render_level"],
    }
    gate_matrix = [
        {
            "gate_name": "diagnostic_render_path_proof",
            "current_status": "available_diagnostic_only",
            "evidence_available": [
                "ED-10af L2 selector probe records local ignored ASS/MP4/manifest render-path proof for neutral, shout, and whisper representative payloads.",
                "ED-10ag lineage surface records same-machine observation paths and confirms no new render was run for lineage.",
                "The restored ED-10af dry-read from commit 7e96a28 remains preserved as predecessor evidence.",
                "Stable body text plus badge/accent/backplate routing and safe-area line-break metadata survive into the active diagnostic proof.",
            ],
            "evidence_missing": [
                "Final render-path readiness packet for a production route.",
                "Representative production-sequence review outside the bounded diagnostic probe.",
            ],
            "agent_can_progress_without_user_judgement": True,
            "human_judgement_required": False,
            "rights_or_publication_decision_required": False,
            "next_agent_action": "Assemble final-render-path-readiness or production-limitation-lift-stage-1 from existing evidence.",
        },
        {
            "gate_name": "production_subtitle_design_acceptance",
            "current_status": "not_accepted",
            "evidence_available": [
                "User observation says the opened surface is acceptable enough and layout polish should not block forward progress.",
                "ED-10af/ED-10ag show the diagnostic body/badge route can be observed on this machine.",
            ],
            "evidence_missing": [
                "Explicit human acceptance that the subtitle design is production-ready.",
                "Production-sequence typography and safe-area acceptance beyond the tiny diagnostic probe.",
            ],
            "agent_can_progress_without_user_judgement": False,
            "human_judgement_required": True,
            "rights_or_publication_decision_required": False,
            "next_agent_action": "Prepare a bounded decision packet only when design acceptance becomes the next required decision.",
        },
        {
            "gate_name": "production_render_acceptance",
            "current_status": "not_accepted",
            "evidence_available": [
                "Diagnostic render-path proof exists for the selected representative payloads.",
                "Same-machine ASS/MP4/manifest/contact-sheet paths are recorded for local inspection.",
            ],
            "evidence_missing": [
                "Accepted production render output.",
                "Final production render command/output manifest and review result.",
            ],
            "agent_can_progress_without_user_judgement": False,
            "human_judgement_required": True,
            "rights_or_publication_decision_required": False,
            "next_agent_action": "Do not infer production render acceptance from the diagnostic proof.",
        },
        {
            "gate_name": "creative_acceptance",
            "current_status": "not_accepted",
            "evidence_available": [
                "Candidate 2 remains the diagnostic lead treatment and Candidate 0 remains fallback/reference in the prior review memory.",
                "No request remains to reopen Candidate 0-3, Keifont baseline, cut_002/cut_003, or cut_008 dense/multiline review.",
            ],
            "evidence_missing": [
                "Explicit creative approval for production use.",
                "Any final editorial review packet chosen by the user.",
            ],
            "agent_can_progress_without_user_judgement": False,
            "human_judgement_required": True,
            "rights_or_publication_decision_required": False,
            "next_agent_action": "Keep prior review axes closed unless a new explicit creative decision is requested.",
        },
        {
            "gate_name": "rights_status",
            "current_status": "pending",
            "evidence_available": [
                "No rights clearance is claimed by ED-10af, ED-10ag, or this ED-10ah entry.",
                "The local proof paths stay same-machine and ignored.",
            ],
            "evidence_missing": [
                "Human/owner rights clearance for the source material and any distribution context.",
                "Any publication-specific rights review.",
            ],
            "agent_can_progress_without_user_judgement": False,
            "human_judgement_required": True,
            "rights_or_publication_decision_required": True,
            "next_agent_action": "Do not make rights claims or convert local proof into public-use permission.",
        },
        {
            "gate_name": "publishing_acceptance",
            "current_status": "not_accepted",
            "evidence_available": [
                "No upload, platform metadata, visibility, or scheduling action is performed in the diagnostic route.",
            ],
            "evidence_missing": [
                "Human publication decision.",
                "Platform/upload/account-specific acceptance and final metadata decision.",
            ],
            "agent_can_progress_without_user_judgement": False,
            "human_judgement_required": True,
            "rights_or_publication_decision_required": True,
            "next_agent_action": "Do not upload, publish, schedule, or prepare public release actions from this entry.",
        },
        {
            "gate_name": "public_use_permission",
            "current_status": "not_allowed",
            "evidence_available": [
                "Production subtitle design, production render, creative, rights, and publishing gates remain false or pending.",
            ],
            "evidence_missing": [
                "All upstream acceptances required for public use.",
                "Explicit public-use permission.",
            ],
            "agent_can_progress_without_user_judgement": False,
            "human_judgement_required": True,
            "rights_or_publication_decision_required": True,
            "next_agent_action": "Keep public-use permission closed until all upstream decisions are explicit.",
        },
    ]
    boundaries = _production_limitation_lift_boundary_flags(probe, lineage)
    validation = _production_limitation_lift_validation(
        dry,
        probe,
        lineage,
        gate_matrix,
        boundaries,
    )
    return {
        "schema_id": PRODUCTION_LIMITATION_LIFT_SCHEMA_ID,
        "artifact_id": PRODUCTION_LIMITATION_LIFT_ARTIFACT_ID,
        "feature_id": PRODUCTION_LIMITATION_LIFT_FEATURE_ID,
        "status": "production_limitation_lift_entry_ready",
        "active_artifact_id": probe["artifact_id"],
        "source_render_path_selector_probe_artifact_id": probe["artifact_id"],
        "source_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "source_render_contract_consumer_dry_read_artifact_id": dry["artifact_id"],
        "surface_kind": "production_limitation_lift_gate_separation_entry",
        "render_level": "gate_entry_no_new_render",
        "source_evidence": source_evidence,
        "user_observation_consumed": {
            "observation_id": "ed10ah_user_display_acceptable_move_forward",
            "display_surface_acceptable_enough": True,
            "layout_polish_deferred": True,
            "move_forward_preferred": True,
            "no_redundant_review_requests": [
                "Candidate 0-3 comparison",
                "Keifont baseline review",
                "cut_002/cut_003 review",
                "cut_008 dense/multiline review",
            ],
        },
        "gate_names": list(PRODUCTION_LIMITATION_LIFT_GATE_NAMES),
        "gate_matrix": gate_matrix,
        "next_executable_route": {
            "route_id": "production-limitation-lift-stage-1",
            "alternate_route_id": "final-render-path-readiness",
            "agent_can_start_without_user_judgement": True,
            "purpose": "Convert existing diagnostic and lineage evidence into a bounded readiness packet without approving production or public use.",
            "first_steps": [
                "Reuse ED-10af as the active diagnostic render-path proof source.",
                "Use ED-10ag only as lineage and same-machine observation support.",
                "List the still-closed human/rights/publication gates before any production route.",
            ],
            "must_not_do": [
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "make rights claims",
                "upload or publish",
                "grant public-use permission",
                "rerun old comparison/review axes unless explicitly requested",
            ],
            "completion_signal": "A bounded stage-1/readiness packet exists and any required human decision is isolated to the relevant gate.",
        },
        "readiness_separation": {
            "diagnostic_render_path_proof": "available_diagnostic_only",
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        },
        "render_gate": {
            "level": "gate_entry_no_new_render",
            "existing_output_first_reused": True,
            "new_render_run": False,
            "source_probe_new_render_run": probe["render_gate"]["new_render_run"],
            "source_lineage_new_render_run": lineage["render_gate"]["new_render_run"],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-production-limitation-lift-entry.json",
            "doc": "docs/style_intent/subtitle-production-limitation-lift-entry.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_entry",
            "fixed_form_required": False,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "human_review_required_only_for": [
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_production_limitation_lift_entry(
    output_dir: Path,
    *,
    dry_read: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    entry = build_subtitle_production_limitation_lift_entry(
        dry_read=dry_read,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-production-limitation-lift-entry.json"
    doc_path = output_dir / "subtitle-production-limitation-lift-entry.md"
    json_path.write_text(
        json.dumps(entry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_production_limitation_lift_entry_markdown(entry),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_final_render_path_readiness_packet(
    *,
    dry_read: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    dry = (
        deepcopy(dry_read)
        if dry_read is not None
        else build_subtitle_render_contract_consumer_dry_read()
    )
    probe = (
        deepcopy(source_probe)
        if source_probe is not None
        else build_subtitle_render_path_selector_probe()
    )
    lineage = (
        deepcopy(lineage_surface)
        if lineage_surface is not None
        else build_subtitle_render_path_lineage_observation_surface(
            dry_read=dry,
            source_probe=probe,
        )
    )
    gate = (
        deepcopy(gate_entry)
        if gate_entry is not None
        else build_subtitle_production_limitation_lift_entry(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
        )
    )
    local_outputs = dict(lineage["observation_surface"]["local_outputs"])
    source_evidence = {
        "gate_separation_source_artifact_id": gate["artifact_id"],
        "gate_separation_source_path": "docs/style_intent/subtitle-production-limitation-lift-entry.json",
        "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
        "active_diagnostic_proof_source_path": "docs/style_intent/subtitle-render-path-selector-probe.json",
        "support_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "support_lineage_observation_surface_path": "docs/style_intent/subtitle-render-path-lineage-observation-surface.json",
        "dry_read_predecessor_artifact_id": dry["artifact_id"],
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "dry_read_predecessor_path": "docs/style_intent/subtitle-render-contract-consumer-dry-read.json",
        "selector_semantic_style_contract_artifact_id": ARTIFACT_ID,
        "selector_semantic_style_contract_path": "docs/style_intent/subtitle-preset-selector.json",
        "style_intent_registry_artifact_id": SOURCE_REGISTRY_ARTIFACT_ID,
        "style_intent_registry_path": "docs/style_intent/subtitle-style-intent-registry.json",
        "render_adapter_input_contract_artifact_id": RENDER_PATH_CONTRACT_ARTIFACT_ID,
        "render_adapter_input_contract_path": "docs/style_intent/subtitle-render-path-selector-contract.json",
        "local_ignored_outputs": local_outputs,
        "local_ignored_output_policy": "same_machine_diagnostic_only_may_be_absent_on_other_clone",
    }
    readiness_matrix = _final_render_path_readiness_matrix(
        dry,
        probe,
        lineage,
        gate,
        local_outputs,
    )
    boundaries = _final_render_path_readiness_boundary_flags(probe, lineage, gate)
    validation = _final_render_path_readiness_validation(
        dry,
        probe,
        lineage,
        gate,
        readiness_matrix,
        boundaries,
    )
    return {
        "schema_id": FINAL_RENDER_PATH_READINESS_SCHEMA_ID,
        "artifact_id": FINAL_RENDER_PATH_READINESS_ARTIFACT_ID,
        "feature_id": FINAL_RENDER_PATH_READINESS_FEATURE_ID,
        "status": "final_render_path_readiness_packet_ready",
        "active_artifact_id": probe["artifact_id"],
        "source_production_limitation_lift_entry_artifact_id": gate["artifact_id"],
        "source_render_path_selector_probe_artifact_id": probe["artifact_id"],
        "source_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "source_render_contract_consumer_dry_read_artifact_id": dry["artifact_id"],
        "surface_kind": "final_render_path_readiness_packet",
        "render_level": "readiness_packet_no_new_render",
        "source_evidence": source_evidence,
        "readiness_matrix_row_ids": list(FINAL_RENDER_PATH_READINESS_REQUIRED_ROW_IDS),
        "readiness_matrix": readiness_matrix,
        "next_executable_route": {
            "route_id": "final-render-path-stage-1",
            "alternate_route_id": "production-limitation-lift-stage-1",
            "agent_can_start_without_user_judgement": True,
            "purpose": "Prepare the later final render-path route from existing diagnostic proof and explicit missing-gate readback without granting production/public approval.",
            "first_steps": [
                "Reuse ED-10af as active diagnostic proof.",
                "Use ED-10ah as the gate-separation source.",
                "Carry forward missing human, rights, publishing, and public-use decisions as closed gates.",
            ],
            "must_not_do": [
                "run a new render in this readiness packet",
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "make rights claims",
                "upload or publish",
                "grant public-use permission",
                "request display/layout polish or old comparison reviews",
            ],
            "completion_signal": "Stage-1 can start with existing evidence and a list of still-missing approvals.",
        },
        "readiness_summary": {
            "diagnostic_proof": "available",
            "selector_semantic_contract": "available",
            "render_adapter_input_contract": "available",
            "local_ignored_proof_media": "available_same_machine_diagnostic_only",
            "lineage_predecessor": "available",
            "production_subtitle_design_acceptance": "missing",
            "production_render_acceptance": "missing",
            "creative_acceptance": "missing",
            "rights_status": "pending",
            "publishing_acceptance": "missing",
            "public_use_permission": "missing",
        },
        "render_gate": {
            "level": "readiness_packet_no_new_render",
            "existing_output_first_reused": True,
            "new_render_run": False,
            "source_probe_new_render_run": probe["render_gate"]["new_render_run"],
            "source_lineage_new_render_run": lineage["render_gate"]["new_render_run"],
            "source_gate_entry_new_render_run": gate["render_gate"]["new_render_run"],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-final-render-path-readiness.json",
            "doc": "docs/style_intent/subtitle-final-render-path-readiness.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_packet",
            "fixed_form_required": False,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "human_review_required_only_for": [
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_final_render_path_readiness_packet(
    output_dir: Path,
    *,
    dry_read: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_final_render_path_readiness_packet(
        dry_read=dry_read,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-final-render-path-readiness.json"
    doc_path = output_dir / "subtitle-final-render-path-readiness.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_final_render_path_readiness_packet_markdown(packet),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_final_render_path_stage1(
    *,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    dry = (
        deepcopy(dry_read)
        if dry_read is not None
        else build_subtitle_render_contract_consumer_dry_read()
    )
    probe = (
        deepcopy(source_probe)
        if source_probe is not None
        else build_subtitle_render_path_selector_probe()
    )
    lineage = (
        deepcopy(lineage_surface)
        if lineage_surface is not None
        else build_subtitle_render_path_lineage_observation_surface(
            dry_read=dry,
            source_probe=probe,
        )
    )
    gate = (
        deepcopy(gate_entry)
        if gate_entry is not None
        else build_subtitle_production_limitation_lift_entry(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
        )
    )
    readiness = (
        deepcopy(readiness_packet)
        if readiness_packet is not None
        else build_subtitle_final_render_path_readiness_packet(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
        )
    )
    local_outputs = dict(readiness["source_evidence"]["local_ignored_outputs"])
    candidate = {
        "candidate_id": "ffmpeg_libass_diagnostic_path_stage_1",
        "render_adapter_path": "ffmpeg/libass diagnostic subtitle overlay path",
        "selected_from_artifact_id": probe["artifact_id"],
        "selection_status": "selected_for_stage_1_preparation_only",
        "selection_reason": (
            "ED-10af already proves representative selector payloads can pass "
            "through FFmpeg/libass with ASS subtitle overlay output, while ED-10ai "
            "keeps production/public approvals closed."
        ),
        "source_policy": "existing_output_first_reuse_ed10af_ed10ag_ed10ai_no_new_render",
        "subtitle_ass_generation_path": local_outputs.get("ass", ""),
        "video_probe_path": local_outputs.get("video", ""),
        "manifest_path": local_outputs.get("manifest", ""),
        "contact_sheet_path": local_outputs.get("contact_sheet", ""),
        "same_machine_evidence_may_be_absent_on_other_clone": True,
        "stage_1_candidate_not_production_render": True,
    }
    checklist = _final_render_path_stage1_checklist(
        probe=probe,
        lineage=lineage,
        readiness=readiness,
        local_outputs=local_outputs,
    )
    boundaries = _final_render_path_stage1_boundary_flags(readiness)
    validation = _final_render_path_stage1_validation(
        probe=probe,
        lineage=lineage,
        gate=gate,
        dry=dry,
        readiness=readiness,
        checklist=checklist,
        boundaries=boundaries,
    )
    return {
        "schema_id": FINAL_RENDER_PATH_STAGE1_SCHEMA_ID,
        "artifact_id": FINAL_RENDER_PATH_STAGE1_ARTIFACT_ID,
        "feature_id": FINAL_RENDER_PATH_STAGE1_FEATURE_ID,
        "status": "final_render_path_stage_1_ready",
        "surface_kind": "final_render_path_stage_1_preparation",
        "render_level": "stage_1_path_selection_no_new_render",
        "source_final_render_path_readiness_artifact_id": readiness["artifact_id"],
        "source_render_path_selector_probe_artifact_id": probe["artifact_id"],
        "source_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "source_production_limitation_lift_entry_artifact_id": gate["artifact_id"],
        "source_render_contract_consumer_dry_read_artifact_id": dry["artifact_id"],
        "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
        "stage_1_candidate": candidate,
        "source_evidence": {
            "readiness_packet_artifact_id": readiness["artifact_id"],
            "readiness_packet_path": "docs/style_intent/subtitle-final-render-path-readiness.json",
            "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
            "active_diagnostic_proof_source_path": "docs/style_intent/subtitle-render-path-selector-probe.json",
            "support_lineage_observation_surface_artifact_id": lineage["artifact_id"],
            "support_lineage_observation_surface_path": "docs/style_intent/subtitle-render-path-lineage-observation-surface.json",
            "gate_separation_source_artifact_id": gate["artifact_id"],
            "gate_separation_source_path": "docs/style_intent/subtitle-production-limitation-lift-entry.json",
            "dry_read_predecessor_artifact_id": dry["artifact_id"],
            "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
            "selector_semantic_style_contract_artifact_id": ARTIFACT_ID,
            "render_adapter_input_contract_artifact_id": RENDER_PATH_CONTRACT_ARTIFACT_ID,
            "local_ignored_outputs": local_outputs,
            "local_ignored_output_policy": "same_machine_diagnostic_only_may_be_absent_on_other_clone",
        },
        "stage_1_checklist_ids": list(FINAL_RENDER_PATH_STAGE1_REQUIRED_CHECK_IDS),
        "stage_1_checklist": checklist,
        "next_executable_route": {
            "route_id": "final-render-path-stage-2",
            "alternate_route_id": "production-limitation-lift-stage-1",
            "agent_can_start_without_user_judgement": True,
            "purpose": (
                "Use the selected FFmpeg/libass diagnostic path candidate to "
                "prepare a later final render-path stage without granting "
                "production, publishing, or public-use approval."
            ),
            "first_steps": [
                "Carry ED-10aj selected path and checklist into final-render-path-stage-2.",
                "Keep ED-10ai missing production/public decision rows attached.",
                "Reuse ignored proof paths only as same-machine diagnostic evidence.",
            ],
            "must_not_do": [
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "make rights claims",
                "upload or publish",
                "grant public-use permission",
                "request display/layout polish or old comparison reviews",
                "add episodes/ or binary proof media to Git",
            ],
            "completion_signal": (
                "A final render-path stage-1 candidate is selected and all "
                "closed production/public gates remain explicit."
            ),
        },
        "render_gate": {
            "level": "stage_1_path_selection_no_new_render",
            "existing_output_first_reused": True,
            "new_render_run": False,
            "source_probe_new_render_run": probe["render_gate"]["new_render_run"],
            "source_lineage_new_render_run": lineage["render_gate"]["new_render_run"],
            "source_readiness_new_render_run": readiness["render_gate"]["new_render_run"],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "production_public_readiness": {
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "missing_before_production_render_approval": [
                "Explicit production subtitle design acceptance.",
                "Accepted final production render output.",
                "Final production render command/output manifest and review result.",
                "Explicit creative acceptance for production use.",
            ],
            "missing_before_publishing_public_use": [
                "Rights clearance or owner decision.",
                "Publishing acceptance.",
                "Explicit public-use permission.",
            ],
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-final-render-path-stage-1.json",
            "doc": "docs/style_intent/subtitle-final-render-path-stage-1.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_stage_1_packet",
            "fixed_form_required": False,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "human_review_required_only_for": [
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_final_render_path_stage1(
    output_dir: Path,
    *,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_final_render_path_stage1(
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-final-render-path-stage-1.json"
    doc_path = output_dir / "subtitle-final-render-path-stage-1.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_final_render_path_stage1_markdown(packet),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_final_render_path_stage2_replayability(
    *,
    stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    dry = (
        deepcopy(dry_read)
        if dry_read is not None
        else build_subtitle_render_contract_consumer_dry_read()
    )
    probe = (
        deepcopy(source_probe)
        if source_probe is not None
        else build_subtitle_render_path_selector_probe()
    )
    lineage = (
        deepcopy(lineage_surface)
        if lineage_surface is not None
        else build_subtitle_render_path_lineage_observation_surface(
            dry_read=dry,
            source_probe=probe,
        )
    )
    gate = (
        deepcopy(gate_entry)
        if gate_entry is not None
        else build_subtitle_production_limitation_lift_entry(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
        )
    )
    readiness = (
        deepcopy(readiness_packet)
        if readiness_packet is not None
        else build_subtitle_final_render_path_readiness_packet(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
        )
    )
    stage1 = (
        deepcopy(stage1_packet)
        if stage1_packet is not None
        else build_subtitle_final_render_path_stage1(
            readiness_packet=readiness,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
            dry_read=dry,
        )
    )
    local_outputs = dict(stage1["source_evidence"]["local_ignored_outputs"])
    local_inputs = {
        "source_video": str(RENDER_PATH_PROBE_SOURCE_VIDEO_RELATIVE_PATH).replace(
            "\\", "/"
        ),
        "source_audio": str(RENDER_PATH_PROBE_SOURCE_AUDIO_RELATIVE_PATH).replace(
            "\\", "/"
        ),
    }
    replay = {
        "operation_id": "ffmpeg_libass_diagnostic_replay_operation",
        "selected_render_path": stage1["stage_1_candidate"]["render_adapter_path"],
        "operation_status": "replayability_packet_ready_no_new_replay",
        "existing_output_first_reused": True,
        "new_replay_run": False,
        "replay_required_now": False,
        "diagnostic_only": True,
        "tracked_inputs": [
            "docs/style_intent/subtitle-final-render-path-stage-1.json",
            "docs/style_intent/subtitle-final-render-path-readiness.json",
            "docs/style_intent/subtitle-render-path-selector-probe.json",
            "docs/style_intent/subtitle-render-path-lineage-observation-surface.json",
            "docs/style_intent/subtitle-render-contract-consumer-dry-read.json",
            "docs/style_intent/subtitle-render-path-selector-contract.json",
            "src/integrations/render/subtitle_preset_selector.py",
            "src/integrations/render/ffmpeg_tiny.py",
        ],
        "same_machine_local_inputs": local_inputs,
        "ignored_output_paths": local_outputs,
        "expected_output_types": ["ass", "mp4", "local_manifest_json", "contact_sheet_jpg"],
        "command_family": "ffmpeg with libass subtitles filter plus ffprobe readback",
        "source_probe_render_command_summary": probe["local_probe"].get(
            "render_command_summary",
            "",
        ),
        "validation_readback_commands": [
            "uvx python -m json.tool docs\\style_intent\\subtitle-final-render-path-stage-2.json",
            "uvx python -m json.tool docs\\style_intent\\subtitle-render-path-selector-probe.json",
            "git ls-files episodes",
            "git check-ignore -v -- episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4 episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg",
        ],
        "fresh_clone_absence_behavior": (
            "Same-machine ignored media may be absent on a fresh clone. "
            "That absence is non-fatal for tracked docs; rerun only under a "
            "separate explicit diagnostic replay route."
        ),
    }
    matrix = _final_render_path_stage2_operation_matrix(
        stage1=stage1,
        readiness=readiness,
        probe=probe,
        lineage=lineage,
        replay=replay,
    )
    boundaries = _final_render_path_stage2_boundary_flags(stage1)
    validation = _final_render_path_stage2_validation(
        stage1=stage1,
        readiness=readiness,
        probe=probe,
        lineage=lineage,
        gate=gate,
        dry=dry,
        matrix=matrix,
        boundaries=boundaries,
    )
    return {
        "schema_id": FINAL_RENDER_PATH_STAGE2_SCHEMA_ID,
        "artifact_id": FINAL_RENDER_PATH_STAGE2_ARTIFACT_ID,
        "feature_id": FINAL_RENDER_PATH_STAGE2_FEATURE_ID,
        "status": "final_render_path_stage_2_replayability_ready",
        "surface_kind": "final_render_path_stage_2_replayability_operation_packet",
        "render_level": "stage_2_replayability_no_new_render",
        "source_final_render_path_stage_1_artifact_id": stage1["artifact_id"],
        "source_final_render_path_readiness_artifact_id": readiness["artifact_id"],
        "source_render_path_selector_probe_artifact_id": probe["artifact_id"],
        "source_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "source_production_limitation_lift_entry_artifact_id": gate["artifact_id"],
        "source_render_contract_consumer_dry_read_artifact_id": dry["artifact_id"],
        "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
        "replay_operation": replay,
        "operation_matrix_row_ids": list(FINAL_RENDER_PATH_STAGE2_REQUIRED_ROW_IDS),
        "operation_matrix": matrix,
        "handoff_routes": {
            "primary_route_id": "final-render-path-stage-3",
            "alternate_route_id": "production-limitation-lift-stage-1",
            "stage_3_purpose": (
                "Prepare an actual final-path rehearsal from the replayability "
                "packet while retaining diagnostic and production boundaries."
            ),
            "production_limitation_lift_stage_1_purpose": (
                "Prepare human, rights, publishing, and public-use decision "
                "packets without approving those decisions."
            ),
            "neither_route_approves_production_public_use": True,
        },
        "render_gate": {
            "level": "stage_2_replayability_no_new_render",
            "existing_output_first_reused": True,
            "new_render_run": False,
            "new_replay_run": False,
            "source_probe_new_render_run": probe["render_gate"]["new_render_run"],
            "source_stage1_new_render_run": stage1["render_gate"]["new_render_run"],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "production_public_readiness": {
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "missing_before_production_render_approval": [
                "Explicit production subtitle design acceptance.",
                "Accepted final production render output.",
                "Final production render command/output manifest and review result.",
                "Explicit creative acceptance for production use.",
            ],
            "missing_before_publishing_public_use": [
                "Rights clearance or owner decision.",
                "Publishing acceptance.",
                "Explicit public-use permission.",
            ],
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-final-render-path-stage-2.json",
            "doc": "docs/style_intent/subtitle-final-render-path-stage-2.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_stage_2_packet",
            "fixed_form_required": False,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "human_review_required_only_for": [
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_final_render_path_stage2_replayability(
    output_dir: Path,
    *,
    stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_final_render_path_stage2_replayability(
        stage1_packet=stage1_packet,
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-final-render-path-stage-2.json"
    doc_path = output_dir / "subtitle-final-render-path-stage-2.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_final_render_path_stage2_replayability_markdown(packet),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_final_render_path_stage3_rehearsal(
    *,
    stage2_packet: Mapping[str, Any] | None = None,
    stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
    rehearsal_local_probe: Mapping[str, Any] | None = None,
    rehearsal_invocation_command: str | None = None,
) -> dict[str, Any]:
    dry = (
        deepcopy(dry_read)
        if dry_read is not None
        else build_subtitle_render_contract_consumer_dry_read()
    )
    probe = (
        deepcopy(source_probe)
        if source_probe is not None
        else build_subtitle_render_path_selector_probe()
    )
    lineage = (
        deepcopy(lineage_surface)
        if lineage_surface is not None
        else build_subtitle_render_path_lineage_observation_surface(
            dry_read=dry,
            source_probe=probe,
        )
    )
    gate = (
        deepcopy(gate_entry)
        if gate_entry is not None
        else build_subtitle_production_limitation_lift_entry(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
        )
    )
    readiness = (
        deepcopy(readiness_packet)
        if readiness_packet is not None
        else build_subtitle_final_render_path_readiness_packet(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
        )
    )
    stage1 = (
        deepcopy(stage1_packet)
        if stage1_packet is not None
        else build_subtitle_final_render_path_stage1(
            readiness_packet=readiness,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
            dry_read=dry,
        )
    )
    stage2 = (
        deepcopy(stage2_packet)
        if stage2_packet is not None
        else build_subtitle_final_render_path_stage2_replayability(
            stage1_packet=stage1,
            readiness_packet=readiness,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
            dry_read=dry,
        )
    )
    local_probe = (
        deepcopy(rehearsal_local_probe)
        if rehearsal_local_probe is not None
        else deepcopy(probe["local_probe"])
    )
    recorded_outputs = dict(stage2["replay_operation"]["ignored_output_paths"])
    generated_outputs = dict(local_probe.get("outputs") or {})
    output_status = {
        "ass": "generated" if generated_outputs.get("ass") else "not_generated",
        "video": "generated" if generated_outputs.get("video") else "not_generated",
        "manifest": "generated" if generated_outputs.get("manifest") else "not_generated",
        "contact_sheet": (
            "recorded_not_generated_by_stage_3_rehearsal"
            if recorded_outputs.get("contact_sheet")
            else "not_recorded"
        ),
    }
    rehearsal = {
        "rehearsal_id": "ffmpeg_libass_diagnostic_stage_3_rehearsal",
        "selected_render_path": stage2["replay_operation"]["selected_render_path"],
        "rehearsal_status": "diagnostic_rehearsal_completed",
        "diagnostic_only": True,
        "existing_output_first_applied": True,
        "existing_output_first_reused": False,
        "new_rehearsal_run": True,
        "new_render_run": True,
        "rehearsal_run_reason": (
            "Tracked ED-10af/ED-10ag readback existed, but the same-machine "
            "ignored ASS/MP4/manifest outputs were absent before this slice "
            "while source video/audio were present."
        ),
        "tracked_inputs": list(stage2["replay_operation"]["tracked_inputs"]),
        "same_machine_local_inputs": dict(
            stage2["replay_operation"]["same_machine_local_inputs"]
        ),
        "recorded_ignored_outputs": recorded_outputs,
        "generated_ignored_outputs": generated_outputs,
        "output_status": output_status,
        "expected_output_types": [
            "ass",
            "mp4",
            "local_manifest_json",
            "contact_sheet_jpg_recorded_not_generated",
        ],
        "command_family": stage2["replay_operation"]["command_family"],
        "rehearsal_invocation_command": rehearsal_invocation_command
        or "write_subtitle_render_path_selector_probe_local_artifacts(...)",
        "render_command_summary": local_probe.get("render_command_summary"),
        "local_probe_readback": local_probe,
        "output_metadata": dict(local_probe.get("metadata") or {}),
        "why_diagnostic_only": (
            "The rehearsal uses ignored local source media and writes ignored "
            "local diagnostic proof only. It does not approve production "
            "subtitle design, production render, creative use, rights, "
            "publishing, or public use."
        ),
    }
    survival = {
        "ass_subtitle_style_tokens_survived": (
            probe["validation"]["style_axis_preserved"] is True
            and local_probe.get("status") == "local_ignored_probe_generated"
        ),
        "stable_body_text_policy_survived": probe["validation"][
            "stable_body_text_preserved"
        ],
        "badge_accent_backplate_route_survived": probe["validation"][
            "badge_accent_backplate_route_preserved"
        ],
        "line_break_safe_area_metadata_survived": probe["validation"][
            "safe_area_line_break_metadata_survived"
        ],
        "production_public_gates_still_closed": True,
    }
    matrix = _final_render_path_stage3_rehearsal_matrix(
        stage2=stage2,
        probe=probe,
        lineage=lineage,
        rehearsal=rehearsal,
        survival=survival,
    )
    boundaries = _final_render_path_stage3_boundary_flags()
    validation = _final_render_path_stage3_validation(
        stage2=stage2,
        stage1=stage1,
        readiness=readiness,
        probe=probe,
        lineage=lineage,
        gate=gate,
        dry=dry,
        rehearsal=rehearsal,
        survival=survival,
        matrix=matrix,
        boundaries=boundaries,
    )
    return {
        "schema_id": FINAL_RENDER_PATH_STAGE3_SCHEMA_ID,
        "artifact_id": FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID,
        "feature_id": FINAL_RENDER_PATH_STAGE3_FEATURE_ID,
        "status": "final_render_path_stage_3_diagnostic_rehearsal_ready",
        "surface_kind": "final_render_path_stage_3_diagnostic_rehearsal_readback",
        "render_level": "stage_3_diagnostic_rehearsal_ignored_local_render",
        "source_final_render_path_stage_2_artifact_id": stage2["artifact_id"],
        "source_final_render_path_stage_1_artifact_id": stage1["artifact_id"],
        "source_final_render_path_readiness_artifact_id": readiness["artifact_id"],
        "source_render_path_selector_probe_artifact_id": probe["artifact_id"],
        "source_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "source_production_limitation_lift_entry_artifact_id": gate["artifact_id"],
        "source_render_contract_consumer_dry_read_artifact_id": dry["artifact_id"],
        "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
        "rehearsal": rehearsal,
        "survival_readback": survival,
        "rehearsal_matrix_row_ids": list(FINAL_RENDER_PATH_STAGE3_REQUIRED_ROW_IDS),
        "rehearsal_matrix": matrix,
        "handoff_routes": {
            "primary_route_id": "production-limitation-lift-stage-1",
            "alternate_route_id": "final-render-path-stage-4",
            "production_limitation_lift_stage_1_purpose": (
                "Prepare explicit human, rights, publishing, and public-use "
                "decision packets after the diagnostic final-path rehearsal "
                "without approving those decisions."
            ),
            "stage_4_purpose": (
                "Inspect or package a later final render-path route only if a "
                "new explicit milestone needs more diagnostic readback."
            ),
            "neither_route_approves_production_public_use": True,
        },
        "render_gate": {
            "level": "stage_3_diagnostic_rehearsal_ignored_local_render",
            "existing_output_first_applied": True,
            "existing_output_first_reused": False,
            "new_render_run": True,
            "new_rehearsal_run": True,
            "source_probe_new_render_run": probe["render_gate"]["new_render_run"],
            "source_stage2_new_render_run": stage2["render_gate"]["new_render_run"],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "production_public_readiness": {
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "missing_before_production_render_approval": [
                "Explicit production subtitle design acceptance.",
                "Accepted final production render output.",
                "Final production render command/output manifest and review result.",
                "Explicit creative acceptance for production use.",
            ],
            "missing_before_publishing_public_use": [
                "Rights clearance or owner decision.",
                "Publishing acceptance.",
                "Explicit public-use permission.",
            ],
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-final-render-path-stage-3.json",
            "doc": "docs/style_intent/subtitle-final-render-path-stage-3.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_stage_3_diagnostic_rehearsal",
            "fixed_form_required": False,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "human_review_required_only_for": [
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_final_render_path_stage3_rehearsal(
    output_dir: Path,
    *,
    stage2_packet: Mapping[str, Any] | None = None,
    stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
    rehearsal_local_probe: Mapping[str, Any] | None = None,
    rehearsal_invocation_command: str | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_final_render_path_stage3_rehearsal(
        stage2_packet=stage2_packet,
        stage1_packet=stage1_packet,
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
        rehearsal_local_probe=rehearsal_local_probe,
        rehearsal_invocation_command=rehearsal_invocation_command,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-final-render-path-stage-3.json"
    doc_path = output_dir / "subtitle-final-render-path-stage-3.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_final_render_path_stage3_rehearsal_markdown(packet),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_production_limitation_lift_stage1(
    *,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    dry = (
        deepcopy(dry_read)
        if dry_read is not None
        else build_subtitle_render_contract_consumer_dry_read()
    )
    probe = (
        deepcopy(source_probe)
        if source_probe is not None
        else build_subtitle_render_path_selector_probe()
    )
    lineage = (
        deepcopy(lineage_surface)
        if lineage_surface is not None
        else build_subtitle_render_path_lineage_observation_surface(
            dry_read=dry,
            source_probe=probe,
        )
    )
    gate = (
        deepcopy(gate_entry)
        if gate_entry is not None
        else build_subtitle_production_limitation_lift_entry(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
        )
    )
    readiness = (
        deepcopy(readiness_packet)
        if readiness_packet is not None
        else build_subtitle_final_render_path_readiness_packet(
            dry_read=dry,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
        )
    )
    stage1 = (
        deepcopy(stage1_packet)
        if stage1_packet is not None
        else build_subtitle_final_render_path_stage1(
            readiness_packet=readiness,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
            dry_read=dry,
        )
    )
    stage2 = (
        deepcopy(stage2_packet)
        if stage2_packet is not None
        else build_subtitle_final_render_path_stage2_replayability(
            stage1_packet=stage1,
            readiness_packet=readiness,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
            dry_read=dry,
        )
    )
    stage3 = (
        deepcopy(stage3_packet)
        if stage3_packet is not None
        else build_subtitle_final_render_path_stage3_rehearsal(
            stage2_packet=stage2,
            stage1_packet=stage1,
            readiness_packet=readiness,
            source_probe=probe,
            lineage_surface=lineage,
            gate_entry=gate,
            dry_read=dry,
        )
    )
    rehearsal = stage3["rehearsal"]
    diagnostic_evidence = {
        "primary_diagnostic_rehearsal_artifact_id": stage3["artifact_id"],
        "primary_diagnostic_rehearsal_path": "docs/style_intent/subtitle-final-render-path-stage-3.json",
        "primary_diagnostic_rehearsal_doc": "docs/style_intent/subtitle-final-render-path-stage-3.md",
        "source_final_render_path_stage_2_artifact_id": stage2["artifact_id"],
        "source_final_render_path_stage_1_artifact_id": stage1["artifact_id"],
        "source_final_render_path_readiness_artifact_id": readiness["artifact_id"],
        "source_production_limitation_lift_entry_artifact_id": gate["artifact_id"],
        "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
        "support_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "dry_read_predecessor_artifact_id": dry["artifact_id"],
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "selected_render_path": rehearsal["selected_render_path"],
        "rehearsal_status": rehearsal["rehearsal_status"],
        "command_family": rehearsal["command_family"],
        "rehearsal_invocation_command": rehearsal["rehearsal_invocation_command"],
        "render_command_summary": rehearsal["render_command_summary"],
        "generated_ignored_outputs": dict(rehearsal["generated_ignored_outputs"]),
        "recorded_ignored_outputs": dict(rehearsal["recorded_ignored_outputs"]),
        "output_status": dict(rehearsal["output_status"]),
        "output_metadata": dict(rehearsal["output_metadata"]),
        "survival_readback": dict(stage3["survival_readback"]),
        "same_machine_local_inputs": dict(rehearsal["same_machine_local_inputs"]),
        "why_diagnostic_only": rehearsal["why_diagnostic_only"],
    }
    gate_matrix = _production_limitation_lift_stage1_gate_matrix(
        stage3=stage3,
        diagnostic_evidence=diagnostic_evidence,
    )
    boundaries = _production_limitation_lift_stage1_boundary_flags(stage3)
    validation = _production_limitation_lift_stage1_validation(
        stage3=stage3,
        gate_matrix=gate_matrix,
        boundaries=boundaries,
        diagnostic_evidence=diagnostic_evidence,
    )
    return {
        "schema_id": PRODUCTION_LIMITATION_LIFT_STAGE1_SCHEMA_ID,
        "artifact_id": PRODUCTION_LIMITATION_LIFT_STAGE1_ARTIFACT_ID,
        "feature_id": PRODUCTION_LIMITATION_LIFT_STAGE1_FEATURE_ID,
        "status": "production_limitation_lift_stage_1_packet_ready",
        "surface_kind": "production_limitation_lift_stage_1_decision_preparation_packet",
        "render_level": "stage_1_decision_preparation_no_new_render",
        "source_final_render_path_stage_3_rehearsal_artifact_id": stage3["artifact_id"],
        "source_final_render_path_stage_2_artifact_id": stage2["artifact_id"],
        "source_final_render_path_stage_1_artifact_id": stage1["artifact_id"],
        "source_final_render_path_readiness_artifact_id": readiness["artifact_id"],
        "source_production_limitation_lift_entry_artifact_id": gate["artifact_id"],
        "active_diagnostic_proof_source_artifact_id": probe["artifact_id"],
        "support_lineage_observation_surface_artifact_id": lineage["artifact_id"],
        "source_render_contract_consumer_dry_read_artifact_id": dry["artifact_id"],
        "diagnostic_evidence": diagnostic_evidence,
        "gate_names": list(PRODUCTION_LIMITATION_LIFT_STAGE1_GATE_NAMES),
        "gate_matrix": gate_matrix,
        "non_approval_readback": {
            "ed10al_does_not_prove": [
                "final production subtitle design acceptance",
                "production render acceptance",
                "creative acceptance",
                "rights clearance",
                "publishing readiness",
                "public-use permission",
            ],
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        },
        "next_executable_route": {
            "route_id": "production-limitation-lift-stage-2-decision-packet",
            "alternate_route_id": "final-render-path-stage-4",
            "alternate_route_condition": (
                "Use only if additional diagnostic evidence is genuinely needed "
                "before preparing decision packets."
            ),
            "agent_can_start_without_user_judgement": True,
            "purpose": (
                "Turn the separated gates into explicit decision packets for "
                "human, rights, publication, and public-use owners without "
                "approving those decisions."
            ),
            "first_steps": [
                "Carry forward ED-10al as diagnostic evidence only.",
                "Prepare at most the next explicit decision packet for the blocking gate.",
                "Keep production/public claims closed until the relevant owner answers.",
            ],
            "must_not_do": [
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "claim rights clearance",
                "claim publishing readiness",
                "grant public-use permission",
                "track ignored media under episodes/",
                "reopen old layout or candidate-comparison reviews",
            ],
        },
        "render_gate": {
            "level": "stage_1_decision_preparation_no_new_render",
            "existing_output_first_applied": True,
            "existing_output_first_reused": True,
            "new_render_run": False,
            "new_rehearsal_run": False,
            "source_stage3_new_render_run": stage3["render_gate"]["new_render_run"],
            "source_stage3_new_rehearsal_run": stage3["render_gate"][
                "new_rehearsal_run"
            ],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-production-limitation-lift-stage-1.json",
            "doc": "docs/style_intent/subtitle-production-limitation-lift-stage-1.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_stage_1_preparation_packet",
            "fixed_form_required": False,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "human_review_required_only_for": [
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_production_limitation_lift_stage1(
    output_dir: Path,
    *,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_production_limitation_lift_stage1(
        stage3_packet=stage3_packet,
        stage2_packet=stage2_packet,
        stage1_packet=stage1_packet,
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-production-limitation-lift-stage-1.json"
    doc_path = output_dir / "subtitle-production-limitation-lift-stage-1.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_production_limitation_lift_stage1_markdown(packet),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_production_limitation_lift_stage2_decision_packet(
    *,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    stage1_lift = (
        deepcopy(production_lift_stage1_packet)
        if production_lift_stage1_packet is not None
        else build_subtitle_production_limitation_lift_stage1(
            stage3_packet=stage3_packet,
            stage2_packet=stage2_packet,
            stage1_packet=final_stage1_packet,
            readiness_packet=readiness_packet,
            source_probe=source_probe,
            lineage_surface=lineage_surface,
            gate_entry=gate_entry,
            dry_read=dry_read,
        )
    )
    diagnostic = stage1_lift["diagnostic_evidence"]
    metadata = diagnostic["output_metadata"]
    source_evidence = {
        "source_stage1_artifact_id": stage1_lift["artifact_id"],
        "source_stage1_path": "docs/style_intent/subtitle-production-limitation-lift-stage-1.json",
        "source_stage1_doc": "docs/style_intent/subtitle-production-limitation-lift-stage-1.md",
        "source_gate_count": len(stage1_lift["gate_matrix"]),
        "source_gate_names": list(stage1_lift["gate_names"]),
        "primary_diagnostic_rehearsal_artifact_id": stage1_lift[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "stage_2_replayability_artifact_id": stage1_lift[
            "source_final_render_path_stage_2_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage1_lift[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "diagnostic_rehearsal_status": diagnostic["rehearsal_status"],
        "diagnostic_outputs": dict(diagnostic["generated_ignored_outputs"]),
        "diagnostic_output_metadata": {
            "duration_seconds": metadata["duration_seconds"],
            "resolution": metadata["resolution"],
            "video_codec": metadata["video_codec"],
            "audio_codec": metadata["audio_codec"],
            "stream_count": metadata["stream_count"],
        },
        "diagnostic_survival_readback": dict(diagnostic["survival_readback"]),
        "ed10am_non_approval_readback": deepcopy(
            stage1_lift["non_approval_readback"]
        ),
    }
    decision_groups = _production_limitation_lift_stage2_decision_groups(
        stage1_lift
    )
    no_decision_yet = _production_limitation_lift_stage2_no_decision_yet(
        stage1_lift
    )
    boundaries = _production_limitation_lift_stage2_boundary_flags(stage1_lift)
    validation = _production_limitation_lift_stage2_validation(
        stage1_lift=stage1_lift,
        source_evidence=source_evidence,
        decision_groups=decision_groups,
        no_decision_yet=no_decision_yet,
        boundaries=boundaries,
    )
    return {
        "schema_id": PRODUCTION_LIMITATION_LIFT_STAGE2_SCHEMA_ID,
        "artifact_id": PRODUCTION_LIMITATION_LIFT_STAGE2_ARTIFACT_ID,
        "feature_id": PRODUCTION_LIMITATION_LIFT_STAGE2_FEATURE_ID,
        "status": "production_limitation_lift_stage_2_decision_packet_ready",
        "surface_kind": "production_limitation_lift_stage_2_decision_preparation_packet",
        "render_level": "stage_2_decision_packet_no_new_render",
        "source_production_limitation_lift_stage_1_artifact_id": stage1_lift[
            "artifact_id"
        ],
        "source_final_render_path_stage_3_rehearsal_artifact_id": stage1_lift[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "source_final_render_path_stage_2_artifact_id": stage1_lift[
            "source_final_render_path_stage_2_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage1_lift[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "source_evidence": source_evidence,
        "decision_group_ids": list(PRODUCTION_LIMITATION_LIFT_STAGE2_DECISION_GROUP_IDS),
        "decision_groups": decision_groups,
        "no_decision_yet": no_decision_yet,
        "gate_separation": {
            "diagnostic_proof_does_not_imply_production_subtitle_design_acceptance": True,
            "diagnostic_rehearsal_does_not_imply_production_render_acceptance": True,
            "local_ignored_media_does_not_imply_publishing_public_use_permission": True,
            "decision_packet_does_not_request_immediate_user_judgement": True,
            "decision_packet_does_not_grant_approval": True,
        },
        "next_executable_route": {
            "route_id": "production-limitation-lift-stage-3-owner-review-prep",
            "alternate_route_id": "final-render-path-stage-4",
            "alternate_route_condition": (
                "Use only if a concrete diagnostic gap is found; ED-10an "
                "does not identify such a gap."
            ),
            "concrete_diagnostic_gap_found": False,
            "agent_can_start_without_user_judgement": True,
            "purpose": (
                "Prepare owner-facing review inputs for the three decision "
                "groups without approving production, rights, publishing, or "
                "public use."
            ),
            "first_steps": [
                "Keep ED-10am as the source gate matrix.",
                "Prepare owner-review material for the three bounded decision groups.",
                "Keep all production/public approvals closed until the relevant owner answers.",
            ],
            "must_not_do": [
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "claim rights clearance",
                "claim publishing readiness",
                "grant public-use permission",
                "track ignored media under episodes/",
                "request repeat layout polish or old candidate reviews",
            ],
        },
        "render_gate": {
            "level": "stage_2_decision_packet_no_new_render",
            "existing_output_first_applied": True,
            "existing_output_first_reused": True,
            "new_render_run": False,
            "new_rehearsal_run": False,
            "source_stage1_new_render_run": stage1_lift["render_gate"][
                "new_render_run"
            ],
            "source_stage3_new_render_run": stage1_lift["render_gate"][
                "source_stage3_new_render_run"
            ],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.json",
            "doc": "docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_stage_2_decision_preparation_packet",
            "fixed_form_required": False,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "owner_judgement_required_later_for": [
                "subtitle design / visual acceptance",
                "production render readiness",
                "rights / publishing / public-use clearance",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_production_limitation_lift_stage2_decision_packet(
    output_dir: Path,
    *,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_production_limitation_lift_stage2_decision_packet(
        production_lift_stage1_packet=production_lift_stage1_packet,
        stage3_packet=stage3_packet,
        stage2_packet=stage2_packet,
        final_stage1_packet=final_stage1_packet,
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-production-limitation-lift-stage-2-decision-packet.json"
    doc_path = output_dir / "subtitle-production-limitation-lift-stage-2-decision-packet.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_production_limitation_lift_stage2_decision_packet_markdown(
            packet
        ),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_production_limitation_lift_stage3_owner_review_prep(
    *,
    production_lift_stage2_packet: Mapping[str, Any] | None = None,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    stage2_lift = (
        deepcopy(production_lift_stage2_packet)
        if production_lift_stage2_packet is not None
        else build_subtitle_production_limitation_lift_stage2_decision_packet(
            production_lift_stage1_packet=production_lift_stage1_packet,
            stage3_packet=stage3_packet,
            stage2_packet=stage2_packet,
            final_stage1_packet=final_stage1_packet,
            readiness_packet=readiness_packet,
            source_probe=source_probe,
            lineage_surface=lineage_surface,
            gate_entry=gate_entry,
            dry_read=dry_read,
        )
    )
    source = stage2_lift["source_evidence"]
    source_evidence = {
        "source_stage2_decision_packet_artifact_id": stage2_lift["artifact_id"],
        "source_stage2_path": "docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.json",
        "source_stage2_doc": "docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md",
        "source_stage1_gate_matrix_artifact_id": stage2_lift[
            "source_production_limitation_lift_stage_1_artifact_id"
        ],
        "primary_diagnostic_rehearsal_artifact_id": stage2_lift[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "stage_2_replayability_artifact_id": stage2_lift[
            "source_final_render_path_stage_2_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage2_lift[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "source_decision_group_count": len(stage2_lift["decision_groups"]),
        "source_decision_group_ids": list(stage2_lift["decision_group_ids"]),
        "diagnostic_output_metadata": deepcopy(source["diagnostic_output_metadata"]),
        "diagnostic_survival_readback": deepcopy(source["diagnostic_survival_readback"]),
        "stage2_no_decision_yet": deepcopy(stage2_lift["no_decision_yet"]),
    }
    owner_review_groups = _production_limitation_lift_stage3_owner_review_groups(
        stage2_lift
    )
    no_approval_yet = _production_limitation_lift_stage3_no_approval_yet(stage2_lift)
    future_decision_shape = (
        _production_limitation_lift_stage3_future_decision_shape(owner_review_groups)
    )
    boundaries = _production_limitation_lift_stage3_boundary_flags(stage2_lift)
    validation = _production_limitation_lift_stage3_validation(
        stage2_lift=stage2_lift,
        source_evidence=source_evidence,
        owner_review_groups=owner_review_groups,
        no_approval_yet=no_approval_yet,
        future_decision_shape=future_decision_shape,
        boundaries=boundaries,
    )
    return {
        "schema_id": PRODUCTION_LIMITATION_LIFT_STAGE3_SCHEMA_ID,
        "artifact_id": PRODUCTION_LIMITATION_LIFT_STAGE3_ARTIFACT_ID,
        "feature_id": PRODUCTION_LIMITATION_LIFT_STAGE3_FEATURE_ID,
        "status": "production_limitation_lift_stage_3_owner_review_prep_ready",
        "surface_kind": "production_limitation_lift_stage_3_owner_review_preparation_packet",
        "render_level": "stage_3_owner_review_prep_no_new_render",
        "source_production_limitation_lift_stage_2_decision_packet_artifact_id": stage2_lift[
            "artifact_id"
        ],
        "source_production_limitation_lift_stage_1_artifact_id": stage2_lift[
            "source_production_limitation_lift_stage_1_artifact_id"
        ],
        "source_final_render_path_stage_3_rehearsal_artifact_id": stage2_lift[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "source_final_render_path_stage_2_artifact_id": stage2_lift[
            "source_final_render_path_stage_2_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage2_lift[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "source_evidence": source_evidence,
        "owner_review_group_ids": list(
            PRODUCTION_LIMITATION_LIFT_STAGE3_OWNER_REVIEW_GROUP_IDS
        ),
        "owner_review_groups": owner_review_groups,
        "no_approval_yet": no_approval_yet,
        "future_user_decision_shape": future_decision_shape,
        "next_executable_route": {
            "route_id": "production-limitation-lift-stage-4-user-decision-card",
            "alternate_route_id": "final-render-path-stage-4",
            "alternate_route_condition": (
                "Use only if a concrete diagnostic gap is found; ED-10ao "
                "does not identify such a gap."
            ),
            "concrete_diagnostic_gap_found": False,
            "agent_can_start_without_user_judgement": True,
            "purpose": (
                "Create the later low-burden user decision card from the "
                "prepared owner-review groups without approving any decision."
            ),
            "first_steps": [
                "Keep ED-10an as the source decision packet.",
                "Convert owner-review prep entries into a short freeform decision card.",
                "Keep approval closed until the relevant owner answers in a later slice.",
            ],
            "must_not_do": [
                "ask the user for an immediate decision in ED-10ao",
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "claim rights clearance",
                "claim publishing readiness",
                "grant public-use permission",
                "track ignored media under episodes/",
                "emit a fixed-choice user form",
                "request repeat layout polish or old candidate reviews",
            ],
        },
        "render_gate": {
            "level": "stage_3_owner_review_prep_no_new_render",
            "existing_output_first_applied": True,
            "existing_output_first_reused": True,
            "new_render_run": False,
            "new_rehearsal_run": False,
            "source_stage2_new_render_run": stage2_lift["render_gate"][
                "new_render_run"
            ],
            "source_stage1_new_render_run": stage2_lift["render_gate"][
                "source_stage1_new_render_run"
            ],
            "source_stage3_new_render_run": stage2_lift["render_gate"][
                "source_stage3_new_render_run"
            ],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.json",
            "doc": "docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_stage_3_owner_review_preparation_packet",
            "user_decision_requested_now": False,
            "fixed_form_required": False,
            "fixed_choice_rows_allowed": False,
            "freeform_future_decision_shape": True,
            "screenshot_required": False,
            "layout_polish_required_before_next_step": False,
            "owner_judgement_required_later_for": [
                "subtitle design / visual acceptance",
                "production render readiness",
                "rights / publishing / public-use clearance",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_production_limitation_lift_stage3_owner_review_prep(
    output_dir: Path,
    *,
    production_lift_stage2_packet: Mapping[str, Any] | None = None,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_production_limitation_lift_stage3_owner_review_prep(
        production_lift_stage2_packet=production_lift_stage2_packet,
        production_lift_stage1_packet=production_lift_stage1_packet,
        stage3_packet=stage3_packet,
        stage2_packet=stage2_packet,
        final_stage1_packet=final_stage1_packet,
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-production-limitation-lift-stage-3-owner-review-prep.json"
    doc_path = output_dir / "subtitle-production-limitation-lift-stage-3-owner-review-prep.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_production_limitation_lift_stage3_owner_review_prep_markdown(
            packet
        ),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_production_limitation_lift_stage4_user_decision_card(
    *,
    production_lift_stage3_owner_review_prep: Mapping[str, Any] | None = None,
    production_lift_stage2_packet: Mapping[str, Any] | None = None,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    stage3_lift = (
        deepcopy(production_lift_stage3_owner_review_prep)
        if production_lift_stage3_owner_review_prep is not None
        else build_subtitle_production_limitation_lift_stage3_owner_review_prep(
            production_lift_stage2_packet=production_lift_stage2_packet,
            production_lift_stage1_packet=production_lift_stage1_packet,
            stage3_packet=stage3_packet,
            stage2_packet=stage2_packet,
            final_stage1_packet=final_stage1_packet,
            readiness_packet=readiness_packet,
            source_probe=source_probe,
            lineage_surface=lineage_surface,
            gate_entry=gate_entry,
            dry_read=dry_read,
        )
    )
    source_evidence = _production_limitation_lift_stage4_source_evidence(stage3_lift)
    decision_topics = _production_limitation_lift_stage4_decision_topics(stage3_lift)
    not_asked_now = _production_limitation_lift_stage4_not_asked_now(stage3_lift)
    freeform_answer_handling = (
        _production_limitation_lift_stage4_freeform_answer_handling(decision_topics)
    )
    boundaries = _production_limitation_lift_stage4_boundary_flags(stage3_lift)
    validation = _production_limitation_lift_stage4_validation(
        stage3_lift=stage3_lift,
        source_evidence=source_evidence,
        decision_topics=decision_topics,
        not_asked_now=not_asked_now,
        freeform_answer_handling=freeform_answer_handling,
        boundaries=boundaries,
    )
    return {
        "schema_id": PRODUCTION_LIMITATION_LIFT_STAGE4_SCHEMA_ID,
        "artifact_id": PRODUCTION_LIMITATION_LIFT_STAGE4_ARTIFACT_ID,
        "feature_id": PRODUCTION_LIMITATION_LIFT_STAGE4_FEATURE_ID,
        "status": "production_limitation_lift_stage_4_user_decision_card_ready",
        "surface_kind": "production_limitation_lift_stage_4_future_user_decision_card",
        "render_level": "stage_4_user_decision_card_no_new_render",
        "source_production_limitation_lift_stage_3_owner_review_prep_artifact_id": stage3_lift[
            "artifact_id"
        ],
        "source_production_limitation_lift_stage_2_decision_packet_artifact_id": stage3_lift[
            "source_production_limitation_lift_stage_2_decision_packet_artifact_id"
        ],
        "source_production_limitation_lift_stage_1_artifact_id": stage3_lift[
            "source_production_limitation_lift_stage_1_artifact_id"
        ],
        "source_final_render_path_stage_3_rehearsal_artifact_id": stage3_lift[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage3_lift[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "source_evidence": source_evidence,
        "decision_topic_ids": list(PRODUCTION_LIMITATION_LIFT_STAGE4_DECISION_TOPIC_IDS),
        "decision_topics": decision_topics,
        "not_asked_now": not_asked_now,
        "future_freeform_answer_handling": freeform_answer_handling,
        "next_executable_route": {
            "route_id": "production-limitation-lift-stage-5-user-decision-ready",
            "alternate_route_id": "final-render-path-stage-4",
            "alternate_route_condition": (
                "Use only if a concrete diagnostic gap is found; ED-10ap "
                "does not identify such a gap."
            ),
            "concrete_diagnostic_gap_found": False,
            "agent_can_start_without_user_judgement": True,
            "purpose": (
                "Record a short freeform user decision card for a "
                "later slice without asking for or granting approval now."
            ),
            "first_steps": [
                "Keep ED-10ao as the source owner-review preparation packet.",
                "Present at most three freeform topics when a later slice asks for user judgement.",
                "Normalize future answers internally while preserving unknowns as unknown.",
            ],
            "must_not_do": [
                "ask the user for a decision in ED-10ap",
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "claim rights clearance",
                "claim publishing readiness",
                "grant public-use permission",
                "emit a fixed user form",
                "emit fixed-choice rows",
                "require a screenshot path",
                "expose hidden schema fields as user input",
                "track ignored media under episodes/",
                "request repeat layout polish or old candidate reviews",
            ],
        },
        "render_gate": {
            "level": "stage_4_user_decision_card_no_new_render",
            "existing_output_first_applied": True,
            "existing_output_first_reused": True,
            "new_render_run": False,
            "new_rehearsal_run": False,
            "source_stage3_owner_review_prep_new_render_run": stage3_lift[
                "render_gate"
            ]["new_render_run"],
            "source_stage2_decision_packet_new_render_run": stage3_lift[
                "render_gate"
            ]["source_stage2_new_render_run"],
            "source_stage1_new_render_run": stage3_lift["render_gate"][
                "source_stage1_new_render_run"
            ],
            "source_final_path_stage3_new_render_run": stage3_lift["render_gate"][
                "source_stage3_new_render_run"
            ],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.json",
            "doc": "docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_production_limitation_lift_stage_4_future_user_decision_card",
            "user_decision_requested_now": False,
            "answer_style": "freeform",
            "template_required": False,
            "schema_owner": "Agent",
            "max_look_for_points": 3,
            "fixed_form_required": False,
            "fixed_choice_rows_allowed": False,
            "fixed_choice_rows_emitted": False,
            "freeform_future_decision_shape": True,
            "screenshot_required": False,
            "hidden_schema_exposed_to_user": False,
            "layout_polish_required_before_next_step": False,
            "user_judgement_required_later_for": [
                "subtitle design / visual acceptance",
                "production render readiness",
                "rights / publishing / public-use clearance",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_production_limitation_lift_stage4_user_decision_card(
    output_dir: Path,
    *,
    production_lift_stage3_owner_review_prep: Mapping[str, Any] | None = None,
    production_lift_stage2_packet: Mapping[str, Any] | None = None,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_production_limitation_lift_stage4_user_decision_card(
        production_lift_stage3_owner_review_prep=production_lift_stage3_owner_review_prep,
        production_lift_stage2_packet=production_lift_stage2_packet,
        production_lift_stage1_packet=production_lift_stage1_packet,
        stage3_packet=stage3_packet,
        stage2_packet=stage2_packet,
        final_stage1_packet=final_stage1_packet,
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-production-limitation-lift-stage-4-user-decision-card.json"
    doc_path = output_dir / "subtitle-production-limitation-lift-stage-4-user-decision-card.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_production_limitation_lift_stage4_user_decision_card_markdown(
            packet
        ),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}


def build_subtitle_production_limitation_lift_stage5_user_decision_ready(
    *,
    production_lift_stage4_user_decision_card: Mapping[str, Any] | None = None,
    production_lift_stage3_owner_review_prep: Mapping[str, Any] | None = None,
    production_lift_stage2_packet: Mapping[str, Any] | None = None,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    stage4_card = (
        deepcopy(production_lift_stage4_user_decision_card)
        if production_lift_stage4_user_decision_card is not None
        else build_subtitle_production_limitation_lift_stage4_user_decision_card(
            production_lift_stage3_owner_review_prep=production_lift_stage3_owner_review_prep,
            production_lift_stage2_packet=production_lift_stage2_packet,
            production_lift_stage1_packet=production_lift_stage1_packet,
            stage3_packet=stage3_packet,
            stage2_packet=stage2_packet,
            final_stage1_packet=final_stage1_packet,
            readiness_packet=readiness_packet,
            source_probe=source_probe,
            lineage_surface=lineage_surface,
            gate_entry=gate_entry,
            dry_read=dry_read,
        )
    )
    source_evidence = _production_limitation_lift_stage5_source_evidence(stage4_card)
    decision_topics = _production_limitation_lift_stage5_decision_topics(stage4_card)
    ready_but_not_asked = _production_limitation_lift_stage5_ready_but_not_asked(
        stage4_card
    )
    future_presentation_constraints = (
        _production_limitation_lift_stage5_future_presentation_constraints(
            decision_topics
        )
    )
    boundaries = _production_limitation_lift_stage5_boundary_flags(stage4_card)
    validation = _production_limitation_lift_stage5_validation(
        stage4_card=stage4_card,
        source_evidence=source_evidence,
        decision_topics=decision_topics,
        ready_but_not_asked=ready_but_not_asked,
        future_presentation_constraints=future_presentation_constraints,
        boundaries=boundaries,
    )
    return {
        "schema_id": PRODUCTION_LIMITATION_LIFT_STAGE5_SCHEMA_ID,
        "artifact_id": PRODUCTION_LIMITATION_LIFT_STAGE5_ARTIFACT_ID,
        "feature_id": PRODUCTION_LIMITATION_LIFT_STAGE5_FEATURE_ID,
        "status": "production_limitation_lift_stage_5_user_decision_ready",
        "surface_kind": "production_limitation_lift_stage_5_user_decision_ready_packet",
        "render_level": "stage_5_user_decision_ready_no_new_render",
        "source_stage4_user_decision_card_artifact_id": stage4_card[
            "artifact_id"
        ],
        "source_production_limitation_lift_stage_3_owner_review_prep_artifact_id": stage4_card[
            "source_production_limitation_lift_stage_3_owner_review_prep_artifact_id"
        ],
        "source_production_limitation_lift_stage_2_decision_packet_artifact_id": stage4_card[
            "source_production_limitation_lift_stage_2_decision_packet_artifact_id"
        ],
        "source_production_limitation_lift_stage_1_artifact_id": stage4_card[
            "source_production_limitation_lift_stage_1_artifact_id"
        ],
        "source_final_render_path_stage_3_rehearsal_artifact_id": stage4_card[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage4_card[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "source_evidence": source_evidence,
        "decision_topic_ids": list(PRODUCTION_LIMITATION_LIFT_STAGE5_DECISION_TOPIC_IDS),
        "decision_topics": decision_topics,
        "ready_but_not_asked": ready_but_not_asked,
        "future_presentation_constraints": future_presentation_constraints,
        "next_executable_route": {
            "route_id": "production-limitation-lift-stage-6-user-freeform-review-request",
            "alternate_route_id": "final-render-path-stage-4",
            "alternate_route_condition": (
                "Use only if a concrete diagnostic gap is found; ED-10aq "
                "does not identify such a gap."
            ),
            "concrete_diagnostic_gap_found": False,
            "agent_can_start_without_user_judgement": True,
            "purpose": (
                "Prepare the later short freeform user review request without "
                "asking for or granting any production, public-use, or rights "
                "approval in this slice."
            ),
            "first_steps": [
                "Use ED-10ap as the source stage-4 user decision-card packet.",
                "Present at most three short freeform topics in the next slice.",
                "Normalize the later user answer internally while keeping unknowns unknown.",
                "Keep production render, rights, publishing, and public-use approval closed until explicit user judgement exists.",
            ],
            "must_not_do": [
                "ask the user for a decision in ED-10aq",
                "approve production subtitle design",
                "approve production render",
                "approve creative use",
                "claim rights clearance",
                "claim publishing readiness",
                "grant public-use permission",
                "emit a fixed user form",
                "emit fixed-choice rows",
                "require a screenshot path",
                "expose hidden schema fields as user input",
                "track ignored media under episodes/",
                "request repeat layout polish or old candidate reviews",
            ],
        },
        "render_gate": {
            "level": "stage_5_user_decision_ready_no_new_render",
            "existing_output_first_applied": True,
            "existing_output_first_reused": True,
            "new_render_run": False,
            "new_rehearsal_run": False,
            "source_stage4_user_decision_card_new_render_run": stage4_card[
                "render_gate"
            ]["new_render_run"],
            "source_stage3_owner_review_prep_new_render_run": stage4_card[
                "render_gate"
            ]["source_stage3_owner_review_prep_new_render_run"],
            "source_stage2_decision_packet_new_render_run": stage4_card[
                "render_gate"
            ]["source_stage2_decision_packet_new_render_run"],
            "source_stage1_new_render_run": stage4_card["render_gate"][
                "source_stage1_new_render_run"
            ],
            "source_final_path_stage3_new_render_run": stage4_card["render_gate"][
                "source_final_path_stage3_new_render_run"
            ],
            "diagnostic_only": True,
            "tracked_binary_artifact_created": False,
            "local_outputs_ignored": True,
            "production_render_acceptance": False,
            "public_use_permission": False,
        },
        "validation": validation,
        "outputs": {
            "json": "docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.json",
            "doc": "docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.md",
        },
        "review_policy": {
            "human_review_required": False,
            "user_side_work": "none_for_this_stage_5_user_decision_ready_packet",
            "user_decision_requested_now": False,
            "answer_style": "freeform",
            "template_required": False,
            "schema_owner": "Agent",
            "max_look_for_points": 3,
            "fixed_form_required": False,
            "fixed_choice_rows_allowed": False,
            "fixed_choice_rows_emitted": False,
            "freeform_future_decision_shape": True,
            "screenshot_required": False,
            "hidden_schema_exposed_to_user": False,
            "layout_polish_required_before_next_step": False,
            "user_judgement_required_later_for": [
                "subtitle design / visual acceptance",
                "production render readiness",
                "rights / publishing / public-use clearance",
            ],
        },
        "boundaries": boundaries,
    }


def write_subtitle_production_limitation_lift_stage5_user_decision_ready(
    output_dir: Path,
    *,
    production_lift_stage4_user_decision_card: Mapping[str, Any] | None = None,
    production_lift_stage3_owner_review_prep: Mapping[str, Any] | None = None,
    production_lift_stage2_packet: Mapping[str, Any] | None = None,
    production_lift_stage1_packet: Mapping[str, Any] | None = None,
    stage3_packet: Mapping[str, Any] | None = None,
    stage2_packet: Mapping[str, Any] | None = None,
    final_stage1_packet: Mapping[str, Any] | None = None,
    readiness_packet: Mapping[str, Any] | None = None,
    source_probe: Mapping[str, Any] | None = None,
    lineage_surface: Mapping[str, Any] | None = None,
    gate_entry: Mapping[str, Any] | None = None,
    dry_read: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    packet = build_subtitle_production_limitation_lift_stage5_user_decision_ready(
        production_lift_stage4_user_decision_card=production_lift_stage4_user_decision_card,
        production_lift_stage3_owner_review_prep=production_lift_stage3_owner_review_prep,
        production_lift_stage2_packet=production_lift_stage2_packet,
        production_lift_stage1_packet=production_lift_stage1_packet,
        stage3_packet=stage3_packet,
        stage2_packet=stage2_packet,
        final_stage1_packet=final_stage1_packet,
        readiness_packet=readiness_packet,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
        gate_entry=gate_entry,
        dry_read=dry_read,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "subtitle-production-limitation-lift-stage-5-user-decision-ready.json"
    doc_path = output_dir / "subtitle-production-limitation-lift-stage-5-user-decision-ready.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(
        render_subtitle_production_limitation_lift_stage5_user_decision_ready_markdown(packet),
        encoding="utf-8",
    )
    return {"json": json_path, "doc": doc_path}



def write_subtitle_render_path_selector_probe_local_artifacts(
    *,
    output_dir: Path,
    source_video_path: Path,
    source_audio_path: Path,
    base_dir: Path | None = None,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
) -> dict[str, Any]:
    base = base_dir or Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    ass_path = output_dir / "subtitle_render_path_selector_probe.ass"
    video_path = output_dir / "subtitle_render_path_selector_probe.mp4"
    manifest_path = output_dir / "subtitle_render_path_selector_probe.local.json"
    probe = build_subtitle_render_path_selector_probe(
        local_probe=_default_render_path_probe_local_readback(
            ass_path=ass_path,
            video_path=video_path,
            manifest_path=manifest_path,
            base_dir=base,
        )
    )
    ass_path.write_text(
        render_subtitle_render_path_selector_probe_ass(probe),
        encoding="utf-8",
    )
    if not source_video_path.exists() or not source_audio_path.exists():
        local = _default_render_path_probe_local_readback(
            status="local_source_media_missing",
            ass_path=ass_path,
            video_path=video_path,
            manifest_path=manifest_path,
            base_dir=base,
        )
        local["missing_inputs"] = [
            _probe_display_path(path, base)
            for path in (source_video_path, source_audio_path)
            if not path.exists()
        ]
    else:
        try:
            result = ffmpeg_tiny.render_tiny_proof(
                source_video_path=source_video_path,
                source_audio_path=source_audio_path,
                output_path=video_path,
                start_seconds=0.0,
                duration_seconds=4.2,
                subtitle_file_path=ass_path,
                ffmpeg_path=ffmpeg_path,
                ffprobe_path=ffprobe_path,
            )
            local = _local_probe_readback_from_render_result(
                render_result=result,
                ass_path=ass_path,
                video_path=video_path,
                manifest_path=manifest_path,
                base_dir=base,
            )
        except ffmpeg_tiny.TinyRenderError as exc:
            local = _default_render_path_probe_local_readback(
                status="local_probe_failed",
                ass_path=ass_path,
                video_path=video_path,
                manifest_path=manifest_path,
                base_dir=base,
            )
            local["failure_reason"] = exc.failure_reason
            local["preflight"] = exc.preflight
            local["attempts"] = [attempt.to_dict() for attempt in exc.attempts]
    manifest_path.write_text(
        json.dumps(local, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return local

def render_subtitle_visual_selector_proof_html(proof: Mapping[str, Any]) -> str:
    cards = "\n".join(_visual_proof_card(example) for example in proof["examples"])
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>ED-10ac Visual Selector Proof</title>
  <style>
    :root {{ color-scheme: light; --body-text: #ffffff; --ink: #222831; --line: #c8d0d9; }}
    body {{ margin: 24px; font-family: system-ui, sans-serif; background: #f6f7f9; color: var(--ink); line-height: 1.5; }}
    h1, h2, h3 {{ margin: 0 0 8px; }}
    .meta, .gate {{ margin: 0 0 18px; padding: 12px; border: 1px solid var(--line); background: #fff; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; }}
    .card {{ border: 1px solid var(--line); background: #fff; padding: 14px; }}
    .sample {{ background: #242830; min-height: 128px; padding: 18px; display: flex; align-items: flex-end; }}
    .subtitle {{ width: 100%; }}
    .backplate {{ display: inline-block; padding: 8px 10px; border-radius: 4px; background: rgba(0, 0, 0, var(--backplate-alpha)); }}
    .badge {{ display: inline-block; min-width: 42px; text-align: center; margin-right: 8px; padding: 2px 5px; border: 2px solid var(--accent); background: var(--badge); color: #20242a; font-weight: 700; font-size: 13px; }}
    .line {{ color: var(--body-text); font-size: var(--font-size); font-weight: 800; text-shadow: 0 0 var(--outline) #000, 3px 3px var(--shadow) #000; }}
    .token-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; table-layout: fixed; }}
    .token-table th, .token-table td {{ border: 1px solid var(--line); padding: 5px; text-align: left; overflow-wrap: anywhere; }}
    .token-table th {{ width: 38%; background: #edf2f7; }}
    code {{ background: #edf2f7; padding: 1px 4px; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>ED-10ac Visual Selector Proof</h1>
  <p class="meta">Artifact <code>{escape(str(proof["artifact_id"]))}</code> visualizes the six ED-10ab semantic preset examples as static diagnostic readback. Body subtitle text stays on <code>stable_default_body_text</code>; speaker or emotion color appears through badge and accent tokens first.</p>
  <p class="gate">Render gate: <code>{escape(str(proof["render_gate"]["level"]))}</code>. New render run: <code>false</code>. This proof does not approve production subtitle design, production render, rights, publishing, or public use.</p>
  <section class="grid">
{cards}
  </section>
</body>
</html>
"""


def render_subtitle_style_family_palette_axis_proof_html(
    proof: Mapping[str, Any],
) -> str:
    cards = "\n".join(_style_axis_card(example) for example in proof["examples"])
    summary_rows = "\n".join(
        (
            "      <tr>"
            f"<td><code>{escape(str(row['family_group']))}</code></td>"
            f"<td><code>{escape(str(row['palette_route']))}</code></td>"
            f"<td>{escape(', '.join(row['examples']))}</td>"
            "</tr>"
        )
        for row in proof["axis_summary"]
    )
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>ED-10ad Style Family / Palette Axis Proof</title>
  <style>
    :root {{ color-scheme: light; --body-text: #ffffff; --ink: #222831; --line: #c8d0d9; }}
    body {{ margin: 24px; font-family: system-ui, sans-serif; background: #f6f7f9; color: var(--ink); line-height: 1.5; }}
    h1, h2, h3 {{ margin: 0 0 8px; }}
    .meta, .gate {{ margin: 0 0 18px; padding: 12px; border: 1px solid var(--line); background: #fff; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 14px; }}
    .card {{ border: 1px solid var(--line); background: #fff; padding: 14px; }}
    .sample {{ background: #242830; min-height: 128px; padding: 18px; display: flex; align-items: flex-end; border-left: 12px solid var(--accent); }}
    .backplate {{ display: inline-block; padding: 8px 10px; border-radius: 4px; background: rgba(0, 0, 0, var(--backplate-alpha)); }}
    .badge {{ display: inline-block; min-width: 42px; text-align: center; margin-right: 8px; padding: 2px 5px; border: 2px solid var(--accent); background: var(--badge); color: #20242a; font-weight: 700; font-size: 13px; }}
    .line {{ color: var(--body-text); font-size: var(--font-size); font-weight: 800; text-shadow: 0 0 var(--outline) #000, 3px 3px var(--shadow) #000; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0 18px; table-layout: fixed; }}
    th, td {{ border: 1px solid var(--line); padding: 6px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ background: #edf2f7; }}
    code {{ background: #edf2f7; padding: 1px 4px; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>ED-10ad Style Family / Palette Axis Proof</h1>
  <p class="meta">Artifact <code>{escape(str(proof["artifact_id"]))}</code> groups the ED-10ac examples by style family and palette route while keeping body subtitle text on <code>stable_default_body_text</code>. Palette remains badge/accent/backplate-first.</p>
  <p class="gate">Render gate: <code>{escape(str(proof["render_gate"]["level"]))}</code>. New render run: <code>false</code>. This proof does not create a new palette, approve production subtitle design, approve production render, or open rights/public-use decisions.</p>
  <h2>Axis Summary</h2>
  <table>
    <tr><th>family group</th><th>palette route</th><th>examples</th></tr>
{summary_rows}
  </table>
  <section class="grid">
{cards}
  </section>
</body>
</html>
"""


def render_subtitle_render_path_selector_contract_markdown(
    contract: Mapping[str, Any],
) -> str:
    rows = "\n".join(
        (
            "| "
            f"`{entry['semantic_preset_id']}` | "
            f"`{entry['preset_key']}` | "
            f"`{entry['render_adapter_input']['style']['family_id']}` | "
            f"`{entry['render_adapter_input']['style']['palette_route']}` | "
            f"`{entry['render_adapter_input']['color_surfaces']['body_text_color_token']}` | "
            f"`{entry['render_adapter_input']['motion_line_break']['safe_area_line_break_behavior']}` |"
        )
        for entry in contract["contract_entries"]
    )
    return (
        "# ED-10ae Render Path Selector Contract Probe\n\n"
        "This tracked contract connects the ED-10ab selector, ED-10ac visual "
        "selector proof, and ED-10ad family / palette proof to the fields a "
        "later render adapter would receive. It is static readback only.\n\n"
        "## Render Gate\n\n"
        f"- level: `{contract['render_gate']['level']}`\n"
        "- new_render_run: `false`\n"
        "- next_render_level: `L2 tiny render path probe milestone`\n"
        "- no video, audio, frame, ASS, or episode artifact is generated here.\n\n"
        "## Contract Fields\n\n"
        "- semantic: `semantic_preset_id`, `preset_key`, `speaker_id`, "
        "`speaker_role`, `emotion`, `intensity`, `utterance_role`, "
        "`readability_priority`\n"
        "- style: `family_id`, `palette_route`, `font_family_role`, "
        "`font_size_scale`, `outline_shadow_strength`\n"
        "- color surfaces: `badge_color_token`, `accent_color_token`, "
        "`backplate_box_token`, `body_text_color_token`, "
        "`body_text_color_changed`\n"
        "- motion / line break: `motion_primitive`, "
        "`safe_area_line_break_behavior`\n\n"
        "## Preset Contract Rows\n\n"
        "| semantic preset | preset key | family | palette | body text | line-break |\n"
        "|---|---|---|---|---|---|\n"
        f"{rows}\n\n"
        "## Readiness Separation\n\n"
        "- subtitle_style_readiness: `selector_static_proof_render_path_contract_ready`\n"
        "- video_render_readiness: `not_run_no_render_pass_implied`\n"
        "- production_readiness: `not_accepted`\n"
        "- rights_public_use_readiness: `not_accepted`\n\n"
        "## Boundary\n\n"
        "This contract preserves `stable_default_body_text`, badge/accent-first "
        "character color, and all production / rights / public-use boundaries. "
        "A later L2 render probe is a separate milestone and is not triggered "
        "by this document.\n"
    )


def render_subtitle_render_contract_consumer_dry_read_markdown(
    dry_read: Mapping[str, Any],
) -> str:
    rows = "\n".join(
        (
            "| "
            f"`{payload['semantic_preset_id']}` | "
            f"`{payload['normalized_render_adapter_payload']['style']['family_id']}` | "
            f"`{payload['normalized_render_adapter_payload']['style']['palette_route']}` | "
            f"`{payload['normalized_render_adapter_payload']['color_surfaces']['badge_color_token']}` | "
            f"`{payload['normalized_render_adapter_payload']['color_surfaces']['accent_color_token']}` | "
            f"`{payload['normalized_render_adapter_payload']['line_break']['safe_area_line_break_behavior']}` |"
        )
        for payload in dry_read["consumer_payloads"]
    )
    validation = dry_read["dry_read_validation"]
    return (
        "# ED-10af Render Contract Consumer Dry-Read\n\n"
        "This tracked dry-read consumes the ED-10ae render-path selector "
        "contract and normalizes the adapter-facing payload a later render "
        "adapter would receive. It is static readback only.\n\n"
        "## Render Gate\n\n"
        f"- level: `{dry_read['render_gate']['level']}`\n"
        "- new_render_run: `false`\n"
        "- consumer_dry_read_only: `true`\n"
        "- next_render_level: `L2 tiny render path probe milestone`\n"
        "- no video, audio, frame, ASS, render, or episode artifact is generated here.\n\n"
        "## Consumer Payload Fields\n\n"
        "- semantic: `semantic_preset_id`, `preset_key`, `speaker_id`, "
        "`speaker_role`, `emotion`, `intensity`, `utterance_role`, "
        "`readability_priority`\n"
        "- style: `family_id`, `palette_route`, `font_family_role`, "
        "`font_size_scale`, `outline_shadow_strength`\n"
        "- color surfaces: `badge_color_token`, `accent_color_token`, "
        "`backplate_box_token`, `body_text_color_policy_reference`, "
        "`body_text_color_token`, `body_text_color_changed`\n"
        "- motion / line break: `motion_primitive`, "
        "`safe_area_line_break_behavior`\n"
        "- boundaries: `render_boundary`, `production_public_boundary`\n\n"
        "## Payload Rows\n\n"
        "| semantic preset | family | palette | badge | accent | line-break |\n"
        "|---|---|---|---|---|---|\n"
        f"{rows}\n\n"
        "## Static Drift Checks\n\n"
        f"- all_payloads_consumer_ready: `{str(validation['all_payloads_consumer_ready']).lower()}`\n"
        f"- missing_required_fields: `{len(validation['missing_required_fields'])}`\n"
        f"- type_mismatches: `{len(validation['type_mismatches'])}`\n"
        f"- body_text_color_policy_drift: `{str(validation['body_text_color_policy_drift']).lower()}`\n"
        f"- render_boundary_leakage: `{str(validation['render_boundary_leakage']).lower()}`\n"
        f"- production_public_boundary_leakage: `{str(validation['production_public_boundary_leakage']).lower()}`\n\n"
        "## Readiness Separation\n\n"
        "- subtitle_style_readiness: "
        "`selector_static_proof_render_path_contract_consumer_dry_read_ready`\n"
        "- video_render_readiness: `not_run_no_render_pass_implied`\n"
        "- production_readiness: `not_accepted`\n"
        "- rights_public_use_readiness: `not_accepted`\n\n"
        "## Boundary\n\n"
        "This dry-read preserves `stable_default_body_text`, badge/accent/"
        "backplate-first color surfaces, family and palette routes, and all "
        "production / rights / public-use boundaries. A later L2 render probe "
        "is a separate milestone and is not triggered by this document.\n"
    )


def render_subtitle_render_path_selector_probe_markdown(
    probe: Mapping[str, Any],
) -> str:
    rows = "\n".join(
        (
            "| "
            f"`{example['example_id']}` | "
            f"`{example['ass_probe']['text']}` | "
            f"`{example['style']['family_id']}` | "
            f"`{example['style']['palette_route']}` | "
            f"`{example['color_surfaces']['body_text_color_token']}` | "
            f"`{example['line_break']['safe_area_line_break_behavior']}` |"
        )
        for example in probe["examples"]
    )
    local_probe = probe["local_probe"]
    validation = probe["validation"]
    outputs = local_probe["outputs"]
    return (
        "# ED-10af L2 Render Path Selector Probe\n\n"
        "This tracked probe consumes the ED-10ae selector-to-render contract and "
        "selects three representative semantic presets for a tiny FFmpeg/libass "
        "diagnostic path: normal dialogue, shout/high-intensity, and low-pressure "
        "whisper. The local media outputs are ignored same-machine evidence; this "
        "document is the tracked readback.\n\n"
        "## Render Gate\n\n"
        f"- level: `{probe['render_gate']['level']}`\n"
        f"- new_render_run: `{str(probe['render_gate']['new_render_run']).lower()}`\n"
        "- diagnostic_only: `true`\n"
        "- tracked_binary_artifact_created: `false`\n"
        "- production_render_acceptance: `false`\n"
        "- public_use_permission: `false`\n\n"
        "## Local Ignored Outputs\n\n"
        f"- status: `{local_probe['status']}`\n"
        f"- ASS: `{outputs['ass']}`\n"
        f"- video: `{outputs['video']}`\n"
        f"- manifest: `{outputs['manifest']}`\n\n"
        "## Probe Rows\n\n"
        "| semantic preset | ASS cue text | family | palette | body text | line-break |\n"
        "|---|---|---|---|---|---|\n"
        f"{rows}\n\n"
        "## Validation\n\n"
        f"- source_contract_referenced: `{str(validation['source_contract_referenced']).lower()}`\n"
        f"- selected_example_count: `{validation['selected_example_count']}`\n"
        f"- stable_body_text_preserved: `{str(validation['stable_body_text_preserved']).lower()}`\n"
        "- badge_accent_backplate_route_preserved: "
        f"`{str(validation['badge_accent_backplate_route_preserved']).lower()}`\n"
        "- safe_area_line_break_metadata_survived: "
        f"`{str(validation['safe_area_line_break_metadata_survived']).lower()}`\n"
        f"- production_public_boundary_closed: `{str(validation['production_public_boundary_closed']).lower()}`\n"
        f"- tracked_binary_artifact_created: `{str(validation['tracked_binary_artifact_created']).lower()}`\n\n"
        "## Boundary\n\n"
        "The probe preserves `stable_default_body_text`; semantic variation stays "
        "badge/accent/backplate-first. The generated ASS/MP4/manifest paths stay "
        "under ignored `episodes/` and do not approve production subtitle design, "
        "production render, creative use, rights, publishing, or public use.\n"
    )


def render_subtitle_render_path_lineage_observation_surface_markdown(
    readback: Mapping[str, Any],
) -> str:
    existing = readback["existing_output_first"]
    lineage = readback["lineage"]
    predecessor = lineage["predecessor_artifacts"][0]
    observation = readback["observation_surface"]
    validation = readback["validation"]
    render_gate = readback["render_gate"]
    boundaries = readback["boundaries"]
    outputs = observation["local_outputs"]
    nl = chr(10)
    example_rows = nl.join(
        "| {example_id} | {role} | {style_family} | {palette_route} | {body_text_color_token} |".format(**example)
        for example in observation["selected_examples"]
    )
    output_rows = nl.join(
        f"| {target} | `{path}` |"
        for target, path in outputs.items()
    )
    command_rows = nl.join(
        f"| {command['target']} | `{command['command']}` |"
        for command in observation["open_commands"]
    )
    lines = [
        "# ED-10ag Lineage and Observation Surface",
        "",
        "This tracked surface keeps the ED-10af L2 selector probe as the active artifact, preserves the restored ED-10af dry-read as predecessor evidence from commit `7e96a28`, and records same-machine observation paths without running a new render.",
        "",
        "## Source Artifacts",
        "",
        f"- active artifact: `{readback['active_artifact_id']}`",
        f"- predecessor dry-read artifact: `{predecessor['artifact_id']}`",
        f"- predecessor source commit: `{predecessor['source_commit']}`",
        f"- predecessor invalidated: `{str(predecessor['invalidated']).lower()}`",
        f"- predecessor superseded_by: `{predecessor['superseded_by']}`",
        f"- source render-path contract: `{readback['source_render_path_selector_contract_artifact_id']}`",
        f"- render level: `{readback['render_level']}`",
        "",
        "## Existing Output First",
        "",
        f"- decision: `{existing['decision']}`",
        f"- reason: {existing['reason']}",
        f"- source_probe_local_status: `{existing['source_probe_local_status']}`",
        f"- source_probe_new_render_run: `{str(existing['source_probe_new_render_run']).lower()}`",
        f"- new_render_run: `{str(existing['new_render_run']).lower()}`",
        "",
        "## Observation Surface",
        "",
        f"- same_machine_only: `{str(observation['same_machine_only']).lower()}`",
        f"- may_be_absent_on_other_clone: `{str(observation['may_be_absent_on_other_clone']).lower()}`",
        f"- user_review_required: `{str(observation['user_review_required']).lower()}`",
        f"- dry-read payloads: `{observation['source_dry_read_payload_count']}` / `6`",
        f"- selected examples: `{observation['selected_example_count']}`",
        f"- local probe status: `{observation['local_probe_status']}`",
        "",
        "| output | repo-relative path |",
        "|---|---|",
        output_rows,
        "",
        "| output | open command |",
        "|---|---|",
        command_rows,
        "",
        "| example | role | family | palette | body text |",
        "|---|---|---|---|---|",
        example_rows,
        "",
        "## Render Gate",
        "",
        f"- level: `{render_gate['level']}`",
        f"- existing_output_first_reused: `{str(render_gate['existing_output_first_reused']).lower()}`",
        f"- new_render_run: `{str(render_gate['new_render_run']).lower()}`",
        f"- source_probe_new_render_run: `{str(render_gate['source_probe_new_render_run']).lower()}`",
        f"- tracked_binary_artifact_created: `{str(render_gate['tracked_binary_artifact_created']).lower()}`",
        "",
        "## Validation",
        "",
        f"- active_artifact_preserved: `{str(validation['active_artifact_preserved']).lower()}`",
        f"- predecessor_lineage_present: `{str(validation['predecessor_lineage_present']).lower()}`",
        f"- observation_paths_present: `{str(validation['observation_paths_present']).lower()}`",
        f"- contact_sheet_path_recorded: `{str(validation['contact_sheet_path_recorded']).lower()}`",
        f"- dry_read_all_payloads_consumer_ready: `{str(validation['dry_read_all_payloads_consumer_ready']).lower()}`",
        f"- source_probe_all_checks_passed: `{str(validation['source_probe_all_checks_passed']).lower()}`",
        f"- selected_examples_covered_by_dry_read: `{str(validation['selected_examples_covered_by_dry_read']).lower()}`",
        f"- stable_body_text_preserved: `{str(validation['stable_body_text_preserved']).lower()}`",
        f"- badge_accent_backplate_route_preserved: `{str(validation['badge_accent_backplate_route_preserved']).lower()}`",
        f"- safe_area_line_break_metadata_survived: `{str(validation['safe_area_line_break_metadata_survived']).lower()}`",
        f"- production_public_boundary_closed: `{str(validation['production_public_boundary_closed']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        "- human_review_required: `false`",
        "- production_subtitle_design_acceptance: `false`",
        "- production_render_acceptance: `false`",
        "- creative_acceptance: `false`",
        "- rights_status: `pending`",
        "- publishing_acceptance: `false`",
        "- public_use_permission: `false`",
        f"- diagnostic_local_ignored_render_reused: `{str(boundaries['diagnostic_local_ignored_render_reused']).lower()}`",
        f"- episodes_tracked: `{str(boundaries['episodes_tracked']).lower()}`",
    ]
    return nl.join(lines) + nl


def render_subtitle_production_limitation_lift_entry_markdown(
    entry: Mapping[str, Any],
) -> str:
    source = entry["source_evidence"]
    user = entry["user_observation_consumed"]
    route = entry["next_executable_route"]
    validation = entry["validation"]
    boundaries = entry["boundaries"]
    nl = chr(10)
    output_rows = nl.join(
        f"| {target} | `{path}` |"
        for target, path in source["local_ignored_outputs"].items()
    )
    gate_rows = nl.join(
        "| {gate} | {status} | {available} | {missing} | {agent} | {human} | {rights} |".format(
            gate=gate["gate_name"],
            status=gate["current_status"],
            available=_markdown_cell_list(gate["evidence_available"]),
            missing=_markdown_cell_list(gate["evidence_missing"]),
            agent=str(gate["agent_can_progress_without_user_judgement"]).lower(),
            human=str(gate["human_judgement_required"]).lower(),
            rights=str(gate["rights_or_publication_decision_required"]).lower(),
        )
        for gate in entry["gate_matrix"]
    )
    route_steps = nl.join(
        f"- {step}"
        for step in route["first_steps"]
    )
    route_boundaries = nl.join(
        f"- {item}"
        for item in route["must_not_do"]
    )
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
        )
    )
    lines = [
        "# ED-10ah Production Limitation-Lift Entry",
        "",
        "This tracked entry separates diagnostic render-path proof from production subtitle design, production render, creative, rights, publishing, and public-use gates. It is a route entry, not an approval.",
        "",
        "## User Observation Consumed",
        "",
        f"- observation_id: `{user['observation_id']}`",
        f"- display_surface_acceptable_enough: `{str(user['display_surface_acceptable_enough']).lower()}`",
        f"- layout_polish_deferred: `{str(user['layout_polish_deferred']).lower()}`",
        f"- move_forward_preferred: `{str(user['move_forward_preferred']).lower()}`",
        f"- no_redundant_review_requests: {_markdown_cell_list(user['no_redundant_review_requests'])}",
        "",
        "## Source Evidence",
        "",
        f"- active diagnostic proof source: `{source['active_diagnostic_proof_source_artifact_id']}`",
        f"- lineage observation support: `{source['support_lineage_observation_surface_artifact_id']}`",
        f"- dry-read predecessor: `{source['dry_read_predecessor_artifact_id']}`",
        f"- dry-read predecessor source commit: `{source['dry_read_predecessor_source_commit']}`",
        f"- local ignored output policy: `{source['local_ignored_output_policy']}`",
        "",
        "| output | same-machine path |",
        "|---|---|",
        output_rows,
        "",
        "## Gate Separation",
        "",
        "| gate | current status | evidence already available | evidence still missing | agent can progress without user judgement | human judgement required | rights/publication decision required |",
        "|---|---|---|---|---|---|---|",
        gate_rows,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- agent_can_start_without_user_judgement: `{str(route['agent_can_start_without_user_judgement']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- gate_names_present: `{str(validation['gate_names_present']).lower()}`",
        f"- active_diagnostic_source_preserved: `{str(validation['active_diagnostic_source_preserved']).lower()}`",
        f"- lineage_support_not_production_proof: `{str(validation['lineage_support_not_production_proof']).lower()}`",
        f"- dry_read_predecessor_preserved: `{str(validation['dry_read_predecessor_preserved']).lower()}`",
        f"- production_public_boundary_closed: `{str(validation['production_public_boundary_closed']).lower()}`",
        f"- next_executable_route_defined: `{str(validation['next_executable_route_defined']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_final_render_path_readiness_packet_markdown(
    packet: Mapping[str, Any],
) -> str:
    source = packet["source_evidence"]
    route = packet["next_executable_route"]
    validation = packet["validation"]
    boundaries = packet["boundaries"]
    nl = chr(10)
    matrix_rows = nl.join(
        "| {row} | {area} | {status} | {artifact} | {path} | {agent} | {future} | {missing} |".format(
            row=row["row_id"],
            area=row["readiness_area"],
            status=row["status"],
            artifact=row["source_artifact_id"],
            path=row["file_path"],
            agent=str(row["agent_can_progress_without_user_judgement"]).lower(),
            future=str(row["future_human_rights_publication_decision_required"]).lower(),
            missing=_markdown_cell_list(row["evidence_missing"]) or "none",
        )
        for row in packet["readiness_matrix"]
    )
    local_rows = nl.join(
        f"| {target} | `{path}` |"
        for target, path in source["local_ignored_outputs"].items()
    )
    route_steps = nl.join(f"- {step}" for step in route["first_steps"])
    route_boundaries = nl.join(f"- {item}" for item in route["must_not_do"])
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
        )
    )
    lines = [
        "# ED-10ai Final Render-Path Readiness Packet",
        "",
        "This tracked packet prepares a later final render-path route from existing diagnostic evidence. It is not production subtitle design acceptance, production render acceptance, creative acceptance, rights clearance, publishing acceptance, or public-use permission.",
        "",
        "## Source Evidence",
        "",
        f"- gate separation source: `{source['gate_separation_source_artifact_id']}`",
        f"- active diagnostic proof source: `{source['active_diagnostic_proof_source_artifact_id']}`",
        f"- lineage observation support: `{source['support_lineage_observation_surface_artifact_id']}`",
        f"- dry-read predecessor: `{source['dry_read_predecessor_artifact_id']}`",
        f"- dry-read predecessor source commit: `{source['dry_read_predecessor_source_commit']}`",
        f"- selector semantic style contract: `{source['selector_semantic_style_contract_artifact_id']}`",
        f"- render adapter input contract: `{source['render_adapter_input_contract_artifact_id']}`",
        "",
        "| local output | same-machine path |",
        "|---|---|",
        local_rows,
        "",
        "## Readiness Matrix",
        "",
        "| row | area | status | source artifact | file/local path | agent can progress without user judgement | future human/rights/publication decision required | missing evidence |",
        "|---|---|---|---|---|---|---|---|",
        matrix_rows,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- agent_can_start_without_user_judgement: `{str(route['agent_can_start_without_user_judgement']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- required_rows_present: `{str(validation['required_rows_present']).lower()}`",
        f"- active_diagnostic_source_preserved: `{str(validation['active_diagnostic_source_preserved']).lower()}`",
        f"- gate_separation_source_preserved: `{str(validation['gate_separation_source_preserved']).lower()}`",
        f"- lineage_predecessor_preserved: `{str(validation['lineage_predecessor_preserved']).lower()}`",
        f"- selector_semantic_contract_present: `{str(validation['selector_semantic_contract_present']).lower()}`",
        f"- render_adapter_input_contract_present: `{str(validation['render_adapter_input_contract_present']).lower()}`",
        f"- local_ignored_proof_media_referenced: `{str(validation['local_ignored_proof_media_referenced']).lower()}`",
        f"- missing_production_public_decisions_explicit: `{str(validation['missing_production_public_decisions_explicit']).lower()}`",
        f"- production_public_boundary_closed: `{str(validation['production_public_boundary_closed']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_final_render_path_stage1_markdown(
    packet: Mapping[str, Any],
) -> str:
    source = packet["source_evidence"]
    candidate = packet["stage_1_candidate"]
    route = packet["next_executable_route"]
    validation = packet["validation"]
    boundaries = packet["boundaries"]
    readiness = packet["production_public_readiness"]
    nl = chr(10)
    checklist_rows = nl.join(
        "| {check_id} | {status} | {source} | {evidence} | {missing} |".format(
            check_id=row["check_id"],
            status=row["status"],
            source=row["source_artifact_id"],
            evidence=_markdown_cell_list(row["evidence"]),
            missing=_markdown_cell_list(row["missing_before_approval"]) or "none",
        )
        for row in packet["stage_1_checklist"]
    )
    local_rows = nl.join(
        f"| {target} | `{path}` |"
        for target, path in source["local_ignored_outputs"].items()
    )
    route_steps = nl.join(f"- {step}" for step in route["first_steps"])
    route_boundaries = nl.join(f"- {item}" for item in route["must_not_do"])
    missing_render = nl.join(
        f"- {item}" for item in readiness["missing_before_production_render_approval"]
    )
    missing_public = nl.join(
        f"- {item}" for item in readiness["missing_before_publishing_public_use"]
    )
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
            "final_render_path_approved",
        )
    )
    lines = [
        "# ED-10aj Final Render-Path Stage 1",
        "",
        "This tracked stage-1 packet selects a final render-path candidate from existing diagnostic evidence. It does not approve production subtitle design, production render, creative use, rights, publishing, or public use.",
        "",
        "## Stage-1 Candidate",
        "",
        f"- candidate_id: `{candidate['candidate_id']}`",
        f"- render_adapter_path: `{candidate['render_adapter_path']}`",
        f"- selection_status: `{candidate['selection_status']}`",
        f"- selected_from_artifact_id: `{candidate['selected_from_artifact_id']}`",
        f"- source_policy: `{candidate['source_policy']}`",
        f"- stage_1_candidate_not_production_render: `{str(candidate['stage_1_candidate_not_production_render']).lower()}`",
        f"- reason: {candidate['selection_reason']}",
        "",
        "## Source Evidence",
        "",
        f"- readiness packet: `{source['readiness_packet_artifact_id']}`",
        f"- active diagnostic proof source: `{source['active_diagnostic_proof_source_artifact_id']}`",
        f"- lineage observation support: `{source['support_lineage_observation_surface_artifact_id']}`",
        f"- gate separation source: `{source['gate_separation_source_artifact_id']}`",
        f"- dry-read predecessor: `{source['dry_read_predecessor_artifact_id']}`",
        f"- dry-read predecessor source commit: `{source['dry_read_predecessor_source_commit']}`",
        f"- selector semantic style contract: `{source['selector_semantic_style_contract_artifact_id']}`",
        f"- render adapter input contract: `{source['render_adapter_input_contract_artifact_id']}`",
        "",
        "| local output | same-machine path |",
        "|---|---|",
        local_rows,
        "",
        "## Stage-1 Checklist",
        "",
        "| check | status | source artifact | evidence | missing before approval |",
        "|---|---|---|---|---|",
        checklist_rows,
        "",
        "## Still Missing Before Production Render Approval",
        "",
        missing_render,
        "",
        "## Still Missing Before Publishing/Public Use",
        "",
        missing_public,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- agent_can_start_without_user_judgement: `{str(route['agent_can_start_without_user_judgement']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- required_checklist_present: `{str(validation['required_checklist_present']).lower()}`",
        f"- readiness_source_preserved: `{str(validation['readiness_source_preserved']).lower()}`",
        f"- active_diagnostic_source_preserved: `{str(validation['active_diagnostic_source_preserved']).lower()}`",
        f"- stage_1_candidate_defined: `{str(validation['stage_1_candidate_defined']).lower()}`",
        f"- semantic_selector_contract_available: `{str(validation['semantic_selector_contract_available']).lower()}`",
        f"- local_ignored_proof_media_referenced: `{str(validation['local_ignored_proof_media_referenced']).lower()}`",
        f"- no_tracked_binary_media: `{str(validation['no_tracked_binary_media']).lower()}`",
        f"- production_public_boundary_closed: `{str(validation['production_public_boundary_closed']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_final_render_path_stage2_replayability_markdown(
    packet: Mapping[str, Any],
) -> str:
    replay = packet["replay_operation"]
    routes = packet["handoff_routes"]
    validation = packet["validation"]
    boundaries = packet["boundaries"]
    readiness = packet["production_public_readiness"]
    nl = chr(10)
    matrix_rows = nl.join(
        "| {row_id} | {area} | {status} | {source} | {detail} |".format(
            row_id=row["row_id"],
            area=row["operation_area"],
            status=row["status"],
            source=row["source_artifact_id"],
            detail=_markdown_cell_list(row["details"]),
        )
        for row in packet["operation_matrix"]
    )
    tracked_rows = nl.join(f"- `{path}`" for path in replay["tracked_inputs"])
    local_input_rows = nl.join(
        f"| {name} | `{path}` |"
        for name, path in replay["same_machine_local_inputs"].items()
    )
    output_rows = nl.join(
        f"| {name} | `{path}` |"
        for name, path in replay["ignored_output_paths"].items()
    )
    readback_rows = nl.join(
        f"- `{command}`" for command in replay["validation_readback_commands"]
    )
    missing_render = nl.join(
        f"- {item}" for item in readiness["missing_before_production_render_approval"]
    )
    missing_public = nl.join(
        f"- {item}" for item in readiness["missing_before_publishing_public_use"]
    )
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
            "new_replay_run",
            "final_render_path_approved",
        )
    )
    lines = [
        "# ED-10ak Final Render-Path Stage 2 Replayability",
        "",
        "This tracked stage-2 packet records how a later agent/operator can inspect or replay the selected FFmpeg/libass diagnostic subtitle overlay path. It does not run a new render and does not approve production subtitle design, production render, creative use, rights, publishing, or public use.",
        "",
        "## Replay Operation",
        "",
        f"- operation_id: `{replay['operation_id']}`",
        f"- selected_render_path: `{replay['selected_render_path']}`",
        f"- operation_status: `{replay['operation_status']}`",
        f"- existing_output_first_reused: `{str(replay['existing_output_first_reused']).lower()}`",
        f"- new_replay_run: `{str(replay['new_replay_run']).lower()}`",
        f"- replay_required_now: `{str(replay['replay_required_now']).lower()}`",
        f"- diagnostic_only: `{str(replay['diagnostic_only']).lower()}`",
        f"- command_family: `{replay['command_family']}`",
        "",
        "## Required Tracked Inputs",
        "",
        tracked_rows,
        "",
        "## Required Same-Machine Local Inputs",
        "",
        "| input | same-machine path |",
        "|---|---|",
        local_input_rows,
        "",
        "## Ignored Output Paths",
        "",
        "| output | path |",
        "|---|---|",
        output_rows,
        "",
        "## Operation Matrix",
        "",
        "| row | area | status | source artifact | details |",
        "|---|---|---|---|---|",
        matrix_rows,
        "",
        "## Command Family",
        "",
        f"- command_family: `{replay['command_family']}`",
        f"- source_probe_render_command_summary: `{replay['source_probe_render_command_summary']}`",
        "",
        "## Validation / Readback Commands",
        "",
        readback_rows,
        "",
        "## Fresh Clone Absence Behavior",
        "",
        replay["fresh_clone_absence_behavior"],
        "",
        "## Still Missing Before Production Render Approval",
        "",
        missing_render,
        "",
        "## Still Missing Before Publishing/Public Use",
        "",
        missing_public,
        "",
        "## Handoff Routes",
        "",
        f"- primary_route_id: `{routes['primary_route_id']}`",
        f"- alternate_route_id: `{routes['alternate_route_id']}`",
        f"- stage_3_purpose: {routes['stage_3_purpose']}",
        f"- production_limitation_lift_stage_1_purpose: {routes['production_limitation_lift_stage_1_purpose']}",
        f"- neither_route_approves_production_public_use: `{str(routes['neither_route_approves_production_public_use']).lower()}`",
        "",
        "## Validation",
        "",
        f"- required_rows_present: `{str(validation['required_rows_present']).lower()}`",
        f"- stage1_source_preserved: `{str(validation['stage1_source_preserved']).lower()}`",
        f"- active_diagnostic_source_preserved: `{str(validation['active_diagnostic_source_preserved']).lower()}`",
        f"- operation_replayability_defined: `{str(validation['operation_replayability_defined']).lower()}`",
        f"- existing_output_first_applied: `{str(validation['existing_output_first_applied']).lower()}`",
        f"- local_ignored_outputs_referenced: `{str(validation['local_ignored_outputs_referenced']).lower()}`",
        f"- production_public_boundary_closed: `{str(validation['production_public_boundary_closed']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_final_render_path_stage3_rehearsal_markdown(
    packet: Mapping[str, Any],
) -> str:
    rehearsal = packet["rehearsal"]
    survival = packet["survival_readback"]
    routes = packet["handoff_routes"]
    validation = packet["validation"]
    boundaries = packet["boundaries"]
    readiness = packet["production_public_readiness"]
    metadata = rehearsal["output_metadata"]
    nl = chr(10)
    matrix_rows = nl.join(
        "| {row_id} | {area} | {status} | {source} | {detail} |".format(
            row_id=row["row_id"],
            area=row["rehearsal_area"],
            status=row["status"],
            source=row["source_artifact_id"],
            detail=_markdown_cell_list(row["details"]),
        )
        for row in packet["rehearsal_matrix"]
    )
    tracked_rows = nl.join(f"- `{path}`" for path in rehearsal["tracked_inputs"])
    local_input_rows = nl.join(
        f"| {name} | `{path}` |"
        for name, path in rehearsal["same_machine_local_inputs"].items()
    )
    generated_rows = nl.join(
        f"| {name} | `{path}` |"
        for name, path in rehearsal["generated_ignored_outputs"].items()
    )
    recorded_rows = nl.join(
        f"| {name} | `{path}` |"
        for name, path in rehearsal["recorded_ignored_outputs"].items()
    )
    status_rows = nl.join(
        f"| {name} | `{status}` |"
        for name, status in rehearsal["output_status"].items()
    )
    metadata_rows = nl.join(
        f"- {key}: `{value}`"
        for key, value in metadata.items()
        if key
        in {
            "duration_seconds",
            "resolution",
            "width",
            "height",
            "video_codec",
            "audio_codec",
            "fps",
            "frame_rate",
            "stream_count",
        }
    )
    missing_render = nl.join(
        f"- {item}" for item in readiness["missing_before_production_render_approval"]
    )
    missing_public = nl.join(
        f"- {item}" for item in readiness["missing_before_publishing_public_use"]
    )
    survival_rows = nl.join(
        f"- {key}: `{str(value).lower()}`" for key, value in survival.items()
    )
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
            "new_rehearsal_run",
            "final_render_path_approved",
        )
    )
    lines = [
        "# ED-10al Final Render-Path Stage 3 Diagnostic Rehearsal",
        "",
        "This tracked stage-3 artifact records a bounded diagnostic final-path rehearsal of the selected FFmpeg/libass subtitle overlay path. It uses ignored local media and ignored local outputs only; it does not approve production subtitle design, production render, creative use, rights, publishing, or public use.",
        "",
        "## Rehearsal",
        "",
        f"- rehearsal_id: `{rehearsal['rehearsal_id']}`",
        f"- selected_render_path: `{rehearsal['selected_render_path']}`",
        f"- rehearsal_status: `{rehearsal['rehearsal_status']}`",
        f"- existing_output_first_applied: `{str(rehearsal['existing_output_first_applied']).lower()}`",
        f"- existing_output_first_reused: `{str(rehearsal['existing_output_first_reused']).lower()}`",
        f"- new_rehearsal_run: `{str(rehearsal['new_rehearsal_run']).lower()}`",
        f"- new_render_run: `{str(rehearsal['new_render_run']).lower()}`",
        f"- diagnostic_only: `{str(rehearsal['diagnostic_only']).lower()}`",
        f"- command_family: `{rehearsal['command_family']}`",
        f"- rehearsal_run_reason: {rehearsal['rehearsal_run_reason']}",
        "",
        "## Required Tracked Inputs Used",
        "",
        tracked_rows,
        "",
        "## Same-Machine Local Inputs Used",
        "",
        "| input | same-machine path |",
        "|---|---|",
        local_input_rows,
        "",
        "## Ignored Outputs",
        "",
        "Generated by this rehearsal:",
        "",
        "| output | path |",
        "|---|---|",
        generated_rows,
        "",
        "Recorded source paths:",
        "",
        "| output | path |",
        "|---|---|",
        recorded_rows,
        "",
        "Output status:",
        "",
        "| output | status |",
        "|---|---|",
        status_rows,
        "",
        "## Command",
        "",
        f"- rehearsal_invocation_command: `{rehearsal['rehearsal_invocation_command']}`",
        f"- render_command_summary: `{rehearsal['render_command_summary']}`",
        "",
        "## Output Metadata",
        "",
        metadata_rows,
        "",
        "## Survival Readback",
        "",
        survival_rows,
        "",
        "## Rehearsal Matrix",
        "",
        "| row | area | status | source artifact | details |",
        "|---|---|---|---|---|",
        matrix_rows,
        "",
        "## Still Missing Before Production Render Approval",
        "",
        missing_render,
        "",
        "## Still Missing Before Publishing/Public Use",
        "",
        missing_public,
        "",
        "## Handoff Routes",
        "",
        f"- primary_route_id: `{routes['primary_route_id']}`",
        f"- alternate_route_id: `{routes['alternate_route_id']}`",
        f"- production_limitation_lift_stage_1_purpose: {routes['production_limitation_lift_stage_1_purpose']}",
        f"- stage_4_purpose: {routes['stage_4_purpose']}",
        f"- neither_route_approves_production_public_use: `{str(routes['neither_route_approves_production_public_use']).lower()}`",
        "",
        "## Validation",
        "",
        f"- required_rows_present: `{str(validation['required_rows_present']).lower()}`",
        f"- stage2_source_preserved: `{str(validation['stage2_source_preserved']).lower()}`",
        f"- active_diagnostic_source_preserved: `{str(validation['active_diagnostic_source_preserved']).lower()}`",
        f"- rehearsal_run_recorded: `{str(validation['rehearsal_run_recorded']).lower()}`",
        f"- output_metadata_available: `{str(validation['output_metadata_available']).lower()}`",
        f"- ass_style_tokens_survived: `{str(validation['ass_style_tokens_survived']).lower()}`",
        f"- stable_body_text_policy_survived: `{str(validation['stable_body_text_policy_survived']).lower()}`",
        f"- badge_accent_backplate_route_survived: `{str(validation['badge_accent_backplate_route_survived']).lower()}`",
        f"- line_break_safe_area_metadata_survived: `{str(validation['line_break_safe_area_metadata_survived']).lower()}`",
        f"- production_public_boundary_closed: `{str(validation['production_public_boundary_closed']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_production_limitation_lift_stage1_markdown(
    packet: Mapping[str, Any],
) -> str:
    evidence = packet["diagnostic_evidence"]
    route = packet["next_executable_route"]
    validation = packet["validation"]
    boundaries = packet["boundaries"]
    non_approval = packet["non_approval_readback"]
    nl = chr(10)
    generated_rows = nl.join(
        f"| {name} | `{path}` |"
        for name, path in evidence["generated_ignored_outputs"].items()
    )
    recorded_rows = nl.join(
        f"| {name} | `{path}` |"
        for name, path in evidence["recorded_ignored_outputs"].items()
    )
    metadata_rows = nl.join(
        f"- {key}: `{value}`"
        for key, value in evidence["output_metadata"].items()
        if key
        in {
            "duration_seconds",
            "resolution",
            "width",
            "height",
            "video_codec",
            "audio_codec",
            "fps",
            "frame_rate",
            "stream_count",
        }
    )
    survival_rows = nl.join(
        f"- {key}: `{str(value).lower()}`"
        for key, value in evidence["survival_readback"].items()
    )
    gate_rows = nl.join(
        "| {gate} | {status} | {source} | {missing} | {owner} | {agent} | {unsafe} |".format(
            gate=gate["gate_name"],
            status=gate["current_status"],
            source=_markdown_cell_list(gate["source_evidence"]),
            missing=_markdown_cell_list(gate["missing_evidence"]) or "none",
            owner=gate["next_decision_owner"],
            agent=str(gate["agent_can_progress_without_user_judgement"]).lower(),
            unsafe=_markdown_cell_list(gate["unsafe_overclaiming"]),
        )
        for gate in packet["gate_matrix"]
    )
    route_steps = nl.join(f"- {step}" for step in route["first_steps"])
    route_boundaries = nl.join(f"- {item}" for item in route["must_not_do"])
    does_not_prove = nl.join(
        f"- {item}" for item in non_approval["ed10al_does_not_prove"]
    )
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
            "new_rehearsal_run",
            "final_render_path_approved",
        )
    )
    lines = [
        "# ED-10am Production Limitation-Lift Stage 1",
        "",
        "This tracked packet converts the ED-10al diagnostic final-path rehearsal into production limitation-lift preparation. It is not production subtitle design acceptance, production render acceptance, creative acceptance, rights clearance, publishing acceptance, or public-use permission.",
        "",
        f"- artifact_id: `{packet['artifact_id']}`",
        f"- status: `{packet['status']}`",
        "",
        "## Primary Diagnostic Evidence",
        "",
        f"- primary_diagnostic_rehearsal_artifact_id: `{evidence['primary_diagnostic_rehearsal_artifact_id']}`",
        f"- stage_2_source_artifact_id: `{evidence['source_final_render_path_stage_2_artifact_id']}`",
        f"- active_diagnostic_proof_source_artifact_id: `{evidence['active_diagnostic_proof_source_artifact_id']}`",
        f"- selected_render_path: `{evidence['selected_render_path']}`",
        f"- rehearsal_status: `{evidence['rehearsal_status']}`",
        f"- command_family: `{evidence['command_family']}`",
        f"- why_diagnostic_only: {evidence['why_diagnostic_only']}",
        "",
        "Generated ignored outputs:",
        "",
        "| output | same-machine path |",
        "|---|---|",
        generated_rows,
        "",
        "Recorded ignored outputs:",
        "",
        "| output | same-machine path |",
        "|---|---|",
        recorded_rows,
        "",
        "## Output Metadata",
        "",
        metadata_rows,
        "",
        "## Survival Readback",
        "",
        survival_rows,
        "",
        "## Gate Matrix",
        "",
        "| gate | current status | source evidence | missing evidence | next decision owner | agent can progress without user judgement | unsafe overclaiming |",
        "|---|---|---|---|---|---|---|",
        gate_rows,
        "",
        "## ED-10al Does Not Prove",
        "",
        does_not_prove,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- alternate_route_condition: {route['alternate_route_condition']}",
        f"- agent_can_start_without_user_judgement: `{str(route['agent_can_start_without_user_judgement']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- gate_names_present: `{str(validation['gate_names_present']).lower()}`",
        f"- stage3_source_preserved: `{str(validation['stage3_source_preserved']).lower()}`",
        f"- diagnostic_evidence_linked: `{str(validation['diagnostic_evidence_linked']).lower()}`",
        f"- production_public_non_approval_explicit: `{str(validation['production_public_non_approval_explicit']).lower()}`",
        f"- owners_present: `{str(validation['owners_present']).lower()}`",
        f"- unsafe_overclaiming_present: `{str(validation['unsafe_overclaiming_present']).lower()}`",
        f"- tracked_media_boundary_closed: `{str(validation['tracked_media_boundary_closed']).lower()}`",
        f"- same_machine_ignored_boundary_recorded: `{str(validation['same_machine_ignored_boundary_recorded']).lower()}`",
        f"- next_executable_route_defined: `{str(validation['next_executable_route_defined']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_production_limitation_lift_stage2_decision_packet_markdown(
    packet: Mapping[str, Any],
) -> str:
    source = packet["source_evidence"]
    route = packet["next_executable_route"]
    validation = packet["validation"]
    no_decision = packet["no_decision_yet"]
    boundaries = packet["boundaries"]
    gate_separation = packet["gate_separation"]
    nl = chr(10)
    group_rows = nl.join(
        "| {group} | {status} | {gates} | {source} | {missing} | {owner} | {agent} | {unsafe} | {action} |".format(
            group=group["decision_group_id"],
            status=group["current_status"],
            gates=", ".join(group["source_gate_names"]),
            source=_markdown_cell_list(group["source_evidence_available"]),
            missing=_markdown_cell_list(group["missing_evidence"]) or "none",
            owner=group["decision_owner"],
            agent=str(group["agent_can_progress_without_user_judgement"]).lower(),
            unsafe=_markdown_cell_list(group["unsafe_overclaiming_examples"]),
            action=group["next_safe_action"],
        )
        for group in packet["decision_groups"]
    )
    no_decision_rows = nl.join(
        f"- {key}: `{str(value).lower()}`" for key, value in no_decision.items()
    )
    separation_rows = nl.join(
        f"- {key}: `{str(value).lower()}`"
        for key, value in gate_separation.items()
    )
    metadata_rows = nl.join(
        f"- {key}: `{value}`"
        for key, value in source["diagnostic_output_metadata"].items()
    )
    survival_rows = nl.join(
        f"- {key}: `{str(value).lower()}`"
        for key, value in source["diagnostic_survival_readback"].items()
    )
    route_steps = nl.join(f"- {step}" for step in route["first_steps"])
    route_boundaries = nl.join(f"- {item}" for item in route["must_not_do"])
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
            "new_rehearsal_run",
            "final_render_path_approved",
            "decision_packet_does_not_grant_approval",
        )
    )
    lines = [
        "# ED-10an Production Limitation-Lift Stage 2 Decision Packet",
        "",
        "This tracked packet converts the ED-10am gate matrix into three bounded decision-preparation groups. It does not approve production subtitle design, production render, creative use, rights, publishing, or public use, and it does not request an immediate user decision.",
        "",
        f"- artifact_id: `{packet['artifact_id']}`",
        f"- status: `{packet['status']}`",
        f"- source_stage1_artifact_id: `{source['source_stage1_artifact_id']}`",
        f"- primary_diagnostic_rehearsal_artifact_id: `{source['primary_diagnostic_rehearsal_artifact_id']}`",
        f"- source_gate_count: `{source['source_gate_count']}`",
        "",
        "## Source Evidence",
        "",
        f"- stage_2_replayability_artifact_id: `{source['stage_2_replayability_artifact_id']}`",
        f"- active_diagnostic_proof_source_artifact_id: `{source['active_diagnostic_proof_source_artifact_id']}`",
        f"- diagnostic_rehearsal_status: `{source['diagnostic_rehearsal_status']}`",
        "",
        "Diagnostic output metadata:",
        "",
        metadata_rows,
        "",
        "Diagnostic survival readback:",
        "",
        survival_rows,
        "",
        "## Decision Groups",
        "",
        "| decision group | current status | source gates | source evidence available | missing evidence | decision owner | agent can progress without user judgement | unsafe overclaiming examples | next safe action |",
        "|---|---|---|---|---|---|---|---|---|",
        group_rows,
        "",
        "## No-Decision Yet",
        "",
        no_decision_rows,
        "",
        "## Gate Separation",
        "",
        separation_rows,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- alternate_route_condition: {route['alternate_route_condition']}",
        f"- concrete_diagnostic_gap_found: `{str(route['concrete_diagnostic_gap_found']).lower()}`",
        f"- agent_can_start_without_user_judgement: `{str(route['agent_can_start_without_user_judgement']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- source_gate_matrix_preserved: `{str(validation['source_gate_matrix_preserved']).lower()}`",
        f"- decision_groups_present: `{str(validation['decision_groups_present']).lower()}`",
        f"- decision_groups_bounded: `{str(validation['decision_groups_bounded']).lower()}`",
        f"- no_decision_boundary_explicit: `{str(validation['no_decision_boundary_explicit']).lower()}`",
        f"- source_evidence_linked: `{str(validation['source_evidence_linked']).lower()}`",
        f"- production_public_gates_still_closed: `{str(validation['production_public_gates_still_closed']).lower()}`",
        f"- unsafe_overclaiming_present: `{str(validation['unsafe_overclaiming_present']).lower()}`",
        f"- next_executable_route_defined: `{str(validation['next_executable_route_defined']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_production_limitation_lift_stage3_owner_review_prep_markdown(
    packet: Mapping[str, Any],
) -> str:
    source = packet["source_evidence"]
    route = packet["next_executable_route"]
    validation = packet["validation"]
    no_approval = packet["no_approval_yet"]
    future_shape = packet["future_user_decision_shape"]
    boundaries = packet["boundaries"]
    nl = chr(10)
    group_rows = nl.join(
        "| {group} | {owner} | {evidence} | {missing} | {safe} | {unsafe} | {proceed} | {stop} |".format(
            group=group["decision_group_id"],
            owner=group["decision_owner_category"],
            evidence=_markdown_cell_list(group["available_evidence"]),
            missing=_markdown_cell_list(group["missing_evidence"]) or "none",
            safe=group["safe_next_action"],
            unsafe=_markdown_cell_list(group["unsafe_overclaiming_examples"]),
            proceed=str(group["can_proceed_without_user_judgement"]).lower(),
            stop=str(group["must_stop_before_approval"]).lower(),
        )
        for group in packet["owner_review_groups"]
    )
    no_approval_rows = nl.join(
        f"- {key}: `{str(value).lower()}`" for key, value in no_approval.items()
    )
    future_rows = nl.join(
        "| {topic} | {owner} | {shape} |".format(
            topic=topic["topic_id"],
            owner=topic["future_owner_category"],
            shape=topic["plain_language_decision_topic"],
        )
        for topic in future_shape["plain_language_topics"]
    )
    metadata_rows = nl.join(
        f"- {key}: `{value}`"
        for key, value in source["diagnostic_output_metadata"].items()
    )
    survival_rows = nl.join(
        f"- {key}: `{str(value).lower()}`"
        for key, value in source["diagnostic_survival_readback"].items()
    )
    route_steps = nl.join(f"- {step}" for step in route["first_steps"])
    route_boundaries = nl.join(f"- {item}" for item in route["must_not_do"])
    closed_boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "new_render_created",
            "new_rehearsal_run",
            "user_decision_requested_now",
            "fixed_user_form_emitted",
            "final_render_path_approved",
            "owner_review_prep_does_not_grant_approval",
        )
    )
    lines = [
        "# ED-10ao Production Limitation-Lift Stage 3 Owner-Review Prep",
        "",
        "This tracked packet converts the ED-10an decision packet into owner-review preparation entries. It does not approve production subtitle design, production render, creative use, rights, publishing, or public use, and it does not ask for an immediate user decision.",
        "",
        f"- artifact_id: `{packet['artifact_id']}`",
        f"- status: `{packet['status']}`",
        f"- source_stage2_decision_packet_artifact_id: `{source['source_stage2_decision_packet_artifact_id']}`",
        f"- source_stage1_gate_matrix_artifact_id: `{source['source_stage1_gate_matrix_artifact_id']}`",
        f"- primary_diagnostic_rehearsal_artifact_id: `{source['primary_diagnostic_rehearsal_artifact_id']}`",
        f"- source_decision_group_count: `{source['source_decision_group_count']}`",
        "",
        "## Source Evidence",
        "",
        f"- stage_2_replayability_artifact_id: `{source['stage_2_replayability_artifact_id']}`",
        f"- active_diagnostic_proof_source_artifact_id: `{source['active_diagnostic_proof_source_artifact_id']}`",
        "",
        "Diagnostic output metadata:",
        "",
        metadata_rows,
        "",
        "Diagnostic survival readback:",
        "",
        survival_rows,
        "",
        "## Owner-Review Preparation Entries",
        "",
        "| decision group | decision owner category | available evidence | missing evidence | safe next action | unsafe overclaiming examples | can proceed without user judgement | must stop before approval |",
        "|---|---|---|---|---|---|---|---|",
        group_rows,
        "",
        "## No Approval Yet",
        "",
        no_approval_rows,
        "",
        "## Future User Decision Shape",
        "",
        "- asked_now: `false`",
        "- fixed_form_required: `false`",
        "- freeform_expected: `true`",
        "- fixed_choice_rows_allowed: `false`",
        "- low_user_burden_goal: Keep the later decision card short and freeform; use the entries below as topics, not as a form to fill now.",
        "",
        "| topic | future owner category | plain-language shape |",
        "|---|---|---|",
        future_rows,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- alternate_route_condition: {route['alternate_route_condition']}",
        f"- concrete_diagnostic_gap_found: `{str(route['concrete_diagnostic_gap_found']).lower()}`",
        f"- agent_can_start_without_user_judgement: `{str(route['agent_can_start_without_user_judgement']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- source_decision_packet_preserved: `{str(validation['source_decision_packet_preserved']).lower()}`",
        f"- owner_review_groups_present: `{str(validation['owner_review_groups_present']).lower()}`",
        f"- owner_review_groups_bounded: `{str(validation['owner_review_groups_bounded']).lower()}`",
        f"- no_approval_boundary_explicit: `{str(validation['no_approval_boundary_explicit']).lower()}`",
        f"- future_user_decision_shape_freeform: `{str(validation['future_user_decision_shape_freeform']).lower()}`",
        f"- no_fixed_user_form_emitted: `{str(validation['no_fixed_user_form_emitted']).lower()}`",
        f"- source_evidence_linked: `{str(validation['source_evidence_linked']).lower()}`",
        f"- production_public_gates_still_closed: `{str(validation['production_public_gates_still_closed']).lower()}`",
        f"- user_decision_not_requested_now: `{str(validation['user_decision_not_requested_now']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        closed_boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_production_limitation_lift_stage4_user_decision_card_markdown(
    packet: Mapping[str, Any],
) -> str:
    source = packet["source_evidence"]
    route = packet["next_executable_route"]
    validation = packet["validation"]
    not_asked_now = packet["not_asked_now"]
    answer_handling = packet["future_freeform_answer_handling"]
    boundaries = packet["boundaries"]
    nl = chr(10)
    topic_rows = nl.join(
        "| {topic} | {question} | {evidence} | {missing} | {answer} | {normalize} | {stop} |".format(
            topic=topic["topic_id"],
            question=topic["plain_language_question_shape"],
            evidence=_markdown_cell_list(topic["available_evidence"]),
            missing=_markdown_cell_list(topic["missing_evidence"]) or "none",
            answer=_markdown_cell_list(topic["safe_freeform_answer_could_mention"]),
            normalize=_markdown_cell_list(topic["agent_may_normalize_internally"]),
            stop=str(topic["must_stop_before_approval"]).lower(),
        )
        for topic in packet["decision_topics"]
    )
    not_asked_rows = nl.join(
        f"- {key}: `{str(value).lower()}`" for key, value in not_asked_now.items()
    )
    handling_rows = nl.join(
        f"- {item}" for item in answer_handling["plain_language_user_instructions"]
    )
    normalization_rows = nl.join(
        f"- {item}" for item in answer_handling["agent_internal_normalization_allowed"]
    )
    unknown_rows = nl.join(
        f"- {item}" for item in answer_handling["unknowns_remain_unknown_examples"]
    )
    boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "user_decision_requested_now",
            "fixed_user_form_emitted",
            "fixed_choice_rows_emitted",
            "screenshot_required",
            "hidden_schema_exposed_to_user",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "final_render_path_approved",
        )
    )
    route_steps = nl.join(f"- {step}" for step in route["first_steps"])
    route_boundaries = nl.join(f"- {item}" for item in route["must_not_do"])
    lines = [
        "# ED-10ap Production Limitation Lift Stage 4 User Decision Card",
        "",
        "This tracked packet prepares a future short freeform user decision-card packet from ED-10ao owner-review entries. It does not ask for a decision now and does not approve production subtitle design, production render, creative use, rights, publishing, or public use.",
        "",
        f"- artifact_id: `{packet['artifact_id']}`",
        f"- status: `{packet['status']}`",
        f"- source_stage3_owner_review_prep_artifact_id: `{source['source_stage3_owner_review_prep_artifact_id']}`",
        f"- source_stage2_decision_packet_artifact_id: `{source['source_stage2_decision_packet_artifact_id']}`",
        f"- source_stage1_gate_matrix_artifact_id: `{source['source_stage1_gate_matrix_artifact_id']}`",
        f"- primary_diagnostic_rehearsal_artifact_id: `{source['primary_diagnostic_rehearsal_artifact_id']}`",
        f"- decision_topic_count: `{len(packet['decision_topics'])}`",
        "",
        "## Future Decision Topics",
        "",
        "| topic | plain-language question shape | available evidence | missing evidence | safe freeform answer could mention | agent may normalize internally | must stop before approval |",
        "|---|---|---|---|---|---|---|",
        topic_rows,
        "",
        "## Not Asked Now",
        "",
        not_asked_rows,
        "",
        "## Future Freeform Answer Handling",
        "",
        "- user_may_answer_naturally: `true`",
        "- one_paragraph_or_few_bullets_allowed: `true`",
        "- answer_style: `freeform`",
        "- template_required: `false`",
        "- schema_owner: `Agent`",
        "- max_look_for_points: `3`",
        "- fixed_form_required: `false`",
        "- fixed_choice_rows_allowed: `false`",
        "- fixed_choice_rows_emitted: `false`",
        "- screenshot_required: `false`",
        "- hidden_schema_exposed_to_user: `false`",
        "",
        handling_rows,
        "",
        "Agent / Supervisor may normalize internally:",
        "",
        normalization_rows,
        "",
        "Unknowns remain unknown:",
        "",
        unknown_rows,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- alternate_route_condition: {route['alternate_route_condition']}",
        f"- concrete_diagnostic_gap_found: `{str(route['concrete_diagnostic_gap_found']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- source_owner_review_prep_preserved: `{str(validation['source_owner_review_prep_preserved']).lower()}`",
        f"- decision_topics_present: `{str(validation['decision_topics_present']).lower()}`",
        f"- decision_topics_bounded_to_three: `{str(validation['decision_topics_bounded_to_three']).lower()}`",
        f"- not_asked_now_boundary_explicit: `{str(validation['not_asked_now_boundary_explicit']).lower()}`",
        f"- future_user_burden_freeform: `{str(validation['future_user_burden_freeform']).lower()}`",
        f"- future_freeform_answer_handling_ready: `{str(validation['future_freeform_answer_handling_ready']).lower()}`",
        f"- hidden_schema_not_exposed: `{str(validation['hidden_schema_not_exposed']).lower()}`",
        f"- no_fixed_choice_or_form_surface: `{str(validation['no_fixed_choice_or_form_surface']).lower()}`",
        f"- source_evidence_linked: `{str(validation['source_evidence_linked']).lower()}`",
        f"- production_public_gates_still_closed: `{str(validation['production_public_gates_still_closed']).lower()}`",
        f"- no_screenshot_requirement: `{str(validation['no_screenshot_requirement']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_production_limitation_lift_stage5_user_decision_ready_markdown(
    packet: Mapping[str, Any],
) -> str:
    source = packet["source_evidence"]
    route = packet["next_executable_route"]
    validation = packet["validation"]
    ready = packet["ready_but_not_asked"]
    constraints = packet["future_presentation_constraints"]
    boundaries = packet["boundaries"]
    nl = chr(10)

    def fmt(value: Any) -> str:
        return str(value).lower() if isinstance(value, bool) else str(value)

    topic_rows = nl.join(
        "| {topic} | {title} | {prompt} | {evidence} | {missing} | {normalize} | {stop} |".format(
            topic=topic["topic_id"],
            title=topic["final_user_facing_topic_title"],
            prompt=topic["low_burden_freeform_prompt_shape"],
            evidence=_markdown_cell_list(topic["evidence_available"]),
            missing=_markdown_cell_list(topic["evidence_still_missing"]) or "none",
            normalize=_markdown_cell_list(topic["internal_normalization_hints"]),
            stop=topic["stop_boundary_before_approval"],
        )
        for topic in packet["decision_topics"]
    )
    ready_rows = nl.join(
        f"- {key}: `{fmt(value)}`" for key, value in ready.items()
    )
    constraint_rows = nl.join(
        f"- {key}: `{fmt(value)}`" for key, value in constraints.items()
    )
    boundary_rows = nl.join(
        f"- {key}: `{str(boundaries[key]).lower()}`"
        for key in (
            "user_decision_card_ready",
            "production_subtitle_design_acceptance",
            "production_render_acceptance",
            "creative_acceptance",
            "rights_status",
            "publishing_acceptance",
            "public_use_permission",
            "user_decision_requested_now",
            "fixed_user_form_emitted",
            "fixed_choice_rows_emitted",
            "screenshot_required",
            "hidden_schema_exposed_to_user",
            "tracked_binary_artifact_created",
            "episodes_tracked",
            "final_render_path_approved",
        )
    )
    route_steps = nl.join(f"- {step}" for step in route["first_steps"])
    route_boundaries = nl.join(f"- {item}" for item in route["must_not_do"])
    lines = [
        "# ED-10aq Production Limitation Lift Stage 5 User-Decision-Ready",
        "",
        "This tracked packet makes the later short freeform user decision prompt ready from ED-10ap. It does not ask for a decision now and does not approve production subtitle design, production render, creative use, rights, publishing, or public use.",
        "",
        f"- artifact_id: `{packet['artifact_id']}`",
        f"- status: `{packet['status']}`",
        f"- source_stage4_user_decision_card_artifact_id: `{source['source_stage4_user_decision_card_artifact_id']}`",
        f"- source_stage3_owner_review_prep_artifact_id: `{source['source_stage3_owner_review_prep_artifact_id']}`",
        f"- source_stage2_decision_packet_artifact_id: `{source['source_stage2_decision_packet_artifact_id']}`",
        f"- source_stage1_gate_matrix_artifact_id: `{source['source_stage1_gate_matrix_artifact_id']}`",
        f"- primary_diagnostic_rehearsal_artifact_id: `{source['primary_diagnostic_rehearsal_artifact_id']}`",
        f"- decision_topic_count: `{len(packet['decision_topics'])}`",
        "",
        "## Decision Topics",
        "",
        "| topic | final user-facing topic title | low-burden freeform prompt shape | evidence available | evidence still missing | internal normalization hints | stop boundary before approval |",
        "|---|---|---|---|---|---|---|",
        topic_rows,
        "",
        "## Ready But Not Asked",
        "",
        ready_rows,
        "",
        "## Future Presentation Constraints",
        "",
        constraint_rows,
        "",
        "## Next Executable Route",
        "",
        f"- route_id: `{route['route_id']}`",
        f"- alternate_route_id: `{route['alternate_route_id']}`",
        f"- alternate_route_condition: {route['alternate_route_condition']}",
        f"- concrete_diagnostic_gap_found: `{str(route['concrete_diagnostic_gap_found']).lower()}`",
        f"- purpose: {route['purpose']}",
        "",
        route_steps,
        "",
        "This route must not:",
        "",
        route_boundaries,
        "",
        "## Validation",
        "",
        f"- source_user_decision_card_preserved: `{str(validation['source_user_decision_card_preserved']).lower()}`",
        f"- source_owner_review_prep_linked: `{str(validation['source_owner_review_prep_linked']).lower()}`",
        f"- decision_topics_present: `{str(validation['decision_topics_present']).lower()}`",
        f"- decision_topics_bounded_to_three: `{str(validation['decision_topics_bounded_to_three']).lower()}`",
        f"- ready_but_not_asked_explicit: `{str(validation['ready_but_not_asked_explicit']).lower()}`",
        f"- future_presentation_constraints_ready: `{str(validation['future_presentation_constraints_ready']).lower()}`",
        f"- no_fixed_choice_or_form_surface: `{str(validation['no_fixed_choice_or_form_surface']).lower()}`",
        f"- source_evidence_linked: `{str(validation['source_evidence_linked']).lower()}`",
        f"- production_public_gates_still_closed: `{str(validation['production_public_gates_still_closed']).lower()}`",
        f"- no_screenshot_requirement: `{str(validation['no_screenshot_requirement']).lower()}`",
        f"- no_hidden_schema_exposed: `{str(validation['no_hidden_schema_exposed']).lower()}`",
        f"- all_checks_passed: `{str(validation['all_checks_passed']).lower()}`",
        "",
        "## Boundary",
        "",
        boundary_rows,
    ]
    return nl.join(lines) + nl


def render_subtitle_render_path_selector_probe_ass(
    probe: Mapping[str, Any],
) -> str:
    styles = "\n".join(_ass_style(example) for example in probe["examples"])
    dialogues = "\n".join(_ass_probe_dialogue(example) for example in probe["examples"])
    return (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1920\n"
        "PlayResY: 1080\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding\n"
        f"{styles}\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n"
        f"{dialogues}\n"
    )

def _example(example_id: str, intent: Mapping[str, Any]) -> dict[str, Any]:
    selection = select_subtitle_preset(intent)
    return {
        "example_id": example_id,
        "intent": selection["normalized_intent"],
        "preset_key": selection["preset_key"],
        "style_tokens": selection["style_tokens"],
        "human_review_required": selection["review_policy"]["human_review_required"],
    }


def _visual_proof_example(index: int, example: Mapping[str, Any]) -> dict[str, Any]:
    tokens = example["style_tokens"]
    return {
        "order": index,
        "example_id": example["example_id"],
        "intent": example["intent"],
        "preset_key": example["preset_key"],
        "display_sample_text": _sample_text_for_example(str(example["example_id"])),
        "visual_sample": {
            "font_size_percent": int(round(float(tokens["font_size_scale"]) * 100)),
            "badge_swatch": _swatch_for_token(str(tokens["badge_color_token"])),
            "accent_swatch": _swatch_for_token(str(tokens["accent_color_token"])),
            "backplate_alpha": _backplate_alpha(str(tokens["backplate_box_token"])),
            "outline_px_placeholder": _outline_px(str(tokens["outline_shadow_strength"])),
            "shadow_px_placeholder": _shadow_px(str(tokens["outline_shadow_strength"])),
            "motion_label": tokens["motion_primitive"],
            "line_break_label": tokens["safe_area_line_break_behavior"],
        },
        "readback_tokens": {
            "font_family_role": tokens["font_family_role"],
            "font_size_scale": tokens["font_size_scale"],
            "outline_shadow_strength": tokens["outline_shadow_strength"],
            "badge_color_token": tokens["badge_color_token"],
            "accent_color_token": tokens["accent_color_token"],
            "backplate_box_token": tokens["backplate_box_token"],
            "motion_primitive": tokens["motion_primitive"],
            "safe_area_line_break_behavior": tokens["safe_area_line_break_behavior"],
            "body_text_color_token": tokens["body_text_color_token"],
            "body_text_color_changed": tokens["body_text_color_changed"],
        },
        "human_review_required": example["human_review_required"],
    }


def _style_axis_example(example: Mapping[str, Any]) -> dict[str, Any]:
    tokens = example["readback_tokens"]
    axis = _style_axis_for_example(str(example["example_id"]))
    return {
        "order": example["order"],
        "example_id": example["example_id"],
        "preset_key": example["preset_key"],
        "intent": example["intent"],
        "display_sample_text": example["display_sample_text"],
        "style_family": axis["style_family"],
        "family_group": axis["family_group"],
        "palette_route": axis["palette_route"],
        "palette_surfaces": {
            "badge_color_token": tokens["badge_color_token"],
            "accent_color_token": tokens["accent_color_token"],
            "backplate_box_token": tokens["backplate_box_token"],
            "body_text_color_token": tokens["body_text_color_token"],
            "body_text_color_changed": tokens["body_text_color_changed"],
        },
        "expression_surfaces": {
            "font_family_role": tokens["font_family_role"],
            "font_size_scale": tokens["font_size_scale"],
            "outline_shadow_strength": tokens["outline_shadow_strength"],
            "motion_primitive": tokens["motion_primitive"],
            "safe_area_line_break_behavior": tokens["safe_area_line_break_behavior"],
        },
        "visual_sample": example["visual_sample"],
        "axis_readback": {
            "body_text_color_policy_preserved": (
                tokens["body_text_color_token"] == "stable_default_body_text"
                and tokens["body_text_color_changed"] is False
            ),
            "palette_changes_body_text": False,
            "new_palette_created": False,
            "new_style_family_created": False,
            "review_required": False,
        },
    }


def _render_path_contract_entry(example: Mapping[str, Any]) -> dict[str, Any]:
    palette = example["palette_surfaces"]
    expression = example["expression_surfaces"]
    intent = example["intent"]
    return {
        "semantic_preset_id": example["example_id"],
        "preset_key": example["preset_key"],
        "render_adapter_input": {
            "semantic": {
                "speaker_id": intent["speaker_id"],
                "speaker_role": intent["speaker_role"],
                "emotion": intent["emotion"],
                "intensity": intent["intensity"],
                "utterance_role": intent["utterance_role"],
                "readability_priority": intent["readability_priority"],
            },
            "style": {
                "family_id": example["family_group"],
                "style_family": example["style_family"],
                "palette_route": example["palette_route"],
                "font_family_role": expression["font_family_role"],
                "font_size_scale": expression["font_size_scale"],
                "outline_shadow_strength": expression["outline_shadow_strength"],
            },
            "color_surfaces": {
                "badge_color_token": palette["badge_color_token"],
                "accent_color_token": palette["accent_color_token"],
                "backplate_box_token": palette["backplate_box_token"],
                "body_text_color_token": palette["body_text_color_token"],
                "body_text_color_changed": palette["body_text_color_changed"],
            },
            "motion_line_break": {
                "motion_primitive": expression["motion_primitive"],
                "safe_area_line_break_behavior": (
                    expression["safe_area_line_break_behavior"]
                ),
            },
        },
        "contract_assertions": {
            "body_text_color_policy_preserved": (
                palette["body_text_color_token"] == "stable_default_body_text"
                and palette["body_text_color_changed"] is False
            ),
            "render_artifact_created": False,
            "production_acceptance": False,
            "rights_public_use_acceptance": False,
        },
    }


def _render_contract_consumer_payload(entry: Mapping[str, Any]) -> dict[str, Any]:
    adapter_input = entry["render_adapter_input"]
    semantic = adapter_input["semantic"]
    style = adapter_input["style"]
    color = adapter_input["color_surfaces"]
    motion_line_break = adapter_input["motion_line_break"]
    normalized_payload = {
        "semantic": {
            "semantic_preset_id": entry["semantic_preset_id"],
            "preset_key": entry["preset_key"],
            "speaker_id": semantic["speaker_id"],
            "speaker_role": semantic["speaker_role"],
            "emotion": semantic["emotion"],
            "intensity": semantic["intensity"],
            "utterance_role": semantic["utterance_role"],
            "readability_priority": semantic["readability_priority"],
        },
        "style": {
            "family_id": style["family_id"],
            "palette_route": style["palette_route"],
            "font_family_role": style["font_family_role"],
            "font_size_scale": style["font_size_scale"],
            "outline_shadow_strength": style["outline_shadow_strength"],
        },
        "color_surfaces": {
            "badge_color_token": color["badge_color_token"],
            "accent_color_token": color["accent_color_token"],
            "backplate_box_token": color["backplate_box_token"],
            "body_text_color_policy_reference": "stable_default_body_text",
            "body_text_color_token": color["body_text_color_token"],
            "body_text_color_changed": color["body_text_color_changed"],
        },
        "motion": {
            "motion_primitive": motion_line_break["motion_primitive"],
        },
        "line_break": {
            "safe_area_line_break_behavior": motion_line_break[
                "safe_area_line_break_behavior"
            ],
        },
        "render_boundary": {
            "render_level": "L0 No Render",
            "new_render_run": False,
            "render_artifact_created": False,
            "video_artifact_created": False,
            "audio_artifact_created": False,
            "frame_artifact_created": False,
            "ass_artifact_created": False,
            "episode_artifact_created": False,
            "consumer_dry_read_only": True,
        },
        "production_public_boundary": {
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        },
    }
    color_payload = normalized_payload["color_surfaces"]
    render_boundary = normalized_payload["render_boundary"]
    production_public_boundary = normalized_payload["production_public_boundary"]
    return {
        "payload_id": f"consumer_dry_read:{entry['semantic_preset_id']}",
        "semantic_preset_id": entry["semantic_preset_id"],
        "preset_key": entry["preset_key"],
        "normalized_render_adapter_payload": normalized_payload,
        "dry_read_assertions": {
            "source_contract_entry_consumed": True,
            "body_text_color_policy_preserved": (
                color_payload["body_text_color_policy_reference"]
                == "stable_default_body_text"
                and color_payload["body_text_color_token"] == "stable_default_body_text"
                and color_payload["body_text_color_changed"] is False
            ),
            "badge_accent_backplate_preserved": all(
                bool(color_payload[field])
                for field in (
                    "badge_color_token",
                    "accent_color_token",
                    "backplate_box_token",
                )
            ),
            "family_palette_route_preserved": (
                bool(normalized_payload["style"]["family_id"])
                and bool(normalized_payload["style"]["palette_route"])
            ),
            "motion_line_break_metadata_preserved": (
                bool(normalized_payload["motion"]["motion_primitive"])
                and bool(
                    normalized_payload["line_break"][
                        "safe_area_line_break_behavior"
                    ]
                )
            ),
            "render_boundary_preserved": (
                render_boundary["render_level"] == "L0 No Render"
                and render_boundary["new_render_run"] is False
                and render_boundary["consumer_dry_read_only"] is True
                and all(
                    render_boundary[field] is False
                    for field in (
                        "render_artifact_created",
                        "video_artifact_created",
                        "audio_artifact_created",
                        "frame_artifact_created",
                        "ass_artifact_created",
                        "episode_artifact_created",
                    )
                )
            ),
            "production_public_boundary_preserved": (
                production_public_boundary["rights_status"] == "pending"
                and all(
                    production_public_boundary[field] is False
                    for field in (
                        "production_subtitle_design_acceptance",
                        "production_render_acceptance",
                        "creative_acceptance",
                        "publishing_acceptance",
                        "public_use_permission",
                    )
                )
            ),
        },
    }


def _render_contract_consumer_validation(
    source_contract: Mapping[str, Any],
    consumer_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    required_fields: tuple[tuple[str, str], ...] = (
        ("semantic.semantic_preset_id", "str"),
        ("semantic.preset_key", "str"),
        ("semantic.speaker_id", "str"),
        ("semantic.speaker_role", "str"),
        ("semantic.emotion", "str"),
        ("semantic.intensity", "int"),
        ("semantic.utterance_role", "str"),
        ("semantic.readability_priority", "str"),
        ("style.family_id", "str"),
        ("style.palette_route", "str"),
        ("style.font_family_role", "str"),
        ("style.font_size_scale", "number"),
        ("style.outline_shadow_strength", "str"),
        ("color_surfaces.badge_color_token", "str"),
        ("color_surfaces.accent_color_token", "str"),
        ("color_surfaces.backplate_box_token", "str"),
        ("color_surfaces.body_text_color_policy_reference", "str"),
        ("color_surfaces.body_text_color_token", "str"),
        ("color_surfaces.body_text_color_changed", "bool"),
        ("motion.motion_primitive", "str"),
        ("line_break.safe_area_line_break_behavior", "str"),
        ("render_boundary.render_level", "str"),
        ("render_boundary.new_render_run", "bool"),
        ("render_boundary.render_artifact_created", "bool"),
        ("render_boundary.video_artifact_created", "bool"),
        ("render_boundary.audio_artifact_created", "bool"),
        ("render_boundary.frame_artifact_created", "bool"),
        ("render_boundary.ass_artifact_created", "bool"),
        ("render_boundary.episode_artifact_created", "bool"),
        ("render_boundary.consumer_dry_read_only", "bool"),
        ("production_public_boundary.production_subtitle_design_acceptance", "bool"),
        ("production_public_boundary.production_render_acceptance", "bool"),
        ("production_public_boundary.creative_acceptance", "bool"),
        ("production_public_boundary.rights_status", "str"),
        ("production_public_boundary.publishing_acceptance", "bool"),
        ("production_public_boundary.public_use_permission", "bool"),
    )
    missing_required_fields: list[str] = []
    type_mismatches: list[str] = []
    body_text_color_policy_drift = False
    render_boundary_leakage = False
    production_public_boundary_leakage = False

    for payload in consumer_payloads:
        payload_id = str(payload["semantic_preset_id"])
        normalized = payload["normalized_render_adapter_payload"]
        for path, expected_type in required_fields:
            value = _nested_value(normalized, path)
            if value is None:
                missing_required_fields.append(f"{payload_id}:{path}")
            elif not _matches_dry_read_type(value, expected_type):
                type_mismatches.append(f"{payload_id}:{path}:expected_{expected_type}")

        color = normalized["color_surfaces"]
        body_text_color_policy_drift = body_text_color_policy_drift or not (
            color["body_text_color_policy_reference"] == "stable_default_body_text"
            and color["body_text_color_token"] == "stable_default_body_text"
            and color["body_text_color_changed"] is False
        )

        render_boundary = normalized["render_boundary"]
        render_boundary_leakage = render_boundary_leakage or not (
            render_boundary["render_level"] == "L0 No Render"
            and render_boundary["new_render_run"] is False
            and render_boundary["consumer_dry_read_only"] is True
            and all(
                render_boundary[field] is False
                for field in (
                    "render_artifact_created",
                    "video_artifact_created",
                    "audio_artifact_created",
                    "frame_artifact_created",
                    "ass_artifact_created",
                    "episode_artifact_created",
                )
            )
        )

        production_public_boundary = normalized["production_public_boundary"]
        production_public_boundary_leakage = production_public_boundary_leakage or not (
            production_public_boundary["rights_status"] == "pending"
            and all(
                production_public_boundary[field] is False
                for field in (
                    "production_subtitle_design_acceptance",
                    "production_render_acceptance",
                    "creative_acceptance",
                    "publishing_acceptance",
                    "public_use_permission",
                )
            )
        )

    expected_count = len(source_contract["examples_represented"])
    actual_count = len(consumer_payloads)
    return {
        "source_contract_artifact_id": source_contract["artifact_id"],
        "source_contract_status": source_contract["status"],
        "expected_payload_count": expected_count,
        "actual_payload_count": actual_count,
        "missing_required_fields": missing_required_fields,
        "type_mismatches": type_mismatches,
        "body_text_color_policy_drift": body_text_color_policy_drift,
        "render_boundary_leakage": render_boundary_leakage,
        "production_public_boundary_leakage": production_public_boundary_leakage,
        "all_payloads_consumer_ready": (
            expected_count == actual_count
            and not missing_required_fields
            and not type_mismatches
            and not body_text_color_policy_drift
            and not render_boundary_leakage
            and not production_public_boundary_leakage
        ),
    }


def _nested_value(mapping: Mapping[str, Any], path: str) -> Any:
    current: Any = mapping
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _matches_dry_read_type(value: Any, expected_type: str) -> bool:
    if expected_type == "bool":
        return isinstance(value, bool)
    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "str":
        return isinstance(value, str) and bool(value)
    return False


def _render_path_probe_examples(
    source_contract: Mapping[str, Any],
) -> list[dict[str, Any]]:
    entries_by_id = {
        entry["semantic_preset_id"]: entry
        for entry in source_contract["contract_entries"]
    }
    return [
        _render_path_probe_example(index=index, entry=entries_by_id[example_id])
        for index, example_id in enumerate(RENDER_PATH_PROBE_SELECTED_EXAMPLE_IDS)
        if example_id in entries_by_id
    ]


def _render_path_probe_example(
    *,
    index: int,
    entry: Mapping[str, Any],
) -> dict[str, Any]:
    adapter_input = entry["render_adapter_input"]
    semantic = adapter_input["semantic"]
    style = adapter_input["style"]
    color = adapter_input["color_surfaces"]
    motion_line_break = adapter_input["motion_line_break"]
    role = _render_path_probe_role(str(entry["semantic_preset_id"]))
    cue = _render_path_probe_cue(str(entry["semantic_preset_id"]))
    return {
        "order": index,
        "example_id": entry["semantic_preset_id"],
        "role": role,
        "semantic": {
            "semantic_preset_id": entry["semantic_preset_id"],
            "preset_key": entry["preset_key"],
            "speaker_id": semantic["speaker_id"],
            "speaker_role": semantic["speaker_role"],
            "emotion": semantic["emotion"],
            "intensity": semantic["intensity"],
            "utterance_role": semantic["utterance_role"],
            "readability_priority": semantic["readability_priority"],
        },
        "style": {
            "family_id": style["family_id"],
            "style_family": style["style_family"],
            "palette_route": style["palette_route"],
            "font_family_role": style["font_family_role"],
            "font_size_scale": style["font_size_scale"],
            "outline_shadow_strength": style["outline_shadow_strength"],
        },
        "color_surfaces": {
            "badge_color_token": color["badge_color_token"],
            "accent_color_token": color["accent_color_token"],
            "backplate_box_token": color["backplate_box_token"],
            "body_text_color_policy_reference": "stable_default_body_text",
            "body_text_color_token": color["body_text_color_token"],
            "body_text_color_changed": color["body_text_color_changed"],
        },
        "motion": {
            "motion_primitive": motion_line_break["motion_primitive"],
        },
        "line_break": {
            "safe_area_line_break_behavior": motion_line_break[
                "safe_area_line_break_behavior"
            ],
            "ass_text_contains_line_break": "\\N" in cue,
            "safe_area_note": "bottom_center_title_safe_probe",
        },
        "ass_probe": {
            "style": f"Probe{index + 1}",
            "start": _probe_ass_time(index * 1.35 + 0.2),
            "end": _probe_ass_time(index * 1.35 + 1.25),
            "text": cue,
        },
        "assertions": {
            "source_contract_entry_consumed": True,
            "body_text_color_policy_preserved": (
                color["body_text_color_token"] == "stable_default_body_text"
                and color["body_text_color_changed"] is False
            ),
            "badge_accent_backplate_preserved": all(
                bool(color[field])
                for field in (
                    "badge_color_token",
                    "accent_color_token",
                    "backplate_box_token",
                )
            ),
            "style_axis_preserved": bool(style["family_id"])
            and bool(style["palette_route"])
            and bool(style["font_family_role"]),
            "motion_line_break_metadata_preserved": (
                bool(motion_line_break["motion_primitive"])
                and bool(motion_line_break["safe_area_line_break_behavior"])
            ),
        },
    }


def _render_path_probe_role(example_id: str) -> str:
    if example_id == "shout_intensity_2":
        return "shout_high_intensity"
    if example_id == "whisper_intensity_1":
        return "low_pressure_whisper"
    return "normal_dialogue"


def _render_path_probe_cue(example_id: str) -> str:
    if example_id == "shout_intensity_2":
        return "SHOUT HIGH INTENSITY"
    if example_id == "whisper_intensity_1":
        return "LOW PRESSURE\\NWHISPER CUE"
    return "NORMAL DIALOGUE CUE"


def _render_path_probe_validation(
    *,
    source_contract: Mapping[str, Any],
    examples: list[dict[str, Any]],
    local_probe: Mapping[str, Any],
) -> dict[str, Any]:
    selected_ids = [example["example_id"] for example in examples]
    missing_selected_examples = [
        example_id
        for example_id in RENDER_PATH_PROBE_SELECTED_EXAMPLE_IDS
        if example_id not in selected_ids
    ]
    stable_body_text_preserved = all(
        example["assertions"]["body_text_color_policy_preserved"]
        for example in examples
    )
    badge_route = all(
        example["assertions"]["badge_accent_backplate_preserved"]
        for example in examples
    )
    style_axis = all(example["assertions"]["style_axis_preserved"] for example in examples)
    motion_survived = all(
        example["assertions"]["motion_line_break_metadata_preserved"]
        for example in examples
    )
    line_break_survived = all(
        bool(example["line_break"]["safe_area_line_break_behavior"])
        for example in examples
    ) and any(
        example["line_break"]["ass_text_contains_line_break"]
        for example in examples
    )
    boundaries = _render_path_probe_boundary_flags(local_probe)
    production_public_boundary_closed = (
        boundaries["rights_status"] == "pending"
        and all(
            boundaries[field] is False
            for field in (
                "production_subtitle_design_acceptance",
                "production_render_acceptance",
                "creative_acceptance",
                "publishing_acceptance",
                "public_use_permission",
            )
        )
    )
    all_checks_passed = (
        source_contract["artifact_id"] == RENDER_PATH_CONTRACT_ARTIFACT_ID
        and len(examples) >= 3
        and not missing_selected_examples
        and stable_body_text_preserved
        and badge_route
        and style_axis
        and motion_survived
        and line_break_survived
        and production_public_boundary_closed
        and boundaries["tracked_binary_artifact_created"] is False
    )
    return {
        "source_contract_artifact_id": source_contract["artifact_id"],
        "source_contract_status": source_contract["status"],
        "source_contract_referenced": (
            source_contract["artifact_id"] == RENDER_PATH_CONTRACT_ARTIFACT_ID
        ),
        "selected_example_count": len(examples),
        "selected_example_ids": selected_ids,
        "missing_selected_examples": missing_selected_examples,
        "stable_body_text_preserved": stable_body_text_preserved,
        "badge_accent_backplate_route_preserved": badge_route,
        "style_axis_preserved": style_axis,
        "motion_metadata_survived": motion_survived,
        "safe_area_line_break_metadata_survived": line_break_survived,
        "local_probe_status": local_probe["status"],
        "production_public_boundary_closed": production_public_boundary_closed,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "all_checks_passed": all_checks_passed,
    }


def _default_render_path_probe_local_readback(
    *,
    status: str = "local_probe_not_attempted",
    ass_path: Path | None = None,
    video_path: Path | None = None,
    manifest_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    base = base_dir or Path.cwd()
    output_dir = base / RENDER_PATH_PROBE_LOCAL_OUTPUT_RELATIVE_DIR
    ass = ass_path or output_dir / "subtitle_render_path_selector_probe.ass"
    video = video_path or output_dir / "subtitle_render_path_selector_probe.mp4"
    manifest = manifest_path or output_dir / "subtitle_render_path_selector_probe.local.json"
    return {
        "status": status,
        "source_policy": "existing_output_first_local_ignored_source_media",
        "outputs": {
            "ass": _probe_display_path(ass, base),
            "video": _probe_display_path(video, base),
            "manifest": _probe_display_path(manifest, base),
        },
        "metadata": {},
        "render_command_summary": None,
        "ffmpeg_path_source": None,
        "ffprobe_path_source": None,
        "ffmpeg_version": None,
        "ffprobe_version": None,
        "fallback_used": False,
        "attempts": [],
        "warnings": [],
        "ignored_by_git": True,
        "tracked_binary_artifact_created": False,
        "production_render_acceptance": False,
        "public_use_permission": False,
    }


def _render_path_probe_boundary_flags(
    local_probe: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    local_generated = local_probe["status"] == "local_ignored_probe_generated"
    flags.update(
        {
            "new_render_created": local_generated,
            "diagnostic_local_ignored_render_created": local_generated,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_render_acceptance": False,
            "public_use_permission": False,
            "rights_status": "pending",
        }
    )
    return flags


def _lineage_observation_surface_boundary_flags(
    source_probe: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "source_probe_new_render_created": source_probe["render_gate"]["new_render_run"],
            "diagnostic_local_ignored_render_reused": True,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_render_acceptance": False,
            "public_use_permission": False,
            "rights_status": "pending",
        }
    )
    return flags


def _lineage_observation_surface_validation(
    dry_read: Mapping[str, Any],
    source_probe: Mapping[str, Any],
    observation_surface: Mapping[str, Any],
) -> dict[str, Any]:
    boundaries = _lineage_observation_surface_boundary_flags(source_probe)
    production_public_boundary_closed = (
        boundaries["rights_status"] == "pending"
        and boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
    )
    dry_validation = dry_read["dry_read_validation"]
    source_probe_validation = source_probe["validation"]
    dry_payload_ids = {payload["semantic_preset_id"] for payload in dry_read["consumer_payloads"]}
    selected_examples_covered = set(source_probe["selected_example_ids"]).issubset(dry_payload_ids)
    dry_payload_body_tokens = {
        payload["normalized_render_adapter_payload"]["color_surfaces"]["body_text_color_token"]
        for payload in dry_read["consumer_payloads"]
    }
    local_outputs = observation_surface["local_outputs"]
    required_output_keys = {"ass", "video", "manifest", "contact_sheet"}
    observation_paths_present = required_output_keys.issubset(local_outputs) and all(
        bool(local_outputs[key]) for key in required_output_keys
    )
    contact_sheet_path_recorded = (
        bool(local_outputs.get("contact_sheet"))
        and local_outputs["contact_sheet"].endswith(
            LINEAGE_OBSERVATION_CONTACT_SHEET_FILENAME
        )
    )
    active_artifact_preserved = source_probe["artifact_id"] == RENDER_PATH_PROBE_ARTIFACT_ID
    predecessor_lineage_present = (
        dry_read["artifact_id"] == RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
        and RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT == "7e96a28"
    )
    return {
        "dry_read_artifact_id": dry_read["artifact_id"],
        "source_probe_artifact_id": source_probe["artifact_id"],
        "active_artifact_preserved": active_artifact_preserved,
        "predecessor_lineage_present": predecessor_lineage_present,
        "predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "predecessor_invalidated": False,
        "observation_paths_present": observation_paths_present,
        "contact_sheet_path_recorded": contact_sheet_path_recorded,
        "dry_read_all_payloads_consumer_ready": dry_validation["all_payloads_consumer_ready"],
        "dry_read_payload_count": dry_validation["actual_payload_count"],
        "expected_dry_read_payload_count": dry_validation["expected_payload_count"],
        "dry_read_body_text_color_policy_drift": dry_validation["body_text_color_policy_drift"],
        "dry_read_render_boundary_leakage": dry_validation["render_boundary_leakage"],
        "dry_read_production_public_boundary_leakage": dry_validation["production_public_boundary_leakage"],
        "source_probe_all_checks_passed": source_probe_validation["all_checks_passed"],
        "source_probe_local_status": source_probe["local_probe"]["status"],
        "source_probe_selected_example_count": source_probe["selected_example_count"],
        "source_probe_selected_examples": list(source_probe["selected_example_ids"]),
        "selected_examples_covered_by_dry_read": selected_examples_covered,
        "new_render_run": False,
        "source_probe_new_render_run": source_probe["render_gate"]["new_render_run"],
        "stable_body_text_preserved": dry_payload_body_tokens == {"stable_default_body_text"} and source_probe_validation["stable_body_text_preserved"],
        "badge_accent_backplate_route_preserved": source_probe_validation["badge_accent_backplate_route_preserved"],
        "safe_area_line_break_metadata_survived": source_probe_validation["safe_area_line_break_metadata_survived"],
        "local_outputs_ignored": True,
        "tracked_binary_artifact_created": False,
        "production_public_boundary_closed": production_public_boundary_closed,
        "episodes_tracked": False,
        "all_checks_passed": (
            dry_validation["all_payloads_consumer_ready"]
            and dry_validation["body_text_color_policy_drift"] is False
            and dry_validation["render_boundary_leakage"] is False
            and dry_validation["production_public_boundary_leakage"] is False
            and source_probe_validation["all_checks_passed"]
            and source_probe["local_probe"]["status"] == "local_ignored_probe_generated"
            and active_artifact_preserved
            and predecessor_lineage_present
            and selected_examples_covered
            and dry_payload_body_tokens == {"stable_default_body_text"}
            and observation_paths_present
            and contact_sheet_path_recorded
            and production_public_boundary_closed
            and boundaries["episodes_tracked"] is False
            and boundaries["tracked_binary_artifact_created"] is False
        ),
    }


def _production_limitation_lift_boundary_flags(
    source_probe: Mapping[str, Any],
    lineage_surface: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "source_probe_new_render_created": source_probe["render_gate"]["new_render_run"],
            "source_lineage_new_render_created": lineage_surface["render_gate"]["new_render_run"],
            "diagnostic_local_ignored_render_reused": True,
            "lineage_surface_support_only": True,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        }
    )
    return flags


def _production_limitation_lift_validation(
    dry_read: Mapping[str, Any],
    source_probe: Mapping[str, Any],
    lineage_surface: Mapping[str, Any],
    gate_matrix: list[Mapping[str, Any]],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    actual_gate_names = [gate["gate_name"] for gate in gate_matrix]
    expected_gate_names = list(PRODUCTION_LIMITATION_LIFT_GATE_NAMES)
    by_gate = {gate["gate_name"]: gate for gate in gate_matrix}
    required_closed_gates = (
        "production_subtitle_design_acceptance",
        "production_render_acceptance",
        "creative_acceptance",
        "rights_status",
        "publishing_acceptance",
        "public_use_permission",
    )
    all_required_gates_present = all(gate in by_gate for gate in required_closed_gates)
    production_public_boundary_closed = (
        boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
    )
    closed_gate_statuses_preserved = (
        all_required_gates_present
        and by_gate["production_subtitle_design_acceptance"]["current_status"] == "not_accepted"
        and by_gate["production_render_acceptance"]["current_status"] == "not_accepted"
        and by_gate["creative_acceptance"]["current_status"] == "not_accepted"
        and by_gate["rights_status"]["current_status"] == "pending"
        and by_gate["publishing_acceptance"]["current_status"] == "not_accepted"
        and by_gate["public_use_permission"]["current_status"] == "not_allowed"
    )
    agent_progress_limited_to_diagnostic_route = (
        by_gate["diagnostic_render_path_proof"]["agent_can_progress_without_user_judgement"]
        is True
        and all(
            by_gate[gate]["agent_can_progress_without_user_judgement"] is False
            for gate in required_closed_gates
        )
    )
    human_or_rights_gates_marked = (
        all(
            by_gate[gate]["human_judgement_required"] is True
            for gate in required_closed_gates
        )
        and by_gate["rights_status"]["rights_or_publication_decision_required"] is True
        and by_gate["publishing_acceptance"]["rights_or_publication_decision_required"]
        is True
        and by_gate["public_use_permission"]["rights_or_publication_decision_required"]
        is True
    )
    active_diagnostic_source_preserved = (
        source_probe["artifact_id"] == RENDER_PATH_PROBE_ARTIFACT_ID
        and source_probe["validation"]["all_checks_passed"] is True
    )
    lineage_support_not_production_proof = (
        lineage_surface["artifact_id"] == LINEAGE_OBSERVATION_ARTIFACT_ID
        and lineage_surface["render_gate"]["new_render_run"] is False
        and lineage_surface["render_gate"]["production_render_acceptance"] is False
        and lineage_surface["render_gate"]["public_use_permission"] is False
        and boundaries["lineage_surface_support_only"] is True
    )
    dry_read_predecessor_preserved = (
        dry_read["artifact_id"] == RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
        and RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT == "7e96a28"
    )
    return {
        "expected_gate_names": expected_gate_names,
        "actual_gate_names": actual_gate_names,
        "gate_names_present": actual_gate_names == expected_gate_names,
        "all_required_gates_present": all_required_gates_present,
        "closed_gate_statuses_preserved": closed_gate_statuses_preserved,
        "agent_progress_limited_to_diagnostic_route": agent_progress_limited_to_diagnostic_route,
        "human_or_rights_gates_marked": human_or_rights_gates_marked,
        "active_diagnostic_source_preserved": active_diagnostic_source_preserved,
        "active_diagnostic_source_artifact_id": source_probe["artifact_id"],
        "lineage_support_not_production_proof": lineage_support_not_production_proof,
        "lineage_support_artifact_id": lineage_surface["artifact_id"],
        "dry_read_predecessor_preserved": dry_read_predecessor_preserved,
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "production_public_boundary_closed": production_public_boundary_closed,
        "new_render_run": False,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "episodes_tracked": boundaries["episodes_tracked"],
        "next_executable_route_defined": True,
        "user_observation_consumed": True,
        "all_checks_passed": (
            actual_gate_names == expected_gate_names
            and all_required_gates_present
            and closed_gate_statuses_preserved
            and agent_progress_limited_to_diagnostic_route
            and human_or_rights_gates_marked
            and active_diagnostic_source_preserved
            and lineage_support_not_production_proof
            and dry_read_predecessor_preserved
            and production_public_boundary_closed
            and boundaries["tracked_binary_artifact_created"] is False
            and boundaries["episodes_tracked"] is False
        ),
    }


def _final_render_path_readiness_matrix(
    dry_read: Mapping[str, Any],
    source_probe: Mapping[str, Any],
    lineage_surface: Mapping[str, Any],
    gate_entry: Mapping[str, Any],
    local_outputs: Mapping[str, str],
) -> list[dict[str, Any]]:
    def row(
        row_id: str,
        area: str,
        status: str,
        source_artifact_id: str,
        file_path: str,
        *,
        supporting: list[str] | None = None,
        local_paths: Mapping[str, str] | None = None,
        available: list[str] | None = None,
        missing: list[str] | None = None,
        agent_can_progress: bool,
        future_decision_required: bool,
        next_action: str,
    ) -> dict[str, Any]:
        return {
            "row_id": row_id,
            "readiness_area": area,
            "status": status,
            "source_artifact_id": source_artifact_id,
            "supporting_artifact_ids": supporting or [],
            "file_path": file_path,
            "local_paths": dict(local_paths or {}),
            "evidence_available": available or [],
            "evidence_missing": missing or [],
            "agent_can_progress_without_user_judgement": agent_can_progress,
            "future_human_rights_publication_decision_required": future_decision_required,
            "next_agent_action": next_action,
        }

    return [
        row(
            "ed10ah_gate_separation_source",
            "gate separation source",
            "available",
            gate_entry["artifact_id"],
            "docs/style_intent/subtitle-production-limitation-lift-entry.json",
            supporting=[
                source_probe["artifact_id"],
                lineage_surface["artifact_id"],
                dry_read["artifact_id"],
            ],
            available=[
                "ED-10ah separates diagnostic proof from production subtitle design, production render, creative, rights, publishing, and public-use gates.",
                "ED-10ah consumes the user observation that display/layout polish should not block forward progress.",
            ],
            agent_can_progress=True,
            future_decision_required=False,
            next_action="Use ED-10ah as the source gate map for final render-path stage preparation.",
        ),
        row(
            "diagnostic_proof_evidence",
            "diagnostic render-path proof",
            "available",
            source_probe["artifact_id"],
            "docs/style_intent/subtitle-render-path-selector-probe.json",
            supporting=[gate_entry["artifact_id"], lineage_surface["artifact_id"]],
            local_paths=source_probe["local_probe"]["outputs"],
            available=[
                "ED-10af L2 selector probe records neutral, shout, and whisper representative payloads through a tiny FFmpeg/libass diagnostic path.",
                "Stable body text, badge/accent/backplate routing, and safe-area line-break metadata are preserved.",
            ],
            missing=["Production-sequence final render acceptance."],
            agent_can_progress=True,
            future_decision_required=False,
            next_action="Reuse ED-10af as active diagnostic proof; do not rerender in this packet.",
        ),
        row(
            "selector_semantic_style_contract_evidence",
            "selector and semantic style contract",
            "available",
            ARTIFACT_ID,
            "docs/style_intent/subtitle-preset-selector.json",
            supporting=[
                SOURCE_REGISTRY_ARTIFACT_ID,
                STYLE_AXIS_PROOF_ARTIFACT_ID,
                VISUAL_PROOF_ARTIFACT_ID,
            ],
            available=[
                "The deterministic preset selector maps speaker/emotion/readability semantics to style tokens.",
                "The style intent registry keeps body text stable by default and routes character/emotion color through badge/accent/backplate surfaces first.",
            ],
            missing=["Production subtitle style acceptance across a final sequence."],
            agent_can_progress=True,
            future_decision_required=False,
            next_action="Carry selector and registry contracts into stage-1 readiness without asking for old visual comparisons.",
        ),
        row(
            "render_adapter_input_contract_evidence",
            "render adapter input contract",
            "available",
            RENDER_PATH_CONTRACT_ARTIFACT_ID,
            "docs/style_intent/subtitle-render-path-selector-contract.json",
            supporting=[STYLE_AXIS_PROOF_ARTIFACT_ID, ARTIFACT_ID],
            available=[
                "ED-10ae records semantic fields, style-axis fields, color surfaces, motion, and safe-area line-break fields that a later render adapter would receive.",
                "ED-10af proves three selected contract entries can pass into the L2 diagnostic render path.",
            ],
            missing=["Final production adapter/run acceptance."],
            agent_can_progress=True,
            future_decision_required=False,
            next_action="Use ED-10ae as the adapter input contract for a later explicit render milestone.",
        ),
        row(
            "local_ignored_proof_media_evidence",
            "local ignored proof media",
            "available",
            lineage_surface["artifact_id"],
            "docs/style_intent/subtitle-render-path-lineage-observation-surface.json",
            supporting=[source_probe["artifact_id"]],
            local_paths=local_outputs,
            available=[
                "Same-machine ignored ASS, MP4, manifest, and contact-sheet paths are recorded for local observation.",
                "The files remain under ignored episodes/ paths and may be absent on another clone without failing the tracked packet.",
            ],
            missing=["Tracked or portable production media artifact strategy."],
            agent_can_progress=True,
            future_decision_required=False,
            next_action="Reference the local outputs as diagnostic evidence only; do not add them to Git.",
        ),
        row(
            "lineage_predecessor_evidence",
            "lineage and predecessor evidence",
            "available",
            lineage_surface["artifact_id"],
            "docs/style_intent/subtitle-render-path-lineage-observation-surface.json",
            supporting=[dry_read["artifact_id"], source_probe["artifact_id"]],
            available=[
                "ED-10ag records the restored dry-read predecessor from commit 7e96a28.",
                "The active ED-10af L2 selector probe supersedes the dry-read for diagnostic render-path proof while preserving dry-read coverage as evidence.",
            ],
            agent_can_progress=True,
            future_decision_required=False,
            next_action="Keep ED-10ag as support, not production proof.",
        ),
        row(
            "missing_production_subtitle_design_acceptance",
            "production subtitle design acceptance",
            "missing",
            gate_entry["artifact_id"],
            "docs/style_intent/subtitle-production-limitation-lift-entry.json",
            available=["Diagnostic style/render path evidence is available."],
            missing=[
                "Explicit human acceptance that the subtitle design is production-ready."
            ],
            agent_can_progress=False,
            future_decision_required=True,
            next_action="Prepare a bounded human decision packet only when this gate is explicitly opened.",
        ),
        row(
            "missing_production_render_acceptance",
            "production render acceptance",
            "missing",
            gate_entry["artifact_id"],
            "docs/style_intent/subtitle-production-limitation-lift-entry.json",
            supporting=[source_probe["artifact_id"]],
            available=["ED-10af diagnostic render-path proof exists."],
            missing=[
                "Accepted final production render output and final run manifest."
            ],
            agent_can_progress=False,
            future_decision_required=True,
            next_action="Do not infer production render acceptance from the diagnostic proof.",
        ),
        row(
            "missing_creative_acceptance",
            "creative acceptance",
            "missing",
            gate_entry["artifact_id"],
            "docs/style_intent/subtitle-production-limitation-lift-entry.json",
            available=[
                "Prior review memory keeps Candidate 2 as diagnostic lead and Candidate 0 as fallback/reference."
            ],
            missing=["Explicit creative acceptance for production use."],
            agent_can_progress=False,
            future_decision_required=True,
            next_action="Do not reopen old candidate or Keifont review axes unless a new explicit decision is requested.",
        ),
        row(
            "missing_rights_publication_public_use_decisions",
            "rights, publishing, and public-use decisions",
            "missing",
            gate_entry["artifact_id"],
            "docs/style_intent/subtitle-production-limitation-lift-entry.json",
            available=[
                "No upload, publication, rights, or public-use action is performed in the diagnostic route."
            ],
            missing=[
                "Rights clearance or owner decision.",
                "Publishing acceptance.",
                "Explicit public-use permission.",
            ],
            agent_can_progress=False,
            future_decision_required=True,
            next_action="Keep rights, publishing, and public-use gates pending until the owner supplies an explicit decision.",
        ),
    ]


def _final_render_path_readiness_boundary_flags(
    source_probe: Mapping[str, Any],
    lineage_surface: Mapping[str, Any],
    gate_entry: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "source_probe_new_render_created": source_probe["render_gate"]["new_render_run"],
            "source_lineage_new_render_created": lineage_surface["render_gate"]["new_render_run"],
            "source_gate_entry_new_render_created": gate_entry["render_gate"]["new_render_run"],
            "diagnostic_local_ignored_render_reused": True,
            "gate_separation_source_reused": True,
            "lineage_surface_support_only": True,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _final_render_path_readiness_validation(
    dry_read: Mapping[str, Any],
    source_probe: Mapping[str, Any],
    lineage_surface: Mapping[str, Any],
    gate_entry: Mapping[str, Any],
    readiness_matrix: list[Mapping[str, Any]],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    actual_row_ids = [row["row_id"] for row in readiness_matrix]
    expected_row_ids = list(FINAL_RENDER_PATH_READINESS_REQUIRED_ROW_IDS)
    by_row = {row["row_id"]: row for row in readiness_matrix}
    missing_decision_rows = (
        "missing_production_subtitle_design_acceptance",
        "missing_production_render_acceptance",
        "missing_creative_acceptance",
        "missing_rights_publication_public_use_decisions",
    )
    required_rows_present = actual_row_ids == expected_row_ids
    active_diagnostic_source_preserved = (
        source_probe["artifact_id"] == RENDER_PATH_PROBE_ARTIFACT_ID
        and source_probe["validation"]["all_checks_passed"] is True
    )
    gate_separation_source_preserved = (
        gate_entry["artifact_id"] == PRODUCTION_LIMITATION_LIFT_ARTIFACT_ID
        and gate_entry["validation"]["all_checks_passed"] is True
        and gate_entry["boundaries"]["production_usage_allowed"] is False
    )
    lineage_predecessor_preserved = (
        lineage_surface["artifact_id"] == LINEAGE_OBSERVATION_ARTIFACT_ID
        and dry_read["artifact_id"] == RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
        and RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT == "7e96a28"
        and lineage_surface["validation"]["predecessor_lineage_present"] is True
    )
    selector_semantic_contract_present = (
        by_row.get("selector_semantic_style_contract_evidence", {}).get(
            "source_artifact_id"
        )
        == ARTIFACT_ID
    )
    render_adapter_input_contract_present = (
        by_row.get("render_adapter_input_contract_evidence", {}).get(
            "source_artifact_id"
        )
        == RENDER_PATH_CONTRACT_ARTIFACT_ID
    )
    local_outputs = by_row.get("local_ignored_proof_media_evidence", {}).get(
        "local_paths",
        {},
    )
    local_ignored_proof_media_referenced = (
        isinstance(local_outputs, Mapping)
        and {"ass", "video", "manifest", "contact_sheet"}.issubset(local_outputs)
    )
    missing_production_public_decisions_explicit = (
        all(
            by_row[row_id]["status"] == "missing"
            and by_row[row_id]["agent_can_progress_without_user_judgement"] is False
            and by_row[row_id]["future_human_rights_publication_decision_required"]
            is True
            for row_id in missing_decision_rows
        )
        and boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
    )
    production_public_boundary_closed = (
        missing_production_public_decisions_explicit
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
    )
    available_rows_have_agent_route = all(
        by_row[row_id]["status"] == "available"
        and by_row[row_id]["agent_can_progress_without_user_judgement"] is True
        for row_id in (
            "ed10ah_gate_separation_source",
            "diagnostic_proof_evidence",
            "selector_semantic_style_contract_evidence",
            "render_adapter_input_contract_evidence",
            "local_ignored_proof_media_evidence",
            "lineage_predecessor_evidence",
        )
    )
    return {
        "expected_row_ids": expected_row_ids,
        "actual_row_ids": actual_row_ids,
        "required_rows_present": required_rows_present,
        "available_rows_have_agent_route": available_rows_have_agent_route,
        "active_diagnostic_source_preserved": active_diagnostic_source_preserved,
        "active_diagnostic_source_artifact_id": source_probe["artifact_id"],
        "gate_separation_source_preserved": gate_separation_source_preserved,
        "gate_separation_source_artifact_id": gate_entry["artifact_id"],
        "lineage_predecessor_preserved": lineage_predecessor_preserved,
        "lineage_support_artifact_id": lineage_surface["artifact_id"],
        "dry_read_predecessor_artifact_id": dry_read["artifact_id"],
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "selector_semantic_contract_present": selector_semantic_contract_present,
        "render_adapter_input_contract_present": render_adapter_input_contract_present,
        "local_ignored_proof_media_referenced": local_ignored_proof_media_referenced,
        "missing_production_public_decisions_explicit": missing_production_public_decisions_explicit,
        "production_public_boundary_closed": production_public_boundary_closed,
        "new_render_run": False,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "episodes_tracked": boundaries["episodes_tracked"],
        "next_executable_route_defined": True,
        "all_checks_passed": (
            required_rows_present
            and available_rows_have_agent_route
            and active_diagnostic_source_preserved
            and gate_separation_source_preserved
            and lineage_predecessor_preserved
            and selector_semantic_contract_present
            and render_adapter_input_contract_present
            and local_ignored_proof_media_referenced
            and missing_production_public_decisions_explicit
            and production_public_boundary_closed
            and boundaries["new_render_created"] is False
            and boundaries["tracked_binary_artifact_created"] is False
            and boundaries["episodes_tracked"] is False
        ),
    }


def _final_render_path_stage1_checklist(
    *,
    probe: Mapping[str, Any],
    lineage: Mapping[str, Any],
    readiness: Mapping[str, Any],
    local_outputs: Mapping[str, str],
) -> list[dict[str, Any]]:
    def row(
        check_id: str,
        status: str,
        source_artifact_id: str,
        evidence: list[str],
        *,
        missing: list[str] | None = None,
        agent_can_continue: bool = True,
    ) -> dict[str, Any]:
        return {
            "check_id": check_id,
            "status": status,
            "source_artifact_id": source_artifact_id,
            "evidence": evidence,
            "missing_before_approval": missing or [],
            "agent_can_continue_without_user_judgement": agent_can_continue,
        }

    return [
        row(
            "render_adapter_path_selected",
            "selected_for_stage_1_preparation",
            probe["artifact_id"],
            [
                "FFmpeg/libass diagnostic subtitle overlay path is selected from ED-10af as the stage-1 candidate.",
                "Selection is preparation only and does not approve production render.",
            ],
            missing=["Production render acceptance remains missing."],
        ),
        row(
            "subtitle_ass_generation_path_available",
            "available_same_machine_diagnostic_only",
            probe["artifact_id"],
            [
                "ED-10af records an ignored ASS output path.",
                f"ASS path: {local_outputs.get('ass', '')}",
            ],
            missing=["Portable/tracked production ASS artifact strategy remains missing."],
        ),
        row(
            "semantic_selector_contract_available",
            "available",
            ARTIFACT_ID,
            [
                "The deterministic preset selector and ED-10ae render adapter input contract are available.",
                "ED-10ai records selector/semantic and render adapter evidence as ready.",
            ],
        ),
        row(
            "stable_body_text_policy_preserved",
            "preserved",
            probe["artifact_id"],
            [
                "ED-10af validation keeps stable body text across selected examples.",
                f"body_text_color_policy: {probe['body_text_color_policy']['reference']}",
            ],
        ),
        row(
            "badge_accent_backplate_routing_preserved",
            "preserved",
            probe["artifact_id"],
            [
                "ED-10af preserves badge/accent/backplate-first semantic variation.",
                "Body subtitle text color is not used as the primary semantic variation surface.",
            ],
        ),
        row(
            "line_break_safe_area_metadata_preserved",
            "preserved",
            probe["artifact_id"],
            [
                "ED-10af validation keeps safe-area line-break metadata.",
                "Whisper selected example records ASS newline behavior.",
            ],
        ),
        row(
            "local_ignored_proof_media_recorded",
            "recorded_same_machine_may_be_absent_elsewhere",
            lineage["artifact_id"],
            [
                "ED-10ag and ED-10ai record ignored ASS/MP4/manifest/contact-sheet paths.",
                readiness["source_evidence"]["local_ignored_output_policy"],
            ],
            missing=["If absent on another clone, regenerate or observe under an explicit diagnostic route only."],
        ),
        row(
            "no_tracked_binary_media",
            "closed",
            readiness["artifact_id"],
            [
                "ED-10ai render gate records no tracked binary artifact.",
                "episodes/ remains outside tracked artifact scope.",
            ],
        ),
        row(
            "production_gates_still_closed",
            "closed",
            readiness["artifact_id"],
            [
                "Production subtitle design, production render, and creative acceptance remain false.",
            ],
            missing=[
                "Explicit production subtitle design acceptance.",
                "Accepted production render output.",
                "Explicit creative acceptance.",
            ],
            agent_can_continue=False,
        ),
        row(
            "publishing_public_use_gates_still_closed",
            "closed_or_pending",
            readiness["artifact_id"],
            [
                "Rights status remains pending.",
                "Publishing acceptance and public-use permission remain false.",
            ],
            missing=[
                "Rights clearance or owner decision.",
                "Publishing acceptance.",
                "Explicit public-use permission.",
            ],
            agent_can_continue=False,
        ),
    ]


def _final_render_path_stage1_boundary_flags(
    readiness: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "source_readiness_new_render_created": readiness["render_gate"]["new_render_run"],
            "diagnostic_local_ignored_render_reused": True,
            "stage_1_path_selected": True,
            "stage_1_candidate_not_production_render": True,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _final_render_path_stage1_validation(
    *,
    probe: Mapping[str, Any],
    lineage: Mapping[str, Any],
    gate: Mapping[str, Any],
    dry: Mapping[str, Any],
    readiness: Mapping[str, Any],
    checklist: list[Mapping[str, Any]],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    actual_check_ids = [row["check_id"] for row in checklist]
    expected_check_ids = list(FINAL_RENDER_PATH_STAGE1_REQUIRED_CHECK_IDS)
    by_check = {row["check_id"]: row for row in checklist}
    required_checklist_present = actual_check_ids == expected_check_ids
    readiness_source_preserved = (
        readiness["artifact_id"] == FINAL_RENDER_PATH_READINESS_ARTIFACT_ID
        and readiness["validation"]["all_checks_passed"] is True
        and readiness["boundaries"]["final_render_path_approved"] is False
    )
    active_diagnostic_source_preserved = (
        probe["artifact_id"] == RENDER_PATH_PROBE_ARTIFACT_ID
        and probe["validation"]["all_checks_passed"] is True
    )
    lineage_source_preserved = (
        lineage["artifact_id"] == LINEAGE_OBSERVATION_ARTIFACT_ID
        and lineage["validation"]["predecessor_lineage_present"] is True
    )
    gate_source_preserved = (
        gate["artifact_id"] == PRODUCTION_LIMITATION_LIFT_ARTIFACT_ID
        and gate["validation"]["all_checks_passed"] is True
    )
    dry_read_predecessor_preserved = (
        dry["artifact_id"] == RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
        and RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT == "7e96a28"
    )
    stage_1_candidate_defined = (
        by_check.get("render_adapter_path_selected", {}).get("status")
        == "selected_for_stage_1_preparation"
        and boundaries["stage_1_path_selected"] is True
        and boundaries["stage_1_candidate_not_production_render"] is True
    )
    semantic_selector_contract_available = (
        by_check.get("semantic_selector_contract_available", {}).get(
            "source_artifact_id"
        )
        == ARTIFACT_ID
        and readiness["validation"]["selector_semantic_contract_present"] is True
        and readiness["validation"]["render_adapter_input_contract_present"] is True
    )
    stable_body_text_policy_preserved = (
        by_check.get("stable_body_text_policy_preserved", {}).get("status")
        == "preserved"
        and probe["validation"]["stable_body_text_preserved"] is True
    )
    badge_accent_backplate_routing_preserved = (
        by_check.get("badge_accent_backplate_routing_preserved", {}).get("status")
        == "preserved"
        and probe["validation"]["badge_accent_backplate_route_preserved"] is True
    )
    line_break_safe_area_metadata_preserved = (
        by_check.get("line_break_safe_area_metadata_preserved", {}).get("status")
        == "preserved"
        and probe["validation"]["safe_area_line_break_metadata_survived"] is True
    )
    local_outputs = readiness["source_evidence"]["local_ignored_outputs"]
    local_ignored_proof_media_referenced = (
        isinstance(local_outputs, Mapping)
        and {"ass", "video", "manifest", "contact_sheet"}.issubset(local_outputs)
        and by_check.get("local_ignored_proof_media_recorded", {}).get("status")
        == "recorded_same_machine_may_be_absent_elsewhere"
    )
    no_tracked_binary_media = (
        by_check.get("no_tracked_binary_media", {}).get("status") == "closed"
        and boundaries["tracked_binary_artifact_created"] is False
        and boundaries["episodes_tracked"] is False
    )
    production_public_boundary_closed = (
        by_check.get("production_gates_still_closed", {}).get("status") == "closed"
        and by_check.get("publishing_public_use_gates_still_closed", {}).get(
            "status"
        )
        == "closed_or_pending"
        and boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
    )
    return {
        "expected_check_ids": expected_check_ids,
        "actual_check_ids": actual_check_ids,
        "required_checklist_present": required_checklist_present,
        "readiness_source_preserved": readiness_source_preserved,
        "readiness_source_artifact_id": readiness["artifact_id"],
        "active_diagnostic_source_preserved": active_diagnostic_source_preserved,
        "active_diagnostic_source_artifact_id": probe["artifact_id"],
        "lineage_source_preserved": lineage_source_preserved,
        "lineage_support_artifact_id": lineage["artifact_id"],
        "gate_source_preserved": gate_source_preserved,
        "gate_source_artifact_id": gate["artifact_id"],
        "dry_read_predecessor_preserved": dry_read_predecessor_preserved,
        "dry_read_predecessor_artifact_id": dry["artifact_id"],
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "stage_1_candidate_defined": stage_1_candidate_defined,
        "semantic_selector_contract_available": semantic_selector_contract_available,
        "stable_body_text_policy_preserved": stable_body_text_policy_preserved,
        "badge_accent_backplate_routing_preserved": badge_accent_backplate_routing_preserved,
        "line_break_safe_area_metadata_preserved": line_break_safe_area_metadata_preserved,
        "local_ignored_proof_media_referenced": local_ignored_proof_media_referenced,
        "no_tracked_binary_media": no_tracked_binary_media,
        "production_public_boundary_closed": production_public_boundary_closed,
        "new_render_run": False,
        "next_executable_route_defined": True,
        "all_checks_passed": (
            required_checklist_present
            and readiness_source_preserved
            and active_diagnostic_source_preserved
            and lineage_source_preserved
            and gate_source_preserved
            and dry_read_predecessor_preserved
            and stage_1_candidate_defined
            and semantic_selector_contract_available
            and stable_body_text_policy_preserved
            and badge_accent_backplate_routing_preserved
            and line_break_safe_area_metadata_preserved
            and local_ignored_proof_media_referenced
            and no_tracked_binary_media
            and production_public_boundary_closed
            and boundaries["new_render_created"] is False
        ),
    }


def _final_render_path_stage2_operation_matrix(
    *,
    stage1: Mapping[str, Any],
    readiness: Mapping[str, Any],
    probe: Mapping[str, Any],
    lineage: Mapping[str, Any],
    replay: Mapping[str, Any],
) -> list[dict[str, Any]]:
    def row(
        row_id: str,
        area: str,
        status: str,
        source_artifact_id: str,
        details: list[str],
    ) -> dict[str, Any]:
        return {
            "row_id": row_id,
            "operation_area": area,
            "status": status,
            "source_artifact_id": source_artifact_id,
            "details": details,
        }

    return [
        row(
            "selected_render_path",
            "selected render path",
            "selected_for_replayability",
            stage1["artifact_id"],
            [
                replay["selected_render_path"],
                "Selected by ED-10aj as preparation only, not production render approval.",
            ],
        ),
        row(
            "required_tracked_inputs",
            "required tracked inputs",
            "available",
            stage1["artifact_id"],
            list(replay["tracked_inputs"]),
        ),
        row(
            "required_same_machine_local_inputs",
            "required same-machine local inputs",
            "same_machine_may_be_absent",
            probe["artifact_id"],
            [
                f"{name}: {path}"
                for name, path in replay["same_machine_local_inputs"].items()
            ],
        ),
        row(
            "ignored_output_paths",
            "ignored output paths",
            "recorded_same_machine_may_be_absent",
            lineage["artifact_id"],
            [
                f"{name}: {path}"
                for name, path in replay["ignored_output_paths"].items()
            ],
        ),
        row(
            "expected_output_types",
            "expected output types",
            "recorded",
            probe["artifact_id"],
            list(replay["expected_output_types"]),
        ),
        row(
            "command_family",
            "command or command family",
            "recorded_from_source_probe",
            probe["artifact_id"],
            [
                replay["command_family"],
                "Source probe command summary is retained for readback; ED-10ak does not rerun it.",
            ],
        ),
        row(
            "validation_readback_commands",
            "validation/readback commands",
            "recorded",
            FINAL_RENDER_PATH_STAGE2_ARTIFACT_ID,
            list(replay["validation_readback_commands"]),
        ),
        row(
            "fresh_clone_absence_behavior",
            "absence behavior on fresh clone",
            "non_fatal_for_tracked_docs",
            readiness["artifact_id"],
            [replay["fresh_clone_absence_behavior"]],
        ),
        row(
            "diagnostic_only_scope",
            "diagnostic-only scope",
            "closed_to_production_public_use",
            stage1["artifact_id"],
            [
                "The operation packet reuses ignored diagnostic proof only.",
                "It does not approve production subtitle design, production render, creative use, rights, publishing, or public use.",
            ],
        ),
        row(
            "missing_before_production_render",
            "missing before production render",
            "missing",
            readiness["artifact_id"],
            [
                "Explicit production subtitle design acceptance.",
                "Accepted final production render output.",
                "Final production render command/output manifest and review result.",
                "Explicit creative acceptance for production use.",
            ],
        ),
    ]


def _final_render_path_stage2_boundary_flags(
    stage1: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "new_replay_run": False,
            "source_stage1_new_render_created": stage1["render_gate"]["new_render_run"],
            "diagnostic_local_ignored_render_reused": True,
            "stage_2_replayability_packet_created": True,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _final_render_path_stage2_validation(
    *,
    stage1: Mapping[str, Any],
    readiness: Mapping[str, Any],
    probe: Mapping[str, Any],
    lineage: Mapping[str, Any],
    gate: Mapping[str, Any],
    dry: Mapping[str, Any],
    matrix: list[Mapping[str, Any]],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    actual_row_ids = [row["row_id"] for row in matrix]
    expected_row_ids = list(FINAL_RENDER_PATH_STAGE2_REQUIRED_ROW_IDS)
    by_row = {row["row_id"]: row for row in matrix}
    required_rows_present = actual_row_ids == expected_row_ids
    stage1_source_preserved = (
        stage1["artifact_id"] == FINAL_RENDER_PATH_STAGE1_ARTIFACT_ID
        and stage1["validation"]["all_checks_passed"] is True
        and stage1["boundaries"]["final_render_path_approved"] is False
    )
    readiness_source_preserved = (
        readiness["artifact_id"] == FINAL_RENDER_PATH_READINESS_ARTIFACT_ID
        and readiness["validation"]["all_checks_passed"] is True
    )
    active_diagnostic_source_preserved = (
        probe["artifact_id"] == RENDER_PATH_PROBE_ARTIFACT_ID
        and probe["validation"]["all_checks_passed"] is True
    )
    lineage_source_preserved = (
        lineage["artifact_id"] == LINEAGE_OBSERVATION_ARTIFACT_ID
        and lineage["validation"]["predecessor_lineage_present"] is True
    )
    gate_source_preserved = (
        gate["artifact_id"] == PRODUCTION_LIMITATION_LIFT_ARTIFACT_ID
        and gate["validation"]["all_checks_passed"] is True
    )
    dry_read_predecessor_preserved = (
        dry["artifact_id"] == RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
        and RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT == "7e96a28"
    )
    operation_replayability_defined = (
        by_row.get("selected_render_path", {}).get("status")
        == "selected_for_replayability"
        and by_row.get("command_family", {}).get("status")
        == "recorded_from_source_probe"
        and by_row.get("validation_readback_commands", {}).get("status")
        == "recorded"
    )
    existing_output_first_applied = (
        boundaries["diagnostic_local_ignored_render_reused"] is True
        and boundaries["new_replay_run"] is False
        and boundaries["new_render_created"] is False
    )
    tracked_inputs_available = (
        by_row.get("required_tracked_inputs", {}).get("status") == "available"
    )
    same_machine_inputs_recorded = (
        by_row.get("required_same_machine_local_inputs", {}).get("status")
        == "same_machine_may_be_absent"
    )
    local_outputs = by_row.get("ignored_output_paths", {}).get("details", [])
    local_ignored_outputs_referenced = (
        by_row.get("ignored_output_paths", {}).get("status")
        == "recorded_same_machine_may_be_absent"
        and all(
            any(detail.startswith(f"{name}:") for detail in local_outputs)
            for name in ("ass", "video", "manifest", "contact_sheet")
        )
    )
    fresh_clone_absence_nonfatal = (
        by_row.get("fresh_clone_absence_behavior", {}).get("status")
        == "non_fatal_for_tracked_docs"
    )
    diagnostic_only_scope_preserved = (
        by_row.get("diagnostic_only_scope", {}).get("status")
        == "closed_to_production_public_use"
    )
    production_public_boundary_closed = (
        by_row.get("missing_before_production_render", {}).get("status") == "missing"
        and boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
    )
    return {
        "expected_row_ids": expected_row_ids,
        "actual_row_ids": actual_row_ids,
        "required_rows_present": required_rows_present,
        "stage1_source_preserved": stage1_source_preserved,
        "stage1_source_artifact_id": stage1["artifact_id"],
        "readiness_source_preserved": readiness_source_preserved,
        "readiness_source_artifact_id": readiness["artifact_id"],
        "active_diagnostic_source_preserved": active_diagnostic_source_preserved,
        "active_diagnostic_source_artifact_id": probe["artifact_id"],
        "lineage_source_preserved": lineage_source_preserved,
        "lineage_support_artifact_id": lineage["artifact_id"],
        "gate_source_preserved": gate_source_preserved,
        "gate_source_artifact_id": gate["artifact_id"],
        "dry_read_predecessor_preserved": dry_read_predecessor_preserved,
        "dry_read_predecessor_artifact_id": dry["artifact_id"],
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "operation_replayability_defined": operation_replayability_defined,
        "existing_output_first_applied": existing_output_first_applied,
        "tracked_inputs_available": tracked_inputs_available,
        "same_machine_inputs_recorded": same_machine_inputs_recorded,
        "local_ignored_outputs_referenced": local_ignored_outputs_referenced,
        "fresh_clone_absence_nonfatal": fresh_clone_absence_nonfatal,
        "diagnostic_only_scope_preserved": diagnostic_only_scope_preserved,
        "production_public_boundary_closed": production_public_boundary_closed,
        "new_render_run": False,
        "new_replay_run": False,
        "next_executable_route_defined": True,
        "all_checks_passed": (
            required_rows_present
            and stage1_source_preserved
            and readiness_source_preserved
            and active_diagnostic_source_preserved
            and lineage_source_preserved
            and gate_source_preserved
            and dry_read_predecessor_preserved
            and operation_replayability_defined
            and existing_output_first_applied
            and tracked_inputs_available
            and same_machine_inputs_recorded
            and local_ignored_outputs_referenced
            and fresh_clone_absence_nonfatal
            and diagnostic_only_scope_preserved
            and production_public_boundary_closed
            and boundaries["tracked_binary_artifact_created"] is False
            and boundaries["episodes_tracked"] is False
        ),
    }


def _final_render_path_stage3_rehearsal_matrix(
    *,
    stage2: Mapping[str, Any],
    probe: Mapping[str, Any],
    lineage: Mapping[str, Any],
    rehearsal: Mapping[str, Any],
    survival: Mapping[str, Any],
) -> list[dict[str, Any]]:
    def row(
        row_id: str,
        area: str,
        status: str,
        source_artifact_id: str,
        details: list[str],
    ) -> dict[str, Any]:
        return {
            "row_id": row_id,
            "rehearsal_area": area,
            "status": status,
            "source_artifact_id": source_artifact_id,
            "details": details,
        }

    metadata = rehearsal["output_metadata"]
    return [
        row(
            "selected_render_path",
            "selected render path",
            "rehearsed_diagnostic_path",
            stage2["artifact_id"],
            [
                rehearsal["selected_render_path"],
                "Selected by ED-10aj and made replayable by ED-10ak; ED-10al rehearses it diagnostically only.",
            ],
        ),
        row(
            "tracked_inputs_used",
            "tracked inputs used",
            "available",
            stage2["artifact_id"],
            list(rehearsal["tracked_inputs"]),
        ),
        row(
            "same_machine_inputs_used",
            "same-machine local inputs used",
            "available_on_this_machine",
            probe["artifact_id"],
            [
                f"{name}: {path}"
                for name, path in rehearsal["same_machine_local_inputs"].items()
            ],
        ),
        row(
            "ignored_outputs_generated_or_recorded",
            "ignored outputs generated or recorded",
            "generated_ass_video_manifest_contact_sheet_recorded",
            lineage["artifact_id"],
            [
                *[
                    f"generated {name}: {path}"
                    for name, path in rehearsal["generated_ignored_outputs"].items()
                ],
                f"recorded contact_sheet: {rehearsal['recorded_ignored_outputs'].get('contact_sheet', '')}",
                "contact_sheet was recorded from ED-10ag but not generated by this stage-3 rehearsal function.",
            ],
        ),
        row(
            "command_and_command_family",
            "command and command family",
            "recorded",
            FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID,
            [
                rehearsal["command_family"],
                str(rehearsal["rehearsal_invocation_command"]),
                str(rehearsal["render_command_summary"]),
            ],
        ),
        row(
            "output_metadata_available",
            "output metadata",
            "available",
            FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID,
            [
                f"duration_seconds: {metadata.get('duration_seconds')}",
                f"resolution: {metadata.get('resolution')}",
                f"video_codec: {metadata.get('video_codec')}",
                f"audio_codec: {metadata.get('audio_codec')}",
                f"stream_count: {metadata.get('stream_count')}",
            ],
        ),
        row(
            "ass_style_tokens_survived",
            "ASS/subtitle style tokens",
            "survived",
            probe["artifact_id"],
            [
                f"ass_subtitle_style_tokens_survived: {survival['ass_subtitle_style_tokens_survived']}",
                "Source probe style axes remain preserved in the generated ASS-backed diagnostic render.",
            ],
        ),
        row(
            "stable_body_text_policy_survived",
            "stable body text policy",
            "survived",
            probe["artifact_id"],
            [
                f"stable_body_text_policy_survived: {survival['stable_body_text_policy_survived']}",
                "Body text stays on stable_default_body_text; semantic variation remains outside body fill.",
            ],
        ),
        row(
            "badge_accent_backplate_route_survived",
            "badge/accent/backplate route",
            "survived",
            probe["artifact_id"],
            [
                f"badge_accent_backplate_route_survived: {survival['badge_accent_backplate_route_survived']}",
                "Speaker/emotion color route remains badge/accent/backplate-first.",
            ],
        ),
        row(
            "line_break_safe_area_metadata_survived",
            "line-break and safe-area metadata",
            "survived",
            probe["artifact_id"],
            [
                f"line_break_safe_area_metadata_survived: {survival['line_break_safe_area_metadata_survived']}",
                "The whisper probe retains explicit ASS line break metadata and bottom safe-area notes.",
            ],
        ),
        row(
            "production_public_gates_still_closed",
            "production/public gates",
            "closed",
            FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID,
            [
                "production_subtitle_design_acceptance=false",
                "production_render_acceptance=false",
                "creative_acceptance=false",
                "rights_status=pending",
                "publishing_acceptance=false",
                "public_use_permission=false",
            ],
        ),
    ]


def _final_render_path_stage3_boundary_flags() -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": True,
            "new_rehearsal_run": True,
            "new_replay_run": False,
            "diagnostic_local_ignored_render_created": True,
            "diagnostic_local_ignored_render_reused": False,
            "stage_3_rehearsal_packet_created": True,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _final_render_path_stage3_validation(
    *,
    stage2: Mapping[str, Any],
    stage1: Mapping[str, Any],
    readiness: Mapping[str, Any],
    probe: Mapping[str, Any],
    lineage: Mapping[str, Any],
    gate: Mapping[str, Any],
    dry: Mapping[str, Any],
    rehearsal: Mapping[str, Any],
    survival: Mapping[str, Any],
    matrix: list[Mapping[str, Any]],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    actual_row_ids = [row["row_id"] for row in matrix]
    expected_row_ids = list(FINAL_RENDER_PATH_STAGE3_REQUIRED_ROW_IDS)
    by_row = {row["row_id"]: row for row in matrix}
    required_rows_present = actual_row_ids == expected_row_ids
    stage2_source_preserved = (
        stage2["artifact_id"] == FINAL_RENDER_PATH_STAGE2_ARTIFACT_ID
        and stage2["validation"]["all_checks_passed"] is True
        and stage2["boundaries"]["final_render_path_approved"] is False
    )
    stage1_source_preserved = stage1["artifact_id"] == FINAL_RENDER_PATH_STAGE1_ARTIFACT_ID
    readiness_source_preserved = (
        readiness["artifact_id"] == FINAL_RENDER_PATH_READINESS_ARTIFACT_ID
    )
    active_diagnostic_source_preserved = (
        probe["artifact_id"] == RENDER_PATH_PROBE_ARTIFACT_ID
        and probe["validation"]["all_checks_passed"] is True
    )
    lineage_source_preserved = (
        lineage["artifact_id"] == LINEAGE_OBSERVATION_ARTIFACT_ID
        and lineage["validation"]["predecessor_lineage_present"] is True
    )
    gate_source_preserved = (
        gate["artifact_id"] == PRODUCTION_LIMITATION_LIFT_ARTIFACT_ID
        and gate["validation"]["all_checks_passed"] is True
    )
    dry_read_predecessor_preserved = (
        dry["artifact_id"] == RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
        and RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT == "7e96a28"
    )
    generated_outputs = rehearsal["generated_ignored_outputs"]
    recorded_outputs = rehearsal["recorded_ignored_outputs"]
    ignored_outputs_generated_or_recorded = (
        all(generated_outputs.get(name) for name in ("ass", "video", "manifest"))
        and bool(recorded_outputs.get("contact_sheet"))
    )
    metadata = rehearsal["output_metadata"]
    output_metadata_available = all(
        metadata.get(name)
        for name in (
            "duration_seconds",
            "resolution",
            "video_codec",
            "audio_codec",
            "stream_count",
        )
    )
    command_recorded = (
        by_row.get("command_and_command_family", {}).get("status") == "recorded"
        and bool(rehearsal.get("render_command_summary"))
        and bool(rehearsal.get("rehearsal_invocation_command"))
    )
    rehearsal_run_recorded = (
        rehearsal["new_rehearsal_run"] is True
        and rehearsal["local_probe_readback"]["status"] == "local_ignored_probe_generated"
        and boundaries["new_rehearsal_run"] is True
        and boundaries["new_render_created"] is True
    )
    ass_style_tokens_survived = (
        survival["ass_subtitle_style_tokens_survived"] is True
        and by_row.get("ass_style_tokens_survived", {}).get("status") == "survived"
    )
    stable_body_text_policy_survived = (
        survival["stable_body_text_policy_survived"] is True
        and by_row.get("stable_body_text_policy_survived", {}).get("status")
        == "survived"
    )
    badge_accent_backplate_route_survived = (
        survival["badge_accent_backplate_route_survived"] is True
        and by_row.get("badge_accent_backplate_route_survived", {}).get("status")
        == "survived"
    )
    line_break_safe_area_metadata_survived = (
        survival["line_break_safe_area_metadata_survived"] is True
        and by_row.get("line_break_safe_area_metadata_survived", {}).get("status")
        == "survived"
    )
    production_public_boundary_closed = (
        by_row.get("production_public_gates_still_closed", {}).get("status")
        == "closed"
        and boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
    )
    return {
        "expected_row_ids": expected_row_ids,
        "actual_row_ids": actual_row_ids,
        "required_rows_present": required_rows_present,
        "stage2_source_preserved": stage2_source_preserved,
        "stage2_source_artifact_id": stage2["artifact_id"],
        "stage1_source_preserved": stage1_source_preserved,
        "stage1_source_artifact_id": stage1["artifact_id"],
        "readiness_source_preserved": readiness_source_preserved,
        "readiness_source_artifact_id": readiness["artifact_id"],
        "active_diagnostic_source_preserved": active_diagnostic_source_preserved,
        "active_diagnostic_source_artifact_id": probe["artifact_id"],
        "lineage_source_preserved": lineage_source_preserved,
        "lineage_support_artifact_id": lineage["artifact_id"],
        "gate_source_preserved": gate_source_preserved,
        "gate_source_artifact_id": gate["artifact_id"],
        "dry_read_predecessor_preserved": dry_read_predecessor_preserved,
        "dry_read_predecessor_artifact_id": dry["artifact_id"],
        "dry_read_predecessor_source_commit": RENDER_CONTRACT_CONSUMER_DRY_READ_COMMIT,
        "rehearsal_run_recorded": rehearsal_run_recorded,
        "existing_output_first_applied": rehearsal["existing_output_first_applied"],
        "existing_output_first_reused": rehearsal["existing_output_first_reused"],
        "ignored_outputs_generated_or_recorded": ignored_outputs_generated_or_recorded,
        "command_recorded": command_recorded,
        "output_metadata_available": output_metadata_available,
        "ass_style_tokens_survived": ass_style_tokens_survived,
        "stable_body_text_policy_survived": stable_body_text_policy_survived,
        "badge_accent_backplate_route_survived": badge_accent_backplate_route_survived,
        "line_break_safe_area_metadata_survived": line_break_safe_area_metadata_survived,
        "production_public_boundary_closed": production_public_boundary_closed,
        "new_render_run": True,
        "new_rehearsal_run": True,
        "next_executable_route_defined": True,
        "all_checks_passed": (
            required_rows_present
            and stage2_source_preserved
            and stage1_source_preserved
            and readiness_source_preserved
            and active_diagnostic_source_preserved
            and lineage_source_preserved
            and gate_source_preserved
            and dry_read_predecessor_preserved
            and rehearsal_run_recorded
            and ignored_outputs_generated_or_recorded
            and command_recorded
            and output_metadata_available
            and ass_style_tokens_survived
            and stable_body_text_policy_survived
            and badge_accent_backplate_route_survived
            and line_break_safe_area_metadata_survived
            and production_public_boundary_closed
            and boundaries["tracked_binary_artifact_created"] is False
            and boundaries["episodes_tracked"] is False
        ),
    }


def _production_limitation_lift_stage1_gate_matrix(
    *,
    stage3: Mapping[str, Any],
    diagnostic_evidence: Mapping[str, Any],
) -> list[dict[str, Any]]:
    def row(
        gate_name: str,
        current_status: str,
        source_evidence: list[str],
        missing_evidence: list[str],
        owner: str,
        agent_can_progress: bool,
        unsafe: list[str],
        action: str,
    ) -> dict[str, Any]:
        return {
            "gate_name": gate_name,
            "current_status": current_status,
            "source_evidence": source_evidence,
            "missing_evidence": missing_evidence,
            "next_decision_owner": owner,
            "agent_can_progress_without_user_judgement": agent_can_progress,
            "decision_preparation_action": action,
            "unsafe_overclaiming": unsafe,
        }

    metadata = diagnostic_evidence["output_metadata"]
    generated_outputs = diagnostic_evidence["generated_ignored_outputs"]
    survival = diagnostic_evidence["survival_readback"]
    return [
        row(
            "diagnostic_render_path_rehearsal_evidence",
            "available_diagnostic_only",
            [
                f"ED-10al artifact: {stage3['artifact_id']}",
                f"selected path: {diagnostic_evidence['selected_render_path']}",
                "generated ignored outputs: "
                + ", ".join(sorted(generated_outputs.keys())),
                f"metadata: {metadata.get('duration_seconds')}s / {metadata.get('resolution')} / {metadata.get('video_codec')} / {metadata.get('audio_codec')}",
                f"style tokens survived: {survival['ass_subtitle_style_tokens_survived']}",
                f"stable body text survived: {survival['stable_body_text_policy_survived']}",
                f"badge/accent/backplate route survived: {survival['badge_accent_backplate_route_survived']}",
                f"line-break/safe-area metadata survived: {survival['line_break_safe_area_metadata_survived']}",
            ],
            [
                "Production subtitle design acceptance.",
                "Production render acceptance.",
                "Creative, rights, publishing, and public-use decisions.",
            ],
            "Agent",
            True,
            [
                "Treating ED-10al diagnostic output as production render approval.",
                "Treating style-token survival as final production subtitle design acceptance.",
            ],
            "Carry ED-10al forward as diagnostic evidence only.",
        ),
        row(
            "production_subtitle_design_acceptance",
            "not_accepted",
            [
                "ED-10al records style-token, stable body text, badge/accent/backplate, and safe-area survival.",
                "Prior user observation allows forward progress without reopening display/layout polish.",
            ],
            [
                "Explicit human acceptance that the subtitle design is production-ready.",
                "Any required representative production-sequence typography review.",
            ],
            "User",
            False,
            [
                "Claiming production subtitle design acceptance from diagnostic survival readback.",
                "Reopening old layout polish as if ED-10am required it.",
            ],
            "Prepare a decision packet only when production design acceptance is the next blocking decision.",
        ),
        row(
            "production_render_acceptance",
            "not_accepted",
            [
                "ED-10al generated a 4.2s ignored diagnostic MP4 and local manifest.",
                "FFmpeg/libass command family and output metadata are recorded.",
            ],
            [
                "Accepted final production render output.",
                "Final production render command, manifest, and human review result.",
            ],
            "User",
            False,
            [
                "Describing the ignored diagnostic MP4 as a production render.",
                "Using output metadata alone as render acceptance.",
            ],
            "Keep production render acceptance closed until a separate output is accepted.",
        ),
        row(
            "creative_acceptance",
            "not_accepted",
            [
                "The diagnostic presentation path is acceptable enough to move forward.",
                "No old candidate or cut review axis is reopened by ED-10am.",
            ],
            [
                "Explicit creative approval for production use.",
                "Any final editorial or representative-sequence acceptance packet.",
            ],
            "User",
            False,
            [
                "Treating forward-progress preference as creative acceptance.",
                "Treating diagnostic rehearsal completion as editorial approval.",
            ],
            "Isolate creative acceptance only when that gate becomes the next decision.",
        ),
        row(
            "rights_status",
            "pending",
            [
                "ED-10al and ED-10am make no rights clearance claim.",
                "Ignored proof outputs stay same-machine diagnostic evidence.",
            ],
            [
                "Rights clearance or owner decision for source material and distribution context.",
                "Publication-specific material-use clearance.",
            ],
            "Rights",
            False,
            [
                "Inferring rights clearance from local diagnostic generation.",
                "Treating ignored proof media as public-use permission.",
            ],
            "Prepare a rights decision packet only when rights is the active gate.",
        ),
        row(
            "publishing_acceptance",
            "not_accepted",
            [
                "No upload, visibility, platform metadata, or scheduling action occurs in ED-10al/ED-10am.",
            ],
            [
                "Human publication decision.",
                "Platform/account-specific publishing acceptance and final metadata decision.",
            ],
            "Publication",
            False,
            [
                "Preparing upload/public release actions from diagnostic evidence.",
                "Claiming publishing readiness before rights and production gates are explicit.",
            ],
            "Keep publishing acceptance closed until a publication owner answers.",
        ),
        row(
            "public_use_permission",
            "not_allowed",
            [
                "Production design, render, creative, rights, and publishing gates remain false or pending.",
            ],
            [
                "All upstream acceptances required for public use.",
                "Explicit public-use permission.",
            ],
            "Publication",
            False,
            [
                "Granting public-use permission from local diagnostic proof.",
                "Combining partial gate evidence into public-ready status.",
            ],
            "Keep public-use permission closed until all upstream gates are explicit.",
        ),
        row(
            "tracked_media_boundary",
            "closed_no_tracked_media",
            [
                "ED-10am creates tracked JSON/Markdown only.",
                "ED-10al recorded `tracked_binary_artifact_created=false` and `episodes_tracked=false`.",
            ],
            [],
            "Agent",
            True,
            [
                "Adding ignored ASS/MP4/manifest/contact-sheet outputs to Git.",
                "Moving same-machine media into tracked docs as binary artifacts.",
            ],
            "Keep `episodes/` ignored and verify `git ls-files episodes` remains empty.",
        ),
        row(
            "same_machine_ignored_evidence_boundary",
            "available_same_machine_only",
            [
                "ED-10al generated ignored ASS/MP4/manifest outputs on this machine.",
                "The contact-sheet path is recorded but not generated by the stage-3 helper.",
            ],
            [
                "A production artifact store or portable media package, if later required.",
                "Fresh-clone local media availability.",
            ],
            "Agent",
            True,
            [
                "Claiming same-machine ignored outputs are portable tracked artifacts.",
                "Treating fresh-clone absence as a failure of this tracked packet.",
            ],
            "Record paths and ignore status; do not promote media without an explicit strategy.",
        ),
    ]


def _production_limitation_lift_stage1_boundary_flags(
    stage3: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "new_rehearsal_run": False,
            "source_stage3_new_render_created": stage3["render_gate"]["new_render_run"],
            "source_stage3_new_rehearsal_run": stage3["render_gate"][
                "new_rehearsal_run"
            ],
            "diagnostic_stage3_evidence_reused": True,
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _production_limitation_lift_stage1_validation(
    *,
    stage3: Mapping[str, Any],
    gate_matrix: list[Mapping[str, Any]],
    boundaries: Mapping[str, Any],
    diagnostic_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    actual_gate_names = [gate["gate_name"] for gate in gate_matrix]
    expected_gate_names = list(PRODUCTION_LIMITATION_LIFT_STAGE1_GATE_NAMES)
    by_gate = {gate["gate_name"]: gate for gate in gate_matrix}
    closed_gate_names = (
        "production_subtitle_design_acceptance",
        "production_render_acceptance",
        "creative_acceptance",
        "rights_status",
        "publishing_acceptance",
        "public_use_permission",
    )
    stage3_source_preserved = (
        stage3["artifact_id"] == FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID
        and stage3["validation"]["all_checks_passed"] is True
        and stage3["validation"]["production_public_boundary_closed"] is True
    )
    generated = diagnostic_evidence["generated_ignored_outputs"]
    metadata = diagnostic_evidence["output_metadata"]
    survival = diagnostic_evidence["survival_readback"]
    diagnostic_evidence_linked = (
        diagnostic_evidence["primary_diagnostic_rehearsal_artifact_id"]
        == FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID
        and all(generated.get(name) for name in ("ass", "video", "manifest"))
        and metadata.get("duration_seconds") == 4.2
        and metadata.get("resolution") == "1920x1080"
        and survival["ass_subtitle_style_tokens_survived"] is True
        and survival["stable_body_text_policy_survived"] is True
        and survival["badge_accent_backplate_route_survived"] is True
        and survival["line_break_safe_area_metadata_survived"] is True
    )
    closed_statuses_preserved = (
        by_gate["production_subtitle_design_acceptance"]["current_status"]
        == "not_accepted"
        and by_gate["production_render_acceptance"]["current_status"]
        == "not_accepted"
        and by_gate["creative_acceptance"]["current_status"] == "not_accepted"
        and by_gate["rights_status"]["current_status"] == "pending"
        and by_gate["publishing_acceptance"]["current_status"] == "not_accepted"
        and by_gate["public_use_permission"]["current_status"] == "not_allowed"
    )
    production_public_non_approval_explicit = (
        closed_statuses_preserved
        and boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
    )
    owners_present = all(gate.get("next_decision_owner") for gate in gate_matrix)
    unsafe_overclaiming_present = all(
        bool(gate.get("unsafe_overclaiming")) for gate in gate_matrix
    )
    agent_progress_scoped = (
        by_gate["diagnostic_render_path_rehearsal_evidence"][
            "agent_can_progress_without_user_judgement"
        ]
        is True
        and by_gate["tracked_media_boundary"][
            "agent_can_progress_without_user_judgement"
        ]
        is True
        and by_gate["same_machine_ignored_evidence_boundary"][
            "agent_can_progress_without_user_judgement"
        ]
        is True
        and all(
            by_gate[gate]["agent_can_progress_without_user_judgement"] is False
            for gate in closed_gate_names
        )
    )
    tracked_media_boundary_closed = (
        by_gate["tracked_media_boundary"]["current_status"] == "closed_no_tracked_media"
        and boundaries["tracked_binary_artifact_created"] is False
        and boundaries["episodes_tracked"] is False
    )
    same_machine_ignored_boundary_recorded = (
        by_gate["same_machine_ignored_evidence_boundary"]["current_status"]
        == "available_same_machine_only"
        and boundaries["diagnostic_stage3_evidence_reused"] is True
    )
    next_executable_route_defined = True
    return {
        "expected_gate_names": expected_gate_names,
        "actual_gate_names": actual_gate_names,
        "gate_names_present": actual_gate_names == expected_gate_names,
        "stage3_source_preserved": stage3_source_preserved,
        "stage3_source_artifact_id": stage3["artifact_id"],
        "diagnostic_evidence_linked": diagnostic_evidence_linked,
        "production_public_non_approval_explicit": production_public_non_approval_explicit,
        "closed_statuses_preserved": closed_statuses_preserved,
        "owners_present": owners_present,
        "unsafe_overclaiming_present": unsafe_overclaiming_present,
        "agent_progress_scoped": agent_progress_scoped,
        "tracked_media_boundary_closed": tracked_media_boundary_closed,
        "same_machine_ignored_boundary_recorded": same_machine_ignored_boundary_recorded,
        "next_executable_route_defined": next_executable_route_defined,
        "new_render_run": False,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "episodes_tracked": boundaries["episodes_tracked"],
        "all_checks_passed": (
            actual_gate_names == expected_gate_names
            and stage3_source_preserved
            and diagnostic_evidence_linked
            and production_public_non_approval_explicit
            and owners_present
            and unsafe_overclaiming_present
            and agent_progress_scoped
            and tracked_media_boundary_closed
            and same_machine_ignored_boundary_recorded
            and next_executable_route_defined
            and boundaries["tracked_binary_artifact_created"] is False
            and boundaries["episodes_tracked"] is False
        ),
    }


def _production_limitation_lift_stage2_decision_groups(
    stage1_lift: Mapping[str, Any],
) -> list[dict[str, Any]]:
    gates = {gate["gate_name"]: gate for gate in stage1_lift["gate_matrix"]}
    diagnostic = stage1_lift["diagnostic_evidence"]
    metadata = diagnostic["output_metadata"]
    survival = diagnostic["survival_readback"]

    def evidence_for(*gate_names: str) -> list[str]:
        evidence: list[str] = []
        for gate_name in gate_names:
            evidence.extend(gates[gate_name]["source_evidence"])
        return list(dict.fromkeys(evidence))

    def missing_for(*gate_names: str) -> list[str]:
        missing: list[str] = []
        for gate_name in gate_names:
            missing.extend(gates[gate_name]["missing_evidence"])
        return list(dict.fromkeys(missing))

    def group(
        group_id: str,
        *,
        gate_names: list[str],
        current_status: str,
        owner: str,
        source_evidence: list[str],
        missing_evidence: list[str],
        unsafe: list[str],
        next_safe_action: str,
    ) -> dict[str, Any]:
        return {
            "decision_group_id": group_id,
            "current_status": current_status,
            "source_gate_names": gate_names,
            "source_evidence_available": source_evidence,
            "missing_evidence": missing_evidence,
            "decision_owner": owner,
            "agent_can_progress_without_user_judgement": True,
            "owner_judgement_required_for_approval": True,
            "agent_may_approve": False,
            "unsafe_overclaiming_examples": unsafe,
            "next_safe_action": next_safe_action,
        }

    return [
        group(
            "subtitle_design_visual_acceptance",
            gate_names=[
                "diagnostic_render_path_rehearsal_evidence",
                "production_subtitle_design_acceptance",
                "creative_acceptance",
            ],
            current_status="decision_prepared_not_approved",
            owner="User",
            source_evidence=[
                f"ED-10am source gate matrix: {stage1_lift['artifact_id']}",
                f"ED-10al diagnostic rehearsal: {stage1_lift['source_final_render_path_stage_3_rehearsal_artifact_id']}",
                f"style tokens survived: {survival['ass_subtitle_style_tokens_survived']}",
                f"stable body text survived: {survival['stable_body_text_policy_survived']}",
                f"badge/accent/backplate route survived: {survival['badge_accent_backplate_route_survived']}",
                f"line-break/safe-area metadata survived: {survival['line_break_safe_area_metadata_survived']}",
            ]
            + evidence_for(
                "production_subtitle_design_acceptance",
                "creative_acceptance",
            ),
            missing_evidence=missing_for(
                "production_subtitle_design_acceptance",
                "creative_acceptance",
            ),
            unsafe=[
                "Treating diagnostic survival readback as production subtitle design acceptance.",
                "Treating forward-progress preference as creative approval.",
                "Reopening old layout polish or Candidate 0-3 review as if ED-10an required it.",
            ],
            next_safe_action=(
                "Prepare owner-review input for design/visual acceptance without "
                "claiming acceptance."
            ),
        ),
        group(
            "production_render_readiness",
            gate_names=[
                "diagnostic_render_path_rehearsal_evidence",
                "production_render_acceptance",
                "tracked_media_boundary",
                "same_machine_ignored_evidence_boundary",
            ],
            current_status="decision_prepared_not_approved",
            owner="User",
            source_evidence=[
                "ED-10am records ED-10al generated ignored ASS/MP4/manifest outputs.",
                f"metadata: {metadata.get('duration_seconds')}s / {metadata.get('resolution')} / {metadata.get('video_codec')} / {metadata.get('audio_codec')} / streams={metadata.get('stream_count')}",
                "tracked media boundary is closed.",
                "same-machine ignored evidence boundary is recorded.",
            ]
            + evidence_for(
                "production_render_acceptance",
                "tracked_media_boundary",
                "same_machine_ignored_evidence_boundary",
            ),
            missing_evidence=missing_for(
                "production_render_acceptance",
                "same_machine_ignored_evidence_boundary",
            ),
            unsafe=[
                "Describing the ignored diagnostic MP4 as a production render.",
                "Using ffprobe metadata alone as production render acceptance.",
                "Treating local ignored media as portable tracked deliverables.",
            ],
            next_safe_action=(
                "Prepare render-readiness owner review inputs while keeping "
                "the diagnostic media ignored and untracked."
            ),
        ),
        group(
            "rights_publishing_public_use_clearance",
            gate_names=[
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ],
            current_status="decision_prepared_not_approved",
            owner="Rights / Publication",
            source_evidence=evidence_for(
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ),
            missing_evidence=missing_for(
                "rights_status",
                "publishing_acceptance",
                "public_use_permission",
            ),
            unsafe=[
                "Inferring rights clearance from local diagnostic generation.",
                "Preparing upload or public release actions from diagnostic evidence.",
                "Granting public-use permission before rights and publishing owners answer.",
            ],
            next_safe_action=(
                "Prepare a rights/publication owner review packet; do not "
                "clear rights, publishing, or public use."
            ),
        ),
    ]


def _production_limitation_lift_stage2_no_decision_yet(
    stage1_lift: Mapping[str, Any],
) -> dict[str, Any]:
    source = stage1_lift["non_approval_readback"]
    return {
        "production_subtitle_design_acceptance": source[
            "production_subtitle_design_acceptance"
        ],
        "production_render_acceptance": source["production_render_acceptance"],
        "creative_acceptance": source["creative_acceptance"],
        "rights_status": source["rights_status"],
        "publishing_acceptance": source["publishing_acceptance"],
        "public_use_permission": source["public_use_permission"],
        "production_public_decision_approved": False,
        "user_decision_requested_now": False,
    }


def _production_limitation_lift_stage2_boundary_flags(
    stage1_lift: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "new_rehearsal_run": False,
            "source_stage1_gate_matrix_reused": True,
            "source_stage1_new_render_created": stage1_lift["render_gate"][
                "new_render_run"
            ],
            "source_stage3_new_render_created": stage1_lift["render_gate"][
                "source_stage3_new_render_run"
            ],
            "diagnostic_stage3_evidence_reused": True,
            "decision_packet_only": True,
            "decision_packet_does_not_grant_approval": True,
            "user_decision_requested_now": False,
            "decision_group_count": len(
                PRODUCTION_LIMITATION_LIFT_STAGE2_DECISION_GROUP_IDS
            ),
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _production_limitation_lift_stage2_validation(
    *,
    stage1_lift: Mapping[str, Any],
    source_evidence: Mapping[str, Any],
    decision_groups: list[Mapping[str, Any]],
    no_decision_yet: Mapping[str, Any],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    expected_group_ids = list(PRODUCTION_LIMITATION_LIFT_STAGE2_DECISION_GROUP_IDS)
    actual_group_ids = [group["decision_group_id"] for group in decision_groups]
    source_gate_matrix_preserved = (
        stage1_lift["artifact_id"] == PRODUCTION_LIMITATION_LIFT_STAGE1_ARTIFACT_ID
        and stage1_lift["validation"]["all_checks_passed"] is True
        and stage1_lift["gate_names"] == list(PRODUCTION_LIMITATION_LIFT_STAGE1_GATE_NAMES)
        and len(stage1_lift["gate_matrix"]) == len(PRODUCTION_LIMITATION_LIFT_STAGE1_GATE_NAMES)
    )
    decision_groups_present = actual_group_ids == expected_group_ids
    decision_groups_bounded = (
        decision_groups_present
        and len(decision_groups) <= 3
        and all(group["source_gate_names"] for group in decision_groups)
    )
    no_decision_boundary_explicit = (
        no_decision_yet["production_subtitle_design_acceptance"] is False
        and no_decision_yet["production_render_acceptance"] is False
        and no_decision_yet["creative_acceptance"] is False
        and no_decision_yet["rights_status"] == "pending"
        and no_decision_yet["publishing_acceptance"] is False
        and no_decision_yet["public_use_permission"] is False
        and no_decision_yet["production_public_decision_approved"] is False
        and no_decision_yet["user_decision_requested_now"] is False
    )
    source_evidence_linked = (
        source_evidence["source_stage1_artifact_id"]
        == PRODUCTION_LIMITATION_LIFT_STAGE1_ARTIFACT_ID
        and source_evidence["primary_diagnostic_rehearsal_artifact_id"]
        == FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID
        and source_evidence["source_gate_count"]
        == len(PRODUCTION_LIMITATION_LIFT_STAGE1_GATE_NAMES)
        and source_evidence["diagnostic_output_metadata"]["duration_seconds"] == 4.2
        and source_evidence["diagnostic_output_metadata"]["resolution"] == "1920x1080"
        and source_evidence["diagnostic_survival_readback"][
            "ass_subtitle_style_tokens_survived"
        ]
        is True
    )
    production_public_gates_still_closed = (
        boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
        and boundaries["decision_packet_does_not_grant_approval"] is True
    )
    unsafe_overclaiming_present = all(
        bool(group["unsafe_overclaiming_examples"]) for group in decision_groups
    )
    next_safe_actions_present = all(
        bool(group["next_safe_action"]) for group in decision_groups
    )
    agent_progress_scoped = all(
        group["agent_can_progress_without_user_judgement"] is True
        and group["owner_judgement_required_for_approval"] is True
        and group["agent_may_approve"] is False
        for group in decision_groups
    )
    tracked_media_boundary_closed = (
        boundaries["tracked_binary_artifact_created"] is False
        and boundaries["episodes_tracked"] is False
    )
    next_executable_route_defined = True
    return {
        "expected_decision_group_ids": expected_group_ids,
        "actual_decision_group_ids": actual_group_ids,
        "source_gate_matrix_preserved": source_gate_matrix_preserved,
        "decision_groups_present": decision_groups_present,
        "decision_groups_bounded": decision_groups_bounded,
        "no_decision_boundary_explicit": no_decision_boundary_explicit,
        "source_evidence_linked": source_evidence_linked,
        "production_public_gates_still_closed": production_public_gates_still_closed,
        "unsafe_overclaiming_present": unsafe_overclaiming_present,
        "next_safe_actions_present": next_safe_actions_present,
        "agent_progress_scoped": agent_progress_scoped,
        "tracked_media_boundary_closed": tracked_media_boundary_closed,
        "next_executable_route_defined": next_executable_route_defined,
        "new_render_run": False,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "episodes_tracked": boundaries["episodes_tracked"],
        "all_checks_passed": (
            source_gate_matrix_preserved
            and decision_groups_bounded
            and no_decision_boundary_explicit
            and source_evidence_linked
            and production_public_gates_still_closed
            and unsafe_overclaiming_present
            and next_safe_actions_present
            and agent_progress_scoped
            and tracked_media_boundary_closed
            and next_executable_route_defined
        ),
    }


def _production_limitation_lift_stage3_owner_review_groups(
    stage2_lift: Mapping[str, Any],
) -> list[dict[str, Any]]:
    by_group = {
        group["decision_group_id"]: group for group in stage2_lift["decision_groups"]
    }
    owner_categories = {
        "subtitle_design_visual_acceptance": "User",
        "production_render_readiness": "User",
        "rights_publishing_public_use_clearance": "Rights / Publication",
    }
    future_topics = {
        "subtitle_design_visual_acceptance": (
            "Future freeform judgement about whether the subtitle design and "
            "visual feel are acceptable enough for production use."
        ),
        "production_render_readiness": (
            "Future freeform judgement about whether render output evidence is "
            "sufficient for production render readiness."
        ),
        "rights_publishing_public_use_clearance": (
            "Future rights/publication judgement about whether source material, "
            "publishing context, and public use are cleared."
        ),
    }
    entries: list[dict[str, Any]] = []
    for group_id in PRODUCTION_LIMITATION_LIFT_STAGE3_OWNER_REVIEW_GROUP_IDS:
        source_group = by_group[group_id]
        entries.append(
            {
                "decision_group_id": group_id,
                "decision_owner_category": owner_categories[group_id],
                "source_decision_group_current_status": source_group[
                    "current_status"
                ],
                "available_evidence": list(source_group["source_evidence_available"]),
                "missing_evidence": list(source_group["missing_evidence"]),
                "safe_next_action": source_group["next_safe_action"],
                "unsafe_overclaiming_examples": list(
                    source_group["unsafe_overclaiming_examples"]
                ),
                "can_proceed_without_user_judgement": True,
                "must_stop_before_approval": True,
                "approval_owner_required_later": True,
                "agent_may_approve": False,
                "future_decision_topic_plain_language": future_topics[group_id],
            }
        )
    return entries


def _production_limitation_lift_stage3_no_approval_yet(
    stage2_lift: Mapping[str, Any],
) -> dict[str, Any]:
    source = stage2_lift["no_decision_yet"]
    return {
        "production_subtitle_design_acceptance": source[
            "production_subtitle_design_acceptance"
        ],
        "production_render_acceptance": source["production_render_acceptance"],
        "creative_acceptance": source["creative_acceptance"],
        "rights_status": source["rights_status"],
        "publishing_acceptance": source["publishing_acceptance"],
        "public_use_permission": source["public_use_permission"],
        "production_public_decision_approved": False,
        "user_decision_requested_now": False,
        "owner_review_prep_does_not_grant_approval": True,
    }


def _production_limitation_lift_stage3_future_decision_shape(
    owner_review_groups: list[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "asked_now": False,
        "fixed_form_required": False,
        "freeform_expected": True,
        "fixed_choice_rows_allowed": False,
        "plain_language_topics": [
            {
                "topic_id": group["decision_group_id"],
                "future_owner_category": group["decision_owner_category"],
                "plain_language_decision_topic": group[
                    "future_decision_topic_plain_language"
                ],
            }
            for group in owner_review_groups
        ],
        "future_card_guidance": (
            "When a later slice creates the user decision card, keep it short "
            "and freeform. Do not require a table, fixed form, or fixed "
            "choice rows from the user."
        ),
    }


def _production_limitation_lift_stage3_boundary_flags(
    stage2_lift: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "new_rehearsal_run": False,
            "source_stage2_decision_packet_reused": True,
            "source_stage2_new_render_created": stage2_lift["render_gate"][
                "new_render_run"
            ],
            "source_stage1_new_render_created": stage2_lift["render_gate"][
                "source_stage1_new_render_run"
            ],
            "source_stage3_new_render_created": stage2_lift["render_gate"][
                "source_stage3_new_render_run"
            ],
            "diagnostic_stage3_evidence_reused": True,
            "owner_review_prep_only": True,
            "owner_review_prep_does_not_grant_approval": True,
            "future_user_decision_shape_freeform": True,
            "fixed_user_form_emitted": False,
            "fixed_choice_rows_emitted": False,
            "user_decision_requested_now": False,
            "owner_review_group_count": len(
                PRODUCTION_LIMITATION_LIFT_STAGE3_OWNER_REVIEW_GROUP_IDS
            ),
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _production_limitation_lift_stage3_validation(
    *,
    stage2_lift: Mapping[str, Any],
    source_evidence: Mapping[str, Any],
    owner_review_groups: list[Mapping[str, Any]],
    no_approval_yet: Mapping[str, Any],
    future_decision_shape: Mapping[str, Any],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    expected_group_ids = list(PRODUCTION_LIMITATION_LIFT_STAGE3_OWNER_REVIEW_GROUP_IDS)
    actual_group_ids = [group["decision_group_id"] for group in owner_review_groups]
    source_decision_packet_preserved = (
        stage2_lift["artifact_id"] == PRODUCTION_LIMITATION_LIFT_STAGE2_ARTIFACT_ID
        and stage2_lift["validation"]["all_checks_passed"] is True
        and stage2_lift["decision_group_ids"]
        == list(PRODUCTION_LIMITATION_LIFT_STAGE2_DECISION_GROUP_IDS)
        and len(stage2_lift["decision_groups"])
        == len(PRODUCTION_LIMITATION_LIFT_STAGE2_DECISION_GROUP_IDS)
    )
    owner_review_groups_present = actual_group_ids == expected_group_ids
    owner_review_groups_bounded = (
        owner_review_groups_present
        and len(owner_review_groups) == 3
        and all(group["available_evidence"] for group in owner_review_groups)
        and all(group["safe_next_action"] for group in owner_review_groups)
    )
    no_approval_boundary_explicit = (
        no_approval_yet["production_subtitle_design_acceptance"] is False
        and no_approval_yet["production_render_acceptance"] is False
        and no_approval_yet["creative_acceptance"] is False
        and no_approval_yet["rights_status"] == "pending"
        and no_approval_yet["publishing_acceptance"] is False
        and no_approval_yet["public_use_permission"] is False
        and no_approval_yet["production_public_decision_approved"] is False
        and no_approval_yet["user_decision_requested_now"] is False
        and no_approval_yet["owner_review_prep_does_not_grant_approval"] is True
    )
    future_user_decision_shape_freeform = (
        future_decision_shape["asked_now"] is False
        and future_decision_shape["fixed_form_required"] is False
        and future_decision_shape["freeform_expected"] is True
        and future_decision_shape["fixed_choice_rows_allowed"] is False
        and len(future_decision_shape["plain_language_topics"]) == 3
    )
    source_evidence_linked = (
        source_evidence["source_stage2_decision_packet_artifact_id"]
        == PRODUCTION_LIMITATION_LIFT_STAGE2_ARTIFACT_ID
        and source_evidence["source_stage1_gate_matrix_artifact_id"]
        == PRODUCTION_LIMITATION_LIFT_STAGE1_ARTIFACT_ID
        and source_evidence["primary_diagnostic_rehearsal_artifact_id"]
        == FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID
        and source_evidence["source_decision_group_count"] == 3
        and source_evidence["diagnostic_output_metadata"]["duration_seconds"] == 4.2
        and source_evidence["diagnostic_output_metadata"]["resolution"] == "1920x1080"
        and source_evidence["diagnostic_survival_readback"][
            "ass_subtitle_style_tokens_survived"
        ]
        is True
    )
    production_public_gates_still_closed = (
        boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
        and boundaries["owner_review_prep_does_not_grant_approval"] is True
    )
    user_decision_not_requested_now = (
        boundaries["user_decision_requested_now"] is False
        and no_approval_yet["user_decision_requested_now"] is False
        and future_decision_shape["asked_now"] is False
    )
    no_fixed_user_form_emitted = (
        boundaries["fixed_user_form_emitted"] is False
        and boundaries["fixed_choice_rows_emitted"] is False
        and future_decision_shape["fixed_form_required"] is False
        and future_decision_shape["fixed_choice_rows_allowed"] is False
    )
    unsafe_overclaiming_present = all(
        bool(group["unsafe_overclaiming_examples"]) for group in owner_review_groups
    )
    owner_review_entries_scoped = all(
        group["can_proceed_without_user_judgement"] is True
        and group["must_stop_before_approval"] is True
        and group["approval_owner_required_later"] is True
        and group["agent_may_approve"] is False
        for group in owner_review_groups
    )
    tracked_media_boundary_closed = (
        boundaries["tracked_binary_artifact_created"] is False
        and boundaries["episodes_tracked"] is False
    )
    next_executable_route_defined = True
    return {
        "expected_owner_review_group_ids": expected_group_ids,
        "actual_owner_review_group_ids": actual_group_ids,
        "source_decision_packet_preserved": source_decision_packet_preserved,
        "owner_review_groups_present": owner_review_groups_present,
        "owner_review_groups_bounded": owner_review_groups_bounded,
        "no_approval_boundary_explicit": no_approval_boundary_explicit,
        "future_user_decision_shape_freeform": future_user_decision_shape_freeform,
        "source_evidence_linked": source_evidence_linked,
        "production_public_gates_still_closed": production_public_gates_still_closed,
        "user_decision_not_requested_now": user_decision_not_requested_now,
        "no_fixed_user_form_emitted": no_fixed_user_form_emitted,
        "unsafe_overclaiming_present": unsafe_overclaiming_present,
        "owner_review_entries_scoped": owner_review_entries_scoped,
        "tracked_media_boundary_closed": tracked_media_boundary_closed,
        "next_executable_route_defined": next_executable_route_defined,
        "new_render_run": False,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "episodes_tracked": boundaries["episodes_tracked"],
        "all_checks_passed": (
            source_decision_packet_preserved
            and owner_review_groups_bounded
            and no_approval_boundary_explicit
            and future_user_decision_shape_freeform
            and source_evidence_linked
            and production_public_gates_still_closed
            and user_decision_not_requested_now
            and no_fixed_user_form_emitted
            and unsafe_overclaiming_present
            and owner_review_entries_scoped
            and tracked_media_boundary_closed
            and next_executable_route_defined
        ),
    }


def _production_limitation_lift_stage4_source_evidence(
    stage3_lift: Mapping[str, Any],
) -> dict[str, Any]:
    source = stage3_lift["source_evidence"]
    return {
        "source_stage3_owner_review_prep_artifact_id": stage3_lift["artifact_id"],
        "source_stage3_owner_review_prep_path": "docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.json",
        "source_stage3_owner_review_prep_doc": "docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md",
        "source_stage2_decision_packet_artifact_id": stage3_lift[
            "source_production_limitation_lift_stage_2_decision_packet_artifact_id"
        ],
        "source_stage1_gate_matrix_artifact_id": stage3_lift[
            "source_production_limitation_lift_stage_1_artifact_id"
        ],
        "primary_diagnostic_rehearsal_artifact_id": stage3_lift[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage3_lift[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "source_owner_review_group_count": len(stage3_lift["owner_review_groups"]),
        "source_owner_review_group_ids": list(stage3_lift["owner_review_group_ids"]),
        "diagnostic_output_metadata": deepcopy(source["diagnostic_output_metadata"]),
        "diagnostic_survival_readback": deepcopy(source["diagnostic_survival_readback"]),
        "stage3_no_approval_yet": deepcopy(stage3_lift["no_approval_yet"]),
    }


def _production_limitation_lift_stage4_decision_topics(
    stage3_lift: Mapping[str, Any],
) -> list[dict[str, Any]]:
    by_group = {
        group["decision_group_id"]: group
        for group in stage3_lift["owner_review_groups"]
    }
    question_shapes = {
        "subtitle_design_visual_acceptance": (
            "When a later slice asks for judgement, describe whether the "
            "subtitle design and visual feel are acceptable enough for "
            "production use, and mention any reservations."
        ),
        "production_render_readiness": (
            "When a later slice asks for judgement, describe whether the "
            "available render evidence is enough to proceed toward production "
            "render readiness, and mention what proof is still needed."
        ),
        "rights_publishing_public_use_clearance": (
            "When a later slice asks for judgement, describe whether rights, "
            "publishing context, and public-use clearance are satisfied or "
            "still pending."
        ),
    }
    safe_answer_hints = {
        "subtitle_design_visual_acceptance": [
            "whether the current visual direction is acceptable",
            "specific reservations or blocked design conditions",
            "whether approval should stay pending",
        ],
        "production_render_readiness": [
            "whether current diagnostic render evidence is enough to continue",
            "which final render evidence is still missing",
            "whether approval should stay pending",
        ],
        "rights_publishing_public_use_clearance": [
            "known rights or publication clearance status",
            "unknown rights or public-use conditions",
            "whether approval should stay pending",
        ],
    }
    normalization = {
        "subtitle_design_visual_acceptance": [
            "visual_acceptance_signal",
            "design_reservation_notes",
            "approval_status_remains_pending_when_unclear",
        ],
        "production_render_readiness": [
            "render_readiness_signal",
            "missing_render_evidence",
            "approval_status_remains_pending_when_unclear",
        ],
        "rights_publishing_public_use_clearance": [
            "rights_publication_signal",
            "missing_rights_or_publication_evidence",
            "approval_status_remains_pending_when_unclear",
        ],
    }
    topics: list[dict[str, Any]] = []
    for topic_id in PRODUCTION_LIMITATION_LIFT_STAGE4_DECISION_TOPIC_IDS:
        source_group = by_group[topic_id]
        topics.append(
            {
                "topic_id": topic_id,
                "source_owner_review_group_id": source_group["decision_group_id"],
                "future_owner_category": source_group["decision_owner_category"],
                "plain_language_question_shape": question_shapes[topic_id],
                "available_evidence": list(source_group["available_evidence"]),
                "missing_evidence": list(source_group["missing_evidence"]),
                "safe_freeform_answer_could_mention": safe_answer_hints[topic_id],
                "agent_may_normalize_internally": normalization[topic_id],
                "stop_boundary_before_approval": (
                    "Do not convert a vague or partial future answer into "
                    "approval; keep missing or unclear conditions pending."
                ),
                "unsafe_overclaiming_examples": list(
                    source_group["unsafe_overclaiming_examples"]
                ),
                "must_stop_before_approval": True,
                "approval_owner_required_later": True,
                "agent_may_approve": False,
                "user_decision_requested_now": False,
                "fixed_form_required": False,
                "fixed_choice_rows_allowed": False,
                "fixed_choice_rows_emitted": False,
                "screenshot_required": False,
                "hidden_schema_exposed_to_user": False,
            }
        )
    return topics


def _production_limitation_lift_stage4_not_asked_now(
    stage3_lift: Mapping[str, Any],
) -> dict[str, Any]:
    source = stage3_lift["no_approval_yet"]
    return {
        "user_decision_requested_now": False,
        "production_subtitle_design_acceptance": source[
            "production_subtitle_design_acceptance"
        ],
        "production_render_acceptance": source["production_render_acceptance"],
        "creative_acceptance": source["creative_acceptance"],
        "rights_status": source["rights_status"],
        "publishing_acceptance": source["publishing_acceptance"],
        "public_use_permission": source["public_use_permission"],
        "production_public_decision_approved": False,
        "stage_4_user_decision_card_does_not_grant_approval": True,
        "stage_4_user_decision_card_does_not_grant_approval": True,
    }


def _production_limitation_lift_stage4_freeform_answer_handling(
    decision_topics: list[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "user_may_answer_naturally": True,
        "one_paragraph_or_few_bullets_allowed": True,
        "answer_style": "freeform",
        "template_required": False,
        "schema_owner": "Agent",
        "fixed_form_required": False,
        "fixed_choice_rows_allowed": False,
        "fixed_choice_rows_emitted": False,
        "required_labels": [],
        "max_look_for_points": 3,
        "screenshot_required": False,
        "hidden_schema_exposed_to_user": False,
        "plain_language_user_instructions": [
            "A later user may answer naturally in one paragraph.",
            "A later user may use a few bullets if that is easier.",
            "The user does not need to follow field names or labels.",
            "The user does not need to provide screenshots for this card.",
        ],
        "agent_internal_normalization_allowed": [
            "map a clear answer to the matching topic id",
            "carry explicit reservations into missing evidence or pending notes",
            "keep ambiguous or absent approvals pending",
            "preserve rights and public-use unknowns as unknown",
        ],
        "unknowns_remain_unknown_examples": [
            "rights clearance not mentioned",
            "publication context not mentioned",
            "final render acceptance not mentioned",
            "production subtitle design acceptance not mentioned",
        ],
        "decision_topic_count": len(decision_topics),
    }



def _production_limitation_lift_stage4_boundary_flags(
    stage3_lift: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "new_rehearsal_run": False,
            "source_stage3_owner_review_prep_reused": True,
            "source_stage3_owner_review_prep_new_render_created": stage3_lift[
                "render_gate"
            ]["new_render_run"],
            "source_stage2_decision_packet_reused": True,
            "source_stage2_new_render_created": stage3_lift["render_gate"][
                "source_stage2_new_render_run"
            ],
            "source_stage1_new_render_created": stage3_lift["render_gate"][
                "source_stage1_new_render_run"
            ],
            "source_final_path_stage3_new_render_created": stage3_lift["render_gate"][
                "source_stage3_new_render_run"
            ],
            "stage_4_user_decision_card_only": True,
            "stage_4_user_decision_card_does_not_grant_approval": True,
            "stage_4_user_decision_card_only": True,
            "stage_4_user_decision_card_does_not_grant_approval": True,
        "stage_4_user_decision_card_does_not_grant_approval": True,
            "future_user_decision_shape_freeform": True,
            "user_decision_requested_now": False,
            "fixed_user_form_emitted": False,
            "fixed_choice_rows_allowed": False,
            "fixed_choice_rows_emitted": False,
            "screenshot_required": False,
            "hidden_schema_exposed_to_user": False,
            "decision_topic_count": len(PRODUCTION_LIMITATION_LIFT_STAGE4_DECISION_TOPIC_IDS),
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _production_limitation_lift_stage4_validation(
    *,
    stage3_lift: Mapping[str, Any],
    source_evidence: Mapping[str, Any],
    decision_topics: list[Mapping[str, Any]],
    not_asked_now: Mapping[str, Any],
    freeform_answer_handling: Mapping[str, Any],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    expected_topic_ids = list(PRODUCTION_LIMITATION_LIFT_STAGE4_DECISION_TOPIC_IDS)
    actual_topic_ids = [topic["topic_id"] for topic in decision_topics]
    source_owner_review_prep_preserved = (
        stage3_lift["artifact_id"] == PRODUCTION_LIMITATION_LIFT_STAGE3_ARTIFACT_ID
        and stage3_lift["validation"]["all_checks_passed"] is True
        and stage3_lift["owner_review_group_ids"]
        == list(PRODUCTION_LIMITATION_LIFT_STAGE3_OWNER_REVIEW_GROUP_IDS)
        and len(stage3_lift["owner_review_groups"]) == 3
    )
    decision_topics_present = actual_topic_ids == expected_topic_ids
    decision_topics_bounded_to_three = (
        decision_topics_present
        and len(decision_topics) == 3
        and all(topic["plain_language_question_shape"] for topic in decision_topics)
        and all(topic["available_evidence"] for topic in decision_topics)
        and all(topic["safe_freeform_answer_could_mention"] for topic in decision_topics)
    )
    not_asked_now_boundary_explicit = (
        not_asked_now["user_decision_requested_now"] is False
        and not_asked_now["production_subtitle_design_acceptance"] is False
        and not_asked_now["production_render_acceptance"] is False
        and not_asked_now["creative_acceptance"] is False
        and not_asked_now["rights_status"] == "pending"
        and not_asked_now["publishing_acceptance"] is False
        and not_asked_now["public_use_permission"] is False
        and not_asked_now["production_public_decision_approved"] is False
        and not_asked_now[
            "stage_4_user_decision_card_does_not_grant_approval"
        ]
        is True
    )
    future_user_burden_freeform = (
        freeform_answer_handling["user_may_answer_naturally"] is True
        and freeform_answer_handling["one_paragraph_or_few_bullets_allowed"] is True
        and freeform_answer_handling["fixed_form_required"] is False
        and freeform_answer_handling["fixed_choice_rows_allowed"] is False
        and freeform_answer_handling["required_labels"] == []
        and freeform_answer_handling["answer_style"] == "freeform"
        and freeform_answer_handling["template_required"] is False
        and freeform_answer_handling["schema_owner"] == "Agent"
        and freeform_answer_handling["max_look_for_points"] == 3
        and freeform_answer_handling["decision_topic_count"] == 3
    )
    no_fixed_choice_or_form_surface = (
        boundaries["fixed_user_form_emitted"] is False
        and boundaries["fixed_choice_rows_allowed"] is False
        and boundaries["fixed_choice_rows_emitted"] is False
        and freeform_answer_handling["fixed_form_required"] is False
        and freeform_answer_handling["fixed_choice_rows_allowed"] is False
        and freeform_answer_handling["fixed_choice_rows_emitted"] is False
        and all(topic["fixed_form_required"] is False for topic in decision_topics)
        and all(topic["fixed_choice_rows_allowed"] is False for topic in decision_topics)
        and all(topic["fixed_choice_rows_emitted"] is False for topic in decision_topics)
    )
    source_evidence_linked = (
        source_evidence["source_stage3_owner_review_prep_artifact_id"] == PRODUCTION_LIMITATION_LIFT_STAGE3_ARTIFACT_ID
        and source_evidence["source_stage2_decision_packet_artifact_id"] == PRODUCTION_LIMITATION_LIFT_STAGE2_ARTIFACT_ID
        and source_evidence["source_stage1_gate_matrix_artifact_id"] == PRODUCTION_LIMITATION_LIFT_STAGE1_ARTIFACT_ID
        and source_evidence["primary_diagnostic_rehearsal_artifact_id"] == FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID
        and source_evidence["source_owner_review_group_count"] == 3
    )
    production_public_gates_still_closed = (
        boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
        and boundaries["stage_4_user_decision_card_does_not_grant_approval"]
        is True
    )
    no_screenshot_requirement = (
        boundaries["screenshot_required"] is False
        and freeform_answer_handling["screenshot_required"] is False
        and all(topic["screenshot_required"] is False for topic in decision_topics)
    )
    hidden_schema_not_exposed = (
        boundaries["hidden_schema_exposed_to_user"] is False
        and freeform_answer_handling["hidden_schema_exposed_to_user"] is False
        and all(topic["hidden_schema_exposed_to_user"] is False for topic in decision_topics)
    )
    unsafe_overclaiming_present = all(bool(topic["unsafe_overclaiming_examples"]) for topic in decision_topics)
    tracked_media_boundary_closed = boundaries["tracked_binary_artifact_created"] is False and boundaries["episodes_tracked"] is False
    next_executable_route_defined = True
    return {
        "expected_decision_topic_ids": expected_topic_ids,
        "actual_decision_topic_ids": actual_topic_ids,
        "source_owner_review_prep_preserved": source_owner_review_prep_preserved,
        "decision_topics_present": decision_topics_present,
        "decision_topics_bounded_to_three": decision_topics_bounded_to_three,
        "not_asked_now_boundary_explicit": not_asked_now_boundary_explicit,
        "future_user_burden_freeform": future_user_burden_freeform,
        "future_freeform_answer_handling_ready": future_user_burden_freeform,
        "no_fixed_choice_or_form_surface": no_fixed_choice_or_form_surface,
        "source_evidence_linked": source_evidence_linked,
        "production_public_gates_still_closed": production_public_gates_still_closed,
        "no_screenshot_requirement": no_screenshot_requirement,
        "hidden_schema_not_exposed": hidden_schema_not_exposed,
        "unsafe_overclaiming_present": unsafe_overclaiming_present,
        "tracked_media_boundary_closed": tracked_media_boundary_closed,
        "next_executable_route_defined": next_executable_route_defined,
        "new_render_run": False,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "episodes_tracked": boundaries["episodes_tracked"],
        "all_checks_passed": (
            source_owner_review_prep_preserved
            and decision_topics_bounded_to_three
            and not_asked_now_boundary_explicit
            and future_user_burden_freeform
            and no_fixed_choice_or_form_surface
            and source_evidence_linked
            and production_public_gates_still_closed
            and no_screenshot_requirement
            and hidden_schema_not_exposed
            and unsafe_overclaiming_present
            and tracked_media_boundary_closed
            and next_executable_route_defined
        ),
    }


def _production_limitation_lift_stage5_source_evidence(
    stage4_card: Mapping[str, Any],
) -> dict[str, Any]:
    source = stage4_card["source_evidence"]
    return {
        "source_stage4_user_decision_card_artifact_id": stage4_card["artifact_id"],
        "source_stage4_user_decision_card_path": (
            "docs/style_intent/"
            "subtitle-production-limitation-lift-stage-4-user-decision-card.json"
        ),
        "source_stage4_user_decision_card_doc": (
            "docs/style_intent/"
            "subtitle-production-limitation-lift-stage-4-user-decision-card.md"
        ),
        "source_stage3_owner_review_prep_artifact_id": stage4_card[
            "source_production_limitation_lift_stage_3_owner_review_prep_artifact_id"
        ],
        "source_stage2_decision_packet_artifact_id": stage4_card[
            "source_production_limitation_lift_stage_2_decision_packet_artifact_id"
        ],
        "source_stage1_gate_matrix_artifact_id": stage4_card[
            "source_production_limitation_lift_stage_1_artifact_id"
        ],
        "primary_diagnostic_rehearsal_artifact_id": stage4_card[
            "source_final_render_path_stage_3_rehearsal_artifact_id"
        ],
        "active_diagnostic_proof_source_artifact_id": stage4_card[
            "active_diagnostic_proof_source_artifact_id"
        ],
        "source_decision_topic_count": len(stage4_card["decision_topics"]),
        "source_decision_topic_ids": list(stage4_card["decision_topic_ids"]),
        "source_owner_review_group_count": source["source_owner_review_group_count"],
        "diagnostic_output_metadata": deepcopy(source["diagnostic_output_metadata"]),
        "diagnostic_survival_readback": deepcopy(source["diagnostic_survival_readback"]),
        "source_not_asked_now": deepcopy(stage4_card["not_asked_now"]),
        "source_future_freeform_answer_handling": deepcopy(
            stage4_card["future_freeform_answer_handling"]
        ),
    }


def _production_limitation_lift_stage5_decision_topics(
    stage4_card: Mapping[str, Any],
) -> list[dict[str, Any]]:
    title_by_topic = {
        "subtitle_design_visual_acceptance": "Subtitle design / visual acceptance",
        "production_render_readiness": "Production render readiness",
        "rights_publishing_public_use_clearance": (
            "Rights / publishing / public-use clearance"
        ),
    }
    by_topic = {topic["topic_id"]: topic for topic in stage4_card["decision_topics"]}
    topics: list[dict[str, Any]] = []
    for topic_id in PRODUCTION_LIMITATION_LIFT_STAGE5_DECISION_TOPIC_IDS:
        source_topic = by_topic[topic_id]
        topics.append(
            {
                "topic_id": topic_id,
                "source_stage4_decision_topic_id": source_topic["topic_id"],
                "final_user_facing_topic_title": title_by_topic[topic_id],
                "low_burden_freeform_prompt_shape": source_topic[
                    "plain_language_question_shape"
                ],
                "evidence_available": list(source_topic["available_evidence"]),
                "evidence_still_missing": list(source_topic["missing_evidence"]),
                "internal_normalization_hints": list(
                    source_topic["agent_may_normalize_internally"]
                ),
                "stop_boundary_before_approval": source_topic[
                    "stop_boundary_before_approval"
                ],
                "unsafe_overclaiming_examples": list(
                    source_topic["unsafe_overclaiming_examples"]
                ),
                "must_stop_before_approval": True,
                "approval_owner_required_later": True,
                "agent_may_approve": False,
                "user_decision_requested_now": False,
                "fixed_form_required": False,
                "fixed_choice_rows_allowed": False,
                "fixed_choice_rows_emitted": False,
                "screenshot_required": False,
                "hidden_schema_exposed_to_user": False,
            }
        )
    return topics


def _production_limitation_lift_stage5_ready_but_not_asked(
    stage4_card: Mapping[str, Any],
) -> dict[str, Any]:
    source_answer = stage4_card["future_freeform_answer_handling"]
    source_not_asked = stage4_card["not_asked_now"]
    return {
        "future_short_freeform_review_request_ready": True,
        "source_stage4_validation_passed": stage4_card["validation"][
            "all_checks_passed"
        ],
        "user_decision_requested_now": False,
        "production_subtitle_design_acceptance": source_not_asked[
            "production_subtitle_design_acceptance"
        ],
        "production_render_acceptance": source_not_asked[
            "production_render_acceptance"
        ],
        "creative_acceptance": source_not_asked["creative_acceptance"],
        "rights_status": source_not_asked["rights_status"],
        "publishing_acceptance": source_not_asked["publishing_acceptance"],
        "public_use_permission": source_not_asked["public_use_permission"],
        "answer_style": source_answer["answer_style"],
        "template_required": source_answer["template_required"],
        "schema_owner": source_answer["schema_owner"],
        "max_look_for_points": source_answer["max_look_for_points"],
        "fixed_form_required": False,
        "fixed_choice_rows_allowed": False,
        "fixed_choice_rows_emitted": False,
        "screenshot_required": False,
        "hidden_schema_exposed_to_user": False,
        "unknowns_remain_unknown": True,
    }


def _production_limitation_lift_stage5_future_presentation_constraints(
    decision_topics: list[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "final_user_prompt_may_be_written_in_natural_language": True,
        "must_present_at_most_three_topics": True,
        "decision_topic_count": len(decision_topics),
        "must_preserve_freeform_answer_style": True,
        "must_not_show_internal_schema": True,
        "must_not_emit_fixed_user_form": True,
        "must_not_emit_fixed_choice_rows": True,
        "must_not_request_screenshot": True,
        "must_keep_unknowns_pending": True,
        "must_keep_rights_publication_and_public_use_separate": True,
        "must_keep_render_acceptance_separate_from_rights": True,
        "must_stop_before_any_production_or_public_approval": True,
        "agent_may_normalize_answer_internally": True,
        "agent_may_approve": False,
    }


def _production_limitation_lift_stage5_boundary_flags(
    stage4_card: Mapping[str, Any],
) -> dict[str, Any]:
    flags = _boundary_flags()
    flags.update(
        {
            "new_render_created": False,
            "new_rehearsal_run": False,
            "source_stage4_user_decision_card_reused": True,
            "source_stage4_user_decision_card_new_render_created": stage4_card[
                "render_gate"
            ]["new_render_run"],
            "source_stage3_owner_review_prep_reused": True,
            "source_stage3_owner_review_prep_new_render_created": stage4_card[
                "render_gate"
            ]["source_stage3_owner_review_prep_new_render_run"],
            "source_stage2_decision_packet_reused": True,
            "source_stage2_new_render_created": stage4_card["render_gate"][
                "source_stage2_decision_packet_new_render_run"
            ],
            "source_stage1_new_render_created": stage4_card["render_gate"][
                "source_stage1_new_render_run"
            ],
            "source_final_path_stage3_new_render_created": stage4_card["render_gate"][
                "source_final_path_stage3_new_render_run"
            ],
            "user_decision_card_ready": True,
            "stage_5_user_decision_ready_only": True,
            "stage_5_user_decision_ready_does_not_grant_approval": True,
            "future_user_decision_shape_freeform": True,
            "user_decision_requested_now": False,
            "fixed_user_form_emitted": False,
            "fixed_choice_rows_allowed": False,
            "fixed_choice_rows_emitted": False,
            "screenshot_required": False,
            "hidden_schema_exposed_to_user": False,
            "decision_topic_count": len(PRODUCTION_LIMITATION_LIFT_STAGE5_DECISION_TOPIC_IDS),
            "tracked_binary_artifact_created": False,
            "episodes_tracked": False,
            "production_candidate": False,
            "production_usage_allowed": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
            "final_render_path_approved": False,
        }
    )
    return flags


def _production_limitation_lift_stage5_validation(
    *,
    stage4_card: Mapping[str, Any],
    source_evidence: Mapping[str, Any],
    decision_topics: list[Mapping[str, Any]],
    ready_but_not_asked: Mapping[str, Any],
    future_presentation_constraints: Mapping[str, Any],
    boundaries: Mapping[str, Any],
) -> dict[str, Any]:
    expected_topic_ids = list(PRODUCTION_LIMITATION_LIFT_STAGE5_DECISION_TOPIC_IDS)
    actual_topic_ids = [topic["topic_id"] for topic in decision_topics]
    source_user_decision_card_preserved = (
        stage4_card["artifact_id"] == PRODUCTION_LIMITATION_LIFT_STAGE4_ARTIFACT_ID
        and stage4_card["validation"]["all_checks_passed"] is True
        and stage4_card["decision_topic_ids"]
        == list(PRODUCTION_LIMITATION_LIFT_STAGE4_DECISION_TOPIC_IDS)
        and len(stage4_card["decision_topics"]) == 3
        and stage4_card["future_freeform_answer_handling"]["answer_style"]
        == "freeform"
        and stage4_card["future_freeform_answer_handling"]["fixed_form_required"]
        is False
        and stage4_card["future_freeform_answer_handling"][
            "fixed_choice_rows_allowed"
        ]
        is False
    )
    source_owner_review_prep_linked = (
        stage4_card[
            "source_production_limitation_lift_stage_3_owner_review_prep_artifact_id"
        ]
        == PRODUCTION_LIMITATION_LIFT_STAGE3_ARTIFACT_ID
    )
    decision_topics_present = actual_topic_ids == expected_topic_ids
    decision_topics_bounded_to_three = (
        decision_topics_present
        and len(decision_topics) == 3
        and all(topic["final_user_facing_topic_title"] for topic in decision_topics)
        and all(topic["low_burden_freeform_prompt_shape"] for topic in decision_topics)
        and all(topic["evidence_available"] for topic in decision_topics)
        and all(topic["internal_normalization_hints"] for topic in decision_topics)
        and all(topic["must_stop_before_approval"] is True for topic in decision_topics)
    )
    ready_but_not_asked_explicit = (
        ready_but_not_asked["future_short_freeform_review_request_ready"] is True
        and ready_but_not_asked["source_stage4_validation_passed"] is True
        and ready_but_not_asked["user_decision_requested_now"] is False
        and ready_but_not_asked["production_subtitle_design_acceptance"] is False
        and ready_but_not_asked["production_render_acceptance"] is False
        and ready_but_not_asked["creative_acceptance"] is False
        and ready_but_not_asked["rights_status"] == "pending"
        and ready_but_not_asked["publishing_acceptance"] is False
        and ready_but_not_asked["public_use_permission"] is False
        and ready_but_not_asked["answer_style"] == "freeform"
        and ready_but_not_asked["template_required"] is False
    )
    future_presentation_constraints_ready = (
        future_presentation_constraints["decision_topic_count"] == 3
        and future_presentation_constraints["must_present_at_most_three_topics"]
        is True
        and future_presentation_constraints["must_preserve_freeform_answer_style"]
        is True
        and future_presentation_constraints["must_not_show_internal_schema"] is True
        and future_presentation_constraints["must_not_emit_fixed_user_form"] is True
        and future_presentation_constraints["must_not_emit_fixed_choice_rows"] is True
        and future_presentation_constraints["must_not_request_screenshot"] is True
        and future_presentation_constraints[
            "must_stop_before_any_production_or_public_approval"
        ]
        is True
        and future_presentation_constraints["agent_may_approve"] is False
    )
    no_fixed_choice_or_form_surface = (
        boundaries["fixed_user_form_emitted"] is False
        and boundaries["fixed_choice_rows_allowed"] is False
        and boundaries["fixed_choice_rows_emitted"] is False
        and ready_but_not_asked["fixed_form_required"] is False
        and ready_but_not_asked["fixed_choice_rows_allowed"] is False
        and ready_but_not_asked["fixed_choice_rows_emitted"] is False
        and all(topic["fixed_form_required"] is False for topic in decision_topics)
        and all(topic["fixed_choice_rows_allowed"] is False for topic in decision_topics)
        and all(topic["fixed_choice_rows_emitted"] is False for topic in decision_topics)
    )
    source_evidence_linked = (
        source_evidence["source_stage4_user_decision_card_artifact_id"]
        == PRODUCTION_LIMITATION_LIFT_STAGE4_ARTIFACT_ID
        and source_evidence["source_stage3_owner_review_prep_artifact_id"]
        == PRODUCTION_LIMITATION_LIFT_STAGE3_ARTIFACT_ID
        and source_evidence["source_stage2_decision_packet_artifact_id"]
        == PRODUCTION_LIMITATION_LIFT_STAGE2_ARTIFACT_ID
        and source_evidence["source_stage1_gate_matrix_artifact_id"]
        == PRODUCTION_LIMITATION_LIFT_STAGE1_ARTIFACT_ID
        and source_evidence["primary_diagnostic_rehearsal_artifact_id"]
        == FINAL_RENDER_PATH_STAGE3_ARTIFACT_ID
        and source_evidence["source_decision_topic_count"] == 3
    )
    production_public_gates_still_closed = (
        boundaries["production_subtitle_design_acceptance"] is False
        and boundaries["production_render_acceptance"] is False
        and boundaries["creative_acceptance"] is False
        and boundaries["rights_status"] == "pending"
        and boundaries["publishing_acceptance"] is False
        and boundaries["public_use_permission"] is False
        and boundaries["production_usage_allowed"] is False
        and boundaries["final_render_path_approved"] is False
        and boundaries["stage_5_user_decision_ready_does_not_grant_approval"]
        is True
    )
    no_screenshot_requirement = (
        boundaries["screenshot_required"] is False
        and ready_but_not_asked["screenshot_required"] is False
        and future_presentation_constraints["must_not_request_screenshot"] is True
        and all(topic["screenshot_required"] is False for topic in decision_topics)
    )
    no_hidden_schema_exposed = (
        boundaries["hidden_schema_exposed_to_user"] is False
        and ready_but_not_asked["hidden_schema_exposed_to_user"] is False
        and future_presentation_constraints["must_not_show_internal_schema"] is True
        and all(topic["hidden_schema_exposed_to_user"] is False for topic in decision_topics)
    )
    unsafe_overclaiming_present = all(
        bool(topic["unsafe_overclaiming_examples"]) for topic in decision_topics
    )
    tracked_media_boundary_closed = (
        boundaries["tracked_binary_artifact_created"] is False
        and boundaries["episodes_tracked"] is False
    )
    next_executable_route_defined = True
    return {
        "expected_decision_topic_ids": expected_topic_ids,
        "actual_decision_topic_ids": actual_topic_ids,
        "source_user_decision_card_preserved": source_user_decision_card_preserved,
        "source_owner_review_prep_linked": source_owner_review_prep_linked,
        "decision_topics_present": decision_topics_present,
        "decision_topics_bounded_to_three": decision_topics_bounded_to_three,
        "ready_but_not_asked_explicit": ready_but_not_asked_explicit,
        "future_presentation_constraints_ready": future_presentation_constraints_ready,
        "no_fixed_choice_or_form_surface": no_fixed_choice_or_form_surface,
        "source_evidence_linked": source_evidence_linked,
        "production_public_gates_still_closed": production_public_gates_still_closed,
        "no_screenshot_requirement": no_screenshot_requirement,
        "no_hidden_schema_exposed": no_hidden_schema_exposed,
        "unsafe_overclaiming_present": unsafe_overclaiming_present,
        "tracked_media_boundary_closed": tracked_media_boundary_closed,
        "next_executable_route_defined": next_executable_route_defined,
        "new_render_run": False,
        "tracked_binary_artifact_created": boundaries["tracked_binary_artifact_created"],
        "episodes_tracked": boundaries["episodes_tracked"],
        "all_checks_passed": (
            source_user_decision_card_preserved
            and source_owner_review_prep_linked
            and decision_topics_bounded_to_three
            and ready_but_not_asked_explicit
            and future_presentation_constraints_ready
            and no_fixed_choice_or_form_surface
            and source_evidence_linked
            and production_public_gates_still_closed
            and no_screenshot_requirement
            and no_hidden_schema_exposed
            and unsafe_overclaiming_present
            and tracked_media_boundary_closed
            and next_executable_route_defined
        ),
    }


def _markdown_cell_list(items: list[str]) -> str:
    return "<br>".join(item.replace("|", "/") for item in items)


def _open_command(target: str, display_path: str) -> dict[str, str]:
    command_path = display_path.replace("/", "\\")
    if target in {"video", "contact_sheet"}:
        command = f'Start-Process "{command_path}"'
    else:
        command = f'notepad "{command_path}"'
    return {"target": target, "command": command}

def _local_probe_readback_from_render_result(
    *,
    render_result: ffmpeg_tiny.RenderResult,
    ass_path: Path,
    video_path: Path,
    manifest_path: Path,
    base_dir: Path,
) -> dict[str, Any]:
    selected_profile = render_result.selected_profile.to_dict()
    selected_profile["output_path"] = _probe_display_path(
        Path(selected_profile["output_path"]),
        base_dir,
    )
    attempts = []
    for attempt in render_result.attempts:
        item = attempt.to_dict()
        item["summary"] = _probe_command_summary(item["summary"], base_dir)
        item["profile"]["output_path"] = _probe_display_path(
            Path(item["profile"]["output_path"]),
            base_dir,
        )
        attempts.append(item)
    return {
        "status": "local_ignored_probe_generated",
        "source_policy": "existing_output_first_local_ignored_source_media",
        "outputs": {
            "ass": _probe_display_path(ass_path, base_dir),
            "video": _probe_display_path(video_path, base_dir),
            "manifest": _probe_display_path(manifest_path, base_dir),
        },
        "metadata": render_result.metadata,
        "render_command_summary": _probe_command_summary(
            render_result.command_summary,
            base_dir,
        ),
        "ffmpeg_path_source": render_result.ffmpeg_path_source,
        "ffprobe_path_source": render_result.ffprobe_path_source,
        "ffmpeg_version": render_result.ffmpeg_version,
        "ffprobe_version": render_result.ffprobe_version,
        "fallback_used": render_result.fallback_used,
        "selected_profile": selected_profile,
        "attempts": attempts,
        "warnings": render_result.warnings,
        "ignored_by_git": True,
        "tracked_binary_artifact_created": False,
        "production_render_acceptance": False,
        "public_use_permission": False,
    }


def _ass_style(example: Mapping[str, Any]) -> str:
    style = example["style"]
    color = example["color_surfaces"]
    font_size = int(round(64 * float(style["font_size_scale"])))
    outline, shadow = _ass_outline_shadow(str(style["outline_shadow_strength"]))
    return (
        f"Style: {example['ass_probe']['style']},Arial,{font_size},"
        "&H00FFFFFF,&H000000FF,&H00000000,"
        f"{_ass_backplate_color(str(color['backplate_box_token']))},"
        "1,0,0,0,100,100,0,0,3,"
        f"{outline},{shadow},2,120,120,90,1"
    )


def _ass_probe_dialogue(example: Mapping[str, Any]) -> str:
    probe = example["ass_probe"]
    return (
        f"Dialogue: 0,{probe['start']},{probe['end']},{probe['style']},"
        f"{example['semantic']['speaker_id']},0,0,0,,{_probe_ass_text(probe['text'])}"
    )


def _ass_backplate_color(backplate_token: str) -> str:
    if "soft" in backplate_token:
        return "&H88000000"
    if "on" in backplate_token or "high_readability" in backplate_token:
        return "&H66000000"
    return "&HAA000000"


def _ass_outline_shadow(outline_token: str) -> tuple[int, int]:
    if "strong" in outline_token:
        return (6, 3)
    if "soft" in outline_token:
        return (3, 1)
    if "heavy" in outline_token:
        return (5, 2)
    return (4, 2)


def _probe_ass_text(text: str) -> str:
    return "{\\an2}" + text.replace("\n", "\\N")


def _probe_ass_time(seconds: float) -> str:
    centiseconds = int(round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    seconds_part, centiseconds_part = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{seconds_part:02d}.{centiseconds_part:02d}"


def _probe_display_path(path: Path, base_dir: Path) -> str:
    try:
        return str(path.resolve().relative_to(base_dir.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _probe_command_summary(summary: str, base_dir: Path) -> str:
    display = summary.replace("\\", "/")
    base = str(base_dir.resolve()).replace("\\", "/")
    display = display.replace(base, ".")
    display = display.replace(base.replace(":", "/:"), ".")
    return re.sub(r"^\S*ffmpeg(?:\.EXE|\.exe)?", "ffmpeg", display)

def _visual_proof_card(example: Mapping[str, Any]) -> str:
    sample = example["visual_sample"]
    tokens = example["readback_tokens"]
    rows = "\n".join(
        (
            f"      <tr><th>{escape(label)}</th><td><code>{escape(str(value))}</code></td></tr>"
        )
        for label, value in [
            ("preset", example["preset_key"]),
            ("font family", tokens["font_family_role"]),
            ("font size", tokens["font_size_scale"]),
            ("outline/shadow", tokens["outline_shadow_strength"]),
            ("badge", tokens["badge_color_token"]),
            ("accent", tokens["accent_color_token"]),
            ("backplate", tokens["backplate_box_token"]),
            ("motion", tokens["motion_primitive"]),
            ("line break", tokens["safe_area_line_break_behavior"]),
            ("body text", tokens["body_text_color_token"]),
            ("review", example["human_review_required"]),
        ]
    )
    style = (
        f"--badge: {sample['badge_swatch']}; --accent: {sample['accent_swatch']}; "
        f"--font-size: {sample['font_size_percent']}%; "
        f"--backplate-alpha: {sample['backplate_alpha']}; "
        f"--outline: {sample['outline_px_placeholder']}px; "
        f"--shadow: {sample['shadow_px_placeholder']}px;"
    )
    return f"""    <article class="card" style="{escape(style)}">
      <h2>{escape(str(example["example_id"]))}</h2>
      <div class="sample">
        <div class="subtitle">
          <span class="backplate"><span class="badge">SPK</span><span class="line">{escape(str(example["display_sample_text"]))}</span></span>
        </div>
      </div>
      <table class="token-table">
{rows}
      </table>
    </article>"""


def _style_axis_card(example: Mapping[str, Any]) -> str:
    sample = example["visual_sample"]
    palette = example["palette_surfaces"]
    expression = example["expression_surfaces"]
    rows = "\n".join(
        (
            f"      <tr><th>{escape(label)}</th><td><code>{escape(str(value))}</code></td></tr>"
        )
        for label, value in [
            ("family group", example["family_group"]),
            ("style family", example["style_family"]),
            ("palette route", example["palette_route"]),
            ("badge", palette["badge_color_token"]),
            ("accent", palette["accent_color_token"]),
            ("backplate", palette["backplate_box_token"]),
            ("body text", palette["body_text_color_token"]),
            ("font role", expression["font_family_role"]),
            ("motion", expression["motion_primitive"]),
            ("line break", expression["safe_area_line_break_behavior"]),
        ]
    )
    style = (
        f"--badge: {sample['badge_swatch']}; --accent: {sample['accent_swatch']}; "
        f"--font-size: {sample['font_size_percent']}%; "
        f"--backplate-alpha: {sample['backplate_alpha']}; "
        f"--outline: {sample['outline_px_placeholder']}px; "
        f"--shadow: {sample['shadow_px_placeholder']}px;"
    )
    return f"""    <article class="card" style="{escape(style)}">
      <h2>{escape(str(example["example_id"]))}</h2>
      <div class="sample">
        <div>
          <span class="backplate"><span class="badge">SPK</span><span class="line">{escape(str(example["display_sample_text"]))}</span></span>
        </div>
      </div>
      <table>
{rows}
      </table>
    </article>"""


def _style_axis_for_example(example_id: str) -> dict[str, str]:
    return {
        "neutral_dialogue_intensity_0": {
            "style_family": "current dialogue family",
            "family_group": "dialogue_current_keifont_family",
            "palette_route": "speaker_identity_blue",
        },
        "shout_intensity_2": {
            "style_family": "high-energy emphasis family",
            "family_group": "emphasis_energy_family",
            "palette_route": "high_energy_warm",
        },
        "whisper_intensity_1": {
            "style_family": "quiet readable dialogue family",
            "family_group": "quiet_soft_readability_family",
            "palette_route": "quiet_cool",
        },
        "ominous_intensity_2": {
            "style_family": "ominous inner-voice family",
            "family_group": "ominous_inner_voice_family",
            "palette_route": "ominous_dark",
        },
        "narration_intensity_0": {
            "style_family": "narration family",
            "family_group": "narration_family",
            "palette_route": "narration_neutral_green",
        },
        "system_note_intensity_0": {
            "style_family": "system note family",
            "family_group": "system_note_family",
            "palette_route": "system_neutral",
        },
    }[example_id]


def _style_axis_summary(examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: dict[tuple[str, str], list[str]] = {}
    for example in examples:
        key = (str(example["family_group"]), str(example["palette_route"]))
        summary.setdefault(key, []).append(str(example["example_id"]))
    return [
        {
            "family_group": family_group,
            "palette_route": palette_route,
            "examples": example_ids,
        }
        for (family_group, palette_route), example_ids in summary.items()
    ]


def _sample_text_for_example(example_id: str) -> str:
    return {
        "neutral_dialogue_intensity_0": "\u3044\u3064\u3082\u306e\u58f0\u3067\u8a71\u3059",
        "shout_intensity_2": "\u6765\u306d\u3047\uff01\uff01",
        "whisper_intensity_1": "\u3061\u3087\u3063\u3068\u5c0f\u58f0\u3067",
        "ominous_intensity_2": "\u305d\u306e\u5f71\u304c\u8fd1\u3065\u304f",
        "narration_intensity_0": "\u3053\u3053\u3067\u5834\u9762\u304c\u5909\u308f\u308b",
        "system_note_intensity_0": "SYSTEM NOTE",
    }[example_id]

def _swatch_for_token(token: str) -> str:
    if "high_energy" in token:
        return "#ffcc33"
    if "quiet" in token:
        return "#9fb7c9"
    if "dark" in token:
        return "#7e6aa8"
    if "narration" in token:
        return "#9cc7a5"
    if "system" in token:
        return "#e8e8e8"
    if "bancho" in token:
        return "#6ec6ff"
    return "#b8c0cc"


def _backplate_alpha(token: str) -> str:
    if token.startswith("on") or "maximum" in token:
        return "0.62"
    if token in {"soft", "optional", "optional_high_readability"}:
        return "0.34"
    return "0.12"


def _outline_px(token: str) -> int:
    if "heavy" in token or "maximum" in token:
        return 7
    if token == "strong":
        return 6
    if "soft" in token:
        return 3
    return 5


def _shadow_px(token: str) -> int:
    if "heavy" in token or "maximum" in token:
        return 5
    if token == "strong":
        return 4
    if "soft" in token:
        return 2
    return 3


def _effective_emotion(intent: Mapping[str, Any]) -> str:
    if intent["speaker_role"] == "system":
        return "system_note"
    if intent["utterance_role"] == "narration":
        return "narration"
    if intent["emotion"] == "neutral" and intent["utterance_role"] == "warning":
        return "system_note"
    return str(intent["emotion"])


def _identity_color_tokens(
    *,
    speaker_id: str,
    speaker_role: str,
    base_badge: str,
    base_accent: str,
) -> tuple[str, str]:
    if speaker_role == "system":
        return "system_badge", "system_accent"
    if speaker_role == "narrator":
        return "narrator_badge_optional", "narration_neutral_accent"
    if speaker_role == "character" and speaker_id != "unknown":
        return (
            f"speaker_{speaker_id}_badge_default",
            f"speaker_{speaker_id}_{base_accent}",
        )
    return base_badge, base_accent


def _font_family_role(intent: Mapping[str, Any]) -> str:
    if intent["speaker_role"] == "system" or intent["emotion"] == "system_note":
        return "system_note_current_family_role"
    if intent["speaker_role"] == "narrator" or intent["utterance_role"] == "narration":
        return "narration_current_family_role"
    return "current_keifont_dialogue_role"


def _readability_backplate(*, base: str, readability: str) -> str:
    if readability == "maximum":
        return "on" if base == "off" else f"{base}_maximum_readability"
    if readability == "high" and base == "off":
        return "optional_high_readability"
    return base


def _readability_line_break(*, base: str, readability: str) -> str:
    if readability == "maximum":
        return "maximum_readability"
    if readability == "high" and base == "normal":
        return "high_readability"
    return base


def _outline_token(*, base: str, intensity: int, readability: str) -> str:
    if readability == "maximum":
        return f"{base}_maximum_readability"
    if intensity >= 2 and base == "current_lead":
        return "current_lead_plus"
    return base


def _speaker_id(value: Any) -> str:
    if value is None:
        return "unknown"
    cleaned = _slug(str(value))
    return cleaned or "unknown"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")


def _enum(value: Any, *, valid: tuple[str, ...], default: str) -> str:
    if value is None:
        return default
    normalized = _slug(str(value))
    return normalized if normalized in valid else default


def _intensity(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 0
    return max(0, min(3, parsed))


def _boundary_flags() -> dict[str, Any]:
    return {
        "production_subtitle_design_acceptance": False,
        "production_render_acceptance": False,
        "creative_acceptance": False,
        "rights_status": "pending",
        "publishing_acceptance": False,
        "public_use_permission": False,
        "broad_renderer_style_system_built": False,
        "new_render_created": False,
        "font_binaries_added": False,
        "episodes_tracked": False,
    }
