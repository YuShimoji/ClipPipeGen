"""Build one private, cross-device artifact transfer ZIP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.private_artifact_transfer import (
    PrivateArtifactTransferError,
    build_private_artifact_transfer,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="build-private-artifact-transfer")
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--source-identity", required=True)
    parser.add_argument("--repo-head", required=True)
    parser.add_argument("--include", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = build_private_artifact_transfer(
            bundle_id=args.bundle_id,
            artifact_id=args.artifact_id,
            source_identity=args.source_identity,
            repo_head=args.repo_head,
            includes=args.include,
            output_path=args.output,
            base_dir=Path.cwd(),
        )
    except PrivateArtifactTransferError as exc:
        print(
            f"build-private-artifact-transfer failed at {exc.stage}: {exc}",
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
            f"{result['archive_byte_size']} bytes"
        )
        print(f"archive: {result['archive']}")
        print(f"sha256: {result['archive_sha256']}")
        print(f"receipt: {result['receipt']}")
    return 0
