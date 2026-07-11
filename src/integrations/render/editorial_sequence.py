"""OUT-04 real-local editorial representative sequence builder.

This module owns one narrow FFmpeg orchestration: trim two or three retained
real cuts, concatenate them in an explicit order, burn sequence-relative
diagnostic subtitles, and expose one same-machine review surface. It is not a
production renderer or a general timeline framework.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from html import escape
from pathlib import Path
from typing import Any

from src.integrations.render.ffmpeg_tiny import (
    COMMAND_TIMEOUT_SECONDS,
    Runner,
    TinyRenderError,
    preflight_tools,
    probe_media,
)


ARTIFACT_ID = "clip-out04-editorial-representative-sequence-v0-001"
STATE = "real_local_editorial_representative_sequence_review_ready"
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
    "tool:asset_fetch_local_",
    "tool:asset_fetch_yt_dlp_",
)
MIN_CUT_COUNT = 2
MAX_CUT_COUNT = 3
MIN_SEQUENCE_SECONDS = 10.0
MAX_SEQUENCE_SECONDS = 30.0
LINKAGE_TOLERANCE_SECONDS = 0.05
OUTPUT_DURATION_TOLERANCE_SECONDS = 0.20


class EditorialSequenceError(ValueError):
    """Raised when inputs cannot honestly support the OUT-04 sequence."""


def build_editorial_sequence(
    *,
    episode_dir: str | Path,
    output_dir: str | Path,
    cut_ids: list[str],
    cut_decision_readback_path: str | Path,
    source_video_material_id: str,
    source_audio_material_id: str,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Build one ignored multi-cut review package and return its paths/readback."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(root, Path(output_dir))
    decision_path = _resolved(root, Path(cut_decision_readback_path))
    _require_directory(episode, "episode directory")
    _require_within(episode, root, "episode directory")
    _validate_output_directory(episode, output)
    _validate_cut_ids(cut_ids)
    _safe_identifier(source_video_material_id, "source video material id")
    _safe_identifier(source_audio_material_id, "source audio material id")

    edit_pack_path = episode / "edit_pack.json"
    transcript_path = episode / "transcript.json"
    ledger_path = episode / "material_ledger.json"
    rights_path = episode / "rights_manifest.json"
    input_paths = [edit_pack_path, transcript_path, ledger_path, rights_path, decision_path]
    for path in input_paths:
        _require_file(path, path.name)
        _require_within(path, episode, path.name)
        _reject_overlap(output, path, "output directory must not overlap an input file")

    edit_pack = _read_object(edit_pack_path)
    transcript = _read_object(transcript_path)
    ledger = _read_object(ledger_path)
    rights = _read_object(rights_path)
    decisions = _read_object(decision_path)

    transcript_info, transcript_segments = _real_transcript(transcript)
    selected_cuts = _ordered_cuts(edit_pack, decisions, cut_ids)
    timeline, subtitle_rows = _sequence_timeline(
        edit_pack=edit_pack,
        selected_cuts=selected_cuts,
        transcript_segments=transcript_segments,
    )
    expected_duration = round(sum(item["duration_seconds"] for item in timeline), 3)
    if expected_duration < MIN_SEQUENCE_SECONDS - LINKAGE_TOLERANCE_SECONDS:
        raise EditorialSequenceError(
            f"sequence duration must be at least {MIN_SEQUENCE_SECONDS:.0f}s; got {expected_duration:.3f}s"
        )
    if expected_duration > MAX_SEQUENCE_SECONDS + LINKAGE_TOLERANCE_SECONDS:
        raise EditorialSequenceError(
            f"sequence duration must be at most {MAX_SEQUENCE_SECONDS:.0f}s; got {expected_duration:.3f}s"
        )

    video_material = _material_readback(
        ledger,
        material_id=source_video_material_id,
        expected_kind="source_video",
        root=root,
        episode=episode,
    )
    audio_material = _material_readback(
        ledger,
        material_id=source_audio_material_id,
        expected_kind="source_audio",
        root=root,
        episode=episode,
    )
    source_video_path = _resolved(root, Path(video_material["file_path"]))
    source_audio_path = _resolved(root, Path(audio_material["file_path"]))
    _reject_overlap(output, source_video_path, "output directory must not overlap source video")
    _reject_overlap(output, source_audio_path, "output directory must not overlap source audio")

    preflight = preflight_tools(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    if preflight.get("status") != "passed":
        reason = preflight.get("failure_reason") or "render_tool_preflight_failed"
        raise EditorialSequenceError(f"FFmpeg/FFprobe preflight failed: {reason}")
    resolved_ffmpeg = str(preflight["ffmpeg"]["path"])
    resolved_ffprobe = str(preflight["ffprobe"]["path"])
    ffprobe_version = str(preflight["ffprobe"].get("version") or "unknown")
    ffprobe_source = str(preflight["ffprobe"].get("path_source") or "unknown")
    try:
        source_video_probe = probe_media(
            input_path=source_video_path,
            ffprobe_path=resolved_ffprobe,
            ffprobe_version=ffprobe_version,
            ffprobe_path_source=ffprobe_source,
            runner=runner,
        ).metadata
        source_audio_probe = probe_media(
            input_path=source_audio_path,
            ffprobe_path=resolved_ffprobe,
            ffprobe_version=ffprobe_version,
            ffprobe_path_source=ffprobe_source,
            runner=runner,
        ).metadata
    except TinyRenderError as exc:
        raise EditorialSequenceError(f"source media probe failed: {exc}") from exc
    maximum_cut_end = max(item["source_end_seconds"] for item in timeline)
    _validate_source_probe(
        source_video_probe,
        label="source video",
        required_stream="video",
        maximum_cut_end=maximum_cut_end,
    )
    _validate_source_probe(
        source_audio_probe,
        label="source audio",
        required_stream="audio",
        maximum_cut_end=maximum_cut_end,
    )

    output.mkdir(parents=True, exist_ok=True)
    assets_dir = output / "assets"
    assets_dir.mkdir(exist_ok=True)
    srt_path = output / "sequence_subtitles.srt"
    video_path = assets_dir / "editorial_sequence.mp4"
    readback_path = output / "sequence_readback.json"
    index_path = output / "index.html"
    open_path = output / "open_preview.ps1"
    serve_path = output / "serve_preview.ps1"
    _write_text(srt_path, _render_srt(subtitle_rows))

    attempts: list[dict[str, Any]] = []
    selected_codec: str | None = None
    for codec in ("libx264", "libopenh264"):
        if video_path.exists():
            video_path.unlink()
        command = _render_command(
            ffmpeg_path=resolved_ffmpeg,
            source_video_path=source_video_path,
            source_audio_path=source_audio_path,
            output_path=video_path,
            srt_path=srt_path,
            timeline=timeline,
            video_codec=codec,
        )
        try:
            result = runner(
                command,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            attempts.append(
                {
                    "video_codec": codec,
                    "status": "failed",
                    "exit_code": None,
                    "failure_class": type(exc).__name__,
                }
            )
            continue
        status = "passed" if result.returncode == 0 and video_path.is_file() else "failed"
        attempts.append(
            {
                "video_codec": codec,
                "status": status,
                "exit_code": result.returncode,
            }
        )
        if status == "passed":
            selected_codec = codec
            break
    if selected_codec is None:
        raise EditorialSequenceError("FFmpeg sequence render failed for all H.264 profiles")

    try:
        output_probe = probe_media(
            input_path=video_path,
            ffprobe_path=resolved_ffprobe,
            ffprobe_version=ffprobe_version,
            ffprobe_path_source=ffprobe_source,
            runner=runner,
        ).metadata
    except TinyRenderError as exc:
        raise EditorialSequenceError(f"rendered sequence probe failed: {exc}") from exc
    _validate_output_probe(output_probe, expected_duration=expected_duration)

    rights_status = str((rights.get("compliance_check") or {}).get("status") or "unknown")
    readback = {
        "schema_version": "clippipegen.out04.editorial_sequence.v0",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "episode_id": str(edit_pack.get("episode_id") or episode.name),
        "source_class": "real_local_retained_source_media",
        "storage": {
            "class": "ignored_local_retained_same_machine",
            "portable_across_clones": False,
            "episodes_tracked": False,
        },
        "ordered_cut_ids": list(cut_ids),
        "transition_type": "hard_cut",
        "selection_rationale": (
            "Explicit requested order of retained keep/accepted cuts with passed context; "
            "two coherent cuts are preferred over adding a needs-review cut."
        ),
        "expected_duration_seconds": expected_duration,
        "duration_tolerance_seconds": OUTPUT_DURATION_TOLERANCE_SECONDS,
        "timeline": timeline,
        "subtitles": subtitle_rows,
        "subtitle_count": len(subtitle_rows),
        "transcript": transcript_info,
        "input_artifacts": {
            "edit_pack": {"path": _relative(edit_pack_path, root), "sha256": _sha256(edit_pack_path)},
            "transcript": {"path": _relative(transcript_path, root), "sha256": _sha256(transcript_path)},
            "material_ledger": {"path": _relative(ledger_path, root), "sha256": _sha256(ledger_path)},
            "rights_manifest": {"path": _relative(rights_path, root), "sha256": _sha256(rights_path)},
            "cut_decisions": {"path": _relative(decision_path, root), "sha256": _sha256(decision_path)},
        },
        "materials": {
            "source_video": {**video_material, "probe": source_video_probe},
            "source_audio": {**audio_material, "probe": source_audio_probe},
        },
        "render": {
            "output_path": _relative(video_path, root),
            "output_sha256": _sha256(video_path),
            "subtitle_path": _relative(srt_path, root),
            "selected_video_encoder": selected_codec,
            "attempts": attempts,
            "media": output_probe,
            "duration_matches_expected": (
                abs(float(output_probe["duration_seconds"]) - expected_duration)
                <= OUTPUT_DURATION_TOLERANCE_SECONDS
            ),
        },
        "review_entrypoint": _relative(index_path, root),
        "machine_readback": _relative(readback_path, root),
        "open_command": _powershell_command(open_path, root),
        "review_questions": [
            "この並びが一つの編集単位として自然に読めるか。",
            "急または分かりにくいカット境界があるか。",
            "結合後も字幕と音声の連続性が保たれているか。",
        ],
        "boundaries": {
            "diagnostic_only": True,
            "rights_status": rights_status,
            "rights_approval": "pending" if rights_status == "pending" else rights_status,
            "production_candidate": False,
            "production_ready": False,
            "production_acceptance": False,
            "public_ready": False,
            "publishing_acceptance": False,
            "publish_attempted": False,
        },
    }
    _write_text(
        readback_path,
        json.dumps(readback, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    _write_text(index_path, _render_html(readback))
    _write_text(open_path, _open_script())
    _write_text(serve_path, _serve_script())
    return {
        "artifact_id": ARTIFACT_ID,
        "output_dir": output,
        "video_path": video_path,
        "subtitle_path": srt_path,
        "readback_path": readback_path,
        "index_path": index_path,
        "open_path": open_path,
        "serve_path": serve_path,
        "readback": readback,
    }


def _ordered_cuts(
    edit_pack: dict[str, Any],
    decision_packet: dict[str, Any],
    cut_ids: list[str],
) -> list[dict[str, Any]]:
    selected_ids = _string_list(edit_pack.get("selected_cut_ids"))
    candidates = {
        str(item.get("id")): item
        for item in edit_pack.get("cut_candidates", [])
        if isinstance(item, dict) and item.get("id")
    }
    decisions = {
        str(item.get("cut_id")): item
        for item in decision_packet.get("decisions", [])
        if isinstance(item, dict) and item.get("cut_id")
    }
    ordered: list[dict[str, Any]] = []
    for cut_id in cut_ids:
        if cut_id not in selected_ids:
            raise EditorialSequenceError(f"cut is not selected in edit_pack: {cut_id}")
        cut = candidates.get(cut_id)
        if cut is None:
            raise EditorialSequenceError(f"selected cut is missing from cut_candidates: {cut_id}")
        decision = decisions.get(cut_id)
        if decision is None:
            raise EditorialSequenceError(f"final cut decision is missing: {cut_id}")
        final_decision = str(decision.get("final_cut_decision") or "")
        if final_decision not in {"keep", "accepted"}:
            raise EditorialSequenceError(
                f"cut decision must be keep/accepted: {cut_id}={final_decision or 'missing'}"
            )
        cut_context = str((cut.get("context_check") or {}).get("status") or "")
        decision_context = str(decision.get("context_status") or "")
        if cut_context != "passed" or decision_context != "passed":
            raise EditorialSequenceError(
                f"cut context must be passed in edit pack and decision packet: {cut_id}"
            )
        start = _number(cut.get("start_seconds"), f"{cut_id} start_seconds")
        end = _number(cut.get("end_seconds"), f"{cut_id} end_seconds")
        if end <= start:
            raise EditorialSequenceError(f"cut has non-positive duration: {cut_id}")
        duration = round(end - start, 3)
        recorded_duration = decision.get("duration_seconds")
        if (
            recorded_duration is not None
            and abs(_number(recorded_duration, "decision duration") - duration)
            > LINKAGE_TOLERANCE_SECONDS
        ):
            raise EditorialSequenceError(f"duration mismatch between edit pack and decision: {cut_id}")
        source_segment_ids = _string_list(cut.get("source_segment_ids"))
        if not source_segment_ids:
            raise EditorialSequenceError(f"source segment linkage is missing: {cut_id}")
        ordered.append(
            {
                "id": cut_id,
                "source_start_seconds": start,
                "source_end_seconds": end,
                "duration_seconds": duration,
                "source_segment_ids": source_segment_ids,
                "context_status": "passed",
                "final_cut_decision": final_decision,
                "decision_reason": str(decision.get("decision_reason") or ""),
            }
        )
    return ordered


def _real_transcript(
    transcript: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    engine = str(stt.get("engine") or "")
    provider = str(stt.get("provider") or "")
    if stt.get("real_transcript") is not True:
        raise EditorialSequenceError("transcript must declare real_transcript=true")
    if (engine, provider) not in REAL_TRANSCRIPT_SOURCES:
        raise EditorialSequenceError(
            f"transcript engine/provider is not an allowed real source: {engine}/{provider}"
        )
    segments = {
        str(item.get("id")): item
        for item in transcript.get("segments", [])
        if isinstance(item, dict) and item.get("id")
    }
    if not segments:
        raise EditorialSequenceError("transcript segments are missing")
    return (
        {
            "engine": engine,
            "provider": provider,
            "real_transcript": True,
            "review_status": str((transcript.get("review") or {}).get("status") or "unknown"),
        },
        segments,
    )


def _sequence_timeline(
    *,
    edit_pack: dict[str, Any],
    selected_cuts: list[dict[str, Any]],
    transcript_segments: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    subtitle_candidates = [
        item for item in edit_pack.get("subtitles", []) if isinstance(item, dict)
    ]
    timeline: list[dict[str, Any]] = []
    subtitle_rows: list[dict[str, Any]] = []
    offset = 0.0
    for index, cut in enumerate(selected_cuts):
        cut_id = cut["id"]
        for segment_id in cut["source_segment_ids"]:
            segment = transcript_segments.get(segment_id)
            if segment is None:
                raise EditorialSequenceError(
                    f"source segment is missing from transcript: {cut_id}/{segment_id}"
                )
            if not str(segment.get("text") or "").strip():
                raise EditorialSequenceError(f"source segment text is empty: {cut_id}/{segment_id}")
            segment_start = _number(segment.get("start_seconds"), f"{segment_id} start")
            segment_end = _number(segment.get("end_seconds"), f"{segment_id} end")
            if (
                segment_start < cut["source_start_seconds"] - LINKAGE_TOLERANCE_SECONDS
                or segment_end > cut["source_end_seconds"] + LINKAGE_TOLERANCE_SECONDS
                or segment_end <= segment_start
            ):
                raise EditorialSequenceError(
                    f"source segment timing is outside its cut: {cut_id}/{segment_id}"
                )
        sequence_start = round(offset, 3)
        sequence_end = round(sequence_start + cut["duration_seconds"], 3)
        per_cut_subtitles: list[dict[str, Any]] = []
        for subtitle in subtitle_candidates:
            if str(subtitle.get("cut_id") or "") != cut_id:
                continue
            subtitle_id = str(subtitle.get("id") or "")
            _safe_identifier(subtitle_id, "subtitle id")
            source_type = str(subtitle.get("source_type") or "")
            if source_type not in REAL_SUBTITLE_SOURCE_TYPES:
                raise EditorialSequenceError(
                    f"subtitle source_type is not allowed for real proof: {subtitle_id}={source_type}"
                )
            text = str(subtitle.get("text") or "").strip()
            if not text:
                raise EditorialSequenceError(f"subtitle text is empty: {subtitle_id}")
            source_start = _number(subtitle.get("start_seconds"), f"{subtitle_id} start")
            source_end = _number(subtitle.get("end_seconds"), f"{subtitle_id} end")
            if source_end <= source_start:
                raise EditorialSequenceError(f"subtitle has non-positive duration: {subtitle_id}")
            if (
                source_start < cut["source_start_seconds"] - LINKAGE_TOLERANCE_SECONDS
                or source_end > cut["source_end_seconds"] + LINKAGE_TOLERANCE_SECONDS
            ):
                raise EditorialSequenceError(f"subtitle is outside its owning cut: {subtitle_id}")
            linked_segments = _string_list(
                subtitle.get("source_segment_ids")
                or ([subtitle.get("source_segment_id")] if subtitle.get("source_segment_id") else [])
            )
            if not linked_segments:
                raise EditorialSequenceError(f"subtitle segment linkage is missing: {subtitle_id}")
            for segment_id in linked_segments:
                if segment_id not in cut["source_segment_ids"] or segment_id not in transcript_segments:
                    raise EditorialSequenceError(
                        f"subtitle links outside its cut transcript segments: {subtitle_id}/{segment_id}"
                    )
            linked_text = " ".join(
                str(transcript_segments[segment_id].get("text") or "").strip()
                for segment_id in linked_segments
            ).strip()
            if linked_text != text:
                raise EditorialSequenceError(
                    f"subtitle text does not match linked transcript: {subtitle_id}"
                )
            cut_relative_start = round(max(0.0, source_start - cut["source_start_seconds"]), 3)
            cut_relative_end = round(
                min(cut["duration_seconds"], source_end - cut["source_start_seconds"]), 3
            )
            sequence_subtitle_start = round(sequence_start + cut_relative_start, 3)
            sequence_subtitle_end = round(sequence_start + cut_relative_end, 3)
            if (
                sequence_subtitle_start < sequence_start - LINKAGE_TOLERANCE_SECONDS
                or sequence_subtitle_end > sequence_end + LINKAGE_TOLERANCE_SECONDS
            ):
                raise EditorialSequenceError(f"rebased subtitle crosses cut boundary: {subtitle_id}")
            row = {
                "id": subtitle_id,
                "cut_id": cut_id,
                "text": text,
                "source_type": source_type,
                "source_segment_ids": linked_segments,
                "source_start_seconds": source_start,
                "source_end_seconds": source_end,
                "cut_relative_start_seconds": cut_relative_start,
                "cut_relative_end_seconds": cut_relative_end,
                "sequence_start_seconds": sequence_subtitle_start,
                "sequence_end_seconds": sequence_subtitle_end,
            }
            per_cut_subtitles.append(row)
            subtitle_rows.append(row)
        if not per_cut_subtitles:
            raise EditorialSequenceError(f"no usable linked subtitles for cut: {cut_id}")
        role = (
            "setup"
            if index == 0
            else "payoff"
            if index == len(selected_cuts) - 1
            else "bridge"
        )
        timeline.append(
            {
                **cut,
                "sequence_start_seconds": sequence_start,
                "sequence_end_seconds": sequence_end,
                "transition_in": "sequence_start" if index == 0 else "hard_cut",
                "editorial_role": role,
                "subtitle_ids": [item["id"] for item in per_cut_subtitles],
                "subtitle_count": len(per_cut_subtitles),
            }
        )
        offset = sequence_end
    return timeline, subtitle_rows


def _material_readback(
    ledger: dict[str, Any],
    *,
    material_id: str,
    expected_kind: str,
    root: Path,
    episode: Path,
) -> dict[str, Any]:
    material = next(
        (
            item
            for item in ledger.get("materials", [])
            if isinstance(item, dict) and str(item.get("id")) == material_id
        ),
        None,
    )
    if material is None:
        raise EditorialSequenceError(f"material not found: {material_id}")
    if str(material.get("kind") or "") != expected_kind:
        raise EditorialSequenceError(f"material kind mismatch: {material_id}")
    registered_by = str(material.get("registered_by") or "")
    if not registered_by.startswith(REAL_MATERIAL_REGISTRATION_PREFIXES):
        raise EditorialSequenceError(f"material must use a real acquisition route: {material_id}")
    file_path = str(material.get("file_path") or "")
    if not file_path:
        raise EditorialSequenceError(f"material file_path is missing: {material_id}")
    resolved = _resolved(root, Path(file_path))
    _require_file(resolved, f"material {material_id}")
    _require_within(resolved, episode, f"material {material_id}")
    recorded_hash = str(material.get("hash_sha256") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", recorded_hash):
        raise EditorialSequenceError(f"recorded hash is required: {material_id}")
    actual_hash = _sha256(resolved)
    if actual_hash != recorded_hash:
        raise EditorialSequenceError(f"material hash mismatch: {material_id}")
    return {
        "id": material_id,
        "kind": expected_kind,
        "file_path": _relative(resolved, root),
        "sha256": actual_hash,
        "registered_by": registered_by,
    }


def _validate_source_probe(
    metadata: dict[str, Any],
    *,
    label: str,
    required_stream: str,
    maximum_cut_end: float,
) -> None:
    counts = metadata.get("stream_counts") if isinstance(metadata.get("stream_counts"), dict) else {}
    if int(counts.get(required_stream) or 0) < 1:
        raise EditorialSequenceError(f"{label} is missing required {required_stream} stream")
    duration = metadata.get("duration_seconds")
    if duration is None:
        raise EditorialSequenceError(f"{label} duration is missing")
    if float(duration) + LINKAGE_TOLERANCE_SECONDS < maximum_cut_end:
        raise EditorialSequenceError(
            f"{label} does not contain the selected media window: {maximum_cut_end:.3f}s"
        )


def _validate_output_probe(metadata: dict[str, Any], *, expected_duration: float) -> None:
    counts = metadata.get("stream_counts") if isinstance(metadata.get("stream_counts"), dict) else {}
    if int(counts.get("video") or 0) < 1 or int(counts.get("audio") or 0) < 1:
        raise EditorialSequenceError("rendered sequence must contain video and audio streams")
    if str(metadata.get("video_codec") or "").lower() != "h264":
        raise EditorialSequenceError("rendered sequence video codec must be H.264")
    if str(metadata.get("audio_codec") or "").lower() != "aac":
        raise EditorialSequenceError("rendered sequence audio codec must be AAC")
    if not metadata.get("resolution") or metadata.get("fps") is None:
        raise EditorialSequenceError("rendered sequence resolution/frame rate is missing")
    duration = metadata.get("duration_seconds")
    if duration is None or abs(float(duration) - expected_duration) > OUTPUT_DURATION_TOLERANCE_SECONDS:
        raise EditorialSequenceError(
            f"rendered sequence duration mismatch: expected {expected_duration:.3f}s, got {duration}"
        )


def _render_command(
    *,
    ffmpeg_path: str,
    source_video_path: Path,
    source_audio_path: Path,
    output_path: Path,
    srt_path: Path,
    timeline: list[dict[str, Any]],
    video_codec: str,
) -> list[str]:
    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, cut in enumerate(timeline):
        start = _seconds(cut["source_start_seconds"])
        end = _seconds(cut["source_end_seconds"])
        filters.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{index}]")
        filters.append(f"[1:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{index}]")
        concat_inputs.extend([f"[v{index}]", f"[a{index}]"])
    filters.append(
        f"{''.join(concat_inputs)}concat=n={len(timeline)}:v=1:a=1[vseq][aseq]"
    )
    escaped_srt = _escape_filter_path(srt_path)
    filters.append(
        "[vseq]scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p,"
        f"subtitles=filename='{escaped_srt}':charenc=UTF-8[vout]"
    )
    return [
        ffmpeg_path,
        "-hide_banner",
        "-y",
        "-i",
        str(source_video_path),
        "-i",
        str(source_audio_path),
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[vout]",
        "-map",
        "[aseq]",
        "-c:v",
        video_codec,
        *( ["-preset", "medium", "-crf", "18"] if video_codec == "libx264" else ["-b:v", "6M"] ),
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        "-shortest",
        str(output_path),
    ]


def _render_srt(subtitles: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, subtitle in enumerate(subtitles, start=1):
        text = str(subtitle["text"]).replace("\r", " ").replace("\n", " ")
        blocks.append(
            f"{index}\n{_srt_time(subtitle['sequence_start_seconds'])} --> "
            f"{_srt_time(subtitle['sequence_end_seconds'])}\n{text}\n"
        )
    return "\n".join(blocks)


def _render_html(readback: dict[str, Any]) -> str:
    timeline = readback["timeline"]
    total = float(readback["expected_duration_seconds"])
    timeline_parts = "".join(
        (
            f'<div class="cut" style="width:{(float(item["duration_seconds"]) / total) * 100:.4f}%">'
            f'<strong>{escape(item["id"])}</strong><span>{item["sequence_start_seconds"]:.3f}–{item["sequence_end_seconds"]:.3f}s</span></div>'
        )
        for item in timeline
    )
    cut_rows = "".join(
        (
            "<tr>"
            f"<td><code>{escape(item['id'])}</code></td>"
            f"<td>{item['source_start_seconds']:.3f}–{item['source_end_seconds']:.3f}s</td>"
            f"<td>{item['sequence_start_seconds']:.3f}–{item['sequence_end_seconds']:.3f}s</td>"
            f"<td>{escape(item['transition_in'])}</td>"
            f"<td>{item['subtitle_count']}</td>"
            "</tr>"
        )
        for item in timeline
    )
    subtitle_sections = "".join(
        (
            f"<section><h3><code>{escape(item['id'])}</code> の字幕</h3><ol>"
            + "".join(
                (
                    f"<li><time>{sub['sequence_start_seconds']:.3f}–{sub['sequence_end_seconds']:.3f}s</time> "
                    f"{escape(sub['text'])} <small><code>{escape(sub['id'])}</code></small></li>"
                )
                for sub in readback["subtitles"]
                if sub["cut_id"] == item["id"]
            )
            + "</ol></section>"
        )
        for item in timeline
    )
    questions = "".join(f"<li>{escape(question)}</li>" for question in readback["review_questions"])
    material_video = readback["materials"]["source_video"]
    material_audio = readback["materials"]["source_audio"]
    boundaries = readback["boundaries"]
    media = readback["render"]["media"]
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-04 編集シーケンスレビュー</title>
<style>
:root {{ color-scheme: dark; font-family: "Yu Gothic UI", "Noto Sans JP", sans-serif; background:#0b1020; color:#edf3ff; }}
* {{ box-sizing:border-box; }} body {{ margin:0; }} main {{ width:min(1120px,100%); margin:auto; padding:24px; overflow-wrap:anywhere; }}
.eyebrow {{ color:#7dd3fc; font-weight:800; letter-spacing:.12em; }} h1 {{ margin:.35rem 0 .5rem; font-size:clamp(1.65rem,4vw,2.6rem); }}
.lead {{ color:#cbd5e1; max-width:75ch; }} video {{ display:block; width:100%; max-height:70vh; margin:20px 0; background:#000; border:1px solid #334155; border-radius:12px; }}
.timeline {{ display:flex; width:100%; min-height:62px; border:1px solid #475569; border-radius:10px; overflow:hidden; }}
.cut {{ min-width:0; display:flex; flex-direction:column; justify-content:center; gap:4px; padding:9px; background:#164e63; border-right:2px solid #e2e8f0; }} .cut:last-child {{ border-right:0; background:#1e3a8a; }} .cut span {{ font-size:.78rem; color:#dbeafe; }}
table {{ width:100%; border-collapse:collapse; margin:18px 0; }} th,td {{ padding:9px; border-bottom:1px solid #334155; text-align:left; }}
section,details,.questions {{ margin-top:20px; padding:16px; border:1px solid #334155; border-radius:10px; background:#111827; }}
time {{ color:#7dd3fc; font-variant-numeric:tabular-nums; }} code {{ color:#bae6fd; }} small {{ color:#94a3b8; }} li {{ margin:.55rem 0; }} summary {{ cursor:pointer; font-weight:700; }}
@media (max-width:700px) {{ main {{ padding:14px; }} th:nth-child(2),td:nth-child(2) {{ display:none; }} .cut {{ padding:6px; }} }}
</style></head><body><main>
<div class="eyebrow">OUT-04 · REAL LOCAL EDITORIAL REVIEW</div>
<h1>{len(timeline)}カットを一本で見る編集シーケンス</h1>
<p class="lead">一つの動画として再生し、並び・境界・字幕と音声の連続性だけを確認します。権利、production、公開・投稿の判断面ではありません。</p>
<video controls preload="metadata" playsinline src="assets/editorial_sequence.mp4"></video>
<h2>カット境界</h2><div class="timeline">{timeline_parts}</div>
<table><thead><tr><th>順序</th><th>元範囲</th><th>シーケンス範囲</th><th>接続</th><th>字幕</th></tr></thead><tbody>{cut_rows}</tbody></table>
<div class="questions"><h2>今回の確認</h2><ol>{questions}</ol></div>
<h2>カット別字幕</h2>{subtitle_sections}
<details><summary>出典・probe・閉じた gate</summary>
<p>Video: <code>{escape(material_video['id'])}</code> · SHA-256 <code>{escape(material_video['sha256'])}</code></p>
<p>Audio: <code>{escape(material_audio['id'])}</code> · SHA-256 <code>{escape(material_audio['sha256'])}</code></p>
<p>Output: {media['duration_seconds']:.3f}s · {escape(str(media['video_codec']))}/{escape(str(media['audio_codec']))} · {escape(str(media['resolution']))} · {escape(str(media['fps']))}fps</p>
<p>Rights: <code>{escape(str(boundaries['rights_status']))}</code>; production_acceptance=false; public_ready=false; publishing_acceptance=false.</p>
</details></main></body></html>
"""


