"""build-vertical-short-candidate subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.vertical_short_candidate import (
    VerticalShortCandidateError,
    build_vertical_short_candidate,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-vertical-short-candidate",
        description=(
            "Build one accepted-timeline 1080x1920 OUT-05 internal review candidate."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--predecessor-readback", required=True)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_vertical_short_candidate(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            predecessor_readback_path=Path(args.predecessor_readback),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except VerticalShortCandidateError as exc:
        print(f"build-vertical-short-candidate failed: {exc}", file=sys.stderr)
        return 2
    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["readback"]["state"],
        "duration_seconds": result["readback"]["render"]["media"]["duration_seconds"],
        "video": result["readback"]["render"]["output_path"],
        "review_entrypoint": result["readback"]["review_entrypoint"],
        "machine_readback": result["readback"]["machine_readback"],
        "open_command": result["readback"]["open_command"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"OUT-05 vertical candidate: {payload['video']}")
        print(f"Review entrypoint: {payload['review_entrypoint']}")
        print(f"Open: {payload['open_command']}")
    return 0
