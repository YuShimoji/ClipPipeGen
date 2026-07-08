"""TRI-01 safety overcapture triage report tests."""

from __future__ import annotations

import json
from pathlib import Path

from tools.triage import build_safety_overcapture_report as triage


REQUIRED_FINDING_FIELDS = {
    "id",
    "file",
    "line_or_pattern",
    "classification",
    "why_it_matters",
    "risk_if_changed",
    "recommended_action",
    "priority",
    "safe_next_slice",
}


def test_safety_overcapture_report_has_required_fields_and_counts():
    report = triage.build_report(generated_at="test-run")
    findings = report["findings"]
    counts = report["summary"]["count_by_classification"]

    assert report["schema_id"] == triage.SCHEMA_ID
    assert report["scope"]["behavior_changed"] is False
    assert report["scope"]["safety_behavior_loosened"] is False
    assert findings
    assert set(counts) == set(triage.CLASSIFICATIONS)
    assert sum(counts.values()) == len(findings)
    assert all(count > 0 for count in counts.values())

    for finding in findings:
        assert REQUIRED_FINDING_FIELDS <= set(finding)
        assert finding["classification"] in triage.CLASSIFICATIONS
        assert finding["priority"] in triage.PRIORITY_ORDER
        for field in REQUIRED_FINDING_FIELDS:
            assert finding[field]


def test_report_preserves_strict_gates_and_names_overcapture_candidates():
    report = triage.build_report(generated_at="test-run")
    findings_by_id = {finding["id"]: finding for finding in report["findings"]}
    top_ids = {
        item["id"]
        for item in report["summary"]["highest_priority_overcapture_candidates"]
    }

    assert findings_by_id["tri_true_public_publication_gate"][
        "classification"
    ] == "true_external_gate"
    assert findings_by_id["tri_true_oauth_credentials_gate"][
        "classification"
    ] == "true_external_gate"
    assert findings_by_id["tri_overcapture_pipeline_term_scan"][
        "classification"
    ] == "overcapture_candidate"
    assert findings_by_id["tri_overcapture_help_text_word_absence"][
        "classification"
    ] == "overcapture_candidate"
    assert "tri_overcapture_pipeline_term_scan" in top_ids
    assert "tri_overcapture_help_text_word_absence" in top_ids


def test_report_splits_execution_path_from_wording_or_hybrid_tests():
    report = triage.build_report(generated_at="test-run")
    summary = report["summary"]

    execution_tests = {item["test"] for item in summary["tests_likely_execution_path"]}
    wording_tests = {
        item["test"] for item in summary["tests_likely_wording_only_or_hybrid"]
    }

    assert "test_fetch_source_video_yt_dlp_video_creates_artifacts" in execution_tests
    assert "test_ffmpeg_and_ytdlp_do_not_enter_pipeline_or_editing_cli" in wording_tests
    assert "test_fetch_source_video_help_exposes_yt_dlp_video_options" in wording_tests
    assert execution_tests.isdisjoint(wording_tests)


def test_write_report_round_trips_json_and_markdown(tmp_path: Path):
    output_json = tmp_path / "safety_overcapture_report.json"
    output_md = tmp_path / "safety_overcapture_report.md"

    report = triage.write_report(
        output_json=output_json,
        output_md=output_md,
        generated_at="test-run",
    )

    persisted = json.loads(output_json.read_text(encoding="utf-8"))
    markdown = output_md.read_text(encoding="utf-8")
    assert persisted["artifact_id"] == report["artifact_id"]
    assert persisted["summary"]["count_by_classification"] == report["summary"][
        "count_by_classification"
    ]
    assert "# TRI-01 Safety Overcapture Report" in markdown
    assert "tri_overcapture_pipeline_term_scan" in markdown
