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
STATE = "out07_reference_derived_shorts_poster_frame_directions_review_ready"
ACCEPTED_VIDEO_SHA256 = (
    "02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0"
)
SOURCE_VIDEO_SHA256 = "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
CANVAS = (1080, 1920)
CENTER_4_5_SAFE_RECT = (0, 285, 1080, 1635)
TAIL_DURATION_SECONDS = 1.80
END_CAP_DURATION_SECONDS = 0.60
DEFAULT_PORT = 8071
OUTPUT_NAME = "out07_shorts_poster_frame_direction_proof"
REFERENCE_CACHE_NAME = "out07_shorts_poster_reference_cache"
REVIEW_QUESTION = (
    "A/B/Cのどれが実用候補に最も近いか、または全案不採用か。"
    "末尾posterの出現が不自然な場合だけ併記してください。"
)
SURVEY_TIMESTAMPS = (
    18.0,
    20.0,
    22.0,
    24.0,
    26.0,
    28.0,
    30.0,
    32.0,
    34.0,
    36.0,
    38.0,
    40.0,
    42.0,
    48.0,
    50.0,
)


class ShortsPosterFrameProofError(Exception):
    """Raised when the proof cannot be built without boundary drift."""


CANDIDATE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "A",
        "family_id": "single_reaction_hero",
        "family_name_ja": "単一リアクション主役",
        "headline_lines": ["来ねぇ!!"],
        "essential_text_block_count": 1,
        "dominant_face_orientation": "front",
        "source_frame_timestamps": [36.0],
        "source_frame_roles": ["Hajime front-facing close reaction"],
        "source_cut_ids": ["cut_003"],
        "copy_evidence": {
            "subtitle_ids": ["sub_010"],
            "segment_ids": ["seg_000010"],
            "accepted_text": "来ねぇ！！",
            "accepted_source_range_seconds": [22.606, 23.640],
        },
        "reference_ids": ["ref-08", "ref-10", "ref-14", "ref-21"],
        "adopted_relationships": [
            "one dominant forward-facing reaction",
            "one oversized headline",
            "simplified high-contrast background",
        ],
        "deliberate_changes": [
            "retained-source portrait is placed in an original rounded panel",
            "reference-specific colors, fonts, logos and decoration are not reused",
        ],
        "fit_reason": "The accepted cut opens its main friction with Hajime realizing Noel did not come.",
        "essential_bounds": [70, 320, 1010, 1600],
    },
    {
        "candidate_id": "B",
        "family_id": "opposed_dialogue",
        "family_name_ja": "対向する二者会話",
        "headline_lines": ["なんで", "来なかった!?"],
        "essential_text_block_count": 1,
        "dominant_face_orientation": "front_and_three_quarter",
        "source_frame_timestamps": [24.0, 36.0],
        "source_frame_roles": [
            "Noel three-quarter reaction",
            "Hajime front-facing reaction",
        ],
        "source_cut_ids": ["cut_003"],
        "copy_evidence": {
            "subtitle_ids": ["sub_013"],
            "segment_ids": ["seg_000013"],
            "accepted_text": "なんで来なかったんすか！！",
            "accepted_source_range_seconds": [25.109, 26.477],
        },
        "reference_ids": ["ref-02", "ref-09", "ref-15", "ref-17"],
        "adopted_relationships": [
            "two large faces in opposing panels",
            "dialogue friction expressed by one central headline",
            "background detail suppressed behind the face relationship",
        ],
        "deliberate_changes": [
            "separate retained-source moments are recomposed into original diagonal panels",
            "no external cutout, logo, typography or thumbnail pixels are reused",
        ],
        "fit_reason": "The two-person structure makes the accepted absence question understandable at one glance.",
        "essential_bounds": [35, 320, 1045, 1590],
    },
    {
        "candidate_id": "C",
        "family_id": "hero_with_reaction_inset",
        "family_name_ja": "主役＋反応inset",
        "headline_lines": ["待ってたんすよ!!"],
        "essential_text_block_count": 1,
        "dominant_face_orientation": "three_quarter_with_front_inset",
        "source_frame_timestamps": [24.0, 36.0],
        "source_frame_roles": [
            "Noel three-quarter dominant reaction",
            "Hajime front-facing reaction inset",
        ],
        "source_cut_ids": ["cut_003"],
        "copy_evidence": {
            "subtitle_ids": ["sub_014"],
            "segment_ids": ["seg_000014"],
            "accepted_text": "ずっと待ってたんすよ！！",
            "accepted_source_range_seconds": [26.477, 27.378],
        },
        "reference_ids": ["ref-05", "ref-07", "ref-19", "ref-22"],
        "adopted_relationships": [
            "one dominant reaction with one small counter-reaction inset",
            "one large headline",
            "simple graphic field carries the emotional focal point",
        ],
        "deliberate_changes": [
            "the source roles are inverted into a new dominant-plus-inset hierarchy",
            "collage density is reduced to two faces and one text block for Shorts scale",
        ],
        "fit_reason": "Noel's reaction and Hajime's complaint remain truthful without inventing a new event or expression.",
        "essential_bounds": [55, 320, 1025, 1600],
    },
)


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
    corpus_summary = validate_reference_corpus(corpus)
    validate_candidate_specs(CANDIDATE_SPECS)

    cache.mkdir(parents=True, exist_ok=True)
    reference_inputs = _freeze_reference_inputs(
        corpus=corpus,
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
            timestamps=SURVEY_TIMESTAMPS,
            frame_dir=frames,
            ffmpeg_path=resolved_ffmpeg,
        )
        _write_source_contact_sheet(
            extracted,
            stage / "source_frame_contact_sheet.jpg",
            selected_seconds={24.0, 36.0},
        )
        _write_reference_board(
            corpus=corpus,
            reference_inputs=reference_inputs,
            out=stage / "reference_board.jpg",
        )

        candidate_records = _render_posters(
            frame_paths=extracted,
            stage=stage,
            output=output,
            root=root,
        )
        _write_poster_contact_sheet(
            stage=stage,
            out=stage / "poster_direction_contact_sheet.jpg",
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

        reference_manifest = _reference_manifest(
            corpus=corpus,
            corpus_summary=corpus_summary,
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


def validate_reference_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    references = corpus.get("references")
    if not isinstance(references, list) or not 18 <= len(references) <= 30:
        raise ShortsPosterFrameProofError("reference corpus must contain 18-30 entries")
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
        "character_count",
        "face_orientation",
        "face_occupancy",
        "layout_family",
        "text_block_count",
        "text_scale_and_position",
        "background_treatment",
        "hook_type",
        "content_fidelity_risk",
        "translation_note",
    }
    ids: set[str] = set()
    channels: set[str] = set()
    query_strategies: set[str] = set()
    targets: dict[str, int] = {}
    family_refs: dict[str, list[dict[str, Any]]] = {}
    publication_dates: list[date] = []
    latest_cutoff = date.fromisoformat(str(corpus["latest_120_day_cutoff"]))
    latest_count = 0
    for entry in references:
        if not isinstance(entry, dict) or required - entry.keys():
            raise ShortsPosterFrameProofError(
                "reference entry is missing structural annotations"
            )
        reference_id = str(entry["reference_id"])
        if reference_id in ids:
            raise ShortsPosterFrameProofError("reference IDs must be unique")
        ids.add(reference_id)
        if entry["source_type"] not in {"user_supplied", "research_collected"}:
            raise ShortsPosterFrameProofError("unsupported reference source_type")
        if not str(entry["public_url"]).startswith("https://"):
            raise ShortsPosterFrameProofError("reference public URL must use https")
        channels.add(str(entry["channel"]))
        query_strategies.add(str(entry["query_strategy"]))
        target = str(entry["target_surface"])
        targets[target] = targets.get(target, 0) + 1
        family_refs.setdefault(str(entry["layout_family"]), []).append(entry)
        published = date.fromisoformat(str(entry["publication_date"]))
        publication_dates.append(published)
        latest_count += int(published >= latest_cutoff)
    if len(query_strategies) < 2:
        raise ShortsPosterFrameProofError("at least two query strategies are required")
    required_families = {spec["family_id"] for spec in CANDIDATE_SPECS}
    if set(family_refs) != required_families:
        raise ShortsPosterFrameProofError(
            "reference corpus must resolve to exactly three families"
        )
    for family_id, entries in family_refs.items():
        family_channels = {str(entry["channel"]) for entry in entries}
        if len(entries) < 3 or len(family_channels) < 2:
            raise ShortsPosterFrameProofError(
                f"composition family lacks multi-source support: {family_id}"
            )
    return {
        "reference_count": len(references),
        "channel_count": len(channels),
        "query_strategy_count": len(query_strategies),
        "latest_120_day_count": latest_count,
        "date_coverage": [
            min(publication_dates).isoformat(),
            max(publication_dates).isoformat(),
        ],
        "target_surfaces": targets,
        "family_counts": {
            key: len(value) for key, value in sorted(family_refs.items())
        },
    }


def validate_candidate_specs(specs: tuple[dict[str, Any], ...]) -> None:
    if len(specs) != 3 or [spec["candidate_id"] for spec in specs] != ["A", "B", "C"]:
        raise ShortsPosterFrameProofError("exactly candidates A, B and C are required")
    if len({spec["family_id"] for spec in specs}) != 3:
        raise ShortsPosterFrameProofError(
            "candidate composition families must be distinct"
        )
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
            raise ShortsPosterFrameProofError(
                "dominant back-facing character is forbidden"
            )
        if len(spec["reference_ids"]) < 3:
            raise ShortsPosterFrameProofError(
                "candidate must map to multiple references"
            )


def _freeze_reference_inputs(
    *, corpus: dict[str, Any], cache_dir: Path, fetch_missing: bool
) -> list[Path]:
    from PIL import Image

    paths: list[Path] = []
    for entry in corpus["references"]:
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
        out = frame_dir / f"frame_{index:02d}_{seconds:.1f}s.png"
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
        _run(command, label=f"source frame {seconds:.1f}s")
        _require_file(out, f"source frame {seconds:.1f}s")
        outputs[seconds] = out
    return outputs


def _render_posters(
    *, frame_paths: dict[float, Path], stage: Path, output: Path, root: Path
) -> list[dict[str, Any]]:
    from PIL import Image

    frames = {
        seconds: Image.open(path).convert("RGB")
        for seconds, path in frame_paths.items()
        if seconds in {24.0, 32.0, 36.0}
    }
    renderers = {
        "A": lambda: _poster_a(frames[36.0]),
        "B": lambda: _poster_b(frames[24.0], frames[36.0]),
        "C": lambda: _poster_c(frames[24.0], frames[36.0]),
    }
    records: list[dict[str, Any]] = []
    try:
        for spec in CANDIDATE_SPECS:
            candidate_id = spec["candidate_id"]
            image = renderers[candidate_id]()
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
            records.append(
                {
                    **spec,
                    "path": _relative(output / out.name, root),
                    "sha256": _sha256(out),
                    "width": CANVAS[0],
                    "height": CANVAS[1],
                    "mode": "RGB",
                    "format": "JPEG",
                    "full_9_16_preview": [180, 320],
                    "center_4_5_preview": [160, 200],
                    "center_4_5_crop_survives": True,
                    "third_party_pixels_used": False,
                    "ai_face_or_expression_change": False,
                    "raw_scene_screenshot_as_finished_background": False,
                    "human_acceptance": "pending",
                }
            )
    finally:
        for image in frames.values():
            image.close()
    return records


def _poster_a(hajime_frame: Any) -> Any:
    from PIL import ImageDraw

    image = _gradient_canvas((16, 32, 76), (14, 126, 153))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(300, 1636, 110):
        draw.rounded_rectangle(
            (50, y, 1030, y + 45), radius=22, fill=(255, 255, 255, 18)
        )
    draw.rounded_rectangle((58, 610, 1022, 1608), radius=92, fill=(4, 9, 24, 135))
    portrait = _cover_crop(hajime_frame, (860, 900), focus=(0.53, 0.40))
    _paste_rounded(
        image, portrait, (110, 650), radius=78, outline=(255, 226, 73), width=18
    )
    font = _project_font(178, weight="Black")
    _draw_centered_text(
        draw,
        ["来ねぇ!!"],
        center=(540, 465),
        font=font,
        fill=(255, 244, 91),
        stroke_fill=(7, 15, 39),
        stroke_width=18,
        spacing=0,
    )
    return image


def _poster_b(noel_frame: Any, hajime_frame: Any) -> Any:
    from PIL import ImageDraw

    image = _gradient_canvas((88, 18, 74), (19, 49, 97))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.polygon(
        [(0, 570), (540, 640), (540, 1635), (0, 1635)], fill=(239, 77, 130, 230)
    )
    draw.polygon(
        [(540, 640), (1080, 570), (1080, 1635), (540, 1635)], fill=(255, 190, 60, 235)
    )
    draw.polygon(
        [(500, 600), (580, 590), (550, 1635), (510, 1635)], fill=(255, 255, 255, 220)
    )
    noel = _cover_crop(noel_frame, (470, 900), focus=(0.52, 0.40))
    hajime = _cover_crop(hajime_frame, (470, 900), focus=(0.53, 0.40))
    _paste_rounded(image, noel, (45, 655), radius=58, outline=(255, 255, 255), width=14)
    _paste_rounded(
        image, hajime, (565, 655), radius=58, outline=(255, 255, 255), width=14
    )
    font = _project_font(142, weight="Black")
    _draw_centered_text(
        draw,
        ["なんで", "来なかった!?"],
        center=(540, 455),
        font=font,
        fill=(255, 255, 255),
        stroke_fill=(48, 10, 43),
        stroke_width=17,
        spacing=-8,
    )
    return image


def _poster_c(noel_frame: Any, hajime_frame: Any) -> Any:
    from PIL import ImageDraw

    image = _gradient_canvas((43, 16, 75), (111, 42, 120))
    draw = ImageDraw.Draw(image, "RGBA")
    center = (540, 1120)
    for index in range(24):
        angle = math.tau * index / 24
        inner = 260
        outer = 760
        p1 = (
            center[0] + math.cos(angle - 0.035) * inner,
            center[1] + math.sin(angle - 0.035) * inner,
        )
        p2 = (
            center[0] + math.cos(angle + 0.035) * inner,
            center[1] + math.sin(angle + 0.035) * inner,
        )
        p3 = (
            center[0] + math.cos(angle + 0.02) * outer,
            center[1] + math.sin(angle + 0.02) * outer,
        )
        p4 = (
            center[0] + math.cos(angle - 0.02) * outer,
            center[1] + math.sin(angle - 0.02) * outer,
        )
        draw.polygon([p1, p2, p3, p4], fill=(255, 255, 255, 13))
    draw.rounded_rectangle((55, 600, 945, 1605), radius=110, fill=(16, 8, 35, 150))
    noel = _cover_crop(noel_frame, (760, 900), focus=(0.52, 0.40))
    _paste_rounded(image, noel, (95, 650), radius=90, outline=(211, 145, 255), width=18)
    hajime = _cover_crop(hajime_frame, (300, 300), focus=(0.53, 0.38))
    _paste_circle(image, hajime, (700, 1210), outline=(255, 225, 81), width=18)
    font = _project_font(112, weight="Black")
    _draw_centered_text(
        draw,
        ["待ってたんすよ!!"],
        center=(540, 445),
        font=font,
        fill=(255, 243, 111),
        stroke_fill=(42, 11, 70),
        stroke_width=16,
        spacing=0,
    )
    return image


def _gradient_canvas(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Any:
    from PIL import Image

    image = Image.new("RGB", CANVAS)
    pixels = image.load()
    for y in range(CANVAS[1]):
        ratio = y / (CANVAS[1] - 1)
        color = tuple(round(a * (1 - ratio) + b * ratio) for a, b in zip(top, bottom))
        for x in range(CANVAS[0]):
            pixels[x, y] = color
    return image


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


def _paste_rounded(
    canvas: Any,
    source: Any,
    xy: tuple[int, int],
    *,
    radius: int,
    outline: tuple[int, int, int],
    width: int,
) -> None:
    from PIL import Image, ImageDraw

    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, source.width - 1, source.height - 1), radius=radius, fill=255
    )
    canvas.paste(source, xy, mask)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (xy[0], xy[1], xy[0] + source.width - 1, xy[1] + source.height - 1),
        radius=radius,
        outline=outline,
        width=width,
    )


