"""Build the accepted-baseline OUT-07 native Shorts cover review package.

The accepted MP4 is copied byte-for-byte and never rendered, remuxed, or
transcoded here.  The only new visual is a decoded frame from that accepted
vertical MP4; list and 4:5 files are explicitly preview-only derivatives.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import uuid
from html import escape
from pathlib import Path
from typing import Any, Iterable

from src.integrations.render.operator_delivery_pack import EPISODE_COPY_PLAN


ARTIFACT_ID = "clip-out07-shorts-poster-frame-direction-proof-v0-001"
HISTORICAL_OPERATOR_ARTIFACT_ID = "clip-out07-internal-operator-delivery-pack-v0-001"
SCHEMA_VERSION = "clippipegen.out07.native_shorts_cover.v0"
STATE = "OUT07_REINSTANTIATED_BASELINE_ACCEPTED_NATIVE_SHORTS_COVER_OPERATOR_PACK_REVIEW_READY"
EPISODE_ID = "jp_pilot01_hololive_bancho_20260525"
SOURCE_PROVIDER_ID = "7J5aS_pcBj4"
SOURCE_VIDEO_SHA256 = "e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889"
ACCEPTED_BASELINE_SHA256 = (
    "2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18"
)
ACCEPTED_BASELINE_BYTES = 21_669_538
ACCEPTED_BASELINE_DURATION_SECONDS = 38.633333
ACCEPTANCE_DATE = "2026-07-13 JST"
RECOMMENDED_BASELINE_SECONDS = 11.930
RECOMMENDED_SOURCE_SECONDS = 22.858
RECOMMENDED_SUBTITLE_ID = "sub_010"
BASELINE_FRAME_FINGERPRINT_SHA256 = (
    "d2187bfb68f14b2eebfea2249061c7130a5bc5a6e25fbb0d5592782c9cb33062"
)
SOURCE_FRAME_FINGERPRINT_SHA256 = (
    "c44c9258b165dda344dab75a68e9f8ee0a0b0c265f2264492275da0de74b64d3"
)
FINGERPRINT_PROFILE = "raw_rgb24_320x180_bilinear"
REVIEW_QUESTION = (
    "Shorts一覧用coverとして、映像由来フレーム＋既存字幕だけのこの方向を採用してよいか。"
    "違和感があれば自由記述してください。"
)
DEFAULT_OUTPUT_NAME = "out07_shorts_poster_frame_direction_proof"
DEFAULT_BASELINE_NAME = "out07_reinstantiated_baseline_candidate"

FRAME_SURVEY: tuple[dict[str, Any], ...] = (
    {
        "baseline_seconds": 11.930,
        "source_seconds": 22.858,
        "subtitle_id": "sub_010",
        "assessment": "recommended: frontal subject, open eyes, single readable burn-in line",
        "recommended": True,
    },
    {
        "baseline_seconds": 22.890,
        "source_seconds": 33.818,
        "subtitle_id": "sub_019",
        "assessment": "not selected: two subjects but denser two-line subtitle and weaker list-scale read",
        "recommended": False,
    },
    {
        "baseline_seconds": 25.158,
        "source_seconds": 36.086,
        "subtitle_id": "sub_021",
        "assessment": "not selected: clear frame but smaller face and less specific cue",
        "recommended": False,
    },
)


class Out07NativeCoverError(ValueError):
    """Raised when the package cannot be built without changing its evidence."""


def reconstitute_out07_native_cover(
    *,
    episode_dir: str | Path,
    reference_corpus_path: str | Path,
    output_dir: str | Path | None = None,
    baseline_output_dir: str | Path | None = None,
    reference_cache_dir: str | Path | None = None,
    fetch_missing_references: bool = False,
    verify_determinism: bool = False,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build twice from fixed local evidence and promote one deterministic package."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    reference_corpus = _resolved(root, Path(reference_corpus_path))
    baseline_dir = _resolved(
        root,
        Path(baseline_output_dir)
        if baseline_output_dir is not None
        else episode / "review" / DEFAULT_BASELINE_NAME,
    )
    output = _resolved(
        root,
        Path(output_dir)
        if output_dir is not None
        else episode / "review" / DEFAULT_OUTPUT_NAME,
    )
    _validate_paths(episode, baseline_dir, output, reference_corpus)

    # The argument remains CLI-compatible.  This route deliberately performs no
    # crawl and does not consume third-party pixel caches.
    reference_cache_observed = None
    if reference_cache_dir is not None:
        reference_cache_observed = _relative(
            _resolved(root, Path(reference_cache_dir)), root
        )

    ffmpeg = _resolve_executable(ffmpeg_path, "ffmpeg")
    ffprobe = _resolve_executable(ffprobe_path, "ffprobe")
    inputs = _validate_fixed_inputs(
        root=root,
        episode=episode,
        baseline_dir=baseline_dir,
        reference_corpus=reference_corpus,
        ffmpeg=ffmpeg,
        ffprobe=ffprobe,
    )
    build_context = {
        **inputs,
        "root": root,
        "episode": episode,
        "baseline_dir": baseline_dir,
        "output": output,
        "reference_corpus": reference_corpus,
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
        "fetch_flag_requested": bool(fetch_missing_references),
        "reference_cache_observed": reference_cache_observed,
    }

    stage_one = output.parent / f".{output.name}.native-cover-pass1-{uuid.uuid4().hex}"
    stage_two = output.parent / f".{output.name}.native-cover-pass2-{uuid.uuid4().hex}"
    try:
        first = _build_once(stage=stage_one, context=build_context)
        second = _build_once(stage=stage_two, context=build_context)
        if first["core_digest"] != second["core_digest"]:
            raise Out07NativeCoverError(
                "fixed-input core digest changed between builds"
            )
        if first["package_digest"] != second["package_digest"]:
            raise Out07NativeCoverError(
                "fixed-input package digest changed between builds"
            )
        if first["file_hashes"] != second["file_hashes"]:
            raise Out07NativeCoverError(
                "fixed-input package bytes changed between builds"
            )
        if verify_determinism is False:
            # The active route always verifies twice; retain the flag only as a
            # compatibility/readback signal rather than weakening the contract.
            pass

        _promote_validated_package(stage=stage_two, output=output)
    finally:
        for path in (stage_one, stage_two):
            if path.exists():
                _safe_remove_internal(path, expected_parent=output.parent)

    return {
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "output_dir": output,
        "index_path": output / "index.html",
        "readback_path": output / "poster_direction_readback.json",
        "manifest_path": output / "combined_review_manifest.json",
        "deterministic_core_digest": second["core_digest"],
        "package_digest": second["package_digest"],
        "reference_evidence_digest": inputs["reference_digest"],
    }


def _promote_validated_package(*, stage: Path, output: Path) -> None:
    """Promote one stage and restore the prior review on any validation error."""

    backup: Path | None = None
    if output.exists():
        backup = output.parent / f".{output.name}.backup-{uuid.uuid4().hex}"
        output.replace(backup)
    failed_promotion: Path | None = None
    try:
        stage.replace(output)
        _validate_promoted_package(output)
    except Exception:
        if output.exists():
            failed_promotion = (
                output.parent / f".{output.name}.failed-{uuid.uuid4().hex}"
            )
            output.replace(failed_promotion)
        if backup is not None and backup.exists():
            backup.replace(output)
            backup = None
        if failed_promotion is not None and failed_promotion.exists():
            _safe_remove_internal(failed_promotion, expected_parent=output.parent)
        raise
    if backup is not None and backup.exists():
        _safe_remove_internal(backup, expected_parent=output.parent)


def _build_once(*, stage: Path, context: dict[str, Any]) -> dict[str, Any]:
    from PIL import Image

    stage.mkdir(parents=False, exist_ok=False)
    baseline_source: Path = context["baseline_video"]
    baseline_copy = stage / "reinstantiated_baseline.mp4"
    shutil.copyfile(baseline_source, baseline_copy)
    _assert_file_identity(
        baseline_copy,
        expected_sha256=ACCEPTED_BASELINE_SHA256,
        expected_bytes=ACCEPTED_BASELINE_BYTES,
        label="accepted baseline copy",
    )

    frame = _decode_rgb_frame(
        context["ffmpeg"], baseline_source, RECOMMENDED_BASELINE_SECONDS, 1080, 1920
    )
    cover = stage / "native_shorts_cover_1080x1920.png"
    Image.frombytes("RGB", (1080, 1920), frame).save(
        cover, format="PNG", optimize=False, compress_level=9
    )
    source_frame = stage / "mapped_source_frame_1920x1080.png"
    Image.frombytes(
        "RGB",
        (1920, 1080),
        _decode_rgb_frame(
            context["ffmpeg"],
            context["source_video"],
            RECOMMENDED_SOURCE_SECONDS,
            1920,
            1080,
        ),
    ).save(source_frame, format="PNG", optimize=False, compress_level=9)
    _write_preview_images(cover=cover, stage=stage)

    baseline_fingerprint = _frame_fingerprint(
        context["ffmpeg"], baseline_source, RECOMMENDED_BASELINE_SECONDS
    )
    source_fingerprint = _frame_fingerprint(
        context["ffmpeg"], context["source_video"], RECOMMENDED_SOURCE_SECONDS
    )
    if baseline_fingerprint != BASELINE_FRAME_FINGERPRINT_SHA256:
        raise Out07NativeCoverError("accepted-baseline frame fingerprint changed")
    if source_fingerprint != SOURCE_FRAME_FINGERPRINT_SHA256:
        raise Out07NativeCoverError("mapped source-frame fingerprint changed")

    logical_output: Path = context["output"]
    baseline_acceptance = _baseline_acceptance_payload(logical_output)
    baseline_readback = _baseline_readback_payload(context, logical_output)
    media_receipt = _media_revision_payload(context)
    reference_observation = _reference_observation_payload(context)
    publish_draft = _publish_draft_payload(cover, logical_output)
    legacy_evidence = _legacy_evidence_payload()
    operator_readback = _operator_readback_payload(
        context=context,
        logical_output=logical_output,
        cover=cover,
        source_frame=source_frame,
        baseline_copy=baseline_copy,
        publish_draft=publish_draft,
    )
    poster_readback = _poster_readback_payload(
        context=context,
        logical_output=logical_output,
        cover=cover,
        source_frame=source_frame,
        baseline_copy=baseline_copy,
        publish_draft=publish_draft,
    )

    payloads = {
        "baseline_acceptance.json": baseline_acceptance,
        "baseline_readback.json": baseline_readback,
        "media_revision_receipt.json": media_receipt,
        "reference_observation_readback.json": reference_observation,
        "publish_draft.json": publish_draft,
        "superseded_poster_evidence.json": legacy_evidence,
        "operator_delivery_readback.json": operator_readback,
        "poster_direction_readback.json": poster_readback,
    }
    for name, payload in payloads.items():
        _write_json(stage / name, payload)

    _write_text(stage / "index.html", _render_html(poster_readback, publish_draft))
    _write_text(stage / "open_preview.ps1", _open_script())
    _write_text(stage / "serve_preview.ps1", _serve_script())

    core_names = (
        "reinstantiated_baseline.mp4",
        "native_shorts_cover_1080x1920.png",
        "mapped_source_frame_1920x1080.png",
        "cover_list_preview.jpg",
        "cover_center_4x5.jpg",
        "cover_shorts_ui_overlay_preview.jpg",
        *payloads.keys(),
    )
    package_names = (*core_names, "index.html", "open_preview.ps1", "serve_preview.ps1")
    core_digest = _named_file_digest(stage, core_names)
    package_digest = _named_file_digest(stage, package_names)
    deterministic_core = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "fixed_input_build_count": 2,
        "core_file_names": list(core_names),
        "core_sha256": core_digest,
        "package_file_names": list(package_names),
        "package_sha256": package_digest,
    }
    determinism_receipt = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "same_fixed_input_build_count": 2,
        "first_build_core_sha256": core_digest,
        "second_build_core_sha256": core_digest,
        "core_digests_match": True,
        "first_build_package_sha256": package_digest,
        "second_build_package_sha256": package_digest,
        "package_digests_match": True,
        "manifest_validation_required": True,
        "verification_status": "passed",
    }
    _write_json(stage / "deterministic_core_readback.json", deterministic_core)
    _write_json(stage / "determinism_receipt.json", determinism_receipt)
    _write_manifest(stage, core_digest=core_digest, package_digest=package_digest)
    file_hashes = _all_file_hashes(stage)
    return {
        "core_digest": core_digest,
        "package_digest": package_digest,
        "file_hashes": file_hashes,
    }


def _baseline_acceptance_payload(logical_output: Path) -> dict[str, Any]:
    accepted_scope = [
        "content_and_narrative",
        "timing_and_tempo",
        "cut_continuity",
        "audio_video_continuity",
        "subtitle_timing_and_readability",
        "visual_integrity",
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "accepted_by": "Planner007",
        "acceptance_date": ACCEPTANCE_DATE,
        "acceptance_basis": "explicit_user_acceptance_of_current_reinstantiated_baseline",
        "accepted_baseline": {
            "path": _logical_path(logical_output, "reinstantiated_baseline.mp4"),
            "sha256": ACCEPTED_BASELINE_SHA256,
            "byte_size": ACCEPTED_BASELINE_BYTES,
            "duration_seconds": ACCEPTED_BASELINE_DURATION_SECONDS,
            "accepted_scope": accepted_scope,
            "human_accepted": True,
        },
        "historical_acceptance_inheritance": {
            "byte_identical_to_historical_out06": False,
            "historical_out06_acceptance_inherited": False,
        },
        "not_accepted": [
            "historical_out06_output",
            "rights_clearance",
            "production_acceptance",
            "public_or_publishing_acceptance",
            "upload_or_visibility",
            "made_for_kids",
        ],
    }


def _baseline_readback_payload(
    context: dict[str, Any], logical_output: Path
) -> dict[str, Any]:
    probe = context["baseline_probe"]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "component_id": "accepted_reinstantiated_baseline_byte_copy",
        "path": _logical_path(logical_output, "reinstantiated_baseline.mp4"),
        "sha256": ACCEPTED_BASELINE_SHA256,
        "byte_size": ACCEPTED_BASELINE_BYTES,
        "media": probe,
        "copy_integrity": {
            "source_path": _relative(context["baseline_video"], context["root"]),
            "source_sha256": ACCEPTED_BASELINE_SHA256,
            "byte_identical": True,
            "rerendered": False,
            "remuxed": False,
            "transcoded": False,
            "subtitle_changed": False,
            "audio_changed": False,
            "edit_or_timing_changed": False,
        },
        "explicit_human_acceptance": {
            "accepted": True,
            "accepted_by": "Planner007",
            "accepted_on": ACCEPTANCE_DATE,
            "historical_acceptance_inherited": False,
        },
    }


def _media_revision_payload(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "episode_id": EPISODE_ID,
        "provider": "youtube",
        "provider_id": SOURCE_PROVIDER_ID,
        "canonical_source_url": f"https://www.youtube.com/watch?v={SOURCE_PROVIDER_ID}",
        "source_video_sha256": SOURCE_VIDEO_SHA256,
        "accepted_baseline_sha256": ACCEPTED_BASELINE_SHA256,
        "source_identity_matches_qualified_revision": True,
        "source_to_baseline_frame_mapping": {
            "baseline_seconds": RECOMMENDED_BASELINE_SECONDS,
            "source_seconds": RECOMMENDED_SOURCE_SECONDS,
            "cut_id": "cut_003",
            "formula": "22.606 + (11.930 - 11.678)",
            "baseline_frame_fingerprint_sha256": BASELINE_FRAME_FINGERPRINT_SHA256,
            "source_frame_fingerprint_sha256": SOURCE_FRAME_FINGERPRINT_SHA256,
            "fingerprint_profile": FINGERPRINT_PROFILE,
        },
        "qualification_status": "readback_from_qualified_current_revision",
        "remote_acquisition_attempted": False,
    }


def _reference_observation_payload(context: dict[str, Any]) -> dict[str, Any]:
    corpus = context["reference_payload"]
    references = corpus.get("references")
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "tracked_corpus_path": _relative(context["reference_corpus"], context["root"]),
        "tracked_corpus_sha256": context["reference_digest"],
        "reference_count": len(references) if isinstance(references, list) else None,
        "role": "historical_direction_context_only",
        "third_party_pixels_loaded_or_used": False,
        "new_remote_crawl_attempted": False,
        "fetch_flag_requested_but_not_executed": context["fetch_flag_requested"],
        "reference_cache_argument_observed": context["reference_cache_observed"],
    }


def _publish_draft_payload(cover: Path, logical_output: Path) -> dict[str, Any]:
    copy_plan = copy.deepcopy(EPISODE_COPY_PLAN)
    payload = {
        # Preserve the existing OUT-07 publish-draft contract because this file
        # is a downstream operator surface.  Native-cover fields are additive.
        "schema_version": "clippipegen.out07.publish_draft.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": EPISODE_ID,
        "status": "internal_operator_draft_native_cover_pending_human_acceptance",
        "language": "ja",
        "title": copy_plan["title"],
        "description": "\n".join(copy_plan["description_lines"]),
        "tags": copy_plan["tags"],
        "evidence_trace": copy_plan["evidence_trace"],
        "video": {
            "path": _logical_path(logical_output, "reinstantiated_baseline.mp4"),
            "sha256": ACCEPTED_BASELINE_SHA256,
            "human_accepted": True,
            "accepted_by": "Planner007",
            "accepted_on": ACCEPTANCE_DATE,
            "byte_copy_only": True,
        },
        "recommended_cover": {
            "path": _logical_path(logical_output, cover.name),
            "sha256": _sha256(cover),
            "baseline_seconds": RECOMMENDED_BASELINE_SECONDS,
            "source_seconds": RECOMMENDED_SOURCE_SECONDS,
            "subtitle_id": RECOMMENDED_SUBTITLE_ID,
            "selection_status": "recommended_pending_human_acceptance",
            "selected_by_human": False,
            "source_frame_only": True,
            "poster_added_abstract_background": False,
            "poster_added_auxiliary_text": False,
            "source_frame_fingerprint": {
                "profile": FINGERPRINT_PROFILE,
                "baseline_sha256": BASELINE_FRAME_FINGERPRINT_SHA256,
                "mapped_source_sha256": SOURCE_FRAME_FINGERPRINT_SHA256,
            },
        },
        "selected_thumbnail": None,
        "poster_decision_status": "human_selection_required",
        "rejected_thumbnail_ids": ["context", "tension", "payoff"],
        "legacy_thumbnail_status": "user_rejected_not_regenerated",
        "source_attribution_status": "operator_decision_required",
        "source_title": None,
        "source_url": None,
        "operator_copy_ready": True,
        "publish_ready": False,
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "public_or_publishing_acceptance": False,
        "rights_status": "pending",
        "publish_attempted": False,
        "upload_attempted": False,
        "thumbnail_upload_attempted": False,
        "metadata_update_attempted": False,
        "visibility_update_attempted": False,
        "visibility_change_attempted": False,
        "external_system_mutation_attempted": False,
        "visibility": "operator_decision_required",
        "made_for_kids": "operator_decision_required",
        "made_for_kids_change_attempted": False,
        "scheduled_at": None,
    }
    _validate_publish_draft_payload(payload)
    return payload


def _metadata_readback(publish_draft: dict[str, Any]) -> dict[str, Any]:
    copy_payload = {
        "title": publish_draft["title"],
        "description": publish_draft["description"],
        "tags": publish_draft["tags"],
        "evidence_trace": publish_draft["evidence_trace"],
    }
    return {
        **copy_payload,
        "canonical_sha256": _canonical_digest(copy_payload),
        "changed_in_this_route": False,
    }


def _validate_publish_draft_payload(payload: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "artifact_id",
        "episode_id",
        "status",
        "language",
        "title",
        "description",
        "tags",
        "evidence_trace",
        "video",
        "recommended_cover",
        "selected_thumbnail",
        "poster_decision_status",
        "source_attribution_status",
        "source_title",
        "source_url",
        "operator_copy_ready",
        "publish_ready",
        "production_acceptance",
        "production_subtitle_design_acceptance",
        "public_or_publishing_acceptance",
        "rights_status",
        "upload_attempted",
        "thumbnail_upload_attempted",
        "metadata_update_attempted",
        "visibility_update_attempted",
        "visibility",
        "made_for_kids",
        "scheduled_at",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise Out07NativeCoverError(f"publish draft missing required fields: {missing}")
    if payload["schema_version"] != "clippipegen.out07.publish_draft.v0":
        raise Out07NativeCoverError("publish draft compatibility schema changed")
    if payload["selected_thumbnail"] is not None:
        raise Out07NativeCoverError("cover must remain pending human selection")
    if payload["poster_decision_status"] != "human_selection_required":
        raise Out07NativeCoverError("cover decision must remain human-gated")
    closed = {
        "publish_ready": False,
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "public_or_publishing_acceptance": False,
        "rights_status": "pending",
        "upload_attempted": False,
        "thumbnail_upload_attempted": False,
        "metadata_update_attempted": False,
        "visibility_update_attempted": False,
        "scheduled_at": None,
    }
    if any(payload.get(key) != value for key, value in closed.items()):
        raise Out07NativeCoverError("publish draft gate or attempt readback changed")


def _legacy_evidence_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "current_review_candidates": [
            {
                "candidate_id": "A",
                "sha256": "168da37103dc141434a27828bfafc8713c8ee225ae6e5524b47ca0f0f0675554",
                "status": "superseded_by_user_short_context_reframe",
                "quality_rejection": False,
                "return_for_selection": False,
            },
            {
                "candidate_id": "B",
                "sha256": "92b71c11c7517616a1f6f1203bb2653d85b158c83e54bd27b704b75fe763f7e5",
                "status": "superseded_by_user_short_context_reframe",
                "quality_rejection": False,
                "return_for_selection": False,
            },
            {
                "candidate_id": "C",
                "sha256": "42961ee686ecd66a4c248bdeac281f8ffd8f4a605ecb2ac8f3be7a10c514e6d7",
                "status": "superseded_by_user_short_context_reframe",
                "quality_rejection": False,
                "return_for_selection": False,
            },
        ],
        "earlier_supervisor_reframe_generation": [
            {
                "candidate_id": "A",
                "sha256": "7a314825a0be95d48801bc0d648615b81a340884c24273fa76abbf18395a3720",
            },
            {
                "candidate_id": "B",
                "sha256": "8ab9e01f81490a3571fa60f59041da73c7122d76673ad8409ecbc7e20d57eab2",
            },
            {
                "candidate_id": "C",
                "sha256": "8d2f05a9fc31f25bd9b8cc20702766c0ea3cc902717efa451837aaec3609ccb2",
            },
        ],
        "historical_operator_directions": {
            "direction_ids": ["context", "tension", "payoff"],
            "status": "user_rejected",
            "selected_thumbnail": None,
            "return_for_selection": False,
        },
    }


def _operator_readback_payload(
    *,
    context: dict[str, Any],
    logical_output: Path,
    cover: Path,
    source_frame: Path,
    baseline_copy: Path,
    publish_draft: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "historical_predecessor_artifact_id": HISTORICAL_OPERATOR_ARTIFACT_ID,
        "episode_id": EPISODE_ID,
        "accepted_baseline": {
            "path": _logical_path(logical_output, baseline_copy.name),
            "sha256": _sha256(baseline_copy),
            "byte_size": baseline_copy.stat().st_size,
            "duration_seconds": ACCEPTED_BASELINE_DURATION_SECONDS,
            "accepted_by": "Planner007",
            "accepted_on": ACCEPTANCE_DATE,
            "byte_copy_only": True,
        },
        "recommended_cover": publish_draft["recommended_cover"],
        "source_comparison": {
            "path": _logical_path(logical_output, source_frame.name),
            "sha256": _sha256(source_frame),
            "source_seconds": RECOMMENDED_SOURCE_SECONDS,
            "source_video_sha256": SOURCE_VIDEO_SHA256,
            "frame_fingerprint_sha256": SOURCE_FRAME_FINGERPRINT_SHA256,
            "fingerprint_profile": FINGERPRINT_PROFILE,
        },
        "metadata": _metadata_readback(publish_draft),
        "selected_thumbnail": None,
        "selected_by_human": False,
        "publish_ready": False,
        "gates": _closed_gates(),
        "attempts": _attempt_flags(),
        "next_state_boundaries": {
            "H1": "final cover acceptance, closure/full suite, and main decision",
            "H2": "real other-host recovery with conditional caption reacquisition",
            "H3": "rights, production, public, publishing, or external-system work",
        },
        "reference_evidence_sha256": context["reference_digest"],
    }


def _poster_readback_payload(
    *,
    context: dict[str, Any],
    logical_output: Path,
    cover: Path,
    source_frame: Path,
    baseline_copy: Path,
    publish_draft: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "episode_id": EPISODE_ID,
        "review_question": REVIEW_QUESTION,
        "review_question_count": 1,
        "review_scope": "native_shorts_cover_direction_only",
        "baseline": {
            "path": _logical_path(logical_output, baseline_copy.name),
            "sha256": _sha256(baseline_copy),
            "human_accepted": True,
            "changed": False,
        },
        "recommended_cover": {
            **publish_draft["recommended_cover"],
            "format": "PNG",
            "dimensions": [1080, 1920],
            "pixel_source": "decoded_frame_from_accepted_vertical_baseline",
            "existing_burn_in_subtitle_only": True,
            "added_text_or_graphics": False,
            "background_replaced": False,
            "mask_or_cutout_used": False,
            "third_party_pixels_used": False,
            "baseline_frame_fingerprint": {
                "profile": FINGERPRINT_PROFILE,
                "sha256": BASELINE_FRAME_FINGERPRINT_SHA256,
                "byte_count": 172_800,
            },
            "mapped_source_frame_fingerprint": {
                "profile": FINGERPRINT_PROFILE,
                "sha256": SOURCE_FRAME_FINGERPRINT_SHA256,
                "byte_count": 172_800,
            },
        },
        "preview_derivatives": [
            {
                "role": "shorts_list_scale_preview",
                "path": _logical_path(logical_output, "cover_list_preview.jpg"),
                "dimensions": [405, 720],
                "preview_only": True,
            },
            {
                "role": "center_4_5_crop_preview",
                "path": _logical_path(logical_output, "cover_center_4x5.jpg"),
                "dimensions": [864, 1080],
                "preview_only": True,
                "official_platform_guarantee": False,
            },
            {
                "role": "shorts_ui_overlay_approximation",
                "path": _logical_path(
                    logical_output, "cover_shorts_ui_overlay_preview.jpg"
                ),
                "dimensions": [405, 720],
                "preview_only": True,
                "generic_ui_shapes_only": True,
                "official_platform_guarantee": False,
            },
        ],
        "source_comparison": {
            "path": _logical_path(logical_output, source_frame.name),
            "sha256": _sha256(source_frame),
            "dimensions": [1920, 1080],
            "source_seconds": RECOMMENDED_SOURCE_SECONDS,
            "source_video_sha256": SOURCE_VIDEO_SHA256,
            "frame_fingerprint_sha256": SOURCE_FRAME_FINGERPRINT_SHA256,
            "fingerprint_profile": FINGERPRINT_PROFILE,
            "unmodified_source_frame": True,
        },
        "internal_frame_survey": {
            "candidate_count": len(FRAME_SURVEY),
            "candidate_limit": 3,
            "alternatives_exported": False,
            "items": [dict(item) for item in FRAME_SURVEY],
        },
        "metadata": _metadata_readback(publish_draft),
        "selected_by_human": False,
        "publish_ready": False,
        "gates": _closed_gates(),
        "attempts": _attempt_flags(),
        "superseded_evidence_path": _logical_path(
            logical_output, "superseded_poster_evidence.json"
        ),
        "reference_evidence_sha256": context["reference_digest"],
    }


def _closed_gates() -> dict[str, Any]:
    return {
        "cover_human_acceptance": {"status": "closed", "approved": False},
        "rights": {"status": "closed", "approved": False, "rights_status": "pending"},
        "production": {"status": "closed", "approved": False},
        "public_or_publishing": {"status": "closed", "approved": False},
        "upload_visibility": {"status": "closed", "approved": False},
        "made_for_kids": {"status": "closed", "decision": None},
    }


def _attempt_flags() -> dict[str, bool]:
    return {
        "publish_attempted": False,
        "upload_attempted": False,
        "thumbnail_upload_attempted": False,
        "metadata_update_attempted": False,
        "visibility_update_attempted": False,
        "visibility_change_attempted": False,
        "made_for_kids_change_attempted": False,
        "external_system_mutation_attempted": False,
    }


def _render_html(readback: dict[str, Any], publish_draft: dict[str, Any]) -> str:
    metadata = _metadata_readback(publish_draft)
    tags = " / ".join(escape(str(tag)) for tag in metadata["tags"])
    description = escape(str(metadata["description"]))
    old_rows = "".join(
        f"<tr><td>{item}</td><td>superseded_by_user_short_context_reframe</td>"
        "<td>品質否定ではなくShorts文脈への再フレーム</td></tr>"
        for item in ("A", "B", "C")
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,">
<title>OUT-07 映像由来Shorts cover確認</title>
<style>
:root {{ color-scheme:dark; font-family:"Yu Gothic UI","Noto Sans JP",sans-serif; background:#0a0c10; color:#f3f4f6; }}
* {{ box-sizing:border-box; }} body {{ margin:0; overflow-x:hidden; }}
main {{ width:min(1040px,100%); margin:auto; padding:24px; overflow-wrap:anywhere; }}
h1 {{ font-size:clamp(1.6rem,4vw,2.6rem); margin:.25rem 0 .6rem; }} h2 {{ margin-top:0; }}
.eyebrow {{ color:#7dd3fc; font-weight:800; letter-spacing:.1em; }} .lead {{ color:#cbd5e1; max-width:78ch; }}
section,details {{ margin-top:22px; padding:18px; border:1px solid #334155; border-radius:14px; background:#111827; }}
.visual {{ display:flex; justify-content:center; }} .preview-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,405px)); gap:16px; justify-content:center; }}
.preview-grid figure {{ margin:0; }} .preview-grid figcaption {{ margin-top:8px; color:#94a3b8; text-align:center; }} img,video {{ display:block; max-width:100%; height:auto; border-radius:12px; background:#000; }}
.full img,.compare video {{ width:min(405px,100%); }} .compare img {{ width:min(640px,100%); }} .crop img {{ width:min(432px,100%); }}
.question {{ border-color:#38bdf8; background:#0c2535; font-size:1.05rem; }}
pre {{ white-space:pre-wrap; margin:0; font:inherit; color:#e2e8f0; }} code {{ color:#bae6fd; }}
button {{ margin:.5rem 0; padding:.55rem .8rem; border:0; border-radius:8px; cursor:pointer; }}
table {{ width:100%; border-collapse:collapse; }} th,td {{ padding:8px; border-bottom:1px solid #334155; text-align:left; vertical-align:top; }}
summary {{ cursor:pointer; font-weight:800; }} .muted {{ color:#94a3b8; }}
@media(max-width:620px) {{ main {{ padding:14px; }} section,details {{ padding:14px; }} }}
</style></head><body><main>
<div class="eyebrow">OUT-07 / NATIVE SHORTS COVER</div>
<h1>受理済み動画の一場面を、そのまま一覧用coverへ</h1>
<p class="lead">受理済みの縦動画から、既存の焼き込み字幕が読める一瞬だけを抽出しました。背景差し替え、人物切り抜き、見出し・ロゴ・CTAなどの追加はありません。</p>

<section><h2>1. Shorts一覧サイズ</h2><div class="preview-grid"><figure><img src="cover_list_preview.jpg" width="405" height="720" alt="Shorts一覧サイズの推奨cover"><figcaption>一覧縮小</figcaption></figure><figure><img src="cover_shorts_ui_overlay_preview.jpg" width="405" height="720" alt="Shorts UI重なりの内部近似"><figcaption>UI重なり近似（previewのみ）</figcaption></figure></div></section>

<section class="full"><h2>2. 9:16フルフレーム</h2><div class="visual"><img src="native_shorts_cover_1080x1920.png" width="540" height="960" alt="受理済み動画由来の9対16フルフレーム"></div></section>

<section class="crop"><h2>3. 中央4:5クロップ確認</h2><p class="muted">一覧面で中央寄せクロップされた場合の内部ヒューリスティックです。公式表示保証ではありません。</p><div class="visual"><img src="cover_center_4x5.jpg" width="432" height="540" alt="中央4対5クロップ確認"></div></section>

<section class="compare"><h2>4. source映像との照合</h2><p>横長sourceの <code>{RECOMMENDED_SOURCE_SECONDS:.3f}s</code> と、受理済み縦動画の対応時刻 <code>{RECOMMENDED_BASELINE_SECONDS:.3f}s</code> を読み戻します。coverは下の受理済み動画側からデコードしており、source画像も比較用に無加工で抽出しています。</p><div class="preview-grid"><figure><img src="mapped_source_frame_1920x1080.png" width="640" height="360" alt="対応するsource映像フレーム"><figcaption>source {RECOMMENDED_SOURCE_SECONDS:.3f}s（無加工比較用）</figcaption></figure><figure><video id="accepted-baseline" controls preload="metadata" playsinline src="reinstantiated_baseline.mp4#t={RECOMMENDED_BASELINE_SECONDS:.3f}"></video><figcaption>受理済み縦動画 {RECOMMENDED_BASELINE_SECONDS:.3f}s</figcaption></figure></div></section>

<section><h2>5. 現在のタイトル・説明・タグ</h2>
<h3>タイトル</h3><pre id="meta-title">{escape(str(metadata["title"]))}</pre><button data-copy="meta-title">タイトルをコピー</button>
<h3>説明</h3><pre id="meta-description">{description}</pre><button data-copy="meta-description">説明をコピー</button>
<h3>タグ</h3><pre id="meta-tags">{tags}</pre><button data-copy="meta-tags">タグをコピー</button>
<p class="muted">既存の自然文案を変更せず読み戻しています。この画面ではmetadataの再承認を求めません。</p></section>

<section><h2>6. 受理済みbaselineの読戻し</h2><p>SHA-256: <code>{ACCEPTED_BASELINE_SHA256}</code></p><p>{ACCEPTED_BASELINE_DURATION_SECONDS:.6f}s / 1080x1920 / Planner007が{ACCEPTANCE_DATE}に内容・テンポ・カット連続性・A/V連続性・字幕・映像完全性を受理。</p><p class="muted">この受理はrights、production、public/publishing、upload、visibility、made-for-kidsには波及しません。</p></section>

<section class="question"><h2>今回の確認</h2><p>{escape(REVIEW_QUESTION)}</p></section>

<details><summary>由来・閉じたgate・旧A/B/C</summary>
<p>推奨cover: baseline {RECOMMENDED_BASELINE_SECONDS:.3f}s / source {RECOMMENDED_SOURCE_SECONDS:.3f}s / <code>{RECOMMENDED_SUBTITLE_ID}</code>。cover選択はまだ人手未確定です。</p>
<p>rights=pending / production=false / public=false / publish_ready=false / upload_attempted=false / external mutation=false</p>
<table><thead><tr><th>旧候補</th><th>状態</th><th>扱い</th></tr></thead><tbody>{old_rows}</tbody></table>
<p>さらに前のcontext / tension / payoffは <code>user_rejected</code> の履歴証跡として分離保持し、再提示しません。</p>
</details>
</main><script>
const video=document.getElementById('accepted-baseline');
video.addEventListener('loadedmetadata',()=>{{ video.currentTime={RECOMMENDED_BASELINE_SECONDS:.3f}; }});
document.querySelectorAll('button[data-copy]').forEach((button)=>{{button.addEventListener('click',async()=>{{
  const text=document.getElementById(button.dataset.copy).innerText;
  await navigator.clipboard.writeText(text); button.textContent='コピーしました';
}});}});
</script></body></html>"""


