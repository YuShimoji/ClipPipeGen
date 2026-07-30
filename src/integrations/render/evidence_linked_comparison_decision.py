"""Fail-closed human decision binding for an S2 comparison artifact."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from .evidence_linked_comparison import (
    EvidenceLinkedComparisonError,
    validate_run_manifest,
)

DECISION_INPUT_SCHEMA_VERSION = (
    "clippipegen.s2.evidence_linked_comparison_decision_input.v1"
)
DECISION_RECEIPT_SCHEMA_VERSION = (
    "clippipegen.s2.evidence_linked_comparison_decision_receipt.v1"
)
REVIEW_CONTEXT_ID = "s2_evidence_linked_comparison_internal_full_view_v1"
REVIEW_DIMENSIONS = (
    "concurrent_panels_speed_comparison",
    "quote_evidence_clarity",
    "foreground_audio_transitions",
    "thesis_coherence",
)
DIMENSION_RESULTS = {"pass", "needs_repair", "fail"}
VERDICTS = {"accept", "bounded_repair", "reject"}


class EvidenceLinkedComparisonDecisionError(ValueError):
    """Raised when a human decision cannot be bound to the exact S2 artifact."""


def record_evidence_linked_comparison_decision(
    *,
    artifact_dir: Path,
    decision_path: Path,
    output_path: Path,
    dry_run: bool = False,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Validate and record one explicit human verdict without opening external gates."""

    base = (base_dir or Path.cwd()).resolve()
    artifact = _resolve(artifact_dir, base)
    decision_file = _resolve(decision_path, base)
    output = _resolve(output_path, base)

    if not artifact.is_dir():
        raise EvidenceLinkedComparisonDecisionError(
            f"artifact directory does not exist: {artifact}"
        )
    if not decision_file.is_file():
        raise EvidenceLinkedComparisonDecisionError(
            f"decision file does not exist: {decision_file}"
        )
    if output.suffix.lower() != ".json":
        raise EvidenceLinkedComparisonDecisionError("output path must end in .json")
    if output == artifact or artifact in output.parents:
        raise EvidenceLinkedComparisonDecisionError(
            "decision receipt must stay outside the closed artifact package"
        )
    if output.exists():
        raise EvidenceLinkedComparisonDecisionError(
            f"decision receipt already exists: {output}"
        )

    try:
        validate_run_manifest(artifact)
    except (OSError, EvidenceLinkedComparisonError) as exc:
        raise EvidenceLinkedComparisonDecisionError(
            f"artifact manifest validation failed: {exc}"
        ) from exc

    manifest = _read_json(artifact / "run_manifest.json", "run manifest")
    decision = _read_json(decision_file, "decision input")
    _validate_decision(decision, manifest)

    receipt = _build_receipt(decision, manifest)
    if not dry_run:
        _write_json_atomic(output, receipt)

    return {
        "state": receipt["state"],
        "artifact_id": receipt["artifact_id"],
        "verdict": receipt["verdict"],
        "human_review_pending": receipt["human_review_pending"],
        "acceptance_granted": receipt["acceptance_granted"],
        "successor_review_required": receipt["successor_review_required"],
        "decision_receipt_path": str(output),
        "written": not dry_run,
        "receipt": receipt,
    }


