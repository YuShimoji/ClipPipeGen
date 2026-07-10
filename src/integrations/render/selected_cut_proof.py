"""Build one real-local selected-cut review proof from existing artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from html import escape
from pathlib import Path
from typing import Any

from . import ffmpeg_tiny


ARTIFACT_ID = "clip-out03-real-local-selected-cut-proof-v0-001"
STATE = "real_local_selected_cut_review_proof_ready"
TIMING_TOLERANCE_SECONDS = 0.05
SAFE_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
REAL_TRANSCRIPT_SOURCES = {
    ("subtitle_track", "youtube_subtitles"),
    ("vosk", "vosk"),
}
REAL_SUBTITLE_SOURCE_TYPES = {
    "imported_subtitle_track",
    "real_transcript",
}
REAL_MATERIAL_REGISTRATION_PREFIXES = (
    "tool:asset_fetch_yt_dlp_",
    "tool:asset_fetch_local_",
)


class SelectedCutProofError(ValueError):
    """Raised when an input cannot honestly support the OUT-03 proof."""


def build_selected_cut_proof(
    *,
    episode_dir: Path,
    output_dir: Path,
    cut_id: str,
    proof_video_path: Path,
    proof_source_readback_path: Path,
    source_video_material_id: str,
    source_audio_material_id: str,
    ffprobe_path: str | Path | None = None,
    base_dir: Path,
    runner=subprocess.run,
) -> dict[str, Any]:
    """Validate and package one playable proof without changing source artifacts."""

    root = base_dir.resolve()
    episode = _resolved(root, episode_dir)
    output = _resolved(root, output_dir)
    proof_video = _resolved(root, proof_video_path)
    proof_source_readback = _resolved(root, proof_source_readback_path)

    _require_directory(episode, "episode directory")
    _safe_identifier(cut_id, "cut id")
    review_root = episode / "review"
    if output.parent != review_root or not output.name.startswith("out03_"):
        raise SelectedCutProofError(
            "output directory must be a dedicated review/out03_* directory"
        )
    if proof_video.is_relative_to(output) or proof_source_readback.is_relative_to(
        output
    ):
        raise SelectedCutProofError("output directory must not contain proof inputs")
    _require_file(proof_video, "proof video")
    if proof_video.suffix.lower() != ".mp4":
        raise SelectedCutProofError("proof video must be a browser-playable MP4")
    _require_within(proof_video, episode, "proof video")
    _require_file(proof_source_readback, "proof source readback")
    _require_within(proof_source_readback, episode, "proof source readback")

    edit_pack_path = episode / "edit_pack.json"
    transcript_path = episode / "transcript.json"
    ledger_path = episode / "material_ledger.json"
    rights_path = episode / "rights_manifest.json"
    edit_pack = _read_object(edit_pack_path)
    transcript = _read_object(transcript_path)
    ledger = _read_object(ledger_path)
    rights = _read_object(rights_path)

    cut = _selected_cut(edit_pack, cut_id)
    cut_start = _number(cut.get("start_seconds"), "cut start_seconds")
    cut_end = _number(cut.get("end_seconds"), "cut end_seconds")
    if cut_end <= cut_start:
        raise SelectedCutProofError("selected cut end_seconds must be after start_seconds")
    cut_duration = round(cut_end - cut_start, 6)
    cut_segment_ids = _string_list(cut.get("source_segment_ids"))
    if not cut_segment_ids:
        raise SelectedCutProofError("selected cut needs source_segment_ids")

    transcript_readback, transcript_segments = _real_transcript(
        transcript,
        transcript_path,
        root,
        cut_segment_ids,
    )
    subtitles = _linked_subtitles(
        edit_pack,
        cut_id=cut_id,
        cut_start=cut_start,
        cut_end=cut_end,
        cut_segment_ids=cut_segment_ids,
        transcript_segments=transcript_segments,
    )

    source_video = _material_readback(
        ledger,
        source_video_material_id,
        "source_video",
        episode,
        root,
    )
    source_audio = _material_readback(
        ledger,
        source_audio_material_id,
        "source_audio",
        episode,
        root,
    )
    source_proof = _source_proof_readback(
        proof_source_readback,
        proof_video,
        cut_id,
        root,
    )

    probe = ffmpeg_tiny.probe_media(
        input_path=proof_video,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    media = probe.metadata
    proof_duration = _number(media.get("duration_seconds"), "proof duration")
    if abs(proof_duration - cut_duration) > TIMING_TOLERANCE_SECONDS:
        raise SelectedCutProofError(
            "proof duration does not match selected cut: "
            f"proof={proof_duration:.6f}s cut={cut_duration:.6f}s"
        )
    stream_counts = media.get("stream_counts") or {}
    if stream_counts.get("video", 0) < 1 or stream_counts.get("audio", 0) < 1:
        raise SelectedCutProofError("proof video needs both video and audio streams")

    output.mkdir(parents=True, exist_ok=True)
    assets_dir = output / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    proof_asset = assets_dir / f"{cut_id}.mp4"
    shutil.copyfile(proof_video, proof_asset)
    source_proof_hash = _sha256(proof_video)
    if _sha256(proof_asset) != source_proof_hash:
        raise SelectedCutProofError("copied proof asset hash does not match its source")

    rights_status = str(
        (rights.get("compliance_check") or {}).get("status") or "unknown"
    )
    readback_path = output / "proof_readback.json"
    index_path = output / "index.html"
    open_path = output / "open_preview.ps1"
    serve_path = output / "serve_preview.ps1"
    readback = {
        "schema_version": "v1",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "source_class": "real_local_retained_source_media",
        "episode_id": str(edit_pack.get("episode_id") or episode.name),
        "selected_cut": {
            "id": cut_id,
            "start_seconds": cut_start,
            "end_seconds": cut_end,
            "duration_seconds": cut_duration,
            "source_segment_ids": cut_segment_ids,
            "context_status": str(
                (cut.get("context_check") or {}).get("status") or "unknown"
            ),
        },
        "transcript": transcript_readback,
        "subtitles": subtitles,
        "materials": {
            "source_video": source_video,
            "source_audio": source_audio,
        },
        "proof": {
            "source_path": _relative(proof_video, root),
            "asset_path": _relative(proof_asset, root),
            "source_readback": source_proof,
            "hash_sha256": source_proof_hash,
            "byte_size": proof_asset.stat().st_size,
            "media": media,
            "duration_matches_selected_cut": True,
        },
        "review_entrypoint": _relative(index_path, root),
        "machine_readback": _relative(readback_path, root),
        "open_command": _powershell_command(open_path, root),
        "serve_command": _powershell_command(open_path, root) + " -Serve",
        "boundaries": {
            "diagnostic_only": True,
            "local_retained_same_machine_only": True,
            "tracked_media": False,
            "rights_status": rights_status,
            "rights_approved": False,
            "production_candidate": False,
            "production_ready": False,
            "production_render_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "creative_acceptance": False,
            "publishing_acceptance": False,
            "publish_attempted": False,
            "public_ready": False,
            "public_use_permission": False,
        },
        "validation": {
            "selected_cut_present": True,
            "real_transcript": True,
            "subtitle_timing_inside_cut": True,
            "source_segment_linkage": True,
            "proof_source_readback_matches": True,
            "ffprobe_passed": True,
            "proof_asset_hash_matches": True,
        },
    }
    _write_text(readback_path, json.dumps(readback, ensure_ascii=False, indent=2) + "\n")
    _write_text(index_path, _render_html(readback))
    _write_text(open_path, _open_script())
    _write_text(serve_path, _serve_script())
    return {
        "readback": readback,
        "readback_path": readback_path,
        "index_path": index_path,
        "open_path": open_path,
        "serve_path": serve_path,
        "proof_asset_path": proof_asset,
    }


def _selected_cut(edit_pack: dict[str, Any], cut_id: str) -> dict[str, Any]:
    selected_ids = _string_list(edit_pack.get("selected_cut_ids"))
    if cut_id not in selected_ids:
        raise SelectedCutProofError(f"cut is not selected: {cut_id}")
    cuts = edit_pack.get("cut_candidates") or []
    cut = next(
        (item for item in cuts if isinstance(item, dict) and item.get("id") == cut_id),
        None,
    )
    if cut is None:
        raise SelectedCutProofError(f"selected cut is missing from cut_candidates: {cut_id}")
    return cut


def _real_transcript(
    transcript: dict[str, Any],
    path: Path,
    root: Path,
    required_segment_ids: list[str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    stt = transcript.get("stt") or {}
    engine = str(stt.get("engine") or "")
    provider = str(stt.get("provider") or "")
    if stt.get("real_transcript") is not True:
        raise SelectedCutProofError("transcript must set stt.real_transcript=true")
    source_pair = (engine.lower(), provider.lower())
    if source_pair not in REAL_TRANSCRIPT_SOURCES:
        raise SelectedCutProofError(
            "transcript engine/provider is not an allowed real source: "
            f"{engine}/{provider}"
        )
    segments = {
        str(item.get("id")): item
        for item in (transcript.get("segments") or [])
        if isinstance(item, dict) and item.get("id")
    }
    missing = [segment_id for segment_id in required_segment_ids if segment_id not in segments]
    if missing:
        raise SelectedCutProofError(
            "selected cut transcript segments are missing: " + ", ".join(missing)
        )
    return (
        {
            "path": _relative(path, root),
            "engine": engine,
            "provider": provider,
            "real_transcript": True,
            "language": transcript.get("language"),
            "review_status": (transcript.get("review") or {}).get("status"),
            "segment_ids": required_segment_ids,
        },
        segments,
    )


def _linked_subtitles(
    edit_pack: dict[str, Any],
    *,
    cut_id: str,
    cut_start: float,
    cut_end: float,
    cut_segment_ids: list[str],
    transcript_segments: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = [
        item
        for item in (edit_pack.get("subtitles") or [])
        if isinstance(item, dict) and item.get("cut_id") == cut_id
    ]
    if not rows:
        raise SelectedCutProofError(f"selected cut has no subtitle rows: {cut_id}")
    result: list[dict[str, Any]] = []
    for item in rows:
        start = _number(item.get("start_seconds"), "subtitle start_seconds")
        end = _number(item.get("end_seconds"), "subtitle end_seconds")
        if start < cut_start - 0.001 or end > cut_end + 0.001 or end <= start:
            raise SelectedCutProofError(
                f"subtitle timing falls outside selected cut: {item.get('id')}"
            )
        segment_ids = _string_list(item.get("source_segment_ids"))
        if not segment_ids and item.get("source_segment_id"):
            segment_ids = [str(item["source_segment_id"])]
        if not segment_ids or any(segment_id not in cut_segment_ids for segment_id in segment_ids):
            raise SelectedCutProofError(
                f"subtitle source linkage is outside selected cut: {item.get('id')}"
            )
        if any(segment_id not in transcript_segments for segment_id in segment_ids):
            raise SelectedCutProofError(
                f"subtitle transcript segment is missing: {item.get('id')}"
            )
        source_text = " ".join(
            str(transcript_segments[segment_id].get("text") or "").strip()
            for segment_id in segment_ids
        ).strip()
        subtitle_text = str(item.get("text") or "").strip()
        if not subtitle_text or source_text != subtitle_text:
            raise SelectedCutProofError(
                f"subtitle text does not match linked transcript: {item.get('id')}"
            )
        source_type = str(item.get("source_type") or "")
        if source_type not in REAL_SUBTITLE_SOURCE_TYPES:
            raise SelectedCutProofError(
                f"subtitle source_type is not real/non-fixture: {item.get('id')}"
            )
        result.append(
            {
                "id": item.get("id"),
                "start_seconds": start,
                "end_seconds": end,
                "text": subtitle_text,
                "source_type": source_type,
                "source_segment_ids": segment_ids,
            }
        )
    return result


def _material_readback(
    ledger: dict[str, Any],
    material_id: str,
    expected_kind: str,
    episode: Path,
    root: Path,
) -> dict[str, Any]:
    material = next(
        (
            item
            for item in (ledger.get("materials") or [])
            if isinstance(item, dict) and item.get("id") == material_id
        ),
        None,
    )
    if material is None:
        raise SelectedCutProofError(f"material is missing: {material_id}")
    if material.get("kind") != expected_kind:
        raise SelectedCutProofError(
            f"material kind mismatch for {material_id}: {material.get('kind')}"
        )
    material_path = _resolved(root, Path(str(material.get("file_path") or "")))
    _require_file(material_path, f"material {material_id}")
    _require_within(material_path, episode, f"material {material_id}")
    actual_hash = _sha256(material_path)
    recorded_hash = material.get("hash_sha256")
    if not recorded_hash:
        raise SelectedCutProofError(f"material recorded hash is required: {material_id}")
    if str(recorded_hash).lower() != actual_hash:
        raise SelectedCutProofError(f"material hash mismatch: {material_id}")
    registered_by = str(material.get("registered_by") or "")
    if not registered_by.startswith(REAL_MATERIAL_REGISTRATION_PREFIXES):
        raise SelectedCutProofError(
            f"material provenance is not an allowed real acquisition route: {material_id}"
        )
    return {
        "id": material_id,
        "kind": expected_kind,
        "path": _relative(material_path, root),
        "hash_sha256": actual_hash,
        "byte_size": material_path.stat().st_size,
        "source_class": "real_local_retained_material",
        "retrieval_method": registered_by,
    }


def _source_proof_readback(
    path: Path,
    proof_video: Path,
    cut_id: str,
    root: Path,
) -> dict[str, Any]:
    payload = _read_object(path)
    assessment = next(
        (
            item
            for item in (payload.get("per_cut_visual_assessment") or [])
            if isinstance(item, dict) and item.get("cut_id") == cut_id
        ),
        None,
    )
    if assessment is None:
        raise SelectedCutProofError(
            f"proof source readback has no assessment for {cut_id}"
        )
    recorded_path = assessment.get("visual_proof_video_artifact_path")
    if not recorded_path or _resolved(root, Path(str(recorded_path))) != proof_video:
        raise SelectedCutProofError("proof source readback points at a different video")
    status = str(assessment.get("visual_proof_status") or "")
    if not status.startswith("available_"):
        raise SelectedCutProofError("proof source readback does not mark the proof available")
    if assessment.get("subtitle_overlay_present") is not True:
        raise SelectedCutProofError("proof source readback does not confirm subtitle overlay")
    return {
        "path": _relative(path, root),
        "status": status,
        "source_used": assessment.get("source_used"),
        "subtitle_overlay_present": True,
    }


def _render_html(readback: dict[str, Any]) -> str:
    cut = readback["selected_cut"]
    subtitles = readback["subtitles"]
    subtitle_rows = "".join(
        "<tr>"
        f"<td><code>{escape(str(item['id']))}</code></td>"
        f"<td>{item['start_seconds']:.3f}–{item['end_seconds']:.3f}s</td>"
        f"<td>{escape(str(item['text']))}</td>"
        f"<td><code>{escape(', '.join(item['source_segment_ids']))}</code></td>"
        "</tr>"
        for item in subtitles
    )
    materials = readback["materials"]
    proof = readback["proof"]
    boundaries = readback["boundaries"]
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OUT-03 実素材 Selected Cut Review</title>
  <style>
    :root {{ color-scheme: dark; font-family: system-ui, sans-serif; background: #0b0d12; color: #f5f7fb; }}
    body {{ margin: 0; }}
    main {{ max-width: 1180px; margin: auto; padding: 28px; }}
    .eyebrow {{ color: #86e1c4; font-weight: 700; letter-spacing: .08em; }}
    h1 {{ margin: .35rem 0; font-size: clamp(1.8rem, 4vw, 3.4rem); }}
    .boundary {{ color: #ffd38a; margin: 0 0 20px; }}
    .stage {{ display: grid; grid-template-columns: minmax(0, 2.2fr) minmax(260px, 1fr); gap: 22px; align-items: start; }}
    video {{ display: block; width: 100%; border-radius: 12px; background: #000; box-shadow: 0 16px 48px #0009; }}
    aside {{ border-left: 3px solid #86e1c4; padding-left: 18px; }}
    .metric {{ margin: 0 0 14px; }} .metric b {{ display: block; color: #aeb7c8; font-size: .8rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 26px; }}
    th, td {{ border-bottom: 1px solid #303746; padding: 12px 8px; text-align: left; vertical-align: top; }}
    th {{ color: #aeb7c8; }} code {{ color: #aeead8; overflow-wrap: anywhere; }}
    details {{ margin-top: 24px; padding: 16px; background: #141923; border-radius: 10px; }}
    @media (max-width: 800px) {{ .stage {{ grid-template-columns: 1fr; }} aside {{ border-left: 0; border-top: 3px solid #86e1c4; padding: 16px 0 0; }} }}
  </style>
</head>
<body><main>
  <div class="eyebrow">OUT-03 · REAL LOCAL REVIEW PROOF</div>
  <h1>選択カット <code>{escape(str(cut['id']))}</code></h1>
  <p class="boundary">内部診断レビュー専用。権利・production・公開・投稿の承認ではありません。</p>
  <section class="stage">
    <video controls preload="metadata" src="assets/{escape(str(cut['id']))}.mp4"></video>
    <aside>
      <p class="metric"><b>ソース区分</b>実ローカル保持素材</p>
      <p class="metric"><b>ソース時間</b>{cut['start_seconds']:.3f}–{cut['end_seconds']:.3f}s</p>
      <p class="metric"><b>カット長</b>{cut['duration_seconds']:.3f}s</p>
      <p class="metric"><b>Transcript</b>{escape(str(readback['transcript']['engine']))} / {escape(str(readback['transcript']['provider']))}</p>
      <p class="metric"><b>Context</b>{escape(str(cut['context_status']))}</p>
      <p class="metric"><b>確認すること</b>映像・選択区間・字幕が同じカットとして直接レビューできるか。</p>
    </aside>
  </section>
  <table><thead><tr><th>字幕</th><th>時間</th><th>本文</th><th>Transcript segment</th></tr></thead><tbody>{subtitle_rows}</tbody></table>
  <details><summary>Provenance / gate readback</summary>
    <p>Source video: <code>{escape(str(materials['source_video']['id']))}</code> · {materials['source_video']['byte_size']} bytes</p>
    <p>Source audio: <code>{escape(str(materials['source_audio']['id']))}</code> · {materials['source_audio']['byte_size']} bytes</p>
    <p>Proof: {proof['media']['duration_seconds']:.3f}s · {escape(str(proof['media']['video_codec']))}/{escape(str(proof['media']['audio_codec']))} · {escape(str(proof['media']['resolution']))}</p>
    <p>Rights: <code>{escape(str(boundaries['rights_status']))}</code>; production_candidate=false; public_ready=false; publishing_acceptance=false.</p>
  </details>
</main></body></html>
"""


