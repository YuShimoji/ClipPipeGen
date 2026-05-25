"""transcript schema v1: STT output for the Editing lane.

ED-07 intentionally stops at local-audio input and transcript readback.
URL/VOD fetch belongs to INT-02 asset_fetch.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .validation import ValidationIssue

SCHEMA_VERSION = "v1"

VALID_SEGMENT_REVIEW_STATUSES = {"unreviewed", "accepted", "needs_fix", "rejected"}
VALID_REVIEW_STATUSES = {"draft", "needs_review", "approved", "rejected"}
SEGMENT_REVIEW_COUNT_KEYS = (
    "unreviewed_count",
    "accepted_count",
    "needs_fix_count",
    "rejected_count",
    "unknown_count",
)


class TranscriptReviewError(Exception):
    """Raised when an ED-09 review patch cannot be applied safely."""


@dataclass(frozen=True)
class TranscriptReviewResult:
    transcript: dict[str, Any]
    updated_segment_count: int
    review_status: str
    segment_review_counts: dict[str, int]
    schema_issues: list[ValidationIssue]

    def to_dict(self, *, dry_run: bool = False) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "updated_segment_count": self.updated_segment_count,
            "review_status": self.review_status,
            "segment_review_counts": self.segment_review_counts,
            "schema_ok": not self.schema_issues,
            "schema_issues": [issue.to_dict() for issue in self.schema_issues],
            "dry_run": dry_run,
        }


def load_transcript(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def save_transcript(transcript: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
        f.write("\n")


def apply_review_patch(
    transcript: dict[str, Any],
    patch: dict[str, Any],
    *,
    reviewed_by: str | None = None,
) -> TranscriptReviewResult:
    """Apply an ED-09 text/status/notes patch to transcript.json data.

    v1 patches deliberately cannot change segment timing, source audio, or STT
    provenance. They only make human review/correction state explicit.
    """
    if not isinstance(transcript, dict):
        raise TranscriptReviewError("transcript must be an object")
    if not isinstance(patch, dict):
        raise TranscriptReviewError("patch must be an object")
    if patch.get("schema_version") != SCHEMA_VERSION:
        raise TranscriptReviewError("patch.schema_version must be 'v1'")

    top_level_allowed = {"schema_version", "segments", "review"}
    extra_top_level = sorted(set(patch) - top_level_allowed)
    if extra_top_level:
        raise TranscriptReviewError(
            "unsupported patch field(s): " + ", ".join(extra_top_level)
        )

    updated = deepcopy(transcript)
    segments_by_id = _segments_by_id(updated.get("segments"))
    segment_patches = patch.get("segments", [])
    if segment_patches is None:
        segment_patches = []
    if not isinstance(segment_patches, list):
        raise TranscriptReviewError("patch.segments must be an array")

    seen_patch_ids: set[str] = set()
    for index, segment_patch in enumerate(segment_patches):
        _apply_segment_review_patch(
            segments_by_id,
            segment_patch,
            index=index,
            seen_patch_ids=seen_patch_ids,
        )

    explicit_reviewer = _resolve_reviewer(patch.get("review"), reviewed_by)
    if "review" in patch:
        _apply_top_level_review_patch(
            updated,
            patch["review"],
            reviewed_by=explicit_reviewer,
        )

    review = updated.setdefault("review", {})
    review_status = review.get("status", "draft")
    if review_status == "approved":
        if not explicit_reviewer:
            raise TranscriptReviewError(
                "review.status=approved requires --reviewed-by or review.reviewed_by"
            )
        not_final = [
            str(segment.get("id"))
            for segment in updated.get("segments") or []
            if isinstance(segment, dict)
            and segment.get("review_status") not in {"accepted", "rejected"}
        ]
        if not_final:
            raise TranscriptReviewError(
                "review.status=approved requires every segment to be accepted or "
                "rejected; remaining: "
                + ", ".join(not_final)
            )
        review["reviewed_by"] = explicit_reviewer
        review["reviewed_at"] = datetime.now(timezone.utc).isoformat()

    updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    issues = validate_transcript(updated)
    return TranscriptReviewResult(
        transcript=updated,
        updated_segment_count=len(segment_patches),
        review_status=review_status,
        segment_review_counts=count_segment_review_statuses(updated.get("segments")),
        schema_issues=issues,
    )


def build_transcript(
    episode_id: str,
    *,
    source_audio_path: str,
    language: str,
    stt_engine: str,
    segments: list[dict[str, Any]],
    material_id: str | None = None,
    stt_provider: str | None = None,
    source_audio_sha256: str | None = None,
    source_audio_duration_seconds: float | None = None,
    source_audio_sample_rate_hz: int | None = None,
    source_audio_channels: int | None = None,
    stt_engine_version: str = "unknown",
    stt_model: str | None = None,
    stt_params: dict[str, Any] | None = None,
    stt_warnings: list[str] | None = None,
    real_transcript: bool = False,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    normalized_segments = normalize_segments(segments)
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
            "provider": stt_provider or stt_engine,
            "engine_version": stt_engine_version,
            "model": stt_model,
            "params": stt_params or {},
            "started_at": now,
            "completed_at": now,
            "warnings": stt_warnings or [],
            "real_transcript": real_transcript,
            "segment_count": len(normalized_segments),
        },
        "segment_count": len(normalized_segments),
        "segments": normalized_segments,
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


def count_segment_review_statuses(segments: Any) -> dict[str, int]:
    counts = {key: 0 for key in SEGMENT_REVIEW_COUNT_KEYS}
    if not isinstance(segments, list):
        return counts
    for segment in segments:
        if not isinstance(segment, dict):
            counts["unknown_count"] += 1
            continue
        status = segment.get("review_status")
        key = f"{status}_count"
        if key in counts:
            counts[key] += 1
        else:
            counts["unknown_count"] += 1
    return counts


def _segments_by_id(segments: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(segments, list):
        raise TranscriptReviewError("transcript.segments must be an array")
    out: dict[str, dict[str, Any]] = {}
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise TranscriptReviewError(f"transcript.segments[{index}] must be an object")
        segment_id = segment.get("id")
        if not isinstance(segment_id, str) or not segment_id:
            raise TranscriptReviewError(f"transcript.segments[{index}].id is required")
        if segment_id in out:
            raise TranscriptReviewError(f"duplicate transcript segment id: {segment_id}")
        out[segment_id] = segment
    return out


def _apply_segment_review_patch(
    segments_by_id: dict[str, dict[str, Any]],
    patch: Any,
    *,
    index: int,
    seen_patch_ids: set[str],
) -> None:
    if not isinstance(patch, dict):
        raise TranscriptReviewError(f"patch.segments[{index}] must be an object")
    allowed = {"id", "text", "review_status", "notes"}
    extra = sorted(set(patch) - allowed)
    if extra:
        raise TranscriptReviewError(
            f"patch.segments[{index}] has unsupported field(s): "
            + ", ".join(extra)
        )
    segment_id = patch.get("id")
    if not isinstance(segment_id, str) or not segment_id:
        raise TranscriptReviewError(f"patch.segments[{index}].id is required")
    if segment_id in seen_patch_ids:
        raise TranscriptReviewError(f"duplicate patch segment id: {segment_id}")
    seen_patch_ids.add(segment_id)
    if segment_id not in segments_by_id:
        raise TranscriptReviewError(f"unknown segment id in patch: {segment_id}")

    target = segments_by_id[segment_id]
    if "text" in patch:
        if not isinstance(patch["text"], str) or not patch["text"].strip():
            raise TranscriptReviewError(f"patch text for {segment_id} must be non-empty")
        target["text"] = patch["text"]
    if "review_status" in patch:
        review_status = patch["review_status"]
        if review_status not in VALID_SEGMENT_REVIEW_STATUSES:
            raise TranscriptReviewError(
                f"patch review_status for {segment_id} must be one of "
                f"{sorted(VALID_SEGMENT_REVIEW_STATUSES)}"
            )
        target["review_status"] = review_status
    if "notes" in patch:
        target["notes"] = _require_string_list(
            patch["notes"],
            field=f"patch.segments[{index}].notes",
        )


def _apply_top_level_review_patch(
    transcript: dict[str, Any],
    review_patch: Any,
    *,
    reviewed_by: str | None,
) -> None:
    if not isinstance(review_patch, dict):
        raise TranscriptReviewError("patch.review must be an object")
    allowed = {"status", "reviewed_by", "notes"}
    extra = sorted(set(review_patch) - allowed)
    if extra:
        raise TranscriptReviewError(
            "patch.review has unsupported field(s): " + ", ".join(extra)
        )
    review = transcript.setdefault("review", {})
    if "status" in review_patch:
        status = review_patch["status"]
        if status not in VALID_REVIEW_STATUSES:
            raise TranscriptReviewError(
                f"patch.review.status must be one of {sorted(VALID_REVIEW_STATUSES)}"
            )
        review["status"] = status
    if "notes" in review_patch:
        review["notes"] = _require_string_list(review_patch["notes"], field="patch.review.notes")
    if reviewed_by:
        review["reviewed_by"] = reviewed_by


def _resolve_reviewer(review_patch: Any, cli_reviewed_by: str | None) -> str | None:
    if cli_reviewed_by is not None:
        stripped = cli_reviewed_by.strip()
        if not stripped:
            raise TranscriptReviewError("--reviewed-by must be a non-empty identifier")
        return stripped
    if isinstance(review_patch, dict) and "reviewed_by" in review_patch:
        value = review_patch.get("reviewed_by")
        if not isinstance(value, str) or not value.strip():
            raise TranscriptReviewError("patch.review.reviewed_by must be non-empty")
        return value.strip()
    return None


def _require_string_list(value: Any, *, field: str) -> list[str]:
    if not isinstance(value, list):
        raise TranscriptReviewError(f"{field} must be an array")
    if not all(isinstance(item, str) for item in value):
        raise TranscriptReviewError(f"{field} must contain only strings")
    return list(value)


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
