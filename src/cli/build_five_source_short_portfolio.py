"""Build the OUT-11 five-source scorecard and combined review package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.five_source_short_portfolio import (
    FiveSourceShortPortfolioError,
    build_five_source_short_portfolio,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-five-source-short-portfolio",
        description="Build the exact three-video OUT-11 combined review package.",
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_five_source_short_portfolio(
            config_path=Path(args.config),
            output_dir=Path(args.output_dir),
            base_dir=Path.cwd(),
        )
    except FiveSourceShortPortfolioError as exc:
        print(f"build-five-source-short-portfolio failed: {exc}", file=sys.stderr)
        return 2

    readback = result["readback"]
    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["state"],
        "review_entrypoint": readback["review_entrypoint"],
        "candidate_count": len(readback["review_candidates"]),
        "scorecard_row_count": readback["scorecard"]["row_count"],
        "output_dir": str(result["output_dir"]),
        "readback": str(result["readback_path"]),
        "manifest": str(result["manifest_path"]),
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"OUT-11 combined review: {payload['candidate_count']} videos / "
            f"{payload['scorecard_row_count']} scorecard rows"
        )
        print(f"Review entrypoint: {payload['review_entrypoint']}")
    return 0
