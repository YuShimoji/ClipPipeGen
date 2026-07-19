"""build-third-source-short-portfolio subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.third_source_short_portfolio import (
    ThirdSourceShortPortfolioError,
    build_third_source_short_portfolio,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-third-source-short-portfolio",
        description=(
            "Build one bounded third-source OUT-10 review candidate and a "
            "three-source scorecard."
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
        result = build_third_source_short_portfolio(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            candidate_plan_input_path=Path(args.candidate_plan_input),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except ThirdSourceShortPortfolioError as exc:
        print(f"build-third-source-short-portfolio failed: {exc}", file=sys.stderr)
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
        "portfolio_scorecard": readback["portfolio_scorecard"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            "OUT-10 third-source Short: "
            f"{payload['duration_seconds']:.3f}s / subtitles={payload['subtitle_count']}"
        )
        print(f"Review entrypoint: {payload['review_entrypoint']}")
    return 0
