"""plan-source-fetch-prep subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_workspace import EpisodeWorkspaceError, plan_source_fetch_prep


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="plan-source-fetch-prep",
        description=(
            "Build a local source fetch-prep plan from an explicit workspace and "
            "source identity decision. This does not open URLs, fetch media, "
            "generate transcripts/renders/thumbnails, or approve rights."
        ),
    )
    parser.add_argument("--workspace", required=True, help="Explicit episode workspace path.")
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
        "--decision",
        default=None,
        help="Optional source_identity.decision.json path; defaults inside the workspace.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output path; defaults to source_fetch_prep_plan.json inside the workspace.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Emit stdout only without writing source_fetch_prep_plan.json.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = plan_source_fetch_prep(
            workspace_path=Path(args.workspace),
            plan_path=Path(args.plan),
            contract_path=Path(args.contract) if args.contract else None,
            decision_path=Path(args.decision) if args.decision else None,
            output_path=Path(args.output) if args.output else None,
            write_output=not args.no_write,
            base_dir=Path.cwd(),
        )
    except (OSError, EpisodeWorkspaceError) as exc:
        print(f"plan-source-fetch-prep failed: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {result['schema_id']}")
        print(f"artifact_id: {result['artifact_id']}")
        print(f"episode_id: {result['episode_id']}")
        print(f"identity_decision: {result['identity_decision']}")
        print(f"allows_fetch_prep: {str(result['allows_fetch_prep']).lower()}")
        print(f"prep_state: {result['prep_state']}")
        print(f"blocked_reason: {result['blocked_reason'] or ''}")
        print(f"fetch_authorized: {str(result['fetch_authorized']).lower()}")
        print(f"media_downloaded: {str(result['media_downloaded']).lower()}")
        print(f"rights_approved: {str(result['rights_approved']).lower()}")
        print(f"public_ready: {str(result['public_ready']).lower()}")
    return 0
