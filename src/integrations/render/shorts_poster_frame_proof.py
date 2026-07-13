"""Reference-derived OUT-07 Shorts poster-frame direction proof.

The builder keeps the accepted OUT-06/OUT-07 video immutable.  It surveys a
frozen public-reference corpus, recomposes retained source pixels into exactly
three 9:16 poster directions, and renders short end-cap proofs for human review.
It never selects a winner, modifies the accepted video, uploads, publishes, or
grants production/rights acceptance.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import urllib.request
import uuid
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny
from src.integrations.render.operator_delivery_pack import _font_path
from src.integrations.render.vertical_short_candidate import (
    _atomic_promote,
    _cleanup_internal_directory,
    _relative,
    _sha256,
    _tree_digest,
    _write_text,
)


ARTIFACT_ID = "clip-out07-shorts-poster-frame-direction-proof-v0-001"
SCHEMA_VERSION = "clippipegen.out07.shorts_poster_frame_direction_proof.v0"
STATE = "out07_reference_fidelity_shorts_poster_directions_review_ready"
ACCEPTED_VIDEO_SHA256 = (
    "02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0"
)
SOURCE_VIDEO_SHA256 = "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
CANVAS = (1080, 1920)
CENTER_4_5_SAFE_RECT = (0, 285, 1080, 1635)
TAIL_DURATION_SECONDS = 1.75
END_CAP_DURATION_SECONDS = 0.50
TRANSITION_DISSOLVE_SECONDS = 0.12
AUDIO_FADE_SECONDS = 0.16
DEFAULT_PORT = 8071
OUTPUT_NAME = "out07_shorts_poster_frame_direction_proof"
REFERENCE_CACHE_NAME = "out07_shorts_poster_reference_cache"
REVIEW_QUESTION = (
    "A/B/Cのどれが実用候補に最も近いか、または全案不採用か。"
    "末尾posterの出現が不自然な場合だけ併記してください。"
)
SURVEY_INTERVAL_SECONDS = 0.15
SURVEY_WINDOWS = {
    "A": {"start": 21.606, "end": 24.640},
    "B": {"start": 24.109, "end": 27.477},
    "C": {"start": 25.477, "end": 28.378},
}
SUPERSEDED_CANDIDATES = (
    {
        "candidate_id": "A",
        "sha256": "7a314825a0be95d48801bc0d648615b81a340884c24273fa76abbf18395a3720",
        "status": "supervisor_reframe_required",
        "reason": "rounded rectangular scene screenshot panel",
    },
    {
        "candidate_id": "B",
        "sha256": "8ab9e01f81490a3571fa60f59041da73c7122d76673ad8409ecbc7e20d57eab2",
        "status": "supervisor_reframe_required",
        "reason": "two rounded rectangular scene screenshot panels",
    },
    {
        "candidate_id": "C",
        "sha256": "8d2f05a9fc31f25bd9b8cc20702766c0ea3cc902717efa451837aaec3609ccb2",
        "status": "supervisor_reframe_required",
        "reason": "rounded scene panel plus circular screenshot inset and speaker inversion",
    },
)


class ShortsPosterFrameProofError(Exception):
    """Raised when the proof cannot be built without boundary drift."""


def build_shorts_poster_frame_proof(
    *,
    episode_dir: str | Path,
    output_dir: str | Path,
    source_video_path: str | Path,
    accepted_video_path: str | Path,
    out07_publish_draft_path: str | Path,
    reference_corpus_path: str | Path,
    reference_cache_dir: str | Path,
    fetch_missing_references: bool = False,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build and atomically promote the ignored local poster proof package."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(root, Path(output_dir))
    source_video = _resolved(root, Path(source_video_path))
    accepted_video = _resolved(root, Path(accepted_video_path))
    out07_publish = _resolved(root, Path(out07_publish_draft_path))
    corpus_path = _resolved(root, Path(reference_corpus_path))
    cache = _resolved(root, Path(reference_cache_dir))
    _require_directory(episode, "episode directory")
    _validate_output_directory(episode, output)
    _validate_cache_directory(episode, cache)
    for path, label in (
        (source_video, "retained source video"),
        (accepted_video, "accepted OUT-07 video"),
        (out07_publish, "OUT-07 publish draft"),
        (corpus_path, "reference corpus"),
    ):
        _require_file(path, label)
        _reject_overlap(output, path, "proof output must not overlap an input")

    if _sha256(source_video) != SOURCE_VIDEO_SHA256:
        raise ShortsPosterFrameProofError("retained source video hash mismatch")
    if _sha256(accepted_video) != ACCEPTED_VIDEO_SHA256:
        raise ShortsPosterFrameProofError("accepted video hash mismatch")

    publish = _read_json(out07_publish, "OUT-07 publish draft")
    publish["_reference_cache"] = str(cache)
    _validate_rejected_out07_truth(publish)
    metadata_copy_hash = _metadata_copy_hash(publish)
    corpus = _read_json(corpus_path, "reference corpus")
    references = _reference_entries(corpus)
    corpus_summary = validate_reference_corpus(corpus)
    candidate_specs = candidate_specs_from_corpus(corpus, references=references)

    cache.mkdir(parents=True, exist_ok=True)
    reference_inputs = _freeze_reference_inputs(
        references=references,
        cache_dir=cache,
        fetch_missing=fetch_missing_references,
    )
    protected_paths = _protected_paths(episode, output=output, cache=cache)
    protected_before = {
        label: _tree_digest(path, root=root) for label, path in protected_paths.items()
    }
    input_paths = [
        source_video,
        accepted_video,
        out07_publish,
        corpus_path,
        *reference_inputs,
    ]
    input_hashes_before = {_relative(path, root): _sha256(path) for path in input_paths}

    resolved_ffmpeg, _ = ffmpeg_tiny.discover_ffmpeg(ffmpeg_path=ffmpeg_path)
    resolved_ffprobe, _ = ffmpeg_tiny.discover_ffprobe(ffprobe_path=ffprobe_path)
    if not resolved_ffmpeg or not resolved_ffprobe:
        raise ShortsPosterFrameProofError("ffmpeg and ffprobe are required")

    review_dir = episode / "review"
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    backup: Path | None = None
    try:
        stage.mkdir(parents=False, exist_ok=False)
        work = stage / ".work"
        frames = work / "source_frames"
        work.mkdir()
        frames.mkdir()

        extracted = _extract_source_frames(
            source_video=source_video,
            timestamps=_dense_survey_timestamps(candidate_specs),
            frame_dir=frames,
            ffmpeg_path=resolved_ffmpeg,
        )
        _write_expression_contact_sheets(
            frames=extracted,
            stage=stage,
            candidate_specs=candidate_specs,
        )
        _write_reference_board(
            references=references,
            reference_inputs=reference_inputs,
            out=stage / "reference_board.jpg",
        )

        candidate_records = _render_posters(
            frame_paths=extracted,
            candidate_specs=candidate_specs,
            stage=stage,
            output=output,
            root=root,
        )
        _write_poster_contact_sheet(
            stage=stage,
            out=stage / "poster_direction_contact_sheet.jpg",
        )
        _write_platform_preview_contact_sheet(
            stage=stage,
            out=stage / "platform_preview_contact_sheet.jpg",
        )

        accepted_probe = _probe_media(accepted_video, ffprobe_path=resolved_ffprobe)
        transition_records = _render_transitions(
            accepted_video=accepted_video,
            accepted_duration=float(accepted_probe["duration_seconds"]),
            stage=stage,
            output=output,
            root=root,
            ffmpeg_path=resolved_ffmpeg,
            ffprobe_path=resolved_ffprobe,
        )
        loop_probe = _render_loop_probe(
            accepted_video=accepted_video,
            transition_path=stage / "transition_A.mp4",
            stage=stage,
            output=output,
            root=root,
            ffmpeg_path=resolved_ffmpeg,
            ffprobe_path=resolved_ffprobe,
        )

        reference_manifest = _reference_manifest(
            corpus=corpus,
            corpus_summary=corpus_summary,
            references=references,
            candidate_specs=candidate_specs,
            reference_inputs=reference_inputs,
            root=root,
            reference_board=stage / "reference_board.jpg",
        )
        _write_json(stage / "reference_manifest.json", reference_manifest)
        _cleanup_internal_directory(work, expected_parent=stage)

        final_paths = _final_paths(output)
        final_paths["stage_reference_manifest"] = stage / "reference_manifest.json"
        readback = _build_readback(
            root=root,
            episode=episode,
            output=output,
            source_video=source_video,
            accepted_video=accepted_video,
            publish=publish,
            metadata_copy_hash=metadata_copy_hash,
            corpus_summary=corpus_summary,
            candidate_records=candidate_records,
            transition_records=transition_records,
            loop_probe=loop_probe,
            reference_manifest=reference_manifest,
            protected_before=protected_before,
            input_hashes=input_hashes_before,
            final_paths=final_paths,
        )
        _write_json(stage / "poster_direction_readback.json", readback)
        _write_text(stage / "index.html", _render_html(readback))
        _write_text(stage / "open_preview.ps1", _open_script())
        _write_text(stage / "serve_preview.ps1", _serve_script())
        _validate_package(stage)

        protected_after = {
            label: _tree_digest(path, root=root)
            for label, path in protected_paths.items()
        }
        if protected_after != protected_before:
            raise ShortsPosterFrameProofError(
                "protected predecessor changed during proof build"
            )
        input_hashes_after = {
            _relative(path, root): _sha256(path) for path in input_paths
        }
        if input_hashes_after != input_hashes_before:
            raise ShortsPosterFrameProofError("frozen proof input changed during build")
        try:
            backup = _atomic_promote(stage, output)
        except PermissionError as exc:
            raise ShortsPosterFrameProofError(
                "poster proof output is in use; stop only its confirmed preview server and rerun"
            ) from exc
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)

    final_readback = _read_json(
        output / "poster_direction_readback.json", "poster direction readback"
    )
    return {
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "output_dir": output,
        "index_path": output / "index.html",
        "readback_path": output / "poster_direction_readback.json",
        "readback": final_readback,
    }


def _reference_entries(corpus: dict[str, Any]) -> list[dict[str, Any]]:
    legacy = corpus.get("references")
    native = corpus.get("native_vertical_surface_references")
    if not isinstance(legacy, list) or not isinstance(native, list):
        raise ShortsPosterFrameProofError("reference corpus sections are missing")
    defaults = corpus.get("native_vertical_surface_defaults")
    if not isinstance(defaults, dict):
        raise ShortsPosterFrameProofError("native vertical defaults are missing")
    observed = date.fromisoformat(str(corpus["observed_at"]))
    entries: list[dict[str, Any]] = []
    for raw in [*legacy, *({**defaults, **entry} for entry in native)]:
        if not isinstance(raw, dict):
            raise ShortsPosterFrameProofError("reference entry must be an object")
        entry = dict(raw)
        entry.setdefault("active_for_structure_count", True)
        published = date.fromisoformat(str(entry["publication_date"]))
        entry.setdefault("days_since_publish", (observed - published).days)
        entry.setdefault("surface_type", entry["target_surface"])
        entry.setdefault("surface_evidence_path", None)
        entry.setdefault("visible_view_count", None)
        entry.setdefault("surface_visible_view_text", None)
        entry.setdefault("success_proxy_causality", False)
        entry.setdefault("face_occupancy_ratio", None)
        entry.setdefault("subject_position", "legacy_annotation_only")
        entry.setdefault("subject_center_normalized", None)
        entry.setdefault("secondary_subject_ratio", None)
        entry.setdefault("headline_bbox_normalized", None)
        entry.setdefault("text_line_count", int(entry["text_block_count"]))
        entry.setdefault("text_region", entry["text_scale_and_position"])
        entry.setdefault("background_detail_level", "legacy_annotation_only")
        entry.setdefault(
            "repeated_layout_usage",
            {"same_surface_family_count": None, "interpretation": "not_observed"},
        )
        entries.append(entry)
    return entries


def validate_reference_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    references = _reference_entries(corpus)
    active_references = [
        entry for entry in references if entry["active_for_structure_count"]
    ]
    if len(active_references) < 36:
        raise ShortsPosterFrameProofError("reference corpus must contain at least 36 entries")
    required = {
        "reference_id",
        "source_type",
        "public_url",
        "thumbnail_url",
        "channel",
        "video_title",
        "publication_date",
        "observed_at",
        "query_strategy",
        "target_surface",
        "surface_type",
        "character_count",
        "face_orientation",
        "face_occupancy",
        "face_occupancy_ratio",
        "subject_position",
        "subject_center_normalized",
        "secondary_subject_ratio",
        "layout_family",
        "text_block_count",
        "headline_bbox_normalized",
        "text_line_count",
        "text_scale_and_position",
        "text_region",
        "background_treatment",
        "background_detail_level",
        "hook_type",
        "content_fidelity_risk",
        "translation_note",
        "visible_view_count",
        "days_since_publish",
        "repeated_layout_usage",
        "success_proxy_causality",
        "active_for_structure_count",
    }
    ids: set[str] = set()
    query_strategies: set[str] = set()
    targets: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    channel_counts: dict[str, int] = {}
    publication_dates: list[date] = []
    native_channels: set[str] = set()
    native_exact_count = 0
    recent_native_exact_count = 0
    conventional_16_9_count = 0
    latest_cutoff = date.fromisoformat(str(corpus["latest_180_day_cutoff"]))
    for entry in references:
        if required - entry.keys():
            raise ShortsPosterFrameProofError(
                "reference entry is missing structural or surface annotations"
            )
        reference_id = str(entry["reference_id"])
        if reference_id in ids:
            raise ShortsPosterFrameProofError("reference IDs must be unique")
        ids.add(reference_id)
        if entry["source_type"] not in {"user_supplied", "research_collected"}:
            raise ShortsPosterFrameProofError("unsupported reference source_type")
        if not str(entry["public_url"]).startswith("https://"):
            raise ShortsPosterFrameProofError("reference public URL must use https")
        if entry["success_proxy_causality"] is not False:
            raise ShortsPosterFrameProofError("view proxy must not be causal proof")
        published = date.fromisoformat(str(entry["publication_date"]))
        if entry["active_for_structure_count"] is not True:
            continue
        channel = str(entry["channel"])
        channel_counts[channel] = channel_counts.get(channel, 0) + 1
        query_strategies.add(str(entry["query_strategy"]))
        target = str(entry["target_surface"])
        targets[target] = targets.get(target, 0) + 1
        family = str(entry["layout_family"])
        family_counts[family] = family_counts.get(family, 0) + 1
        publication_dates.append(published)
        if target == "native_vertical_exact_youtube_search_shorts_card":
            native_exact_count += 1
            native_channels.add(channel)
            recent_native_exact_count += int(published >= latest_cutoff)
            if not entry.get("surface_evidence_path"):
                raise ShortsPosterFrameProofError(
                    "native exact-surface reference lacks surface evidence"
                )
        if target == "conventional_16_9_secondary_reference":
            conventional_16_9_count += 1
    if len(query_strategies) < 2:
        raise ShortsPosterFrameProofError("at least two query strategies are required")
    if max(channel_counts.values()) > 3:
        raise ShortsPosterFrameProofError("one channel exceeds the three-reference cap")
    if native_exact_count < 12 or len(native_channels) < 6:
        raise ShortsPosterFrameProofError("native exact-surface coverage is insufficient")
    if recent_native_exact_count < 8:
        raise ShortsPosterFrameProofError("recent native exact-surface coverage is insufficient")
    if conventional_16_9_count * 2 >= len(active_references):
        raise ShortsPosterFrameProofError("16:9 references must remain below half")
    policy = corpus.get("success_proxy_policy", {})
    if policy.get("view_count_is_causal_proof") is not False:
        raise ShortsPosterFrameProofError("success proxy policy must reject causality")
    candidate_specs = candidate_specs_from_corpus(corpus, references=references)
    return {
        "reference_count": len(active_references),
        "stored_reference_count": len(references),
        "inactive_duplicate_reference_count": len(references) - len(active_references),
        "channel_count": len(channel_counts),
        "query_strategy_count": len(query_strategies),
        "native_vertical_exact_surface_count": native_exact_count,
        "native_vertical_exact_surface_channel_count": len(native_channels),
        "recent_180_day_native_vertical_exact_surface_count": recent_native_exact_count,
        "conventional_16_9_secondary_count": conventional_16_9_count,
        "conventional_16_9_ratio": round(
            conventional_16_9_count / len(active_references), 4
        ),
        "max_references_per_channel": max(channel_counts.values()),
        "date_coverage": [
            min(publication_dates).isoformat(),
            max(publication_dates).isoformat(),
        ],
        "target_surfaces": dict(sorted(targets.items())),
        "observed_family_counts": dict(sorted(family_counts.items())),
        "candidate_family_ids_derived_after_research": [
            spec["family_id"] for spec in candidate_specs
        ],
        "success_proxy_is_causal_proof": False,
    }


def candidate_specs_from_corpus(
    corpus: dict[str, Any], *, references: list[dict[str, Any]] | None = None
) -> tuple[dict[str, Any], ...]:
    raw_specs = corpus.get("candidate_directions")
    if not isinstance(raw_specs, list):
        raise ShortsPosterFrameProofError("research-derived candidate directions missing")
    specs = tuple(dict(spec) for spec in raw_specs)
    validate_candidate_specs(specs, references=references or _reference_entries(corpus))
    return specs


def validate_candidate_specs(
    specs: tuple[dict[str, Any], ...], *, references: list[dict[str, Any]]
) -> None:
    if len(specs) != 3 or [spec["candidate_id"] for spec in specs] != ["A", "B", "C"]:
        raise ShortsPosterFrameProofError("exactly candidates A, B and C are required")
    if len({spec["family_id"] for spec in specs}) != 3:
        raise ShortsPosterFrameProofError("candidate composition families must be distinct")
    reference_by_id = {str(entry["reference_id"]): entry for entry in references}
    sx0, sy0, sx1, sy1 = CENTER_4_5_SAFE_RECT
    for spec in specs:
        bounds = spec["essential_bounds"]
        x0, y0, x1, y1 = map(int, bounds)
        if not (sx0 <= x0 < x1 <= sx1 and sy0 <= y0 < y1 <= sy1):
            raise ShortsPosterFrameProofError(
                "candidate essential content leaves center 4:5 safe area"
            )
        if not 1 <= int(spec["essential_text_block_count"]) <= 2:
            raise ShortsPosterFrameProofError(
                "candidate must use one or two essential text blocks"
            )
        if "back" in str(spec["dominant_face_orientation"]):
            raise ShortsPosterFrameProofError("dominant back-facing character is forbidden")
        reference_ids = [str(value) for value in spec["reference_ids"]]
        if len(reference_ids) < 3 or str(spec["primary_exemplar_id"]) not in reference_ids:
            raise ShortsPosterFrameProofError(
                "candidate must map a primary exemplar and supporting references"
            )
        if any(reference_id not in reference_by_id for reference_id in reference_ids):
            raise ShortsPosterFrameProofError("candidate reference mapping is unresolved")
        channels = {reference_by_id[reference_id]["channel"] for reference_id in reference_ids}
        if len(channels) < 2:
            raise ShortsPosterFrameProofError(
                "candidate references must cover at least two channels"
            )
        if spec.get("speaker") != spec.get("emotional_subject"):
            raise ShortsPosterFrameProofError(
                "dominant emotional subject must align with the speaker"
            )
        if not isinstance(spec.get("primary_exemplar_proportions"), dict):
            raise ShortsPosterFrameProofError("primary exemplar proportions missing")


def _freeze_reference_inputs(
    *, references: list[dict[str, Any]], cache_dir: Path, fetch_missing: bool
) -> list[Path]:
    from PIL import Image

    paths: list[Path] = []
    for entry in references:
        reference_id = str(entry["reference_id"])
        target = cache_dir / f"{reference_id}.jpg"
        if not target.is_file():
            if not fetch_missing:
                raise ShortsPosterFrameProofError(
                    f"frozen reference image missing: {reference_id}; rerun with explicit fetch"
                )
            request = urllib.request.Request(
                str(entry["thumbnail_url"]), headers={"User-Agent": "Mozilla/5.0"}
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    data = response.read()
            except Exception as exc:
                raise ShortsPosterFrameProofError(
                    f"public thumbnail fetch failed: {reference_id}"
                ) from exc
            if len(data) < 10_000:
                raise ShortsPosterFrameProofError(
                    f"public thumbnail response is unexpectedly small: {reference_id}"
                )
            target.write_bytes(data)
        try:
            with Image.open(target) as image:
                image.verify()
        except Exception as exc:
            raise ShortsPosterFrameProofError(
                f"frozen reference image is invalid: {reference_id}"
            ) from exc
        paths.append(target)
    return paths


def _extract_source_frames(
    *,
    source_video: Path,
    timestamps: tuple[float, ...],
    frame_dir: Path,
    ffmpeg_path: str,
) -> dict[float, Path]:
    outputs: dict[float, Path] = {}
    for index, seconds in enumerate(timestamps, start=1):
        out = frame_dir / f"frame_{index:03d}_{seconds:.3f}s.png"
        command = [
            ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(source_video),
            "-frames:v",
            "1",
            str(out),
        ]
        _run(command, label=f"source frame {seconds:.3f}s")
        _require_file(out, f"source frame {seconds:.3f}s")
        outputs[seconds] = out
    return outputs


def _dense_survey_timestamps(
    candidate_specs: tuple[dict[str, Any], ...]
) -> tuple[float, ...]:
    values: set[float] = set()
    for window in SURVEY_WINDOWS.values():
        count = int((window["end"] - window["start"]) / SURVEY_INTERVAL_SECONDS) + 1
        values.update(
            round(window["start"] + index * SURVEY_INTERVAL_SECONDS, 3)
            for index in range(count)
        )
    for spec in candidate_specs:
        values.update(round(float(value), 3) for value in spec["source_frame_timestamps"])
    return tuple(sorted(values))


def _render_posters(
    *,
    frame_paths: dict[float, Path],
    candidate_specs: tuple[dict[str, Any], ...],
    stage: Path,
    output: Path,
    root: Path,
) -> list[dict[str, Any]]:
    from PIL import Image

    selected_seconds = {
        round(float(value), 3)
        for spec in candidate_specs
        for value in spec["source_frame_timestamps"]
    }
    frames = {
        seconds: Image.open(path).convert("RGB")
        for seconds, path in frame_paths.items()
        if seconds in selected_seconds
    }
    records: list[dict[str, Any]] = []
    opened_cutouts: list[Any] = []
    try:
        for spec in candidate_specs:
            candidate_id = spec["candidate_id"]
            subject_assets: list[dict[str, Any]] = []
            if candidate_id == "A":
                hajime, mask, info = _manual_subject_cutout(
                    frames[22.806], subject="hajime_macro"
                )
                opened_cutouts.extend([hajime, mask])
                subject_assets.append(
                    _write_subject_asset(
                        candidate_id="A",
                        role="hajime",
                        cutout=hajime,
                        mask=mask,
                        info=info,
                        source_timestamp=22.806,
                        stage=stage,
                        output=output,
                        root=root,
                    )
                )
                image = _poster_a(hajime)
            elif candidate_id == "B":
                hajime, hajime_mask, hajime_info = _manual_subject_cutout(
                    frames[22.656], subject="hajime_macro"
                )
                noel, noel_mask, noel_info = _manual_subject_cutout(
                    frames[25.159], subject="noel_three_quarter"
                )
                opened_cutouts.extend([hajime, hajime_mask, noel, noel_mask])
                subject_assets.extend(
                    [
                        _write_subject_asset(
                            candidate_id="B",
                            role="hajime",
                            cutout=hajime,
                            mask=hajime_mask,
                            info=hajime_info,
                            source_timestamp=22.656,
                            stage=stage,
                            output=output,
                            root=root,
                        ),
                        _write_subject_asset(
                            candidate_id="B",
                            role="noel_secondary",
                            cutout=noel,
                            mask=noel_mask,
                            info=noel_info,
                            source_timestamp=25.159,
                            stage=stage,
                            output=output,
                            root=root,
                        ),
                    ]
                )
                image = _poster_b(noel, hajime)
            else:
                hajime, mask, info = _manual_subject_cutout(
                    frames[23.556], subject="hajime_macro"
                )
                opened_cutouts.extend([hajime, mask])
                subject_assets.append(
                    _write_subject_asset(
                        candidate_id="C",
                        role="hajime",
                        cutout=hajime,
                        mask=mask,
                        info=info,
                        source_timestamp=23.556,
                        stage=stage,
                        output=output,
                        root=root,
                    )
                )
                image = _poster_c(hajime)
            if image.size != CANVAS or image.mode != "RGB":
                raise ShortsPosterFrameProofError(
                    "poster dimensions or color mode invalid"
                )
            out = stage / f"poster_{candidate_id}_1080x1920.jpg"
            image.save(
                out,
                format="JPEG",
                quality=94,
                subsampling=0,
                optimize=False,
                progressive=False,
            )
            platform_previews = _write_platform_previews(
                image=image,
                candidate_id=candidate_id,
                stage=stage,
                output=output,
                root=root,
            )
            records.append(
                {
                    **spec,
                    "path": _relative(output / out.name, root),
                    "sha256": _sha256(out),
                    "width": CANVAS[0],
                    "height": CANVAS[1],
                    "mode": "RGB",
                    "format": "JPEG",
                    "dominant_subject": spec["speaker"],
                    "speaker_alignment": "speaker_is_dominant_subject",
                    "subject_assets": subject_assets,
                    "subject_isolation_method": "Pillow manual polygon alpha matte",
                    "temporary_segmentation_tool_used": False,
                    "platform_previews": platform_previews,
                    "full_9_16_preview": [405, 720],
                    "center_4_5_preview": [320, 400],
                    "center_4_5_crop_survives": True,
                    "youtube_verified": False,
                    "third_party_pixels_used": False,
                    "ai_face_or_expression_change": False,
                    "raw_scene_screenshot_as_finished_background": False,
                    "rectangular_scene_screenshot_panel_used": False,
                    "circular_scene_screenshot_inset_used": False,
                    "human_acceptance": "pending",
                }
            )
            image.close()
        _write_mask_inspection(stage=stage)
    finally:
        for image in frames.values():
            image.close()
        for image in opened_cutouts:
            image.close()
    return records


def _manual_subject_cutout(
    source: Any, *, subject: str
) -> tuple[Any, Any, dict[str, Any]]:
    from PIL import Image, ImageDraw, ImageFilter

    if source.size != (1920, 1080):
        raise ShortsPosterFrameProofError("subject source frame dimensions changed")
    if subject == "hajime_macro":
        points = [
            (455, 0),
            (1465, 0),
            (1635, 115),
            (1775, 285),
            (1885, 535),
            (1760, 815),
            (1435, 1080),
            (485, 1080),
            (165, 815),
            (35, 535),
            (175, 285),
            (320, 115),
        ]
        feather_radius = 5
    elif subject == "noel_three_quarter":
        points = [
            (300, 0),
            (535, 0),
            (615, 85),
            (625, 255),
            (690, 345),
            (765, 410),
            (805, 535),
            (815, 655),
            (770, 790),
            (850, 1080),
            (125, 1080),
            (185, 930),
            (235, 835),
            (225, 680),
            (245, 520),
            (265, 405),
            (300, 335),
            (260, 230),
        ]
        feather_radius = 3
    else:
        raise ShortsPosterFrameProofError(f"unsupported manual mask subject: {subject}")
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather_radius))
    bbox = mask.getbbox()
    if bbox is None:
        raise ShortsPosterFrameProofError("manual subject mask is empty")
    cutout_mask = mask.crop(bbox)
    cutout = source.crop(bbox).convert("RGBA")
    cutout.putalpha(cutout_mask)
    histogram = cutout_mask.histogram()
    pixel_count = cutout_mask.width * cutout_mask.height
    return cutout, cutout_mask, {
        "subject": subject,
        "source_dimensions": list(source.size),
        "crop_box": list(bbox),
        "mask_dimensions": list(cutout_mask.size),
        "alpha_opaque_ratio": round(histogram[255] / pixel_count, 6),
        "alpha_feather_ratio": round(sum(histogram[1:255]) / pixel_count, 6),
        "alpha_transparent_ratio": round(histogram[0] / pixel_count, 6),
        "edge_feather_radius_pixels": feather_radius,
        "person_pixels_generated_or_modified": False,
    }


def _write_subject_asset(
    *,
    candidate_id: str,
    role: str,
    cutout: Any,
    mask: Any,
    info: dict[str, Any],
    source_timestamp: float,
    stage: Path,
    output: Path,
    root: Path,
) -> dict[str, Any]:
    cutout_name = f"subject_{candidate_id}_{role}_rgba.png"
    mask_name = f"subject_{candidate_id}_{role}_mask.png"
    cutout_path = stage / cutout_name
    mask_path = stage / mask_name
    cutout.save(cutout_path, format="PNG", optimize=False)
    mask.save(mask_path, format="PNG", optimize=False)
    return {
        "role": role,
        "source_timestamp_seconds": source_timestamp,
        "cutout_path": _relative(output / cutout_name, root),
        "cutout_sha256": _sha256(cutout_path),
        "mask_path": _relative(output / mask_name, root),
        "mask_sha256": _sha256(mask_path),
        "method": "Pillow manual polygon alpha matte",
        "tool": "Pillow",
        "license": "HPND",
        "purpose": "alpha mask generation only",
        **info,
    }


def _place_cutout(
    canvas: Any,
    cutout: Any,
    *,
    xy: tuple[int, int],
    width: int | None = None,
    height: int | None = None,
    outline: tuple[int, int, int, int] = (255, 255, 255, 220),
) -> None:
    from PIL import Image, ImageFilter

    if (width is None) == (height is None):
        raise ShortsPosterFrameProofError("cutout placement requires width or height")
    scale = (width / cutout.width) if width is not None else (height / cutout.height)
    size = (round(cutout.width * scale), round(cutout.height * scale))
    resized = cutout.resize(size, Image.Resampling.LANCZOS)
    alpha = resized.getchannel("A")
    expanded = alpha.filter(ImageFilter.MaxFilter(31))
    outline_layer = Image.new("RGBA", size, outline)
    outline_layer.putalpha(expanded)
    canvas.paste(outline_layer, (xy[0] + 5, xy[1] + 8), outline_layer)
    canvas.paste(resized, xy, resized)
    resized.close()
    outline_layer.close()


def _write_mask_inspection(*, stage: Path) -> None:
    from PIL import Image, ImageDraw

    paths = sorted(stage.glob("subject_*_rgba.png"))
    cell_w, cell_h = 270, 520
    canvas = Image.new("RGB", (cell_w * len(paths), cell_h), (18, 20, 24))
    draw = ImageDraw.Draw(canvas)
    font = _project_font(19)
    for index, path in enumerate(paths):
        x0 = index * cell_w
        checker = Image.new("RGB", (cell_w, 430), (225, 225, 225))
        checker_draw = ImageDraw.Draw(checker)
        for y in range(0, 430, 24):
            for x in range(0, cell_w, 24):
                if (x // 24 + y // 24) % 2:
                    checker_draw.rectangle((x, y, x + 23, y + 23), fill=(180, 180, 180))
        with Image.open(path) as source:
            rgba = source.convert("RGBA")
            scale = min(240 / rgba.width, 360 / rgba.height)
            size = (round(rgba.width * scale), round(rgba.height * scale))
            large = rgba.resize(size, Image.Resampling.LANCZOS)
            checker.paste(large, ((cell_w - size[0]) // 2, 28), large)
            tiny_scale = min(80 / rgba.width, 120 / rgba.height)
            tiny_size = (round(rgba.width * tiny_scale), round(rgba.height * tiny_scale))
            tiny = rgba.resize(tiny_size, Image.Resampling.LANCZOS)
            checker.paste(tiny, (cell_w - tiny_size[0] - 12, 430 - tiny_size[1] - 12), tiny)
            large.close()
            tiny.close()
            rgba.close()
        canvas.paste(checker, (x0, 0))
        draw.text((x0 + 8, 448), path.stem, font=font, fill=(245, 245, 245))
        draw.text((x0 + 8, 480), "large edge + reduced edge", font=font, fill=(185, 195, 210))
        checker.close()
    canvas.save(
        stage / "subject_mask_inspection.jpg",
        format="JPEG",
        quality=94,
        subsampling=0,
        optimize=False,
    )


def _poster_a(hajime_cutout: Any) -> Any:
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", CANVAS, (10, 91, 116, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((120, 245, 960, 1085), fill=(255, 219, 72, 235))
    draw.polygon(
        [(0, 1180), (270, 1040), (1080, 1300), (1080, 1920), (0, 1920)],
        fill=(5, 45, 72, 255),
    )
    for x in (95, 250, 820, 965):
        draw.ellipse((x - 28, 590, x + 28, 646), fill=(255, 255, 255, 90))
    _place_cutout(
        image,
        hajime_cutout,
        xy=(-150, 720),
        width=1380,
        outline=(255, 255, 255, 225),
    )
    font = _project_font(184, weight="Black")
    _draw_centered_text(
        draw,
        ["来ねぇ!!"],
        center=(540, 445),
        font=font,
        fill=(255, 255, 255),
        stroke_fill=(4, 38, 58),
        stroke_width=19,
        spacing=0,
    )
    return image.convert("RGB")


def _poster_b(noel_cutout: Any, hajime_cutout: Any) -> Any:
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", CANVAS, (242, 87, 111, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.polygon([(0, 0), (1080, 0), (1080, 720), (0, 900)], fill=(255, 239, 196, 255))
    draw.polygon(
        [(0, 1060), (1080, 810), (1080, 1920), (0, 1920)],
        fill=(35, 45, 83, 255),
    )
    draw.ellipse((650, 875, 1240, 1465), fill=(255, 205, 73, 210))
    _place_cutout(
        image,
        noel_cutout,
        xy=(-100, 680),
        height=990,
        outline=(255, 255, 255, 210),
    )
    _place_cutout(
        image,
        hajime_cutout,
        xy=(175, 900),
        width=1040,
        outline=(255, 235, 95, 235),
    )
    font = _project_font(142, weight="Black")
    _draw_centered_text(
        draw,
        ["なんで", "来なかった!?"],
        center=(540, 460),
        font=font,
        fill=(43, 49, 77),
        stroke_fill=(255, 255, 255),
        stroke_width=17,
        spacing=-8,
    )
    return image.convert("RGB")


def _poster_c(hajime_cutout: Any) -> Any:
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", CANVAS, (24, 24, 57, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.polygon(
        [(545, 0), (1080, 0), (1080, 1180), (725, 1050), (410, 260)],
        fill=(255, 207, 67, 255),
    )
    draw.polygon(
        [(0, 1340), (550, 1090), (1080, 1390), (1080, 1920), (0, 1920)],
        fill=(11, 103, 116, 255),
    )
    draw.ellipse((670, 220, 1020, 570), fill=(255, 255, 255, 55))
    _place_cutout(
        image,
        hajime_cutout,
        xy=(-285, 760),
        width=1260,
        outline=(255, 255, 255, 225),
    )
    first_font = _project_font(148, weight="Black")
    _draw_centered_text(
        draw,
        ["ずっと"],
        center=(735, 380),
        font=first_font,
        fill=(29, 31, 64),
        stroke_fill=(255, 255, 255),
        stroke_width=16,
        spacing=0,
    )
    second_font = _project_font(105, weight="Black")
    _draw_centered_text(
        draw,
        ["待ってたんすよ!!"],
        center=(535, 595),
        font=second_font,
        fill=(255, 255, 255),
        stroke_fill=(24, 24, 57),
        stroke_width=15,
        spacing=0,
    )
    return image.convert("RGB")


def _project_font(size: int, *, weight: str = "Bold") -> Any:
    from PIL import ImageFont

    font = ImageFont.truetype(str(_font_path()), size)
    if hasattr(font, "set_variation_by_name"):
        try:
            font.set_variation_by_name(weight)
        except OSError:
            pass
    return font


def _cover_crop(
    source: Any, size: tuple[int, int], *, focus: tuple[float, float]
) -> Any:
    from PIL import Image

    width, height = size
    scale = max(width / source.width, height / source.height)
    resized = source.resize(
        (round(source.width * scale), round(source.height * scale)),
        Image.Resampling.LANCZOS,
    )
    focus_x = round(focus[0] * resized.width)
    focus_y = round(focus[1] * resized.height)
    left = min(max(0, focus_x - width // 2), resized.width - width)
    top = min(max(0, focus_y - height // 2), resized.height - height)
    return resized.crop((left, top, left + width, top + height))


def _draw_centered_text(
    draw: Any,
    lines: list[str],
    *,
    center: tuple[int, int],
    font: Any,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int],
    stroke_width: int,
    spacing: int,
) -> None:
    text = "\n".join(lines)
    box = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
        align="center",
    )
    width = box[2] - box[0]
    height = box[3] - box[1]
    xy = (center[0] - width / 2 - box[0], center[1] - height / 2 - box[1])
    draw.multiline_text(
        xy,
        text,
        font=font,
        fill=fill,
        spacing=spacing,
        align="center",
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def _write_poster_contact_sheet(*, stage: Path, out: Path) -> None:
    from PIL import Image, ImageDraw

    canvas = Image.new("RGB", (1080, 720), (12, 14, 20))
    draw = ImageDraw.Draw(canvas)
    font = _project_font(44)
    for index, candidate_id in enumerate(("A", "B", "C")):
        with Image.open(stage / f"poster_{candidate_id}_1080x1920.jpg") as source:
            small = source.convert("RGB").resize((360, 640), Image.Resampling.LANCZOS)
        x = index * 360
        canvas.paste(small, (x, 0))
        draw.text((x + 18, 657), candidate_id, font=font, fill=(255, 255, 255))
    canvas.save(out, format="JPEG", quality=94, subsampling=0, optimize=False)


def _write_platform_previews(
    *, image: Any, candidate_id: str, stage: Path, output: Path, root: Path
) -> dict[str, Any]:
    from PIL import Image, ImageDraw

    tile_name = f"preview_{candidate_id}_channel_search_tile.jpg"
    center_name = f"preview_{candidate_id}_center_4_5.jpg"
    ui_name = f"preview_{candidate_id}_shorts_ui_overlay.jpg"
    tile_path = stage / tile_name
    center_path = stage / center_name
    ui_path = stage / ui_name

    tile = image.resize((405, 720), Image.Resampling.LANCZOS)
    tile.save(tile_path, format="JPEG", quality=94, subsampling=0, optimize=False)
    center = image.crop(CENTER_4_5_SAFE_RECT).resize(
        (320, 400), Image.Resampling.LANCZOS
    )
    center.save(center_path, format="JPEG", quality=94, subsampling=0, optimize=False)
    ui = tile.convert("RGBA")
    draw = ImageDraw.Draw(ui, "RGBA")
    draw.rounded_rectangle((16, 14, 150, 54), radius=18, fill=(0, 0, 0, 130))
    draw.ellipse((22, 22, 40, 40), fill=(255, 255, 255, 220))
    draw.rounded_rectangle((322, 12, 389, 52), radius=18, fill=(0, 0, 0, 130))
    for y in (255, 340, 425, 510):
        draw.ellipse((349, y, 389, y + 40), fill=(0, 0, 0, 145))
        draw.ellipse((359, y + 10, 379, y + 30), outline=(255, 255, 255, 230), width=3)
    draw.rounded_rectangle((14, 615, 335, 704), radius=14, fill=(0, 0, 0, 155))
    draw.rounded_rectangle((28, 639, 245, 652), radius=6, fill=(255, 255, 255, 215))
    draw.rounded_rectangle((28, 666, 292, 678), radius=6, fill=(255, 255, 255, 145))
    ui.convert("RGB").save(
        ui_path, format="JPEG", quality=94, subsampling=0, optimize=False
    )
    tile.close()
    center.close()
    ui.close()
    return {
        "channel_search_tile": {
            "path": _relative(output / tile_name, root),
            "sha256": _sha256(tile_path),
            "dimensions": [405, 720],
            "basis": "observed public YouTube search Shorts card surface",
        },
        "center_4_5_heuristic": {
            "path": _relative(output / center_name, root),
            "sha256": _sha256(center_path),
            "dimensions": [320, 400],
            "official_guarantee": False,
        },
        "shorts_playback_ui_overlay": {
            "path": _relative(output / ui_name, root),
            "sha256": _sha256(ui_path),
            "dimensions": [405, 720],
            "approximation": True,
        },
    }


def _write_platform_preview_contact_sheet(*, stage: Path, out: Path) -> None:
    from PIL import Image, ImageDraw

    canvas = Image.new("RGB", (1080, 1620), (13, 16, 22))
    draw = ImageDraw.Draw(canvas)
    heading = _project_font(30)
    label = _project_font(21)
    for row, candidate_id in enumerate(("A", "B", "C")):
        y0 = row * 540
        draw.text((18, y0 + 12), f"{candidate_id} platform previews", font=heading, fill=(255, 255, 255))
        with Image.open(stage / f"preview_{candidate_id}_channel_search_tile.jpg") as source:
            tile = source.convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
        with Image.open(stage / f"preview_{candidate_id}_center_4_5.jpg") as source:
            center = source.convert("RGB").resize((320, 400), Image.Resampling.LANCZOS)
        with Image.open(stage / f"preview_{candidate_id}_shorts_ui_overlay.jpg") as source:
            ui = source.convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
        canvas.paste(tile, (20, y0 + 56))
        canvas.paste(center, (380, y0 + 96))
        canvas.paste(ui, (790, y0 + 56))
        draw.text((54, y0 + 506), "channel / search", font=label, fill=(205, 214, 228))
        draw.text((405, y0 + 506), "center 4:5 heuristic", font=label, fill=(205, 214, 228))
        draw.text((820, y0 + 506), "Shorts UI overlay", font=label, fill=(205, 214, 228))
        tile.close()
        center.close()
        ui.close()
    canvas.save(out, format="JPEG", quality=94, subsampling=0, optimize=False)


def _write_expression_contact_sheets(
    *,
    frames: dict[float, Path],
    stage: Path,
    candidate_specs: tuple[dict[str, Any], ...],
) -> None:
    from PIL import Image, ImageDraw

    tile_w, image_h, label_h = 384, 216, 44
    font = _project_font(25)
    for spec in candidate_specs:
        candidate_id = str(spec["candidate_id"])
        window = SURVEY_WINDOWS[candidate_id]
        selected_seconds = {
            round(float(value), 3) for value in spec["source_frame_timestamps"]
        }
        window_seconds = [
            seconds
            for seconds in frames
            if window["start"] - 0.001 <= seconds <= window["end"] + 0.001
        ]
        fallback_seconds = sorted(selected_seconds - set(window_seconds))
        ordered_seconds = [*fallback_seconds, *window_seconds]
        rows = math.ceil(len(ordered_seconds) / 5)
        canvas = Image.new(
            "RGB", (tile_w * 5, (image_h + label_h) * rows), (14, 17, 23)
        )
        draw = ImageDraw.Draw(canvas)
        for index, seconds in enumerate(ordered_seconds):
            with Image.open(frames[seconds]) as source:
                small = source.convert("RGB").resize((tile_w, image_h))
            col, row = index % 5, index // 5
            x, y = col * tile_w, row * (image_h + label_h)
            canvas.paste(small, (x, y))
            selected = seconds in selected_seconds
            fallback = seconds in fallback_seconds
            color = (255, 224, 77) if selected else (213, 220, 232)
            label = f"{candidate_id} {seconds:.3f}s"
            if selected:
                label += "  selected"
            if fallback:
                label += "  nearest frontal fallback"
            draw.rectangle(
                (x, y, x + tile_w - 1, y + image_h + label_h - 1),
                outline=color,
                width=5 if selected else 2,
            )
            draw.text((x + 10, y + image_h + 6), label, font=font, fill=color)
        canvas.save(
            stage / f"expression_contact_sheet_{candidate_id}.jpg",
            format="JPEG",
            quality=92,
            subsampling=0,
            optimize=False,
        )


def _write_reference_board(
    *, references: list[dict[str, Any]], reference_inputs: list[Path], out: Path
) -> None:
    from PIL import Image, ImageDraw

    cols = 6
    tile_w, image_h, label_h = 180, 320, 66
    rows = math.ceil(len(references) / cols)
    canvas = Image.new(
        "RGB", (tile_w * cols, (image_h + label_h) * rows), (17, 20, 24)
    )
    draw = ImageDraw.Draw(canvas)
    font = _project_font(14)
    for index, (entry, path) in enumerate(zip(references, reference_inputs)):
        with Image.open(path) as source:
            small = _cover_crop(
                source.convert("RGB"), (tile_w, image_h), focus=(0.5, 0.5)
            )
        col, row = index % cols, index // cols
        x, y = col * tile_w, row * (image_h + label_h)
        canvas.paste(small, (x, y))
        draw.rectangle(
            (x, y, x + tile_w - 1, y + image_h + label_h - 1),
            outline=(56, 65, 77),
            width=2,
        )
        target = (
            "exact search 9:16"
            if entry["target_surface"]
            == "native_vertical_exact_youtube_search_shorts_card"
            else (
                "older native 9:16"
                if "native_vertical" in entry["target_surface"]
                else "16:9 secondary"
            )
        )
        draw.text(
            (x + 8, y + image_h + 4),
            f"{entry['reference_id']}  {entry['layout_family'][:20]}",
            font=font,
            fill=(255, 255, 255),
        )
        draw.text((x + 8, y + image_h + 27), target, font=font, fill=(178, 190, 205))
    canvas.save(out, format="JPEG", quality=92, subsampling=0, optimize=False)


def _render_transitions(
    *,
    accepted_video: Path,
    accepted_duration: float,
    stage: Path,
    output: Path,
    root: Path,
    ffmpeg_path: str,
    ffprobe_path: str,
) -> list[dict[str, Any]]:
    start = max(0.0, accepted_duration - TAIL_DURATION_SECONDS)
    transition_offset = TAIL_DURATION_SECONDS - TRANSITION_DISSOLVE_SECONDS
    proof_duration = TAIL_DURATION_SECONDS + END_CAP_DURATION_SECONDS - TRANSITION_DISSOLVE_SECONDS
    audio_fade_start = TAIL_DURATION_SECONDS - AUDIO_FADE_SECONDS
    audio_pad_seconds = proof_duration - TAIL_DURATION_SECONDS
    records: list[dict[str, Any]] = []
    for candidate_id in ("A", "B", "C"):
        poster = stage / f"poster_{candidate_id}_1080x1920.jpg"
        out = stage / f"transition_{candidate_id}.mp4"
        filter_complex = (
            f"[0:v]trim=duration={TAIL_DURATION_SECONDS:.2f},setpts=PTS-STARTPTS,"
            "scale=1080:1920,setsar=1,fps=30,format=yuv420p[v0];"
            f"[1:v]trim=duration={END_CAP_DURATION_SECONDS:.2f},setpts=PTS-STARTPTS,"
            "scale=1080:1920,setsar=1,fps=30,format=yuv420p[v1];"
            f"[v0][v1]xfade=transition=fade:duration={TRANSITION_DISSOLVE_SECONDS:.2f}:"
            f"offset={transition_offset:.2f}[v];"
            f"[0:a]atrim=duration={TAIL_DURATION_SECONDS:.2f},asetpts=PTS-STARTPTS,"
            "aformat=sample_rates=48000:channel_layouts=stereo,"
            f"afade=t=out:st={audio_fade_start:.2f}:d={AUDIO_FADE_SECONDS:.2f},"
            f"apad=pad_dur={audio_pad_seconds:.2f},atrim=duration={proof_duration:.2f}[a]"
        )
        command = [
            ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.6f}",
            "-i",
            str(accepted_video),
            "-loop",
            "1",
            "-i",
            str(poster),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            "-map_metadata",
            "-1",
            "-threads",
            "1",
            "-t",
            f"{proof_duration:.2f}",
            str(out),
        ]
        _run(command, label=f"transition {candidate_id}")
        probe = _probe_media(out, ffprobe_path=ffprobe_path)
        if probe["width"] != 1080 or probe["height"] != 1920:
            raise ShortsPosterFrameProofError("transition aspect or dimensions invalid")
        if abs(float(probe["duration_seconds"]) - proof_duration) > 0.12:
            raise ShortsPosterFrameProofError("transition duration outside tolerance")
        decode = [
            ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(out),
            "-f",
            "null",
            "-",
        ]
        _run(decode, label=f"transition {candidate_id} full decode")
        records.append(
            {
                "candidate_id": candidate_id,
                "path": _relative(output / out.name, root),
                "sha256": _sha256(out),
                "duration_seconds": probe["duration_seconds"],
                "width": probe["width"],
                "height": probe["height"],
                "narrative_tail_seconds": TAIL_DURATION_SECONDS,
                "poster_end_cap_seconds": END_CAP_DURATION_SECONDS,
                "dissolve_seconds": TRANSITION_DISSOLVE_SECONDS,
                "fully_static_hold_seconds": round(
                    END_CAP_DURATION_SECONDS - TRANSITION_DISSOLVE_SECONDS, 2
                ),
                "video_treatment": "shared_short_dissolve_to_static_poster_end_cap",
                "audio_treatment": "accepted narrative tail with 0.16s fade; only the final hold remains silent",
                "shared_treatment_id": "dissolve_0_12_poster_0_50_audio_fade_0_16",
                "full_decode": "passed",
                "review_only": True,
                "replaces_accepted_video": False,
            }
        )
    return records


def _render_loop_probe(
    *,
    accepted_video: Path,
    transition_path: Path,
    stage: Path,
    output: Path,
    root: Path,
    ffmpeg_path: str,
    ffprobe_path: str,
) -> dict[str, Any]:
    out = stage / "loop_probe_A_tail_poster_start.mp4"
    first_loop_seconds = 0.80
    filter_complex = (
        "[0:v]setpts=PTS-STARTPTS,scale=1080:1920,setsar=1,fps=30,format=yuv420p[v0];"
        f"[1:v]trim=duration={first_loop_seconds:.2f},setpts=PTS-STARTPTS,"
        "scale=1080:1920,setsar=1,fps=30,format=yuv420p[v1];"
        "[v0][v1]concat=n=2:v=1:a=0[v];"
        "[0:a]asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[a0];"
        f"[1:a]atrim=duration={first_loop_seconds:.2f},asetpts=PTS-STARTPTS,"
        "aformat=sample_rates=48000:channel_layouts=stereo[a1];"
        "[a0][a1]concat=n=2:v=0:a=1[a]"
    )
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(transition_path),
        "-i",
        str(accepted_video),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        "-map_metadata",
        "-1",
        "-threads",
        "1",
        str(out),
    ]
    _run(command, label="tail-poster-loop-start probe")
    probe = _probe_media(out, ffprobe_path=ffprobe_path)
    _run(
        [ffmpeg_path, "-hide_banner", "-loglevel", "error", "-i", str(out), "-f", "null", "-"],
        label="tail-poster-loop-start full decode",
    )
    return {
        "candidate_id": "A",
        "path": _relative(output / out.name, root),
        "sha256": _sha256(out),
        "duration_seconds": probe["duration_seconds"],
        "width": probe["width"],
        "height": probe["height"],
        "first_loop_seconds": first_loop_seconds,
        "shared_transition_treatment": "dissolve_0_12_poster_0_50_audio_fade_0_16",
        "full_decode": "passed",
        "browser_observation": "pending",
        "human_naturalness_acceptance": "pending",
    }


def _probe_media(path: Path, *, ffprobe_path: str) -> dict[str, Any]:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height:format=duration",
        "-of",
        "json",
        str(path),
    ]
    result = _run(command, label=f"probe {path.name}")
    payload = json.loads(result.stdout)
    stream = payload["streams"][0]
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "duration_seconds": round(float(payload["format"]["duration"]), 3),
    }


def _reference_manifest(
    *,
    corpus: dict[str, Any],
    corpus_summary: dict[str, Any],
    references: list[dict[str, Any]],
    candidate_specs: tuple[dict[str, Any], ...],
    reference_inputs: list[Path],
    root: Path,
    reference_board: Path,
) -> dict[str, Any]:
    entries = []
    for entry, path in zip(references, reference_inputs):
        entries.append(
            {
                **entry,
                "thumbnail_image_sha256": _sha256(path),
                "thumbnail_image_storage": "ignored_local_frozen_cache_not_packaged_individually",
                "tracked_pixel_reuse_allowed": False,
            }
        )
    families = []
    entry_by_id = {entry["reference_id"]: entry for entry in entries}
    for spec in candidate_specs:
        family_entries = [entry_by_id[value] for value in spec["reference_ids"]]
        families.append(
            {
                "family_id": spec["family_id"],
                "family_name_ja": spec["family_name_ja"],
                "reference_ids": [entry["reference_id"] for entry in family_entries],
                "primary_exemplar_id": spec["primary_exemplar_id"],
                "primary_exemplar_proportions": spec[
                    "primary_exemplar_proportions"
                ],
                "channels": sorted({entry["channel"] for entry in family_entries}),
                "recurring_relationships": spec["adopted_relationships"],
                "derived_after_surface_research": True,
            }
        )
    return {
        "schema_version": "clippipegen.out07.reference_manifest.v0",
        "artifact_id": ARTIFACT_ID,
        "source_priority": corpus["reference_priority"],
        "query_strategies": corpus["query_strategies"],
        "collection_stop_reason": corpus["collection_stop_reason"],
        "surface_observation": corpus["surface_observation"],
        "success_proxy_policy": corpus["success_proxy_policy"],
        "summary": corpus_summary,
        "families": families,
        "references": entries,
        "reference_board": {
            "package_relative_path": reference_board.name,
            "sha256": _sha256(reference_board),
            "third_party_pixels": True,
            "storage": "ignored_local_proof_only_not_committed",
        },
        "candidate_pixel_policy": {
            "third_party_reference_pixels": False,
            "external_character_art": False,
            "logos": False,
            "ai_face_or_expression_changes": False,
            "retained_source_pixels_only": True,
        },
        "tracked_reference_corpus": "docs/output_layer/OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json",
        "official_platform_reference": "https://support.google.com/youtube/answer/10343433?co=GENIE.Platform%3DAndroid&hl=ja",
        "youtube_verified": False,
    }


def _build_readback(
    *,
    root: Path,
    episode: Path,
    output: Path,
    source_video: Path,
    accepted_video: Path,
    publish: dict[str, Any],
    metadata_copy_hash: str,
    corpus_summary: dict[str, Any],
    candidate_records: list[dict[str, Any]],
    transition_records: list[dict[str, Any]],
    loop_probe: dict[str, Any],
    reference_manifest: dict[str, Any],
    protected_before: dict[str, Any],
    input_hashes: dict[str, str],
    final_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "parent_artifact_id": publish["artifact_id"],
        "state": STATE,
        "episode_id": episode.name,
        "target_surface": "youtube_shorts_in_video_selectable_poster_frame",
        "review_entrypoint": _relative(final_paths["index"], root),
        "open_command": _powershell_command(final_paths["open"], root),
        "serve_command": _powershell_command(final_paths["serve"], root),
        "preview_url": f"http://127.0.0.1:{DEFAULT_PORT}/index.html",
        "default_port": DEFAULT_PORT,
        "review_question": REVIEW_QUESTION,
        "poster_decision_status": "human_selection_required",
        "selected_thumbnail": None,
        "current_recommendation": None,
        "candidate_count": 3,
        "canvas": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
        "center_4_5_safe_rect": {"x0": 0, "y0": 285, "x1": 1080, "y1": 1635},
        "candidates": candidate_records,
        "transitions": transition_records,
        "transition_treatment": {
            "selected_shared_treatment_id": "dissolve_0_12_poster_0_50_audio_fade_0_16",
            "comparison_options": [
                {
                    "id": "hard_cut_poster_0_45",
                    "disposition": "not_selected",
                    "reason": "preserved the abrupt stop signal from the superseded proof",
                },
                {
                    "id": "dissolve_0_12_poster_0_50_audio_fade_0_16",
                    "disposition": "selected_for_shared_review_proof",
                    "reason": "keeps a readable poster hold while shortening and softening the stop before loop restart",
                },
                {
                    "id": "dissolve_0_12_poster_0_65_audio_fade_0_16",
                    "disposition": "not_selected",
                    "reason": "longer static hold increased the perceived loop pause",
                },
            ],
            "loop_probe": loop_probe,
            "human_naturalness_acceptance": "pending",
        },
        "reference_corpus": {
            **corpus_summary,
            "manifest_path": _relative(final_paths["reference_manifest"], root),
            "manifest_sha256": _sha256(final_paths["stage_reference_manifest"]),
            "third_party_board_path": _relative(final_paths["reference_board"], root),
            "third_party_board_storage": "ignored_local_proof_only",
        },
        "composition_families": reference_manifest["families"],
        "source_frame_survey": {
            "retained_source_path": _relative(source_video, root),
            "retained_source_sha256": _sha256(source_video),
            "interval_seconds": SURVEY_INTERVAL_SECONDS,
            "windows": SURVEY_WINDOWS,
            "survey_timestamps_seconds": list(
                _dense_survey_timestamps(tuple(candidate_records))
            ),
            "selected_timestamps_seconds": {
                record["candidate_id"]: record["source_frame_timestamps"]
                for record in candidate_records
            },
            "dominant_back_facing_frames_rejected": True,
            "fallback_policy": "nearest truthful frontal complaint frame from the same accepted cut when the exact spoken interval is back-facing",
            "visual_inspection_required_and_performed": True,
            "expression_contact_sheets": {
                candidate_id: _relative(
                    output / f"expression_contact_sheet_{candidate_id}.jpg", root
                )
                for candidate_id in ("A", "B", "C")
            },
        },
        "subject_isolation": {
            "method": "Pillow manual polygon alpha matte",
            "tool": "Pillow",
            "license": "HPND",
            "temporary_segmentation_tool_used": False,
            "person_pixels_generated_or_modified": False,
            "inspection_contact_sheet": _relative(
                output / "subject_mask_inspection.jpg", root
            ),
            "full_resolution_masks_and_reduced_edge_previews_available": True,
        },
        "platform_preview_contract": {
            "channel_search_tile_observed_surface": True,
            "center_4_5_is_project_heuristic_not_official_guarantee": True,
            "shorts_playback_ui_overlay_is_approximation": True,
            "youtube_verified": False,
            "official_reference": "https://support.google.com/youtube/answer/10343433?co=GENIE.Platform%3DAndroid&hl=ja",
            "contact_sheet": _relative(output / "platform_preview_contact_sheet.jpg", root),
        },
        "accepted_video": {
            "path": _relative(accepted_video, root),
            "sha256": _sha256(accepted_video),
            "changed": False,
            "poster_integrated_into_full_video": False,
        },
        "rejected_legacy_thumbnails": {
            "status": "user_rejected",
            "direction_ids": publish["rejected_thumbnail_ids"],
            "selected_thumbnail": publish["selected_thumbnail"],
            "recommended_direction_id": None,
            "returned_as_candidates": False,
        },
        "superseded_poster_candidates": {
            "status": "supervisor_reframe_required",
            "human_rejection": False,
            "returned_as_candidates": False,
            "candidates": list(SUPERSEDED_CANDIDATES),
        },
        "metadata_copy": {
            "title": publish["title"],
            "description": publish["description"],
            "tags": publish["tags"],
            "semantic_sha256": metadata_copy_hash,
            "modified_in_this_slice": False,
            "accepted_in_this_slice": False,
        },
        "gates": {
            "h0_poster_direction_review_ready": True,
            "h1_full_short_integration": False,
            "human_selection_required": True,
            "publish_ready": False,
            "rights_status": "pending",
            "production_acceptance": False,
            "public_or_publishing_acceptance": False,
            "upload_attempted": False,
            "thumbnail_upload_attempted": False,
            "metadata_update_attempted": False,
        },
        "protected_evidence": protected_before,
        "input_hashes": input_hashes,
        "storage": {
            "class": "ignored_local_retained_same_machine",
            "episodes_tracked": False,
            "reference_pixels_committed": False,
            "portable_across_clones": False,
        },
        "regeneration": {
            "frozen_inputs_required": True,
            "network_fetch_required_after_cache_freeze": False,
            "command": (
                "uvx --with Pillow python -m src.cli.main build-shorts-poster-frame-proof "
                f"--episode-dir {_relative(episode, root)} --output-dir {_relative(output, root)} "
                f"--source-video {_relative(source_video, root)} "
                f"--accepted-video {_relative(accepted_video, root)} "
                f"--out07-publish-draft {_relative(Path(publish['_source_path']), root)} "
                "--reference-corpus docs/output_layer/OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json "
                f"--reference-cache-dir {_relative(Path(publish['_reference_cache']), root)} "
                "--format json"
            ),
        },
        "human_acceptance": "pending",
    }


def _render_html(readback: dict[str, Any]) -> str:
    candidate_sections = []
    transition_sections = []
    for candidate in readback["candidates"]:
        candidate_id = candidate["candidate_id"]
        poster_name = f"poster_{candidate_id}_1080x1920.jpg"
        candidate_sections.append(
            f"""<figure class="candidate" data-candidate="{candidate_id}">
