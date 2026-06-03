"""build-operator-proxy-decision-handoff subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.operator_proxy_decision_handoff import (
    OperatorProxyDecisionHandoffError,
    build_operator_proxy_decision_handoff,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-operator-proxy-decision-handoff",
        description=(
            "Build cut-scoped text/proxy review and operator decision handoff "
            "artifacts. This is not visual proof, rendering, production "
            "acceptance, or rights approval."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--review-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--target-cut", action="append", dest="target_cuts")
    parser.add_argument("--edit-pack")
    parser.add_argument("--material-ledger")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_operator_proxy_decision_handoff(
            episode_dir=Path(args.episode_dir),
            review_dir=Path(args.review_dir) if args.review_dir else None,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            target_cut_ids=args.target_cuts,
            edit_pack_path=Path(args.edit_pack) if args.edit_pack else None,
            material_ledger_path=Path(args.material_ledger) if args.material_ledger else None,
            base_dir=Path.cwd(),
        )
    except (OSError, json.JSONDecodeError, OperatorProxyDecisionHandoffError) as exc:
        print(f"build-operator-proxy-decision-handoff failed: {exc}", file=sys.stderr)
        return 1

    handoff = result["handoff"]
    boundary = handoff.get("boundary_flags") or {}
    source_media = handoff.get("source_media_status") or {}
    payload = {
        "schema_version": "v1",
        "episode_id": handoff.get("episode_id"),
        "scope": handoff.get("scope"),
        "target_cuts": handoff.get("target_cuts") or [],
        "source_media_status": source_media.get("status"),
        "visual_proof_status": handoff.get("visual_proof_status"),
        "production_candidate": boundary.get("production_candidate"),
        "creative_acceptance": boundary.get("creative_acceptance"),
        "publish_acceptance": boundary.get("publish_acceptance"),
        "rights_status": boundary.get("rights_status"),
        "production_usage_allowed": boundary.get("production_usage_allowed"),
        "text_review": str(result["text_review_path"]).replace("\\", "/"),
        "text_review_html": str(result["text_review_html_path"]).replace("\\", "/"),
        "handoff": str(result["handoff_path"]).replace("\\", "/"),
        "handoff_html": str(result["handoff_html_path"]).replace("\\", "/"),
        "patch_template": str(result["patch_template_path"]).replace("\\", "/"),
        "patch_csv": str(result["patch_csv_path"]).replace("\\", "/"),
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"episode_id: {payload['episode_id']}")
        print(f"scope: {payload['scope']}")
        print(f"target_cuts: {', '.join(payload['target_cuts'])}")
        print(f"source_media_status: {payload['source_media_status']}")
        print(f"visual_proof_status: {payload['visual_proof_status']}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(f"creative_acceptance: {str(payload['creative_acceptance']).lower()}")
        print(f"publish_acceptance: {str(payload['publish_acceptance']).lower()}")
        print(f"rights_status: {payload['rights_status']}")
        print(f"production_usage_allowed: {str(payload['production_usage_allowed']).lower()}")
        print(f"text_review: {payload['text_review']}")
        print(f"text_review_html: {payload['text_review_html']}")
        print(f"handoff: {payload['handoff']}")
        print(f"handoff_html: {payload['handoff_html']}")
        print(f"patch_template: {payload['patch_template']}")
        print(f"patch_csv: {payload['patch_csv']}")
    return 0
