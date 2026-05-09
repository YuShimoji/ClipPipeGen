"""generate-subtitles subcommand: ED-04 transcript -> edit_pack subtitles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.edit_pack import load_edit_pack, save_edit_pack
from src.pipeline.subtitle_generation import (
    SubtitleGenerationError,
    generate_subtitle_drafts,
)
from src.pipeline.transcript import load_transcript


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="generate-subtitles",
        description="Generate edit_pack.subtitles[] drafts from transcript.json.",
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
    parser.add_argument("--wrap-eaw", type=int)
    parser.add_argument(
        "--ambiguous-width",
        type=int,
        choices=(1, 2),
        default=1,
    )
    parser.add_argument("--style-slot", default="subtitle.default")
    parser.add_argument("--replace-auto", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        transcript = load_transcript(args.transcript)
        edit_pack = load_edit_pack(args.edit_pack)
        result = generate_subtitle_drafts(
            edit_pack,
            transcript,
            selected_cuts_only=args.selected_cuts_only,
            cut_id=args.cut_id,
            wrap_eaw=args.wrap_eaw,
            ambiguous_width=args.ambiguous_width,
            style_slot=args.style_slot,
            replace_auto=args.replace_auto,
        )
    except (OSError, json.JSONDecodeError, SubtitleGenerationError) as exc:
        print(f"generate-subtitles failed: {exc}", file=sys.stderr)
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
        print(f"{action}: {payload['generated_count']} subtitle(s)")
        print(f"scope: {payload['scope']}")
        print(f"subtitles_count: {payload['subtitles_count']}")
        if payload["replaced_auto_count"]:
            print(f"replaced_auto: {payload['replaced_auto_count']}")
        if payload["skipped_segments_count"]:
            print(f"skipped_segments: {payload['skipped_segments_count']}")
        if args.dry_run:
            print(f"dry_run: no files written; output would be {payload['output']}")
        else:
            print(f"saved: {payload['output']}")

    return 0
