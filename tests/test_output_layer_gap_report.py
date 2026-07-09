"""OUT-02 output layer fixture proof and gap report tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.output_layer.build_output_layer_gap_report import (
    ALLOWED_STATES,
    PROOF_STATUS,
    build_output_layer_gap_report,
    render_fixture_subtitles_srt,
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
        "local_fixture_output_proof",
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

    assert rows["source_material_presence"]["current_state"] == "fixture_only"
    assert rows["local_fixture_output_proof"]["current_state"] == "fixture_only"
    assert rows["thumbnail_brief_readiness"]["current_state"] == "planned"
    assert rows["public_upload_readiness"]["current_state"] == "gated"
    assert rows["public_upload_readiness"]["blocked_by_true_gate"] is True


def test_report_gap_log_marks_fixture_proof_present_and_remaining_gates() -> None:
    report = build_output_layer_gap_report(base_dir=REPO_ROOT, generated_at="test-run")

    proof = report["proof_readback"]
    assert proof["proof_status"] == PROOF_STATUS
    assert proof["source_kind"] == "synthetic_fixture"
    assert proof["external_media_used"] is False
    assert proof["network_used"] is False
    assert proof["fetch_authorized"] is False
    assert proof["rights_approved"] is False
    assert proof["production_ready"] is False
    assert proof["public_ready"] is False
    assert report["scope"]["media_generated"] is False
    assert report["scope"]["yt_dlp_used"] is False

    gaps = {gap["gap_id"]: gap for gap in report["gap_log"]}
    assert gaps["gap_current_no_proof_artifact"]["status"] == PROOF_STATUS
    assert gaps["gap_real_source_material_absent"]["status"] == "remaining_gap"
    assert gaps["gap_real_transcript_absent"]["status"] == "remaining_gap"
    assert gaps["gap_production_render_absent"]["status"] == "remaining_gap"
    assert gaps["gap_rights_approval_absent"]["status"] == "true_gate"
    assert gaps["gap_public_upload_true_gate"]["status"] == "true_gate"
    assert report["recommended_next_slice"]["slice_id"] == "OUT-03-selected-cut-proof-link"


def test_write_outputs_are_parseable_and_html_is_static_fixture_readback(tmp_path: Path) -> None:
    result = write_output_layer_gap_report(
        base_dir=REPO_ROOT,
        output_dir=tmp_path / "output_layer",
        generated_at="test-run",
    )
    outputs = result["outputs"]
    json_path = tmp_path / "output_layer" / "video_output_gap_log.json"
    matrix_path = tmp_path / "output_layer" / "output_capability_matrix.md"
    html_path = tmp_path / "output_layer" / "local_output_readback.html"
    proof_dir = tmp_path / "output_layer" / "local_fixture_output_proof"
    proof_manifest_path = proof_dir / "proof_manifest.json"
    proof_readback_path = proof_dir / "proof_readback.json"
    proof_timeline_path = proof_dir / "proof_timeline.html"
    fixture_edit_pack_path = proof_dir / "fixture_edit_pack.json"
    fixture_subtitles_path = proof_dir / "fixture_subtitles.srt"
    proof_readme_path = proof_dir / "README.md"

    assert outputs["video_output_gap_log"] == json_path.as_posix()
    report_json = json.loads(json_path.read_text(encoding="utf-8"))
    assert report_json["proof_readback"]["proof_status"] == PROOF_STATUS
    assert "local_fixture_output_proof" in matrix_path.read_text(encoding="utf-8")

    manifest = json.loads(proof_manifest_path.read_text(encoding="utf-8"))
    readback = json.loads(proof_readback_path.read_text(encoding="utf-8"))
    fixture_edit_pack = json.loads(fixture_edit_pack_path.read_text(encoding="utf-8"))
    assert manifest["proof_status"] == PROOF_STATUS
    assert manifest["source_kind"] == "synthetic_fixture"
    assert manifest["external_media_used"] is False
    assert manifest["network_used"] is False
    assert manifest["fetch_authorized"] is False
    assert manifest["rights_approved"] is False
    assert manifest["public_ready"] is False
    assert manifest["production_ready"] is False
    assert readback["subtitle_band"]["source"] == "fixture_subtitles.srt"
    assert fixture_edit_pack["selected_cut_ids"] == manifest["selected_cut_ids"]

    top_html = html_path.read_text(encoding="utf-8")
    timeline_html = proof_timeline_path.read_text(encoding="utf-8")
    assert "OUT-02 Local Output Readback" in top_html
    assert PROOF_STATUS in top_html
    assert "proof_manifest.json" in top_html
    assert "OUT-02 Local Fixture Output Proof" in timeline_html
    assert "Subtitle band source" in timeline_html
    for html in (top_html, timeline_html):
        assert "<button" not in html.lower()
        assert "<form" not in html.lower()
        assert "<video" not in html.lower()
    assert "Local fixture proof starts here." in fixture_subtitles_path.read_text(encoding="utf-8")
    assert "What This Proves" in proof_readme_path.read_text(encoding="utf-8")
    assert render_local_output_readback_html(result["report"]).startswith("<!doctype html>")
    assert "00:00:00,000 --> 00:00:02,800" in render_fixture_subtitles_srt(
        result["proof_package"]["proof_readback"]["segments"]
    )


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
    assert payload["proof_status"] == PROOF_STATUS
    assert payload["source_kind"] == "synthetic_fixture"
    assert payload["external_media_used"] is False
    assert payload["production_ready"] is False
    assert payload["public_ready"] is False
    assert payload["network_used"] is False
    assert payload["fetch_authorized"] is False
    assert payload["rights_approved"] is False
    assert payload["media_generated"] is False
    assert payload["capability_count"] == 10
    assert payload["gap_count"] >= 7
    assert payload["recommended_next_slice"] == "OUT-03-selected-cut-proof-link"
    assert payload["proof_artifacts"]["proof_manifest"].endswith("proof_manifest.json")
    assert (output_dir / "video_output_gap_log.json").exists()
    assert (output_dir / "output_capability_matrix.md").exists()
    assert (output_dir / "local_output_readback.html").exists()
    assert (output_dir / "local_fixture_output_proof" / "proof_manifest.json").exists()