def _paste_circle(
    canvas: Any,
    source: Any,
    xy: tuple[int, int],
    *,
    outline: tuple[int, int, int],
    width: int,
) -> None:
    from PIL import Image, ImageDraw

    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, source.width - 1, source.height - 1), fill=255)
    canvas.paste(source, xy, mask)
    ImageDraw.Draw(canvas).ellipse(
        (xy[0], xy[1], xy[0] + source.width - 1, xy[1] + source.height - 1),
        outline=outline,
        width=width,
    )


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


def _write_source_contact_sheet(
    frames: dict[float, Path], out: Path, *, selected_seconds: set[float]
) -> None:
    from PIL import Image, ImageDraw

    tile_w, image_h, label_h = 384, 216, 44
    canvas = Image.new("RGB", (tile_w * 5, (image_h + label_h) * 3), (14, 17, 23))
    draw = ImageDraw.Draw(canvas)
    font = _project_font(25)
    for index, (seconds, path) in enumerate(frames.items()):
        with Image.open(path) as source:
            small = source.convert("RGB").resize((tile_w, image_h))
        col, row = index % 5, index // 5
        x, y = col * tile_w, row * (image_h + label_h)
        canvas.paste(small, (x, y))
        selected = seconds in selected_seconds
        color = (255, 224, 77) if selected else (213, 220, 232)
        label = f"{seconds:.1f}s" + ("  selected source" if selected else "")
        draw.rectangle(
            (x, y, x + tile_w - 1, y + image_h + label_h - 1),
            outline=color,
            width=5 if selected else 2,
        )
        draw.text((x + 10, y + image_h + 6), label, font=font, fill=color)
    canvas.save(out, format="JPEG", quality=92, subsampling=0, optimize=False)


