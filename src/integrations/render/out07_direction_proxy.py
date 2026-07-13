"""Build one Thank-host OUT-07 native Shorts cover direction proxy.

This route is deliberately separate from :mod:`out07_native_cover`.  The
strict route still requires the exact accepted baseline bytes.  This route
uses the known Thank source revision only to review the same scene, timestamp,
subtitle authority, and established vertical presentation direction.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import socket
import subprocess
import uuid
from html import escape
from pathlib import Path
from typing import Any, Iterable

from src.integrations.render import out07_native_cover as strict
from src.integrations.render import out07_reconstitution as rebuild
from src.integrations.render.subtitle_overlay_visual_proof import _write_ass
from src.integrations.render.vertical_short_candidate import (
    _escape_filter_path,
    build_vertical_subtitle_presentation,
)


ARTIFACT_ID = strict.ARTIFACT_ID
SCHEMA_VERSION = "clippipegen.out07.native_shorts_cover_direction_proxy.v1"
STATE = "OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY"
EPISODE_ID = strict.EPISODE_ID
SOURCE_PROVIDER = "youtube"
SOURCE_PROVIDER_ID = strict.SOURCE_PROVIDER_ID
SOURCE_URL = f"https://www.youtube.com/watch?v={SOURCE_PROVIDER_ID}"
LOCAL_SOURCE_SHA256 = rebuild.HISTORICAL_SOURCE_SHA256
PLANNER_SOURCE_SHA256 = rebuild.CURRENT_SOURCE_SHA256
CAPTION_SHA256 = "3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919"
ACCEPTED_BASELINE_SHA256 = strict.ACCEPTED_BASELINE_SHA256
PLANNER_COVER_SHA256 = (
    "6d8cf92ae49658a9eacb98e7a6e584aa69d2a4ecbb56b553c93eec69e6a3a174"
)
PLANNER_BASELINE_FRAME_FINGERPRINT = strict.BASELINE_FRAME_FINGERPRINT_SHA256
PLANNER_SOURCE_FRAME_FINGERPRINT = strict.SOURCE_FRAME_FINGERPRINT_SHA256
FINGERPRINT_PROFILE = strict.FINGERPRINT_PROFILE
SOURCE_TIMESTAMP_SECONDS = strict.RECOMMENDED_SOURCE_SECONDS
SEQUENCE_TIMESTAMP_SECONDS = strict.RECOMMENDED_BASELINE_SECONDS
CUT_ID = "cut_003"
SUBTITLE_ID = strict.RECOMMENDED_SUBTITLE_ID
SUBTITLE_TEXT_SHA256 = (
    "55520df85f88b66e66ae9d057a814ebedf8e6b4578281665d24ca4341f6bd9ed"
)
SUBTITLE_SOURCE_START_SECONDS = 22.606
SUBTITLE_SOURCE_END_SECONDS = 23.640
SUBTITLE_SEQUENCE_START_SECONDS = 11.678
SUBTITLE_SEQUENCE_END_SECONDS = 12.712
EVIDENCE_REVISION = "thank-6f78657e-native-cover-direction-proxy-v1"
DEFAULT_OUTPUT_NAME = "out07_native_shorts_cover_direction_proxy"
THANK_HOST = "DESKTOP-H53P1T4"
STRICT_EXACT_BASELINE_LOCATORS = (
    Path("review")
    / strict.DEFAULT_BASELINE_NAME
    / "assets"
    / "reinstantiated_baseline.mp4",
    Path("review") / strict.DEFAULT_OUTPUT_NAME / "reinstantiated_baseline.mp4",
)
REVIEW_QUESTION = (
    "このThank source revisionによる同一時刻・同一字幕のShorts一覧cover方向を"
    "採用してよいか。違和感があれば自由記述してください。"
)
PROXY_FILE = "native_shorts_cover_direction_proxy_1080x1920.png"
MAPPED_SOURCE_FILE = "mapped_source_frame_1920x1080.png"
READBACK_FILE = "cover_direction_proxy_readback.json"
MANIFEST_FILE = "combined_review_manifest.json"


class Out07DirectionProxyError(ValueError):
    """Raised when the proxy cannot preserve the fixed evidence boundary."""


def build_out07_direction_proxy(
    *,
    episode_dir: str | Path,
    output_dir: str | Path | None = None,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    verify_determinism: bool = False,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build twice, compare every package byte, and atomically promote."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    expected_episode = root / "episodes" / EPISODE_ID
    if episode != expected_episode or episode.name != EPISODE_ID:
        raise Out07DirectionProxyError(f"episode must be {expected_episode}")
    _require_directory(episode, "episode directory")

    output = _resolved(
        root,
        Path(output_dir)
        if output_dir is not None
        else episode / "review" / DEFAULT_OUTPUT_NAME,
    )
    expected_output = episode / "review" / DEFAULT_OUTPUT_NAME
    if output != expected_output:
        raise Out07DirectionProxyError(f"proxy output must be {expected_output}")
    if output == episode / "review" / strict.DEFAULT_OUTPUT_NAME:
        raise Out07DirectionProxyError("proxy must not overwrite the strict OUT-07 package")

    ffmpeg = strict._resolve_executable(ffmpeg_path, "ffmpeg")
    ffprobe = strict._resolve_executable(ffprobe_path, "ffprobe")
    inputs = _validate_inputs(
        root=root,
        episode=episode,
        ffmpeg=ffmpeg,
        ffprobe=ffprobe,
    )
    context = {
        **inputs,
        "root": root,
        "episode": episode,
        "output": output,
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
    }

    stage_one = output.parent / f".{output.name}.proxy-pass1-{uuid.uuid4().hex}"
    stage_two = output.parent / f".{output.name}.proxy-pass2-{uuid.uuid4().hex}"
    first: dict[str, Any] | None = None
    second: dict[str, Any] | None = None
    try:
        first = _build_once(stage=stage_one, context=context)
        second = _build_once(stage=stage_two, context=context)
        if first["core_digest"] != second["core_digest"]:
            raise Out07DirectionProxyError("fixed-input core digest changed")
        if first["package_digest"] != second["package_digest"]:
            raise Out07DirectionProxyError("fixed-input package digest changed")
        if first["file_hashes"] != second["file_hashes"]:
            raise Out07DirectionProxyError("fixed-input package bytes changed")
        if verify_determinism is False:
            # The proxy always performs the two-build check.  Keep the flag as
            # an explicit CLI/readback compatibility signal only.
            pass
        _promote_validated_package(stage=stage_two, output=output)
    finally:
        for path in (stage_one, stage_two):
            if path.exists():
                _safe_remove_internal(path, expected_parent=output.parent)

    if first is None or second is None:  # pragma: no cover - defensive only
        raise Out07DirectionProxyError("proxy build did not produce two receipts")
    readback = _read_json(output / READBACK_FILE, "proxy readback")
    return {
        "artifact_id": ARTIFACT_ID,
        "evidence_revision": EVIDENCE_REVISION,
        "state": STATE,
        "output_dir": output,
        "index_path": output / "index.html",
        "readback_path": output / READBACK_FILE,
        "manifest_path": output / MANIFEST_FILE,
        "proxy_path": output / PROXY_FILE,
        "proxy_classification": readback["proxy_classification"],
        "proxy_sha256": readback["proxy_sha256"],
        "deterministic_core_digest": second["core_digest"],
        "package_digest": second["package_digest"],
    }


def _validate_inputs(
    *, root: Path, episode: Path, ffmpeg: str, ffprobe: str
) -> dict[str, Any]:
    host = socket.gethostname()
    if host.upper() != THANK_HOST:
        raise Out07DirectionProxyError(
            f"Thank proxy host changed: expected {THANK_HOST}, got {host}"
        )

    contract_path = root / rebuild.ACTIVE_REBUILD_CONTRACT
    source = episode / "materials/src_video_jp_pilot01/source_video.mp4"
    caption = episode / f"source_subs/{SOURCE_PROVIDER_ID}.ja.json3"
    ledger_path = episode / "material_ledger.json"
    sidecar_path = episode / "materials/src_video_jp_pilot01/sidecar.json"
    receipt_path = episode / "materials/src_video_jp_pilot01/fetch_receipt.json"
    rights_path = episode / "rights_manifest.json"
    decision_path = episode / "review/jp_pilot01r3_cut_review/cut_decision_packet.json"
    for label, path in (
        ("active rebuild contract", contract_path),
        ("Thank source video", source),
        ("official caption", caption),
        ("material ledger", ledger_path),
        ("source sidecar", sidecar_path),
        ("source receipt", receipt_path),
        ("rights manifest", rights_path),
        ("cut decision packet", decision_path),
    ):
        _require_file(path, label)

    _assert_exact_baseline_absent(episode)

    contract = _read_json(contract_path, "active rebuild contract")
    identity = contract.get("source_identity") or {}
    if (
        contract.get("artifact_id") != ARTIFACT_ID
        or contract.get("episode_id") != EPISODE_ID
        or identity.get("provider") != SOURCE_PROVIDER
        or identity.get("provider_id") != SOURCE_PROVIDER_ID
        or identity.get("canonical_url") != SOURCE_URL
        or (identity.get("current_media_revision") or {}).get("sha256")
        != PLANNER_SOURCE_SHA256
    ):
        raise Out07DirectionProxyError("tracked OUT-07 source identity changed")

    source_sha = strict._sha256(source)
    caption_sha = strict._sha256(caption)
    if source_sha != LOCAL_SOURCE_SHA256:
        raise Out07DirectionProxyError("Thank historical source revision changed")
    if caption_sha != CAPTION_SHA256:
        raise Out07DirectionProxyError("official caption SHA-256 changed")

    ledger = _read_json(ledger_path, "material ledger")
    matches = [
        item
        for item in (ledger.get("materials") or [])
        if item.get("id") == rebuild.SOURCE_MATERIAL_ID
    ]
    if len(matches) != 1:
        raise Out07DirectionProxyError("Thank source material ledger entry changed")
    material = matches[0]
    sidecar = _read_json(sidecar_path, "source sidecar")
    receipt = _read_json(receipt_path, "source receipt")
    expected_source_path = strict._relative(source, root)
    if (
        material.get("file_path") != expected_source_path
        or material.get("hash_sha256") != source_sha
        or int(material.get("byte_size") or 0) != source.stat().st_size
        or sidecar.get("asset_hash_sha256") != source_sha
        or sidecar.get("asset_path") != expected_source_path
        or receipt.get("sha256") != source_sha
        or receipt.get("output_path") != expected_source_path
        or int(receipt.get("byte_size") or 0) != source.stat().st_size
        or receipt.get("mode") != "yt-dlp-video"
    ):
        raise Out07DirectionProxyError("Thank source ledger/sidecar/receipt chain changed")

    rights = _read_json(rights_path, "rights manifest")
    decision = _read_json(decision_path, "cut decision packet")
    decision_source = decision.get("source_identity") or {}
    if (
        (rights.get("source_video") or {}).get("url") != SOURCE_URL
        or decision_source.get("youtube_id") != SOURCE_PROVIDER_ID
        or decision_source.get("source_url") != SOURCE_URL
        or decision_source.get("source_video_material_id")
        != rebuild.SOURCE_MATERIAL_ID
        or not str(decision_source.get("subtitle_track") or "").endswith(
            f"/{SOURCE_PROVIDER_ID}.ja.json3"
        )
    ):
        raise Out07DirectionProxyError("provider identity cannot be tied to local authority")

    timeline, subtitle_contract, _, _ = rebuild._semantic_authority_from_contract(
        contract
    )
    caption_payload = _read_json(caption, "official caption")
    semantic_subtitles = rebuild._rehydrate_semantic_subtitles_from_caption(
        subtitle_contract=subtitle_contract,
        subtitle_track=caption_payload,
    )
    subtitle = next(
        (item for item in semantic_subtitles if item.get("id") == SUBTITLE_ID),
        None,
    )
    contract_subtitle = next(
        (item for item in subtitle_contract if item.get("id") == SUBTITLE_ID),
        None,
    )
    cut = next((item for item in timeline if item.get("id") == CUT_ID), None)
    _validate_mapping(subtitle=subtitle, contract_subtitle=contract_subtitle, cut=cut)

    layout, items, selector = build_vertical_subtitle_presentation(
        [subtitle],
        application_key="out07_direction_proxy",
        dimension_source="out07_thank_native_cover_direction_proxy",
    )
    if len(items) != 1 or items[0].get("subtitle_id") != SUBTITLE_ID:
        raise Out07DirectionProxyError("existing subtitle presentation changed")
    style = layout.get("diagnostic_ass_style") or {}
    font_file = Path(str(style.get("resolved_font_file") or ""))
    if (
        style.get("candidate_id") != "ed10l_keifont_pop_dialogue_candidate"
        or style.get("font_name") != "Keifont"
        or not font_file.is_file()
        or strict._sha256(font_file) != rebuild.KEIFONT_SHA256
    ):
        raise Out07DirectionProxyError("established Keifont subtitle contract unavailable")

    probe = strict._probe_media(ffprobe, source)
    if (
        probe.get("width") != 1920
        or probe.get("height") != 1080
        or abs(float(probe.get("fps") or 0.0) - 30.0) > 0.001
        or float(probe.get("duration_seconds") or 0.0) < SUBTITLE_SOURCE_END_SECONDS
    ):
        raise Out07DirectionProxyError("Thank source media identity/probe changed")
    actual_decode_timestamp = _nearest_frame_timestamp(
        ffprobe=ffprobe,
        source=source,
        target=SOURCE_TIMESTAMP_SECONDS,
    )
    if not (
        SUBTITLE_SOURCE_START_SECONDS
        <= actual_decode_timestamp
        <= SUBTITLE_SOURCE_END_SECONDS
    ):
        raise Out07DirectionProxyError("decoded frame left the authoritative sub_010 cue")

    return {
        "contract_path": contract_path,
        "source": source,
        "caption": caption,
        "source_sha": source_sha,
        "caption_sha": caption_sha,
        "source_probe": probe,
        "subtitle": subtitle,
        "contract_subtitle": contract_subtitle,
        "cut": cut,
        "layout": layout,
        "presentation_item": items[0],
        "selector": selector,
        "font_file": font_file,
        "actual_decode_timestamp": actual_decode_timestamp,
    }


def _assert_exact_baseline_absent(episode: Path) -> None:
    for locator in STRICT_EXACT_BASELINE_LOCATORS:
        path = episode / locator
        if not path.exists():
            continue
        if not path.is_file() or strict._sha256(path) != ACCEPTED_BASELINE_SHA256:
            raise Out07DirectionProxyError(
                f"non-exact media occupies an accepted-baseline path: {locator}"
            )
        raise Out07DirectionProxyError(
            f"exact accepted baseline is available at {locator}; "
            "use the strict exact route"
        )


def _validate_mapping(
    *,
    subtitle: dict[str, Any] | None,
    contract_subtitle: dict[str, Any] | None,
    cut: dict[str, Any] | None,
) -> None:
    if not isinstance(subtitle, dict) or not isinstance(contract_subtitle, dict):
        raise Out07DirectionProxyError("sub_010 authority is missing")
    if not isinstance(cut, dict):
        raise Out07DirectionProxyError("cut_003 authority is missing")
    text_hash = hashlib.sha256(str(subtitle.get("text") or "").encode("utf-8")).hexdigest()
    checks = {
        "subtitle id": subtitle.get("id") == SUBTITLE_ID,
        "cut id": subtitle.get("cut_id") == CUT_ID,
        "text hash": text_hash == SUBTITLE_TEXT_SHA256,
        "tracked text hash": contract_subtitle.get("text_sha256")
        == SUBTITLE_TEXT_SHA256,
        "source start": _close(
            subtitle.get("source_start_seconds"), SUBTITLE_SOURCE_START_SECONDS
        ),
        "source end": _close(
            subtitle.get("source_end_seconds"), SUBTITLE_SOURCE_END_SECONDS
        ),
        "sequence start": _close(
            subtitle.get("sequence_start_seconds"),
            SUBTITLE_SEQUENCE_START_SECONDS,
        ),
        "sequence end": _close(
            subtitle.get("sequence_end_seconds"), SUBTITLE_SEQUENCE_END_SECONDS
        ),
        "target source time": SUBTITLE_SOURCE_START_SECONDS
        <= SOURCE_TIMESTAMP_SECONDS
        <= SUBTITLE_SOURCE_END_SECONDS,
        "target sequence time": SUBTITLE_SEQUENCE_START_SECONDS
        <= SEQUENCE_TIMESTAMP_SECONDS
        <= SUBTITLE_SEQUENCE_END_SECONDS,
        "cut source mapping": _close(cut.get("source_start_seconds"), 22.606)
        and _close(cut.get("sequence_start_seconds"), 11.678),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise Out07DirectionProxyError(
            f"caption/timestamp/cut authority mismatch: {failed}"
        )


def _build_once(*, stage: Path, context: dict[str, Any]) -> dict[str, Any]:
    from PIL import Image

    stage.mkdir(parents=False, exist_ok=False)
    ass_path = stage / "proxy_subtitle.ass"
    proxy_path = stage / PROXY_FILE
    source_frame_path = stage / MAPPED_SOURCE_FILE

    item = copy.deepcopy(context["presentation_item"])
    item["display_start_seconds"] = 0.0
    item["display_end_seconds"] = 1.0
    _write_ass(ass_path, [item], layout=context["layout"], review_label=None)
    _render_proxy_frame(
        ffmpeg=context["ffmpeg"],
        source=context["source"],
        ass_path=ass_path,
        font_file=context["font_file"],
        output=proxy_path,
    )

    raw = strict._decode_rgb_frame(
        context["ffmpeg"],
        context["source"],
        SOURCE_TIMESTAMP_SECONDS,
        1920,
        1080,
    )
    source_image = Image.frombytes("RGB", (1920, 1080), raw)
    source_image.save(
        source_frame_path,
        format="PNG",
        optimize=False,
        compress_level=9,
    )
    source_image.close()
    strict._write_preview_images(cover=proxy_path, stage=stage)

    source_fingerprint = strict._frame_fingerprint(
        context["ffmpeg"], context["source"], SOURCE_TIMESTAMP_SECONDS
    )
    proxy_fingerprint = _image_fingerprint(context["ffmpeg"], proxy_path)
    proxy_sha = strict._sha256(proxy_path)
    classification = classify_proxy(
        proxy_sha256=proxy_sha,
        source_frame_fingerprint=source_fingerprint,
        proxy_frame_fingerprint=proxy_fingerprint,
    )
    neighborhood = [
        {
            "offset_frames": offset,
            "requested_seconds": round(SOURCE_TIMESTAMP_SECONDS + offset / 30.0, 6),
            "fingerprint_sha256": strict._frame_fingerprint(
                context["ffmpeg"],
                context["source"],
                SOURCE_TIMESTAMP_SECONDS + offset / 30.0,
            ),
        }
        for offset in (-1, 0, 1)
    ]
    readback = _readback_payload(
        context=context,
        proxy_sha=proxy_sha,
        source_fingerprint=source_fingerprint,
        proxy_fingerprint=proxy_fingerprint,
        classification=classification,
        neighborhood=neighborhood,
    )
    _write_json(stage / READBACK_FILE, readback)
    _write_text(stage / "index.html", _render_html(readback))
    _write_text(stage / "open_preview.ps1", _open_script())
    _write_text(stage / "serve_preview.ps1", _serve_script())

    core = _deterministic_core(readback)
    core_digest = _canonical_digest(core)
    _write_json(stage / "deterministic_core_readback.json", core)
    package_digest = _named_file_digest(
        stage,
        (
            PROXY_FILE,
            MAPPED_SOURCE_FILE,
            "cover_list_preview.jpg",
            "cover_shorts_ui_overlay_preview.jpg",
            "cover_center_4x5.jpg",
            "proxy_subtitle.ass",
            READBACK_FILE,
            "deterministic_core_readback.json",
            "index.html",
            "open_preview.ps1",
            "serve_preview.ps1",
        ),
    )
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "evidence_revision": EVIDENCE_REVISION,
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
    _write_json(stage / "determinism_receipt.json", receipt)
    _write_manifest(stage, core_digest=core_digest, package_digest=package_digest)
    _validate_promoted_package(stage)
    return {
        "core_digest": core_digest,
        "package_digest": package_digest,
        "file_hashes": _all_file_hashes(stage),
    }


def classify_proxy(
    *,
    proxy_sha256: str,
    source_frame_fingerprint: str,
    proxy_frame_fingerprint: str,
) -> str:
    """Use the strongest classification directly supported by known hashes."""

    source_matches = source_frame_fingerprint == PLANNER_SOURCE_FRAME_FINGERPRINT
    proxy_matches = proxy_frame_fingerprint == PLANNER_BASELINE_FRAME_FINGERPRINT
    if (
        proxy_sha256 == PLANNER_COVER_SHA256
        and source_matches
        and proxy_matches
    ):
        return "cover_visual_exact_reconstitution"
    if source_matches and proxy_matches:
        return "cover_pixel_equivalent_proxy"
    return "cover_direction_semantic_proxy"


def _readback_payload(
    *,
    context: dict[str, Any],
    proxy_sha: str,
    source_fingerprint: str,
    proxy_fingerprint: str,
    classification: str,
    neighborhood: list[dict[str, Any]],
) -> dict[str, Any]:
    actual = float(context["actual_decode_timestamp"])
    style = context["layout"]["diagnostic_ass_style"]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "evidence_revision": EVIDENCE_REVISION,
        "state": STATE,
        "episode_id": EPISODE_ID,
        "provider": SOURCE_PROVIDER,
        "provider_id": SOURCE_PROVIDER_ID,
        "local_source_sha256": LOCAL_SOURCE_SHA256,
        "planner_source_sha256": PLANNER_SOURCE_SHA256,
        "byte_equivalence_claimed": False,
        "caption_sha256": CAPTION_SHA256,
        "source_timestamp_seconds": SOURCE_TIMESTAMP_SECONDS,
        "actual_decode_timestamp_seconds": actual,
        "decode_timestamp_delta_seconds": round(
            actual - SOURCE_TIMESTAMP_SECONDS, 6
        ),
        "decode_adjustment_reason": (
            "nearest_30fps_frame_within_same_subtitle_cue"
            if not _close(actual, SOURCE_TIMESTAMP_SECONDS, tolerance=0.0005)
            else "target_timestamp_is_decode_frame"
        ),
        "sequence_timestamp_seconds": SEQUENCE_TIMESTAMP_SECONDS,
        "cut_id": CUT_ID,
        "subtitle_id": SUBTITLE_ID,
        "subtitle_authority": {
            "text_sha256": SUBTITLE_TEXT_SHA256,
            "source_start_seconds": SUBTITLE_SOURCE_START_SECONDS,
            "source_end_seconds": SUBTITLE_SOURCE_END_SECONDS,
            "sequence_start_seconds": SUBTITLE_SEQUENCE_START_SECONDS,
            "sequence_end_seconds": SUBTITLE_SEQUENCE_END_SECONDS,
            "source_segment_ids": ["seg_000010"],
            "caption_payload_digest": rebuild.CAPTION_PAYLOAD_DIGEST,
            "plaintext_stored_in_tracked_contract": False,
            "caption_authority_validation": "passed",
        },
        "exact_baseline_available": False,
        "accepted_baseline_status": "accepted_historical_fact",
        "accepted_baseline_sha256": ACCEPTED_BASELINE_SHA256,
        "baseline_acceptance_reopened": False,
        "cover_direction_review_available": True,
        "cover_direction_acceptance": "pending",
        "proxy_classification": classification,
        "proxy_sha256": proxy_sha,
        "source_frame_fingerprint": source_fingerprint,
        "proxy_frame_fingerprint": proxy_fingerprint,
        "fingerprint_profile": FINGERPRINT_PROFILE,
        "planner_comparison_hashes": {
            "planner_cover_sha256": PLANNER_COVER_SHA256,
            "planner_baseline_frame_fingerprint": PLANNER_BASELINE_FRAME_FINGERPRINT,
            "planner_mapped_source_fingerprint": PLANNER_SOURCE_FRAME_FINGERPRINT,
            "cover_sha_matches": proxy_sha == PLANNER_COVER_SHA256,
            "source_fingerprint_matches": source_fingerprint
            == PLANNER_SOURCE_FRAME_FINGERPRINT,
            "proxy_fingerprint_matches": proxy_fingerprint
            == PLANNER_BASELINE_FRAME_FINGERPRINT,
        },
        "classification_evidence": {
            "same_provider_identity": True,
            "same_scene_timestamp_mapping": True,
            "same_caption_authority_and_cue": True,
            "planner_pixels_available_on_thank": False,
            "semantic_continuity_is_inference": classification
            == "cover_direction_semantic_proxy",
            "stronger_classification_hidden": False,
        },
        "decode_neighborhood_fingerprints": neighborhood,
        "source_frame_only": True,
        "existing_subtitle_only": True,
        "poster_added_abstract_background": False,
        "poster_added_auxiliary_text": False,
        "masks_used": False,
        "collage_used": False,
        "third_party_pixels_used": False,
        "render_contract": {
            "reframe": "full_16_9_fit_source_derived_blurred_canvas",
            "subtitle_presentation": "existing_out05_vertical_subtitle_presentation",
            "font_candidate_id": style.get("candidate_id"),
            "font_family": style.get("font_name"),
            "font_file_sha256": rebuild.KEIFONT_SHA256,
            "font_file_status": style.get("font_file_status"),
            "frame_width": 1080,
            "frame_height": 1920,
        },
        "source_probe": context["source_probe"],
        "visual_evidence": {
            "list_preview": "cover_list_preview.jpg",
            "native_cover_proxy": PROXY_FILE,
            "shorts_ui_overlay_preview": "cover_shorts_ui_overlay_preview.jpg",
            "center_4x5_preview": "cover_center_4x5.jpg",
            "mapped_source_frame": MAPPED_SOURCE_FILE,
        },
        "review_scope": {
            "question": REVIEW_QUESTION,
            "allowed": [
                "timestamp",
                "subject_direction",
                "expression",
                "crop",
                "existing_subtitle",
                "shorts_list_appearance",
            ],
            "baseline_video_reviewed": False,
            "tempo_reviewed": False,
            "full_subtitle_track_reviewed": False,
            "metadata_reviewed": False,
            "rights_reviewed": False,
        },
        "local_host_receipt": {
            "local_verified_host": THANK_HOST,
            "local_entrypoint": "http://127.0.0.1:8071/index.html",
            "open_command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "out07_native_shorts_cover_direction_proxy\\open_preview.ps1 "
                "-Port 8071"
            ),
            "server_restart_command": (
                "uvx python -m src.cli.serve_review --root "
                "episodes/jp_pilot01_hololive_bancho_20260525/review/"
                "out07_native_shorts_cover_direction_proxy --port 8071"
            ),
            "portable_entrypoint": None,
        },
        "rights_status": "pending",
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "public_or_publishing_acceptance": False,
        "publish_ready": False,
        "all_external_attempts": False,
        "attempts": strict._attempt_flags(),
    }


def _deterministic_core(readback: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "evidence_revision": EVIDENCE_REVISION,
        "provider_id": readback["provider_id"],
        "local_source_sha256": readback["local_source_sha256"],
        "planner_source_sha256": readback["planner_source_sha256"],
        "caption_sha256": readback["caption_sha256"],
        "mapping": {
            "source_timestamp_seconds": readback["source_timestamp_seconds"],
            "sequence_timestamp_seconds": readback["sequence_timestamp_seconds"],
            "cut_id": readback["cut_id"],
            "subtitle_id": readback["subtitle_id"],
            "subtitle_text_sha256": readback["subtitle_authority"]["text_sha256"],
        },
        "exact_baseline_available": False,
        "accepted_baseline_status": "accepted_historical_fact",
        "cover_direction_review_available": True,
        "cover_direction_acceptance": "pending",
        "proxy_classification": readback["proxy_classification"],
        "proxy_sha256": readback["proxy_sha256"],
        "source_frame_fingerprint": readback["source_frame_fingerprint"],
        "proxy_frame_fingerprint": readback["proxy_frame_fingerprint"],
        "render_contract": readback["render_contract"],
        "pixel_policy": {
            "source_frame_only": True,
            "existing_subtitle_only": True,
            "poster_added_abstract_background": False,
            "poster_added_auxiliary_text": False,
            "masks_used": False,
            "collage_used": False,
            "third_party_pixels_used": False,
        },
        "gates": {
            "rights_status": "pending",
            "production_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "public_or_publishing_acceptance": False,
            "all_external_attempts": False,
        },
    }


def _render_proxy_frame(
    *,
    ffmpeg: str,
    source: Path,
    ass_path: Path,
    font_file: Path,
    output: Path,
) -> None:
    ass = _escape_filter_path(ass_path)
    fonts = _escape_filter_path(font_file.parent)
    start = f"{SOURCE_TIMESTAMP_SECONDS:.3f}"
    end = f"{SOURCE_TIMESTAMP_SECONDS + 0.050:.3f}"
    filters = ";".join(
        (
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,split=2[bgraw][fgraw]",
            "[bgraw]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            "crop=1080:1920,gblur=sigma=42,eq=saturation=0.72:brightness=-0.10[bg]",
            "[fgraw]scale=1080:-2:flags=lanczos[fg]",
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p[base]",
            f"[base]ass=filename='{ass}':fontsdir='{fonts}',format=rgb24[out]",
        )
    )
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-filter_complex",
            filters,
            "-map",
            "[out]",
            "-frames:v",
            "1",
            "-compression_level",
            "9",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    if result.returncode != 0 or not output.is_file():
        raise Out07DirectionProxyError(
            "native cover proxy render failed: "
            + (result.stderr or "unknown ffmpeg error").strip()[-800:]
        )


def _nearest_frame_timestamp(*, ffprobe: str, source: Path, target: float) -> float:
    start = max(0.0, target - 0.350)
    end = target + 0.350
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-read_intervals",
            f"{start:.6f}%{end:.6f}",
            "-show_frames",
            "-show_entries",
            "frame=best_effort_timestamp_time",
            "-of",
            "json",
            str(source),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    payload = json.loads(result.stdout)
    values = [
        float(item["best_effort_timestamp_time"])
        for item in payload.get("frames") or []
        if item.get("best_effort_timestamp_time") is not None
    ]
    values = [value for value in values if start <= value <= end]
    if not values:
        raise Out07DirectionProxyError("cannot resolve source frame timestamp")
    return min(values, key=lambda value: abs(value - target))


def _image_fingerprint(ffmpeg: str, path: Path) -> str:
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(path),
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
        timeout=60,
    )
    if len(result.stdout) != 320 * 180 * 3:
        raise Out07DirectionProxyError("proxy fingerprint byte count changed")
    return hashlib.sha256(result.stdout).hexdigest()


def _render_html(readback: dict[str, Any]) -> str:
    classification = escape(str(readback["proxy_classification"]))
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,">
<title>OUT-07 Thank Shorts cover方向確認</title>
<style>
:root {{ color-scheme:dark; font-family:"Yu Gothic UI","Noto Sans JP",sans-serif; background:#090c11; color:#f3f4f6; }}
* {{ box-sizing:border-box; }} html,body {{ margin:0; max-width:100%; overflow-x:hidden; }}
main {{ width:min(880px,100%); margin:auto; padding:24px; overflow-wrap:anywhere; }}
h1 {{ font-size:clamp(1.55rem,4vw,2.45rem); margin:.3rem 0 .7rem; }} h2 {{ margin:0 0 14px; font-size:1.2rem; }}
.eyebrow {{ color:#7dd3fc; font-weight:800; letter-spacing:.08em; }} .lead,.muted {{ color:#aeb9c8; }}
section,details {{ width:100%; margin-top:20px; padding:18px; border:1px solid #334155; border-radius:14px; background:#111827; }}
.visual {{ display:flex; justify-content:center; min-width:0; }} figure {{ margin:0; min-width:0; }} figcaption {{ margin-top:8px; color:#94a3b8; text-align:center; }}
img {{ display:block; max-width:100%; height:auto; border-radius:12px; background:#000; }}
.portrait img {{ width:min(405px,100%); }} .crop img {{ width:min(432px,100%); }} .source img {{ width:min(720px,100%); }}
.question {{ border-color:#38bdf8; background:#0c2535; font-size:1.08rem; }}
summary {{ cursor:pointer; font-weight:800; }} code {{ color:#bae6fd; }} dl {{ display:grid; grid-template-columns:minmax(120px,220px) 1fr; gap:8px 14px; }} dt {{ color:#94a3b8; }} dd {{ margin:0; }}
@media(max-width:620px) {{ main {{ padding:14px; }} section,details {{ padding:14px; }} dl {{ grid-template-columns:1fr; }} dd {{ margin-bottom:8px; }} }}
</style></head><body><main>
<div class="eyebrow">OUT-07 / THANK DIRECTION PROXY</div>
<h1>同じ時刻・同じ字幕を、Shorts一覧の一枚で確認</h1>
<p class="lead">これは受理済みbaseline bytesの代替ではありません。Thank端末にある同一providerの既知source revisionから、映像フレーム、既存の9:16 reframe、既存の字幕処理だけを使った方向確認用proxyです。</p>

<section class="portrait"><h2>1. 一覧縮小preview</h2><div class="visual"><figure><img src="cover_list_preview.jpg" width="405" height="720" alt="Shorts一覧縮小preview"><figcaption>405×720での一覧縮小</figcaption></figure></div></section>

<section class="portrait"><h2>2. 1080×1920 native cover proxy</h2><div class="visual"><figure><img src="{PROXY_FILE}" width="540" height="960" alt="Thank source revisionによるnative cover方向proxy"><figcaption>source {SOURCE_TIMESTAMP_SECONDS:.3f}s / {CUT_ID} / {SUBTITLE_ID}</figcaption></figure></div></section>

<section class="portrait"><h2>3. Shorts UI overlay近似</h2><p class="muted">公式UI保証ではなく、右側操作と下部情報の重なりを見る内部近似です。</p><div class="visual"><img src="cover_shorts_ui_overlay_preview.jpg" width="405" height="720" alt="Shorts UI overlay近似"></div></section>

<section class="crop"><h2>4. center 4:5 crop確認</h2><div class="visual"><img src="cover_center_4x5.jpg" width="432" height="540" alt="中央4対5crop確認"></div></section>

<section class="source"><h2>5. mapped source frame</h2><p class="muted">横長sourceの {SOURCE_TIMESTAMP_SECONDS:.3f}s を無加工で読み戻します。</p><div class="visual"><img src="{MAPPED_SOURCE_FILE}" width="720" height="405" alt="対応するsource frame"></div></section>

<details><summary>6. evidence / readback</summary><dl>
<dt>evidence revision</dt><dd><code>{EVIDENCE_REVISION}</code></dd>
<dt>proxy classification</dt><dd><code>{classification}</code></dd>
<dt>Thank source SHA</dt><dd><code>{LOCAL_SOURCE_SHA256}</code></dd>
<dt>Planner source SHA</dt><dd><code>{PLANNER_SOURCE_SHA256}</code>（byte-equivalentとは主張しません）</dd>
<dt>caption SHA</dt><dd><code>{CAPTION_SHA256}</code></dd>
<dt>accepted baseline</dt><dd>historical accepted fact / Thank端末では exact bytes unavailable</dd>
<dt>closed gates</dt><dd>rights=pending / production=false / public・publishing=false / external attempts=false</dd>
</dl></details>

<section class="question"><h2>7. 今回の確認</h2><p>{escape(REVIEW_QUESTION)}</p></section>
</main></body></html>"""


