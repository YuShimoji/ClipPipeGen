"""fetch-source-audio subcommand: INT-02a fake source audio material flow."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.integrations.asset_fetch import fake_audio
from src.pipeline.material_ledger import (
    LedgerError,
    build_skeleton,
    compute_sha256,
    load_ledger,
    register_material,
    save_ledger,
)
from src.pipeline.material_sidecar import save_sidecar
from src.pipeline.rights_manifest import load_rights_manifest

SCHEMA_VERSION = "v1"


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="fetch-source-audio",
        description="Create/register source_audio material. INT-02a supports fake mode only.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--material-id", required=True)
    parser.add_argument("--mode", choices=("fake",), required=True)
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--registered-by", default="tool:asset_fetch_fake")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    paths = _paths(Path(args.root), args.episode_id, args.material_id)
    preflight = _preflight(
        episode_id=args.episode_id,
        source_url=args.source_url,
        material_id=args.material_id,
        mode=args.mode,
        paths=paths,
        will_write=not args.dry_run,
    )

    rights_path = paths["rights_manifest"]
    if not rights_path.exists():
        print(f"rights_manifest not found: {rights_path}", file=sys.stderr)
        return 1

    conflicts = _conflicts(paths=paths, material_id=args.material_id)
    preflight["conflicts"] = conflicts
    preflight["would_fail_without_force"] = bool(conflicts and not args.force)

    if args.dry_run:
        json.dump(preflight, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    if conflicts and not args.force:
        print(
            "fetch-source-audio refused to overwrite/register existing artifact(s): "
            + ", ".join(conflicts)
            + " (use --force to overwrite generated files and refresh the same material id)",
            file=sys.stderr,
        )
        return 1

    print(json.dumps(preflight, ensure_ascii=False, indent=2))

    try:
        receipt = _execute_fake_fetch(
            episode_id=args.episode_id,
            source_url=args.source_url,
            material_id=args.material_id,
            registered_by=args.registered_by,
            paths=paths,
            preflight=preflight,
            force=args.force,
        )
    except (LedgerError, ValueError) as exc:
        print(f"fetch-source-audio failed: {exc}", file=sys.stderr)
        return 1

    print(f"created: {paths['audio']}")
    print(f"registered: {args.material_id} -> {paths['ledger']}")
    print(f"receipt: {paths['receipt']}")
    print(f"sha256: {receipt['sha256']}")
    return 0


def _paths(root: Path, episode_id: str, material_id: str) -> dict[str, Path]:
    episode_dir = root / episode_id
    material_dir = episode_dir / "materials" / material_id
    return {
        "episode_dir": episode_dir,
        "material_dir": material_dir,
        "rights_manifest": episode_dir / "rights_manifest.json",
        "ledger": episode_dir / "material_ledger.json",
        "audio": material_dir / "source.wav",
        "sidecar": material_dir / "sidecar.json",
        "receipt": material_dir / "fetch_receipt.json",
    }


def _preflight(
    *,
    episode_id: str,
    source_url: str,
    material_id: str,
    mode: str,
    paths: dict[str, Path],
    will_write: bool,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": mode,
        "source_url": source_url,
        "output_path": _display_path(paths["audio"], Path.cwd()),
        "sidecar_path": _display_path(paths["sidecar"], Path.cwd()),
        "receipt_path": _display_path(paths["receipt"], Path.cwd()),
        "material_ledger_path": _display_path(paths["ledger"], Path.cwd()),
        "rights_manifest_path": _display_path(paths["rights_manifest"], Path.cwd()),
        "audio_format": {
            "container": "wav",
            "codec": "pcm_s16le",
            "sample_rate_hz": fake_audio.SAMPLE_RATE_HZ,
            "channels": fake_audio.CHANNELS,
            "sample_width_bytes": fake_audio.SAMPLE_WIDTH_BYTES,
            "duration_seconds": fake_audio.DURATION_SECONDS,
        },
        "will_write": will_write,
    }


def _conflicts(*, paths: dict[str, Path], material_id: str) -> list[str]:
    conflicts: list[str] = []
    for key in ("audio", "sidecar", "receipt"):
        if paths[key].exists():
            conflicts.append(str(paths[key]))
    ledger_path = paths["ledger"]
    if ledger_path.exists():
        ledger = load_ledger(ledger_path)
        if any(m.get("id") == material_id for m in ledger.get("materials", [])):
            conflicts.append(f"{ledger_path}:material_id={material_id}")
    return conflicts


def _execute_fake_fetch(
    *,
    episode_id: str,
    source_url: str,
    material_id: str,
    registered_by: str,
    paths: dict[str, Path],
    preflight: dict[str, Any],
    force: bool,
) -> dict[str, Any]:
    rights = load_rights_manifest(paths["rights_manifest"])
    compliance = rights.get("compliance_check") or {}
    rights_status = compliance.get("status", "pending")

    if paths["ledger"].exists():
        ledger = (
            _ledger_without_material(paths["ledger"], material_id)
            if force
            else load_ledger(paths["ledger"])
        )
    else:
        ledger = build_skeleton(episode_id)

    fake_audio.write_silent_wav(paths["audio"])
    asset_hash = compute_sha256(paths["audio"])
    now = datetime.now(timezone.utc).isoformat()
    sidecar = _build_sidecar(
        material_id=material_id,
        audio_path=paths["audio"],
        asset_hash=asset_hash,
        source_url=source_url,
        retrieved_at=now,
        retrieved_by=registered_by,
    )
    save_sidecar(sidecar, paths["sidecar"])

    ledger = register_material(
        ledger,
        kind="source_audio",
        subkind=fake_audio.SUBKIND,
        file_path=_display_path(paths["audio"], Path.cwd()),
        sidecar_path=_display_path(paths["sidecar"], Path.cwd()),
        intended_uses=["editing_audio"],
        registered_by=registered_by,
        rights_manifest_id=rights.get("episode_id", episode_id),
        rights_status_at_registration=rights_status,
        material_id=material_id,
    )
    save_ledger(ledger, paths["ledger"])

    receipt = _build_receipt(
        episode_id=episode_id,
        material_id=material_id,
        source_url=source_url,
        output_path=paths["audio"],
        sha256=asset_hash,
        byte_size=paths["audio"].stat().st_size,
        created_at=now,
        preflight=preflight,
    )
    _save_json(receipt, paths["receipt"])
    return receipt


def _ledger_without_material(path: Path, material_id: str) -> dict[str, Any]:
    ledger = load_ledger(path)
    ledger = dict(ledger)
    ledger["materials"] = [
        m for m in ledger.get("materials", []) if m.get("id") != material_id
    ]
    return ledger


def _build_sidecar(
    *,
    material_id: str,
    audio_path: Path,
    asset_hash: str,
    source_url: str,
    retrieved_at: str,
    retrieved_by: str,
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "asset_id": material_id,
        "asset_path": _display_path(audio_path, Path.cwd()),
        "asset_hash_sha256": asset_hash,
        "source": {
            "kind": "unverified",
            "url": source_url,
            "retrieved_at": retrieved_at,
            "retrieved_by": retrieved_by,
            "retrieval_method": "asset_fetch_fake",
            "notes": "Fake INT-02a source audio fixture; no network download performed.",
        },
        "license": {
            "kind": "unknown",
            "guideline_url": None,
            "guideline_version_checked_at": None,
            "url": None,
            "spdx_id": None,
            "notes": "License metadata is captured as readback and must be reviewed before publishing.",
        },
        "usage_conditions": ["source_link_required"],
        "restrictions": {
            "thumbnail_use": "guideline_dependent",
            "commercial_use": "guideline_dependent",
            "modification": "guideline_dependent",
            "redistribution": "guideline_dependent",
        },
        "attribution_text": f"Source: {source_url}",
        "derived_from": None,
    }


def _build_receipt(
    *,
    episode_id: str,
    material_id: str,
    source_url: str,
    output_path: Path,
    sha256: str,
    byte_size: int,
    created_at: str,
    preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": "fake",
        "source_url": source_url,
        "output_path": _display_path(output_path, Path.cwd()),
        "sha256": sha256,
        "byte_size": byte_size,
        "created_at": created_at,
        "rollback": {
            "files": [
                preflight["output_path"],
                preflight["sidecar_path"],
                preflight["receipt_path"],
            ],
            "ledger_material_id": material_id,
        },
        "command_summary": "fetch-source-audio --mode fake",
        "preflight": preflight,
    }


def _save_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
