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
