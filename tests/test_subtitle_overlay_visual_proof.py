"""Subtitle-overlay visual proof tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.operator_proxy_decision_handoff import build_operator_proxy_decision_handoff
from src.integrations.render import subtitle_overlay_visual_proof as overlay_proof
from src.integrations.render import subtitle_style_spike as spike
from src.integrations.render.subtitle_overlay_visual_proof import (
    SubtitleOverlayVisualProofError,
    _presentation_items,
    _subtitle_layout_contract,
    _write_ass,
    build_subtitle_overlay_visual_proof,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_subtitle_overlay_visual_proof_targets_explicit_cuts_and_updates_ed10d(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    before = build_operator_proxy_decision_handoff(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )
    assert before["handoff"]["visual_proof_status"] == "blocked_no_cut_002_cut_003_overlay_proof"
    legacy_cut3_srt = review_dir / "subtitle_overlay_visual_proof_cut_003.srt"
    legacy_cut3_srt.write_text("legacy autoload subtitle", encoding="utf-8")
    legacy_cut3_video = review_dir / "subtitle_overlay_visual_proof_cut_003.mp4"
    legacy_cut3_frame = review_dir / "subtitle_overlay_visual_proof_cut_003.png"
    legacy_cut3_video.write_bytes(b"previous video")
    legacy_cut3_frame.write_bytes(b"previous frame")

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_002", "cut_003"],
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    assert report["target_cuts"] == ["cut_002", "cut_003"]
    assert report["production_candidate"] is False
    assert report["rights_status"] == "pending"
    assert report["production_usage_allowed"] is False
    assert report["creative_acceptance"] is False
    assert report["publish_acceptance"] is False
    assert report["style_direction"]["preset_name"] == "jp_clip_readable_v1"
    assert report["style_direction"]["target_viewing_context"] == (
        "smartphone_readable_japanese_clip_subtitle"
    )
    assert report["style_parameters"]["renderer"] == "ffmpeg_subtitles_filter_ass"
    assert report["style_parameters"]["explicit_ass_style_file"] is True
    assert report["style_parameters"]["font_size"]["source"] == (
        "formula_from_frame_height"
    )
    assert report["style_parameters"]["font_size"]["value"] == 21
    assert report["style_parameters"]["outline"]["value"] == 2
    assert report["style_parameters"]["margin_v"]["value"] == 16
    assert report["style_parameters"]["presentation_mode"] == "badge_left_dialogue"
    assert report["style_parameters"]["supported_presentation_modes"] == [
        "badge_left_dialogue",
        "bottom_center_emphasis",
    ]
    assert report["style_parameters"]["left_alignment_scope"].startswith("conditional")
    assert report["style_parameters"]["layout_formulas"]["font_size"] == (
        "round(frame_height * 0.115)"
    )
    assert report["style_parameters"]["layout_values"]["badge_width"] == 21
    assert report["style_parameters"]["layout_values"]["badge_height"] == 15
    assert report["style_parameters"]["layout_values"]["badge_font_size"] == 9
    assert report["style_parameters"]["layout_values"]["badge_text_gap"] == 6
    assert report["style_parameters"]["layout_values"]["line_height"] == 24
    assert report["style_parameters"]["wrapping"]["automatic_wrap_applied_by_overlay_generator"] is True
    assert report["style_parameters"]["wrapping"]["wrap_algorithm"]["name"] == (
        "japanese_boundary_font_bbox_pixel_wrap_v1"
    )
    assert report["style_parameters"]["wrapping"]["wrapping_authority"] == (
        "font_bbox_pixel_measurement_not_grid_cell_count"
    )
    assert report["style_parameters"]["font_bbox_wrap_readback"]["renderer_gap"]["exists"] is True
    assert (
        report["style_parameters"]["font_bbox_wrap_readback"][
            "suffix_tail_prevention_applied_count"
        ]
        == 0
    )
    assert (
        report["style_parameters"]["font_bbox_wrap_readback"][
            "suspicious_tail_line_present"
        ]
        is False
    )
    assert report["font_bbox_wrap_readback"]["wrap_algorithm"]["name"] == (
        "japanese_boundary_font_bbox_pixel_wrap_v1"
    )
    assert report["subtitle_presentation_contract"]["contract_id"] == (
        "jp_clip_dialogue_reference_v0"
    )
    assert report["subtitle_presentation_contract"]["selected_presentation_mode"] == (
        "badge_left_dialogue"
    )
    assert report["subtitle_presentation_contract"]["supported_presentation_modes"] == [
        "badge_left_dialogue",
        "bottom_center_emphasis",
    ]
    assert report["subtitle_presentation_contract"]["left_alignment_is_universal"] is False
    assert report["subtitle_presentation_contract"]["layout_values"]["font_size"] == 21
    assert report["speaker_identity_presentation"]["fallback_used"] is True
    assert report["speaker_identity_presentation"]["fallback_kind"] == (
        "speaker_badge_placeholder"
    )
    assert report["speaker_identity_presentation"]["fallback_badge_size"] == {
        "width": 21,
        "height": 15,
        "font_size": 9,
        "formula": "badge_width=round(font_size*1.0), badge_height=round(font_size*0.7), badge_font_size=round(font_size*0.44)",
    }
    assert report["replacement_behavior"]["mode"] == "replace_on_next_subtitle_start"
    assert report["renderer_path_audit"]["old_candidate_insufficiency"][
        "insufficient_style_difference"
    ] is True
    assert report["sample_frame_selection"]["required_roles"] == [
        "early",
        "middle",
        "response_referral",
        "final",
    ]
    assert report["burned_in_subtitle_style"]["style_candidate_id"] == (
        "jp_clip_dialogue_badge_left_v0"
    )
    assert report["burned_in_subtitle_style"]["production_subtitle_design_acceptance"] is False
    assert report["sidecar_srt_reference"]["role"] == (
        "reference_text_only_not_burned_in_subtitle_rendering"
    )
    assert report["review_warning"]["vlc_sidecar_srt_auto_display"] == "can_confuse_review"
    assert report["aggregate_summary"]["subtitle_overlay_available_count"] == 2
    assert {item["cut_id"] for item in report["cut_results"]} == {"cut_002", "cut_003"}

    for item in report["cut_results"]:
        assert item["subtitle_overlay_present"] is True
        assert item["visual_proof_status"] == "available_diagnostic_subtitle_overlay"
        assert item["style_direction"]["preset_name"] == "jp_clip_readable_v1"
        assert item["style_parameters"]["alignment"]["value"] == (
            "speaker_badge_left_aligned_dialogue"
        )
        assert item["style_parameters"]["font_size"]["value"] == 21
        assert item["style_parameters"]["font_size"]["source"] == "formula_from_frame_height"
        assert item["style_parameters"]["layout_values"]["line_height"] == 24
        assert item["burned_in_subtitle_style"]["font_size"] == 21
        assert item["burned_in_subtitle_style"]["outline"] == 2
        assert item["burned_in_subtitle_style"]["badge_size"]["width"] == 21
        assert item["burned_in_subtitle_style"]["line_height"] == 24
        assert item["burned_in_subtitle_style"]["left_alignment_scope"].startswith("conditional")
        assert item["subtitle_presentation_contract"]["contract_id"] == (
            "jp_clip_dialogue_reference_v0"
        )
        assert item["subtitle_presentation_contract"]["left_alignment_is_universal"] is False
        assert item["speaker_identity_presentation"]["pattern_status"] == (
            "approximated_with_fallback_speaker_badge_no_face_icon_assets"
        )
        assert item["speaker_identity_presentation"]["badge_vertical_alignment_rule"].startswith(
            "Align badge center"
        )
        assert item["replacement_behavior"]["mode"] == "replace_on_next_subtitle_start"
        assert item["sample_frame_selection"]["roles"] == [
            "early",
            "middle",
            "response_referral",
            "final",
        ]
        assert len(item["generated_artifacts"]["sample_frames"]) == 4
        for sample in item["generated_artifacts"]["sample_frames"]:
            assert sample["subtitle_bearing_expected"] is True
            assert sample["path"].endswith(f"sample_{sample['role']}.png")
            assert (tmp_path / sample["path"]).is_relative_to(review_dir)
        assert item["sidecar_srt_reference"]["role"] == (
            "reference_text_only_not_burned_in_subtitle_rendering"
        )
        assert item["generated_artifacts"]["burned_in_subtitle_file"].endswith(".burned_in.ass")
        assert item["generated_artifacts"]["sidecar_srt_reference"].endswith(".reference.srt")
        assert "subtitle_overlay_reference" in item["generated_artifacts"]["sidecar_srt_reference"]
        assert item["artifact_exists"]["burned_in_subtitle_file"] is True
        assert item["artifact_exists"]["sidecar_srt_reference"] is True
        assert ".burned_in.ass" in item["attempts"][0]["summary"]
        assert ".reference.srt" not in item["attempts"][0]["summary"]
        assert item["line_width_readback"]["measurement_kind"] == "east_asian_width_proxy"
        assert item["font_bbox_wrap_readback"]["wrap_algorithm"]["name"] == (
            "japanese_boundary_font_bbox_pixel_wrap_v1"
        )
        assert item["font_bbox_wrap_readback"]["renderer_gap"]["exists"] is True
        assert item["font_bbox_wrap_readback"]["proof_renderer"] == "ffmpeg_subtitles_filter_ass"
        assert item["font_bbox_wrap_readback"]["measurement_renderer"] == (
            "Pillow ImageDraw.multiline_textbbox"
        )
        assert (tmp_path / item["generated_artifacts"]["video"]).is_relative_to(review_dir)
        assert (tmp_path / item["generated_artifacts"]["frame"]).is_relative_to(review_dir)
        assert item["generated_artifacts"]["video"].endswith(f"{item['cut_id']}.mp4")
        assert item["generated_artifacts"]["frame"].endswith(f"{item['cut_id']}.png")

    assert not (review_dir / "subtitle_overlay_visual_proof_cut_001.mp4").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_002.mp4").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_002.png").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_002.burned_in.ass").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_002.reference.srt").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_002.sample_early.png").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_003.mp4").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_003.png").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.sample_response_referral.png").exists()
    assert not legacy_cut3_srt.exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.legacy_autoload.srt").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.previous_style.mp4").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.previous_style.png").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.previous_autoload.srt").exists()

    overlay_html = (review_dir / "subtitle_overlay_visual_proof_report.html").read_text(encoding="utf-8")
    assert "jp_clip_readable_v1" in overlay_html
    assert "jp_clip_dialogue_reference_v0" in overlay_html
    assert "speaker_badge_placeholder_plus_left_aligned_subtitle" in overlay_html
    assert "bottom_center_emphasis" in overlay_html
    assert "conditional" in overlay_html
    assert "font_size" in overlay_html
    assert "round(frame_height * 0.115)" in overlay_html
    assert "badge alignment rule" in overlay_html
    assert "japanese_boundary_font_bbox_pixel_wrap_v1" in overlay_html
    assert "font bbox carry-over" in overlay_html
    assert "suffix_tail_prevention_count" in overlay_html
    assert "wrap_items" in overlay_html
    assert "SPK/A/B are temporary speaker badge placeholders" in overlay_html
    assert "Repeated text across modes is intentional comparison" in overlay_html
    assert "measurement/proof renderer gap" in overlay_html
    assert "Burned-in vs Sidecar SRT" in overlay_html
    assert "subtitle-bearing samples" in overlay_html
    assert "previous proof for comparison" in overlay_html
    assert "subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_003.sample_response_referral.png" in overlay_html
    assert "subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_003.previous_style.png" in overlay_html
    assert "subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_003.reference.srt" in overlay_html
    assert 'src="subtitle_overlay_visual_proof_cut_002.png"' in overlay_html
    assert 'src="subtitle_overlay_visual_proof_cut_003.mp4"' in overlay_html
    assert 'src="visual_proof_contact_sheet.png"' in overlay_html
    cut3_ass = (
        review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.burned_in.ass"
    ).read_text(encoding="utf-8")
    assert "Style: ClipPipeDialogueLeft" in cut3_ass
    assert "Style: ClipPipeSpeakerBadge" in cut3_ass
    assert "\\pos(45,140)" in cut3_ass
    assert "\\pos(28,152)" in cut3_ass

    representative = json.loads(
        (review_dir / "representative_visual_proof_report.json").read_text(encoding="utf-8")
    )
    assert representative["diagnostic_style_direction"]["preset_name"] == "jp_clip_readable_v1"
    assert representative["subtitle_presentation_contract"]["contract_id"] == (
        "jp_clip_dialogue_reference_v0"
    )
    assert representative["burned_in_subtitle_style"]["style_candidate_id"] == (
        "jp_clip_dialogue_badge_left_v0"
    )
    assert representative["sidecar_srt_reference"]["role"] == (
        "reference_text_only_not_burned_in_subtitle_rendering"
    )
    assessments = {item["cut_id"]: item for item in representative["per_cut_visual_assessment"]}
    assert assessments["cut_001"]["visual_proof_status"] == "available_diagnostic_render_frame"
    assert assessments["cut_002"]["visual_proof_status"] == "available_diagnostic_subtitle_overlay"
    assert assessments["cut_002"]["style_parameters"]["font_size"]["source"] == (
        "formula_from_frame_height"
    )
    assert assessments["cut_002"]["style_parameters"]["font_size"]["value"] == 21
    assert assessments["cut_002"]["subtitle_presentation_contract"][
        "left_alignment_is_universal"
    ] is False
    assert assessments["cut_002"]["subtitle_presentation_contract"]["contract_id"] == (
        "jp_clip_dialogue_reference_v0"
    )
    assert assessments["cut_002"]["sidecar_srt_reference"]["autoload_prevention"]
    assert assessments["cut_002"]["previous_visual_proof_status"] == (
        "available_source_frame_only_no_subtitle_overlay"
    )
    assert assessments["cut_003"]["visual_proof_status"] == "available_diagnostic_subtitle_overlay"
    assert assessments["cut_003"]["sample_frame_selection"][
        "includes_response_referral_block"
    ] is True

    representative_html = (review_dir / "representative_visual_proof_report.html").read_text(encoding="utf-8")
    assert "jp_clip_readable_v1" in representative_html
    assert "jp_clip_dialogue_reference_v0" in representative_html
    assert 'src="subtitle_overlay_visual_proof_cut_002.png"' in representative_html

    after = build_operator_proxy_decision_handoff(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )
    handoff = after["handoff"]
    assert handoff["visual_proof_status"] == "available_requires_human_review"
    assert handoff["boundary_flags"]["production_candidate"] is False
    assert handoff["boundary_flags"]["rights_status"] == "pending"
    cut_002, cut_003 = handoff["cuts"]
    assert cut_002["visual_proof"]["style_direction"]["preset_name"] == "jp_clip_readable_v1"
    assert cut_002["visual_proof"]["style_parameters"]["style_slot"] == "subtitle.default"
    assert cut_002["visual_proof"]["style_parameters"]["font_size"]["value"] == 21
    assert cut_002["operator_input_fields"]["proxy_decision"] == "undecided"
    assert cut_002["operator_input_fields"]["editorial_intent"] == ""
    assert cut_003["context_status"] == "needs_review"
    assert cut_003["retained_context_risk"] is True
    assert cut_003["operator_input_fields"]["context_risk_handling"] == "undecided"


def test_subtitle_overlay_visual_proof_applies_ed10g_typography_candidate(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_002", "cut_003"],
        typography_decoration_candidate_id="noto_sans_jp_clean_outline",
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    assert report["target_cuts"] == ["cut_002", "cut_003"]
    assert report["style_direction"]["ed10g_small_adjustment_selected"] is True
    assert report["style_direction"]["typography_decoration_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert report["style_parameters"]["typography_decoration_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert report["style_parameters"]["style_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert report["style_parameters"]["font_size"]["readback"] == (
        "round(frame_height * 0.115)"
    )
    assert report["style_parameters"]["font_size"]["value"] == 21
    assert report["style_parameters"]["outline"]["readback"] == (
        "max(2, round(font_size * 0.086))"
    )
    assert report["burned_in_subtitle_style"]["typography_decoration_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert report["burned_in_subtitle_style"]["font_family_route"]["requested"] == (
        "Noto Sans JP"
    )
    assert report["production_candidate"] is False
    assert report["rights_status"] == "pending"
    assert report["production_usage_allowed"] is False

    for item in report["cut_results"]:
        assert item["style_parameters"]["typography_decoration_candidate_id"] == (
            "noto_sans_jp_clean_outline"
        )
        assert item["burned_in_subtitle_style"]["style_candidate_id"] == (
            "noto_sans_jp_clean_outline"
        )
        assert item["font_bbox_wrap_readback"]["typography_decoration_candidate_id"] == (
            "noto_sans_jp_clean_outline"
        )

    ass = (
        review_dir
        / "subtitle_overlay_reference"
        / "subtitle_overlay_visual_proof_cut_002.burned_in.ass"
    ).read_text(encoding="utf-8")
    assert "Style: ClipPipeDialogueLeft," in ass
    assert "&H00E68B22" in ass


def test_subtitle_overlay_visual_proof_applies_selected_ed10i_meiryo_candidate(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_002", "cut_003"],
        typography_decoration_candidate_id="ed10i_meiryo_bold_fill_outline_balance",
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    assert report["target_cuts"] == ["cut_002", "cut_003"]
    assert report["style_direction"]["ed10i_kirinuki_gothic_balance_candidate"] is True
    assert report["style_direction"]["ed10g_small_adjustment_selected"] is False
    assert report["style_direction"]["typography_decoration_candidate_id"] == (
        "ed10i_meiryo_bold_fill_outline_balance"
    )
    assert report["style_direction"]["decoration_route"]["body_weight_note"] == (
        "bold body with warm fill; tests the most balanced fill/outline read"
    )
    assert report["style_direction"]["decoration_route"]["outline_balance_role"] == (
        "balanced_fill_outline_variant"
    )
    assert report["style_parameters"]["style_candidate_id"] == (
        "ed10i_meiryo_bold_fill_outline_balance"
    )
    assert report["style_parameters"]["typography_decoration_candidate"][
        "requested_font_family"
    ] == "Meiryo"
    assert report["style_parameters"]["typography_decoration_candidate"][
        "emoji_evaluation_scope"
    ] == "emoji_neutral_ignored_for_ed10i"
    assert report["burned_in_subtitle_style"][
        "ed10i_kirinuki_gothic_balance_candidate"
    ] is True
    assert report["production_candidate"] is False
    assert report["rights_status"] == "pending"
    assert report["production_usage_allowed"] is False

    for item in report["cut_results"]:
        assert item["style_parameters"]["typography_decoration_candidate_id"] == (
            "ed10i_meiryo_bold_fill_outline_balance"
        )
        assert item["style_parameters"][
            "ed10i_kirinuki_gothic_balance_candidate"
        ] is True
        assert item["burned_in_subtitle_style"]["decoration_route"][
            "outline_balance_role"
        ] == "balanced_fill_outline_variant"
        assert item["subtitle_overlay_present"] is True


def test_subtitle_overlay_visual_proof_applies_selected_ed10j_biz_candidate(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_002", "cut_003"],
        typography_decoration_candidate_id="ed10j_biz_udgothic_bold_telop_candidate",
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    assert report["target_cuts"] == ["cut_002", "cut_003"]
    assert report["style_direction"]["ed10j_kirinuki_font_audit_candidate"] is True
    assert report["style_direction"]["ed10i_kirinuki_gothic_balance_candidate"] is False
    assert report["style_direction"]["typography_decoration_candidate_id"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert report["style_direction"]["decoration_route"]["outline_balance_role"] == (
        "body_first_telop_candidate"
    )
    assert report["style_parameters"]["style_candidate_id"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert report["style_parameters"]["ed10j_kirinuki_font_audit_candidate"] is True
    assert report["style_parameters"]["typography_decoration_candidate"][
        "requested_font_family"
    ] == "BIZ UDGothic"
    assert report["style_parameters"]["typography_decoration_candidate"][
        "emoji_evaluation_scope"
    ] == "emoji_neutral_ignored_for_ed10j"
    assert report["burned_in_subtitle_style"][
        "ed10j_kirinuki_font_audit_candidate"
    ] is True
    assert report["production_candidate"] is False
    assert report["rights_status"] == "pending"
    assert report["production_usage_allowed"] is False

    for item in report["cut_results"]:
        assert item["style_parameters"]["typography_decoration_candidate_id"] == (
            "ed10j_biz_udgothic_bold_telop_candidate"
        )
        assert item["style_parameters"]["ed10j_kirinuki_font_audit_candidate"] is True
        assert item["burned_in_subtitle_style"]["decoration_route"][
            "outline_balance_role"
        ] == "body_first_telop_candidate"
        assert item["subtitle_overlay_present"] is True


def test_subtitle_overlay_visual_proof_ed10p_keifont_profile(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_002", "cut_003"],
        typography_decoration_candidate_id="ed10l_keifont_pop_dialogue_candidate",
        proof_profile="ed10p_keifont_lead_representative_proof",
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    representative = result["representative_visual_proof_report"]
    assert report["artifact_id"] == "clip-ed10p-keifont-lead-representative-proof-001"
    assert report["proof_profile"] == "ed10p_keifont_lead_representative_proof"
    assert report["source_review_artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert report["source_proof_artifact_id"] == (
        "clip-ed10n-keifont-overlay-proof-001"
    )
    assert report["style_parameters"]["typography_decoration_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert report["focused_proof_review"]["status"] == (
        "representative_keifont_lead_proof_ready"
    )
    assert report["focused_proof_review"]["input_mode"] == "freeform"
    assert report["focused_proof_review"]["current_lead_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert report["outputs"]["focused_review_html"].endswith(
        "current_proof_focused_review.html"
    )
    assert report["review_surface_direction"]["status"] == (
        "accepted_as_review_direction_not_production_acceptance"
    )
    assert report["candidate_state"]["alternates_preserved"] == [
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    ]
    assert report["review_debt"][0]["debt_id"] == "cut_008_dense_stress_proof"
    assert report["production_candidate"] is False
    assert report["rights_status"] == "pending"
    assert representative["active_overlay_artifact_id"] == (
        "clip-ed10p-keifont-lead-representative-proof-001"
    )
    assert representative["focused_proof_review"]["source_review_artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert representative["review_debt"][0]["status"] == "deferred_not_blocking_ed10p"

    report_html = (review_dir / "subtitle_overlay_visual_proof_report.html").read_text(
        encoding="utf-8"
    )
    focused_html = (review_dir / "current_proof_focused_review.html").read_text(
        encoding="utf-8"
    )
    representative_html = (
        review_dir / "representative_visual_proof_report.html"
    ).read_text(encoding="utf-8")
    assert result["focused_review_html_path"] == (
        review_dir / "current_proof_focused_review.html"
    )
    assert "Review Focus: Current Proof" in focused_html
    assert "Subtitle-Area Evidence" in focused_html
    assert "Detailed Reports" in focused_html
    assert focused_html.index("Review Focus") < focused_html.index(
        "Subtitle-Area Evidence"
    )
    assert focused_html.index("Subtitle-Area Evidence") < focused_html.index(
        "Detailed Reports"
    )
    assert "subtitle_overlay_visual_proof_cut_002.png" in focused_html
    assert "subtitle_overlay_visual_proof_cut_003.png" in focused_html
    assert (
        'href="subtitle_multifont_focused_review/subtitle_multifont_focused_review_report.html"'
        in focused_html
    )
    assert "cut_008_dense_stress_proof" in focused_html
    assert "<tr><th>cut</th><th>status</th><th>visual</th>" not in focused_html
    assert "Review Focus" in report_html
    assert "Target Lines" in report_html
    assert "clip-ed10o-multifont-focused-review-001" in report_html
    assert "cut_008_dense_stress_proof" in report_html
    assert "Review Focus" in representative_html


def test_subtitle_overlay_visual_proof_ed10p_profile_requires_keifont(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    with pytest.raises(SubtitleOverlayVisualProofError, match="requires"):
        build_subtitle_overlay_visual_proof(
            episode_dir=episode_dir,
            review_dir=review_dir,
            target_cut_ids=["cut_002", "cut_003"],
            typography_decoration_candidate_id="ed10j_biz_udgothic_bold_telop_candidate",
            proof_profile="ed10p_keifont_lead_representative_proof",
            ffmpeg_path="fake-ffmpeg",
            ffprobe_path="fake-ffprobe",
            base_dir=tmp_path,
            runner=_fake_runner,
        )


def test_subtitle_overlay_visual_proof_ed10r_keifont_dense_stress_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    monkeypatch.setattr(
        overlay_proof,
        "_resolve_candidate_font",
        lambda candidate: (
            "Keifont",
            "C:/Users/PLANNER007/AppData/Local/Microsoft/Windows/Fonts/keifont.ttf",
            "candidate_primary_font_file_found",
        ),
    )

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_008"],
        typography_decoration_candidate_id="ed10l_keifont_pop_dialogue_candidate",
        proof_profile="ed10r_keifont_dense_stress_proof",
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    representative = result["representative_visual_proof_report"]
    assert report["artifact_id"] == "clip-ed10r-keifont-dense-stress-proof-001"
    assert report["proof_profile"] == "ed10r_keifont_dense_stress_proof"
    assert report["target_cuts"] == ["cut_008"]
    assert report["source_review_artifact_id"] == (
        "clip-ed10p-keifont-lead-representative-proof-001"
    )
    assert report["source_comparison_artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert report["focused_proof_review"]["status"] == (
        "dense_stress_keifont_proof_ready"
    )
    assert report["focused_proof_review"]["input_mode"] == (
        "dense_stress_diagnostic_review"
    )
    assert report["candidate_state"][
        "keifont_is_diagnostic_representative_normal_dialogue_provisional_baseline"
    ] is True
    assert report["candidate_state"]["keifont_general_acceptance_reopened"] is False
    assert report["review_debt"][0]["status"] == "current_target"
    assert report["production_candidate"] is False
    assert report["production_usage_allowed"] is False
    assert report["creative_acceptance"] is False
    assert report["rights_status"] == "pending"
    assert report["publish_acceptance"] is False
    assert report["aggregate_summary"]["subtitle_overlay_available_count"] == 1
    assert report["font_visual_evidence"]["status"] == (
        "valid_requested_keifont_visual_evidence"
    )
    assert report["review_memory"]["current_blocker"] == "none_for_font_evidence"
    assert report["review_memory"]["font_evidence_gate"] == (
        "valid_requested_keifont_visual_evidence"
    )
    assert report["review_card_status"] == "review_card_allowed_after_scope_checks"
    assert {item["cut_id"] for item in report["cut_results"]} == {"cut_008"}
    assert result["visual_proof_status"] == "available_requires_human_review"
    assert representative["active_overlay_artifact_id"] == (
        "clip-ed10r-keifont-dense-stress-proof-001"
    )
    assert representative["source_review_artifact_id"] == (
        "clip-ed10p-keifont-lead-representative-proof-001"
    )
    assert representative["review_debt"][0]["status"] == "current_target"
    assert representative["review_memory"]["current_blocker"] == (
        "none_for_font_evidence"
    )
    assert representative["subtitle_overlay_visual_proof"]["review_card_status"] == (
        "review_card_allowed_after_scope_checks"
    )

    focused_html = (review_dir / "current_proof_focused_review.html").read_text(
        encoding="utf-8"
    )
    assert "cut_008 dense/stress diagnostic proof" in focused_html
    assert "subtitle_overlay_visual_proof_cut_008.png" in focused_html
    assert "do not re-decide general Keifont acceptance" in focused_html
    assert "Use this page for ED-10p Keifont review" not in focused_html
    assert "subtitle_overlay_visual_proof_cut_002.png" not in focused_html
    assert "subtitle_overlay_visual_proof_cut_003.png" not in focused_html


def test_subtitle_overlay_visual_proof_ed10r_marks_fallback_font_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    monkeypatch.setattr(
        overlay_proof,
        "_resolve_candidate_font",
        lambda candidate: (
            "Noto Sans JP",
            "C:/Windows/Fonts/NotoSansJP-VF.ttf",
            "candidate_font_paths_missing_used_global_fallback: font_file_found",
        ),
    )

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_008"],
        typography_decoration_candidate_id="ed10l_keifont_pop_dialogue_candidate",
        proof_profile="ed10r_keifont_dense_stress_proof",
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    representative = result["representative_visual_proof_report"]
    evidence = report["font_visual_evidence"]
    assert result["visual_proof_status"] == (
        "blocked_invalid_requested_font_visual_evidence"
    )
    assert report["visual_proof_status"] == (
        "blocked_invalid_requested_font_visual_evidence"
    )
    assert report["review_card_status"] == "withheld_font_visual_evidence_invalid"
    assert evidence["status"] == "blocked_requested_keifont_font_missing_uses_fallback"
    assert evidence["valid_requested_font_visual_evidence"] is False
    assert evidence["requested_font_family"] == "Keifont"
    assert evidence["resolved_font_family"] == "Noto Sans JP"
    assert evidence["resolved_font_file"] == "C:/Windows/Fonts/NotoSansJP-VF.ttf"
    assert any(
        warning.startswith("Keifont proof profile is active")
        for warning in report["warnings"]
    )
    assert representative["font_visual_evidence"]["status"] == (
        "blocked_requested_keifont_font_missing_uses_fallback"
    )
    assert representative["review_card_status"] == (
        "withheld_font_visual_evidence_invalid"
    )
    assert representative["subtitle_overlay_visual_proof"]["review_card_status"] == (
        "withheld_font_visual_evidence_invalid"
    )
    assert report["review_memory"]["repeated_general_review"] is False
    assert report["review_memory"]["next_nonredundant_axis"] == "dense_stress"
    assert report["review_memory"]["current_blocker"] == "font_evidence_fallback"
    assert report["review_memory"]["font_evidence_gate"] == (
        "blocked_requested_keifont_font_missing_uses_fallback"
    )

    focused_html = (review_dir / "current_proof_focused_review.html").read_text(
        encoding="utf-8"
    )
    assert "Font evidence warning" in focused_html
    assert "requested=Keifont; resolved=Noto Sans JP" in focused_html
    assert "do not re-decide general Keifont acceptance" in focused_html


def test_subtitle_overlay_visual_proof_ed10r_profile_requires_cut_008(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    with pytest.raises(SubtitleOverlayVisualProofError, match="cut_008"):
        build_subtitle_overlay_visual_proof(
            episode_dir=episode_dir,
            review_dir=review_dir,
            target_cut_ids=["cut_002", "cut_003"],
            typography_decoration_candidate_id="ed10l_keifont_pop_dialogue_candidate",
            proof_profile="ed10r_keifont_dense_stress_proof",
            ffmpeg_path="fake-ffmpeg",
            ffprobe_path="fake-ffprobe",
            base_dir=tmp_path,
            runner=_fake_runner,
        )


def test_subtitle_overlay_visual_proof_ed10r_profile_requires_keifont(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    with pytest.raises(SubtitleOverlayVisualProofError, match="requires"):
        build_subtitle_overlay_visual_proof(
            episode_dir=episode_dir,
            review_dir=review_dir,
            target_cut_ids=["cut_008"],
            typography_decoration_candidate_id="ed10j_biz_udgothic_bold_telop_candidate",
            proof_profile="ed10r_keifont_dense_stress_proof",
            ffmpeg_path="fake-ffmpeg",
            ffprobe_path="fake-ffprobe",
            base_dir=tmp_path,
            runner=_fake_runner,
        )


def test_build_subtitle_overlay_visual_proof_cli_dry_run_outputs_plan(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    help_result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "build-subtitle-overlay-visual-proof", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert help_result.returncode == 0
    assert "--target-cut" in help_result.stdout
    assert "--typography-decoration-candidate-id" in help_result.stdout
    assert "--proof-profile" in help_result.stdout

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-overlay-visual-proof",
            "--episode-dir",
            str(episode_dir),
            "--review-dir",
            str(review_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--typography-decoration-candidate-id",
            "noto_sans_jp_clean_outline",
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target_cuts"] == ["cut_002", "cut_003"]
    assert payload["dry_run"] is True
    assert payload["visual_proof_status"] == "blocked_no_cut_002_cut_003_overlay_proof"
    assert payload["style_direction_preset"] == "jp_clip_readable_v1"
    assert payload["style_candidate_id"] == "noto_sans_jp_clean_outline"
    assert payload["typography_decoration_candidate_id"] == "noto_sans_jp_clean_outline"
    assert payload["focused_review_html"].endswith(
        "current_proof_focused_review.html"
    )
    assert payload["production_candidate"] is False
    assert payload["rights_status"] == "pending"
    assert not (review_dir / "subtitle_overlay_visual_proof_report.json").exists()
    assert not (review_dir / "subtitle_overlay_visual_proof_cut_002.mp4").exists()


def test_bottom_center_emphasis_layout_writes_centered_ass_without_badge_dialogue(
    tmp_path: Path,
):
    layout = _subtitle_layout_contract(
        frame_width=320,
        frame_height=180,
        mode="bottom_center_emphasis",
        dimension_source="test_frame",
    )
    items = _presentation_items(
        [
            {
                "subtitle_id": "sub_test",
                "status": "included",
                "render_start_seconds": 0.0,
                "render_end_seconds": 2.0,
                "text": "center emphasis",
            }
        ],
        layout=layout,
    )
    ass_path = tmp_path / "bottom_center.burned_in.ass"
    _write_ass(ass_path, items, layout=layout)

    ass = ass_path.read_text(encoding="utf-8")
    assert layout["alignment"] == "bottom_center_emphasis"
    assert layout["values"]["bottom_center_x"] == 160
    assert "\\an2\\pos(160,165)" in ass
    assert "Style: ClipPipeDialogueLeft,Yu Gothic,22," in ass
    assert "Dialogue: 0,0:00:00.00,0:00:02.00,ClipPipeSpeakerBadge" not in ass


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_pillow_font_bbox_wrap_lines_are_passed_to_ass_without_one_character_orphans(
    tmp_path: Path,
):
    _, font_path, _ = spike._select_font()
    if font_path is None:
        pytest.skip("Japanese font file is not available for font-bbox wrapping")
    layout = _subtitle_layout_contract(
        frame_width=1280,
        frame_height=720,
        mode="badge_left_dialogue",
        dimension_source="test_frame",
    )
    items = _presentation_items(
        [
            {
                "subtitle_id": "sub_orphan_1",
                "status": "included",
                "render_start_seconds": 0.0,
                "render_end_seconds": 2.0,
                "text": "この条件、かなり危ないです",
            },
            {
                "subtitle_id": "sub_orphan_2",
                "status": "included",
                "render_start_seconds": 2.0,
                "render_end_seconds": 4.0,
                "text": "まず物件カードを見ます",
            },
        ],
        layout=layout,
    )

    for item in items:
        readback = item["font_bbox_wrap_readback"]
        assert readback["status"] == "applied_to_ass_dialogue_text"
        assert readback["applied_to_proof_text"] is True
        assert readback["explicit_line_breaks_passed_to_ass"] is True
        assert readback["wrap_algorithm"]["name"] == "japanese_boundary_font_bbox_pixel_wrap_v1"
        assert readback["wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
        assert readback["selected_wrapped_lines"] == item["wrapped_lines"]
        assert readback["one_character_orphan_present"] is False
        assert readback["suffix_tail_prevention_applied"] is False
        assert readback["suspicious_tail_line_present"] is False
        assert all(spike._visible_char_count(line) != 1 for line in item["wrapped_lines"])
        assert readback["font_file_status"] == "font_file_found"
        assert readback["measured_bbox_provenance"]["source_function"] == (
            "draw.multiline_textbbox"
        )
        assert readback["renderer_gap"]["exists"] is True
        assert readback["renderer_gap"]["production_typography_readiness_claimed"] is False

    assert items[0]["orphan_prevention_applied"] is True
    assert items[0]["font_bbox_wrap_readback"]["orphan_prevention_examples"]
    assert items[0]["wrapped_lines"] == ["この条件、かなり危", "ないです"]

    ass_path = tmp_path / "bbox_wrapped.burned_in.ass"
    _write_ass(ass_path, items, layout=layout)
    ass = ass_path.read_text(encoding="utf-8")
    assert "この条件、かなり危\\Nないです" in ass
    assert "この条件、かなり危ない\\Nです" not in ass
    assert "この条件、かなり危ないで\\Nす" not in ass


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_overlay_font_bbox_wrap_prevents_suffix_tail_examples():
    _, font_path, _ = spike._select_font()
    if font_path is None:
        pytest.skip("Japanese font file is not available for font-bbox wrapping")
    layout = _subtitle_layout_contract(
        frame_width=1920,
        frame_height=1080,
        mode="badge_left_dialogue",
        dimension_source="test_frame",
    )
    items = _presentation_items(
        [
            {
                "subtitle_id": "sub_013",
                "status": "included",
                "render_start_seconds": 0.0,
                "render_end_seconds": 2.0,
                "text": "なんで来なかったんすか！！",
            },
            {
                "subtitle_id": "sub_017",
                "status": "included",
                "render_start_seconds": 2.0,
                "render_end_seconds": 4.0,
                "text": "まあ謝るんなら許してあげます",
            },
            {
                "subtitle_id": "sub_024",
                "status": "included",
                "render_start_seconds": 4.0,
                "render_end_seconds": 6.0,
                "text": "団長、ちなみに、他の番長知ってますか？",
            },
            {
                "subtitle_id": "sub_025",
                "status": "included",
                "render_start_seconds": 6.0,
                "render_end_seconds": 8.0,
                "text": "長(ちょう)？　長って言った？",
            },
        ],
        layout=layout,
    )

    by_id = {item["subtitle_id"]: item for item in items}
    assert by_id["sub_013"]["wrapped_lines"] == ["なんで来なかった", "んすか！！"]
    assert by_id["sub_013"]["suffix_tail_prevention_applied"] is True
    assert by_id["sub_013"]["suspicious_tail_line_present"] is False
    assert by_id["sub_017"]["wrapped_lines"] != ["まあ謝るんなら許してあげ", "ます"]
    assert by_id["sub_017"]["wrapped_lines"][-1] in {
        "あげます",
        "てあげます",
        "許してあげます",
    }
    assert by_id["sub_017"]["suffix_tail_prevention_applied"] is True
    assert by_id["sub_017"]["suspicious_tail_line_present"] is False
    assert by_id["sub_024"]["wrapped_lines"] == ["団長、ちなみに、他の", "番長知ってますか？"]
    assert by_id["sub_024"]["suffix_tail_prevention_applied"] is False
    assert by_id["sub_025"]["wrapped_lines"] == ["長(ちょう)？　長って", "言った？"]
    assert by_id["sub_025"]["suffix_tail_prevention_applied"] is False
    assert all(
        item["font_bbox_wrap_readback"]["one_character_orphan_present"] is False
        for item in items
    )


def _write_episode(tmp_path: Path) -> Path:
    episode_dir = tmp_path / "episodes" / "jp_pilot01_hololive_bancho_20260525"
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    video_dir = episode_dir / "materials" / "src_video_jp_pilot01"
    audio_dir = episode_dir / "materials" / "src_audio_jp_pilot01"
    review_dir.mkdir(parents=True)
    video_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)
    (video_dir / "source_video.mp4").write_bytes(b"video")
    (audio_dir / "source.wav").write_bytes(b"audio")
    (review_dir / "visual_proof_contact_sheet.png").write_bytes(b"contact-sheet")
    _write_json(_edit_pack(episode_dir.name), episode_dir / "edit_pack.json")
    _write_json(_material_ledger(episode_dir), episode_dir / "material_ledger.json")
    _write_json(_chapter_revision_board(episode_dir.name), review_dir / "chapter_revision_board.json")
    _write_json(_cut_decision_packet(episode_dir.name), review_dir / "cut_decision_packet.json")
    _write_json(_representative_visual_report(episode_dir.name), review_dir / "representative_visual_proof_report.json")
    return episode_dir


def _edit_pack(episode_id: str) -> dict:
    now = "2026-06-04T00:00:00+00:00"
    return {
        "schema_version": "v1",
        "episode_id": episode_id,
        "rights_manifest_path": f"episodes/{episode_id}/rights_manifest.json",
        "material_ledger_path": f"episodes/{episode_id}/material_ledger.json",
        "created_at": now,
        "updated_at": now,
        "editing_intent": {
            "target_duration_seconds": None,
            "topic": "",
            "audience_note": "",
            "language": "ja",
        },
        "cut_candidates": [
            _cut("cut_001", 2.453, 9.293, "passed"),
            _cut("cut_002", 12.329, 17.167, "passed"),
            _cut("cut_003", 22.606, 49.566, "needs_review"),
            _cut("cut_008", 116.934, 135.219, "needs_review"),
        ],
        "selected_cut_ids": ["cut_001", "cut_002", "cut_003", "cut_008"],
        "subtitles": [
            _subtitle("sub_001", "cut_001", 2.453, 3.32, "cut 1"),
            _subtitle("sub_008", "cut_002", 12.329, 14.298, "subtitle 2a"),
            _subtitle("sub_009", "cut_002", 14.298, 17.167, "subtitle 2b"),
            *_cut_003_subtitles(),
            *_cut_008_subtitles(),
        ],
        "review": {
            "status": "draft",
            "reviewed_by": None,
            "reviewed_at": None,
            "notes": [],
        },
    }


def _cut(cut_id: str, start: float, end: float, context_status: str) -> dict:
    return {
        "id": cut_id,
        "start_seconds": start,
        "end_seconds": end,
        "source": "auto",
        "reason": "fixture",
        "confidence": 1.0,
        "context_check": {"status": context_status, "notes": []},
    }


def _subtitle(subtitle_id: str, cut_id: str, start: float, end: float, text: str) -> dict:
    return {
        "id": subtitle_id,
        "cut_id": cut_id,
        "start_seconds": start,
        "end_seconds": end,
        "text": text,
        "source": "auto",
        "source_type": "imported_subtitle_track",
        "source_segment_ids": [subtitle_id.replace("sub", "seg")],
        "draft": True,
        "diagnostic": True,
        "not_production_subtitle_design": True,
    }


def _cut_003_subtitles() -> list[dict]:
    rows = [
        ("sub_010", 22.606, 23.640, "subtitle 3a"),
        ("sub_011", 24.041, 25.109, "subtitle 3b"),
        ("sub_012", 25.109, 26.000, "subtitle 3c"),
        ("sub_013", 26.000, 27.000, "subtitle 3d"),
        ("sub_014", 27.000, 28.000, "subtitle 3e"),
        ("sub_015", 28.000, 29.000, "subtitle 3f"),
        ("sub_016", 29.000, 30.000, "subtitle 3g"),
        ("sub_017", 30.000, 31.000, "subtitle 3h"),
        ("sub_018", 31.000, 32.000, "subtitle 3i"),
        ("sub_019", 32.000, 33.000, "subtitle 3j"),
        ("sub_020", 33.000, 34.000, "subtitle 3k"),
        ("sub_021", 34.000, 35.000, "subtitle 3l"),
        ("sub_022", 35.000, 36.000, "subtitle 3m"),
        ("sub_023", 36.000, 37.000, "subtitle 3n"),
        ("sub_024", 37.000, 38.000, "subtitle 3o"),
        ("sub_025", 38.000, 40.000, "response block starts"),
        ("sub_026", 40.000, 42.000, "response block continues"),
        ("sub_027", 42.000, 44.000, "response block detail"),
        ("sub_028", 44.000, 46.000, "response block referral"),
        ("sub_029", 46.000, 49.566, "response block closes"),
    ]
    return [_subtitle(subtitle_id, "cut_003", start, end, text) for subtitle_id, start, end, text in rows]


def _cut_008_subtitles() -> list[dict]:
    rows = [
        ("sub_069", 116.934, 117.402, "dense stress opening"),
        ("sub_070", 117.402, 118.236, "rapid handoff with longer dialogue"),
        ("sub_071", 118.236, 119.204, "wrap pressure continues across the same beat"),
        ("sub_072", 119.204, 120.204, "short response"),
        ("sub_073", 120.204, 120.671, "very fast cue"),
        ("sub_074", 120.671, 121.238, "another fast cue"),
        ("sub_075", 121.238, 121.672, "timing replacement check"),
        ("sub_076", 121.672, 123.672, "dense subtitle line with punctuation and extra length"),
        ("sub_077", 123.672, 126.000, "badge and outline pressure should stay reviewable"),
        ("sub_078", 126.000, 129.500, "stress block keeps going without becoming production approval"),
        ("sub_079", 129.500, 135.219, "final dense stress line closes the proof"),
    ]
    return [
        _subtitle(subtitle_id, "cut_008", start, end, text)
        for subtitle_id, start, end, text in rows
    ]


def _material_ledger(episode_dir: Path) -> dict:
    return {
        "schema_version": "v1",
        "episode_id": episode_dir.name,
        "materials": [
            {
                "id": "src_video_jp_pilot01",
                "kind": "source_video",
                "file_path": str(episode_dir / "materials" / "src_video_jp_pilot01" / "source_video.mp4"),
                "hash_sha256": "video-hash",
                "byte_size": 5,
            },
            {
                "id": "src_audio_jp_pilot01",
                "kind": "source_audio",
                "file_path": str(episode_dir / "materials" / "src_audio_jp_pilot01" / "source.wav"),
                "hash_sha256": "audio-hash",
                "byte_size": 5,
            },
        ],
    }


def _chapter_revision_board(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "artifact_kind": "chapter_revision_board",
        "episode_id": episode_id,
        "chapters": [
            _chapter("ch_002", "cut_002", "passed", False, 4.838, 2),
            _chapter("ch_003", "cut_003", "needs_review", True, 26.96, 20),
            _chapter("ch_008", "cut_008", "needs_review", True, 18.285, 11),
        ],
    }


def _chapter(
    chapter_id: str,
    cut_id: str,
    context_status: str,
    retained_context_risk: bool,
    duration: float,
    subtitle_count: int,
) -> dict:
    return {
        "chapter_id": chapter_id,
        "source_cut_id": cut_id,
        "duration_seconds": duration,
        "original_context_status": context_status,
        "retained_context_risk": retained_context_risk,
        "subtitle_count": subtitle_count,
        "subtitle_density": 0.5,
        "subtitle_chars_per_second": 8.0,
        "line_wrap_proxy": {"proxy_only": True},
        "timing_span": {},
        "current_risks": ["retained_context_risk"] if retained_context_risk else [],
    }


def _cut_decision_packet(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "artifact_kind": "r3_cut_decision_packet",
        "episode_id": episode_id,
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": "pending",
        "decisions": [
            {
                "cut_id": "cut_002",
                "final_cut_decision": "keep",
                "context_status": "passed",
                "duration_seconds": 4.838,
                "subtitle_event_count": 2,
                "manual_override_reason": None,
            },
            {
                "cut_id": "cut_003",
                "final_cut_decision": "keep",
                "context_status": "needs_review",
                "duration_seconds": 26.96,
                "subtitle_event_count": 20,
                "manual_override_reason": "retained risk stays visible",
            },
            {
                "cut_id": "cut_008",
                "final_cut_decision": "keep",
                "context_status": "needs_review",
                "duration_seconds": 18.285,
                "subtitle_event_count": 11,
                "manual_override_reason": "dense stress target stays diagnostic",
            },
        ],
    }


def _representative_visual_report(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "report_kind": "representative_visual_proof_report",
        "episode_id": episode_id,
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": "pending",
        "production_usage_allowed": False,
        "per_cut_visual_assessment": [
            {
                "cut_id": "cut_001",
                "visual_proof_status": "available_diagnostic_render_frame",
                "visual_proof_artifact_path": "review/visual_proof_cut_001.png",
                "source_used": "existing_cut_001_diagnostic_render_frame_with_subtitle_overlay",
                "typography_status": "diagnostic_overlay_visible_human_review_required",
                "safe_area_status": "diagnostic_overlay_visible_human_review_required",
                "line_wrapping_status": "proxy_ok",
                "timing_sync_status": "diagnostic_timing_proxy_available_visual_audio_review_required",
                "retained_context_risk": False,
            },
            _source_frame_assessment("cut_002", False),
            _source_frame_assessment("cut_003", True),
            _source_frame_assessment("cut_008", True),
        ],
        "outputs": {
            "json": f"episodes/{episode_id}/review/jp_pilot01r3_cut_review/representative_visual_proof_report.json",
            "html": f"episodes/{episode_id}/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html",
            "contact_sheet": f"episodes/{episode_id}/review/jp_pilot01r3_cut_review/visual_proof_contact_sheet.png",
        },
    }


def _source_frame_assessment(cut_id: str, retained_context_risk: bool) -> dict:
    return {
        "cut_id": cut_id,
        "visual_proof_status": "available_source_frame_only_no_subtitle_overlay",
        "visual_proof_artifact_path": f"review/visual_proof_{cut_id}.png",
        "source_used": "existing_source_video_frame_only",
        "typography_status": "visual_proof_required_no_subtitle_overlay",
        "safe_area_status": "visual_proof_required_no_subtitle_overlay",
        "line_wrapping_status": "line_wrap_visual_review_required",
        "timing_sync_status": "timing_visual_audio_review_required",
        "retained_context_risk": retained_context_risk,
        "proof_limitations": ["source frame has no subtitle overlay"],
        "recommended_next_action": ["generate_representative_diagnostic_visual_proof"],
    }


def _fake_runner(args, *, capture_output: bool, text: bool, timeout: int):
    command = [str(arg) for arg in args]
    if "-version" in command:
        return subprocess.CompletedProcess(args, 0, stdout=f"{Path(command[0]).name} version fake\n", stderr="")
    if "-print_format" in command and "-show_streams" in command:
        payload = {
            "format": {"duration": "1.5", "format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "codec_long_name": "H.264",
                    "width": 320,
                    "height": 180,
                    "avg_frame_rate": "24/1",
                },
                {"codec_type": "audio", "codec_name": "aac", "codec_long_name": "AAC"},
            ],
        }
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload), stderr="")
    output = Path(command[-1])
    output.parent.mkdir(parents=True, exist_ok=True)
    if "-frames:v" in command:
        output.write_bytes(b"png")
    else:
        output.write_bytes(b"video")
    return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
