"""CPD-03 source metadata resolver and manual source intake artifacts.

This module reads CPD-02 draft episode seeds and creates deterministic source
resolution records. It parses already-known URLs, prepares lookup/manual intake
readback for unresolved seeds, and writes review-only JSON/HTML artifacts.
It does not fetch media, call public APIs, create episode folders, generate
transcripts, render, thumbnail, publish, or approve rights.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .content_planning import display_path, write_json, write_text

SCHEMA_ID = "clippipegen.source_metadata_resolver.v0"
TEMPLATE_SCHEMA_ID = "clippipegen.source_metadata_registry.template.v0"
DEFAULT_ARTIFACT_ID = "clip-cpd03-source-metadata-resolver-v0-001"
DEFAULT_GENERATED_AT = "2026-07-06"
DEFAULT_OUTPUT_FILENAME = "episode_seed_source_resolution.json"
DEFAULT_DASHBOARD_FILENAME = "source_resolution_dashboard.html"
DEFAULT_REGISTRY_FILENAME = "source_metadata_registry.json"
DEFAULT_REGISTRY_TEMPLATE_FILENAME = "source_metadata_registry.template.json"

VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{6,}$")


class SourceMetadataResolverError(ValueError):
    """Raised when CPD-03 source resolution input cannot be used."""


def resolve_episode_seed_sources(
    *,
    input_path: Path,
    output_path: Path,
    base_dir: Path,
    dashboard_path: Path | None = None,
    registry_path: Path | None = None,
    registry_template_path: Path | None = None,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Read CPD-02 seeds and write source-resolution JSON/HTML artifacts."""

    seed_payload, seeds = load_episode_seed_drafts(input_path)
    registry_entries, registry_readback = load_manual_registry(
        registry_path,
        base_dir=base_dir,
    )
    records = [
        build_resolution_record(
            seed,
            registry_entry=registry_entries.get(str(seed.get("seed_id") or ""))
            or registry_entries.get(str(seed.get("candidate_id") or "")),
            generated_at=generated_at,
        )
        for seed in seeds
    ]
    payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": {
            "input_artifact": display_path(input_path, base_dir),
            "input_schema_id": str(seed_payload.get("schema_id") or ""),
            "input_artifact_id": str(seed_payload.get("artifact_id") or ""),
            "network_required": False,
        },
        "manual_registry": registry_readback,
        "summary": summarize_records(records),
        "gate_readback": build_gate_readback(records),
        "source_resolution_records": records,
    }
    write_json(payload, output_path)

    resolved_template_path = (
        registry_template_path
        or output_path.with_name(DEFAULT_REGISTRY_TEMPLATE_FILENAME)
    )
    template_payload = build_manual_registry_template(
        payload=payload,
        records=records,
        registry_path=registry_path,
        output_path=output_path,
        base_dir=base_dir,
        generated_at=generated_at,
    )
    write_json(template_payload, resolved_template_path)

    resolved_dashboard_path = dashboard_path or output_path.with_name(DEFAULT_DASHBOARD_FILENAME)
    write_text(
        render_source_resolution_dashboard_html(
            payload=payload,
            output_path=output_path,
            dashboard_path=resolved_dashboard_path,
            registry_template_path=resolved_template_path,
            base_dir=base_dir,
        ),
        resolved_dashboard_path,
    )

    return {
        "artifact_id": artifact_id,
        "record_count": len(records),
        "resolved_count": payload["summary"]["resolved_source_url_count"],
        "manual_intake_required_count": payload["summary"]["manual_intake_required_count"],
        "output_path": output_path,
        "dashboard_path": resolved_dashboard_path,
        "registry_template_path": resolved_template_path,
        "payload": payload,
    }


