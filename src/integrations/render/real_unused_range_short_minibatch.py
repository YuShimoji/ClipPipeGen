"""OUT-08 real unused-range vertical-short minibatch builder.

The builder consumes one declarative, ignored candidate plan and current
episode authority.  It derives subtitle timing, reuses the established OUT-05
vertical render path, and atomically promotes one same-machine review package.
It does not mutate edit, decision, boundary, rights, or material authority.
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
    _real_transcript,
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


ARTIFACT_ID = "clip-out08-real-unused-range-short-minibatch-v0-001"
SCHEMA_VERSION = "clippipegen.out08.real_unused_range_short_minibatch.v0"
STATE = "OUT08_REAL_UNUSED_RANGE_SHORT_MINIBATCH_REVIEW_READY"
EPISODE_ID = "jp_pilot01_hololive_bancho_20260525"
SOURCE_PROVIDER_ID = "7J5aS_pcBj4"
SOURCE_URL = f"https://www.youtube.com/watch?v={SOURCE_PROVIDER_ID}"
SOURCE_VIDEO_MATERIAL_ID = "src_video_jp_pilot01"
SOURCE_AUDIO_MATERIAL_ID = "src_audio_jp_pilot01"
SOURCE_VIDEO_SHA256 = "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
SOURCE_AUDIO_SHA256 = "46e4bc9e26d52ed8f83b0b4088ddcd6ddac5a873fa1bb4a440c209834f026671"
CAPTION_SHA256 = "3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919"
CAPTION_RELATIVE = Path(f"source_subs/{SOURCE_PROVIDER_ID}.ja.json3")
DECISION_RELATIVE = Path("review/jp_pilot01r3_cut_review/cut_decision_packet.json")
BOUNDARY_RELATIVE = Path(
    "review/jp_pilot01r3_cut_review/cut_003_boundary_recommendation_report.json"
)
OUTPUT_PREFIX = "out08_"
TARGET_CANDIDATE_COUNT = 2
MIN_CANDIDATE_COUNT = 1
MAX_CANDIDATE_COUNT = 2
MIN_DURATION_SECONDS = 12.0
MAX_DURATION_SECONDS = 55.0
TIME_TOLERANCE_SECONDS = 0.002
USED_RANGES = (
    ("cut_001", 2.453, 9.293),
    ("cut_002", 12.329, 17.167),
    ("cut_003", 22.606, 49.566),
)
ELIGIBLE_CUT_IDS = tuple(f"cut_{index:03d}" for index in range(4, 9))
REJECTED_CUT_ID = "cut_009"
CANDIDATE_01_SHA256 = "f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a"
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
ABSOLUTE_PATH = re.compile(r"(?:^[A-Za-z]:[\\/]|^\\\\)")
REVIEW_QUESTION = "追加Shorts候補ごとに、一本の編集単位として成立するか、テンポ・境界・字幕・音声に違和感があれば自由記述してください。"
OUT08_DISPLAY_WHITESPACE_NORMALIZATION_IDS = frozenset(
    {"sub_061", "sub_064", "sub_067"}
)
OUT08_REVIEWED_LINE_BREAK_HINTS: dict[str, dict[str, Any]] = {
    "sub_038": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["お店屋さん", "ごっこかな～？😄"]],
        "forbidden_boundaries": ["お店屋|さん"],
    },
    "sub_045": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["ありがとう", "ございました～！"]],
        "forbidden_boundaries": ["ありがとうご|ざいました"],
    },
    "sub_061": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["こんなゾクゾクする", "バトルは", "久しぶりだ…！"]],
        "forbidden_boundaries": ["バ|トル"],
    },
    "sub_063": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["番長の血が", "よぉぉぉーーー！！！"]],
        "forbidden_boundaries": ["よぉ|ぉぉ"],
    },
    "sub_064": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["はじめ様がなんか", "ホニャホニャ", "言ってる…"]],
        "forbidden_boundaries": ["ホ|ニャ"],
    },
    "sub_067": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["そして、さっきの", "はじめちゃんの特殊", "なイントネーションが"]],
        "forbidden_boundaries": ["は|じめ"],
    },
    "sub_096": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["下界ニ呼ビ出シタ", "ノハキサマカ。"]],
        "forbidden_boundaries": ["出シ|タノハ"],
    },
    "sub_098": {
        "reason": "out08_bounded_wrap_repair_2026_07_14",
        "preferred_lines": [["はじめは", "リグロスの番長！"]],
        "forbidden_boundaries": ["リグ|ロス"],
    },
}

RenderExecutor = Callable[..., dict[str, Any]]
NavigationExecutor = Callable[..., dict[str, Any]]


class RealUnusedRangeShortMinibatchError(VerticalShortCandidateError):
    """Raised when OUT-08 cannot be built without authority or scope drift."""


def _build_out08_subtitle_presentation(
    semantic_subtitles: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    presentation_subtitles: list[dict[str, Any]] = []
    for value in semantic_subtitles:
        subtitle_id = str(value.get("id") or "")
        source_text = str(value.get("text") or "")
        display_text = source_text
        normalization = "none"
        if subtitle_id in OUT08_DISPLAY_WHITESPACE_NORMALIZATION_IDS:
            display_text = re.sub(r"[ \t]+", "", source_text)
            normalization = "display_only_ascii_whitespace_removed"
        presentation_subtitles.append(
            {
                **value,
                "text": display_text,
                "source_text": source_text,
                "display_text_normalization": normalization,
            }
        )
    return build_vertical_subtitle_presentation(
        presentation_subtitles,
        application_key="out08_application",
        dimension_source="out08_real_unused_range_vertical_canvas",
        line_break_hints=OUT08_REVIEWED_LINE_BREAK_HINTS,
    )


def build_real_unused_range_short_minibatch(
    *,
    episode_dir: str | Path,
    output_dir: str | Path,
    candidate_plan_input_path: str | Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
    render_executor: RenderExecutor | None = None,
    navigation_executor: NavigationExecutor | None = None,
    expected_source_video_sha256: str = SOURCE_VIDEO_SHA256,
    expected_source_audio_sha256: str = SOURCE_AUDIO_SHA256,
    expected_caption_sha256: str = CAPTION_SHA256,
) -> dict[str, Any]:
    """Build and atomically promote one ignored OUT-08 review minibatch."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(root, Path(output_dir))
    plan_input_path = _resolved(root, Path(candidate_plan_input_path))
    _require_directory(episode, "episode directory")
    if episode.name != EPISODE_ID:
        raise RealUnusedRangeShortMinibatchError(f"episode must be {EPISODE_ID}")
    _require_within(episode, root, "episode directory")
    _validate_output_directory(episode, output)
    _require_file(plan_input_path, "candidate plan input")
    _require_within(plan_input_path, episode, "candidate plan input")
    _reject_overlap(output, plan_input_path, "output must not overlap plan input")

    authority = _load_authority(
        root=root,
        episode=episode,
        plan_input_path=plan_input_path,
        expected_source_video_sha256=expected_source_video_sha256,
        expected_source_audio_sha256=expected_source_audio_sha256,
        expected_caption_sha256=expected_caption_sha256,
    )
    scan = _candidate_scan(episode=episode, authority=authority)
    plan = _normalize_plan(
        episode=episode,
        plan_input=authority["plan_input"],
        authority=authority,
        scan=scan,
    )
    input_hashes_before = {
        _relative(path, root): _sha256(path) for path in authority["input_paths"]
    }
    review_dir = episode / "review"
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    backup: Path | None = None
    try:
        stage.mkdir(parents=False, exist_ok=False)
        work = stage / ".work"
        work.mkdir()
        rendered: list[dict[str, Any]] = []
        executor = render_executor or render_vertical_sequence_assets
        nav_executor = navigation_executor or _extract_navigation_frame
        for candidate in plan["candidates"]:
            reused = _reuse_existing_candidate(
                output=output,
                stage=stage,
                candidate=candidate,
            )
            if reused is not None:
                rendered.append(reused)
                continue
            rendered.append(
                _render_candidate(
                    root=root,
                    output=output,
                    stage=stage,
                    work=work,
                    authority=authority,
                    candidate=candidate,
                    render_executor=executor,
                    navigation_executor=nav_executor,
                    ffmpeg_path=ffmpeg_path,
                    ffprobe_path=ffprobe_path,
                    runner=runner,
                )
            )
        _cleanup_internal_directory(work, expected_parent=stage)

        if input_hashes_before != {
            _relative(path, root): _sha256(path) for path in authority["input_paths"]
        }:
            raise RealUnusedRangeShortMinibatchError(
                "authority or source input changed during render"
            )
        scan_payload = {
            **scan,
            "input_hashes": input_hashes_before,
            "authority_mutated": False,
        }
        readback = _batch_readback(
            root=root,
            episode=episode,
            output=output,
            authority=authority,
            plan=plan,
            rendered=rendered,
            input_hashes=input_hashes_before,
        )
        _write_json(stage / "candidate_scan_readback.json", scan_payload)
        _write_json(stage / "candidate_plan.json", plan)
        _write_json(stage / "batch_readback.json", readback)
        _write_text(stage / "index.html", _render_html(readback))
        _write_text(stage / "open_preview.ps1", _open_script())
        _write_text(stage / "serve_preview.ps1", _serve_script())
        manifest = _batch_manifest(
            root=root, output=output, stage=stage, readback=readback
        )
        _write_json(stage / "batch_manifest.json", manifest)
        _validate_staged_package(stage=stage, manifest=manifest, readback=readback)
        try:
            backup = _atomic_promote(stage, output)
        except PermissionError as exc:
            raise RealUnusedRangeShortMinibatchError(
                "OUT-08 output is in use; stop its preview server and rerun"
            ) from exc
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)

    final_readback = _read_json(output / "batch_readback.json", "batch readback")
    return {
        "artifact_id": ARTIFACT_ID,
        "output_dir": output,
        "index_path": output / "index.html",
        "readback_path": output / "batch_readback.json",
        "manifest_path": output / "batch_manifest.json",
        "readback": final_readback,
    }


