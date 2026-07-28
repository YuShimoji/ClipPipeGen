"""Build a private, evidence-linked multi-source comparison artifact."""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny

PLAN_SCHEMA_VERSION = "clippipegen.s2.evidence_linked_comparison_plan.v1"
DIRECTION_SCHEMA_VERSION = "clippipegen.s2.evidence_linked_comparison_direction.v1"
MANIFEST_SCHEMA_VERSION = "clippipegen.s2.evidence_linked_comparison_manifest.v1"
TIMELINE_SCHEMA_VERSION = "clippipegen.s2.evidence_linked_comparison_timeline.v1"
TRANSCRIPT_SCHEMA_VERSION = (
    "clippipegen.s2.evidence_linked_comparison_transcript_context.v1"
)
PROVENANCE_SCHEMA_VERSION = (
    "clippipegen.s2.evidence_linked_comparison_provenance.v1"
)
MEDIA_SCHEMA_VERSION = "clippipegen.s2.evidence_linked_comparison_media_readback.v1"
READY_STATE = "EVIDENCE_LINKED_MULTI_SOURCE_COMPARISON_ARTIFACT_READY_FOR_HUMAN_REVIEW"
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
OUTPUT_FPS = 30
DEFAULT_REVIEW_PORT = 8082
COMMAND_TIMEOUT_SECONDS = 60 * 60
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_ID_RE = re.compile(r"^clip-[a-z0-9][a-z0-9-]+-v[0-9]+-[0-9]{3}$")
ABSOLUTE_PATH_RE = re.compile(r"(?:[A-Za-z]:[\\/]|\\\\\?\\)")
LOCATOR_NAMES = (
    "media",
    "fetch_receipt",
    "material_ledger",
    "provider_metadata",
    "caption",
    "processing_snapshot",
    "identity_binding",
)
REQUIRED_EXCLUSIONS = {
    "tts",
    "ai_imagery",
    "decorative_diagrams",
    "new_music",
    "promotional_packaging",
    "calls_to_action",
}


class EvidenceLinkedComparisonError(RuntimeError):
    """Fail-closed comparison build error with a stable stage label."""

    def __init__(self, message: str, *, stage: str) -> None:
        super().__init__(message)
        self.stage = stage


