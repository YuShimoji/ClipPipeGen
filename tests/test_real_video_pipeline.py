from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src.cli import main as cli_main
from src.cli import build_real_video as cli_build_real_video
from src.integrations.render import real_video_pipeline as pipeline


def test_cli_dispatch_registers_out12_one_command() -> None:
    assert "build-real-video" in cli_main.SUBCOMMANDS


def test_cli_orchestrates_resume_arguments(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_build(**kwargs):
        captured.update(kwargs)
        return {
            "artifact_id": "clip-out12-test",
            "state": pipeline.READY_STATE,
            "source_identity": "local:test",
            "duration_seconds": 200.0,
            "cut_count": 8,
            "final_video": tmp_path / "final_video.mp4",
            "review_index": tmp_path / "review" / "index.html",
            "resume": True,
        }

    monkeypatch.setattr(cli_build_real_video, "build_real_video", _fake_build)

    code = cli_build_real_video.run(
        [
            "--source",
            str(tmp_path / "source.mp4"),
            "--output-dir",
            str(tmp_path / "out"),
            "--profile",
            "long-form",
            "--target-duration",
            "240",
            "--resume",
            "--format",
            "json",
        ]
    )

    assert code == 0
    assert captured["resume"] is True
    assert captured["force"] is False
    assert captured["target_duration_seconds"] == 240.0


def test_content_fingerprint_is_stable_and_content_derived() -> None:
    first = pipeline.content_fingerprint({"source": "a", "target": 300})
    same = pipeline.content_fingerprint({"target": 300, "source": "a"})
    changed = pipeline.content_fingerprint({"source": "b", "target": 300})

    assert first == same
    assert first != changed
    assert len(first) == 64


def test_full_source_timeline_is_scene_partitioned_and_traceable() -> None:
    timeline = pipeline.plan_timeline(
        source_identity="youtube:real-source",
        source_duration_seconds=260.644,
        scene_boundaries=[23.0, 49.5, 73.0, 97.0, 121.0, 144.5, 168.0, 191.0, 215.0, 238.0],
        target_duration_seconds=300.0,
    )

    assert timeline["source_duration_constraint"] is True
    assert timeline["selection_mode"] == "full_source_scene_boundary_partition"
    assert 8 <= timeline["cut_count"] <= 20
    assert timeline["semantic_section_count"] == 3
    assert timeline["cuts"][0]["source_in_seconds"] == 0.0
    assert timeline["cuts"][-1]["source_out_seconds"] == pytest.approx(260.644)
    assert timeline["cuts"][-1]["output_out_seconds"] == pytest.approx(260.644)
    pipeline.validate_timeline_ir(timeline)


def test_review_cut_table_scrolls_within_mobile_viewport() -> None:
    timeline = pipeline.plan_timeline(
        source_identity="local:real",
        source_duration_seconds=200.0,
        scene_boundaries=[],
        target_duration_seconds=200.0,
    )
    html = pipeline.render_review_html(
        timeline,
        {
            "source_identity": "local:real",
            "caption_mode": "none",
            "rights": {"status": "pending"},
        },
        {
            "media": {
                "duration_seconds": 200.0,
                "resolution": "1920x1080",
                "sha256": "a" * 64,
            },
            "checks": {"full_decode": True},
        },
    )

    assert "box-sizing:border-box" in html
    assert "overflow-x:auto" in html
    assert "white-space:nowrap" in html


def test_shorter_target_samples_source_in_chronological_order() -> None:
    timeline = pipeline.plan_timeline(
        source_identity="local:real",
        source_duration_seconds=600.0,
        scene_boundaries=[],
        target_duration_seconds=300.0,
    )

    assert timeline["selection_mode"] == "chronological_uniform_semantic_thread_sampling"
    assert timeline["output_duration_seconds"] == pytest.approx(300.0)
    assert all(
        current["source_in_seconds"] >= previous["source_out_seconds"]
        for previous, current in zip(timeline["cuts"], timeline["cuts"][1:])
    )
    assert timeline["cuts"][-1]["source_out_seconds"] <= 600.0


def test_timeline_validation_rejects_output_gap() -> None:
    timeline = pipeline.plan_timeline(
        source_identity="local:real",
        source_duration_seconds=240.0,
        scene_boundaries=[],
        target_duration_seconds=240.0,
    )
    timeline["cuts"][1]["output_in_seconds"] += 1.0

    with pytest.raises(pipeline.RealVideoPipelineError, match="invalid Timeline IR cut"):
        pipeline.validate_timeline_ir(timeline)


def test_caption_remap_merges_contiguous_cut_split_and_clips_overlap() -> None:
    cuts = [
        {
            "cut_id": "cut_001",
            "source_in_seconds": 0.0,
            "source_out_seconds": 5.0,
            "output_in_seconds": 0.0,
            "output_out_seconds": 5.0,
        },
        {
            "cut_id": "cut_002",
            "source_in_seconds": 5.0,
            "source_out_seconds": 10.0,
            "output_in_seconds": 5.0,
            "output_out_seconds": 10.0,
        },
    ]
    events = [
        {
            "event_id": "event_000001",
            "source_start_seconds": 4.5,
            "source_end_seconds": 5.5,
            "text": "authority text",
            "text_sha256": "a" * 64,
        },
        {
            "event_id": "event_000002",
            "source_start_seconds": 5.25,
            "source_end_seconds": 6.0,
            "text": "overlap text",
            "text_sha256": "b" * 64,
        },
    ]

    rows = pipeline.remap_caption_events(events, cuts)

    assert len(rows) == 2
    assert rows[0]["output_start_seconds"] == 4.5
    assert rows[0]["output_end_seconds"] == 5.5
    assert rows[0]["split_at_cut_boundary"] is True
    assert rows[1]["output_start_seconds"] == 5.5
    assert rows[1]["adjustment"] == "overlap_clipped_to_previous_output_end"


def test_caption_readback_hides_text_for_native_baked_authority() -> None:
    rows = [
        {
            "caption_id": "caption_0001",
            "cut_id": "cut_001",
            "source_start_seconds": 1.0,
            "source_end_seconds": 2.0,
            "output_start_seconds": 1.0,
            "output_end_seconds": 2.0,
            "text": "do not infer lyric meaning",
            "text_sha256": "c" * 64,
            "split_at_cut_boundary": False,
            "adjustment": None,
        }
    ]

    readback = pipeline.build_caption_readback(
        caption_mode="native_baked",
        caption_authority={"source": "official_json3"},
        caption_rows=rows,
        source_caption_sha256="d" * 64,
        timeline_duration_seconds=10.0,
    )

    assert readback["status"] == "passed"
    assert readback["double_display_rejected"] is True
    assert "text" not in readback["items"][0]
    assert readback["items"][0]["text_sha256"] == "c" * 64


def test_official_sidecar_srt_has_output_timestamps() -> None:
    text = pipeline.render_srt(
        [
            {
                "output_start_seconds": 1.25,
                "output_end_seconds": 2.5,
                "text": "exact authority",
            }
        ]
    )

    assert "00:00:01,250 --> 00:00:02,500" in text
    assert "exact authority" in text


def test_render_filter_contains_each_real_cut_and_concat() -> None:
    timeline = pipeline.plan_timeline(
        source_identity="youtube:real",
        source_duration_seconds=200.0,
        scene_boundaries=[],
        target_duration_seconds=200.0,
    )
    script = pipeline.render_filter_complex(timeline["cuts"])

    assert script.count("[0:v:0]trim=start=") == len(timeline["cuts"])
    assert script.count("[0:a:0]atrim=start=") == len(timeline["cuts"])
    assert f"concat=n={len(timeline['cuts'])}:v=1:a=1" in script
    assert "loudnorm=I=-15:TP=-2.0" in script


def test_direct_renderer_uses_real_cut_filter_and_h264(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    output = tmp_path / "final_video.mp4"
    source.write_bytes(b"real-source")
    timeline = pipeline.plan_timeline(
        source_identity="local:real",
        source_duration_seconds=200.0,
        scene_boundaries=[],
        target_duration_seconds=200.0,
    )
    commands: list[list[str]] = []

    def _runner(command, *, capture_output, text, timeout):
        commands.append(command)
        Path(command[-1]).write_bytes(b"rendered-real-media")
        return subprocess.CompletedProcess(command, 0, "", "")

    result = pipeline.render_timeline(
        source_path=source,
        video_path=output,
        cuts=timeline["cuts"],
        ffmpeg_path="ffmpeg",
        runner=_runner,
    )

    assert result["status"] == "passed"
    assert result["selected_video_encoder"] == "libx264"
    assert output.read_bytes() == b"rendered-real-media"
    assert "-filter_complex_script" in commands[0]
    assert "libx264" in commands[0]
    assert "-shortest" in commands[0]


def test_mapping_coverage_is_complete() -> None:
    timeline = pipeline.plan_timeline(
        source_identity="youtube:real",
        source_duration_seconds=200.0,
        scene_boundaries=[],
        target_duration_seconds=200.0,
    )

    coverage = pipeline.mapping_coverage(timeline)
    assert coverage["coverage_ratio"] == 1.0
    assert pipeline.validate_mapping_coverage(timeline) is True


def test_run_manifest_payload_and_self_integrity(tmp_path: Path) -> None:
    (tmp_path / "final_video.mp4").write_bytes(b"real-media")
    (tmp_path / "timeline_ir.json").write_text("{}\n", encoding="utf-8")
    timeline = pipeline.plan_timeline(
        source_identity="local:real",
        source_duration_seconds=200.0,
        scene_boundaries=[],
        target_duration_seconds=200.0,
    )
    resolved = {
        "source_identity": "local:real",
        "source_sha256": "e" * 64,
        "caption_authority": {"mode": "none"},
    }
    validation = {
        "status": "passed",
        "media": {
            "sha256": pipeline._sha256(tmp_path / "final_video.mp4"),
            "byte_size": 10,
            "duration_seconds": 200.0,
            "resolution": "1920x1080",
        },
    }
    manifest = pipeline.build_run_manifest(
        stage=tmp_path,
        input_fingerprint="f" * 64,
        resolved=resolved,
        timeline=timeline,
        validation=validation,
        review={"index": "review/index.html"},
        stages=[],
    )

    pipeline.validate_run_manifest(tmp_path, manifest)
    assert manifest["file_count"] == 2
    assert manifest["manifest_self_integrity"]["sha256"] == (
        pipeline._canonical_manifest_self_hash(manifest)
    )


def test_resume_verifies_manifest_and_skips_expensive_stages(tmp_path: Path) -> None:
    (tmp_path / "final_video.mp4").write_bytes(b"real-media")
    (tmp_path / "timeline_ir.json").write_text("{}\n", encoding="utf-8")
    timeline = pipeline.plan_timeline(
        source_identity="local:real",
        source_duration_seconds=200.0,
        scene_boundaries=[],
        target_duration_seconds=200.0,
    )
    validation = {
        "status": "passed",
        "media": {
            "sha256": pipeline._sha256(tmp_path / "final_video.mp4"),
            "byte_size": 10,
            "duration_seconds": 200.0,
            "resolution": "1920x1080",
        },
    }
    manifest = pipeline.build_run_manifest(
        stage=tmp_path,
        input_fingerprint="f" * 64,
        resolved={
            "source_identity": "local:real",
            "source_sha256": "e" * 64,
            "caption_authority": {"mode": "none"},
        },
        timeline=timeline,
        validation=validation,
        review={"index": "review/index.html"},
        stages=[],
    )
    (tmp_path / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = pipeline.resume_existing_output(
        output_dir=tmp_path,
        input_fingerprint="f" * 64,
        root=tmp_path,
    )

    assert result["resume"] is True
    assert result["render_executed"] is False
    assert "render" in result["cache_hits"]
    assert (tmp_path / "resume_readback.json").is_file()


def test_machine_readable_failure_state(tmp_path: Path) -> None:
    output = tmp_path / "out"
    pipeline.write_failure_state(
        output_dir=output,
        stage="render",
        message="controlled failure",
        input_fingerprint="a" * 64,
    )

    payload = json.loads((output / "pipeline_failure.json").read_text(encoding="utf-8"))
    assert payload["ready"] is False
    assert payload["failure_stage"] == "render"