<figcaption><strong>{candidate_id}</strong> — {escape(candidate["family_name_ja"])}</figcaption>
<p class="mapping">話者: {escape(candidate["speaker"])} / primary: {escape(candidate["primary_exemplar_id"])} / {escape(candidate["fit_reason"])}</p>
<img class="poster-main" id="poster-{candidate_id}" src="{poster_name}" alt="候補{candidate_id} {escape(candidate["family_name_ja"])}">
<div class="platform-previews">
<div><span>channel / search 405×720</span><img src="preview_{candidate_id}_channel_search_tile.jpg" alt="候補{candidate_id} channel search tile"></div>
<div><span>center 4:5 heuristic</span><img src="preview_{candidate_id}_center_4_5.jpg" alt="候補{candidate_id} center 4:5 heuristic"></div>
<div><span>Shorts playback UI overlay</span><img src="preview_{candidate_id}_shorts_ui_overlay.jpg" alt="候補{candidate_id} Shorts UI overlay"></div>
</div>
</figure>"""
        )
        transition_sections.append(
            f"""<figure><figcaption><strong>{candidate_id}</strong> — 末尾1.75秒＋0.12秒dissolve＋poster 0.50秒</figcaption>
<video id="transition-{candidate_id}" controls preload="metadata" src="transition_{candidate_id}.mp4"></video></figure>"""
        )
    evidence_rows = "".join(
        f"<tr><td>{candidate['candidate_id']}</td><td>{escape(candidate['family_name_ja'])}</td>"
        f"<td>{escape(candidate['speaker'])}</td>"
        f"<td>{escape(', '.join(f'{value:.1f}s' for value in candidate['source_frame_timestamps']))}</td>"
        f"<td>{escape(candidate['copy_evidence']['accepted_text'])}</td>"
        f"<td>{escape(candidate['primary_exemplar_id'])} + {escape(', '.join(candidate['reference_ids'][1:]))}</td></tr>"
        for candidate in readback["candidates"]
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OUT-07 Shorts poster方向proof</title>
<style>
:root{{--bg:#0c0e13;--panel:#171a22;--line:#333949;--text:#f7f8fb;--muted:#b8c0ce;--accent:#ffe15d}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,'Yu Gothic',sans-serif;overflow-x:hidden}}
main{{max-width:1320px;margin:0 auto;padding:24px}}h1{{margin:.15em 0}}.status{{color:var(--muted)}}.question{{font-size:clamp(18px,2vw,26px);font-weight:800;border-left:6px solid var(--accent);padding:12px 16px;background:#181b23}}
.candidates{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;align-items:start}}figure{{margin:0;min-width:0}}figcaption{{margin:0 0 10px;font-size:18px}}
.poster-main{{display:block;width:100%;height:auto;border-radius:18px;background:#000;border:1px solid var(--line)}}
.mapping{{min-height:5.4em;color:var(--muted);line-height:1.45}}.platform-previews{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:14px;align-items:end}}
.platform-previews>div{{display:grid;gap:6px;justify-items:center;color:var(--muted);font-size:12px;text-align:center}}.platform-previews img{{display:block;width:100%;height:auto;border:1px solid var(--line);background:#000}}
section{{margin-top:34px}}.sheet{{display:block;width:100%;height:auto;border:1px solid var(--line);background:#000}}
.transitions{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}}video{{display:block;width:100%;max-height:72vh;background:#000;border:1px solid var(--line);border-radius:14px}}
details{{margin-top:34px;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}}summary{{cursor:pointer;font-weight:800;font-size:19px}}table{{width:100%;border-collapse:collapse;margin-top:14px;font-size:14px}}th,td{{border-top:1px solid var(--line);padding:9px;text-align:left;vertical-align:top}}code{{overflow-wrap:anywhere}}.secondary{{color:var(--muted)}}
@media(max-width:900px){{.candidates,.transitions{{grid-template-columns:1fr}}.poster-main{{max-width:560px;margin:0 auto}}main{{padding:16px}}table{{display:block;overflow-x:auto}}}}
</style></head><body><main>
<header><p class="status">reference-fidelity 9:16 Shorts poster / human selection pending / youtube_verified=false</p><h1>poster frame 方向比較 A／B／C</h1><p class="question">{escape(REVIEW_QUESTION)}</p></header>
<section class="candidates" id="candidates">{"".join(candidate_sections)}</section>
<section><h2>3案比較</h2><img class="sheet" id="poster-contact-sheet" src="poster_direction_contact_sheet.jpg" alt="poster方向A B C比較シート"></section>
<section><h2>platform preview 一覧</h2><p class="secondary">center 4:5 は project robustness heuristic であり、YouTube の公式 crop 保証ではありません。UI overlay も比較用近似です。</p><img class="sheet" src="platform_preview_contact_sheet.jpg" alt="channel search center 4:5 Shorts UI preview comparison"></section>
<section><h2>末尾transition proof</h2><p class="secondary">受入済み本編の末尾1.75秒から、全案共通の0.12秒dissolveでposterを0.50秒表示し、音声は末尾0.16秒でfade。proofは本編を置換しません。感覚的な自然さはhuman acceptance pendingです。</p><div class="transitions">{"".join(transition_sections)}</div></section>
<details id="evidence"><summary>参照構造・元フレーム・provenance</summary>
<p>{readback["reference_corpus"]["reference_count"]}件／{readback["reference_corpus"]["channel_count"]}チャンネル。native vertical exact-surface {readback["reference_corpus"]["native_vertical_exact_surface_count"]}件、16:9補助 {readback["reference_corpus"]["conventional_16_9_secondary_count"]}件。view count は因果証明ではありません。第三者画像はignored local reference boardだけに保持し、候補A/B/Cには流用していません。</p>
<table><thead><tr><th>候補</th><th>構図文法</th><th>話者</th><th>実素材timestamp</th><th>受入済み内容根拠</th><th>primary + supporting</th></tr></thead><tbody>{evidence_rows}</tbody></table>
<h3>発話区間 dense expression survey（0.15秒）</h3><img class="sheet" src="expression_contact_sheet_A.jpg" alt="候補A dense expression survey"><img class="sheet" src="expression_contact_sheet_B.jpg" alt="候補B dense expression survey"><img class="sheet" src="expression_contact_sheet_C.jpg" alt="候補C dense expression survey">
<h3>人物mask edge inspection</h3><img class="sheet" src="subject_mask_inspection.jpg" alt="人物maskの原寸系と縮小edge inspection">
<h3>公開参照board（構造抽出専用）</h3><img class="sheet" src="reference_board.jpg" alt="公開サムネイル参照board">
<p><code>reference_manifest.json</code> / <code>poster_direction_readback.json</code></p>
</details>
<script>
const media=[...document.images,...document.querySelectorAll('video')];
document.body.dataset.mediaCount=String(media.length);
Promise.all(media.map((node)=>new Promise((resolve)=>{{
  if(node.tagName==='IMG'){{if(node.complete)resolve(!node.naturalWidth);else{{node.addEventListener('load',()=>resolve(false),{{once:true}});node.addEventListener('error',()=>resolve(true),{{once:true}})}}}}
  else{{if(node.readyState>=1)resolve(false);else{{node.addEventListener('loadedmetadata',()=>resolve(false),{{once:true}});node.addEventListener('error',()=>resolve(true),{{once:true}})}}}}
}}))).then(values=>{{document.body.dataset.mediaErrors=String(values.filter(Boolean).length);document.body.dataset.mediaReady='true'}});
</script></main></body></html>"""


