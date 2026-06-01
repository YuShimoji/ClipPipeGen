"""build-chapter-revision-board subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.chapter_revision_board import (
    ChapterRevisionBoardError,
    build_chapter_revision_board,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-chapter-revision-board",
        description=(
            "Build a static chapter revision board and patch templates from existing "
            "R3 review artifacts. This is an operator decision surface only, not "
            "production acceptance."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--review-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--edit-pack")
    parser.add_argument("--transcript")
    parser.add_argument("--rights-manifest")
    parser.add_argument("--no-example", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    episode_dir = Path(args.episode_dir)
    try:
        result = build_chapter_revision_board(
            episode_dir=episode_dir,
            review_dir=Path(args.review_dir) if args.review_dir else None,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            edit_pack_path=Path(args.edit_pack) if args.edit_pack else None,
            transcript_path=Path(args.transcript) if args.transcript else None,
            rights_manifest_path=Path(args.rights_manifest) if args.rights_manifest else None,
            base_dir=Path.cwd(),
            include_example=not args.no_example,
        )
    except (OSError, json.JSONDecodeError, ChapterRevisionBoardError) as exc:
        print(f"build-chapter-revision-board failed: {exc}", file=sys.stderr)
        return 1

    board = result["board"]
    summary = board.get("summary") or {}
    boundary = board.get("boundary_flags") or {}
    payload = {
        "schema_version": "v1",
        "episode_id": board.get("episode_id"),
        "board_kind": board.get("board_kind"),
        "chapter_count": summary.get("chapter_count"),
        "candidate_seed_count": summary.get("candidate_seed_count"),
        "retained_context_risk_count": summary.get("retained_context_risk_count"),
        "production_candidate": boundary.get("production_candidate"),
        "creative_acceptance": boundary.get("creative_acceptance"),
        "publish_acceptance": boundary.get("publish_acceptance"),
        "rights_status": boundary.get("rights_status"),
        "board": str(result["board_path"]).replace("\\", "/"),
        "board_html": str(result["board_html_path"]).replace("\\", "/"),
        "patch_template": str(result["patch_template_path"]).replace("\\", "/"),
        "patch_csv": str(result["patch_csv_path"]).replace("\\", "/"),
        "example": str(result["example_path"]).replace("\\", "/")
        if result.get("example_path")
        else None,
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"episode_id: {payload['episode_id']}")
        print(f"board_kind: {payload['board_kind']}")
        print(f"chapter_count: {payload['chapter_count']}")
        print(f"candidate_seed_count: {payload['candidate_seed_count']}")
        print(f"retained_context_risk_count: {payload['retained_context_risk_count']}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(f"creative_acceptance: {str(payload['creative_acceptance']).lower()}")
        print(f"publish_acceptance: {str(payload['publish_acceptance']).lower()}")
        print(f"rights_status: {payload['rights_status']}")
        print(f"board: {payload['board']}")
        print(f"board_html: {payload['board_html']}")
        print(f"patch_template: {payload['patch_template']}")
        print(f"patch_csv: {payload['patch_csv']}")
        if payload["example"]:
            print(f"example: {payload['example']}")
    return 0
