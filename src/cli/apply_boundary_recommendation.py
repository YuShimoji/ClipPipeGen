"""apply-boundary-recommendation subcommand: ED-10e safe boundary preflight."""

from __future__ import annotations

import argparse
import json
import sys

from src.pipeline.boundary_recommendation_apply import (
    BoundaryRecommendationApplyError,
    build_boundary_recommendation_receipt,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="apply-boundary-recommendation",
        description=(
            "Validate a cut boundary recommendation against edit_pack and write "
            "a dry-run/blocking receipt. ED-10e does not mutate edit_pack."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--edit-pack", required=True)
    parser.add_argument("--recommendation-report", required=True)
    parser.add_argument("--cut-id", required=True)
    parser.add_argument("--output-receipt", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        receipt = build_boundary_recommendation_receipt(
            episode_dir=args.episode_dir,
            edit_pack_path=args.edit_pack,
            recommendation_report_path=args.recommendation_report,
            cut_id=args.cut_id,
            output_receipt_path=args.output_receipt,
            dry_run=args.dry_run,
        )
    except BoundaryRecommendationApplyError as exc:
        print(f"apply-boundary-recommendation failed: {exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"apply-boundary-recommendation failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "status": receipt["status"],
        "dry_run": receipt["dry_run"],
        "cut_id": receipt["cut_id"],
        "source_recommendation_report": receipt["source_recommendation_report"],
        "previous_start_seconds": receipt["previous_start_seconds"],
        "previous_end_seconds": receipt["previous_end_seconds"],
        "requested_start_seconds": receipt["requested_start_seconds"],
        "requested_end_seconds": receipt["requested_end_seconds"],
        "conflicting_cut_ids": receipt["conflict_detection"]["conflicting_cut_ids"],
        "proof_stale_or_requires_regeneration": receipt[
            "proof_stale_or_requires_regeneration"
        ],
        "production_candidate": receipt["production_candidate"],
        "rights_status": receipt["rights_status"],
        "production_usage_allowed": receipt["production_usage_allowed"],
        "outputs": receipt.get("outputs") or {},
    }

    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"status: {payload['status']}")
        print(f"cut_id: {payload['cut_id']}")
        print(
            "requested_range: "
            f"{payload['requested_start_seconds']} -> {payload['requested_end_seconds']}"
        )
        print(
            "conflicting_cut_ids: "
            + (", ".join(payload["conflicting_cut_ids"]) or "none")
        )
        print(f"json_receipt: {payload['outputs'].get('json_receipt', '')}")
        print(f"html_receipt: {payload['outputs'].get('html_receipt', '')}")

    return 0
