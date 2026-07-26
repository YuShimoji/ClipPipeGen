"""CLI for OUT-14 editorial presentation reconstruction v3."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.push_microarc_editorial_v3 import (
    ARTIFACT_ID,
    DEFAULT_REVIEW_PORT,
    PushMicroarcEditorialV3Error,
    build_push_microarc_editorial_v3,
    finalize_full_view_self_review,
    render_probe_candidate,
)


def _serializable(value: dict) -> dict:
    return {
        key: str(item) if isinstance(item, Path) else item
        for key, item in value.items()
    }


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="build-push-microarc-editorial-v3")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(target: argparse.ArgumentParser) -> None:
        target.add_argument("--source", required=True, type=Path)
        target.add_argument("--v2-reference-dir", required=True, type=Path)
        target.add_argument("--v2-final-video", required=True, type=Path)
        target.add_argument("--design-basis", required=True, type=Path)
        target.add_argument("--output-dir", required=True, type=Path)
        target.add_argument("--ffmpeg")
        target.add_argument("--ffprobe")

    probe = subparsers.add_parser("probe")
    add_common(probe)

    build = subparsers.add_parser("build")
    add_common(build)
    build.add_argument("--artifact-id", default=ARTIFACT_ID)
    build.add_argument("--review-port", type=int, default=DEFAULT_REVIEW_PORT)

    finalize = subparsers.add_parser("finalize-full-view")
    finalize.add_argument("--artifact-dir", required=True, type=Path)
    finalize.add_argument("--played-duration-seconds", required=True, type=float)
    finalize.add_argument("--ended-event-observed", action="store_true")
    finalize.add_argument("--checkpoint-count", required=True, type=int)

    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        if args.command == "probe":
            result = render_probe_candidate(
                source_path=args.source,
                v2_reference_dir=args.v2_reference_dir,
                v2_final_video_path=args.v2_final_video,
                design_basis_path=args.design_basis,
                output_dir=args.output_dir,
                ffmpeg_path=args.ffmpeg,
                ffprobe_path=args.ffprobe,
            )
        elif args.command == "build":
            result = build_push_microarc_editorial_v3(
                artifact_id=args.artifact_id,
                source_path=args.source,
                v2_reference_dir=args.v2_reference_dir,
                v2_final_video_path=args.v2_final_video,
                design_basis_path=args.design_basis,
                output_dir=args.output_dir,
                review_port=args.review_port,
                ffmpeg_path=args.ffmpeg,
                ffprobe_path=args.ffprobe,
            )
        else:
            result = finalize_full_view_self_review(
                artifact_dir=args.artifact_dir,
                played_duration_seconds=args.played_duration_seconds,
                ended_event_observed=args.ended_event_observed,
                checkpoint_count=args.checkpoint_count,
            )
    except PushMicroarcEditorialV3Error as exc:
        print(f"v3 failed at {exc.stage}: {exc}", file=sys.stderr)
        return 1
    serializable = _serializable(result)
    if args.format == "json":
        json.dump(serializable, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        for key, value in serializable.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
