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
    assert status["current_focus"]["feature_id"] == "ED-10af"
    assert status["current_focus"]["artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert status["current_focus"][
        "source_render_path_selector_contract_artifact_id"
    ] == (
        "clip-ed10ae-render-path-selector-contract-probe-001"
    )
    assert status["current_focus"]["source_style_family_palette_artifact_id"] == (
        "clip-ed10ad-style-family-palette-axis-proof-001"
    )
    assert status["current_focus"]["source_visual_selector_artifact_id"] == (
        "clip-ed10ac-visual-selector-proof-001"
    )
    assert status["current_focus"]["source_selector_artifact_id"] == (
        "clip-ed10ab-subtitle-preset-selector-001"
    )
    assert status["current_focus"]["source_style_intent_artifact_id"] == (
        "clip-ed10aa-subtitle-style-intent-registry-001"
    )
    assert status["current_focus"]["source_render_path_artifact_id"] == (
        "clip-ed10z-tiny-render-path-nearer-probe-001"
    )
    assert status["current_focus"]["source_review_artifact_id"] == (
        "clip-ed10y-candidate2-carry-forward-001"
    )
    assert status["current_focus"]["source_previous_artifact_id"] == (
        "clip-ed10y-candidate2-carry-forward-001"
    )
    assert status["current_focus"]["source_comparison_artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert status["current_focus"]["source_proof_artifact_id"] == (
        "clip-ed10r-keifont-dense-stress-proof-001"
    )
    assert status["current_focus"]["state"] == (
        "l2_render_path_selector_probe_ready"
    )
    assert status["current_focus"][
        "source_render_contract_consumer_dry_read_artifact_id"
    ] == (
        "clip-ed10af-render-contract-consumer-dry-read-001"
    )
    assert status["current_focus"]["source_l2_selector_probe_artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert status["current_focus"]["lineage_observation_surface_artifact_id"] == (
        "clip-ed10ag-lineage-and-observation-surface-001"
    )
    assert status["current_focus"]["production_limitation_lift_entry_artifact_id"] == (
        "clip-ed10ah-production-limitation-lift-entry-001"
    )
    assert status["current_focus"][
        "render_readiness_separation_readback_artifact_id"
    ] == "clip-ed10ah-render-readiness-separation-readback-001"
    assert status["current_focus"][
        "final_render_path_readiness_packet_artifact_id"
    ] == "clip-ed10ai-final-render-path-readiness-packet-001"
    assert status["current_focus"]["human_visual_judgement"] == (
        "ed10w_candidate2_lead_freeform_review_consumed_then_ed10z_probe_completed"
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
        "ed10ai_final_render_path_readiness_packet_ready_active_ed10af_l2_preserved"
    )
    assert status["current_focus"]["user_action_type"] == (
        "NO_USER_ACTION_EXISTING_OUTPUT_READBACK_ONLY"
    )
    assert status["current_focus"]["next_review_action_type"] == (
        "NO_REVIEW_CARD_REVIEW_CONSUMED"
    )
    assert status["current_focus"]["current_visual_comparison_validity"] == (
        "valid_requested_keifont_visual_evidence"
    )
    assert status["current_focus"]["review_surface_direction"] == (
        "final_render_path_readiness_packet_no_review_card"
    )
    assert status["current_focus"]["font_visual_evidence_status"] == (
        "valid_requested_keifont_visual_evidence_on_current_windows_profile"
    )
    assert status["current_focus"]["multiline_wrap_evidence_status"] == (
        "passed_diagnostic_review"
    )
    assert status["current_focus"]["user_observation_consumed"]["status"] == (
        "display_acceptable_move_forward_no_layout_polish"
    )
    assert status["current_focus"]["user_observation_consumed"][
        "layout_polish_deferred"
    ] is True
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
    assert "production_limitation_lift" in status["current_focus"]["review_memory"][
        "next_nonredundant_axis"
    ]
    assert status["current_focus"]["review_memory"]["repeated_general_review"] is False
    assert status["current_focus"]["review_memory"][
        "same_candidate_comparison_review_allowed"
    ] is False
    assert status["current_focus"]["review_memory"]["current_blocker"] == (
        "none_for_final_render_path_readiness_packet"
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
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert status["current_focus"]["review_card"]["axis"] == (
        "final_render_path_readiness_packet"
    )
    assert status["current_focus"]["subtitle_preset_selector"]["artifact_id"] == (
        "clip-ed10ab-subtitle-preset-selector-001"
    )
    assert status["current_focus"]["subtitle_preset_selector"][
        "body_text_color_policy"
    ] == "stable_default_body_text"
    assert "shout_intensity_2" in status["current_focus"]["subtitle_preset_selector"][
        "example_ids"
    ]
    assert status["current_focus"]["subtitle_preset_selector"]["new_render_run"] is False
    assert status["current_focus"]["subtitle_visual_selector_proof"]["artifact_id"] == (
        "clip-ed10ac-visual-selector-proof-001"
    )
    assert status["current_focus"]["subtitle_visual_selector_proof"][
        "source_selector_artifact_id"
    ] == "clip-ed10ab-subtitle-preset-selector-001"
    assert status["current_focus"]["subtitle_visual_selector_proof"][
        "body_text_color_policy"
    ] == "stable_default_body_text"
    assert status["current_focus"]["subtitle_visual_selector_proof"][
        "existing_output_first_considered"
    ] is True
    assert status["current_focus"]["subtitle_visual_selector_proof"][
        "new_render_run"
    ] is False
    assert status["current_focus"]["subtitle_style_family_palette_axis_proof"][
        "artifact_id"
    ] == "clip-ed10ad-style-family-palette-axis-proof-001"
    assert status["current_focus"]["subtitle_style_family_palette_axis_proof"][
        "source_visual_selector_artifact_id"
    ] == "clip-ed10ac-visual-selector-proof-001"
    assert status["current_focus"]["subtitle_style_family_palette_axis_proof"][
        "body_text_color_policy"
    ] == "stable_default_body_text"
    assert status["current_focus"]["subtitle_style_family_palette_axis_proof"][
        "new_style_family_created"
    ] is False
    assert status["current_focus"]["subtitle_style_family_palette_axis_proof"][
        "new_palette_created"
    ] is False
    assert status["current_focus"]["subtitle_style_family_palette_axis_proof"][
        "new_render_run"
    ] is False
    assert status["current_focus"]["subtitle_render_path_selector_contract"][
        "artifact_id"
    ] == "clip-ed10ae-render-path-selector-contract-probe-001"
    assert status["current_focus"]["subtitle_render_path_selector_contract"][
        "source_style_family_palette_artifact_id"
    ] == "clip-ed10ad-style-family-palette-axis-proof-001"
    assert status["current_focus"]["subtitle_render_path_selector_contract"][
        "render_level"
    ] == "L0 No Render"
    assert "semantic_preset_id" in status["current_focus"][
        "subtitle_render_path_selector_contract"
    ]["semantic_fields"]
    assert "badge_color_token" in status["current_focus"][
        "subtitle_render_path_selector_contract"
    ]["color_surface_fields"]
    assert status["current_focus"]["subtitle_render_path_selector_contract"][
        "later_l2_render_path_probe_trigger"
    ] == "not_triggered_in_this_slice"
    assert status["current_focus"]["subtitle_render_path_selector_contract"][
        "new_render_run"
    ] is False
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "artifact_id"
    ] == "clip-ed10af-l2-render-path-selector-probe-001"
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "source_render_path_selector_contract_artifact_id"
    ] == "clip-ed10ae-render-path-selector-contract-probe-001"
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "metadata_json"
    ] == "docs/style_intent/subtitle-render-path-selector-probe.json"
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "doc"
    ] == "docs/style_intent/subtitle-render-path-selector-probe.md"
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "probe_kind"
    ] == "tiny_ffmpeg_libass_selector_probe_readback"
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "render_level"
    ] == "L2 tiny render path selector probe"
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "example_ids"
    ] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
    ]
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "selected_example_count"
    ] == 3
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "stable_body_text_preserved"
    ] is True
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "badge_accent_backplate_route_preserved"
    ] is True
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "safe_area_line_break_metadata_survived"
    ] is True
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "local_probe_status"
    ] == "local_ignored_probe_generated"
    assert "subtitle_render_path_selector_probe" in status["current_focus"][
        "subtitle_render_path_selector_probe"
    ]["local_outputs"]["video"]
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "new_render_run"
    ] is True
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "tracked_binary_artifact_created"
    ] is False
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "production_render_acceptance"
    ] is False
    assert status["current_focus"]["subtitle_render_path_selector_probe"][
        "public_use_permission"
    ] is False
    assert status["current_focus"]["subtitle_render_contract_consumer_dry_read"][
        "artifact_id"
    ] == (
        "clip-ed10af-render-contract-consumer-dry-read-001"
    )
    assert status["current_focus"]["subtitle_render_contract_consumer_dry_read"][
        "payload_count"
    ] == 6
    assert status["current_focus"]["subtitle_render_contract_consumer_dry_read"][
        "all_payloads_consumer_ready"
    ] is True
    lineage_surface = status["current_focus"][
        "subtitle_render_path_lineage_observation_surface"
    ]
    assert lineage_surface[
        "artifact_id"
    ] == "clip-ed10ag-lineage-and-observation-surface-001"
    assert lineage_surface["active_artifact_id"] == "clip-ed10af-l2-render-path-selector-probe-001"
    assert lineage_surface[
        "source_render_path_selector_probe_artifact_id"
    ] == "clip-ed10af-l2-render-path-selector-probe-001"
    assert lineage_surface[
        "source_render_contract_consumer_dry_read_artifact_id"
    ] == "clip-ed10af-render-contract-consumer-dry-read-001"
    assert lineage_surface["dry_read_source_commit"] == "7e96a28"
    assert lineage_surface["dry_read_invalidated"] is False
    assert lineage_surface["existing_output_first_reused"] is True
    assert lineage_surface["new_render_run"] is False
    assert lineage_surface["source_probe_new_render_run"] is True
    assert lineage_surface["same_machine_only"] is True
    assert lineage_surface["may_be_absent_on_other_clone"] is True
    assert lineage_surface["source_dry_read_payload_count"] == 6
    assert lineage_surface["selected_example_count"] == 3
    assert (
        "subtitle_render_path_selector_probe.mp4"
        in lineage_surface["local_outputs"]["video"]
    )
    assert (
        "subtitle_render_path_selector_probe_contact_sheet.jpg"
        in lineage_surface["local_outputs"]["contact_sheet"]
    )
    assert lineage_surface["production_render_acceptance"] is False
    assert lineage_surface["public_use_permission"] is False
    lift_entry = status["current_focus"]["subtitle_production_limitation_lift_entry"]
    assert lift_entry["artifact_id"] == (
        "clip-ed10ah-production-limitation-lift-entry-001"
    )
    assert lift_entry["active_diagnostic_proof_source_artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert lift_entry["support_lineage_observation_surface_artifact_id"] == (
        "clip-ed10ag-lineage-and-observation-surface-001"
    )
    assert lift_entry["dry_read_predecessor_artifact_id"] == (
        "clip-ed10af-render-contract-consumer-dry-read-001"
    )
    assert lift_entry["dry_read_source_commit"] == "7e96a28"
    assert lift_entry["gate_names"] == [
        "diagnostic_render_path_proof",
        "production_subtitle_design_acceptance",
        "production_render_acceptance",
        "creative_acceptance",
        "rights_status",
        "publishing_acceptance",
        "public_use_permission",
    ]
    assert lift_entry["diagnostic_render_path_proof"] == "available_diagnostic_only"
    assert lift_entry["production_subtitle_design_acceptance"] is False
    assert lift_entry["production_render_acceptance"] is False
    assert lift_entry["creative_acceptance"] is False
    assert lift_entry["rights_status"] == "pending"
    assert lift_entry["publishing_acceptance"] is False
    assert lift_entry["public_use_permission"] is False
    assert lift_entry["lineage_support_not_production_proof"] is True
    assert lift_entry["new_render_run"] is False
    assert lift_entry["tracked_binary_artifact_created"] is False
    assert lift_entry["episodes_tracked"] is False
    assert lift_entry["next_executable_route"] == "production-limitation-lift-stage-1"
    readiness = status["current_focus"]["subtitle_render_readiness_separation_readback"]
    assert readiness["artifact_id"] == (
        "clip-ed10ah-render-readiness-separation-readback-001"
    )
    assert readiness["source_l2_selector_probe_artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert readiness["source_lineage_observation_surface_artifact_id"] == (
        "clip-ed10ag-lineage-and-observation-surface-001"
    )
    assert readiness["source_production_limitation_lift_entry_artifact_id"] == (
        "clip-ed10ah-production-limitation-lift-entry-001"
    )
    assert readiness["new_render_run"] is False
    assert readiness["next_render_trigger"] == "later_explicit_milestone_only"
    assert readiness["production_readiness"] == "not_accepted"
    assert readiness["rights_public_use_readiness"] == "not_accepted"
    assert "production_render_acceptance" in readiness["does_not_prove"]
    final_packet = status["current_focus"]["subtitle_final_render_path_readiness_packet"]
    assert final_packet["artifact_id"] == (
        "clip-ed10ai-final-render-path-readiness-packet-001"
    )
    assert final_packet["source_production_limitation_lift_entry_artifact_id"] == (
        "clip-ed10ah-production-limitation-lift-entry-001"
    )
    assert final_packet["active_diagnostic_proof_source_artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert final_packet["support_lineage_observation_surface_artifact_id"] == (
        "clip-ed10ag-lineage-and-observation-surface-001"
    )
    assert final_packet["dry_read_predecessor_artifact_id"] == (
        "clip-ed10af-render-contract-consumer-dry-read-001"
    )
    assert final_packet["selector_semantic_style_contract_artifact_id"] == (
        "clip-ed10ab-subtitle-preset-selector-001"
    )
    assert final_packet["render_adapter_input_contract_artifact_id"] == (
        "clip-ed10ae-render-path-selector-contract-probe-001"
    )
    assert final_packet["readiness_matrix_row_ids"] == [
        "ed10ah_gate_separation_source",
        "diagnostic_proof_evidence",
        "selector_semantic_style_contract_evidence",
        "render_adapter_input_contract_evidence",
        "local_ignored_proof_media_evidence",
        "lineage_predecessor_evidence",
        "missing_production_subtitle_design_acceptance",
        "missing_production_render_acceptance",
        "missing_creative_acceptance",
        "missing_rights_publication_public_use_decisions",
    ]
    assert final_packet["diagnostic_proof"] == "available"
    assert final_packet["selector_semantic_contract"] == "available"
    assert final_packet["render_adapter_input_contract"] == "available"
    assert final_packet["local_ignored_proof_media"] == (
        "available_same_machine_diagnostic_only"
    )
    assert final_packet["lineage_predecessor"] == "available"
    assert final_packet["production_subtitle_design_acceptance"] is False
    assert final_packet["production_render_acceptance"] is False
    assert final_packet["creative_acceptance"] is False
    assert final_packet["rights_status"] == "pending"
    assert final_packet["publishing_acceptance"] is False
    assert final_packet["public_use_permission"] is False
    assert final_packet["agent_can_start_next_route_without_user_judgement"] is True
    assert final_packet["next_executable_route"] == "final-render-path-stage-1"
    assert final_packet["alternate_next_executable_route"] == (
        "production-limitation-lift-stage-1"
    )
    assert final_packet["new_render_run"] is False
    assert final_packet["tracked_binary_artifact_created"] is False
    assert final_packet["episodes_tracked"] is False
    assert status["current_focus"]["subtitle_style_intent_registry"][
        "body_text_color_policy"
    ] == "stable_by_default"
    assert "emotion" in status["current_focus"]["subtitle_style_intent_registry"][
        "axes"
    ]
    assert status["current_focus"]["review_surface_layout_debt"][
        "same_candidate_review_reopened"
    ] is False
    assert "cut_002 / cut_003 review" in status["current_focus"]["review_card"][
        "not_asking"
    ]
    assert status["current_focus"]["focused_review_html"] == (
        "episodes/.../subtitle_presentation_review_pack.html"
    )
    assert status["current_focus"]["review_debt"][0]["debt_id"] == (
        "production_limitation_lift"
    )
    assert status["current_focus"]["review_debt"][0]["status"] == (
        "final_readiness_packet_ready_stage_1_next"
    )
    assert status["current_focus"]["bounded_decoration_candidates"] == [
        "ed10w_current_pass_reference",
        "ed10w_lighter_outline_shadow_pressure",
        "ed10w_badge_label_pressure_adjustment",
        "ed10w_balanced_combined_low_risk",
    ]
    assert status["current_focus"]["candidate_delta_visibility"]["status"] == (
        "consumed_candidate2_probe_profile_ready_after_ed10y"
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
        "ed10z_actual_generation_available_requires_human_review_after_explicit_ffmpeg_ffprobe_paths"
    )
    assert status["current_focus"]["render_path_readiness"]["latest_actual_rerun"][
        "visual_proof_status"
    ] == "available_requires_human_review"
    assert status["current_focus"]["production_subtitle_design_acceptance"] is False
    assert status["current_focus"]["production_render_acceptance"] is False
    assert status["current_focus"]["production_usage_allowed"] is False
    assert [item["command"] for item in status["open_surfaces"]] == [
        ".\\open-dashboard.ps1",
        ".\\open-artifacts.ps1",
        "see docs\\style_intent\\subtitle-final-render-path-readiness.md",
        "see docs\\style_intent\\subtitle-production-limitation-lift-entry.md",
        "see docs\\style_intent\\subtitle-render-readiness-separation.md",
        "see docs\\style_intent\\subtitle-render-path-selector-probe.md",
        "see docs\\style_intent\\subtitle-render-path-lineage-observation-surface.md",
        "see docs\\style_intent\\subtitle-render-path-selector-contract.md",
        "see docs\\style_intent\\subtitle-style-family-palette-proof.html",
        "see docs\\style_intent\\subtitle-visual-selector-proof.html",
        "see docs\\style_intent\\subtitle-preset-selector.json",
        "see docs\\SUBTITLE_STYLE_INTENT_REGISTRY.md",
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
        "clip-ed10ai-final-render-path-readiness-packet-001"
    )
    assert status["next_review_items"][1]["artifact"] == (
        "clip-ed10ah-render-readiness-separation-readback-001"
    )
    assert status["next_review_items"][2]["artifact"] == (
        "clip-ed10ah-production-limitation-lift-entry-001"
    )
    assert status["next_review_items"][3]["artifact"] == (
        "clip-ed10ag-lineage-and-observation-surface-001"
    )
    assert status["next_review_items"][4]["artifact"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
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
        "docs/style_intent/subtitle-final-render-path-readiness.md"
    )
    assert persisted["open_surfaces"][3]["target"] == (
        "docs/style_intent/subtitle-production-limitation-lift-entry.md"
    )
    assert persisted["open_surfaces"][4]["target"] == (
        "docs/style_intent/subtitle-render-readiness-separation.md"
    )
    assert persisted["open_surfaces"][5]["target"] == (
        "docs/style_intent/subtitle-render-path-selector-probe.md"
    )
    assert persisted["open_surfaces"][6]["target"] == (
        "docs/style_intent/subtitle-render-path-lineage-observation-surface.md"
    )
    assert persisted["open_surfaces"][7]["target"] == (
        "docs/style_intent/subtitle-render-path-selector-contract.md"
    )
    assert persisted["open_surfaces"][8]["target"] == (
        "docs/style_intent/subtitle-style-family-palette-proof.html"
    )
    assert persisted["open_surfaces"][9]["target"] == (
        "docs/style_intent/subtitle-visual-selector-proof.html"
    )
    assert persisted["open_surfaces"][10]["target"] == (
        "docs/style_intent/subtitle-preset-selector.json"
    )
    assert persisted["open_surfaces"][11]["target"] == (
        "docs/SUBTITLE_STYLE_INTENT_REGISTRY.md"
    )
    assert persisted["open_surfaces"][12]["target"] == (
        "episodes/.../subtitle_presentation_review_pack.html"
    )
    assert "ED-10z local readback" in persisted["open_surfaces"][12][
        "when_to_use"
    ]
    assert "Open Surfaces" in html
    assert "subtitle_known_kirinuki_font_pack" in html
    assert "subtitle_kirinuki_font_audit" in html
    assert "Doc Health Findings" in html
    assert "Feature Progress" in html
    assert "Active Artifacts" in html
    assert "Next Review Items" in html
    assert "clip-ed10ai-final-render-path-readiness-packet-001" in html
    assert "clip-ed10ah-production-limitation-lift-entry-001" in html
    assert "clip-ed10ah-render-readiness-separation-readback-001" in html
    assert "clip-ed10r-keifont-dense-stress-proof-001" in html
    assert "clip-ed10z-tiny-render-path-nearer-probe-001" in html
    assert "clip-ed10aa-subtitle-style-intent-registry-001" in html
    assert "clip-ed10ab-subtitle-preset-selector-001" in html
    assert "clip-ed10ac-visual-selector-proof-001" in html
    assert "clip-ed10ad-style-family-palette-axis-proof-001" in html
    assert "clip-ed10ae-render-path-selector-contract-probe-001" in html
    assert "clip-ed10af-l2-render-path-selector-probe-001" in html
    assert "clip-ed10ag-lineage-and-observation-surface-001" in html
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


