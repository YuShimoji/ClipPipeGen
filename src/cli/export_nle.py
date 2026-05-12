"""export-nle subcommand: ED-06 edit_pack -> external editing CSV."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.nle_export import NleExportError, export_csv_cut_list


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="export-nle",
        description="Export edit_pack.json to a minimal human-readable NLE CSV cut list.",
    )
    parser.add_argument("--edit-pack", required=True)
    parser.add_argument(
        "--output-dir",
        help="output directory (default: edit_pack sibling exports/ed06)",
    )
    parser.add_argument(
        "--preview-manifest",
        help="preview_manifest.json for source audio provenance readback",
    )
    parser.add_argument(
        "--transcript",
        help="transcript.json for STT provenance readback",
    )
    parser.add_argument(
        "--export-format",
        choices=("csv",),
        default="csv",
        help="external artifact format (ED-06 supports csv only)",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    edit_pack_path = Path(args.edit_pack)
    output_dir = Path(args.output_dir) if args.output_dir else edit_pack_path.parent / "exports" / "ed06"
    preview_manifest_path = Path(args.preview_manifest) if args.preview_manifest else None
    transcript_path = Path(args.transcript) if args.transcript else None

    try:
        result = export_csv_cut_list(
            edit_pack_path=edit_pack_path,
            output_dir=output_dir,
            preview_manifest_path=preview_manifest_path,
            transcript_path=transcript_path,
            base_dir=Path.cwd(),
        )
    except (OSError, json.JSONDecodeError, NleExportError) as exc:
        print(f"export-nle failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "format": result["manifest"]["format"],
        "csv_cut_list": str(result["csv_path"]).replace("\\", "/"),
        "manifest": str(result["manifest_path"]).replace("\\", "/"),
        "report": str(result["report_path"]).replace("\\", "/"),
        "cut_rows": len(result["rows"]),
        "production_edit_candidate": result["manifest"]["production_edit_candidate"],
        "transcript": result["manifest"]["source_refs"]["transcript"],
        "warnings": result["manifest"]["warnings"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"format: {payload['format']}")
        print(f"csv_cut_list: {payload['csv_cut_list']}")
        print(f"manifest: {payload['manifest']}")
        print(f"report: {payload['report']}")
        print(f"cut_rows: {payload['cut_rows']}")
        print(f"production_edit_candidate: {str(payload['production_edit_candidate']).lower()}")
        transcript = payload["transcript"]
        print(f"transcript: {transcript.get('path') or ''}")
        print(f"transcript_real: {str(transcript.get('real_transcript', False)).lower()}")
        for warning in payload["warnings"]:
            print(f"warning: {warning}")
    return 0
