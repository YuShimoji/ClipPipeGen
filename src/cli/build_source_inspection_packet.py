"""build-source-inspection-packet subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.source_inspection_packet import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_DASHBOARD_FILENAME,
    DEFAULT_DECISION_TEMPLATE_FILENAME,
    DEFAULT_GENERATED_AT,
    DEFAULT_OUTPUT_FILENAME,
    SourceInspectionPacketError,
    build_source_inspection_packet,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-source-inspection-packet",
        description=(
            "Build CPD-05 source inspection packets from CPD-04 dry-run "
            "episode init plans. This writes local review artifacts only; it "
            "does not open source URLs, authorize source collection, create "
            "episode folders, generate downstream episode files, approve "
            "rights, or mark anything production/public ready."
        ),
    )
    parser.add_argument(
        "--input",
        default="docs/content_planning/episode_init_plan.json",
        help="CPD-04 episode_init_plan.json path.",
    )
    parser.add_argument(
        "--output",
        default=f"docs/content_planning/{DEFAULT_OUTPUT_FILENAME}",
        help="Output source inspection packet JSON path.",
    )
    parser.add_argument(
        "--dashboard",
        default=f"docs/content_planning/{DEFAULT_DASHBOARD_FILENAME}",
        help="Output static HTML dashboard path.",
    )
    parser.add_argument(
        "--decision-template",
        default=f"docs/content_planning/{DEFAULT_DECISION_TEMPLATE_FILENAME}",
        help="Output blank source inspection decision template path.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_source_inspection_packet(
            input_path=Path(args.input),
            output_path=Path(args.output),
            dashboard_path=Path(args.dashboard),
            decision_template_path=Path(args.decision_template),
            base_dir=Path.cwd(),
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
        )
    except (OSError, SourceInspectionPacketError) as exc:
        print(f"build-source-inspection-packet failed: {exc}", file=sys.stderr)
        return 1

    summary = result["payload"]["summary"]
    gates = result["payload"]["gate_readback"]
    payload = {
        "schema_id": result["payload"]["schema_id"],
        "artifact_id": result["artifact_id"],
        "episode_init_plan_count": summary["episode_init_plan_count"],
        "inspectable_packet_count": summary["inspectable_packet_count"],
        "blocked_skipped_count": summary["blocked_skipped_count"],
        "decision_template_entry_count": summary["decision_template_entry_count"],
        "health": summary["health"],
        "source_inspection_packet_json": str(result["output_path"]).replace("\\", "/"),
        "dashboard_html": str(result["dashboard_path"]).replace("\\", "/"),
        "decision_template_json": str(result["decision_template_path"]).replace("\\", "/"),
        "dry_run": gates["dry_run"],
        "source_opened_by_worker": gates["source_opened_by_worker"],
        "network_required": gates["network_required"],
        "external_api_used": gates["external_api_used"],
        "media_downloaded": gates["media_downloaded"],
        "episode_dirs_created": gates["episode_dirs_created"],
        "fetch_authorized": gates["fetch_authorized"],
        "rights_approved": gates["rights_approved"],
        "production_ready": gates["production_ready"],
        "public_ready": gates["public_ready"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {payload['schema_id']}")
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"episode_init_plan_count: {payload['episode_init_plan_count']}")
        print(f"inspectable_packet_count: {payload['inspectable_packet_count']}")
        print(f"blocked_skipped_count: {payload['blocked_skipped_count']}")
        print(f"decision_template_entry_count: {payload['decision_template_entry_count']}")
        print(f"health: {payload['health']}")
        print(f"source_inspection_packet_json: {payload['source_inspection_packet_json']}")
        print(f"dashboard_html: {payload['dashboard_html']}")
        print(f"decision_template_json: {payload['decision_template_json']}")
        print(f"dry_run: {str(payload['dry_run']).lower()}")
        print(f"source_opened_by_worker: {str(payload['source_opened_by_worker']).lower()}")
        print(f"network_required: {str(payload['network_required']).lower()}")
        print(f"external_api_used: {str(payload['external_api_used']).lower()}")
        print(f"media_downloaded: {str(payload['media_downloaded']).lower()}")
        print(f"episode_dirs_created: {str(payload['episode_dirs_created']).lower()}")
        print(f"fetch_authorized: {str(payload['fetch_authorized']).lower()}")
        print(f"rights_approved: {str(payload['rights_approved']).lower()}")
        print(f"production_ready: {str(payload['production_ready']).lower()}")
        print(f"public_ready: {str(payload['public_ready']).lower()}")
    return 0
