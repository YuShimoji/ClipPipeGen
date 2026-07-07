from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.episode_workspace import (
    EpisodeWorkspaceError,
    build_episode_workspace_plan,
    inspect_episode_workspace,
    init_episode_workspace,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
OPERATOR_COCKPIT = REPO_ROOT / "docs" / "content_planning" / "operator_cockpit.json"


def test_episode_workspace_plan_writes_contract_and_plan(tmp_path: Path):
    result = build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=tmp_path / "episode_workspace_plan.json",
        contract_output_path=tmp_path / "automation_contract.json",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    plan = json.loads(result["output_path"].read_text(encoding="utf-8"))
    contract = json.loads(result["contract_output_path"].read_text(encoding="utf-8"))

    assert plan["schema_id"] == "clippipegen.episode_workspace_plan.v0"
    assert plan["artifact_id"] == "clip-ews01-episode-workspace-spine-v0-001"
    assert plan["episode_id"] == "ep_seed_cpd01_bancho_marine_misunderstanding"
    assert plan["planning_label"] == "番長、船長を完全に勘違いする"
    assert plan["label_provenance"] == "planning_label_unverified"
    assert plan["verified_video_title"] == ""
    assert plan["source_url"] == "https://www.youtube.com/watch?v=7J5aS_pcBj4"
    assert plan["source_url_state"] == "present"
    assert plan["identity_state"] == "unverified"
    assert plan["fetch_authorized"] is False
    assert plan["local_workspace_state"] == "planned"
    assert plan["planned_paths"]["manifest"].endswith("/episode_manifest.json")
    assert plan["planned_paths"]["source_receipt"].endswith(
        "/materials/source/source_receipt.pending.json"
    )
    assert plan["planned_paths"]["transcript"].endswith("/transcript.json")
    assert plan["planned_paths"]["edit_pack"].endswith("/edit_pack.json")
    assert plan["planned_paths"]["subtitle"].endswith("/subtitles.json")
    assert plan["planned_paths"]["thumbnail_brief"].endswith("/thumbnail_brief_seed.json")
    assert plan["planned_paths"]["preview_pack"].endswith(
        "/review/preview_pack/preview_manifest.json"
    )
    assert plan["next_allowed_local_action"]["action_id"] == (
        "init_episode_workspace_explicit_target"
    )
    assert "source_url_opening" in plan["deferred_local_actions"]
    assert "oauth_api_keys_credentials" in plan["blocked_true_gates"]
    assert plan["readback"]["planning_label_is_verified_video_title"] is False
    assert plan["readback"]["source_url_opened_by_worker"] is False
    assert plan["readback"]["media_downloaded"] is False
    assert plan["readback"]["transcript_generated"] is False
    assert plan["readback"]["render_generated"] is False
    assert plan["readback"]["rights_approved"] is False

    assert contract["schema_id"] == "clippipegen.automation_contract.v0"
    assert len(contract["allowed_local_actions"]) >= 6
    assert len(contract["deferred_local_actions"]) >= 6
    assert len(contract["true_external_gates"]) >= 7
    assert contract["classification_readback"]["local_episode_workspace_init"] == (
        "allowed_local_actions"
    )
    assert (
        contract["classification_readback"]["local_episode_workspace_init_is_true_external_gate"]
        is False
    )
    assert not any(
        item["action_id"] == "local_episode_workspace_init"
        for item in contract["true_external_gates"]
    )

    assert not (tmp_path / "episodes").exists()


def test_build_episode_workspace_plan_cli_writes_outputs(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-episode-workspace-plan",
            "--input",
            str(OPERATOR_COCKPIT),
            "--output",
            str(plan_path),
            "--contract-output",
            str(contract_path),
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
    assert payload["artifact_id"] == "clip-ews01-episode-workspace-spine-v0-001"
    assert payload["episode_id"] == "ep_seed_cpd01_bancho_marine_misunderstanding"
    assert payload["local_workspace_state"] == "planned"
    assert payload["source_url_state"] == "present"
    assert payload["identity_state"] == "unverified"
    assert payload["fetch_authorized"] is False
    assert payload["source_url_opened_by_worker"] is False
    assert payload["media_downloaded"] is False
    assert payload["rights_approved"] is False
    assert plan_path.exists()
    assert contract_path.exists()


def test_init_episode_workspace_dry_run_does_not_write(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=plan_path,
        contract_output_path=contract_path,
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    target_root = tmp_path / "workspace_target"
    result = init_episode_workspace(
        plan_path=plan_path,
        target_root=target_root,
        materialize=False,
        base_dir=REPO_ROOT,
    )

    assert result["materialized"] is False
    assert result["created_file_count"] == 0
    assert result["planned_file_count"] == 5
    assert not target_root.exists()
    assert result["side_effects"]["source_url_opened"] is False
    assert result["side_effects"]["media_files_created"] is False
    assert result["side_effects"]["transcript_generated"] is False
    assert result["side_effects"]["render_generated"] is False
    assert result["side_effects"]["rights_approved"] is False


def test_init_episode_workspace_materializes_tempdir_skeleton(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=plan_path,
        contract_output_path=contract_path,
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    target_root = tmp_path / "workspace_target"
    result = init_episode_workspace(
        plan_path=plan_path,
        target_root=target_root,
        materialize=True,
        base_dir=REPO_ROOT,
    )

    workspace_dir = target_root / "ep_seed_cpd01_bancho_marine_misunderstanding"
    expected = {
        "episode_manifest.json",
        "README_NEXT.md",
        "source_identity.pending.json",
        "edit_plan_seed.json",
        "thumbnail_brief_seed.json",
    }
    assert result["materialized"] is True
    assert result["created_file_count"] == len(expected)
    assert {path.name for path in workspace_dir.iterdir()} == expected
    assert not list(workspace_dir.rglob("*.mp4"))
    assert not list(workspace_dir.rglob("*.wav"))

    manifest = json.loads((workspace_dir / "episode_manifest.json").read_text(encoding="utf-8"))
    source_identity = json.loads(
        (workspace_dir / "source_identity.pending.json").read_text(encoding="utf-8")
    )
    assert manifest["planning_label_is_verified_video_title"] is False
    assert manifest["fetch_authorized"] is False
    assert manifest["media_files_expected"] is False
    assert source_identity["review_status"] == "pending"
    assert source_identity["source_url_opened_by_worker"] is False
    assert result["side_effects"]["media_files_created"] is False


def test_init_episode_workspace_cli_materializes_tempdir_skeleton(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=plan_path,
        contract_output_path=contract_path,
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    target_root = tmp_path / "workspace_target"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "init-episode-workspace",
            "--plan",
            str(plan_path),
            "--target",
            str(target_root),
            "--materialize",
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
    assert payload["episode_id"] == "ep_seed_cpd01_bancho_marine_misunderstanding"
    assert payload["materialized"] is True
    assert payload["created_file_count"] == 5
    assert payload["source_url_opened"] is False
    assert payload["media_files_created"] is False
    assert payload["transcript_generated"] is False
    assert payload["render_generated"] is False
    assert payload["rights_approved"] is False


def test_init_episode_workspace_refuses_existing_files_without_force(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=plan_path,
        contract_output_path=contract_path,
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )
    target_root = tmp_path / "workspace_target"
    init_episode_workspace(plan_path=plan_path, target_root=target_root, materialize=True)

    with pytest.raises(EpisodeWorkspaceError, match="refusing to overwrite"):
        init_episode_workspace(plan_path=plan_path, target_root=target_root, materialize=True)


def test_inspect_episode_workspace_reports_skeleton_status(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=plan_path,
        contract_output_path=contract_path,
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )
    target_root = tmp_path / "workspace_target"
    init_result = init_episode_workspace(
        plan_path=plan_path,
        target_root=target_root,
        materialize=True,
        base_dir=REPO_ROOT,
    )

    result = inspect_episode_workspace(
        workspace_path=Path(init_result["workspace_dir"]),
        plan_path=plan_path,
        contract_path=contract_path,
        base_dir=REPO_ROOT,
    )

    expected = {
        "episode_manifest.json",
        "README_NEXT.md",
        "source_identity.pending.json",
        "edit_plan_seed.json",
        "thumbnail_brief_seed.json",
    }
    assert result["schema_id"] == "clippipegen.episode_workspace_inspection.v0"
    assert result["artifact_id"] == "clip-ews02-episode-workspace-inspector-v0-001"
    assert result["episode_id"] == "ep_seed_cpd01_bancho_marine_misunderstanding"
    assert result["planned_slug"] == "ep_seed_cpd01_bancho_marine_misunderstanding"
    assert result["manifest_state"] == "initialized"
    assert result["source_identity_state"] == "pending"
    assert result["source_url_state"] == "present"
    assert result["fetch_authorized"] is False
    assert set(result["skeleton_files_present"]) == expected
    assert result["missing_files"] == []
    assert result["files"]["unexpected_media_like"] == []
    assert result["states"]["workspace_state"] == "skeleton_ready"
    assert result["states"]["media_state"] == "not_present"
    assert result["states"]["transcript_state"] == "not_present"
    assert result["states"]["edit_pack_state"] == "seed_present"
    assert result["states"]["render_state"] == "not_present"
    assert result["readiness_level"] == "source_identity_pending"
    assert result["readiness"]["skeleton_ready"] is True
    assert result["readiness"]["ready_for_source_identity_decision"] is True
    assert result["readiness"]["ready_for_fetch"] is False
    assert result["readiness"]["blocked_by_true_gate"] is False
    assert result["next_allowed_local_action"]["action_id"] == (
        "record_source_identity_decision_local"
    )
    assert "source_url_opening" in result["deferred_local_actions"]
    assert "public_upload_publication" in result["true_external_gates"]
    assert result["thin_gate_contract"]["local_workspace_init_is_true_external_gate"] is False
    assert result["side_effects"]["source_url_opened"] is False
    assert result["side_effects"]["media_files_created"] is False
    assert result["side_effects"]["transcript_generated"] is False
    assert result["side_effects"]["render_generated"] is False
    assert result["side_effects"]["thumbnail_generated"] is False
    assert result["side_effects"]["rights_approved"] is False


def test_inspect_episode_workspace_cli_emits_parseable_json(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=plan_path,
        contract_output_path=contract_path,
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )
    target_root = tmp_path / "workspace_target"
    init_result = init_episode_workspace(
        plan_path=plan_path,
        target_root=target_root,
        materialize=True,
        base_dir=REPO_ROOT,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "inspect-episode-workspace",
            "--workspace",
            init_result["workspace_dir"],
            "--plan",
            str(plan_path),
            "--contract",
            str(contract_path),
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
    assert payload["artifact_id"] == "clip-ews02-episode-workspace-inspector-v0-001"
    assert payload["episode_id"] == "ep_seed_cpd01_bancho_marine_misunderstanding"
    assert payload["manifest_state"] == "initialized"
    assert payload["source_identity_state"] == "pending"
    assert payload["readiness_level"] == "source_identity_pending"
    assert payload["readiness"]["skeleton_ready"] is True
    assert payload["readiness"]["ready_for_fetch"] is False
    assert payload["files"]["unexpected_media_like"] == []


def test_inspect_episode_workspace_reports_missing_skeleton_files(tmp_path: Path):
    plan_path = tmp_path / "episode_workspace_plan.json"
    contract_path = tmp_path / "automation_contract.json"
    build_episode_workspace_plan(
        operator_cockpit_path=OPERATOR_COCKPIT,
        output_path=plan_path,
        contract_output_path=contract_path,
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )
    target_root = tmp_path / "workspace_target"
    init_result = init_episode_workspace(
        plan_path=plan_path,
        target_root=target_root,
        materialize=True,
        base_dir=REPO_ROOT,
    )
    workspace_dir = Path(init_result["workspace_dir"])
    (workspace_dir / "thumbnail_brief_seed.json").unlink()

    result = inspect_episode_workspace(
        workspace_path=workspace_dir,
        plan_path=plan_path,
        contract_path=contract_path,
        base_dir=REPO_ROOT,
    )

    assert result["missing_files"] == ["thumbnail_brief_seed.json"]
    assert result["states"]["workspace_state"] == "planned_missing_files"
    assert result["readiness_level"] == "planned"
    assert result["readiness"]["skeleton_ready"] is False
    assert result["next_allowed_local_action"]["action_id"] == (
        "init_episode_workspace_explicit_target"
    )
