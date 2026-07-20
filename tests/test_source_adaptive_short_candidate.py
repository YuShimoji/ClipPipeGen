from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.integrations.render import endpoint_preflight as endpoint
from src.integrations.render import source_adaptive_short_candidate as source_candidate
from src.integrations.render import vertical_short_candidate as vertical


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path, *, native: bool = False) -> dict[str, Path]:
    root = tmp_path
    episode = root / "episodes" / ("official_source_native" if native else "official_source_overlay")
    video = episode / "materials" / "video_01" / "source.mp4"
    audio = episode / "materials" / "audio_01" / "source.m4a"
    video.parent.mkdir(parents=True)
    audio.parent.mkdir(parents=True)
    video.write_bytes(b"source-specific-video")
    audio.write_bytes(b"source-specific-audio")
    provider_id = "SOURCE_NATIVE" if native else "SOURCE_OVERLAY"
    identity = f"youtube:{provider_id}"
    start = 5.0
    end = 18.5

    rights = episode / "rights_manifest.json"
    ledger = episode / "material_ledger.json"
    captions = episode / "official.en.json3"
    _write_json(
        rights,
        {
            "source_video": {
                "url": f"https://www.youtube.com/watch?v={provider_id}"
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
                    "hash_sha256": source_candidate._sha256(video),
                },
                {
                    "id": "audio_01",
                    "kind": "source_audio",
                    "registered_by": "tool:asset_fetch_local_media_audio:test",
                    "file_path": audio.relative_to(root).as_posix(),
                    "hash_sha256": source_candidate._sha256(audio),
                },
            ]
        },
    )
    _write_json(
        captions,
        {
            "events": [
                {
                    "tStartMs": 5000,
                    "dDurationMs": 5000,
                    "segs": [{"utf8": "official setup"}],
                },
                {
                    "tStartMs": 10000,
                    "dDurationMs": 8500,
                    "segs": [{"utf8": "official payoff"}],
                },
            ]
        },
    )

    endpoint_dir = episode / "inspection" / "endpoint"
    endpoint_dir.mkdir(parents=True)
    contact = endpoint_dir / "endpoint_contact_sheet.jpg"
    waveform = endpoint_dir / "endpoint_waveform.png"
    candidate_contact = endpoint_dir / "candidate_contact_sheet.jpg"
    contact.write_bytes(b"endpoint-contact")
    waveform.write_bytes(b"endpoint-waveform")
    candidate_contact.write_bytes(b"candidate-contact")
    preflight = endpoint.build_endpoint_preflight(
        {
            "source": {
                "media_path": video.relative_to(root).as_posix(),
                "identity": identity,
                "sha256": source_candidate._sha256(video),
                "expected_sha256": source_candidate._sha256(video),
                "duration_seconds": 30.0,
                "frame_rate": 30.0,
            },
            "source_start_seconds": start,
            "proposed_end_seconds": end,
            "search_range": {"start_seconds": end - 1.0, "end_seconds": end + 1.0},
            "caption_track": {
                "authority": "official_json3",
                "expected_authority": "official_json3",
                "source_identity": identity,
                "source_media_sha256": source_candidate._sha256(video),
                "mapping_complete": True,
                "mapping_gaps": [],
                "cues": [
                    {"cue_id": "event_000", "start_seconds": 5.0, "end_seconds": 10.0},
                    {"cue_id": "event_001", "start_seconds": 10.0, "end_seconds": 18.5},
                ],
            },
            "probe_status": {"frame_ok": True, "audio_ok": True},
            "limits": {
                "min_duration_seconds": 12.0,
                "max_duration_seconds": 60.0,
                "caption_guard_seconds": 0.0,
                "candidate_limit": 6,
            },
            "observations": [
                {"kind": "low_motion", "time_seconds": end},
                {"kind": "shot_transition", "time_seconds": end + 0.034},
            ],
        }
    )
    selection = endpoint.build_endpoint_selection(
        preflight,
        {
            "preflight_sha256": endpoint.payload_sha256(preflight),
            "selected_candidate_id": "endpoint-001",
            "selected_end_seconds": end,
            "agent_observation": {
                "last_utterance": "complete",
                "audio": "complete",
                "telop_action_transition": "complete",
                "topic_closure": "complete",
                "unrelated_topic": "not_overrun",
                "earlier_candidate_rejections": [],
            },
        },
    )
    preflight_path = endpoint_dir / "endpoint_preflight.json"
    selection_path = endpoint_dir / "endpoint_selection.json"
    _write_json(preflight_path, preflight)
    _write_json(selection_path, selection)
    evidence_manifest = endpoint_dir / "endpoint_evidence_manifest.json"
    evidence_files = [preflight_path, selection_path, contact, waveform, candidate_contact]
    evidence_payload = {
        "schema_version": "clippipegen.endpoint_evidence_manifest.v0",
        "source_identity": identity,
        "source_media_sha256": source_candidate._sha256(video),
        "selected_end_seconds": end,
        "selection_state": "ready_for_render",
        "files": [
            {
                "path": path.name,
                "sha256": source_candidate._sha256(path),
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
        source_candidate._canonical_manifest_self_hash(evidence_payload)
    )
    _write_json(evidence_manifest, evidence_payload)

    roles = {
        "rights_manifest": rights,
        "material_ledger": ledger,
        "source_caption_track": captions,
        "endpoint_preflight": preflight_path,
        "endpoint_selection": selection_path,
        "endpoint_evidence_manifest": evidence_manifest,
    }
    mode = (
        source_candidate.CAPTION_MODE_NATIVE
        if native
        else source_candidate.CAPTION_MODE_OVERLAY
    )
    plan_payload = {
        "schema_version": source_candidate.PLAN_SCHEMA_VERSION,
        "artifact_id": f"clip-out11-{provider_id.lower()}-v0-001",
        "episode_id": episode.name,
        "source_identity": {
            "identity": identity,
            "platform": "youtube",
            "provider_id": provider_id,
            "url": f"https://www.youtube.com/watch?v={provider_id}",
            "title": f"source-specific {mode}",
            "channel": "official source-specific channel",
            "channel_id": f"CHANNEL_{provider_id}",
            "official_channel": True,
        },
        "materials": {
            "source_video": {
                "material_id": "video_01",
                "sha256": source_candidate._sha256(video),
            },
            "source_audio": {
                "material_id": "audio_01",
                "sha256": source_candidate._sha256(audio),
            },
        },
        "expected_inputs": [
            {
                "role": role,
                "path": path.relative_to(root).as_posix(),
                "sha256": source_candidate._sha256(path),
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
        "caption_policy": {
            "mode": mode,
            "source_authority": "official_json3",
            "overlay_enabled": not native,
            "native_captions_visible": native,
            "crop_intersects_native_caption_band": False,
        },
        "candidate": {
            "candidate_id": "candidate_01",
            "source_start_seconds": start,
            "source_end_seconds": end,
            "duration_seconds": end - start,
            "rationale": "source-specific complete setup and payoff",
            "caption_cues": []
            if native
            else [
                {
                    "id": "cue_001",
                    "event_index": 0,
                    "source_start_seconds": 5.0,
                    "source_end_seconds": 10.0,
                    "text": "official setup",
                },
                {
                    "id": "cue_002",
                    "event_index": 1,
                    "source_start_seconds": 10.0,
                    "source_end_seconds": 18.5,
                    "text": "official payoff",
                },
            ],
        },
        "review_question": "Does this source-specific Short stand on its own?",
        "boundaries": {
            "rights_status": "pending",
            "production_acceptance": False,
            "thumbnail_acceptance": False,
            "public_or_publishing_acceptance": False,
            "publish_or_upload_attempted": False,
            "human_review_pending": True,
            "acceptance_granted": False,
        },
    }
    plan = episode / "out11_candidate_plan.json"
    _write_json(plan, endpoint.bind_builder_input(plan_payload, preflight, selection))
    return {
        "root": root,
        "episode": episode,
        "output": episode / "review" / f"out11_{provider_id.lower()}_candidate",
        "plan": plan,
        "preflight": preflight_path,
        "selection": selection_path,
        "provider_id": Path(provider_id),
    }


def _fake_render(**kwargs) -> dict:
    assert kwargs["composition_policy"]["mode"] == vertical.NEUTRAL_MATTE_BACKGROUND_POLICY
    assert kwargs["timeline"][0]["source_start_seconds"] == 5.0
    Path(kwargs["video_path"]).write_bytes(b"source-adaptive-candidate")
    Path(kwargs["frame_sheet_path"]).write_bytes(b"source-adaptive-frames")
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
            "video": {"width": 1920, "height": 1080, "duration_seconds": 30.0},
            "audio": {"duration_seconds": 30.0},
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
    Path(kwargs["output_path"]).write_bytes(b"source-adaptive-navigation")
    return {"status": "passed", "seconds": kwargs["seconds"]}


def _fake_signal_qa(**_kwargs) -> dict:
    return {
        "status": "passed",
        "blackdetect": {"event_count": 0},
        "silencedetect": {"event_count": 0},
    }


def _build(fixture: dict[str, Path]) -> dict:
    return source_candidate.build_source_adaptive_short_candidate(
        episode_dir=fixture["episode"],
        output_dir=fixture["output"],
        candidate_plan_input_path=fixture["plan"],
        base_dir=fixture["root"],
        render_executor=_fake_render,
        navigation_executor=_fake_navigation,
        signal_qa_executor=_fake_signal_qa,
    )


def test_builds_source_specific_overlay_package_with_self_integrity(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    result = _build(fixture)
    readback = result["readback"]
    assert readback["state"] == source_candidate.STATE
    assert readback["source_identity"]["provider_id"] == "SOURCE_OVERLAY"
    assert readback["caption"]["mode"] == source_candidate.CAPTION_MODE_OVERLAY
    assert readback["caption"]["count"] == 2
    assert readback["render"]["execution_count"] == 1
    assert (fixture["output"] / "candidate_subtitles.ass").is_file()
    assert (fixture["output"] / "candidate_subtitles.srt").is_file()
    manifest = json.loads(
        (fixture["output"] / "candidate_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["candidate_video_sha256"] == readback["video"]["sha256"]
    assert manifest["manifest_self_integrity"]["sha256"] == (
        source_candidate._canonical_manifest_self_hash(manifest)
    )
    assert manifest["file_count"] == len(manifest["files"])
    first_manifest_bytes = (fixture["output"] / "candidate_manifest.json").read_bytes()
    _build(fixture)
    assert (fixture["output"] / "candidate_manifest.json").read_bytes() == (
        first_manifest_bytes
    )


def test_builds_native_baked_mode_without_overlay_double_display(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path, native=True)
    readback = _build(fixture)["readback"]
    assert readback["source_identity"]["provider_id"] == "SOURCE_NATIVE"
    assert readback["caption"]["native_baked_caption_only"] is True
    assert readback["caption"]["overlay_burn_in_applied"] is False
    assert (fixture["output"] / "official_captions.json3").is_file()
    assert not (fixture["output"] / "candidate_subtitles.ass").exists()
    assert not (fixture["output"] / "candidate_subtitles.srt").exists()


def test_rejects_tampered_endpoint_binding_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan["endpoint_binding"]["selection_sha256"] = "0" * 64
    _write_json(fixture["plan"], plan)

    def _must_not_render(**_kwargs) -> dict:
        raise AssertionError("renderer must not run")

    with pytest.raises(
        source_candidate.SourceAdaptiveShortCandidateError,
        match="endpoint is not ready for render",
    ):
        source_candidate.build_source_adaptive_short_candidate(
            episode_dir=fixture["episode"],
            output_dir=fixture["output"],
            candidate_plan_input_path=fixture["plan"],
            base_dir=fixture["root"],
            render_executor=_must_not_render,
            navigation_executor=_fake_navigation,
            signal_qa_executor=_fake_signal_qa,
        )


def test_rejects_native_and_overlay_conflict_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = json.loads(fixture["plan"].read_text(encoding="utf-8"))
    plan.pop("endpoint_binding")
    plan["caption_policy"]["native_captions_visible"] = True
    preflight = json.loads(fixture["preflight"].read_text(encoding="utf-8"))
    selection = json.loads(fixture["selection"].read_text(encoding="utf-8"))
    _write_json(fixture["plan"], endpoint.bind_builder_input(plan, preflight, selection))

    def _must_not_render(**_kwargs) -> dict:
        raise AssertionError("renderer must not run")

    with pytest.raises(
        source_candidate.SourceAdaptiveShortCandidateError,
        match="display/crop conflict",
    ):
        source_candidate.build_source_adaptive_short_candidate(
            episode_dir=fixture["episode"],
            output_dir=fixture["output"],
            candidate_plan_input_path=fixture["plan"],
            base_dir=fixture["root"],
            render_executor=_must_not_render,
            navigation_executor=_fake_navigation,
            signal_qa_executor=_fake_signal_qa,
        )