def build_evidence_linked_comparison(
    *,
    plan_path: Path,
    direction_path: Path,
    output_dir: Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    review_port: int = DEFAULT_REVIEW_PORT,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Build one immutable private comparison package from local source evidence."""

    root = (base_dir or Path.cwd()).resolve()
    plan_file = _resolved(root, plan_path)
    direction_file = _resolved(root, direction_path)
    output = _resolved(root, output_dir)
    if output.exists():
        raise EvidenceLinkedComparisonError(
            f"output directory already exists: {_display_path(root, output)}",
            stage="output_allocation",
        )
    if not 1 <= int(review_port) <= 65535:
        raise EvidenceLinkedComparisonError(
            "review port must be between 1 and 65535",
            stage="preflight",
        )
    if not plan_file.is_file() or not direction_file.is_file():
        raise EvidenceLinkedComparisonError(
            "plan and predeclared direction must exist",
            stage="preflight",
        )

    tools = ffmpeg_tiny.preflight_tools(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )
    if tools.get("status") != "passed":
        raise EvidenceLinkedComparisonError(
            "FFmpeg/FFprobe preflight failed",
            stage="preflight",
        )
    ffmpeg = str(tools["ffmpeg"]["path"])
    ffprobe = str(tools["ffprobe"]["path"])

    direction = _read_json(direction_file, "predeclared direction")
    plan = _read_json(plan_file, "comparison plan")
    validate_direction(direction)
    validate_comparison_plan(
        plan,
        direction=direction,
        direction_sha256=_sha256(direction_file),
    )
    source_bindings = bind_source_inputs(
        plan=plan,
        root=root,
        ffprobe_path=ffprobe,
    )
    transcript_context = build_transcript_context(
        plan=plan,
        source_bindings=source_bindings,
    )
    timeline = build_comparison_timeline(
        plan=plan,
        source_bindings=source_bindings,
    )
    overlay_ass = render_ass_overlay(
        direction=direction,
        plan=plan,
        timeline=timeline,
        transcript_context=transcript_context,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    stage.mkdir(parents=False, exist_ok=False)
    try:
        emitted_direction = json.loads(json.dumps(direction))
        emitted_direction["source_sha256"] = _sha256(direction_file)
        emitted_plan = json.loads(json.dumps(plan))
        emitted_plan["source_sha256"] = _sha256(plan_file)
        _write_json(stage / "predeclared_direction.json", emitted_direction)
        _write_json(stage / "paired_evidence_plan.json", emitted_plan)
        _write_json(stage / "comparison_timeline.json", timeline)
        _write_json(stage / "transcript_context.json", transcript_context)
        _write_json(
            stage / "provenance_snapshot.json",
            build_provenance_snapshot(
                plan=plan,
                source_bindings=source_bindings,
                transcript_context=transcript_context,
            ),
        )

        ass_path = stage / ".comparison_overlay.ass"
        filter_path = stage / ".comparison_filter.txt"
        _write_text(ass_path, overlay_ass)
        _write_text(
            filter_path,
            render_filter_complex(
                timeline=timeline,
                source_bindings=source_bindings,
                ass_path=ass_path,
            ),
        )
        final_video = stage / "final_video.mp4"
        render_video(
            final_video=final_video,
            filter_path=filter_path,
            source_bindings=source_bindings,
            ffmpeg_path=ffmpeg,
        )
        media_readback = validate_rendered_comparison(
            final_video=final_video,
            plan=plan,
            direction=direction,
            timeline=timeline,
            source_bindings=source_bindings,
            ffmpeg_path=ffmpeg,
            ffprobe_path=ffprobe,
        )
        _write_json(stage / "media_readback.json", media_readback)
        _write_json(
            stage / "render_inspection_targets.json",
            {
                "schema_version": (
                    "clippipegen.s2.evidence_linked_comparison_inspection_targets.v1"
                ),
                "artifact_id": plan["artifact_id"],
                "silent_inspection_required": True,
                "targets": timeline["inspection_targets"],
            },
        )
        build_contact_sheet(
            final_video=final_video,
            timeline=timeline,
            output_path=(
                stage / "review" / "evidence" / "comparison_contact_sheet.jpg"
            ),
            ffmpeg_path=ffmpeg,
        )
        build_review_package(
            stage=stage,
            direction=direction,
            plan=plan,
            timeline=timeline,
            transcript_context=transcript_context,
            media_readback=media_readback,
            review_port=review_port,
        )
        ass_path.unlink()
        filter_path.unlink()
        manifest = build_run_manifest(
            stage=stage,
            plan=plan,
            timeline=timeline,
            media_readback=media_readback,
        )
        _write_json(stage / "run_manifest.json", manifest)
        validate_run_manifest(stage)
        stage.replace(output)
    except Exception:  # noqa: TRY203
        # Keep a failed mission-owned staging directory for cause-bounded inspection.
        raise

    return {
        "artifact_id": plan["artifact_id"],
        "state": READY_STATE,
        "output_dir": output,
        "final_video": output / "final_video.mp4",
        "review_index": output / "review" / "index.html",
        "duration_seconds": media_readback["duration_seconds"],
        "final_video_sha256": media_readback["sha256"],
        "beat_count": timeline["beat_count"],
        "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
        "review_port": review_port,
    }


def validate_direction(direction: dict[str, Any]) -> None:
    if direction.get("schema_version") != DIRECTION_SCHEMA_VERSION:
        raise EvidenceLinkedComparisonError(
            "unsupported direction schema",
            stage="direction_validation",
        )
    artifact_id = str(direction.get("artifact_id") or "")
    if not ARTIFACT_ID_RE.fullmatch(artifact_id):
        raise EvidenceLinkedComparisonError(
            "direction requires a versioned artifact_id",
            stage="direction_validation",
        )
    for key in (
        "subject_line",
        "date_line",
        "comparison_question",
        "thesis",
        "viewer_benefit",
    ):
        if not str(direction.get(key) or "").strip():
            raise EvidenceLinkedComparisonError(
                f"direction is missing {key}",
                stage="direction_validation",
            )
    source_dates = direction.get("source_dates")
    if (
        not isinstance(source_dates, list)
        or not 2 <= len(source_dates) <= 3
        or len({str(value) for value in source_dates}) != len(source_dates)
    ):
        raise EvidenceLinkedComparisonError(
            "direction must declare two or three distinct source dates",
            stage="direction_validation",
        )
    if (
        direction.get("private_review_only") is not True
        or direction.get("human_review_pending") is not True
    ):
        raise EvidenceLinkedComparisonError(
            "direction cannot bypass private human review",
            stage="direction_validation",
        )


def validate_comparison_plan(
    plan: dict[str, Any],
    *,
    direction: dict[str, Any],
    direction_sha256: str,
) -> None:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise EvidenceLinkedComparisonError(
            "unsupported comparison plan schema",
            stage="plan_validation",
        )
    artifact_id = str(plan.get("artifact_id") or "")
    if (
        not ARTIFACT_ID_RE.fullmatch(artifact_id)
        or artifact_id != direction["artifact_id"]
    ):
        raise EvidenceLinkedComparisonError(
            "plan artifact_id must match the direction",
            stage="plan_validation",
        )
    if plan.get("predeclared_direction_sha256") != direction_sha256:
        raise EvidenceLinkedComparisonError(
            "plan is not bound to the predeclared direction",
            stage="plan_validation",
        )
    title_duration = float(plan.get("title_duration_seconds") or 0)
    transition_duration = float(plan.get("transition_duration_seconds") or 0)
    if not 5.0 <= title_duration <= 10.0:
        raise EvidenceLinkedComparisonError(
            "title duration must be 5-10 seconds",
            stage="plan_validation",
        )
    if not 2.0 <= transition_duration <= 4.0:
        raise EvidenceLinkedComparisonError(
            "transition duration must be 2-4 seconds",
            stage="plan_validation",
        )

    sources = plan.get("sources")
    if not isinstance(sources, list) or not 2 <= len(sources) <= 3:
        raise EvidenceLinkedComparisonError(
            "comparison IR requires two or three source records",
            stage="plan_validation",
        )
    source_by_id: dict[str, dict[str, Any]] = {}
    identities: set[str] = set()
    dates: set[str] = set()
    for source in sources:
        source_id = str(source.get("source_id") or "")
        source_identity = str(source.get("source_identity") or "")
        archive_date = str(source.get("archive_date") or "")
        if (
            not source_id
            or source_id in source_by_id
            or not source_identity
            or source_identity in identities
            or not archive_date
            or archive_date in dates
        ):
            raise EvidenceLinkedComparisonError(
                "source IDs, identities and dates must be distinct and non-empty",
                stage="plan_validation",
            )
        if not str(source.get("member") or "").strip():
            raise EvidenceLinkedComparisonError(
                f"source member is missing: {source_id}",
                stage="plan_validation",
            )
        source_by_id[source_id] = source
        identities.add(source_identity)
        dates.add(archive_date)
        media_duration = float((source.get("media") or {}).get("duration_seconds") or 0)
        if media_duration <= 0:
            raise EvidenceLinkedComparisonError(
                f"source duration is missing: {source_id}",
                stage="plan_validation",
            )
        for locator_name in LOCATOR_NAMES:
            locator = source.get(locator_name) or {}
            locator_path = str(locator.get("path") or "")
            if (
                not locator_path
                or Path(locator_path).is_absolute()
                or ABSOLUTE_PATH_RE.search(locator_path)
                or not SHA256_RE.fullmatch(str(locator.get("sha256") or ""))
            ):
                raise EvidenceLinkedComparisonError(
                    f"{source_id} {locator_name} needs a relative path and SHA-256",
                    stage="plan_validation",
                )
        snapshot = source["processing_snapshot"]
        if (
            snapshot.get("user_granted_processing_scope")
            != "local_private_review_only"
            or snapshot.get("underlying_rights_status")
            != "pending_or_unverified"
            or snapshot.get("public_use") != "not_authorized"
            or snapshot.get("monetized_use") != "not_authorized"
            or snapshot.get("rights_clearance") is not False
            or snapshot.get("rights_approval") is not False
        ):
            raise EvidenceLinkedComparisonError(
                f"source processing boundary is incomplete: {source_id}",
                stage="plan_validation",
            )

    if {str(value) for value in direction["source_dates"]} != dates:
        raise EvidenceLinkedComparisonError(
            "direction dates do not match the bound sources",
            stage="plan_validation",
        )

    beats = plan.get("comparison_beats")
    if not isinstance(beats, list) or not beats:
        raise EvidenceLinkedComparisonError(
            "comparison plan requires evidence-backed beats",
            stage="plan_validation",
        )
    seen_beat_ids: set[str] = set()
    previous_active_audio = ""
    for beat_index, beat in enumerate(beats):
        beat_id = str(beat.get("beat_id") or "")
        if not beat_id or beat_id in seen_beat_ids:
            raise EvidenceLinkedComparisonError(
                "comparison beat IDs must be unique and non-empty",
                stage="plan_validation",
            )
        seen_beat_ids.add(beat_id)
        for key in (
            "proposition",
            "why_informative",
            "transition_label",
            "transition_kind",
        ):
            if not str(beat.get(key) or "").strip():
                raise EvidenceLinkedComparisonError(
                    f"beat {beat_id} is missing {key}",
                    stage="plan_validation",
                )
        evidence = beat.get("evidence")
        if not isinstance(evidence, list) or not 2 <= len(evidence) <= 3:
            raise EvidenceLinkedComparisonError(
                f"beat {beat_id} needs two or three evidence bindings",
                stage="plan_validation",
            )
        bound_source_ids: set[str] = set()
        roles: list[str] = []
        foreground: list[str] = []
        for row in evidence:
            source_id = str(row.get("source_id") or "")
            source = source_by_id.get(source_id)
            if source is None or source_id in bound_source_ids:
                raise EvidenceLinkedComparisonError(
                    f"beat {beat_id} contains unbound or duplicate evidence",
                    stage="plan_validation",
                )
            bound_source_ids.add(source_id)
            role = str(row.get("role") or "")
            roles.append(role)
            if role not in {"primary_quote", "paired_evidence"}:
                raise EvidenceLinkedComparisonError(
                    f"beat {beat_id} has an unsupported evidence role",
                    stage="plan_validation",
                )
            source_in = float(row.get("source_in") or 0)
            source_out = float(row.get("source_out") or 0)
            source_duration = float(source["media"]["duration_seconds"])
            if (
                source_in < 0
                or source_out <= source_in
                or source_out > source_duration + 0.05
            ):
                raise EvidenceLinkedComparisonError(
                    f"beat {beat_id} has an invalid source range",
                    stage="plan_validation",
                )
            expected_label = _canonical_source_label(source)
            if row.get("visible_source_label") != expected_label:
                raise EvidenceLinkedComparisonError(
                    f"beat {beat_id} source label does not match its binding",
                    stage="plan_validation",
                )
            audio_mode = row.get("audio_mode")
            if audio_mode not in {"foreground", "muted_reference"}:
                raise EvidenceLinkedComparisonError(
                    f"beat {beat_id} has an invalid audio mode",
                    stage="plan_validation",
                )
            if audio_mode == "foreground":
                foreground.append(source_id)
        if roles.count("primary_quote") != 1 or roles.count("paired_evidence") < 1:
            raise EvidenceLinkedComparisonError(
                f"beat {beat_id} needs one primary quote and paired evidence",
                stage="plan_validation",
            )
        active_audio = str(beat.get("active_audio_source_id") or "")
        if foreground != [active_audio]:
            raise EvidenceLinkedComparisonError(
                f"beat {beat_id} must have exactly one foreground audio owner",
                stage="plan_validation",
            )
        if (
            beat_index
            and previous_active_audio != active_audio
            and beat.get("transition_kind") != "comparison_proposition_change"
        ):
            raise EvidenceLinkedComparisonError(
                f"beat {beat_id} changes audio owner without a marked transition",
                stage="plan_validation",
            )
        previous_active_audio = active_audio

    if not REQUIRED_EXCLUSIONS.issubset(set(plan.get("excluded_assets") or [])):
        raise EvidenceLinkedComparisonError(
            "excluded asset boundary is incomplete",
            stage="plan_validation",
        )
    labels = plan.get("review_labels") or {}
    if (
        labels.get("private_review_only") is not True
        or labels.get("human_review_pending") is not True
        or labels.get("rights_approval") != "not_granted"
        or labels.get("production_approval") is not False
        or labels.get("public_use") is not False
        or labels.get("monetized_use") is not False
        or labels.get("publication_approval") is not False
        or labels.get("upload_attempted") is not False
    ):
        raise EvidenceLinkedComparisonError(
            "comparison plan cannot open closed review gates",
            stage="plan_validation",
        )


def bind_source_inputs(
    *,
    plan: dict[str, Any],
    root: Path,
    ffprobe_path: str,
) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for index, source in enumerate(plan["sources"]):
        resolved_locators: dict[str, dict[str, Any]] = {}
        for locator_name in LOCATOR_NAMES:
            locator = source[locator_name]
            path = _resolved(root, Path(locator["path"]))
            if not path.is_file():
                raise EvidenceLinkedComparisonError(
                    f"source locator is missing: {locator_name} / {locator['path']}",
                    stage="source_binding",
                )
            actual_hash = _sha256(path)
            if actual_hash != locator["sha256"]:
                raise EvidenceLinkedComparisonError(
                    f"source locator hash mismatch: {locator_name} / {locator['path']}",
                    stage="source_binding",
                )
            resolved_locators[locator_name] = {
                "path": path,
                "relative_path": locator["path"],
                "sha256": actual_hash,
            }

        snapshot = _read_json(
            resolved_locators["processing_snapshot"]["path"],
            "processing snapshot",
        )
        if (
            snapshot.get("source_identity") != source["source_identity"]
            or snapshot.get("user_granted_processing_scope")
            != "local_private_review_only"
            or snapshot.get("underlying_rights_status")
            != "pending_or_unverified"
            or snapshot.get("public_use") != "not_authorized"
            or snapshot.get("monetized_use") != "not_authorized"
            or snapshot.get("rights_clearance") is not False
            or snapshot.get("rights_approval") is not False
        ):
            raise EvidenceLinkedComparisonError(
                f"processing snapshot mismatch: {source['source_id']}",
                stage="source_binding",
            )
        identity_binding = _read_json(
            resolved_locators["identity_binding"]["path"],
            "source identity binding",
        )
        if (
            identity_binding.get("source_identity") != source["source_identity"]
            or identity_binding.get("media_sha256")
            != resolved_locators["media"]["sha256"]
            or identity_binding.get("fetch_receipt_sha256")
            != resolved_locators["fetch_receipt"]["sha256"]
            or identity_binding.get("material_ledger_sha256")
            != resolved_locators["material_ledger"]["sha256"]
        ):
            raise EvidenceLinkedComparisonError(
                f"source identity binding mismatch: {source['source_id']}",
                stage="source_binding",
            )
        provider_metadata = _read_json(
            resolved_locators["provider_metadata"]["path"],
            "provider metadata",
        )
        if (
            provider_metadata.get("id")
            != str(source["source_identity"]).removeprefix("youtube:")
            or provider_metadata.get("upload_date")
            != str(source["archive_date"]).replace("-", "")
            or provider_metadata.get("channel")
            != str(source.get("provider_channel") or "")
            or provider_metadata.get("was_live") is not True
        ):
            raise EvidenceLinkedComparisonError(
                f"provider metadata mismatch: {source['source_id']}",
                stage="source_binding",
            )
        probe = ffmpeg_tiny.probe_media(
            input_path=resolved_locators["media"]["path"],
            ffprobe_path=ffprobe_path,
        ).metadata
        duration = float(probe.get("duration_seconds") or 0)
        if abs(duration - float(source["media"]["duration_seconds"])) > 0.2:
            raise EvidenceLinkedComparisonError(
                f"source duration mismatch: {source['source_id']}",
                stage="source_binding",
            )
        if (
            int((probe.get("stream_counts") or {}).get("video") or 0) != 1
            or int((probe.get("stream_counts") or {}).get("audio") or 0) != 1
        ):
            raise EvidenceLinkedComparisonError(
                f"source needs one video and one audio stream: {source['source_id']}",
                stage="source_binding",
            )
        bindings.append(
            {
                "index": index,
                "source_id": source["source_id"],
                "source_identity": source["source_identity"],
                "archive_date": source["archive_date"],
                "member": source["member"],
                "locators": resolved_locators,
                "processing_snapshot": snapshot,
                "media_metadata": probe,
            }
        )
    return bindings


def build_transcript_context(
    *,
    plan: dict[str, Any],
    source_bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    rows_by_source = {
        binding["source_id"]: _json3_caption_rows(
            _read_json(
                binding["locators"]["caption"]["path"],
                "provider caption",
            )
        )
        for binding in source_bindings
    }
    beat_rows: list[dict[str, Any]] = []
    for beat in plan["comparison_beats"]:
        evidence_rows: list[dict[str, Any]] = []
        for evidence in beat["evidence"]:
            source_in = float(evidence["source_in"])
            source_out = float(evidence["source_out"])
            caption_rows = rows_by_source[evidence["source_id"]]
            selected = _overlapping_caption_rows(
                caption_rows,
                source_in,
                source_out,
            )
            if not selected:
                raise EvidenceLinkedComparisonError(
                    f"no transcript evidence for {beat['beat_id']} / "
                    f"{evidence['source_id']}",
                    stage="transcript_context",
                )
            evidence_rows.append(
                {
                    "role": evidence["role"],
                    "source_id": evidence["source_id"],
                    "source_range": [source_in, source_out],
                    "audio_mode": evidence["audio_mode"],
                    "visible_source_label": evidence["visible_source_label"],
                    "before_context": _overlapping_caption_rows(
                        caption_rows,
                        max(0.0, source_in - 8.0),
                        source_in,
                    )[-4:],
                    "selected_cues": selected,
                    "after_context": _overlapping_caption_rows(
                        caption_rows,
                        source_out,
                        source_out + 8.0,
                    )[:4],
                    "selected_text": " ".join(
                        str(row.get("text") or "") for row in selected
                    ).strip(),
                }
            )
        beat_rows.append(
            {
                "beat_id": beat["beat_id"],
                "proposition": beat["proposition"],
                "why_informative": beat["why_informative"],
                "active_audio_source_id": beat["active_audio_source_id"],
                "evidence": evidence_rows,
            }
        )
    return {
        "schema_version": TRANSCRIPT_SCHEMA_VERSION,
        "artifact_id": plan["artifact_id"],
        "provider_caption_class": "youtube_auto_caption_json3",
        "official_authorship_claimed": False,
        "beats": beat_rows,
    }


def build_comparison_timeline(
    *,
    plan: dict[str, Any],
    source_bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    source_by_id = {row["source_id"]: row for row in plan["sources"]}
    metadata_by_id = {
        row["source_id"]: row["media_metadata"] for row in source_bindings
    }
    cursor = 0.0
    events: list[dict[str, Any]] = []
    first_evidence = plan["comparison_beats"][0]["evidence"]
    first_layout = _layout_for_evidence(first_evidence, metadata_by_id)
    title_duration = float(plan["title_duration_seconds"])
    events.append(
        {
            "event_id": "opening",
            "event_type": "opening",
            "output_in": cursor,
            "output_out": cursor + title_duration,
            "duration_seconds": title_duration,
            "evidence": first_evidence,
            "layout": first_layout,
            "active_audio_source_id": None,
        }
    )
    cursor += title_duration

    beat_events: list[dict[str, Any]] = []
    inspection_targets = [
        {
            "target_id": "opening_thesis",
            "event_type": "opening",
            "time_seconds": round(min(2.0, title_duration / 2), 3),
            "expected_visible_text": plan["comparison_beats"][0]["proposition"],
        }
    ]
    transition_duration = float(plan["transition_duration_seconds"])
    for beat_index, beat in enumerate(plan["comparison_beats"]):
        active = next(
            row
            for row in beat["evidence"]
            if row["source_id"] == beat["active_audio_source_id"]
        )
        beat_duration = float(active["source_out"]) - float(active["source_in"])
        layout = _layout_for_evidence(beat["evidence"], metadata_by_id)
        transition = {
            "event_id": f"transition_{beat_index + 1:03d}",
            "event_type": "comparison_transition",
            "beat_id": beat["beat_id"],
            "output_in": cursor,
            "output_out": cursor + transition_duration,
            "duration_seconds": transition_duration,
            "evidence": beat["evidence"],
            "layout": layout,
            "transition_label": beat["transition_label"],
            "proposition": beat["proposition"],
            "why_informative": beat["why_informative"],
            "active_audio_source_id": None,
            "next_active_audio_source_id": beat["active_audio_source_id"],
        }
        events.append(transition)
        inspection_targets.append(
            {
                "target_id": transition["event_id"],
                "event_type": transition["event_type"],
                "beat_id": beat["beat_id"],
                "time_seconds": round(cursor + transition_duration / 2, 3),
                "expected_visible_text": beat["transition_label"],
            }
        )
        cursor += transition_duration
        comparison = {
            "event_id": f"comparison_{beat_index + 1:03d}",
            "event_type": "comparison_beat",
            "beat_id": beat["beat_id"],
            "output_in": cursor,
            "output_out": cursor + beat_duration,
            "duration_seconds": beat_duration,
            "proposition": beat["proposition"],
            "why_informative": beat["why_informative"],
            "evidence": beat["evidence"],
            "layout": layout,
            "active_audio_source_id": beat["active_audio_source_id"],
            "foreground_audio_owner_count": 1,
            "concurrent_source_ids": [
                row["source_id"] for row in beat["evidence"]
            ],
            "source_bindings": [
                {
                    "source_id": row["source_id"],
                    "source_identity": source_by_id[row["source_id"]][
                        "source_identity"
                    ],
                    "source_range": [row["source_in"], row["source_out"]],
                    "role": row["role"],
                    "audio_mode": row["audio_mode"],
                    "visible_source_label": row["visible_source_label"],
                }
                for row in beat["evidence"]
            ],
        }
        events.append(comparison)
        beat_events.append(comparison)
        inspection_targets.append(
            {
                "target_id": comparison["event_id"],
                "event_type": comparison["event_type"],
                "beat_id": beat["beat_id"],
                "time_seconds": round(cursor + min(2.0, beat_duration / 2), 3),
                "expected_visible_text": beat["proposition"],
            }
        )
        cursor += beat_duration

    layout_checks = _validate_layouts(events)
    if not all(layout_checks.values()):
        failed = [name for name, passed in layout_checks.items() if not passed]
        raise EvidenceLinkedComparisonError(
            f"comparison layout is unsafe: {', '.join(failed)}",
            stage="timeline",
        )
    return {
        "schema_version": TIMELINE_SCHEMA_VERSION,
        "artifact_id": plan["artifact_id"],
        "frame": {
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT,
            "aspect_ratio": "16:9",
            "fps": OUTPUT_FPS,
        },
        "presentation": "stable_concurrent_source_panels",
        "panel_policy": {
            "two_way": "side_by_side_actual_source_content",
            "three_way": "three_equal_actual_source_panels_unverified_until_held_out",
            "active_audio_border": "warm_yellow",
            "muted_reference_border": "blue",
        },
        "events": events,
        "beats": beat_events,
        "beat_count": len(beat_events),
        "output_duration_seconds": round(cursor, 3),
        "layout_checks": layout_checks,
        "inspection_targets": inspection_targets,
    }


def render_filter_complex(
    *,
    timeline: dict[str, Any],
    source_bindings: list[dict[str, Any]],
    ass_path: Path,
) -> str:
    index_by_source = {
        binding["source_id"]: binding["index"] for binding in source_bindings
    }
    filters: list[str] = []
    concat_parts: list[str] = []
    for event_index, event in enumerate(timeline["events"]):
        key = f"s{event_index}"
        duration = float(event["duration_seconds"])
        filters.append(
            f"color=c=0x0B1320:s={FRAME_WIDTH}x{FRAME_HEIGHT}:"
            f"r={OUTPUT_FPS}:d={duration:.3f}[base_{key}]"
        )
        previous = f"base_{key}"
        for panel_index, (evidence, layout) in enumerate(
            zip(event["evidence"], event["layout"], strict=True)
        ):
            source_index = index_by_source[evidence["source_id"]]
            source_in = float(evidence["source_in"])
            source_out = float(evidence["source_out"])
            if event["event_type"] != "comparison_beat":
                source_out = min(source_out, source_in + 0.12)
            panel_label = f"panel_{key}_{panel_index}"
            border_color = (
                "0xF6C453"
                if evidence["source_id"]
                == (
                    event.get("active_audio_source_id")
                    or event.get("next_active_audio_source_id")
                )
                else "0x5B8DEF"
            )
            border_width = (
                10
                if evidence["source_id"]
                == (
                    event.get("active_audio_source_id")
                    or event.get("next_active_audio_source_id")
                )
                else 5
            )
            filters.append(
                f"[{source_index}:v:0]"
                f"trim=start={source_in:.3f}:end={source_out:.3f},"
                "setpts=PTS-STARTPTS,"
                f"scale={layout['width']}:{layout['height']}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={layout['width']}:{layout['height']}:"
                "(ow-iw)/2:(oh-ih)/2:color=0x05080D,"
                f"fps={OUTPUT_FPS},"
                f"tpad=stop_mode=clone:stop_duration={duration:.3f},"
                f"trim=duration={duration:.3f},"
                f"drawbox=x=0:y=0:w=iw:h=ih:color={border_color}:"
                f"t={border_width},format=yuv420p[{panel_label}]"
            )
            overlay_label = f"overlay_{key}_{panel_index}"
            filters.append(
                f"[{previous}][{panel_label}]"
                f"overlay=x={layout['x']}:y={layout['y']}:"
                f"shortest=1[{overlay_label}]"
            )
            previous = overlay_label
        filters.append(f"[{previous}]format=yuv420p[v_{key}]")

        if event["event_type"] == "comparison_beat":
            active = next(
                row
                for row in event["evidence"]
                if row["source_id"] == event["active_audio_source_id"]
            )
            source_index = index_by_source[active["source_id"]]
            filters.append(
                f"[{source_index}:a:0]"
                f"atrim=start={float(active['source_in']):.3f}:"
                f"end={float(active['source_out']):.3f},"
                "asetpts=PTS-STARTPTS,aresample=48000,"
                "aformat=sample_fmts=fltp:channel_layouts=stereo"
                f"[a_{key}]"
            )
        else:
            filters.append(
                f"anullsrc=r=48000:cl=stereo:d={duration:.3f}[a_{key}]"
            )
        concat_parts.append(f"[v_{key}][a_{key}]")

    filters.append(
        "".join(concat_parts)
        + f"concat=n={len(timeline['events'])}:v=1:a=1[vbase][aout]"
    )
    filters.append(
        f"[vbase]subtitles=filename='{_escape_filter_path(ass_path)}'[vout]"
    )
    return ";\n".join(filters)


def render_ass_overlay(
    *,
    direction: dict[str, Any],
    plan: dict[str, Any],
    timeline: dict[str, Any],
    transcript_context: dict[str, Any],
) -> str:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {FRAME_WIDTH}
PlayResY: {FRAME_HEIGHT}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Title,Meiryo,64,&H00FFFFFF,&H00FFFFFF,&H00131B29,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,8,100,100,48,1
Style: TitleSub,Meiryo,38,&H00D8E7FF,&H00D8E7FF,&H00131B29,&H00000000,0,0,0,0,100,100,0,0,1,4,0,8,120,120,132,1
Style: Proposition,Meiryo,42,&H00FFFFFF,&H00FFFFFF,&H00131B29,&H900B1320,-1,0,0,0,100,100,0,0,3,3,0,8,120,120,45,1
Style: Why,Meiryo,28,&H00BED4F2,&H00BED4F2,&H00131B29,&H900B1320,0,0,0,0,100,100,0,0,3,2,0,8,150,150,112,1
Style: Panel,Meiryo,25,&H00FFFFFF,&H00FFFFFF,&H00131B29,&H900B1320,-1,0,0,0,100,100,0,0,3,2,0,7,0,0,0,1
Style: Badge,Meiryo,24,&H000B1320,&H000B1320,&H00F6C453,&H00F6C453,-1,0,0,0,100,100,0,0,3,1,0,9,0,0,0,1
Style: Caption,Meiryo,48,&H00FFFFFF,&H00FFFFFF,&H00131B29,&HCC000000,-1,0,0,0,100,100,0,0,3,3,0,2,150,150,64,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events: list[str] = []
    opening = timeline["events"][0]
    opening_end = float(opening["output_out"])
    events.extend(
        [
            _ass_dialogue(
                0,
                0.35,
                opening_end - 0.2,
                "Title",
                direction["subject_line"],
            ),
            _ass_dialogue(
                0,
                0.8,
                opening_end - 0.2,
                "TitleSub",
                f"{direction['date_line']}｜{direction['thesis']}",
            ),
            _ass_dialogue(
                0,
                1.3,
                opening_end - 0.2,
                "Why",
                direction["viewer_benefit"],
            ),
        ]
    )
    _append_panel_labels(events, opening)

    context_by_beat = {
        row["beat_id"]: row for row in transcript_context["beats"]
    }
    for event in timeline["events"][1:]:
        output_in = float(event["output_in"])
        output_out = float(event["output_out"])
        if event["event_type"] == "comparison_transition":
            events.append(
                _ass_dialogue(
                    1,
                    output_in,
                    output_out,
                    "Proposition",
                    f"{event['transition_label']}｜{event['proposition']}",
                )
            )
            events.append(
                _ass_dialogue(
                    1,
                    output_in,
                    output_out,
                    "Why",
                    event["why_informative"],
                )
            )
        else:
            events.append(
                _ass_dialogue(
                    1,
                    output_in,
                    output_out,
                    "Proposition",
                    event["proposition"],
                )
            )
        _append_panel_labels(events, event)
        if event["event_type"] != "comparison_beat":
            continue
        context = context_by_beat[event["beat_id"]]
        active_context = next(
            row
            for row in context["evidence"]
            if row["source_id"] == event["active_audio_source_id"]
        )
        active_binding = next(
            row
            for row in event["evidence"]
            if row["source_id"] == event["active_audio_source_id"]
        )
        for cue in active_context["selected_cues"]:
            start = output_in + max(
                0.0,
                float(cue["start"]) - float(active_binding["source_in"]),
            )
            end = output_in + min(
                float(event["duration_seconds"]),
                float(cue["end"]) - float(active_binding["source_in"]),
            )
            if end - start < 0.12:
                continue
            events.append(
                _ass_dialogue(
                    3,
                    start,
                    end,
                    "Caption",
                    _wrap_caption(cue["text"]),
                )
            )
    return header + "\n".join(events) + "\n"


def render_video(
    *,
    final_video: Path,
    filter_path: Path,
    source_bindings: list[dict[str, Any]],
    ffmpeg_path: str,
) -> None:
    command = [ffmpeg_path, "-y", "-hide_banner", "-loglevel", "error"]
    for binding in source_bindings:
        command.extend(["-i", str(binding["locators"]["media"]["path"])])
    command.extend(
        [
            "-filter_complex_script",
            str(filter_path),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(OUTPUT_FPS),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(final_video),
        ]
    )
    _run(command, stage="render")
    if not final_video.is_file() or final_video.stat().st_size == 0:
        raise EvidenceLinkedComparisonError(
            "render did not produce final_video.mp4",
            stage="render",
        )


def validate_rendered_comparison(
    *,
    final_video: Path,
    plan: dict[str, Any],
    direction: dict[str, Any],
    timeline: dict[str, Any],
    source_bindings: list[dict[str, Any]],
    ffmpeg_path: str,
    ffprobe_path: str,
) -> dict[str, Any]:
    probe = ffmpeg_tiny.probe_media(
        input_path=final_video,
        ffprobe_path=ffprobe_path,
    ).metadata
    duration = float(probe.get("duration_seconds") or 0)
    stream_counts = probe.get("stream_counts") or {}
    checks = {
        "direction_bound": direction["artifact_id"] == plan["artifact_id"],
        "actual_content_16_9_layout": (
            timeline["frame"]["width"],
            timeline["frame"]["height"],
        )
        == (FRAME_WIDTH, FRAME_HEIGHT),
        "concurrent_evidence_each_beat": all(
            len(event["concurrent_source_ids"]) >= 2 for event in timeline["beats"]
        ),
        "exactly_one_foreground_audio_owner": all(
            event["foreground_audio_owner_count"] == 1
            for event in timeline["beats"]
        ),
        "active_audio_is_bound_evidence": all(
            event["active_audio_source_id"] in event["concurrent_source_ids"]
            for event in timeline["beats"]
        ),
        "all_source_labels_bound": all(
            row["visible_source_label"]
            == _canonical_source_label(
                next(
                    source
                    for source in plan["sources"]
                    if source["source_id"] == row["source_id"]
                )
            )
            for event in timeline["beats"]
            for row in event["source_bindings"]
        ),
        "layout_bounds_safe": timeline["layout_checks"]["within_frame"],
        "panel_overlap_absent": timeline["layout_checks"]["panels_do_not_overlap"],
        "label_lanes_separate": timeline["layout_checks"]["label_lanes_separate"],
        "source_legible_at_review_size": timeline["layout_checks"][
            "source_legible_at_review_size"
        ],
        "low_resolution_upscale_bounded": timeline["layout_checks"][
            "upscale_factor_at_most_1_5"
        ],
        "opening_thesis_target_present": any(
            row["target_id"] == "opening_thesis"
            for row in timeline["inspection_targets"]
        ),
        "all_comparison_transitions_targeted": len(
            [
                row
                for row in timeline["inspection_targets"]
                if row["event_type"] == "comparison_transition"
            ]
        )
        == timeline["beat_count"],
        "duration_matches_timeline": abs(
            duration - float(timeline["output_duration_seconds"])
        )
        <= 0.3,
        "video_stream_present": int(stream_counts.get("video") or 0) == 1,
        "audio_stream_present": int(stream_counts.get("audio") or 0) == 1,
        "h264_video": probe.get("video_codec") == "h264",
        "aac_audio": probe.get("audio_codec") == "aac",
        "resolution_1920x1080": probe.get("resolution") == "1920x1080",
        "private_review_only": plan["review_labels"]["private_review_only"] is True,
        "human_review_pending": plan["review_labels"]["human_review_pending"] is True,
        "rights_not_granted": plan["review_labels"]["rights_approval"]
        == "not_granted",
        "production_closed": plan["review_labels"]["production_approval"] is False,
        "public_use_closed": plan["review_labels"]["public_use"] is False,
        "monetized_use_closed": plan["review_labels"]["monetized_use"] is False,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise EvidenceLinkedComparisonError(
            f"render validation failed: {', '.join(failed)}",
            stage="media_validation",
        )
    decode = _run(
        [
            ffmpeg_path,
            "-v",
            "error",
            "-i",
            str(final_video),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-f",
            "null",
            "-",
        ],
        stage="full_decode",
    )
    checks["full_non_audible_decode"] = decode.returncode == 0
    return {
        "schema_version": MEDIA_SCHEMA_VERSION,
        "artifact_id": plan["artifact_id"],
        "state": READY_STATE,
        "status": "passed",
        "sha256": _sha256(final_video),
        "byte_size": final_video.stat().st_size,
        "duration_seconds": duration,
        "expected_duration_seconds": timeline["output_duration_seconds"],
        "metadata": {
            "container": probe.get("container"),
            "video_codec": probe.get("video_codec"),
            "audio_codec": probe.get("audio_codec"),
            "resolution": probe.get("resolution"),
            "fps": probe.get("fps"),
            "stream_counts": stream_counts,
        },
        "checks": checks,
        "source_count": len(source_bindings),
        "beat_count": timeline["beat_count"],
        "full_decode": {
            "silent_non_playing": True,
            "exit_code": decode.returncode,
            "stderr_sha256": hashlib.sha256(
                (decode.stderr or "").encode("utf-8")
            ).hexdigest(),
        },
    }


def build_contact_sheet(
    *,
    final_video: Path,
    timeline: dict[str, Any],
    output_path: Path,
    ffmpeg_path: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame_numbers = sorted(
        {
            max(0, round(float(row["time_seconds"]) * OUTPUT_FPS))
            for row in timeline["inspection_targets"]
        }
    )
    select = "+".join(f"eq(n\\,{value})" for value in frame_numbers)
    columns = 2
    rows = max(1, math.ceil(len(frame_numbers) / columns))
    vf = (
        f"select='{select}',scale=640:360,"
        f"tile={columns}x{rows}:padding=8:margin=8:color=0x0B1320"
    )
    _run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(final_video),
            "-vf",
            vf,
            "-frames:v",
            "1",
            str(output_path),
        ],
        stage="contact_sheet",
    )


def build_review_package(
    *,
    stage: Path,
    direction: dict[str, Any],
    plan: dict[str, Any],
    timeline: dict[str, Any],
    transcript_context: dict[str, Any],
    media_readback: dict[str, Any],
    review_port: int,
) -> None:
    review = stage / "review"
    review.mkdir(parents=True, exist_ok=True)
    review_html = render_review_html(
        direction=direction,
        plan=plan,
        timeline=timeline,
        transcript_context=transcript_context,
        media_readback=media_readback,
    ).replace("<head>", '<head>\n  <link rel="icon" href="data:,">', 1)
    _write_text(review / "index.html", review_html)
    _write_text(
        review / "open_preview.ps1",
        """param()
$ErrorActionPreference = 'Stop'
$index = Join-Path $PSScriptRoot 'index.html'
Start-Process -FilePath $index
""",
    )
    _write_text(
        review / "serve_preview.ps1",
        f"""param([int]$Port = {review_port})
$ErrorActionPreference = 'Stop'
$bundleRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
uv run python -m src.cli.serve_review --root $bundleRoot --port $Port
""",
    )


def render_review_html(
    *,
    direction: dict[str, Any],
    plan: dict[str, Any],
    timeline: dict[str, Any],
    transcript_context: dict[str, Any],
    media_readback: dict[str, Any],
) -> str:
    beat_context = {row["beat_id"]: row for row in transcript_context["beats"]}
    cards = []
    for index, beat in enumerate(plan["comparison_beats"], start=1):
        context = beat_context[beat["beat_id"]]
        evidence_rows = []
        for row in context["evidence"]:
            evidence_rows.append(
                "<li>"
                f"<strong>{html.escape(row['role'])}</strong> — "
                f"{html.escape(row['visible_source_label'])}; "
                f"{row['source_range'][0]:.3f}–{row['source_range'][1]:.3f}s; "
                f"{html.escape(row['audio_mode'])}"
                "</li>"
            )
        cards.append(
            "<article>"
            f"<p class=\"eyebrow\">比較 {index}</p>"
            f"<h2>{html.escape(beat['proposition'])}</h2>"
            f"<p>{html.escape(beat['why_informative'])}</p>"
            f"<ul>{''.join(evidence_rows)}</ul>"
            "</article>"
        )
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(direction['subject_line'])}</title>
  <style>
    :root {{ color-scheme: dark; font-family: "Meiryo", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #08111d; color: #f5f8ff; overflow-x: hidden; }}
    main {{ width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 64px; }}
    header, article {{ background: #101d2d; border: 1px solid #263a52; border-radius: 18px; padding: 22px; }}
    header {{ margin-bottom: 20px; }}
    h1 {{ font-size: clamp(1.65rem, 3vw, 2.45rem); margin: 0 0 10px; }}
    h2 {{ font-size: 1.2rem; margin: 5px 0 8px; }}
    p {{ line-height: 1.7; }}
    .boundary {{ color: #f6c453; font-weight: 700; }}
    .video-shell {{ background: #02050a; border: 1px solid #334b68; border-radius: 18px; padding: 12px; margin-bottom: 20px; }}
    video {{ display: block; width: 100%; max-height: 78vh; aspect-ratio: 16 / 9; background: #000; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: 16px; }}
    .eyebrow {{ color: #91b9ec; font-weight: 700; margin: 0; }}
    code {{ overflow-wrap: anywhere; }}
    a {{ color: #9bc5ff; }}
    ul {{ line-height: 1.7; padding-left: 22px; }}
  </style>
</head>
<body>
<main>
  <header>
    <p class="eyebrow">Evidence-linked comparison / private review</p>
    <h1>{html.escape(direction['thesis'])}</h1>
    <p>{html.escape(direction['comparison_question'])}</p>
    <p>{html.escape(direction['viewer_benefit'])}</p>
    <p class="boundary">人間レビュー待ち。rights・production・public/monetized use・publication・uploadは未承認。</p>
  </header>
  <section class="video-shell">
    <video id="review-video" controls muted preload="metadata" src="../final_video.mp4"></video>
  </section>
  <section class="grid">{''.join(cards)}</section>
  <article>
    <h2>Exact package</h2>
    <p><code>{html.escape(plan['artifact_id'])}</code></p>
    <p>MP4 SHA-256: <code>{media_readback['sha256']}</code></p>
    <p>Duration: {media_readback['duration_seconds']:.3f}s / beats: {timeline['beat_count']}</p>
    <ul>
      <li><a href="../paired_evidence_plan.json">paired-evidence plan</a></li>
      <li><a href="../comparison_timeline.json">comparison timeline</a></li>
      <li><a href="../transcript_context.json">transcript context</a></li>
      <li><a href="../provenance_snapshot.json">provenance snapshot</a></li>
      <li><a href="../media_readback.json">media readback</a></li>
      <li><a href="evidence/comparison_contact_sheet.jpg">contact sheet</a></li>
    </ul>
  </article>
</main>
<script>
  const video = document.getElementById("review-video");
  video.muted = true;
  video.pause();
  video.addEventListener("loadedmetadata", () => {{
    video.muted = true;
    video.pause();
    video.currentTime = 0;
  }});
</script>
</body>
</html>
"""


def build_provenance_snapshot(
    *,
    plan: dict[str, Any],
    source_bindings: list[dict[str, Any]],
    transcript_context: dict[str, Any],
) -> dict[str, Any]:
    binding_by_id = {row["source_id"]: row for row in source_bindings}
    sources = []
    for source in plan["sources"]:
        binding = binding_by_id[source["source_id"]]
        sources.append(
            {
                "source_id": source["source_id"],
                "source_identity": source["source_identity"],
                "archive_date": source["archive_date"],
                "member": source["member"],
                "provider_channel": source["provider_channel"],
                "locators": {
                    name: {
                        "path": binding["locators"][name]["relative_path"],
                        "sha256": binding["locators"][name]["sha256"],
                    }
                    for name in LOCATOR_NAMES
                },
                "media_probe": binding["media_metadata"],
                "processing_boundary": {
                    "user_granted_processing_scope": (
                        binding["processing_snapshot"][
                            "user_granted_processing_scope"
                        ]
                    ),
                    "underlying_rights_status": (
                        binding["processing_snapshot"]["underlying_rights_status"]
                    ),
                    "rights_clearance": False,
                    "rights_approval": False,
                    "public_use": False,
                    "monetized_use": False,
                },
            }
        )
    context_by_beat = {
        row["beat_id"]: row for row in transcript_context["beats"]
    }
    beat_bindings = []
    for beat in plan["comparison_beats"]:
        beat_bindings.append(
            {
                "beat_id": beat["beat_id"],
                "proposition": beat["proposition"],
                "why_informative": beat["why_informative"],
                "active_audio_source_id": beat["active_audio_source_id"],
                "evidence": [
                    {
                        **row,
                        "transcript_context_locator": (
                            "transcript_context.json#"
                            f"/beats/{plan['comparison_beats'].index(beat)}/"
                            f"evidence/{beat['evidence'].index(row)}"
                        ),
                    }
                    for row in beat["evidence"]
                ],
                "transcript_context_present": bool(
                    context_by_beat[beat["beat_id"]]["evidence"]
                ),
            }
        )
    return {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "artifact_id": plan["artifact_id"],
        "sources": sources,
        "beat_bindings": beat_bindings,
        "presentation": {
            "concurrent_source_imagery": True,
            "exactly_one_foreground_speech_track": True,
            "reference_audio_muted": True,
            "source_identity_and_date_visible": True,
        },
        "boundary": {
            "private_review_only": True,
            "human_review_pending": True,
            "rights_clearance": False,
            "rights_approval": False,
            "production_approval": False,
            "public_use": False,
            "monetized_use": False,
            "publication_approval": False,
            "upload_attempted": False,
        },
    }


def build_run_manifest(
    *,
    stage: Path,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    media_readback: dict[str, Any],
) -> dict[str, Any]:
    payloads = []
    for path in sorted(
        (row for row in stage.rglob("*") if row.is_file()),
        key=lambda row: row.relative_to(stage).as_posix(),
    ):
        relative = path.relative_to(stage).as_posix()
        if relative == "run_manifest.json":
            continue
        payloads.append(
            {
                "path": relative,
                "sha256": _sha256(path),
                "byte_size": path.stat().st_size,
            }
        )
    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_id": plan["artifact_id"],
        "state": READY_STATE,
        **plan["review_labels"],
        "source_identities": [
            source["source_identity"] for source in plan["sources"]
        ],
        "output": {
            "path": "final_video.mp4",
            "sha256": media_readback["sha256"],
            "byte_size": media_readback["byte_size"],
            "duration_seconds": media_readback["duration_seconds"],
        },
        "comparison": {
            "beat_count": timeline["beat_count"],
            "presentation": timeline["presentation"],
            "concurrent_source_panels": True,
            "foreground_audio_owner_per_beat": 1,
        },
        "payloads": payloads,
        "payload_tree_digest": {
            "algorithm": "sha256",
            "sha256": _payload_tree_digest(payloads),
            "file_count": len(payloads),
        },
    }
    manifest["manifest_self_integrity"] = {
        "algorithm": "sha256",
        "scope": "canonical_json_without_manifest_self_integrity",
        "sha256": _manifest_self_hash(manifest),
    }
    return manifest


