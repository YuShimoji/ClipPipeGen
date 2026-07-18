"""build-second-source-short-repeatability subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.second_source_short_repeatability import (
    SecondSourceShortRepeatabilityError,
    build_second_source_short_repeatability,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-second-source-short-repeatability",
        description=(
            "Build one declarative second-source 1080x1920 OUT-09 review candidate."
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
        result = build_second_source_short_repeatability(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            candidate_plan_input_path=Path(args.candidate_plan_input),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except SecondSourceShortRepeatabilityError as exc:
        print(f"build-second-source-short-repeatability failed: {exc}", file=sys.stderr)
        return 2

    readback = result["readback"]
    payload = {
        "artifact_id": result["artifact_id"],
        "state": readback["state"],
        "source_provider_id": readback["source_identity"]["provider_id"],
        "duration_seconds": readback["candidate"]["duration_seconds"],
        "subtitle_count": readback["subtitle"]["count"],
        "video": readback["video"]["package_relative_path"],
        "review_entrypoint": readback["review_entrypoint"],
        "machine_readback": readback["machine_readback"],
        "candidate_manifest": readback["candidate_manifest"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            "OUT-09 second-source Short: "
            f"{payload['duration_seconds']:.3f}s / subtitles={payload['subtitle_count']}"
        )
        print(f"Review entrypoint: {payload['review_entrypoint']}")
    return 0
