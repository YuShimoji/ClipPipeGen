"""build-subtitle-overlay-visual-proof subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.subtitle_overlay_visual_proof import (
    SubtitleOverlayVisualProofError,
    build_subtitle_overlay_visual_proof,
    subtitle_overlay_proof_profiles,
    typography_decoration_candidate_ids,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-subtitle-overlay-visual-proof",
        description=(
            "Build cut-scoped diagnostic subtitle-overlay visual proof under a "
            "review directory. This is not production render, subtitle design "
            "acceptance, creative acceptance, publishing acceptance, or rights approval."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--review-dir", required=True)
    parser.add_argument("--target-cut", action="append", dest="target_cuts", required=True)
    parser.add_argument("--edit-pack")
    parser.add_argument("--material-ledger")
    parser.add_argument("--source-video-material-id", default="src_video_jp_pilot01")
    parser.add_argument("--source-audio-material-id", default="src_audio_jp_pilot01")
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--container", choices=("mp4", "mkv"), default="mp4")
    parser.add_argument(
        "--typography-decoration-candidate-id",
        choices=typography_decoration_candidate_ids(),
        help=(
            "Optional ED-10g/ED-10i typography/decoration candidate to apply "
            "to the diagnostic overlay proof. Omit to keep the legacy overlay "
            "style."
        ),
    )
    parser.add_argument(
        "--proof-profile",
        choices=subtitle_overlay_proof_profiles(),
        default="default",
        help=(
            "Optional proof metadata profile. Use "
            "ed10p_keifont_lead_representative_proof to consume the ED-10o "
            "review-surface acceptance and produce the next Keifont lead proof."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_subtitle_overlay_visual_proof(
            episode_dir=Path(args.episode_dir),
            review_dir=Path(args.review_dir),
            target_cut_ids=args.target_cuts,
            edit_pack_path=Path(args.edit_pack) if args.edit_pack else None,
            material_ledger_path=Path(args.material_ledger) if args.material_ledger else None,
            source_video_material_id=args.source_video_material_id,
            source_audio_material_id=args.source_audio_material_id,
            ffmpeg_path=args.ffmpeg_path,
            ffprobe_path=args.ffprobe_path,
            container=args.container,
            typography_decoration_candidate_id=args.typography_decoration_candidate_id,
            proof_profile=args.proof_profile,
            dry_run=args.dry_run,
            base_dir=Path.cwd(),
        )
    except (OSError, json.JSONDecodeError, SubtitleOverlayVisualProofError) as exc:
        print(f"build-subtitle-overlay-visual-proof failed: {exc}", file=sys.stderr)
        return 1

    report = result["report"]
    payload = {
        "schema_version": "v1",
        "episode_id": report.get("episode_id"),
        "artifact_id": report.get("artifact_id"),
        "proof_profile": report.get("proof_profile"),
        "source_review_artifact_id": report.get("source_review_artifact_id"),
        "scope": report.get("scope"),
        "target_cuts": report.get("target_cuts") or [],
        "dry_run": result["dry_run"],
        "source_media_status": report.get("source_media_status"),
        "visual_proof_status": result["visual_proof_status"],
        "style_direction_preset": (
            (report.get("style_direction") or {}).get("preset_name")
        ),
        "style_candidate_id": (
            (report.get("style_parameters") or {}).get("style_candidate_id")
        ),
        "typography_decoration_candidate_id": (
            (report.get("style_parameters") or {}).get(
                "typography_decoration_candidate_id"
            )
        ),
        "subtitle_overlay_available_count": (
            report.get("aggregate_summary") or {}
        ).get("subtitle_overlay_available_count"),
        "focused_proof_review": report.get("focused_proof_review"),
        "review_debt": report.get("review_debt", []),
        "production_candidate": report.get("production_candidate"),
        "creative_acceptance": report.get("creative_acceptance"),
        "publish_acceptance": report.get("publish_acceptance"),
        "rights_status": report.get("rights_status"),
        "production_usage_allowed": report.get("production_usage_allowed"),
        "report": str(result["report_path"]).replace("\\", "/"),
        "report_html": str(result["report_html_path"]).replace("\\", "/"),
        "focused_review_html": str(result["focused_review_html_path"]).replace(
            "\\", "/"
        ),
        "representative_visual_proof_report": str(
            result["representative_visual_proof_report_path"]
        ).replace("\\", "/"),
        "representative_visual_proof_report_html": str(
            result["representative_visual_proof_report_html_path"]
        ).replace("\\", "/"),
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"episode_id: {payload['episode_id']}")
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"proof_profile: {payload['proof_profile']}")
        print(f"scope: {payload['scope']}")
        print(f"target_cuts: {', '.join(payload['target_cuts'])}")
        print(f"dry_run: {str(payload['dry_run']).lower()}")
        print(f"source_media_status: {payload['source_media_status']}")
        print(f"visual_proof_status: {payload['visual_proof_status']}")
        print(f"style_direction_preset: {payload['style_direction_preset']}")
        print(f"style_candidate_id: {payload['style_candidate_id']}")
        print(
            "typography_decoration_candidate_id: "
            f"{payload['typography_decoration_candidate_id']}"
        )
        print(f"subtitle_overlay_available_count: {payload['subtitle_overlay_available_count']}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(f"creative_acceptance: {str(payload['creative_acceptance']).lower()}")
        print(f"publish_acceptance: {str(payload['publish_acceptance']).lower()}")
        print(f"rights_status: {payload['rights_status']}")
        print(f"production_usage_allowed: {str(payload['production_usage_allowed']).lower()}")
        print(f"report: {payload['report']}")
        print(f"report_html: {payload['report_html']}")
        print(f"focused_review_html: {payload['focused_review_html']}")
        print(f"representative_visual_proof_report: {payload['representative_visual_proof_report']}")
        print(
            "representative_visual_proof_report_html: "
            f"{payload['representative_visual_proof_report_html']}"
        )
    return 0
