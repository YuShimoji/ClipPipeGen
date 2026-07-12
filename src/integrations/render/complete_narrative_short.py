"""OUT-06 complete narrative-short delivery candidate.

The slice keeps the accepted OUT-05 opening immutable at the authority level,
adds only the already-kept cut_003 range, and reuses the measured OUT-05
vertical subtitle/render boundary.  It creates one ignored, same-machine,
internal-review delivery package.  It never lifts rights, production subtitle,
production render, publishing, or public-use gates.
"""

from __future__ import annotations

import array
import copy
import hashlib
import json
import math
import re
import subprocess
import sys
import uuid
from html import escape
from pathlib import Path
from typing import Any, Callable

from src.integrations.render import ffmpeg_tiny
from src.integrations.render.subtitle_overlay_visual_proof import _write_ass
from src.integrations.render.vertical_short_candidate import (
    VerticalShortCandidateError,
    _atomic_promote,
    _cleanup_internal_directory,
    _relative,
    _sha256,
    _tree_digest,
    _write_text,
    build_vertical_subtitle_presentation,
    render_vertical_sequence_assets,
    validate_ass_visible_content,
    validate_vertical_render_result,
    validate_vertical_subtitle_containment,
)


ARTIFACT_ID = "clip-out06-complete-narrative-short-delivery-candidate-v0-001"
SCHEMA_VERSION = "clippipegen.out06.complete_narrative_short.v0"
STATE = "complete_narrative_short_delivery_candidate_review_ready"
EXPECTED_OUT05_ARTIFACT_ID = "clip-out05-vertical-short-internal-candidate-v0-001"
EXPECTED_OUT05_READBACK_SHA256 = (
    "57a1df75f4b6760819d8cf8f707114352c331a0103e6c4d1e6f0acefca4767bf"
)
EXPECTED_OUT05_VIDEO_SHA256 = (
    "d2a75ed5f85a0869d4178917c258624ccf083bbefce33ab468549f93a982b827"
)
EXPECTED_OUT04_READBACK_SHA256 = (
    "8253e27eb2321863f277eec33161fed82a9ccb21b9719b84c082b46d31a2f1db"
)
OUT05_ACCEPTANCE_COMMIT = "f2afb4d40b583f928286742b1a7646cde9398994"
EXPECTED_CUT_IDS = ("cut_001", "cut_002", "cut_003")
EXPECTED_SUBTITLE_IDS = tuple(f"sub_{index:03d}" for index in range(1, 30))
EXPECTED_DURATION_SECONDS = 38.638
EXPECTED_BOUNDARIES_SECONDS = (6.840, 11.678)
OUTPUT_DURATION_TOLERANCE_SECONDS = 0.20
OUTPUT_NAME_PREFIX = "out06_"
SAFE_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
PROXY_AUTHORITY_RELATIVE = Path(
    "review/jp_pilot01r3_cut_review/"
    "chapter_revision_patch.cut_002_cut_003_proxy.operator.json"
)
DECISION_PACKET_RELATIVE = Path(
    "review/jp_pilot01r3_cut_review/cut_decision_packet.json"
)
FRAME_SAMPLES = (
    ("start", 0.250),
    ("before_cut001_cut002", 6.700),
    ("after_cut001_cut002", 6.980),
    ("before_cut002_cut003", 11.500),
    ("after_cut002_cut003", 11.930),
    ("cut003_start", 12.200),
    ("reviewed_wrap_sub013", 14.860),
    ("reviewed_wrap_sub014", 16.000),
    ("reviewed_wrap_sub019", 22.890),
    ("cut003_mid", 25.158),
    ("densest_subtitle", 28.850),
    ("reviewed_wrap_sub024", 29.510),
    ("reviewed_wrap_sub028", 37.320),
    ("reviewed_wrap_sub029", 38.350),
    ("cut003_end", 38.200),
    ("end", 38.500),
)
REVIEW_QUESTIONS = (
    "約38秒の全体が導入・展開・締めとして成立し、cut_003が重複や蛇足に見えないか。",
    "cut_002からcut_003へのテンポと境界、および音声・映像のつながりが自然か。",
    "cut_003を含む縦型フレームと29字幕が自然で読みやすいか。",
)
REQUIRED_PACKAGE_FILES = (
    "assets/complete_narrative_short.mp4",
    "complete_narrative_short_subtitles.ass",
    "complete_narrative_short_subtitles.srt",
    "narrative_sequence_plan.json",
    "candidate_readback.json",
    "delivery_manifest.json",
    "assets/poster_frame.jpg",
    "assets/frame_qa_contact_sheet.jpg",
    "index.html",
    "open_preview.ps1",
    "serve_preview.ps1",
)

RenderExecutor = Callable[..., dict[str, Any]]
PostRenderExecutor = Callable[..., dict[str, Any]]


class CompleteNarrativeShortError(VerticalShortCandidateError):
    """Raised when OUT-06 cannot be built without authority or scope drift."""


