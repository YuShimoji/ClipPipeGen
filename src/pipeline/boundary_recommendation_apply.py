"""ED-10e boundary recommendation receipt builder.

This module intentionally starts with a conservative dry-run/blocking surface.
It validates the operator-owned boundary recommendation against the current
edit_pack and writes a receipt, but it does not mutate cut ranges.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from .edit_pack import load_edit_pack

SCHEMA_VERSION = "v1"
RECEIPT_KIND = "boundary_recommendation_apply_receipt_v0"
SUPPORTED_BOUNDARY_REQUESTS = {"adjust_end"}
TIME_TOLERANCE_SECONDS = 0.001


class BoundaryRecommendationApplyError(Exception):
    """Raised when the recommendation cannot be safely read or validated."""


def build_boundary_recommendation_receipt(
    *,
    episode_dir: str | Path,
    edit_pack_path: str | Path,
    recommendation_report_path: str | Path,
    cut_id: str,
    output_receipt_path: str | Path,
    dry_run: bool,
) -> dict[str, Any]:
    """Validate one boundary recommendation and write JSON/HTML receipts.

    ED-10e supports dry-run/readback only. If the requested range overlaps an
    already selected cut, the receipt status is ``blocked_overlap``. Otherwise
    the status is ``dry_run``. The edit_pack is never modified by this function.
    """
    if not dry_run:
        raise BoundaryRecommendationApplyError(
            "ED-10e only supports --dry-run; non-dry-run boundary application "
            "requires a later overlap/subtitle reassignment slice"
        )

    edit_pack_path = Path(edit_pack_path)
    recommendation_report_path = Path(recommendation_report_path)
    output_receipt_path = Path(output_receipt_path)

    edit_pack = load_edit_pack(edit_pack_path)
    original_edit_pack = deepcopy(edit_pack)
    report = _load_json(recommendation_report_path)
    recommendation = _read_recommendation(report, cut_id)

    cut = _find_cut(edit_pack, cut_id)
    previous_start = _read_float(recommendation, "current_start_seconds")
    previous_end = _read_float(recommendation, "current_end_seconds")
    requested_start = _read_float(recommendation, "recommended_start_seconds")
    requested_end = _read_float(recommendation, "recommended_end_seconds")
    requested_duration = _read_float(recommendation, "recommended_duration_seconds")

    _assert_close(
        _read_float(cut, "start_seconds"),
        previous_start,
        "recommendation.current_start_seconds",
    )
    _assert_close(
        _read_float(cut, "end_seconds"),
        previous_end,
        "recommendation.current_end_seconds",
    )
    if requested_start >= requested_end:
        raise BoundaryRecommendationApplyError(
            "recommended range must satisfy recommended_start_seconds < "
            "recommended_end_seconds"
        )

    selected_ids = set(edit_pack.get("selected_cut_ids") or [])
    conflicts = _detect_selected_cut_overlaps(
        edit_pack,
        cut_id=cut_id,
        requested_start=requested_start,
        requested_end=requested_end,
        selected_ids=selected_ids,
    )
    proposed_added_segments = _read_string_list(
        recommendation,
        "proposed_added_segments",
    )
    excluded_next_segment = _read_optional_string(
        recommendation,
        "excluded_next_segment",
    )
    affected_subtitles = _collect_affected_subtitles(
        edit_pack,
        proposed_added_segments=proposed_added_segments,
        excluded_next_segment=excluded_next_segment,
        target_cut_id=cut_id,
    )
    status = "blocked_overlap" if conflicts else "dry_run"
    boundary_change_requested = (
        abs(requested_start - previous_start) > TIME_TOLERANCE_SECONDS
        or abs(requested_end - previous_end) > TIME_TOLERANCE_SECONDS
    )

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": RECEIPT_KIND,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "episode_id": edit_pack.get("episode_id"),
        "episode_dir": _posix(episode_dir),
        "status": status,
        "dry_run": True,
        "edit_pack_mutated": False,
        "cut_id": cut_id,
        "source_recommendation_report": _posix(recommendation_report_path),
        "source_edit_pack": _posix(edit_pack_path),
        "source_decision_authority_ref": report.get("decision_authority_ref"),
        "boundary_request": recommendation.get("boundary_request"),
        "previous_start_seconds": previous_start,
        "previous_end_seconds": previous_end,
        "previous_duration_seconds": round(previous_end - previous_start, 3),
        "requested_start_seconds": requested_start,
        "requested_end_seconds": requested_end,
        "requested_duration_seconds": requested_duration,
        "proposed_added_segments": proposed_added_segments,
        "excluded_next_segment": excluded_next_segment,
        "conflict_detection": {
            "scope": "selected_cut_ids",
            "has_overlap": bool(conflicts),
            "conflicting_cut_ids": [item["cut_id"] for item in conflicts],
            "conflicts": conflicts,
        },
        "subtitle_assignment_status": {
            "stale_or_requires_regeneration": bool(affected_subtitles),
            "affected_subtitles": affected_subtitles,
            "note": (
                "Proposed added/excluded segment subtitle assignments require "
                "explicit downstream regeneration or reassignment readback "
                "before any boundary application."
            ),
        },
        "downstream_stale_if_applied": [
            "cut_context_check",
            "subtitle_drafts",
            "nle_export",
            "diagnostic_visual_proof",
            "render_manifest",
            "operator_review_artifacts",
        ]
        if boundary_change_requested
        else [],
        "proof_stale_or_requires_regeneration": bool(boundary_change_requested),
        "transcript_not_mutated": True,
        "official_subtitle_evidence_not_mutated": True,
        "source_media_not_mutated": True,
        "source_media_changed": False,
        "timing_implementation_changed": False,
        "typography_changed": False,
        "production_candidate": False,
        "rights_status": "pending",
        "production_usage_allowed": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "warnings": _warnings(status),
    }

    if edit_pack != original_edit_pack:
        raise BoundaryRecommendationApplyError(
            "internal error: edit_pack changed during dry-run receipt build"
        )

    html_path = output_receipt_path.with_suffix(".html")
    receipt["outputs"] = {
        "json_receipt": _posix(output_receipt_path),
        "html_receipt": _posix(html_path),
    }
    _write_json(receipt, output_receipt_path)
    _write_html(receipt, html_path)
    return receipt


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except OSError as exc:
        raise BoundaryRecommendationApplyError(f"failed to read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise BoundaryRecommendationApplyError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BoundaryRecommendationApplyError(f"{path} must contain a JSON object")
    return payload


def _read_recommendation(report: dict[str, Any], cut_id: str) -> dict[str, Any]:
    recommendation = report.get("recommendation")
    if not isinstance(recommendation, dict):
        raise BoundaryRecommendationApplyError("recommendation object is required")
    if recommendation.get("cut_id") != cut_id:
        raise BoundaryRecommendationApplyError(
            f"recommendation cut_id {recommendation.get('cut_id')!r} does not match {cut_id!r}"
        )
    boundary_request = recommendation.get("boundary_request")
    if boundary_request not in SUPPORTED_BOUNDARY_REQUESTS:
        raise BoundaryRecommendationApplyError(
            f"unsupported boundary_request {boundary_request!r}; supported: "
            f"{sorted(SUPPORTED_BOUNDARY_REQUESTS)}"
        )
    return recommendation


def _find_cut(edit_pack: dict[str, Any], cut_id: str) -> dict[str, Any]:
    for cut in edit_pack.get("cut_candidates") or []:
        if isinstance(cut, dict) and cut.get("id") == cut_id:
            return cut
    raise BoundaryRecommendationApplyError(f"cut_id not found in edit_pack: {cut_id}")


def _read_float(payload: dict[str, Any], key: str) -> float:
    value = payload.get(key)
    if not isinstance(value, (int, float)):
        raise BoundaryRecommendationApplyError(f"{key} must be a number")
    return round(float(value), 3)


def _read_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BoundaryRecommendationApplyError(f"{key} must be a string array")
    return list(value)


def _read_optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise BoundaryRecommendationApplyError(f"{key} must be a string")
    return value


def _assert_close(actual: float, expected: float, field: str) -> None:
    if abs(actual - expected) > TIME_TOLERANCE_SECONDS:
        raise BoundaryRecommendationApplyError(
            f"{field} is stale: edit_pack has {actual:.3f}, recommendation has {expected:.3f}"
        )


def _detect_selected_cut_overlaps(
    edit_pack: dict[str, Any],
    *,
    cut_id: str,
    requested_start: float,
    requested_end: float,
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for cut in edit_pack.get("cut_candidates") or []:
        if not isinstance(cut, dict):
            continue
        other_id = str(cut.get("id") or "")
        if other_id == cut_id:
            continue
        if selected_ids and other_id not in selected_ids:
            continue
        other_start = _read_float(cut, "start_seconds")
        other_end = _read_float(cut, "end_seconds")
        overlap_start = max(requested_start, other_start)
        overlap_end = min(requested_end, other_end)
        if overlap_start < overlap_end:
            conflicts.append(
                {
                    "cut_id": other_id,
                    "start_seconds": other_start,
                    "end_seconds": other_end,
                    "overlap_start_seconds": round(overlap_start, 3),
                    "overlap_end_seconds": round(overlap_end, 3),
                    "overlap_duration_seconds": round(overlap_end - overlap_start, 3),
                }
            )
    return conflicts


def _collect_affected_subtitles(
    edit_pack: dict[str, Any],
    *,
    proposed_added_segments: list[str],
    excluded_next_segment: str | None,
    target_cut_id: str,
) -> list[dict[str, Any]]:
    proposed_set = set(proposed_added_segments)
    excluded_set = {excluded_next_segment} if excluded_next_segment else set()
    affected: list[dict[str, Any]] = []
    for subtitle in edit_pack.get("subtitles") or []:
        if not isinstance(subtitle, dict):
            continue
        segment_ids = _subtitle_segment_ids(subtitle)
        added_hits = sorted(proposed_set & segment_ids)
        excluded_hits = sorted(excluded_set & segment_ids)
        if not added_hits and not excluded_hits:
            continue
        current_cut_id = subtitle.get("cut_id")
        affected.append(
            {
                "subtitle_id": subtitle.get("id"),
                "current_cut_id": current_cut_id,
                "source_segment_ids": sorted(segment_ids),
                "matches_proposed_added_segments": added_hits,
                "matches_excluded_next_segment": excluded_hits,
                "start_seconds": _read_float(subtitle, "start_seconds"),
                "end_seconds": _read_float(subtitle, "end_seconds"),
                "text": subtitle.get("text", ""),
                "already_assigned_to_target_cut": current_cut_id == target_cut_id,
            }
        )
    return affected


def _subtitle_segment_ids(subtitle: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    single = subtitle.get("source_segment_id")
    if isinstance(single, str):
        ids.add(single)
    multiple = subtitle.get("source_segment_ids")
    if isinstance(multiple, list):
        ids.update(item for item in multiple if isinstance(item, str))
    return ids


def _warnings(status: str) -> list[str]:
    warnings = [
        "This receipt is diagnostic/operator-routing readback only.",
        "No edit_pack, transcript, official subtitle evidence, source media, typography, proof, or render artifact was mutated.",
        "This is not production subtitle design acceptance.",
        "This is not production render acceptance.",
        "This is not creative acceptance.",
        "This is not rights approval.",
        "This is not publishing or public-use permission.",
        "rights_status=pending and production_candidate=false remain in force.",
    ]
    if status == "blocked_overlap":
        warnings.append(
            "Requested cut range overlaps selected cuts; boundary application is blocked until overlap/subtitle reassignment is explicitly resolved."
        )
    return warnings


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
        f.write("\n")


def _write_html(receipt: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conflicts = receipt.get("conflict_detection", {}).get("conflicts") or []
    affected = receipt.get("subtitle_assignment_status", {}).get("affected_subtitles") or []
    conflict_rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(str(item.get('cut_id', '')))}</code></td>"
        f"<td>{escape(str(item.get('start_seconds', '')))}-{escape(str(item.get('end_seconds', '')))}</td>"
        f"<td>{escape(str(item.get('overlap_start_seconds', '')))}-{escape(str(item.get('overlap_end_seconds', '')))}</td>"
        f"<td>{escape(str(item.get('overlap_duration_seconds', '')))}s</td>"
        "</tr>"
        for item in conflicts
    )
    affected_rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(str(item.get('subtitle_id', '')))}</code></td>"
        f"<td><code>{escape(str(item.get('current_cut_id', '')))}</code></td>"
        f"<td>{escape(', '.join(item.get('source_segment_ids') or []))}</td>"
        f"<td>{escape(str(item.get('start_seconds', '')))}-{escape(str(item.get('end_seconds', '')))}</td>"
        f"<td>{escape(str(item.get('text', '')))}</td>"
        "</tr>"
        for item in affected
    )
    warning_items = "\n".join(
        f"<li>{escape(str(item))}</li>" for item in receipt.get("warnings") or []
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Boundary Recommendation Apply Receipt - {escape(str(receipt.get("cut_id", "")))}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.5; }}
    code {{ background: #f4f4f4; padding: 0.1rem 0.25rem; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem; vertical-align: top; }}
    th {{ background: #f5f5f5; text-align: left; }}
    .warn {{ color: #8a4b00; font-weight: 600; }}
  </style>
</head>
<body>
  <h1>Boundary Recommendation Apply Receipt</h1>
  <p class="warn">status={escape(str(receipt.get("status", "")))}; production_candidate=false; rights_status=pending; production_usage_allowed=false</p>
  <dl>
    <dt>cut_id</dt><dd><code>{escape(str(receipt.get("cut_id", "")))}</code></dd>
    <dt>source recommendation</dt><dd><code>{escape(str(receipt.get("source_recommendation_report", "")))}</code></dd>
    <dt>previous range</dt><dd>{escape(str(receipt.get("previous_start_seconds", "")))} - {escape(str(receipt.get("previous_end_seconds", "")))}</dd>
    <dt>requested range</dt><dd>{escape(str(receipt.get("requested_start_seconds", "")))} - {escape(str(receipt.get("requested_end_seconds", "")))}</dd>
    <dt>boundary request</dt><dd>{escape(str(receipt.get("boundary_request", "")))}</dd>
    <dt>proposed added segments</dt><dd>{escape(", ".join(receipt.get("proposed_added_segments") or []))}</dd>
    <dt>excluded next segment</dt><dd>{escape(str(receipt.get("excluded_next_segment", "")))}</dd>
    <dt>edit_pack mutated</dt><dd>{escape(str(receipt.get("edit_pack_mutated", False)).lower())}</dd>
  </dl>
  <h2>Overlap Detection</h2>
  <table>
    <thead><tr><th>cut</th><th>current range</th><th>overlap</th><th>duration</th></tr></thead>
    <tbody>{conflict_rows or '<tr><td colspan="4">none</td></tr>'}</tbody>
  </table>
  <h2>Subtitle Assignment Readback</h2>
  <table>
    <thead><tr><th>subtitle</th><th>current cut</th><th>segments</th><th>range</th><th>text</th></tr></thead>
    <tbody>{affected_rows or '<tr><td colspan="5">none</td></tr>'}</tbody>
  </table>
  <h2>Warnings</h2>
  <ul>{warning_items}</ul>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")
