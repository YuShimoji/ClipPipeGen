"""Non-repo artifact handoff manifests.

This module records the identity and recovery path for local artifacts that
must not be committed, such as diagnostic render videos or source media.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

SCHEMA_VERSION = "v1"
ARTIFACT_KIND = "non_repo_artifact_handoff"
DEFAULT_HANDOFF_KIND = "diagnostic_render_video"
DEFAULT_GIT_POLICY = "excluded_from_git"
YOUTUBE_ID_PATTERN = re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])")


class NonRepoArtifactHandoffError(Exception):
    """Raised when a handoff manifest cannot be built safely."""


def build_non_repo_artifact_handoff(
    *,
    episode_dir: Path,
    artifact_path: Path | None = None,
    output_dir: Path,
    artifact_id: str | None = None,
    artifact_kind: str = DEFAULT_HANDOFF_KIND,
    git_policy: str = DEFAULT_GIT_POLICY,
    generated_by_command: str | None = None,
    render_manifest_path: Path | None = None,
    render_receipt_path: Path | None = None,
    render_report_path: Path | None = None,
    transcript_path: Path | None = None,
    edit_pack_path: Path | None = None,
    rights_manifest_path: Path | None = None,
    material_ledger_path: Path | None = None,
    nle_manifest_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Write a JSON/HTML handoff manifest for a local non-repo artifact."""
    base = base_dir or Path.cwd()
    render_manifest = _load_json_optional(render_manifest_path)
    render_receipt = _load_json_optional(render_receipt_path)
    transcript_path = transcript_path or episode_dir / "transcript.json"
    edit_pack_path = edit_pack_path or episode_dir / "edit_pack.json"
    rights_manifest_path = rights_manifest_path or episode_dir / "rights_manifest.json"
    material_ledger_path = material_ledger_path or episode_dir / "material_ledger.json"
    transcript = _load_json_optional(transcript_path)
    rights = _load_json_optional(rights_manifest_path)
    material_ledger = _load_json_optional(material_ledger_path)

    if artifact_path is None:
        artifact_path = _artifact_path_from_render_manifest(render_manifest, render_manifest_path)
    if artifact_path is None:
        raise NonRepoArtifactHandoffError(
            "--artifact-path is required unless --render-manifest points to a manifest with outputs.rendered_video "
            "or a sibling rendered_video.mp4 recovery path"
        )
    resolved_artifact = _resolve_path(artifact_path, base=base, anchor=episode_dir)
    exists = resolved_artifact.exists() and resolved_artifact.is_file()
    size_bytes = resolved_artifact.stat().st_size if exists else None
    sha256 = _sha256(resolved_artifact) if exists else None
    artifact_id = artifact_id or _infer_artifact_id(
        artifact_path=resolved_artifact,
        artifact_kind=artifact_kind,
        render_manifest=render_manifest,
    )
    generated_by_command = generated_by_command or _infer_generation_command(
        episode_dir=episode_dir,
        render_manifest=render_manifest,
    )
    source_identity = build_source_identity(
        episode_dir=episode_dir,
        transcript=transcript,
        rights=rights,
        render_manifest=render_manifest,
        material_ledger=material_ledger,
        base_dir=base,
    )
    dependency_artifacts = _dependency_artifacts(
        transcript_path=transcript_path,
        edit_pack_path=edit_pack_path,
        rights_manifest_path=rights_manifest_path,
        material_ledger_path=material_ledger_path,
        render_manifest_path=render_manifest_path,
        render_receipt_path=render_receipt_path,
        render_report_path=render_report_path,
        nle_manifest_path=nle_manifest_path,
        source_identity=source_identity,
        base_dir=base,
    )
    boundary = _boundary(
        artifact_kind=artifact_kind,
        rights=rights,
        render_manifest=render_manifest,
    )
    handoff_status = _handoff_status(
        artifact_kind=artifact_kind,
        generated_by_command=generated_by_command,
        dependency_artifacts=dependency_artifacts,
    )
    missing_behavior = _missing_behavior(
        artifact_kind=artifact_kind,
        local_path=_display_path(resolved_artifact, base),
        generated_by_command=generated_by_command,
        dependency_artifacts=dependency_artifacts,
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "created_at": _now(),
        "episode_id": _episode_id(episode_dir, render_manifest, transcript, rights),
        "artifact_id": artifact_id,
        "artifact": {
            "artifact_kind": artifact_kind,
            "git_policy": git_policy,
            "local_path": _absolute_display_path(resolved_artifact),
            "repo_relative_path": _display_path(resolved_artifact, base),
            "exists": exists,
            "size_bytes": size_bytes,
            "sha256": sha256,
            "content_hash": sha256,
            "generated_by_command": generated_by_command,
            "render_readback": _render_readback(render_manifest),
        },
        "source_identity": source_identity,
        "dependency_artifacts": dependency_artifacts,
        "boundary": boundary,
        "handoff_status": handoff_status,
        "missing_behavior": missing_behavior,
        "notes": [
            "The binary artifact is intentionally excluded from Git.",
            "This manifest records identity, hashes, source identity, recovery commands, and acceptance boundaries only.",
            "Diagnostic render video is local review evidence, not production, creative, or publish acceptance.",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "non_repo_artifact_handoff.json"
    report_path = output_dir / "non_repo_artifact_handoff.html"
    _write_json(payload, manifest_path)
    report_path.write_text(_handoff_html(payload), encoding="utf-8")
    return {
        "manifest": payload,
        "manifest_path": manifest_path,
        "report_path": report_path,
    }


def build_source_identity(
    *,
    episode_dir: Path,
    transcript: dict[str, Any],
    rights: dict[str, Any],
    render_manifest: dict[str, Any],
    material_ledger: dict[str, Any] | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Build human-review source identity from local manifests only."""
    base = base_dir or Path.cwd()
    source_video = rights.get("source_video") if isinstance(rights.get("source_video"), dict) else {}
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    render_source_refs = (
        render_manifest.get("source_refs") if isinstance(render_manifest.get("source_refs"), dict) else {}
    )
    render_transcript = (
        render_source_refs.get("transcript") if isinstance(render_source_refs.get("transcript"), dict) else {}
    )
    render_source_video = (
        render_source_refs.get("source_video") if isinstance(render_source_refs.get("source_video"), dict) else {}
    )
    render_source_audio = (
        render_source_refs.get("source_audio") if isinstance(render_source_refs.get("source_audio"), dict) else {}
    )
    material_ledger = material_ledger or {}
    subtitle_track = (
        _string_or_none(stt.get("model"))
        or _string_or_none((stt.get("params") or {}).get("subtitle_track_path") if isinstance(stt.get("params"), dict) else None)
        or _string_or_none(render_transcript.get("model"))
        or _display_path(_first_existing(episode_dir / "source_subs", "*.json3"), base)
    )
    source_url = _string_or_none(source_video.get("url")) or _string_or_none(render_source_video.get("source_url"))
    youtube_id = (
        _youtube_id_from_url(source_url)
        or _youtube_id_from_path(subtitle_track)
        or _youtube_id_from_url(_string_or_none(render_source_video.get("source_url")))
        or "unknown"
    )
    transcript_engine = _string_or_none(stt.get("engine")) or _string_or_none(render_transcript.get("engine"))
    transcript_provider = _string_or_none(stt.get("provider")) or _string_or_none(render_transcript.get("provider"))
    source_video_material_id = (
        _string_or_none(render_source_video.get("material_id"))
        or _first_material_id(material_ledger, "source_video")
        or "unknown"
    )
    source_audio_material_id = (
        _string_or_none(render_source_audio.get("material_id"))
        or _first_material_id(material_ledger, "source_audio")
        or "unknown"
    )
    title = _string_or_none(source_video.get("title")) or "unknown"
    channel = _string_or_none(source_video.get("channel")) or "unknown"
    return {
        "source_video_identity": title,
        "source_video_title": title,
        "source_video_channel": channel,
        "youtube_id": youtube_id,
        "source_url": source_url or "unknown",
        "subtitle_track": subtitle_track or "unknown",
        "transcript_source": _transcript_source_label(transcript_engine, transcript_provider),
        "transcript_engine": transcript_engine or "unknown",
        "transcript_provider": transcript_provider or "unknown",
        "source_video_material_id": source_video_material_id,
        "source_audio_material_id": source_audio_material_id,
    }


def extract_youtube_id_from_subtitle_track(path: str | Path | None) -> str:
    """Return a YouTube id from a subtitle track path, or ``unknown``."""
    return _youtube_id_from_path(str(path) if path is not None else None) or "unknown"


def _artifact_path_from_render_manifest(
    render_manifest: dict[str, Any],
    render_manifest_path: Path | None,
) -> Path | None:
    outputs = render_manifest.get("outputs") if isinstance(render_manifest.get("outputs"), dict) else {}
    if outputs.get("rendered_video"):
        return Path(str(outputs["rendered_video"]))
    if render_manifest_path:
        return render_manifest_path.parent / "rendered_video.mp4"
    return None


def _infer_artifact_id(
    *,
    artifact_path: Path,
    artifact_kind: str,
    render_manifest: dict[str, Any],
) -> str:
    output_id = _string_or_none(render_manifest.get("output_id"))
    if output_id:
        return output_id
    return f"{artifact_kind}:{artifact_path.stem}"


def _infer_generation_command(
    *,
    episode_dir: Path,
    render_manifest: dict[str, Any],
) -> str | None:
    if not render_manifest:
        return None
    source_refs = render_manifest.get("source_refs") if isinstance(render_manifest.get("source_refs"), dict) else {}
    source_video = source_refs.get("source_video") if isinstance(source_refs.get("source_video"), dict) else {}
    source_audio = source_refs.get("source_audio") if isinstance(source_refs.get("source_audio"), dict) else {}
    edit_pack = source_refs.get("edit_pack") if isinstance(source_refs.get("edit_pack"), dict) else {}
    output_id = _string_or_none(render_manifest.get("output_id"))
    episode_id = _string_or_none(render_manifest.get("episode_id")) or episode_dir.name
    duration = ((render_manifest.get("timeline_mapping") or {}).get("duration_target_seconds")
                if isinstance(render_manifest.get("timeline_mapping"), dict) else None)
    burn_in = render_manifest.get("subtitle_burn_in") if isinstance(render_manifest.get("subtitle_burn_in"), dict) else {}
    burn_in_mode = burn_in.get("requested_mode") or "off"
    if not (source_video.get("material_id") and source_audio.get("material_id") and edit_pack.get("path") and output_id):
        return None
    parts = [
        "python -m src.cli.main render-tiny-proof",
        f"--episode-id {episode_id}",
        f"--source-video-material-id {source_video['material_id']}",
        f"--source-audio-material-id {source_audio['material_id']}",
        f"--edit-pack-path {edit_pack['path']}",
        f"--output-id {output_id}",
    ]
    if duration is not None:
        parts.append(f"--duration-sec {duration}")
    if burn_in_mode != "off":
        parts.append(f"--burn-in-subtitles {burn_in_mode}")
    parts.extend(["--force", "--format json"])
    return " ".join(parts)


def _dependency_artifacts(
    *,
    transcript_path: Path,
    edit_pack_path: Path,
    rights_manifest_path: Path,
    material_ledger_path: Path,
    render_manifest_path: Path | None,
    render_receipt_path: Path | None,
    render_report_path: Path | None,
    nle_manifest_path: Path | None,
    source_identity: dict[str, Any],
    base_dir: Path,
) -> dict[str, Any]:
    subtitle_track = source_identity.get("subtitle_track")
    subtitle_path = Path(subtitle_track) if isinstance(subtitle_track, str) and subtitle_track != "unknown" else None
    render_receipt_path = render_receipt_path or (
        render_manifest_path.parent / "render_receipt.json" if render_manifest_path else None
    )
    render_report_path = render_report_path or (
        render_manifest_path.parent / "render_report.html" if render_manifest_path else None
    )
    nle_report_path = nle_manifest_path.parent / "nle_export_report.html" if nle_manifest_path else None
    return {
        "transcript": _artifact("transcript.json", transcript_path, base_dir),
        "edit_pack": _artifact("edit_pack.json", edit_pack_path, base_dir),
        "rights_manifest": _artifact("rights_manifest.json", rights_manifest_path, base_dir),
        "material_ledger": _artifact("material_ledger.json", material_ledger_path, base_dir),
        "subtitle_track": _artifact("subtitle_track", subtitle_path, base_dir),
        "render_manifest": _artifact("render_manifest.json", render_manifest_path, base_dir),
        "render_receipt": _artifact("render_receipt.json", render_receipt_path, base_dir),
        "render_report": _artifact("render_report.html", render_report_path, base_dir),
        "nle_manifest": _artifact("nle_export_manifest.json", nle_manifest_path, base_dir),
        "nle_report": _artifact("nle_export_report.html", nle_report_path, base_dir),
    }


def _boundary(
    *,
    artifact_kind: str,
    rights: dict[str, Any],
    render_manifest: dict[str, Any],
) -> dict[str, Any]:
    rights_status = _rights_status(rights)
    production_candidate = render_manifest.get("production_candidate")
    creative_acceptance = render_manifest.get("creative_acceptance")
    publish_acceptance = render_manifest.get("publish_acceptance")
    if artifact_kind == DEFAULT_HANDOFF_KIND:
        production_candidate = False if production_candidate is None else production_candidate
        creative_acceptance = False if creative_acceptance is None else creative_acceptance
        publish_acceptance = False if publish_acceptance is None else publish_acceptance
    return {
        "production_candidate": bool(production_candidate) if production_candidate is not None else False,
        "creative_acceptance": bool(creative_acceptance) if creative_acceptance is not None else False,
        "publish_acceptance": bool(publish_acceptance) if publish_acceptance is not None else False,
        "rights_status": rights_status,
        "production_usage_allowed": rights_status == "passed"
        and bool(production_candidate)
        and bool(creative_acceptance)
        and bool(publish_acceptance),
        "diagnostic_render_only": artifact_kind == DEFAULT_HANDOFF_KIND,
        "rights_review_required_before_production": rights_status != "passed",
    }


def _handoff_status(
    *,
    artifact_kind: str,
    generated_by_command: str | None,
    dependency_artifacts: dict[str, Any],
) -> dict[str, Any]:
    required = [
        dependency_artifacts[name]
        for name in ("transcript", "edit_pack", "rights_manifest", "material_ledger", "render_manifest")
        if name in dependency_artifacts
    ]
    required_present = all(bool(item.get("exists")) for item in required)
    return {
        "transferable_by_git": False,
        "regeneratable": bool(generated_by_command and required_present),
        "requires_local_media": artifact_kind in {"diagnostic_render_video", "source_video", "source_audio"},
        "requires_external_credentials": False if artifact_kind == DEFAULT_HANDOFF_KIND else "unknown",
        "requires_rights_review_before_production": True,
    }


def _missing_behavior(
    *,
    artifact_kind: str,
    local_path: str,
    generated_by_command: str | None,
    dependency_artifacts: dict[str, Any],
) -> dict[str, Any]:
    required = [
        item.get("path")
        for item in dependency_artifacts.values()
        if item.get("path") and item.get("name") not in {"nle_export_report.html"}
    ]
    return {
        "when_absent_show": (
            f"{artifact_kind} is missing at {local_path}. Treat it as unavailable local diagnostic evidence, "
            "not as a failed production candidate."
        ),
        "regeneration_command": generated_by_command or "unknown",
        "required_upstream_artifacts": required,
        "exact_verification": (
            "Exact match: compare sha256 only when source media, upstream JSON artifacts, render command, "
            "tool versions, and render profile are unchanged."
        ),
        "approximate_verification": (
            "Approximate match: compare render_manifest output duration/resolution/video_codec/audio_codec, "
            "timeline cut_id/render_start/duration, subtitle source refs, and boundary flags. Encoder drift may change sha256."
        ),
        "production_acceptance_rule": (
            "If regeneration cannot be completed, keep the artifact missing and do not advance to production, creative, or publish acceptance."
        ),
    }


def _render_readback(render_manifest: dict[str, Any]) -> dict[str, Any]:
    metadata = render_manifest.get("output_metadata") if isinstance(render_manifest.get("output_metadata"), dict) else {}
    return {
        "duration_seconds": metadata.get("duration_seconds"),
        "resolution": metadata.get("resolution"),
        "video_codec": metadata.get("video_codec"),
        "audio_codec": metadata.get("audio_codec"),
        "container": metadata.get("container"),
        "fps": metadata.get("fps"),
        "stream_count": metadata.get("stream_count"),
    }


def _handoff_html(manifest: dict[str, Any]) -> str:
    artifact = manifest.get("artifact") or {}
    source = manifest.get("source_identity") or {}
    boundary = manifest.get("boundary") or {}
    handoff = manifest.get("handoff_status") or {}
    missing = manifest.get("missing_behavior") or {}
    dependencies = manifest.get("dependency_artifacts") or {}
    dep_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(name))}</td>"
        f"<td>{escape(str(item.get('exists', False)).lower())}</td>"
        f"<td>{escape(str(item.get('path') or ''))}</td>"
        f"<td>{escape(str(item.get('size_bytes') or ''))}</td>"
        f"<td>{escape(str(item.get('sha256') or ''))}</td>"
        "</tr>"
        for name, item in dependencies.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Non-Repo Artifact Handoff - {escape(str(manifest.get("episode_id", "")))}</title>
  <style>
    body {{ font-family: sans-serif; line-height: 1.4; margin: 24px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; vertical-align: top; }}
    th {{ background: #f2f2f2; }}
    .warn {{ color: #7a3b00; font-weight: 600; }}
    code {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Non-Repo Artifact Handoff</h1>
  <p class="warn">Binary artifact is excluded from Git. This page records identity and recovery steps only; it does not embed or auto-open video.</p>

  <h2>Artifact</h2>
  <dl>
    <dt>episode_id</dt><dd>{escape(str(manifest.get("episode_id", "")))}</dd>
    <dt>artifact_id</dt><dd>{escape(str(manifest.get("artifact_id", "")))}</dd>
    <dt>artifact_kind</dt><dd>{escape(str(artifact.get("artifact_kind", "")))}</dd>
    <dt>git_policy</dt><dd>{escape(str(artifact.get("git_policy", "")))}</dd>
    <dt>local_path</dt><dd>{escape(str(artifact.get("local_path", "")))}</dd>
    <dt>repo_relative_path</dt><dd>{escape(str(artifact.get("repo_relative_path", "")))}</dd>
    <dt>exists</dt><dd>{escape(str(artifact.get("exists", False)).lower())}</dd>
    <dt>size_bytes</dt><dd>{escape(str(artifact.get("size_bytes") or ""))}</dd>
    <dt>sha256</dt><dd>{escape(str(artifact.get("sha256") or ""))}</dd>
    <dt>generated_by_command</dt><dd><code>{escape(str(artifact.get("generated_by_command") or "unknown"))}</code></dd>
  </dl>

  <h2>Source Video Identity</h2>
  <dl>
    <dt>Source video identity</dt><dd>{escape(str(source.get("source_video_identity", "unknown")))}</dd>
    <dt>YouTube ID</dt><dd>{escape(str(source.get("youtube_id", "unknown")))}</dd>
    <dt>Source URL</dt><dd>{escape(str(source.get("source_url", "unknown")))}</dd>
    <dt>Subtitle track</dt><dd>{escape(str(source.get("subtitle_track", "unknown")))}</dd>
    <dt>Transcript source</dt><dd>{escape(str(source.get("transcript_source", "unknown")))}</dd>
    <dt>Source video material id</dt><dd>{escape(str(source.get("source_video_material_id", "unknown")))}</dd>
    <dt>Source audio material id</dt><dd>{escape(str(source.get("source_audio_material_id", "unknown")))}</dd>
    <dt>Rights status</dt><dd>{escape(str(boundary.get("rights_status", "unknown")))}</dd>
    <dt>Production usage</dt><dd>{escape("not allowed until rights approval" if not boundary.get("production_usage_allowed") else "allowed by current boundary")}</dd>
  </dl>

  <h2>Render Readback</h2>
  <pre>{escape(json.dumps(artifact.get("render_readback") or {}, ensure_ascii=False, indent=2))}</pre>

  <h2>Boundary</h2>
  <dl>
    <dt>production_candidate</dt><dd>{escape(str(boundary.get("production_candidate", False)).lower())}</dd>
    <dt>creative_acceptance</dt><dd>{escape(str(boundary.get("creative_acceptance", False)).lower())}</dd>
    <dt>publish_acceptance</dt><dd>{escape(str(boundary.get("publish_acceptance", False)).lower())}</dd>
    <dt>transferable_by_git</dt><dd>{escape(str(handoff.get("transferable_by_git", False)).lower())}</dd>
    <dt>regeneratable</dt><dd>{escape(str(handoff.get("regeneratable", False)).lower())}</dd>
    <dt>requires_local_media</dt><dd>{escape(str(handoff.get("requires_local_media", "")).lower())}</dd>
  </dl>

  <h2>Dependency Artifacts</h2>
  <table>
    <thead><tr><th>name</th><th>exists</th><th>path</th><th>size</th><th>sha256</th></tr></thead>
    <tbody>{dep_rows}</tbody>
  </table>

  <h2>Missing Behavior</h2>
  <p>{escape(str(missing.get("when_absent_show", "")))}</p>
  <p><code>{escape(str(missing.get("regeneration_command", "unknown")))}</code></p>
  <p>{escape(str(missing.get("exact_verification", "")))}</p>
  <p>{escape(str(missing.get("approximate_verification", "")))}</p>
  <p>{escape(str(missing.get("production_acceptance_rule", "")))}</p>
</body>
</html>
"""


def _artifact(name: str, path: Path | None, base_dir: Path) -> dict[str, Any]:
    if path is None:
        return {"name": name, "path": None, "exists": False, "size_bytes": None, "sha256": None}
    resolved = _resolve_path(path, base=base_dir, anchor=base_dir)
    exists = resolved.exists() and resolved.is_file()
    return {
        "name": name,
        "path": _display_path(resolved, base_dir),
        "exists": exists,
        "size_bytes": resolved.stat().st_size if exists else None,
        "sha256": _sha256(resolved) if exists else None,
    }


def _resolve_path(path: Path, *, base: Path, anchor: Path) -> Path:
    if path.is_absolute():
        return path
    candidates = [base / path, anchor / path, path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return base / path


def _load_json_optional(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _episode_id(
    episode_dir: Path,
    render_manifest: dict[str, Any],
    transcript: dict[str, Any],
    rights: dict[str, Any],
) -> str:
    return (
        _string_or_none(render_manifest.get("episode_id"))
        or _string_or_none(transcript.get("episode_id"))
        or _string_or_none(rights.get("episode_id"))
        or episode_dir.name
    )


def _rights_status(rights: dict[str, Any]) -> str:
    compliance = rights.get("compliance_check") if isinstance(rights.get("compliance_check"), dict) else {}
    return _string_or_none(compliance.get("status")) or "missing"


def _transcript_source_label(engine: str | None, provider: str | None) -> str:
    if engine == "subtitle_track" and provider == "youtube_subtitles":
        return "imported subtitle track / youtube_subtitles"
    if engine and provider:
        return f"{engine} / {provider}"
    return engine or provider or "unknown"


def _first_material_id(material_ledger: dict[str, Any], kind: str) -> str | None:
    materials = material_ledger.get("materials") if isinstance(material_ledger.get("materials"), list) else []
    for material in materials:
        if isinstance(material, dict) and material.get("kind") == kind and material.get("id"):
            return str(material["id"])
    return None


def _youtube_id_from_path(path: str | None) -> str | None:
    if not path:
        return None
    match = YOUTUBE_ID_PATTERN.search(Path(path).name)
    return match.group(1) if match else None


def _youtube_id_from_url(url: str | None) -> str | None:
    if not url or "<query:redacted>" in url:
        return None
    parsed = urlparse(url)
    if parsed.netloc.endswith("youtu.be"):
        candidate = parsed.path.strip("/").split("/")[0]
        return candidate if YOUTUBE_ID_PATTERN.fullmatch(candidate) else None
    query_id = parse_qs(parsed.query).get("v", [None])[0]
    if query_id and YOUTUBE_ID_PATTERN.fullmatch(query_id):
        return query_id
    match = YOUTUBE_ID_PATTERN.search(url)
    return match.group(1) if match else None


def _first_existing(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    return next(iter(sorted(root.glob(pattern))), None)


def _string_or_none(value: Any) -> str | None:
    return str(value) if isinstance(value, str) and value else None


def _display_path(path: Path | None, base: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def _absolute_display_path(path: Path) -> str:
    try:
        return str(path.resolve()).replace("\\", "/")
    except OSError:
        return str(path).replace("\\", "/")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
