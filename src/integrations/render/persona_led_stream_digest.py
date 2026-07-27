"""Build the bounded two-week Oozora Subaru persona-led stream digest."""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny


ARTIFACT_ID = "clip-s1-subaru-ohasuba-20260718-20260725-digest-v1-001"
PLAN_SCHEMA_VERSION = "clippipegen.s1.persona_led_stream_digest_plan.v1"
DIRECTION_SCHEMA_VERSION = "clippipegen.s1.persona_led_stream_digest_direction.v1"
MANIFEST_SCHEMA_VERSION = "clippipegen.s1.persona_led_stream_digest_manifest.v1"
READY_STATE = "PERSONA_LED_ORDINARY_STREAM_S1_CANDIDATE_READY_FOR_HUMAN_REVIEW"
SOURCE_IDENTITIES = {
    "youtube:ib3DwHDI71Q": "2026-07-18",
    "youtube:rltNvZ_FY8Q": "2026-07-25",
}
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
OUTPUT_FPS = 30
DEFAULT_REVIEW_PORT = 8079
COMMAND_TIMEOUT_SECONDS = 60 * 60
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class PersonaLedStreamDigestError(RuntimeError):
    """Fail-closed digest build error with a stable stage label."""

    def __init__(self, message: str, *, stage: str) -> None:
        super().__init__(message)
        self.stage = stage


