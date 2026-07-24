"""Provenance-bound edit-ready source packet contract.

This module is intentionally provider-neutral and side-effect-light. The CLI
orchestrator reuses existing acquisition/STT adapters, while this module owns
caption validation, transcript authority selection, packet integrity, and the
consumer-facing readback contract.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .transcript import build_transcript, validate_transcript

PACKET_SCHEMA = "clippipegen.edit_ready_source_packet.v1"
SCHEMA_VERSION = "v1"
READY_STATE = "EDIT_READY_SOURCE_PACKET_OPERATIONAL_V1"
BLOCKED_STATE = "EDIT_READY_SOURCE_PACKET_BLOCKED_V1"
MIN_AUTHORITY_COVERAGE_RATIO = 0.05
SOURCE_DURATION_TOLERANCE_SECONDS = 0.25
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SourcePacketBlocked(Exception):
    """Typed fail-closed result for an ineligible source packet."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "details": self.details,
        }


@dataclass(frozen=True)
class AuthorityCandidate:
    candidate_id: str
    kind: str
    priority: int
    eligible: bool
    selection_reason: str
    transcript: dict[str, Any] | None
    readback: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "kind": self.kind,
            "priority": self.priority,
            "eligible": self.eligible,
            "selection_reason": self.selection_reason,
            **self.readback,
        }


def load_json(path: str | Path, *, label: str) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourcePacketBlocked(
            f"{label}_unreadable",
            f"{label} must be readable UTF-8 JSON: {source} ({exc})",
        ) from exc
    if not isinstance(payload, dict):
        raise SourcePacketBlocked(
            f"{label}_not_object",
            f"{label} must be a JSON object: {source}",
        )
    return payload