def _open_script() -> str:
    return """param([int]$Port = 8071)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
exit $LASTEXITCODE
"""


def _serve_script() -> str:
    return """param([int]$Port = 8071)
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
Write-Host "OUT-07 Thank direction proxy URL: $url"
Start-Process -FilePath $url
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
Push-Location $repoRoot
try {
    uvx python -m src.cli.serve_review --root $PSScriptRoot --port $Port
} finally {
    Pop-Location
}
"""


def _write_manifest(stage: Path, *, core_digest: str, package_digest: str) -> None:
    files = [
        {
            "path": path.relative_to(stage).as_posix(),
            "byte_size": path.stat().st_size,
            "sha256": strict._sha256(path),
        }
        for path in sorted(item for item in stage.rglob("*") if item.is_file())
        if path.name != MANIFEST_FILE
    ]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "evidence_revision": EVIDENCE_REVISION,
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
    _write_json(stage / MANIFEST_FILE, payload)


def validate_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    payload = _read_json(manifest_path, "combined proxy manifest")
    root = manifest_path.parent
    files = payload.get("files")
    if not isinstance(files, list) or payload.get("file_count") != len(files):
        raise Out07DirectionProxyError("manifest file inventory is invalid")
    names: set[str] = set()
    for row in files:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise Out07DirectionProxyError("manifest row is invalid")
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise Out07DirectionProxyError(f"unsafe manifest path: {row['path']}")
        name = relative.as_posix()
        if name in names:
            raise Out07DirectionProxyError(f"duplicate manifest path: {name}")
        names.add(name)
        target = root / relative
        _require_file(target, f"manifest file {name}")
        if (
            target.stat().st_size != row.get("byte_size")
            or strict._sha256(target) != row.get("sha256")
        ):
            raise Out07DirectionProxyError(f"manifest mismatch: {name}")
    actual = {
        item.relative_to(root).as_posix()
        for item in root.rglob("*")
        if item.is_file() and item.resolve() != manifest_path.resolve()
    }
    if actual != names:
        raise Out07DirectionProxyError("manifest inventory mismatch")
    integrity = payload.get("manifest_self_integrity") or {}
    unsigned = dict(payload)
    unsigned.pop("manifest_self_integrity", None)
    if _canonical_digest(unsigned) != integrity.get("sha256"):
        raise Out07DirectionProxyError("manifest self-integrity mismatch")
    return payload


