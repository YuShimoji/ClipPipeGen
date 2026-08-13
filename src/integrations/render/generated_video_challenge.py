"""Source-bound, non-adoptive generated-video challenge.

This route exists for the narrow case where the active review media cannot be
recovered but the current host still has a separately provenanced local source.
It renders one mechanically constrained internal review video under a new
identity.  It never substitutes for, relabels, or supplies acceptance evidence
for the missing S2/four-way/OUT-13 artifacts.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Callable

from src.integrations.render import complete_narrative_short as complete
from src.integrations.render import out07_reconstitution as source_authority
from src.integrations.render.subtitle_overlay_visual_proof import _write_ass
from src.integrations.render.vertical_short_candidate import (
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


CHALLENGE_ID = "clip-development-generated-video-challenge-v1-001"
SCHEMA_VERSION = "clippipegen.development_generated_video_challenge.v1"
STATE = "DEVELOPMENT_GENERATED_VIDEO_CHALLENGE_REVIEW_READY"
OUTPUT_NAME_PREFIX = "development_generated_video_challenge_"
DEFAULT_OUTPUT_NAME = "development_generated_video_challenge_v1_001"
FONT_SIZE = 76
MAXIMUM_LINES = 2
MINIMUM_DISPLAY_SECONDS = 0.4
REVIEW_PORT = 8077
MISSING_FOUR_WAY_PROOF_ID = "clip-wiki-integrated-subtitle-cut-proof-v1-001"
S2_ARTIFACT_ID = "clip-s2-subaru-evidence-linked-comparison-v1-002"
OUT13_IDENTITIES = (
    "clip-out13-editorial-video-candidate-v1-001",
    "clip-out13-editorial-video-candidate-v1-003",
    "clip-out13-editorial-video-candidate-v1-005",
)
NOT_REPLACEMENTS = (MISSING_FOUR_WAY_PROOF_ID, S2_ARTIFACT_ID, *OUT13_IDENTITIES)
MECHANICAL_LINE_BREAK_HINTS = {
    "sub_009": {
        "reason": "generated_challenge_two_line_mechanical_repair",
        "preferred_lines": [
            ["ホロライブの番長として、", "団長を倒してやる！！"],
        ],
        "forbidden_boundaries": ["し|て", "や|る"],
    }
}
REQUIRED_FILES = (
    "assets/challenge.mp4",
    "assets/poster_frame.jpg",
    "assets/frame_qa_contact_sheet.jpg",
    "challenge_subtitles.ass",
    "challenge_subtitles.srt",
    "challenge_plan.json",
    "generation_receipt.json",
    "validation_readback.json",
    "review/index.html",
    "review/open_review.ps1",
    "review/serve_review.ps1",
)

RenderExecutor = Callable[..., dict[str, Any]]
PostRenderExecutor = Callable[..., dict[str, Any]]


class GeneratedVideoChallengeError(ValueError):
    """Raised when the challenge cannot be built without identity or safety drift."""


def build_generated_video_challenge(
    *,
    episode_dir: str | Path,
    output_dir: str | Path,
    base_dir: str | Path | None = None,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    render_executor: RenderExecutor | None = None,
    post_render_executor: PostRenderExecutor | None = None,
) -> dict[str, Any]:
    """Build one new ignored review package from the fixed local source authority."""

    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(root, Path(output_dir))
    _validate_destination(root=root, episode=episode, output=output)

    try:
        authority = source_authority.load_current_episode_authority(
            episode_dir=episode,
            base_dir=root,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            execute_media_checks=True,
        )
    except source_authority.Out07ReconstitutionError as exc:
        raise GeneratedVideoChallengeError(
            f"source authority preflight failed: {exc}"
        ) from exc
    _validate_source_identity(authority)

    protected_paths = _protected_paths(root=root, episode=episode)
    protected_before = {
        label: _tree_digest(path, root=root)
        for label, path in protected_paths.items()
        if path.exists()
    }
    input_hashes_before = {
        _relative(Path(path), root): _sha256(Path(path))
        for path in authority["input_paths"]
    }

    layout, subtitle_items, selector = build_vertical_subtitle_presentation(
        authority["semantic_subtitles"],
        application_key="generated_video_challenge_application",
        dimension_source="development_generated_video_challenge_vertical_canvas",
        line_break_hints=MECHANICAL_LINE_BREAK_HINTS,
        font_size_override=FONT_SIZE,
        maximum_lines=MAXIMUM_LINES,
    )
    containment = validate_vertical_subtitle_containment(
        subtitle_items,
        expected_duration=complete.EXPECTED_DURATION_SECONDS,
        layout=layout,
        expected_count=len(complete.EXPECTED_SUBTITLE_IDS),
    )
    mechanical = validate_mechanical_subtitles(
        subtitle_items,
        maximum_lines=MAXIMUM_LINES,
        minimum_display_seconds=MINIMUM_DISPLAY_SECONDS,
    )
    plan = _challenge_plan(authority=authority, subtitle_items=subtitle_items)

    review_parent = episode / "review"
    stage = review_parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    try:
        stage.mkdir(parents=False, exist_ok=False)
        assets = stage / "assets"
        review = stage / "review"
        work = stage / ".work"
        assets.mkdir()
        review.mkdir()
        work.mkdir()

        paths = {
            "video": assets / "challenge.mp4",
            "poster": assets / "poster_frame.jpg",
            "frame_sheet": assets / "frame_qa_contact_sheet.jpg",
            "ass": stage / "challenge_subtitles.ass",
            "srt": stage / "challenge_subtitles.srt",
            "plan": stage / "challenge_plan.json",
            "receipt": stage / "generation_receipt.json",
            "validation": stage / "validation_readback.json",
            "index": review / "index.html",
            "open": review / "open_review.ps1",
            "serve": review / "serve_review.ps1",
            "manifest": stage / "manifest.json",
        }
        _write_ass(paths["ass"], subtitle_items, layout=layout, review_label=None)
        _write_text(paths["srt"], complete._render_srt(subtitle_items))
        _write_json(paths["plan"], plan)
        validate_ass_visible_content(
            paths["ass"],
            expected_count=len(complete.EXPECTED_SUBTITLE_IDS),
            required_texts=tuple(
                str(item.get("wrapped_text") or item["text"]).replace("\n", "")
                for item in subtitle_items
            ),
        )

        executor = render_executor or render_vertical_sequence_assets
        render_result = executor(
            source_video_path=authority["source_video"],
            source_audio_path=authority["source_audio"],
            timeline=authority["timeline"],
            ass_path=paths["ass"],
            video_path=paths["video"],
            compare_sheet_path=None,
            frame_sheet_path=paths["frame_sheet"],
            work_dir=work,
            subtitle_layout=layout,
            expected_duration=complete.EXPECTED_DURATION_SECONDS,
            frame_samples=complete.FRAME_SAMPLES,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        validate_vertical_render_result(
            render_result,
            video_path=paths["video"],
            expected_duration=complete.EXPECTED_DURATION_SECONDS,
        )

        post_executor = post_render_executor or complete._post_render_assets
        post_render = post_executor(
            video_path=paths["video"],
            poster_path=paths["poster"],
            boundaries=complete.EXPECTED_BOUNDARIES_SECONDS,
            expected_duration=complete.EXPECTED_DURATION_SECONDS,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
        if post_render.get("status") != "passed":
            raise GeneratedVideoChallengeError("post-render boundary QA did not pass")
        visual_qa = (
            source_authority._baseline_visual_qa(
                video_path=paths["video"], ffmpeg_path=ffmpeg_path
            )
            if render_executor is None
            else {"status": "not_run_fixture", "samples": []}
        )
        _cleanup_internal_directory(work, expected_parent=stage)

        input_hashes_after = {
            _relative(Path(path), root): _sha256(Path(path))
            for path in authority["input_paths"]
        }
        if input_hashes_after != input_hashes_before:
            raise GeneratedVideoChallengeError(
                "source authority changed during challenge render"
            )
        protected_after = {
            label: _tree_digest(path, root=root)
            for label, path in protected_paths.items()
            if path.exists()
        }
        if protected_after != protected_before:
            raise GeneratedVideoChallengeError(
                "protected review evidence changed during challenge render"
            )

        video_sha = _sha256(paths["video"])
        validation = _validation_readback(
            root=root,
            output=output,
            authority=authority,
            layout=layout,
            subtitle_items=subtitle_items,
            selector=selector,
            containment=containment,
            mechanical=mechanical,
            render_result=render_result,
            post_render=post_render,
            visual_qa=visual_qa,
            video_sha=video_sha,
            input_hashes=input_hashes_before,
            protected_before=protected_before,
        )
        receipt = _generation_receipt(
            root=root,
            output=output,
            authority=authority,
            video_path=paths["video"],
            video_sha=video_sha,
            validation=validation,
        )
        _write_json(paths["validation"], validation)
        _write_json(paths["receipt"], receipt)
        _write_text(paths["index"], _review_html(validation=validation))
        _write_text(paths["serve"], _serve_script())
        _write_text(paths["open"], _open_script())
        manifest = _manifest(stage=stage, output=output, root=root)
        _write_json(paths["manifest"], manifest)
        validate_challenge_package(stage)

        if output.exists():
            raise GeneratedVideoChallengeError(
                "challenge output appeared during render; refusing overwrite"
            )
        stage.replace(output)
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_parent)
        raise

    return {
        "artifact_id": CHALLENGE_ID,
        "state": STATE,
        "source_identity": f"{source_authority.SOURCE_PROVIDER}:{source_authority.SOURCE_PROVIDER_ID}",
        "output_dir": output,
        "video_path": output / "assets/challenge.mp4",
        "video_sha256": _sha256(output / "assets/challenge.mp4"),
        "duration_seconds": complete.EXPECTED_DURATION_SECONDS,
        "review_entrypoint": output / "review/index.html",
        "serve_command": _serve_command(output=output, root=root),
        "open_command": _open_command(output=output, root=root),
        "manifest_path": output / "manifest.json",
        "validation_path": output / "validation_readback.json",
        "receipt_path": output / "generation_receipt.json",
    }


def validate_mechanical_subtitles(
    items: list[dict[str, Any]],
    *,
    maximum_lines: int,
    minimum_display_seconds: float,
) -> dict[str, Any]:
    """Enforce the challenge's mechanical subtitle acceptance boundary."""

    checks: list[dict[str, Any]] = []
    for item in items:
        subtitle_id = str(item.get("subtitle_id") or "")
        lines = [str(line) for line in (item.get("wrapped_lines") or [])]
        duration = round(
            float(item.get("display_end_seconds") or 0.0)
            - float(item.get("display_start_seconds") or 0.0),
            3,
        )
        visible_counts = [_visible_character_count(line) for line in lines]
        if not lines or len(lines) > maximum_lines:
            raise GeneratedVideoChallengeError(
                f"subtitle exceeds {maximum_lines} lines: {subtitle_id}"
            )
        if any(count <= 0 for count in visible_counts):
            raise GeneratedVideoChallengeError(f"subtitle contains an empty line: {subtitle_id}")
        if len(lines) > 1 and visible_counts[-1] == 1:
            raise GeneratedVideoChallengeError(
                f"subtitle leaves a one-character final line: {subtitle_id}"
            )
        if duration + 0.001 < minimum_display_seconds:
            raise GeneratedVideoChallengeError(
                f"subtitle display duration is too short: {subtitle_id}={duration}"
            )
        if item.get("suspicious_tail_line_present") is True:
            raise GeneratedVideoChallengeError(
                f"subtitle leaves a suspicious tail: {subtitle_id}"
            )
        bbox = item.get("font_bbox_wrap_readback") or {}
        selected = bbox.get("selected_wrapped_lines") or lines
        if selected != lines:
            raise GeneratedVideoChallengeError(
                f"subtitle line-break readback does not match: {subtitle_id}"
            )
        checks.append(
            {
                "subtitle_id": subtitle_id,
                "line_count": len(lines),
                "lines": lines,
                "visible_character_counts": visible_counts,
                "display_duration_seconds": duration,
                "one_character_final_line": False,
                "measured_widths": list(
                    ((bbox.get("out05_vertical_balance") or {}).get("measured_widths") or [])
                ),
                "status": "passed",
            }
        )
    return {
        "status": "passed",
        "maximum_line_count": max((item["line_count"] for item in checks), default=0),
        "minimum_display_seconds": min(
            (item["display_duration_seconds"] for item in checks), default=0.0
        ),
        "no_crop_or_overflow_claim": "measured_subtitle_envelope_only",
        "no_one_character_final_line": True,
        "checks": checks,
    }


