"""Build human-review packets for selected cuts.

The packet is a review surface for edit decisions. It does not approve cuts,
alter edit timing, render video, or move an episode toward publishing.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from .edit_pack import load_edit_pack, validate_edit_pack
from .rights_manifest import load_rights_manifest, validate_rights_manifest
from .transcript import count_segment_review_statuses, load_transcript, validate_transcript

SCHEMA_VERSION = "v1"


class CutReviewPacketError(Exception):
    """Raised when a cut review packet cannot be built safely."""


def build_cut_review_packet(
    *,
    episode_dir: Path,
    edit_pack_path: Path,
    transcript_path: Path,
    output_dir: Path,
    rights_manifest_path: Path | None = None,
    nle_manifest_path: Path | None = None,
    render_manifest_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Write cut review JSON/HTML plus evidence JSON/HTML.

    Returns a dictionary containing the generated payloads and output paths.
    """
    base = base_dir or Path.cwd()
    edit_pack = load_edit_pack(edit_pack_path)
    transcript = load_transcript(transcript_path)
    _raise_if_issues("edit_pack", validate_edit_pack(edit_pack))
    _raise_if_issues("transcript", validate_transcript(transcript))
    if edit_pack.get("episode_id") != transcript.get("episode_id"):
        raise CutReviewPacketError(
            "episode_id mismatch: "
            f"edit_pack={edit_pack.get('episode_id')!r}, "
            f"transcript={transcript.get('episode_id')!r}"
        )

    rights_path = rights_manifest_path or episode_dir / "rights_manifest.json"
    rights, rights_issues = _load_rights(rights_path)
    nle_manifest = _load_json_optional(nle_manifest_path)
    render_manifest = _load_json_optional(render_manifest_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    packet_path = output_dir / "cut_review_packet.json"
    report_path = output_dir / "cut_review_report.html"
    evidence_path = output_dir / "evidence_summary.json"
    evidence_report_path = output_dir / "evidence_summary.html"

    packet = _packet_payload(
        episode_dir=episode_dir,
        edit_pack_path=edit_pack_path,
        transcript_path=transcript_path,
        output_dir=output_dir,
        edit_pack=edit_pack,
        transcript=transcript,
        rights=rights,
        rights_issues=rights_issues,
        nle_manifest_path=nle_manifest_path,
        nle_manifest=nle_manifest,
        render_manifest_path=render_manifest_path,
        render_manifest=render_manifest,
        base_dir=base,
    )
    evidence = _evidence_payload(
        episode_dir=episode_dir,
        edit_pack_path=edit_pack_path,
        transcript_path=transcript_path,
        rights_manifest_path=rights_path,
        nle_manifest_path=nle_manifest_path,
        render_manifest_path=render_manifest_path,
        packet_path=packet_path,
        report_path=report_path,
        evidence_path=evidence_path,
        evidence_report_path=evidence_report_path,
        edit_pack=edit_pack,
        transcript=transcript,
        rights=rights,
        rights_issues=rights_issues,
        nle_manifest=nle_manifest,
        render_manifest=render_manifest,
        base_dir=base,
    )

    _write_json(packet, packet_path)
    report_path.write_text(_packet_html(packet), encoding="utf-8")
    _write_json(evidence, evidence_path)
    evidence_report_path.write_text(_evidence_html(evidence), encoding="utf-8")
    # Rebuild once after writing so the evidence inventory reflects the files
    # that this command just generated.
    evidence = _evidence_payload(
        episode_dir=episode_dir,
        edit_pack_path=edit_pack_path,
        transcript_path=transcript_path,
        rights_manifest_path=rights_path,
        nle_manifest_path=nle_manifest_path,
        render_manifest_path=render_manifest_path,
        packet_path=packet_path,
        report_path=report_path,
        evidence_path=evidence_path,
        evidence_report_path=evidence_report_path,
        edit_pack=edit_pack,
        transcript=transcript,
        rights=rights,
        rights_issues=rights_issues,
        nle_manifest=nle_manifest,
        render_manifest=render_manifest,
        base_dir=base,
    )
    _write_json(evidence, evidence_path)
    evidence_report_path.write_text(_evidence_html(evidence), encoding="utf-8")
    return {
        "packet": packet,
        "evidence": evidence,
        "packet_path": packet_path,
        "report_path": report_path,
        "evidence_path": evidence_path,
        "evidence_report_path": evidence_report_path,
    }


def _packet_payload(
    *,
    episode_dir: Path,
    edit_pack_path: Path,
    transcript_path: Path,
    output_dir: Path,
    edit_pack: dict[str, Any],
    transcript: dict[str, Any],
    rights: dict[str, Any],
    rights_issues: list[Any],
    nle_manifest_path: Path | None,
    nle_manifest: dict[str, Any],
    render_manifest_path: Path | None,
    render_manifest: dict[str, Any],
    base_dir: Path,
) -> dict[str, Any]:
    cuts = _selected_cuts(edit_pack)
    subtitles = [s for s in edit_pack.get("subtitles") or [] if isinstance(s, dict)]
    segment_index = {
        str(s.get("id")): s
        for s in transcript.get("segments") or []
        if isinstance(s, dict) and s.get("id")
    }
    cut_entries = [
        _cut_entry(cut, subtitles=subtitles, segment_index=segment_index)
        for cut in cuts
    ]
    context_counts = _context_counts(cut_entries)
    rights_status = _rights_status(rights)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "cut_review_packet",
        "created_at": _now(),
        "episode_id": edit_pack["episode_id"],
        "input": {
            "episode_dir": _display_path(episode_dir, base_dir),
            "edit_pack": _display_path(edit_pack_path, base_dir),
            "transcript": _display_path(transcript_path, base_dir),
            "rights_manifest": _display_path(
                Path(edit_pack.get("rights_manifest_path") or episode_dir / "rights_manifest.json"),
                base_dir,
            ),
            "nle_manifest": _display_path(nle_manifest_path, base_dir)
            if nle_manifest_path
            else None,
            "render_manifest": _display_path(render_manifest_path, base_dir)
            if render_manifest_path
            else None,
        },
        "outputs": {
            "output_dir": _display_path(output_dir, base_dir),
            "cut_review_packet": _display_path(output_dir / "cut_review_packet.json", base_dir),
            "cut_review_report": _display_path(output_dir / "cut_review_report.html", base_dir),
            "evidence_summary": _display_path(output_dir / "evidence_summary.json", base_dir),
            "evidence_report": _display_path(output_dir / "evidence_summary.html", base_dir),
        },
        "summary": {
            "cut_count": len(cut_entries),
            "selected_cut_count": len(edit_pack.get("selected_cut_ids") or []),
            "context_counts": context_counts,
            "subtitle_count": len(subtitles),
            "transcript_segment_count": len(transcript.get("segments") or []),
            "transcript_engine": (transcript.get("stt") or {}).get("engine"),
            "transcript_provider": (transcript.get("stt") or {}).get("provider"),
            "transcript_review_status": (transcript.get("review") or {}).get("status"),
            "rights_status": rights_status,
            "production_candidate": False,
        },
        "review_boundary": {
            "agent_auto_accepts_final_cuts": False,
            "decision_required": "human final cut/context review",
            "diagnostic_render_only": True,
            "production_candidate": False,
            "rights_pending_blocks_public_production_use": rights_status != "passed",
            "notes": [
                "This packet organizes generated cuts for review; it does not choose final cuts.",
                "Diagnostic render evidence is not production render acceptance.",
                "rights_manifest pending is allowed for local diagnostic processing only.",
            ],
        },
        "source_refs": {
            "rights": {
                "status": rights_status,
                "schema_ok": not rights_issues,
                "schema_issues": [_issue_to_dict(issue) for issue in rights_issues],
                "production_usage_allowed": rights_status == "passed",
            },
            "transcript": _transcript_readback(transcript),
            "edit_pack": {
                "review_status": (edit_pack.get("review") or {}).get("status"),
                "selected_cut_ids": edit_pack.get("selected_cut_ids") or [],
            },
            "nle": _manifest_readback(nle_manifest_path, nle_manifest, base_dir),
            "render": _render_readback(render_manifest_path, render_manifest, base_dir),
        },
        "cuts": cut_entries,
    }


