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
DEFAULT_CANVAS = (1280, 720)
SAMPLE_TEXTS = (
    "来ねぇ！！",
    "この条件、かなり危ないです",
    "まず物件カードを見ます",
    "ここで事故ります",
)
FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
    Path("C:/Windows/Fonts/YuGothB.ttc"),
    Path("C:/Windows/Fonts/meiryob.ttc"),
    Path("C:/Windows/Fonts/msgothic.ttc"),
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

    image = Image.new("RGB", (width, height), (32, 35, 39))
    draw = ImageDraw.Draw(image)
    _draw_reference_background(draw, width=width, height=height, safe_x=safe_x, safe_y=safe_y)

    max_text_width = max(120, width - (safe_x * 2))
    if spec.mode in {"dialogue_badge_left", "speaker_badge_stack"}:
        badge_w = max(48, round(font_size * 1.0))
        badge_gap = max(8, round(font_size * 0.3))
        max_text_width = max(120, width - safe_x - badge_w - badge_gap - safe_x)

    wrapped_text = _wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_text_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )
    line_count = len(wrapped_text.splitlines()) or 1
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
    return {
        "output_image_path": output_path.as_posix(),
        "sample_variant": "guide_overlay" if guide_profile else "clean",
        "canvas_size": {"width": width, "height": height},
        "subtitle_mode": spec.mode,
        "text": text,
        "wrapped_text": wrapped_text,
        "font_family": font_family,
        "font_file": font_path,
        "font_fallback_status": font_fallback_status,
        "requested_font_size": font_size,
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
) -> str:
    if _text_size(draw=draw, text=text, font=font, spacing=spacing, stroke_width=stroke_width)[0] <= max_width:
        return text
    lines: list[str] = []
    current = ""
    for char in text:
        trial = current + char
        width = _text_size(
            draw=draw,
            text=trial,
            font=font,
            spacing=spacing,
            stroke_width=stroke_width,
        )[0]
        if current and width > max_width:
            lines.append(current)
            current = char
        else:
            current = trial
    if current:
        lines.append(current)
    return "\n".join(lines)


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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
  spike, and decorative or visual-guide elements are not production design.</p>
  <p class="notice">clean samples and guide overlay samples are separate. Guide
  overlays use center lines, safe-area readback, subtitle baseline guides,
  badge/icon slot guides, and bbox overlays only as labeled review aids; they
  do not drive Japanese wrapping.</p>
  <h2>Visible Element Authority</h2>
  <pre>{html.escape(json.dumps(report["visible_element_authority_classes"], ensure_ascii=False, indent=2))}</pre>
  <table>
    <thead>
      <tr><th>element</th><th>class</th><th>clean</th><th>guide overlay</th><th>layout authority</th><th>used in calculation</th><th>meaning</th><th>test coverage</th></tr>
    </thead>
    <tbody>{authority_rows}</tbody>
  </table>
  <h2>Guide Overlay Contract</h2>
  <pre>{html.escape(json.dumps({k: v for k, v in report["guide_overlay"].items() if k != "guided_samples"}, ensure_ascii=False, indent=2))}</pre>
  <h2>Grid Readback</h2>
  <pre>{html.escape(json.dumps(report["grid_readback"], ensure_ascii=False, indent=2))}</pre>
  <h2>Mode Decision</h2>
  <pre>{html.escape(json.dumps(report["mode_decision"], ensure_ascii=False, indent=2))}</pre>
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
        "font_family": sample["font_family"],
        "font_fallback_status": sample["font_fallback_status"],
        "requested_font_size": sample["requested_font_size"],
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
