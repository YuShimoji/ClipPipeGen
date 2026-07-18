"""Repair OUT-09 review access without changing media bytes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.second_source_short_repeatability import (
    SecondSourceShortRepeatabilityError,
    repair_second_source_review_access_package,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="repair-second-source-review-access",
        description=(
            "Repair only OUT-09 HTML, PowerShell helpers, readback, and manifest. "
            "The current MP4 SHA-256 must remain fixed."
        ),
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = repair_second_source_review_access_package(
            output_dir=Path(args.output_dir),
            base_dir=Path.cwd(),
        )
    except SecondSourceShortRepeatabilityError as exc:
        print(f"repair-second-source-review-access failed: {exc}", file=sys.stderr)
        return 2

    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["state"],
        "video_sha256": result["video_sha256"],
        "media_bytes_changed": result["media_bytes_changed"],
        "clean_human_url": result["review_access"]["clean_human_url"],
        "canonical_foreground_server_command": result["review_access"][
            "canonical_foreground_server_command"
        ],
        "convenience_open_command": result["review_access"][
            "convenience_open_command"
        ],
        "manifest_self_integrity": result["manifest_self_integrity"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"OUT-09 review access repaired: {payload['state']}")
        print(f"Media unchanged: {payload['video_sha256']}")
        print(
            "Canonical foreground server: "
            f"{payload['canonical_foreground_server_command']}"
        )
    return 0
