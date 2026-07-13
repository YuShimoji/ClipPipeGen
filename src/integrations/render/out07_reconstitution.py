"""Revision-aware OUT-07 baseline and poster review reconstruction.

This module is intentionally separate from the historical accepted-only
OUT-05/06/07 builders.  It qualifies one episode-local media revision from
receipt/sidecar/ledger/rights evidence, reconstructs the fixed three-cut
semantic baseline, and reuses the established render/poster primitives.  A
different source or output byte hash never inherits historical human
acceptance.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import re
import shutil
import socket
import subprocess
import uuid
from html import escape
from pathlib import Path, PureWindowsPath
from typing import Any, Callable

from src.integrations.render import complete_narrative_short as complete
from src.integrations.render import ffmpeg_tiny
from src.integrations.render import shorts_poster_frame_proof as poster
from src.integrations.render.operator_delivery_pack import EPISODE_COPY_PLAN
from src.integrations.render.subtitle_overlay_visual_proof import _write_ass
from src.integrations.render.vertical_short_candidate import (
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


ARTIFACT_ID = poster.ARTIFACT_ID
SCHEMA_VERSION = "clippipegen.out07.reconstitution.v0"
STATE = "reinstantiated_baseline_and_out07_poster_directions_combined_review_ready"
EPISODE_ID = "jp_pilot01_hololive_bancho_20260525"
SOURCE_PROVIDER = "youtube"
SOURCE_PROVIDER_ID = "7J5aS_pcBj4"
SOURCE_URL = f"https://www.youtube.com/watch?v={SOURCE_PROVIDER_ID}"
SOURCE_MATERIAL_ID = "src_video_jp_pilot01"
AUDIO_MATERIAL_ID = "src_audio_jp_pilot01"
HISTORICAL_SOURCE_SHA256 = (
    "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
)
CURRENT_SOURCE_SHA256 = (
    "e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889"
)
CURRENT_AUDIO_SHA256 = (
    "7cd566dc62683651b05b10b1b4397c44699807249f90af784b88ba0f572cae5d"
)
KEIFONT_SHA256 = "d5795bdff960c2b2ec5727ffeb79d836f8f11dac3015f6e16089a912e9cced6f"
HISTORICAL_ACCEPTED_BASELINE_SHA256 = poster.ACCEPTED_VIDEO_SHA256
BASELINE_OUTPUT_NAME = "out07_reinstantiated_baseline_candidate"
COMBINED_OUTPUT_NAME = poster.OUTPUT_NAME
MEDIA_REVISION_ID = "planner007-e2206cef-20260525"
ACTIVE_REBUILD_CONTRACT = Path("artifacts/ACTIVE_REBUILD.json")
BASELINE_REVIEW_QUESTION = (
    "再構成動画に、内容・タイミング・字幕・音声・画面上の新しい異常はありませんか？"
)
POSTER_REVIEW_QUESTION = "A/B/C のどれが実用候補に最も近いですか。全案不採用、または poster 表現に違和感がある場合は併記してください。"
FRAME_FINGERPRINT_TIMES = (2.453, 8.900, 12.329, 16.900, 22.606, 37.050, 49.400)
PCM_FINGERPRINT_WINDOWS = (
    ("cut001_open", 2.453, 0.500),
    ("cut001_close", 8.793, 0.500),
    ("cut002_open", 12.329, 0.500),
    ("cut003_open", 22.606, 0.500),
    ("cut003_mid", 36.587, 0.500),
    ("cut003_close", 49.066, 0.500),
)
EXPECTED_WRAP_LINES = {
    "sub_013": ["なんで", "来なかった", "んすか！！"],
    "sub_014": ["ずっと", "待ってたんすよ！！"],
    "sub_019": ["はじめの勝ちって", "ことでいいですね？"],
    "sub_024": ["団長、ちなみに、", "他の番長", "知ってますか？"],
    "sub_028": ["マリンなら", "あっちにいたよ"],
    "sub_029": ["ありがとう", "ございますー！"],
}


class Out07ReconstitutionError(Exception):
    """Raised when revision qualification or deterministic reconstruction fails."""


RenderExecutor = Callable[..., dict[str, Any]]
PostRenderExecutor = Callable[..., dict[str, Any]]


def load_current_episode_authority(
    *,
    episode_dir: str | Path,
    base_dir: str | Path | None = None,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    execute_media_checks: bool = True,
) -> dict[str, Any]:
    """Triangulate the current media revision and fixed semantic timeline."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    if episode.name != EPISODE_ID:
        raise Out07ReconstitutionError(f"episode must be {EPISODE_ID}")
    _require_directory(episode, "episode directory")

    contract_path = _resolved(root, ACTIVE_REBUILD_CONTRACT)
    _require_file(contract_path, "active rebuild contract")
    contract = _read_json(contract_path, "active rebuild contract")
    if (
        contract.get("artifact_id") != ARTIFACT_ID
        or contract.get("episode_id") != episode.name
        or (contract.get("source_identity") or {}).get("provider_id")
        != SOURCE_PROVIDER_ID
    ):
        raise Out07ReconstitutionError("active rebuild contract identity changed")

    paths = {
        "ledger": episode / "material_ledger.json",
        "rights": episode / "rights_manifest.json",
        "edit_pack": episode / "edit_pack.json",
        "transcript": episode / "transcript.json",
        "decision": episode / "review/jp_pilot01r3_cut_review/cut_decision_packet.json",
        "proxy": episode
        / "review/jp_pilot01r3_cut_review/cut_002_cut_003_operator_proxy_decision_handoff.json",
        "subtitle_track": episode / f"source_subs/{SOURCE_PROVIDER_ID}.ja.json3",
    }
    _require_file(paths["ledger"], "material ledger")
    ledger = _read_json(paths["ledger"], "material ledger")
    direct_names = ("edit_pack", "transcript", "decision", "proxy", "subtitle_track")
    direct_presence = {name: paths[name].is_file() for name in direct_names}
    if any(direct_presence.values()) and not all(direct_presence.values()):
        missing = sorted(
            name for name, present in direct_presence.items() if not present
        )
        raise Out07ReconstitutionError(
            f"episode authority is partial; restore all direct files or none: {missing}"
        )
    direct_authority = all(direct_presence.values())
    rights = (
        _read_json(paths["rights"], "rights manifest")
        if paths["rights"].is_file()
        else None
    )
    if direct_authority:
        edit_pack = _read_json(paths["edit_pack"], "edit pack")
        transcript = _read_json(paths["transcript"], "transcript")
        decision = _read_json(paths["decision"], "cut decision packet")
        proxy = _read_json(paths["proxy"], "operator proxy authority")
        subtitle_track = _read_json(paths["subtitle_track"], "subtitle track")
        _validate_direct_authority_inventory(contract=contract, paths=paths)
    else:
        edit_pack = transcript = proxy = subtitle_track = None
        _, _, decision, _ = _semantic_authority_from_contract(contract)

    video_entry = _single_material(ledger, SOURCE_MATERIAL_ID)
    audio_entry = _single_material(ledger, AUDIO_MATERIAL_ID)
    source_video = _resolved(root, Path(str(video_entry.get("file_path") or "")))
    source_audio = _resolved(root, Path(str(audio_entry.get("file_path") or "")))
    video_sidecar = _resolved(root, Path(str(video_entry.get("sidecar_path") or "")))
    audio_sidecar = _resolved(root, Path(str(audio_entry.get("sidecar_path") or "")))
    video_receipt = video_sidecar.parent / "fetch_receipt.json"
    audio_receipt = audio_sidecar.parent / "fetch_receipt.json"
    for label, path in (
        ("source video", source_video),
        ("source audio", source_audio),
        ("video sidecar", video_sidecar),
        ("video receipt", video_receipt),
        ("audio sidecar", audio_sidecar),
        ("audio receipt", audio_receipt),
    ):
        _require_file(path, label)

    video_sidecar_data = _read_json(video_sidecar, "video sidecar")
    video_receipt_data = _read_json(video_receipt, "video receipt")
    audio_sidecar_data = _read_json(audio_sidecar, "audio sidecar")
    audio_receipt_data = _read_json(audio_receipt, "audio receipt")
    source_hash = _sha256(source_video)
    audio_hash = _sha256(source_audio)
    if source_hash != CURRENT_SOURCE_SHA256:
        raise Out07ReconstitutionError("Planner007 source video revision hash changed")
    if audio_hash != CURRENT_AUDIO_SHA256:
        raise Out07ReconstitutionError("Planner007 source audio revision hash changed")
    _validate_material_chain(
        entry=video_entry,
        sidecar=video_sidecar_data,
        receipt=video_receipt_data,
        material_id=SOURCE_MATERIAL_ID,
        path=source_video,
        sha256=source_hash,
        root=root,
        expected_mode="yt-dlp-video",
    )
    _validate_material_chain(
        entry=audio_entry,
        sidecar=audio_sidecar_data,
        receipt=audio_receipt_data,
        material_id=AUDIO_MATERIAL_ID,
        path=source_audio,
        sha256=audio_hash,
        root=root,
        expected_mode="yt-dlp-audio",
    )

    if direct_authority:
        if rights is None:
            raise Out07ReconstitutionError(
                "rights manifest is required with direct episode authority"
            )
        rights_source = rights.get("source_video") or {}
        decision_source = decision.get("source_identity") or {}
        if (
            rights_source.get("url") != SOURCE_URL
            or rights_source.get("platform") != SOURCE_PROVIDER
            or decision_source.get("youtube_id") != SOURCE_PROVIDER_ID
            or decision_source.get("source_url") != SOURCE_URL
            or decision_source.get("source_video_material_id") != SOURCE_MATERIAL_ID
            or decision_source.get("source_audio_material_id") != AUDIO_MATERIAL_ID
        ):
            raise Out07ReconstitutionError(
                "canonical source identity evidence does not agree"
            )
        if not str(decision_source.get("subtitle_track") or "").endswith(
            f"/{SOURCE_PROVIDER_ID}.ja.json3"
        ):
            raise Out07ReconstitutionError("subtitle-track source identity changed")
        episode_ids = {
            "rights": rights.get("episode_id"),
            "decision": decision.get("episode_id"),
            "edit_pack": edit_pack.get("episode_id"),
            "transcript": transcript.get("episode_id"),
            "operator_proxy": proxy.get("episode_id"),
        }
        _validate_episode_identity(episode_id=episode.name, values=episode_ids)
        _validate_subtitle_track_authority(
            transcript=transcript,
            subtitle_track=subtitle_track,
            subtitle_track_path=paths["subtitle_track"],
        )
        timeline, semantic_subtitles = _semantic_timeline(
            edit_pack=edit_pack,
            transcript=transcript,
            decision=decision,
        )
        contract_timeline, contract_subtitles, _, _ = _semantic_authority_from_contract(
            contract
        )
        if timeline != contract_timeline or semantic_subtitles != contract_subtitles:
            raise Out07ReconstitutionError(
                "direct episode authority differs from tracked semantic authority"
            )
        proxy_authority = _validate_operator_proxy_authority(
            proxy=proxy,
            episode_id=episode.name,
            source_hash=source_hash,
            audio_hash=audio_hash,
        )
        authority_mode = "episode_files_direct"
    else:
        timeline, semantic_subtitles, decision, proxy_authority = (
            _semantic_authority_from_contract(contract)
        )
        if rights is not None and rights.get("episode_id") != episode.name:
            raise Out07ReconstitutionError(
                "rights skeleton belongs to a different episode"
            )
        authority_mode = "tracked_rebuild_contract"
    resolved_ffmpeg, _ = ffmpeg_tiny.discover_ffmpeg(ffmpeg_path=ffmpeg_path)
    resolved_ffprobe, _ = ffmpeg_tiny.discover_ffprobe(ffprobe_path=ffprobe_path)
    if execute_media_checks and (not resolved_ffmpeg or not resolved_ffprobe):
        raise Out07ReconstitutionError(
            "ffmpeg and ffprobe are required for qualification"
        )
    media = (
        _qualify_media(
            source_video=source_video,
            source_audio=source_audio,
            ffmpeg_path=str(resolved_ffmpeg),
            ffprobe_path=str(resolved_ffprobe),
        )
        if execute_media_checks
        else {
            "probe": video_receipt_data.get("video_metadata") or {},
            "full_decode": {"status": "not_run_fixture"},
            "frame_fingerprints": [],
            "pcm_window_fingerprints": [],
        }
    )
    duration = float((media.get("probe") or {}).get("duration_seconds") or 0.0)
    if execute_media_checks and duration < 49.566:
        raise Out07ReconstitutionError(
            "source media does not cover the required timeline"
        )

    input_paths = [
        *(path for path in paths.values() if path.is_file()),
        contract_path,
        source_video,
        source_audio,
        video_sidecar,
        video_receipt,
        audio_sidecar,
        audio_receipt,
    ]
    receipt = {
        "schema_version": "clippipegen.media_revision_receipt.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": episode.name,
        "media_revision_id": MEDIA_REVISION_ID,
        "qualification_status": "same_underlying_source_identity_timing_compatible",
        "provider": SOURCE_PROVIDER,
        "provider_id": SOURCE_PROVIDER_ID,
        "canonical_source_url": SOURCE_URL,
        "acquisition_route": "yt-dlp-video",
        "source_video": {
            "material_id": SOURCE_MATERIAL_ID,
            "path": _relative(source_video, root),
            "sha256": source_hash,
            "byte_size": source_video.stat().st_size,
        },
        "source_audio": {
            "material_id": AUDIO_MATERIAL_ID,
            "path": _relative(source_audio, root),
            "sha256": audio_hash,
            "byte_size": source_audio.stat().st_size,
        },
        "historical_source_host_evidence": {
            "sha256": HISTORICAL_SOURCE_SHA256,
            "byte_equivalence_to_current_claimed": False,
            "role": "historical_source_host_evidence_only",
        },
        "identity_evidence": {
            "receipt_sidecar_ledger_hash_chain": "passed",
            "episode_authority_mode": authority_mode,
            "rights_url_provider_id": (
                "passed" if direct_authority else "tracked_contract_identity"
            ),
            "decision_packet_provider_id_and_material_ids": (
                "passed" if direct_authority else "tracked_contract_identity"
            ),
            "subtitle_track_provider_id_and_content": (
                "passed" if direct_authority else "tracked_contract_snapshot"
            ),
            "operator_proxy_authority": proxy_authority,
            "episode_id_agreement": "passed",
            "semantic_timeline_mapping": "passed",
        },
        "timeline_compatibility": {
            "status": "passed",
            "required_source_range_seconds": [2.453, 49.566],
            "ordered_cut_ids": list(complete.EXPECTED_CUT_IDS),
            "cut_source_ranges_seconds": [
                [2.453, 9.293],
                [12.329, 17.167],
                [22.606, 49.566],
            ],
            "sequence_boundaries_seconds": list(complete.EXPECTED_BOUNDARIES_SECONDS),
            "semantic_duration_seconds": complete.EXPECTED_DURATION_SECONDS,
            "subtitle_ids": list(complete.EXPECTED_SUBTITLE_IDS),
            "sub030_excluded": True,
        },
        "probe": media["probe"],
        "full_decode": media["full_decode"],
        "frame_fingerprints": media["frame_fingerprints"],
        "pcm_window_fingerprints": media["pcm_window_fingerprints"],
        "authority_files": {
            _relative(path, root): _sha256(path)
            for path in input_paths
            if path.is_file()
        },
        "acceptance_boundary": {
            "historical_output_acceptance_inherited": False,
            "reason": "source revision is identity-compatible but not byte-equivalent to historical input",
            "rights_status": "pending",
            "production_acceptance": False,
            "public_or_publishing_acceptance": False,
        },
    }
    return {
        "root": root,
        "episode": episode,
        "source_video": source_video,
        "source_audio": source_audio,
        "source_hash": source_hash,
        "audio_hash": audio_hash,
        "timeline": timeline,
        "semantic_subtitles": semantic_subtitles,
        "decision": decision,
        "proxy_authority": proxy_authority,
        "authority_mode": authority_mode,
        "receipt": receipt,
        "input_paths": input_paths,
    }


