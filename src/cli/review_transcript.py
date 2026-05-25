"""review-transcript subcommand: ED-09 transcript correction workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.pipeline.transcript import (
    TranscriptReviewError,
    apply_review_patch,
    load_transcript,
    save_transcript,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="review-transcript",
        description=(
            "Apply a v1 human review/correction patch to transcript.json. "
            "Only segment text, review_status, and notes are mutable."
        ),
    )
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--patch", required=True)
    parser.add_argument(
        "--reviewed-by",
        help="Human reviewer identifier. Required when review.status=approved.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        transcript = load_transcript(args.transcript)
        patch = _load_patch(Path(args.patch))
        result = apply_review_patch(
            transcript,
            patch,
            reviewed_by=args.reviewed_by,
        )
    except (OSError, json.JSONDecodeError, TranscriptReviewError) as exc:
        _print_failure(str(exc), fmt=args.format, dry_run=args.dry_run)
        return 1

    payload = result.to_dict(dry_run=args.dry_run)
    payload["transcript"] = str(Path(args.transcript)).replace("\\", "/")
    payload["patch"] = str(Path(args.patch)).replace("\\", "/")

    if result.schema_issues:
        _print_payload(payload, fmt=args.format)
        print(
            "review-transcript failed: patched transcript would not validate",
            file=sys.stderr,
        )
        return 1

    if not args.dry_run:
        save_transcript(result.transcript, args.transcript)

    _print_payload(payload, fmt=args.format)
    return 0


def _load_patch(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise TranscriptReviewError("patch file must contain a JSON object")
    return payload


def _print_payload(payload: dict[str, Any], *, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    action = "would update" if payload["dry_run"] else "updated"
    counts = payload["segment_review_counts"]
    print(
        "review-transcript: "
        f"{action} {payload['updated_segment_count']} segment(s); "
        f"review.status={payload['review_status']}; "
        f"accepted={counts['accepted_count']}; "
        f"needs_fix={counts['needs_fix_count']}; "
        f"rejected={counts['rejected_count']}; "
        f"unreviewed={counts['unreviewed_count']}"
    )


def _print_failure(message: str, *, fmt: str, dry_run: bool) -> None:
    if fmt == "json":
        print(
            json.dumps(
                {
                    "schema_version": "v1",
                    "schema_ok": False,
                    "error": message,
                    "dry_run": dry_run,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    print(f"review-transcript failed: {message}", file=sys.stderr)
