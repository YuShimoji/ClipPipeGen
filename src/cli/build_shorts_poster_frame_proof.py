"""build-shorts-poster-frame-proof subcommand."""

from __future__ import annotations

import argparse
import json
import sys

from src.integrations.render.shorts_poster_frame_proof import (
    ShortsPosterFrameProofError,
    build_shorts_poster_frame_proof,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-shorts-poster-frame-proof",
        description="Build the ignored local OUT-07 reference-derived 9:16 poster review proof.",
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-video", required=True)
    parser.add_argument("--accepted-video", required=True)
    parser.add_argument("--out07-publish-draft", required=True)
    parser.add_argument("--reference-corpus", required=True)
    parser.add_argument("--reference-cache-dir", required=True)
    parser.add_argument("--fetch-missing-references", action="store_true")
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_shorts_poster_frame_proof(
            episode_dir=args.episode_dir,
            output_dir=args.output_dir,
            source_video_path=args.source_video,
            accepted_video_path=args.accepted_video,
            out07_publish_draft_path=args.out07_publish_draft,
            reference_corpus_path=args.reference_corpus,
            reference_cache_dir=args.reference_cache_dir,
            fetch_missing_references=args.fetch_missing_references,
            ffmpeg_path=args.ffmpeg_path,
            ffprobe_path=args.ffprobe_path,
        )
    except ShortsPosterFrameProofError as exc:
        print(f"build-shorts-poster-frame-proof failed: {exc}", file=sys.stderr)
        return 1
    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["state"],
        "output_dir": str(result["output_dir"]),
        "index_path": str(result["index_path"]),
        "readback_path": str(result["readback_path"]),
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"state: {payload['state']}")
        print(f"index: {payload['index_path']}")
    return 0
