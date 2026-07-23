from __future__ import annotations

from array import array
import json
from pathlib import Path
import subprocess

import pytest

from src.cli import build_editorial_video_candidate as cli
from src.cli import main as cli_main
from src.integrations.render import editorial_video_candidate as candidate
from src.integrations.render.subtitle_overlay_visual_proof import (
    ED10L_KEIFONT_CANDIDATE_ID,
    _diagnostic_ass_style_for_candidate,
    _subtitle_layout_contract,
)
from src.integrations.render.subtitle_preset_selector import select_subtitle_preset


def _directory_link_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
        return
    except OSError:
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip("directory symlink/junction creation is unavailable")


def _pcm_fixture_bytes(offset: int = 0) -> bytes:
    samples = array("h")
    amplitudes = [400, 1200, 3000, 800, 5000, 2000, 6500, 900, 4200, 1500]
    for amplitude in amplitudes:
        samples.extend([amplitude + offset] * candidate.PCM_FRAME_SAMPLES)
    return samples.tobytes()


def _closed_manifest(
    root: Path,
    *,
    artifact_id: str = "clip-out13-editorial-video-candidate-v1-002",
) -> dict:
    rows = [
        {
            "repo_relative_path": path.relative_to(root).as_posix(),
            "sha256": candidate._sha256(path),
            "byte_size": path.stat().st_size,
        }
        for path in sorted(item for item in root.rglob("*") if item.is_file())
        if path.name != "run_manifest.json"
    ]
    manifest = {
        "schema_version": candidate.MANIFEST_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "state": candidate.READY_STATE,
        "files": rows,
        "file_count": len(rows),
        "closed_file_set": {
            "status": "passed",
            "excluded_paths": ["run_manifest.json"],
            "payload_tree_digest_sha256": candidate._payload_tree_digest(rows),
        },
        "manifest_self_integrity": {"sha256": None},
    }
    manifest["manifest_self_integrity"]["sha256"] = candidate._manifest_self_hash(
        manifest
    )
    return manifest


def _rewrite_manifest_integrity(manifest: dict) -> None:
    manifest["manifest_self_integrity"]["sha256"] = candidate._manifest_self_hash(
        manifest
    )


def _plan() -> dict:
    return {
        "schema_version": candidate.PLAN_SCHEMA_VERSION,
        "source": {
            "identity": "youtube:AbCdEf12345",
            "provider_locator": "https://www.youtube.com/watch?v=AbCdEf12345",
            "sha256": "a" * 64,
            "duration_seconds": 120.0,
        },
        "cuts": [
            {
                "cut_id": "cut_001",
                "output_order": 1,
                "section": "setup",
                "editorial_role": "challenge_setup",
                "source_in_seconds": 0.0,
                "source_out_seconds": 20.0,
                "selection_reason": "caption evidence states the challenge",
                "direct_evidence_segment_ids": ["seg_001"],
                "transition": "sequence_start",
                "context_evidence": {
                    "continuity_note": "source opening establishes the goal",
                    "segment_ids": [],
                },
            },
            {
                "cut_id": "cut_002",
                "output_order": 2,
                "section": "development",
                "editorial_role": "first_resolution",
                "source_in_seconds": 30.0,
                "source_out_seconds": 55.0,
                "selection_reason": "caption evidence resolves the first encounter",
                "direct_evidence_segment_ids": ["seg_002"],
                "transition": "hard_cut",
                "context_evidence": {
                    "continuity_note": "the omitted wait does not change the stated goal",
                    "segment_ids": ["seg_001"],
                },
            },
            {
                "cut_id": "cut_003",
                "output_order": 3,
                "section": "resolution",
                "editorial_role": "final_resolution",
                "source_in_seconds": 70.0,
                "source_out_seconds": 100.0,
                "selection_reason": "caption evidence closes the challenge",
                "direct_evidence_segment_ids": ["seg_003"],
                "transition": "hard_cut",
                "context_evidence": {
                    "continuity_note": "the final exchange retains cause and result",
                    "segment_ids": ["seg_002"],
                },
            },
        ],
        "omitted_ranges": [
            {
                "omitted_id": "omit_001",
                "source_in_seconds": 20.0,
                "source_out_seconds": 30.0,
                "omission_reason": "redundant wait",
                "transcript_segment_ids": [],
                "intentional_editorial_omission": True,
            },
            {
                "omitted_id": "omit_002",
                "source_in_seconds": 55.0,
                "source_out_seconds": 70.0,
                "omission_reason": "repeated action",
                "transcript_segment_ids": [],
                "intentional_editorial_omission": True,
            },
            {
                "omitted_id": "omit_003",
                "source_in_seconds": 100.0,
                "source_out_seconds": 120.0,
                "omission_reason": "credits",
                "transcript_segment_ids": [],
                "intentional_editorial_omission": False,
            },
        ],
    }


def _transcript() -> dict:
    return {
        "segments": [
            {"id": "seg_001", "start_seconds": 1.0, "end_seconds": 10.0},
            {"id": "seg_002", "start_seconds": 31.0, "end_seconds": 50.0},
            {"id": "seg_003", "start_seconds": 72.0, "end_seconds": 95.0},
        ]
    }


def _caption_events() -> list[dict]:
    return [
        {
            "event_id": "event_001",
            "source_start_seconds": 1.0,
            "source_end_seconds": 5.0,
            "text": "challenge",
            "text_sha256": "b" * 64,
        },
        {
            "event_id": "event_002",
            "source_start_seconds": 31.0,
            "source_end_seconds": 35.0,
            "text": "development",
            "text_sha256": "c" * 64,
        },
        {
            "event_id": "event_003",
            "source_start_seconds": 72.0,
            "source_end_seconds": 75.0,
            "text": "resolution",
            "text_sha256": "d" * 64,
        },
    ]


