"""build-operator-cockpit subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.operator_cockpit import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_DASHBOARD_FILENAME,
    DEFAULT_GENERATED_AT,
    DEFAULT_OUTPUT_FILENAME,
    OperatorCockpitError,
    build_operator_cockpit,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-operator-cockpit",
        description=(
            "Build the CPD-08 operator home / funnel meters cockpit from CPD-01 "
            "through CPD-05 planning artifacts. This writes a human-facing "
            "dark-mode review surface only; it does not open URLs, fetch media, "
            "create episode folders, approve rights, or mark anything production/public ready."
        ),
    )
    parser.add_argument(
        "--candidates",
        default="docs/content_planning/content_candidates.json",
        help="CPD-01 content_candidates.json path.",
    )
    parser.add_argument(
        "--seeds",
        default="docs/content_planning/episode_seed_drafts.json",
        help="CPD-02 episode_seed_drafts.json path.",
    )
    parser.add_argument(
        "--source-resolution",
        default="docs/content_planning/episode_seed_source_resolution.json",
        help="CPD-03 episode_seed_source_resolution.json path.",
    )
    parser.add_argument(
        "--episode-init-plan",
        default="docs/content_planning/episode_init_plan.json",
        help="CPD-04 episode_init_plan.json path.",
    )
    parser.add_argument(
        "--source-inspection-packet",
        default="docs/content_planning/source_inspection_packet.json",
        help="CPD-05 source_inspection_packet.json path.",
    )
    parser.add_argument(
        "--decision-template",
        default="docs/content_planning/source_inspection_decisions.template.json",
        help="CPD-05 source_inspection_decisions.template.json path.",
    )
    parser.add_argument(
        "--output",
        default=f"docs/content_planning/{DEFAULT_OUTPUT_FILENAME}",
        help="Output consolidated operator cockpit JSON path.",
    )
    parser.add_argument(
        "--dashboard",
        default=f"docs/content_planning/{DEFAULT_DASHBOARD_FILENAME}",
        help="Output consolidated operator cockpit HTML path.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_operator_cockpit(
            candidates_path=Path(args.candidates),
            seed_path=Path(args.seeds),
            source_resolution_path=Path(args.source_resolution),
            episode_init_plan_path=Path(args.episode_init_plan),
            source_inspection_packet_path=Path(args.source_inspection_packet),
            decision_template_path=Path(args.decision_template),
            output_path=Path(args.output),
            dashboard_path=Path(args.dashboard),
            base_dir=Path.cwd(),
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
        )
    except (OSError, OperatorCockpitError) as exc:
        print(f"build-operator-cockpit failed: {exc}", file=sys.stderr)
        return 1

    payload = result["payload"]
    summary = payload["summary"]
    gates = payload["gate_readback"]
    cli_payload = {
        "schema_id": payload["schema_id"],
        "artifact_id": result["artifact_id"],
        "total_candidates": summary["total_candidates"],
        "source_backed_count": summary["source_backed_count"],
        "source_missing_count": summary["source_missing_count"],
        "source_missing_idea_backlog_count": summary["source_missing_idea_backlog_count"],
        "blocked_or_hold_count": summary["blocked_or_hold_count"],
        "inspectable_packet_count": summary["inspectable_packet_count"],
        "fetch_authorized_count": summary["fetch_authorized_count"],
        "home_metric_count": len(payload["home_metrics"]),
        "funnel_stage_count": len(payload["funnel_stages"]),
        "action_queue_count": len(payload["action_queue"]),
        "recommended_next_action": payload["recommended_next_action"]["action_id"],
        "operator_cockpit_json": str(result["output_path"]).replace("\\", "/"),
        "operator_cockpit_html": str(result["dashboard_path"]).replace("\\", "/"),
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
        json.dump(cli_payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {cli_payload['schema_id']}")
        print(f"artifact_id: {cli_payload['artifact_id']}")
        print(f"total_candidates: {cli_payload['total_candidates']}")
        print(f"source_backed_count: {cli_payload['source_backed_count']}")
        print(f"source_missing_count: {cli_payload['source_missing_count']}")
        print(f"source_missing_idea_backlog_count: {cli_payload['source_missing_idea_backlog_count']}")
        print(f"blocked_or_hold_count: {cli_payload['blocked_or_hold_count']}")
        print(f"inspectable_packet_count: {cli_payload['inspectable_packet_count']}")
        print(f"fetch_authorized_count: {cli_payload['fetch_authorized_count']}")
        print(f"home_metric_count: {cli_payload['home_metric_count']}")
        print(f"funnel_stage_count: {cli_payload['funnel_stage_count']}")
        print(f"action_queue_count: {cli_payload['action_queue_count']}")
        print(f"recommended_next_action: {cli_payload['recommended_next_action']}")
        print(f"operator_cockpit_json: {cli_payload['operator_cockpit_json']}")
        print(f"operator_cockpit_html: {cli_payload['operator_cockpit_html']}")
        print(f"source_opened_by_worker: {str(cli_payload['source_opened_by_worker']).lower()}")
        print(f"network_required: {str(cli_payload['network_required']).lower()}")
        print(f"external_api_used: {str(cli_payload['external_api_used']).lower()}")
        print(f"media_downloaded: {str(cli_payload['media_downloaded']).lower()}")
        print(f"episode_dirs_created: {str(cli_payload['episode_dirs_created']).lower()}")
        print(f"fetch_authorized: {str(cli_payload['fetch_authorized']).lower()}")
        print(f"rights_approved: {str(cli_payload['rights_approved']).lower()}")
        print(f"production_ready: {str(cli_payload['production_ready']).lower()}")
        print(f"public_ready: {str(cli_payload['public_ready']).lower()}")
    return 0
