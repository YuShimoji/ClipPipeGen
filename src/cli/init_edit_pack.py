"""init-edit-pack subcommand: create an edit_pack skeleton for an episode."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.pipeline.edit_pack import build_skeleton, save_edit_pack


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="init-edit-pack",
        description="Create episodes/<episode_id>/edit_pack.json skeleton.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    episode_dir = Path(args.root) / args.episode_id
    rights_path = episode_dir / "rights_manifest.json"
    output_path = episode_dir / "edit_pack.json"

    if not rights_path.exists():
        print(
            f"rights_manifest not found: {rights_path}. "
            "Create and validate rights before creating edit_pack.",
            file=sys.stderr,
        )
        return 1
    if output_path.exists() and not args.force:
        print(
            f"refusing to overwrite existing edit_pack: {output_path} "
            "(use --force to overwrite)",
            file=sys.stderr,
        )
        return 1

    pack = build_skeleton(
        args.episode_id,
        rights_manifest_path=str(rights_path).replace("\\", "/"),
        material_ledger_path=str((episode_dir / "material_ledger.json")).replace("\\", "/"),
    )
    save_edit_pack(pack, output_path)
    print(f"created: {output_path}")
    return 0
