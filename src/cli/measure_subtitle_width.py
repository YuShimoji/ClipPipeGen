"""measure-subtitle-width subcommand: ED-05.

EAW-based subtitle width measurement and optional wrapping.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.text_measure import measure_subtitle


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="measure-subtitle-width",
        description=(
            "Measure subtitle text width in East Asian Width units. "
            "If --wrap-eaw is given, also report greedy-wrapped lines."
        ),
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="subtitle text (use --text-file for multi-line)")
    src.add_argument("--text-file", help="path to a UTF-8 text file")
    parser.add_argument("--wrap-eaw", type=int, default=None, help="wrap target in EAW units")
    parser.add_argument(
        "--ambiguous-width",
        type=int,
        choices=(1, 2),
        default=1,
        help="treat unicode 'A' (Ambiguous) chars as N units (default 1)",
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)

    if args.text is not None:
        text = args.text
    else:
        text = Path(args.text_file).read_text(encoding="utf-8")

    result = measure_subtitle(
        text,
        wrap_eaw=args.wrap_eaw,
        ambiguous_width=args.ambiguous_width,
    )

    if args.format == "json":
        json.dump(result.to_dict(), sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"chars: {result.total_chars}")
        print(f"eaw_units: {result.total_eaw_units}")
        if result.wrap_eaw is not None:
            print(f"wrap_eaw: {result.wrap_eaw}")
            print(f"longest_line_eaw: {result.longest_line_eaw}")
            print(f"needs_wrap: {result.needs_wrap}")
        print(f"lines ({len(result.lines)}):")
        for i, line in enumerate(result.lines, 1):
            flag = " !overflow" if line.overflows else ""
            print(f"  {i:>2}. [{line.eaw_units:>3}u]{flag} {line.text}")

    return 1 if result.needs_wrap else 0
