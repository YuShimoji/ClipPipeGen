"""Connect calibrated editorial decisions to the production review workflow.

This module emits a deterministic tracked receipt.  It does not render media,
mutate FrontierBoard, or grant production authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "clippipegen.editorial_production_workflow.v1"
REQUIREMENT_ID = "CLIP-PRODUCTION-WORKFLOW-CONNECTION-20260825-001"
CURRENT_BASIS_STATEMENT = "修正後の終端artifactを現行基準として採用する判断でよい"
CURRENT_BASIS_MISSION_ID = "VIDEO-CLIP-CURRENT-REVIEW-CLOSE-20260830-001"
CURRENT_BASIS_SCOPE_SHA256 = (
    "2e57cce2e4bd2d10bc63a370cddbea38559dda05ec0952ba3620b6fca9c19ca5"
)
CURRENT_BASIS_BOARD_CONTEXT_SHA256 = (
    "05eb79593cba2951aa49173e07ece5a3597c7e6d7682ad9546328f1702fd7968"
)


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


def _validate_current_basis_adoption(
    whole: dict[str, Any], adoption: dict[str, Any]
) -> None:
    if adoption.get("schema_version") != "clippipegen.current_basis_adoption.v1":
        raise EditorialProductionWorkflowError("current_basis_adoption_schema_mismatch")
    if adoption.get("receipt_id") != "clip-335s-current-basis-adoption-v1-001":
        raise EditorialProductionWorkflowError("current_basis_adoption_identity_mismatch")
    mission = adoption.get("mission") or {}
    if (
        mission.get("mission_id") != CURRENT_BASIS_MISSION_ID
        or mission.get("scope_sha256") != CURRENT_BASIS_SCOPE_SHA256
        or mission.get("authority_envelope_id")
        != "video.clip.current-review.specialist.v1"
        or mission.get("parent_authority_envelope_id")
        != "video.clip.current-review.project.v1"
    ):
        raise EditorialProductionWorkflowError("current_basis_adoption_mission_mismatch")
    authority = adoption.get("authority") or {}
    if authority.get("kind") != "explicit_user_statement":
        raise EditorialProductionWorkflowError("current_basis_adoption_authority_missing")
    if authority.get("source_task_id") != "01a0202f-adb4-76c2-980d-f63509a5fa17":
        raise EditorialProductionWorkflowError("current_basis_adoption_source_mismatch")
    if authority.get("statement") != CURRENT_BASIS_STATEMENT:
        raise EditorialProductionWorkflowError("current_basis_adoption_statement_mismatch")
    if authority.get("selected_outcome") != "accept_whole_candidate":
        raise EditorialProductionWorkflowError("current_basis_adoption_outcome_mismatch")
    if authority.get("scope") != "exact_artifact_internal_content_editorial_current_basis_only":
        raise EditorialProductionWorkflowError("current_basis_adoption_scope_mismatch")

    artifact = adoption.get("artifact") or {}
    expected_artifact = {
        "artifact_id": whole.get("artifact_id"),
        "media_path": (
            "episodes/integrated_checklist_reverse_test_20260811/artifacts/"
            "cpg-integrated-checklist-reverse-test-v1/successors/"
            "cpg-wiki-selected-opening-current-basis-v1/package/final_video.mp4"
        ),
        "sha256": (whole.get("media") or {}).get("sha256"),
        "byte_size": (whole.get("media") or {}).get("byte_size"),
        "editorial_duration_seconds": (whole.get("media") or {}).get(
            "editorial_duration_seconds"
        ),
        "container_duration_seconds": (whole.get("media") or {}).get(
            "container_duration_seconds"
        ),
        "source_range_seconds": (whole.get("media") or {}).get(
            "source_range_seconds"
        ),
    }
    if any(artifact.get(key) != value for key, value in expected_artifact.items()):
        raise EditorialProductionWorkflowError("current_basis_adoption_artifact_mismatch")

    board = adoption.get("board_readback") or {}
    if (
        board.get("status") != "PASS"
        or board.get("context_sha256") != CURRENT_BASIS_BOARD_CONTEXT_SHA256
        or board.get("project_id") != 13
        or board.get("choice_set_id") != 7
        or board.get("choice_set_revision") != 2
        or board.get("option_id") != 18
        or board.get("selection_id") != 5
        or board.get("awaiting_user_count") != 0
        or board.get("production_authority") is not False
        or board.get("scheduler_authority") is not False
        or board.get("read_only") is not True
    ):
        raise EditorialProductionWorkflowError("current_basis_adoption_board_mismatch")

    disposition = adoption.get("disposition") or {}
    if (
        disposition.get("status")
        != "ACCEPTED_CURRENT_BASIS_INTERNAL_CONTENT_EDITORIAL"
        or disposition.get("whole_content_review_gate")
        != "CLOSED_ACCEPT_WHOLE_CANDIDATE"
        or disposition.get("remaining_human_judgment_count") != 0
        or disposition.get("item_level_questions_reemitted") != 0
        or disposition.get("opening_or_endpoint_question_reopened") is not False
        or disposition.get("new_choice_created") is not False
        or disposition.get("media_created_or_modified") is not False
    ):
        raise EditorialProductionWorkflowError("current_basis_adoption_disposition_mismatch")

    required_closed = {
        "general_creative_rule_adoption",
        "another_artifact_or_video_authority",
        "rights_approval",
        "production_acceptance",
        "delivery_acceptance",
        "publication_acceptance",
        "monetization",
        "upload",
        "frontierboard_mutation",
    }
    if not required_closed.issubset(set(adoption.get("not_granted") or [])):
        raise EditorialProductionWorkflowError("current_basis_adoption_boundary_missing")


def build_editorial_production_workflow(
    *,
    mixed_path: Path,
    acceptance_path: Path,
    whole_review_path: Path,
    current_basis_adoption_path: Path,
    output_path: Path,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Validate calibrated inputs and exact current-basis adoption."""

    base = (base_dir or Path.cwd()).resolve()
    mixed = _load_json(mixed_path)
    acceptance = _load_json(acceptance_path)
    whole = _load_json(whole_review_path)
    adoption = _load_json(current_basis_adoption_path)
    acceptance_sha256 = _sha256(acceptance_path)
    _validate_mixed(mixed)
    _validate_acceptance(mixed, acceptance, acceptance_sha256)
    _validate_whole(mixed, whole)
    _validate_current_basis_adoption(whole, adoption)

    summary = mixed["decision_summary"]
    authority = whole["human_authority_required"]
    packet = {
        "schema_version": SCHEMA_VERSION,
        "requirement_id": REQUIREMENT_ID,
        "artifact_id": "clip-editorial-production-workflow-connection-v1-001",
        "status": "CONNECTED_CURRENT_BASIS_ADOPTED",
        "material_change": (
            "The production review workflow consumes the exact user current-basis "
            "adoption without regenerating fifteen item-level questions."
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
            "current_basis_adoption": {
                "path": _display(current_basis_adoption_path, base),
                "sha256": _sha256(current_basis_adoption_path),
                "receipt_id": adoption["receipt_id"],
                "selected_outcome": adoption["authority"]["selected_outcome"],
                "scope": adoption["authority"]["scope"],
            },
        },
        "ready_conditions": [
            {"condition": "mixed_keep_drop_hold_calibration", "result": "PASS"},
            {"condition": "accepted_exact_authority_hash_and_scope", "result": "PASS"},
            {"condition": "fifteen_item_questions_eliminated", "result": "PASS"},
            {"condition": "single_whole_or_bounded_revision_gate", "result": "PASS"},
            {"condition": "exact_current_basis_adoption_bound", "result": "PASS"},
            {"condition": "choice_7_resolved_and_awaiting_user_zero", "result": "PASS"},
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
            "count_meaning": "original_compressed_gate_count",
            "remaining_count": 0,
            "status": "RESOLVED_ACCEPT_WHOLE_CANDIDATE",
            "selected_outcome": adoption["authority"]["selected_outcome"],
            "artifact_id": whole["artifact_id"],
            "media": whole["media"],
            "original_question": authority["question"],
            "allowed_outcomes": authority["allowed_outcomes"],
            "item_level_fallback_allowed": False,
            "authority_receipt": {
                "path": _display(current_basis_adoption_path, base),
                "sha256": _sha256(current_basis_adoption_path),
            },
        },
        "choice_serialization": {
            "tracked_existing_choice": "Project13_ChoiceSet7_revision2",
            "option_id": 18,
            "selection_id": 5,
            "status": "RESOLVED_SELECTED",
            "relationship": "independent_gui_direction_not_335s_content_judgment",
            "new_choice_created": False,
            "prompt_emission": "NONE_ALREADY_RESOLVED",
        },
        "workflow_connection": {
            "entry": "Episode Review Workflow / Cut Review to Video Review Player",
            "input_contract": "calibrated trace plus accepted exact authority",
            "output_contract": "exact current-basis internal content/editorial adoption receipt",
            "on_accept": "consume the bound exact-media current-basis adoption",
            "on_bounded_revision": "reopen only named ranges and causally affected dimensions",
            "current_state": "CURRENT_BASIS_ADOPTED_NO_HUMAN_PROMPT_PENDING",
        },
        "closed_boundaries": {
            "next_video_started": False,
            "new_media_generated": False,
            "production_acceptance": False,
            "rights_approval": False,
            "delivery_acceptance": False,
            "publication_acceptance": False,
            "monetization": False,
            "upload_attempted": False,
            "frontierboard_mutated": False,
            "remote_seal": "NOT_PERFORMED",
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return packet
