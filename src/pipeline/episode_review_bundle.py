"""Episode review bundle surface.

This module collects existing episode and review artifacts into one local
review entry point. It does not render, fetch, upload, approve rights, or make
production acceptance claims.
"""

from __future__ import annotations

import json
import os
import hashlib
import shutil
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v1"
BUNDLE_KIND = "human_preview_session_bundle"
DEFAULT_REVIEW_DIR_NAME = "jp_pilot01r3_cut_review"
DEFAULT_OUTPUT_DIR_NAME = "human_preview_session"
DEFAULT_ACTIVE_ARTIFACT = "clip-human-preview-session-001"
ARTIFACT_ALIASES = ["clip-episode-review-surface-001"]
DECISION_ALLOWED_RESPONSES = [
    "accept_candidate",
    "adjust_boundary",
    "reject",
    "blocked_missing_artifact",
    "blocked_missing_dense_stress_proof",
]
DIRECT_ASSET_MEDIA_TYPES = {"mp4", "png", "srt", "ass"}


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
    """Write a human preview session for existing review artifacts."""
    base = base_dir or Path.cwd()
    episode_dir = _resolve_existing_or_candidate(episode_dir, base)
    review_dir = (
        _resolve_existing_or_candidate(review_dir, base)
        if review_dir
        else episode_dir / "review" / DEFAULT_REVIEW_DIR_NAME
    )
    output_dir = output_dir or review_dir / DEFAULT_OUTPUT_DIR_NAME

    rights_path = episode_dir / "rights_manifest.json"
    transcript_path = episode_dir / "transcript.json"
    edit_pack_path = episode_dir / "edit_pack.json"
    material_ledger_path = episode_dir / "material_ledger.json"
    rights = _load_json_optional(rights_path)
    transcript = _load_json_optional(transcript_path)
    edit_pack = _load_json_optional(edit_pack_path)
    episode_id = _episode_id(episode_dir, rights, transcript, edit_pack)
    target_cut_ids = target_cut_ids or _target_cut_ids(review_dir, edit_pack)

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
        target_cut_ids=target_cut_ids,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    asset_dir = output_dir / "assets"
    asset_entries = _bundle_direct_assets(optional_files, asset_dir=asset_dir, base=base, output_dir=output_dir)

    playable_videos = [item for item in optional_files if item["role"] == "playable_video" and item["exists"]]
    contact_images = [
        item
        for item in optional_files
        if item["role"] in {"contact_sheet", "representative_frame"} and item["exists"]
    ]
    missing_required = [item for item in required_files if not item["exists"]]
    missing_expected_media = [
        item
        for item in optional_files
        if item.get("expected_for_target") and not item["exists"]
    ]
    missing_media = not playable_videos and not contact_images
    review_ready = not missing_required and not missing_media
    rights_status = _rights_status(rights)
    production_candidate = _production_candidate(edit_pack)
    status = _status_readback(transcript, edit_pack)

    manifest_path = output_dir / "review_manifest.json"
    decision_request_path = output_dir / "decision_request.json"
    decision_template_path = output_dir / "decision_template.json"
    open_preview_path = output_dir / "open_preview.ps1"
    serve_preview_path = output_dir / "serve_preview.ps1"
    index_path = output_dir / "index.html"
    decision_request = _decision_request(target_cut_ids)
    decision_template = _decision_template(target_cut_ids)
    open_commands = _open_commands(output_dir=output_dir, base=base)
    generated_files = [
        _generated_file("index_html", index_path, "html", base, output_dir),
        _generated_file("review_manifest", manifest_path, "json", base, output_dir),
        _generated_file("decision_request", decision_request_path, "json", base, output_dir),
        _generated_file("decision_template", decision_template_path, "json", base, output_dir),
        _generated_file("open_preview_helper", open_preview_path, "ps1", base, output_dir),
        _generated_file("serve_preview_helper", serve_preview_path, "ps1", base, output_dir),
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": BUNDLE_KIND,
        "active_artifact": active_artifact,
        "artifact_aliases": ARTIFACT_ALIASES,
        "created_at": _now(),
        "episode_id": episode_id,
        "bundle": {
            "repo_relative_dir": _display_path(output_dir, base),
            "index_html": _display_path(index_path, base),
            "review_manifest": _display_path(manifest_path, base),
            "decision_request": _display_path(decision_request_path, base),
            "decision_template": _display_path(decision_template_path, base),
            "open_preview_helper": _display_path(open_preview_path, base),
            "serve_preview_helper": _display_path(serve_preview_path, base),
            "assets_dir": _display_path(asset_dir, base),
            "preferred_open_route": {
                "repo_relative_path": _display_path(index_path, base),
                "open_helper": open_commands["open_preview"],
                "localhost_helper": open_commands["serve_preview"],
                "os_open_requires_confirmation": True,
            },
            "path_authority": "repo_relative_paths_only; absolute local paths are not authority",
        },
        "open_commands": open_commands,
        "reviewability": {
            "review_ready": review_ready,
            "state": "diagnostic_only" if review_ready else "review_blocked_missing_artifacts",
            "missing_required_files": [item["path"] for item in missing_required],
            "missing_expected_media": [item["path"] for item in missing_expected_media],
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
        "decision_request": decision_request,
        "decision_template": {
            "path": _display_path(decision_template_path, base),
            "state": "blank_response_template",
        },
        "generated_files": generated_files,
        "assets": {
            "directory": _display_path(asset_dir, base),
            "entries": asset_entries,
        },
        "missing_artifacts": [
            *[item["path"] for item in missing_required],
            *[item["path"] for item in missing_expected_media],
        ],
        "primary_review_order": _primary_review_order(
            playable_videos=playable_videos,
            contact_images=contact_images,
            required_files=required_files,
            optional_files=optional_files,
        ),
        "required_files": required_files,
        "optional_files": optional_files,
        "screens": _screen_map(),
        "human_decision_questions": _human_decision_questions(target_cut_ids),
        "notes": [
            "Generated video review is in scope for diagnostic and representative review.",
            "Production render, rights approval, publishing, upload, and public-use acceptance remain separate gates.",
            "The bundle links existing ignored/local artifacts and does not regenerate proof.",
            "decision_template.json is intentionally blank and must not be treated as a human answer.",
        ],
    }

    _write_json(manifest, manifest_path)
    _write_json(decision_request, decision_request_path)
    _write_json(decision_template, decision_template_path)
    open_preview_path.write_text(_open_preview_script(), encoding="utf-8")
    serve_preview_path.write_text(_serve_preview_script(), encoding="utf-8")
    index_path.write_text(_index_html(manifest), encoding="utf-8")
    return {
        "manifest": manifest,
        "manifest_path": manifest_path,
        "decision_request_path": decision_request_path,
        "decision_template_path": decision_template_path,
        "open_preview_path": open_preview_path,
        "serve_preview_path": serve_preview_path,
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


def _optional_files(
    *,
    episode_dir: Path,
    review_dir: Path,
    base: Path,
    output_dir: Path,
    target_cut_ids: list[str],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    items.extend(_target_media_files(review_dir=review_dir, base=base, output_dir=output_dir, target_cut_ids=target_cut_ids))
    for path in sorted(review_dir.glob("subtitle_overlay_visual_proof_cut_*.mp4")):
        items.append(_artifact("playable_video", path, "mp4", base, output_dir))
    for path in sorted(review_dir.glob("subtitle_overlay_visual_proof_cut_*.png")):
        items.append(_artifact("representative_frame", path, "png", base, output_dir))
    for path in sorted(review_dir.glob("subtitle_overlay_visual_proof_cut_*.srt")):
        items.append(_artifact("subtitle_sidecar_srt", path, "srt", base, output_dir))
    for path in sorted(review_dir.glob("visual_proof_contact_sheet*.png")):
        items.append(_artifact("contact_sheet", path, "png", base, output_dir))
    reference_dir = review_dir / "subtitle_overlay_reference"
    for path in sorted(reference_dir.glob("*.sample_*.png")):
        items.append(_artifact("representative_frame", path, "png", base, output_dir))
    for path in sorted(reference_dir.glob("*.srt")):
        items.append(_artifact("subtitle_reference_srt", path, "srt", base, output_dir))
    for path in sorted(reference_dir.glob("*.ass")):
        items.append(_artifact("subtitle_burned_in_ass", path, "ass", base, output_dir))

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
        "sha256": _sha256(path) if exists else None,
    }


def _target_media_files(
    *,
    review_dir: Path,
    base: Path,
    output_dir: Path,
    target_cut_ids: list[str],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    reference_dir = review_dir / "subtitle_overlay_reference"
    for cut_id in target_cut_ids:
        prefix = f"subtitle_overlay_visual_proof_{cut_id}"
        expected = [
            ("playable_video", review_dir / f"{prefix}.mp4", "mp4"),
            ("representative_frame", review_dir / f"{prefix}.png", "png"),
            ("subtitle_reference_srt", reference_dir / f"{prefix}.reference.srt", "srt"),
            ("subtitle_burned_in_ass", reference_dir / f"{prefix}.burned_in.ass", "ass"),
        ]
        for role, path, media_type in expected:
            artifact = _artifact(role, path, media_type, base, output_dir)
            artifact["expected_for_target"] = True
            artifact["target_cut_id"] = cut_id
            items.append(artifact)
    return items


def _generated_file(role: str, path: Path, media_type: str, base: Path, output_dir: Path) -> dict[str, Any]:
    return {
        "role": role,
        "media_type": media_type,
        "path": _display_path(path, base),
        "href": _href(path, output_dir),
        "exists": True,
    }


def _bundle_direct_assets(
    items: list[dict[str, Any]],
    *,
    asset_dir: Path,
    base: Path,
    output_dir: Path,
) -> list[dict[str, Any]]:
    asset_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    used_names: set[str] = set()
    for item in items:
        if not item.get("exists") or item.get("media_type") not in DIRECT_ASSET_MEDIA_TYPES:
            continue
        source = _source_path_from_artifact(item, base)
        if not source.exists() or not source.is_file():
            continue
        dest = asset_dir / _unique_asset_name(item, source, used_names)
        if source.resolve() != dest.resolve():
            shutil.copy2(source, dest)
        item["asset_path"] = _display_path(dest, base)
        item["asset_href"] = _href(dest, output_dir)
        item["bundled_asset"] = True
        entries.append(
            {
                "role": item["role"],
                "media_type": item["media_type"],
                "target_cut_id": item.get("target_cut_id"),
                "source_path": item["path"],
                "asset_path": item["asset_path"],
                "href": item["asset_href"],
                "size_bytes": dest.stat().st_size,
                "sha256": _sha256(dest),
            }
        )
    return entries


def _source_path_from_artifact(item: dict[str, Any], base: Path) -> Path:
    path = Path(str(item.get("path", "")))
    return path if path.is_absolute() else base / path


def _unique_asset_name(item: dict[str, Any], source: Path, used_names: set[str]) -> str:
    raw_name = f"{item.get('role', 'asset')}__{source.name}"
    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in raw_name)
    candidate = safe_name
    stem = Path(safe_name).stem
    suffix = Path(safe_name).suffix
    counter = 2
    while candidate in used_names:
        candidate = f"{stem}_{counter}{suffix}"
        counter += 1
    used_names.add(candidate)
    return candidate


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


def _human_decision_questions(target_cut_ids: list[str]) -> list[str]:
    return [
        _decision_question(target_cut_ids),
    ]


def _decision_request(target_cut_ids: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "question": _decision_question(target_cut_ids),
        "allowed_responses": DECISION_ALLOWED_RESPONSES,
        "response_meanings": {
            "accept_candidate": "Proceed with this diagnostic representative subtitle evidence as a candidate for the next non-production step.",
            "adjust_boundary": "The review needs a cut boundary or scoped artifact adjustment before proceeding.",
            "reject": "Do not proceed with this diagnostic representative evidence.",
            "blocked_missing_artifact": "A required local artifact is missing, so the human cannot answer yet.",
            "blocked_missing_dense_stress_proof": "Do not lift representative subtitle design limitations until the dense/stress proof path exists.",
        },
        "boundary_reminder": _boundary_reminder(),
    }


def _decision_template(target_cut_ids: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "target_cuts": target_cut_ids,
        "selected_response": None,
        "reviewed_by": "",
        "reviewed_at": "",
        "notes": "",
        "boundary_flags_confirmed": {
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "creative_acceptance": False,
            "rights_status": "pending",
            "production_candidate": False,
            "production_usage_allowed": False,
            "publishing_acceptance": False,
            "public_use_permission": False,
        },
        "do_not_fill_without_human_answer": True,
    }


def _decision_question(target_cut_ids: list[str]) -> str:
    cuts = " / ".join(target_cut_ids) if target_cut_ids else "the current target cuts"
    return (
        f"For {cuts}, should the current diagnostic representative subtitle overlay evidence "
        "proceed to the next diagnostic step? This answer does not approve production subtitle "
        "design, production render, creative quality, rights, publishing, public use, or upload."
    )


def _boundary_reminder() -> dict[str, Any]:
    return {
        "production_subtitle_design_acceptance": False,
        "production_render_acceptance": False,
        "creative_acceptance": False,
        "rights_status": "pending",
        "production_candidate": False,
        "production_usage_allowed": False,
        "publishing_acceptance": False,
        "public_use_permission": False,
    }


def _open_commands(*, output_dir: Path, base: Path) -> dict[str, str]:
    open_script = _display_path(output_dir / "open_preview.ps1", base).replace("/", "\\")
    serve_script = _display_path(output_dir / "serve_preview.ps1", base).replace("/", "\\")
    return {
        "open_preview": f"powershell -ExecutionPolicy Bypass -File {open_script}",
        "serve_preview": f"powershell -ExecutionPolicy Bypass -File {serve_script} -Port 8000",
    }


def _open_preview_script() -> str:
    return """$ErrorActionPreference = 'Stop'
$previewRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$index = Join-Path $previewRoot 'index.html'
if (-not (Test-Path -LiteralPath $index)) {
  throw "index.html not found next to open_preview.ps1"
}
Invoke-Item -LiteralPath $index
"""


def _serve_preview_script() -> str:
    return """param(
  [int]$Port = 8000
)
$ErrorActionPreference = 'Stop'
$previewRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Serving human preview session at http://localhost:$Port/"
python -m http.server $Port --directory $previewRoot
"""


def _index_html(manifest: dict[str, Any]) -> str:
    boundary = manifest["boundary_flags"]
    reviewability = manifest["reviewability"]
    primary = manifest["primary_review_order"]
    required = manifest["required_files"]
    optional = manifest["optional_files"]
    generated = manifest["generated_files"]
    screens = manifest["screens"]
    decision = manifest["decision_request"]
    media_html = _media_html(primary)
    missing = manifest["missing_artifacts"]
    missing_html = (
        "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in missing) + "</ul>"
        if missing
        else "<p>No required files missing.</p>"
    )
    required_rows = _artifact_rows(required)
    optional_rows = _artifact_rows(optional)
    generated_rows = _artifact_rows(generated)
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
    boundary_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(key))}</td>"
        f"<td>{escape(str(value).lower() if isinstance(value, bool) else str(value))}</td>"
        "</tr>"
        for key, value in boundary.items()
    )
    response_options = "".join(
        f"<li><code>{escape(str(option))}</code></li>" for option in decision.get("allowed_responses", [])
    )
    target_cuts = ", ".join(str(item) for item in manifest.get("target_cuts", []))
    open_commands = manifest.get("open_commands", {})
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Human Preview Session - {escape(str(manifest.get("episode_id", "")))}</title>
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
  <h1>Human Preview Session</h1>
  <p>This page is the single local entry point for diagnostic and representative review. It does not approve production render, production subtitle design, creative quality, rights, publishing, upload, or public use.</p>

  <h2>Active Artifact</h2>
  <p><strong>{escape(str(manifest.get("active_artifact")))}</strong></p>
  <p><strong>target cuts:</strong> {escape(target_cuts)}</p>

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

  <h2>Decision Request</h2>
  <p>{escape(str(decision.get("question")))}</p>
  <ul>{response_options}</ul>
  <p>Use <code>decision_template.json</code> only after a human gives one of these answers.</p>

  <h2>Boundary Flags</h2>
  <table>
    <thead><tr><th>flag</th><th>value</th></tr></thead>
    <tbody>{boundary_rows}</tbody>
  </table>

  <h2>Missing Artifacts</h2>
  <div class="blocked">{missing_html}</div>

  <h2>Open Commands</h2>
  <p><code>{escape(str(open_commands.get("open_preview", "")))}</code></p>
  <p><code>{escape(str(open_commands.get("serve_preview", "")))}</code></p>

  <h2>Screen Map</h2>
  <table>
    <thead><tr><th>screen</th><th>creator sees</th><th>decision</th><th>artifact backs it</th><th>not accepted here</th></tr></thead>
    <tbody>{screen_rows}</tbody>
  </table>

  <h2>Generated Files</h2>
  <table>
    <thead><tr><th>role</th><th>exists</th><th>path</th><th>open</th></tr></thead>
    <tbody>{generated_rows}</tbody>
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
    <li>{escape(str(decision.get("question")))}</li>
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
        href = item.get("asset_href") or href
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
        href = item.get("asset_href") or item.get("href")
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
