"""ED-07: transcript schema and fake transcribe-audio CLI tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.material_ledger import compute_sha256
from src.pipeline.transcript import (
    build_transcript,
    load_transcript,
    save_transcript,
    validate_transcript,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def _segments() -> list[dict]:
    return [
        {
            "start_seconds": 1.0,
            "end_seconds": 2.5,
            "text": "ここが見どころ",
        }
    ]


def _valid_transcript() -> dict:
    return build_transcript(
        "ep_tr_001",
        source_audio_path="episodes/ep_tr_001/source.wav",
        source_audio_sha256="abc123",
        language="ja",
        stt_engine="fake",
        stt_engine_version="fake-v1",
        segments=_segments(),
    )


def test_valid_transcript_positive():
    transcript = _valid_transcript()
    assert validate_transcript(transcript) == []
    assert transcript["segments"][0]["id"] == "seg_000001"
    assert transcript["segments"][0]["review_status"] == "unreviewed"


def test_duplicate_segment_id_is_invalid():
    transcript = _valid_transcript()
    transcript["segments"].append(dict(transcript["segments"][0]))
    issues = validate_transcript(transcript)
    assert any(i.code == "TRANSCRIPT_SEGMENT_ID_DUPLICATE" for i in issues)


def test_segment_time_range_must_be_ordered():
    transcript = _valid_transcript()
    transcript["segments"][0]["end_seconds"] = 1.0
    issues = validate_transcript(transcript)
    assert any(i.code == "TRANSCRIPT_SEGMENT_TIME_RANGE_INVALID" for i in issues)


def test_segment_text_is_required():
    transcript = _valid_transcript()
    transcript["segments"][0]["text"] = " "
    issues = validate_transcript(transcript)
    assert any(i.code == "TRANSCRIPT_SEGMENT_TEXT_MISSING" for i in issues)


def test_empty_segments_need_warning_or_review_note():
    transcript = build_transcript(
        "ep_tr_001",
        source_audio_path="episodes/ep_tr_001/source.wav",
        language="ja",
        stt_engine="fake",
        segments=[],
    )
    issues = validate_transcript(transcript)
    assert any(i.code == "TRANSCRIPT_SEGMENTS_EMPTY_REASON_MISSING" for i in issues)


def test_approved_review_requires_reviewer_and_time():
    transcript = _valid_transcript()
    transcript["review"]["status"] = "approved"
    issues = validate_transcript(transcript)
    codes = {i.code for i in issues}
    assert "TRANSCRIPT_REVIEWED_BY_MISSING" in codes
    assert "TRANSCRIPT_REVIEWED_AT_MISSING" in codes


def test_cli_transcribe_audio_fake_roundtrip(tmp_path: Path):
    audio_path = tmp_path / "source.wav"
    audio_path.write_bytes(b"fake audio")
    fixture_path = tmp_path / "segments.json"
    fixture_path.write_text(json.dumps(_segments(), ensure_ascii=False), encoding="utf-8")
    ledger_path = tmp_path / "material_ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "episode_id": "ep_tr_cli",
                "materials": [
                    {
                        "id": "src_audio_001",
                        "kind": "source_audio",
                        "file_path": str(audio_path),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    transcript_path = tmp_path / "transcript.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "transcribe-audio",
            "--episode-id",
            "ep_tr_cli",
            "--source-audio",
            str(audio_path),
            "--output",
            str(transcript_path),
            "--language",
            "ja",
            "--engine",
            "fake",
            "--fixture-segments",
            str(fixture_path),
            "--material-ledger",
            str(ledger_path),
            "--material-id",
            "src_audio_001",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    transcript = load_transcript(transcript_path)
    assert transcript["episode_id"] == "ep_tr_cli"
    assert transcript["source_audio"]["material_id"] == "src_audio_001"
    assert transcript["source_audio"]["sha256"] == compute_sha256(audio_path)
    assert transcript["stt"]["engine"] == "fake"
    assert transcript["segments"][0]["text"] == "ここが見どころ"


def test_cli_validate_transcript_json(tmp_path: Path):
    transcript_path = tmp_path / "transcript.json"
    save_transcript(_valid_transcript(), transcript_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "validate-transcript",
            "--transcript",
            str(transcript_path),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_ok"] is True
    assert payload["schema_issues"] == []
