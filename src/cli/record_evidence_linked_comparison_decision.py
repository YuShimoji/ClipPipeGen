"""Record an explicit human verdict for one exact S2 comparison artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.evidence_linked_comparison_decision import (
    EvidenceLinkedComparisonDecisionError,
    record_evidence_linked_comparison_decision,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="record-evidence-linked-comparison-decision",
        description=(
            "Bind a human-provided accept, bounded_repair, or reject verdict "
            "to one closed S2 artifact manifest. This does not decide the "
            "verdict or approve rights, production, publishing, or upload."
        ),
    )
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--decision", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
    )
    args = parser.parse_args(argv)

    try:
        result = record_evidence_linked_comparison_decision(
            artifact_dir=args.artifact_dir,
            decision_path=args.decision,
            output_path=args.output,
            dry_run=args.dry_run,
            base_dir=Path.cwd(),
        )
    except EvidenceLinkedComparisonDecisionError as exc:
        print(
            f"record-evidence-linked-comparison-decision failed: {exc}",
            file=sys.stderr,
        )
        return 2

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"state: {result['state']}")
        print(f"artifact_id: {result['artifact_id']}")
        print(f"verdict: {result['verdict']}")
        print(f"written: {str(result['written']).lower()}")
        print(f"decision_receipt: {result['decision_receipt_path']}")
        print("external_gates_opened: false")
    return 0
