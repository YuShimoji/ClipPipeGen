"""CPD-05 source inspection packet and decision template builder.

This module reads CPD-04 dry-run episode init plans and writes local review
artifacts for operator source inspection. It never opens source URLs, creates
episode folders, writes episode artifacts, generates media-derived records, or
approves rights/public/production use.
"""

from __future__ import annotations

import json
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any

from .content_planning import display_path, write_json, write_text

SCHEMA_ID = "clippipegen.source_inspection_packet.v0"
DECISION_TEMPLATE_SCHEMA_ID = "clippipegen.source_inspection_decisions.template.v0"
DEFAULT_ARTIFACT_ID = "clip-cpd05-source-inspection-packet-v0-001"
DEFAULT_GENERATED_AT = "2026-07-06"
DEFAULT_OUTPUT_FILENAME = "source_inspection_packet.json"
DEFAULT_DASHBOARD_FILENAME = "source_inspection_packet_dashboard.html"
DEFAULT_DECISION_TEMPLATE_FILENAME = "source_inspection_decisions.template.json"

DECISION_OPTIONS = [
    "approve_for_future_private_fetch",
    "reject_source",
    "needs_different_source",
    "needs_manual_review",
    "defer",
]

NEXT_ACTION_OPTIONS = [
    "operator_open_source_url",
    "fill_source_inspection_decisions",
    "reject_or_defer",
    "future_fetch_slice_after_approval",
]


class SourceInspectionPacketError(ValueError):
    """Raised when CPD-05 input cannot be used."""


