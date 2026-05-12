"""ED-06 minimal NLE export.

This is an export plumbing proof, not a renderer and not production edit
acceptance. The first format is a human-readable CSV cut list plus a JSON
manifest that carries source/provenance readback.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from .edit_pack import load_edit_pack, validate_edit_pack

SCHEMA_VERSION = "v1"
EXPORT_FORMAT = "csv_cut_list_v1"

CSV_FIELDS = [
    "episode_id",
    "cut_id",
    "selected",
    "title",
    "start_seconds",
    "end_seconds",
    "duration_seconds",
    "source",
    "confidence",
    "context_status",
    "reason",
    "source_segment_ids",
    "subtitle_ids",
    "subtitle_text",
    "subtitle_ranges",
    "source_audio_material_id",
    "source_audio_path",
    "source_audio_provider",
    "source_audio_mode",
    "source_url",
    "source_audio_sha256",
    "transcript_path",
    "transcript_provider",
    "transcript_engine",
    "transcript_model",
    "transcript_real",
    "transcript_segment_count",
    "transcript_duration_seconds",
    "production_edit_candidate",
    "warnings",
]


class NleExportError(Exception):
    """Raised when ED-06 cannot export the edit pack."""


def export_csv_cut_list(
    *,
    edit_pack_path: Path,
    output_dir: Path,
    preview_manifest_path: Path | None = None,
    transcript_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    base = base_dir or Path.cwd()
    edit_pack = load_edit_pack(edit_pack_path)
    issues = validate_edit_pack(edit_pack)
    if issues:
        raise NleExportError(
            "edit_pack invalid: "
            + ", ".join(f"{issue.code}@{issue.field}" for issue in issues)
        )

    episode_id = edit_pack["episode_id"]
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "nle_cut_list.csv"
    manifest_path = output_dir / "nle_export_manifest.json"
    report_path = output_dir / "nle_export_report.html"

    preview_path = _resolve_preview_manifest(
        preview_manifest_path,
        edit_pack_path=edit_pack_path,
    )
    preview_manifest = _load_json_optional(preview_path) if preview_path else {}
    resolved_transcript_path = _resolve_transcript_path(
        transcript_path,
        edit_pack_path=edit_pack_path,
    )
    transcript = _load_json_optional(resolved_transcript_path) if resolved_transcript_path else {}
    transcript_readback = _transcript_readback(
        transcript_path=resolved_transcript_path,
        transcript=transcript,
        base_dir=base,
    )
    source_readback = _source_readback(
        edit_pack=edit_pack,
        edit_pack_path=edit_pack_path,
        preview_manifest=preview_manifest,
        base_dir=base,
    )
    warnings = _warnings(
        edit_pack=edit_pack,
        preview_manifest=preview_manifest,
        transcript_readback=transcript_readback,
    )
    rows = _rows(
        edit_pack=edit_pack,
        source_readback=source_readback,
        transcript_readback=transcript_readback,
        warnings=warnings,
    )

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "nle_export",
        "format": EXPORT_FORMAT,
        "episode_id": episode_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "production_edit_candidate": False,
        "input": {
            "edit_pack": display_path(edit_pack_path, base),
            "preview_manifest": display_path(preview_path, base) if preview_path else None,
            "transcript": display_path(resolved_transcript_path, base) if resolved_transcript_path else None,
        },
        "outputs": {
            "csv_cut_list": display_path(csv_path, base),
            "readback_manifest": display_path(manifest_path, base),
            "readback_report": display_path(report_path, base),
        },
        "summary": {
            "cut_rows": len(rows),
            "cut_candidates_count": len(edit_pack.get("cut_candidates") or []),
            "selected_cut_count": len(edit_pack.get("selected_cut_ids") or []),
            "subtitle_count": len(edit_pack.get("subtitles") or []),
            "review_status": (edit_pack.get("review") or {}).get("status", "unknown"),
            "transcript_segment_count": transcript_readback.get("segment_count"),
        },
        "source_refs": {
            "rights_manifest": edit_pack.get("rights_manifest_path"),
            "material_ledger": edit_pack.get("material_ledger_path"),
            "source_audio": source_readback,
            "transcript": transcript_readback,
        },
        "warnings": warnings,
    }
    _write_json(manifest, manifest_path)
    report_path.write_text(_make_report_html(manifest=manifest, rows=rows), encoding="utf-8")
    return {
        "manifest": manifest,
        "csv_path": csv_path,
        "manifest_path": manifest_path,
        "report_path": report_path,
        "rows": rows,
    }


def display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _rows(
    *,
    edit_pack: dict[str, Any],
    source_readback: dict[str, Any],
    transcript_readback: dict[str, Any],
    warnings: list[str],
) -> list[dict[str, Any]]:
    cuts = edit_pack.get("cut_candidates") or []
    selected_ids = edit_pack.get("selected_cut_ids") or []
    selected_set = set(selected_ids)
    if selected_ids:
        ordered = [
            cut
            for cut_id in selected_ids
            for cut in cuts
            if isinstance(cut, dict) and cut.get("id") == cut_id
        ]
    else:
        ordered = [cut for cut in cuts if isinstance(cut, dict)]

    return [
        _row(
            edit_pack=edit_pack,
            cut=cut,
            selected=not selected_ids or cut.get("id") in selected_set,
            source_readback=source_readback,
            transcript_readback=transcript_readback,
            warnings=warnings,
        )
        for cut in ordered
    ]


def _row(
    *,
    edit_pack: dict[str, Any],
    cut: dict[str, Any],
    selected: bool,
    source_readback: dict[str, Any],
    transcript_readback: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    subtitles = _subtitles_for_cut(edit_pack.get("subtitles") or [], cut)
    start = float(cut.get("start_seconds", 0.0))
    end = float(cut.get("end_seconds", start))
    return {
        "episode_id": edit_pack["episode_id"],
        "cut_id": cut.get("id", ""),
        "selected": str(selected).lower(),
        "title": _title(edit_pack, cut),
        "start_seconds": _seconds(start),
        "end_seconds": _seconds(end),
        "duration_seconds": _seconds(end - start),
        "source": cut.get("source", ""),
        "confidence": "" if cut.get("confidence") is None else cut.get("confidence"),
        "context_status": (cut.get("context_check") or {}).get("status", "not_checked"),
        "reason": cut.get("reason", ""),
        "source_segment_ids": ";".join(cut.get("source_segment_ids") or []),
        "subtitle_ids": ";".join(str(s.get("id", "")) for s in subtitles),
        "subtitle_text": " | ".join(str(s.get("text", "")) for s in subtitles),
        "subtitle_ranges": " | ".join(
            f"{_seconds(float(s.get('start_seconds', 0.0)))}-{_seconds(float(s.get('end_seconds', 0.0)))}"
            for s in subtitles
        ),
        "source_audio_material_id": source_readback.get("material_id", ""),
        "source_audio_path": source_readback.get("source_wav", ""),
        "source_audio_provider": source_readback.get("provider", ""),
        "source_audio_mode": source_readback.get("mode", ""),
        "source_url": source_readback.get("source_url") or "",
        "source_audio_sha256": source_readback.get("sha256", ""),
        "transcript_path": transcript_readback.get("path") or "",
        "transcript_provider": transcript_readback.get("provider", ""),
        "transcript_engine": transcript_readback.get("engine", ""),
        "transcript_model": transcript_readback.get("model", ""),
        "transcript_real": str(bool(transcript_readback.get("real_transcript"))).lower(),
        "transcript_segment_count": transcript_readback.get("segment_count", ""),
        "transcript_duration_seconds": _seconds(float(transcript_readback.get("duration_seconds") or 0.0))
        if transcript_readback.get("duration_seconds") is not None
        else "",
        "production_edit_candidate": "false",
        "warnings": " | ".join(warnings),
    }


def _subtitles_for_cut(subtitles: list[Any], cut: dict[str, Any]) -> list[dict[str, Any]]:
    cut_id = cut.get("id")
    start = float(cut.get("start_seconds", 0.0))
    end = float(cut.get("end_seconds", 0.0))
    matched = [
        subtitle
        for subtitle in subtitles
        if isinstance(subtitle, dict) and subtitle.get("cut_id") == cut_id
    ]
    if matched:
        return matched
    return [
        subtitle
        for subtitle in subtitles
        if isinstance(subtitle, dict)
        and float(subtitle.get("start_seconds", -1.0)) >= start
        and float(subtitle.get("end_seconds", -1.0)) <= end
    ]


def _title(edit_pack: dict[str, Any], cut: dict[str, Any]) -> str:
    reason = str(cut.get("reason") or "").strip()
    if reason:
        return reason
    topic = str((edit_pack.get("editing_intent") or {}).get("topic") or "").strip()
    return topic or str(cut.get("id") or "cut")


def _warnings(
    *,
    edit_pack: dict[str, Any],
    preview_manifest: dict[str, Any],
    transcript_readback: dict[str, Any],
) -> list[str]:
    warnings = [
        "ED-06 CSV export is a plumbing proof, not production edit acceptance.",
    ]
    if transcript_readback.get("available"):
        if transcript_readback.get("real_transcript") is True:
            warnings.append(
                "real STT transcript is unreviewed; transcript quality is not creative acceptance."
            )
        else:
            warnings.append("transcript real_transcript is false; export remains preview-only.")
        for warning in transcript_readback.get("warnings") or []:
            if warning not in warnings:
                warnings.append(str(warning))
    else:
        transcript = preview_manifest.get("transcript") if isinstance(preview_manifest, dict) else {}
        if isinstance(transcript, dict):
            source = transcript.get("source")
            if transcript.get("not_for_acceptance") is True:
                warnings.append("preview transcript is not acceptance material.")
            if source in {"fixture", "deterministic_fake"}:
                warnings.append(f"{source} transcript means exported cuts remain preview-only.")
        else:
            warnings.append("preview_manifest transcript readback is unavailable.")
    review_status = (edit_pack.get("review") or {}).get("status", "unknown")
    if review_status != "approved":
        warnings.append(f"edit_pack review.status is {review_status}; export is not approved.")
    if not edit_pack.get("selected_cut_ids"):
        warnings.append("selected_cut_ids is empty; exporting all cut candidates for review.")
    return warnings


def _transcript_readback(
    *,
    transcript_path: Path | None,
    transcript: dict[str, Any],
    base_dir: Path,
) -> dict[str, Any]:
    if not transcript_path or not isinstance(transcript, dict) or not transcript:
        return {
            "available": False,
            "path": display_path(transcript_path, base_dir) if transcript_path else None,
            "provider": "",
            "engine": "",
            "model": "",
            "real_transcript": False,
            "segment_count": None,
            "duration_seconds": None,
            "source_audio_path": "",
            "source_audio_material_id": "",
            "source_audio_sha256": "",
            "warnings": [],
        }
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    source_audio = (
        transcript.get("source_audio")
        if isinstance(transcript.get("source_audio"), dict)
        else {}
    )
    segments = transcript.get("segments") if isinstance(transcript.get("segments"), list) else []
    segment_count = stt.get("segment_count")
    if not isinstance(segment_count, int):
        segment_count = transcript.get("segment_count")
    if not isinstance(segment_count, int):
        segment_count = len(segments)
    return {
        "available": True,
        "path": display_path(transcript_path, base_dir),
        "provider": stt.get("provider") or stt.get("engine") or "",
        "engine": stt.get("engine", ""),
        "model": stt.get("model") or (stt.get("params") or {}).get("model_path") or "",
        "engine_version": stt.get("engine_version", ""),
        "real_transcript": stt.get("real_transcript") is True,
        "segment_count": segment_count,
        "duration_seconds": source_audio.get("duration_seconds"),
        "source_audio_path": source_audio.get("path", ""),
        "source_audio_material_id": source_audio.get("material_id", ""),
        "source_audio_sha256": source_audio.get("sha256", ""),
        "warnings": stt.get("warnings") if isinstance(stt.get("warnings"), list) else [],
    }


def _source_readback(
    *,
    edit_pack: dict[str, Any],
    edit_pack_path: Path,
    preview_manifest: dict[str, Any],
    base_dir: Path,
) -> dict[str, Any]:
    material = preview_manifest.get("material") if isinstance(preview_manifest, dict) else {}
    provenance = (
        preview_manifest.get("source_audio_provenance")
        if isinstance(preview_manifest.get("source_audio_provenance"), dict)
        else {}
    )
    ledger_entry = material.get("ledger_entry") if isinstance(material, dict) else {}
    if isinstance(material, dict) and material.get("source_wav"):
        return {
            "material_id": material.get("material_id", ""),
            "source_wav": material.get("source_wav", ""),
            "fetch_receipt": material.get("fetch_receipt", ""),
            "sidecar": material.get("sidecar", ""),
            "material_ledger": material.get("material_ledger", edit_pack.get("material_ledger_path", "")),
            "mode": provenance.get("mode", ""),
            "provider": provenance.get("provider", ""),
            "source_url": provenance.get("source_url"),
            "sha256": provenance.get("output_sha256") or ledger_entry.get("hash_sha256", ""),
            "rights_status_at_fetch": provenance.get("rights_status_at_fetch", "unknown"),
            "rights_hard_gate": provenance.get("rights_hard_gate", False),
        }

    ledger_path = _resolve_path(
        edit_pack.get("material_ledger_path"),
        anchor=edit_pack_path.parent,
    )
    ledger = _load_json_optional(ledger_path) if ledger_path else {}
    material_entry = next(
        (
            item
            for item in ledger.get("materials") or []
            if isinstance(item, dict) and item.get("kind") == "source_audio"
        ),
        {},
    )
    sidecar_path = _resolve_path(
        material_entry.get("sidecar_path"),
        anchor=ledger_path.parent if ledger_path else edit_pack_path.parent,
    )
    receipt_path = sidecar_path.parent / "fetch_receipt.json" if sidecar_path else None
    sidecar = _load_json_optional(sidecar_path) if sidecar_path else {}
    receipt = _load_json_optional(receipt_path) if receipt_path and receipt_path.exists() else {}
    sidecar_source = sidecar.get("source") if isinstance(sidecar.get("source"), dict) else {}
    sidecar_provenance = (
        sidecar.get("provenance") if isinstance(sidecar.get("provenance"), dict) else {}
    )
    receipt_input = receipt.get("input") if isinstance(receipt.get("input"), dict) else {}
    return {
        "material_id": material_entry.get("id", ""),
        "source_wav": material_entry.get("file_path", ""),
        "fetch_receipt": display_path(receipt_path, base_dir) if receipt_path and receipt_path.exists() else "",
        "sidecar": display_path(sidecar_path, base_dir) if sidecar_path else material_entry.get("sidecar_path", ""),
        "material_ledger": display_path(ledger_path, base_dir) if ledger_path else edit_pack.get("material_ledger_path", ""),
        "mode": receipt.get("mode") or sidecar_provenance.get("mode") or "",
        "provider": receipt.get("provider")
        or sidecar_provenance.get("provider")
        or sidecar_source.get("retrieval_method")
        or "",
        "source_url": receipt.get("source_url")
        or receipt_input.get("source_url")
        or sidecar_provenance.get("source_url")
        or sidecar_source.get("url"),
        "sha256": material_entry.get("hash_sha256", ""),
        "rights_status_at_fetch": material_entry.get("rights_status_at_registration", "unknown"),
        "rights_hard_gate": False,
    }


def _resolve_preview_manifest(
    preview_manifest_path: Path | None,
    *,
    edit_pack_path: Path,
) -> Path | None:
    if preview_manifest_path:
        return preview_manifest_path
    sibling = edit_pack_path.parent / "preview_manifest.json"
    return sibling if sibling.exists() else None


def _resolve_transcript_path(
    transcript_path: Path | None,
    *,
    edit_pack_path: Path,
) -> Path | None:
    if transcript_path:
        return transcript_path
    sibling = edit_pack_path.parent / "transcript.json"
    return sibling if sibling.exists() else None


def _resolve_path(value: object, *, anchor: Path) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    raw = Path(value)
    candidates = [raw]
    if not raw.is_absolute():
        candidates.extend([Path.cwd() / raw, anchor / raw])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


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


def _make_report_html(*, manifest: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    source = manifest.get("source_refs", {}).get("source_audio", {})
    transcript = manifest.get("source_refs", {}).get("transcript", {})
    outputs = manifest.get("outputs", {})
    warnings = manifest.get("warnings", [])
    rows_html = "\n".join(
        "<tr>"
        f"<td>{escape(str(row.get('cut_id', '')))}</td>"
        f"<td>{escape(str(row.get('start_seconds', '')))}–{escape(str(row.get('end_seconds', '')))}</td>"
        f"<td>{escape(str(row.get('title', '')))}</td>"
        f"<td>{escape(str(row.get('subtitle_text', '')))}</td>"
        "</tr>"
        for row in rows
    )
    warning_items = "\n".join(f"<li>{escape(str(warning))}</li>" for warning in warnings)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>ED-06 NLE Export Readback</title>
</head>
<body>
  <h1>ED-06 NLE Export Readback</h1>
  <p>This CSV export is a plumbing proof, not production edit acceptance.</p>
  <h2>Artifact Paths</h2>
  <ul>
    <li>csv_cut_list: {escape(str(outputs.get("csv_cut_list", "")))}</li>
    <li>readback_manifest: {escape(str(outputs.get("readback_manifest", "")))}</li>
    <li>readback_report: {escape(str(outputs.get("readback_report", "")))}</li>
  </ul>
  <h2>Source Audio Provenance</h2>
  <dl>
    <dt>provider</dt><dd>{escape(str(source.get("provider", "")))}</dd>
    <dt>mode</dt><dd>{escape(str(source.get("mode", "")))}</dd>
    <dt>source_url</dt><dd>{escape(str(source.get("source_url") or ""))}</dd>
    <dt>sha256</dt><dd>{escape(str(source.get("sha256", "")))}</dd>
    <dt>rights_status_at_fetch</dt><dd>{escape(str(source.get("rights_status_at_fetch", "")))}</dd>
  </dl>
  <h2>Transcript Provenance</h2>
  <dl>
    <dt>path</dt><dd>{escape(str(transcript.get("path") or ""))}</dd>
    <dt>provider</dt><dd>{escape(str(transcript.get("provider", "")))}</dd>
    <dt>engine</dt><dd>{escape(str(transcript.get("engine", "")))}</dd>
    <dt>model</dt><dd>{escape(str(transcript.get("model", "")))}</dd>
    <dt>real_transcript</dt><dd>{escape(str(transcript.get("real_transcript", False)).lower())}</dd>
    <dt>segment_count</dt><dd>{escape(str(transcript.get("segment_count", "")))}</dd>
    <dt>duration_seconds</dt><dd>{escape(str(transcript.get("duration_seconds", "")))}</dd>
  </dl>
  <h2>Cut List Preview</h2>
  <table>
    <thead><tr><th>cut_id</th><th>range</th><th>title</th><th>subtitle</th></tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  <h2>Warnings</h2>
  <ul>
{warning_items}
  </ul>
</body>
</html>
"""


def _seconds(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")
