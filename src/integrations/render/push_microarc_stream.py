"""OUT-14 Push Micro-Arc profile for one completed public stream archive."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from src.integrations.render import editorial_video_candidate as out13
from src.integrations.render import ffmpeg_tiny
from src.integrations.render import real_video_pipeline as out12
from src.integrations.render.subtitle_preset_selector import select_subtitle_preset

SCHEMA_VERSION = "clippipegen.out14.push_microarc_stream.v1"
PLAN_SCHEMA_VERSION = "clippipegen.out14.push_microarc_plan.v1"
MANIFEST_SCHEMA_VERSION = "clippipegen.out14.run_manifest.v1"
PIPELINE_VERSION = "out14-push-microarc-stream-v1"
READY_STATE = "OUT14_PUSH_MICROARC_REAL_STREAM_READY_FOR_HUMAN_REVIEW"
ARTIFACT_ID_PATTERN = re.compile(r"^clip-out14-push-microarc-stream-v1-\d{3}$")
DEFAULT_REVIEW_PORT = 8078
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
NORMAL_MIN_OUTPUT_SECONDS = 300.0
NORMAL_MAX_OUTPUT_SECONDS = 900.0
EXCEPTION_MIN_OUTPUT_SECONDS = 240.0
EXCEPTION_MAX_OUTPUT_SECONDS = 1080.0
SEMANTIC_ROLES = (
    "hook_or_inciting_situation",
    "necessary_context",
    "development_or_escalation",
    "turn_payoff_or_resolution",
    "completing_aftermath",
)
GENERIC_SECTION_LABELS = frozenset({"まず見る", "ここでは", "展開", "結論"})


class PushMicroarcStreamError(Exception):
    """Raised when the OUT-14 profile cannot produce a reviewable package."""

    def __init__(self, message: str, *, stage: str = "unknown") -> None:
        super().__init__(message)
        self.stage = stage


def build_push_microarc_stream(
    *,
    artifact_id: str,
    source_path: Path,
    plan_path: Path,
    caption_track_path: Path,
    caption_receipt_path: Path,
    source_info_path: Path,
    source_receipt_path: Path,
    source_audio_receipt_path: Path,
    material_ledger_path: Path,
    rights_manifest_path: Path,
    output_dir: Path,
    source_identity: str,
    review_port: int = DEFAULT_REVIEW_PORT,
    resume: bool = False,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
) -> dict[str, Any]:
    """Build one chronology-preserving, closed micro-arc from one stream."""

    overall_started = time.monotonic()
    root = (base_dir or Path.cwd()).resolve()
    output = _resolved(root, output_dir)
    journal = out13._validated_run_journal_dir(output)
    stage: Path | None = None
    fingerprint: str | None = None
    current_stage = "source_resolution"
    timings: dict[str, float] = {}
    try:
        _validate_artifact_id(artifact_id)
        if not 1 <= int(review_port) <= 65535:
            raise PushMicroarcStreamError(
                "review port must be between 1 and 65535", stage=current_stage
            )
        tools = ffmpeg_tiny.preflight_tools(
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        if tools.get("status") != "passed":
            raise PushMicroarcStreamError(
                f"FFmpeg preflight failed: {tools.get('failure_reason')}",
                stage=current_stage,
            )
        ffmpeg = str(tools["ffmpeg"]["path"])
        ffprobe = str(tools["ffprobe"]["path"])

        source = _resolved(root, source_path)
        plan_file = _resolved(root, plan_path)
        caption_track = _resolved(root, caption_track_path)
        caption_receipt_file = _resolved(root, caption_receipt_path)
        source_info_file = _resolved(root, source_info_path)
        source_receipt_file = _resolved(root, source_receipt_path)
        source_audio_receipt_file = _resolved(root, source_audio_receipt_path)
        ledger_file = _resolved(root, material_ledger_path)
        rights_file = _resolved(root, rights_manifest_path)
        required_files = (
            source,
            plan_file,
            caption_track,
            caption_receipt_file,
            source_info_file,
            source_receipt_file,
            source_audio_receipt_file,
            ledger_file,
            rights_file,
        )
        if any(not path.is_file() for path in required_files):
            missing = [str(path) for path in required_files if not path.is_file()]
            raise PushMicroarcStreamError(
                f"required OUT-14 input missing: {missing}", stage=current_stage
            )
        plan = _read_json(plan_file, "OUT-14 plan")
        source_info = _read_json(source_info_file, "source info")
        caption_receipt = _read_json(caption_receipt_file, "caption receipt")
        source_receipt = _read_json(source_receipt_file, "source receipt")
        source_audio_receipt = _read_json(
            source_audio_receipt_file, "source audio receipt"
        )
        ledger = _read_json(ledger_file, "material ledger")
        rights = _read_json(rights_file, "rights manifest")

        source_started = time.monotonic()
        resolved = out12.resolve_source(
            root=root,
            source_path=source,
            intake_identity=None,
            source_identity=source_identity,
            rights_manifest_path=rights_file,
            caption_track_path=caption_track,
            authority_readback_path=None,
            caption_mode="sidecar",
        )
        source_probe = out12.probe_media_detail(
            resolved["source_path"], ffprobe_path=ffprobe, runner=runner
        )
        authority = validate_profile_authority(
            artifact_id=artifact_id,
            plan=plan,
            source_info=source_info,
            caption_receipt=caption_receipt,
            source_receipt=source_receipt,
            source_audio_receipt=source_audio_receipt,
            ledger=ledger,
            rights=rights,
            resolved=resolved,
            source_probe=source_probe,
            source_info_sha256=_sha256(source_info_file),
            caption_sha256=_sha256(caption_track),
            caption_receipt_sha256=_sha256(caption_receipt_file),
            source_receipt_sha256=_sha256(source_receipt_file),
            source_audio_receipt_sha256=_sha256(source_audio_receipt_file),
            material_ledger_sha256=_sha256(ledger_file),
            rights_sha256=_sha256(rights_file),
        )
        evidence_transcript = build_semantic_evidence_transcript(plan)
        all_caption_events = out12.load_caption_events(caption_track)
        selection = plan["selection"]
        selected_start = float(selection["source_in_seconds"])
        selected_end = float(selection["source_out_seconds"])
        caption_events = [
            row
            for row in all_caption_events
            if float(row["source_start_seconds"]) >= selected_start - 0.001
            and float(row["source_end_seconds"]) <= selected_end + 0.001
        ]
        if not caption_events:
            raise PushMicroarcStreamError(
                "selected micro-arc has no fully contained provider caption cues",
                stage=current_stage,
            )
        timeline = out13.build_editorial_timeline(
            plan=plan,
            source_identity=resolved["source_identity"],
            source_sha256=resolved["source_sha256"],
            source_duration_seconds=float(source_probe["duration_seconds"]),
            transcript=evidence_transcript,
            caption_events=caption_events,
            plan_schema_version=PLAN_SCHEMA_VERSION,
            profile_schema_version=SCHEMA_VERSION,
            min_output_seconds=EXCEPTION_MIN_OUTPUT_SECONDS,
            max_output_seconds=EXCEPTION_MAX_OUTPUT_SECONDS,
            min_selected_cuts=1,
            min_intentional_omitted_spans=2,
            max_source_utilization_ratio=0.5,
            min_semantic_section_count=1,
            selection_mode="push_microarc_closed_episode_chronological_v1",
        )
        profile_validation = validate_push_microarc_plan(
            plan=plan,
            timeline=timeline,
            source_info=source_info,
        )
        timings["source_resolution_and_plan_validation_seconds"] = round(
            time.monotonic() - source_started, 3
        )

        fingerprint_payload = {
            "artifact_id": artifact_id,
            "pipeline_version": PIPELINE_VERSION,
            "source_identity": resolved["source_identity"],
            "source_sha256": resolved["source_sha256"],
            "source_probe": source_probe,
            "plan_sha256": _sha256(plan_file),
            "caption_sha256": _sha256(caption_track),
            "caption_receipt_sha256": _sha256(caption_receipt_file),
            "source_info_sha256": _sha256(source_info_file),
            "source_receipt_sha256": _sha256(source_receipt_file),
            "source_audio_receipt_sha256": _sha256(source_audio_receipt_file),
            "material_ledger_sha256": _sha256(ledger_file),
            "rights_sha256": _sha256(rights_file),
            "review_port": int(review_port),
            "target_resolution": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
        }
        fingerprint = out12.content_fingerprint(fingerprint_payload)
        if resume:
            result = resume_existing_output(
                output_dir=output,
                artifact_id=artifact_id,
                input_fingerprint=fingerprint,
                run_journal_dir=journal,
            )
            result["elapsed_seconds"] = round(time.monotonic() - overall_started, 3)
            return result

        out13._validate_output_allocation(
            output=output, artifact_id=artifact_id, force=False
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        stage = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
        stage.mkdir()
        _write_json(stage / "editorial_plan.json", plan)
        _write_json(stage / "timeline_ir.json", timeline)
        _write_json(stage / "profile_contract_snapshot.json", profile_validation)
        _write_json(stage / "authority_binding.json", authority)
        _write_json(
            stage / "source_receipts.json",
            {
                "schema_version": SCHEMA_VERSION,
                "source_receipt": authority["source_receipt"],
                "source_audio_receipt": authority["source_audio_receipt"],
                "caption_receipt": {
                    "sha256": authority["caption"]["receipt_sha256"],
                    "provider": authority["caption"]["provider"],
                    "language": authority["caption"]["language"],
                    "classification": authority["caption"]["classification"],
                },
                "material_ledger": authority["material_ledger"],
                "source_info": authority["source_info"],
                "rights_snapshot": authority["rights"],
            },
        )
        _write_json(
            stage / "transcript_linkage.json",
            {
                "schema_version": SCHEMA_VERSION,
                "classification": (
                    "semantic_selection_evidence_not_verbatim_transcript"
                ),
                "provider_caption_classification": authority["caption"][
                    "classification"
                ],
                "provider_caption_authoritative_transcript_claim": False,
                "semantic_evidence_spans": plan["evidence_spans"],
                "cut_linkage": [
                    {
                        "cut_id": cut["cut_id"],
                        "evidence_span_ids": cut["direct_evidence_segment_ids"],
                        "provider_caption_event_ids": cut["eligible_caption_event_ids"],
                    }
                    for cut in timeline["cuts"]
                ],
            },
        )
        _write_json(
            stage / "creator_context_linkage.json",
            build_creator_context_linkage(plan),
        )
        metadata = build_metadata_draft(plan=plan, source_info=source_info)
        _write_json(stage / "metadata_draft.json", metadata)
        _write_json(
            stage / "provenance_snapshot.json",
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": artifact_id,
                "source_identity": resolved["source_identity"],
                "source_url": plan["source"]["url"],
                "source_title": plan["source"]["title"],
                "source_path": _display_path(resolved["source_path"], root),
                "source_sha256": resolved["source_sha256"],
                "source_byte_size": resolved["source_byte_size"],
                "source_probe": source_probe,
                "acquired_resolution": source_probe["resolution"],
                "output_resolution_contract": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
                "upscale_applied": (
                    int(source_probe["width"]) != TARGET_WIDTH
                    or int(source_probe["height"]) != TARGET_HEIGHT
                ),
                "caption_authority": authority["caption"],
                "creator_context": build_creator_context_linkage(plan),
                "rights": resolved["rights"],
                "closed_gates": _closed_gates(),
            },
        )

        current_stage = "caption_presentation"
        caption_started = time.monotonic()
        caption_rows = out12.remap_caption_events(caption_events, timeline["cuts"])
        out13._attach_caption_ids(timeline["cuts"], caption_rows)
        out12.validate_timeline_ir(timeline)
        _write_json(stage / "timeline_ir.json", timeline)
        caption_authority = {
            **authority["caption"],
            "overlay_burn_in_applied": True,
            "native_pixels_preserved": True,
            "provider_auto_caption_authoritative_transcript_claim": False,
        }
        caption_readback = out12.build_caption_readback(
            caption_mode="official_sidecar",
            caption_authority=caption_authority,
            caption_rows=caption_rows,
            source_caption_sha256=_sha256(caption_track),
            timeline_duration_seconds=float(timeline["output_duration_seconds"]),
        )
        caption_readback.update(
            {
                "schema_version": SCHEMA_VERSION,
                "provider_caption_quality_status": (
                    "automatic_asr_requires_human_language_review"
                ),
                "creator_context_count": 0,
                "identity_collision_count": 0,
                "provenance_collision_count": 0,
            }
        )
        _write_json(stage / "caption_readback.json", caption_readback)
        _write_text(stage / "captions.srt", out12.render_srt(caption_rows))
        style = out13._diagnostic_ass_style_for_candidate(
            out13.ED10L_KEIFONT_CANDIDATE_ID
        )
        font_file = Path(str(style.get("resolved_font_file") or ""))
        font_sha256 = _sha256(font_file) if font_file.is_file() else None
        layout = out13._editorial_subtitle_layout_contract(
            frame_width=TARGET_WIDTH,
            frame_height=TARGET_HEIGHT,
            dimension_source="out14_profile_output_resolution",
            diagnostic_ass_style=style,
        )
        raw_items = [
            {
                "subtitle_id": row["caption_id"],
                "cut_id": row["cut_id"],
                "status": "included",
                "render_start_seconds": row["output_start_seconds"],
                "render_end_seconds": row["output_end_seconds"],
                "text": out13._caption_text_for_presentation(row["text"]),
                "authority_text": row["text"],
                "source_type": authority["caption"]["classification"],
                "source_segment_ids": [span["id"] for span in plan["evidence_spans"]],
            }
            for row in caption_rows
        ]
        presentation_items = out13._presentation_items(raw_items, layout=layout)
        selector = select_subtitle_preset(
            {
                "speaker_id": "unknown",
                "speaker_role": "unknown",
                "emotion": "neutral",
                "intensity": 0,
                "utterance_role": "dialogue",
                "readability_priority": "maximum",
            }
        )
        subtitle_readback = out13.build_subtitle_presentation_readback(
            layout=layout,
            presentation_items=presentation_items,
            selector=selector,
            caption_readback=caption_readback,
            font_sha256=font_sha256,
        )
        subtitle_readback["schema_version"] = SCHEMA_VERSION
        subtitle_readback["source_caption_count"] = len(presentation_items)
        subtitle_readback["creator_context_count"] = 0
        subtitle_readback["presentation_identity_collision_count"] = 0
        _write_json(stage / "subtitle_presentation_readback.json", subtitle_readback)
        if subtitle_readback["status"] != "passed":
            raise PushMicroarcStreamError(
                "subtitle presentation validation failed",
                stage=current_stage,
            )
        ass_path = stage / "source_captions.ass"
        out13._write_ass(ass_path, presentation_items, layout=layout, review_label=None)
        timings["caption_presentation_seconds"] = round(
            time.monotonic() - caption_started, 3
        )

        current_stage = "render"
        render_started = time.monotonic()
        final_video = stage / "final_video.mp4"
        render = out13.render_editorial_timeline(
            source_path=resolved["source_path"],
            video_path=final_video,
            cuts=timeline["cuts"],
            ass_path=ass_path,
            font_file=font_file,
            ffmpeg_path=ffmpeg,
            runner=runner,
            output_width=TARGET_WIDTH,
            output_height=TARGET_HEIGHT,
        )
        timings["render_seconds"] = round(time.monotonic() - render_started, 3)

        current_stage = "media_validation"
        validation_started = time.monotonic()
        expected_output_probe = {
            **source_probe,
            "width": TARGET_WIDTH,
            "height": TARGET_HEIGHT,
            "resolution": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
        }
        validation = out12.validate_rendered_video(
            video_path=final_video,
            timeline=timeline,
            caption_readback=caption_readback,
            source_probe=expected_output_probe,
            ffmpeg_path=ffmpeg,
            ffprobe_path=ffprobe,
            runner=runner,
        )
        validation["schema_version"] = SCHEMA_VERSION
        validation["state"] = (
            READY_STATE
            if validation["status"] == "passed"
            else "OUT14_VALIDATION_FAILED"
        )
        validation["render"] = render
        validation["input_fingerprint"] = fingerprint
        validation["source_media"] = {
            "sha256": resolved["source_sha256"],
            "resolution": source_probe["resolution"],
            "duration_seconds": source_probe["duration_seconds"],
        }
        validation["output_resolution_contract"] = {
            "expected": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
            "actual": validation["media"]["resolution"],
            "upscale_from_source": source_probe["resolution"],
            "passed": validation["media"]["resolution"]
            == f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
        }
        validation["editorial_checks"] = {
            "profile_contract": profile_validation["status"] == "passed",
            "natural_duration_contract": profile_validation[
                "natural_duration_contract"
            ]["passed"],
            "chronology_preserved": timeline["chronology_preserved"],
            "single_source_mapping": all(
                cut["source_identity"] == resolved["source_identity"]
                for cut in timeline["cuts"]
            ),
            "semantic_arc_complete": len(plan["semantic_arc"]) == 5,
            "provider_caption_not_claimed_authoritative": not authority["caption"][
                "authoritative_transcript_claim"
            ],
            "creator_context_separated": caption_readback["identity_collision_count"]
            == 0,
            "subtitle_presentation": subtitle_readback["status"] == "passed",
            "metadata_source_first": metadata["checks"]["source_url_first"]
            and metadata["checks"]["source_title_second"],
        }
        if not all(validation["editorial_checks"].values()):
            validation["status"] = "failed"
        _write_json(stage / "validation_readback.json", validation)
        if validation["status"] != "passed":
            raise PushMicroarcStreamError(
                "rendered OUT-14 media validation failed", stage=current_stage
            )
        timings["media_validation_seconds"] = round(
            time.monotonic() - validation_started, 3
        )

        current_stage = "review_package"
        review_started = time.monotonic()
        review = out13.build_review_package(
            artifact_id=artifact_id,
            plan_sha256=_sha256(plan_file),
            stage=stage,
            timeline=timeline,
            resolved=resolved,
            validation=validation,
            subtitle_readback=subtitle_readback,
            source_probe=source_probe,
            review_port=int(review_port),
            ffmpeg_path=ffmpeg,
            runner=runner,
        )
        review_readback = build_review_readback(
            artifact_id=artifact_id,
            plan=plan,
            timeline=timeline,
            authority=authority,
            validation=validation,
            subtitle_readback=subtitle_readback,
            review=review,
        )
        _write_json(stage / "review" / "review_readback.json", review_readback)
        _write_text(
            stage / "review" / "index.html",
            render_review_html(
                plan=plan,
                timeline=timeline,
                authority=authority,
                validation=validation,
                subtitle_readback=subtitle_readback,
            ),
        )
        timings["review_package_seconds"] = round(time.monotonic() - review_started, 3)

        publication_time = datetime.fromtimestamp(
            float(source_info["release_timestamp"]), tz=timezone.utc
        )
        review_ready_time = datetime.now(timezone.utc)
        timings["pipeline_seconds_before_manifest"] = round(
            time.monotonic() - overall_started, 3
        )
        timings_payload = {
            "schema_version": SCHEMA_VERSION,
            "measured_stage_durations_seconds": timings,
            "external_acquisition_observations_seconds": plan[
                "acquisition_observations_seconds"
            ],
            "source_publication_time": publication_time.isoformat(),
            "review_ready_time": review_ready_time.isoformat(),
            "publication_to_review_ready_seconds": round(
                (review_ready_time - publication_time).total_seconds(), 3
            ),
        }
        _write_json(stage / "stage_timings.json", timings_payload)
        pipeline_state = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": artifact_id,
            "state": READY_STATE,
            "ready": True,
            "human_review_pending": True,
            "visual_editorial_acceptance_verified": False,
            "input_fingerprint": fingerprint,
            "source_identity": resolved["source_identity"],
            "source_sha256": resolved["source_sha256"],
            "final_video_sha256": validation["media"]["sha256"],
            "source_duration_seconds": source_probe["duration_seconds"],
            "output_duration_seconds": validation["media"]["duration_seconds"],
            "cut_count": timeline["cut_count"],
            "semantic_role_count": len(plan["semantic_arc"]),
            "creator_context_count": 0,
            "review_entrypoint": "review/index.html",
            "closed_gates": _closed_gates(),
        }
        _write_json(stage / "pipeline_state.json", pipeline_state)

        current_stage = "manifest"
        manifest = build_run_manifest(
            artifact_id=artifact_id,
            stage=stage,
            input_fingerprint=fingerprint,
            resolved=resolved,
            source_probe=source_probe,
            timeline=timeline,
            plan=plan,
            authority=authority,
            validation=validation,
            review=review,
            timings=timings_payload,
        )
        _write_json(stage / "run_manifest.json", manifest)
        validate_run_manifest(stage, manifest, expected_artifact_id=artifact_id)
        out13._promote_output_immutable(stage=stage, output=output)
        stage = None
        validate_run_manifest(output, manifest, expected_artifact_id=artifact_id)
        return {
            "artifact_id": artifact_id,
            "state": READY_STATE,
            "output_dir": output,
            "final_video": output / "final_video.mp4",
            "review_index": output / "review" / "index.html",
            "review_url": f"http://127.0.0.1:{review_port}/review/index.html",
            "open_command": str(output / "review" / "open_preview.ps1"),
            "source_identity": resolved["source_identity"],
            "source_sha256": resolved["source_sha256"],
            "source_duration_seconds": source_probe["duration_seconds"],
            "duration_seconds": validation["media"]["duration_seconds"],
            "cut_count": timeline["cut_count"],
            "semantic_role_count": len(plan["semantic_arc"]),
            "creator_context_count": 0,
            "video_sha256": validation["media"]["sha256"],
            "manifest_sha256": manifest["manifest_self_integrity"]["sha256"],
            "package_tree_digest": out13._package_tree_digest(output),
            "run_journal_dir": journal,
            "elapsed_seconds": round(time.monotonic() - overall_started, 3),
            "resume": False,
        }
    except Exception as exc:  # noqa: BLE001 - normalize dependency failures into a staged receipt
        if stage is not None and stage.exists():
            failure_dir = (
                journal / "failed_stages" / (f"{stage.name}-{uuid.uuid4().hex}")
            )
            failure_dir.parent.mkdir(parents=True, exist_ok=True)
            stage.replace(failure_dir)
        error = (
            exc
            if isinstance(exc, PushMicroarcStreamError)
            else PushMicroarcStreamError(str(exc), stage=current_stage)
        )
        try:
            journal.mkdir(parents=True, exist_ok=True)
            _write_json(
                journal / "pipeline_failure.json",
                {
                    "schema_version": SCHEMA_VERSION,
                    "artifact_id": artifact_id,
                    "state": "OUT14_PIPELINE_FAILED",
                    "failure_stage": error.stage,
                    "message": str(error),
                    "input_fingerprint": fingerprint,
                },
            )
        except OSError:
            pass
        raise error


def validate_profile_authority(
    *,
    artifact_id: str,
    plan: dict[str, Any],
    source_info: dict[str, Any],
    caption_receipt: dict[str, Any],
    source_receipt: dict[str, Any],
    source_audio_receipt: dict[str, Any],
    ledger: dict[str, Any],
    rights: dict[str, Any],
    resolved: dict[str, Any],
    source_probe: dict[str, Any],
    source_info_sha256: str,
    caption_sha256: str,
    caption_receipt_sha256: str,
    source_receipt_sha256: str,
    source_audio_receipt_sha256: str,
    material_ledger_sha256: str,
    rights_sha256: str,
) -> dict[str, Any]:
    binding = plan.get("authority_binding") or {}
    if plan.get("artifact_id") != artifact_id:
        raise PushMicroarcStreamError(
            "OUT-14 plan artifact identity mismatch", stage="source_resolution"
        )
    expected = {
        "source_sha256": resolved["source_sha256"],
        "caption_sha256": caption_sha256,
        "caption_receipt_sha256": caption_receipt_sha256,
        "source_info_sha256": source_info_sha256,
        "source_receipt_sha256": source_receipt_sha256,
        "source_audio_receipt_sha256": source_audio_receipt_sha256,
        "material_ledger_sha256": material_ledger_sha256,
        "rights_sha256": rights_sha256,
    }
    if any(binding.get(key) != value for key, value in expected.items()):
        raise PushMicroarcStreamError(
            "OUT-14 authority binding hash mismatch", stage="source_resolution"
        )
    provider_id = resolved["source_identity"].partition(":")[2]
    source_url = str(plan.get("source", {}).get("url") or "")
    if (
        resolved["source_identity"] != f"youtube:{source_info.get('id')}"
        or source_info.get("id") != provider_id
        or source_info.get("webpage_url") != source_url
        or source_info.get("live_status") != "was_live"
        or source_info.get("availability") != "public"
        or not bool(source_info.get("was_live"))
        or str(source_info.get("channel_id") or "")
        != str(plan.get("source", {}).get("channel_id") or "")
    ):
        raise PushMicroarcStreamError(
            "source info does not prove a completed public talent stream",
            stage="source_resolution",
        )
    if (
        caption_receipt.get("provider") != "youtube"
        or caption_receipt.get("provider_video_id") != provider_id
        or caption_receipt.get("source_url") != source_url
        or caption_receipt.get("language") != "ja-orig"
        or caption_receipt.get("format") != "json3"
        or caption_receipt.get("caption_sha256") != caption_sha256
        or caption_receipt.get("anonymous_access") is not True
        or caption_receipt.get("cookies_used") is not False
        or caption_receipt.get("oauth_used") is not False
        or caption_receipt.get("authoritative_transcript_claim") is not False
    ):
        raise PushMicroarcStreamError(
            "caption receipt does not bind anonymous provider-auto caption evidence",
            stage="source_resolution",
        )
    if any(
        phrase in str(source_info.get("title") or "").casefold()
        for phrase in ("members only", "メン限", "concert", "歌ってみた")
    ):
        raise PushMicroarcStreamError(
            "source title matches a restricted content class",
            stage="source_resolution",
        )
    if source_receipt.get("sha256") != resolved["source_sha256"]:
        raise PushMicroarcStreamError(
            "source receipt does not bind source bytes", stage="source_resolution"
        )
    if (
        float(source_info.get("duration") or 0.0) <= 0
        or abs(float(source_info["duration"]) - float(source_probe["duration_seconds"]))
        > 1.0
    ):
        raise PushMicroarcStreamError(
            "source info duration does not match acquired media",
            stage="source_resolution",
        )
    material_ids = {
        str(row.get("id")): row
        for row in ledger.get("materials") or []
        if isinstance(row, dict)
    }
    if (
        source_receipt.get("material_id") not in material_ids
        or source_audio_receipt.get("material_id") not in material_ids
    ):
        raise PushMicroarcStreamError(
            "material ledger is missing source video/audio receipt identities",
            stage="source_resolution",
        )
    rights_source = rights.get("source_video") or {}
    if (
        rights_source.get("url") != source_url
        or rights_source.get("vod_status") != "public"
        or rights_source.get("membership_only") is not False
        or rights_source.get("is_archived_live") is not True
    ):
        raise PushMicroarcStreamError(
            "rights readback does not match public archived stream class",
            stage="source_resolution",
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "artifact_id": artifact_id,
        **expected,
        "source_identity": resolved["source_identity"],
        "source_url": source_url,
        "source_title": source_info["title"],
        "provider": {
            "name": "youtube",
            "video_id": provider_id,
            "channel": source_info["channel"],
            "channel_id": source_info["channel_id"],
            "live_status": source_info["live_status"],
            "availability": source_info["availability"],
            "release_timestamp": source_info["release_timestamp"],
        },
        "content_class": "public_completed_talent_free_talk_stream_archive",
        "caption": {
            "provider": "youtube",
            "language": "ja-orig",
            "format": "json3",
            "classification": (
                "provider_automatic_caption_selection_evidence_not_authoritative"
            ),
            "sha256": caption_sha256,
            "receipt_sha256": caption_receipt_sha256,
            "authoritative_transcript_claim": False,
            "speaker_identity_claim": False,
        },
        "source_receipt": {
            "material_id": source_receipt["material_id"],
            "sha256": source_receipt_sha256,
            "source_media_sha256": source_receipt["sha256"],
            "mode": source_receipt["mode"],
        },
        "source_audio_receipt": {
            "material_id": source_audio_receipt["material_id"],
            "sha256": source_audio_receipt_sha256,
            "source_audio_sha256": source_audio_receipt["sha256"],
            "mode": source_audio_receipt["mode"],
        },
        "material_ledger": {"sha256": material_ledger_sha256},
        "source_info": {"sha256": source_info_sha256},
        "rights": {
            "sha256": rights_sha256,
            "status": (rights.get("compliance_check") or {}).get("status"),
            "approval_granted": False,
        },
    }


def build_semantic_evidence_transcript(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "segments": [
            {
                "id": row["id"],
                "start_seconds": row["source_in_seconds"],
                "end_seconds": row["source_out_seconds"],
                "text": row["summary"],
            }
            for row in plan.get("evidence_spans") or []
        ],
    }


def validate_push_microarc_plan(
    *,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    source_info: dict[str, Any],
) -> dict[str, Any]:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise PushMicroarcStreamError(
            "OUT-14 plan schema mismatch", stage="timeline_selection"
        )
    if plan.get("profile") != "PUSH_MICROARC":
        raise PushMicroarcStreamError(
            "OUT-14 plan profile must be PUSH_MICROARC",
            stage="timeline_selection",
        )
    _validate_artifact_id(str(plan.get("artifact_id") or ""))
    semantic_arc = plan.get("semantic_arc")
    if not isinstance(semantic_arc, list) or [
        row.get("role") for row in semantic_arc
    ] != list(SEMANTIC_ROLES):
        raise PushMicroarcStreamError(
            "semantic_arc must contain the five ordered micro-arc roles",
            stage="timeline_selection",
        )
    selection = plan.get("selection") or {}
    selected_start = float(selection.get("source_in_seconds") or 0.0)
    selected_end = float(selection.get("source_out_seconds") or 0.0)
    previous_end = selected_start
    for row in semantic_arc:
        start = float(row.get("source_in_seconds") or 0.0)
        end = float(row.get("source_out_seconds") or 0.0)
        if (
            start < selected_start - 0.001
            or end > selected_end + 0.001
            or start < previous_end - 0.001
            or end <= start
            or not str(row.get("summary") or "").strip()
        ):
            raise PushMicroarcStreamError(
                "semantic_arc ranges must be ordered inside the selected episode",
                stage="timeline_selection",
            )
        previous_end = end
    context = plan.get("creator_context") or {}
    if context.get("items") not in ([], None):
        raise PushMicroarcStreamError(
            "OUT-14 v1 source-self-explanatory run does not render creator context",
            stage="timeline_selection",
        )
    if not str(context.get("omission_reason") or "").strip():
        raise PushMicroarcStreamError(
            "creator_context omission requires an episode-specific reason",
            stage="timeline_selection",
        )
    rendered_labels = set(plan.get("rendered_section_labels") or [])
    if rendered_labels & GENERIC_SECTION_LABELS:
        raise PushMicroarcStreamError(
            "generic semantic section labels must not be rendered",
            stage="timeline_selection",
        )
    duration = float(timeline["output_duration_seconds"])
    natural_exception = plan.get("natural_duration_exception")
    normal_pass = NORMAL_MIN_OUTPUT_SECONDS <= duration <= NORMAL_MAX_OUTPUT_SECONDS
    exception_pass = (
        EXCEPTION_MIN_OUTPUT_SECONDS <= duration <= EXCEPTION_MAX_OUTPUT_SECONDS
        and isinstance(natural_exception, dict)
        and bool(str(natural_exception.get("reason") or "").strip())
    )
    if not normal_pass and not exception_pass:
        raise PushMicroarcStreamError(
            "micro-arc duration is outside the natural-duration contract",
            stage="timeline_selection",
        )
    if (
        plan.get("source", {}).get("title") != source_info.get("title")
        or plan.get("source", {}).get("publication_time")
        != datetime.fromtimestamp(
            float(source_info["release_timestamp"]), tz=timezone.utc
        ).isoformat()
    ):
        raise PushMicroarcStreamError(
            "plan source title/publication time mismatch",
            stage="timeline_selection",
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "profile": "PUSH_MICROARC",
        "delivery_lane_axis": plan.get("delivery_lane_axis"),
        "source_attribute_axes": plan.get("source_attributes"),
        "episode_premise": plan.get("episode_premise"),
        "semantic_roles": list(SEMANTIC_ROLES),
        "semantic_role_count": len(semantic_arc),
        "chronology_preserved": timeline["chronology_preserved"],
        "cut_count": timeline["cut_count"],
        "selected_ranges_non_overlapping": True,
        "omitted_ranges_non_overlapping": True,
        "creator_context_count": 0,
        "source_caption_creator_context_identity_collision_count": 0,
        "natural_duration_contract": {
            "normal_range_seconds": [300.0, 900.0],
            "exception_range_seconds": [240.0, 1080.0],
            "actual_seconds": duration,
            "exception_used": not normal_pass,
            "exception_reason": (
                natural_exception.get("reason") if not normal_pass else None
            ),
            "passed": normal_pass or exception_pass,
        },
        "human_review_pending": True,
    }


def build_creator_context_linkage(plan: dict[str, Any]) -> dict[str, Any]:
    context = plan.get("creator_context") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "source_caption_namespace": "source_caption:*",
        "creator_context_namespace": "creator_context:*",
        "creator_context_items": [],
        "creator_context_count": 0,
        "identity_collision_count": 0,
        "provenance_collision_count": 0,
        "presentation_collision_count": 0,
        "omission_reason": context.get("omission_reason"),
        "source_self_explanatory": True,
    }


def build_metadata_draft(
    *, plan: dict[str, Any], source_info: dict[str, Any]
) -> dict[str, Any]:
    source_url = str(plan["source"]["url"])
    source_title = str(plan["source"]["title"])
    description = (
        f"{source_url}\n{source_title}\n\n"
        "この動画は非公式の切り抜き・編集です。元配信および出演者による"
        "承認・推奨を示すものではありません。\n\n"
        f"編集内容: {plan['episode_premise']}"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "title": plan["metadata"]["draft_title"],
        "description": description,
        "source_url": source_url,
        "source_title": source_title,
        "provider_video_id": source_info["id"],
        "unofficial_clip_edit": True,
        "endorsement_claimed": False,
        "monetization_verdict": "not_evaluated",
        "publication_ready": False,
        "checks": {
            "source_url_first": description.splitlines()[0] == source_url,
            "source_title_second": description.splitlines()[1] == source_title,
            "unofficial_disclosure_present": "非公式の切り抜き・編集" in description,
            "no_endorsement_claim_present": "承認・推奨を示すものではありません"
            in description,
        },
    }


def build_review_readback(
    *,
    artifact_id: str,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    authority: dict[str, Any],
    validation: dict[str, Any],
    subtitle_readback: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "state": READY_STATE,
        "episode_premise": plan["episode_premise"],
        "semantic_arc": plan["semantic_arc"],
        "source_identity": authority["source_identity"],
        "source_url": authority["source_url"],
        "source_title": authority["source_title"],
        "source_sha256": authority["source_sha256"],
        "final_video_sha256": validation["media"]["sha256"],
        "output_duration_seconds": validation["media"]["duration_seconds"],
        "cut_count": timeline["cut_count"],
        "creator_context_count": 0,
        "source_caption_count": subtitle_readback["source_caption_count"],
        "caption_authority": authority["caption"],
        "review_assets": review,
        "human_review_pending": True,
        "visual_editorial_acceptance_verified": False,
        "decision_options": ["accept", "bounded_repair", "reject"],
        "closed_gates": _closed_gates(),
    }


def render_review_html(
    *,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    authority: dict[str, Any],
    validation: dict[str, Any],
    subtitle_readback: dict[str, Any],
) -> str:
    arc_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['role']))}</td>"
        f"<td>{float(row['source_in_seconds']):.3f}–"
        f"{float(row['source_out_seconds']):.3f}</td>"
        f"<td>{escape(str(row['summary']))}</td>"
        "</tr>"
        for row in plan["semantic_arc"]
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-14 Push Micro-Arc review</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#08101d;color:#e8eef8;font-family:system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:24px}}video{{display:block;width:100%;max-height:72vh;background:#000;border-radius:12px}}.hero,.note{{background:#111d31;border:1px solid #2d4265;border-radius:12px;padding:16px;margin-bottom:18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}}.metric{{background:#172640;padding:12px;border-radius:10px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #334155;text-align:left;vertical-align:top}}code{{overflow-wrap:anywhere}}img{{max-width:100%;height:auto}}.pending{{color:#f4c777}}@media(max-width:600px){{main{{padding:12px}}}}</style></head>
<body><main><section class="hero"><p>OUT-14 · PUSH MICRO-ARC</p><h1>{escape(str(plan["episode_premise"]))}</h1>
<video id="video" controls muted preload="metadata" playsinline src="../final_video.mp4"></video>
<div class="grid"><div class="metric">output<br><strong>{float(validation["media"]["duration_seconds"]):.3f}s</strong></div><div class="metric">media cuts<br><strong>{timeline["cut_count"]}</strong></div><div class="metric">semantic roles<br><strong>{len(plan["semantic_arc"])}</strong></div><div class="metric">source captions / creator context<br><strong>{subtitle_readback["source_caption_count"]} / 0</strong></div></div>
<p>artifact <code>{escape(str(plan["artifact_id"]))}</code><br>source <a href="{escape(authority["source_url"])}">{escape(authority["source_title"])}</a><br>source SHA <code>{escape(authority["source_sha256"])}</code><br>output SHA <code>{escape(validation["media"]["sha256"])}</code></p></section>
<section class="note"><strong>字幕の証拠区分</strong><p>表示字幕は YouTube の日本語自動字幕に由来し、選定証拠として保持しています。逐語的に正確な transcript、話者同定、公式著者字幕とは扱いません。creator-authored context は 0 件で、source caption と別 namespace のままです。</p></section>
<h2>Semantic arc</h2><table><thead><tr><th>role</th><th>source</th><th>editorial purpose</th></tr></thead><tbody>{arc_rows}</tbody></table>
<h2>確認してほしいこと</h2><ol><li>冒頭だけで出来事と話題が理解できるか</li><li>一話の流れが hook → context → development → payoff → aftermath と自然に閉じるか</li><li>自動字幕の誤りや二重表示、重要情報の遮蔽が判断を妨げないか</li><li>間・反応・音の切れ方に不自然さがないか</li></ol>
<details><summary>代表フレームと技術証拠</summary><p>単一連続区間のため internal cut boundary は 0 件です。boundary sheet は選定区間の開始・終了側を示します。</p><img src="evidence/source_selected_ranges_contact_sheet.jpg" alt="source frames"><img src="evidence/subtitle_presentation_contact_sheet.jpg" alt="subtitle frames"><img src="evidence/cut_boundary_contact_sheet.jpg" alt="single selected range endpoints"><img src="evidence/waveform.png" alt="waveform"></details>
<p class="pending">Human editorial review pending. Machine evidence proves construction, traceability, decode, mapping and media integrity only. It does not prove editorial quality, YPP eligibility, rights approval, production acceptance or publication readiness.</p>
</main><script>const v=document.getElementById('video');v.autoplay=false;v.muted=true;v.volume=.25;v.currentTime=0;</script></body></html>
"""