def test_subtitle_style_intent_registry_is_machine_readable():
    registry_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-style-intent-registry.json"
    )

    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    assert registry["artifact_id"] == "clip-ed10aa-subtitle-style-intent-registry-001"
    assert registry["active_normal_dialogue_lead"] == (
        "ed10w_badge_label_pressure_adjustment"
    )
    assert set(registry["axes"]) == {
        "speaker_id",
        "speaker_role",
        "emotion",
        "intensity",
        "utterance_role",
        "readability_priority",
    }
    assert registry["axes"]["emotion"]["values"] == [
        "neutral",
        "emphasis",
        "shout",
        "whisper",
        "ominous",
        "narration",
        "system_note",
    ]
    assert registry["body_text_color_policy"]["default"] == "stable"
    assert registry["agent_rule"][
        "semantic_tags_to_presets_without_numeric_review"
    ] is True
    assert "new_color_palette" in registry["agent_rule"][
        "human_review_required_for"
    ]
    assert "font_size" in registry["perceptual_impact"]["high"]
    assert "one_pixel_outline_delta" in registry["perceptual_impact"]["low"]
    assert registry["review_surface_layout_debt"][
        "not_a_new_review_request"
    ] is True
    assert registry["boundaries"]["broad_renderer_style_system_built"] is False
    assert registry["boundaries"]["production_render_acceptance"] is False