def validate_challenge_package(package_dir: str | Path) -> dict[str, Any]:
    """Validate exact package inventory, payload hashes, and identity boundaries."""

    package = Path(package_dir).resolve()
    manifest_path = package / "manifest.json"
    manifest = _read_json(manifest_path, "challenge manifest")
    if (
        manifest.get("artifact_id") != CHALLENGE_ID
        or manifest.get("state") != STATE
        or manifest.get("not_replacements") != list(NOT_REPLACEMENTS)
    ):
        raise GeneratedVideoChallengeError("challenge manifest identity changed")
    rows = manifest.get("files")
    if not isinstance(rows, list) or manifest.get("file_count") != len(rows):
        raise GeneratedVideoChallengeError("challenge manifest inventory is invalid")
    expected = set(REQUIRED_FILES)
    names: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise GeneratedVideoChallengeError("challenge manifest row is invalid")
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts or "\\" in row["path"]:
            raise GeneratedVideoChallengeError(f"unsafe manifest path: {row['path']}")
        name = relative.as_posix()
        if name in names:
            raise GeneratedVideoChallengeError(f"duplicate manifest path: {name}")
        names.add(name)
        target = package / relative
        if not target.is_file():
            raise GeneratedVideoChallengeError(f"manifest file missing: {name}")
        if target.stat().st_size != row.get("byte_size") or _sha256(target) != row.get(
            "sha256"
        ):
            raise GeneratedVideoChallengeError(f"manifest mismatch: {name}")
    actual = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if names != expected or actual != expected:
        raise GeneratedVideoChallengeError(
            f"challenge package inventory changed: expected={sorted(expected)} actual={sorted(actual)}"
        )
    integrity = manifest.get("manifest_self_integrity") or {}
    unsigned = dict(manifest)
    unsigned.pop("manifest_self_integrity", None)
    if _canonical_digest(unsigned) != integrity.get("sha256"):
        raise GeneratedVideoChallengeError("manifest self-integrity mismatch")
    validation = _read_json(package / "validation_readback.json", "validation readback")
    receipt = _read_json(package / "generation_receipt.json", "generation receipt")
    video = package / "assets/challenge.mp4"
    serve_script = (package / "review/serve_review.ps1").read_text(encoding="utf-8")
    serve_command = str(receipt.get("serve_command") or "")
    if (
        validation.get("state") != STATE
        or validation.get("human_viewing_claimed") is not False
        or validation.get("production_acceptance") is not False
        or validation.get("public_ready") is not False
        or receipt.get("video_sha256") != _sha256(video)
        or "python -m src.cli.serve_review" not in serve_script
        or "python -m src.cli.serve_review" not in serve_command
        or "src.cli.main serve-review" in serve_script
        or "src.cli.main serve-review" in serve_command
    ):
        raise GeneratedVideoChallengeError("challenge acceptance boundary changed")
    return manifest


