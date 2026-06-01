"""JP-Pilot R3 cut decision packet tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.cut_decision_packet import build_cut_decision_packet
from src.pipeline.episode_status import build_episode_status

from tests.test_chapter_revision_board import _write_episode


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_cut_decision_packet_classifies_all_r3_cuts(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = build_cut_decision_packet(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )

    packet = result["packet"]
    summary = packet["summary"]
    assert packet["artifact_kind"] == "r3_cut_decision_packet"
    assert packet["decision_scope"] == "candidate_for_next_acceptance_slice_only"
    assert packet["production_candidate"] is False
    assert packet["creative_acceptance"] is False
    assert packet["publish_acceptance"] is False
    assert packet["rights_status"] == "pending"
    assert summary["decision_counts"] == {"keep": 3, "reject": 1, "needs_adjustment": 5}
    assert summary["keep_cut_ids"] == ["cut_001", "cut_002", "cut_003"]
    assert summary["needs_adjustment_cut_ids"] == [
        "cut_004",
        "cut_005",
        "cut_006",
        "cut_007",
        "cut_008",
    ]
    assert summary["reject_cut_ids"] == ["cut_009"]
    cut_003 = _decision(packet, "cut_003")
    assert cut_003["context_status"] == "needs_review"
    assert "not as production-approved" in cut_003["manual_override_reason"]
    assert _decision(packet, "cut_008")["subtitle_timing_status"]["overlap_count"] == 0
    assert result["packet_path"].exists()
    assert result["report_path"].exists()


def test_cut_decision_report_names_candidate_boundary(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = build_cut_decision_packet(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )

    html = result["report_path"].read_text(encoding="utf-8")
    assert "not production acceptance" in html
    assert "not rights approval" in html
    assert "not publishing acceptance" in html
    assert "production_candidate=false" in html
    assert "cut_003" in html
    assert "needs_adjustment" in html


def test_build_cut_decision_packet_cli_writes_json_and_html(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-cut-decision-packet",
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
    assert payload["decision_counts"] == {"keep": 3, "reject": 1, "needs_adjustment": 5}
    assert payload["keep_cut_ids"] == ["cut_001", "cut_002", "cut_003"]
    assert payload["kept_needs_review_cut_ids"] == ["cut_003"]
    assert payload["production_candidate"] is False
    assert payload["rights_status"] == "pending"
    assert Path(payload["packet"]).exists()
    assert Path(payload["report"]).exists()


def test_status_episode_reads_final_cut_decision_summary(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    build_cut_decision_packet(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )

    status = build_episode_status(episode_dir=episode_dir, base_dir=tmp_path)

    final = status["final_cut_decision"]
    assert final["state"] == "ready"
    assert final["ready_for_next_acceptance_slice"] is True
    assert final["keep_cut_ids"] == ["cut_001", "cut_002", "cut_003"]
    assert final["needs_adjustment_cut_ids"] == [
        "cut_004",
        "cut_005",
        "cut_006",
        "cut_007",
        "cut_008",
    ]
    assert final["reject_cut_ids"] == ["cut_009"]
    assert final["production_candidate"] is False
    assert final["rights_status"] == "pending"
    assert status["next_action"]["action"].startswith("Start production subtitle/render acceptance")


def _decision(packet: dict, cut_id: str) -> dict:
    return next(item for item in packet["decisions"] if item["cut_id"] == cut_id)
