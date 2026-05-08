"""transcribe-audio subcommand: local audio -> transcript.json.

ED-07 only provides the adapter surface. The initial executable engine is
`fake`, which consumes fixture segments for deterministic tests and smoke runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.pipeline.material_ledger import compute_sha256, load_ledger
from src.pipeline.transcript import (
    build_transcript,
    save_transcript,
    validate_transcript,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="transcribe-audio",
        description="Create transcript.json from an existing local audio file.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--source-audio", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--language", default="ja")
    parser.add_argument("--engine", choices=("fake",), required=True)
    parser.add_argument("--fixture-segments")
    parser.add_argument("--material-ledger")
    parser.add_argument("--material-id")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    if "://" in args.source_audio:
        print(
            "transcribe-audio accepts local audio files only; URL/VOD fetch belongs to INT-02 asset_fetch",
            file=sys.stderr,
        )
        return 1

    source_audio = Path(args.source_audio)
    if not source_audio.exists() or not source_audio.is_file():
        print(f"source audio not found: {source_audio}", file=sys.stderr)
        return 1

    output_path = Path(args.output)
    if output_path.exists() and not args.force:
        print(
            f"refusing to overwrite existing transcript: {output_path} "
            "(use --force to overwrite)",
            file=sys.stderr,
        )
        return 1

    if not args.fixture_segments:
        print("--fixture-segments is required for --engine fake", file=sys.stderr)
        return 1

    try:
        segments = _load_fixture_segments(Path(args.fixture_segments))
        material_id = _validate_material_link(
            material_ledger_path=args.material_ledger,
            material_id=args.material_id,
            source_audio=source_audio,
        )
    except ValueError as exc:
        print(f"transcribe-audio failed: {exc}", file=sys.stderr)
        return 1

    warnings = []
    if not segments:
        warnings.append("fake engine fixture produced no segments")

    transcript = build_transcript(
        args.episode_id,
        source_audio_path=_display_path(source_audio, Path.cwd()),
        language=args.language,
        stt_engine=args.engine,
        stt_engine_version="fake-v1",
        stt_params={
            "fixture_segments": _display_path(Path(args.fixture_segments), Path.cwd()),
            "language": args.language,
        },
        stt_warnings=warnings,
        segments=segments,
        material_id=material_id,
        source_audio_sha256=compute_sha256(source_audio),
    )
    issues = validate_transcript(transcript)
    if issues:
        print(f"transcribe-audio produced invalid transcript: {len(issues)} issue(s)", file=sys.stderr)
        for issue in issues:
            print(f"  {issue.code} @ {issue.field}: {issue.message}", file=sys.stderr)
        return 1

    save_transcript(transcript, output_path)
    print(f"created: {output_path}")
    print(f"segments: {len(transcript['segments'])}")
    return 0


def _load_fixture_segments(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        raise ValueError(f"fixture segments not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if isinstance(payload, dict):
        payload = payload.get("segments")
    if not isinstance(payload, list):
        raise ValueError("fixture segments must be a JSON array or an object with segments[]")
    return payload


def _validate_material_link(
    *,
    material_ledger_path: str | None,
    material_id: str | None,
    source_audio: Path,
) -> str | None:
    if not material_id:
        return None
    if not material_ledger_path:
        raise ValueError("--material-ledger is required when --material-id is provided")

    ledger_path = Path(material_ledger_path)
    if not ledger_path.exists():
        raise ValueError(f"material ledger not found: {ledger_path}")
    ledger = load_ledger(ledger_path)
    material = next(
        (m for m in ledger.get("materials", []) if m.get("id") == material_id),
        None,
    )
    if material is None:
        raise ValueError(f"material id not found in ledger: {material_id}")
    if material.get("kind") and material.get("kind") != "source_audio":
        raise ValueError(
            f"material {material_id!r} must be kind='source_audio' "
            f"(actual={material.get('kind')!r})"
        )
    file_path = material.get("file_path")
    if file_path and not _same_path(file_path, ledger_path=ledger_path, expected=source_audio):
        raise ValueError(
            f"material {material_id!r} file_path does not match source audio: {file_path}"
        )
    return material_id


def _same_path(file_path: str, *, ledger_path: Path, expected: Path) -> bool:
    expected_resolved = expected.resolve()
    raw = Path(file_path)
    candidates = [raw]
    if not raw.is_absolute():
        candidates.append(Path.cwd() / raw)
        candidates.append(ledger_path.parent / raw)
    for candidate in candidates:
        try:
            if candidate.resolve() == expected_resolved:
                return True
        except OSError:
            continue
    return False


def _display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
