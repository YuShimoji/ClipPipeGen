"""CPD-04 dry-run episode initialization plan builder.

This module reads CPD-03 source resolution records and produces deterministic
episode initialization plans for records with usable source URLs. It only writes
review artifacts under docs/content_planning; it never creates episode
directories, media files, transcripts, edit packs, material ledgers, receipts,
renders, thumbnails, uploads, or rights/public approval.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any

from .content_planning import display_path, write_json, write_text

SCHEMA_ID = "clippipegen.episode_init_plan.v0"
DEFAULT_ARTIFACT_ID = "clip-cpd04-init-episode-dry-run-plan-v0-001"
DEFAULT_GENERATED_AT = "2026-07-06"
DEFAULT_OUTPUT_FILENAME = "episode_init_plan.json"
DEFAULT_DASHBOARD_FILENAME = "episode_init_plan_dashboard.html"


class EpisodeInitPlanError(ValueError):
    """Raised when CPD-04 source resolution input cannot be used."""


def build_episode_init_plan(
    *,
    input_path: Path,
    output_path: Path,
    base_dir: Path,
    dashboard_path: Path | None = None,
    seed_input_path: Path | None = None,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Read CPD-03 source resolution JSON and write dry-run init plans."""

    source_payload, records = load_source_resolution_records(input_path)
    seed_index, seed_readback = load_seed_index(seed_input_path, base_dir=base_dir)
    ready_records = [record for record in records if is_ready_source_record(record)]
    skipped_records = [record for record in records if not is_ready_source_record(record)]
    plans = [
        build_plan_record(
            record,
            seed=seed_index.get(str(record.get("seed_id") or "")),
            generated_at=generated_at,
        )
        for record in ready_records
    ]
    skipped = [
        build_skipped_record(record, generated_at=generated_at)
        for record in skipped_records
    ]
    payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": {
            "input_artifact": display_path(input_path, base_dir),
            "input_schema_id": str(source_payload.get("schema_id") or ""),
            "input_artifact_id": str(source_payload.get("artifact_id") or ""),
            "seed_enrichment": seed_readback,
            "network_required": False,
        },
        "summary": summarize(plans, skipped, records),
        "gate_readback": build_gate_readback(plans, skipped),
        "episode_init_plans": plans,
        "skipped_source_records": skipped,
    }
    write_json(payload, output_path)

    resolved_dashboard_path = dashboard_path or output_path.with_name(DEFAULT_DASHBOARD_FILENAME)
    write_text(
        render_episode_init_plan_dashboard_html(
            payload=payload,
            output_path=output_path,
            dashboard_path=resolved_dashboard_path,
            base_dir=base_dir,
        ),
        resolved_dashboard_path,
    )
    return {
        "artifact_id": artifact_id,
        "record_count": len(records),
        "ready_plan_count": len(plans),
        "skipped_unresolved_count": len(skipped),
        "output_path": output_path,
        "dashboard_path": resolved_dashboard_path,
        "payload": payload,
    }


