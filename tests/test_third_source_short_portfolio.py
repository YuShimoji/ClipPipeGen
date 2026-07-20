from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import main as cli_main
from src.integrations.render import endpoint_preflight as endpoint
from src.integrations.render import third_source_short_portfolio as out10
from src.integrations.render import vertical_short_candidate as vertical


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path
    episode = root / "episodes" / "third_source_episode"
    review = episode / "review"
    video = episode / "materials" / "video_01" / "source_video.mp4"
    audio = episode / "materials" / "audio_01" / "source.wav"
    video.parent.mkdir(parents=True)
    audio.parent.mkdir(parents=True)
    video.write_bytes(b"third-source-video")
    audio.write_bytes(b"third-source-audio")

    rights = episode / "rights_manifest.json"
    ledger = episode / "material_ledger.json"
    captions = episode / "source_captions.ja.json3"
    transcript = episode / "transcript_source_captions.json"
    edit_pack = episode / "edit_pack.json"
    receipt = root / "docs" / "output_layer" / "out10_external_receipt.json"
    candidate_end = 30.014
    predecessor_end = out10.PREDECESSOR_SOURCE_END_SECONDS
    bounds = [
        round(
            predecessor_end * index / out10.PREDECESSOR_CAPTION_CUE_COUNT,
            3,
        )
        for index in range(out10.PREDECESSOR_CAPTION_CUE_COUNT + 1)
    ]
    bounds.append(candidate_end)
    caption_events = []
    transcript_segments = []
    planned_subtitles = []
    for index, (start, end) in enumerate(zip(bounds, bounds[1:]), start=1):
        text = f"公式字幕{index:02d}"
        caption_events.append(
            {
                "tStartMs": int(round(start * 1000)),
                "dDurationMs": int(round((end - start) * 1000)),
                "segs": [{"utf8": text}],
            }
        )
        segment_id = f"seg_{index:06d}"
        transcript_segments.append(
            {
                "id": segment_id,
                "start_seconds": start,
                "end_seconds": end,
                "text": text,
            }
        )
        planned_subtitles.append(
            {
                "id": f"out10_cue_{index:03d}",
                "source_start_seconds": start,
                "source_end_seconds": end,
                "text": text,
                "source_segment_id": segment_id,
                "caption_event_index": index - 1,
            }
        )
    _write_json(
        rights,
        {
            "source_video": {
                "url": "https://www.youtube.com/watch?v=THIRD123456",
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
                    "registered_by": "tool:asset_fetch_yt_dlp_video:test",
                    "file_path": video.relative_to(root).as_posix(),
                    "hash_sha256": out10._sha256(video),
                },
                {
                    "id": "audio_01",
                    "kind": "source_audio",
                    "registered_by": "tool:asset_fetch_local_media_audio:test",
                    "file_path": audio.relative_to(root).as_posix(),
                    "hash_sha256": out10._sha256(audio),
                },
            ]
        },
    )
    _write_json(
        captions,
        {"events": caption_events},
    )
    _write_json(
        transcript,
        {
            "stt": {
                "engine": "subtitle_track",
                "provider": "youtube_subtitles",
                "real_transcript": True,
            },
            "review": {"status": "needs_review"},
            "segments": transcript_segments,
        },
    )
    _write_json(
        edit_pack,
        {
            "selected_cut_ids": ["cut_001"],
            "cut_candidates": [
                {
                    "id": "cut_001",
                    "start_seconds": 0.0,
                    "end_seconds": candidate_end,
                    "context_check": {"status": "passed"},
                }
            ],
        },
    )
    _write_json(
        receipt,
        {
            "artifact_id": out10.ARTIFACT_ID,
            "state": "OUT10_BOUNDED_EXTERNAL_ACQUISITION_AUTHORIZED",
            "scope": {
                "metadata_candidate_count": 5,
                "detailed_preflight_count": 3,
                "media_download_count": 1,
            },
            "selected_source": {"rank": 1, "provider_id": "THIRD123456"},
            "decision": {
                "rejected_preflight_provider_ids": ["OTHER000001", "OTHER000002"]
            },
        },
    )
    endpoint_dir = episode / "inspection" / "endpoint"
    endpoint_dir.mkdir(parents=True)
    contact_sheet = endpoint_dir / "endpoint_contact_sheet.jpg"
    waveform = endpoint_dir / "endpoint_waveform.png"
    contact_sheet.write_bytes(b"endpoint-contact-sheet")
    waveform.write_bytes(b"endpoint-waveform")
    endpoint_spec = {
        "source": {
            "media_path": video.relative_to(root).as_posix(),
            "identity": "youtube:THIRD123456",
            "sha256": out10._sha256(video),
            "expected_sha256": out10._sha256(video),
            "duration_seconds": 40.0,
            "frame_rate": 30.0,
        },
        "source_start_seconds": 0.0,
        "proposed_end_seconds": candidate_end,
        "search_range": {
            "start_seconds": predecessor_end,
            "end_seconds": predecessor_end + 12.0,
        },
        "caption_track": {
            "authority": "official_json3",
            "expected_authority": "official_json3",
            "source_identity": "youtube:THIRD123456",
            "source_media_sha256": out10._sha256(video),
            "mapping_complete": True,
            "mapping_gaps": [],
            "cues": [
                {
                    "cue_id": f"event_{index:03d}",
                    "start_seconds": start,
                    "end_seconds": end,
                }
                for index, (start, end) in enumerate(
                    zip(bounds, bounds[1:]),
                    start=1,
                )
            ],
        },
        "probe_status": {"frame_ok": True, "audio_ok": True},
        "limits": {
            "min_duration_seconds": 12.0,
            "max_duration_seconds": 60.0,
            "repair_max_extension_seconds": 12.0,
            "caption_guard_seconds": 0.0,
            "candidate_limit": 12,
        },
        "observations": [
            {"kind": "shot_transition", "time_seconds": 30.033333},
            {"kind": "high_motion", "time_seconds": candidate_end},
        ],
    }
    preflight = endpoint.build_endpoint_preflight(endpoint_spec)
    selection = endpoint.build_endpoint_selection(
        preflight,
        {
            "preflight_sha256": endpoint.payload_sha256(preflight),
            "selected_candidate_id": "endpoint-002",
            "selected_end_seconds": candidate_end,
            "agent_observation": {
                "last_utterance": "complete",
                "audio": "complete",
                "telop_action_transition": "complete",
                "topic_closure": "complete",
                "unrelated_topic": "not_overrun",
                "earlier_candidate_rejections": [
                    {
                        "candidate_id": "endpoint-001",
                        "reason": "the response utterance has only just started",
                    }
                ],
            },
        },
    )
    preflight_path = endpoint_dir / "endpoint_preflight.json"
    selection_path = endpoint_dir / "endpoint_selection.json"
    _write_json(preflight_path, preflight)
    _write_json(selection_path, selection)
    evidence_manifest = endpoint_dir / "endpoint_evidence_manifest.json"
    evidence_files = [preflight_path, selection_path, contact_sheet, waveform]
    evidence_payload = {
        "schema_version": "clippipegen.endpoint_evidence_manifest.v0",
        "source_identity": "youtube:THIRD123456",
        "source_media_sha256": out10._sha256(video),
        "selected_end_seconds": candidate_end,
        "selection_state": "ready_for_render",
        "files": [
            {
                "path": path.name,
                "sha256": out10._sha256(path),
                "byte_size": path.stat().st_size,
            }
            for path in evidence_files
        ],
        "file_count": len(evidence_files),
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    evidence_payload["manifest_self_integrity"]["sha256"] = (
        out10._canonical_manifest_self_hash(evidence_payload)
    )
    _write_json(evidence_manifest, evidence_payload)
    roles = {
        "rights_manifest": rights,
        "material_ledger": ledger,
        "source_caption_track": captions,
        "authoritative_transcript": transcript,
        "edit_pack": edit_pack,
        "source_selection_receipt": receipt,
        "endpoint_preflight": preflight_path,
        "endpoint_selection": selection_path,
        "endpoint_evidence_manifest": evidence_manifest,
    }
    plan = episode / "out10_candidate_plan_input.json"
    plan_payload = {
        "schema_version": out10.PLAN_SCHEMA_VERSION,
        "artifact_id": out10.ARTIFACT_ID,
        "episode_id": episode.name,
        "source_identity": {
            "platform": "youtube",
            "provider_id": "THIRD123456",
            "url": "https://www.youtube.com/watch?v=THIRD123456",
            "title": "third source",
            "channel": "official channel",
            "channel_id": "UCJFZiqLMntJufDCHc6bQixg",
            "official_channel": True,
            "channel_verified": True,
        },
        "external_acquisition": {
            "authorized": True,
            "anonymous": True,
            "metadata_candidate_count": 5,
            "detailed_preflight_count": 3,
            "media_download_count": 1,
            "cookie_or_login_used": False,
            "bypass_used": False,
            "alternate_candidate_download_on_failure": False,
            "source_audio_derived_locally": True,
        },
        "materials": {
            "source_video": {
                "material_id": "video_01",
                "sha256": out10._sha256(video),
            },
            "source_audio": {
                "material_id": "audio_01",
                "sha256": out10._sha256(audio),
            },
        },
        "expected_inputs": [
            {
                "role": role,
                "path": path.relative_to(root).as_posix(),
                "sha256": out10._sha256(path),
            }
            for role, path in roles.items()
        ],
        "composition_policy": {
            "mode": vertical.NEUTRAL_MATTE_BACKGROUND_POLICY,
            "source_frame_pixels": {"width": 1920, "height": 1080},
            "foreground_source_crop_pixels": {
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 1080,
            },
            "matte_color": "0x0D1624",
            "source_derived_background": False,
            "blur_applied": False,
            "crop_applied": False,
            "source_native_caption_pixels_suppressed": False,
            "additional_blur_or_frosted_caption_surface": False,
            "full_source_blur_fallback_allowed": False,
            "important_content_preserved": True,
        },
        "candidate": {
            "candidate_id": "candidate_01",
            "source_start_seconds": 0.0,
            "source_end_seconds": candidate_end,
            "duration_seconds": candidate_end,
            "authority_cut_id": "cut_001",
            "candidate_count_considered": 1,
            "start_basis": "opening",
            "end_basis": "closed event",
            "next_scene_transition_seconds": 30.033333,
            "rationale": "setup to complete response payoff",
            "narrative_arc": {
                "setup": "setup",
                "development": "development",
                "payoff": "payoff",
            },
            "subtitles": planned_subtitles,
        },
        "endpoint_repair": {
            "predecessor_state": out10.PREDECESSOR_STATE,
            "predecessor_video_sha256": out10.PREDECESSOR_VIDEO_SHA256,
            "predecessor_source_end_seconds": predecessor_end,
            "predecessor_caption_cue_count": (out10.PREDECESSOR_CAPTION_CUE_COUNT),
            "lineage_reason": out10.LINEAGE_REASON,
            "earlier_lineage": {
                "predecessor_video_sha256": (out10.EARLIER_PREDECESSOR_VIDEO_SHA256),
                "predecessor_source_end_seconds": (
                    out10.EARLIER_PREDECESSOR_SOURCE_END_SECONDS
                ),
                "lineage_reason": out10.EARLIER_LINEAGE_REASON,
            },
            "inherited_pass": [
                "content_and_tempo",
                "subtitle_audio_sync",
                "subtitle_readability",
                "neutral_matte_composition",
                "safe_review_route",
            ],
            "probe_candidates": [
                {
                    "source_seconds": predecessor_end,
                    "status": "rejected_active_telop_motion",
                },
                {
                    "source_seconds": candidate_end,
                    "status": "selected",
                },
            ],
            "selection_basis": "caption, pose, and shot boundary complete",
        },
        "portfolio_subtitle_differentiation_debt": {
            "status": "deferred",
            "current_white_style_approved_as_general_standard": False,
            "speaker_identity_inference_allowed": False,
            "revisit_condition": "after_3_to_5_accepted_real_shorts_or_explicit_production_subtitle_design_gate",
        },
        "review_questions": [out10.REVIEW_QUESTION],
        "boundaries": {
            "rights_status": "pending",
            "production_candidate": False,
            "production_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "production_image_quality_acceptance": False,
            "thumbnail_acceptance": False,
            "public_or_publishing_acceptance": False,
            "publish_or_upload_attempted": False,
            "cross_machine_portability": False,
            "human_review_pending": True,
            "acceptance_granted": False,
        },
    }
    _write_json(
        plan,
        endpoint.bind_builder_input(plan_payload, preflight, selection),
    )
    return {
        "root": root,
        "episode": episode,
        "output": review / "out10_third_source_portfolio",
        "plan": plan,
        "preflight": preflight_path,
        "selection": selection_path,
    }


def _fake_render(**kwargs) -> dict:
    assert kwargs["composition_policy"]["mode"] == (
        vertical.NEUTRAL_MATTE_BACKGROUND_POLICY
    )
    Path(kwargs["video_path"]).write_bytes(b"out10-video")
    Path(kwargs["frame_sheet_path"]).write_bytes(b"out10-frame")
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
        "attempts": [{"video_codec": "libx264", "status": "passed"}],
        "duration_matches_expected": True,
        "full_decode": {"status": "passed", "exit_code": 0, "stderr_empty": True},
        "faststart": {"status": "passed", "moov_before_mdat": True},
        "source_probe": {
            "video": {"width": 1920, "height": 1080, "duration_seconds": 40},
            "audio": {"duration_seconds": 40},
        },
        "composition_policy": kwargs["composition_policy"],
        "audio": {
            "input_measurement": {"integrated_lufs": -20.0, "true_peak_dbtp": -3.0},
            "output_measurement": {"integrated_lufs": -14.0, "true_peak_dbtp": -1.5},
            "normalization_applied": True,
        },
        "frame_samples": [
            {"label": label, "seconds": seconds, "status": "extracted"}
            for label, seconds in kwargs["frame_samples"]
        ],
    }


