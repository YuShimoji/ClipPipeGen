"""transcribe-audio subcommand: local audio -> transcript.json.

ED-07 provides the transcript artifact surface. `fake` consumes fixture
segments for deterministic tests; `vosk` is an optional local real-STT adapter
that requires an explicit model path and never falls back to fixture data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from src.integrations.stt.vosk_adapter import (
    VoskSttError,
    preflight_vosk,
    transcribe_vosk,
    try_read_wav_info,
)
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
    parser.add_argument("--source-audio", "--source-audio-path", dest="source_audio", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--language",
        default="ja",
        help=(
            'BCP-47 language tag recorded in transcript metadata (e.g. "en", "ja"). '
            'Default "ja". For Vosk models, the CLI validates this against an '
            "inferable model language such as vosk-model-small-en-us-0.15 or "
            "vosk-model-small-ja-0.22."
        ),
    )
    parser.add_argument("--engine", choices=("fake", "vosk"))
    parser.add_argument("--provider", choices=("fake", "vosk"), help="alias for --engine")
    parser.add_argument(
        "--model",
        help=(
            "model name or path for real STT providers. Vosk EN example: "
            "_tmp/stt_models/vosk-model-small-en-us-0.15 (ED-07b). Vosk JP example: "
            "_tmp/stt_models/vosk-model-small-ja-0.22 (JP-STT-01). See "
            "docs/JP_STT_SMOKE.md for the JP model fetch runbook."
        ),
    )
    parser.add_argument("--fixture-segments")
    parser.add_argument("--material-ledger")
    parser.add_argument("--material-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        engine = _resolve_engine(args.engine, args.provider)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if engine is None:
        print("transcribe-audio requires --engine or --provider", file=sys.stderr)
        return 1

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
    if output_path.exists() and not args.force and not args.dry_run:
        print(
            f"refusing to overwrite existing transcript: {output_path} "
            "(use --force to overwrite)",
            file=sys.stderr,
        )
        return 1

    try:
        material_id = _validate_material_link(
            material_ledger_path=args.material_ledger,
            material_id=args.material_id,
            source_audio=source_audio,
        )
        if args.dry_run:
            payload = _dry_run_payload(
                engine=engine,
                source_audio=source_audio,
                output_path=output_path,
                language=args.language,
                model=args.model,
                fixture_segments=args.fixture_segments,
                material_id=material_id,
            )
            _print_payload(payload, fmt=args.format)
            return 0 if payload["preflight_ok"] else 1
        transcript = _build_transcript(
            episode_id=args.episode_id,
            source_audio=source_audio,
            language=args.language,
            engine=engine,
            model=args.model,
            fixture_segments=args.fixture_segments,
            material_id=material_id,
        )
    except (ValueError, VoskSttError) as exc:
        print(f"transcribe-audio failed: {exc}", file=sys.stderr)
        return 1

    issues = validate_transcript(transcript)
    if issues:
        print(f"transcribe-audio produced invalid transcript: {len(issues)} issue(s)", file=sys.stderr)
        for issue in issues:
            print(f"  {issue.code} @ {issue.field}: {issue.message}", file=sys.stderr)
        return 1

    save_transcript(transcript, output_path)
    payload = {
        "created": str(output_path).replace("\\", "/"),
        "segments": len(transcript["segments"]),
        "duration_seconds": transcript.get("source_audio", {}).get("duration_seconds"),
        "provider": transcript["stt"].get("provider"),
        "engine": transcript["stt"].get("engine"),
        "model": transcript["stt"].get("model"),
        "real_transcript": transcript["stt"].get("real_transcript"),
        "warnings": transcript["stt"].get("warnings", []),
    }
    if args.format == "json":
        _print_payload(payload, fmt=args.format)
    else:
        print(f"created: {output_path}")
        print(f"segments: {len(transcript['segments'])}")
        print(f"duration_seconds: {payload['duration_seconds']}")
        print(f"provider: {payload['provider']}")
        print(f"engine: {payload['engine']}")
        print(f"model: {payload['model']}")
        print(f"real_transcript: {str(payload['real_transcript']).lower()}")
        for warning in payload["warnings"]:
            print(f"warning: {warning}")
    return 0


def _resolve_engine(engine: str | None, provider: str | None) -> str | None:
    if engine and provider and engine != provider:
        raise ValueError("--engine and --provider must match when both are provided")
    return engine or provider


def _build_transcript(
    *,
    episode_id: str,
    source_audio: Path,
    language: str,
    engine: str,
    model: str | None,
    fixture_segments: str | None,
    material_id: str | None,
) -> dict[str, Any]:
    audio_info = try_read_wav_info(source_audio)
    common = {
        "episode_id": episode_id,
        "source_audio_path": _display_path(source_audio, Path.cwd()),
        "language": language,
        "material_id": material_id,
        "source_audio_sha256": compute_sha256(source_audio),
        "source_audio_duration_seconds": audio_info.duration_seconds if audio_info else None,
        "source_audio_sample_rate_hz": audio_info.sample_rate_hz if audio_info else None,
        "source_audio_channels": audio_info.channels if audio_info else None,
    }
    if engine == "fake":
        if not fixture_segments:
            raise ValueError("--fixture-segments is required for --engine fake")
        segments = _load_fixture_segments(Path(fixture_segments))
        warnings = []
        if not segments:
            warnings.append("fake engine fixture produced no segments")
        return build_transcript(
            **common,
            stt_engine=engine,
            stt_provider="fake",
            stt_engine_version="fake-v1",
            stt_params={
                "fixture_segments": _display_path(Path(fixture_segments), Path.cwd()),
                "language": language,
            },
            stt_warnings=warnings,
            segments=segments,
            real_transcript=False,
        )

    if engine == "vosk":
        if not model:
            raise ValueError("--model is required for --engine vosk")
        language_check = _check_vosk_model_language(language=language, model=model)
        if language_check["issues"]:
            raise ValueError(language_check["issues"][0])
        result = transcribe_vosk(
            source_audio_path=source_audio,
            model_path=Path(model),
            language=language,
        )
        stt_params = dict(result.params)
        stt_params["language_model_check"] = language_check["status"]
        if language_check["model_language"]:
            stt_params["model_language"] = language_check["model_language"]
        return build_transcript(
            **common,
            stt_engine="vosk",
            stt_provider="vosk",
            stt_engine_version=result.engine_version,
            stt_model=result.model_readback,
            stt_params=stt_params,
            stt_warnings=[
                *result.warnings,
                *language_check["warnings"],
                "real STT plumbing proof only; transcript quality is not creative acceptance",
            ],
            segments=result.segments,
            real_transcript=True,
        )

    raise ValueError(f"unsupported engine: {engine}")


def _dry_run_payload(
    *,
    engine: str,
    source_audio: Path,
    output_path: Path,
    language: str,
    model: str | None,
    fixture_segments: str | None,
    material_id: str | None,
) -> dict[str, Any]:
    issues: list[str] = []
    provider_payload: dict[str, Any] | None = None
    if engine == "fake":
        if not fixture_segments:
            issues.append("--fixture-segments is required for --engine fake")
        provider_payload = {"provider": "fake", "fixture_segments": fixture_segments}
        language_check = _empty_language_model_check(
            status="not_applicable",
            language=language,
            model=model,
        )
    elif engine == "vosk":
        if not model:
            issues.append("--model is required for --engine vosk")
            language_check = _empty_language_model_check(
                status="not_checked",
                language=language,
                model=model,
            )
        else:
            language_check = _check_vosk_model_language(language=language, model=model)
            issues.extend(language_check["issues"])
            provider_payload = preflight_vosk(source_audio_path=source_audio, model_path=Path(model))
            issues.extend(provider_payload["issues"])
    else:
        issues.append(f"unsupported engine: {engine}")
        language_check = _empty_language_model_check(
            status="not_applicable",
            language=language,
            model=model,
        )
    audio_info = try_read_wav_info(source_audio)
    return {
        "preflight_ok": not issues,
        "will_write": False,
        "engine": engine,
        "provider": engine,
        "real_transcript": engine != "fake",
        "source_audio": _display_path(source_audio, Path.cwd()),
        "output": str(output_path).replace("\\", "/"),
        "language": language,
        "model": model,
        "material_id": material_id,
        "audio": audio_info.to_dict() if audio_info else None,
        "provider_preflight": provider_payload,
        "language_model_check": language_check,
        "issues": issues,
    }


def _check_vosk_model_language(*, language: str, model: str) -> dict[str, Any]:
    language_primary = _primary_language(language)
    model_language = _infer_vosk_model_language(Path(model))
    if model_language is None:
        return _empty_language_model_check(
            status="not_inferable",
            language=language,
            model=model,
            warnings=[
                (
                    "could not infer Vosk model language from --model; ensure "
                    f"--language {language!r} matches the selected model"
                )
            ],
        )
    if language_primary != model_language:
        return _empty_language_model_check(
            status="failed",
            language=language,
            model=model,
            model_language=model_language,
            issues=[
                (
                    f"--language {language!r} does not match inferred Vosk model "
                    f"language {model_language!r} from --model {model!r}; pass "
                    f"--language {model_language} or choose a matching model"
                )
            ],
        )
    return _empty_language_model_check(
        status="passed",
        language=language,
        model=model,
        model_language=model_language,
    )


def _empty_language_model_check(
    *,
    status: str,
    language: str,
    model: str | None,
    model_language: str | None = None,
    issues: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "language": language,
        "language_primary": _primary_language(language),
        "model": model,
        "model_language": model_language,
        "issues": issues or [],
        "warnings": warnings or [],
    }


def _primary_language(language: str) -> str:
    return re.split(r"[-_]", language.strip().lower(), maxsplit=1)[0]


def _infer_vosk_model_language(model_path: Path) -> str | None:
    tokens = [token for token in re.split(r"[-_.]+", model_path.name.lower()) if token]
    try:
        model_index = tokens.index("model")
    except ValueError:
        return None
    descriptors = {
        "android",
        "big",
        "grammar",
        "large",
        "lgraph",
        "portable",
        "server",
        "small",
        "speaker",
        "spk",
    }
    for token in tokens[model_index + 1 :]:
        if token in descriptors:
            continue
        if len(token) == 2 and token.isalpha():
            return token
    return None


def _print_payload(payload: dict[str, Any], *, fmt: str) -> None:
    if fmt == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            print(f"{key}: {value}")


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
