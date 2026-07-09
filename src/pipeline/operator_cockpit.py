"""CPD-12 operator cockpit minimal review console builder.

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
DEFAULT_ARTIFACT_ID = "clip-cpd12-minimal-review-console-v0-001"
DEFAULT_GENERATED_AT = "2026-07-07"
DEFAULT_OUTPUT_FILENAME = "operator_cockpit.json"
DEFAULT_DASHBOARD_FILENAME = "operator_cockpit.html"
HTML_TITLE = "ClipPipeGen Review Console"
UX_VERSION = "v7_minimal_review_console_v0"
DEFAULT_BRANCH_LABEL = "codex/cpd-12-minimal-review-console-v0"

NOT_YET_FLAGS = [
    "fetch",
    "transcript",
    "render",
    "upload",
    "rights",
]

LEDGER_GROUP_LABELS = {
    "source_backed": "source付き",
    "source_missing": "source未特定",
    "blocked_hold": "保留",
}

SOURCE_STATE_LABELS = {
    "source_url_present_identity_unchecked": "URLあり",
    "source_missing": "URL待ち",
    "hold": "保留",
}

REVIEW_STATE_LABELS = {
    "human_review_pending": "確認待ち",
    "not_reviewable_as_video": "動画未確認",
    "song_or_music_rights_sensitive": "音楽権利route確認待ち",
}

OPERATOR_USE_LABELS = {
    "primary_action": "現在の確認",
    "source_url_intake_backlog": "URL待ち",
    "do_not_progress_without_rights_route": "権利route待ち",
}

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
    gate_summary = build_gate_summary(gates)
    status_rail = build_status_rail(summary=summary, gate_summary=gate_summary)
    queue_summary = build_queue_summary(status_rail=status_rail)
    candidate_groups = build_candidate_groups(candidate_ledger)
    current_work_item = build_current_work_item(action_script=action_script, gate_summary=gate_summary)
    provenance_badges = build_provenance_badges(current_work_item=current_work_item)
    current_work_item["provenance_badges"] = provenance_badges
    modes = build_modes(summary=summary)
    shell = build_shell(summary=summary, modes=modes, artifact_id=artifact_id)
    link_targets = build_link_targets(modes=modes)
    microcopy_policy = build_microcopy_policy()
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
            "layout": "minimal_review_console_true_modes",
            "default_theme": "dark",
            "theme_toggle": True,
            "developer_appendix_default": "collapsed",
            "view_shell": "superseded_by_shell",
            "fixed_shell": "visible",
            "default_visible_mode": "review",
            "mode_separation": "review_backlog_system",
            "briefing_board": "superseded_by_view_shell",
            "annotated_flow": "model_readback_only",
            "candidate_ledger": "responsive_stacked",
            "ledger_layout": "responsive_ledger_stacked",
            "title_wrapping_guard": True,
            "id_wrapping_scope": "code_strip_only",
            "candidate_ledger_default": "collapsed",
            "system_mode_default": "collapsed",
            "microcopy_budget": True,
            "usage_frequency_ia": False,
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
            "primary_message": "One source-ready item is available.",
            "secondary_message": (
                "Backlog and hold items are not source-ready video candidates."
            ),
            "operator_open_first": display_path(dashboard_path, base_dir),
            "user_work": recommended_next_action["user_work"],
        },
        "summary": summary,
        "shell": shell,
        "view_shell": shell,
        "current_work_item": current_work_item,
        "modes": modes,
        "work_modes": modes,
        "status_rail": status_rail,
        "queue_summary": queue_summary,
        "provenance_badges": provenance_badges,
        "link_targets": link_targets,
        "candidate_groups": candidate_groups,
        "gate_summary": gate_summary,
        "microcopy_policy": microcopy_policy,
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
                "CPD-12 converts the CPD operator cockpit into a minimal review "
                "console with fixed shell regions, true local modes, and explicit "
                "planning-label provenance. It does not change source, fetch, "
                "rights, production, or public gates."
            ),
            "shell": "minimal_review_console",
            "view_shell": "minimal_review_console",
            "default_visible_mode": "review",
            "work_mode_count": len(modes),
            "queue_chip_count": len(status_rail["chips"]),
            "locked_gate_count": gate_summary["locked_gate_count"],
            "ledger_layout": "responsive_ledger_stacked",
            "title_wrapping_guard": True,
            "provenance_badge_count": len(provenance_badges),
            "link_target_count": len(link_targets),
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
            "label": "Current source review",
            "reason": "One source-ready item is available; backlog and hold items stay outside the default review.",
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
        {"section_id": "review-console", "label": "Review Console", "href": "#review-console"},
        {"section_id": "mode-review", "label": "Review", "href": "#mode-review"},
        {"section_id": "current-review", "label": "Current Review", "href": "#current-review"},
        {"section_id": "mode-backlog", "label": "Backlog", "href": "#mode-backlog"},
        {"section_id": "backlog", "label": "Backlog", "href": "#backlog"},
        {"section_id": "candidate-ledger", "label": "Candidate Ledger", "href": "#candidate-ledger"},
        {"section_id": "mode-system", "label": "System", "href": "#mode-system"},
        {"section_id": "system", "label": "System", "href": "#system"},
        {"section_id": "safety-boundary", "label": "Safety Boundary", "href": "#safety-boundary"},
        {"section_id": "developer-appendix", "label": "Developer Appendix", "href": "#developer-appendix"},
    ]


def build_gate_summary(gates: dict[str, Any]) -> dict[str, Any]:
    locked_gates = list(NOT_YET_FLAGS)
    return {
        "line": f"locked: {' / '.join(locked_gates)}",
        "compact_line": "locked: fetch/render/upload/rights",
        "locked_gates": locked_gates,
        "locked_gate_count": len(locked_gates),
        "gate_defaults": {
            "fetch_authorized": bool(gates["fetch_authorized"]),
            "rights_approved": bool(gates["rights_approved"]),
            "production_ready": bool(gates["production_ready"]),
            "public_ready": bool(gates["public_ready"]),
        },
    }


def build_status_rail(*, summary: dict[str, Any], gate_summary: dict[str, Any]) -> dict[str, Any]:
    chips = [
        {"id": "source_url_present", "label": "URLあり", "value": summary["source_backed_count"], "href": "#mode-review"},
        {"id": "source_url_waiting", "label": "URL待ち", "value": summary["source_missing_idea_backlog_count"], "href": "#mode-backlog"},
        {"id": "hold", "label": "保留", "value": summary["blocked_or_hold_count"], "href": "#mode-backlog"},
        {"id": "locked", "label": "locked", "value": gate_summary["compact_line"].replace("locked: ", ""), "href": "#mode-system"},
    ]
    return {
        "status_rail_id": "minimal_review_console_status_rail",
        "chips": chips,
        "lock_line": gate_summary["compact_line"],
        "source": "local_cpd_json",
    }


def build_queue_summary(*, status_rail: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "operator_queue_summary",
        "chips": status_rail["chips"],
        "source": status_rail["source"],
    }


def build_candidate_groups(candidate_ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    group_specs = [
        ("source_backed", "Source ready", "URLあり。人間のsource identity確認だけが次の作業です。"),
        ("source_missing", "Source backlog", "URL待ち。動画未確認の企画メモとして扱います。"),
        ("blocked_hold", "Hold", "権利route待ち。ここから先へ進めません。"),
    ]
    groups = []
    for group_id, label, note in group_specs:
        items = [row for row in candidate_ledger if row["ledger_group"] == group_id]
        groups.append(
            {
                "group_id": group_id,
                "label": label,
                "count": len(items),
                "note": note,
                "items": items,
            }
        )
    return groups


def build_current_work_item(*, action_script: dict[str, Any], gate_summary: dict[str, Any]) -> dict[str, Any]:
    planning_label = action_script["target_title"]
    source_url = action_script["source_url"]
    return {
        "work_item_id": "source_identity_review",
        "label": "Current Review",
        "title": planning_label,
        "planning_label": planning_label,
        "candidate_label": planning_label,
        "label_provenance": "planning_label_unverified",
        "verified_video_title": "",
        "target_candidate_id": action_script["target_candidate_id"],
        "target_seed_id": action_script["target_seed_id"],
        "source_url": source_url,
        "source_url_state": "present" if source_url else "missing",
        "identity_state": "unverified",
        "fetch_authorized": False,
        "source_opened_by_worker": False,
        "source_button_label": "Source URL",
        "question": action_script["question"],
        "unverified_markers": action_script["unverified_markers"],
        "decision_labels": action_script["visual_choices"],
        "locked_line": gate_summary["line"],
        "compact_locked_line": gate_summary["compact_line"],
        "user_work": "open_only" if source_url else "source_url_intake",
    }


def build_provenance_badges(*, current_work_item: dict[str, Any]) -> list[dict[str, str]]:
    source_badge = "source_url_present" if current_work_item["source_url_state"] == "present" else "source_url_missing"
    return [
        {
            "id": "planning_label",
            "label": "planning_label",
            "meaning": "generated planning label; not a verified video title",
        },
        {
            "id": source_badge,
            "label": source_badge,
            "meaning": "source URL is available in local data",
        },
        {
            "id": "identity_unverified",
            "label": "identity_unverified",
            "meaning": "human source identity review is still pending",
        },
        {
            "id": "not_fetched",
            "label": "not_fetched",
            "meaning": "worker did not open, fetch, download, or initialize media",
        },
    ]


def build_modes(*, summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "mode_id": "review",
            "label": "Review",
            "jp_label": "常用",
            "href": "#mode-review",
            "panel_id": "mode-review",
            "button_id": "mode-control-review",
            "target_slot": "current_work_item",
            "default_active": True,
            "default_visible": True,
            "purpose": "current work item and OK / NG / HOLD labels",
        },
        {
            "mode_id": "backlog",
            "label": "Backlog",
            "jp_label": "要確認",
            "href": "#mode-backlog",
            "panel_id": "mode-backlog",
            "button_id": "mode-control-backlog",
            "target_slot": "backlog_groups",
            "default_active": False,
            "default_visible": False,
            "purpose": f"source missing {summary['source_missing_idea_backlog_count']} and hold {summary['blocked_or_hold_count']}",
        },
        {
            "mode_id": "system",
            "label": "System",
            "jp_label": "開発用",
            "href": "#mode-system",
            "panel_id": "mode-system",
            "button_id": "mode-control-system",
            "target_slot": "gate_summary",
            "default_active": False,
            "default_visible": False,
            "purpose": "closed gates and internal artifacts",
        },
    ]


def build_work_modes(*, summary: dict[str, Any]) -> list[dict[str, Any]]:
    return build_modes(summary=summary)


def build_shell(*, summary: dict[str, Any], modes: list[dict[str, Any]], artifact_id: str) -> dict[str, Any]:
    return {
        "shell_id": "minimal_review_console",
        "title": "Review Console",
        "console_title": HTML_TITLE,
        "shell_label": "fixed shell: Review Console",
        "artifact_id": artifact_id,
        "version_label": "CPD-12",
        "branch_label": DEFAULT_BRANCH_LABEL,
        "subtitle": "Review, Backlog, and System are separate local modes over the same generated data.",
        "content_model_version": UX_VERSION,
        "fixed_regions": [
            "console_header",
            "artifact_version_chip",
            "mode_switcher",
            "status_rail",
            "system_lock_indicator",
        ],
        "dynamic_slots": [
            "current_work_item",
            "source_url",
            "planning_label",
            "provenance_badges",
            "candidate_counts",
            "backlog_groups",
            "candidate_ledger",
            "gate_summary",
            "internal_artifacts",
        ],
        "default_mode": "review",
        "mode_ids": [mode["mode_id"] for mode in modes],
        "anchors": [item["href"] for item in build_section_links()],
        "first_viewport_explanatory_paragraph_limit": 1,
        "default_visible_counts": {
            "source_backed": summary["source_backed_count"],
            "source_missing_backlog": summary["source_missing_idea_backlog_count"],
            "hold": summary["blocked_or_hold_count"],
        },
    }


def build_view_shell(*, summary: dict[str, Any], work_modes: list[dict[str, Any]]) -> dict[str, Any]:
    return build_shell(
        summary=summary,
        modes=work_modes,
        artifact_id=DEFAULT_ARTIFACT_ID,
    )


def build_link_targets(*, modes: list[dict[str, Any]]) -> list[dict[str, str]]:
    targets = [
        {"id": "review-console", "kind": "shell", "href": "#review-console"},
        {"id": "current-review", "kind": "slot", "href": "#current-review"},
        {"id": "backlog", "kind": "slot", "href": "#backlog"},
        {"id": "candidate-ledger", "kind": "slot", "href": "#candidate-ledger"},
        {"id": "system", "kind": "slot", "href": "#system"},
        {"id": "safety-boundary", "kind": "slot", "href": "#safety-boundary"},
        {"id": "developer-appendix", "kind": "slot", "href": "#developer-appendix"},
    ]
    mode_targets = [
        {"id": mode["panel_id"], "kind": "mode_panel", "href": mode["href"]}
        for mode in modes
    ]
    return [targets[0], *mode_targets, *targets[1:]]


def build_microcopy_policy() -> dict[str, Any]:
    return {
        "policy_id": "stable_operator_microcopy_v0",
        "main_copy": "stable_short_labels",
        "first_viewport_explanatory_paragraph_limit": 1,
        "gate_copy": "one_line_plus_collapsed_detail",
        "machine_state_visibility": "system_mode_or_code_strip_only",
        "unverified_marker": "[ ]",
    }


def build_briefing(
    *,
    summary: dict[str, Any],
    recommended_next_action: dict[str, Any],
    annotated_flow: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "briefing_id": "cpd12_minimal_review_console_readback",
        "title": "Review Console",
        "status_line": (
            f"URLあり {summary['source_backed_count']} / "
            f"URL待ち {summary['source_missing_idea_backlog_count']} / "
            f"hold {summary['blocked_or_hold_count']}"
        ),
        "decision_line": "Current Review is the only default action.",
        "bottleneck_line": "Backlog and hold items stay behind true mode switching.",
        "locked_line": "locked: fetch/render/upload/rights",
        "primary_action": {
            "action_id": recommended_next_action["action_id"],
            "label": recommended_next_action["label"],
            "href": "#current-review",
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
            "annotation": "Candidate inventory for comparison mode.",
            "usage_frequency": "必要時",
            "is_bottleneck": False,
        },
        {
            "stage_id": "source_backed",
            "label": "source付き",
            "count": summary["source_backed_count"],
            "total": total,
            "href": "#current-review",
            "status": "reviewable",
            "annotation": "Source URL is present; identity review is still human-owned.",
            "usage_frequency": "常用",
            "is_bottleneck": False,
        },
        {
            "stage_id": "human_review_waiting",
            "label": "人間確認待ち",
            "count": summary["inspectable_packet_count"],
            "total": total,
            "href": "#current-review",
            "status": "current_bottleneck",
            "annotation": "Current review accepts only OK / NG / HOLD labels and notes.",
            "usage_frequency": "常用",
            "is_bottleneck": True,
        },
        {
            "stage_id": "private_local_review",
            "label": "private/local検証",
            "count": summary["fetch_authorized_count"],
            "total": total,
            "href": "#system",
            "status": "locked",
            "annotation": "Zero is a closed pre-fetch state, not a failure.",
            "usage_frequency": "後工程",
            "is_bottleneck": False,
        },
        {
            "stage_id": "edit_render_public",
            "label": "edit/render/public",
            "count": 0,
            "total": total,
            "href": "#system",
            "status": "locked",
            "annotation": "Transcript / render / upload / public gates remain closed.",
            "usage_frequency": "後工程",
            "is_bottleneck": False,
        },
    ]


def build_usage_frequency_sections() -> list[dict[str, str]]:
    return [
        {
            "frequency": "常用",
            "section_id": "current-review",
            "href": "#current-review",
            "role": "current source review work item",
        },
        {
            "frequency": "要確認",
            "section_id": "backlog",
            "href": "#backlog",
            "role": "source missing and hold queue",
        },
        {
            "frequency": "必要時",
            "section_id": "candidate-ledger",
            "href": "#candidate-ledger",
            "role": "responsive candidate comparison list",
        },
        {
            "frequency": "開発用",
            "section_id": "system",
            "href": "#system",
            "role": "closed gates and internal readback",
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
        source_state = "source_url_present_identity_unchecked"
        review_state = "human_review_pending"
        operator_use = "primary_action"
        rows.append(
            {
                "ledger_group": "source_backed",
                "ledger_group_label": LEDGER_GROUP_LABELS["source_backed"],
                "candidate_id": item["candidate_id"],
                "seed_id": item["seed_id"],
                "working_title": item["working_title"],
                "source_state": source_state,
                "source_state_label": SOURCE_STATE_LABELS[source_state],
                "review_state": review_state,
                "review_state_label": REVIEW_STATE_LABELS[review_state],
                "video_backed": True,
                "video_backed_label": "video-backed",
                "operator_use": operator_use,
                "operator_use_label": OPERATOR_USE_LABELS[operator_use],
                "href": "#current-review",
                "source_url": item["source_url"],
                "video_id": item["video_id"],
            }
        )
    for item in source_missing_ideas:
        source_state = "source_missing"
        review_state = "not_reviewable_as_video"
        operator_use = "source_url_intake_backlog"
        rows.append(
            {
                "ledger_group": "source_missing",
                "ledger_group_label": LEDGER_GROUP_LABELS["source_missing"],
                "candidate_id": item["candidate_id"],
                "seed_id": item["seed_id"],
                "working_title": item["working_title"],
                "source_state": source_state,
                "source_state_label": SOURCE_STATE_LABELS[source_state],
                "review_state": review_state,
                "review_state_label": REVIEW_STATE_LABELS[review_state],
                "video_backed": False,
                "video_backed_label": "not video-backed",
                "operator_use": operator_use,
                "operator_use_label": OPERATOR_USE_LABELS[operator_use],
                "href": "#backlog",
                "source_url": "",
                "video_id": "",
            }
        )
    for item in blocked_or_hold:
        source_state = "hold"
        review_state = item["reason"]
        operator_use = "do_not_progress_without_rights_route"
        rows.append(
            {
                "ledger_group": "blocked_hold",
                "ledger_group_label": LEDGER_GROUP_LABELS["blocked_hold"],
                "candidate_id": item["candidate_id"],
                "seed_id": item["seed_id"],
                "working_title": item["working_title"],
                "source_state": source_state,
                "source_state_label": SOURCE_STATE_LABELS[source_state],
                "review_state": review_state,
                "review_state_label": REVIEW_STATE_LABELS.get(review_state, review_state),
                "video_backed": False,
                "video_backed_label": "not video-backed",
                "operator_use": operator_use,
                "operator_use_label": OPERATOR_USE_LABELS[operator_use],
                "href": "#backlog",
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
        "target_title": title,
        "target_candidate_id": clean_string(item.get("candidate_id")),
        "target_seed_id": clean_string(item.get("seed_id")),
        "source_url": clean_string(item.get("source_url")),
        "video_id": clean_string(item.get("video_id")),
        "question": f"このSource URLは Planning label「{title}」の候補意図と同じ動画に見えるか。",
        "open_label": "Source URLを開く",
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
            '<html lang="ja" data-theme="dark" data-view="review">',
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
            '<a class="skip-link" href="#mode-review">Reviewへ移動</a>',
            _hero_html(payload),
            '<main id="review-console" class="console-frame">',
            _review_mode_html(payload),
            _backlog_mode_html(payload),
            _system_mode_html(payload, output_path, dashboard_path, base_dir),
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
.console-header{
  border-bottom:1px solid var(--border);
  background:var(--surface);
}
.console-header-inner,.console-frame{
  width:min(1080px,calc(100% - 32px));
  margin:0 auto;
}
.console-header-inner{padding:18px 0 16px}
.topbar{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:start}
h1,h2,h3,p{margin:0}
h1{font-size:32px;line-height:1.15;letter-spacing:0}
h2{font-size:22px;line-height:1.28;letter-spacing:0}
h3{font-size:17px;line-height:1.35;letter-spacing:0}
.subtitle{margin-top:6px;color:var(--muted);max-width:760px;font-size:14px}
.theme-toggle{
  min-width:112px;
  border:1px solid var(--border);
  border-radius:8px;
  color:var(--text);
  background:var(--surface-2);
  padding:8px 10px;
  cursor:pointer;
}
.artifact-strip{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
.artifact-chip,.mode-control,.state-chip,.provenance-badge,.pill{
  display:inline-flex;
  align-items:center;
  gap:7px;
  border:1px solid var(--border);
  border-radius:999px;
  padding:4px 9px;
  background:var(--surface-2);
  color:var(--text);
  text-decoration:none;
  font-size:13px;
}
.artifact-chip strong,.state-chip strong{color:var(--accent-2)}
.shell-label,.slot-label,.kicker{color:var(--accent);font-weight:700;font-size:12px;text-transform:none;margin-bottom:5px}
.mode-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-top:14px}
.mode-control{border-radius:7px;font-weight:700;padding:7px 10px}
.mode-control.is-active{border-color:var(--accent);background:rgba(245,158,11,.16)}
.state-rail{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.lock-line{color:var(--muted);font-size:13px;margin-top:8px}
main{padding:22px 0 40px}
.console-frame{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:8px;
  box-shadow:var(--shadow);
  padding:0 20px 20px;
}
.mode-panel{padding:20px 0;border-top:1px solid var(--border)}
.mode-panel:first-child{border-top:0}
.js-enabled .mode-panel{display:none}
.js-enabled .mode-panel.is-active{display:block}
.mode-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:16px}
.mode-head p{color:var(--muted);font-size:14px;margin-top:4px}
.compact-line{color:var(--muted);font-size:13px}
.surface{margin-top:18px}
.current-item-panel{display:grid;grid-template-columns:minmax(0,1fr) minmax(240px,.38fr);gap:18px;align-items:start;background:var(--surface-2);border-left:4px solid var(--accent);border-radius:8px;padding:16px}
.candidate-title{font-size:25px;line-height:1.36;word-break:normal;overflow-wrap:normal;line-break:strict;margin-top:2px}
.meta-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:14px 0 0}
.meta-grid div{border-top:1px solid var(--border);padding-top:8px}
.meta-grid dt{color:var(--muted);font-size:12px}
.meta-grid dd{margin:2px 0 0;font-weight:700}
.badge-row{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}
.provenance-badge{background:var(--surface-3);font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.side-stack{display:grid;gap:13px}
.source-link{display:inline-flex;justify-content:center;align-items:center;border:1px solid var(--accent);border-radius:7px;padding:8px 10px;background:rgba(245,158,11,.16);text-decoration:none;color:var(--text);font-weight:700}
.url-text{display:block;margin-top:7px;color:var(--muted);font-size:12px;overflow-wrap:break-word;word-break:normal}
.question{font-size:18px;font-weight:700;margin-top:14px}
.checklist{display:grid;gap:7px;margin:12px 0 0;padding:0;list-style:none}
.checklist li{display:flex;gap:8px;align-items:flex-start}
.review-marker{color:var(--accent);font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-weight:700}
.decision-labels{display:flex;gap:8px;flex-wrap:wrap}
.decision-label{border:1px solid var(--border);border-radius:999px;background:var(--surface-3);padding:5px 9px}
.decision-label strong{margin-right:5px}
.backlog-list{display:grid;gap:6px}
.backlog-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;border-top:1px solid var(--border);padding:10px 0;color:var(--text);text-decoration:none}
.backlog-row strong{line-height:1.45;word-break:normal;overflow-wrap:normal;line-break:strict}
.backlog-row span{color:var(--muted);font-size:13px}
.group-panel{padding:10px 0}
.group-panel + .group-panel{border-top:1px solid var(--border)}
.system-grid{display:grid;gap:10px}
.status-line{font-size:19px;font-weight:700;color:var(--ink-soft)}
.locked-list{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.ok{color:var(--success)}.warn{color:var(--warning)}.danger{color:var(--danger)}
.section-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.section-heading p{color:var(--muted);margin-top:4px}
.ledger-summary{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.ledger-summary .pill{background:var(--surface-2)}
.ledger-list{display:grid;gap:10px}
.ledger-item{border-top:1px solid var(--border);padding:12px 0;display:grid;gap:10px}
.ledger-row-top{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.state-badge{display:inline-flex;align-items:center;border:1px solid var(--border);border-radius:999px;padding:4px 9px;background:var(--surface-3);color:var(--text);font-size:13px;font-weight:700;text-decoration:none}
.state-badge.source-backed{border-color:rgba(34,197,94,.55)}
.state-badge.source-missing{border-color:rgba(245,158,11,.6)}
.state-badge.blocked-hold{border-color:rgba(239,68,68,.55)}
.ledger-title{font-size:18px;line-height:1.48;letter-spacing:0;word-break:normal;overflow-wrap:normal;line-break:strict}
.ledger-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px 12px;margin:0}
.ledger-meta div{border-top:1px solid var(--border);padding-top:8px}
.ledger-meta dt{color:var(--muted);font-size:12px}
.ledger-meta dd{margin:2px 0 0;font-weight:700}
.code-strip-details{background:transparent}
.code-strip-details summary{padding:8px 0;color:var(--muted);font-size:12px}
.code-strip{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px}
.code-strip code{white-space:nowrap;word-break:break-all;overflow-wrap:anywhere}
details{border:1px solid var(--border);border-radius:8px;background:var(--surface-2)}
summary{cursor:pointer;padding:12px 14px;font-weight:700}
.details-body{border-top:1px solid var(--border);padding:14px}
.table-scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:720px}
th,td{border-bottom:1px solid var(--border);padding:8px;text-align:left;vertical-align:top}
th{background:var(--surface-3)}
.video-backed{color:var(--success);font-weight:700}
.not-video-backed{color:var(--warning);font-weight:700}
code{background:var(--surface-3);border:1px solid var(--border);border-radius:5px;padding:1px 4px;color:var(--text)}
.muted{color:var(--muted)}
@media (max-width:720px){
  .topbar{display:block}
  .theme-toggle{margin-top:14px}
  .current-item-panel{grid-template-columns:1fr}
  .console-frame,.console-header-inner{width:min(100% - 20px,1080px)}
  .source-link{display:flex;justify-content:center}
  .backlog-row{grid-template-columns:1fr}
}
"""


