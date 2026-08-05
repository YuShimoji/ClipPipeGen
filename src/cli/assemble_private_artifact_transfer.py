"""Verify private transfer parts and optionally assemble their archive."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.private_artifact_transfer import (
    PrivateArtifactTransferError,
    verify_private_artifact_parts,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="assemble-private-artifact-transfer")
    parser.add_argument("--parts-manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = verify_private_artifact_parts(
            parts_manifest_path=args.parts_manifest,
            output_path=args.output,
        )
    except (PrivateArtifactTransferError, OSError, json.JSONDecodeError) as exc:
        stage = getattr(exc, "stage", "parts_verification")
        print(f"assemble-private-artifact-transfer failed at {stage}: {exc}", file=sys.stderr)
        return 2
    payload = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in result.items()
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{result['state']}: {result['part_count']} parts")
        print(f"archive sha256: {result['archive_sha256']}")
        if result["assembled_archive"]:
            print(f"assembled: {result['assembled_archive']}")
    return 0