def _open_script() -> str:
    return """param([switch]$Serve, [int]$Port = 8000)
$ErrorActionPreference = 'Stop'
if ($Serve) {
    & (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
    exit $LASTEXITCODE
}
$index = Join-Path $PSScriptRoot 'index.html'
Write-Host "OUT-03 review entrypoint: $index"
Start-Process -FilePath $index
Write-Host "If local-file playback is blocked, rerun this command with -Serve."
"""


def _serve_script() -> str:
    return """param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
Write-Host "OUT-03 review URL: $url"
Start-Process -FilePath $url
Push-Location $PSScriptRoot
try {
    uvx python -m http.server $Port --bind 127.0.0.1
} finally {
    Pop-Location
}
"""


def _read_object(path: Path) -> dict[str, Any]:
    _require_file(path, "JSON input")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise SelectedCutProofError(f"JSON root must be an object: {path}")
    return payload


def _resolved(root: Path, path: Path) -> Path:
    return (path if path.is_absolute() else root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SelectedCutProofError(f"{label} is missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise SelectedCutProofError(f"{label} is missing: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    if not path.is_relative_to(parent):
        raise SelectedCutProofError(f"{label} must stay inside the episode directory")


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as exc:
        raise SelectedCutProofError(f"path is outside the repository: {path}") from exc


def _powershell_command(path: Path, root: Path) -> str:
    relative = _relative(path, root).replace("/", "\\")
    return f"powershell -ExecutionPolicy Bypass -File {relative}"


def _number(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise SelectedCutProofError(f"{label} must be numeric") from exc


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int))]


def _safe_identifier(value: str, label: str) -> None:
    if SAFE_IDENTIFIER.fullmatch(value) is None:
        raise SelectedCutProofError(f"{label} contains unsafe path characters")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