def _single_material(ledger: dict[str, Any], material_id: str) -> dict[str, Any]:
    matches = [
        item
        for item in (ledger.get("materials") or [])
        if item.get("id") == material_id
    ]
    if len(matches) != 1:
        raise Out07ReconstitutionError(
            f"material authority is missing or ambiguous: {material_id}"
        )
    return matches[0]


def _semantic_authority_from_contract(
    contract: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    snapshot = contract.get("semantic_authority_snapshot") or {}
    timeline = copy.deepcopy(snapshot.get("timeline") or [])
    subtitles = copy.deepcopy(snapshot.get("subtitles") or [])
    cut_decisions = copy.deepcopy(snapshot.get("cut_decisions") or [])
    proxy = copy.deepcopy(snapshot.get("operator_proxy_authority") or {})
    if [item.get("id") for item in timeline] != list(complete.EXPECTED_CUT_IDS):
        raise Out07ReconstitutionError("tracked cut authority is incomplete")
    if [item.get("id") for item in subtitles] != list(complete.EXPECTED_SUBTITLE_IDS):
        raise Out07ReconstitutionError("tracked subtitle authority is incomplete")
    if [item.get("cut_id") for item in cut_decisions] != list(
        complete.EXPECTED_CUT_IDS
    ):
        raise Out07ReconstitutionError("tracked cut decisions are incomplete")
    if any(
        item.get("source_segment_ids") != [f"seg_{index:06d}"]
        for index, item in enumerate(subtitles, start=1)
    ):
        raise Out07ReconstitutionError("tracked subtitle source mapping changed")
    _assert_close(timeline[-1].get("sequence_end_seconds"), 38.638, "contract duration")
    _assert_close(
        subtitles[-1].get("sequence_end_seconds"), 38.638, "contract subtitle duration"
    )
    if (
        proxy.get("target_cuts") != ["cut_002", "cut_003"]
        or proxy.get("rights_status") != "pending"
        or proxy.get("production_candidate") is not False
        or proxy.get("operator_fields_state") != "undecided"
    ):
        raise Out07ReconstitutionError("tracked operator proxy authority changed")
    decision = {
        "episode_id": contract.get("episode_id"),
        "source_identity": {
            "youtube_id": SOURCE_PROVIDER_ID,
            "source_url": SOURCE_URL,
            "source_video_material_id": SOURCE_MATERIAL_ID,
            "source_audio_material_id": AUDIO_MATERIAL_ID,
            "subtitle_track": "tracked-contract://semantic-authority-snapshot",
        },
        "decisions": cut_decisions,
    }
    return (
        timeline,
        subtitles,
        decision,
        {
            **proxy,
            "status": "validated_from_tracked_rebuild_contract",
            "role": "retained_limitation_authority_not_final_timing_authority",
        },
    )


def _validate_episode_identity(*, episode_id: str, values: dict[str, Any]) -> None:
    if any(value != episode_id for value in values.values()):
        raise Out07ReconstitutionError(
            f"episode identity does not agree across authority: {values}"
        )


def _validate_direct_authority_inventory(
    *, contract: dict[str, Any], paths: dict[str, Path]
) -> None:
    inventory = contract.get("authority_file_inventory") or {}
    expected = {
        "rights_manifest": paths["rights"],
        "transcript": paths["transcript"],
        "edit_pack": paths["edit_pack"],
        "cut_decision_packet": paths["decision"],
        "operator_proxy_authority": paths["proxy"],
        "official_subtitle_track": paths["subtitle_track"],
    }
    records = {str(item.get("id")): item for item in inventory.get("files") or []}
    if set(records) != set(expected):
        raise Out07ReconstitutionError("direct authority inventory is incomplete")
    for authority_id, path in expected.items():
        if records[authority_id].get("sha256") != _sha256(path):
            raise Out07ReconstitutionError(
                f"direct authority revision changed: {authority_id}"
            )


def _validate_subtitle_track_authority(
    *,
    transcript: dict[str, Any],
    subtitle_track: dict[str, Any],
    subtitle_track_path: Path,
) -> None:
    stt = transcript.get("stt") or {}
    params = stt.get("params") or {}
    expected_suffix = f"/{SOURCE_PROVIDER_ID}.ja.json3"
    if (
        stt.get("engine") != "subtitle_track"
        or stt.get("provider") != "youtube_subtitles"
        or stt.get("engine_version") != "youtube-json3"
        or not str(stt.get("model") or "").replace("\\", "/").endswith(expected_suffix)
        or not str(params.get("subtitle_track_path") or "")
        .replace("\\", "/")
        .endswith(expected_suffix)
    ):
        raise Out07ReconstitutionError("transcript subtitle-track provenance changed")
    events = list(subtitle_track.get("events") or [])
    segments = list(transcript.get("segments") or [])
    if len(events) != len(segments) or len(events) < 29:
        raise Out07ReconstitutionError("subtitle-track event coverage changed")

    def normalized(value: str) -> str:
        without_formatting = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", value)
        return re.sub(r"\s+", " ", without_formatting).strip()

    for index, (event, segment) in enumerate(zip(events, segments, strict=True)):
        text = normalized(
            "".join(str(item.get("utf8") or "") for item in event.get("segs") or [])
        )
        if text != normalized(str(segment.get("text") or "")):
            raise Out07ReconstitutionError(
                f"subtitle-track text differs from transcript at event {index}"
            )
        start = float(event.get("tStartMs") or 0) / 1000.0
        end = start + float(event.get("dDurationMs") or 0) / 1000.0
        _assert_close(segment.get("start_seconds"), start, f"track event {index}.start")
        _assert_close(segment.get("end_seconds"), end, f"track event {index}.end")
    if subtitle_track_path.stat().st_size <= 0:
        raise Out07ReconstitutionError("subtitle-track source is empty")


def _validate_operator_proxy_authority(
    *, proxy: dict[str, Any], episode_id: str, source_hash: str, audio_hash: str
) -> dict[str, Any]:
    media = proxy.get("source_media_status") or {}
    video = media.get("source_video") or {}
    audio = media.get("source_audio") or {}
    flags = proxy.get("boundary_flags") or {}
    cuts = {str(item.get("cut_id")): item for item in proxy.get("cuts") or []}
    if (
        proxy.get("artifact_kind") != "operator_proxy_decision_handoff_v0"
        or proxy.get("episode_id") != episode_id
        or proxy.get("target_cuts") != ["cut_002", "cut_003"]
        or video.get("material_id") != SOURCE_MATERIAL_ID
        or video.get("sha256") != source_hash
        or audio.get("material_id") != AUDIO_MATERIAL_ID
        or audio.get("sha256") != audio_hash
        or flags.get("production_candidate") is not False
        or flags.get("creative_acceptance") is not False
        or flags.get("publish_acceptance") is not False
        or flags.get("rights_status") != "pending"
        or set(cuts) != {"cut_002", "cut_003"}
    ):
        raise Out07ReconstitutionError("operator proxy authority changed")
    for cut_id, expected_context, retained_risk in (
        ("cut_002", "passed", False),
        ("cut_003", "needs_review", True),
    ):
        cut = cuts[cut_id]
        fields = cut.get("operator_input_fields") or {}
        if (
            cut.get("context_status") != expected_context
            or cut.get("retained_context_risk") is not retained_risk
            or fields.get("proxy_decision") != "undecided"
            or fields.get("boundary_request") != "none"
            or fields.get("analyst_action") != "noop"
            or fields.get("downstream_target") != "none"
        ):
            raise Out07ReconstitutionError(
                f"operator proxy limitation changed for {cut_id}"
            )
    return {
        "status": "validated_directly",
        "target_cuts": ["cut_002", "cut_003"],
        "rights_status": "pending",
        "production_candidate": False,
        "operator_fields_state": "undecided",
        "role": "retained_limitation_authority_not_final_timing_authority",
    }


def _validate_material_chain(
    *,
    entry: dict[str, Any],
    sidecar: dict[str, Any],
    receipt: dict[str, Any],
    material_id: str,
    path: Path,
    sha256: str,
    root: Path,
    expected_mode: str,
    allow_mode_prefix: bool = False,
) -> None:
    relative = _relative(path, root)
    values = (
        entry.get("hash_sha256"),
        sidecar.get("asset_hash_sha256"),
        receipt.get("sha256"),
    )
    if any(value != sha256 for value in values):
        raise Out07ReconstitutionError(
            f"{material_id} receipt/sidecar/ledger hash mismatch"
        )
    if (
        entry.get("id") != material_id
        or sidecar.get("asset_id") != material_id
        or receipt.get("material_id") != material_id
    ):
        raise Out07ReconstitutionError(f"{material_id} identity mismatch")
    recorded_paths = (
        entry.get("file_path"),
        sidecar.get("asset_path"),
        receipt.get("output_path"),
    )
    if any(value != relative for value in recorded_paths):
        raise Out07ReconstitutionError(f"{material_id} path mismatch")
    mode = str(receipt.get("mode") or "")
    mode_ok = (
        mode.startswith(expected_mode) if allow_mode_prefix else mode == expected_mode
    )
    if not mode_ok:
        raise Out07ReconstitutionError(f"{material_id} acquisition route mismatch")


def _semantic_timeline(
    *,
    edit_pack: dict[str, Any],
    transcript: dict[str, Any],
    decision: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    expected = (
        ("cut_001", 2.453, 9.293, 0.000, 6.840, "sequence_start"),
        ("cut_002", 12.329, 17.167, 6.840, 11.678, "hard_cut"),
        ("cut_003", 22.606, 49.566, 11.678, 38.638, "hard_cut"),
    )
    cuts_by_id = {
        str(item.get("id")): item for item in edit_pack.get("cut_candidates") or []
    }
    decisions_by_id = {
        str(item.get("cut_id")): item for item in decision.get("decisions") or []
    }
    timeline: list[dict[str, Any]] = []
    for (
        cut_id,
        source_start,
        source_end,
        sequence_start,
        sequence_end,
        transition,
    ) in expected:
        cut = cuts_by_id.get(cut_id)
        cut_decision = decisions_by_id.get(cut_id)
        if cut is None or cut_decision is None:
            raise Out07ReconstitutionError(f"{cut_id} authority is missing")
        _assert_close(cut.get("start_seconds"), source_start, f"{cut_id}.start")
        _assert_close(cut.get("end_seconds"), source_end, f"{cut_id}.end")
        if cut_decision.get("final_cut_decision") != "keep":
            raise Out07ReconstitutionError(f"{cut_id} is no longer a kept cut")
        if cut_id == "cut_003":
            if (
                (cut.get("context_check") or {}).get("status") != "needs_review"
                or cut_decision.get("context_status") != "needs_review"
                or not str(cut_decision.get("manual_override_reason") or "").strip()
            ):
                raise Out07ReconstitutionError(
                    "cut_003 retained limitation authority changed"
                )
        elif cut_decision.get("context_status") != "passed":
            raise Out07ReconstitutionError(f"{cut_id} context authority changed")
        timeline.append(
            {
                "id": cut_id,
                "source_start_seconds": source_start,
                "source_end_seconds": source_end,
                "sequence_start_seconds": sequence_start,
                "sequence_end_seconds": sequence_end,
                "duration_seconds": round(source_end - source_start, 3),
                "transition_in": transition,
                "context_status": cut_decision.get("context_status"),
            }
        )

    subtitles = list(edit_pack.get("subtitles") or [])
    selected = [
        item
        for item in subtitles
        if str(item.get("id")) in complete.EXPECTED_SUBTITLE_IDS
    ]
    if (
        tuple(str(item.get("id")) for item in selected)
        != complete.EXPECTED_SUBTITLE_IDS
    ):
        raise Out07ReconstitutionError(
            "subtitles must be exactly ordered sub_001..sub_029"
        )
    sub030 = [item for item in subtitles if item.get("id") == "sub_030"]
    if len(sub030) != 1 or sub030[0].get("cut_id") == "cut_003":
        raise Out07ReconstitutionError("sub_030 exclusion authority changed")
    segment_by_id = {
        str(item.get("id")): item for item in transcript.get("segments") or []
    }
    timeline_by_id = {item["id"]: item for item in timeline}
    semantic: list[dict[str, Any]] = []
    for index, subtitle in enumerate(selected, start=1):
        subtitle_id = f"sub_{index:03d}"
        segment_id = f"seg_{index:06d}"
        if subtitle.get("id") != subtitle_id:
            raise Out07ReconstitutionError("subtitle ID ordering changed")
        if list(subtitle.get("source_segment_ids") or []) != [segment_id]:
            raise Out07ReconstitutionError(f"{subtitle_id} source mapping changed")
        segment = segment_by_id.get(segment_id)
        if segment is None or segment.get("review_status") != "accepted":
            raise Out07ReconstitutionError(
                f"{segment_id} is not accepted transcript authority"
            )
        if subtitle.get("text") != segment.get("text"):
            raise Out07ReconstitutionError(
                f"{subtitle_id} text changed from transcript"
            )
        for field in ("start_seconds", "end_seconds"):
            _assert_close(
                subtitle.get(field), segment.get(field), f"{subtitle_id}.{field}"
            )
        cut_id = str(subtitle.get("cut_id") or "")
        cut = timeline_by_id.get(cut_id)
        if cut is None:
            raise Out07ReconstitutionError(
                f"{subtitle_id} moved outside the selected cuts"
            )
        source_start = float(subtitle["start_seconds"])
        source_end = float(subtitle["end_seconds"])
        sequence_start = (
            float(cut["sequence_start_seconds"])
            + source_start
            - float(cut["source_start_seconds"])
        )
        sequence_end = (
            float(cut["sequence_start_seconds"])
            + source_end
            - float(cut["source_start_seconds"])
        )
        semantic.append(
            {
                "id": subtitle_id,
                "cut_id": cut_id,
                "source_start_seconds": source_start,
                "source_end_seconds": source_end,
                "sequence_start_seconds": round(sequence_start, 3),
                "sequence_end_seconds": round(sequence_end, 3),
                "text": str(subtitle["text"]),
                "source_type": str(subtitle.get("source_type") or ""),
                "source_segment_ids": [segment_id],
            }
        )
    _assert_close(semantic[-1]["sequence_end_seconds"], 38.638, "semantic duration")
    return timeline, semantic


def _qualify_media(
    *, source_video: Path, source_audio: Path, ffmpeg_path: str, ffprobe_path: str
) -> dict[str, Any]:
    probe_command = [
        ffprobe_path,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(source_video),
    ]
    probe_result = _run_text(probe_command, "source ffprobe")
    probe_payload = json.loads(probe_result.stdout)
    streams = list(probe_payload.get("streams") or [])
    video_streams = [item for item in streams if item.get("codec_type") == "video"]
    audio_streams = [item for item in streams if item.get("codec_type") == "audio"]
    if len(video_streams) != 1 or len(audio_streams) != 1:
        raise Out07ReconstitutionError(
            "source must contain exactly one video and one audio stream"
        )
    video = video_streams[0]
    audio = audio_streams[0]
    duration = float((probe_payload.get("format") or {}).get("duration") or 0.0)
    frame_rate = str(video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1")
    numerator, denominator = frame_rate.split("/", maxsplit=1)
    fps = float(numerator) / float(denominator)
    probe = {
        "container": str((probe_payload.get("format") or {}).get("format_name") or ""),
        "duration_seconds": round(duration, 6),
        "start_time_seconds": round(
            float((probe_payload.get("format") or {}).get("start_time") or 0.0), 6
        ),
        "video": {
            "codec": video.get("codec_name"),
            "width": int(video.get("width") or 0),
            "height": int(video.get("height") or 0),
            "fps": round(fps, 6),
            "start_time_seconds": round(float(video.get("start_time") or 0.0), 6),
            "duration_seconds": round(float(video.get("duration") or duration), 6),
        },
        "audio": {
            "codec": audio.get("codec_name"),
            "channels": int(audio.get("channels") or 0),
            "sample_rate": int(audio.get("sample_rate") or 0),
            "start_time_seconds": round(float(audio.get("start_time") or 0.0), 6),
            "duration_seconds": round(float(audio.get("duration") or duration), 6),
        },
    }
    if (
        probe["video"]["codec"] != "h264"
        or probe["audio"]["codec"] != "aac"
        or (probe["video"]["width"], probe["video"]["height"]) != (1920, 1080)
        or abs(float(probe["video"]["fps"]) - 30.0) > 0.001
    ):
        raise Out07ReconstitutionError("source stream properties changed")

    null_target = "NUL" if os.name == "nt" else "/dev/null"
    decode_result = _run_text(
        [
            ffmpeg_path,
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(source_video),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-f",
            "null",
            null_target,
        ],
        "source full decode",
        timeout=1200,
    )
    frame_fingerprints = []
    for seconds in FRAME_FINGERPRINT_TIMES:
        raw = _run_binary(
            [
                ffmpeg_path,
                "-hide_banner",
                "-v",
                "error",
                "-ss",
                f"{seconds:.3f}",
                "-i",
                str(source_video),
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
            f"frame fingerprint {seconds:.3f}",
        )
        if len(raw) != 320 * 180 * 3:
            raise Out07ReconstitutionError(
                "decoded frame fingerprint byte count changed"
            )
        frame_fingerprints.append(
            {
                "source_seconds": seconds,
                "canonical_decode": "raw_rgb24_320x180_bilinear",
                "byte_count": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    pcm_fingerprints = []
    for label, seconds, duration_seconds in PCM_FINGERPRINT_WINDOWS:
        raw = _run_binary(
            [
                ffmpeg_path,
                "-hide_banner",
                "-v",
                "error",
                "-ss",
                f"{seconds:.3f}",
                "-t",
                f"{duration_seconds:.3f}",
                "-i",
                str(source_video),
                "-map",
                "0:a:0",
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "pcm_s16le",
                "-f",
                "s16le",
                "pipe:1",
            ],
            f"PCM fingerprint {label}",
        )
        expected_samples = round(duration_seconds * 16000)
        if abs(len(raw) - expected_samples * 2) > 4:
            raise Out07ReconstitutionError(
                "canonical PCM fingerprint byte count changed"
            )
        pcm_fingerprints.append(
            {
                "label": label,
                "source_start_seconds": seconds,
                "duration_seconds": duration_seconds,
                "canonical_decode": "mono_pcm_s16le_16000hz",
                "byte_count": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    audio_decode = _run_text(
        [
            ffmpeg_path,
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(source_audio),
            "-f",
            "null",
            null_target,
        ],
        "source audio full decode",
        timeout=1200,
    )
    return {
        "probe": probe,
        "full_decode": {
            "status": "passed",
            "video_audio_exit_code": decode_result.returncode,
            "video_audio_stderr_empty": not decode_result.stderr.strip(),
            "render_source_audio_exit_code": audio_decode.returncode,
            "render_source_audio_stderr_empty": not audio_decode.stderr.strip(),
        },
        "frame_fingerprints": frame_fingerprints,
        "pcm_window_fingerprints": pcm_fingerprints,
    }


def build_reinstantiated_baseline(
    *,
    authority: dict[str, Any],
    output_dir: str | Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    render_executor: RenderExecutor | None = None,
    post_render_executor: PostRenderExecutor | None = None,
) -> dict[str, Any]:
    """Render one revision-qualified 38.638 second baseline component."""

    root = Path(authority["root"]).resolve()
    episode = Path(authority["episode"]).resolve()
    output = _resolved(root, Path(output_dir))
    expected_output = episode / "review" / BASELINE_OUTPUT_NAME
    if output != expected_output:
        raise Out07ReconstitutionError(f"baseline output must be {expected_output}")
    for path in authority["input_paths"]:
        _reject_overlap(
            output, Path(path), "baseline output overlaps an authority input"
        )
    input_hashes_before = {
        _relative(Path(path), root): _sha256(Path(path))
        for path in authority["input_paths"]
    }

    layout, subtitle_items, selector = build_vertical_subtitle_presentation(
        authority["semantic_subtitles"],
        application_key="out07_reinstantiation_application",
        dimension_source="out07_reinstantiated_vertical_canvas",
    )
    font_style = layout["diagnostic_ass_style"]
    font_file = Path(str(font_style.get("resolved_font_file") or ""))
    if (
        str(font_style.get("font_name") or "").casefold() != "keifont"
        or font_file.name.casefold() != "keifont.ttf"
        or not font_file.is_file()
        or _sha256(font_file) != KEIFONT_SHA256
    ):
        raise Out07ReconstitutionError(
            "the revision rebuild requires the frozen Keifont dependency"
        )
    containment = validate_vertical_subtitle_containment(
        subtitle_items,
        expected_duration=complete.EXPECTED_DURATION_SECONDS,
        layout=layout,
        expected_count=29,
    )
    _validate_reviewed_wraps(subtitle_items)
    plan = _baseline_plan(authority=authority, subtitle_items=subtitle_items)

    review_dir = _ensure_review_directory(episode)
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    backup: Path | None = None
    try:
        stage.mkdir(parents=False, exist_ok=False)
        assets = stage / "assets"
        work = stage / ".work"
        assets.mkdir()
        work.mkdir()
        ass_path = stage / "reinstantiated_baseline_subtitles.ass"
        srt_path = stage / "reinstantiated_baseline_subtitles.srt"
        plan_path = stage / "baseline_sequence_plan.json"
        receipt_path = stage / "media_revision_receipt.json"
        readback_path = stage / "baseline_readback.json"
        video_path = assets / "reinstantiated_baseline.mp4"
        poster_path = assets / "baseline_poster_frame.jpg"
        frame_sheet_path = assets / "baseline_frame_qa_contact_sheet.jpg"

        _write_ass(ass_path, subtitle_items, layout=layout, review_label=None)
        _write_text(srt_path, complete._render_srt(subtitle_items))
        _write_json(plan_path, plan)
        _write_json(receipt_path, authority["receipt"])
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
            source_video_path=authority["source_video"],
            source_audio_path=authority["source_audio"],
            timeline=authority["timeline"],
            ass_path=ass_path,
            video_path=video_path,
            compare_sheet_path=None,
            frame_sheet_path=frame_sheet_path,
            work_dir=work,
            subtitle_layout=layout,
            expected_duration=complete.EXPECTED_DURATION_SECONDS,
            frame_samples=complete.FRAME_SAMPLES,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=subprocess.run,
        )
        validate_vertical_render_result(
            render_result,
            video_path=video_path,
            expected_duration=complete.EXPECTED_DURATION_SECONDS,
        )
        post_executor = post_render_executor or complete._post_render_assets
        post_render = post_executor(
            video_path=video_path,
            poster_path=poster_path,
            boundaries=complete.EXPECTED_BOUNDARIES_SECONDS,
            expected_duration=complete.EXPECTED_DURATION_SECONDS,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=subprocess.run,
        )
        if post_render.get("status") != "passed":
            raise Out07ReconstitutionError("baseline boundary QA did not pass")
        visual_qa = (
            _baseline_visual_qa(video_path=video_path, ffmpeg_path=ffmpeg_path)
            if render_executor is None
            else {"status": "not_run_fixture", "samples": []}
        )
        _cleanup_internal_directory(work, expected_parent=stage)

        input_hashes_after = {
            _relative(Path(path), root): _sha256(Path(path))
            for path in authority["input_paths"]
        }
        if input_hashes_after != input_hashes_before:
            raise Out07ReconstitutionError(
                "authority input changed during baseline render"
            )
        output_hash = _sha256(video_path)
        byte_identical = output_hash == HISTORICAL_ACCEPTED_BASELINE_SHA256
        plan["cut003_limitation"]["new_human_acceptance_required"] = not byte_identical
        plan["boundaries"] = _closed_gates(human_baseline_acceptance=byte_identical)
        _write_json(plan_path, plan)
        acceptance = {
            "historical_accepted_sha256": HISTORICAL_ACCEPTED_BASELINE_SHA256,
            "output_sha256": output_hash,
            "byte_identical_to_historical_accepted_output": byte_identical,
            "classification": (
                "historical_byte_identical_acceptance_carried_forward"
                if byte_identical
                else "reinstantiated_baseline_candidate"
            ),
            "historical_human_acceptance_inherited": byte_identical,
            "human_acceptance": byte_identical,
        }
        readback = {
            "schema_version": "clippipegen.out07.reinstantiated_baseline.v0",
            "artifact_id": ARTIFACT_ID,
            "component_id": "reinstantiated_baseline",
            "state": acceptance["classification"],
            "episode_id": episode.name,
            "media_revision_id": MEDIA_REVISION_ID,
            "source_identity": {
                "provider": SOURCE_PROVIDER,
                "provider_id": SOURCE_PROVIDER_ID,
                "current_source_sha256": authority["source_hash"],
                "historical_source_host_sha256": HISTORICAL_SOURCE_SHA256,
                "same_underlying_source_identity": True,
                "byte_equivalence_claimed": False,
            },
            "timeline": {
                "ordered_cut_ids": list(complete.EXPECTED_CUT_IDS),
                "semantic_duration_seconds": complete.EXPECTED_DURATION_SECONDS,
                "hard_cut_boundaries_seconds": list(
                    complete.EXPECTED_BOUNDARIES_SECONDS
                ),
                "cuts": authority["timeline"],
            },
            "subtitle": {
                "count": 29,
                "ids": list(complete.EXPECTED_SUBTITLE_IDS),
                "sub030_excluded": True,
                "reviewed_wrap_lines": EXPECTED_WRAP_LINES,
                "font_family": layout["diagnostic_ass_style"].get("font_name"),
                "font_file": layout["diagnostic_ass_style"].get("resolved_font_file"),
                "font_file_status": layout["diagnostic_ass_style"].get(
                    "font_file_status"
                ),
                "font_file_sha256": KEIFONT_SHA256,
                "layout": layout,
                "selector": selector,
                "containment": containment,
                "items": subtitle_items,
            },
            "render": {
                "path": _relative(output / "assets/reinstantiated_baseline.mp4", root),
                "sha256": output_hash,
                "media": render_result["media"],
                "selected_video_encoder": render_result["selected_video_encoder"],
                "attempts": render_result["attempts"],
                "full_decode": render_result["full_decode"],
                "duration_matches_expected": render_result["duration_matches_expected"],
                "faststart": render_result.get("faststart"),
                "audio": render_result["audio"],
            },
            "quality_assurance": {
                "frame_contact_sheet": _relative(
                    output / "assets/baseline_frame_qa_contact_sheet.jpg", root
                ),
                "frame_samples": render_result["frame_samples"],
                "black_or_corrupt_frame_check": visual_qa,
                "boundary_analysis": post_render["boundary_analysis"],
                "sync": post_render["sync"],
            },
            "acceptance_inheritance": acceptance,
            "input_hashes": input_hashes_before,
            "media_revision_receipt": _relative(
                output / "media_revision_receipt.json", root
            ),
            "boundaries": _closed_gates(human_baseline_acceptance=byte_identical),
        }
        readback = _portable_payload(readback, root=root)
        _write_json(readback_path, readback)
        manifest = _component_manifest(stage=stage, output=output, root=root)
        _write_json(stage / "baseline_manifest.json", manifest)
        _validate_baseline_stage(stage)
        try:
            backup = _atomic_promote(stage, output)
        except PermissionError as exc:
            raise Out07ReconstitutionError(
                "baseline output is in use; stop only its confirmed preview server and rerun"
            ) from exc
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)
    return {
        "output_dir": output,
        "video_path": output / "assets/reinstantiated_baseline.mp4",
        "readback_path": output / "baseline_readback.json",
        "receipt_path": output / "media_revision_receipt.json",
        "publish_draft_path": _write_publish_draft(
            output=output,
            root=root,
            episode=episode,
            baseline_readback=_read_json(
                output / "baseline_readback.json", "baseline readback"
            ),
        ),
    }


def _baseline_plan(
    *, authority: dict[str, Any], subtitle_items: list[dict[str, Any]]
) -> dict[str, Any]:
    presentation_by_id = {str(item["subtitle_id"]): item for item in subtitle_items}
    mapping = []
    for semantic in authority["semantic_subtitles"]:
        shown = presentation_by_id[str(semantic["id"])]
        mapping.append(
            {
                "subtitle_id": semantic["id"],
                "cut_id": semantic["cut_id"],
                "source_segment_ids": semantic["source_segment_ids"],
                "source_start_seconds": semantic["source_start_seconds"],
                "source_end_seconds": semantic["source_end_seconds"],
                "semantic_sequence_start_seconds": semantic["sequence_start_seconds"],
                "semantic_sequence_end_seconds": semantic["sequence_end_seconds"],
                "display_start_seconds": shown["display_start_seconds"],
                "display_end_seconds": shown["display_end_seconds"],
                "text": semantic["text"],
                "wrapped_lines": shown["wrapped_lines"],
            }
        )
    cut003 = next(
        item
        for item in authority["decision"].get("decisions") or []
        if item.get("cut_id") == "cut_003"
    )
    return {
        "schema_version": "clippipegen.out07.reinstantiated_baseline_plan.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": authority["episode"].name,
        "media_revision_id": MEDIA_REVISION_ID,
        "purpose": "Reinstantiate the fixed three-cut editorial decision from current episode authority for one combined human review.",
        "ordered_cut_ids": list(complete.EXPECTED_CUT_IDS),
        "semantic_duration_seconds": complete.EXPECTED_DURATION_SECONDS,
        "hard_cut_boundaries_seconds": list(complete.EXPECTED_BOUNDARIES_SECONDS),
        "timeline": authority["timeline"],
        "subtitle_count": 29,
        "subtitle_ids": list(complete.EXPECTED_SUBTITLE_IDS),
        "subtitle_mapping": mapping,
        "six_reviewed_wraps": EXPECTED_WRAP_LINES,
        "cut003_limitation": {
            "final_cut_decision": "keep",
            "context_status": "needs_review",
            "manual_override_reason": cut003.get("manual_override_reason"),
            "operator_proxy_authority": authority["proxy_authority"],
            "missing_historical_operator_proxy_patch": False,
            "new_human_acceptance_required": True,
        },
        "reframe": {
            "selected_option": "full_16_9_fit_source_derived_blurred_canvas",
            "route": "shared_vertical_render_primitive",
        },
        "boundaries": _closed_gates(),
    }


def _validate_reviewed_wraps(items: list[dict[str, Any]]) -> None:
    by_id = {str(item["subtitle_id"]): item for item in items}
    for subtitle_id, lines in EXPECTED_WRAP_LINES.items():
        if by_id.get(subtitle_id, {}).get("wrapped_lines") != lines:
            raise Out07ReconstitutionError(f"reviewed wrap changed: {subtitle_id}")


def _baseline_visual_qa(
    *, video_path: Path, ffmpeg_path: str | Path | None
) -> dict[str, Any]:
    from PIL import Image, ImageStat

    resolved_ffmpeg, _ = ffmpeg_tiny.discover_ffmpeg(ffmpeg_path=ffmpeg_path)
    if not resolved_ffmpeg:
        raise Out07ReconstitutionError("ffmpeg is required for baseline frame QA")
    samples = []
    for label, seconds in complete.FRAME_SAMPLES:
        png = _run_binary(
            [
                str(resolved_ffmpeg),
                "-hide_banner",
                "-v",
                "error",
                "-ss",
                f"{seconds:.3f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-f",
                "image2pipe",
                "-vcodec",
                "png",
                "pipe:1",
            ],
            f"baseline frame QA {label}",
        )
        try:
            with Image.open(io.BytesIO(png)) as image:
                rgb = image.convert("RGB")
                stat = ImageStat.Stat(rgb.resize((160, 284)))
                mean = sum(stat.mean) / 3.0
                extrema = rgb.getextrema()
                corrupt = rgb.size != (1080, 1920) or len(extrema) != 3
        except Exception as exc:
            raise Out07ReconstitutionError(
                f"baseline frame is corrupt: {label}"
            ) from exc
        black = mean < 4.0
        samples.append(
            {
                "label": label,
                "seconds": seconds,
                "mean_rgb": round(mean, 3),
                "black_frame": black,
                "corrupt_frame": corrupt,
                "status": "passed" if not black and not corrupt else "failed",
            }
        )
    if any(item["status"] != "passed" for item in samples):
        raise Out07ReconstitutionError("baseline black/corrupt frame QA failed")
    return {"status": "passed", "samples": samples}


def _write_publish_draft(
    *, output: Path, root: Path, episode: Path, baseline_readback: dict[str, Any]
) -> Path:
    copy_plan = copy.deepcopy(EPISODE_COPY_PLAN)
    draft = {
        "schema_version": "clippipegen.out07.publish_draft.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": episode.name,
        "status": "internal_operator_draft_reconstructed_from_tracked_copy_plan",
        "language": "ja",
        "title": copy_plan["title"],
        "description": "\n".join(copy_plan["description_lines"]),
        "tags": copy_plan["tags"],
        "evidence_trace": copy_plan["evidence_trace"],
        "video": {
            "path": _relative(output / "assets/reinstantiated_baseline.mp4", root),
            "sha256": baseline_readback["render"]["sha256"],
            "acceptance_class": baseline_readback["acceptance_inheritance"][
                "classification"
            ],
            "human_acceptance": baseline_readback["acceptance_inheritance"][
                "human_acceptance"
            ],
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
        "upload_attempted": False,
        "thumbnail_upload_attempted": False,
        "visibility_update_attempted": False,
        "metadata_update_attempted": False,
        "visibility": "operator_decision_required",
        "made_for_kids": "operator_decision_required",
        "scheduled_at": None,
    }
    path = output / "publish_draft.json"
    _write_json(path, draft)
    return path


def _rewrite_revision_mask_inspection_labels(*, stage: Path) -> None:
    """Keep compact labels local to the revision package's visual QA sheet."""

    from PIL import Image, ImageDraw

    paths = sorted(stage.glob("subject_*_rgba.png"))
    sheet_path = stage / "subject_mask_inspection.jpg"
    if not paths:
        raise Out07ReconstitutionError("revision subject assets are missing")
    with Image.open(sheet_path) as source:
        sheet = source.convert("RGB")
    cell_width = sheet.width // len(paths)
    draw = ImageDraw.Draw(sheet)
    font = poster._project_font(19)
    for index, path in enumerate(paths):
        x0 = index * cell_width
        draw.rectangle(
            (x0, 430, x0 + cell_width - 1, sheet.height - 1), fill=(18, 20, 24)
        )
        parts = path.stem.split("_")
        label = f"{parts[1]} / {'_'.join(parts[2:-1])}"
        draw.text((x0 + 8, 448), label, font=font, fill=(245, 245, 245))
        draw.text(
            (x0 + 8, 480),
            "large edge + reduced edge",
            font=font,
            fill=(185, 195, 210),
        )
    sheet.save(
        sheet_path,
        format="JPEG",
        quality=94,
        subsampling=0,
        optimize=False,
    )
    sheet.close()


def build_revision_poster_review(
    *,
    authority: dict[str, Any],
    baseline: dict[str, Any],
    output_dir: str | Path,
    reference_corpus_path: str | Path,
    reference_cache_dir: str | Path,
    fetch_missing_references: bool,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build one combined baseline-first A/B/C review from frozen inputs."""

    root = Path(authority["root"]).resolve()
    episode = Path(authority["episode"]).resolve()
    output = _resolved(root, Path(output_dir))
    expected_output = episode / "review" / COMBINED_OUTPUT_NAME
    if output != expected_output:
        raise Out07ReconstitutionError(f"combined output must be {expected_output}")
    cache = _resolved(root, Path(reference_cache_dir))
    expected_cache = episode / "review" / poster.REFERENCE_CACHE_NAME
    if cache != expected_cache:
        raise Out07ReconstitutionError(f"reference cache must be {expected_cache}")
    corpus_path = _resolved(root, Path(reference_corpus_path))
    baseline_video = Path(baseline["video_path"]).resolve()
    baseline_readback = Path(baseline["readback_path"]).resolve()
    media_receipt = Path(baseline["receipt_path"]).resolve()
    publish_path = Path(baseline["publish_draft_path"]).resolve()
    for label, path in (
        ("source video", authority["source_video"]),
        ("reinstantiated baseline", baseline_video),
        ("baseline readback", baseline_readback),
        ("media revision receipt", media_receipt),
        ("publish draft", publish_path),
        ("reference corpus", corpus_path),
    ):
        _require_file(Path(path), label)
        _reject_overlap(output, Path(path), "combined output overlaps an input")

    baseline_data = _read_json(baseline_readback, "baseline readback")
    publish = _read_json(publish_path, "publish draft")
    publish["_source_path"] = str(publish_path)
    publish["_reference_cache"] = str(cache)
    poster._validate_rejected_out07_truth(publish)
    if publish["video"]["sha256"] != _sha256(baseline_video):
        raise Out07ReconstitutionError("publish draft baseline hash changed")
    baseline_acceptance = baseline_data["acceptance_inheritance"]
    if (
        baseline_acceptance["human_acceptance"]
        is not baseline_acceptance["byte_identical_to_historical_accepted_output"]
    ):
        raise Out07ReconstitutionError(
            "baseline acceptance does not match the historical byte identity boundary"
        )
    metadata_copy_hash = poster._metadata_copy_hash(publish)
    corpus = _read_json(corpus_path, "reference corpus")
    references = poster._reference_entries(corpus)
    corpus_summary = poster.validate_reference_corpus(corpus)
    candidate_specs = poster.candidate_specs_from_corpus(corpus, references=references)
    poster.validate_candidate_specs(candidate_specs, references=references)

    cache.mkdir(parents=True, exist_ok=True)
    reference_inputs = poster._freeze_reference_inputs(
        references=references,
        cache_dir=cache,
        fetch_missing=fetch_missing_references,
    )
    input_paths = [
        Path(authority["source_video"]),
        baseline_video,
        baseline_readback,
        media_receipt,
        publish_path,
        corpus_path,
        *reference_inputs,
    ]
    input_hashes_before = {_relative(path, root): _sha256(path) for path in input_paths}
    resolved_ffmpeg, _ = ffmpeg_tiny.discover_ffmpeg(ffmpeg_path=ffmpeg_path)
    resolved_ffprobe, _ = ffmpeg_tiny.discover_ffprobe(ffprobe_path=ffprobe_path)
    if not resolved_ffmpeg or not resolved_ffprobe:
        raise Out07ReconstitutionError(
            "ffmpeg and ffprobe are required for poster proof"
        )

    review_dir = _ensure_review_directory(episode)
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    backup: Path | None = None
    try:
        stage.mkdir(parents=False, exist_ok=False)
        work = stage / ".work"
        frames = work / "source_frames"
        work.mkdir()
        frames.mkdir()
        extracted = poster._extract_source_frames(
            source_video=Path(authority["source_video"]),
            timestamps=poster._dense_survey_timestamps(candidate_specs),
            frame_dir=frames,
            ffmpeg_path=str(resolved_ffmpeg),
        )
        poster._write_expression_contact_sheets(
            frames=extracted,
            stage=stage,
            candidate_specs=candidate_specs,
        )
        poster._write_reference_board(
            references=references,
            reference_inputs=reference_inputs,
            out=stage / "reference_board.jpg",
        )
        candidate_records = poster._render_posters(
            frame_paths=extracted,
            candidate_specs=candidate_specs,
            stage=stage,
            output=output,
            root=root,
        )
        _rewrite_revision_mask_inspection_labels(stage=stage)
        poster._write_poster_contact_sheet(
            stage=stage,
            out=stage / "poster_direction_contact_sheet.jpg",
        )
        poster._write_platform_preview_contact_sheet(
            stage=stage,
            out=stage / "platform_preview_contact_sheet.jpg",
        )
        accepted_probe = poster._probe_media(
            baseline_video, ffprobe_path=str(resolved_ffprobe)
        )
        transition_records = poster._render_transitions(
            accepted_video=baseline_video,
            accepted_duration=float(accepted_probe["duration_seconds"]),
            stage=stage,
            output=output,
            root=root,
            ffmpeg_path=str(resolved_ffmpeg),
            ffprobe_path=str(resolved_ffprobe),
        )
        loop_probe = poster._render_loop_probe(
            accepted_video=baseline_video,
            transition_path=stage / "transition_A.mp4",
            stage=stage,
            output=output,
            root=root,
            ffmpeg_path=str(resolved_ffmpeg),
            ffprobe_path=str(resolved_ffprobe),
        )
        reference_manifest = poster._reference_manifest(
            corpus=corpus,
            corpus_summary=corpus_summary,
            references=references,
            candidate_specs=candidate_specs,
            reference_inputs=reference_inputs,
            root=root,
            reference_board=stage / "reference_board.jpg",
        )
        _augment_reference_manifest(
            manifest=reference_manifest,
            references=references,
            reference_inputs=reference_inputs,
        )
        _write_json(stage / "reference_manifest.json", reference_manifest)
        _cleanup_internal_directory(work, expected_parent=stage)

        shutil.copyfile(baseline_video, stage / "reinstantiated_baseline.mp4")
        shutil.copyfile(baseline_readback, stage / "baseline_readback.json")
        shutil.copyfile(media_receipt, stage / "media_revision_receipt.json")
        shutil.copyfile(publish_path, stage / "publish_draft.json")
        final_paths = poster._final_paths(output)
        final_paths["stage_reference_manifest"] = stage / "reference_manifest.json"
        readback = poster._build_readback(
            root=root,
            episode=episode,
            output=output,
            source_video=Path(authority["source_video"]),
            accepted_video=baseline_video,
            publish=publish,
            metadata_copy_hash=metadata_copy_hash,
            corpus_summary=corpus_summary,
            candidate_records=candidate_records,
            transition_records=transition_records,
            loop_probe=loop_probe,
            reference_manifest=reference_manifest,
            protected_before={},
            input_hashes=input_hashes_before,
            final_paths=final_paths,
        )
        _apply_revision_readback(
            readback=readback,
            root=root,
            output=output,
            authority=authority,
            baseline_data=baseline_data,
            reference_manifest=reference_manifest,
        )
        _write_json(stage / "poster_direction_readback.json", readback)
        _write_text(stage / "index.html", _combined_html(readback))
        _write_text(stage / "open_preview.ps1", poster._open_script())
        _write_text(stage / "serve_preview.ps1", poster._serve_script())
        _validate_revision_stage(
            stage=stage,
            baseline_sha256=_sha256(baseline_video),
        )
        input_hashes_after = {
            _relative(path, root): _sha256(path) for path in input_paths
        }
        if input_hashes_after != input_hashes_before:
            raise Out07ReconstitutionError(
                "frozen revision input changed during poster build"
            )
        try:
            backup = _atomic_promote(stage, output)
        except PermissionError as exc:
            raise Out07ReconstitutionError(
                "combined review is in use; stop only its confirmed preview server and rerun"
            ) from exc
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)
    return {
        "output_dir": output,
        "index_path": output / "index.html",
        "readback_path": output / "poster_direction_readback.json",
        "reference_manifest_path": output / "reference_manifest.json",
    }


def _augment_reference_manifest(
    *,
    manifest: dict[str, Any],
    references: list[dict[str, Any]],
    reference_inputs: list[Path],
) -> None:
    from PIL import Image

    by_id = {str(item["reference_id"]): item for item in manifest["references"]}
    evidence = []
    for source, path in zip(references, reference_inputs, strict=True):
        reference_id = str(source["reference_id"])
        with Image.open(path) as image:
            width, height = image.size
            image_format = str(image.format or "").upper()
        mime = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "WEBP": "image/webp",
        }.get(image_format, "application/octet-stream")
        item = by_id[reference_id]
        item.update(
            {
                "source_url": source["thumbnail_url"],
                "mime_type": mime,
                "width": width,
                "height": height,
                "fetch_status": "frozen_cache_verified",
                "fetch_failure": None,
            }
        )
        evidence.append(
            {
                "reference_id": reference_id,
                "url": source["thumbnail_url"],
                "mime_type": mime,
                "width": width,
                "height": height,
                "sha256": item["thumbnail_image_sha256"],
            }
        )
    evidence_digest = _canonical_digest(evidence)
    manifest["fetch_revision"] = {
        "revision_id": f"reference-cache-{evidence_digest[:16]}",
        "status": "frozen",
        "success_count": len(evidence),
        "failure_count": 0,
        "failures": [],
    }
    manifest["reference_evidence_digest"] = evidence_digest


def _apply_revision_readback(
    *,
    readback: dict[str, Any],
    root: Path,
    output: Path,
    authority: dict[str, Any],
    baseline_data: dict[str, Any],
    reference_manifest: dict[str, Any],
) -> None:
    baseline_acceptance = baseline_data["acceptance_inheritance"]
    baseline_human_acceptance = bool(baseline_acceptance["human_acceptance"])
    readback.update(
        {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": ARTIFACT_ID,
            "state": STATE,
            "source_class": "qualified_same_source_identity_new_media_revision",
            "review_question": POSTER_REVIEW_QUESTION,
            "review_questions": [BASELINE_REVIEW_QUESTION, POSTER_REVIEW_QUESTION],
            "media_revision": {
                "media_revision_id": MEDIA_REVISION_ID,
                "provider": SOURCE_PROVIDER,
                "provider_id": SOURCE_PROVIDER_ID,
                "current_source_sha256": authority["source_hash"],
                "historical_source_host_sha256": HISTORICAL_SOURCE_SHA256,
                "same_underlying_source_identity": True,
                "byte_equivalence_claimed": False,
                "receipt_path": _relative(output / "media_revision_receipt.json", root),
            },
            "baseline": {
                "path": _relative(output / "reinstantiated_baseline.mp4", root),
                "sha256": baseline_data["render"]["sha256"],
                "semantic_duration_seconds": complete.EXPECTED_DURATION_SECONDS,
                "classification": baseline_data["acceptance_inheritance"][
                    "classification"
                ],
                "historical_accepted_sha256": HISTORICAL_ACCEPTED_BASELINE_SHA256,
                "byte_identical_to_historical_accepted_output": baseline_data[
                    "acceptance_inheritance"
                ]["byte_identical_to_historical_accepted_output"],
                "historical_human_acceptance_inherited": baseline_human_acceptance,
                "human_acceptance": baseline_human_acceptance,
                "readback_path": _relative(output / "baseline_readback.json", root),
            },
            "reference_revision": {
                **reference_manifest["fetch_revision"],
                "reference_evidence_digest": reference_manifest[
                    "reference_evidence_digest"
                ],
            },
            "portability": {
                "remote_code_complete": True,
                "local_artifact_available": True,
                "cross_machine_resume_class": "reacquirable",
                "last_verified_host": _verified_host(),
                "active_rebuild_contract": "artifacts/ACTIVE_REBUILD.json",
            },
            "regeneration": {
                "frozen_inputs_required": True,
                "network_fetch_required_after_cache_freeze": False,
                "command": (
                    "uvx --with Pillow python -m src.cli.main reconstitute-out07-review "
                    f"--episode-dir {_relative(Path(authority['episode']), root)} "
                    "--reference-corpus docs/output_layer/OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json "
                    "--verify-determinism --format json"
                ),
            },
        }
    )
    readback["accepted_video"].update(
        {
            "acceptance_class": baseline_acceptance["classification"],
            "historical_acceptance_inherited": baseline_human_acceptance,
            "human_acceptance": baseline_human_acceptance,
        }
    )
    readback["gates"]["human_baseline_acceptance"] = baseline_human_acceptance
    readback["storage"].update(
        {
            "portable_across_clones": False,
            "rebuild_contract_portable": True,
            "cross_machine_resume_class": "reacquirable",
        }
    )


def _combined_html(readback: dict[str, Any]) -> str:
    html = poster._render_html(readback)
    html = html.replace("<title>", '<link rel="icon" href="data:,"><title>', 1)
    header_start = html.index("<header>")
    header_end = html.index("</header>", header_start) + len("</header>")
    baseline = readback["baseline"]
    baseline_status = (
        "historical byte-identical"
        if baseline["byte_identical_to_historical_accepted_output"]
        else "new media revision candidate / human acceptance pending"
    )
    acceptance_note = (
        "historical output hashとの完全一致により、既存の動画acceptanceだけを継承しています。"
        if baseline["byte_identical_to_historical_accepted_output"]
        else "旧動画のbyte acceptanceは自動継承していません。"
    )
    replacement = f"""<header><p class="status">OUT-07 combined review / rights pending / publishing disabled</p><h1>再構成baseline＋Shorts poster A／B／C</h1></header>
<section id="baseline-review"><h2>最初に 38.6秒の再構成動画を確認</h2><p class="question">{escape(BASELINE_REVIEW_QUESTION)}</p>
<p class="secondary">{escape(baseline_status)}。{escape(acceptance_note)}</p>
<video id="reinstantiated-baseline" controls preload="metadata" playsinline src="reinstantiated_baseline.mp4"></video></section>
<section id="poster-question"><h2>次に poster 方向を比較</h2><p class="question">{escape(POSTER_REVIEW_QUESTION)}</p></section>"""
    html = html[:header_start] + replacement + html[header_end:]
    evidence = f"""<details id="revision-evidence"><summary>media revision・fingerprints・hash・gate</summary>
<p>provider: <code>{SOURCE_PROVIDER}/{SOURCE_PROVIDER_ID}</code> / media revision: <code>{MEDIA_REVISION_ID}</code></p>
<p>current source: <code>{readback["media_revision"]["current_source_sha256"]}</code><br>historical source-host evidence: <code>{HISTORICAL_SOURCE_SHA256}</code><br>baseline: <code>{baseline["sha256"]}</code></p>
<p>同一 source identity と timing compatibility は認定済みですが、historical byte equivalence は主張していません。rights / production / public / upload gates は閉じたままです。</p>
<p><code>media_revision_receipt.json</code> / <code>baseline_readback.json</code> / <code>reference_manifest.json</code> / <code>poster_direction_readback.json</code></p>
</details>"""
    html = html.replace("<script>\nconst media=", evidence + "\n<script>\nconst media=")
    return html


def _validate_revision_stage(*, stage: Path, baseline_sha256: str) -> None:
    from PIL import Image

    expected = set(poster.REQUIRED_PACKAGE_FILES) | {
        "reinstantiated_baseline.mp4",
        "baseline_readback.json",
        "media_revision_receipt.json",
        "publish_draft.json",
    }
    names = {path.name for path in stage.iterdir() if path.is_file()}
    if names != expected:
        raise Out07ReconstitutionError("combined revision package file list mismatch")
    if _sha256(stage / "reinstantiated_baseline.mp4") != baseline_sha256:
        raise Out07ReconstitutionError(
            "packaged baseline is not byte-identical to component"
        )
    readback = _read_json(stage / "poster_direction_readback.json", "poster readback")
    if (
        readback["selected_thumbnail"] is not None
        or readback["current_recommendation"] is not None
        or readback["baseline"]["human_acceptance"]
        is not readback["baseline"]["byte_identical_to_historical_accepted_output"]
    ):
        raise Out07ReconstitutionError("combined review crossed a human decision gate")
    for candidate_id in ("A", "B", "C"):
        with Image.open(stage / f"poster_{candidate_id}_1080x1920.jpg") as image:
            if image.size != poster.CANVAS or image.mode != "RGB":
                raise Out07ReconstitutionError(
                    "poster dimensions or color mode changed"
                )
        for mask_path in stage.glob(f"subject_{candidate_id}_*_mask.png"):
            with Image.open(mask_path) as mask:
                if mask.mode != "L" or mask.getextrema() != (0, 255):
                    raise Out07ReconstitutionError(
                        "poster subject alpha mask is invalid"
                    )
    manifest = _read_json(stage / "reference_manifest.json", "reference manifest")
    if (
        manifest["fetch_revision"]["failure_count"] != 0
        or len(manifest["references"]) != 51
        or manifest["summary"]["reference_count"] != 50
        or manifest["summary"]["inactive_duplicate_reference_count"] != 1
        or not manifest.get("reference_evidence_digest")
    ):
        raise Out07ReconstitutionError("reference freeze manifest is incomplete")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if (
        html.count('class="candidate"') != 3
        or html.count("<video") != 4
        or html.count('class="question"') != 2
        or html.index('id="reinstantiated-baseline"') > html.index('id="candidates"')
        or "<details open" in html
    ):
        raise Out07ReconstitutionError("combined baseline-first review flow changed")


def reconstitute_out07_review(
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
    """Run qualification through a baseline-first combined review package."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(
        root,
        Path(output_dir)
        if output_dir is not None
        else episode / "review" / COMBINED_OUTPUT_NAME,
    )
    baseline_output = _resolved(
        root,
        Path(baseline_output_dir)
        if baseline_output_dir is not None
        else episode / "review" / BASELINE_OUTPUT_NAME,
    )
    cache = _resolved(
        root,
        Path(reference_cache_dir)
        if reference_cache_dir is not None
        else episode / "review" / poster.REFERENCE_CACHE_NAME,
    )
    authority = load_current_episode_authority(
        episode_dir=episode,
        base_dir=root,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
        execute_media_checks=True,
    )

    baseline = build_reinstantiated_baseline(
        authority=authority,
        output_dir=baseline_output,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )
    combined = build_revision_poster_review(
        authority=authority,
        baseline=baseline,
        output_dir=output,
        reference_corpus_path=reference_corpus_path,
        reference_cache_dir=cache,
        fetch_missing_references=fetch_missing_references,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )
    first_core = _deterministic_core_payload(output=output)
    first_core_digest = _canonical_digest(first_core)
    first_reference_digest = _reference_evidence_digest(output=output)
    second_core_digest = first_core_digest
    second_reference_digest = first_reference_digest

    if verify_determinism:
        baseline = build_reinstantiated_baseline(
            authority=authority,
            output_dir=baseline_output,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
        )
        combined = build_revision_poster_review(
            authority=authority,
            baseline=baseline,
            output_dir=output,
            reference_corpus_path=reference_corpus_path,
            reference_cache_dir=cache,
            fetch_missing_references=False,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
        )
        second_core = _deterministic_core_payload(output=output)
        second_core_digest = _canonical_digest(second_core)
        second_reference_digest = _reference_evidence_digest(output=output)
        if second_core_digest != first_core_digest:
            raise Out07ReconstitutionError(
                "same frozen inputs produced a different deterministic core digest"
            )
        if second_reference_digest != first_reference_digest:
            raise Out07ReconstitutionError(
                "same frozen reference cache produced a different evidence digest"
            )

    _finalize_combined_package(
        output=output,
        root=root,
        core_payload=_deterministic_core_payload(output=output),
        first_core_digest=first_core_digest,
        second_core_digest=second_core_digest,
        first_reference_digest=first_reference_digest,
        second_reference_digest=second_reference_digest,
        verified_twice=verify_determinism,
    )
    final_readback = _read_json(
        output / "poster_direction_readback.json", "combined review readback"
    )
    return {
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "output_dir": output,
        "baseline_output_dir": baseline_output,
        "index_path": output / "index.html",
        "readback_path": output / "poster_direction_readback.json",
        "manifest_path": output / "combined_review_manifest.json",
        "determinism_receipt_path": output / "determinism_receipt.json",
        "media_revision_receipt_path": output / "media_revision_receipt.json",
        "deterministic_core_digest": second_core_digest,
        "reference_evidence_digest": second_reference_digest,
        "readback": final_readback,
        "component": combined,
    }


CORE_FILE_NAMES = (
    "reinstantiated_baseline.mp4",
    "poster_A_1080x1920.jpg",
    "poster_B_1080x1920.jpg",
    "poster_C_1080x1920.jpg",
    "poster_direction_contact_sheet.jpg",
    "platform_preview_contact_sheet.jpg",
    "expression_contact_sheet_A.jpg",
    "expression_contact_sheet_B.jpg",
    "expression_contact_sheet_C.jpg",
    "subject_mask_inspection.jpg",
    "subject_A_hajime_rgba.png",
    "subject_A_hajime_mask.png",
    "subject_B_hajime_rgba.png",
    "subject_B_hajime_mask.png",
    "subject_B_noel_secondary_rgba.png",
    "subject_B_noel_secondary_mask.png",
    "subject_C_hajime_rgba.png",
    "subject_C_hajime_mask.png",
    "preview_A_channel_search_tile.jpg",
    "preview_A_center_4_5.jpg",
    "preview_A_shorts_ui_overlay.jpg",
    "preview_B_channel_search_tile.jpg",
    "preview_B_center_4_5.jpg",
    "preview_B_shorts_ui_overlay.jpg",
    "preview_C_channel_search_tile.jpg",
    "preview_C_center_4_5.jpg",
    "preview_C_shorts_ui_overlay.jpg",
    "transition_A.mp4",
    "transition_B.mp4",
    "transition_C.mp4",
    "loop_probe_A_tail_poster_start.mp4",
)


def _deterministic_core_payload(*, output: Path) -> dict[str, Any]:
    baseline = _read_json(output / "baseline_readback.json", "baseline readback")
    poster_readback = _read_json(
        output / "poster_direction_readback.json", "poster readback"
    )
    files = []
    for name in CORE_FILE_NAMES:
        path = output / name
        _require_file(path, f"deterministic core {name}")
        files.append(
            {
                "package_relative_path": name,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return {
        "schema_version": "clippipegen.out07.deterministic_core.v0",
        "artifact_id": ARTIFACT_ID,
        "media_revision_id": MEDIA_REVISION_ID,
        "source_sha256": CURRENT_SOURCE_SHA256,
        "timeline": baseline["timeline"],
        "subtitle_contract": {
            "count": baseline["subtitle"]["count"],
            "ids": baseline["subtitle"]["ids"],
            "reviewed_wrap_lines": baseline["subtitle"]["reviewed_wrap_lines"],
            "sub030_excluded": baseline["subtitle"]["sub030_excluded"],
        },
        "baseline_render": {
            "sha256": baseline["render"]["sha256"],
            "media": baseline["render"]["media"],
            "selected_video_encoder": baseline["render"]["selected_video_encoder"],
            "acceptance_inheritance": baseline["acceptance_inheritance"],
        },
        "poster_contract": [
            {
                "candidate_id": item["candidate_id"],
                "source_frame_timestamps": item["source_frame_timestamps"],
                "copy_evidence": item["copy_evidence"],
                "third_party_pixels_used": item["third_party_pixels_used"],
                "human_acceptance": item["human_acceptance"],
            }
            for item in poster_readback["candidates"]
        ],
        "files": files,
        "excluded_from_digest": [
            "absolute_paths",
            "staging_uuid",
            "generated_at",
            "ffmpeg_stderr",
            "reference_board_pixels",
            "reference_manifest",
            "reference_fetch_metadata",
            "preview_server_pid",
        ],
    }


def _reference_evidence_digest(*, output: Path) -> str:
    manifest = _read_json(output / "reference_manifest.json", "reference manifest")
    digest = str(manifest.get("reference_evidence_digest") or "")
    if len(digest) != 64:
        raise Out07ReconstitutionError("reference evidence digest is missing")
    return digest


def _finalize_combined_package(
    *,
    output: Path,
    root: Path,
    core_payload: dict[str, Any],
    first_core_digest: str,
    second_core_digest: str,
    first_reference_digest: str,
    second_reference_digest: str,
    verified_twice: bool,
) -> None:
    core_readback = {
        **core_payload,
        "deterministic_core_digest": second_core_digest,
    }
    _write_json(output / "deterministic_core_readback.json", core_readback)
    determinism = {
        "schema_version": "clippipegen.out07.determinism_receipt.v0",
        "artifact_id": ARTIFACT_ID,
        "media_revision_id": MEDIA_REVISION_ID,
        "same_frozen_inputs_build_count": 2 if verified_twice else 1,
        "deterministic_core": {
            "first_build_digest": first_core_digest,
            "second_build_digest": second_core_digest,
            "match": first_core_digest == second_core_digest,
            "status": "passed" if first_core_digest == second_core_digest else "failed",
        },
        "reference_evidence": {
            "first_build_digest": first_reference_digest,
            "second_build_digest": second_reference_digest,
            "match": first_reference_digest == second_reference_digest,
            "status": "passed"
            if first_reference_digest == second_reference_digest
            else "failed",
            "separated_from_deterministic_core": True,
        },
        "volatile_fields_excluded": core_payload["excluded_from_digest"],
    }
    _write_json(output / "determinism_receipt.json", determinism)

    readback_path = output / "poster_direction_readback.json"
    readback = _read_json(readback_path, "combined review readback")
    readback["determinism"] = {
        "deterministic_core_digest": second_core_digest,
        "reference_evidence_digest": second_reference_digest,
        "same_frozen_inputs_build_count": 2 if verified_twice else 1,
        "core_match": first_core_digest == second_core_digest,
        "reference_match": first_reference_digest == second_reference_digest,
        "receipt_path": _relative(output / "determinism_receipt.json", root),
        "core_readback_path": _relative(
            output / "deterministic_core_readback.json", root
        ),
    }
    readback["combined_review_manifest"] = _relative(
        output / "combined_review_manifest.json", root
    )
    _write_json(readback_path, readback)
    _write_text(output / "index.html", _combined_html(readback))
    manifest = _combined_manifest(
        output=output,
        root=root,
        human_baseline_acceptance=bool(readback["baseline"]["human_acceptance"]),
    )
    _write_json(output / "combined_review_manifest.json", manifest)
    _validate_final_package(output=output, manifest=manifest)


def _component_manifest(*, stage: Path, output: Path, root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.name == "baseline_manifest.json":
            continue
        relative = path.relative_to(stage).as_posix()
        files.append(
            {
                "package_relative_path": relative,
                "repo_relative_path": _relative(output / relative, root),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return {
        "schema_version": "clippipegen.out07.baseline_manifest.v0",
        "artifact_id": ARTIFACT_ID,
        "component_id": "reinstantiated_baseline",
        "files": files,
    }


def _combined_manifest(
    *, output: Path, root: Path, human_baseline_acceptance: bool
) -> dict[str, Any]:
    files = []
    for path in sorted(output.iterdir()):
        if not path.is_file() or path.name == "combined_review_manifest.json":
            continue
        files.append(
            {
                "package_relative_path": path.name,
                "repo_relative_path": _relative(path, root),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return {
        "schema_version": "clippipegen.out07.combined_review_manifest.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": EPISODE_ID,
        "media_revision_id": MEDIA_REVISION_ID,
        "state": STATE,
        "files": files,
        "third_party_reference_pixels": {
            "present_in_package": True,
            "candidate_pixel_reuse": False,
            "git_tracking_allowed": False,
        },
        "gates": _closed_gates(human_baseline_acceptance=human_baseline_acceptance),
    }


def _validate_baseline_stage(stage: Path) -> None:
    required = {
        "assets/reinstantiated_baseline.mp4",
        "assets/baseline_poster_frame.jpg",
        "assets/baseline_frame_qa_contact_sheet.jpg",
        "reinstantiated_baseline_subtitles.ass",
        "reinstantiated_baseline_subtitles.srt",
        "baseline_sequence_plan.json",
        "media_revision_receipt.json",
        "baseline_readback.json",
        "baseline_manifest.json",
    }
    actual = {
        path.relative_to(stage).as_posix()
        for path in stage.rglob("*")
        if path.is_file()
    }
    if actual != required:
        raise Out07ReconstitutionError("baseline component file list mismatch")
    readback = _read_json(stage / "baseline_readback.json", "baseline readback")
    if (
        readback["subtitle"]["count"] != 29
        or not readback["subtitle"]["sub030_excluded"]
    ):
        raise Out07ReconstitutionError("baseline subtitle contract changed")
    if readback["acceptance_inheritance"]["human_acceptance"] not in (True, False):
        raise Out07ReconstitutionError("baseline acceptance boundary is ambiguous")
    if re.search(
        r"(?<![A-Za-z])[A-Za-z]:[\\/]", json.dumps(readback, ensure_ascii=False)
    ):
        raise Out07ReconstitutionError("baseline readback contains a host path")


def _validate_final_package(*, output: Path, manifest: dict[str, Any]) -> None:
    required = {
        "combined_review_manifest.json",
        "determinism_receipt.json",
        "deterministic_core_readback.json",
        "media_revision_receipt.json",
        "baseline_readback.json",
        "publish_draft.json",
        "poster_direction_readback.json",
        "reference_manifest.json",
        "index.html",
        "open_preview.ps1",
        "serve_preview.ps1",
        "reinstantiated_baseline.mp4",
    }
    names = {path.name for path in output.iterdir() if path.is_file()}
    if not required.issubset(names):
        raise Out07ReconstitutionError("final combined package is incomplete")
    for item in manifest["files"]:
        path = output / item["package_relative_path"]
        if _sha256(path) != item["sha256"]:
            raise Out07ReconstitutionError("combined manifest payload hash mismatch")
    readback = _read_json(output / "poster_direction_readback.json", "final readback")
    if (
        not readback["determinism"]["core_match"]
        or not readback["determinism"]["reference_match"]
        or readback["baseline"]["human_acceptance"]
        is not readback["baseline"]["byte_identical_to_historical_accepted_output"]
    ):
        raise Out07ReconstitutionError("final determinism or acceptance gate failed")


def _closed_gates(*, human_baseline_acceptance: bool = False) -> dict[str, Any]:
    return {
        "internal_review_only": True,
        "human_baseline_acceptance": human_baseline_acceptance,
        "human_poster_selection_required": True,
        "production_candidate": False,
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "rights_status": "pending",
        "public_ready": False,
        "publishing": False,
        "publish_attempted": False,
        "upload_attempted": False,
    }


def _ensure_review_directory(episode: Path) -> Path:
    review_dir = episode / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    return review_dir


def _portable_payload(value: Any, *, root: Path) -> Any:
    if isinstance(value, dict):
        return {key: _portable_payload(item, root=root) for key, item in value.items()}
    if isinstance(value, list):
        return [_portable_payload(item, root=root) for item in value]
    if not isinstance(value, str):
        return value
    windows_absolute = bool(re.match(r"^[A-Za-z]:[\\/]", value))
    native = Path(value)
    if not windows_absolute and not native.is_absolute():
        return value
    if windows_absolute and os.name != "nt":
        name = PureWindowsPath(value).name
        return f"external_dependency/{name}"
    try:
        return native.resolve().relative_to(root).as_posix()
    except ValueError:
        name = native.name or PureWindowsPath(value).name
        return f"external_dependency/{name}"


def _verified_host() -> str:
    return socket.gethostname().strip() or "unknown-host"


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _run_text(
    command: list[str], label: str, *, timeout: int = 900
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Out07ReconstitutionError(f"{label} failed before exit") from exc
    if result.returncode != 0:
        raise Out07ReconstitutionError(f"{label} failed: {result.stderr[-1200:]}")
    return result


def _run_binary(command: list[str], label: str) -> bytes:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=900,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Out07ReconstitutionError(f"{label} failed before exit") from exc
    if result.returncode != 0:
        tail = result.stderr.decode("utf-8", errors="replace")[-1200:]
        raise Out07ReconstitutionError(f"{label} failed: {tail}")
    return result.stdout


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Out07ReconstitutionError(f"{label} is not readable JSON") from exc
    if not isinstance(payload, dict):
        raise Out07ReconstitutionError(f"{label} must be a JSON object")
    return payload


def _resolved(root: Path, path: Path) -> Path:
    return (path if path.is_absolute() else root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise Out07ReconstitutionError(f"{label} missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise Out07ReconstitutionError(f"{label} missing: {path}")


def _reject_overlap(output: Path, input_path: Path, message: str) -> None:
    try:
        output.relative_to(input_path)
        raise Out07ReconstitutionError(message)
    except ValueError:
        pass
    try:
        input_path.relative_to(output)
        raise Out07ReconstitutionError(message)
    except ValueError:
        pass


def _assert_close(actual: Any, expected: float, label: str) -> None:
    try:
        value = float(actual)
    except (TypeError, ValueError) as exc:
        raise Out07ReconstitutionError(f"{label} is not numeric") from exc
    if abs(value - expected) > 0.001:
        raise Out07ReconstitutionError(
            f"{label} changed: expected {expected:.3f}, got {value:.3f}"
        )
