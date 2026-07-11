"""build-complete-narrative-short subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.complete_narrative_short import (
    build_complete_narrative_short,
)
from src.integrations.render.vertical_short_candidate import VerticalShortCandidateError


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-complete-narrative-short",
        description=(
            "Build one three-cut 1080x1920 OUT-06 internal narrative delivery candidate."
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
        result = build_complete_narrative_short(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            predecessor_readback_path=Path(args.predecessor_readback),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except VerticalShortCandidateError as exc:
        print(f"build-complete-narrative-short failed: {exc}", file=sys.stderr)
        return 2
    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["readback"]["state"],
        "semantic_duration_seconds": result["readback"]["timeline"][
            "semantic_duration_seconds"
        ],
        "media_duration_seconds": result["readback"]["render"]["media"][
            "duration_seconds"
        ],
        "subtitle_count": result["readback"]["subtitle"]["count"],
        "video": result["readback"]["render"]["output_path"],
        "review_entrypoint": result["readback"]["review_entrypoint"],
        "machine_readback": result["readback"]["machine_readback"],
        "delivery_manifest": result["readback"]["delivery_manifest"],
        "open_command": result["readback"]["open_command"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"OUT-06 narrative candidate: {payload['video']}")
        print(f"Review entrypoint: {payload['review_entrypoint']}")
        print(f"Open: {payload['open_command']}")
    return 0
