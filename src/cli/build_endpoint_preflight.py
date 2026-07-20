"""Build source-neutral endpoint preflight and optional Agent selection JSON."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from src.integrations.render.endpoint_preflight import (
    EndpointPreflightError,
    build_endpoint_preflight,
    build_endpoint_selection,
    payload_sha256,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-endpoint-preflight",
        description=(
            "Build deterministic mechanical endpoint candidates and, when "
            "provided, bind one explicit Agent selection."
        ),
    )
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--selection-request")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        spec = _read_json(Path(args.spec), "endpoint preflight spec")
        preflight = build_endpoint_preflight(spec)
        output = Path(args.output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        preflight_path = output / "endpoint_preflight.json"
        _write_json(preflight_path, preflight)

        selection = None
        selection_path = None
        if args.selection_request:
            request = copy.deepcopy(
                _read_json(Path(args.selection_request), "endpoint selection request")
            )
            request["preflight_sha256"] = payload_sha256(preflight)
            selection = build_endpoint_selection(preflight, request)
            selection_path = output / "endpoint_selection.json"
            _write_json(selection_path, selection)
    except (EndpointPreflightError, OSError, ValueError) as exc:
        print(f"build-endpoint-preflight failed: {exc}", file=sys.stderr)
        return 2

    payload = {
        "preflight": str(preflight_path),
        "preflight_state": preflight["state"],
        "preflight_sha256": payload_sha256(preflight),
        "candidate_count": len(preflight["candidates"]),
        "selection": str(selection_path) if selection_path else None,
        "selection_state": selection["state"] if selection else None,
        "selection_sha256": payload_sha256(selection) if selection else None,
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"endpoint preflight: {payload['preflight_state']} / "
            f"candidates={payload['candidate_count']}"
        )
        if selection is not None:
            print(f"endpoint selection: {payload['selection_state']}")
    return 0


def _read_json(path: Path, label: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain a JSON object")
    return payload


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