def theme_script() -> str:
    return """
<script>
(function(){
  const key = "clippipegen.operatorCockpit.theme";
  const root = document.documentElement;
  root.classList.add("js-enabled");
  const saved = localStorage.getItem(key);
  root.dataset.theme = saved === "light" || saved === "dark" ? saved : "dark";
  const modeByHash = {
    "review-console": "review",
    "mode-review": "review",
    "current-review": "review",
    "mode-backlog": "backlog",
    "backlog": "backlog",
    "candidate-ledger": "backlog",
    "mode-system": "system",
    "system": "system",
    "safety-boundary": "system",
    "developer-appendix": "system"
  };
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
  function modeFromHash(){
    const id = window.location.hash ? window.location.hash.slice(1) : "";
    return modeByHash[id] || "review";
  }
  function activateMode(mode, focusPanel){
    const selected = mode === "backlog" || mode === "system" ? mode : "review";
    root.dataset.view = selected;
    document.querySelectorAll("[data-mode-panel]").forEach(function(panel){
      const active = panel.getAttribute("data-mode-panel") === selected;
      panel.classList.toggle("is-active", active);
      panel.setAttribute("aria-hidden", active ? "false" : "true");
    });
    document.querySelectorAll("[data-mode-target]").forEach(function(control){
      const active = control.getAttribute("data-mode-target") === selected;
      control.classList.toggle("is-active", active);
      control.setAttribute("aria-current", active ? "page" : "false");
    });
    const panel = document.getElementById("mode-" + selected);
    if (focusPanel && panel) {
      panel.focus({preventScroll:true});
    }
  }
  document.addEventListener("DOMContentLoaded", function(){
    syncButton();
    activateMode(modeFromHash(), false);
    document.querySelectorAll("[data-mode-target]").forEach(function(control){
      control.addEventListener("click", function(event){
        const mode = control.getAttribute("data-mode-target");
        activateMode(mode, true);
      });
    });
  });
  window.addEventListener("hashchange", function(){
    activateMode(modeFromHash(), false);
  });
})();
</script>"""


