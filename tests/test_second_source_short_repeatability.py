from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import build_second_source_short_repeatability as out09_cli
from src.integrations.render import second_source_short_repeatability as out09


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path
    episode = root / "episodes" / "second_source_episode"
    review = episode / "review"
    video = episode / "materials" / "video_01" / "source_video.mp4"
    audio = episode / "materials" / "audio_01" / "source.wav"
    video.parent.mkdir(parents=True)
    audio.parent.mkdir(parents=True)
    video.write_bytes(b"real-route-video-fixture")
    audio.write_bytes(b"real-route-audio-fixture")

    rights = episode / "rights_manifest.json"
    ledger = episode / "material_ledger.json"
    base_transcript = episode / "transcript.json"
    captions = episode / "source_captions.en-orig.json3"
    transcript = episode / "transcript_source_captions.json"
    edit_pack = episode / "edit_pack.json"
    _write_json(
        rights,
        {
            "source_video": {
                "url": "https://www.youtube.com/watch?v=SECOND123",
                "title": "Second source title",
            },
            "compliance_check": {"status": "pending"},
        },
    )
    _write_json(
        ledger,
        {
            "materials": [
                {
                    "id": "video_01",
                    "kind": "source_video",
                    "registered_by": "tool:asset_fetch_yt_dlp_video",
                    "file_path": video.relative_to(root).as_posix(),
                    "hash_sha256": out09._sha256(video),
                },
                {
                    "id": "audio_01",
                    "kind": "source_audio",
                    "registered_by": "tool:asset_fetch_yt_dlp_audio",
                    "file_path": audio.relative_to(root).as_posix(),
                    "hash_sha256": out09._sha256(audio),
                },
            ]
        },
    )
    _write_json(
        base_transcript,
        {
            "stt": {"engine": "vosk", "provider": "vosk", "real_transcript": True},
            "segments": [{"id": "vosk_001", "text": "fixture"}],
        },
    )
    _write_json(captions, {"events": [{"tStartMs": 10000, "segs": [{"utf8": "Hello"}]}]})
    segments = [
        {
            "id": "seg_000001",
            "start_seconds": 10.0,
            "end_seconds": 16.0,
            "text": "Hello there this is the setup",
            "review_status": "unreviewed",
        },
        {
            "id": "seg_000002",
            "start_seconds": 16.0,
            "end_seconds": 24.0,
            "text": "this is the middle with a repeated repeated word",
            "review_status": "unreviewed",
        },
        {
            "id": "seg_000003",
            "start_seconds": 24.0,
            "end_seconds": 32.0,
            "text": "and this is the final payoff",
            "review_status": "unreviewed",
        },
    ]
    _write_json(
        transcript,
        {
            "stt": {
                "engine": "subtitle_track",
                "provider": "youtube_subtitles",
                "real_transcript": True,
            },
            "review": {"status": "needs_review"},
            "segments": segments,
        },
    )
    _write_json(
        edit_pack,
        {
            "episode_id": episode.name,
            "cut_candidates": [
                {
                    "id": "cut_001",
                    "start_seconds": 8.0,
                    "end_seconds": 24.0,
                    "context_check": {"status": "passed"},
                },
                {
                    "id": "cut_002",
                    "start_seconds": 22.0,
                    "end_seconds": 34.0,
                    "context_check": {"status": "passed"},
                },
            ],
        },
    )
    roles = {
        "rights_manifest": rights,
        "material_ledger": ledger,
        "base_vosk_transcript": base_transcript,
        "source_caption_track": captions,
        "authoritative_transcript": transcript,
        "edit_pack": edit_pack,
    }
    plan = episode / "out09_candidate_plan_input.json"
    _write_json(
        plan,
        {
            "schema_version": out09.PLAN_SCHEMA_VERSION,
            "artifact_id": out09.ARTIFACT_ID,
            "episode_id": episode.name,
            "source_identity": {
                "platform": "youtube",
                "provider_id": "SECOND123",
                "url": "https://www.youtube.com/watch?v=SECOND123",
                "title": "Second source title",
                "channel": "fixture channel",
            },
            "materials": {
                "source_video": {
                    "material_id": "video_01",
                    "sha256": out09._sha256(video),
                },
                "source_audio": {
                    "material_id": "audio_01",
                    "sha256": out09._sha256(audio),
                },
            },
            "expected_inputs": [
                {
                    "role": role,
                    "path": path.relative_to(root).as_posix(),
                    "sha256": out09._sha256(path),
                }
                for role, path in roles.items()
            ],
            "transcript_authority": {
                "engine": "subtitle_track",
                "provider": "youtube_subtitles",
                "real_transcript": True,
            },
            "selection_authority": {
                "allowed_ranges": [
                    {
                        "id": "allowed_001",
                        "source_start_seconds": 10.0,
                        "source_end_seconds": 32.0,
                    }
                ],
                "excluded_ranges": [
                    {
                        "id": "before",
                        "source_start_seconds": 0.0,
                        "source_end_seconds": 10.0,
                        "reason": "unselected",
                    },
                    {
                        "id": "after",
                        "source_start_seconds": 32.0,
                        "source_end_seconds": 40.0,
                        "reason": "unselected",
                    },
                ],
            },
            "candidate": {
                "candidate_id": "candidate_01",
                "source_start_seconds": 10.0,
                "source_end_seconds": 32.0,
                "duration_seconds": 22.0,
                "authority_cut_ids": ["cut_001", "cut_002"],
                "source_segment_ids": ["seg_000001", "seg_000002", "seg_000003"],
                "rationale": "fixture setup to payoff",
                "narrative_arc": {
                    "setup": "setup",
                    "development": "middle",
                    "payoff": "payoff",
                },
                "subtitles": [
                    {
                        "id": "out09_sub_001",
                        "source_start_seconds": 10.0,
                        "source_end_seconds": 16.0,
                        "text": "Hello there this is the setup",
                        "source_segment_ids": ["seg_000001"],
                    },
                    {
                        "id": "out09_sub_002",
                        "source_start_seconds": 16.0,
                        "source_end_seconds": 24.0,
                        "text": "This is the middle with a repeated word",
                        "source_segment_ids": ["seg_000002"],
                    },
                    {
                        "id": "out09_sub_003",
                        "source_start_seconds": 24.0,
                        "source_end_seconds": 32.0,
                        "text": "And this is the final payoff",
                        "source_segment_ids": ["seg_000003"],
                    },
                ],
            },
            "review_questions": ["Question one?", "Question two?"],
            "boundaries": {
                "rights_status": "pending",
                "production_candidate": False,
                "public_use_allowed": False,
                "human_creative_acceptance": False,
                "h1_successor_data_only": True,
            },
        },
    )
    return {
        "root": root,
        "episode": episode,
        "output": review / "out09_second_source_short_repeatability",
        "plan": plan,
        "edit_pack": edit_pack,
    }


