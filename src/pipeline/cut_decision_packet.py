"""Final-cut decision packet generation for JP-Pilot R3.

The packet narrows R3 selected cuts into keep / reject / needs_adjustment for
the next production-adjacent slice. It is still not production acceptance,
rights approval, publishing, or a render command.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v1"
ARTIFACT_KIND = "r3_cut_decision_packet"


class CutDecisionPacketError(Exception):
    """Raised when a cut decision packet cannot be built safely."""


MANUAL_DECISIONS = {
    "cut_001": {
        "final_cut_decision": "keep",
        "decision_reason": (
            "passed context check; short rendered diagnostic baseline exists; subtitle density is manageable"
        ),
    },
    "cut_002": {
        "final_cut_decision": "keep",
        "decision_reason": "passed context check; compact setup beat; subtitle density is low",
    },
    "cut_003": {
        "final_cut_decision": "keep",
        "decision_reason": "strong candidate arc despite needs_review context flag",
        "manual_override_reason": (
            "context flag is caused by immediate following subtitle boundary; official subtitle track source, "
            "19.119s duration, and moderate subtitle density make it worth carrying to production subtitle/render "
            "acceptance as a candidate, not as production-approved"
        ),
    },
    "cut_004": {
        "final_cut_decision": "needs_adjustment",
        "decision_reason": "needs both previous and following context review before candidate promotion",
        "adjustment_recommendation": "review start/end boundary against neighboring cuts before carrying forward",
    },
    "cut_005": {
        "final_cut_decision": "needs_adjustment",
        "decision_reason": "needs both previous and following context review before candidate promotion",
        "adjustment_recommendation": "review whether setup from previous cut and payoff after end are required",
    },
    "cut_006": {
        "final_cut_decision": "needs_adjustment",
        "decision_reason": "needs both previous and following context review before candidate promotion",
        "adjustment_recommendation": "review boundary continuity and whether the beat should merge with neighbors",
    },
    "cut_007": {
        "final_cut_decision": "needs_adjustment",
        "decision_reason": "high confidence but context notes require boundary review",
        "adjustment_recommendation": "review previous setup and following continuation before deciding keep/reject",
    },
    "cut_008": {
        "final_cut_decision": "needs_adjustment",
        "decision_reason": "dense subtitle load plus retained context risk",
        "adjustment_recommendation": "split or rewrite subtitle surface before production-adjacent acceptance",
    },
    "cut_009": {
        "final_cut_decision": "reject",
        "decision_reason": "very short closing beat with low confidence; better treated as dependent payoff",
        "rejection_reason": "too short and context-dependent for this 1-3 candidate pass",
    },
}


def build_cut_decision_packet(
    *,
    episode_dir: Path,
    review_dir: Path,
    output_dir: Path | None = None,
    cut_review_packet_path: Path | None = None,
    edit_pack_path: Path | None = None,
    transcript_path: Path | None = None,
    render_manifest_path: Path | None = None,
    nle_manifest_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    base = base_dir or Path.cwd()
    output_dir = output_dir or review_dir
    cut_review_packet_path = cut_review_packet_path or review_dir / "cut_review_packet.json"
    edit_pack_path = edit_pack_path or episode_dir / "edit_pack.json"
    transcript_path = transcript_path or episode_dir / "transcript.json"
    render_manifest_path = render_manifest_path or _first_existing(
        episode_dir / "renders", "*/render_manifest.json"
    )
    nle_manifest_path = nle_manifest_path or _first_existing(
        episode_dir / "exports", "*/nle_export_manifest.json"
    )

    cut_review_packet = _load_json_required(cut_review_packet_path)
    edit_pack = _load_json_required(edit_pack_path)
    transcript = _load_json_required(transcript_path)
    render_manifest = _load_json_optional(render_manifest_path)
    nle_manifest = _load_json_optional(nle_manifest_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    packet_path = output_dir / "cut_decision_packet.json"
    report_path = output_dir / "cut_decision_report.html"

    decisions = [
        _decision_entry(
            cut,
            edit_pack=edit_pack,
            render_manifest=render_manifest,
        )
        for cut in cut_review_packet.get("cuts") or []
        if isinstance(cut, dict)
    ]
    _validate_decisions(decisions)
    summary = _summary(decisions)
    rights_status = str((cut_review_packet.get("summary") or {}).get("rights_status") or "unknown")
    packet = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "created_at": _now(),
        "episode_id": cut_review_packet.get("episode_id") or episode_dir.name,
        "decision_policy": "jp_pilot_r3_cut_decision_v0",
        "decision_scope": "candidate_for_next_acceptance_slice_only",
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": rights_status,
        "source_identity": cut_review_packet.get("source_identity") or {},
        "input": {
            "episode_dir": _display_path(episode_dir, base),
            "cut_review_packet": _display_path(cut_review_packet_path, base),
            "edit_pack": _display_path(edit_pack_path, base),
            "transcript": _display_path(transcript_path, base),
            "render_manifest": _display_path(render_manifest_path, base),
            "nle_manifest": _display_path(nle_manifest_path, base),
        },
        "outputs": {
            "cut_decision_packet": _display_path(packet_path, base),
            "cut_decision_report": _display_path(report_path, base),
        },
        "summary": summary,
        "source_readback": {
            "transcript_source": _transcript_source(transcript),
            "nle": {
                "available": bool(nle_manifest),
                "production_edit_candidate": nle_manifest.get("production_edit_candidate"),
                "summary": nle_manifest.get("summary") or {},
            },
            "diagnostic_render": _render_readback(render_manifest),
        },
        "rules": {
            "keep_max": 3,
            "needs_review_keep_requires_manual_override_reason": True,
            "classification_values": ["keep", "reject", "needs_adjustment"],
            "not_production_acceptance": True,
            "not_rights_approval": True,
        },
        "next_step": {
            "recommended": "production_subtitle_render_acceptance",
            "candidate_cut_ids": [d["cut_id"] for d in decisions if d["final_cut_decision"] == "keep"],
            "boundary": (
                "Carry keep cuts into production subtitle/render acceptance as candidates only; "
                "rights remain pending and production_candidate=false."
            ),
        },
        "decisions": decisions,
    }
    _write_json(packet, packet_path)
    report_path.write_text(_report_html(packet), encoding="utf-8")
    return {"packet": packet, "packet_path": packet_path, "report_path": report_path}


def _decision_entry(
    cut: dict[str, Any],
    *,
    edit_pack: dict[str, Any],
    render_manifest: dict[str, Any],
) -> dict[str, Any]:
    cut_id = str(cut.get("cut_id") or "")
    manual = MANUAL_DECISIONS.get(cut_id)
    if manual is None:
        raise CutDecisionPacketError(f"missing manual decision for {cut_id}")
    timing = _subtitle_timing_status(cut_id, edit_pack, render_manifest)
    decision = {
        "cut_id": cut_id,
        "final_cut_decision": manual["final_cut_decision"],
        "context_status": cut.get("context_status"),
        "context_notes": cut.get("context_notes") or [],
        "duration_seconds": cut.get("duration_seconds"),
        "subtitle_event_count": cut.get("subtitle_event_count"),
        "subtitle_density_per_second": cut.get("subtitle_density_per_second"),
        "subtitle_chars_per_second": cut.get("subtitle_chars_per_second"),
        "subtitle_timing_status": timing,
        "candidate_reason": cut.get("candidate_reason", ""),
        "decision_reason": manual["decision_reason"],
        "rejection_reason": manual.get("rejection_reason"),
        "adjustment_recommendation": manual.get("adjustment_recommendation"),
        "manual_override_reason": manual.get("manual_override_reason"),
        "production_candidate": False,
        "rights_status": "pending",
    }
    return decision


def _subtitle_timing_status(
    cut_id: str,
    edit_pack: dict[str, Any],
    render_manifest: dict[str, Any],
) -> dict[str, Any]:
    render_cut = ((render_manifest.get("timeline_mapping") or {}).get("cut_id")) if render_manifest else None
    if render_cut == cut_id:
        burn = render_manifest.get("subtitle_burn_in") or {}
        mapping = burn.get("timing_mapping") or {}
        return {
            "source": "render_manifest",
            "rendered_in_diagnostic": True,
            "status_counts": mapping.get("status_counts") or {},
            "skipped_item_count": mapping.get("skipped_item_count", 0),
            "clamped_item_count": (mapping.get("status_counts") or {}).get("clamped_to_render_window", 0),
            "overlap_count": _overlap_count(_subtitles_for_cut(cut_id, edit_pack)),
        }
    subtitles = _subtitles_for_cut(cut_id, edit_pack)
    return {
        "source": "edit_pack_subtitles",
        "rendered_in_diagnostic": False,
        "status_counts": {"not_rendered_in_current_diagnostic": len(subtitles)},
        "skipped_item_count": None,
        "clamped_item_count": None,
        "overlap_count": _overlap_count(subtitles),
    }


def _subtitles_for_cut(cut_id: str, edit_pack: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in edit_pack.get("subtitles") or []
        if isinstance(item, dict) and item.get("cut_id") == cut_id
    ]


def _overlap_count(subtitles: list[dict[str, Any]]) -> int:
    ordered = sorted(
        subtitles,
        key=lambda item: float(item.get("start_seconds", 0.0)),
    )
    count = 0
    previous_end: float | None = None
    for item in ordered:
        start = float(item.get("start_seconds", 0.0))
        end = float(item.get("end_seconds", start))
        if previous_end is not None and start < previous_end:
            count += 1
        previous_end = max(previous_end if previous_end is not None else end, end)
    return count


def _validate_decisions(decisions: list[dict[str, Any]]) -> None:
    if len(decisions) != 9:
        raise CutDecisionPacketError(f"expected 9 R3 cuts, got {len(decisions)}")
    keep = [d for d in decisions if d.get("final_cut_decision") == "keep"]
    if not (1 <= len(keep) <= 3):
        raise CutDecisionPacketError(f"keep cut count must be 1-3, got {len(keep)}")
    for decision in keep:
        if decision.get("context_status") == "needs_review" and not decision.get("manual_override_reason"):
            raise CutDecisionPacketError(
                f"{decision.get('cut_id')} keeps a needs_review cut without manual_override_reason"
            )


def _summary(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {"keep": 0, "reject": 0, "needs_adjustment": 0}
    context_counts: dict[str, int] = {}
    for decision in decisions:
        final = str(decision.get("final_cut_decision"))
        counts[final] = counts.get(final, 0) + 1
        context = str(decision.get("context_status") or "unknown")
        context_counts[context] = context_counts.get(context, 0) + 1
    return {
        "cut_count": len(decisions),
        "decision_counts": counts,
        "context_counts": context_counts,
        "keep_cut_ids": [d["cut_id"] for d in decisions if d.get("final_cut_decision") == "keep"],
        "reject_cut_ids": [d["cut_id"] for d in decisions if d.get("final_cut_decision") == "reject"],
        "needs_adjustment_cut_ids": [
            d["cut_id"] for d in decisions if d.get("final_cut_decision") == "needs_adjustment"
        ],
        "kept_needs_review_cut_ids": [
            d["cut_id"]
            for d in decisions
            if d.get("final_cut_decision") == "keep" and d.get("context_status") == "needs_review"
        ],
        "production_candidate": False,
    }


def _render_readback(render_manifest: dict[str, Any]) -> dict[str, Any]:
    if not render_manifest:
        return {"available": False}
    timeline = render_manifest.get("timeline_mapping") or {}
    burn = render_manifest.get("subtitle_burn_in") or {}
    return {
        "available": True,
        "status": render_manifest.get("status"),
        "rendered_cut_id": timeline.get("cut_id"),
        "production_candidate": render_manifest.get("production_candidate"),
        "creative_acceptance": render_manifest.get("creative_acceptance"),
        "publish_acceptance": render_manifest.get("publish_acceptance"),
        "subtitle_burn_in_status": burn.get("status"),
        "timing_status_counts": (burn.get("timing_mapping") or {}).get("status_counts") or {},
    }


def _transcript_source(transcript: dict[str, Any]) -> dict[str, Any]:
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    return {
        "engine": stt.get("engine"),
        "provider": stt.get("provider"),
        "model": stt.get("model"),
        "segment_count": len(transcript.get("segments") or []),
        "review_status": (transcript.get("review") or {}).get("status"),
    }


def _report_html(packet: dict[str, Any]) -> str:
    summary = packet.get("summary") or {}
    rows = "\n".join(_decision_row_html(item) for item in packet.get("decisions") or [])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>R3 Cut Decision Report - {escape(str(packet.get("episode_id", "")))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.45; margin: 24px; color: #202020; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; vertical-align: top; }}
    th {{ background: #f2f2f2; }}
    code {{ background: #f6f6f6; padding: 1px 3px; }}
    .warn {{ color: #7a3b00; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>JP-Pilot R3 Cut Decision Report</h1>
  <p class="warn">Candidate triage only: not production acceptance, not rights approval, not publishing acceptance. production_candidate=false; rights_status={escape(str(packet.get("rights_status", "unknown")))}.</p>
  <section>
    <h2>Decision Summary</h2>
    <dl>
      <dt>keep</dt><dd>{escape(", ".join(summary.get("keep_cut_ids") or []))}</dd>
      <dt>needs_adjustment</dt><dd>{escape(", ".join(summary.get("needs_adjustment_cut_ids") or []))}</dd>
      <dt>reject</dt><dd>{escape(", ".join(summary.get("reject_cut_ids") or []))}</dd>
      <dt>kept needs_review with override</dt><dd>{escape(", ".join(summary.get("kept_needs_review_cut_ids") or []))}</dd>
      <dt>next step</dt><dd>{escape(str((packet.get("next_step") or {}).get("recommended", "")))}</dd>
    </dl>
  </section>
  <section>
    <h2>Cut Decisions</h2>
    <table>
      <thead>
        <tr>
          <th>cut</th><th>decision</th><th>context</th><th>duration / density</th>
          <th>subtitle timing</th><th>reason</th><th>override / reject / adjust</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </section>
</body>
</html>
"""


