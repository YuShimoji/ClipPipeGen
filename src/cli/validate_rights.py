"""validate-rights subcommand: schema validation for rights_manifest."""

from __future__ import annotations

import argparse
import json
import sys

from src.pipeline.rights_manifest import (
    evaluate_compliance_auto_fail,
    load_rights_manifest,
    validate_rights_manifest,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="validate-rights",
        description="Validate a rights_manifest.json against schema v1.",
    )
    parser.add_argument("--rights-manifest", required=True)
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
    )
    args = parser.parse_args(argv)

    manifest = load_rights_manifest(args.rights_manifest)
    schema_issues = validate_rights_manifest(manifest)
    review_notes = evaluate_compliance_auto_fail(manifest)

    if args.format == "json":
        payload = {
            "schema_issues": [i.to_dict() for i in schema_issues],
            "review_notes": [i.to_dict() for i in review_notes],
            "schema_ok": not schema_issues,
            "compliance_passable": True,
        }
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        if schema_issues:
            print(f"schema issues ({len(schema_issues)}):")
            for i in schema_issues:
                print(f"  [{i.severity}] {i.code} @ {i.field}: {i.message}")
        else:
            print("schema: OK")

        if review_notes:
            print(f"rights review notes ({len(review_notes)}):")
            for i in review_notes:
                print(f"  [{i.severity}] {i.code} @ {i.field}: {i.message}")
        else:
            print("rights review: no notes")

    return 0 if not schema_issues else 1