def _final_paths(output: Path) -> dict[str, Path]:
    paths = {
        "index": output / "index.html",
        "open": output / "open_preview.ps1",
        "serve": output / "serve_preview.ps1",
        "readback": output / "poster_direction_readback.json",
        "reference_manifest": output / "reference_manifest.json",
        "reference_board": output / "reference_board.jpg",
        "poster_contact_sheet": output / "poster_direction_contact_sheet.jpg",
        "platform_contact_sheet": output / "platform_preview_contact_sheet.jpg",
        "mask_inspection": output / "subject_mask_inspection.jpg",
        "loop_probe": output / "loop_probe_A_tail_poster_start.mp4",
    }
    return paths


def _open_script() -> str:
    return f"""param([switch]$Serve, [int]$Port = {DEFAULT_PORT})
$ErrorActionPreference = 'Stop'
if ($Serve) {{
    & (Join-Path $PSScriptRoot 'serve_preview.ps1') -Port $Port
    exit $LASTEXITCODE
}}
$index = Join-Path $PSScriptRoot 'index.html'
Write-Host "OUT-07 Shorts poster proof: $index"
Start-Process -FilePath $index
Write-Host "If local-file media is blocked, rerun with -Serve."
"""


def _serve_script() -> str:
    return rf"""param([int]$Port = {DEFAULT_PORT})
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')
Write-Host "OUT-07 Shorts poster proof URL: $url"
Write-Host "OUT-07 Shorts poster proof root: $PSScriptRoot"
Start-Process -FilePath $url
Push-Location $repoRoot
try {{
    uvx python -m src.cli.serve_review --root $PSScriptRoot --port $Port
}} finally {{
    Pop-Location
}}
"""


