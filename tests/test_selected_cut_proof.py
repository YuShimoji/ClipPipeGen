"""OUT-03 real-local selected-cut proof tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from src.integrations.render.selected_cut_proof import (
    ARTIFACT_ID,
    SelectedCutProofError,
    build_selected_cut_proof,
)


def test_build_selected_cut_proof_writes_one_playable_real_review_surface(
    tmp_path: Path,
):
    inputs = _write_inputs(tmp_path)

    result = _build(tmp_path, inputs)

    readback = result["readback"]
    assert readback["artifact_id"] == ARTIFACT_ID
    assert readback["source_class"] == "real_local_retained_source_media"
    assert readback["selected_cut"] == {
        "id": "cut_002",
        "start_seconds": 1.0,
        "end_seconds": 3.0,
        "duration_seconds": 2.0,
        "source_segment_ids": ["seg_1", "seg_2"],
        "context_status": "passed",
    }
    assert readback["transcript"]["real_transcript"] is True
    assert readback["transcript"]["provider"] == "youtube_subtitles"
    assert [item["id"] for item in readback["subtitles"]] == ["sub_1", "sub_2"]
    assert readback["proof"]["duration_matches_selected_cut"] is True
    assert readback["proof"]["media"]["video_codec"] == "h264"
    assert readback["boundaries"]["rights_status"] == "pending"
    assert readback["boundaries"]["production_candidate"] is False
    assert readback["boundaries"]["public_ready"] is False
    assert result["proof_asset_path"].read_bytes() == inputs["proof_video"].read_bytes()

    html = result["index_path"].read_text(encoding="utf-8")
    assert html.count("<video ") == 1
    assert "controls" in html
    assert 'src="assets/cut_002.mp4"' in html
    assert "選択カット" in html
    assert "字幕 1" in html
    assert "字幕 2" in html
    assert "production_candidate=false" in html
    assert "<details>" in html
    assert "-Serve" in result["open_path"].read_text(encoding="utf-8")

    serialized = result["readback_path"].read_text(encoding="utf-8")
    assert str(tmp_path) not in serialized
    assert readback["review_entrypoint"].endswith("/index.html")
    assert readback["machine_readback"].endswith("/proof_readback.json")


def test_build_selected_cut_proof_is_deterministic(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    first = _build(tmp_path, inputs)
    paths = [
        first["readback_path"],
        first["index_path"],
        first["open_path"],
        first["serve_path"],
        first["proof_asset_path"],
    ]
    first_bytes = {path.name: path.read_bytes() for path in paths}

    second = _build(tmp_path, inputs)
    second_paths = [
        second["readback_path"],
        second["index_path"],
        second["open_path"],
        second["serve_path"],
        second["proof_asset_path"],
    ]

    assert {path.name: path.read_bytes() for path in second_paths} == first_bytes


def test_build_selected_cut_proof_rejects_fixture_transcript(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    transcript = _read(inputs["episode"] / "transcript.json")
    transcript["stt"]["real_transcript"] = False
    transcript["stt"]["provider"] = "fake"
    _write_json(inputs["episode"] / "transcript.json", transcript)

    with pytest.raises(SelectedCutProofError, match="real_transcript"):
        _build(tmp_path, inputs)


def test_build_selected_cut_proof_rejects_unapproved_transcript_provider(
    tmp_path: Path,
):
    inputs = _write_inputs(tmp_path)
    transcript = _read(inputs["episode"] / "transcript.json")
    transcript["stt"]["provider"] = "fixture_v2"
    _write_json(inputs["episode"] / "transcript.json", transcript)

    with pytest.raises(SelectedCutProofError, match="allowed real source"):
        _build(tmp_path, inputs)


def test_build_selected_cut_proof_rejects_subtitle_outside_cut(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    edit_pack = _read(inputs["episode"] / "edit_pack.json")
    edit_pack["subtitles"][1]["end_seconds"] = 3.5
    _write_json(inputs["episode"] / "edit_pack.json", edit_pack)

    with pytest.raises(SelectedCutProofError, match="outside selected cut"):
        _build(tmp_path, inputs)


def test_build_selected_cut_proof_rejects_unlinked_proof_video(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    source = _read(inputs["proof_readback"])
    source["per_cut_visual_assessment"][0]["visual_proof_video_artifact_path"] = (
        "episodes/ep/review/different.mp4"
    )
    _write_json(inputs["proof_readback"], source)

    with pytest.raises(SelectedCutProofError, match="different video"):
        _build(tmp_path, inputs)


def test_build_selected_cut_proof_rejects_cut_id_path_traversal(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    edit_pack = _read(inputs["episode"] / "edit_pack.json")
    edit_pack["selected_cut_ids"] = ["../escape"]
    edit_pack["cut_candidates"][0]["id"] = "../escape"
    edit_pack["subtitles"][0]["cut_id"] = "../escape"
    edit_pack["subtitles"][1]["cut_id"] = "../escape"
    _write_json(inputs["episode"] / "edit_pack.json", edit_pack)

    with pytest.raises(SelectedCutProofError, match="unsafe path characters"):
        build_selected_cut_proof(
            episode_dir=inputs["episode"],
            output_dir=inputs["output"],
            cut_id="../escape",
            proof_video_path=inputs["proof_video"],
            proof_source_readback_path=inputs["proof_readback"],
            source_video_material_id="src_video",
            source_audio_material_id="src_audio",
            ffprobe_path="ffprobe",
            base_dir=tmp_path,
            runner=_fake_runner,
        )


def test_build_selected_cut_proof_rejects_non_dedicated_output(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    protected = inputs["episode"] / "review" / "human_preview_session"

    with pytest.raises(SelectedCutProofError, match="dedicated review/out03"):
        build_selected_cut_proof(
            episode_dir=inputs["episode"],
            output_dir=protected,
            cut_id="cut_002",
            proof_video_path=inputs["proof_video"],
            proof_source_readback_path=inputs["proof_readback"],
            source_video_material_id="src_video",
            source_audio_material_id="src_audio",
            ffprobe_path="ffprobe",
            base_dir=tmp_path,
            runner=_fake_runner,
        )


def test_build_selected_cut_proof_rejects_output_containing_proof_inputs(
    tmp_path: Path,
):
    inputs = _write_inputs(tmp_path)
    proof_output = inputs["episode"] / "review" / "out03_source"
    proof_output.mkdir()
    proof_video = proof_output / "cut_002.mp4"
    proof_readback = proof_output / "representative_visual_proof_report.json"
    proof_video.write_bytes(inputs["proof_video"].read_bytes())
    source = _read(inputs["proof_readback"])
    source["per_cut_visual_assessment"][0]["visual_proof_video_artifact_path"] = (
        proof_video.relative_to(tmp_path).as_posix()
    )
    _write_json(proof_readback, source)

    with pytest.raises(SelectedCutProofError, match="must not contain proof inputs"):
        build_selected_cut_proof(
            episode_dir=inputs["episode"],
            output_dir=proof_output,
            cut_id="cut_002",
            proof_video_path=proof_video,
            proof_source_readback_path=proof_readback,
            source_video_material_id="src_video",
            source_audio_material_id="src_audio",
            ffprobe_path="ffprobe",
            base_dir=tmp_path,
            runner=_fake_runner,
        )


def test_build_selected_cut_proof_rejects_fixture_subtitle_source(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    edit_pack = _read(inputs["episode"] / "edit_pack.json")
    edit_pack["subtitles"][0]["source_type"] = "fixture_v2"
    _write_json(inputs["episode"] / "edit_pack.json", edit_pack)

    with pytest.raises(SelectedCutProofError, match="source_type"):
        _build(tmp_path, inputs)


def test_build_selected_cut_proof_requires_real_material_provenance(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    ledger = _read(inputs["episode"] / "material_ledger.json")
    ledger["materials"][0]["registered_by"] = "tool:fixture_video"
    _write_json(inputs["episode"] / "material_ledger.json", ledger)

    with pytest.raises(SelectedCutProofError, match="real acquisition route"):
        _build(tmp_path, inputs)


def test_build_selected_cut_proof_requires_recorded_material_hash(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    ledger = _read(inputs["episode"] / "material_ledger.json")
    ledger["materials"][0].pop("hash_sha256")
    _write_json(inputs["episode"] / "material_ledger.json", ledger)

    with pytest.raises(SelectedCutProofError, match="recorded hash is required"):
        _build(tmp_path, inputs)


def _build(tmp_path: Path, inputs: dict[str, Path]):
    return build_selected_cut_proof(
        episode_dir=inputs["episode"],
        output_dir=inputs["output"],
        cut_id="cut_002",
        proof_video_path=inputs["proof_video"],
        proof_source_readback_path=inputs["proof_readback"],
        source_video_material_id="src_video",
        source_audio_material_id="src_audio",
        ffprobe_path="ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )


def _write_inputs(tmp_path: Path) -> dict[str, Path]:
    episode = tmp_path / "episodes" / "ep"
    review = episode / "review" / "source"
    materials = episode / "materials"
    review.mkdir(parents=True)
    materials.mkdir()
    source_video = materials / "source_video.mp4"
    source_audio = materials / "source_audio.wav"
    proof_video = review / "cut_002.mp4"
    source_video.write_bytes(b"real-source-video")
    source_audio.write_bytes(b"real-source-audio")
    proof_video.write_bytes(b"diagnostic-proof-video")

    _write_json(
        episode / "edit_pack.json",
        {
            "episode_id": "ep",
            "selected_cut_ids": ["cut_002"],
            "cut_candidates": [
                {
                    "id": "cut_002",
                    "start_seconds": 1.0,
                    "end_seconds": 3.0,
                    "source_segment_ids": ["seg_1", "seg_2"],
                    "context_check": {"status": "passed"},
                }
            ],
            "subtitles": [
                {
                    "id": "sub_1",
                    "cut_id": "cut_002",
                    "start_seconds": 1.0,
                    "end_seconds": 2.0,
                    "text": "字幕 1",
                    "source_type": "imported_subtitle_track",
                    "source_segment_ids": ["seg_1"],
                },
                {
                    "id": "sub_2",
                    "cut_id": "cut_002",
                    "start_seconds": 2.0,
                    "end_seconds": 3.0,
                    "text": "字幕 2",
                    "source_type": "imported_subtitle_track",
                    "source_segment_ids": ["seg_2"],
                },
            ],
        },
    )
    _write_json(
        episode / "transcript.json",
        {
            "episode_id": "ep",
            "language": "ja",
            "stt": {
                "engine": "subtitle_track",
                "provider": "youtube_subtitles",
                "real_transcript": True,
            },
            "review": {"status": "needs_review"},
            "segments": [
                {"id": "seg_1", "start_seconds": 1.0, "end_seconds": 2.0, "text": "字幕 1"},
                {"id": "seg_2", "start_seconds": 2.0, "end_seconds": 3.0, "text": "字幕 2"},
            ],
        },
    )
    _write_json(
        episode / "material_ledger.json",
        {
            "materials": [
                {
                    "id": "src_video",
                    "kind": "source_video",
                    "file_path": source_video.relative_to(tmp_path).as_posix(),
                    "hash_sha256": _hash(source_video),
                    "registered_by": "tool:asset_fetch_local_video",
                },
                {
                    "id": "src_audio",
                    "kind": "source_audio",
                    "file_path": source_audio.relative_to(tmp_path).as_posix(),
                    "hash_sha256": _hash(source_audio),
                    "registered_by": "tool:asset_fetch_local_audio",
                },
            ]
        },
    )
    _write_json(
        episode / "rights_manifest.json",
        {"compliance_check": {"status": "pending"}},
    )
    proof_readback = review / "representative_visual_proof_report.json"
    _write_json(
        proof_readback,
        {
            "per_cut_visual_assessment": [
                {
                    "cut_id": "cut_002",
                    "visual_proof_status": "available_diagnostic_subtitle_overlay",
                    "visual_proof_video_artifact_path": proof_video.relative_to(
                        tmp_path
                    ).as_posix(),
                    "source_used": "diagnostic_subtitle_overlay_render_from_material_ledger",
                    "subtitle_overlay_present": True,
                }
            ]
        },
    )
    return {
        "episode": episode,
        "output": episode / "review" / "out03_test",
        "proof_video": proof_video,
        "proof_readback": proof_readback,
    }


def _fake_runner(args, *, capture_output: bool, text: bool, timeout: int):
    if "-version" in args:
        return subprocess.CompletedProcess(args, 0, stdout="ffprobe test\n", stderr="")
    payload = {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "h264",
                "width": 1920,
                "height": 1080,
                "avg_frame_rate": "30/1",
            },
            {"codec_type": "audio", "codec_name": "aac"},
        ],
        "format": {"duration": "2.000", "format_name": "mov,mp4"},
    }
    return subprocess.CompletedProcess(
        args,
        0,
        stdout=json.dumps(payload),
        stderr="",
    )


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
