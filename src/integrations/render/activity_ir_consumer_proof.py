"""Materialize an exact-plan activity chronology as a private review proof.

This adapter is intentionally narrow.  It consumes the immutable S2 activity
plan and already-retained source/caption bytes, produces a new diagnostic MP4,
and keeps all human, rights, production, and publication decisions closed.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

from src.integrations.render.real_video_pipeline import load_caption_events
from src.pipeline.editorial_form_selection import (
    ACTIVITY_CHRONOLOGY_VARIANT_ID,
    EditorialFormValidationError,
    normalize_editorial_form_plan,
)


ARTIFACT_ID = "clip-s2-activity-ir-consumer-proof-v1-001"
STATE = "NON_ADOPTED_REVIEW_PROOF"
LEGACY_PLAN_SHA256 = "36d5bbe3fec3c6fb0e69b76bcc7cdc5c7b7fb03f73aeadd79a7ad2a95b1b1988"
FONT_SHA256 = "d5795bdff960c2b2ec5727ffeb79d836f8f11dac3015f6e16089a912e9cced6f"
EXPECTED_SOURCES = {
    "youtube:ib3DwHDI71Q": "cf6a010a26c1a159b902bb5412f952086c365ce7e73d3775ee5a25aaaa11d353",
    "youtube:rltNvZ_FY8Q": "5e026c94f40acd0dfc32a5ab610300a7bccbe3cd66441a7d9cc703cc7b83d240",
}
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
FPS = 30
SUBTITLE_FONT_SIZE = 54
SUBTITLE_SAFE_WIDTH = 1500
MIN_CUE_SECONDS = 0.12


class ActivityIRConsumerError(RuntimeError):
    """Fail-closed materialization error."""

    def __init__(self, message: str, *, stage: str) -> None:
        super().__init__(message)
        self.stage = stage


def build_package(
    *,
    repo: Path,
    legacy_plan_path: Path,
    output_dir: Path,
    font_path: Path,
    chrome_path: Path,
) -> dict[str, Any]:
    global ARTIFACT_ID
    repo = repo.resolve()
    plan_path = legacy_plan_path.resolve()
    target = output_dir.resolve()
    if not re.fullmatch(r"clip-[a-z0-9][a-z0-9-]{15,127}", target.name):
        raise ActivityIRConsumerError(
            "output directory name must be the explicit clip-* artifact identity",
            stage="artifact_identity",
        )
    ARTIFACT_ID = target.name
    if target.exists():
        raise ActivityIRConsumerError(
            f"refusing to overwrite output: {target}", stage="exclusive_output"
        )
    staging = target.parent / f".{target.name}.staging"
    if staging.exists():
        raise ActivityIRConsumerError(
            f"refusing to overwrite retained staging: {staging}",
            stage="exclusive_output",
        )

    plan = _read_json(plan_path)
    source_bindings = _validate_exact_inputs(repo, plan_path, plan, font_path)
    direct_validation = _direct_validator_attempt(plan)
    adapted_plan = _adapt_legacy_plan(plan)
    normalized_ir = normalize_editorial_form_plan(
        adapted_plan, variant_id=ACTIVITY_CHRONOLOGY_VARIANT_ID
    )

    staging.mkdir(parents=True)
    try:
        (staging / "review" / "evidence" / "full").mkdir(parents=True)
        (staging / "review" / "evidence" / "mobile").mkdir(parents=True)
        (staging / "assets").mkdir(parents=True)
        shutil.copy2(font_path, staging / "assets" / "keifont.ttf")
        shutil.copy2(plan_path, staging / "legacy_activity_plan.json")
        _write_json(staging / "adapted_editorial_form_plan.json", adapted_plan)
        _write_json(staging / "normalized_ir.json", normalized_ir)
        _write_json(staging / "source_binding.json", source_bindings)
        _write_json(staging / "legacy_validator_attempt.json", direct_validation)

        timeline = _build_timeline(plan, normalized_ir)
        caption_rows, caption_stats = _build_caption_rows(repo, plan, timeline)
        width_readback = _measure_and_wrap_subtitles(
            staging=staging,
            rows=caption_rows,
        )
        if width_readback["status"] != "passed":
            raise ActivityIRConsumerError(
                "subtitle measurement did not pass", stage="subtitle_measurement"
            )
        _write_json(staging / "timeline_map.json", timeline)
        _write_json(
            staging / "subtitle_readback.json",
            {
                "schema_version": "clippipegen.activity_ir_consumer_subtitles.v1",
                "artifact_id": ARTIFACT_ID,
                "status": "passed",
                "provider_timing_preserved": True,
                "cue_start_delay_seconds": {"average": 0.0, "maximum": 0.0},
                "overlap_resolution": caption_stats,
                "measurement": width_readback,
                "cues": caption_rows,
            },
        )

        _write_text(staging / "overlay.ass", _render_ass(plan, caption_rows))
        _write_text(staging / "render_filter.txt", _render_filter(plan))
        command = _render_command(repo, staging, plan)
        _write_json(
            staging / "render_command.json",
            {
                "schema_version": "clippipegen.activity_ir_consumer_render_command.v1",
                "artifact_id": ARTIFACT_ID,
                "command": command,
                "working_directory": ".",
                "network_access": False,
                "source_fetch": False,
                "production_candidate": False,
            },
        )
        rendered = _run(command, cwd=staging, timeout=1200)
        _write_json(
            staging / "render_result.json",
            {
                "schema_version": "clippipegen.activity_ir_consumer_render_result.v1",
                "artifact_id": ARTIFACT_ID,
                "exit_code": rendered.returncode,
                "stderr_sha256": _sha256_bytes(rendered.stderr.encode("utf-8")),
                "font_selection_observed": "Keifont" in rendered.stderr,
                "stderr_tail": rendered.stderr[-4000:],
            },
        )
        final_video = staging / "final_video.mp4"
        probe = _probe(final_video, staging)
        validation = _validate_media(staging, probe, timeline)
        _build_review_frames(staging, timeline)
        _build_review_surface(staging, plan, timeline, width_readback)
        html_readback = _http_and_viewport_readback(staging, chrome_path)
        _write_json(staging / "html_readback.json", html_readback)

        receipt = _build_receipt(
            plan_path=plan_path,
            plan=plan,
            normalized_ir_path=staging / "normalized_ir.json",
            source_bindings=source_bindings,
            direct_validation=direct_validation,
            final_video=final_video,
            probe=probe,
            timeline=timeline,
            caption_stats=caption_stats,
            width_readback=width_readback,
            validation=validation,
            html_readback=html_readback,
        )
        _write_json(staging / "consumer_receipt.json", receipt)
        _write_json(staging / "validation.json", validation)
        manifest = _build_manifest(staging, final_video, probe)
        _write_json(staging / "run_manifest.json", manifest)
        _validate_manifest(staging)
        staging.rename(target)
        _validate_manifest(target)
    except Exception as exc:
        if staging.exists():
            failure = {
                "artifact_id": ARTIFACT_ID,
                "state": "MATERIALIZATION_FAILED",
                "stage": getattr(exc, "stage", "unclassified"),
                "error_type": type(exc).__name__,
                "message": str(exc),
            }
            _write_json(staging / "build_failure.json", failure)
        raise

    video = target / "final_video.mp4"
    result = {
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "artifact_path": target.as_posix(),
        "final_video": {
            "path": "final_video.mp4",
            "sha256": _sha256(video),
            "byte_size": video.stat().st_size,
            "duration_seconds": float(probe["format"]["duration"]),
        },
        "manifest_sha256": _sha256(target / "run_manifest.json"),
        "review_entry": (target / "review" / "index.html").as_posix(),
        "human_editorial_acceptance": False,
        "semantic_winner_selected": False,
        "rights_approval": False,
        "production_acceptance": False,
        "publication_or_upload": False,
    }
    return result


def _validate_exact_inputs(
    repo: Path, plan_path: Path, plan: dict[str, Any], font_path: Path
) -> dict[str, Any]:
    if _sha256(plan_path) != LEGACY_PLAN_SHA256:
        raise ActivityIRConsumerError(
            "legacy activity plan hash mismatch", stage="input_identity"
        )
    if plan.get("schema_version") != "clippipegen.s2.activity_chronology_plan.v1":
        raise ActivityIRConsumerError(
            "legacy activity plan schema mismatch", stage="input_identity"
        )
    if _sha256(font_path) != FONT_SHA256:
        raise ActivityIRConsumerError("Keifont hash mismatch", stage="font_identity")

    bindings: list[dict[str, Any]] = []
    for source in plan.get("sources") or []:
        identity = str(source.get("source_identity") or "")
        expected_media = EXPECTED_SOURCES.get(identity)
        if expected_media is None or source.get("media", {}).get("sha256") != expected_media:
            raise ActivityIRConsumerError(
                f"unapproved source identity: {identity}", stage="input_identity"
            )
        evidence: dict[str, Any] = {}
        for key in (
            "media",
            "caption",
            "fetch_receipt",
            "material_ledger",
            "provider_metadata",
            "processing_snapshot",
            "identity_binding",
        ):
            item = source.get(key) or {}
            locator = repo / str(item.get("path") or "")
            expected = str(item.get("sha256") or "")
            if not locator.is_file() or _sha256(locator) != expected:
                raise ActivityIRConsumerError(
                    f"source evidence mismatch: {identity}/{key}",
                    stage="input_identity",
                )
            evidence[key] = {
                "path": locator.relative_to(repo).as_posix(),
                "sha256": expected,
                "byte_size": locator.stat().st_size,
            }
        snapshot = source["processing_snapshot"]
        if (
            snapshot.get("user_granted_processing_scope")
            != "local_private_review_only"
            or snapshot.get("rights_clearance") is not False
            or snapshot.get("rights_approval") is not False
            or snapshot.get("public_use") != "not_authorized"
            or snapshot.get("monetized_use") != "not_authorized"
        ):
            raise ActivityIRConsumerError(
                f"source processing boundary mismatch: {identity}",
                stage="input_identity",
            )
        bindings.append(
            {
                "source_id": source["source_id"],
                "source_identity": identity,
                "archive_date": source["archive_date"],
                "evidence": evidence,
            }
        )
    if set(EXPECTED_SOURCES) != {item["source_identity"] for item in bindings}:
        raise ActivityIRConsumerError(
            "exact two-source set is incomplete", stage="input_identity"
        )
    return {
        "schema_version": "clippipegen.activity_ir_consumer_source_binding.v1",
        "artifact_id": ARTIFACT_ID,
        "legacy_plan": {
            "path": plan_path.relative_to(repo).as_posix(),
            "sha256": LEGACY_PLAN_SHA256,
            "byte_size": plan_path.stat().st_size,
        },
        "sources": bindings,
        "font": {
            "family": "Keifont",
            "sha256": FONT_SHA256,
            "byte_size": font_path.stat().st_size,
            "artifact_member": "assets/keifont.ttf",
        },
        "network_access": False,
        "source_fetch": False,
    }


def _direct_validator_attempt(plan: dict[str, Any]) -> dict[str, Any]:
    try:
        normalize_editorial_form_plan(
            plan, variant_id=ACTIVITY_CHRONOLOGY_VARIANT_ID
        )
    except EditorialFormValidationError as exc:
        return {
            "status": "legacy_schema_rejected_expected",
            "rule": exc.rule,
            "locator": exc.locator,
            "message": str(exc),
            "alternate_route": "mechanical_range_preserving_legacy_adapter",
        }
    return {"status": "accepted_directly", "rule": None, "locator": None}


def _adapt_legacy_plan(plan: dict[str, Any]) -> dict[str, Any]:
    sources = {source["source_id"]: source for source in plan["sources"]}
    units: list[dict[str, Any]] = []
    for unit in plan["activity_units"]:
        source = sources[unit["source_id"]]
        source_in, source_out = map(float, unit["source_range"])
        quote_in, quote_out = map(float, unit["quote_source_range"])
        item: dict[str, Any] = {
            "unit_id": unit["unit_id"],
            "topic": unit["activity_topic"],
            "source": {
                "source_id": unit["source_id"],
                "source_locator": source["source_identity"],
                "source_in": source_in,
                "source_out": source_out,
                "timepoint": unit["date"],
            },
            "context": {
                "source_in": source_in,
                "source_out": source_out,
                "basis": "exact_legacy_selected_range_no_context_expansion",
            },
            "connection_basis": "direct_attributable_quote",
            "subtitle_dependency": False,
            "quote": {
                "text": unit["quote"],
                "attribution": source["provider_channel"],
                "source_locator": source["source_identity"],
                "source_in": quote_in,
                "source_out": quote_out,
            },
        }
        if unit.get("temporal_relation"):
            item["temporal_bridge_from_previous"] = {
                "relation": "one_week_later",
                "caption": plan["temporal_bridge"]["visible_text"],
            }
        units.append(item)
    return {
        "schema_version": "clippipegen.editorial_form_plan.v1",
        "variant_id": ACTIVITY_CHRONOLOGY_VARIANT_ID,
        "primary_axis": "observable_activity_chronology",
        "units": units,
    }


def _build_timeline(
    plan: dict[str, Any], normalized_ir: dict[str, Any]
) -> dict[str, Any]:
    normalized = {unit["unit_id"]: unit for unit in normalized_ir["units"]}
    events: list[dict[str, Any]] = [
        {
            "event_id": "opening",
            "event_type": "factual_title",
            **plan["opening"],
        }
    ]
    for unit in plan["activity_units"]:
        if unit.get("temporal_relation"):
            events.append(
                {
                    "event_id": "one_week_later",
                    "event_type": "temporal_bridge",
                    **plan["temporal_bridge"],
                }
            )
        events.append(
            {
                "event_id": unit["unit_id"],
                "event_type": "activity_unit",
                "source_id": unit["source_id"],
                "source_range": list(map(float, unit["source_range"])),
                "output_range": list(map(float, unit["output_range"])),
                "topic": unit["activity_topic"],
                "date": unit["date"],
                "normalized_ir_unit": normalized[unit["unit_id"]],
            }
        )
    return {
        "schema_version": "clippipegen.activity_ir_consumer_timeline.v1",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "primary_axis": "observable_activity_chronology",
        "events": events,
        "activity_unit_count": len(plan["activity_units"]),
        "navigation_partition_count": len(events),
        "expected_duration_seconds": float(plan["expected_output_duration_seconds"]),
        "semantic_winner_selected": False,
        "human_editorial_acceptance": False,
    }


def _build_caption_rows(
    repo: Path, plan: dict[str, Any], timeline: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_map = {source["source_id"]: source for source in plan["sources"]}
    raw: list[dict[str, Any]] = []
    selected_provider_events = 0
    for unit in plan["activity_units"]:
        source = source_map[unit["source_id"]]
        events = load_caption_events(repo / source["caption"]["path"])
        source_in, source_out = map(float, unit["source_range"])
        output_in = float(unit["output_range"][0])
        for event in events:
            start = max(float(event["source_start_seconds"]), source_in)
            end = min(float(event["source_end_seconds"]), source_out)
            if end - start < MIN_CUE_SECONDS:
                continue
            selected_provider_events += 1
            raw.append(
                {
                    "provider_event_id": event["event_id"],
                    "unit_id": unit["unit_id"],
                    "source_id": unit["source_id"],
                    "source_identity": source["source_identity"],
                    "source_start_seconds": round(start, 6),
                    "source_end_seconds": round(end, 6),
                    "output_start_seconds": round(output_in + start - source_in, 6),
                    "output_end_seconds": round(output_in + end - source_in, 6),
                    "text": event["text"],
                    "text_sha256": event["text_sha256"],
                    "split_at_selected_range": (
                        start > float(event["source_start_seconds"]) + 0.001
                        or end < float(event["source_end_seconds"]) - 0.001
                    ),
                }
            )
    raw.sort(key=lambda row: (row["output_start_seconds"], row["output_end_seconds"]))
    resolved, stats = _resolve_rolling_overlaps(raw)
    for index, row in enumerate(resolved, start=1):
        row["caption_id"] = f"caption_{index:04d}"
        row["provider_timing_delay_seconds"] = 0.0
    stats["selected_provider_event_count"] = selected_provider_events
    stats["output_cue_count_before_text_wrapping"] = len(resolved)
    stats["timeline_duration_seconds"] = timeline["expected_duration_seconds"]
    return resolved, stats


def _resolve_rolling_overlaps(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    duplicate_merges = 0
    previous_closures = 0
    short_drops = 0
    for original in rows:
        row = dict(original)
        if resolved and resolved[-1]["unit_id"] == row["unit_id"]:
            previous = resolved[-1]
            start = float(row["output_start_seconds"])
            previous_end = float(previous["output_end_seconds"])
            if start < previous_end - 0.001:
                if _caption_equivalent(previous["text"], row["text"]):
                    previous["output_end_seconds"] = max(
                        previous_end, float(row["output_end_seconds"])
                    )
                    previous["source_end_seconds"] = max(
                        float(previous["source_end_seconds"]),
                        float(row["source_end_seconds"]),
                    )
                    previous.setdefault("merged_provider_event_ids", []).append(
                        row["provider_event_id"]
                    )
                    duplicate_merges += 1
                    continue
                previous["output_end_seconds"] = round(start, 6)
                previous["source_end_seconds"] = round(
                    float(previous["source_start_seconds"])
                    + float(previous["output_end_seconds"])
                    - float(previous["output_start_seconds"]),
                    6,
                )
                previous["timing_adjustment"] = "closed_at_next_provider_cue_start"
                previous_closures += 1
                if (
                    float(previous["output_end_seconds"])
                    - float(previous["output_start_seconds"])
                    < MIN_CUE_SECONDS
                ):
                    resolved.pop()
                    short_drops += 1
        if (
            float(row["output_end_seconds"])
            - float(row["output_start_seconds"])
            < MIN_CUE_SECONDS
        ):
            short_drops += 1
            continue
        row["timing_adjustment"] = row.get("timing_adjustment")
        resolved.append(row)
    overlap_count = sum(
        1
        for previous, current in zip(resolved, resolved[1:])
        if float(current["output_start_seconds"])
        < float(previous["output_end_seconds"]) - 0.001
    )
    if overlap_count:
        raise ActivityIRConsumerError(
            "rolling caption overlap remains after resolution",
            stage="caption_timing",
        )
    return resolved, {
        "strategy": "merge_equivalent_else_close_previous_at_next_provider_start",
        "provider_cues_delayed_to_previous_end": 0,
        "equivalent_rolling_cues_merged": duplicate_merges,
        "previous_cues_closed_at_next_start": previous_closures,
        "sub_minimum_cues_dropped": short_drops,
        "remaining_overlap_count": overlap_count,
    }


def _caption_equivalent(left: str, right: str) -> bool:
    normalize = lambda value: re.sub(r"[\s\u3000]+", "", value)
    return normalize(left) == normalize(right)


def _measure_and_wrap_subtitles(
    *, staging: Path, rows: list[dict[str, Any]]
) -> dict[str, Any]:
    texts = sorted(
        {
            part
            for row in rows
            for part in _measurement_parts(str(row["text"]))
            if part
        }
    )
    widths = _measure_texts_with_system_drawing(staging, texts)
    for row in rows:
        text = _clean_caption_text(str(row["text"]))
        lines = _wrap_two_lines(text, widths)
        row["ass_lines"] = lines
        row["ass_text"] = r"\N".join(lines)
        row["measured_width_pixels_by_line"] = [round(widths[line], 3) for line in lines]
        row["max_measured_width_pixels"] = round(max(widths[line] for line in lines), 3)
        row["line_count"] = len(lines)
        row["orphan_tail_present"] = len(lines) > 1 and _visible_count(lines[-1]) <= 2
        if (
            row["line_count"] > 2
            or row["max_measured_width_pixels"] <= 0
            or row["max_measured_width_pixels"] > SUBTITLE_SAFE_WIDTH
            or row["orphan_tail_present"]
        ):
            raise ActivityIRConsumerError(
                f"subtitle readability failed: {row.get('caption_id')}",
                stage="subtitle_measurement",
            )
    measured = [float(row["max_measured_width_pixels"]) for row in rows]
    return {
        "status": "passed" if rows and all(value > 0 for value in measured) else "failed",
        "engine": "System.Drawing.PrivateFontCollection",
        "font_family": "Keifont",
        "font_sha256": FONT_SHA256,
        "font_size_pixels": SUBTITLE_FONT_SIZE,
        "safe_width_pixels": SUBTITLE_SAFE_WIDTH,
        "cue_count": len(rows),
        "nonzero_width_cue_count": sum(value > 0 for value in measured),
        "maximum_measured_width_pixels": round(max(measured, default=0.0), 3),
        "maximum_line_count": max((int(row["line_count"]) for row in rows), default=0),
        "orphan_tail_count": sum(bool(row["orphan_tail_present"]) for row in rows),
    }


def _measurement_parts(text: str) -> set[str]:
    text = _clean_caption_text(text)
    parts = {text}
    for index in range(1, len(text)):
        parts.add(text[:index])
        parts.add(text[index:])
    return parts


def _measure_texts_with_system_drawing(
    staging: Path, texts: list[str]
) -> dict[str, float]:
    work = staging / ".measurement"
    work.mkdir()
    input_path = work / "texts.json"
    output_path = work / "widths.json"
    script_path = work / "measure.ps1"
    _write_json(input_path, {"texts": texts})
    _write_text(
        script_path,
        """param([string]$InputPath,[string]$OutputPath,[string]$FontPath,[single]$FontSize)
