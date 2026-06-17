"""build-subtitle-typography-decoration-comparison subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.subtitle_style_spike import (
    TYPOGRAPHY_COMPARISON_PROFILES,
    build_subtitle_typography_decoration_comparison,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-subtitle-typography-decoration-comparison",
        description=(
            "Build review-only font-family / decoration comparison PNGs for the "
            "diagnostic subtitle route. This is not production subtitle design "
            "acceptance, production render acceptance, rights approval, publishing, "
            "public use, or upload."
        ),
    )
    parser.add_argument("--episode-dir")
    parser.add_argument("--review-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--target-cut", action="append", dest="target_cuts")
    parser.add_argument("--sample-text", action="append", dest="sample_texts")
    parser.add_argument(
        "--comparison-profile",
        choices=TYPOGRAPHY_COMPARISON_PROFILES,
        default="ed10g_typography_decoration",
        help=(
            "Comparison profile to generate. The default preserves the historical "
            "ED-10g artifact; ed10i_kirinuki_gothic_balance creates the narrow "
            "gothic body/outline balance proof; ed10j_kirinuki_font_audit creates "
            "the follow-up normal-dialogue font audit after Meiryo review; "
            "ed10l_known_kirinuki_font_pack creates the route-correction audit "
            "for known Japanese kirinuki/telop fonts after BIZ review."
        ),
    )
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    build_kwargs = {
        "episode_dir": Path(args.episode_dir) if args.episode_dir else None,
        "review_dir": Path(args.review_dir) if args.review_dir else None,
        "target_cut_ids": args.target_cuts,
        "sample_texts": args.sample_texts,
        "canvas_size": (args.width, args.height),
        "base_dir": Path.cwd(),
        "comparison_profile": args.comparison_profile,
    }
    if args.output_dir:
        build_kwargs["output_dir"] = Path(args.output_dir)

    try:
        report = build_subtitle_typography_decoration_comparison(**build_kwargs)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"build-subtitle-typography-decoration-comparison failed: {exc}", file=sys.stderr)
        return 1

    decision_packet = report.get("comparison_decision_packet") or report.get(
        "small_adjustment_decision_packet"
    )
    if not isinstance(decision_packet, dict):
        decision_packet = {}
    payload = {
        "schema_version": "v1",
        "artifact_id": report["artifact_id"],
        "scope": report["scope"],
        "comparison_profile": report["comparison_profile"],
        "target_cuts": report["target_cuts"],
        "sample_count": len(report["samples"]),
        "candidate_count": report["candidate_count"],
        "font_size": report["font_size_policy"],
        "comparison_response": report["comparison_response_readback"],
        "selected_candidate_for_next_proof_base": report[
            "comparison_response_readback"
        ].get("selected_candidate_for_next_proof_base"),
        "next_diagnostic_overlay_proof_route": report[
            "next_diagnostic_overlay_proof_route"
        ],
        "small_adjustment_decision_packet": report.get(
            "small_adjustment_decision_packet",
            decision_packet,
        ),
        "comparison_decision_packet": decision_packet,
        "review_only": report["review_only"],
        "production_candidate": report["production_candidate"],
        "production_subtitle_design_acceptance": report[
            "production_subtitle_design_acceptance"
        ],
        "rights_status": report["rights_status"],
        "outputs": report["outputs"],
        "open_command": report["open_commands"]["open_comparison"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"scope: {payload['scope']}")
        print(f"target_cuts: {', '.join(payload['target_cuts'])}")
        print(f"sample_count: {payload['sample_count']}")
        print(f"candidate_count: {payload['candidate_count']}")
        print(f"font_size_status: {payload['font_size']['status']}")
        print(
            "comparison_response: "
            f"{payload['comparison_response']['selected_response']}"
        )
        print(
            "next_route: "
            f"{payload['next_diagnostic_overlay_proof_route']['route_kind']}"
        )
        print(
            "recommended_default_candidate: "
            f"{decision_packet.get('recommended_default_candidate_id', '')}"
        )
        print(
            "selected_candidate_for_next_proof_base: "
            f"{payload['selected_candidate_for_next_proof_base']}"
        )
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(
            "production_subtitle_design_acceptance: "
            f"{str(payload['production_subtitle_design_acceptance']).lower()}"
        )
        print(f"rights_status: {payload['rights_status']}")
        print(f"report: {payload['outputs']['json']}")
        print(f"report_html: {payload['outputs']['html']}")
        print(f"contact_sheet: {payload['outputs']['contact_sheet']}")
        print(f"open_command: {payload['open_command']}")
    return 0