def _validate_destination(*, root: Path, episode: Path, output: Path) -> None:
    if episode.name != source_authority.EPISODE_ID or not episode.is_dir():
        raise GeneratedVideoChallengeError(
            f"episode must be the existing {source_authority.EPISODE_ID} directory"
        )
    review_parent = episode / "review"
    if not review_parent.is_dir():
        raise GeneratedVideoChallengeError("episode review directory is missing")
    if output.parent != review_parent or not output.name.startswith(OUTPUT_NAME_PREFIX):
        raise GeneratedVideoChallengeError(
            f"challenge output must be a new {OUTPUT_NAME_PREFIX}* directory under {review_parent}"
        )
    if output.exists():
        raise GeneratedVideoChallengeError("challenge output already exists; refusing overwrite")
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise GeneratedVideoChallengeError("challenge output must remain inside the media repo") from exc
    for protected in (
        review_parent / "jp_pilot01r3_cut_review/human_preview_session",
        review_parent / source_authority.BASELINE_OUTPUT_NAME,
        review_parent / source_authority.COMBINED_OUTPUT_NAME,
    ):
        if output == protected or protected in output.parents or output in protected.parents:
            raise GeneratedVideoChallengeError("challenge output overlaps protected evidence")


def _validate_source_identity(authority: dict[str, Any]) -> None:
    receipt = authority.get("receipt") or {}
    if (
        receipt.get("provider") != source_authority.SOURCE_PROVIDER
        or receipt.get("provider_id") != source_authority.SOURCE_PROVIDER_ID
        or receipt.get("source_video", {}).get("sha256")
        != source_authority.CURRENT_SOURCE_SHA256
        or receipt.get("source_audio", {}).get("sha256")
        != source_authority.CURRENT_AUDIO_SHA256
        or receipt.get("timeline_compatibility", {}).get("status") != "passed"
        or receipt.get("timeline_compatibility", {}).get("sub030_excluded") is not True
    ):
        raise GeneratedVideoChallengeError("challenge source identity is not exact")
    timeline = authority.get("timeline") or []
    if (
        [item.get("id") for item in timeline] != list(complete.EXPECTED_CUT_IDS)
        or abs(float(timeline[-1].get("sequence_end_seconds") or 0.0) - complete.EXPECTED_DURATION_SECONDS)
        > 0.001
        or abs(float(timeline[-1].get("source_end_seconds") or 0.0) - 49.566) > 0.001
    ):
        raise GeneratedVideoChallengeError("challenge timeline identity changed")