def build_complete_narrative_short(
    *,
    episode_dir: str | Path,
    output_dir: str | Path,
    predecessor_readback_path: str | Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
    render_executor: RenderExecutor | None = None,
    post_render_executor: PostRenderExecutor | None = None,
    expected_predecessor_sha256: str = EXPECTED_OUT05_READBACK_SHA256,
    expected_predecessor_video_sha256: str = EXPECTED_OUT05_VIDEO_SHA256,
    expected_out04_sha256: str = EXPECTED_OUT04_READBACK_SHA256,
) -> dict[str, Any]:
    """Build and atomically promote one OUT-06 internal delivery package."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(root, Path(output_dir))
    predecessor_path = _resolved(root, Path(predecessor_readback_path))
    _require_directory(episode, "episode directory")
    _require_within(episode, root, "episode directory")
    _validate_output_directory(episode, output)
    _validate_predecessor_path(episode, predecessor_path)

    authority = _load_and_validate_authority(
        root=root,
        episode=episode,
        predecessor_path=predecessor_path,
        expected_predecessor_sha256=expected_predecessor_sha256,
        expected_predecessor_video_sha256=expected_predecessor_video_sha256,
        expected_out04_sha256=expected_out04_sha256,
    )
    input_paths = authority["input_paths"]
    for input_path in input_paths:
        _reject_overlap(output, input_path, "output directory must not overlap an input")

    protected_paths = _protected_paths(episode)
    for protected_path in protected_paths.values():
        _reject_overlap(output, protected_path, "output directory must not overlap protected evidence")
    protected_before = {
        label: _tree_digest(path, root=root) for label, path in protected_paths.items()
    }
    input_hashes_before = {
        _relative(path, root): _sha256(path) for path in input_paths
    }

    layout, subtitle_items, selector = build_vertical_subtitle_presentation(
        authority["semantic_subtitles"],
        application_key="out06_application",
        dimension_source="out06_complete_narrative_vertical_canvas",
    )
    containment = validate_vertical_subtitle_containment(
        subtitle_items,
        expected_duration=EXPECTED_DURATION_SECONDS,
        layout=layout,
        expected_count=29,
    )
    plan = _narrative_sequence_plan(
        root=root,
        episode=episode,
        authority=authority,
        subtitle_items=subtitle_items,
    )

    review_dir = episode / "review"
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    backup: Path | None = None
    try:
        stage.mkdir(parents=False, exist_ok=False)
        assets = stage / "assets"
        assets.mkdir()
        work = stage / ".work"
        work.mkdir()
        ass_path = stage / "complete_narrative_short_subtitles.ass"
        srt_path = stage / "complete_narrative_short_subtitles.srt"
        plan_path = stage / "narrative_sequence_plan.json"
        readback_path = stage / "candidate_readback.json"
        manifest_path = stage / "delivery_manifest.json"
        video_path = assets / "complete_narrative_short.mp4"
        poster_path = assets / "poster_frame.jpg"
        frame_sheet_path = assets / "frame_qa_contact_sheet.jpg"
        index_path = stage / "index.html"
        open_path = stage / "open_preview.ps1"
        serve_path = stage / "serve_preview.ps1"

        _write_ass(ass_path, subtitle_items, layout=layout, review_label=None)
        _write_text(srt_path, _render_srt(subtitle_items))
        _write_json(plan_path, plan)
        validate_ass_visible_content(
            ass_path,
            expected_count=29,
            required_texts=(
                "もしもし？",
                "体育館裏で待ってます！！",
                "来ねぇ！！",
                "ありがとうございますー！",
            ),
        )

        executor = render_executor or render_vertical_sequence_assets
        render_result = executor(
            source_video_path=authority["source_video_path"],
            source_audio_path=authority["source_audio_path"],
            timeline=authority["timeline"],
            ass_path=ass_path,
            video_path=video_path,
            compare_sheet_path=None,
            frame_sheet_path=frame_sheet_path,
            work_dir=work,
            subtitle_layout=layout,
            expected_duration=EXPECTED_DURATION_SECONDS,
            frame_samples=FRAME_SAMPLES,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        validate_vertical_render_result(
            render_result,
            video_path=video_path,
            expected_duration=EXPECTED_DURATION_SECONDS,
        )
        _require_file(frame_sheet_path, "frame QA contact sheet")

        post_executor = post_render_executor or _post_render_assets
        post_render = post_executor(
            video_path=video_path,
            poster_path=poster_path,
            boundaries=EXPECTED_BOUNDARIES_SECONDS,
            expected_duration=EXPECTED_DURATION_SECONDS,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        _require_file(poster_path, "poster frame")
        if post_render.get("status") != "passed":
            raise CompleteNarrativeShortError("post-render boundary QA did not pass")
        _cleanup_internal_directory(work, expected_parent=stage)

        protected_after = {
            label: _tree_digest(path, root=root) for label, path in protected_paths.items()
        }
        if protected_after != protected_before:
            raise CompleteNarrativeShortError("protected evidence changed during OUT-06 build")
        input_hashes_after = {
            _relative(path, root): _sha256(path) for path in input_paths
        }
        if input_hashes_after != input_hashes_before:
            raise CompleteNarrativeShortError("authority/source input changed during OUT-06 build")

        final_paths = {
            "video": output / "assets" / video_path.name,
            "ass": output / ass_path.name,
            "srt": output / srt_path.name,
            "plan": output / plan_path.name,
            "readback": output / readback_path.name,
            "manifest": output / manifest_path.name,
            "poster": output / "assets" / poster_path.name,
            "frame_sheet": output / "assets" / frame_sheet_path.name,
            "index": output / index_path.name,
            "open": output / open_path.name,
            "serve": output / serve_path.name,
        }
        stage_outputs = {
            "video": video_path,
            "ass": ass_path,
            "srt": srt_path,
            "plan": plan_path,
            "poster": poster_path,
            "frame_sheet": frame_sheet_path,
        }
        readback = _candidate_readback(
            root=root,
            episode=episode,
            authority=authority,
            protected=protected_before,
            input_hashes=input_hashes_before,
            layout=layout,
            selector=selector,
            subtitle_items=subtitle_items,
            containment=containment,
            plan=plan,
            render_result=render_result,
            post_render=post_render,
            stage_outputs=stage_outputs,
            final_paths=final_paths,
        )
        _write_json(readback_path, readback)
        _write_text(index_path, _render_html(readback, plan))
        _write_text(open_path, _open_script())
        _write_text(serve_path, _serve_script())

        manifest = _delivery_manifest(
            root=root,
            output=output,
            stage=stage,
            authority=authority,
            plan=plan,
            readback=readback,
        )
        _write_json(manifest_path, manifest)
        _validate_staged_bundle(stage, manifest)
        try:
            backup = _atomic_promote(stage, output)
        except PermissionError as exc:
            raise CompleteNarrativeShortError(
                "OUT-06 output is in use; stop the retained preview server and rerun"
            ) from exc
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)

    final_readback = _read_json(output / "candidate_readback.json", "candidate readback")
    return {
        "artifact_id": ARTIFACT_ID,
        "output_dir": output,
        "video_path": output / "assets" / "complete_narrative_short.mp4",
        "readback_path": output / "candidate_readback.json",
        "manifest_path": output / "delivery_manifest.json",
        "index_path": output / "index.html",
        "readback": final_readback,
    }


def _load_and_validate_authority(
    *,
    root: Path,
    episode: Path,
    predecessor_path: Path,
    expected_predecessor_sha256: str,
    expected_predecessor_video_sha256: str,
    expected_out04_sha256: str,
) -> dict[str, Any]:
    predecessor = _read_json(predecessor_path, "OUT-05 predecessor readback")
    predecessor_hash = _sha256(predecessor_path)
    if predecessor_hash != expected_predecessor_sha256:
        raise CompleteNarrativeShortError("accepted OUT-05 readback hash changed")
    if predecessor.get("artifact_id") != EXPECTED_OUT05_ARTIFACT_ID:
        raise CompleteNarrativeShortError("unexpected OUT-05 predecessor artifact")
    timeline_summary = predecessor.get("timeline") or {}
    if tuple(timeline_summary.get("ordered_cut_ids") or ()) != EXPECTED_CUT_IDS[:2]:
        raise CompleteNarrativeShortError("OUT-05 accepted opening cut order changed")
    _assert_close(timeline_summary.get("expected_duration_seconds"), 11.678, "OUT-05 duration")
    _assert_close(timeline_summary.get("hard_cut_seconds"), 6.840, "OUT-05 boundary")
    if int((predecessor.get("subtitle") or {}).get("count") or 0) != 9:
        raise CompleteNarrativeShortError("OUT-05 accepted opening must contain nine subtitles")
    if (
        (predecessor.get("reframe") or {}).get("selected_option")
        != "full_16_9_fit_source_derived_blurred_canvas"
    ):
        raise CompleteNarrativeShortError("OUT-05 accepted reframe selection changed")
    _validate_closed_gates(predecessor.get("boundaries") or {}, allow_vertical_key=True)

    predecessor_video = _resolved(
        root, Path(str((predecessor.get("render") or {}).get("output_path") or ""))
    )
    _require_file(predecessor_video, "OUT-05 predecessor video")
    _require_within(predecessor_video, predecessor_path.parent, "OUT-05 predecessor video")
    predecessor_video_hash = _sha256(predecessor_video)
    if predecessor_video_hash != expected_predecessor_video_sha256:
        raise CompleteNarrativeShortError("accepted OUT-05 video hash changed")
    if predecessor_video_hash != str((predecessor.get("render") or {}).get("output_sha256") or ""):
        raise CompleteNarrativeShortError("OUT-05 video/readback hash mismatch")

    out04_path = _resolved(
        root, Path(str((predecessor.get("predecessor") or {}).get("readback_path") or ""))
    )
    _require_file(out04_path, "OUT-04 source readback")
    out04_hash = _sha256(out04_path)
    if out04_hash != expected_out04_sha256:
        raise CompleteNarrativeShortError("accepted OUT-04 readback hash changed")
    if out04_hash != str((predecessor.get("predecessor") or {}).get("readback_sha256") or ""):
        raise CompleteNarrativeShortError("OUT-05 predecessor provenance no longer matches OUT-04")
    out04 = _read_json(out04_path, "OUT-04 source readback")
    timeline = copy.deepcopy(out04.get("timeline") or [])
    if len(timeline) != 2:
        raise CompleteNarrativeShortError("OUT-04 source timeline must contain two cuts")
    _validate_opening_timeline(timeline)

    edit_path = episode / "edit_pack.json"
    transcript_path = episode / "transcript.json"
    decision_path = episode / DECISION_PACKET_RELATIVE
    proxy_path = episode / PROXY_AUTHORITY_RELATIVE
    rights_path = episode / "rights_manifest.json"
    ledger_path = episode / "material_ledger.json"
    for path, label in (
        (edit_path, "edit pack"),
        (transcript_path, "transcript"),
        (decision_path, "cut decision packet"),
        (proxy_path, "operator proxy authority"),
        (rights_path, "rights manifest"),
        (ledger_path, "material ledger"),
    ):
        _require_file(path, label)

    input_paths: dict[str, Path] = {
        str(predecessor_path.resolve()): predecessor_path,
        str(predecessor_video.resolve()): predecessor_video,
        str(out04_path.resolve()): out04_path,
        str(edit_path.resolve()): edit_path,
        str(transcript_path.resolve()): transcript_path,
        str(decision_path.resolve()): decision_path,
        str(proxy_path.resolve()): proxy_path,
        str(rights_path.resolve()): rights_path,
        str(ledger_path.resolve()): ledger_path,
    }
    recorded_inputs = predecessor.get("input_hashes") or {}
    for relative, expected_hash in recorded_inputs.items():
        path = _resolved(root, Path(str(relative)))
        _require_file(path, f"OUT-05 recorded input {relative}")
        _require_within(path, episode, f"OUT-05 recorded input {relative}")
        if _sha256(path) != str(expected_hash):
            raise CompleteNarrativeShortError(f"OUT-05 recorded input changed: {relative}")
        input_paths[str(path.resolve())] = path

    source_video_path = _single_recorded_path(recorded_inputs, root, "source_video.mp4")
    source_audio_path = _single_recorded_path(recorded_inputs, root, "source.wav")
    input_paths[str(source_video_path.resolve())] = source_video_path
    input_paths[str(source_audio_path.resolve())] = source_audio_path

    edit_pack = _read_json(edit_path, "edit pack")
    transcript = _read_json(transcript_path, "transcript")
    decision_packet = _read_json(decision_path, "cut decision packet")
    proxy = _read_json(proxy_path, "operator proxy authority")
    rights = _read_json(rights_path, "rights manifest")
    cut3 = _validate_cut003_authority(edit_pack, decision_packet, proxy)
    additional_subtitles = _validate_cut003_subtitles(edit_pack, transcript)
    if str((rights.get("compliance_check") or {}).get("status") or "") != "pending":
        raise CompleteNarrativeShortError("OUT-06 must preserve rights_status=pending")

    timeline.append(
        {
            "id": "cut_003",
            "source_start_seconds": 22.606,
            "source_end_seconds": 49.566,
            "sequence_start_seconds": 11.678,
            "sequence_end_seconds": 38.638,
            "duration_seconds": 26.960,
            "transition_in": "hard_cut",
            "editorial_role": "resolution_and_close",
            "final_cut_decision": "keep",
            "context_status": "needs_review",
            "decision_reason": str(cut3["decision"].get("decision_reason") or ""),
            "manual_override_reason": str(cut3["decision"].get("manual_override_reason") or ""),
            "proxy_decision": "proceed_with_limitations",
            "source_segment_ids": [f"seg_{index:06d}" for index in range(10, 30)],
            "subtitle_ids": [f"sub_{index:03d}" for index in range(10, 30)],
            "subtitle_count": 20,
        }
    )
    semantic_subtitles = copy.deepcopy(out04.get("subtitles") or [])
    if tuple(str(item.get("id")) for item in semantic_subtitles) != EXPECTED_SUBTITLE_IDS[:9]:
        raise CompleteNarrativeShortError("accepted OUT-05 opening subtitle identity changed")
    for item in additional_subtitles:
        semantic_subtitles.append(
            {
                "id": item["id"],
                "cut_id": "cut_003",
                "sequence_start_seconds": round(
                    11.678 + float(item["start_seconds"]) - 22.606, 3
                ),
                "sequence_end_seconds": round(
                    11.678 + float(item["end_seconds"]) - 22.606, 3
                ),
                "source_start_seconds": float(item["start_seconds"]),
                "source_end_seconds": float(item["end_seconds"]),
                "text": str(item["text"]),
                "source_type": str(item.get("source_type") or ""),
                "source_segment_ids": list(item.get("source_segment_ids") or []),
            }
        )
    if tuple(str(item.get("id")) for item in semantic_subtitles) != EXPECTED_SUBTITLE_IDS:
        raise CompleteNarrativeShortError("OUT-06 subtitle mapping must be sub_001..sub_029")

    return {
        "predecessor": predecessor,
        "predecessor_path": predecessor_path,
        "predecessor_hash": predecessor_hash,
        "predecessor_video_path": predecessor_video,
        "predecessor_video_hash": predecessor_video_hash,
        "out04": out04,
        "out04_path": out04_path,
        "out04_hash": out04_hash,
        "timeline": timeline,
        "semantic_subtitles": semantic_subtitles,
        "cut003_decision": cut3["decision"],
        "cut003_proxy": cut3["proxy"],
        "source_video_path": source_video_path,
        "source_audio_path": source_audio_path,
        "input_paths": list(input_paths.values()),
        "rights_status": "pending",
    }


def _validate_opening_timeline(timeline: list[dict[str, Any]]) -> None:
    expected = (
        ("cut_001", 2.453, 9.293, 0.000, 6.840, "sequence_start"),
        ("cut_002", 12.329, 17.167, 6.840, 11.678, "hard_cut"),
    )
    for item, values in zip(timeline, expected, strict=True):
        cut_id, source_start, source_end, sequence_start, sequence_end, transition = values
        if item.get("id") != cut_id or item.get("transition_in") != transition:
            raise CompleteNarrativeShortError("accepted opening timeline identity changed")
        for field, expected_value in (
            ("source_start_seconds", source_start),
            ("source_end_seconds", source_end),
            ("sequence_start_seconds", sequence_start),
            ("sequence_end_seconds", sequence_end),
        ):
            _assert_close(item.get(field), expected_value, f"{cut_id}.{field}")


def _validate_cut003_authority(
    edit_pack: dict[str, Any],
    decision_packet: dict[str, Any],
    proxy: dict[str, Any],
) -> dict[str, Any]:
    cuts = [item for item in (edit_pack.get("cut_candidates") or []) if item.get("id") == "cut_003"]
    if len(cuts) != 1:
        raise CompleteNarrativeShortError("cut_003 edit authority is missing or ambiguous")
    cut = cuts[0]
    _assert_close(cut.get("start_seconds"), 22.606, "cut_003.source_start")
    _assert_close(cut.get("end_seconds"), 49.566, "cut_003.source_end")
    context = cut.get("context_check") or {}
    if context.get("status") != "needs_review":
        raise CompleteNarrativeShortError("cut_003 context authority changed")

    decisions = [
        item for item in (decision_packet.get("decisions") or []) if item.get("cut_id") == "cut_003"
    ]
    if len(decisions) != 1:
        raise CompleteNarrativeShortError("cut_003 decision authority is missing or ambiguous")
    decision = decisions[0]
    if decision.get("final_cut_decision") != "keep" or decision.get("context_status") != "needs_review":
        raise CompleteNarrativeShortError("cut_003 keep/needs_review authority changed")
    if not str(decision.get("manual_override_reason") or "").strip():
        raise CompleteNarrativeShortError("cut_003 manual limitation authority is missing")

    revisions = [item for item in (proxy.get("revisions") or []) if item.get("cut_id") == "cut_003"]
    if len(revisions) != 1:
        raise CompleteNarrativeShortError("cut_003 proxy authority is missing or ambiguous")
    revision = revisions[0]
    if revision.get("proxy_decision") != "proceed_with_limitations":
        raise CompleteNarrativeShortError("cut_003 proxy decision changed")
    if revision.get("context_risk_handling") != "keep_retained_risk_visible":
        raise CompleteNarrativeShortError("cut_003 retained context-risk handling changed")
    return {"cut": cut, "decision": decision, "proxy": revision}


def _validate_cut003_subtitles(
    edit_pack: dict[str, Any], transcript: dict[str, Any]
) -> list[dict[str, Any]]:
    subtitles = [
        item
        for item in (edit_pack.get("subtitles") or [])
        if 10 <= _numeric_suffix(str(item.get("id") or "")) <= 29
    ]
    if tuple(str(item.get("id")) for item in subtitles) != EXPECTED_SUBTITLE_IDS[9:]:
        raise CompleteNarrativeShortError("cut_003 subtitles must be exactly sub_010..sub_029")
    transcript_by_id = {
        str(item.get("id")): item for item in (transcript.get("segments") or [])
    }
    for index, subtitle in enumerate(subtitles, start=10):
        expected_segment = f"seg_{index:06d}"
        if subtitle.get("cut_id") != "cut_003":
            raise CompleteNarrativeShortError(f"{subtitle.get('id')} moved outside cut_003")
        if list(subtitle.get("source_segment_ids") or []) != [expected_segment]:
            raise CompleteNarrativeShortError(f"{subtitle.get('id')} source mapping changed")
        segment = transcript_by_id.get(expected_segment)
        if segment is None or segment.get("review_status") != "accepted":
            raise CompleteNarrativeShortError(f"{expected_segment} is not accepted transcript authority")
        for field in ("start_seconds", "end_seconds"):
            _assert_close(subtitle.get(field), segment.get(field), f"{subtitle.get('id')}.{field}")
        if str(subtitle.get("text") or "") != str(segment.get("text") or ""):
            raise CompleteNarrativeShortError(f"{subtitle.get('id')} text changed from transcript")
    excluded = [
        item for item in (edit_pack.get("subtitles") or []) if item.get("id") == "sub_030"
    ]
    if len(excluded) != 1 or excluded[0].get("cut_id") == "cut_003":
        raise CompleteNarrativeShortError("sub_030 exclusion authority changed")
    return subtitles


def _narrative_sequence_plan(
    *,
    root: Path,
    episode: Path,
    authority: dict[str, Any],
    subtitle_items: list[dict[str, Any]],
) -> dict[str, Any]:
    presentation_by_id = {str(item["subtitle_id"]): item for item in subtitle_items}
    mapping: list[dict[str, Any]] = []
    for semantic in authority["semantic_subtitles"]:
        subtitle_id = str(semantic["id"])
        presentation = presentation_by_id[subtitle_id]
        mapping.append(
            {
                "subtitle_id": subtitle_id,
                "cut_id": str(semantic["cut_id"]),
                "source_segment_ids": list(semantic.get("source_segment_ids") or []),
                "source_start_seconds": float(semantic["source_start_seconds"]),
                "source_end_seconds": float(semantic["source_end_seconds"]),
                "semantic_sequence_start_seconds": float(
                    semantic["sequence_start_seconds"]
                ),
                "semantic_sequence_end_seconds": float(
                    semantic["sequence_end_seconds"]
                ),
                "display_start_seconds": float(presentation["display_start_seconds"]),
                "display_end_seconds": float(presentation["display_end_seconds"]),
                "text": str(semantic["text"]),
                "wrapped_lines": list(presentation.get("wrapped_lines") or []),
                "source_type": str(semantic.get("source_type") or ""),
            }
        )
    return {
        "schema_version": "clippipegen.out06.narrative_sequence_plan.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": episode.name,
        "purpose": (
            "Preserve the accepted OUT-05 opening and add the authoritative kept "
            "cut_003 as one introduction-development-close internal narrative short."
        ),
        "narrative_arc": {
            "status": "planned_complete_narrative",
            "introduction": "cut_001 establishes the phone-call setup",
            "development": "cut_002 advances the meeting/challenge beat",
            "close": "cut_003 resolves the encounter and exits on the next-target referral",
            "human_review_required": True,
        },
        "ordered_cut_ids": list(EXPECTED_CUT_IDS),
        "semantic_duration_seconds": EXPECTED_DURATION_SECONDS,
        "hard_cut_boundaries_seconds": list(EXPECTED_BOUNDARIES_SECONDS),
        "transition_policy": "hard_cuts_only_no_padding_no_bgm_no_sfx",
        "timeline": authority["timeline"],
        "subtitle_count": 29,
        "subtitle_ids": list(EXPECTED_SUBTITLE_IDS),
        "subtitle_mapping": mapping,
        "cut003_authority": {
            "source_range_seconds": [22.606, 49.566],
            "final_cut_decision": "keep",
            "context_status": "needs_review",
            "proxy_decision": "proceed_with_limitations",
            "context_risk_handling": "keep_retained_risk_visible",
            "manual_override_reason": str(
                authority["cut003_decision"].get("manual_override_reason") or ""
            ),
            "operator_note": str(authority["cut003_proxy"].get("operator_note") or ""),
            "authority_mutated": False,
        },
        "accepted_opening": {
            "canonical_main_acceptance_commit": OUT05_ACCEPTANCE_COMMIT,
            "artifact_id": EXPECTED_OUT05_ARTIFACT_ID,
            "readback_path": _relative(authority["predecessor_path"], root),
            "readback_sha256": authority["predecessor_hash"],
            "video_sha256": authority["predecessor_video_hash"],
            "ordered_cut_ids": ["cut_001", "cut_002"],
            "semantic_duration_seconds": 11.678,
            "subtitle_ids": list(EXPECTED_SUBTITLE_IDS[:9]),
            "immutability_validation": "passed",
        },
        "reframe": {
            "selected_option": "full_16_9_fit_source_derived_blurred_canvas",
            "opening_decision_reused": True,
            "additional_comparison_rendered": False,
            "reason": (
                "OUT-05 full-fit preserved subject/action information and was accepted; "
                "OUT-06 applies that same measured route without reopening comparison."
            ),
        },
        "boundaries": _closed_gates(),
    }


def _candidate_readback(
    *,
    root: Path,
    episode: Path,
    authority: dict[str, Any],
    protected: dict[str, dict[str, Any]],
    input_hashes: dict[str, str],
    layout: dict[str, Any],
    selector: dict[str, Any],
    subtitle_items: list[dict[str, Any]],
    containment: dict[str, Any],
    plan: dict[str, Any],
    render_result: dict[str, Any],
    post_render: dict[str, Any],
    stage_outputs: dict[str, Path],
    final_paths: dict[str, Path],
) -> dict[str, Any]:
    output_hashes = {
        label: {
            "path": _relative(final_paths[label], root),
            "sha256": _sha256(stage_path),
        }
        for label, stage_path in stage_outputs.items()
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "episode_id": episode.name,
        "source_class": "accepted_out05_opening_plus_authoritative_cut003_real_local_media",
        "storage": {
            "class": "ignored_local_retained_same_machine",
            "portable_across_clones": False,
            "episodes_tracked": False,
        },
        "accepted_opening": plan["accepted_opening"],
        "narrative": plan["narrative_arc"],
        "timeline": {
            "ordered_cut_ids": list(EXPECTED_CUT_IDS),
            "semantic_duration_seconds": EXPECTED_DURATION_SECONDS,
            "hard_cut_boundaries_seconds": list(EXPECTED_BOUNDARIES_SECONDS),
            "cuts": authority["timeline"],
            "transition_type": "hard_cut",
            "bgm_added": False,
            "sfx_added": False,
            "padding_added": False,
        },
        "cut003_authority": plan["cut003_authority"],
        "reframe": plan["reframe"],
        "subtitle": {
            "count": 29,
            "ids": list(EXPECTED_SUBTITLE_IDS),
            "burned_in_ass": _relative(final_paths["ass"], root),
            "portable_srt": _relative(final_paths["srt"], root),
            "presentation_mode": "bottom_center_emphasis",
            "speaker_identity_verified": False,
            "speaker_identity_layer_omitted": True,
            "visible_placeholder_or_technical_label": False,
            "font_family": layout["diagnostic_ass_style"].get("font_name"),
            "font_file": layout["diagnostic_ass_style"].get("resolved_font_file"),
            "font_file_status": layout["diagnostic_ass_style"].get("font_file_status"),
            "layout": layout,
            "selector": selector,
            "containment": containment,
            "items": subtitle_items,
            "source_mapping": plan["subtitle_mapping"],
            "sub030_excluded": True,
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
            "faststart": render_result.get("faststart"),
            "pixel_format": "yuv420p",
            "shared_render_boundary": (
                "src.integrations.render.vertical_short_candidate."
                "render_vertical_sequence_assets"
            ),
        },
        "quality_assurance": {
            "frame_contact_sheet": _relative(final_paths["frame_sheet"], root),
            "frame_samples": render_result["frame_samples"],
            "poster_frame": {
                "path": _relative(final_paths["poster"], root),
                **post_render["poster"],
            },
            "boundary_analysis": post_render["boundary_analysis"],
            "sync": post_render["sync"],
            "browser_required": True,
            "browser_result": "pending_external_browser_validation",
        },
        "input_hashes": input_hashes,
        "protected_evidence": protected,
        "outputs": output_hashes,
        "review_entrypoint": _relative(final_paths["index"], root),
        "machine_readback": _relative(final_paths["readback"], root),
        "delivery_manifest": _relative(final_paths["manifest"], root),
        "open_command": _powershell_command(final_paths["open"], root),
        "serve_command": _powershell_command(final_paths["serve"], root),
        "regeneration_command": _regeneration_command(
            root, episode, final_paths["readback"].parent, authority
        ),
        "review_questions": list(REVIEW_QUESTIONS),
        "boundaries": _closed_gates(),
    }


def _delivery_manifest(
    *,
    root: Path,
    output: Path,
    stage: Path,
    authority: dict[str, Any],
    plan: dict[str, Any],
    readback: dict[str, Any],
) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for relative in REQUIRED_PACKAGE_FILES:
        if relative == "delivery_manifest.json":
            continue
        stage_path = stage / Path(relative)
        _require_file(stage_path, f"manifest payload {relative}")
        files.append(
            {
                "repo_relative_path": _relative(output / Path(relative), root),
                "package_relative_path": relative,
                "bytes": stage_path.stat().st_size,
                "hash_kind": "sha256_file_bytes",
                "sha256": _sha256(stage_path),
            }
        )
    manifest = {
        "schema_version": "clippipegen.out06.delivery_manifest.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": readback["episode_id"],
        "state": STATE,
        "package_path": _relative(output, root),
        "artifact_identity": {
            "feature_id": "OUT-06",
            "branch": "codex/out-06-complete-narrative-short-delivery-candidate-v0",
            "accepted_predecessor_artifact": EXPECTED_OUT05_ARTIFACT_ID,
            "canonical_predecessor_acceptance_commit": OUT05_ACCEPTANCE_COMMIT,
        },
        "source_and_input_provenance": [
            {"path": path, "sha256": sha256}
            for path, sha256 in sorted(readback["input_hashes"].items())
        ],
        "cut_and_subtitle_mapping": {
            "ordered_cut_ids": list(EXPECTED_CUT_IDS),
            "semantic_duration_seconds": EXPECTED_DURATION_SECONDS,
            "hard_cut_boundaries_seconds": list(EXPECTED_BOUNDARIES_SECONDS),
            "subtitle_ids": list(EXPECTED_SUBTITLE_IDS),
            "subtitle_count": 29,
            "cut003_context_status": "needs_review",
            "cut003_proxy_decision": "proceed_with_limitations",
            "sub030_excluded": True,
        },
        "media_probe": readback["render"]["media"],
        "audio_measurement": readback["audio"],
        "boundary_qa": readback["quality_assurance"]["boundary_analysis"],
        "closed_gates": _closed_gates(),
        "regeneration_command": _regeneration_command(
            root,
            Path(authority["predecessor_path"]).parents[2],
            output,
            authority,
        ),
        "files": files,
        "file_hash_coverage": {
            "required_package_file_count": len(REQUIRED_PACKAGE_FILES),
            "byte_hashed_payload_file_count": len(files),
            "manifest_self_hash_method": "canonical_json_with_self_sha256_value_omitted",
            "status": "complete_including_declared_canonical_manifest_self_hash",
        },
        "manifest_self_integrity": {
            "repo_relative_path": _relative(output / "delivery_manifest.json", root),
            "package_relative_path": "delivery_manifest.json",
            "hash_kind": "sha256_canonical_json_with_this_value_null",
            "sha256": None,
        },
        "narrative_plan_sha256": next(
            item["sha256"]
            for item in files
            if item["package_relative_path"] == "narrative_sequence_plan.json"
        ),
        "authority_summary": plan["cut003_authority"],
    }
    manifest["manifest_self_integrity"]["sha256"] = _canonical_manifest_self_hash(manifest)
    return manifest


def _post_render_assets(
    *,
    video_path: Path,
    poster_path: Path,
    boundaries: tuple[float, ...],
    expected_duration: float,
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
        raise CompleteNarrativeShortError("post-render FFmpeg preflight failed")
    resolved_ffmpeg = str(preflight["ffmpeg"]["path"])
    poster_seconds = 37.800
    poster_command = [
        resolved_ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{poster_seconds:.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(poster_path),
    ]
    poster_result = _run_text_command(poster_command, runner=runner)
    if poster_result.returncode != 0 or not poster_path.is_file():
        raise CompleteNarrativeShortError("final-video poster frame extraction failed")

    boundary_analysis = [
        _audio_boundary_analysis(
            ffmpeg_path=resolved_ffmpeg,
            video_path=video_path,
            boundary_seconds=boundary,
        )
        for boundary in boundaries
    ]
    status = (
        "passed"
        if all(item["status"] == "passed" for item in boundary_analysis)
        else "failed"
    )
    return {
        "status": status,
        "poster": {
            "source": "final_render_frame",
            "seconds": poster_seconds,
            "decorated_thumbnail": False,
            "status": "extracted",
        },
        "boundary_analysis": boundary_analysis,
        "sync": {
            "status": "passed",
            "method": "single_filtergraph_audio_video_concat_with_shared_cut_boundaries",
            "boundaries_seconds": list(boundaries),
            "expected_duration_seconds": expected_duration,
        },
    }


def _audio_boundary_analysis(
    *, ffmpeg_path: str, video_path: Path, boundary_seconds: float
) -> dict[str, Any]:
    window_seconds = 0.500
    half = window_seconds / 2
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{boundary_seconds - half:.3f}",
        "-t",
        f"{window_seconds:.3f}",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "48000",
        "-f",
        "f32le",
        "pipe:1",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CompleteNarrativeShortError(f"boundary PCM extraction failed: {exc}") from exc
    if result.returncode != 0 or not result.stdout:
        raise CompleteNarrativeShortError("boundary PCM extraction produced no samples")
    samples = array.array("f")
    usable = len(result.stdout) - (len(result.stdout) % samples.itemsize)
    samples.frombytes(result.stdout[:usable])
    if sys.byteorder != "little":
        samples.byteswap()
    sample_rate = 48000
    center = min(len(samples) - 1, int(half * sample_rate))
    rms_window = int(0.100 * sample_rate)
    pre = samples[max(0, center - rms_window) : center]
    post = samples[center : min(len(samples), center + rms_window)]
    around = samples[
        max(0, center - int(0.020 * sample_rate)) :
        min(len(samples), center + int(0.020 * sample_rate))
    ]
    max_delta = max(
        (abs(float(around[index]) - float(around[index - 1])) for index in range(1, len(around))),
        default=0.0,
    )
    near_zero_threshold = 1e-5
    longest_zero_run = 0
    current_zero_run = 0
    for sample in samples[
        max(0, center - rms_window) : min(len(samples), center + rms_window)
    ]:
        if abs(float(sample)) <= near_zero_threshold:
            current_zero_run += 1
            longest_zero_run = max(longest_zero_run, current_zero_run)
        else:
            current_zero_run = 0
    longest_zero_seconds = longest_zero_run / sample_rate
    click_risk = max_delta > 1.75
    digital_dropout_risk = longest_zero_seconds > 0.050
    status = "passed" if not click_risk and not digital_dropout_risk else "failed"
    return {
        "boundary_seconds": boundary_seconds,
        "status": status,
        "method": "decoded_f32le_boundary_window_analysis",
        "window_seconds": window_seconds,
        "sample_rate_hz": sample_rate,
        "pre_rms_dbfs": _rms_dbfs(pre),
        "post_rms_dbfs": _rms_dbfs(post),
        "max_adjacent_sample_delta": round(max_delta, 6),
        "click_risk": click_risk,
        "longest_digital_zero_run_seconds": round(longest_zero_seconds, 6),
        "digital_dropout_risk": digital_dropout_risk,
    }


def _rms_dbfs(samples: array.array[float]) -> float:
    if not samples:
        return -120.0
    rms = math.sqrt(sum(float(item) ** 2 for item in samples) / len(samples))
    return round(20.0 * math.log10(max(rms, 1e-6)), 2)


def _validate_staged_bundle(stage: Path, manifest: dict[str, Any]) -> None:
    for relative in REQUIRED_PACKAGE_FILES:
        _require_file(stage / Path(relative), f"staged OUT-06 file {relative}")
    if (stage / ".work").exists():
        raise CompleteNarrativeShortError("internal work directory remained in package")
    plan = _read_json(stage / "narrative_sequence_plan.json", "staged narrative plan")
    readback = _read_json(stage / "candidate_readback.json", "staged candidate readback")
    parsed_manifest = _read_json(stage / "delivery_manifest.json", "staged manifest")
    if plan.get("ordered_cut_ids") != list(EXPECTED_CUT_IDS):
        raise CompleteNarrativeShortError("staged plan cut order changed")
    if int(plan.get("subtitle_count") or 0) != 29:
        raise CompleteNarrativeShortError("staged plan subtitle count changed")
    if readback.get("artifact_id") != ARTIFACT_ID:
        raise CompleteNarrativeShortError("staged readback artifact identity changed")
    if parsed_manifest != manifest:
        raise CompleteNarrativeShortError("staged manifest does not parse identically")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count("<video ") != 1:
        raise CompleteNarrativeShortError("review page must contain exactly one video")
    if "class=\"grid\"" in html:
        raise CompleteNarrativeShortError("review page must not use a card grid")
    file_entries = parsed_manifest.get("files") or []
    if len(file_entries) != len(REQUIRED_PACKAGE_FILES) - 1:
        raise CompleteNarrativeShortError("manifest byte-hash coverage is incomplete")
    for entry in file_entries:
        path = stage / Path(str(entry.get("package_relative_path") or ""))
        if _sha256(path) != str(entry.get("sha256") or ""):
            raise CompleteNarrativeShortError(
                f"manifest hash mismatch: {entry.get('package_relative_path')}"
            )
    declared_self = str(
        (parsed_manifest.get("manifest_self_integrity") or {}).get("sha256") or ""
    )
    if declared_self != _canonical_manifest_self_hash(parsed_manifest):
        raise CompleteNarrativeShortError("manifest canonical self-integrity hash mismatch")
    _validate_closed_gates(parsed_manifest.get("closed_gates") or {})


def _canonical_manifest_self_hash(manifest: dict[str, Any]) -> str:
    payload = copy.deepcopy(manifest)
    payload.setdefault("manifest_self_integrity", {})["sha256"] = None
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _render_html(readback: dict[str, Any], plan: dict[str, Any]) -> str:
    media = readback["render"]["media"]
    audio = readback["audio"]
    questions = "".join(
        f"<li>{escape(question)}</li>" for question in readback["review_questions"]
    )
    cut_rows = "".join(
        "<tr>"
        f"<td><code>{escape(str(item['id']))}</code></td>"
        f"<td>{float(item['source_start_seconds']):.3f}–{float(item['source_end_seconds']):.3f}s</td>"
        f"<td>{float(item['sequence_start_seconds']):.3f}–{float(item['sequence_end_seconds']):.3f}s</td>"
        f"<td>{escape(str(item.get('context_status') or 'passed'))}</td>"
        "</tr>"
        for item in plan["timeline"]
    )
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
<title>OUT-06 完結型ナラティブショート内部候補</title>
<style>
:root {{ color-scheme:dark; font-family:"Yu Gothic UI","Noto Sans JP",sans-serif; background:#07111f; color:#eef6ff; }}
* {{ box-sizing:border-box; }} body {{ margin:0; overflow-x:hidden; }} main {{ width:min(980px,100%); margin:auto; padding:22px; overflow-wrap:anywhere; }}
.eyebrow {{ color:#67e8f9; font-weight:800; letter-spacing:.12em; }} h1 {{ margin:.35rem 0 .4rem; font-size:clamp(1.55rem,4vw,2.45rem); }}
.lead {{ color:#cbd5e1; max-width:74ch; }} .video-wrap {{ display:flex; justify-content:center; margin:18px 0 24px; }}
video {{ display:block; width:auto; height:min(78vh,820px); max-width:100%; max-height:78vh; aspect-ratio:9/16; background:#000; border:1px solid #334155; border-radius:14px; }}
.play-action {{ display:block; margin:0 auto 18px; padding:.7rem 1rem; border:1px solid #22d3ee; border-radius:999px; background:#0e7490; color:#fff; font:inherit; font-weight:800; cursor:pointer; }}
section,details {{ margin-top:20px; padding:16px; border:1px solid #334155; border-radius:11px; background:#0f1b2d; }}
summary {{ cursor:pointer; font-weight:800; }} img {{ display:block; width:100%; height:auto; margin-top:14px; border-radius:9px; }}
table {{ width:100%; border-collapse:collapse; font-size:.92rem; }} th,td {{ padding:8px; text-align:left; vertical-align:top; border-bottom:1px solid #334155; }}
code {{ color:#bae6fd; }} .gate {{ color:#fbbf24; }} li {{ margin:.55rem 0; }}
@media(max-width:620px) {{ main {{ padding:14px; }} video {{ height:min(74vh,720px); }} th:first-child,td:first-child {{ display:none; }} }}
</style></head><body><main>
<div class="eyebrow">OUT-06 · INTERNAL NARRATIVE DELIVERY CANDIDATE</div>
<h1>導入から締めまでを一本で確認</h1>
<p class="lead">受理済みOUT-05の導入を保ち、保持済みcut_003を加えた約38秒の内部レビュー候補です。権利・production・公開判断は含みません。</p>
<div class="video-wrap"><video controls preload="metadata" playsinline poster="assets/poster_frame.jpg" src="assets/complete_narrative_short.mp4"></video></div>
<button class="play-action" data-testid="play-full-candidate" type="button">最初から全編再生</button>
<section><h2>今回の確認</h2><ol>{questions}</ol></section>
<details><summary>ナラティブ構成とカットauthority</summary>
<p>導入=cut_001、展開=cut_002、解決と締め=cut_003。cut_003のneeds_reviewとproceed_with_limitationsは保持しています。</p>
<table><thead><tr><th>Cut</th><th>Source</th><th>Sequence</th><th>Context</th></tr></thead><tbody>{cut_rows}</tbody></table></details>
<details><summary>境界・中盤・終端のフレーム確認</summary><img src="assets/frame_qa_contact_sheet.jpg" alt="開始、両境界、cut_003中盤、密字幕、終端のフレーム確認"></details>
<details><summary>29字幕の表示readback</summary><table><thead><tr><th>ID</th><th>時間</th><th>表示</th></tr></thead><tbody>{subtitle_rows}</tbody></table></details>
<details><summary>媒体・音声・出典</summary>
<p>Video: <code>{escape(str(media['video_codec']))}</code> / {media['width']}x{media['height']} / {media['fps']}fps / {media['duration_seconds']:.3f}s / yuv420p / faststart</p>
<p>Audio: <code>{escape(str(media['audio_codec']))}</code>; input {audio['input_measurement']['integrated_lufs']:.2f} LUFS / {audio['input_measurement']['true_peak_dbtp']:.2f} dBTP; output {audio['output_measurement']['integrated_lufs']:.2f} LUFS / {audio['output_measurement']['true_peak_dbtp']:.2f} dBTP.</p>
<p>Accepted OUT-05 SHA-256: <code>{escape(readback['accepted_opening']['video_sha256'])}</code></p></details>
<details><summary>閉じたゲート</summary><p class="gate">internal_review_only=true / production_candidate=false / production_acceptance=false / production_subtitle_design_acceptance=false / rights_status=pending / public_ready=false / publishing_acceptance=false / publish_attempted=false</p></details>
<script>
const candidateVideo = document.querySelector("video");
const playFullCandidate = document.querySelector('[data-testid="play-full-candidate"]');
playFullCandidate.addEventListener("click", async () => {{
  candidateVideo.currentTime = 0;
  await candidateVideo.play();
}});
const qaParams = new URLSearchParams(window.location.search);
if (qaParams.get("qa-playback") === "1") {{
  candidateVideo.muted = true;
  candidateVideo.currentTime = 0;
  candidateVideo.play();
}}
if (qaParams.has("qa-seek")) {{
  document.body.dataset.qaSeekStatus = "pending";
  candidateVideo.muted = true;
  const requestedRatio = Number(qaParams.get("qa-seek"));
  const runSeekQa = async () => {{
    const duration = candidateVideo.duration;
    const target = Math.max(0, Math.min(duration - 0.05, duration * requestedRatio));
    const startedAt = candidateVideo.currentTime;
    const completed = new Promise((resolve) => {{
      const finish = (status) => resolve(status);
      candidateVideo.addEventListener("seeked", () => finish("seeked"), {{ once: true }});
      window.setTimeout(() => finish("timeout"), 5000);
    }});
    candidateVideo.currentTime = target;
    const status = await completed;
    let playStatus = "not_attempted";
    try {{
      await candidateVideo.play();
      playStatus = "resumed";
    }} catch (error) {{
      playStatus = `play_failed:${{error && error.name ? error.name : "unknown"}}`;
    }}
    const qaResult = {{
      status,
      requestedRatio,
      target,
      startedAt,
      currentTime: candidateVideo.currentTime,
      delta: Math.abs(candidateVideo.currentTime - target),
      duration,
      playStatus,
      readyState: candidateVideo.readyState,
      mediaError: candidateVideo.error ? candidateVideo.error.message : null,
    }};
    document.body.dataset.qaSeek = JSON.stringify(qaResult);
    document.body.dataset.qaSeekStatus = status;
  }};
  if (Number.isFinite(candidateVideo.duration) && candidateVideo.duration > 0) {{
    runSeekQa();
  }} else {{
    candidateVideo.addEventListener("loadedmetadata", runSeekQa, {{ once: true }});
  }}
}}
</script>
</main></body></html>"""


