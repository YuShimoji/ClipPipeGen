"""Split a private transfer archive into connector-friendly parts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.private_artifact_transfer import (
    PrivateArtifactTransferError,
    split_private_artifact_transfer,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="split-private-artifact-transfer")
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--part-size-mib", type=int, default=16)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = split_private_artifact_transfer(
            archive_path=args.archive,
            part_size_bytes=args.part_size_mib * 1024 * 1024,
        )
    except (PrivateArtifactTransferError, OSError) as exc:
        stage = getattr(exc, "stage", "split")
        print(f"split-private-artifact-transfer failed at {stage}: {exc}", file=sys.stderr)
        return 2
    payload = {
        key: [str(path) for path in value]
        if key == "parts"
        else str(value)
        if isinstance(value, Path)
        else value
        for key, value in result.items()
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{result['state']}: {result['part_count']} parts")
        print(f"parts manifest: {result['parts_manifest']}")
    return 0
