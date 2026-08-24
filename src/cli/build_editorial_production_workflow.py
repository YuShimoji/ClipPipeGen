"""Build the calibrated editorial production-workflow connection receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.editorial_production_workflow import (
    EditorialProductionWorkflowError,
    build_editorial_production_workflow,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="build-editorial-production-workflow")
    parser.add_argument(
        "--mixed",
        default=REPO_ROOT / "docs/output_layer/clip_mixed_editorial_calibration_v1.json",
        type=Path,
    )
    parser.add_argument(
        "--accepted-authority",
        default=REPO_ROOT / "docs/output_layer/out13_human_acceptance_receipt.json",
        type=Path,
    )
    parser.add_argument(
        "--whole-review",
        default=REPO_ROOT / "docs/output_layer/clip_335s_whole_content_review_v1.json",
        type=Path,
    )
    parser.add_argument(
        "--output",
        default=REPO_ROOT
        / "docs/output_layer/clip_editorial_production_workflow_connection_v1.json",
        type=Path,
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        packet = build_editorial_production_workflow(
            mixed_path=args.mixed,
            acceptance_path=args.accepted_authority,
            whole_review_path=args.whole_review,
            output_path=args.output,
            base_dir=REPO_ROOT,
        )
    except (OSError, json.JSONDecodeError, EditorialProductionWorkflowError) as exc:
        print(f"build-editorial-production-workflow failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "requirementId": packet["requirement_id"],
        "status": packet["status"],
        "resolvedDecisionUnits": packet["autonomous_resolution"][
            "decision_units_resolved"
        ],
        "itemLevelQuestionsReemitted": 0,
        "remainingHumanJudgments": packet["human_judgment"]["count"],
        "promptEmission": packet["choice_serialization"]["prompt_emission"],
        "output": args.output.resolve().as_posix(),
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0