def build_run_manifest(
    *,
    artifact_id: str,
    stage: Path,
    input_fingerprint: str,
    resolved: dict[str, Any],
    source_probe: dict[str, Any],
    timeline: dict[str, Any],
    plan: dict[str, Any],
    authority: dict[str, Any],
    validation: dict[str, Any],
    review: dict[str, Any],
    timings: dict[str, Any],
) -> dict[str, Any]:
    out13._validate_payload_tree_no_links(stage)
    files = [
        {
            "repo_relative_path": path.relative_to(stage).as_posix(),
            "sha256": _sha256(path),
            "byte_size": path.stat().st_size,
        }
        for path in sorted(item for item in stage.rglob("*") if item.is_file())
        if path.relative_to(stage).as_posix() != "run_manifest.json"
    ]
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "state": READY_STATE,
        "input_fingerprint": input_fingerprint,
        "profile": {
            "id": "PUSH_MICROARC",
            "delivery_lane_axis": plan["delivery_lane_axis"],
            "source_attributes": plan["source_attributes"],
        },
        "source": {
            "identity": resolved["source_identity"],
            "url": authority["source_url"],
            "title": authority["source_title"],
            "sha256": resolved["source_sha256"],
            "byte_size": resolved["source_byte_size"],
            "duration_seconds": source_probe["duration_seconds"],
            "resolution": source_probe["resolution"],
            "content_class": authority["content_class"],
        },
        "editorial": {
            "episode_premise": plan["episode_premise"],
            "selection_mode": timeline["selection_mode"],
            "cut_count": timeline["cut_count"],
            "semantic_arc": plan["semantic_arc"],
            "omitted_ranges": timeline["omitted_ranges"],
            "source_utilization_ratio": timeline["source_utilization_ratio"],
        },
        "caption_and_context": {
            "caption_authority": authority["caption"],
            "source_caption_count": validation["caption_validation"].get(
                "cue_count",
                len(
                    _read_json(stage / "caption_readback.json", "caption").get("items")
                    or []
                ),
            ),
            "creator_context_count": 0,
            "identity_collision_count": 0,
        },
        "final_video": {
            "path": "final_video.mp4",
            "sha256": validation["media"]["sha256"],
            "byte_size": validation["media"]["byte_size"],
            "duration_seconds": validation["media"]["duration_seconds"],
            "resolution": validation["media"]["resolution"],
            "video_codec": validation["media"]["video_codec"],
            "audio_codec": validation["media"]["audio_codec"],
        },
        "validation_status": validation["status"],
        "review": review,
        "timings": timings,
        "files": files,
        "file_count": len(files),
        "closed_file_set": {
            "status": "passed",
            "excluded_paths": ["run_manifest.json"],
            "payload_tree_digest_sha256": out13._payload_tree_digest(files),
        },
        "human_review_pending": True,
        "visual_editorial_acceptance_verified": False,
        "closed_gates": _closed_gates(),
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    manifest["manifest_self_integrity"]["sha256"] = out13._manifest_self_hash(manifest)
    return manifest