def validate_run_manifest(stage: Path) -> None:
    manifest_path = stage / "run_manifest.json"
    manifest = _read_json(manifest_path, "run manifest")
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise EvidenceLinkedComparisonError(
            "manifest schema mismatch",
            stage="manifest_validation",
        )
    actual_paths = {
        path.relative_to(stage).as_posix()
        for path in stage.rglob("*")
        if path.is_file() and path != manifest_path
    }
    expected_paths = {row["path"] for row in manifest.get("payloads") or []}
    if actual_paths != expected_paths:
        raise EvidenceLinkedComparisonError(
            "manifest payload set is not closed",
            stage="manifest_validation",
        )
    for row in manifest["payloads"]:
        path = stage / row["path"]
        if (
            _sha256(path) != row["sha256"]
            or path.stat().st_size != row["byte_size"]
        ):
            raise EvidenceLinkedComparisonError(
                f"manifest payload mismatch: {row['path']}",
                stage="manifest_validation",
            )
        if path.suffix.lower() in {".json", ".html", ".ps1", ".txt"}:
            text = path.read_text(encoding="utf-8")
            if ABSOLUTE_PATH_RE.search(text):
                raise EvidenceLinkedComparisonError(
                    f"portable payload exposes an absolute path: {row['path']}",
                    stage="manifest_validation",
                )
    if (
        _payload_tree_digest(manifest["payloads"])
        != manifest["payload_tree_digest"]["sha256"]
    ):
        raise EvidenceLinkedComparisonError(
            "manifest payload tree digest mismatch",
            stage="manifest_validation",
        )
    if (
        _manifest_self_hash(manifest)
        != manifest["manifest_self_integrity"]["sha256"]
    ):
        raise EvidenceLinkedComparisonError(
            "manifest self-integrity mismatch",
            stage="manifest_validation",
        )
    review_html = (stage / "review" / "index.html").read_text(encoding="utf-8")
    video_tag = re.search(r"<video\b[^>]*>", review_html)
    if (
        video_tag is None
        or re.search(r"\sautoplay(?:\s|=|>)", video_tag.group(0))
        or " muted" not in video_tag.group(0)
        or 'src="../final_video.mp4"' not in video_tag.group(0)
        or ABSOLUTE_PATH_RE.search(review_html)
    ):
        raise EvidenceLinkedComparisonError(
            "portable review playback boundary failed",
            stage="manifest_validation",
        )


