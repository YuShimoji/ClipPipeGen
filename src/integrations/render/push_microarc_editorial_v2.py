"""OUT-14 editorial reconstruction v2 for one selected stream micro-arc."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import uuid
from html import escape
from itertools import pairwise
from pathlib import Path
from typing import Any

from src.integrations.render import editorial_video_candidate as out13
from src.integrations.render import ffmpeg_tiny
from src.integrations.render import real_video_pipeline as out12
from src.integrations.render.subtitle_overlay_visual_proof import (
    ED10L_KEIFONT_CANDIDATE_ID,
    _diagnostic_ass_style_for_candidate,
    _presentation_items,
)
from src.integrations.render.subtitle_preset_selector import select_subtitle_preset

SCHEMA_VERSION = "clippipegen.out14.push_microarc_editorial.v2"
MANIFEST_SCHEMA_VERSION = "clippipegen.out14.push_microarc_editorial_manifest.v2"
PIPELINE_VERSION = "out14-push-microarc-editorial-reconstruction-v2"
READY_STATE = "OUT14_PUSH_MICROARC_EDITORIAL_V2_READY_FOR_HUMAN_REVIEW"
ARTIFACT_ID_PATTERN = re.compile(r"^clip-out14-push-microarc-editorial-v2-\d{3}$")
DEFAULT_REVIEW_PORT = 8081
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
MIN_OUTPUT_SECONDS = 180.0
MAX_OUTPUT_SECONDS = 420.0
V1_SOURCE_SPAN = (786.36, 1487.52)
KNOWN_V1_LOCI = (
    {
        "locus_id": "v1_monkey_fight_and_following_phrase",
        "source_in_seconds": 981.199,
        "source_out_seconds": 1008.72,
    },
    {
        "locus_id": "v1_animal_misrecognition_cluster",
        "source_in_seconds": 1052.08,
        "source_out_seconds": 1075.799,
    },
)
SCORE_WEIGHTS = {
    "narrative_completeness": 20,
    "punchline_payoff_clarity": 15,
    "opening_hook_comprehension": 10,
    "beat_density": 10,
    "title_to_content_congruence": 10,
    "thumbnail_articulability": 10,
    "observed_demand_corroboration": 10,
    "differentiation_editorial_whitespace": 10,
    "transcript_media_feasibility": 5,
}
V1_ARTIFACT_ID = "clip-out14-push-microarc-stream-v1-001"
V1_FINAL_VIDEO_SHA256 = (
    "1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f"
)
V1_QUARANTINE_ID = "out14-contiguous-auto-caption-unstructured-v1"
NON_SPEECH_PATTERN = re.compile(
    r"[\[【（(](?:笑い|笑|息をのむ音|いきをのむ音|音楽|拍手|BGM|歓声|ノイズ)"
    r"[\]】）)]",
    flags=re.IGNORECASE,
)


class PushMicroarcEditorialV2Error(Exception):
    """Raised when the v2 package cannot reach its review admission state."""

    def __init__(self, message: str, *, stage: str = "unknown") -> None:
        super().__init__(message)
        self.stage = stage


def validate_v1_human_decision(payload: dict[str, Any]) -> dict[str, Any]:
    events = payload.get("events") or []
    rejection_events = [
        event
        for event in events
        if isinstance(event, dict)
        and event.get("editorial_dimension", {}).get("status") == "rejected"
        and event.get("editorial_dimension", {}).get("canonical") is False
        and event.get("editorial_dimension", {}).get("default_candidate") is False
        and event.get("editorial_dimension", {}).get("release_candidate") is False
        and event.get("editorial_dimension", {}).get("unmentioned_regions")
        == "not_accepted"
    ]
    quarantine = payload.get("quarantine") or {}
    if (
        payload.get("record_mode") != "append_only_events"
        or payload.get("artifact_id") != V1_ARTIFACT_ID
        or payload.get("v1_final_video_sha256") != V1_FINAL_VIDEO_SHA256
        or not rejection_events
        or quarantine.get("quarantine_id") != V1_QUARANTINE_ID
        or quarantine.get("status") != "ACTIVE"
        or quarantine.get("cosmetic_fix_is_not_escape") is not True
    ):
        raise PushMicroarcEditorialV2Error(
            "human decision does not bind the rejected and quarantined v1 identity",
            stage="preflight",
        )
    return {
        "status": "passed",
        "rejection_event_count": len(rejection_events),
        "quarantine_id": V1_QUARANTINE_ID,
    }


def validate_candidate_selection(payload: dict[str, Any]) -> dict[str, Any]:
    streams = payload.get("stream_identities") or []
    candidates = payload.get("candidates") or []
    winner = payload.get("winner") or {}
    if len(streams) < 3:
        raise PushMicroarcEditorialV2Error(
            "candidate selection requires at least three stream identities",
            stage="selection",
        )
    if len(candidates) < 6:
        raise PushMicroarcEditorialV2Error(
            "candidate selection requires at least six episode candidates",
            stage="selection",
        )
    selected = [
        row
        for row in candidates
        if isinstance(row, dict) and row.get("candidate_id") == winner.get("candidate_id")
    ]
    if len(selected) != 1 or selected[0].get("disposition") != "selected":
        raise PushMicroarcEditorialV2Error(
            "winner must bind one selected episode card", stage="selection"
        )
    candidate = selected[0]
    if candidate.get("hard_gates") != "passed":
        raise PushMicroarcEditorialV2Error(
            "winner did not pass hard gates", stage="selection"
        )
    configured_weights = payload.get("selection_policy", {}).get("score_weights")
    if configured_weights != SCORE_WEIGHTS or sum(SCORE_WEIGHTS.values()) != 100:
        raise PushMicroarcEditorialV2Error(
            "candidate selection does not use the fixed 100-point rubric",
            stage="selection",
        )
    score = candidate.get("score") or {}
    if set(score) != {*SCORE_WEIGHTS, "total"}:
        raise PushMicroarcEditorialV2Error(
            "winner score keys do not match the fixed rubric", stage="selection"
        )
    if any(
        not isinstance(score[key], int) or not 0 <= score[key] <= maximum
        for key, maximum in SCORE_WEIGHTS.items()
    ):
        raise PushMicroarcEditorialV2Error(
            "winner score is outside the rubric bounds", stage="selection"
        )
    expected_total = sum(score[key] for key in SCORE_WEIGHTS)
    if score.get("total") != expected_total or expected_total < 70:
        raise PushMicroarcEditorialV2Error(
            "winner score is inconsistent or below 70", stage="selection"
        )
    cuts = candidate.get("planned_cuts_seconds") or []
    if len(cuts) < 3:
        raise PushMicroarcEditorialV2Error(
            "editorial reconstruction requires multiple meaningful cuts",
            stage="selection",
        )
    duration = sum(float(end) - float(start) for start, end in cuts)
    if not MIN_OUTPUT_SECONDS <= duration <= MAX_OUTPUT_SECONDS:
        raise PushMicroarcEditorialV2Error(
            "winner is outside the normal three-to-seven-minute profile",
            stage="selection",
        )
    if any(float(end) <= float(start) for start, end in cuts):
        raise PushMicroarcEditorialV2Error(
            "winner has an invalid cut range", stage="selection"
        )
    if any(
        float(current[0]) < float(previous[1])
        for previous, current in pairwise(cuts)
    ):
        raise PushMicroarcEditorialV2Error(
            "winner cut chronology is invalid", stage="selection"
        )
    overlap = sum(
        max(0.0, min(float(end), V1_SOURCE_SPAN[1]) - max(float(start), V1_SOURCE_SPAN[0]))
        for start, end in cuts
    )
    v1_duration = V1_SOURCE_SPAN[1] - V1_SOURCE_SPAN[0]
    excluded_fraction = 1.0 - overlap / v1_duration
    if excluded_fraction < 0.25:
        raise PushMicroarcEditorialV2Error(
            "current-source winner did not materially exclude the rejected v1 span",
            stage="selection",
        )
    return {
        "status": "passed",
        "stream_identity_count": len(streams),
        "episode_candidate_count": len(candidates),
        "winner_candidate_id": candidate["candidate_id"],
        "winner_score": expected_total,
        "planned_cut_count": len(cuts),
        "planned_output_duration_seconds": round(duration, 3),
        "v1_overlap_seconds": round(overlap, 3),
        "v1_excluded_fraction": round(excluded_fraction, 6),
    }


def strip_non_speech_annotations(text: str) -> str:
    value = NON_SPEECH_PATTERN.sub("", str(text or ""))
    value = re.sub(r"\s+", " ", value).strip()
    return value


VIEWER_TRANSCRIPT_REPLACEMENTS = (
    ("ちょネゴマジさん", "おかゆ"),
    ("ちょネゴマさん", "おかゆ"),
    ("ディスコード", "Discord"),
    ("デスコード", "Discord"),
    ("Disccord", "Discord"),
    ("そのお買いが", "そのおかゆが"),
    ("そのお買い", "そのおかゆ"),
    ("ネゴマジさん", "おかゆ"),
    ("ネゴマさん", "おかゆ"),
    ("スバオカ", "スバおか"),
    ("買おうかな", "変えようかな"),
    ("テストでしたチャット", "テストで使ったチャット"),
    ("勇気を見たいなな", "遊戯王みたいだな"),
    ("勇気を見たい", "遊戯王みたい"),
    ("信仰してください", "進行してください"),
    ("セータスメッセージ", "ステータスメッセージ"),
    ("見込めと", "みこめっと"),
    ("プロフール買いだから", "プロフィール変えたから"),
    ("プロフール", "プロフィール"),
    ("プロフィール買い", "プロフィール変えた"),
    ("見こっち", "みこち"),
    ("スイちゃん", "すいちゃん"),
    ("ヤくて", "ヤバくて"),
    ("レッカード", "レッドカード"),
    ("そう持ってる", "そう思ってる"),
    ("めちゃめちゃわってて", "めちゃめちゃ笑ってて"),
    ("ていうふに", "ていうふうに"),
    ("みたいなった", "みたいになった"),
    ("ここまで通知", "どこまで通知"),
    ("このアコ", "このアイコン"),
    ("固めんスバル", "蒙古タンメン スバル"),
    ("子端面スバル", "蒙古タンメン スバル"),
    ("子端面スバる", "蒙古タンメン スバル"),
    ("ステータスカイル", "ステータス変える"),
    ("二の前", "二の舞"),
)


def normalize_viewer_transcript(text: str) -> str:
    value = strip_non_speech_annotations(text)
    for before, after in VIEWER_TRANSCRIPT_REPLACEMENTS:
        value = value.replace(before, after)
    value = value.replace("蒙古タンメン スバル", "蒙古タンメンスバル")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _merge_replacement_words(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    replacements = sorted(
        (
            (re.sub(r"\s+", "", before), after)
            for before, after in VIEWER_TRANSCRIPT_REPLACEMENTS
            if re.sub(r"\s+", "", before)
        ),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    merged = []
    index = 0
    while index < len(words):
        winner: tuple[int, str] | None = None
        for before, after in replacements:
            candidate = ""
            for end_index in range(index, len(words)):
                candidate += re.sub(r"\s+", "", str(words[end_index]["text"]))
                if candidate == before:
                    winner = (end_index, after)
                    break
                if len(candidate) >= len(before) or not before.startswith(candidate):
                    break
            if winner is not None:
                break
        if winner is None:
            merged.append(words[index])
            index += 1
            continue
        end_index, replacement = winner
        merged.append(
            {
                "start": words[index]["start"],
                "end": words[end_index]["end"],
                "text": replacement,
            }
        )
        index = end_index + 1
    return merged


def _word_caption_chunks(
    segment: dict[str, Any],
    *,
    cut_start: float,
    cut_end: float,
) -> list[dict[str, Any]]:
    words = []
    for word in segment.get("words") or []:
        start = max(cut_start, float(word["source_start_seconds"]))
        end = min(cut_end, float(word["source_end_seconds"]))
        text = strip_non_speech_annotations(word.get("text") or "")
        if text and end - start >= 0.02:
            words.append({"start": start, "end": end, "text": text})
    if not words:
        return []
    words = _merge_replacement_words(words)

    chunks: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    for word in words:
        candidate_text = normalize_viewer_transcript(
            "".join([*(item["text"] for item in current), word["text"]])
        )
        gap = word["start"] - current[-1]["end"] if current else 0.0
        duration = word["end"] - current[0]["start"] if current else 0.0
        if current and (gap > 0.7 or duration > 4.8 or len(candidate_text) > 16):
            chunks.append(
                {
                    "start": current[0]["start"],
                    "end": current[-1]["end"],
                    "text": normalize_viewer_transcript(
                        "".join(item["text"] for item in current)
                    ),
                }
            )
            current = []
        current.append(word)
    if current:
        chunks.append(
            {
                "start": current[0]["start"],
                "end": current[-1]["end"],
                "text": normalize_viewer_transcript(
                    "".join(item["text"] for item in current)
                ),
            }
        )
    return [row for row in chunks if row["text"]]


def build_timeline(
    selection: dict[str, Any],
    *,
    source_identity: str,
    source_sha256: str,
    source_duration_seconds: float,
    source_media_offset_seconds: float = 0.0,
) -> dict[str, Any]:
    winner_id = selection["winner"]["candidate_id"]
    winner = next(
        row for row in selection["candidates"] if row.get("candidate_id") == winner_id
    )
    section_names = (
        "premise_setup",
        "red_card_setup",
        "work_context",
        "profile_escalation",
        "notification_reveal",
        "apology",
        "aftermath",
        "ending_warning",
    )
    roles = (
        "hook",
        "visual_setup",
        "necessary_context",
        "escalation",
        "turn_and_payoff",
        "response",
        "aftermath",
        "closure",
    )
    cuts = []
    cursor = 0.0
    for index, pair in enumerate(winner["planned_cuts_seconds"], start=1):
        provider_source_in = float(pair[0])
        provider_source_out = float(pair[1])
        source_in = provider_source_in - source_media_offset_seconds
        source_out = provider_source_out - source_media_offset_seconds
        duration = source_out - source_in
        if source_in < 0 or source_out > source_duration_seconds + 0.5:
            raise PushMicroarcEditorialV2Error(
                "planned provider range is outside the acquired source window",
                stage="selection",
            )
        cuts.append(
            {
                "cut_id": f"out14_v2_cut_{index:03d}",
                "output_order": index,
                "source_identity": source_identity,
                "source_sha256": source_sha256,
                "source_in_seconds": round(source_in, 6),
                "source_out_seconds": round(source_out, 6),
                "provider_source_in_seconds": round(provider_source_in, 6),
                "provider_source_out_seconds": round(provider_source_out, 6),
                "output_in_seconds": round(cursor, 6),
                "output_out_seconds": round(cursor + duration, 6),
                "duration_seconds": round(duration, 6),
                "section": section_names[index - 1],
                "editorial_role": roles[index - 1],
                "selection_reason": (
                    "retains one causal beat while removing false starts, repeated "
                    "phrasing, screen-navigation delay, or unrelated chat response"
                ),
                "transition": "sequence_start" if index == 1 else "hard_cut",
                "transcript_segment_ids": [],
                "caption_ids": [],
            }
        )
        cursor += duration
    omitted = _omitted_ranges(cuts, source_duration_seconds)
    return {
        "schema_version": "clippipegen.timeline_ir.v1",
        "selection_mode": "push_microarc_editorial_reconstruction_v2",
        "source_identity": source_identity,
        "source_sha256": source_sha256,
        "source_duration_seconds": round(source_duration_seconds, 6),
        "source_media_offset_seconds": round(source_media_offset_seconds, 6),
        "cuts": cuts,
        "cut_count": len(cuts),
        "output_duration_seconds": round(cursor, 6),
        "chronology_preserved": True,
        "source_order_changed": False,
        "cold_open_applied": False,
        "omitted_ranges": omitted,
        "selected_source_seconds": round(cursor, 6),
        "source_utilization_ratio": round(cursor / source_duration_seconds, 9),
        "semantic_section_count": len({row["section"] for row in cuts}),
    }


def _omitted_ranges(
    cuts: list[dict[str, Any]], source_duration_seconds: float
) -> list[dict[str, Any]]:
    rows = []
    cursor = 0.0
    for cut in cuts:
        source_in = float(cut["source_in_seconds"])
        if source_in > cursor + 0.001:
            rows.append(
                {
                    "omitted_id": f"out14_v2_omit_{len(rows) + 1:03d}",
                    "source_in_seconds": round(cursor, 6),
                    "source_out_seconds": round(source_in, 6),
                    "duration_seconds": round(source_in - cursor, 6),
                    "omission_reason": (
                        "outside the selected premise or removed as repetition, "
                        "false start, dead time, or nonessential digression"
                    ),
                    "intentional_editorial_omission": True,
                }
            )
        cursor = float(cut["source_out_seconds"])
    if cursor < source_duration_seconds:
        rows.append(
            {
                "omitted_id": f"out14_v2_omit_{len(rows) + 1:03d}",
                "source_in_seconds": round(cursor, 6),
                "source_out_seconds": round(source_duration_seconds, 6),
                "duration_seconds": round(source_duration_seconds - cursor, 6),
                "omission_reason": "later unrelated stream topics are outside this premise",
                "intentional_editorial_omission": True,
            }
        )
    return rows


def remap_canonical_transcript(
    transcript: dict[str, Any], timeline: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = []
    for segment in transcript.get("segments") or []:
        text = normalize_viewer_transcript(segment.get("text") or "")
        if not text:
            continue
        segment_start = float(segment["source_start_seconds"])
        segment_end = float(segment["source_end_seconds"])
        for cut in timeline["cuts"]:
            provider_source_in = float(cut["provider_source_in_seconds"])
            provider_source_out = float(cut["provider_source_out_seconds"])
            overlap_start = max(provider_source_in, segment_start)
            overlap_end = min(provider_source_out, segment_end)
            if overlap_end - overlap_start < 0.12:
                continue
            chunks = _word_caption_chunks(
                segment, cut_start=overlap_start, cut_end=overlap_end
            )
            if not chunks:
                chunks = [{"start": overlap_start, "end": overlap_end, "text": text}]
            for chunk in chunks:
                chunk_start = float(chunk["start"])
                chunk_end = float(chunk["end"])
                chunk_text = str(chunk["text"])
                output_start = (
                    float(cut["output_in_seconds"])
                    + chunk_start
                    - provider_source_in
                )
                output_end = (
                    float(cut["output_in_seconds"]) + chunk_end - provider_source_in
                )
                rows.append(
                    {
                        "caption_id": f"speech_{len(rows) + 1:04d}",
                        "cut_id": cut["cut_id"],
                        "source_start_seconds": round(chunk_start, 6),
                        "source_end_seconds": round(chunk_end, 6),
                        "media_start_seconds": round(
                            chunk_start - timeline["source_media_offset_seconds"], 6
                        ),
                        "media_end_seconds": round(
                            chunk_end - timeline["source_media_offset_seconds"], 6
                        ),
                        "output_start_seconds": round(output_start, 6),
                        "output_end_seconds": round(output_end, 6),
                        "text": chunk_text,
                        "text_sha256": hashlib.sha256(
                            chunk_text.encode("utf-8")
                        ).hexdigest(),
                        "source_segment_id": segment["segment_id"],
                        "source_type": "canonical_actual_audio_speech",
                        "confidence": segment.get("confidence"),
                        "split_at_cut_boundary": (
                            overlap_start > segment_start + 0.001
                            or overlap_end < segment_end - 0.001
                        ),
                        "word_timed_chunk": bool(segment.get("words")),
                    }
                )
                cut["transcript_segment_ids"].append(segment["segment_id"])
                cut["caption_ids"].append(rows[-1]["caption_id"])
    rows.sort(key=lambda row: (row["output_start_seconds"], row["output_end_seconds"]))
    previous_end = 0.0
    for row in rows:
        if row["output_start_seconds"] < previous_end:
            row["output_start_seconds"] = round(previous_end, 6)
        if row["output_end_seconds"] - row["output_start_seconds"] < 0.12:
            row["output_end_seconds"] = round(row["output_start_seconds"] + 0.12, 6)
        previous_end = row["output_end_seconds"]
    if not rows:
        raise PushMicroarcEditorialV2Error(
            "canonical transcript produced no viewer-facing speech cues",
            stage="transcript_alignment",
        )
    if any(NON_SPEECH_PATTERN.search(row["text"]) for row in rows):
        raise PushMicroarcEditorialV2Error(
            "viewer-facing transcript retained a non-speech annotation",
            stage="transcript_alignment",
        )
    return rows


def build_timing_readback(
    transcript: dict[str, Any],
    caption_rows: list[dict[str, Any]],
    timeline: dict[str, Any],
) -> dict[str, Any]:
    anchors = transcript.get("timing_anchors") or []
    required = max(15, 3 * len({row["section"] for row in timeline["cuts"]}))
    if len(anchors) < required:
        raise PushMicroarcEditorialV2Error(
            f"timing anchor set requires at least {required} anchors",
            stage="transcript_alignment",
        )
    rendered_errors = [float(row["rendered_onset_error_ms"]) for row in anchors]
    median = statistics.median(rendered_errors)
    absolute = sorted(abs(value) for value in rendered_errors)
    p95_index = max(0, math.ceil(0.95 * len(absolute)) - 1)
    p95 = absolute[p95_index]
    provider_errors = [
        float(row["provider_signed_onset_error_ms"])
        for row in anchors
        if row.get("provider_signed_onset_error_ms") is not None
    ]
    provider_median = statistics.median(provider_errors) if provider_errors else None
    section_counts: dict[str, int] = {}
    for row in anchors:
        section_counts[str(row["section"])] = section_counts.get(str(row["section"]), 0) + 1
    passed = (
        -100.0 <= median <= 100.0
        and p95 <= 300.0
        and len(caption_rows) > 0
        and all(value >= 3 for value in section_counts.values())
    )
    if not passed:
        raise PushMicroarcEditorialV2Error(
            "canonical subtitle timing acceptance target failed",
            stage="transcript_alignment",
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "method": transcript["method"],
        "anchor_count": len(anchors),
        "required_anchor_count": required,
        "section_anchor_counts": section_counts,
        "rendered_median_signed_onset_error_ms": round(median, 3),
        "rendered_absolute_onset_error_p95_ms": round(p95, 3),
        "systematic_late_bias": False,
        "provider_caption_diagnostic": {
            "median_signed_onset_error_ms": (
                round(provider_median, 3) if provider_median is not None else None
            ),
            "systematic_late_bias_observed": (
                provider_median is not None and provider_median > 100.0
            ),
            "authority": "discovery_provenance_only",
        },
        "source_to_output_mapping": "deterministic_cut_offset",
        "viewer_facing_non_speech_annotation_count": 0,
        "anchors": anchors,
    }


def _ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, centis = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def _ass_text(value: str) -> str:
    return str(value).replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def write_combined_ass(
    path: Path,
    speech_items: list[dict[str, Any]],
    telops: list[dict[str, Any]],
    *,
    font_family: str,
) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {TARGET_WIDTH}
PlayResY: {TARGET_HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Speech,{font_family},74,&H00FFFFFF,&H000000FF,&H00100B08,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,150,150,68,1
Style: Telop,{font_family},66,&H00FFFFFF,&H000000FF,&H00221708,&HC0000000,-1,0,0,0,100,100,0,0,3,2,0,8,120,120,88,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for item in speech_items:
        text = r"\N".join(
            _ass_text(line)
            for line in (item.get("wrapped_lines") or [item["text"]])
        )
        events.append(
            "Dialogue: 0,"
            f"{_ass_time(float(item['render_start_seconds']))},"
            f"{_ass_time(float(item['render_end_seconds']))},"
            f"Speech,,0,0,0,,{text}"
        )
    for row in telops:
        events.append(
            "Dialogue: 1,"
            f"{_ass_time(float(row['output_start_seconds']))},"
            f"{_ass_time(float(row['output_end_seconds']))},"
            f"Telop,,0,0,0,,{_ass_text(row['text'])}"
        )
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8-sig")


def build_push_microarc_editorial_v2(
    *,
    artifact_id: str,
    source_path: Path,
    source_identity: str,
    source_receipt_path: Path,
    material_ledger_path: Path,
    rights_manifest_path: Path,
    selection_path: Path,
    competitive_scan_path: Path,
    canonical_transcript_path: Path,
    provider_caption_path: Path,
    human_decision_path: Path,
    output_dir: Path,
    review_port: int = DEFAULT_REVIEW_PORT,
    source_media_offset_seconds: float = 0.0,
    pre_rendered_video_path: Path | None = None,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    root = (base_dir or Path.cwd()).resolve()
    stage_name = "preflight"
    stage: Path | None = None
    output = _resolved(root, output_dir)
    try:
        if not ARTIFACT_ID_PATTERN.fullmatch(artifact_id):
            raise PushMicroarcEditorialV2Error(
                "invalid v2 artifact id", stage=stage_name
            )
        if not 1 <= review_port <= 65535:
            raise PushMicroarcEditorialV2Error(
                "review port must be valid", stage=stage_name
            )
        tools = ffmpeg_tiny.preflight_tools(
            ffmpeg_path=ffmpeg_path, ffprobe_path=ffprobe_path
        )
        if tools.get("status") != "passed":
            raise PushMicroarcEditorialV2Error(
                "FFmpeg preflight failed", stage=stage_name
            )
        ffmpeg = str(tools["ffmpeg"]["path"])
        ffprobe = str(tools["ffprobe"]["path"])
        files = {
            "source": _resolved(root, source_path),
            "source_receipt": _resolved(root, source_receipt_path),
            "material_ledger": _resolved(root, material_ledger_path),
            "rights_manifest": _resolved(root, rights_manifest_path),
            "selection": _resolved(root, selection_path),
            "competitive": _resolved(root, competitive_scan_path),
            "transcript": _resolved(root, canonical_transcript_path),
            "provider_caption": _resolved(root, provider_caption_path),
            "human_decision": _resolved(root, human_decision_path),
        }
        missing = [name for name, path in files.items() if not path.is_file()]
        if missing:
            raise PushMicroarcEditorialV2Error(
                f"required inputs missing: {missing}", stage=stage_name
            )
        source_sha256 = _sha256(files["source"])
        receipt = _read_json(files["source_receipt"])
        if (
            receipt.get("sha256") != source_sha256
            or receipt.get("byte_size") != files["source"].stat().st_size
        ):
            raise PushMicroarcEditorialV2Error(
                "HD source receipt does not bind selected bytes", stage=stage_name
            )
        decision = _read_json(files["human_decision"])
        validate_v1_human_decision(decision)
        selection = _read_json(files["selection"])
        competitive = _read_json(files["competitive"])
        if len(competitive.get("confirmed_items") or []) < 1:
            raise PushMicroarcEditorialV2Error(
                "competitive scan has no confirmed observations", stage="selection"
            )
        transcript = _read_json(files["transcript"])
        selection_validation = validate_candidate_selection(selection)
        if transcript.get("source_identity") != source_identity:
            raise PushMicroarcEditorialV2Error(
                "canonical transcript source identity mismatch",
                stage="transcript_alignment",
            )
        if transcript.get("manual_verification", {}).get("status") != "completed":
            raise PushMicroarcEditorialV2Error(
                "canonical transcript manual language verification is incomplete",
                stage="transcript_alignment",
            )
        source_probe = out12.probe_media_detail(
            files["source"], ffprobe_path=ffprobe, runner=subprocess.run
        )
        if (
            int(source_probe["width"]) < 1280
            or int(source_probe["height"]) < 720
        ):
            raise PushMicroarcEditorialV2Error(
                "selected source is not anonymous HD", stage=stage_name
            )
        timeline = build_timeline(
            selection,
            source_identity=source_identity,
            source_sha256=source_sha256,
            source_duration_seconds=float(source_probe["duration_seconds"]),
            source_media_offset_seconds=float(source_media_offset_seconds),
        )
        speech_rows = remap_canonical_transcript(transcript, timeline)
        timing = build_timing_readback(transcript, speech_rows, timeline)
        known_loci = []
        for locus in KNOWN_V1_LOCI:
            retained = any(
                max(
                    float(locus["source_in_seconds"]),
                    float(cut["provider_source_in_seconds"]),
                )
                < min(
                    float(locus["source_out_seconds"]),
                    float(cut["provider_source_out_seconds"]),
                )
                for cut in timeline["cuts"]
            )
            known_loci.append(
                {
                    **locus,
                    "retained_in_v2": retained,
                    "resolution": (
                        "canonical_actual_audio_repair_required"
                        if retained
                        else "explicitly_excluded_with_v1_manifest_resolved_source_time"
                    ),
                    "exclusion_reason": (
                        None
                        if retained
                        else "selected Discord micro-arc is disjoint from the rejected rural/animal span"
                    ),
                }
            )
        if any(row["retained_in_v2"] for row in known_loci):
            raise PushMicroarcEditorialV2Error(
                "known v1 loci unexpectedly overlap the selected v2 episode",
                stage="transcript_alignment",
            )
        out13._validate_output_allocation(
            output=output, artifact_id=artifact_id, force=False
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        stage = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
        stage.mkdir()
        for name, source in (
            ("selection_record.json", files["selection"]),
            ("competitive_coverage.json", files["competitive"]),
            ("canonical_transcript.json", files["transcript"]),
            ("provider_caption_provenance.json3", files["provider_caption"]),
            ("v1_human_decision_record.json", files["human_decision"]),
        ):
            shutil.copyfile(source, stage / name)
        _write_json(stage / "timeline_ir.json", timeline)
        _write_json(stage / "subtitle_timing_readback.json", timing)
        _write_json(stage / "known_v1_loci_readback.json", {"items": known_loci})
        _write_json(
            stage / "profile_contract_snapshot.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "passed",
                "selection": selection_validation,
                "normal_duration_contract": True,
                "multiple_meaningful_cuts": len(timeline["cuts"]) >= 3,
                "chronology_preserved": True,
                "v1_quarantine_avoided": True,
                "provider_caption_viewer_authority": False,
                "canonical_actual_audio_transcript": True,
                "anonymous_hd_source": True,
            },
        )
        caption_readback = out12.build_caption_readback(
            caption_mode="official_sidecar",
            caption_authority={
                "classification": "canonical_actual_audio_transcript",
                "engine": transcript["method"]["engine"],
                "model": transcript["method"]["model"],
                "manual_language_verification": True,
                "provider_caption_authority": False,
            },
            caption_rows=speech_rows,
            source_caption_sha256=_sha256(files["transcript"]),
            timeline_duration_seconds=float(timeline["output_duration_seconds"]),
        )
        caption_readback["schema_version"] = SCHEMA_VERSION
        caption_readback["viewer_facing_non_speech_annotation_count"] = 0
        caption_readback["creator_telop_count"] = 4
        _write_json(stage / "caption_readback.json", caption_readback)
        _write_text(stage / "captions.srt", out12.render_srt(speech_rows))

        style = _diagnostic_ass_style_for_candidate(ED10L_KEIFONT_CANDIDATE_ID)
        font_file = Path(str(style.get("resolved_font_file") or ""))
        layout = out13._editorial_subtitle_layout_contract(
            frame_width=TARGET_WIDTH,
            frame_height=TARGET_HEIGHT,
            dimension_source="out14_editorial_v2_output",
            diagnostic_ass_style=style,
        )
        raw_items = [
            {
                "subtitle_id": row["caption_id"],
                "cut_id": row["cut_id"],
                "status": "included",
                "render_start_seconds": row["output_start_seconds"],
                "render_end_seconds": row["output_end_seconds"],
                "text": out13._caption_text_for_presentation(row["text"]),
                "authority_text": row["text"],
                "source_type": "canonical_actual_audio_speech",
                "source_segment_ids": [row["source_segment_id"]],
            }
            for row in speech_rows
        ]
        presentation_items = _presentation_items(raw_items, layout=layout)
        selector = select_subtitle_preset(
            {
                "speaker_id": "unknown",
                "speaker_role": "talent",
                "emotion": "neutral",
                "intensity": 0,
                "utterance_role": "dialogue",
                "readability_priority": "maximum",
            }
        )
        subtitle_readback = out13.build_subtitle_presentation_readback(
            layout=layout,
            presentation_items=presentation_items,
            selector=selector,
            caption_readback=caption_readback,
            font_sha256=_sha256(font_file) if font_file.is_file() else None,
        )
        subtitle_readback["schema_version"] = SCHEMA_VERSION
        subtitle_readback["speech_source_type"] = "canonical_actual_audio_speech"
        subtitle_readback["creator_telop_source_type"] = "creator_authored_editorial"
        _write_json(stage / "subtitle_presentation_readback.json", subtitle_readback)
        if subtitle_readback["status"] != "passed":
            raise PushMicroarcEditorialV2Error(
                "subtitle presentation failed", stage="subtitle_presentation"
            )
        telops = [
            {
                "telop_id": "telop_premise",
                "output_start_seconds": 0.25,
                "output_end_seconds": 5.0,
                "text": "Discordのプロフィールを変えた朝",
                "role": "premise",
                "provenance": "creator_authored_editorial",
            },
            {
                "telop_id": "telop_escalation",
                "output_start_seconds": 168.1,
                "output_end_seconds": 172.4,
                "text": "遊びで変え続けた結果",
                "role": "transition",
                "provenance": "creator_authored_editorial",
            },
            {
                "telop_id": "telop_payoff",
                "output_start_seconds": 244.3,
                "output_end_seconds": 249.2,
                "text": "変更通知が届いていた",
                "role": "punchline",
                "provenance": "creator_authored_editorial",
            },
            {
                "telop_id": "telop_ending",
                "output_start_seconds": 386.2,
                "output_end_seconds": 391.2,
                "text": "変更は全体通知される",
                "role": "ending",
                "provenance": "creator_authored_editorial",
            },
        ]
        _write_json(
            stage / "section_map.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cuts": timeline["cuts"],
                "telops": telops,
                "speech_and_telop_identity_collision_count": 0,
            },
        )
        ass_path = stage / "speech_and_telops.ass"
        write_combined_ass(
            ass_path,
            presentation_items,
            telops,
            font_family=str(style.get("font_name") or "Arial"),
        )

        stage_name = "thumbnail_preflight"
        thumbnail = _build_thumbnail_rough(
            source_path=files["source"],
            stage=stage,
            source_seconds=2688.44,
            source_media_offset_seconds=float(source_media_offset_seconds),
            font_file=font_file,
            ffmpeg_path=ffmpeg,
        )
        titles = {
            "working_title": "Discordのプロフィールを遊びで変えたら、全スタッフに通知が飛んでいた",
            "alternatives": [
                "おかゆとプロフィールをいじった結果、通知先に戦慄するスバル",
                "「蒙古タンメン スバル」が全スタッフに共有された朝",
            ],
            "funeral_primary_hook": False,
        }
        _write_json(
            stage / "title_thumbnail_readback.json",
            {
                "schema_version": SCHEMA_VERSION,
                **titles,
                "thumbnail": thumbnail,
                "actual_source_frame_only": True,
                "generated_image_count": 0,
                "publication_thumbnail_acceptance": False,
                "diagnostic_review_use_only": True,
            },
        )

        stage_name = "render"
        final_video = stage / "final_video.mp4"
        if pre_rendered_video_path is not None:
            render = _reuse_completed_render_for_validation_retry(
                artifact_id=artifact_id,
                recovered_path=_resolved(root, pre_rendered_video_path),
                stage_video_path=final_video,
                artifact_root=output.parent,
            )
        else:
            render = _render_editorial_v2(
                source_path=files["source"],
                video_path=final_video,
                cuts=timeline["cuts"],
                ass_path=ass_path,
                font_file=font_file,
                ffmpeg_path=ffmpeg,
                output_width=TARGET_WIDTH,
                output_height=TARGET_HEIGHT,
            )
        stage_name = "media_validation"
        expected_probe = {
            **source_probe,
            "width": TARGET_WIDTH,
            "height": TARGET_HEIGHT,
            "resolution": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
        }
        validation = out12.validate_rendered_video(
            video_path=final_video,
            timeline=timeline,
            caption_readback=caption_readback,
            source_probe=expected_probe,
            ffmpeg_path=ffmpeg,
            ffprobe_path=ffprobe,
            runner=subprocess.run,
        )
        validation["schema_version"] = SCHEMA_VERSION
        validation["render"] = render
        validation["editorial_checks"] = {
            "candidate_selection": selection_validation["status"] == "passed",
            "transcript_alignment": timing["status"] == "passed",
            "non_speech_annotations_removed": (
                caption_readback["viewer_facing_non_speech_annotation_count"] == 0
            ),
            "visible_structure": len(telops) >= 3,
            "speech_telop_provenance_separated": True,
            "thumbnail_preflight": thumbnail["status"] == "passed",
            "anonymous_hd_source": int(source_probe["height"]) >= 720,
            "known_v1_loci_resolved": all(
                not row["retained_in_v2"] for row in known_loci
            ),
        }
        if validation["status"] != "passed" or not all(
            validation["editorial_checks"].values()
        ):
            raise PushMicroarcEditorialV2Error(
                "render/media admission failed", stage=stage_name
            )
        validation["state"] = READY_STATE
        _write_json(stage / "validation_readback.json", validation)

        stage_name = "review_package"
        resolved = {
            "source_path": files["source"],
            "source_identity": source_identity,
            "source_sha256": source_sha256,
            "source_byte_size": files["source"].stat().st_size,
            "caption_mode": "canonical_actual_audio_transcript",
            "rights": {
                "status": "pending",
                "public_release_approved": False,
            },
        }
        review = out12.build_review_package(
            stage=stage,
            timeline=timeline,
            resolved=resolved,
            validation=validation,
            review_port=review_port,
            ffmpeg_path=ffmpeg,
            runner=subprocess.run,
        )
        source_contact = stage / "review" / "evidence" / "source_selected_ranges.jpg"
        out12.render_contact_sheet(
            video_path=files["source"],
            output_path=source_contact,
            sample_times=[
                (float(row["source_in_seconds"]) + float(row["source_out_seconds"]))
                / 2.0
                for row in timeline["cuts"]
            ],
            fps=out12._frame_rate_float(source_probe.get("frame_rate")),
            ffmpeg_path=ffmpeg,
            runner=subprocess.run,
        )
        probes = _review_probes(timeline, known_loci)
        _write_json(
            stage / "review" / "review_readback.json",
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": artifact_id,
                "working_title": titles["working_title"],
                "thumbnail_rough": "../thumbnail_rough_1280x720.jpg",
                "full_video": "../final_video.mp4",
                "probes": probes,
                "human_review_pending": True,
                "machine_evidence_scope": (
                    "construction, traceability, timing, decode, mapping, and media integrity"
                ),
                "not_machine_approved": [
                    "editorial_quality",
                    "rights",
                    "YPP_eligibility",
                    "publication_readiness",
                    "thumbnail_acceptance",
                ],
            },
        )
        _write_text(
            stage / "review" / "index.html",
            _render_review_html(
                artifact_id=artifact_id,
                titles=titles,
                timeline=timeline,
                validation=validation,
                probes=probes,
                selection=selection_validation,
                timing=timing,
            ),
        )
        _write_json(
            stage / "provenance_snapshot.json",
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": artifact_id,
                "source_identity": source_identity,
                "source_sha256": source_sha256,
                "source_byte_size": files["source"].stat().st_size,
                "source_receipt_sha256": _sha256(files["source_receipt"]),
                "material_ledger_sha256": _sha256(files["material_ledger"]),
                "rights_manifest_sha256": _sha256(files["rights_manifest"]),
                "source_probe": source_probe,
                "source_media_offset_seconds": float(source_media_offset_seconds),
                "provider_caption_sha256": _sha256(files["provider_caption"]),
                "provider_caption_viewer_authority": False,
                "canonical_transcript_sha256": _sha256(files["transcript"]),
                "human_decision_sha256": _sha256(files["human_decision"]),
                "competitive_scan_sha256": _sha256(files["competitive"]),
                "external_mutation": False,
            },
        )
        _write_json(
            stage / "pipeline_state.json",
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": artifact_id,
                "state": READY_STATE,
                "human_review_ready": True,
                "human_review_pending": True,
                "final_video_sha256": validation["media"]["sha256"],
                "output_duration_seconds": validation["media"]["duration_seconds"],
                "cut_count": len(timeline["cuts"]),
                "speech_cue_count": len(speech_rows),
                "creator_telop_count": len(telops),
                "external_mutation": False,
                "closed_gates": _closed_gates(),
            },
        )
        manifest = _build_manifest(
            artifact_id=artifact_id,
            stage=stage,
            source_identity=source_identity,
            source_sha256=source_sha256,
            validation=validation,
            timeline=timeline,
            review=review,
        )
        _write_json(stage / "run_manifest.json", manifest)
        _validate_manifest(stage, manifest, artifact_id)
        out13._promote_output_immutable(stage=stage, output=output)
        stage = None
        promoted_manifest = _read_json(output / "run_manifest.json")
        _validate_manifest(output, promoted_manifest, artifact_id)
        return {
            "artifact_id": artifact_id,
            "state": READY_STATE,
            "output_dir": output,
            "final_video": output / "final_video.mp4",
            "review_index": output / "review" / "index.html",
            "review_url": f"http://127.0.0.1:{review_port}/review/index.html",
            "open_command": output / "review" / "open_preview.ps1",
            "video_sha256": validation["media"]["sha256"],
            "manifest_sha256": _sha256(output / "run_manifest.json"),
            "duration_seconds": validation["media"]["duration_seconds"],
            "cut_count": len(timeline["cuts"]),
            "speech_cue_count": len(speech_rows),
            "creator_telop_count": len(telops),
        }
    except Exception as exc:
        if stage is not None and stage.exists():
            failure = output.parent / f".{output.name}.failed-{uuid.uuid4().hex}"
            stage.replace(failure)
        if isinstance(exc, PushMicroarcEditorialV2Error):
            raise
        raise PushMicroarcEditorialV2Error(str(exc), stage=stage_name) from exc


def _build_thumbnail_rough(
    *,
    source_path: Path,
    stage: Path,
    source_seconds: float,
    source_media_offset_seconds: float,
    font_file: Path,
    ffmpeg_path: str,
) -> dict[str, Any]:
    large = stage / "thumbnail_rough_1280x720.jpg"
    small = stage / "thumbnail_rough_320x180.jpg"
    font = str(font_file).replace("\\", "/").replace(":", r"\:")
    text = "全スタッフに通知"
    vf = (
        "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
        "drawbox=x=0:y=500:w=1280:h=220:color=black@0.62:t=fill,"
        f"drawtext=fontfile='{font}':text='{text}':fontcolor=white:"
        "fontsize=78:borderw=5:bordercolor=black:x=(w-text_w)/2:y=545"
    )
    result = subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{source_seconds - source_media_offset_seconds:.3f}",
            "-i",
            str(source_path),
            "-frames:v",
            "1",
            "-vf",
            vf,
            "-q:v",
            "2",
            str(large),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=out12.COMMAND_TIMEOUT_SECONDS,
    )
    if result.returncode != 0 or not large.is_file():
        raise PushMicroarcEditorialV2Error(
            "source-frame thumbnail rough generation failed",
            stage="thumbnail_preflight",
        )
    result = subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(large),
            "-vf",
            "scale=320:180",
            "-q:v",
            "2",
            str(small),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=out12.COMMAND_TIMEOUT_SECONDS,
    )
    if result.returncode != 0 or not small.is_file():
        raise PushMicroarcEditorialV2Error(
            "small thumbnail readback generation failed",
            stage="thumbnail_preflight",
        )
    return {
        "status": "passed",
        "source_frame_seconds": source_seconds,
        "source_media_frame_seconds": round(
            source_seconds - source_media_offset_seconds, 3
        ),
        "source_frame_identity": "selected_source_bytes",
        "focal_relationship": "profile change and unexpected staff-wide notification",
        "text": text,
        "large": {
            "path": large.name,
            "resolution": "1280x720",
            "sha256": _sha256(large),
        },
        "small": {
            "path": small.name,
            "resolution": "320x180",
            "sha256": _sha256(small),
        },
    }


def _reuse_completed_render_for_validation_retry(
    *,
    artifact_id: str,
    recovered_path: Path,
    stage_video_path: Path,
    artifact_root: Path,
) -> dict[str, Any]:
    recovered = recovered_path.resolve()
    expected_root = artifact_root.resolve()
    expected_prefix = f".{artifact_id}.failed-"
    if (
        not recovered.is_file()
        or recovered.name != "final_video.mp4"
        or recovered.parent.parent != expected_root
        or not recovered.parent.name.startswith(expected_prefix)
    ):
        raise PushMicroarcEditorialV2Error(
            "pre-rendered recovery input is outside the exact failed artifact identity",
            stage="render",
        )
    os.link(recovered, stage_video_path)
    if (
        not stage_video_path.is_file()
        or stage_video_path.stat().st_size != recovered.stat().st_size
        or _sha256(stage_video_path) != _sha256(recovered)
    ):
        raise PushMicroarcEditorialV2Error(
            "pre-rendered recovery hardlink failed identity verification",
            stage="render",
        )
    return {
        "status": "passed",
        "selected_video_encoder": "completed_prior_attempt_pending_revalidation",
        "audio_encoder": "completed_prior_attempt_pending_revalidation",
        "subtitle_renderer": "ffmpeg_ass_libass",
        "attempts": [
            {
                "status": "reused_for_validation_retry",
                "sha256": _sha256(recovered),
                "byte_size": recovered.stat().st_size,
            }
        ],
        "execution_count": 1,
        "corrective_pass_count": 0,
        "validation_retry_count": 1,
        "recovery_copy_mode": "same_volume_hardlink",
    }


def _render_editorial_v2(
    *,
    source_path: Path,
    video_path: Path,
    cuts: list[dict[str, Any]],
    ass_path: Path,
    font_file: Path,
    ffmpeg_path: str,
    output_width: int,
    output_height: int,
) -> dict[str, Any]:
    work = video_path.parent / ".render_work"
    work.mkdir()
    filter_path = work / "filter_complex.txt"
    _write_text(
        filter_path,
        out13.render_editorial_filter_complex(
            cuts=cuts,
            ass_path=ass_path,
            font_file=font_file,
            output_width=output_width,
            output_height=output_height,
        ),
    )
    attempts = []
    profiles = (
        (
            "h264_nvenc",
            ["-preset", "p4", "-tune", "hq", "-rc", "vbr", "-cq", "20", "-b:v", "0"],
        ),
        ("libx264", ["-preset", "veryfast", "-crf", "20"]),
    )
    for codec, options in profiles:
        command = [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-i",
            str(source_path),
            "-filter_complex_script",
            str(filter_path),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            codec,
            *options,
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-shortest",
            "-movflags",
            "+faststart",
            str(video_path),
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=out12.COMMAND_TIMEOUT_SECONDS,
        )
        passed = result.returncode == 0 and video_path.is_file()
        attempts.append(
            {
                "codec": codec,
                "status": "passed" if passed else "failed",
                "exit_code": result.returncode,
                "stderr_sha256": hashlib.sha256(
                    (result.stderr or "").encode("utf-8")
                ).hexdigest(),
            }
        )
        if passed:
            shutil.rmtree(work)
            return {
                "status": "passed",
                "selected_video_encoder": codec,
                "audio_encoder": "aac",
                "subtitle_renderer": "ffmpeg_ass_libass",
                "attempts": attempts,
                "execution_count": 1,
                "corrective_pass_count": 0,
            }
        if video_path.exists():
            video_path.unlink()
    shutil.rmtree(work)
    raise PushMicroarcEditorialV2Error(
        "FFmpeg editorial render failed for NVENC and libx264",
        stage="render",
    )


def _review_probes(
    timeline: dict[str, Any], known_loci: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    probes = [
        {"probe_id": "opening", "output_seconds": 0.5},
        {
            "probe_id": "profile_escalation",
            "output_seconds": timeline["cuts"][3]["output_in_seconds"] + 0.5,
        },
        {
            "probe_id": "notification_payoff",
            "output_seconds": timeline["cuts"][4]["output_in_seconds"] + 0.5,
        },
        {
            "probe_id": "apology",
            "output_seconds": timeline["cuts"][5]["output_in_seconds"] + 0.5,
        },
        {
            "probe_id": "ending",
            "output_seconds": max(0.0, timeline["output_duration_seconds"] - 5.0),
        },
    ]
    for locus in known_loci:
        probes.append(
            {
                "probe_id": locus["locus_id"],
                "availability": "excluded_from_v2",
                "source_in_seconds": locus["source_in_seconds"],
                "source_out_seconds": locus["source_out_seconds"],
                "resolution": locus["resolution"],
            }
        )
    return probes


def _render_review_html(
    *,
    artifact_id: str,
    titles: dict[str, Any],
    timeline: dict[str, Any],
    validation: dict[str, Any],
    probes: list[dict[str, Any]],
    selection: dict[str, Any],
    timing: dict[str, Any],
) -> str:
    probe_buttons = "".join(
        (
            f'<button type="button" data-seek="{float(row["output_seconds"]):.3f}">'
            f'{escape(str(row["probe_id"]))}</button>'
            if row.get("output_seconds") is not None
            else f'<span class="excluded">{escape(str(row["probe_id"]))}: excluded</span>'
        )
        for row in probes
    )
    cut_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['cut_id']))}</td>"
        f"<td>{escape(str(row['section']))}</td>"
        f"<td>{float(row['provider_source_in_seconds']):.3f}–{float(row['provider_source_out_seconds']):.3f}</td>"
        f"<td>{float(row['output_in_seconds']):.3f}–{float(row['output_out_seconds']):.3f}</td>"
        "</tr>"
        for row in timeline["cuts"]
    )
    alternatives = "".join(f"<li>{escape(value)}</li>" for value in titles["alternatives"])
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-14 editorial v2 review</title>
<style>body{{margin:0;background:#07111f;color:#e8f0fa;font-family:system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:24px}}h1{{font-size:clamp(24px,4vw,44px)}}.hero{{display:grid;grid-template-columns:minmax(280px,1fr) minmax(300px,1.3fr);gap:24px;align-items:start}}.hero img{{width:100%;height:auto;border-radius:12px}}video{{display:block;width:100%;background:#000;margin:22px 0}}button,.excluded{{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #38bdf8;border-radius:8px;background:#0f2940;color:white}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #334155;text-align:left}}code{{overflow-wrap:anywhere}}.pending{{padding:14px;border-left:4px solid #f59e0b;background:#2b2110}}@media(max-width:760px){{.hero{{grid-template-columns:1fr}}}}</style></head>
<body><main><h1>{escape(titles["working_title"])}</h1>
<div class="hero"><img src="../thumbnail_rough_1280x720.jpg" alt="actual source frame thumbnail rough"><section><p><code>{escape(artifact_id)}</code></p><p>thumbnail roughは実source frame由来のreview補助。publication/marketing acceptanceは未判定。</p><h2>比較タイトル</h2><ul>{alternatives}</ul><p>selection {selection["winner_score"]}/100 · {selection["planned_cut_count"]} cuts · {selection["planned_output_duration_seconds"]:.3f}s</p></section></div>
<video id="finalVideo" controls muted preload="metadata" playsinline src="../final_video.mp4"></video>
<div>{probe_buttons}</div>
<p>SHA-256 <code>{escape(str(validation["media"]["sha256"]))}</code> · {float(validation["media"]["duration_seconds"]):.3f}s · {escape(str(validation["media"]["resolution"]))}</p>
<h2>Source → output mapping</h2><table><thead><tr><th>cut</th><th>section</th><th>source</th><th>output</th></tr></thead><tbody>{cut_rows}</tbody></table>
<h2>字幕 timing</h2><p>{timing["anchor_count"]} anchors · median {timing["rendered_median_signed_onset_error_ms"]:.1f}ms · abs p95 {timing["rendered_absolute_onset_error_p95_ms"]:.1f}ms · viewer-facing non-speech annotations 0.</p>
<p class="pending">Human editorial review pending. Machine evidence covers construction, traceability, timing, mapping, decode and media integrity. Editorial quality, rights, YPP eligibility, publication readiness and thumbnail acceptance remain closed.</p>
<details><summary>Evidence images</summary><img src="evidence/first_middle_last_contact_sheet.jpg" alt="first middle last"><img src="evidence/cut_boundary_contact_sheet.jpg" alt="cut boundaries"><img src="evidence/source_selected_ranges.jpg" alt="selected source ranges"><img src="evidence/waveform.png" alt="waveform"></details>
</main><script>const v=document.getElementById('finalVideo');v.autoplay=false;v.muted=true;v.volume=.25;v.currentTime=0;document.querySelectorAll('[data-seek]').forEach(b=>b.addEventListener('click',()=>{{v.pause();v.currentTime=Number(b.dataset.seek);}}));</script></body></html>
"""