def build_source_inspection_packet(
    *,
    input_path: Path,
    output_path: Path,
    base_dir: Path,
    dashboard_path: Path | None = None,
    decision_template_path: Path | None = None,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Read CPD-04 plans and write source inspection JSON/HTML artifacts."""

    input_payload, plans, skipped_source_records = load_episode_init_plan_records(input_path)
    inspectable_plans = [plan for plan in plans if is_inspectable_plan(plan)]
    non_ready_plans = [plan for plan in plans if not is_inspectable_plan(plan)]
    packets = [
        build_packet_record(plan, generated_at=generated_at)
        for plan in inspectable_plans
    ]
    blocked = [
        build_blocked_record(item, generated_at=generated_at, source_kind="episode_init_plan")
        for item in non_ready_plans
    ] + [
        build_blocked_record(item, generated_at=generated_at, source_kind="skipped_source_record")
        for item in skipped_source_records
    ]
    summary = summarize(plans=plans, packets=packets, blocked=blocked)
    gates = build_gate_readback(packets=packets, blocked=blocked)
    payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": {
            "input_artifact": display_path(input_path, base_dir),
            "input_schema_id": str(input_payload.get("schema_id") or ""),
            "input_artifact_id": str(input_payload.get("artifact_id") or ""),
            "network_required": False,
            "source_opened_by_worker": False,
        },
        "summary": summary,
        "gate_readback": gates,
        "decision_options": DECISION_OPTIONS,
        "next_action_options": NEXT_ACTION_OPTIONS,
        "source_inspection_packets": packets,
        "blocked_source_records": blocked,
    }
    write_json(payload, output_path)

    resolved_template_path = (
        decision_template_path
        or output_path.with_name(DEFAULT_DECISION_TEMPLATE_FILENAME)
    )
    decision_template = build_decision_template(
        packet_payload=payload,
        packets=packets,
        output_path=output_path,
        base_dir=base_dir,
        generated_at=generated_at,
    )
    write_json(decision_template, resolved_template_path)

    resolved_dashboard_path = dashboard_path or output_path.with_name(DEFAULT_DASHBOARD_FILENAME)
    write_text(
        render_source_inspection_dashboard_html(
            payload=payload,
            output_path=output_path,
            dashboard_path=resolved_dashboard_path,
            decision_template_path=resolved_template_path,
            base_dir=base_dir,
        ),
        resolved_dashboard_path,
    )
    return {
        "artifact_id": artifact_id,
        "episode_init_plan_count": len(plans),
        "inspectable_packet_count": len(packets),
        "blocked_skipped_count": len(blocked),
        "output_path": output_path,
        "dashboard_path": resolved_dashboard_path,
        "decision_template_path": resolved_template_path,
        "payload": payload,
        "decision_template": decision_template,
    }


def load_episode_init_plan_records(
    path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise SourceInspectionPacketError(f"episode init plan input is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SourceInspectionPacketError(f"episode init plan input is not valid JSON: {path}") from exc

    if isinstance(raw, list):
        raw = {"schema_id": "", "artifact_id": "", "episode_init_plans": raw}
    if not isinstance(raw, dict):
        raise SourceInspectionPacketError("episode init plan input root must be an object or list")

    plans = raw.get("episode_init_plans")
    if not isinstance(plans, list):
        raise SourceInspectionPacketError("episode init plan input must contain episode_init_plans[]")
    skipped = raw.get("skipped_source_records")
    if skipped is None:
        skipped = []
    if not isinstance(skipped, list):
        raise SourceInspectionPacketError("episode init plan skipped_source_records must be a list")

    usable_plans = [plan for plan in plans if isinstance(plan, dict)]
    usable_skipped = [record for record in skipped if isinstance(record, dict)]
    for plan in usable_plans:
        if not clean_string(plan.get("episode_plan_id")):
            raise SourceInspectionPacketError("every episode init plan must contain episode_plan_id")
        if not clean_string(plan.get("seed_id")):
            raise SourceInspectionPacketError("every episode init plan must contain seed_id")
        if not clean_string(plan.get("candidate_id")):
            raise SourceInspectionPacketError("every episode init plan must contain candidate_id")
    return raw, usable_plans, usable_skipped


def is_inspectable_plan(plan: dict[str, Any]) -> bool:
    return (
        plan.get("ready_for_real_init") is True
        and clean_string(plan.get("source_url_state")) == "present"
        and bool(clean_string(plan.get("source_url")))
    )


def build_packet_record(plan: dict[str, Any], *, generated_at: str) -> dict[str, Any]:
    packet_id = f"source_inspection_packet_{clean_string(plan.get('planned_episode_slug'))}"
    rights = normalize_rights_readback(plan.get("rights_readback"))
    proposed_scope = (
        dict(plan.get("proposed_clip_scope"))
        if isinstance(plan.get("proposed_clip_scope"), dict)
        else {}
    )
    return {
        "inspection_packet_id": packet_id,
        "episode_plan_id": clean_string(plan.get("episode_plan_id")),
        "source_resolution_id": clean_string(plan.get("source_resolution_id")),
        "seed_id": clean_string(plan.get("seed_id")),
        "candidate_id": clean_string(plan.get("candidate_id")),
        "generated_at": generated_at,
        "working_title": clean_string(plan.get("working_title")),
        "planned_episode_slug": clean_string(plan.get("planned_episode_slug")),
        "source_url": clean_string(plan.get("source_url")),
        "video_id": clean_string(plan.get("video_id")),
        "source_url_state": clean_string(plan.get("source_url_state")),
        "dry_run": True,
        "source_media_state": "not_fetched",
        "source_open_state": "not_opened_by_worker",
        "inspection_state": "pending_operator_review",
        "decision_state": "pending",
        "fetch_authorized": False,
        "rights_readback": rights,
        "rights_approved": False,
        "public_ready": False,
        "production_ready": False,
        "proposed_clip_scope": proposed_scope,
        "expected_edit_value": clean_string(plan.get("expected_edit_value")),
        "risk_flags": as_risk_flags(plan.get("risk_flags")),
        "operator_checklist": operator_checklist(),
        "decision_options": DECISION_OPTIONS,
        "next_action_options": NEXT_ACTION_OPTIONS,
        "next_action": "operator_open_source_url",
        "blocked_reason": "",
    }


def build_blocked_record(
    item: dict[str, Any],
    *,
    generated_at: str,
    source_kind: str,
) -> dict[str, Any]:
    url_state = clean_string(item.get("source_url_state")) or "unknown"
    reason = clean_string(item.get("blocked_reason")) or clean_string(item.get("blocking_reason"))
    if not reason:
        reason = "source record is not ready for operator inspection"
    return {
        "source_kind": source_kind,
        "episode_plan_id": clean_string(item.get("episode_plan_id")),
        "source_resolution_id": clean_string(item.get("source_resolution_id")),
        "seed_id": clean_string(item.get("seed_id")),
        "candidate_id": clean_string(item.get("candidate_id")),
        "generated_at": generated_at,
        "working_title": clean_string(item.get("working_title")),
        "planned_episode_slug": clean_string(item.get("planned_episode_slug")),
        "source_url": clean_string(item.get("source_url")),
        "video_id": clean_string(item.get("video_id")),
        "source_url_state": url_state,
        "source_media_state": "not_fetched",
        "ready_for_source_inspection": False,
        "inspection_state": "blocked",
        "decision_state": "blocked",
        "fetch_authorized": False,
        "rights_approved": False,
        "public_ready": False,
        "production_ready": False,
        "blocked_reason": reason,
        "next_action": blocked_next_action(url_state, clean_string(item.get("next_action"))),
    }


def operator_checklist() -> list[dict[str, Any]]:
    labels = [
        ("source_page_availability", "source page exists / availability"),
        ("title_channel_consistency", "title/channel appears consistent"),
        ("clip_angle_relevance", "content appears relevant to clip_angle"),
        ("obvious_risk_flags", "obvious risk flags"),
        ("future_fetch_authorization", "whether future private/local fetch should be authorized"),
    ]
    return [
        {
            "check_id": check_id,
            "label": label,
            "state": "unchecked",
            "result": None,
            "source_opened_by_worker": False,
            "notes": [],
        }
        for check_id, label in labels
    ]


def build_decision_template(
    *,
    packet_payload: dict[str, Any],
    packets: list[dict[str, Any]],
    output_path: Path,
    base_dir: Path,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "schema_id": DECISION_TEMPLATE_SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": f"{packet_payload['artifact_id']}-decision-template",
        "generated_at": generated_at,
        "source_packet_artifact": display_path(output_path, base_dir),
        "instructions": [
            "Fill only after a human/operator source inspection.",
            "Leave decision as pending until the source URL has actually been reviewed.",
            "Do not paste credentials, cookies, private account data, or downloaded media paths.",
            "approve_future_private_fetch is only an input to a later gated slice; it is not rights approval or public readiness.",
        ],
        "allowed_decisions": DECISION_OPTIONS,
        "entry_count": len(packets),
        "entries": [
            {
                "inspection_packet_id": packet["inspection_packet_id"],
                "episode_plan_id": packet["episode_plan_id"],
                "seed_id": packet["seed_id"],
                "candidate_id": packet["candidate_id"],
                "source_url_reviewed": False,
                "source_available": None,
                "title_channel_match": None,
                "clip_relevance": None,
                "risk_notes": [],
                "decision": "pending",
                "approve_future_private_fetch": False,
                "reviewer_notes": [],
                "reviewed_at": "",
                "boundary_flags_confirmed": {
                    "fetch_authorized": False,
                    "rights_approved": False,
                    "production_ready": False,
                    "public_ready": False,
                },
                "do_not_fill_without_human_review": True,
            }
            for packet in packets
        ],
    }


def summarize(
    *,
    plans: list[dict[str, Any]],
    packets: list[dict[str, Any]],
    blocked: list[dict[str, Any]],
) -> dict[str, Any]:
    states = Counter(
        clean_string(packet.get("source_url_state")) or "unknown"
        for packet in packets
    )
    blocked_states = Counter(
        clean_string(record.get("source_url_state")) or "unknown"
        for record in blocked
    )
    return {
        "episode_init_plan_count": len(plans),
        "inspectable_packet_count": len(packets),
        "blocked_skipped_count": len(blocked),
        "decision_template_entry_count": len(packets),
        "source_url_present_count": states.get("present", 0) + blocked_states.get("present", 0),
        "source_url_missing_count": states.get("missing", 0) + blocked_states.get("missing", 0),
        "source_url_invalid_count": states.get("invalid", 0) + blocked_states.get("invalid", 0),
        "fetch_authorized_count": 0,
        "source_opened_by_worker": False,
        "media_downloaded": False,
        "episode_dirs_created": False,
        "health": "ready" if packets else "blocked_by_no_ready_episode_plan",
        "packet_ids": [packet["inspection_packet_id"] for packet in packets],
    }


def build_gate_readback(
    *,
    packets: list[dict[str, Any]],
    blocked: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dry_run": True,
        "offline_first": True,
        "source_opened_by_worker": False,
        "network_required": False,
        "external_api_used": False,
        "media_downloaded": False,
        "source_video_downloaded": False,
        "source_audio_downloaded": False,
        "episode_dirs_created": False,
        "rights_manifest_created": False,
        "material_ledger_created": False,
        "fetch_receipt_created": False,
        "transcript_generated": False,
        "edit_pack_created": False,
        "render_generated": False,
        "thumbnail_generated": False,
        "oauth_or_credentials_used": False,
        "fetch_authorized": False,
        "rights_approved": False,
        "production_ready": False,
        "public_ready": False,
        "public_use_permission": False,
        "inspectable_packet_count": len(packets),
        "blocked_skipped_count": len(blocked),
        "readback_note": (
            "CPD-05 writes source inspection packets and a blank decision template only. "
            "Opening source pages, authorizing a future private fetch, real episode init, "
            "rights approval, production readiness, and public readiness remain separate steps."
        ),
    }


def render_source_inspection_dashboard_html(
    *,
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    decision_template_path: Path,
    base_dir: Path,
) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>CPD-05 Source Inspection Packet</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,'Yu Gothic','Meiryo',sans-serif;margin:24px;line-height:1.5;color:#1f2933;background:#f7f8fa}",
            "main{max-width:1240px;margin:0 auto}",
            "section{margin:18px 0;padding:16px;background:#fff;border:1px solid #d8dde5;border-radius:8px}",
            "h1{font-size:28px;margin:0 0 6px}h2{font-size:19px;margin:0 0 12px}h3{font-size:16px;margin:0 0 8px}",
            "table{width:100%;border-collapse:collapse;font-size:14px;table-layout:fixed}",
            "th,td{border-bottom:1px solid #e5e8ee;padding:8px;text-align:left;vertical-align:top;overflow-wrap:anywhere}",
            "th{background:#eef3f8}.muted{color:#5f6b7a}.gate{border-color:#e3b341;background:#fffaf0}",
            ".ok{color:#12633d;font-weight:700}.warn{color:#8a4b00;font-weight:700}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}",
            ".card{border:1px solid #d8dde5;border-radius:8px;padding:12px;background:#fbfcfe}code{background:#eef1f5;padding:2px 4px;border-radius:4px}",
            "ul{margin:6px 0 0 18px;padding:0}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>CPD-05 Source Inspection Packet v0</h1>",
            '<p class="muted">Local inspection packet only. The worker did not open source URLs, authorize future fetch, clear rights, create episode artifacts, or mark anything production/public ready.</p>',
            _summary_html(payload, output_path, dashboard_path, decision_template_path, base_dir),
            _packets_html(payload["source_inspection_packets"]),
            _blocked_html(payload["blocked_source_records"]),
            _gate_html(payload["gate_readback"]),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def normalize_rights_readback(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        status = clean_string(value.get("status")) or "unknown"
        source = clean_string(value.get("source")) or "episode_init_plan"
        notes = as_string_list(value.get("notes"))
    else:
        status = "unknown"
        source = "episode_init_plan"
        notes = []
    if status not in {"pending", "unverified", "unknown"}:
        notes.append(f"CPD-05 downgraded non-inspection rights status {status!r} to unverified")
        status = "unverified"
    return {
        "status": status,
        "source": source,
        "notes": notes,
        "approved": False,
        "hard_gate": False,
    }


def blocked_next_action(url_state: str, original_next_action: str) -> str:
    if url_state == "missing":
        return "add_source_url"
    if url_state == "present" and original_next_action:
        return "reject_or_defer"
    if url_state == "invalid":
        return "fix_source_url"
    return original_next_action or "needs_manual_review"


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if not isinstance(value, list):
        return [str(value)]
    return [str(item) for item in value if str(item).strip()]


def as_risk_flags(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def clean_string(value: Any) -> str:
    return str(value or "").strip()


def _summary_html(
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    decision_template_path: Path,
    base_dir: Path,
) -> str:
    summary = payload["summary"]
    return f"""
  <section>
    <h2>Generation Summary</h2>
    <table>
      <tr><th>artifact_id</th><td>{escape(payload["artifact_id"])}</td></tr>
      <tr><th>episode init plans read</th><td>{summary["episode_init_plan_count"]}</td></tr>
      <tr><th>inspectable source packets</th><td>{summary["inspectable_packet_count"]}</td></tr>
      <tr><th>blocked/skipped records</th><td>{summary["blocked_skipped_count"]}</td></tr>
      <tr><th>fetch authorized</th><td>false</td></tr>
      <tr><th>media downloaded</th><td>{str(summary["media_downloaded"]).lower()}</td></tr>
      <tr><th>episode dirs created</th><td>{str(summary["episode_dirs_created"]).lower()}</td></tr>
      <tr><th>machine JSON</th><td><code>{escape(display_path(output_path, base_dir))}</code></td></tr>
      <tr><th>decision template</th><td><code>{escape(display_path(decision_template_path, base_dir))}</code></td></tr>
      <tr><th>HTML</th><td><code>{escape(display_path(dashboard_path, base_dir))}</code></td></tr>
      <tr><th>input</th><td>{escape(payload["source"]["input_artifact"])}</td></tr>
    </table>
  </section>"""


def _packets_html(packets: list[dict[str, Any]]) -> str:
    if not packets:
        return """
  <section>
    <h2>Inspectable Packets</h2>
    <p class="warn">No ready CPD-04 episode init plan was available for source inspection.</p>
  </section>"""
    cards = []
    for packet in packets:
        checklist = "".join(
            f"<li>{escape(item['label'])}: {escape(item['state'])}</li>"
            for item in packet["operator_checklist"]
        )
        cards.append(
            f"""
      <div class="card">
        <h3>{escape(packet["inspection_packet_id"])}</h3>
        <table>
          <tr><th>Inspection Packet ID</th><td>{escape(packet["inspection_packet_id"])}</td></tr>
          <tr><th>Episode plan ID</th><td>{escape(packet["episode_plan_id"])}</td></tr>
          <tr><th>seed ID</th><td>{escape(packet["seed_id"])}</td></tr>
          <tr><th>Candidate ID</th><td>{escape(packet["candidate_id"])}</td></tr>
          <tr><th>Source URL</th><td>{escape(packet["source_url"])}</td></tr>
          <tr><th>video_id</th><td>{escape(packet["video_id"] or "-")}</td></tr>
          <tr><th>planned episode slug</th><td>{escape(packet["planned_episode_slug"])}</td></tr>
          <tr><th>inspection checklist</th><td><ul>{checklist}</ul></td></tr>
          <tr><th>decision state</th><td>{escape(packet["decision_state"])}</td></tr>
          <tr><th>fetch authorization</th><td>{str(packet["fetch_authorized"]).lower()}</td></tr>
          <tr><th>rights readback</th><td>{escape(packet["rights_readback"]["status"])} / approved=false</td></tr>
          <tr><th>next action</th><td class="ok">{escape(packet["next_action"])}</td></tr>
        </table>
      </div>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>Inspectable Packets</h2>",
            '    <div class="grid">',
            *cards,
            "    </div>",
            "  </section>",
        ]
    )


