"""build-episode-seed-drafts subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_seed_bridge import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_DASHBOARD_FILENAME,
    DEFAULT_GENERATED_AT,
    DEFAULT_OUTPUT_FILENAME,
    EpisodeSeedBridgeError,
    build_episode_seed_drafts,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-episode-seed-drafts",
        description=(
            "Build CPD-02 draft episode seeds from CPD-01 candidate JSON. "
            "This writes planning artifacts only; it does not fetch media, "
            "create episode folders, approve rights, render, thumbnail, or publish."
        ),
    )
    parser.add_argument(
        "--input",
        default="docs/content_planning/content_candidates.json",
        help="CPD-01 content_candidates.json or fixture JSON.",
    )
    parser.add_argument(
        "--output",
        default=f"docs/content_planning/{DEFAULT_OUTPUT_FILENAME}",
        help="Output episode seed draft JSON path.",
    )
    parser.add_argument(
        "--dashboard",
        default=f"docs/content_planning/{DEFAULT_DASHBOARD_FILENAME}",
        help="Output static HTML dashboard path.",
    )
    parser.add_argument(
        "--candidate-id",
        action="append",
        default=[],
        help="Limit output to one candidate id. May be repeated.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit output to the top N candidates after score ordering.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_episode_seed_drafts(
            input_path=Path(args.input),
            output_path=Path(args.output),
            dashboard_path=Path(args.dashboard),
            base_dir=Path.cwd(),
            candidate_ids=args.candidate_id or None,
            limit=args.limit,
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
        )
    except (OSError, EpisodeSeedBridgeError) as exc:
        print(f"build-episode-seed-drafts failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "schema_id": result["payload"]["schema_id"],
        "artifact_id": result["artifact_id"],
        "seed_count": result["seed_count"],
        "top_seed_id": result["top_seed_id"],
        "episode_seed_drafts": str(result["output_path"]).replace("\\", "/"),
        "dashboard_html": str(result["dashboard_path"]).replace("\\", "/"),
        "network_required": result["payload"]["gate_readback"]["network_required"],
        "media_downloaded": result["payload"]["gate_readback"]["media_downloaded"],
        "episode_dirs_created": result["payload"]["gate_readback"]["episode_dirs_created"],
        "production_candidate": result["payload"]["gate_readback"]["production_candidate"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {payload['schema_id']}")
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"seed_count: {payload['seed_count']}")
        print(f"top_seed_id: {payload['top_seed_id']}")
        print(f"episode_seed_drafts: {payload['episode_seed_drafts']}")
        print(f"dashboard_html: {payload['dashboard_html']}")
        print(f"network_required: {str(payload['network_required']).lower()}")
        print(f"media_downloaded: {str(payload['media_downloaded']).lower()}")
        print(f"episode_dirs_created: {str(payload['episode_dirs_created']).lower()}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
    return 0
