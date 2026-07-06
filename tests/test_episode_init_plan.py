from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.episode_init_plan import (
    EpisodeInitPlanError,
    build_episode_init_plan,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CPD03_RESOLUTION = REPO_ROOT / "docs" / "content_planning" / "episode_seed_source_resolution.json"
CPD02_SEEDS = REPO_ROOT / "docs" / "content_planning" / "episode_seed_drafts.json"


def test_episode_init_plan_writes_dry_run_json_and_html(tmp_path: Path):
    result = build_episode_init_plan(
        input_path=CPD03_RESOLUTION,
        seed_input_path=CPD02_SEEDS,
        output_path=tmp_path / "episode_init_plan.json",
        dashboard_path=tmp_path / "episode_init_plan_dashboard.html",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    payload = json.loads(result["output_path"].read_text(encoding="utf-8"))
    html = result["dashboard_path"].read_text(encoding="utf-8")

    assert payload["schema_id"] == "clippipegen.episode_init_plan.v0"
    assert payload["summary"]["source_resolution_record_count"] == 5
    assert payload["summary"]["ready_dry_run_plan_count"] == 1
    assert payload["summary"]["skipped_unresolved_count"] == 4
    assert payload["summary"]["media_downloaded"] is False
    assert payload["summary"]["episode_dirs_created"] is False
    assert payload["gate_readback"]["dry_run"] is True
    assert payload["gate_readback"]["network_required"] is False
    assert payload["gate_readback"]["external_api_used"] is False
    assert payload["gate_readback"]["media_downloaded"] is False
    assert payload["gate_readback"]["episode_dirs_created"] is False
    assert payload["gate_readback"]["rights_manifest_created"] is False
    assert payload["gate_readback"]["material_ledger_created"] is False
    assert payload["gate_readback"]["fetch_receipt_created"] is False
    assert payload["gate_readback"]["transcript_generated"] is False
    assert payload["gate_readback"]["edit_pack_created"] is False
    assert payload["gate_readback"]["thumbnail_generated"] is False
    assert payload["gate_readback"]["rights_approved"] is False
    assert payload["gate_readback"]["production_ready"] is False
    assert payload["gate_readback"]["public_ready"] is False

    plan = payload["episode_init_plans"][0]
    assert plan["source_resolution_id"] == (
        "source_resolution_seed_cpd01_bancho_marine_misunderstanding"
    )
    assert plan["seed_id"] == "seed_cpd01_bancho_marine_misunderstanding"
    assert plan["candidate_id"] == "cpd01_bancho_marine_misunderstanding"
    assert plan["dry_run"] is True
    assert plan["ready_for_real_init"] is True
    assert plan["source_url_state"] == "present"
    assert plan["source_media_state"] == "not_fetched"
    assert plan["transcript_state"] == "not_generated"
    assert plan["material_ledger_state"] == "planned_only"
    assert plan["edit_pack_state"] == "planned_only"
    assert plan["thumbnail_state"] == "planned_only"
    assert plan["approved"] is False
    assert plan["public_ready"] is False
    assert plan["production_ready"] is False
    assert plan["video_id"] == "7J5aS_pcBj4"
    assert plan["planned_episode_slug"] == "ep_seed_cpd01_bancho_marine_misunderstanding"
    assert plan["planned_episode_root"] == (
        "episodes/ep_seed_cpd01_bancho_marine_misunderstanding"
    )
    assert plan["planned_artifacts"]["rights_manifest_path"].endswith("/rights_manifest.json")
    assert plan["planned_artifacts"]["source_receipt_path"].endswith(
        "/materials/src_video/fetch_receipt.json"
    )
    assert plan["planned_artifacts"]["material_ledger_path"].endswith("/material_ledger.json")
    assert plan["planned_artifacts"]["transcript_path"].endswith("/transcript.json")
    assert plan["planned_artifacts"]["edit_pack_path"].endswith("/edit_pack.json")
    assert plan["planned_artifacts"]["thumbnail_brief_path"].endswith("/thumbnail_brief.json")
    assert plan["source_inspection_plan"]["future_lane_needed"] == (
        "source_inspection_then_asset_fetch"
    )
    assert all(
        command.startswith("DO_NOT_RUN_NOW:")
        for command in plan["source_inspection_plan"]["future_commands_data_only"]
    )
    assert plan["proposed_clip_scope"]["available"] is True
    assert "番長が船長" in plan["proposed_clip_scope"]["clip_angle"]
    assert plan["rights_readback"]["status"] == "pending"
    assert plan["rights_readback"]["approved"] is False
    assert plan["gates"]["public_upload_forbidden_now"] is True
    assert plan["next_action"] == "ready_for_operator_source_inspection"

    skipped = payload["skipped_source_records"]
    assert len(skipped) == 4
    assert all(item["ready_for_real_init"] is False for item in skipped)
    assert all(item["source_url_state"] == "missing" for item in skipped)
    assert {item["next_action"] for item in skipped} == {"add_source_url"}

    assert "CPD-04 Init Episode Dry-Run Plan v0" in html
    assert "Episode計画ID" in html
    assert "予定episode slug" in html
    assert "media_downloaded</th><td>false" in html
    assert "episode_dirs_created</th><td>false" in html
    assert "rights_manifest=false" in html

    assert not (tmp_path / "episodes").exists()


def test_episode_init_plan_handles_no_ready_records(tmp_path: Path):
    source_path = tmp_path / "source_resolution.json"
    source_path.write_text(
        json.dumps(
            {
                "schema_id": "clippipegen.source_metadata_resolver.v0",
                "artifact_id": "test-source-resolution",
                "source_resolution_records": [
                    {
                        "resolution_id": "source_resolution_missing",
                        "seed_id": "seed_missing",
                        "candidate_id": "candidate_missing",
                        "working_title": "missing source",
                        "source_url": "",
                        "source_url_state": "missing",
                        "source_metadata_state": "unresolved_missing_source_url",
                        "source_media_state": "not_fetched",
                        "blocking_reason": "source_url is missing",
                        "manual_intake_required": True,
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = build_episode_init_plan(
        input_path=source_path,
        seed_input_path=None,
        output_path=tmp_path / "episode_init_plan.json",
        dashboard_path=tmp_path / "episode_init_plan_dashboard.html",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    payload = result["payload"]
    assert payload["summary"]["health"] == "blocked_by_no_resolved_source"
    assert payload["summary"]["ready_dry_run_plan_count"] == 0
    assert payload["summary"]["skipped_unresolved_count"] == 1
    assert payload["episode_init_plans"] == []
    assert payload["skipped_source_records"][0]["next_action"] == "add_source_url"
    assert payload["gate_readback"]["media_downloaded"] is False
    assert payload["gate_readback"]["episode_dirs_created"] is False


def test_episode_init_plan_rejects_missing_source_records(tmp_path: Path):
    bad_input = tmp_path / "bad.json"
    bad_input.write_text('{"schema_id":"bad"}', encoding="utf-8")

    with pytest.raises(EpisodeInitPlanError, match="source_resolution_records"):
        build_episode_init_plan(
            input_path=bad_input,
            seed_input_path=None,
            output_path=tmp_path / "episode_init_plan.json",
            dashboard_path=tmp_path / "episode_init_plan_dashboard.html",
            base_dir=REPO_ROOT,
            generated_at="test-run",
        )


def test_build_episode_init_plan_cli_writes_outputs(tmp_path: Path):
    output_path = tmp_path / "episode_init_plan.json"
    dashboard_path = tmp_path / "episode_init_plan_dashboard.html"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-episode-init-plan",
            "--input",
            str(CPD03_RESOLUTION),
            "--seed-input",
            str(CPD02_SEEDS),
            "--output",
            str(output_path),
            "--dashboard",
            str(dashboard_path),
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
    assert payload["artifact_id"] == "clip-cpd04-init-episode-dry-run-plan-v0-001"
    assert payload["source_resolution_record_count"] == 5
    assert payload["ready_dry_run_plan_count"] == 1
    assert payload["skipped_unresolved_count"] == 4
    assert payload["dry_run"] is True
    assert payload["network_required"] is False
    assert payload["external_api_used"] is False
    assert payload["media_downloaded"] is False
    assert payload["episode_dirs_created"] is False
    assert payload["rights_approved"] is False
    assert payload["production_ready"] is False
    assert payload["public_ready"] is False
    assert output_path.exists()
    assert dashboard_path.exists()
