"""OUT-01 output layer gap report tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.output_layer.build_output_layer_gap_report import (
    ALLOWED_STATES,
    build_output_layer_gap_report,
    render_local_output_readback_html,
    write_output_layer_gap_report,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_ROW_FIELDS = {
    "capability_id",
    "current_state",
    "evidence_path",
    "missing_input",
    "next_local_action",
    "blocked_by_true_gate",
    "notes",
}


def test_report_has_required_capability_rows_and_states() -> None:
    report = build_output_layer_gap_report(base_dir=REPO_ROOT, generated_at="test-run")
    rows = {row["capability_id"]: row for row in report["capability_matrix"]}

    assert set(rows) == {
        "source_material_presence",
        "transcript_readiness",
        "edit_pack_readiness",
        "subtitle_readiness",
        "thumbnail_brief_readiness",
        "preview_pack_readiness",
        "nle_export_readiness",
        "local_render_proof_readiness",
        "public_upload_readiness",
    }
    for row in rows.values():
        assert REQUIRED_ROW_FIELDS.issubset(row)
        assert row["current_state"] in ALLOWED_STATES
        assert isinstance(row["evidence_path"], str)
        assert row["evidence_path"]
        assert row["evidence_exists"] is True

    assert rows["source_material_presence"]["current_state"] == "absent"
    assert rows["thumbnail_brief_readiness"]["current_state"] == "planned"
    assert rows["public_upload_readiness"]["current_state"] == "gated"
    assert rows["public_upload_readiness"]["blocked_by_true_gate"] is True


def test_report_gap_log_marks_proof_missing_and_next_out_slice() -> None:
    report = build_output_layer_gap_report(base_dir=REPO_ROOT, generated_at="test-run")

    assert report["proof_readback"]["proof_status"] == "proof_missing"
    assert report["proof_readback"]["production_ready"] is False
    assert report["proof_readback"]["public_ready"] is False
    assert report["scope"]["network_used"] is False
    assert report["scope"]["media_generated"] is False
    assert len(report["gap_log"]) >= 5
    assert any(gap["status"] == "true_gate" for gap in report["gap_log"])
    assert any(gap["status"] == "recommendation" for gap in report["gap_log"])
    assert report["recommended_next_slice"]["slice_id"].startswith("OUT-02")


def test_write_outputs_are_parseable_and_html_is_no_media_readback(tmp_path: Path) -> None:
    result = write_output_layer_gap_report(
        base_dir=REPO_ROOT,
        output_dir=tmp_path / "output_layer",
        generated_at="test-run",
    )
    outputs = result["outputs"]
    json_path = tmp_path / "output_layer" / "video_output_gap_log.json"
    matrix_path = tmp_path / "output_layer" / "output_capability_matrix.md"
    html_path = tmp_path / "output_layer" / "local_output_readback.html"

    assert outputs["video_output_gap_log"] == json_path.as_posix()
    assert json.loads(json_path.read_text(encoding="utf-8"))["schema_version"] == "v0"
    assert "public_upload_readiness" in matrix_path.read_text(encoding="utf-8")

    html = html_path.read_text(encoding="utf-8")
    assert "OUT-01 Local Output Readback" in html
    assert "proof_missing" in html
    assert "<button" not in html.lower()
    assert "<form" not in html.lower()
    assert "<video" not in html.lower()
    assert render_local_output_readback_html(result["report"]).startswith("<!doctype html>")


def test_cli_writes_report_json_readback(tmp_path: Path) -> None:
    output_dir = tmp_path / "docs" / "output_layer"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-output-layer-gap-report",
            "--output-dir",
            str(output_dir),
            "--generated-at",
            "test-run",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["format"] == "output_layer_gap_report_v0"
    assert payload["proof_status"] == "proof_missing"
    assert payload["production_ready"] is False
    assert payload["public_ready"] is False
    assert payload["network_used"] is False
    assert payload["media_generated"] is False
    assert payload["capability_count"] == 9
    assert payload["gap_count"] >= 5
    assert (output_dir / "video_output_gap_log.json").exists()
    assert (output_dir / "output_capability_matrix.md").exists()
    assert (output_dir / "local_output_readback.html").exists()
