"""Source-neutral endpoint preflight and render-input binding helpers.

This module evaluates observations produced elsewhere.  It does not inspect
media, call FFmpeg, choose a creative endpoint, or grant acceptance.  Its job
is to remove mechanically invalid cut points and require an explicit Agent
selection before a renderer may be called.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any


PREFLIGHT_SCHEMA_VERSION = "clippipegen.endpoint_preflight.v0"
SELECTION_SCHEMA_VERSION = "clippipegen.endpoint_selection.v0"
BINDING_SCHEMA_VERSION = "clippipegen.endpoint_builder_binding.v0"

STATE_BLOCKED = "blocked"
STATE_AGENT_REVIEW_REQUIRED = "agent_review_required"
STATE_READY_FOR_RENDER = "ready_for_render"

_SHA256 = re.compile(r"[0-9a-f]{64}")
_SIGNAL_ORDER = {
    "proposed_end": 0,
    "caption_end": 1,
    "caption_gap": 2,
    "pause": 3,
    "low_motion": 4,
    "shot_transition": 5,
    "agent_override": 6,
}
_OBSERVATION_KINDS = {
    "pause",
    "low_motion",
    "high_motion",
    "high_audio",
    "shot_transition",
}
_AGENT_OBSERVATION_EXPECTATIONS = {
    "last_utterance": "complete",
    "audio": "complete",
    "telop_action_transition": "complete",
    "topic_closure": "complete",
    "unrelated_topic": "not_overrun",
}


class EndpointPreflightError(ValueError):
    """Raised for malformed contracts or a failed render-readiness guard."""


def payload_sha256(payload: Any) -> str:
    """Return a deterministic SHA-256 for a JSON-compatible payload."""

    try:
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise EndpointPreflightError(
            "payload must contain only finite JSON-compatible values"
        ) from exc
    return hashlib.sha256(encoded).hexdigest()


def build_endpoint_preflight(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one observation set and return early-ordered endpoint options.

    The result never selects an endpoint.  Eligible candidates are ordered by
    time, with stable signal/reason ordering, and the state remains
    ``agent_review_required`` until :func:`build_endpoint_selection` succeeds.
    """

    normalized = _normalize_spec(spec)
    global_blocks = _global_blocks(normalized)
    warning_context = _warning_context(normalized)
    candidate_points = _candidate_points(normalized)

    assessed = [
        _assess_candidate(
            end_seconds=end_seconds,
            signals=signals,
            normalized=normalized,
            warning_context=warning_context,
        )
        for end_seconds, signals in sorted(candidate_points.items())
    ]
    eligible_all = [row for row in assessed if not row["hard_blocks"]]
    rejected = [row for row in assessed if row["hard_blocks"]]
    candidate_limit = normalized["limits"]["candidate_limit"]
    eligible = eligible_all[:candidate_limit]

    top_warnings: list[dict[str, Any]] = []
    if len(eligible_all) > candidate_limit:
        top_warnings.append(
            _issue(
                "candidate_limit_applied",
                f"{len(eligible_all) - candidate_limit} later eligible candidates omitted",
            )
        )
    if not eligible_all:
        global_blocks.append(
            _issue(
                "no_caption_clear_candidate",
                "no mechanically eligible caption-clear endpoint candidate exists",
            )
        )

    _assign_candidate_ids(eligible, prefix="endpoint")
    _assign_candidate_ids(rejected, prefix="rejected-endpoint")
    state = STATE_BLOCKED if global_blocks else STATE_AGENT_REVIEW_REQUIRED
    return {
        "schema_version": PREFLIGHT_SCHEMA_VERSION,
        "state": state,
        "ready_for_render": False,
        "selection_required": True,
        "input_sha256": payload_sha256(normalized),
        "input": normalized,
        "hard_blocks": _dedupe_issues(global_blocks),
        "warnings": _dedupe_issues(top_warnings),
        "candidates": eligible,
        "rejected_candidates": rejected,
        "candidate_count_before_limit": len(eligible_all),
        "selection_policy": {
            "order": "earliest_source_time_first",
            "automatic_selection": False,
            "agent_must_select_first_semantically_complete_candidate": True,
        },
    }


