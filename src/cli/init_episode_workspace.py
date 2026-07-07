"""init-episode-workspace subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_workspace import EpisodeWorkspaceError, init_episode_workspace


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="init-episode-workspace",
        description=(
            "Dry-run or materialize an empty local episode workspace skeleton "
            "from an EWS-01 plan. Requires an explicit target; it does not open "
            "URLs, fetch media, generate transcripts/renders, or approve rights."
        ),
    )
    parser.add_argument(
        "--plan",
        default="docs/content_planning/episode_workspace_plan.json",
        help="EWS-01 episode_workspace_plan.json path.",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Explicit target root. The workspace is created as <target>/<episode_id>.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Report planned skeleton files without writing them. This is the default.",
    )
    mode.add_argument(
        "--materialize",
        action="store_true",
        help="Create empty skeleton files under the explicit target.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing skeleton files.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    materialize = bool(args.materialize)
    try:
        result = init_episode_workspace(
            plan_path=Path(args.plan),
            target_root=Path(args.target),
            materialize=materialize,
            force=args.force,
            base_dir=Path.cwd(),
        )
    except (OSError, EpisodeWorkspaceError) as exc:
        print(f"init-episode-workspace failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "schema_id": result["schema_id"],
        "episode_id": result["episode_id"],
        "workspace_dir": result["workspace_dir"],
        "materialized": result["materialized"],
        "created_file_count": result["created_file_count"],
        "planned_file_count": result["planned_file_count"],
        "source_url_opened": result["side_effects"]["source_url_opened"],
        "media_files_created": result["side_effects"]["media_files_created"],
        "transcript_generated": result["side_effects"]["transcript_generated"],
        "render_generated": result["side_effects"]["render_generated"],
        "rights_approved": result["side_effects"]["rights_approved"],
        "files": result["files"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {payload['schema_id']}")
        print(f"episode_id: {payload['episode_id']}")
        print(f"workspace_dir: {payload['workspace_dir']}")
        print(f"materialized: {str(payload['materialized']).lower()}")
        print(f"created_file_count: {payload['created_file_count']}")
        print(f"planned_file_count: {payload['planned_file_count']}")
        print(f"source_url_opened: {str(payload['source_url_opened']).lower()}")
        print(f"media_files_created: {str(payload['media_files_created']).lower()}")
        print(f"transcript_generated: {str(payload['transcript_generated']).lower()}")
        print(f"render_generated: {str(payload['render_generated']).lower()}")
        print(f"rights_approved: {str(payload['rights_approved']).lower()}")
    return 0