def _validate_decision(
    decision: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    required_keys = {
        "schema_version",
        "artifact_id",
        "output_sha256",
        "manifest_self_sha256",
        "verdict",
        "reviewer",
        "reviewed_at",
        "reviewed_full_video",
        "summary",
        "review_dimensions",
        "repair_instructions",
    }
    if set(decision) != required_keys:
        missing = sorted(required_keys - set(decision))
        extra = sorted(set(decision) - required_keys)
        raise EvidenceLinkedComparisonDecisionError(
            f"decision keys mismatch; missing={missing}, extra={extra}"
        )
    if decision["schema_version"] != DECISION_INPUT_SCHEMA_VERSION:
        raise EvidenceLinkedComparisonDecisionError("decision schema mismatch")
    if decision["artifact_id"] != manifest["artifact_id"]:
        raise EvidenceLinkedComparisonDecisionError("artifact_id mismatch")
    if decision["output_sha256"] != manifest["output"]["sha256"]:
        raise EvidenceLinkedComparisonDecisionError("output_sha256 mismatch")
    if (
        decision["manifest_self_sha256"]
        != manifest["manifest_self_integrity"]["sha256"]
    ):
        raise EvidenceLinkedComparisonDecisionError(
            "manifest_self_sha256 mismatch"
        )

    verdict = decision["verdict"]
    if verdict not in VERDICTS:
        raise EvidenceLinkedComparisonDecisionError(
            f"verdict must be one of {sorted(VERDICTS)}"
        )
    _require_nonempty_string(decision["reviewer"], "reviewer")
    _require_nonempty_string(decision["summary"], "summary")
    _validate_reviewed_at(decision["reviewed_at"])
    if decision["reviewed_full_video"] is not True:
        raise EvidenceLinkedComparisonDecisionError(
            "reviewed_full_video must be true"
        )

    dimensions = decision["review_dimensions"]
    if not isinstance(dimensions, dict) or set(dimensions) != set(
        REVIEW_DIMENSIONS
    ):
        raise EvidenceLinkedComparisonDecisionError(
            "review_dimensions must contain the exact S2 review dimension set"
        )
    invalid_results = {
        key: value
        for key, value in dimensions.items()
        if value not in DIMENSION_RESULTS
    }
    if invalid_results:
        raise EvidenceLinkedComparisonDecisionError(
            f"invalid review dimension results: {invalid_results}"
        )

    instructions = decision["repair_instructions"]
    if not isinstance(instructions, list) or any(
        not isinstance(item, str) or not item.strip() for item in instructions
    ):
        raise EvidenceLinkedComparisonDecisionError(
            "repair_instructions must be a list of non-empty strings"
        )
    results = set(dimensions.values())
    if verdict == "accept" and (results != {"pass"} or instructions):
        raise EvidenceLinkedComparisonDecisionError(
            "accept requires every review dimension to pass and no repair instructions"
        )
    if verdict == "bounded_repair" and (
        "needs_repair" not in results or "fail" in results or not instructions
    ):
        raise EvidenceLinkedComparisonDecisionError(
            "bounded_repair requires needs_repair, no fail result, and repair instructions"
        )
    if verdict == "reject" and ("fail" not in results or instructions):
        raise EvidenceLinkedComparisonDecisionError(
            "reject requires a fail result and no repair instructions"
        )


def _build_receipt(
    decision: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    verdict = decision["verdict"]
    state_by_verdict = {
        "accept": "accepted_internal_editorial_review",
        "bounded_repair": "bounded_repair_requested",
        "reject": "rejected_internal_editorial_review",
    }
    receipt: dict[str, Any] = {
        "schema_version": DECISION_RECEIPT_SCHEMA_VERSION,
        "artifact_id": manifest["artifact_id"],
        "state": state_by_verdict[verdict],
        "decision_source": "human_provided_json",
        "decision_authority": "human",
        "verdict": verdict,
        "reviewer": decision["reviewer"].strip(),
        "reviewed_at": decision["reviewed_at"],
        "reviewed_full_video": True,
        "summary": decision["summary"].strip(),
        "review_context": {
            "context_id": REVIEW_CONTEXT_ID,
            "scope": "internal_full_view_editorial_review",
            "artifact_id": manifest["artifact_id"],
            "output_sha256": manifest["output"]["sha256"],
            "output_byte_size": manifest["output"]["byte_size"],
            "output_duration_seconds": manifest["output"]["duration_seconds"],
            "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
            "payload_tree_sha256": manifest["payload_tree_digest"]["sha256"],
            "review_dimensions": {
                key: decision["review_dimensions"][key]
                for key in REVIEW_DIMENSIONS
            },
        },
        "repair_instructions": [
            item.strip() for item in decision["repair_instructions"]
        ],
        "source_decision_sha256": _canonical_hash(decision),
        "human_review_pending": False,
        "acceptance_granted": verdict == "accept",
        "bounded_repair_requested": verdict == "bounded_repair",
        "rejected": verdict == "reject",
        "successor_review_required": verdict == "bounded_repair",
        "external_gates": {
            "rights_approval": "not_granted",
            "production_acceptance": False,
            "thumbnail_acceptance": False,
            "publishing_acceptance": False,
            "public_use": False,
            "monetized_use": False,
            "upload_authorized": False,
        },
    }
    receipt["receipt_self_integrity"] = {
        "algorithm": "sha256",
        "scope": "canonical_json_without_receipt_self_integrity",
        "sha256": _canonical_hash(receipt),
    }
    return receipt


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceLinkedComparisonDecisionError(
            f"invalid {label}: {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise EvidenceLinkedComparisonDecisionError(
            f"{label} must be a JSON object"
        )
    return value


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(serialized)
            temporary_name = handle.name
        os.link(temporary_name, path)
    finally:
        if temporary_name:
            temporary = Path(temporary_name)
            if temporary.exists():
                temporary.unlink()


def _canonical_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_reviewed_at(value: Any) -> None:
    _require_nonempty_string(value, "reviewed_at")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceLinkedComparisonDecisionError(
            "reviewed_at must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EvidenceLinkedComparisonDecisionError(
            "reviewed_at must include a timezone"
        )


def _require_nonempty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceLinkedComparisonDecisionError(
            f"{label} must be a non-empty string"
        )


def _resolve(path: Path, base_dir: Path) -> Path:
    return (path if path.is_absolute() else base_dir / path).resolve()
