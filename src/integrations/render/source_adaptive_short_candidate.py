"""Source-neutral OUT-11 vertical Short candidate package builder.

The builder consumes only local, hash-bound authority.  It deliberately does
not fetch media, infer rights, choose an endpoint, or grant human/production
acceptance.  A source-specific plan must select its caption and composition
policies explicitly, and an endpoint selection must be bound before the render
executor can run.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
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
from src.integrations.render.endpoint_preflight import (
    EndpointPreflightError,
    payload_sha256 as _endpoint_payload_sha256,
    require_ready_for_render,
)
from src.integrations.render.real_unused_range_short_minibatch import (
    _extract_navigation_frame,
)
from src.integrations.render.second_source_short_repeatability import (
    _render_srt,
    _run_signal_qa,
)
from src.integrations.render.subtitle_overlay_visual_proof import _write_ass
from src.integrations.render.vertical_short_candidate import (
    NEUTRAL_MATTE_BACKGROUND_POLICY,
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


SCHEMA_VERSION = "clippipegen.out11.source_adaptive_short_candidate.v0"
PLAN_SCHEMA_VERSION = "clippipegen.out11.source_adaptive_candidate_plan.v0"
STATE = "OUT11_SOURCE_ADAPTIVE_SHORT_CANDIDATE_REVIEW_READY"
CAPTION_MODE_OVERLAY = "official_overlay"
CAPTION_MODE_NATIVE = "native_baked_caption_only"
MIN_DURATION_SECONDS = 12.0
MAX_DURATION_SECONDS = 60.0
TIME_TOLERANCE_SECONDS = 0.006
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
REQUIRED_INPUT_ROLES = {
    "rights_manifest",
    "material_ledger",
    "source_caption_track",
    "endpoint_preflight",
    "endpoint_selection",
    "endpoint_evidence_manifest",
}

RenderExecutor = Callable[..., dict[str, Any]]
NavigationExecutor = Callable[..., dict[str, Any]]
SignalQaExecutor = Callable[..., dict[str, Any]]


class SourceAdaptiveShortCandidateError(VerticalShortCandidateError):
    """Raised when source-specific authority or the candidate package is invalid."""


def build_source_adaptive_short_candidate(
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
    """Build one hash-bound source-adaptive vertical candidate package."""

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
    try:
        require_ready_for_render(
            plan,
            authority["endpoint_preflight"],
            authority["endpoint_selection"],
        )
    except EndpointPreflightError as exc:
        raise SourceAdaptiveShortCandidateError(str(exc)) from exc
    normalized = _normalize_plan(plan=plan, authority=authority)

    review_dir = output.parent
    review_dir.mkdir(parents=True, exist_ok=True)
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    stage.mkdir()
    work = stage / ".work"
    work.mkdir()
    backup: Path | None = None
    try:
        _write_json(stage / "candidate_plan.json", plan)
        endpoint_evidence = _copy_endpoint_evidence(stage=stage, authority=authority)

        video_path = stage / "candidate.mp4"
        frame_path = stage / "candidate_frame_qa.jpg"
        navigation_path = stage / "candidate_navigation.jpg"
        internal_ass = work / "render_subtitles.ass"
        layout, presentation, selector = build_vertical_subtitle_presentation(
            normalized["semantic_subtitles"],
            application_key="out11_source_adaptive_application",
            dimension_source="out11_source_adaptive_vertical_canvas",
        )
        _write_ass(internal_ass, presentation, layout=layout, review_label=None)

        subtitle_files: list[dict[str, Any]] = []
        containment: dict[str, Any] | None = None
        if normalized["caption_mode"] == CAPTION_MODE_OVERLAY:
            containment = validate_vertical_subtitle_containment(
                presentation,
                expected_duration=normalized["duration_seconds"],
                layout=layout,
                expected_count=len(presentation),
            )
            ass_path = stage / "candidate_subtitles.ass"
            srt_path = stage / "candidate_subtitles.srt"
            shutil.copyfile(internal_ass, ass_path)
            _write_text(srt_path, _render_srt(presentation))
            validate_ass_visible_content(
                ass_path,
                expected_count=len(presentation),
                required_texts=(
                    _ass_visible_anchor(str(presentation[0]["text"])),
                    _ass_visible_anchor(str(presentation[-1]["text"])),
                ),
            )
            subtitle_files = [
                _file_row(ass_path),
                _file_row(srt_path),
            ]
        else:
            sidecar = stage / "official_captions.json3"
            shutil.copyfile(authority["source_caption_track_path"], sidecar)
            subtitle_files = [_file_row(sidecar)]

        render_result = render_executor(
            source_video_path=authority["source_video_path"],
            source_audio_path=authority["source_audio_path"],
            timeline=normalized["timeline"],
            ass_path=internal_ass,
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
            raise SourceAdaptiveShortCandidateError(
                "candidate black/silence QA did not pass"
            )
        _cleanup_internal_directory(work, expected_parent=stage)

        video_sha256 = _sha256(video_path)
        subtitle_items = [
            {
                "subtitle_id": str(item["subtitle_id"]),
                "display_start_seconds": float(item["display_start_seconds"]),
                "display_end_seconds": float(item["display_end_seconds"]),
                "text": str(item["text"]),
                "source_event_index": int(
                    (item.get("json3_timing_authority") or {})["event_index"]
                ),
            }
            for item in presentation
        ]
        readback = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": normalized["artifact_id"],
            "state": STATE,
            "episode_id": episode.name,
            "source_identity": normalized["source_identity"],
            "input_integrity": authority["input_integrity"],
            "materials": authority["materials"],
            "candidate": {
                "candidate_id": normalized["candidate_id"],
                "source_start_seconds": normalized["source_start_seconds"],
                "source_end_seconds": normalized["source_end_seconds"],
                "duration_seconds": normalized["duration_seconds"],
                "rationale": normalized["rationale"],
                "human_review_pending": True,
                "acceptance_granted": False,
            },
            "repair_lineage": normalized["repair_lineage"],
            "endpoint_preflight": {
                "preflight_sha256": _endpoint_payload_sha256(
                    authority["endpoint_preflight"]
                ),
                "selection_sha256": _endpoint_payload_sha256(
                    authority["endpoint_selection"]
                ),
                "selection_state": authority["endpoint_selection"]["state"],
                "selected_candidate": authority["endpoint_selection"][
                    "selected_candidate"
                ],
                "evidence": endpoint_evidence,
            },
            "caption": {
                "mode": normalized["caption_mode"],
                "source_authority": "official_json3",
                "overlay_burn_in_applied": normalized["caption_mode"]
                == CAPTION_MODE_OVERLAY,
                "native_baked_caption_only": normalized["caption_mode"]
                == CAPTION_MODE_NATIVE,
                "double_display_rejected": True,
                "source_caption_track_sha256": authority["source_caption_track_sha256"],
                "files": subtitle_files,
                "count": len(subtitle_items),
                "containment": containment,
                "selector": selector if presentation else None,
                "items": subtitle_items,
            },
            "video": {
                "package_relative_path": video_path.name,
                "sha256": video_sha256,
                "byte_size": video_path.stat().st_size,
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
            "safe_review": {
                "autoplay": False,
                "initial_muted": True,
                "initial_time_seconds": 0,
                "initial_volume_ceiling": 0.25,
                "exact_video_sha256": video_sha256,
                "human_review_pending": True,
            },
            "review_question": normalized["review_question"],
            "boundaries": normalized["boundaries"],
        }
        _write_json(stage / "candidate_readback.json", readback)
        _write_text(stage / "index.html", _render_html(readback))

        files = [
            _file_row(path)
            for path in sorted(item for item in stage.iterdir() if item.is_file())
        ]
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": normalized["artifact_id"],
            "state": STATE,
            "episode_id": episode.name,
            "source_identity": normalized["source_identity"]["identity"],
            "candidate_video_sha256": video_sha256,
            "caption_mode": normalized["caption_mode"],
            "repair_lineage": normalized["repair_lineage"],
            "files": files,
            "file_count": len(files),
            "closed_gates": normalized["boundaries"],
            "manifest_self_integrity": {
                "algorithm": "sha256-canonical-json-self-null",
                "sha256": None,
            },
        }
        manifest["manifest_self_integrity"]["sha256"] = _canonical_manifest_self_hash(
            manifest
        )
        _write_json(stage / "candidate_manifest.json", manifest)
        _validate_staged_package(stage, readback, manifest)
        backup = _atomic_promote(stage, output)
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)

    final_readback = _read_json(
        output / "candidate_readback.json", "candidate readback"
    )
    return {
        "artifact_id": normalized["artifact_id"],
        "output_dir": output,
        "video_path": output / "candidate.mp4",
        "readback_path": output / "candidate_readback.json",
        "manifest_path": output / "candidate_manifest.json",
        "index_path": output / "index.html",
        "readback": final_readback,
    }


def _load_authority(
    *, root: Path, episode: Path, plan: dict[str, Any]
) -> dict[str, Any]:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise SourceAdaptiveShortCandidateError("unsupported candidate plan schema")
    artifact_id = str(plan.get("artifact_id") or "")
    _safe_identifier(artifact_id, "artifact id")
    if plan.get("episode_id") != episode.name:
        raise SourceAdaptiveShortCandidateError("candidate plan episode_id mismatch")
    rows = plan.get("expected_inputs")
    if not isinstance(rows, list):
        raise SourceAdaptiveShortCandidateError("expected_inputs are missing")
    paths: dict[str, Path] = {}
    integrity: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise SourceAdaptiveShortCandidateError("invalid expected input row")
        role = str(row.get("role") or "")
        if role in paths or role not in REQUIRED_INPUT_ROLES:
            raise SourceAdaptiveShortCandidateError(f"unexpected input role: {role}")
        path = _resolved(root, Path(str(row.get("path") or "")))
        _require_file(path, f"input {role}")
        _require_within(path, episode, f"input {role}")
        actual = _sha256(path)
        if str(row.get("sha256") or "").lower() != actual:
            raise SourceAdaptiveShortCandidateError(f"input hash mismatch: {role}")
        paths[role] = path
        integrity.append(
            {
                "role": role,
                "path": _relative(path, root),
                "sha256": actual,
                "verified": True,
            }
        )
    if set(paths) != REQUIRED_INPUT_ROLES:
        missing = sorted(REQUIRED_INPUT_ROLES - set(paths))
        raise SourceAdaptiveShortCandidateError(
            f"required input roles are missing: {', '.join(missing)}"
        )

    rights = _read_json(paths["rights_manifest"], "rights manifest")
    if str((rights.get("compliance_check") or {}).get("status") or "") != "pending":
        raise SourceAdaptiveShortCandidateError("OUT-11 requires rights=pending")
    ledger = _read_json(paths["material_ledger"], "material ledger")
    materials = plan.get("materials") if isinstance(plan.get("materials"), dict) else {}
    try:
        video = _material_readback(
            ledger,
            material_id=str(
                (materials.get("source_video") or {}).get("material_id") or ""
            ),
            expected_kind="source_video",
            root=root,
            episode=episode,
        )
        audio = _material_readback(
            ledger,
            material_id=str(
                (materials.get("source_audio") or {}).get("material_id") or ""
            ),
            expected_kind="source_audio",
            root=root,
            episode=episode,
        )
    except EditorialSequenceError as exc:
        raise SourceAdaptiveShortCandidateError(str(exc)) from exc
    for label, actual, expected in (
        ("video", video["sha256"], (materials.get("source_video") or {}).get("sha256")),
        ("audio", audio["sha256"], (materials.get("source_audio") or {}).get("sha256")),
    ):
        if actual != str(expected or "").lower():
            raise SourceAdaptiveShortCandidateError(
                f"source {label} plan hash mismatch"
            )
    return {
        "rights": rights,
        "ledger": ledger,
        "source_caption_track": _read_json(
            paths["source_caption_track"], "source caption track"
        ),
        "source_caption_track_path": paths["source_caption_track"],
        "source_caption_track_sha256": _sha256(paths["source_caption_track"]),
        "endpoint_preflight": _read_json(
            paths["endpoint_preflight"], "endpoint preflight"
        ),
        "endpoint_selection": _read_json(
            paths["endpoint_selection"], "endpoint selection"
        ),
        "endpoint_evidence_manifest": _read_json(
            paths["endpoint_evidence_manifest"], "endpoint evidence manifest"
        ),
        "endpoint_evidence_manifest_path": paths["endpoint_evidence_manifest"],
        "source_video_path": _resolved(root, Path(video["file_path"])),
        "source_audio_path": _resolved(root, Path(audio["file_path"])),
        "materials": {"source_video": video, "source_audio": audio},
        "input_integrity": integrity,
    }


def _normalize_plan(
    *, plan: dict[str, Any], authority: dict[str, Any]
) -> dict[str, Any]:
    identity = plan.get("source_identity")
    if not isinstance(identity, dict):
        raise SourceAdaptiveShortCandidateError("source identity is missing")
    source_identity = {
        key: str(identity.get(key) or "").strip()
        for key in (
            "identity",
            "platform",
            "provider_id",
            "url",
            "title",
            "channel",
            "channel_id",
        )
    }
    if (
        not all(source_identity.values())
        or identity.get("official_channel") is not True
    ):
        raise SourceAdaptiveShortCandidateError(
            "official source identity is incomplete"
        )
    _safe_identifier(source_identity["provider_id"], "source provider id")
    if source_identity["identity"] != (
        f"{source_identity['platform']}:{source_identity['provider_id']}"
    ):
        raise SourceAdaptiveShortCandidateError("source identity tuple is inconsistent")
    rights_url = str((authority["rights"].get("source_video") or {}).get("url") or "")
    if source_identity["provider_id"] not in rights_url:
        raise SourceAdaptiveShortCandidateError(
            "rights snapshot source identity mismatch"
        )

    preflight = authority["endpoint_preflight"]
    selection = authority["endpoint_selection"]
    preflight_source = (preflight.get("input") or {}).get("source") or {}
    if (
        preflight_source.get("identity") != source_identity["identity"]
        or preflight_source.get("sha256")
        != authority["materials"]["source_video"]["sha256"]
    ):
        raise SourceAdaptiveShortCandidateError("endpoint source authority mismatch")

    candidate = plan.get("candidate")
    if not isinstance(candidate, dict):
        raise SourceAdaptiveShortCandidateError("candidate is missing")
    candidate_id = str(candidate.get("candidate_id") or "")
    _safe_identifier(candidate_id, "candidate id")
    start = _number(candidate.get("source_start_seconds"), "candidate source start")
    end = _number(candidate.get("source_end_seconds"), "candidate source end")
    duration = round(end - start, 6)
    if not MIN_DURATION_SECONDS <= duration <= MAX_DURATION_SECONDS:
        raise SourceAdaptiveShortCandidateError(
            "candidate duration is outside 12-60 seconds"
        )
    if (
        abs(duration - _number(candidate.get("duration_seconds"), "candidate duration"))
        > TIME_TOLERANCE_SECONDS
    ):
        raise SourceAdaptiveShortCandidateError(
            "candidate duration does not match source range"
        )
    selected = selection.get("selected_candidate") or {}
    if (
        abs(_number(selected.get("end_seconds"), "selected endpoint") - end)
        > TIME_TOLERANCE_SECONDS
        or abs(
            _number(
                (preflight.get("input") or {}).get("source_start_seconds"),
                "endpoint source start",
            )
            - start
        )
        > TIME_TOLERANCE_SECONDS
    ):
        raise SourceAdaptiveShortCandidateError(
            "endpoint selection does not match candidate range"
        )

    composition = plan.get("composition_policy")
    if (
        not isinstance(composition, dict)
        or composition.get("mode") != NEUTRAL_MATTE_BACKGROUND_POLICY
    ):
        raise SourceAdaptiveShortCandidateError(
            "explicit neutral-matte full-source-fit composition is required"
        )
    if (
        composition.get("crop_applied") is not False
        or composition.get("important_content_preserved") is not True
    ):
        raise SourceAdaptiveShortCandidateError(
            "neutral-matte composition must preserve the full source"
        )

    caption = plan.get("caption_policy")
    if not isinstance(caption, dict):
        raise SourceAdaptiveShortCandidateError("caption policy is missing")
    mode = str(caption.get("mode") or "")
    if mode not in {CAPTION_MODE_OVERLAY, CAPTION_MODE_NATIVE}:
        raise SourceAdaptiveShortCandidateError("unsupported caption mode")
    if caption.get("source_authority") != "official_json3":
        raise SourceAdaptiveShortCandidateError(
            "caption authority must be official_json3"
        )
    overlay_enabled = caption.get("overlay_enabled") is True
    native_visible = caption.get("native_captions_visible") is True
    crop_conflict = caption.get("crop_intersects_native_caption_band") is True
    if crop_conflict or (overlay_enabled and native_visible):
        raise SourceAdaptiveShortCandidateError(
            "native and overlay caption display/crop conflict"
        )
    if mode == CAPTION_MODE_OVERLAY and (not overlay_enabled or native_visible):
        raise SourceAdaptiveShortCandidateError(
            "official overlay caption policy is incomplete"
        )
    if mode == CAPTION_MODE_NATIVE and (overlay_enabled or not native_visible):
        raise SourceAdaptiveShortCandidateError(
            "native baked caption policy is incomplete"
        )

    events = _caption_event_index(authority["source_caption_track"])
    raw_cues = candidate.get("caption_cues")
    if not isinstance(raw_cues, list):
        raise SourceAdaptiveShortCandidateError("candidate caption_cues must be a list")
    if mode == CAPTION_MODE_OVERLAY and not raw_cues:
        raise SourceAdaptiveShortCandidateError("official overlay cues are missing")
    if mode == CAPTION_MODE_NATIVE and raw_cues:
        raise SourceAdaptiveShortCandidateError(
            "native baked mode cannot also render overlay cues"
        )
    semantic: list[dict[str, Any]] = []
    previous_source_start = start
    for index, raw in enumerate(raw_cues, start=1):
        if not isinstance(raw, dict):
            raise SourceAdaptiveShortCandidateError("invalid caption cue")
        cue_id = str(raw.get("id") or f"cue_{index:03d}")
        _safe_identifier(cue_id, "caption cue id")
        event_index = int(raw.get("event_index", -1))
        event = events.get(event_index)
        if event is None:
            raise SourceAdaptiveShortCandidateError(
                f"official caption event is missing: {cue_id}"
            )
        cue_start = _number(raw.get("source_start_seconds"), "caption source start")
        cue_end = _number(raw.get("source_end_seconds"), "caption source end")
        text = str(raw.get("text") or "").strip()
        if (
            abs(cue_start - event["start_seconds"]) > TIME_TOLERANCE_SECONDS
            or abs(cue_end - event["end_seconds"]) > TIME_TOLERANCE_SECONDS
            or text != event["text"]
        ):
            raise SourceAdaptiveShortCandidateError(
                f"caption is not exact official JSON3 authority: {cue_id}"
            )
        if (
            cue_start < start - TIME_TOLERANCE_SECONDS
            or cue_end > end + TIME_TOLERANCE_SECONDS
        ):
            raise SourceAdaptiveShortCandidateError(
                f"caption leaves candidate: {cue_id}"
            )
        if (
            cue_end <= cue_start
            or cue_start < previous_source_start - TIME_TOLERANCE_SECONDS
        ):
            raise SourceAdaptiveShortCandidateError(
                f"caption timing is invalid: {cue_id}"
            )
        semantic.append(
            {
                "id": cue_id,
                "cut_id": candidate_id,
                "sequence_start_seconds": round(cue_start - start, 3),
                "sequence_end_seconds": round(cue_end - start, 3),
                "text": text,
                "source_type": "official_json3_event",
                "source_segment_ids": [f"event_{event_index:06d}"],
                "json3_timing_authority": {
                    "event_index": event_index,
                    "source_start_seconds": cue_start,
                    "source_end_seconds": cue_end,
                },
            }
        )
        previous_source_start = cue_start

    boundaries = plan.get("boundaries")
    if not isinstance(boundaries, dict):
        raise SourceAdaptiveShortCandidateError("closed-gate boundaries are missing")
    expected_boundaries = {
        "rights_status": "pending",
        "production_acceptance": False,
        "thumbnail_acceptance": False,
        "public_or_publishing_acceptance": False,
        "publish_or_upload_attempted": False,
        "human_review_pending": True,
        "acceptance_granted": False,
    }
    if any(boundaries.get(key) != value for key, value in expected_boundaries.items()):
        raise SourceAdaptiveShortCandidateError("closed-gate boundaries are incomplete")
    review_question = str(plan.get("review_question") or "").strip()
    if not review_question:
        raise SourceAdaptiveShortCandidateError("review question is missing")
    repair_lineage = plan.get("repair_lineage")
    if repair_lineage is not None:
        if not isinstance(repair_lineage, dict):
            raise SourceAdaptiveShortCandidateError("repair lineage must be an object")
        predecessor_sha = str(repair_lineage.get("predecessor_video_sha256") or "")
        predecessor_reason = str(repair_lineage.get("predecessor_reason") or "").strip()
        if (
            not re.fullmatch(r"[0-9a-f]{64}", predecessor_sha)
            or int(repair_lineage.get("predecessor_video_byte_size") or 0) <= 0
            or _number(
                repair_lineage.get("predecessor_source_end_seconds"),
                "predecessor source end",
            )
            <= _number(
                repair_lineage.get("predecessor_source_start_seconds"),
                "predecessor source start",
            )
            or not predecessor_reason
            or repair_lineage.get("human_decision")
            != "bounded_same_source_interval_repair_required"
        ):
            raise SourceAdaptiveShortCandidateError("repair lineage is incomplete")
        repair_lineage = dict(repair_lineage)
    return {
        "artifact_id": str(plan["artifact_id"]),
        "source_identity": {**source_identity, "official_channel": True},
        "candidate_id": candidate_id,
        "source_start_seconds": start,
        "source_end_seconds": end,
        "duration_seconds": duration,
        "rationale": str(candidate.get("rationale") or "").strip(),
        "repair_lineage": repair_lineage,
        "caption_mode": mode,
        "semantic_subtitles": semantic,
        "composition_policy": dict(composition),
        "timeline": [
            {
                "id": candidate_id,
                "source_start_seconds": start,
                "source_end_seconds": end,
                "sequence_start_seconds": 0.0,
                "sequence_end_seconds": duration,
                "transition_in": "sequence_start",
            }
        ],
        "frame_samples": _frame_samples(candidate, duration),
        "review_question": review_question,
        "boundaries": dict(boundaries),
    }


def _copy_endpoint_evidence(
    *, stage: Path, authority: dict[str, Any]
) -> list[dict[str, Any]]:
    manifest = authority["endpoint_evidence_manifest"]
    preflight = authority["endpoint_preflight"]
    selection = authority["endpoint_selection"]
    expected_identity = str(
        (((preflight.get("input") or {}).get("source") or {}).get("identity") or "")
    )
    if (
        manifest.get("schema_version") != "clippipegen.endpoint_evidence_manifest.v0"
        or manifest.get("source_identity") != expected_identity
        or manifest.get("source_media_sha256")
        != authority["materials"]["source_video"]["sha256"]
        or manifest.get("selection_state") != "ready_for_render"
        or abs(
            _number(
                manifest.get("selected_end_seconds"), "endpoint evidence selected end"
            )
            - _number(
                (selection.get("selected_candidate") or {}).get("end_seconds"),
                "selected endpoint",
            )
        )
        > TIME_TOLERANCE_SECONDS
        or (manifest.get("manifest_self_integrity") or {}).get("sha256")
        != _canonical_manifest_self_hash(manifest)
    ):
        raise SourceAdaptiveShortCandidateError(
            "endpoint evidence manifest is incomplete"
        )
    rows = manifest.get("files")
    if not isinstance(rows, list) or manifest.get("file_count") != len(rows):
        raise SourceAdaptiveShortCandidateError(
            "endpoint evidence file list is invalid"
        )
    source_dir = authority["endpoint_evidence_manifest_path"].parent.resolve()
    copied: list[dict[str, Any]] = []
    names: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise SourceAdaptiveShortCandidateError("invalid endpoint evidence row")
        relative = Path(str(row.get("path") or ""))
        if relative.is_absolute() or len(relative.parts) != 1:
            raise SourceAdaptiveShortCandidateError(
                "endpoint evidence path is not package-local"
            )
        name = relative.name
        _safe_identifier(name, "endpoint evidence file")
        if name in names:
            raise SourceAdaptiveShortCandidateError("duplicate endpoint evidence file")
        names.add(name)
        source = (source_dir / name).resolve()
        _require_within(source, source_dir, "endpoint evidence file")
        _require_file(source, "endpoint evidence file")
        if _sha256(source) != str(
            row.get("sha256") or ""
        ).lower() or source.stat().st_size != int(row.get("byte_size") or -1):
            raise SourceAdaptiveShortCandidateError(
                f"endpoint evidence payload mismatch: {name}"
            )
        target = stage / name
        shutil.copyfile(source, target)
        copied.append(_file_row(target))
    required = {
        "endpoint_preflight.json",
        "endpoint_selection.json",
        "endpoint_contact_sheet.jpg",
        "endpoint_waveform.png",
    }
    if not required.issubset(names):
        raise SourceAdaptiveShortCandidateError(
            "endpoint evidence payloads are missing"
        )
    manifest_target = stage / "endpoint_evidence_manifest.json"
    shutil.copyfile(authority["endpoint_evidence_manifest_path"], manifest_target)
    copied.append(_file_row(manifest_target))
    return copied


def _caption_event_index(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    events: dict[int, dict[str, Any]] = {}
    for index, row in enumerate(payload.get("events") or []):
        if not isinstance(row, dict):
            continue
        text = _normalize_caption_text(
            "".join(
                str(segment.get("utf8") or "")
                for segment in row.get("segs") or []
                if isinstance(segment, dict)
            )
        )
        if not text:
            continue
        start = float(row.get("tStartMs") or 0) / 1000.0
        duration = float(row.get("dDurationMs") or 0) / 1000.0
        if duration <= 0:
            continue
        events[index] = {
            "start_seconds": round(start, 3),
            "end_seconds": round(start + duration, 3),
            "text": text,
        }
    if not events:
        raise SourceAdaptiveShortCandidateError(
            "official JSON3 caption events are missing"
        )
    return events


def _normalize_caption_text(value: str) -> str:
    """Remove non-rendering YouTube spacing controls without rewriting words."""

    return (
        value.replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u2060", "")
        .replace("\ufeff", "")
        .strip()
    )


def _ass_visible_anchor(value: str) -> str:
    """Select a stable rendered word for the shared UTF-8 ASS visibility guard."""

    runs = re.findall(r"[A-Za-z0-9\u3040-\u30ff\u3400-\u9fff]+", value)
    if not runs:
        raise SourceAdaptiveShortCandidateError(
            "official caption has no stable visible ASS anchor"
        )
    return max(runs, key=lambda item: (len(item), item))


def _frame_samples(
    candidate: dict[str, Any], duration: float
) -> list[tuple[str, float]]:
    raw = candidate.get("frame_samples")
    if raw is None:
        return [
            ("opening", round(min(0.8, duration * 0.08), 3)),
            ("middle", round(duration * 0.5, 3)),
            ("closing", round(max(0.0, duration - 0.25), 3)),
        ]
    if not isinstance(raw, list) or len(raw) < 3:
        raise SourceAdaptiveShortCandidateError(
            "frame_samples require at least three rows"
        )
    result: list[tuple[str, float]] = []
    names: set[str] = set()
    for row in raw:
        if not isinstance(row, dict):
            raise SourceAdaptiveShortCandidateError("invalid frame sample row")
        label = str(row.get("label") or "")
        _safe_identifier(label, "frame sample label")
        seconds = _number(row.get("seconds"), "frame sample seconds")
        if label in names or seconds < 0 or seconds >= duration:
            raise SourceAdaptiveShortCandidateError("frame sample is outside candidate")
        names.add(label)
        result.append((label, seconds))
    return result


def _render_html(readback: dict[str, Any]) -> str:
    title = escape(str(readback["source_identity"]["title"]))
    question = escape(str(readback["review_question"]))
    sha = escape(str(readback["video"]["sha256"]))
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} candidate review</title></head>
<body><main><h1>{title}</h1><p>{question}</p>
<video id="candidate" controls muted preload="metadata" playsinline src="candidate.mp4"></video>
<p><code>{sha}</code></p></main>
<script>const v=document.getElementById('candidate');v.currentTime=0;v.muted=true;v.volume=0.25;</script>
</body></html>
"""