Add-Type -AssemblyName System.Drawing
$collection=[System.Drawing.Text.PrivateFontCollection]::new()
$collection.AddFontFile($FontPath)
if($collection.Families.Count -ne 1){throw 'exact font family resolution failed'}
$font=[System.Drawing.Font]::new($collection.Families[0],$FontSize,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
$bitmap=[System.Drawing.Bitmap]::new(4096,256)
$graphics=[System.Drawing.Graphics]::FromImage($bitmap)
$graphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$format=[System.Drawing.StringFormat]::GenericTypographic
$format.FormatFlags=$format.FormatFlags -bor [System.Drawing.StringFormatFlags]::MeasureTrailingSpaces
$payload=[System.IO.File]::ReadAllText($InputPath,[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$rows=@()
foreach($text in $payload.texts){
  $size=$graphics.MeasureString([string]$text,$font,4096,$format)
  $rows+=[ordered]@{text=[string]$text;width=[double]$size.Width;height=[double]$size.Height}
}
$result=[ordered]@{font_family=$collection.Families[0].Name;font_size_pixels=$FontSize;rows=$rows}
$json=$result | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($OutputPath,$json,[System.Text.UTF8Encoding]::new($false))
$graphics.Dispose();$bitmap.Dispose();$font.Dispose();$collection.Dispose()
""",
    )
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-InputPath",
        str(input_path),
        "-OutputPath",
        str(output_path),
        "-FontPath",
        str(staging / "assets" / "keifont.ttf"),
        "-FontSize",
        str(SUBTITLE_FONT_SIZE),
    ]
    _run(command, cwd=staging, timeout=120)
    result = _read_json(output_path)
    if str(result.get("font_family") or "").lower() != "keifont":
        raise ActivityIRConsumerError(
            "measurement did not resolve Keifont", stage="subtitle_measurement"
        )
    measured_rows = result.get("rows") or []
    if len(measured_rows) != len(texts):
        raise ActivityIRConsumerError(
            "measurement row count does not match input text count",
            stage="subtitle_measurement",
        )
    widths = {
        text: float(row["width"])
        for text, row in zip(texts, measured_rows, strict=True)
    }
    if any(width <= 0 for width in widths.values()):
        raise ActivityIRConsumerError(
            "measurement returned a non-positive width",
            stage="subtitle_measurement",
        )
    shutil.rmtree(work)
    return widths


def _wrap_two_lines(text: str, widths: dict[str, float]) -> list[str]:
    if widths[text] <= SUBTITLE_SAFE_WIDTH:
        return [text]
    candidates: list[tuple[float, int, str, str]] = []
    for index in range(1, len(text)):
        left, right = text[:index].strip(), text[index:].strip()
        if not left or not right or _visible_count(right) <= 2:
            continue
        if widths[left] <= SUBTITLE_SAFE_WIDTH and widths[right] <= SUBTITLE_SAFE_WIDTH:
            candidates.append((abs(widths[left] - widths[right]), index, left, right))
    if not candidates:
        raise ActivityIRConsumerError(
            "caption cannot fit in two measured lines", stage="subtitle_measurement"
        )
    _, _, left, right = min(candidates, key=lambda item: (item[0], item[1]))
    return [left, right]


def _clean_caption_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def _visible_count(text: str) -> int:
    return len(re.sub(r"[\s\u3000]+", "", text))


def _render_filter(plan: dict[str, Any]) -> str:
    source_index = {source["source_id"]: index for index, source in enumerate(plan["sources"])}
    opening_duration = float(plan["opening"]["duration_seconds"])
    bridge_duration = float(plan["temporal_bridge"]["duration_seconds"])
    lines = [
        f"color=c=0x101820:s={FRAME_WIDTH}x{FRAME_HEIGHT}:r={FPS}:d={opening_duration},format=yuv420p[open_v];",
        f"anullsrc=r=48000:cl=stereo,atrim=duration={opening_duration}[open_a];",
    ]
    for index, unit in enumerate(plan["activity_units"], start=1):
        source_in, source_out = map(float, unit["source_range"])
        duration = source_out - source_in
        input_index = source_index[unit["source_id"]]
        lines.append(
            f"[{input_index}:v]trim=start={source_in}:end={source_out},"
            "setpts=PTS-STARTPTS,scale=1280:720:flags=lanczos,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x101820,"
            f"setsar=1,fps={FPS},format=yuv420p[v{index}];"
        )
        lines.append(
            f"[{input_index}:a]atrim=start={source_in}:end={source_out},"
            "asetpts=PTS-STARTPTS,aresample=48000,"
            "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
            f"afade=t=in:st=0:d=0.08,afade=t=out:st={max(0.0, duration - 0.12)}:d=0.12[a{index}];"
        )
    lines.extend(
        [
            f"color=c=0x101820:s={FRAME_WIDTH}x{FRAME_HEIGHT}:r={FPS}:d={bridge_duration},format=yuv420p[bridge_v];",
            f"anullsrc=r=48000:cl=stereo,atrim=duration={bridge_duration}[bridge_a];",
            "[open_v][open_a][v1][a1][v2][a2][v3][a3][bridge_v][bridge_a][v4][a4][v5][a5]concat=n=7:v=1:a=1[base_v][aout];",
            "[base_v]ass=overlay.ass:fontsdir=assets[vout]",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_ass(plan: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Opening,Keifont,70,&H00FFFFFF,&H00FFFFFF,&H00202020,&H00000000,0,0,0,0,100,100,0,0,1,4,1,5,120,120,40,1
Style: OpeningSub,Keifont,42,&H0000D7FF,&H0000D7FF,&H00202020,&H00000000,0,0,0,0,100,100,0,0,1,3,1,5,120,120,40,1
Style: Header,Keifont,46,&H00FFFFFF,&H00FFFFFF,&H00202020,&H00000000,0,0,0,0,100,100,0,0,1,4,1,7,72,72,56,1
Style: Source,Keifont,26,&H00D8DEE9,&H00D8DEE9,&H00202020,&H00000000,0,0,0,0,100,100,0,0,1,2,0,9,72,72,58,1
Style: Subtitle,Keifont,54,&H00FFFFFF,&H00FFFFFF,&H00101010,&H78000000,0,0,0,0,100,100,0,0,3,3,0,2,210,210,76,1
Style: Bridge,Keifont,62,&H0000D7FF,&H0000D7FF,&H00202020,&H00000000,0,0,0,0,100,100,0,0,1,4,1,5,100,100,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        _ass_event(0.3, 3.2, "Opening", "大空スバル｜ドラゴンボールを読む"),
        _ass_event(1.35, 3.2, "OpeningSub", "2026年7月の活動記録"),
    ]
    source_labels = {
        source["source_id"]: f"{source['provider_channel']}｜{source['source_identity']}"
        for source in plan["sources"]
    }
    for unit in plan["activity_units"]:
        output_in, output_out = map(float, unit["output_range"])
        events.append(
            _ass_event(
                output_in + 0.05,
                output_out - 0.05,
                "Header",
                f"{unit['date'].replace('-', '.')}｜{unit['activity_topic']}",
            )
        )
        events.append(
            _ass_event(
                output_in + 0.05,
                output_out - 0.05,
                "Source",
                source_labels[unit["source_id"]],
            )
        )
    bridge = plan["temporal_bridge"]
    events.append(
        _ass_event(
            float(bridge["output_in"]),
            float(bridge["output_out"]),
            "Bridge",
            bridge["visible_text"],
        )
    )
    for row in rows:
        events.append(
            _ass_event(
                float(row["output_start_seconds"]),
                float(row["output_end_seconds"]),
                "Subtitle",
                str(row["ass_text"]),
            )
        )
    return header + "".join(events)


def _ass_event(start: float, end: float, style: str, text: str) -> str:
    safe = text.replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")
    return (
        f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},{style},,0,0,0,,{safe}\n"
    )


def _ass_time(value: float) -> str:
    centiseconds = max(0, round(value * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    seconds, hundredths = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{hundredths:02d}"


def _render_command(repo: Path, staging: Path, plan: dict[str, Any]) -> list[str]:
    inputs: list[str] = []
    for source in plan["sources"]:
        inputs.extend(["-i", str((repo / source["media"]["path"]).resolve())])
    return [
        "ffmpeg",
        "-hide_banner",
        "-y",
        *inputs,
        "-filter_complex_script",
        "render_filter.txt",
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        "final_video.mp4",
    ]


def _probe(video: Path, cwd: Path) -> dict[str, Any]:
    result = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,format_name",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            video.name,
        ],
        cwd=cwd,
        timeout=60,
    )
    return json.loads(result.stdout)


def _validate_media(
    staging: Path, probe: dict[str, Any], timeline: dict[str, Any]
) -> dict[str, Any]:
    video_decode = _run(
        ["ffmpeg", "-v", "error", "-i", "final_video.mp4", "-map", "0:v:0", "-f", "null", "NUL"],
        cwd=staging,
        timeout=360,
    )
    audio_decode = _run(
        ["ffmpeg", "-v", "error", "-i", "final_video.mp4", "-map", "0:a:0", "-f", "null", "NUL"],
        cwd=staging,
        timeout=360,
    )
    streams = probe.get("streams") or []
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = float(probe["format"]["duration"])
    checks = {
        "h264_video": bool(video and video.get("codec_name") == "h264"),
        "aac_audio": bool(audio and audio.get("codec_name") == "aac"),
        "resolution_1920x1080": bool(video and video.get("width") == 1920 and video.get("height") == 1080),
        "video_full_decode": video_decode.returncode == 0,
        "audio_full_decode": audio_decode.returncode == 0,
        "duration_matches_timeline": abs(duration - float(timeline["expected_duration_seconds"])) <= 0.08,
        "production_candidate_false": True,
        "semantic_winner_selected_false": True,
    }
    if not all(checks.values()):
        raise ActivityIRConsumerError(
            f"media validation failed: {checks}", stage="media_validation"
        )
    return {
        "schema_version": "clippipegen.activity_ir_consumer_validation.v1",
        "artifact_id": ARTIFACT_ID,
        "status": "passed",
        "duration_seconds": duration,
        "probe": probe,
        "checks": checks,
        "video_decode_stderr_sha256": _sha256_bytes(video_decode.stderr.encode("utf-8")),
        "audio_decode_stderr_sha256": _sha256_bytes(audio_decode.stderr.encode("utf-8")),
    }


def _build_review_frames(staging: Path, timeline: dict[str, Any]) -> None:
    moments: list[tuple[str, float]] = [("opening", 1.5)]
    for event in timeline["events"]:
        if event["event_type"] == "activity_unit":
            start, end = map(float, event["output_range"])
            moments.append((event["event_id"], min(end - 0.05, start + 0.25)))
        elif event["event_type"] == "temporal_bridge":
            moments.append((event["event_id"], float(event["output_in"]) + 0.3))
    for name, moment in moments:
        full = f"review/evidence/full/{name}_{moment:.3f}s.png"
        mobile = f"review/evidence/mobile/{name}_{moment:.3f}s_480x270.png"
        _run(
            ["ffmpeg", "-v", "error", "-ss", f"{moment:.6f}", "-i", "final_video.mp4", "-frames:v", "1", full],
            cwd=staging,
            timeout=60,
        )
        _run(
            ["ffmpeg", "-v", "error", "-ss", f"{moment:.6f}", "-i", "final_video.mp4", "-frames:v", "1", "-vf", "scale=480:270:flags=lanczos", mobile],
            cwd=staging,
            timeout=60,
        )


def _build_review_surface(
    staging: Path,
    plan: dict[str, Any],
    timeline: dict[str, Any],
    width_readback: dict[str, Any],
) -> None:
    rows: list[str] = []
    for event in timeline["events"]:
        if event["event_type"] == "activity_unit":
            output_in, output_out = map(float, event["output_range"])
            source_in, source_out = map(float, event["source_range"])
            rows.append(
                "<tr>"
                f"<td><button data-time=\"{output_in:.3f}\">{html.escape(event['event_id'])}</button></td>"
                f"<td>{html.escape(event['date'])}</td>"
                f"<td>{html.escape(event['topic'])}</td>"
                f"<td>{html.escape(event['source_id'])} {source_in:.3f}–{source_out:.3f}</td>"
                f"<td>{output_in:.3f}–{output_out:.3f}</td>"
                "</tr>"
            )
        elif event["event_type"] == "temporal_bridge":
            rows.append(
                "<tr>"
                f"<td><button data-time=\"{float(event['output_in']):.3f}\">temporal bridge</button></td>"
                "<td>2026-07-25</td><td>1週間後</td><td>silent factual bridge</td>"
                f"<td>{float(event['output_in']):.3f}–{float(event['output_out']):.3f}</td>"
                "</tr>"
            )
    artifact = html.escape(ARTIFACT_ID)
    body = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{artifact}</title>
<style>
body{{margin:0;background:#0b0f14;color:#edf3f8;font:16px/1.5 system-ui,sans-serif}}main{{width:min(1120px,94vw);margin:24px auto 60px}}video{{width:100%;background:#000;border:1px solid #405064}}.notice{{padding:12px 14px;background:#28171c;border:1px solid #8a4352}}.status{{padding:12px 14px;background:#11251a;border:1px solid #3d7651;margin:12px 0}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border:1px solid #3b4655;padding:8px;vertical-align:top}}button{{cursor:pointer;padding:6px 9px}}code{{overflow-wrap:anywhere}}@media(max-width:600px){{body{{font-size:14px}}table{{display:block;overflow-x:auto}}}}
</style></head><body><main>
<h1>Activity chronology IR consumer proof</h1><p><code>{artifact}</code></p>
<div class="notice">NON_ADOPTED_REVIEW_PROOF。semantic winner、human creative acceptance、rights、production、publication、uploadは未承認です。</div>
<div class="status">Exact legacy planをrange不変adapterでnormalized IRへ接続し、provider caption、cut、chronology transitionを同じcandidate identityへ閉じています。字幕はKeifont実測、最大{width_readback['maximum_measured_width_pixels']:.1f}px / safe {SUBTITLE_SAFE_WIDTH}px、最大2行、orphan 0です。</div>
<video id="player" controls preload="metadata" src="../final_video.mp4"></video>
<p id="clock">00:00.000</p>
<h2>Timestamp map</h2><table><thead><tr><th>jump</th><th>date</th><th>activity</th><th>source</th><th>output</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Independent review question</h2><p>活動時系列として、各unitの字幕・映像・音声と一週間後のtransitionが誤解なく連続して見えるか。technical PASSをcreative acceptanceへ置き換えないこと。</p>
<script>const v=document.getElementById('player'),c=document.getElementById('clock');document.querySelectorAll('[data-time]').forEach(b=>b.addEventListener('click',()=>{{v.currentTime=Number(b.dataset.time);v.play();}}));v.addEventListener('timeupdate',()=>{{c.textContent=v.currentTime.toFixed(3)+'s';}});</script>
</main></body></html>"""
    _write_text(staging / "review" / "index.html", body)
    _write_text(
        staging / "review" / "serve_preview.ps1",
        """$ErrorActionPreference='Stop'\n$PackageRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path\nuv run python -m src.cli.serve_review --root $PackageRoot --port 8765\n""",
    )
    _write_text(
        staging / "review" / "open_preview.ps1",
        """$ErrorActionPreference='Stop'\n$PackageRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path\nWrite-Output \"Start server from repository root: uv run python -m src.cli.serve_review --root '$PackageRoot' --port 8765\"\nWrite-Output 'Then open http://127.0.0.1:8765/review/index.html'\n""",
    )


def _http_and_viewport_readback(staging: Path, chrome_path: Path) -> dict[str, Any]:
    port = _free_port()
    command = [
        sys.executable,
        "-m",
        "src.cli.serve_review",
        "--root",
        str(staging),
        "--port",
        str(port),
    ]
    server = subprocess.Popen(
        command,
        cwd=Path.cwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    base = f"http://127.0.0.1:{port}"
    try:
        page_status = None
        page_body = ""
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"{base}/review/index.html", timeout=1) as response:
                    page_status = response.status
                    page_body = response.read().decode("utf-8")
                break
            except Exception:
                if server.poll() is not None:
                    break
                time.sleep(0.1)
        if page_status != 200 or ARTIFACT_ID not in page_body or "data-time" not in page_body:
            raise ActivityIRConsumerError(
                "review HTML did not pass HTTP readback", stage="html_readback"
            )
        request = urllib.request.Request(
            f"{base}/final_video.mp4", headers={"Range": "bytes=0-127"}
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            range_status = response.status
            range_bytes = response.read()
        if range_status != 206 or len(range_bytes) != 128:
            raise ActivityIRConsumerError(
                "review MP4 byte-range readback failed", stage="html_readback"
            )
        profile = staging / ".chrome-profile"
        screenshot = staging / "review" / "evidence" / "mobile_review_480x900.png"
        chrome = _run(
            [
                str(chrome_path),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-first-run",
                f"--user-data-dir={profile}",
                "--window-size=480,900",
                f"--screenshot={screenshot}",
                f"{base}/review/index.html",
            ],
            cwd=staging,
            timeout=120,
        )
        if not screenshot.is_file() or screenshot.stat().st_size <= 0:
            raise ActivityIRConsumerError(
                "headless viewport screenshot missing", stage="html_viewport"
            )
        shutil.rmtree(profile, ignore_errors=True)
        return {
            "schema_version": "clippipegen.activity_ir_consumer_html_readback.v1",
            "status": "passed",
            "entry_status": page_status,
            "entry_contains_artifact_id": True,
            "timestamp_controls_present": True,
            "mp4_range_status": range_status,
            "mp4_range_bytes": len(range_bytes),
            "viewport": "480x900",
            "viewport_screenshot": "review/evidence/mobile_review_480x900.png",
            "chrome_exit_code": chrome.returncode,
            "server_process_stopped": True,
        }
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _build_receipt(
    *,
    plan_path: Path,
    plan: dict[str, Any],
    normalized_ir_path: Path,
    source_bindings: dict[str, Any],
    direct_validation: dict[str, Any],
    final_video: Path,
    probe: dict[str, Any],
    timeline: dict[str, Any],
    caption_stats: dict[str, Any],
    width_readback: dict[str, Any],
    validation: dict[str, Any],
    html_readback: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.activity_ir_consumer_receipt.v1",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "purpose": "exact retained activity chronology IR consumer material proof",
        "legacy_plan": {
            "sha256": _sha256(plan_path),
            "byte_size": plan_path.stat().st_size,
            "schema_version": plan["schema_version"],
        },
        "direct_validator_attempt": direct_validation,
        "normalized_ir": {
            "path": "normalized_ir.json",
            "sha256": _sha256(normalized_ir_path),
            "byte_size": normalized_ir_path.stat().st_size,
            "range_preserving_adapter": True,
            "semantic_content_added": False,
        },
        "sources": source_bindings["sources"],
        "output": {
            "path": "final_video.mp4",
            "sha256": _sha256(final_video),
            "byte_size": final_video.stat().st_size,
            "duration_seconds": float(probe["format"]["duration"]),
            "video_codec": "h264",
            "audio_codec": "aac",
        },
        "mapping": {
            "activity_unit_count": timeline["activity_unit_count"],
            "events": timeline["events"],
        },
        "subtitles": {**caption_stats, **width_readback},
        "validation_status": validation["status"],
        "html_readback_status": html_readback["status"],
        "network_access": False,
        "source_fetch": False,
        "semantic_winner_selected": False,
        "human_editorial_acceptance": False,
        "rights_approval": False,
        "production_acceptance": False,
        "publication_approval": False,
        "upload_attempted": False,
        "public_use": False,
        "monetized_use": False,
    }


def _build_manifest(
    staging: Path, final_video: Path, probe: dict[str, Any]
) -> dict[str, Any]:
    payloads = []
    for path in sorted(
        (item for item in staging.rglob("*") if item.is_file() and item.name != "run_manifest.json"),
        key=lambda item: item.relative_to(staging).as_posix(),
    ):
        payloads.append(
            {
                "path": path.relative_to(staging).as_posix(),
                "sha256": _sha256(path),
                "byte_size": path.stat().st_size,
            }
        )
    tree_bytes = "".join(
        f"{item['path']}\0{item['sha256']}\0{item['byte_size']}\n" for item in payloads
    ).encode("utf-8")
    manifest: dict[str, Any] = {
        "schema_version": "clippipegen.activity_ir_consumer_manifest.v1",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "private_review_only": True,
        "production_candidate": False,
        "semantic_winner_selected": False,
        "human_editorial_acceptance": False,
        "rights_approval": False,
        "production_acceptance": False,
        "publication_approval": False,
        "upload_attempted": False,
        "output": {
            "path": "final_video.mp4",
            "sha256": _sha256(final_video),
            "byte_size": final_video.stat().st_size,
            "duration_seconds": float(probe["format"]["duration"]),
        },
        "payloads": payloads,
        "payload_tree": {
            "file_count": len(payloads),
            "sha256": _sha256_bytes(tree_bytes),
        },
    }
    canonical = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    manifest["manifest_self_integrity"] = {
        "scope": "canonical_json_without_manifest_self_integrity",
        "sha256": _sha256_bytes(canonical),
    }
    return manifest


def _validate_manifest(root: Path) -> None:
    manifest = _read_json(root / "run_manifest.json")
    if manifest.get("artifact_id") != ARTIFACT_ID or manifest.get("state") != STATE:
        raise ActivityIRConsumerError("manifest identity mismatch", stage="manifest")
    listed = {str(item["path"]): item for item in manifest.get("payloads") or []}
    physical = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "run_manifest.json"
    }
    if physical != set(listed):
        raise ActivityIRConsumerError("manifest closure mismatch", stage="manifest")
    for relative, item in listed.items():
        path = root / relative
        if path.stat().st_size != int(item["byte_size"]) or _sha256(path) != item["sha256"]:
            raise ActivityIRConsumerError(
                f"manifest payload mismatch: {relative}", stage="manifest"
            )
    stripped = dict(manifest)
    self_integrity = stripped.pop("manifest_self_integrity")
    canonical = json.dumps(
        stripped, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    if _sha256_bytes(canonical) != self_integrity["sha256"]:
        raise ActivityIRConsumerError("manifest self integrity mismatch", stage="manifest")


def _run(
    command: list[str], *, cwd: Path, timeout: int
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise ActivityIRConsumerError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{result.stderr[-4000:]}",
            stage="tool_execution",
        )
    return result


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ActivityIRConsumerError(
            f"expected JSON object: {path}", stage="input_read"
        )
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
