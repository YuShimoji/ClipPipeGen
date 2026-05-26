"""ED-10: subtitle track import / transcript alignment tests."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.cut_generation import generate_cut_candidates
from src.pipeline.edit_pack import build_skeleton, save_edit_pack
from src.pipeline.nle_export import export_csv_cut_list
from src.pipeline.subtitle_generation import generate_subtitle_drafts
from src.pipeline.subtitle_import import import_subtitle_track_transcript
from src.pipeline.transcript import build_transcript, save_transcript, validate_transcript


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_import_youtube_json3_builds_transcript_with_alignment_readback():
    base = _base_transcript()
    payload = {
        "events": [
            {
                "tStartMs": 100,
                "dDurationMs": 900,
                "segs": [{"utf8": "\u200bもしもし？\nはじめです！"}],
            },
            {
                "tStartMs": 1500,
                "dDurationMs": 1000,
                "segs": [{"utf8": "体育館裏で待ってます！！"}],
            },
            {
                "tStartMs": 2400,
                "dDurationMs": 800,
                "segs": [{"utf8": "なんて？？"}],
            },
            {
                "tStartMs": 7000,
                "dDurationMs": 1000,
                "segs": [{"utf8": "Vosk が拾っていない公式字幕"}],
            },
            {"tStartMs": 9000, "dDurationMs": 500, "segs": [{"utf8": "   "}]},
        ]
    }

    result = import_subtitle_track_transcript(
        base_transcript=base,
        subtitle_payload=payload,
        subtitle_track_path="episodes/ep/source_subs/test.ja.json3",
        reviewed_by="codex:test",
    )

    transcript = result.transcript
    assert result.imported_segment_count == 4
    assert result.skipped_event_count == 1
    assert result.aligned_segment_count == 3
    assert result.unaligned_segment_count == 1
    assert result.overlapping_segment_count == 1
    assert validate_transcript(transcript) == []
    assert transcript["episode_id"] == "ep_sub_import"
    assert transcript["source_audio"]["material_id"] == "src_audio_001"
    assert transcript["stt"]["engine"] == "subtitle_track"
    assert transcript["stt"]["provider"] == "youtube_subtitles"
    assert transcript["stt"]["real_transcript"] is True
    assert transcript["review"]["status"] == "needs_review"
    assert transcript["review"]["reviewed_by"] == "codex:test"
    assert transcript["segments"][0]["text"] == "もしもし？ はじめです！"
    assert transcript["segments"][0]["review_status"] == "accepted"
    assert "aligned_base_segment_id=seg_base_001" in " ".join(
        transcript["segments"][0]["notes"]
    )
    assert "no_base_segment_overlap" in " ".join(transcript["segments"][-1]["notes"])


def test_import_subtitle_track_cli_dry_run_does_not_write(tmp_path: Path):
    base_path = tmp_path / "base_transcript.json"
    track_path = tmp_path / "track.json3"
    output_path = tmp_path / "imported_transcript.json"
    save_transcript(_base_transcript(), base_path)
    track_path.write_text(json.dumps(_simple_json3(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "import-subtitle-track",
            "--base-transcript",
            str(base_path),
            "--subtitle-track",
            str(track_path),
            "--output",
            str(output_path),
            "--reviewed-by",
            "codex:test",
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["dry_run"] is True
    assert payload["imported_segment_count"] == 3
    assert payload["schema_ok"] is True
    assert not output_path.exists()


def test_imported_subtitle_track_flows_to_subtitles_and_nle_warning(tmp_path: Path):
    episode_dir = tmp_path / "episodes" / "ep_sub_import"
    episode_dir.mkdir(parents=True)
    transcript_result = import_subtitle_track_transcript(
        base_transcript=_base_transcript(),
        subtitle_payload=_simple_json3(),
        subtitle_track_path=episode_dir / "source_subs" / "track.ja.json3",
        reviewed_by="codex:test",
    )
    transcript = transcript_result.transcript
    transcript_path = episode_dir / "transcript.json"
    save_transcript(transcript, transcript_path)

    edit_pack = build_skeleton(
        "ep_sub_import",
        rights_manifest_path=str(episode_dir / "rights_manifest.json").replace("\\", "/"),
        material_ledger_path=str(episode_dir / "material_ledger.json").replace("\\", "/"),
    )
    cut_result = generate_cut_candidates(
        edit_pack,
        transcript,
        target_duration_seconds=2.0,
        min_duration_seconds=0.5,
        max_duration_seconds=5.0,
        max_candidates=2,
        select_generated=True,
    )
    subtitle_result = generate_subtitle_drafts(
        cut_result.edit_pack,
        transcript,
        selected_cuts_only=True,
    )
    edit_pack_path = episode_dir / "edit_pack.json"
    save_edit_pack(subtitle_result.edit_pack, edit_pack_path)

    export = export_csv_cut_list(
        edit_pack_path=edit_pack_path,
        output_dir=episode_dir / "exports" / "ed10",
        transcript_path=transcript_path,
        base_dir=tmp_path,
    )
    rows = list(csv.DictReader(export["csv_path"].open("r", encoding="utf-8")))
    warnings = " | ".join(export["manifest"]["warnings"])

    assert subtitle_result.subtitle_source_type == "imported_subtitle_track"
    assert subtitle_result.edit_pack["subtitles"][0]["source_type"] == "imported_subtitle_track"
    assert rows[0]["transcript_provider"] == "youtube_subtitles"
    assert rows[0]["transcript_engine"] == "subtitle_track"
    assert rows[0]["transcript_real"] == "true"
    assert "subtitle track transcript review.status is needs_review" in warnings
    assert "real STT transcript review.status" not in warnings


def _base_transcript() -> dict:
    return build_transcript(
        "ep_sub_import",
        source_audio_path="episodes/ep_sub_import/materials/src_audio_001/source.wav",
        material_id="src_audio_001",
        source_audio_sha256="sha",
        source_audio_duration_seconds=10.0,
        source_audio_sample_rate_hz=16000,
        source_audio_channels=1,
        language="ja",
        stt_engine="vosk",
        stt_provider="vosk",
        stt_model="_tmp/stt_models/vosk-model-small-ja-0.22",
        segments=[
            {
                "id": "seg_base_001",
                "start_seconds": 0.0,
                "end_seconds": 2.0,
                "text": "base one",
            },
            {
                "id": "seg_base_002",
                "start_seconds": 2.2,
                "end_seconds": 3.0,
                "text": "base two",
            },
        ],
        real_transcript=True,
    )


def _simple_json3() -> dict:
    return {
        "events": [
            {"tStartMs": 0, "dDurationMs": 1000, "segs": [{"utf8": "もしもし？"}]},
            {"tStartMs": 1200, "dDurationMs": 1000, "segs": [{"utf8": "はじめです！"}]},
            {"tStartMs": 2600, "dDurationMs": 700, "segs": [{"utf8": "なんて？？"}]},
        ]
    }
