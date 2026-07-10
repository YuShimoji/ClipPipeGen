"""build-docs-dashboard subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.docs_dashboard import DEFAULT_GENERATED_AT, write_project_status


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-docs-dashboard",
        description=(
            "Build the docs v1.5 project-status dashboard. This is a docs "
            "navigation/readback tool, not a production acceptance gate."
        ),
    )
    parser.add_argument("--output-dir", default="docs/dashboard")
    parser.add_argument(
        "--generated-at",
        default=DEFAULT_GENERATED_AT,
        help=(
            "Override generated_at. By default the value is derived from "
            "docs/RUNTIME_STATE.md front matter."
        ),
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = write_project_status(
            base_dir=Path.cwd(),
            output_dir=Path(args.output_dir),
            generated_at=args.generated_at,
        )
    except (OSError, ValueError) as exc:
        print(f"build-docs-dashboard failed: {exc}", file=sys.stderr)
        return 1

    status = result["status"]
    payload = {
        "schema_id": status["schema_id"],
        "generated_at": status["generated_at"],
        "dashboard_json": str(result["json_path"]).replace("\\", "/"),
        "dashboard_html": str(result["html_path"]).replace("\\", "/"),
        "features_index": str(result["features_path"]).replace("\\", "/"),
        "finding_count": status["doc_health"]["finding_count"],
        "finding_total": status["doc_health"]["finding_total"],
        "findings_truncated": status["doc_health"]["findings_truncated"],
        "feature_count": status["feature_summary"]["feature_count"],
        "artifact_count": status["artifact_summary"]["artifact_count"],
        "finding_types": sorted(
            {finding["type"] for finding in status["doc_health"]["findings"]}
        ),
        "top_next_improvements": status["top_next_improvements"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {payload['schema_id']}")
        print(f"dashboard_json: {payload['dashboard_json']}")
        print(f"dashboard_html: {payload['dashboard_html']}")
        print(f"features_index: {payload['features_index']}")
        print(f"feature_count: {payload['feature_count']}")
        print(f"artifact_count: {payload['artifact_count']}")
        print(
            f"finding_count: {payload['finding_count']} "
            f"of {payload['finding_total']}"
        )
        print(f"findings_truncated: {str(payload['findings_truncated']).lower()}")
        print(f"finding_types: {', '.join(payload['finding_types'])}")
    return 0
