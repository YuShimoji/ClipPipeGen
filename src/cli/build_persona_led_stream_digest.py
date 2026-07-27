"""Build the bounded S1 persona-led Oozora Subaru stream digest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.persona_led_stream_digest import (
    DEFAULT_REVIEW_PORT,
    PersonaLedStreamDigestError,
    build_persona_led_stream_digest,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-persona-led-stream-digest",
        description=(
            "Bind the fixed 2026-07-18/2026-07-25 Oozora Subaru ordinary-stream "
            "pair to a concept-first private-review digest."
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
        result = build_persona_led_stream_digest(
            plan_path=args.plan,
            direction_path=args.direction,
            output_dir=args.output_dir,
            review_port=args.review_port,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except PersonaLedStreamDigestError as exc:
        print(
            f"build-persona-led-stream-digest failed at {exc.stage}: {exc}",
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
        print(f"sha256: {result['final_video_sha256']}")
        print(f"video: {result['final_video']}")
        print(f"review: {result['review_index']}")
    return 0