def _hero_html(payload: dict[str, Any]) -> str:
    shell = payload["shell"]
    chips = [_state_chip_html(chip) for chip in payload["status_rail"]["chips"]]
    tabs = [_mode_tab_html(mode) for mode in payload["modes"]]
    return "\n".join(
        [
            '<header class="console-header">',
            '<div class="console-header-inner">',
            '<div class="topbar">',
            "<div>",
            f'<p class="shell-label">{escape(shell["shell_label"])}</p>',
            f"<h1>{escape(payload['title'])}</h1>",
            f'<p class="subtitle">{escape(shell["subtitle"])}</p>',
            '<div class="artifact-strip" aria-label="artifact version">',
            f'<span class="artifact-chip"><strong>{escape(shell["version_label"])}</strong></span>',
            f'<span class="artifact-chip">artifact <code>{escape(shell["artifact_id"])}</code></span>',
            f'<span class="artifact-chip">branch <code>{escape(shell["branch_label"])}</code></span>',
            "</div>",
            "</div>",
            '<button id="theme-toggle" class="theme-toggle" type="button" onclick="toggleOperatorTheme()" aria-pressed="true">Light mode</button>',
            "</div>",
            '<div class="state-rail" aria-label="status rail">',
            *chips,
            "</div>",
            f'<p class="lock-line">{escape(payload["status_rail"]["lock_line"])}</p>',
            '<nav class="mode-tabs" aria-label="Review Console modes">',
            *tabs,
            "</nav>",
            "</div>",
            "</header>",
        ]
    )


