from __future__ import annotations

import copy
import json

import pytest

from src.integrations.render.endpoint_preflight import (
    EndpointPreflightError,
    bind_builder_input,
    build_endpoint_preflight,
    build_endpoint_selection,
    payload_sha256,
    require_ready_for_render,
    validate_builder_input_binding,
)


SHA_A = "a" * 64
SHA_B = "b" * 64


def _spec(*, identity: str = "neutral-recording-alpha", sha256: str = SHA_A) -> dict:
    return {
        "source": {
            "media_path": f"inputs/{identity}.mp4",
            "identity": identity,
            "sha256": sha256,
            "expected_sha256": sha256,
            "duration_seconds": 75.0,
            "frame_rate": 30.0,
        },
        "source_start_seconds": 0.0,
        "proposed_end_seconds": 20.5,
        "search_range": {"start_seconds": 12.0, "end_seconds": 32.0},
        "caption_track": {
            "authority": "official-caption-track",
            "expected_authority": "official-caption-track",
            "source_identity": identity,
            "source_media_sha256": sha256,
            "mapping_complete": True,
            "mapping_gaps": [],
            "cues": [
                {"cue_id": "cue-a", "start_seconds": 10.0, "end_seconds": 12.4},
                {"cue_id": "cue-b", "start_seconds": 14.0, "end_seconds": 16.0},
                {"cue_id": "cue-c", "start_seconds": 19.8, "end_seconds": 21.0},
                {"cue_id": "cue-d", "start_seconds": 23.0, "end_seconds": 24.0},
            ],
        },
        "probe_status": {"frame_ok": True, "audio_ok": True},
        "limits": {
            "min_duration_seconds": 12.0,
            "max_duration_seconds": 60.0,
            "repair_max_extension_seconds": 12.0,
            "caption_guard_seconds": 0.08,
            "caption_gap_min_seconds": 0.2,
            "candidate_limit": 12,
        },
        "observations": [
            {"kind": "pause", "time_seconds": 16.3},
            {"kind": "low_motion", "time_seconds": 18.0},
            {"kind": "high_audio", "time_seconds": 18.1},
            {"kind": "high_motion", "time_seconds": 24.1},
            {"kind": "shot_transition", "time_seconds": 24.5},
        ],
    }


def _observation(preflight: dict, selected_id: str) -> dict:
    selected = next(
        row for row in preflight["candidates"] if row["candidate_id"] == selected_id
    )
    earlier = [
        {
            "candidate_id": row["candidate_id"],
            "reason": "observed utterance or action is still incomplete",
        }
        for row in preflight["candidates"]
        if row["end_seconds"] < selected["end_seconds"]
    ]
    return {
        "last_utterance": "complete",
        "audio": "complete",
        "telop_action_transition": "complete",
        "topic_closure": "complete",
        "unrelated_topic": "not_overrun",
        "earlier_candidate_rejections": earlier,
    }


def _ready_selection(preflight: dict, selected_id: str | None = None) -> dict:
    selected_id = selected_id or preflight["candidates"][0]["candidate_id"]
    return build_endpoint_selection(
        preflight,
        {
            "preflight_sha256": payload_sha256(preflight),
            "selected_candidate_id": selected_id,
            "agent_observation": _observation(preflight, selected_id),
        },
    )


def _codes(rows: list[dict]) -> set[str]:
    return {row["code"] for row in rows}


def test_preflight_excludes_active_cue_and_generates_caption_clear_candidates() -> None:
    result = build_endpoint_preflight(_spec())

    assert result["state"] == "agent_review_required"
    assert result["ready_for_render"] is False
    assert [row["end_seconds"] for row in result["candidates"]] == sorted(
        row["end_seconds"] for row in result["candidates"]
    )
    active = next(
        row for row in result["rejected_candidates"] if row["end_seconds"] == 20.5
    )
    assert "active_caption_crossing" in _codes(active["hard_blocks"])
    assert any(
        "caption_end" in row["signals"] and row["end_seconds"] == 16.08
        for row in result["candidates"]
    )


@pytest.mark.parametrize(
    ("proposed", "expected_code"),
    [(11.9, "duration_below_minimum"), (61.0, "duration_above_maximum")],
)
def test_duration_limits_reject_proposed_endpoint(
    proposed: float, expected_code: str
) -> None:
    spec = _spec()
    spec["proposed_end_seconds"] = proposed
    spec["search_range"] = {"start_seconds": 0.0, "end_seconds": 70.0}
    result = build_endpoint_preflight(spec)
    proposed_row = next(
        row for row in result["rejected_candidates"] if "proposed_end" in row["signals"]
    )

    assert expected_code in _codes(proposed_row["hard_blocks"])


