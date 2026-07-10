"""build-selected-cut-proof subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.ffmpeg_tiny import TinyRenderError
from src.integrations.render.selected_cut_proof import (
    SelectedCutProofError,
    build_selected_cut_proof,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-selected-cut-proof",
        description=(
            "Build one real-local selected-cut review proof from existing "
            "episode artifacts and a validated diagnostic proof video. This "
            "does not fetch media, approve rights, or create production/public output."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cut-id", required=True)
    parser.add_argument("--proof-video", required=True)
    parser.add_argument("--proof-source-readback", required=True)
    parser.add_argument(
        "--source-video-material-id",
        default="src_video_jp_pilot01",
    )
    parser.add_argument(
        "--source-audio-material-id",
        default="src_audio_jp_pilot01",
    )
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_selected_cut_proof(
            episode_dir=Path(args.episode_dir),
            output_dir=Path(args.output_dir),
            cut_id=args.cut_id,
            proof_video_path=Path(args.proof_video),
            proof_source_readback_path=Path(args.proof_source_readback),
            source_video_material_id=args.source_video_material_id,
            source_audio_material_id=args.source_audio_material_id,
            ffprobe_path=args.ffprobe_path,
            base_dir=Path.cwd(),
        )
    except (
        OSError,
        json.JSONDecodeError,
        SelectedCutProofError,
        TinyRenderError,
    ) as exc:
        print(f"build-selected-cut-proof failed: {exc}", file=sys.stderr)
        return 1

    readback = result["readback"]
    payload = {
        "artifact_id": readback["artifact_id"],
        "state": readback["state"],
        "source_class": readback["source_class"],
        "selected_cut": readback["selected_cut"],
        "transcript": readback["transcript"],
        "proof": readback["proof"],
        "boundaries": readback["boundaries"],
        "review_entrypoint": readback["review_entrypoint"],
        "machine_readback": readback["machine_readback"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"state: {payload['state']}")
        print(f"source_class: {payload['source_class']}")
        print(f"cut_id: {payload['selected_cut']['id']}")
        print(f"review_entrypoint: {payload['review_entrypoint']}")
        print(f"machine_readback: {payload['machine_readback']}")
        print("production_candidate: false")
        print("public_ready: false")
    return 0
