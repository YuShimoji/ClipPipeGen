from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.pipeline.editorial_production_workflow import (
    EditorialProductionWorkflowError,
    build_editorial_production_workflow,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MIXED = REPO_ROOT / "docs/output_layer/clip_mixed_editorial_calibration_v1.json"
ACCEPTANCE = REPO_ROOT / "docs/output_layer/out13_human_acceptance_receipt.json"
WHOLE = REPO_ROOT / "docs/output_layer/clip_335s_whole_content_review_v1.json"
ADOPTION = REPO_ROOT / "docs/output_layer/clip_335s_current_basis_adoption_v1.json"


def test_workflow_consumes_current_basis_adoption_without_new_gate(tmp_path: Path) -> None:
    output = tmp_path / "workflow.json"
    packet = build_editorial_production_workflow(
        mixed_path=MIXED,
        acceptance_path=ACCEPTANCE,
        whole_review_path=WHOLE,
        current_basis_adoption_path=ADOPTION,
        output_path=output,
        base_dir=REPO_ROOT,
    )

    assert packet["status"] == "CONNECTED_CURRENT_BASIS_ADOPTED"
    assert packet["autonomous_resolution"]["decision_counts"] == {
        "KEEP": 7,
        "DROP": 1,
        "HOLD_REUSABLE": 7,
    }
    assert packet["autonomous_resolution"]["item_level_questions_reemitted"] == 0
    assert packet["human_judgment"]["count"] == 1
    assert packet["human_judgment"]["remaining_count"] == 0
    assert packet["human_judgment"]["selected_outcome"] == "accept_whole_candidate"
    assert [item["id"] for item in packet["human_judgment"]["allowed_outcomes"]] == [
        "accept_whole_candidate",
        "bounded_revision",
    ]
    assert packet["choice_serialization"]["new_choice_created"] is False
    assert packet["choice_serialization"]["status"] == "RESOLVED_SELECTED"
    assert packet["choice_serialization"]["prompt_emission"] == "NONE_ALREADY_RESOLVED"
    assert packet["closed_boundaries"]["production_acceptance"] is False
    assert json.loads(output.read_text(encoding="utf-8")) == packet


def test_workflow_fails_closed_if_item_question_returns(tmp_path: Path) -> None:
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    mixed["question_granularity_audit"]["genuinely_requires_human_authority"] = [
        {"unit_id": "omit_001"}
    ]
    changed = tmp_path / "mixed.json"
    changed.write_text(json.dumps(mixed), encoding="utf-8")

    with pytest.raises(
        EditorialProductionWorkflowError,
        match="mixed_item_human_authority_remaining",
    ):
        build_editorial_production_workflow(
            mixed_path=changed,
            acceptance_path=ACCEPTANCE,
            whole_review_path=WHOLE,
            current_basis_adoption_path=ADOPTION,
            output_path=tmp_path / "workflow.json",
            base_dir=REPO_ROOT,
        )


def test_workflow_keeps_choice_7_separate(tmp_path: Path) -> None:
    packet = build_editorial_production_workflow(
        mixed_path=MIXED,
        acceptance_path=ACCEPTANCE,
        whole_review_path=WHOLE,
        current_basis_adoption_path=ADOPTION,
        output_path=tmp_path / "workflow.json",
        base_dir=REPO_ROOT,
    )

    serialization = packet["choice_serialization"]
    assert serialization["tracked_existing_choice"] == "Project13_ChoiceSet7_revision2"
    assert serialization["relationship"] == (
        "independent_gui_direction_not_335s_content_judgment"
    )
    assert serialization["prompt_emission"] == "NONE_ALREADY_RESOLVED"


def test_workflow_rejects_adoption_for_another_media_sha(tmp_path: Path) -> None:
    adoption = json.loads(ADOPTION.read_text(encoding="utf-8"))
    adoption["artifact"]["sha256"] = "0" * 64
    changed = tmp_path / "adoption.json"
    changed.write_text(json.dumps(adoption, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(
        EditorialProductionWorkflowError,
        match="current_basis_adoption_artifact_mismatch",
    ):
        build_editorial_production_workflow(
            mixed_path=MIXED,
            acceptance_path=ACCEPTANCE,
            whole_review_path=WHOLE,
            current_basis_adoption_path=changed,
            output_path=tmp_path / "workflow.json",
            base_dir=REPO_ROOT,
        )


def test_workflow_rejects_adoption_that_opens_production(tmp_path: Path) -> None:
    adoption = json.loads(ADOPTION.read_text(encoding="utf-8"))
    adoption["not_granted"].remove("production_acceptance")
    changed = tmp_path / "adoption.json"
    changed.write_text(json.dumps(adoption, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(
        EditorialProductionWorkflowError,
        match="current_basis_adoption_boundary_missing",
    ):
        build_editorial_production_workflow(
            mixed_path=MIXED,
            acceptance_path=ACCEPTANCE,
            whole_review_path=WHOLE,
            current_basis_adoption_path=changed,
            output_path=tmp_path / "workflow.json",
            base_dir=REPO_ROOT,
        )
