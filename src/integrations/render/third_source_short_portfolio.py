"""OUT-10 bounded third-source Short portfolio builder.

The builder consumes one hash-bound, externally acquired official source and
reuses the shared vertical render path.  It does not fetch network resources,
change predecessor artifacts, or grant rights/production/public acceptance.
"""

from __future__ import annotations

import json
import re
import shutil
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
from src.integrations.render.second_source_short_repeatability import (
    _open_script,
    _render_srt,
    _run_signal_qa,
    _serve_script,
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


ARTIFACT_ID = "clip-out10-third-source-short-portfolio-expansion-v0-001"
SCHEMA_VERSION = "clippipegen.out10.third_source_short_portfolio.v0"
PLAN_SCHEMA_VERSION = "clippipegen.out10.candidate_plan_input.v0"
STATE = "OUT10_ENDPOINT_BOUNDED_REPAIR_REVIEW_READY"
PREDECESSOR_STATE = (
    "OUT10_THIRD_DISTINCT_EXTERNAL_SOURCE_SHORT_REVIEW_READY_WITH_3_SOURCE_SCORECARD"
)
PREDECESSOR_VIDEO_SHA256 = (
    "9c930f82a2447bbdbae8db477d30d46dd5ad3a7710109dd0cba7117686a4bb2f"
)
PREDECESSOR_SOURCE_END_SECONDS = 20.304
LINEAGE_REASON = "superseded_predecessor_endpoint_too_early_active_telop_motion"
OUTPUT_PREFIX = "out10_"
OUT08_PROVIDER_ID = "7J5aS_pcBj4"
OUT09_PROVIDER_ID = "D4i4fjs9PWc"
OUT08_CANDIDATE_HASHES = (
    "f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a",
    "47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b",
)
OUT09_CANDIDATE_HASH = (
    "b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50"
)
REVIEW_QUESTION = (
    "最後のテロップや動きが途中で切れず、一本のShortとして自然に終わるようになったか。"
    "既に合格していた字幕・音声・構図に明確な回帰があれば併せて教えてください。"
)
REVIEW_HOST = "127.0.0.1"
REVIEW_PORT = 8073
INITIAL_VOLUME_CEILING = 0.25
MIN_DURATION_SECONDS = 12.0
MAX_DURATION_SECONDS = 60.0
TIME_TOLERANCE_SECONDS = 0.006
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
REQUIRED_INPUT_ROLES = {
    "rights_manifest",
    "material_ledger",
    "source_caption_track",
    "authoritative_transcript",
    "edit_pack",
    "source_selection_receipt",
}

RenderExecutor = Callable[..., dict[str, Any]]
NavigationExecutor = Callable[..., dict[str, Any]]
SignalQaExecutor = Callable[..., dict[str, Any]]


class ThirdSourceShortPortfolioError(VerticalShortCandidateError):
    """Raised when the OUT-10 authority or package contract is invalid."""


def build_third_source_short_portfolio(
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
    """Build one third-source candidate and a three-source comparison package."""

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
        shutil.copyfile(
            authority["source_selection_receipt_path"],
            stage / "source_selection_receipt.json",
        )

        ass_path = stage / "candidate_01_subtitles.ass"
        srt_path = stage / "candidate_01_subtitles.srt"
        video_path = stage / "candidate_01.mp4"
        frame_path = stage / "candidate_01_frame_qa.jpg"
        navigation_path = stage / "candidate_01_navigation.jpg"

        layout, presentation, selector = build_vertical_subtitle_presentation(
            normalized["semantic_subtitles"],
            application_key="out10_application",
            dimension_source="out10_third_source_neutral_matte_canvas",
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
            raise ThirdSourceShortPortfolioError(
                "black/silence QA did not pass"
            )

        _cleanup_internal_directory(work, expected_parent=stage)
        elapsed = round(time.monotonic() - started, 3)
        video_sha256 = _sha256(video_path)
        presentation_items = [
            {
                "subtitle_id": str(item["subtitle_id"]),
                "display_start_seconds": float(item["display_start_seconds"]),
                "display_end_seconds": float(item["display_end_seconds"]),
                "text": str(item["text"]),
                "wrapped_lines": list(item.get("wrapped_lines") or []),
                "source_segment_ids": list(item.get("source_segment_ids") or []),
                "caption_event_index": int(
                    (item.get("json3_timing_authority") or {})["event_index"]
                ),
            }
            for item in presentation
        ]
        review_access = _review_access_contract(output=output, root=root)
        scorecard = _build_scorecard(
            normalized=normalized,
            video_sha256=video_sha256,
            render_result=render_result,
            subtitle_count=len(presentation_items),
        )
        _write_json(stage / "source_portfolio_scorecard.json", scorecard)
        _write_text(
            stage / "source_portfolio_comparison.html",
            _render_comparison_html(scorecard),
        )

        readback = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": ARTIFACT_ID,
            "state": STATE,
            "episode_id": episode.name,
            "source_identity": normalized["source_identity"],
            "source_difference": {
                "out08_provider_id": OUT08_PROVIDER_ID,
                "out09_provider_id": OUT09_PROVIDER_ID,
                "out10_provider_id": normalized["source_identity"]["provider_id"],
                "all_distinct": True,
            },
            "external_acquisition": normalized["external_acquisition"],
            "source_selection": normalized["source_selection"],
            "input_integrity": authority["input_integrity"],
            "materials": authority["materials"],
            "transcript_authority": normalized["transcript_authority"],
            "selection_authority": normalized["selection_authority"],
            "repair_lineage": normalized["repair_lineage"],
            "endpoint_repair": normalized["endpoint_repair"],
            "portfolio_subtitle_differentiation_debt": normalized[
                "portfolio_subtitle_differentiation_debt"
            ],
            "candidate": {
                "candidate_id": normalized["candidate_id"],
                "source_start_seconds": normalized["source_start_seconds"],
                "source_end_seconds": normalized["source_end_seconds"],
                "duration_seconds": normalized["duration_seconds"],
                "authority_cut_id": normalized["authority_cut_id"],
                "source_segment_ids": normalized["source_segment_ids"],
                "rationale": normalized["rationale"],
                "narrative_arc": normalized["narrative_arc"],
                "predecessor_source_end_seconds": PREDECESSOR_SOURCE_END_SECONDS,
                "endpoint_extension_seconds": normalized["endpoint_repair"][
                    "extension_seconds"
                ],
                "human_review_pending": True,
                "acceptance_granted": False,
            },
            "subtitle": {
                "count": len(presentation_items),
                "ass_path": ass_path.name,
                "srt_path": srt_path.name,
                "containment": containment,
                "selector": selector,
                "items": presentation_items,
                "source_type": "imported_subtitle_track",
                "display_authority": "official_json3_event_text_and_timing",
                "burn_in_applied": True,
                "source_native_dialogue_captions_observed": False,
                "source_native_name_labels_preserved": True,
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
            "portfolio_scorecard": "source_portfolio_scorecard.json",
            "portfolio_comparison": "source_portfolio_comparison.html",
            "review_questions": [REVIEW_QUESTION],
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
                "uvx python -m src.cli.main build-third-source-short-portfolio "
                f"--episode-dir {_relative(episode, root)} "
                f"--output-dir {_relative(output, root)} "
                f"--candidate-plan-input {_relative(plan_path, root)}"
            ),
        }
        _write_json(stage / "candidate_readback.json", readback)
        _write_text(stage / "index.html", _render_html(readback, scorecard))
        _write_text(
            stage / "open_preview.ps1",
            _open_script(default_port=REVIEW_PORT, review_label="OUT-10"),
        )
        _write_text(
            stage / "serve_preview.ps1",
            _serve_script(
                expected_video_sha256=video_sha256,
                artifact_id=ARTIFACT_ID,
                default_port=REVIEW_PORT,
                review_label="OUT-10",
            ),
        )

        files = [
            {
                "package_relative_path": path.name,
                "sha256": _sha256(path),
                "byte_size": path.stat().st_size,
            }
            for path in sorted(item for item in stage.iterdir() if item.is_file())
        ]
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": ARTIFACT_ID,
            "state": STATE,
            "episode_id": episode.name,
            "candidate_video_sha256": video_sha256,
            "candidate_lineage": normalized["repair_lineage"],
            "endpoint_repair": {
                "source_end_seconds": normalized["source_end_seconds"],
                "extension_seconds": normalized["endpoint_repair"][
                    "extension_seconds"
                ],
                "additional_caption_cue_count": normalized["endpoint_repair"][
                    "additional_caption_cue_count"
                ],
            },
            "files": files,
            "file_count": len(files),
            "closed_gates": normalized["boundaries"],
            "manifest_self_integrity": {
                "algorithm": "sha256-canonical-json-self-null",
                "sha256": None,
            },
        }
        manifest["manifest_self_integrity"]["sha256"] = (
            _canonical_manifest_self_hash(manifest)
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

    final_readback = _read_json(output / "candidate_readback.json", "candidate readback")
    return {
        "artifact_id": ARTIFACT_ID,
        "output_dir": output,
        "video_path": output / "candidate_01.mp4",
        "readback_path": output / "candidate_readback.json",
        "manifest_path": output / "candidate_manifest.json",
        "index_path": output / "index.html",
        "readback": final_readback,
    }


def _load_authority(*, root: Path, episode: Path, plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise ThirdSourceShortPortfolioError("unsupported candidate plan schema")
    if plan.get("artifact_id") != ARTIFACT_ID:
        raise ThirdSourceShortPortfolioError("candidate plan artifact_id mismatch")
    if plan.get("episode_id") != episode.name:
        raise ThirdSourceShortPortfolioError("candidate plan episode_id mismatch")
    rows = plan.get("expected_inputs")
    if not isinstance(rows, list):
        raise ThirdSourceShortPortfolioError("expected_inputs are missing")
    paths: dict[str, Path] = {}
    integrity: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ThirdSourceShortPortfolioError("invalid expected input row")
        role = str(row.get("role") or "")
        if role in paths or role not in REQUIRED_INPUT_ROLES:
            raise ThirdSourceShortPortfolioError(f"unexpected input role: {role}")
        path = _resolved(root, Path(str(row.get("path") or "")))
        _require_file(path, f"input {role}")
        _require_within(path, root, f"input {role}")
        if role != "source_selection_receipt":
            _require_within(path, episode, f"input {role}")
        expected = str(row.get("sha256") or "").lower()
        actual = _sha256(path)
        if expected != actual:
            raise ThirdSourceShortPortfolioError(f"input hash mismatch: {role}")
        paths[role] = path
        integrity.append(
            {"role": role, "path": _relative(path, root), "sha256": actual, "verified": True}
        )
    if set(paths) != REQUIRED_INPUT_ROLES:
        missing = sorted(REQUIRED_INPUT_ROLES - set(paths))
        raise ThirdSourceShortPortfolioError(
            f"required input roles are missing: {', '.join(missing)}"
        )

    rights = _read_json(paths["rights_manifest"], "rights manifest")
    if str((rights.get("compliance_check") or {}).get("status") or "") != "pending":
        raise ThirdSourceShortPortfolioError("OUT-10 requires rights=pending")
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
        raise ThirdSourceShortPortfolioError(str(exc)) from exc
    if video["sha256"] != str((materials.get("source_video") or {}).get("sha256") or ""):
        raise ThirdSourceShortPortfolioError("source video plan hash mismatch")
    if audio["sha256"] != str((materials.get("source_audio") or {}).get("sha256") or ""):
        raise ThirdSourceShortPortfolioError("source audio plan hash mismatch")
    return {
        "rights": rights,
        "ledger": ledger,
        "captions": _read_json(paths["source_caption_track"], "source caption track"),
        "transcript": _read_json(paths["authoritative_transcript"], "authoritative transcript"),
        "edit_pack": _read_json(paths["edit_pack"], "edit pack"),
        "selection_receipt": _read_json(paths["source_selection_receipt"], "source selection receipt"),
        "source_selection_receipt_path": paths["source_selection_receipt"],
        "source_video_path": _resolved(root, Path(video["file_path"])),
        "source_audio_path": _resolved(root, Path(audio["file_path"])),
        "materials": {"source_video": video, "source_audio": audio},
        "input_integrity": integrity,
    }


def _normalize_plan(*, plan: dict[str, Any], authority: dict[str, Any]) -> dict[str, Any]:
    identity = plan.get("source_identity") if isinstance(plan.get("source_identity"), dict) else {}
    provider_id = str(identity.get("provider_id") or "")
    if provider_id in {OUT08_PROVIDER_ID, OUT09_PROVIDER_ID} or not provider_id:
        raise ThirdSourceShortPortfolioError("third source recording identity is not distinct")
    if (
        identity.get("platform") != "youtube"
        or identity.get("channel_id") != "UCJFZiqLMntJufDCHc6bQixg"
        or identity.get("official_channel") is not True
        or identity.get("channel_verified") is not True
    ):
        raise ThirdSourceShortPortfolioError("official public channel identity is incomplete")
    rights_source = authority["rights"].get("source_video") or {}
    if provider_id not in str(rights_source.get("url") or ""):
        raise ThirdSourceShortPortfolioError("rights snapshot source identity mismatch")

    acquisition = plan.get("external_acquisition") if isinstance(plan.get("external_acquisition"), dict) else {}
    expected_acquisition = {
        "authorized": True,
        "anonymous": True,
        "metadata_candidate_count": 5,
        "detailed_preflight_count": 3,
        "media_download_count": 1,
        "cookie_or_login_used": False,
        "bypass_used": False,
        "alternate_candidate_download_on_failure": False,
        "source_audio_derived_locally": True,
    }
    if any(acquisition.get(key) != value for key, value in expected_acquisition.items()):
        raise ThirdSourceShortPortfolioError("bounded external acquisition receipt is incomplete")
    receipt = authority["selection_receipt"]
    if (
        receipt.get("artifact_id") != ARTIFACT_ID
        or receipt.get("state") != "OUT10_BOUNDED_EXTERNAL_ACQUISITION_AUTHORIZED"
        or (receipt.get("selected_source") or {}).get("provider_id") != provider_id
        or (receipt.get("scope") or {}).get("metadata_candidate_count") != 5
        or (receipt.get("scope") or {}).get("detailed_preflight_count") != 3
        or (receipt.get("scope") or {}).get("media_download_count") != 1
    ):
        raise ThirdSourceShortPortfolioError("source selection receipt does not bind the selected source")

    transcript = authority["transcript"]
    stt = transcript.get("stt") if isinstance(transcript.get("stt"), dict) else {}
    if (
        stt.get("engine") != "subtitle_track"
        or stt.get("provider") != "youtube_subtitles"
        or stt.get("real_transcript") is not True
        or (transcript.get("review") or {}).get("status") != "needs_review"
    ):
        raise ThirdSourceShortPortfolioError("official subtitle transcript authority is incomplete")
    segments = {
        str(item.get("id") or ""): item
        for item in transcript.get("segments") or []
        if isinstance(item, dict) and item.get("id")
    }
    edit_pack = authority["edit_pack"]
    cuts = {
        str(item.get("id") or ""): item
        for item in edit_pack.get("cut_candidates") or []
        if isinstance(item, dict) and item.get("id")
    }

    candidate = plan.get("candidate") if isinstance(plan.get("candidate"), dict) else {}
    candidate_id = str(candidate.get("candidate_id") or "")
    _safe_identifier(candidate_id, "candidate id")
    start = _number(candidate.get("source_start_seconds"), "candidate source start")
    end = _number(candidate.get("source_end_seconds"), "candidate source end")
    duration = round(end - start, 6)
    if not MIN_DURATION_SECONDS <= duration <= MAX_DURATION_SECONDS:
        raise ThirdSourceShortPortfolioError("candidate duration is outside 12-60 seconds")
    if abs(duration - _number(candidate.get("duration_seconds"), "candidate duration")) > TIME_TOLERANCE_SECONDS:
        raise ThirdSourceShortPortfolioError("candidate duration does not match source range")

    endpoint_repair = (
        plan.get("endpoint_repair")
        if isinstance(plan.get("endpoint_repair"), dict)
        else {}
    )
    extension = round(end - PREDECESSOR_SOURCE_END_SECONDS, 6)
    probes = endpoint_repair.get("probe_candidates")
    inherited_pass = endpoint_repair.get("inherited_pass")
    if (
        endpoint_repair.get("predecessor_state") != PREDECESSOR_STATE
        or endpoint_repair.get("predecessor_video_sha256")
        != PREDECESSOR_VIDEO_SHA256
        or abs(
            _number(
                endpoint_repair.get("predecessor_source_end_seconds"),
                "predecessor source end",
            )
            - PREDECESSOR_SOURCE_END_SECONDS
        )
        > TIME_TOLERANCE_SECONDS
        or endpoint_repair.get("lineage_reason") != LINEAGE_REASON
        or extension <= 0
        or extension > 12.0 + TIME_TOLERANCE_SECONDS
        or not isinstance(probes, list)
        or len(probes) < 2
        or not isinstance(inherited_pass, list)
        or inherited_pass
        != [
            "content_and_tempo",
            "subtitle_audio_sync",
            "subtitle_readability",
            "neutral_matte_composition",
            "safe_review_route",
        ]
    ):
        raise ThirdSourceShortPortfolioError(
            "endpoint repair authority is incomplete"
        )
    selected_probes = [
        item
        for item in probes
        if isinstance(item, dict) and item.get("status") == "selected"
    ]
    if (
        len(selected_probes) != 1
        or abs(
            _number(selected_probes[0].get("source_seconds"), "selected probe")
            - end
        )
        > TIME_TOLERANCE_SECONDS
    ):
        raise ThirdSourceShortPortfolioError(
            "endpoint repair selected probe does not match candidate end"
        )

    subtitle_debt = plan.get("portfolio_subtitle_differentiation_debt")
    if not isinstance(subtitle_debt, dict) or (
        subtitle_debt.get("status") != "deferred"
        or subtitle_debt.get("current_white_style_approved_as_general_standard")
        is not False
        or subtitle_debt.get("speaker_identity_inference_allowed") is not False
        or subtitle_debt.get("revisit_condition")
        != "after_3_to_5_accepted_real_shorts_or_explicit_production_subtitle_design_gate"
    ):
        raise ThirdSourceShortPortfolioError(
            "portfolio subtitle differentiation debt is incomplete"
        )
    cut_id = str(candidate.get("authority_cut_id") or "")
    cut = cuts.get(cut_id)
    if (
        cut is None
        or str((cut.get("context_check") or {}).get("status") or "") != "passed"
        or start < float(cut["start_seconds"]) - TIME_TOLERANCE_SECONDS
        or end > float(cut["end_seconds"]) + TIME_TOLERANCE_SECONDS
        or cut_id not in (edit_pack.get("selected_cut_ids") or [])
    ):
        raise ThirdSourceShortPortfolioError("candidate cut authority is incomplete")

    captions = _caption_event_index(authority["captions"])
    raw_subtitles = candidate.get("subtitles") if isinstance(candidate.get("subtitles"), list) else []
    if not raw_subtitles:
        raise ThirdSourceShortPortfolioError("candidate subtitles are missing")
    semantic: list[dict[str, Any]] = []
    previous_end = start
    used_segments: list[str] = []
    for index, raw in enumerate(raw_subtitles, start=1):
        if not isinstance(raw, dict):
            raise ThirdSourceShortPortfolioError("invalid subtitle plan row")
        subtitle_id = str(raw.get("id") or "")
        _safe_identifier(subtitle_id, "subtitle id")
        segment_id = str(raw.get("source_segment_id") or "")
        segment = segments.get(segment_id)
        event_index = int(raw.get("caption_event_index", -1))
        event = captions.get(event_index)
        if segment is None or event is None:
            raise ThirdSourceShortPortfolioError(f"subtitle authority is missing: {subtitle_id}")
        source_start = _number(raw.get("source_start_seconds"), "subtitle source start")
        source_end = _number(raw.get("source_end_seconds"), "subtitle source end")
        text = str(raw.get("text") or "").strip()
        if (
            abs(source_start - float(segment["start_seconds"])) > TIME_TOLERANCE_SECONDS
            or abs(source_end - float(segment["end_seconds"])) > TIME_TOLERANCE_SECONDS
            or text != str(segment.get("text") or "").strip()
            or abs(source_start - event["start_seconds"]) > TIME_TOLERANCE_SECONDS
            or abs(source_end - event["end_seconds"]) > TIME_TOLERANCE_SECONDS
            or text != event["text"]
        ):
            raise ThirdSourceShortPortfolioError(
                f"subtitle is not exact official JSON3 event authority: {subtitle_id}"
            )
        if source_start < start - TIME_TOLERANCE_SECONDS or source_end > end + TIME_TOLERANCE_SECONDS:
            raise ThirdSourceShortPortfolioError(f"subtitle leaves candidate: {subtitle_id}")
        if source_start < previous_end - TIME_TOLERANCE_SECONDS or source_start - previous_end > 0.15:
            raise ThirdSourceShortPortfolioError(f"subtitle timing gap/overlap is unsafe: {subtitle_id}")
        semantic.append(
            {
                "id": subtitle_id,
                "cut_id": cut_id,
                "sequence_start_seconds": round(source_start - start, 3),
                "sequence_end_seconds": round(source_end - start, 3),
                "text": text,
                "source_type": "imported_subtitle_track",
                "source_segment_ids": [segment_id],
                "json3_timing_authority": {
                    "source": "youtube_json3_official_event",
                    "event_index": event_index,
                    "event_start_seconds": event["start_seconds"],
                    "event_end_seconds": event["end_seconds"],
                },
            }
        )
        used_segments.append(segment_id)
        previous_end = source_end
    if end - previous_end > 0.15 + TIME_TOLERANCE_SECONDS:
        raise ThirdSourceShortPortfolioError("last official caption leaves an unsafe trailing gap")
    predecessor_cue_count = int(
        endpoint_repair.get("predecessor_caption_cue_count") or 0
    )
    additional_cue_count = len(semantic) - predecessor_cue_count
    if predecessor_cue_count != 15 or additional_cue_count <= 0:
        raise ThirdSourceShortPortfolioError(
            "endpoint repair caption lineage is incomplete"
        )

    composition = plan.get("composition_policy") if isinstance(plan.get("composition_policy"), dict) else {}
    if (
        composition.get("mode") != NEUTRAL_MATTE_BACKGROUND_POLICY
        or composition.get("source_frame_pixels") != {"width": 1920, "height": 1080}
        or composition.get("foreground_source_crop_pixels")
        != {"x": 0, "y": 0, "width": 1920, "height": 1080}
        or composition.get("important_content_preserved") is not True
    ):
        raise ThirdSourceShortPortfolioError("full-source neutral matte policy is incomplete")
    boundaries = plan.get("boundaries") if isinstance(plan.get("boundaries"), dict) else {}
    expected_boundaries = {
        "rights_status": "pending",
        "production_candidate": False,
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "production_image_quality_acceptance": False,
        "thumbnail_acceptance": False,
        "public_or_publishing_acceptance": False,
        "publish_or_upload_attempted": False,
        "cross_machine_portability": False,
        "human_review_pending": True,
        "acceptance_granted": False,
    }
    if any(boundaries.get(key) != value for key, value in expected_boundaries.items()):
        raise ThirdSourceShortPortfolioError("candidate boundaries are not closed")
    if plan.get("review_questions") != [REVIEW_QUESTION]:
        raise ThirdSourceShortPortfolioError("OUT-10 requires the exact single review question")

    samples = tuple(
        (label, max(0.1, min(duration - 0.1, round(seconds, 3))))
        for label, seconds in (
            ("start", 0.25),
            ("early", duration * 0.15),
            ("mid", duration * 0.50),
            ("late", duration * 0.75),
            ("final_3_0", duration - 3.0),
            ("final_2_5", duration - 2.5),
            ("final_2_0", duration - 2.0),
            ("final_1_5", duration - 1.5),
            ("final_1_0", duration - 1.0),
            ("final_0_5", duration - 0.5),
            ("final_0_1", duration - 0.1),
        )
    )
    return {
        "source_identity": dict(identity),
        "external_acquisition": expected_acquisition,
        "source_selection": {
            "selected_rank": (authority["selection_receipt"].get("selected_source") or {}).get("rank"),
            "provider_id": provider_id,
            "selection_receipt_state": authority["selection_receipt"]["state"],
            "rejected_preflight_provider_ids": list(
                (authority["selection_receipt"].get("decision") or {}).get("rejected_preflight_provider_ids") or []
            ),
        },
        "candidate_id": candidate_id,
        "source_start_seconds": start,
        "source_end_seconds": end,
        "duration_seconds": duration,
        "authority_cut_id": cut_id,
        "source_segment_ids": used_segments,
        "rationale": str(candidate.get("rationale") or ""),
        "narrative_arc": dict(candidate.get("narrative_arc") or {}),
        "semantic_subtitles": semantic,
        "timeline": [
            {
                "id": "out10_range_001",
                "cut_id": cut_id,
                "source_start_seconds": start,
                "source_end_seconds": end,
                "duration_seconds": duration,
                "sequence_start_seconds": 0.0,
                "sequence_end_seconds": duration,
                "transition_in": "hard_cut",
            }
        ],
        "frame_samples": samples,
        "composition_policy": dict(composition),
        "transcript_authority": {
            "engine": "subtitle_track",
            "provider": "youtube_subtitles",
            "real_transcript": True,
            "review_status": "needs_review",
            "used_source_segment_ids": used_segments,
            "display_authority": "exact_official_json3_event_text_and_timing",
            "human_transcript_acceptance_claimed": False,
        },
        "selection_authority": {
            "candidate_within_context_passed_cut": True,
            "start_basis": str(candidate.get("start_basis") or ""),
            "end_basis": str(candidate.get("end_basis") or ""),
            "next_scene_transition_seconds": candidate.get("next_scene_transition_seconds"),
            "candidate_count_considered": int(candidate.get("candidate_count_considered") or 1),
        },
        "repair_lineage": {
            "predecessor_state": PREDECESSOR_STATE,
            "predecessor_video_sha256": PREDECESSOR_VIDEO_SHA256,
            "predecessor_source_end_seconds": PREDECESSOR_SOURCE_END_SECONDS,
            "lineage_reason": LINEAGE_REASON,
            "predecessor_acceptance_granted": False,
        },
        "endpoint_repair": {
            "probe_window_start_seconds": PREDECESSOR_SOURCE_END_SECONDS,
            "probe_window_end_seconds": round(
                PREDECESSOR_SOURCE_END_SECONDS + 12.0, 3
            ),
            "selected_source_end_seconds": end,
            "extension_seconds": extension,
            "probe_candidates": list(probes),
            "selection_basis": str(
                endpoint_repair.get("selection_basis") or ""
            ),
            "predecessor_caption_cue_count": predecessor_cue_count,
            "additional_caption_cue_count": additional_cue_count,
            "final_caption_end_seconds": previous_end,
        },
        "portfolio_subtitle_differentiation_debt": dict(subtitle_debt),
        "boundaries": expected_boundaries,
    }


def _caption_event_index(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    events = payload.get("events")
    if not isinstance(events, list):
        raise ThirdSourceShortPortfolioError("source caption track has no events")
    result: dict[int, dict[str, Any]] = {}
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        start_ms = event.get("tStartMs")
        duration_ms = event.get("dDurationMs")
        segs = event.get("segs")
        if not isinstance(start_ms, (int, float)) or not isinstance(duration_ms, (int, float)) or not isinstance(segs, list):
            continue
        text = "".join(
            str(item.get("utf8") or "") for item in segs if isinstance(item, dict)
        )
        text = text.replace("\u200b", "").replace("\ufeff", "")
        text = re.sub(r"[ \t\f\v]+", " ", text.replace("\r", "\n"))
        text = re.sub(r" *\n+ *", " ", text).strip()
        if not text:
            continue
        start = round(float(start_ms) / 1000.0, 6)
        result[index] = {
            "start_seconds": start,
            "end_seconds": round(start + float(duration_ms) / 1000.0, 6),
            "text": text,
        }
    return result


def _build_scorecard(
    *,
    normalized: dict[str, Any],
    video_sha256: str,
    render_result: dict[str, Any],
    subtitle_count: int,
) -> dict[str, Any]:
    media = render_result["media"]
    return {
        "schema_version": "clippipegen.out10.source_portfolio_scorecard.v0",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "comparison_scope": "three_distinct_real_recordings_internal_review_evidence_only",
        "rows": [
            {
                "portfolio_slot": "OUT-08",
                "provider_id": OUT08_PROVIDER_ID,
                "candidate_count": 2,
                "media_duration_seconds": [28.266667, 53.466667],
                "subtitle_count": [17, 54],
                "candidate_sha256": list(OUT08_CANDIDATE_HASHES),
                "review_status": "accepted_internal",
                "human_review_pending": False,
                "composition": "full_16_9_fit_source_derived_canvas",
            },
            {
                "portfolio_slot": "OUT-09",
                "provider_id": OUT09_PROVIDER_ID,
                "candidate_count": 1,
                "media_duration_seconds": [33.333008],
                "subtitle_count": [27],
                "candidate_sha256": [OUT09_CANDIDATE_HASH],
                "review_status": "accepted_internal",
                "human_review_pending": False,
                "composition": "caption_free_source_canvas_and_bottom_crop",
            },
            {
                "portfolio_slot": "OUT-10",
                "provider_id": normalized["source_identity"]["provider_id"],
                "candidate_count": 1,
                "media_duration_seconds": [float(media["duration_seconds"])],
                "subtitle_count": [subtitle_count],
                "candidate_sha256": [video_sha256],
                "review_status": "human_review_pending",
                "human_review_pending": True,
                "composition": "full_16_9_fit_neutral_matte_no_blur_no_crop",
                "endpoint_status": "bounded_repair_human_review_pending",
                "endpoint_source_seconds": normalized["source_end_seconds"],
                "superseded_predecessor_sha256": PREDECESSOR_VIDEO_SHA256,
            },
        ],
        "all_recording_identities_distinct": True,
        "production_repeatability_claimed": False,
        "rights_or_publication_acceptance_claimed": False,
        "out10_acceptance_granted": False,
        "winner_selected": False,
        "portfolio_subtitle_differentiation_debt": normalized[
            "portfolio_subtitle_differentiation_debt"
        ],
    }


def _review_access_contract(*, output: Path, root: Path) -> dict[str, Any]:
    clean_url = f"http://{REVIEW_HOST}:{REVIEW_PORT}/index.html"
    relative = _relative(output, root).replace("/", "\\")
    return {
        "clean_human_url": clean_url,
        "canonical_foreground_server_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            f"{relative}\\serve_preview.ps1 -Port {REVIEW_PORT}"
        ),
        "convenience_open_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            f"{relative}\\open_preview.ps1 -Serve -Port {REVIEW_PORT}"
        ),
        "server_bind": REVIEW_HOST,
        "server_port": REVIEW_PORT,
        "server_window_must_remain_open": True,
        "unknown_port_owner_killed": False,
        "autoplay": False,
        "initial_paused": True,
        "initial_muted": True,
        "initial_volume_maximum": INITIAL_VOLUME_CEILING,
        "qa_route": {
            "exact_query": "qa-playback=1",
            "human_documentation_allowed": False,
            "muted_or_zero_volume_required": True,
            "pause_after_check": True,
        },
    }


def _render_html(readback: dict[str, Any], scorecard: dict[str, Any]) -> str:
    candidate = readback["candidate"]
    rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['portfolio_slot']))}</td>"
        f"<td><code>{escape(str(row['provider_id']))}</code></td>"
        f"<td>{escape(str(row['media_duration_seconds']))}</td>"
        f"<td>{escape(str(row['subtitle_count']))}</td>"
        f"<td>{escape(str(row['review_status']))}</td>"
        "</tr>"
        for row in scorecard["rows"]
    )
    question = escape(REVIEW_QUESTION)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="clippipegen-artifact-id" content="{ARTIFACT_ID}"><meta name="clippipegen-video-sha256" content="{escape(readback['video']['sha256'])}">
