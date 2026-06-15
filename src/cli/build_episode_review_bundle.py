"""build-episode-review-bundle subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.episode_review_bundle import (
    DEFAULT_ACTIVE_ARTIFACT,
    EpisodeReviewBundleError,
    build_episode_review_bundle,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-episode-review-bundle",
        description=(
            "Build a single local diagnostic/representative review bundle from existing "
            "episode artifacts. This command does not render, fetch, upload, or approve production use."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--review-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--active-artifact", default=DEFAULT_ACTIVE_ARTIFACT)
    parser.add_argument("--target-cut", action="append", dest="target_cuts")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_episode_review_bundle(
            episode_dir=Path(args.episode_dir),
            review_dir=Path(args.review_dir) if args.review_dir else None,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            active_artifact=args.active_artifact,
            target_cut_ids=args.target_cuts,
            base_dir=Path.cwd(),
        )
    except (OSError, json.JSONDecodeError, EpisodeReviewBundleError) as exc:
        print(f"build-episode-review-bundle failed: {exc}", file=sys.stderr)
        return 1

    manifest = result["manifest"]
    reviewability = manifest["reviewability"]
    boundary = manifest["boundary_flags"]
    payload = {
        "schema_version": manifest["schema_version"],
        "episode_id": manifest["episode_id"],
        "active_artifact": manifest["active_artifact"],
        "review_ready": reviewability["review_ready"],
        "reviewability": reviewability["state"],
        "missing_required_files": reviewability["missing_required_files"],
        "diagnostic_only": boundary["diagnostic_only"],
        "production_render_acceptance": boundary["production_render_acceptance"],
        "production_subtitle_design_acceptance": boundary["production_subtitle_design_acceptance"],
        "rights_status": boundary["rights_status"],
        "publishing_acceptance": boundary["publishing_acceptance"],
        "review_manifest": str(result["manifest_path"]).replace("\\", "/"),
        "index_html": str(result["index_path"]).replace("\\", "/"),
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"episode_id: {payload['episode_id']}")
        print(f"active_artifact: {payload['active_artifact']}")
        print(f"review_ready: {str(payload['review_ready']).lower()}")
        print(f"reviewability: {payload['reviewability']}")
        print(f"diagnostic_only: {str(payload['diagnostic_only']).lower()}")
        print(f"production_render_acceptance: {str(payload['production_render_acceptance']).lower()}")
        print(
            "production_subtitle_design_acceptance: "
            f"{str(payload['production_subtitle_design_acceptance']).lower()}"
        )
        print(f"rights_status: {payload['rights_status']}")
        print(f"publishing_acceptance: {str(payload['publishing_acceptance']).lower()}")
        print(f"review_manifest: {payload['review_manifest']}")
        print(f"index_html: {payload['index_html']}")
    return 0