def _protected_paths(*, root: Path, episode: Path) -> dict[str, Path]:
    review = episode / "review"
    paths = {
        "active_human_preview_session": review
        / "jp_pilot01r3_cut_review/human_preview_session",
        "out07_reinstantiated_baseline": review / source_authority.BASELINE_OUTPUT_NAME,
        "out07_combined_review": review / source_authority.COMBINED_OUTPUT_NAME,
        "out13_current_host_package": root
        / "episodes/out13_editorial_video_candidate_20260722/review/out13_editorial_video_candidate",
    }
    return paths


def _challenge_plan(
    *, authority: dict[str, Any], subtitle_items: list[dict[str, Any]]
) -> dict[str, Any]:
    by_id = {str(item["subtitle_id"]): item for item in subtitle_items}
    return {
        "schema_version": "clippipegen.generated_video_challenge.plan.v1",
        "artifact_id": CHALLENGE_ID,
        "state": "DEVELOPMENT_GENERATED_VIDEO_CHALLENGE",
        "episode_id": source_authority.EPISODE_ID,
        "source_identity": {
            "provider": source_authority.SOURCE_PROVIDER,
            "provider_id": source_authority.SOURCE_PROVIDER_ID,
            "media_revision_id": source_authority.MEDIA_REVISION_ID,
            "source_video_sha256": authority["source_hash"],
            "source_audio_sha256": authority["audio_hash"],
        },
        "selection_reason": (
            "This is the shortest executable local route with an exact ledger/sidecar/receipt/"
            "rights/caption/cut chain and an existing render integration."
        ),
        "intent": {
            "one_coherent_idea": "A prompt confrontation establishes its premise, resolves the challenge, and exits before the next subtitle/event.",
            "opening": {
                "cut_id": "cut_001",
                "source_range_seconds": [2.453, 9.293],
                "claim": "premise promptness remains a human viewing check",
            },
            "endpoint": {
                "cut_id": "cut_003",
                "source_end_seconds": 49.566,
                "last_subtitle_id": "sub_029",
                "next_subtitle_id": "sub_030",
                "next_subtitle_included": False,
                "claim": "complete payoff/no new event remains a human viewing check",
            },
        },
        "timeline": authority["timeline"],
        "semantic_duration_seconds": complete.EXPECTED_DURATION_SECONDS,
        "subtitle": {
            "count": len(subtitle_items),
            "ids": list(by_id),
            "font_size": FONT_SIZE,
            "maximum_lines": MAXIMUM_LINES,
            "mechanical_change_only": True,
            "text_changed": False,
            "timing_changed": False,
            "minimum_display_seconds": MINIMUM_DISPLAY_SECONDS,
            "historical_timing_readability_evidence_inherited": False,
        },
        "foreground_audio": {
            "owner_count": 1,
            "owner": f"{source_authority.SOURCE_PROVIDER}:{source_authority.SOURCE_PROVIDER_ID}",
            "synthetic_or_secondary_audio_added": False,
        },
        "identity_boundary": {
            "distinct_identity": True,
            "not_replacements": list(NOT_REPLACEMENTS),
            "missing_four_way_state_unchanged": "NON_ADOPTED_REVIEW_PROOF",
            "historical_acceptance_inherited": False,
        },
        "gates": _closed_gates(),
    }


