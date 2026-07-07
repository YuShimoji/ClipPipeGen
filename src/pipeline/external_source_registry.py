"""HUB-01 offline external source registry builder.

This module normalizes local RSS/manual fixtures into a source candidate
registry. It never opens source URLs, fetches network RSS, downloads media,
calls public APIs, creates episode artifacts, approves rights, renders, or
publishes.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from .content_planning import display_path, write_json

SCHEMA_ID = "clippipegen.external_source_registry.v0"
DEFAULT_ARTIFACT_ID = "clip-hub01-external-source-registry-v0-001"
DEFAULT_GENERATED_AT = "2026-07-08"
DEFAULT_RSS_FIXTURE = Path("samples/external_sources/rss_fixture.xml")
DEFAULT_MANUAL_SEEDS = Path("samples/external_sources/manual_source_seeds.json")
DEFAULT_OUTPUT = Path("docs/external_sources/external_source_registry.json")

ALLOWED_STATES = {"source_candidate", "needs_review", "rejected", "hold"}


class ExternalSourceRegistryError(ValueError):
    """Raised when HUB-01 local fixture input cannot be normalized."""


def build_external_source_registry(
    *,
    rss_fixture_path: Path,
    manual_seeds_path: Path,
    output_path: Path,
    base_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Build a normalized offline source registry from local fixtures."""

    rss_records = load_rss_fixture(rss_fixture_path, generated_at=generated_at)
    manual_records = load_manual_source_seeds(manual_seeds_path, generated_at=generated_at)
    records = ensure_unique_candidate_ids([*rss_records, *manual_records])
    if not records:
        raise ExternalSourceRegistryError("external source registry requires at least one record")

    payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": {
            "rss_fixture": display_path(rss_fixture_path, base_dir),
            "manual_source_seeds": display_path(manual_seeds_path, base_dir),
            "network_required": False,
            "network_used": False,
            "parser": "python_stdlib_xml_etree",
        },
        "summary": summarize_records(records),
        "gate_readback": gate_readback(records),
        "external_source_records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(payload, output_path)
    return {
        "artifact_id": artifact_id,
        "record_count": len(records),
        "output_path": output_path,
        "payload": payload,
    }


def load_rss_fixture(path: Path, *, generated_at: str) -> list[dict[str, Any]]:
    try:
        tree = ET.parse(path)
    except OSError as exc:
        raise ExternalSourceRegistryError(f"RSS fixture is not readable: {path}") from exc
    except ET.ParseError as exc:
        raise ExternalSourceRegistryError(f"RSS fixture is not valid XML: {path}") from exc

    channel = tree.getroot().find("channel")
    if channel is None:
        raise ExternalSourceRegistryError("RSS fixture must contain channel")

    channel_title = child_text(channel, "title") or "unknown feed"
    language_hint = child_text(channel, "language")
    records = []
    for index, item in enumerate(channel.findall("item"), start=1):
        title = child_text(item, "title") or "untitled RSS item"
        source_url = child_text(item, "link")
        tags = [clean_string(category.text) for category in item.findall("category")]
        tags = [tag for tag in tags if tag]
        records.append(
            normalize_record(
                source_candidate_id=(
                    child_text(item, "guid")
                    or f"hub_rss_{index:03d}_{slugify(title)}"
                ),
                source_kind="rss_item",
                source_url=source_url,
                title=title,
                channel_or_feed=channel_title,
                published_at=child_text(item, "pubDate"),
                description=child_text(item, "description"),
                tags=tags,
                language_hint=language_hint or "unknown",
                source_confidence="fixture_metadata_unverified",
                candidate_state="source_candidate" if source_url else "needs_review",
                provenance="fixture",
                next_local_action="operator_source_review_required",
                generated_at=generated_at,
            )
        )
    return records


