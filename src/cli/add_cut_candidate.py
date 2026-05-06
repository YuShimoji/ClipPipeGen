"""add-cut-candidate subcommand: safe manual/import path for ED-02a."""

from __future__ import annotations

import argparse
import sys

from src.pipeline.edit_pack import add_cut_candidate, load_edit_pack, save_edit_pack


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="add-cut-candidate",
        description="Append one manual/imported cut candidate to edit_pack.json.",
    )
    parser.add_argument("--edit-pack", required=True)
    parser.add_argument("--start-seconds", type=float, required=True)
    parser.add_argument("--end-seconds", type=float, required=True)
    parser.add_argument("--id", dest="cut_id")
    parser.add_argument(
        "--source",
        choices=("manual", "auto", "imported"),
        default="manual",
    )
    parser.add_argument("--reason", default="")
    parser.add_argument("--confidence", type=float, default=1.0)
    parser.add_argument(
        "--context-status",
        choices=("not_checked", "passed", "needs_review", "failed"),
        default="not_checked",
    )
    parser.add_argument("--select", action="store_true")
    args = parser.parse_args(argv)

    pack = load_edit_pack(args.edit_pack)
    try:
        pack = add_cut_candidate(
            pack,
            start_seconds=args.start_seconds,
            end_seconds=args.end_seconds,
            source=args.source,
            reason=args.reason,
            confidence=args.confidence,
            context_status=args.context_status,
            cut_id=args.cut_id,
            select=args.select,
        )
    except ValueError as exc:
        print(f"add-cut-candidate failed: {exc}", file=sys.stderr)
        return 1

    save_edit_pack(pack, args.edit_pack)
    new_cut = pack["cut_candidates"][-1]
    selected = " selected" if new_cut["id"] in (pack.get("selected_cut_ids") or []) else ""
    print(f"added: {new_cut['id']}{selected}")
    return 0
