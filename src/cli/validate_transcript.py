"""validate-transcript subcommand: schema validation for transcript.json."""

from __future__ import annotations

import argparse
import json
import sys

from src.pipeline.transcript import load_transcript, validate_transcript


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="validate-transcript",
        description="Validate transcript.json against schema v1.",
    )
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    transcript = load_transcript(args.transcript)
    issues = validate_transcript(transcript)

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
            print(f"validate-transcript: {len(issues)} issue(s)")
            for issue in issues:
                print(
                    f"  [{issue.severity}] {issue.code} @ "
                    f"{issue.field}: {issue.message}"
                )
        else:
            print("validate-transcript: OK")

    return 0 if not issues else 1
