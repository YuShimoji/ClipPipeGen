"""import-subtitle-track subcommand: ED-10 subtitle track -> transcript.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.subtitle_import import (
    SubtitleTrackImportError,
    import_subtitle_track_transcript,
)
from src.pipeline.transcript import load_transcript, save_transcript


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="import-subtitle-track",
        description=(
            "Import an existing subtitle track as a transcript.json-compatible artifact. "
            "This preserves source_audio readback from a base transcript."
        ),
    )
    parser.add_argument("--base-transcript", required=True)
    parser.add_argument("--subtitle-track", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--source-format",
        choices=("youtube-json3",),
        default="youtube-json3",
    )
    parser.add_argument("--provider", default="youtube_subtitles")
    parser.add_argument("--language")
    parser.add_argument(
        "--segment-review-status",
        choices=("unreviewed", "accepted", "needs_fix"),
        default="accepted",
    )
    parser.add_argument("--reviewed-by")
    parser.add_argument("--min-alignment-overlap-seconds", type=float, default=0.05)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    output_path = Path(args.output)
    if output_path.exists() and not args.force and not args.dry_run:
        _print_failure(
            f"refusing to overwrite existing transcript: {output_path} (use --force)",
            fmt=args.format,
            dry_run=args.dry_run,
        )
        return 1

    try:
        base_transcript = load_transcript(args.base_transcript)
        subtitle_payload = _load_json(Path(args.subtitle_track))
        result = import_subtitle_track_transcript(
            base_transcript=base_transcript,
            subtitle_payload=subtitle_payload,
            subtitle_track_path=args.subtitle_track,
            source_format=args.source_format,
            language=args.language,
            provider=args.provider,
            segment_review_status=args.segment_review_status,
            reviewed_by=args.reviewed_by,
            min_alignment_overlap_seconds=args.min_alignment_overlap_seconds,
        )
    except (OSError, json.JSONDecodeError, SubtitleTrackImportError) as exc:
        _print_failure(str(exc), fmt=args.format, dry_run=args.dry_run)
        return 1

    payload = result.to_dict(dry_run=args.dry_run)
    payload["base_transcript"] = str(Path(args.base_transcript)).replace("\\", "/")
    payload["subtitle_track"] = str(Path(args.subtitle_track)).replace("\\", "/")
    payload["output"] = str(output_path).replace("\\", "/")

    if result.schema_issues:
        _print_payload(payload, fmt=args.format)
        print(
            "import-subtitle-track failed: imported transcript would not validate",
            file=sys.stderr,
        )
        return 1

    if not args.dry_run:
        save_transcript(result.transcript, output_path)

    _print_payload(payload, fmt=args.format)
    return 0


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise SubtitleTrackImportError("subtitle track file must contain a JSON object")
    return payload


def _print_payload(payload: dict, *, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    action = "would import" if payload["dry_run"] else "imported"
    print(
        "import-subtitle-track: "
        f"{action} {payload['imported_segment_count']} segment(s); "
        f"skipped={payload['skipped_event_count']}; "
        f"aligned={payload['aligned_segment_count']}; "
        f"unaligned={payload['unaligned_segment_count']}; "
        f"overlapping={payload['overlapping_segment_count']}; "
        f"review.status={payload['review_status']}"
    )
    if payload["dry_run"]:
        print(f"dry_run: no files written; output would be {payload['output']}")
    else:
        print(f"saved: {payload['output']}")


def _print_failure(message: str, *, fmt: str, dry_run: bool) -> None:
    if fmt == "json":
        print(
            json.dumps(
                {
                    "schema_version": "v1",
                    "schema_ok": False,
                    "error": message,
                    "dry_run": dry_run,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    print(f"import-subtitle-track failed: {message}", file=sys.stderr)
