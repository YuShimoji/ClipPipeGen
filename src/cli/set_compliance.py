"""set-compliance subcommand: update compliance_check.status readback."""

from __future__ import annotations

import argparse
import sys

from src.pipeline.rights_manifest import (
    load_rights_manifest,
    save_rights_manifest,
    set_compliance_status,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="set-compliance",
        description=(
            "Record a rights/compliance status. Review notes are retained as "
            "warnings but do not block status updates."
        ),
    )
    parser.add_argument("--rights-manifest", required=True)
    parser.add_argument(
        "--status",
        required=True,
        choices=("passed", "pending", "failed"),
    )
    parser.add_argument(
        "--checked-by",
        required=True,
        help="Human checker identifier (e.g. 'user:thankyoukass'). Required.",
    )
    args = parser.parse_args(argv)

    if not args.checked_by.strip():
        print("--checked-by must be a non-empty identifier", file=sys.stderr)
        return 2

    manifest = load_rights_manifest(args.rights_manifest)

    try:
        updated = set_compliance_status(
            manifest,
            status=args.status,
            checked_by=args.checked_by,
        )
    except ValueError as exc:
        print(f"set-compliance failed: {exc}", file=sys.stderr)
        return 1

    save_rights_manifest(updated, args.rights_manifest)
    print(
        f"compliance_check.status -> {args.status} "
        f"(checked_by={args.checked_by})"
    )
    return 0