def _closed_gates() -> dict[str, bool]:
    return {
        "human_editorial_acceptance": False,
        "rights_approval": False,
        "YPP_eligibility": False,
        "production_acceptance": False,
        "publication_readiness": False,
        "thumbnail_acceptance": False,
        "upload": False,
        "visibility_change": False,
    }


def _build_manifest(
    *,
    artifact_id: str,
    stage: Path,
    source_identity: str,
    source_sha256: str,
    validation: dict[str, Any],
    timeline: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    files = []
    for path in sorted(row for row in stage.rglob("*") if row.is_file()):
        relative = path.relative_to(stage).as_posix()
        if relative == "run_manifest.json":
            continue
        files.append(
            {
                "repo_relative_path": relative,
                "sha256": _sha256(path),
                "byte_size": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
        "artifact_id": artifact_id,
        "state": READY_STATE,
        "source": {
            "identity": source_identity,
            "sha256": source_sha256,
        },
        "final_video": {
            "path": "final_video.mp4",
            "sha256": validation["media"]["sha256"],
            "byte_size": validation["media"]["byte_size"],
            "duration_seconds": validation["media"]["duration_seconds"],
            "resolution": validation["media"]["resolution"],
        },
        "editorial": {
            "cut_count": len(timeline["cuts"]),
            "chronology_preserved": True,
            "source_order_changed": False,
        },
        "review": review,
        "human_review_ready": True,
        "human_review_pending": True,
        "files": files,
        "file_count": len(files),
        "closed_gates": _closed_gates(),
        "manifest_self_integrity": {"sha256": None},
    }
    manifest["manifest_self_integrity"]["sha256"] = _manifest_hash(manifest)
    return manifest


def _validate_manifest(stage: Path, manifest: dict[str, Any], artifact_id: str) -> None:
    if (
        manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION
        or manifest.get("artifact_id") != artifact_id
        or manifest.get("state") != READY_STATE
        or manifest.get("manifest_self_integrity", {}).get("sha256")
        != _manifest_hash(manifest)
    ):
        raise PushMicroarcEditorialV2Error(
            "manifest identity/integrity mismatch", stage="manifest"
        )
    expected = {
        path.relative_to(stage).as_posix()
        for path in stage.rglob("*")
        if path.is_file() and path.name != "run_manifest.json"
    }
    declared = {row["repo_relative_path"] for row in manifest.get("files") or []}
    if expected != declared or manifest.get("file_count") != len(declared):
        raise PushMicroarcEditorialV2Error(
            "manifest closed file set mismatch", stage="manifest"
        )
    for row in manifest["files"]:
        path = stage / row["repo_relative_path"]
        if (
            not path.is_file()
            or path.stat().st_size != row["byte_size"]
            or _sha256(path) != row["sha256"]
        ):
            raise PushMicroarcEditorialV2Error(
                f"manifest payload mismatch: {row['repo_relative_path']}",
                stage="manifest",
            )


def _manifest_hash(payload: dict[str, Any]) -> str:
    clone = json.loads(json.dumps(payload))
    clone["manifest_self_integrity"]["sha256"] = None
    raw = json.dumps(clone, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _resolved(root: Path, path: Path) -> Path:
    value = path if path.is_absolute() else root / path
    return value.resolve()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise PushMicroarcEditorialV2Error(
            f"JSON input is not an object: {path}", stage="preflight"
        )
    return payload


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