def load_episode_seed_drafts(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise SourceMetadataResolverError(f"episode seed input is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SourceMetadataResolverError(f"episode seed input is not valid JSON: {path}") from exc

    if isinstance(raw, list):
        raw = {"schema_id": "", "artifact_id": "", "episode_seed_drafts": raw}
    if not isinstance(raw, dict):
        raise SourceMetadataResolverError("episode seed input root must be an object or list")

    seeds = raw.get("episode_seed_drafts")
    if not isinstance(seeds, list):
        raise SourceMetadataResolverError("episode seed input must contain episode_seed_drafts[]")

    usable = [seed for seed in seeds if isinstance(seed, dict)]
    if not usable:
        raise SourceMetadataResolverError("episode seed input contains no usable seed records")
    for seed in usable:
        if not str(seed.get("seed_id") or "").strip():
            raise SourceMetadataResolverError("every seed record must contain seed_id")
        if not str(seed.get("candidate_id") or "").strip():
            raise SourceMetadataResolverError("every seed record must contain candidate_id")
    return raw, usable


def load_manual_registry(
    path: Path | None,
    *,
    base_dir: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if path is None:
        return {}, {
            "path": "",
            "exists": False,
            "entry_count": 0,
            "readback_note": "manual registry not requested; unresolved sources remain intake tasks",
        }
    if not path.exists():
        return {}, {
            "path": display_path(path, base_dir),
            "exists": False,
            "entry_count": 0,
            "readback_note": "manual registry file is absent; template output shows required fields",
        }
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise SourceMetadataResolverError(f"manual source registry is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SourceMetadataResolverError(f"manual source registry is not valid JSON: {path}") from exc
    if not isinstance(raw, dict):
        raise SourceMetadataResolverError("manual source registry root must be an object")

    entries = raw.get("entries")
    if isinstance(entries, dict):
        entries = list(entries.values())
    if not isinstance(entries, list):
        raise SourceMetadataResolverError("manual source registry must contain entries[]")

    by_key: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        seed_id = str(entry.get("seed_id") or "").strip()
        candidate_id = str(entry.get("candidate_id") or "").strip()
        if seed_id:
            by_key[seed_id] = entry
        if candidate_id:
            by_key[candidate_id] = entry
    return by_key, {
        "path": display_path(path, base_dir),
        "exists": True,
        "entry_count": sum(1 for entry in entries if isinstance(entry, dict)),
        "readback_note": "manual registry was read locally; no network/API/OAuth lookup was performed",
    }


def build_resolution_record(
    seed: dict[str, Any],
    *,
    registry_entry: dict[str, Any] | None,
    generated_at: str,
) -> dict[str, Any]:
    seed_id = str(seed.get("seed_id") or "").strip()
    candidate_id = str(seed.get("candidate_id") or "").strip()
    seed_source_url = clean_string(seed.get("source_url"))
    registry_source_url = clean_string((registry_entry or {}).get("source_url"))
    source_url = seed_source_url or registry_source_url
    source_url_origin = (
        "episode_seed_drafts"
        if seed_source_url
        else "manual_registry"
        if registry_source_url
        else "missing"
    )
    parsed = parse_source_url(source_url)
    metadata_state = source_metadata_state(parsed["source_url_state"], source_url_origin)
    lookup_terms = build_lookup_terms(seed)
    manual_required = parsed["source_url_state"] != "present"
    confidence = source_confidence(parsed["source_url_state"], source_url_origin)
    rights = normalize_rights_readback(seed.get("rights_readback"))
    next_action = source_next_action(
        url_state=parsed["source_url_state"],
        seed_next_action=clean_string(seed.get("next_action")),
        source_url_origin=source_url_origin,
    )

    return {
        "resolution_id": f"source_resolution_{slugify(seed_id)}",
        "seed_id": seed_id,
        "candidate_id": candidate_id,
        "generated_at": generated_at,
        "working_title": clean_string(seed.get("working_title") or seed.get("title")),
        "candidate_title": clean_string(seed.get("title")),
        "talent": as_string_list(seed.get("talent")),
        "candidate_channel_name": clean_string(seed.get("channel_name")),
        "group": clean_string(seed.get("group")),
        "language": clean_string(seed.get("language")),
        "topic_tags": as_string_list(seed.get("topic_tags")),
        "source_ref": clean_string(seed.get("source_ref")),
        "source_url": source_url,
        "source_url_origin": source_url_origin,
        "source_url_state": parsed["source_url_state"],
        "source_platform": parsed["source_platform"],
        "video_id": parsed["video_id"],
        "url_parse_note": parsed["note"],
        "source_media_state": "not_fetched",
        "source_metadata_state": metadata_state,
        "registry_entry_used": bool(registry_entry and not seed_source_url and registry_source_url),
        "manual_intake_required": manual_required,
        "manual_intake_fields_needed": manual_intake_fields(parsed["source_url_state"]),
        "lookup_query": " ".join(lookup_terms),
        "lookup_terms": lookup_terms,
        "confidence": confidence,
        "rights_readback": rights,
        "approval_state": {
            "source_resolved_for_planning": parsed["source_url_state"] == "present",
            "source_fetched": False,
            "rights_cleared": False,
            "production_ready": False,
            "public_ready": False,
            "publishing_accepted": False,
        },
        "blocking_reason": blocking_reason(parsed["source_url_state"]),
        "next_action": next_action,
        "risk_flags": as_risk_flags(seed.get("risk_flags")),
        "later_artifact_paths": dict(seed.get("later_artifact_paths") or {}),
        "planned_later_artifacts_only": True,
    }


def parse_source_url(source_url: str) -> dict[str, str]:
    if not source_url:
        return {
            "source_url_state": "missing",
            "source_platform": "unknown",
            "video_id": "",
            "note": "source_url is empty",
        }

    parsed = urlparse(source_url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return {
            "source_url_state": "invalid",
            "source_platform": "unknown",
            "video_id": "",
            "note": "source_url must be an http(s) URL",
        }

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.startswith("m."):
        host = host[2:]

    if host == "youtu.be":
        video_id = first_path_segment(parsed.path)
        return youtube_parse_result(video_id)

    if host == "youtube.com" or host.endswith(".youtube.com"):
        video_id = ""
        path = parsed.path.strip("/")
        if path == "watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif path.startswith(("shorts/", "live/", "embed/")):
            video_id = path.split("/", 1)[1].split("/", 1)[0]
        result = youtube_parse_result(video_id)
        if result["source_url_state"] == "present":
            return result
        return {
            "source_url_state": "invalid",
            "source_platform": "youtube",
            "video_id": "",
            "note": "youtube URL is missing a parseable video id",
        }

    return {
        "source_url_state": "present",
        "source_platform": "other_web",
        "video_id": "",
        "note": "non-youtube http(s) source URL present; video_id not parsed",
    }


def youtube_parse_result(video_id: str) -> dict[str, str]:
    if VIDEO_ID_PATTERN.match(video_id or ""):
        return {
            "source_url_state": "present",
            "source_platform": "youtube",
            "video_id": video_id,
            "note": "youtube video_id parsed from URL",
        }
    return {
        "source_url_state": "invalid",
        "source_platform": "youtube",
        "video_id": "",
        "note": "youtube video_id is missing or invalid",
    }


def build_manual_registry_template(
    *,
    payload: dict[str, Any],
    records: list[dict[str, Any]],
    registry_path: Path | None,
    output_path: Path,
    base_dir: Path,
    generated_at: str,
) -> dict[str, Any]:
    intake_records = [
        record
        for record in records
        if record["manual_intake_required"]
    ]
    return {
        "schema_id": TEMPLATE_SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": f"{payload['artifact_id']}-manual-registry-template",
        "generated_at": generated_at,
        "source_resolution_artifact": display_path(output_path, base_dir),
        "target_registry_path": display_path(
            registry_path or output_path.with_name(DEFAULT_REGISTRY_FILENAME),
            base_dir,
        ),
        "instructions": [
            "Fill only with real, human-confirmed public source metadata.",
            "Leave source_url empty until a real source URL is known.",
            "Do not paste downloaded media paths, OAuth data, cookies, or credentials.",
            "This registry is input to a later local resolver run; it is not rights approval.",
        ],
        "entry_count": len(intake_records),
        "entries": [
            {
                "seed_id": record["seed_id"],
                "candidate_id": record["candidate_id"],
                "candidate_working_title": record["working_title"],
                "source_ref": record["source_ref"],
                "lookup_query": record["lookup_query"],
                "source_url": "",
                "source_title": "",
                "channel_name": "",
                "published_at": "",
                "duration_seconds": None,
                "timestamp_hint": "",
                "verification_status": "unverified",
                "operator_source": "manual",
                "rights_readback_note": "",
                "operator_notes": [],
            }
            for record in intake_records
        ],
    }


def render_source_resolution_dashboard_html(
    *,
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    registry_template_path: Path,
    base_dir: Path,
) -> str:
    records = payload["source_resolution_records"]
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>CPD-03 Source Metadata Resolution</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,'Yu Gothic','Meiryo',sans-serif;margin:24px;line-height:1.5;color:#1f2933;background:#f7f8fa}",
            "main{max-width:1240px;margin:0 auto}",
            "section{margin:18px 0;padding:16px;background:#fff;border:1px solid #d8dde5;border-radius:8px}",
            "h1{font-size:28px;margin:0 0 6px}h2{font-size:19px;margin:0 0 12px}",
            "table{width:100%;border-collapse:collapse;font-size:14px;table-layout:fixed}",
            "th,td{border-bottom:1px solid #e5e8ee;padding:8px;text-align:left;vertical-align:top;overflow-wrap:anywhere}",
            "th{background:#eef3f8}.muted{color:#5f6b7a}.gate{border-color:#e3b341;background:#fffaf0}",
            ".ok{color:#12633d;font-weight:700}.warn{color:#8a4b00;font-weight:700}.bad{color:#8a1f11;font-weight:700}",
            "code{background:#eef1f5;padding:2px 4px;border-radius:4px}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>CPD-03 Source Metadata Resolver v0</h1>",
            '<p class="muted">episode seed の source URL 状態を読み取り、未解決 seed の手入力 intake を作るレビュー専用画面です。動画・音声取得、API/OAuth、episode 初期化、権利承認、公開承認は行っていません。</p>',
            _summary_html(payload, output_path, dashboard_path, registry_template_path, base_dir),
            _records_table_html(records),
            _gate_html(payload["gate_readback"]),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    states = Counter(str(record.get("source_url_state") or "unknown") for record in records)
    confidence = Counter(str(record.get("confidence") or "unknown") for record in records)
    metadata = Counter(str(record.get("source_metadata_state") or "unknown") for record in records)
    return {
        "record_count": len(records),
        "resolved_source_url_count": states.get("present", 0),
        "source_url_present_count": states.get("present", 0),
        "source_url_missing_count": states.get("missing", 0),
        "source_url_invalid_count": states.get("invalid", 0),
        "manual_intake_required_count": sum(
            1 for record in records if record.get("manual_intake_required")
        ),
        "registry_entry_used_count": sum(
            1 for record in records if record.get("registry_entry_used")
        ),
        "confidence_counts": dict(sorted(confidence.items())),
        "source_metadata_state_counts": dict(sorted(metadata.items())),
    }


def build_gate_readback(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "offline_first": True,
        "network_required": False,
        "external_api_used": False,
        "media_downloaded": False,
        "source_video_downloaded": False,
        "source_audio_downloaded": False,
        "episode_dirs_created": False,
        "transcript_generated": False,
        "render_generated": False,
        "thumbnail_generated": False,
        "oauth_or_credentials_used": False,
        "rights_approved": False,
        "production_candidate": False,
        "production_usage_allowed": False,
        "publishing_acceptance": False,
        "public_use_permission": False,
        "all_source_media_states": sorted(
            {str(record.get("source_media_state")) for record in records}
        ),
        "readback_note": (
            "CPD-03 records source URL resolution only. Manual metadata can make a "
            "later local dry-run easier, but it is not material fetch, rights "
            "approval, production approval, or public-use acceptance."
        ),
    }


def source_metadata_state(url_state: str, source_url_origin: str) -> str:
    if url_state == "present" and source_url_origin == "episode_seed_drafts":
        return "resolved_from_seed_url"
    if url_state == "present" and source_url_origin == "manual_registry":
        return "resolved_from_manual_registry"
    if url_state == "invalid":
        return "invalid_source_url"
    return "unresolved_missing_source_url"


def source_confidence(url_state: str, source_url_origin: str) -> str:
    if url_state == "present" and source_url_origin == "episode_seed_drafts":
        return "seed_url_exact"
    if url_state == "present" and source_url_origin == "manual_registry":
        return "manual_registry_url"
    if url_state == "invalid":
        return "invalid_url"
    return "query_only"


def manual_intake_fields(url_state: str) -> list[str]:
    if url_state == "present":
        return []
    if url_state == "invalid":
        return [
            "valid_source_url",
            "source_title",
            "channel_name",
            "published_at",
            "duration_seconds_or_timestamp_hint",
            "rights_readback_note",
        ]
    return [
        "source_url",
        "source_title",
        "channel_name",
        "published_at",
        "duration_seconds_or_timestamp_hint",
        "rights_readback_note",
    ]


def source_next_action(
    *,
    url_state: str,
    seed_next_action: str,
    source_url_origin: str,
) -> str:
    if seed_next_action in {"hold", "reject"} and url_state != "present":
        return f"{seed_next_action}_until_source_route_reopened"
    if url_state == "present" and source_url_origin == "manual_registry":
        return "review_manual_registry_source_before_fetch"
    if url_state == "present":
        return "ready_for_source_inspection_without_fetch"
    if url_state == "invalid":
        return "fix_manual_source_url"
    return "manual_source_intake_required"


def blocking_reason(url_state: str) -> str:
    if url_state == "present":
        return ""
    if url_state == "invalid":
        return "source_url is present but not parseable as a valid inspectable URL"
    return "source_url is missing; manual source intake is required before fetch/init lanes"


def normalize_rights_readback(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        status = clean_string(value.get("status")) or "unknown"
        source = clean_string(value.get("source")) or "episode_seed_drafts"
        notes = as_string_list(value.get("notes"))
    else:
        status = "unknown"
        source = "episode_seed_drafts"
        notes = []
    return {
        "status": status,
        "source": source,
        "notes": notes,
        "approved": False,
        "hard_gate": False,
    }


def build_lookup_terms(seed: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    add_term(terms, seed.get("working_title"))
    add_term(terms, seed.get("title"))
    for talent in as_string_list(seed.get("talent")):
        add_term(terms, talent)
    channel = clean_string(seed.get("channel_name"))
    if channel and channel.lower() not in {"unknown", "unknown fixture channel"}:
        add_term(terms, channel)
    add_term(terms, seed.get("group"))
    add_term(terms, seed.get("source_ref"))
    for tag in as_string_list(seed.get("topic_tags"))[:4]:
        add_term(terms, tag)
    if not terms:
        terms.append(clean_string(seed.get("candidate_id")) or clean_string(seed.get("seed_id")))
    return terms[:12]


def add_term(terms: list[str], value: Any) -> None:
    term = clean_string(value)
    if term and term not in terms:
        terms.append(term)


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


def first_path_segment(path: str) -> str:
    return path.strip("/").split("/", 1)[0]


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "seed"


def _summary_html(
    payload: dict[str, Any],
    output_path: Path,
    dashboard_path: Path,
    registry_template_path: Path,
    base_dir: Path,
) -> str:
    summary = payload["summary"]
    return f"""
  <section>
    <h2>生成サマリー</h2>
    <table>
      <tr><th>artifact_id</th><td>{escape(payload["artifact_id"])}</td></tr>
      <tr><th>source records</th><td>{summary["record_count"]}</td></tr>
      <tr><th>URL 解決済み</th><td>{summary["resolved_source_url_count"]}</td></tr>
      <tr><th>URL 未入力</th><td>{summary["source_url_missing_count"]}</td></tr>
      <tr><th>手入力が必要</th><td>{summary["manual_intake_required_count"]}</td></tr>
      <tr><th>machine JSON</th><td><code>{escape(display_path(output_path, base_dir))}</code></td></tr>
      <tr><th>HTML</th><td><code>{escape(display_path(dashboard_path, base_dir))}</code></td></tr>
      <tr><th>manual registry template</th><td><code>{escape(display_path(registry_template_path, base_dir))}</code></td></tr>
      <tr><th>入力</th><td>{escape(payload["source"]["input_artifact"])}</td></tr>
    </table>
  </section>"""


def _records_table_html(records: list[dict[str, Any]]) -> str:
    rows = []
    for record in records:
        state_class = {
            "present": "ok",
            "missing": "warn",
            "invalid": "bad",
        }.get(record["source_url_state"], "warn")
        rows.append(
            f"""
      <tr>
        <td><code>{escape(record["seed_id"])}</code><br>{escape(record["candidate_id"])}</td>
        <td>{escape(record["working_title"])}</td>
        <td class="{state_class}">{escape(record["source_url_state"])}<br><span class="muted">{escape(record["source_url_origin"])}</span></td>
        <td>{escape(record["source_url"] or "(missing)")}</td>
        <td>{escape(record["video_id"] or "-")}</td>
        <td>{escape(record["lookup_query"])}</td>
        <td>{str(record["manual_intake_required"]).lower()}<br><span class="muted">{escape(", ".join(record["manual_intake_fields_needed"]))}</span></td>
        <td>{escape(record["confidence"])}</td>
        <td>{escape(record["next_action"])}</td>
        <td>source_media_state={escape(record["source_media_state"])}<br>rights_approved={str(record["rights_readback"]["approved"]).lower()}<br>public_ready={str(record["approval_state"]["public_ready"]).lower()}</td>
      </tr>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>Source Resolution Records</h2>",
            "    <table>",
            "      <tr><th>seed / candidate</th><th>予定タイトル</th><th>元動画URL状態</th><th>source_url</th><th>video_id</th><th>検索query</th><th>手入力</th><th>信頼度</th><th>次アクション</th><th>権利・取得状態</th></tr>",
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
      <tr><th>network_required</th><td>{str(gates["network_required"]).lower()}</td></tr>
      <tr><th>external_api_used</th><td>{str(gates["external_api_used"]).lower()}</td></tr>
      <tr><th>media_downloaded</th><td>{str(gates["media_downloaded"]).lower()}</td></tr>
      <tr><th>episode_dirs_created</th><td>{str(gates["episode_dirs_created"]).lower()}</td></tr>
      <tr><th>OAuth / credentials</th><td>{str(gates["oauth_or_credentials_used"]).lower()}</td></tr>
      <tr><th>generated outputs</th><td>transcript=false; render=false; thumbnail=false</td></tr>
      <tr><th>production/public</th><td>rights_approved=false; production_candidate=false; publishing_acceptance=false; public_use_permission=false</td></tr>
      <tr><th>note</th><td>{escape(gates["readback_note"])}</td></tr>
    </table>
  </section>"""
