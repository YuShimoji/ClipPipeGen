"""ED-01: edit_pack schema / CLI tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.edit_pack import (
    add_cut_candidate,
    build_skeleton,
    load_edit_pack,
    save_edit_pack,
    validate_edit_pack,
)
from src.pipeline.rights_manifest import (
    build_skeleton as build_rights_skeleton,
    save_rights_manifest,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def _pack_with_one_cut() -> dict:
    pack = build_skeleton("ep_ed_001")
    pack["cut_candidates"] = [
        {
            "id": "cut_001",
            "start_seconds": 10.0,
            "end_seconds": 25.0,
            "source": "manual",
            "reason": "good punchline",
            "confidence": 1.0,
            "context_check": {"status": "not_checked", "notes": []},
        }
    ]
    pack["selected_cut_ids"] = ["cut_001"]
    pack["subtitles"] = [
        {
            "id": "sub_001",
            "cut_id": "cut_001",
            "start_seconds": 10.0,
            "end_seconds": 12.0,
            "text": "ここが見どころ",
            "source": "manual",
            "style_slot": "subtitle.default",
        }
    ]
    return pack


def test_edit_pack_skeleton_is_valid():
    pack = build_skeleton("ep_ed_001")
    assert validate_edit_pack(pack) == []


def test_edit_pack_with_manual_cut_and_subtitle_is_valid():
    pack = _pack_with_one_cut()
    assert validate_edit_pack(pack) == []


def test_add_cut_candidate_appends_and_selects():
    pack = build_skeleton("ep_ed_001")
    updated = add_cut_candidate(
        pack,
        start_seconds=5.0,
        end_seconds=12.5,
        reason="manual highlight",
        select=True,
    )
    assert updated["cut_candidates"][0]["id"] == "cut_001"
    assert updated["selected_cut_ids"] == ["cut_001"]
    assert validate_edit_pack(updated) == []


def test_add_cut_candidate_rejects_invalid_time_range():
    pack = build_skeleton("ep_ed_001")
    try:
        add_cut_candidate(pack, start_seconds=12.0, end_seconds=5.0)
    except ValueError as exc:
        assert "EDIT_CUT_TIME_RANGE_INVALID" in str(exc)
    else:
        raise AssertionError("invalid range should fail")


def test_cut_time_range_must_be_ordered():
    pack = _pack_with_one_cut()
    pack["cut_candidates"][0]["end_seconds"] = 9.0
    issues = validate_edit_pack(pack)
    assert any(i.code == "EDIT_CUT_TIME_RANGE_INVALID" for i in issues)


def test_selected_cut_id_must_exist():
    pack = _pack_with_one_cut()
    pack["selected_cut_ids"] = ["cut_missing"]
    issues = validate_edit_pack(pack)
    assert any(i.code == "EDIT_SELECTED_CUT_ID_UNKNOWN" for i in issues)


def test_subtitle_text_is_required():
    pack = _pack_with_one_cut()
    pack["subtitles"][0]["text"] = ""
    issues = validate_edit_pack(pack)
    assert any(i.code == "EDIT_SUBTITLE_TEXT_MISSING" for i in issues)


def test_approved_review_requires_reviewer_and_time():
    pack = build_skeleton("ep_ed_001")
    pack["review"]["status"] = "approved"
    issues = validate_edit_pack(pack)
    codes = {i.code for i in issues}
    assert "EDIT_REVIEWED_BY_MISSING" in codes
    assert "EDIT_REVIEWED_AT_MISSING" in codes


def test_cli_init_and_validate_edit_pack_roundtrip(tmp_path: Path):
    episode_root = tmp_path / "episodes"
    episode_dir = episode_root / "ep_ed_cli"
    episode_dir.mkdir(parents=True)
    save_rights_manifest(
        build_rights_skeleton("ep_ed_cli"),
        episode_dir / "rights_manifest.json",
    )

    init = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "init-edit-pack",
            "--episode-id",
            "ep_ed_cli",
            "--root",
            str(episode_root),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert init.returncode == 0, init.stderr
    edit_pack_path = episode_dir / "edit_pack.json"
    assert edit_pack_path.exists()

    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "validate-edit-pack",
            "--edit-pack",
            str(edit_pack_path),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, validate.stderr
    payload = json.loads(validate.stdout)
    assert payload["schema_ok"] is True


def test_cli_add_cut_candidate_roundtrip(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    save_edit_pack(build_skeleton("ep_ed_cli"), edit_pack_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "add-cut-candidate",
            "--edit-pack",
            str(edit_pack_path),
            "--start-seconds",
            "10",
            "--end-seconds",
            "18.5",
            "--reason",
            "manual import",
            "--select",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    pack = load_edit_pack(edit_pack_path)
    assert pack["cut_candidates"][0]["id"] == "cut_001"
    assert pack["selected_cut_ids"] == ["cut_001"]
