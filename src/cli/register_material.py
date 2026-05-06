"""register-material subcommand: add a material to the episode ledger.

sidecar 必須・hash 一致・透過PNG check を強制する。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.pipeline.material_ledger import (
    LedgerError,
    build_skeleton,
    load_ledger,
    register_material,
    save_ledger,
)
from src.pipeline.rights_manifest import load_rights_manifest


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="register-material",
        description="Register a material into the episode ledger with required sidecar.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument(
        "--root",
        default="episodes",
        help="Episode root directory (default: episodes)",
    )
    parser.add_argument("--kind", required=True)
    parser.add_argument("--subkind", default=None)
    parser.add_argument("--file", required=True, help="Asset file path")
    parser.add_argument("--sidecar", required=True, help="Sidecar JSON file path")
    parser.add_argument(
        "--intended-use",
        action="append",
        required=True,
        help="Intended use (repeatable). At least one required.",
    )
    parser.add_argument("--registered-by", required=True)
    parser.add_argument(
        "--material-id",
        default=None,
        help="Override auto-generated material id (must match sidecar.asset_id)",
    )
    args = parser.parse_args(argv)

    episode_dir = Path(args.root) / args.episode_id
    rights_path = episode_dir / "rights_manifest.json"
    ledger_path = episode_dir / "material_ledger.json"

    if not rights_path.exists():
        print(
            f"rights_manifest not found: {rights_path}. "
            "run init-episode first.",
            file=sys.stderr,
        )
        return 1

    rights = load_rights_manifest(rights_path)
    rights_status = (rights.get("compliance_check") or {}).get("status", "pending")

    if ledger_path.exists():
        ledger = load_ledger(ledger_path)
    else:
        ledger = build_skeleton(args.episode_id)

    try:
        ledger = register_material(
            ledger,
            kind=args.kind,
            subkind=args.subkind,
            file_path=args.file,
            sidecar_path=args.sidecar,
            intended_uses=args.intended_use,
            registered_by=args.registered_by,
            rights_manifest_id=rights.get("episode_id", args.episode_id),
            rights_status_at_registration=rights_status,
            material_id=args.material_id,
        )
    except LedgerError as exc:
        print(f"register-material failed: {exc}", file=sys.stderr)
        return 1

    save_ledger(ledger, ledger_path)
    new_id = ledger["materials"][-1]["id"]
    print(f"registered: {new_id} -> {ledger_path}")
    return 0
