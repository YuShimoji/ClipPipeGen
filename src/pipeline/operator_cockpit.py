"""CPD-09 operator cockpit briefing-board UX builder.

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
DEFAULT_ARTIFACT_ID = "clip-cpd09-operator-briefing-board-v0-001"
DEFAULT_GENERATED_AT = "2026-07-06"
DEFAULT_OUTPUT_FILENAME = "operator_cockpit.json"
DEFAULT_DASHBOARD_FILENAME = "operator_cockpit.html"
HTML_TITLE = "ClipPipeGen Operator Cockpit / Content Planning Review"
UX_VERSION = "v4_briefing_board_usage_frequency_v0"

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
    annotated_flow = build_annotated_flow(summary=summary)
    usage_frequency_sections = build_usage_frequency_sections()
    candidate_ledger = build_candidate_ledger(
        source_backed=source_backed,
        source_missing_ideas=source_missing_ideas,
        blocked_or_hold=blocked_or_hold,
    )
    action_script = build_action_script(source_backed=source_backed, summary=summary)
    briefing = build_briefing(
        summary=summary,
        recommended_next_action=recommended_next_action,
        annotated_flow=annotated_flow,
    )
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
            "layout": "operator_briefing_board_usage_frequency",
            "default_theme": "dark",
            "theme_toggle": True,
            "developer_appendix_default": "collapsed",
            "briefing_board": "visible",
            "annotated_flow": "visible",
            "candidate_ledger": "compact",
            "usage_frequency_ia": True,
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
            "primary_message": "Human review has one source-backed candidate.",
            "secondary_message": (
                "The remaining unresolved ideas are source-missing or hold items; "
                "they are not video-backed candidates."
            ),
            "operator_open_first": display_path(dashboard_path, base_dir),
            "user_work": recommended_next_action["user_work"],
        },
        "summary": summary,
        "briefing": briefing,
        "annotated_flow": annotated_flow,
        "usage_frequency_sections": usage_frequency_sections,
        "candidate_ledger": candidate_ledger,
        "action_script": action_script,
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
                "CPD-09 is a briefing-board information architecture layer over CPD-01 through CPD-05. "
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
        {"section_id": "briefing-board", "label": "Briefing Board", "href": "#briefing-board"},
        {"section_id": "primary-review", "label": "次に判断する1件", "href": "#primary-review"},
        {"section_id": "candidate-ledger", "label": "Candidate Ledger", "href": "#candidate-ledger"},
        {"section_id": "source-missing", "label": "source未特定", "href": "#source-missing"},
        {"section_id": "blocked-hold", "label": "保留", "href": "#blocked-hold"},
        {"section_id": "safety-boundary", "label": "閉じたゲート", "href": "#safety-boundary"},
        {"section_id": "developer-appendix", "label": "開発用詳細", "href": "#developer-appendix"},
    ]


def build_briefing(
    *,
    summary: dict[str, Any],
    recommended_next_action: dict[str, Any],
    annotated_flow: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "briefing_id": "cpd09_operator_briefing",
        "title": "今日のBriefing",
        "status_line": (
            f"source付き候補は {summary['source_backed_count']} 件、"
            f"source未特定は {summary['source_missing_idea_backlog_count']} 件、"
            f"保留は {summary['blocked_or_hold_count']} 件です。"
        ),
        "decision_line": "次に見るのは、番長/船長のURLが候補意図と同じ動画に見えるかだけです。",
        "bottleneck_line": "判断待ちは人間確認の1件で、source未特定と保留は下段ledgerに退避しています。",
        "locked_line": "fetch / download / transcript / render / upload / rights approval は未実行です。",
        "primary_action": {
            "action_id": recommended_next_action["action_id"],
            "label": recommended_next_action["label"],
            "href": "#primary-review",
            "state": "human_review_waiting",
            "user_work": recommended_next_action["user_work"],
        },
        "flow_stage_count": len(annotated_flow),
    }


def build_annotated_flow(*, summary: dict[str, Any]) -> list[dict[str, Any]]:
    total = summary["total_candidates"]
    return [
        {
            "stage_id": "ideas",
            "label": "企画候補",
            "count": total,
            "total": total,
            "href": "#candidate-ledger",
            "status": "inventory",
            "annotation": "入口。ここは採用判断ではなく候補棚卸しです。",
            "usage_frequency": "必要時",
            "is_bottleneck": False,
        },
        {
            "stage_id": "source_backed",
            "label": "source付き",
            "count": summary["source_backed_count"],
            "total": total,
            "href": "#primary-review",
            "status": "reviewable",
            "annotation": "今すぐ人間がURL同一性を見られる候補です。",
            "usage_frequency": "常用",
            "is_bottleneck": False,
        },
        {
            "stage_id": "human_review_waiting",
            "label": "人間確認待ち",
            "count": summary["inspectable_packet_count"],
            "total": total,
            "href": "#primary-review",
            "status": "current_bottleneck",
            "annotation": "ここが今回の詰まりです。OK / NG / HOLD の自由文判断だけを受けます。",
            "usage_frequency": "常用",
            "is_bottleneck": True,
        },
        {
            "stage_id": "private_local_review",
            "label": "private/local検証",
            "count": summary["fetch_authorized_count"],
            "total": total,
            "href": "#safety-boundary",
            "status": "locked",
            "annotation": "0は失敗ではなく、fetch許可前なので閉じている状態です。",
            "usage_frequency": "後工程",
            "is_bottleneck": False,
        },
        {
            "stage_id": "edit_render_public",
            "label": "edit/render/public",
            "count": 0,
            "total": total,
            "href": "#safety-boundary",
            "status": "locked",
            "annotation": "transcript / render / upload / public gate はまだ開始しません。",
            "usage_frequency": "後工程",
            "is_bottleneck": False,
        },
    ]


def build_usage_frequency_sections() -> list[dict[str, str]]:
    return [
        {
            "frequency": "常用",
            "section_id": "briefing-board",
            "href": "#briefing-board",
            "role": "最初に読む判断路線図",
        },
        {
            "frequency": "常用",
            "section_id": "primary-review",
            "href": "#primary-review",
            "role": "今回の1件を確認する操作単位",
        },
        {
            "frequency": "必要時",
            "section_id": "candidate-ledger",
            "href": "#candidate-ledger",
            "role": "候補状態の比較とsource未特定の確認",
        },
        {
            "frequency": "開発用",
            "section_id": "developer-appendix",
            "href": "#developer-appendix",
            "role": "内部artifactとmachine readbackの退避先",
        },
    ]


def build_candidate_ledger(
    *,
    source_backed: list[dict[str, Any]],
    source_missing_ideas: list[dict[str, Any]],
    blocked_or_hold: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in source_backed:
        rows.append(
            {
                "ledger_group": "source_backed",
                "candidate_id": item["candidate_id"],
                "seed_id": item["seed_id"],
                "working_title": item["working_title"],
                "source_state": "source_url_present_identity_unchecked",
                "review_state": "human_review_pending",
                "video_backed": True,
                "operator_use": "primary_action",
                "href": "#primary-review",
                "source_url": item["source_url"],
                "video_id": item["video_id"],
            }
        )
    for item in source_missing_ideas:
        rows.append(
            {
                "ledger_group": "source_missing",
                "candidate_id": item["candidate_id"],
                "seed_id": item["seed_id"],
                "working_title": item["working_title"],
                "source_state": "source_missing",
                "review_state": "not_reviewable_as_video",
                "video_backed": False,
                "operator_use": "source_url_intake_backlog",
                "href": "#source-missing",
                "source_url": "",
                "video_id": "",
            }
        )
    for item in blocked_or_hold:
        rows.append(
            {
                "ledger_group": "blocked_hold",
                "candidate_id": item["candidate_id"],
                "seed_id": item["seed_id"],
                "working_title": item["working_title"],
                "source_state": "hold",
                "review_state": item["reason"],
                "video_backed": False,
                "operator_use": "do_not_progress_without_rights_route",
                "href": "#blocked-hold",
                "source_url": "",
                "video_id": "",
            }
        )
    return rows


def build_action_script(*, source_backed: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    item = source_backed[0] if source_backed else {}
    title = clean_string(item.get("working_title")) or "source付き候補"
    return {
        "script_id": "single_source_identity_check",
        "target_candidate_id": clean_string(item.get("candidate_id")),
        "target_seed_id": clean_string(item.get("seed_id")),
        "source_url": clean_string(item.get("source_url")),
        "video_id": clean_string(item.get("video_id")),
        "question": f"このURLは「{title}」の候補意図と同じ動画に見えるか。",
        "open_label": "YouTube source URLを開いて人間が同一性だけを見る",
        "unverified_markers": [
            {"marker": "[ ]", "label": "動画ページが開ける"},
            {"marker": "[ ]", "label": "タイトル / チャンネルが候補の意図と矛盾しない"},
            {"marker": "[ ]", "label": "内容が切り抜き軸に関係していそう"},
            {"marker": "[ ]", "label": "次にprivate/local検証へ進める価値がある"},
        ],
        "visual_choices": [
            {"label": "OK", "meaning": "候補意図と同じ動画に見える"},
            {"label": "NG", "meaning": "候補意図と違う、またはsourceが違う"},
            {"label": "HOLD", "meaning": "画面だけではまだ判断しない"},
        ],
        "not_yet": list(NOT_YET_FLAGS),
        "source_backed_count": summary["source_backed_count"],
    }


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
            '<a class="skip-link" href="#briefing-board">Briefing Boardへ移動</a>',
            _hero_html(payload),
            '<main class="page-shell">',
            _briefing_board_html(payload),
            _primary_review_script_html(payload),
            _candidate_ledger_html(payload),
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
  --bg:#111315;
  --surface:#1b2024;
  --surface-2:#242b31;
  --surface-3:#303941;
  --text:#f1f5f9;
  --muted:#aeb8c2;
  --border:#3f4a54;
  --accent:#f59e0b;
  --accent-2:#22d3ee;
  --success:#86efac;
  --warning:#fbbf24;
  --danger:#fca5a5;
  --link:#93c5fd;
  --ink-soft:#d8e0e8;
  --shadow:0 18px 40px rgba(0,0,0,.28);
}
:root[data-theme="light"]{
  color-scheme:light;
  --bg:#f7f8fa;
  --surface:#ffffff;
  --surface-2:#f1f4f7;
  --surface-3:#e5ebf0;
  --text:#17202a;
  --muted:#5d6872;
  --border:#d4dce3;
  --accent:#b45309;
  --accent-2:#0f766e;
  --success:#13723f;
  --warning:#9a5a00;
  --danger:#a32626;
  --link:#075985;
  --ink-soft:#2f3b46;
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
.briefing-board{display:grid;gap:16px}
.briefing-copy{display:grid;gap:8px;max-width:880px}
.briefing-line{font-size:20px;font-weight:700;color:var(--ink-soft)}
.briefing-note{color:var(--muted)}
.primary-action-line{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;align-items:center;border:1px solid var(--accent);border-radius:8px;background:var(--surface-2);padding:14px}
.primary-action-line strong{display:block;font-size:18px}
.primary-action-line a{display:inline-block;border:1px solid var(--accent);border-radius:6px;padding:7px 10px;text-decoration:none;color:var(--text);background:rgba(245,158,11,.16);font-weight:700}
.usage-frequency{display:flex;gap:8px;flex-wrap:wrap}
.usage-frequency a{border:1px solid var(--border);border-radius:999px;padding:5px 9px;text-decoration:none;color:var(--text);background:var(--surface-2);font-size:13px}
.usage-frequency span{color:var(--accent);font-weight:700}
.flow-rail{display:grid;gap:8px}
.flow-step{display:grid;grid-template-columns:34px minmax(0,1fr) auto;gap:10px;align-items:start;border-left:4px solid var(--border);background:var(--surface-2);padding:10px 12px;text-decoration:none;color:var(--text);border-radius:0 8px 8px 0}
.flow-step.current{border-left-color:var(--accent);background:linear-gradient(90deg,rgba(245,158,11,.16),var(--surface-2))}
.flow-step.locked{border-left-color:var(--muted);opacity:.86}
.flow-step .index{width:26px;height:26px;border-radius:999px;display:grid;place-items:center;background:var(--surface-3);font-weight:700}
.flow-step .annotation{display:block;color:var(--muted);font-size:13px}
.flow-step .count{font-weight:700;color:var(--accent-2);white-space:nowrap}
.anchor-alias{position:relative;top:-16px}
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
.review-marker{color:var(--accent);font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-weight:700}
.decision-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.decision-chip{border:1px solid var(--border);border-radius:8px;background:var(--surface-3);padding:10px}
.decision-chip strong{display:block;margin-bottom:4px}
.ok{color:var(--success)}.warn{color:var(--warning)}.danger{color:var(--danger)}
.locked-list{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.pill{border:1px solid var(--border);border-radius:999px;padding:4px 9px;background:var(--surface-3);font-size:13px;color:var(--text)}
.section-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.section-heading p{color:var(--muted);margin-top:4px}
.ledger-summary{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.ledger-summary .pill{background:var(--surface-2)}
details{border:1px solid var(--border);border-radius:8px;background:var(--surface-2)}
summary{cursor:pointer;padding:12px 14px;font-weight:700}
.details-body{border-top:1px solid var(--border);padding:14px}
.table-scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:720px}
th,td{border-bottom:1px solid var(--border);padding:8px;text-align:left;vertical-align:top}
th{background:var(--surface-3)}
.ledger-table td:first-child{font-weight:700}
.video-backed{color:var(--success);font-weight:700}
.not-video-backed{color:var(--warning);font-weight:700}
code{background:var(--surface-3);border:1px solid var(--border);border-radius:5px;padding:1px 4px;color:var(--text)}
.muted{color:var(--muted)}
@media (max-width:720px){
  .topbar{display:block}
  .theme-toggle{margin-top:14px}
  .primary-action-line{grid-template-columns:1fr}
  .page-shell,.hero-inner{width:min(100% - 20px,1040px)}
  .source-link{display:flex;justify-content:center}
  .flow-step{grid-template-columns:30px minmax(0,1fr)}
  .flow-step .count{grid-column:2}
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
                '<p class="subtitle">Briefing Board / Usage-Frequency IA v0。'
                "最初に読む説明付きフロー、今回の1アクション、必要時だけ見るledgerを分けます。</p>"
            ),
            "</div>",
            '<button id="theme-toggle" class="theme-toggle" type="button" onclick="toggleOperatorTheme()" aria-pressed="true">Light mode</button>',
            "</div>",
            '<nav class="mini-nav" aria-label="ページ内ナビゲーション">',
            '<a href="#briefing-board">Briefing Board</a>',
            '<a href="#primary-review">次に判断する1件</a>',
            '<a href="#candidate-ledger">Candidate Ledger</a>',
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


def _briefing_board_html(payload: dict[str, Any]) -> str:
    briefing = payload["briefing"]
    flow_steps = [
        _annotated_flow_step_html(index, stage)
        for index, stage in enumerate(payload["annotated_flow"], start=1)
    ]
    usage_links = [_usage_frequency_link_html(item) for item in payload["usage_frequency_sections"]]
    primary = briefing["primary_action"]
    return "\n".join(
        [
            '<section id="briefing-board" class="surface briefing-board">',
            '<div class="briefing-copy">',
            '<p class="kicker">常用 / Briefing Board</p>',
            f'<h2>{escape(briefing["title"])}</h2>',
            f'<p class="briefing-line">{escape(briefing["status_line"])}</p>',
            f'<p>{escape(briefing["decision_line"])}</p>',
            f'<p class="briefing-note">{escape(briefing["bottleneck_line"])}</p>',
            f'<p class="briefing-note">{escape(briefing["locked_line"])}</p>',
            "</div>",
            '<div class="primary-action-line">',
            "<div>",
            '<span class="kicker">Primary action</span>',
            f'<strong>{escape(primary["label"])}</strong>',
            f'<span class="muted">state: <code>{escape(primary["state"])}</code> / user_work: <code>{escape(primary["user_work"])}</code></span>',
            "</div>",
            f'<a href="{escape(primary["href"])}">Review Scriptへ</a>',
            "</div>",
            '<div class="usage-frequency" aria-label="usage frequency">',
            *usage_links,
            "</div>",
            '<div class="flow-rail" aria-label="annotated flow">',
            *flow_steps,
            "</div>",
            "</section>",
        ]
    )


def _annotated_flow_step_html(index: int, stage: dict[str, Any]) -> str:
    class_name = "flow-step"
    if stage["is_bottleneck"]:
        class_name += " current"
    if stage["status"] == "locked":
        class_name += " locked"
    return "\n".join(
        [
            f'<a class="{class_name}" href="{escape(stage["href"])}">',
            f'<span class="index">{index}</span>',
            "<span>",
            f'<strong>{escape(stage["label"])}</strong>',
            f'<span class="annotation">{escape(stage["annotation"])}</span>',
            f'<span class="annotation">usage: {escape(stage["usage_frequency"])} / status: <code>{escape(stage["status"])}</code></span>',
            "</span>",
            f'<span class="count">{int(stage["count"])}/{int(stage["total"])}</span>',
            "</a>",
        ]
    )


def _usage_frequency_link_html(item: dict[str, str]) -> str:
    return (
        f'<a href="{escape(item["href"])}"><span>{escape(item["frequency"])}</span> '
        f'{escape(item["section_id"])}: {escape(item["role"])}</a>'
    )


def _primary_review_script_html(payload: dict[str, Any]) -> str:
    script = payload["action_script"]
    if not script["source_url"]:
        return """
