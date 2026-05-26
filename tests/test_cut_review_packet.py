"""Cut review packet generation tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.cut_review_packet import build_cut_review_packet
from src.pipeline.edit_pack import build_skeleton, save_edit_pack
from src.pipeline.rights_manifest import build_skeleton as build_rights_skeleton
from src.pipeline.rights_manifest import save_rights_manifest
from src.pipeline.transcript import build_transcript, save_transcript


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_cut_review_packet_summarizes_needs_review_and_boundaries(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)

    result = build_cut_review_packet(
        episode_dir=episode_dir,
        edit_pack_path=episode_dir / "edit_pack.json",
        transcript_path=episode_dir / "transcript.json",
        rights_manifest_path=episode_dir / "rights_manifest.json",
        nle_manifest_path=episode_dir / "exports" / "r3" / "nle_export_manifest.json",
        render_manifest_path=episode_dir / "renders" / "r3" / "render_manifest.json",
        output_dir=episode_dir / "review" / "r3",
        base_dir=tmp_path,
    )

    packet = result["packet"]
    report = result["report_path"].read_text(encoding="utf-8")
    evidence_report = result["evidence_report_path"].read_text(encoding="utf-8")
    evidence = result["evidence"]

    assert packet["summary"]["cut_count"] == 2
    assert packet["summary"]["context_counts"] == {"passed": 1, "needs_review": 1, "failed": 0, "not_checked": 0}
    assert packet["summary"]["production_candidate"] is False
    assert packet["source_refs"]["rights"]["status"] == "pending"
    assert packet["source_refs"]["rights"]["production_usage_allowed"] is False
    needs_review = packet["cuts"][1]
    assert needs_review["needs_review_reason_category"] == "nearby_previous_context"
    assert "setup" in needs_review["suggested_human_review_focus"]
    assert needs_review["decision_placeholder"]["final_decision"] == "undecided"
    assert needs_review["subtitle_event_count"] == 2
    assert "Production candidate: false" in report
    assert "Operator Reviewability" in report
    assert "What this page is" in report
    assert "review_ready=true" in report
    assert "Natural language is allowed" in report
    assert "Recovery and reproduction commands are appendix material" in report
    assert evidence["metrics"]["render"]["production_candidate"] is False
    assert evidence["metrics"]["rights"]["production_usage_allowed"] is False
    assert evidence["operator_review"]["reviewability"] == "diagnostic_only"
    assert any("rights_manifest status=pending" in item for item in evidence["boundary_evidence"])
    assert "Operator Reviewability" in evidence_report
    assert "<details>" in evidence_report
    assert "<summary>Recovery / reproduction commands</summary>" in evidence_report
    generated = {
        item["name"]: item for item in evidence["artifact_inventory"]
        if item["name"] in {"cut_review_packet", "cut_review_report", "evidence_summary", "evidence_report"}
    }
    assert all(item["exists"] for item in generated.values())


def test_cut_review_packet_cli_writes_json_and_html(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    output_dir = episode_dir / "review" / "cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-cut-review-packet",
            "--episode-dir",
            str(episode_dir),
            "--nle-manifest",
            str(episode_dir / "exports" / "r3" / "nle_export_manifest.json"),
            "--render-manifest",
            str(episode_dir / "renders" / "r3" / "render_manifest.json"),
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
    assert payload["cut_count"] == 2
    assert payload["production_candidate"] is False
    assert Path(payload["packet"]).exists()
    assert Path(payload["report"]).exists()
    assert Path(payload["evidence_summary"]).exists()
    assert Path(payload["evidence_report"]).exists()
    evidence_report = Path(payload["evidence_report"]).read_text(encoding="utf-8")
    assert "Production candidate: false" in evidence_report
    assert "rights_manifest status=pending" in evidence_report
    assert "<summary>Recovery / reproduction commands</summary>" in evidence_report


def test_operator_review_ux_doc_accepts_natural_language_and_blocks_auto_final_cut():
    doc = (REPO_ROOT / "docs" / "OPERATOR_REVIEW_UX.md").read_text(encoding="utf-8")
    assert "review_blocked_missing_artifacts" in doc
    assert "natural language" in doc
    assert "must not auto-accept" in doc
    assert "Commands" in doc and "appendix" in doc


def _write_episode(tmp_path: Path) -> Path:
    episode_dir = tmp_path / "episodes" / "ep_r3"
    episode_dir.mkdir(parents=True)
    save_rights_manifest(build_rights_skeleton("ep_r3"), episode_dir / "rights_manifest.json")
    transcript = _transcript()
    save_transcript(transcript, episode_dir / "transcript.json")
    edit_pack = _edit_pack(episode_dir)
    save_edit_pack(edit_pack, episode_dir / "edit_pack.json")
    _write_json(
        {
            "schema_version": "v1",
            "artifact_kind": "nle_export",
            "production_edit_candidate": False,
            "summary": {"cut_rows": 2, "selected_cut_count": 2, "subtitle_count": 3},
            "warnings": ["not production edit acceptance"],
        },
        episode_dir / "exports" / "r3" / "nle_export_manifest.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "artifact_kind": "tiny_render",
            "production_candidate": False,
            "creative_acceptance": False,
            "publish_acceptance": False,
            "outputs": {
                "rendered_video": "episodes/ep_r3/renders/r3/rendered_video.mp4",
                "render_receipt": "episodes/ep_r3/renders/r3/render_receipt.json",
                "render_report": "episodes/ep_r3/renders/r3/render_report.html",
            },
            "output_metadata": {
                "duration_seconds": 6.84,
                "resolution": "1920x1080",
                "video_codec": "h264",
                "audio_codec": "aac",
            },
            "warnings": ["diagnostic render is not production acceptance"],
        },
        episode_dir / "renders" / "r3" / "render_manifest.json",
    )
    return episode_dir


def _transcript() -> dict:
    return build_transcript(
        "ep_r3",
        source_audio_path="episodes/ep_r3/materials/src_audio/source.wav",
        material_id="src_audio",
        source_audio_sha256="sha",
        source_audio_duration_seconds=20.0,
        source_audio_sample_rate_hz=16000,
        source_audio_channels=1,
        language="ja",
        stt_engine="subtitle_track",
        stt_provider="youtube_subtitles",
        stt_engine_version="youtube-json3",
        stt_model="episodes/ep_r3/source_subs/source.ja.json3",
        stt_warnings=[
            "subtitle track import is a transcript alignment aid, not subtitle design or production acceptance"
        ],
        segments=[
            {"id": "seg_000001", "start_seconds": 0.0, "end_seconds": 2.0, "text": "hello", "review_status": "accepted"},
            {"id": "seg_000002", "start_seconds": 2.0, "end_seconds": 4.0, "text": "setup", "review_status": "accepted"},
            {"id": "seg_000003", "start_seconds": 4.0, "end_seconds": 6.0, "text": "payoff", "review_status": "accepted"},
        ],
        real_transcript=True,
    )


def _edit_pack(episode_dir: Path) -> dict:
    edit_pack = build_skeleton(
        "ep_r3",
        rights_manifest_path=str(episode_dir / "rights_manifest.json").replace("\\", "/"),
        material_ledger_path=str(episode_dir / "material_ledger.json").replace("\\", "/"),
    )
    edit_pack["cut_candidates"] = [
        {
            "id": "cut_001",
            "start_seconds": 0.0,
            "end_seconds": 2.0,
            "source": "auto",
            "reason": "auto transcript window: seg_000001",
            "confidence": 0.8,
            "context_check": {
                "status": "passed",
                "notes": ["context check passed: seg_000001 boundaries align with transcript segments"],
                "checked_at": "2026-05-26T00:00:00+00:00",
                "source": "transcript_boundary_v1",
            },
            "source_segment_ids": ["seg_000001"],
        },
        {
            "id": "cut_002",
            "start_seconds": 4.0,
            "end_seconds": 6.0,
            "source": "auto",
            "reason": "auto transcript window: seg_000003",
            "confidence": 0.7,
            "context_check": {
                "status": "needs_review",
                "notes": ["previous segment seg_000002 ends 0.00s before cut context starts"],
                "checked_at": "2026-05-26T00:00:00+00:00",
                "source": "transcript_boundary_v1",
            },
            "source_segment_ids": ["seg_000003"],
        },
    ]
    edit_pack["selected_cut_ids"] = ["cut_001", "cut_002"]
    edit_pack["subtitles"] = [
        _subtitle("sub_001", "cut_001", 0.0, 2.0, "hello", "seg_000001"),
        _subtitle("sub_002", "cut_002", 4.0, 5.0, "pay", "seg_000003"),
        _subtitle("sub_003", "cut_002", 5.0, 6.0, "off", "seg_000003"),
    ]
    return edit_pack


def _subtitle(
    subtitle_id: str,
    cut_id: str,
    start: float,
    end: float,
    text: str,
    segment_id: str,
) -> dict:
    return {
        "id": subtitle_id,
        "cut_id": cut_id,
        "start_seconds": start,
        "end_seconds": end,
        "text": text,
        "source": "auto",
        "source_type": "imported_subtitle_track",
        "style_slot": "subtitle.default",
        "source_segment_id": segment_id,
        "source_segment_ids": [segment_id],
        "draft": True,
        "diagnostic": True,
        "not_production_subtitle_design": True,
        "production_subtitle_design": False,
    }


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
