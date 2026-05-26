"""build-cut-review-packet subcommand: selected cuts -> review JSON/HTML."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.cut_review_packet import (
    CutReviewPacketError,
    build_cut_review_packet,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-cut-review-packet",
        description=(
            "Build machine-readable and human-readable review packets for selected cuts. "
            "This is a review surface only, not final cut or production acceptance."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--edit-pack")
    parser.add_argument("--transcript")
    parser.add_argument("--rights-manifest")
    parser.add_argument("--nle-manifest")
    parser.add_argument("--render-manifest")
    parser.add_argument("--output-dir")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    episode_dir = Path(args.episode_dir)
    edit_pack_path = Path(args.edit_pack) if args.edit_pack else episode_dir / "edit_pack.json"
    transcript_path = Path(args.transcript) if args.transcript else episode_dir / "transcript.json"
    rights_manifest_path = (
        Path(args.rights_manifest) if args.rights_manifest else episode_dir / "rights_manifest.json"
    )
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else episode_dir / "review" / "cut_review_packet"
    )

    try:
        result = build_cut_review_packet(
            episode_dir=episode_dir,
            edit_pack_path=edit_pack_path,
            transcript_path=transcript_path,
            rights_manifest_path=rights_manifest_path,
            nle_manifest_path=Path(args.nle_manifest) if args.nle_manifest else None,
            render_manifest_path=Path(args.render_manifest) if args.render_manifest else None,
            output_dir=output_dir,
            base_dir=Path.cwd(),
        )
    except (OSError, json.JSONDecodeError, CutReviewPacketError) as exc:
        print(f"build-cut-review-packet failed: {exc}", file=sys.stderr)
        return 1

    packet = result["packet"]
    payload = {
        "schema_version": "v1",
        "episode_id": packet["episode_id"],
        "cut_count": packet["summary"]["cut_count"],
        "context_counts": packet["summary"]["context_counts"],
        "production_candidate": packet["summary"]["production_candidate"],
        "rights_status": packet["summary"]["rights_status"],
        "packet": str(result["packet_path"]).replace("\\", "/"),
        "report": str(result["report_path"]).replace("\\", "/"),
        "evidence_summary": str(result["evidence_path"]).replace("\\", "/"),
        "evidence_report": str(result["evidence_report_path"]).replace("\\", "/"),
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"episode_id: {payload['episode_id']}")
        print(f"cut_count: {payload['cut_count']}")
        print(f"context_counts: {json.dumps(payload['context_counts'], ensure_ascii=False)}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(f"rights_status: {payload['rights_status']}")
        print(f"packet: {payload['packet']}")
        print(f"report: {payload['report']}")
        print(f"evidence_summary: {payload['evidence_summary']}")
        print(f"evidence_report: {payload['evidence_report']}")
    return 0
