"""status-episode subcommand: SH-02-lite episode status adapter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.pipeline.episode_status import build_episode_status


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="status-episode",
        description="Summarize one episode's Slice 1 artifacts for the GUI MVP.",
    )
    parser.add_argument("--episode-id", help="Episode id under --root")
    parser.add_argument("--root", default="episodes")
    parser.add_argument(
        "--episode-dir",
        help="Explicit episode directory. Overrides --root/--episode-id.",
    )
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--bridge-config", default="config/nlmytgen_path.json")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)

    if args.episode_dir:
        episode_dir = Path(args.episode_dir)
    elif args.episode_id:
        episode_dir = Path(args.root) / args.episode_id
    else:
        parser.error("either --episode-dir or --episode-id is required")

    status = build_episode_status(
        episode_dir=episode_dir,
        base_dir=args.base_dir,
        bridge_config_path=args.bridge_config,
    )

    if args.format == "json":
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        _print_text(status)
    return 0


def _print_text(status: dict) -> None:
    print(f"episode: {status.get('episode_id') or '(unknown)'}")
    print(f"dir: {status['episode_dir']}")
    print(f"rights: {status['rights']['state']} ({status['rights'].get('compliance_status')})")
    print(
        "materials: "
        f"{status['materials']['state']} "
        f"({status['materials'].get('materials_count', 0)} materials)"
    )
    print(
        "editing: "
        f"{status['editing']['state']} "
        f"({status['editing'].get('cut_candidates_count', 0)} cuts)"
    )
    context = status["editing"].get("context_checks") or {}
    if context:
        print(
            "context: "
            f"passed={context.get('passed_count', 0)}, "
            f"needs_review={context.get('needs_review_count', 0)}, "
            f"failed={context.get('failed_count', 0)}, "
            f"not_checked={context.get('not_checked_count', 0)}"
        )
    operator = status.get("operator_review") or {}
    if operator:
        print(
            "reviewability: "
            f"{operator.get('reviewability', 'unknown')} "
            f"(review_ready={str(operator.get('review_ready', False)).lower()}, "
            f"missing={len(operator.get('missing_review_artifacts') or [])})"
        )
        print(f"review next: {operator.get('next_human_action', '')}")
    final_cut = status.get("final_cut_decision") or {}
    if final_cut:
        print(
            "final cut decision: "
            f"{final_cut.get('state', 'unknown')} "
            f"(keep={len(final_cut.get('keep_cut_ids') or [])}, "
            f"needs_adjustment={len(final_cut.get('needs_adjustment_cut_ids') or [])}, "
            f"reject={len(final_cut.get('reject_cut_ids') or [])})"
        )
    print(
        "thumbnail: "
        f"{status['thumbnail']['state']} "
        f"({status['thumbnail'].get('slots_count', 0)} slots)"
    )
    action = status["next_action"]
    print(f"next[{action['owner']}]: {action['action']}")
