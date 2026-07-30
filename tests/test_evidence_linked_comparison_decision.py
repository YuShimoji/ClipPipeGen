from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from src.cli.main import main
from src.integrations.render import evidence_linked_comparison as comparison
from src.integrations.render.evidence_linked_comparison_decision import (
    DECISION_INPUT_SCHEMA_VERSION,
    REVIEW_DIMENSIONS,
    EvidenceLinkedComparisonDecisionError,
    record_evidence_linked_comparison_decision,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _build_artifact(tmp_path: Path) -> tuple[Path, dict]:
    artifact = tmp_path / "artifact"
    review = artifact / "review"
    review.mkdir(parents=True)
    video = artifact / "final_video.mp4"
    video.write_bytes(b"synthetic-s2-test-video")
    (review / "index.html").write_text(
        '<video controls muted preload="metadata" '
        'src="../final_video.mp4"></video>\n',
        encoding="utf-8",
    )

    payloads = []
    for path in (video, review / "index.html"):
        payloads.append(
            {
                "path": path.relative_to(artifact).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "byte_size": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": comparison.MANIFEST_SCHEMA_VERSION,
        "artifact_id": "clip-s2-decision-test-001",
        "state": comparison.READY_STATE,
        "private_review_only": True,
        "human_review_pending": True,
        "rights_approval": "not_granted",
        "production_approval": False,
        "public_use": False,
        "monetized_use": False,
        "publication_approval": False,
        "upload_attempted": False,
        "source_identities": ["youtube:first", "youtube:second"],
        "output": {
            "path": "final_video.mp4",
            "sha256": payloads[0]["sha256"],
            "byte_size": payloads[0]["byte_size"],
            "duration_seconds": 63.466667,
        },
        "comparison": {
            "beat_count": 3,
            "presentation": "stable_concurrent_source_panels",
            "concurrent_source_panels": True,
            "foreground_audio_owner_per_beat": 1,
        },
        "payloads": payloads,
        "payload_tree_digest": {
            "algorithm": "sha256",
            "sha256": comparison._payload_tree_digest(payloads),
            "file_count": len(payloads),
        },
    }
    manifest["manifest_self_integrity"] = {
        "algorithm": "sha256",
        "scope": "canonical_json_without_manifest_self_integrity",
        "sha256": comparison._manifest_self_hash(manifest),
    }
    _write_json(artifact / "run_manifest.json", manifest)
    comparison.validate_run_manifest(artifact)
    return artifact, manifest


def _decision(manifest: dict, *, verdict: str = "accept") -> dict:
    results = {key: "pass" for key in REVIEW_DIMENSIONS}
    instructions: list[str] = []
    if verdict == "bounded_repair":
        results["foreground_audio_transitions"] = "needs_repair"
        instructions = ["Beat 2のaudio-owner切替を短くする。"]
    elif verdict == "reject":
        results["thesis_coherence"] = "fail"
    return {
        "schema_version": DECISION_INPUT_SCHEMA_VERSION,
        "artifact_id": manifest["artifact_id"],
        "output_sha256": manifest["output"]["sha256"],
        "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
        "verdict": verdict,
        "reviewer": "product-owner",
        "reviewed_at": "2026-07-31T12:00:00+09:00",
        "reviewed_full_video": True,
        "summary": "exact artifactを全編確認した。",
        "review_dimensions": results,
        "repair_instructions": instructions,
    }


def test_accept_receipt_binds_exact_artifact_and_keeps_external_gates_closed(
    tmp_path: Path,
) -> None:
    artifact, manifest = _build_artifact(tmp_path)
    decision_path = tmp_path / "decision.json"
    output_path = tmp_path / "receipt.json"
    _write_json(decision_path, _decision(manifest))
    manifest_before = (artifact / "run_manifest.json").read_bytes()

    result = record_evidence_linked_comparison_decision(
        artifact_dir=artifact,
        decision_path=decision_path,
        output_path=output_path,
    )

    receipt = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["written"] is True
    assert result["state"] == "accepted_internal_editorial_review"
    assert receipt["review_context"]["output_sha256"] == manifest["output"]["sha256"]
    assert receipt["human_review_pending"] is False
    assert receipt["acceptance_granted"] is True
    assert receipt["successor_review_required"] is False
    assert receipt["external_gates"] == {
        "rights_approval": "not_granted",
        "production_acceptance": False,
        "thumbnail_acceptance": False,
        "publishing_acceptance": False,
        "public_use": False,
        "monetized_use": False,
        "upload_authorized": False,
    }
    assert (artifact / "run_manifest.json").read_bytes() == manifest_before


def test_bounded_repair_requires_explicit_instructions(tmp_path: Path) -> None:
    artifact, manifest = _build_artifact(tmp_path)
    decision = _decision(manifest, verdict="bounded_repair")
    decision["repair_instructions"] = []
    decision_path = tmp_path / "decision.json"
    _write_json(decision_path, decision)

    with pytest.raises(
        EvidenceLinkedComparisonDecisionError,
        match="bounded_repair requires",
    ):
        record_evidence_linked_comparison_decision(
            artifact_dir=artifact,
            decision_path=decision_path,
            output_path=tmp_path / "receipt.json",
        )

    assert not (tmp_path / "receipt.json").exists()


def test_rejects_decision_for_different_video_bytes(tmp_path: Path) -> None:
    artifact, manifest = _build_artifact(tmp_path)
    decision = _decision(manifest)
    decision["output_sha256"] = "0" * 64
    decision_path = tmp_path / "decision.json"
    _write_json(decision_path, decision)

    with pytest.raises(
        EvidenceLinkedComparisonDecisionError,
        match="output_sha256 mismatch",
    ):
        record_evidence_linked_comparison_decision(
            artifact_dir=artifact,
            decision_path=decision_path,
            output_path=tmp_path / "receipt.json",
        )


def test_existing_receipt_is_never_overwritten(tmp_path: Path) -> None:
    artifact, manifest = _build_artifact(tmp_path)
    decision_path = tmp_path / "decision.json"
    output_path = tmp_path / "receipt.json"
    _write_json(decision_path, _decision(manifest))
    output_path.write_text("retained receipt\n", encoding="utf-8")

    with pytest.raises(
        EvidenceLinkedComparisonDecisionError,
        match="decision receipt already exists",
    ):
        record_evidence_linked_comparison_decision(
            artifact_dir=artifact,
            decision_path=decision_path,
            output_path=output_path,
        )

    assert output_path.read_text(encoding="utf-8") == "retained receipt\n"


def test_cli_dry_run_validates_without_writing(tmp_path: Path, capsys) -> None:
    artifact, manifest = _build_artifact(tmp_path)
    decision_path = tmp_path / "decision.json"
    output_path = tmp_path / "receipt.json"
    _write_json(decision_path, _decision(manifest, verdict="reject"))

    exit_code = main(
        [
            "record-evidence-linked-comparison-decision",
            "--artifact-dir",
            str(artifact),
            "--decision",
            str(decision_path),
            "--output",
            str(output_path),
            "--dry-run",
            "--format",
            "json",
        ]
    )

    result = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert result["verdict"] == "reject"
    assert result["written"] is False
    assert not output_path.exists()