def _validate_staged_package(
    stage: Path, readback: dict[str, Any], manifest: dict[str, Any]
) -> None:
    required = {
        "candidate.mp4",
        "candidate_frame_qa.jpg",
        "candidate_navigation.jpg",
        "candidate_plan.json",
        "candidate_readback.json",
        "candidate_manifest.json",
        "index.html",
        "endpoint_evidence_manifest.json",
    }
    if readback["caption"]["mode"] == CAPTION_MODE_OVERLAY:
        required.update({"candidate_subtitles.ass", "candidate_subtitles.srt"})
    else:
        required.add("official_captions.json3")
    for name in required:
        _require_file(stage / name, f"staged package file {name}")
    if (stage / ".work").exists():
        raise SourceAdaptiveShortCandidateError("internal work directory remained")
    parsed_readback = _read_json(stage / "candidate_readback.json", "staged readback")
    if parsed_readback.get("video", {}).get("sha256") != _sha256(
        stage / "candidate.mp4"
    ):
        raise SourceAdaptiveShortCandidateError("candidate video SHA readback mismatch")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count("<video ") != 1 or "autoplay" in html.lower():
        raise SourceAdaptiveShortCandidateError("unsafe single-candidate review page")
    if manifest.get("file_count") != len(manifest.get("files") or []):
        raise SourceAdaptiveShortCandidateError("manifest file count mismatch")
    for row in manifest.get("files") or []:
        path = stage / str(row.get("package_relative_path") or "")
        _require_file(path, "manifest payload")
        if _sha256(path) != row.get("sha256") or path.stat().st_size != row.get(
            "byte_size"
        ):
            raise SourceAdaptiveShortCandidateError("manifest payload mismatch")
    if (manifest.get("manifest_self_integrity") or {}).get(
        "sha256"
    ) != _canonical_manifest_self_hash(manifest):
        raise SourceAdaptiveShortCandidateError("manifest self-integrity mismatch")


def _file_row(path: Path) -> dict[str, Any]:
    return {
        "package_relative_path": path.name,
        "sha256": _sha256(path),
        "byte_size": path.stat().st_size,
    }


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if output.parent != review:
        raise SourceAdaptiveShortCandidateError(
            "output directory must be a direct episode/review child"
        )
    if not output.name.startswith("out11_"):
        raise SourceAdaptiveShortCandidateError(
            "output directory name must start with out11_"
        )
    _safe_identifier(output.name, "output directory name")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceAdaptiveShortCandidateError(f"invalid {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SourceAdaptiveShortCandidateError(f"{label} must be an object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SourceAdaptiveShortCandidateError(f"{label} not found: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise SourceAdaptiveShortCandidateError(f"{label} not found: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise SourceAdaptiveShortCandidateError(
            f"{label} must stay within {parent}"
        ) from exc


def _safe_identifier(value: str, label: str) -> None:
    if not value or SAFE_ID.fullmatch(value) is None:
        raise SourceAdaptiveShortCandidateError(f"invalid {label}")


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SourceAdaptiveShortCandidateError(f"{label} must be numeric")
    return float(value)