def _authority_fixture(tmp_path: Path) -> dict:
    source = tmp_path / "source.mp4"
    audio = tmp_path / "source.wav"
    caption = tmp_path / "caption.json3"
    transcript_path = tmp_path / "transcript.json"
    rights = tmp_path / "rights.json"
    receipt = tmp_path / "source_receipt.json"
    audio_receipt = tmp_path / "source_audio_receipt.json"
    ledger = tmp_path / "material_ledger.json"
    evidence = tmp_path / "caption_evidence.json"
    caption_receipt = tmp_path / "caption_acquisition_receipt.json"
    source.write_bytes(_pcm_fixture_bytes())
    audio.write_bytes(_pcm_fixture_bytes())
    caption.write_text('{"events":[]}\n', encoding="utf-8")
    source_sha = candidate._sha256(source)
    audio_sha = candidate._sha256(audio)
    transcript = {
        "source_audio": {
            "path": str(audio),
            "material_id": "source-audio",
            "sha256": audio_sha,
            "duration_seconds": len(_pcm_fixture_bytes())
            / candidate.PCM_SAMPLE_WIDTH_BYTES
            / candidate.PCM_SAMPLE_RATE_HZ,
            "sample_rate_hz": candidate.PCM_SAMPLE_RATE_HZ,
            "channels": candidate.PCM_CHANNELS,
        },
        "stt": {
            "provider": "youtube_subtitles",
            "engine_version": "youtube-json3",
            "model": str(caption),
        },
    }
    transcript_path.write_text(
        json.dumps(transcript, ensure_ascii=False), encoding="utf-8"
    )
    rights.write_text(
        json.dumps(
            {
                "source_video": {
                    "url": "https://www.youtube.com/watch?v=AbCdEf12345"
                },
                "compliance_check": {"status": "pending"},
            }
        ),
        encoding="utf-8",
    )
    receipt.write_text(
        json.dumps({"output_path": str(source), "sha256": source_sha}),
        encoding="utf-8",
    )
    audio_receipt.write_text(
        json.dumps(
            {
                "mode": "yt-dlp-audio",
                "provider": "yt-dlp",
                "output_path": str(audio),
                "sha256": audio_sha,
                "byte_size": audio.stat().st_size,
                "tools": [
                    {"name": "yt-dlp", "version": "test"},
                    {"name": "ffmpeg", "version": "test"},
                ],
                "commands": [
                    {"summary": "yt-dlp", "exit_code": 0},
                    {"summary": "ffmpeg", "exit_code": 0},
                ],
                "outputs": [
                    {
                        "path": str(audio),
                        "sha256": audio_sha,
                        "byte_size": audio.stat().st_size,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    ledger.write_text(
        json.dumps(
            {
                "materials": [
                    {
                        "id": "source-video",
                        "kind": "source_video",
                        "file_path": str(source),
                        "hash_sha256": source_sha,
                    },
                    {
                        "id": "source-audio",
                        "kind": "source_audio",
                        "file_path": str(audio),
                        "hash_sha256": audio_sha,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    caption_receipt.write_text(
        json.dumps(
            {
                "schema_version": "clippipegen.caption_acquisition_verification.v1",
                "receipt_kind": "caption_acquisition_verification",
                "status": "passed",
                "source_identity": "youtube:AbCdEf12345",
                "provider": {
                    "name": "youtube",
                    "video_id": "AbCdEf12345",
                    "locator": "https://www.youtube.com/watch?v=AbCdEf12345",
                },
                "acquisition": {
                    "language": "ja",
                    "format": "json3",
                    "retrieved_sha256": candidate._sha256(caption),
                    "retrieved_byte_size": caption.stat().st_size,
                    "method": {
                        "name": "yt_dlp_anonymous_subtitle_sha256_v1",
                        "anonymous": True,
                        "credentials_used": False,
                        "cookies_used": False,
                        "oauth_used": False,
                        "mfa_used": False,
                        "tool": "yt-dlp",
                        "tool_version": "test",
                        "exit_code": 0,
                    },
                },
                "local_caption": {
                    "path": str(caption),
                    "sha256": candidate._sha256(caption),
                    "byte_size": caption.stat().st_size,
                },
                "result": {
                    "status": "passed",
                    "provider_identity_verified": True,
                    "exact_caption_bytes_verified": True,
                    "official_authorship_claim": False,
                },
            }
        ),
        encoding="utf-8",
    )
    evidence.write_text(
        json.dumps(
            {
                "source_refs": {
                    "transcript": {
                        "provider": "youtube_subtitles",
                        "model": str(caption),
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    artifact_id = "clip-out13-editorial-video-candidate-v1-002"
    plan = {
        "artifact_id": artifact_id,
        "authority_binding": {
            "source_identity": "youtube:AbCdEf12345",
            "source_sha256": source_sha,
            "transcript_sha256": candidate._sha256(transcript_path),
            "caption_sha256": candidate._sha256(caption),
            "rights_sha256": candidate._sha256(rights),
            "source_material_id": "source-video",
            "caption_classification": "provider_json3_sidecar",
            "evidence": {
                "source_receipt": {
                    "path": str(receipt),
                    "sha256": candidate._sha256(receipt),
                },
                "material_ledger": {
                    "path": str(ledger),
                    "sha256": candidate._sha256(ledger),
                },
                "caption_provenance": {
                    "path": str(evidence),
                    "sha256": candidate._sha256(evidence),
                },
                "caption_acquisition_receipt": {
                    "path": str(caption_receipt),
                    "sha256": candidate._sha256(caption_receipt),
                },
                "source_audio_receipt": {
                    "path": str(audio_receipt),
                    "sha256": candidate._sha256(audio_receipt),
                },
            },
        },
    }
    return {
        "root": tmp_path,
        "plan": plan,
        "artifact_id": artifact_id,
        "resolved": {
            "source_identity": "youtube:AbCdEf12345",
            "source_sha256": source_sha,
            "source_path": source,
            "rights_sha256": candidate._sha256(rights),
        },
        "transcript_path": transcript_path,
        "transcript": transcript,
        "caption_track_path": caption,
        "rights_manifest_path": rights,
        "pcm_decoder": lambda path: path.read_bytes(),
    }


def test_cli_dispatch_registers_out13() -> None:
    assert "build-editorial-video-candidate" in cli_main.SUBCOMMANDS


def test_editorial_timeline_is_explicit_nonuniform_and_traceable() -> None:
    timeline = candidate.build_editorial_timeline(
        plan=_plan(),
        source_identity="youtube:AbCdEf12345",
        source_sha256="a" * 64,
        source_duration_seconds=120.0,
        transcript=_transcript(),
        caption_events=_caption_events(),
    )

    assert timeline["selection_mode"] == "explicit_caption_evidence_editorial_plan"
    assert timeline["uniform_sampling_used"] is False
    assert timeline["arbitrary_thirds_used"] is False
    assert timeline["cut_count"] == 3
    assert timeline["intentional_omitted_span_count"] == 2
    assert timeline["output_duration_seconds"] == 75.0
    assert timeline["source_utilization_ratio"] == 0.625
    assert [row["section"] for row in timeline["cuts"]] == [
        "setup",
        "development",
        "resolution",
    ]


def test_editorial_timeline_rejects_missing_caption_evidence() -> None:
    plan = _plan()
    plan["cuts"][1]["direct_evidence_segment_ids"] = []

    with pytest.raises(candidate.EditorialVideoCandidateError, match="transcript evidence"):
        candidate.build_editorial_timeline(
            plan=plan,
            source_identity="youtube:AbCdEf12345",
            source_sha256="a" * 64,
            source_duration_seconds=120.0,
            transcript=_transcript(),
            caption_events=_caption_events(),
        )


def test_editorial_filter_burns_ass_after_real_cut_concat(tmp_path: Path) -> None:
    ass = tmp_path / "subtitle.ass"
    font = tmp_path / "font.ttf"
    ass.write_text("[Script Info]\n", encoding="utf-8")
    font.write_bytes(b"font")
    timeline = candidate.build_editorial_timeline(
        plan=_plan(),
        source_identity="youtube:AbCdEf12345",
        source_sha256="a" * 64,
        source_duration_seconds=120.0,
        transcript=_transcript(),
        caption_events=_caption_events(),
    )

    script = candidate.render_editorial_filter_complex(
        cuts=timeline["cuts"], ass_path=ass, font_file=font
    )

    assert script.count("[0:v:0]trim=start=") == 3
    assert "concat=n=3:v=1:a=1[vcat][acat]" in script
    assert "ass=filename=" in script
    assert "fontsdir=" in script
    assert "loudnorm=I=-15:TP=-2.0" in script


def test_subtitle_readback_exposes_resolved_values_without_speaker_inference() -> None:
    style = _diagnostic_ass_style_for_candidate(ED10L_KEIFONT_CANDIDATE_ID)
    layout = _subtitle_layout_contract(
        frame_width=1920,
        frame_height=1080,
        mode="bottom_center_emphasis",
        dimension_source="test",
        diagnostic_ass_style=style,
    )
    selector = select_subtitle_preset(
        {
            "speaker_id": "unknown",
            "speaker_role": "unknown",
            "emotion": "neutral",
            "intensity": 0,
            "utterance_role": "dialogue",
            "readability_priority": "maximum",
        }
    )
    readback = candidate.build_subtitle_presentation_readback(
        layout=layout,
        presentation_items=[
            {
                "subtitle_id": "caption_0001",
                "display_start_seconds": 0.0,
                "display_end_seconds": 1.0,
                "wrapped_lines": ["読みやすい字幕"],
                "wrapped_line_count": 1,
                "suspicious_tail_line_present": False,
                "font_bbox_wrap_readback": {
                    "selected_measurement": {"width": 300}
                },
            }
        ],
        selector=selector,
        caption_readback={
            "status": "passed",
            "overlap_count": 0,
            "negative_duration_count": 0,
            "orphan_cue_count": 0,
        },
        font_sha256="c" * 64,
    )

    assert readback["status"] == "passed"
    assert readback["body_text"]["fill"] == "#ffffff"
    assert readback["badge_accent"]["speaker_identity_verified"] is False
    assert readback["badge_accent"]["badge_rendered"] is False
    assert readback["outline_shadow"]["outline_pixels"] > 0
    assert readback["safe_area"]["overflow_count"] == 0
    assert "official" not in readback["line_break"]["authority_whitespace_policy"]


def test_caption_presentation_normalizes_provider_line_breaks_before_wrap() -> None:
    source = "偶然にも魔導書(ホロモワール)の \n 召喚呪文と一致したでござる！"

    assert candidate._caption_text_for_presentation(source) == (
        "偶然にも魔導書(ホロモワール)の 召喚呪文と一致したでござる！"
    )


def test_editorial_layout_resolves_readable_two_line_scale() -> None:
    style = _diagnostic_ass_style_for_candidate(ED10L_KEIFONT_CANDIDATE_ID)

    layout = candidate._editorial_subtitle_layout_contract(
        frame_width=1920,
        frame_height=1080,
        dimension_source="test",
        diagnostic_ass_style=style,
    )

    assert layout["mode"] == "bottom_center_emphasis"
    assert layout["values"]["font_size"] == 100
    assert layout["values"]["line_height"] == 115
    assert layout["values"]["outline"] == 8
    assert layout["values"]["bottom_margin"] == 92


def test_subtitle_readback_uses_measured_width_by_line_for_safe_area() -> None:
    style = _diagnostic_ass_style_for_candidate(ED10L_KEIFONT_CANDIDATE_ID)
    layout = _subtitle_layout_contract(
        frame_width=1920,
        frame_height=1080,
        mode="bottom_center_emphasis",
        dimension_source="test",
        diagnostic_ass_style=style,
    )
    selector = select_subtitle_preset(
        {
            "speaker_id": "unknown",
            "speaker_role": "unknown",
            "emotion": "neutral",
            "intensity": 0,
            "utterance_role": "dialogue",
            "readability_priority": "maximum",
        }
    )

    readback = candidate.build_subtitle_presentation_readback(
        layout=layout,
        presentation_items=[
            {
                "subtitle_id": "caption_overflow",
                "display_start_seconds": 0.0,
                "display_end_seconds": 1.0,
                "wrapped_lines": ["幅超過"],
                "wrapped_line_count": 1,
                "suspicious_tail_line_present": False,
                "font_bbox_wrap_readback": {
                    "measured_width_by_line": [2000],
                },
            }
        ],
        selector=selector,
        caption_readback={
            "status": "passed",
            "overlap_count": 0,
            "negative_duration_count": 0,
            "orphan_cue_count": 0,
        },
        font_sha256="c" * 64,
    )

    assert readback["status"] == "failed"
    assert readback["safe_area"]["overflow_count"] == 1
    assert readback["violations"] == ["caption_overflow:safe_width_overflow"]


def test_cli_orchestrates_resume(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_build(**kwargs):
        captured.update(kwargs)
        return {
            "artifact_id": "clip-out13-editorial-video-candidate-v1-002",
            "state": candidate.READY_STATE,
            "source_identity": "youtube:AbCdEf12345",
            "duration_seconds": 75.0,
            "cut_count": 3,
            "omitted_span_count": 2,
            "final_video": tmp_path / "final_video.mp4",
            "review_index": tmp_path / "review" / "index.html",
            "resume": True,
        }

    monkeypatch.setattr(cli, "build_editorial_video_candidate", _fake_build)
    code = cli.run(
        [
            "--artifact-id",
            "clip-out13-editorial-video-candidate-v1-002",
            "--source",
            str(tmp_path / "source.mp4"),
            "--source-identity",
            "youtube:AbCdEf12345",
            "--editorial-plan",
            str(tmp_path / "plan.json"),
            "--transcript",
            str(tmp_path / "transcript.json"),
            "--caption-track",
            str(tmp_path / "caption.json3"),
            "--rights-manifest",
            str(tmp_path / "rights.json"),
            "--output-dir",
            str(tmp_path / "out"),
            "--resume",
            "--format",
            "json",
        ]
    )

    assert code == 0
    assert captured["resume"] is True
    assert captured["force"] is False
    assert captured["artifact_id"] == "clip-out13-editorial-video-candidate-v1-002"


def test_manifest_self_integrity_and_resume_fingerprint(tmp_path: Path) -> None:
    (tmp_path / "final_video.mp4").write_bytes(b"video")
    (tmp_path / "timeline_ir.json").write_text("{}\n", encoding="utf-8")
    manifest = candidate.build_run_manifest(
        artifact_id="clip-out13-editorial-video-candidate-v1-002",
        stage=tmp_path,
        input_fingerprint="d" * 64,
        resolved={
            "source_identity": "youtube:AbCdEf12345",
            "source_sha256": "a" * 64,
            "source_byte_size": 123,
            "caption_sha256": "b" * 64,
            "rights_sha256": "c" * 64,
        },
        source_probe={
            "duration_seconds": 120.0,
            "resolution": "1920x1080",
        },
        timeline={
            "selection_mode": "explicit_caption_evidence_editorial_plan",
            "cut_count": 3,
            "semantic_section_count": 3,
            "omitted_ranges": [{"omitted_id": "omit_001"}],
            "source_utilization_ratio": 0.625,
        },
        subtitle_readback={
            "status": "passed",
            "cue_count": 1,
            "typography_decoration_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
            "resolved_font_family": "Keifont",
            "resolved_font_file_sha256": "e" * 64,
            "outline_shadow": {},
            "safe_area": {},
            "line_break": {},
        },
        validation={
            "status": "passed",
            "mapping_coverage": {"coverage_ratio": 1.0},
            "media": {
                "sha256": candidate._sha256(tmp_path / "final_video.mp4"),
                "byte_size": 5,
                "duration_seconds": 75.0,
                "resolution": "1920x1080",
            },
        },
        review={"clean_url": "http://127.0.0.1:8076/review/index.html"},
        plan_sha256="f" * 64,
        transcript_sha256="0" * 64,
    )
    (tmp_path / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    candidate.validate_run_manifest(
        tmp_path,
        manifest,
        expected_artifact_id="clip-out13-editorial-video-candidate-v1-002",
    )
    package_digest_before = candidate._package_tree_digest(tmp_path)
    resumed = candidate.resume_existing_output(
        output_dir=tmp_path,
        input_fingerprint="d" * 64,
        artifact_id="clip-out13-editorial-video-candidate-v1-002",
    )

    assert resumed["resume"] is True
    assert resumed["package_tree_digest"] == package_digest_before
    assert candidate._package_tree_digest(tmp_path) == package_digest_before
    assert not (tmp_path / "resume_readback.json").exists()
    assert resumed["resume_readback"].is_file()
    assert resumed["resume_readback"].parent == candidate._run_journal_dir(tmp_path)
    assert resumed["video_sha256"] == candidate._sha256(
        tmp_path / "final_video.mp4"
    )
    with pytest.raises(candidate.EditorialVideoCandidateError, match="fingerprint mismatch"):
        candidate.resume_existing_output(
            output_dir=tmp_path,
            input_fingerprint="1" * 64,
            artifact_id="clip-out13-editorial-video-candidate-v1-002",
        )


def test_editorial_timeline_rejects_unsupported_transition() -> None:
    plan = _plan()
    plan["cuts"][1]["transition"] = "hard_cut_after_wait_omission"

    with pytest.raises(candidate.EditorialVideoCandidateError, match="unsupported transition"):
        candidate.build_editorial_timeline(
            plan=plan,
            source_identity="youtube:AbCdEf12345",
            source_sha256="a" * 64,
            source_duration_seconds=120.0,
            transcript=_transcript(),
            caption_events=_caption_events(),
        )


def test_editorial_timeline_rejects_extra_or_split_evidence() -> None:
    plan = _plan()
    plan["cuts"][0]["direct_evidence_segment_ids"].append("seg_002")

    with pytest.raises(candidate.EditorialVideoCandidateError, match="exactly match"):
        candidate.build_editorial_timeline(
            plan=plan,
            source_identity="youtube:AbCdEf12345",
            source_sha256="a" * 64,
            source_duration_seconds=120.0,
            transcript=_transcript(),
            caption_events=_caption_events(),
        )


def test_editorial_timeline_rejects_split_caption_boundary() -> None:
    plan = _plan()
    plan["cuts"][0]["source_out_seconds"] = 4.0
    plan["cuts"][0]["direct_evidence_segment_ids"] = ["seg_001"]
    transcript = _transcript()
    transcript["segments"][0]["end_seconds"] = 4.0

    with pytest.raises(candidate.EditorialVideoCandidateError, match="splits caption"):
        candidate.build_editorial_timeline(
            plan=plan,
            source_identity="youtube:AbCdEf12345",
            source_sha256="a" * 64,
            source_duration_seconds=120.0,
            transcript=transcript,
            caption_events=_caption_events(),
        )


def test_editorial_timeline_rejects_incomplete_omitted_complement() -> None:
    plan = _plan()
    plan["omitted_ranges"][-1]["source_in_seconds"] = 101.0

    with pytest.raises(candidate.EditorialVideoCandidateError, match="source complement"):
        candidate.build_editorial_timeline(
            plan=plan,
            source_identity="youtube:AbCdEf12345",
            source_sha256="a" * 64,
            source_duration_seconds=120.0,
            transcript=_transcript(),
            caption_events=_caption_events(),
        )


def test_manifest_rejects_cross_candidate_identity(tmp_path: Path) -> None:
    (tmp_path / "final_video.mp4").write_bytes(b"video")
    manifest = {
        "schema_version": candidate.MANIFEST_SCHEMA_VERSION,
        "artifact_id": "clip-out13-editorial-video-candidate-v1-002",
        "state": candidate.READY_STATE,
        "files": [],
        "file_count": 0,
        "manifest_self_integrity": {"sha256": None},
    }
    manifest["manifest_self_integrity"]["sha256"] = candidate._manifest_self_hash(
        manifest
    )

    with pytest.raises(candidate.EditorialVideoCandidateError, match="identity mismatch"):
        candidate.validate_run_manifest(
            tmp_path,
            manifest,
            expected_artifact_id="clip-out13-editorial-video-candidate-v1-003",
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("unexpected", "closed file set mismatch"),
        ("nested_manifest", "closed file set mismatch"),
        ("missing", "payload mismatch"),
        ("altered", "payload mismatch"),
        ("duplicate", "duplicate payload path"),
        ("unsafe", "unsafe payload path"),
        ("count", "file count mismatch"),
    ],
)
def test_manifest_rejects_non_closed_or_unsafe_payload_sets(
    tmp_path: Path, mutation: str, message: str
) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}\n", encoding="utf-8")
    manifest = _closed_manifest(tmp_path)
    (tmp_path / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if mutation == "unexpected":
        (tmp_path / "unexpected.txt").write_text("unexpected", encoding="utf-8")
    elif mutation == "nested_manifest":
        nested = tmp_path / "review" / "run_manifest.json"
        nested.parent.mkdir()
        nested.write_text("{}\n", encoding="utf-8")
    elif mutation == "missing":
        payload.unlink()
    elif mutation == "altered":
        payload.write_text('{"changed":true}\n', encoding="utf-8")
    elif mutation == "duplicate":
        manifest["files"].append(dict(manifest["files"][0]))
        manifest["file_count"] = len(manifest["files"])
        manifest["closed_file_set"][
            "payload_tree_digest_sha256"
        ] = candidate._payload_tree_digest(manifest["files"])
        _rewrite_manifest_integrity(manifest)
    elif mutation == "unsafe":
        manifest["files"][0]["repo_relative_path"] = "../payload.json"
        manifest["closed_file_set"][
            "payload_tree_digest_sha256"
        ] = candidate._payload_tree_digest(manifest["files"])
        _rewrite_manifest_integrity(manifest)
    elif mutation == "count":
        manifest["file_count"] = 99
        _rewrite_manifest_integrity(manifest)

    with pytest.raises(candidate.EditorialVideoCandidateError, match=message):
        candidate.validate_run_manifest(
            tmp_path,
            manifest,
            expected_artifact_id="clip-out13-editorial-video-candidate-v1-002",
        )


@pytest.mark.parametrize(
    "requested_id",
    [
        "clip-out13-editorial-video-candidate-v1-002",
        "clip-out13-editorial-video-candidate-v1-003",
    ],
)
def test_successful_output_rejects_rerun_without_package_mutation(
    tmp_path: Path, requested_id: str
) -> None:
    package = tmp_path / "candidate"
    package.mkdir()
    (package / "payload.json").write_text("{}\n", encoding="utf-8")
    manifest = _closed_manifest(package)
    (package / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    before = candidate._package_tree_digest(package)

    with pytest.raises(candidate.EditorialVideoCandidateError):
        candidate._validate_output_allocation(
            output=package,
            artifact_id=requested_id,
            force=True,
        )
    candidate.write_failure_state(
        artifact_id=requested_id,
        output_dir=package,
        run_journal_dir=None,
        stage="source_resolution",
        message="rejected allocation probe",
        input_fingerprint=None,
        failure_evidence_dir=None,
    )

    assert candidate._package_tree_digest(package) == before
    assert not (package / "pipeline_failure.json").exists()
    assert (
        candidate._run_journal_dir(package) / "pipeline_failure.json"
    ).is_file()


@pytest.mark.parametrize(
    ("schema_version", "state", "existing_id"),
    [
        (
            "clippipegen.out13.run_manifest.v2",
            "OUT13_EVIDENCE_BOUND_REVIEWABLE_ON_THANK_V1",
            "clip-out13-editorial-video-candidate-v1-003",
        ),
        (
            "unknown.manifest.v99",
            "UNKNOWN_STATE",
            "clip-out13-editorial-video-candidate-v1-002",
        ),
        (None, None, None),
    ],
)
def test_historical_or_malformed_manifest_directory_is_permanently_immutable(
    tmp_path: Path,
    schema_version: str | None,
    state: str | None,
    existing_id: str | None,
) -> None:
    package = tmp_path / "historical"
    package.mkdir()
    (package / "payload.bin").write_bytes(b"historical")
    manifest_path = package / "run_manifest.json"
    if schema_version is None:
        manifest_path.write_text("{malformed", encoding="utf-8")
    else:
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": schema_version,
                    "state": state,
                    "artifact_id": existing_id,
                }
            ),
            encoding="utf-8",
        )
    before = candidate._package_tree_digest(package)

    with pytest.raises(candidate.EditorialVideoCandidateError, match="immutable"):
        candidate._validate_output_allocation(
            output=package,
            artifact_id="clip-out13-editorial-video-candidate-v1-003",
            force=True,
        )

    assert candidate._package_tree_digest(package) == before


def test_immutable_promotion_refuses_race_without_replacing_stage_or_output(
    tmp_path: Path,
) -> None:
    stage = tmp_path / ".candidate.staging"
    output = tmp_path / "candidate"
    stage.mkdir()
    (stage / "payload.bin").write_bytes(b"new")
    candidate._validate_output_allocation(
        output=output,
        artifact_id="clip-out13-editorial-video-candidate-v1-005",
        force=False,
    )
    output.mkdir()
    (output / "sentinel.bin").write_bytes(b"race-winner")

    with pytest.raises(candidate.EditorialVideoCandidateError, match="claimed"):
        candidate._promote_output_immutable(stage=stage, output=output)

    assert (output / "sentinel.bin").read_bytes() == b"race-winner"
    assert (stage / "payload.bin").read_bytes() == b"new"


@pytest.mark.parametrize(
    "requested_factory",
    [
        lambda output: output,
        lambda output: output / "journal",
        lambda output: output.parent
        / "alias"
        / ".."
        / f"{output.name}.run_journal",
    ],
)
def test_run_journal_rejects_package_and_alias_overrides(
    tmp_path: Path, requested_factory
) -> None:
    output = tmp_path / "candidate"
    output.mkdir()
    requested = requested_factory(output)

    with pytest.raises(candidate.EditorialVideoCandidateError, match="run journal"):
        candidate._validated_run_journal_dir(output, requested=requested)


def test_run_journal_rejects_symlink_alias(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    output.mkdir()
    expected = candidate._run_journal_dir(output.resolve())
    target = tmp_path / "journal-target"
    target.mkdir()
    _directory_link_or_skip(expected, target)

    with pytest.raises(candidate.EditorialVideoCandidateError, match="symlink"):
        candidate._validated_run_journal_dir(output, requested=expected)


def test_manifest_rejects_symlink_payload_and_external_target(tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    (external / "payload.bin").write_bytes(b"external")
    link = package / "external-link"
    _directory_link_or_skip(link, external)
    manifest = _closed_manifest(package)

    with pytest.raises(candidate.EditorialVideoCandidateError, match="symlink"):
        candidate.validate_run_manifest(
            package,
            manifest,
            expected_artifact_id="clip-out13-editorial-video-candidate-v1-002",
        )


def test_authority_binding_accepts_provider_sidecar_lineage(tmp_path: Path) -> None:
    result = candidate._validate_authority_binding(**_authority_fixture(tmp_path))

    assert result["status"] == "passed"
    assert result["caption"]["classification"] == "provider_json3_sidecar"
    assert result["caption"]["provider_video_id"] == "AbCdEf12345"
    assert result["caption"]["official_authorship_claim"] is False
    assert result["transcript"]["source_video_audio_lineage"]["equivalent"] is True
    assert (
        result["transcript"]["source_video_audio_lineage"]["lineage_class"]
        == "content_verified_exact_source_audio"
    )


def test_out13_module_has_no_default_artifact_identity() -> None:
    assert not hasattr(candidate, "ARTIFACT_ID")


def test_authority_binding_rejects_source_audio_self_reference_without_derivation(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path)
    fixture.pop("pcm_decoder")

    with pytest.raises(
        candidate.EditorialVideoCandidateError,
        match="requires canonical PCM decode evidence",
    ):
        candidate._validate_authority_binding(**fixture)


def test_authority_binding_rejects_mismatched_source_pcm(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path)
    audio_path = tmp_path / "source.wav"
    audio_path.write_bytes(_pcm_fixture_bytes(offset=9000))
    audio_sha = candidate._sha256(audio_path)
    fixture["transcript"]["source_audio"]["sha256"] = audio_sha
    fixture["transcript_path"].write_text(
        json.dumps(fixture["transcript"], ensure_ascii=False),
        encoding="utf-8",
    )
    fixture["plan"]["authority_binding"][
        "transcript_sha256"
    ] = candidate._sha256(fixture["transcript_path"])
    ledger_path = tmp_path / "material_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["materials"][1]["hash_sha256"] = audio_sha
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    fixture["plan"]["authority_binding"]["evidence"]["material_ledger"][
        "sha256"
    ] = candidate._sha256(ledger_path)
    audio_receipt_path = tmp_path / "source_audio_receipt.json"
    audio_receipt = json.loads(audio_receipt_path.read_text(encoding="utf-8"))
    audio_receipt["sha256"] = audio_sha
    audio_receipt["byte_size"] = audio_path.stat().st_size
    audio_receipt["outputs"][0]["sha256"] = audio_sha
    audio_receipt["outputs"][0]["byte_size"] = audio_path.stat().st_size
    audio_receipt_path.write_text(json.dumps(audio_receipt), encoding="utf-8")
    fixture["plan"]["authority_binding"]["evidence"]["source_audio_receipt"][
        "sha256"
    ] = candidate._sha256(audio_receipt_path)

    with pytest.raises(
        candidate.EditorialVideoCandidateError,
        match="not equivalent",
    ):
        candidate._validate_authority_binding(**fixture)


@pytest.mark.parametrize("provider_id", ["WrongId0000", None])
def test_authority_binding_rejects_wrong_or_absent_caption_receipt_identity(
    tmp_path: Path, provider_id: str | None
) -> None:
    fixture = _authority_fixture(tmp_path)
    receipt_path = tmp_path / "caption_acquisition_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["provider"]["video_id"] = provider_id
    receipt["provider"]["locator"] = (
        f"https://www.youtube.com/watch?v={provider_id}" if provider_id else None
    )
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    fixture["plan"]["authority_binding"]["evidence"]["caption_acquisition_receipt"][
        "sha256"
    ] = candidate._sha256(receipt_path)

    with pytest.raises(
        candidate.EditorialVideoCandidateError,
        match="trusted provider lineage root",
    ):
        candidate._validate_authority_binding(**fixture)


def test_authority_binding_rejects_plan_only_caption_identity(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path)
    fixture["plan"]["authority_binding"]["provider_video_id"] = "AbCdEf12345"
    del fixture["plan"]["authority_binding"]["evidence"][
        "caption_acquisition_receipt"
    ]

    with pytest.raises(
        candidate.EditorialVideoCandidateError,
        match="requires caption acquisition receipt",
    ):
        candidate._validate_authority_binding(**fixture)


def test_authority_binding_rejects_generic_handoff_as_caption_receipt(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path)
    receipt_path = tmp_path / "caption_acquisition_receipt.json"
    receipt_path.write_text(
        json.dumps(
            {
                "artifact_kind": "non_repo_artifact_handoff",
                "source_identity": {
                    "youtube_id": "AbCdEf12345",
                    "source_url": "https://www.youtube.com/watch?v=AbCdEf12345",
                },
            }
        ),
        encoding="utf-8",
    )
    fixture["plan"]["authority_binding"]["evidence"]["caption_acquisition_receipt"][
        "sha256"
    ] = candidate._sha256(receipt_path)

    with pytest.raises(
        candidate.EditorialVideoCandidateError,
        match="trusted provider lineage root",
    ):
        candidate._validate_authority_binding(**fixture)


@pytest.mark.parametrize(
    ("mutation", "value"),
    [
        ("retrieved_sha256", "0" * 64),
        ("exact_caption_bytes_verified", False),
        ("anonymous", False),
        ("credentials_used", True),
        ("locator", "https://www.youtube.com/watch?v=WrongId0000"),
    ],
)
def test_authority_binding_rejects_untrusted_caption_receipt_fields(
    tmp_path: Path, mutation: str, value
) -> None:
    fixture = _authority_fixture(tmp_path)
    receipt_path = tmp_path / "caption_acquisition_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if mutation == "retrieved_sha256":
        receipt["acquisition"][mutation] = value
    elif mutation == "exact_caption_bytes_verified":
        receipt["result"][mutation] = value
    elif mutation == "locator":
        receipt["provider"][mutation] = value
    else:
        receipt["acquisition"]["method"][mutation] = value
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    fixture["plan"]["authority_binding"]["evidence"]["caption_acquisition_receipt"][
        "sha256"
    ] = candidate._sha256(receipt_path)

    with pytest.raises(
        candidate.EditorialVideoCandidateError,
        match="trusted provider lineage root",
    ):
        candidate._validate_authority_binding(**fixture)


def test_authority_binding_rejects_invalid_source_identity_namespace(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path)
    fixture["resolved"]["source_identity"] = "youtube-video:AbCdEf12345"
    fixture["plan"]["authority_binding"][
        "source_identity"
    ] = "youtube-video:AbCdEf12345"

    with pytest.raises(candidate.EditorialVideoCandidateError, match="exact youtube"):
        candidate._validate_authority_binding(**fixture)


def test_authority_binding_rejects_tampered_source_audio_receipt(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path)
    receipt_path = tmp_path / "source_audio_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["commands"][0]["exit_code"] = 1
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    fixture["plan"]["authority_binding"]["evidence"]["source_audio_receipt"][
        "sha256"
    ] = candidate._sha256(receipt_path)

    with pytest.raises(candidate.EditorialVideoCandidateError, match="acquisition bytes"):
        candidate._validate_authority_binding(**fixture)


def test_signed_pcm_lineage_accepts_exact_content() -> None:
    payload = _pcm_fixture_bytes()
    result = candidate._compare_canonical_pcm(payload, payload)

    assert result["equivalent"] is True
    assert result["signed_waveform_similarity"] == 1.0
    assert result["coverage_ratio"] == 1.0


def test_signed_pcm_lineage_rejects_equal_energy_different_waveform() -> None:
    source = array("h")
    other = array("h")
    amplitudes = [400, 1200, 3000, 800, 5000, 2000, 6500, 900, 4200, 1500]
    for amplitude in amplitudes:
        source.extend([amplitude] * candidate.PCM_FRAME_SAMPLES)
        other.extend(
            [
                amplitude if index % 2 == 0 else -amplitude
                for index in range(candidate.PCM_FRAME_SAMPLES)
            ]
        )

    result = candidate._compare_canonical_pcm(source.tobytes(), other.tobytes())

    assert result["coarse_frame_energy_correlation"] == pytest.approx(1.0)
    assert result["equivalent"] is False


@pytest.mark.parametrize("mutation", ["polarity", "reordered", "truncated", "unrelated"])
def test_signed_pcm_lineage_rejects_adversarial_content(mutation: str) -> None:
    source = array("h")
    source.frombytes(_pcm_fixture_bytes())
    other = array("h", source)
    if mutation == "polarity":
        other = array("h", (-value for value in source))
    elif mutation == "reordered":
        frames = [
            source[offset : offset + candidate.PCM_FRAME_SAMPLES]
            for offset in range(0, len(source), candidate.PCM_FRAME_SAMPLES)
        ]
        other = array("h")
        for frame in reversed(frames):
            other.extend(frame)
    elif mutation == "truncated":
        other = array("h", source[: -2 * candidate.PCM_FRAME_SAMPLES])
    else:
        other = array(
            "h",
            (
                7000 if index % 7 in {0, 1, 2} else -3500
                for index in range(len(source))
            ),
        )

    result = candidate._compare_canonical_pcm(source.tobytes(), other.tobytes())

    assert result["equivalent"] is False


def test_authority_binding_rejects_arbitrary_official_claim(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path)
    fixture["plan"]["authority_binding"][
        "caption_classification"
    ] = "official_json3_sidecar"

    with pytest.raises(candidate.EditorialVideoCandidateError, match="provenance"):
        candidate._validate_authority_binding(**fixture)


def test_authority_binding_rejects_missing_rights_manifest(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path)
    fixture["rights_manifest_path"].unlink()

    with pytest.raises(candidate.EditorialVideoCandidateError, match="rights manifest"):
        candidate._validate_authority_binding(**fixture)


def test_font_binding_rejects_fallback_identity() -> None:
    artifact_id = "clip-out13-editorial-video-candidate-v1-002"
    style = {
        "requested_font_family": "Keifont",
        "resolved_font_family": "Fallback Sans",
        "font_file_status": "fallback_font_file_found",
    }
    plan = {
        "typography_binding": {
            "artifact_id": artifact_id,
            "typography_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
            "requested_font_family": "Keifont",
            "resolved_font_family": "Fallback Sans",
            "resolved_font_file_sha256": "e" * 64,
        }
    }

    with pytest.raises(candidate.EditorialVideoCandidateError, match="fallback font"):
        candidate._validate_font_binding(
            plan=plan,
            artifact_id=artifact_id,
            style=style,
            font_sha256="e" * 64,
        )


def test_caption_readback_emits_provider_classification_without_official_claim() -> None:
    readback = {"status": "passed"}
    events = _caption_events()
    rows = [
        {
            "source_start_seconds": event["source_start_seconds"],
            "source_end_seconds": event["source_end_seconds"],
            "text_sha256": event["text_sha256"],
            "split_at_cut_boundary": False,
        }
        for event in events
    ]
    cuts = [
        {"source_in_seconds": 0.0, "source_out_seconds": 20.0},
        {"source_in_seconds": 30.0, "source_out_seconds": 55.0},
        {"source_in_seconds": 70.0, "source_out_seconds": 100.0},
    ]

    candidate._apply_out13_caption_integrity(
        caption_readback=readback,
        caption_rows=rows,
        caption_events=events,
        cuts=cuts,
    )

    assert readback["status"] == "passed"
    assert readback["mode"] == "provider_sidecar"
    assert "official" not in json.dumps(readback)
