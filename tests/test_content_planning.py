from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.content_planning import build_content_candidate_dashboard


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "samples" / "content_planning" / "content_candidates_fixture.json"


def test_content_candidate_dashboard_builds_json_and_html(tmp_path: Path):
    result = build_content_candidate_dashboard(
        fixture_path=FIXTURE,
        output_dir=tmp_path / "content_planning",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    candidates_path = result["candidates_path"]
    strategy_path = result["strategy_path"]
    dashboard_path = result["dashboard_path"]

    assert candidates_path.exists()
    assert strategy_path.exists()
    assert dashboard_path.exists()

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    strategies = json.loads(strategy_path.read_text(encoding="utf-8"))
    dashboard = dashboard_path.read_text(encoding="utf-8")

    assert candidates["schema_id"] == "clippipegen.content_planning_dashboard.v0"
    assert candidates["summary"]["candidate_count"] == 5
    assert candidates["summary"]["top_candidate_id"] == (
        "cpd01_bancho_marine_misunderstanding"
    )
    assert candidates["source"]["network_required"] is False
    assert candidates["gate_readback"]["media_downloaded"] is False
    assert candidates["gate_readback"]["production_candidate"] is False
    assert candidates["gate_readback"]["rights_status_counts"]["pending"] == 1
    assert candidates["candidates"][0]["score_total"] >= candidates["candidates"][1]["score_total"]
    assert candidates["candidates"][0]["score_components"]["risk_penalty"] < 0
    assert candidates["candidates"][0]["rights_readback"]["hard_gate"] is False

    assert strategies["summary"]["strategy_count"] == 3
    assert strategies["strategies"][0]["candidate_ids"]
    assert "production/public/publishing acceptance remains false" in (
        strategies["strategies"][0]["risk_readback_notes"]
    )
    assert "候補カード" in dashboard
    assert "チャンネル戦略カード" in dashboard
    assert "権利・ゲート readback" in dashboard
    assert "network_required=false" in dashboard


def test_build_content_candidate_dashboard_cli_writes_outputs(tmp_path: Path):
    output_dir = tmp_path / "docs" / "content_planning"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-content-candidate-dashboard",
            "--input",
            str(FIXTURE),
            "--output-dir",
            str(output_dir),
            "--generated-at",
            "test-run",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["artifact_id"] == "clip-cpd01-content-candidate-dashboard-v0-001"
    assert payload["candidate_count"] == 5
    assert payload["strategy_count"] == 3
    assert payload["network_required"] is False
    assert payload["media_downloaded"] is False
    assert payload["production_candidate"] is False
    assert (output_dir / "content_candidates.json").exists()
    assert (output_dir / "channel_strategy.json").exists()
    assert (output_dir / "content_dashboard.html").exists()
