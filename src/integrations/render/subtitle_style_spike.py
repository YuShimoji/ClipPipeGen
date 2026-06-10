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
        "visible_in_default_samples": True,
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
]

VISIBLE_ELEMENT_AUTHORITY_BY_ID = {item["element_id"]: item for item in VISIBLE_ELEMENT_AUTHORITY}


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
    output_path = output_dir / f"subtitle_style_spike.{spec.mode}.{text_index:02d}.png"
    image.save(output_path)

    safe_area_status = _bbox_inside_safe_area(
        measured_bbox,
        canvas_size=(width, height),
        safe_x=safe_x,
        safe_y=safe_y,
    )
    return {
        "output_image_path": output_path.as_posix(),
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
        "visible_element_authority_ids": _visible_element_authority_ids_for_mode(spec.mode),
        "speaker_identity_asset_status": _speaker_identity_asset_status(spec.mode),
    }


def _draw_reference_background(draw, *, width: int, height: int, safe_x: int, safe_y: int) -> None:
    draw.rectangle((0, 0, width, height), fill=(36, 39, 44))
    draw.rectangle(
        (safe_x, safe_y, width - safe_x, height - safe_y),
        outline=(93, 108, 125),
        width=2,
    )


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


def _visible_element_authority_ids_for_mode(mode: str) -> list[str]:
    ids = [
        "subtitle_text_block",
        "safe_area_rectangle",
        "measured_text_bbox_readback",
        "sample_mode_label",
        "sample_background",
        "html_sample_image_frame",
    ]
    if mode in {"dialogue_badge_left", "speaker_badge_stack"}:
        ids.extend(["placeholder_speaker_badge", "speaker_accent_color"])
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
    rows = []
    for sample in report["samples"]:
        image_path = Path(sample["output_image_path"])
        rel = image_path.name
        rows.append(
            "<section class=\"sample\">"
            f"<h3>{html.escape(sample['subtitle_mode'])}: {html.escape(sample['text'])}</h3>"
            f"<img src=\"{html.escape(rel)}\" alt=\"{html.escape(sample['subtitle_mode'])} sample\">"
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
        f"<td>{html.escape(str(item['visible_in_default_samples']).lower())}</td>"
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
  <h2>Visible Element Authority</h2>
  <pre>{html.escape(json.dumps(report["visible_element_authority_classes"], ensure_ascii=False, indent=2))}</pre>
  <table>
    <thead>
      <tr><th>element</th><th>class</th><th>visible</th><th>layout authority</th><th>used in calculation</th><th>meaning</th><th>test coverage</th></tr>
    </thead>
    <tbody>{authority_rows}</tbody>
  </table>
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
  <h2>Samples</h2>
  {''.join(rows)}
</body>
</html>
"""
    path.write_text(body, encoding="utf-8")


def _sample_readback_for_html(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "output_image_path": sample["output_image_path"],
        "canvas_size": sample["canvas_size"],
        "subtitle_mode": sample["subtitle_mode"],
        "text": sample["text"],
        "font_family": sample["font_family"],
        "font_fallback_status": sample["font_fallback_status"],
        "requested_font_size": sample["requested_font_size"],
        "measured_bbox": sample["measured_bbox"],
        "safe_area_margin": sample["safe_area_margin"],
        "safe_area_status": sample["safe_area_status"],
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
