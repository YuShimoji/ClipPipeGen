"""CPD-08 operator cockpit home / funnel UX builder.

This module consolidates the CPD-01 through CPD-05 planning artifacts into one
operator-facing entry point. It only reads local JSON artifacts and writes
review surfaces; it never opens source URLs, fetches media, creates episode
folders, generates transcripts/renders, or changes rights/publication state.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from .content_planning import display_path, write_json, write_text

SCHEMA_ID = "clippipegen.operator_cockpit.v0"
DEFAULT_ARTIFACT_ID = "clip-cpd08-operator-home-funnel-meters-v0-001"
DEFAULT_GENERATED_AT = "2026-07-06"
DEFAULT_OUTPUT_FILENAME = "operator_cockpit.json"
DEFAULT_DASHBOARD_FILENAME = "operator_cockpit.html"
HTML_TITLE = "ClipPipeGen Operator Cockpit / Content Planning Review"
UX_VERSION = "v3_home_funnel_meters_v0"

NOT_YET_FLAGS = [
    "fetch",
    "transcript",
    "render",
    "public",
    "rights",
]

INTERNAL_ARTIFACTS = [
    {
        "path": "docs/content_planning/content_dashboard.html",
        "purpose": "CPD-01 candidate scoring and channel strategy readback",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/content_candidates.json",
        "purpose": "CPD-01 normalized candidate machine data",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/channel_strategy.json",
        "purpose": "CPD-01 strategy machine data",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/episode_seed_dashboard.html",
        "purpose": "CPD-02 episode seed draft readback",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/episode_seed_drafts.json",
        "purpose": "CPD-02 episode seed draft machine data",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/source_resolution_dashboard.html",
        "purpose": "CPD-03 source URL resolution readback",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/episode_seed_source_resolution.json",
        "purpose": "CPD-03 source URL resolution machine data",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/source_metadata_registry.template.json",
        "purpose": "CPD-03 blank manual source intake template",
        "audience": "operator intake after real source identification",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/episode_init_plan_dashboard.html",
        "purpose": "CPD-04 dry-run episode init plan readback",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/episode_init_plan.json",
        "purpose": "CPD-04 dry-run episode init plan machine data",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/source_inspection_packet_dashboard.html",
        "purpose": "CPD-05 source inspection packet readback",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/source_inspection_packet.json",
        "purpose": "CPD-05 source inspection packet machine data",
        "audience": "internal pipeline/debug readback",
        "open_by_default": False,
    },
    {
        "path": "docs/content_planning/source_inspection_decisions.template.json",
        "purpose": "CPD-05 blank post-human-inspection decision template",
        "audience": "operator intake after real source inspection",
        "open_by_default": False,
    },
]


class OperatorCockpitError(ValueError):
    """Raised when CPD-06 inputs cannot be consolidated."""


def build_operator_cockpit(
    *,
    candidates_path: Path,
    seed_path: Path,
    source_resolution_path: Path,
    episode_init_plan_path: Path,
    source_inspection_packet_path: Path,
    decision_template_path: Path,
    output_path: Path,
    dashboard_path: Path,
    base_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Read CPD planning outputs and write one operator-facing cockpit."""

    candidates_payload = load_json_object(candidates_path, "content candidates")
    seed_payload = load_json_object(seed_path, "episode seed drafts")
    resolution_payload = load_json_object(source_resolution_path, "source resolution")
    init_plan_payload = load_json_object(episode_init_plan_path, "episode init plan")
    inspection_payload = load_json_object(source_inspection_packet_path, "source inspection packet")
    decision_template_payload = load_json_object(decision_template_path, "source inspection decisions template")

    candidates = required_list(candidates_payload, "candidates", "content candidates")
    seeds = required_list(seed_payload, "episode_seed_drafts", "episode seed drafts")
    resolutions = required_list(
        resolution_payload,
        "source_resolution_records",
        "source resolution",
    )
    init_plans = required_list(init_plan_payload, "episode_init_plans", "episode init plan")
    skipped_init_records = required_list(
        init_plan_payload,
        "skipped_source_records",
        "episode init plan",
    )
    inspection_packets = required_list(
        inspection_payload,
        "source_inspection_packets",
        "source inspection packet",
    )
    blocked_inspection_records = required_list(
        inspection_payload,
        "blocked_source_records",
        "source inspection packet",
    )
    decision_entries = required_list(decision_template_payload, "entries", "source inspection decisions template")

    candidate_index = by_id(candidates, "candidate_id")
    seed_index = by_id(seeds, "seed_id")
    resolution_index = by_id(resolutions, "seed_id")

    source_backed = [
        source_backed_record(
            packet,
            candidate=candidate_index.get(clean_string(packet.get("candidate_id"))),
            seed=seed_index.get(clean_string(packet.get("seed_id"))),
            resolution=resolution_index.get(clean_string(packet.get("seed_id"))),
        )
        for packet in inspection_packets
        if is_source_backed_packet(packet)
    ]

    blocked_or_hold: list[dict[str, Any]] = []
    source_missing_ideas: list[dict[str, Any]] = []
    for resolution in resolutions:
        if clean_string(resolution.get("source_url_state")) != "missing":
            continue
        candidate_id = clean_string(resolution.get("candidate_id"))
        seed_id = clean_string(resolution.get("seed_id"))
        seed = seed_index.get(seed_id)
        candidate = candidate_index.get(candidate_id)
        if is_blocked_or_hold_record(resolution, seed=seed, candidate=candidate):
            blocked_or_hold.append(blocked_or_hold_record(resolution, seed=seed, candidate=candidate))
        else:
            source_missing_ideas.append(source_missing_record(resolution, seed=seed, candidate=candidate))

    internal_artifacts = [
        {
            **artifact,
            "exists": (base_dir / artifact["path"]).exists(),
        }
        for artifact in INTERNAL_ARTIFACTS
    ]
    summary = summary_counts(
        candidates=candidates,
        seeds=seeds,
        resolutions=resolutions,
        source_backed=source_backed,
        source_missing_ideas=source_missing_ideas,
        blocked_or_hold=blocked_or_hold,
        inspection_payload=inspection_payload,
        decision_entries=decision_entries,
        internal_artifacts=internal_artifacts,
    )
    recommended_next_action = build_recommended_next_action(summary)
    gates = build_gate_readback(
        inspection_payload=inspection_payload,
        init_plan_payload=init_plan_payload,
        source_backed=source_backed,
    )
    section_links = build_section_links()
    home_metrics = build_home_metrics(summary=summary, gates=gates)
    funnel_stages = build_funnel_stages(summary=summary)
    action_queue = build_action_queue(summary=summary)
    generated_from = generated_from_records(
        candidates_path=candidates_path,
        seed_path=seed_path,
        source_resolution_path=source_resolution_path,
        episode_init_plan_path=episode_init_plan_path,
        source_inspection_packet_path=source_inspection_packet_path,
        decision_template_path=decision_template_path,
        candidates_payload=candidates_payload,
        seed_payload=seed_payload,
        resolution_payload=resolution_payload,
        init_plan_payload=init_plan_payload,
        inspection_payload=inspection_payload,
        decision_template_payload=decision_template_payload,
        base_dir=base_dir,
    )

    payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "title": HTML_TITLE,
        "ux": {
            "version": UX_VERSION,
            "layout": "operator_home_funnel_meters",
            "default_theme": "dark",
            "theme_toggle": True,
            "developer_appendix_default": "collapsed",
            "home_area": "visible",
            "action_queue": "visible",
        },
        "source": {
            "network_required": False,
            "source_opened_by_worker": False,
            "input_artifacts": {
                "content_candidates": display_path(candidates_path, base_dir),
                "episode_seed_drafts": display_path(seed_path, base_dir),
                "source_resolution": display_path(source_resolution_path, base_dir),
                "episode_init_plan": display_path(episode_init_plan_path, base_dir),
                "source_inspection_packet": display_path(source_inspection_packet_path, base_dir),
                "source_inspection_decisions_template": display_path(decision_template_path, base_dir),
            },
        },
        "human_review": {
            "primary_message": "今、人間が確認する動画は 1 件だけです。",
            "secondary_message": "残り 4 件は元動画未特定の企画メモであり、動画候補として扱いません。",
            "operator_open_first": display_path(dashboard_path, base_dir),
            "user_work": recommended_next_action["user_work"],
        },
        "summary": summary,
        "home_metrics": home_metrics,
        "funnel_stages": funnel_stages,
        "action_queue": action_queue,
        "section_links": section_links,
        "recommended_next_action": recommended_next_action,
        "gate_readback": gates,
        "buckets": {
            "source_backed_ready_for_human_inspection": source_backed,
            "source_missing_idea_backlog": source_missing_ideas,
            "blocked_or_hold": blocked_or_hold,
            "internal_pipeline_artifact_only": internal_artifacts,
        },
        "generated_from": generated_from,
        "readback": {
            "episode_init_plan_count": len(init_plans),
            "skipped_source_record_count": len(skipped_init_records),
            "blocked_source_record_count": len(blocked_inspection_records),
            "decision_template_entry_count": len(decision_entries),
            "note": (
                "CPD-08 is an operator-home information architecture layer over CPD-01 through CPD-05. "
                "It does not change source, fetch, rights, production, or public gates."
            ),
        },
    }

    write_json(payload, output_path)
    write_text(
        render_operator_cockpit_html(
            payload=payload,
            output_path=output_path,
            dashboard_path=dashboard_path,
            base_dir=base_dir,
        ),
        dashboard_path,
    )
    return {
        "artifact_id": artifact_id,
        "output_path": output_path,
        "dashboard_path": dashboard_path,
        "payload": payload,
    }


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise OperatorCockpitError(f"{label} JSON is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OperatorCockpitError(f"{label} JSON is not valid: {path}") from exc
    if not isinstance(payload, dict):
        raise OperatorCockpitError(f"{label} JSON root must be an object")
    return payload


def required_list(payload: dict[str, Any], key: str, label: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise OperatorCockpitError(f"{label} JSON must contain {key}[]")
    return [item for item in value if isinstance(item, dict)]


def by_id(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {
        clean_string(item.get(key)): item
        for item in items
        if clean_string(item.get(key))
    }


def is_source_backed_packet(packet: dict[str, Any]) -> bool:
    return (
        clean_string(packet.get("source_url_state")) == "present"
        and bool(clean_string(packet.get("source_url")))
        and packet.get("fetch_authorized") is False
        and packet.get("rights_approved") is False
        and packet.get("production_ready") is False
        and packet.get("public_ready") is False
    )


def source_backed_record(
    packet: dict[str, Any],
    *,
    candidate: dict[str, Any] | None,
    seed: dict[str, Any] | None,
    resolution: dict[str, Any] | None,
) -> dict[str, Any]:
    rights = packet.get("rights_readback") if isinstance(packet.get("rights_readback"), dict) else {}
    return {
        "candidate_id": clean_string(packet.get("candidate_id")),
        "seed_id": clean_string(packet.get("seed_id")),
        "inspection_packet_id": clean_string(packet.get("inspection_packet_id")),
        "episode_plan_id": clean_string(packet.get("episode_plan_id")),
        "working_title": first_nonempty(
            packet.get("working_title"),
            seed.get("working_title") if seed else "",
            candidate.get("title") if candidate else "",
        ),
        "source_url": clean_string(packet.get("source_url")),
        "video_id": clean_string(packet.get("video_id")),
        "provenance_state": "source_url_present_unreviewed",
        "source_grounding_status": "source_url_present_but_identity_unchecked_by_worker",
        "source_open_state": clean_string(packet.get("source_open_state")) or "not_opened_by_worker",
        "decision_state": clean_string(packet.get("decision_state")) or "pending",
        "human_action": "open_source_url_and_check_identity",
        "recommended_review_question": "Does this source page match the intended clip candidate?",
        "not_yet": list(NOT_YET_FLAGS),
        "fetch_authorized": False,
        "rights_status": clean_string(rights.get("status")) or "unknown",
        "rights_approved": False,
        "production_ready": False,
        "public_ready": False,
        "clip_angle": first_nonempty(
            (packet.get("proposed_clip_scope") or {}).get("clip_angle")
            if isinstance(packet.get("proposed_clip_scope"), dict)
            else "",
            seed.get("clip_angle") if seed else "",
        ),
        "source_resolution_id": clean_string((resolution or {}).get("resolution_id")),
    }


def is_blocked_or_hold_record(
    resolution: dict[str, Any],
    *,
    seed: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
) -> bool:
    actions = " ".join(
        clean_string(value).lower()
        for value in (
            resolution.get("next_action"),
            seed.get("next_action") if seed else "",
            candidate.get("next_action") if candidate else "",
        )
    )
    if any(term in actions for term in ("reject", "hold", "defer")):
        return True
    return any(
        clean_string(flag.get("code")) == "song_or_music_rights_sensitive"
        for flag in risk_flags(resolution, seed=seed, candidate=candidate)
    )


def source_missing_record(
    resolution: dict[str, Any],
    *,
    seed: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "candidate_id": clean_string(resolution.get("candidate_id")),
        "seed_id": clean_string(resolution.get("seed_id")),
        "working_title": first_nonempty(
            resolution.get("working_title"),
            seed.get("working_title") if seed else "",
            candidate.get("title") if candidate else "",
        ),
        "source_ref": clean_string(resolution.get("source_ref")),
        "idea_basis": idea_basis(resolution),
        "source_url_state": "missing",
        "source_metadata_state": clean_string(resolution.get("source_metadata_state")),
        "grounding_status": "not_grounded_to_source",
        "warning": "do_not_treat_as_video-backed_candidate",
        "required_before_progress": required_before_progress(resolution),
        "blocking_reason": clean_string(resolution.get("blocking_reason")),
        "next_action": clean_string(resolution.get("next_action")) or "manual_source_intake_required",
        "risk_flags": risk_flags(resolution, seed=seed, candidate=candidate),
    }


def blocked_or_hold_record(
    resolution: dict[str, Any],
    *,
    seed: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
) -> dict[str, Any]:
    flags = risk_flags(resolution, seed=seed, candidate=candidate)
    return {
        "candidate_id": clean_string(resolution.get("candidate_id")),
        "seed_id": clean_string(resolution.get("seed_id")),
        "working_title": first_nonempty(
            resolution.get("working_title"),
            seed.get("working_title") if seed else "",
            candidate.get("title") if candidate else "",
        ),
        "source_url_state": clean_string(resolution.get("source_url_state")) or "missing",
        "source_metadata_state": clean_string(resolution.get("source_metadata_state")),
        "grounding_status": "not_grounded_to_source",
        "state": "blocked_or_hold",
        "reason": blocked_reason(resolution, seed=seed, flags=flags),
        "required_before_progress": required_before_progress(resolution),
        "next_action": clean_string(resolution.get("next_action")) or "defer_unresolved",
        "risk_flags": flags,
        "warning": "do_not_treat_as_video-backed_candidate",
    }


def risk_flags(
    resolution: dict[str, Any],
    *,
    seed: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    for source in (resolution, seed, candidate):
        flags = source.get("risk_flags") if source else None
        if isinstance(flags, list) and flags:
            return [dict(flag) for flag in flags if isinstance(flag, dict)]
    return []


def idea_basis(resolution: dict[str, Any]) -> str:
    if clean_string(resolution.get("source_ref")):
        return clean_string(resolution.get("source_ref"))
    if clean_string(resolution.get("confidence")):
        return clean_string(resolution.get("confidence"))
    return "manual_idea_without_source_url"


def required_before_progress(resolution: dict[str, Any]) -> list[str]:
    fields = resolution.get("manual_intake_fields_needed")
    if isinstance(fields, list) and fields:
        return [clean_string(field) for field in fields if clean_string(field)]
    return ["source_url", "source_title", "channel_name", "rights_readback_note"]


def blocked_reason(
    resolution: dict[str, Any],
    *,
    seed: dict[str, Any] | None,
    flags: list[dict[str, Any]],
) -> str:
    if any(clean_string(flag.get("code")) == "song_or_music_rights_sensitive" for flag in flags):
        return "song_or_music_rights_sensitive"
    if seed and clean_string(seed.get("next_action")):
        return clean_string(seed.get("next_action"))
    return clean_string(resolution.get("blocking_reason")) or "blocked_or_hold"


def summary_counts(
    *,
    candidates: list[dict[str, Any]],
    seeds: list[dict[str, Any]],
    resolutions: list[dict[str, Any]],
    source_backed: list[dict[str, Any]],
    source_missing_ideas: list[dict[str, Any]],
    blocked_or_hold: list[dict[str, Any]],
    inspection_payload: dict[str, Any],
    decision_entries: list[dict[str, Any]],
    internal_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    inspection_summary = (
        inspection_payload.get("summary")
        if isinstance(inspection_payload.get("summary"), dict)
        else {}
    )
    source_missing_count = sum(
        1 for record in resolutions if clean_string(record.get("source_url_state")) == "missing"
    )
    source_present_count = sum(
        1 for record in resolutions if clean_string(record.get("source_url_state")) == "present"
    )
    fetch_authorized_count = int(inspection_summary.get("fetch_authorized_count") or 0)
    return {
        "total_candidates": len(candidates),
        "total_seed_drafts": len(seeds),
        "source_url_present_count": source_present_count,
        "source_backed_count": len(source_backed),
        "source_missing_count": source_missing_count,
        "source_missing_idea_backlog_count": len(source_missing_ideas),
        "blocked_or_hold_count": len(blocked_or_hold),
        "inspectable_packet_count": int(inspection_summary.get("inspectable_packet_count") or len(source_backed)),
        "decision_template_entry_count": len(decision_entries),
        "fetch_authorized_count": fetch_authorized_count,
        "source_opened_by_worker": bool(inspection_summary.get("source_opened_by_worker")),
        "media_downloaded": bool(inspection_summary.get("media_downloaded")),
        "episode_dirs_created": bool(inspection_summary.get("episode_dirs_created")),
        "internal_artifact_count": len(internal_artifacts),
        "health": "ready_for_single_source_identity_review" if source_backed else "blocked_by_no_source_backed_candidate",
    }


def build_recommended_next_action(summary: dict[str, Any]) -> dict[str, str]:
    if summary["source_backed_count"] > 0:
        return {
            "action_id": "inspect_single_source_backed_item",
            "label": "今回確認する1件を見る",
            "reason": "URL が分かっている候補は 1 件だけです。ほかは元動画未特定の企画メモまたは保留です。",
            "user_work": "open_only",
        }
    if summary["source_missing_count"] > 0:
        return {
            "action_id": "fill_source_urls_for_missing_ideas",
            "label": "未特定の企画メモに source URL を入れる",
            "reason": "確認できる動画候補がまだありません。",
            "user_work": "source_url_intake",
        }
    return {
        "action_id": "defer_all",
        "label": "すべて保留する",
        "reason": "いま確認できる動画候補がありません。",
        "user_work": "none",
    }


def build_gate_readback(
    *,
    inspection_payload: dict[str, Any],
    init_plan_payload: dict[str, Any],
    source_backed: list[dict[str, Any]],
) -> dict[str, Any]:
    inspection_gates = (
        inspection_payload.get("gate_readback")
        if isinstance(inspection_payload.get("gate_readback"), dict)
        else {}
    )
    init_gates = (
        init_plan_payload.get("gate_readback")
        if isinstance(init_plan_payload.get("gate_readback"), dict)
        else {}
    )
    return {
        "source_opened_by_worker": False,
        "network_required": False,
        "external_api_used": False,
        "media_downloaded": False,
        "episode_dirs_created": False,
        "fetch_authorized": False,
        "rights_approved": False,
        "production_ready": False,
        "public_ready": False,
        "transcript_generated": False,
        "render_generated": False,
        "oauth_or_credentials_used": False,
        "source_backed_review_ready_count": len(source_backed),
        "source_inspection_packet_gate_readback": {
            "dry_run": bool(inspection_gates.get("dry_run")),
            "source_opened_by_worker": bool(inspection_gates.get("source_opened_by_worker")),
            "media_downloaded": bool(inspection_gates.get("media_downloaded")),
            "episode_dirs_created": bool(inspection_gates.get("episode_dirs_created")),
        },
        "episode_init_plan_gate_readback": {
            "dry_run": bool(init_gates.get("dry_run")),
            "media_downloaded": bool(init_gates.get("media_downloaded")),
            "episode_dirs_created": bool(init_gates.get("episode_dirs_created")),
        },
    }


def build_section_links() -> list[dict[str, str]]:
    return [
        {"section_id": "primary-review", "label": "\u6b21\u306b\u5224\u65ad\u3059\u308b1\u4ef6", "href": "#primary-review"},
        {"section_id": "source-missing", "label": "source\u672a\u7279\u5b9a\u306e\u4f01\u753b\u30e1\u30e2", "href": "#source-missing"},
        {"section_id": "blocked-hold", "label": "\u4fdd\u7559", "href": "#blocked-hold"},
        {"section_id": "safety-boundary", "label": "\u9589\u3058\u305f\u30b2\u30fc\u30c8", "href": "#safety-boundary"},
        {"section_id": "developer-appendix", "label": "\u958b\u767a\u7528\u8a73\u7d30", "href": "#developer-appendix"},
    ]


def build_home_metrics(*, summary: dict[str, Any], gates: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "metric_id": "total_candidates",
            "label": "\u4f01\u753b\u5019\u88dc",
            "value": summary["total_candidates"],
            "total": summary["total_candidates"],
            "href": "#candidate-state-board",
            "why": "\u624b\u5143\u306b\u3042\u308b\u5019\u88dc\u5168\u4f53\u3067\u3059\u3002",
            "state": "planning_inventory",
            "kind": "measured_count",
        },
        {
            "metric_id": "source_backed",
            "label": "source\u7279\u5b9a\u6e08\u307f",
            "value": summary["source_backed_count"],
            "total": summary["total_candidates"],
            "href": "#primary-review",
            "why": "\u4eba\u9593\u304c\u78ba\u8a8d\u3067\u304d\u308bURL\u4ed8\u304d\u306e\u5019\u88dc\u6570\u3067\u3059\u3002",
            "state": "one_primary_review_target",
            "kind": "measured_count",
        },
        {
            "metric_id": "source_missing_ideas",
            "label": "source\u672a\u7279\u5b9a",
            "value": summary["source_missing_idea_backlog_count"],
            "total": summary["total_candidates"],
            "href": "#source-missing",
            "why": "URL\u304c\u306a\u3044\u305f\u3081\u3001\u307e\u3060\u52d5\u753b\u5019\u88dc\u3068\u3057\u3066\u6271\u3044\u307e\u305b\u3093\u3002",
            "state": "not_video_backed",
            "kind": "measured_count",
        },
        {
            "metric_id": "blocked_or_hold",
            "label": "\u4fdd\u7559",
            "value": summary["blocked_or_hold_count"],
            "total": summary["total_candidates"],
            "href": "#blocked-hold",
            "why": "\u6a29\u5229\u30fb\u97f3\u697d\u30ea\u30b9\u30af\u304c\u5206\u96e2\u3055\u308c\u305f\u5019\u88dc\u3067\u3059\u3002",
            "state": "hold",
            "kind": "measured_count",
        },
        {
            "metric_id": "inspectable_packets",
            "label": "\u4eba\u9593\u78ba\u8a8d\u5f85\u3061",
            "value": summary["inspectable_packet_count"],
            "total": summary["total_candidates"],
            "href": "#primary-review",
            "why": "\u4eca\u958b\u3051\u308b\u78ba\u8a8dpacket\u306f1\u4ef6\u3060\u3051\u3067\u3059\u3002",
            "state": "human_review_waiting",
            "kind": "measured_count",
        },
        {
            "metric_id": "fetch_authorized",
            "label": "\u53d6\u5f97\u8a31\u53ef",
            "value": summary["fetch_authorized_count"],
            "total": summary["total_candidates"],
            "href": "#safety-boundary",
            "why": "0\u306e\u307e\u307e\u306a\u306e\u3067\u3001\u3053\u3053\u306f\u307e\u3060source review\u753b\u9762\u3067\u3059\u3002",
            "state": "locked",
            "kind": "measured_count",
        },
        {
            "metric_id": "media_downloaded",
            "label": "media\u53d6\u5f97",
            "value": int(bool(gates["media_downloaded"])),
            "total": 1,
            "href": "#safety-boundary",
            "why": "\u52d5\u753b\u30fb\u97f3\u58f0\u53d6\u5f97\u306b\u9032\u3093\u3067\u3044\u306a\u3044\u3053\u3068\u3092\u793a\u3057\u307e\u3059\u3002",
            "state": "locked",
            "kind": "gate_count",
        },
        {
            "metric_id": "episode_dirs_created",
            "label": "episode dirs",
            "value": int(bool(gates["episode_dirs_created"])),
            "total": 1,
            "href": "#safety-boundary",
            "why": "real episode init\u306f\u672a\u958b\u59cb\u3067\u3001CPD\u3067\u306fdry-run\u306e\u307f\u3067\u3059\u3002",
            "state": "locked",
            "kind": "gate_count",
        },
    ]


def build_funnel_stages(*, summary: dict[str, Any]) -> list[dict[str, Any]]:
    total = summary["total_candidates"]
    return [
        {
            "stage_id": "idea_candidates",
            "label": "\u4f01\u753b\u5019\u88dc",
            "count": total,
            "total": total,
            "href": "#candidate-state-board",
            "status": "measured",
            "note": "\u5168\u5019\u88dc\u306e\u5165\u53e3\u3002",
        },
        {
            "stage_id": "source_backed",
            "label": "source\u7279\u5b9a\u6e08\u307f",
            "count": summary["source_backed_count"],
            "total": total,
            "href": "#primary-review",
            "status": "one_ready",
            "note": "URL\u4ed8\u304d\u306f1\u4ef6\u3002",
        },
        {
            "stage_id": "human_review_waiting",
            "label": "\u4eba\u9593\u78ba\u8a8d\u5f85\u3061",
            "count": summary["inspectable_packet_count"],
            "total": total,
            "href": "#primary-review",
            "status": "waiting",
            "note": "\u5224\u65ad\u5f85\u3061\u306epacket\u3002",
        },
        {
            "stage_id": "private_local_review_waiting",
            "label": "private/local\u691c\u8a3c\u5f85\u3061",
            "count": summary["fetch_authorized_count"],
            "total": total,
            "href": "#safety-boundary",
            "status": "locked",
            "note": "fetch authorization\u306f0\u3002",
        },
        {
            "stage_id": "edit_render_not_started",
            "label": "\u7de8\u96c6\u30fbrender\u672a\u958b\u59cb",
            "count": 0,
            "total": total,
            "href": "#safety-boundary",
            "status": "locked",
            "note": "render / transcript / public gate\u306f\u672a\u958b\u59cb\u3002",
        },
    ]


def build_action_queue(*, summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "queue_id": "primary_source_identity",
            "priority": "primary",
            "label": "\u756a\u9577/\u8239\u9577\u306eURL\u304c\u5019\u88dc\u610f\u56f3\u3068\u540c\u3058\u52d5\u753b\u304b\u78ba\u8a8d",
            "href": "#primary-review",
            "count": summary["source_backed_count"],
            "state": "actionable_now",
            "why": "source URL\u4ed8\u304d\u3067\u4eca\u5224\u65ad\u3067\u304d\u308b\u5019\u88dc\u306f1\u4ef6\u3060\u3051\u3067\u3059\u3002",
        },
        {
            "queue_id": "secondary_missing_sources",
            "priority": "secondary",
            "label": "source\u672a\u7279\u5b9a\u306e\u4f01\u753b\u30e1\u30e2\u306bURL\u3092\u8db3\u3059",
            "href": "#source-missing",
            "count": summary["source_missing_idea_backlog_count"],
            "state": "backlog",
            "why": "source URL\u304c\u306a\u3044\u305f\u3081\u3001\u4eca\u306f\u52d5\u753b\u5019\u88dc\u3067\u306f\u3042\u308a\u307e\u305b\u3093\u3002",
        },
        {
            "queue_id": "hold_music_rights",
            "priority": "hold",
            "label": "\u6b4c\u30fb\u97f3\u697d\u6a29\u5229\u30ea\u30b9\u30af\u5019\u88dc\u306f\u4fdd\u7559",
            "href": "#blocked-hold",
            "count": summary["blocked_or_hold_count"],
            "state": "hold",
            "why": "\u5225\u306erights/publication route\u304c\u306a\u3044\u307e\u307e\u3067\u306f\u9032\u3081\u307e\u305b\u3093\u3002",
        },
    ]


def generated_from_records(
    *,
    candidates_path: Path,
    seed_path: Path,
    source_resolution_path: Path,
    episode_init_plan_path: Path,
    source_inspection_packet_path: Path,
    decision_template_path: Path,
    candidates_payload: dict[str, Any],
    seed_payload: dict[str, Any],
    resolution_payload: dict[str, Any],
    init_plan_payload: dict[str, Any],
    inspection_payload: dict[str, Any],
    decision_template_payload: dict[str, Any],
    base_dir: Path,
) -> list[dict[str, str]]:
    rows = [
        ("CPD-01", candidates_path, candidates_payload, "candidate planning"),
        ("CPD-02", seed_path, seed_payload, "episode seed draft bridge"),
        ("CPD-03", source_resolution_path, resolution_payload, "source provenance resolution"),
        ("CPD-04", episode_init_plan_path, init_plan_payload, "dry-run init plan"),
        ("CPD-05", source_inspection_packet_path, inspection_payload, "source inspection packet"),
        ("CPD-05-template", decision_template_path, decision_template_payload, "blank source decision template"),
    ]
    return [
        {
            "stage": stage,
            "path": display_path(path, base_dir),
            "schema_id": clean_string(payload.get("schema_id")),
            "artifact_id": clean_string(payload.get("artifact_id")),
            "role": role,
        }
        for stage, path, payload, role in rows
    ]


def render_operator_cockpit_html(
    *,
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    base_dir: Path,
) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja" data-theme="dark">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(HTML_TITLE)}</title>",
            "<style>",
            operator_cockpit_css(),
            "</style>",
            theme_script(),
            "</head>",
            "<body>",
            '<a class="skip-link" href="#primary-review-card">確認カードへ移動</a>',
            _hero_html(payload),
            '<main class="page-shell">',
            _operator_home_html(payload),
            _action_queue_html(payload),
            _primary_review_card_html(payload),
            _candidate_state_board_html(payload),
            _safety_boundary_html(payload),
            _developer_appendix_html(payload, output_path, dashboard_path, base_dir),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def operator_cockpit_css() -> str:
    return """
:root{
  color-scheme:dark;
  --bg:#0f1218;
  --surface:#171c25;
  --surface-2:#202633;
  --surface-3:#273142;
  --text:#f1f5f9;
  --muted:#a8b3c4;
  --border:#344155;
  --accent:#7dd3fc;
  --accent-2:#38bdf8;
  --success:#86efac;
  --warning:#fbbf24;
  --danger:#fca5a5;
  --link:#93c5fd;
  --shadow:0 18px 40px rgba(0,0,0,.28);
}
:root[data-theme="light"]{
  color-scheme:light;
  --bg:#f6f7fb;
  --surface:#ffffff;
  --surface-2:#f0f4f8;
  --surface-3:#e7edf5;
  --text:#172033;
  --muted:#5b6678;
  --border:#d3dbe7;
  --accent:#0369a1;
  --accent-2:#0284c7;
  --success:#13723f;
  --warning:#9a5a00;
  --danger:#a32626;
  --link:#075985;
  --shadow:0 16px 32px rgba(30,41,59,.12);
}
*{box-sizing:border-box}
body{
  margin:0;
  background:var(--bg);
  color:var(--text);
  font-family:system-ui,-apple-system,Segoe UI,'Yu Gothic','Meiryo',sans-serif;
  line-height:1.58;
}
a{color:var(--link);text-decoration-thickness:1px;text-underline-offset:3px}
button{font:inherit}
.skip-link{position:absolute;left:-999px;top:8px;background:var(--surface);color:var(--text);padding:8px;border:1px solid var(--border);border-radius:6px}
.skip-link:focus{left:8px;z-index:20}
.hero{
  border-bottom:1px solid var(--border);
  background:var(--surface);
}
.page-shell,.hero-inner{
  width:min(1040px,calc(100% - 32px));
  margin:0 auto;
}
.hero-inner{padding:22px 0 18px}
.topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
h1,h2,h3,p{margin:0}
h1{font-size:clamp(24px,4vw,36px);line-height:1.18}
h2{font-size:22px;line-height:1.28}
h3{font-size:17px;line-height:1.35}
.subtitle{margin-top:8px;color:var(--muted);max-width:760px}
.theme-toggle{
  min-width:112px;
  border:1px solid var(--border);
  border-radius:8px;
  color:var(--text);
  background:var(--surface-2);
  padding:8px 10px;
  cursor:pointer;
}
.mini-nav{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
.mini-nav a{border:1px solid var(--border);border-radius:999px;padding:5px 10px;background:var(--surface-2);color:var(--text);text-decoration:none;font-size:13px}
main{padding:22px 0 40px}
section{margin:0 0 18px}
.surface,.primary-card{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:8px;
  box-shadow:var(--shadow);
}
.surface{padding:18px}
.verdict-grid{display:grid;grid-template-columns:minmax(0,1fr);gap:12px}
.verdict-line{font-size:20px;font-weight:700}
.home-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(260px,.9fr);gap:14px;align-items:start}
.home-answer{border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:14px}
.home-answer h2{margin-bottom:8px}
.home-answer p{color:var(--muted);margin-top:6px}
.meter-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-top:14px}
.meter-card{display:block;border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:11px;text-decoration:none;color:var(--text)}
.meter-card:hover{border-color:var(--accent)}
.meter-card span{display:block;color:var(--muted);font-size:12px}
.meter-card strong{display:block;font-size:26px;line-height:1.1;margin:3px 0}
.meter-card em{display:block;color:var(--muted);font-size:12px;font-style:normal}
.meter-bar{height:7px;border-radius:999px;background:var(--surface-3);overflow:hidden;margin-top:8px}
.meter-fill{height:100%;border-radius:999px;background:var(--accent)}
.funnel{display:grid;gap:8px;margin-top:12px}
.funnel-step{display:grid;grid-template-columns:34px minmax(0,1fr) auto;gap:10px;align-items:center;border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:10px;text-decoration:none;color:var(--text)}
.funnel-step .index{width:28px;height:28px;border-radius:999px;display:grid;place-items:center;background:var(--surface-3);font-weight:700}
.funnel-step .note{color:var(--muted);font-size:12px}
.funnel-step .count{font-weight:700;color:var(--accent)}
.queue-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.queue-card{border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:14px}
.queue-card.primary{border-color:var(--accent);background:linear-gradient(180deg,var(--surface-2),var(--surface))}
.queue-card.hold{border-color:rgba(251,191,36,.6)}
.queue-card a{display:inline-block;margin-top:10px;font-weight:700}
.state-board{display:grid;gap:12px}
.state-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.state-card{border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:14px}
.anchor-alias{position:relative;top:-16px}
.metric-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-top:14px}
.metric{border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:10px}
.metric span{display:block;color:var(--muted);font-size:12px}
.metric strong{display:block;font-size:24px;line-height:1.15}
.primary-card{padding:0;overflow:hidden}
.card-header{padding:18px;border-bottom:1px solid var(--border);background:var(--surface-2)}
.kicker{color:var(--accent);font-weight:700;font-size:13px;margin-bottom:6px}
.id-line{margin-top:8px;color:var(--muted);font-size:12px;display:flex;gap:8px;flex-wrap:wrap}
.card-body{display:grid;gap:16px;padding:18px}
.review-block{border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:14px}
.review-block h3{margin-bottom:8px}
.source-link{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--border);border-radius:8px;padding:8px 10px;background:var(--surface-3);text-decoration:none;color:var(--text);font-weight:700}
.url-text{display:block;margin-top:8px;color:var(--muted);font-size:13px;overflow-wrap:break-word;word-break:normal}
.question{font-size:18px;font-weight:700}
.checklist{display:grid;gap:8px;margin-top:10px;padding:0;list-style:none}
.checklist li{display:flex;gap:8px;align-items:flex-start}
.checkmark{color:var(--success);font-weight:700}
.decision-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.decision-chip{border:1px solid var(--border);border-radius:8px;background:var(--surface-3);padding:10px}
.decision-chip strong{display:block;margin-bottom:4px}
.ok{color:var(--success)}.warn{color:var(--warning)}.danger{color:var(--danger)}
.locked-list{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.pill{border:1px solid var(--border);border-radius:999px;padding:4px 9px;background:var(--surface-3);font-size:13px;color:var(--text)}
.section-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.section-heading p{color:var(--muted);margin-top:4px}
.idea-list{display:grid;gap:10px;margin-top:12px}
.idea-card{border:1px solid var(--border);border-radius:8px;background:var(--surface-2);padding:12px}
.idea-card .meta{color:var(--muted);font-size:12px;margin-top:4px}
details{border:1px solid var(--border);border-radius:8px;background:var(--surface-2)}
summary{cursor:pointer;padding:12px 14px;font-weight:700}
.details-body{border-top:1px solid var(--border);padding:14px}
.table-scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:720px}
th,td{border-bottom:1px solid var(--border);padding:8px;text-align:left;vertical-align:top}
th{background:var(--surface-3)}
code{background:var(--surface-3);border:1px solid var(--border);border-radius:5px;padding:1px 4px;color:var(--text)}
.muted{color:var(--muted)}
@media (max-width:720px){
  .topbar{display:block}
  .theme-toggle{margin-top:14px}
  .home-grid{grid-template-columns:1fr}
  .page-shell,.hero-inner{width:min(100% - 20px,1040px)}
  .source-link{display:flex;justify-content:center}
}
"""


def theme_script() -> str:
    return """
<script>
(function(){
  const key = "clippipegen.operatorCockpit.theme";
  const root = document.documentElement;
  const saved = localStorage.getItem(key);
  root.dataset.theme = saved === "light" || saved === "dark" ? saved : "dark";
  function syncButton(){
    const button = document.getElementById("theme-toggle");
    if (!button) return;
    const isDark = root.dataset.theme === "dark";
    button.textContent = isDark ? "Light mode" : "Dark mode";
    button.setAttribute("aria-pressed", String(isDark));
  }
  window.toggleOperatorTheme = function(){
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem(key, root.dataset.theme);
    syncButton();
  };
  document.addEventListener("DOMContentLoaded", syncButton);
})();
</script>"""


def _legacy_hero_html_cpd07(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            '<header class="hero">',
            '<div class="hero-inner">',
            '<div class="topbar">',
            "<div>",
            "<h1>コンテンツ候補レビュー</h1>",
            '<p class="subtitle">最初に見るものを 1 件に絞った確認画面です。開発用の中間 artifact は下部の折りたたみへ移しました。</p>',
            "</div>",
            '<button id="theme-toggle" class="theme-toggle" type="button" onclick="toggleOperatorTheme()" aria-pressed="true">Light mode</button>',
            "</div>",
            '<nav class="mini-nav" aria-label="ページ内ナビゲーション">',
            '<a href="#primary-review-card">今回確認する1件</a>',
            '<a href="#source-missing-ideas">未特定の企画メモ</a>',
            '<a href="#safety-boundary">安全境界</a>',
            '<a href="#developer-appendix">開発用詳細</a>',
            "</nav>",
            "</div>",
            "</header>",
        ]
    )


def _hero_html(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            '<header class="hero">',
            '<div class="hero-inner">',
            '<div class="topbar">',
            "<div>",
            f"<h1>{escape(payload['title'])}</h1>",
            (
                '<p class="subtitle">Operator Home / Funnel Meters v0。'
                "いま見るもの、見なくてよいもの、詰まっているメーターを最初の画面にまとめます。</p>"
            ),
            "</div>",
            '<button id="theme-toggle" class="theme-toggle" type="button" onclick="toggleOperatorTheme()" aria-pressed="true">Light mode</button>',
            "</div>",
            '<nav class="mini-nav" aria-label="ページ内ナビゲーション">',
            '<a href="#operator-home">Operator Home</a>',
            '<a href="#action-queue">Action Queue</a>',
            '<a href="#primary-review">次に判断する1件</a>',
            '<a href="#source-missing">source未特定</a>',
            '<a href="#blocked-hold">保留</a>',
            '<a href="#safety-boundary">閉じたゲート</a>',
            '<a href="#developer-appendix">開発用詳細</a>',
            "</nav>",
            "</div>",
            "</header>",
        ]
    )


def _verdict_html(payload: dict[str, Any]) -> str:
    human = payload["human_review"]
    summary = payload["summary"]
    action = payload["recommended_next_action"]
    return "\n".join(
        [
            '<section id="verdict" class="surface">',
            '<div class="verdict-grid">',
            '<div>',
            '<p class="kicker">今の結論</p>',
            f'<p class="verdict-line">{escape(human["primary_message"])}</p>',
            f'<p class="subtitle">{escape(human["secondary_message"])}</p>',
            "</div>",
            '<div>',
            '<p class="kicker">次の動き</p>',
            f'<p class="verdict-line">{escape(action["label"])}</p>',
            f'<p class="subtitle">{escape(action["reason"])}</p>',
            "</div>",
            "</div>",
            '<div class="metric-row" aria-label="状態サマリー">',
            f'<div class="metric"><span>確認する動画</span><strong>{summary["source_backed_count"]}</strong></div>',
            f'<div class="metric"><span>元動画未特定</span><strong>{summary["source_missing_count"]}</strong></div>',
            f'<div class="metric"><span>保留</span><strong>{summary["blocked_or_hold_count"]}</strong></div>',
            f'<div class="metric"><span>取得許可</span><strong>{summary["fetch_authorized_count"]}</strong></div>',
            "</div>",
            "</section>",
        ]
    )


def _operator_home_html(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    metrics = payload["home_metrics"]
    funnel = payload["funnel_stages"]
    meter_cards = [_meter_card_html(metric) for metric in metrics]
    funnel_steps = [_funnel_step_html(index, stage) for index, stage in enumerate(funnel, start=1)]
    return "\n".join(
        [
            '<section id="operator-home" class="surface">',
            '<div class="home-grid">',
            '<div class="home-answer">',
            '<p class="kicker">Operator Home</p>',
            "<h2>いま見るもの</h2>",
            (
                f'<p class="verdict-line">source付きで人間確認待ちの候補は '
                f'{summary["source_backed_count"]} 件です。</p>'
            ),
            (
                '<p>次は1件だけ確認します。source未特定の企画メモと保留候補は、'
                "動画候補として扱わず別の棚に分けています。</p>"
            ),
            '<div class="meter-grid">',
            *meter_cards,
            "</div>",
            "</div>",
            '<div class="home-answer">',
            '<p class="kicker">Candidate Funnel</p>',
            "<h2>どのメーターが詰まっているか</h2>",
            '<p>countsは既存CPD JSONから測定した値です。0のゲートはproduction進捗ではなく、まだ閉じている境界を示します。</p>',
            '<div class="funnel">',
            *funnel_steps,
            "</div>",
            "</div>",
            "</div>",
            "</section>",
        ]
    )


def _action_queue_html(payload: dict[str, Any]) -> str:
    queue = payload["action_queue"]
    cards = [_queue_card_html(item) for item in queue]
    return "\n".join(
        [
            '<section id="action-queue" class="surface">',
            '<div class="section-heading">',
            '<div><p class="kicker">Action Queue</p><h2>次に動く順番</h2><p>primaryは1件だけです。secondaryとholdは、いま開く対象ではなく backlog / 保留として分けています。</p></div>',
            "</div>",
            '<div class="queue-grid">',
            *cards,
            "</div>",
            "</section>",
        ]
    )


def _candidate_state_board_html(payload: dict[str, Any]) -> str:
    source_backed = payload["buckets"]["source_backed_ready_for_human_inspection"]
    backlog = payload["buckets"]["source_missing_idea_backlog"]
    blocked = payload["buckets"]["blocked_or_hold"]
    backed_item = source_backed[0] if source_backed else None
    backlog_cards = [_idea_card_html(item) for item in backlog]
    blocked_cards = [_blocked_card_html(item) for item in blocked]
    return "\n".join(
        [
            '<section id="candidate-state-board" class="surface">',
            '<div class="section-heading">',
            '<div><p class="kicker">Candidate State Board</p><h2>候補の状態</h2><p>ホームのメーターと同じ状態を、詳細セクションとしてたどれるようにしています。</p></div>',
            "</div>",
            '<div class="state-board">',
            '<section id="source-backed" class="state-card">',
            '<h3>source付き候補</h3>',
            (
                _source_backed_state_html(backed_item)
                if backed_item
                else '<p class="muted">source付き候補はありません。</p>'
            ),
            "</section>",
            '<section id="source-missing" class="state-card">',
            '<h3>source未特定 / not video-backed</h3>',
            '<p class="muted">JP/EN phrase gapを含む企画メモは、source URLが入るまで動画候補として扱いません。</p>',
            '<div class="idea-list">',
            *(backlog_cards or ['<p class="muted">source未特定の企画メモはありません。</p>']),
            "</div>",
            "</section>",
            '<section id="blocked-hold" class="state-card">',
            "<h3>保留</h3>",
            '<p class="muted">歌・音楽権利リスクなど、別routeが必要な候補です。</p>',
            '<div class="idea-list">',
            *(blocked_cards or ['<p class="muted">保留候補はありません。</p>']),
            "</div>",
            "</section>",
            "</div>",
            "</section>",
        ]
    )


def _meter_card_html(metric: dict[str, Any]) -> str:
    total = max(int(metric.get("total") or 0), 1)
    value = int(metric.get("value") or 0)
    width = max(0, min(100, round(value / total * 100)))
    return "\n".join(
        [
            f'<a class="meter-card" href="{escape(metric["href"])}">',
            f'<span>{escape(metric["label"])}</span>',
            f"<strong>{value}</strong>",
            f'<em>{escape(metric["why"])}</em>',
            '<div class="meter-bar" aria-hidden="true">',
            f'<div class="meter-fill" style="width:{width}%"></div>',
            "</div>",
            "</a>",
        ]
    )


def _funnel_step_html(index: int, stage: dict[str, Any]) -> str:
    return "\n".join(
        [
            f'<a class="funnel-step" href="{escape(stage["href"])}">',
            f'<span class="index">{index}</span>',
            "<span>",
            f'<strong>{escape(stage["label"])}</strong>',
            f'<span class="note">{escape(stage["note"])}</span>',
            "</span>",
            f'<span class="count">{int(stage["count"])}/{int(stage["total"])}</span>',
            "</a>",
        ]
    )


def _queue_card_html(item: dict[str, Any]) -> str:
    priority = clean_string(item.get("priority"))
    class_name = "queue-card"
    if priority == "primary":
        class_name += " primary"
    elif priority == "hold":
        class_name += " hold"
    return "\n".join(
        [
            f'<article class="{class_name}">',
            f'<p class="kicker">{escape(priority)}</p>',
            f'<h3>{escape(item["label"])}</h3>',
            f'<p class="muted">{escape(item["why"])}</p>',
            f'<span class="pill">{escape(item["state"])} / {int(item["count"])}件</span>',
            f'<br><a href="{escape(item["href"])}">対応するセクションへ</a>',
            "</article>",
        ]
    )


def _source_backed_state_html(item: dict[str, Any]) -> str:
    return "\n".join(
        [
            f'<p><strong>{escape(item["working_title"])}</strong></p>',
            f'<p class="muted">video_id: <code>{escape(item["video_id"])}</code> / decision: <code>{escape(item["decision_state"])}</code></p>',
            '<p class="muted">source URLは存在しますが、workerは開いておらず、identityは未確認です。</p>',
            '<a href="#primary-review">Primary Review Cardへ</a>',
        ]
    )


def _primary_review_card_html(payload: dict[str, Any]) -> str:
    source_backed = payload["buckets"]["source_backed_ready_for_human_inspection"]
    if not source_backed:
        return """
<section id="primary-review" class="primary-card">
  <span id="primary-review-card" class="anchor-alias" aria-hidden="true"></span>
  <div class="card-header">
    <p class="kicker">今回確認する1件</p>
    <h2>確認できる動画候補はありません</h2>
  </div>
  <div class="card-body">
    <p class="warn">source URL がある候補がないため、先に未特定の企画メモへ source URL を入れる必要があります。</p>
  </div>
</section>"""
    item = source_backed[0]
    question = f"このURLは、「{item['working_title']}」の元動画として妥当か？"
    checklist = [
        "動画ページが開ける",
        "タイトル / チャンネルが候補の意図と矛盾しない",
        "内容が切り抜き軸に関係していそう",
        "次に private/local 検証へ進める価値がある",
    ]
    return "\n".join(
        [
            '<section id="primary-review" class="primary-card">',
            '<span id="primary-review-card" class="anchor-alias" aria-hidden="true"></span>',
            '<div class="card-header">',
            '<p class="kicker">今回確認する1件</p>',
            f'<h2>{escape(item["working_title"])}</h2>',
            '<p class="id-line">',
            f'<span>candidate: <code>{escape(item["candidate_id"])}</code></span>',
            f'<span>seed: <code>{escape(item["seed_id"])}</code></span>',
            f'<span>video_id: <code>{escape(item["video_id"])}</code></span>',
            "</p>",
            "</div>",
            '<div class="card-body">',
            '<div class="review-block">',
            "<h3>URL</h3>",
            f'<a class="source-link" href="{escape(item["source_url"])}" target="_blank" rel="noreferrer">YouTube source URL を開く</a>',
            f'<span class="url-text">{escape(item["source_url"])}</span>',
            "</div>",
            '<div class="review-block">',
            "<h3>判断すること</h3>",
            f'<p class="question">{escape(question)}</p>',
            '<ul class="checklist">',
            *[
                f'<li><span class="checkmark">✓</span><span>{escape(label)}</span></li>'
                for label in checklist
            ],
            "</ul>",
            "</div>",
            '<div class="review-block">',
            "<h3>判断ラベル（表示のみ）</h3>",
            '<div class="decision-row">',
            '<div class="decision-chip"><strong class="ok">OK</strong><span>次に private/local 検証へ進めたい</span></div>',
            '<div class="decision-chip"><strong class="danger">NG</strong><span>source が違う</span></div>',
            '<div class="decision-chip"><strong class="warn">HOLD</strong><span>まだ判断しない</span></div>',
            "</div>",
            '<p class="muted" style="margin-top:10px">これは視覚的な判断メモです。この画面だけでは承認・取得許可・権利承認は発生しません。</p>',
            "</div>",
            '<div class="review-block">',
            "<h3>まだやらないこと</h3>",
            f'<div class="locked-list">{locked_pills_html(item["not_yet"])}</div>',
            "</div>",
            "</div>",
            "</section>",
        ]
    )


def _source_missing_ideas_html(payload: dict[str, Any]) -> str:
    backlog = payload["buckets"]["source_missing_idea_backlog"]
    blocked = payload["buckets"]["blocked_or_hold"]
    backlog_cards = [_idea_card_html(item) for item in backlog]
    blocked_cards = [_blocked_card_html(item) for item in blocked]
    return "\n".join(
        [
            '<section id="source-missing-ideas" class="surface">',
            '<div class="section-heading">',
            '<div><h2>未特定の企画メモ</h2><p>ここは次に見る動画ではありません。source URL が入るまで元動画候補として扱いません。</p></div>',
            f'<span class="pill">{len(backlog)} 件 + 保留 {len(blocked)} 件</span>',
            "</div>",
            '<details>',
            '<summary>未特定の企画メモを見る</summary>',
            '<div class="details-body">',
            '<div class="idea-list">',
            *(backlog_cards or ['<p class="muted">未特定の企画メモはありません。</p>']),
            *(blocked_cards or []),
            "</div>",
            "</div>",
            "</details>",
            "</section>",
        ]
    )


def _safety_boundary_html(payload: dict[str, Any]) -> str:
    gates = payload["gate_readback"]
    visible = [
        "fetch_authorized",
        "media_downloaded",
        "episode_dirs_created",
        "rights_approved",
        "production_ready",
        "public_ready",
    ]
    pills = [
        f'<span class="pill">{escape(key)}={str(gates[key]).lower()}</span>'
        for key in visible
    ]
    return "\n".join(
        [
            '<section id="safety-boundary" class="surface">',
            '<div class="section-heading">',
            '<div><h2>安全境界</h2><p>この画面は確認用です。取得・生成・承認はまだ閉じています。</p></div>',
            "</div>",
            "<details>",
            "<summary>閉じたままのゲートを見る</summary>",
            '<div class="details-body">',
            f'<div class="locked-list">{"".join(pills)}</div>',
            "</div>",
            "</details>",
            "</section>",
        ]
    )


def _developer_appendix_html(
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    base_dir: Path,
) -> str:
    rows = []
    for item in payload["buckets"]["internal_pipeline_artifact_only"]:
        status = "exists" if item["exists"] else "missing"
        rows.append(
            f"""
      <tr>
        <td><code>{escape(item["path"])}</code></td>
        <td>{escape(item["purpose"])}</td>
        <td>{escape(item["audience"])}</td>
        <td>{str(item["open_by_default"]).lower()}</td>
        <td>{escape(status)}</td>
      </tr>"""
        )
    return "\n".join(
        [
            '<section id="developer-appendix" class="surface">',
            '<div class="section-heading">',
            '<div><h2>開発用詳細</h2><p>個別 CPD HTML/JSON と machine readback は通常確認では開かない情報です。</p></div>',
            "</div>",
            "<details>",
            "<summary>artifact_id / machine JSON / 内部 artifact を見る</summary>",
            '<div class="details-body">',
            '<p class="muted">',
            f'artifact_id: <code>{escape(payload["artifact_id"])}</code><br>',
            f'generated_at: <code>{escape(payload["generated_at"])}</code><br>',
            f'operator JSON: <code>{escape(display_path(output_path, base_dir))}</code><br>',
            f'operator HTML: <code>{escape(display_path(dashboard_path, base_dir))}</code>',
            "</p>",
            '<div class="table-scroll">',
            "<table>",
            "<tr><th>path</th><th>purpose</th><th>audience</th><th>open by default</th><th>state</th></tr>",
            *rows,
            "</table>",
            "</div>",
            "</div>",
            "</details>",
            "</section>",
        ]
    )


def _idea_card_html(item: dict[str, Any]) -> str:
    return "\n".join(
        [
            '<article class="idea-card">',
            f'<h3>{escape(item["working_title"])}</h3>',
            '<p class="warn">元動画未確認。動画候補として扱わない。</p>',
            f'<p class="meta"><code>{escape(item["candidate_id"])}</code> / <code>{escape(item["seed_id"])}</code></p>',
            f'<p class="meta">必要: {escape(", ".join(item["required_before_progress"]))}</p>',
            "</article>",
        ]
    )


def _blocked_card_html(item: dict[str, Any]) -> str:
    return "\n".join(
        [
            '<article class="idea-card">',
            f'<h3>{escape(item["working_title"])}</h3>',
            f'<p class="danger">{escape(blocked_reason_label(item["reason"]))}</p>',
            f'<p class="meta"><code>{escape(item["candidate_id"])}</code> / <code>{escape(item["seed_id"])}</code></p>',
            "</article>",
        ]
    )


def locked_pills_html(values: list[str]) -> str:
    return "".join(f'<span class="pill">{escape(locked_label(value))}</span>' for value in values)


def locked_label(value: str) -> str:
    labels = {
        "fetch": "今は取得しない",
        "transcript": "文字起こししない",
        "render": "レンダーしない",
        "public": "公開しない",
        "rights": "権利承認しない",
    }
    return labels.get(value, value)


def first_nonempty(*values: Any) -> str:
    for value in values:
        text = clean_string(value)
        if text:
            return text
    return ""


def human_action_label(value: str) -> str:
    if value == "open_source_url_and_check_identity":
        return "URL を開いて、意図した候補と同じ動画か確認する"
    return value


def not_yet_label(values: list[str]) -> str:
    labels = {
        "fetch": "fetch 未許可",
        "transcript": "transcript 未作成",
        "render": "render 未作成",
        "public": "public 化未許可",
        "rights": "rights 未承認",
    }
    return " / ".join(labels.get(value, value) for value in values)


def grounding_label(value: str) -> str:
    if value == "not_grounded_to_source":
        return "元動画未確認。video-backed candidate として扱わない"
    return value


def blocked_reason_label(value: str) -> str:
    if value == "song_or_music_rights_sensitive":
        return "歌・音楽権利リスクがあるため保留"
    return value


def clean_string(value: Any) -> str:
    return str(value or "").strip()
