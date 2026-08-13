"""build-generated-video-challenge subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.generated_video_challenge import (
    GeneratedVideoChallengeError,
    build_generated_video_challenge,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-generated-video-challenge",
        description=(
            "Build one source-bound 30-90 second internal generated-video challenge "
            "without substituting for unavailable review artifacts."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_generated_video_challenge(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            base_dir=Path(args.repo_root),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
        )
    except GeneratedVideoChallengeError as exc:
        print(f"build-generated-video-challenge failed: {exc}", file=sys.stderr)
        return 2
    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["state"],
        "source_identity": result["source_identity"],
        "duration_seconds": result["duration_seconds"],
        "video_path": str(result["video_path"]),
        "video_sha256": result["video_sha256"],
        "review_entrypoint": str(result["review_entrypoint"]),
        "serve_command": result["serve_command"],
        "open_command": result["open_command"],
        "manifest_path": str(result["manifest_path"]),
        "validation_path": str(result["validation_path"]),
        "receipt_path": str(result["receipt_path"]),
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Generated video challenge: {payload['video_path']}")
        print(f"Review entrypoint: {payload['review_entrypoint']}")
        print(f"MP4 SHA-256: {payload['video_sha256']}")
        print(f"Serve: {payload['serve_command']}")
    return 0
