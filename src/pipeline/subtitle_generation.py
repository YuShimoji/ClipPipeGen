"""ED-04: generate edit_pack subtitle drafts from transcript segments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .edit_pack import validate_edit_pack
from .text_measure import measure_subtitle
from .transcript import validate_transcript


class SubtitleGenerationError(Exception):
    """Raised when transcript/edit_pack input cannot produce valid subtitles."""


@dataclass
class SubtitleGenerationResult:
    edit_pack: dict[str, Any]
    generated_count: int
    replaced_auto_count: int
    skipped_segments_count: int
    scope: str
    subtitle_source_type: str
    source_segment_ids: list[str]
    production_subtitle_design: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_count": self.generated_count,
            "replaced_auto_count": self.replaced_auto_count,
            "skipped_segments_count": self.skipped_segments_count,
            "scope": self.scope,
            "subtitles_count": len(self.edit_pack.get("subtitles") or []),
            "subtitle_source_type": self.subtitle_source_type,
            "source_segment_ids": self.source_segment_ids,
            "production_subtitle_design": self.production_subtitle_design,
        }


def generate_subtitle_drafts(
    edit_pack: dict[str, Any],
    transcript: dict[str, Any],
    *,
    selected_cuts_only: bool = False,
    cut_id: str | None = None,
    wrap_eaw: int | None = None,
    ambiguous_width: int = 1,
    style_slot: str = "subtitle.default",
    replace_auto: bool = False,
) -> SubtitleGenerationResult:
    """Return edit_pack with auto subtitle drafts appended/replaced.

    ED-04 consumes transcript segments and ED-05 EAW wrapping. It does not run
    STT, fetch media, render video, or decide final subtitle acceptance.
    """
    transcript_issues = validate_transcript(transcript)
    if transcript_issues:
        raise SubtitleGenerationError(
            "transcript invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in transcript_issues)
        )
    pack_issues = validate_edit_pack(edit_pack)
    if pack_issues:
        raise SubtitleGenerationError(
            "edit_pack invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in pack_issues)
        )

    if transcript.get("episode_id") != edit_pack.get("episode_id"):
        raise SubtitleGenerationError(
            "episode_id mismatch: "
            f"transcript={transcript.get('episode_id')!r}, "
            f"edit_pack={edit_pack.get('episode_id')!r}"
        )
    if wrap_eaw is not None and wrap_eaw <= 0:
        raise SubtitleGenerationError("wrap_eaw must be positive")

    existing = list(edit_pack.get("subtitles") or [])
    auto_existing = [s for s in existing if isinstance(s, dict) and s.get("source") == "auto"]
    if auto_existing and not replace_auto:
        raise SubtitleGenerationError(
            "edit_pack already has auto subtitles; use --replace-auto to refresh them"
        )

    kept = [s for s in existing if not (isinstance(s, dict) and s.get("source") == "auto")]
    target_cuts = _target_cuts(edit_pack, selected_cuts_only=selected_cuts_only, cut_id=cut_id)
    scope = "all"
    if cut_id:
        scope = f"cut:{cut_id}"
    elif selected_cuts_only:
        scope = "selected_cuts"

    used_ids = {s.get("id") for s in kept if isinstance(s, dict)}
    generated: list[dict[str, Any]] = []
    skipped = 0
    subtitle_source_type = _subtitle_source_type(transcript)
    for segment in transcript.get("segments") or []:
        if not isinstance(segment, dict) or segment.get("review_status") == "rejected":
            skipped += 1
            continue
        windows = _subtitle_windows(segment, target_cuts)
        if not windows:
            skipped += 1
            continue
        segment_id = str(segment.get("id") or "")
        source_segment_ids = [segment_id] if segment_id else []
        for start, end, assigned_cut_id in windows:
            subtitle_id = _next_subtitle_id(used_ids)
            used_ids.add(subtitle_id)
            generated.append(
                {
                    "id": subtitle_id,
                    "cut_id": assigned_cut_id,
                    "start_seconds": start,
                    "end_seconds": end,
                    "text": _format_text(
                        segment.get("text", ""),
                        wrap_eaw=wrap_eaw,
                        ambiguous_width=ambiguous_width,
                    ),
                    "source": "auto",
                    "source_type": subtitle_source_type,
                    "style_slot": style_slot,
                    "source_segment_id": segment.get("id"),
                    "source_segment_ids": source_segment_ids,
                    "draft": True,
                    "diagnostic": True,
                    "not_production_subtitle_design": True,
                    "production_subtitle_design": False,
                }
            )

    new_pack = dict(edit_pack)
    new_pack["subtitles"] = kept + generated
    new_pack["updated_at"] = datetime.now(timezone.utc).isoformat()
    issues = validate_edit_pack(new_pack)
    if issues:
        raise SubtitleGenerationError(
            "generated subtitles would make edit_pack invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in issues)
        )

    return SubtitleGenerationResult(
        edit_pack=new_pack,
        generated_count=len(generated),
        replaced_auto_count=len(auto_existing) if replace_auto else 0,
        skipped_segments_count=skipped,
        scope=scope,
        subtitle_source_type=subtitle_source_type,
        source_segment_ids=[
            segment_id
            for subtitle in generated
            for segment_id in subtitle.get("source_segment_ids", [])
        ],
        production_subtitle_design=False,
    )


def _target_cuts(
    edit_pack: dict[str, Any],
    *,
    selected_cuts_only: bool,
    cut_id: str | None,
) -> list[dict[str, Any]]:
    cuts = edit_pack.get("cut_candidates") or []
    if cut_id:
        matches = [c for c in cuts if isinstance(c, dict) and c.get("id") == cut_id]
        if not matches:
            raise SubtitleGenerationError(f"cut_id not found: {cut_id}")
        return matches
    if selected_cuts_only:
        selected = set(edit_pack.get("selected_cut_ids") or [])
        if not selected:
            raise SubtitleGenerationError("--selected-cuts-only requires selected_cut_ids")
        return [c for c in cuts if isinstance(c, dict) and c.get("id") in selected]
    return []


def _subtitle_windows(
    segment: dict[str, Any],
    target_cuts: list[dict[str, Any]],
) -> list[tuple[float, float, str | None]]:
    start = float(segment["start_seconds"])
    end = float(segment["end_seconds"])
    if not target_cuts:
        return [(start, end, None)]

    best: tuple[float, float, str | None] | None = None
    best_overlap = 0.0
    for cut in target_cuts:
        cut_start = float(cut["start_seconds"])
        cut_end = float(cut["end_seconds"])
        overlap_start = max(start, cut_start)
        overlap_end = min(end, cut_end)
        overlap = overlap_end - overlap_start
        if overlap > best_overlap:
            best_overlap = overlap
            best = (overlap_start, overlap_end, cut.get("id"))
    if best is None or best_overlap <= 0:
        return []
    return [best]


def _format_text(text: str, *, wrap_eaw: int | None, ambiguous_width: int) -> str:
    stripped = text.strip()
    if wrap_eaw is None:
        return stripped
    measured = measure_subtitle(
        stripped,
        wrap_eaw=wrap_eaw,
        ambiguous_width=ambiguous_width,
    )
    return "\n".join(line.text for line in measured.lines)


def _subtitle_source_type(transcript: dict[str, Any]) -> str:
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    return "real_transcript" if stt.get("real_transcript") is True else "transcript_segments"


def _next_subtitle_id(used_ids: set[Any]) -> str:
    n = 1
    while True:
        candidate = f"sub_{n:03d}"
        if candidate not in used_ids:
            return candidate
        n += 1