def _review_mode_html(payload: dict[str, Any]) -> str:
    item = payload["current_work_item"]
    badges = [
        f'<span class="provenance-badge">{escape(badge["label"])}</span>'
        for badge in item["provenance_badges"]
    ]
    markers = [
        f'<li><span class="review-marker">{escape(marker["marker"])}</span><span>{escape(marker["label"])}</span></li>'
        for marker in item["unverified_markers"]
    ]
    decisions = [
        (
            '<div class="decision-label">'
            f'<strong>{escape(decision["label"])}</strong>'
            f'<span>{escape(decision["meaning"])}</span>'
            "</div>"
        )
        for decision in item["decision_labels"]
    ]
    source_link = (
        f'<a class="source-link" href="{escape(item["source_url"])}" target="_blank" rel="noreferrer">'
        f'{escape(item["source_button_label"])}</a>'
        if item["source_url"]
        else '<span class="pill">source URL required</span>'
    )
    return "\n".join(
        [
            '<section id="mode-review" class="mode-panel is-active" data-mode-panel="review" tabindex="-1">',
            '<div class="mode-head">',
            '<div><p class="kicker">Review mode / 常用</p><h2>Current Review</h2></div>',
            "</div>",
            '<div id="current-review" class="current-item-panel">',
            "<div>",
            '<p class="slot-label">data slot: current_work_item</p>',
            '<dl class="meta-grid">',
            f'<div><dt>Planning label</dt><dd class="candidate-title">{escape(item["planning_label"])}</dd></div>',
            f'<div><dt>label provenance</dt><dd>{escape(item["label_provenance"])}</dd></div>',
            f'<div><dt>source URL state</dt><dd>{escape(item["source_url_state"])}</dd></div>',
            f'<div><dt>identity state</dt><dd>{escape(item["identity_state"])}</dd></div>',
            "</dl>",
            '<div class="badge-row" aria-label="provenance badges">',
            *badges,
            "</div>",
            f'<p class="question">{escape(item["question"])}</p>',
            '<ul class="checklist">',
            *markers,
            "</ul>",
            "</div>",
            '<aside class="side-stack">',
            "<h3>Decision labels</h3>",
            '<div class="decision-labels">',
            *decisions,
            "</div>",
            "<div>",
            source_link,
            f'<span class="url-text">{escape(item["source_url"])}</span>',
            "</div>",
            f'<p class="lock-line">{escape(item["compact_locked_line"])}</p>',
            "</aside>",
            "</div>",
            "</section>",
        ]
    )


