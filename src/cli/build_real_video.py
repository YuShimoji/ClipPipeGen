"""Run the reusable OUT-12 real-video automation pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.real_video_pipeline import (
    RealVideoPipelineError,
    build_real_video,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-real-video",
        description=(
            "Resolve one real source, build a chronological long-form Timeline IR, "
            "render/validate an MP4, and create a localhost review package."
        ),
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source", type=Path)
    source.add_argument(
        "--intake-identity",
        help="Existing intake as <episode-dir>#<source-video-material-id>.",
    )
    parser.add_argument("--source-identity")
    parser.add_argument("--rights-manifest", type=Path)
    parser.add_argument("--caption-track", type=Path)
    parser.add_argument("--authority-readback", type=Path)
    parser.add_argument(
        "--caption-mode",
        choices=("auto", "native", "sidecar", "none"),
        default="auto",
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--profile", choices=("long-form",), default="long-form")
    parser.add_argument("--target-duration", type=float, default=300.0)
    behavior = parser.add_mutually_exclusive_group()
    behavior.add_argument("--resume", action="store_true")
    behavior.add_argument("--force", action="store_true")
    parser.add_argument("--review-port", type=int, default=8075)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_real_video(
            source_path=args.source,
            intake_identity=args.intake_identity,
            source_identity=args.source_identity,
            rights_manifest_path=args.rights_manifest,
            caption_track_path=args.caption_track,
            authority_readback_path=args.authority_readback,
            caption_mode=args.caption_mode,
            output_dir=args.output_dir,
            profile=args.profile,
            target_duration_seconds=args.target_duration,
            resume=args.resume,
            force=args.force,
            review_port=args.review_port,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except RealVideoPipelineError as exc:
        print(
            f"build-real-video failed at {exc.stage}: {exc}",
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
        cache = " / resume cache hit" if result.get("resume") else ""
        print(
            f"{result['state']}: {result['source_identity']} -> "
            f"{result['duration_seconds']:.3f}s / {result['cut_count']} cuts{cache}"
        )
        print(f"video: {result['final_video']}")
        print(f"review: {result['review_index']}")
    return 0