def _validation_readback(
    *,
    root: Path,
    output: Path,
    authority: dict[str, Any],
    layout: dict[str, Any],
    subtitle_items: list[dict[str, Any]],
    selector: dict[str, Any],
    containment: dict[str, Any],
    mechanical: dict[str, Any],
    render_result: dict[str, Any],
    post_render: dict[str, Any],
    visual_qa: dict[str, Any],
    video_sha: str,
    input_hashes: dict[str, str],
    protected_before: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": CHALLENGE_ID,
        "state": STATE,
        "source_identity": {
            "provider": source_authority.SOURCE_PROVIDER,
            "provider_id": source_authority.SOURCE_PROVIDER_ID,
            "media_revision_id": source_authority.MEDIA_REVISION_ID,
            "source_video_sha256": authority["source_hash"],
            "source_audio_sha256": authority["audio_hash"],
            "authority_mode": authority["authority_mode"],
        },
        "identity": {
            "status": "passed",
            "distinct_identity": True,
            "not_replacements": list(NOT_REPLACEMENTS),
            "source_inputs_unchanged": True,
            "protected_artifacts_unchanged": True,
        },
        "intent": {
            "status": "source_bound_and_human_review_pending",
            "opening_premise": "bounded human review dimension",
            "endpoint_payoff": "bounded human review dimension",
            "coherent_idea": "bounded human review dimension",
        },
        "experience": {
            "status": "mechanical_and_headless_checks_passed_human_viewing_pending",
            "duration_seconds": render_result["media"]["duration_seconds"],
            "subtitle": mechanical,
            "review_entrypoint": _relative(output / "review/index.html", root),
            "initial_page_policy": "paused_muted_no_autoplay",
        },
        "integrity": {
            "status": "passed",
            "video_sha256": video_sha,
            "media": render_result["media"],
            "full_decode": render_result["full_decode"],
            "faststart": render_result.get("faststart"),
            "audio": render_result["audio"],
            "boundary_analysis": post_render["boundary_analysis"],
            "sync": post_render["sync"],
            "black_or_corrupt_frame_check": visual_qa,
            "input_hashes": input_hashes,
            "protected_tree_digests": protected_before,
        },
        "subtitle_layout": layout,
        "subtitle_selector": selector,
        "subtitle_containment": containment,
        "subtitle_items": subtitle_items,
        "human_viewing_claimed": False,
        **_closed_gates(),
    }


