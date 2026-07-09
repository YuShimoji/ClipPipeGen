"""inspect-episode-workspace subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_workspace import EpisodeWorkspaceError, inspect_episode_workspace


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="inspect-episode-workspace",
        description=(
            "Inspect an explicit local episode workspace skeleton and emit "
            "machine-readable readiness/status. This is read-only: it does not "
            "open URLs, fetch media, generate transcripts/renders/thumbnails, "
            "or approve rights."
        ),
    )
    parser.add_argument(
        "--workspace",
        required=True,
        help="Explicit episode workspace path, usually <target>/<episode_id>.",
    )
    parser.add_argument(
        "--plan",
        default="docs/content_planning/episode_workspace_plan.json",
        help="EWS-01 episode_workspace_plan.json path.",
    )
    parser.add_argument(
        "--contract",
        default=None,
        help="Optional automation_contract.json path; defaults to the plan reference.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON output path. Stdout is still emitted.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = inspect_episode_workspace(
            workspace_path=Path(args.workspace),
            plan_path=Path(args.plan),
            contract_path=Path(args.contract) if args.contract else None,
            output_path=Path(args.output) if args.output else None,
            base_dir=Path.cwd(),
        )
    except (OSError, EpisodeWorkspaceError) as exc:
        print(f"inspect-episode-workspace failed: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {result['schema_id']}")
        print(f"artifact_id: {result['artifact_id']}")
        print(f"episode_id: {result['episode_id']}")
        print(f"workspace_path: {result['workspace_path']}")
        print(f"manifest_state: {result['manifest_state']}")
        print(f"source_identity_state: {result['source_identity_state']}")
        print(f"source_url_state: {result['source_url_state']}")
        print(f"fetch_authorized: {str(result['fetch_authorized']).lower()}")
        print(f"readiness_level: {result['readiness_level']}")
        print(f"skeleton_ready: {str(result['readiness']['skeleton_ready']).lower()}")
        print(f"missing_file_count: {len(result['missing_files'])}")
        print(
            "unexpected_media_like_count: "
            f"{len(result['files']['unexpected_media_like'])}"
        )
        print(
            "next_allowed_local_action: "
            f"{result['next_allowed_local_action'].get('action_id', '')}"
        )
    return 0
