"""ED-02: cut candidate generation from transcript segments."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.cut_generation import CutGenerationError, generate_cut_candidates
from src.pipeline.edit_pack import (
    build_skeleton as build_edit_skeleton,
    load_edit_pack,
    save_edit_pack,
    validate_edit_pack,
)
from src.pipeline.transcript import build_transcript, save_transcript


REPO_ROOT = Path(__file__).resolve().parent.parent


def _transcript() -> dict:
    return build_transcript(
        "ep_cut_001",
        source_audio_path="episodes/ep_cut_001/materials/src_audio_001/source.wav",
        language="ja",
        stt_engine="fake",
        segments=[
            {
                "id": "seg_001",
                "start_seconds": 0.0,
                "end_seconds": 10.0,
                "text": "最初の導入です",
                "confidence": 0.8,
            },
            {
                "id": "seg_002",
                "start_seconds": 11.0,
                "end_seconds": 20.0,
                "text": "ここで大きな見どころがあります",
                "confidence": 0.9,
            },
            {
                "id": "seg_003",
                "start_seconds": 21.0,
                "end_seconds": 30.0,
                "text": "最後にオチがあります",
                "confidence": 0.85,
            },
        ],
    )


def test_generate_cut_candidates_from_transcript_windows():
    pack = build_edit_skeleton("ep_cut_001")
    result = generate_cut_candidates(
        pack,
        _transcript(),
        target_duration_seconds=20.0,
        max_duration_seconds=22.0,
    )

    assert result.generated_count == 2
    cuts = result.edit_pack["cut_candidates"]
    assert cuts[0]["id"] == "cut_001"
    assert cuts[0]["source"] == "auto"
    assert cuts[0]["source_segment_ids"] == ["seg_001", "seg_002"]
    assert cuts[0]["context_check"]["status"] == "not_checked"
    assert 0 <= cuts[0]["confidence"] <= 1
    assert validate_edit_pack(result.edit_pack) == []


def test_generate_cut_candidates_splits_on_large_gap():
    transcript = _transcript()
    transcript["segments"][1]["start_seconds"] = 30.0
    transcript["segments"][1]["end_seconds"] = 40.0
    transcript["segments"][2]["start_seconds"] = 41.0
    transcript["segments"][2]["end_seconds"] = 50.0
    pack = build_edit_skeleton("ep_cut_001")

    result = generate_cut_candidates(
        pack,
        transcript,
        target_duration_seconds=20.0,
        gap_threshold_seconds=4.0,
        max_candidates=5,
    )

    assert result.generated_count == 2
    assert result.edit_pack["cut_candidates"][0]["source_segment_ids"] == ["seg_001"]
    assert result.edit_pack["cut_candidates"][1]["source_segment_ids"] == ["seg_002", "seg_003"]


def test_existing_auto_cuts_require_replace_auto():
    pack = build_edit_skeleton("ep_cut_001")
    first = generate_cut_candidates(pack, _transcript(), target_duration_seconds=20.0)

    with pytest.raises(CutGenerationError, match="replace-auto"):
        generate_cut_candidates(first.edit_pack, _transcript(), target_duration_seconds=20.0)

    refreshed = generate_cut_candidates(
        first.edit_pack,
        _transcript(),
        target_duration_seconds=20.0,
        replace_auto=True,
    )
    assert refreshed.replaced_auto_count == first.generated_count
    assert refreshed.generated_count == first.generated_count


def test_select_generated_adds_selected_cut_ids():
    pack = build_edit_skeleton("ep_cut_001")
    result = generate_cut_candidates(
        pack,
        _transcript(),
        target_duration_seconds=20.0,
        select_generated=True,
    )

    assert result.edit_pack["selected_cut_ids"] == [
        c["id"] for c in result.edit_pack["cut_candidates"]
    ]


def test_invalid_duration_options_fail():
    pack = build_edit_skeleton("ep_cut_001")
    with pytest.raises(CutGenerationError, match="min_duration_seconds"):
        generate_cut_candidates(
            pack,
            _transcript(),
            min_duration_seconds=30.0,
            max_duration_seconds=10.0,
        )


def test_cli_generate_cuts_roundtrip(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    transcript_path = tmp_path / "transcript.json"
    save_edit_pack(build_edit_skeleton("ep_cut_001"), edit_pack_path)
    save_transcript(_transcript(), transcript_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "generate-cuts",
            "--edit-pack",
            str(edit_pack_path),
            "--transcript",
            str(transcript_path),
            "--target-duration-seconds",
            "20",
            "--max-duration-seconds",
            "22",
            "--select-generated",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["generated_count"] == 2
    pack = load_edit_pack(edit_pack_path)
    assert len(pack["cut_candidates"]) == 2
    assert pack["selected_cut_ids"] == ["cut_001", "cut_002"]
    assert validate_edit_pack(pack) == []


def test_cli_generate_cuts_dry_run_writes_nothing(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    transcript_path = tmp_path / "transcript.json"
    save_edit_pack(build_edit_skeleton("ep_cut_001"), edit_pack_path)
    save_transcript(_transcript(), transcript_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "generate-cuts",
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
    assert load_edit_pack(edit_pack_path)["cut_candidates"] == []