def _validate_promoted_package(output: Path) -> None:
    from PIL import Image

    required = {
        PROXY_FILE,
        MAPPED_SOURCE_FILE,
        "cover_list_preview.jpg",
        "cover_shorts_ui_overlay_preview.jpg",
        "cover_center_4x5.jpg",
        "proxy_subtitle.ass",
        READBACK_FILE,
        "deterministic_core_readback.json",
        "determinism_receipt.json",
        MANIFEST_FILE,
        "index.html",
        "open_preview.ps1",
        "serve_preview.ps1",
    }
    actual = {path.name for path in output.iterdir() if path.is_file()}
    if actual != required:
        raise Out07DirectionProxyError(
            f"proxy package inventory changed: missing={sorted(required - actual)} "
            f"unexpected={sorted(actual - required)}"
        )
    validate_manifest(output / MANIFEST_FILE)
    readback = _read_json(output / READBACK_FILE, "proxy readback")
    if (
        readback.get("artifact_id") != ARTIFACT_ID
        or readback.get("evidence_revision") != EVIDENCE_REVISION
        or readback.get("exact_baseline_available") is not False
        or readback.get("cover_direction_review_available") is not True
        or readback.get("cover_direction_acceptance") != "pending"
        or readback.get("proxy_sha256") != strict._sha256(output / PROXY_FILE)
    ):
        raise Out07DirectionProxyError("proxy readback boundary changed")
    dimensions = {
        PROXY_FILE: (1080, 1920),
        MAPPED_SOURCE_FILE: (1920, 1080),
        "cover_list_preview.jpg": (405, 720),
        "cover_shorts_ui_overlay_preview.jpg": (405, 720),
        "cover_center_4x5.jpg": (864, 1080),
    }
    for name, expected in dimensions.items():
        with Image.open(output / name) as image:
            image.load()
            if image.size != expected:
                raise Out07DirectionProxyError(
                    f"image dimensions changed: {name}={image.size}"
                )
    html = (output / "index.html").read_text(encoding="utf-8")
    if html.count(REVIEW_QUESTION) != 1:
        raise Out07DirectionProxyError("review page must contain exactly one question")
    ordered = (
        "cover_list_preview.jpg",
        PROXY_FILE,
        "cover_shorts_ui_overlay_preview.jpg",
        "cover_center_4x5.jpg",
        MAPPED_SOURCE_FILE,
        "evidence / readback",
        REVIEW_QUESTION,
    )
    positions = [html.index(value) for value in ordered]
    if positions != sorted(positions):
        raise Out07DirectionProxyError("review page evidence order changed")
    forbidden = (
        "reinstantiated_baseline.mp4",
        "poster_A_1080x1920.jpg",
        "poster_B_1080x1920.jpg",
        "poster_C_1080x1920.jpg",
        "metadataを再審査",
    )
    if any(value in html for value in forbidden):
        raise Out07DirectionProxyError("review page reopened excluded evidence")


