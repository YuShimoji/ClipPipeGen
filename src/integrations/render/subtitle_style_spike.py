"""Subtitle renderer / typography measurement spike.

This module creates local review artifacts only. The generated PNGs and report
are not production subtitle design or production render acceptance.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover - exercised only on missing optional dep
    Image = None
    ImageDraw = None
    ImageFont = None


PILLOW_OPTIONAL_DEPENDENCY_MESSAGE = (
    "Pillow is an optional local review dependency for subtitle_style_spike; "
    "install Pillow only when generating review-only PNG measurement artifacts. "
    "This spike is not a production renderer dependency."
)
DEFAULT_OUTPUT_DIR = Path(
    "episodes/jp_pilot01_hololive_bancho_20260525/"
    "review/jp_pilot01r3_cut_review/subtitle_style_spike"
)
DEFAULT_TYPOGRAPHY_COMPARISON_OUTPUT_DIR = Path(
    "episodes/jp_pilot01_hololive_bancho_20260525/"
    "review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison"
)
DEFAULT_KIRINUKI_GOTHIC_BALANCE_OUTPUT_DIR = Path(
    "episodes/jp_pilot01_hololive_bancho_20260525/"
    "review/jp_pilot01r3_cut_review/subtitle_kirinuki_gothic_balance_comparison"
)
ED10G_TYPOGRAPHY_DECORATION_PROFILE = "ed10g_typography_decoration"
ED10I_KIRINUKI_GOTHIC_BALANCE_PROFILE = "ed10i_kirinuki_gothic_balance"
TYPOGRAPHY_COMPARISON_PROFILES = (
    ED10G_TYPOGRAPHY_DECORATION_PROFILE,
    ED10I_KIRINUKI_GOTHIC_BALANCE_PROFILE,
)
DEFAULT_CANVAS = (1280, 720)
SAMPLE_TEXTS = (
    "来ねぇ！！",
    "この条件、かなり危ないです",
    "まず物件カードを見ます",
    "ここで事故ります",
)
TYPOGRAPHY_COMPARISON_SAMPLE_TEXTS = (
    "団長、ちなみに、他の番長知ってますか？",
    "なんで来なかったんすか！！",
    "まあ謝るんなら許してあげます",
    "長(ちょう)？　長って言った？",
)
FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
    Path("C:/Windows/Fonts/YuGothB.ttc"),
    Path("C:/Windows/Fonts/meiryob.ttc"),
    Path("C:/Windows/Fonts/msgothic.ttc"),
)
JAPANESE_WRAP_ALGORITHM = "japanese_boundary_font_bbox_pixel_wrap_v1"
JAPANESE_BREAK_AFTER_PUNCTUATION = frozenset("、。！？!?」』）)]")
JAPANESE_AVOID_LINE_START = frozenset("、。！？!?」』）)]ゃゅょぁぃぅぇぉっッー")
JAPANESE_PARTICLE_BREAKS = (
    "から",
    "まで",
    "より",
    "ので",
    "けど",
    "なら",
    "って",
    "では",
    "には",
    "とは",
    "は",
    "が",
    "を",
    "に",
    "へ",
    "と",
    "で",
    "も",
    "の",
    "や",
    "か",
    "ね",
    "よ",
)
JAPANESE_PHRASE_ENDINGS = (
    "です",
    "ます",
    "でした",
    "ました",
    "ない",
    "する",
    "します",
    "ください",
)
JAPANESE_TAIL_PUNCTUATION = frozenset("、。！？!?…ー〜～・「」『』（）()[]【】")
JAPANESE_SUSPICIOUS_TAIL_CORES = frozenset(
    (
        "か",
        "すか",
        "です",
        "ます",
        "まし",
        "ました",
        "でした",
        "ません",
        "よ",
        "ね",
        "の",
        "ん",
        "な",
        "だ",
    )
)


@dataclass(frozen=True)
class ModeSpec:
    mode: str
    purpose: str
    target_renderer_candidate: str
    font_ratio: float
    stroke_ratio: float
    shadow_offset_ratio: float
    safe_x_ratio: float
    safe_y_ratio: float
    line_height_ratio: float
    anchor: str
    transfer_risk: str


@dataclass(frozen=True)
class WrapResult:
    text: str
    lines: list[str]
    algorithm_name: str
    candidate_breaks: list[dict[str, Any]]
    selected_break_reason: str
    selected_breaks: list[dict[str, Any]]
    orphan_prevention_applied: bool
    suffix_tail_prevention_applied: bool
    suspicious_tail_line_present: bool
    suspicious_tail_lines: list[str]
    measured_width_by_line: list[int]


@dataclass(frozen=True)
class TypographyDecorationCandidate:
    candidate_id: str
    display_name: str
    font_paths: tuple[Path, ...]
    fallback_family: str
    stroke_ratio: float
    shadow_offset_ratio: float
    text_fill: tuple[int, int, int]
    stroke_fill: tuple[int, int, int]
    shadow_fill: tuple[int, int, int]
    badge_fill: tuple[int, int, int]
    badge_outline: tuple[int, int, int]
    decoration_note: str
    body_weight_note: str = "candidate-specific glyph body weight"
    outline_balance_role: str = "general font-family and decoration comparison"
    emoji_evaluation_scope: str = "neutral_not_primary_evaluation_target"


MODE_SPECS: tuple[ModeSpec, ...] = (
    ModeSpec(
        mode="dialogue_badge_left",
        purpose="normal dialogue with speaker identity badge",
        target_renderer_candidate="pillow_image_drawing_spike",
        font_ratio=0.115,
        stroke_ratio=0.096,
        shadow_offset_ratio=0.035,
        safe_x_ratio=0.055,
        safe_y_ratio=0.09,
        line_height_ratio=1.15,
        anchor="left_badge_first_line_center",
        transfer_risk=(
            "Badge and text grouping must be revalidated in ASS, YMM4, or Premiere; "
            "Pillow bbox is not editor behavior."
        ),
    ),
    ModeSpec(
        mode="bottom_center_emphasis",
        purpose="short emphasis or retort without speaker identity",
        target_renderer_candidate="pillow_image_drawing_spike",
        font_ratio=0.125,
        stroke_ratio=0.105,
        shadow_offset_ratio=0.04,
        safe_x_ratio=0.07,
        safe_y_ratio=0.085,
        line_height_ratio=1.12,
        anchor="bottom_center",
        transfer_risk=(
            "Center anchoring and line wrapping must be compared against ASS and editor exports."
        ),
    ),
    ModeSpec(
        mode="reaction_caption",
        purpose="instant reaction or punchline caption",
        target_renderer_candidate="pillow_image_drawing_spike",
        font_ratio=0.15,
        stroke_ratio=0.12,
        shadow_offset_ratio=0.045,
        safe_x_ratio=0.06,
        safe_y_ratio=0.12,
        line_height_ratio=1.08,
        anchor="lower_center_punchline",
        transfer_risk=(
            "Punchline treatment may need a distinct ASS/YMM4/Premiere style slot."
        ),
    ),
    ModeSpec(
        mode="speaker_badge_stack",
        purpose="multiple speakers or future face-icon/name-plate stack",
        target_renderer_candidate="pillow_image_drawing_spike",
        font_ratio=0.105,
        stroke_ratio=0.09,
        shadow_offset_ratio=0.035,
        safe_x_ratio=0.055,
        safe_y_ratio=0.09,
        line_height_ratio=1.15,
        anchor="left_identity_stack",
        transfer_risk=(
            "Identity grouping is a renderer integration problem, not only text styling."
        ),
    ),
)

ED10G_TYPOGRAPHY_DECORATION_CANDIDATES: tuple[TypographyDecorationCandidate, ...] = (
    TypographyDecorationCandidate(
        candidate_id="current_yu_gothic_heavy_outline",
        display_name="Current Yu Gothic heavy outline",
        font_paths=(
            Path("C:/Windows/Fonts/YuGothB.ttc"),
            Path("C:/Windows/Fonts/YuGothM.ttc"),
        ),
        fallback_family="Yu Gothic",
        stroke_ratio=0.096,
        shadow_offset_ratio=0.018,
        text_fill=(255, 255, 255),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(255, 210, 0),
        badge_outline=(0, 0, 0),
        decoration_note="baseline: current diagnostic heavy outline and placeholder yellow speaker badge",
    ),
    TypographyDecorationCandidate(
        candidate_id="noto_sans_jp_clean_outline",
        display_name="Noto Sans JP clean outline",
        font_paths=(
            Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
            Path("C:/Windows/Fonts/YuGothB.ttc"),
        ),
        fallback_family="Noto Sans JP",
        stroke_ratio=0.086,
        shadow_offset_ratio=0.018,
        text_fill=(255, 255, 255),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(34, 139, 230),
        badge_outline=(12, 36, 56),
        decoration_note="cleaner outline with a cooler placeholder badge accent",
    ),
    TypographyDecorationCandidate(
        candidate_id="meiryo_bold_soft_shadow",
        display_name="Meiryo bold soft shadow",
        font_paths=(
            Path("C:/Windows/Fonts/meiryob.ttc"),
            Path("C:/Windows/Fonts/YuGothB.ttc"),
        ),
        fallback_family="Meiryo Bold",
        stroke_ratio=0.078,
        shadow_offset_ratio=0.035,
        text_fill=(255, 252, 238),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(237, 86, 59),
        badge_outline=(50, 22, 14),
        decoration_note="slightly lighter outline with a stronger soft-shadow readback",
    ),
    TypographyDecorationCandidate(
        candidate_id="gothic_high_contrast_minimal_badge",
        display_name="Gothic high contrast minimal badge",
        font_paths=(
            Path("C:/Windows/Fonts/msgothic.ttc"),
            Path("C:/Windows/Fonts/YuGothB.ttc"),
        ),
        fallback_family="MS Gothic",
        stroke_ratio=0.105,
        shadow_offset_ratio=0.012,
        text_fill=(255, 255, 255),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(46, 50, 56),
        badge_outline=(245, 196, 74),
        decoration_note="high-contrast text with a quieter placeholder badge block",
    ),
)

ED10I_KIRINUKI_GOTHIC_CANDIDATES: tuple[TypographyDecorationCandidate, ...] = (
    TypographyDecorationCandidate(
        candidate_id="ed10i_reference_noto_clean_outline",
        display_name="ED-10i reference: Noto Sans JP clean outline",
        font_paths=(
            Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
            Path("C:/Windows/Fonts/YuGothB.ttc"),
        ),
        fallback_family="Noto Sans JP",
        stroke_ratio=0.086,
        shadow_offset_ratio=0.014,
        text_fill=(255, 255, 255),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(60, 96, 140),
        badge_outline=(18, 30, 44),
        decoration_note=(
            "current ED-10g reference carried forward only to show the fill/outline "
            "balance issue; not accepted as the final route"
        ),
        body_weight_note="current reference body; glyph fill can feel outweighed by outline",
        outline_balance_role="current_reference_outline_can_dominate",
        emoji_evaluation_scope="emoji_neutral_ignored_for_ed10i",
    ),
    TypographyDecorationCandidate(
        candidate_id="ed10i_biz_udgothic_bold_balanced_outline",
        display_name="BIZ UDGothic Bold balanced outline",
        font_paths=(
            Path("C:/Windows/Fonts/BIZ-UDGothicB.ttc"),
            Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
        ),
        fallback_family="BIZ UDGothic",
        stroke_ratio=0.066,
        shadow_offset_ratio=0.014,
        text_fill=(255, 255, 255),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(210, 46, 58),
        badge_outline=(52, 14, 18),
        decoration_note=(
            "local gothic bold candidate for thicker glyph body with a reduced outline"
        ),
        body_weight_note="bold local gothic body; intended to make fill weight lead the outline",
        outline_balance_role="thicker_glyph_body_vs_thinner_outline",
        emoji_evaluation_scope="emoji_neutral_ignored_for_ed10i",
    ),
    TypographyDecorationCandidate(
        candidate_id="ed10i_yu_gothic_bold_thin_outline",
        display_name="Yu Gothic Bold thinner outline",
        font_paths=(
            Path("C:/Windows/Fonts/YuGothB.ttc"),
            Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
        ),
        fallback_family="Yu Gothic",
        stroke_ratio=0.062,
        shadow_offset_ratio=0.012,
        text_fill=(255, 255, 255),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(244, 162, 48),
        badge_outline=(61, 38, 8),
        decoration_note=(
            "system gothic bold route that isolates a thinner outline against a heavy body"
        ),
        body_weight_note="bold system gothic body; thinner outline isolates outline pressure",
        outline_balance_role="thin_outline_variant",
        emoji_evaluation_scope="emoji_neutral_ignored_for_ed10i",
    ),
    TypographyDecorationCandidate(
        candidate_id="ed10i_meiryo_bold_fill_outline_balance",
        display_name="Meiryo Bold fill/outline balance",
        font_paths=(
            Path("C:/Windows/Fonts/meiryob.ttc"),
            Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
        ),
        fallback_family="Meiryo",
        stroke_ratio=0.072,
        shadow_offset_ratio=0.016,
        text_fill=(255, 252, 238),
        stroke_fill=(0, 0, 0),
        shadow_fill=(0, 0, 0),
        badge_fill=(44, 151, 116),
        badge_outline=(10, 45, 36),
        decoration_note=(
            "balanced local gothic/sans fallback with slightly warm fill and restrained outline"
        ),
        body_weight_note="bold body with warm fill; tests the most balanced fill/outline read",
        outline_balance_role="balanced_fill_outline_variant",
        emoji_evaluation_scope="emoji_neutral_ignored_for_ed10i",
    ),
)

TYPOGRAPHY_DECORATION_CANDIDATES: tuple[TypographyDecorationCandidate, ...] = (
    ED10G_TYPOGRAPHY_DECORATION_CANDIDATES
    + ED10I_KIRINUKI_GOTHIC_CANDIDATES
)


TAXONOMY = {
    "dialogue_badge_left": {
        "use": "normal conversation where speaker identity is useful",
        "decision": "keep as a diagnostic dialogue mode, not a universal layout",
    },
    "bottom_center_emphasis": {
        "use": "emphasis, retort, or generic subtitle without badge",
        "decision": "supported alternative for short emphasis lines",
    },
    "reaction_caption": {
        "use": "instant reaction or punchline such as 来ねぇ！！",
        "decision": "treat 来ねぇ！！ as this or bottom_center_emphasis first",
    },
    "speaker_badge_stack": {
        "use": "multiple speaker identity markers or future face icons",
        "decision": "defer production path; keep as isolated spike sample",
    },
}


RENDERER_DECISION_MATRIX = [
    {
        "candidate": "ASS/libass + FFmpeg",
        "use": "burned-in diagnostic proof and timing verification",
        "strength": "already integrated; supports stroke and positioning",
        "weakness": "ASS units and font fallback differ from YMM4/Premiere",
        "ymm4_premiere_connection": "indirect translation plus visual QA",
        "bbox_measurement": "medium; intended layout known, final glyphs renderer-dependent",
    },
    {
        "candidate": "HTML/CSS + Playwright screenshot",
        "use": "review-only layout prototype",
        "strength": "fast comparison and contact sheets",
        "weakness": "CSS values must not become production subtitle settings",
        "ymm4_premiere_connection": "weak; useful only for visual exploration",
        "bbox_measurement": "medium in browser, weak for production transfer",
    },
    {
        "candidate": "Pillow / Skia / Pango image drawing",
        "use": "pixel bbox spike and image overlay experiments",
        "strength": "direct generated bitmap bbox readback",
        "weakness": "font shaping and fallback may differ from video editors",
        "ymm4_premiere_connection": "moderate as pre-rendered overlay, weak as editable subtitle",
        "bbox_measurement": "strong for generated bitmap only",
    },
    {
        "candidate": "YMM4 .ymmp TextItem direct generation or patch",
        "use": "editable YMM4 project output",
        "strength": "closest to the YMM4 operation path",
        "weakness": "needs schema pinning and local editor validation",
        "ymm4_premiere_connection": "strong for YMM4 after schema is pinned",
        "bbox_measurement": "strong only after YMM4 render/probe",
    },
    {
        "candidate": "Premiere MOGRT / Essential Graphics / image overlay",
        "use": "Premiere-centered editorial handoff",
        "strength": "can preserve editable graphics after template path exists",
        "weakness": "automation is toolchain-heavy; image overlay loses editability",
        "ymm4_premiere_connection": "strong for Premiere after template path exists",
        "bbox_measurement": "weak before Premiere render; good for pre-rendered PNG only",
    },
]


GRID_READBACK = {
    "grid_model": "none",
    "grid_origin": None,
    "grid_cell_size": None,
    "grid_line_spacing": None,
    "grid_visible_in_samples": False,
    "grid_authority": "none",
    "snap_to_grid": False,
    "bbox_grid_coords": None,
    "safe_area_grid_coords": None,
    "actual_layout_authority": (
        "Pillow font pixel bbox, measured text width, per-mode safe-area margins, "
        "and explicit anchor rules"
    ),
    "wrapping_authority": "font_bbox_pixel_measurement_not_grid_cell_count",
    "human_review_note": (
        "No layout grid is drawn or used. The visible readback is the safe-area "
        "rectangle plus JSON bbox readback; actual placement comes from "
        "safe-area margin fields, measured bbox, and anchors."
    ),
}

VISIBLE_ELEMENT_AUTHORITY_CLASSES = {
    "computational_authority": (
        "The element or its directly reported fields are used to calculate the "
        "sample layout."
    ),
    "measured_readback": (
        "The element visualizes or reports measured values; it is evidence, not "
        "a separate design system."
    ),
    "visual_guide_only": (
        "The element helps human orientation and must not be read as a layout "
        "calculation rule."
    ),
    "placeholder": (
        "The element reserves or illustrates a future production asset or "
        "identity role, but is not the final asset."
    ),
    "decorative": "The element has no layout or design authority.",
}

VISIBLE_ELEMENT_AUTHORITY = [
    {
        "element_id": "subtitle_text_block",
        "display_name": "drawn subtitle text block",
        "authority_class": "computational_authority",
        "visible_in_default_samples": True,
        "visible_in_clean_samples": True,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": True,
        "used_in_layout_calculation": True,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The visible subtitle block is positioned from measured font bbox, "
            "wrapping width, safe-area margins, and the mode anchor."
        ),
        "readback_fields": [
            "measured_bbox",
            "wrapped_text",
            "layout_anchor",
            "layout_authority",
            "wrapping_authority",
        ],
        "test_coverage": (
            "tests assert non-empty measured_bbox, layout_anchor, and "
            "font/bbox wrapping authority for every sample"
        ),
    },
    {
        "element_id": "safe_area_rectangle",
        "display_name": "safe-area rectangle",
        "authority_class": "measured_readback",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The rectangle shows the safe-area margin used by the sample. The "
            "underlying safe_area_margin fields are layout constraints; the "
            "drawn rectangle itself is readback."
        ),
        "readback_fields": ["safe_area_margin", "safe_area_status"],
        "test_coverage": (
            "tests assert safe_area_margin/readback and sample pixel presence "
            "for the default safe-area rectangle"
        ),
    },
    {
        "element_id": "measured_text_bbox_readback",
        "display_name": "measured text bbox readback",
        "authority_class": "measured_readback",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The bbox is shown in JSON/HTML as measured evidence for the "
            "generated bitmap. It is not an editor-portable bbox contract."
        ),
        "readback_fields": ["measured_bbox"],
        "test_coverage": "tests assert measured_bbox width and height are non-zero",
    },
    {
        "element_id": "placeholder_speaker_badge",
        "display_name": "placeholder speaker badge",
        "authority_class": "placeholder",
        "visible_in_default_samples": True,
        "visible_in_clean_samples": True,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": True,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "SPK/A/B badges are placeholder speaker badges. They are not real "
            "face icons, final speaker identity design, or production artwork."
        ),
        "readback_fields": [
            "badge_bbox",
            "speaker_identity_asset_status",
            "visible_element_authority_ids",
        ],
        "test_coverage": (
            "tests assert badge samples are labeled placeholder speaker badges "
            "and real face icons are unavailable to this spike"
        ),
    },
    {
        "element_id": "speaker_accent_color",
        "display_name": "speaker badge accent color",
        "authority_class": "placeholder",
        "visible_in_default_samples": True,
        "visible_in_clean_samples": True,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The yellow badge fill is a placeholder accent. It is not derived "
            "from real member assets or a production color palette."
        ),
        "readback_fields": ["speaker_identity_asset_status"],
        "test_coverage": "tests assert the speaker accent color authority entry",
    },
    {
        "element_id": "layout_grid",
        "display_name": "layout grid",
        "authority_class": "visual_guide_only",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": False,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "No grid is drawn in default samples and no sample snaps to grid. "
            "If a grid is ever reintroduced, it must remain labeled as visual "
            "guidance or gain computational readback plus tests first."
        ),
        "readback_fields": ["grid_readback", "grid_model", "snap_to_grid"],
        "test_coverage": (
            "tests assert grid_model=none, snap_to_grid=false, null grid "
            "coordinates, and no grid-line pixel at the old default position"
        ),
    },
    {
        "element_id": "sample_mode_label",
        "display_name": "sample mode label",
        "authority_class": "visual_guide_only",
        "visible_in_default_samples": True,
        "visible_in_clean_samples": True,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The HTML label names the sample mode for review routing. It is not "
            "a layout rule or production style name."
        ),
        "readback_fields": ["subtitle_mode", "mode_decision"],
        "test_coverage": "tests assert sample mode labels and mode decisions are present",
    },
    {
        "element_id": "sample_background",
        "display_name": "plain sample background",
        "authority_class": "decorative",
        "visible_in_default_samples": True,
        "visible_in_clean_samples": True,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The dark background only makes white subtitle text readable in the "
            "review PNG."
        ),
        "readback_fields": [],
        "test_coverage": "tests assert the old grid-line pixel is plain background",
    },
    {
        "element_id": "html_sample_image_frame",
        "display_name": "HTML sample image frame",
        "authority_class": "decorative",
        "visible_in_default_samples": True,
        "visible_in_clean_samples": True,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The browser border around each image is page chrome only and has "
            "no subtitle layout meaning."
        ),
        "readback_fields": [],
        "test_coverage": "tests assert the authority table is rendered in HTML",
    },
    {
        "element_id": "frame_center_lines",
        "display_name": "frame center lines",
        "authority_class": "visual_guide_only",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "Center lines help reviewers see symmetry and bottom-center alignment. "
            "They are not snap lines."
        ),
        "readback_fields": ["guide_overlay.center_lines"],
        "test_coverage": "tests assert guided samples expose center line readback",
    },
    {
        "element_id": "frame_thirds_lines",
        "display_name": "frame thirds lines",
        "authority_class": "visual_guide_only",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "Thirds lines are optional orientation guides for human review only."
        ),
        "readback_fields": ["guide_overlay.thirds_lines"],
        "test_coverage": "tests assert guided samples expose thirds line readback",
    },
    {
        "element_id": "lower_subtitle_zone",
        "display_name": "lower subtitle zone",
        "authority_class": "visual_guide_only",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The lower zone helps judge bottom-centered subtitle placement. It "
            "does not drive Japanese wrapping."
        ),
        "readback_fields": ["guide_overlay.lower_subtitle_zone"],
        "test_coverage": "tests assert bottom_center_emphasis guide exposes lower subtitle zone",
    },
    {
        "element_id": "subtitle_baseline_guides",
        "display_name": "subtitle baseline guides",
        "authority_class": "measured_readback",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "Baseline guides are derived readback from current text position and "
            "line height. They are not font-engine baseline guarantees."
        ),
        "readback_fields": ["guide_overlay.baseline_lines", "line_height"],
        "test_coverage": "tests assert guided samples expose baseline line readback",
    },
    {
        "element_id": "badge_slot_guide",
        "display_name": "speaker badge/icon slot guide",
        "authority_class": "placeholder",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": True,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The badge slot guide shows the placeholder identity slot used to "
            "anchor dialogue text. It is not a real face icon asset."
        ),
        "readback_fields": ["guide_overlay.badge_slot", "badge_bbox"],
        "test_coverage": "tests assert dialogue guide exposes placeholder badge slot readback",
    },
    {
        "element_id": "badge_center_line",
        "display_name": "speaker badge center line",
        "authority_class": "measured_readback",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The badge center line reads back the current first-line alignment "
            "target for placeholder badge review."
        ),
        "readback_fields": ["guide_overlay.badge_center_line"],
        "test_coverage": "tests assert dialogue guide exposes badge center line readback",
    },
    {
        "element_id": "text_start_x_line",
        "display_name": "subtitle text start x line",
        "authority_class": "measured_readback",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The text start line reads back the current left text start used by "
            "the sample."
        ),
        "readback_fields": ["guide_overlay.text_start_x"],
        "test_coverage": "tests assert dialogue guide exposes text start x readback",
    },
    {
        "element_id": "badge_to_text_gap_guide",
        "display_name": "badge-to-text gap guide",
        "authority_class": "measured_readback",
        "visible_in_default_samples": False,
        "visible_in_clean_samples": False,
        "visible_in_guide_overlay_samples": True,
        "actual_layout_authority": False,
        "used_in_layout_calculation": False,
        "production_design_authority": False,
        "meaning_for_reviewer": (
            "The gap guide reads back the current placeholder badge-to-text gap."
        ),
        "readback_fields": ["guide_overlay.badge_to_text_gap"],
        "test_coverage": "tests assert dialogue guide exposes badge-to-text gap readback",
    },
]

VISIBLE_ELEMENT_AUTHORITY_BY_ID = {item["element_id"]: item for item in VISIBLE_ELEMENT_AUTHORITY}

GUIDE_OVERLAY_PROFILES = {
    "bottom_center_emphasis": {
        "guide_profile": "bottom_center_emphasis_guide_v0",
        "status": "implemented",
        "sample_text_index": 1,
        "sample_variant": "guide_overlay",
        "purpose": "review bottom-centered emphasis placement without grid cells",
        "visible_element_authority_ids": [
            "frame_center_lines",
            "frame_thirds_lines",
            "safe_area_rectangle",
            "lower_subtitle_zone",
            "subtitle_baseline_guides",
            "measured_text_bbox_readback",
        ],
    },
    "dialogue_badge_left": {
        "guide_profile": "dialogue_badge_left_guide_v0",
        "status": "implemented",
        "sample_text_index": 2,
        "sample_variant": "guide_overlay",
        "purpose": "review placeholder badge slot, text start, gap, and baseline alignment",
        "visible_element_authority_ids": [
            "frame_center_lines",
            "frame_thirds_lines",
            "safe_area_rectangle",
            "subtitle_baseline_guides",
            "measured_text_bbox_readback",
            "badge_slot_guide",
            "badge_center_line",
            "text_start_x_line",
            "badge_to_text_gap_guide",
        ],
    },
    "speaker_badge_stack": {
        "guide_profile": "speaker_badge_stack_guide_future",
        "status": "documented_deferred",
        "purpose": "future multi-speaker icon/name-plate stack review",
    },
    "status_caption": {
        "guide_profile": "status_caption_guide_future",
        "status": "documented_future_advanced",
        "purpose": "future explanatory/status caption placement review",
    },
}

GUIDE_COLORS = {
    "center": (68, 158, 255),
    "thirds": (82, 96, 112),
    "safe_area": (93, 108, 125),
    "zone": (52, 82, 108),
    "baseline": (255, 210, 0),
    "bbox": (0, 220, 180),
    "badge": (255, 100, 180),
    "text_start": (255, 150, 60),
    "gap": (255, 190, 80),
}


def build_subtitle_style_spike(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    canvas_size: tuple[int, int] = DEFAULT_CANVAS,
) -> dict[str, Any]:
    if Image is None or ImageDraw is None or ImageFont is None:
        raise RuntimeError(PILLOW_OPTIONAL_DEPENDENCY_MESSAGE)

    output_dir.mkdir(parents=True, exist_ok=True)
    width, height = canvas_size
    font_family, font_path, font_fallback_status = _select_font()
    samples: list[dict[str, Any]] = []
    guided_samples: list[dict[str, Any]] = []

    for spec in MODE_SPECS:
        for index, text in enumerate(SAMPLE_TEXTS, start=1):
            sample = _render_sample(
                output_dir=output_dir,
                canvas_size=(width, height),
                spec=spec,
                text=text,
                text_index=index,
                font_family=font_family,
                font_path=font_path,
                font_fallback_status=font_fallback_status,
            )
            samples.append(sample)

        guide_profile = GUIDE_OVERLAY_PROFILES.get(spec.mode)
        if guide_profile and guide_profile.get("status") == "implemented":
            text_index = int(guide_profile["sample_text_index"])
            guided_sample = _render_sample(
                output_dir=output_dir,
                canvas_size=(width, height),
                spec=spec,
                text=SAMPLE_TEXTS[text_index - 1],
                text_index=text_index,
                font_family=font_family,
                font_path=font_path,
                font_fallback_status=font_fallback_status,
                guide_profile=guide_profile,
            )
            guided_samples.append(guided_sample)

    report = {
        "schema_version": "v1",
        "report_kind": "subtitle_renderer_typography_spike",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": "subtitle_renderer_typography_spike_only",
        "review_only": True,
        "production_candidate": False,
        "production_compatible": False,
        "production_subtitle_design_acceptance": False,
        "production_render_acceptance": False,
        "creative_acceptance": False,
        "rights_approval": False,
        "publishing_acceptance": False,
        "public_use_permission": False,
        "reference_screenshot_status": (
            "not_found_in_repo; spike limited to subtitle mode classification "
            "and renderer-path measurement"
        ),
        "dependency_boundary": {
            "pillow": "optional_local_review_tool",
            "declared_project_dependency": False,
            "missing_dependency_behavior": "module import remains available; PNG generation raises explicit RuntimeError",
        },
        "sample_texts": list(SAMPLE_TEXTS),
        "canvas_size": {"width": width, "height": height},
        "grid_readback": GRID_READBACK,
        "visible_element_authority_classes": VISIBLE_ELEMENT_AUTHORITY_CLASSES,
        "visible_element_authority": VISIBLE_ELEMENT_AUTHORITY,
        "measured_bbox_provenance": {
            "status": "systematic_measured_readback",
            "measurement_method": "Pillow ImageDraw.multiline_textbbox after text placement",
            "source_function": "draw.multiline_textbbox",
            "hardcoded_per_sample": False,
            "manual_adjustment": False,
            "design_target": False,
            "style_values_and_layout_formulas_are_design_inputs": True,
            "report_sections": ["style_inputs", "computed_layout", "measured_output"],
            "human_review_note": (
                "measured_bbox is rendered-output measurement. It is not a "
                "hand-tuned style target and should not be copied as editor "
                "coordinates without renderer-specific validation."
            ),
        },
        "guide_overlay": {
            "contract_id": "subtitle_style_spike_layout_guide_overlay_v0",
            "role": "review_aid_not_japanese_wrapping_authority",
            "clean_samples_distinguishable": True,
            "implemented_profiles": [
                profile
                for profile in GUIDE_OVERLAY_PROFILES.values()
                if profile.get("status") == "implemented"
            ],
            "documented_profiles": [
                profile
                for profile in GUIDE_OVERLAY_PROFILES.values()
                if profile.get("status") != "implemented"
            ],
            "guided_samples": guided_samples,
            "readback_requirements": [
                "guide_profile",
                "frame_size",
                "safe_area",
                "center_lines",
                "baseline_lines",
                "badge_slot when applicable",
                "text_bbox",
                "authority_class for each visible guide element",
            ],
            "non_authority_rules": [
                "guide overlays do not reintroduce grid cells",
                "guide overlays do not drive Japanese wrapping",
                "clean samples remain available without guide overlay lines",
            ],
        },
        "taxonomy": TAXONOMY,
        "mode_semantics": {
            "comparison_reuse_note": (
                "The same text is intentionally repeated across modes so humans can "
                "compare layout behavior. Repeated text is not a universal style rule."
            ),
            "recommended_mode_policy": {
                "dialogue_badge_left": "normal speaker-identified dialogue",
                "bottom_center_emphasis": "emphasized dialogue or strong one-liner",
                "reaction_caption": "punchline, surprise, or instant reaction such as 来ねぇ！！",
                "speaker_badge_stack": "comparison-only placeholder stack for multi-speaker or future face-icon/nameplate work",
            },
            "placeholder_badge_note": (
                "SPK/A/B are temporary speaker badge placeholders, not real face "
                "icons and not production speaker identity design. Real face icon "
                "asset intake is a separate future slice."
            ),
        },
        "renderer_decision_matrix": RENDERER_DECISION_MATRIX,
        "mode_decision": {
            "line": "来ねぇ！！",
            "recommended_modes": ["reaction_caption", "bottom_center_emphasis"],
            "not_recommended_default": "dialogue_badge_left",
            "reason": (
                "The line acts as an instant reaction/punchline rather than normal "
                "speaker-continuity dialogue."
            ),
        },
        "samples": samples,
        "outputs": {
            "json": str((output_dir / "subtitle_style_spike_report.json").as_posix()),
            "html": str((output_dir / "subtitle_style_spike_report.html").as_posix()),
        },
    }
    _write_json(output_dir / "subtitle_style_spike_report.json", report)
    _write_html(output_dir / "subtitle_style_spike_report.html", report, output_dir=output_dir)
    return report


def build_subtitle_typography_decoration_comparison(
    *,
    output_dir: Path | None = None,
    episode_dir: Path | None = None,
    review_dir: Path | None = None,
    target_cut_ids: list[str] | tuple[str, ...] | None = None,
    sample_texts: list[str] | tuple[str, ...] | None = None,
    canvas_size: tuple[int, int] = (1920, 1080),
    base_dir: Path | None = None,
    comparison_profile: str = ED10G_TYPOGRAPHY_DECORATION_PROFILE,
) -> dict[str, Any]:
    """Generate review-only font-family / decoration comparison artifacts.

    This preserves the accepted diagnostic font-size direction and varies only
    font family and decorative treatment. It does not render source media or
    approve production subtitle design.
    """
    if Image is None or ImageDraw is None or ImageFont is None:
        raise RuntimeError(PILLOW_OPTIONAL_DEPENDENCY_MESSAGE)

    base = base_dir or Path.cwd()
    target_cut_ids = tuple(target_cut_ids or ("cut_002", "cut_003"))
    profile = _typography_comparison_profile(
        comparison_profile,
        target_cut_ids=target_cut_ids,
    )
    if output_dir is None:
        output_dir = (
            review_dir / profile["output_dir_name"]
            if review_dir is not None
            else profile["default_output_dir"]
        )
    output_dir = output_dir if output_dir.is_absolute() else base / output_dir
    texts = list(
        sample_texts
        or _comparison_texts_from_edit_pack(
            episode_dir=episode_dir,
            target_cut_ids=target_cut_ids,
            base=base,
        )
        or TYPOGRAPHY_COMPARISON_SAMPLE_TEXTS
    )
    texts = _dedupe_nonempty_texts(texts)[:4]
    if not texts:
        texts = list(TYPOGRAPHY_COMPARISON_SAMPLE_TEXTS)

    output_dir.mkdir(parents=True, exist_ok=True)
    width, height = canvas_size
    samples: list[dict[str, Any]] = []
    for candidate in profile["candidates"]:
        for index, text in enumerate(texts, start=1):
            samples.append(
                _render_typography_decoration_sample(
                    output_dir=output_dir,
                    canvas_size=(width, height),
                    candidate=candidate,
                    text=text,
                    text_index=index,
                    sample_variant=profile["sample_variant"],
                )
            )

    contact_sheet_path = _write_typography_comparison_contact_sheet(
        samples=samples,
        output_dir=output_dir,
        filename=profile["contact_sheet_filename"],
    )
    json_path = output_dir / profile["json_filename"]
    html_path = output_dir / profile["html_filename"]
    open_helper_path = output_dir / "open_comparison.ps1"
    open_helper_path.write_text(
        _open_comparison_script(profile["html_filename"]),
        encoding="utf-8",
    )
    open_helper_display = _display_path(open_helper_path, base)
    open_helper_windows = open_helper_display.replace("/", "\\")

    report = {
        "schema_version": "v1",
        "report_kind": profile["report_kind"],
        "artifact_id": profile["artifact_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": profile["scope"],
        "comparison_profile": comparison_profile,
        "html_title": profile["html_title"],
        "source_notice": profile["source_notice"],
        "decision_packet_title": profile["decision_packet_title"],
        "decision_packet_key": profile["decision_packet_key"],
        "review_only": True,
        "production_candidate": False,
        "production_compatible": False,
        "production_subtitle_design_acceptance": False,
        "production_render_acceptance": False,
        "creative_acceptance": False,
        "rights_status": "pending",
        "publishing_acceptance": False,
        "public_use_permission": False,
        "source_media_mutated": False,
        "transcript_mutated": False,
        "official_subtitle_evidence_mutated": False,
        "target_cuts": list(target_cut_ids),
        "human_decision_readback": profile["human_decision_readback"],
        "comparison_response_readback": profile["comparison_response_readback"],
        "candidate_count": len(profile["candidates"]),
        "sample_texts": texts,
        "canvas_size": {"width": width, "height": height},
        "font_size_policy": {
            "status": profile["font_size_status"],
            "formula": "round(frame_height * 0.115)",
            "value": max(16, round(height * 0.115)),
            "scope": "diagnostic_representative_review_only",
        },
        "comparison_axes": profile["comparison_axes"],
        "next_diagnostic_overlay_proof_route": profile["next_diagnostic_overlay_proof_route"],
        profile["decision_packet_key"]: profile["decision_packet"],
        "comparison_decision_packet": profile["decision_packet"],
        "candidates": [_candidate_readback(candidate) for candidate in profile["candidates"]],
        "samples": samples,
        "outputs": {
            "json": _display_path(json_path, base),
            "html": _display_path(html_path, base),
            "contact_sheet": _display_path(contact_sheet_path, base),
            "open_helper": _display_path(open_helper_path, base),
        },
        "open_commands": {
            "open_comparison": (
                "powershell -ExecutionPolicy Bypass -File "
                f"{open_helper_windows}"
            )
        },
        "next_decision_question": (
            profile["next_decision_question"]
        ),
    }
    _write_json(json_path, report)
    _write_typography_comparison_html(html_path, report)
    return report


def _typography_comparison_profile(
    comparison_profile: str,
    *,
    target_cut_ids: tuple[str, ...],
) -> dict[str, Any]:
    if comparison_profile == ED10G_TYPOGRAPHY_DECORATION_PROFILE:
        decision_packet = _small_adjustment_decision_packet(target_cut_ids=target_cut_ids)
        return {
            "output_dir_name": "subtitle_typography_decoration_comparison",
            "default_output_dir": DEFAULT_TYPOGRAPHY_COMPARISON_OUTPUT_DIR,
            "json_filename": "subtitle_typography_decoration_comparison_report.json",
            "html_filename": "subtitle_typography_decoration_comparison_report.html",
            "contact_sheet_filename": "subtitle_typography_decoration_contact_sheet.png",
            "sample_variant": "font_family_decoration_comparison",
            "report_kind": "subtitle_typography_decoration_comparison",
            "artifact_id": "clip-typography-decoration-comparison-001",
            "scope": "diagnostic_representative_font_family_decoration_comparison",
            "html_title": "Subtitle Typography Decoration Comparison",
            "source_notice": (
                "Source human readback: adjust_boundary. ED-10g comparison response: "
                "small_adjustment. Font size is accepted only for the current "
                "diagnostic / representative route; font family and decoration "
                "remain unresolved until a concrete adjusted candidate is selected."
            ),
            "decision_packet_title": "Small Adjustment Decision Packet",
            "decision_packet_key": "small_adjustment_decision_packet",
            "decision_packet": decision_packet,
            "font_size_status": "preserved_from_human_review",
            "human_decision_readback": {
                "source_artifact": "clip-human-preview-session-001",
                "selected_response": "adjust_boundary",
                "font_size": "accepted_for_diagnostic_representative_review",
                "font_family": "unresolved_needs_comparison",
                "decoration": "unresolved_needs_comparison",
                "production_subtitle_design_acceptance": False,
            },
            "comparison_response_readback": {
                "source_artifact": "clip-typography-decoration-comparison-001",
                "selected_response": "small_adjustment",
                "selected_candidate_for_next_proof_base": "noto_sans_jp_clean_outline",
                "font_size": "accepted_for_diagnostic_representative_review",
                "font_family": "narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof",
                "decoration": "narrowed_to_clean_outline_for_next_diagnostic_proof",
                "production_subtitle_design_acceptance": False,
                "production_render_acceptance": False,
                "creative_acceptance": False,
                "rights_status": "pending",
                "publishing_acceptance": False,
                "public_use_permission": False,
            },
            "comparison_axes": {
                "fixed": ["font_size", "badge_left_dialogue placement", "font_bbox wrapping"],
                "varied": [
                    "font_family",
                    "outline/stroke ratio",
                    "shadow offset",
                    "placeholder badge accent",
                ],
                "out_of_scope": [
                    "production subtitle design acceptance",
                    "production render acceptance",
                    "rights approval",
                    "publishing",
                    "public use",
                ],
            },
            "next_diagnostic_overlay_proof_route": {
                "route_kind": "small_adjustment_diagnostic_overlay_proof",
                "target_cuts": list(target_cut_ids),
                "selected_candidate_for_next_proof_base": "noto_sans_jp_clean_outline",
                "recommended_default_candidate_id": "noto_sans_jp_clean_outline",
                "font_size": {
                    "status": "preserve_accepted_diagnostic_representative_direction",
                    "formula": "round(frame_height * 0.115)",
                },
                "font_family": "narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof",
                "decoration": "narrowed_to_clean_outline_for_next_diagnostic_proof",
                "regenerate_sh08_required": False,
                "comparison_artifact_required": "only_when_visual_candidate_readback_is_needed",
                "episodes_artifact_tracking_allowed": False,
                "production_subtitle_design_acceptance": False,
                "production_render_acceptance": False,
                "creative_acceptance": False,
                "rights_status": "pending",
                "publishing_acceptance": False,
                "public_use_permission": False,
            },
            "candidates": ED10G_TYPOGRAPHY_DECORATION_CANDIDATES,
            "next_decision_question": (
                "After generating the next cut_002 / cut_003 diagnostic overlay proof "
                "from noto_sans_jp_clean_outline, is this small adjustment acceptable "
                "for diagnostic / representative review? "
                "This does not approve production subtitle design, production render, "
                "rights, publishing, public use, or upload."
            ),
        }
    if comparison_profile == ED10I_KIRINUKI_GOTHIC_BALANCE_PROFILE:
        decision_packet = _kirinuki_gothic_balance_decision_packet(
            target_cut_ids=target_cut_ids,
        )
        return {
            "output_dir_name": "subtitle_kirinuki_gothic_balance_comparison",
            "default_output_dir": DEFAULT_KIRINUKI_GOTHIC_BALANCE_OUTPUT_DIR,
            "json_filename": "subtitle_kirinuki_gothic_balance_comparison_report.json",
            "html_filename": "subtitle_kirinuki_gothic_balance_comparison_report.html",
            "contact_sheet_filename": "subtitle_kirinuki_gothic_balance_contact_sheet.png",
            "sample_variant": "kirinuki_gothic_weight_balance_comparison",
            "report_kind": "subtitle_kirinuki_gothic_weight_balance_comparison",
            "artifact_id": "clip-ed10i-kirinuki-gothic-balance-001",
            "scope": "diagnostic_representative_kirinuki_gothic_weight_balance_comparison",
            "html_title": "ED-10i Kirinuki Gothic Weight Balance Comparison",
            "source_notice": (
                "Human review consumed: the current Noto clean-outline proof is "
                "not accepted as-is. Preferred direction is kirinuki YouTube style "
                "gothic; the main issue is fill/outline balance, so this slice "
                "compares thicker glyph bodies and restrained outline thickness. "
                "Emoji rendering is neutral and ignored for this evaluation."
            ),
            "decision_packet_title": "Kirinuki Gothic Balance Decision Packet",
            "decision_packet_key": "kirinuki_gothic_balance_decision_packet",
            "decision_packet": decision_packet,
            "font_size_status": "preserved_as_starting_reference_not_reopened",
            "human_decision_readback": {
                "source_artifact": "clip-ed10g-noto-overlay-proof-001",
                "selected_response": "not_accepted_as_is",
                "preferred_direction": "kirinuki_youtube_style_gothic",
                "main_issue": "fill_outline_balance_outline_dominates",
                "desired_adjustment": "make_glyph_body_thicker_so_outline_does_not_dominate",
                "emoji_treatment": "neutral_ignore_for_evaluation",
                "font_size": "preserve_current_size_policy_as_starting_reference",
                "production_subtitle_design_acceptance": False,
            },
            "comparison_response_readback": {
                "source_artifact": "clip-ed10i-kirinuki-gothic-balance-001",
                "selected_response": "generate_narrow_kirinuki_gothic_balance_comparison",
                "selected_candidate_for_next_proof_base": "pending_ed10i_human_review",
                "recommended_default_candidate_id": "ed10i_biz_udgothic_bold_balanced_outline",
                "font_size": "preserved_as_starting_reference_not_primary_axis",
                "font_family": "gothic_sans_only",
                "font_weight": "compare_bold_glyph_body",
                "decoration": "compare_restrained_outline_against_body_weight",
                "emoji_treatment": "neutral_ignore_for_evaluation",
                "production_subtitle_design_acceptance": False,
                "production_render_acceptance": False,
                "creative_acceptance": False,
                "rights_status": "pending",
                "publishing_acceptance": False,
                "public_use_permission": False,
            },
            "comparison_axes": {
                "fixed": [
                    "font_size_policy=round(frame_height * 0.115)",
                    "badge_left_dialogue placement",
                    "font_bbox wrapping",
                    "target_cuts=cut_002/cut_003",
                ],
                "varied": [
                    "font_family",
                    "font_weight / glyph body thickness",
                    "outline/stroke ratio",
                    "fill vs outline balance",
                ],
                "out_of_scope": [
                    "emoji quality",
                    "serif/mincho candidates",
                    "display-font experimentation",
                    "all-font sweep",
                    "production subtitle design acceptance",
                    "production render acceptance",
                    "rights approval",
                    "publishing",
                    "public use",
                ],
            },
            "next_diagnostic_overlay_proof_route": {
                "route_kind": "kirinuki_gothic_weight_balance_diagnostic_proof",
                "target_cuts": list(target_cut_ids),
                "selected_candidate_for_next_proof_base": "pending_ed10i_human_review",
                "recommended_default_candidate_id": "ed10i_biz_udgothic_bold_balanced_outline",
                "font_size": {
                    "status": "preserve_existing_size_policy_as_starting_reference",
                    "formula": "round(frame_height * 0.115)",
                },
                "font_family": "gothic_sans_only",
                "font_weight": "heavier_body_preferred",
                "outline": "thinner_than_current_reference_when_body_weight_allows",
                "emoji_treatment": "neutral_ignore_for_evaluation",
                "regenerate_sh08_required": False,
                "comparison_artifact_required": "generated_for_ed10i_human_review",
                "episodes_artifact_tracking_allowed": False,
                "production_subtitle_design_acceptance": False,
                "production_render_acceptance": False,
                "creative_acceptance": False,
                "rights_status": "pending",
                "publishing_acceptance": False,
                "public_use_permission": False,
            },
            "candidates": ED10I_KIRINUKI_GOTHIC_CANDIDATES,
            "next_decision_question": (
                "For cut_002 / cut_003, which ED-10i gothic balance candidate "
                "should become the next diagnostic overlay proof base: the current "
                "reference, the thicker BIZ UDGothic body, the thinner-outline Yu "
                "Gothic variant, or the balanced Meiryo variant? Emoji differences "
                "are intentionally ignored in this slice."
            ),
        }
    known = ", ".join(TYPOGRAPHY_COMPARISON_PROFILES)
    raise ValueError(f"unknown comparison_profile: {comparison_profile}; known={known}")


def _comparison_texts_from_edit_pack(
    *,
    episode_dir: Path | None,
    target_cut_ids: tuple[str, ...],
    base: Path,
) -> list[str]:
    if episode_dir is None:
        return []
    episode_dir = episode_dir if episode_dir.is_absolute() else base / episode_dir
    edit_pack_path = episode_dir / "edit_pack.json"
    try:
        edit_pack = json.loads(edit_pack_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    subtitles = edit_pack.get("subtitles") if isinstance(edit_pack.get("subtitles"), list) else []
    target_set = set(target_cut_ids)
    by_id = {
        str(item.get("id")): str(item.get("text") or "")
        for item in subtitles
        if isinstance(item, dict) and str(item.get("cut_id") or "") in target_set
    }
    preferred_ids = ("sub_008", "sub_013", "sub_017", "sub_025")
    texts = [by_id[item_id] for item_id in preferred_ids if by_id.get(item_id)]
    for item in subtitles:
        if not isinstance(item, dict) or str(item.get("cut_id") or "") not in target_set:
            continue
        text = str(item.get("text") or "")
        if text:
            texts.append(text)
    return _dedupe_nonempty_texts(texts)


def _dedupe_nonempty_texts(texts: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for text in texts:
        text = str(text).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _small_adjustment_decision_packet(
    *,
    target_cut_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "decision_state": "selected_for_next_diagnostic_overlay_proof_base",
        "selected_candidate_for_next_proof_base": "noto_sans_jp_clean_outline",
        "recommended_default_candidate_id": "noto_sans_jp_clean_outline",
        "recommended_default_use": (
            "Adopted as the next diagnostic overlay proof base for this "
            "small-adjustment route."
        ),
        "target_cuts": list(target_cut_ids),
        "font_size": {
            "decision": "accepted_for_diagnostic_representative_review",
            "formula": "round(frame_height * 0.115)",
            "reopen_as_primary_axis": False,
        },
        "active_adjustment_axes": [
            "font_family",
            "outline/stroke ratio",
            "shadow offset",
            "placeholder speaker-badge accent",
        ],
        "options": [
            {
                "candidate_id": "current_yu_gothic_heavy_outline",
                "use_as": "reference_only",
                "adoption_reason": (
                    "Keeps the accepted diagnostic baseline visible for comparison."
                ),
                "watch_item": (
                    "Does not satisfy small_adjustment by itself because font family "
                    "and decoration stay at the current baseline."
                ),
            },
            {
                "candidate_id": "noto_sans_jp_clean_outline",
                "use_as": "selected_next_proof_base",
                "adoption_reason": (
                    "Smallest readable adjustment: cleaner Japanese face route, "
                    "slightly lighter outline, cooler placeholder badge accent, "
                    "and unchanged accepted size / placement."
                ),
                "watch_item": (
                    "Font availability can fall back locally; the next proof must "
                    "record the resolved font file."
                ),
            },
            {
                "candidate_id": "meiryo_bold_soft_shadow",
                "use_as": "alternate_if_default_feels_too_heavy",
                "adoption_reason": (
                    "Preserves readable boldness while testing softer decoration "
                    "and stronger shadow."
                ),
                "watch_item": "Shadow softness may reduce crispness on fast video motion.",
            },
            {
                "candidate_id": "gothic_high_contrast_minimal_badge",
                "use_as": "alternate_if_badge_decoration_is_primary_concern",
                "adoption_reason": (
                    "Reduces badge visual weight while keeping high contrast text."
                ),
                "watch_item": (
                    "MS Gothic can feel more mechanical; use only if high contrast "
                    "matters more than warmth."
                ),
            },
        ],
        "rejected_alternatives": [
            {
                "route": "regenerate_sh08_human_preview_session",
                "reason": "Not required for this ED-10g small-adjustment route.",
            },
            {
                "route": "claim_production_subtitle_design_acceptance",
                "reason": "small_adjustment is diagnostic feedback, not production approval.",
            },
            {
                "route": "add_cut_008_dense_stress_proof_now",
                "reason": (
                    "Dense/stress coverage remains a separate route unless the next "
                    "review explicitly widens scope."
                ),
            },
            {
                "route": "mutate_source_or_rights_or_publishing_state",
                "reason": (
                    "Source media, transcript, official subtitle evidence, rights, "
                    "publishing, public use, and upload are outside this proof route."
                ),
            },
        ],
        "smallest_next_proof_route": {
            "route_kind": "small_adjustment_diagnostic_overlay_proof",
            "selected_candidate_id": "noto_sans_jp_clean_outline",
            "default_candidate_id": "noto_sans_jp_clean_outline",
            "target_cuts": list(target_cut_ids),
            "keep_baseline_reference": True,
            "proof_scope": "diagnostic_representative_review_only",
            "regenerate_sh08_required": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        },
    }


def _kirinuki_gothic_balance_decision_packet(
    *,
    target_cut_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "decision_state": "generated_requires_human_review",
        "current_reference_not_accepted_as_is": True,
        "preferred_direction": "kirinuki_youtube_style_gothic",
        "main_issue": "fill_outline_balance_outline_dominates",
        "desired_adjustment": "make_glyph_body_thicker_so_outline_does_not_dominate",
        "recommended_default_candidate_id": "ed10i_biz_udgothic_bold_balanced_outline",
        "selected_candidate_for_next_proof_base": "pending_ed10i_human_review",
        "target_cuts": list(target_cut_ids),
        "font_size": {
            "decision": "preserve_existing_size_policy_as_starting_reference",
            "formula": "round(frame_height * 0.115)",
            "reopen_as_primary_axis": False,
        },
        "active_adjustment_axes": [
            "font_family",
            "font_weight / glyph body thickness",
            "outline/stroke ratio",
            "fill vs outline balance",
        ],
        "emoji_treatment": {
            "decision": "neutral_ignore_for_evaluation",
            "optimize_in_this_slice": False,
        },
        "options": [
            {
                "candidate_id": "ed10i_reference_noto_clean_outline",
                "use_as": "current_reference_only",
                "adoption_reason": (
                    "Keeps the visible ED-10g Noto route in the comparison so the "
                    "new thicker-body candidates can be judged fairly."
                ),
                "watch_item": "Human review already says this route is not accepted as-is.",
            },
            {
                "candidate_id": "ed10i_biz_udgothic_bold_balanced_outline",
                "use_as": "recommended_default_for_next_diagnostic_overlay_proof",
                "adoption_reason": (
                    "BIZ UDGothic Bold gives a heavier local gothic body while the "
                    "outline is reduced enough to stop dominating the fill."
                ),
                "watch_item": (
                    "Local/system font availability is same-machine evidence; a "
                    "future reproducible route needs license/source readback."
                ),
            },
            {
                "candidate_id": "ed10i_yu_gothic_bold_thin_outline",
                "use_as": "thinner_outline_variant",
                "adoption_reason": (
                    "Keeps a familiar Windows gothic route and isolates whether "
                    "outline reduction alone solves the balance issue."
                ),
                "watch_item": "May retain some of the earlier system-font look.",
            },
            {
                "candidate_id": "ed10i_meiryo_bold_fill_outline_balance",
                "use_as": "balanced_fill_outline_variant",
                "adoption_reason": (
                    "Tests a bold readable sans route with slightly warm fill and "
                    "a restrained outline."
                ),
                "watch_item": "May feel softer than the kirinuki-gothic target.",
            },
        ],
        "rejected_alternatives": [
            {
                "route": "re_accept_current_noto_clean_outline_as_final",
                "reason": "The consumed human review explicitly says the current proof is not accepted as-is.",
            },
            {
                "route": "broaden_to_all_font_sweep",
                "reason": "ED-10i is a narrow gothic/sans balance proof, not ED-10h all-font exploration.",
            },
            {
                "route": "optimize_emoji_rendering",
                "reason": "Emoji treatment is neutral and ignored for this slice.",
            },
            {
                "route": "vendor_third_party_font_binaries",
                "reason": "No font binary vendoring is approved for this slice.",
            },
            {
                "route": "claim_production_subtitle_design_acceptance",
                "reason": "The generated comparison remains diagnostic / representative review only.",
            },
            {
                "route": "mutate_source_or_rights_or_publishing_state",
                "reason": (
                    "Source media, transcript, official subtitle evidence, rights, "
                    "publishing, public use, and upload are outside this proof route."
                ),
            },
        ],
        "smallest_next_proof_route": {
            "route_kind": "kirinuki_gothic_weight_balance_diagnostic_proof",
            "selected_candidate_id": "pending_ed10i_human_review",
            "default_candidate_id": "ed10i_biz_udgothic_bold_balanced_outline",
            "target_cuts": list(target_cut_ids),
            "keep_current_reference_visible": True,
            "proof_scope": "diagnostic_representative_review_only",
            "regenerate_sh08_required": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "publishing_acceptance": False,
            "public_use_permission": False,
        },
    }


def _candidate_readback(candidate: TypographyDecorationCandidate) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "display_name": candidate.display_name,
        "requested_font_paths": [path.as_posix() for path in candidate.font_paths],
        "fallback_family": candidate.fallback_family,
        "stroke_ratio": candidate.stroke_ratio,
        "shadow_offset_ratio": candidate.shadow_offset_ratio,
        "text_fill": _rgb_hex(candidate.text_fill),
        "stroke_fill": _rgb_hex(candidate.stroke_fill),
        "shadow_fill": _rgb_hex(candidate.shadow_fill),
        "badge_fill": _rgb_hex(candidate.badge_fill),
        "badge_outline": _rgb_hex(candidate.badge_outline),
        "decoration_note": candidate.decoration_note,
        "body_weight_note": candidate.body_weight_note,
        "outline_balance_role": candidate.outline_balance_role,
        "emoji_evaluation_scope": candidate.emoji_evaluation_scope,
        "production_subtitle_design_acceptance": False,
    }


def _render_typography_decoration_sample(
    *,
    output_dir: Path,
    canvas_size: tuple[int, int],
    candidate: TypographyDecorationCandidate,
    text: str,
    text_index: int,
    sample_variant: str = "font_family_decoration_comparison",
) -> dict[str, Any]:
    width, height = canvas_size
    font_size = max(16, round(height * 0.115))
    stroke_width = max(2, round(font_size * candidate.stroke_ratio))
    shadow_offset = max(1, round(font_size * candidate.shadow_offset_ratio))
    safe_x = round(width * 0.055)
    safe_y = round(height * 0.09)
    line_height = max(font_size, round(font_size * 1.15))
    spacing = max(0, line_height - font_size)
    badge_w = max(48, round(font_size * 1.0))
    badge_h = max(32, round(font_size * 0.7))
    badge_gap = max(8, round(font_size * 0.3))
    badge_font_size = max(12, round(font_size * 0.44))
    font_family, font_path, font_status = _select_candidate_font(candidate)
    font = _load_font(font_path, font_size)

    image = Image.new("RGB", (width, height), (36, 39, 44))
    draw = ImageDraw.Draw(image)
    max_text_width = max(120, width - safe_x - badge_w - badge_gap - safe_x)
    wrap_result = _wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_text_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    origin_bbox = _text_bbox_at_origin(
        draw=draw,
        text=wrap_result.text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    text_x, text_y = _origin_for_target_bbox(
        origin_bbox,
        target_left=safe_x + badge_w + badge_gap,
        target_bottom=height - safe_y,
    )
    first_line_top = text_y + origin_bbox[1]
    badge_center_y = first_line_top + round(line_height * 0.52)
    badge_y = badge_center_y - round(badge_h / 2)
    badge_bbox = _draw_comparison_badge(
        draw,
        label="SPK",
        xy=(safe_x, badge_y),
        size=(badge_w, badge_h),
        font_path=font_path,
        font_size=badge_font_size,
        fill=candidate.badge_fill,
        outline=candidate.badge_outline,
    )
    _draw_comparison_text(
        draw,
        xy=(text_x, text_y),
        text=wrap_result.text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
        shadow_offset=shadow_offset,
        text_fill=candidate.text_fill,
        stroke_fill=candidate.stroke_fill,
        shadow_fill=candidate.shadow_fill,
    )
    measured_bbox = draw.multiline_textbbox(
        (text_x, text_y),
        wrap_result.text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    output_path = output_dir / (
        f"subtitle_typography_decoration.{candidate.candidate_id}.{text_index:02d}.png"
    )
    image.save(output_path)
    safe_area_status = _bbox_inside_safe_area(
        measured_bbox,
        canvas_size=(width, height),
        safe_x=safe_x,
        safe_y=safe_y,
    )
    return {
        "candidate_id": candidate.candidate_id,
        "display_name": candidate.display_name,
        "output_image_path": output_path.as_posix(),
        "sample_variant": sample_variant,
        "canvas_size": {"width": width, "height": height},
        "subtitle_mode": "badge_left_dialogue",
        "text": text,
        "wrapped_text": wrap_result.text,
        "wrapped_lines": wrap_result.lines,
        "wrap_algorithm": {
            "name": wrap_result.algorithm_name,
            "authority": GRID_READBACK["wrapping_authority"],
            "source_function": "_wrap_text_to_width",
            "not_grid_based": True,
        },
        "candidate_breaks": wrap_result.candidate_breaks,
        "selected_break_reason": wrap_result.selected_break_reason,
        "orphan_prevention_applied": wrap_result.orphan_prevention_applied,
        "suffix_tail_prevention_applied": wrap_result.suffix_tail_prevention_applied,
        "suspicious_tail_line_present": wrap_result.suspicious_tail_line_present,
        "suspicious_tail_lines": wrap_result.suspicious_tail_lines,
        "measured_width_by_line": wrap_result.measured_width_by_line,
        "font_family": font_family,
        "font_file": font_path,
        "font_file_status": font_status,
        "font_size_status": "accepted_for_diagnostic_representative_review",
        "requested_font_size": font_size,
        "font_size_formula": "round(frame_height * 0.115)",
        "style_inputs": {
            "font_family_axis": "comparison_candidate",
            "decoration_axis": "comparison_candidate",
            "font_size_axis": "fixed_from_human_review",
            "stroke_ratio": candidate.stroke_ratio,
            "shadow_offset_ratio": candidate.shadow_offset_ratio,
            "badge_fill": _rgb_hex(candidate.badge_fill),
            "badge_outline": _rgb_hex(candidate.badge_outline),
            "text_fill": _rgb_hex(candidate.text_fill),
            "stroke_fill": _rgb_hex(candidate.stroke_fill),
            "shadow_fill": _rgb_hex(candidate.shadow_fill),
            "decoration_note": candidate.decoration_note,
            "body_weight_axis": candidate.body_weight_note,
            "outline_balance_axis": candidate.outline_balance_role,
            "emoji_evaluation_scope": candidate.emoji_evaluation_scope,
        },
        "computed_layout": {
            "layout_anchor": "left_badge_first_line_center",
            "text_start_position": {"x": text_x, "y": text_y},
            "badge_slot": _bbox_dict(badge_bbox),
            "badge_to_text_gap": badge_gap,
            "line_height": line_height,
            "max_text_width": max_text_width,
            "wrapped_lines": wrap_result.lines,
        },
        "measured_output": {
            "source_function": "draw.multiline_textbbox",
            "measured_bbox": _bbox_dict(measured_bbox),
            "safe_area_status": safe_area_status,
            "manual_override": False,
            "design_target": False,
        },
        "measured_bbox": _bbox_dict(measured_bbox),
        "badge_bbox": _bbox_dict(badge_bbox),
        "safe_area_margin": {"x": safe_x, "y": safe_y},
        "safe_area_status": safe_area_status,
        "line_height": line_height,
        "line_count": len(wrap_result.lines),
        "grid_model": GRID_READBACK["grid_model"],
        "snap_to_grid": False,
        "layout_authority": GRID_READBACK["actual_layout_authority"],
        "wrapping_authority": GRID_READBACK["wrapping_authority"],
        "outline": {
            "stroke_width": stroke_width,
            "stroke_fill": _rgb_hex(candidate.stroke_fill),
            "renderer_term": "Pillow stroke_width, not ASS/YMM4/Premiere value",
        },
        "shadow": {
            "offset_px": shadow_offset,
            "fill": _rgb_hex(candidate.shadow_fill),
            "renderer_term": "Pillow shadow offset, not ASS/YMM4/Premiere value",
        },
        "review_only": True,
        "production_candidate": False,
        "production_compatible": False,
        "production_subtitle_design_acceptance": False,
        "visible_element_authority_ids": [
            "subtitle_text_block",
            "placeholder_speaker_badge",
            "speaker_accent_color",
            "sample_background",
        ],
        "speaker_identity_asset_status": _speaker_identity_asset_status("dialogue_badge_left"),
        "body_weight_note": candidate.body_weight_note,
        "outline_balance_role": candidate.outline_balance_role,
        "emoji_evaluation_scope": candidate.emoji_evaluation_scope,
    }


def _select_candidate_font(
    candidate: TypographyDecorationCandidate,
) -> tuple[str, str | None, str]:
    for path in candidate.font_paths:
        if path.exists():
            return path.stem, str(path), "font_file_found"
    fallback_family, fallback_path, fallback_status = _select_font()
    return (
        fallback_family or candidate.fallback_family,
        fallback_path,
        f"requested_candidate_font_missing_used_{fallback_status}",
    )


def _draw_comparison_badge(
    draw,
    *,
    label: str,
    xy: tuple[int, int],
    size: tuple[int, int],
    font_path: str | None,
    font_size: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int],
) -> tuple[int, int, int, int]:
    x, y = xy
    w, h = size
    draw.rounded_rectangle((x, y, x + w, y + h), radius=4, fill=fill, outline=outline, width=2)
    badge_font = _load_font(font_path, font_size)
    bbox = draw.textbbox((0, 0), label, font=badge_font, stroke_width=0)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (x + round((w - tw) / 2), y + round((h - th) / 2) - 2),
        label,
        font=badge_font,
        fill=(255, 255, 255),
        stroke_width=1,
        stroke_fill=(0, 0, 0),
    )
    return (x, y, x + w, y + h)


def _draw_comparison_text(
    draw,
    *,
    xy: tuple[int, int],
    text: str,
    font,
    spacing: int,
    stroke_width: int,
    shadow_offset: int,
    text_fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int],
    shadow_fill: tuple[int, int, int],
) -> None:
    x, y = xy
    draw.multiline_text(
        (x + shadow_offset, y + shadow_offset),
        text,
        font=font,
        fill=shadow_fill,
        spacing=spacing,
        stroke_width=stroke_width,
        stroke_fill=shadow_fill,
    )
    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=text_fill,
        spacing=spacing,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def _write_typography_comparison_contact_sheet(
    *,
    samples: list[dict[str, Any]],
    output_dir: Path,
    filename: str = "subtitle_typography_decoration_contact_sheet.png",
) -> Path:
    image_paths = [Path(sample["output_image_path"]) for sample in samples]
    thumbnails = []
    for path in image_paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((480, 270))
        thumbnails.append(image.copy())
    if not thumbnails:
        raise RuntimeError("no typography comparison images were generated")
    columns = 2
    cell_w = max(image.width for image in thumbnails)
    cell_h = max(image.height for image in thumbnails)
    rows = (len(thumbnails) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), (22, 25, 29))
    for index, image in enumerate(thumbnails):
        x = (index % columns) * cell_w
        y = (index // columns) * cell_h
        sheet.paste(image, (x, y))
    contact_sheet = output_dir / filename
    sheet.save(contact_sheet)
    return contact_sheet


def _write_typography_comparison_html(path: Path, report: dict[str, Any]) -> None:
    samples_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for sample in report["samples"]:
        samples_by_candidate.setdefault(str(sample["candidate_id"]), []).append(sample)
    sections = []
    for candidate in report["candidates"]:
        candidate_id = str(candidate["candidate_id"])
        sample_blocks = []
        for sample in samples_by_candidate.get(candidate_id, []):
            image_name = Path(sample["output_image_path"]).name
            readback = {
                "text": sample["text"],
                "font_family": sample["font_family"],
                "font_file_status": sample["font_file_status"],
                "font_size_status": sample["font_size_status"],
                "requested_font_size": sample["requested_font_size"],
                "outline": sample["outline"],
                "shadow": sample["shadow"],
                "safe_area_status": sample["safe_area_status"],
                "wrapped_lines": sample["wrapped_lines"],
                "body_weight_note": sample.get("body_weight_note"),
                "outline_balance_role": sample.get("outline_balance_role"),
                "emoji_evaluation_scope": sample.get("emoji_evaluation_scope"),
                "production_subtitle_design_acceptance": sample[
                    "production_subtitle_design_acceptance"
                ],
            }
            sample_blocks.append(
                "<figure>"
                f"<img src=\"{html.escape(image_name)}\" alt=\"{html.escape(candidate_id)} sample\">"
                "<figcaption><pre>"
                f"{html.escape(json.dumps(readback, ensure_ascii=False, indent=2))}"
                "</pre></figcaption>"
                "</figure>"
            )
        sections.append(
            "<section class=\"candidate\">"
            f"<h2>{html.escape(candidate['display_name'])}</h2>"
            f"<p>{html.escape(candidate['decoration_note'])}</p>"
            f"<p>body weight: {html.escape(str(candidate.get('body_weight_note', '')))}</p>"
            f"<p>outline balance: {html.escape(str(candidate.get('outline_balance_role', '')))}</p>"
            f"<p>emoji: {html.escape(str(candidate.get('emoji_evaluation_scope', '')))}</p>"
            f"<p>font paths: {html.escape(', '.join(candidate['requested_font_paths']))}</p>"
            f"{''.join(sample_blocks)}"
            "</section>"
        )
    contact_sheet = Path(report["outputs"]["contact_sheet"]).name
    title = str(report.get("html_title") or "Subtitle Typography Decoration Comparison")
    source_notice = str(
        report.get("source_notice")
        or "Source human readback: adjust_boundary. ED-10g comparison response: small_adjustment."
    )
    decision_packet_key = str(
        report.get("decision_packet_key") or "small_adjustment_decision_packet"
    )
    decision_packet_title = str(
        report.get("decision_packet_title") or "Small Adjustment Decision Packet"
    )
    decision_packet = report.get(decision_packet_key) or report.get(
        "small_adjustment_decision_packet"
    )
    body = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; color: #20242a; background: #f5f7f9; }}
    .notice {{ padding: 12px 14px; border: 1px solid #aab5c0; background: #fff; }}
    .candidate {{ margin: 24px 0; padding: 16px; background: #fff; border: 1px solid #d4dde6; }}
    figure {{ margin: 16px 0; }}
    img {{ max-width: 100%; border: 1px solid #b8c2cc; background: #222; }}
    pre {{ white-space: pre-wrap; background: #eef2f5; padding: 10px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p class="notice">review_only=true / production_candidate=false / production_subtitle_design_acceptance=false / rights_status=pending</p>
  <p class="notice">{html.escape(source_notice)}</p>
  <p class="notice">This artifact uses generated review-only PNGs. It does not mutate source media, transcript, official subtitle evidence, rights, publishing, public use, or upload state.</p>
  <h2>Contact Sheet</h2>
  <p><a href="{html.escape(contact_sheet)}"><img src="{html.escape(contact_sheet)}" alt="typography decoration contact sheet"></a></p>
  <h2>Decision Question</h2>
  <p>{html.escape(str(report["next_decision_question"]))}</p>
  <h2>Next Diagnostic Overlay Proof Route</h2>
  <pre>{html.escape(json.dumps(report["next_diagnostic_overlay_proof_route"], ensure_ascii=False, indent=2))}</pre>
  <h2>{html.escape(decision_packet_title)}</h2>
  <pre>{html.escape(json.dumps(decision_packet, ensure_ascii=False, indent=2))}</pre>
  <h2>Fixed / Varied Axes</h2>
  <pre>{html.escape(json.dumps(report["comparison_axes"], ensure_ascii=False, indent=2))}</pre>
  {''.join(sections)}
</body>
</html>
"""
    path.write_text(body, encoding="utf-8")


