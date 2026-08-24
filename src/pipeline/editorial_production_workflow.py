"""Connect calibrated editorial decisions to the production review workflow.

This module emits a deterministic tracked receipt.  It does not render media,
mutate FrontierBoard, grant production authority, or record a human verdict.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "clippipegen.editorial_production_workflow.v1"
REQUIREMENT_ID = "CLIP-PRODUCTION-WORKFLOW-CONNECTION-20260825-001"


class EditorialProductionWorkflowError(ValueError):
    """Raised when calibrated inputs cannot safely enter the workflow."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EditorialProductionWorkflowError(f"input_missing:{path}") from exc
    if not isinstance(value, dict):
        raise EditorialProductionWorkflowError(f"input_not_object:{path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _validate_mixed(mixed: dict[str, Any]) -> None:
    if mixed.get("schema_version") != "clippipegen.editorial_calibration.v1":
        raise EditorialProductionWorkflowError("mixed_schema_mismatch")
    if mixed.get("status") != "COMPLETE":
        raise EditorialProductionWorkflowError("mixed_calibration_incomplete")
    summary = mixed.get("decision_summary") or {}
    expected = {
        "meaningful_units": 15,
        "KEEP": 7,
        "DROP": 1,
        "HOLD_REUSABLE": 7,
    }
    if any(summary.get(key) != value for key, value in expected.items()):
        raise EditorialProductionWorkflowError("mixed_decision_summary_mismatch")
    questions = mixed.get("question_granularity_audit") or {}
    if questions.get("eliminated_item_questions") != 15:
        raise EditorialProductionWorkflowError("mixed_item_questions_not_compressed")
    if questions.get("genuinely_requires_human_authority"):
        raise EditorialProductionWorkflowError("mixed_item_human_authority_remaining")
    if questions.get("choice_created") is not False:
        raise EditorialProductionWorkflowError("mixed_choice_boundary_missing")
    production = mixed.get("production_scale_entry_conditions") or {}
    if production.get("overall") != "PASS":
        raise EditorialProductionWorkflowError("mixed_production_scale_not_pass")


def _validate_acceptance(
    mixed: dict[str, Any], acceptance: dict[str, Any], acceptance_sha256: str
) -> None:
    basis = mixed.get("basis") or {}
    if acceptance_sha256 != basis.get("human_acceptance_receipt_sha256"):
        raise EditorialProductionWorkflowError("accepted_authority_sha_mismatch")
    if acceptance.get("artifact_id") != basis.get("artifact_id"):
        raise EditorialProductionWorkflowError("accepted_authority_identity_mismatch")
    if acceptance.get("acceptance_granted") is not True:
        raise EditorialProductionWorkflowError("accepted_authority_not_granted")
    if acceptance.get("human_review_pending") is not False:
        raise EditorialProductionWorkflowError("accepted_authority_still_pending")
    context = acceptance.get("review_context") or {}
    if context.get("scope") != basis.get("human_acceptance_scope"):
        raise EditorialProductionWorkflowError("accepted_authority_scope_mismatch")
    if context.get("media_sha256") != basis.get("output_sha256"):
        raise EditorialProductionWorkflowError("accepted_authority_media_mismatch")
    closed = acceptance.get("closed_gates") or {}
    for gate in (
        "rights_approval",
        "production_acceptance",
        "publishing_acceptance",
        "upload_attempted",
    ):
        if closed.get(gate) is not False:
            raise EditorialProductionWorkflowError(f"accepted_authority_gate_open:{gate}")


def _validate_whole(mixed: dict[str, Any], whole: dict[str, Any]) -> None:
    if whole.get("schema_version") != "clippipegen.whole_content_review.v1":
        raise EditorialProductionWorkflowError("whole_review_schema_mismatch")
    if whole.get("status") != "READY_FOR_ONE_WHOLE_CANDIDATE_JUDGMENT":
        raise EditorialProductionWorkflowError("whole_review_not_ready")
    authority = whole.get("human_authority_required") or {}
    outcomes = authority.get("allowed_outcomes") or []
    if authority.get("count") != 1 or [item.get("id") for item in outcomes] != [
        "accept_whole_candidate",
        "bounded_revision",
    ]:
        raise EditorialProductionWorkflowError("whole_review_not_single_bounded_gate")
    if authority.get("not_issued_as_choice_in_this_mission") is not True:
        raise EditorialProductionWorkflowError("whole_review_choice_boundary_missing")
    relation = whole.get("production_scale_relation") or {}
    if relation.get("mixed_calibration_identity") != mixed.get("case_identity"):
        raise EditorialProductionWorkflowError("whole_review_calibration_mismatch")
    if relation.get("mixed_calibration_result") != "PASS":
        raise EditorialProductionWorkflowError("whole_review_calibration_not_pass")
    if whole.get("media_created_or_modified") or whole.get("frontierboard_mutated"):
        raise EditorialProductionWorkflowError("whole_review_mutation_boundary_broken")


def build_editorial_production_workflow(
    *,
    mixed_path: Path,
    acceptance_path: Path,
    whole_review_path: Path,
    output_path: Path,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Validate the three authorities and emit one production-workflow receipt."""

    base = (base_dir or Path.cwd()).resolve()
    mixed = _load_json(mixed_path)
    acceptance = _load_json(acceptance_path)
    whole = _load_json(whole_review_path)
    acceptance_sha256 = _sha256(acceptance_path)
    _validate_mixed(mixed)
    _validate_acceptance(mixed, acceptance, acceptance_sha256)
    _validate_whole(mixed, whole)

    summary = mixed["decision_summary"]
    authority = whole["human_authority_required"]
    packet = {
        "schema_version": SCHEMA_VERSION,
        "requirement_id": REQUIREMENT_ID,
        "artifact_id": "clip-editorial-production-workflow-connection-v1-001",
        "status": "CONNECTED_READY_FOR_SERIALIZED_HUMAN_REVIEW",
        "material_change": (
            "The production review workflow now consumes calibrated decision "
            "authority instead of regenerating fifteen item-level questions."
        ),
        "inputs": {
            "mixed_calibration": {
                "path": _display(mixed_path, base),
                "sha256": _sha256(mixed_path),
                "case_identity": mixed["case_identity"],
            },
            "accepted_authority": {
                "path": _display(acceptance_path, base),
                "sha256": acceptance_sha256,
                "artifact_id": acceptance["artifact_id"],
                "scope": acceptance["review_context"]["scope"],
            },
            "whole_content_review": {
                "path": _display(whole_review_path, base),
                "sha256": _sha256(whole_review_path),
                "review_identity": whole["review_identity"],
                "media_sha256": whole["media"]["sha256"],
            },
        },
        "ready_conditions": [
            {"condition": "mixed_keep_drop_hold_calibration", "result": "PASS"},
            {"condition": "accepted_exact_authority_hash_and_scope", "result": "PASS"},
            {"condition": "fifteen_item_questions_eliminated", "result": "PASS"},
            {"condition": "single_whole_or_bounded_revision_gate", "result": "PASS"},
            {
                "condition": "workflow_builder_performed_no_media_or_frontierboard_mutation",
                "result": "PASS",
            },
        ],
        "autonomous_resolution": {
            "precedence": ["Evidence", "validated Rule", "accepted authority"],
            "decision_units_resolved": summary["meaningful_units"],
            "decision_counts": {
                "KEEP": summary["KEEP"],
                "DROP": summary["DROP"],
                "HOLD_REUSABLE": summary["HOLD_REUSABLE"],
            },
            "item_level_questions_reemitted": 0,
            "policy": "ask only when all three authorities fail and creative authority changes the result",
        },
        "human_judgment": {
            "count": 1,
            "artifact_id": whole["artifact_id"],
            "media": whole["media"],
            "question": authority["question"],
            "allowed_outcomes": authority["allowed_outcomes"],
            "item_level_fallback_allowed": False,
        },
        "choice_serialization": {
            "tracked_existing_choice": "Project13_ChoiceSet7_revision1",
            "relationship": "independent_gui_direction_not_335s_content_judgment",
            "new_choice_created": False,
            "prompt_emission": "WAIT_UNTIL_NO_COMPETING_CURRENT_CHOICE",
        },
        "workflow_connection": {
            "entry": "Episode Review Workflow / Cut Review to Video Review Player",
            "input_contract": "calibrated trace plus accepted exact authority",
            "output_contract": "one whole-candidate accept or exact-range bounded revision judgment",
            "on_accept": "record exact-media internal content/editorial acceptance only",
            "on_bounded_revision": "reopen only named ranges and causally affected dimensions",
        },
        "closed_boundaries": {
            "next_video_started": False,
            "new_media_generated": False,
            "production_acceptance": False,
            "rights_approval": False,
            "publication_acceptance": False,
            "frontierboard_mutated": False,
            "remote_seal": "NOT_PERFORMED",
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return packet
