"""OUT-05 internal vertical-short candidate builder.

This module preserves the accepted OUT-04 timeline and converts it into one
1080x1920 same-machine review candidate.  It deliberately owns only a bounded
diagnostic/internal render path: no publication, production acceptance, rights
approval, speaker-identity inference, transition design, or new editorial cut
is performed here.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import uuid
from html import escape
from pathlib import Path
from typing import Any, Callable

from src.integrations.render import ffmpeg_tiny, subtitle_style_spike
from src.integrations.render.editorial_sequence import (
    _material_readback as _out04_material_readback,
    _read_object as _read_object,
)
from src.integrations.render.subtitle_overlay_visual_proof import (
    ED10L_KEIFONT_CANDIDATE_ID,
    ED10W_CANDIDATE0_BASELINE_ID,
    ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
    _diagnostic_ass_style_for_candidate,
    _ed10w_candidate_ass_style,
    _item_layout,
    _presentation_items,
    _subtitle_layout_contract,
    _write_ass,
)
from src.integrations.render.subtitle_preset_selector import select_subtitle_preset
from src.pipeline.text_measure import measure_subtitle


ARTIFACT_ID = "clip-out05-vertical-short-internal-candidate-v0-001"
SCHEMA_VERSION = "clippipegen.out05.vertical_short_candidate.v0"
STATE = "vertical_short_internal_candidate_review_ready"
EXPECTED_OUT04_ARTIFACT_ID = "clip-out04-editorial-representative-sequence-v0-001"
EXPECTED_OUT04_READBACK_SHA256 = (
    "8253e27eb2321863f277eec33161fed82a9ccb21b9719b84c082b46d31a2f1db"
)
EXPECTED_OUT04_VIDEO_SHA256 = (
    "9fa17e8566acd3e4237793840edffa2485350575876c99b04bed065a8ae6e19a"
)
EXPECTED_SUBTITLE_SEMANTIC_SHA256 = (
    "5d3f3c8b9102b5a486cba7fb54fd76851c2fe3e6f939fde9e075481461aef235"
)
EXPECTED_CUT_IDS = ("cut_001", "cut_002")
EXPECTED_DURATION_SECONDS = 11.678
EXPECTED_BOUNDARY_SECONDS = 6.840
OUTPUT_DURATION_TOLERANCE_SECONDS = 0.20
FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920
FRAME_RATE = 30.0
SAFE_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
OUTPUT_NAME_PREFIX = "out05_"
SELECTED_REFRAME = "full_16_9_fit_source_derived_blurred_canvas"
DEFAULT_BACKGROUND_POLICY = "full_source_blurred_canvas_default"
CAPTION_FREE_BACKGROUND_POLICY = "caption_free_background_canvas"
REFRAME_OPTIONS = (
    "cut_level_explicit_anchor_crop",
    SELECTED_REFRAME,
    "bounded_hybrid",
)
REVIEW_QUESTIONS = (
    "縦型フレームで主役や動作が欠けず、Shorts候補として自然に見えるか。",
    "字幕の位置・改行・読みやすさが一貫し、映像を邪魔していないか。",
    "音声・カット境界・画面に欠落、乱れ、書き出し異常がないか。",
)
OUT05_FRAME_SAMPLES = (
    ("start", 0.250),
    ("before_boundary", 6.700),
    ("after_boundary", 6.980),
    ("dense_subtitle", 9.300),
    ("end", 11.450),
)
RenderExecutor = Callable[..., dict[str, Any]]


class VerticalShortCandidateError(ValueError):
    """Raised when OUT-05 cannot be built without violating its boundaries."""


REVIEWED_LINE_BREAK_HINTS: dict[str, dict[str, Any]] = {
    "sub_013": {
        "reason": "out06_user_feedback_wrap_repair_2026_07_12",
        "preferred_lines": [
            ["なんで", "来なかったんすか！！"],
            ["なんで", "来なかった", "んすか！！"],
        ],
        "forbidden_boundaries": ["来|なかった"],
    },
    "sub_014": {
        "reason": "out06_user_feedback_wrap_repair_2026_07_12",
        "preferred_lines": [["ずっと", "待ってたんすよ！！"]],
        "forbidden_boundaries": ["待|って"],
    },
    "sub_019": {
        "reason": "out06_user_feedback_wrap_repair_2026_07_12",
        "preferred_lines": [["はじめの勝ちって", "ことでいいですね？"]],
        "forbidden_boundaries": ["こ|とで"],
    },
    "sub_024": {
        "reason": "out06_user_feedback_wrap_repair_2026_07_12",
        "preferred_lines": [
            ["団長、ちなみに、", "他の番長知ってますか？"],
            ["団長、ちなみに、", "他の番長", "知ってますか？"],
        ],
        "forbidden_boundaries": ["知|って"],
    },
    "sub_028": {
        "reason": "out06_user_feedback_wrap_repair_2026_07_12",
        "preferred_lines": [["マリンなら", "あっちにいたよ"]],
        "forbidden_boundaries": ["マリン|なら"],
    },
    "sub_029": {
        "reason": "out06_user_feedback_wrap_repair_2026_07_12",
        "preferred_lines": [["ありがとうございますー！"], ["ありがとう", "ございますー！"]],
        "forbidden_boundaries": ["ありがとうご|ざいます"],
    },
}


def build_vertical_short_candidate(
    *,
    episode_dir: str | Path,
    output_dir: str | Path,
    predecessor_readback_path: str | Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
    render_executor: RenderExecutor | None = None,
    expected_predecessor_sha256: str = EXPECTED_OUT04_READBACK_SHA256,
    expected_predecessor_video_sha256: str = EXPECTED_OUT04_VIDEO_SHA256,
    expected_subtitle_semantic_sha256: str = EXPECTED_SUBTITLE_SEMANTIC_SHA256,
) -> dict[str, Any]:
    """Build and atomically promote one ignored OUT-05 review bundle."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(root, Path(output_dir))
    predecessor_path = _resolved(root, Path(predecessor_readback_path))
    _require_directory(episode, "episode directory")
    _require_within(episode, root, "episode directory")
    _validate_output_directory(episode, output)
    _validate_predecessor_path(episode, predecessor_path)
    _reject_overlap(output, predecessor_path, "output directory must not overlap predecessor")

    predecessor = _read_json(predecessor_path, "OUT-04 predecessor readback")
    predecessor_info = _validate_predecessor(
        predecessor,
        predecessor_path=predecessor_path,
        root=root,
        episode=episode,
        expected_readback_sha256=expected_predecessor_sha256,
        expected_video_sha256=expected_predecessor_video_sha256,
        expected_subtitle_semantic_sha256=expected_subtitle_semantic_sha256,
    )
    source_video_path = predecessor_info["source_video_path"]
    source_audio_path = predecessor_info["source_audio_path"]
    input_paths = [
        predecessor_path,
        predecessor_info["predecessor_video_path"],
        source_video_path,
        source_audio_path,
        *predecessor_info["input_paths"],
    ]
    for path in input_paths:
        _reject_overlap(output, path, "output directory must not overlap an input")

    protected_paths = _protected_paths(episode)
    for protected in protected_paths.values():
        _reject_overlap(output, protected, "output directory must not overlap protected evidence")
    protected_before = {
        label: _tree_digest(path, root=root) for label, path in protected_paths.items()
    }
    source_hashes_before = {
        _relative(path, root): _sha256(path) for path in input_paths
    }

    subtitle_layout, subtitle_items, selector_readback = _build_subtitle_presentation(
        predecessor["subtitles"]
    )
    subtitle_containment = _validate_subtitle_containment(
        subtitle_items,
        expected_duration=EXPECTED_DURATION_SECONDS,
        layout=subtitle_layout,
    )
    reframe_plan = _build_reframe_plan(predecessor)
    _validate_reframe_plan(reframe_plan)

    review_dir = episode / "review"
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    backup: Path | None = None
    try:
        stage.mkdir(parents=False, exist_ok=False)
        assets = stage / "assets"
        assets.mkdir()
        work = stage / ".work"
        work.mkdir()
        ass_path = stage / "vertical_short_subtitles.ass"
        srt_path = stage / "vertical_short_subtitles.srt"
        video_path = assets / "vertical_short_candidate.mp4"
        compare_sheet_path = assets / "reframe_comparison_contact_sheet.jpg"
        frame_sheet_path = assets / "frame_qa_contact_sheet.jpg"
        reframe_plan_path = stage / "reframe_plan.json"
        readback_path = stage / "candidate_readback.json"
        index_path = stage / "index.html"
        open_path = stage / "open_preview.ps1"
        serve_path = stage / "serve_preview.ps1"

        _write_ass(ass_path, subtitle_items, layout=subtitle_layout, review_label=None)
        _write_text(srt_path, _render_srt(subtitle_items))
        _write_text(
            reframe_plan_path,
            json.dumps(reframe_plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        _validate_ass_visible_content(ass_path)

        executor = render_executor or _render_candidate_assets
        render_result = executor(
            source_video_path=source_video_path,
            source_audio_path=source_audio_path,
            timeline=predecessor["timeline"],
            ass_path=ass_path,
            video_path=video_path,
            compare_sheet_path=compare_sheet_path,
            frame_sheet_path=frame_sheet_path,
            work_dir=work,
            subtitle_layout=subtitle_layout,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        _validate_render_result(render_result, video_path=video_path)
        _require_file(compare_sheet_path, "reframe comparison contact sheet")
        _require_file(frame_sheet_path, "frame QA contact sheet")
        _cleanup_internal_directory(work, expected_parent=stage)

        protected_after_render = {
            label: _tree_digest(path, root=root) for label, path in protected_paths.items()
        }
        if protected_after_render != protected_before:
            raise VerticalShortCandidateError("protected evidence changed during render")
        source_hashes_after = {_relative(path, root): _sha256(path) for path in input_paths}
        if source_hashes_after != source_hashes_before:
            raise VerticalShortCandidateError("source or predecessor input changed during render")

        rights_status = predecessor_info["rights_status"]
        final_paths = {
            "video": output / "assets" / video_path.name,
            "ass": output / ass_path.name,
            "srt": output / srt_path.name,
            "reframe_plan": output / reframe_plan_path.name,
            "readback": output / readback_path.name,
            "index": output / index_path.name,
            "open": output / open_path.name,
            "serve": output / serve_path.name,
            "reframe_comparison_contact_sheet": output / "assets" / compare_sheet_path.name,
            "frame_qa_contact_sheet": output / "assets" / frame_sheet_path.name,
        }
        readback = _candidate_readback(
            root=root,
            episode=episode,
            output=output,
            predecessor=predecessor,
            predecessor_info=predecessor_info,
            source_hashes=source_hashes_before,
            protected=protected_before,
            subtitle_layout=subtitle_layout,
            subtitle_items=subtitle_items,
            subtitle_containment=subtitle_containment,
            selector_readback=selector_readback,
            reframe_plan=reframe_plan,
            render_result=render_result,
            stage_paths={
                "video": video_path,
                "ass": ass_path,
                "srt": srt_path,
                "reframe_plan": reframe_plan_path,
                "reframe_comparison_contact_sheet": compare_sheet_path,
                "frame_qa_contact_sheet": frame_sheet_path,
            },
            final_paths=final_paths,
            rights_status=rights_status,
        )
        _write_text(
            readback_path,
            json.dumps(readback, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        _write_text(index_path, _render_html(readback))
        _write_text(open_path, _open_script())
        _write_text(serve_path, _serve_script())
        _validate_staged_bundle(stage, readback)
        backup = _atomic_promote(stage, output)
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)

    final_readback_path = output / "candidate_readback.json"
    final_readback = _read_json(final_readback_path, "promoted candidate readback")
    return {
        "artifact_id": ARTIFACT_ID,
        "output_dir": output,
        "video_path": output / "assets" / "vertical_short_candidate.mp4",
        "ass_path": output / "vertical_short_subtitles.ass",
        "srt_path": output / "vertical_short_subtitles.srt",
        "reframe_plan_path": output / "reframe_plan.json",
        "readback_path": final_readback_path,
        "index_path": output / "index.html",
        "open_path": output / "open_preview.ps1",
        "serve_path": output / "serve_preview.ps1",
        "readback": final_readback,
    }


def _validate_predecessor(
    predecessor: dict[str, Any],
    *,
    predecessor_path: Path,
    root: Path,
    episode: Path,
    expected_readback_sha256: str,
    expected_video_sha256: str,
    expected_subtitle_semantic_sha256: str,
) -> dict[str, Any]:
    actual_readback_hash = _sha256(predecessor_path)
    if actual_readback_hash != expected_readback_sha256:
        raise VerticalShortCandidateError("OUT-04 predecessor readback hash changed")
    if predecessor.get("artifact_id") != EXPECTED_OUT04_ARTIFACT_ID:
        raise VerticalShortCandidateError("unexpected OUT-04 predecessor artifact")
    if tuple(predecessor.get("ordered_cut_ids") or ()) != EXPECTED_CUT_IDS:
        raise VerticalShortCandidateError("OUT-04 cut order must remain cut_001 -> cut_002")
    _assert_close(
        predecessor.get("expected_duration_seconds"),
        EXPECTED_DURATION_SECONDS,
        "OUT-04 duration",
    )
    timeline = predecessor.get("timeline")
    if not isinstance(timeline, list) or len(timeline) != 2:
        raise VerticalShortCandidateError("OUT-04 timeline must contain exactly two cuts")
    expected_ranges = (
        ("cut_001", 2.453, 9.293, 0.000, 6.840, "sequence_start"),
        ("cut_002", 12.329, 17.167, 6.840, 11.678, "hard_cut"),
    )
    for item, expected in zip(timeline, expected_ranges, strict=True):
        cut_id, src_start, src_end, seq_start, seq_end, transition = expected
        if item.get("id") != cut_id or item.get("transition_in") != transition:
            raise VerticalShortCandidateError("OUT-04 timeline identity/transition changed")
        for field, value in (
            ("source_start_seconds", src_start),
            ("source_end_seconds", src_end),
            ("sequence_start_seconds", seq_start),
            ("sequence_end_seconds", seq_end),
        ):
            _assert_close(item.get(field), value, f"{cut_id}.{field}")
    _assert_close(timeline[1].get("sequence_start_seconds"), EXPECTED_BOUNDARY_SECONDS, "boundary")

    subtitles = predecessor.get("subtitles")
    if not isinstance(subtitles, list) or len(subtitles) != 9:
        raise VerticalShortCandidateError("OUT-04 predecessor must contain nine subtitles")
    if _subtitle_semantic_hash(subtitles) != expected_subtitle_semantic_sha256:
        raise VerticalShortCandidateError("OUT-04 subtitle timing/text hash changed")
    _validate_predecessor_subtitle_ranges(subtitles, timeline)

    render = predecessor.get("render") if isinstance(predecessor.get("render"), dict) else {}
    predecessor_video_path = _resolved(root, Path(str(render.get("output_path") or "")))
    _require_file(predecessor_video_path, "OUT-04 predecessor video")
    _require_within(predecessor_video_path, predecessor_path.parent, "OUT-04 predecessor video")
    actual_video_hash = _sha256(predecessor_video_path)
    if actual_video_hash != str(render.get("output_sha256") or ""):
        raise VerticalShortCandidateError("OUT-04 predecessor video/readback hash mismatch")
    if actual_video_hash != expected_video_sha256:
        raise VerticalShortCandidateError("accepted OUT-04 predecessor video hash changed")

    input_paths: list[Path] = []
    for label, entry in (predecessor.get("input_artifacts") or {}).items():
        if not isinstance(entry, dict):
            raise VerticalShortCandidateError(f"invalid OUT-04 input readback: {label}")
        path = _resolved(root, Path(str(entry.get("path") or "")))
        _require_file(path, f"OUT-04 input {label}")
        _require_within(path, episode, f"OUT-04 input {label}")
        if _sha256(path) != str(entry.get("sha256") or ""):
            raise VerticalShortCandidateError(f"OUT-04 input hash changed: {label}")
        input_paths.append(path)

    ledger_path = episode / "material_ledger.json"
    ledger = _read_json(ledger_path, "material ledger")
    materials = predecessor.get("materials") or {}
    video_id = str((materials.get("source_video") or {}).get("id") or "")
    audio_id = str((materials.get("source_audio") or {}).get("id") or "")
    _safe_identifier(video_id, "source video material id")
    _safe_identifier(audio_id, "source audio material id")
    try:
        video_material = _out04_material_readback(
            ledger,
            material_id=video_id,
            expected_kind="source_video",
            root=root,
            episode=episode,
        )
        audio_material = _out04_material_readback(
            ledger,
            material_id=audio_id,
            expected_kind="source_audio",
            root=root,
            episode=episode,
        )
    except ValueError as exc:
        raise VerticalShortCandidateError(str(exc)) from exc
    source_video_path = _resolved(root, Path(video_material["file_path"]))
    source_audio_path = _resolved(root, Path(audio_material["file_path"]))
    for kind, material, predecessor_material in (
        ("video", video_material, materials.get("source_video") or {}),
        ("audio", audio_material, materials.get("source_audio") or {}),
    ):
        if material["sha256"] != str(predecessor_material.get("sha256") or ""):
            raise VerticalShortCandidateError(f"source {kind} hash changed from OUT-04")

    rights_status = str((predecessor.get("boundaries") or {}).get("rights_status") or "unknown")
    if rights_status != "pending":
        raise VerticalShortCandidateError("OUT-05 requires the accepted pending-rights baseline")
    return {
        "readback_sha256": actual_readback_hash,
        "video_sha256": actual_video_hash,
        "predecessor_video_path": predecessor_video_path,
        "source_video_path": source_video_path,
        "source_audio_path": source_audio_path,
        "input_paths": input_paths,
        "materials": {"source_video": video_material, "source_audio": audio_material},
        "rights_status": rights_status,
    }


def _build_subtitle_presentation(
    predecessor_subtitles: list[dict[str, Any]],
    *,
    application_key: str = "out05_application",
    dimension_source: str = "out05_vertical_canvas_width_clamped_safe_envelope",
    line_break_hints: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    base_style = _diagnostic_ass_style_for_candidate(ED10L_KEIFONT_CANDIDATE_ID)
    base_layout = _subtitle_layout_contract(
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        mode="bottom_center_emphasis",
        dimension_source="out05_vertical_canvas",
        diagnostic_ass_style=base_style,
    )
    lead_style = _ed10w_candidate_ass_style(
        base_style=base_style,
        base_layout=base_layout,
        candidate={"candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID},
    )
    layout = _subtitle_layout_contract(
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        mode="bottom_center_emphasis",
        dimension_source=dimension_source,
        diagnostic_ass_style=lead_style,
    )
    values = layout["values"]
    values.update(
        {
            "font_size": 92,
            "outline": 9,
            "shadow": 2,
            "margin_l": 90,
            "margin_r": 90,
            "bottom_margin": 310,
            "line_height": 106,
            "bottom_center_x": 540,
            "bottom_center_y": 1610,
            "dialogue_wrap_eaw": 20,
        }
    )
    layout["formulas"].update(
        {
            "font_size": "min(round(frame_height * 0.125), round(frame_width * 0.0852))",
            "outline": "round(font_size * 0.096)",
            "shadow": "round(font_size * 0.019)",
            "horizontal_margin": "round(frame_width * 0.0833)",
            "bottom_margin": "round(frame_height * 0.1615)",
            "dialogue_y": "frame_height - bottom_margin",
        }
    )
    layout["vertical_safe_envelope"] = {
        "policy": "internal_vertical_candidate_conservative_envelope_v0",
        "frame": {"left": 72, "right": 1008, "top": 180, "bottom": 1680},
        "subtitle": {"left": 90, "right": 990, "top": 1080, "bottom": 1610},
        "platform_production_safe_claimed": False,
        "reason": (
            "Keep the full 16:9 action band visible and place dialogue in the lower "
            "source-derived canvas with conservative side and bottom clearance."
        ),
    }
    raw_items = [
        {
            "subtitle_id": str(item["id"]),
            "cut_id": str(item["cut_id"]),
            "status": "included",
            "render_start_seconds": float(item["sequence_start_seconds"]),
            "render_end_seconds": float(item["sequence_end_seconds"]),
            "text": str(item["text"]),
            "source_text": str(item.get("source_text") or item["text"]),
            "display_text_normalization": str(
                item.get("display_text_normalization") or "none"
            ),
            "source_type": str(item.get("source_type") or ""),
            "source_segment_ids": list(item.get("source_segment_ids") or []),
            "json3_timing_authority": dict(
                item.get("json3_timing_authority") or {}
            ),
        }
        for item in predecessor_subtitles
    ]
    presentation = _presentation_items(raw_items, layout=layout)
    presentation = _apply_vertical_balanced_wrap(
        presentation,
        layout=layout,
        line_break_hints=line_break_hints,
    )
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
    selector[application_key] = {
        "lead_bounded_decoration_candidate_id": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
        "fallback_reference_candidate_id": ED10W_CANDIDATE0_BASELINE_ID,
        "base_font_candidate_id": ED10L_KEIFONT_CANDIDATE_ID,
        "speaker_identity_verified": False,
        "speaker_identity_layer_omitted": True,
        "visible_placeholder_badge_omitted": True,
        "body_text_color_policy": "stable_default_body_text",
    }
    return layout, presentation, selector


def build_vertical_subtitle_presentation(
    subtitles: list[dict[str, Any]],
    *,
    application_key: str,
    dimension_source: str,
    line_break_hints: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Shared measured subtitle-layout boundary for vertical review candidates."""

    return _build_subtitle_presentation(
        subtitles,
        application_key=application_key,
        dimension_source=dimension_source,
        line_break_hints=line_break_hints,
    )


def _apply_vertical_balanced_wrap(
    items: list[dict[str, Any]],
    *,
    layout: dict[str, Any],
    line_break_hints: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Rebalance measured-valid lines for the narrower vertical canvas.

    The existing wrapper remains the measurement and candidate source.  This
    pass only chooses a less ragged partition within the same width limit and
    prevents a short verb/punctuation tail from becoming a fourth line.
    """

    updated: list[dict[str, Any]] = []
    for item in items:
        original_lines = list(item.get("wrapped_lines") or [str(item.get("text") or "")])
        balance = _balanced_vertical_lines(
            str(item.get("text") or ""),
            layout=layout,
            font_bbox_readback=item.get("font_bbox_wrap_readback") or {},
            line_break_hint=_line_break_hint_for_item(
                item,
                line_break_hints=line_break_hints,
            ),
        )
        lines = balance["lines"] if balance["status"] == "applied" else original_lines
        wrapped_text = "\n".join(lines)
        font_bbox = dict(item.get("font_bbox_wrap_readback") or {})
        font_bbox.update(
            {
                "out05_vertical_balance": balance,
                "selected_wrapped_lines": lines,
                "wrapped_text": wrapped_text,
                "explicit_line_breaks_passed_to_ass": True,
                "applied_to_proof_text": True,
            }
        )
        updated.append(
            {
                **item,
                "wrapped_text": wrapped_text,
                "wrapped_lines": lines,
                "wrapped_line_count": len(lines),
                "max_wrapped_line_eaw": max(
                    (measure_subtitle(line).longest_line_eaw for line in lines),
                    default=0,
                ),
                "layout": _item_layout(layout, wrapped_line_count=len(lines)),
                "font_bbox_wrap_readback": font_bbox,
                "vertical_balance_readback": balance,
            }
        )
    return updated


def _balanced_vertical_lines(
    text: str,
    *,
    layout: dict[str, Any],
    font_bbox_readback: dict[str, Any],
    line_break_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = text.strip()
    if not source:
        return {"status": "not_applied_empty_text", "lines": [""]}
    max_pixel_width = int(
        ((font_bbox_readback.get("wrap_algorithm") or {}).get("max_text_width") or 0)
    )
    font_file = font_bbox_readback.get("font_file")
    font_size = int(layout["values"]["font_size"])
    stroke = int(layout["values"]["outline"])
    measure_mode = "east_asian_width_proxy"
    max_width = float(layout["values"]["dialogue_wrap_eaw"])

    def measure(line: str) -> float:
        return float(measure_subtitle(line).longest_line_eaw)

    if (
        subtitle_style_spike.Image is not None
        and subtitle_style_spike.ImageDraw is not None
        and font_file
        and Path(str(font_file)).is_file()
        and max_pixel_width > 0
    ):
        try:
            font = subtitle_style_spike._load_font(str(font_file), font_size)
            image = subtitle_style_spike.Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0))
            draw = subtitle_style_spike.ImageDraw.Draw(image)

            def measure(line: str) -> float:
                bbox = subtitle_style_spike._text_bbox_at_origin(
                    draw=draw,
                    text=line,
                    font=font,
                    spacing=0,
                    stroke_width=stroke,
                )
                return float(max(0, bbox[2] - bbox[0]))

            measure_mode = "existing_pillow_font_bbox_pixel_measurement"
            max_width = float(max_pixel_width)
        except Exception:
            measure_mode = "east_asian_width_proxy_after_font_measurement_failure"

    hint_result = _select_preferred_hint_lines(
        source,
        hint=line_break_hint,
        measure=measure,
        max_width=max_width,
    )
    if hint_result is not None:
        lines, widths, hint_readback = hint_result
        return {
            "status": "applied",
            "algorithm": "out06_hint_validated_existing_measurement_partition_v1",
            "measurement_mode": measure_mode,
            "max_width": round(max_width, 3),
            "line_count": len(lines),
            "lines": lines,
            "measured_widths": [round(value, 3) for value in widths],
            "break_indices": _break_indices_for_lines(source, lines),
            "score": 0.0,
            "short_final_tail": len(lines) > 1 and _content_character_count(lines[-1]) < 4,
            "line_break_hint": hint_readback,
            "production_typography_readiness_claimed": False,
        }

    total_content = _content_character_count(source)
    best: tuple[float, list[str], list[float], tuple[int, ...]] | None = None
    maximum_lines = min(3, max(1, len(source)))
    for line_count in range(1, maximum_lines + 1):
        for breaks in itertools.combinations(range(1, len(source)), line_count - 1):
            boundaries = (0, *breaks, len(source))
            lines = [
                source[boundaries[index] : boundaries[index + 1]].strip()
                for index in range(line_count)
            ]
            if any(not line for line in lines):
                continue
            counts = [_content_character_count(line) for line in lines]
            if total_content >= 8 and any(count < 2 for count in counts):
                continue
            if total_content >= 12 and counts[-1] < 4:
                continue
            if any(_invalid_line_edge(line) for line in lines):
                continue
            widths = [measure(line) for line in lines]
            if any(width > max_width + 0.5 for width in widths):
                continue
            score = _vertical_partition_score(
                source,
                breaks=breaks,
                widths=widths,
                max_width=max_width,
                line_count=line_count,
                line_break_hint=line_break_hint,
            )
            candidate = (score, lines, widths, breaks)
            if best is None or candidate[0] < best[0]:
                best = candidate
        if best is not None:
            # Prefer the smallest measured-valid line count; scoring chooses its partition.
            break
    if best is None:
        return {
            "status": "not_applied_no_three_line_measured_valid_partition",
            "lines": list(font_bbox_readback.get("selected_wrapped_lines") or [source]),
            "measurement_mode": measure_mode,
            "max_width": max_width,
        }
    score, lines, widths, breaks = best
    return {
        "status": "applied",
        "algorithm": "out05_existing_measurement_balanced_partition_v0",
        "measurement_mode": measure_mode,
        "max_width": round(max_width, 3),
        "line_count": len(lines),
        "lines": lines,
        "measured_widths": [round(value, 3) for value in widths],
        "break_indices": list(breaks),
        "score": round(score, 6),
        "short_final_tail": len(lines) > 1 and _content_character_count(lines[-1]) < 4,
        "line_break_hint": _line_break_hint_readback(source, line_break_hint),
        "production_typography_readiness_claimed": False,
    }


def _vertical_partition_score(
    source: str,
    *,
    breaks: tuple[int, ...],
    widths: list[float],
    max_width: float,
    line_count: int,
    line_break_hint: dict[str, Any] | None = None,
) -> float:
    mean = sum(widths) / len(widths)
    score = sum(((width - mean) / max_width) ** 2 for width in widths)
    score += max(0.0, 0.55 - (widths[-1] / max_width)) * 2.0
    score += line_count * 0.03
    opening = "「『（([{【〈《"
    closing = "、。！？!?)]}」』】〉》"
    punctuation = "、。！？!?…"
    for index in breaks:
        previous = source[index - 1]
        following = source[index]
        if previous.isspace() or following.isspace():
            score -= 0.30
        if previous in punctuation:
            score -= 0.38
        if previous in opening or following in closing:
            score += 10.0
        if _is_hiragana(previous) and _is_hiragana(following):
            score += 0.55
        elif _is_kanji(previous) and _is_kanji(following):
            score += 0.18
        elif previous in "はがをにへでとものやて" and not _is_hiragana(following):
            score -= 0.08
    hinted = _line_break_hint_readback(source, line_break_hint)
    for index in breaks:
        boundary_tokens = _boundary_tokens(source, index)
        if any(
            forbidden in boundary_tokens
            for forbidden in hinted.get("forbidden_boundaries", ())
        ):
            score += 25.0
    return score


def _line_break_hint_for_item(
    item: dict[str, Any],
    *,
    line_break_hints: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    subtitle_id = str(item.get("subtitle_id") or item.get("id") or "")
    hint = (line_break_hints or {}).get(subtitle_id)
    source = "caller_supplied_reviewed_line_break_hint"
    if hint is None:
        hint = REVIEWED_LINE_BREAK_HINTS.get(subtitle_id)
        source = "reviewed_out06_user_feedback_declarative_cue_metadata"
    if hint is None:
        return None
    return {
        **hint,
        "subtitle_id": subtitle_id,
        "source": str(hint.get("source") or source),
    }


def _line_break_hint_readback(
    source: str, hint: dict[str, Any] | None
) -> dict[str, Any]:
    if not hint:
        return {"status": "none"}
    preferred_lines = [
        list(candidate)
        for candidate in hint.get("preferred_lines", [])
        if "".join(str(line) for line in candidate) == source
    ]
    return {
        "status": "available",
        "source": hint.get("source"),
        "subtitle_id": hint.get("subtitle_id"),
        "reason": hint.get("reason"),
        "preferred_lines": preferred_lines,
        "forbidden_boundaries": list(hint.get("forbidden_boundaries") or []),
    }


def _select_preferred_hint_lines(
    source: str,
    *,
    hint: dict[str, Any] | None,
    measure: Callable[[str], float],
    max_width: float,
) -> tuple[list[str], list[float], dict[str, Any]] | None:
    if not hint:
        return None
    readback = _line_break_hint_readback(source, hint)
    for candidate in readback.get("preferred_lines", []):
        lines = [str(line).strip() for line in candidate]
        if not lines or len(lines) > 3 or any(not line for line in lines):
            continue
        if "".join(lines) != source:
            continue
        if any(_invalid_line_edge(line) for line in lines):
            continue
        widths = [measure(line) for line in lines]
        if any(width > max_width + 0.5 for width in widths):
            continue
        return (
            lines,
            widths,
            {
                **readback,
                "status": "applied_preferred_lines",
                "selected_lines": lines,
                "measured_widths": [round(value, 3) for value in widths],
            },
        )
    return None


def _break_indices_for_lines(source: str, lines: list[str]) -> list[int]:
    indices: list[int] = []
    cursor = 0
    for line in lines[:-1]:
        cursor += len(line)
        indices.append(cursor)
    if "".join(lines) != source:
        return []
    return indices


def _boundary_tokens(source: str, index: int) -> set[str]:
    previous = source[:index].rstrip()
    following = source[index:].lstrip()
    if not previous or not following:
        return set()
    left = previous[-5:]
    right = following[:5]
    tokens = set()
    for left_size in range(1, len(left) + 1):
        for right_size in range(1, len(right) + 1):
            tokens.add(f"{left[-left_size:]}|{right[:right_size]}")
    return tokens


def _invalid_line_edge(line: str) -> bool:
    return line[0] in "、。！？!?)]}」』】〉》" or line[-1] in "「『（([{【〈《"


def _content_character_count(text: str) -> int:
    return sum(1 for char in text if not char.isspace() and char not in "、。！？!?…😏")


def _is_hiragana(char: str) -> bool:
    return "\u3040" <= char <= "\u309f"


def _is_kanji(char: str) -> bool:
    return "\u3400" <= char <= "\u9fff"


def _validate_subtitle_containment(
    items: list[dict[str, Any]],
    *,
    expected_duration: float,
    layout: dict[str, Any],
    expected_count: int = 9,
) -> dict[str, Any]:
    safe = layout["vertical_safe_envelope"]["subtitle"]
    checks: list[dict[str, Any]] = []
    previous_end = 0.0
    for item in items:
        start = float(item["display_start_seconds"])
        end = float(item["display_end_seconds"])
        if start < -0.001 or end > expected_duration + 0.001 or end <= start:
            raise VerticalShortCandidateError(f"subtitle timing is outside candidate: {item['subtitle_id']}")
        if start + 0.001 < previous_end:
            raise VerticalShortCandidateError(f"subtitle overlap remains after replacement: {item['subtitle_id']}")
        previous_end = end
        line_count = int(item.get("wrapped_line_count") or 1)
        if line_count > 3:
            raise VerticalShortCandidateError(f"subtitle exceeds three-line safe envelope: {item['subtitle_id']}")
        estimated_top = int(layout["values"]["bottom_center_y"]) - (
            int(layout["values"]["line_height"]) * line_count
        )
        if estimated_top < int(safe["top"]):
            raise VerticalShortCandidateError(f"subtitle exceeds vertical safe envelope: {item['subtitle_id']}")
        if item.get("suspicious_tail_line_present") is True:
            raise VerticalShortCandidateError(f"subtitle has suspicious wrapped tail: {item['subtitle_id']}")
        checks.append(
            {
                "subtitle_id": item["subtitle_id"],
                "start_seconds": start,
                "end_seconds": end,
                "wrapped_lines": list(item.get("wrapped_lines") or []),
                "wrapped_line_count": line_count,
                "estimated_top": estimated_top,
                "safe": True,
            }
        )
    if len(checks) != expected_count:
        raise VerticalShortCandidateError(
            f"candidate must preserve exactly {expected_count} subtitles"
        )
    return {
        "status": "passed",
        "subtitle_count": len(checks),
        "all_inside_timeline": True,
        "all_inside_vertical_safe_envelope": True,
        "maximum_line_count": max((item["wrapped_line_count"] for item in checks), default=0),
        "checks": checks,
    }


def validate_vertical_subtitle_containment(
    items: list[dict[str, Any]],
    *,
    expected_duration: float,
    layout: dict[str, Any],
    expected_count: int,
) -> dict[str, Any]:
    """Validate timing, overlap, line count, and the shared vertical envelope."""

    return _validate_subtitle_containment(
        items,
        expected_duration=expected_duration,
        layout=layout,
        expected_count=expected_count,
    )


def _build_reframe_plan(predecessor: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.out05.reframe_plan.v0",
        "artifact_id": ARTIFACT_ID,
        "source_frame": {"width": 1920, "height": 1080, "aspect_ratio": "16:9"},
        "output_frame": {"width": FRAME_WIDTH, "height": FRAME_HEIGHT, "aspect_ratio": "9:16"},
        "comparison_scope": "still_frame_specimens_only_no_three_full_video_renders",
        "comparison_frame_sources": [
            {"cut_id": "cut_001", "source_seconds": 5.453},
            {"cut_id": "cut_002", "source_seconds": 14.700},
        ],
        "options": [
            {
                "id": "cut_level_explicit_anchor_crop",
                "foreground": "608x1080 source crop scaled to 1080x1920",
                "cut_anchors": {"cut_001": 0.68, "cut_002": 0.78},
                "assessment": "rejected_information_loss_left_right_composition",
            },
            {
                "id": SELECTED_REFRAME,
                "foreground": "full 1920x1080 fit at 1080x608 centered",
                "canvas": "same-source fill crop plus blur, reduced saturation and brightness",
                "assessment": "selected_preserves_complete_subject_action_and_dialogue_composition",
            },
            {
                "id": "bounded_hybrid",
                "foreground": "1280x720 center crop to 1080x720 over same-source canvas",
                "assessment": "held_minor_edge_loss_without_clear_subject_gain",
            },
        ],
        "selected_option": SELECTED_REFRAME,
        "selection_reason": (
            "Both accepted cuts contain meaningful left/right composition. The explicit anchor crop "
            "can remove the phone counterpart or action entry, while the bounded hybrid still loses "
            "edge context without a clear gain. Full fit plus source-derived canvas preserves the "
            "accepted editorial information and is the tie/default route."
        ),
        "timeline_preserved": {
            "ordered_cut_ids": list(predecessor["ordered_cut_ids"]),
            "duration_seconds": predecessor["expected_duration_seconds"],
            "hard_cut_seconds": EXPECTED_BOUNDARY_SECONDS,
            "new_cut_added": False,
            "transition_added": False,
        },
        "subtitle_safe_envelope": {
            "left": 90,
            "right": 990,
            "top": 1080,
            "bottom": 1610,
            "platform_production_safe_claimed": False,
        },
    }


def _validate_reframe_plan(plan: dict[str, Any]) -> None:
    if tuple(item.get("id") for item in plan.get("options") or []) != REFRAME_OPTIONS:
        raise VerticalShortCandidateError("reframe comparison must contain the three bounded options")
    if plan.get("selected_option") != SELECTED_REFRAME:
        raise VerticalShortCandidateError("OUT-05 selected reframe must be full fit plus source-derived canvas")
    output = plan.get("output_frame") or {}
    if (output.get("width"), output.get("height")) != (FRAME_WIDTH, FRAME_HEIGHT):
        raise VerticalShortCandidateError("OUT-05 output frame must be 1080x1920")
    preserved = plan.get("timeline_preserved") or {}
    if tuple(preserved.get("ordered_cut_ids") or ()) != EXPECTED_CUT_IDS:
        raise VerticalShortCandidateError("reframe plan changed the accepted cut order")
    if preserved.get("new_cut_added") is not False or preserved.get("transition_added") is not False:
        raise VerticalShortCandidateError("reframe plan must not add cuts or transitions")


def _candidate_readback(
    *,
    root: Path,
    episode: Path,
    output: Path,
    predecessor: dict[str, Any],
    predecessor_info: dict[str, Any],
    source_hashes: dict[str, str],
    protected: dict[str, dict[str, Any]],
    subtitle_layout: dict[str, Any],
    subtitle_items: list[dict[str, Any]],
    subtitle_containment: dict[str, Any],
    selector_readback: dict[str, Any],
    reframe_plan: dict[str, Any],
    render_result: dict[str, Any],
    stage_paths: dict[str, Path],
    final_paths: dict[str, Path],
    rights_status: str,
) -> dict[str, Any]:
    output_hashes = {
        label: {
            "path": _relative(final_paths[label], root),
            "sha256": _sha256(stage_path),
        }
        for label, stage_path in stage_paths.items()
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "episode_id": str(predecessor.get("episode_id") or episode.name),
        "source_class": "accepted_out04_real_local_retained_source_media",
        "storage": {
            "class": "ignored_local_retained_same_machine",
            "portable_across_clones": False,
            "episodes_tracked": False,
        },
        "predecessor": {
            "artifact_id": predecessor["artifact_id"],
            "readback_path": _relative(_resolved(root, Path(predecessor["machine_readback"])), root),
            "readback_sha256": predecessor_info["readback_sha256"],
            "video_sha256": predecessor_info["video_sha256"],
            "accepted_scope": "OUT-04 internal editorial representative sequence only",
            "immutable_validation": "passed",
        },
        "timeline": {
            "ordered_cut_ids": list(EXPECTED_CUT_IDS),
            "expected_duration_seconds": EXPECTED_DURATION_SECONDS,
            "hard_cut_seconds": EXPECTED_BOUNDARY_SECONDS,
            "transition_type": "hard_cut",
            "cut_003_included": False,
            "timeline_changed": False,
        },
        "reframe": reframe_plan,
        "subtitle": {
            "count": len(subtitle_items),
            "burned_in_ass": _relative(final_paths["ass"], root),
            "portable_srt": _relative(final_paths["srt"], root),
            "presentation_mode": "bottom_center_emphasis",
            "speaker_identity_verified": False,
            "speaker_identity_layer_omitted": True,
            "visible_placeholder_or_technical_label": False,
            "lead_candidate": ED10W_CANDIDATE2_BADGE_PRESSURE_ID,
            "fallback_reference": ED10W_CANDIDATE0_BASELINE_ID,
            "font_family": subtitle_layout["diagnostic_ass_style"].get("font_name"),
            "font_file": subtitle_layout["diagnostic_ass_style"].get("resolved_font_file"),
            "font_file_status": subtitle_layout["diagnostic_ass_style"].get("font_file_status"),
            "stable_body_text_color": True,
            "layout": subtitle_layout,
            "selector": selector_readback,
            "containment": subtitle_containment,
            "items": subtitle_items,
        },
        "audio": render_result["audio"],
        "render": {
            "output_path": _relative(final_paths["video"], root),
            "output_sha256": output_hashes["video"]["sha256"],
            "media": render_result["media"],
            "selected_video_encoder": render_result["selected_video_encoder"],
            "attempts": render_result["attempts"],
            "full_decode": render_result["full_decode"],
            "duration_tolerance_seconds": OUTPUT_DURATION_TOLERANCE_SECONDS,
            "duration_matches_expected": render_result["duration_matches_expected"],
            "faststart": True,
            "pixel_format": "yuv420p",
        },
        "quality_assurance": {
            "reframe_comparison": _relative(final_paths["reframe_comparison_contact_sheet"], root),
            "frame_contact_sheet": _relative(final_paths["frame_qa_contact_sheet"], root),
            "frame_samples": render_result["frame_samples"],
            "browser_required": True,
            "browser_result": "pending_external_browser_validation",
        },
        "input_hashes": source_hashes,
        "protected_evidence": protected,
        "outputs": output_hashes,
        "review_entrypoint": _relative(final_paths["index"], root),
        "machine_readback": _relative(final_paths["readback"], root),
        "open_command": _powershell_command(final_paths["open"], root),
        "review_questions": list(REVIEW_QUESTIONS),
        "boundaries": {
            "internal_review_only": True,
            "vertical_format_candidate": True,
            "production_candidate": False,
            "production_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "rights": rights_status,
            "rights_status": rights_status,
            "public_ready": False,
            "publishing": False,
            "publish_attempted": False,
        },
    }


def _render_candidate_assets(
    *,
    source_video_path: Path,
    source_audio_path: Path,
    timeline: list[dict[str, Any]],
    ass_path: Path,
    video_path: Path,
    compare_sheet_path: Path,
    frame_sheet_path: Path,
    work_dir: Path,
    subtitle_layout: dict[str, Any],
    ffmpeg_path: str | Path | None,
    ffprobe_path: str | Path | None,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    return render_vertical_sequence_assets(
        source_video_path=source_video_path,
        source_audio_path=source_audio_path,
        timeline=timeline,
        ass_path=ass_path,
        video_path=video_path,
        compare_sheet_path=compare_sheet_path,
        frame_sheet_path=frame_sheet_path,
        work_dir=work_dir,
        subtitle_layout=subtitle_layout,
        expected_duration=EXPECTED_DURATION_SECONDS,
        frame_samples=OUT05_FRAME_SAMPLES,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )


def render_vertical_sequence_assets(
    *,
    source_video_path: Path,
    source_audio_path: Path,
    timeline: list[dict[str, Any]],
    ass_path: Path,
    video_path: Path,
    compare_sheet_path: Path | None,
    frame_sheet_path: Path,
    work_dir: Path,
    subtitle_layout: dict[str, Any],
    expected_duration: float,
    frame_samples: tuple[tuple[str, float], ...],
    ffmpeg_path: str | Path | None,
    ffprobe_path: str | Path | None,
    composition_policy: dict[str, Any] | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
) -> dict[str, Any]:
    """Render a data-driven 9:16 hard-cut sequence using the OUT-05 path."""

    preflight = ffmpeg_tiny.preflight_tools(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    if preflight.get("status") != "passed":
        reason = preflight.get("failure_reason") or "render_tool_preflight_failed"
        raise VerticalShortCandidateError(f"FFmpeg/FFprobe preflight failed: {reason}")
    resolved_ffmpeg = str(preflight["ffmpeg"]["path"])
    resolved_ffprobe = str(preflight["ffprobe"]["path"])
    ffprobe_version = str(preflight["ffprobe"].get("version") or "unknown")
    ffprobe_source = str(preflight["ffprobe"].get("path_source") or "unknown")
    try:
        source_video_probe = ffmpeg_tiny.probe_media(
            input_path=source_video_path,
            ffprobe_path=resolved_ffprobe,
            ffprobe_version=ffprobe_version,
            ffprobe_path_source=ffprobe_source,
            runner=runner,
        ).metadata
        source_audio_probe = ffmpeg_tiny.probe_media(
            input_path=source_audio_path,
            ffprobe_path=resolved_ffprobe,
            ffprobe_version=ffprobe_version,
            ffprobe_path_source=ffprobe_source,
            runner=runner,
        ).metadata
    except ffmpeg_tiny.TinyRenderError as exc:
        raise VerticalShortCandidateError(f"source probe failed: {exc}") from exc
    _validate_source_probe(source_video_probe, source_audio_probe, timeline)
    composition_readback = _validate_vertical_composition_policy(
        composition_policy,
        source_video_probe=source_video_probe,
    )

    input_measurement = _measure_loudness(
        ffmpeg_path=resolved_ffmpeg,
        input_path=source_audio_path,
        timeline=timeline,
        runner=runner,
    )
    normalize = (
        abs(float(input_measurement["integrated_lufs"]) - (-14.0)) > 3.0
        or float(input_measurement["true_peak_dbtp"]) > -1.0
    )
    if normalize:
        normalization_filter = _normalization_filter(input_measurement)
        decision = "normalize_clear_loudness_gap_to_internal_candidate_target"
    else:
        normalization_filter = "anull"
        decision = "pass_through_no_clear_loudness_or_peak_issue"

    if compare_sheet_path is not None:
        _render_reframe_comparison_sheet(
            ffmpeg_path=resolved_ffmpeg,
            source_video_path=source_video_path,
            output_path=compare_sheet_path,
            work_dir=work_dir,
            runner=runner,
        )
    attempts: list[dict[str, Any]] = []
    selected_codec: str | None = None
    for codec in ("libx264", "libopenh264"):
        if video_path.exists():
            video_path.unlink()
        command = _vertical_render_command(
            ffmpeg_path=resolved_ffmpeg,
            source_video_path=source_video_path,
            source_audio_path=source_audio_path,
            ass_path=ass_path,
            font_file=Path(str(subtitle_layout["diagnostic_ass_style"].get("resolved_font_file") or "")),
            timeline=timeline,
            output_path=video_path,
            video_codec=codec,
            audio_filter=normalization_filter,
            composition_policy=composition_policy,
        )
        result = _run_command(command, runner=runner, timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS)
        status = "passed" if result.returncode == 0 and video_path.is_file() else "failed"
        attempts.append(
            {
                "video_codec": codec,
                "status": status,
                "exit_code": result.returncode,
                "stderr_sha256": hashlib.sha256((result.stderr or "").encode("utf-8")).hexdigest(),
            }
        )
        if status == "passed":
            selected_codec = codec
            break
    if selected_codec is None:
        raise VerticalShortCandidateError("FFmpeg vertical render failed for all H.264 profiles")

    try:
        output_probe = ffmpeg_tiny.probe_media(
            input_path=video_path,
            ffprobe_path=resolved_ffprobe,
            ffprobe_version=ffprobe_version,
            ffprobe_path_source=ffprobe_source,
            runner=runner,
        ).metadata
    except ffmpeg_tiny.TinyRenderError as exc:
        raise VerticalShortCandidateError(f"vertical candidate probe failed: {exc}") from exc
    details = _probe_output_details(
        ffprobe_path=resolved_ffprobe,
        input_path=video_path,
        runner=runner,
    )
    output_probe.update(details)
    faststart = _faststart_readback(video_path)
    if output_probe.get("pixel_format") != "yuv420p":
        raise VerticalShortCandidateError("vertical candidate pixel format must be yuv420p")
    if faststart.get("status") != "passed":
        raise VerticalShortCandidateError("vertical candidate must place moov before mdat")

    decode_command = [
        resolved_ffmpeg,
        "-hide_banner",
        "-v",
        "error",
        "-i",
        str(video_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-f",
        "null",
        os.devnull,
    ]
    decoded = _run_command(
        decode_command,
        runner=runner,
        timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
    )
    full_decode = {
        "status": "passed" if decoded.returncode == 0 else "failed",
        "exit_code": decoded.returncode,
        "stderr_empty": not bool((decoded.stderr or "").strip()),
    }
    if full_decode["status"] != "passed":
        raise VerticalShortCandidateError("vertical candidate full decode failed")

    output_measurement = _measure_loudness(
        ffmpeg_path=resolved_ffmpeg,
        input_path=video_path,
        timeline=None,
        runner=runner,
    )
    frame_sample_readback = _render_frame_qa_sheet(
        ffmpeg_path=resolved_ffmpeg,
        video_path=video_path,
        output_path=frame_sheet_path,
        work_dir=work_dir,
        samples=frame_samples,
        runner=runner,
    )
    return {
        "media": output_probe,
        "selected_video_encoder": selected_codec,
        "attempts": attempts,
        "duration_matches_expected": (
            abs(float(output_probe.get("duration_seconds") or 0.0) - expected_duration)
            <= OUTPUT_DURATION_TOLERANCE_SECONDS
        ),
        "full_decode": full_decode,
        "faststart": faststart,
        "source_probe": {"video": source_video_probe, "audio": source_audio_probe},
        "composition_policy": composition_readback,
        "audio": {
            "measurement_method": "ffmpeg_loudnorm_json_true_peak",
            "input_measurement": input_measurement,
            "decision": decision,
            "normalization_applied": normalize,
            "target": {"integrated_lufs": -14.0, "true_peak_dbtp_max": -1.0},
            "render_filter_target_true_peak_dbtp": -1.5 if normalize else None,
            "output_measurement": output_measurement,
        },
        "frame_samples": frame_sample_readback,
    }


def _validate_source_probe(
    video: dict[str, Any], audio: dict[str, Any], timeline: list[dict[str, Any]]
) -> None:
    video_counts = video.get("stream_counts") or {}
    audio_counts = audio.get("stream_counts") or {}
    if int(video_counts.get("video") or 0) < 1:
        raise VerticalShortCandidateError("source video stream is missing")
    if int(audio_counts.get("audio") or 0) < 1:
        raise VerticalShortCandidateError("source audio stream is missing")
    maximum_end = max(float(item["source_end_seconds"]) for item in timeline)
    if float(video.get("duration_seconds") or 0.0) + 0.05 < maximum_end:
        raise VerticalShortCandidateError("source video does not contain accepted timeline")
    if float(audio.get("duration_seconds") or 0.0) + 0.05 < maximum_end:
        raise VerticalShortCandidateError("source audio does not contain accepted timeline")


def _measure_loudness(
    *,
    ffmpeg_path: str,
    input_path: Path,
    timeline: list[dict[str, Any]] | None,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, float]:
    command = [ffmpeg_path, "-hide_banner", "-nostats", "-i", str(input_path)]
    if timeline is None:
        command.extend(
            [
                "-map",
                "0:a:0",
                "-af",
                "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
            ]
        )
    else:
        filters: list[str] = []
        labels: list[str] = []
        for index, cut in enumerate(timeline):
            start = _seconds(float(cut["source_start_seconds"]))
            end = _seconds(float(cut["source_end_seconds"]))
            filters.append(
                f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{index}]"
            )
            labels.append(f"[a{index}]")
        filters.append(
            f"{''.join(labels)}concat=n={len(timeline)}:v=0:a=1,"
            "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[aout]"
        )
        command.extend(["-filter_complex", ";".join(filters), "-map", "[aout]"])
    command.extend(["-f", "null", os.devnull])
    result = _run_command(
        command,
        runner=runner,
        timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise VerticalShortCandidateError("audio loudness measurement failed")
    match = re.search(r"\{\s*\"input_i\".*?\}", result.stderr or "", flags=re.DOTALL)
    if match is None:
        raise VerticalShortCandidateError("audio loudness JSON was not found")
    try:
        payload = json.loads(match.group(0))
        return {
            "integrated_lufs": float(payload["input_i"]),
            "true_peak_dbtp": float(payload["input_tp"]),
            "loudness_range_lu": float(payload["input_lra"]),
            "threshold_lufs": float(payload["input_thresh"]),
            "target_offset_lu": float(payload["target_offset"]),
        }
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise VerticalShortCandidateError(f"invalid audio loudness JSON: {exc}") from exc


def _normalization_filter(measurement: dict[str, float]) -> str:
    return (
        "loudnorm=I=-14:TP=-1.5:LRA=11:"
        f"measured_I={measurement['integrated_lufs']}:"
        f"measured_TP={measurement['true_peak_dbtp']}:"
        f"measured_LRA={measurement['loudness_range_lu']}:"
        f"measured_thresh={measurement['threshold_lufs']}:"
        f"offset={measurement['target_offset_lu']}:"
        "linear=false:print_format=summary"
    )


def _vertical_render_command(
    *,
    ffmpeg_path: str,
    source_video_path: Path,
    source_audio_path: Path,
    ass_path: Path,
    font_file: Path,
    timeline: list[dict[str, Any]],
    output_path: Path,
    video_codec: str,
    audio_filter: str,
    composition_policy: dict[str, Any] | None = None,
) -> list[str]:
    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, cut in enumerate(timeline):
        start = _seconds(float(cut["source_start_seconds"]))
        end = _seconds(float(cut["source_end_seconds"]))
        background_filter, foreground_filter = _vertical_composition_filters(
            index=index,
            composition_policy=composition_policy,
        )
        filters.extend(
            [
                f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,split=2[bgraw{index}][fgraw{index}]",
                background_filter,
                foreground_filter,
                (
                    f"[bg{index}][fg{index}]overlay=(W-w)/2:(H-h)/2,setsar=1,"
                    f"fps={int(FRAME_RATE)},format=yuv420p[v{index}]"
                ),
                f"[1:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{index}]",
            ]
        )
        concat_inputs.extend([f"[v{index}]", f"[a{index}]"])
    filters.append(
        f"{''.join(concat_inputs)}concat=n={len(timeline)}:v=1:a=1[vseq][aseq]"
    )
    ass = _escape_filter_path(ass_path)
    fonts_dir = _escape_filter_path(font_file.parent) if font_file.is_file() else None
    ass_filter = f"ass=filename='{ass}'"
    if fonts_dir:
        ass_filter += f":fontsdir='{fonts_dir}'"
    filters.append(f"[vseq]{ass_filter},format=yuv420p[vout]")
    filters.append(f"[aseq]{audio_filter},aresample=48000[aout]")
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
        "[aout]",
        "-c:v",
        video_codec,
        *(
            ["-preset", "medium", "-crf", "18"]
            if video_codec == "libx264"
            else ["-b:v", "8M"]
        ),
        "-pix_fmt",
        "yuv420p",
        "-r",
        "30",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        "-shortest",
        str(output_path),
    ]


def _vertical_composition_filters(
    *,
    index: int,
    composition_policy: dict[str, Any] | None,
) -> tuple[str, str]:
    if composition_policy is None:
        return (
            (
                f"[bgraw{index}]scale={FRAME_WIDTH}:{FRAME_HEIGHT}:"
                "force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={FRAME_WIDTH}:{FRAME_HEIGHT},gblur=sigma=42,"
                f"eq=saturation=0.72:brightness=-0.10[bg{index}]"
            ),
            f"[fgraw{index}]scale={FRAME_WIDTH}:-2:flags=lanczos[fg{index}]",
        )
    background = composition_policy["background_source_crop_pixels"]
    foreground = composition_policy["foreground_source_crop_pixels"]
    background_crop = _pixel_crop_filter(background)
    foreground_crop = _pixel_crop_filter(foreground)
    return (
        (
            f"[bgraw{index}]{background_crop},"
            f"scale={FRAME_WIDTH}:{FRAME_HEIGHT}:"
            "force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={FRAME_WIDTH}:{FRAME_HEIGHT},gblur=sigma=42,"
            f"eq=saturation=0.72:brightness=-0.10[bg{index}]"
        ),
        (
            f"[fgraw{index}]{foreground_crop},"
            f"scale={FRAME_WIDTH}:-2:flags=lanczos[fg{index}]"
        ),
    )


def _pixel_crop_filter(rectangle: dict[str, Any]) -> str:
    return (
        f"crop={int(rectangle['width'])}:{int(rectangle['height'])}:"
        f"{int(rectangle['x'])}:{int(rectangle['y'])}"
    )


def _validate_vertical_composition_policy(
    composition_policy: dict[str, Any] | None,
    *,
    source_video_probe: dict[str, Any],
) -> dict[str, Any]:
    """Validate an optional source-specific canvas policy without changing defaults."""

    if composition_policy is None:
        return {
            "mode": DEFAULT_BACKGROUND_POLICY,
            "default_policy_unchanged": True,
        }
    if composition_policy.get("mode") != CAPTION_FREE_BACKGROUND_POLICY:
        raise VerticalShortCandidateError("unsupported vertical composition policy")
    if (
        composition_policy.get("full_source_blur_fallback_allowed") is not False
        or composition_policy.get("additional_blur_or_frosted_caption_surface")
        is not False
    ):
        raise VerticalShortCandidateError(
            "caption-free composition must fail closed without full-source blur fallback"
        )
    expected_width = int(source_video_probe.get("width") or 0)
    expected_height = int(source_video_probe.get("height") or 0)
    source_frame = composition_policy.get("source_frame_pixels") or {}
    if source_frame != {"width": expected_width, "height": expected_height}:
        raise VerticalShortCandidateError(
            "composition policy source dimensions do not match probed video"
        )
    background = _validated_pixel_rectangle(
        composition_policy.get("background_source_crop_pixels"),
        frame_width=expected_width,
        frame_height=expected_height,
        label="background source crop",
    )
    foreground = _validated_pixel_rectangle(
        composition_policy.get("foreground_source_crop_pixels"),
        frame_width=expected_width,
        frame_height=expected_height,
        label="foreground source crop",
    )
    band = _validated_pixel_rectangle(
        composition_policy.get("native_caption_band_pixels"),
        frame_width=expected_width,
        frame_height=expected_height,
        label="native caption band",
    )
    suppression = composition_policy.get("native_caption_suppression") or {}
    if suppression.get("method") != "bottom_crop":
        raise VerticalShortCandidateError(
            "native caption suppression must use the approved bottom crop"
        )
    if _rectangles_overlap(background, band) or _rectangles_overlap(foreground, band):
        raise VerticalShortCandidateError(
            "caption-free crop intersects the native caption band"
        )
    if (
        foreground["x"] != 0
        or foreground["y"] != 0
        or foreground["width"] != expected_width
        or foreground["height"] != band["y"]
    ):
        raise VerticalShortCandidateError(
            "bottom-crop suppression does not exactly remove the measured caption band"
        )
    return {
        **composition_policy,
        "background_source_crop_pixels": background,
        "foreground_source_crop_pixels": foreground,
        "native_caption_band_pixels": band,
        "default_policy_unchanged": False,
        "validated_against_source_probe": True,
    }


def _validated_pixel_rectangle(
    value: Any,
    *,
    frame_width: int,
    frame_height: int,
    label: str,
) -> dict[str, int]:
    if not isinstance(value, dict):
        raise VerticalShortCandidateError(f"{label} is missing")
    try:
        rectangle = {
            key: int(value[key]) for key in ("x", "y", "width", "height")
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise VerticalShortCandidateError(f"{label} is invalid") from exc
    if (
        rectangle["x"] < 0
        or rectangle["y"] < 0
        or rectangle["width"] <= 0
        or rectangle["height"] <= 0
        or rectangle["x"] + rectangle["width"] > frame_width
        or rectangle["y"] + rectangle["height"] > frame_height
        or rectangle["width"] % 2
        or rectangle["height"] % 2
    ):
        raise VerticalShortCandidateError(f"{label} leaves the source frame")
    return rectangle


def _rectangles_overlap(left: dict[str, int], right: dict[str, int]) -> bool:
    return (
        max(left["x"], right["x"])
        < min(left["x"] + left["width"], right["x"] + right["width"])
        and max(left["y"], right["y"])
        < min(left["y"] + left["height"], right["y"] + right["height"])
    )


def _render_reframe_comparison_sheet(
    *,
    ffmpeg_path: str,
    source_video_path: Path,
    output_path: Path,
    work_dir: Path,
    runner: ffmpeg_tiny.Runner,
) -> None:
    frames: list[Path] = []
    samples = (("cut_001", 5.453), ("cut_002", 14.700))
    for cut_id, seconds in samples:
        for option in REFRAME_OPTIONS:
            frame = work_dir / f"compare_{cut_id}_{option}.png"
            command = [
                ffmpeg_path,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-ss",
                _seconds(seconds),
                "-i",
                str(source_video_path),
                "-filter_complex",
                _specimen_filter(option, cut_id=cut_id),
                "-map",
                "[out]",
                "-frames:v",
                "1",
                str(frame),
            ]
            result = _run_command(
                command,
                runner=runner,
                timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
            )
            if result.returncode != 0 or not frame.is_file():
                raise VerticalShortCandidateError(f"reframe specimen failed: {cut_id}/{option}")
            frames.append(frame)
    _tile_images(
        ffmpeg_path=ffmpeg_path,
        inputs=frames,
        layout="0_0|360_0|720_0|0_640|360_640|720_640",
        output_path=output_path,
        runner=runner,
    )


def _specimen_filter(option: str, *, cut_id: str) -> str:
    if option == "cut_level_explicit_anchor_crop":
        anchor = 0.68 if cut_id == "cut_001" else 0.78
        x = round((1920 - 608) * anchor)
        return f"[0:v]crop=608:1080:{x}:0,scale=360:640:flags=lanczos[out]"
    if option == SELECTED_REFRAME:
        return (
            "[0:v]split=2[bgraw][fgraw];"
            "[bgraw]scale=360:640:force_original_aspect_ratio=increase:flags=lanczos,"
            "crop=360:640,gblur=sigma=14,eq=saturation=0.72:brightness=-0.10[bg];"
            "[fgraw]scale=360:-2:flags=lanczos[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[out]"
        )
    if option == "bounded_hybrid":
        return (
            "[0:v]split=2[bgraw][fgraw];"
            "[bgraw]scale=360:640:force_original_aspect_ratio=increase:flags=lanczos,"
            "crop=360:640,gblur=sigma=14,eq=saturation=0.72:brightness=-0.10[bg];"
            "[fgraw]scale=427:240:flags=lanczos,crop=360:240:(in_w-out_w)/2:0[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[out]"
        )
    raise VerticalShortCandidateError(f"unsupported reframe option: {option}")


def _render_frame_qa_sheet(
    *,
    ffmpeg_path: str,
    video_path: Path,
    output_path: Path,
    work_dir: Path,
    samples: tuple[tuple[str, float], ...] = OUT05_FRAME_SAMPLES,
    runner: ffmpeg_tiny.Runner,
) -> list[dict[str, Any]]:
    if not samples:
        raise VerticalShortCandidateError("frame QA requires at least one sample")
    frames: list[Path] = []
    readback: list[dict[str, Any]] = []
    for label, seconds in samples:
        frame = work_dir / f"qa_{label}.png"
        command = [
            ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            _seconds(seconds),
            "-i",
            str(video_path),
            "-vf",
            "scale=216:384:flags=lanczos",
            "-frames:v",
            "1",
            str(frame),
        ]
        result = _run_command(
            command,
            runner=runner,
            timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
        )
        if result.returncode != 0 or not frame.is_file():
            raise VerticalShortCandidateError(f"frame QA extraction failed: {label}")
        frames.append(frame)
        readback.append({"label": label, "seconds": seconds, "status": "extracted"})
    columns = min(5, len(frames))
    layout = "|".join(
        f"{(index % columns) * 216}_{(index // columns) * 384}"
        for index in range(len(frames))
    )
    _tile_images(
        ffmpeg_path=ffmpeg_path,
        inputs=frames,
        layout=layout,
        output_path=output_path,
        runner=runner,
    )
    return readback


def _tile_images(
    *,
    ffmpeg_path: str,
    inputs: list[Path],
    layout: str,
    output_path: Path,
    runner: ffmpeg_tiny.Runner,
) -> None:
    command = [ffmpeg_path, "-hide_banner", "-loglevel", "error", "-y"]
    for path in inputs:
        command.extend(["-i", str(path)])
    labels = "".join(f"[{index}:v]" for index in range(len(inputs)))
    command.extend(
        [
            "-filter_complex",
            f"{labels}xstack=inputs={len(inputs)}:layout={layout}:fill=black[out]",
            "-map",
            "[out]",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-update",
            "1",
            str(output_path),
        ]
    )
    result = _run_command(
        command,
        runner=runner,
        timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
    )
    if result.returncode != 0 or not output_path.is_file():
        raise VerticalShortCandidateError("contact sheet composition failed")


def _probe_output_details(
    *,
    ffprobe_path: str,
    input_path: Path,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=pix_fmt,profile,level",
        "-of",
        "json",
        str(input_path),
    ]
    result = _run_command(command, runner=runner, timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS)
    if result.returncode != 0:
        raise VerticalShortCandidateError("output pixel-format probe failed")
    try:
        payload = json.loads(result.stdout or "{}")
        stream = (payload.get("streams") or [{}])[0]
    except (json.JSONDecodeError, IndexError, TypeError) as exc:
        raise VerticalShortCandidateError(f"invalid output detail probe: {exc}") from exc
    return {
        "pixel_format": stream.get("pix_fmt"),
        "video_profile": stream.get("profile"),
        "video_level": stream.get("level"),
    }


def _faststart_readback(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        head = handle.read(min(path.stat().st_size, 8 * 1024 * 1024))
    moov = head.find(b"moov")
    mdat = head.find(b"mdat")
    passed = moov >= 0 and mdat >= 0 and moov < mdat
    return {
        "status": "passed" if passed else "failed",
        "moov_offset": moov,
        "mdat_offset": mdat,
        "moov_before_mdat": passed,
    }


def _run_command(
    command: list[str],
    *,
    runner: ffmpeg_tiny.Runner,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    try:
        return runner(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VerticalShortCandidateError(f"external render command failed: {exc}") from exc


def _escape_filter_path(path: Path) -> str:
    value = path.resolve().as_posix().replace("\\", "/")
    return value.replace(":", r"\:").replace("'", r"\'")


def _seconds(value: float) -> str:
    return f"{value:.3f}"


def _render_srt(items: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, item in enumerate(items, start=1):
        text = str(item.get("wrapped_text") or item.get("text") or "").replace("\r", "")
        blocks.append(
            f"{index}\n{_srt_time(float(item['display_start_seconds']))} --> "
            f"{_srt_time(float(item['display_end_seconds']))}\n{text}\n"
        )
    return "\n".join(blocks)


def _validate_ass_visible_content(
    path: Path,
    *,
    expected_count: int = 9,
    required_texts: tuple[str, ...] = (
        "もしもし？",
        "体育館裏で待ってます！！",
        "ホロライブの番長として",
    ),
) -> None:
    text = path.read_text(encoding="utf-8")
    event_lines = [line for line in text.splitlines() if line.startswith("Dialogue:")]
    if len(event_lines) != expected_count:
        raise VerticalShortCandidateError(
            f"ASS must contain exactly {expected_count} visible dialogue events"
        )
    forbidden = ("SPK", "DIAGNOSTIC", "TECHNICAL", "PLACEHOLDER")
    if any(token in line.upper() for token in forbidden for line in event_lines):
        raise VerticalShortCandidateError("ASS contains a visible placeholder/technical label")
    flattened = text.replace(r"\N", "").replace(" ", "")
    if not all(value.replace(" ", "") in flattened for value in required_texts):
        raise VerticalShortCandidateError("ASS lost expected UTF-8 Japanese subtitle text")


def validate_ass_visible_content(
    path: Path,
    *,
    expected_count: int,
    required_texts: tuple[str, ...],
) -> None:
    """Shared visible-event and UTF-8 guard for vertical ASS output."""

    _validate_ass_visible_content(
        path,
        expected_count=expected_count,
        required_texts=required_texts,
    )


def _validate_render_result(
    result: dict[str, Any],
    *,
    video_path: Path,
    expected_duration: float = EXPECTED_DURATION_SECONDS,
) -> None:
    _require_file(video_path, "vertical candidate video")
    media = result.get("media") if isinstance(result.get("media"), dict) else {}
    counts = media.get("stream_counts") if isinstance(media.get("stream_counts"), dict) else {}
    if int(counts.get("video") or 0) != 1 or int(counts.get("audio") or 0) != 1:
        raise VerticalShortCandidateError("vertical candidate must have one video and one audio stream")
    if str(media.get("video_codec") or "").lower() != "h264":
        raise VerticalShortCandidateError("vertical candidate video codec must be H.264")
    if str(media.get("audio_codec") or "").lower() != "aac":
        raise VerticalShortCandidateError("vertical candidate audio codec must be AAC")
    if (int(media.get("width") or 0), int(media.get("height") or 0)) != (
        FRAME_WIDTH,
        FRAME_HEIGHT,
    ):
        raise VerticalShortCandidateError("vertical candidate resolution must be 1080x1920")
    if abs(float(media.get("fps") or 0.0) - FRAME_RATE) > 0.01:
        raise VerticalShortCandidateError("vertical candidate frame rate must be 30fps")
    if abs(float(media.get("duration_seconds") or 0.0) - expected_duration) > OUTPUT_DURATION_TOLERANCE_SECONDS:
        raise VerticalShortCandidateError("vertical candidate duration changed from authority")
    if result.get("full_decode", {}).get("status") != "passed":
        raise VerticalShortCandidateError("vertical candidate full decode did not pass")
    final_audio = result.get("audio", {}).get("output_measurement", {})
    if float(final_audio.get("integrated_lufs") or -999.0) < -15.5:
        raise VerticalShortCandidateError("vertical candidate audio remained materially below target")
    if float(final_audio.get("integrated_lufs") or 999.0) > -12.5:
        raise VerticalShortCandidateError("vertical candidate audio exceeded loudness window")
    if float(final_audio.get("true_peak_dbtp") or 999.0) > -1.0:
        raise VerticalShortCandidateError("vertical candidate true peak exceeds -1 dBTP")


def validate_vertical_render_result(
    result: dict[str, Any],
    *,
    video_path: Path,
    expected_duration: float,
) -> None:
    """Shared media/decode/audio validation for vertical review candidates."""

    _validate_render_result(
        result,
        video_path=video_path,
        expected_duration=expected_duration,
    )


def _validate_staged_bundle(stage: Path, readback: dict[str, Any]) -> None:
    required = (
        stage / "assets" / "vertical_short_candidate.mp4",
        stage / "vertical_short_subtitles.ass",
        stage / "vertical_short_subtitles.srt",
        stage / "reframe_plan.json",
        stage / "candidate_readback.json",
        stage / "assets" / "reframe_comparison_contact_sheet.jpg",
        stage / "assets" / "frame_qa_contact_sheet.jpg",
        stage / "index.html",
        stage / "open_preview.ps1",
        stage / "serve_preview.ps1",
    )
    for path in required:
        _require_file(path, f"staged bundle file {path.name}")
    if (stage / ".work").exists():
        raise VerticalShortCandidateError("internal work directory remained in staged bundle")
    parsed = _read_json(stage / "candidate_readback.json", "staged candidate readback")
    if parsed.get("artifact_id") != readback.get("artifact_id"):
        raise VerticalShortCandidateError("staged candidate readback does not parse consistently")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count("<video ") != 1:
        raise VerticalShortCandidateError("review page must contain exactly one video")


def _atomic_promote(stage: Path, output: Path) -> Path | None:
    review_dir = output.parent
    _require_within(stage, review_dir, "staging directory")
    if stage.parent != review_dir or not stage.name.startswith(f".{output.name}.staging-"):
        raise VerticalShortCandidateError("invalid staging directory for atomic promotion")
    backup: Path | None = None
    if output.exists():
        backup = review_dir / f".{output.name}.backup-{uuid.uuid4().hex}"
        output.replace(backup)
    try:
        stage.replace(output)
    except Exception:
        if backup is not None and backup.exists() and not output.exists():
            backup.replace(output)
        raise
    return backup


def _protected_paths(episode: Path) -> dict[str, Path]:
    review = episode / "review"
    paths = {
        "human_preview_session": review / "jp_pilot01r3_cut_review" / "human_preview_session",
        "out03_real_local_selected_cut_proof": review / "out03_real_local_selected_cut_proof",
        "out04_editorial_representative_sequence": review / "out04_editorial_representative_sequence",
    }
    for label, path in paths.items():
        _require_directory(path, f"protected {label}")
    return paths


def _tree_digest(path: Path, *, root: Path) -> dict[str, Any]:
    rows: list[str] = []
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = file_path.relative_to(path).as_posix()
        rows.append(f"{relative}\t{_sha256(file_path)}")
    digest = hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()
    return {"path": _relative(path, root), "file_count": len(rows), "sha256": digest, "unchanged": True}


def _validate_predecessor_subtitle_ranges(
    subtitles: list[dict[str, Any]], timeline: list[dict[str, Any]]
) -> None:
    cut_ranges = {
        str(item["id"]): (
            float(item["sequence_start_seconds"]),
            float(item["sequence_end_seconds"]),
        )
        for item in timeline
    }
    for item in subtitles:
        cut_id = str(item.get("cut_id") or "")
        if cut_id not in cut_ranges:
            raise VerticalShortCandidateError("subtitle refers to an unexpected cut")
        start = float(item.get("sequence_start_seconds") or 0.0)
        end = float(item.get("sequence_end_seconds") or 0.0)
        cut_start, cut_end = cut_ranges[cut_id]
        if start < cut_start - 0.001 or end > cut_end + 0.001 or end <= start:
            raise VerticalShortCandidateError(f"predecessor subtitle crosses its cut: {item.get('id')}")


def _subtitle_semantic_hash(subtitles: list[dict[str, Any]]) -> str:
    rows = [
        f"{item.get('id')}|{float(item.get('sequence_start_seconds')):.3f}|"
        f"{float(item.get('sequence_end_seconds')):.3f}|{item.get('text')}"
        for item in subtitles
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if output.parent != review:
        raise VerticalShortCandidateError("output directory must be a direct episode/review child")
    if not output.name.startswith(OUTPUT_NAME_PREFIX):
        raise VerticalShortCandidateError("output directory name must start with out05_")
    _safe_identifier(output.name, "output directory name")


def _validate_predecessor_path(episode: Path, path: Path) -> None:
    expected_parent = (episode / "review" / "out04_editorial_representative_sequence").resolve()
    if path.parent != expected_parent or path.name != "sequence_readback.json":
        raise VerticalShortCandidateError("predecessor must be the retained OUT-04 sequence readback")


def _reject_overlap(output: Path, input_path: Path, message: str) -> None:
    output_resolved = output.resolve()
    input_resolved = input_path.resolve()
    if _is_relative_to(output_resolved, input_resolved) or _is_relative_to(input_resolved, output_resolved):
        raise VerticalShortCandidateError(message)


def _cleanup_internal_directory(path: Path, *, expected_parent: Path) -> None:
    resolved = path.resolve()
    parent = expected_parent.resolve()
    if resolved.parent != parent:
        raise VerticalShortCandidateError("refused cleanup outside expected parent")
    if not (resolved.name.startswith(".") or resolved.name == ".work"):
        raise VerticalShortCandidateError("refused cleanup of non-internal directory")
    shutil.rmtree(resolved)


def _render_html(readback: dict[str, Any]) -> str:
    render = readback["render"]
    media = render["media"]
    audio = readback["audio"]
    output_audio = audio["output_measurement"]
    questions = "".join(f"<li>{escape(question)}</li>" for question in readback["review_questions"])
    subtitle_rows = "".join(
        "<tr>"
        f"<td><code>{escape(item['subtitle_id'])}</code></td>"
        f"<td>{item['display_start_seconds']:.3f}–{item['display_end_seconds']:.3f}s</td>"
        f"<td>{'<br>'.join(escape(line) for line in item.get('wrapped_lines') or [])}</td>"
        "</tr>"
        for item in readback["subtitle"]["items"]
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-05 縦型ショート内部候補</title>
<style>
:root {{ color-scheme:dark; font-family:"Yu Gothic UI","Noto Sans JP",sans-serif; background:#07111f; color:#eef6ff; }}
* {{ box-sizing:border-box; }} body {{ margin:0; overflow-x:hidden; }} main {{ width:min(980px,100%); margin:auto; padding:22px; overflow-wrap:anywhere; }}
.eyebrow {{ color:#67e8f9; font-weight:800; letter-spacing:.12em; }} h1 {{ margin:.35rem 0 .4rem; font-size:clamp(1.55rem,4vw,2.45rem); }}
.lead {{ color:#cbd5e1; max-width:72ch; }} .video-wrap {{ display:flex; justify-content:center; margin:18px 0 24px; }}
video {{ display:block; width:auto; height:min(78vh,820px); max-width:100%; max-height:78vh; aspect-ratio:9/16; background:#000; border:1px solid #334155; border-radius:14px; }}
section,details {{ margin-top:20px; padding:16px; border:1px solid #334155; border-radius:11px; background:#0f1b2d; }}
summary {{ cursor:pointer; font-weight:800; }} img {{ display:block; width:100%; height:auto; margin-top:14px; border-radius:9px; }}
table {{ width:100%; border-collapse:collapse; font-size:.92rem; }} th,td {{ padding:8px; text-align:left; vertical-align:top; border-bottom:1px solid #334155; }}
code {{ color:#bae6fd; }} .gate {{ color:#fbbf24; }} li {{ margin:.55rem 0; }}
@media(max-width:620px) {{ main {{ padding:14px; }} video {{ height:min(74vh,720px); }} th:first-child,td:first-child {{ display:none; }} }}
</style></head><body><main>
<div class="eyebrow">OUT-05 · INTERNAL VERTICAL CANDIDATE</div>
<h1>縦型ショート候補を一本で確認</h1>
<p class="lead">OUT-04で受け入れたカット順と境界を変えず、全画面情報を残す縦型フレーム、字幕、音声だけを確認する内部候補です。</p>
<div class="video-wrap"><video controls preload="metadata" playsinline src="assets/vertical_short_candidate.mp4"></video></div>
<section><h2>今回の確認</h2><ol>{questions}</ol></section>
<details><summary>リフレーム比較とフレーム確認</summary>
<p>左から明示アンカークロップ、採用した全体fit＋同一ソース背景、bounded hybrid。上段はcut_001、下段はcut_002です。</p>
<img src="assets/reframe_comparison_contact_sheet.jpg" alt="3方式のリフレーム静止画比較">
<p>開始、境界前、境界後、密な字幕、終端の順です。</p>
<img src="assets/frame_qa_contact_sheet.jpg" alt="縦型候補の5点フレーム確認">
</details>
<details><summary>字幕の改行と安全域</summary><table><thead><tr><th>ID</th><th>時間</th><th>表示</th></tr></thead><tbody>{subtitle_rows}</tbody></table></details>
<details><summary>probe・音声・出典</summary>
<p>Video: <code>{escape(str(media['video_codec']))}</code> / {media['width']}x{media['height']} / {media['fps']}fps / {media['duration_seconds']:.3f}s / yuv420p / faststart</p>
<p>Audio: <code>{escape(str(media['audio_codec']))}</code>; input {audio['input_measurement']['integrated_lufs']:.2f} LUFS / {audio['input_measurement']['true_peak_dbtp']:.2f} dBTP; output {output_audio['integrated_lufs']:.2f} LUFS / {output_audio['true_peak_dbtp']:.2f} dBTP.</p>
<p>OUT-04 SHA-256: <code>{escape(readback['predecessor']['video_sha256'])}</code></p>
</details>
<details><summary>閉じたゲート</summary><p class="gate">internal_review_only=true / vertical_format_candidate=true / production_candidate=false / production_acceptance=false / production_subtitle_design_acceptance=false / rights=pending / public_ready=false / publishing=false / publish_attempted=false</p></details>
</main></body></html>"""


def _open_script() -> str:
    return """param([switch]$Serve, [int]$Port = 8000)
$ErrorActionPreference = 'Stop'
if ($Serve) {
    & (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
    exit $LASTEXITCODE
}
$index = Join-Path $PSScriptRoot 'index.html'
Write-Host "OUT-05 review entrypoint: $index"
Start-Process -FilePath $index
Write-Host "If local-file playback is blocked, rerun this command with -Serve."
"""


def _serve_script() -> str:
    return """param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
Write-Host "OUT-05 review URL: $url"
Start-Process -FilePath $url
Push-Location $PSScriptRoot
try {
    uvx python -m http.server $Port --bind 127.0.0.1
} finally {
    Pop-Location
}
"""


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return _read_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise VerticalShortCandidateError(f"invalid {label}: {exc}") from exc


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise VerticalShortCandidateError(f"{label} is missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise VerticalShortCandidateError(f"{label} is missing: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    if not _is_relative_to(path.resolve(), parent.resolve()):
        raise VerticalShortCandidateError(f"{label} must stay inside {parent}")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _safe_identifier(value: str, label: str) -> None:
    if not value or SAFE_IDENTIFIER.fullmatch(value) is None:
        raise VerticalShortCandidateError(f"unsafe {label}: {value!r}")


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _powershell_command(path: Path, root: Path) -> str:
    relative = _relative(path, root).replace("/", "\\")
    return f"powershell -ExecutionPolicy Bypass -File {relative}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _assert_close(value: Any, expected: float, label: str, tolerance: float = 0.001) -> None:
    try:
        actual = float(value)
    except (TypeError, ValueError) as exc:
        raise VerticalShortCandidateError(f"{label} is not numeric") from exc
    if abs(actual - expected) > tolerance:
        raise VerticalShortCandidateError(f"{label} changed: expected {expected:.3f}, got {actual:.3f}")


def _srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    sec = total_seconds % 60
    total_minutes = total_seconds // 60
    minute = total_minutes % 60
    hour = total_minutes // 60
    return f"{hour:02d}:{minute:02d}:{sec:02d},{ms:03d}"
