"""CLI entrypoint for the OUT-14 Push Micro-Arc stream profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.push_microarc_stream import (
    DEFAULT_REVIEW_PORT,
    PushMicroarcStreamError,
    build_push_microarc_stream,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-push-microarc-stream",
        description=(
            "Build one 5-15 minute closed Push Micro-Arc from a completed "
            "public stream archive, with traceable captions, media validation, "
            "and a video-first localhost review package."
        ),
    )
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-identity", required=True)
    parser.add_argument("--editorial-plan", required=True, type=Path)
    parser.add_argument("--caption-track", required=True, type=Path)
    parser.add_argument("--caption-receipt", required=True, type=Path)
    parser.add_argument("--source-info", required=True, type=Path)
    parser.add_argument("--source-receipt", required=True, type=Path)
    parser.add_argument("--source-audio-receipt", required=True, type=Path)
    parser.add_argument("--material-ledger", required=True, type=Path)
    parser.add_argument("--rights-manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--review-port", type=int, default=DEFAULT_REVIEW_PORT)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_push_microarc_stream(
            artifact_id=args.artifact_id,
            source_path=args.source,
            plan_path=args.editorial_plan,
            caption_track_path=args.caption_track,
            caption_receipt_path=args.caption_receipt,
            source_info_path=args.source_info,
            source_receipt_path=args.source_receipt,
            source_audio_receipt_path=args.source_audio_receipt,
            material_ledger_path=args.material_ledger,
            rights_manifest_path=args.rights_manifest,
            output_dir=args.output_dir,
            source_identity=args.source_identity,
            review_port=args.review_port,
            resume=args.resume,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
        )
    except PushMicroarcStreamError as exc:
        print(
            f"build-push-microarc-stream failed at {exc.stage}: {exc}",
            file=sys.stderr,
        )
        return 1
    serializable = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in result.items()
    }
    if args.format == "json":
        json.dump(serializable, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        for key, value in serializable.items():
            print(f"{key}: {value}")
    return 0
