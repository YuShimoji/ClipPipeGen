"""render-tiny-proof subcommand: OUT-01 diagnostic rendered artifact."""

from __future__ import annotations

import argparse
import json
import sys
import wave
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny
from src.pipeline.edit_pack import load_edit_pack, validate_edit_pack
from src.pipeline.material_ledger import load_ledger

SCHEMA_VERSION = "v1"
ARTIFACT_KIND = "tiny_render_proof"
FORMAT = "tiny_render_proof_v1"


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="render-tiny-proof",
        description="Render a tiny diagnostic video from source video, source audio, and edit_pack.",
    )
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--source-video-material-id", required=True)
    parser.add_argument("--source-audio-material-id", required=True)
    parser.add_argument("--edit-pack-path", required=True)
    parser.add_argument("--output-id", required=True)
    parser.add_argument("--duration-sec", type=float, default=10.0)
    parser.add_argument("--container", choices=("mp4", "mkv"), default="mp4")
    parser.add_argument("--video-codec", default="auto")
    parser.add_argument("--audio-codec", default="auto")
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--ffprobe-path")
    parser.add_argument(
        "--burn-in-subtitles",
        choices=("off", "diagnostic"),
        default="off",
        help="Optionally burn edit_pack/transcript subtitles as a diagnostic overlay.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    context: dict[str, Any] | None = None
    mapping: dict[str, Any] | None = None
    preflight: dict[str, Any] | None = None
    try:
        context = _resolve_context(
            root=Path(args.root),
            episode_id=args.episode_id,
            source_video_material_id=args.source_video_material_id,
            source_audio_material_id=args.source_audio_material_id,
            edit_pack_path=Path(args.edit_pack_path),
            output_id=args.output_id,
            container=args.container,
        )
        mapping = _timeline_mapping(
            edit_pack=context["edit_pack"],
            source_video_duration=context["source_video"]["metadata"].get("duration_seconds"),
            source_audio_duration=context["source_audio"]["metadata"].get("duration_seconds"),
            duration_target_seconds=args.duration_sec,
        )
        subtitle_burn_in = _subtitle_burn_in_plan(
            context=context,
            mapping=mapping,
            mode=args.burn_in_subtitles,
        )
        context["subtitle_burn_in"] = subtitle_burn_in
        if subtitle_burn_in["enabled"]:
            mapping = dict(mapping)
            mapping["policy"] = mapping["policy"].replace(
                "no_subtitle_burn_in",
                "diagnostic_subtitle_burn_in",
            )
        preflight = _preflight(
            context=context,
            mapping=mapping,
            ffmpeg_path=args.ffmpeg_path,
            ffprobe_path=args.ffprobe_path,
            container=args.container,
            video_codec=args.video_codec,
            audio_codec=args.audio_codec,
            will_write=not args.dry_run,
        )
    except (OSError, json.JSONDecodeError, RenderCliError) as exc:
        print(f"render-tiny-proof failed: {exc}", file=sys.stderr)
        return 1

    conflicts = _conflicts(context["paths"], preflight=preflight)
    preflight["conflicts"] = conflicts
    preflight["would_fail_without_force"] = bool(conflicts and not args.force)

    if args.dry_run:
        _print_payload(preflight, fmt=args.format)
        return 0

    if conflicts and not args.force:
        print(
            "render-tiny-proof refused to overwrite existing artifact(s): "
            + ", ".join(conflicts)
            + " (use --force to overwrite)",
            file=sys.stderr,
        )
        return 1

    try:
        subtitle_file_path = None
        if context["subtitle_burn_in"]["enabled"]:
            subtitle_file_path = context["paths"]["subtitle_file"]
            _write_diagnostic_subtitle_file(
                subtitle_file_path,
                context["subtitle_burn_in"]["items"],
            )
        result = ffmpeg_tiny.render_tiny_proof(
            source_video_path=context["source_video"]["path"],
            source_audio_path=context["source_audio"]["path"],
            output_path=context["paths"]["video"],
            start_seconds=mapping["render_start_seconds"],
            duration_seconds=mapping["render_duration_seconds"],
            ffmpeg_path=args.ffmpeg_path,
            ffprobe_path=args.ffprobe_path,
            container=args.container,
            video_codec=args.video_codec,
            audio_codec=args.audio_codec,
            subtitle_file_path=subtitle_file_path,
        )
        receipt, manifest = _write_outputs(
            context=context,
            mapping=mapping,
            preflight=preflight,
            render_result=result,
        )
    except (OSError, ffmpeg_tiny.TinyRenderError) as exc:
        if context is not None and mapping is not None and preflight is not None:
            _write_failure_outputs(
                context=context,
                mapping=mapping,
                preflight=preflight,
                error=exc,
            )
        reason = getattr(exc, "failure_reason", "code_bug_or_unexpected_exception")
        print(f"render-tiny-proof failed: {reason}: {exc}", file=sys.stderr)
        return 1

    payload = {
        "rendered_video": _display_path(context["paths"]["video"], Path.cwd()),
        "render_receipt": _display_path(context["paths"]["receipt"], Path.cwd()),
        "render_manifest": _display_path(context["paths"]["manifest"], Path.cwd()),
        "render_report": _display_path(context["paths"]["report"], Path.cwd()),
        "output_metadata": manifest["output_metadata"],
        "timeline_mapping": mapping,
        "selected_render_profile": manifest["selected_render_profile"],
        "attempted_render_profiles": manifest["attempted_render_profiles"],
        "fallback_used": manifest["fallback_used"],
        "subtitle_burn_in": manifest["subtitle_burn_in"],
        "production_candidate": manifest["production_candidate"],
        "warnings": manifest["warnings"],
        "receipt": receipt["schema_version"],
    }
    _print_payload(payload, fmt=args.format)
    return 0


class RenderCliError(Exception):
    """Raised when CLI input resolution fails."""


def _resolve_context(
    *,
    root: Path,
    episode_id: str,
    source_video_material_id: str,
    source_audio_material_id: str,
    edit_pack_path: Path,
    output_id: str,
    container: str,
) -> dict[str, Any]:
    episode_dir = root / episode_id
    ledger_path = episode_dir / "material_ledger.json"
    if not ledger_path.exists():
        raise RenderCliError(f"material_ledger not found: {ledger_path}")
    if not edit_pack_path.exists():
        raise RenderCliError(f"edit_pack not found: {edit_pack_path}")

    ledger = load_ledger(ledger_path)
    edit_pack = load_edit_pack(edit_pack_path)
    edit_issues = validate_edit_pack(edit_pack)
    if edit_issues:
        raise RenderCliError(
            "edit_pack invalid: "
            + ", ".join(f"{issue.code}@{issue.field}" for issue in edit_issues)
        )

    source_video_entry = _find_material(
        ledger,
        material_id=source_video_material_id,
        kind="source_video",
    )
    source_audio_entry = _find_material(
        ledger,
        material_id=source_audio_material_id,
        kind="source_audio",
    )
    source_video = _source_ref(
        entry=source_video_entry,
        expected_kind="source_video",
        anchor=ledger_path.parent,
    )
    source_audio = _source_ref(
        entry=source_audio_entry,
        expected_kind="source_audio",
        anchor=ledger_path.parent,
    )
    if source_audio["metadata"].get("duration_seconds") is None:
        source_audio["metadata"]["duration_seconds"] = _wav_duration(source_audio["path"])

    transcript_path = edit_pack_path.parent / "transcript.json"
    transcript_payload = _load_json_optional(transcript_path) if transcript_path.exists() else {}
    output_dir = episode_dir / "renders" / output_id
    return {
        "episode_id": episode_id,
        "episode_dir": episode_dir,
        "output_id": output_id,
        "ledger": ledger,
        "ledger_path": ledger_path,
        "edit_pack": edit_pack,
        "edit_pack_path": edit_pack_path,
        "source_video": source_video,
        "source_audio": source_audio,
        "transcript": _transcript_ref(transcript_path, transcript_payload),
        "transcript_path": transcript_path,
        "transcript_payload": transcript_payload,
        "paths": {
            "output_dir": output_dir,
            "video": output_dir / f"rendered_video.{container}",
            "subtitle_file": output_dir / "diagnostic_subtitles.srt",
            "receipt": output_dir / "render_receipt.json",
            "manifest": output_dir / "render_manifest.json",
            "report": output_dir / "render_report.html",
        },
    }


def _find_material(ledger: dict[str, Any], *, material_id: str, kind: str) -> dict[str, Any]:
    for entry in ledger.get("materials") or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("id") == material_id:
            if entry.get("kind") != kind:
                raise RenderCliError(
                    f"material {material_id!r} has kind {entry.get('kind')!r}, expected {kind!r}"
                )
            return entry
    raise RenderCliError(f"{kind} material id not found: {material_id}")


def _source_ref(*, entry: dict[str, Any], expected_kind: str, anchor: Path) -> dict[str, Any]:
    media_path = _resolve_existing_path(entry.get("file_path"), anchor=anchor)
    sidecar_path = _resolve_existing_path(entry.get("sidecar_path"), anchor=anchor)
    receipt_path = sidecar_path.parent / "fetch_receipt.json" if sidecar_path else None
    sidecar = _load_json_optional(sidecar_path)
    receipt = _load_json_optional(receipt_path) if receipt_path and receipt_path.exists() else {}
    source = sidecar.get("source") if isinstance(sidecar.get("source"), dict) else {}
    receipt_input = receipt.get("input") if isinstance(receipt.get("input"), dict) else {}
    metadata = _metadata_for_source(expected_kind, sidecar=sidecar, receipt=receipt)
    compliance = entry.get("compliance_link") if isinstance(entry.get("compliance_link"), dict) else {}
    rights_status = (
        compliance.get("compliance_status_at_registration")
        or (receipt.get("rights_snapshot") or {}).get("compliance_status_at_fetch")
        or entry.get("rights_status_at_registration")
        or "unknown"
    )
    return {
        "material_id": entry.get("id"),
        "kind": entry.get("kind"),
        "subkind": entry.get("subkind"),
        "path": media_path,
        "path_readback": _display_path(media_path, Path.cwd()) if media_path else entry.get("file_path"),
        "sidecar_path": sidecar_path,
        "sidecar_readback": _display_path(sidecar_path, Path.cwd()) if sidecar_path else entry.get("sidecar_path"),
        "receipt_path": receipt_path if receipt_path and receipt_path.exists() else None,
        "receipt_readback": _display_path(receipt_path, Path.cwd()) if receipt_path and receipt_path.exists() else "",
        "ledger_entry": entry,
        "sha256": entry.get("hash_sha256") or receipt.get("sha256"),
        "byte_size": entry.get("byte_size") or receipt.get("byte_size"),
        "provider": receipt.get("provider") or source.get("retrieval_method") or "",
        "mode": receipt.get("mode") or "",
        "source_url": receipt.get("source_url") or receipt_input.get("source_url") or source.get("url"),
        "local_path": receipt_input.get("local_path") or source.get("local_path"),
        "rights_status": rights_status,
        "metadata": metadata,
        "warnings": _list_of_strings(receipt.get("warnings")) + _list_of_strings(sidecar.get("warnings")),
    }


def _metadata_for_source(kind: str, *, sidecar: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    if kind == "source_video":
        for value in (
            sidecar.get("media_metadata"),
            receipt.get("video_metadata"),
            (receipt.get("outputs") or [{}])[0].get("metadata") if isinstance(receipt.get("outputs"), list) else None,
        ):
            if isinstance(value, dict):
                return dict(value)
        return {}

    outputs = receipt.get("outputs") if isinstance(receipt.get("outputs"), list) else []
    output = outputs[0] if outputs and isinstance(outputs[0], dict) else {}
    metadata: dict[str, Any] = {}
    if output.get("duration_seconds") is not None:
        metadata["duration_seconds"] = output.get("duration_seconds")
    audio_format = receipt.get("audio_format") if isinstance(receipt.get("audio_format"), dict) else {}
    if not audio_format:
        preflight = receipt.get("preflight") if isinstance(receipt.get("preflight"), dict) else {}
        audio_format = preflight.get("audio_format") if isinstance(preflight.get("audio_format"), dict) else {}
    metadata.update({k: v for k, v in audio_format.items() if v is not None})
    return metadata


def _timeline_mapping(
    *,
    edit_pack: dict[str, Any],
    source_video_duration: Any,
    source_audio_duration: Any,
    duration_target_seconds: float,
) -> dict[str, Any]:
    cut = _select_cut(edit_pack)
    cut_start = _as_float(cut.get("start_seconds"), field="cut.start_seconds")
    cut_end = _as_float(cut.get("end_seconds"), field="cut.end_seconds")
    cut_duration = cut_end - cut_start
    if cut_duration <= 0:
        raise RenderCliError("selected cut duration must be positive")
    if duration_target_seconds <= 0:
        raise RenderCliError("--duration-sec must be positive")

    warnings: list[str] = []
    render_start = cut_start
    video_duration = _optional_float(source_video_duration)
    audio_duration = _optional_float(source_audio_duration)
    if video_duration is not None and render_start >= video_duration:
        warnings.append("cut start exceeds source video duration; render start reset to 0")
        render_start = 0.0
    if audio_duration is not None and render_start >= audio_duration:
        warnings.append("cut start exceeds source audio duration; render start reset to 0")
        render_start = 0.0

    limits = [cut_duration, float(duration_target_seconds)]
    if video_duration is not None:
        limits.append(max(0.0, video_duration - render_start))
    if audio_duration is not None:
        limits.append(max(0.0, audio_duration - render_start))
    render_duration = min(limits)
    if render_duration <= 0:
        raise RenderCliError("timeline mapping produced non-positive render duration")

    if render_duration < cut_duration - 0.001:
        warnings.append("cut range clamped to available diagnostic render duration")
    if render_duration < duration_target_seconds - 0.001:
        warnings.append("duration target unmet; diagnostic proof keeps the shorter available range")
    if video_duration is not None and audio_duration is not None and abs(video_duration - audio_duration) > 0.25:
        warnings.append("source video/audio duration mismatch; render clamps to the shortest available input")

    return {
        "policy": "single_selected_cut_clamped_to_shortest_input_no_loop_no_speed_change_no_subtitle_burn_in",
        "cut_id": cut.get("id"),
        "cut_source": cut.get("source"),
        "requested_start_seconds": cut_start,
        "requested_end_seconds": cut_end,
        "requested_cut_duration_seconds": cut_duration,
        "duration_target_seconds": float(duration_target_seconds),
        "render_start_seconds": render_start,
        "render_duration_seconds": render_duration,
        "source_video_duration_seconds": video_duration,
        "source_audio_duration_seconds": audio_duration,
        "clamped": bool(warnings),
        "warnings": warnings,
    }


def _select_cut(edit_pack: dict[str, Any]) -> dict[str, Any]:
    cuts = [c for c in edit_pack.get("cut_candidates") or [] if isinstance(c, dict)]
    if not cuts:
        raise RenderCliError("edit_pack has no cut_candidates")
    selected_ids = [c for c in edit_pack.get("selected_cut_ids") or [] if isinstance(c, str)]
    if selected_ids:
        for cut_id in selected_ids:
            for cut in cuts:
                if cut.get("id") == cut_id:
                    return cut
        raise RenderCliError("selected_cut_ids do not match cut_candidates")
    return cuts[0]


def _subtitle_burn_in_plan(
    *,
    context: dict[str, Any],
    mapping: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    overlay_policy = {
        "overlay_mode": mode,
        "position": "bottom_center_fixed",
        "font_strategy": "ffmpeg subtitles filter default font provider; no project fontfile or typography polish",
        "timing_policy": "map source timeline seconds to rendered timeline seconds and clamp each subtitle to the rendered range",
        "text_source": "prefer edit_pack.subtitles[]; fall back to sibling transcript.json segments only for diagnostic linkage",
        "line_handling": "preserve existing newlines; no line-wrap, kinsoku, safe-area, outline, or background polish",
        "escaping": "write UTF-8 SRT and escape the subtitle file path for FFmpeg filtergraph use",
    }
    if mode == "off":
        return {
            "enabled": False,
            "requested_mode": mode,
            "status": "disabled",
            "source_ref": {
                "source_type": "none",
                "path": None,
                "subtitle_ids": [],
                "source_segment_ids": [],
                "item_count": 0,
            },
            "overlay_policy": overlay_policy,
            "items": [],
            "text_preview": [],
            "warnings": [],
        }
    if mode != "diagnostic":
        raise RenderCliError(f"unsupported subtitle burn-in mode: {mode}")

    items, source_ref, warnings = _subtitle_items_from_edit_pack(context=context, mapping=mapping)
    if not items:
        items, source_ref, transcript_warnings = _subtitle_items_from_transcript(context=context, mapping=mapping)
        warnings.extend(transcript_warnings)
    if not items:
        raise RenderCliError(
            "diagnostic subtitle burn-in requested but no edit_pack subtitles or transcript segments overlap the rendered range"
        )

    source_ref = dict(source_ref)
    source_ref["subtitle_file"] = _display_path(context["paths"]["subtitle_file"], Path.cwd())
    return {
        "enabled": True,
        "requested_mode": mode,
        "status": "enabled",
        "source_ref": source_ref,
        "overlay_policy": overlay_policy,
        "items": items,
        "text_preview": [item["text"] for item in items[:3]],
        "warnings": warnings,
    }


def _subtitle_items_from_edit_pack(
    *,
    context: dict[str, Any],
    mapping: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    subtitles = [s for s in context["edit_pack"].get("subtitles") or [] if isinstance(s, dict)]
    items = _subtitle_items_from_source(
        entries=subtitles,
        mapping=mapping,
        id_field="id",
        source_type="edit_pack_subtitles",
    )
    return (
        items,
        {
            "source_type": "edit_pack_subtitles",
            "path": _display_path(context["edit_pack_path"], Path.cwd()),
            "subtitle_ids": [item["source_id"] for item in items],
            "source_segment_ids": [
                item["source_segment_id"]
                for item in items
                if item.get("source_segment_id")
            ],
            "item_count": len(items),
        },
        [] if items else ["edit_pack has no subtitles overlapping the diagnostic render range"],
    )


def _subtitle_items_from_transcript(
    *,
    context: dict[str, Any],
    mapping: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    transcript = context.get("transcript_payload") or {}
    segments = [s for s in transcript.get("segments") or [] if isinstance(s, dict)]
    items = _subtitle_items_from_source(
        entries=segments,
        mapping=mapping,
        id_field="id",
        source_type="transcript_segments_diagnostic",
    )
    return (
        items,
        {
            "source_type": "transcript_segments_diagnostic",
            "path": _display_path(context["transcript_path"], Path.cwd()) if transcript else None,
            "subtitle_ids": [],
            "source_segment_ids": [item["source_id"] for item in items],
            "item_count": len(items),
        },
        [
            "no edit_pack subtitle draft overlapped the render range; diagnostic overlay uses transcript segments directly"
        ]
        if items
        else ["transcript has no segments overlapping the diagnostic render range"],
    )


def _subtitle_items_from_source(
    *,
    entries: list[dict[str, Any]],
    mapping: dict[str, Any],
    id_field: str,
    source_type: str,
) -> list[dict[str, Any]]:
    render_start = float(mapping["render_start_seconds"])
    render_end = render_start + float(mapping["render_duration_seconds"])
    cut_id = mapping.get("cut_id")
    items: list[dict[str, Any]] = []
    for entry in entries:
        text = str(entry.get("text") or "").strip()
        if not text:
            continue
        if source_type == "edit_pack_subtitles" and entry.get("cut_id") and entry.get("cut_id") != cut_id:
            continue
        source_start = _optional_float(entry.get("start_seconds"))
        source_end = _optional_float(entry.get("end_seconds"))
        if source_start is None or source_end is None or source_end <= source_start:
            continue
        overlap_start = max(source_start, render_start)
        overlap_end = min(source_end, render_end)
        if overlap_end <= overlap_start:
            continue
        items.append(
            {
                "source_type": source_type,
                "source_id": entry.get(id_field),
                "subtitle_id": entry.get("id") if source_type == "edit_pack_subtitles" else None,
                "cut_id": entry.get("cut_id") or cut_id,
                "source": entry.get("source") or source_type,
                "source_segment_id": entry.get("source_segment_id") or (
                    entry.get("id") if source_type == "transcript_segments_diagnostic" else None
                ),
                "source_start_seconds": source_start,
                "source_end_seconds": source_end,
                "start_seconds": round(overlap_start - render_start, 3),
                "end_seconds": round(overlap_end - render_start, 3),
                "text": text,
            }
        )
    return items


def _preflight(
    *,
    context: dict[str, Any],
    mapping: dict[str, Any],
    ffmpeg_path: str | None,
    ffprobe_path: str | None,
    container: str,
    video_codec: str,
    audio_codec: str,
    will_write: bool,
) -> dict[str, Any]:
    plan = ffmpeg_tiny.build_plan(
        source_video_path=context["source_video"]["path"],
        source_audio_path=context["source_audio"]["path"],
        output_path=context["paths"]["video"],
        start_seconds=mapping["render_start_seconds"],
        duration_seconds=mapping["render_duration_seconds"],
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        container=container,
        video_codec=video_codec,
        audio_codec=audio_codec,
        subtitle_file_path=(
            context["paths"]["subtitle_file"]
            if (context.get("subtitle_burn_in") or {}).get("enabled")
            else None
        ),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "format": FORMAT,
        "episode_id": context["episode_id"],
        "output_id": context["output_id"],
        "will_write": will_write,
        "will_call_subprocess": will_write,
        "input": _input_readback(context),
        "timeline_mapping": mapping,
        "subtitle_burn_in": _subtitle_burn_in_readback(context),
        "subtitle_source_ref": _subtitle_burn_in_readback(context)["source_ref"],
        "subtitle_overlay_policy": _subtitle_burn_in_readback(context)["overlay_policy"],
        "outputs": _output_readback(context),
        "command_plan": plan.to_dict(),
        "tool_preflight": {
            "status": "not_checked",
            "reason": "dry-run command planning does not execute ffmpeg/ffprobe version checks",
            "ffmpeg": {
                "path": plan.ffmpeg_path,
                "path_source": plan.ffmpeg_path_source,
                "available": plan.ffmpeg_path is not None,
                "version": None,
            },
            "ffprobe": {
                "path": plan.ffprobe_path,
                "path_source": plan.ffprobe_path_source,
                "available": plan.ffprobe_path is not None,
                "version": None,
            },
        },
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "warnings": _warnings(context=context, mapping=mapping, render_warnings=plan.warnings),
    }


def _write_outputs(
    *,
    context: dict[str, Any],
    mapping: dict[str, Any],
    preflight: dict[str, Any],
    render_result: ffmpeg_tiny.RenderResult,
) -> tuple[dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    paths = context["paths"]
    warnings = _warnings(
        context=context,
        mapping=mapping,
        render_warnings=render_result.warnings,
    )
    output_metadata = render_result.metadata
    outputs = {
        "rendered_video": render_result.output_path,
        "render_receipt": _display_path(paths["receipt"], Path.cwd()),
        "render_manifest": _display_path(paths["manifest"], Path.cwd()),
        "render_report": _display_path(paths["report"], Path.cwd()),
    }
    if (context.get("subtitle_burn_in") or {}).get("enabled"):
        outputs["diagnostic_subtitle_file"] = _display_path(paths["subtitle_file"], Path.cwd())
    execution_preflight = dict(preflight)
    execution_preflight["tool_preflight"] = render_result.preflight
    subtitle_burn_in = _subtitle_burn_in_readback(
        context,
        status="enabled" if (context.get("subtitle_burn_in") or {}).get("enabled") else "disabled",
    )
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "format": FORMAT,
        "episode_id": context["episode_id"],
        "output_id": context["output_id"],
        "created_at": now,
        "provider": "ffmpeg",
        "mode": "tiny-render-proof",
        "status": "succeeded",
        "failure_classification": {
            "status": "succeeded",
            "failure_reason": None,
            "message": None,
        },
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "input": _input_readback(context),
        "timeline_mapping": mapping,
        "subtitle_burn_in": subtitle_burn_in,
        "subtitle_source_ref": subtitle_burn_in["source_ref"],
        "subtitle_overlay_policy": subtitle_burn_in["overlay_policy"],
        "outputs": outputs,
        "output_metadata": output_metadata,
        "selected_render_profile": render_result.selected_profile.to_dict(),
        "attempted_render_profiles": [attempt.to_dict() for attempt in render_result.attempts],
        "fallback_used": render_result.fallback_used,
        "selected_container": render_result.selected_profile.container,
        "selected_video_codec": render_result.selected_profile.video_codec,
        "selected_audio_codec": render_result.selected_profile.audio_codec,
        "tools": [
            {
                "name": "ffmpeg",
                "path": render_result.ffmpeg_path,
                "path_source": render_result.ffmpeg_path_source,
                "version": render_result.ffmpeg_version,
            },
            {
                "name": "ffprobe",
                "path": render_result.ffprobe_path,
                "path_source": render_result.ffprobe_path_source,
                "version": render_result.ffprobe_version,
            },
        ],
        "commands": [attempt.to_dict() for attempt in render_result.attempts],
        "selected_command_summary": render_result.command_summary,
        "probe": render_result.probe_result.to_dict(),
        "warnings": warnings,
        "preflight": execution_preflight,
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "format": FORMAT,
        "episode_id": context["episode_id"],
        "output_id": context["output_id"],
        "created_at": now,
        "status": "succeeded",
        "failure_classification": receipt["failure_classification"],
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "source_refs": _input_readback(context),
        "timeline_mapping": mapping,
        "subtitle_burn_in": subtitle_burn_in,
        "subtitle_source_ref": subtitle_burn_in["source_ref"],
        "subtitle_overlay_policy": subtitle_burn_in["overlay_policy"],
        "outputs": outputs,
        "output_metadata": output_metadata,
        "selected_render_profile": receipt["selected_render_profile"],
        "attempted_render_profiles": receipt["attempted_render_profiles"],
        "fallback_used": receipt["fallback_used"],
        "selected_container": receipt["selected_container"],
        "selected_video_codec": receipt["selected_video_codec"],
        "selected_audio_codec": receipt["selected_audio_codec"],
        "preflight": execution_preflight,
        "warnings": warnings,
    }
    _write_json(receipt, paths["receipt"])
    _write_json(manifest, paths["manifest"])
    paths["report"].parent.mkdir(parents=True, exist_ok=True)
    paths["report"].write_text(_make_report_html(manifest), encoding="utf-8")
    return receipt, manifest


def _write_failure_outputs(
    *,
    context: dict[str, Any],
    mapping: dict[str, Any],
    preflight: dict[str, Any],
    error: BaseException,
) -> tuple[dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    paths = context["paths"]
    failure_reason = getattr(error, "failure_reason", "code_bug_or_unexpected_exception")
    attempts = getattr(error, "attempts", []) or []
    selected_profile = getattr(error, "selected_profile", None)
    selected_profile_dict = selected_profile.to_dict() if selected_profile else None
    output_path = (
        selected_profile.output_path
        if selected_profile
        else _first_planned_output(preflight) or _display_path(paths["video"], Path.cwd())
    )
    execution_preflight = dict(preflight)
    error_preflight = getattr(error, "preflight", None)
    if error_preflight:
        execution_preflight["tool_preflight"] = error_preflight
    warnings = _warnings(
        context=context,
        mapping=mapping,
        render_warnings=[
            f"render failed before diagnostic artifact acceptance: {failure_reason}",
            str(error),
        ],
    )
    subtitle_status = "failed" if (context.get("subtitle_burn_in") or {}).get("enabled") else "disabled"
    subtitle_burn_in = _subtitle_burn_in_readback(
        context,
        status=subtitle_status,
        failure_reason=failure_reason if subtitle_status == "failed" else None,
    )
    outputs = {
        "rendered_video": output_path,
        "render_receipt": _display_path(paths["receipt"], Path.cwd()),
        "render_manifest": _display_path(paths["manifest"], Path.cwd()),
        "render_report": _display_path(paths["report"], Path.cwd()),
    }
    if (context.get("subtitle_burn_in") or {}).get("enabled"):
        outputs["diagnostic_subtitle_file"] = _display_path(paths["subtitle_file"], Path.cwd())
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "format": FORMAT,
        "episode_id": context["episode_id"],
        "output_id": context["output_id"],
        "created_at": now,
        "provider": "ffmpeg",
        "mode": "tiny-render-proof",
        "status": "failed",
        "failure_classification": {
            "status": "failed",
            "failure_reason": failure_reason,
            "message": str(error),
        },
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "input": _input_readback(context),
        "timeline_mapping": mapping,
        "subtitle_burn_in": subtitle_burn_in,
        "subtitle_source_ref": subtitle_burn_in["source_ref"],
        "subtitle_overlay_policy": subtitle_burn_in["overlay_policy"],
        "outputs": outputs,
        "output_metadata": {},
        "selected_render_profile": selected_profile_dict,
        "attempted_render_profiles": [attempt.to_dict() for attempt in attempts],
        "fallback_used": any(not attempt.selected for attempt in attempts),
        "selected_container": selected_profile.container if selected_profile else None,
        "selected_video_codec": selected_profile.video_codec if selected_profile else None,
        "selected_audio_codec": selected_profile.audio_codec if selected_profile else None,
        "commands": [attempt.to_dict() for attempt in attempts],
        "selected_command_summary": None,
        "probe": None,
        "warnings": warnings,
        "preflight": execution_preflight,
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "format": FORMAT,
        "episode_id": context["episode_id"],
        "output_id": context["output_id"],
        "created_at": now,
        "status": "failed",
        "failure_classification": receipt["failure_classification"],
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "source_refs": _input_readback(context),
        "timeline_mapping": mapping,
        "subtitle_burn_in": subtitle_burn_in,
        "subtitle_source_ref": subtitle_burn_in["source_ref"],
        "subtitle_overlay_policy": subtitle_burn_in["overlay_policy"],
        "outputs": receipt["outputs"],
        "output_metadata": {},
        "selected_render_profile": selected_profile_dict,
        "attempted_render_profiles": receipt["attempted_render_profiles"],
        "fallback_used": receipt["fallback_used"],
        "selected_container": receipt["selected_container"],
        "selected_video_codec": receipt["selected_video_codec"],
        "selected_audio_codec": receipt["selected_audio_codec"],
        "preflight": execution_preflight,
        "warnings": warnings,
    }
    _write_json(receipt, paths["receipt"])
    _write_json(manifest, paths["manifest"])
    paths["report"].parent.mkdir(parents=True, exist_ok=True)
    paths["report"].write_text(_make_report_html(manifest), encoding="utf-8")
    return receipt, manifest


def _warnings(
    *,
    context: dict[str, Any],
    mapping: dict[str, Any],
    render_warnings: list[str],
) -> list[str]:
    warnings = list(dict.fromkeys(render_warnings + mapping["warnings"]))
    warnings.append("OUT-01 tiny render proof is diagnostic; production render acceptance is not claimed.")
    subtitle_burn_in = context.get("subtitle_burn_in") or {}
    if subtitle_burn_in.get("enabled"):
        warnings.append(
            "subtitle burn-in is diagnostic overlay only; typography, safe-area, creative acceptance, publishing, and production subtitle design are out of scope."
        )
    else:
        warnings.append("subtitle burn-in is disabled; visual polish, publishing, and creative acceptance are out of scope.")
    for warning in subtitle_burn_in.get("warnings") or []:
        warnings.append(str(warning))
    review_status = (context["edit_pack"].get("review") or {}).get("status", "unknown")
    if review_status != "approved":
        warnings.append(f"edit_pack review.status is {review_status}; render is not approved.")
    transcript = context.get("transcript") or {}
    if transcript.get("available") and transcript.get("real_transcript") is not True:
        warnings.append("transcript is not real STT; rendered proof remains fixture/preview-derived.")
    if not transcript.get("available"):
        warnings.append("transcript readback is unavailable; render proof relies on edit_pack timing only.")
    for label in ("source_video", "source_audio"):
        rights_status = context[label].get("rights_status") or "unknown"
        if rights_status != "passed":
            warnings.append(
                f"{label} rights status is {rights_status}; user review required before production/publishing."
            )
    return list(dict.fromkeys(warnings))


def _input_readback(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "material_ledger": _display_path(context["ledger_path"], Path.cwd()),
        "edit_pack": {
            "path": _display_path(context["edit_pack_path"], Path.cwd()),
            "episode_id": context["edit_pack"].get("episode_id"),
            "review_status": (context["edit_pack"].get("review") or {}).get("status"),
            "cut_candidates_count": len(context["edit_pack"].get("cut_candidates") or []),
            "selected_cut_ids": context["edit_pack"].get("selected_cut_ids") or [],
            "subtitle_count": len(context["edit_pack"].get("subtitles") or []),
        },
        "transcript": context["transcript"],
        "source_video": _source_readback(context["source_video"]),
        "source_audio": _source_readback(context["source_audio"]),
    }


def _source_readback(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "material_id": source.get("material_id"),
        "kind": source.get("kind"),
        "subkind": source.get("subkind"),
        "path": source.get("path_readback"),
        "sidecar": source.get("sidecar_readback"),
        "fetch_receipt": source.get("receipt_readback"),
        "sha256": source.get("sha256"),
        "byte_size": source.get("byte_size"),
        "provider": source.get("provider"),
        "mode": source.get("mode"),
        "source_url": source.get("source_url"),
        "local_path": source.get("local_path"),
        "rights_status": source.get("rights_status"),
        "metadata": source.get("metadata"),
        "ledger_entry": source.get("ledger_entry"),
    }


def _subtitle_burn_in_readback(
    context: dict[str, Any],
    *,
    status: str | None = None,
    failure_reason: str | None = None,
) -> dict[str, Any]:
    plan = context.get("subtitle_burn_in") or {}
    current_status = status or plan.get("status") or "disabled"
    return {
        "enabled": bool(plan.get("enabled")),
        "requested_mode": plan.get("requested_mode") or "off",
        "status": current_status,
        "failure_reason": failure_reason,
        "source_ref": plan.get("source_ref")
        or {
            "source_type": "none",
            "path": None,
            "subtitle_ids": [],
            "source_segment_ids": [],
            "item_count": 0,
        },
        "overlay_policy": plan.get("overlay_policy") or {},
        "items": plan.get("items") or [],
        "text_preview": plan.get("text_preview") or [],
    }


def _output_readback(context: dict[str, Any]) -> dict[str, str]:
    outputs = {
        "rendered_video": _display_path(context["paths"]["video"], Path.cwd()),
        "render_receipt": _display_path(context["paths"]["receipt"], Path.cwd()),
        "render_manifest": _display_path(context["paths"]["manifest"], Path.cwd()),
        "render_report": _display_path(context["paths"]["report"], Path.cwd()),
    }
    if (context.get("subtitle_burn_in") or {}).get("enabled"):
        outputs["diagnostic_subtitle_file"] = _display_path(context["paths"]["subtitle_file"], Path.cwd())
    return outputs


def _write_diagnostic_subtitle_file(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blocks: list[str] = []
    for index, item in enumerate(items, start=1):
        start = _format_srt_timestamp(float(item["start_seconds"]))
        end = _format_srt_timestamp(float(item["end_seconds"]))
        text = str(item["text"]).replace("\r\n", "\n").replace("\r", "\n")
        blocks.append(f"{index}\n{start} --> {end}\n{text}\n")
    path.write_text("\n".join(blocks), encoding="utf-8")


def _format_srt_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    milliseconds_total = int(round(seconds * 1000))
    milliseconds = milliseconds_total % 1000
    total_seconds = milliseconds_total // 1000
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def _transcript_ref(transcript_path: Path, transcript: dict[str, Any]) -> dict[str, Any]:
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    source_audio = transcript.get("source_audio") if isinstance(transcript.get("source_audio"), dict) else {}
    return {
        "available": bool(transcript),
        "path": _display_path(transcript_path, Path.cwd()) if transcript else None,
        "provider": stt.get("provider") or stt.get("engine") or "",
        "engine": stt.get("engine") or "",
        "model": stt.get("model") or (stt.get("params") or {}).get("model_path") or "",
        "real_transcript": stt.get("real_transcript") is True,
        "segment_count": stt.get("segment_count") or transcript.get("segment_count"),
        "duration_seconds": source_audio.get("duration_seconds"),
        "source_audio_material_id": source_audio.get("material_id"),
    }


def _conflicts(paths: dict[str, Path], *, preflight: dict[str, Any] | None = None) -> list[str]:
    out: list[str] = []
    for key in ("video", "subtitle_file", "receipt", "manifest", "report"):
        if paths[key].exists():
            out.append(str(paths[key]))
    planned_outputs = set()
    if preflight:
        plan = preflight.get("command_plan") if isinstance(preflight.get("command_plan"), dict) else {}
        for profile in plan.get("render_profiles") or []:
            if isinstance(profile, dict) and profile.get("output_path"):
                planned_outputs.add(str(profile["output_path"]))
    for planned in sorted(planned_outputs):
        path = Path(planned)
        if path.exists() and str(path) not in out:
            out.append(str(path))
    return out


def _resolve_existing_path(value: Any, *, anchor: Path) -> Path:
    if not isinstance(value, str) or not value:
        raise RenderCliError("material entry path is missing")
    raw = Path(value)
    candidates = [raw]
    if not raw.is_absolute():
        candidates.extend([Path.cwd() / raw, anchor / raw])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RenderCliError(f"material file not found: {value}")


def _load_json_optional(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _make_report_html(manifest: dict[str, Any]) -> str:
    source_video = manifest["source_refs"]["source_video"]
    source_audio = manifest["source_refs"]["source_audio"]
    edit_pack = manifest["source_refs"]["edit_pack"]
    transcript = manifest["source_refs"]["transcript"]
    mapping = manifest["timeline_mapping"]
    metadata = manifest["output_metadata"]
    outputs = manifest["outputs"]
    warnings = manifest["warnings"]
    selected_profile = manifest.get("selected_render_profile") or {}
    failure = manifest.get("failure_classification") or {}
    attempts = manifest.get("attempted_render_profiles") or []
    subtitle_burn_in = manifest.get("subtitle_burn_in") or {}
    subtitle_source_ref = subtitle_burn_in.get("source_ref") or manifest.get("subtitle_source_ref") or {}
    subtitle_policy = subtitle_burn_in.get("overlay_policy") or manifest.get("subtitle_overlay_policy") or {}
    tool_preflight = (manifest.get("preflight") or {}).get("tool_preflight") or {}
    ffmpeg = tool_preflight.get("ffmpeg") or {}
    ffprobe = tool_preflight.get("ffprobe") or {}
    warning_items = "\n".join(f"<li>{escape(str(warning))}</li>" for warning in warnings)
    attempt_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str((attempt.get('profile') or {}).get('profile_id', '')))}</td>"
        f"<td>{escape(str((attempt.get('profile') or {}).get('container', '')))}</td>"
        f"<td>{escape(str((attempt.get('profile') or {}).get('video_codec', '')))}</td>"
        f"<td>{escape(str((attempt.get('profile') or {}).get('audio_codec', '')))}</td>"
        f"<td>{escape(str(attempt.get('status', '')))}</td>"
        f"<td>{escape(str(attempt.get('failure_reason') or ''))}</td>"
        f"<td>{escape(str(attempt.get('selected', False)).lower())}</td>"
        "</tr>"
        for attempt in attempts
    )
    subtitle_items = subtitle_burn_in.get("items") or []
    subtitle_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('source_id') or item.get('subtitle_id') or ''))}</td>"
        f"<td>{escape(str(item.get('start_seconds')))}-{escape(str(item.get('end_seconds')))}</td>"
        f"<td>{escape(str(item.get('text') or ''))}</td>"
        "</tr>"
        for item in subtitle_items
    )
    subtitle_text_preview = " | ".join(str(text) for text in subtitle_burn_in.get("text_preview") or [])
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>OUT-01 Tiny Render Proof Readback</title>
</head>
<body>
  <h1>OUT-01 Tiny Render Proof Readback</h1>
  <p>This rendered artifact is diagnostic plumbing proof, not production / creative / publish acceptance.</p>
  <h2>Render Status</h2>
  <dl>
    <dt>status</dt><dd>{escape(str(manifest.get("status", "succeeded")))}</dd>
    <dt>failure_reason</dt><dd>{escape(str(failure.get("failure_reason") or ""))}</dd>
    <dt>selected_profile</dt><dd>{escape(str(selected_profile.get("profile_id") or ""))}</dd>
    <dt>selected_container</dt><dd>{escape(str(manifest.get("selected_container") or ""))}</dd>
    <dt>selected_video_codec</dt><dd>{escape(str(manifest.get("selected_video_codec") or ""))}</dd>
    <dt>selected_audio_codec</dt><dd>{escape(str(manifest.get("selected_audio_codec") or ""))}</dd>
    <dt>fallback_used</dt><dd>{escape(str(manifest.get("fallback_used", False)).lower())}</dd>
  </dl>
  <h2>Tool Preflight</h2>
  <dl>
    <dt>ffmpeg_available</dt><dd>{escape(str(ffmpeg.get("available", False)).lower())}</dd>
    <dt>ffmpeg_path</dt><dd>{escape(str(ffmpeg.get("path") or ""))}</dd>
    <dt>ffmpeg_version</dt><dd>{escape(str(ffmpeg.get("version") or ""))}</dd>
    <dt>ffprobe_available</dt><dd>{escape(str(ffprobe.get("available", False)).lower())}</dd>
    <dt>ffprobe_path</dt><dd>{escape(str(ffprobe.get("path") or ""))}</dd>
    <dt>ffprobe_version</dt><dd>{escape(str(ffprobe.get("version") or ""))}</dd>
  </dl>
  <h2>Artifact Paths</h2>
  <ul>
    <li>rendered_video: {escape(str(outputs.get("rendered_video", "")))}</li>
    <li>diagnostic_subtitle_file: {escape(str(outputs.get("diagnostic_subtitle_file", "")))}</li>
    <li>render_receipt: {escape(str(outputs.get("render_receipt", "")))}</li>
    <li>render_manifest: {escape(str(outputs.get("render_manifest", "")))}</li>
    <li>render_report: {escape(str(outputs.get("render_report", "")))}</li>
  </ul>
  <h2>Input Refs</h2>
  <dl>
    <dt>source_video</dt><dd>{escape(str(source_video.get("material_id")))} / {escape(str(source_video.get("path")))}</dd>
    <dt>source_audio</dt><dd>{escape(str(source_audio.get("material_id")))} / {escape(str(source_audio.get("path")))}</dd>
    <dt>edit_pack</dt><dd>{escape(str(edit_pack.get("path")))} / review={escape(str(edit_pack.get("review_status")))}</dd>
    <dt>transcript</dt><dd>{escape(str(transcript.get("path") or ""))} / real={escape(str(transcript.get("real_transcript", False)).lower())}</dd>
  </dl>
  <h2>Subtitle Burn-In Diagnostic</h2>
  <p>Diagnostic overlay only. This is not typography / safe-area / line-wrap / font polish / creative acceptance.</p>
  <dl>
    <dt>status</dt><dd>{escape(str(subtitle_burn_in.get("status", "disabled")))}</dd>
    <dt>requested_mode</dt><dd>{escape(str(subtitle_burn_in.get("requested_mode", "off")))}</dd>
    <dt>source_type</dt><dd>{escape(str(subtitle_source_ref.get("source_type", "none")))}</dd>
    <dt>source_path</dt><dd>{escape(str(subtitle_source_ref.get("path") or ""))}</dd>
    <dt>subtitle_file</dt><dd>{escape(str(subtitle_source_ref.get("subtitle_file") or ""))}</dd>
    <dt>text_preview</dt><dd>{escape(subtitle_text_preview)}</dd>
    <dt>position</dt><dd>{escape(str(subtitle_policy.get("position", "")))}</dd>
    <dt>font_strategy</dt><dd>{escape(str(subtitle_policy.get("font_strategy", "")))}</dd>
    <dt>timing_policy</dt><dd>{escape(str(subtitle_policy.get("timing_policy", "")))}</dd>
    <dt>line_handling</dt><dd>{escape(str(subtitle_policy.get("line_handling", "")))}</dd>
  </dl>
  <table>
    <thead><tr><th>source</th><th>render time</th><th>text</th></tr></thead>
    <tbody>
{subtitle_rows}
    </tbody>
  </table>
  <h2>Timeline Mapping</h2>
  <dl>
    <dt>policy</dt><dd>{escape(str(mapping.get("policy")))}</dd>
    <dt>cut_id</dt><dd>{escape(str(mapping.get("cut_id")))}</dd>
    <dt>requested_range</dt><dd>{escape(str(mapping.get("requested_start_seconds")))}-{escape(str(mapping.get("requested_end_seconds")))}</dd>
    <dt>render_range</dt><dd>start={escape(str(mapping.get("render_start_seconds")))} duration={escape(str(mapping.get("render_duration_seconds")))}</dd>
    <dt>clamped</dt><dd>{escape(str(mapping.get("clamped")).lower())}</dd>
  </dl>
  <h2>Output Metadata</h2>
  <dl>
    <dt>duration_seconds</dt><dd>{escape(str(metadata.get("duration_seconds")))}</dd>
    <dt>container</dt><dd>{escape(str(metadata.get("container")))}</dd>
    <dt>video_codec</dt><dd>{escape(str(metadata.get("video_codec")))}</dd>
    <dt>audio_codec</dt><dd>{escape(str(metadata.get("audio_codec")))}</dd>
    <dt>resolution</dt><dd>{escape(str(metadata.get("resolution")))}</dd>
    <dt>fps</dt><dd>{escape(str(metadata.get("fps")))}</dd>
    <dt>stream_count</dt><dd>{escape(str(metadata.get("stream_count")))}</dd>
  </dl>
  <h2>Render Attempts</h2>
  <table>
    <thead>
      <tr><th>profile</th><th>container</th><th>video</th><th>audio</th><th>status</th><th>failure</th><th>selected</th></tr>
    </thead>
    <tbody>
{attempt_rows}
    </tbody>
  </table>
  <h2>Warnings</h2>
  <ul>
{warning_items}
  </ul>
