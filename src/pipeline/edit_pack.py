"""edit_pack schema v1: Editing lane artifact.

ED-01 intentionally stops at schema / skeleton / validation. Cut detection,
subtitle generation, and NLE export are later ED-* features.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .validation import ValidationIssue

SCHEMA_VERSION = "v1"

VALID_CUT_SOURCES = {"manual", "auto", "imported"}
VALID_CONTEXT_STATUSES = {"not_checked", "passed", "needs_review", "failed"}
VALID_REVIEW_STATUSES = {"draft", "needs_review", "approved", "rejected"}
VALID_SUBTITLE_SOURCES = {"manual", "auto", "imported"}


def load_edit_pack(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def save_edit_pack(pack: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_skeleton(
    episode_id: str,
    *,
    rights_manifest_path: str | None = None,
    material_ledger_path: str | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    rights_path = rights_manifest_path or f"episodes/{episode_id}/rights_manifest.json"
    ledger_path = material_ledger_path or f"episodes/{episode_id}/material_ledger.json"
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "rights_manifest_path": rights_path,
        "material_ledger_path": ledger_path,
        "created_at": now,
        "updated_at": now,
        "editing_intent": {
            "target_duration_seconds": None,
            "topic": "",
            "audience_note": "",
            "language": "ja",
        },
        "cut_candidates": [],
        "selected_cut_ids": [],
        "subtitles": [],
        "review": {
            "status": "draft",
            "reviewed_by": None,
            "reviewed_at": None,
            "notes": [],
        },
    }


def validate_edit_pack(pack: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if pack.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                code="EDIT_SCHEMA_VERSION",
                field="schema_version",
                message=f"expected {SCHEMA_VERSION!r}",
            )
        )

    for required in ("episode_id", "rights_manifest_path", "created_at", "updated_at"):
        if not pack.get(required):
            issues.append(
                ValidationIssue(
                    code="EDIT_FIELD_MISSING",
                    field=required,
                    message=f"{required} is required",
                )
            )

    intent = pack.get("editing_intent")
    if not isinstance(intent, dict):
        issues.append(
            ValidationIssue(
                code="EDIT_INTENT_MISSING",
                field="editing_intent",
                message="editing_intent object is required",
            )
        )
    elif not intent.get("language"):
        issues.append(
            ValidationIssue(
                code="EDIT_INTENT_LANGUAGE_MISSING",
                field="editing_intent.language",
                message="language is required",
            )
        )

    cuts = pack.get("cut_candidates")
    cut_ids: set[str] = set()
    if not isinstance(cuts, list):
        issues.append(
            ValidationIssue(
                code="EDIT_CUTS_NOT_LIST",
                field="cut_candidates",
                message="cut_candidates must be array",
            )
        )
        cuts = []
    for i, cut in enumerate(cuts):
        issues.extend(_validate_cut(cut, i, cut_ids))

    selected = pack.get("selected_cut_ids")
    if not isinstance(selected, list):
        issues.append(
            ValidationIssue(
                code="EDIT_SELECTED_CUT_IDS_NOT_LIST",
                field="selected_cut_ids",
                message="selected_cut_ids must be array",
            )
        )
    else:
        for i, cut_id in enumerate(selected):
            if cut_id not in cut_ids:
                issues.append(
                    ValidationIssue(
                        code="EDIT_SELECTED_CUT_ID_UNKNOWN",
                        field=f"selected_cut_ids[{i}]",
                        message=f"selected cut id {cut_id!r} is not in cut_candidates",
                    )
                )

    subtitles = pack.get("subtitles")
    subtitle_ids: set[str] = set()
    if not isinstance(subtitles, list):
        issues.append(
            ValidationIssue(
                code="EDIT_SUBTITLES_NOT_LIST",
                field="subtitles",
                message="subtitles must be array",
            )
        )
        subtitles = []
    for i, subtitle in enumerate(subtitles):
        issues.extend(_validate_subtitle(subtitle, i, subtitle_ids, cut_ids))

    issues.extend(_validate_review(pack.get("review")))
    return issues


def _validate_cut(cut: Any, index: int, seen_ids: set[str]) -> list[ValidationIssue]:
    prefix = f"cut_candidates[{index}]"
    if not isinstance(cut, dict):
        return [
            ValidationIssue(
                code="EDIT_CUT_NOT_OBJECT",
                field=prefix,
                message="cut candidate must be object",
            )
        ]

    issues: list[ValidationIssue] = []
    cut_id = cut.get("id")
    if not cut_id:
        issues.append(
            ValidationIssue(
                code="EDIT_CUT_ID_MISSING",
                field=f"{prefix}.id",
                message="cut id is required",
            )
        )
    elif cut_id in seen_ids:
        issues.append(
            ValidationIssue(
                code="EDIT_CUT_ID_DUPLICATE",
                field=f"{prefix}.id",
                message=f"cut id {cut_id!r} is duplicated",
            )
        )
    else:
        seen_ids.add(cut_id)

    issues.extend(
        _validate_time_range(
            cut,
            prefix,
            start_field="start_seconds",
            end_field="end_seconds",
            code_prefix="EDIT_CUT",
        )
    )

    if cut.get("source") not in VALID_CUT_SOURCES:
        issues.append(
            ValidationIssue(
                code="EDIT_CUT_SOURCE_INVALID",
                field=f"{prefix}.source",
                message=f"must be one of {sorted(VALID_CUT_SOURCES)}",
            )
        )

    confidence = cut.get("confidence")
    if confidence is not None and not (
        isinstance(confidence, (int, float)) and 0 <= confidence <= 1
    ):
        issues.append(
            ValidationIssue(
                code="EDIT_CUT_CONFIDENCE_INVALID",
                field=f"{prefix}.confidence",
                message="confidence must be between 0 and 1",
            )
        )

    context = cut.get("context_check")
    if not isinstance(context, dict):
        issues.append(
            ValidationIssue(
                code="EDIT_CONTEXT_CHECK_MISSING",
                field=f"{prefix}.context_check",
                message="context_check object is required",
            )
        )
    elif context.get("status") not in VALID_CONTEXT_STATUSES:
        issues.append(
            ValidationIssue(
                code="EDIT_CONTEXT_STATUS_INVALID",
                field=f"{prefix}.context_check.status",
                message=f"must be one of {sorted(VALID_CONTEXT_STATUSES)}",
            )
        )

    return issues


def _validate_subtitle(
    subtitle: Any,
    index: int,
    seen_ids: set[str],
    cut_ids: set[str],
) -> list[ValidationIssue]:
    prefix = f"subtitles[{index}]"
    if not isinstance(subtitle, dict):
        return [
            ValidationIssue(
                code="EDIT_SUBTITLE_NOT_OBJECT",
                field=prefix,
                message="subtitle must be object",
            )
        ]

    issues: list[ValidationIssue] = []
    subtitle_id = subtitle.get("id")
    if not subtitle_id:
        issues.append(
            ValidationIssue(
                code="EDIT_SUBTITLE_ID_MISSING",
                field=f"{prefix}.id",
                message="subtitle id is required",
            )
        )
    elif subtitle_id in seen_ids:
        issues.append(
            ValidationIssue(
                code="EDIT_SUBTITLE_ID_DUPLICATE",
                field=f"{prefix}.id",
                message=f"subtitle id {subtitle_id!r} is duplicated",
            )
        )
    else:
        seen_ids.add(subtitle_id)

    issues.extend(
        _validate_time_range(
            subtitle,
            prefix,
            start_field="start_seconds",
            end_field="end_seconds",
            code_prefix="EDIT_SUBTITLE",
        )
    )

    if not subtitle.get("text"):
        issues.append(
            ValidationIssue(
                code="EDIT_SUBTITLE_TEXT_MISSING",
                field=f"{prefix}.text",
                message="subtitle text is required",
            )
        )

    if subtitle.get("source") not in VALID_SUBTITLE_SOURCES:
        issues.append(
            ValidationIssue(
                code="EDIT_SUBTITLE_SOURCE_INVALID",
                field=f"{prefix}.source",
                message=f"must be one of {sorted(VALID_SUBTITLE_SOURCES)}",
            )
        )

    cut_id = subtitle.get("cut_id")
    if cut_id and cut_id not in cut_ids:
        issues.append(
            ValidationIssue(
                code="EDIT_SUBTITLE_CUT_ID_UNKNOWN",
                field=f"{prefix}.cut_id",
                message=f"subtitle cut_id {cut_id!r} is not in cut_candidates",
            )
        )

    return issues


def _validate_time_range(
    item: dict[str, Any],
    prefix: str,
    *,
    start_field: str,
    end_field: str,
    code_prefix: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    start = item.get(start_field)
    end = item.get(end_field)
    if not isinstance(start, (int, float)):
        issues.append(
            ValidationIssue(
                code=f"{code_prefix}_START_INVALID",
                field=f"{prefix}.{start_field}",
                message=f"{start_field} must be a number",
            )
        )
    if not isinstance(end, (int, float)):
        issues.append(
            ValidationIssue(
                code=f"{code_prefix}_END_INVALID",
                field=f"{prefix}.{end_field}",
                message=f"{end_field} must be a number",
            )
        )
    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        if start < 0 or end < 0 or start >= end:
            issues.append(
                ValidationIssue(
                    code=f"{code_prefix}_TIME_RANGE_INVALID",
                    field=f"{prefix}.{start_field}",
                    message=f"must satisfy 0 <= {start_field} < {end_field}",
                )
            )
    return issues


def _validate_review(review: Any) -> list[ValidationIssue]:
    if not isinstance(review, dict):
        return [
            ValidationIssue(
                code="EDIT_REVIEW_MISSING",
                field="review",
                message="review object is required",
            )
        ]
    issues: list[ValidationIssue] = []
    status = review.get("status")
    if status not in VALID_REVIEW_STATUSES:
        issues.append(
            ValidationIssue(
                code="EDIT_REVIEW_STATUS_INVALID",
                field="review.status",
                message=f"must be one of {sorted(VALID_REVIEW_STATUSES)}",
            )
        )
    if status == "approved":
        if not review.get("reviewed_by"):
            issues.append(
                ValidationIssue(
                    code="EDIT_REVIEWED_BY_MISSING",
                    field="review.reviewed_by",
                    message="reviewed_by is required when review.status=approved",
                )
            )
        if not review.get("reviewed_at"):
            issues.append(
                ValidationIssue(
                    code="EDIT_REVIEWED_AT_MISSING",
                    field="review.reviewed_at",
                    message="reviewed_at is required when review.status=approved",
                )
            )
    if "notes" in review and not isinstance(review["notes"], list):
        issues.append(
            ValidationIssue(
                code="EDIT_REVIEW_NOTES_NOT_LIST",
                field="review.notes",
                message="review.notes must be array",
            )
        )
    return issues
