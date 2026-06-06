"""ED-10e boundary recommendation receipt tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.boundary_recommendation_apply import (
    BoundaryRecommendationApplyError,
    build_boundary_recommendation_receipt,
)
from src.pipeline.edit_pack import build_skeleton, load_edit_pack, save_edit_pack


REPO_ROOT = Path(__file__).resolve().parent.parent


def _pack(*, overlap: bool = True) -> dict:
    pack = build_skeleton("ep_boundary_001")
    pack["cut_candidates"] = [
        {
            "id": "cut_003",
            "start_seconds": 22.606,
            "end_seconds": 41.725,
            "source": "auto",
            "reason": "seg_000010..seg_000024",
            "confidence": 0.888,
            "context_check": {
                "status": "needs_review",
                "notes": ["next segment seg_000025 starts 0.00s after cut context ends"],
            },
            "source_segment_ids": [
                "seg_000010",
                "seg_000011",
                "seg_000012",
                "seg_000013",
                "seg_000014",
                "seg_000015",
                "seg_000016",
                "seg_000017",
                "seg_000018",
                "seg_000019",
                "seg_000020",
                "seg_000021",
                "seg_000022",
                "seg_000023",
                "seg_000024",
            ],
        },
        {
            "id": "cut_004",
            "start_seconds": 41.725 if overlap else 60.277,
            "end_seconds": 60.277 if overlap else 72.0,
            "source": "auto",
            "reason": "seg_000025..seg_000034",
            "confidence": 0.867,
            "context_check": {"status": "needs_review", "notes": []},
            "source_segment_ids": ["seg_000025", "seg_000026", "seg_000027"],
        },
    ]
    pack["selected_cut_ids"] = ["cut_003", "cut_004"]
    pack["subtitles"] = [
        {
            "id": "sub_025",
            "cut_id": "cut_004",
            "start_seconds": 41.725,
            "end_seconds": 43.36,
            "text": "長(ちょう)？　長って言った？",
            "source": "auto",
            "source_type": "imported_subtitle_track",
            "source_segment_id": "seg_000025",
            "source_segment_ids": ["seg_000025"],
            "draft": True,
        },
        {
            "id": "sub_029",
            "cut_id": "cut_004",
            "start_seconds": 48.999,
            "end_seconds": 49.566,
            "text": "ありがとうございますー！",
            "source": "auto",
            "source_type": "imported_subtitle_track",
            "source_segment_id": "seg_000029",
            "source_segment_ids": ["seg_000029"],
            "draft": True,
        },
        {
            "id": "sub_030",
            "cut_id": "cut_004",
            "start_seconds": 50.868,
            "end_seconds": 53.904,
            "text": "ホロライブの番長として、 船長を倒してやる！！",
            "source": "auto",
            "source_type": "imported_subtitle_track",
            "source_segment_id": "seg_000030",
            "source_segment_ids": ["seg_000030"],
            "draft": True,
        },
    ]
    return pack


def _recommendation() -> dict:
    return {
        "schema_version": "v1",
        "artifact_kind": "cut_boundary_recommendation_report_v0",
        "episode_id": "ep_boundary_001",
        "decision_authority_ref": "chapter_revision_patch.operator.json",
        "recommendation": {
            "cut_id": "cut_003",
            "boundary_request": "adjust_end",
            "current_start_seconds": 22.606,
            "current_end_seconds": 41.725,
            "current_duration_seconds": 19.119,
            "recommended_start_seconds": 22.606,
            "recommended_end_seconds": 49.566,
            "recommended_duration_seconds": 26.96,
            "proposed_added_segments": [
                "seg_000025",
                "seg_000026",
                "seg_000027",
                "seg_000028",
                "seg_000029",
            ],
            "excluded_next_segment": "seg_000030",
            "boundary_application_status": "proposal_only_not_applied",
            "rationale": (
                "seg_000024 asks about other Bancho; seg_000025..seg_000029 "
                "provide the response/referral; seg_000030 starts the next challenge arc."
            ),
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_dry_run_receipt_writes_no_mutation_when_no_overlap(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    recommendation_path = tmp_path / "recommendation.json"
    receipt_path = tmp_path / "receipt.json"
    save_edit_pack(_pack(overlap=False), edit_pack_path)
    before = edit_pack_path.read_text(encoding="utf-8")
    _write_json(recommendation_path, _recommendation())

    receipt = build_boundary_recommendation_receipt(
        episode_dir=tmp_path,
        edit_pack_path=edit_pack_path,
        recommendation_report_path=recommendation_path,
        cut_id="cut_003",
        output_receipt_path=receipt_path,
        dry_run=True,
    )

    assert receipt["status"] == "dry_run"
    assert receipt["edit_pack_mutated"] is False
    assert edit_pack_path.read_text(encoding="utf-8") == before
    assert receipt_path.exists()
    assert receipt_path.with_suffix(".html").exists()


def test_current_range_mismatch_blocks_before_receipt(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    recommendation_path = tmp_path / "recommendation.json"
    receipt_path = tmp_path / "receipt.json"
    pack = _pack()
    pack["cut_candidates"][0]["end_seconds"] = 42.0
    save_edit_pack(pack, edit_pack_path)
    _write_json(recommendation_path, _recommendation())

    with pytest.raises(BoundaryRecommendationApplyError, match="current_end_seconds"):
        build_boundary_recommendation_receipt(
            episode_dir=tmp_path,
            edit_pack_path=edit_pack_path,
            recommendation_report_path=recommendation_path,
            cut_id="cut_003",
            output_receipt_path=receipt_path,
            dry_run=True,
        )
    assert not receipt_path.exists()


def test_selected_cut_overlap_blocks_and_reports_cut_004(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    recommendation_path = tmp_path / "recommendation.json"
    receipt_path = tmp_path / "receipt.json"
    save_edit_pack(_pack(overlap=True), edit_pack_path)
    before = load_edit_pack(edit_pack_path)
    _write_json(recommendation_path, _recommendation())

    receipt = build_boundary_recommendation_receipt(
        episode_dir=tmp_path,
        edit_pack_path=edit_pack_path,
        recommendation_report_path=recommendation_path,
        cut_id="cut_003",
        output_receipt_path=receipt_path,
        dry_run=True,
    )

    assert receipt["status"] == "blocked_overlap"
    assert receipt["conflict_detection"]["has_overlap"] is True
    assert receipt["conflict_detection"]["conflicting_cut_ids"] == ["cut_004"]
    conflict = receipt["conflict_detection"]["conflicts"][0]
    assert conflict["start_seconds"] == 41.725
    assert conflict["end_seconds"] == 60.277
    assert load_edit_pack(edit_pack_path) == before


def test_receipt_preserves_evidence_and_production_boundaries(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    recommendation_path = tmp_path / "recommendation.json"
    receipt_path = tmp_path / "receipt.json"
    save_edit_pack(_pack(overlap=True), edit_pack_path)
    _write_json(recommendation_path, _recommendation())

    receipt = build_boundary_recommendation_receipt(
        episode_dir=tmp_path,
        edit_pack_path=edit_pack_path,
        recommendation_report_path=recommendation_path,
        cut_id="cut_003",
        output_receipt_path=receipt_path,
        dry_run=True,
    )

    subtitles = receipt["subtitle_assignment_status"]["affected_subtitles"]
    assert receipt["subtitle_assignment_status"]["stale_or_requires_regeneration"] is True
    assert [item["subtitle_id"] for item in subtitles] == ["sub_025", "sub_029", "sub_030"]
    assert subtitles[0]["current_cut_id"] == "cut_004"
    assert receipt["transcript_not_mutated"] is True
    assert receipt["official_subtitle_evidence_not_mutated"] is True
    assert receipt["source_media_not_mutated"] is True
    assert receipt["proof_stale_or_requires_regeneration"] is True
    assert receipt["production_candidate"] is False
    assert receipt["rights_status"] == "pending"
    assert receipt["production_usage_allowed"] is False


def test_cli_writes_blocked_receipt(tmp_path: Path):
    edit_pack_path = tmp_path / "edit_pack.json"
    recommendation_path = tmp_path / "recommendation.json"
    receipt_path = tmp_path / "receipt.json"
    save_edit_pack(_pack(overlap=True), edit_pack_path)
    _write_json(recommendation_path, _recommendation())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "apply-boundary-recommendation",
            "--episode-dir",
            str(tmp_path),
            "--edit-pack",
            str(edit_pack_path),
            "--recommendation-report",
            str(recommendation_path),
            "--cut-id",
            "cut_003",
            "--output-receipt",
            str(receipt_path),
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
    assert payload["status"] == "blocked_overlap"
    assert payload["conflicting_cut_ids"] == ["cut_004"]
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["status"] == "blocked_overlap"