REQUIRED_PACKAGE_FILES = (
    "index.html",
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
    "reference_board.jpg",
    "reference_manifest.json",
    "poster_direction_readback.json",
    "transition_A.mp4",
    "transition_B.mp4",
    "transition_C.mp4",
    "loop_probe_A_tail_poster_start.mp4",
    "open_preview.ps1",
    "serve_preview.ps1",
)


def _validate_package(stage: Path) -> None:
    from PIL import Image

    names = {path.name for path in stage.iterdir() if path.is_file()}
    if names != set(REQUIRED_PACKAGE_FILES):
        raise ShortsPosterFrameProofError("proof package file list mismatch")
    readback = _read_json(stage / "poster_direction_readback.json", "poster readback")
    if (
        readback["selected_thumbnail"] is not None
        or readback["current_recommendation"] is not None
    ):
        raise ShortsPosterFrameProofError("proof must not select or recommend a winner")
    if readback["poster_decision_status"] != "human_selection_required":
        raise ShortsPosterFrameProofError("proof must remain pending human selection")
    if readback["accepted_video"]["sha256"] != ACCEPTED_VIDEO_SHA256:
        raise ShortsPosterFrameProofError("accepted video hash drifted in readback")
    if (
        readback["superseded_poster_candidates"]["status"]
        != "supervisor_reframe_required"
        or readback["superseded_poster_candidates"]["human_rejection"] is not False
    ):
        raise ShortsPosterFrameProofError("superseded candidate status is incorrect")
    for candidate_id in ("A", "B", "C"):
        with Image.open(stage / f"poster_{candidate_id}_1080x1920.jpg") as image:
            if image.size != CANVAS or image.mode != "RGB":
                raise ShortsPosterFrameProofError(
                    "poster file dimensions or mode invalid"
                )
        for preview_name, expected_size in (
            (f"preview_{candidate_id}_channel_search_tile.jpg", (405, 720)),
            (f"preview_{candidate_id}_center_4_5.jpg", (320, 400)),
            (f"preview_{candidate_id}_shorts_ui_overlay.jpg", (405, 720)),
        ):
            with Image.open(stage / preview_name) as preview:
                if preview.size != expected_size:
                    raise ShortsPosterFrameProofError("platform preview dimensions changed")
    for mask_path in stage.glob("subject_*_mask.png"):
        with Image.open(mask_path) as mask:
            if mask.mode != "L" or mask.getextrema() != (0, 255):
                raise ShortsPosterFrameProofError("subject alpha mask is invalid")
    manifest = _read_json(stage / "reference_manifest.json", "reference manifest")
    if len(manifest["references"]) < 18 or len(manifest["families"]) != 3:
        raise ShortsPosterFrameProofError("reference manifest coverage mismatch")
    summary = manifest["summary"]
    if (
        summary["native_vertical_exact_surface_count"] < 12
        or summary["native_vertical_exact_surface_channel_count"] < 6
        or summary["conventional_16_9_ratio"] >= 0.5
    ):
        raise ShortsPosterFrameProofError("reference fidelity coverage mismatch")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count('class="candidate"') != 3 or html.count("<video") != 3:
        raise ShortsPosterFrameProofError(
            "review page candidate or transition count mismatch"
        )
    if html.count(REVIEW_QUESTION) != 1 or "<details open" in html:
        raise ShortsPosterFrameProofError(
            "review page question or folded evidence mismatch"
        )
    if "source_frame_contact_sheet" in html or "hard cut" in html.lower():
        raise ShortsPosterFrameProofError("superseded poster or transition method leaked")


