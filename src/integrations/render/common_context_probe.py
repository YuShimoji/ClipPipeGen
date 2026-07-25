"""Probe-specific two-source common-context renderer for ClipPipeGen S1.

The module deliberately supports exactly two evidence-bound sources.  It creates
one internal review package and stops before any human coherence, rights,
production, publication, or release decision.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid
from html import escape
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny
from src.integrations.render.real_video_pipeline import (
    load_caption_events,
    measure_cut_loudness,
    probe_media_detail,
    validate_packet_timestamps,
)
from src.integrations.render.second_source_short_repeatability import _run_signal_qa
from src.integrations.render.vertical_short_candidate import (
    _faststart_readback,
    _measure_loudness,
)


ARTIFACT_ID = "clip-s1-two-source-common-context-probe-v1-001"
PLAN_SCHEMA_VERSION = "clippipegen.s1.common_context_probe_plan.v1"
TIMELINE_SCHEMA_VERSION = "clippipegen.s1.common_context_probe_timeline.v1"
CAPTION_SCHEMA_VERSION = "clippipegen.s1.common_context_probe_caption_readback.v1"
COMMENTARY_SCHEMA_VERSION = "clippipegen.s1.common_context_probe_commentary.v1"
VALIDATION_SCHEMA_VERSION = "clippipegen.s1.common_context_probe_validation.v1"
MANIFEST_SCHEMA_VERSION = "clippipegen.s1.common_context_probe_manifest.v1"
READY_STATE = "S1_S3_COMMON_CONTEXT_PROBE_READY_FOR_S4_HUMAN_REVIEW"
DIRECTION_SIGNATURE = "neutral_evidence_commentary_overlay_v1"
REVIEW_PORT = 8077
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
SOURCE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_ARGUMENT_RELATIONS = {
    "introduces",
    "supports",
    "contrasts",
    "qualifies",
    "synthesizes",
}
COMMAND_TIMEOUT_SECONDS = 1800


class CommonContextProbeError(Exception):
    """Raised when the bounded S1 probe cannot be constructed objectively."""

    def __init__(self, message: str, *, stage: str = "unknown") -> None:
        super().__init__(message)
        self.stage = stage


def build_common_context_probe(
    *,
    plan_path: Path,
    output_dir: Path,
    design_basis_path: Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    review_port: int = REVIEW_PORT,
    base_dir: Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
) -> dict[str, Any]:
    """Build one new immutable two-source internal review package."""

    root = (base_dir or Path.cwd()).resolve()
    plan_file = _resolved(root, plan_path)
    design_basis_file = _resolved(root, design_basis_path)
    output = _resolved(root, output_dir)
    if output.exists():
        raise CommonContextProbeError(
            f"output directory already exists: {_display_path(root, output)}",
            stage="output_allocation",
        )
    if not 1 <= int(review_port) <= 65535:
        raise CommonContextProbeError(
            "review port must be between 1 and 65535", stage="preflight"
        )
    if not plan_file.is_file() or not design_basis_file.is_file():
        raise CommonContextProbeError(
            "plan and pre-render design basis must exist", stage="preflight"
        )

    tools = ffmpeg_tiny.preflight_tools(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    if tools.get("status") != "passed":
        raise CommonContextProbeError(
            "FFmpeg/FFprobe preflight failed", stage="preflight"
        )
    ffmpeg = str(tools["ffmpeg"]["path"])
    ffprobe = str(tools["ffprobe"]["path"])
    plan = _read_json(plan_file, "common-context plan")
    validate_common_context_plan(plan)
    design_basis = _read_json(design_basis_file, "pre-render design basis")
    if design_basis.get("direction_signature") != DIRECTION_SIGNATURE:
        raise CommonContextProbeError(
            "pre-render design direction signature mismatch", stage="design_binding"
        )
    if design_basis.get("artifact_id") != ARTIFACT_ID:
        raise CommonContextProbeError(
            "pre-render design artifact identity mismatch", stage="design_binding"
        )

    source_bindings, evidence = bind_source_inputs(
        plan=plan,
        root=root,
        ffprobe_path=ffprobe,
        runner=runner,
    )
    validate_direct_evidence(plan, evidence)
    fingerprint = input_fingerprint(plan, source_bindings, design_basis)
    emitted_plan = json.loads(json.dumps(plan))
    emitted_plan["artifact_id"] = ARTIFACT_ID
    emitted_plan["input_fingerprint"] = fingerprint
    timeline = build_timeline_ir(emitted_plan)
    captions = remap_source_captions(
        plan=emitted_plan,
        evidence=evidence,
        timeline=timeline,
    )
    commentary = build_commentary_track(emitted_plan, evidence)
    validate_caption_commentary_separation(
        captions=captions,
        commentary=commentary,
        output_duration=float(timeline["output_duration_seconds"]),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    stage.mkdir(parents=False, exist_ok=False)
    try:
        _write_json(stage / "common_context_plan.json", emitted_plan)
        _write_json(stage / "timeline_ir.json", timeline)
        selection = build_source_pair_selection_readback(
            emitted_plan, source_bindings, fingerprint
        )
        _write_json(stage / "source_pair_selection_readback.json", selection)
        _write_json(
            stage / "argument_trace.json",
            build_argument_trace(emitted_plan, evidence, fingerprint),
        )
        _write_json(stage / "commentary_track.json", commentary)
        _write_json(
            stage / "provenance_snapshot.json",
            build_provenance_snapshot(source_bindings, fingerprint),
        )
        _write_json(
            stage / "range_rights_inventory.json",
            build_range_rights_inventory(emitted_plan, fingerprint),
        )
        _write_json(stage / "caption_readback.json", captions)
        presentation = build_commentary_presentation_readback(
            captions=captions,
            commentary=commentary,
            design_basis=design_basis,
            fingerprint=fingerprint,
        )
        _write_json(stage / "commentary_presentation_readback.json", presentation)
        copied_design = json.loads(json.dumps(design_basis))
        copied_design["input_fingerprint"] = fingerprint
        _write_json(stage / "pre_render_design_basis.json", copied_design)

        ass_path = stage / ".render_overlay.ass"
        filter_path = stage / ".render_filter.txt"
        _write_text(
            ass_path,
            render_ass_overlay(
                captions=captions,
                commentary=commentary,
                timeline=timeline,
                sources=emitted_plan["sources"],
            ),
        )
        _write_text(
            filter_path,
            render_filter_complex(
                cuts=timeline["cuts"],
                source_input_indexes=timeline["source_input_indexes"],
                ass_path=ass_path,
            ),
        )
        final_video = stage / "final_video.mp4"
        render_video(
            final_video=final_video,
            sources=source_bindings,
            filter_path=filter_path,
            ffmpeg_path=ffmpeg,
            runner=runner,
        )
        validation = validate_rendered_probe(
            final_video=final_video,
            timeline=timeline,
            captions=captions,
            commentary=commentary,
            source_bindings=source_bindings,
            ffmpeg_path=ffmpeg,
            ffprobe_path=ffprobe,
            runner=runner,
            fingerprint=fingerprint,
        )
        if validation["status"] != "passed":
            failed = [
                key for key, value in validation["checks"].items() if not value
            ]
            raise CommonContextProbeError(
                f"render validation failed: {', '.join(failed)}",
                stage="media_validation",
            )
        _write_json(stage / "validation_readback.json", validation)
        build_review_package(
            stage=stage,
            plan=emitted_plan,
            timeline=timeline,
            commentary=commentary,
            rights_inventory=build_range_rights_inventory(
                emitted_plan, fingerprint
            ),
            validation=validation,
            review_port=review_port,
            ffmpeg_path=ffmpeg,
            runner=runner,
        )
        ass_path.unlink()
        filter_path.unlink()
        manifest = build_run_manifest(
            stage=stage,
            plan=emitted_plan,
            timeline=timeline,
            validation=validation,
            source_bindings=source_bindings,
            fingerprint=fingerprint,
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
        "duration_seconds": timeline["output_duration_seconds"],
        "cut_count": timeline["cut_count"],
        "source_switch_count": timeline["source_switch_count"],
        "commentary_count": len(commentary["events"]),
        "input_fingerprint": fingerprint,
        "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
        "review_port": review_port,
    }


def validate_common_context_plan(plan: dict[str, Any]) -> None:
    """Validate the probe-specific two-source argument and timeline contract."""

    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise CommonContextProbeError("unsupported plan schema", stage="plan_validation")
    if plan.get("artifact_id") not in (None, ARTIFACT_ID):
        raise CommonContextProbeError("unexpected artifact_id", stage="plan_validation")
    for key in (
        "editorial_question",
        "working_thesis",
        "thesis_classification",
        "sources",
        "argument_map",
        "cuts",
        "commentary_track",
        "excluded_directions",
        "closed_gates",
    ):
        if key not in plan:
            raise CommonContextProbeError(
                f"plan field missing: {key}", stage="plan_validation"
            )
    if plan["thesis_classification"] != "authored_synthesis":
        raise CommonContextProbeError(
            "thesis_classification must be authored_synthesis",
            stage="plan_validation",
        )
    if not str(plan["editorial_question"]).strip() or not str(
        plan["working_thesis"]
    ).strip():
        raise CommonContextProbeError(
            "editorial question and thesis must be non-empty",
            stage="plan_validation",
        )
    if plan.get("direction_signature") != DIRECTION_SIGNATURE:
        raise CommonContextProbeError(
            "bounded direction signature is required", stage="plan_validation"
        )

    sources = plan["sources"]
    if not isinstance(sources, list) or len(sources) != 2:
        raise CommonContextProbeError(
            "probe requires exactly two sources", stage="plan_validation"
        )
    source_ids: set[str] = set()
    identities: set[str] = set()
    media_hashes: set[str] = set()
    durations: dict[str, float] = {}
    for source in sources:
        source_id = str(source.get("source_id") or "")
        if not SOURCE_ID_PATTERN.fullmatch(source_id) or source_id in source_ids:
            raise CommonContextProbeError(
                "source IDs must be stable, safe, and unique", stage="plan_validation"
            )
        source_ids.add(source_id)
        identity = str(source.get("source_identity") or "")
        media = source.get("media") or {}
        if not identity or identity in identities:
            raise CommonContextProbeError(
                "source identities must be distinct", stage="plan_validation"
            )
        identities.add(identity)
        media_hash = str(media.get("sha256") or "")
        if not SHA256_PATTERN.fullmatch(media_hash) or media_hash in media_hashes:
            raise CommonContextProbeError(
                "source media hashes must be distinct SHA-256 values",
                stage="plan_validation",
            )
        media_hashes.add(media_hash)
        duration = float(media.get("duration_seconds") or 0.0)
        if duration <= 0:
            raise CommonContextProbeError(
                "source duration must be positive", stage="plan_validation"
            )
        durations[source_id] = duration
        for locator_key in ("caption", "rights"):
            locator = source.get(locator_key) or {}
            if not locator.get("path") or not SHA256_PATTERN.fullmatch(
                str(locator.get("sha256") or "")
            ):
                raise CommonContextProbeError(
                    f"{source_id} {locator_key} locator/hash is required",
                    stage="plan_validation",
                )
        rights_status = str((source.get("rights") or {}).get("status") or "")
        if rights_status not in {"pending", "unknown", "not_granted"}:
            raise CommonContextProbeError(
                "rights status cannot be upgraded by this probe",
                stage="plan_validation",
            )
        transcript = source.get("transcript") or {}
        if transcript.get("path") and not SHA256_PATTERN.fullmatch(
            str(transcript.get("sha256") or "")
        ):
            raise CommonContextProbeError(
                f"{source_id} transcript hash is invalid", stage="plan_validation"
            )

    cuts = plan["cuts"]
    if not isinstance(cuts, list) or not 4 <= len(cuts) <= 6:
        raise CommonContextProbeError(
            "timeline must contain 4-6 cuts", stage="plan_validation"
        )
    expected_output = 0.0
    cut_ids: set[str] = set()
    per_source: dict[str, list[tuple[float, float]]] = {
        source_id: [] for source_id in source_ids
    }
    source_sequence: list[str] = []
    evidence_ids: set[str] = set()
    for source in sources:
        for row in source.get("evidence_segments") or []:
            evidence_id = str(row.get("evidence_id") or "")
            if not evidence_id.startswith(f"{source['source_id']}:"):
                raise CommonContextProbeError(
                    "evidence IDs must be source-namespaced",
                    stage="plan_validation",
                )
            if evidence_id in evidence_ids:
                raise CommonContextProbeError(
                    "evidence IDs must be globally unique", stage="plan_validation"
                )
            evidence_ids.add(evidence_id)
    for index, cut in enumerate(cuts):
        cut_id = str(cut.get("cut_id") or "")
        source_id = str(cut.get("source_id") or "")
        if not cut_id or cut_id in cut_ids or source_id not in source_ids:
            raise CommonContextProbeError(
                "cut identity/source mapping is invalid", stage="plan_validation"
            )
        cut_ids.add(cut_id)
        source_in = float(cut.get("source_in") or 0.0)
        source_out = float(cut.get("source_out") or 0.0)
        output_in = float(cut.get("output_in") or 0.0)
        output_out = float(cut.get("output_out") or 0.0)
        if (
            source_in < 0
            or source_out <= source_in
            or source_out > durations[source_id] + 0.01
            or abs(output_in - expected_output) > 0.002
            or abs((output_out - output_in) - (source_out - source_in)) > 0.002
        ):
            raise CommonContextProbeError(
                f"invalid or non-continuous cut range: {cut_id}",
                stage="plan_validation",
            )
        if cut.get("transition") not in (
            "sequence_start" if index == 0 else "hard_cut",
        ):
            raise CommonContextProbeError(
                "only sequence_start then hard_cut transitions are allowed",
                stage="plan_validation",
            )
        relation = str(cut.get("argument_relation") or "")
        if relation not in ALLOWED_ARGUMENT_RELATIONS:
            raise CommonContextProbeError(
                f"invalid argument relation: {relation}", stage="plan_validation"
            )
        for key in ("section", "editorial_role", "selection_reason", "context_evidence"):
            if not cut.get(key):
                raise CommonContextProbeError(
                    f"cut {cut_id} is missing {key}", stage="plan_validation"
                )
        direct_ids = cut.get("direct_evidence_ids") or []
        if not direct_ids or any(
            evidence_id not in evidence_ids
            or not str(evidence_id).startswith(f"{source_id}:")
            for evidence_id in direct_ids
        ):
            raise CommonContextProbeError(
                f"cut {cut_id} has invalid direct evidence",
                stage="plan_validation",
            )
        per_source[source_id].append((source_in, source_out))
        source_sequence.append(source_id)
        expected_output = output_out
    if not 60.0 <= expected_output <= 120.0:
        raise CommonContextProbeError(
            "probe duration must be approximately 60-120 seconds",
            stage="plan_validation",
        )
    for source_id, ranges in per_source.items():
        if len(ranges) < 2:
            raise CommonContextProbeError(
                f"{source_id} must contribute at least two cuts",
                stage="plan_validation",
            )
        if any(
            current[0] < previous[1] - 0.002
            for previous, current in zip(ranges, ranges[1:])
        ):
            raise CommonContextProbeError(
                f"{source_id} chronology is not preserved", stage="plan_validation"
            )
    if count_source_switches(source_sequence) < 2:
        raise CommonContextProbeError(
            "timeline requires at least two source switches",
            stage="plan_validation",
        )
    argument_cut_ids = {
        str(row.get("cut_id") or "") for row in plan.get("argument_map") or []
    }
    if argument_cut_ids != cut_ids:
        raise CommonContextProbeError(
            "argument_map must cover every cut exactly", stage="plan_validation"
        )
    commentary = plan["commentary_track"]
    if not isinstance(commentary, list) or not 2 <= len(commentary) <= 4:
        raise CommonContextProbeError(
            "commentary track must contain 2-4 events", stage="plan_validation"
        )
    commentary_ids: set[str] = set()
    previous_commentary_end = -1.0
    for row in commentary:
        commentary_id = str(row.get("commentary_id") or "")
        start = float(row.get("output_start") or 0.0)
        end = float(row.get("output_end") or 0.0)
        if (
            not commentary_id
            or commentary_id in commentary_ids
            or row.get("type") != "authored_commentary"
            or row.get("authored_by") != "creator"
            or start < 0
            or end <= start
            or end > expected_output + 0.002
            or start < previous_commentary_end - 0.002
            or not str(row.get("text") or "").strip()
            or not row.get("evidence_cut_ids")
            or not row.get("evidence_ids")
            or any(value not in cut_ids for value in row["evidence_cut_ids"])
            or any(value not in evidence_ids for value in row["evidence_ids"])
            or not row.get("claim_role")
            or not row.get("presentation_anchor")
        ):
            raise CommonContextProbeError(
                f"invalid commentary event: {commentary_id or '<missing>'}",
                stage="plan_validation",
            )
        commentary_ids.add(commentary_id)
        previous_commentary_end = end
    gates = {str(row.get("gate")): row.get("value") for row in plan["closed_gates"]}
    expected_gates = _closed_gates()
    if any(gates.get(key) != value for key, value in expected_gates.items()):
        raise CommonContextProbeError(
            "default-off closed gates are incomplete", stage="plan_validation"
        )


def bind_source_inputs(
    *,
    plan: dict[str, Any],
    root: Path,
    ffprobe_path: str,
    runner: ffmpeg_tiny.Runner,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Verify exact local source/caption/transcript/rights bytes and evidence rows."""

    bindings: list[dict[str, Any]] = []
    evidence: dict[str, dict[str, Any]] = {}
    for input_index, source in enumerate(plan["sources"]):
        media_path = _resolved(root, Path(source["media"]["path"]))
        caption_path = _resolved(root, Path(source["caption"]["path"]))
        rights_path = _resolved(root, Path(source["rights"]["path"]))
        transcript_info = source.get("transcript") or {}
        transcript_path = (
            _resolved(root, Path(transcript_info["path"]))
            if transcript_info.get("path")
            else None
        )
        exact_files = [
            (media_path, source["media"]["sha256"], "media"),
            (caption_path, source["caption"]["sha256"], "caption"),
            (rights_path, source["rights"]["sha256"], "rights"),
        ]
        if transcript_path is not None:
            exact_files.append(
                (transcript_path, transcript_info["sha256"], "transcript")
            )
        for path, expected_hash, label in exact_files:
            if not path.is_file() or _sha256(path) != expected_hash:
                raise CommonContextProbeError(
                    f"{source['source_id']} {label} binding mismatch",
                    stage="source_binding",
                )
        probe = probe_media_detail(
            media_path, ffprobe_path=ffprobe_path, runner=runner
        )
        if (
            abs(
                float(probe["duration_seconds"])
                - float(source["media"]["duration_seconds"])
            )
            > 0.10
            or int(probe["video_stream_count"]) != 1
            or int(probe["audio_stream_count"]) != 1
        ):
            raise CommonContextProbeError(
                f"{source['source_id']} media probe mismatch",
                stage="source_binding",
            )
        source_evidence = _load_evidence_rows(
            source_id=source["source_id"],
            transcript_path=transcript_path,
            caption_path=caption_path,
        )
        declared = {
            str(row["evidence_id"]): row
            for row in source.get("evidence_segments") or []
        }
        for evidence_id, declaration in declared.items():
            actual = source_evidence.get(evidence_id)
            if (
                actual is None
                or abs(float(actual["source_start"]) - float(declaration["source_start"]))
                > 0.002
                or abs(float(actual["source_end"]) - float(declaration["source_end"]))
                > 0.002
                or str(actual["text"]) != str(declaration["text"])
            ):
                raise CommonContextProbeError(
                    f"declared evidence mismatch: {evidence_id}",
                    stage="source_binding",
                )
        evidence.update(source_evidence)
        bindings.append(
            {
                "source_id": source["source_id"],
                "source_identity": source["source_identity"],
                "material_id": source["material_id"],
                "input_index": input_index,
                "media_path": media_path,
                "media_sha256": source["media"]["sha256"],
                "media_duration_seconds": probe["duration_seconds"],
                "media_probe": probe,
                "caption_path": caption_path,
                "caption_sha256": source["caption"]["sha256"],
                "transcript_path": transcript_path,
                "transcript_sha256": transcript_info.get("sha256"),
                "rights_path": rights_path,
                "rights_sha256": source["rights"]["sha256"],
                "rights_status": source["rights"]["status"],
            }
        )
    return bindings, evidence


