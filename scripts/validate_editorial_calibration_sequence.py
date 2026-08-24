from __future__ import annotations

import argparse
import hashlib
import json
from itertools import pairwise
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MIXED = (
    REPO_ROOT / "docs" / "output_layer" / "clip_mixed_editorial_calibration_v1.json"
)
DEFAULT_WHOLE_REVIEW = (
    REPO_ROOT / "docs" / "output_layer" / "clip_335s_whole_content_review_v1.json"
)
DEFAULT_OUT13_PACKAGE = (
    REPO_ROOT
    / "episodes"
    / "out13_editorial_video_candidate_20260723"
    / "review"
    / "out13_editorial_video_candidate_v005"
)
DEFAULT_335_PACKAGE = (
    REPO_ROOT
    / "episodes"
    / "integrated_checklist_reverse_test_20260811"
    / "artifacts"
    / "cpg-integrated-checklist-reverse-test-v1"
    / "successors"
    / "cpg-wiki-selected-opening-current-basis-v1"
    / "package"
)


class CalibrationSequenceError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def close(left: float, right: float) -> bool:
    return abs(float(left) - float(right)) <= 0.001


def validate_mixed_document(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("schema_version") != "clippipegen.editorial_calibration.v1":
        raise CalibrationSequenceError("mixed_schema_mismatch")

    units = document["decision_units"]
    summary = document["decision_summary"]
    counts = {"KEEP": 0, "DROP": 0, "HOLD_REUSABLE": 0}
    ids: set[str] = set()
    for unit in units:
        unit_id = unit["unit_id"]
        if unit_id in ids:
            raise CalibrationSequenceError("mixed_unit_duplicate")
        ids.add(unit_id)
        decision = unit["decision"]
        if decision not in counts:
            raise CalibrationSequenceError("mixed_decision_invalid")
        counts[decision] += 1
        source_start, source_end = unit["source_range_seconds"]
        if source_end <= source_start:
            raise CalibrationSequenceError("mixed_source_range_invalid")
        if not unit["reason"] or not unit["evidence"]["observed"]:
            raise CalibrationSequenceError("mixed_evidence_missing")
        if not unit["evidence"]["inferred"] or not unit["resulting_edit"]:
            raise CalibrationSequenceError("mixed_trace_missing")
        if not unit["confidence"] or not unit["limitation"]:
            raise CalibrationSequenceError("mixed_uncertainty_missing")

    expected_ids = {f"cut_{index:03d}" for index in range(1, 8)} | {
        f"omit_{index:03d}" for index in range(1, 9)
    }
    if ids != expected_ids:
        raise CalibrationSequenceError("mixed_unit_identity_mismatch")
    if counts != {"KEEP": 7, "DROP": 1, "HOLD_REUSABLE": 7}:
        raise CalibrationSequenceError("mixed_decision_count_mismatch")
    if summary["meaningful_units"] != len(units):
        raise CalibrationSequenceError("mixed_summary_unit_count_mismatch")
    if any(summary[key] != value for key, value in counts.items()):
        raise CalibrationSequenceError("mixed_summary_decision_count_mismatch")

    states = {rule["state"] for rule in document["reusable_rules"]}
    if states - {"proposed", "validated", "human-approved"}:
        raise CalibrationSequenceError("mixed_rule_state_invalid")
    for rule in document["reusable_rules"]:
        if not rule["supporting_evidence"] or not rule["scope_boundary"]:
            raise CalibrationSequenceError("mixed_rule_support_missing")
        if not rule["plausible_counterexamples"]:
            raise CalibrationSequenceError("mixed_rule_counterexample_missing")

    questions = document["question_granularity_audit"]
    if questions["choice_created"]:
        raise CalibrationSequenceError("mixed_choice_created")
    if questions["genuinely_requires_human_authority"]:
        raise CalibrationSequenceError("mixed_item_question_not_eliminated")
    production = document["production_scale_entry_conditions"]
    if production["overall"] != "PASS":
        raise CalibrationSequenceError("mixed_production_result_not_pass")
    if any(condition["result"] != "PASS" for condition in production["conditions"]):
        raise CalibrationSequenceError("mixed_production_condition_not_pass")

    shared_text = json.dumps(document["cross_project_grammar"], ensure_ascii=False)
    for forbidden in ("event_", "seg_", "provider_json3", "cut_001"):
        if forbidden in shared_text:
            raise CalibrationSequenceError("mixed_project_detail_leaked_to_shared")

    return {
        "status": "PASS",
        "caseIdentity": document["case_identity"],
        "decisionCounts": counts,
        "decisionUnitCount": len(units),
        "eliminatedItemQuestions": questions["eliminated_item_questions"],
        "productionScale": production["overall"],
    }


def validate_whole_review_document(
    document: dict[str, Any], mixed_document: dict[str, Any]
) -> dict[str, Any]:
    if document.get("schema_version") != "clippipegen.whole_content_review.v1":
        raise CalibrationSequenceError("whole_review_schema_mismatch")
    if document["status"] != "READY_FOR_ONE_WHOLE_CANDIDATE_JUDGMENT":
        raise CalibrationSequenceError("whole_review_status_mismatch")
    authority = document["human_authority_required"]
    if authority["count"] != 1 or len(authority["allowed_outcomes"]) != 2:
        raise CalibrationSequenceError("whole_review_not_compressed")
    if not authority["not_issued_as_choice_in_this_mission"]:
        raise CalibrationSequenceError("whole_review_choice_boundary_missing")
    relation = document["production_scale_relation"]
    if relation["mixed_calibration_identity"] != mixed_document["case_identity"]:
        raise CalibrationSequenceError("whole_review_mixed_identity_mismatch")
    if relation["mixed_calibration_result"] != "PASS":
        raise CalibrationSequenceError("whole_review_mixed_result_mismatch")
    if document["media_created_or_modified"] or document["frontierboard_mutated"]:
        raise CalibrationSequenceError("whole_review_mutation_claim_invalid")
    return {
        "status": "PASS",
        "reviewIdentity": document["review_identity"],
        "remainingHumanJudgments": authority["count"],
        "choiceCreated": False,
    }


def validate_out13_package(document: dict[str, Any], package: Path) -> dict[str, Any]:
    required = {
        name: package / name
        for name in ("editorial_plan.json", "timeline_ir.json", "final_video.mp4")
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise CalibrationSequenceError(
            "out13_exact_package_missing:" + ",".join(sorted(missing))
        )
    basis = document["basis"]
    if sha256(required["editorial_plan.json"]) != basis["editorial_plan_sha256"]:
        raise CalibrationSequenceError("out13_plan_sha_mismatch")
    if sha256(required["timeline_ir.json"]) != basis["timeline_ir_sha256"]:
        raise CalibrationSequenceError("out13_timeline_sha_mismatch")
    if sha256(required["final_video.mp4"]) != basis["output_sha256"]:
        raise CalibrationSequenceError("out13_media_sha_mismatch")
    if required["final_video.mp4"].stat().st_size != basis["output_bytes"]:
        raise CalibrationSequenceError("out13_media_size_mismatch")

    plan = load_json(required["editorial_plan.json"])
    timeline = load_json(required["timeline_ir.json"])
    if plan["artifact_id"] != basis["artifact_id"]:
        raise CalibrationSequenceError("out13_artifact_identity_mismatch")
    if len(plan["cuts"]) != 7 or len(plan["omitted_ranges"]) != 8:
        raise CalibrationSequenceError("out13_plan_partition_count_mismatch")
    if len(timeline["cuts"]) != 7 or len(timeline["omitted_ranges"]) != 8:
        raise CalibrationSequenceError("out13_timeline_partition_count_mismatch")

    partitions = sorted(
        [
            (float(item["source_in_seconds"]), float(item["source_out_seconds"]))
            for item in timeline["cuts"] + timeline["omitted_ranges"]
        ]
    )
    if not close(partitions[0][0], 0.0):
        raise CalibrationSequenceError("out13_partition_start_mismatch")
    for previous, current in pairwise(partitions):
        if not close(previous[1], current[0]):
            raise CalibrationSequenceError("out13_partition_gap_or_overlap")
    if not close(partitions[-1][1], basis["source_duration_seconds"]):
        raise CalibrationSequenceError("out13_partition_end_mismatch")

    return {
        "status": "PASS",
        "artifactId": basis["artifact_id"],
        "cuts": len(plan["cuts"]),
        "omittedRanges": len(plan["omitted_ranges"]),
        "mediaSha256": basis["output_sha256"],
        "packageMutated": False,
    }


def validate_335_package(document: dict[str, Any], package: Path) -> dict[str, Any]:
    media = package / "final_video.mp4"
    if not media.is_file():
        raise CalibrationSequenceError("whole_review_exact_media_missing")
    identity = document["media"]
    if sha256(media) != identity["sha256"]:
        raise CalibrationSequenceError("whole_review_media_sha_mismatch")
    if media.stat().st_size != identity["byte_size"]:
        raise CalibrationSequenceError("whole_review_media_size_mismatch")
    return {
        "status": "PASS",
        "artifactId": document["artifact_id"],
        "mediaSha256": identity["sha256"],
        "mediaBytes": identity["byte_size"],
        "packageMutated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mixed", type=Path, default=DEFAULT_MIXED)
    parser.add_argument("--whole-review", type=Path, default=DEFAULT_WHOLE_REVIEW)
    parser.add_argument("--out13-package", type=Path, default=DEFAULT_OUT13_PACKAGE)
    parser.add_argument("--whole-package", type=Path, default=DEFAULT_335_PACKAGE)
    parser.add_argument("--skip-packages", action="store_true")
    args = parser.parse_args()

    mixed = load_json(args.mixed.resolve())
    whole_review = load_json(args.whole_review.resolve())
    result: dict[str, Any] = {
        "mixedCalibration": validate_mixed_document(mixed),
        "wholeContentReview": validate_whole_review_document(whole_review, mixed),
    }
    if not args.skip_packages:
        result["out13Package"] = validate_out13_package(
            mixed, args.out13_package.resolve()
        )
        result["whole335Package"] = validate_335_package(
            whole_review, args.whole_package.resolve()
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
