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
    assert report["comparison_response_readback"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert report["comparison_response_readback"]["font_family"] == (
        "narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof"
    )
    assert report["comparison_response_readback"]["decoration"] == (
        "narrowed_to_clean_outline_for_next_diagnostic_proof"
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
    assert next_route["selected_candidate_for_next_proof_base"] == (
        "noto_sans_jp_clean_outline"
    )
    assert next_route["recommended_default_candidate_id"] == "noto_sans_jp_clean_outline"
    assert next_route["font_size"]["formula"] == "round(frame_height * 0.115)"
    assert next_route["font_size"]["status"] == (
        "preserve_accepted_diagnostic_representative_direction"
    )
    assert next_route["font_family"] == (
        "narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof"
    )
    assert next_route["decoration"] == (
        "narrowed_to_clean_outline_for_next_diagnostic_proof"
    )
    assert next_route["regenerate_sh08_required"] is False
    assert next_route["episodes_artifact_tracking_allowed"] is False
    assert next_route["production_subtitle_design_acceptance"] is False
    decision_packet = report["small_adjustment_decision_packet"]
    assert decision_packet["decision_state"] == (
        "selected_for_next_diagnostic_overlay_proof_base"
    )
    assert decision_packet["selected_candidate_for_next_proof_base"] == (
        "noto_sans_jp_clean_outline"
    )
    assert decision_packet["recommended_default_candidate_id"] == "noto_sans_jp_clean_outline"
    assert decision_packet["font_size"]["reopen_as_primary_axis"] is False
    assert decision_packet["smallest_next_proof_route"]["default_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert decision_packet["smallest_next_proof_route"]["selected_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert decision_packet["smallest_next_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert decision_packet["smallest_next_proof_route"]["regenerate_sh08_required"] is False
    assert {
        option["candidate_id"] for option in decision_packet["options"]
    } == {
        "current_yu_gothic_heavy_outline",
        "noto_sans_jp_clean_outline",
        "meiryo_bold_soft_shadow",
        "gothic_high_contrast_minimal_badge",
    }
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } == {
        "regenerate_sh08_human_preview_session",
        "claim_production_subtitle_design_acceptance",
        "add_cut_008_dense_stress_proof_now",
        "mutate_source_or_rights_or_publishing_state",
    }
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
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["font_size_policy"]["value"] == 41
    assert persisted["comparison_response_readback"]["selected_response"] == "small_adjustment"
    assert persisted["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert persisted["next_diagnostic_overlay_proof_route"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert persisted["small_adjustment_decision_packet"][
        "recommended_default_candidate_id"
    ] == "noto_sans_jp_clean_outline"
    assert persisted["small_adjustment_decision_packet"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert persisted["outputs"]["html"].endswith(
        "subtitle_typography_decoration_comparison_report.html"
    )
    assert "open_comparison.ps1" in persisted["open_commands"]["open_comparison"]
    html = html_path.read_text(encoding="utf-8")
    assert "Source human readback: adjust_boundary" in html
    assert "ED-10g comparison response: small_adjustment" in html
    assert "Next Diagnostic Overlay Proof Route" in html
    assert "Small Adjustment Decision Packet" in html
    assert "noto_sans_jp_clean_outline" in html
    assert "small_adjustment_diagnostic_overlay_proof" in html
    assert "selected_for_next_diagnostic_overlay_proof_base" in html
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
    assert payload["selected_candidate_for_next_proof_base"] == (
        "noto_sans_jp_clean_outline"
    )
    assert payload["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert payload["next_diagnostic_overlay_proof_route"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert payload["next_diagnostic_overlay_proof_route"]["target_cuts"] == [
        "cut_002",
        "cut_003",
    ]
    assert payload["small_adjustment_decision_packet"][
        "recommended_default_candidate_id"
    ] == "noto_sans_jp_clean_outline"
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_kirinuki_gothic_balance_profile_records_weight_outline_review(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_kirinuki_gothic_balance_comparison"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "なんで来なかったんすか！！",
            "まあ謝るんなら許してあげます",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10i_kirinuki_gothic_balance",
    )

    assert report["report_kind"] == "subtitle_kirinuki_gothic_weight_balance_comparison"
    assert report["artifact_id"] == "clip-ed10i-kirinuki-gothic-balance-001"
    assert report["comparison_profile"] == "ed10i_kirinuki_gothic_balance"
    assert report["human_decision_readback"]["selected_response"] == (
        "not_accepted_as_is"
    )
    assert report["human_decision_readback"]["preferred_direction"] == (
        "kirinuki_youtube_style_gothic"
    )
    assert report["human_decision_readback"]["desired_adjustment"] == (
        "make_glyph_body_thicker_so_outline_does_not_dominate"
    )
    assert report["comparison_response_readback"]["emoji_treatment"] == (
        "neutral_ignore_for_evaluation"
    )
    assert report["comparison_response_readback"]["selected_candidate_for_next_proof_base"] == (
        "pending_ed10i_human_review"
    )
    assert report["candidate_count"] == 4
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10i_reference_noto_clean_outline",
        "ed10i_biz_udgothic_bold_balanced_outline",
        "ed10i_yu_gothic_bold_thin_outline",
        "ed10i_meiryo_bold_fill_outline_balance",
    }
    assert report["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "kirinuki_gothic_weight_balance_diagnostic_proof"
    )
    assert report["next_diagnostic_overlay_proof_route"][
        "recommended_default_candidate_id"
    ] == "ed10i_biz_udgothic_bold_balanced_outline"
    decision_packet = report["kirinuki_gothic_balance_decision_packet"]
    assert decision_packet["decision_state"] == "generated_requires_human_review"
    assert decision_packet["current_reference_not_accepted_as_is"] is True
    assert decision_packet["font_size"]["reopen_as_primary_axis"] is False
    assert decision_packet["emoji_treatment"]["optimize_in_this_slice"] is False
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } >= {
        "broaden_to_all_font_sweep",
        "optimize_emoji_rendering",
        "vendor_third_party_font_binaries",
        "claim_production_subtitle_design_acceptance",
    }
    assert len(report["samples"]) == 8
    for sample in report["samples"]:
        assert sample["sample_variant"] == "kirinuki_gothic_weight_balance_comparison"
        assert sample["style_inputs"]["body_weight_axis"]
        assert sample["style_inputs"]["outline_balance_axis"]
        assert sample["style_inputs"]["emoji_evaluation_scope"] == (
            "emoji_neutral_ignored_for_ed10i"
        )
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_kirinuki_gothic_balance_comparison_report.json"
    html_path = output_dir / "subtitle_kirinuki_gothic_balance_comparison_report.html"
    contact_sheet = output_dir / "subtitle_kirinuki_gothic_balance_contact_sheet.png"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["comparison_profile"] == "ed10i_kirinuki_gothic_balance"
    html = html_path.read_text(encoding="utf-8")
    assert "ED-10i Kirinuki Gothic Weight Balance Comparison" in html
    assert "Kirinuki Gothic Balance Decision Packet" in html
    assert "emoji_neutral_ignored_for_ed10i" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10i_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10i_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10i_kirinuki_gothic_balance",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10i kirinuki gothic balance smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10i-kirinuki-gothic-balance-001"
    assert payload["comparison_profile"] == "ed10i_kirinuki_gothic_balance"
    assert payload["comparison_response"]["selected_response"] == (
        "generate_narrow_kirinuki_gothic_balance_comparison"
    )
    assert payload["selected_candidate_for_next_proof_base"] == (
        "pending_ed10i_human_review"
    )
    assert payload["comparison_decision_packet"]["recommended_default_candidate_id"] == (
        "ed10i_biz_udgothic_bold_balanced_outline"
    )
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_kirinuki_font_audit_profile_consumes_meiryo_freeform_review(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_kirinuki_font_audit"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "団長、ちなみに、他の番長知ってますか？",
            "まあ謝るんなら許してあげます",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10j_kirinuki_font_audit",
    )

    assert report["report_kind"] == "subtitle_kirinuki_font_research_candidate_audit"
    assert report["artifact_id"] == "clip-ed10j-kirinuki-font-audit-001"
    assert report["comparison_profile"] == "ed10j_kirinuki_font_audit"
    assert report["human_decision_readback"]["selected_response"] == (
        "freeform_review_not_accepted_as_normal_baseline"
    )
    assert report["human_decision_readback"][
        "current_meiryo_proof_accepted_as_normal_baseline"
    ] is False
    assert report["human_decision_readback"]["meiryo_role"] == (
        "reviewed_reference_candidate_not_selected_baseline"
    )
    assert report["comparison_response_readback"][
        "selected_candidate_for_next_proof_base"
    ] == "ed10j_biz_udgothic_bold_telop_candidate"
    assert report["comparison_response_readback"]["blue_badge_candidate_id"] == (
        "ed10j_noto_sans_jp_local_telop_candidate"
    )
    assert report["comparison_response_readback"]["blue_badge_is_meiryo_reference"] is False
    assert report["candidate_count"] == 4
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10j_reference_meiryo_reviewed_not_baseline",
        "ed10j_biz_udgothic_bold_telop_candidate",
        "ed10j_yu_gothic_bold_system_candidate",
        "ed10j_noto_sans_jp_local_telop_candidate",
    }
    assert report["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "ed10j_review_consumed_ed10k_biz_overlay_proof"
    )
    assert report["next_diagnostic_overlay_proof_route"][
        "selected_candidate_for_next_proof_base"
    ] == "ed10j_biz_udgothic_bold_telop_candidate"
    assert report["next_diagnostic_overlay_proof_route"][
        "selected_overlay_artifact_id"
    ] == "clip-ed10k-biz-overlay-proof-001"
    assert report["next_diagnostic_overlay_proof_route"][
        "recommended_default_candidate_id"
    ] == "ed10j_biz_udgothic_bold_telop_candidate"
    decision_packet = report["kirinuki_font_audit_decision_packet"]
    assert decision_packet["decision_state"] == "review_consumed_next_overlay_proof_selected"
    assert decision_packet["current_meiryo_proof_accepted_as_normal_baseline"] is False
    assert decision_packet["freeform_review_consumed"][
        "meiryo_removed_from_normal_baseline_candidates"
    ] is True
    assert decision_packet["badge_color_readback"]["blue_badge_candidate_id"] == (
        "ed10j_noto_sans_jp_local_telop_candidate"
    )
    assert decision_packet["badge_color_readback"]["blue_badge_is_meiryo_reference"] is False
    assert decision_packet["font_size"]["reopen_as_primary_axis"] is False
    assert decision_packet["emoji_treatment"]["optimize_in_this_slice"] is False
    assert {
        bucket["bucket"] for bucket in decision_packet["candidate_buckets"]
    } == {
        "system_default_safe",
        "reviewed_reference_only",
        "likely_video_telop_friendly_local",
        "local_only_reproducibility_weak",
        "later_download_license_decision",
    }
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } >= {
        "treat_meiryo_overlay_as_accepted_normal_baseline",
        "minor_meiryo_outline_tweak_only",
        "download_or_vendor_third_party_fonts_now",
        "broaden_to_narration_mincho_or_display_fonts",
        "claim_production_subtitle_design_acceptance",
    }
    assert len(report["samples"]) == 8
    for sample in report["samples"]:
        assert sample["sample_variant"] == "kirinuki_font_research_candidate_audit"
        assert sample["style_inputs"]["emoji_evaluation_scope"] == (
            "emoji_neutral_ignored_for_ed10j"
        )
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_kirinuki_font_audit_report.json"
    html_path = output_dir / "subtitle_kirinuki_font_audit_report.html"
    contact_sheet = output_dir / "subtitle_kirinuki_font_audit_contact_sheet.png"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["comparison_profile"] == "ed10j_kirinuki_font_audit"
    html = html_path.read_text(encoding="utf-8")
    assert "ED-10j Kirinuki Subtitle Font Research" in html
    assert "Kirinuki Font Audit Decision Packet" in html
    assert "reviewed_reference_candidate_not_selected_baseline" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_known_kirinuki_font_pack_profile_consumes_biz_freeform_review(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_known_kirinuki_font_pack_comparison"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "団長、ちなみに、他の番長知ってますか？",
            "まあ謝るんなら許してあげます",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10l_known_kirinuki_font_pack",
    )

    assert report["report_kind"] == "subtitle_known_kirinuki_font_pack_audit"
    assert report["artifact_id"] == "clip-ed10l-known-kirinuki-font-pack-001"
    assert report["comparison_profile"] == "ed10l_known_kirinuki_font_pack"
    assert report["human_decision_readback"]["selected_response"] == (
        "freeform_review_biz_not_accepted_as_normal_baseline"
    )
    assert report["human_decision_readback"][
        "current_biz_proof_accepted_as_normal_baseline"
    ] is False
    assert report["human_decision_readback"]["system_safe_route_role"] == (
        "reference_rejected_for_this_use_case"
    )
    local_readback = report["known_kirinuki_font_pack_decision_packet"][
        "research_readback"
    ]["local_font_readback"]
    all_known_fonts_found = not local_readback["target_candidate_ids_missing"]
    assert report["comparison_response_readback"]["selected_response"] == (
        "per_user_font_readback_valid_route_to_keifont_overlay_proof"
        if all_known_fonts_found
        else "fallback_confirmed_route_to_font_install_readback"
    )
    assert report["comparison_response_readback"][
        "selected_candidate_for_next_proof_base"
    ] == (
        "ed10l_keifont_pop_dialogue_candidate"
        if all_known_fonts_found
        else "pending_real_font_install_readback_after_fallback_confirmation"
    )
    assert report["comparison_response_readback"][
        "candidate_selection_from_current_pngs_allowed"
    ] is all_known_fonts_found
    assert report["comparison_response_readback"][
        "recommended_default_candidate_id"
    ] == "ed10l_keifont_pop_dialogue_candidate"
    assert report["candidate_count"] == 4
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10l_keifont_pop_dialogue_candidate",
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_m_plus_fonts_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    }
    route = report["next_diagnostic_overlay_proof_route"]
    assert route["route_kind"] == (
        "ed10n_keifont_overlay_proof_after_per_user_font_readback"
        if all_known_fonts_found
        else "ed10l_known_font_pack_install_readback_before_visual_proof"
    )
    assert route["current_fallback_contact_sheet_role"] == (
        "real_font_visual_comparison_after_per_user_readback"
        if all_known_fonts_found
        else "readback_only_not_visual_selection"
    )
    assert route["recommended_default_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert route["font_binaries_downloaded"] is False
    decision_packet = report["known_kirinuki_font_pack_decision_packet"]
    if all_known_fonts_found:
        assert decision_packet["decision_state"] == (
            "per_user_font_readback_valid_real_font_evidence"
        )
        assert (
            decision_packet["selected_candidate_for_next_proof_base"]
            == "ed10l_keifont_pop_dialogue_candidate"
        )
        assert decision_packet["candidate_selection_from_current_pngs_allowed"] is True
    else:
        assert decision_packet["decision_state"] == (
            "font_fallback_confirmed_visual_selection_invalid"
        )
        assert (
            decision_packet["candidate_selection_from_current_pngs_allowed"] is False
        )
    assert decision_packet["current_biz_proof_accepted_as_normal_baseline"] is False
    assert decision_packet["self_diagnosis"]["candidate_universe_bias"] == (
        "system_safe_generic_readability"
    )
    assert decision_packet["self_diagnosis"][
        "safe_reproducible_conflated_with_strong_kirinuki_design"
    ] is True
    assert decision_packet["self_diagnosis"][
        "user_known_good_domain_knowledge_not_elevated_early_enough"
    ] is True
    assert {
        slot["slot"] for slot in decision_packet["usage_slots"]
    } == {
        "normal_dialogue_baseline",
        "emphasis_shout_tsukkomi",
        "mood_literary",
    }
    assert {
        bucket["bucket"] for bucket in decision_packet["candidate_buckets"]
    } == {
        "strong_design_candidates",
        "locally_available_now",
        "requires_download_install",
        "requires_explicit_license_handling",
        "reference_rejected_for_normal_baseline",
    }
    assert local_readback["font_readback_sources"] == [
        "HKCU:Software/Microsoft/Windows NT/CurrentVersion/Fonts",
        "HKLM:Software/Microsoft/Windows NT/CurrentVersion/Fonts",
        "%LOCALAPPDATA%/Microsoft/Windows/Fonts",
        "C:/Windows/Fonts",
    ]
    if all_known_fonts_found:
        assert set(local_readback["target_fonts_found"]) == {
            "Keifont",
            "851 Chikara Yowaku",
            "M+ FONTS",
            "Yasashisa Gothic",
        }
        assert local_readback["target_fonts_missing"] == []
        assert local_readback["current_png_valid_visual_evidence"] is True
        assert report["font_visual_comparison_validity"]["status"] == (
            "valid_requested_font_visual_evidence"
        )
        assert report["font_visual_comparison_validity"][
            "all_candidates_valid_real_font"
        ] is True
    else:
        assert local_readback["current_png_valid_visual_evidence"] is False
        assert report["font_visual_comparison_validity"]["status"] == (
            "invalid_fallback_render_not_target_font_visual_evidence"
        )
        assert report["font_visual_comparison_validity"][
            "all_candidates_valid_real_font"
        ] is False
    assert {
        row["current_png_valid_visual_evidence"]
        for row in report["font_visual_comparison_validity"]["candidate_resolution"]
    } == ({True} if all_known_fonts_found else {False})
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } >= {
        "treat_biz_udgothic_overlay_as_accepted_normal_baseline",
        "continue_biz_noto_meiryo_system_safe_tuning_as_main_route",
        "select_candidate_from_current_fallback_contact_sheet",
        "download_or_vendor_font_binaries_now",
        "claim_production_subtitle_design_acceptance",
    }
    assert len(report["samples"]) == 8
    for sample in report["samples"]:
        assert sample["sample_variant"] == (
            "known_kirinuki_font_pack_normal_dialogue_comparison"
        )
        assert sample["style_inputs"]["emoji_evaluation_scope"] == (
            "emoji_neutral_ignored_for_ed10l"
        )
        if all_known_fonts_found:
            assert sample["font_file_status"] == "candidate_primary_font_file_found"
            assert sample["font_fallback_status"] == "requested_candidate_font_file_found"
            assert sample["visual_comparison_validity"] == (
                "valid_requested_font_visual_evidence"
            )
        else:
            assert sample["font_file_status"].startswith(
                "requested_candidate_font_missing_used_"
            )
            assert sample["font_fallback_status"] == (
                "requested_candidate_missing_fallback_font_used"
            )
            assert sample["visual_comparison_validity"] == (
                "invalid_fallback_render_not_target_font_visual_evidence"
            )
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_known_kirinuki_font_pack_report.json"
    html_path = output_dir / "subtitle_known_kirinuki_font_pack_report.html"
    contact_sheet = output_dir / "subtitle_known_kirinuki_font_pack_contact_sheet.png"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["comparison_profile"] == "ed10l_known_kirinuki_font_pack"
    html = html_path.read_text(encoding="utf-8")
    assert "ED-10l Known Kirinuki Font Pack Audit" in html
    assert "Known Kirinuki Font Pack Decision Packet" in html
    assert "system_safe_generic_readability" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10j_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10j_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10j_kirinuki_font_audit",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10j kirinuki font audit smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10j-kirinuki-font-audit-001"
    assert payload["comparison_profile"] == "ed10j_kirinuki_font_audit"
    assert payload["comparison_response"]["selected_response"] == (
        "freeform_review_consumed_move_to_biz_overlay_proof"
    )
    assert payload["selected_candidate_for_next_proof_base"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert payload["comparison_decision_packet"]["recommended_default_candidate_id"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10l_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10l_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10l_known_kirinuki_font_pack",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10l known kirinuki font pack smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10l-known-kirinuki-font-pack-001"
    assert payload["comparison_profile"] == "ed10l_known_kirinuki_font_pack"
    all_known_fonts_found = not payload["comparison_decision_packet"][
        "research_readback"
    ]["local_font_readback"]["target_candidate_ids_missing"]
    assert payload["comparison_response"]["selected_response"] == (
        "per_user_font_readback_valid_route_to_keifont_overlay_proof"
        if all_known_fonts_found
        else "fallback_confirmed_route_to_font_install_readback"
    )
    assert payload["selected_candidate_for_next_proof_base"] == (
        "ed10l_keifont_pop_dialogue_candidate"
        if all_known_fonts_found
        else "pending_real_font_install_readback_after_fallback_confirmation"
    )
    assert payload["comparison_decision_packet"]["recommended_default_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert payload["comparison_decision_packet"]["self_diagnosis"][
        "candidate_universe_bias"
    ] == "system_safe_generic_readability"
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_multifont_focused_review_profile_builds_same_line_matrix(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10o_multifont"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "なんで来なかったんすか！！",
            "まあ謝るんなら許してあげます",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10o_multifont_focused_review",
    )

    assert report["artifact_id"] == "clip-ed10o-multifont-focused-review-001"
    assert report["comparison_profile"] == "ed10o_multifont_focused_review"
    assert report["report_kind"] == "subtitle_multifont_focused_review_surface"
    assert report["candidate_count"] == 3
    assert len(report["samples"]) == 6
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10l_keifont_pop_dialogue_candidate",
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    }
    assert report["focused_review_surface"]["primary_visual"] == (
        "subtitle_area_crop_matrix"
    )
    assert report["focused_review_surface"]["current_lead_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert report["excluded_candidates"] == [
        {
            "candidate_id": "ed10l_m_plus_fonts_dialogue_candidate",
            "reason": "weight_style_unresolved",
            "readback": (
                "registry_display_name=M PLUS 1 Thin; "
                "file=MPLUS1-VariableFont_wght.ttf"
            ),
            "next_action": (
                "pin an exact non-thin M+ weight/style before including it "
                "in baseline comparison"
            ),
        }
    ]
    assert {
        sample["sample_text_index"] for sample in report["samples"]
    } == {1, 2}
    assert {
        sample["sample_variant"] for sample in report["samples"]
    } == {"ed10o_multifont_same_line_subtitle_area_comparison"}
    assert report["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "ed10o_multifont_review_then_bounded_next_proof"
    )
    assert report["production_subtitle_design_acceptance"] is False
    assert report["rights_status"] == "pending"

    html_path = output_dir / "subtitle_multifont_focused_review_report.html"
    matrix_path = output_dir / "subtitle_multifont_focused_review_matrix.png"
    assert html_path.exists()
    assert matrix_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "Review Focus" in html
    assert "Focused Matrix" in html
    assert "Excluded From This One-shot Comparison" in html
    assert "ed10l_m_plus_fonts_dialogue_candidate" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10o_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10o_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10o_multifont_focused_review",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10o one-shot font comparison smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10o-multifont-focused-review-001"
    assert payload["comparison_profile"] == "ed10o_multifont_focused_review"
    assert payload["candidate_count"] == 3
    assert payload["comparison_response"]["selected_response"] == (
        "build_one_shot_multifont_focused_review_surface"
    )
    assert payload["focused_review_surface"]["primary_visual"] == (
        "subtitle_area_crop_matrix"
    )
    assert payload["excluded_candidates"][0]["reason"] == "weight_style_unresolved"
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()
