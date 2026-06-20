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
    assert status["current_focus"]["feature_id"] == "ED-10o"
    assert status["current_focus"]["artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert status["current_focus"]["source_comparison_artifact_id"] == (
        "clip-ed10l-known-kirinuki-font-pack-001"
    )
    assert status["current_focus"]["source_proof_artifact_id"] == (
        "clip-ed10n-keifont-overlay-proof-001"
    )
    assert status["current_focus"]["state"] == (
        "ed10o_multifont_focused_review_ready"
    )
    assert status["current_focus"]["human_visual_judgement"] == (
        "ed10k_biz_freeform_review_consumed_not_accepted"
    )
    assert status["current_focus"]["selected_typography_base"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert status["current_focus"]["selected_source_license_install_route"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert status["current_focus"]["route_status"] == (
        "one_shot_multifont_focused_review_surface_ready"
    )
    assert status["current_focus"]["current_visual_comparison_validity"] == (
        "valid_requested_font_visual_evidence_after_per_user_font_readback"
    )
    assert status["current_focus"]["production_subtitle_design_acceptance"] is False
    assert status["current_focus"]["production_render_acceptance"] is False
    assert status["current_focus"]["production_usage_allowed"] is False
    assert [item["command"] for item in status["open_surfaces"]] == [
        ".\\open-dashboard.ps1",
        ".\\open-artifacts.ps1",
        (
            "powershell -ExecutionPolicy Bypass -File "
            "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
            "jp_pilot01r3_cut_review\\subtitle_multifont_focused_review\\"
            "open_comparison.ps1"
        ),
        ".\\open-current-proof.ps1",
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
        "clip-ed10o-multifont-focused-review-001"
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
    assert "Open Surfaces" in html
    assert "subtitle_known_kirinuki_font_pack" in html
    assert "subtitle_kirinuki_font_audit" in html
    assert "Doc Health Findings" in html
    assert "Feature Progress" in html
    assert "Active Artifacts" in html
    assert "Next Review Items" in html
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
