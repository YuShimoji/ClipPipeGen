"""OUT-04 real-local editorial sequence tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.integrations.render.editorial_sequence import (
    ARTIFACT_ID,
    EditorialSequenceError,
    build_editorial_sequence,
)


def test_build_editorial_sequence_writes_ordered_two_cut_surface(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    runner = FakeRunner(output_duration=11.0)

    result = _build(tmp_path, inputs, runner=runner)
    readback = result["readback"]

    assert readback["artifact_id"] == ARTIFACT_ID
    assert readback["ordered_cut_ids"] == ["cut_001", "cut_002"]
    assert readback["transition_type"] == "hard_cut"
    assert readback["expected_duration_seconds"] == 11.0
    assert [item["sequence_start_seconds"] for item in readback["timeline"]] == [0.0, 6.0]
    assert [item["sequence_end_seconds"] for item in readback["timeline"]] == [6.0, 11.0]
    assert [item["sequence_start_seconds"] for item in readback["subtitles"]] == [0.0, 6.0]
    assert [item["sequence_end_seconds"] for item in readback["subtitles"]] == [6.0, 11.0]
    assert readback["render"]["media"]["video_codec"] == "h264"
    assert readback["render"]["media"]["audio_codec"] == "aac"
    assert readback["boundaries"]["rights_status"] == "pending"
    assert readback["boundaries"]["production_acceptance"] is False
    assert readback["boundaries"]["public_ready"] is False

    html = result["index_path"].read_text(encoding="utf-8")
    assert html.count("<video ") == 1
    assert "assets/editorial_sequence.mp4" in html
    assert "カット境界" in html
    assert "今回の確認" in html
    assert "card-grid" not in html
    assert "<details>" in html
    assert "-Serve" in result["open_path"].read_text(encoding="utf-8")
    assert str(tmp_path) not in result["readback_path"].read_text(encoding="utf-8")

    filter_graph = runner.render_commands[0][runner.render_commands[0].index("-filter_complex") + 1]
    assert "trim=start=1:end=7" in filter_graph
    assert "trim=start=10:end=15" in filter_graph
    assert filter_graph.index("trim=start=1:end=7") < filter_graph.index("trim=start=10:end=15")
    assert "concat=n=2:v=1:a=1" in filter_graph


def test_build_editorial_sequence_supports_ordered_three_cuts(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    runner = FakeRunner(output_duration=15.0)

    result = _build(
        tmp_path,
        inputs,
        cut_ids=["cut_001", "cut_002", "cut_003"],
        runner=runner,
    )

    timeline = result["readback"]["timeline"]
    assert [item["id"] for item in timeline] == ["cut_001", "cut_002", "cut_003"]
    assert [item["sequence_start_seconds"] for item in timeline] == [0.0, 6.0, 11.0]
    assert timeline[-1]["sequence_end_seconds"] == 15.0
    filter_graph = runner.render_commands[0][runner.render_commands[0].index("-filter_complex") + 1]
    assert "concat=n=3:v=1:a=1" in filter_graph


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("final_cut_decision", "reject", "keep/accepted"),
        ("context_status", "needs_review", "context must be passed"),
    ],
)
def test_build_editorial_sequence_rejects_ineligible_decision(
    tmp_path: Path, field: str, value: str, match: str
):
    inputs = _write_inputs(tmp_path)
    packet = _read(inputs["decisions"])
    packet["decisions"][1][field] = value
    _write_json(inputs["decisions"], packet)

    with pytest.raises(EditorialSequenceError, match=match):
        _build(tmp_path, inputs)


def test_build_editorial_sequence_rejects_edit_pack_needs_review(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    edit_pack = _read(inputs["episode"] / "edit_pack.json")
    edit_pack["cut_candidates"][1]["context_check"]["status"] = "needs_review"
    _write_json(inputs["episode"] / "edit_pack.json", edit_pack)

    with pytest.raises(EditorialSequenceError, match="context must be passed"):
        _build(tmp_path, inputs)


def test_build_editorial_sequence_rejects_missing_source_segment(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    transcript = _read(inputs["episode"] / "transcript.json")
    transcript["segments"] = [
        item for item in transcript["segments"] if item["id"] != "seg_2"
    ]
    _write_json(inputs["episode"] / "transcript.json", transcript)

    with pytest.raises(EditorialSequenceError, match="source segment is missing"):
        _build(tmp_path, inputs)


def test_build_editorial_sequence_rejects_decision_duration_mismatch(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    packet = _read(inputs["decisions"])
    packet["decisions"][0]["duration_seconds"] = 5.0
    _write_json(inputs["decisions"], packet)

    with pytest.raises(EditorialSequenceError, match="duration mismatch"):
        _build(tmp_path, inputs)


def test_build_editorial_sequence_rejects_subtitle_outside_owning_cut(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    edit_pack = _read(inputs["episode"] / "edit_pack.json")
    edit_pack["subtitles"][0]["end_seconds"] = 7.5
    _write_json(inputs["episode"] / "edit_pack.json", edit_pack)

    with pytest.raises(EditorialSequenceError, match="outside its owning cut"):
        _build(tmp_path, inputs)


def test_build_editorial_sequence_rejects_subtitle_text_mismatch(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    edit_pack = _read(inputs["episode"] / "edit_pack.json")
    edit_pack["subtitles"][1]["text"] = "different text"
    _write_json(inputs["episode"] / "edit_pack.json", edit_pack)

    with pytest.raises(EditorialSequenceError, match="does not match linked transcript"):
        _build(tmp_path, inputs)


@pytest.mark.parametrize(("target", "stream"), [("source_video", "video"), ("source_audio", "audio")])
def test_build_editorial_sequence_rejects_missing_source_stream(
    tmp_path: Path, target: str, stream: str
):
    inputs = _write_inputs(tmp_path)
    runner = FakeRunner(output_duration=11.0, missing_source_stream=target)

    with pytest.raises(EditorialSequenceError, match=f"missing required {stream} stream"):
        _build(tmp_path, inputs, runner=runner)


def test_build_editorial_sequence_rejects_source_window_beyond_duration(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    runner = FakeRunner(output_duration=11.0, source_duration=14.0)

    with pytest.raises(EditorialSequenceError, match="does not contain the selected media window"):
        _build(tmp_path, inputs, runner=runner)


@pytest.mark.parametrize("missing", ["video", "audio"])
def test_build_editorial_sequence_rejects_missing_output_stream(tmp_path: Path, missing: str):
    inputs = _write_inputs(tmp_path)
    runner = FakeRunner(output_duration=11.0, missing_output_stream=missing)

    with pytest.raises(EditorialSequenceError, match="must contain video and audio"):
        _build(tmp_path, inputs, runner=runner)


def test_build_editorial_sequence_rejects_output_duration_mismatch(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    runner = FakeRunner(output_duration=10.0)

    with pytest.raises(EditorialSequenceError, match="duration mismatch"):
        _build(tmp_path, inputs, runner=runner)


def test_build_editorial_sequence_rejects_fixture_material_provenance(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    ledger = _read(inputs["episode"] / "material_ledger.json")
    ledger["materials"][0]["registered_by"] = "tool:fixture_video"
    _write_json(inputs["episode"] / "material_ledger.json", ledger)

    with pytest.raises(EditorialSequenceError, match="real acquisition route"):
        _build(tmp_path, inputs)


def test_build_editorial_sequence_rejects_material_hash_mismatch(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    ledger = _read(inputs["episode"] / "material_ledger.json")
    ledger["materials"][1]["hash_sha256"] = "0" * 64
    _write_json(inputs["episode"] / "material_ledger.json", ledger)

    with pytest.raises(EditorialSequenceError, match="material hash mismatch"):
        _build(tmp_path, inputs)


@pytest.mark.parametrize("cut_ids", [["../escape", "cut_002"], ["cut_001", "cut_001"]])
def test_build_editorial_sequence_rejects_unsafe_or_duplicate_ids(
    tmp_path: Path, cut_ids: list[str]
):
    inputs = _write_inputs(tmp_path)
    match = "unsafe path characters" if "../escape" in cut_ids else "must be unique"

    with pytest.raises(EditorialSequenceError, match=match):
        _build(tmp_path, inputs, cut_ids=cut_ids)


def test_build_editorial_sequence_rejects_protected_or_non_dedicated_output(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    protected = inputs["episode"] / "review" / "human_preview_session"

    with pytest.raises(EditorialSequenceError, match="dedicated episode/review/out04"):
        _build(tmp_path, inputs, output=protected)


def test_build_editorial_sequence_rejects_output_containing_input(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    output = inputs["episode"] / "review" / "out04_input_overlap"
    output.mkdir()
    decision = output / "decisions.json"
    decision.write_bytes(inputs["decisions"].read_bytes())
    inputs["decisions"] = decision

    with pytest.raises(EditorialSequenceError, match="must not overlap an input file"):
        _build(tmp_path, inputs, output=output)


def test_build_editorial_sequence_is_deterministic_and_preserves_out03(tmp_path: Path):
    inputs = _write_inputs(tmp_path)
    out03 = inputs["episode"] / "review" / "out03_existing"
    out03.mkdir()
    sentinel = out03 / "proof_readback.json"
    sentinel.write_bytes(b"accepted-out03-evidence")
    out03_before = sentinel.read_bytes()
    runner = FakeRunner(output_duration=11.0)

    first = _build(tmp_path, inputs, runner=runner)
    first_files = {
        path.name: path.read_bytes()
        for path in (
            first["video_path"],
            first["subtitle_path"],
            first["readback_path"],
            first["index_path"],
            first["open_path"],
            first["serve_path"],
        )
    }
    second = _build(tmp_path, inputs, runner=runner)
    second_files = {
        path.name: path.read_bytes()
        for path in (
            second["video_path"],
            second["subtitle_path"],
            second["readback_path"],
            second["index_path"],
            second["open_path"],
            second["serve_path"],
        )
    }

    assert second_files == first_files
    assert sentinel.read_bytes() == out03_before


def test_build_editorial_sequence_cli_is_dispatched():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "build-editorial-sequence", "--help"],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "--cut-id" in result.stdout
    assert "--cut-decision-readback" in result.stdout


def _build(
    tmp_path: Path,
    inputs: dict[str, Path],
    *,
    cut_ids: list[str] | None = None,
    output: Path | None = None,
    runner: "FakeRunner | None" = None,
):
    return build_editorial_sequence(
        episode_dir=inputs["episode"],
        output_dir=output or inputs["output"],
        cut_ids=cut_ids or ["cut_001", "cut_002"],
        cut_decision_readback_path=inputs["decisions"],
        source_video_material_id="src_video",
        source_audio_material_id="src_audio",
        ffmpeg_path="ffmpeg",
        ffprobe_path="ffprobe",
        base_dir=tmp_path,
        runner=runner or FakeRunner(output_duration=11.0),
    )


def _write_inputs(tmp_path: Path) -> dict[str, Path]:
    episode = tmp_path / "episodes" / "ep"
    review = episode / "review" / "source"
    materials = episode / "materials"
    review.mkdir(parents=True)
    materials.mkdir()
    source_video = materials / "source_video.mp4"
    source_audio = materials / "source_audio.wav"
    source_video.write_bytes(b"real-source-video")
    source_audio.write_bytes(b"real-source-audio")

    cuts = [
        ("cut_001", 1.0, 7.0, "seg_1", "sub_1", "字幕 1"),
        ("cut_002", 10.0, 15.0, "seg_2", "sub_2", "字幕 2"),
        ("cut_003", 20.0, 24.0, "seg_3", "sub_3", "字幕 3"),
    ]
    _write_json(
        episode / "edit_pack.json",
        {
            "episode_id": "ep",
            "selected_cut_ids": [item[0] for item in cuts],
            "cut_candidates": [
                {
                    "id": cut_id,
                    "start_seconds": start,
                    "end_seconds": end,
                    "source_segment_ids": [segment_id],
                    "context_check": {"status": "passed"},
                }
                for cut_id, start, end, segment_id, _, _ in cuts
            ],
            "subtitles": [
                {
                    "id": subtitle_id,
                    "cut_id": cut_id,
                    "start_seconds": start,
                    "end_seconds": end,
                    "text": text,
                    "source_type": "imported_subtitle_track",
                    "source_segment_ids": [segment_id],
                }
                for cut_id, start, end, segment_id, subtitle_id, text in cuts
            ],
        },
    )
    _write_json(
        episode / "transcript.json",
        {
            "episode_id": "ep",
            "stt": {
                "engine": "subtitle_track",
                "provider": "youtube_subtitles",
                "real_transcript": True,
            },
            "review": {"status": "needs_review"},
            "segments": [
                {
                    "id": segment_id,
                    "start_seconds": start,
                    "end_seconds": end,
                    "text": text,
                    "review_status": "accepted",
                }
                for _, start, end, segment_id, _, text in cuts
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
    _write_json(episode / "rights_manifest.json", {"compliance_check": {"status": "pending"}})
    decisions = review / "decisions.json"
    _write_json(
        decisions,
        {
            "decisions": [
                {
                    "cut_id": cut_id,
                    "final_cut_decision": "keep",
                    "context_status": "passed",
                    "duration_seconds": end - start,
                    "decision_reason": "retained coherent cut",
                }
                for cut_id, start, end, _, _, _ in cuts
            ]
        },
    )
    return {
        "episode": episode,
        "decisions": decisions,
        "output": episode / "review" / "out04_test",
    }


class FakeRunner:
    def __init__(
        self,
        *,
        output_duration: float,
        source_duration: float = 60.0,
        missing_source_stream: str | None = None,
        missing_output_stream: str | None = None,
    ) -> None:
        self.output_duration = output_duration
        self.source_duration = source_duration
        self.missing_source_stream = missing_source_stream
        self.missing_output_stream = missing_output_stream
        self.render_commands: list[list[str]] = []

    def __call__(self, args, *, capture_output: bool, text: bool, timeout: int):
        if "-version" in args:
            return subprocess.CompletedProcess(args, 0, stdout=f"{args[0]} test\n", stderr="")
        if "-filter_complex" in args:
            self.render_commands.append(list(args))
            Path(args[-1]).write_bytes(b"deterministic-editorial-sequence")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="render passed")

        input_path = Path(args[-1])
        if input_path.name == "source_video.mp4":
            streams = [] if self.missing_source_stream == "source_video" else [
                {
                    "codec_type": "video",
                    "codec_name": "av1",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "30/1",
                }
            ]
            duration = self.source_duration
        elif input_path.name == "source_audio.wav":
            streams = [] if self.missing_source_stream == "source_audio" else [
                {"codec_type": "audio", "codec_name": "pcm_s16le"}
            ]
            duration = self.source_duration
        else:
            streams = []
            if self.missing_output_stream != "video":
                streams.append(
                    {
                        "codec_type": "video",
                        "codec_name": "h264",
                        "width": 1920,
                        "height": 1080,
                        "avg_frame_rate": "30/1",
                    }
                )
            if self.missing_output_stream != "audio":
                streams.append({"codec_type": "audio", "codec_name": "aac"})
            duration = self.output_duration
        payload = {
            "streams": streams,
            "format": {"duration": str(duration), "format_name": "mov,mp4"},
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
