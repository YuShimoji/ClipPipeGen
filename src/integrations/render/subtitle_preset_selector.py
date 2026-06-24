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

SCHEMA_ID = "clippipegen.subtitle_preset_selector.v1"
ARTIFACT_ID = "clip-ed10ab-subtitle-preset-selector-001"
FEATURE_ID = "ED-10ab"
VISUAL_PROOF_SCHEMA_ID = "clippipegen.subtitle_visual_selector_proof.v1"
VISUAL_PROOF_ARTIFACT_ID = "clip-ed10ac-visual-selector-proof-001"
VISUAL_PROOF_FEATURE_ID = "ED-10ac"
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


def _sample_text_for_example(example_id: str) -> str:
    return {
        "neutral_dialogue_intensity_0": "いつもの声で話す",
        "shout_intensity_2": "来ねぇ！！",
        "whisper_intensity_1": "ちょっと小声で",
        "ominous_intensity_2": "その影が近づく",
        "narration_intensity_0": "ここで場面が変わる",
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
