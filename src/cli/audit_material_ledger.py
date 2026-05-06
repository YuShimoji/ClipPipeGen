"""audit-material-ledger subcommand: integrity check for material_ledger.

NLMYTGen の audit-* 命名規則に揃える。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.material_ledger import audit_ledger, load_ledger


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="audit-material-ledger",
        description="Integrity check for an episode material_ledger.json.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument(
        "--root",
        default="episodes",
        help="Episode root directory (default: episodes)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
    )
    args = parser.parse_args(argv)

    ledger_path = Path(args.root) / args.episode_id / "material_ledger.json"
    if not ledger_path.exists():
        print(f"ledger not found: {ledger_path}", file=sys.stderr)
        return 1

    ledger = load_ledger(ledger_path)
    issues = audit_ledger(ledger, base_dir=Path("."))

    if args.format == "json":
        json.dump(
            {
                "ok": not issues,
                "issues": [i.to_dict() for i in issues],
                "materials_count": len(ledger.get("materials", [])),
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        if issues:
            print(f"audit-material-ledger: {len(issues)} issue(s)")
            for i in issues:
                print(f"  [{i.severity}] {i.code} @ {i.field}: {i.message}")
        else:
            print(
                f"audit-material-ledger: OK ({len(ledger.get('materials', []))} materials)"
            )

    return 0 if not issues else 1
