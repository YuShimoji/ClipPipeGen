"""ED-10e boundary recommendation receipt builder.

This module is conservative by default. It validates the operator-owned
boundary recommendation against the current edit_pack and writes a receipt.
Mutation requires an explicit apply mode plus an overlap policy.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from .edit_pack import load_edit_pack, save_edit_pack, validate_edit_pack

SCHEMA_VERSION = "v1"
RECEIPT_KIND = "boundary_recommendation_apply_receipt_v0"
SUPPORTED_BOUNDARY_REQUESTS = {"adjust_end"}
SUPPORTED_OVERLAP_POLICIES = {"none", "shrink_or_split_cut_004"}
TIME_TOLERANCE_SECONDS = 0.001
DOWNSTREAM_STALE_IF_APPLIED = [
    "edit_pack.cut_candidates cut_003/cut_004 range/source_segment_ids",
    "edit_pack.subtitles cut_id/source_segment linkage",
    "cut_context_check",
    "cut_review_packet",
    "cut_decision_packet",
    "chapter_revision_board",
    "operator_proxy_decision_handoff",
    "nle_export",
    "diagnostic_visual_proof",
    "render_manifest",
    "operator_review_artifacts",
]


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
    apply: bool = False,
    overlap_policy: str = "none",
    transcript_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate one boundary recommendation and write JSON/HTML receipts.

    Without an explicit overlap policy, overlap remains blocked. With
    ``overlap_policy="shrink_or_split_cut_004"``, the function can plan or apply
    the cut_003 end extension and explicit cut_004 shrink/resegmentation target.
    """
    if dry_run == apply:
        raise BoundaryRecommendationApplyError(
            "choose exactly one of dry_run=True or apply=True"
        )
    if overlap_policy not in SUPPORTED_OVERLAP_POLICIES:
        raise BoundaryRecommendationApplyError(
            f"unsupported overlap_policy {overlap_policy!r}; supported: "
            f"{sorted(SUPPORTED_OVERLAP_POLICIES)}"
        )

    edit_pack_path = Path(edit_pack_path)
    recommendation_report_path = Path(recommendation_report_path)
    output_receipt_path = Path(output_receipt_path)

    edit_pack = load_edit_pack(edit_pack_path)
    original_edit_pack = deepcopy(edit_pack)
    report = _load_json(recommendation_report_path)
    transcript = _load_json(Path(transcript_path)) if transcript_path else None
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
    overlap_resolution = None
    if conflicts and overlap_policy == "shrink_or_split_cut_004":
        overlap_resolution = _plan_shrink_or_split_cut004(
            edit_pack,
            transcript=transcript,
            target_cut=cut,
            cut_id=cut_id,
            conflicts=conflicts,
            requested_start=requested_start,
            requested_end=requested_end,
            proposed_added_segments=proposed_added_segments,
            excluded_next_segment=excluded_next_segment,
            affected_subtitles=affected_subtitles,
        )

    if conflicts and overlap_policy == "none":
        status = "blocked_overlap"
    elif apply and overlap_resolution is None:
        raise BoundaryRecommendationApplyError(
            "apply mode requires an explicit supported overlap policy for this slice"
        )
    elif apply:
        status = "applied"
    else:
        status = "dry_run"

    boundary_change_requested = (
        abs(requested_start - previous_start) > TIME_TOLERANCE_SECONDS
        or abs(requested_end - previous_end) > TIME_TOLERANCE_SECONDS
    )

    if apply and overlap_resolution is not None:
        _apply_overlap_resolution(edit_pack, overlap_resolution)
        issues = validate_edit_pack(edit_pack)
        if issues:
            detail = ", ".join(f"{issue.code}@{issue.field}" for issue in issues)
            raise BoundaryRecommendationApplyError(
                f"boundary application would make edit_pack invalid: {detail}"
            )
        save_edit_pack(edit_pack, edit_pack_path)

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": RECEIPT_KIND,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "episode_id": edit_pack.get("episode_id"),
        "episode_dir": _posix(episode_dir),
        "status": status,
        "dry_run": dry_run,
        "apply_requested": apply,
        "selected_policy": overlap_policy,
        "edit_pack_mutated": bool(apply and status == "applied"),
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
        "cut_003_range": _range_readback(
            previous_start=previous_start,
            previous_end=previous_end,
            requested_start=requested_start,
            requested_end=requested_end,
            new_start=(
                overlap_resolution["target_cut_after"]["start_seconds"]
                if overlap_resolution
                else None
            ),
            new_end=(
                overlap_resolution["target_cut_after"]["end_seconds"]
                if overlap_resolution
                else None
            ),
        ),
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
            "subtitle_reassignment_policy": (
                overlap_resolution.get("subtitle_reassignment_policy")
                if overlap_resolution
                else "blocked_until_explicit_policy"
            ),
            "planned_or_applied_changes": (
                overlap_resolution.get("subtitle_changes") if overlap_resolution else []
            ),
            "note": (
                "Proposed added/excluded segment subtitle assignments require "
                "explicit downstream regeneration or reassignment readback "
                "before any boundary application."
            ),
        },
        "cut_004_handling": (
            overlap_resolution.get("cut_004_handling") if overlap_resolution else None
        ),
        "applied_changes": (
            overlap_resolution.get("applied_changes") if apply and overlap_resolution else []
        ),
        "planned_changes": (
            overlap_resolution.get("applied_changes") if dry_run and overlap_resolution else []
        ),
        "downstream_stale_if_applied": (
            list(DOWNSTREAM_STALE_IF_APPLIED) if boundary_change_requested else []
        ),
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

    if dry_run and edit_pack != original_edit_pack:
        raise BoundaryRecommendationApplyError(
            "internal error: edit_pack changed during dry-run receipt build"
        )
    if apply and edit_pack == original_edit_pack:
        raise BoundaryRecommendationApplyError(
            "internal error: apply mode did not change edit_pack"
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


def _plan_shrink_or_split_cut004(
    edit_pack: dict[str, Any],
    *,
    transcript: dict[str, Any] | None,
    target_cut: dict[str, Any],
    cut_id: str,
    conflicts: list[dict[str, Any]],
    requested_start: float,
    requested_end: float,
    proposed_added_segments: list[str],
    excluded_next_segment: str | None,
    affected_subtitles: list[dict[str, Any]],
) -> dict[str, Any]:
    if cut_id != "cut_003":
        raise BoundaryRecommendationApplyError(
            "shrink_or_split_cut_004 only supports the scoped cut_003/cut_004 policy"
        )
    if [item["cut_id"] for item in conflicts] != ["cut_004"]:
        raise BoundaryRecommendationApplyError(
            "shrink_or_split_cut_004 requires exactly one selected overlap with cut_004"
        )
    if transcript is None:
        raise BoundaryRecommendationApplyError(
            "shrink_or_split_cut_004 requires --transcript to read segment timing"
        )
    if not excluded_next_segment:
        raise BoundaryRecommendationApplyError(
            "shrink_or_split_cut_004 requires excluded_next_segment"
        )
    if not proposed_added_segments:
        raise BoundaryRecommendationApplyError(
            "shrink_or_split_cut_004 requires proposed_added_segments"
        )

    cut004 = _find_cut(edit_pack, "cut_004")
    transcript_segments = _transcript_segment_map(transcript)
    for segment_id in [*proposed_added_segments, excluded_next_segment]:
        if segment_id not in transcript_segments:
            raise BoundaryRecommendationApplyError(
                f"transcript segment not found for policy planning: {segment_id}"
            )

    target_before = _cut_readback(target_cut)
    cut004_before = _cut_readback(cut004)
    target_after_segments = _merge_segment_ids(
        list(target_cut.get("source_segment_ids") or []),
        proposed_added_segments,
    )
    if excluded_next_segment in target_after_segments:
        raise BoundaryRecommendationApplyError(
            f"excluded_next_segment {excluded_next_segment!r} would enter cut_003"
        )

    proposed_set = set(proposed_added_segments)
    cut004_after_segments = [
        item
        for item in list(cut004.get("source_segment_ids") or [])
        if item not in proposed_set
    ]
    if excluded_next_segment not in cut004_after_segments:
        raise BoundaryRecommendationApplyError(
            f"excluded_next_segment {excluded_next_segment!r} must remain in cut_004"
        )
    cut004_new_start = _read_float(
        transcript_segments[excluded_next_segment],
        "start_seconds",
    )
    cut004_new_end = _read_float(cut004, "end_seconds")
    if cut004_new_start >= cut004_new_end:
        raise BoundaryRecommendationApplyError(
            "cut_004 shrink would make start_seconds >= end_seconds"
        )

    subtitle_changes = _plan_subtitle_changes(
        affected_subtitles,
        proposed_added_segments=proposed_added_segments,
        excluded_next_segment=excluded_next_segment,
        target_cut_id=cut_id,
        neighbor_cut_id="cut_004",
    )
    _assert_all_proposed_segments_have_subtitles(
        proposed_added_segments,
        subtitle_changes,
    )

    target_after = {
        **target_before,
        "start_seconds": requested_start,
        "end_seconds": requested_end,
        "source_segment_ids": target_after_segments,
    }
    cut004_after = {
        **cut004_before,
        "start_seconds": cut004_new_start,
        "end_seconds": cut004_new_end,
        "source_segment_ids": cut004_after_segments,
        "resegmentation_target": True,
    }
    return {
        "policy": "shrink_or_split_cut_004",
        "subtitle_reassignment_policy": (
            "assign proposed_added_segments to cut_003; keep excluded_next_segment "
            "and later cut_004 subtitles on cut_004"
        ),
        "target_cut_id": cut_id,
        "neighbor_cut_id": "cut_004",
        "target_cut_before": target_before,
        "target_cut_after": target_after,
        "cut_004_before": cut004_before,
        "cut_004_after": cut004_after,
        "cut_004_handling": {
            "policy": "shrink_or_split_cut_004",
            "previous_start_seconds": cut004_before["start_seconds"],
            "previous_end_seconds": cut004_before["end_seconds"],
            "new_start_seconds": cut004_after["start_seconds"],
            "new_end_seconds": cut004_after["end_seconds"],
            "previous_source_segment_ids": cut004_before["source_segment_ids"],
            "new_source_segment_ids": cut004_after["source_segment_ids"],
            "resegmentation_target": True,
            "note": (
                "cut_004 is explicitly shrunk to the excluded next segment start "
                "and remains a needs-adjustment/resegmentation target."
            ),
        },
        "subtitle_changes": subtitle_changes,
        "applied_changes": [
            {
                "field": "cut_candidates.cut_003.end_seconds",
                "previous": target_before["end_seconds"],
                "new": requested_end,
            },
            {
                "field": "cut_candidates.cut_003.source_segment_ids",
                "previous": target_before["source_segment_ids"],
                "new": target_after_segments,
            },
            {
                "field": "cut_candidates.cut_004.start_seconds",
                "previous": cut004_before["start_seconds"],
                "new": cut004_new_start,
            },
            {
                "field": "cut_candidates.cut_004.source_segment_ids",
                "previous": cut004_before["source_segment_ids"],
                "new": cut004_after_segments,
            },
            {
                "field": "subtitles.cut_id",
                "changes": subtitle_changes,
            },
        ],
    }


def _apply_overlap_resolution(
    edit_pack: dict[str, Any],
    resolution: dict[str, Any],
) -> None:
    target = _find_cut(edit_pack, resolution["target_cut_id"])
    neighbor = _find_cut(edit_pack, resolution["neighbor_cut_id"])
    target_after = resolution["target_cut_after"]
    cut004_after = resolution["cut_004_after"]

    target["start_seconds"] = target_after["start_seconds"]
    target["end_seconds"] = target_after["end_seconds"]
    target["source_segment_ids"] = target_after["source_segment_ids"]
    _mark_context_stale(target, resolution["policy"])

    neighbor["start_seconds"] = cut004_after["start_seconds"]
    neighbor["end_seconds"] = cut004_after["end_seconds"]
    neighbor["source_segment_ids"] = cut004_after["source_segment_ids"]
    neighbor["resegmentation_target"] = True
    _mark_context_stale(neighbor, resolution["policy"])

    changes_by_id = {
        item["subtitle_id"]: item
        for item in resolution.get("subtitle_changes") or []
        if item.get("previous_cut_id") != item.get("new_cut_id")
    }
    for subtitle in edit_pack.get("subtitles") or []:
        if not isinstance(subtitle, dict):
            continue
        change = changes_by_id.get(subtitle.get("id"))
        if change:
            subtitle["cut_id"] = change["new_cut_id"]

    edit_pack["updated_at"] = datetime.now(timezone.utc).isoformat()


def _mark_context_stale(cut: dict[str, Any], policy: str) -> None:
    context = cut.setdefault("context_check", {})
    notes = list(context.get("notes") or [])
    stale_note = (
        f"boundary changed by {policy}; rerun check-cut-context before promotion"
    )
    if stale_note not in notes:
        notes.append(stale_note)
    context["status"] = "needs_review"
    context["notes"] = notes
    context["source"] = "boundary_recommendation_apply_v1"
    context["checked_at"] = None


def _cut_readback(cut: dict[str, Any]) -> dict[str, Any]:
    return {
        "cut_id": cut.get("id"),
        "start_seconds": _read_float(cut, "start_seconds"),
        "end_seconds": _read_float(cut, "end_seconds"),
        "source_segment_ids": list(cut.get("source_segment_ids") or []),
        "context_status": (cut.get("context_check") or {}).get("status"),
        "context_notes": list((cut.get("context_check") or {}).get("notes") or []),
    }


def _transcript_segment_map(transcript: dict[str, Any]) -> dict[str, dict[str, Any]]:
    segments = transcript.get("segments")
    if not isinstance(segments, list):
        raise BoundaryRecommendationApplyError("transcript.segments must be an array")
    return {
        item["id"]: item
        for item in segments
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _merge_segment_ids(existing: list[str], added: list[str]) -> list[str]:
    merged: list[str] = []
    for item in [*existing, *added]:
        if item not in merged:
            merged.append(item)
    return merged


def _plan_subtitle_changes(
    affected_subtitles: list[dict[str, Any]],
    *,
    proposed_added_segments: list[str],
    excluded_next_segment: str,
    target_cut_id: str,
    neighbor_cut_id: str,
) -> list[dict[str, Any]]:
    proposed_set = set(proposed_added_segments)
    changes: list[dict[str, Any]] = []
    for subtitle in affected_subtitles:
        segment_ids = set(subtitle.get("source_segment_ids") or [])
        previous_cut_id = subtitle.get("current_cut_id")
        if segment_ids & proposed_set:
            new_cut_id = target_cut_id
            reason = "proposed_added_segment_moves_to_target_cut"
        elif excluded_next_segment in segment_ids:
            new_cut_id = neighbor_cut_id
            reason = "excluded_next_segment_remains_neighbor_cut"
        else:
            new_cut_id = previous_cut_id
            reason = "unmodified_affected_subtitle"
        changes.append(
            {
                "subtitle_id": subtitle.get("subtitle_id"),
                "source_segment_ids": list(subtitle.get("source_segment_ids") or []),
                "previous_cut_id": previous_cut_id,
                "new_cut_id": new_cut_id,
                "start_seconds": subtitle.get("start_seconds"),
                "end_seconds": subtitle.get("end_seconds"),
                "reason": reason,
            }
        )
    return changes


def _assert_all_proposed_segments_have_subtitles(
    proposed_added_segments: list[str],
    subtitle_changes: list[dict[str, Any]],
) -> None:
    covered: set[str] = set()
    for change in subtitle_changes:
        if change.get("new_cut_id") == "cut_003":
            covered.update(
                item
                for item in change.get("source_segment_ids") or []
                if isinstance(item, str)
            )
    missing = [item for item in proposed_added_segments if item not in covered]
    if missing:
        raise BoundaryRecommendationApplyError(
            "cannot apply policy; missing subtitle reassignment readback for "
            + ", ".join(missing)
        )


def _range_readback(
    *,
    previous_start: float,
    previous_end: float,
    requested_start: float,
    requested_end: float,
    new_start: float | None,
    new_end: float | None,
) -> dict[str, Any]:
    return {
        "previous_start_seconds": previous_start,
        "previous_end_seconds": previous_end,
        "requested_start_seconds": requested_start,
        "requested_end_seconds": requested_end,
        "new_start_seconds": new_start,
        "new_end_seconds": new_end,
    }


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
    subtitle_changes = (
        receipt.get("subtitle_assignment_status", {}).get("planned_or_applied_changes")
        or []
    )
    cut004 = receipt.get("cut_004_handling") or {}
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
    change_rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(str(item.get('subtitle_id', '')))}</code></td>"
        f"<td>{escape(str(item.get('previous_cut_id', '')))}</td>"
        f"<td>{escape(str(item.get('new_cut_id', '')))}</td>"
        f"<td>{escape(', '.join(item.get('source_segment_ids') or []))}</td>"
        f"<td>{escape(str(item.get('reason', '')))}</td>"
        "</tr>"
        for item in subtitle_changes
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
    <dt>selected policy</dt><dd>{escape(str(receipt.get("selected_policy", "")))}</dd>
    <dt>proposed added segments</dt><dd>{escape(", ".join(receipt.get("proposed_added_segments") or []))}</dd>
    <dt>excluded next segment</dt><dd>{escape(str(receipt.get("excluded_next_segment", "")))}</dd>
    <dt>edit_pack mutated</dt><dd>{escape(str(receipt.get("edit_pack_mutated", False)).lower())}</dd>
  </dl>
  <h2>cut_004 Handling</h2>
  <dl>
    <dt>policy</dt><dd>{escape(str(cut004.get("policy", "")))}</dd>
    <dt>previous range</dt><dd>{escape(str(cut004.get("previous_start_seconds", "")))} - {escape(str(cut004.get("previous_end_seconds", "")))}</dd>
    <dt>new range</dt><dd>{escape(str(cut004.get("new_start_seconds", "")))} - {escape(str(cut004.get("new_end_seconds", "")))}</dd>
    <dt>new source segments</dt><dd>{escape(", ".join(cut004.get("new_source_segment_ids") or []))}</dd>
    <dt>resegmentation target</dt><dd>{escape(str(cut004.get("resegmentation_target", False)).lower())}</dd>
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
  <h2>Subtitle Reassignment</h2>
  <p>{escape(str((receipt.get("subtitle_assignment_status") or {}).get("subtitle_reassignment_policy", "")))}</p>
  <table>
    <thead><tr><th>subtitle</th><th>previous cut</th><th>new cut</th><th>segments</th><th>reason</th></tr></thead>
    <tbody>{change_rows or '<tr><td colspan="5">none</td></tr>'}</tbody>
  </table>
  <h2>Warnings</h2>
  <ul>{warning_items}</ul>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")
