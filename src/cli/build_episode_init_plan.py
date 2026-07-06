"""build-episode-init-plan subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_init_plan import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_DASHBOARD_FILENAME,
    DEFAULT_GENERATED_AT,
    DEFAULT_OUTPUT_FILENAME,
    EpisodeInitPlanError,
    build_episode_init_plan,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-episode-init-plan",
        description=(
            "Build CPD-04 dry-run episode initialization plans from CPD-03 "
            "source resolution records. This writes planning/review artifacts "
            "only; it does not create episode folders, fetch media, generate "
            "transcripts, create edit packs, render, thumbnail, publish, or "
            "approve rights."
        ),
    )
    parser.add_argument(
        "--input",
        default="docs/content_planning/episode_seed_source_resolution.json",
        help="CPD-03 episode_seed_source_resolution.json path.",
    )
    parser.add_argument(
        "--seed-input",
        default="docs/content_planning/episode_seed_drafts.json",
        help="Optional CPD-02 seed JSON for clip-scope enrichment.",
    )
    parser.add_argument(
        "--output",
        default=f"docs/content_planning/{DEFAULT_OUTPUT_FILENAME}",
        help="Output dry-run episode init plan JSON path.",
    )
    parser.add_argument(
        "--dashboard",
        default=f"docs/content_planning/{DEFAULT_DASHBOARD_FILENAME}",
        help="Output static HTML dashboard path.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_episode_init_plan(
            input_path=Path(args.input),
            output_path=Path(args.output),
            dashboard_path=Path(args.dashboard),
            seed_input_path=Path(args.seed_input) if args.seed_input else None,
            base_dir=Path.cwd(),
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
        )
    except (OSError, EpisodeInitPlanError) as exc:
        print(f"build-episode-init-plan failed: {exc}", file=sys.stderr)
        return 1

    summary = result["payload"]["summary"]
    gates = result["payload"]["gate_readback"]
    payload = {
        "schema_id": result["payload"]["schema_id"],
        "artifact_id": result["artifact_id"],
        "source_resolution_record_count": result["record_count"],
        "ready_dry_run_plan_count": result["ready_plan_count"],
        "skipped_unresolved_count": result["skipped_unresolved_count"],
        "health": summary["health"],
        "episode_init_plan_json": str(result["output_path"]).replace("\\", "/"),
        "dashboard_html": str(result["dashboard_path"]).replace("\\", "/"),
        "dry_run": gates["dry_run"],
        "network_required": gates["network_required"],
        "external_api_used": gates["external_api_used"],
        "media_downloaded": gates["media_downloaded"],
        "episode_dirs_created": gates["episode_dirs_created"],
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
        print(f"source_resolution_record_count: {payload['source_resolution_record_count']}")
        print(f"ready_dry_run_plan_count: {payload['ready_dry_run_plan_count']}")
        print(f"skipped_unresolved_count: {payload['skipped_unresolved_count']}")
        print(f"health: {payload['health']}")
        print(f"episode_init_plan_json: {payload['episode_init_plan_json']}")
        print(f"dashboard_html: {payload['dashboard_html']}")
        print(f"dry_run: {str(payload['dry_run']).lower()}")
        print(f"network_required: {str(payload['network_required']).lower()}")
        print(f"external_api_used: {str(payload['external_api_used']).lower()}")
        print(f"media_downloaded: {str(payload['media_downloaded']).lower()}")
        print(f"episode_dirs_created: {str(payload['episode_dirs_created']).lower()}")
        print(f"rights_approved: {str(payload['rights_approved']).lower()}")
        print(f"production_ready: {str(payload['production_ready']).lower()}")
        print(f"public_ready: {str(payload['public_ready']).lower()}")
    return 0
