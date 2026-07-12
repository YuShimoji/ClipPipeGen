"""build-operator-delivery-pack subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.operator_delivery_pack import (
    OperatorDeliveryPackError,
    build_operator_delivery_pack,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-operator-delivery-pack",
        description="Build one OUT-07 internal operator delivery pack from accepted OUT-06.",
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--out06-readback", required=True)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_operator_delivery_pack(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            out06_readback_path=Path(args.out06_readback),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except OperatorDeliveryPackError as exc:
        print(f"build-operator-delivery-pack failed: {exc}", file=sys.stderr)
        return 2
    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["readback"]["state"],
        "review_entrypoint": result["readback"]["review_entrypoint"],
        "operator_delivery_readback": result["readback"]["operator_delivery_readback"],
        "delivery_manifest": result["readback"]["delivery_manifest"],
        "recommended_thumbnail": result["readback"]["thumbnail"]["recommended"]["path"],
        "video_sha256": result["readback"]["video"]["packaged_sha256"],
        "open_command": result["readback"]["open_command"],
        "serve_command": result["readback"]["serve_command"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"OUT-07 operator delivery pack: {payload['review_entrypoint']}")
        print(f"Recommended thumbnail: {payload['recommended_thumbnail']}")
        print(f"Open: {payload['open_command']}")
    return 0