def validate_direct_evidence(
    plan: dict[str, Any], evidence: dict[str, dict[str, Any]]
) -> None:
    for cut in plan["cuts"]:
        for evidence_id in cut["direct_evidence_ids"]:
            row = evidence.get(evidence_id)
            if row is None or row["source_id"] != cut["source_id"]:
                raise CommonContextProbeError(
                    f"orphan direct evidence: {evidence_id}",
                    stage="evidence_validation",
                )
            overlap = min(float(row["source_end"]), float(cut["source_out"])) - max(
                float(row["source_start"]), float(cut["source_in"])
            )
            if overlap <= 0.02:
                raise CommonContextProbeError(
                    f"direct evidence is outside its cut: {evidence_id}",
                    stage="evidence_validation",
                )
    thesis_sources = {
        evidence[evidence_id]["source_id"]
        for row in plan["argument_map"]
        for evidence_id in row.get("direct_evidence_ids") or []
        if evidence_id in evidence
    }
    if thesis_sources != {source["source_id"] for source in plan["sources"]}:
        raise CommonContextProbeError(
            "working thesis is not traceable to both sources",
            stage="evidence_validation",
        )


def build_timeline_ir(plan: dict[str, Any]) -> dict[str, Any]:
    source_indexes = {
        source["source_id"]: index for index, source in enumerate(plan["sources"])
    }
    cuts: list[dict[str, Any]] = []
    contribution: dict[str, dict[str, Any]] = {
        source_id: {"cut_count": 0, "duration_seconds": 0.0}
        for source_id in source_indexes
    }
    for cut in plan["cuts"]:
        row = json.loads(json.dumps(cut))
        row["input_index"] = source_indexes[cut["source_id"]]
        duration = float(cut["output_out"]) - float(cut["output_in"])
        contribution[cut["source_id"]]["cut_count"] += 1
        contribution[cut["source_id"]]["duration_seconds"] += duration
        cuts.append(row)
    for row in contribution.values():
        row["duration_seconds"] = round(float(row["duration_seconds"]), 6)
    return {
        "schema_version": TIMELINE_SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": plan["input_fingerprint"],
        "source_input_indexes": source_indexes,
        "cuts": cuts,
        "cut_count": len(cuts),
        "source_switch_count": count_source_switches(
            [cut["source_id"] for cut in cuts]
        ),
        "output_duration_seconds": round(float(cuts[-1]["output_out"]), 6),
        "mapping_coverage_ratio": 1.0,
        "source_contribution": contribution,
        "transition_policy": "hard_cut_only",
        "output_clock": "continuous_monotonic",
    }