def _cut_entry(
    cut: dict[str, Any],
    *,
    subtitles: list[dict[str, Any]],
    segment_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    cut_subtitles = _subtitles_for_cut(cut, subtitles)
    start = float(cut.get("start_seconds", 0.0))
    end = float(cut.get("end_seconds", start))
    duration = max(0.0, end - start)
    notes = list((cut.get("context_check") or {}).get("notes") or [])
    context_status = (cut.get("context_check") or {}).get("status", "not_checked")
    categories = _needs_review_categories(context_status, notes)
    source_segment_ids = [str(s) for s in cut.get("source_segment_ids") or []]
    segment_texts = [
        str(segment_index[segment_id].get("text", ""))
        for segment_id in source_segment_ids
        if segment_id in segment_index
    ]
    subtitle_text = " ".join(str(s.get("text", "")) for s in cut_subtitles)
    subtitle_char_count = len(subtitle_text)
    return {
        "cut_id": cut.get("id"),
        "selected": True,
        "start_seconds": round(start, 3),
        "end_seconds": round(end, 3),
        "duration_seconds": round(duration, 3),
        "candidate_reason": cut.get("reason", ""),
        "source": cut.get("source"),
        "confidence": cut.get("confidence"),
        "context_status": context_status,
        "context_notes": notes,
        "source_segment_ids": source_segment_ids,
        "source_segment_count": len(source_segment_ids),
        "subtitle_event_count": len(cut_subtitles),
        "subtitle_density_per_second": round(len(cut_subtitles) / duration, 3)
        if duration
        else 0.0,
        "subtitle_char_count": subtitle_char_count,
        "subtitle_chars_per_second": round(subtitle_char_count / duration, 3)
        if duration
        else 0.0,
        "subtitle_preview": [str(s.get("text", "")) for s in cut_subtitles[:3]],
        "segment_text_preview": segment_texts[:3],
        "needs_review_reason_category": categories[0] if categories else "none",
        "needs_review_reason_categories": categories,
        "suggested_human_review_focus": _review_focus(context_status, categories),
        "decision_placeholder": {
            "final_decision": "undecided",
            "allowed_values": ["accept", "reject", "adjust", "needs_more_review"],
            "decided_by": None,
            "decided_at": None,
            "notes": [],
        },
    }


def _evidence_payload(
    *,
    episode_dir: Path,
    edit_pack_path: Path,
    transcript_path: Path,
    rights_manifest_path: Path,
    nle_manifest_path: Path | None,
    render_manifest_path: Path | None,
    packet_path: Path,
    report_path: Path,
    evidence_path: Path,
    evidence_report_path: Path,
    edit_pack: dict[str, Any],
    transcript: dict[str, Any],
    rights: dict[str, Any],
    rights_issues: list[Any],
    nle_manifest: dict[str, Any],
    render_manifest: dict[str, Any],
    base_dir: Path,
) -> dict[str, Any]:
    rights_status = _rights_status(rights)
    artifact_paths = _artifact_inventory(
        episode_dir=episode_dir,
        edit_pack_path=edit_pack_path,
        transcript_path=transcript_path,
        rights_manifest_path=rights_manifest_path,
        nle_manifest_path=nle_manifest_path,
        render_manifest_path=render_manifest_path,
        packet_path=packet_path,
        report_path=report_path,
        evidence_path=evidence_path,
        evidence_report_path=evidence_report_path,
        base_dir=base_dir,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "ed10_r3_evidence_summary",
        "created_at": _now(),
        "episode_id": edit_pack["episode_id"],
        "production_candidate": False,
        "manual_operation_readback": {
            "local_cli_reproducible": True,
            "browser_click_required": False,
            "oauth_or_external_credentials_required": False,
            "human_acceptance_required_after_packet": True,
            "acceptance_gates_remaining": [
                "final cut/context review",
                "rights approval",
                "production subtitle/render acceptance",
                "publishing/OAuth",
            ],
        },
        "artifact_inventory": artifact_paths,
        "metrics": {
            "transcript": _transcript_readback(transcript),
            "edit_pack": {
                "cut_candidates_count": len(edit_pack.get("cut_candidates") or []),
                "selected_cut_count": len(edit_pack.get("selected_cut_ids") or []),
                "subtitle_count": len(edit_pack.get("subtitles") or []),
                "context_counts": _context_counts(
                    [_cut_entry(c, subtitles=edit_pack.get("subtitles") or [], segment_index={})
                     for c in _selected_cuts(edit_pack)]
                ),
                "review_status": (edit_pack.get("review") or {}).get("status"),
            },
            "nle": _manifest_readback(nle_manifest_path, nle_manifest, base_dir),
            "render": _render_readback(render_manifest_path, render_manifest, base_dir),
            "rights": {
                "status": rights_status,
                "schema_ok": not rights_issues,
                "production_usage_allowed": rights_status == "passed",
            },
        },
        "reproduction_commands": _reproduction_commands(edit_pack["episode_id"]),
        "boundary_evidence": [
            "cut_review_packet production_candidate=false",
            "diagnostic render production_candidate=false when render manifest is present",
            f"rights_manifest status={rights_status}; pending is local diagnostic readback, not production approval",
            "Agent does not auto-decide final cut acceptance; decision placeholders remain undecided",
        ],
    }


def _selected_cuts(edit_pack: dict[str, Any]) -> list[dict[str, Any]]:
    cuts = [c for c in edit_pack.get("cut_candidates") or [] if isinstance(c, dict)]
    selected_ids = [str(cut_id) for cut_id in edit_pack.get("selected_cut_ids") or []]
    if not selected_ids:
        return cuts
    by_id = {str(c.get("id")): c for c in cuts if c.get("id") is not None}
    return [by_id[cut_id] for cut_id in selected_ids if cut_id in by_id]


def _subtitles_for_cut(cut: dict[str, Any], subtitles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cut_id = cut.get("id")
    matched = [s for s in subtitles if s.get("cut_id") == cut_id]
    if matched:
        return matched
    start = float(cut.get("start_seconds", 0.0))
    end = float(cut.get("end_seconds", 0.0))
    return [
        s
        for s in subtitles
        if float(s.get("start_seconds", -1.0)) >= start
        and float(s.get("end_seconds", -1.0)) <= end
    ]


def _needs_review_categories(context_status: str, notes: list[str]) -> list[str]:
    categories: list[str] = []
    text = " | ".join(notes).lower()
    if context_status == "passed":
        return ["passed_boundary_check"]
    if context_status == "not_checked":
        return ["context_not_checked"]
    if "previous segment" in text:
        categories.append("nearby_previous_context")
    if "next segment" in text:
        categories.append("nearby_following_context")
    if "cuts through segment" in text or "excludes beginning" in text or "excludes tail" in text:
        categories.append("boundary_cuts_through_segment")
    if "not contiguous" in text:
        categories.append("non_contiguous_source_segments")
    if "needs_fix" in text:
        categories.append("transcript_segment_needs_fix")
    if context_status == "failed" and not categories:
        categories.append("failed_context_mapping")
    if context_status == "needs_review" and not categories:
        categories.append("manual_context_review")
    return categories


def _review_focus(context_status: str, categories: list[str]) -> str:
    if context_status == "passed":
        return "Quick sanity check: boundary notes passed, but creative acceptance is still undecided."
    if "nearby_previous_context" in categories and "nearby_following_context" in categories:
        return "Check both setup before the cut and continuation after the cut before accepting."
    if "nearby_previous_context" in categories:
        return "Check whether the previous subtitle/segment is needed as setup."
    if "nearby_following_context" in categories:
        return "Check whether the following subtitle/segment is needed for payoff or continuation."
    if "boundary_cuts_through_segment" in categories:
        return "Check cut timing against the source; boundary may split transcript context."
    if "context_not_checked" in categories:
        return "Run or review context check before accepting this cut."
    return "Manual context review required before final cut acceptance."


def _context_counts(cuts: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"passed": 0, "needs_review": 0, "failed": 0, "not_checked": 0}
    for cut in cuts:
        status = str(cut.get("context_status") or "not_checked")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _transcript_readback(transcript: dict[str, Any]) -> dict[str, Any]:
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    review = transcript.get("review") if isinstance(transcript.get("review"), dict) else {}
    segments = transcript.get("segments") if isinstance(transcript.get("segments"), list) else []
    return {
        "engine": stt.get("engine"),
        "provider": stt.get("provider"),
        "model": stt.get("model"),
        "real_transcript": stt.get("real_transcript") is True,
        "segment_count": len(segments),
        "review_status": review.get("status"),
        "reviewed_by": review.get("reviewed_by"),
        "segment_review_counts": count_segment_review_statuses(segments),
        "warnings": stt.get("warnings") if isinstance(stt.get("warnings"), list) else [],
    }


def _manifest_readback(
    manifest_path: Path | None,
    manifest: dict[str, Any],
    base_dir: Path,
) -> dict[str, Any]:
    if not manifest_path:
        return {"available": False, "path": None}
    return {
        "available": manifest_path.exists(),
        "path": _display_path(manifest_path, base_dir),
        "production_edit_candidate": manifest.get("production_edit_candidate"),
        "summary": manifest.get("summary") or {},
        "warnings": manifest.get("warnings") or [],
    }


def _render_readback(
    manifest_path: Path | None,
    manifest: dict[str, Any],
    base_dir: Path,
) -> dict[str, Any]:
    if not manifest_path:
        return {"available": False, "path": None}
    metadata = manifest.get("output_metadata") if isinstance(manifest.get("output_metadata"), dict) else {}
    outputs = manifest.get("outputs") if isinstance(manifest.get("outputs"), dict) else {}
    return {
        "available": manifest_path.exists(),
        "path": _display_path(manifest_path, base_dir),
        "rendered_video": outputs.get("rendered_video"),
        "render_receipt": outputs.get("render_receipt"),
        "render_report": outputs.get("render_report"),
        "production_candidate": manifest.get("production_candidate"),
        "creative_acceptance": manifest.get("creative_acceptance"),
        "publish_acceptance": manifest.get("publish_acceptance"),
        "duration_seconds": metadata.get("duration_seconds"),
        "resolution": metadata.get("resolution"),
        "video_codec": metadata.get("video_codec"),
        "audio_codec": metadata.get("audio_codec"),
        "warnings": manifest.get("warnings") or [],
    }


def _artifact_inventory(
    *,
    episode_dir: Path,
    edit_pack_path: Path,
    transcript_path: Path,
    rights_manifest_path: Path,
    nle_manifest_path: Path | None,
    render_manifest_path: Path | None,
    packet_path: Path,
    report_path: Path,
    evidence_path: Path,
    evidence_report_path: Path,
    base_dir: Path,
) -> list[dict[str, Any]]:
    named_paths: list[tuple[str, Path | None]] = [
        ("episode_dir", episode_dir),
        ("transcript_default", transcript_path),
        ("edit_pack_default", edit_pack_path),
        ("rights_manifest", rights_manifest_path),
        ("material_ledger", episode_dir / "material_ledger.json"),
        ("source_subtitle_track", _first_existing(episode_dir / "source_subs", "*.json3")),
        ("r2_transcript_backup", _first_existing(episode_dir, "transcript.jp_pilot01r2*.json")),
        ("r2_edit_pack_backup", _first_existing(episode_dir, "edit_pack.jp_pilot01r2*.json")),
        ("r3_transcript_backup", _first_existing(episode_dir, "transcript.subtitle_track_jp_pilot01r3*.json")),
        ("r3_edit_pack_backup", _first_existing(episode_dir, "edit_pack.subtitle_track_jp_pilot01r3*.json")),
        ("nle_manifest", nle_manifest_path),
        ("nle_csv", nle_manifest_path.parent / "nle_cut_list.csv" if nle_manifest_path else None),
        ("nle_report", nle_manifest_path.parent / "nle_export_report.html" if nle_manifest_path else None),
        ("render_manifest", render_manifest_path),
        ("render_receipt", render_manifest_path.parent / "render_receipt.json" if render_manifest_path else None),
        ("render_report", render_manifest_path.parent / "render_report.html" if render_manifest_path else None),
        ("rendered_video", render_manifest_path.parent / "rendered_video.mp4" if render_manifest_path else None),
        ("cut_review_packet", packet_path),
        ("cut_review_report", report_path),
        ("evidence_summary", evidence_path),
        ("evidence_report", evidence_report_path),
    ]
    return [_artifact(name, path, base_dir) for name, path in named_paths]


def _reproduction_commands(episode_id: str) -> list[str]:
    episode = f"episodes/{episode_id}"
    return [
        "python -m src.cli.main import-subtitle-track "
        f"--base-transcript {episode}/transcript.jp_pilot01r2_20260526.json "
        f"--subtitle-track {episode}/source_subs/7J5aS_pcBj4.ja.json3 "
        f"--output {episode}/transcript.json --reviewed-by codex:jp-pilot01r3 "
        "--force --format json",
        "python -m src.cli.main generate-cuts "
        f"--transcript {episode}/transcript.json --edit-pack {episode}/edit_pack.json "
        "--target-duration-seconds 18 --min-duration-seconds 4 --max-duration-seconds 28 "
        "--gap-threshold-seconds 2.5 --max-candidates 10 --replace-auto --select-generated --format json",
        "python -m src.cli.main check-cut-context "
        f"--transcript {episode}/transcript.json --edit-pack {episode}/edit_pack.json "
        "--selected-cuts-only --format json",
        "python -m src.cli.main generate-subtitles "
        f"--transcript {episode}/transcript.json --edit-pack {episode}/edit_pack.json "
        "--selected-cuts-only --replace-auto --format json",
        "python -m src.cli.main export-nle "
        f"--edit-pack {episode}/edit_pack.json --transcript {episode}/transcript.json "
        f"--output-dir {episode}/exports/jp_pilot01r3_subtitle_import --format json",
        "python -m src.cli.main render-tiny-proof "
        f"--episode-id {episode_id} --source-video-material-id src_video_jp_pilot01 "
        "--source-audio-material-id src_audio_jp_pilot01 "
        f"--edit-pack-path {episode}/edit_pack.json "
        "--output-id jp_pilot01r3_subtitle_import_diagnostic_render "
        "--duration-sec 6.84 --burn-in-subtitles diagnostic --force --format json",
    ]


def _packet_html(packet: dict[str, Any]) -> str:
    rows = "\n".join(_cut_row_html(cut) for cut in packet.get("cuts") or [])
    boundary = packet.get("review_boundary") or {}
    summary = packet.get("summary") or {}
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Cut Review Packet - {escape(str(packet.get("episode_id", "")))}</title>
  <style>
    body {{ font-family: sans-serif; line-height: 1.4; margin: 24px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; vertical-align: top; }}
    th {{ background: #f2f2f2; }}
    .warn {{ color: #7a3b00; font-weight: 600; }}
  </style>
</head>
<body>
  <h1>Cut Review Packet</h1>
  <p class="warn">Review surface only. Agent auto-accepts final cuts: {escape(str(boundary.get("agent_auto_accepts_final_cuts")).lower())}. Production candidate: {escape(str(boundary.get("production_candidate")).lower())}.</p>
  <dl>
    <dt>episode_id</dt><dd>{escape(str(packet.get("episode_id", "")))}</dd>
    <dt>cut_count</dt><dd>{escape(str(summary.get("cut_count", "")))}</dd>
    <dt>context_counts</dt><dd>{escape(json.dumps(summary.get("context_counts", {}), ensure_ascii=False))}</dd>
    <dt>rights_status</dt><dd>{escape(str(summary.get("rights_status", "")))}</dd>
    <dt>transcript</dt><dd>{escape(str(summary.get("transcript_engine", "")))} / {escape(str(summary.get("transcript_provider", "")))}</dd>
  </dl>
  <table>
    <thead>
      <tr>
        <th>cut</th><th>range</th><th>reason</th><th>context</th>
        <th>density</th><th>review focus</th><th>decision</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>
"""


def _cut_row_html(cut: dict[str, Any]) -> str:
    notes = "<br>".join(escape(str(note)) for note in cut.get("context_notes") or [])
    preview = "<br>".join(escape(str(text)) for text in cut.get("subtitle_preview") or [])
    return (
        "<tr>"
        f"<td>{escape(str(cut.get('cut_id', '')))}</td>"
        f"<td>{escape(str(cut.get('start_seconds', '')))}-{escape(str(cut.get('end_seconds', '')))}"
        f"<br>{escape(str(cut.get('duration_seconds', '')))}s</td>"
        f"<td>{escape(str(cut.get('candidate_reason', '')))}</td>"
        f"<td>{escape(str(cut.get('context_status', '')))}<br>{notes}</td>"
        f"<td>subs={escape(str(cut.get('subtitle_event_count', '')))}"
        f"<br>subs/sec={escape(str(cut.get('subtitle_density_per_second', '')))}"
        f"<br>{preview}</td>"
        f"<td>{escape(str(cut.get('needs_review_reason_category', '')))}"
        f"<br>{escape(str(cut.get('suggested_human_review_focus', '')))}</td>"
        f"<td>{escape(str((cut.get('decision_placeholder') or {}).get('final_decision', '')))}</td>"
        "</tr>"
    )


def _evidence_html(evidence: dict[str, Any]) -> str:
    inventory_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('name', '')))}</td>"
        f"<td>{escape(str(item.get('exists', False)).lower())}</td>"
        f"<td>{escape(str(item.get('path', '')))}</td>"
        f"<td>{escape(str(item.get('size_bytes', '')))}</td>"
        "</tr>"
        for item in evidence.get("artifact_inventory") or []
    )
    commands = "\n".join(
        f"<li><code>{escape(str(command))}</code></li>"
        for command in evidence.get("reproduction_commands") or []
    )
    metrics = evidence.get("metrics") or {}
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>ED-10 / R3 Evidence Summary</title></head>
<body>
  <h1>ED-10 / JP-Pilot R3 Evidence Summary</h1>
  <p>Production candidate: {escape(str(evidence.get("production_candidate", False)).lower())}. This evidence supports local review only.</p>
  <h2>Metrics</h2>
  <pre>{escape(json.dumps(metrics, ensure_ascii=False, indent=2))}</pre>
  <h2>Artifact Inventory</h2>
  <table>
    <thead><tr><th>name</th><th>exists</th><th>path</th><th>size</th></tr></thead>
    <tbody>{inventory_rows}</tbody>
  </table>
  <h2>Reproduction Commands</h2>
  <ol>{commands}</ol>
  <h2>Boundary Evidence</h2>
  <ul>{''.join(f'<li>{escape(str(item))}</li>' for item in evidence.get('boundary_evidence') or [])}</ul>
</body>
</html>
"""


def _load_rights(path: Path) -> tuple[dict[str, Any], list[Any]]:
    if not path.exists():
        return {}, []
    rights = load_rights_manifest(path)
    return rights, validate_rights_manifest(rights)


def _rights_status(rights: dict[str, Any]) -> str:
    compliance = rights.get("compliance_check") if isinstance(rights.get("compliance_check"), dict) else {}
    return str(compliance.get("status") or "missing")


def _load_json_optional(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _raise_if_issues(label: str, issues: list[Any]) -> None:
    if issues:
        raise CutReviewPacketError(
            f"{label} invalid: "
            + ", ".join(f"{getattr(issue, 'code', 'issue')}@{getattr(issue, 'field', '')}" for issue in issues)
        )


def _artifact(name: str, path: Path | None, base_dir: Path) -> dict[str, Any]:
    if path is None:
        return {"name": name, "path": None, "exists": False, "size_bytes": None}
    exists = path.exists()
    return {
        "name": name,
        "path": _display_path(path, base_dir),
        "exists": exists,
        "size_bytes": path.stat().st_size if exists and path.is_file() else None,
    }


def _first_existing(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    return next(iter(sorted(root.glob(pattern))), None)


def _issue_to_dict(issue: Any) -> dict[str, Any]:
    if hasattr(issue, "to_dict"):
        return issue.to_dict()
    return {"code": str(getattr(issue, "code", "issue")), "field": str(getattr(issue, "field", ""))}


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _display_path(path: Path | None, base: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
