"""Subtitle renderer typography spike tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.integrations.render import subtitle_style_spike as spike


def test_subtitle_style_spike_records_optional_pillow_boundary():
    assert spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE.startswith("Pillow is an optional")
    assert "review-only PNG measurement artifacts" in spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE
    assert "production renderer dependency" in spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_subtitle_style_spike_writes_png_json_and_html_readback(tmp_path: Path):
    output_dir = tmp_path / "subtitle_style_spike"

    report = spike.build_subtitle_style_spike(output_dir=output_dir, canvas_size=(640, 360))

    assert report["review_only"] is True
    assert report["production_candidate"] is False
    assert report["production_compatible"] is False
    assert report["production_subtitle_design_acceptance"] is False
    assert report["dependency_boundary"] == {
        "pillow": "optional_local_review_tool",
        "declared_project_dependency": False,
        "missing_dependency_behavior": "module import remains available; PNG generation raises explicit RuntimeError",
    }
    assert report["grid_readback"]["grid_model"] == "none"
    assert report["grid_readback"]["grid_visible_in_samples"] is False
    assert report["grid_readback"]["snap_to_grid"] is False
    assert report["grid_readback"]["bbox_grid_coords"] is None
    assert report["grid_readback"]["safe_area_grid_coords"] is None
    assert report["grid_readback"]["wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
    assert set(report["visible_element_authority_classes"]) == {
        "computational_authority",
        "measured_readback",
        "visual_guide_only",
        "placeholder",
        "decorative",
    }
    authority = {
        item["element_id"]: item
        for item in report["visible_element_authority"]
    }
    assert authority["subtitle_text_block"]["authority_class"] == "computational_authority"
    assert authority["subtitle_text_block"]["actual_layout_authority"] is True
    assert authority["safe_area_rectangle"]["authority_class"] == "measured_readback"
    assert authority["safe_area_rectangle"]["visible_in_default_samples"] is True
    assert authority["measured_text_bbox_readback"]["authority_class"] == "measured_readback"
    assert authority["placeholder_speaker_badge"]["authority_class"] == "placeholder"
    assert "not real face icons" in authority["placeholder_speaker_badge"]["meaning_for_reviewer"]
    assert authority["speaker_accent_color"]["authority_class"] == "placeholder"
    assert authority["layout_grid"]["authority_class"] == "visual_guide_only"
    assert authority["layout_grid"]["visible_in_default_samples"] is False
    assert authority["sample_mode_label"]["authority_class"] == "visual_guide_only"
    assert authority["sample_background"]["authority_class"] == "decorative"
    assert authority["html_sample_image_frame"]["authority_class"] == "decorative"
    assert report["mode_decision"]["line"] == "来ねぇ！！"
    assert report["mode_decision"]["not_recommended_default"] == "dialogue_badge_left"
    assert set(report["mode_decision"]["recommended_modes"]) == {
        "reaction_caption",
        "bottom_center_emphasis",
    }
    assert set(report["taxonomy"]) == {
        "dialogue_badge_left",
        "bottom_center_emphasis",
        "reaction_caption",
        "speaker_badge_stack",
    }
    assert {row["candidate"] for row in report["renderer_decision_matrix"]} == {
        "ASS/libass + FFmpeg",
        "HTML/CSS + Playwright screenshot",
        "Pillow / Skia / Pango image drawing",
        "YMM4 .ymmp TextItem direct generation or patch",
        "Premiere MOGRT / Essential Graphics / image overlay",
    }

    samples = report["samples"]
    assert len(samples) == 16
    assert {sample["subtitle_mode"] for sample in samples} == {
        "dialogue_badge_left",
        "bottom_center_emphasis",
        "reaction_caption",
        "speaker_badge_stack",
    }
    for sample in samples:
        image_path = Path(sample["output_image_path"])
        assert image_path.exists()
        assert image_path.suffix == ".png"
        assert sample["canvas_size"] == {"width": 640, "height": 360}
        assert sample["review_only"] is True
        assert sample["production_candidate"] is False
        assert sample["production_compatible"] is False
        assert sample["requested_font_size"] > 0
        assert sample["measured_bbox"]["width"] > 0
        assert sample["measured_bbox"]["height"] > 0
        assert sample["safe_area_margin"]["x"] > 0
        assert sample["grid_model"] == "none"
        assert sample["layout_anchor"]
        assert sample["snap_to_grid"] is False
        assert sample["text_bbox_grid_coords"] is None
        assert sample["badge_bbox_grid_coords"] is None
        assert sample["safe_area_grid_coords"] is None
        assert sample["wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
        assert sample["outline"]["stroke_width"] > 0
        assert sample["shadow"]["offset_px"] > 0
        assert "subtitle_text_block" in sample["visible_element_authority_ids"]
        assert "safe_area_rectangle" in sample["visible_element_authority_ids"]
        assert "measured_text_bbox_readback" in sample["visible_element_authority_ids"]
        assert "sample_mode_label" in sample["visible_element_authority_ids"]
        assert "layout_grid" not in sample["visible_element_authority_ids"]
        assert sample["speaker_identity_asset_status"]["real_face_icons_available"] is False
        assert (
            sample["speaker_identity_asset_status"]["production_speaker_identity_design"]
            is False
        )
        if sample["subtitle_mode"] in {"dialogue_badge_left", "speaker_badge_stack"}:
            assert "placeholder_speaker_badge" in sample["visible_element_authority_ids"]
            assert "speaker_accent_color" in sample["visible_element_authority_ids"]
            assert sample["speaker_identity_asset_status"]["uses_speaker_badge"] is True
            assert sample["speaker_identity_asset_status"]["badge_role"] == "placeholder_speaker_badge"
            assert "placeholder speaker badges only" in sample["speaker_identity_asset_status"]["human_review_note"]
        else:
            assert "placeholder_speaker_badge" not in sample["visible_element_authority_ids"]
            assert sample["speaker_identity_asset_status"]["uses_speaker_badge"] is False

    first_image = spike.Image.open(samples[0]["output_image_path"])
    assert first_image.getpixel((80, 10)) == (36, 39, 44)
    assert first_image.getpixel((35, 32)) == (93, 108, 125)

    json_path = output_dir / "subtitle_style_spike_report.json"
    html_path = output_dir / "subtitle_style_spike_report.html"
    assert json_path.exists()
    assert html_path.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert persisted["review_only"] is True
    assert persisted["production_candidate"] is False
    assert persisted["samples"][0]["measured_bbox"]["width"] > 0
    html = html_path.read_text(encoding="utf-8")
    assert "review_only: true" in html
    assert "production_candidate: false" in html
    assert "grid authority: none" in html
    assert "snap-to-grid" in html
    assert "Visible Element Authority" in html
    assert "placeholder speaker badges" in html
    assert "real face icons are unavailable" in html
    assert "decorative" in html
    assert "reaction_caption" in html