def _write_reference_board(
    *, corpus: dict[str, Any], reference_inputs: list[Path], out: Path
) -> None:
    from PIL import Image, ImageDraw

    tile_w, image_h, label_h = 300, 170, 52
    canvas = Image.new("RGB", (tile_w * 4, (image_h + label_h) * 6), (17, 20, 24))
    draw = ImageDraw.Draw(canvas)
    font = _project_font(17)
    for index, (entry, path) in enumerate(zip(corpus["references"], reference_inputs)):
        with Image.open(path) as source:
            small = _cover_crop(
                source.convert("RGB"), (tile_w, image_h), focus=(0.5, 0.5)
            )
        col, row = index % 4, index // 4
        x, y = col * tile_w, row * (image_h + label_h)
        canvas.paste(small, (x, y))
        draw.rectangle(
            (x, y, x + tile_w - 1, y + image_h + label_h - 1),
            outline=(56, 65, 77),
            width=2,
        )
        target = (
            "native 9:16"
            if "native_vertical" in entry["target_surface"]
            else "16:9 -> 9:16"
        )
        draw.text(
            (x + 8, y + image_h + 4),
            f"{entry['reference_id']}  {entry['layout_family']}",
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
    records: list[dict[str, Any]] = []
    for candidate_id in ("A", "B", "C"):
        poster = stage / f"poster_{candidate_id}_1080x1920.jpg"
        out = stage / f"transition_{candidate_id}.mp4"
        filter_complex = (
            f"[0:v]trim=duration={TAIL_DURATION_SECONDS:.2f},setpts=PTS-STARTPTS,"
            "scale=1080:1920,setsar=1,fps=30,format=yuv420p[v0];"
            f"[1:v]trim=duration={END_CAP_DURATION_SECONDS:.2f},setpts=PTS-STARTPTS,"
            "scale=1080:1920,setsar=1,fps=30,format=yuv420p[v1];"
            "[v0][v1]concat=n=2:v=1:a=0[v];"
            f"[0:a]atrim=duration={TAIL_DURATION_SECONDS:.2f},asetpts=PTS-STARTPTS,"
            "aformat=sample_rates=48000:channel_layouts=stereo[a0];"
            f"anullsrc=r=48000:cl=stereo,atrim=duration={END_CAP_DURATION_SECONDS:.2f},"
            "asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[a]"
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
            f"{TAIL_DURATION_SECONDS + END_CAP_DURATION_SECONDS:.2f}",
            str(out),
        ]
        _run(command, label=f"transition {candidate_id}")
        probe = _probe_media(out, ffprobe_path=ffprobe_path)
        if probe["width"] != 1080 or probe["height"] != 1920:
            raise ShortsPosterFrameProofError("transition aspect or dimensions invalid")
        if abs(float(probe["duration_seconds"]) - 2.40) > 0.12:
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
                "video_treatment": "hard_cut_to_shared_static_poster_end_cap",
                "audio_treatment": "accepted_narrative_audio_then_intentional_silence_in_end_cap",
                "full_decode": "passed",
                "review_only": True,
                "replaces_accepted_video": False,
            }
        )
    return records


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
    reference_inputs: list[Path],
    root: Path,
    reference_board: Path,
) -> dict[str, Any]:
    entries = []
    for entry, path in zip(corpus["references"], reference_inputs):
        entries.append(
            {
                **entry,
                "thumbnail_image_sha256": _sha256(path),
                "thumbnail_image_storage": "ignored_local_frozen_cache_not_packaged_individually",
                "tracked_pixel_reuse_allowed": False,
            }
        )
    families = []
    for spec in CANDIDATE_SPECS:
        family_entries = [
            entry for entry in entries if entry["layout_family"] == spec["family_id"]
        ]
        families.append(
            {
                "family_id": spec["family_id"],
                "family_name_ja": spec["family_name_ja"],
                "reference_ids": [entry["reference_id"] for entry in family_entries],
                "channels": sorted({entry["channel"] for entry in family_entries}),
                "recurring_relationships": spec["adopted_relationships"],
            }
        )
    return {
        "schema_version": "clippipegen.out07.reference_manifest.v0",
        "artifact_id": ARTIFACT_ID,
        "source_priority": corpus["reference_priority"],
        "query_strategies": corpus["query_strategies"],
        "collection_stop_reason": corpus["collection_stop_reason"],
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
            "survey_timestamps_seconds": list(SURVEY_TIMESTAMPS),
            "selected_timestamps_seconds": [24.0, 36.0],
            "dominant_back_facing_frames_rejected": True,
            "visual_inspection_required_and_performed": True,
            "contact_sheet": _relative(final_paths["source_contact_sheet"], root),
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
<img class="poster-main" id="poster-{candidate_id}" src="{poster_name}" alt="候補{candidate_id} {escape(candidate["family_name_ja"])}">
<div class="reduced"><div><span>180×320</span><img class="preview-9x16" src="{poster_name}" alt="候補{candidate_id} 180x320"></div>
<div><span>center 4:5 / 160×200</span><img class="preview-4x5" src="{poster_name}" alt="候補{candidate_id} center 4:5"></div></div>
</figure>"""
        )
        transition_sections.append(
            f"""<figure><figcaption><strong>{candidate_id}</strong> — 末尾1.80秒＋poster 0.60秒</figcaption>
<video id="transition-{candidate_id}" controls preload="metadata" src="transition_{candidate_id}.mp4"></video></figure>"""
        )
    evidence_rows = "".join(
        f"<tr><td>{candidate['candidate_id']}</td><td>{escape(candidate['family_name_ja'])}</td>"
        f"<td>{escape(', '.join(f'{value:.1f}s' for value in candidate['source_frame_timestamps']))}</td>"
        f"<td>{escape(candidate['copy_evidence']['accepted_text'])}</td>"
        f"<td>{escape(', '.join(candidate['reference_ids']))}</td></tr>"
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
.reduced{{display:flex;gap:16px;align-items:end;justify-content:center;margin-top:14px;flex-wrap:wrap}}.reduced>div{{display:grid;gap:5px;justify-items:center;color:var(--muted);font-size:13px}}
.preview-9x16{{width:180px;height:320px;object-fit:cover;border:1px solid var(--line)}}.preview-4x5{{width:160px;height:200px;object-fit:cover;object-position:center;border:1px solid var(--line)}}
section{{margin-top:34px}}.sheet{{display:block;width:100%;height:auto;border:1px solid var(--line);background:#000}}
.transitions{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}}video{{display:block;width:100%;max-height:72vh;background:#000;border:1px solid var(--line);border-radius:14px}}
details{{margin-top:34px;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}}summary{{cursor:pointer;font-weight:800;font-size:19px}}table{{width:100%;border-collapse:collapse;margin-top:14px;font-size:14px}}th,td{{border-top:1px solid var(--line);padding:9px;text-align:left;vertical-align:top}}code{{overflow-wrap:anywhere}}.secondary{{color:var(--muted)}}
@media(max-width:900px){{.candidates,.transitions{{grid-template-columns:1fr}}.poster-main{{max-width:560px;margin:0 auto}}main{{padding:16px}}table{{display:block;overflow-x:auto}}}}
</style></head><body><main>
<header><p class="status">9:16 Shorts selectable in-video poster / human selection pending</p><h1>poster frame 方向比較 A／B／C</h1><p class="question">{escape(REVIEW_QUESTION)}</p></header>
<section class="candidates" id="candidates">{"".join(candidate_sections)}</section>
<section><h2>3案比較</h2><img class="sheet" id="poster-contact-sheet" src="poster_direction_contact_sheet.jpg" alt="poster方向A B C比較シート"></section>
<section><h2>末尾transition proof</h2><p class="secondary">受入済み本編の末尾1.80秒に、共通処理の静止poster 0.60秒をハードカットで付加。poster区間だけ意図的に無音です。proofは本編を置換しません。</p><div class="transitions">{"".join(transition_sections)}</div></section>
<details id="evidence"><summary>参照構造・元フレーム・provenance</summary>
<p>24件／{readback["reference_corpus"]["channel_count"]}チャンネル。第三者画像はこのignored local proofのreference boardだけに保持し、候補A/B/Cには流用していません。</p>
<table><thead><tr><th>候補</th><th>構図文法</th><th>実素材timestamp</th><th>受入済み内容根拠</th><th>構造参照</th></tr></thead><tbody>{evidence_rows}</tbody></table>
<h3>元フレームsurvey</h3><img class="sheet" src="source_frame_contact_sheet.jpg" alt="元動画の正面・斜め正面フレームsurvey">
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
        "source_contact_sheet": output / "source_frame_contact_sheet.jpg",
        "poster_contact_sheet": output / "poster_direction_contact_sheet.jpg",
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
    "source_frame_contact_sheet.jpg",
    "reference_board.jpg",
    "reference_manifest.json",
    "poster_direction_readback.json",
    "transition_A.mp4",
    "transition_B.mp4",
    "transition_C.mp4",
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
    for candidate_id in ("A", "B", "C"):
        with Image.open(stage / f"poster_{candidate_id}_1080x1920.jpg") as image:
            if image.size != CANVAS or image.mode != "RGB":
                raise ShortsPosterFrameProofError(
                    "poster file dimensions or mode invalid"
                )
    manifest = _read_json(stage / "reference_manifest.json", "reference manifest")
    if len(manifest["references"]) < 18 or len(manifest["families"]) != 3:
        raise ShortsPosterFrameProofError("reference manifest coverage mismatch")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count('class="candidate"') != 3 or html.count("<video") != 3:
        raise ShortsPosterFrameProofError(
            "review page candidate or transition count mismatch"
        )
    if html.count(REVIEW_QUESTION) != 1 or "<details open" in html:
        raise ShortsPosterFrameProofError(
            "review page question or folded evidence mismatch"
        )


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