def _state_chip_html(chip: dict[str, Any]) -> str:
    return (
        f'<a class="state-chip" href="{escape(chip["href"])}">'
        f'<span>{escape(chip["label"])}</span><strong>{escape(str(chip["value"]))}</strong></a>'
    )


def _mode_tab_html(mode: dict[str, Any]) -> str:
    class_name = "mode-control is-active" if mode["default_active"] else "mode-control"
    return (
        f'<a id="{escape(mode["button_id"])}" class="{class_name}" href="{escape(mode["href"])}" '
        f'data-mode-target="{escape(mode["mode_id"])}">'
        f'{escape(mode["label"])} / {escape(mode["jp_label"])}</a>'
    )


def _backlog_mode_html(payload: dict[str, Any]) -> str:
    groups = [
        group for group in payload["candidate_groups"] if group["group_id"] in {"source_missing", "blocked_hold"}
    ]
    group_panels = [_candidate_group_panel_html(group) for group in groups]
    return "\n".join(
        [
            '<section id="mode-backlog" class="mode-panel" data-mode-panel="backlog" tabindex="-1">',
            '<div id="backlog" class="mode-head">',
            '<div><p class="kicker">Backlog mode / 要確認</p><h2>Source backlog</h2><p>URL待ちと保留は Current Review と同格にしません。</p></div>',
            "</div>",
            '<div class="backlog-list">',
            *group_panels,
            "</div>",
            _candidate_ledger_html(payload),
            "</section>",
        ]
    )