def build_endpoint_selection(
    preflight: Mapping[str, Any], request: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply an explicit Agent observation and endpoint selection.

    A time outside ``preflight.candidates`` is permitted only as an explicit
    override with both a non-empty reason and evidence.  Mechanical endpoint
    constraints still apply to overrides.
    """

    _require_mapping(preflight, "preflight")
    _require_mapping(request, "selection request")
    normalized = _selection_request(request)
    actual_preflight_sha = payload_sha256(preflight)
    blocks: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        raise EndpointPreflightError("unsupported endpoint preflight schema")
    if normalized["preflight_sha256"] != actual_preflight_sha:
        blocks.append(
            _issue(
                "preflight_sha256_mismatch",
                "selection is not bound to the supplied preflight payload",
            )
        )
    if preflight.get("state") == STATE_BLOCKED or preflight.get("hard_blocks"):
        blocks.append(
            _issue(
                "preflight_blocked",
                "the endpoint preflight contains unresolved hard blocks",
            )
        )

    candidates = _candidate_rows(preflight.get("candidates"), "preflight candidates")
    rejected = _candidate_rows(
        preflight.get("rejected_candidates"), "preflight rejected candidates"
    )
    selected = _find_candidate(candidates, normalized["selected_candidate_id"])
    rejected_selection = _find_candidate(rejected, normalized["selected_candidate_id"])
    override = normalized["override"]

    if selected is not None:
        if normalized["selected_end_seconds"] is not None and not math.isclose(
            normalized["selected_end_seconds"],
            selected["end_seconds"],
            abs_tol=1e-6,
        ):
            blocks.append(
                _issue(
                    "selected_end_mismatch",
                    "selected endpoint time does not match the candidate identity",
                )
            )
    elif rejected_selection is not None:
        selected = copy.deepcopy(rejected_selection)
        blocks.append(
            _issue(
                "selected_candidate_ineligible",
                "the selected candidate has mechanical hard blocks",
            )
        )
    else:
        selected, override_blocks = _build_override_candidate(
            preflight=preflight,
            normalized_request=normalized,
        )
        blocks.extend(override_blocks)
        if selected is not None:
            warnings.append(
                _issue(
                    "candidate_outside_preflight_overridden",
                    "Agent selected an evidenced endpoint outside the candidate list",
                )
            )

    observation_blocks = _agent_observation_blocks(normalized["agent_observation"])
    blocks.extend(observation_blocks)
    if selected is not None:
        blocks.extend(
            _earlier_candidate_blocks(
                candidates=candidates,
                selected_end_seconds=selected["end_seconds"],
                observation=normalized["agent_observation"],
            )
        )
        blocks.extend(selected.get("hard_blocks") or [])
        warnings.extend(selected.get("warnings") or [])

    blocks = _dedupe_issues(blocks)
    warnings = _dedupe_issues(warnings)
    ready = selected is not None and not blocks
    state = STATE_READY_FOR_RENDER if ready else STATE_BLOCKED
    return {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "state": state,
        "ready_for_render": ready,
        "preflight_sha256": actual_preflight_sha,
        "requested_preflight_sha256": normalized["preflight_sha256"],
        "selected_candidate": selected,
        "agent_observation": normalized["agent_observation"],
        "override": override,
        "hard_blocks": blocks,
        "warnings": warnings,
        "automatic_selection": False,
    }


def bind_builder_input(
    builder_input: Mapping[str, Any],
    preflight: Mapping[str, Any],
    selection: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a copy of builder input bound to exact preflight/selection hashes."""

    _require_mapping(builder_input, "builder input")
    _require_selection_ready(preflight, selection)
    unbound = copy.deepcopy(dict(builder_input))
    unbound.pop("endpoint_binding", None)
    binding = {
        "schema_version": BINDING_SCHEMA_VERSION,
        "preflight_sha256": payload_sha256(preflight),
        "selection_sha256": payload_sha256(selection),
        "builder_input_sha256": payload_sha256(unbound),
        "source_media_sha256": preflight["input"]["source"]["sha256"],
        "source_start_seconds": preflight["input"]["source_start_seconds"],
        "selected_end_seconds": selection["selected_candidate"]["end_seconds"],
    }
    bound = copy.deepcopy(unbound)
    bound["endpoint_binding"] = binding
    return bound


def validate_builder_input_binding(
    builder_input: Mapping[str, Any],
    preflight: Mapping[str, Any],
    selection: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate render readiness and exact binding without calling a renderer."""

    _require_mapping(builder_input, "builder input")
    blocks: list[dict[str, Any]] = []
    if preflight.get("state") == STATE_BLOCKED or preflight.get("hard_blocks"):
        blocks.append(_issue("preflight_blocked", "endpoint preflight is blocked"))
    if selection.get("state") != STATE_READY_FOR_RENDER or not selection.get(
        "ready_for_render"
    ):
        blocks.append(
            _issue("selection_not_ready", "endpoint selection is not ready for render")
        )
    actual_preflight_sha = payload_sha256(preflight)
    actual_selection_sha = payload_sha256(selection)
    if selection.get("preflight_sha256") != actual_preflight_sha:
        blocks.append(
            _issue(
                "selection_preflight_sha256_mismatch",
                "selection no longer matches the endpoint preflight",
            )
        )

    binding = builder_input.get("endpoint_binding")
    if not isinstance(binding, Mapping):
        blocks.append(
            _issue("endpoint_binding_missing", "builder input has no endpoint binding")
        )
        binding = {}
    unbound = copy.deepcopy(dict(builder_input))
    unbound.pop("endpoint_binding", None)
    expected = {
        "schema_version": BINDING_SCHEMA_VERSION,
        "preflight_sha256": actual_preflight_sha,
        "selection_sha256": actual_selection_sha,
        "builder_input_sha256": payload_sha256(unbound),
        "source_media_sha256": preflight.get("input", {})
        .get("source", {})
        .get("sha256"),
        "source_start_seconds": preflight.get("input", {}).get("source_start_seconds"),
        "selected_end_seconds": (selection.get("selected_candidate") or {}).get(
            "end_seconds"
        ),
    }
    for field, expected_value in expected.items():
        if binding.get(field) != expected_value:
            blocks.append(
                _issue(
                    f"endpoint_binding_{field}_mismatch",
                    f"builder endpoint binding field {field} does not match",
                )
            )
    blocks = _dedupe_issues(blocks)
    ready = not blocks
    return {
        "state": STATE_READY_FOR_RENDER if ready else STATE_BLOCKED,
        "ready_for_render": ready,
        "hard_blocks": blocks,
        "preflight_sha256": actual_preflight_sha,
        "selection_sha256": actual_selection_sha,
        "builder_input_sha256": payload_sha256(unbound),
    }


def require_ready_for_render(
    builder_input: Mapping[str, Any],
    preflight: Mapping[str, Any],
    selection: Mapping[str, Any],
) -> None:
    """Fail closed unless the exact builder input is ready for render."""

    result = validate_builder_input_binding(builder_input, preflight, selection)
    if not result["ready_for_render"]:
        codes = ", ".join(row["code"] for row in result["hard_blocks"])
        raise EndpointPreflightError(f"endpoint is not ready for render: {codes}")


def _normalize_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    _require_mapping(spec, "endpoint preflight spec")
    source = _require_mapping(spec.get("source"), "source")
    captions = _require_mapping(spec.get("caption_track"), "caption_track")
    search_range = _require_mapping(spec.get("search_range"), "search_range")
    probe_status = _require_mapping(spec.get("probe_status"), "probe_status")
    limits_raw = spec.get("limits") or {}
    limits_mapping = _require_mapping(limits_raw, "limits")

    identity = _text(source.get("identity"), "source identity")
    path = _text(source.get("media_path"), "source media_path")
    sha256 = _sha(source.get("sha256"), "source sha256")
    expected_sha256 = _sha(source.get("expected_sha256"), "source expected_sha256")
    duration = _positive_number(source.get("duration_seconds"), "source duration")
    frame_rate = _positive_number(source.get("frame_rate"), "source frame_rate")
    source_start = _nonnegative_number(
        spec.get("source_start_seconds"), "source_start_seconds"
    )
    proposed_end = _optional_number(
        spec.get("proposed_end_seconds"), "proposed_end_seconds"
    )

    limits = {
        "min_duration_seconds": _positive_number(
            limits_mapping.get("min_duration_seconds", 12.0),
            "limits min_duration_seconds",
        ),
        "max_duration_seconds": _positive_number(
            limits_mapping.get("max_duration_seconds", 60.0),
            "limits max_duration_seconds",
        ),
        "repair_max_extension_seconds": _optional_positive_number(
            limits_mapping.get("repair_max_extension_seconds"),
            "limits repair_max_extension_seconds",
        ),
        "caption_guard_seconds": _nonnegative_number(
            limits_mapping.get("caption_guard_seconds", 0.08),
            "limits caption_guard_seconds",
        ),
        "caption_gap_min_seconds": _nonnegative_number(
            limits_mapping.get("caption_gap_min_seconds", 0.20),
            "limits caption_gap_min_seconds",
        ),
        "short_next_cue_warning_seconds": _nonnegative_number(
            limits_mapping.get("short_next_cue_warning_seconds", 0.50),
            "limits short_next_cue_warning_seconds",
        ),
        "warning_proximity_seconds": _nonnegative_number(
            limits_mapping.get("warning_proximity_seconds", 0.50),
            "limits warning_proximity_seconds",
        ),
        "candidate_limit": _positive_int(
            limits_mapping.get("candidate_limit", 12), "limits candidate_limit"
        ),
    }
    if limits["min_duration_seconds"] >= limits["max_duration_seconds"]:
        raise EndpointPreflightError(
            "limits min_duration_seconds must be less than max_duration_seconds"
        )

    cues = _normalize_cues(captions.get("cues"))
    gaps = _normalize_intervals(captions.get("mapping_gaps", []), "mapping gap")
    observations = _normalize_observations(spec.get("observations", []))
    return {
        "source": {
            "media_path": path,
            "identity": identity,
            "sha256": sha256,
            "expected_sha256": expected_sha256,
            "duration_seconds": duration,
            "frame_rate": frame_rate,
        },
        "source_start_seconds": source_start,
        "proposed_end_seconds": proposed_end,
        "search_range": {
            "start_seconds": _nonnegative_number(
                search_range.get("start_seconds"), "search range start"
            ),
            "end_seconds": _positive_number(
                search_range.get("end_seconds"), "search range end"
            ),
        },
        "caption_track": {
            "authority": _text(captions.get("authority"), "caption authority"),
            "expected_authority": _text(
                captions.get("expected_authority"), "caption expected_authority"
            ),
            "source_identity": _text(
                captions.get("source_identity"), "caption source_identity"
            ),
            "source_media_sha256": _sha(
                captions.get("source_media_sha256"),
                "caption source_media_sha256",
            ),
            "mapping_complete": _boolean(
                captions.get("mapping_complete"), "caption mapping_complete"
            ),
            "mapping_gaps": gaps,
            "cues": cues,
        },
        "probe_status": {
            "frame_ok": _boolean(probe_status.get("frame_ok"), "frame probe status"),
            "audio_ok": _boolean(probe_status.get("audio_ok"), "audio probe status"),
        },
        "limits": limits,
        "observations": observations,
    }


def _normalize_cues(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or not raw:
        raise EndpointPreflightError("caption cues must be a non-empty list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        cue = _require_mapping(item, f"caption cue {index}")
        cue_id = _text(cue.get("cue_id"), f"caption cue {index} cue_id")
        if cue_id in seen:
            raise EndpointPreflightError(f"duplicate caption cue_id: {cue_id}")
        seen.add(cue_id)
        start = _nonnegative_number(
            cue.get("start_seconds"), f"caption cue {cue_id} start"
        )
        end = _positive_number(cue.get("end_seconds"), f"caption cue {cue_id} end")
        if end <= start:
            raise EndpointPreflightError(
                f"caption cue {cue_id} must have positive duration"
            )
        result.append({"cue_id": cue_id, "start_seconds": start, "end_seconds": end})
    return sorted(
        result,
        key=lambda row: (row["start_seconds"], row["end_seconds"], row["cue_id"]),
    )


def _normalize_intervals(raw: Any, label: str) -> list[dict[str, float]]:
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise EndpointPreflightError(f"{label}s must be a list")
    result = []
    for index, item in enumerate(raw):
        interval = _require_mapping(item, f"{label} {index}")
        start = _nonnegative_number(interval.get("start_seconds"), f"{label} start")
        end = _positive_number(interval.get("end_seconds"), f"{label} end")
        if end <= start:
            raise EndpointPreflightError(f"{label} must have positive duration")
        result.append({"start_seconds": start, "end_seconds": end})
    return sorted(result, key=lambda row: (row["start_seconds"], row["end_seconds"]))


def _normalize_observations(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise EndpointPreflightError("observations must be a list")
    result = []
    for index, item in enumerate(raw):
        observation = _require_mapping(item, f"observation {index}")
        kind = _text(observation.get("kind"), f"observation {index} kind")
        if kind not in _OBSERVATION_KINDS:
            raise EndpointPreflightError(
                f"unsupported endpoint observation kind: {kind}"
            )
        result.append(
            {
                "kind": kind,
                "time_seconds": _nonnegative_number(
                    observation.get("time_seconds"),
                    f"observation {index} time_seconds",
                ),
            }
        )
    return sorted(result, key=lambda row: (row["time_seconds"], row["kind"]))


def _global_blocks(normalized: Mapping[str, Any]) -> list[dict[str, Any]]:
    source = normalized["source"]
    captions = normalized["caption_track"]
    search_range = normalized["search_range"]
    blocks: list[dict[str, Any]] = []
    if source["sha256"] != source["expected_sha256"]:
        blocks.append(
            _issue("source_media_sha256_mismatch", "source media hash mismatch")
        )
    if captions["source_media_sha256"] != source["sha256"]:
        blocks.append(
            _issue(
                "caption_source_sha256_mismatch", "caption track source hash mismatch"
            )
        )
    if captions["source_identity"] != source["identity"]:
        blocks.append(
            _issue(
                "caption_source_identity_mismatch",
                "caption track source identity mismatch",
            )
        )
    if captions["authority"] != captions["expected_authority"]:
        blocks.append(
            _issue(
                "caption_authority_mismatch",
                "caption authority does not match expectation",
            )
        )
    if not captions["mapping_complete"]:
        blocks.append(
            _issue("caption_mapping_incomplete", "caption source mapping is incomplete")
        )
    if not normalized["probe_status"]["frame_ok"]:
        blocks.append(_issue("frame_probe_failed", "frame endpoint probe failed"))
    if not normalized["probe_status"]["audio_ok"]:
        blocks.append(_issue("audio_probe_failed", "audio endpoint probe failed"))
    if (
        search_range["start_seconds"] < normalized["source_start_seconds"]
        or search_range["end_seconds"] > source["duration_seconds"]
        or search_range["end_seconds"] <= search_range["start_seconds"]
    ):
        blocks.append(
            _issue(
                "search_range_outside_source",
                "endpoint search range is outside source media",
            )
        )
    for cue in captions["cues"]:
        if cue["end_seconds"] > source["duration_seconds"]:
            blocks.append(
                _issue(
                    "caption_mapping_outside_source",
                    "caption cue exceeds source media EOF",
                )
            )
            break
    return blocks


def _candidate_points(normalized: Mapping[str, Any]) -> dict[float, set[str]]:
    points: dict[float, set[str]] = {}
    proposed = normalized["proposed_end_seconds"]
    if proposed is not None:
        _add_point(points, proposed, "proposed_end")
    cues = normalized["caption_track"]["cues"]
    guard = normalized["limits"]["caption_guard_seconds"]
    gap_min = normalized["limits"]["caption_gap_min_seconds"]
    for index, cue in enumerate(cues):
        point = cue["end_seconds"] + guard
        _add_point(points, point, "caption_end")
        next_cue = cues[index + 1] if index + 1 < len(cues) else None
        if (
            next_cue is None
            or next_cue["start_seconds"] - cue["end_seconds"] >= gap_min
        ):
            _add_point(points, point, "caption_gap")
    frame_seconds = 1.0 / normalized["source"]["frame_rate"]
    for observation in normalized["observations"]:
        kind = observation["kind"]
        if kind in {"pause", "low_motion"}:
            _add_point(points, observation["time_seconds"], kind)
        elif kind == "shot_transition":
            _add_point(
                points,
                max(
                    normalized["source_start_seconds"],
                    observation["time_seconds"] - frame_seconds,
                ),
                "shot_transition",
            )
    return points


def _assess_candidate(
    *,
    end_seconds: float,
    signals: set[str],
    normalized: Mapping[str, Any],
    warning_context: Mapping[str, Any],
) -> dict[str, Any]:
    end_seconds = _rounded(end_seconds)
    source_start = normalized["source_start_seconds"]
    duration = _rounded(end_seconds - source_start)
    limits = normalized["limits"]
    search_range = normalized["search_range"]
    blocks: list[dict[str, Any]] = []
    if (
        end_seconds < search_range["start_seconds"]
        or end_seconds > search_range["end_seconds"]
    ):
        blocks.append(
            _issue(
                "candidate_outside_search_range", "candidate is outside search range"
            )
        )
    if end_seconds > normalized["source"]["duration_seconds"]:
        blocks.append(
            _issue("candidate_outside_source", "candidate exceeds source media EOF")
        )
    if duration < limits["min_duration_seconds"]:
        blocks.append(
            _issue(
                "duration_below_minimum", "candidate is shorter than minimum duration"
            )
        )
    if duration > limits["max_duration_seconds"]:
        blocks.append(
            _issue("duration_above_maximum", "candidate exceeds maximum duration")
        )
    proposed = normalized["proposed_end_seconds"]
    max_extension = limits["repair_max_extension_seconds"]
    if (
        proposed is not None
        and max_extension is not None
        and end_seconds > proposed + max_extension
    ):
        blocks.append(
            _issue(
                "repair_extension_exceeded", "candidate exceeds repair extension budget"
            )
        )
    guard = limits["caption_guard_seconds"]
    cues = normalized["caption_track"]["cues"]
    if any(
        cue["start_seconds"] - guard < end_seconds < cue["end_seconds"] + guard
        for cue in cues
    ):
        blocks.append(
            _issue(
                "active_caption_crossing", "candidate crosses an active caption guard"
            )
        )
    for gap in normalized["caption_track"]["mapping_gaps"]:
        if gap["start_seconds"] <= end_seconds <= gap["end_seconds"]:
            blocks.append(
                _issue(
                    "caption_mapping_gap",
                    "candidate falls inside a caption mapping gap",
                )
            )
            break

    warnings = _candidate_warnings(end_seconds, normalized, warning_context)
    return {
        "candidate_id": None,
        "end_seconds": end_seconds,
        "duration_seconds": duration,
        "signals": sorted(signals, key=lambda value: (_SIGNAL_ORDER[value], value)),
        "eligible": not blocks,
        "hard_blocks": _dedupe_issues(blocks),
        "warnings": warnings,
    }


def _warning_context(normalized: Mapping[str, Any]) -> dict[str, list[float]]:
    result = {"high_audio": [], "high_motion": [], "shot_transition": []}
    for row in normalized["observations"]:
        if row["kind"] in result:
            result[row["kind"]].append(row["time_seconds"])
    return result


def _candidate_warnings(
    end_seconds: float,
    normalized: Mapping[str, Any],
    warning_context: Mapping[str, Sequence[float]],
) -> list[dict[str, Any]]:
    proximity = normalized["limits"]["warning_proximity_seconds"]
    warnings: list[dict[str, Any]] = []
    for kind, code, message in (
        ("high_audio", "high_audio_near_endpoint", "high audio observed near endpoint"),
        (
            "high_motion",
            "high_motion_near_endpoint",
            "high motion observed near endpoint",
        ),
        (
            "shot_transition",
            "scene_change_near_endpoint",
            "scene change observed near endpoint",
        ),
    ):
        if any(
            abs(point - end_seconds) <= proximity for point in warning_context[kind]
        ):
            warnings.append(_issue(code, message))
    next_cue = next(
        (
            cue
            for cue in normalized["caption_track"]["cues"]
            if cue["start_seconds"] >= end_seconds
        ),
        None,
    )
    if next_cue is not None and (
        next_cue["start_seconds"] - end_seconds
        <= normalized["limits"]["short_next_cue_warning_seconds"]
    ):
        warnings.append(
            _issue(
                "next_caption_near_endpoint",
                "next caption starts shortly after endpoint",
            )
        )
    return _dedupe_issues(warnings)


def _selection_request(request: Mapping[str, Any]) -> dict[str, Any]:
    observation_raw = request.get("agent_observation") or {}
    observation = _require_mapping(observation_raw, "agent_observation")
    normalized_observation = {
        field: str(observation.get(field) or "")
        for field in _AGENT_OBSERVATION_EXPECTATIONS
    }
    rejections = observation.get("earlier_candidate_rejections") or []
    if not isinstance(rejections, Sequence) or isinstance(rejections, (str, bytes)):
        raise EndpointPreflightError("earlier_candidate_rejections must be a list")
    normalized_rejections = []
    for index, raw in enumerate(rejections):
        row = _require_mapping(raw, f"earlier candidate rejection {index}")
        normalized_rejections.append(
            {
                "candidate_id": _text(
                    row.get("candidate_id"), "earlier rejection candidate_id"
                ),
                "reason": _text(row.get("reason"), "earlier rejection reason"),
            }
        )
    normalized_observation["earlier_candidate_rejections"] = sorted(
        normalized_rejections, key=lambda row: row["candidate_id"]
    )

    override_raw = request.get("override")
    override = None
    if override_raw is not None:
        override_mapping = _require_mapping(override_raw, "override")
        evidence = override_mapping.get("evidence") or []
        if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)):
            raise EndpointPreflightError("override evidence must be a list")
        override = {
            "reason": str(override_mapping.get("reason") or "").strip(),
            "evidence": copy.deepcopy(list(evidence)),
        }
    return {
        "preflight_sha256": str(request.get("preflight_sha256") or "").lower(),
        "selected_candidate_id": str(
            request.get("selected_candidate_id") or ""
        ).strip(),
        "selected_end_seconds": _optional_number(
            request.get("selected_end_seconds"), "selected_end_seconds"
        ),
        "agent_observation": normalized_observation,
        "override": override,
    }


def _build_override_candidate(
    *,
    preflight: Mapping[str, Any],
    normalized_request: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    blocks: list[dict[str, Any]] = []
    override = normalized_request["override"]
    end_seconds = normalized_request["selected_end_seconds"]
    if end_seconds is None:
        blocks.append(
            _issue(
                "selected_candidate_missing",
                "no endpoint candidate or override time selected",
            )
        )
        return None, blocks
    if not override or not override["reason"]:
        blocks.append(
            _issue("override_reason_missing", "candidate override requires a reason")
        )
    if (
        not override
        or not override["evidence"]
        or not all(_nonempty_evidence(row) for row in override["evidence"])
    ):
        blocks.append(
            _issue("override_evidence_missing", "candidate override requires evidence")
        )
    normalized = preflight.get("input")
    if not isinstance(normalized, Mapping):
        raise EndpointPreflightError("preflight input snapshot is missing")
    selected = _assess_candidate(
        end_seconds=end_seconds,
        signals={"agent_override"},
        normalized=normalized,
        warning_context=_warning_context(normalized),
    )
    selected["candidate_id"] = "agent-override"
    return selected, blocks


def _agent_observation_blocks(observation: Mapping[str, Any]) -> list[dict[str, Any]]:
    blocks = []
    for field, expected in _AGENT_OBSERVATION_EXPECTATIONS.items():
        actual = observation.get(field)
        if actual != expected:
            blocks.append(
                _issue(
                    "agent_observation_incomplete_or_ambiguous",
                    f"Agent observation {field} must be {expected}; got {actual or 'missing'}",
                )
            )
    return blocks


def _earlier_candidate_blocks(
    *,
    candidates: Sequence[Mapping[str, Any]],
    selected_end_seconds: float,
    observation: Mapping[str, Any],
) -> list[dict[str, Any]]:
    reasons = {
        row["candidate_id"]: row["reason"]
        for row in observation["earlier_candidate_rejections"]
    }
    blocks = []
    for candidate in candidates:
        if candidate["end_seconds"] >= selected_end_seconds - 1e-6:
            continue
        if not reasons.get(candidate["candidate_id"]):
            blocks.append(
                _issue(
                    "earlier_candidate_reason_missing",
                    f"no rejection reason for earlier candidate {candidate['candidate_id']}",
                )
            )
    return blocks


def _require_selection_ready(
    preflight: Mapping[str, Any], selection: Mapping[str, Any]
) -> None:
    if preflight.get("state") == STATE_BLOCKED or preflight.get("hard_blocks"):
        raise EndpointPreflightError("cannot bind builder input to a blocked preflight")
    if selection.get("state") != STATE_READY_FOR_RENDER or not selection.get(
        "ready_for_render"
    ):
        raise EndpointPreflightError(
            "cannot bind builder input to an unready selection"
        )
    if selection.get("preflight_sha256") != payload_sha256(preflight):
        raise EndpointPreflightError("selection preflight SHA-256 mismatch")


def _candidate_rows(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise EndpointPreflightError(f"{label} must be a list")
    rows = []
    for index, item in enumerate(value):
        row = _require_mapping(item, f"{label} {index}")
        rows.append(copy.deepcopy(dict(row)))
    return rows


def _find_candidate(
    candidates: Sequence[Mapping[str, Any]], candidate_id: str
) -> dict[str, Any] | None:
    if not candidate_id:
        return None
    return next(
        (
            copy.deepcopy(dict(row))
            for row in candidates
            if row.get("candidate_id") == candidate_id
        ),
        None,
    )


def _assign_candidate_ids(rows: Sequence[dict[str, Any]], *, prefix: str) -> None:
    for index, row in enumerate(rows, start=1):
        row["candidate_id"] = f"{prefix}-{index:03d}"


def _add_point(points: dict[float, set[str]], seconds: float, signal: str) -> None:
    points.setdefault(_rounded(seconds), set()).add(signal)


def _dedupe_issues(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["code"]), str(row["message"]))
        unique[key] = {"code": key[0], "message": key[1]}
    return [unique[key] for key in sorted(unique)]


def _issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _rounded(value: float) -> float:
    return round(float(value), 6)


def _nonempty_evidence(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value) and all(
            not isinstance(item, str) or bool(item.strip()) for item in value.values()
        )
    return False


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EndpointPreflightError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EndpointPreflightError(f"{label} must be a non-empty string")
    return value.strip()


def _sha(value: Any, label: str) -> str:
    sha = _text(value, label).lower()
    if not _SHA256.fullmatch(sha):
        raise EndpointPreflightError(f"{label} must be a lowercase SHA-256")
    return sha


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EndpointPreflightError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise EndpointPreflightError(f"{label} must be a finite number")
    return _rounded(result)


def _positive_number(value: Any, label: str) -> float:
    result = _number(value, label)
    if result <= 0:
        raise EndpointPreflightError(f"{label} must be greater than zero")
    return result


def _nonnegative_number(value: Any, label: str) -> float:
    result = _number(value, label)
    if result < 0:
        raise EndpointPreflightError(f"{label} must be non-negative")
    return result


def _optional_number(value: Any, label: str) -> float | None:
    return None if value is None else _number(value, label)


def _optional_positive_number(value: Any, label: str) -> float | None:
    return None if value is None else _positive_number(value, label)


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise EndpointPreflightError(f"{label} must be a positive integer")
    return value


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise EndpointPreflightError(f"{label} must be boolean")
    return value
