from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.episode_seed_bridge import (
    EpisodeSeedBridgeError,
    build_episode_seed_drafts,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CPD01_CANDIDATES = REPO_ROOT / "docs" / "content_planning" / "content_candidates.json"


def test_episode_seed_bridge_writes_non_fetching_draft_json_and_html(tmp_path: Path):
    result = build_episode_seed_drafts(
        input_path=CPD01_CANDIDATES,
        output_path=tmp_path / "episode_seed_drafts.json",
        dashboard_path=tmp_path / "episode_seed_dashboard.html",
        base_dir=REPO_ROOT,
        generated_at="test-run",
        limit=3,
    )

    output_path = result["output_path"]
    dashboard_path = result["dashboard_path"]
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    html = dashboard_path.read_text(encoding="utf-8")

    assert payload["schema_id"] == "clippipegen.episode_seed_bridge.v0"
    assert payload["summary"]["seed_count"] == 3
    assert payload["summary"]["top_seed_id"] == (
        "seed_cpd01_bancho_marine_misunderstanding"
    )
    assert payload["gate_readback"]["media_downloaded"] is False
    assert payload["gate_readback"]["episode_dirs_created"] is False
    assert payload["gate_readback"]["production_candidate"] is False
    assert payload["gate_readback"]["public_use_permission"] is False

    top = payload["episode_seed_drafts"][0]
    assert top["candidate_id"] == "cpd01_bancho_marine_misunderstanding"
    assert top["status"] == "draft"
    assert top["source_media_state"] == "not_fetched"
    assert top["transcript_state"] == "needed"
    assert top["rights_readback"]["approved"] is False
    assert top["approval_state"]["seed_approved"] is False
    assert top["approval_state"]["source_fetched"] is False
    assert top["later_artifact_paths"]["rights_manifest"].endswith("/rights_manifest.json")
    assert top["output_plan"]["creates_episode_dir_now"] is False
    assert top["thumbnail_brief_seed"]["not_image_generation"] is True
    assert "confirm source URL/ref" in top["source_inspection_checklist"][0]

    assert "CPD-02 Candidate-to-Episode Seed Bridge v0" in html
    assert "候補ID" in html
    assert "取得状態" in html
    assert "権利readback" in html
    assert "media_downloaded</th><td>false" in html


def test_episode_seed_bridge_filters_by_candidate_id(tmp_path: Path):
    result = build_episode_seed_drafts(
        input_path=CPD01_CANDIDATES,
        output_path=tmp_path / "episode_seed_drafts.json",
        dashboard_path=tmp_path / "episode_seed_dashboard.html",
        base_dir=REPO_ROOT,
        generated_at="test-run",
        candidate_ids=["cpd01_song_moment_hold"],
    )

    payload = result["payload"]
    assert payload["summary"]["seed_count"] == 1
    seed = payload["episode_seed_drafts"][0]
    assert seed["candidate_id"] == "cpd01_song_moment_hold"
    assert seed["next_action"] == "reject"
    assert seed["source_media_state"] == "not_fetched"


def test_episode_seed_bridge_rejects_missing_candidate(tmp_path: Path):
    with pytest.raises(EpisodeSeedBridgeError, match="candidate_id not found"):
        build_episode_seed_drafts(
            input_path=CPD01_CANDIDATES,
            output_path=tmp_path / "episode_seed_drafts.json",
            dashboard_path=tmp_path / "episode_seed_dashboard.html",
            base_dir=REPO_ROOT,
            generated_at="test-run",
            candidate_ids=["missing"],
        )


def test_build_episode_seed_drafts_cli_writes_outputs(tmp_path: Path):
    output_path = tmp_path / "episode_seed_drafts.json"
    dashboard_path = tmp_path / "episode_seed_dashboard.html"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-episode-seed-drafts",
            "--input",
            str(CPD01_CANDIDATES),
            "--output",
            str(output_path),
            "--dashboard",
            str(dashboard_path),
            "--limit",
            "2",
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
    assert payload["artifact_id"] == "clip-cpd02-candidate-to-episode-seed-bridge-v0-001"
    assert payload["seed_count"] == 2
    assert payload["media_downloaded"] is False
    assert payload["episode_dirs_created"] is False
    assert payload["production_candidate"] is False
    assert output_path.exists()
    assert dashboard_path.exists()