def _load_authority(
    *,
    root: Path,
    episode: Path,
    plan_input_path: Path,
    expected_source_video_sha256: str,
    expected_source_audio_sha256: str,
    expected_caption_sha256: str,
) -> dict[str, Any]:
    paths = {
        "edit_pack": episode / "edit_pack.json",
        "transcript": episode / "transcript.json",
        "ledger": episode / "material_ledger.json",
        "rights": episode / "rights_manifest.json",
        "caption": episode / CAPTION_RELATIVE,
        "decision": episode / DECISION_RELATIVE,
        "boundary": episode / BOUNDARY_RELATIVE,
        "plan_input": plan_input_path,
    }
    for label, path in paths.items():
        _require_file(path, label)
        _require_within(path, episode, label)
    values = {label: _read_json(path, label) for label, path in paths.items()}
    if str(values["edit_pack"].get("episode_id") or episode.name) != EPISODE_ID:
        raise RealUnusedRangeShortMinibatchError("edit pack episode identity changed")

    transcript_info, transcript_segments = _real_transcript(values["transcript"])
    try:
        video = _material_readback(
            values["ledger"],
            material_id=SOURCE_VIDEO_MATERIAL_ID,
            expected_kind="source_video",
            root=root,
            episode=episode,
        )
        audio = _material_readback(
            values["ledger"],
            material_id=SOURCE_AUDIO_MATERIAL_ID,
            expected_kind="source_audio",
            root=root,
            episode=episode,
        )
    except EditorialSequenceError as exc:
        raise RealUnusedRangeShortMinibatchError(str(exc)) from exc
    if video["sha256"] != expected_source_video_sha256:
        raise RealUnusedRangeShortMinibatchError("source video SHA-256 changed")
    if audio["sha256"] != expected_source_audio_sha256:
        raise RealUnusedRangeShortMinibatchError("source audio SHA-256 changed")
    caption_sha = _sha256(paths["caption"])
    if caption_sha != expected_caption_sha256:
        raise RealUnusedRangeShortMinibatchError("official caption SHA-256 changed")

    source_identity = values["decision"].get("source_identity") or {}
    subtitle_track = str(source_identity.get("subtitle_track") or "").replace("\\", "/")
    rights_source = values["rights"].get("source_video") or {}
    if (
        source_identity.get("youtube_id") != SOURCE_PROVIDER_ID
        or source_identity.get("source_video_material_id") != SOURCE_VIDEO_MATERIAL_ID
        or not subtitle_track.endswith(CAPTION_RELATIVE.as_posix())
        or rights_source.get("url") != SOURCE_URL
    ):
        raise RealUnusedRangeShortMinibatchError(
            "source/caption identity cannot be tied to decision and rights authority"
        )
    if (
        str((values["rights"].get("compliance_check") or {}).get("status") or "")
        != "pending"
    ):
        raise RealUnusedRangeShortMinibatchError("OUT-08 must preserve rights pending")

    boundary_options = _boundary_options(values["boundary"])
    if not any(
        item["cut_id"] == "cut_003"
        and _close(item["start_seconds"], 22.606)
        and _close(item["end_seconds"], 49.566)
        for item in boundary_options
    ):
        raise RealUnusedRangeShortMinibatchError(
            "cut_003 applied boundary cannot be tied to recommendation authority"
        )
    source_video_path = _resolved(root, Path(video["file_path"]))
    source_audio_path = _resolved(root, Path(audio["file_path"]))
    input_paths = list(paths.values()) + [source_video_path, source_audio_path]
    return {
        **values,
        "paths": paths,
        "input_paths": input_paths,
        "transcript_info": transcript_info,
        "transcript_segments": transcript_segments,
        "video_material": video,
        "audio_material": audio,
        "source_video_path": source_video_path,
        "source_audio_path": source_audio_path,
        "caption_sha256": caption_sha,
        "boundary_options": boundary_options,
    }


