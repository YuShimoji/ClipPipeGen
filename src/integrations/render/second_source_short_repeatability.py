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
    CAPTION_FREE_BACKGROUND_POLICY,
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
STATE = "OUT09_STABLE_MANUAL_SAFE_REVIEW_READY"
OUTPUT_PREFIX = "out09_"
OUT08_PROVIDER_ID = "7J5aS_pcBj4"
CURRENT_MP4_SHA256 = (
    "b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50"
)
INITIAL_PREDECESSOR_MP4_SHA256 = (
    "300ee360e0b14c04345dec8df0d6ffd6b2eba85e655624ef7eb338426679e0c9"
)
FAILED_REPAIR_PREDECESSOR_MP4_SHA256 = (
    "3e7ef9d883cd10660b6aa95bdf9af364e076c3594b27c73c7ad065ad85a92916"
)
PREDECESSOR_MP4_SHA256 = INITIAL_PREDECESSOR_MP4_SHA256
SUBTITLE_DISPLAY_AUTHORITY = "generated_short_cue_overlay_from_source_json3"
REPAIR_REVIEW_QUESTION = (
    "字幕が短い単位で自然に切り替わり、画面を邪魔せず読めるか。"
    "最後の終わり方を含め、ほかに明確な違和感があれば教えてください。"
)
SAFE_REVIEW_QUESTIONS = (
    "ページを開いた直後に動画や音が勝手に始まらず、レビュー中にserverが維持されるか。",
    "手動で再生・音声解除した後、字幕の切替・可読性・終わり方に明確な違和感があるか。",
)
REVIEW_PORT = 8072
REVIEW_HOST = "127.0.0.1"
INITIAL_VOLUME_CEILING = 0.25
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
        _apply_out09_short_cue_style(layout)
        presentation_statistics = _validate_short_cue_presentation(
            presentation,
            expected_count=len(normalized["semantic_subtitles"]),
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
            composition_policy=normalized["composition_policy"],
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
                "json3_timing_authority": dict(
                    item.get("json3_timing_authority") or {}
                ),
            }
            for item in presentation
        ]
        elapsed = round(time.monotonic() - started, 3)
        video_sha256 = _sha256(video_path)
        review_access = _review_access_contract(
            output=output,
            root=root,
            video_sha256=video_sha256,
        )
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
            "user_feedback": normalized["user_feedback"],
            "repair": normalized["repair"],
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
                "display_authority": SUBTITLE_DISPLAY_AUTHORITY,
                "burn_in_applied": True,
                "source_native_caption_pixels_suppressed": True,
                "visible_overlay_event_count": len(presentation_items),
                "ass_srt_role": "display_and_provenance_sidecar",
                "statistics": presentation_statistics,
                "additional_blur_or_frosted_caption_surface": False,
                "human_transcript_acceptance_claimed": False,
            },
            "video": {
                "package_relative_path": video_path.name,
                "sha256": video_sha256,
            },
            "render": {
                "media": render_result["media"],
                "selected_video_encoder": render_result["selected_video_encoder"],
                "attempts": render_result["attempts"],
                "full_decode": render_result["full_decode"],
                "faststart": render_result.get("faststart"),
                "source_probe": render_result.get("source_probe"),
                "composition_policy": render_result.get("composition_policy"),
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
            "review_questions": list(SAFE_REVIEW_QUESTIONS),
            "review_entrypoint": review_access["clean_human_url"],
            "open_command": review_access["convenience_open_command"],
            "canonical_server_command": review_access[
                "canonical_foreground_server_command"
            ],
            "review_access": review_access,
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
        _write_text(
            stage / "serve_preview.ps1",
            _serve_script(expected_video_sha256=readback["video"]["sha256"]),
        )

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
            "repair": normalized["repair"],
            "subtitle_display_authority": {
                "mode": SUBTITLE_DISPLAY_AUTHORITY,
                "source_native_caption_pixels_suppressed": True,
                "burn_in_applied": True,
                "visible_overlay_event_count": len(presentation_items),
                "ass_srt_role": "display_and_provenance_sidecar",
                "additional_blur_or_frosted_caption_surface": False,
            },
            "composition_policy": normalized["composition_policy"],
            "review_access": review_access,
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


def repair_second_source_review_access_package(
    *,
    output_dir: Path,
    base_dir: Path | None = None,
    expected_video_sha256: str = CURRENT_MP4_SHA256,
) -> dict[str, Any]:
    """Repair only OUT-09 HTML/scripts/readback while preserving media bytes."""

    root = (base_dir or Path.cwd()).resolve()
    output = _resolved(root, output_dir)
    _require_directory(output, "OUT-09 review package")
    episode = output.parent.parent
    _validate_output_directory(episode, output)
    readback_path = output / "candidate_readback.json"
    manifest_path = output / "candidate_manifest.json"
    video_path = output / "candidate_01.mp4"
    for path, label in (
        (readback_path, "candidate readback"),
        (manifest_path, "candidate manifest"),
        (video_path, "current MP4"),
    ):
        _require_file(path, label)

    readback = _read_json(readback_path, "candidate readback")
    manifest = _read_json(manifest_path, "candidate manifest")
    if readback.get("artifact_id") != ARTIFACT_ID or manifest.get("artifact_id") != ARTIFACT_ID:
        raise SecondSourceShortRepeatabilityError("OUT-09 artifact identity mismatch")
    if manifest.get("manifest_self_integrity", {}).get(
        "sha256"
    ) != _canonical_manifest_self_hash(manifest):
        raise SecondSourceShortRepeatabilityError(
            "existing manifest self-integrity mismatch"
        )
    video_sha_before = _sha256(video_path)
    if video_sha_before != expected_video_sha256:
        raise SecondSourceShortRepeatabilityError(
            "current MP4 SHA-256 changed; access repair refused"
        )
    if readback.get("video", {}).get("sha256") != video_sha_before:
        raise SecondSourceShortRepeatabilityError("readback MP4 identity mismatch")
    if manifest.get("candidate_video_sha256") != video_sha_before:
        raise SecondSourceShortRepeatabilityError("manifest MP4 identity mismatch")
    file_names: list[str] = []
    for row in manifest.get("files", []):
        name = str(row.get("package_relative_path") or "")
        path = output / name
        _require_file(path, f"manifest file {name}")
        if _sha256(path) != str(row.get("sha256") or ""):
            raise SecondSourceShortRepeatabilityError(
                f"existing manifest file hash mismatch: {name}"
            )
        file_names.append(name)

    required_access_files = {
        "candidate_readback.json",
        "index.html",
        "open_preview.ps1",
        "serve_preview.ps1",
    }
    if not required_access_files.issubset(file_names):
        raise SecondSourceShortRepeatabilityError(
            "manifest does not contain the required review access files"
        )

    access = _review_access_contract(
        output=output,
        root=root,
        video_sha256=video_sha_before,
    )
    updated_readback = json.loads(json.dumps(readback))
    updated_readback["state"] = STATE
    updated_readback["review_questions"] = list(SAFE_REVIEW_QUESTIONS)
    updated_readback["review_entrypoint"] = access["clean_human_url"]
    updated_readback["open_command"] = access["convenience_open_command"]
    updated_readback["canonical_server_command"] = access[
        "canonical_foreground_server_command"
    ]
    updated_readback["review_access"] = access
    updated_readback["access_repair"] = {
        "kind": "stable_manual_safe_review_access_only",
        "media_sha256_before": video_sha_before,
        "media_sha256_after": video_sha_before,
        "media_bytes_changed": False,
        "updated_files": sorted(required_access_files),
    }

    stage = output / f".access-staging-{uuid.uuid4().hex}"
    stage.mkdir()
    try:
        _write_json(stage / "candidate_readback.json", updated_readback)
        _write_text(stage / "index.html", _render_html(updated_readback))
        _write_text(stage / "open_preview.ps1", _open_script())
        _write_text(
            stage / "serve_preview.ps1",
            _serve_script(expected_video_sha256=video_sha_before),
        )
        _validate_safe_review_assets(
            html=(stage / "index.html").read_text(encoding="utf-8"),
            open_script=(stage / "open_preview.ps1").read_text(encoding="utf-8"),
            serve_script=(stage / "serve_preview.ps1").read_text(encoding="utf-8"),
            expected_video_sha256=video_sha_before,
        )

        updated_manifest = json.loads(json.dumps(manifest))
        updated_manifest["state"] = STATE
        updated_manifest["review_access"] = access
        updated_files = []
        for name in sorted(file_names):
            source = stage / name if name in required_access_files else output / name
            updated_files.append(
                {
                    "package_relative_path": name,
                    "sha256": _sha256(source),
                    "byte_size": source.stat().st_size,
                }
            )
        updated_manifest["files"] = updated_files
        updated_manifest["manifest_self_integrity"] = {
            "algorithm": "sha256",
            "sha256": None,
        }
        updated_manifest["manifest_self_integrity"]["sha256"] = (
            _canonical_manifest_self_hash(updated_manifest)
        )
        _write_json(stage / "candidate_manifest.json", updated_manifest)

        if updated_manifest["candidate_video_sha256"] != video_sha_before:
            raise SecondSourceShortRepeatabilityError(
                "access repair attempted to change MP4 identity"
            )
        if updated_manifest["manifest_self_integrity"][
            "sha256"
        ] != _canonical_manifest_self_hash(updated_manifest):
            raise SecondSourceShortRepeatabilityError(
                "updated manifest self-integrity mismatch"
            )
        for name in sorted(required_access_files):
            os.replace(stage / name, output / name)
        os.replace(stage / "candidate_manifest.json", manifest_path)
    finally:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=output)

    video_sha_after = _sha256(video_path)
    if video_sha_after != video_sha_before:
        raise SecondSourceShortRepeatabilityError(
            "current MP4 changed during access repair"
        )
    parsed_manifest = _read_json(manifest_path, "updated candidate manifest")
    if parsed_manifest.get("manifest_self_integrity", {}).get(
        "sha256"
    ) != _canonical_manifest_self_hash(parsed_manifest):
        raise SecondSourceShortRepeatabilityError(
            "promoted manifest self-integrity mismatch"
        )
    return {
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "output_dir": output,
        "video_sha256": video_sha_after,
        "media_bytes_changed": False,
        "review_access": access,
        "manifest_self_integrity": parsed_manifest["manifest_self_integrity"][
            "sha256"
        ],
    }


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
    source_captions = _read_json(paths["source_caption_track"], "source caption track")
    edit_pack = _read_json(paths["edit_pack"], "edit pack")
    return {
        "rights": rights,
        "transcript": transcript,
        "source_captions": source_captions,
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

    feedback = plan.get("user_feedback")
    expected_feedback = {
        "overall": "bounded_presentation_repair_required",
        "human_observation_priority": (
            "authoritative_over_agent_legibility_observation"
        ),
        "native_caption_only_result": "failed_unreadable_at_review_size",
        "blurred_caption_duplication": "observed_in_lower_canvas",
        "content_selection": "not_rejected_not_yet_accepted",
        "endpoint_edit": "unchanged_not_reopened",
    }
    if not isinstance(feedback, dict) or any(
        feedback.get(key) != value for key, value in expected_feedback.items()
    ):
        raise SecondSourceShortRepeatabilityError(
            "bounded-repair user feedback is incomplete"
        )

    repair = plan.get("repair") if isinstance(plan.get("repair"), dict) else {}
    if (
        repair.get("kind") != "caption_canvas_presentation_repair"
        or repair.get("lineage_index") != 2
    ):
        raise SecondSourceShortRepeatabilityError("unsupported OUT-09 repair kind")
    initial_predecessor = (
        repair.get("initial_predecessor")
        if isinstance(repair.get("initial_predecessor"), dict)
        else {}
    )
    if (
        initial_predecessor.get("candidate_id") != candidate_id
        or initial_predecessor.get("video_sha256")
        != INITIAL_PREDECESSOR_MP4_SHA256
        or initial_predecessor.get("human_acceptance_claimed") is not False
    ):
        raise SecondSourceShortRepeatabilityError(
            "initial predecessor identity mismatch"
        )
    if not _close(
        _number(
            initial_predecessor.get("source_start_seconds"),
            "initial predecessor source start",
        ),
        start,
    ):
        raise SecondSourceShortRepeatabilityError(
            "bounded repair must preserve candidate start"
        )
    failed_predecessor = (
        repair.get("failed_repair_predecessor")
        if isinstance(repair.get("failed_repair_predecessor"), dict)
        else {}
    )
    if (
        failed_predecessor.get("candidate_id") != candidate_id
        or failed_predecessor.get("video_sha256")
        != FAILED_REPAIR_PREDECESSOR_MP4_SHA256
        or failed_predecessor.get("reason")
        != "unreadable_native_caption_and_blurred_caption_duplication"
        or failed_predecessor.get("human_acceptance_claimed") is not False
        or not _close(
            _number(
                failed_predecessor.get("source_start_seconds"),
                "failed predecessor source start",
            ),
            start,
        )
        or not _close(
            _number(
                failed_predecessor.get("source_end_seconds"),
                "failed predecessor source end",
            ),
            end,
        )
    ):
        raise SecondSourceShortRepeatabilityError(
            "failed repair predecessor identity mismatch"
        )

    subtitle_repair = (
        repair.get("subtitle_presentation")
        if isinstance(repair.get("subtitle_presentation"), dict)
        else {}
    )
    expected_subtitle_repair = {
        "display_authority": SUBTITLE_DISPLAY_AUTHORITY,
        "source_native_caption_pixels_suppressed": True,
        "timing_authority": "youtube_json3_event_and_token_offsets",
        "ass_srt_role": "display_and_provenance_sidecar",
        "maximum_words_per_cue": 6,
        "maximum_lines_per_cue": 2,
        "caption_plate": "opaque_solid_black",
        "caption_plate_alpha": 1.0,
        "additional_blur_or_frosted_caption_surface": False,
        "scope": "source_specific",
    }
    if any(
        subtitle_repair.get(key) != value
        for key, value in expected_subtitle_repair.items()
    ):
        raise SecondSourceShortRepeatabilityError(
            "short-cue caption authority is incomplete"
        )

    composition_policy = _normalize_composition_policy(repair)

    endpoint = (
        repair.get("endpoint_authority")
        if isinstance(repair.get("endpoint_authority"), dict)
        else {}
    )
    if endpoint.get("basis") != (
        "first_scene_transition_after_last_caption_and_speech"
    ):
        raise SecondSourceShortRepeatabilityError("endpoint basis is not natural")
    last_caption_end = _number(
        endpoint.get("last_native_caption_end_seconds"),
        "last native caption end",
    )
    last_speech_end = _number(
        endpoint.get("last_speech_end_seconds"), "last speech end"
    )
    silence_end = _number(endpoint.get("silence_end_seconds"), "silence end")
    next_scene_start = _number(
        endpoint.get("next_scene_start_seconds"), "next scene start"
    )
    next_caption_start = _number(
        endpoint.get("next_native_caption_start_seconds"),
        "next native caption start",
    )
    selected_end = _number(
        endpoint.get("selected_source_end_seconds"), "selected source end"
    )
    if (
        last_caption_end > selected_end + TIME_TOLERANCE_SECONDS
        or last_speech_end > selected_end + TIME_TOLERANCE_SECONDS
        or selected_end > silence_end + TIME_TOLERANCE_SECONDS
        or not _close(selected_end, end)
        or not _close(next_scene_start, end)
        or next_caption_start < end - TIME_TOLERANCE_SECONDS
    ):
        raise SecondSourceShortRepeatabilityError(
            "candidate endpoint does not preserve caption/speech/scene completion"
        )
    if (
        endpoint.get("fixed_padding_used") is not False
        or endpoint.get("fade_sfx_freeze_or_silence_added") is not False
        or endpoint.get("reopened_for_this_repair") is not False
    ):
        raise SecondSourceShortRepeatabilityError(
            "presentation repair must preserve the endpoint without effects"
        )

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
    json3_events = _json3_event_index(authority["source_captions"])
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
        if display_start < previous_end - TIME_TOLERANCE_SECONDS:
            raise SecondSourceShortRepeatabilityError("short cue plan must not overlap")
        if display_start - previous_end > 0.15 + TIME_TOLERANCE_SECONDS:
            raise SecondSourceShortRepeatabilityError(
                "short cue plan contains an unexplained display gap"
            )
        linked_ids = _string_list(raw.get("source_segment_ids"))
        if not linked_ids or any(value not in segments for value in linked_ids):
            raise SecondSourceShortRepeatabilityError(
                f"subtitle transcript linkage is incomplete: {subtitle_id}"
            )
        source_text = " ".join(str(segments[value].get("text") or "") for value in linked_ids)
        text = str(raw.get("text") or "").strip()
        words = _normalized_tokens(text)
        if not text or not 1 <= len(words) <= 6 or "\n" in text or "\r" in text:
            raise SecondSourceShortRepeatabilityError(
                f"short cue must contain 1-6 whole words: {subtitle_id}"
            )
        timing_authority = _validate_json3_cue_timing(
            raw,
            events=json3_events,
            source_start=source_start,
            source_end=source_end,
            subtitle_id=subtitle_id,
        )
        if (
            not _token_subsequence(text, source_text)
            or words != _normalized_tokens(timing_authority["token_text"])
        ):
            raise SecondSourceShortRepeatabilityError(
                f"short cue is not JSON3/transcript-backed: {subtitle_id}"
            )
        semantic.append(
            {
                "id": subtitle_id,
                "cut_id": "out09_candidate",
                "sequence_start_seconds": display_start,
                "sequence_end_seconds": display_end,
                "text": text,
                "source_text": source_text,
                "display_text_normalization": (
                    "short_phrase_from_json3_token_offsets_v1"
                ),
                "source_type": "imported_subtitle_track",
                "source_segment_ids": linked_ids,
                "json3_timing_authority": timing_authority,
            }
        )
        previous_end = display_end
    if duration - previous_end > 0.15 + TIME_TOLERANCE_SECONDS:
        raise SecondSourceShortRepeatabilityError(
            "last short cue leaves an unexplained trailing gap"
        )

    review_questions = plan.get("review_questions")
    if review_questions != [REPAIR_REVIEW_QUESTION]:
        raise SecondSourceShortRepeatabilityError(
            "the bounded repair requires exactly one review question"
        )
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
        ("caption_start", 0.25),
        ("caption_early_a", round(duration * 0.10, 3)),
        ("caption_early_b", round(duration * 0.20, 3)),
        ("caption_mid_a", round(duration * 0.30, 3)),
        (
            "authority_boundary",
            max(0.25, min(duration - 0.25, authority_boundary)),
        ),
        ("caption_mid_b", round(duration * 0.60, 3)),
        ("caption_late_a", round(duration * 0.70, 3)),
        ("caption_late_b", round(duration * 0.83, 3)),
        ("endpoint_caption", round(duration * 0.925, 3)),
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
            "display_normalization": "short_phrase_from_json3_token_offsets_v1",
            "human_transcript_acceptance_claimed": False,
        },
        "user_feedback": expected_feedback,
        "repair": {
            "kind": "caption_canvas_presentation_repair",
            "lineage_index": 2,
            "initial_predecessor": {
                "candidate_id": candidate_id,
                "source_start_seconds": _number(
                    initial_predecessor.get("source_start_seconds"),
                    "initial predecessor source start",
                ),
                "source_end_seconds": _number(
                    initial_predecessor.get("source_end_seconds"),
                    "initial predecessor source end",
                ),
                "duration_seconds": _number(
                    initial_predecessor.get("duration_seconds"),
                    "initial predecessor duration",
                ),
                "media_duration_seconds": _number(
                    initial_predecessor.get("media_duration_seconds"),
                    "initial predecessor media duration",
                ),
                "video_sha256": INITIAL_PREDECESSOR_MP4_SHA256,
                "human_acceptance_claimed": False,
            },
            "failed_repair_predecessor": {
                "candidate_id": candidate_id,
                "source_start_seconds": start,
                "source_end_seconds": end,
                "duration_seconds": _number(
                    failed_predecessor.get("duration_seconds"),
                    "failed predecessor duration",
                ),
                "media_duration_seconds": _number(
                    failed_predecessor.get("media_duration_seconds"),
                    "failed predecessor media duration",
                ),
                "video_sha256": FAILED_REPAIR_PREDECESSOR_MP4_SHA256,
                "reason": (
                    "unreadable_native_caption_and_blurred_caption_duplication"
                ),
                "human_acceptance_claimed": False,
            },
            "human_observation": dict(repair.get("human_observation") or {}),
            "background_canvas": dict(repair.get("background_canvas") or {}),
            "native_caption_suppression": dict(
                repair.get("native_caption_suppression") or {}
            ),
            "subtitle_presentation": expected_subtitle_repair,
            "endpoint_authority": {
                "basis": str(endpoint["basis"]),
                "last_native_caption_end_seconds": last_caption_end,
                "last_speech_end_seconds": last_speech_end,
                "silence_end_seconds": silence_end,
                "next_scene_start_seconds": next_scene_start,
                "next_native_caption_start_seconds": next_caption_start,
                "selected_source_end_seconds": selected_end,
                "fixed_padding_used": False,
                "fade_sfx_freeze_or_silence_added": False,
                "reopened_for_this_repair": False,
                "candidate_start_preserved": True,
                "verified_before_render": True,
            },
        },
        "composition_policy": composition_policy,
        "selection_authority": {
            "allowed_ranges": allowed,
            "excluded_ranges": excluded_readback,
            "candidate_within_allowed_range": True,
            "rejected_or_unselected_overlap_count": 0,
            "checked_before_render": True,
        },
        "boundaries": expected_boundaries,
    }


