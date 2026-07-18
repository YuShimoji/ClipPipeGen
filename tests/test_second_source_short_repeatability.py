from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import build_second_source_short_repeatability as out09_cli
from src.integrations.render import second_source_short_repeatability as out09
from src.integrations.render import vertical_short_candidate as vertical


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
    _write_json(
        captions,
        {
            "events": [
                {
                    "tStartMs": 10000,
                    "dDurationMs": 4000,
                    "segs": [
                        {"utf8": "Hello"},
                        {"utf8": " there", "tOffsetMs": 1000},
                        {"utf8": " this", "tOffsetMs": 2000},
                        {"utf8": " is", "tOffsetMs": 3000},
                    ],
                },
                {
                    "tStartMs": 14000,
                    "dDurationMs": 4000,
                    "segs": [
                        {"utf8": "the"},
                        {"utf8": " middle", "tOffsetMs": 1000},
                        {"utf8": " stays", "tOffsetMs": 2000},
                        {"utf8": " clear", "tOffsetMs": 3000},
                    ],
                },
                {
                    "tStartMs": 18000,
                    "dDurationMs": 4000,
                    "segs": [
                        {"utf8": "final"},
                        {"utf8": " payoff", "tOffsetMs": 1000},
                        {"utf8": " lands", "tOffsetMs": 2000},
                        {"utf8": " now", "tOffsetMs": 3000},
                    ],
                },
            ]
        },
    )
    segments = [
        {
            "id": "seg_000001",
            "start_seconds": 10.0,
            "end_seconds": 14.0,
            "text": "Hello there this is",
            "review_status": "unreviewed",
        },
        {
            "id": "seg_000002",
            "start_seconds": 14.0,
            "end_seconds": 18.0,
            "text": "the middle stays clear",
            "review_status": "unreviewed",
        },
        {
            "id": "seg_000003",
            "start_seconds": 18.0,
            "end_seconds": 22.0,
            "text": "final payoff lands now",
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
            "user_feedback": {
                "overall": "bounded_presentation_repair_required",
                "human_observation_priority": (
                    "authoritative_over_agent_legibility_observation"
                ),
                "native_caption_only_result": "failed_unreadable_at_review_size",
                "blurred_caption_duplication": "observed_in_lower_canvas",
                "content_selection": "not_rejected_not_yet_accepted",
                "endpoint_edit": "unchanged_not_reopened",
            },
            "repair": {
                "kind": "caption_canvas_presentation_repair",
                "lineage_index": 2,
                "initial_predecessor": {
                    "candidate_id": "candidate_01",
                    "source_start_seconds": 10.0,
                    "source_end_seconds": 20.0,
                    "duration_seconds": 10.0,
                    "media_duration_seconds": 10.0,
                    "video_sha256": out09.INITIAL_PREDECESSOR_MP4_SHA256,
                    "human_acceptance_claimed": False,
                },
                "failed_repair_predecessor": {
                    "candidate_id": "candidate_01",
                    "source_start_seconds": 10.0,
                    "source_end_seconds": 22.0,
                    "duration_seconds": 12.0,
                    "media_duration_seconds": 12.0,
                    "video_sha256": out09.FAILED_REPAIR_PREDECESSOR_MP4_SHA256,
                    "reason": (
                        "unreadable_native_caption_and_blurred_caption_duplication"
                    ),
                    "human_acceptance_claimed": False,
                },
                "human_observation": {
                    "native_caption_too_small_in_16_9_foreground": True,
                    "full_source_blur_duplicates_caption_glyphs": True,
                    "lower_canvas_appears_frosted_and_unreadable": True,
                    "agent_legibility_observation_overridden": True,
                },
                "background_canvas": {
                    "mode": vertical.CAPTION_FREE_BACKGROUND_POLICY,
                    "measurement_source": "ten_caption_active_source_frames",
                    "source_frame_pixels": {"width": 640, "height": 360},
                    "caption_free_crop_pixels": {
                        "x": 0,
                        "y": 0,
                        "width": 640,
                        "height": 286,
                    },
                    "caption_free_crop_normalized": {
                        "x": 0.0,
                        "y": 0.0,
                        "width": 1.0,
                        "height": 286 / 360,
                    },
                    "representative_frame_source_seconds": [
                        10.1,
                        11.0,
                        12.0,
                        13.0,
                        14.0,
                        15.0,
                        16.0,
                        17.0,
                        18.0,
                        21.8,
                    ],
                    "fallback": "neutral_solid_or_caption_free_edge_only",
                    "full_source_blur_fallback_allowed": False,
                },
                "native_caption_suppression": {
                    "method": "bottom_crop",
                    "caption_band_pixels": {
                        "x": 0,
                        "y": 286,
                        "width": 640,
                        "height": 74,
                    },
                    "caption_band_normalized": {
                        "x": 0.0,
                        "y": 286 / 360,
                        "width": 1.0,
                        "height": 74 / 360,
                    },
                    "foreground_source_crop_pixels": {
                        "x": 0,
                        "y": 0,
                        "width": 640,
                        "height": 286,
                    },
                    "validated_caption_active_frame_count": 10,
                    "important_content_preserved": True,
                    "mask_used": False,
                    "conflict_status": "none",
                },
                "subtitle_presentation": {
                    "display_authority": out09.SUBTITLE_DISPLAY_AUTHORITY,
                    "source_native_caption_pixels_suppressed": True,
                    "timing_authority": "youtube_json3_event_and_token_offsets",
                    "ass_srt_role": "display_and_provenance_sidecar",
                    "maximum_words_per_cue": 6,
                    "maximum_lines_per_cue": 2,
                    "caption_plate": "opaque_solid_black",
                    "caption_plate_alpha": 1.0,
                    "additional_blur_or_frosted_caption_surface": False,
                    "scope": "source_specific",
                },
                "endpoint_authority": {
                    "basis": (
                        "first_scene_transition_after_last_caption_and_speech"
                    ),
                    "last_native_caption_end_seconds": 22.0,
                    "last_speech_end_seconds": 21.9,
                    "silence_end_seconds": 22.1,
                    "next_scene_start_seconds": 22.0,
                    "next_native_caption_start_seconds": 22.0,
                    "selected_source_end_seconds": 22.0,
                    "fixed_padding_used": False,
                    "fade_sfx_freeze_or_silence_added": False,
                    "reopened_for_this_repair": False,
                },
            },
            "selection_authority": {
                "allowed_ranges": [
                    {
                        "id": "allowed_001",
                        "source_start_seconds": 10.0,
                        "source_end_seconds": 22.0,
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
                        "source_start_seconds": 22.0,
                        "source_end_seconds": 40.0,
                        "reason": "unselected",
                    },
                ],
            },
            "candidate": {
                "candidate_id": "candidate_01",
                "source_start_seconds": 10.0,
                "source_end_seconds": 22.0,
                "duration_seconds": 12.0,
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
                        "id": "out09_cue_001",
                        "source_start_seconds": 10.0,
                        "source_end_seconds": 12.0,
                        "text": "Hello there",
                        "source_segment_ids": ["seg_000001"],
                        "timing_authority": {
                            "source": "youtube_json3_event_and_token_offsets",
                            "event_index": 0,
                            "token_start_index": 0,
                            "token_end_index_exclusive": 2,
                            "end_boundary": {
                                "kind": "token_onset",
                                "event_index": 0,
                                "token_index": 2,
                            },
                        },
                    },
                    {
                        "id": "out09_cue_002",
                        "source_start_seconds": 12.0,
                        "source_end_seconds": 14.0,
                        "text": "this is",
                        "source_segment_ids": ["seg_000001"],
                        "timing_authority": {
                            "source": "youtube_json3_event_and_token_offsets",
                            "event_index": 0,
                            "token_start_index": 2,
                            "token_end_index_exclusive": 4,
                            "end_boundary": {
                                "kind": "json3_event_start",
                                "event_index": 1,
                            },
                        },
                    },
                    {
                        "id": "out09_cue_003",
                        "source_start_seconds": 14.0,
                        "source_end_seconds": 16.0,
                        "text": "the middle",
                        "source_segment_ids": ["seg_000002"],
                        "timing_authority": {
                            "source": "youtube_json3_event_and_token_offsets",
                            "event_index": 1,
                            "token_start_index": 0,
                            "token_end_index_exclusive": 2,
                            "end_boundary": {
                                "kind": "token_onset",
                                "event_index": 1,
                                "token_index": 2,
                            },
                        },
                    },
                    {
                        "id": "out09_cue_004",
                        "source_start_seconds": 16.0,
                        "source_end_seconds": 18.0,
                        "text": "stays clear",
                        "source_segment_ids": ["seg_000002"],
                        "timing_authority": {
                            "source": "youtube_json3_event_and_token_offsets",
                            "event_index": 1,
                            "token_start_index": 2,
                            "token_end_index_exclusive": 4,
                            "end_boundary": {
                                "kind": "json3_event_start",
                                "event_index": 2,
                            },
                        },
                    },
                    {
                        "id": "out09_cue_005",
                        "source_start_seconds": 18.0,
                        "source_end_seconds": 20.0,
                        "text": "final payoff",
                        "source_segment_ids": ["seg_000003"],
                        "timing_authority": {
                            "source": "youtube_json3_event_and_token_offsets",
                            "event_index": 2,
                            "token_start_index": 0,
                            "token_end_index_exclusive": 2,
                            "end_boundary": {
                                "kind": "token_onset",
                                "event_index": 2,
                                "token_index": 2,
                            },
                        },
                    },
                    {
                        "id": "out09_cue_006",
                        "source_start_seconds": 20.0,
                        "source_end_seconds": 22.0,
                        "text": "lands now",
                        "source_segment_ids": ["seg_000003"],
                        "timing_authority": {
                            "source": "youtube_json3_event_and_token_offsets",
                            "event_index": 2,
                            "token_start_index": 2,
                            "token_end_index_exclusive": 4,
                            "end_boundary": {
                                "kind": "json3_event_end",
                                "event_index": 2,
                            },
                        },
                    },
                ],
            },
            "review_questions": [out09.REPAIR_REVIEW_QUESTION],
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
    render_ass = Path(kwargs["ass_path"]).read_text(encoding="utf-8")
    assert Path(kwargs["ass_path"]).name == "candidate_01_subtitles.ass"
    assert render_ass.count("Dialogue:") == 6
    assert "BorderStyle" in render_ass
    assert kwargs["composition_policy"]["mode"] == (
        vertical.CAPTION_FREE_BACKGROUND_POLICY
    )
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
        "composition_policy": kwargs["composition_policy"],
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
    assert readback["candidate"]["duration_seconds"] == 12.0
    assert readback["subtitle"]["count"] == 6
    assert readback["subtitle"]["display_authority"] == (
        "generated_short_cue_overlay_from_source_json3"
    )
    assert readback["subtitle"]["burn_in_applied"] is True
    assert readback["subtitle"]["source_native_caption_pixels_suppressed"] is True
    assert readback["subtitle"]["visible_overlay_event_count"] == 6
    assert readback["subtitle"]["statistics"]["word_count_range"] == {
        "minimum": 2,
        "maximum": 2,
    }
    assert readback["repair"]["lineage_index"] == 2
    assert readback["repair"]["initial_predecessor"]["video_sha256"] == (
        out09.INITIAL_PREDECESSOR_MP4_SHA256
    )
    assert readback["repair"]["failed_repair_predecessor"]["video_sha256"] == (
        out09.FAILED_REPAIR_PREDECESSOR_MP4_SHA256
    )
    assert readback["render"]["composition_policy"]["mode"] == (
        vertical.CAPTION_FREE_BACKGROUND_POLICY
    )
    assert readback["render"]["execution_count"] == 1
    assert readback["render"]["corrective_pass_count"] == 0
    assert readback["selection_authority"]["checked_before_render"] is True
    assert readback["selection_authority"]["rejected_or_unselected_overlap_count"] == 0

    html = (output / "index.html").read_text(encoding="utf-8")
    assert html.count("<video ") == 1
    assert html.count("data-review-question=") == 1
    assert out09.REPAIR_REVIEW_QUESTION in html
    manifest = json.loads((output / "candidate_manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_self_integrity"]["sha256"] == out09._canonical_manifest_self_hash(manifest)
    for row in manifest["files"]:
        assert out09._sha256(output / row["package_relative_path"]) == row["sha256"]


def test_rejects_excluded_overlap_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["candidate"]["source_start_seconds"] = 9.0
    plan["candidate"]["duration_seconds"] = 13.0
    plan["repair"]["initial_predecessor"]["source_start_seconds"] = 9.0
    plan["repair"]["failed_repair_predecessor"]["source_start_seconds"] = 9.0
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
    with pytest.raises(
        out09.SecondSourceShortRepeatabilityError,
        match="not JSON3/transcript-backed",
    ):
        _build(fixture)
    assert not fixture["output"].exists()


def test_rejects_native_caption_as_display_authority_before_render(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["repair"]["subtitle_presentation"]["display_authority"] = (
        "source_native_caption_pixels"
    )
    _write_json(fixture["plan"], plan)
    with pytest.raises(
        out09.SecondSourceShortRepeatabilityError,
        match="short-cue caption authority is incomplete",
    ):
        _build(fixture)
    assert not fixture["output"].exists()


def test_rejects_endpoint_that_cuts_before_speech_completion(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["repair"]["endpoint_authority"]["last_speech_end_seconds"] = 22.2
    _write_json(fixture["plan"], plan)
    with pytest.raises(
        out09.SecondSourceShortRepeatabilityError,
        match="does not preserve caption/speech/scene completion",
    ):
        _build(fixture)
    assert not fixture["output"].exists()


def test_rejects_caption_crop_that_intersects_measured_band(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["repair"]["background_canvas"]["caption_free_crop_pixels"][
        "height"
    ] = 288
    _write_json(fixture["plan"], plan)
    with pytest.raises(
        out09.SecondSourceShortRepeatabilityError,
        match="does not match the measured source rectangle",
    ):
        _build(fixture)
    assert not fixture["output"].exists()


def test_rejects_json3_token_boundary_drift_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["candidate"]["subtitles"][1]["timing_authority"][
        "token_start_index"
    ] = 3
    _write_json(fixture["plan"], plan)
    with pytest.raises(
        out09.SecondSourceShortRepeatabilityError,
        match="does not match JSON3 boundary",
    ):
        _build(fixture)
    assert not fixture["output"].exists()


def test_rejects_more_than_six_words_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["candidate"]["subtitles"][0]["text"] = (
        "one two three four five six seven"
    )
    _write_json(fixture["plan"], plan)
    with pytest.raises(
        out09.SecondSourceShortRepeatabilityError,
        match="must contain 1-6 whole words",
    ):
        _build(fixture)
    assert not fixture["output"].exists()


def test_rejects_failed_predecessor_chain_drift(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["repair"]["failed_repair_predecessor"]["video_sha256"] = "0" * 64
    _write_json(fixture["plan"], plan)
    with pytest.raises(
        out09.SecondSourceShortRepeatabilityError,
        match="failed repair predecessor identity mismatch",
    ):
        _build(fixture)
    assert not fixture["output"].exists()


def test_shared_renderer_default_background_filter_is_unchanged() -> None:
    command = vertical._vertical_render_command(
        ffmpeg_path="ffmpeg",
        source_video_path=Path("source.mp4"),
        source_audio_path=Path("source.wav"),
        ass_path=Path("captions.ass"),
        font_file=Path("font.ttf"),
        timeline=[{"source_start_seconds": 1.0, "source_end_seconds": 2.0}],
        output_path=Path("output.mp4"),
        video_codec="libx264",
        audio_filter="anull",
    )
    filter_complex = command[command.index("-filter_complex") + 1]
    assert "[bgraw0]scale=1080:1920:" in filter_complex
    assert "crop=1080:1920,gblur=sigma=42" in filter_complex
    assert "[fgraw0]scale=1080:-2:flags=lanczos[fg0]" in filter_complex
    assert "crop=640:286:0:0" not in filter_complex


def test_caption_free_policy_crops_before_background_and_foreground_scale(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    policy = out09._normalize_composition_policy(plan["repair"])
    command = vertical._vertical_render_command(
        ffmpeg_path="ffmpeg",
        source_video_path=Path("source.mp4"),
        source_audio_path=Path("source.wav"),
        ass_path=Path("captions.ass"),
        font_file=Path("font.ttf"),
        timeline=[{"source_start_seconds": 1.0, "source_end_seconds": 2.0}],
        output_path=Path("output.mp4"),
        video_codec="libx264",
        audio_filter="anull",
        composition_policy=policy,
    )
    filter_complex = command[command.index("-filter_complex") + 1]
    assert filter_complex.count("crop=640:286:0:0") == 2
    assert "[bgraw0]crop=640:286:0:0,scale=1080:1920" in filter_complex
    assert "[fgraw0]crop=640:286:0:0,scale=1080:-2" in filter_complex


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