def _candidate_scan(*, episode: Path, authority: dict[str, Any]) -> dict[str, Any]:
    cuts = _cut_map(authority["edit_pack"])
    decisions = _decision_map(authority["decision"])
    for cut_id, start, end in USED_RANGES:
        cut = cuts.get(cut_id)
        if (
            cut is None
            or not _close(cut.get("start_seconds"), start)
            or not _close(cut.get("end_seconds"), end)
        ):
            raise RealUnusedRangeShortMinibatchError(
                f"used range authority changed: {cut_id}"
            )
    examined: list[dict[str, Any]] = []
    for cut_id in ELIGIBLE_CUT_IDS:
        cut = cuts.get(cut_id)
        decision = decisions.get(cut_id)
        if cut is None or decision is None:
            raise RealUnusedRangeShortMinibatchError(
                f"candidate authority missing: {cut_id}"
            )
        final = str(decision.get("final_cut_decision") or "")
        if final not in {"keep", "accepted", "needs_adjustment"}:
            raise RealUnusedRangeShortMinibatchError(
                f"candidate cut is not usable: {cut_id}"
            )
        examined.append(_scan_cut(cut, decision))
    rejected = cuts.get(REJECTED_CUT_ID)
    rejected_decision = decisions.get(REJECTED_CUT_ID)
    if rejected is None or rejected_decision is None:
        raise RealUnusedRangeShortMinibatchError("cut_009 reject authority is missing")
    if rejected_decision.get("final_cut_decision") != "reject":
        raise RealUnusedRangeShortMinibatchError("cut_009 rejection changed")
    return {
        "schema_version": "clippipegen.out08.candidate_scan.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": episode.name,
        "source_identity": {
            "provider": "youtube",
            "provider_id": SOURCE_PROVIDER_ID,
            "source_video_sha256": authority["video_material"]["sha256"],
            "caption_sha256": authority["caption_sha256"],
        },
        "examined_cut_ids": list(ELIGIBLE_CUT_IDS),
        "examined_cuts": examined,
        "excluded_ranges": [
            {
                "cut_id": cut_id,
                "start_seconds": start,
                "end_seconds": end,
                "reason": "already_used_by_out06",
            }
            for cut_id, start, end in USED_RANGES
        ]
        + [
            {
                "cut_id": REJECTED_CUT_ID,
                "start_seconds": float(rejected["start_seconds"]),
                "end_seconds": float(rejected["end_seconds"]),
                "reason": "final_cut_decision_reject",
            }
        ],
        "boundary_authority": authority["boundary_options"],
        "target_candidate_count": TARGET_CANDIDATE_COUNT,
        "minimum_candidate_count": MIN_CANDIDATE_COUNT,
        "authority_mutated": False,
    }


def _normalize_plan(
    *,
    episode: Path,
    plan_input: dict[str, Any],
    authority: dict[str, Any],
    scan: dict[str, Any],
) -> dict[str, Any]:
    if plan_input.get("schema_version") != "clippipegen.out08.candidate_plan_input.v0":
        raise RealUnusedRangeShortMinibatchError("unexpected candidate plan schema")
    if (
        plan_input.get("episode_id") != EPISODE_ID
        or plan_input.get("source_id") != SOURCE_PROVIDER_ID
    ):
        raise RealUnusedRangeShortMinibatchError(
            "candidate plan source identity changed"
        )
    specs = plan_input.get("candidates")
    if (
        not isinstance(specs, list)
        or not MIN_CANDIDATE_COUNT <= len(specs) <= MAX_CANDIDATE_COUNT
    ):
        raise RealUnusedRangeShortMinibatchError(
            "candidate plan must contain one or two candidates"
        )
    cuts = _cut_map(authority["edit_pack"])
    decisions = _decision_map(authority["decision"])
    subtitles = [
        item
        for item in authority["edit_pack"].get("subtitles", [])
        if isinstance(item, dict)
    ]
    candidates: list[dict[str, Any]] = []
    all_ranges: list[tuple[str, float, float]] = []
    for index, spec in enumerate(specs, start=1):
        expected_id = f"candidate_{index:02d}"
        if not isinstance(spec, dict) or spec.get("candidate_id") != expected_id:
            raise RealUnusedRangeShortMinibatchError(
                f"candidate id must be {expected_id}"
            )
        rationale = str(spec.get("rationale") or "").strip()
        arc = spec.get("narrative_arc") or {}
        if not rationale or any(
            not str(arc.get(key) or "").strip()
            for key in ("setup", "development", "payoff")
        ):
            raise RealUnusedRangeShortMinibatchError(
                f"{expected_id} narrative rationale is incomplete"
            )
        ranges = spec.get("ranges")
        if not isinstance(ranges, list) or not ranges:
            raise RealUnusedRangeShortMinibatchError(
                f"{expected_id} ranges are missing"
            )
        timeline: list[dict[str, Any]] = []
        semantic_subtitles: list[dict[str, Any]] = []
        offset = 0.0
        for range_index, item in enumerate(ranges, start=1):
            normalized = _normalize_range(
                candidate_id=expected_id,
                range_index=range_index,
                item=item,
                cuts=cuts,
                decisions=decisions,
                subtitles=subtitles,
            )
            for owner, previous_start, previous_end in all_ranges:
                if _overlap(
                    normalized["source_start_seconds"],
                    normalized["source_end_seconds"],
                    previous_start,
                    previous_end,
                ):
                    raise RealUnusedRangeShortMinibatchError(
                        f"candidate source ranges overlap: {owner}/{expected_id}"
                    )
            all_ranges.append(
                (
                    expected_id,
                    normalized["source_start_seconds"],
                    normalized["source_end_seconds"],
                )
            )
            duration = round(
                normalized["source_end_seconds"] - normalized["source_start_seconds"], 3
            )
            sequence_start = round(offset, 3)
            sequence_end = round(offset + duration, 3)
            timeline.append(
                {
                    **normalized,
                    "id": f"{expected_id}_range_{range_index:02d}",
                    "duration_seconds": duration,
                    "sequence_start_seconds": sequence_start,
                    "sequence_end_seconds": sequence_end,
                    "transition_in": "sequence_start"
                    if range_index == 1
                    else "hard_cut",
                }
            )
            selected = _subtitles_for_range(
                normalized,
                subtitles=subtitles,
                transcript_segments=authority["transcript_segments"],
            )
            if not selected:
                raise RealUnusedRangeShortMinibatchError(
                    f"{expected_id} range {range_index} has no fully contained subtitles"
                )
            for subtitle in selected:
                semantic_subtitles.append(
                    {
                        "id": subtitle["id"],
                        "cut_id": subtitle["cut_id"],
                        "source_start_seconds": subtitle["start_seconds"],
                        "source_end_seconds": subtitle["end_seconds"],
                        "sequence_start_seconds": round(
                            sequence_start
                            + subtitle["start_seconds"]
                            - normalized["source_start_seconds"],
                            3,
                        ),
                        "sequence_end_seconds": round(
                            sequence_start
                            + subtitle["end_seconds"]
                            - normalized["source_start_seconds"],
                            3,
                        ),
                        "text": subtitle["text"],
                        "source_type": subtitle["source_type"],
                        "source_segment_ids": subtitle["source_segment_ids"],
                    }
                )
            offset = sequence_end
        if (
            offset < MIN_DURATION_SECONDS - TIME_TOLERANCE_SECONDS
            or offset > MAX_DURATION_SECONDS + TIME_TOLERANCE_SECONDS
        ):
            raise RealUnusedRangeShortMinibatchError(
                f"{expected_id} duration must be 12-55 seconds; got {offset:.3f}"
            )
        candidates.append(
            {
                "candidate_id": expected_id,
                "rationale": rationale,
                "narrative_arc": {
                    key: str(arc[key]) for key in ("setup", "development", "payoff")
                },
                "semantic_duration_seconds": round(offset, 3),
                "timeline": timeline,
                "subtitle_count": len(semantic_subtitles),
                "subtitle_ids": [item["id"] for item in semantic_subtitles],
                "semantic_subtitles": semantic_subtitles,
                "hard_cut_boundaries_seconds": [
                    item["sequence_end_seconds"] for item in timeline[:-1]
                ],
                "cut009_rejection_preserved": True,
            }
        )
    return {
        "schema_version": "clippipegen.out08.candidate_plan.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": episode.name,
        "source_identity": scan["source_identity"],
        "target_candidate_count": TARGET_CANDIDATE_COUNT,
        "minimum_candidate_count": MIN_CANDIDATE_COUNT,
        "actual_candidate_count": len(candidates),
        "selection_status": "human_review_pending",
        "authority_mutated": False,
        "cut009_final_cut_decision": "reject",
        "candidates": candidates,
    }


