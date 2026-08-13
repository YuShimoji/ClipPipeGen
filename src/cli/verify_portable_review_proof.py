"""Verify and optionally extract an exact portable review proof package."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from src.pipeline.portable_review_proof import (
    PortableReviewProofError,
    verify_portable_review_proof,
)


def _jsonable(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="verify-portable-review-proof")
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--outer-manifest", required=True, type=Path)
    parser.add_argument("--expected", required=True, type=Path)
    parser.add_argument("--extract-to", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = verify_portable_review_proof(
            archive_path=args.archive,
            outer_manifest_path=args.outer_manifest,
            expectation_path=args.expected,
            extract_to=args.extract_to,
        )
    except (PortableReviewProofError, OSError, zipfile.BadZipFile) as exc:
        stage = getattr(exc, "stage", "verification")
        print(
            f"verify-portable-review-proof failed at {stage}: {exc}",
            file=sys.stderr,
        )
        return 2
    payload = _jsonable(result)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"{result['state']}: {result['package_file_count']} package files / "
            f"{result['archive_sha256']}"
        )
        if result["review_entrypoint"] is not None:
            print(f"review: {result['review_entrypoint']}")
            print(f"open: {result['review_open_command']}")
    return 0