def _validate_rejected_out07_truth(publish: dict[str, Any]) -> None:
    if publish.get("selected_thumbnail") is not None:
        raise ShortsPosterFrameProofError("legacy rejected thumbnail remains selected")
    if publish.get("poster_decision_status") != "human_selection_required":
        raise ShortsPosterFrameProofError("OUT-07 poster decision state is not pending")
    if publish.get("rejected_thumbnail_ids") != ["context", "tension", "payoff"]:
        raise ShortsPosterFrameProofError("OUT-07 rejected thumbnail IDs mismatch")
    expected_copy = {
        "title": "番長、団長を呼び出すも来ない！？",
        "description": (
            "番長のはじめが団長を体育館裏へ呼び出し、「倒してやる！！」と意気込みます。\n"
            "ところが団長は来ず、待ち続けたはじめが「なんで来なかったんすか！！」と問いかけます。\n"
            "最後は“はじめの勝ち”で決着し、次の番長を探し始めます。"
        ),
        "tags": [
            "ホロライブ",
            "はじめ",
            "番長",
            "団長",
            "体育館裏",
            "呼び出し",
            "来なかった理由",
        ],
    }
    if any(publish.get(key) != value for key, value in expected_copy.items()):
        raise ShortsPosterFrameProofError("OUT-07 metadata copy changed")
    if (
        publish.get("publish_ready") is not False
        or publish.get("rights_status") != "pending"
    ):
        raise ShortsPosterFrameProofError("OUT-07 publish/rights gates changed")