def _decision_row_html(decision: dict[str, Any]) -> str:
    timing = decision.get("subtitle_timing_status") or {}
    detail = (
        decision.get("manual_override_reason")
        or decision.get("rejection_reason")
        or decision.get("adjustment_recommendation")
        or ""
    )
    return (
        "<tr>"
        f"<td><code>{escape(str(decision.get('cut_id', '')))}</code></td>"
        f"<td>{escape(str(decision.get('final_cut_decision', '')))}</td>"
        f"<td>{escape(str(decision.get('context_status', '')))}<br>"
        f"{escape(' | '.join(str(n) for n in decision.get('context_notes') or []))}</td>"
        f"<td>{escape(str(decision.get('duration_seconds', '')))}s<br>"
        f"events/sec={escape(str(decision.get('subtitle_density_per_second', '')))}<br>"
        f"chars/sec={escape(str(decision.get('subtitle_chars_per_second', '')))}</td>"
        f"<td>{escape(str(timing.get('source', '')))}<br>"
        f"overlap={escape(str(timing.get('overlap_count', '')))}; "
        f"skipped={escape(str(timing.get('skipped_item_count', '')))}; "
        f"clamped={escape(str(timing.get('clamped_item_count', '')))}</td>"
        f"<td>{escape(str(decision.get('decision_reason', '')))}<br>"
        f"{escape(str(decision.get('candidate_reason', '')))}</td>"
        f"<td>{escape(str(detail))}</td>"
        "</tr>"
    )


def _load_json_required(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise CutDecisionPacketError(f"missing required input: {path}")
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise CutDecisionPacketError(f"expected JSON object: {path}")
    return payload


def _load_json_optional(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _first_existing(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    return next(iter(sorted(root.glob(pattern))), None)


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
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
