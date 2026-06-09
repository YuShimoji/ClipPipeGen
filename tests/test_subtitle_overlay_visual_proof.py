"""Subtitle-overlay visual proof tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.operator_proxy_decision_handoff import build_operator_proxy_decision_handoff
from src.integrations.render.subtitle_overlay_visual_proof import build_subtitle_overlay_visual_proof


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_subtitle_overlay_visual_proof_targets_explicit_cuts_and_updates_ed10d(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    before = build_operator_proxy_decision_handoff(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )
    assert before["handoff"]["visual_proof_status"] == "blocked_no_cut_002_cut_003_overlay_proof"
    legacy_cut3_srt = review_dir / "subtitle_overlay_visual_proof_cut_003.srt"
    legacy_cut3_srt.write_text("legacy autoload subtitle", encoding="utf-8")
    legacy_cut3_video = review_dir / "subtitle_overlay_visual_proof_cut_003.mp4"
    legacy_cut3_frame = review_dir / "subtitle_overlay_visual_proof_cut_003.png"
    legacy_cut3_video.write_bytes(b"previous video")
    legacy_cut3_frame.write_bytes(b"previous frame")

    result = build_subtitle_overlay_visual_proof(
        episode_dir=episode_dir,
        review_dir=review_dir,
        target_cut_ids=["cut_002", "cut_003"],
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        base_dir=tmp_path,
        runner=_fake_runner,
    )

    report = result["report"]
    assert report["target_cuts"] == ["cut_002", "cut_003"]
    assert report["production_candidate"] is False
    assert report["rights_status"] == "pending"
    assert report["production_usage_allowed"] is False
    assert report["creative_acceptance"] is False
    assert report["publish_acceptance"] is False
    assert report["style_direction"]["preset_name"] == "jp_clip_readable_v1"
    assert report["style_direction"]["target_viewing_context"] == (
        "smartphone_readable_japanese_clip_subtitle"
    )
    assert report["style_parameters"]["renderer"] == "ffmpeg_subtitles_filter_ass"
    assert report["style_parameters"]["explicit_ass_style_file"] is True
    assert report["style_parameters"]["font_size"]["source"] == (
        "explicit_diagnostic_ass_style_candidate"
    )
    assert report["style_parameters"]["font_size"]["value"] == 92
    assert report["style_parameters"]["outline"]["value"] == 7
    assert report["style_parameters"]["margin_v"]["value"] == 110
    assert report["style_parameters"]["wrapping"]["automatic_wrap_applied_by_overlay_generator"] is True
    assert report["subtitle_presentation_contract"]["contract_id"] == (
        "jp_clip_dialogue_reference_v0"
    )
    assert report["speaker_identity_presentation"]["fallback_used"] is True
    assert report["speaker_identity_presentation"]["fallback_kind"] == (
        "speaker_badge_placeholder"
    )
    assert report["replacement_behavior"]["mode"] == "replace_on_next_subtitle_start"
    assert report["renderer_path_audit"]["old_candidate_insufficiency"][
        "insufficient_style_difference"
    ] is True
    assert report["sample_frame_selection"]["required_roles"] == [
        "early",
        "middle",
        "response_referral",
        "final",
    ]
    assert report["burned_in_subtitle_style"]["style_candidate_id"] == (
        "jp_clip_dialogue_badge_left_v0"
    )
    assert report["burned_in_subtitle_style"]["production_subtitle_design_acceptance"] is False
    assert report["sidecar_srt_reference"]["role"] == (
        "reference_text_only_not_burned_in_subtitle_rendering"
    )
    assert report["review_warning"]["vlc_sidecar_srt_auto_display"] == "can_confuse_review"
    assert report["aggregate_summary"]["subtitle_overlay_available_count"] == 2
    assert {item["cut_id"] for item in report["cut_results"]} == {"cut_002", "cut_003"}

    for item in report["cut_results"]:
        assert item["subtitle_overlay_present"] is True
        assert item["visual_proof_status"] == "available_diagnostic_subtitle_overlay"
        assert item["style_direction"]["preset_name"] == "jp_clip_readable_v1"
        assert item["style_parameters"]["alignment"]["value"] == (
            "speaker_badge_left_aligned_dialogue"
        )
        assert item["style_parameters"]["font_size"]["value"] == 92
        assert item["burned_in_subtitle_style"]["font_size"] == 92
        assert item["subtitle_presentation_contract"]["contract_id"] == (
            "jp_clip_dialogue_reference_v0"
        )
        assert item["speaker_identity_presentation"]["pattern_status"] == (
            "approximated_with_fallback_speaker_badge_no_face_icon_assets"
        )
        assert item["replacement_behavior"]["mode"] == "replace_on_next_subtitle_start"
        assert item["sample_frame_selection"]["roles"] == [
            "early",
            "middle",
            "response_referral",
            "final",
        ]
        assert len(item["generated_artifacts"]["sample_frames"]) == 4
        for sample in item["generated_artifacts"]["sample_frames"]:
            assert sample["subtitle_bearing_expected"] is True
            assert sample["path"].endswith(f"sample_{sample['role']}.png")
            assert (tmp_path / sample["path"]).is_relative_to(review_dir)
        assert item["sidecar_srt_reference"]["role"] == (
            "reference_text_only_not_burned_in_subtitle_rendering"
        )
        assert item["generated_artifacts"]["burned_in_subtitle_file"].endswith(".burned_in.ass")
        assert item["generated_artifacts"]["sidecar_srt_reference"].endswith(".reference.srt")
        assert "subtitle_overlay_reference" in item["generated_artifacts"]["sidecar_srt_reference"]
        assert item["artifact_exists"]["burned_in_subtitle_file"] is True
        assert item["artifact_exists"]["sidecar_srt_reference"] is True
        assert ".burned_in.ass" in item["attempts"][0]["summary"]
        assert ".reference.srt" not in item["attempts"][0]["summary"]
        assert item["line_width_readback"]["measurement_kind"] == "east_asian_width_proxy"
        assert (tmp_path / item["generated_artifacts"]["video"]).is_relative_to(review_dir)
        assert (tmp_path / item["generated_artifacts"]["frame"]).is_relative_to(review_dir)
        assert item["generated_artifacts"]["video"].endswith(f"{item['cut_id']}.mp4")
        assert item["generated_artifacts"]["frame"].endswith(f"{item['cut_id']}.png")

    assert not (review_dir / "subtitle_overlay_visual_proof_cut_001.mp4").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_002.mp4").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_002.png").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_002.burned_in.ass").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_002.reference.srt").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_002.sample_early.png").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_003.mp4").exists()
    assert (review_dir / "subtitle_overlay_visual_proof_cut_003.png").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.sample_response_referral.png").exists()
    assert not legacy_cut3_srt.exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.legacy_autoload.srt").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.previous_style.mp4").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.previous_style.png").exists()
    assert (review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.previous_autoload.srt").exists()

    overlay_html = (review_dir / "subtitle_overlay_visual_proof_report.html").read_text(encoding="utf-8")
    assert "jp_clip_readable_v1" in overlay_html
    assert "jp_clip_dialogue_reference_v0" in overlay_html
    assert "speaker_badge_placeholder_plus_left_aligned_subtitle" in overlay_html
    assert "font_size" in overlay_html
    assert "Burned-in vs Sidecar SRT" in overlay_html
    assert "subtitle-bearing samples" in overlay_html
    assert "previous proof for comparison" in overlay_html
    assert "subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_003.sample_response_referral.png" in overlay_html
    assert "subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_003.previous_style.png" in overlay_html
    assert "subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_003.reference.srt" in overlay_html
    assert 'src="subtitle_overlay_visual_proof_cut_002.png"' in overlay_html
    assert 'src="subtitle_overlay_visual_proof_cut_003.mp4"' in overlay_html
    assert 'src="visual_proof_contact_sheet.png"' in overlay_html
    cut3_ass = (
        review_dir / "subtitle_overlay_reference" / "subtitle_overlay_visual_proof_cut_003.burned_in.ass"
    ).read_text(encoding="utf-8")
    assert "Style: ClipPipeDialogueLeft" in cut3_ass
    assert "Style: ClipPipeSpeakerBadge" in cut3_ass
    assert "\\pos(250,742)" in cut3_ass
    assert "\\pos(128,805)" in cut3_ass

    representative = json.loads(
        (review_dir / "representative_visual_proof_report.json").read_text(encoding="utf-8")
    )
    assert representative["diagnostic_style_direction"]["preset_name"] == "jp_clip_readable_v1"
    assert representative["subtitle_presentation_contract"]["contract_id"] == (
        "jp_clip_dialogue_reference_v0"
    )
    assert representative["burned_in_subtitle_style"]["style_candidate_id"] == (
        "jp_clip_dialogue_badge_left_v0"
    )
    assert representative["sidecar_srt_reference"]["role"] == (
        "reference_text_only_not_burned_in_subtitle_rendering"
    )
    assessments = {item["cut_id"]: item for item in representative["per_cut_visual_assessment"]}
    assert assessments["cut_001"]["visual_proof_status"] == "available_diagnostic_render_frame"
    assert assessments["cut_002"]["visual_proof_status"] == "available_diagnostic_subtitle_overlay"
    assert assessments["cut_002"]["style_parameters"]["font_size"]["source"] == (
        "explicit_diagnostic_ass_style_candidate"
    )
    assert assessments["cut_002"]["subtitle_presentation_contract"]["contract_id"] == (
        "jp_clip_dialogue_reference_v0"
    )
    assert assessments["cut_002"]["sidecar_srt_reference"]["autoload_prevention"]
    assert assessments["cut_002"]["previous_visual_proof_status"] == (
        "available_source_frame_only_no_subtitle_overlay"
    )
    assert assessments["cut_003"]["visual_proof_status"] == "available_diagnostic_subtitle_overlay"
    assert assessments["cut_003"]["sample_frame_selection"][
        "includes_response_referral_block"
    ] is True

    representative_html = (review_dir / "representative_visual_proof_report.html").read_text(encoding="utf-8")
    assert "jp_clip_readable_v1" in representative_html
    assert "jp_clip_dialogue_reference_v0" in representative_html
    assert 'src="subtitle_overlay_visual_proof_cut_002.png"' in representative_html

    after = build_operator_proxy_decision_handoff(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )
    handoff = after["handoff"]
    assert handoff["visual_proof_status"] == "available_requires_human_review"
    assert handoff["boundary_flags"]["production_candidate"] is False
    assert handoff["boundary_flags"]["rights_status"] == "pending"
    cut_002, cut_003 = handoff["cuts"]
    assert cut_002["visual_proof"]["style_direction"]["preset_name"] == "jp_clip_readable_v1"
    assert cut_002["visual_proof"]["style_parameters"]["style_slot"] == "subtitle.default"
    assert cut_002["visual_proof"]["style_parameters"]["font_size"]["value"] == 92
    assert cut_002["operator_input_fields"]["proxy_decision"] == "undecided"
    assert cut_002["operator_input_fields"]["editorial_intent"] == ""
    assert cut_003["context_status"] == "needs_review"
    assert cut_003["retained_context_risk"] is True
    assert cut_003["operator_input_fields"]["context_risk_handling"] == "undecided"


def test_build_subtitle_overlay_visual_proof_cli_dry_run_outputs_plan(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    help_result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "build-subtitle-overlay-visual-proof", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert help_result.returncode == 0
    assert "--target-cut" in help_result.stdout

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-overlay-visual-proof",
            "--episode-dir",
            str(episode_dir),
            "--review-dir",
            str(review_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target_cuts"] == ["cut_002", "cut_003"]
    assert payload["dry_run"] is True
    assert payload["visual_proof_status"] == "blocked_no_cut_002_cut_003_overlay_proof"
    assert payload["style_direction_preset"] == "jp_clip_readable_v1"
    assert payload["production_candidate"] is False
    assert payload["rights_status"] == "pending"
    assert not (review_dir / "subtitle_overlay_visual_proof_report.json").exists()
    assert not (review_dir / "subtitle_overlay_visual_proof_cut_002.mp4").exists()


def _write_episode(tmp_path: Path) -> Path:
    episode_dir = tmp_path / "episodes" / "jp_pilot01_hololive_bancho_20260525"
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    video_dir = episode_dir / "materials" / "src_video_jp_pilot01"
    audio_dir = episode_dir / "materials" / "src_audio_jp_pilot01"
    review_dir.mkdir(parents=True)
    video_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)
    (video_dir / "source_video.mp4").write_bytes(b"video")
    (audio_dir / "source.wav").write_bytes(b"audio")
    (review_dir / "visual_proof_contact_sheet.png").write_bytes(b"contact-sheet")
    _write_json(_edit_pack(episode_dir.name), episode_dir / "edit_pack.json")
    _write_json(_material_ledger(episode_dir), episode_dir / "material_ledger.json")
    _write_json(_chapter_revision_board(episode_dir.name), review_dir / "chapter_revision_board.json")
    _write_json(_cut_decision_packet(episode_dir.name), review_dir / "cut_decision_packet.json")
    _write_json(_representative_visual_report(episode_dir.name), review_dir / "representative_visual_proof_report.json")
    return episode_dir


def _edit_pack(episode_id: str) -> dict:
    now = "2026-06-04T00:00:00+00:00"
    return {
        "schema_version": "v1",
        "episode_id": episode_id,
        "rights_manifest_path": f"episodes/{episode_id}/rights_manifest.json",
        "material_ledger_path": f"episodes/{episode_id}/material_ledger.json",
        "created_at": now,
        "updated_at": now,
        "editing_intent": {
            "target_duration_seconds": None,
            "topic": "",
            "audience_note": "",
            "language": "ja",
        },
        "cut_candidates": [
            _cut("cut_001", 2.453, 9.293, "passed"),
            _cut("cut_002", 12.329, 17.167, "passed"),
            _cut("cut_003", 22.606, 49.566, "needs_review"),
        ],
        "selected_cut_ids": ["cut_001", "cut_002", "cut_003"],
        "subtitles": [
            _subtitle("sub_001", "cut_001", 2.453, 3.32, "cut 1"),
            _subtitle("sub_008", "cut_002", 12.329, 14.298, "subtitle 2a"),
            _subtitle("sub_009", "cut_002", 14.298, 17.167, "subtitle 2b"),
            *_cut_003_subtitles(),
        ],
        "review": {
            "status": "draft",
            "reviewed_by": None,
            "reviewed_at": None,
            "notes": [],
        },
    }


def _cut(cut_id: str, start: float, end: float, context_status: str) -> dict:
    return {
        "id": cut_id,
        "start_seconds": start,
        "end_seconds": end,
        "source": "auto",
        "reason": "fixture",
        "confidence": 1.0,
        "context_check": {"status": context_status, "notes": []},
    }


def _subtitle(subtitle_id: str, cut_id: str, start: float, end: float, text: str) -> dict:
    return {
        "id": subtitle_id,
        "cut_id": cut_id,
        "start_seconds": start,
        "end_seconds": end,
        "text": text,
        "source": "auto",
        "source_type": "imported_subtitle_track",
        "source_segment_ids": [subtitle_id.replace("sub", "seg")],
        "draft": True,
        "diagnostic": True,
        "not_production_subtitle_design": True,
    }


def _cut_003_subtitles() -> list[dict]:
    rows = [
        ("sub_010", 22.606, 23.640, "subtitle 3a"),
        ("sub_011", 24.041, 25.109, "subtitle 3b"),
        ("sub_012", 25.109, 26.000, "subtitle 3c"),
        ("sub_013", 26.000, 27.000, "subtitle 3d"),
        ("sub_014", 27.000, 28.000, "subtitle 3e"),
        ("sub_015", 28.000, 29.000, "subtitle 3f"),
        ("sub_016", 29.000, 30.000, "subtitle 3g"),
        ("sub_017", 30.000, 31.000, "subtitle 3h"),
        ("sub_018", 31.000, 32.000, "subtitle 3i"),
        ("sub_019", 32.000, 33.000, "subtitle 3j"),
        ("sub_020", 33.000, 34.000, "subtitle 3k"),
        ("sub_021", 34.000, 35.000, "subtitle 3l"),
        ("sub_022", 35.000, 36.000, "subtitle 3m"),
        ("sub_023", 36.000, 37.000, "subtitle 3n"),
        ("sub_024", 37.000, 38.000, "subtitle 3o"),
        ("sub_025", 38.000, 40.000, "response block starts"),
        ("sub_026", 40.000, 42.000, "response block continues"),
        ("sub_027", 42.000, 44.000, "response block detail"),
        ("sub_028", 44.000, 46.000, "response block referral"),
        ("sub_029", 46.000, 49.566, "response block closes"),
    ]
    return [_subtitle(subtitle_id, "cut_003", start, end, text) for subtitle_id, start, end, text in rows]


def _material_ledger(episode_dir: Path) -> dict:
    return {
        "schema_version": "v1",
        "episode_id": episode_dir.name,
        "materials": [
            {
                "id": "src_video_jp_pilot01",
                "kind": "source_video",
                "file_path": str(episode_dir / "materials" / "src_video_jp_pilot01" / "source_video.mp4"),
                "hash_sha256": "video-hash",
                "byte_size": 5,
            },
            {
                "id": "src_audio_jp_pilot01",
                "kind": "source_audio",
                "file_path": str(episode_dir / "materials" / "src_audio_jp_pilot01" / "source.wav"),
                "hash_sha256": "audio-hash",
                "byte_size": 5,
            },
        ],
    }


def _chapter_revision_board(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "artifact_kind": "chapter_revision_board",
        "episode_id": episode_id,
        "chapters": [
            _chapter("ch_002", "cut_002", "passed", False, 4.838, 2),
            _chapter("ch_003", "cut_003", "needs_review", True, 26.96, 20),
        ],
    }


def _chapter(
    chapter_id: str,
    cut_id: str,
    context_status: str,
    retained_context_risk: bool,
    duration: float,
    subtitle_count: int,
) -> dict:
    return {
        "chapter_id": chapter_id,
        "source_cut_id": cut_id,
        "duration_seconds": duration,
        "original_context_status": context_status,
        "retained_context_risk": retained_context_risk,
        "subtitle_count": subtitle_count,
        "subtitle_density": 0.5,
        "subtitle_chars_per_second": 8.0,
        "line_wrap_proxy": {"proxy_only": True},
        "timing_span": {},
        "current_risks": ["retained_context_risk"] if retained_context_risk else [],
    }


def _cut_decision_packet(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "artifact_kind": "r3_cut_decision_packet",
        "episode_id": episode_id,
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": "pending",
        "decisions": [
            {
                "cut_id": "cut_002",
                "final_cut_decision": "keep",
                "context_status": "passed",
                "duration_seconds": 4.838,
                "subtitle_event_count": 2,
                "manual_override_reason": None,
            },
            {
                "cut_id": "cut_003",
                "final_cut_decision": "keep",
                "context_status": "needs_review",
                "duration_seconds": 26.96,
                "subtitle_event_count": 20,
                "manual_override_reason": "retained risk stays visible",
            },
        ],
    }


def _representative_visual_report(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "report_kind": "representative_visual_proof_report",
        "episode_id": episode_id,
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": "pending",
        "production_usage_allowed": False,
        "per_cut_visual_assessment": [
            {
                "cut_id": "cut_001",
                "visual_proof_status": "available_diagnostic_render_frame",
                "visual_proof_artifact_path": "review/visual_proof_cut_001.png",
                "source_used": "existing_cut_001_diagnostic_render_frame_with_subtitle_overlay",
                "typography_status": "diagnostic_overlay_visible_human_review_required",
                "safe_area_status": "diagnostic_overlay_visible_human_review_required",
                "line_wrapping_status": "proxy_ok",
                "timing_sync_status": "diagnostic_timing_proxy_available_visual_audio_review_required",
                "retained_context_risk": False,
            },
            _source_frame_assessment("cut_002", False),
            _source_frame_assessment("cut_003", True),
        ],
        "outputs": {
            "json": f"episodes/{episode_id}/review/jp_pilot01r3_cut_review/representative_visual_proof_report.json",
            "html": f"episodes/{episode_id}/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html",
            "contact_sheet": f"episodes/{episode_id}/review/jp_pilot01r3_cut_review/visual_proof_contact_sheet.png",
        },
    }


def _source_frame_assessment(cut_id: str, retained_context_risk: bool) -> dict:
    return {
        "cut_id": cut_id,
        "visual_proof_status": "available_source_frame_only_no_subtitle_overlay",
        "visual_proof_artifact_path": f"review/visual_proof_{cut_id}.png",
        "source_used": "existing_source_video_frame_only",
        "typography_status": "visual_proof_required_no_subtitle_overlay",
        "safe_area_status": "visual_proof_required_no_subtitle_overlay",
        "line_wrapping_status": "line_wrap_visual_review_required",
        "timing_sync_status": "timing_visual_audio_review_required",
        "retained_context_risk": retained_context_risk,
        "proof_limitations": ["source frame has no subtitle overlay"],
        "recommended_next_action": ["generate_representative_diagnostic_visual_proof"],
    }


def _fake_runner(args, *, capture_output: bool, text: bool, timeout: int):
    command = [str(arg) for arg in args]
    if "-version" in command:
        return subprocess.CompletedProcess(args, 0, stdout=f"{Path(command[0]).name} version fake\n", stderr="")
    if "-print_format" in command and "-show_streams" in command:
        payload = {
            "format": {"duration": "1.5", "format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "codec_long_name": "H.264",
                    "width": 320,
                    "height": 180,
                    "avg_frame_rate": "24/1",
                },
                {"codec_type": "audio", "codec_name": "aac", "codec_long_name": "AAC"},
            ],
        }
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload), stderr="")
    output = Path(command[-1])
    output.parent.mkdir(parents=True, exist_ok=True)
    if "-frames:v" in command:
        output.write_bytes(b"png")
    else:
        output.write_bytes(b"video")
    return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