def _write_preview_images(*, cover: Path, stage: Path) -> None:
    from PIL import Image, ImageDraw

    with Image.open(cover) as source:
        rgb = source.convert("RGB")
        list_preview = rgb.resize((405, 720), Image.Resampling.LANCZOS)
        list_preview.save(
            stage / "cover_list_preview.jpg",
            format="JPEG",
            quality=92,
            subsampling=0,
            optimize=False,
            progressive=False,
        )
        ui_preview = list_preview.copy()
        draw = ImageDraw.Draw(ui_preview, "RGBA")
        for center_y in (365, 425, 485):
            draw.ellipse(
                (357, center_y - 18, 393, center_y + 18),
                fill=(0, 0, 0, 105),
                outline=(255, 255, 255, 220),
                width=2,
            )
        draw.rounded_rectangle((18, 664, 282, 702), radius=8, fill=(0, 0, 0, 115))
        draw.rounded_rectangle((30, 676, 218, 682), radius=3, fill=(255, 255, 255, 215))
        draw.rounded_rectangle((30, 689, 162, 695), radius=3, fill=(255, 255, 255, 150))
        ui_preview.save(
            stage / "cover_shorts_ui_overlay_preview.jpg",
            format="JPEG",
            quality=92,
            subsampling=0,
            optimize=False,
            progressive=False,
        )
        top = (rgb.height - 1350) // 2
        crop = rgb.crop((0, top, 1080, top + 1350)).resize(
            (864, 1080), Image.Resampling.LANCZOS
        )
        crop.save(
            stage / "cover_center_4x5.jpg",
            format="JPEG",
            quality=92,
            subsampling=0,
            optimize=False,
            progressive=False,
        )