<section id="primary-review" class="primary-card">
  <span id="primary-review-card" class="anchor-alias" aria-hidden="true"></span>
  <div class="card-header">
    <p class="kicker">常用 / Primary Review Script</p>
    <h2>確認できるsource付き候補はありません</h2>
  </div>
  <div class="card-body">
    <p class="warn">まずsource未特定の候補に実URLを追加してください。</p>
  </div>
</section>"""
    markers = [
        f'<li><span class="review-marker">{escape(item["marker"])}</span><span>{escape(item["label"])}</span></li>'
        for item in script["unverified_markers"]
    ]
    choices = [
        f'<div class="decision-chip"><strong>{escape(item["label"])}</strong><span>{escape(item["meaning"])}</span></div>'
        for item in script["visual_choices"]
    ]
    return "\n".join(
        [
            '<section id="primary-review" class="primary-card">',
            '<span id="primary-review-card" class="anchor-alias" aria-hidden="true"></span>',
            '<div class="card-header">',
            '<p class="kicker">常用 / Primary Review Script</p>',
            "<h2>番長/船長URLのsource identityだけを見る</h2>",
            '<p class="id-line">',
            f'<span>candidate: <code>{escape(script["target_candidate_id"])}</code></span>',
            f'<span>seed: <code>{escape(script["target_seed_id"])}</code></span>',
            f'<span>video_id: <code>{escape(script["video_id"])}</code></span>',
            "</p>",
            "</div>",
            '<div class="card-body">',
            '<div class="review-block">',
            "<h3>開くURL</h3>",
            f'<a class="source-link" href="{escape(script["source_url"])}" target="_blank" rel="noreferrer">{escape(script["open_label"])}</a>',
            f'<span class="url-text">{escape(script["source_url"])}</span>',
            "</div>",
            '<div class="review-block">',
            "<h3>判断すること</h3>",
            f'<p class="question">{escape(script["question"])}</p>',
            '<ul class="checklist">',
            *markers,
            "</ul>",
            '<p class="muted">上の印は未検証の観点です。完了を示すチェックマークではありません。</p>',
            "</div>",
            '<div class="review-block">',
            "<h3>返す判断ラベル（表示のみ）</h3>",
            '<div class="decision-row">',
            *choices,
            "</div>",
            '<p class="muted" style="margin-top:10px">この画面だけではfetch許可、取得、文字起こし、render、upload、rights approvalは発生しません。</p>',
            "</div>",
            '<div class="review-block">',
            "<h3>まだやらないこと</h3>",
            f'<div class="locked-list">{locked_pills_html(script["not_yet"])}</div>',
            "</div>",
            "</div>",
            "</section>",
        ]
    )


def _candidate_ledger_html(payload: dict[str, Any]) -> str:
    rows = [_candidate_ledger_row_html(row) for row in payload["candidate_ledger"]]
    summary = payload["summary"]
    return "\n".join(
        [
            '<section id="candidate-ledger" class="surface">',
            '<div class="section-heading">',
            '<div><p class="kicker">必要時 / Candidate Ledger</p><h2>候補状態を下段で比較する</h2><p>上段の判断を邪魔しないよう、source付き / source未特定 / 保留をledgerに集約します。</p></div>',
            "</div>",
            '<div class="ledger-summary">',
            f'<span class="pill">source-backed {summary["source_backed_count"]}</span>',
            f'<span class="pill">source-missing {summary["source_missing_idea_backlog_count"]}</span>',
            f'<span class="pill">hold {summary["blocked_or_hold_count"]}</span>',
            "</div>",
            '<div class="table-scroll">',
            '<table class="ledger-table">',
            "<tr><th>group</th><th>candidate</th><th>title</th><th>source state</th><th>review state</th><th>video-backed</th><th>operator use</th></tr>",
            *rows,
            "</table>",
            "</div>",
            '<span id="source-missing" class="anchor-alias" aria-hidden="true"></span>',
            '<details>',
            '<summary>source未特定の扱いを確認する</summary>',
            '<div class="details-body"><p>source-missing行は、URLが入るまで動画候補ではありません。JP/EN phrase gap も企画メモであり、video-backed candidate として扱いません。</p></div>',
            "</details>",
            '<span id="blocked-hold" class="anchor-alias" aria-hidden="true"></span>',
            '<details>',
            '<summary>保留の扱いを確認する</summary>',
            '<div class="details-body"><p>song / music rights sensitive の候補は、別のrights routeがない限りこの画面から進めません。</p></div>',
            "</details>",
            "</section>",
        ]
    )


def _candidate_ledger_row_html(row: dict[str, Any]) -> str:
    video_class = "video-backed" if row["video_backed"] else "not-video-backed"
    video_label = "video-backed" if row["video_backed"] else "not video-backed"
    return "\n".join(
        [
            "<tr>",
            f'<td><a href="{escape(row["href"])}">{escape(row["ledger_group"])}</a></td>',
            f'<td><code>{escape(row["candidate_id"])}</code><br><code>{escape(row["seed_id"])}</code></td>',
            f'<td>{escape(row["working_title"])}</td>',
            f'<td>{escape(row["source_state"])}</td>',
            f'<td>{escape(row["review_state"])}</td>',
            f'<td class="{video_class}">{video_label}</td>',
            f'<td>{escape(row["operator_use"])}</td>',
            "</tr>",
        ]
    )


def _primary_review_card_html(payload: dict[str, Any]) -> str:
    return _primary_review_script_html(payload)


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
