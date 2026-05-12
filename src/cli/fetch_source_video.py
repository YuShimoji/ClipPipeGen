"""fetch-source-video subcommand: source_video material flow."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.integrations.asset_fetch import source_video, yt_dlp_audio
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
        prog="fetch-source-video",
        description="Create/register source_video material from an existing local video file.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--source-url")
    parser.add_argument("--source-path", "--local-media", dest="source_path")
    parser.add_argument("--material-id", required=True)
    parser.add_argument("--mode", choices=("local-media-video",), required=True)
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--registered-by")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    arg_error = _mode_arg_error(args)
    if arg_error:
        print(f"fetch-source-video argument error: {arg_error}", file=sys.stderr)
        return 2

    paths = _paths(Path(args.root), args.episode_id, args.material_id, args.source_path)
    registered_by = args.registered_by or "tool:asset_fetch_local_media_video"
    preflight = _preflight(
        episode_id=args.episode_id,
        source_path=args.source_path,
        source_url=args.source_url,
        material_id=args.material_id,
        mode=args.mode,
        paths=paths,
        ffprobe_path=args.ffprobe_path,
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
            "fetch-source-video refused to overwrite/register existing artifact(s): "
            + ", ".join(conflicts)
            + " (use --force to overwrite generated files and refresh the same material id)",
            file=sys.stderr,
        )
        return 1

    print(json.dumps(preflight, ensure_ascii=False, indent=2))

    try:
        receipt = _execute_local_media_video(
            episode_id=args.episode_id,
            source_path=args.source_path,
            material_id=args.material_id,
            registered_by=registered_by,
            paths=paths,
            preflight=preflight,
            force=args.force,
            ffprobe_path=args.ffprobe_path,
        )
    except (LedgerError, ValueError, source_video.SourceVideoError) as exc:
        print(f"fetch-source-video failed: {exc}", file=sys.stderr)
        return 1

    metadata = receipt.get("video_metadata") or {}
    print(f"created: {paths['video']}")
    print(f"registered: {args.material_id} -> {paths['ledger']}")
    print(f"receipt: {paths['receipt']}")
    print(f"sha256: {receipt['sha256']}")
    print(f"duration_seconds: {metadata.get('duration_seconds')}")
    print(f"video_codec: {metadata.get('video_codec')}")
    print(f"resolution: {metadata.get('resolution')}")
    print(f"fps: {metadata.get('fps')}")
    return 0


def _mode_arg_error(args: argparse.Namespace) -> str | None:
    if args.mode == "local-media-video":
        if not args.source_path:
            return "--source-path is required when --mode local-media-video"
        if args.source_url:
            return "--mode local-media-video does not accept --source-url"
        return None
    return f"unsupported mode: {args.mode}"


def _paths(root: Path, episode_id: str, material_id: str, source_path: str) -> dict[str, Path]:
    episode_dir = root / episode_id
    material_dir = episode_dir / "materials" / material_id
    return {
        "episode_dir": episode_dir,
        "material_dir": material_dir,
        "rights_manifest": episode_dir / "rights_manifest.json",
        "ledger": episode_dir / "material_ledger.json",
        "video": material_dir / source_video.output_filename_for(source_path),
        "sidecar": material_dir / "sidecar.json",
        "receipt": material_dir / "fetch_receipt.json",
    }


def _preflight(
    *,
    episode_id: str,
    source_path: str,
    source_url: str | None,
    material_id: str,
    mode: str,
    paths: dict[str, Path],
    ffprobe_path: str | None,
    will_write: bool,
) -> dict[str, Any]:
    command_plan = source_video.build_probe_plan(
        input_path=source_path,
        ffprobe_path=ffprobe_path,
    ).to_dict()
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": mode,
        "source_url": _source_url_readback(source_url),
        "source_path": source_path,
        "source_path_exists": Path(source_path).exists() if source_path else None,
        "output_path": _display_path(paths["video"], Path.cwd()),
        "sidecar_path": _display_path(paths["sidecar"], Path.cwd()),
        "receipt_path": _display_path(paths["receipt"], Path.cwd()),
        "material_ledger_path": _display_path(paths["ledger"], Path.cwd()),
        "rights_manifest_path": _display_path(paths["rights_manifest"], Path.cwd()),
        "will_write": will_write,
        "will_call_subprocess": will_write,
        "command_plan": command_plan,
        "output_contract": {
            "kind": "source_video",
            "subkind": source_video.SUBKIND,
            "intended_uses": ["editing_video"],
            "render_or_encode": False,
        },
    }


def _conflicts(*, paths: dict[str, Path], material_id: str) -> list[str]:
    conflicts: list[str] = []
    for key in ("video", "sidecar", "receipt"):
        if paths[key].exists():
            conflicts.append(str(paths[key]))
    ledger_path = paths["ledger"]
    if ledger_path.exists():
        ledger = load_ledger(ledger_path)
        if any(m.get("id") == material_id for m in ledger.get("materials", [])):
            conflicts.append(f"{ledger_path}:material_id={material_id}")
    return conflicts


def _execute_local_media_video(
    *,
    episode_id: str,
    source_path: str,
    material_id: str,
    registered_by: str,
    paths: dict[str, Path],
    preflight: dict[str, Any],
    force: bool,
    ffprobe_path: str | None,
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

    result = source_video.copy_local_media_video(
        input_path=source_path,
        output_path=paths["video"],
        ffprobe_path=ffprobe_path,
    )
    asset_hash = compute_sha256(paths["video"])
    now = datetime.now(timezone.utc).isoformat()
    sidecar = _build_sidecar(
        material_id=material_id,
        video_path=paths["video"],
        asset_hash=asset_hash,
        source_local_path=source_path,
        retrieved_at=now,
        retrieved_by=registered_by,
        media_metadata=result.metadata,
        warnings=_warnings_for_rights(rights_status, result.warnings),
    )
    save_sidecar(sidecar, paths["sidecar"])

    ledger = register_material(
        ledger,
        kind="source_video",
        subkind=source_video.SUBKIND,
        file_path=_display_path(paths["video"], Path.cwd()),
        sidecar_path=_display_path(paths["sidecar"], Path.cwd()),
        intended_uses=["editing_video"],
        registered_by=registered_by,
        rights_manifest_id=rights.get("episode_id", episode_id),
        rights_status_at_registration=rights_status,
        material_id=material_id,
    )
    save_ledger(ledger, paths["ledger"])

    receipt = _build_receipt(
        episode_id=episode_id,
        material_id=material_id,
        source_path=source_path,
        output_path=paths["video"],
        sha256=asset_hash,
        byte_size=paths["video"].stat().st_size,
        created_at=now,
        preflight=preflight,
        result=result,
        rights_status=rights_status,
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
    video_path: Path,
    asset_hash: str,
    source_local_path: str,
    retrieved_at: str,
    retrieved_by: str,
    media_metadata: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "asset_id": material_id,
        "asset_path": _display_path(video_path, Path.cwd()),
        "asset_hash_sha256": asset_hash,
        "source": {
            "kind": "unverified",
            "url": None,
            "local_path": source_local_path,
            "retrieved_at": retrieved_at,
            "retrieved_by": retrieved_by,
            "retrieval_method": source_video.RETRIEVAL_METHOD,
            "notes": (
                "Local source video copied into material storage without "
                "render/encode. Rights and creative acceptance remain user-owned."
            ),
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
        "attribution_text": f"Local video source: {source_local_path}",
        "derived_from": None,
        "media_metadata": media_metadata,
        "warnings": warnings,
    }


def _build_receipt(
    *,
    episode_id: str,
    material_id: str,
    source_path: str,
    output_path: Path,
    sha256: str,
    byte_size: int,
    created_at: str,
    preflight: dict[str, Any],
    result: source_video.LocalVideoResult,
    rights_status: str,
) -> dict[str, Any]:
    output_display = _display_path(output_path, Path.cwd())
    probe = result.probe_result
    warnings = _warnings_for_rights(rights_status, result.warnings)
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": "local-media-video",
        "source_url": None,
        "output_path": output_display,
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
        "command_summary": "fetch-source-video --mode local-media-video",
        "provider": source_video.PROVIDER,
        "tools": [
            {
                "name": "ffprobe",
                "path": probe.ffprobe_path,
                "path_source": probe.ffprobe_path_source,
                "version": probe.ffprobe_version,
            }
        ],
        "commands": [
            {
                "summary": probe.command_summary,
                "exit_code": probe.exit_code,
            }
        ],
        "input": {
            "source_url": None,
            "local_path": str(source_path).replace("\\", "/"),
        },
        "intermediate": {
            "retained": False,
            "strategy": "none; local source video copied directly",
        },
        "outputs": [
            {
                "path": output_display,
                "sha256": sha256,
                "byte_size": byte_size,
                "duration_seconds": result.metadata.get("duration_seconds"),
                "metadata": result.metadata,
            }
        ],
        "video_metadata": result.metadata,
        "warnings": warnings,
        "stderr_digest": probe.stderr_digest,
        "rights_snapshot": {
            "compliance_status_at_fetch": rights_status,
            "hard_gate": False,
        },
        "preflight": preflight,
    }


def _warnings_for_rights(rights_status: str, warnings: list[str]) -> list[str]:
    out = list(warnings)
    if rights_status != "passed":
        out.append(
            f"rights status at fetch is {rights_status}; user review required before production/publishing"
        )
    if "source video acquisition is not production/creative/publish acceptance" not in out:
        out.append("source video acquisition is not production/creative/publish acceptance")
    return out


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


def _source_url_readback(source_url: str | None) -> str | None:
    return yt_dlp_audio.scrub_url_for_readback(source_url)