def _generation_receipt(
    *,
    root: Path,
    output: Path,
    authority: dict[str, Any],
    video_path: Path,
    video_sha: str,
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.generated_video_challenge.receipt.v1",
        "artifact_id": CHALLENGE_ID,
        "state": STATE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "route": "existing_local_render_integration",
        "source_identity": f"{source_authority.SOURCE_PROVIDER}:{source_authority.SOURCE_PROVIDER_ID}",
        "source_video_sha256": authority["source_hash"],
        "source_audio_sha256": authority["audio_hash"],
        "video_path": _relative(output / "assets/challenge.mp4", root),
        "video_byte_size": video_path.stat().st_size,
        "video_sha256": video_sha,
        "duration_seconds": validation["experience"]["duration_seconds"],
        "review_entrypoint": _relative(output / "review/index.html", root),
        "serve_command": _serve_command(output=output, root=root),
        "open_command": _open_command(output=output, root=root),
        "not_replacements": list(NOT_REPLACEMENTS),
        "network_acquisition": False,
        "upload_attempted": False,
        "human_viewing_claimed": False,
    }


def _manifest(*, stage: Path, output: Path, root: Path) -> dict[str, Any]:
    files = []
    for relative_name in REQUIRED_FILES:
        path = stage / Path(relative_name)
        if not path.is_file():
            raise GeneratedVideoChallengeError(f"required package file missing: {relative_name}")
        files.append(
            {
                "path": relative_name,
                "repo_relative_path": _relative(output / relative_name, root),
                "byte_size": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    payload = {
        "schema_version": "clippipegen.generated_video_challenge.manifest.v1",
        "artifact_id": CHALLENGE_ID,
        "state": STATE,
        "source_identity": f"{source_authority.SOURCE_PROVIDER}:{source_authority.SOURCE_PROVIDER_ID}",
        "not_replacements": list(NOT_REPLACEMENTS),
        "file_count": len(files),
        "files": files,
        "gates": _closed_gates(),
    }
    payload["manifest_self_integrity"] = {
        "method": "canonical_sha256_without_manifest_self_integrity",
        "sha256": _canonical_digest(payload),
        "status": "passed",
    }
    return payload


def _review_html(*, validation: dict[str, Any]) -> str:
    video_sha = escape(str(validation["integrity"]["video_sha256"]))
    source_id = escape(
        f"{source_authority.SOURCE_PROVIDER}:{source_authority.SOURCE_PROVIDER_ID}"
    )
    artifact = escape(CHALLENGE_ID)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Generated Video Challenge Review</title>
<style>
:root {{ color-scheme:dark; font-family:"Yu Gothic UI","Noto Sans JP",sans-serif; background:#07111f; color:#eef6ff; }}
* {{ box-sizing:border-box; }} body {{ margin:0; }} main {{ width:min(980px,100%); margin:auto; padding:24px; }}
.eyebrow {{ color:#67e8f9; font-weight:800; letter-spacing:.12em; }} h1 {{ font-size:clamp(1.55rem,4vw,2.4rem); }}
.lead,.muted {{ color:#cbd5e1; }} .video {{ display:flex; justify-content:center; margin:20px 0; }}
video {{ width:auto; height:min(76vh,820px); max-width:100%; aspect-ratio:9/16; background:#000; border:1px solid #334155; border-radius:14px; }}
section {{ background:#0f1d31; border:1px solid #263a55; border-radius:14px; padding:18px; margin:16px 0; }}
code,pre {{ white-space:pre-wrap; overflow-wrap:anywhere; }} li {{ margin:.55rem 0; }}
</style></head><body><main>
<div class="eyebrow">DEVELOPMENT GENERATED VIDEO CHALLENGE</div>
<h1>一つの premise と payoff を 38.638 秒で確認</h1>
<p class="lead">これは欠落中の四択 proof、S2、OUT-13、v003 の代替でも採用証拠でもありません。取得済み source と既存 cut authority を新しい内部診断 identity へ束ねた一件レビューです。</p>
<section><strong>Identity</strong><p>artifact <code>{artifact}</code><br>source <code>{source_id}</code><br>MP4 SHA-256 <code>{video_sha}</code></p></section>
<div class="video"><video controls muted playsinline preload="metadata" src="../assets/challenge.mp4"></video></div>
<section><h2>見る順番</h2><ol>
<li>最初の数秒で状況と対立の premise が分かるか。</li>
<li>最後が payoff を完了し、次の新しい出来事を始めていないか。</li>
<li>字幕が最大2行で、欠け・はみ出し・一文字だけの末尾行がなく、読める時間があるか。</li>
<li>foreground audio の出所が一つに聞こえ、全体が一つの話として読めるか。</li>
</ol><p class="muted">ページは autoplay せず、初期状態は muted / paused です。音声確認は人が明示的に解除した時だけ行います。</p></section>
<section><h2>Coordinator への返却形式</h2><pre>ACCEPT challenge={artifact} note=&lt;optional&gt;
REPAIR issue=&lt;opening|endpoint|subtitle|audio|coherence|other&gt; at=&lt;timestamp|n/a&gt; note=&lt;required&gt;
REJECT reason=&lt;required&gt;</pre>
<p>ACCEPT はこの challenge identity の内部 editorial review のみ。REPAIR は affected dimension だけを新 identity へ修正。REJECT はこの challenge を履歴として保持し、欠落 proof や既存 artifact の状態を変えません。</p></section>
</main></body></html>
"""


def _serve_script() -> str:
    return f"""param([int]$Port = {REVIEW_PORT})
$ErrorActionPreference = 'Stop'
$packageRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../../..')).Path
Push-Location $repoRoot
try {{
    python -m src.cli.serve_review --root $packageRoot --port $Port
}} finally {{
    Pop-Location
}}
"""


def _open_script() -> str:
    return f"""param([int]$Port = {REVIEW_PORT})
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/review/index.html"
Start-Process -FilePath $url
& (Join-Path $PSScriptRoot 'serve_review.ps1') -Port $Port
exit $LASTEXITCODE
"""


def _serve_command(*, output: Path, root: Path) -> str:
    return (
        "python -m src.cli.serve_review --root "
        f'"{_relative(output, root)}" --port {REVIEW_PORT}'
    )


def _open_command(*, output: Path, root: Path) -> str:
    return (
        "powershell -NoProfile -ExecutionPolicy Bypass -File "
        f'"{_relative(output / "review/open_review.ps1", root)}" -Port {REVIEW_PORT}'
    )


def _closed_gates() -> dict[str, Any]:
    return {
        "internal_review_only": True,
        "human_editorial_acceptance": False,
        "historical_acceptance_inherited": False,
        "production_candidate": False,
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "rights_status": "pending",
        "public_ready": False,
        "publishing": False,
        "upload_attempted": False,
    }


def _visible_character_count(text: str) -> int:
    return len(re.sub(r"[\s\u3000]", "", text))


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GeneratedVideoChallengeError(f"{label} is unreadable: {path}") from exc
    if not isinstance(payload, dict):
        raise GeneratedVideoChallengeError(f"{label} must be a JSON object")
    return payload


def _resolved(root: Path, path: Path) -> Path:
    return (path if path.is_absolute() else root / path).resolve()