def _layout_for_evidence(
    evidence: list[dict[str, Any]],
    metadata_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if len(evidence) == 2:
        positions = [(80, 250, 840, 472), (1000, 250, 840, 472)]
    elif len(evidence) == 3:
        positions = [
            (60, 290, 580, 326),
            (670, 290, 580, 326),
            (1280, 290, 580, 326),
        ]
    else:
        raise EvidenceLinkedComparisonError(
            "unsupported evidence panel count",
            stage="timeline",
        )
    layouts = []
    for row, (x, y, width, height) in zip(evidence, positions, strict=True):
        metadata = metadata_by_id[row["source_id"]]
        source_width, source_height = _resolution_parts(metadata.get("resolution"))
        layouts.append(
            {
                "source_id": row["source_id"],
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "label_y": y + height + 14,
                "source_width": source_width,
                "source_height": source_height,
                "upscale_factor": round(
                    min(width / source_width, height / source_height),
                    4,
                ),
            }
        )
    return layouts


def _validate_layouts(events: list[dict[str, Any]]) -> dict[str, bool]:
    layouts = [event["layout"] for event in events]
    within_frame = all(
        panel["x"] >= 0
        and panel["y"] >= 0
        and panel["x"] + panel["width"] <= FRAME_WIDTH
        and panel["y"] + panel["height"] <= FRAME_HEIGHT
        for layout in layouts
        for panel in layout
    )
    panels_do_not_overlap = True
    for layout in layouts:
        for index, first in enumerate(layout):
            for second in layout[index + 1 :]:
                if not (
                    first["x"] + first["width"] <= second["x"]
                    or second["x"] + second["width"] <= first["x"]
                    or first["y"] + first["height"] <= second["y"]
                    or second["y"] + second["height"] <= first["y"]
                ):
                    panels_do_not_overlap = False
    return {
        "within_frame": within_frame,
        "panels_do_not_overlap": panels_do_not_overlap,
        "label_lanes_separate": all(
            panel["label_y"] < 825 for layout in layouts for panel in layout
        ),
        "source_legible_at_review_size": all(
            panel["width"] >= 560 and panel["height"] >= 315
            for layout in layouts
            for panel in layout
        ),
        "upscale_factor_at_most_1_5": all(
            panel["upscale_factor"] <= 1.5
            for layout in layouts
            for panel in layout
        ),
    }


def _append_panel_labels(
    events: list[str],
    event: dict[str, Any],
) -> None:
    start = float(event["output_in"])
    end = float(event["output_out"])
    highlighted = (
        event.get("active_audio_source_id")
        or event.get("next_active_audio_source_id")
    )
    for evidence, panel in zip(event["evidence"], event["layout"], strict=True):
        events.append(
            _ass_positioned_dialogue(
                2,
                start,
                end,
                "Panel",
                evidence["visible_source_label"],
                x=panel["x"] + 8,
                y=panel["label_y"],
                alignment=7,
            )
        )
        if evidence["source_id"] == highlighted:
            badge = (
                "音声"
                if event["event_type"] == "comparison_beat"
                else "次の音声"
            )
            events.append(
                _ass_positioned_dialogue(
                    3,
                    start,
                    end,
                    "Badge",
                    badge,
                    x=panel["x"] + panel["width"] - 14,
                    y=panel["y"] + 14,
                    alignment=9,
                )
            )
        elif event["event_type"] != "opening":
            events.append(
                _ass_positioned_dialogue(
                    3,
                    start,
                    end,
                    "Panel",
                    "比較映像・消音",
                    x=panel["x"] + panel["width"] - 14,
                    y=panel["y"] + 14,
                    alignment=9,
                )
            )


def _json3_caption_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, event in enumerate(payload.get("events") or []):
        start = float(event.get("tStartMs") or 0) / 1000
        duration = float(event.get("dDurationMs") or 0) / 1000
        text = "".join(
            str(segment.get("utf8") or "") for segment in event.get("segs") or []
        ).replace("\n", " ")
        text = " ".join(text.split())
        if not text or duration <= 0:
            continue
        rows.append(
            {
                "cue_id": f"cue_{index:06d}",
                "start": round(start, 3),
                "end": round(start + duration, 3),
                "text": text,
            }
        )
    return rows


def _overlapping_caption_rows(
    rows: list[dict[str, Any]],
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if float(row["end"]) > start + 0.001
        and float(row["start"]) < end - 0.001
    ]


def _canonical_source_label(source: dict[str, Any]) -> str:
    return (
        f"{source['member']}｜{source['archive_date']}｜"
        f"{source['source_identity']}"
    )


def _resolution_parts(value: Any) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", str(value or ""))
    if not match:
        raise EvidenceLinkedComparisonError(
            f"source resolution is not readable: {value}",
            stage="timeline",
        )
    return int(match.group(1)), int(match.group(2))


def _wrap_caption(value: Any, *, width: int = 22) -> str:
    text = " ".join(str(value or "").replace("\n", " ").split())
    if len(text) <= width:
        return text
    first = text[:width]
    second = text[width : width * 2]
    if len(text) > width * 2:
        second = second[:-1] + "…"
    return f"{first}\n{second}"


def _ass_dialogue(
    layer: int,
    start: float,
    end: float,
    style: str,
    text: Any,
) -> str:
    return (
        f"Dialogue: {layer},{_ass_time(start)},{_ass_time(end)},{style},"
        f",0,0,0,,{_ass_text(text)}"
    )


def _ass_positioned_dialogue(
    layer: int,
    start: float,
    end: float,
    style: str,
    text: Any,
    *,
    x: int,
    y: int,
    alignment: int,
) -> str:
    return (
        f"Dialogue: {layer},{_ass_time(start)},{_ass_time(end)},{style},"
        f",0,0,0,,{{\\an{alignment}\\pos({x},{y})}}{_ass_text(text)}"
    )


def _ass_text(value: Any) -> str:
    return (
        str(value or "")
        .replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\n", r"\N")
    )


def _ass_time(seconds: float) -> str:
    centiseconds = max(0, round(float(seconds) * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole_seconds, hundredths = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{hundredths:02d}"


def _escape_filter_path(path: Path) -> str:
    value = path.resolve().as_posix()
    return value.replace("\\", r"\\").replace(":", r"\:").replace("'", r"\'")


def _payload_tree_digest(payloads: list[dict[str, Any]]) -> str:
    lines = [
        f"{row['path']}\0{row['sha256']}\0{row['byte_size']}"
        for row in sorted(payloads, key=lambda item: item["path"])
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _manifest_self_hash(manifest: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in manifest.items()
        if key != "manifest_self_integrity"
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _run(command: list[str], *, stage: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        stderr = ""
        if isinstance(exc, subprocess.CalledProcessError):
            stderr = (exc.stderr or "").strip()
        detail = f": {stderr}" if stderr else ""
        raise EvidenceLinkedComparisonError(
            f"command failed during {stage}{detail}",
            stage=stage,
        ) from exc


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceLinkedComparisonError(
            f"{label} is not readable JSON: {path}",
            stage="input_read",
        ) from exc
    if not isinstance(payload, dict):
        raise EvidenceLinkedComparisonError(
            f"{label} must be a JSON object",
            stage="input_read",
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()
