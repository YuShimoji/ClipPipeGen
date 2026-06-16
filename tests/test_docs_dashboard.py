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
    assert status["current_focus"]["artifact_id"] == "clip-ed10g-noto-overlay-proof-001"
    assert status["current_focus"]["state"] == "diagnostic_base_accepted_next_route_needed"
    assert status["current_focus"]["human_visual_judgement"] == "accept_diagnostic_base"
    assert status["current_focus"]["production_subtitle_design_acceptance"] is False
    assert status["current_focus"]["production_render_acceptance"] is False
    assert status["current_focus"]["production_usage_allowed"] is False
    assert [item["command"] for item in status["open_surfaces"]] == [
        ".\\open-dashboard.ps1",
        ".\\open-artifacts.ps1",
        ".\\open-current-proof.ps1",
        ".\\open-font-candidates.ps1",
    ]
    assert status["doc_health"]["finding_total"] >= status["doc_health"]["finding_count"]
    assert status["doc_health"]["finding_limit"] == 50
    assert status["feature_summary"]["status_counts"]["done"] == 1
    assert status["features"][0]["id"] == "ED-01"
    assert status["features"][0]["progress_pct"] == 100
    assert status["artifact_coverage"]["registered_artifact_count"] == 1
    assert status["next_review_items"][0]["artifact"] == (
        "clip-ed10g-noto-overlay-proof-001"
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
    assert ".\\open-current-proof.ps1" in html
    assert "Doc Health Findings" in html
    assert "Feature Progress" in html
    assert "Active Artifacts" in html
    assert "Next Review Items" in html
    assert "clip-ed10g-noto-overlay-proof-001" in html
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
        "noto_sans_jp_clean_outline"
    )
    assert registry["font_size_policy"]["formula"] == "round(frame_height * 0.115)"
    assert registry["boundary_flags"]["font_binaries_downloaded"] is False
    assert registry["boundary_flags"]["production_candidate"] is False
    assert "noto_sans_jp_clean_outline" in candidate_ids
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
