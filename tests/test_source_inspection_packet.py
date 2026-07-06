from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.source_inspection_packet import (
    DECISION_OPTIONS,
    SourceInspectionPacketError,
    build_source_inspection_packet,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CPD04_INIT_PLAN = REPO_ROOT / "docs" / "content_planning" / "episode_init_plan.json"


def test_source_inspection_packet_writes_json_dashboard_and_template(tmp_path: Path):
    result = build_source_inspection_packet(
        input_path=CPD04_INIT_PLAN,
        output_path=tmp_path / "source_inspection_packet.json",
        dashboard_path=tmp_path / "source_inspection_packet_dashboard.html",
        decision_template_path=tmp_path / "source_inspection_decisions.template.json",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    payload = json.loads(result["output_path"].read_text(encoding="utf-8"))
    template = json.loads(result["decision_template_path"].read_text(encoding="utf-8"))
    html = result["dashboard_path"].read_text(encoding="utf-8")

    assert payload["schema_id"] == "clippipegen.source_inspection_packet.v0"
    assert payload["summary"]["episode_init_plan_count"] == 1
    assert payload["summary"]["inspectable_packet_count"] == 1
    assert payload["summary"]["blocked_skipped_count"] == 4
    assert payload["summary"]["decision_template_entry_count"] == 1
    assert payload["summary"]["source_url_present_count"] == 1
    assert payload["summary"]["source_url_missing_count"] == 4
    assert payload["summary"]["source_url_invalid_count"] == 0
    assert payload["summary"]["fetch_authorized_count"] == 0
    assert payload["summary"]["media_downloaded"] is False
    assert payload["summary"]["episode_dirs_created"] is False
    assert payload["summary"]["health"] == "ready"
    assert payload["gate_readback"]["dry_run"] is True
    assert payload["gate_readback"]["source_opened_by_worker"] is False
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
    assert payload["gate_readback"]["fetch_authorized"] is False
    assert payload["gate_readback"]["rights_approved"] is False
    assert payload["gate_readback"]["production_ready"] is False
    assert payload["gate_readback"]["public_ready"] is False

    packet = payload["source_inspection_packets"][0]
    assert packet["inspection_packet_id"] == (
        "source_inspection_packet_ep_seed_cpd01_bancho_marine_misunderstanding"
    )
    assert packet["episode_plan_id"] == (
        "episode_init_plan_ep_seed_cpd01_bancho_marine_misunderstanding"
    )
    assert packet["source_resolution_id"] == (
        "source_resolution_seed_cpd01_bancho_marine_misunderstanding"
    )
    assert packet["seed_id"] == "seed_cpd01_bancho_marine_misunderstanding"
    assert packet["candidate_id"] == "cpd01_bancho_marine_misunderstanding"
    assert packet["source_url"] == "https://www.youtube.com/watch?v=7J5aS_pcBj4"
    assert packet["video_id"] == "7J5aS_pcBj4"
    assert packet["source_url_state"] == "present"
    assert packet["dry_run"] is True
    assert packet["source_media_state"] == "not_fetched"
    assert packet["source_open_state"] == "not_opened_by_worker"
    assert packet["inspection_state"] == "pending_operator_review"
    assert packet["decision_state"] == "pending"
    assert packet["fetch_authorized"] is False
    assert packet["rights_readback"]["status"] == "pending"
    assert packet["rights_readback"]["approved"] is False
    assert packet["rights_approved"] is False
    assert packet["public_ready"] is False
    assert packet["production_ready"] is False
    assert packet["proposed_clip_scope"]["available"] is True
    assert packet["decision_options"] == DECISION_OPTIONS
    assert packet["next_action"] == "operator_open_source_url"
    assert [item["label"] for item in packet["operator_checklist"]] == [
        "source page exists / availability",
        "title/channel appears consistent",
        "content appears relevant to clip_angle",
        "obvious risk flags",
        "whether future private/local fetch should be authorized",
    ]
    assert all(item["state"] == "unchecked" for item in packet["operator_checklist"])
    assert all(item["source_opened_by_worker"] is False for item in packet["operator_checklist"])

    assert len(payload["blocked_source_records"]) == 4
    assert all(item["ready_for_source_inspection"] is False for item in payload["blocked_source_records"])
    assert {item["next_action"] for item in payload["blocked_source_records"]} == {"add_source_url"}

    assert template["schema_id"] == "clippipegen.source_inspection_decisions.template.v0"
    assert template["entry_count"] == 1
    assert template["allowed_decisions"] == DECISION_OPTIONS
    entry = template["entries"][0]
    assert entry["inspection_packet_id"] == packet["inspection_packet_id"]
    assert entry["episode_plan_id"] == packet["episode_plan_id"]
    assert entry["seed_id"] == packet["seed_id"]
    assert entry["candidate_id"] == packet["candidate_id"]
    assert entry["source_url_reviewed"] is False
    assert entry["source_available"] is None
    assert entry["title_channel_match"] is None
    assert entry["clip_relevance"] is None
    assert entry["risk_notes"] == []
    assert entry["decision"] == "pending"
    assert entry["approve_future_private_fetch"] is False
    assert entry["reviewer_notes"] == []
    assert entry["reviewed_at"] == ""
    assert entry["boundary_flags_confirmed"]["fetch_authorized"] is False
    assert entry["boundary_flags_confirmed"]["rights_approved"] is False
    assert entry["boundary_flags_confirmed"]["production_ready"] is False
    assert entry["boundary_flags_confirmed"]["public_ready"] is False

    assert "CPD-05 Source Inspection Packet v0" in html
    assert "Inspection Packet ID" in html
    assert "source page exists / availability" in html
    assert "fetch_authorized=false" in html
    assert "rights_approved=false" in html

    assert not (tmp_path / "episodes").exists()


def test_source_inspection_packet_handles_no_ready_plans(tmp_path: Path):
    source_path = tmp_path / "episode_init_plan.json"
    source_path.write_text(
        json.dumps(
            {
                "schema_id": "clippipegen.episode_init_plan.v0",
                "artifact_id": "test-init-plan",
                "episode_init_plans": [
                    {
                        "episode_plan_id": "episode_init_plan_not_ready",
                        "seed_id": "seed_not_ready",
                        "candidate_id": "candidate_not_ready",
                        "working_title": "not ready source",
                        "planned_episode_slug": "ep_not_ready",
                        "source_url": "",
                        "source_url_state": "missing",
                        "ready_for_real_init": False,
                        "blocked_reason": "source_url is missing",
                    }
                ],
                "skipped_source_records": [
                    {
                        "source_resolution_id": "source_resolution_missing",
                        "seed_id": "seed_missing",
                        "candidate_id": "candidate_missing",
                        "working_title": "missing source",
                        "source_url": "",
                        "source_url_state": "missing",
                        "source_media_state": "not_fetched",
                        "blocking_reason": "source_url is missing",
                        "next_action": "add_source_url",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = build_source_inspection_packet(
        input_path=source_path,
        output_path=tmp_path / "source_inspection_packet.json",
        dashboard_path=tmp_path / "source_inspection_packet_dashboard.html",
        decision_template_path=tmp_path / "source_inspection_decisions.template.json",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    payload = result["payload"]
    template = result["decision_template"]
    assert payload["summary"]["health"] == "blocked_by_no_ready_episode_plan"
    assert payload["summary"]["episode_init_plan_count"] == 1
    assert payload["summary"]["inspectable_packet_count"] == 0
    assert payload["summary"]["blocked_skipped_count"] == 2
    assert payload["summary"]["source_url_missing_count"] == 2
    assert payload["source_inspection_packets"] == []
    assert all(item["ready_for_source_inspection"] is False for item in payload["blocked_source_records"])
    assert payload["gate_readback"]["fetch_authorized"] is False
    assert payload["gate_readback"]["media_downloaded"] is False
    assert payload["gate_readback"]["episode_dirs_created"] is False
    assert template["entry_count"] == 0
    assert template["entries"] == []


def test_source_inspection_packet_rejects_missing_episode_init_plans(tmp_path: Path):
    bad_input = tmp_path / "bad.json"
    bad_input.write_text('{"schema_id":"bad"}', encoding="utf-8")

    with pytest.raises(SourceInspectionPacketError, match="episode_init_plans"):
        build_source_inspection_packet(
            input_path=bad_input,
            output_path=tmp_path / "source_inspection_packet.json",
            dashboard_path=tmp_path / "source_inspection_packet_dashboard.html",
            decision_template_path=tmp_path / "source_inspection_decisions.template.json",
            base_dir=REPO_ROOT,
            generated_at="test-run",
        )


def test_build_source_inspection_packet_cli_writes_outputs(tmp_path: Path):
    output_path = tmp_path / "source_inspection_packet.json"
    dashboard_path = tmp_path / "source_inspection_packet_dashboard.html"
    template_path = tmp_path / "source_inspection_decisions.template.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-source-inspection-packet",
            "--input",
            str(CPD04_INIT_PLAN),
            "--output",
            str(output_path),
            "--dashboard",
            str(dashboard_path),
            "--decision-template",
            str(template_path),
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
    assert payload["artifact_id"] == "clip-cpd05-source-inspection-packet-v0-001"
    assert payload["episode_init_plan_count"] == 1
    assert payload["inspectable_packet_count"] == 1
    assert payload["blocked_skipped_count"] == 4
    assert payload["decision_template_entry_count"] == 1
    assert payload["dry_run"] is True
    assert payload["source_opened_by_worker"] is False
    assert payload["network_required"] is False
    assert payload["external_api_used"] is False
    assert payload["media_downloaded"] is False
    assert payload["episode_dirs_created"] is False
    assert payload["fetch_authorized"] is False
    assert payload["rights_approved"] is False
    assert payload["production_ready"] is False
    assert payload["public_ready"] is False
    assert output_path.exists()
    assert dashboard_path.exists()
    assert template_path.exists()
