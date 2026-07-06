"""CPD-02 candidate-to-episode seed draft bridge.

This module converts CPD-01 candidate records into deterministic draft episode
seeds. It only writes review artifacts; it does not create episode folders,
fetch media, initialize rights manifests, build transcripts, edit packs,
renders, thumbnails, or publishing state.
"""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from typing import Any

from .content_planning import display_path, normalize_candidates, write_json, write_text

SCHEMA_ID = "clippipegen.episode_seed_bridge.v0"
DEFAULT_ARTIFACT_ID = "clip-cpd02-candidate-to-episode-seed-bridge-v0-001"
DEFAULT_GENERATED_AT = "2026-07-06"
DEFAULT_OUTPUT_FILENAME = "episode_seed_drafts.json"
DEFAULT_DASHBOARD_FILENAME = "episode_seed_dashboard.html"


class EpisodeSeedBridgeError(ValueError):
    """Raised when CPD-02 seed input cannot be used."""


def build_episode_seed_drafts(
    *,
    input_path: Path,
    output_path: Path,
    base_dir: Path,
    dashboard_path: Path | None = None,
    candidate_ids: list[str] | None = None,
    limit: int | None = None,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Read candidate JSON/fixture and write deterministic seed draft artifacts."""

    candidates, source = load_candidates(input_path, base_dir=base_dir)
    selected = select_candidates(candidates, candidate_ids=candidate_ids, limit=limit)
    if not selected:
        raise EpisodeSeedBridgeError("no candidates matched the requested selection")

    seeds = [
        build_seed(candidate, input_path=input_path, base_dir=base_dir, generated_at=generated_at)
        for candidate in selected
    ]
    payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": source,
        "selection": {
            "candidate_ids": candidate_ids or [],
            "limit": limit,
            "selected_count": len(seeds),
        },
        "gate_readback": build_gate_readback(seeds),
        "summary": summarize_seeds(seeds),
        "episode_seed_drafts": seeds,
    }
    write_json(payload, output_path)

    resolved_dashboard_path = dashboard_path or output_path.with_name(DEFAULT_DASHBOARD_FILENAME)
    write_text(
        render_episode_seed_dashboard_html(
            payload=payload,
            output_path=output_path,
            dashboard_path=resolved_dashboard_path,
            base_dir=base_dir,
        ),
        resolved_dashboard_path,
    )
    return {
        "artifact_id": artifact_id,
        "seed_count": len(seeds),
        "top_seed_id": seeds[0]["seed_id"],
        "output_path": output_path,
        "dashboard_path": resolved_dashboard_path,
        "payload": payload,
    }


def load_candidates(input_path: Path, *, base_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        with input_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise EpisodeSeedBridgeError(f"candidate input is not readable: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise EpisodeSeedBridgeError(f"candidate input is not valid JSON: {input_path}") from exc

    if isinstance(raw, list):
        raw = {"source_mode": "candidate_json", "candidates": raw}
    if not isinstance(raw, dict):
        raise EpisodeSeedBridgeError("candidate input root must be an object or list")

    if isinstance(raw.get("candidates"), list):
        candidates = raw["candidates"]
        input_kind = "candidate_json" if raw.get("schema_id") else "fixture"
    else:
        raise EpisodeSeedBridgeError("candidate input must contain candidates[]")

    if raw.get("schema_id") != "clippipegen.content_planning_dashboard.v0":
        candidates = normalize_candidates(raw)
        input_kind = "fixture"
    else:
        candidates = [candidate for candidate in candidates if isinstance(candidate, dict)]

    if not candidates:
        raise EpisodeSeedBridgeError("candidate input contains no usable candidates")

    candidates = sorted(
        candidates,
        key=lambda candidate: (-int(candidate.get("score_total") or 0), str(candidate.get("candidate_id") or "")),
    )
    return candidates, {
        "input_artifact": display_path(input_path, base_dir),
        "input_kind": input_kind,
        "source_schema_id": str(raw.get("schema_id") or ""),
        "network_required": False,
    }


def select_candidates(
    candidates: list[dict[str, Any]],
    *,
    candidate_ids: list[str] | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    if candidate_ids:
        requested = set(candidate_ids)
        selected = [
            candidate
            for candidate in candidates
            if str(candidate.get("candidate_id") or "") in requested
        ]
        missing = sorted(requested - {str(candidate.get("candidate_id") or "") for candidate in selected})
        if missing:
            raise EpisodeSeedBridgeError("candidate_id not found: " + ", ".join(missing))
    else:
        selected = list(candidates)
    if limit is not None:
        if limit <= 0:
            raise EpisodeSeedBridgeError("--limit must be greater than 0 when provided")
        selected = selected[:limit]
    return selected


def build_seed(
    candidate: dict[str, Any],
    *,
    input_path: Path,
    base_dir: Path,
    generated_at: str,
) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id") or "").strip()
    if not candidate_id:
        raise EpisodeSeedBridgeError("candidate_id is required for seed generation")

    seed_slug = slugify(candidate_id)
    seed_id = f"seed_{seed_slug}"
    episode_id = f"ep_seed_{seed_slug}"
    source_url = str(candidate.get("source_url") or "")
    rights = safe_rights(candidate.get("rights_readback"))
    risk_flags = candidate.get("risk_flags") if isinstance(candidate.get("risk_flags"), list) else []
    next_action = seed_next_action(candidate=candidate, rights=rights, risk_flags=risk_flags)
    duration_hint = duration_hint_from_candidate(candidate)

    return {
        "seed_id": seed_id,
        "candidate_id": candidate_id,
        "status": "draft",
        "generated_at": generated_at,
        "source_candidate_path": display_path(input_path, base_dir),
        "input_artifact": display_path(input_path, base_dir),
        "source_mode": str(candidate.get("source_mode") or "candidate_json"),
        "source_ref": str(candidate.get("source_ref") or source_url or ""),
        "source_url": source_url,
        "source_media_state": "not_fetched",
        "transcript_state": "needed" if source_url else "unavailable_until_source_ref_resolved",
        "rights_readback": rights,
        "episode_id_draft": episode_id,
        "title": str(candidate.get("title") or "untitled candidate"),
        "working_title": first_or_title(candidate),
        "title_hooks": list(candidate.get("title_hooks") or candidate.get("proposed_clip_titles") or []),
        "talent": list(candidate.get("talent") or []),
        "channel_name": str(candidate.get("channel_name") or "unknown"),
        "group": str(candidate.get("group") or "unknown"),
        "language": str(candidate.get("language") or "unknown"),
        "topic_tags": list(candidate.get("topic_tags") or []),
        "clip_angle": str(candidate.get("clip_angle") or ""),
        "target_clip_duration_hint": duration_hint,
        "expected_edit_value": str(candidate.get("expected_edit_value") or ""),
        "thumbnailability": str(candidate.get("thumbnailability") or ""),
        "editability": str(candidate.get("editability") or ""),
        "audience_fit": str(candidate.get("audience_fit") or ""),
        "risk_flags": risk_flags,
        "score_total": int(candidate.get("score_total") or 0),
        "score_components": dict(candidate.get("score_components") or {}),
        "source_inspection_checklist": source_inspection_checklist(candidate, rights),
        "proposed_edit_plan": proposed_edit_plan(candidate, duration_hint),
        "thumbnail_brief_seed": thumbnail_brief_seed(candidate),
        "later_artifact_paths": later_artifact_paths(episode_id),
        "output_plan": {
            "creates_files_now": False,
            "creates_episode_dir_now": False,
            "media_downloaded": False,
            "planned_episode_dir": f"episodes/{episode_id}",
            "planned_artifacts_only": True,
        },
        "next_action": next_action,
        "approval_state": {
            "seed_approved": False,
            "rights_cleared": False,
            "source_fetched": False,
            "production_ready": False,
            "public_ready": False,
            "publishing_accepted": False,
        },
    }


def build_gate_readback(seeds: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "offline_first": True,
        "network_required": False,
        "media_downloaded": False,
        "episode_dirs_created": False,
        "oauth_or_credentials_used": False,
        "production_candidate": False,
        "production_usage_allowed": False,
        "publishing_acceptance": False,
        "public_use_permission": False,
        "all_seed_statuses": sorted({str(seed.get("status")) for seed in seeds}),
        "readback_note": (
            "Episode seeds are draft planning records only. Later source fetch, "
            "rights, transcript, edit, thumbnail, render, and publishing steps remain gated."
        ),
    }


def summarize_seeds(seeds: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "seed_count": len(seeds),
        "top_seed_id": seeds[0]["seed_id"] if seeds else "",
        "source_url_known_count": sum(1 for seed in seeds if seed.get("source_url")),
        "needs_human_review_count": sum(
            1 for seed in seeds if str(seed.get("next_action")) == "needs_human_review"
        ),
        "hold_or_reject_count": sum(
            1 for seed in seeds if str(seed.get("next_action")) in {"hold", "reject"}
        ),
    }


def render_episode_seed_dashboard_html(
    *,
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    base_dir: Path,
) -> str:
    seeds = payload["episode_seed_drafts"]
    gates = payload["gate_readback"]
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>CPD-02 Episode Seed Drafts</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,'Yu Gothic','Meiryo',sans-serif;margin:24px;line-height:1.5;color:#1f2933;background:#f7f8fa}",
            "main{max-width:1180px;margin:0 auto}",
            "section{margin:18px 0;padding:16px;background:#fff;border:1px solid #d8dde5;border-radius:8px}",
            "h1{font-size:28px;margin:0 0 6px}h2{font-size:19px;margin:0 0 12px}h3{font-size:16px;margin:0 0 8px}",
            "table{width:100%;border-collapse:collapse;font-size:14px;table-layout:fixed}",
            "th,td{border-bottom:1px solid #e5e8ee;padding:8px;text-align:left;vertical-align:top;overflow-wrap:anywhere}",
            "th{background:#eef3f8}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}",
            ".card{border:1px solid #d8dde5;border-radius:8px;padding:12px;background:#fbfcfe}",
            ".badge{display:inline-block;border:1px solid #b8c7d9;background:#eef3fa;border-radius:999px;padding:2px 8px;margin:2px;font-size:12px}",
            ".gate{border-color:#e3b341;background:#fffaf0}.muted{color:#5f6b7a}.risk{color:#8a4b00}code{background:#eef1f5;padding:2px 4px;border-radius:4px}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>CPD-02 Candidate-to-Episode Seed Bridge v0</h1>",
            '<p class="muted">候補カードから作った draft seed です。動画・音声取得、episode 初期化、権利承認、制作承認は行っていません。</p>',
            _summary_html(payload, output_path, dashboard_path, base_dir),
            _seed_cards_html(seeds),
            _gate_html(gates),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "candidate"


def safe_rights(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        status = str(value.get("status") or "unknown")
        source = str(value.get("source") or "candidate")
        notes = value.get("notes") if isinstance(value.get("notes"), list) else []
    else:
        status = "unknown"
        source = "candidate"
        notes = []
    if status in {"approved", "cleared", "passed"}:
        status = "unverified"
        notes = [*notes, "CPD-02 does not carry rights approval into seed drafts"]
    return {
        "status": status,
        "source": source,
        "notes": [str(note) for note in notes],
        "hard_gate": False,
        "approved": False,
    }


def seed_next_action(
    *,
    candidate: dict[str, Any],
    rights: dict[str, Any],
    risk_flags: list[Any],
) -> str:
    candidate_next = str(candidate.get("next_action") or "").lower()
    risk_codes = {
        str(flag.get("code") or "")
        for flag in risk_flags
        if isinstance(flag, dict)
    }
    if "reject" in candidate_next:
        return "reject"
    if "hold" in candidate_next or "song_or_music_rights_sensitive" in risk_codes:
        return "hold"
    if not candidate.get("source_url"):
        return "needs_human_review"
    if rights.get("status") in {"unknown", "unverified"}:
        return "needs_human_review"
    return "inspect_source"


def duration_hint_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    tags = set(candidate.get("topic_tags") or [])
    if "short_anime" in tags or "fast_payoff" in tags:
        return {"target_seconds": 20, "min_seconds": 12, "max_seconds": 30}
    if "language_gap" in tags or "collab" in tags:
        return {"target_seconds": 35, "min_seconds": 20, "max_seconds": 55}
    if "gameplay" in tags:
        return {"target_seconds": 30, "min_seconds": 20, "max_seconds": 45}
    return {"target_seconds": 25, "min_seconds": 12, "max_seconds": 40}


def first_or_title(candidate: dict[str, Any]) -> str:
    hooks = candidate.get("title_hooks") or candidate.get("proposed_clip_titles") or []
    if hooks:
        return str(hooks[0])
    return str(candidate.get("title") or "untitled candidate")


def source_inspection_checklist(candidate: dict[str, Any], rights: dict[str, Any]) -> list[str]:
    checklist = [
        "confirm source URL/ref points to public inspectable material",
        "confirm source timestamp or narrow searchable moment before fetch",
        "check whether the clip angle has setup and payoff in one bounded window",
        "record rights/material-use readback before any production/public use",
    ]
    if not candidate.get("source_url"):
        checklist.insert(0, "resolve source URL before material fetch")
    if rights.get("status") != "pending":
        checklist.append("convert rights status from seed readback into real rights_manifest later")
    return checklist


def proposed_edit_plan(candidate: dict[str, Any], duration_hint: dict[str, Any]) -> dict[str, Any]:
    return {
        "nonbinding": True,
        "target_duration_seconds": duration_hint["target_seconds"],
        "outline": [
            "inspect source context and identify exact start/end later",
            "preserve one setup beat before the payoff",
            "draft subtitles from real transcript or official subtitle source later",
            "run context check before selecting a final cut candidate",
        ],
        "editing_intent": {
            "topic": str(candidate.get("clip_angle") or ""),
            "audience_note": str(candidate.get("audience_fit") or ""),
            "language": str(candidate.get("language") or "unknown"),
        },
    }


def thumbnail_brief_seed(candidate: dict[str, Any]) -> dict[str, Any]:
    hooks = list(candidate.get("title_hooks") or candidate.get("proposed_clip_titles") or [])
    return {
        "text_only": True,
        "not_image_generation": True,
        "primary_hook": hooks[0] if hooks else str(candidate.get("title") or ""),
        "supporting_hooks": hooks[1:3],
        "talent": list(candidate.get("talent") or []),
        "visual_direction_hint": str(candidate.get("thumbnailability") or ""),
        "topic_tags": list(candidate.get("topic_tags") or []),
    }


def later_artifact_paths(episode_id: str) -> dict[str, str]:
    root = f"episodes/{episode_id}"
    return {
        "episode_dir": root,
        "rights_manifest": f"{root}/rights_manifest.json",
        "material_ledger": f"{root}/material_ledger.json",
        "source_video_material": f"{root}/materials/src_video/source_video.mp4",
        "source_audio_material": f"{root}/materials/src_audio/source.wav",
        "transcript": f"{root}/transcript.json",
        "edit_pack": f"{root}/edit_pack.json",
        "preview_or_review_dir": f"{root}/review/",
    }


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
      <tr><th>seed 数</th><td>{summary["seed_count"]}</td></tr>
      <tr><th>top seed</th><td>{escape(summary["top_seed_id"])}</td></tr>
      <tr><th>machine JSON</th><td><code>{escape(display_path(output_path, base_dir))}</code></td></tr>
      <tr><th>HTML</th><td><code>{escape(display_path(dashboard_path, base_dir))}</code></td></tr>
      <tr><th>入力</th><td>{escape(payload["source"]["input_artifact"])}</td></tr>
    </table>
  </section>"""


def _seed_cards_html(seeds: list[dict[str, Any]]) -> str:
    cards = []
    for seed in seeds:
        risks = "<br>".join(
            escape(f"{flag.get('code')} ({flag.get('severity')}): {flag.get('note', '')}")
            for flag in seed.get("risk_flags", [])
            if isinstance(flag, dict)
        ) or "none"
        tags = "".join(
            f'<span class="badge">{escape(tag)}</span>'
            for tag in seed.get("topic_tags", [])
        )
        cards.append(
            f"""
      <div class="card">
        <h3>{escape(seed["seed_id"])}</h3>
        <table>
          <tr><th>候補ID</th><td>{escape(seed["candidate_id"])}</td></tr>
          <tr><th>予定タイトル</th><td>{escape(seed["working_title"])}</td></tr>
          <tr><th>切り抜き軸</th><td>{escape(seed["clip_angle"])}</td></tr>
          <tr><th>取得状態</th><td>{escape(seed["source_media_state"])}</td></tr>
          <tr><th>権利readback</th><td>{escape(seed["rights_readback"]["status"])}</td></tr>
          <tr><th>次アクション</th><td>{escape(seed["next_action"])}</td></tr>
          <tr><th>リスク</th><td class="risk">{risks}</td></tr>
          <tr><th>score</th><td>{seed["score_total"]}</td></tr>
          <tr><th>tags</th><td>{tags}</td></tr>
        </table>
      </div>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>Seed Draft Cards</h2>",
            '    <div class="grid">',
            *cards,
            "    </div>",
            "  </section>",
        ]
    )


def _gate_html(gates: dict[str, Any]) -> str:
    return f"""
  <section class="gate">
    <h2>ゲート readback</h2>
    <table>
      <tr><th>network_required</th><td>{str(gates["network_required"]).lower()}</td></tr>
      <tr><th>media_downloaded</th><td>{str(gates["media_downloaded"]).lower()}</td></tr>
      <tr><th>episode_dirs_created</th><td>{str(gates["episode_dirs_created"]).lower()}</td></tr>
      <tr><th>OAuth / credentials</th><td>{str(gates["oauth_or_credentials_used"]).lower()}</td></tr>
      <tr><th>production/public</th><td>production_candidate=false; production_usage_allowed=false; publishing_acceptance=false; public_use_permission=false</td></tr>
      <tr><th>note</th><td>{escape(gates["readback_note"])}</td></tr>
    </table>
  </section>"""
