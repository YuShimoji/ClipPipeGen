"""build-local-preview-pack subcommand: local media -> read-only review pack."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.cli import (
    check_cut_context,
    fetch_source_audio,
    generate_cuts,
    generate_subtitles,
    transcribe_audio,
)
from src.pipeline import preview_pack
from src.pipeline.edit_pack import build_skeleton as build_edit_skeleton
from src.pipeline.edit_pack import save_edit_pack
from src.pipeline.material_ledger import load_ledger
from src.pipeline.rights_manifest import build_skeleton as build_rights_skeleton
from src.pipeline.rights_manifest import load_rights_manifest, save_rights_manifest


class PreviewPackError(Exception):
    """Raised when SH-05 cannot complete the local review pack."""


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-local-preview-pack",
        description="Build a read-only local preview pack from local media or an existing source audio material.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--local-media")
    parser.add_argument("--material-id", required=True)
    parser.add_argument(
        "--use-existing-source-audio",
        action="store_true",
        help="Consume an existing source_audio material entry without acquiring media again.",
    )
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--transcript-fixture")
    parser.add_argument("--language", default="ja")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        if not args.use_existing_source_audio and not args.local_media:
            raise PreviewPackError("--local-media is required unless --use-existing-source-audio is set")
        if args.use_existing_source_audio and args.local_media:
            raise PreviewPackError("--local-media is not used with --use-existing-source-audio")
        if args.local_media:
            _reject_locator(args.local_media, "--local-media")
        if args.transcript_fixture:
            _reject_locator(args.transcript_fixture, "--transcript-fixture")
        local_media = Path(args.local_media) if args.local_media else None
        if local_media and (not local_media.exists() or not local_media.is_file()):
            raise PreviewPackError(f"local media file not found: {local_media}")
        fixture_path = Path(args.transcript_fixture) if args.transcript_fixture else None
        if fixture_path and (not fixture_path.exists() or not fixture_path.is_file()):
            raise PreviewPackError(f"transcript fixture not found: {fixture_path}")

        root = Path(args.root)
        paths = _paths(root, args.episode_id, args.material_id)
        conflicts = _conflicts(
            paths,
            args.material_id,
            use_existing_source_audio=args.use_existing_source_audio,
        )
        if conflicts and not args.force:
            raise PreviewPackError(
                "refusing to overwrite existing preview pack artifact(s): "
                + ", ".join(conflicts)
                + " (use --force to refresh this episode/material)"
            )

        _ensure_rights_manifest(args.episode_id, paths["rights_manifest"])
        input_kind = "local_media_file"
        input_path = local_media
        source_wav = paths["source_wav"]
        sidecar = paths["sidecar"]
        fetch_receipt = paths["fetch_receipt"]
        if args.use_existing_source_audio:
            existing = _resolve_existing_source_audio(paths, args.material_id)
            source_wav = existing["source_wav"]
            sidecar = existing["sidecar"]
            fetch_receipt = existing["fetch_receipt"]
            input_path = source_wav
            input_kind = "existing_source_audio_material"
        else:
            _run_fetch_source_audio(
                episode_id=args.episode_id,
                root=root,
                local_media=local_media,
                material_id=args.material_id,
                force=args.force,
            )
        _write_edit_pack_skeleton(
            episode_id=args.episode_id,
            episode_dir=paths["episode_dir"],
            output_path=paths["edit_pack"],
        )

        transcript_source = "fixture" if fixture_path else "deterministic_fake"
        if fixture_path is None:
            duration = preview_pack.read_wav_duration_seconds(source_wav)
            fixture_path = paths["fake_segments"]
            preview_pack.write_deterministic_fake_segments(
                output_path=fixture_path,
                duration_seconds=duration,
            )

        _run_transcribe_audio(
            episode_id=args.episode_id,
            source_wav=source_wav,
            transcript_path=paths["transcript"],
            language=args.language,
            fixture_path=fixture_path,
            material_ledger=paths["material_ledger"],
            material_id=args.material_id,
            force=args.force,
        )

        duration = preview_pack.read_wav_duration_seconds(source_wav)
        target_duration = max(1.0, min(duration or 12.0, 20.0))
        _run_generate_cuts(
            transcript_path=paths["transcript"],
            edit_pack_path=paths["edit_pack"],
            target_duration=target_duration,
            min_duration=min(target_duration, 5.0),
            max_duration=max(target_duration * 1.5, target_duration),
        )
        _run_check_cut_context(
            transcript_path=paths["transcript"],
            edit_pack_path=paths["edit_pack"],
        )
        _run_generate_subtitles(
            transcript_path=paths["transcript"],
            edit_pack_path=paths["edit_pack"],
        )

        warnings = _warnings(
            transcript_source=transcript_source,
            rights_manifest_path=paths["rights_manifest"],
            edit_pack_path=paths["edit_pack"],
        )
        next_actions = [
            "Review preview_report.html before moving to external acquisition or output work.",
            "Replace fake or fixture transcript with reviewed transcript before acceptance.",
            "Treat the generated edit_pack as a preview draft until transcript quality is accepted.",
            "Keep source acquisition, output generation, and GUI execution as separate slices.",
        ]
        manifest = preview_pack.build_preview_manifest(
            episode_id=args.episode_id,
            episode_dir=paths["episode_dir"],
            input_path=input_path,
            material_id=args.material_id,
            source_wav_path=source_wav,
            fetch_receipt_path=fetch_receipt,
            sidecar_path=sidecar,
            material_ledger_path=paths["material_ledger"],
            transcript_path=paths["transcript"],
            transcript_source=transcript_source,
            edit_pack_path=paths["edit_pack"],
            report_path=paths["report"],
            warnings=warnings,
            next_actions=next_actions,
            base_dir=Path.cwd(),
            input_kind=input_kind,
        )
        manifest_issues = preview_pack.validate_preview_manifest(manifest)
        if manifest_issues:
            raise PreviewPackError("preview_manifest validation failed: " + "; ".join(manifest_issues))
        preview_pack.write_json(manifest, paths["manifest"])
        report_html = preview_pack.make_preview_report_html(
            manifest=manifest,
            source_wav_path=source_wav,
            edit_pack_path=paths["edit_pack"],
            transcript_path=paths["transcript"],
            fetch_receipt_path=fetch_receipt,
            sidecar_path=sidecar,
            material_ledger_path=paths["material_ledger"],
            rights_manifest_path=paths["rights_manifest"],
            manifest_path=paths["manifest"],
            report_path=paths["report"],
        )
        preview_pack.write_text(report_html, paths["report"])
    except PreviewPackError as exc:
        print(f"build-local-preview-pack failed: {exc}", file=sys.stderr)
        return 1

    print(f"preview_manifest: {paths['manifest']}")
    print(f"preview_report: {paths['report']}")
    print(f"source_wav: {source_wav}")
    print(f"transcript_source: {transcript_source}")
    print(f"cut_candidates: {manifest['cuts']['candidate_count']}")
    print(f"subtitles: {manifest['subtitles']['subtitle_count']}")
    return 0


def _reject_locator(value: str, field: str) -> None:
    if "://" in value:
        raise PreviewPackError(f"{field} accepts local files only")


def _paths(root: Path, episode_id: str, material_id: str) -> dict[str, Path]:
    episode_dir = root / episode_id
    material_dir = episode_dir / "materials" / material_id
    preview_dir = episode_dir / preview_pack.PREVIEW_WORK_DIR
    return {
        "episode_dir": episode_dir,
        "rights_manifest": episode_dir / "rights_manifest.json",
        "material_ledger": episode_dir / "material_ledger.json",
        "edit_pack": episode_dir / "edit_pack.json",
        "transcript": episode_dir / "transcript.json",
        "manifest": episode_dir / "preview_manifest.json",
        "report": episode_dir / "preview_report.html",
        "source_wav": material_dir / "source.wav",
        "sidecar": material_dir / "sidecar.json",
        "fetch_receipt": material_dir / "fetch_receipt.json",
        "fake_segments": preview_dir / preview_pack.FAKE_SEGMENTS_FILENAME,
    }


def _conflicts(
    paths: dict[str, Path],
    material_id: str,
    *,
    use_existing_source_audio: bool,
) -> list[str]:
    conflicts = []
    keys = (
        "edit_pack",
        "transcript",
        "manifest",
        "report",
        "fake_segments",
    )
    if not use_existing_source_audio:
        keys = (*keys, "source_wav", "sidecar", "fetch_receipt")
    for key in keys:
        if paths[key].exists():
            conflicts.append(str(paths[key]))
    ledger_path = paths["material_ledger"]
    if ledger_path.exists() and not use_existing_source_audio:
        ledger = load_ledger(ledger_path)
        if any(m.get("id") == material_id for m in ledger.get("materials", [])):
            conflicts.append(f"{ledger_path}:material_id={material_id}")
    return conflicts


def _resolve_existing_source_audio(paths: dict[str, Path], material_id: str) -> dict[str, Path]:
    ledger_path = paths["material_ledger"]
    if not ledger_path.exists():
        raise PreviewPackError(f"material_ledger not found: {ledger_path}")
    ledger = load_ledger(ledger_path)
    material = next(
        (m for m in ledger.get("materials", []) if isinstance(m, dict) and m.get("id") == material_id),
        None,
    )
    if material is None:
        raise PreviewPackError(f"material id not found in ledger: {material_id}")
    if material.get("kind") != "source_audio":
        raise PreviewPackError(
            f"material {material_id!r} must be kind='source_audio' (actual={material.get('kind')!r})"
        )
    source_wav = _resolve_material_path(material.get("file_path"), ledger_path=ledger_path)
    sidecar = _resolve_material_path(material.get("sidecar_path"), ledger_path=ledger_path)
    fetch_receipt = source_wav.parent / "fetch_receipt.json"
    if not fetch_receipt.exists():
        fetch_receipt = paths["fetch_receipt"]
    for label, path in (
        ("source.wav", source_wav),
        ("sidecar.json", sidecar),
        ("fetch_receipt.json", fetch_receipt),
    ):
        if not path.exists() or not path.is_file():
            raise PreviewPackError(f"{label} not found for existing source audio material: {path}")
    return {
        "source_wav": source_wav,
        "sidecar": sidecar,
        "fetch_receipt": fetch_receipt,
    }


def _resolve_material_path(value: object, *, ledger_path: Path) -> Path:
    if not isinstance(value, str) or not value:
        raise PreviewPackError("material ledger entry is missing file path readback")
    raw = Path(value)
    candidates = [raw]
    if not raw.is_absolute():
        candidates.extend([Path.cwd() / raw, ledger_path.parent / raw])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _ensure_rights_manifest(episode_id: str, path: Path) -> None:
    if path.exists():
        return
    save_rights_manifest(build_rights_skeleton(episode_id), path)


def _write_edit_pack_skeleton(*, episode_id: str, episode_dir: Path, output_path: Path) -> None:
    pack = build_edit_skeleton(
        episode_id,
        rights_manifest_path=str(episode_dir / "rights_manifest.json").replace("\\", "/"),
        material_ledger_path=str(episode_dir / "material_ledger.json").replace("\\", "/"),
    )
    save_edit_pack(pack, output_path)


def _run_fetch_source_audio(
    *,
    episode_id: str,
    root: Path,
    local_media: Path,
    material_id: str,
    force: bool,
) -> None:
    argv = [
        "--episode-id",
        episode_id,
        "--root",
        str(root),
        "--local-media",
        str(local_media),
        "--material-id",
        material_id,
        "--mode",
        "local-media-audio",
    ]
    if force:
        argv.append("--force")
    _run_step("fetch-source-audio", fetch_source_audio.run, argv)


def _run_transcribe_audio(
    *,
    episode_id: str,
    source_wav: Path,
    transcript_path: Path,
    language: str,
    fixture_path: Path,
    material_ledger: Path,
    material_id: str,
    force: bool,
) -> None:
    argv = [
        "--episode-id",
        episode_id,
        "--source-audio",
        str(source_wav),
        "--output",
        str(transcript_path),
        "--language",
        language,
        "--engine",
        "fake",
        "--fixture-segments",
        str(fixture_path),
        "--material-ledger",
        str(material_ledger),
        "--material-id",
        material_id,
    ]
    if force:
        argv.append("--force")
    _run_step("transcribe-audio", transcribe_audio.run, argv)


def _run_generate_cuts(
    *,
    transcript_path: Path,
    edit_pack_path: Path,
    target_duration: float,
    min_duration: float,
    max_duration: float,
) -> None:
    argv = [
        "--transcript",
        str(transcript_path),
        "--edit-pack",
        str(edit_pack_path),
        "--target-duration-seconds",
        f"{target_duration:.3f}",
        "--min-duration-seconds",
        f"{min_duration:.3f}",
        "--max-duration-seconds",
        f"{max_duration:.3f}",
        "--max-candidates",
        "5",
    ]
    _run_step("generate-cuts", generate_cuts.run, argv)


def _run_check_cut_context(*, transcript_path: Path, edit_pack_path: Path) -> None:
    _run_step(
        "check-cut-context",
        check_cut_context.run,
        ["--transcript", str(transcript_path), "--edit-pack", str(edit_pack_path)],
    )


def _run_generate_subtitles(*, transcript_path: Path, edit_pack_path: Path) -> None:
    _run_step(
        "generate-subtitles",
        generate_subtitles.run,
        ["--transcript", str(transcript_path), "--edit-pack", str(edit_pack_path)],
    )


def _run_step(label: str, handler, argv: list[str]) -> None:
    code = handler(argv)
    if code != 0:
        raise PreviewPackError(f"{label} failed with exit code {code}")


def _warnings(
    *,
    transcript_source: str,
    rights_manifest_path: Path,
    edit_pack_path: Path,
) -> list[str]:
    warnings = [
        f"transcript source is {transcript_source}; transcript.not_for_acceptance is true",
        "fake or fixture transcript and generated edit_pack are preview-only, not production candidates",
    ]
    rights = load_rights_manifest(rights_manifest_path)
    compliance = rights.get("compliance_check") or {}
    status = compliance.get("status", "unknown")
    if status != "passed":
        warnings.append(f"rights status is {status}; this is readback only")
    edit_pack = json.loads(edit_pack_path.read_text(encoding="utf-8"))
    if not edit_pack.get("cut_candidates"):
        warnings.append("no cut candidates were generated")
    if not edit_pack.get("subtitles"):
        warnings.append("no subtitle drafts were generated")
    return warnings