def _normalize_composition_policy(repair: dict[str, Any]) -> dict[str, Any]:
    observation = repair.get("human_observation") or {}
    expected_observation = {
        "native_caption_too_small_in_16_9_foreground": True,
        "full_source_blur_duplicates_caption_glyphs": True,
        "lower_canvas_appears_frosted_and_unreadable": True,
        "agent_legibility_observation_overridden": True,
    }
    if not isinstance(observation, dict) or any(
        observation.get(key) != value
        for key, value in expected_observation.items()
    ):
        raise SecondSourceShortRepeatabilityError(
            "human caption/canvas observation is incomplete"
        )

    background = repair.get("background_canvas") or {}
    suppression = repair.get("native_caption_suppression") or {}
    if (
        not isinstance(background, dict)
        or background.get("mode") != CAPTION_FREE_BACKGROUND_POLICY
        or background.get("measurement_source")
        != "ten_caption_active_source_frames"
        or background.get("full_source_blur_fallback_allowed") is not False
        or background.get("fallback")
        != "neutral_solid_or_caption_free_edge_only"
    ):
        raise SecondSourceShortRepeatabilityError(
            "caption-free background policy is incomplete"
        )
    source_frame = _exact_pixel_rect_source(background.get("source_frame_pixels"))
    if source_frame != {"width": 640, "height": 360}:
        raise SecondSourceShortRepeatabilityError(
            "OUT-09 caption crop requires the measured 640x360 source"
        )
    background_crop = _exact_pixel_rectangle(
        background.get("caption_free_crop_pixels"),
        label="caption-free background crop",
    )
    foreground_crop = _exact_pixel_rectangle(
        suppression.get("foreground_source_crop_pixels"),
        label="caption-free foreground crop",
    )
    caption_band = _exact_pixel_rectangle(
        suppression.get("caption_band_pixels"),
        label="native caption band",
    )
    if (
        suppression.get("method") != "bottom_crop"
        or suppression.get("mask_used") is not False
        or suppression.get("validated_caption_active_frame_count") != 10
        or suppression.get("important_content_preserved") is not True
        or suppression.get("conflict_status") != "none"
    ):
        raise SecondSourceShortRepeatabilityError(
            "native caption suppression evidence is incomplete"
        )
    expected_crop = {"x": 0, "y": 0, "width": 640, "height": 286}
    expected_band = {"x": 0, "y": 286, "width": 640, "height": 74}
    if background_crop != expected_crop or foreground_crop != expected_crop:
        raise SecondSourceShortRepeatabilityError(
            "caption-free crop does not match the measured source rectangle"
        )
    if caption_band != expected_band:
        raise SecondSourceShortRepeatabilityError(
            "native caption band does not match the measured source rectangle"
        )
    _validate_normalized_rectangle(
        background.get("caption_free_crop_normalized"),
        pixels=background_crop,
        source_frame=source_frame,
        label="caption-free background crop",
    )
    _validate_normalized_rectangle(
        suppression.get("caption_band_normalized"),
        pixels=caption_band,
        source_frame=source_frame,
        label="native caption band",
    )
    sample_times = background.get("representative_frame_source_seconds")
    if not isinstance(sample_times, list) or len(sample_times) != 10:
        raise SecondSourceShortRepeatabilityError(
            "caption-free crop requires ten measured source frames"
        )
    return {
        "mode": CAPTION_FREE_BACKGROUND_POLICY,
        "source_frame_pixels": source_frame,
        "background_source_crop_pixels": background_crop,
        "background_source_crop_normalized": dict(
            background["caption_free_crop_normalized"]
        ),
        "foreground_source_crop_pixels": foreground_crop,
        "native_caption_band_pixels": caption_band,
        "native_caption_band_normalized": dict(
            suppression["caption_band_normalized"]
        ),
        "native_caption_suppression": {
            "method": "bottom_crop",
            "mask_used": False,
            "important_content_preserved": True,
            "validated_caption_active_frame_count": 10,
            "conflict_status": "none",
        },
        "representative_frame_source_seconds": [
            round(_number(value, "caption crop sample time"), 3)
            for value in sample_times
        ],
        "full_source_blur_fallback_allowed": False,
        "fallback": "neutral_solid_or_caption_free_edge_only",
        "additional_blur_or_frosted_caption_surface": False,
    }