def test_subtitle_preset_selector_readback_is_machine_readable():
    selector_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-preset-selector.json"
    )

    selector = json.loads(selector_path.read_text(encoding="utf-8"))
    examples = {item["example_id"]: item for item in selector["examples"]}

    assert selector["artifact_id"] == "clip-ed10ab-subtitle-preset-selector-001"
    assert selector["source_registry_artifact_id"] == (
        "clip-ed10aa-subtitle-style-intent-registry-001"
    )
    assert selector["source_render_path_artifact_id"] == (
        "clip-ed10z-tiny-render-path-nearer-probe-001"
    )
    assert selector["input_axes"] == [
        "speaker_id",
        "speaker_role",
        "emotion",
        "intensity",
        "utterance_role",
        "readability_priority",
    ]
    assert "badge_color_token" in selector["output_style_tokens"]
    assert selector["selector_contract"]["deterministic"] is True
    assert selector["selector_contract"]["body_text_color_default"] == (
        "stable_default_body_text"
    )
    assert selector["selector_contract"]["character_color_first_surfaces"] == [
        "badge_color_token",
        "accent_color_token",
    ]
    assert selector["selector_contract"]["same_candidate_comparison_reopened"] is False
    assert examples["neutral_dialogue_intensity_0"]["style_tokens"][
        "body_text_color_changed"
    ] is False
    assert examples["shout_intensity_2"]["style_tokens"]["font_size_scale"] == 1.16
    assert examples["whisper_intensity_1"]["style_tokens"][
        "outline_shadow_strength"
    ] == "soft_readable"
    assert examples["ominous_intensity_2"]["style_tokens"][
        "safe_area_line_break_behavior"
    ] == "maximum_readability"
    assert examples["narration_intensity_0"]["style_tokens"][
        "font_family_role"
    ] == "narration_current_family_role"
    assert examples["system_note_intensity_0"]["style_tokens"][
        "badge_color_token"
    ] == "system_badge"
    assert selector["render_gate"]["new_render_run"] is False
    assert selector["boundaries"]["new_render_created"] is False
    assert selector["boundaries"]["production_subtitle_design_acceptance"] is False


