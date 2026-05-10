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
        description="Build a read-only local preview pack from one local media file.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--local-media", required=True)
    parser.add_argument("--material-id", required=True)
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--transcript-fixture")
    parser.add_argument("--language", default="ja")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        _reject_locator(args.local_media, "--local-media")
        if args.transcript_fixture:
            _reject_locator(args.transcript_fixture, "--transcript-fixture")
        local_media = Path(args.local_media)
        if not local_media.exists() or not local_media.is_file():
            raise PreviewPackError(f"local media file not found: {local_media}")
        fixture_path = Path(args.transcript_fixture) if args.transcript_fixture else None
        if fixture_path and (not fixture_path.exists() or not fixture_path.is_file()):
            raise PreviewPackError(f"transcript fixture not found: {fixture_path}")

        root = Path(args.root)
        paths = _paths(root, args.episode_id, args.material_id)
        conflicts = _conflicts(paths, args.material_id)
        if conflicts and not args.force:
            raise PreviewPackError(
                "refusing to overwrite existing preview pack artifact(s): "
                + ", ".join(conflicts)
                + " (use --force to refresh this episode/material)"
            )

        _ensure_rights_manifest(args.episode_id, paths["rights_manifest"])
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
            duration = preview_pack.read_wav_duration_seconds(paths["source_wav"])
            fixture_path = paths["fake_segments"]
            preview_pack.write_deterministic_fake_segments(
                output_path=fixture_path,
                duration_seconds=duration,
            )

        _run_transcribe_audio(
            episode_id=args.episode_id,
            source_wav=paths["source_wav"],
            transcript_path=paths["transcript"],
            language=args.language,
            fixture_path=fixture_path,
            material_ledger=paths["material_ledger"],
            material_id=args.material_id,
            force=args.force,
        )

        duration = preview_pack.read_wav_duration_seconds(paths["source_wav"])
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
            "Keep source acquisition, output generation, and GUI execution as separate slices.",
        ]
        manifest = preview_pack.build_preview_manifest(
            episode_id=args.episode_id,
            episode_dir=paths["episode_dir"],
            input_path=local_media,
            material_id=args.material_id,
            source_wav_path=paths["source_wav"],
            fetch_receipt_path=paths["fetch_receipt"],
            transcript_path=paths["transcript"],
            transcript_source=transcript_source,
            edit_pack_path=paths["edit_pack"],
            report_path=paths["report"],
            warnings=warnings,
            next_actions=next_actions,
            base_dir=Path.cwd(),
        )
        preview_pack.write_json(manifest, paths["manifest"])
        report_html = preview_pack.make_preview_report_html(
            manifest=manifest,
            episode_dir=paths["episode_dir"],
            edit_pack_path=paths["edit_pack"],
            transcript_path=paths["transcript"],
            fetch_receipt_path=paths["fetch_receipt"],
            rights_manifest_path=paths["rights_manifest"],
            report_path=paths["report"],
        )
        preview_pack.write_text(report_html, paths["report"])
    except PreviewPackError as exc:
        print(f"build-local-preview-pack failed: {exc}", file=sys.stderr)
        return 1

    print(f"preview_manifest: {paths['manifest']}")
    print(f"preview_report: {paths['report']}")
    print(f"source_wav: {paths['source_wav']}")
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


def _conflicts(paths: dict[str, Path], material_id: str) -> list[str]:
    conflicts = []
    for key in (
        "edit_pack",
        "transcript",
        "manifest",
        "report",
        "source_wav",
        "sidecar",
        "fetch_receipt",
        "fake_segments",
    ):
        if paths[key].exists():
            conflicts.append(str(paths[key]))
    ledger_path = paths["material_ledger"]
    if ledger_path.exists():
        ledger = load_ledger(ledger_path)
        if any(m.get("id") == material_id for m in ledger.get("materials", [])):
            conflicts.append(f"{ledger_path}:material_id={material_id}")
    return conflicts


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
