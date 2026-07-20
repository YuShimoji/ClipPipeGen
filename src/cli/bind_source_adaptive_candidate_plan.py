"""Hash, hydrate, and endpoint-bind an OUT-11 candidate plan template."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from src.integrations.render.endpoint_preflight import (
    EndpointPreflightError,
    bind_builder_input,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="bind-source-adaptive-candidate-plan",
        description=(
            "Resolve exact input hashes, hydrate official JSON3 cue fields, and "
            "bind a candidate plan to ready endpoint authority."
        ),
    )
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        template_path = Path(args.template).resolve()
        output_path = Path(args.output).resolve()
        if output_path.parent != template_path.parent:
            raise ValueError("bound plan output must remain beside its template")
        plan = _read_json(template_path, "candidate plan template")
        inputs = plan.get("expected_inputs")
        if not isinstance(inputs, list):
            raise ValueError("expected_inputs must be a list")
        resolved: dict[str, Path] = {}
        for row in inputs:
            if not isinstance(row, dict):
                raise ValueError("expected input row must be an object")
            role = str(row.get("role") or "")
            path = Path(str(row.get("path") or "")).resolve()
            if not role or role in resolved or not path.is_file():
                raise ValueError(f"invalid expected input: {role or 'missing role'}")
            row["sha256"] = _sha256(path)
            resolved[role] = path

        caption_track = _read_json(
            resolved["source_caption_track"], "source caption track"
        )
        events = caption_track.get("events")
        if not isinstance(events, list):
            raise ValueError("source caption track events are missing")
        cues = (plan.get("candidate") or {}).get("caption_cues")
        if not isinstance(cues, list):
            raise ValueError("candidate caption_cues must be a list")
        for cue in cues:
            if not isinstance(cue, dict):
                raise ValueError("candidate caption cue must be an object")
            index = int(cue.get("event_index", -1))
            if index < 0 or index >= len(events) or not isinstance(events[index], dict):
                raise ValueError(f"caption event index is invalid: {index}")
            event = events[index]
            text = _normalize_caption_text(
                "".join(
                    str(segment.get("utf8") or "")
                    for segment in event.get("segs") or []
                    if isinstance(segment, dict)
                )
            )
            if not text:
                raise ValueError(f"caption event has no text: {index}")
            start = round(float(event.get("tStartMs") or 0) / 1000.0, 3)
            duration = round(float(event.get("dDurationMs") or 0) / 1000.0, 3)
            if duration <= 0:
                raise ValueError(f"caption event has no duration: {index}")
            cue["source_start_seconds"] = start
            cue["source_end_seconds"] = round(start + duration, 3)
            cue["text"] = text

        preflight = _read_json(resolved["endpoint_preflight"], "endpoint preflight")
        selection = _read_json(resolved["endpoint_selection"], "endpoint selection")
        bound = bind_builder_input(plan, preflight, selection)
        output_path.write_text(
            json.dumps(bound, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (EndpointPreflightError, KeyError, OSError, ValueError) as exc:
        print(f"bind-source-adaptive-candidate-plan failed: {exc}", file=sys.stderr)
        return 2

    payload = {
        "output": str(output_path),
        "artifact_id": bound.get("artifact_id"),
        "input_count": len(bound["expected_inputs"]),
        "caption_cue_count": len((bound.get("candidate") or {})["caption_cues"]),
        "builder_input_sha256": bound["endpoint_binding"]["builder_input_sha256"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"bound source-adaptive plan: {payload['artifact_id']} / "
            f"cues={payload['caption_cue_count']}"
        )
    return 0


def _read_json(path: Path, label: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain a JSON object")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_caption_text(value: str) -> str:
    return (
        value.replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u2060", "")
        .replace("\ufeff", "")
        .strip()
    )