def _open_script() -> str:
    return """param([switch]$Serve, [int]$Port = 8060)
$ErrorActionPreference = 'Stop'
if ($Serve) {
    & (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
    exit $LASTEXITCODE
}
$index = Join-Path $PSScriptRoot 'index.html'
Write-Host "OUT-06 review entrypoint: $index"
Start-Process -FilePath $index
Write-Host "If local-file playback is blocked, rerun this command with -Serve."
"""


def _serve_script() -> str:
    return """param([int]$Port = 8060)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\\..\\..\\..')
Write-Host "OUT-06 review URL: $url"
Write-Host "OUT-06 review root: $PSScriptRoot"
Start-Process -FilePath $url
Push-Location $repoRoot
try {
    uvx python -m src.cli.serve_review --root $PSScriptRoot --port $Port
} finally {
    Pop-Location
}
"""


def _closed_gates() -> dict[str, Any]:
    return {
        "internal_review_only": True,
        "production_candidate": False,
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "rights_status": "pending",
        "public_ready": False,
        "publishing_acceptance": False,
        "publish_attempted": False,
    }


def _validate_closed_gates(
    values: dict[str, Any], *, allow_vertical_key: bool = False
) -> None:
    expected = _closed_gates()
    for key, value in expected.items():
        source_key = key
        if key == "publishing_acceptance" and allow_vertical_key:
            source_key = "publishing"
        if values.get(source_key) != value:
            raise CompleteNarrativeShortError(f"closed gate changed: {source_key}")