def save_json(payload: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def input_fingerprint(payload: dict[str, Any]) -> str:
    return canonical_sha256(
        {
            "contract": PACKET_SCHEMA,
            "inputs": payload,
        }
    )


def parse_youtube_json3_caption(
    payload: dict[str, Any],
    *,
    language: str,
    provider_locator: str,
    source_duration_seconds: float | None,
    minimum_coverage_ratio: float = MIN_AUTHORITY_COVERAGE_RATIO,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    events = payload.get("events")
    if not isinstance(events, list):
        raise SourcePacketBlocked(
            "caption_events_missing",
            "youtube-json3 caption payload must contain events[]",
        )
    locator_language = _provider_locator_language(provider_locator)
    if locator_language and _primary_language(locator_language) != _primary_language(language):
        raise SourcePacketBlocked(
            "caption_language_mismatch",
            (
                f"caption locator language {locator_language!r} does not match "
                f"requested language {language!r}"
            ),
        )

    segments: list[dict[str, Any]] = []
    seen_raw_ids: set[str] = set()
    previous_start = -1.0
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise SourcePacketBlocked(
                "caption_event_not_object",
                f"caption event {index} must be an object",
            )
        raw_id = str(event.get("id") or f"event_{index:06d}")
        if raw_id in seen_raw_ids:
            raise SourcePacketBlocked(
                "caption_duplicate_id",
                f"caption event id is duplicated: {raw_id}",
            )
        seen_raw_ids.add(raw_id)
        start_ms = event.get("tStartMs")
        duration_ms = event.get("dDurationMs")
        if not isinstance(start_ms, (int, float)) or not isinstance(
            duration_ms, (int, float)
        ):
            raise SourcePacketBlocked(
                "caption_timing_missing",
                f"caption event {raw_id} requires numeric tStartMs/dDurationMs",
            )
        start = float(start_ms) / 1000.0
        duration = float(duration_ms) / 1000.0
        end = start + duration
        if start < 0 or duration <= 0 or end <= start:
            raise SourcePacketBlocked(
                "caption_time_range_invalid",
                f"caption event {raw_id} must satisfy 0 <= start < end",
            )
        if start < previous_start:
            raise SourcePacketBlocked(
                "caption_order_invalid",
                f"caption event {raw_id} starts before the preceding event",
            )
        previous_start = start
        text = _caption_text(event.get("segs"))
        if not text:
            raise SourcePacketBlocked(
                "caption_text_empty",
                f"caption event {raw_id} has empty text",
            )
        if (
            source_duration_seconds is not None
            and end > source_duration_seconds + SOURCE_DURATION_TOLERANCE_SECONDS
        ):
            raise SourcePacketBlocked(
                "caption_outside_source_duration",
                (
                    f"caption event {raw_id} ends at {end:.3f}s beyond source "
                    f"duration {source_duration_seconds:.3f}s"
                ),
            )
        segments.append(
            {
                "id": f"seg_{index:06d}",
                "start_seconds": round(start, 6),
                "end_seconds": round(end, 6),
                "text": text,
                "confidence": None,
                "speaker": None,
                "review_status": "unreviewed",
                "notes": [
                    f"source_caption_event_id={raw_id}",
                    f"source_caption_event_index={index}",
                ],
            }
        )

    coverage = timed_segment_coverage(
        segments,
        source_duration_seconds=source_duration_seconds,
    )
    if not segments:
        raise SourcePacketBlocked(
            "caption_segments_empty",
            "caption payload does not contain usable text events",
        )
    if (
        source_duration_seconds is not None
        and coverage["coverage_ratio"] < minimum_coverage_ratio
    ):
        raise SourcePacketBlocked(
            "caption_coverage_too_low",
            (
                f"caption coverage {coverage['coverage_ratio']:.6f} is below "
                f"minimum {minimum_coverage_ratio:.6f}"
            ),
            details=coverage,
        )
    return segments, {
        "format": "youtube-json3",
        "provider_locator": provider_locator,
        "language": language,
        "event_count": len(events),
        "segment_count": len(segments),
        **coverage,
    }


def timed_segment_coverage(
    segments: list[dict[str, Any]],
    *,
    source_duration_seconds: float | None,
) -> dict[str, Any]:
    intervals: list[tuple[float, float]] = []
    for segment in segments:
        start = segment.get("start_seconds")
        end = segment.get("end_seconds")
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            intervals.append((float(start), float(end)))
    intervals.sort()
    covered = 0.0
    merged: list[list[float]] = []
    for start, end in intervals:
        if end <= start:
            continue
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    covered = sum(end - start for start, end in merged)
    duration = float(source_duration_seconds or 0.0)
    return {
        "covered_seconds": round(covered, 6),
        "source_duration_seconds": round(duration, 6) if duration else None,
        "coverage_ratio": round(covered / duration, 9) if duration > 0 else None,
        "interval_count": len(merged),
    }


def validate_timed_segments(
    segments: list[dict[str, Any]],
    *,
    source_duration_seconds: float,
) -> list[str]:
    issues: list[str] = []
    previous_start = -1.0
    seen_ids: set[str] = set()
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            issues.append(f"segments[{index}] must be an object")
            continue
        segment_id = str(segment.get("id") or "")
        if not segment_id:
            issues.append(f"segments[{index}].id is required")
        elif segment_id in seen_ids:
            issues.append(f"segments[{index}].id is duplicated: {segment_id}")
        seen_ids.add(segment_id)
        start = segment.get("start_seconds")
        end = segment.get("end_seconds")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            issues.append(f"segments[{index}] requires numeric timing")
            continue
        start_f = float(start)
        end_f = float(end)
        if start_f < 0 or end_f <= start_f:
            issues.append(f"segments[{index}] has invalid timing")
        if start_f < previous_start:
            issues.append(f"segments[{index}] is out of order")
        if end_f > source_duration_seconds + SOURCE_DURATION_TOLERANCE_SECONDS:
            issues.append(f"segments[{index}] exceeds source duration")
        previous_start = start_f
        text = segment.get("text")
        if not isinstance(text, str) or not text.strip():
            issues.append(f"segments[{index}].text is required")
    return issues


def caption_authority_candidate(
    *,
    authority_kind: str,
    caption_path: Path,
    caption_sha256: str,
    caption_segments: list[dict[str, Any]],
    caption_readback: dict[str, Any],
    episode_id: str,
    language: str,
    source_audio: dict[str, Any],
) -> AuthorityCandidate:
    priority_by_kind = {
        "provider_official": (300, "official_provider_caption"),
        "verified_sidecar": (250, "verified_caption_sidecar"),
    }
    if authority_kind not in priority_by_kind:
        raise SourcePacketBlocked(
            "caption_authority_kind_invalid",
            f"unsupported caption authority kind: {authority_kind}",
        )
    priority, kind = priority_by_kind[authority_kind]
    transcript = build_transcript(
        episode_id,
        source_audio_path=str(source_audio["path"]),
        material_id=str(source_audio["material_id"]),
        source_audio_sha256=str(source_audio["sha256"]),
        source_audio_duration_seconds=float(source_audio["duration_seconds"]),
        source_audio_sample_rate_hz=int(source_audio["sample_rate_hz"]),
        source_audio_channels=int(source_audio["channels"]),
        language=language,
        stt_engine="subtitle_track",
        stt_provider="youtube_subtitles",
        stt_engine_version="youtube-json3",
        stt_model=display_path(caption_path, Path.cwd()),
        stt_params={
            "authority_kind": authority_kind,
            "caption_sha256": caption_sha256,
            "provider_locator": caption_readback["provider_locator"],
            "official_authorship_claim": False,
        },
        stt_warnings=[
            "provider caption text/timing is transcript authority, not production subtitle acceptance",
            "speaker, singing, lyric, and proper-name meaning are not inferred",
        ],
        segments=caption_segments,
        real_transcript=True,
    )
    transcript["review"] = {
        "status": "needs_review",
        "reviewed_by": None,
        "reviewed_at": None,
        "notes": [
            "Normalized from provider caption events without semantic rewriting.",
            "Editorial, rights, production, and public acceptance remain separate.",
        ],
    }
    return AuthorityCandidate(
        candidate_id=f"caption:{authority_kind}",
        kind=kind,
        priority=priority,
        eligible=not validate_transcript(transcript),
        selection_reason=(
            "provider caption has the highest configured eligible authority priority"
            if authority_kind == "provider_official"
            else "verified caption sidecar outranks real STT"
        ),
        transcript=transcript,
        readback={
            "path": display_path(caption_path, Path.cwd()),
            "sha256": caption_sha256,
            **caption_readback,
            "official_authorship_claim": False,
        },
    )


def transcript_authority_candidate(
    *,
    transcript: dict[str, Any],
    transcript_path: Path,
    transcript_sha256: str,
    language: str,
    source_audio_sha256: str,
    source_duration_seconds: float,
    episode_id: str,
    source_audio: dict[str, Any],
) -> AuthorityCandidate:
    schema_issues = validate_transcript(transcript)
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    real = stt.get("real_transcript") is True
    engine = str(stt.get("engine") or "")
    provider = str(stt.get("provider") or "")
    ineligible_engine = engine in {"fake", "fixture", "deterministic_fake"} or provider in {
        "fake",
        "fixture",
        "deterministic_fake",
    }
    language_matches = _primary_language(str(transcript.get("language") or "")) == _primary_language(
        language
    )
    transcript_audio = transcript.get("source_audio")
    transcript_audio_sha = (
        str(transcript_audio.get("sha256") or "")
        if isinstance(transcript_audio, dict)
        else ""
    )
    audio_matches = transcript_audio_sha == source_audio_sha256
    segments = transcript.get("segments") if isinstance(transcript.get("segments"), list) else []
    timing_issues = validate_timed_segments(
        segments,
        source_duration_seconds=source_duration_seconds,
    )
    coverage = timed_segment_coverage(
        segments,
        source_duration_seconds=source_duration_seconds,
    )
    coverage_ok = (
        coverage["coverage_ratio"] is not None
        and coverage["coverage_ratio"] >= MIN_AUTHORITY_COVERAGE_RATIO
    )
    eligible = (
        not schema_issues
        and real
        and not ineligible_engine
        and language_matches
        and audio_matches
        and not timing_issues
        and coverage_ok
    )
    kind = (
        "verified_imported_subtitle_transcript"
        if engine == "subtitle_track"
        else "configured_real_stt"
    )
    priority = 200 if engine == "subtitle_track" else 100
    reasons: list[str] = []
    if schema_issues:
        reasons.append("schema_invalid")
    if not real or ineligible_engine:
        reasons.append("not_real_authority")
    if not language_matches:
        reasons.append("language_mismatch")
    if not audio_matches:
        reasons.append("source_audio_sha_mismatch")
    reasons.extend(timing_issues)
    if not coverage_ok:
        reasons.append("coverage_too_low")

    normalized_segments = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            continue
        source_id = str(segment.get("id") or f"segment_{index + 1}")
        copied = dict(segment)
        copied["notes"] = [
            *(
                list(segment.get("notes"))
                if isinstance(segment.get("notes"), list)
                else []
            ),
            f"source_transcript_segment_id={source_id}",
        ]
        normalized_segments.append(copied)
    normalized: dict[str, Any] | None = None
    if eligible:
        normalized = build_transcript(
            episode_id,
            source_audio_path=str(source_audio["path"]),
            material_id=str(source_audio["material_id"]),
            source_audio_sha256=str(source_audio["sha256"]),
            source_audio_duration_seconds=float(source_audio["duration_seconds"]),
            source_audio_sample_rate_hz=int(source_audio["sample_rate_hz"]),
            source_audio_channels=int(source_audio["channels"]),
            language=language,
            stt_engine=engine,
            stt_provider=provider,
            stt_engine_version=str(stt.get("engine_version") or "unknown"),
            stt_model=stt.get("model"),
            stt_params={
                **(stt.get("params") if isinstance(stt.get("params"), dict) else {}),
                "source_transcript_sha256": transcript_sha256,
            },
            stt_warnings=list(stt.get("warnings") or []),
            segments=normalized_segments,
            real_transcript=True,
        )
        normalized["review"] = {
            "status": "needs_review",
            "reviewed_by": None,
            "reviewed_at": None,
            "notes": [
                "Real transcript normalized without changing utterance text.",
                "Editorial, rights, production, and public acceptance remain separate.",
            ],
        }
    return AuthorityCandidate(
        candidate_id=f"transcript:{kind}",
        kind=kind,
        priority=priority,
        eligible=eligible,
        selection_reason=(
            "eligible real transcript selected because no higher-priority caption authority exists"
            if eligible
            else "ineligible: " + "; ".join(reasons)
        ),
        transcript=normalized,
        readback={
            "path": display_path(transcript_path, Path.cwd()),
            "sha256": transcript_sha256,
            "language": transcript.get("language"),
            "engine": engine,
            "provider": provider,
            "real_transcript": real,
            "source_audio_sha256": transcript_audio_sha or None,
            "segment_count": len(segments),
            **coverage,
            "schema_issues": [
                f"{issue.code}@{issue.field}" for issue in schema_issues
            ],
            "timing_issues": timing_issues,
        },
    )


def choose_authority(
    candidates: list[AuthorityCandidate],
) -> AuthorityCandidate:
    eligible = [
        candidate
        for candidate in candidates
        if candidate.eligible and candidate.transcript is not None
    ]
    if not eligible:
        raise SourcePacketBlocked(
            "transcript_authority_missing",
            "no eligible provider caption, verified sidecar, or configured real STT authority",
            details={"candidates": [candidate.to_dict() for candidate in candidates]},
        )
    return sorted(eligible, key=lambda candidate: candidate.priority, reverse=True)[0]


def build_packet(
    *,
    packet_id: str,
    episode_id: str,
    created_at: str,
    input_fingerprint_value: str,
    source: dict[str, Any],
    acquisition: dict[str, Any],
    materials: dict[str, Any],
    rights: dict[str, Any],
    candidates: list[AuthorityCandidate],
    selected: AuthorityCandidate,
    normalized_transcript_path: Path,
    artifact_manifest: list[dict[str, Any]],
    warnings: list[str],
) -> dict[str, Any]:
    if selected.transcript is None:
        raise SourcePacketBlocked(
            "selected_authority_transcript_missing",
            "selected authority does not contain a normalized transcript",
        )
    duration = float(source["duration_seconds"])
    transcript_issues = validate_transcript(selected.transcript)
    timing_issues = validate_timed_segments(
        selected.transcript.get("segments") or [],
        source_duration_seconds=duration,
    )
    coverage = timed_segment_coverage(
        selected.transcript.get("segments") or [],
        source_duration_seconds=duration,
    )
    if transcript_issues or timing_issues:
        raise SourcePacketBlocked(
            "normalized_transcript_invalid",
            "normalized transcript failed packet validation",
            details={
                "schema_issues": [
                    f"{issue.code}@{issue.field}" for issue in transcript_issues
                ],
                "timing_issues": timing_issues,
            },
        )
    if (
        coverage["coverage_ratio"] is None
        or coverage["coverage_ratio"] < MIN_AUTHORITY_COVERAGE_RATIO
    ):
        raise SourcePacketBlocked(
            "normalized_transcript_coverage_too_low",
            "normalized transcript coverage is insufficient for edit-ready consumers",
            details=coverage,
        )
    packet = {
        "packet_schema": PACKET_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "packet_id": packet_id,
        "episode_id": episode_id,
        "state": READY_STATE,
        "created_at": created_at,
        "input_fingerprint": input_fingerprint_value,
        "source": source,
        "acquisition": acquisition,
        "materials": materials,
        "rights": rights,
        "transcript_candidates": [candidate.to_dict() for candidate in candidates],
        "authority": {
            "selected_candidate_id": selected.candidate_id,
            "kind": selected.kind,
            "selection_reason": selected.selection_reason,
            "priority": selected.priority,
            "fixture_authority_allowed": False,
        },
        "normalized_transcript": {
            "path": display_path(normalized_transcript_path, Path.cwd()),
            "segment_count": len(selected.transcript.get("segments") or []),
            "language": selected.transcript.get("language"),
            **coverage,
            "source_mapping": "segment notes retain source caption event or transcript segment IDs",
        },
        "warnings": warnings,
        "blocking_reason": None,
        "consumer_readiness": {
            "ready": True,
            "state": READY_STATE,
            "consumers": {
                "editorial_planning": "ready",
                "timeline_ir_generation": "ready",
                "subtitle_processing": "ready",
                "render_pipeline": "ready",
            },
        },
        "artifact_manifest": artifact_manifest,
        "acceptance_boundaries": {
            "human_editorial_review": "pending_separate_gate",
            "editorial_acceptance": False,
            "rights_approval": False,
            "production_acceptance": False,
            "public_or_publishing_readiness": False,
            "upload_attempted": False,
        },
    }
    packet["packet_integrity"] = {
        "algorithm": "sha256",
        "canonical_payload_sha256": canonical_sha256(packet),
    }
    return packet


def validate_packet(packet: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if packet.get("packet_schema") != PACKET_SCHEMA:
        issues.append(f"packet_schema must be {PACKET_SCHEMA}")
    if packet.get("schema_version") != SCHEMA_VERSION:
        issues.append("schema_version must be v1")
    if packet.get("state") != READY_STATE:
        issues.append(f"state must be {READY_STATE}")
    if not packet.get("packet_id"):
        issues.append("packet_id is required")
    fingerprint = str(packet.get("input_fingerprint") or "")
    if not SHA256_RE.fullmatch(fingerprint):
        issues.append("input_fingerprint must be a SHA-256 digest")
    source = packet.get("source")
    if not isinstance(source, dict):
        issues.append("source must be an object")
    else:
        if not SHA256_RE.fullmatch(str(source.get("sha256") or "")):
            issues.append("source.sha256 must be a SHA-256 digest")
        if not isinstance(source.get("duration_seconds"), (int, float)) or float(
            source.get("duration_seconds") or 0
        ) <= 0:
            issues.append("source.duration_seconds must be positive")
        if not source.get("resolution"):
            issues.append("source.resolution is required")
    authority = packet.get("authority")
    if not isinstance(authority, dict) or not authority.get("selected_candidate_id"):
        issues.append("authority.selected_candidate_id is required")
    normalized = packet.get("normalized_transcript")
    if not isinstance(normalized, dict):
        issues.append("normalized_transcript must be an object")
    else:
        if not normalized.get("path"):
            issues.append("normalized_transcript.path is required")
        if not isinstance(normalized.get("segment_count"), int) or normalized.get(
            "segment_count", 0
        ) <= 0:
            issues.append("normalized_transcript.segment_count must be positive")
    readiness = packet.get("consumer_readiness")
    if not isinstance(readiness, dict) or readiness.get("ready") is not True:
        issues.append("consumer_readiness.ready must be true")
    boundaries = packet.get("acceptance_boundaries")
    if not isinstance(boundaries, dict):
        issues.append("acceptance_boundaries must be an object")
    else:
        for key in (
            "editorial_acceptance",
            "rights_approval",
            "production_acceptance",
            "public_or_publishing_readiness",
            "upload_attempted",
        ):
            if boundaries.get(key) is not False:
                issues.append(f"acceptance_boundaries.{key} must be false")
    integrity = packet.get("packet_integrity")
    if not isinstance(integrity, dict):
        issues.append("packet_integrity must be an object")
    else:
        expected = str(integrity.get("canonical_payload_sha256") or "")
        payload = dict(packet)
        payload.pop("packet_integrity", None)
        actual = canonical_sha256(payload)
        if expected != actual:
            issues.append("packet_integrity canonical payload digest mismatch")
    return issues


def validate_packet_files(
    packet: dict[str, Any],
    *,
    base_dir: Path,
) -> list[str]:
    issues: list[str] = []
    manifest = packet.get("artifact_manifest")
    if not isinstance(manifest, list):
        return ["artifact_manifest must be an array"]
    seen: set[str] = set()
    for index, item in enumerate(manifest):
        if not isinstance(item, dict):
            issues.append(f"artifact_manifest[{index}] must be an object")
            continue
        path_text = str(item.get("path") or "")
        expected = str(item.get("sha256") or "")
        if not path_text:
            issues.append(f"artifact_manifest[{index}].path is required")
            continue
        if path_text in seen:
            issues.append(f"artifact_manifest path duplicated: {path_text}")
        seen.add(path_text)
        path = Path(path_text)
        if not path.is_absolute():
            path = base_dir / path
        if not path.exists() or not path.is_file():
            issues.append(f"artifact missing: {path_text}")
            continue
        if not SHA256_RE.fullmatch(expected):
            issues.append(f"artifact digest invalid: {path_text}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            issues.append(f"artifact digest mismatch: {path_text}")
    return issues


def blocked_result(
    *,
    packet_id: str,
    episode_id: str,
    input_fingerprint_value: str | None,
    error: SourcePacketBlocked,
) -> dict[str, Any]:
    return {
        "packet_schema": PACKET_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "packet_id": packet_id,
        "episode_id": episode_id,
        "state": BLOCKED_STATE,
        "input_fingerprint": input_fingerprint_value,
        "blocking_reason": error.to_dict(),
        "consumer_readiness": {
            "ready": False,
            "state": BLOCKED_STATE,
            "consumers": {
                "editorial_planning": "blocked",
                "timeline_ir_generation": "blocked",
                "subtitle_processing": "blocked",
                "render_pipeline": "blocked",
            },
        },
        "acceptance_boundaries": {
            "human_editorial_review": "pending_separate_gate",
            "editorial_acceptance": False,
            "rights_approval": False,
            "production_acceptance": False,
            "public_or_publishing_readiness": False,
            "upload_attempted": False,
        },
    }


def render_report_html(packet: dict[str, Any]) -> str:
    source = packet["source"]
    authority = packet["authority"]
    transcript = packet["normalized_transcript"]
    rights = packet["rights"]
    warnings = "".join(
        f"<li>{html.escape(str(warning))}</li>" for warning in packet.get("warnings") or []
    )
    consumers = "".join(
        "<tr>"
        f"<td>{html.escape(str(name))}</td>"
        f"<td>{html.escape(str(status))}</td>"
        "</tr>"
        for name, status in packet["consumer_readiness"]["consumers"].items()
    )
    candidates = "".join(
        "<tr>"
        f"<td>{html.escape(str(candidate.get('candidate_id')))}</td>"
        f"<td>{html.escape(str(candidate.get('kind')))}</td>"
        f"<td>{html.escape(str(candidate.get('eligible')).lower())}</td>"
        f"<td>{html.escape(str(candidate.get('selection_reason')))}</td>"
        "</tr>"
        for candidate in packet.get("transcript_candidates") or []
    )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>ClipPipeGen Edit-Ready Source Packet</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,'Yu Gothic',sans-serif;margin:24px;background:#f4f6f8;color:#17202a}",
            "main{max-width:1080px;margin:auto}section{background:#fff;border:1px solid #d7dde5;border-radius:10px;padding:18px;margin:16px 0}",
            "table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #e4e8ee;text-align:left;vertical-align:top}",
            "code{overflow-wrap:anywhere}.ready{color:#0b6b3a;font-weight:700}.pending{color:#8a4b00}",
            "</style>",
            "</head>",
            "<body><main>",
            "<h1>Edit-Ready Source Packet</h1>",
            f"<p class=\"ready\">{html.escape(str(packet['state']))}</p>",
            "<section><h2>Packet Identity</h2><table>",
            f"<tr><th>packet</th><td><code>{html.escape(str(packet['packet_id']))}</code></td></tr>",
            f"<tr><th>input fingerprint</th><td><code>{html.escape(str(packet['input_fingerprint']))}</code></td></tr>",
            f"<tr><th>integrity</th><td><code>{html.escape(str(packet['packet_integrity']['canonical_payload_sha256']))}</code></td></tr>",
            "</table></section>",
            "<section><h2>Source</h2><table>",
            f"<tr><th>identity</th><td>{html.escape(str(source['identity']))}</td></tr>",
            f"<tr><th>SHA-256</th><td><code>{html.escape(str(source['sha256']))}</code></td></tr>",
            f"<tr><th>media</th><td>{html.escape(str(source['duration_seconds']))}s / {html.escape(str(source['resolution']))}</td></tr>",
            "</table></section>",
            "<section><h2>Transcript Authority</h2><table>",
            f"<tr><th>selected</th><td>{html.escape(str(authority['kind']))}</td></tr>",
            f"<tr><th>reason</th><td>{html.escape(str(authority['selection_reason']))}</td></tr>",
            f"<tr><th>segments</th><td>{html.escape(str(transcript['segment_count']))}</td></tr>",
            f"<tr><th>coverage</th><td>{html.escape(str(transcript['coverage_ratio']))}</td></tr>",
            "</table><h3>Candidates</h3><table><tr><th>ID</th><th>kind</th><th>eligible</th><th>reason</th></tr>",
            candidates,
            "</table></section>",
            "<section><h2>Consumer Readiness</h2><table><tr><th>consumer</th><th>state</th></tr>",
            consumers,
            "</table></section>",
            "<section><h2>Rights and Acceptance Boundaries</h2>",
            f"<p>Rights snapshot status: <strong class=\"pending\">{html.escape(str(rights['status']))}</strong></p>",
            "<p>Editorial acceptance, production acceptance, rights approval, publishing/public readiness, and upload remain separate closed gates.</p>",
            "</section>",
            f"<section><h2>Warnings</h2><ul>{warnings}</ul></section>",
            "</main></body></html>",
        ]
    )


def display_path(path: str | Path, base_dir: Path) -> str:
    value = Path(path)
    try:
        return str(value.resolve().relative_to(base_dir.resolve())).replace("\\", "/")
    except (OSError, ValueError):
        return str(value).replace("\\", "/")


def _caption_text(segs: Any) -> str:
    if not isinstance(segs, list):
        return ""
    text = "".join(
        str(segment.get("utf8") or "")
        for segment in segs
        if isinstance(segment, dict)
    )
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n+ *", " ", text)
    return text.strip()


def _provider_locator_language(locator: str) -> str | None:
    parts = [part for part in locator.split(":") if part]
    return parts[-1] if len(parts) >= 3 else None


def _primary_language(language: str) -> str:
    return re.split(r"[-_]", language.strip().lower(), maxsplit=1)[0]