def load_manual_source_seeds(path: Path, *, generated_at: str) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise ExternalSourceRegistryError(f"manual source seeds are not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ExternalSourceRegistryError(f"manual source seeds are not valid JSON: {path}") from exc

    if isinstance(raw, list):
        seeds = raw
    elif isinstance(raw, dict):
        seeds = raw.get("seeds") or raw.get("entries")
    else:
        raise ExternalSourceRegistryError("manual source seeds root must be an object or list")
    if not isinstance(seeds, list):
        raise ExternalSourceRegistryError("manual source seeds must contain seeds[] or entries[]")

    records = []
    for index, seed in enumerate(seeds, start=1):
        if not isinstance(seed, dict):
            continue
        title = clean_string(seed.get("title")) or f"manual source seed {index}"
        state = clean_string(seed.get("candidate_state")) or "needs_review"
        if state not in ALLOWED_STATES:
            state = "needs_review"
        records.append(
            normalize_record(
                source_candidate_id=(
                    clean_string(seed.get("source_candidate_id"))
                    or clean_string(seed.get("candidate_id"))
                    or f"hub_manual_{index:03d}_{slugify(title)}"
                ),
                source_kind="manual_seed",
                source_url=clean_string(seed.get("source_url") or seed.get("url")),
                title=title,
                channel_or_feed=clean_string(seed.get("channel_or_feed") or seed.get("channel")),
                published_at=clean_string(seed.get("published_at")),
                description=clean_string(seed.get("description") or seed.get("notes")),
                tags=as_string_list(seed.get("tags") or seed.get("candidate_tags")),
                language_hint=clean_string(seed.get("language_hint") or seed.get("language")),
                source_confidence=clean_string(seed.get("source_confidence")) or "manual_seed_unverified",
                candidate_state=state,
                provenance=clean_string(seed.get("provenance")) or "manual_seed",
                next_local_action=(
                    clean_string(seed.get("next_local_action"))
                    or "operator_source_review_required"
                ),
                generated_at=generated_at,
            )
        )
    return records


def normalize_record(
    *,
    source_candidate_id: str,
    source_kind: str,
    source_url: str,
    title: str,
    channel_or_feed: str,
    published_at: str,
    description: str,
    tags: list[str],
    language_hint: str,
    source_confidence: str,
    candidate_state: str,
    provenance: str,
    next_local_action: str,
    generated_at: str,
) -> dict[str, Any]:
    state = candidate_state if candidate_state in ALLOWED_STATES else "needs_review"
    if not clean_string(source_url) and state == "source_candidate":
        state = "needs_review"
    return {
        "source_candidate_id": slugify(source_candidate_id) or "hub_source_candidate",
        "source_kind": source_kind,
        "source_url": clean_string(source_url),
        "title": clean_string(title) or "untitled source candidate",
        "channel_or_feed": clean_string(channel_or_feed) or "unknown",
        "published_at": clean_string(published_at),
        "description": clean_string(description),
        "tags": sorted(set(tags)),
        "language_hint": clean_string(language_hint) or "unknown",
        "source_confidence": clean_string(source_confidence) or "unverified",
        "candidate_state": state,
        "provenance": clean_string(provenance) or "fixture",
        "network_used": False,
        "media_downloaded": False,
        "rights_approved": False,
        "public_ready": False,
        "next_local_action": clean_string(next_local_action) or "operator_source_review_required",
        "generated_at": generated_at,
    }


def ensure_unique_candidate_ids(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: Counter[str] = Counter()
    normalized = []
    for record in records:
        base_id = record["source_candidate_id"]
        seen[base_id] += 1
        if seen[base_id] == 1:
            normalized.append(record)
            continue
        deduped = dict(record)
        deduped["source_candidate_id"] = f"{base_id}_{seen[base_id]}"
        normalized.append(deduped)
    return normalized


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind = Counter(record["source_kind"] for record in records)
    by_state = Counter(record["candidate_state"] for record in records)
    return {
        "record_count": len(records),
        "rss_item_count": by_kind.get("rss_item", 0),
        "manual_seed_count": by_kind.get("manual_seed", 0),
        "source_candidate_count": by_state.get("source_candidate", 0),
        "needs_review_count": by_state.get("needs_review", 0),
        "rejected_count": by_state.get("rejected", 0),
        "hold_count": by_state.get("hold", 0),
        "network_used_count": sum(1 for record in records if record["network_used"]),
        "media_downloaded_count": sum(1 for record in records if record["media_downloaded"]),
        "rights_approved_count": sum(1 for record in records if record["rights_approved"]),
        "public_ready_count": sum(1 for record in records if record["public_ready"]),
    }


def gate_readback(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "network_required": False,
        "network_used": any(record["network_used"] for record in records),
        "external_api_used": False,
        "source_urls_opened": False,
        "media_downloaded": any(record["media_downloaded"] for record in records),
        "transcript_generated": False,
        "render_generated": False,
        "thumbnail_generated": False,
        "upload_created": False,
        "oauth_or_credentials_used": False,
        "rights_approved": any(record["rights_approved"] for record in records),
        "public_ready": any(record["public_ready"] for record in records),
        "production_ready": False,
    }


def child_text(node: ET.Element, tag: str) -> str:
    child = node.find(tag)
    return clean_string(child.text if child is not None else "")


def clean_string(value: Any) -> str:
    return str(value or "").strip()


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        values = value
    else:
        values = [value]
    return [clean_string(item) for item in values if clean_string(item)]


def slugify(value: str) -> str:
    text = clean_string(value).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text
