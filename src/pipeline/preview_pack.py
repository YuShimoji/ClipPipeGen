"""SH-05 local preview pack artifacts.

The preview pack is a read-only review surface over generated artifacts. It
does not acquire external media, modify timings, or create video output.
"""

from __future__ import annotations

import html
import json
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .edit_pack import load_edit_pack
from .rights_manifest import load_rights_manifest
from .transcript import load_transcript

SCHEMA_VERSION = "v1"
PREVIEW_WORK_DIR = "_preview_pack"
FAKE_SEGMENTS_FILENAME = "deterministic_fake_segments.json"
INPUT_KINDS = {"local_media_file", "existing_source_audio_material"}
TRANSCRIPT_SOURCES = {"fixture", "deterministic_fake"}


def write_deterministic_fake_segments(
    *,
    output_path: Path,
    duration_seconds: float | None,
) -> list[dict[str, Any]]:
    segments = deterministic_fake_segments(duration_seconds=duration_seconds)
    write_json(segments, output_path)
    return segments


def deterministic_fake_segments(*, duration_seconds: float | None) -> list[dict[str, Any]]:
    duration = duration_seconds if duration_seconds and duration_seconds > 0 else 12.0
    count = max(1, min(4, int(duration // 4) or 1))
    step = duration / count
    segments: list[dict[str, Any]] = []
    for i in range(count):
        start = round(i * step, 3)
        end = round(duration if i == count - 1 else (i + 1) * step, 3)
        if end <= start:
            end = round(start + 1.0, 3)
        segments.append(
            {
                "id": f"seg_{i + 1:03d}",
                "start_seconds": start,
                "end_seconds": end,
                "text": f"Deterministic preview segment {i + 1}",
                "confidence": 0.5,
            }
        )
    return segments


def read_wav_duration_seconds(path: Path) -> float | None:
    try:
        with wave.open(str(path), "rb") as wav:
            frame_rate = wav.getframerate()
            if frame_rate <= 0:
                return None
            return wav.getnframes() / frame_rate
    except (OSError, wave.Error):
        return None


def build_preview_manifest(
    *,
    episode_id: str,
    episode_dir: Path,
    input_path: Path,
    material_id: str,
    source_wav_path: Path,
    fetch_receipt_path: Path,
    sidecar_path: Path,
    material_ledger_path: Path,
    transcript_path: Path,
    transcript_source: str,
    edit_pack_path: Path,
    report_path: Path,
    warnings: list[str],
    next_actions: list[str],
    base_dir: Path,
    input_kind: str = "local_media_file",
) -> dict[str, Any]:
    edit_pack = load_edit_pack(edit_pack_path)
    transcript = load_transcript(transcript_path)
    receipt = _load_json_optional(fetch_receipt_path)
    sidecar = _load_json_optional(sidecar_path)
    ledger = _load_json_optional(material_ledger_path)
    material_entry = _find_material_entry(ledger, material_id)
    cuts = edit_pack.get("cut_candidates") or []
    subtitles = edit_pack.get("subtitles") or []
    context_counts = _context_counts(cuts)

    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": {
            "kind": input_kind,
            "path": display_path(input_path, base_dir),
        },
        "material": {
            "material_id": material_id,
            "source_wav": display_path(source_wav_path, base_dir),
            "fetch_receipt": display_path(fetch_receipt_path, base_dir),
            "sidecar": display_path(sidecar_path, base_dir),
            "material_ledger": display_path(material_ledger_path, base_dir),
            "ledger_entry": _material_entry_readback(material_entry),
        },
        "source_audio_provenance": _source_audio_provenance(
            receipt=receipt,
            sidecar=sidecar,
            material_entry=material_entry,
        ),
        "transcript": {
            "source": transcript_source,
            "path": display_path(transcript_path, base_dir),
            "segment_count": len(transcript.get("segments") or []),
            "not_for_acceptance": True,
        },
        "cuts": {
            "path": display_path(edit_pack_path, base_dir),
            "candidate_count": len(cuts),
            "context_counts": context_counts,
        },
        "subtitles": {
            "path": display_path(edit_pack_path, base_dir),
            "subtitle_count": len(subtitles),
        },
        "report": {
            "path": display_path(report_path, base_dir),
        },
        "warnings": warnings,
        "next_actions": next_actions,
    }


def validate_preview_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return lightweight schema issues for SH-05 preview manifests."""
    issues: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        issues.append("schema_version must be v1")
    _require_string(manifest, "episode_id", issues)
    _require_string(manifest, "created_at", issues)

    input_info = _require_dict(manifest, "input", issues)
    if input_info:
        if input_info.get("kind") not in INPUT_KINDS:
            issues.append("input.kind must be local_media_file or existing_source_audio_material")
        _require_string(input_info, "path", issues, "input.path")

    material = _require_dict(manifest, "material", issues)
    if material:
        _require_string(material, "material_id", issues, "material.material_id")
        _require_string(material, "source_wav", issues, "material.source_wav")
        _require_string(material, "fetch_receipt", issues, "material.fetch_receipt")
        _require_string(material, "sidecar", issues, "material.sidecar")
        _require_string(material, "material_ledger", issues, "material.material_ledger")
        _require_dict(material, "ledger_entry", issues, "material.ledger_entry")

    provenance = _require_dict(manifest, "source_audio_provenance", issues)
    if provenance:
        _require_string(provenance, "mode", issues, "source_audio_provenance.mode")
        _require_string(provenance, "provider", issues, "source_audio_provenance.provider")

    transcript = _require_dict(manifest, "transcript", issues)
    if transcript:
        if transcript.get("source") not in TRANSCRIPT_SOURCES:
            issues.append("transcript.source must be fixture or deterministic_fake")
        _require_string(transcript, "path", issues, "transcript.path")
        _require_int(transcript, "segment_count", issues, "transcript.segment_count")
        if transcript.get("not_for_acceptance") is not True:
            issues.append("transcript.not_for_acceptance must be true")

    cuts = _require_dict(manifest, "cuts", issues)
    if cuts:
        _require_string(cuts, "path", issues, "cuts.path")
        _require_int(cuts, "candidate_count", issues, "cuts.candidate_count")
        _require_dict(cuts, "context_counts", issues, "cuts.context_counts")

    subtitles = _require_dict(manifest, "subtitles", issues)
    if subtitles:
        _require_string(subtitles, "path", issues, "subtitles.path")
        _require_int(subtitles, "subtitle_count", issues, "subtitles.subtitle_count")

    report = _require_dict(manifest, "report", issues)
    if report:
        _require_string(report, "path", issues, "report.path")

    if not isinstance(manifest.get("warnings"), list):
        issues.append("warnings must be a list")
    if not isinstance(manifest.get("next_actions"), list):
        issues.append("next_actions must be a list")
    return issues


def make_preview_report_html(
    *,
    manifest: dict[str, Any],
    source_wav_path: Path,
    edit_pack_path: Path,
    transcript_path: Path,
    fetch_receipt_path: Path,
    sidecar_path: Path,
    material_ledger_path: Path,
    rights_manifest_path: Path,
    manifest_path: Path,
    report_path: Path,
) -> str:
    edit_pack = load_edit_pack(edit_pack_path)
    transcript = load_transcript(transcript_path)
    receipt = _load_json_optional(fetch_receipt_path)
    rights = _load_json_optional(rights_manifest_path)
    compliance = (rights.get("compliance_check") or {}) if isinstance(rights, dict) else {}
    rights_status = compliance.get("status", "unknown")
    audio_src = display_path(source_wav_path, report_path.parent)
    artifact_paths = {
        "Source WAV": source_wav_path,
        "Preview manifest": manifest_path,
        "Fetch receipt": fetch_receipt_path,
        "Sidecar": sidecar_path,
        "Material ledger": material_ledger_path,
        "Transcript": transcript_path,
        "Edit pack": edit_pack_path,
    }

    cuts = edit_pack.get("cut_candidates") or []
    subtitles = edit_pack.get("subtitles") or []
    segments = transcript.get("segments") or []
    decision_warnings = _decision_warnings(manifest, rights_status)

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>ClipPipeGen Local Preview Pack</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,'Yu Gothic','Meiryo',sans-serif;margin:24px;line-height:1.45;color:#1f2933;background:#f7f8fa}",
            "main{max-width:1120px;margin:0 auto}",
            "section{margin:18px 0;padding:16px;background:#fff;border:1px solid #d8dde5;border-radius:8px}",
            "h1{font-size:28px;margin:0 0 6px}h2{font-size:18px;margin:0 0 12px}",
            ".status-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}",
            ".status-item{border:1px solid #d8dde5;border-radius:6px;padding:10px;background:#fbfcfe}",
            ".label{font-size:12px;color:#5f6b7a;text-transform:uppercase;letter-spacing:0}.value{font-weight:650;margin-top:4px}",
            ".badge{display:inline-block;padding:2px 8px;border-radius:999px;border:1px solid #c9d2df;background:#eef3fa}.badge.warning{border-color:#e3b341;background:#fff7db;color:#6f4700}",
            "table{width:100%;border-collapse:collapse;font-size:14px}th,td{border-bottom:1px solid #e5e8ee;padding:8px;text-align:left;vertical-align:top;overflow-wrap:anywhere}",
            "code{background:#eef1f5;padding:2px 4px;border-radius:4px}.warning{color:#8a4b00}.muted{color:#5f6b7a}",
            ".warning-panel{border-color:#e3b341;background:#fffaf0}.warning-panel h2{color:#6f4700}",
            "a{color:#075985}ul{padding-left:20px}",
            "audio{width:100%;max-width:520px}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            f"<h1>Local Preview Pack: {esc(manifest['episode_id'])}</h1>",
            '<p class="muted">Read-only artifact preview. No video file is generated.</p>',
            _status_summary_section(manifest, rights_status),
            _list_section("Decision Warnings", decision_warnings, css_class="warning"),
            _summary_section(manifest, rights_status, receipt),
            _source_audio_provenance_section(manifest.get("source_audio_provenance") or {}),
            _artifact_links_section(artifact_paths, report_path.parent),
            _audio_section(audio_src),
            _segments_section(segments),
            _cuts_section(cuts),
            _subtitles_section(subtitles),
            _list_section("Warnings", manifest.get("warnings") or [], css_class="warning"),
            _list_section("Next Actions", manifest.get("next_actions") or []),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _context_counts(cuts: list[Any]) -> dict[str, int]:
    counts = {"passed": 0, "needs_review": 0, "failed": 0, "not_checked": 0}
    for cut in cuts:
        if not isinstance(cut, dict):
            continue
        status = ((cut.get("context_check") or {}).get("status")) or "not_checked"
        if status not in counts:
            counts[status] = 0
        counts[status] += 1
    return counts


def _load_json_optional(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _find_material_entry(ledger: dict[str, Any], material_id: str) -> dict[str, Any]:
    for material in ledger.get("materials") or []:
        if isinstance(material, dict) and material.get("id") == material_id:
            return material
    return {}


def _material_entry_readback(entry: dict[str, Any]) -> dict[str, Any]:
    compliance = entry.get("compliance_link") or {}
    return {
        "id": entry.get("id", "unknown"),
        "kind": entry.get("kind", "unknown"),
        "subkind": entry.get("subkind", "unknown"),
        "file_path": entry.get("file_path", "unknown"),
        "sidecar_path": entry.get("sidecar_path", "unknown"),
        "hash_sha256": entry.get("hash_sha256", "unknown"),
        "byte_size": entry.get("byte_size", 0),
        "intended_uses": list(entry.get("intended_uses") or []),
        "registered_by": entry.get("registered_by", "unknown"),
        "compliance_status_at_registration": compliance.get(
            "compliance_status_at_registration",
            "unknown",
        ),
    }


def _source_audio_provenance(
    *,
    receipt: dict[str, Any],
    sidecar: dict[str, Any],
    material_entry: dict[str, Any],
) -> dict[str, Any]:
    receipt_input = receipt.get("input") if isinstance(receipt.get("input"), dict) else {}
    sidecar_source = sidecar.get("source") if isinstance(sidecar.get("source"), dict) else {}
    sidecar_license = sidecar.get("license") if isinstance(sidecar.get("license"), dict) else {}
    rights_snapshot = (
        receipt.get("rights_snapshot")
        if isinstance(receipt.get("rights_snapshot"), dict)
        else {}
    )
    intermediate = (
        receipt.get("intermediate")
        if isinstance(receipt.get("intermediate"), dict)
        else {}
    )
    tools = receipt.get("tools") if isinstance(receipt.get("tools"), list) else []
    outputs = receipt.get("outputs") if isinstance(receipt.get("outputs"), list) else []
    first_output = outputs[0] if outputs and isinstance(outputs[0], dict) else {}
    return {
        "mode": receipt.get("mode", "unknown"),
        "provider": receipt.get("provider", "unknown"),
        "command_summary": receipt.get("command_summary", "unknown"),
        "source_url": receipt_input.get("source_url") or receipt.get("source_url"),
        "local_path": receipt_input.get("local_path"),
        "retrieval_method": sidecar_source.get("retrieval_method", "unknown"),
        "retrieved_at": sidecar_source.get("retrieved_at", "unknown"),
        "retrieved_by": sidecar_source.get("retrieved_by", "unknown"),
        "source_kind": sidecar_source.get("kind", "unknown"),
        "source_notes": sidecar_source.get("notes", ""),
        "license_kind": sidecar_license.get("kind", "unknown"),
        "rights_status_at_fetch": rights_snapshot.get(
            "compliance_status_at_fetch",
            "unknown",
        ),
        "rights_hard_gate": rights_snapshot.get("hard_gate", False),
        "intermediate_retained": intermediate.get("retained"),
        "output_sha256": receipt.get("sha256")
        or first_output.get("sha256", material_entry.get("hash_sha256")),
        "ledger_registered_by": material_entry.get("registered_by", "unknown"),
        "tools": [
            {
                "name": tool.get("name", "unknown"),
                "version": tool.get("version", "unknown"),
            }
            for tool in tools
            if isinstance(tool, dict)
        ],
    }


def _require_dict(payload: dict[str, Any], key: str, issues: list[str], label: str | None = None) -> dict[str, Any]:
    value = payload.get(key)
    name = label or key
    if not isinstance(value, dict):
        issues.append(f"{name} must be an object")
        return {}
    return value


def _require_string(payload: dict[str, Any], key: str, issues: list[str], label: str | None = None) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        issues.append(f"{label or key} must be a non-empty string")


def _require_int(payload: dict[str, Any], key: str, issues: list[str], label: str | None = None) -> None:
    value = payload.get(key)
    if not isinstance(value, int) or value < 0:
        issues.append(f"{label or key} must be a non-negative integer")


def _summary_section(
    manifest: dict[str, Any],
    rights_status: str,
    receipt: dict[str, Any],
) -> str:
    rows = [
        ("Input", manifest["input"]["path"]),
        ("Material", manifest["material"]["material_id"]),
        ("Source WAV", manifest["material"]["source_wav"]),
        ("Receipt", manifest["material"]["fetch_receipt"]),
        ("Transcript", f"{manifest['transcript']['source']} ({manifest['transcript']['segment_count']} segments)"),
        ("Cuts", str(manifest["cuts"]["candidate_count"])),
        ("Subtitles", str(manifest["subtitles"]["subtitle_count"])),
        ("Rights status", rights_status),
        ("Provider", receipt.get("provider", "unknown")),
    ]
    body = "".join(f"<tr><th>{esc(k)}</th><td><code>{esc(v)}</code></td></tr>" for k, v in rows)
    return f"<section><h2>Episode</h2><table>{body}</table></section>"


def _source_audio_provenance_section(provenance: dict[str, Any]) -> str:
    tools = provenance.get("tools") if isinstance(provenance.get("tools"), list) else []
    tool_text = ", ".join(
        f"{tool.get('name', 'unknown')} {tool.get('version', 'unknown')}"
        for tool in tools
        if isinstance(tool, dict)
    ) or "none"
    rows = [
        ("Mode", provenance.get("mode", "unknown")),
        ("Provider", provenance.get("provider", "unknown")),
        ("Command summary", provenance.get("command_summary", "unknown")),
        ("Source URL", provenance.get("source_url") or "none"),
        ("Local path", provenance.get("local_path") or "none"),
        ("Retrieval method", provenance.get("retrieval_method", "unknown")),
        ("Retrieved by", provenance.get("retrieved_by", "unknown")),
        ("Retrieved at", provenance.get("retrieved_at", "unknown")),
        ("Source kind", provenance.get("source_kind", "unknown")),
        ("License kind", provenance.get("license_kind", "unknown")),
        ("Rights at fetch", provenance.get("rights_status_at_fetch", "unknown")),
        ("Rights hard gate", str(provenance.get("rights_hard_gate", False)).lower()),
        ("Intermediate retained", str(provenance.get("intermediate_retained", "unknown")).lower()),
        ("Output sha256", provenance.get("output_sha256", "unknown")),
        ("Tools", tool_text),
    ]
    if provenance.get("source_notes"):
        rows.append(("Source notes", provenance["source_notes"]))
    body = "".join(f"<tr><th>{esc(k)}</th><td><code>{esc(v)}</code></td></tr>" for k, v in rows)
    return f"<section><h2>Source Audio Provenance</h2><table>{body}</table></section>"


def _status_summary_section(manifest: dict[str, Any], rights_status: str) -> str:
    transcript = manifest.get("transcript") or {}
    source = transcript.get("source", "unknown")
    not_for_acceptance = transcript.get("not_for_acceptance") is True
    rights_class = "badge warning" if rights_status != "passed" else "badge"
    acceptance_class = "badge warning" if not_for_acceptance else "badge"
    items = [
        ("Report mode", '<span class="badge">Read-only artifact preview</span>'),
        ("Transcript source", f'<span class="badge">{esc(source)}</span>'),
        (
            "Not for acceptance",
            f'<span class="{acceptance_class}">{esc(str(not_for_acceptance).lower())}</span>',
        ),
        ("Rights status", f'<span class="{rights_class}">{esc(rights_status)}</span>'),
    ]
    body = "".join(
        '<div class="status-item">'
        f'<div class="label">{esc(label)}</div>'
        f'<div class="value">{value}</div>'
        "</div>"
        for label, value in items
    )
    return f'<section><h2>Status Summary</h2><div class="status-grid">{body}</div></section>'


def _artifact_links_section(paths: dict[str, Path], base: Path) -> str:
    rows = []
    for label, path in paths.items():
        href = display_path(path, base)
        rows.append(
            "<tr>"
            f"<th>{esc(label)}</th>"
            f'<td><a href="{esc(href)}">{esc(href)}</a></td>'
            "</tr>"
        )
    return f"<section><h2>Artifact Links</h2><table>{''.join(rows)}</table></section>"


def _audio_section(audio_src: str) -> str:
    return (
        "<section><h2>Material Audio</h2>"
        f'<p><a href="{esc(audio_src)}">{esc(audio_src)}</a></p>'
        f'<audio controls preload="metadata" src="{esc(audio_src)}"></audio>'
        "</section>"
    )


def _segments_section(segments: list[Any]) -> str:
    rows = []
    for segment in segments[:8]:
        if not isinstance(segment, dict):
            continue
        rows.append(
            "<tr>"
            f"<td>{esc(segment.get('id'))}</td>"
            f"<td>{esc(segment.get('start_seconds'))}</td>"
            f"<td>{esc(segment.get('end_seconds'))}</td>"
            f"<td>{esc(segment.get('text'))}</td>"
            "</tr>"
        )
    return (
        "<section><h2>Transcript</h2>"
        "<table><thead><tr><th>ID</th><th>Start</th><th>End</th><th>Text</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        "</section>"
    )


def _cuts_section(cuts: list[Any]) -> str:
    rows = []
    for cut in cuts:
        if not isinstance(cut, dict):
            continue
        context = cut.get("context_check") or {}
        rows.append(
            "<tr>"
            f"<td>{esc(cut.get('id'))}</td>"
            f"<td>{esc(cut.get('start_seconds'))}</td>"
            f"<td>{esc(cut.get('end_seconds'))}</td>"
            f"<td>{esc(cut.get('confidence'))}</td>"
            f"<td>{esc(context.get('status', 'not_checked'))}</td>"
            f"<td>{esc(cut.get('reason'))}</td>"
            "</tr>"
        )
    return (
        "<section><h2>Cut Candidates</h2>"
        "<table><thead><tr><th>ID</th><th>Start</th><th>End</th><th>Score</th><th>Context</th><th>Reason</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        "</section>"
    )


def _subtitles_section(subtitles: list[Any]) -> str:
    rows = []
    for subtitle in subtitles[:20]:
        if not isinstance(subtitle, dict):
            continue
        rows.append(
            "<tr>"
            f"<td>{esc(subtitle.get('id'))}</td>"
            f"<td>{esc(subtitle.get('cut_id'))}</td>"
            f"<td>{esc(subtitle.get('start_seconds'))}</td>"
            f"<td>{esc(subtitle.get('end_seconds'))}</td>"
            f"<td>{esc(subtitle.get('text'))}</td>"
            "</tr>"
        )
    return (
        "<section><h2>Subtitle Draft</h2>"
        "<table><thead><tr><th>ID</th><th>Cut</th><th>Start</th><th>End</th><th>Text</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        "</section>"
    )


def _list_section(title: str, items: list[Any], *, css_class: str = "") -> str:
    if not items:
        items = ["none"]
    cls = f' class="{css_class}"' if css_class else ""
    section_cls = ' class="warning-panel"' if css_class == "warning" else ""
    rows = "".join(f"<li{cls}>{esc(item)}</li>" for item in items)
    return f"<section{section_cls}><h2>{esc(title)}</h2><ul>{rows}</ul></section>"


def _decision_warnings(manifest: dict[str, Any], rights_status: str) -> list[str]:
    transcript = manifest.get("transcript") or {}
    source = transcript.get("source", "unknown")
    warnings = [
        f"{source} transcript is not acceptance material.",
    ]
    if transcript.get("not_for_acceptance") is True:
        warnings.append("transcript.not_for_acceptance is true.")
        warnings.append("fake or fixture transcript and generated edit_pack are not production candidates.")
    if rights_status != "passed":
        warnings.append(f"rights {rights_status} is readback only.")
    return warnings
