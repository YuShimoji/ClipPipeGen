"""OUT-09 second-source vertical Short repeatability builder.

The implementation is intentionally source-neutral.  A declarative ignored
plan identifies inputs, allowed/excluded source ranges, and transcript-backed
display subtitles.  The builder verifies those authorities before invoking
the shared OUT-05 vertical render path exactly once.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
import uuid
from html import escape
from pathlib import Path
from typing import Any, Callable

from src.integrations.render import ffmpeg_tiny
from src.integrations.render.complete_narrative_short import (
    _canonical_manifest_self_hash,
)
from src.integrations.render.editorial_sequence import (
    EditorialSequenceError,
    _material_readback,
)
from src.integrations.render.real_unused_range_short_minibatch import (
    _extract_navigation_frame,
)
from src.integrations.render.subtitle_overlay_visual_proof import _write_ass
from src.integrations.render.vertical_short_candidate import (
    VerticalShortCandidateError,
    _atomic_promote,
    _cleanup_internal_directory,
    _relative,
    _sha256,
    _write_text,
    build_vertical_subtitle_presentation,
    render_vertical_sequence_assets,
    validate_ass_visible_content,
    validate_vertical_render_result,
    validate_vertical_subtitle_containment,
)


ARTIFACT_ID = "clip-out09-second-source-short-repeatability-v0-001"
SCHEMA_VERSION = "clippipegen.out09.second_source_short_repeatability.v0"
PLAN_SCHEMA_VERSION = "clippipegen.out09.candidate_plan_input.v0"
STATE = "OUT09_SECOND_SOURCE_SHORT_REPEATABILITY_REVIEW_READY"
OUTPUT_PREFIX = "out09_"
OUT08_PROVIDER_ID = "7J5aS_pcBj4"
MIN_DURATION_SECONDS = 12.0
MAX_DURATION_SECONDS = 60.0
TIME_TOLERANCE_SECONDS = 0.002
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
REQUIRED_INPUT_ROLES = {
    "rights_manifest",
    "material_ledger",
    "base_vosk_transcript",
    "source_caption_track",
    "authoritative_transcript",
    "edit_pack",
}

RenderExecutor = Callable[..., dict[str, Any]]
NavigationExecutor = Callable[..., dict[str, Any]]
SignalQaExecutor = Callable[..., dict[str, Any]]


class SecondSourceShortRepeatabilityError(VerticalShortCandidateError):
    """Raised when OUT-09 authority or output validation fails."""


def build_second_source_short_repeatability(
    *,
    episode_dir: Path,
    output_dir: Path,
    candidate_plan_input_path: Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
    render_executor: RenderExecutor = render_vertical_sequence_assets,
    navigation_executor: NavigationExecutor = _extract_navigation_frame,
    signal_qa_executor: SignalQaExecutor | None = None,
) -> dict[str, Any]:
    """Build one hash-bound 1080x1920 second-source review candidate."""

    started = time.monotonic()
    root = (base_dir or Path.cwd()).resolve()
    episode = _resolved(root, episode_dir)
    output = _resolved(root, output_dir)
    plan_path = _resolved(root, candidate_plan_input_path)
    _require_directory(episode, "episode directory")
    _require_file(plan_path, "candidate plan input")
    _require_within(plan_path, episode, "candidate plan input")
    _validate_output_directory(episode, output)

    plan = _read_json(plan_path, "candidate plan input")
    authority = _load_authority(root=root, episode=episode, plan=plan)
    normalized = _normalize_plan(plan=plan, authority=authority)

    review_dir = output.parent
    review_dir.mkdir(parents=True, exist_ok=True)
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    stage.mkdir()
    work = stage / ".work"
    work.mkdir()
    backup: Path | None = None
    try:
        plan_snapshot = stage / "candidate_plan.json"
        _write_json(plan_snapshot, plan)

        ass_path = stage / "candidate_01_subtitles.ass"
        srt_path = stage / "candidate_01_subtitles.srt"
        video_path = stage / "candidate_01.mp4"
        frame_path = stage / "candidate_01_frame_qa.jpg"
        navigation_path = stage / "candidate_01_navigation.jpg"

        layout, presentation, selector = build_vertical_subtitle_presentation(
            normalized["semantic_subtitles"],
            application_key="out09_application",
            dimension_source="out09_second_source_vertical_canvas",
        )
        containment = validate_vertical_subtitle_containment(
            presentation,
            expected_duration=normalized["duration_seconds"],
            layout=layout,
            expected_count=len(presentation),
        )
        _write_ass(ass_path, presentation, layout=layout, review_label=None)
        _write_text(srt_path, _render_srt(presentation))
        validate_ass_visible_content(
            ass_path,
            expected_count=len(presentation),
            required_texts=(
                str(presentation[0]["text"]),
                str(presentation[-1]["text"]),
            ),
        )

        render_result = render_executor(
            source_video_path=authority["source_video_path"],
            source_audio_path=authority["source_audio_path"],
            timeline=normalized["timeline"],
            ass_path=ass_path,
            video_path=video_path,
            compare_sheet_path=None,
            frame_sheet_path=frame_path,
            work_dir=work,
            subtitle_layout=layout,
            expected_duration=normalized["duration_seconds"],
            frame_samples=normalized["frame_samples"],
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        validate_vertical_render_result(
            render_result,
            video_path=video_path,
            expected_duration=normalized["duration_seconds"],
        )
        _require_file(frame_path, "frame QA contact sheet")

        navigation_seconds = round(normalized["duration_seconds"] * 0.62, 3)
        navigation = navigation_executor(
            video_path=video_path,
            output_path=navigation_path,
            seconds=navigation_seconds,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        _require_file(navigation_path, "representative navigation frame")

        signal_qa = (signal_qa_executor or _run_signal_qa)(
            video_path=video_path,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        if signal_qa.get("status") != "passed":
            raise SecondSourceShortRepeatabilityError(
                "black/silence QA did not pass"
            )

        _cleanup_internal_directory(work, expected_parent=stage)
        presentation_items = [
            {
                "subtitle_id": str(item["subtitle_id"]),
                "display_start_seconds": float(item["display_start_seconds"]),
                "display_end_seconds": float(item["display_end_seconds"]),
                "text": str(item["text"]),
                "source_text": str(item.get("source_text") or item["text"]),
                "source_segment_ids": list(item.get("source_segment_ids") or []),
                "wrapped_lines": list(item.get("wrapped_lines") or []),
                "display_text_normalization": str(
                    item.get("display_text_normalization") or "none"
                ),
            }
            for item in presentation
        ]
        elapsed = round(time.monotonic() - started, 3)
        readback = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": ARTIFACT_ID,
            "state": STATE,
            "episode_id": episode.name,
            "source_identity": normalized["source_identity"],
            "source_difference": {
                "out08_provider_id": OUT08_PROVIDER_ID,
                "out09_provider_id": normalized["source_identity"]["provider_id"],
                "different": True,
            },
            "input_integrity": authority["input_integrity"],
            "materials": authority["materials"],
            "transcript_authority": normalized["transcript_authority"],
            "selection_authority": normalized["selection_authority"],
            "candidate": {
                "candidate_id": normalized["candidate_id"],
                "source_start_seconds": normalized["source_start_seconds"],
                "source_end_seconds": normalized["source_end_seconds"],
                "duration_seconds": normalized["duration_seconds"],
                "authority_cut_ids": normalized["authority_cut_ids"],
                "source_segment_ids": normalized["source_segment_ids"],
                "rationale": normalized["rationale"],
                "narrative_arc": normalized["narrative_arc"],
            },
            "subtitle": {
                "count": len(presentation_items),
                "ass_path": ass_path.name,
                "srt_path": srt_path.name,
                "containment": containment,
                "selector": selector,
                "items": presentation_items,
                "source_type": "imported_subtitle_track",
                "human_transcript_acceptance_claimed": False,
            },
            "video": {
                "package_relative_path": video_path.name,
                "sha256": _sha256(video_path),
            },
            "render": {
                "media": render_result["media"],
                "selected_video_encoder": render_result["selected_video_encoder"],
                "attempts": render_result["attempts"],
                "full_decode": render_result["full_decode"],
                "faststart": render_result.get("faststart"),
                "source_probe": render_result.get("source_probe"),
                "execution_count": 1,
                "corrective_pass_count": 0,
                "build_elapsed_seconds": elapsed,
            },
            "audio": render_result["audio"],
            "signal_qa": signal_qa,
            "frame_qa": {
                "package_relative_path": frame_path.name,
                "sha256": _sha256(frame_path),
                "samples": render_result["frame_samples"],
            },
            "navigation_frame": {
                "package_relative_path": navigation_path.name,
                "sha256": _sha256(navigation_path),
                "seconds": navigation_seconds,
                "role": "representative_navigation_only",
                "thumbnail_acceptance_claimed": False,
                "extraction": navigation,
            },
            "review_questions": list(plan["review_questions"]),
            "review_entrypoint": _relative(output / "index.html", root),
            "open_command": _powershell_command(output / "open_preview.ps1", root),
            "machine_readback": _relative(output / "candidate_readback.json", root),
            "candidate_manifest": _relative(output / "candidate_manifest.json", root),
            "candidate_plan": _relative(output / "candidate_plan.json", root),
            "boundaries": normalized["boundaries"],
            "regeneration_command": (
                "uvx python -m src.cli.main build-second-source-short-repeatability "
                f"--episode-dir {_relative(episode, root)} "
                f"--output-dir {_relative(output, root)} "
                f"--candidate-plan-input {_relative(plan_path, root)}"
            ),
        }
        _write_json(stage / "candidate_readback.json", readback)
        _write_text(stage / "index.html", _render_html(readback))
        _write_text(stage / "open_preview.ps1", _open_script())
        _write_text(stage / "serve_preview.ps1", _serve_script())

        files = []
        for file_path in sorted(path for path in stage.iterdir() if path.is_file()):
            files.append(
                {
                    "package_relative_path": file_path.name,
                    "sha256": _sha256(file_path),
                    "byte_size": file_path.stat().st_size,
                }
            )
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": ARTIFACT_ID,
            "state": STATE,
            "episode_id": episode.name,
            "source_identity": normalized["source_identity"],
            "candidate_video_sha256": readback["video"]["sha256"],
            "plan_input_sha256": _sha256(plan_path),
            "input_integrity": authority["input_integrity"],
            "files": files,
            "boundaries": normalized["boundaries"],
            "manifest_self_integrity": {"algorithm": "sha256", "sha256": None},
        }
        manifest["manifest_self_integrity"]["sha256"] = (
            _canonical_manifest_self_hash(manifest)
        )
        _write_json(stage / "candidate_manifest.json", manifest)
        _validate_staged_bundle(stage=stage, readback=readback, manifest=manifest)

        backup = _atomic_promote(stage, output)
        if backup is not None:
            _cleanup_internal_directory(backup, expected_parent=review_dir)
        return {
            "artifact_id": ARTIFACT_ID,
            "output_dir": output,
            "readback": readback,
            "manifest": manifest,
        }
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise


def _load_authority(*, root: Path, episode: Path, plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise SecondSourceShortRepeatabilityError("unsupported candidate plan schema")
    if plan.get("artifact_id") != ARTIFACT_ID:
        raise SecondSourceShortRepeatabilityError("candidate plan artifact_id mismatch")
    if plan.get("episode_id") != episode.name:
        raise SecondSourceShortRepeatabilityError("candidate plan episode_id mismatch")

    input_rows = plan.get("expected_inputs")
    if not isinstance(input_rows, list):
        raise SecondSourceShortRepeatabilityError("expected_inputs are missing")
    integrity: list[dict[str, Any]] = []
    paths: dict[str, Path] = {}
    for row in input_rows:
        if not isinstance(row, dict):
            raise SecondSourceShortRepeatabilityError("invalid expected input row")
        role = str(row.get("role") or "")
        if role in paths or role not in REQUIRED_INPUT_ROLES:
            raise SecondSourceShortRepeatabilityError(f"unexpected input role: {role}")
        path = _resolved(root, Path(str(row.get("path") or "")))
        _require_file(path, f"input {role}")
        _require_within(path, episode, f"input {role}")
        expected_hash = str(row.get("sha256") or "").lower()
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise SecondSourceShortRepeatabilityError(f"input hash mismatch: {role}")
        paths[role] = path
        integrity.append(
            {
                "role": role,
                "path": _relative(path, root),
                "sha256": actual_hash,
                "verified": True,
            }
        )
    if set(paths) != REQUIRED_INPUT_ROLES:
        missing = sorted(REQUIRED_INPUT_ROLES - set(paths))
        raise SecondSourceShortRepeatabilityError(
            f"required input roles are missing: {', '.join(missing)}"
        )

    rights = _read_json(paths["rights_manifest"], "rights manifest")
    if str((rights.get("compliance_check") or {}).get("status") or "") != "pending":
        raise SecondSourceShortRepeatabilityError("OUT-09 requires rights=pending")
    ledger = _read_json(paths["material_ledger"], "material ledger")
    materials = plan.get("materials") if isinstance(plan.get("materials"), dict) else {}
    try:
        video = _material_readback(
            ledger,
            material_id=str((materials.get("source_video") or {}).get("material_id") or ""),
            expected_kind="source_video",
            root=root,
            episode=episode,
        )
        audio = _material_readback(
            ledger,
            material_id=str((materials.get("source_audio") or {}).get("material_id") or ""),
            expected_kind="source_audio",
            root=root,
            episode=episode,
        )
    except EditorialSequenceError as exc:
        raise SecondSourceShortRepeatabilityError(str(exc)) from exc
    if video["sha256"] != str((materials.get("source_video") or {}).get("sha256") or ""):
        raise SecondSourceShortRepeatabilityError("source video plan hash mismatch")
    if audio["sha256"] != str((materials.get("source_audio") or {}).get("sha256") or ""):
        raise SecondSourceShortRepeatabilityError("source audio plan hash mismatch")

    transcript = _read_json(paths["authoritative_transcript"], "authoritative transcript")
    edit_pack = _read_json(paths["edit_pack"], "edit pack")
    return {
        "rights": rights,
        "transcript": transcript,
        "edit_pack": edit_pack,
        "source_video_path": _resolved(root, Path(video["file_path"])),
        "source_audio_path": _resolved(root, Path(audio["file_path"])),
        "materials": {"source_video": video, "source_audio": audio},
        "input_integrity": integrity,
    }


def _normalize_plan(*, plan: dict[str, Any], authority: dict[str, Any]) -> dict[str, Any]:
    identity = plan.get("source_identity") if isinstance(plan.get("source_identity"), dict) else {}
    provider_id = str(identity.get("provider_id") or "")
    if not provider_id or provider_id == OUT08_PROVIDER_ID:
        raise SecondSourceShortRepeatabilityError(
            "OUT-09 source identity must differ from OUT-08"
        )
    rights_source = authority["rights"].get("source_video") or {}
    if provider_id not in str(rights_source.get("url") or ""):
        raise SecondSourceShortRepeatabilityError("rights/source identity mismatch")
    if str(rights_source.get("title") or "") != str(identity.get("title") or ""):
        raise SecondSourceShortRepeatabilityError("rights/source title mismatch")

    transcript = authority["transcript"]
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    transcript_plan = plan.get("transcript_authority") or {}
    if (
        stt.get("real_transcript") is not True
        or str(stt.get("engine") or "") != str(transcript_plan.get("engine") or "")
        or str(stt.get("provider") or "") != str(transcript_plan.get("provider") or "")
    ):
        raise SecondSourceShortRepeatabilityError("real transcript authority mismatch")
    segments = {
        str(item.get("id")): item
        for item in transcript.get("segments", [])
        if isinstance(item, dict) and item.get("id")
    }
    if not segments:
        raise SecondSourceShortRepeatabilityError("transcript segments are missing")

    cuts = {
        str(item.get("id")): item
        for item in authority["edit_pack"].get("cut_candidates", [])
        if isinstance(item, dict) and item.get("id")
    }
    candidate = plan.get("candidate") if isinstance(plan.get("candidate"), dict) else {}
    candidate_id = str(candidate.get("candidate_id") or "")
    _safe_identifier(candidate_id, "candidate_id")
    start = _number(candidate.get("source_start_seconds"), "candidate source start")
    end = _number(candidate.get("source_end_seconds"), "candidate source end")
    duration = round(end - start, 3)
    if duration < MIN_DURATION_SECONDS or duration > MAX_DURATION_SECONDS:
        raise SecondSourceShortRepeatabilityError("candidate duration must be 12-60 seconds")
    if abs(duration - _number(candidate.get("duration_seconds"), "candidate duration")) > TIME_TOLERANCE_SECONDS:
        raise SecondSourceShortRepeatabilityError("candidate duration readback mismatch")

    cut_ids = _string_list(candidate.get("authority_cut_ids"))
    if not cut_ids:
        raise SecondSourceShortRepeatabilityError("candidate authority_cut_ids are missing")
    for cut_id in cut_ids:
        cut = cuts.get(cut_id)
        if cut is None or str((cut.get("context_check") or {}).get("status") or "") != "passed":
            raise SecondSourceShortRepeatabilityError(
                f"candidate cut authority is not context-passed: {cut_id}"
            )
    envelope_start = min(float(cuts[value]["start_seconds"]) for value in cut_ids)
    envelope_end = max(float(cuts[value]["end_seconds"]) for value in cut_ids)
    if start < envelope_start - TIME_TOLERANCE_SECONDS or end > envelope_end + TIME_TOLERANCE_SECONDS:
        raise SecondSourceShortRepeatabilityError("candidate leaves cut authority envelope")

    selection = plan.get("selection_authority") if isinstance(plan.get("selection_authority"), dict) else {}
    allowed = selection.get("allowed_ranges") if isinstance(selection.get("allowed_ranges"), list) else []
    excluded = selection.get("excluded_ranges") if isinstance(selection.get("excluded_ranges"), list) else []
    if len(allowed) != 1 or not excluded:
        raise SecondSourceShortRepeatabilityError("allowed/excluded range authority is incomplete")
    allowed_start = _number(allowed[0].get("source_start_seconds"), "allowed range start")
    allowed_end = _number(allowed[0].get("source_end_seconds"), "allowed range end")
    if not _close(start, allowed_start) or not _close(end, allowed_end):
        raise SecondSourceShortRepeatabilityError("candidate must match its allowed range")
    excluded_readback = []
    for item in excluded:
        excluded_start = _number(item.get("source_start_seconds"), "excluded range start")
        excluded_end = _number(item.get("source_end_seconds"), "excluded range end")
        if _overlap(start, end, excluded_start, excluded_end):
            raise SecondSourceShortRepeatabilityError(
                f"candidate overlaps rejected/unselected authority: {item.get('id')}"
            )
        excluded_readback.append(
            {
                "id": str(item.get("id") or ""),
                "source_start_seconds": excluded_start,
                "source_end_seconds": excluded_end,
                "reason": str(item.get("reason") or ""),
                "overlap_rejected_before_render": True,
            }
        )

    source_segment_ids = _string_list(candidate.get("source_segment_ids"))
    if not source_segment_ids or any(value not in segments for value in source_segment_ids):
        raise SecondSourceShortRepeatabilityError("candidate transcript linkage is incomplete")
    subtitles = candidate.get("subtitles") if isinstance(candidate.get("subtitles"), list) else []
    if not subtitles:
        raise SecondSourceShortRepeatabilityError("candidate subtitles are missing")
    semantic: list[dict[str, Any]] = []
    previous_end = 0.0
    for index, raw in enumerate(subtitles, start=1):
        if not isinstance(raw, dict):
            raise SecondSourceShortRepeatabilityError("invalid subtitle plan row")
        subtitle_id = str(raw.get("id") or "")
        _safe_identifier(subtitle_id, "subtitle id")
        source_start = _number(raw.get("source_start_seconds"), "subtitle source start")
        source_end = _number(raw.get("source_end_seconds"), "subtitle source end")
        if source_start < start - TIME_TOLERANCE_SECONDS or source_end > end + TIME_TOLERANCE_SECONDS or source_end <= source_start:
            raise SecondSourceShortRepeatabilityError(f"subtitle leaves candidate range: {subtitle_id}")
        display_start = round(source_start - start, 3)
        display_end = round(source_end - start, 3)
        if index == 1 and not _close(display_start, 0.0):
            raise SecondSourceShortRepeatabilityError("first subtitle must start with candidate")
        if not _close(display_start, previous_end):
            raise SecondSourceShortRepeatabilityError("subtitle plan must be contiguous")
        linked_ids = _string_list(raw.get("source_segment_ids"))
        if not linked_ids or any(value not in segments for value in linked_ids):
            raise SecondSourceShortRepeatabilityError(
                f"subtitle transcript linkage is incomplete: {subtitle_id}"
            )
        source_text = " ".join(str(segments[value].get("text") or "") for value in linked_ids)
        text = str(raw.get("text") or "").strip()
        if not text or not _token_subsequence(text, source_text):
            raise SecondSourceShortRepeatabilityError(
                f"subtitle normalization is not transcript-backed: {subtitle_id}"
            )
        semantic.append(
            {
                "id": subtitle_id,
                "cut_id": "out09_candidate",
                "sequence_start_seconds": display_start,
                "sequence_end_seconds": display_end,
                "text": text,
                "source_text": source_text,
                "display_text_normalization": "rolling_caption_dedup_subsequence_v1",
                "source_type": "imported_subtitle_track",
                "source_segment_ids": linked_ids,
            }
        )
        previous_end = display_end
    if not _close(previous_end, duration):
        raise SecondSourceShortRepeatabilityError("subtitles must end with candidate")

    review_questions = plan.get("review_questions")
    if not isinstance(review_questions, list) or len(review_questions) != 2 or any(not isinstance(value, str) or not value.strip() for value in review_questions):
        raise SecondSourceShortRepeatabilityError("exactly two review questions are required")
    boundaries = plan.get("boundaries") if isinstance(plan.get("boundaries"), dict) else {}
    expected_boundaries = {
        "rights_status": "pending",
        "production_candidate": False,
        "public_use_allowed": False,
        "human_creative_acceptance": False,
        "h1_successor_data_only": True,
    }
    if any(boundaries.get(key) != value for key, value in expected_boundaries.items()):
        raise SecondSourceShortRepeatabilityError("candidate boundaries are not closed")

    authority_boundary = round(float(cuts[cut_ids[-1]]["start_seconds"]) - start, 3)
    frame_samples = (
        ("start", 0.25),
        ("subtitle_dense", round(duration * 0.34, 3)),
        ("authority_boundary", max(0.25, min(duration - 0.25, authority_boundary))),
        ("end", round(duration - 0.25, 3)),
    )
    timeline = [
        {
            "id": "out09_range_001",
            "cut_id": "out09_candidate",
            "source_start_seconds": start,
            "source_end_seconds": end,
            "duration_seconds": duration,
            "sequence_start_seconds": 0.0,
            "sequence_end_seconds": duration,
            "transition_in": "hard_cut",
        }
    ]
    return {
        "source_identity": {
            "platform": str(identity.get("platform") or ""),
            "provider_id": provider_id,
            "url": str(identity.get("url") or ""),
            "title": str(identity.get("title") or ""),
            "channel": str(identity.get("channel") or ""),
        },
        "candidate_id": candidate_id,
        "source_start_seconds": start,
        "source_end_seconds": end,
        "duration_seconds": duration,
        "authority_cut_ids": cut_ids,
        "source_segment_ids": source_segment_ids,
        "rationale": str(candidate.get("rationale") or ""),
        "narrative_arc": dict(candidate.get("narrative_arc") or {}),
        "timeline": timeline,
        "semantic_subtitles": semantic,
        "frame_samples": frame_samples,
        "transcript_authority": {
            "engine": str(stt.get("engine") or ""),
            "provider": str(stt.get("provider") or ""),
            "real_transcript": True,
            "review_status": str((transcript.get("review") or {}).get("status") or "unknown"),
            "segment_count": len(segments),
            "used_source_segment_ids": source_segment_ids,
            "display_normalization": "rolling_caption_dedup_subsequence_v1",
            "human_transcript_acceptance_claimed": False,
        },
        "selection_authority": {
            "allowed_ranges": allowed,
            "excluded_ranges": excluded_readback,
            "candidate_within_allowed_range": True,
            "rejected_or_unselected_overlap_count": 0,
            "checked_before_render": True,
        },
        "boundaries": expected_boundaries,
    }


def _run_signal_qa(
    *,
    video_path: Path,
    ffmpeg_path: str | Path | None,
    ffprobe_path: str | Path | None,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    preflight = ffmpeg_tiny.preflight_tools(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    if preflight.get("status") != "passed":
        raise SecondSourceShortRepeatabilityError("signal QA tool preflight failed")
    ffmpeg = str(preflight["ffmpeg"]["path"])
    black_command = [
        ffmpeg,
        "-hide_banner",
        "-i",
        str(video_path),
        "-vf",
        "blackdetect=d=0.5:pix_th=0.10",
        "-an",
        "-f",
        "null",
        os.devnull,
    ]
    silence_command = [
        ffmpeg,
        "-hide_banner",
        "-i",
        str(video_path),
        "-af",
        "silencedetect=noise=-50dB:d=1.0",
        "-vn",
        "-f",
        "null",
        os.devnull,
    ]
    black_result = runner(
        black_command,
        capture_output=True,
        text=True,
        timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
    )
    silence_result = runner(
        silence_command,
        capture_output=True,
        text=True,
        timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
    )
    if black_result.returncode != 0 or silence_result.returncode != 0:
        raise SecondSourceShortRepeatabilityError("black/silence command failed")
    black_durations = [
        float(value)
        for value in re.findall(r"black_duration:([0-9.]+)", black_result.stderr or "")
    ]
    silence_durations = [
        float(value)
        for value in re.findall(r"silence_duration: ([0-9.]+)", silence_result.stderr or "")
    ]
    max_black = max(black_durations, default=0.0)
    max_silence = max(silence_durations, default=0.0)
    status = "passed" if max_black <= 1.5 and max_silence <= 2.5 else "failed"
    return {
        "status": status,
        "blackdetect": {
            "threshold": "d=0.5:pix_th=0.10",
            "event_count": len(black_durations),
            "durations_seconds": black_durations,
            "maximum_duration_seconds": max_black,
            "maximum_allowed_seconds": 1.5,
            "exit_code": black_result.returncode,
        },
        "silencedetect": {
            "threshold": "noise=-50dB:d=1.0",
            "event_count": len(silence_durations),
            "durations_seconds": silence_durations,
            "maximum_duration_seconds": max_silence,
            "maximum_allowed_seconds": 2.5,
            "exit_code": silence_result.returncode,
        },
    }


def _validate_staged_bundle(
    *, stage: Path, readback: dict[str, Any], manifest: dict[str, Any]
) -> None:
    required = {
        "candidate_01.mp4",
        "candidate_01_subtitles.ass",
        "candidate_01_subtitles.srt",
        "candidate_01_frame_qa.jpg",
        "candidate_01_navigation.jpg",
        "candidate_plan.json",
        "candidate_readback.json",
        "candidate_manifest.json",
        "index.html",
        "open_preview.ps1",
        "serve_preview.ps1",
    }
    for name in required:
        _require_file(stage / name, f"staged {name}")
    if (stage / ".work").exists():
        raise SecondSourceShortRepeatabilityError("internal work directory remained")
    parsed_readback = _read_json(stage / "candidate_readback.json", "staged readback")
    if parsed_readback.get("artifact_id") != readback.get("artifact_id"):
        raise SecondSourceShortRepeatabilityError("staged readback parse mismatch")
    parsed_manifest = _read_json(stage / "candidate_manifest.json", "staged manifest")
    if parsed_manifest.get("manifest_self_integrity", {}).get("sha256") != _canonical_manifest_self_hash(parsed_manifest):
        raise SecondSourceShortRepeatabilityError("manifest self-integrity mismatch")
    for entry in manifest.get("files", []):
        path = stage / str(entry.get("package_relative_path") or "")
        if _sha256(path) != str(entry.get("sha256") or ""):
            raise SecondSourceShortRepeatabilityError(
                f"manifest file hash mismatch: {path.name}"
            )
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count("<video ") != 1 or html.count("data-review-question=") != 2:
        raise SecondSourceShortRepeatabilityError(
            "review page must contain one video and exactly two questions"
        )


def _render_html(readback: dict[str, Any]) -> str:
    candidate = readback["candidate"]
    media = readback["render"]["media"]
    audio = readback["audio"]["output_measurement"]
    questions = "".join(
        f'<li data-review-question="{index}">{escape(question)}</li>'
        for index, question in enumerate(readback["review_questions"], start=1)
    )
    arc = candidate["narrative_arc"]
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-09 second-source Short review</title><style>
:root{{color-scheme:dark;font-family:"Yu Gothic UI","Noto Sans JP",sans-serif;background:#06101d;color:#eff7ff}}*{{box-sizing:border-box}}body{{margin:0;overflow-x:hidden}}main{{width:min(900px,100%);margin:auto;padding:22px;overflow-wrap:anywhere}}section,details{{margin-top:18px;padding:16px;border:1px solid #30445f;border-radius:14px;background:#0d1a2c}}video{{display:block;width:auto;height:min(76vh,820px);max-width:100%;aspect-ratio:9/16;margin:18px auto;background:#000}}code{{color:#9fe7ff}}.boundary{{color:#ffd166}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #30445f;text-align:left}}@media(max-width:620px){{main{{padding:14px}}video{{height:min(72vh,700px)}}}}
</style></head><body><main><h1>OUT-09 second-source Short review</h1>
<p><code>{escape(readback['source_identity']['provider_id'])}</code> / source {candidate['source_start_seconds']:.3f}–{candidate['source_end_seconds']:.3f}s / sequence {candidate['duration_seconds']:.3f}s</p>
<p class="boundary">rights=pending / production_candidate=false / public use is not allowed</p>
<video controls preload="metadata" playsinline poster="{escape(readback['navigation_frame']['package_relative_path'])}" src="{escape(readback['video']['package_relative_path'])}"></video>
<section><h2>確認する2点</h2><ol>{questions}</ol></section>
<details open><summary>構成</summary><table><tr><th>導入</th><td>{escape(str(arc.get('setup') or ''))}</td></tr><tr><th>展開</th><td>{escape(str(arc.get('development') or ''))}</td></tr><tr><th>着地</th><td>{escape(str(arc.get('payoff') or ''))}</td></tr></table></details>
<details><summary>検証 readback</summary><p>{escape(str(media['video_codec']))}/{escape(str(media['audio_codec']))} · {media['width']}x{media['height']} · {media['fps']}fps · {media['duration_seconds']:.3f}s</p><p>Audio {audio['integrated_lufs']:.2f} LUFS / {audio['true_peak_dbtp']:.2f} dBTP · full decode {escape(str(readback['render']['full_decode']['status']))} · black/silence {escape(str(readback['signal_qa']['status']))}</p><p>Transcript: {escape(readback['transcript_authority']['engine'])}/{escape(readback['transcript_authority']['provider'])}; imported source captions, human transcript acceptance not claimed.</p></details>
</main></body></html>"""