def _blocked_html(blocked: list[dict[str, Any]]) -> str:
    rows = []
    for item in blocked:
        rows.append(
            f"""
      <tr>
        <td><code>{escape(item["seed_id"])}</code><br>{escape(item["candidate_id"])}</td>
        <td>{escape(item["working_title"])}</td>
        <td>{escape(item["source_kind"])}</td>
        <td class="warn">{escape(item["source_url_state"])}</td>
        <td>{escape(item["blocked_reason"])}</td>
        <td>{escape(item["next_action"])}</td>
      </tr>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>Blocked / Skipped Source Records</h2>",
            "    <table>",
            "      <tr><th>seed / candidate</th><th>working title</th><th>source kind</th><th>URL state</th><th>blocked reason</th><th>next action</th></tr>",
            *rows,
            "    </table>",
            "  </section>",
        ]
    )


def _gate_html(gates: dict[str, Any]) -> str:
    return f"""
  <section class="gate">
    <h2>Gate Readback</h2>
    <table>
      <tr><th>dry_run</th><td>{str(gates["dry_run"]).lower()}</td></tr>
      <tr><th>source_opened_by_worker</th><td>{str(gates["source_opened_by_worker"]).lower()}</td></tr>
      <tr><th>network_required</th><td>{str(gates["network_required"]).lower()}</td></tr>
      <tr><th>external_api_used</th><td>{str(gates["external_api_used"]).lower()}</td></tr>
      <tr><th>media_downloaded</th><td>{str(gates["media_downloaded"]).lower()}</td></tr>
      <tr><th>episode_dirs_created</th><td>{str(gates["episode_dirs_created"]).lower()}</td></tr>
      <tr><th>created artifacts</th><td>rights_manifest=false; material_ledger=false; fetch_receipt=false; transcript=false; edit_pack=false; render=false; thumbnail=false</td></tr>
      <tr><th>production/public</th><td>fetch_authorized=false; rights_approved=false; production_ready=false; public_ready=false</td></tr>
      <tr><th>note</th><td>{escape(gates["readback_note"])}</td></tr>
    </table>
  </section>"""
