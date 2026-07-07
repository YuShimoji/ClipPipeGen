"""build-episode-workspace-plan subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_workspace import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_CONTRACT_ARTIFACT_ID,
    DEFAULT_CONTRACT_FILENAME,
    DEFAULT_GENERATED_AT,
    DEFAULT_PLAN_FILENAME,
    EpisodeWorkspaceError,
    build_episode_workspace_plan,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-episode-workspace-plan",
        description=(
            "Build EWS-01 episode workspace plan and thin automation contract "
            "from the CPD-12 operator cockpit current work item. This writes "
            "planning JSON only; it does not open URLs, fetch media, generate "
            "transcripts/renders, create episode media, or approve rights."
        ),
    )
    parser.add_argument(
        "--input",
        default="docs/content_planning/operator_cockpit.json",
        help="CPD-12 operator_cockpit.json path.",
    )
    parser.add_argument(
        "--output",
        default=f"docs/content_planning/{DEFAULT_PLAN_FILENAME}",
        help="Output episode workspace plan JSON path.",
    )
    parser.add_argument(
        "--contract-output",
        default=f"docs/content_planning/{DEFAULT_CONTRACT_FILENAME}",
        help="Output thin automation contract JSON path.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--contract-artifact-id", default=DEFAULT_CONTRACT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_episode_workspace_plan(
            operator_cockpit_path=Path(args.input),
            output_path=Path(args.output),
            contract_output_path=Path(args.contract_output),
            base_dir=Path.cwd(),
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
            contract_artifact_id=args.contract_artifact_id,
        )
    except (OSError, EpisodeWorkspaceError) as exc:
        print(f"build-episode-workspace-plan failed: {exc}", file=sys.stderr)
        return 1

    plan = result["payload"]
    contract = result["contract"]
    payload = {
        "schema_id": plan["schema_id"],
        "artifact_id": result["artifact_id"],
        "episode_id": result["episode_id"],
        "episode_workspace_plan_json": str(result["output_path"]).replace("\\", "/"),
        "automation_contract_json": str(result["contract_output_path"]).replace("\\", "/"),
        "allowed_local_action_count": len(contract["allowed_local_actions"]),
        "deferred_local_action_count": len(contract["deferred_local_actions"]),
        "true_external_gate_count": len(contract["true_external_gates"]),
        "local_workspace_state": plan["local_workspace_state"],
        "source_url_state": plan["source_url_state"],
        "identity_state": plan["identity_state"],
        "fetch_authorized": plan["fetch_authorized"],
        "source_url_opened_by_worker": plan["readback"]["source_url_opened_by_worker"],
        "media_downloaded": plan["readback"]["media_downloaded"],
        "rights_approved": plan["readback"]["rights_approved"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {payload['schema_id']}")
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"episode_id: {payload['episode_id']}")
        print(f"episode_workspace_plan_json: {payload['episode_workspace_plan_json']}")
        print(f"automation_contract_json: {payload['automation_contract_json']}")
        print(f"allowed_local_action_count: {payload['allowed_local_action_count']}")
        print(f"deferred_local_action_count: {payload['deferred_local_action_count']}")
        print(f"true_external_gate_count: {payload['true_external_gate_count']}")
        print(f"local_workspace_state: {payload['local_workspace_state']}")
        print(f"source_url_state: {payload['source_url_state']}")
        print(f"identity_state: {payload['identity_state']}")
        print(f"fetch_authorized: {str(payload['fetch_authorized']).lower()}")
        print(f"source_url_opened_by_worker: {str(payload['source_url_opened_by_worker']).lower()}")
        print(f"media_downloaded: {str(payload['media_downloaded']).lower()}")
        print(f"rights_approved: {str(payload['rights_approved']).lower()}")
    return 0