def _open_script() -> str:
    return """param([int]$Port = 8072)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
exit $LASTEXITCODE
"""


def _serve_script() -> str:
    return r"""param([int]$Port = 8072)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
Write-Host "OUT-09 review URL: $url"
Start-Process -FilePath $url
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')
Push-Location $repoRoot
try {
    uvx python -m src.cli.serve_review --root $PSScriptRoot --port $Port
} finally {
    Pop-Location
}
"""


def _render_srt(items: list[dict[str, Any]]) -> str:
    blocks = []
    for index, item in enumerate(items, start=1):
        text = str(item.get("wrapped_text") or item.get("text") or "").replace("\r", "")
        blocks.append(
            f"{index}\n{_srt_time(float(item['display_start_seconds']))} --> "
            f"{_srt_time(float(item['display_end_seconds']))}\n{text}\n"
        )
    return "\n".join(blocks)


def _srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def _token_subsequence(display_text: str, source_text: str) -> bool:
    display = re.findall(r"[a-z0-9]+", display_text.lower())
    source = re.findall(r"[a-z0-9]+", source_text.lower())
    if not display:
        return False
    cursor = iter(source)
    return all(any(token == candidate for candidate in cursor) for token in display)


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if output.parent != review:
        raise SecondSourceShortRepeatabilityError(
            "output directory must be a direct episode/review child"
        )
    if not output.name.startswith(OUTPUT_PREFIX):
        raise SecondSourceShortRepeatabilityError("output directory must start with out09_")
    _safe_identifier(output.name, "output directory")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SecondSourceShortRepeatabilityError(f"invalid {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SecondSourceShortRepeatabilityError(f"{label} must be a JSON object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SecondSourceShortRepeatabilityError(f"{label} not found: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise SecondSourceShortRepeatabilityError(f"{label} not found: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise SecondSourceShortRepeatabilityError(
            f"{label} escapes allowed root: {path}"
        ) from exc


def _safe_identifier(value: str, label: str) -> None:
    if not value or SAFE_ID.fullmatch(value) is None:
        raise SecondSourceShortRepeatabilityError(f"unsafe {label}: {value!r}")


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise SecondSourceShortRepeatabilityError(f"{label} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise SecondSourceShortRepeatabilityError(f"{label} must be numeric") from exc


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item]


def _close(left: float, right: float) -> bool:
    return abs(float(left) - float(right)) <= TIME_TOLERANCE_SECONDS


def _overlap(left_start: float, left_end: float, right_start: float, right_end: float) -> bool:
    return max(left_start, right_start) < min(left_end, right_end) - TIME_TOLERANCE_SECONDS


def _powershell_command(path: Path, root: Path) -> str:
    relative = _relative(path, root).replace("/", "\\")
    return f"powershell -ExecutionPolicy Bypass -File {relative}"
