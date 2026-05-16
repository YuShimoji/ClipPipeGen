"""ED-04: subtitle draft generation from transcript segments."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.edit_pack import (
    add_cut_candidate,
    build_skeleton as build_edit_skeleton,
    load_edit_pack,
    save_edit_pack,
    validate_edit_pack,
)
from src.pipeline.subtitle_generation import (
    SubtitleGenerationError,
    generate_subtitle_drafts,
)
from src.pipeline.transcript import build_transcript, save_transcript


REPO_ROOT = Path(__file__).resolve().parent.parent


def _transcript() -> dict:
    return build_transcript(
        "ep_sub_001",
        source_audio_path="episodes/ep_sub_001/materials/src_audio_001/source.wav",
        language="ja",
        stt_engine="fake",
        segments=[
            {
                "id": "seg_001",
                "start_seconds": 1.0,
                "end_seconds": 3.0,
                "text": "ここが一番おもしろいところ",
            },
            {
                "id": "seg_002",
                "start_seconds": 4.0,
                "end_seconds": 6.0,
                "text": "次の展開も見てください",
            },
        ],
    )


def test_generate_subtitle_drafts_from_all_segments():
    pack = build_edit_skeleton("ep_sub_001")
    result = generate_subtitle_drafts(pack, _transcript())

    assert result.generated_count == 2
    assert result.subtitle_source_type == "transcript_segments"
    assert result.production_subtitle_design is False
    subtitles = result.edit_pack["subtitles"]
    assert subtitles[0]["id"] == "sub_001"
    assert subtitles[0]["source"] == "auto"
    assert subtitles[0]["source_type"] == "transcript_segments"
    assert subtitles[0]["source_segment_id"] == "seg_001"
    assert subtitles[0]["source_segment_ids"] == ["seg_001"]
    assert subtitles[0]["draft"] is True
    assert subtitles[0]["diagnostic"] is True
    assert subtitles[0]["not_production_subtitle_design"] is True
    assert subtitles[0]["production_subtitle_design"] is False
    assert subtitles[0]["cut_id"] is None
    assert validate_edit_pack(result.edit_pack) == []


def test_generate_subtitle_drafts_wraps_by_eaw():
    pack = build_edit_skeleton("ep_sub_001")
    result = generate_subtitle_drafts(pack, _transcript(), wrap_eaw=8)

    assert "\n" in result.edit_pack["subtitles"][0]["text"]


def test_selected_cuts_only_filters_and_assigns_cut_id():
    pack = build_edit_skeleton("ep_sub_001")
    pack = add_cut_candidate(
        pack,
        start_seconds=2.0,
        end_seconds=5.0,
        reason="selected highlight",
        select=True,
    )

    result = generate_subtitle_drafts(pack, _transcript(), selected_cuts_only=True)

    assert result.generated_count == 2
    assert result.edit_pack["subtitles"][0]["cut_id"] == "cut_001"
    assert result.edit_pack["subtitles"][0]["start_seconds"] == 2.0
    assert result.edit_pack["subtitles"][0]["end_seconds"] == 3.0
    assert result.edit_pack["subtitles"][1]["start_seconds"] == 4.0
    assert result.edit_pack["subtitles"][1]["end_seconds"] == 5.0


def test_existing_auto_subtitles_require_replace_auto():
    pack = build_edit_skeleton("ep_sub_001")
    result = generate_subtitle_drafts(pack, _transcript())

    with pytest.raises(SubtitleGenerationError, match="replace-auto"):
        generate_subtitle_drafts(result.edit_pack, _transcript())

    refreshed = generate_subtitle_drafts(
        result.edit_pack,
        _transcript(),
        replace_auto=True,
    )
    assert refreshed.generated_count == 2
    assert refreshed.replaced_auto_count == 2
    assert len(refreshed.edit_pack["subtitles"]) == 2


def test_wrap_eaw_must_be_positive():
    pack = build_edit_skeleton("ep_sub_001")
    with pytest.raises(SubtitleGenerationError, match="wrap_eaw"):
        generate_subtitle_drafts(pack, _transcript(), wrap_eaw=0)


def test_cli_generate_subtitles_roundtrip(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    transcript_path = tmp_path / "transcript.json"
    save_edit_pack(build_edit_skeleton("ep_sub_001"), edit_pack_path)
    save_transcript(_transcript(), transcript_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "generate-subtitles",
            "--edit-pack",
            str(edit_pack_path),
            "--transcript",
            str(transcript_path),
            "--wrap-eaw",
            "10",
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
    assert payload["subtitle_source_type"] == "transcript_segments"
    assert payload["production_subtitle_design"] is False
    pack = load_edit_pack(edit_pack_path)
    assert len(pack["subtitles"]) == 2
    assert validate_edit_pack(pack) == []


def test_cli_generate_subtitles_dry_run_writes_nothing(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    transcript_path = tmp_path / "transcript.json"
    save_edit_pack(build_edit_skeleton("ep_sub_001"), edit_pack_path)
    save_transcript(_transcript(), transcript_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "generate-subtitles",
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
    assert load_edit_pack(edit_pack_path)["subtitles"] == []