def _open_script() -> str:
    return """param([switch]$Serve, [int]$Port = 8000)
$ErrorActionPreference = 'Stop'
if ($Serve) {
    & (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
    exit $LASTEXITCODE
}
$index = Join-Path $PSScriptRoot 'index.html'
Write-Host "OUT-04 review entrypoint: $index"
Start-Process -FilePath $index
Write-Host "If local-file playback is blocked, rerun this command with -Serve."
"""


def _serve_script() -> str:
    return """param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
Write-Host "OUT-04 review URL: $url"
Start-Process -FilePath $url
Push-Location $PSScriptRoot
try {
    uvx python -m http.server $Port --bind 127.0.0.1
} finally {
    Pop-Location
}
"""


def _validate_cut_ids(cut_ids: list[str]) -> None:
    if not MIN_CUT_COUNT <= len(cut_ids) <= MAX_CUT_COUNT:
        raise EditorialSequenceError("explicit ordered cut list must contain two or three cut IDs")
    if len(set(cut_ids)) != len(cut_ids):
        raise EditorialSequenceError("ordered cut IDs must be unique")
    for cut_id in cut_ids:
        _safe_identifier(cut_id, "cut id")


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if output.parent != review or not output.name.startswith("out04_"):
        raise EditorialSequenceError("output must be a direct dedicated episode/review/out04_* directory")
    _safe_identifier(output.name, "output directory name")
    if "human_preview_session" in {part.lower() for part in output.parts}:
        raise EditorialSequenceError("output must not overlap human_preview_session")