def test_subtitle_visual_selector_proof_is_machine_readable():
    proof_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-visual-selector-proof.json"
    )

    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    examples = {item["example_id"]: item for item in proof["examples"]}

    assert proof["artifact_id"] == "clip-ed10ac-visual-selector-proof-001"
    assert proof["source_selector_artifact_id"] == (
        "clip-ed10ab-subtitle-preset-selector-001"
    )
    assert proof["status"] == "visual_selector_proof_ready"
    assert proof["proof_kind"] == "tracked_static_html_json_readback"
    assert proof["existing_output_first"]["considered"] is True
    assert proof["existing_output_first"]["new_render_run"] is False
    assert proof["body_text_color_policy"]["stable_across_examples"] is True
    assert proof["body_text_color_policy"]["changed_in_any_example"] is False
    assert proof["body_text_color_policy"]["character_color_first_surfaces"] == [
        "badge_color_token",
        "accent_color_token",
    ]
    assert proof["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert examples["shout_intensity_2"]["visual_sample"][
        "font_size_percent"
    ] == 116
    assert examples["whisper_intensity_1"]["readback_tokens"][
        "backplate_box_token"
    ] == "soft"
    assert examples["system_note_intensity_0"]["readback_tokens"][
        "body_text_color_token"
    ] == "stable_default_body_text"
    assert proof["review_policy"]["human_review_required"] is False
    assert proof["render_gate"]["new_render_run"] is False
    assert proof["boundaries"]["production_render_acceptance"] is False


