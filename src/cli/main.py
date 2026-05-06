"""ClipPipeGen CLI dispatcher.

Usage:
    python -m src.cli.main <subcommand> [args...]

Subcommands:
    init-episode             Create a new episode skeleton with rights_manifest.
    validate-rights          Validate a rights_manifest.json against schema v1.
    set-compliance           Update compliance_check.status with auto-fail re-check.
    register-material        Register a material into the episode ledger (sidecar required).
    audit-material-ledger    Integrity check for an episode material_ledger.json.
"""

from __future__ import annotations

import sys
from typing import Callable

from . import (
    audit_material_ledger,
    init_episode,
    register_material,
    set_compliance,
    validate_rights,
)

SUBCOMMANDS: dict[str, Callable[[list[str]], int]] = {
    "init-episode": init_episode.run,
    "validate-rights": validate_rights.run,
    "set-compliance": set_compliance.run,
    "register-material": register_material.run,
    "audit-material-ledger": audit_material_ledger.run,
}


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in ("-h", "--help"):
        _print_help()
        return 0 if args else 2

    sub = args[0]
    handler = SUBCOMMANDS.get(sub)
    if handler is None:
        print(f"unknown subcommand: {sub}", file=sys.stderr)
        _print_help()
        return 2

    return handler(args[1:])


def _print_help() -> None:
    print(__doc__ or "")


if __name__ == "__main__":
    raise SystemExit(main())
