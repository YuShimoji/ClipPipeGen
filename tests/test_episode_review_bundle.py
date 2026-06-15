"""Episode review bundle tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.episode_review_bundle import build_episode_review_bundle


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_episode_review_bundle_prioritizes_playable_video_and_keeps_boundaries(tmp_path: Path):
    episode_dir, review_dir = _write_episode(tmp_path)

    result = build_episode_review_bundle(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir / "human_preview_session",
        base_dir=tmp_path,
    )

    manifest = result["manifest"]
    index = result["index_path"].read_text(encoding="utf-8")
    serialized = json.dumps(manifest)
    decision_request = json.loads(result["decision_request_path"].read_text(encoding="utf-8"))
    decision_template = json.loads(result["decision_template_path"].read_text(encoding="utf-8"))
    assert manifest["active_artifact"] == "clip-human-preview-session-001"
    assert manifest["artifact_kind"] == "human_preview_session_bundle"
    assert "clip-episode-review-surface-001" in manifest["artifact_aliases"]
    assert manifest["reviewability"]["state"] == "diagnostic_only"
    assert manifest["reviewability"]["review_ready"] is True
    assert manifest["boundary_flags"]["diagnostic_only"] is True
    assert manifest["boundary_flags"]["production_candidate"] is False
    assert manifest["boundary_flags"]["production_render_acceptance"] is False
    assert manifest["boundary_flags"]["production_subtitle_design_acceptance"] is False
    assert manifest["boundary_flags"]["creative_acceptance"] is False
    assert manifest["boundary_flags"]["rights_status"] == "pending"
    assert manifest["boundary_flags"]["production_usage_allowed"] is False
    assert manifest["boundary_flags"]["publishing_acceptance"] is False
    assert manifest["boundary_flags"]["public_use_permission"] is False
    assert manifest["target_cuts"] == ["cut_002", "cut_003"]
    assert manifest["decision_request"]["allowed_responses"] == [
        "accept_candidate",
        "adjust_boundary",
        "reject",
        "blocked_missing_artifact",
        "blocked_missing_dense_stress_proof",
    ]
    assert decision_request["question"] == manifest["decision_request"]["question"]
    assert decision_template["selected_response"] is None
    assert manifest["primary_review_order"][0]["role"] == "playable_video"
    assert manifest["primary_review_order"][0]["media_type"] == "mp4"
    assert manifest["primary_review_order"][0]["asset_href"].startswith("assets/")
    assert manifest["assets"]["entries"]
    assert "video_review_player" in {screen["screen_id"] for screen in manifest["screens"]}
    assert "Generated video review is in scope" in " ".join(manifest["notes"])
    assert str(tmp_path) not in serialized
    assert "<video controls" in index
    assert "Decision Request" in index
    assert "accept_candidate" in index
    assert "production_render_acceptance=false" in index
    assert "creative_acceptance" in index
    assert "rights_status=pending" in index
    assert "subtitle_overlay_visual_proof_cut_002.mp4" in index
    assert "decision_template.json" in index
    assert "cut_review_report.html" in index
    assert result["open_preview_path"].exists()
    assert result["serve_preview_path"].exists()
    assert (result["index_path"].parent / "assets").exists()


def test_episode_review_bundle_reports_missing_media_before_html_hunt(tmp_path: Path):
    episode_dir, review_dir = _write_episode(tmp_path, include_media=False)

    result = build_episode_review_bundle(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir / "human_preview_session",
        base_dir=tmp_path,
    )

    manifest = result["manifest"]
    index = result["index_path"].read_text(encoding="utf-8")
    assert manifest["reviewability"]["state"] == "review_blocked_missing_artifacts"
    assert manifest["reviewability"]["review_ready"] is False
    assert any(
        item.endswith("subtitle_overlay_visual_proof_cut_002.mp4")
        for item in manifest["reviewability"]["missing_expected_media"]
    )
    assert manifest["primary_review_order"][0]["role"] == "subtitle_overlay_report_html"
    assert "No playable video or contact sheet is available" in index
    assert "subtitle_overlay_visual_proof_cut_002.mp4" in index
    assert manifest["boundary_flags"]["production_render_acceptance"] is False
    assert manifest["boundary_flags"]["publishing_acceptance"] is False


def test_build_episode_review_bundle_cli_writes_manifest_and_index(tmp_path: Path):
    episode_dir, review_dir = _write_episode(tmp_path)
    output_dir = review_dir / "human_preview_session"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-episode-review-bundle",
            "--episode-dir",
            str(episode_dir),
            "--review-dir",
            str(review_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["active_artifact"] == "clip-human-preview-session-001"
    assert payload["review_ready"] is True
    assert payload["diagnostic_only"] is True
    assert payload["production_render_acceptance"] is False
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["review_manifest"]).exists()
    assert Path(payload["decision_request"]).exists()
    assert Path(payload["decision_template"]).exists()
    assert Path(payload["open_preview"]).exists()
    assert Path(payload["serve_preview"]).exists()
    assert Path(payload["index_html"]).exists()
    manifest = json.loads(Path(payload["review_manifest"]).read_text(encoding="utf-8"))
    assert manifest["bundle"]["path_authority"].startswith("repo_relative_paths_only")
    assert manifest["open_commands"]["open_preview"] == payload["open_command"]


def test_build_human_preview_session_alias_uses_same_contract(tmp_path: Path):
    episode_dir, review_dir = _write_episode(tmp_path)
    output_dir = review_dir / "human_preview_session_alias"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-human-preview-session",
            "--episode-dir",
            str(episode_dir),
            "--review-dir",
            str(review_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["active_artifact"] == "clip-human-preview-session-001"
    assert Path(payload["index_html"]).exists()
    assert Path(payload["decision_request"]).exists()


def _write_episode(tmp_path: Path, *, include_media: bool = True) -> tuple[Path, Path]:
    episode_dir = tmp_path / "episodes" / "ep_r3"
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    export_dir = episode_dir / "exports" / "r3"
    render_dir = episode_dir / "renders" / "r3"
    reference_dir = review_dir / "subtitle_overlay_reference"
    review_dir.mkdir(parents=True)
    export_dir.mkdir(parents=True)
    render_dir.mkdir(parents=True)
    reference_dir.mkdir(parents=True)

    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_r3",
            "source_video": {"url": "https://www.youtube.com/watch?v=7J5aS_pcBj4"},
            "compliance_check": {"status": "pending"},
        },
        episode_dir / "rights_manifest.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_r3",
            "materials": [
                {"id": "src_video_jp_pilot01", "kind": "source_video"},
                {"id": "src_audio_jp_pilot01", "kind": "source_audio"},
            ],
        },
        episode_dir / "material_ledger.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_r3",
            "stt": {"engine": "subtitle_track", "provider": "youtube_subtitles"},
            "review": {"status": "needs_review"},
            "segments": [{"id": "seg_001", "start_seconds": 0.0, "end_seconds": 1.0, "text": "hello"}],
        },
        episode_dir / "transcript.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_r3",
            "selected_cut_ids": ["cut_002", "cut_003"],
            "cut_candidates": [
                {"id": "cut_002", "context_check": {"status": "passed"}},
                {"id": "cut_003", "context_check": {"status": "needs_review"}},
            ],
            "subtitles": [
                {"id": "sub_008", "cut_id": "cut_002", "text": "hello"},
                {"id": "sub_010", "cut_id": "cut_003", "text": "world"},
            ],
        },
        episode_dir / "edit_pack.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "target_cuts": ["cut_002", "cut_003"],
            "all_target_cuts_have_overlay": include_media,
            "production_candidate": False,
            "rights_status": "pending",
        },
        review_dir / "subtitle_overlay_visual_proof_report.json",
    )
    _write_json({"schema_version": "v1"}, review_dir / "representative_visual_proof_report.json")
    _write_json({"schema_version": "v1"}, review_dir / "cut_decision_packet.json")
    _write_json({"schema_version": "v1"}, review_dir / "cut_002_cut_003_operator_proxy_decision_handoff.json")
    _write_json({"schema_version": "v1"}, render_dir / "render_manifest.json")
    _write_json({"schema_version": "v1"}, review_dir / "non_repo_artifact_handoff.json")
    (review_dir / "cut_review_report.html").write_text("<html>cut review</html>", encoding="utf-8")
    (review_dir / "evidence_summary.html").write_text("<html>evidence</html>", encoding="utf-8")
    (review_dir / "subtitle_overlay_visual_proof_report.html").write_text("<html>overlay</html>", encoding="utf-8")
    (review_dir / "representative_visual_proof_report.html").write_text("<html>representative</html>", encoding="utf-8")
    (review_dir / "cut_decision_report.html").write_text("<html>decision</html>", encoding="utf-8")
    (review_dir / "cut_002_cut_003_operator_proxy_decision_handoff.html").write_text(
        "<html>handoff</html>",
        encoding="utf-8",
    )
    (review_dir / "non_repo_artifact_handoff.html").write_text("<html>nonrepo</html>", encoding="utf-8")
    (review_dir / "chapter_revision_patch.cut_002_cut_003_proxy.template.csv").write_text(
        "chapter_id,decision\n",
        encoding="utf-8",
    )
    (export_dir / "nle_cut_list.csv").write_text("cut_id,start,end\n", encoding="utf-8")
    (export_dir / "nle_export_report.html").write_text("<html>nle</html>", encoding="utf-8")
    (render_dir / "render_report.html").write_text("<html>render</html>", encoding="utf-8")
    if include_media:
        (review_dir / "subtitle_overlay_visual_proof_cut_002.mp4").write_bytes(b"mp4")
        (review_dir / "subtitle_overlay_visual_proof_cut_003.mp4").write_bytes(b"mp4")
        (review_dir / "subtitle_overlay_visual_proof_cut_002.png").write_bytes(b"png")
        (review_dir / "visual_proof_contact_sheet.png").write_bytes(b"png")
        (reference_dir / "subtitle_overlay_visual_proof_cut_003.sample_response_referral.png").write_bytes(b"png")
        (render_dir / "rendered_video.mp4").write_bytes(b"render")
    return episode_dir, review_dir


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