def test_subtitle_style_family_palette_axis_proof_is_machine_readable():
    proof_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-style-family-palette-proof.json"
    )

    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    examples = {item["example_id"]: item for item in proof["examples"]}

    assert proof["artifact_id"] == "clip-ed10ad-style-family-palette-axis-proof-001"
    assert proof["source_visual_selector_artifact_id"] == (
        "clip-ed10ac-visual-selector-proof-001"
    )
    assert proof["status"] == "style_family_palette_axis_proof_ready"
    assert proof["proof_kind"] == "tracked_static_html_json_readback"
    assert proof["axis_contract"]["body_text_color_policy"] == (
        "stable_default_body_text"
    )
    assert proof["axis_contract"]["new_palette_created"] is False
    assert proof["axis_contract"]["new_style_family_created"] is False
    assert proof["axis_contract"]["character_color_first_surfaces"] == [
        "badge_color_token",
        "accent_color_token",
    ]
    assert proof["body_text_color_policy"]["stable_across_examples"] is True
    assert proof["body_text_color_policy"]["changed_in_any_example"] is False
    assert proof["existing_output_first"]["level"] == (
        "L0 No Render / Existing Output First"
    )
    assert proof["existing_output_first"]["new_render_run"] is False
    assert proof["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert examples["neutral_dialogue_intensity_0"]["family_group"] == (
        "dialogue_current_keifont_family"
    )
    assert examples["shout_intensity_2"]["palette_route"] == "high_energy_warm"
    assert examples["ominous_intensity_2"]["palette_route"] == "ominous_dark"
    assert examples["system_note_intensity_0"]["family_group"] == (
        "system_note_family"
    )
    assert {
        example["palette_surfaces"]["body_text_color_token"]
        for example in proof["examples"]
    } == {"stable_default_body_text"}
    assert proof["review_policy"]["human_review_required"] is False
    assert proof["review_policy"]["user_side_work"] == "none"
    assert proof["render_gate"]["new_render_run"] is False
    assert proof["boundaries"]["production_render_acceptance"] is False


