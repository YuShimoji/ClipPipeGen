from __future__ import annotations

import json
from pathlib import Path

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


def _plan() -> dict:
    return {
        "schema_version": candidate.PLAN_SCHEMA_VERSION,
        "source": {
            "identity": "youtube:editorial",
            "provider_locator": "https://www.youtube.com/watch?v=editorial",
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
                "transcript_segment_ids": ["seg_001"],
                "transition": "sequence_start",
                "context_evidence": {
                    "status": "passed",
                    "continuity_note": "source opening establishes the goal",
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
                "transcript_segment_ids": ["seg_002"],
                "transition": "hard_cut_after_wait_omission",
                "context_evidence": {
                    "status": "passed",
                    "continuity_note": "the omitted wait does not change the stated goal",
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
                "transcript_segment_ids": ["seg_003"],
                "transition": "hard_cut_after_repetition_omission",
                "context_evidence": {
                    "status": "passed",
                    "continuity_note": "the final exchange retains cause and result",
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
        }
    ]


def test_cli_dispatch_registers_out13() -> None:
    assert "build-editorial-video-candidate" in cli_main.SUBCOMMANDS


def test_editorial_timeline_is_explicit_nonuniform_and_traceable() -> None:
    timeline = candidate.build_editorial_timeline(
        plan=_plan(),
        source_identity="youtube:editorial",
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
    plan["cuts"][1]["transcript_segment_ids"] = []

    with pytest.raises(candidate.EditorialVideoCandidateError, match="transcript evidence"):
        candidate.build_editorial_timeline(
            plan=plan,
            source_identity="youtube:editorial",
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
        source_identity="youtube:editorial",
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
            "artifact_id": candidate.ARTIFACT_ID,
            "state": candidate.READY_STATE,
            "source_identity": "youtube:editorial",
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
            "--source",
            str(tmp_path / "source.mp4"),
            "--source-identity",
            "youtube:editorial",
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


def test_manifest_self_integrity_and_resume_fingerprint(tmp_path: Path) -> None:
    (tmp_path / "final_video.mp4").write_bytes(b"video")
    (tmp_path / "timeline_ir.json").write_text("{}\n", encoding="utf-8")
    manifest = candidate.build_run_manifest(
        stage=tmp_path,
        input_fingerprint="d" * 64,
        resolved={
            "source_identity": "youtube:editorial",
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

    candidate.validate_run_manifest(tmp_path, manifest)
    resumed = candidate.resume_existing_output(
        output_dir=tmp_path, input_fingerprint="d" * 64
    )

    assert resumed["resume"] is True
    assert resumed["video_sha256"] == candidate._sha256(
        tmp_path / "final_video.mp4"
    )
    with pytest.raises(candidate.EditorialVideoCandidateError, match="fingerprint mismatch"):
        candidate.resume_existing_output(
            output_dir=tmp_path, input_fingerprint="1" * 64
        )
