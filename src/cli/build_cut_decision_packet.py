"""build-cut-decision-packet subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.cut_decision_packet import (
    CutDecisionPacketError,
    build_cut_decision_packet,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-cut-decision-packet",
        description=(
            "Classify JP-Pilot R3 selected cuts into keep / reject / needs_adjustment. "
            "This is candidate triage only, not production acceptance."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--review-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--cut-review-packet")
    parser.add_argument("--edit-pack")
    parser.add_argument("--transcript")
    parser.add_argument("--render-manifest")
    parser.add_argument("--nle-manifest")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    episode_dir = Path(args.episode_dir)
    review_dir = (
        Path(args.review_dir)
        if args.review_dir
        else episode_dir / "review" / "jp_pilot01r3_cut_review"
    )
    try:
        result = build_cut_decision_packet(
            episode_dir=episode_dir,
            review_dir=review_dir,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            cut_review_packet_path=Path(args.cut_review_packet)
            if args.cut_review_packet
            else None,
            edit_pack_path=Path(args.edit_pack) if args.edit_pack else None,
            transcript_path=Path(args.transcript) if args.transcript else None,
            render_manifest_path=Path(args.render_manifest) if args.render_manifest else None,
            nle_manifest_path=Path(args.nle_manifest) if args.nle_manifest else None,
            base_dir=Path.cwd(),
        )
    except (OSError, json.JSONDecodeError, CutDecisionPacketError) as exc:
        print(f"build-cut-decision-packet failed: {exc}", file=sys.stderr)
        return 1

    packet = result["packet"]
    summary = packet.get("summary") or {}
    payload = {
        "schema_version": "v1",
        "episode_id": packet.get("episode_id"),
        "decision_policy": packet.get("decision_policy"),
        "decision_scope": packet.get("decision_scope"),
        "decision_counts": summary.get("decision_counts"),
        "keep_cut_ids": summary.get("keep_cut_ids"),
        "needs_adjustment_cut_ids": summary.get("needs_adjustment_cut_ids"),
        "reject_cut_ids": summary.get("reject_cut_ids"),
        "kept_needs_review_cut_ids": summary.get("kept_needs_review_cut_ids"),
        "production_candidate": packet.get("production_candidate"),
        "rights_status": packet.get("rights_status"),
        "packet": str(result["packet_path"]).replace("\\", "/"),
        "report": str(result["report_path"]).replace("\\", "/"),
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"episode_id: {payload['episode_id']}")
        print(f"decision_policy: {payload['decision_policy']}")
        print(f"decision_counts: {json.dumps(payload['decision_counts'], ensure_ascii=False)}")
        print(f"keep_cut_ids: {', '.join(payload['keep_cut_ids'] or [])}")
        print(
            "needs_adjustment_cut_ids: "
            + ", ".join(payload["needs_adjustment_cut_ids"] or [])
        )
        print(f"reject_cut_ids: {', '.join(payload['reject_cut_ids'] or [])}")
        print(
            "kept_needs_review_cut_ids: "
            + ", ".join(payload["kept_needs_review_cut_ids"] or [])
        )
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(f"rights_status: {payload['rights_status']}")
        print(f"packet: {payload['packet']}")
        print(f"report: {payload['report']}")
    return 0