def test_subtitle_render_path_selector_contract_is_machine_readable():
    contract_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-selector-contract.json"
    )

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    entries = {
        item["semantic_preset_id"]: item
        for item in contract["contract_entries"]
    }

    assert contract["artifact_id"] == (
        "clip-ed10ae-render-path-selector-contract-probe-001"
    )
    assert contract["source_style_family_palette_artifact_id"] == (
        "clip-ed10ad-style-family-palette-axis-proof-001"
    )
    assert contract["status"] == "render_path_selector_contract_ready"
    assert contract["contract_kind"] == "static_selector_to_render_path_readback"
    assert contract["render_level"] == "L0 No Render"
    assert "semantic_preset_id" in contract["render_adapter_input_contract"][
        "semantic_fields"
    ]
    assert "palette_route" in contract["render_adapter_input_contract"][
        "style_axis_fields"
    ]
    assert "body_text_color_token" in contract["render_adapter_input_contract"][
        "color_surface_fields"
    ]
    assert "safe_area_line_break_behavior" in contract[
        "render_adapter_input_contract"
    ]["motion_line_break_fields"]
    assert contract["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert entries["shout_intensity_2"]["render_adapter_input"]["style"][
        "family_id"
    ] == "emphasis_energy_family"
    assert entries["ominous_intensity_2"]["render_adapter_input"]["style"][
        "palette_route"
    ] == "ominous_dark"
    assert {
        entry["render_adapter_input"]["color_surfaces"]["body_text_color_token"]
        for entry in contract["contract_entries"]
    } == {"stable_default_body_text"}
    assert {
        entry["contract_assertions"]["render_artifact_created"]
        for entry in contract["contract_entries"]
    } == {False}
    assert contract["later_l2_render_path_probe_trigger"]["status"] == (
        "not_triggered_in_this_slice"
    )
    assert "HTML proof updates" in contract["later_l2_render_path_probe_trigger"][
        "not_triggered_by"
    ]
    assert contract["render_gate"]["new_render_run"] is False
    assert contract["readiness_separation"]["production_readiness"] == "not_accepted"
    assert contract["boundaries"]["production_render_acceptance"] is False


