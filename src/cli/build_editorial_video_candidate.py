"""Build the OUT-13 caption-evidence-bound editorial video candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.editorial_video_candidate import (
    DEFAULT_REVIEW_PORT,
    EditorialVideoCandidateError,
    build_editorial_video_candidate,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-editorial-video-candidate",
        description=(
            "Apply one explicit caption/transcript-evidence editorial plan to a real "
            "source, burn readable sidecar subtitles, validate the MP4, and build a "
            "single video-first review package."
        ),
    )
    parser.add_argument(
        "--artifact-id",
        required=True,
        help="Immutable OUT-13 candidate identity (for example ...-002).",
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-identity", required=True)
    parser.add_argument("--editorial-plan", required=True, type=Path)
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--caption-track", required=True, type=Path)
    parser.add_argument("--rights-manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    behavior = parser.add_mutually_exclusive_group()
    behavior.add_argument("--resume", action="store_true")
    behavior.add_argument("--force", action="store_true")
    parser.add_argument("--review-port", type=int, default=DEFAULT_REVIEW_PORT)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_editorial_video_candidate(
            artifact_id=args.artifact_id,
            source_path=args.source,
            source_identity=args.source_identity,
            editorial_plan_path=args.editorial_plan,
            transcript_path=args.transcript,
            caption_track_path=args.caption_track,
            rights_manifest_path=args.rights_manifest,
            output_dir=args.output_dir,
            resume=args.resume,
            force=args.force,
            review_port=args.review_port,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except EditorialVideoCandidateError as exc:
        print(
            f"build-editorial-video-candidate failed at {exc.stage}: {exc}",
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
            f"{result['duration_seconds']:.3f}s / {result['cut_count']} cuts / "
            f"{result['omitted_span_count']} omitted{cache}"
        )
        print(f"video: {result['final_video']}")
        print(f"review: {result['review_index']}")
    return 0