def _exact_pixel_rect_source(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    try:
        return {"width": int(value["width"]), "height": int(value["height"])}
    except (KeyError, TypeError, ValueError):
        return {}


def _exact_pixel_rectangle(value: Any, *, label: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise SecondSourceShortRepeatabilityError(f"{label} is missing")
    try:
        return {key: int(value[key]) for key in ("x", "y", "width", "height")}
    except (KeyError, TypeError, ValueError) as exc:
        raise SecondSourceShortRepeatabilityError(f"{label} is invalid") from exc


def _validate_normalized_rectangle(
    value: Any,
    *,
    pixels: dict[str, int],
    source_frame: dict[str, int],
    label: str,
) -> None:
    if not isinstance(value, dict):
        raise SecondSourceShortRepeatabilityError(f"{label} normalized rectangle is missing")
    expected = {
        "x": pixels["x"] / source_frame["width"],
        "y": pixels["y"] / source_frame["height"],
        "width": pixels["width"] / source_frame["width"],
        "height": pixels["height"] / source_frame["height"],
    }
    if any(
        abs(_number(value.get(key), f"{label} normalized {key}") - target)
        > 0.00001
        for key, target in expected.items()
    ):
        raise SecondSourceShortRepeatabilityError(
            f"{label} normalized rectangle does not match pixels"
        )


def _json3_event_index(captions: dict[str, Any]) -> dict[int, dict[str, Any]]:
    raw_events = captions.get("events")
    if not isinstance(raw_events, list):
        raise SecondSourceShortRepeatabilityError("JSON3 caption events are missing")
    return {
        index: event
        for index, event in enumerate(raw_events)
        if isinstance(event, dict)
    }


def _validate_json3_cue_timing(
    raw: dict[str, Any],
    *,
    events: dict[int, dict[str, Any]],
    source_start: float,
    source_end: float,
    subtitle_id: str,
) -> dict[str, Any]:
    timing = raw.get("timing_authority") or {}
    if (
        not isinstance(timing, dict)
        or timing.get("source") != "youtube_json3_event_and_token_offsets"
    ):
        raise SecondSourceShortRepeatabilityError(
            f"JSON3 timing authority is missing: {subtitle_id}"
        )
    try:
        event_index = int(timing["event_index"])
        token_start = int(timing["token_start_index"])
        token_end = int(timing["token_end_index_exclusive"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SecondSourceShortRepeatabilityError(
            f"JSON3 token span is invalid: {subtitle_id}"
        ) from exc
    event = events.get(event_index)
    if event is None:
        raise SecondSourceShortRepeatabilityError(
            f"JSON3 event is missing: {subtitle_id}"
        )
    tokens = _json3_text_tokens(event)
    if token_start < 0 or token_end <= token_start or token_end > len(tokens):
        raise SecondSourceShortRepeatabilityError(
            f"JSON3 token span leaves event: {subtitle_id}"
        )
    event_start = _json3_event_start_seconds(event)
    expected_start = event_start + (tokens[token_start]["offset_ms"] / 1000.0)
    boundary = timing.get("end_boundary") or {}
    expected_end = _json3_boundary_seconds(boundary, events=events)
    if (
        not _close(source_start, expected_start)
        or not _close(source_end, expected_end)
    ):
        raise SecondSourceShortRepeatabilityError(
            f"short cue timing does not match JSON3 boundary: {subtitle_id}"
        )
    token_text = "".join(token["text"] for token in tokens[token_start:token_end])
    return {
        "source": "youtube_json3_event_and_token_offsets",
        "event_index": event_index,
        "event_start_seconds": round(event_start, 3),
        "token_start_index": token_start,
        "token_end_index_exclusive": token_end,
        "token_text": " ".join(token_text.split()),
        "cue_source_start_seconds": round(expected_start, 3),
        "cue_source_end_seconds": round(expected_end, 3),
        "end_boundary": dict(boundary),
    }


def _json3_text_tokens(event: dict[str, Any]) -> list[dict[str, Any]]:
    tokens: list[dict[str, Any]] = []
    for segment in event.get("segs") or []:
        if not isinstance(segment, dict):
            continue
        text = str(segment.get("utf8") or "")
        if not text.strip():
            continue
        offset = segment.get("tOffsetMs")
        tokens.append(
            {
                "text": text,
                "offset_ms": 0 if offset is None else int(offset),
            }
        )
    return tokens


def _json3_event_start_seconds(event: dict[str, Any]) -> float:
    return _number(event.get("tStartMs"), "JSON3 event start") / 1000.0


def _json3_boundary_seconds(
    boundary: Any,
    *,
    events: dict[int, dict[str, Any]],
) -> float:
    if not isinstance(boundary, dict):
        raise SecondSourceShortRepeatabilityError("JSON3 cue end boundary is missing")
    kind = boundary.get("kind")
    try:
        event_index = int(boundary["event_index"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SecondSourceShortRepeatabilityError(
            "JSON3 cue end event is invalid"
        ) from exc
    event = events.get(event_index)
    if event is None:
        raise SecondSourceShortRepeatabilityError("JSON3 cue end event is missing")
    if kind == "token_onset":
        try:
            token_index = int(boundary["token_index"])
            token = _json3_text_tokens(event)[token_index]
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise SecondSourceShortRepeatabilityError(
                "JSON3 cue end token is invalid"
            ) from exc
        return _json3_event_start_seconds(event) + token["offset_ms"] / 1000.0
    if kind == "json3_event_start":
        return _json3_event_start_seconds(event)
    if kind == "json3_event_end":
        duration_ms = _number(event.get("dDurationMs"), "JSON3 event duration")
        return _json3_event_start_seconds(event) + duration_ms / 1000.0
    raise SecondSourceShortRepeatabilityError("unsupported JSON3 cue end boundary")


def _validate_short_cue_presentation(
    presentation: list[dict[str, Any]],
    *,
    expected_count: int,
) -> dict[str, Any]:
    if len(presentation) != expected_count or not presentation:
        raise SecondSourceShortRepeatabilityError(
            "short-cue presentation count mismatch"
        )
    word_counts: list[int] = []
    line_counts: list[int] = []
    durations: list[float] = []
    for item in presentation:
        text = str(item.get("text") or "")
        lines = [str(value) for value in item.get("wrapped_lines") or []]
        words = _normalized_tokens(text)
        duration = round(
            float(item["display_end_seconds"])
            - float(item["display_start_seconds"]),
            3,
        )
        if not 1 <= len(words) <= 6:
            raise SecondSourceShortRepeatabilityError(
                "short cue word count must stay within 1-6"
            )
        if not 1 <= len(lines) <= 2:
            raise SecondSourceShortRepeatabilityError(
                "short cue must render in one or two lines"
            )
        if _normalized_tokens(" ".join(lines)) != words:
            raise SecondSourceShortRepeatabilityError(
                "short cue line wrapping split a word"
            )
        if duration < 0.4 - TIME_TOLERANCE_SECONDS or duration > 2.5:
            raise SecondSourceShortRepeatabilityError(
                "short cue duration must stay within 0.4-2.5 seconds"
            )
        word_counts.append(len(words))
        line_counts.append(len(lines))
        durations.append(duration)
    return {
        "cue_count": len(presentation),
        "word_count_range": {"minimum": min(word_counts), "maximum": max(word_counts)},
        "line_count_range": {"minimum": min(line_counts), "maximum": max(line_counts)},
        "duration_seconds_range": {
            "minimum": min(durations),
            "maximum": max(durations),
        },
        "whole_word_wrap": True,
        "timing_authority": "youtube_json3_event_and_token_offsets",
    }


def _apply_out09_short_cue_style(layout: dict[str, Any]) -> None:
    """Use a crisp opaque plate so canvas blur is never the caption surface."""

    style = dict(layout.get("diagnostic_ass_style") or {})
    style.update(
        {
            "border_style": 3,
            "back_colour": "&H00000000",
            "out09_caption_plate": "opaque_solid_black",
            "out09_caption_plate_alpha": 1.0,
            "additional_blur_or_frosted_caption_surface": False,
        }
    )
    layout["diagnostic_ass_style"] = style
    layout["values"]["outline"] = 6
    layout["values"]["shadow"] = 1
    layout["out09_short_cue_overlay"] = {
        "caption_plate": "opaque_solid_black",
        "caption_plate_alpha": 1.0,
        "position": {
            "x": layout["values"]["bottom_center_x"],
            "y": layout["values"]["bottom_center_y"],
        },
        "safe_area": dict(layout["vertical_safe_envelope"]["subtitle"]),
        "additional_blur_or_frosted_caption_surface": False,
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
    if html.count("<video ") != 1 or html.count("data-review-question=") != len(
        SAFE_REVIEW_QUESTIONS
    ):
        raise SecondSourceShortRepeatabilityError(
            "review page must contain one video and exactly two safe review questions"
        )
    _validate_safe_review_assets(
        html=html,
        open_script=(stage / "open_preview.ps1").read_text(encoding="utf-8"),
        serve_script=(stage / "serve_preview.ps1").read_text(encoding="utf-8"),
        expected_video_sha256=str(readback["video"]["sha256"]),
    )


def _validate_safe_review_assets(
    *,
    html: str,
    open_script: str,
    serve_script: str,
    expected_video_sha256: str,
) -> None:
    video_tag = re.search(r"<video\b[^>]*>", html)
    if video_tag is None:
        raise SecondSourceShortRepeatabilityError("safe review video is missing")
    tag = video_tag.group(0)
    if re.search(r"\bautoplay\b", tag, flags=re.IGNORECASE):
        raise SecondSourceShortRepeatabilityError("human review video must not autoplay")
    for attribute in ("controls", "playsinline", "muted"):
        if re.search(rf"\b{attribute}\b", tag, flags=re.IGNORECASE) is None:
            raise SecondSourceShortRepeatabilityError(
                f"human review video is missing {attribute}"
            )
    if 'preload="metadata"' not in tag:
        raise SecondSourceShortRepeatabilityError(
            "human review video must preload metadata only"
        )
    required_html = (
        expected_video_sha256,
        ARTIFACT_ID,
        'window.location.search === "?qa-playback=1"',
        "video.defaultMuted = true",
        "video.muted = true",
        f"const maximumVolume = {INITIAL_VOLUME_CEILING:.2f}",
        "初期状態は停止・ミュート",
    )
    if any(value not in html for value in required_html):
        raise SecondSourceShortRepeatabilityError(
            "human review playback safety contract is incomplete"
        )
    if html.count("video.play()") != 1 or "if (exactMutedQaRoute)" not in html:
        raise SecondSourceShortRepeatabilityError(
            "QA playback must be explicit and exact-query gated"
        )
    if "localStorage" in html or "sessionStorage" in html:
        raise SecondSourceShortRepeatabilityError(
            "review playback state must not be restored from browser storage"
        )
    if "qa-playback" in open_script or "Start-Process -FilePath $url" not in open_script:
        raise SecondSourceShortRepeatabilityError(
            "open helper must use only the clean human URL"
        )
    if "[switch]$Serve" not in open_script or "-ProbeOnly" not in open_script:
        raise SecondSourceShortRepeatabilityError(
            "open helper must separate probe and explicit server startup"
        )
    required_server = (
        "127.0.0.1",
        expected_video_sha256,
        ARTIFACT_ID,
        "$request.AddRange(0, 1023)",
        "No process was stopped",
        "Press Ctrl+C",
    )
    if any(value not in serve_script for value in required_server):
        raise SecondSourceShortRepeatabilityError(
            "foreground server safety contract is incomplete"
        )
    if "Stop-Process" in serve_script or "taskkill" in serve_script.lower():
        raise SecondSourceShortRepeatabilityError(
            "foreground server helper must not kill a port owner"
        )


def _review_access_contract(
    *,
    output: Path,
    root: Path,
    video_sha256: str = CURRENT_MP4_SHA256,
) -> dict[str, Any]:
    clean_url = f"http://{REVIEW_HOST}:{REVIEW_PORT}/index.html"
    server = _powershell_script_command(
        output / "serve_preview.ps1",
        root,
        arguments=f"-Port {REVIEW_PORT}",
    )
    opener = _powershell_script_command(
        output / "open_preview.ps1",
        root,
        arguments=f"-Serve -Port {REVIEW_PORT}",
    )
    return {
        "state": STATE,
        "clean_human_url": clean_url,
        "canonical_foreground_server_command": server,
        "convenience_open_command": opener,
        "server_bind": REVIEW_HOST,
        "server_port": REVIEW_PORT,
        "server_ownership": "operator_foreground_powershell_until_ctrl_c",
        "server_window_must_remain_open": True,
        "worker_process_retention_claimed": False,
        "unknown_port_owner_killed": False,
        "autoplay": False,
        "initial_paused": True,
        "initial_muted": True,
        "initial_volume_maximum": INITIAL_VOLUME_CEILING,
        "qa_route": {
            "exact_query": "qa-playback=1",
            "human_documentation_allowed": False,
            "isolated_context_required": True,
            "muted_or_zero_volume_required": True,
            "pause_after_check": True,
        },
        "candidate_video_sha256": video_sha256,
        "media_mutation_allowed": False,
    }


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
<meta name="clippipegen-artifact-id" content="{ARTIFACT_ID}"><meta name="clippipegen-video-sha256" content="{escape(readback['video']['sha256'])}">
<title>OUT-09 second-source Short review</title><style>
:root{{color-scheme:dark;font-family:"Yu Gothic UI","Noto Sans JP",sans-serif;background:#06101d;color:#eff7ff}}*{{box-sizing:border-box}}body{{margin:0;overflow-x:hidden}}main{{width:min(900px,100%);margin:auto;padding:22px;overflow-wrap:anywhere}}section,details{{margin-top:18px;padding:16px;border:1px solid #30445f;border-radius:14px;background:#0d1a2c}}video{{display:block;width:auto;height:min(76vh,820px);max-width:100%;aspect-ratio:9/16;margin:18px auto;background:#000}}code{{color:#9fe7ff}}.boundary{{color:#ffd166}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #30445f;text-align:left}}@media(max-width:620px){{main{{padding:14px}}video{{height:min(72vh,700px)}}}}
</style></head><body data-artifact-id="{ARTIFACT_ID}" data-video-sha256="{escape(readback['video']['sha256'])}"><main><h1>OUT-09 second-source Short review</h1>
<p><code>{escape(readback['source_identity']['provider_id'])}</code> / source {candidate['source_start_seconds']:.3f}–{candidate['source_end_seconds']:.3f}s / sequence {candidate['duration_seconds']:.3f}s</p>
<p class="boundary">rights=pending / production_candidate=false / public use is not allowed</p>
<p id="playback-safety-note">初期状態は停止・ミュートです。音声確認時は手動で再生・解除してください（音量上限25%）。</p>
<video id="candidate-video" controls playsinline muted preload="metadata" poster="{escape(readback['navigation_frame']['package_relative_path'])}?v={escape(readback['navigation_frame']['sha256'][:16])}" src="{escape(readback['video']['package_relative_path'])}?v={escape(readback['video']['sha256'][:16])}"></video>
<script>
(() => {{
  const video = document.getElementById("candidate-video");
  const maximumVolume = {INITIAL_VOLUME_CEILING:.2f};
  const exactMutedQaRoute = window.location.search === "?qa-playback=1" && window.location.hash === "";
  video.defaultMuted = true;
  video.muted = true;
  video.volume = exactMutedQaRoute ? 0 : maximumVolume;
  const qaState = {{ exactRoute: exactMutedQaRoute, playEvents: 0, playingEvents: 0, audibleStateEvents: 0, completed: false, error: null }};
  window.__clipPipeReviewQa = qaState;
  video.addEventListener("play", () => {{ qaState.playEvents += 1; }});
  video.addEventListener("playing", () => {{ qaState.playingEvents += 1; }});
  video.addEventListener("volumechange", () => {{
    if (video.volume > maximumVolume) video.volume = maximumVolume;
    if (!video.muted && video.volume > 0) qaState.audibleStateEvents += 1;
  }});
  const runMutedQaPlayback = async () => {{
    video.defaultMuted = true;
    video.muted = true;
    video.volume = 0;
    try {{
      await video.play();
      window.setTimeout(() => {{ video.pause(); qaState.completed = true; }}, 1200);
    }} catch (error) {{
      qaState.error = error && error.name ? error.name : "play_failed";
      video.pause();
      qaState.completed = true;
    }}
  }};
  if (exactMutedQaRoute) {{
    if (video.readyState >= 2) window.queueMicrotask(runMutedQaPlayback);
    else video.addEventListener("canplay", runMutedQaPlayback, {{ once: true }});
  }}
}})();
</script>
<section><h2>安全なレビューで確認する2点</h2><ol>{questions}</ol></section>
<details open><summary>構成</summary><table><tr><th>導入</th><td>{escape(str(arc.get('setup') or ''))}</td></tr><tr><th>展開</th><td>{escape(str(arc.get('development') or ''))}</td></tr><tr><th>着地</th><td>{escape(str(arc.get('payoff') or ''))}</td></tr></table></details>
<details><summary>検証 readback</summary><p>{escape(str(media['video_codec']))}/{escape(str(media['audio_codec']))} · {media['width']}x{media['height']} · {media['fps']}fps · {media['duration_seconds']:.3f}s</p><p>Audio {audio['integrated_lufs']:.2f} LUFS / {audio['true_peak_dbtp']:.2f} dBTP · full decode {escape(str(readback['render']['full_decode']['status']))} · black/silence {escape(str(readback['signal_qa']['status']))}</p><p>Subtitle display authority: generated short-cue overlay from source JSON3. Source-native caption pixels are bottom-cropped; ASS/SRT preserve display and provenance.</p><p>Background: caption-free source crop only; no full-source fallback and no frosted caption surface.</p><p>Transcript: {escape(readback['transcript_authority']['engine'])}/{escape(readback['transcript_authority']['provider'])}; imported source captions, human transcript acceptance not claimed.</p></details>
</main></body></html>"""


def _open_script(
    *,
    default_port: int = REVIEW_PORT,
    review_label: str = "OUT-09",
) -> str:
    template = r"""param([switch]$Serve, [int]$Port = __DEFAULT_PORT__)
$ErrorActionPreference = 'Stop'
$serveScript = Join-Path $PSScriptRoot 'serve_preview.ps1'
$url = "http://127.0.0.1:$Port/index.html"
$canonical = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$serveScript`" -Port $Port"

function Get-ReviewProbeExitCode {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $serveScript -Port $Port -ProbeOnly *> $null
    return $LASTEXITCODE
}

$probe = Get-ReviewProbeExitCode
if ($probe -eq 0) {
    Start-Process -FilePath $url
    return
}
if ($probe -eq 5) {
    throw "Port $Port is occupied by an unrecognized process. No process was stopped."
}
if (-not $Serve) {
    Write-Host "__REVIEW_LABEL__ review server is not running."
    Write-Host "Start it in a foreground PowerShell and keep that window open:"
    Write-Host $canonical
    exit 2
}

$serverArgs = @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', "`"$serveScript`"",
    '-Port', "$Port"
)
$serverProcess = Start-Process -FilePath 'powershell.exe' -ArgumentList $serverArgs -PassThru
$deadline = [DateTime]::UtcNow.AddSeconds(20)
do {
    Start-Sleep -Milliseconds 400
    $serverProcess.Refresh()
    if ($serverProcess.HasExited) {
        throw "The foreground review server PowerShell exited before becoming healthy."
    }
    $probe = Get-ReviewProbeExitCode
    if ($probe -eq 0) {
        Start-Process -FilePath $url
        Write-Host "Review opened at $url"
        Write-Host "Keep the foreground server PowerShell window open during review; use Ctrl+C to stop it."
        return
    }
} while ([DateTime]::UtcNow -lt $deadline)
throw "The foreground review server did not pass its identity and Range health gate."
"""
    return (
        template.replace("__DEFAULT_PORT__", str(default_port))
        .replace("__REVIEW_LABEL__", review_label)
    )


def _serve_script(
    *,
    expected_video_sha256: str = CURRENT_MP4_SHA256,
    artifact_id: str = ARTIFACT_ID,
    default_port: int = REVIEW_PORT,
    review_label: str = "OUT-09",
) -> str:
    template = r"""param([int]$Port = __DEFAULT_PORT__, [switch]$ProbeOnly)
$ErrorActionPreference = 'Stop'
$expectedArtifact = '__ARTIFACT_ID__'
$expectedVideoSha256 = '__VIDEO_SHA256__'
$videoName = 'candidate_01.mp4'
$url = "http://127.0.0.1:$Port/index.html"

function Confirm-ReviewPackage {
    $root = (Resolve-Path -LiteralPath $PSScriptRoot).Path
    $indexPath = Join-Path $root 'index.html'
    $manifestPath = Join-Path $root 'candidate_manifest.json'
    $videoPath = Join-Path $root $videoName
    foreach ($path in @($indexPath, $manifestPath, $videoPath)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Required review file is missing: $path"
        }
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.artifact_id -ne $expectedArtifact) {
        throw "Review manifest artifact identity mismatch."
    }
    if ($manifest.candidate_video_sha256 -ne $expectedVideoSha256) {
        throw "Review manifest video identity mismatch."
    }
    $actualVideoSha256 = (Get-FileHash -LiteralPath $videoPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualVideoSha256 -ne $expectedVideoSha256) {
        throw "Current MP4 SHA-256 mismatch. Media serving was refused."
    }
    $index = Get-Content -LiteralPath $indexPath -Raw
    if (-not $index.Contains($expectedArtifact) -or -not $index.Contains($expectedVideoSha256)) {
        throw "Review index identity mismatch."
    }
    return [pscustomobject]@{ Root = $root; VideoLength = (Get-Item -LiteralPath $videoPath).Length }
}

function Test-PortListener {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $connect = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne(400)) { return $false }
        $client.EndConnect($connect)
        return $true
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

function Test-ReviewServerIdentity([long]$VideoLength) {
    try {
        $page = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        if ([int]$page.StatusCode -ne 200) { return $false }
        if (-not $page.Content.Contains($expectedArtifact) -or -not $page.Content.Contains($expectedVideoSha256)) { return $false }
        $request = [System.Net.HttpWebRequest]::Create("http://127.0.0.1:$Port/$videoName")
        $request.Method = 'GET'
        $request.Timeout = 3000
        $request.AddRange(0, 1023)
        $range = [System.Net.HttpWebResponse]$request.GetResponse()
        try {
            if ([int]$range.StatusCode -ne 206) { return $false }
            if ($range.Headers['Content-Range'] -ne "bytes 0-1023/$VideoLength") { return $false }
            if ([long]$range.ContentLength -ne 1024) { return $false }
        } finally {
            $range.Close()
        }
        return $true
    } catch {
        return $false
    }
}

$package = Confirm-ReviewPackage
$hasListener = Test-PortListener
if ($ProbeOnly) {
    if (-not $hasListener) { exit 4 }
    if (Test-ReviewServerIdentity -VideoLength $package.VideoLength) { exit 0 }
    exit 5
}
if ($hasListener) {
    if (Test-ReviewServerIdentity -VideoLength $package.VideoLength) {
        Write-Host "Verified existing __REVIEW_LABEL__ server at $url"
        Write-Host "Its owning foreground PowerShell remains responsible for server lifetime."
        exit 0
    }
    throw "Port $Port is occupied by an unrecognized process. No process was stopped and no alternate port was selected."
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
Write-Host "__REVIEW_LABEL__ review URL: $url"
Write-Host "Keep this PowerShell window open during review. Press Ctrl+C to stop the server."
Push-Location -LiteralPath $repoRoot
try {
    & uvx python -m src.cli.serve_review --root $package.Root --port $Port
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
"""
    return (
        template.replace("__ARTIFACT_ID__", artifact_id)
        .replace("__VIDEO_SHA256__", expected_video_sha256)
        .replace("__DEFAULT_PORT__", str(default_port))
        .replace("__REVIEW_LABEL__", review_label)
    )


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
    display = _normalized_tokens(display_text)
    source = _normalized_tokens(source_text)
    if not display:
        return False
    cursor = iter(source)
    return all(any(token == candidate for candidate in cursor) for token in display)


def _normalized_tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


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


def _powershell_script_command(
    path: Path,
    root: Path,
    *,
    arguments: str = "",
) -> str:
    relative = _relative(path, root).replace("/", "\\")
    suffix = f" {arguments}" if arguments else ""
    return (
        "powershell -NoProfile -ExecutionPolicy Bypass "
        f"-File {relative}{suffix}"
    )
