"""CR-01: rights_manifest の最小テスト。

testing policy: positive 1 + critical negatives 数個。網羅率を目的にしない。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.rights_manifest import (
    assert_compliance_passed,
    build_skeleton,
    evaluate_compliance_auto_fail,
    set_compliance_status,
    validate_rights_manifest,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def _hololive_passable() -> dict:
    """review notes が出ない最小 manifest。"""
    m = build_skeleton("ep_test_001")
    m["source_video"].update(
        url="https://www.youtube.com/watch?v=AAA",
        title="t",
        channel="c",
        channel_id="UC0001",
        vod_status="public",
    )
    m["talents"] = [
        {
            "name": "TestTalent",
            "agency": "hololive",
            "guideline_url": "https://www.hololive.tv/terms",
            "guideline_version_checked_at": "2026-05-06",
        }
    ]
    return m


# --- positive ---


def test_skeleton_passes_basic_validation_after_minimum_fill():
    m = _hololive_passable()
    issues = validate_rights_manifest(m)
    assert issues == [], [i.to_dict() for i in issues]


# --- critical negatives ---


def test_validation_detects_empty_talents():
    m = _hololive_passable()
    m["talents"] = []
    issues = validate_rights_manifest(m)
    assert any(i.code == "TALENTS_EMPTY" for i in issues)


def test_review_note_when_vod_is_members_only():
    m = _hololive_passable()
    m["source_video"]["vod_status"] = "members_only"
    notes = evaluate_compliance_auto_fail(m)
    assert any(i.code == "VOD_STATUS_REVIEW" for i in notes)


def test_review_note_when_third_party_ip_not_permitted():
    m = _hololive_passable()
    m["third_party_ip"] = [
        {"kind": "music", "name": "X", "rights_holder": "Y", "permitted": False}
    ]
    notes = evaluate_compliance_auto_fail(m)
    assert any(i.code == "THIRD_PARTY_IP_REVIEW" for i in notes)


def test_set_compliance_passed_keeps_review_notes_as_warnings():
    m = _hololive_passable()
    m["source_video"]["vod_status"] = "private"
    updated = set_compliance_status(m, status="passed", checked_by="user:tester")
    assert updated["compliance_check"]["status"] == "passed"
    assert any(
        w["code"] == "VOD_STATUS_REVIEW"
        for w in updated["compliance_check"]["warnings"]
    )


def test_set_compliance_passed_succeeds_when_clean():
    m = _hololive_passable()
    updated = set_compliance_status(m, status="passed", checked_by="user:tester")
    assert updated["compliance_check"]["status"] == "passed"
    assert updated["compliance_check"]["checked_by"] == "user:tester"
    assert updated["compliance_check"]["checked_at"]
    # legacy compatibility helper is a no-op
    assert_compliance_passed(updated)


def test_assert_compliance_passed_is_legacy_noop_when_pending():
    m = _hololive_passable()  # status=pending by default
    assert_compliance_passed(m)


def test_hololive_talent_with_unrelated_guideline_url_is_flagged():
    m = _hololive_passable()
    m["talents"][0]["guideline_url"] = "https://example.com/random"
    issues = validate_rights_manifest(m)
    assert any(i.code == "TALENT_HOLOLIVE_GUIDELINE_URL" for i in issues)


# --- CLI smoke (subprocess, but lightweight) ---


def test_cli_init_episode_and_validate_roundtrip(tmp_path: Path):
    env_args = {"cwd": str(REPO_ROOT)}
    episode_root = tmp_path / "episodes"
    init = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "init-episode",
            "--episode-id",
            "ep_smoke_001",
            "--root",
            str(episode_root),
        ],
        capture_output=True,
        text=True,
        **env_args,
    )
    assert init.returncode == 0, init.stderr
    manifest_path = episode_root / "ep_smoke_001" / "rights_manifest.json"
    assert manifest_path.exists()

    # validate the freshly created skeleton: schema is incomplete (empty talents),
    # so we expect non-zero exit and at least one TALENTS_EMPTY issue.
    val = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "validate-rights",
            "--rights-manifest",
            str(manifest_path),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        **env_args,
    )
    assert val.returncode == 1
    payload = json.loads(val.stdout)
    assert payload["schema_ok"] is False
    assert any(i["code"] == "TALENTS_EMPTY" for i in payload["schema_issues"])