def _candidate_group_panel_html(group: dict[str, Any]) -> str:
    rows = [
        (
            '<a class="backlog-row" href="#candidate-ledger">'
            "<span>"
            f'<strong>{escape(item["working_title"])}</strong>'
            f'<span>{escape(item["source_state_label"])} / '
            f'{escape(item["review_state_label"])} / not source-ready</span>'
            "</span>"
            f'<span class="pill">{escape(item["operator_use_label"])}</span></a>'
        )
        for item in group["items"]
    ]
    return "\n".join(
        [
            '<article class="group-panel">',
            f'<h3>{escape(group["label"])} <span class="pill">{int(group["count"])}</span></h3>',
            '<div class="backlog-list">',
            *(rows or ['<p class="compact-line">none</p>']),
            "</div>",
            "</article>",
        ]
    )


def _system_mode_html(
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    base_dir: Path,
) -> str:
    gate_summary = payload["gate_summary"]
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
            '<section id="mode-system" class="mode-panel" data-mode-panel="system" tabindex="-1">',
            '<div id="system" class="mode-head">',
            '<div><p class="kicker">System mode / 開発用</p><h2>System readback</h2><p>Internal state is subordinate to the current review.</p></div>',
            "</div>",
            '<div id="safety-boundary" class="system-grid">',
            f'<p class="status-line">{escape(gate_summary["line"])}</p>',
            "<details>",
            "<summary>gate detail</summary>",
            '<div class="details-body">',
            f'<div class="locked-list">{"".join(pills)}</div>',
            "</div>",
            "</details>",
            "</div>",
            _developer_appendix_html(payload, output_path, dashboard_path, base_dir),
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
            '<div><p class="kicker">Candidate Ledger</p><h2>Candidate state list</h2><p>比較が必要な時だけ候補5件を開きます。</p></div>',
            "</div>",
            '<div class="ledger-summary">',
            f'<span class="pill">source-backed {summary["source_backed_count"]}</span>',
            f'<span class="pill">source-missing {summary["source_missing_idea_backlog_count"]}</span>',
            f'<span class="pill">hold {summary["blocked_or_hold_count"]}</span>',
            "</div>",
            "<details>",
            "<summary>open responsive Candidate Ledger</summary>",
            '<div class="details-body">',
            '<div class="ledger-list" role="list">',
            *rows,
            "</div>",
            "</div>",
            "</details>",
            "</section>",
        ]
    )


