"""Verify and optionally restore a private artifact transfer ZIP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.private_artifact_transfer import (
    PrivateArtifactTransferError,
    verify_private_artifact_transfer,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="verify-private-artifact-transfer")
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--restore-root", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = verify_private_artifact_transfer(
            archive_path=args.archive,
            receipt_path=args.receipt,
            restore_root=args.restore_root,
        )
    except (PrivateArtifactTransferError, OSError, json.JSONDecodeError) as exc:
        stage = getattr(exc, "stage", "verification")
        print(
            f"verify-private-artifact-transfer failed at {stage}: {exc}",
            file=sys.stderr,
        )
        return 2
    payload = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in result.items()
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"{result['state']}: {result['payload_file_count']} files / "
            f"{result['archive_sha256']}"
        )
        if args.restore_root:
            print(
                f"restored: {result['restored_file_count']} / "
                f"existing exact: {result['existing_exact_file_count']}"
            )
    return 0
