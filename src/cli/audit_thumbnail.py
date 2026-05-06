"""audit-thumbnail subcommand: NLMYTGen audit-thumbnail-template の bridge wrapper."""

from __future__ import annotations

import argparse
import json
import sys

from src.pipeline import nlmytgen_bridge as bridge


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="audit-thumbnail",
        description=(
            "Audit a YMM4 thumbnail template's thumb.* slots via NLMYTGen "
            "subprocess (read-only)."
        ),
    )
    parser.add_argument("--base-template", required=True, help="Path to base .ymmp")
    parser.add_argument("--config", default=bridge.CONFIG_PATH_DEFAULT)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        cfg = bridge.BridgeConfig.load(args.config)
        result = bridge.audit_thumbnail_template(args.base_template, config=cfg)
    except bridge.BridgeConfigError as exc:
        print(f"audit-thumbnail config error: {exc}", file=sys.stderr)
        return 2
    except bridge.BridgeExecutionError as exc:
        print(f"audit-thumbnail subprocess failed: {exc}", file=sys.stderr)
        if exc.stderr:
            print(f"stderr (tail): {exc.stderr[-500:]}", file=sys.stderr)
        return 1

    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        slots = result.get("slots", [])
        errors = result.get("errors", [])
        print(f"slots found: {len(slots)}")
        for s in slots:
            print(f"  {s.get('kind') or s.get('slot_type')}.{s.get('id') or s.get('slot_id')}")
        if errors:
            print(f"errors: {len(errors)}")
            for e in errors:
                print(f"  {e}")
    return 0