def _validate_fixed_inputs(
    *,
    root: Path,
    episode: Path,
    baseline_dir: Path,
    reference_corpus: Path,
    ffmpeg: str,
    ffprobe: str,
) -> dict[str, Any]:
    baseline_video = baseline_dir / "assets" / "reinstantiated_baseline.mp4"
    source_video = episode / "materials" / "src_video_jp_pilot01" / "source_video.mp4"
    _require_file(baseline_video, "accepted baseline")
    _require_file(source_video, "qualified source video")
    _require_file(reference_corpus, "tracked reference corpus")
    _assert_file_identity(
        baseline_video,
        expected_sha256=ACCEPTED_BASELINE_SHA256,
        expected_bytes=ACCEPTED_BASELINE_BYTES,
        label="accepted baseline",
    )
    if _sha256(source_video) != SOURCE_VIDEO_SHA256:
        raise Out07NativeCoverError("qualified source video SHA-256 changed")
    probe = _probe_media(ffprobe, baseline_video)
    if probe["width"] != 1080 or probe["height"] != 1920:
        raise Out07NativeCoverError("accepted baseline dimensions changed")
    if (
        abs(float(probe["duration_seconds"]) - ACCEPTED_BASELINE_DURATION_SECONDS)
        > 0.01
    ):
        raise Out07NativeCoverError("accepted baseline duration changed")
    try:
        reference_payload = json.loads(reference_corpus.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Out07NativeCoverError(
            "tracked reference corpus is not readable JSON"
        ) from exc
    if not isinstance(reference_payload, dict):
        raise Out07NativeCoverError("tracked reference corpus must be a JSON object")
    return {
        "baseline_video": baseline_video,
        "source_video": source_video,
        "baseline_probe": probe,
        "reference_payload": reference_payload,
        "reference_digest": _sha256(reference_corpus),
        "input_paths": {
            "accepted_baseline": _relative(baseline_video, root),
            "qualified_source_video": _relative(source_video, root),
            "tracked_reference_corpus": _relative(reference_corpus, root),
        },
    }


def _probe_media(ffprobe: str, path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,codec_name,width,height,avg_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload = json.loads(result.stdout)
    streams = payload.get("streams") or []
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    if not isinstance(video, dict) or not isinstance(audio, dict):
        raise Out07NativeCoverError("accepted baseline must contain video and audio")
    frame_rate = str(video.get("avg_frame_rate") or "0/1")
    numerator, denominator = frame_rate.split("/", maxsplit=1)
    return {
        "duration_seconds": float(payload["format"]["duration"]),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": float(numerator) / float(denominator),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"),
        "stream_count": len(streams),
    }


def _decode_rgb_frame(
    ffmpeg: str, path: Path, seconds: float, width: int, height: int
) -> bytes:
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-v",
            "error",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-an",
            "-frames:v",
            "1",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ],
        check=True,
        capture_output=True,
    )
    expected = width * height * 3
    if len(result.stdout) != expected:
        raise Out07NativeCoverError(
            f"decoded cover frame byte count changed: expected {expected}, got {len(result.stdout)}"
        )
    return result.stdout