def _fake_render(**kwargs) -> dict:
    Path(kwargs["video_path"]).write_bytes(b"out09-video")
    Path(kwargs["frame_sheet_path"]).write_bytes(b"out09-frame-sheet")
    duration = float(kwargs["expected_duration"])
    return {
        "media": {
            "video_codec": "h264",
            "audio_codec": "aac",
            "width": 1080,
            "height": 1920,
            "fps": 30.0,
            "duration_seconds": duration,
            "stream_counts": {"video": 1, "audio": 1, "other": 0},
            "pixel_format": "yuv420p",
        },
        "selected_video_encoder": "libx264",
        "attempts": [{"video_codec": "libx264", "status": "passed", "exit_code": 0}],
        "duration_matches_expected": True,
        "full_decode": {"status": "passed", "exit_code": 0, "stderr_empty": True},
        "faststart": {"status": "passed", "moov_before_mdat": True},
        "source_probe": {"video": {"duration_seconds": 40}, "audio": {"duration_seconds": 40}},
        "audio": {
            "measurement_method": "fixture",
            "input_measurement": {"integrated_lufs": -18.0, "true_peak_dbtp": -2.0},
            "decision": "normalize",
            "normalization_applied": True,
            "target": {"integrated_lufs": -14.0, "true_peak_dbtp_max": -1.0},
            "output_measurement": {"integrated_lufs": -14.0, "true_peak_dbtp": -1.5},
        },
        "frame_samples": [
            {"label": label, "seconds": seconds, "status": "extracted"}
            for label, seconds in kwargs["frame_samples"]
        ],
    }


