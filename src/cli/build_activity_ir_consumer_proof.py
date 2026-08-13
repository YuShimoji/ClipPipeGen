"""CLI for the private activity chronology IR consumer proof."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.integrations.render.activity_ir_consumer_proof import (
    ActivityIRConsumerError,
    build_package,
)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build-activity-ir-consumer-proof",
        description=(
            "Bind the exact retained S2 activity plan, media, and captions to a "
            "new non-adopted H.264/AAC review proof."
        ),
    )
    parser.add_argument("--legacy-plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--chrome", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build_package(
            repo=Path.cwd(),
            legacy_plan_path=args.legacy_plan,
            output_dir=args.output_dir,
            font_path=args.font,
            chrome_path=args.chrome,
        )
    except (ActivityIRConsumerError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            "build-activity-ir-consumer-proof failed "
            f"[stage={getattr(exc, 'stage', 'unclassified')}]: {exc}",
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