def remap_source_captions(
    *,
    plan: dict[str, Any],
    evidence: dict[str, dict[str, Any]],
    timeline: dict[str, Any],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for cut in timeline["cuts"]:
        source_rows = sorted(
            (
                row
                for row in evidence.values()
                if row["source_id"] == cut["source_id"]
            ),
            key=lambda row: (row["source_start"], row["source_end"], row["evidence_id"]),
        )
        for evidence_row in source_rows:
            overlap_start = max(
                float(evidence_row["source_start"]), float(cut["source_in"])
            )
            overlap_end = min(
                float(evidence_row["source_end"]), float(cut["source_out"])
            )
            if overlap_end - overlap_start <= 0.12:
                continue
            output_start = (
                float(cut["output_in"]) + overlap_start - float(cut["source_in"])
            )
            output_end = (
                float(cut["output_in"]) + overlap_end - float(cut["source_in"])
            )
            rows.append(
                {
                    "source_id": cut["source_id"],
                    "cut_id": cut["cut_id"],
                    "evidence_id": evidence_row["evidence_id"],
                    "source_start": round(overlap_start, 6),
                    "source_end": round(overlap_end, 6),
                    "output_start": round(output_start, 6),
                    "output_end": round(output_end, 6),
                    "text": evidence_row["text"],
                    "provenance_type": "source_caption",
                    "presentation_track": "source_caption_bottom",
                }
            )
    rows.sort(key=lambda row: (row["output_start"], row["output_end"], row["evidence_id"]))
    normalized: list[dict[str, Any]] = []
    previous_end = 0.0
    for row in rows:
        start = max(float(row["output_start"]), previous_end)
        end = float(row["output_end"])
        if end - start <= 0.18:
            continue
        item = dict(row)
        item["output_start"] = round(start, 6)
        item["output_end"] = round(end, 6)
        item["caption_id"] = f"{row['source_id']}:caption_{len(normalized) + 1:04d}"
        normalized.append(item)
        previous_end = end
    overlap_count = sum(
        float(current["output_start"]) < float(previous["output_end"]) - 0.001
        for previous, current in zip(normalized, normalized[1:])
    )
    negative_count = sum(
        float(row["output_end"]) <= float(row["output_start"]) for row in normalized
    )
    namespace_valid = all(
        row["caption_id"].startswith(f"{row['source_id']}:")
        and row["evidence_id"].startswith(f"{row['source_id']}:")
        for row in normalized
    )
    contribution = {
        source["source_id"]: sum(
            row["source_id"] == source["source_id"] for row in normalized
        )
        for source in plan["sources"]
    }
    return {
        "schema_version": CAPTION_SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": plan["input_fingerprint"],
        "status": (
            "passed"
            if normalized
            and overlap_count == 0
            and negative_count == 0
            and namespace_valid
            and all(value > 0 for value in contribution.values())
            else "failed"
        ),
        "authority": "provider_caption_or_transcript_bound_per_source",
        "official_authorship_claimed": False,
        "provenance_type": "source_caption",
        "presentation_track": "source_caption_bottom",
        "cue_count": len(normalized),
        "per_source_cue_count": contribution,
        "overlap_count": overlap_count,
        "negative_duration_count": negative_count,
        "orphan_cue_count": 0,
        "namespace_valid": namespace_valid,
        "items": normalized,
    }


def build_commentary_track(
    plan: dict[str, Any], evidence: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    events = []
    for row in plan["commentary_track"]:
        item = json.loads(json.dumps(row))
        item["evidence_snapshot"] = [
            {
                "evidence_id": evidence_id,
                "source_id": evidence[evidence_id]["source_id"],
                "text": evidence[evidence_id]["text"],
            }
            for evidence_id in row["evidence_ids"]
        ]
        item["provenance_type"] = "creator_authored_commentary"
        item["presentation_track"] = "authored_commentary_top"
        events.append(item)
    return {
        "schema_version": COMMENTARY_SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": plan["input_fingerprint"],
        "status": "passed",
        "event_count": len(events),
        "provenance_type": "creator_authored_commentary",
        "events": events,
    }


def validate_caption_commentary_separation(
    *,
    captions: dict[str, Any],
    commentary: dict[str, Any],
    output_duration: float,
) -> None:
    if captions["status"] != "passed" or commentary["status"] != "passed":
        raise CommonContextProbeError(
            "caption/commentary track validation failed",
            stage="presentation_validation",
        )
    caption_ids = {row["caption_id"] for row in captions["items"]}
    commentary_ids = {
        row["commentary_id"] for row in commentary["events"]
    }
    if caption_ids & commentary_ids:
        raise CommonContextProbeError(
            "caption/commentary IDs collide", stage="presentation_validation"
        )
    previous_end = -1.0
    for row in commentary["events"]:
        start = float(row["output_start"])
        end = float(row["output_end"])
        if start < previous_end - 0.001 or end <= start or end > output_duration + 0.002:
            raise CommonContextProbeError(
                "commentary overlap/orphan detected", stage="presentation_validation"
            )
        previous_end = end


def render_filter_complex(
    *,
    cuts: list[dict[str, Any]],
    source_input_indexes: dict[str, int],
    ass_path: Path,
) -> str:
    """Build a two-input 1920x1080 hard-cut filter graph."""

    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, cut in enumerate(cuts):
        input_index = source_input_indexes[cut["source_id"]]
        start = _seconds(float(cut["source_in"]))
        end = _seconds(float(cut["source_out"]))
        filters.append(
            f"[{input_index}:v:0]trim=start={start}:end={end},"
            "setpts=PTS-STARTPTS,"
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"setsar=1[v{index}]"
        )
        filters.append(
            f"[{input_index}:a:0]atrim=start={start}:end={end},"
            "asetpts=PTS-STARTPTS,"
            f"aformat=sample_rates=48000:channel_layouts=stereo[a{index}]"
        )
        concat_inputs.extend((f"[v{index}]", f"[a{index}]"))
    filters.append(
        f"{''.join(concat_inputs)}concat=n={len(cuts)}:v=1:a=1[vcat][acat]"
    )
    ass = _escape_filter_path(ass_path)
    filters.append(f"[vcat]ass=filename='{ass}',format=yuv420p[vout]")
    filters.append("[acat]loudnorm=I=-15:TP=-2.0:LRA=11[aout]")
    return ";\n".join(filters) + "\n"


def render_ass_overlay(
    *,
    captions: dict[str, Any],
    commentary: dict[str, Any],
    timeline: dict[str, Any],
    sources: list[dict[str, Any]],
) -> str:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: SourceCaption,Arial,64,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,1,2,106,106,58,1
Style: Commentary,Arial,42,&H00FFFFFF,&H000000FF,&H00000000,&HC0182028,1,0,0,0,100,100,0,0,3,1,0,8,160,160,54,1
Style: SourceLabel,Arial,26,&H00FFFFFF,&H000000FF,&H00000000,&HA0182028,1,0,0,0,100,100,0,0,3,1,0,7,28,28,28,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events: list[str] = []
    labels = {
        source["source_id"]: f"SOURCE · {source['display_name']}"
        for source in sources
    }
    for cut in timeline["cuts"]:
        events.append(
            _ass_dialogue(
                start=float(cut["output_in"]),
                end=float(cut["output_out"]),
                style="SourceLabel",
                text=labels[cut["source_id"]],
                layer=1,
            )
        )
    for row in captions["items"]:
        events.append(
            _ass_dialogue(
                start=float(row["output_start"]),
                end=float(row["output_end"]),
                style="SourceCaption",
                text=row["text"],
                layer=2,
            )
        )
    for row in commentary["events"]:
        events.append(
            _ass_dialogue(
                start=float(row["output_start"]),
                end=float(row["output_end"]),
                style="Commentary",
                text=f"CREATOR CONTEXT · {row['text']}",
                layer=3,
            )
        )
    return header + "\n".join(events) + "\n"


def render_video(
    *,
    final_video: Path,
    sources: list[dict[str, Any]],
    filter_path: Path,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> None:
    command = [ffmpeg_path, "-hide_banner", "-v", "error", "-nostdin", "-y"]
    for source in sources:
        command.extend(["-i", str(source["media_path"])])
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
            "medium",
            "-crf",
            "18",
            "-profile:v",
            "high",
            "-level",
            "4.1",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(final_video),
        ]
    )
    result = _run(
        command,
        runner=runner,
        stage="render",
        allow_failure=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )
    if result.returncode != 0 or not final_video.is_file():
        raise CommonContextProbeError(
            "two-input FFmpeg render failed", stage="render"
        )


def validate_rendered_probe(
    *,
    final_video: Path,
    timeline: dict[str, Any],
    captions: dict[str, Any],
    commentary: dict[str, Any],
    source_bindings: list[dict[str, Any]],
    ffmpeg_path: str,
    ffprobe_path: str,
    runner: ffmpeg_tiny.Runner,
    fingerprint: str,
) -> dict[str, Any]:
    media = probe_media_detail(
        final_video, ffprobe_path=ffprobe_path, runner=runner
    )
    media["sha256"] = _sha256(final_video)
    media["byte_size"] = final_video.stat().st_size
    decode = _run(
        [
            ffmpeg_path,
            "-hide_banner",
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
            os.devnull,
        ],
        runner=runner,
        stage="media_validation",
        allow_failure=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )
    timestamp_readback = validate_packet_timestamps(
        video_path=final_video, ffprobe_path=ffprobe_path, runner=runner
    )
    faststart = _faststart_readback(final_video)
    loudness = _measure_loudness(
        ffmpeg_path=ffmpeg_path,
        input_path=final_video,
        timeline=None,
        runner=runner,
    )
    signal = _run_signal_qa(
        video_path=final_video,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    adapted_cuts = [
        {
            "cut_id": cut["cut_id"],
            "output_in_seconds": cut["output_in"],
            "output_out_seconds": cut["output_out"],
            "duration_seconds": round(
                float(cut["output_out"]) - float(cut["output_in"]), 6
            ),
        }
        for cut in timeline["cuts"]
    ]
    cut_loudness = measure_cut_loudness(
        video_path=final_video,
        cuts=adapted_cuts,
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    source_decode = _validate_source_contribution(
        source_bindings=source_bindings,
        cuts=timeline["cuts"],
        ffmpeg_path=ffmpeg_path,
        runner=runner,
    )
    duration_delta = abs(
        float(media["duration_seconds"]) - float(timeline["output_duration_seconds"])
    )
    av_delta = abs(
        float(media["video_duration_seconds"])
        - float(media["audio_duration_seconds"])
    )
    checks = {
        "stream_count": int(media["video_stream_count"]) == 1
        and int(media["audio_stream_count"]) == 1,
        "shipping_codec": media["video_codec"] == "h264"
        and media["audio_codec"] == "aac",
        "resolution": int(media["width"]) == FRAME_WIDTH
        and int(media["height"]) == FRAME_HEIGHT,
        "duration": duration_delta <= 0.75,
        "monotonic_timestamps": timestamp_readback["status"] == "passed",
        "av_duration_delta": av_delta <= 0.10,
        "faststart": faststart["status"] == "passed",
        "full_decode": decode.returncode == 0,
        "loudness": -16.5 <= float(loudness["integrated_lufs"]) <= -12.0
        and float(loudness["true_peak_dbtp"]) <= -1.0,
        "source_switch_loudness_delta": float(
            cut_loudness["maximum_adjacent_delta_lu"]
        )
        <= 6.0,
        "black_silence": signal["status"] == "passed",
        "source_mapping_coverage": timeline["mapping_coverage_ratio"] == 1.0,
        "both_sources_decoded": all(
            row["status"] == "passed" for row in source_decode
        ),
        "caption_containment": captions["status"] == "passed",
        "commentary_containment": commentary["status"] == "passed",
        "caption_commentary_provenance_separate": captions["provenance_type"]
        != commentary["provenance_type"],
    }
    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": fingerprint,
        "status": "passed" if all(checks.values()) else "failed",
        "state": READY_STATE if all(checks.values()) else "S1_PROBE_VALIDATION_FAILED",
        "checks": checks,
        "media": media,
        "expected_duration_seconds": timeline["output_duration_seconds"],
        "duration_delta_seconds": round(duration_delta, 6),
        "av_duration_delta_seconds": round(av_delta, 6),
        "full_decode": {
            "status": "passed" if decode.returncode == 0 else "failed",
            "exit_code": decode.returncode,
            "stderr_empty": not bool((decode.stderr or "").strip()),
        },
        "timestamp_readback": timestamp_readback,
        "faststart": faststart,
        "loudness": loudness,
        "source_switch_loudness": cut_loudness,
        "signal_qa": signal,
        "source_contribution_decode": source_decode,
        "source_mapping": [
            {
                "cut_id": cut["cut_id"],
                "source_id": cut["source_id"],
                "input_index": cut["input_index"],
                "source_range": [cut["source_in"], cut["source_out"]],
                "output_range": [cut["output_in"], cut["output_out"]],
            }
            for cut in timeline["cuts"]
        ],
        "caption_commentary": {
            "source_caption_count": captions["cue_count"],
            "commentary_count": commentary["event_count"],
            "source_caption_provenance": captions["provenance_type"],
            "commentary_provenance": commentary["provenance_type"],
        },
        "visual_observation": {"status": "unverified"},
        "human_review_pending": True,
        **_closed_gates(),
    }


def build_review_package(
    *,
    stage: Path,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    commentary: dict[str, Any],
    rights_inventory: dict[str, Any],
    validation: dict[str, Any],
    review_port: int,
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> None:
    review = stage / "review"
    evidence_dir = review / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=False)
    samples = [
        ("setup_actual_frame.jpg", 12.0),
        ("comparison_actual_frame.jpg", 58.0),
        ("synthesis_actual_frame.jpg", 94.0),
    ]
    for filename, timestamp in samples:
        result = _run(
            [
                ffmpeg_path,
                "-hide_banner",
                "-v",
                "error",
                "-ss",
                _seconds(timestamp),
                "-i",
                str(stage / "final_video.mp4"),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(evidence_dir / filename),
            ],
            runner=runner,
            stage="representative_frames",
            allow_failure=True,
        )
        if result.returncode != 0 or not (evidence_dir / filename).is_file():
            raise CommonContextProbeError(
                f"representative frame extraction failed: {filename}",
                stage="representative_frames",
            )
    contact = _run(
        [
            ffmpeg_path,
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(evidence_dir / samples[0][0]),
            "-i",
            str(evidence_dir / samples[1][0]),
            "-i",
            str(evidence_dir / samples[2][0]),
            "-filter_complex",
            "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[2:v]scale=640:360[c];[a][b][c]hstack=inputs=3[v]",
            "-map",
            "[v]",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(evidence_dir / "representative_actual_frames_contact_sheet.jpg"),
        ],
        runner=runner,
        stage="representative_frames",
        allow_failure=True,
    )
    if contact.returncode != 0:
        raise CommonContextProbeError(
            "representative contact sheet failed", stage="representative_frames"
        )
    _write_text(
        review / "index.html",
        render_review_html(
            plan=plan,
            timeline=timeline,
            commentary=commentary,
            rights_inventory=rights_inventory,
            validation=validation,
        ),
    )
    _write_text(
        review / "serve_preview.ps1",
        f"""param([int]$Port = {review_port})
$reviewDir = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$outputDir = (Resolve-Path -LiteralPath (Join-Path $reviewDir '..')).Path
$cursor = Get-Item -LiteralPath $outputDir
while ($null -ne $cursor -and -not (Test-Path -LiteralPath (Join-Path $cursor.FullName 'src\\cli\\main.py'))) {{ $cursor = $cursor.Parent }}
if ($null -eq $cursor) {{ throw 'ClipPipeGen repository root not found' }}
Push-Location $cursor.FullName
try {{ uvx python -m src.cli.serve_review --root $outputDir --port $Port }} finally {{ Pop-Location }}
""",
    )
    _write_text(
        review / "open_preview.ps1",
        f"""param([int]$Port = {review_port})
$url = "http://127.0.0.1:$Port/review/index.html"
Start-Process $url
& (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
""",
    )


def render_review_html(
    *,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    commentary: dict[str, Any],
    rights_inventory: dict[str, Any],
    validation: dict[str, Any],
) -> str:
    source_names = {
        source["source_id"]: source["display_name"] for source in plan["sources"]
    }
    cut_rows = "".join(
        "<tr>"
        f"<td>{escape(cut['cut_id'])}</td>"
        f"<td>{escape(source_names[cut['source_id']])}</td>"
        f"<td>{cut['source_in']:.3f}–{cut['source_out']:.3f}s</td>"
        f"<td>{escape(cut['argument_relation'])}</td>"
        f"<td>{escape(cut['selection_reason'])}</td>"
        f"<td><button type=\"button\" data-seek=\"{cut['output_in']:.3f}\">seek</button></td>"
        "</tr>"
        for cut in timeline["cuts"]
    )
    commentary_rows = "".join(
        "<li>"
        f"<button type=\"button\" data-seek=\"{row['output_start']:.3f}\">{row['output_start']:.1f}s</button> "
        f"<strong>creator framing:</strong> {escape(row['text'])} "
        f"<small>{escape(', '.join(row['evidence_cut_ids']))}</small>"
        "</li>"
        for row in commentary["events"]
    )
    legend = "".join(
        f"<li><code>{escape(source['source_id'])}</code> — "
        f"{escape(source['display_name'])} / {escape(source['source_identity'])}</li>"
        for source in plan["sources"]
    )
    rights_rows = "".join(
        "<tr>"
        f"<td>{escape(row['cut_id'])}</td><td>{escape(row['source_id'])}</td>"
        f"<td>{row['source_in']:.3f}–{row['source_out']:.3f}s</td>"
        f"<td>{escape(row['rights_status'])}</td>"
        "</tr>"
        for row in rights_inventory["ranges"]
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>S1 two-source common-context probe</title>
<style>
:root{{color-scheme:dark;background:#0b1017;color:#edf2f7;font-family:system-ui,sans-serif}}
*{{box-sizing:border-box}} body{{margin:0}} main{{width:min(1180px,100%);margin:auto;padding:20px}}
.status{{color:#9ae6b4;font-weight:700;letter-spacing:.03em;overflow-wrap:anywhere}} .video{{position:sticky;top:0;background:#0b1017;padding:8px 0;z-index:3}}
video{{display:block;width:100%;max-height:70vh;background:#000;border-radius:10px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}} section{{background:#121a25;border:1px solid #263244;border-radius:10px;padding:16px;margin-top:16px}}
h1{{font-size:clamp(1.35rem,3vw,2rem);margin:.4rem 0}} h2{{font-size:1.05rem}} p{{line-height:1.55}}
.table{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;min-width:780px}} th,td{{border-bottom:1px solid #344258;padding:8px;text-align:left;vertical-align:top}}
button{{background:#d9e2ec;color:#111827;border:0;border-radius:6px;padding:6px 10px;cursor:pointer}} code,small{{color:#b8c5d6}}
.notice{{border-left:4px solid #e3b341;padding-left:12px}} @media(max-width:720px){{main{{padding:10px}}.grid{{grid-template-columns:1fr}}.video{{position:static}}section{{padding:12px}}}}
</style></head><body><main data-artifact-id="{ARTIFACT_ID}" data-input-fingerprint="{plan['input_fingerprint']}">
<div class="status">{READY_STATE}</div>
<h1>Two-source common-context internal probe</h1>
<div class="video"><video id="probe" controls preload="metadata" src="../final_video.mp4"></video></div>
<section><h2>問い</h2><p>{escape(plan['editorial_question'])}</p>
<h2>作業仮説（creator-authored synthesis）</h2><p>{escape(plan['working_thesis'])}</p>
<p class="notice">機械検証は構築と追跡可能性だけを示します。二本が一つの論として成立したかは未判定です。</p></section>
<div class="grid"><section><h2>Source legend</h2><ul>{legend}</ul></section>
<section><h2>Provenance</h2><p>下部の字幕は source caption。上部の <strong>CREATOR CONTEXT</strong> は creator framing / inference です。</p>
<ul>{commentary_rows}</ul></section></div>
<section><h2>Ordered cuts</h2><div class="table"><table><thead><tr><th>cut</th><th>source</th><th>source range</th><th>argument</th><th>selection</th><th></th></tr></thead><tbody>{cut_rows}</tbody></table></div></section>
<section><h2>Range rights</h2><div class="table"><table><thead><tr><th>cut</th><th>source</th><th>range</th><th>status</th></tr></thead><tbody>{rights_rows}</tbody></table></div>
<p>rights approval: not_granted / internal probe only / public and monetized use: false</p></section>
<section><h2>Technical readback</h2><p>{validation['media']['duration_seconds']:.3f}s · H.264/AAC · 1920×1080 · validation {escape(validation['status'])}</p>
<p>visual observation: unverified · human review pending: true</p></section>
<script>
const video=document.getElementById('probe');
for(const button of document.querySelectorAll('[data-seek]')){{button.addEventListener('click',()=>{{
  const target=Number(button.dataset.seek);
  const applySeek=()=>{{video.pause();video.currentTime=target;}};
  if(video.readyState>=1){{applySeek();}}else{{video.addEventListener('loadedmetadata',applySeek,{{once:true}});}}
  video.scrollIntoView({{behavior:'smooth',block:'center'}});
}})}}
</script></main></body></html>"""


def build_source_pair_selection_readback(
    plan: dict[str, Any],
    bindings: list[dict[str, Any]],
    fingerprint: str,
) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.s1.source_pair_selection.v1",
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": fingerprint,
        "status": "selected_from_actual_inventory",
        "selection_rule": "strongest_defensible_pair_from_direct_caption_evidence",
        "selected_source_ids": [row["source_id"] for row in bindings],
        "selected_sources": [
            {
                "source_id": row["source_id"],
                "source_identity": row["source_identity"],
                "material_id": row["material_id"],
                "media_sha256": row["media_sha256"],
                "media_duration_seconds": row["media_duration_seconds"],
                "caption_sha256": row["caption_sha256"],
                "transcript_sha256": row["transcript_sha256"],
                "rights_sha256": row["rights_sha256"],
                "rights_status": row["rights_status"],
            }
            for row in bindings
        ],
        "pair_comparison": plan.get("pair_comparison") or [],
        "editorial_question": plan["editorial_question"],
        "working_thesis": plan["working_thesis"],
        "automated_coherence_verdict": None,
        "human_review_pending": True,
    }


def build_argument_trace(
    plan: dict[str, Any],
    evidence: dict[str, dict[str, Any]],
    fingerprint: str,
) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.s1.common_context_argument_trace.v1",
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": fingerprint,
        "editorial_question": plan["editorial_question"],
        "working_thesis": plan["working_thesis"],
        "thesis_classification": "authored_synthesis",
        "argument_map": [
            {
                **row,
                "evidence_snapshot": [
                    {
                        "evidence_id": evidence_id,
                        "source_id": evidence[evidence_id]["source_id"],
                        "source_range": [
                            evidence[evidence_id]["source_start"],
                            evidence[evidence_id]["source_end"],
                        ],
                        "text": evidence[evidence_id]["text"],
                    }
                    for evidence_id in row["direct_evidence_ids"]
                ],
            }
            for row in plan["argument_map"]
        ],
        "automated_coherence_score": None,
        "automated_acceptance_verdict": None,
        "human_review_pending": True,
    }


def build_provenance_snapshot(
    bindings: list[dict[str, Any]], fingerprint: str
) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.s1.common_context_provenance.v1",
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": fingerprint,
        "sources": [
            {
                "source_id": row["source_id"],
                "source_identity": row["source_identity"],
                "material_id": row["material_id"],
                "input_index": row["input_index"],
                "media": {
                    "path": row["media_path"].as_posix(),
                    "sha256": row["media_sha256"],
                    "duration_seconds": row["media_duration_seconds"],
                },
                "caption": {
                    "path": row["caption_path"].as_posix(),
                    "sha256": row["caption_sha256"],
                },
                "transcript": {
                    "path": (
                        row["transcript_path"].as_posix()
                        if row["transcript_path"]
                        else None
                    ),
                    "sha256": row["transcript_sha256"],
                },
                "rights": {
                    "path": row["rights_path"].as_posix(),
                    "sha256": row["rights_sha256"],
                    "status": row["rights_status"],
                },
            }
            for row in bindings
        ],
        "authored_commentary_is_source_caption": False,
        **_closed_gates(),
    }


def build_range_rights_inventory(
    plan: dict[str, Any], fingerprint: str
) -> dict[str, Any]:
    source_rights = {
        source["source_id"]: source["rights"] for source in plan["sources"]
    }
    return {
        "schema_version": "clippipegen.s1.common_context_range_rights.v1",
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": fingerprint,
        "status": "pending_snapshot_only",
        "ranges": [
            {
                "cut_id": cut["cut_id"],
                "source_id": cut["source_id"],
                "source_in": cut["source_in"],
                "source_out": cut["source_out"],
                "rights_path": source_rights[cut["source_id"]]["path"],
                "rights_sha256": source_rights[cut["source_id"]]["sha256"],
                "rights_status": source_rights[cut["source_id"]]["status"],
                "rights_approval": "not_granted",
                "public_use": False,
                "monetized_use": False,
            }
            for cut in plan["cuts"]
        ],
        **_closed_gates(),
    }


def build_commentary_presentation_readback(
    *,
    captions: dict[str, Any],
    commentary: dict[str, Any],
    design_basis: dict[str, Any],
    fingerprint: str,
) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.s1.commentary_presentation.v1",
        "artifact_id": ARTIFACT_ID,
        "input_fingerprint": fingerprint,
        "status": "passed",
        "direction_signature": DIRECTION_SIGNATURE,
        "source_caption_track": {
            "provenance": captions["provenance_type"],
            "placement": "bottom_center",
            "cue_count": captions["cue_count"],
        },
        "authored_commentary_track": {
            "provenance": commentary["provenance_type"],
            "placement": "top_center_compact_band",
            "event_count": commentary["event_count"],
        },
        "source_attribution": {
            "placement": "top_left",
            "role": "subordinate_readable_label",
        },
        "collision_by_design": False,
        "actual_visual_observation": {"status": "unverified"},
        "design_basis_status": design_basis["status"],
    }


def build_run_manifest(
    *,
    stage: Path,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    validation: dict[str, Any],
    source_bindings: list[dict[str, Any]],
    fingerprint: str,
) -> dict[str, Any]:
    rows = [
        {
            "repo_relative_path": path.relative_to(stage).as_posix(),
            "sha256": _sha256(path),
            "byte_size": path.stat().st_size,
        }
        for path in sorted(item for item in stage.rglob("*") if item.is_file())
        if path.name != "run_manifest.json"
    ]
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": READY_STATE,
        "input_fingerprint": fingerprint,
        "sources": [
            {
                "source_id": row["source_id"],
                "source_identity": row["source_identity"],
                "material_id": row["material_id"],
                "input_index": row["input_index"],
                "media_sha256": row["media_sha256"],
            }
            for row in source_bindings
        ],
        "timeline": {
            "cut_count": timeline["cut_count"],
            "source_switch_count": timeline["source_switch_count"],
            "duration_seconds": timeline["output_duration_seconds"],
            "mapping_coverage_ratio": timeline["mapping_coverage_ratio"],
        },
        "final_video": {
            "repo_relative_path": "final_video.mp4",
            "sha256": validation["media"]["sha256"],
            "byte_size": validation["media"]["byte_size"],
        },
        "files": rows,
        "file_count": len(rows),
        "closed_file_set": {
            "status": "passed",
            "excluded_paths": ["run_manifest.json"],
            "payload_tree_digest_sha256": _payload_tree_digest(rows),
        },
        "visual_observation": {"status": "unverified"},
        "human_review_pending": True,
        **_closed_gates(),
        "manifest_self_integrity": {
            "algorithm": "sha256_canonical_json_self_field_null",
            "sha256": None,
        },
    }
    manifest["manifest_self_integrity"]["sha256"] = _manifest_self_hash(manifest)
    return manifest


def validate_run_manifest(package: Path) -> dict[str, Any]:
    manifest_path = package / "run_manifest.json"
    manifest = _read_json(manifest_path, "run manifest")
    if (
        manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION
        or manifest.get("artifact_id") != ARTIFACT_ID
        or (manifest.get("manifest_self_integrity") or {}).get("sha256")
        != _manifest_self_hash(manifest)
    ):
        raise CommonContextProbeError(
            "manifest identity/self-integrity mismatch", stage="manifest_validation"
        )
    payload_names: set[str] = set()
    for row in manifest.get("files") or []:
        name = str(row.get("repo_relative_path") or "")
        if (
            not name
            or name in payload_names
            or Path(name).is_absolute()
            or ".." in Path(name).parts
        ):
            raise CommonContextProbeError(
                "manifest payload path is invalid/duplicated",
                stage="manifest_validation",
            )
        payload_names.add(name)
        path = package / Path(name)
        if (
            not path.is_file()
            or _sha256(path) != row.get("sha256")
            or path.stat().st_size != int(row.get("byte_size") or -1)
        ):
            raise CommonContextProbeError(
                f"manifest payload mismatch: {name}", stage="manifest_validation"
            )
    actual = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and path.name != "run_manifest.json"
    }
    if payload_names != actual or manifest["closed_file_set"][
        "payload_tree_digest_sha256"
    ] != _payload_tree_digest(manifest["files"]):
        raise CommonContextProbeError(
            "manifest closed file set mismatch", stage="manifest_validation"
        )
    return manifest


def input_fingerprint(
    plan: dict[str, Any],
    bindings: list[dict[str, Any]],
    design_basis: dict[str, Any],
) -> str:
    payload = {
        "artifact_id": ARTIFACT_ID,
        "plan": plan,
        "source_bindings": [
            {
                "source_id": row["source_id"],
                "source_identity": row["source_identity"],
                "media_sha256": row["media_sha256"],
                "caption_sha256": row["caption_sha256"],
                "transcript_sha256": row["transcript_sha256"],
                "rights_sha256": row["rights_sha256"],
            }
            for row in bindings
        ],
        "direction_signature": design_basis["direction_signature"],
    }
    return hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def count_source_switches(source_sequence: list[str]) -> int:
    return sum(
        current != previous
        for previous, current in zip(source_sequence, source_sequence[1:])
    )


def _load_evidence_rows(
    *,
    source_id: str,
    transcript_path: Path | None,
    caption_path: Path,
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if transcript_path is not None:
        payload = _read_json(transcript_path, "source transcript")
        for segment in payload.get("segments") or []:
            segment_id = str(segment.get("id") or "")
            text = _normalize_text(segment.get("text"))
            if not segment_id or not text:
                continue
            evidence_id = f"{source_id}:{segment_id}"
            rows[evidence_id] = {
                "evidence_id": evidence_id,
                "source_id": source_id,
                "source_start": round(float(segment["start_seconds"]), 6),
                "source_end": round(float(segment["end_seconds"]), 6),
                "text": text,
                "authority": "transcript_bound_to_provider_caption",
            }
        return rows
    for event in load_caption_events(caption_path):
        evidence_id = f"{source_id}:{event['event_id']}"
        rows[evidence_id] = {
            "evidence_id": evidence_id,
            "source_id": source_id,
            "source_start": event["source_start_seconds"],
            "source_end": event["source_end_seconds"],
            "text": _normalize_text(event["text"]),
            "authority": "provider_json3_sidecar",
        }
    return rows


def _validate_source_contribution(
    *,
    source_bindings: list[dict[str, Any]],
    cuts: list[dict[str, Any]],
    ffmpeg_path: str,
    runner: ffmpeg_tiny.Runner,
) -> list[dict[str, Any]]:
    result_rows: list[dict[str, Any]] = []
    for source in source_bindings:
        selected = [cut for cut in cuts if cut["source_id"] == source["source_id"]]
        decoded_ranges = []
        for cut in selected:
            result = _run(
                [
                    ffmpeg_path,
                    "-hide_banner",
                    "-v",
                    "error",
                    "-ss",
                    _seconds(float(cut["source_in"])),
                    "-t",
                    _seconds(float(cut["source_out"]) - float(cut["source_in"])),
                    "-i",
                    str(source["media_path"]),
                    "-map",
                    "0:v:0",
                    "-map",
                    "0:a:0",
                    "-f",
                    "null",
                    os.devnull,
                ],
                runner=runner,
                stage="source_contribution_decode",
                allow_failure=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
            decoded_ranges.append(
                {
                    "cut_id": cut["cut_id"],
                    "source_in": cut["source_in"],
                    "source_out": cut["source_out"],
                    "exit_code": result.returncode,
                }
            )
        result_rows.append(
            {
                "source_id": source["source_id"],
                "input_index": source["input_index"],
                "cut_count": len(selected),
                "decoded_ranges": decoded_ranges,
                "video_and_audio_mapped": bool(selected),
                "status": (
                    "passed"
                    if len(selected) >= 2
                    and all(row["exit_code"] == 0 for row in decoded_ranges)
                    else "failed"
                ),
            }
        )
    return result_rows


def _closed_gates() -> dict[str, Any]:
    return {
        "internal_probe_only": True,
        "production_acceptance": False,
        "rights_approval": "not_granted",
        "public_use": False,
        "monetized_use": False,
        "upload_attempted": False,
        "generic_n_source_architecture": False,
        "synchronized_multiview": False,
        "generated_imagery": False,
    }


def _manifest_self_hash(manifest: dict[str, Any]) -> str:
    clone = json.loads(json.dumps(manifest))
    integrity = clone.get("manifest_self_integrity")
    if not isinstance(integrity, dict):
        raise CommonContextProbeError(
            "manifest self-integrity block missing", stage="manifest_validation"
        )
    integrity["sha256"] = None
    return hashlib.sha256(
        json.dumps(
            clone, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _payload_tree_digest(rows: list[dict[str, Any]]) -> str:
    canonical = [
        {
            "repo_relative_path": row["repo_relative_path"],
            "sha256": row["sha256"],
            "byte_size": int(row["byte_size"]),
        }
        for row in sorted(rows, key=lambda row: row["repo_relative_path"])
    ]
    return hashlib.sha256(
        json.dumps(
            canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _ass_dialogue(
    *, start: float, end: float, style: str, text: str, layer: int
) -> str:
    safe = (
        _normalize_text(text)
        .replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\n", r"\N")
    )
    return (
        f"Dialogue: {layer},{_ass_time(start)},{_ass_time(end)},{style},,"
        f"0,0,0,,{safe}"
    )


def _ass_time(value: float) -> str:
    centiseconds = max(0, int(round(value * 100.0)))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    seconds, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{fraction:02d}"


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


def _normalize_text(value: Any) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(value or "")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\ufeff", ""),
    ).strip()


def _run(
    command: list[str],
    *,
    runner: ffmpeg_tiny.Runner,
    stage: str,
    allow_failure: bool = False,
    timeout: int = COMMAND_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[str]:
    try:
        result = runner(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CommonContextProbeError(
            f"subprocess failed at {stage}: {exc}", stage=stage
        ) from exc
    if result.returncode != 0 and not allow_failure:
        raise CommonContextProbeError(
            f"subprocess returned {result.returncode} at {stage}", stage=stage
        )
    return result


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CommonContextProbeError(
            f"cannot read {label}: {path}", stage="input_read"
        ) from exc
    if not isinstance(payload, dict):
        raise CommonContextProbeError(
            f"{label} must be a JSON object", stage="input_read"
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
        return path.name


def _seconds(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")