def test_source_eof_and_mapping_gap_fail_closed() -> None:
    eof = _spec()
    eof["search_range"]["end_seconds"] = 76.0
    eof_result = build_endpoint_preflight(eof)
    assert eof_result["state"] == "blocked"
    assert "search_range_outside_source" in _codes(eof_result["hard_blocks"])

    gap = _spec()
    gap["caption_track"]["mapping_gaps"] = [
        {"start_seconds": 17.9, "end_seconds": 18.1}
    ]
    gap_result = build_endpoint_preflight(gap)
    gap_row = next(
        row for row in gap_result["rejected_candidates"] if row["end_seconds"] == 18.0
    )
    assert "caption_mapping_gap" in _codes(gap_row["hard_blocks"])


def test_candidate_order_and_hash_are_deterministic_with_deduplicated_signals() -> None:
    spec = _spec()
    spec["observations"].extend(
        [
            {"kind": "pause", "time_seconds": 16.08},
            {"kind": "pause", "time_seconds": 16.08},
        ]
    )
    first = build_endpoint_preflight(spec)
    second = build_endpoint_preflight(copy.deepcopy(spec))
    row = next(row for row in first["candidates"] if row["end_seconds"] == 16.08)

    assert first == second
    assert payload_sha256(first) == payload_sha256(second)
    assert row["signals"] == ["caption_end", "caption_gap", "pause"]
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


@pytest.mark.parametrize("include_pause", [False, True])
def test_caption_candidates_are_retained_with_or_without_pause(
    include_pause: bool,
) -> None:
    spec = _spec()
    spec["observations"] = [
        row for row in spec["observations"] if row["kind"] != "pause"
    ]
    if include_pause:
        spec["observations"].append({"kind": "pause", "time_seconds": 17.0})
    result = build_endpoint_preflight(spec)

    assert any("caption_end" in row["signals"] for row in result["candidates"])
    assert (
        any("pause" in row["signals"] for row in result["candidates"]) is include_pause
    )


def test_shot_transition_is_candidate_and_high_signals_are_warnings_only() -> None:
    result = build_endpoint_preflight(_spec())
    shot = next(
        row for row in result["candidates"] if "shot_transition" in row["signals"]
    )
    high_audio = next(row for row in result["candidates"] if row["end_seconds"] == 18.0)
    high_motion = next(
        row for row in result["candidates"] if row["end_seconds"] == 24.08
    )

    assert shot["end_seconds"] == pytest.approx(24.466667)
    assert "scene_change_near_endpoint" in _codes(shot["warnings"])
    assert "high_audio_near_endpoint" in _codes(high_audio["warnings"])
    assert "high_motion_near_endpoint" in _codes(high_motion["warnings"])
    assert not high_audio["hard_blocks"]
    assert not high_motion["hard_blocks"]


def test_candidate_outside_override_requires_reason_and_evidence() -> None:
    preflight = build_endpoint_preflight(_spec())
    request = {
        "preflight_sha256": payload_sha256(preflight),
        "selected_end_seconds": 25.0,
        "agent_observation": {
            "last_utterance": "complete",
            "audio": "complete",
            "telop_action_transition": "complete",
            "topic_closure": "complete",
            "unrelated_topic": "not_overrun",
            "earlier_candidate_rejections": [
                {"candidate_id": row["candidate_id"], "reason": "still incomplete"}
                for row in preflight["candidates"]
                if row["end_seconds"] < 25.0
            ],
        },
    }

    blocked = build_endpoint_selection(preflight, request)
    assert blocked["state"] == "blocked"
    assert {"override_reason_missing", "override_evidence_missing"} <= _codes(
        blocked["hard_blocks"]
    )

    request["override"] = {
        "reason": "the first complete final syllable occurs between supplied signals",
        "evidence": ["endpoint-tail-audio-sha256:1234", "frame:25.000"],
    }
    ready = build_endpoint_selection(preflight, request)
    assert ready["state"] == "ready_for_render"
    assert ready["selected_candidate"]["signals"] == ["agent_override"]


def test_incomplete_agent_observation_and_missing_earlier_reason_block_selection() -> (
    None
):
    preflight = build_endpoint_preflight(_spec())
    selected = preflight["candidates"][2]
    observation = _observation(preflight, selected["candidate_id"])
    observation["audio"] = "ambiguous"
    observation["earlier_candidate_rejections"] = []
    result = build_endpoint_selection(
        preflight,
        {
            "preflight_sha256": payload_sha256(preflight),
            "selected_candidate_id": selected["candidate_id"],
            "agent_observation": observation,
        },
    )

    assert result["state"] == "blocked"
    assert {
        "agent_observation_incomplete_or_ambiguous",
        "earlier_candidate_reason_missing",
    } <= _codes(result["hard_blocks"])


