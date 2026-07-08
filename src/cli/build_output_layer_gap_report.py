"""CLI for OUT-01 output layer gap report generation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from tools.output_layer.build_output_layer_gap_report import (
    DEFAULT_ARTIFACT_ID,
    write_output_layer_gap_report,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-output-layer-gap-report",
        description="Build readback-only OUT-01 output capability and gap artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/output_layer",
        help="Directory for JSON, Markdown, and HTML outputs.",
    )
    parser.add_argument(
        "--generated-at",
        default=None,
        help="Generated-at value for deterministic tests or handoff reports.",
    )
    parser.add_argument(
        "--artifact-id",
        default=DEFAULT_ARTIFACT_ID,
        help="Stable artifact id to write into the report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Readback format for stdout.",
    )
    args = parser.parse_args(argv)

    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
    result = write_output_layer_gap_report(
        base_dir=Path.cwd(),
        output_dir=Path(args.output_dir),
        generated_at=generated_at,
        artifact_id=args.artifact_id,
    )
    report = result["report"]
    payload = {
        "format": "output_layer_gap_report_v0",
        "artifact_id": report["artifact_id"],
        "generated_at": report["generated_at"],
        "proof_status": report["proof_readback"]["proof_status"],
        "production_ready": report["proof_readback"]["production_ready"],
        "public_ready": report["proof_readback"]["public_ready"],
        "network_used": report["scope"]["network_used"],
        "media_generated": report["scope"]["media_generated"],
        "capability_count": len(report["capability_matrix"]),
        "gap_count": len(report["gap_log"]),
        "recommended_next_slice": report["recommended_next_slice"]["slice_id"],
        "outputs": result["outputs"],
    }

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"wrote output layer gap report: {payload['artifact_id']}")
        for label, output_path in result["outputs"].items():
            print(f"- {label}: {output_path}")
        print(f"proof_status: {payload['proof_status']}")
        print(f"recommended_next_slice: {payload['recommended_next_slice']}")
    return 0
