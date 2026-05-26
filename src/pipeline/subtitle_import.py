"""ED-10: import subtitle track events as transcript-compatible segments."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .transcript import build_transcript, validate_transcript
from .validation import ValidationIssue

SCHEMA_VERSION = "v1"
SUPPORTED_SOURCE_FORMATS = {"youtube-json3"}
VALID_IMPORTED_SEGMENT_STATUSES = {"unreviewed", "accepted", "needs_fix"}


class SubtitleTrackImportError(Exception):
    """Raised when a subtitle track cannot be imported safely."""


@dataclass(frozen=True)
class SubtitleTrackImportResult:
    transcript: dict[str, Any]
    imported_segment_count: int
    skipped_event_count: int
    aligned_segment_count: int
    unaligned_segment_count: int
    overlapping_segment_count: int
    source_format: str
    schema_issues: list[ValidationIssue]
    warnings: list[str]

    def to_dict(self, *, dry_run: bool = False) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "source_format": self.source_format,
            "imported_segment_count": self.imported_segment_count,
            "skipped_event_count": self.skipped_event_count,
            "aligned_segment_count": self.aligned_segment_count,
            "unaligned_segment_count": self.unaligned_segment_count,
            "overlapping_segment_count": self.overlapping_segment_count,
            "review_status": (self.transcript.get("review") or {}).get("status"),
            "segment_review_counts": _segment_review_counts(self.transcript),
            "schema_ok": not self.schema_issues,
            "schema_issues": [issue.to_dict() for issue in self.schema_issues],
            "warnings": self.warnings,
            "dry_run": dry_run,
        }


def import_subtitle_track_transcript(
    *,
    base_transcript: dict[str, Any],
    subtitle_payload: dict[str, Any],
    subtitle_track_path: str | Path,
    source_format: str = "youtube-json3",
    language: str | None = None,
    provider: str = "youtube_subtitles",
    segment_review_status: str = "accepted",
    reviewed_by: str | None = None,
    min_alignment_overlap_seconds: float = 0.05,
) -> SubtitleTrackImportResult:
    """Build a transcript from subtitle track events and base transcript readback.

    The imported transcript keeps the episode/source-audio provenance from an
    existing transcript but replaces segment timing/text with subtitle events.
    It does not fetch media, call a provider, or approve production subtitles.
    """
    if source_format not in SUPPORTED_SOURCE_FORMATS:
        raise SubtitleTrackImportError(
            f"unsupported subtitle source format: {source_format}"
        )
    if segment_review_status not in VALID_IMPORTED_SEGMENT_STATUSES:
        raise SubtitleTrackImportError(
            "segment_review_status must be one of "
            + ", ".join(sorted(VALID_IMPORTED_SEGMENT_STATUSES))
        )
    if min_alignment_overlap_seconds < 0:
        raise SubtitleTrackImportError("min_alignment_overlap_seconds must be non-negative")

    base_issues = validate_transcript(base_transcript)
    if base_issues:
        raise SubtitleTrackImportError(
            "base transcript invalid: "
            + ", ".join(f"{issue.code}@{issue.field}" for issue in base_issues)
        )

    if source_format == "youtube-json3":
        parsed_segments, skipped, parse_warnings = _parse_youtube_json3(
            subtitle_payload,
            segment_review_status=segment_review_status,
        )
    else:  # pragma: no cover - guarded above.
        raise SubtitleTrackImportError(f"unsupported subtitle source format: {source_format}")

    if not parsed_segments:
        raise SubtitleTrackImportError("subtitle track did not contain importable text events")

    alignment = _annotate_alignment(
        parsed_segments,
        base_transcript.get("segments") or [],
        min_overlap_seconds=min_alignment_overlap_seconds,
    )
    overlapping_count = _annotate_overlaps(parsed_segments)
    source_audio = base_transcript.get("source_audio") or {}
    subtitle_path = str(subtitle_track_path).replace("\\", "/")
    warnings = list(parse_warnings)
    warnings.append(
        "subtitle track import is a transcript alignment aid, not subtitle design or production acceptance"
    )
    if alignment["unaligned_segment_count"]:
        warnings.append(
            f"{alignment['unaligned_segment_count']} imported subtitle segment(s) did not align "
            "to the base transcript above the overlap threshold"
        )
    if overlapping_count:
        warnings.append(
            f"{overlapping_count} imported subtitle segment(s) overlap prior subtitle timing; "
            "downstream use remains diagnostic"
        )

    transcript = build_transcript(
        str(base_transcript["episode_id"]),
        source_audio_path=str(source_audio.get("path") or ""),
        material_id=source_audio.get("material_id"),
        source_audio_sha256=source_audio.get("sha256"),
        source_audio_duration_seconds=source_audio.get("duration_seconds"),
        source_audio_sample_rate_hz=source_audio.get("sample_rate_hz"),
        source_audio_channels=source_audio.get("channels"),
        language=language or str(base_transcript.get("language") or "ja"),
        stt_engine="subtitle_track",
        stt_provider=provider,
        stt_engine_version=source_format,
        stt_model=subtitle_path,
        stt_params={
            "source_format": source_format,
            "subtitle_track_path": subtitle_path,
            "base_transcript_engine": (base_transcript.get("stt") or {}).get("engine"),
            "base_transcript_provider": (base_transcript.get("stt") or {}).get("provider"),
            "base_transcript_segment_count": len(base_transcript.get("segments") or []),
            "min_alignment_overlap_seconds": min_alignment_overlap_seconds,
        },
        stt_warnings=warnings,
        segments=parsed_segments,
        real_transcript=True,
    )
    transcript["review"] = {
        "status": "needs_review",
        "reviewed_by": reviewed_by.strip() if isinstance(reviewed_by, str) and reviewed_by.strip() else None,
        "reviewed_at": None,
        "notes": [
            "Imported from subtitle track; transcript remains needs_review.",
            "Imported subtitle timing/text is diagnostic until production subtitle acceptance.",
        ],
    }
    issues = validate_transcript(transcript)
    return SubtitleTrackImportResult(
        transcript=transcript,
        imported_segment_count=len(parsed_segments),
        skipped_event_count=skipped,
        aligned_segment_count=alignment["aligned_segment_count"],
        unaligned_segment_count=alignment["unaligned_segment_count"],
        overlapping_segment_count=overlapping_count,
        source_format=source_format,
        schema_issues=issues,
        warnings=warnings,
    )


def _parse_youtube_json3(
    payload: dict[str, Any],
    *,
    segment_review_status: str,
) -> tuple[list[dict[str, Any]], int, list[str]]:
    events = payload.get("events")
    if not isinstance(events, list):
        raise SubtitleTrackImportError("youtube-json3 payload must contain events[]")

    segments: list[dict[str, Any]] = []
    skipped = 0
    warnings: list[str] = []
    for event_index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            skipped += 1
            continue
        text = _clean_json3_text(event.get("segs"))
        if not text:
            skipped += 1
            continue
        start_ms = event.get("tStartMs")
        duration_ms = event.get("dDurationMs")
        if not isinstance(start_ms, (int, float)) or not isinstance(duration_ms, (int, float)):
            skipped += 1
            warnings.append(f"skipped subtitle event {event_index}: missing numeric timing")
            continue
        start_seconds = float(start_ms) / 1000.0
        end_seconds = start_seconds + float(duration_ms) / 1000.0
        if start_seconds < 0 or end_seconds <= start_seconds:
            skipped += 1
            warnings.append(f"skipped subtitle event {event_index}: invalid timing")
            continue
        segments.append(
            {
                "id": f"seg_{len(segments) + 1:06d}",
                "start_seconds": round(start_seconds, 6),
                "end_seconds": round(end_seconds, 6),
                "text": text,
                "confidence": None,
                "speaker": None,
                "review_status": segment_review_status,
                "notes": [f"imported from youtube-json3 subtitle event {event_index}"],
            }
        )
    return segments, skipped, warnings


def _clean_json3_text(segs: Any) -> str:
    if not isinstance(segs, list):
        return ""
    text = "".join(
        str(seg.get("utf8", ""))
        for seg in segs
        if isinstance(seg, dict) and seg.get("utf8") is not None
    )
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n+ *", " ", text)
    return text.strip()


def _annotate_alignment(
    imported_segments: list[dict[str, Any]],
    base_segments: list[Any],
    *,
    min_overlap_seconds: float,
) -> dict[str, int]:
    valid_base = [
        segment
        for segment in base_segments
        if isinstance(segment, dict)
        and isinstance(segment.get("start_seconds"), (int, float))
        and isinstance(segment.get("end_seconds"), (int, float))
        and segment.get("id")
    ]
    aligned = 0
    unaligned = 0
    for segment in imported_segments:
        best_segment: dict[str, Any] | None = None
        best_overlap = 0.0
        start = float(segment["start_seconds"])
        end = float(segment["end_seconds"])
        for base in valid_base:
            overlap = _overlap_seconds(
                start,
                end,
                float(base["start_seconds"]),
                float(base["end_seconds"]),
            )
            if overlap > best_overlap:
                best_overlap = overlap
                best_segment = base
        if best_segment is not None and best_overlap >= min_overlap_seconds:
            aligned += 1
            segment["notes"].append(
                f"aligned_base_segment_id={best_segment['id']} overlap_seconds={best_overlap:.3f}"
            )
        else:
            unaligned += 1
            segment["notes"].append(
                f"no_base_segment_overlap_above={min_overlap_seconds:.3f}s"
            )
    return {"aligned_segment_count": aligned, "unaligned_segment_count": unaligned}


def _annotate_overlaps(imported_segments: list[dict[str, Any]]) -> int:
    previous_end: float | None = None
    overlapping = 0
    for segment in imported_segments:
        start = float(segment["start_seconds"])
        end = float(segment["end_seconds"])
        if previous_end is not None and start < previous_end:
            overlapping += 1
            segment["notes"].append("overlaps_previous_imported_subtitle_segment")
        previous_end = max(previous_end if previous_end is not None else end, end)
    return overlapping


def _overlap_seconds(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))


def _segment_review_counts(transcript: dict[str, Any]) -> dict[str, int]:
    counts = {
        "unreviewed_count": 0,
        "accepted_count": 0,
        "needs_fix_count": 0,
        "rejected_count": 0,
        "unknown_count": 0,
    }
    for segment in transcript.get("segments") or []:
        status = segment.get("review_status") if isinstance(segment, dict) else None
        key = f"{status}_count"
        if key in counts:
            counts[key] += 1
        else:
            counts["unknown_count"] += 1
    return counts