def build_persona_led_stream_digest(
    *,
    plan_path: Path,
    direction_path: Path,
    output_dir: Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    review_port: int = DEFAULT_REVIEW_PORT,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Build one immutable private-review artifact from the two fixed streams."""

    root = (base_dir or Path.cwd()).resolve()
    plan_file = _resolved(root, plan_path)
    direction_file = _resolved(root, direction_path)
    output = _resolved(root, output_dir)
    if output.exists():
        raise PersonaLedStreamDigestError(
            f"output directory already exists: {_display_path(root, output)}",
            stage="output_allocation",
        )
    if not 1 <= int(review_port) <= 65535:
        raise PersonaLedStreamDigestError(
            "review port must be between 1 and 65535",
            stage="preflight",
        )
    if not plan_file.is_file() or not direction_file.is_file():
        raise PersonaLedStreamDigestError(
            "plan and predeclared direction must exist",
            stage="preflight",
        )

    tools = ffmpeg_tiny.preflight_tools(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )
    if tools.get("status") != "passed":
        raise PersonaLedStreamDigestError(
            "FFmpeg/FFprobe preflight failed",
            stage="preflight",
        )
    ffmpeg = str(tools["ffmpeg"]["path"])
    ffprobe = str(tools["ffprobe"]["path"])

    direction = _read_json(direction_file, "predeclared direction")
    plan = _read_json(plan_file, "digest plan")
    validate_predeclared_direction(direction)
    validate_digest_plan(plan, direction_sha256=_sha256(direction_file))
    source_bindings = bind_source_inputs(
        plan=plan,
        root=root,
        ffprobe_path=ffprobe,
    )
    timeline = build_timeline(plan)
    transcript_context = build_transcript_context(
        plan=plan,
        timeline=timeline,
        root=root,
    )
    transition_continuity = build_transition_continuity(plan, timeline)
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
        _write_json(stage / "digest_plan.json", emitted_plan)
        _write_json(stage / "ordered_cut_list.json", timeline)
        _write_json(stage / "transition_continuity.json", transition_continuity)
        _write_json(stage / "transcript_context.json", transcript_context)
        _write_json(
            stage / "provenance_snapshot.json",
            build_provenance_snapshot(
                plan=plan,
                source_bindings=source_bindings,
                root=root,
            ),
        )

        ass_path = stage / ".render_overlay.ass"
        filter_path = stage / ".render_filter.txt"
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
        media_readback = validate_rendered_digest(
            final_video=final_video,
            plan=plan,
            direction=direction,
            timeline=timeline,
            transition_continuity=transition_continuity,
            source_bindings=source_bindings,
            ffmpeg_path=ffmpeg,
            ffprobe_path=ffprobe,
        )
        _write_json(stage / "media_readback.json", media_readback)
        build_contact_sheet(
            final_video=final_video,
            timeline=timeline,
            output_path=stage / "review" / "evidence" / "cut_contact_sheet.jpg",
            ffmpeg_path=ffmpeg,
        )
        build_review_package(
            stage=stage,
            direction=direction,
            plan=plan,
            timeline=timeline,
            transition_continuity=transition_continuity,
            transcript_context=transcript_context,
            media_readback=media_readback,
            review_port=review_port,
        )
        ass_path.unlink()
        filter_path.unlink()
        manifest = build_run_manifest(
            stage=stage,
            timeline=timeline,
            media_readback=media_readback,
            source_bindings=source_bindings,
        )
        _write_json(stage / "run_manifest.json", manifest)
        validate_run_manifest(stage)
        stage.replace(output)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise

    return {
        "artifact_id": ARTIFACT_ID,
        "state": READY_STATE,
        "output_dir": output,
        "final_video": output / "final_video.mp4",
        "review_index": output / "review" / "index.html",
        "duration_seconds": media_readback["duration_seconds"],
        "final_video_sha256": media_readback["sha256"],
        "cut_count": timeline["cut_count"],
        "source_switch_count": timeline["source_switch_count"],
        "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
        "review_port": review_port,
    }


def validate_predeclared_direction(direction: dict[str, Any]) -> None:
    if direction.get("schema_version") != DIRECTION_SCHEMA_VERSION:
        raise PersonaLedStreamDigestError(
            "unsupported direction schema",
            stage="direction_validation",
        )
    if direction.get("artifact_id") != ARTIFACT_ID:
        raise PersonaLedStreamDigestError(
            "predeclared direction artifact identity mismatch",
            stage="direction_validation",
        )
    required = {
        "primary_persona",
        "member",
        "source_archive_dates",
        "concept",
        "viewer_benefit",
        "both_sources_necessary",
    }
    if any(not direction.get(key) for key in required):
        raise PersonaLedStreamDigestError(
            "predeclared direction is incomplete",
            stage="direction_validation",
        )
    if direction["member"] != "大空スバル":
        raise PersonaLedStreamDigestError(
            "member must remain 大空スバル",
            stage="direction_validation",
        )
    if direction["source_archive_dates"] != ["2026-07-18", "2026-07-25"]:
        raise PersonaLedStreamDigestError(
            "source dates must remain the fixed chronological pair",
            stage="direction_validation",
        )
    concept = str(direction["concept"])
    if "ドラゴンボール" not in concept or "2026-07-18" not in concept or "2026-07-25" not in concept:
        raise PersonaLedStreamDigestError(
            "concept must state the evidence-backed topic and date range",
            stage="direction_validation",
        )
    if "最新" in concept or direction.get("claims_latest") is not False:
        raise PersonaLedStreamDigestError(
            "latest claims are not allowed",
            stage="direction_validation",
        )
    if (
        "大空スバル" not in str(direction.get("title_line") or "")
        or "2026-07-18" not in str(direction.get("subtitle_line") or "")
        or "2026-07-25" not in str(direction.get("subtitle_line") or "")
        or "ドラゴンボール" not in str(direction.get("subtitle_line") or "")
    ):
        raise PersonaLedStreamDigestError(
            "opening lines must state member, date range, and concrete topic",
            stage="direction_validation",
        )
    if direction.get("orientation") != "concept_first":
        raise PersonaLedStreamDigestError(
            "concept-first orientation is required",
            stage="direction_validation",
        )


def validate_digest_plan(plan: dict[str, Any], *, direction_sha256: str) -> None:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise PersonaLedStreamDigestError(
            "unsupported plan schema",
            stage="plan_validation",
        )
    if plan.get("artifact_id") != ARTIFACT_ID:
        raise PersonaLedStreamDigestError(
            "unexpected artifact_id",
            stage="plan_validation",
        )
    if plan.get("predeclared_direction_sha256") != direction_sha256:
        raise PersonaLedStreamDigestError(
            "plan is not bound to the predeclared direction",
            stage="plan_validation",
        )
    title_duration = float(plan.get("title_duration_seconds") or 0)
    if not 4.0 <= title_duration <= 10.0:
        raise PersonaLedStreamDigestError(
            "title duration must be 4-10 seconds",
            stage="plan_validation",
        )

    sources = plan.get("sources")
    if not isinstance(sources, list) or len(sources) != 2:
        raise PersonaLedStreamDigestError(
            "digest requires exactly two sources",
            stage="plan_validation",
        )
    identities = {str(source.get("source_identity")) for source in sources}
    if identities != set(SOURCE_IDENTITIES):
        raise PersonaLedStreamDigestError(
            "source pair differs from the fixed authority",
            stage="plan_validation",
        )
    source_ids: set[str] = set()
    source_dates: dict[str, str] = {}
    source_durations: dict[str, float] = {}
    for source in sources:
        source_id = str(source.get("source_id") or "")
        identity = str(source.get("source_identity") or "")
        if not source_id or source_id in source_ids:
            raise PersonaLedStreamDigestError(
                "source IDs must be non-empty and unique",
                stage="plan_validation",
            )
        source_ids.add(source_id)
        expected_date = SOURCE_IDENTITIES[identity]
        if source.get("archive_date") != expected_date:
            raise PersonaLedStreamDigestError(
                f"archive date mismatch for {identity}",
                stage="plan_validation",
            )
        source_dates[source_id] = expected_date
        if (
            source.get("member") != "大空スバル"
            or source.get("ordinary_livestream") is not True
            or source.get("official_animation") is not False
            or source.get("fixture") is not False
        ):
            raise PersonaLedStreamDigestError(
                f"source classification is unsafe: {source_id}",
                stage="plan_validation",
            )
        media = source.get("media") or {}
        source_durations[source_id] = float(media.get("duration_seconds") or 0)
        if source_durations[source_id] <= 0:
            raise PersonaLedStreamDigestError(
                f"source duration missing: {source_id}",
                stage="plan_validation",
            )
        for locator_name in (
            "media",
            "fetch_receipt",
            "material_ledger",
            "provider_metadata",
            "caption",
            "processing_snapshot",
            "identity_binding",
        ):
            locator = source.get(locator_name) or {}
            if not locator.get("path") or not SHA256_RE.fullmatch(
                str(locator.get("sha256") or "")
            ):
                raise PersonaLedStreamDigestError(
                    f"{source_id} {locator_name} locator/hash is required",
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
            raise PersonaLedStreamDigestError(
                f"{source_id} processing boundary is incomplete",
                stage="plan_validation",
            )

    cuts = plan.get("cuts")
    if not isinstance(cuts, list) or not cuts:
        raise PersonaLedStreamDigestError(
            "digest requires an evidence-backed cut list",
            stage="plan_validation",
        )
    seen_cut_ids: set[str] = set()
    seen_sources: set[str] = set()
    previous_date = ""
    previous_source_ranges: dict[str, float] = {}
    for index, cut in enumerate(cuts):
        cut_id = str(cut.get("cut_id") or "")
        source_id = str(cut.get("source_id") or "")
        source_in = float(cut.get("source_in") or 0)
        source_out = float(cut.get("source_out") or 0)
        if not cut_id or cut_id in seen_cut_ids or source_id not in source_ids:
            raise PersonaLedStreamDigestError(
                "cut identity/source mapping is invalid",
                stage="plan_validation",
            )
        seen_cut_ids.add(cut_id)
        seen_sources.add(source_id)
        if (
            source_in < 0
            or source_out <= source_in
            or source_out > source_durations[source_id] + 0.05
        ):
            raise PersonaLedStreamDigestError(
                f"invalid source range: {cut_id}",
                stage="plan_validation",
            )
        if source_in < previous_source_ranges.get(source_id, -1.0) - 0.002:
            raise PersonaLedStreamDigestError(
                f"source chronology is not preserved: {cut_id}",
                stage="plan_validation",
            )
        previous_source_ranges[source_id] = source_out
        current_date = source_dates[source_id]
        if previous_date and current_date < previous_date:
            raise PersonaLedStreamDigestError(
                "archive chronology is not preserved",
                stage="plan_validation",
            )
        previous_date = current_date
        for key in (
            "topic",
            "immediate_function",
            "section_label",
            "transition_basis",
        ):
            if not str(cut.get(key) or "").strip():
                raise PersonaLedStreamDigestError(
                    f"cut {cut_id} is missing {key}",
                    stage="plan_validation",
                )
        expected_basis = "sequence_start" if index == 0 else None
        if expected_basis and cut["transition_basis"] != expected_basis:
            raise PersonaLedStreamDigestError(
                "first cut must use sequence_start",
                stage="plan_validation",
            )
        if index and cut["transition_basis"] not in {
            "same_topic_continuation",
            "explicit_topic_change",
        }:
            raise PersonaLedStreamDigestError(
                f"transition basis is not explicit: {cut_id}",
                stage="plan_validation",
            )
    if seen_sources != source_ids:
        raise PersonaLedStreamDigestError(
            "both fixed sources must contribute",
            stage="plan_validation",
        )
    excluded = set(plan.get("excluded_assets") or [])
    required_exclusions = {
        "official_animation",
        "fixture_media",
        "tts",
        "generated_narration",
        "new_music",
        "ai_imagery",
        "promotional_cta",
    }
    if not required_exclusions.issubset(excluded):
        raise PersonaLedStreamDigestError(
            "excluded asset boundary is incomplete",
            stage="plan_validation",
        )
    labels = plan.get("review_labels") or {}
    if (
        labels.get("private_review_only") is not True
        or labels.get("human_review_pending") is not True
        or labels.get("rights_approval") != "not_granted"
        or labels.get("public_use") is not False
        or labels.get("monetized_use") is not False
    ):
        raise PersonaLedStreamDigestError(
            "review labels cannot open closed gates",
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
        for locator_name in (
            "media",
            "fetch_receipt",
            "material_ledger",
            "provider_metadata",
            "caption",
            "processing_snapshot",
            "identity_binding",
        ):
            locator = source[locator_name]
            path = _resolved(root, Path(locator["path"]))
            if not path.is_file():
                raise PersonaLedStreamDigestError(
                    f"source locator missing: {locator_name} / {locator['path']}",
                    stage="source_binding",
                )
            actual_hash = _sha256(path)
            if actual_hash != locator["sha256"]:
                raise PersonaLedStreamDigestError(
                    f"source locator hash mismatch: {locator_name} / {locator['path']}",
                    stage="source_binding",
                )
            resolved_locators[locator_name] = {
                "path": path,
                "sha256": actual_hash,
            }
        snapshot = _read_json(
            resolved_locators["processing_snapshot"]["path"],
            "processing snapshot",
        )
        if snapshot.get("source_identity") != source["source_identity"]:
            raise PersonaLedStreamDigestError(
                f"processing snapshot identity mismatch: {source['source_id']}",
                stage="source_binding",
            )
        if (
            source["source_identity"] == "youtube:ib3DwHDI71Q"
            and snapshot.get("authority_id")
            != "CPG-AUTH-20260728-IB3DWH-PRIVATE-ACQUISITION-01"
        ):
            raise PersonaLedStreamDigestError(
                "authorized acquisition is not bound to the exact target",
                stage="source_binding",
            )
        if (
            source["source_identity"] == "youtube:rltNvZ_FY8Q"
            and snapshot.get("acquisition_effect_this_mission")
            != "not_attempted_reused_existing"
        ):
            raise PersonaLedStreamDigestError(
                "existing source must remain read-only reuse",
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
            raise PersonaLedStreamDigestError(
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
            or provider_metadata.get("channel") != "Subaru Ch. 大空スバル"
            or provider_metadata.get("was_live") is not True
            or provider_metadata.get("availability") != "public"
        ):
            raise PersonaLedStreamDigestError(
                f"provider metadata identity/classification mismatch: {source['source_id']}",
                stage="source_binding",
            )
        probe = ffmpeg_tiny.probe_media(
            input_path=resolved_locators["media"]["path"],
            ffprobe_path=ffprobe_path,
        ).metadata
        duration = float(probe.get("duration_seconds") or 0)
        if abs(duration - float(source["media"]["duration_seconds"])) > 0.2:
            raise PersonaLedStreamDigestError(
                f"source duration mismatch: {source['source_id']}",
                stage="source_binding",
            )
        bindings.append(
            {
                "index": index,
                "source_id": source["source_id"],
                "source_identity": source["source_identity"],
                "archive_date": source["archive_date"],
                "locators": resolved_locators,
                "media_metadata": probe,
            }
        )
    return bindings


def build_timeline(plan: dict[str, Any]) -> dict[str, Any]:
    output_clock = float(plan["title_duration_seconds"])
    cuts: list[dict[str, Any]] = []
    previous_source: str | None = None
    source_switches = 0
    for cut in plan["cuts"]:
        duration = float(cut["source_out"]) - float(cut["source_in"])
        emitted = json.loads(json.dumps(cut))
        emitted["output_in"] = round(output_clock, 3)
        emitted["output_out"] = round(output_clock + duration, 3)
        emitted["duration_seconds"] = round(duration, 3)
        cuts.append(emitted)
        if previous_source and previous_source != cut["source_id"]:
            source_switches += 1
        previous_source = cut["source_id"]
        output_clock += duration
    return {
        "schema_version": "clippipegen.s1.persona_led_stream_digest_timeline.v1",
        "artifact_id": ARTIFACT_ID,
        "title_duration_seconds": float(plan["title_duration_seconds"]),
        "cuts": cuts,
        "cut_count": len(cuts),
        "source_switch_count": source_switches,
        "output_duration_seconds": round(output_clock, 3),
        "chronology": "2026-07-18_then_2026-07-25",
    }


def build_transcript_context(
    *,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    source_rows: dict[str, list[dict[str, Any]]] = {}
    for source in plan["sources"]:
        caption_path = _resolved(root, Path(source["caption"]["path"]))
        source_rows[source["source_id"]] = _json3_caption_rows(caption_path)
    cut_rows: list[dict[str, Any]] = []
    for cut in timeline["cuts"]:
        rows = source_rows[cut["source_id"]]
        selected = _overlapping_caption_rows(
            rows,
            float(cut["source_in"]),
            float(cut["source_out"]),
        )
        if len(selected) < 2:
            raise PersonaLedStreamDigestError(
                f"insufficient transcript evidence for {cut['cut_id']}",
                stage="caption_binding",
            )
        before = [
            row for row in rows
            if float(cut["source_in"]) - 15.0 <= row["start"] < float(cut["source_in"])
        ][-4:]
        after = [
            row for row in rows
            if float(cut["source_out"]) <= row["start"] <= float(cut["source_out"]) + 15.0
        ][:4]
        cut_rows.append(
            {
                "cut_id": cut["cut_id"],
                "source_id": cut["source_id"],
                "source_range": [
                    float(cut["source_in"]),
                    float(cut["source_out"]),
                ],
                "topic": cut["topic"],
                "immediate_function": cut["immediate_function"],
                "before_context": before,
                "selected_cues": selected,
                "after_context": after,
                "selected_text": " ".join(row["text"] for row in selected),
            }
        )
    return {
        "schema_version": "clippipegen.s1.persona_led_stream_digest_transcript_context.v1",
        "artifact_id": ARTIFACT_ID,
        "provider_caption_class": "youtube_auto_caption_json3",
        "official_authorship_claimed": False,
        "cuts": cut_rows,
    }


def build_transition_continuity(
    plan: dict[str, Any],
    timeline: dict[str, Any],
) -> dict[str, Any]:
    transitions: list[dict[str, Any]] = [
        {
            "transition_id": "opening_to_cut_001",
            "from": "concept_title",
            "to": timeline["cuts"][0]["cut_id"],
            "basis": "concept_first_orientation",
            "visible_marker": timeline["cuts"][0]["section_label"],
            "requires_abstract_inference": False,
        }
    ]
    for previous, current in zip(timeline["cuts"], timeline["cuts"][1:]):
        transitions.append(
            {
                "transition_id": f"{previous['cut_id']}_to_{current['cut_id']}",
                "from": previous["cut_id"],
                "to": current["cut_id"],
                "basis": current["transition_basis"],
                "visible_marker": current["section_label"],
                "relationship": current.get("transition_explanation"),
                "requires_abstract_inference": False,
            }
        )
    return {
        "schema_version": "clippipegen.s1.persona_led_stream_digest_transitions.v1",
        "artifact_id": ARTIFACT_ID,
        "transitions": transitions,
        "all_adjacent_transitions_explicit": True,
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
    filters = [
        (
            f"color=c=0x0B1320:s={FRAME_WIDTH}x{FRAME_HEIGHT}:"
            f"r={OUTPUT_FPS}:d={timeline['title_duration_seconds']:.3f},"
            "format=yuv420p[titlev]"
        ),
        (
            "anullsrc=r=48000:cl=stereo:"
            f"d={timeline['title_duration_seconds']:.3f}[titlea]"
        ),
    ]
    concat_parts = ["[titlev][titlea]"]
    for index, cut in enumerate(timeline["cuts"]):
        source_index = index_by_source[cut["source_id"]]
        source_in = float(cut["source_in"])
        source_out = float(cut["source_out"])
        filters.append(
            f"[{source_index}:v:0]trim=start={source_in:.3f}:end={source_out:.3f},"
            "setpts=PTS-STARTPTS,"
            f"scale={FRAME_WIDTH}:{FRAME_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={FRAME_WIDTH}:{FRAME_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x0B1320,"
            f"fps={OUTPUT_FPS},format=yuv420p[v{index}]"
        )
        filters.append(
            f"[{source_index}:a:0]atrim=start={source_in:.3f}:end={source_out:.3f},"
            "asetpts=PTS-STARTPTS,aresample=48000,"
            "aformat=sample_fmts=fltp:channel_layouts=stereo"
            f"[a{index}]"
        )
        concat_parts.append(f"[v{index}][a{index}]")
    filters.append(
        "".join(concat_parts)
        + f"concat=n={len(timeline['cuts']) + 1}:v=1:a=1[vbase][aout]"
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
Style: Title,Meiryo,84,&H00FFFFFF,&H00FFFFFF,&H00131B29,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,5,120,120,120,1
Style: TitleSub,Meiryo,42,&H00D8E7FF,&H00D8E7FF,&H00131B29,&H00000000,0,0,0,0,100,100,0,0,1,4,0,5,180,180,150,1
Style: Benefit,Meiryo,34,&H00AFC7E6,&H00AFC7E6,&H00131B29,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,220,220,235,1
Style: Section,Meiryo,38,&H00FFFFFF,&H00FFFFFF,&H00131B29,&H900B1320,-1,0,0,0,100,100,0,0,3,2,0,7,70,70,62,1
Style: Source,Meiryo,28,&H00D8E7FF,&H00D8E7FF,&H00131B29,&H900B1320,0,0,0,0,100,100,0,0,3,2,0,9,70,70,62,1
Style: Caption,Meiryo,54,&H00FFFFFF,&H00FFFFFF,&H00131B29,&H90000000,-1,0,0,0,100,100,0,0,3,3,0,2,120,120,72,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    title_end = float(timeline["title_duration_seconds"])
    events = [
        _ass_dialogue(
            0,
            0.35,
            title_end - 0.3,
            "Title",
            direction["title_line"],
        ),
        _ass_dialogue(
            0,
            0.8,
            title_end - 0.3,
            "TitleSub",
            direction["subtitle_line"],
        ),
        _ass_dialogue(
            0,
            1.3,
            title_end - 0.3,
            "Benefit",
            direction["viewer_benefit"],
        ),
    ]
    context_by_cut = {
        row["cut_id"]: row for row in transcript_context["cuts"]
    }
    source_by_id = {row["source_id"]: row for row in plan["sources"]}
    for cut in timeline["cuts"]:
        label_end = min(float(cut["output_in"]) + 5.5, float(cut["output_out"]))
        events.append(
            _ass_dialogue(
                1,
                float(cut["output_in"]),
                label_end,
                "Section",
                cut["section_label"],
            )
        )
        source = source_by_id[cut["source_id"]]
        events.append(
            _ass_dialogue(
                1,
                float(cut["output_in"]),
                label_end,
                "Source",
                f"大空スバル / おはスバ {source['archive_date']}",
            )
        )
        for cue in context_by_cut[cut["cut_id"]]["selected_cues"]:
            start = float(cut["output_in"]) + max(
                0.0,
                float(cue["start"]) - float(cut["source_in"]),
            )
            end = float(cut["output_in"]) + min(
                float(cut["duration_seconds"]),
                float(cue["end"]) - float(cut["source_in"]),
            )
            if end - start < 0.12:
                continue
            events.append(
                _ass_dialogue(
                    2,
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
            "18",
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
        raise PersonaLedStreamDigestError(
            "render did not produce final_video.mp4",
            stage="render",
        )


def validate_rendered_digest(
    *,
    final_video: Path,
    plan: dict[str, Any],
    direction: dict[str, Any],
    timeline: dict[str, Any],
    transition_continuity: dict[str, Any],
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
        "exact_source_pair": {
            binding["source_identity"] for binding in source_bindings
        }
        == set(SOURCE_IDENTITIES),
        "ordinary_streams_only": all(
            source["ordinary_livestream"]
            and not source["official_animation"]
            and not source["fixture"]
            for source in plan["sources"]
        ),
        "direction_concept_bound": direction["concept"] == plan["concept"],
        "concept_first_title_present": float(plan["title_duration_seconds"]) >= 4.0,
        "all_transitions_explicit": transition_continuity[
            "all_adjacent_transitions_explicit"
        ],
        "chronological_dates": timeline["chronology"]
        == "2026-07-18_then_2026-07-25",
        "duration_matches_timeline": abs(
            duration - float(timeline["output_duration_seconds"])
        )
        <= 0.25,
        "video_stream_present": int(stream_counts.get("video") or 0) == 1,
        "audio_stream_present": int(stream_counts.get("audio") or 0) == 1,
        "h264_video": probe.get("video_codec") == "h264",
        "aac_audio": probe.get("audio_codec") == "aac",
        "resolution_1920x1080": probe.get("resolution") == "1920x1080",
        "private_review_only": plan["review_labels"]["private_review_only"] is True,
        "human_review_pending": plan["review_labels"]["human_review_pending"] is True,
        "rights_not_granted": plan["review_labels"]["rights_approval"]
        == "not_granted",
        "public_use_closed": plan["review_labels"]["public_use"] is False,
        "monetized_use_closed": plan["review_labels"]["monetized_use"] is False,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise PersonaLedStreamDigestError(
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
        "schema_version": "clippipegen.s1.persona_led_stream_digest_media_readback.v1",
        "artifact_id": ARTIFACT_ID,
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
    timestamps = [max(0.5, float(timeline["title_duration_seconds"]) / 2)]
    timestamps.extend(
        min(float(cut["output_out"]) - 0.2, float(cut["output_in"]) + 2.0)
        for cut in timeline["cuts"]
    )
    frame_indexes = sorted({max(0, round(value * OUTPUT_FPS)) for value in timestamps})
    select = "+".join(f"eq(n\\,{index})" for index in frame_indexes)
    columns = min(4, len(frame_indexes))
    rows = math.ceil(len(frame_indexes) / columns)
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
            (
                f"select='{select}',scale=448:-2,"
                f"tile={columns}x{rows}:padding=8:margin=8:color=0x0B1320"
            ),
            "-frames:v",
            "1",
            "-q:v",
            "2",
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
    transition_continuity: dict[str, Any],
    transcript_context: dict[str, Any],
    media_readback: dict[str, Any],
    review_port: int,
) -> None:
    review = stage / "review"
    review.mkdir(parents=True, exist_ok=True)
    _write_text(
        review / "index.html",
        render_review_html(
            direction=direction,
            plan=plan,
            timeline=timeline,
            transition_continuity=transition_continuity,
            transcript_context=transcript_context,
            media_readback=media_readback,
        ),
    )
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
    transition_continuity: dict[str, Any],
    transcript_context: dict[str, Any],
    media_readback: dict[str, Any],
) -> str:
    source_by_id = {source["source_id"]: source for source in plan["sources"]}
    context_by_cut = {
        row["cut_id"]: row for row in transcript_context["cuts"]
    }
    cut_rows = []
    for cut in timeline["cuts"]:
        source = source_by_id[cut["source_id"]]
        cut_rows.append(
            "<tr>"
            f"<td><code>{html.escape(cut['cut_id'])}</code></td>"
            f"<td>{html.escape(source['archive_date'])}</td>"
            f"<td>{float(cut['source_in']):.3f}–{float(cut['source_out']):.3f}s</td>"
            f"<td>{html.escape(cut['topic'])}</td>"
            f"<td>{html.escape(cut['immediate_function'])}</td>"
            f"<td>{html.escape(cut['transition_basis'])}</td>"
            "</tr>"
        )
    transition_rows = []
    for row in transition_continuity["transitions"]:
        transition_rows.append(
            "<tr>"
            f"<td><code>{html.escape(row['from'])}</code> → "
            f"<code>{html.escape(row['to'])}</code></td>"
            f"<td>{html.escape(str(row['basis']))}</td>"
            f"<td>{html.escape(str(row.get('visible_marker') or ''))}</td>"
            f"<td>{html.escape(str(row.get('relationship') or ''))}</td>"
            "</tr>"
        )
    context_cards = []
    for cut in timeline["cuts"]:
        context = context_by_cut[cut["cut_id"]]
        context_cards.append(
            "<article class=\"context-card\">"
            f"<h3>{html.escape(cut['cut_id'])} — {html.escape(cut['topic'])}</h3>"
            f"<p>{html.escape(context['selected_text'])}</p>"
            "</article>"
        )
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(direction['concept'])}</title>
  <style>
    :root {{ color-scheme: dark; --bg:#08111d; --card:#101d2d; --line:#28405e; --text:#f5f8fc; --muted:#a8bed8; --accent:#66d9ef; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:linear-gradient(180deg,#07101b,#0b1624 38rem); color:var(--text); font-family:Meiryo,"Noto Sans JP",sans-serif; line-height:1.65; }}
    main {{ width:min(1180px,calc(100% - 32px)); margin:0 auto; padding:28px 0 72px; }}
    .eyebrow {{ color:var(--accent); font-weight:700; letter-spacing:.08em; }}
    h1 {{ max-width:22ch; font-size:clamp(2rem,5vw,4.4rem); line-height:1.08; margin:.25em 0; }}
    .lede {{ max-width:74ch; color:var(--muted); font-size:1.05rem; }}
    .labels {{ display:flex; flex-wrap:wrap; gap:8px; margin:18px 0; }}
    .label {{ border:1px solid var(--line); border-radius:999px; padding:5px 11px; color:var(--muted); background:#0a1523; }}
    video {{ width:100%; display:block; background:#03070d; border:1px solid var(--line); border-radius:18px; box-shadow:0 24px 80px #0008; }}
    section {{ margin-top:34px; padding:24px; border:1px solid var(--line); border-radius:18px; background:color-mix(in srgb,var(--card) 93%,transparent); }}
    h2 {{ margin-top:0; font-size:clamp(1.35rem,2.5vw,2rem); }}
    table {{ width:100%; border-collapse:collapse; }}
    th,td {{ text-align:left; vertical-align:top; border-bottom:1px solid var(--line); padding:12px 10px; }}
    th {{ color:var(--muted); }}
    code {{ color:#bfe6ff; overflow-wrap:anywhere; }}
    .table-scroll {{ overflow-x:auto; }}
    .grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
    .context-card {{ padding:16px; border:1px solid var(--line); border-radius:14px; background:#0a1523; }}
    .context-card h3 {{ margin-top:0; }}
    .context-card p {{ color:var(--muted); margin-bottom:0; }}
    .evidence {{ width:100%; height:auto; border:1px solid var(--line); border-radius:12px; }}
    .warning {{ border-left:4px solid #f6c85f; padding-left:14px; color:#f8deb0; }}
    @media (max-width:700px) {{
      main {{ width:min(100% - 20px,1180px); padding-top:16px; }}
      section {{ padding:16px; }}
      .grid {{ grid-template-columns:1fr; }}
      th,td {{ min-width:9rem; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div class="eyebrow">大空スバル / 2026-07-18 → 2026-07-25</div>
    <h1>{html.escape(direction['concept'])}</h1>
    <p class="lede">{html.escape(direction['viewer_benefit'])}</p>
    <div class="labels">
      <span class="label">private review only</span>
      <span class="label">human review pending</span>
      <span class="label">rights pending / unverified</span>
      <span class="label">autoplay disabled</span>
      <span class="label">initially muted</span>
    </div>
  </header>

  <video id="review-video" controls muted playsinline preload="metadata">
    <source src="../final_video.mp4" type="video/mp4">
  </video>

  <section>
    <h2>先に分かる約束</h2>
    <p><strong>対象:</strong> {html.escape(direction['primary_persona'])}</p>
    <p><strong>今回の見どころ:</strong> {html.escape(direction['subtitle_line'])}</p>
    <p><strong>二本が必要な理由:</strong> {html.escape(direction['both_sources_necessary'])}</p>
    <p class="warning">この package は非公開の人間レビュー候補です。技術検証は editorial acceptance、rights approval、public/monetized use approval を意味しません。</p>
  </section>

  <section>
    <h2>実際の cut と役割</h2>
    <div class="table-scroll">
      <table>
        <thead><tr><th>cut</th><th>archive</th><th>source range</th><th>topic</th><th>function</th><th>transition</th></tr></thead>
        <tbody>{''.join(cut_rows)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>隣接 transition の根拠</h2>
    <div class="table-scroll">
      <table>
        <thead><tr><th>adjacent pair</th><th>basis</th><th>visible marker</th><th>relationship</th></tr></thead>
        <tbody>{''.join(transition_rows)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>字幕文脈の readback</h2>
    <div class="grid">{''.join(context_cards)}</div>
  </section>

  <section>
    <h2>actual-content contact sheet</h2>
    <img class="evidence" src="evidence/cut_contact_sheet.jpg" alt="Opening and selected cut frames">
  </section>

  <section>
    <h2>exact media identity</h2>
    <p><code>{html.escape(media_readback['sha256'])}</code></p>
    <p>{media_readback['duration_seconds']:.3f}s / {media_readback['byte_size']:,} bytes / H.264 + AAC / 1920×1080</p>
  </section>
</main>
<script>
  const video = document.getElementById('review-video');
  const enforceSafeStart = () => {{
    video.muted = true;
    video.pause();
    if (video.currentTime > 0.05) video.currentTime = 0;
  }};
  enforceSafeStart();
  window.addEventListener('pageshow', enforceSafeStart);
  document.addEventListener('visibilitychange', () => {{
    if (document.visibilityState === 'visible' && !video.dataset.userStarted) enforceSafeStart();
  }});
  video.addEventListener('play', () => {{ video.dataset.userStarted = 'true'; }}, {{ once:true }});
</script>
</body>
</html>
"""


def build_provenance_snapshot(
    *,
    plan: dict[str, Any],
    source_bindings: list[dict[str, Any]],
    root: Path,
) -> dict[str, Any]:
    source_by_id = {source["source_id"]: source for source in plan["sources"]}
    sources = []
    for binding in source_bindings:
        source = source_by_id[binding["source_id"]]
        sources.append(
            {
                "source_id": binding["source_id"],
                "source_identity": binding["source_identity"],
                "archive_date": binding["archive_date"],
                "member": "大空スバル",
                "ordinary_livestream": True,
                "official_animation": False,
                "fixture": False,
                "media": source["media"],
                "fetch_receipt": source["fetch_receipt"],
                "material_ledger": source["material_ledger"],
                "provider_metadata": source["provider_metadata"],
                "caption": source["caption"],
                "processing_snapshot": source["processing_snapshot"],
                "identity_binding": source["identity_binding"],
                "media_probe": {
                    "duration_seconds": binding["media_metadata"].get(
                        "duration_seconds"
                    ),
                    "video_codec": binding["media_metadata"].get("video_codec"),
                    "audio_codec": binding["media_metadata"].get("audio_codec"),
                    "resolution": binding["media_metadata"].get("resolution"),
                },
            }
        )
    return {
        "schema_version": "clippipegen.s1.persona_led_stream_digest_provenance.v1",
        "artifact_id": ARTIFACT_ID,
        "sources": sources,
        "acquisition_authority": {
            "authority_id": "CPG-AUTH-20260728-IB3DWH-PRIVATE-ACQUISITION-01",
            "exact_target": "youtube:ib3DwHDI71Q",
            "scope": "anonymous_acquisition_and_local_private_review_only",
            "credentials_used": False,
            "cookies_used": False,
            "oauth_used": False,
            "other_source_acquisition_attempted": False,
        },
        "boundary": {
            "underlying_rights_status": "pending_or_unverified",
            "rights_clearance": False,
            "rights_approval": False,
            "public_use": False,
            "monetized_use": False,
            "upload_attempted": False,
        },
    }


def build_run_manifest(
    *,
    stage: Path,
    timeline: dict[str, Any],
    media_readback: dict[str, Any],
    source_bindings: list[dict[str, Any]],
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
    tree_digest = _payload_tree_digest(payloads)
    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": READY_STATE,
        "private_review_only": True,
        "human_review_pending": True,
        "rights_approval": "not_granted",
        "public_use": False,
        "monetized_use": False,
        "publication_approval": False,
        "upload_attempted": False,
        "source_identities": [
            binding["source_identity"] for binding in source_bindings
        ],
        "output": {
            "path": "final_video.mp4",
            "sha256": media_readback["sha256"],
            "byte_size": media_readback["byte_size"],
            "duration_seconds": media_readback["duration_seconds"],
        },
        "timeline": {
            "cut_count": timeline["cut_count"],
            "source_switch_count": timeline["source_switch_count"],
            "output_duration_seconds": timeline["output_duration_seconds"],
        },
        "payloads": payloads,
        "payload_tree_digest": {
            "algorithm": "sha256",
            "sha256": tree_digest,
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
        raise PersonaLedStreamDigestError(
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
        raise PersonaLedStreamDigestError(
            "manifest payload set is not closed",
            stage="manifest_validation",
        )
    for row in manifest["payloads"]:
        path = stage / row["path"]
        if _sha256(path) != row["sha256"] or path.stat().st_size != row["byte_size"]:
            raise PersonaLedStreamDigestError(
                f"manifest payload mismatch: {row['path']}",
                stage="manifest_validation",
            )
    if _payload_tree_digest(manifest["payloads"]) != manifest[
        "payload_tree_digest"
    ]["sha256"]:
        raise PersonaLedStreamDigestError(
            "manifest payload tree digest mismatch",
            stage="manifest_validation",
        )
    if _manifest_self_hash(manifest) != manifest["manifest_self_integrity"]["sha256"]:
        raise PersonaLedStreamDigestError(
            "manifest self-integrity mismatch",
            stage="manifest_validation",
        )
    review_html = (stage / "review" / "index.html").read_text(encoding="utf-8")
    if (
        " autoplay" in review_html
        or "<video" not in review_html
        or " muted" not in review_html
        or 'src="../final_video.mp4"' not in review_html
        or re.search(r"[A-Za-z]:[\\/]", review_html)
    ):
        raise PersonaLedStreamDigestError(
            "portable review playback boundary failed",
            stage="manifest_validation",
        )


def _json3_caption_rows(path: Path) -> list[dict[str, Any]]:
    payload = _read_json(path, "provider caption")
    rows: list[dict[str, Any]] = []
    for index, event in enumerate(payload.get("events") or []):
        if event.get("tStartMs") is None or not event.get("segs"):
            continue
        text = "".join(str(segment.get("utf8") or "") for segment in event["segs"])
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        start = float(event["tStartMs"]) / 1000.0
        duration = float(event.get("dDurationMs") or 2500.0) / 1000.0
        rows.append(
            {
                "cue_id": f"cue_{index:06d}",
                "start": round(start, 3),
                "end": round(start + max(duration, 0.2), 3),
                "text": text,
            }
        )
    if not rows:
        raise PersonaLedStreamDigestError(
            f"provider caption contains no timed text: {path}",
            stage="caption_binding",
        )
    return rows


def _overlapping_caption_rows(
    rows: list[dict[str, Any]],
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    selected = []
    for row in rows:
        clipped_start = max(start, float(row["start"]))
        clipped_end = min(end, float(row["end"]))
        if clipped_end <= clipped_start:
            continue
        emitted = json.loads(json.dumps(row))
        emitted["start"] = round(clipped_start, 3)
        emitted["end"] = round(clipped_end, 3)
        selected.append(emitted)
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(selected):
        next_start = (
            float(selected[index + 1]["start"])
            if index + 1 < len(selected)
            else float(row["end"])
        )
        if next_start > float(row["start"]):
            row["end"] = round(min(float(row["end"]), next_start), 3)
        if float(row["end"]) - float(row["start"]) >= 0.12:
            normalized.append(row)
    return normalized


def _wrap_caption(text: str, max_chars: int = 28) -> str:
    clean = re.sub(r"\s+", " ", str(text)).strip()
    if len(clean) <= max_chars:
        return clean
    split_at = min(
        range(max(8, len(clean) // 2 - 8), min(len(clean), len(clean) // 2 + 9)),
        key=lambda index: (
            0 if clean[index - 1] in "、。！？!? " else 1,
            abs(index - len(clean) / 2),
        ),
    )
    return clean[:split_at].rstrip() + "\n" + clean[split_at:].lstrip()


def _ass_dialogue(
    layer: int,
    start: float,
    end: float,
    style: str,
    text: str,
) -> str:
    return (
        f"Dialogue: {layer},{_ass_time(start)},{_ass_time(end)},"
        f"{style},,0,0,0,,{_ass_text(text)}"
    )


def _ass_text(value: str) -> str:
    return (
        str(value)
        .replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\r", "")
        .replace("\n", r"\N")
    )


def _ass_time(seconds: float) -> str:
    centiseconds = max(0, round(float(seconds) * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole_seconds, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{fraction:02d}"


def _escape_filter_path(path: Path) -> str:
    return (
        path.resolve()
        .as_posix()
        .replace("\\", "/")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )


def _payload_tree_digest(payloads: list[dict[str, Any]]) -> str:
    rows = [
        f"{row['path']}|{row['sha256']}|{row['byte_size']}"
        for row in sorted(payloads, key=lambda item: item["path"])
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def _manifest_self_hash(manifest: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in manifest.items()
        if key != "manifest_self_integrity"
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run(command: list[str], *, stage: str) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise PersonaLedStreamDigestError(
            f"subprocess failed before exit code: {exc}",
            stage=stage,
        ) from exc
    if result.returncode != 0:
        stderr_hash = hashlib.sha256(
            (result.stderr or "").encode("utf-8")
        ).hexdigest()
        tail = (result.stderr or "")[-1200:]
        raise PersonaLedStreamDigestError(
            f"subprocess exit {result.returncode}; stderr_sha256={stderr_hash}; tail={tail}",
            stage=stage,
        )
    return result


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PersonaLedStreamDigestError(
            f"{label} is not valid JSON: {path}: {exc}",
            stage="input_read",
        ) from exc
    if not isinstance(payload, dict):
        raise PersonaLedStreamDigestError(
            f"{label} must be a JSON object",
            stage="input_read",
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


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
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
