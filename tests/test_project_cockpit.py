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
    readback_path = tmp_path / "docs" / "readback.json"
    readback = {
        "status": "CONNECTED_NONBLOCKING_PARTIAL_OBSERVATION",
        "artifact": {"artifact_id": "candidate-001", "sha256": _sha256(media)},
        "decision_path": {"item_level_questions_reemitted": 0},
        "legacy_gate": {"blocks_workflow": False, "mandatory_human_judgment_count": 0},
    }
    readback_path.write_text(json.dumps(readback), encoding="utf-8")
    navigation_path = tmp_path / "docs" / "navigation.json"
    navigation = {
        "calibration_scope": {"artifact_identity": "candidate-001", "output_sha256": _sha256(media)},
        "decision_units": [
            {
                "unit_id": f"unit_{index + 1:03d}",
                "content_label": f"Section {index + 1}",
                "output_range_seconds": [index * 1.5, (index + 1) * 1.5 if index < 7 else 12.3],
            }
            for index in range(8)
        ],
    }
    navigation_path.write_text(json.dumps(navigation), encoding="utf-8")
    rejection_path = tmp_path / "docs" / "rejection.json"
    rejection = {
        "status": "REJECTED_LEGACY_TASK_SETTING",
        "artifact": {"sha256": _sha256(media)},
    }
    rejection_path.write_text(json.dumps(rejection), encoding="utf-8")
    task_board_path = tmp_path / "docs" / "task_board.json"
    task_board = {
        "status": "ACTIVE_TEMPORARY_PROJECT_WORK_SURFACE",
        "artifact_id": "task-board-001",
        "tasks": [
            {"task_id": f"ED-13R-{index:02d}", "title": f"Task {index}", "status": "planned", "work": "work"}
            for index in range(1, 11)
        ],
    }
    task_board_path.write_text(json.dumps(task_board), encoding="utf-8")
    config_path = tmp_path / "docs" / "cockpit.json"
    config = {
        "schema_version": "clippipegen.project_cockpit.v2",
        "requirement_id": "REQ-1",
        "artifact_id": "cockpit-001",
        "title": "Current candidate",
        "workflow_receipt": {
            "path": "docs/workflow.json",
            "sha256": _sha256(workflow_path),
            "required_status": "CONNECTED_READY_FOR_SERIALIZED_HUMAN_REVIEW",
        },
        "workflow_readback": {
            "path": "docs/readback.json",
            "sha256": _sha256(readback_path),
            "required_status": "CONNECTED_NONBLOCKING_PARTIAL_OBSERVATION",
        },
        "navigation_calibration": {
            "path": "docs/navigation.json",
            "sha256": _sha256(navigation_path),
            "unit_count": 8,
        },
        "legacy_task_rejection": {
            "path": "docs/rejection.json",
            "sha256": _sha256(rejection_path),
        },
        "task_board": {
            "path": "docs/task_board.json",
            "sha256": _sha256(task_board_path),
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
        "observation_mode": {
            "status": "OPTIONAL_PARTIAL_OBSERVATION",
            "whole_acceptance_requested": False,
            "whole_rejection_requested": False,
            "mandatory_item_questions": 0,
        },
        "boundaries": {
            "human_content_acceptance": "not_requested_at_this_stage",
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
    assert payload["project_state"] == "TASK_BOARD_ACTIVE"
    assert payload["candidate"]["observed_byte_size"] == 128
    assert payload["workflow"]["resolved_decision_units"] == 15
    assert payload["workflow"]["item_level_questions_reemitted"] == 0
    assert payload["workflow"]["blocks_workflow"] is False
    assert len(payload["navigation_units"]) == 8


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
    assert state["status"] == "ARTIFACT_ROUTE_READY"
    assert state["legacy_task"]["status"] == "REJECTED_LEGACY_TASK_SETTING"
    assert state["legacy_task"]["human_gate_count"] == 0
    assert state["boundaries"]["production_acceptance"] is False
    payload = cockpit_payload(snapshot, review_url="http://127.0.0.1:8060/final_video.mp4")
    assert payload["project_state"] == "TASK_BOARD_ACTIVE"


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


def test_snapshot_rejects_task_board_without_ten_unique_tasks(tmp_path: Path) -> None:
    root, config_path = _fixture(tmp_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    task_board_path = root / config["task_board"]["path"]
    task_board = json.loads(task_board_path.read_text(encoding="utf-8"))
    task_board["tasks"] = task_board["tasks"][:9]
    task_board_path.write_text(json.dumps(task_board), encoding="utf-8")
    config["task_board"]["sha256"] = _sha256(task_board_path)
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly ten unique tasks"):
        load_cockpit_snapshot(
            repo_root=root,
            config_path=config_path,
            duration_probe=lambda _path: 12.3,
        )


def test_snapshot_rejects_noncontiguous_navigation_units(tmp_path: Path) -> None:
    root, config_path = _fixture(tmp_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    navigation_path = root / config["navigation_calibration"]["path"]
    navigation = json.loads(navigation_path.read_text(encoding="utf-8"))
    navigation["decision_units"][3]["output_range_seconds"][0] = 5.0
    navigation_path.write_text(json.dumps(navigation), encoding="utf-8")
    config["navigation_calibration"]["sha256"] = _sha256(navigation_path)
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="contiguous"):
        load_cockpit_snapshot(
            repo_root=root,
            config_path=config_path,
            duration_probe=lambda _path: 12.3,
        )


def test_static_surface_exposes_task_board_without_whole_gate() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    html = (repo_root / "gui" / "project_cockpit" / "index.html").read_text(encoding="utf-8")
    script = (repo_root / "gui" / "project_cockpit" / "app.js").read_text(encoding="utf-8")
    assert "いま進める作業" in html
    assert "この段階では要求しない" in html
    assert "task_board.tasks" in script
    assert "payload.workflow.resolved_decision_units" in script
    assert "0 questions revived" in script
    assert "window.open(cockpit.candidate.review_url" in script
    assert "8区間から再生位置を選ぶ" in html
    assert "payload.navigation_units.map" in script
    assert "activeNavigation.end_seconds" in script
    assert "ui.video.currentTime = unit.start_seconds" in script
    assert 'type="radio"' not in html
    assert "accept_whole_candidate" not in html
    assert '<video id="candidate-video" controls muted' in html
    assert "ui.video.volume = 0" in script
    assert "ui.video.pause()" in script
    assert "Accept whole or bounded revision?" not in html
