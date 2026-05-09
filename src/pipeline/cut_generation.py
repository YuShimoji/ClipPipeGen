"""ED-02: generate edit_pack cut candidates from transcript segments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .edit_pack import validate_edit_pack
from .transcript import validate_transcript


class CutGenerationError(Exception):
    """Raised when transcript/edit_pack input cannot produce valid cut candidates."""


@dataclass
class CutGenerationResult:
    edit_pack: dict[str, Any]
    generated_count: int
    replaced_auto_count: int
    skipped_segments_count: int
    target_duration_seconds: float
    min_duration_seconds: float
    max_duration_seconds: float
    gap_threshold_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_count": self.generated_count,
            "replaced_auto_count": self.replaced_auto_count,
            "skipped_segments_count": self.skipped_segments_count,
            "target_duration_seconds": self.target_duration_seconds,
            "min_duration_seconds": self.min_duration_seconds,
            "max_duration_seconds": self.max_duration_seconds,
            "gap_threshold_seconds": self.gap_threshold_seconds,
            "cut_candidates_count": len(self.edit_pack.get("cut_candidates") or []),
            "selected_cuts_count": len(self.edit_pack.get("selected_cut_ids") or []),
        }


def generate_cut_candidates(
    edit_pack: dict[str, Any],
    transcript: dict[str, Any],
    *,
    target_duration_seconds: float | None = None,
    min_duration_seconds: float = 5.0,
    max_duration_seconds: float | None = None,
    gap_threshold_seconds: float = 4.0,
    max_candidates: int = 5,
    replace_auto: bool = False,
    select_generated: bool = False,
) -> CutGenerationResult:
    """Return edit_pack with auto cut candidates appended/replaced.

    The v1 heuristic forms contiguous transcript "speech islands", splits long
    islands at segment boundaries, and ranks windows by duration/keyword/text
    density. It does not fetch media, run STT, or perform ED-03 context review.
    """
    transcript_issues = validate_transcript(transcript)
    if transcript_issues:
        raise CutGenerationError(
            "transcript invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in transcript_issues)
        )
    pack_issues = validate_edit_pack(edit_pack)
    if pack_issues:
        raise CutGenerationError(
            "edit_pack invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in pack_issues)
        )
    if transcript.get("episode_id") != edit_pack.get("episode_id"):
        raise CutGenerationError(
            "episode_id mismatch: "
            f"transcript={transcript.get('episode_id')!r}, "
            f"edit_pack={edit_pack.get('episode_id')!r}"
        )

    target = _resolve_target_duration(edit_pack, target_duration_seconds)
    if target <= 0:
        raise CutGenerationError("target_duration_seconds must be positive")
    if min_duration_seconds <= 0:
        raise CutGenerationError("min_duration_seconds must be positive")
    max_duration = max_duration_seconds if max_duration_seconds is not None else target * 1.5
    if max_duration <= 0:
        raise CutGenerationError("max_duration_seconds must be positive")
    if min_duration_seconds > max_duration:
        raise CutGenerationError("min_duration_seconds must be <= max_duration_seconds")
    if gap_threshold_seconds < 0:
        raise CutGenerationError("gap_threshold_seconds must be non-negative")
    if max_candidates <= 0:
        raise CutGenerationError("max_candidates must be positive")

    existing = list(edit_pack.get("cut_candidates") or [])
    auto_existing = [c for c in existing if isinstance(c, dict) and c.get("source") == "auto"]
    if auto_existing and not replace_auto:
        raise CutGenerationError(
            "edit_pack already has auto cut candidates; use --replace-auto to refresh them"
        )
    kept = [c for c in existing if not (isinstance(c, dict) and c.get("source") == "auto")]
    segments, skipped = _eligible_segments(transcript)
    windows = _candidate_windows(
        segments,
        target_duration_seconds=target,
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration,
        gap_threshold_seconds=gap_threshold_seconds,
    )
    topic = ((edit_pack.get("editing_intent") or {}).get("topic") or "").strip()
    ranked = _rank_windows(windows, topic=topic, target_duration_seconds=target)
    selected_windows = sorted(ranked[:max_candidates], key=lambda w: w["start_seconds"])

    used_ids = {c.get("id") for c in kept if isinstance(c, dict)}
    generated: list[dict[str, Any]] = []
    for window in selected_windows:
        cut_id = _next_cut_id(used_ids)
        used_ids.add(cut_id)
        generated.append(_to_cut_candidate(cut_id, window, target, topic))

    selected_ids = [cid for cid in (edit_pack.get("selected_cut_ids") or []) if _cut_id_exists(cid, kept)]
    if select_generated:
        selected_ids.extend(c["id"] for c in generated)

    new_pack = dict(edit_pack)
    new_pack["cut_candidates"] = kept + generated
    new_pack["selected_cut_ids"] = selected_ids
    new_pack["updated_at"] = datetime.now(timezone.utc).isoformat()
    issues = validate_edit_pack(new_pack)
    if issues:
        raise CutGenerationError(
            "generated cuts would make edit_pack invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in issues)
        )

    return CutGenerationResult(
        edit_pack=new_pack,
        generated_count=len(generated),
        replaced_auto_count=len(auto_existing) if replace_auto else 0,
        skipped_segments_count=skipped,
        target_duration_seconds=target,
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration,
        gap_threshold_seconds=gap_threshold_seconds,
    )


def _resolve_target_duration(edit_pack: dict[str, Any], explicit: float | None) -> float:
    if explicit is not None:
        return float(explicit)
    intent = edit_pack.get("editing_intent") or {}
    value = intent.get("target_duration_seconds")
    if isinstance(value, (int, float)) and value > 0:
        return float(value)
    return 60.0


def _eligible_segments(transcript: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    out: list[dict[str, Any]] = []
    skipped = 0
    for segment in transcript.get("segments") or []:
        if not isinstance(segment, dict) or segment.get("review_status") == "rejected":
            skipped += 1
            continue
        text = segment.get("text")
        if not isinstance(text, str) or not text.strip():
            skipped += 1
            continue
        out.append(segment)
    out.sort(key=lambda s: (float(s["start_seconds"]), float(s["end_seconds"])))
    return out, skipped


def _candidate_windows(
    segments: list[dict[str, Any]],
    *,
    target_duration_seconds: float,
    min_duration_seconds: float,
    max_duration_seconds: float,
    gap_threshold_seconds: float,
) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    for island in _speech_islands(segments, gap_threshold_seconds):
        windows.extend(
            _split_island(
                island,
                target_duration_seconds=target_duration_seconds,
                min_duration_seconds=min_duration_seconds,
                max_duration_seconds=max_duration_seconds,
            )
        )
    return windows


def _speech_islands(
    segments: list[dict[str, Any]], gap_threshold_seconds: float
) -> list[list[dict[str, Any]]]:
    islands: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    prev_end: float | None = None
    for segment in segments:
        start = float(segment["start_seconds"])
        if current and prev_end is not None and start - prev_end > gap_threshold_seconds:
            islands.append(current)
            current = []
        current.append(segment)
        prev_end = float(segment["end_seconds"])
    if current:
        islands.append(current)
    return islands


def _split_island(
    island: list[dict[str, Any]],
    *,
    target_duration_seconds: float,
    min_duration_seconds: float,
    max_duration_seconds: float,
) -> list[dict[str, Any]]:
    if not island:
        return []
    windows: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    for segment in island:
        if not current:
            current = [segment]
            continue
        candidate = current + [segment]
        duration = _duration(candidate)
        if duration > max_duration_seconds and _duration(current) >= min_duration_seconds:
            windows.append(_window(current))
            current = [segment]
            continue
        current = candidate
        if duration >= target_duration_seconds:
            windows.append(_window(current))
            current = []
    if current:
        if _duration(current) >= min_duration_seconds:
            windows.append(_window(current))
        elif windows:
            windows[-1] = _window(windows[-1]["segments"] + current)
        else:
            windows.append(_window(current))
    return windows


def _duration(segments: list[dict[str, Any]]) -> float:
    return float(segments[-1]["end_seconds"]) - float(segments[0]["start_seconds"])


def _window(segments: list[dict[str, Any]]) -> dict[str, Any]:
    text = "\n".join(str(s.get("text", "")).strip() for s in segments if s.get("text"))
    confidences = [
        float(s["confidence"])
        for s in segments
        if isinstance(s.get("confidence"), (int, float))
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else None
    return {
        "start_seconds": float(segments[0]["start_seconds"]),
        "end_seconds": float(segments[-1]["end_seconds"]),
        "segments": list(segments),
        "source_segment_ids": [s.get("id") for s in segments],
        "text": text,
        "text_chars": len(text.replace("\n", "")),
        "avg_confidence": avg_confidence,
    }


def _rank_windows(
    windows: list[dict[str, Any]],
    *,
    topic: str,
    target_duration_seconds: float,
) -> list[dict[str, Any]]:
    topic_terms = [t for t in topic.replace("　", " ").split(" ") if t]
    for window in windows:
        duration = window["end_seconds"] - window["start_seconds"]
        duration_score = max(0.0, 1.0 - abs(duration - target_duration_seconds) / target_duration_seconds)
        density_score = min(1.0, window["text_chars"] / max(duration, 1.0) / 8.0)
        confidence = window["avg_confidence"] if window["avg_confidence"] is not None else 0.75
        topic_score = 0.0
        if topic_terms and any(term in window["text"] for term in topic_terms):
            topic_score = 0.15
        window["score"] = min(1.0, 0.45 * duration_score + 0.35 * density_score + 0.20 * confidence + topic_score)
    return sorted(windows, key=lambda w: (-w["score"], w["start_seconds"]))


def _to_cut_candidate(
    cut_id: str,
    window: dict[str, Any],
    target_duration_seconds: float,
    topic: str,
) -> dict[str, Any]:
    duration = window["end_seconds"] - window["start_seconds"]
    topic_note = "; topic match" if topic and topic in window["text"] else ""
    reason = (
        "auto transcript window: "
        f"{window['source_segment_ids'][0]}..{window['source_segment_ids'][-1]}, "
        f"duration={duration:.1f}s, target={target_duration_seconds:.1f}s, "
        f"text_chars={window['text_chars']}{topic_note}"
    )
    return {
        "id": cut_id,
        "start_seconds": window["start_seconds"],
        "end_seconds": window["end_seconds"],
        "source": "auto",
        "reason": reason,
        "confidence": round(float(window["score"]), 3),
        "context_check": {"status": "not_checked", "notes": []},
        "source_segment_ids": window["source_segment_ids"],
    }


def _next_cut_id(used_ids: set[Any]) -> str:
    n = 1
    while True:
        candidate = f"cut_{n:03d}"
        if candidate not in used_ids:
            return candidate
        n += 1


def _cut_id_exists(cut_id: Any, cuts: list[dict[str, Any]]) -> bool:
    return any(isinstance(c, dict) and c.get("id") == cut_id for c in cuts)
