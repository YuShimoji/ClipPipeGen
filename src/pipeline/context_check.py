"""ED-03: review cut candidate boundaries against transcript context."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .edit_pack import validate_edit_pack
from .transcript import validate_transcript


class ContextCheckError(Exception):
    """Raised when transcript/edit_pack input cannot be context-checked."""


@dataclass
class ContextCheckResult:
    edit_pack: dict[str, Any]
    checked_count: int
    skipped_count: int
    passed_count: int
    needs_review_count: int
    failed_count: int
    scope: str
    boundary_tolerance_seconds: float
    adjacent_window_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_count": self.checked_count,
            "skipped_count": self.skipped_count,
            "passed_count": self.passed_count,
            "needs_review_count": self.needs_review_count,
            "failed_count": self.failed_count,
            "scope": self.scope,
            "boundary_tolerance_seconds": self.boundary_tolerance_seconds,
            "adjacent_window_seconds": self.adjacent_window_seconds,
            "cut_candidates_count": len(self.edit_pack.get("cut_candidates") or []),
        }


def check_cut_context(
    edit_pack: dict[str, Any],
    transcript: dict[str, Any],
    *,
    selected_cuts_only: bool = False,
    cut_id: str | None = None,
    boundary_tolerance_seconds: float = 0.25,
    adjacent_window_seconds: float = 1.5,
) -> ContextCheckResult:
    """Return edit_pack with cut_candidates[].context_check updated.

    ED-03 is a readback/review layer. It does not fetch media, run STT, alter
    cut timing, or approve creative quality. It only records deterministic
    notes about transcript boundary alignment and nearby omitted context.
    """
    if selected_cuts_only and cut_id:
        raise ContextCheckError("--selected-cuts-only and --cut-id are mutually exclusive")
    if boundary_tolerance_seconds < 0:
        raise ContextCheckError("boundary_tolerance_seconds must be non-negative")
    if adjacent_window_seconds < 0:
        raise ContextCheckError("adjacent_window_seconds must be non-negative")

    transcript_issues = validate_transcript(transcript)
    if transcript_issues:
        raise ContextCheckError(
            "transcript invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in transcript_issues)
        )
    pack_issues = validate_edit_pack(edit_pack)
    if pack_issues:
        raise ContextCheckError(
            "edit_pack invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in pack_issues)
        )
    if transcript.get("episode_id") != edit_pack.get("episode_id"):
        raise ContextCheckError(
            "episode_id mismatch: "
            f"transcript={transcript.get('episode_id')!r}, "
            f"edit_pack={edit_pack.get('episode_id')!r}"
        )

    cuts = edit_pack.get("cut_candidates") or []
    selected = set(edit_pack.get("selected_cut_ids") or [])
    if cut_id and not any(isinstance(c, dict) and c.get("id") == cut_id for c in cuts):
        raise ContextCheckError(f"cut_id not found: {cut_id}")

    segments = _eligible_segments(transcript)
    segment_index = {str(s.get("id")): i for i, s in enumerate(segments)}
    checked_at = datetime.now(timezone.utc).isoformat()
    scope = _scope_label(selected_cuts_only=selected_cuts_only, cut_id=cut_id)

    new_pack = deepcopy(edit_pack)
    new_cuts = new_pack.get("cut_candidates") or []
    counts = {"passed": 0, "needs_review": 0, "failed": 0}
    checked = 0
    skipped = 0

    for cut in new_cuts:
        if not isinstance(cut, dict) or not _in_scope(
            cut,
            selected=selected,
            selected_cuts_only=selected_cuts_only,
            cut_id=cut_id,
        ):
            skipped += 1
            continue
        status, notes = _evaluate_cut(
            cut,
            segments,
            segment_index,
            boundary_tolerance_seconds=boundary_tolerance_seconds,
            adjacent_window_seconds=adjacent_window_seconds,
        )
        cut["context_check"] = {
            "status": status,
            "notes": notes,
            "checked_at": checked_at,
            "source": "transcript_boundary_v1",
        }
        counts[status] += 1
        checked += 1

    new_pack["updated_at"] = checked_at
    issues = validate_edit_pack(new_pack)
    if issues:
        raise ContextCheckError(
            "context check would make edit_pack invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in issues)
        )

    return ContextCheckResult(
        edit_pack=new_pack,
        checked_count=checked,
        skipped_count=skipped,
        passed_count=counts["passed"],
        needs_review_count=counts["needs_review"],
        failed_count=counts["failed"],
        scope=scope,
        boundary_tolerance_seconds=boundary_tolerance_seconds,
        adjacent_window_seconds=adjacent_window_seconds,
    )


def _scope_label(*, selected_cuts_only: bool, cut_id: str | None) -> str:
    if cut_id:
        return f"cut_id:{cut_id}"
    if selected_cuts_only:
        return "selected"
    return "all"


def _in_scope(
    cut: dict[str, Any],
    *,
    selected: set[Any],
    selected_cuts_only: bool,
    cut_id: str | None,
) -> bool:
    if cut_id:
        return cut.get("id") == cut_id
    if selected_cuts_only:
        return cut.get("id") in selected
    return True


def _eligible_segments(transcript: dict[str, Any]) -> list[dict[str, Any]]:
    segments = [
        s
        for s in (transcript.get("segments") or [])
        if isinstance(s, dict) and s.get("review_status") != "rejected"
    ]
    return sorted(segments, key=lambda s: (float(s["start_seconds"]), float(s["end_seconds"])))


def _evaluate_cut(
    cut: dict[str, Any],
    segments: list[dict[str, Any]],
    segment_index: dict[str, int],
    *,
    boundary_tolerance_seconds: float,
    adjacent_window_seconds: float,
) -> tuple[str, list[str]]:
    failed: list[str] = []
    review: list[str] = []
    notes: list[str] = []

    start = float(cut["start_seconds"])
    end = float(cut["end_seconds"])
    covered, mapping_notes, mapping_review, mapping_failed = _covered_segments(
        cut,
        segments,
        segment_index,
        start_seconds=start,
        end_seconds=end,
        boundary_tolerance_seconds=boundary_tolerance_seconds,
    )
    notes.extend(mapping_notes)
    review.extend(mapping_review)
    failed.extend(mapping_failed)

    if not covered:
        failed.append("no transcript segment overlaps this cut range")
        return "failed", failed + notes

    first_index = segment_index[str(covered[0]["id"])]
    last_index = segment_index[str(covered[-1]["id"])]
    first = covered[0]
    last = covered[-1]

    if _cuts_through_segment(start, first, boundary_tolerance_seconds):
        failed.append(f"start boundary cuts through segment {first['id']}")
    if _cuts_through_segment(end, last, boundary_tolerance_seconds):
        failed.append(f"end boundary cuts through segment {last['id']}")

    for segment in covered:
        if segment.get("review_status") == "needs_fix":
            review.append(f"segment {segment['id']} is marked needs_fix in transcript review")

    if first_index > 0:
        previous = segments[first_index - 1]
        gap = float(first["start_seconds"]) - float(previous["end_seconds"])
        if 0 <= gap <= adjacent_window_seconds:
            speaker_note = _speaker_note(previous, first)
            review.append(
                f"previous segment {previous['id']} ends {gap:.2f}s before cut context starts"
                f"{speaker_note}"
            )

    if last_index + 1 < len(segments):
        following = segments[last_index + 1]
        gap = float(following["start_seconds"]) - float(last["end_seconds"])
        if 0 <= gap <= adjacent_window_seconds:
            speaker_note = _speaker_note(last, following)
            review.append(
                f"next segment {following['id']} starts {gap:.2f}s after cut context ends"
                f"{speaker_note}"
            )

    if failed:
        return "failed", failed + review + notes
    if review:
        return "needs_review", review + notes

    return (
        "passed",
        [
            "context check passed: "
            f"{covered[0]['id']}..{covered[-1]['id']} boundaries align with transcript segments"
        ]
        + notes,
    )


def _covered_segments(
    cut: dict[str, Any],
    segments: list[dict[str, Any]],
    segment_index: dict[str, int],
    *,
    start_seconds: float,
    end_seconds: float,
    boundary_tolerance_seconds: float,
) -> tuple[list[dict[str, Any]], list[str], list[str], list[str]]:
    notes: list[str] = []
    review: list[str] = []
    failed: list[str] = []
    ids = cut.get("source_segment_ids")
    if isinstance(ids, list) and ids:
        covered: list[dict[str, Any]] = []
        missing: list[str] = []
        for segment_id in ids:
            key = str(segment_id)
            index = segment_index.get(key)
            if index is None:
                missing.append(key)
            else:
                covered.append(segments[index])
        if missing:
            failed.append(f"source_segment_ids missing from transcript: {', '.join(missing)}")
        covered.sort(key=lambda s: segment_index[str(s["id"])])
        if covered:
            indexes = [segment_index[str(s["id"])] for s in covered]
            expected = list(range(indexes[0], indexes[-1] + 1))
            if indexes != expected:
                review.append("source_segment_ids are not contiguous in transcript order")
            first = covered[0]
            last = covered[-1]
            if start_seconds > float(first["start_seconds"]) + boundary_tolerance_seconds:
                failed.append(f"cut start excludes beginning of source segment {first['id']}")
            if end_seconds < float(last["end_seconds"]) - boundary_tolerance_seconds:
                failed.append(f"cut end excludes tail of source segment {last['id']}")
        return covered, notes, review, failed

    covered = [
        segment
        for segment in segments
        if _overlap_seconds(segment, start_seconds, end_seconds) > boundary_tolerance_seconds
    ]
    if covered:
        notes.append(
            "source_segment_ids missing; context derived from overlapping transcript segments"
        )
    return covered, notes, review, failed


def _overlap_seconds(segment: dict[str, Any], start_seconds: float, end_seconds: float) -> float:
    return max(
        0.0,
        min(float(segment["end_seconds"]), end_seconds)
        - max(float(segment["start_seconds"]), start_seconds),
    )


def _cuts_through_segment(
    boundary_seconds: float,
    segment: dict[str, Any],
    tolerance_seconds: float,
) -> bool:
    return (
        float(segment["start_seconds"]) + tolerance_seconds
        < boundary_seconds
        < float(segment["end_seconds"]) - tolerance_seconds
    )


def _speaker_note(left: dict[str, Any], right: dict[str, Any]) -> str:
    left_speaker = left.get("speaker")
    right_speaker = right.get("speaker")
    if left_speaker and left_speaker == right_speaker:
        return f" (same speaker: {left_speaker})"
    return ""
