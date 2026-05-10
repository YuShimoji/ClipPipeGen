"""ED-03: cut boundary context checks from transcript adjacency."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.context_check import ContextCheckError, check_cut_context
from src.pipeline.edit_pack import build_skeleton as build_edit_skeleton
from src.pipeline.edit_pack import load_edit_pack, save_edit_pack, validate_edit_pack
from src.pipeline.transcript import build_transcript, save_transcript


REPO_ROOT = Path(__file__).resolve().parent.parent


def _transcript(*, close_next: bool = False) -> dict:
    next_start = 20.5 if close_next else 23.0
    return build_transcript(
        "ep_ctx_001",
        source_audio_path="episodes/ep_ctx_001/materials/src_audio_001/source.wav",
        language="ja",
        stt_engine="fake",
        segments=[
            {
                "id": "seg_001",
                "start_seconds": 0.0,
                "end_seconds": 9.0,
                "text": "導入です",
                "confidence": 0.8,
            },
            {
                "id": "seg_002",
                "start_seconds": 10.0,
                "end_seconds": 20.0,
                "text": "ここが見どころです",
                "confidence": 0.9,
            },
            {
                "id": "seg_003",
                "start_seconds": next_start,
                "end_seconds": next_start + 8.0,
                "text": "その後の補足です",
                "confidence": 0.85,
            },
        ],
    )


def _pack_with_cuts() -> dict:
    pack = build_edit_skeleton("ep_ctx_001")
    pack["cut_candidates"] = [
        {
            "id": "cut_001",
            "start_seconds": 0.0,
            "end_seconds": 20.0,
            "source": "auto",
            "reason": "auto transcript window",
            "confidence": 0.8,
            "context_check": {"status": "not_checked", "notes": []},
            "source_segment_ids": ["seg_001", "seg_002"],
        },
        {
            "id": "cut_002",
            "start_seconds": 10.0,
            "end_seconds": 20.0,
            "source": "manual",
            "reason": "manual short version",
            "confidence": 1.0,
            "context_check": {"status": "not_checked", "notes": []},
            "source_segment_ids": ["seg_002"],
        },
    ]
    pack["selected_cut_ids"] = ["cut_002"]
    return pack


def test_context_check_passes_aligned_cut_boundaries():
    result = check_cut_context(
        _pack_with_cuts(),
        _transcript(),
        cut_id="cut_001",
    )

    assert result.checked_count == 1
    assert result.passed_count == 1
    cut = result.edit_pack["cut_candidates"][0]
    assert cut["context_check"]["status"] == "passed"
    assert "checked_at" in cut["context_check"]
    assert validate_edit_pack(result.edit_pack) == []


def test_context_check_needs_review_for_close_adjacent_segment():
    result = check_cut_context(
        _pack_with_cuts(),
        _transcript(close_next=True),
        cut_id="cut_001",
    )

    cut = result.edit_pack["cut_candidates"][0]
    assert cut["context_check"]["status"] == "needs_review"
    assert any("next segment seg_003" in note for note in cut["context_check"]["notes"])


def test_context_check_fails_when_boundary_cuts_through_segment():
    pack = _pack_with_cuts()
    pack["cut_candidates"][0]["start_seconds"] = 2.0

    result = check_cut_context(pack, _transcript(), cut_id="cut_001")

    cut = result.edit_pack["cut_candidates"][0]
    assert cut["context_check"]["status"] == "failed"
    assert any("start boundary cuts through segment seg_001" in note for note in cut["context_check"]["notes"])


def test_context_check_selected_scope_leaves_other_cuts_unchanged():
    result = check_cut_context(
        _pack_with_cuts(),
        _transcript(close_next=True),
        selected_cuts_only=True,
    )

    assert result.checked_count == 1
    assert result.skipped_count == 1
    assert result.edit_pack["cut_candidates"][0]["context_check"]["status"] == "not_checked"
    assert result.edit_pack["cut_candidates"][1]["context_check"]["status"] == "needs_review"


def test_context_check_rejects_unknown_cut_id():
    with pytest.raises(ContextCheckError, match="cut_id not found"):
        check_cut_context(_pack_with_cuts(), _transcript(), cut_id="cut_missing")


def test_cli_check_cut_context_roundtrip(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    transcript_path = tmp_path / "transcript.json"
    save_edit_pack(_pack_with_cuts(), edit_pack_path)
    save_transcript(_transcript(close_next=True), transcript_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "check-cut-context",
            "--edit-pack",
            str(edit_pack_path),
            "--transcript",
            str(transcript_path),
            "--cut-id",
            "cut_001",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["needs_review_count"] == 1
    pack = load_edit_pack(edit_pack_path)
    assert pack["cut_candidates"][0]["context_check"]["status"] == "needs_review"


def test_cli_check_cut_context_dry_run_writes_nothing(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    transcript_path = tmp_path / "transcript.json"
    save_edit_pack(_pack_with_cuts(), edit_pack_path)
    save_transcript(_transcript(close_next=True), transcript_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "check-cut-context",
            "--edit-pack",
            str(edit_pack_path),
            "--transcript",
            str(transcript_path),
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["dry_run"] is True
    pack = load_edit_pack(edit_pack_path)
    assert [c["context_check"]["status"] for c in pack["cut_candidates"]] == [
        "not_checked",
        "not_checked",
    ]
