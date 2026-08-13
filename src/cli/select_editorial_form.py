"""Select an editorial-form family member and normalize supported plans."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.pipeline.editorial_form_selection import (
    ACTIVITY_CHRONOLOGY_VARIANT_ID,
    EDITORIAL_FORM_VARIANTS,
    EditorialFormValidationError,
    normalize_editorial_form_plan,
    select_editorial_form,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="select-editorial-form",
        description=(
            "Select one editorial-form family member. activity_chronology "
            "validates and serializes a normalized structural IR; existing "
            "forms keep their current build commands unchanged."
        ),
    )
    parser.add_argument(
        "--variant",
        required=True,
        choices=sorted(EDITORIAL_FORM_VARIANTS),
    )
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        selection = select_editorial_form(args.variant)
        result: dict[str, Any] = {"selection": selection}
        if args.variant == ACTIVITY_CHRONOLOGY_VARIANT_ID:
            if args.plan is None or args.output is None:
                raise EditorialFormValidationError(
                    "activity_chronology requires --plan and --output",
                    rule="activity_chronology_io",
                    locator="command_line",
                )
            if args.output.exists():
                raise EditorialFormValidationError(
                    "refusing to overwrite normalized editorial-form IR",
                    rule="exclusive_output",
                    locator=str(args.output),
                )
            plan = _read_json(args.plan)
            normalized = normalize_editorial_form_plan(
                plan,
                variant_id=args.variant,
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(
                    normalized,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            result.update(
                {
                    "status": "normalized",
                    "output": str(args.output),
                    "unit_count": len(normalized["units"]),
                    "schema_version": normalized["schema_version"],
                }
            )
        else:
            if args.plan is not None or args.output is not None:
                raise EditorialFormValidationError(
                    (
                        f"{args.variant} keeps its existing entry command "
                        f"{selection['entry_command']}"
                    ),
                    rule="existing_variant_entry_path",
                    locator=f"variant:{args.variant}",
                )
            result["status"] = "existing_entry_path_preserved"
    except EditorialFormValidationError as exc:
        print(
            "select-editorial-form failed "
            f"[rule={exc.rule} locator={exc.locator}]: {exc}",
            file=sys.stderr,
        )
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"select-editorial-form failed [rule=plan_read locator={args.plan}]: {exc}",
            file=sys.stderr,
        )
        return 2

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "normalized":
        print(
            f"activity_chronology normalized: {result['unit_count']} units -> "
            f"{result['output']}"
        )
    else:
        print(
            f"{args.variant}: existing entry path preserved at "
            f"{selection['entry_command']}"
        )
    return 0


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EditorialFormValidationError(
            "editorial form plan must be a JSON object",
            rule="plan_schema",
            locator=str(path),
        )
    return value