def _frame_fingerprint(ffmpeg: str, path: Path, seconds: float) -> str:
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-v",
            "error",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-an",
            "-frames:v",
            "1",
            "-vf",
            "scale=320:180:flags=bilinear",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ],
        check=True,
        capture_output=True,
    )
    if len(result.stdout) != 320 * 180 * 3:
        raise Out07NativeCoverError("canonical frame fingerprint byte count changed")
    return hashlib.sha256(result.stdout).hexdigest()


def _write_manifest(stage: Path, *, core_digest: str, package_digest: str) -> None:
    files = [
        {
            "path": path.relative_to(stage).as_posix(),
            "byte_size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted(item for item in stage.rglob("*") if item.is_file())
        if path.name != "combined_review_manifest.json"
    ]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "deterministic_core_sha256": core_digest,
        "deterministic_package_sha256": package_digest,
        "file_count": len(files),
        "files": files,
    }
    payload["manifest_self_integrity"] = {
        "method": "canonical_sha256_of_manifest_without_manifest_self_integrity",
        "sha256": _canonical_digest(payload),
        "status": "passed",
    }
    _write_json(stage / "combined_review_manifest.json", payload)


def validate_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    files = payload.get("files")
    if not isinstance(files, list):
        raise Out07NativeCoverError("manifest files must be an array")
    if payload.get("file_count") != len(files):
        raise Out07NativeCoverError("manifest file_count mismatch")
    manifest_names: set[str] = set()
    for row in files:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise Out07NativeCoverError("manifest row is invalid")
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise Out07NativeCoverError(f"unsafe manifest path: {row['path']}")
        normalized = relative.as_posix()
        if normalized in manifest_names:
            raise Out07NativeCoverError(f"duplicate manifest path: {normalized}")
        manifest_names.add(normalized)
        file_path = root / relative
        _require_file(file_path, f"manifest file {row['path']}")
        if (
            file_path.stat().st_size != row["byte_size"]
            or _sha256(file_path) != row["sha256"]
        ):
            raise Out07NativeCoverError(f"manifest mismatch: {row['path']}")
    actual_names = {
        item.relative_to(root).as_posix()
        for item in root.rglob("*")
        if item.is_file() and item.resolve() != manifest_path.resolve()
    }
    if actual_names != manifest_names:
        raise Out07NativeCoverError(
            "manifest inventory mismatch: "
            f"missing={sorted(actual_names - manifest_names)} "
            f"unexpected={sorted(manifest_names - actual_names)}"
        )
    integrity = payload.get("manifest_self_integrity")
    if not isinstance(integrity, dict):
        raise Out07NativeCoverError("manifest self-integrity record missing")
    expected = integrity.get("sha256")
    unsigned = dict(payload)
    unsigned.pop("manifest_self_integrity", None)
    if _canonical_digest(unsigned) != expected:
        raise Out07NativeCoverError("manifest self-integrity mismatch")
    return payload


