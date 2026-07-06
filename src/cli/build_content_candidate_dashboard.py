"""build-content-candidate-dashboard subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.content_planning import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_GENERATED_AT,
    ContentPlanningError,
    build_content_candidate_dashboard,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-content-candidate-dashboard",
        description=(
            "Build the CPD-01 local/offline content candidate and channel "
            "strategy dashboard from fixture metadata. This does not fetch "
            "media, use OAuth, publish, or make rights acceptance claims."
        ),
    )
    parser.add_argument(
        "--input",
        default="samples/content_planning/content_candidates_fixture.json",
        help="Candidate fixture JSON path.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/content_planning",
        help="Directory for content_candidates.json, channel_strategy.json, and HTML.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_content_candidate_dashboard(
            fixture_path=Path(args.input),
            output_dir=Path(args.output_dir),
            base_dir=Path.cwd(),
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
        )
    except (OSError, ContentPlanningError) as exc:
        print(f"build-content-candidate-dashboard failed: {exc}", file=sys.stderr)
        return 1

    candidate_payload = result["candidate_payload"]
    gate_readback = candidate_payload["gate_readback"]
    payload = {
        "schema_id": candidate_payload["schema_id"],
        "artifact_id": result["artifact_id"],
        "candidate_count": result["candidate_count"],
        "strategy_count": result["strategy_count"],
        "top_candidate_id": result["top_candidate_id"],
        "content_candidates": str(result["candidates_path"]).replace("\\", "/"),
        "channel_strategy": str(result["strategy_path"]).replace("\\", "/"),
        "dashboard_html": str(result["dashboard_path"]).replace("\\", "/"),
        "network_required": gate_readback["network_required"],
        "media_downloaded": gate_readback["media_downloaded"],
        "production_candidate": gate_readback["production_candidate"],
        "rights_status_counts": gate_readback["rights_status_counts"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {payload['schema_id']}")
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"candidate_count: {payload['candidate_count']}")
        print(f"strategy_count: {payload['strategy_count']}")
        print(f"top_candidate_id: {payload['top_candidate_id']}")
        print(f"content_candidates: {payload['content_candidates']}")
        print(f"channel_strategy: {payload['channel_strategy']}")
        print(f"dashboard_html: {payload['dashboard_html']}")
        print(f"network_required: {str(payload['network_required']).lower()}")
        print(f"media_downloaded: {str(payload['media_downloaded']).lower()}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
    return 0