def validate_run_manifest(
    stage: Path, manifest: dict[str, Any], *, expected_artifact_id: str
) -> None:
    out13._validate_payload_tree_no_links(stage)
    _validate_artifact_id(expected_artifact_id)
    if (
        manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION
        or manifest.get("artifact_id") != expected_artifact_id
        or manifest.get("state") != READY_STATE
    ):
        raise PushMicroarcStreamError(
            "OUT-14 run manifest identity mismatch", stage="manifest"
        )
    rows = manifest.get("files")
    if not isinstance(rows, list) or manifest.get("file_count") != len(rows):
        raise PushMicroarcStreamError(
            "OUT-14 run manifest file inventory invalid", stage="manifest"
        )
    declared: list[str] = []
    for row in rows:
        relative = out13._validated_manifest_path(row.get("repo_relative_path"))
        path = stage / relative
        if (
            not path.is_file()
            or path.stat().st_size != row.get("byte_size")
            or _sha256(path) != row.get("sha256")
        ):
            raise PushMicroarcStreamError(
                f"OUT-14 manifest payload mismatch: {relative}", stage="manifest"
            )
        declared.append(relative)
    actual = sorted(
        path.relative_to(stage).as_posix()
        for path in stage.rglob("*")
        if path.is_file() and path.relative_to(stage).as_posix() != "run_manifest.json"
    )
    if sorted(declared) != actual:
        raise PushMicroarcStreamError(
            "OUT-14 manifest closed file set mismatch", stage="manifest"
        )
    if manifest.get("closed_file_set", {}).get(
        "payload_tree_digest_sha256"
    ) != out13._payload_tree_digest(rows) or manifest.get(
        "manifest_self_integrity", {}
    ).get("sha256") != out13._manifest_self_hash(manifest):
        raise PushMicroarcStreamError(
            "OUT-14 manifest integrity mismatch", stage="manifest"
        )


