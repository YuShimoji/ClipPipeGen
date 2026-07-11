"""build-editorial-sequence subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.editorial_sequence import (
    EditorialSequenceError,
    build_editorial_sequence,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-editorial-sequence",
        description="Build one real-local two/three-cut OUT-04 editorial review sequence.",
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--cut-id",
        action="append",
        required=True,
        dest="cut_ids",
        help="Cut ID in editorial order; repeat two or three times.",
    )
    parser.add_argument("--cut-decision-readback", required=True)
    parser.add_argument("--source-video-material-id", required=True)
    parser.add_argument("--source-audio-material-id", required=True)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_editorial_sequence(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            cut_ids=args.cut_ids,
            cut_decision_readback_path=Path(args.cut_decision_readback),
            source_video_material_id=args.source_video_material_id,
            source_audio_material_id=args.source_audio_material_id,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except EditorialSequenceError as exc:
        print(f"build-editorial-sequence failed: {exc}", file=sys.stderr)
        return 2
    payload = {
        "artifact_id": result["artifact_id"],
        "ordered_cut_ids": result["readback"]["ordered_cut_ids"],
        "duration_seconds": result["readback"]["render"]["media"]["duration_seconds"],
        "video": result["readback"]["render"]["output_path"],
        "review_entrypoint": result["readback"]["review_entrypoint"],
        "machine_readback": result["readback"]["machine_readback"],
        "open_command": result["readback"]["open_command"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"OUT-04 sequence: {payload['video']}")
        print(f"Review entrypoint: {payload['review_entrypoint']}")
        print(f"Open: {payload['open_command']}")
    return 0
