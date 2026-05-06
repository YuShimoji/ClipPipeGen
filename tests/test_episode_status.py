"""SH-02-lite: episode status adapter tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.edit_pack import build_skeleton as build_edit_skeleton, save_edit_pack
from src.pipeline.material_ledger import build_skeleton as build_ledger_skeleton, save_ledger
from src.pipeline.episode_status import build_episode_status
from src.pipeline.rights_manifest import (
    build_skeleton,
    save_rights_manifest,
    set_compliance_status,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def _rights_passed(episode_id: str) -> dict:
    manifest = build_skeleton(episode_id)
    manifest["source_video"].update(
        url="https://www.youtube.com/watch?v=AAA",
        title="t",
        channel="c",
        channel_id="UC0001",
        vod_status="public",
    )
    manifest["talents"] = [
        {
            "name": "Talent",
            "agency": "hololive",
            "guideline_url": "https://www.hololive.tv/terms",
            "guideline_version_checked_at": "2026-05-07",
        }
    ]
    return set_compliance_status(manifest, status="passed", checked_by="user:tester")


def test_status_reports_missing_rights_first(tmp_path: Path):
    ep_dir = tmp_path / "episodes" / "ep_missing"
    ep_dir.mkdir(parents=True)
    status = build_episode_status(episode_dir=ep_dir, base_dir=tmp_path)
    assert status["rights"]["state"] == "missing"
    assert status["next_action"]["action"].startswith("Run init-episode")


def test_status_reports_material_registration_next_after_passed_rights(tmp_path: Path):
    ep_dir = tmp_path / "episodes" / "ep_ready"
    ep_dir.mkdir(parents=True)
    save_rights_manifest(_rights_passed("ep_ready"), ep_dir / "rights_manifest.json")

    status = build_episode_status(episode_dir=ep_dir, base_dir=tmp_path)
    assert status["episode_id"] == "ep_ready"
    assert status["rights"]["state"] == "ready"
    assert status["materials"]["state"] == "missing"
    assert status["next_action"]["action"].startswith("Register thumbnail material")


def test_status_reports_edit_pack_next_after_empty_ledger_exists(tmp_path: Path):
    ep_dir = tmp_path / "episodes" / "ep_edit_next"
    ep_dir.mkdir(parents=True)
    save_rights_manifest(_rights_passed("ep_edit_next"), ep_dir / "rights_manifest.json")
    save_ledger(build_ledger_skeleton("ep_edit_next"), ep_dir / "material_ledger.json")

    status = build_episode_status(episode_dir=ep_dir, base_dir=tmp_path)
    assert status["editing"]["state"] == "missing"
    # Empty material ledger is still treated as missing before editing can start.
    assert status["next_action"]["action"].startswith("Register thumbnail material")


def test_status_reads_edit_pack_when_present(tmp_path: Path):
    ep_dir = tmp_path / "episodes" / "ep_edit_present"
    ep_dir.mkdir(parents=True)
    save_rights_manifest(_rights_passed("ep_edit_present"), ep_dir / "rights_manifest.json")
    pack = build_edit_skeleton("ep_edit_present")
    save_edit_pack(pack, ep_dir / "edit_pack.json")

    status = build_episode_status(episode_dir=ep_dir, base_dir=tmp_path)
    assert status["editing"]["state"] == "manual_needed"
    assert status["editing"]["cut_candidates_count"] == 0


def test_status_episode_cli_outputs_json(tmp_path: Path):
    ep_dir = tmp_path / "episodes" / "ep_cli"
    ep_dir.mkdir(parents=True)
    save_rights_manifest(_rights_passed("ep_cli"), ep_dir / "rights_manifest.json")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "status-episode",
            "--episode-dir",
            str(ep_dir),
            "--base-dir",
            str(tmp_path),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["episode_id"] == "ep_cli"
    assert payload["rights"]["state"] == "ready"
