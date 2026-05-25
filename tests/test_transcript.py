"""ED-07: transcript schema and fake transcribe-audio CLI tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.cli.transcribe_audio import _check_vosk_model_language
from src.pipeline.context_check import check_cut_context
from src.pipeline.cut_generation import generate_cut_candidates
from src.pipeline.edit_pack import build_skeleton as build_edit_skeleton
from src.pipeline.material_ledger import compute_sha256
from src.pipeline.subtitle_generation import generate_subtitle_drafts
from src.pipeline.transcript import (
    TranscriptReviewError,
    apply_review_patch,
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
    assert transcript["stt"]["provider"] == "fake"
    assert transcript["stt"]["real_transcript"] is False
    assert transcript["stt"]["segment_count"] == 1
    assert transcript["segment_count"] == 1


def test_real_transcript_metadata_is_readable():
    transcript = build_transcript(
        "ep_tr_real",
        source_audio_path="episodes/ep_tr_real/materials/src_audio/source.wav",
        source_audio_sha256="def456",
        source_audio_duration_seconds=3.2,
        source_audio_sample_rate_hz=16000,
        source_audio_channels=1,
        language="en",
        stt_engine="vosk",
        stt_provider="vosk",
        stt_engine_version="test-vosk",
        stt_model="models/vosk-small",
        stt_params={"model_path": "models/vosk-small"},
        stt_warnings=["real STT plumbing proof only"],
        segments=[
            {
                "start_seconds": 0.0,
                "end_seconds": 1.0,
                "text": "real source audio",
                "confidence": 0.8,
            }
        ],
        real_transcript=True,
    )

    assert validate_transcript(transcript) == []
    assert transcript["source_audio"]["duration_seconds"] == 3.2
    assert transcript["stt"]["provider"] == "vosk"
    assert transcript["stt"]["model"] == "models/vosk-small"
    assert transcript["stt"]["real_transcript"] is True
    assert transcript["stt"]["segment_count"] == 1


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


def test_apply_review_patch_updates_text_status_notes_and_preserves_provenance():
    transcript = build_transcript(
        "ep_review",
        source_audio_path="episodes/ep_review/source.wav",
        source_audio_sha256="sha",
        source_audio_duration_seconds=3.0,
        language="ja",
        stt_engine="vosk",
        stt_provider="vosk",
        stt_model="_tmp/stt_models/vosk-model-small-ja-0.22",
        segments=[
            {"id": "seg_a", "start_seconds": 0.0, "end_seconds": 1.0, "text": "bad a"},
            {"id": "seg_b", "start_seconds": 1.5, "end_seconds": 2.5, "text": "bad b"},
        ],
        real_transcript=True,
    )
    result = apply_review_patch(
        transcript,
        {
            "schema_version": "v1",
            "segments": [
                {
                    "id": "seg_a",
                    "text": "corrected a",
                    "review_status": "accepted",
                    "notes": ["human correction"],
                },
                {"id": "seg_b", "review_status": "needs_fix"},
            ],
            "review": {"status": "needs_review", "notes": ["pass 1"]},
        },
    )

    updated = result.transcript
    assert transcript["segments"][0]["text"] == "bad a"
    assert updated["segments"][0]["text"] == "corrected a"
    assert updated["segments"][0]["review_status"] == "accepted"
    assert updated["segments"][0]["notes"] == ["human correction"]
    assert updated["segments"][1]["review_status"] == "needs_fix"
    assert updated["review"]["status"] == "needs_review"
    assert updated["review"]["notes"] == ["pass 1"]
    assert updated["source_audio"]["sha256"] == "sha"
    assert updated["stt"]["provider"] == "vosk"
    assert result.updated_segment_count == 2
    assert result.segment_review_counts["accepted_count"] == 1
    assert result.segment_review_counts["needs_fix_count"] == 1
    assert result.schema_issues == []


@pytest.mark.parametrize(
    ("patch", "message"),
    [
        (
            {"schema_version": "v1", "segments": [{"id": "missing", "text": "x"}]},
            "unknown segment id",
        ),
        (
            {
                "schema_version": "v1",
                "segments": [
                    {"id": "seg_000001", "review_status": "accepted"},
                    {"id": "seg_000001", "review_status": "rejected"},
                ],
            },
            "duplicate patch segment id",
        ),
        (
            {
                "schema_version": "v1",
                "segments": [{"id": "seg_000001", "review_status": "done"}],
            },
            "review_status",
        ),
        (
            {
                "schema_version": "v1",
                "segments": [
                    {"id": "seg_000001", "text": " ", "review_status": "accepted"}
                ],
            },
            "non-empty",
        ),
    ],
)
def test_apply_review_patch_rejects_unsafe_segment_patches(patch: dict, message: str):
    with pytest.raises(TranscriptReviewError, match=message):
        apply_review_patch(_valid_transcript(), patch)


def test_apply_review_patch_approved_requires_reviewer_and_final_segment_statuses():
    transcript = _valid_transcript()
    with pytest.raises(TranscriptReviewError, match="requires --reviewed-by"):
        apply_review_patch(
            transcript,
            {"schema_version": "v1", "review": {"status": "approved"}},
        )

    with pytest.raises(TranscriptReviewError, match="every segment"):
        apply_review_patch(
            transcript,
            {"schema_version": "v1", "review": {"status": "approved"}},
            reviewed_by="user:reviewer",
        )

    result = apply_review_patch(
        transcript,
        {
            "schema_version": "v1",
            "segments": [{"id": "seg_000001", "review_status": "accepted"}],
            "review": {"status": "approved"},
        },
        reviewed_by="user:reviewer",
    )
    assert result.transcript["review"]["status"] == "approved"
    assert result.transcript["review"]["reviewed_by"] == "user:reviewer"
    assert result.transcript["review"]["reviewed_at"]
    assert result.schema_issues == []


def test_review_transcript_cli_dry_run_does_not_write(tmp_path: Path):
    transcript_path = tmp_path / "transcript.json"
    patch_path = tmp_path / "review_patch.json"
    save_transcript(_valid_transcript(), transcript_path)
    before = transcript_path.read_text(encoding="utf-8")
    patch_path.write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "segments": [
                    {
                        "id": "seg_000001",
                        "text": "corrected from cli",
                        "review_status": "accepted",
                    }
                ],
                "review": {"status": "needs_review"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "review-transcript",
            "--transcript",
            str(transcript_path),
            "--patch",
            str(patch_path),
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
    assert payload["updated_segment_count"] == 1
    assert payload["segment_review_counts"]["accepted_count"] == 1
    assert transcript_path.read_text(encoding="utf-8") == before


def test_review_transcript_cli_rejects_invalid_patch_without_saving(tmp_path: Path):
    transcript_path = tmp_path / "transcript.json"
    patch_path = tmp_path / "bad_review_patch.json"
    save_transcript(_valid_transcript(), transcript_path)
    before = transcript_path.read_text(encoding="utf-8")
    patch_path.write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "segments": [{"id": "missing", "review_status": "accepted"}],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "review-transcript",
            "--transcript",
            str(transcript_path),
            "--patch",
            str(patch_path),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "unknown segment id" in payload["error"]
    assert transcript_path.read_text(encoding="utf-8") == before


def test_reviewed_transcript_statuses_feed_downstream_generation_and_context_check():
    transcript = build_transcript(
        "ep_review_downstream",
        source_audio_path="episodes/ep_review_downstream/source.wav",
        language="en",
        stt_engine="fake",
        segments=[
            {"id": "seg_a", "start_seconds": 0.0, "end_seconds": 1.0, "text": "keep"},
            {"id": "seg_b", "start_seconds": 1.2, "end_seconds": 2.2, "text": "drop"},
            {"id": "seg_c", "start_seconds": 3.0, "end_seconds": 4.0, "text": "fix"},
        ],
    )
    review_result = apply_review_patch(
        transcript,
        {
            "schema_version": "v1",
            "segments": [
                {"id": "seg_a", "review_status": "accepted"},
                {"id": "seg_b", "review_status": "rejected"},
                {"id": "seg_c", "review_status": "needs_fix"},
            ],
            "review": {"status": "needs_review"},
        },
    )
    reviewed = review_result.transcript
    edit_pack = build_edit_skeleton("ep_review_downstream")

    cut_result = generate_cut_candidates(
        edit_pack,
        reviewed,
        target_duration_seconds=1.0,
        min_duration_seconds=0.5,
        max_duration_seconds=2.0,
        gap_threshold_seconds=0.5,
        max_candidates=4,
        select_generated=True,
    )
    assert cut_result.skipped_segments_count == 1
    assert all(
        "seg_b" not in (cut.get("source_segment_ids") or [])
        for cut in cut_result.edit_pack["cut_candidates"]
    )

    subtitle_result = generate_subtitle_drafts(cut_result.edit_pack, reviewed)
    assert subtitle_result.skipped_segments_count == 1
    assert "seg_b" not in subtitle_result.source_segment_ids

    context_result = check_cut_context(
        cut_result.edit_pack,
        reviewed,
        cut_id=next(
            cut["id"]
            for cut in cut_result.edit_pack["cut_candidates"]
            if cut.get("source_segment_ids") == ["seg_c"]
        ),
    )
    assert context_result.needs_review_count == 1
    assert "marked needs_fix" in " ".join(
        context_result.edit_pack["cut_candidates"][-1]["context_check"]["notes"]
    )


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
    assert transcript["stt"]["provider"] == "fake"
    assert transcript["stt"]["real_transcript"] is False
    assert transcript["segments"][0]["text"] == "ここが見どころ"


def test_cli_transcribe_audio_vosk_dry_run_reports_preflight_failure(tmp_path: Path):
    audio_path = tmp_path / "source.wav"
    _write_mono_wav(audio_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "transcribe-audio",
            "--episode-id",
            "ep_tr_cli_vosk",
            "--source-audio",
            str(audio_path),
            "--output",
            str(tmp_path / "transcript.json"),
            "--language",
            "en",
            "--engine",
            "vosk",
            "--model",
            str(tmp_path / "missing-model"),
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["preflight_ok"] is False
    assert payload["provider"] == "vosk"
    assert payload["real_transcript"] is True
    assert any("model directory not found" in issue.lower() for issue in payload["issues"])


def test_vosk_model_language_check_detects_known_model_names():
    en_check = _check_vosk_model_language(
        language="en-US",
        model="_tmp/stt_models/vosk-model-small-en-us-0.15",
    )
    jp_check = _check_vosk_model_language(
        language="ja",
        model="_tmp/stt_models/vosk-model-small-ja-0.22",
    )
    unknown_check = _check_vosk_model_language(language="ja", model="_tmp/stt_models/model")

    assert en_check["status"] == "passed"
    assert en_check["language_primary"] == "en"
    assert en_check["model_language"] == "en"
    assert jp_check["status"] == "passed"
    assert jp_check["model_language"] == "ja"
    assert unknown_check["status"] == "not_inferable"
    assert unknown_check["warnings"]


def test_cli_transcribe_audio_vosk_rejects_inferable_language_model_mismatch(tmp_path: Path):
    audio_path = tmp_path / "source.wav"
    model_path = tmp_path / "vosk-model-small-en-us-0.15"
    transcript_path = tmp_path / "transcript.json"
    model_path.mkdir()
    _write_mono_wav(audio_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "transcribe-audio",
            "--episode-id",
            "ep_tr_cli_vosk_mismatch",
            "--source-audio",
            str(audio_path),
            "--output",
            str(transcript_path),
            "--language",
            "ja",
            "--engine",
            "vosk",
            "--model",
            str(model_path),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "does not match inferred Vosk model language 'en'" in result.stderr
    assert not transcript_path.exists()


def test_cli_transcribe_audio_vosk_dry_run_reports_language_model_mismatch(
    tmp_path: Path,
):
    audio_path = tmp_path / "source.wav"
    model_path = tmp_path / "vosk-model-small-ja-0.22"
    model_path.mkdir()
    _write_mono_wav(audio_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "transcribe-audio",
            "--episode-id",
            "ep_tr_cli_vosk_mismatch",
            "--source-audio",
            str(audio_path),
            "--output",
            str(tmp_path / "transcript.json"),
            "--language",
            "en",
            "--engine",
            "vosk",
            "--model",
            str(model_path),
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["preflight_ok"] is False
    assert payload["language_model_check"]["status"] == "failed"
    assert payload["language_model_check"]["model_language"] == "ja"
    assert any("does not match inferred Vosk model language" in i for i in payload["issues"])


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


def _write_mono_wav(path: Path) -> None:
    import wave

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\0\0" * 1600)
