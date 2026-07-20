"""Build one hash-bound OUT-11 source-adaptive Short candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.source_adaptive_short_candidate import (
    SourceAdaptiveShortCandidateError,
    build_source_adaptive_short_candidate,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-source-adaptive-short-candidate",
        description="Build one endpoint-bound real-source vertical review candidate.",
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--candidate-plan-input", required=True)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_source_adaptive_short_candidate(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            candidate_plan_input_path=Path(args.candidate_plan_input),
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
            base_dir=Path.cwd(),
        )
    except SourceAdaptiveShortCandidateError as exc:
        print(f"build-source-adaptive-short-candidate failed: {exc}", file=sys.stderr)
        return 2

    readback = result["readback"]
    payload = {
        "artifact_id": result["artifact_id"],
        "state": readback["state"],
        "source_identity": readback["source_identity"]["identity"],
        "duration_seconds": readback["candidate"]["duration_seconds"],
        "caption_mode": readback["caption"]["mode"],
        "video_sha256": readback["video"]["sha256"],
        "output_dir": str(result["output_dir"]),
        "readback": str(result["readback_path"]),
        "manifest": str(result["manifest_path"]),
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"source-adaptive candidate: {payload['source_identity']} / "
            f"{payload['duration_seconds']:.3f}s / {payload['caption_mode']}"
        )
    return 0
