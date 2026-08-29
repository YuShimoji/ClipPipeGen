from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from src.cli.serve_project_cockpit import (
    cockpit_payload,
    load_cockpit_snapshot,
    transition_review_ready,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    package = tmp_path / "episodes" / "candidate" / "package"
    package.mkdir(parents=True)
    media = package / "final_video.mp4"
    media.write_bytes(b"0" * 128)
    workflow_path = tmp_path / "docs" / "workflow.json"
    workflow_path.parent.mkdir(parents=True)
    workflow = {
        "status": "CONNECTED_READY_FOR_SERIALIZED_HUMAN_REVIEW",
        "autonomous_resolution": {
            "decision_units_resolved": 15,
            "item_level_questions_reemitted": 0,
            "decision_counts": {"KEEP": 7, "DROP": 1, "HOLD_REUSABLE": 7},
        },
        "human_judgment": {
            "count": 1,
            "artifact_id": "candidate-001",
            "item_level_fallback_allowed": False,
        },
    }
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")
    config_path = tmp_path / "docs" / "cockpit.json"
    config = {
        "schema_version": "clippipegen.project_cockpit.v1",
        "requirement_id": "REQ-1",
        "artifact_id": "cockpit-001",
        "title": "Current candidate",
        "workflow_receipt": {
            "path": "docs/workflow.json",
            "sha256": _sha256(workflow_path),
            "required_status": "CONNECTED_READY_FOR_SERIALIZED_HUMAN_REVIEW",
        },
        "candidate": {
            "artifact_id": "candidate-001",
            "package_root": "episodes/candidate/package",
            "media_name": "final_video.mp4",
            "sha256": _sha256(media),
            "byte_size": 128,
            "editorial_duration_seconds": 12.3,
            "container_duration_seconds": 12.3,
            "source_range_seconds": [1.0, 13.3],
        },
        "state_receipt": {
            "path": "episodes/candidate/review/cockpit_review_state_v1.json",
            "from": "WORKFLOW_CONNECTED",
            "to": "REVIEW_READY",
        },
        "review": {
            "resolved_decision_units": 15,
            "item_level_questions": 0,
            "remaining_human_judgment_count": 1,
            "question": "Accept whole or bounded revision?",
            "allowed_outcomes": [
                {"id": "accept_whole_candidate", "label": "Accept", "meaning": "internal only"},
                {"id": "bounded_revision", "label": "Revise", "meaning": "exact ranges"},
            ],
        },
        "boundaries": {
            "human_content_acceptance": "pending",
            "production_acceptance": False,
            "rights_approval": False,
            "publication_acceptance": False,
        },
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return tmp_path, config_path


def test_snapshot_and_payload_start_workflow_connected(tmp_path: Path) -> None:
    root, config_path = _fixture(tmp_path)
    snapshot = load_cockpit_snapshot(
        repo_root=root,
        config_path=config_path,
        duration_probe=lambda _path: 12.3,
    )
    payload = cockpit_payload(snapshot, review_url="http://127.0.0.1:8060/final_video.mp4")
    assert payload["project_state"] == "WORKFLOW_CONNECTED"
    assert payload["candidate"]["observed_byte_size"] == 128
    assert payload["workflow"]["resolved_decision_units"] == 15
    assert payload["workflow"]["item_level_questions_reemitted"] == 0


def test_transition_requires_actual_playback(tmp_path: Path) -> None:
    root, config_path = _fixture(tmp_path)
    snapshot = load_cockpit_snapshot(
        repo_root=root,
        config_path=config_path,
        duration_probe=lambda _path: 12.3,
    )
    with pytest.raises(ValueError, match="playback"):
        transition_review_ready(
            snapshot=snapshot,
            playback={"observed": False},
            review_url="http://127.0.0.1:8060/final_video.mp4",
            route_validator=lambda _url: {"http_status": 206, "bytes_read": 32},
        )
    assert not snapshot.state_path.exists()


def test_transition_writes_review_ready_without_acceptance(tmp_path: Path) -> None:
    root, config_path = _fixture(tmp_path)
    snapshot = load_cockpit_snapshot(
        repo_root=root,
        config_path=config_path,
        duration_probe=lambda _path: 12.3,
    )
    state = transition_review_ready(
        snapshot=snapshot,
        playback={"observed": True, "current_time_seconds": 1.25, "ready_state": 4},
        review_url="http://127.0.0.1:8060/final_video.mp4",
        route_validator=lambda _url: {"http_status": 206, "bytes_read": 32, "content_range": "bytes 0-31/128"},
    )
    assert state["status"] == "REVIEW_READY"
    assert state["human_judgment"]["status"] == "PENDING_NOT_SELECTED"
    assert state["human_judgment"]["selected_outcome"] is None
    assert state["boundaries"]["production_acceptance"] is False
    payload = cockpit_payload(snapshot, review_url="http://127.0.0.1:8060/final_video.mp4")
    assert payload["project_state"] == "REVIEW_READY"


def test_snapshot_rejects_reemitted_item_questions(tmp_path: Path) -> None:
    root, config_path = _fixture(tmp_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    workflow_path = root / config["workflow_receipt"]["path"]
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow["autonomous_resolution"]["item_level_questions_reemitted"] = 1
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")
    config["workflow_receipt"]["sha256"] = _sha256(workflow_path)
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="must not re-emit"):
        load_cockpit_snapshot(
            repo_root=root,
            config_path=config_path,
            duration_probe=lambda _path: 12.3,
        )


def test_snapshot_accepts_resolved_current_basis_without_reopening_items(
    tmp_path: Path,
) -> None:
    root, config_path = _fixture(tmp_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    workflow_path = root / config["workflow_receipt"]["path"]
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow["status"] = "CONNECTED_CURRENT_BASIS_ADOPTED"
    workflow["human_judgment"].update(
        {
            "remaining_count": 0,
            "status": "RESOLVED_ACCEPT_WHOLE_CANDIDATE",
            "selected_outcome": "accept_whole_candidate",
        }
    )
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")
    config["workflow_receipt"]["sha256"] = _sha256(workflow_path)
    config["workflow_receipt"]["required_status"] = workflow["status"]
    config["review"].update(
        {
            "remaining_human_judgment_count": 0,
            "status": "RESOLVED_ACCEPT_WHOLE_CANDIDATE",
            "selected_outcome": "accept_whole_candidate",
        }
    )
    config_path.write_text(json.dumps(config), encoding="utf-8")

    snapshot = load_cockpit_snapshot(
        repo_root=root,
        config_path=config_path,
        duration_probe=lambda _path: 12.3,
    )
    payload = cockpit_payload(
        snapshot, review_url="http://127.0.0.1:8060/final_video.mp4"
    )
    assert payload["workflow"]["status"] == "CONNECTED_CURRENT_BASIS_ADOPTED"
    assert payload["human_judgment"]["remaining_human_judgment_count"] == 0
    assert payload["human_judgment"]["selected_outcome"] == "accept_whole_candidate"


def test_static_surface_exposes_one_non_selecting_gate() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    html = (repo_root / "gui" / "project_cockpit" / "index.html").read_text(encoding="utf-8")
    script = (repo_root / "gui" / "project_cockpit" / "app.js").read_text(encoding="utf-8")
    assert "残る判断を1件に圧縮" in html
    assert "ここでは選びません" in html
    assert "payload.workflow.resolved_decision_units" in script
    assert "0 questions revived" in script
    assert "/api/review-ready" in script
    assert 'type="radio"' not in html
    assert "accept_whole_candidate" not in html
    assert '<video id="candidate-video" controls muted' in html
    assert "ui.video.volume = 0" in script
    assert "ui.video.pause()" in script
