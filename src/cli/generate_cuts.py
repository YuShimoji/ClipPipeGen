"""generate-cuts subcommand: ED-02 transcript -> edit_pack cut candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.cut_generation import CutGenerationError, generate_cut_candidates
from src.pipeline.edit_pack import load_edit_pack, save_edit_pack
from src.pipeline.transcript import load_transcript


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="generate-cuts",
        description="Generate edit_pack.cut_candidates[] from transcript.json.",
    )
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--edit-pack", required=True)
    parser.add_argument("--output", help="output edit_pack path (default: overwrite --edit-pack)")
    parser.add_argument("--target-duration-seconds", type=float)
    parser.add_argument("--min-duration-seconds", type=float, default=5.0)
    parser.add_argument("--max-duration-seconds", type=float)
    parser.add_argument("--gap-threshold-seconds", type=float, default=4.0)
    parser.add_argument("--max-candidates", type=int, default=5)
    parser.add_argument("--replace-auto", action="store_true")
    parser.add_argument("--select-generated", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        transcript = load_transcript(args.transcript)
        edit_pack = load_edit_pack(args.edit_pack)
        result = generate_cut_candidates(
            edit_pack,
            transcript,
            target_duration_seconds=args.target_duration_seconds,
            min_duration_seconds=args.min_duration_seconds,
            max_duration_seconds=args.max_duration_seconds,
            gap_threshold_seconds=args.gap_threshold_seconds,
            max_candidates=args.max_candidates,
            replace_auto=args.replace_auto,
            select_generated=args.select_generated,
        )
    except (OSError, json.JSONDecodeError, CutGenerationError) as exc:
        print(f"generate-cuts failed: {exc}", file=sys.stderr)
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
        action = "would generate" if args.dry_run else "generated"
        print(f"{action}: {payload['generated_count']} cut candidate(s)")
        print(f"cut_candidates_count: {payload['cut_candidates_count']}")
        print(f"selected_cuts_count: {payload['selected_cuts_count']}")
        print(f"target_duration_seconds: {payload['target_duration_seconds']}")
        if payload["replaced_auto_count"]:
            print(f"replaced_auto: {payload['replaced_auto_count']}")
        if payload["skipped_segments_count"]:
            print(f"skipped_segments: {payload['skipped_segments_count']}")
        if args.dry_run:
            print(f"dry_run: no files written; output would be {payload['output']}")
        else:
            print(f"saved: {payload['output']}")

    return 0
