"""Subtitle renderer typography spike tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.integrations.render import subtitle_style_spike as spike


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_subtitle_style_spike_records_optional_pillow_boundary():
    assert spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE.startswith("Pillow is an optional")
    assert "review-only PNG measurement artifacts" in spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE
    assert "production renderer dependency" in spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_japanese_wrapper_prevents_one_character_orphan_when_measured_alternative_exists():
    image = spike.Image.new("RGB", (420, 180), (0, 0, 0))
    draw = spike.ImageDraw.Draw(image)
    _, font_path, _ = spike._select_font()
    font = spike._load_font(font_path, 42)
    text = "あいうえお"
    spacing = 0
    stroke_width = 0
    max_width = spike._text_size(
        draw=draw,
        text=text[:-1],
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]
    if max_width >= spike._text_size(
        draw=draw,
        text=text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]:
        pytest.skip("selected font does not increase measured width for the orphan fixture")

    result = spike._wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )

    assert result.algorithm_name == "japanese_boundary_font_bbox_pixel_wrap_v1"
    assert result.orphan_prevention_applied is True
    assert result.selected_break_reason == "orphan_prevention_shifted_break"
    assert spike._visible_char_count(result.lines[-1]) > 1
    assert result.lines != ["あいうえ", "お"]
    assert all(width <= max_width for width in result.measured_width_by_line)
    assert any(candidate["would_leave_one_character_orphan"] for candidate in result.candidate_breaks)


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_japanese_wrapper_prevents_suffix_only_tail_when_measured_alternative_exists():
    image = spike.Image.new("RGB", (1920, 1080), (0, 0, 0))
    draw = spike.ImageDraw.Draw(image)
    _, font_path, _ = spike._select_font()
    if font_path is None:
        pytest.skip("Japanese font file is not available for suffix-tail fixture")
    font = spike._load_font(font_path, 124)
    spacing = 19
    stroke_width = 12
    text = "まあ謝るんなら許してあげます"
    max_width = spike._text_size(
        draw=draw,
        text="まあ謝るんなら許してあげ",
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]

    result = spike._wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )

    assert result.suffix_tail_prevention_applied is True
    assert result.selected_break_reason == "suffix_tail_prevention_shifted_break"
    assert result.lines != ["まあ謝るんなら許してあげ", "ます"]
    assert result.lines[-1] in {"あげます", "てあげます", "許してあげます"}
    assert result.suspicious_tail_line_present is False
    assert any(
        candidate["remaining_text"] == "ます"
        and candidate["would_leave_suspicious_tail_line"] is True
        for candidate in result.candidate_breaks
    )


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_japanese_wrapper_marks_question_particle_tail_suspicious():
    image = spike.Image.new("RGB", (1920, 1080), (0, 0, 0))
    draw = spike.ImageDraw.Draw(image)
    _, font_path, _ = spike._select_font()
    if font_path is None:
        pytest.skip("Japanese font file is not available for suffix-tail fixture")
    font = spike._load_font(font_path, 124)
    spacing = 19
    stroke_width = 12
    text = "なんで来なかったんすか！！"
    max_width = spike._text_size(
        draw=draw,
        text="なんで来なかったんす",
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]

    result = spike._wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )

    assert result.suffix_tail_prevention_applied is True
    assert result.lines == ["なんで来なかった", "んすか！！"]
    assert result.suspicious_tail_line_present is False
    assert any(
        candidate["remaining_text"] == "か！！"
        and candidate["would_leave_suspicious_tail_line"] is True
        for candidate in result.candidate_breaks
    )


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
    assert report["measured_bbox_provenance"]["status"] == "systematic_measured_readback"
    assert report["measured_bbox_provenance"]["source_function"] == "draw.multiline_textbbox"
    assert report["measured_bbox_provenance"]["hardcoded_per_sample"] is False
    assert report["measured_bbox_provenance"]["manual_adjustment"] is False
    assert report["measured_bbox_provenance"]["design_target"] is False
    assert report["measured_bbox_provenance"]["report_sections"] == [
        "style_inputs",
        "computed_layout",
        "measured_output",
    ]
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
    assert authority["safe_area_rectangle"]["visible_in_clean_samples"] is False
    assert authority["safe_area_rectangle"]["visible_in_guide_overlay_samples"] is True
    assert authority["measured_text_bbox_readback"]["authority_class"] == "measured_readback"
    assert authority["placeholder_speaker_badge"]["authority_class"] == "placeholder"
    assert "not real face icons" in authority["placeholder_speaker_badge"]["meaning_for_reviewer"]
    assert authority["speaker_accent_color"]["authority_class"] == "placeholder"
    assert authority["layout_grid"]["authority_class"] == "visual_guide_only"
    assert authority["layout_grid"]["visible_in_default_samples"] is False
    assert authority["layout_grid"]["visible_in_guide_overlay_samples"] is False
    assert authority["frame_center_lines"]["authority_class"] == "visual_guide_only"
    assert authority["frame_center_lines"]["visible_in_guide_overlay_samples"] is True
    assert authority["frame_thirds_lines"]["authority_class"] == "visual_guide_only"
    assert authority["lower_subtitle_zone"]["authority_class"] == "visual_guide_only"
    assert authority["subtitle_baseline_guides"]["authority_class"] == "measured_readback"
    assert authority["badge_slot_guide"]["authority_class"] == "placeholder"
    assert authority["badge_center_line"]["authority_class"] == "measured_readback"
    assert authority["text_start_x_line"]["authority_class"] == "measured_readback"
    assert authority["badge_to_text_gap_guide"]["authority_class"] == "measured_readback"
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
        assert sample["sample_variant"] == "clean"
        assert sample["canvas_size"] == {"width": 640, "height": 360}
        assert sample["review_only"] is True
        assert sample["production_candidate"] is False
        assert sample["production_compatible"] is False
        assert sample["requested_font_size"] > 0
        assert sample["style_inputs"]["mode"] == sample["subtitle_mode"]
        assert (
            sample["style_inputs"]["font"]["requested_font_size"]["source"]
            == "formula_from_frame_height_and_mode_constant"
        )
        assert sample["style_inputs"]["font"]["requested_font_size"]["value"] == sample["requested_font_size"]
        assert sample["style_inputs"]["outline"]["stroke_width"]["value"] == sample["outline"]["stroke_width"]
        assert sample["style_inputs"]["safe_area_margin"]["x"]["value"] == sample["safe_area_margin"]["x"]
        assert sample["style_inputs"]["safe_area_margin"]["y"]["value"] == sample["safe_area_margin"]["y"]
        assert sample["style_inputs"]["line_height"]["value"] == sample["line_height"]
        assert sample["computed_layout"]["layout_anchor"] == sample["layout_anchor"]
        assert sample["wrap_algorithm"]["source_function"] == "_wrap_text_to_width"
        assert sample["wrap_algorithm"]["name"] == "japanese_boundary_font_bbox_pixel_wrap_v1"
        assert sample["computed_layout"]["wrap_algorithm"] == sample["wrap_algorithm"]
        assert sample["computed_layout"]["wrap_algorithm"]["not_grid_based"] is True
        assert sample["computed_layout"]["wrapped_text"] == sample["wrapped_text"]
        assert sample["computed_layout"]["wrapped_lines"] == sample["wrapped_lines"]
        assert sample["computed_layout"]["line_count"] == sample["line_count"]
        assert len(sample["measured_width_by_line"]) == sample["line_count"]
        assert sample["computed_layout"]["measured_width_by_line"] == sample["measured_width_by_line"]
        assert sample["computed_layout"]["candidate_breaks"] == sample["candidate_breaks"]
        assert sample["computed_layout"]["selected_break_reason"] == sample["selected_break_reason"]
        assert sample["computed_layout"]["orphan_prevention_applied"] == sample["orphan_prevention_applied"]
        assert (
            sample["computed_layout"]["suffix_tail_prevention_applied"]
            == sample["suffix_tail_prevention_applied"]
        )
        assert (
            sample["computed_layout"]["suspicious_tail_line_present"]
            == sample["suspicious_tail_line_present"]
        )
        assert sample["font_file_status"] == sample["font_fallback_status"]
        assert sample["computed_layout"]["text_start_position"]["x"] >= 0
        assert sample["computed_layout"]["text_start_position"]["y"] >= 0
        assert sample["measured_output"]["source_function"] == "draw.multiline_textbbox"
        assert sample["measured_output"]["manual_override"] is False
        assert sample["measured_output"]["hardcoded_per_sample"] is False
        assert sample["measured_output"]["design_target"] is False
        assert sample["measured_output"]["measured_bbox"] == sample["measured_bbox"]
        assert sample["measured_output"]["safe_area_status"] == sample["safe_area_status"]
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
        assert "safe_area_rectangle" not in sample["visible_element_authority_ids"]
        assert "measured_text_bbox_readback" not in sample["visible_element_authority_ids"]
        assert "frame_center_lines" not in sample["visible_element_authority_ids"]
        assert "sample_mode_label" in sample["visible_element_authority_ids"]
        assert "layout_grid" not in sample["visible_element_authority_ids"]
        assert sample["guide_overlay"]["enabled"] is False
        assert sample["speaker_identity_asset_status"]["real_face_icons_available"] is False
        assert (
            sample["speaker_identity_asset_status"]["production_speaker_identity_design"]
            is False
        )
        if sample["subtitle_mode"] in {"dialogue_badge_left", "speaker_badge_stack"}:
            assert "placeholder_speaker_badge" in sample["visible_element_authority_ids"]
            assert "speaker_accent_color" in sample["visible_element_authority_ids"]
            assert sample["style_inputs"]["badge"]["production_identity_asset"] is False
            assert sample["computed_layout"]["badge_slot"]["authority_class"] == "placeholder"
            assert sample["speaker_identity_asset_status"]["uses_speaker_badge"] is True
            assert sample["speaker_identity_asset_status"]["badge_role"] == "placeholder_speaker_badge"
            assert "placeholder speaker badges only" in sample["speaker_identity_asset_status"]["human_review_note"]
        else:
            assert "placeholder_speaker_badge" not in sample["visible_element_authority_ids"]
            assert sample["style_inputs"]["badge"] is None
            assert sample["speaker_identity_asset_status"]["uses_speaker_badge"] is False

    first_image = spike.Image.open(samples[0]["output_image_path"])
    assert first_image.getpixel((80, 10)) == (36, 39, 44)
    assert first_image.getpixel((35, 32)) == (36, 39, 44)

    guide_overlay = report["guide_overlay"]
    assert guide_overlay["contract_id"] == "subtitle_style_spike_layout_guide_overlay_v0"
    assert guide_overlay["role"] == "review_aid_not_japanese_wrapping_authority"
    assert guide_overlay["clean_samples_distinguishable"] is True
    assert {profile["guide_profile"] for profile in guide_overlay["implemented_profiles"]} == {
        "bottom_center_emphasis_guide_v0",
        "dialogue_badge_left_guide_v0",
    }
    assert {profile["guide_profile"] for profile in guide_overlay["documented_profiles"]} == {
        "speaker_badge_stack_guide_future",
        "status_caption_guide_future",
    }
    guided_samples = guide_overlay["guided_samples"]
    assert len(guided_samples) == 2
    assert {sample["subtitle_mode"] for sample in guided_samples} == {
        "bottom_center_emphasis",
        "dialogue_badge_left",
    }
    for sample in guided_samples:
        image_path = Path(sample["output_image_path"])
        assert image_path.exists()
        assert ".guide" in image_path.name
        assert sample["sample_variant"] == "guide_overlay"
        assert sample["guide_overlay"]["enabled"] is True
        assert sample["guide_overlay"]["snap_to_grid"] is False
        assert sample["guide_overlay"]["japanese_wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
        assert sample["guide_overlay"]["center_lines"]["vertical"]["authority_class"] == "visual_guide_only"
        assert sample["guide_overlay"]["thirds_lines"]["vertical"][0]["authority_class"] == "visual_guide_only"
        assert sample["guide_overlay"]["safe_area"]["authority_class"] == "measured_readback"
        assert sample["guide_overlay"]["text_bbox"]["authority_class"] == "measured_readback"
        assert sample["guide_overlay"]["baseline_lines"]
        assert "safe_area_rectangle" in sample["visible_element_authority_ids"]
        assert "frame_center_lines" in sample["visible_element_authority_ids"]
        assert "frame_thirds_lines" in sample["visible_element_authority_ids"]
        assert "subtitle_baseline_guides" in sample["visible_element_authority_ids"]
        assert "measured_text_bbox_readback" in sample["visible_element_authority_ids"]
        assert "layout_grid" not in sample["visible_element_authority_ids"]
    bottom_guide = next(
        sample for sample in guided_samples if sample["subtitle_mode"] == "bottom_center_emphasis"
    )
    assert bottom_guide["guide_overlay"]["guide_profile"] == "bottom_center_emphasis_guide_v0"
    assert bottom_guide["guide_overlay"]["lower_subtitle_zone"]["authority_class"] == "visual_guide_only"
    assert len(bottom_guide["guide_overlay"]["mode_baseline_targets"]["two_line"]) == 2
    dialogue_guide = next(
        sample for sample in guided_samples if sample["subtitle_mode"] == "dialogue_badge_left"
    )
    assert dialogue_guide["guide_overlay"]["guide_profile"] == "dialogue_badge_left_guide_v0"
    assert dialogue_guide["guide_overlay"]["badge_slot"]["authority_class"] == "placeholder"
    assert dialogue_guide["guide_overlay"]["badge_center_line"]["authority_class"] == "measured_readback"
    assert dialogue_guide["guide_overlay"]["text_start_x"]["authority_class"] == "measured_readback"
    assert dialogue_guide["guide_overlay"]["badge_to_text_gap"]["authority_class"] == "measured_readback"
    assert "badge_slot_guide" in dialogue_guide["visible_element_authority_ids"]
    guided_image = spike.Image.open(dialogue_guide["output_image_path"])
    safe = dialogue_guide["guide_overlay"]["safe_area"]
    assert guided_image.getpixel((safe["left"], safe["top"])) == spike.GUIDE_COLORS["safe_area"]

    json_path = output_dir / "subtitle_style_spike_report.json"
    html_path = output_dir / "subtitle_style_spike_report.html"
    assert json_path.exists()
    assert html_path.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert persisted["review_only"] is True
    assert persisted["production_candidate"] is False
    assert persisted["measured_bbox_provenance"]["status"] == "systematic_measured_readback"
    assert persisted["samples"][0]["measured_bbox"]["width"] > 0
    assert persisted["samples"][0]["measured_output"]["measured_bbox"] == persisted["samples"][0]["measured_bbox"]
    assert persisted["samples"][0]["wrap_algorithm"]["name"] == "japanese_boundary_font_bbox_pixel_wrap_v1"
    assert "candidate_breaks" in persisted["samples"][0]
    assert "measured_width_by_line" in persisted["samples"][0]
    assert len(persisted["guide_overlay"]["guided_samples"]) == 2
    html = html_path.read_text(encoding="utf-8")
    assert "review_only: true" in html
    assert "production_candidate: false" in html
    assert "grid authority: none" in html
    assert "snap-to-grid" in html
    assert "Visible Element Authority" in html
    assert "Measured Bbox Provenance" in html
    assert "style_inputs" in html
    assert "computed_layout" in html
    assert "measured_output" in html
    assert "japanese_boundary_font_bbox_pixel_wrap_v1" in html
    assert "orphan_prevention_applied" in html
    assert "suffix_tail_prevention_applied" in html
    assert "candidate_breaks" in html
    assert "placeholder speaker badges" in html
    assert "real face icons are unavailable" in html
    assert "comparison-only" in html
    assert "Repeated text" in html
    assert "intentional comparison" in html
    assert "clean sample" in html
    assert "guide overlay sample" in html
    assert "Guide Overlay Contract" in html
    assert "bottom_center_emphasis_guide_v0" in html
    assert "dialogue_badge_left_guide_v0" in html
    assert "decorative" in html
    assert "reaction_caption" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_preserves_accepted_font_size_boundary(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_typography_decoration_comparison"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "なんで来なかったんすか！！",
            "まあ謝るんなら許してあげます",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
    )

    assert report["report_kind"] == "subtitle_typography_decoration_comparison"
    assert report["artifact_id"] == "clip-typography-decoration-comparison-001"
    assert report["human_decision_readback"]["selected_response"] == "adjust_boundary"
    assert report["human_decision_readback"]["font_size"] == (
        "accepted_for_diagnostic_representative_review"
    )
    assert report["human_decision_readback"]["font_family"] == (
        "unresolved_needs_comparison"
    )
    assert report["human_decision_readback"]["decoration"] == (
        "unresolved_needs_comparison"
    )
    assert report["comparison_response_readback"]["selected_response"] == "small_adjustment"
    assert report["comparison_response_readback"]["font_size"] == (
        "accepted_for_diagnostic_representative_review"
    )
    assert report["comparison_response_readback"]["font_family"] == (
        "unresolved_requires_comparison_or_selection"
    )
    assert report["comparison_response_readback"]["decoration"] == (
        "unresolved_requires_comparison_or_selection"
    )
    assert report["comparison_response_readback"]["production_subtitle_design_acceptance"] is False
    assert report["production_candidate"] is False
    assert report["production_subtitle_design_acceptance"] is False
    assert report["production_render_acceptance"] is False
    assert report["creative_acceptance"] is False
    assert report["rights_status"] == "pending"
    assert report["publishing_acceptance"] is False
    assert report["public_use_permission"] is False
    assert report["font_size_policy"]["status"] == "preserved_from_human_review"
    assert report["font_size_policy"]["value"] == 41
    next_route = report["next_diagnostic_overlay_proof_route"]
    assert next_route["route_kind"] == "small_adjustment_diagnostic_overlay_proof"
    assert next_route["target_cuts"] == ["cut_002", "cut_003"]
    assert next_route["font_size"]["formula"] == "round(frame_height * 0.115)"
    assert next_route["font_size"]["status"] == (
        "preserve_accepted_diagnostic_representative_direction"
    )
    assert next_route["font_family"] == (
        "unresolved_until_concrete_adjusted_candidate_selected"
    )
    assert next_route["decoration"] == (
        "unresolved_until_outline_shadow_badge_accent_selected"
    )
    assert next_route["regenerate_sh08_required"] is False
    assert next_route["episodes_artifact_tracking_allowed"] is False
    assert next_route["production_subtitle_design_acceptance"] is False
    assert report["candidate_count"] == 4
    assert len(report["samples"]) == 8
    assert {sample["candidate_id"] for sample in report["samples"]} == {
        "current_yu_gothic_heavy_outline",
        "noto_sans_jp_clean_outline",
        "meiryo_bold_soft_shadow",
        "gothic_high_contrast_minimal_badge",
    }
    for sample in report["samples"]:
        assert Path(sample["output_image_path"]).exists()
        assert sample["sample_variant"] == "font_family_decoration_comparison"
        assert sample["subtitle_mode"] == "badge_left_dialogue"
        assert sample["font_size_status"] == "accepted_for_diagnostic_representative_review"
        assert sample["requested_font_size"] == 41
        assert sample["style_inputs"]["font_size_axis"] == "fixed_from_human_review"
        assert sample["style_inputs"]["font_family_axis"] == "comparison_candidate"
        assert sample["style_inputs"]["decoration_axis"] == "comparison_candidate"
        assert sample["wrap_algorithm"]["name"] == "japanese_boundary_font_bbox_pixel_wrap_v1"
        assert sample["wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
        assert sample["production_subtitle_design_acceptance"] is False
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_typography_decoration_comparison_report.json"
    html_path = output_dir / "subtitle_typography_decoration_comparison_report.html"
    contact_sheet = output_dir / "subtitle_typography_decoration_contact_sheet.png"
    open_helper = output_dir / "open_comparison.ps1"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    assert open_helper.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert persisted["font_size_policy"]["value"] == 41
    assert persisted["comparison_response_readback"]["selected_response"] == "small_adjustment"
    assert persisted["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert persisted["outputs"]["html"].endswith(
        "subtitle_typography_decoration_comparison_report.html"
    )
    assert "open_comparison.ps1" in persisted["open_commands"]["open_comparison"]
    html = html_path.read_text(encoding="utf-8")
    assert "Source human readback: adjust_boundary" in html
    assert "ED-10g comparison response: small_adjustment" in html
    assert "Next Diagnostic Overlay Proof Route" in html
    assert "small_adjustment_diagnostic_overlay_proof" in html
    assert "font family and decoration remain unresolved" in html
    assert "production_subtitle_design_acceptance=false" in html
    assert "Current Yu Gothic heavy outline" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_small_adjustment_route(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_typography_decoration_comparison_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10g small adjustment smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-typography-decoration-comparison-001"
    assert payload["comparison_response"]["selected_response"] == "small_adjustment"
    assert payload["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert payload["next_diagnostic_overlay_proof_route"]["target_cuts"] == [
        "cut_002",
        "cut_003",
    ]
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()