def _promote_validated_package(*, stage: Path, output: Path) -> None:
    backup: Path | None = None
    if output.exists():
        backup = output.parent / f".{output.name}.backup-{uuid.uuid4().hex}"
        output.replace(backup)
    failed: Path | None = None
    try:
        stage.replace(output)
        _validate_promoted_package(output)
    except Exception:
        if output.exists():
            failed = output.parent / f".{output.name}.failed-{uuid.uuid4().hex}"
            output.replace(failed)
        if backup is not None and backup.exists():
            backup.replace(output)
            backup = None
        if failed is not None and failed.exists():
            _safe_remove_internal(failed, expected_parent=output.parent)
        raise
    if backup is not None and backup.exists():
        _safe_remove_internal(backup, expected_parent=output.parent)


def _all_file_hashes(root: Path) -> dict[str, str]:
    return {
        item.relative_to(root).as_posix(): strict._sha256(item)
        for item in sorted(path for path in root.rglob("*") if path.is_file())
    }


def _named_file_digest(stage: Path, names: Iterable[str]) -> str:
    payload = [
        {
            "path": name,
            "byte_size": (stage / name).stat().st_size,
            "sha256": strict._sha256(stage / name),
        }
        for name in names
    ]
    return _canonical_digest(payload)


def _canonical_digest(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Out07DirectionProxyError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise Out07DirectionProxyError(f"{label} must be a JSON object")
    return payload


def _resolved(root: Path, path: Path) -> Path:
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Out07DirectionProxyError(f"path escapes repo root: {path}") from exc
    return resolved


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise Out07DirectionProxyError(f"{label} is missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise Out07DirectionProxyError(f"{label} is missing: {path}")


def _safe_remove_internal(path: Path, *, expected_parent: Path) -> None:
    resolved = path.resolve()
    parent = expected_parent.resolve()
    if resolved.parent != parent or not resolved.name.startswith("."):
        raise Out07DirectionProxyError(
            f"refused cleanup outside internal path: {resolved}"
        )
    shutil.rmtree(resolved)


def _close(value: Any, expected: float, *, tolerance: float = 0.001) -> bool:
    try:
        return abs(float(value) - expected) <= tolerance
    except (TypeError, ValueError):
        return False