def _metadata_copy_hash(publish: dict[str, Any]) -> str:
    payload = {
        "title": publish["title"],
        "description": publish["description"],
        "tags": publish["tags"],
    }
    data = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(data).hexdigest()


def _protected_paths(episode: Path, *, output: Path, cache: Path) -> dict[str, Path]:
    review = episode / "review"
    paths = {
        "out03_real_local_selected_cut_proof": review
        / "out03_real_local_selected_cut_proof",
        "out04_editorial_representative_sequence": review
        / "out04_editorial_representative_sequence",
        "out05_vertical_short_internal_candidate": review
        / "out05_vertical_short_internal_candidate",
        "out06_complete_narrative_short_delivery_candidate": review
        / "out06_complete_narrative_short_delivery_candidate",
        "out07_internal_operator_delivery_pack": review
        / "out07_internal_operator_delivery_pack",
    }
    for label, path in paths.items():
        _require_directory(path, f"protected {label}")
        if path in {output, cache}:
            raise ShortsPosterFrameProofError(
                "proof/cache overlaps protected predecessor"
            )
    return paths


def _run(command: list[str], *, label: str) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=900,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ShortsPosterFrameProofError(f"{label} failed before exit") from exc
    if result.returncode != 0:
        tail = result.stderr[-1200:]
        raise ShortsPosterFrameProofError(f"{label} failed: {tail}")
    return result


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShortsPosterFrameProofError(f"{label} is not readable JSON") from exc
    if not isinstance(payload, dict):
        raise ShortsPosterFrameProofError(f"{label} must be a JSON object")
    payload["_source_path"] = str(path)
    return payload


def _resolved(root: Path, path: Path) -> Path:
    return (path if path.is_absolute() else root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise ShortsPosterFrameProofError(f"{label} missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise ShortsPosterFrameProofError(f"{label} missing: {path}")


def _validate_output_directory(episode: Path, output: Path) -> None:
    expected = episode / "review" / OUTPUT_NAME
    if output != expected:
        raise ShortsPosterFrameProofError(f"output must be {expected}")


def _validate_cache_directory(episode: Path, cache: Path) -> None:
    expected = episode / "review" / REFERENCE_CACHE_NAME
    if cache != expected:
        raise ShortsPosterFrameProofError(f"reference cache must be {expected}")


def _reject_overlap(output: Path, input_path: Path, message: str) -> None:
    try:
        output.relative_to(input_path)
        raise ShortsPosterFrameProofError(message)
    except ValueError:
        pass
    try:
        input_path.relative_to(output)
        raise ShortsPosterFrameProofError(message)
    except ValueError:
        pass


def _powershell_command(path: Path, root: Path) -> str:
    return f'powershell -ExecutionPolicy Bypass -File "{_relative(path, root)}" -Serve -Port {DEFAULT_PORT}'
