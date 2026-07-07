"""prepare-source-identity-decision subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_workspace import (
    EpisodeWorkspaceError,
    prepare_source_identity_decision,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="prepare-source-identity-decision",
        description=(
            "Create a pending local source identity decision template from an "
            "explicit workspace skeleton. This does not open URLs, fetch media, "
            "or fabricate a human decision."
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
        "--output",
        default=None,
        help="Optional template JSON path; defaults inside the workspace.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = prepare_source_identity_decision(
            workspace_path=Path(args.workspace),
            plan_path=Path(args.plan),
            contract_path=Path(args.contract) if args.contract else None,
            output_path=Path(args.output) if args.output else None,
            base_dir=Path.cwd(),
        )
    except (OSError, EpisodeWorkspaceError) as exc:
        print(f"prepare-source-identity-decision failed: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {result['schema_id']}")
        print(f"artifact_id: {result['artifact_id']}")
        print(f"episode_id: {result['episode_id']}")
        print(f"identity_decision: {result['identity_decision']}")
        print(f"decision_record_path: {result['decision_record_path']}")
        print(f"allows_fetch_prep: {str(result['allows_fetch_prep']).lower()}")
        print(f"fetch_authorized: {str(result['fetch_authorized']).lower()}")
    return 0
