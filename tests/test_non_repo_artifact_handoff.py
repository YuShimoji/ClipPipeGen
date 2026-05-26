"""Non-repo artifact handoff tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.non_repo_artifact_handoff import (
    build_non_repo_artifact_handoff,
    extract_youtube_id_from_subtitle_track,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_non_repo_handoff_records_existing_diagnostic_render_identity(tmp_path: Path):
    episode_dir, render_manifest, nle_manifest, artifact = _write_episode(tmp_path)

    result = build_non_repo_artifact_handoff(
        episode_dir=episode_dir,
        render_manifest_path=render_manifest,
        nle_manifest_path=nle_manifest,
        output_dir=episode_dir / "review" / "handoff",
        generated_by_command="python -m src.cli.main render-tiny-proof --episode-id ep_r3",
        base_dir=tmp_path,
    )

    manifest = result["manifest"]
    expected_hash = hashlib.sha256(b"tiny diagnostic render").hexdigest()
    assert manifest["episode_id"] == "ep_r3"
    assert manifest["artifact_id"] == "r3_diagnostic_render"
    assert manifest["artifact"]["artifact_kind"] == "diagnostic_render_video"
    assert manifest["artifact"]["git_policy"] == "excluded_from_git"
    assert manifest["artifact"]["exists"] is True
    assert manifest["artifact"]["size_bytes"] == artifact.stat().st_size
    assert manifest["artifact"]["sha256"] == expected_hash
    assert manifest["artifact"]["generated_by_command"].startswith("python -m src.cli.main")
    assert manifest["source_identity"]["youtube_id"] == "7J5aS_pcBj4"
    assert manifest["source_identity"]["source_video_material_id"] == "src_video_jp_pilot01"
    assert manifest["source_identity"]["source_audio_material_id"] == "src_audio_jp_pilot01"
    assert manifest["source_identity"]["transcript_source"] == "imported subtitle track / youtube_subtitles"
    assert manifest["boundary"]["production_candidate"] is False
    assert manifest["boundary"]["creative_acceptance"] is False
    assert manifest["boundary"]["publish_acceptance"] is False
    assert manifest["boundary"]["rights_status"] == "pending"
    assert manifest["boundary"]["production_usage_allowed"] is False
    assert manifest["handoff_status"]["transferable_by_git"] is False
    assert manifest["handoff_status"]["regeneratable"] is True
    _assert_no_video_embed(result["report_path"].read_text(encoding="utf-8"))


def test_non_repo_handoff_cli_writes_missing_report_without_video_embed(tmp_path: Path):
    episode_dir, render_manifest, nle_manifest, artifact = _write_episode(tmp_path)
    artifact.unlink()
    output_dir = episode_dir / "review" / "cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-non-repo-handoff",
            "--episode-dir",
            str(episode_dir),
            "--render-manifest",
            str(render_manifest),
            "--nle-manifest",
            str(nle_manifest),
            "--output-dir",
            str(output_dir),
            "--generated-by-command",
            "python -m src.cli.main render-tiny-proof --episode-id ep_r3",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["exists"] is False
    assert payload["size_bytes"] is None
    assert payload["sha256"] is None
    assert payload["git_policy"] == "excluded_from_git"
    manifest = json.loads(Path(payload["manifest"]).read_text(encoding="utf-8"))
    report = Path(payload["report"]).read_text(encoding="utf-8")
    assert "is missing" in manifest["missing_behavior"]["when_absent_show"]
    assert "regeneration_command" in json.dumps(manifest["missing_behavior"])
    assert manifest["boundary"]["production_candidate"] is False
    assert manifest["boundary"]["creative_acceptance"] is False
    assert manifest["boundary"]["publish_acceptance"] is False
    assert manifest["boundary"]["rights_status"] == "pending"
    assert "do not advance to production, creative, or publish acceptance" in manifest["missing_behavior"][
        "production_acceptance_rule"
    ]
    assert "Missing Behavior" in report
    assert "production_candidate</dt><dd>false" in report
    _assert_no_video_embed(report)


def test_render_manifest_without_rendered_video_output_infers_sibling_missing(tmp_path: Path):
    episode_dir, render_manifest, nle_manifest, artifact = _write_episode(tmp_path)
    artifact.unlink()
    manifest_payload = json.loads(render_manifest.read_text(encoding="utf-8"))
    manifest_payload["outputs"].pop("rendered_video")
    _write_json(manifest_payload, render_manifest)

    result = build_non_repo_artifact_handoff(
        episode_dir=episode_dir,
        render_manifest_path=render_manifest,
        nle_manifest_path=nle_manifest,
        output_dir=episode_dir / "review" / "handoff",
        base_dir=tmp_path,
    )

    artifact_info = result["manifest"]["artifact"]
    assert artifact_info["repo_relative_path"].endswith("episodes/ep_r3/renders/r3/rendered_video.mp4")
    assert artifact_info["exists"] is False
    assert artifact_info["size_bytes"] is None
    assert artifact_info["sha256"] is None
    assert result["manifest"]["handoff_status"]["transferable_by_git"] is False
    assert result["manifest"]["missing_behavior"]["regeneration_command"].startswith(
        "python -m src.cli.main render-tiny-proof"
    )


def test_cli_fails_without_render_manifest_or_artifact_path(tmp_path: Path):
    episode_dir = tmp_path / "episodes" / "fresh"
    episode_dir.mkdir(parents=True)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-non-repo-handoff",
            "--episode-dir",
            str(episode_dir),
            "--output-dir",
            str(episode_dir / "review" / "handoff"),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "--artifact-path is required" in result.stderr
    assert "--render-manifest" in result.stderr


def test_fresh_checkout_missing_dependencies_report_is_readable(tmp_path: Path):
    episode_dir = tmp_path / "episodes" / "fresh"
    render_dir = episode_dir / "renders" / "r3"
    render_dir.mkdir(parents=True)
    render_manifest = render_dir / "render_manifest.json"
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "fresh",
            "output_id": "fresh_diagnostic_render",
            "source_refs": {
                "source_video": {"material_id": "src_video_jp_pilot01"},
                "source_audio": {"material_id": "src_audio_jp_pilot01"},
                "edit_pack": {"path": "episodes/fresh/edit_pack.json"},
                "transcript": {
                    "engine": "subtitle_track",
                    "provider": "youtube_subtitles",
                    "model": "episodes/fresh/source_subs/7J5aS_pcBj4.ja.json3",
                },
            },
            "timeline_mapping": {"duration_target_seconds": 6.84},
            "subtitle_burn_in": {"requested_mode": "diagnostic"},
            "outputs": {"rendered_video": str(render_dir / "rendered_video.mp4").replace("\\", "/")},
            "output_metadata": {
                "duration_seconds": 6.84,
                "resolution": "1920x1080",
                "video_codec": "h264",
                "audio_codec": "aac",
            },
        },
        render_manifest,
    )

    result = build_non_repo_artifact_handoff(
        episode_dir=episode_dir,
        render_manifest_path=render_manifest,
        output_dir=episode_dir / "review" / "handoff",
        base_dir=tmp_path,
    )

    manifest = result["manifest"]
    report = result["report_path"].read_text(encoding="utf-8")
    assert manifest["artifact"]["exists"] is False
    assert manifest["source_identity"]["youtube_id"] == "7J5aS_pcBj4"
    assert manifest["source_identity"]["source_video_title"] == "unknown"
    assert manifest["source_identity"]["source_url"] == "unknown"
    assert manifest["dependency_artifacts"]["transcript"]["exists"] is False
    assert manifest["dependency_artifacts"]["edit_pack"]["exists"] is False
    assert manifest["dependency_artifacts"]["rights_manifest"]["exists"] is False
    assert manifest["dependency_artifacts"]["material_ledger"]["exists"] is False
    assert manifest["dependency_artifacts"]["subtitle_track"]["exists"] is False
    assert manifest["dependency_artifacts"]["render_manifest"]["exists"] is True
    assert manifest["handoff_status"]["regeneratable"] is False
    assert manifest["handoff_status"]["requires_local_media"] is True
    assert "Dependency Artifacts" in report
    assert "transcript.json" in report
    assert "<td>false</td>" in report
    assert "Missing Behavior" in report
    assert "do not advance to production, creative, or publish acceptance" in report
    _assert_no_video_embed(report)


def test_extract_youtube_id_from_subtitle_track_path():
    assert extract_youtube_id_from_subtitle_track("source_subs/7J5aS_pcBj4.ja.json3") == "7J5aS_pcBj4"
    assert extract_youtube_id_from_subtitle_track("source_subs/not-a-youtube-id.ja.json3") == "unknown"


def _assert_no_video_embed(report: str) -> None:
    lowered = report.lower()
    assert "<video" not in lowered
    assert "data:video" not in lowered
    assert "base64" not in lowered


def _write_episode(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    episode_dir = tmp_path / "episodes" / "ep_r3"
    render_dir = episode_dir / "renders" / "r3"
    export_dir = episode_dir / "exports" / "r3"
    source_subs = episode_dir / "source_subs"
    render_dir.mkdir(parents=True)
    export_dir.mkdir(parents=True)
    source_subs.mkdir(parents=True)
    artifact = render_dir / "rendered_video.mp4"
    artifact.write_bytes(b"tiny diagnostic render")
    (source_subs / "7J5aS_pcBj4.ja.json3").write_text("{}", encoding="utf-8")
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_r3",
            "source_video": {
                "url": "https://www.youtube.com/watch?v=7J5aS_pcBj4",
                "title": "Test JP source",
                "channel": "Test Channel",
            },
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
            "stt": {
                "engine": "subtitle_track",
                "provider": "youtube_subtitles",
                "model": str(source_subs / "7J5aS_pcBj4.ja.json3").replace("\\", "/"),
                "real_transcript": True,
            },
            "segment_count": 1,
            "segments": [
                {
                    "id": "seg_001",
                    "start_seconds": 0.0,
                    "end_seconds": 1.0,
                    "text": "hello",
                    "review_status": "accepted",
                }
            ],
        },
        episode_dir / "transcript.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_r3",
            "review": {"status": "draft"},
            "cut_candidates": [],
            "selected_cut_ids": [],
            "subtitles": [],
        },
        episode_dir / "edit_pack.json",
    )
    render_manifest = render_dir / "render_manifest.json"
    _write_json(
        {
            "schema_version": "v1",
            "artifact_kind": "tiny_render_proof",
            "episode_id": "ep_r3",
            "output_id": "r3_diagnostic_render",
            "production_candidate": False,
            "creative_acceptance": False,
            "publish_acceptance": False,
            "source_refs": {
                "source_video": {
                    "material_id": "src_video_jp_pilot01",
                    "source_url": "https://www.youtube.com/watch?<query:redacted>",
                },
                "source_audio": {"material_id": "src_audio_jp_pilot01"},
                "edit_pack": {"path": str(episode_dir / "edit_pack.json").replace("\\", "/")},
                "transcript": {
                    "engine": "subtitle_track",
                    "provider": "youtube_subtitles",
                    "model": str(source_subs / "7J5aS_pcBj4.ja.json3").replace("\\", "/"),
                },
            },
            "timeline_mapping": {"duration_target_seconds": 6.84},
            "subtitle_burn_in": {"requested_mode": "diagnostic"},
            "outputs": {
                "rendered_video": str(artifact).replace("\\", "/"),
                "render_receipt": str(render_dir / "render_receipt.json").replace("\\", "/"),
                "render_report": str(render_dir / "render_report.html").replace("\\", "/"),
            },
            "output_metadata": {
                "duration_seconds": 6.84,
                "resolution": "1920x1080",
                "video_codec": "h264",
                "audio_codec": "aac",
            },
        },
        render_manifest,
    )
    _write_json({"schema_version": "v1"}, render_dir / "render_receipt.json")
    (render_dir / "render_report.html").write_text("<html>render report</html>", encoding="utf-8")
    nle_manifest = export_dir / "nle_export_manifest.json"
    _write_json({"schema_version": "v1", "production_edit_candidate": False}, nle_manifest)
    return episode_dir, render_manifest, nle_manifest, artifact


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