def _reject_overlap(output: Path, input_path: Path, message: str) -> None:
    output_resolved = output.resolve()
    input_resolved = input_path.resolve()
    if (
        output_resolved == input_resolved
        or output_resolved in input_resolved.parents
        or input_resolved in output_resolved.parents
    ):
        raise EditorialSequenceError(message)


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EditorialSequenceError(f"failed to read JSON {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise EditorialSequenceError(f"JSON root must be an object: {path.name}")
    return value


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise EditorialSequenceError(f"{label} not found: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise EditorialSequenceError(f"{label} not found: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise EditorialSequenceError(f"{label} escapes allowed root: {path}") from exc


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise EditorialSequenceError(f"path escapes repository root: {path}") from exc


def _powershell_command(path: Path, root: Path) -> str:
    relative = _relative(path, root).replace("/", "\\")
    return f"powershell -ExecutionPolicy Bypass -File {relative}"


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise EditorialSequenceError(f"{label} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise EditorialSequenceError(f"{label} must be numeric") from exc


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item]


def _safe_identifier(value: str, label: str) -> None:
    if not value or SAFE_IDENTIFIER.fullmatch(value) is None:
        raise EditorialSequenceError(f"{label} contains unsafe path characters: {value!r}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def _escape_filter_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def _seconds(value: float) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".")


def _srt_time(value: float) -> str:
    milliseconds = max(0, int(round(float(value) * 1000)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
