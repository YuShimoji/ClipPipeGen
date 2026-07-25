"""Build the bounded S1 two-source common-context internal probe."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.common_context_probe import (
    CommonContextProbeError,
    build_common_context_probe,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-common-context-probe",
        description=(
            "Bind exactly two existing real sources to an evidence-grounded "
            "argument timeline, render one internal MP4, and create a "
            "video-first localhost review package."
        ),
    )
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--design-basis", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--review-port", type=int, default=8077)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_common_context_probe(
            plan_path=args.plan,
            design_basis_path=args.design_basis,
            output_dir=args.output_dir,
            review_port=args.review_port,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except CommonContextProbeError as exc:
        print(
            f"build-common-context-probe failed at {exc.stage}: {exc}",
            file=sys.stderr,
        )
        return 2
    payload = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in result.items()
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"{result['state']}: {result['duration_seconds']:.3f}s / "
            f"{result['cut_count']} cuts / "
            f"{result['source_switch_count']} source switches"
        )
        print(f"video: {result['final_video']}")
        print(f"review: {result['review_index']}")
    return 0
