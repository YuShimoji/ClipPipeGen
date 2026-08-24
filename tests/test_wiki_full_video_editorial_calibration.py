from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_wiki_full_video_editorial_calibration.py"
CALIBRATION = (
    REPO_ROOT
    / "docs"
    / "output_layer"
    / "clip_full_video_editorial_calibration_v1.json"
)
SPEC = importlib.util.spec_from_file_location("full_video_calibration", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_full_video_calibration_is_contiguous_and_question_bounded() -> None:
    calibration = MODULE.load_json(CALIBRATION)
    result = MODULE.validate_calibration(calibration)

    assert result["status"] == "PASS"
    assert result["decisionUnitCount"] == 8
    assert result["decisionCounts"] == {"KEEP": 8, "DROP": 0, "HOLD": 0}
    assert result["eliminatedQuestionCount"] == 11
    assert result["remainingHumanQuestionCount"] == 1
    assert result["productionScale"] == "PARTIAL"


def test_full_video_calibration_keeps_clip_details_out_of_shared_grammar() -> None:
    calibration = MODULE.load_json(CALIBRATION)
    shared = calibration["cross_project_grammar"]

    assert shared["shared_sequence"] == [
        "Segment",
        "Decision",
        "Reason",
        "Evidence",
        "Rule",
        "Override",
        "Result",
    ]
    shared_text = " ".join(shared["shared_fields"])
    assert "event_" not in shared_text
    assert "caption" not in shared_text.lower()
    assert shared["other_projects_modified"] is False


def test_current_exact_package_mismatch_is_recorded_not_hidden() -> None:
    calibration = MODULE.load_json(CALIBRATION)
    observation = calibration["trace_contract_observation"]

    assert observation["classification"] == "LOCAL_REPAIR"
    assert observation["evidence"]["timeline_caption_reference_count"] == 97
    assert observation["evidence"]["caption_readback_item_count"] == 96
    assert observation["evidence"]["dangling_caption_ids"] == ["caption_0097"]
    assert calibration["production_scale_entry_conditions"]["overall"] == "PARTIAL"
