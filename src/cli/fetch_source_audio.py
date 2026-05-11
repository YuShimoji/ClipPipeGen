"""fetch-source-audio subcommand: source_audio material flow."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.integrations.asset_fetch import fake_audio, ffmpeg_audio, yt_dlp_audio
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
        description="Create/register source_audio material.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--source-url")
    parser.add_argument("--local-media")
    parser.add_argument("--material-id", required=True)
    parser.add_argument(
        "--mode",
        choices=("fake", "local-media-audio", "yt-dlp-audio"),
        required=True,
    )
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--yt-dlp-path")
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--registered-by")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    arg_error = _mode_arg_error(args)
    if arg_error:
        print(f"fetch-source-audio argument error: {arg_error}", file=sys.stderr)
        return 2

    paths = _paths(Path(args.root), args.episode_id, args.material_id)
    registered_by = args.registered_by or _default_registered_by(args.mode)
    preflight = _preflight(
        episode_id=args.episode_id,
        source_url=args.source_url,
        local_media=args.local_media,
        material_id=args.material_id,
        mode=args.mode,
        paths=paths,
        ffmpeg_path=args.ffmpeg_path,
        yt_dlp_path=args.yt_dlp_path,
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
        if args.mode == "fake":
            receipt = _execute_fake_fetch(
                episode_id=args.episode_id,
                source_url=args.source_url,
                material_id=args.material_id,
                registered_by=registered_by,
                paths=paths,
                preflight=preflight,
                force=args.force,
            )
        elif args.mode == "local-media-audio":
            receipt = _execute_local_media_audio(
                episode_id=args.episode_id,
                local_media=args.local_media,
                material_id=args.material_id,
                registered_by=registered_by,
                paths=paths,
                preflight=preflight,
                force=args.force,
                ffmpeg_path=args.ffmpeg_path,
            )
        else:
            receipt = _execute_yt_dlp_audio(
                episode_id=args.episode_id,
                source_url=args.source_url,
                material_id=args.material_id,
                registered_by=registered_by,
                paths=paths,
                preflight=preflight,
                force=args.force,
                yt_dlp_path=args.yt_dlp_path,
                ffmpeg_path=args.ffmpeg_path,
            )
    except (LedgerError, ValueError) as exc:
        print(f"fetch-source-audio failed: {exc}", file=sys.stderr)
        return 1
    except ffmpeg_audio.FfmpegError as exc:
        print(f"fetch-source-audio failed: {exc}", file=sys.stderr)
        return 1
    except yt_dlp_audio.YtDlpAudioError as exc:
        print(f"fetch-source-audio failed: {exc}", file=sys.stderr)
        return 1

    print(f"created: {paths['audio']}")
    print(f"registered: {args.material_id} -> {paths['ledger']}")
    print(f"receipt: {paths['receipt']}")
    print(f"sha256: {receipt['sha256']}")
    return 0


def _mode_arg_error(args: argparse.Namespace) -> str | None:
    if args.mode == "fake":
        if not args.source_url:
            return "--source-url is required when --mode fake"
        if args.local_media:
            return "--local-media is only valid when --mode local-media-audio"
        if args.ffmpeg_path:
            return "--ffmpeg-path is only valid when --mode local-media-audio or --mode yt-dlp-audio"
        if args.yt_dlp_path:
            return "--yt-dlp-path is only valid when --mode yt-dlp-audio"
        return None
    if args.mode == "local-media-audio":
        if not args.local_media:
            return "--local-media is required when --mode local-media-audio"
        if args.source_url:
            return "--mode local-media-audio does not accept --source-url"
        if args.yt_dlp_path:
            return "--yt-dlp-path is only valid when --mode yt-dlp-audio"
        return None
    if args.mode == "yt-dlp-audio":
        if not args.source_url:
            return "--source-url is required when --mode yt-dlp-audio"
        if args.local_media:
            return "--local-media is only valid when --mode local-media-audio"
        return None
    return f"unsupported mode: {args.mode}"


def _default_registered_by(mode: str) -> str:
    if mode == "yt-dlp-audio":
        return "tool:asset_fetch_yt_dlp_audio"
    if mode == "local-media-audio":
        return "tool:asset_fetch_local_media_audio"
    return "tool:asset_fetch_fake"


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
    source_url: str | None,
    local_media: str | None,
    material_id: str,
    mode: str,
    paths: dict[str, Path],
    ffmpeg_path: str | None,
    yt_dlp_path: str | None,
    will_write: bool,
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": mode,
        "source_url": source_url,
        "local_media_path": local_media,
        "local_media_exists": Path(local_media).exists() if local_media else None,
        "output_path": _display_path(paths["audio"], Path.cwd()),
        "sidecar_path": _display_path(paths["sidecar"], Path.cwd()),
        "receipt_path": _display_path(paths["receipt"], Path.cwd()),
        "material_ledger_path": _display_path(paths["ledger"], Path.cwd()),
        "rights_manifest_path": _display_path(paths["rights_manifest"], Path.cwd()),
        "audio_format": _audio_format_for_mode(mode),
        "will_write": will_write,
    }
    if mode == "local-media-audio":
        payload["command_plan"] = ffmpeg_audio.build_plan(
            input_path=local_media or "",
            output_path=paths["audio"],
            ffmpeg_path=ffmpeg_path,
        ).to_dict()
        payload["will_call_subprocess"] = will_write
    elif mode == "yt-dlp-audio":
        payload["command_plan"] = yt_dlp_audio.build_plan(
            source_url=source_url or "",
            output_path=paths["audio"],
            yt_dlp_path=yt_dlp_path,
            ffmpeg_path=ffmpeg_path,
        ).to_dict()
        payload["will_call_subprocess"] = will_write
    else:
        payload["command_plan"] = None
        payload["will_call_subprocess"] = False
    return payload


def _audio_format_for_mode(mode: str) -> dict[str, Any]:
    if mode in {"local-media-audio", "yt-dlp-audio"}:
        return ffmpeg_audio.audio_format()
    return {
        "container": "wav",
        "codec": "pcm_s16le",
        "sample_rate_hz": fake_audio.SAMPLE_RATE_HZ,
        "channels": fake_audio.CHANNELS,
        "sample_width_bytes": fake_audio.SAMPLE_WIDTH_BYTES,
        "duration_seconds": fake_audio.DURATION_SECONDS,
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


def _execute_local_media_audio(
    *,
    episode_id: str,
    local_media: str,
    material_id: str,
    registered_by: str,
    paths: dict[str, Path],
    preflight: dict[str, Any],
    force: bool,
    ffmpeg_path: str | None,
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

    result = ffmpeg_audio.normalize_local_media_audio(
        input_path=local_media,
        output_path=paths["audio"],
        ffmpeg_path=ffmpeg_path,
    )
    asset_hash = compute_sha256(paths["audio"])
    now = datetime.now(timezone.utc).isoformat()
    sidecar = _build_sidecar(
        material_id=material_id,
        audio_path=paths["audio"],
        asset_hash=asset_hash,
        source_url=None,
        source_local_path=local_media,
        retrieved_at=now,
        retrieved_by=registered_by,
        retrieval_method=ffmpeg_audio.RETRIEVAL_METHOD,
        source_notes=(
            "Local media source normalized by FFmpeg inside asset_fetch; "
            "no URL/VOD/network fetch performed."
        ),
    )
    save_sidecar(sidecar, paths["sidecar"])

    ledger = register_material(
        ledger,
        kind="source_audio",
        subkind=ffmpeg_audio.SUBKIND,
        file_path=_display_path(paths["audio"], Path.cwd()),
        sidecar_path=_display_path(paths["sidecar"], Path.cwd()),
        intended_uses=["editing_audio"],
        registered_by=registered_by,
        rights_manifest_id=rights.get("episode_id", episode_id),
        rights_status_at_registration=rights_status,
        material_id=material_id,
    )
    save_ledger(ledger, paths["ledger"])

    receipt = _build_local_media_receipt(
        episode_id=episode_id,
        material_id=material_id,
        local_media=local_media,
        output_path=paths["audio"],
        sha256=asset_hash,
        byte_size=paths["audio"].stat().st_size,
        created_at=now,
        preflight=preflight,
        normalize_result=result,
    )
    _save_json(receipt, paths["receipt"])
    return receipt


def _execute_yt_dlp_audio(
    *,
    episode_id: str,
    source_url: str,
    material_id: str,
    registered_by: str,
    paths: dict[str, Path],
    preflight: dict[str, Any],
    force: bool,
    yt_dlp_path: str | None,
    ffmpeg_path: str | None,
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

    result = yt_dlp_audio.fetch_url_audio(
        source_url=source_url,
        output_path=paths["audio"],
        yt_dlp_path=yt_dlp_path,
        ffmpeg_path=ffmpeg_path,
    )
    asset_hash = compute_sha256(paths["audio"])
    now = datetime.now(timezone.utc).isoformat()
    sidecar = _build_sidecar(
        material_id=material_id,
        audio_path=paths["audio"],
        asset_hash=asset_hash,
        source_url=source_url,
        retrieved_at=now,
        retrieved_by=registered_by,
        retrieval_method=yt_dlp_audio.RETRIEVAL_METHOD,
        source_notes=(
            "Source audio fetched from URL by yt-dlp inside asset_fetch and "
            "normalized by FFmpeg; downloaded intermediate media is not retained."
        ),
    )
    save_sidecar(sidecar, paths["sidecar"])

    ledger = register_material(
        ledger,
        kind="source_audio",
        subkind=yt_dlp_audio.SUBKIND,
        file_path=_display_path(paths["audio"], Path.cwd()),
        sidecar_path=_display_path(paths["sidecar"], Path.cwd()),
        intended_uses=["editing_audio"],
        registered_by=registered_by,
        rights_manifest_id=rights.get("episode_id", episode_id),
        rights_status_at_registration=rights_status,
        material_id=material_id,
    )
    save_ledger(ledger, paths["ledger"])

    receipt = _build_yt_dlp_audio_receipt(
        episode_id=episode_id,
        material_id=material_id,
        source_url=source_url,
        output_path=paths["audio"],
        sha256=asset_hash,
        byte_size=paths["audio"].stat().st_size,
        created_at=now,
        preflight=preflight,
        fetch_result=result,
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
    audio_path: Path,
    asset_hash: str,
    source_url: str | None,
    source_local_path: str | None = None,
    retrieved_at: str,
    retrieved_by: str,
    retrieval_method: str = "asset_fetch_fake",
    source_notes: str = "Fake INT-02a source audio fixture; no network download performed.",
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "asset_id": material_id,
        "asset_path": _display_path(audio_path, Path.cwd()),
        "asset_hash_sha256": asset_hash,
        "source": {
            "kind": "unverified",
            "url": source_url,
            "local_path": source_local_path,
            "retrieved_at": retrieved_at,
            "retrieved_by": retrieved_by,
            "retrieval_method": retrieval_method,
            "notes": source_notes,
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
        "attribution_text": _attribution_text(source_url, source_local_path),
        "derived_from": None,
    }


def _attribution_text(source_url: str | None, source_local_path: str | None) -> str:
    if source_url:
        return f"Source: {source_url}"
    return f"Local media source: {source_local_path}"


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
        "provider": "asset_fetch_fake",
        "tools": [],
        "commands": [],
        "input": {
            "source_url": source_url,
            "local_path": None,
        },
        "outputs": [
            {
                "path": _display_path(output_path, Path.cwd()),
                "sha256": sha256,
                "byte_size": byte_size,
                "duration_seconds": preflight["audio_format"]["duration_seconds"],
            }
        ],
        "warnings": [],
        "stderr_digest": None,
        "preflight": preflight,
    }


def _build_local_media_receipt(
    *,
    episode_id: str,
    material_id: str,
    local_media: str,
    output_path: Path,
    sha256: str,
    byte_size: int,
    created_at: str,
    preflight: dict[str, Any],
    normalize_result: ffmpeg_audio.NormalizeResult,
) -> dict[str, Any]:
    output_display = _display_path(output_path, Path.cwd())
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": "local-media-audio",
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
        "command_summary": "fetch-source-audio --mode local-media-audio",
        "provider": ffmpeg_audio.PROVIDER,
        "tools": [
            {
                "name": "ffmpeg",
                "path": normalize_result.ffmpeg_path,
                "path_source": normalize_result.ffmpeg_path_source,
                "version": normalize_result.ffmpeg_version,
            }
        ],
        "commands": [
            {
                "summary": normalize_result.command_summary,
                "exit_code": normalize_result.exit_code,
            }
        ],
        "input": {
            "source_url": None,
            "local_path": str(local_media).replace("\\", "/"),
        },
        "outputs": [
            {
                "path": output_display,
                "sha256": sha256,
                "byte_size": byte_size,
                "duration_seconds": normalize_result.duration_seconds,
            }
        ],
        "warnings": normalize_result.warnings,
        "stderr_digest": normalize_result.stderr_digest,
        "preflight": preflight,
    }


def _build_yt_dlp_audio_receipt(
    *,
    episode_id: str,
    material_id: str,
    source_url: str,
    output_path: Path,
    sha256: str,
    byte_size: int,
    created_at: str,
    preflight: dict[str, Any],
    fetch_result: yt_dlp_audio.YtDlpAudioResult,
    rights_status: str,
) -> dict[str, Any]:
    output_display = _display_path(output_path, Path.cwd())
    ffmpeg_result = fetch_result.ffmpeg_result
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": "yt-dlp-audio",
        "source_url": source_url,
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
        "command_summary": "fetch-source-audio --mode yt-dlp-audio",
        "provider": yt_dlp_audio.PROVIDER,
        "tools": [
            {
                "name": "yt-dlp",
                "path": fetch_result.yt_dlp_path,
                "path_source": fetch_result.yt_dlp_path_source,
                "version": fetch_result.yt_dlp_version,
            },
            {
                "name": "ffmpeg",
                "path": ffmpeg_result.ffmpeg_path,
                "path_source": ffmpeg_result.ffmpeg_path_source,
                "version": ffmpeg_result.ffmpeg_version,
            },
        ],
        "commands": [
            {
                "summary": fetch_result.yt_dlp_command_summary,
                "exit_code": fetch_result.yt_dlp_exit_code,
            },
            {
                "summary": ffmpeg_result.command_summary,
                "exit_code": ffmpeg_result.exit_code,
            },
        ],
        "input": {
            "source_url": source_url,
            "local_path": None,
        },
        "intermediate": {
            "name": fetch_result.downloaded_intermediate_name,
            "byte_size": fetch_result.downloaded_intermediate_byte_size,
            "retained": fetch_result.intermediate_retained,
        },
        "outputs": [
            {
                "path": output_display,
                "sha256": sha256,
                "byte_size": byte_size,
                "duration_seconds": ffmpeg_result.duration_seconds,
            }
        ],
        "warnings": fetch_result.warnings,
        "stderr_digest": fetch_result.stderr_digest,
        "tool_stderr_digests": {
            "yt_dlp": fetch_result.yt_dlp_stderr_digest,
            "ffmpeg": ffmpeg_result.stderr_digest,
        },
        "rights_snapshot": {
            "compliance_status_at_fetch": rights_status,
            "hard_gate": False,
        },
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
