"""build-out07-direction-proxy subcommand."""

from __future__ import annotations

import argparse
import json
import sys

from src.integrations.render.out07_direction_proxy import (
    Out07DirectionProxyError,
    build_out07_direction_proxy,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-out07-direction-proxy",
        description=(
            "Build one Thank-source native Shorts cover direction proxy without "
            "weakening the exact accepted-baseline route."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--verify-determinism", action="store_true")
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_out07_direction_proxy(
            episode_dir=args.episode_dir,
            output_dir=args.output_dir,
            verify_determinism=args.verify_determinism,
            ffmpeg_path=args.ffmpeg_path,
            ffprobe_path=args.ffprobe_path,
        )
    except Out07DirectionProxyError as exc:
        print(f"build-out07-direction-proxy failed: {exc}", file=sys.stderr)
        return 1
    payload = {
        "artifact_id": result["artifact_id"],
        "evidence_revision": result["evidence_revision"],
        "state": result["state"],
        "output_dir": str(result["output_dir"]),
        "index_path": str(result["index_path"]),
        "readback_path": str(result["readback_path"]),
        "manifest_path": str(result["manifest_path"]),
        "proxy_path": str(result["proxy_path"]),
        "proxy_classification": result["proxy_classification"],
        "proxy_sha256": result["proxy_sha256"],
        "deterministic_core_digest": result["deterministic_core_digest"],
        "package_digest": result["package_digest"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"evidence_revision: {payload['evidence_revision']}")
        print(f"state: {payload['state']}")
        print(f"classification: {payload['proxy_classification']}")
        print(f"review: {payload['index_path']}")
    return 0
