"""init-episode subcommand: create a new episode skeleton."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.pipeline.rights_manifest import build_skeleton, save_rights_manifest


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="init-episode",
        description="Create a new episode directory with a rights_manifest skeleton.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument(
        "--root",
        default="episodes",
        help="Episode root directory (default: episodes)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing rights_manifest.json if present.",
    )
    args = parser.parse_args(argv)

    episode_dir = Path(args.root) / args.episode_id
    manifest_path = episode_dir / "rights_manifest.json"

    if manifest_path.exists() and not args.force:
        print(
            f"refusing to overwrite existing manifest: {manifest_path} "
            "(use --force to overwrite)",
            file=sys.stderr,
        )
        return 1

    manifest = build_skeleton(args.episode_id)
    save_rights_manifest(manifest, manifest_path)
    print(f"created: {manifest_path}")
    return 0
