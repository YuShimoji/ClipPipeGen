"""transcript schema v1: STT output for the Editing lane.

ED-07 intentionally stops at local-audio input and transcript readback.
URL/VOD fetch belongs to INT-02 asset_fetch.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .validation import ValidationIssue

SCHEMA_VERSION = "v1"

VALID_SEGMENT_REVIEW_STATUSES = {"unreviewed", "accepted", "needs_fix", "rejected"}
VALID_REVIEW_STATUSES = {"draft", "needs_review", "approved", "rejected"}


def load_transcript(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def save_transcript(transcript: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_transcript(
    episode_id: str,
    *,
    source_audio_path: str,
    language: str,
    stt_engine: str,
    segments: list[dict[str, Any]],
    material_id: str | None = None,
    source_audio_sha256: str | None = None,
    source_audio_duration_seconds: float | None = None,
    source_audio_sample_rate_hz: int | None = None,
    source_audio_channels: int | None = None,
    stt_engine_version: str = "unknown",
    stt_model: str | None = None,
    stt_params: dict[str, Any] | None = None,
    stt_warnings: list[str] | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    source_audio: dict[str, Any] = {
        "path": source_audio_path,
        "material_id": material_id,
    }
    if source_audio_sha256 is not None:
        source_audio["sha256"] = source_audio_sha256
    if source_audio_duration_seconds is not None:
        source_audio["duration_seconds"] = source_audio_duration_seconds
    if source_audio_sample_rate_hz is not None:
        source_audio["sample_rate_hz"] = source_audio_sample_rate_hz
    if source_audio_channels is not None:
        source_audio["channels"] = source_audio_channels

    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "created_at": now,
        "updated_at": now,
        "language": language,
        "source_audio": source_audio,
        "stt": {
            "engine": stt_engine,
            "engine_version": stt_engine_version,
            "model": stt_model,
            "params": stt_params or {},
            "started_at": now,
            "completed_at": now,
            "warnings": stt_warnings or [],
        },
        "segments": normalize_segments(segments),
        "review": {
            "status": "draft",
            "reviewed_by": None,
            "reviewed_at": None,
            "notes": [],
        },
    }


def normalize_segments(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for i, segment in enumerate(segments):
        if not isinstance(segment, dict):
            normalized.append(segment)
            continue
        item = dict(segment)
        item.setdefault("id", f"seg_{i + 1:06d}")
        if "start_seconds" in item:
            item["start_seconds"] = _maybe_float(item["start_seconds"])
        if "end_seconds" in item:
            item["end_seconds"] = _maybe_float(item["end_seconds"])
        item.setdefault("confidence", None)
        item.setdefault("speaker", None)
        item.setdefault("review_status", "unreviewed")
        item.setdefault("notes", [])
        normalized.append(item)
    return normalized


def validate_transcript(transcript: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if transcript.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SCHEMA_VERSION",
                field="schema_version",
                message=f"expected {SCHEMA_VERSION!r}",
            )
        )

    for required in ("episode_id", "created_at", "updated_at", "language"):
        if not transcript.get(required):
            issues.append(
                ValidationIssue(
                    code="TRANSCRIPT_FIELD_MISSING",
                    field=required,
                    message=f"{required} is required",
                )
            )

    stt = transcript.get("stt")
    issues.extend(_validate_source_audio(transcript.get("source_audio")))
    issues.extend(_validate_stt(stt))

    review = transcript.get("review")
    issues.extend(_validate_review(review))

    segments = transcript.get("segments")
    seen_ids: set[str] = set()
    if not isinstance(segments, list):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENTS_NOT_LIST",
                field="segments",
                message="segments must be array",
            )
        )
        return issues

    if not segments and not _has_empty_segments_reason(stt, review):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENTS_EMPTY_REASON_MISSING",
                field="segments",
                message="empty segments require stt.warnings or review.notes",
            )
        )

    for i, segment in enumerate(segments):
        issues.extend(_validate_segment(segment, i, seen_ids))

    return issues


def _validate_source_audio(source_audio: Any) -> list[ValidationIssue]:
    if not isinstance(source_audio, dict):
        return [
            ValidationIssue(
                code="TRANSCRIPT_SOURCE_AUDIO_MISSING",
                field="source_audio",
                message="source_audio object is required",
            )
        ]
    issues: list[ValidationIssue] = []
    if not source_audio.get("path"):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SOURCE_AUDIO_PATH_MISSING",
                field="source_audio.path",
                message="source_audio.path is required",
            )
        )
    for field in ("duration_seconds", "sample_rate_hz", "channels"):
        value = source_audio.get(field)
        if value is not None and not isinstance(value, (int, float)):
            issues.append(
                ValidationIssue(
                    code="TRANSCRIPT_SOURCE_AUDIO_NUMBER_INVALID",
                    field=f"source_audio.{field}",
                    message=f"{field} must be a number",
                )
            )
    return issues


def _validate_stt(stt: Any) -> list[ValidationIssue]:
    if not isinstance(stt, dict):
        return [
            ValidationIssue(
                code="TRANSCRIPT_STT_MISSING",
                field="stt",
                message="stt object is required",
            )
        ]
    issues: list[ValidationIssue] = []
    if not stt.get("engine"):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_STT_ENGINE_MISSING",
                field="stt.engine",
                message="stt.engine is required",
            )
        )
    if "warnings" in stt and not isinstance(stt["warnings"], list):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_STT_WARNINGS_NOT_LIST",
                field="stt.warnings",
                message="stt.warnings must be array",
            )
        )
    return issues


def _validate_segment(
    segment: Any,
    index: int,
    seen_ids: set[str],
) -> list[ValidationIssue]:
    prefix = f"segments[{index}]"
    if not isinstance(segment, dict):
        return [
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_NOT_OBJECT",
                field=prefix,
                message="segment must be object",
            )
        ]

    issues: list[ValidationIssue] = []
    segment_id = segment.get("id")
    if not segment_id:
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_ID_MISSING",
                field=f"{prefix}.id",
                message="segment id is required",
            )
        )
    elif segment_id in seen_ids:
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_ID_DUPLICATE",
                field=f"{prefix}.id",
                message=f"segment id {segment_id!r} is duplicated",
            )
        )
    else:
        seen_ids.add(segment_id)

    start = segment.get("start_seconds")
    end = segment.get("end_seconds")
    if not isinstance(start, (int, float)):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_START_INVALID",
                field=f"{prefix}.start_seconds",
                message="start_seconds must be a number",
            )
        )
    if not isinstance(end, (int, float)):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_END_INVALID",
                field=f"{prefix}.end_seconds",
                message="end_seconds must be a number",
            )
        )
    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        if start < 0 or end < 0 or start >= end:
            issues.append(
                ValidationIssue(
                    code="TRANSCRIPT_SEGMENT_TIME_RANGE_INVALID",
                    field=f"{prefix}.start_seconds",
                    message="must satisfy 0 <= start_seconds < end_seconds",
                )
            )

    text = segment.get("text")
    if not isinstance(text, str) or not text.strip():
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_TEXT_MISSING",
                field=f"{prefix}.text",
                message="segment text is required",
            )
        )

    confidence = segment.get("confidence")
    if confidence is not None and not (
        isinstance(confidence, (int, float)) and 0 <= confidence <= 1
    ):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_CONFIDENCE_INVALID",
                field=f"{prefix}.confidence",
                message="confidence must be between 0 and 1",
            )
        )

    if segment.get("review_status") not in VALID_SEGMENT_REVIEW_STATUSES:
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_REVIEW_STATUS_INVALID",
                field=f"{prefix}.review_status",
                message=f"must be one of {sorted(VALID_SEGMENT_REVIEW_STATUSES)}",
            )
        )
    if "notes" in segment and not isinstance(segment["notes"], list):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_SEGMENT_NOTES_NOT_LIST",
                field=f"{prefix}.notes",
                message="segment notes must be array",
            )
        )
    return issues


def _validate_review(review: Any) -> list[ValidationIssue]:
    if not isinstance(review, dict):
        return [
            ValidationIssue(
                code="TRANSCRIPT_REVIEW_MISSING",
                field="review",
                message="review object is required",
            )
        ]
    issues: list[ValidationIssue] = []
    status = review.get("status")
    if status not in VALID_REVIEW_STATUSES:
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_REVIEW_STATUS_INVALID",
                field="review.status",
                message=f"must be one of {sorted(VALID_REVIEW_STATUSES)}",
            )
        )
    if status == "approved":
        if not review.get("reviewed_by"):
            issues.append(
                ValidationIssue(
                    code="TRANSCRIPT_REVIEWED_BY_MISSING",
                    field="review.reviewed_by",
                    message="reviewed_by is required when review.status=approved",
                )
            )
        if not review.get("reviewed_at"):
            issues.append(
                ValidationIssue(
                    code="TRANSCRIPT_REVIEWED_AT_MISSING",
                    field="review.reviewed_at",
                    message="reviewed_at is required when review.status=approved",
                )
            )
    if "notes" in review and not isinstance(review["notes"], list):
        issues.append(
            ValidationIssue(
                code="TRANSCRIPT_REVIEW_NOTES_NOT_LIST",
                field="review.notes",
                message="review.notes must be array",
            )
        )
    return issues


def _has_empty_segments_reason(stt: Any, review: Any) -> bool:
    stt_warnings = stt.get("warnings") if isinstance(stt, dict) else None
    review_notes = review.get("notes") if isinstance(review, dict) else None
    return bool(stt_warnings) or bool(review_notes)


def _maybe_float(value: Any) -> Any:
    try:
        return float(value)
    except (TypeError, ValueError):
        return value