<title>OUT-10 endpoint repair review</title><style>
:root{{color-scheme:dark;font-family:"Yu Gothic UI","Noto Sans JP",sans-serif;background:#06101d;color:#eff7ff}}*{{box-sizing:border-box}}body{{margin:0;overflow-x:hidden}}main{{width:min(960px,100%);margin:auto;padding:22px;overflow-wrap:anywhere}}section,details{{margin-top:18px;padding:16px;border:1px solid #30445f;border-radius:14px;background:#0d1a2c}}video{{display:block;width:auto;height:min(76vh,820px);max-width:100%;aspect-ratio:9/16;margin:18px auto;background:#000}}code{{color:#9fe7ff}}.boundary{{color:#ffd166}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #30445f;text-align:left}}@media(max-width:620px){{main{{padding:14px}}video{{height:min(72vh,700px)}}table{{font-size:.82rem}}}}
</style></head><body data-artifact-id="{ARTIFACT_ID}" data-video-sha256="{escape(readback['video']['sha256'])}"><main><h1>OUT-10 endpoint bounded repair review</h1>
<p><code>{escape(readback['source_identity']['provider_id'])}</code> / source {candidate['source_start_seconds']:.3f}–{candidate['source_end_seconds']:.3f}s / {candidate['duration_seconds']:.3f}s</p>
<p class="boundary">rights=pending / human review pending / production・public・publishing未承認</p>
<p id="playback-safety-note">初期状態は停止・ミュートです。音声確認時は手動で再生・解除してください（音量上限25%）。</p>
<video id="candidate-video" controls playsinline muted preload="metadata" poster="{escape(readback['navigation_frame']['package_relative_path'])}?v={escape(readback['navigation_frame']['sha256'][:16])}" src="{escape(readback['video']['package_relative_path'])}?v={escape(readback['video']['sha256'][:16])}"></video>
<script>(()=>{{const video=document.getElementById("candidate-video");const maximumVolume={INITIAL_VOLUME_CEILING:.2f};const exactMutedQaRoute=window.location.search==="?qa-playback=1"&&window.location.hash==="";video.defaultMuted=true;video.muted=true;video.volume=exactMutedQaRoute?0:maximumVolume;window.__clipPipeReviewQa={{exactRoute:exactMutedQaRoute,completed:false,error:null}};video.addEventListener("volumechange",()=>{{if(video.volume>maximumVolume)video.volume=maximumVolume;}});const run=async()=>{{video.defaultMuted=true;video.muted=true;video.volume=0;try{{await video.play();window.setTimeout(()=>{{video.pause();window.__clipPipeReviewQa.completed=true;}},1200);}}catch(error){{video.pause();window.__clipPipeReviewQa.error=error&&error.name?error.name:"play_failed";window.__clipPipeReviewQa.completed=true;}}}};if(exactMutedQaRoute){{if(video.readyState>=2)window.queueMicrotask(run);else video.addEventListener("canplay",run,{{once:true}});}}}})();</script>
<section><h2>今回の確認</h2><ol><li data-review-question="1">{question}</li></ol></section>
<section><h2>3-source scorecard</h2><table><thead><tr><th>slot</th><th>recording</th><th>duration(s)</th><th>subtitle(s)</th><th>status</th></tr></thead><tbody>{rows}</tbody></table><p><a href="source_portfolio_comparison.html">比較説明を開く</a> / <a href="source_portfolio_scorecard.json">JSONを開く</a></p></section>
<details open><summary>終端修復・構成・境界</summary><p>{escape(str(candidate['rationale']))}</p><p>旧終端 {PREDECESSOR_SOURCE_END_SECONDS:.3f}s / MP4 <code>{PREDECESSOR_VIDEO_SHA256}</code> は、テロップと動作が途中で切れたため未受理のpredecessorとして保持。新終端は {candidate['source_end_seconds']:.3f}sで、最後の公式captionとthumb-up poseが完了し、直後のshot changeより前で閉じます。</p><p>全16:9 foregroundを保持し、source-derived blurもcenter cropも使わず、neutral matteへfit。元映像のname labelは保持し、dialogue subtitleは公式JSON3 eventから別canvas位置へburn-in。</p><p>全白字幕は一般標準として承認せず、speaker differentiationは3〜5本のaccepted real Shorts比較後またはproduction subtitle-design gate開始時に再検討します。navigation frameは識別用でありthumbnail候補ではありません。</p></details>
</main></body></html>"""


def _render_comparison_html(scorecard: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['portfolio_slot']))}</td>"
        f"<td><code>{escape(str(row['provider_id']))}</code></td>"
        f"<td>{escape(str(row['candidate_count']))}</td>"
        f"<td>{escape(str(row['media_duration_seconds']))}</td>"
        f"<td>{escape(str(row['composition']))}</td>"
        f"<td>{escape(str(row['review_status']))}</td>"
        "</tr>"
        for row in scorecard["rows"]
    )
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OUT-10 3-source comparison</title><style>:root{{color-scheme:dark;font-family:"Yu Gothic UI",sans-serif;background:#07111f;color:#eef6ff}}main{{max-width:1100px;margin:auto;padding:22px;overflow-wrap:anywhere}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #334155;text-align:left}}code{{color:#9fe7ff}}.boundary{{color:#ffd166}}@media(max-width:700px){{table{{font-size:.78rem}}}}</style></head><body><main><h1>OUT-08 / OUT-09 / OUT-10 source portfolio</h1><p>三つのdistinct recordingに対するinternal evidenceを並べる。OUT-08/09はaccepted internal、OUT-10はhuman review pendingで、production repeatability・rights・公開可否は証明しない。</p><table><thead><tr><th>slot</th><th>recording</th><th>candidate</th><th>duration(s)</th><th>composition</th><th>status</th></tr></thead><tbody>{rows}</tbody></table><p class="boundary">OUT-10の判断はexact MP4 hashへbindし、他sourceのacceptanceを継承しない。</p><p><a href="index.html">OUT-10 video reviewへ戻る</a></p></main></body></html>"""


def _validate_staged_package(
    stage: Path,
    readback: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    required = (
        "candidate_01.mp4",
        "candidate_01_subtitles.ass",
        "candidate_01_subtitles.srt",
        "candidate_01_frame_qa.jpg",
        "candidate_01_navigation.jpg",
        "candidate_plan.json",
        "source_selection_receipt.json",
        "candidate_readback.json",
        "candidate_manifest.json",
        "source_portfolio_scorecard.json",
        "source_portfolio_comparison.html",
        "index.html",
        "open_preview.ps1",
        "serve_preview.ps1",
    )
    for name in required:
        _require_file(stage / name, f"staged package file {name}")
    if (stage / ".work").exists():
        raise ThirdSourceShortPortfolioError("internal work directory remained")
    if _read_json(stage / "candidate_readback.json", "staged readback") != readback:
        raise ThirdSourceShortPortfolioError("staged readback did not parse consistently")
    parsed_manifest = _read_json(stage / "candidate_manifest.json", "staged manifest")
    if parsed_manifest != manifest:
        raise ThirdSourceShortPortfolioError("staged manifest did not parse consistently")
    if parsed_manifest["manifest_self_integrity"]["sha256"] != _canonical_manifest_self_hash(parsed_manifest):
        raise ThirdSourceShortPortfolioError("manifest self-integrity mismatch")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count("<video ") != 1 or html.count("data-review-question=") != 1:
        raise ThirdSourceShortPortfolioError("review page surface is invalid")
    if "autoplay" in html.lower() or "localStorage" in html or "sessionStorage" in html:
        raise ThirdSourceShortPortfolioError("review page violates playback safety")
    server = (stage / "serve_preview.ps1").read_text(encoding="utf-8")
    if "Stop-Process" in server or "taskkill" in server.lower():
        raise ThirdSourceShortPortfolioError("review server must not kill a port owner")


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if output.parent != review or not output.name.startswith(OUTPUT_PREFIX):
        raise ThirdSourceShortPortfolioError(
            "output directory must be a direct episode/review child starting with out10_"
        )
    _safe_identifier(output.name, "output directory")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ThirdSourceShortPortfolioError(f"invalid {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ThirdSourceShortPortfolioError(f"{label} must be a JSON object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise ThirdSourceShortPortfolioError(f"{label} not found: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise ThirdSourceShortPortfolioError(f"{label} not found: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise ThirdSourceShortPortfolioError(f"{label} escapes allowed root") from exc


def _safe_identifier(value: str, label: str) -> None:
    if not value or SAFE_ID.fullmatch(value) is None:
        raise ThirdSourceShortPortfolioError(f"unsafe {label}: {value!r}")


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ThirdSourceShortPortfolioError(f"{label} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ThirdSourceShortPortfolioError(f"{label} must be numeric") from exc