def _open_comparison_script(html_filename: str = "subtitle_typography_decoration_comparison_report.html") -> str:
    return """$ErrorActionPreference = 'Stop'
$previewRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$index = Join-Path $previewRoot '%s'
if (-not (Test-Path -LiteralPath $index)) {
  throw "%s not found next to open_comparison.ps1"
}
Invoke-Item -LiteralPath $index
""" % (html_filename, html_filename)


def _rgb_hex(value: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{component:02x}" for component in value)


def _display_path(path: Path, base: Path) -> str:
    try:
        text = path.resolve().relative_to(base.resolve())
    except (OSError, ValueError):
        text = path
    return str(text).replace("\\", "/")


def _select_font() -> tuple[str, str | None, str]:
    for path in FONT_CANDIDATES:
        if path.exists():
            return path.stem, str(path), "font_file_found"
    return "Pillow default", None, "fallback_default_font_no_japanese_font_file_found"


def _load_font(font_path: str | None, font_size: int):
    if font_path:
        return ImageFont.truetype(font_path, font_size)
    return ImageFont.load_default(size=font_size)


def _render_sample(
    *,
    output_dir: Path,
    canvas_size: tuple[int, int],
    spec: ModeSpec,
    text: str,
    text_index: int,
    font_family: str,
    font_path: str | None,
    font_fallback_status: str,
    guide_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    width, height = canvas_size
    font_size = max(16, round(height * spec.font_ratio))
    stroke_width = max(2, round(font_size * spec.stroke_ratio))
    shadow_offset = max(1, round(font_size * spec.shadow_offset_ratio))
    safe_x = round(width * spec.safe_x_ratio)
    safe_y = round(height * spec.safe_y_ratio)
    line_height = max(font_size, round(font_size * spec.line_height_ratio))
    spacing = max(0, line_height - font_size)
    font = _load_font(font_path, font_size)
    badge_style_inputs = None

    image = Image.new("RGB", (width, height), (32, 35, 39))
    draw = ImageDraw.Draw(image)
    _draw_reference_background(draw, width=width, height=height, safe_x=safe_x, safe_y=safe_y)

    max_text_width = max(120, width - (safe_x * 2))
    if spec.mode in {"dialogue_badge_left", "speaker_badge_stack"}:
        badge_w = max(48, round(font_size * 1.0))
        badge_gap = max(8, round(font_size * 0.3))
        max_text_width = max(120, width - safe_x - badge_w - badge_gap - safe_x)

    wrap_result = _wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_text_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    wrapped_text = wrap_result.text
    line_count = len(wrap_result.lines) or 1
    origin_bbox = _text_bbox_at_origin(
        draw=draw,
        text=wrapped_text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    text_w = origin_bbox[2] - origin_bbox[0]
    text_h = origin_bbox[3] - origin_bbox[1]

    badge_bbox = None
    if spec.mode == "dialogue_badge_left":
        badge_w = max(48, round(font_size * 1.0))
        badge_h = max(32, round(font_size * 0.7))
        badge_gap = max(8, round(font_size * 0.3))
        badge_style_inputs = _badge_style_inputs(
            badge_width=badge_w,
            badge_height=badge_h,
            badge_gap=badge_gap,
            badge_font_size=max(12, round(font_size * 0.44)),
            width_formula="max(48, round(font_size * 1.0))",
            height_formula="max(32, round(font_size * 0.7))",
            gap_formula="max(8, round(font_size * 0.3))",
            font_size_formula="max(12, round(font_size * 0.44))",
        )
        text_x, text_y = _origin_for_target_bbox(
            origin_bbox,
            target_left=safe_x + badge_w + badge_gap,
            target_bottom=height - safe_y,
        )
        badge_x = safe_x
        first_line_top = text_y + origin_bbox[1]
        badge_center_y = first_line_top + round(line_height * 0.52)
        badge_y = badge_center_y - round(badge_h / 2)
        badge_bbox = _draw_badge(
            draw,
            label="SPK",
            xy=(badge_x, badge_y),
            size=(badge_w, badge_h),
            font_path=font_path,
            font_size=max(12, round(font_size * 0.44)),
        )
    elif spec.mode == "speaker_badge_stack":
        badge_w = max(52, round(font_size * 0.9))
        badge_h = max(30, round(font_size * 0.52))
        badge_gap = max(8, round(font_size * 0.26))
        stack_gap = max(6, round(font_size * 0.12))
        badge_style_inputs = _badge_style_inputs(
            badge_width=badge_w,
            badge_height=badge_h,
            badge_gap=badge_gap,
            badge_font_size=max(12, round(font_size * 0.38)),
            width_formula="max(52, round(font_size * 0.9))",
            height_formula="max(30, round(font_size * 0.52))",
            gap_formula="max(8, round(font_size * 0.26))",
            font_size_formula="max(12, round(font_size * 0.38))",
            stack_gap=stack_gap,
            stack_gap_formula="max(6, round(font_size * 0.12))",
        )
        text_x, text_y = _origin_for_target_bbox(
            origin_bbox,
            target_left=safe_x + badge_w + badge_gap,
            target_bottom=height - safe_y,
        )
        text_top = text_y + origin_bbox[1]
        stack_y = text_top + round(line_height * 0.12)
        first = _draw_badge(
            draw,
            label="A",
            xy=(safe_x, stack_y),
            size=(badge_w, badge_h),
            font_path=font_path,
            font_size=max(12, round(font_size * 0.38)),
        )
        second = _draw_badge(
            draw,
            label="B",
            xy=(safe_x, stack_y + badge_h + stack_gap),
            size=(badge_w, badge_h),
            font_path=font_path,
            font_size=max(12, round(font_size * 0.38)),
        )
        badge_bbox = _union_bbox(first, second)
    elif spec.mode == "reaction_caption":
        target_left = round((width - text_w) / 2)
        target_top = _clamp(
            round(height * 0.66) - round(text_h / 2),
            safe_y,
            height - safe_y - text_h,
        )
        text_x, text_y = _origin_for_target_bbox(
            origin_bbox,
            target_left=target_left,
            target_top=target_top,
        )
    else:
        target_left = round((width - text_w) / 2)
        text_x, text_y = _origin_for_target_bbox(
            origin_bbox,
            target_left=target_left,
            target_bottom=height - safe_y,
        )

    _draw_text_with_shadow(
        draw,
        xy=(text_x, text_y),
        text=wrapped_text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
        shadow_offset=shadow_offset,
    )
    measured_bbox = draw.multiline_textbbox(
        (text_x, text_y),
        wrapped_text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    guide_overlay_readback = None
    if guide_profile:
        guide_overlay_readback = _build_guide_overlay_readback(
            guide_profile=guide_profile,
            mode=spec.mode,
            canvas_size=(width, height),
            safe_x=safe_x,
            safe_y=safe_y,
            font_size=font_size,
            line_height=line_height,
            line_count=line_count,
            text_bbox=measured_bbox,
            badge_bbox=badge_bbox,
            badge_gap=(
                max(8, round(font_size * 0.3))
                if spec.mode == "dialogue_badge_left"
                else None
            ),
        )
        _draw_guide_overlay(draw, guide_overlay_readback)
    variant_slug = ".guide" if guide_profile else ""
    output_path = output_dir / f"subtitle_style_spike.{spec.mode}.{text_index:02d}{variant_slug}.png"
    image.save(output_path)

    safe_area_status = _bbox_inside_safe_area(
        measured_bbox,
        canvas_size=(width, height),
        safe_x=safe_x,
        safe_y=safe_y,
    )
    style_inputs = _style_inputs_readback(
        spec=spec,
        canvas_size=(width, height),
        font_family=font_family,
        font_path=font_path,
        font_fallback_status=font_fallback_status,
        font_size=font_size,
        stroke_width=stroke_width,
        shadow_offset=shadow_offset,
        safe_x=safe_x,
        safe_y=safe_y,
        line_height=line_height,
        badge_style_inputs=badge_style_inputs,
    )
    computed_layout = _computed_layout_readback(
        spec=spec,
        max_text_width=max_text_width,
        wrap_result=wrap_result,
        origin_bbox=origin_bbox,
        text_xy=(text_x, text_y),
        badge_bbox=badge_bbox,
        badge_style_inputs=badge_style_inputs,
    )
    measured_output = _measured_output_readback(
        measured_bbox=measured_bbox,
        safe_area_status=safe_area_status,
        canvas_size=(width, height),
    )
    return {
        "output_image_path": output_path.as_posix(),
        "sample_variant": "guide_overlay" if guide_profile else "clean",
        "canvas_size": {"width": width, "height": height},
        "subtitle_mode": spec.mode,
        "text": text,
        "wrapped_text": wrapped_text,
        "wrapped_lines": wrap_result.lines,
        "wrap_algorithm": computed_layout["wrap_algorithm"],
        "candidate_breaks": wrap_result.candidate_breaks,
        "selected_break_reason": wrap_result.selected_break_reason,
        "orphan_prevention_applied": wrap_result.orphan_prevention_applied,
        "suffix_tail_prevention_applied": wrap_result.suffix_tail_prevention_applied,
        "suspicious_tail_line_present": wrap_result.suspicious_tail_line_present,
        "suspicious_tail_lines": wrap_result.suspicious_tail_lines,
        "measured_width_by_line": wrap_result.measured_width_by_line,
        "font_family": font_family,
        "font_file": font_path,
        "font_file_status": font_fallback_status,
        "font_fallback_status": font_fallback_status,
        "requested_font_size": font_size,
        "style_inputs": style_inputs,
        "computed_layout": computed_layout,
        "measured_output": measured_output,
        "measured_bbox": _bbox_dict(measured_bbox),
        "badge_bbox": _bbox_dict(badge_bbox) if badge_bbox else None,
        "safe_area_margin": {"x": safe_x, "y": safe_y},
        "safe_area_status": safe_area_status,
        "line_height": line_height,
        "line_count": line_count,
        "grid_model": GRID_READBACK["grid_model"],
        "layout_anchor": spec.anchor,
        "snap_to_grid": False,
        "text_bbox_grid_coords": None,
        "badge_bbox_grid_coords": None,
        "safe_area_grid_coords": None,
        "layout_authority": GRID_READBACK["actual_layout_authority"],
        "wrapping_authority": GRID_READBACK["wrapping_authority"],
        "outline": {
            "stroke_width": stroke_width,
            "stroke_fill": "#000000",
            "renderer_term": "Pillow stroke_width, not ASS/YMM4/Premiere value",
        },
        "shadow": {
            "offset_px": shadow_offset,
            "fill": "rgba(0,0,0,160)",
            "renderer_term": "Pillow shadow offset, not ASS/YMM4/Premiere value",
        },
        "review_only": True,
        "production_candidate": False,
        "production_compatible": False,
        "target_renderer_candidate": spec.target_renderer_candidate,
        "anchor_rule": spec.anchor,
        "transfer_risk": spec.transfer_risk,
        "visible_element_authority_ids": _visible_element_authority_ids_for_mode(
            spec.mode,
            guide_profile=guide_profile,
        ),
        "speaker_identity_asset_status": _speaker_identity_asset_status(spec.mode),
        "guide_overlay": guide_overlay_readback
        or {
            "enabled": False,
            "sample_variant": "clean",
            "human_review_note": "clean sample without guide overlay lines",
        },
    }


def _draw_reference_background(draw, *, width: int, height: int, safe_x: int, safe_y: int) -> None:
    draw.rectangle((0, 0, width, height), fill=(36, 39, 44))


def _badge_style_inputs(
    *,
    badge_width: int,
    badge_height: int,
    badge_gap: int,
    badge_font_size: int,
    width_formula: str,
    height_formula: str,
    gap_formula: str,
    font_size_formula: str,
    stack_gap: int | None = None,
    stack_gap_formula: str | None = None,
) -> dict[str, Any]:
    readback: dict[str, Any] = {
        "badge_width": {
            "value": badge_width,
            "source": "formula_from_font_size_with_minimum",
            "formula": width_formula,
        },
        "badge_height": {
            "value": badge_height,
            "source": "formula_from_font_size_with_minimum",
            "formula": height_formula,
        },
        "badge_text_gap": {
            "value": badge_gap,
            "source": "formula_from_font_size_with_minimum",
            "formula": gap_formula,
        },
        "badge_font_size": {
            "value": badge_font_size,
            "source": "formula_from_font_size_with_minimum",
            "formula": font_size_formula,
        },
        "production_identity_asset": False,
    }
    if stack_gap is not None:
        readback["stack_gap"] = {
            "value": stack_gap,
            "source": "formula_from_font_size_with_minimum",
            "formula": stack_gap_formula,
        }
    return readback


def _style_inputs_readback(
    *,
    spec: ModeSpec,
    canvas_size: tuple[int, int],
    font_family: str,
    font_path: str | None,
    font_fallback_status: str,
    font_size: int,
    stroke_width: int,
    shadow_offset: int,
    safe_x: int,
    safe_y: int,
    line_height: int,
    badge_style_inputs: dict[str, Any] | None,
) -> dict[str, Any]:
    width, height = canvas_size
    return {
        "mode": spec.mode,
        "mode_purpose": spec.purpose,
        "mode_token_constants": {
            "font_ratio": spec.font_ratio,
            "stroke_ratio": spec.stroke_ratio,
            "shadow_offset_ratio": spec.shadow_offset_ratio,
            "safe_x_ratio": spec.safe_x_ratio,
            "safe_y_ratio": spec.safe_y_ratio,
            "line_height_ratio": spec.line_height_ratio,
            "anchor": spec.anchor,
        },
        "font": {
            "family": font_family,
            "file": font_path,
            "fallback_status": font_fallback_status,
            "requested_font_size": {
                "value": font_size,
                "source": "formula_from_frame_height_and_mode_constant",
                "formula": "max(16, round(frame_height * mode.font_ratio))",
                "frame_height": height,
            },
        },
        "outline": {
            "stroke_width": {
                "value": stroke_width,
                "source": "formula_from_font_size_and_mode_constant",
                "formula": "max(2, round(font_size * mode.stroke_ratio))",
            }
        },
        "shadow": {
            "offset_px": {
                "value": shadow_offset,
                "source": "formula_from_font_size_and_mode_constant",
                "formula": "max(1, round(font_size * mode.shadow_offset_ratio))",
            }
        },
        "safe_area_margin": {
            "x": {
                "value": safe_x,
                "source": "formula_from_frame_width_and_mode_constant",
                "formula": "round(frame_width * mode.safe_x_ratio)",
                "frame_width": width,
            },
            "y": {
                "value": safe_y,
                "source": "formula_from_frame_height_and_mode_constant",
                "formula": "round(frame_height * mode.safe_y_ratio)",
                "frame_height": height,
            },
        },
        "line_height": {
            "value": line_height,
            "source": "formula_from_font_size_and_mode_constant",
            "formula": "max(font_size, round(font_size * mode.line_height_ratio))",
        },
        "badge": badge_style_inputs,
        "not_measured_output": True,
    }


def _computed_layout_readback(
    *,
    spec: ModeSpec,
    max_text_width: int,
    wrap_result: WrapResult,
    origin_bbox: tuple[int, int, int, int],
    text_xy: tuple[int, int],
    badge_bbox: tuple[int, int, int, int] | None,
    badge_style_inputs: dict[str, Any] | None,
) -> dict[str, Any]:
    wrapped_text = wrap_result.text
    lines = wrap_result.lines
    text_x, text_y = text_xy
    readback: dict[str, Any] = {
        "layout_anchor": spec.anchor,
        "wrap_algorithm": {
            "name": wrap_result.algorithm_name,
            "source_function": "_wrap_text_to_width",
            "max_text_width": max_text_width,
            "authority": GRID_READBACK["wrapping_authority"],
            "not_character_count_only": True,
            "not_grid_based": True,
            "candidate_break_strategy": (
                "Japanese punctuation, particle, and phrase-boundary candidates "
                "are preferred only after each candidate prefix passes font bbox "
                "pixel-width measurement."
            ),
            "orphan_prevention": (
                "When a greedy measured break would leave a single visible "
                "Japanese character or kana on the next line, the wrapper uses "
                "an earlier measured-valid break if one exists."
            ),
            "suffix_tail_prevention": (
                "When a measured break would isolate a short Japanese sentence "
                "suffix such as ます or か plus punctuation, the wrapper prefers "
                "a nearby measured-valid break when one exists."
            ),
        },
        "candidate_breaks": wrap_result.candidate_breaks,
        "selected_break_reason": wrap_result.selected_break_reason,
        "selected_breaks": wrap_result.selected_breaks,
        "orphan_prevention_applied": wrap_result.orphan_prevention_applied,
        "suffix_tail_prevention_applied": wrap_result.suffix_tail_prevention_applied,
        "suspicious_tail_line_present": wrap_result.suspicious_tail_line_present,
        "suspicious_tail_lines": wrap_result.suspicious_tail_lines,
        "wrapped_text": wrapped_text,
        "wrapped_lines": lines,
        "line_count": len(lines),
        "measured_width_by_line": wrap_result.measured_width_by_line,
        "text_start_position": {
            "x": text_x,
            "y": text_y,
            "source": "_origin_for_target_bbox result",
        },
        "origin_bbox": {
            **(_bbox_dict(origin_bbox) or {}),
            "source": "draw.multiline_textbbox at origin before final placement",
        },
        "text_position_source": "anchor-specific calculation from origin bbox and safe margins",
        "not_measured_output": True,
    }
    if badge_bbox:
        readback["badge_slot"] = {
            **(_bbox_dict(badge_bbox) or {}),
            "source": "computed placeholder badge rectangle",
            "authority_class": "placeholder",
            "style_inputs": badge_style_inputs,
        }
    return readback


def _measured_output_readback(
    *,
    measured_bbox: tuple[int, int, int, int],
    safe_area_status: dict[str, Any],
    canvas_size: tuple[int, int],
) -> dict[str, Any]:
    bbox = _bbox_dict(measured_bbox) or {}
    return {
        "measurement_method": "Pillow ImageDraw.multiline_textbbox after text placement",
        "source_function": "draw.multiline_textbbox",
        "manual_override": False,
        "hardcoded_per_sample": False,
        "design_target": False,
        "measured_bbox": bbox,
        "rendered_bbox_dimensions": {
            "width": bbox.get("width"),
            "height": bbox.get("height"),
        },
        "safe_area_status": safe_area_status,
        "overflow_readback": {
            "left_overflow_px": safe_area_status["left_overflow_px"],
            "right_overflow_px": safe_area_status["right_overflow_px"],
            "top_overflow_px": safe_area_status["top_overflow_px"],
            "bottom_overflow_px": safe_area_status["bottom_overflow_px"],
        },
        "canvas_size": {"width": canvas_size[0], "height": canvas_size[1]},
    }


def _draw_badge(draw, *, label: str, xy: tuple[int, int], size: tuple[int, int], font_path: str | None, font_size: int):
    x, y = xy
    w, h = size
    draw.rounded_rectangle((x, y, x + w, y + h), radius=4, fill=(255, 210, 0), outline=(0, 0, 0), width=2)
    badge_font = _load_font(font_path, font_size)
    bbox = draw.textbbox((0, 0), label, font=badge_font, stroke_width=0)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (x + round((w - tw) / 2), y + round((h - th) / 2) - 2),
        label,
        font=badge_font,
        fill=(255, 255, 255),
        stroke_width=1,
        stroke_fill=(0, 0, 0),
    )
    return (x, y, x + w, y + h)


def _draw_text_with_shadow(
    draw,
    *,
    xy: tuple[int, int],
    text: str,
    font,
    spacing: int,
    stroke_width: int,
    shadow_offset: int,
) -> None:
    x, y = xy
    draw.multiline_text(
        (x + shadow_offset, y + shadow_offset),
        text,
        font=font,
        fill=(0, 0, 0),
        spacing=spacing,
        stroke_width=stroke_width,
        stroke_fill=(0, 0, 0),
    )
    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255),
        spacing=spacing,
        stroke_width=stroke_width,
        stroke_fill=(0, 0, 0),
    )


def _wrap_text_to_width(
    *,
    draw,
    text: str,
    font,
    max_width: int,
    spacing: int,
    stroke_width: int,
) -> WrapResult:
    initial_width = _text_size(
        draw=draw,
        text=text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]
    if initial_width <= max_width:
        return WrapResult(
            text=text,
            lines=[text],
            algorithm_name=JAPANESE_WRAP_ALGORITHM,
            candidate_breaks=[],
            selected_break_reason="whole_text_fits_font_bbox",
            selected_breaks=[],
            orphan_prevention_applied=False,
            suffix_tail_prevention_applied=False,
            suspicious_tail_line_present=False,
            suspicious_tail_lines=[],
            measured_width_by_line=[initial_width],
        )

    lines: list[str] = []
    candidate_breaks: list[dict[str, Any]] = []
    selected_breaks: list[dict[str, Any]] = []
    orphan_prevention_applied = False
    suffix_tail_prevention_applied = False
    remaining = text
    line_number = 1

    while remaining:
        remaining_width = _text_size(
            draw=draw,
            text=remaining,
            font=font,
            spacing=spacing,
            stroke_width=stroke_width,
        )[0]
        if remaining_width <= max_width:
            lines.append(remaining)
            break

        candidates = _build_wrap_candidates(
            draw=draw,
            text=remaining,
            font=font,
            max_width=max_width,
            spacing=spacing,
            stroke_width=stroke_width,
            line_number=line_number,
        )
        selectable = [
            candidate
            for candidate in candidates
            if candidate["fits_max_width"] and candidate["remaining_text"]
        ]
        if not selectable:
            forced_line = remaining[0]
            forced_width = _text_size(
                draw=draw,
                text=forced_line,
                font=font,
                spacing=spacing,
                stroke_width=stroke_width,
            )[0]
            forced = {
                "line_number": line_number,
                "break_index": 1,
                "line_text": forced_line,
                "remaining_text": remaining[1:],
                "measured_width": forced_width,
                "max_width": max_width,
                "fits_max_width": forced_width <= max_width,
                "reason": "forced_single_character_no_measured_alternative",
                "priority": 0,
                "would_leave_one_character_orphan": _visible_char_count(remaining[1:]) == 1,
                "would_leave_suspicious_tail_line": _is_suspicious_tail_line(remaining[1:]),
                "tail_line_status": _tail_line_status(remaining[1:]),
                "next_line_starts_with_avoided_char": bool(remaining[1:] and remaining[1] in JAPANESE_AVOID_LINE_START),
                "selected": True,
                "selection_reason": "forced_single_character_no_measured_alternative",
            }
            candidate_breaks.extend(candidates)
            selected_breaks.append(forced)
            lines.append(forced_line)
            remaining = remaining[1:]
            line_number += 1
            continue

        selected, prevented_orphan, prevented_suffix_tail = _select_wrap_candidate(selectable)
        if prevented_orphan:
            orphan_prevention_applied = True
        if prevented_suffix_tail:
            suffix_tail_prevention_applied = True
        selection_reason = (
            "orphan_prevention_shifted_break"
            if prevented_orphan
            else "suffix_tail_prevention_shifted_break"
            if prevented_suffix_tail
            else selected["reason"]
        )
        for candidate in candidates:
            candidate_breaks.append(
                {
                    **candidate,
                    "selected": (
                        candidate["line_number"] == selected["line_number"]
                        and candidate["break_index"] == selected["break_index"]
                    ),
                    "selection_reason": selection_reason
                    if (
                        candidate["line_number"] == selected["line_number"]
                        and candidate["break_index"] == selected["break_index"]
                    )
                    else None,
                }
            )
        selected_breaks.append({**selected, "selected": True, "selection_reason": selection_reason})
        lines.append(selected["line_text"])
        remaining = selected["remaining_text"]
        line_number += 1

    measured_width_by_line = [
        _text_size(draw=draw, text=line, font=font, spacing=spacing, stroke_width=stroke_width)[0]
        for line in lines
    ]
    suspicious_tail_lines = _suspicious_tail_lines(lines)
    return WrapResult(
        text="\n".join(lines),
        lines=lines,
        algorithm_name=JAPANESE_WRAP_ALGORITHM,
        candidate_breaks=candidate_breaks,
        selected_break_reason=(
            "orphan_prevention_shifted_break"
            if orphan_prevention_applied
            else "suffix_tail_prevention_shifted_break"
            if suffix_tail_prevention_applied
            else (selected_breaks[0]["selection_reason"] if selected_breaks else "whole_text_fits_font_bbox")
        ),
        selected_breaks=selected_breaks,
        orphan_prevention_applied=orphan_prevention_applied,
        suffix_tail_prevention_applied=suffix_tail_prevention_applied,
        suspicious_tail_line_present=bool(suspicious_tail_lines),
        suspicious_tail_lines=suspicious_tail_lines,
        measured_width_by_line=measured_width_by_line,
    )


def _build_wrap_candidates(
    *,
    draw,
    text: str,
    font,
    max_width: int,
    spacing: int,
    stroke_width: int,
    line_number: int,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for break_index in range(1, len(text) + 1):
        line_text = text[:break_index]
        remaining_text = text[break_index:]
        measured_width = _text_size(
            draw=draw,
            text=line_text,
            font=font,
            spacing=spacing,
            stroke_width=stroke_width,
        )[0]
        reason, priority = _classify_japanese_break(text, break_index)
        candidates.append(
            {
                "line_number": line_number,
                "break_index": break_index,
                "line_text": line_text,
                "remaining_text": remaining_text,
                "measured_width": measured_width,
                "max_width": max_width,
                "fits_max_width": measured_width <= max_width,
                "reason": reason,
                "priority": priority,
                "would_leave_one_character_orphan": _visible_char_count(remaining_text) == 1,
                "would_leave_suspicious_tail_line": _is_suspicious_tail_line(remaining_text),
                "tail_line_status": _tail_line_status(remaining_text),
                "next_line_starts_with_avoided_char": bool(
                    remaining_text and remaining_text[0] in JAPANESE_AVOID_LINE_START
                ),
                "selected": False,
                "selection_reason": None,
            }
        )
    return candidates


def _select_wrap_candidate(
    candidates: list[dict[str, Any]],
) -> tuple[dict[str, Any], bool, bool]:
    greedy = max(candidates, key=lambda candidate: (candidate["break_index"], candidate["measured_width"]))
    near_limit_start = max(1, greedy["break_index"] - max(3, round(greedy["break_index"] * 0.25)))
    near_limit = [candidate for candidate in candidates if candidate["break_index"] >= near_limit_start]
    pool = near_limit or candidates

    clean_near_limit = [
        candidate
        for candidate in pool
        if not candidate["would_leave_one_character_orphan"]
        and not candidate["next_line_starts_with_avoided_char"]
        and not candidate["would_leave_suspicious_tail_line"]
    ]
    if clean_near_limit:
        selected = max(
            clean_near_limit,
            key=lambda candidate: (
                candidate["priority"],
                candidate["break_index"],
                candidate["measured_width"],
            ),
        )
    else:
        clean_anywhere = [
            candidate
            for candidate in candidates
            if not candidate["would_leave_one_character_orphan"]
            and not candidate["next_line_starts_with_avoided_char"]
            and not candidate["would_leave_suspicious_tail_line"]
        ]
        if clean_anywhere:
            selected = max(
                clean_anywhere,
                key=lambda candidate: (
                    candidate["break_index"],
                    candidate["priority"],
                    candidate["measured_width"],
                ),
            )
        else:
            non_orphan = [
                candidate
                for candidate in pool
                if not candidate["would_leave_one_character_orphan"]
                and not candidate["next_line_starts_with_avoided_char"]
            ]
            if not non_orphan:
                non_orphan = [
                    candidate
                    for candidate in candidates
                    if not candidate["would_leave_one_character_orphan"]
                    and not candidate["next_line_starts_with_avoided_char"]
                ]
            if not non_orphan:
                non_orphan = [candidate for candidate in pool if not candidate["would_leave_one_character_orphan"]]
            if not non_orphan:
                non_orphan = candidates

            selected = max(
                non_orphan,
                key=lambda candidate: (
                    candidate["priority"],
                    candidate["break_index"],
                    candidate["measured_width"],
                ),
            )
    prevented_orphan = (
        greedy["would_leave_one_character_orphan"]
        and not selected["would_leave_one_character_orphan"]
        and selected["break_index"] != greedy["break_index"]
    )
    prevented_suffix_tail = (
        greedy["would_leave_suspicious_tail_line"]
        and not selected["would_leave_suspicious_tail_line"]
        and selected["break_index"] != greedy["break_index"]
    )
    return selected, prevented_orphan, prevented_suffix_tail


def _classify_japanese_break(text: str, break_index: int) -> tuple[str, int]:
    if break_index >= len(text):
        return "end_of_text", 0
    prefix = text[:break_index]
    next_char = text[break_index]
    if next_char in JAPANESE_AVOID_LINE_START:
        return "avoid_japanese_line_start_character", 1
    if prefix[-1] in JAPANESE_BREAK_AFTER_PUNCTUATION:
        return "japanese_punctuation_boundary", 90
    if any(prefix.endswith(ending) for ending in JAPANESE_PHRASE_ENDINGS):
        return "japanese_phrase_boundary", 70
    if any(prefix.endswith(particle) for particle in JAPANESE_PARTICLE_BREAKS):
        return "japanese_particle_boundary", 60
    return "measured_width_limit", 10


def _visible_char_count(text: str) -> int:
    return sum(1 for char in text if not char.isspace())


def _tail_core(text: str) -> str:
    return "".join(
        char
        for char in text.strip()
        if not char.isspace() and char not in JAPANESE_TAIL_PUNCTUATION
    )


def _is_suspicious_tail_line(text: str) -> bool:
    core = _tail_core(text)
    if not core:
        return bool(text.strip())
    if core in JAPANESE_SUSPICIOUS_TAIL_CORES:
        return True
    if core.endswith("ます") and _visible_char_count(core) <= 3:
        return True
    if core.endswith("です") and _visible_char_count(core) <= 3:
        return True
    return False


def _tail_line_status(text: str) -> str:
    return "suspicious_suffix_tail" if _is_suspicious_tail_line(text) else "ok"


def _suspicious_tail_lines(lines: list[str]) -> list[str]:
    if len(lines) < 2:
        return []
    return [line for line in lines[1:] if _is_suspicious_tail_line(line)]


def _text_size(*, draw, text: str, font, spacing: int, stroke_width: int) -> tuple[int, int]:
    bbox = _text_bbox_at_origin(
        draw=draw,
        text=text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _text_bbox_at_origin(*, draw, text: str, font, spacing: int, stroke_width: int) -> tuple[int, int, int, int]:
    return draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )


def _origin_for_target_bbox(
    origin_bbox: tuple[int, int, int, int],
    *,
    target_left: int,
    target_top: int | None = None,
    target_bottom: int | None = None,
) -> tuple[int, int]:
    if target_top is None and target_bottom is None:
        raise ValueError("target_top or target_bottom is required")
    x = int(target_left - origin_bbox[0])
    if target_bottom is not None:
        y = int(target_bottom - origin_bbox[3])
    else:
        y = int(target_top - origin_bbox[1])
    return x, y


def _clamp(value: int, lower: int, upper: int) -> int:
    if upper < lower:
        return lower
    return max(lower, min(upper, value))


def _bbox_inside_safe_area(
    bbox: tuple[int, int, int, int],
    *,
    canvas_size: tuple[int, int],
    safe_x: int,
    safe_y: int,
) -> dict[str, Any]:
    width, height = canvas_size
    left, top, right, bottom = bbox
    inside = left >= safe_x and right <= width - safe_x and top >= safe_y and bottom <= height - safe_y
    return {
        "text_bbox_inside_safe_area": inside,
        "left_overflow_px": max(0, safe_x - left),
        "right_overflow_px": max(0, right - (width - safe_x)),
        "top_overflow_px": max(0, safe_y - top),
        "bottom_overflow_px": max(0, bottom - (height - safe_y)),
    }


def _bbox_dict(bbox: tuple[int, int, int, int] | None) -> dict[str, int] | None:
    if bbox is None:
        return None
    left, top, right, bottom = [int(v) for v in bbox]
    return {
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom,
        "width": right - left,
        "height": bottom - top,
    }


def _union_bbox(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def _build_guide_overlay_readback(
    *,
    guide_profile: dict[str, Any],
    mode: str,
    canvas_size: tuple[int, int],
    safe_x: int,
    safe_y: int,
    font_size: int,
    line_height: int,
    line_count: int,
    text_bbox: tuple[int, int, int, int],
    badge_bbox: tuple[int, int, int, int] | None,
    badge_gap: int | None,
) -> dict[str, Any]:
    width, height = canvas_size
    text_left, text_top, text_right, text_bottom = text_bbox
    bottom_baseline_y = height - safe_y - max(2, round(font_size * 0.12))
    one_line_baselines = [
        {
            "line_index": 1,
            "y": bottom_baseline_y,
            "authority_class": "visual_guide_only",
            "meaning": "bottom-zone one-line target guide, not font baseline authority",
        }
    ]
    two_line_baselines = [
        {
            "line_index": 1,
            "y": bottom_baseline_y - line_height,
            "authority_class": "visual_guide_only",
            "meaning": "bottom-zone two-line first-line target guide",
        },
        {
            "line_index": 2,
            "y": bottom_baseline_y,
            "authority_class": "visual_guide_only",
            "meaning": "bottom-zone two-line second-line target guide",
        },
    ]
    actual_baselines = [
        {
            "line_index": index,
            "y": text_top + round(font_size * 0.86) + (index - 1) * line_height,
            "authority_class": "measured_readback",
            "meaning": "approximate visual baseline derived from current text bbox and line height",
        }
        for index in range(1, min(3, line_count) + 1)
    ]
    readback: dict[str, Any] = {
        "enabled": True,
        "sample_variant": "guide_overlay",
        "guide_profile": guide_profile["guide_profile"],
        "profile_status": guide_profile["status"],
        "mode": mode,
        "frame_size": {"width": width, "height": height},
        "safe_area": {
            "left": safe_x,
            "top": safe_y,
            "right": width - safe_x,
            "bottom": height - safe_y,
            "authority_class": "measured_readback",
            "meaning": "drawn safe-area rectangle is readback; margin fields constrain placement",
        },
        "center_lines": {
            "vertical": {"x": round(width / 2), "authority_class": "visual_guide_only"},
            "horizontal": {"y": round(height / 2), "authority_class": "visual_guide_only"},
        },
        "thirds_lines": {
            "vertical": [
                {"x": round(width / 3), "authority_class": "visual_guide_only"},
                {"x": round(width * 2 / 3), "authority_class": "visual_guide_only"},
            ],
            "horizontal": [
                {"y": round(height / 3), "authority_class": "visual_guide_only"},
                {"y": round(height * 2 / 3), "authority_class": "visual_guide_only"},
            ],
        },
        "line_height": line_height,
        "baseline_lines": actual_baselines,
        "text_bbox": {
            **(_bbox_dict(text_bbox) or {}),
            "authority_class": "measured_readback",
            "meaning": "measured bitmap text bbox for this generated sample",
        },
        "visible_element_authority_ids": list(guide_profile["visible_element_authority_ids"]),
        "japanese_wrapping_authority": GRID_READBACK["wrapping_authority"],
        "snap_to_grid": False,
    }
    if mode == "bottom_center_emphasis":
        readback["center_alignment"] = {
            "x": round(width / 2),
            "authority_class": "visual_guide_only",
            "meaning": "visual center guide for bottom-centered emphasis review",
        }
        readback["lower_subtitle_zone"] = {
            "left": safe_x,
            "top": round(height * 0.58),
            "right": width - safe_x,
            "bottom": height - safe_y,
            "authority_class": "visual_guide_only",
            "meaning": "review zone only; not a wrapping or placement algorithm",
        }
        readback["mode_baseline_targets"] = {
            "one_line": one_line_baselines,
            "two_line": two_line_baselines,
        }
    if mode == "dialogue_badge_left" and badge_bbox:
        badge = _bbox_dict(badge_bbox) or {}
        readback["badge_slot"] = {
            **badge,
            "authority_class": "placeholder",
            "meaning": "placeholder speaker badge/icon slot; not a real face icon asset",
        }
        readback["badge_center_line"] = {
            "x1": badge["left"],
            "x2": text_right,
            "y": round((badge["top"] + badge["bottom"]) / 2),
            "authority_class": "measured_readback",
            "meaning": "badge center alignment readback for the placeholder badge",
        }
        readback["text_start_x"] = {
            "x": text_left,
            "authority_class": "measured_readback",
            "meaning": "current measured left edge of subtitle text",
        }
        readback["badge_to_text_gap"] = {
            "left": badge["right"],
            "right": text_left,
            "width": badge_gap,
            "authority_class": "measured_readback",
            "meaning": "current placeholder badge-to-text gap readback",
        }
        readback["badge_vertical_alignment_rule"] = (
            "guide reads back current badge center against the first subtitle line; "
            "it is not real face-icon production design"
        )
    return readback


def _draw_guide_overlay(draw, guide: dict[str, Any]) -> None:
    frame = guide["frame_size"]
    width, height = frame["width"], frame["height"]
    safe = guide["safe_area"]
    zone = guide.get("lower_subtitle_zone")
    if zone:
        draw.rectangle(
            (zone["left"], zone["top"], zone["right"], zone["bottom"]),
            outline=GUIDE_COLORS["zone"],
            width=1,
        )
    for line in guide["thirds_lines"]["vertical"]:
        draw.line((line["x"], 0, line["x"], height), fill=GUIDE_COLORS["thirds"], width=1)
    for line in guide["thirds_lines"]["horizontal"]:
        draw.line((0, line["y"], width, line["y"]), fill=GUIDE_COLORS["thirds"], width=1)
    draw.line(
        (guide["center_lines"]["vertical"]["x"], 0, guide["center_lines"]["vertical"]["x"], height),
        fill=GUIDE_COLORS["center"],
        width=1,
    )
    draw.line(
        (0, guide["center_lines"]["horizontal"]["y"], width, guide["center_lines"]["horizontal"]["y"]),
        fill=GUIDE_COLORS["center"],
        width=1,
    )
    draw.rectangle(
        (safe["left"], safe["top"], safe["right"], safe["bottom"]),
        outline=GUIDE_COLORS["safe_area"],
        width=2,
    )
    for baseline in guide.get("baseline_lines", []):
        y = baseline["y"]
        draw.line((safe["left"], y, safe["right"], y), fill=GUIDE_COLORS["baseline"], width=1)
    for baselines in (guide.get("mode_baseline_targets") or {}).values():
        for baseline in baselines:
            y = baseline["y"]
            draw.line((safe["left"], y, safe["right"], y), fill=(180, 145, 0), width=1)
    bbox = guide["text_bbox"]
    draw.rectangle(
        (bbox["left"], bbox["top"], bbox["right"], bbox["bottom"]),
        outline=GUIDE_COLORS["bbox"],
        width=2,
    )
    badge = guide.get("badge_slot")
    if badge:
        draw.rectangle(
            (badge["left"], badge["top"], badge["right"], badge["bottom"]),
            outline=GUIDE_COLORS["badge"],
            width=2,
        )
    badge_center = guide.get("badge_center_line")
    if badge_center:
        draw.line(
            (badge_center["x1"], badge_center["y"], badge_center["x2"], badge_center["y"]),
            fill=GUIDE_COLORS["badge"],
            width=1,
        )
    text_start = guide.get("text_start_x")
    if text_start:
        draw.line((text_start["x"], safe["top"], text_start["x"], safe["bottom"]), fill=GUIDE_COLORS["text_start"], width=1)
    gap = guide.get("badge_to_text_gap")
    if gap:
        y = (guide.get("badge_center_line") or {}).get("y", safe["bottom"])
        draw.line((gap["left"], y, gap["right"], y), fill=GUIDE_COLORS["gap"], width=3)


def _visible_element_authority_ids_for_mode(
    mode: str,
    *,
    guide_profile: dict[str, Any] | None = None,
) -> list[str]:
    ids = [
        "subtitle_text_block",
        "sample_mode_label",
        "sample_background",
        "html_sample_image_frame",
    ]
    if mode in {"dialogue_badge_left", "speaker_badge_stack"}:
        ids.extend(["placeholder_speaker_badge", "speaker_accent_color"])
    if guide_profile:
        ids.extend(guide_profile["visible_element_authority_ids"])
    return ids


def _speaker_identity_asset_status(mode: str) -> dict[str, Any]:
    uses_badge = mode in {"dialogue_badge_left", "speaker_badge_stack"}
    return {
        "uses_speaker_badge": uses_badge,
        "badge_role": "placeholder_speaker_badge" if uses_badge else "not_used",
        "real_face_icons_available": False,
        "real_face_icon_status": "unavailable_to_this_spike_no_asset_input",
        "production_speaker_identity_design": False,
        "human_review_note": (
            "SPK/A/B badges are placeholder speaker badges only; this spike "
            "does not load real face icons or final speaker identity assets."
        )
        if uses_badge
        else "This mode does not display a speaker badge.",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _write_html(path: Path, report: dict[str, Any], *, output_dir: Path) -> None:
    clean_rows = []
    for sample in report["samples"]:
        image_path = Path(sample["output_image_path"])
        rel = image_path.name
        clean_rows.append(
            "<section class=\"sample\">"
            f"<h3>clean sample / {html.escape(sample['subtitle_mode'])}: {html.escape(sample['text'])}</h3>"
            f"<img src=\"{html.escape(rel)}\" alt=\"{html.escape(sample['subtitle_mode'])} sample\">"
            "<pre>"
            f"{html.escape(json.dumps(_sample_readback_for_html(sample), ensure_ascii=False, indent=2))}"
            "</pre>"
            "</section>"
        )
    guide_rows = []
    for sample in report["guide_overlay"]["guided_samples"]:
        image_path = Path(sample["output_image_path"])
        rel = image_path.name
        guide_rows.append(
            "<section class=\"sample guide-sample\">"
            f"<h3>guide overlay sample / {html.escape(sample['subtitle_mode'])}: {html.escape(sample['text'])}</h3>"
            f"<img src=\"{html.escape(rel)}\" alt=\"{html.escape(sample['subtitle_mode'])} guide overlay sample\">"
            "<pre>"
            f"{html.escape(json.dumps(_sample_readback_for_html(sample), ensure_ascii=False, indent=2))}"
            "</pre>"
            "</section>"
        )
    matrix_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(item['candidate'])}</td>"
        f"<td>{html.escape(item['use'])}</td>"
        f"<td>{html.escape(item['strength'])}</td>"
        f"<td>{html.escape(item['weakness'])}</td>"
        f"<td>{html.escape(item['ymm4_premiere_connection'])}</td>"
        f"<td>{html.escape(item['bbox_measurement'])}</td>"
        "</tr>"
        for item in report["renderer_decision_matrix"]
    )
    authority_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(item['element_id'])}</td>"
        f"<td>{html.escape(item['authority_class'])}</td>"
        f"<td>{html.escape(str(item['visible_in_clean_samples']).lower())}</td>"
        f"<td>{html.escape(str(item['visible_in_guide_overlay_samples']).lower())}</td>"
        f"<td>{html.escape(str(item['actual_layout_authority']).lower())}</td>"
        f"<td>{html.escape(str(item['used_in_layout_calculation']).lower())}</td>"
        f"<td>{html.escape(item['meaning_for_reviewer'])}</td>"
        f"<td>{html.escape(item['test_coverage'])}</td>"
        "</tr>"
        for item in report["visible_element_authority"]
    )
    body = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Subtitle Renderer Typography Spike</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; color: #20242a; background: #f6f7f9; }}
    .notice {{ padding: 12px 14px; border: 1px solid #9aa8b5; background: #fff; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; }}
    th, td {{ border: 1px solid #c7d0da; padding: 8px; vertical-align: top; }}
    img {{ max-width: 100%; border: 1px solid #b8c2cc; background: #222; }}
    .sample {{ margin: 22px 0; padding: 14px; background: #fff; border: 1px solid #d5dde5; }}
    .guide-sample {{ border-color: #7a9cc7; }}
    pre {{ white-space: pre-wrap; background: #f0f3f6; padding: 10px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>Subtitle Renderer Typography Spike</h1>
  <p class="notice">review_only: true / production_candidate: false / production_compatible: false</p>
  <p>This report is for renderer and measurement comparison only. It is not a
  production subtitle design, render acceptance, rights approval, publishing
  acceptance, or public-use permission.</p>
  <p class="notice">grid authority: none. The samples do not use snap-to-grid,
  grid cells, grid coordinates, or grid-based wrapping. Layout authority comes
  from measured font bbox, safe-area margin fields, and anchor readback; the
  safe-area rectangle is measured readback.</p>
  <p class="notice">visible element authority is explicit: SPK/A/B badges are
  placeholder speaker badges only, real face icons are unavailable to this
  spike, real face icon asset intake is a separate future slice, and decorative
  or visual-guide elements are not production design.</p>
  <p class="notice">mode semantics: dialogue_badge_left is for normal
  speaker-identified dialogue; bottom_center_emphasis is for emphasized dialogue
  or a strong one-liner; reaction_caption is for punchline, surprise, or instant
  reaction such as 来ねぇ！！; speaker_badge_stack is comparison-only placeholder
  stack work for future multi-speaker face-icon/nameplate design. Repeated text
  across modes is intentional comparison, not a universal style rule.</p>
  <p class="notice">clean samples and guide overlay samples are separate. Guide
  overlays use center lines, safe-area readback, subtitle baseline guides,
  badge/icon slot guides, and bbox overlays only as labeled review aids; they
  do not drive Japanese wrapping.</p>
  <p class="notice">Japanese wrapping uses
  {html.escape(JAPANESE_WRAP_ALGORITHM)}. Candidate punctuation, particle, and
  phrase boundaries are considered only when the candidate line passes
  font/bbox pixel measurement; one-character orphan prevention and suffix-tail
  prevention are recorded per sample.</p>
  <h2>Visible Element Authority</h2>
  <pre>{html.escape(json.dumps(report["visible_element_authority_classes"], ensure_ascii=False, indent=2))}</pre>
  <table>
    <thead>
      <tr><th>element</th><th>class</th><th>clean</th><th>guide overlay</th><th>layout authority</th><th>used in calculation</th><th>meaning</th><th>test coverage</th></tr>
    </thead>
    <tbody>{authority_rows}</tbody>
  </table>
  <h2>Measured Bbox Provenance</h2>
  <pre>{html.escape(json.dumps(report["measured_bbox_provenance"], ensure_ascii=False, indent=2))}</pre>
  <h2>Guide Overlay Contract</h2>
  <pre>{html.escape(json.dumps({k: v for k, v in report["guide_overlay"].items() if k != "guided_samples"}, ensure_ascii=False, indent=2))}</pre>
  <h2>Grid Readback</h2>
  <pre>{html.escape(json.dumps(report["grid_readback"], ensure_ascii=False, indent=2))}</pre>
  <h2>Mode Decision</h2>
  <pre>{html.escape(json.dumps(report["mode_decision"], ensure_ascii=False, indent=2))}</pre>
  <h2>Mode Semantics</h2>
  <pre>{html.escape(json.dumps(report["mode_semantics"], ensure_ascii=False, indent=2))}</pre>
  <h2>Renderer Decision Matrix</h2>
  <table>
    <thead>
      <tr><th>candidate</th><th>use</th><th>strength</th><th>weakness</th><th>YMM4/Premiere</th><th>bbox</th></tr>
    </thead>
    <tbody>{matrix_rows}</tbody>
  </table>
  <h2>Clean Samples</h2>
  {''.join(clean_rows)}
  <h2>Guide Overlay Samples</h2>
  {''.join(guide_rows)}
</body>
</html>
"""
    path.write_text(body, encoding="utf-8")


def _sample_readback_for_html(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "output_image_path": sample["output_image_path"],
        "sample_variant": sample["sample_variant"],
        "canvas_size": sample["canvas_size"],
        "subtitle_mode": sample["subtitle_mode"],
        "text": sample["text"],
        "wrapped_text": sample["wrapped_text"],
        "wrapped_lines": sample["wrapped_lines"],
        "wrap_algorithm": sample["wrap_algorithm"],
        "candidate_breaks": sample["candidate_breaks"],
        "selected_break_reason": sample["selected_break_reason"],
        "orphan_prevention_applied": sample["orphan_prevention_applied"],
        "suffix_tail_prevention_applied": sample["suffix_tail_prevention_applied"],
        "suspicious_tail_line_present": sample["suspicious_tail_line_present"],
        "suspicious_tail_lines": sample["suspicious_tail_lines"],
        "measured_width_by_line": sample["measured_width_by_line"],
        "font_family": sample["font_family"],
        "font_file_status": sample["font_file_status"],
        "font_fallback_status": sample["font_fallback_status"],
        "requested_font_size": sample["requested_font_size"],
        "style_inputs": sample["style_inputs"],
        "computed_layout": sample["computed_layout"],
        "measured_output": sample["measured_output"],
        "measured_bbox": sample["measured_bbox"],
        "safe_area_margin": sample["safe_area_margin"],
        "safe_area_status": sample["safe_area_status"],
        "line_height": sample["line_height"],
        "line_count": sample["line_count"],
        "grid_model": sample["grid_model"],
        "layout_anchor": sample["layout_anchor"],
        "snap_to_grid": sample["snap_to_grid"],
        "text_bbox_grid_coords": sample["text_bbox_grid_coords"],
        "badge_bbox_grid_coords": sample["badge_bbox_grid_coords"],
        "safe_area_grid_coords": sample["safe_area_grid_coords"],
        "layout_authority": sample["layout_authority"],
        "wrapping_authority": sample["wrapping_authority"],
        "outline": sample["outline"],
        "shadow": sample["shadow"],
        "review_only": sample["review_only"],
        "production_candidate": sample["production_candidate"],
        "production_compatible": sample["production_compatible"],
        "target_renderer_candidate": sample["target_renderer_candidate"],
        "visible_element_authority_ids": sample["visible_element_authority_ids"],
        "speaker_identity_asset_status": sample["speaker_identity_asset_status"],
        "guide_overlay": sample["guide_overlay"],
    }


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate subtitle style spike PNG/readback artifacts.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--width", type=int, default=DEFAULT_CANVAS[0])
    parser.add_argument("--height", type=int, default=DEFAULT_CANVAS[1])
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)

    report = build_subtitle_style_spike(
        output_dir=Path(args.output_dir),
        canvas_size=(args.width, args.height),
    )
    if args.format == "json":
        json.dump(
            {
                "outputs": report["outputs"],
                "sample_count": len(report["samples"]),
                "modes": sorted({sample["subtitle_mode"] for sample in report["samples"]}),
                "review_only": report["review_only"],
                "production_candidate": report["production_candidate"],
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        print(f"json: {report['outputs']['json']}")
        print(f"html: {report['outputs']['html']}")
        print(f"samples: {len(report['samples'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