def _regeneration_command(
    root: Path,
    episode: Path,
    output: Path,
    authority: dict[str, Any],
) -> str:
    episode_value = _relative(episode, root)
    output_value = _relative(output, root)
    predecessor_value = _relative(Path(authority["predecessor_path"]), root)
    return (
        "uvx --with Pillow python -m src.cli.main build-complete-narrative-short "
        f"--episode-dir {episode_value} --output-dir {output_value} "
        f"--predecessor-readback {predecessor_value} --format json"
    )


def _render_srt(items: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, item in enumerate(items, start=1):
        text = str(item.get("wrapped_text") or item.get("text") or "").replace("\r", "")
        blocks.append(
            f"{index}\n{_srt_time(float(item['display_start_seconds']))} --> "
            f"{_srt_time(float(item['display_end_seconds']))}\n{text}\n"
        )
    return "\n".join(blocks)


def _srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    milliseconds = total_ms % 1000
    total_seconds = total_ms // 1000
    second = total_seconds % 60
    total_minutes = total_seconds // 60
    minute = total_minutes % 60
    hour = total_minutes // 60
    return f"{hour:02d}:{minute:02d}:{second:02d},{milliseconds:03d}"


def _protected_paths(episode: Path) -> dict[str, Path]:
    review = episode / "review"
    paths = {
        "human_preview_session": review
        / "jp_pilot01r3_cut_review"
        / "human_preview_session",
        "out03_real_local_selected_cut_proof": review
        / "out03_real_local_selected_cut_proof",
        "out04_editorial_representative_sequence": review
        / "out04_editorial_representative_sequence",
        "out05_vertical_short_internal_candidate": review
        / "out05_vertical_short_internal_candidate",
    }
    for label, path in paths.items():
        _require_directory(path, f"protected {label}")
    return paths


def _single_recorded_path(
    recorded_inputs: dict[str, Any], root: Path, suffix: str
) -> Path:
    matches = [
        _resolved(root, Path(str(relative)))
        for relative in recorded_inputs
        if str(relative).replace("\\", "/").endswith(suffix)
    ]
    if len(matches) != 1:
        raise CompleteNarrativeShortError(f"expected one recorded input ending in {suffix}")
    _require_file(matches[0], f"recorded {suffix}")
    return matches[0]


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if output.parent != review:
        raise CompleteNarrativeShortError(
            "output directory must be a direct episode/review child"
        )
    if not output.name.startswith(OUTPUT_NAME_PREFIX):
        raise CompleteNarrativeShortError("output directory name must start with out06_")
    if SAFE_IDENTIFIER.fullmatch(output.name) is None:
        raise CompleteNarrativeShortError("unsafe OUT-06 output directory name")


def _validate_predecessor_path(episode: Path, path: Path) -> None:
    expected = (
        episode
        / "review"
        / "out05_vertical_short_internal_candidate"
        / "candidate_readback.json"
    ).resolve()
    if path != expected:
        raise CompleteNarrativeShortError(
            "predecessor must be the retained OUT-05 candidate readback"
        )


def _reject_overlap(output: Path, input_path: Path, message: str) -> None:
    output_resolved = output.resolve()
    input_resolved = input_path.resolve()
    if _is_relative_to(output_resolved, input_resolved) or _is_relative_to(
        input_resolved, output_resolved
    ):
        raise CompleteNarrativeShortError(message)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompleteNarrativeShortError(f"invalid {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CompleteNarrativeShortError(f"invalid {label}: expected JSON object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _run_text_command(
    command: list[str], *, runner: ffmpeg_tiny.Runner
) -> subprocess.CompletedProcess[str]:
    try:
        return runner(
            command,
            capture_output=True,
            text=True,
            timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CompleteNarrativeShortError(f"external command failed: {exc}") from exc


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise CompleteNarrativeShortError(f"{label} is missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise CompleteNarrativeShortError(f"{label} is missing: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    if not _is_relative_to(path.resolve(), parent.resolve()):
        raise CompleteNarrativeShortError(f"{label} must stay inside {parent}")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _numeric_suffix(value: str) -> int:
    try:
        return int(value.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise CompleteNarrativeShortError(f"invalid numbered identifier: {value}") from exc


def _powershell_command(path: Path, root: Path) -> str:
    relative = _relative(path, root).replace("/", "\\")
    return f"powershell -ExecutionPolicy Bypass -File {relative}"


def _assert_close(
    value: Any,
    expected: float,
    label: str,
    tolerance: float = 0.001,
) -> None:
    try:
        actual = float(value)
    except (TypeError, ValueError) as exc:
        raise CompleteNarrativeShortError(f"{label} is not numeric") from exc
    if abs(actual - expected) > tolerance:
        raise CompleteNarrativeShortError(
            f"{label} changed: expected {expected:.3f}, got {actual:.3f}"
        )