</body>
</html>
"""


def _list_of_strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _as_float(value: Any, *, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RenderCliError(f"{field} must be numeric") from exc


def _optional_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _wav_duration(path: Path | None) -> float | None:
    if path is None:
        return None
    try:
        with wave.open(str(path), "rb") as wav:
            rate = wav.getframerate()
            if rate <= 0:
                return None
            return wav.getnframes() / float(rate)
    except (OSError, EOFError, wave.Error):
        return None


def _display_path(path: Path | None, base: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _first_planned_output(preflight: dict[str, Any]) -> str | None:
    plan = preflight.get("command_plan") if isinstance(preflight.get("command_plan"), dict) else {}
    profiles = plan.get("render_profiles") if isinstance(plan.get("render_profiles"), list) else []
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("output_path"):
            return str(profile["output_path"]).replace("\\", "/")
    return None


def _print_payload(payload: dict[str, Any], *, fmt: str) -> None:
    if fmt == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if "rendered_video" in payload:
        print(f"rendered_video: {payload['rendered_video']}")
        print(f"render_receipt: {payload['render_receipt']}")
        print(f"render_manifest: {payload['render_manifest']}")
        print(f"render_report: {payload['render_report']}")
        metadata = payload["output_metadata"]
        print(f"duration_seconds: {metadata.get('duration_seconds')}")
        print(f"container: {metadata.get('container')}")
        print(f"video_codec: {metadata.get('video_codec')}")
        print(f"audio_codec: {metadata.get('audio_codec')}")
        print(f"resolution: {metadata.get('resolution')}")
        print(f"fps: {metadata.get('fps')}")
        print(f"stream_count: {metadata.get('stream_count')}")
        selected_profile = payload.get("selected_render_profile")
        if selected_profile:
            print(f"selected_render_profile: {selected_profile.get('profile_id')}")
        if "fallback_used" in payload:
            print(f"fallback_used: {str(payload['fallback_used']).lower()}")
        subtitle_burn_in = payload.get("subtitle_burn_in") or {}
        if subtitle_burn_in:
            print(f"subtitle_burn_in_status: {subtitle_burn_in.get('status')}")
            source_ref = subtitle_burn_in.get("source_ref") or {}
            print(f"subtitle_source_type: {source_ref.get('source_type')}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        for warning in payload["warnings"]:
            print(f"warning: {warning}")
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))