def load_source_resolution_records(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise EpisodeInitPlanError(f"source resolution input is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EpisodeInitPlanError(f"source resolution input is not valid JSON: {path}") from exc

    if isinstance(raw, list):
        raw = {"schema_id": "", "artifact_id": "", "source_resolution_records": raw}
    if not isinstance(raw, dict):
        raise EpisodeInitPlanError("source resolution input root must be an object or list")

    records = raw.get("source_resolution_records")
    if not isinstance(records, list):
        raise EpisodeInitPlanError("source resolution input must contain source_resolution_records[]")

    usable = [record for record in records if isinstance(record, dict)]
    if not usable:
        raise EpisodeInitPlanError("source resolution input contains no usable records")
    for record in usable:
        if not str(record.get("resolution_id") or "").strip():
            raise EpisodeInitPlanError("every source resolution record must contain resolution_id")
        if not str(record.get("seed_id") or "").strip():
            raise EpisodeInitPlanError("every source resolution record must contain seed_id")
        if not str(record.get("candidate_id") or "").strip():
            raise EpisodeInitPlanError("every source resolution record must contain candidate_id")
    return raw, usable


def load_seed_index(
    path: Path | None,
    *,
    base_dir: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if path is None:
        return {}, {
            "path": "",
            "exists": False,
            "seed_count": 0,
            "readback_note": "seed enrichment not requested",
        }
    if not path.exists():
        return {}, {
            "path": display_path(path, base_dir),
            "exists": False,
            "seed_count": 0,
            "readback_note": "seed enrichment file is absent; init plans use source resolution fields only",
        }
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise EpisodeInitPlanError(f"episode seed input is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EpisodeInitPlanError(f"episode seed input is not valid JSON: {path}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("episode_seed_drafts"), list):
        raise EpisodeInitPlanError("episode seed enrichment must contain episode_seed_drafts[]")
    seeds = [seed for seed in raw["episode_seed_drafts"] if isinstance(seed, dict)]
    return {
        str(seed.get("seed_id") or ""): seed
        for seed in seeds
        if str(seed.get("seed_id") or "")
    }, {
        "path": display_path(path, base_dir),
        "exists": True,
        "seed_count": len(seeds),
        "readback_note": "seed enrichment read locally; no network/API/OAuth lookup was performed",
    }


def is_ready_source_record(record: dict[str, Any]) -> bool:
    return str(record.get("source_url_state") or "") == "present" and bool(
        str(record.get("source_url") or record.get("video_id") or "").strip()
    )


def build_plan_record(
    record: dict[str, Any],
    *,
    seed: dict[str, Any] | None,
    generated_at: str,
) -> dict[str, Any]:
    seed_id = clean_string(record.get("seed_id"))
    candidate_id = clean_string(record.get("candidate_id"))
    slug = planned_episode_slug(record, seed=seed)
    root = planned_episode_root(record, slug)
    rights = normalize_rights_readback(record.get("rights_readback"))
    return {
        "episode_plan_id": f"episode_init_plan_{slug}",
        "source_resolution_id": clean_string(record.get("resolution_id")),
        "seed_id": seed_id,
        "candidate_id": candidate_id,
        "generated_at": generated_at,
        "working_title": clean_string(record.get("working_title")),
        "planned_episode_slug": slug,
        "talent": as_string_list(record.get("talent")),
        "channel_name": clean_string(record.get("candidate_channel_name")),
        "group": clean_string(record.get("group")),
        "language": clean_string(record.get("language")),
        "source_url": clean_string(record.get("source_url")),
        "video_id": clean_string(record.get("video_id")),
        "source_url_state": clean_string(record.get("source_url_state")),
        "source_metadata_state": clean_string(record.get("source_metadata_state")),
        "source_media_state": "not_fetched",
        "transcript_state": "not_generated",
        "material_ledger_state": "planned_only",
        "edit_pack_state": "planned_only",
        "thumbnail_state": "planned_only",
        "dry_run": True,
        "ready_for_real_init": True,
        "blocked_reason": "",
        "approved": False,
        "public_ready": False,
        "production_ready": False,
        "planned_episode_root": root,
        "planned_artifacts": planned_artifacts(root),
        "source_inspection_plan": source_inspection_plan(record, slug),
        "proposed_clip_scope": proposed_clip_scope(seed),
        "risk_flags": as_risk_flags(record.get("risk_flags")),
        "rights_readback": rights,
        "gates": {
            "fetch_required_later": True,
            "manual_source_review_required": True,
            "rights_review_required_later": True,
            "public_upload_forbidden_now": True,
        },
        "next_action": "ready_for_operator_source_inspection",
    }


def build_skipped_record(record: dict[str, Any], *, generated_at: str) -> dict[str, Any]:
    url_state = clean_string(record.get("source_url_state")) or "unknown"
    source_next_action = clean_string(record.get("next_action"))
    return {
        "source_resolution_id": clean_string(record.get("resolution_id")),
        "seed_id": clean_string(record.get("seed_id")),
        "candidate_id": clean_string(record.get("candidate_id")),
        "generated_at": generated_at,
        "working_title": clean_string(record.get("working_title")),
        "source_url": clean_string(record.get("source_url")),
        "video_id": clean_string(record.get("video_id")),
        "source_url_state": url_state,
        "source_metadata_state": clean_string(record.get("source_metadata_state")),
        "source_media_state": "not_fetched",
        "ready_for_real_init": False,
        "dry_run": True,
        "approved": False,
        "public_ready": False,
        "production_ready": False,
        "blocked_reason": clean_string(record.get("blocking_reason"))
        or "source record is not ready for dry-run episode initialization",
        "manual_intake_required": bool(record.get("manual_intake_required")),
        "manual_intake_fields_needed": as_string_list(record.get("manual_intake_fields_needed")),
        "next_action": skipped_next_action(url_state, source_next_action),
    }


def planned_episode_slug(record: dict[str, Any], *, seed: dict[str, Any] | None) -> str:
    if seed and seed.get("episode_id_draft"):
        return slugify(clean_string(seed["episode_id_draft"]))
    episode_dir = (record.get("later_artifact_paths") or {}).get("episode_dir")
    if episode_dir:
        return slugify(Path(str(episode_dir).replace("\\", "/")).name)
    return f"ep_seed_{slugify(clean_string(record.get('candidate_id')))}"


def planned_episode_root(record: dict[str, Any], slug: str) -> str:
    episode_dir = (record.get("later_artifact_paths") or {}).get("episode_dir")
    if episode_dir:
        return str(episode_dir).replace("\\", "/")
    return f"episodes/{slug}"


def planned_artifacts(root: str) -> dict[str, str]:
    root = root.rstrip("/")
    source_video_root = f"{root}/materials/src_video"
    source_audio_root = f"{root}/materials/src_audio"
    return {
        "rights_manifest_path": f"{root}/rights_manifest.json",
        "source_receipt_path": f"{source_video_root}/fetch_receipt.json",
        "source_video_receipt_path": f"{source_video_root}/fetch_receipt.json",
        "source_audio_receipt_path": f"{source_audio_root}/fetch_receipt.json",
        "source_video_material_path": f"{source_video_root}/source_video.mp4",
        "source_audio_material_path": f"{source_audio_root}/source.wav",
        "material_ledger_path": f"{root}/material_ledger.json",
        "transcript_path": f"{root}/transcript.json",
        "edit_pack_path": f"{root}/edit_pack.json",
        "subtitle_path": f"{root}/subtitles.json",
        "thumbnail_brief_path": f"{root}/thumbnail_brief.json",
        "preview_pack_path": f"{root}/review/preview_pack/preview_manifest.json",
    }


def source_inspection_plan(record: dict[str, Any], slug: str) -> dict[str, Any]:
    return {
        "what_to_inspect_later": [
            "confirm the source URL still points to the intended public source",
            "identify a bounded timestamp window before any fetch or transcript work",
            "record source title/channel/duration readback from a human-approved route",
            "preserve rights/material-use readback before any production or public use",
        ],
        "future_lane_needed": "source_inspection_then_asset_fetch",
        "manual_decisions_needed_before_fetch": [
            "operator confirms the source identity matches the candidate",
            "operator confirms rights status remains pending/unverified and not approved",
            "operator chooses whether to run a later real init-episode step",
        ],
        "future_commands_data_only": [
            f"DO_NOT_RUN_NOW: python -m src.cli.main init-episode --episode-id {slug}",
            f"DO_NOT_RUN_NOW: python -m src.cli.main fetch-source-video --episode-id {slug} --material-id src_video --mode <future_source_video_fetch_mode> --source-url <confirmed_source_url>",
            f"DO_NOT_RUN_NOW: python -m src.cli.main fetch-source-audio --episode-id {slug} --material-id src_audio --mode <future_source_audio_fetch_mode> --source-url <confirmed_source_url>",
        ],
        "source_url": clean_string(record.get("source_url")),
        "video_id": clean_string(record.get("video_id")),
    }


def proposed_clip_scope(seed: dict[str, Any] | None) -> dict[str, Any]:
    if not seed:
        return {
            "available": False,
            "clip_angle": "",
            "title_hooks": [],
            "duration_hint": {},
            "edit_plan_outline": [],
        }
    edit_plan = seed.get("proposed_edit_plan") if isinstance(seed.get("proposed_edit_plan"), dict) else {}
    return {
        "available": True,
        "clip_angle": clean_string(seed.get("clip_angle")),
        "title_hooks": as_string_list(seed.get("title_hooks")),
        "duration_hint": dict(seed.get("target_clip_duration_hint") or {}),
        "edit_plan_outline": as_string_list(edit_plan.get("outline")),
    }


def normalize_rights_readback(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        status = clean_string(value.get("status")) or "unknown"
        source = clean_string(value.get("source")) or "source_resolution"
        notes = as_string_list(value.get("notes"))
    else:
        status = "unknown"
        source = "source_resolution"
        notes = []
    if status not in {"pending", "unverified", "unknown"}:
        notes.append(f"CPD-04 downgrades non-planning rights status {status!r} to unverified")
        status = "unverified"
    return {
        "status": status,
        "source": source,
        "notes": notes,
        "approved": False,
        "hard_gate": False,
    }


def summarize(
    plans: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    states = Counter(str(record.get("source_url_state") or "unknown") for record in records)
    health = "ready" if plans else "blocked_by_no_resolved_source"
    return {
        "source_resolution_record_count": len(records),
        "ready_dry_run_plan_count": len(plans),
        "skipped_unresolved_count": len(skipped),
        "source_url_present_count": states.get("present", 0),
        "source_url_missing_count": states.get("missing", 0),
        "source_url_invalid_count": states.get("invalid", 0),
        "media_downloaded": False,
        "episode_dirs_created": False,
        "health": health,
        "planned_episode_roots": [plan["planned_episode_root"] for plan in plans],
    }


def build_gate_readback(
    plans: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dry_run": True,
        "offline_first": True,
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
        "rights_approved": False,
        "production_candidate": False,
        "production_ready": False,
        "publishing_acceptance": False,
        "public_ready": False,
        "public_use_permission": False,
        "ready_plan_count": len(plans),
        "skipped_unresolved_count": len(skipped),
        "readback_note": (
            "CPD-04 is a dry-run plan only. Planned episode paths are strings; "
            "real init-episode, source fetch, transcript, edit, thumbnail, render, "
            "publishing, and rights approval remain separate later gates."
        ),
    }


def render_episode_init_plan_dashboard_html(
    *,
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    base_dir: Path,
) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>CPD-04 Episode Init Dry-Run Plan</title>",
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
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>CPD-04 Init Episode Dry-Run Plan v0</h1>",
            '<p class="muted">source 解決済み seed だけを episode 初期化の dry-run 計画にしています。実 episode フォルダ、素材、台帳、receipt、transcript、edit_pack、thumbnail、render、upload、権利承認は作成していません。</p>',
            _summary_html(payload, output_path, dashboard_path, base_dir),
            _plans_html(payload["episode_init_plans"]),
            _skipped_html(payload["skipped_source_records"]),
            _gate_html(payload["gate_readback"]),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def skipped_next_action(url_state: str, source_next_action: str) -> str:
    if url_state == "missing":
        return "add_source_url"
    if url_state == "invalid":
        return "rerun_source_resolution"
    if "reject" in source_next_action or "hold" in source_next_action:
        return "defer_unresolved"
    return "needs_human_review"


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


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "episode"


def _summary_html(
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    base_dir: Path,
) -> str:
    summary = payload["summary"]
    return f"""
  <section>
    <h2>生成サマリー</h2>
    <table>
      <tr><th>artifact_id</th><td>{escape(payload["artifact_id"])}</td></tr>
      <tr><th>source resolution records read</th><td>{summary["source_resolution_record_count"]}</td></tr>
      <tr><th>ready dry-run plans</th><td>{summary["ready_dry_run_plan_count"]}</td></tr>
      <tr><th>skipped / unresolved</th><td>{summary["skipped_unresolved_count"]}</td></tr>
      <tr><th>media downloaded</th><td>{str(summary["media_downloaded"]).lower()}</td></tr>
      <tr><th>episode dirs created</th><td>{str(summary["episode_dirs_created"]).lower()}</td></tr>
      <tr><th>machine JSON</th><td><code>{escape(display_path(output_path, base_dir))}</code></td></tr>
      <tr><th>HTML</th><td><code>{escape(display_path(dashboard_path, base_dir))}</code></td></tr>
      <tr><th>入力</th><td>{escape(payload["source"]["input_artifact"])}</td></tr>
    </table>
  </section>"""


def _plans_html(plans: list[dict[str, Any]]) -> str:
    if not plans:
        return """
  <section>
    <h2>Ready Dry-Run Plans</h2>
    <p class="warn">source 解決済み record がないため、ready plan はありません。</p>
  </section>"""
    cards = []
    for plan in plans:
        artifacts = "<br>".join(
            f"{escape(key)}: <code>{escape(path)}</code>"
            for key, path in plan["planned_artifacts"].items()
        )
        cards.append(
            f"""
      <div class="card">
        <h3>{escape(plan["episode_plan_id"])}</h3>
        <table>
          <tr><th>Episode計画ID</th><td>{escape(plan["episode_plan_id"])}</td></tr>
          <tr><th>seed ID</th><td>{escape(plan["seed_id"])}</td></tr>
          <tr><th>候補ID</th><td>{escape(plan["candidate_id"])}</td></tr>
          <tr><th>予定タイトル</th><td>{escape(plan["working_title"])}</td></tr>
          <tr><th>元動画URL</th><td>{escape(plan["source_url"])}</td></tr>
          <tr><th>video_id</th><td>{escape(plan["video_id"] or "-")}</td></tr>
          <tr><th>予定episode slug</th><td>{escape(plan["planned_episode_slug"])}</td></tr>
          <tr><th>予定成果物</th><td>{artifacts}</td></tr>
          <tr><th>取得状態</th><td>source_media_state={escape(plan["source_media_state"])}<br>material_ledger_state={escape(plan["material_ledger_state"])}<br>transcript_state={escape(plan["transcript_state"])}</td></tr>
          <tr><th>権利readback</th><td>{escape(plan["rights_readback"]["status"])} / approved=false</td></tr>
          <tr><th>次アクション</th><td class="ok">{escape(plan["next_action"])}</td></tr>
        </table>
      </div>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>Ready Dry-Run Plans</h2>",
            '    <div class="grid">',
            *cards,
            "    </div>",
            "  </section>",
        ]
    )


def _skipped_html(skipped: list[dict[str, Any]]) -> str:
    rows = []
    for item in skipped:
        rows.append(
            f"""
      <tr>
        <td><code>{escape(item["seed_id"])}</code><br>{escape(item["candidate_id"])}</td>
        <td>{escape(item["working_title"])}</td>
        <td class="warn">{escape(item["source_url_state"])}</td>
        <td>{escape(item["blocked_reason"])}</td>
        <td>{escape(item["next_action"])}</td>
      </tr>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>Skipped / Unresolved Source Records</h2>",
            "    <table>",
            "      <tr><th>seed / candidate</th><th>予定タイトル</th><th>元動画URL状態</th><th>blocked reason</th><th>次アクション</th></tr>",
            *rows,
            "    </table>",
            "  </section>",
        ]
    )


def _gate_html(gates: dict[str, Any]) -> str:
    return f"""
  <section class="gate">
    <h2>ゲート readback</h2>
    <table>
      <tr><th>dry_run</th><td>{str(gates["dry_run"]).lower()}</td></tr>
      <tr><th>network_required</th><td>{str(gates["network_required"]).lower()}</td></tr>
      <tr><th>external_api_used</th><td>{str(gates["external_api_used"]).lower()}</td></tr>
      <tr><th>media_downloaded</th><td>{str(gates["media_downloaded"]).lower()}</td></tr>
      <tr><th>episode_dirs_created</th><td>{str(gates["episode_dirs_created"]).lower()}</td></tr>
      <tr><th>created artifacts</th><td>rights_manifest=false; material_ledger=false; fetch_receipt=false; transcript=false; edit_pack=false; render=false; thumbnail=false</td></tr>
      <tr><th>production/public</th><td>rights_approved=false; production_ready=false; publishing_acceptance=false; public_ready=false</td></tr>
      <tr><th>note</th><td>{escape(gates["readback_note"])}</td></tr>
    </table>
  </section>"""
