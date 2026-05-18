"""fetch-source-video subcommand: source_video material flow."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.integrations.asset_fetch import source_video, yt_dlp_audio, yt_dlp_video
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
        description=(
            "Create/register source_video material from a local video file "
            "(local-media-video) or a URL fetched via yt-dlp (yt-dlp-video)."
        ),
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--source-url")
    parser.add_argument("--source-path", "--local-media", dest="source_path")
    parser.add_argument("--material-id", required=True)
    parser.add_argument(
        "--mode",
        choices=("local-media-video", "yt-dlp-video"),
        required=True,
    )
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--yt-dlp-path")
    parser.add_argument(
        "--format-selector",
        default=yt_dlp_video.DEFAULT_FORMAT_SELECTOR,
        help=(
            "yt-dlp -f expression used in --mode yt-dlp-video; defaults to "
            "best[ext=mp4]/best[ext=mkv]/best[ext=webm]/best"
        ),
    )
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--registered-by")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    arg_error = _mode_arg_error(args)
    if arg_error:
        print(f"fetch-source-video argument error: {arg_error}", file=sys.stderr)
        return 2

    paths = _paths(
        Path(args.root),
        args.episode_id,
        args.material_id,
        args.source_path,
        args.mode,
    )
    registered_by = args.registered_by or _default_registered_by(args.mode)
    preflight = _preflight(
        episode_id=args.episode_id,
        source_path=args.source_path,
        source_url=args.source_url,
        material_id=args.material_id,
        mode=args.mode,
        paths=paths,
        ffprobe_path=args.ffprobe_path,
        yt_dlp_path=args.yt_dlp_path,
        format_selector=args.format_selector,
        will_write=not args.dry_run,
    )

    rights_path = paths["rights_manifest"]
    if not rights_path.exists():
        print(f"rights_manifest not found: {rights_path}", file=sys.stderr)
        return 1

    conflicts = _conflicts(paths=paths, material_id=args.material_id, mode=args.mode)
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
        if args.mode == "local-media-video":
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
        else:
            receipt = _execute_yt_dlp_video(
                episode_id=args.episode_id,
                source_url=args.source_url,
                material_id=args.material_id,
                registered_by=registered_by,
                paths=paths,
                preflight=preflight,
                force=args.force,
                yt_dlp_path=args.yt_dlp_path,
                ffprobe_path=args.ffprobe_path,
                format_selector=args.format_selector,
            )
    except (LedgerError, ValueError, source_video.SourceVideoError) as exc:
        print(f"fetch-source-video failed: {exc}", file=sys.stderr)
        return 1
    except yt_dlp_video.YtDlpVideoError as exc:
        print(f"fetch-source-video failed: {exc}", file=sys.stderr)
        return 1

    metadata = receipt.get("video_metadata") or {}
    print(f"created: {receipt['output_path']}")
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
        if args.yt_dlp_path:
            return "--yt-dlp-path is only valid when --mode yt-dlp-video"
        return None
    if args.mode == "yt-dlp-video":
        if not args.source_url:
            return "--source-url is required when --mode yt-dlp-video"
        if args.source_path:
            return "--mode yt-dlp-video does not accept --source-path/--local-media"
        return None
    return f"unsupported mode: {args.mode}"


def _default_registered_by(mode: str) -> str:
    if mode == "yt-dlp-video":
        return "tool:asset_fetch_yt_dlp_video"
    return "tool:asset_fetch_local_media_video"


def _paths(
    root: Path,
    episode_id: str,
    material_id: str,
    source_path: str | None,
    mode: str,
) -> dict[str, Path | None]:
    episode_dir = root / episode_id
    material_dir = episode_dir / "materials" / material_id
    if mode == "local-media-video":
        video_path: Path | None = material_dir / source_video.output_filename_for(
            source_path or ""
        )
    else:
        # yt-dlp-video: extension is decided by yt-dlp at download time.
        video_path = None
    return {
        "episode_dir": episode_dir,
        "material_dir": material_dir,
        "rights_manifest": episode_dir / "rights_manifest.json",
        "ledger": episode_dir / "material_ledger.json",
        "video": video_path,
        "sidecar": material_dir / "sidecar.json",
        "receipt": material_dir / "fetch_receipt.json",
    }


def _preflight(
    *,
    episode_id: str,
    source_path: str | None,
    source_url: str | None,
    material_id: str,
    mode: str,
    paths: dict[str, Path | None],
    ffprobe_path: str | None,
    yt_dlp_path: str | None,
    format_selector: str,
    will_write: bool,
) -> dict[str, Any]:
    material_dir = paths["material_dir"]
    if mode == "local-media-video":
        command_plan = source_video.build_probe_plan(
            input_path=source_path or "",
            ffprobe_path=ffprobe_path,
        ).to_dict()
        output_path_display = _display_path(paths["video"], Path.cwd())
    else:
        command_plan = yt_dlp_video.build_plan(
            source_url=source_url or "",
            output_dir=material_dir,
            yt_dlp_path=yt_dlp_path,
            ffprobe_path=ffprobe_path,
            format_selector=format_selector,
        ).to_dict()
        output_path_display = (
            _display_path(material_dir, Path.cwd())
            + "/source_video.<ext-chosen-by-yt-dlp>"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": mode,
        "source_url": _source_url_readback(source_url),
        "source_path": source_path,
        "source_path_exists": Path(source_path).exists() if source_path else None,
        "format_selector": format_selector if mode == "yt-dlp-video" else None,
        "allowed_containers": (
            list(yt_dlp_video.ALLOWED_CONTAINERS) if mode == "yt-dlp-video" else None
        ),
        "output_path": output_path_display,
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


def _conflicts(
    *,
    paths: dict[str, Path | None],
    material_id: str,
    mode: str,
) -> list[str]:
    conflicts: list[str] = []
    material_dir = paths["material_dir"]
    if mode == "local-media-video":
        if paths["video"] is not None and paths["video"].exists():
            conflicts.append(str(paths["video"]))
    else:
        if material_dir.exists():
            for path in sorted(material_dir.iterdir()):
                if (
                    path.is_file()
                    and path.stem == yt_dlp_video.OUTPUT_BASENAME
                    and not path.name.endswith((".part", ".ytdl"))
                ):
                    conflicts.append(str(path))
    for key in ("sidecar", "receipt"):
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
    paths: dict[str, Path | None],
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


def _execute_yt_dlp_video(
    *,
    episode_id: str,
    source_url: str,
    material_id: str,
    registered_by: str,
    paths: dict[str, Path | None],
    preflight: dict[str, Any],
    force: bool,
    yt_dlp_path: str | None,
    ffprobe_path: str | None,
    format_selector: str,
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

    material_dir = paths["material_dir"]
    if force:
        _cleanup_existing_source_video(material_dir)

    result = yt_dlp_video.fetch_url_video(
        source_url=source_url,
        output_dir=material_dir,
        yt_dlp_path=yt_dlp_path,
        ffprobe_path=ffprobe_path,
        format_selector=format_selector,
    )
    video_path = result.output_path
    asset_hash = compute_sha256(video_path)
    now = datetime.now(timezone.utc).isoformat()
    sidecar = _build_yt_dlp_video_sidecar(
        material_id=material_id,
        video_path=video_path,
        asset_hash=asset_hash,
        source_url=source_url,
        retrieved_at=now,
        retrieved_by=registered_by,
        media_metadata=result.metadata,
        chosen_format=result.chosen_format,
        warnings=_warnings_for_rights(rights_status, result.warnings),
    )
    save_sidecar(sidecar, paths["sidecar"])

    ledger = register_material(
        ledger,
        kind="source_video",
        subkind=source_video.SUBKIND,
        file_path=_display_path(video_path, Path.cwd()),
        sidecar_path=_display_path(paths["sidecar"], Path.cwd()),
        intended_uses=["editing_video"],
        registered_by=registered_by,
        rights_manifest_id=rights.get("episode_id", episode_id),
        rights_status_at_registration=rights_status,
        material_id=material_id,
    )
    save_ledger(ledger, paths["ledger"])

    receipt = _build_yt_dlp_video_receipt(
        episode_id=episode_id,
        material_id=material_id,
        source_url=source_url,
        output_path=video_path,
        sha256=asset_hash,
        byte_size=video_path.stat().st_size,
        created_at=now,
        preflight=preflight,
        fetch_result=result,
        rights_status=rights_status,
    )
    _save_json(receipt, paths["receipt"])
    return receipt


def _cleanup_existing_source_video(material_dir: Path) -> None:
    if not material_dir.exists():
        return
    for path in list(material_dir.iterdir()):
        if not path.is_file():
            continue
        if path.stem == yt_dlp_video.OUTPUT_BASENAME and not path.name.endswith(
            (".part", ".ytdl")
        ):
            try:
                path.unlink()
            except OSError:
                pass


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


def _build_yt_dlp_video_sidecar(
    *,
    material_id: str,
    video_path: Path,
    asset_hash: str,
    source_url: str,
    retrieved_at: str,
    retrieved_by: str,
    media_metadata: dict[str, Any],
    chosen_format: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "asset_id": material_id,
        "asset_path": _display_path(video_path, Path.cwd()),
        "asset_hash_sha256": asset_hash,
        "source": {
            "kind": "unverified",
            "url": _source_url_readback(source_url),
            "local_path": None,
            "retrieved_at": retrieved_at,
            "retrieved_by": retrieved_by,
            "retrieval_method": yt_dlp_video.RETRIEVAL_METHOD,
            "notes": (
                "Source video fetched from URL by yt-dlp inside asset_fetch; "
                "the downloaded file is the source_video itself with no "
                "render/encode. Rights and creative acceptance remain user-owned."
            ),
        },
        "license": {
            "kind": "unknown",
            "guideline_url": None,
            "guideline_version_checked_at": None,
            "url": None,
            "spdx_id": None,
            "notes": (
                "License metadata is captured as readback and must be reviewed "
                "before publishing."
            ),
        },
        "usage_conditions": ["source_link_required"],
        "restrictions": {
            "thumbnail_use": "guideline_dependent",
            "commercial_use": "guideline_dependent",
            "modification": "guideline_dependent",
            "redistribution": "guideline_dependent",
        },
        "attribution_text": f"Source: {_source_url_readback(source_url)}",
        "derived_from": None,
        "media_metadata": media_metadata,
        "chosen_format": chosen_format,
        "warnings": warnings,
    }


def _build_yt_dlp_video_receipt(
    *,
    episode_id: str,
    material_id: str,
    source_url: str,
    output_path: Path,
    sha256: str,
    byte_size: int,
    created_at: str,
    preflight: dict[str, Any],
    fetch_result: yt_dlp_video.YtDlpVideoResult,
    rights_status: str,
) -> dict[str, Any]:
    output_display = _display_path(output_path, Path.cwd())
    probe = fetch_result.probe_result
    warnings = _warnings_for_rights(rights_status, fetch_result.warnings)
    source_url_readback = _source_url_readback(source_url)
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "material_id": material_id,
        "mode": "yt-dlp-video",
        "source_url": source_url_readback,
        "output_path": output_display,
        "sha256": sha256,
        "byte_size": byte_size,
        "created_at": created_at,
        "rollback": {
            "files": [
                output_display,
                preflight["sidecar_path"],
                preflight["receipt_path"],
            ],
            "ledger_material_id": material_id,
        },
        "command_summary": "fetch-source-video --mode yt-dlp-video",
        "provider": yt_dlp_video.PROVIDER,
        "tools": [
            {
                "name": "yt-dlp",
                "path": fetch_result.yt_dlp_path,
                "path_source": fetch_result.yt_dlp_path_source,
                "version": fetch_result.yt_dlp_version,
            },
            {
                "name": "ffprobe",
                "path": probe.ffprobe_path,
                "path_source": probe.ffprobe_path_source,
                "version": probe.ffprobe_version,
            },
        ],
        "commands": [
            {
                "summary": fetch_result.yt_dlp_command_summary,
                "exit_code": fetch_result.yt_dlp_exit_code,
            },
            {
                "summary": probe.command_summary,
                "exit_code": probe.exit_code,
            },
        ],
        "input": {
            "source_url": source_url_readback,
            "local_path": None,
            "format_selector": fetch_result.format_selector,
            "allowed_containers": list(yt_dlp_video.ALLOWED_CONTAINERS),
        },
        "chosen_format": fetch_result.chosen_format,
        "container": fetch_result.container,
        "intermediate": {
            "retained": fetch_result.intermediate_retained,
            "strategy": (
                "yt-dlp output is the source_video file itself; no separate "
                "intermediate is retained"
            ),
        },
        "source_pipeline": {
            "intermediate_retained": fetch_result.intermediate_retained,
        },
        "outputs": [
            {
                "path": output_display,
                "sha256": sha256,
                "byte_size": byte_size,
                "duration_seconds": fetch_result.metadata.get("duration_seconds"),
                "metadata": fetch_result.metadata,
            }
        ],
        "video_metadata": fetch_result.metadata,
        "warnings": warnings,
        "stderr_digest": fetch_result.stderr_digest,
        "tool_stderr_digests": {
            "yt_dlp": fetch_result.yt_dlp_stderr_digest,
            "ffprobe": probe.stderr_digest,
        },
        "rights_snapshot": {
            "compliance_status_at_fetch": rights_status,
            "hard_gate": False,
            "production_acceptance": False,
        },
        "preflight": preflight,
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