def _normalize_range(
    *,
    candidate_id: str,
    range_index: int,
    item: Any,
    cuts: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    subtitles: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise RealUnusedRangeShortMinibatchError(
            f"{candidate_id} range {range_index} is invalid"
        )
    start = _number(item.get("source_start_seconds"), "range start")
    end = _number(item.get("source_end_seconds"), "range end")
    if end <= start:
        raise RealUnusedRangeShortMinibatchError(
            "candidate range must have positive duration"
        )
    rejected = cuts.get(REJECTED_CUT_ID)
    if rejected is None:
        raise RealUnusedRangeShortMinibatchError("cut_009 reject authority is missing")
    if _overlap(
        start,
        end,
        float(rejected["start_seconds"]),
        float(rejected["end_seconds"]),
    ):
        raise RealUnusedRangeShortMinibatchError(
            "candidate overlaps rejected cut_009"
        )
    cut_ids = item.get("authority_cut_ids")
    if (
        not isinstance(cut_ids, list)
        or not cut_ids
        or any(not isinstance(value, str) for value in cut_ids)
    ):
        raise RealUnusedRangeShortMinibatchError(
            "candidate range authority_cut_ids are missing"
        )
    if "dependent_payoff_only" in item:
        raise RealUnusedRangeShortMinibatchError(
            "dependent_payoff_only is not supported"
        )
    if any(cut_id not in ELIGIBLE_CUT_IDS for cut_id in cut_ids):
        raise RealUnusedRangeShortMinibatchError(
            "candidate range may use only cut_004..cut_008"
        )
    for cut_id in cut_ids:
        if cut_id not in cuts or str(
            (decisions.get(cut_id) or {}).get("final_cut_decision") or ""
        ) not in {"keep", "accepted", "needs_adjustment"}:
            raise RealUnusedRangeShortMinibatchError(
                f"range authority is not usable: {cut_id}"
            )
    envelope_start = min(float(cuts[value]["start_seconds"]) for value in cut_ids)
    envelope_end = max(float(cuts[value]["end_seconds"]) for value in cut_ids)
    if (
        start < envelope_start - TIME_TOLERANCE_SECONDS
        or end > envelope_end + TIME_TOLERANCE_SECONDS
    ):
        raise RealUnusedRangeShortMinibatchError(
            "candidate range leaves its cut authority envelope"
        )
    basis = item.get("boundary_basis")
    if basis == "cut_authority":
        if not _close(start, envelope_start) or not _close(end, envelope_end):
            raise RealUnusedRangeShortMinibatchError(
                "cut-authority range must match its envelope"
            )
    elif basis == "subtitle_aligned_derivation":
        owned = [value for value in subtitles if value.get("cut_id") in cut_ids]
        if not any(
            _close(start, value.get("start_seconds")) for value in owned
        ) or not any(_close(end, value.get("end_seconds")) for value in owned):
            raise RealUnusedRangeShortMinibatchError(
                "derived range must align to subtitle boundaries"
            )
    else:
        raise RealUnusedRangeShortMinibatchError("unsupported boundary_basis")
    for cut_id, used_start, used_end in USED_RANGES:
        if _overlap(start, end, used_start, used_end):
            raise RealUnusedRangeShortMinibatchError(
                f"candidate overlaps used range {cut_id}"
            )
    return {
        "source_start_seconds": round(start, 3),
        "source_end_seconds": round(end, 3),
        "authority_cut_ids": cut_ids,
        "boundary_basis": str(item.get("boundary_basis")),
        "authority_mutated": False,
    }


def _subtitles_for_range(
    item: dict[str, Any],
    *,
    subtitles: list[dict[str, Any]],
    transcript_segments: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for raw in subtitles:
        if raw.get("cut_id") not in item["authority_cut_ids"]:
            continue
        start = _number(raw.get("start_seconds"), "subtitle start")
        end = _number(raw.get("end_seconds"), "subtitle end")
        if (
            start < item["source_start_seconds"] - TIME_TOLERANCE_SECONDS
            or end > item["source_end_seconds"] + TIME_TOLERANCE_SECONDS
        ):
            continue
        subtitle_id = str(raw.get("id") or "")
        text = str(raw.get("text") or "").strip()
        source_type = str(raw.get("source_type") or "")
        segment_ids = [str(value) for value in (raw.get("source_segment_ids") or [])]
        if (
            not subtitle_id
            or not text
            or source_type not in {"imported_subtitle_track", "real_transcript"}
            or not segment_ids
        ):
            raise RealUnusedRangeShortMinibatchError(
                f"invalid subtitle authority: {subtitle_id or 'unknown'}"
            )
        linked: list[dict[str, Any]] = []
        for segment_id in segment_ids:
            segment = transcript_segments.get(segment_id)
            if segment is None or segment.get("review_status") != "accepted":
                raise RealUnusedRangeShortMinibatchError(
                    f"transcript segment is not accepted: {segment_id}"
                )
            linked.append(segment)
        linked_text = " ".join(
            str(value.get("text") or "").strip() for value in linked
        ).strip()
        if linked_text != text:
            raise RealUnusedRangeShortMinibatchError(
                f"subtitle/transcript text mismatch: {subtitle_id}"
            )
        if not _close(start, linked[0].get("start_seconds")) or not _close(
            end, linked[-1].get("end_seconds")
        ):
            raise RealUnusedRangeShortMinibatchError(
                f"subtitle/transcript timing mismatch: {subtitle_id}"
            )
        selected.append(
            {
                "id": subtitle_id,
                "cut_id": str(raw["cut_id"]),
                "start_seconds": start,
                "end_seconds": end,
                "text": text,
                "source_type": source_type,
                "source_segment_ids": segment_ids,
            }
        )
    return sorted(selected, key=lambda value: (value["start_seconds"], value["id"]))


def _reuse_existing_candidate(
    *,
    output: Path,
    stage: Path,
    candidate: dict[str, Any],
) -> dict[str, Any] | None:
    """Copy the unchanged candidate 01 bytes into a replacement package."""

    if candidate["candidate_id"] != "candidate_01" or not output.is_dir():
        return None
    readback_path = output / "batch_readback.json"
    manifest_path = output / "batch_manifest.json"
    if not readback_path.is_file() or not manifest_path.is_file():
        return None
    readback = _read_json(readback_path, "existing batch readback")
    manifest = _read_json(manifest_path, "existing batch manifest")
    if manifest.get("manifest_self_integrity", {}).get(
        "sha256"
    ) != _canonical_manifest_self_hash(manifest):
        raise RealUnusedRangeShortMinibatchError(
            "existing manifest self-integrity mismatch"
        )
    existing = next(
        (
            value
            for value in readback.get("candidates", [])
            if value.get("candidate_id") == "candidate_01"
        ),
        None,
    )
    if existing is None:
        raise RealUnusedRangeShortMinibatchError(
            "existing candidate_01 readback is missing"
        )
    range_keys = (
        "source_start_seconds",
        "source_end_seconds",
        "authority_cut_ids",
        "boundary_basis",
        "id",
        "duration_seconds",
        "sequence_start_seconds",
        "sequence_end_seconds",
        "transition_in",
    )
    existing_ranges = [
        {key: value.get(key) for key in range_keys}
        for value in existing.get("source_ranges", [])
        if isinstance(value, dict)
    ]
    current_ranges = [
        {key: value.get(key) for key in range_keys}
        for value in candidate["timeline"]
    ]
    expected_plan_values = (
        ("semantic_duration_seconds", candidate["semantic_duration_seconds"]),
        ("subtitle_count", candidate["subtitle_count"]),
        ("subtitle_ids", candidate["subtitle_ids"]),
        ("rationale", candidate["rationale"]),
        ("narrative_arc", candidate["narrative_arc"]),
    )
    if existing_ranges != current_ranges or any(
        existing.get(key) != expected for key, expected in expected_plan_values
    ):
        raise RealUnusedRangeShortMinibatchError(
            "existing candidate_01 does not match the unchanged plan"
        )
    if (existing.get("video") or {}).get("sha256") != CANDIDATE_01_SHA256:
        raise RealUnusedRangeShortMinibatchError(
            "existing candidate_01 SHA-256 changed"
        )

    expected_files = {
        "candidate_01.mp4",
        "candidate_01_subtitles.ass",
        "candidate_01_subtitles.srt",
        "candidate_01_navigation.jpg",
        "candidate_01_frame_qa.jpg",
    }
    entries = {
        str(value.get("package_relative_path")): value
        for value in manifest.get("files", [])
        if isinstance(value, dict)
    }
    for relative in sorted(expected_files):
        source = output / relative
        entry = entries.get(relative) or {}
        _require_file(source, f"existing {relative}")
        if _sha256(source) != entry.get("sha256"):
            raise RealUnusedRangeShortMinibatchError(
                f"existing candidate_01 manifest hash mismatch: {relative}"
            )
        shutil.copy2(source, stage / relative)
    if _sha256(stage / "candidate_01.mp4") != CANDIDATE_01_SHA256:
        raise RealUnusedRangeShortMinibatchError(
            "staged candidate_01 SHA-256 changed"
        )
    return {
        "candidate_id": "candidate_01",
        "video": existing["video"],
        "subtitle": existing["subtitle"],
        "navigation_frame": existing["navigation_frame"],
        "frame_qa": existing["frame_qa"],
        "render": existing["render"],
        "audio": existing["audio"],
        "render_reuse": {
            "status": "reused_existing_candidate_bytes",
            "video_sha256": CANDIDATE_01_SHA256,
            "manifest_verified": True,
        },
    }


def _render_candidate(
    *,
    root: Path,
    output: Path,
    stage: Path,
    work: Path,
    authority: dict[str, Any],
    candidate: dict[str, Any],
    render_executor: RenderExecutor,
    navigation_executor: NavigationExecutor,
    ffmpeg_path: str | Path | None,
    ffprobe_path: str | Path | None,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    candidate_id = candidate["candidate_id"]
    ass_path = stage / f"{candidate_id}_subtitles.ass"
    srt_path = stage / f"{candidate_id}_subtitles.srt"
    video_path = stage / f"{candidate_id}.mp4"
    navigation_path = stage / f"{candidate_id}_navigation.jpg"
    frame_sheet_path = stage / f"{candidate_id}_frame_qa.jpg"
    candidate_work = work / candidate_id
    candidate_work.mkdir()
    layout, items, _selector = _build_out08_subtitle_presentation(
        candidate["semantic_subtitles"]
    )
    containment = validate_vertical_subtitle_containment(
        items,
        expected_duration=float(candidate["semantic_duration_seconds"]),
        layout=layout,
        expected_count=len(items),
    )
    _write_ass(ass_path, items, layout=layout, review_label=None)
    _write_text(srt_path, _render_srt(items))
    required_texts = tuple(str(value["text"]) for value in items[:1] + items[-1:])
    validate_ass_visible_content(
        ass_path, expected_count=len(items), required_texts=required_texts
    )
    result = render_executor(
        source_video_path=authority["source_video_path"],
        source_audio_path=authority["source_audio_path"],
        timeline=candidate["timeline"],
        ass_path=ass_path,
        video_path=video_path,
        compare_sheet_path=None,
        frame_sheet_path=frame_sheet_path,
        work_dir=candidate_work,
        subtitle_layout=layout,
        expected_duration=float(candidate["semantic_duration_seconds"]),
        frame_samples=_frame_samples(candidate),
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    validate_vertical_render_result(
        result,
        video_path=video_path,
        expected_duration=float(candidate["semantic_duration_seconds"]),
    )
    _require_file(frame_sheet_path, "frame QA sheet")
    nav_seconds = round(
        min(
            max(0.25, float(candidate["semantic_duration_seconds"]) * 0.5),
            float(candidate["semantic_duration_seconds"]) - 0.25,
        ),
        3,
    )
    navigation = navigation_executor(
        video_path=video_path,
        output_path=navigation_path,
        seconds=nav_seconds,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        runner=runner,
    )
    _require_file(navigation_path, "navigation frame")
    presentation_items = [
        {
            "subtitle_id": value["subtitle_id"],
            "display_start_seconds": value["display_start_seconds"],
            "display_end_seconds": value["display_end_seconds"],
            "text": value["text"],
            "source_text": value.get("source_text", value["text"]),
            "display_text_normalization": value.get(
                "display_text_normalization", "none"
            ),
            "wrapped_lines": list(value.get("wrapped_lines") or []),
        }
        for value in items
    ]
    return {
        "candidate_id": candidate_id,
        "video": {
            "package_relative_path": video_path.name,
            "sha256": _sha256(video_path),
        },
        "subtitle": {
            "count": len(items),
            "ass_path": ass_path.name,
            "srt_path": srt_path.name,
            "containment": containment,
            "font_family": (layout.get("diagnostic_ass_style") or {}).get("font_name"),
            "items": presentation_items,
        },
        "navigation_frame": {
            "package_relative_path": navigation_path.name,
            "sha256": _sha256(navigation_path),
            "seconds": nav_seconds,
            "role": "navigation_only",
            "human_thumbnail_review_required": False,
            "decorated_thumbnail": False,
            "headline_added": False,
            "mask_added": False,
            "reference_pixels_used": False,
            "thumbnail_acceptance_claimed": False,
            "extraction": navigation,
        },
        "frame_qa": {
            "package_relative_path": frame_sheet_path.name,
            "sha256": _sha256(frame_sheet_path),
            "samples": result["frame_samples"],
        },
        "render": {
            "media": result["media"],
            "selected_video_encoder": result["selected_video_encoder"],
            "attempts": result["attempts"],
            "full_decode": result["full_decode"],
            "faststart": result.get("faststart"),
        },
        "audio": result["audio"],
    }


def _extract_navigation_frame(
    *,
    video_path: Path,
    output_path: Path,
    seconds: float,
    ffmpeg_path: str | Path | None,
    ffprobe_path: str | Path | None,
    runner: ffmpeg_tiny.Runner,
) -> dict[str, Any]:
    preflight = ffmpeg_tiny.preflight_tools(
        ffmpeg_path=ffmpeg_path, ffprobe_path=ffprobe_path, runner=runner
    )
    if preflight.get("status") != "passed":
        raise RealUnusedRangeShortMinibatchError(
            "navigation frame FFmpeg preflight failed"
        )
    command = [
        str(preflight["ffmpeg"]["path"]),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{seconds:.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ]
    try:
        result = runner(
            command,
            capture_output=True,
            text=True,
            timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RealUnusedRangeShortMinibatchError(
            f"navigation frame extraction failed: {exc}"
        ) from exc
    if result.returncode != 0 or not output_path.is_file():
        raise RealUnusedRangeShortMinibatchError(
            "navigation frame extraction produced no frame"
        )
    return {"status": "passed", "source": "final_candidate_frame", "seconds": seconds}


def _batch_readback(
    *,
    root: Path,
    episode: Path,
    output: Path,
    authority: dict[str, Any],
    plan: dict[str, Any],
    rendered: list[dict[str, Any]],
    input_hashes: dict[str, str],
) -> dict[str, Any]:
    by_id = {value["candidate_id"]: value for value in rendered}
    candidates: list[dict[str, Any]] = []
    for candidate in plan["candidates"]:
        rendered_item = by_id[candidate["candidate_id"]]
        candidates.append(
            {
                "candidate_id": candidate["candidate_id"],
                "semantic_duration_seconds": candidate["semantic_duration_seconds"],
                "source_ranges": candidate["timeline"],
                "hard_cut_boundaries_seconds": candidate["hard_cut_boundaries_seconds"],
                "subtitle_count": candidate["subtitle_count"],
                "subtitle_ids": candidate["subtitle_ids"],
                "rationale": candidate["rationale"],
                "narrative_arc": candidate["narrative_arc"],
                "cut009_rejection_preserved": candidate["cut009_rejection_preserved"],
                **rendered_item,
                "browser_qa": {
                    "required": True,
                    "status": "pending_external_browser_validation",
                    "points_seconds": [
                        0.0,
                        *candidate["hard_cut_boundaries_seconds"],
                        candidate["semantic_duration_seconds"],
                    ],
                },
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "episode_id": episode.name,
        "source_class": "real_local_unused_range_internal_review_media",
        "storage": {
            "class": "ignored_local_retained_same_machine",
            "portable_across_clones": False,
            "episodes_tracked": False,
        },
        "source_identity": {
            "provider": "youtube",
            "provider_id": SOURCE_PROVIDER_ID,
            "source_video": authority["video_material"],
            "source_audio": authority["audio_material"],
            "caption": {
                "path": _relative(authority["paths"]["caption"], root),
                "sha256": authority["caption_sha256"],
            },
            "transcript": authority["transcript_info"],
        },
        "target_candidate_count": TARGET_CANDIDATE_COUNT,
        "minimum_candidate_count": MIN_CANDIDATE_COUNT,
        "actual_candidate_count": len(candidates),
        "candidates": candidates,
        "input_hashes": input_hashes,
        "review_entrypoint": _relative(output / "index.html", root),
        "machine_readback": _relative(output / "batch_readback.json", root),
        "batch_manifest": _relative(output / "batch_manifest.json", root),
        "review_questions": [REVIEW_QUESTION],
        "boundaries": {
            "internal_review_only": True,
            "human_review_pending": True,
            "production_candidate": False,
            "production_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "rights_status": "pending",
            "public_ready": False,
            "publishing_acceptance": False,
            "publish_attempted": False,
            "navigation_frames_are_thumbnails": False,
            "cut009_final_cut_decision": "reject",
            "authority_mutated": False,
        },
    }


def _batch_manifest(
    *, root: Path, output: Path, stage: Path, readback: dict[str, Any]
) -> dict[str, Any]:
    files = []
    for path in sorted(
        (
            value
            for value in stage.rglob("*")
            if value.is_file() and value.name != "batch_manifest.json"
        ),
        key=lambda value: value.relative_to(stage).as_posix(),
    ):
        relative = path.relative_to(stage).as_posix()
        files.append(
            {
                "package_relative_path": relative,
                "repo_relative_path": _relative(output / Path(relative), root),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "hash_kind": "sha256_file_bytes",
            }
        )
    manifest = {
        "schema_version": "clippipegen.out08.batch_manifest.v0",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "episode_id": readback["episode_id"],
        "package_path": _relative(output, root),
        "candidate_count": readback["actual_candidate_count"],
        "files": files,
        "file_hash_coverage": {
            "status": "complete",
            "byte_hashed_payload_file_count": len(files),
        },
        "closed_gates": readback["boundaries"],
        "manifest_self_integrity": {
            "package_relative_path": "batch_manifest.json",
            "hash_kind": "sha256_canonical_json_with_this_value_null",
            "sha256": None,
        },
    }
    manifest["manifest_self_integrity"]["sha256"] = _canonical_manifest_self_hash(
        manifest
    )
    return manifest


def _validate_staged_package(
    *, stage: Path, manifest: dict[str, Any], readback: dict[str, Any]
) -> None:
    common = {
        "index.html",
        "candidate_scan_readback.json",
        "candidate_plan.json",
        "batch_readback.json",
        "batch_manifest.json",
        "open_preview.ps1",
        "serve_preview.ps1",
    }
    dynamic = set()
    for candidate in readback["candidates"]:
        candidate_id = candidate["candidate_id"]
        dynamic.update(
            {
                f"{candidate_id}.mp4",
                f"{candidate_id}_subtitles.ass",
                f"{candidate_id}_subtitles.srt",
                f"{candidate_id}_navigation.jpg",
                f"{candidate_id}_frame_qa.jpg",
            }
        )
    actual = {
        value.relative_to(stage).as_posix()
        for value in stage.rglob("*")
        if value.is_file()
    }
    if actual != common | dynamic:
        raise RealUnusedRangeShortMinibatchError("staged package file set changed")
    parsed_manifest = _read_json(stage / "batch_manifest.json", "staged manifest")
    if parsed_manifest != manifest:
        raise RealUnusedRangeShortMinibatchError("staged manifest parse mismatch")
    expected_payload = actual - {"batch_manifest.json"}
    entries = {
        str(value.get("package_relative_path")): value for value in manifest["files"]
    }
    if set(entries) != expected_payload:
        raise RealUnusedRangeShortMinibatchError("manifest file coverage is incomplete")
    for relative, entry in entries.items():
        if _sha256(stage / relative) != entry.get("sha256"):
            raise RealUnusedRangeShortMinibatchError(
                f"manifest hash mismatch: {relative}"
            )
    if manifest["manifest_self_integrity"]["sha256"] != _canonical_manifest_self_hash(
        manifest
    ):
        raise RealUnusedRangeShortMinibatchError("manifest self-integrity mismatch")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if (
        html.count("<video ") != readback["actual_candidate_count"]
        or "display:grid" in html
        or "grid-template" in html
    ):
        raise RealUnusedRangeShortMinibatchError(
            "review page is not a single-column candidate list"
        )
    if html.count(REVIEW_QUESTION) != 1:
        raise RealUnusedRangeShortMinibatchError("review page question changed")
    for path in stage.rglob("*"):
        if path.is_file() and path.suffix.lower() in {
            ".json",
            ".html",
            ".ps1",
            ".srt",
            ".ass",
        }:
            _assert_no_absolute_paths(path.read_text(encoding="utf-8-sig"), path.name)


def _render_html(readback: dict[str, Any]) -> str:
    sections = []
    for candidate in readback["candidates"]:
        ranges = " / ".join(
            f"{value['source_start_seconds']:.3f}-{value['source_end_seconds']:.3f}s"
            for value in candidate["source_ranges"]
        )
        media = candidate["render"]["media"]
        audio = candidate["audio"]["output_measurement"]
        sections.append(
            f"""<section class="candidate" data-candidate-id="{escape(candidate["candidate_id"])}">
<h2>{escape(candidate["candidate_id"])}</h2>
<video controls preload="metadata" playsinline poster="{escape(candidate["navigation_frame"]["package_relative_path"])}" src="{escape(candidate["video"]["package_relative_path"])}"></video>
<p>source {escape(ranges)} / sequence {candidate["semantic_duration_seconds"]:.3f}s / subtitles {candidate["subtitle_count"]}</p>
<p>{escape(candidate["rationale"])}</p>
<details><summary>構成と根拠</summary><dl><dt>導入</dt><dd>{escape(candidate["narrative_arc"]["setup"])}</dd><dt>展開</dt><dd>{escape(candidate["narrative_arc"]["development"])}</dd><dt>着地</dt><dd>{escape(candidate["narrative_arc"]["payoff"])}</dd></dl></details>
<details><summary>media / subtitle / audio evidence</summary><p>{escape(str(media["video_codec"]))}/{escape(str(media["audio_codec"]))} · {media["width"]}x{media["height"]} · {media["fps"]}fps · {media["duration_seconds"]:.3f}s</p><p>Audio {audio["integrated_lufs"]:.2f} LUFS / {audio["true_peak_dbtp"]:.2f} dBTP</p><p>navigation role=navigation_only / human_thumbnail_review_required=false</p></details>
</section>"""
        )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-08 追加Shorts候補</title><style>
:root{{color-scheme:dark;font-family:"Yu Gothic UI","Noto Sans JP",sans-serif;background:#07111f;color:#eef6ff}}*{{box-sizing:border-box}}body{{margin:0;overflow-x:hidden}}main{{width:min(880px,100%);margin:auto;padding:22px;overflow-wrap:anywhere}}.candidate,details,.question{{display:block;margin-top:20px;padding:16px;border:1px solid #334155;border-radius:12px;background:#0f1b2d}}video{{display:block;width:auto;height:min(76vh,820px);max-width:100%;aspect-ratio:9/16;margin:16px auto;background:#000}}summary{{cursor:pointer;font-weight:800}}dt{{font-weight:800;margin-top:8px}}dd{{margin-left:0;color:#cbd5e1}}.notice{{color:#fbbf24}}@media(max-width:620px){{main{{padding:14px}}video{{height:min(72vh,700px)}}}}
</style></head><body><main><h1>OUT-08 追加Shorts候補</h1><p>target 2 / actual {readback["actual_candidate_count"]}。各 navigation frame は移動補助のみで、サムネイル評価ではありません。</p>
<section class="question"><h2>確認事項</h2><p>{escape(REVIEW_QUESTION)}</p></section>
{"".join(sections)}
</main></body></html>"""


def _open_script() -> str:
    return """param([int]$Port = 8071)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
exit $LASTEXITCODE
"""


def _serve_script() -> str:
    return r"""param([int]$Port = 8071)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
Write-Host "OUT-08 review URL: $url"
Start-Process -FilePath $url
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')
Push-Location $repoRoot
try {
    uvx python -m src.cli.serve_review --root $PSScriptRoot --port $Port
} finally {
    Pop-Location
}
"""


def _frame_samples(candidate: dict[str, Any]) -> tuple[tuple[str, float], ...]:
    duration = float(candidate["semantic_duration_seconds"])
    samples: list[tuple[str, float]] = [("start", min(0.25, duration / 2))]
    for index, boundary in enumerate(candidate["hard_cut_boundaries_seconds"], start=1):
        samples.append((f"before_boundary_{index}", max(0.0, float(boundary) - 0.15)))
        samples.append(
            (f"after_boundary_{index}", min(duration - 0.05, float(boundary) + 0.15))
        )
    samples.append(("end", max(0.0, duration - 0.25)))
    return tuple(samples)


def _render_srt(items: list[dict[str, Any]]) -> str:
    blocks = []
    for index, item in enumerate(items, start=1):
        text = str(item.get("wrapped_text") or item.get("text") or "").replace("\r", "")
        blocks.append(
            f"{index}\n{_srt_time(float(item['display_start_seconds']))} --> {_srt_time(float(item['display_end_seconds']))}\n{text}\n"
        )
    return "\n".join(blocks)


def _srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    milliseconds = total_ms % 1000
    total_seconds = total_ms // 1000
    second = total_seconds % 60
    minute = (total_seconds // 60) % 60
    hour = total_seconds // 3600
    return f"{hour:02d}:{minute:02d}:{second:02d},{milliseconds:03d}"


def _boundary_options(payload: dict[str, Any]) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    stack: list[Any] = [payload]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            cut_id = value.get("cut_id")
            start = value.get("recommended_start_seconds")
            end = value.get("recommended_end_seconds")
            if (
                isinstance(cut_id, str)
                and isinstance(start, (int, float))
                and isinstance(end, (int, float))
            ):
                options.append(
                    {
                        "cut_id": cut_id,
                        "start_seconds": float(start),
                        "end_seconds": float(end),
                        "kind": "recommended",
                    }
                )
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
    return sorted(
        options,
        key=lambda item: (item["cut_id"], item["start_seconds"], item["end_seconds"]),
    )


def _cut_map(edit_pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["id"]): item
        for item in edit_pack.get("cut_candidates", [])
        if isinstance(item, dict) and item.get("id")
    }


def _decision_map(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["cut_id"]): item
        for item in packet.get("decisions", [])
        if isinstance(item, dict) and item.get("cut_id")
    }


def _scan_cut(cut: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "cut_id": str(cut["id"]),
        "start_seconds": float(cut["start_seconds"]),
        "end_seconds": float(cut["end_seconds"]),
        "context_status": str(
            (cut.get("context_check") or {}).get("status")
            or decision.get("context_status")
            or "unknown"
        ),
        "final_cut_decision": str(decision.get("final_cut_decision") or ""),
        "decision_reason": str(decision.get("decision_reason") or ""),
    }


def _assert_no_absolute_paths(text: str, label: str) -> None:
    for token in re.findall(r"[^\s\"'<>]+", text):
        unix_absolute = token.startswith("/") and token.count("/") >= 2
        if ABSOLUTE_PATH.match(token) or unix_absolute:
            raise RealUnusedRangeShortMinibatchError(
                f"absolute path leaked into {label}"
            )


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if (
        output.parent != review
        or not output.name.startswith(OUTPUT_PREFIX)
        or SAFE_ID.fullmatch(output.name) is None
    ):
        raise RealUnusedRangeShortMinibatchError(
            "output must be a safe direct episode/review/out08_* directory"
        )


def _reject_overlap(output: Path, input_path: Path, message: str) -> None:
    try:
        output.resolve().relative_to(input_path.resolve())
        raise RealUnusedRangeShortMinibatchError(message)
    except ValueError:
        pass
    try:
        input_path.resolve().relative_to(output.resolve())
        raise RealUnusedRangeShortMinibatchError(message)
    except ValueError:
        pass


def _overlap(start: float, end: float, other_start: float, other_end: float) -> bool:
    return (
        start < other_end - TIME_TOLERANCE_SECONDS
        and other_start < end - TIME_TOLERANCE_SECONDS
    )


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RealUnusedRangeShortMinibatchError(f"{label} must be numeric")
    return float(value)


def _close(value: Any, expected: Any) -> bool:
    try:
        return abs(float(value) - float(expected)) <= TIME_TOLERANCE_SECONDS
    except (TypeError, ValueError):
        return False


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RealUnusedRangeShortMinibatchError(f"invalid {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RealUnusedRangeShortMinibatchError(
            f"invalid {label}: expected JSON object"
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise RealUnusedRangeShortMinibatchError(f"missing {label}: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise RealUnusedRangeShortMinibatchError(f"missing {label}: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise RealUnusedRangeShortMinibatchError(
            f"{label} must remain within {parent}"
        ) from exc
