"""Build one private evidence-linked multi-source comparison artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.evidence_linked_comparison import (
    DEFAULT_REVIEW_PORT,
    EvidenceLinkedComparisonError,
    build_evidence_linked_comparison,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-evidence-linked-comparison",
        description=(
            "Bind two or three local source records to concurrent comparison "
            "beats, one foreground speech owner, and a private review package."
        ),
    )
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--direction", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--review-port", type=int, default=DEFAULT_REVIEW_PORT)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_evidence_linked_comparison(
            plan_path=args.plan,
            direction_path=args.direction,
            output_dir=args.output_dir,
            review_port=args.review_port,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except EvidenceLinkedComparisonError as exc:
        print(
            f"build-evidence-linked-comparison failed at {exc.stage}: {exc}",
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
            f"{result['beat_count']} comparison beats"
        )
        print(f"sha256: {result['final_video_sha256']}")
        print(f"video: {result['final_video']}")
        print(f"review: {result['review_index']}")
    return 0
