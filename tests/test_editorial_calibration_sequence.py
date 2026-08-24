from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_editorial_calibration_sequence.py"
MIXED = REPO_ROOT / "docs" / "output_layer" / "clip_mixed_editorial_calibration_v1.json"
WHOLE = REPO_ROOT / "docs" / "output_layer" / "clip_335s_whole_content_review_v1.json"
SPEC = importlib.util.spec_from_file_location("editorial_calibration_sequence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_mixed_calibration_has_real_keep_drop_and_hold() -> None:
    mixed = MODULE.load_json(MIXED)
    result = MODULE.validate_mixed_document(mixed)

    assert result["status"] == "PASS"
    assert result["decisionCounts"] == {
        "KEEP": 7,
        "DROP": 1,
        "HOLD_REUSABLE": 7,
    }
    assert result["eliminatedItemQuestions"] == 15
    assert result["productionScale"] == "PASS"


def test_whole_candidate_review_is_one_human_judgment_without_choice() -> None:
    mixed = MODULE.load_json(MIXED)
    whole = MODULE.load_json(WHOLE)
    result = MODULE.validate_whole_review_document(whole, mixed)

    assert result["status"] == "PASS"
    assert result["remainingHumanJudgments"] == 1
    assert result["choiceCreated"] is False


def test_shared_grammar_does_not_require_clip_provider_fields() -> None:
    mixed = MODULE.load_json(MIXED)
    shared = mixed["cross_project_grammar"]

    assert shared["shared_sequence"] == [
        "Segment",
        "Decision",
        "Reason",
        "Evidence",
        "Rule",
        "Override",
        "Result",
    ]
    assert shared["other_projects_modified"] is False
