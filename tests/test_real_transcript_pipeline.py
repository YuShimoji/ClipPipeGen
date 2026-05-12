"""ED-07b: real transcript metadata flows through edit/export plumbing."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.pipeline.cut_generation import generate_cut_candidates
from src.pipeline.edit_pack import build_skeleton, save_edit_pack
from src.pipeline.nle_export import export_csv_cut_list
from src.pipeline.subtitle_generation import generate_subtitle_drafts
from src.pipeline.transcript import build_transcript, save_transcript


def test_real_transcript_flows_to_cuts_subtitles_and_nle_export(tmp_path: Path):
    episode_dir = tmp_path / "episodes" / "ep_real_stt"
    material_dir = episode_dir / "materials" / "src_audio_real"
    material_dir.mkdir(parents=True)
    source_audio_path = material_dir / "source.wav"
    source_audio_path.write_bytes(b"placeholder source wav")
    ledger_path = episode_dir / "material_ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "episode_id": "ep_real_stt",
                "materials": [
                    {
                        "id": "src_audio_real",
                        "kind": "source_audio",
                        "file_path": str(source_audio_path).replace("\\", "/"),
                        "hash_sha256": "realsha",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    transcript = build_transcript(
        "ep_real_stt",
        source_audio_path=str(source_audio_path).replace("\\", "/"),
        material_id="src_audio_real",
        source_audio_sha256="realsha",
        source_audio_duration_seconds=1.2,
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
                "end_seconds": 1.2,
                "text": "real source audio can reach the edit export",
                "confidence": 0.82,
            }
        ],
        real_transcript=True,
    )
    transcript_path = episode_dir / "transcript.json"
    save_transcript(transcript, transcript_path)

    edit_pack = build_skeleton(
        "ep_real_stt",
        rights_manifest_path=str(episode_dir / "rights_manifest.json").replace("\\", "/"),
        material_ledger_path=str(ledger_path).replace("\\", "/"),
    )
    cut_result = generate_cut_candidates(
        edit_pack,
        transcript,
        target_duration_seconds=1.0,
        min_duration_seconds=0.5,
        max_duration_seconds=2.0,
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
        output_dir=episode_dir / "exports" / "ed06",
        transcript_path=transcript_path,
        base_dir=tmp_path,
    )

    rows = list(csv.DictReader(export["csv_path"].open("r", encoding="utf-8")))
    manifest = export["manifest"]
    report = export["report_path"].read_text(encoding="utf-8")

    assert cut_result.generated_count == 1
    assert subtitle_result.generated_count == 1
    assert rows[0]["transcript_provider"] == "vosk"
    assert rows[0]["transcript_real"] == "true"
    assert rows[0]["transcript_segment_count"] == "1"
    assert manifest["source_refs"]["transcript"]["real_transcript"] is True
    assert manifest["source_refs"]["transcript"]["source_audio_material_id"] == "src_audio_real"
    assert "real STT transcript is unreviewed" in " | ".join(manifest["warnings"])
    assert "fixture transcript" not in " | ".join(manifest["warnings"])
    assert "Transcript Provenance" in report
    assert "vosk" in report
    assert "real_transcript" in report