def resume_existing_output(
    *,
    output_dir: Path,
    artifact_id: str,
    input_fingerprint: str,
    run_journal_dir: Path,
) -> dict[str, Any]:
    manifest_path = output_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise PushMicroarcStreamError(
            "resume requires a successful OUT-14 manifest",
            stage="source_resolution",
        )
    before = out13._package_tree_digest(output_dir)
    manifest = _read_json(manifest_path, "OUT-14 manifest")
    if manifest.get("input_fingerprint") != input_fingerprint:
        raise PushMicroarcStreamError(
            "resume fingerprint mismatch", stage="source_resolution"
        )
    validate_run_manifest(output_dir, manifest, expected_artifact_id=artifact_id)
    after = out13._package_tree_digest(output_dir)
    if before != after:
        raise PushMicroarcStreamError(
            "resume changed successful package bytes", stage="source_resolution"
        )
    run_journal_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        run_journal_dir / "resume_readback.json",
        {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": artifact_id,
            "state": READY_STATE,
            "render_executed": False,
            "cache_hits": [
                "plan",
                "caption_presentation",
                "render",
                "media_validation",
                "review_package",
            ],
            "package_tree_digest_before": before,
            "package_tree_digest_after": after,
            "package_tree_unchanged": True,
        },
    )
    return {
        "artifact_id": artifact_id,
        "state": READY_STATE,
        "output_dir": output_dir,
        "final_video": output_dir / "final_video.mp4",
        "review_index": output_dir / "review" / "index.html",
        "review_url": manifest["review"]["clean_url"],
        "open_command": str(output_dir / "review" / "open_preview.ps1"),
        "source_identity": manifest["source"]["identity"],
        "source_sha256": manifest["source"]["sha256"],
        "source_duration_seconds": manifest["source"]["duration_seconds"],
        "duration_seconds": manifest["final_video"]["duration_seconds"],
        "cut_count": manifest["editorial"]["cut_count"],
        "semantic_role_count": len(manifest["editorial"]["semantic_arc"]),
        "creator_context_count": 0,
        "video_sha256": manifest["final_video"]["sha256"],
        "manifest_sha256": manifest["manifest_self_integrity"]["sha256"],
        "package_tree_digest": after,
        "run_journal_dir": run_journal_dir,
        "resume": True,
    }


def _validate_artifact_id(artifact_id: str) -> None:
    if not ARTIFACT_ID_PATTERN.fullmatch(str(artifact_id or "")):
        raise PushMicroarcStreamError(
            "artifact identity must match clip-out14-push-microarc-stream-v1-NNN",
            stage="source_resolution",
        )


def _closed_gates() -> dict[str, Any]:
    return {
        "human_review_pending": True,
        "editorial_acceptance_verified": False,
        "rights_approval": False,
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "ypp_eligibility": "not_evaluated",
        "thumbnail_generated": False,
        "shorts_derivative_generated": False,
        "public_or_publishing_acceptance": False,
        "upload_attempted": False,
        "visibility_changed": False,
    }


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PushMicroarcStreamError(
            f"invalid {label}: {exc}", stage="source_resolution"
        ) from exc
    if not isinstance(payload, dict):
        raise PushMicroarcStreamError(
            f"{label} must be an object", stage="source_resolution"
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")
