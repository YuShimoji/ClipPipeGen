"""Build a hash-bound endpoint evidence manifest from package-local files."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

from src.integrations.render.endpoint_preflight import payload_sha256


_SHA256 = re.compile(r"[0-9a-f]{64}")
REQUIRED_NAMES = {
    "endpoint_preflight.json",
    "endpoint_selection.json",
    "endpoint_contact_sheet.jpg",
    "endpoint_waveform.png",
}


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-endpoint-evidence-manifest",
        description="Hash package-local endpoint evidence into one self-bound manifest.",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-identity", required=True)
    parser.add_argument("--source-media-sha256", required=True)
    parser.add_argument("--selected-end-seconds", required=True, type=float)
    parser.add_argument("--selection-state", default="ready_for_render")
    parser.add_argument("--file", action="append", required=True, dest="files")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        output = Path(args.output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        source_hash = args.source_media_sha256.lower()
        if not _SHA256.fullmatch(source_hash):
            raise ValueError("source media SHA-256 is invalid")
        rows = []
        names: set[str] = set()
        for value in args.files:
            path = Path(value).resolve()
            if not path.is_file() or path.parent != output:
                raise ValueError("evidence files must exist directly in output-dir")
            if path.name in names:
                raise ValueError("evidence file name is duplicated")
            names.add(path.name)
            rows.append(
                {
                    "path": path.name,
                    "sha256": _sha256(path),
                    "byte_size": path.stat().st_size,
                }
            )
        missing = REQUIRED_NAMES - names
        if missing:
            raise ValueError(
                f"required endpoint evidence is missing: {sorted(missing)}"
            )
        rows.sort(key=lambda row: row["path"])
        manifest = {
            "schema_version": "clippipegen.endpoint_evidence_manifest.v0",
            "source_identity": args.source_identity,
            "source_media_sha256": source_hash,
            "selected_end_seconds": args.selected_end_seconds,
            "selection_state": args.selection_state,
            "files": rows,
            "file_count": len(rows),
            "manifest_self_integrity": {
                "algorithm": "sha256-canonical-json-self-null",
                "sha256": None,
            },
        }
        canonical = copy.deepcopy(manifest)
        canonical["manifest_self_integrity"]["sha256"] = None
        manifest["manifest_self_integrity"]["sha256"] = payload_sha256(canonical)
        path = output / "endpoint_evidence_manifest.json"
        path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        print(f"build-endpoint-evidence-manifest failed: {exc}", file=sys.stderr)
        return 2

    payload = {
        "manifest": str(path),
        "file_count": manifest["file_count"],
        "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
        "manifest_file_sha256": _sha256(path),
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"endpoint evidence manifest: {payload['file_count']} files")
    return 0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
