"""Operator proxy decision handoff tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.operator_proxy_decision_handoff import (
    build_operator_proxy_decision_handoff,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_operator_proxy_decision_handoff_keeps_operator_fields_blank(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)

    result = build_operator_proxy_decision_handoff(
        episode_dir=episode_dir,
        review_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        output_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        base_dir=tmp_path,
    )

    handoff = result["handoff"]
    patch = result["patch_template"]
    assert handoff["scope"] == "cut_002_cut_003_proxy_decision"
    assert handoff["target_cuts"] == ["cut_002", "cut_003"]
    assert handoff["source_media_status"]["status"] == "available_from_material_ledger"
    assert handoff["visual_proof_status"] == "blocked_no_cut_002_cut_003_overlay_proof"
    assert handoff["boundary_flags"] == {
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": "pending",
        "production_usage_allowed": False,
    }

    cut_002, cut_003 = handoff["cuts"]
    assert cut_002["cut_id"] == "cut_002"
    assert cut_002["context_status"] == "passed"
    assert cut_002["operator_input_fields"]["proxy_decision"] == "undecided"
    assert cut_002["operator_input_fields"]["editorial_intent"] == ""
    assert cut_002["operator_input_fields"]["script_override"] == ""
    assert cut_002["operator_input_fields"]["display_subtitle_request"] == ""
    assert cut_002["operator_input_fields"]["operator_note"] == ""
    assert cut_003["cut_id"] == "cut_003"
    assert cut_003["context_status"] == "needs_review"
    assert cut_003["retained_context_risk"] is True
    assert cut_003["operator_input_fields"]["context_risk_handling"] == "undecided"

    assert [revision["cut_id"] for revision in patch["revisions"]] == ["cut_002", "cut_003"]
    assert {revision["proxy_decision"] for revision in patch["revisions"]} == {"undecided"}
    assert patch["boundary_flags"]["production_candidate"] is False
    assert result["text_review_path"].exists()
    assert result["text_review_html_path"].exists()
    assert result["handoff_path"].exists()
    assert result["handoff_html_path"].exists()
    assert result["patch_template_path"].exists()
    assert result["patch_csv_path"].exists()
    assert result["patch_csv_path"].read_text(encoding="utf-8").splitlines()[0].startswith(
        "chapter_id,cut_id,proxy_decision"
    )


def test_build_operator_proxy_decision_handoff_cli_outputs_paths(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-operator-proxy-decision-handoff",
            "--episode-dir",
            str(episode_dir),
            "--review-dir",
            str(review_dir),
            "--output-dir",
            str(review_dir),
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
    assert payload["source_media_status"] == "available_from_material_ledger"
    assert payload["visual_proof_status"] == "blocked_no_cut_002_cut_003_overlay_proof"
    assert payload["production_candidate"] is False
    assert payload["rights_status"] == "pending"
    assert Path(payload["handoff"]).exists()
    assert Path(payload["patch_template"]).exists()


def _write_episode(tmp_path: Path) -> Path:
    episode_dir = tmp_path / "episodes" / "jp_pilot01_hololive_bancho_20260525"
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    material_video_dir = episode_dir / "materials" / "src_video_jp_pilot01"
    material_audio_dir = episode_dir / "materials" / "src_audio_jp_pilot01"
    review_dir.mkdir(parents=True)
    material_video_dir.mkdir(parents=True)
    material_audio_dir.mkdir(parents=True)
    (material_video_dir / "source_video.mp4").write_bytes(b"video")
    (material_audio_dir / "source.wav").write_bytes(b"audio")
    _write_json(_chapter_revision_board(episode_dir.name), review_dir / "chapter_revision_board.json")
    _write_json(_cut_decision_packet(episode_dir.name), review_dir / "cut_decision_packet.json")
    _write_json(_visual_proof_report(episode_dir.name), review_dir / "representative_visual_proof_report.json")
    _write_json(_edit_pack(episode_dir.name), episode_dir / "edit_pack.json")
    _write_json(_material_ledger(episode_dir), episode_dir / "material_ledger.json")
    return episode_dir


def _chapter_revision_board(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "artifact_kind": "chapter_revision_board",
        "episode_id": episode_id,
        "boundary_flags": {
            "production_candidate": False,
            "creative_acceptance": False,
            "publish_acceptance": False,
            "rights_status": "pending",
            "production_usage_allowed": False,
        },
        "chapters": [
            _chapter("ch_002", "cut_002", "passed", False, 4.838, 2, 0.413),
            _chapter("ch_003", "cut_003", "needs_review", True, 19.119, 15, 0.785),
        ],
    }


def _chapter(
    chapter_id: str,
    cut_id: str,
    context_status: str,
    retained_context_risk: bool,
    duration: float,
    subtitle_count: int,
    density: float,
) -> dict:
    return {
        "chapter_id": chapter_id,
        "source_cut_id": cut_id,
        "duration_seconds": duration,
        "original_context_status": context_status,
        "retained_context_risk": retained_context_risk,
        "subtitle_count": subtitle_count,
        "subtitle_density": density,
        "subtitle_chars_per_second": 8.0,
        "line_wrap_proxy": {
            "measurement_kind": "east_asian_width_proxy",
            "wrap_eaw": 40,
            "subtitle_count_measured": subtitle_count,
            "max_raw_eaw": 45 if cut_id == "cut_002" else 38,
            "max_wrapped_line_eaw": 33 if cut_id == "cut_002" else 38,
            "needs_wrap_count": 1 if cut_id == "cut_002" else 0,
            "proxy_only": True,
        },
        "timing_span": {
            "source_start_seconds": 12.0 if cut_id == "cut_002" else 22.0,
            "source_end_seconds": 17.0 if cut_id == "cut_002" else 41.0,
            "duration_seconds": duration,
            "subtitle_start_seconds": 12.0 if cut_id == "cut_002" else 22.0,
            "subtitle_end_seconds": 17.0 if cut_id == "cut_002" else 41.0,
        },
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
                "subtitle_density_per_second": 0.413,
                "subtitle_chars_per_second": 8.475,
                "manual_override_reason": None,
                "production_candidate": False,
                "rights_status": "pending",
            },
            {
                "cut_id": "cut_003",
                "final_cut_decision": "keep",
                "context_status": "needs_review",
                "duration_seconds": 19.119,
                "subtitle_event_count": 15,
                "subtitle_density_per_second": 0.785,
                "subtitle_chars_per_second": 7.95,
                "manual_override_reason": "retained risk stays visible",
                "production_candidate": False,
                "rights_status": "pending",
            },
        ],
    }


def _visual_proof_report(episode_id: str) -> dict:
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
            _visual_assessment("cut_002", "passed", False),
            _visual_assessment("cut_003", "needs_review", True),
        ],
    }


def _visual_assessment(cut_id: str, context_status: str, retained_context_risk: bool) -> dict:
    return {
        "cut_id": cut_id,
        "visual_proof_status": "available_source_frame_only_no_subtitle_overlay",
        "visual_proof_artifact_path": f"review/{cut_id}.png",
        "source_used": "existing_source_video_frame_only",
        "original_context_status": context_status,
        "retained_context_risk": retained_context_risk,
        "typography_status": "visual_proof_required_no_subtitle_overlay",
        "safe_area_status": "visual_proof_required_no_subtitle_overlay",
        "line_wrapping_status": "line_wrap_visual_review_required",
        "timing_sync_status": "timing_visual_audio_review_required",
        "context_risk_status": "retained_context_risk" if retained_context_risk else "context_proxy_ok",
        "proof_limitations": ["source frame has no subtitle overlay"],
        "recommended_next_action": ["generate_representative_diagnostic_visual_proof"],
    }


def _edit_pack(episode_id: str) -> dict:
    return {
        "schema_version": "v1",
        "episode_id": episode_id,
        "subtitles": [
            {
                "id": "sub_008",
                "cut_id": "cut_002",
                "start_seconds": 12.329,
                "end_seconds": 14.298,
                "text": "subtitle 2a",
            },
            {
                "id": "sub_009",
                "cut_id": "cut_002",
                "start_seconds": 14.298,
                "end_seconds": 17.167,
                "text": "subtitle 2b",
            },
            {
                "id": "sub_010",
                "cut_id": "cut_003",
                "start_seconds": 22.606,
                "end_seconds": 23.64,
                "text": "subtitle 3a",
            },
        ],
    }


def _material_ledger(episode_dir: Path) -> dict:
    return {
        "schema_version": "v1",
        "episode_id": episode_dir.name,
        "materials": [
            {
                "id": "src_video_jp_pilot01",
                "kind": "source_video",
                "file_path": str(
                    episode_dir
                    / "materials"
                    / "src_video_jp_pilot01"
                    / "source_video.mp4"
                ),
                "hash_sha256": "video-hash",
                "byte_size": 5,
            },
            {
                "id": "src_audio_jp_pilot01",
                "kind": "source_audio",
                "file_path": str(
                    episode_dir
                    / "materials"
                    / "src_audio_jp_pilot01"
                    / "source.wav"
                ),
                "hash_sha256": "audio-hash",
                "byte_size": 5,
            },
        ],
    }


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