def _validate_promoted_package(output: Path) -> None:
    required = {
        "reinstantiated_baseline.mp4",
        "native_shorts_cover_1080x1920.png",
        "mapped_source_frame_1920x1080.png",
        "cover_list_preview.jpg",
        "cover_center_4x5.jpg",
        "cover_shorts_ui_overlay_preview.jpg",
        "baseline_acceptance.json",
        "baseline_readback.json",
        "media_revision_receipt.json",
        "reference_observation_readback.json",
        "publish_draft.json",
        "superseded_poster_evidence.json",
        "operator_delivery_readback.json",
        "poster_direction_readback.json",
        "deterministic_core_readback.json",
        "determinism_receipt.json",
        "combined_review_manifest.json",
        "index.html",
        "open_preview.ps1",
        "serve_preview.ps1",
    }
    actual = {path.name for path in output.iterdir() if path.is_file()}
    if actual != required:
        raise Out07NativeCoverError(
            f"promoted package inventory changed: missing={sorted(required - actual)} "
            f"unexpected={sorted(actual - required)}"
        )
    validate_manifest(output / "combined_review_manifest.json")
    readback = json.loads(
        (output / "poster_direction_readback.json").read_text(encoding="utf-8")
    )
    if readback.get("state") != STATE or readback.get("review_question_count") != 1:
        raise Out07NativeCoverError("promoted review readback changed")
    html = (output / "index.html").read_text(encoding="utf-8")
    if html.count(REVIEW_QUESTION) != 1 or html.count("<video ") != 1:
        raise Out07NativeCoverError(
            "review page must contain one question and one video"
        )
    _assert_file_identity(
        output / "reinstantiated_baseline.mp4",
        expected_sha256=ACCEPTED_BASELINE_SHA256,
        expected_bytes=ACCEPTED_BASELINE_BYTES,
        label="promoted accepted baseline",
    )


