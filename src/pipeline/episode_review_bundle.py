"""Episode review bundle surface.

This module collects existing episode and review artifacts into one local
review entry point. It does not render, fetch, upload, approve rights, or make
production acceptance claims.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v1"
BUNDLE_KIND = "episode_review_bundle"
DEFAULT_REVIEW_DIR_NAME = "jp_pilot01r3_cut_review"
DEFAULT_ACTIVE_ARTIFACT = "clip-episode-review-surface-001"


class EpisodeReviewBundleError(Exception):
    """Raised when the review bundle cannot be built safely."""


def build_episode_review_bundle(
    *,
    episode_dir: Path,
    review_dir: Path | None = None,
    output_dir: Path | None = None,
    active_artifact: str = DEFAULT_ACTIVE_ARTIFACT,
    target_cut_ids: list[str] | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Write review_manifest.json and index.html for existing review artifacts."""
    base = base_dir or Path.cwd()
    episode_dir = _resolve_existing_or_candidate(episode_dir, base)
    review_dir = (
        _resolve_existing_or_candidate(review_dir, base)
        if review_dir
        else episode_dir / "review" / DEFAULT_REVIEW_DIR_NAME
    )
    output_dir = output_dir or review_dir / "review_bundle"

    rights_path = episode_dir / "rights_manifest.json"
    transcript_path = episode_dir / "transcript.json"
    edit_pack_path = episode_dir / "edit_pack.json"
    material_ledger_path = episode_dir / "material_ledger.json"
    rights = _load_json_optional(rights_path)
    transcript = _load_json_optional(transcript_path)
    edit_pack = _load_json_optional(edit_pack_path)
    episode_id = _episode_id(episode_dir, rights, transcript, edit_pack)

    required_files = _required_files(
        episode_dir=episode_dir,
        review_dir=review_dir,
        base=base,
        output_dir=output_dir,
    )
    optional_files = _optional_files(
        episode_dir=episode_dir,
        review_dir=review_dir,
        base=base,
        output_dir=output_dir,
    )
    playable_videos = [item for item in optional_files if item["role"] == "playable_video" and item["exists"]]
    contact_images = [
        item
        for item in optional_files
        if item["role"] in {"contact_sheet", "representative_frame"} and item["exists"]
    ]
    missing_required = [item for item in required_files if not item["exists"]]
    missing_media = not playable_videos and not contact_images
    review_ready = not missing_required and not missing_media
    rights_status = _rights_status(rights)
    production_candidate = _production_candidate(edit_pack)
    status = _status_readback(transcript, edit_pack)
    target_cut_ids = target_cut_ids or _target_cut_ids(review_dir, edit_pack)

    manifest_path = output_dir / "review_manifest.json"
    index_path = output_dir / "index.html"
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": BUNDLE_KIND,
        "active_artifact": active_artifact,
        "created_at": _now(),
        "episode_id": episode_id,
        "bundle": {
            "repo_relative_dir": _display_path(output_dir, base),
            "index_html": _display_path(index_path, base),
            "review_manifest": _display_path(manifest_path, base),
            "preferred_open_route": {
                "repo_relative_path": _display_path(index_path, base),
                "localhost_helper": f"python -m http.server --directory {_display_path(output_dir, base)} 8000",
                "os_open_requires_confirmation": True,
            },
            "path_authority": "repo_relative_paths_only; absolute local paths are not authority",
        },
        "reviewability": {
            "review_ready": review_ready,
            "state": "diagnostic_only" if review_ready else "review_blocked_missing_artifacts",
            "missing_required_files": [item["path"] for item in missing_required],
            "missing_artifact_behavior": (
                "Show the missing panel, keep the bundle diagnostic-only, and do not ask the creator "
                "to hunt scattered local HTML paths."
            ),
        },
        "boundary_flags": {
            "diagnostic_only": True,
            "production_candidate": bool(production_candidate),
            "production_render_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "creative_acceptance": False,
            "rights_status": rights_status,
            "production_usage_allowed": False,
            "publishing_acceptance": False,
            "public_use_permission": False,
        },
        "status_readback": status,
        "target_cuts": target_cut_ids,
        "primary_review_order": _primary_review_order(
            playable_videos=playable_videos,
            contact_images=contact_images,
            required_files=required_files,
            optional_files=optional_files,
        ),
        "required_files": required_files,
        "optional_files": optional_files,
        "screens": _screen_map(),
        "human_decision_questions": _human_decision_questions(),
        "notes": [
            "Generated video review is in scope for diagnostic and representative review.",
            "Production render, rights approval, publishing, upload, and public-use acceptance remain separate gates.",
            "The bundle links existing ignored/local artifacts and does not regenerate proof.",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(manifest, manifest_path)
    index_path.write_text(_index_html(manifest), encoding="utf-8")
    return {
        "manifest": manifest,
        "manifest_path": manifest_path,
        "index_path": index_path,
    }


def _required_files(*, episode_dir: Path, review_dir: Path, base: Path, output_dir: Path) -> list[dict[str, Any]]:
    return [
        _artifact("rights_readback", episode_dir / "rights_manifest.json", "json", base, output_dir),
        _artifact("source_materials", episode_dir / "material_ledger.json", "json", base, output_dir),
        _artifact("transcript_source", episode_dir / "transcript.json", "json", base, output_dir),
        _artifact("cut_and_subtitle_source", episode_dir / "edit_pack.json", "json", base, output_dir),
        _artifact("cut_review", review_dir / "cut_review_report.html", "html", base, output_dir),
        _artifact("evidence_summary", review_dir / "evidence_summary.html", "html", base, output_dir),
        _artifact(
            "subtitle_overlay_report_json",
            review_dir / "subtitle_overlay_visual_proof_report.json",
            "json",
            base,
            output_dir,
        ),
        _artifact(
            "subtitle_overlay_report_html",
            review_dir / "subtitle_overlay_visual_proof_report.html",
            "html",
            base,
            output_dir,
        ),
    ]


def _optional_files(*, episode_dir: Path, review_dir: Path, base: Path, output_dir: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in sorted(review_dir.glob("subtitle_overlay_visual_proof_cut_*.mp4")):
        items.append(_artifact("playable_video", path, "mp4", base, output_dir))
    for path in sorted(review_dir.glob("subtitle_overlay_visual_proof_cut_*.png")):
        items.append(_artifact("representative_frame", path, "png", base, output_dir))
    for path in sorted(review_dir.glob("visual_proof_contact_sheet*.png")):
        items.append(_artifact("contact_sheet", path, "png", base, output_dir))
    reference_dir = review_dir / "subtitle_overlay_reference"
    for path in sorted(reference_dir.glob("*.sample_*.png")):
        items.append(_artifact("representative_frame", path, "png", base, output_dir))

    known = [
        ("representative_visual_proof", review_dir / "representative_visual_proof_report.html", "html"),
        ("representative_visual_proof_json", review_dir / "representative_visual_proof_report.json", "json"),
        ("cut_decision", review_dir / "cut_decision_report.html", "html"),
        ("cut_decision_json", review_dir / "cut_decision_packet.json", "json"),
        ("operator_proxy_handoff", review_dir / "cut_002_cut_003_operator_proxy_decision_handoff.html", "html"),
        ("operator_proxy_handoff_json", review_dir / "cut_002_cut_003_operator_proxy_decision_handoff.json", "json"),
        ("text_proxy_review", review_dir / "cut_002_cut_003_text_proxy_review.html", "html"),
        ("text_proxy_review_json", review_dir / "cut_002_cut_003_text_proxy_review.json", "json"),
        ("chapter_revision_board", review_dir / "chapter_revision_board.html", "html"),
        ("chapter_revision_board_json", review_dir / "chapter_revision_board.json", "json"),
        ("non_repo_handoff", review_dir / "non_repo_artifact_handoff.html", "html"),
        ("non_repo_handoff_json", review_dir / "non_repo_artifact_handoff.json", "json"),
        (
            "production_subtitle_render_acceptance_report",
            review_dir / "production_subtitle_render_acceptance_report.html",
            "html",
        ),
        (
            "production_subtitle_render_acceptance_json",
            review_dir / "production_subtitle_render_acceptance_report.json",
            "json",
        ),
    ]
    for role, path, media_type in known:
        items.append(_artifact(role, path, media_type, base, output_dir))

    for path in sorted(review_dir.glob("*.csv")):
        items.append(_artifact("operator_csv", path, "csv", base, output_dir))
    for path in sorted((episode_dir / "exports").glob("**/nle_cut_list.csv")):
        items.append(_artifact("nle_csv", path, "csv", base, output_dir))
    for path in sorted((episode_dir / "exports").glob("**/nle_export_report.html")):
        items.append(_artifact("nle_report", path, "html", base, output_dir))
    for path in sorted((episode_dir / "renders").glob("**/rendered_video.mp4")):
        items.append(_artifact("playable_video", path, "mp4", base, output_dir))
    for path in sorted((episode_dir / "renders").glob("**/render_report.html")):
        items.append(_artifact("render_report", path, "html", base, output_dir))
    for path in sorted((episode_dir / "renders").glob("**/render_manifest.json")):
        items.append(_artifact("render_manifest", path, "json", base, output_dir))
    return _dedupe_artifacts(items)


def _artifact(role: str, path: Path, media_type: str, base: Path, output_dir: Path) -> dict[str, Any]:
    exists = path.exists() and path.is_file()
    return {
        "role": role,
        "media_type": media_type,
        "path": _display_path(path, base),
        "href": _href(path, output_dir) if exists else None,
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else None,
    }


def _primary_review_order(
    *,
    playable_videos: list[dict[str, Any]],
    contact_images: list[dict[str, Any]],
    required_files: list[dict[str, Any]],
    optional_files: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    report_roles = [
        "subtitle_overlay_report_html",
        "representative_visual_proof",
        "cut_review",
        "evidence_summary",
        "operator_proxy_handoff",
        "nle_csv",
    ]
    reports: list[dict[str, Any]] = []
    for role in report_roles:
        reports.extend(
            item
            for item in required_files + optional_files
            if item["role"] == role and item["exists"]
        )
    ordered = [
        *playable_videos,
        *contact_images,
        *reports,
    ]
    return _dedupe_artifacts(ordered)


def _screen_map() -> list[dict[str, Any]]:
    return [
        {
            "screen_id": "episode_dashboard",
            "creator_sees": "reviewability, boundary badges, primary playable video or contact sheet, and missing artifacts first",
            "decision": "whether the episode has enough local diagnostic evidence to start review",
            "backing_artifacts": ["review_manifest.json", "status readback", "required_files"],
            "not_accepted": ["production readiness", "rights approval", "publishing"],
        },
        {
            "screen_id": "source_rights_readback",
            "creator_sees": "source identity, material ledger, rights status, and production/public-use block",
            "decision": "whether source and rights readback are understood before review",
            "backing_artifacts": ["rights_manifest.json", "material_ledger.json"],
            "not_accepted": ["rights clearance", "public use"],
        },
        {
            "screen_id": "transcript_subtitle_source",
            "creator_sees": "transcript source, imported subtitle track status, subtitle counts, and review status",
            "decision": "whether text evidence is sufficient for diagnostic review",
            "backing_artifacts": ["transcript.json", "edit_pack.json"],
            "not_accepted": ["official subtitle design", "transcript mutation"],
        },
        {
            "screen_id": "cut_review",
            "creator_sees": "selected cuts, context status, retained risk, and cut review report",
            "decision": "keep, adjust, reject, or block a cut for the next diagnostic step",
            "backing_artifacts": ["cut_review_report.html", "cut_decision_packet.json"],
            "not_accepted": ["final production edit", "creative acceptance"],
        },
        {
            "screen_id": "video_review_player",
            "creator_sees": "playable diagnostic MP4 first when available, otherwise contact sheet or representative frames",
            "decision": "whether generated video/overlay evidence is inspectable for diagnostic or representative review",
            "backing_artifacts": ["subtitle_overlay_visual_proof_cut_*.mp4", "rendered_video.mp4", "visual proof PNGs"],
            "not_accepted": ["production render acceptance", "upload readiness"],
        },
        {
            "screen_id": "subtitle_design_review",
            "creator_sees": "overlay report, representative frames, wrapping/readability readback, and renderer_gap",
            "decision": "accept, adjust, reject, or block representative subtitle design evidence",
            "backing_artifacts": ["subtitle_overlay_visual_proof_report.*", "representative_visual_proof_report.*"],
            "not_accepted": ["production subtitle design acceptance"],
        },
        {
            "screen_id": "export_handoff",
            "creator_sees": "NLE CSV, handoff reports, render identity, and recovery notes",
            "decision": "whether external editor handoff material is present enough for downstream work",
            "backing_artifacts": ["nle_cut_list.csv", "non_repo_artifact_handoff.*", "render_manifest.json"],
            "not_accepted": ["FCPXML/Resolve XML primary target", "public publishing"],
        },
        {
            "screen_id": "acceptance_dashboard",
            "creator_sees": "all false/pending production, rights, publishing, and public-use flags",
            "decision": "which separate limitation-lift slice is next",
            "backing_artifacts": ["boundary_flags", "review_manifest.json"],
            "not_accepted": ["implicit production/public acceptance"],
        },
    ]


def _human_decision_questions() -> list[str]:
    return [
        "Can the creator review the generated diagnostic video or representative frames from this single bundle entry?",
        "For the current target cuts, should the diagnostic subtitle overlay evidence proceed, adjust, reject, or remain blocked?",
        "Which separate limitation-lift path is next: subtitle design, final render-path output, editorial sequence quality, or rights clearance?",
    ]


def _index_html(manifest: dict[str, Any]) -> str:
    boundary = manifest["boundary_flags"]
    reviewability = manifest["reviewability"]
    primary = manifest["primary_review_order"]
    required = manifest["required_files"]
    optional = manifest["optional_files"]
    screens = manifest["screens"]
    media_html = _media_html(primary)
    missing = reviewability["missing_required_files"]
    missing_html = (
        "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in missing) + "</ul>"
        if missing
        else "<p>No required files missing.</p>"
    )
    required_rows = _artifact_rows(required)
    optional_rows = _artifact_rows(optional)
    screen_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(screen['screen_id']))}</td>"
        f"<td>{escape(str(screen['creator_sees']))}</td>"
        f"<td>{escape(str(screen['decision']))}</td>"
        f"<td>{escape(', '.join(screen['backing_artifacts']))}</td>"
        f"<td>{escape(', '.join(screen['not_accepted']))}</td>"
        "</tr>"
        for screen in screens
    )
    questions_html = "".join(
        f"<li>{escape(question)}</li>" for question in manifest.get("human_decision_questions", [])
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Episode Review Bundle - {escape(str(manifest.get("episode_id", "")))}</title>
  <style>
    body {{ font-family: sans-serif; margin: 24px; line-height: 1.45; color: #20242a; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #ccd2d8; padding: 6px; vertical-align: top; }}
    th {{ background: #eef4f1; }}
    .badge {{ display: inline-block; margin: 0 6px 6px 0; padding: 4px 8px; border: 1px solid #ccd2d8; border-radius: 4px; }}
    .blocked {{ color: #9a2f2f; font-weight: 700; }}
    video, img {{ display: block; max-width: 100%; margin: 8px 0 16px; border: 1px solid #ccd2d8; }}
    code {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Episode Review Bundle</h1>
  <p>This page is the single local entry point for diagnostic and representative review. It does not approve production render, rights, publishing, upload, or public use.</p>

  <h2>Reviewability</h2>
  <p><strong>state:</strong> {escape(str(reviewability.get("state")))} / <strong>review_ready:</strong> {escape(str(reviewability.get("review_ready")).lower())}</p>
  <div>
    <span class="badge">diagnostic_only={escape(str(boundary.get("diagnostic_only")).lower())}</span>
    <span class="badge">production_render_acceptance={escape(str(boundary.get("production_render_acceptance")).lower())}</span>
    <span class="badge">production_subtitle_design_acceptance={escape(str(boundary.get("production_subtitle_design_acceptance")).lower())}</span>
    <span class="badge">rights_status={escape(str(boundary.get("rights_status")))}</span>
    <span class="badge">publishing_acceptance={escape(str(boundary.get("publishing_acceptance")).lower())}</span>
  </div>

  <h2>Start Here</h2>
  {media_html}

  <h2>Missing Artifacts</h2>
  <div class="blocked">{missing_html}</div>

  <h2>Screen Map</h2>
  <table>
    <thead><tr><th>screen</th><th>creator sees</th><th>decision</th><th>artifact backs it</th><th>not accepted here</th></tr></thead>
    <tbody>{screen_rows}</tbody>
  </table>

  <h2>Required Files</h2>
  <table>
    <thead><tr><th>role</th><th>exists</th><th>path</th><th>open</th></tr></thead>
    <tbody>{required_rows}</tbody>
  </table>

  <h2>Optional Files</h2>
  <table>
    <thead><tr><th>role</th><th>exists</th><th>path</th><th>open</th></tr></thead>
    <tbody>{optional_rows}</tbody>
  </table>

  <h2>Human Decision Questions</h2>
  <ol>
    {questions_html}
  </ol>
</body>
</html>
"""


def _media_html(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<p>No playable video or contact sheet is available. Use the missing-artifact panel before asking for HTML inspection.</p>"
    no_direct_media = not any(item.get("media_type") in {"mp4", "png"} for item in items)
    blocks: list[str] = []
    if no_direct_media:
        blocks.append(
            "<p>No playable video or contact sheet is available. Use the missing-artifact panel before asking for HTML inspection.</p>"
        )
    for item in items:
        href = item.get("href")
        if not href:
            continue
        label = escape(str(item.get("path", "")))
        if item.get("media_type") == "mp4":
            blocks.append(f'<h3>{label}</h3><video controls src="{escape(href)}"></video>')
        elif item.get("media_type") == "png":
            blocks.append(f'<h3>{label}</h3><img src="{escape(href)}" alt="{label}">')
        else:
            blocks.append(f'<p><a href="{escape(href)}">{label}</a></p>')
    return "\n".join(blocks) if blocks else "<p>No directly openable media found.</p>"


def _artifact_rows(items: list[dict[str, Any]]) -> str:
    rows = []
    for item in items:
        href = item.get("href")
        link = f'<a href="{escape(href)}">open</a>' if href else ""
        rows.append(
            "<tr>"
            f"<td>{escape(str(item.get('role')))}</td>"
            f"<td>{escape(str(item.get('exists')).lower())}</td>"
            f"<td>{escape(str(item.get('path')))}</td>"
            f"<td>{link}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _target_cut_ids(review_dir: Path, edit_pack: dict[str, Any]) -> list[str]:
    overlay = _load_json_optional(review_dir / "subtitle_overlay_visual_proof_report.json")
    target_cuts = overlay.get("target_cuts") if isinstance(overlay.get("target_cuts"), list) else []
    if target_cuts:
        return [str(item) for item in target_cuts]
    selected = edit_pack.get("selected_cut_ids") if isinstance(edit_pack.get("selected_cut_ids"), list) else []
    return [str(item) for item in selected]


def _status_readback(transcript: dict[str, Any], edit_pack: dict[str, Any]) -> dict[str, Any]:
    segments = transcript.get("segments") if isinstance(transcript.get("segments"), list) else []
    subtitles = edit_pack.get("subtitles") if isinstance(edit_pack.get("subtitles"), list) else []
    selected = edit_pack.get("selected_cut_ids") if isinstance(edit_pack.get("selected_cut_ids"), list) else []
    review = transcript.get("review") if isinstance(transcript.get("review"), dict) else {}
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    context_counts = {"passed": 0, "needs_review": 0, "failed": 0, "not_checked": 0}
    candidates = edit_pack.get("cut_candidates") if isinstance(edit_pack.get("cut_candidates"), list) else []
    for cut in candidates:
        if not isinstance(cut, dict):
            continue
        status = (cut.get("context_check") or {}).get("status") if isinstance(cut.get("context_check"), dict) else None
        if status in context_counts:
            context_counts[status] += 1
        else:
            context_counts["not_checked"] += 1
    return {
        "transcript_segments": len(segments),
        "transcript_engine": stt.get("engine"),
        "transcript_provider": stt.get("provider"),
        "transcript_review_status": review.get("status"),
        "selected_cuts_count": len(selected),
        "subtitle_count": len(subtitles),
        "context_counts": context_counts,
    }


def _episode_id(episode_dir: Path, rights: dict[str, Any], transcript: dict[str, Any], edit_pack: dict[str, Any]) -> str:
    return (
        _string_or_none(rights.get("episode_id"))
        or _string_or_none(transcript.get("episode_id"))
        or _string_or_none(edit_pack.get("episode_id"))
        or episode_dir.name
    )


def _rights_status(rights: dict[str, Any]) -> str:
    compliance = rights.get("compliance_check") if isinstance(rights.get("compliance_check"), dict) else {}
    return _string_or_none(compliance.get("status")) or "missing"


def _production_candidate(edit_pack: dict[str, Any]) -> bool:
    value = edit_pack.get("production_candidate")
    return bool(value) if value is not None else False


def _load_json_optional(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
        f.write("\n")


def _resolve_existing_or_candidate(path: Path, base: Path) -> Path:
    if path.is_absolute():
        return path
    candidate = base / path
    return candidate if candidate.exists() else path


def _display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def _href(path: Path, output_dir: Path) -> str:
    try:
        return os.path.relpath(path.resolve(), start=output_dir.resolve()).replace("\\", "/")
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def _string_or_none(value: Any) -> str | None:
    return str(value) if isinstance(value, str) and value else None


def _dedupe_artifacts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = (str(item.get("role")), str(item.get("path")))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
