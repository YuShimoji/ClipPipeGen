from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALIBRATION = (
    REPO_ROOT
    / "docs"
    / "output_layer"
    / "clip_full_video_editorial_calibration_v1.json"
)
DEFAULT_PACKAGE = (
    REPO_ROOT
    / "episodes"
    / "integrated_checklist_reverse_test_20260811"
    / "artifacts"
    / "cpg-integrated-checklist-reverse-test-v1"
    / "successors"
    / "cpg-wiki-selected-opening-current-basis-v1"
    / "package"
)


class CalibrationValidationError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _equal_time(left: float, right: float) -> bool:
    return abs(float(left) - float(right)) <= 0.001


def validate_calibration(calibration: dict[str, Any]) -> dict[str, Any]:
    if calibration.get("schema_version") != (
        "clippipegen.full_video_editorial_calibration.v1"
    ):
        raise CalibrationValidationError("calibration_schema_mismatch")
    scope = calibration["calibration_scope"]
    units = calibration["decision_units"]
    if len(units) != scope["decision_unit_count"] or len(units) != 8:
        raise CalibrationValidationError("decision_unit_count_mismatch")

    decisions = {"KEEP": 0, "DROP": 0, "HOLD": 0}
    previous_source_out: float | None = None
    previous_output_out: float | None = None
    for index, unit in enumerate(units, start=1):
        if unit["unit_id"] != f"unit_{index:03d}":
            raise CalibrationValidationError("decision_unit_order_mismatch")
        decision = unit["decision"]
        if decision not in decisions:
            raise CalibrationValidationError("decision_value_invalid")
        decisions[decision] += 1
        source_in, source_out = unit["source_range_seconds"]
        output_in, output_out = unit["output_range_seconds"]
        if source_out <= source_in or output_out <= output_in:
            raise CalibrationValidationError("decision_unit_range_invalid")
        if previous_source_out is not None and not _equal_time(
            source_in, previous_source_out
        ):
            raise CalibrationValidationError("decision_unit_source_gap")
        if previous_output_out is not None and not _equal_time(
            output_in, previous_output_out
        ):
            raise CalibrationValidationError("decision_unit_output_gap")
        if not unit["evidence"]["observed"] or not unit["evidence"]["locators"]:
            raise CalibrationValidationError("decision_unit_evidence_missing")
        previous_source_out = float(source_out)
        previous_output_out = float(output_out)

    if not _equal_time(units[0]["source_range_seconds"][0], 2530.319):
        raise CalibrationValidationError("calibration_source_start_mismatch")
    if not _equal_time(previous_source_out or 0.0, 2865.599):
        raise CalibrationValidationError("calibration_source_end_mismatch")
    if not _equal_time(previous_output_out or 0.0, 335.28):
        raise CalibrationValidationError("calibration_output_end_mismatch")
    if decisions != {"KEEP": 8, "DROP": 0, "HOLD": 0}:
        raise CalibrationValidationError("decision_unit_summary_mismatch")

    rules = calibration["reusable_rules"]
    if {rule["state"] for rule in rules} - {
        "proposed",
        "validated",
        "human-approved",
    }:
        raise CalibrationValidationError("reusable_rule_state_invalid")
    if any(
        not rule.get("supporting_evidence")
        or not rule.get("scope_boundary")
        or not rule.get("plausible_counterexamples")
        for rule in rules
    ):
        raise CalibrationValidationError("reusable_rule_boundary_missing")

    audit = calibration["question_granularity_audit"]
    if audit["choice_created"]:
        raise CalibrationValidationError("mission_created_choice")
    if len(audit["genuinely_requires_human_authority"]) != 1:
        raise CalibrationValidationError("human_question_not_compressed")
    if calibration["production_scale_entry_conditions"]["overall"] != "PARTIAL":
        raise CalibrationValidationError("production_scale_result_mismatch")

    return {
        "status": "PASS",
        "caseIdentity": calibration["case_identity"],
        "decisionUnitCount": len(units),
        "decisionCounts": decisions,
        "reusableRuleCount": len(rules),
        "eliminatedQuestionCount": calibration["observed_measurements"][
            "item_level_questions_eliminated"
        ],
        "remainingHumanQuestionCount": len(audit["genuinely_requires_human_authority"]),
        "productionScale": "PARTIAL",
    }


def validate_exact_package(
    calibration: dict[str, Any], package: Path
) -> dict[str, Any]:
    required = {
        name: package / name
        for name in (
            "final_video.mp4",
            "successor_receipt.json",
            "timeline_ir.json",
            "caption_readback.json",
            "validation_readback.json",
        )
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise CalibrationValidationError(
            "exact_package_missing:" + ",".join(sorted(missing))
        )
    scope = calibration["calibration_scope"]
    if sha256(required["final_video.mp4"]) != scope["output_sha256"]:
        raise CalibrationValidationError("exact_media_sha256_mismatch")
    if required["final_video.mp4"].stat().st_size != scope["output_bytes"]:
        raise CalibrationValidationError("exact_media_size_mismatch")

    receipt = load_json(required["successor_receipt.json"])
    timeline = load_json(required["timeline_ir.json"])
    captions = load_json(required["caption_readback.json"])
    validation = load_json(required["validation_readback.json"])
    if receipt["artifact_id"] != scope["artifact_identity"]:
        raise CalibrationValidationError("exact_receipt_identity_mismatch")
    if validation["output_sha256"] != scope["output_sha256"]:
        raise CalibrationValidationError("validation_output_sha256_mismatch")
    if len(timeline["cuts"]) != scope["decision_unit_count"]:
        raise CalibrationValidationError("timeline_partition_count_mismatch")

    caption_items = {item["caption_id"] for item in captions["items"]}
    timeline_refs = {
        caption_id
        for cut in timeline["cuts"]
        for caption_id in cut.get("caption_ids", [])
    }
    dangling = sorted(timeline_refs - caption_items)
    observation = calibration["trace_contract_observation"]["evidence"]
    if len(timeline_refs) != observation["timeline_caption_reference_count"]:
        raise CalibrationValidationError("trace_observation_reference_count_stale")
    if len(caption_items) != observation["caption_readback_item_count"]:
        raise CalibrationValidationError("trace_observation_item_count_stale")
    if dangling != observation["dangling_caption_ids"]:
        raise CalibrationValidationError("trace_observation_dangling_ids_stale")

    return {
        "status": "PASS_WITH_RECORDED_LOCAL_REPAIR",
        "artifactIdentity": receipt["artifact_id"],
        "outputSha256": scope["output_sha256"],
        "outputBytes": scope["output_bytes"],
        "timelineDecisionUnits": len(timeline["cuts"]),
        "captionItems": len(caption_items),
        "danglingCaptionIds": dangling,
        "packageMutated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration", type=Path, default=DEFAULT_CALIBRATION)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--skip-package", action="store_true")
    args = parser.parse_args()

    calibration = load_json(args.calibration.resolve())
    result: dict[str, Any] = {"calibration": validate_calibration(calibration)}
    if not args.skip_package:
        result["exactPackage"] = validate_exact_package(
            calibration, args.package.resolve()
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
