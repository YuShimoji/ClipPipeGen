"""build-real-unused-range-short-minibatch subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.real_unused_range_short_minibatch import (
    build_real_unused_range_short_minibatch,
)
from src.integrations.render.vertical_short_candidate import VerticalShortCandidateError


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-real-unused-range-short-minibatch",
        description=(
            "Build one or two real unused-range 1080x1920 OUT-08 internal review candidates."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--candidate-plan-input", required=True)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_real_unused_range_short_minibatch(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            candidate_plan_input_path=Path(args.candidate_plan_input),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except VerticalShortCandidateError as exc:
        print(f"build-real-unused-range-short-minibatch failed: {exc}", file=sys.stderr)
        return 2

    readback = result["readback"]
    payload = {
        "artifact_id": result["artifact_id"],
        "state": readback["state"],
        "target_candidate_count": readback["target_candidate_count"],
        "actual_candidate_count": readback["actual_candidate_count"],
        "candidates": [
            {
                "candidate_id": item["candidate_id"],
                "duration_seconds": item["semantic_duration_seconds"],
                "subtitle_count": item["subtitle_count"],
                "video": item["video"]["package_relative_path"],
            }
            for item in readback["candidates"]
        ],
        "review_entrypoint": readback["review_entrypoint"],
        "machine_readback": readback["machine_readback"],
        "batch_manifest": readback["batch_manifest"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            "OUT-08 real unused-range candidates: "
            f"{payload['actual_candidate_count']}/{payload['target_candidate_count']}"
        )
        print(f"Review entrypoint: {payload['review_entrypoint']}")
    return 0