def _validate_paths(
    episode: Path, baseline_dir: Path, output: Path, reference_corpus: Path
) -> None:
    _require_directory(episode, "episode directory")
    _require_directory(episode / "review", "episode review directory")
    _require_directory(baseline_dir, "accepted baseline component directory")
    _require_file(reference_corpus, "reference corpus")
    review = (episode / "review").resolve()
    if output.parent != review or output.name != DEFAULT_OUTPUT_NAME:
        raise Out07NativeCoverError(
            f"output must be the active single-review directory {review / DEFAULT_OUTPUT_NAME}"
        )
    if baseline_dir.resolve() == output.resolve():
        raise Out07NativeCoverError(
            "accepted baseline component cannot overlap the output"
        )


def _resolve_executable(value: str | Path | None, fallback: str) -> str:
    candidate = str(value) if value is not None else fallback
    resolved = shutil.which(candidate)
    if resolved is None:
        direct = Path(candidate)
        if direct.is_file():
            return str(direct.resolve())
        raise Out07NativeCoverError(f"required executable is unavailable: {candidate}")
    return resolved


def _named_file_digest(stage: Path, names: Iterable[str]) -> str:
    rows = [f"{name}\t{_sha256(stage / name)}" for name in names]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def _all_file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    }


def _canonical_digest(payload: Any) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _assert_file_identity(
    path: Path, *, expected_sha256: str, expected_bytes: int, label: str
) -> None:
    if path.stat().st_size != expected_bytes:
        raise Out07NativeCoverError(f"{label} byte size changed")
    if _sha256(path) != expected_sha256:
        raise Out07NativeCoverError(f"{label} SHA-256 changed")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    _write_text(
        path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _logical_path(output: Path, name: str) -> str:
    return f"episodes/{EPISODE_ID}/review/{output.name}/{name}"


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise Out07NativeCoverError(f"{label} missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise Out07NativeCoverError(f"{label} missing: {path}")


def _safe_remove_internal(path: Path, *, expected_parent: Path) -> None:
    resolved = path.resolve()
    parent = expected_parent.resolve()
    if resolved.parent != parent or not resolved.name.startswith("."):
        raise Out07NativeCoverError(
            f"refused cleanup outside internal path: {resolved}"
        )
    shutil.rmtree(resolved)


def _open_script() -> str:
    return """param([switch]$Serve, [int]$Port = 8071)
$ErrorActionPreference = 'Stop'
if ($Serve) {
    & (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
    exit $LASTEXITCODE
}
$index = Join-Path $PSScriptRoot 'index.html'
Write-Host "OUT-07 review entrypoint: $index"
Start-Process -FilePath $index
Write-Host "If local-file playback is blocked, rerun with -Serve."
"""


def _serve_script() -> str:
    return """param([int]$Port = 8071)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
Write-Host "OUT-07 review URL: $url"
Start-Process -FilePath $url
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
Push-Location $repoRoot
try {
    python -m src.cli.serve_review --root $PSScriptRoot --port $Port
} finally {
    Pop-Location
}
"""