def test_builder_binding_blocks_stale_preflight_selection_and_input() -> None:
    preflight = build_endpoint_preflight(_spec())
    selection = _ready_selection(preflight)
    bound = bind_builder_input(
        {
            "candidate": {
                "source_end_seconds": selection["selected_candidate"]["end_seconds"]
            }
        },
        preflight,
        selection,
    )
    assert validate_builder_input_binding(bound, preflight, selection)[
        "ready_for_render"
    ]
    require_ready_for_render(bound, preflight, selection)

    changed_input = copy.deepcopy(bound)
    changed_input["candidate"]["source_end_seconds"] += 0.5
    input_result = validate_builder_input_binding(changed_input, preflight, selection)
    assert "endpoint_binding_builder_input_sha256_mismatch" in _codes(
        input_result["hard_blocks"]
    )
    with pytest.raises(EndpointPreflightError, match="not ready for render"):
        require_ready_for_render(changed_input, preflight, selection)

    changed_preflight = copy.deepcopy(preflight)
    changed_preflight["warnings"].append({"code": "new", "message": "changed"})
    preflight_result = validate_builder_input_binding(
        bound, changed_preflight, selection
    )
    assert "selection_preflight_sha256_mismatch" in _codes(
        preflight_result["hard_blocks"]
    )

    changed_selection = copy.deepcopy(selection)
    changed_selection["warnings"].append({"code": "new", "message": "changed"})
    selection_result = validate_builder_input_binding(
        bound, preflight, changed_selection
    )
    assert "endpoint_binding_selection_sha256_mismatch" in _codes(
        selection_result["hard_blocks"]
    )


def test_renderer_callback_is_not_reached_before_ready_for_render() -> None:
    preflight = build_endpoint_preflight(_spec())
    blocked_selection = build_endpoint_selection(
        preflight,
        {
            "preflight_sha256": payload_sha256(preflight),
            "selected_candidate_id": preflight["candidates"][0]["candidate_id"],
            "agent_observation": {},
        },
    )
    renderer_calls: list[str] = []

    with pytest.raises(EndpointPreflightError):
        bound = bind_builder_input({}, preflight, blocked_selection)
        require_ready_for_render(bound, preflight, blocked_selection)
        renderer_calls.append("called")

    assert renderer_calls == []


def test_source_contract_mismatches_block_without_path_existence_dependency() -> None:
    spec = _spec(identity="neutral-recording-beta", sha256=SHA_B)
    spec["source"]["media_path"] = "does/not/exist/source.mov"
    spec["source"]["expected_sha256"] = SHA_A
    spec["caption_track"]["expected_authority"] = "different-authority"
    result = build_endpoint_preflight(spec)

    assert result["state"] == "blocked"
    assert {
        "source_media_sha256_mismatch",
        "caption_authority_mismatch",
    } <= _codes(result["hard_blocks"])


def test_caption_binding_mapping_and_probe_failures_are_global_hard_blocks() -> None:
    spec = _spec()
    spec["caption_track"]["source_identity"] = "different-recording"
    spec["caption_track"]["source_media_sha256"] = SHA_B
    spec["caption_track"]["mapping_complete"] = False
    spec["probe_status"] = {"frame_ok": False, "audio_ok": False}
    result = build_endpoint_preflight(spec)

    assert result["state"] == "blocked"
    assert {
        "caption_source_identity_mismatch",
        "caption_source_sha256_mismatch",
        "caption_mapping_incomplete",
        "frame_probe_failed",
        "audio_probe_failed",
    } <= _codes(result["hard_blocks"])


def test_no_caption_clear_candidate_blocks_preflight() -> None:
    spec = _spec()
    spec["proposed_end_seconds"] = 15.0
    spec["search_range"] = {"start_seconds": 12.0, "end_seconds": 18.0}
    spec["caption_track"]["cues"] = [
        {"cue_id": "continuous", "start_seconds": 11.0, "end_seconds": 19.0}
    ]
    spec["observations"] = [
        {"kind": "pause", "time_seconds": 14.0},
        {"kind": "low_motion", "time_seconds": 17.0},
    ]
    result = build_endpoint_preflight(spec)

    assert result["state"] == "blocked"
    assert "no_caption_clear_candidate" in _codes(result["hard_blocks"])
    assert result["candidates"] == []
    assert all(
        "active_caption_crossing" in _codes(row["hard_blocks"])
        or "candidate_outside_search_range" in _codes(row["hard_blocks"])
        for row in result["rejected_candidates"]
    )


def test_selection_request_preflight_sha_mismatch_blocks() -> None:
    preflight = build_endpoint_preflight(_spec())
    selected = preflight["candidates"][0]
    result = build_endpoint_selection(
        preflight,
        {
            "preflight_sha256": SHA_B,
            "selected_candidate_id": selected["candidate_id"],
            "agent_observation": _observation(preflight, selected["candidate_id"]),
        },
    )

    assert result["state"] == "blocked"
    assert "preflight_sha256_mismatch" in _codes(result["hard_blocks"])


@pytest.mark.parametrize(
    ("identity", "sha256"),
    [("neutral-alpha", SHA_A), ("neutral-beta", SHA_B)],
)
def test_same_contract_behavior_for_multiple_source_neutral_fixtures(
    identity: str, sha256: str
) -> None:
    result = build_endpoint_preflight(_spec(identity=identity, sha256=sha256))

    assert result["state"] == "agent_review_required"
    assert [row["end_seconds"] for row in result["candidates"]][:3] == [
        12.48,
        16.08,
        16.3,
    ]
    assert identity in result["input"]["source"]["identity"]