def _candidate_ledger_row_html(row: dict[str, Any]) -> str:
    video_class = "video-backed" if row["video_backed"] else "not-video-backed"
    group_class = row["ledger_group"].replace("_", "-")
    return "\n".join(
        [
            f'<article class="ledger-item {escape(group_class)}" role="listitem">',
            '<div class="ledger-row-top">',
            f'<a class="state-badge {escape(group_class)}" href="{escape(row["href"])}">{escape(row["ledger_group_label"])}</a>',
            f'<span class="{video_class}">{escape(row["video_backed_label"])}</span>',
            "</div>",
            f'<h3 class="ledger-title">{escape(row["working_title"])}</h3>',
            '<dl class="ledger-meta">',
            f'<div><dt>source</dt><dd>{escape(row["source_state_label"])}</dd></div>',
            f'<div><dt>review</dt><dd>{escape(row["review_state_label"])}</dd></div>',
            f'<div><dt>operator</dt><dd>{escape(row["operator_use_label"])}</dd></div>',
            "</dl>",
            '<details class="code-strip-details">',
            "<summary>machine ids</summary>",
            '<div class="code-strip">',
            f'<code>{escape(row["candidate_id"])}</code>',
            f'<code>{escape(row["seed_id"])}</code>',
            "</div>",
            "</details>",
            "</article>",
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


def locked_label(value: str) -> str:
    labels = {
        "fetch": "今は取得しない",
        "transcript": "文字起こししない",
        "render": "レンダーしない",
        "upload": "アップロードしない",
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
        "upload": "upload 未許可",
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