def test_subtitle_render_path_selector_probe_is_machine_readable():
    probe_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-selector-probe.json"
    )
    probe = json.loads(probe_path.read_text(encoding="utf-8"))

    assert probe["artifact_id"] == "clip-ed10af-l2-render-path-selector-probe-001"
    assert probe["source_render_path_selector_contract_artifact_id"] == (
        "clip-ed10ae-render-path-selector-contract-probe-001"
    )
    assert probe["status"] == "l2_render_path_selector_probe_ready"
    assert probe["probe_kind"] == "tiny_ffmpeg_libass_selector_probe_readback"
    assert probe["render_level"] == "L2 tiny render path selector probe"
    assert probe["selected_example_ids"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
    ]
    assert probe["selected_example_count"] == 3
    assert probe["validation"]["source_contract_referenced"] is True
    assert probe["validation"]["stable_body_text_preserved"] is True
    assert probe["validation"]["badge_accent_backplate_route_preserved"] is True
    assert probe["validation"]["safe_area_line_break_metadata_survived"] is True
    assert probe["validation"]["production_public_boundary_closed"] is True
    assert probe["validation"]["tracked_binary_artifact_created"] is False
    assert probe["validation"]["all_checks_passed"] is True
    assert {
        example["color_surfaces"]["body_text_color_token"]
        for example in probe["examples"]
    } == {"stable_default_body_text"}
    assert all(
        example["assertions"]["badge_accent_backplate_preserved"]
        for example in probe["examples"]
    )
    assert any(
        example["line_break"]["ass_text_contains_line_break"]
        for example in probe["examples"]
    )
    assert probe["local_probe"]["status"] == "local_ignored_probe_generated"
    assert "subtitle_render_path_selector_probe.ass" in probe["local_probe"]["outputs"]["ass"]
    assert "subtitle_render_path_selector_probe.mp4" in probe["local_probe"]["outputs"]["video"]
    assert probe["render_gate"]["new_render_run"] is True
    assert probe["render_gate"]["tracked_binary_artifact_created"] is False
    assert probe["boundaries"]["production_render_acceptance"] is False
    assert probe["boundaries"]["rights_status"] == "pending"
    assert probe["boundaries"]["public_use_permission"] is False
    assert probe["boundaries"]["tracked_binary_artifact_created"] is False
    assert probe["boundaries"]["episodes_tracked"] is False


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
    assert registry["ed10z_tiny_render_path_nearer_probe"]["feature_id"] == "ED-10z"
    assert registry["ed10z_tiny_render_path_nearer_probe"]["artifact_id"] == (
        "clip-ed10z-tiny-render-path-nearer-probe-001"
    )
    assert registry["ed10z_tiny_render_path_nearer_probe"]["proof_profile"] == (
        "ed10z_tiny_render_path_nearer_probe"
    )
    assert registry["ed10z_tiny_render_path_nearer_probe"][
        "source_previous_artifact_id"
    ] == "clip-ed10y-candidate2-carry-forward-001"
    assert registry["ed10z_tiny_render_path_nearer_probe"][
        "current_lead_candidate_id"
    ] == "ed10w_badge_label_pressure_adjustment"
    assert registry["ed10z_tiny_render_path_nearer_probe"][
        "fallback_reference_candidate_id"
    ] == "ed10w_current_pass_reference"
    assert registry["ed10z_tiny_render_path_nearer_probe"]["render_path_readiness"][
        "status"
    ] == "ed10z_tiny_render_path_nearer_probe_completed"
    assert registry["ed10z_tiny_render_path_nearer_probe"][
        "actual_materialization_status"
    ]["status"] == "blocked_environment_missing_ffprobe"
    assert registry["ed10z_tiny_render_path_nearer_probe"]["review_card"][
        "action_type"
    ] == "NO_REVIEW_CARD_REVIEW_CONSUMED"
    assert registry["ed10z_tiny_render_path_nearer_probe"][
        "production_render_acceptance"
    ] is False
    assert registry["ed10z_tiny_render_path_nearer_probe"][
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
    assert "Current ED-10z Tiny Render-Path-Nearer Probe" in text
    assert "Current ED-10ag Lineage and Observation Surface" in text
    assert "Current ED-10ah Production Limitation-Lift Entry" in text
    assert "Current ED-10ai Final Render-Path Readiness Packet" in text
    assert "clip-ed10z-tiny-render-path-nearer-probe-001" in text
    assert "clip-ed10w-subtitle-presentation-review-pack-001" in text
    assert "clip-ed10af-render-contract-consumer-dry-read-001" in text
    assert "clip-ed10af-l2-render-path-selector-probe-001" in text
    assert "clip-ed10ag-lineage-and-observation-surface-001" in text
    assert "clip-ed10ah-production-limitation-lift-entry-001" in text
    assert "clip-ed10ai-final-render-path-readiness-packet-001" in text
    assert "final-render-path-stage-1" in text
    assert "production-limitation-lift-stage-1" in text
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
        "隰・ｽｿ髫ｱ繝ｻ隶難ｽｩ陋ｻ・ｩ 陷茨ｽｬ鬮｢繝ｻ"
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


def test_docs_dashboard_current_focus_registration_uses_active_ed10af_artifact(
    tmp_path: Path,
):
    _write_fixture_docs(tmp_path)
    (tmp_path / "artifacts" / "ARTIFACTS.md").write_text(
        "# Artifact Registry\n\n"
        "## `clip-ed10r-keifont-dense-stress-proof-001`\n",
        encoding="utf-8",
    )

    status = build_project_status(base_dir=tmp_path, generated_at="test-run")

    assert status["current_focus"]["artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert (
        status["artifact_coverage"]["current_focus_artifact_registered"]
        is False
    )


def test_artifact_registry_records_ed10ah_limitation_lift_sources():
    status = build_project_status(base_dir=REPO_ROOT, generated_at="test-run")
    artifact_ids = set(status["artifact_summary"]["artifact_ids"])

    assert status["current_focus"]["artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert "clip-ed10af-l2-render-path-selector-probe-001" in artifact_ids
    assert "clip-ed10af-render-contract-consumer-dry-read-001" in artifact_ids
    assert "clip-ed10ag-lineage-and-observation-surface-001" in artifact_ids
    assert "clip-ed10ah-production-limitation-lift-entry-001" in artifact_ids
    assert "clip-ed10ah-render-readiness-separation-readback-001" in artifact_ids
    assert "clip-ed10ai-final-render-path-readiness-packet-001" in artifact_ids
    assert status["artifact_coverage"]["current_focus_artifact_registered"] is True
    lineage_surface = status["current_focus"][
        "subtitle_render_path_lineage_observation_surface"
    ]
    assert lineage_surface[
        "source_render_contract_consumer_dry_read_artifact_id"
    ] == "clip-ed10af-render-contract-consumer-dry-read-001"
    assert lineage_surface[
        "source_render_path_selector_probe_artifact_id"
    ] == "clip-ed10af-l2-render-path-selector-probe-001"
    assert lineage_surface["active_artifact_id"] == "clip-ed10af-l2-render-path-selector-probe-001"
    assert lineage_surface["dry_read_source_commit"] == "7e96a28"
    lift_entry = status["current_focus"]["subtitle_production_limitation_lift_entry"]
    assert lift_entry["artifact_id"] == (
        "clip-ed10ah-production-limitation-lift-entry-001"
    )
    assert lift_entry["active_diagnostic_proof_source_artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert lift_entry["support_lineage_observation_surface_artifact_id"] == (
        "clip-ed10ag-lineage-and-observation-surface-001"
    )
    assert lift_entry["dry_read_source_commit"] == "7e96a28"
    assert lift_entry["production_subtitle_design_acceptance"] is False
    assert lift_entry["production_render_acceptance"] is False
    assert lift_entry["creative_acceptance"] is False
    assert lift_entry["rights_status"] == "pending"
    assert lift_entry["publishing_acceptance"] is False
    assert lift_entry["public_use_permission"] is False
    assert lift_entry["lineage_support_not_production_proof"] is True
    readiness = status["current_focus"]["subtitle_render_readiness_separation_readback"]
    assert readiness["artifact_id"] == (
        "clip-ed10ah-render-readiness-separation-readback-001"
    )
    assert readiness["new_render_run"] is False
    assert readiness["episodes_tracked"] is False
    assert readiness["next_render_trigger"] == "later_explicit_milestone_only"
    final_packet = status["current_focus"]["subtitle_final_render_path_readiness_packet"]
    assert final_packet["artifact_id"] == (
        "clip-ed10ai-final-render-path-readiness-packet-001"
    )
    assert final_packet["source_production_limitation_lift_entry_artifact_id"] == (
        "clip-ed10ah-production-limitation-lift-entry-001"
    )
    assert final_packet["active_diagnostic_proof_source_artifact_id"] == (
        "clip-ed10af-l2-render-path-selector-probe-001"
    )
    assert final_packet["support_lineage_observation_surface_artifact_id"] == (
        "clip-ed10ag-lineage-and-observation-surface-001"
    )
    assert final_packet["dry_read_predecessor_artifact_id"] == (
        "clip-ed10af-render-contract-consumer-dry-read-001"
    )
    assert final_packet["readiness_matrix_row_ids"][0] == (
        "ed10ah_gate_separation_source"
    )
    assert final_packet["readiness_matrix_row_ids"][-1] == (
        "missing_rights_publication_public_use_decisions"
    )
    assert final_packet["diagnostic_proof"] == "available"
    assert final_packet["selector_semantic_contract"] == "available"
    assert final_packet["render_adapter_input_contract"] == "available"
    assert final_packet["local_ignored_proof_media"] == (
        "available_same_machine_diagnostic_only"
    )
    assert final_packet["production_subtitle_design_acceptance"] is False
    assert final_packet["production_render_acceptance"] is False
    assert final_packet["creative_acceptance"] is False
    assert final_packet["rights_status"] == "pending"
    assert final_packet["publishing_acceptance"] is False
    assert final_packet["public_use_permission"] is False
    assert final_packet["next_executable_route"] == "final-render-path-stage-1"
    assert final_packet["alternate_next_executable_route"] == (
        "production-limitation-lift-stage-1"
    )
    assert final_packet["new_render_run"] is False
    assert final_packet["tracked_binary_artifact_created"] is False
    assert final_packet["episodes_tracked"] is False
    assert status["current_focus"]["production_render_acceptance"] is False
    assert status["current_focus"]["public_use_permission"] is False
