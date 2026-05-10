"""check-cut-context subcommand: ED-03 transcript context review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.context_check import ContextCheckError, check_cut_context
from src.pipeline.edit_pack import load_edit_pack, save_edit_pack
from src.pipeline.transcript import load_transcript


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="check-cut-context",
        description="Update edit_pack cut context_check results from transcript.json.",
    )
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--edit-pack", required=True)
    parser.add_argument(
        "--output",
        help="output edit_pack path (default: overwrite --edit-pack)",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--selected-cuts-only", action="store_true")
    scope.add_argument("--cut-id")
    parser.add_argument("--boundary-tolerance-seconds", type=float, default=0.25)
    parser.add_argument("--adjacent-window-seconds", type=float, default=1.5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        transcript = load_transcript(args.transcript)
        edit_pack = load_edit_pack(args.edit_pack)
        result = check_cut_context(
            edit_pack,
            transcript,
            selected_cuts_only=args.selected_cuts_only,
            cut_id=args.cut_id,
            boundary_tolerance_seconds=args.boundary_tolerance_seconds,
            adjacent_window_seconds=args.adjacent_window_seconds,
        )
    except (OSError, json.JSONDecodeError, ContextCheckError) as exc:
        print(f"check-cut-context failed: {exc}", file=sys.stderr)
        return 1

    output_path = Path(args.output or args.edit_pack)
    payload = {
        **result.to_dict(),
        "transcript": args.transcript,
        "edit_pack": args.edit_pack,
        "output": str(output_path).replace("\\", "/"),
        "dry_run": args.dry_run,
    }

    if not args.dry_run:
        save_edit_pack(result.edit_pack, output_path)

    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        action = "would check" if args.dry_run else "checked"
        print(f"{action}: {payload['checked_count']} cut candidate(s)")
        print(f"scope: {payload['scope']}")
        print(f"passed: {payload['passed_count']}")
        print(f"needs_review: {payload['needs_review_count']}")
        print(f"failed: {payload['failed_count']}")
        if payload["skipped_count"]:
            print(f"skipped: {payload['skipped_count']}")
        if args.dry_run:
            print(f"dry_run: no files written; output would be {payload['output']}")
        else:
            print(f"saved: {payload['output']}")

    return 0