def _fake_navigation(**kwargs) -> dict:
    Path(kwargs["output_path"]).write_bytes(b"out09-navigation")
    return {"status": "passed", "seconds": kwargs["seconds"]}


def _fake_signal_qa(**_kwargs) -> dict:
    return {
        "status": "passed",
        "blackdetect": {"event_count": 0, "maximum_duration_seconds": 0.0},
        "silencedetect": {"event_count": 0, "maximum_duration_seconds": 0.0},
    }


def _build(fixture: dict[str, Path], **overrides):
    args = {
        "episode_dir": fixture["episode"],
        "output_dir": fixture["output"],
        "candidate_plan_input_path": fixture["plan"],
        "base_dir": fixture["root"],
        "render_executor": _fake_render,
        "navigation_executor": _fake_navigation,
        "signal_qa_executor": _fake_signal_qa,
    }
    args.update(overrides)
    return out09.build_second_source_short_repeatability(**args)


def test_builds_one_hash_bound_second_source_package(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    result = _build(fixture)
    output = fixture["output"]
    readback = result["readback"]
    assert readback["source_difference"] == {
        "out08_provider_id": out09.OUT08_PROVIDER_ID,
        "out09_provider_id": "SECOND123",
        "different": True,
    }
    assert readback["candidate"]["duration_seconds"] == 22.0
    assert readback["subtitle"]["count"] == 3
    assert readback["render"]["execution_count"] == 1
    assert readback["render"]["corrective_pass_count"] == 0
    assert readback["selection_authority"]["checked_before_render"] is True
    assert readback["selection_authority"]["rejected_or_unselected_overlap_count"] == 0

    html = (output / "index.html").read_text(encoding="utf-8")
    assert html.count("<video ") == 1
    assert html.count("data-review-question=") == 2
    assert "Question one?" in html and "Question two?" in html
    manifest = json.loads((output / "candidate_manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_self_integrity"]["sha256"] == out09._canonical_manifest_self_hash(manifest)
    for row in manifest["files"]:
        assert out09._sha256(output / row["package_relative_path"]) == row["sha256"]


def test_rejects_excluded_overlap_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["candidate"]["source_start_seconds"] = 9.0
    plan["candidate"]["duration_seconds"] = 23.0
    plan["selection_authority"]["allowed_ranges"][0]["source_start_seconds"] = 9.0
    plan["candidate"]["subtitles"][0]["source_start_seconds"] = 9.0
    _write_json(fixture["plan"], plan)
    called = False

    def renderer(**_kwargs):
        nonlocal called
        called = True
        return {}

    with pytest.raises(out09.SecondSourceShortRepeatabilityError, match="overlaps rejected/unselected"):
        _build(fixture, render_executor=renderer)
    assert called is False
    assert not fixture["output"].exists()


def test_rejects_input_hash_change_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    edit_pack = json.loads(fixture["edit_pack"].read_text(encoding="utf-8"))
    edit_pack["cut_candidates"][0]["end_seconds"] = 23.5
    _write_json(fixture["edit_pack"], edit_pack)
    with pytest.raises(out09.SecondSourceShortRepeatabilityError, match="input hash mismatch: edit_pack"):
        _build(fixture)
    assert not fixture["output"].exists()


def test_rejects_non_provenance_subtitle_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["candidate"]["subtitles"][1]["text"] = "Words not present in source"
    _write_json(fixture["plan"], plan)
    with pytest.raises(out09.SecondSourceShortRepeatabilityError, match="not transcript-backed"):
        _build(fixture)
    assert not fixture["output"].exists()


def test_cli_reports_controlled_builder_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(**_kwargs):
        raise out09.SecondSourceShortRepeatabilityError("fixture authority failure")

    monkeypatch.setattr(out09_cli, "build_second_source_short_repeatability", fail)
    code = out09_cli.run(
        [
            "--episode-dir",
            "episode",
            "--output-dir",
            "output",
            "--candidate-plan-input",
            "plan.json",
        ]
    )
    assert code == 2
    assert "fixture authority failure" in capsys.readouterr().err
