"""validate-edit-pack subcommand: schema validation for edit_pack."""

from __future__ import annotations

import argparse
import json
import sys

from src.pipeline.edit_pack import load_edit_pack, validate_edit_pack


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="validate-edit-pack",
        description="Validate edit_pack.json against schema v1.",
    )
    parser.add_argument("--edit-pack", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    pack = load_edit_pack(args.edit_pack)
    issues = validate_edit_pack(pack)

    if args.format == "json":
        json.dump(
            {
                "schema_ok": not issues,
                "schema_issues": [i.to_dict() for i in issues],
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        if issues:
            print(f"validate-edit-pack: {len(issues)} issue(s)")
            for issue in issues:
                print(
                    f"  [{issue.severity}] {issue.code} @ "
                    f"{issue.field}: {issue.message}"
                )
        else:
            print("validate-edit-pack: OK")

    return 0 if not issues else 1
