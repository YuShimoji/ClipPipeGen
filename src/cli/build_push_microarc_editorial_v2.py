"""CLI for the OUT-14 editorial reconstruction v2 profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.push_microarc_editorial_v2 import (
    DEFAULT_REVIEW_PORT,
    PushMicroarcEditorialV2Error,
    build_push_microarc_editorial_v2,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="build-push-microarc-editorial-v2")
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-identity", required=True)
    parser.add_argument("--source-receipt", required=True, type=Path)
    parser.add_argument("--material-ledger", required=True, type=Path)
    parser.add_argument("--rights-manifest", required=True, type=Path)
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--competitive-scan", required=True, type=Path)
    parser.add_argument("--canonical-transcript", required=True, type=Path)
    parser.add_argument("--provider-caption", required=True, type=Path)
    parser.add_argument("--human-decision", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--review-port", type=int, default=DEFAULT_REVIEW_PORT)
    parser.add_argument("--source-media-offset-seconds", type=float, default=0.0)
    parser.add_argument("--pre-rendered-video", type=Path)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_push_microarc_editorial_v2(
            artifact_id=args.artifact_id,
            source_path=args.source,
            source_identity=args.source_identity,
            source_receipt_path=args.source_receipt,
            material_ledger_path=args.material_ledger,
            rights_manifest_path=args.rights_manifest,
            selection_path=args.selection,
            competitive_scan_path=args.competitive_scan,
            canonical_transcript_path=args.canonical_transcript,
            provider_caption_path=args.provider_caption,
            human_decision_path=args.human_decision,
            output_dir=args.output_dir,
            review_port=args.review_port,
            source_media_offset_seconds=args.source_media_offset_seconds,
            pre_rendered_video_path=args.pre_rendered_video,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
        )
    except PushMicroarcEditorialV2Error as exc:
        print(
            f"build-push-microarc-editorial-v2 failed at {exc.stage}: {exc}",
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
