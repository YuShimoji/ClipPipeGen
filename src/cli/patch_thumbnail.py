"""patch-thumbnail subcommand: TH-01 オーケストレータ。

rights readback -> material validation -> NLMYTGen audit -> NLMYTGen patch -> readback。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline import nlmytgen_bridge as bridge
from src.pipeline.thumbnail_patch import (
    apply_thumbnail_patch,
    load_thumbnail_patch_input,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="patch-thumbnail",
        description=(
            "Apply a thumbnail_patch_input.json end-to-end: "
            "rights readback -> material validation -> NLMYTGen audit -> "
            "NLMYTGen patch -> readback."
        ),
    )
    parser.add_argument("--input", required=True, help="thumbnail_patch_input.json")
    parser.add_argument(
        "--output-result",
        required=True,
        help="Where to write thumbnail_patch_result.json",
    )
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Base directory for resolving relative paths in input (default: cwd)",
    )
    parser.add_argument("--config", default=bridge.CONFIG_PATH_DEFAULT)
    parser.add_argument(
        "--work-dir",
        default="_tmp/thumbnail_patch",
        help="Workdir for intermediate patch JSON",
    )
    args = parser.parse_args(argv)

    try:
        cfg = bridge.BridgeConfig.load(args.config)
    except bridge.BridgeConfigError as exc:
        print(f"patch-thumbnail config error: {exc}", file=sys.stderr)
        return 2

    payload = load_thumbnail_patch_input(args.input)
    result = apply_thumbnail_patch(
        payload,
        base_dir=args.base_dir,
        config=cfg,
        work_dir=Path(args.work_dir),
    )

    out = Path(args.output_result)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    errors = result["patch_result"].get("errors", [])
    if errors:
        print(f"patch-thumbnail FAILED: {errors}", file=sys.stderr)
        return 1
    print(
        f"patch-thumbnail OK -> {result['patch_result']['output_ymmp_path']}"
    )
    return 0