def _fake_navigation(**kwargs) -> dict:
    Path(kwargs["output_path"]).write_bytes(b"out10-navigation")
    return {"status": "passed", "seconds": kwargs["seconds"]}


def _fake_signal_qa(**_kwargs) -> dict:
    return {
        "status": "passed",
        "blackdetect": {"event_count": 0},
        "silencedetect": {"event_count": 0},
    }


def test_builds_third_source_package_and_scorecard(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    result = out10.build_third_source_short_portfolio(
        episode_dir=fixture["episode"],
        output_dir=fixture["output"],
        candidate_plan_input_path=fixture["plan"],
        base_dir=fixture["root"],
        render_executor=_fake_render,
        navigation_executor=_fake_navigation,
        signal_qa_executor=_fake_signal_qa,
    )
    readback = result["readback"]
    assert readback["state"] == out10.STATE
    assert readback["source_difference"]["all_distinct"] is True
    assert readback["candidate"]["human_review_pending"] is True
    assert readback["subtitle"]["count"] == 46
    assert readback["repair_lineage"]["predecessor_video_sha256"] == (
        out10.PREDECESSOR_VIDEO_SHA256
    )
    assert readback["endpoint_repair"]["additional_caption_cue_count"] == 1
    assert readback["portfolio_subtitle_differentiation_debt"]["status"] == ("deferred")
    scorecard = json.loads(
        (fixture["output"] / "source_portfolio_scorecard.json").read_text(
            encoding="utf-8"
        )
    )
    assert [row["portfolio_slot"] for row in scorecard["rows"]] == [
        "OUT-08",
        "OUT-09",
        "OUT-10",
    ]
    html = (fixture["output"] / "index.html").read_text(encoding="utf-8")
    assert html.count("data-review-question=") == 1
    assert "autoplay" not in html.lower()
    assert out10.REVIEW_QUESTION in html


def test_rejects_predecessor_recording_identity(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["source_identity"]["provider_id"] = out10.OUT09_PROVIDER_ID
    _write_json(
        fixture["plan"],
        endpoint.bind_builder_input(
            plan,
            json.loads(fixture["preflight"].read_text(encoding="utf-8")),
            json.loads(fixture["selection"].read_text(encoding="utf-8")),
        ),
    )
    with pytest.raises(out10.ThirdSourceShortPortfolioError, match="not distinct"):
        out10.build_third_source_short_portfolio(
            episode_dir=fixture["episode"],
            output_dir=fixture["output"],
            candidate_plan_input_path=fixture["plan"],
            base_dir=fixture["root"],
            render_executor=_fake_render,
            navigation_executor=_fake_navigation,
            signal_qa_executor=_fake_signal_qa,
        )


def test_rejects_endpoint_repair_without_exact_predecessor_hash(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["endpoint_repair"]["predecessor_video_sha256"] = "0" * 64
    _write_json(
        fixture["plan"],
        endpoint.bind_builder_input(
            plan,
            json.loads(fixture["preflight"].read_text(encoding="utf-8")),
            json.loads(fixture["selection"].read_text(encoding="utf-8")),
        ),
    )
    with pytest.raises(
        out10.ThirdSourceShortPortfolioError,
        match="endpoint repair authority is incomplete",
    ):
        out10.build_third_source_short_portfolio(
            episode_dir=fixture["episode"],
            output_dir=fixture["output"],
            candidate_plan_input_path=fixture["plan"],
            base_dir=fixture["root"],
            render_executor=_fake_render,
            navigation_executor=_fake_navigation,
            signal_qa_executor=_fake_signal_qa,
        )


def test_rejects_tampered_endpoint_binding_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["endpoint_binding"]["selection_sha256"] = "0" * 64
    _write_json(fixture["plan"], plan)

    def _render_must_not_run(**_kwargs) -> dict:
        raise AssertionError("render executor must not run")

    with pytest.raises(
        out10.ThirdSourceShortPortfolioError,
        match="endpoint is not ready for render",
    ):
        out10.build_third_source_short_portfolio(
            episode_dir=fixture["episode"],
            output_dir=fixture["output"],
            candidate_plan_input_path=fixture["plan"],
            base_dir=fixture["root"],
            render_executor=_render_must_not_run,
            navigation_executor=_fake_navigation,
            signal_qa_executor=_fake_signal_qa,
        )


def test_neutral_matte_policy_has_no_blur_or_source_crop() -> None:
    policy = {
        "mode": vertical.NEUTRAL_MATTE_BACKGROUND_POLICY,
        "source_frame_pixels": {"width": 1920, "height": 1080},
        "foreground_source_crop_pixels": {
            "x": 0,
            "y": 0,
            "width": 1920,
            "height": 1080,
        },
        "matte_color": "0x0D1624",
        "source_derived_background": False,
        "blur_applied": False,
        "crop_applied": False,
        "source_native_caption_pixels_suppressed": False,
        "additional_blur_or_frosted_caption_surface": False,
        "full_source_blur_fallback_allowed": False,
        "important_content_preserved": True,
    }
    readback = vertical._validate_vertical_composition_policy(
        policy,
        source_video_probe={"width": 1920, "height": 1080},
    )
    background, foreground = vertical._vertical_composition_filters(
        index=0,
        composition_policy=readback,
    )
    assert "drawbox" in background
    assert "gblur" not in background
    assert "crop=1920:1080:0:0" in foreground


def test_cli_is_registered_and_server_helpers_are_parameterized() -> None:
    assert "build-third-source-short-portfolio" in cli_main.SUBCOMMANDS
    server = out10._serve_script(
        expected_video_sha256="a" * 64,
        artifact_id=out10.ARTIFACT_ID,
        default_port=out10.REVIEW_PORT,
        review_label="OUT-10",
    )
    opener = out10._open_script(
        default_port=out10.REVIEW_PORT,
        review_label="OUT-10",
    )
    assert out10.ARTIFACT_ID in server
    assert "OUT-10 review URL" in server
    assert "[int]$Port = 8073" in server
    assert "OUT-10 review server is not running" in opener
