"""Docs v1.5 dashboard tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from src.pipeline.docs_dashboard import build_project_status, write_project_status


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_docs_dashboard_detects_unclear_and_over_guarded_docs(tmp_path: Path):
    _write_fixture_docs(tmp_path)

    result = write_project_status(
        base_dir=tmp_path,
        output_dir=tmp_path / "docs" / "dashboard",
        generated_at="test-run",
    )

    status = result["status"]
    findings = status["doc_health"]["findings"]
    assert status["schema_id"] == "clippipegen.docs_dashboard.v1_5"
    assert status["project"]["wiki_entry"] == "docs/index.md"
    assert status["current_focus"]["feature_id"] == "ED-10y"
    assert status["current_focus"]["artifact_id"] == (
        "clip-ed10y-candidate2-carry-forward-001"
    )
    assert status["current_focus"]["source_review_artifact_id"] == (
        "clip-ed10w-subtitle-presentation-review-pack-001"
    )
    assert status["current_focus"]["source_comparison_artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert status["current_focus"]["source_proof_artifact_id"] == (
        "clip-ed10r-keifont-dense-stress-proof-001"
    )
    assert status["current_focus"]["state"] == (
        "candidate2_carry_forward_ready"
    )
    assert status["current_focus"]["human_visual_judgement"] == (
        "ed10w_candidate2_lead_freeform_review_consumed"
    )
    assert status["current_focus"]["latest_review_consumed"] == (
        "ed10w_user_review_candidate0_and_2_good_candidate1_and_3_too_thin"
    )
    assert status["current_focus"]["target_cuts"] == ["cut_008"]
    assert status["current_focus"]["selected_typography_base"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert status["current_focus"]["selected_source_license_install_route"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert status["current_focus"]["route_status"] == (
        "candidate2_promoted_to_provisional_bounded_decoration_lead"
    )
    assert status["current_focus"]["user_action_type"] == (
        "NO_USER_ACTION_REVIEW_CONSUMED"
    )
    assert status["current_focus"]["next_review_action_type"] == (
        "NO_REVIEW_CARD_REVIEW_CONSUMED"
    )
    assert status["current_focus"]["current_visual_comparison_validity"] == (
        "valid_requested_keifont_visual_evidence"
    )
    assert status["current_focus"]["review_surface_direction"] == (
        "one_pass_subtitle_presentation_review_pack"
    )
    assert status["current_focus"]["font_visual_evidence_status"] == (
        "valid_requested_keifont_visual_evidence_on_current_windows_profile"
    )
    assert status["current_focus"]["multiline_wrap_evidence_status"] == (
        "passed_diagnostic_review"
    )
    assert status["current_focus"]["multiline_wrap_evidence"]["subtitle_id"] == (
        "sub_096"
    )
    assert status["current_focus"]["multiline_wrap_evidence"][
        "screenshot_default_max_width_px"
    ] == 220
    assert status["current_focus"]["line_break_policy_readback"]["status"] == (
        "diagnostic_policy_recorded"
    )
    assert status["current_focus"]["line_break_policy_readback"][
        "accepted_evidence"
    ] == "cut_008/sub_096 two-line wrap"
    assert "NLMYTGen" in status["current_focus"]["line_break_policy_readback"][
        "shared_policy_note"
    ]
    assert status["current_focus"]["review_memory"]["prior_review_count"] == "3+"
    assert status["current_focus"]["review_memory"][
        "latest_freeform_review_consumed"
    ] is True
    assert status["current_focus"]["review_memory"]["lead_candidate"] == (
        "ed10w_badge_label_pressure_adjustment"
    )
    assert "candidate2_render_path_nearer_probe_readback" in status["current_focus"]["review_memory"][
        "next_nonredundant_axis"
    ]
    assert status["current_focus"]["review_memory"]["repeated_general_review"] is False
    assert status["current_focus"]["review_memory"][
        "same_candidate_comparison_review_allowed"
    ] is False
    assert status["current_focus"]["review_memory"]["current_blocker"] == (
        "none_for_candidate2_carry_forward"
    )
    assert status["current_focus"]["review_memory"]["font_evidence_gate"] == (
        "valid_requested_keifont_visual_evidence"
    )
    assert status["current_focus"]["review_card"]["action_type"] == (
        "NO_REVIEW_CARD_REVIEW_CONSUMED"
    )
    assert status["current_focus"]["review_card"]["status"] == (
        "withheld_latest_review_already_consumed"
    )
    assert status["current_focus"]["review_card"]["target"] == (
        "clip-ed10y-candidate2-carry-forward-001"
    )
    assert status["current_focus"]["review_card"]["axis"] == (
        "candidate2_carry_forward + render_path_nearer_probe"
    )
    assert "cut_002 / cut_003 review" in status["current_focus"]["review_card"][
        "not_asking"
    ]
    assert status["current_focus"]["focused_review_html"] == (
        "episodes/.../subtitle_presentation_review_pack.html"
    )
    assert status["current_focus"]["review_debt"][0]["debt_id"] == (
        "render_path_nearer_probe"
    )
    assert status["current_focus"]["review_debt"][0]["status"] == (
        "candidate2_tiny_diagnostic_probe_included"
    )
    assert status["current_focus"]["bounded_decoration_candidates"] == [
        "ed10w_current_pass_reference",
        "ed10w_lighter_outline_shadow_pressure",
        "ed10w_badge_label_pressure_adjustment",
        "ed10w_balanced_combined_low_risk",
    ]
    assert status["current_focus"]["candidate_delta_visibility"]["status"] == (
        "consumed_candidate2_promoted_after_ed10x_fix"
    )
    assert "compact subtitle body crops" in status["current_focus"][
        "candidate_delta_visibility"
    ]["default_evidence"]
    assert status["current_focus"]["lead_fallback_readback"]["lead_candidate"] == (
        "ed10w_badge_label_pressure_adjustment"
    )
    assert status["current_focus"]["lead_fallback_readback"]["fallback_reference"] == (
        "ed10w_current_pass_reference"
    )
    assert status["current_focus"]["render_path_readiness"]["status"] == (
        "candidate2_tiny_render_path_nearer_diagnostic_probe_completed"
    )
    assert status["current_focus"]["production_subtitle_design_acceptance"] is False
    assert status["current_focus"]["production_render_acceptance"] is False
    assert status["current_focus"]["production_usage_allowed"] is False
    assert [item["command"] for item in status["open_surfaces"]] == [
        ".\\open-dashboard.ps1",
        ".\\open-artifacts.ps1",
        ".\\open-current-proof.ps1",
        (
            "powershell -ExecutionPolicy Bypass -File "
            "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
            "jp_pilot01r3_cut_review\\subtitle_multifont_focused_review\\"
            "open_comparison.ps1"
        ),
        (
            "powershell -ExecutionPolicy Bypass -File "
            "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
            "jp_pilot01r3_cut_review\\subtitle_known_kirinuki_font_pack_comparison\\"
            "open_comparison.ps1"
        ),
        "see artifact registry for archived previous proof paths",
        (
            "powershell -ExecutionPolicy Bypass -File "
            "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
            "jp_pilot01r3_cut_review\\subtitle_kirinuki_font_audit\\"
            "open_comparison.ps1"
        ),
        (
            "powershell -ExecutionPolicy Bypass -File "
            "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
            "jp_pilot01r3_cut_review\\subtitle_kirinuki_gothic_balance_comparison\\"
            "open_comparison.ps1"
        ),
        ".\\open-font-candidates.ps1",
    ]
    assert status["doc_health"]["finding_total"] >= status["doc_health"]["finding_count"]
    assert status["doc_health"]["finding_limit"] == 50
    assert status["feature_summary"]["status_counts"]["done"] == 1
    assert status["features"][0]["id"] == "ED-01"
    assert status["features"][0]["progress_pct"] == 100
    assert status["artifact_coverage"]["registered_artifact_count"] == 1
    assert status["next_review_items"][0]["artifact"] == (
        "clip-ed10y-candidate2-carry-forward-001"
    )
    assert "clip-test-artifact" in status["artifact_summary"]["artifact_ids"]
    assert {finding["type"] for finding in findings} >= {"unclear", "over_guarded"}
    assert result["json_path"].exists()
    assert result["html_path"].exists()
    assert result["features_path"].exists()

    persisted = json.loads(result["json_path"].read_text(encoding="utf-8"))
    html = result["html_path"].read_text(encoding="utf-8")
    features_index = result["features_path"].read_text(encoding="utf-8")
    assert persisted["generated_at"] == "test-run"
    assert persisted["open_surfaces"][0]["target"] == "docs/dashboard/index.html"
    assert persisted["open_surfaces"][2]["target"] == (
        "episodes/.../subtitle_presentation_review_pack.html"
    )
    assert "Candidate 2 lead" in persisted["open_surfaces"][2][
        "when_to_use"
    ]
    assert "Open Surfaces" in html
    assert "subtitle_known_kirinuki_font_pack" in html
    assert "subtitle_kirinuki_font_audit" in html
    assert "Doc Health Findings" in html
    assert "Feature Progress" in html
    assert "Active Artifacts" in html
    assert "Next Review Items" in html
    assert "clip-ed10r-keifont-dense-stress-proof-001" in html
    assert "clip-ed10y-candidate2-carry-forward-001" in html
    assert "clip-ed10p-keifont-lead-representative-proof-001" in html
    assert "clip-ed10o-multifont-focused-review-001" in html
    assert "subtitle_multifont_focused_review" in html
    assert "clip-ed10n-keifont-overlay-proof-001" in html
    assert "clip-ed10l-known-kirinuki-font-pack-001" in html
    assert "| ED-01 | Editing | done | stable | 100 |  |" in features_index


def test_build_docs_dashboard_cli_writes_outputs(tmp_path: Path):
    _write_fixture_docs(tmp_path)
    output_dir = tmp_path / "docs" / "dashboard"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-docs-dashboard",
            "--output-dir",
            str(output_dir),
            "--generated-at",
            "cli-test",
            "--format",
            "json",
        ],
        cwd=str(tmp_path),
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "clippipegen.docs_dashboard.v1_5"
    assert payload["dashboard_json"].endswith("project-status.json")
    assert payload["dashboard_html"].endswith("index.html")
    assert payload["features_index"].endswith("features/index.md")
    assert payload["feature_count"] == 1
    assert payload["artifact_count"] == 1
    assert payload["finding_total"] >= payload["finding_count"]
    assert isinstance(payload["findings_truncated"], bool)
    assert (output_dir / "project-status.json").exists()
    assert (output_dir / "index.html").exists()
    assert (tmp_path / "docs" / "features" / "index.md").exists()


def test_open_current_proof_launcher_targets_focused_review_surface():
    launcher = (REPO_ROOT / "open-current-proof.ps1").read_text(encoding="utf-8")

    assert "subtitle_presentation_review_pack.html" in launcher
    assert "current_proof_focused_review.html" in launcher
    relative_target_line = next(
        line for line in launcher.splitlines() if line.startswith("$relativeTarget")
    )
    assert "subtitle_presentation_review_pack.html" in relative_target_line
    assert "current_proof_focused_review.html" not in relative_target_line
    assert "subtitle_overlay_visual_proof_report.html" not in relative_target_line


def test_subtitle_font_candidate_registry_is_machine_readable():
    registry_path = (
        REPO_ROOT / "docs" / "font_candidates" / "subtitle-font-candidates.json"
    )

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    candidate_ids = {candidate["candidate_id"] for candidate in registry["candidates"]}

    assert registry["artifact_id"] == "clip-subtitle-font-candidate-sweep-001"
    assert registry["current_selected_diagnostic_overlay_proof_base"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert registry["font_size_policy"]["formula"] == "round(frame_height * 0.115)"
    assert registry["boundary_flags"]["font_binaries_downloaded"] is False
    assert registry["boundary_flags"]["production_candidate"] is False
    assert registry["ed10i_narrow_slice"]["artifact_id"] == (
        "clip-ed10i-kirinuki-gothic-balance-001"
    )
    assert registry["ed10i_narrow_slice"]["recommended_default_candidate_id"] == (
        "ed10i_biz_udgothic_bold_balanced_outline"
    )
    assert registry["ed10i_narrow_slice"]["selected_candidate_id"] == (
        "ed10i_meiryo_bold_fill_outline_balance"
    )
    assert registry["ed10i_narrow_slice"]["selected_overlay_artifact_id"] == (
        "clip-ed10i-meiryo-overlay-proof-001"
    )
    assert registry["ed10i_narrow_slice"]["selected_overlay_review_status"] == (
        "reviewed_not_accepted_as_normal_baseline"
    )
    assert registry["ed10j_research_audit_slice"]["artifact_id"] == (
        "clip-ed10j-kirinuki-font-audit-001"
    )
    assert registry["ed10j_research_audit_slice"]["recommended_default_candidate_id"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert registry["ed10j_research_audit_slice"]["selected_candidate_id"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert registry["ed10j_research_audit_slice"]["selected_overlay_artifact_id"] == (
        "clip-ed10k-biz-overlay-proof-001"
    )
    assert registry["ed10j_research_audit_slice"]["badge_color_readback"][
        "blue_badge_candidate_id"
    ] == "ed10j_noto_sans_jp_local_telop_candidate"
    assert registry["ed10j_research_audit_slice"]["badge_color_readback"][
        "blue_badge_is_meiryo_reference"
    ] is False
    assert registry["ed10k_overlay_proof_slice"]["review_status"] == (
        "reviewed_not_accepted_as_normal_baseline"
    )
    assert registry["ed10l_known_font_pack_slice"]["artifact_id"] == (
        "clip-ed10l-known-kirinuki-font-pack-001"
    )
    assert registry["ed10l_known_font_pack_slice"]["recommended_default_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert registry["ed10l_known_font_pack_slice"][
        "selected_source_license_install_route_candidate_id"
    ] == "ed10l_keifont_pop_dialogue_candidate"
    assert registry["ed10m_real_font_source_license_install_route"][
        "selected_candidate_id"
    ] == "ed10l_keifont_pop_dialogue_candidate"
    assert registry["ed10m_real_font_source_license_install_route"][
        "font_binaries_downloaded"
    ] is False
    assert registry["ed10l_known_font_pack_slice"]["selected_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert registry["ed10l_known_font_pack_slice"]["review_status"] == (
        "per_user_font_readback_valid_keifont_proof_generated"
    )
    assert registry["ed10l_known_font_pack_slice"][
        "candidate_selection_from_current_pngs_allowed"
    ] is True
    assert registry["ed10l_known_font_pack_slice"][
        "current_visual_comparison_validity"
    ] == (
        "valid_requested_font_visual_evidence_after_per_user_font_readback"
    )
    assert registry["ed10l_known_font_pack_slice"]["self_diagnosis"][
        "candidate_universe_bias"
    ] == "system_safe_generic_readability"
    assert registry["ed10l_known_font_pack_slice"]["local_font_readback"][
        "target_fonts_found"
    ] == ["Keifont", "851 Chikara Yowaku", "M+ FONTS", "Yasashisa Gothic"]
    assert registry["ed10m_real_font_source_license_install_route"][
        "local_font_file_found"
    ] is True
    assert registry["ed10n_per_user_font_readback_and_real_proof"][
        "selected_overlay_candidate_id"
    ] == "ed10l_keifont_pop_dialogue_candidate"
    assert registry["ed10n_per_user_font_readback_and_real_proof"][
        "font_binaries_copied_or_vendored"
    ] is False
    assert registry["ed10o_multifont_focused_review"]["artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert registry["ed10o_multifont_focused_review"]["review_surface_status"] == (
        "focused_review_surface_accepted_as_review_direction"
    )
    assert registry["ed10o_multifont_focused_review"]["human_review_consumed"][
        "focused_review_surface_easier_to_understand"
    ] is True
    assert registry["ed10o_multifont_focused_review"]["human_review_consumed"][
        "final_baseline_acceptance"
    ] is False
    assert registry["ed10o_multifont_focused_review"][
        "source_proof_artifact_id"
    ] == "clip-ed10n-keifont-overlay-proof-001"
    assert registry["ed10o_multifont_focused_review"]["primary_visual"] == (
        "subtitle_area_crop_matrix"
    )
    assert registry["ed10o_multifont_focused_review"][
        "current_lead_candidate_id"
    ] == "ed10l_keifont_pop_dialogue_candidate"
    assert registry["ed10o_multifont_focused_review"][
        "included_candidate_ids"
    ] == [
        "ed10l_keifont_pop_dialogue_candidate",
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    ]
    assert registry["ed10o_multifont_focused_review"]["excluded_candidates"] == [
        {
            "candidate_id": "ed10l_m_plus_fonts_dialogue_candidate",
            "reason": "weight_style_unresolved",
            "readback": "M PLUS 1 Thin via MPLUS1-VariableFont_wght.ttf",
            "next_action": (
                "pin an exact non-thin M+ weight/style before including it "
                "in baseline comparison"
            ),
        }
    ]
    assert registry["ed10o_multifont_focused_review"][
        "production_subtitle_design_acceptance"
    ] is False
    assert registry["ed10o_multifont_focused_review"][
        "font_binaries_copied_or_vendored"
    ] is False
    assert registry["ed10p_keifont_lead_representative_proof"]["artifact_id"] == (
        "clip-ed10p-keifont-lead-representative-proof-001"
    )
    assert registry["ed10p_keifont_lead_representative_proof"][
        "source_review_artifact_id"
    ] == "clip-ed10o-multifont-focused-review-001"
    assert registry["ed10p_keifont_lead_representative_proof"]["proof_profile"] == (
        "ed10p_keifont_lead_representative_proof"
    )
    assert registry["ed10p_keifont_lead_representative_proof"][
        "current_review_page"
    ].endswith("current_proof_focused_review.html")
    assert registry["ed10p_keifont_lead_representative_proof"][
        "detailed_overlay_report"
    ].endswith("subtitle_overlay_visual_proof_report.html")
    assert registry["ed10p_keifont_lead_representative_proof"][
        "current_lead_candidate_id"
    ] == "ed10l_keifont_pop_dialogue_candidate"
    assert registry["ed10p_keifont_lead_representative_proof"]["lead_status"] == (
        "diagnostic_representative_normal_dialogue_provisional_baseline"
    )
    assert registry["ed10p_keifont_lead_representative_proof"][
        "review_surface_direction"
    ] == "ed10o_focused_matrix_accepted_as_preferred_review_direction"
    assert registry["ed10p_keifont_lead_representative_proof"][
        "included_candidate_ids"
    ] == ["ed10l_keifont_pop_dialogue_candidate"]
    assert registry["ed10p_keifont_lead_representative_proof"][
        "alternates_preserved"
    ] == [
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    ]
    assert registry["ed10p_keifont_lead_representative_proof"]["review_debt"][0][
        "debt_id"
    ] == "cut_008_dense_stress_proof"
    assert registry["ed10p_keifont_lead_representative_proof"]["review_debt"][0][
        "status"
    ] == "superseded_by_ed10r_current_target"
    assert registry["ed10p_keifont_lead_representative_proof"][
        "keifont_general_acceptance_reopened"
    ] is False
    assert registry["ed10p_keifont_lead_representative_proof"][
        "production_subtitle_design_acceptance"
    ] is False
    assert registry["ed10p_keifont_lead_representative_proof"][
        "font_binaries_copied_or_vendored"
    ] is False
    assert registry["ed10q_current_proof_focused_review_fix"]["feature_id"] == (
        "ED-10q"
    )
    assert registry["ed10q_current_proof_focused_review_fix"]["artifact_id"] == (
        "clip-ed10p-keifont-lead-representative-proof-001"
    )
    assert registry["ed10q_current_proof_focused_review_fix"][
        "launcher_target"
    ].endswith("current_proof_focused_review.html")
    assert registry["ed10q_current_proof_focused_review_fix"][
        "debug_tables_primary"
    ] is False
    assert registry["ed10q_current_proof_focused_review_fix"][
        "first_view_order"
    ][0] == "Review Focus: Current Proof"
    assert registry["ed10q_current_proof_focused_review_fix"][
        "production_subtitle_design_acceptance"
    ] is False
    assert registry["ed10r_keifont_dense_stress_proof"]["feature_id"] == "ED-10v"
    assert registry["ed10r_keifont_dense_stress_proof"]["artifact_id"] == (
        "clip-ed10r-keifont-dense-stress-proof-001"
    )
    assert registry["ed10r_keifont_dense_stress_proof"]["proof_profile"] == (
        "ed10r_keifont_dense_stress_proof"
    )
    assert registry["ed10r_keifont_dense_stress_proof"]["target_cut_ids"] == [
        "cut_008"
    ]
    assert registry["ed10r_keifont_dense_stress_proof"]["baseline_scope"] == (
        "diagnostic_representative_normal_dialogue_provisional"
    )
    assert registry["ed10r_keifont_dense_stress_proof"][
        "keifont_general_acceptance_reopened"
    ] is False
    assert registry["ed10r_keifont_dense_stress_proof"]["user_action_type"] == (
        "NO_REVIEW_CARD_CURRENT_AXIS_PASSED"
    )
    assert registry["ed10r_keifont_dense_stress_proof"][
        "next_review_action_type"
    ] == "NEW_AXIS_ONLY"
    assert registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
        "prior_review_count"
    ] == "3+"
    assert "linebreak_policy_readback" in registry[
        "ed10r_keifont_dense_stress_proof"
    ]["review_memory"]["next_nonredundant_axis"]
    assert registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
        "repeated_general_review"
    ] is False
    assert registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
        "current_blocker"
    ] == "none_for_diagnostic_dense_stress"
    assert registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
        "font_evidence_gate"
    ] == "valid_requested_keifont_visual_evidence"
    assert registry["ed10r_keifont_dense_stress_proof"]["review_debt"][0][
        "status"
    ] == "closed_diagnostic_pass"
    assert registry["ed10r_keifont_dense_stress_proof"][
        "current_workspace_font_visual_evidence"
    ]["status"] == "valid_requested_keifont_visual_evidence"
    assert registry["ed10r_keifont_dense_stress_proof"][
        "multiline_wrap_evidence"
    ]["status"] == "passed_diagnostic_review"
    assert registry["ed10r_keifont_dense_stress_proof"][
        "multiline_wrap_evidence"
    ]["subtitle_id"] == "sub_096"
    assert registry["ed10r_keifont_dense_stress_proof"][
        "multiline_wrap_evidence"
    ]["default_display_max_width_px"] == 220
    assert registry["ed10r_keifont_dense_stress_proof"][
        "line_break_policy_readback"
    ]["status"] == "diagnostic_policy_recorded"
    assert "NLMYTGen" in registry["ed10r_keifont_dense_stress_proof"][
        "line_break_policy_readback"
    ]["nlmytgen_portability_note"]
    assert registry["ed10r_keifont_dense_stress_proof"]["review_card"][
        "action_type"
    ] == "NO_REVIEW_CARD_CURRENT_AXIS_PASSED"
    assert registry["ed10r_keifont_dense_stress_proof"]["review_card"][
        "status"
    ] == "withheld_no_redundant_review_after_pass"
    assert registry["ed10r_keifont_dense_stress_proof"]["review_card"][
        "axis"
    ] == "dense_stress"
    assert registry["ed10r_keifont_dense_stress_proof"][
        "production_subtitle_design_acceptance"
    ] is False
    assert registry["ed10r_keifont_dense_stress_proof"][
        "production_render_acceptance"
    ] is False
    assert registry["ed10r_keifont_dense_stress_proof"][
        "font_binaries_copied_or_vendored"
    ] is False
    assert registry["ed10w_subtitle_presentation_review_pack"]["feature_id"] == (
        "ED-10w"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"]["artifact_id"] == (
        "clip-ed10w-subtitle-presentation-review-pack-001"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"]["proof_profile"] == (
        "ed10w_subtitle_presentation_review_pack"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "current_review_page"
    ].endswith("subtitle_presentation_review_pack.html")
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "bounded_decoration_candidates"
    ] == [
        "ed10w_current_pass_reference",
        "ed10w_lighter_outline_shadow_pressure",
        "ed10w_badge_label_pressure_adjustment",
        "ed10w_balanced_combined_low_risk",
    ]
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "render_path_readiness"
    ]["status"] == "decision_card_included_no_production_claim"
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "candidate_delta_visibility"
    ]["status"] == "reviewable_after_ed10x_fix"
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "candidate_delta_visibility"
    ]["candidate_3_expected_delta"] == (
        "combined_outline_shadow_and_badge_pressure_reduction"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"]["review_card"][
        "status"
    ] == "emitted_nonredundant_new_axis"
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "keifont_general_acceptance_reopened"
    ] is False
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "production_subtitle_design_acceptance"
    ] is False
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "production_render_acceptance"
    ] is False
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "font_binaries_copied_or_vendored"
    ] is False
    assert registry["ed10y_candidate2_carry_forward"]["feature_id"] == "ED-10y"
    assert registry["ed10y_candidate2_carry_forward"]["artifact_id"] == (
        "clip-ed10y-candidate2-carry-forward-001"
    )
    assert registry["ed10y_candidate2_carry_forward"]["proof_profile"] == (
        "ed10y_candidate2_carry_forward"
    )
    assert registry["ed10y_candidate2_carry_forward"]["current_lead_candidate_id"] == (
        "ed10w_badge_label_pressure_adjustment"
    )
    assert registry["ed10y_candidate2_carry_forward"][
        "fallback_reference_candidate_id"
    ] == "ed10w_current_pass_reference"
    assert registry["ed10y_candidate2_carry_forward"][
        "held_reference_candidate_ids"
    ] == [
        "ed10w_lighter_outline_shadow_pressure",
        "ed10w_balanced_combined_low_risk",
    ]
    assert registry["ed10y_candidate2_carry_forward"]["review_memory"][
        "latest_freeform_review_consumed"
    ] is True
    assert registry["ed10y_candidate2_carry_forward"]["review_memory"][
        "same_candidate_comparison_review_allowed"
    ] is False
    assert registry["ed10y_candidate2_carry_forward"]["render_path_readiness"][
        "status"
    ] == "candidate2_tiny_render_path_nearer_diagnostic_probe_completed"
    assert registry["ed10y_candidate2_carry_forward"]["review_card"][
        "action_type"
    ] == "NO_REVIEW_CARD_REVIEW_CONSUMED"
    assert registry["ed10y_candidate2_carry_forward"][
        "production_subtitle_design_acceptance"
    ] is False
    assert registry["ed10y_candidate2_carry_forward"][
        "font_binaries_copied_or_vendored"
    ] is False
    assert "noto_sans_jp_clean_outline" in candidate_ids
    assert "ed10i_reference_noto_clean_outline" in candidate_ids
    assert "ed10i_biz_udgothic_bold_balanced_outline" in candidate_ids
    assert "ed10i_yu_gothic_bold_thin_outline" in candidate_ids
    assert "ed10i_meiryo_bold_fill_outline_balance" in candidate_ids
    assert "ed10j_reference_meiryo_reviewed_not_baseline" in candidate_ids
    assert "ed10j_biz_udgothic_bold_telop_candidate" in candidate_ids
    assert "ed10j_yu_gothic_bold_system_candidate" in candidate_ids
    assert "ed10j_noto_sans_jp_local_telop_candidate" in candidate_ids
    assert "ed10l_keifont_pop_dialogue_candidate" in candidate_ids
    assert "ed10l_851_chikara_yowaku_dialogue_candidate" in candidate_ids
    assert "ed10l_m_plus_fonts_dialogue_candidate" in candidate_ids
    assert "ed10l_yasashisa_gothic_goodfreefonts_candidate" in candidate_ids
    assert "ed10l_851_chikara_zuyoku_emphasis_candidate" in candidate_ids
    assert "ed10l_source_han_serif_mood_candidate" in candidate_ids
    assert "ed10l_shippori_mincho_mood_candidate" in candidate_ids
    assert "m_plus_1p_bold" in candidate_ids
    assert "dela_gothic_one_emphasis" in candidate_ids
    assert "noto_serif_jp_narration_local" in candidate_ids


def test_subtitle_presentation_contract_records_ed10v_linebreak_policy():
    text = (REPO_ROOT / "docs" / "SUBTITLE_PRESENTATION_CONTRACT.md").read_text(
        encoding="utf-8"
    )

    assert "ED-10v records the current line-break behavior" in text
    assert "Current Cut_008 Dense/Stress Diagnostic Pass" in text
    assert "Current ED-10w Presentation Review Pack" in text
    assert "Current ED-10y Candidate 2 Carry-Forward" in text
    assert "clip-ed10w-subtitle-presentation-review-pack-001" in text
    assert "ed10w_badge_label_pressure_adjustment" in text
    assert "ed10w_balanced_combined_low_risk" in text
    assert "diagnostic dense/stress behavior" in text
    assert "`sub_096` multiline/wrap evidence" in text
    assert "Future Shared Line-Break Policy Note" in text
    compact_text = " ".join(text.split())
    assert "do not read, edit, or depend on NLMYTGen files" in compact_text


def _write_fixture_docs(base: Path) -> None:
    (base / "docs").mkdir(parents=True)
    (base / "artifacts").mkdir()
    (base / "README.md").write_text(
        "# Fixture\n\n## What This Is\nA fixture.\n\n## Current State\nReady.\n\n"
        "## Next\nContinue.\n\n## Constraints / Risks\nNone.\n",
        encoding="utf-8",
    )
    (base / "docs" / "index.md").write_text(
        "# Docs Index\n\n## What This Is\nA front door.\n\n## Current State\nReady.\n\n"
        "## Next\nUse dashboard.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    (base / "docs" / "RUNTIME_STATE.md").write_text(
        "# Runtime State\n\nThis page lacks the v1.5 front sections.\n",
        encoding="utf-8",
    )
    (base / "docs" / "FEATURE_REGISTRY.md").write_text(
        "# Feature Registry\n\n| ID | Name | Status | Summary |\n"
        "|---|---|---|---|\n| ED-01 | Editing | done | ok |\n",
        encoding="utf-8",
    )
    boundary_sentence = (
        "production rights publishing public use acceptance "
        "承認 権利 公開 "
    )
    (base / "docs" / "EPISODE_REVIEW_WORKFLOW.md").write_text(
        "# Episode Review Workflow\n\n" + boundary_sentence * 4,
        encoding="utf-8",
    )
    (base / "docs" / "OPERATOR_REVIEW_UX.md").write_text(
        "# Operator Review UX\n\n## What This Is\nUX.\n\n## Current State\nReady.\n\n"
        "## Next\nUse it.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    (base / "docs" / "SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md").write_text(
        "# Subtitle Typography\n\n## What This Is\nCompare.\n\n## Current State\nReady.\n\n"
        "## Next\nReview.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    (base / "docs" / "REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md").write_text(
        "# Representative Review\n\n## What This Is\nReview.\n\n## Current State\nReady.\n\n"
        "## Next\nReview.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    (base / "artifacts" / "ARTIFACTS.md").write_text(
        "# Artifact Registry\n\n## `clip-test-artifact`\n",
        encoding="utf-8",
    )
