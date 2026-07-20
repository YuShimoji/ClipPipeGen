"""Build the OUT-11 five-source scorecard and combined three-video review.

The builder is intentionally media-agnostic.  It consumes three already-built,
hash-bound candidate packages and five data-driven scorecard rows.  It does not
render, fetch, select a winner, or grant rights, production, or publication
acceptance.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from html import escape
from pathlib import Path
from typing import Any


ARTIFACT_ID = "clip-out11-five-source-short-portfolio-wave-v0-001"
STATE = "OUT11_FIVE_SOURCE_SHORT_PORTFOLIO_COMBINED_REVIEW_READY"
SCHEMA_VERSION = "clippipegen.out11.five_source_short_portfolio.v0"
CONFIG_SCHEMA_VERSION = "clippipegen.out11.five_source_short_portfolio_input.v0"
REVIEW_HOST = "127.0.0.1"
REVIEW_PORT = 8074
INITIAL_VOLUME_CEILING = 0.25
REVIEW_QUESTION = (
    "OUT-10は最後のセリフまで自然に完結したか。"
    "第4・第5候補はそれぞれ一本のShortとして内容・テンポ・字幕・音声・構図・終端が成立しているか。"
    "候補ごとに明確な違和感があれば自由に教えてください。"
)
EXPECTED_REVIEW_ROLES = ("out10", "source04", "source05")
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
SHA256 = re.compile(r"[0-9a-f]{64}")
REQUIRED_SCORECARD_COLUMNS = (
    "portfolio_slot",
    "source_identity",
    "video_identity",
    "episode_identity",
    "language",
    "source_resolution",
    "source_aspect",
    "selected_duration_seconds",
    "transcript_caption_authority",
    "native_baked_caption_status",
    "speaker_count",
    "speaker_identity_authority",
    "cue_count",
    "average_cue_length_seconds",
    "maximum_cue_length_seconds",
    "composition_strategy",
    "caption_handling",
    "endpoint_evidence",
    "render_count",
    "corrective_render_count",
    "mp4_sha256",
    "human_acceptance_status",
    "source_specific_debt",
    "reusable_validation",
    "source_specific_human_judgment",
    "important_content_conflict",
    "production_status",
    "rights_status",
)
_BANNED_SCORECARD_KEYS = {
    "winner",
    "selected_winner",
    "production_ready",
    "universal_crop",
    "universal_caption_style",
    "universal_speaker_color_policy",
}


class FiveSourceShortPortfolioError(ValueError):
    """Raised when source evidence or the combined review contract is invalid."""


def build_five_source_short_portfolio(
    *,
    config_path: Path,
    output_dir: Path,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Build one atomic, package-contained OUT-11 review surface."""

    root = (base_dir or Path.cwd()).resolve()
    config_file = _resolved(root, config_path)
    output = _resolved(root, output_dir)
    _require_within(config_file, root, "OUT-11 config")
    _require_within(output, root, "OUT-11 output")
    _require_file(config_file, "OUT-11 config")
    if output == root or output.parent == root or not output.name.startswith("out11_"):
        raise FiveSourceShortPortfolioError(
            "output directory must be a nested path whose name starts with out11_"
        )
    _safe_identifier(output.name, "output directory")

    config = _read_json(config_file, "OUT-11 config")
    normalized = _normalize_config(config=config, root=root)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    stage.mkdir()
    backup: Path | None = None
    try:
        candidates_dir = stage / "candidates"
        evidence_dir = stage / "evidence"
        candidates_dir.mkdir()
        evidence_dir.mkdir()
        copied_candidates = _copy_candidate_packages(
            stage=stage,
            candidates=normalized["review_candidates"],
        )
        scorecard = _build_scorecard(normalized["scorecard_rows"])
        _write_json(stage / "five_source_scorecard.json", scorecard)

        review_access = _review_access_contract(output=output, root=root)
        readback = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": ARTIFACT_ID,
            "state": STATE,
            "review_question": REVIEW_QUESTION,
            "review_question_count": 1,
            "review_candidates": copied_candidates,
            "scorecard": {
                "package_relative_path": "five_source_scorecard.json",
                "row_count": 5,
                "review_media_count": 3,
                "accepted_context_only_slots": list(
                    normalized["accepted_context_only_slots"]
                ),
            },
            "review_access": review_access,
            "review_entrypoint": review_access["clean_human_url"],
            "canonical_server_command": review_access[
                "canonical_foreground_server_command"
            ],
            "open_command": review_access["convenience_open_command"],
            "boundaries": dict(normalized["boundaries"]),
            "automation_boundary": {
                "automated": [
                    "source_package_manifest_validation",
                    "exact_mp4_hash_and_size_validation",
                    "package_contained_byte_copy",
                    "five_row_scorecard_contract",
                    "safe_review_playback_initialization",
                ],
                "source_specific_observation_required": [
                    "composition",
                    "caption_handling",
                    "endpoint_semantics",
                ],
                "not_decided": [
                    "portfolio_subtitle_differentiation",
                    "production_subtitle_design",
                    "rights_or_publication_acceptance",
                ],
            },
            "regeneration_command": (
                "uvx python -m src.cli.main build-five-source-short-portfolio "
                f"--config {_relative(config_file, root)} "
                f"--output-dir {_relative(output, root)}"
            ),
        }
        _write_json(stage / "review_readback.json", readback)
        _write_text(stage / "index.html", _render_html(readback, scorecard))
        _write_text(
            stage / "serve_preview.ps1",
            _serve_script(candidates=copied_candidates),
        )
        _write_text(stage / "open_preview.ps1", _open_script())

        files = _manifest_file_rows(stage)
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": ARTIFACT_ID,
            "state": STATE,
            "review_question_sha256": _payload_sha256(REVIEW_QUESTION),
            "candidate_videos": [
                {
                    "role": item["role"],
                    "portfolio_slot": item["portfolio_slot"],
                    "package_relative_path": item["video"]["package_relative_path"],
                    "sha256": item["video"]["sha256"],
                    "byte_size": item["video"]["byte_size"],
                }
                for item in copied_candidates
            ],
            "source_packages": [
                {
                    "role": item["role"],
                    "artifact_id": item["source_artifact_id"],
                    "state": item["source_state"],
                    "readback_sha256": item["source_readback"]["sha256"],
                    "manifest_sha256": item["source_manifest"]["sha256"],
                    "source_manifest_self_sha256": item["source_manifest"][
                        "self_sha256"
                    ],
                }
                for item in copied_candidates
            ],
            "files": files,
            "file_count": len(files),
            "closed_gates": dict(normalized["boundaries"]),
            "manifest_self_integrity": {
                "algorithm": "sha256-canonical-json-self-null",
                "sha256": None,
            },
        }
        manifest["manifest_self_integrity"]["sha256"] = (
            _canonical_manifest_self_hash(manifest)
        )
        _write_json(stage / "review_manifest.json", manifest)
        _validate_staged_package(stage=stage, readback=readback, manifest=manifest)
        backup = _atomic_promote(stage=stage, output=output)
    except Exception:
        if stage.exists():
            _remove_owned_tree(stage=stage, expected_parent=output.parent)
        raise
    finally:
        if backup is not None and backup.exists():
            _remove_owned_tree(stage=backup, expected_parent=output.parent)

    return {
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "output_dir": output,
        "index_path": output / "index.html",
        "readback_path": output / "review_readback.json",
        "manifest_path": output / "review_manifest.json",
        "scorecard_path": output / "five_source_scorecard.json",
        "readback": _read_json(output / "review_readback.json", "review readback"),
    }


def _normalize_config(*, config: dict[str, Any], root: Path) -> dict[str, Any]:
    if config.get("schema_version") != CONFIG_SCHEMA_VERSION:
        raise FiveSourceShortPortfolioError("OUT-11 config schema mismatch")
    if config.get("artifact_id") != ARTIFACT_ID or config.get("state") != STATE:
        raise FiveSourceShortPortfolioError("OUT-11 config identity mismatch")
    if config.get("review_question") != REVIEW_QUESTION:
        raise FiveSourceShortPortfolioError("combined review question is not exact")

    raw_candidates = config.get("review_candidates")
    if not isinstance(raw_candidates, list) or len(raw_candidates) != 3:
        raise FiveSourceShortPortfolioError("exactly three review candidates are required")
    candidates = [
        _load_candidate_binding(raw=item, root=root, expected_role=role)
        for role, item in zip(EXPECTED_REVIEW_ROLES, raw_candidates, strict=True)
    ]
    identities = [item["video_identity"] for item in candidates]
    if len(set(identities)) != 3:
        raise FiveSourceShortPortfolioError(
            "review candidate recording identities must be distinct"
        )

    rows = config.get("scorecard_rows")
    if not isinstance(rows, list) or len(rows) != 5:
        raise FiveSourceShortPortfolioError("scorecard must contain exactly five rows")
    normalized_rows = [_validate_scorecard_row(row) for row in rows]
    slots = [row["portfolio_slot"] for row in normalized_rows]
    if len(set(slots)) != 5:
        raise FiveSourceShortPortfolioError("scorecard slots must be unique")

    accepted_slots = config.get("accepted_context_only_slots")
    if not isinstance(accepted_slots, list) or len(accepted_slots) != 2:
        raise FiveSourceShortPortfolioError(
            "exactly two accepted context-only slots are required"
        )
    accepted = tuple(str(item) for item in accepted_slots)
    if len(set(accepted)) != 2 or any(slot not in slots for slot in accepted):
        raise FiveSourceShortPortfolioError(
            "accepted context-only slots do not match scorecard"
        )
    rows_by_slot = {row["portfolio_slot"]: row for row in normalized_rows}
    for slot in accepted:
        row = rows_by_slot[slot]
        if row["human_acceptance_status"] != "accepted_internal":
            raise FiveSourceShortPortfolioError(
                "context-only rows must remain accepted_internal"
            )

    candidate_slots = {item["portfolio_slot"] for item in candidates}
    if candidate_slots != set(slots) - set(accepted):
        raise FiveSourceShortPortfolioError(
            "review candidates must cover the three non-context scorecard rows"
        )
    for item in candidates:
        row = rows_by_slot[item["portfolio_slot"]]
        if row["human_acceptance_status"] != "human_review_pending":
            raise FiveSourceShortPortfolioError(
                "review candidate rows must remain human_review_pending"
            )
        if row["mp4_sha256"] != item["video_sha256"]:
            raise FiveSourceShortPortfolioError(
                f"scorecard MP4 hash mismatch: {item['role']}"
            )
        if row["video_identity"] != item["video_identity"]:
            raise FiveSourceShortPortfolioError(
                f"scorecard video identity mismatch: {item['role']}"
            )
        if row["episode_identity"] != item["episode_identity"]:
            raise FiveSourceShortPortfolioError(
                f"scorecard episode identity mismatch: {item['role']}"
            )
        if (
            abs(
                _number(row["selected_duration_seconds"], "selected duration")
                - item["duration_seconds"]
            )
            > 0.05
        ):
            raise FiveSourceShortPortfolioError(
                f"scorecard duration mismatch: {item['role']}"
            )

    boundaries = config.get("boundaries")
    expected_boundaries = {
        "rights_acceptance": False,
        "production_acceptance": False,
        "thumbnail_acceptance": False,
        "public_or_publishing_acceptance": False,
        "winner_selected": False,
        "universal_crop_claimed": False,
        "universal_caption_style_claimed": False,
        "universal_speaker_color_policy_claimed": False,
        "human_review_pending": True,
        "acceptance_granted": False,
    }
    if not isinstance(boundaries, dict) or any(
        boundaries.get(key) != value for key, value in expected_boundaries.items()
    ):
        raise FiveSourceShortPortfolioError("OUT-11 gates are not closed")
    return {
        "review_candidates": candidates,
        "scorecard_rows": normalized_rows,
        "accepted_context_only_slots": accepted,
        "boundaries": expected_boundaries,
    }


def _load_candidate_binding(
    *, raw: Any, root: Path, expected_role: str
) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("role") != expected_role:
        raise FiveSourceShortPortfolioError(
            f"review candidate order/role mismatch: expected {expected_role}"
        )
    package = _resolved(root, Path(str(raw.get("package_dir") or "")))
    _require_within(package, root, f"{expected_role} source package")
    _require_directory(package, f"{expected_role} source package")
    readback_relative = _safe_relative_file(
        raw.get("readback_relative_path"), "source readback"
    )
    manifest_relative = _safe_relative_file(
        raw.get("manifest_relative_path"), "source manifest"
    )
    video_relative = _safe_relative_file(
        raw.get("video_relative_path"), "source video"
    )
    readback_path = (package / readback_relative).resolve()
    manifest_path = (package / manifest_relative).resolve()
    video_path = (package / video_relative).resolve()
    for path, label in (
        (readback_path, "source readback"),
        (manifest_path, "source manifest"),
        (video_path, "source video"),
    ):
        _require_within(path, package, label)
        _require_file(path, label)

    readback = _read_json(readback_path, f"{expected_role} source readback")
    manifest = _read_json(manifest_path, f"{expected_role} source manifest")
    expected_readback_sha = _sha_value(
        raw.get("readback_sha256"), "source readback SHA-256"
    )
    expected_manifest_sha = _sha_value(
        raw.get("manifest_sha256"), "source manifest SHA-256"
    )
    if (
        _sha256(readback_path) != expected_readback_sha
        or _sha256(manifest_path) != expected_manifest_sha
    ):
        raise FiveSourceShortPortfolioError(
            f"source readback/manifest config binding mismatch: {expected_role}"
        )
    source_artifact = str(raw.get("source_artifact_id") or "")
    source_state = str(raw.get("source_state") or "")
    if (
        readback.get("artifact_id") != source_artifact
        or manifest.get("artifact_id") != source_artifact
        or readback.get("state") != source_state
        or manifest.get("state") != source_state
    ):
        raise FiveSourceShortPortfolioError(
            f"source package identity mismatch: {expected_role}"
        )
    declared_self = str(
        (manifest.get("manifest_self_integrity") or {}).get("sha256") or ""
    )
    if declared_self != _canonical_manifest_self_hash(manifest):
        raise FiveSourceShortPortfolioError(
            f"source manifest self-integrity mismatch: {expected_role}"
        )
    _validate_source_manifest(package=package, manifest=manifest, role=expected_role)

    expected_hash = _sha_value(raw.get("video_sha256"), "video SHA-256")
    expected_size = _positive_int(raw.get("video_byte_size"), "video byte size")
    if _sha256(video_path) != expected_hash or video_path.stat().st_size != expected_size:
        raise FiveSourceShortPortfolioError(
            f"source MP4 hash/size mismatch: {expected_role}"
        )
    manifest_row = _manifest_row(manifest, video_relative.as_posix())
    if (
        manifest_row is None
        or manifest_row.get("sha256") != expected_hash
        or int(manifest_row.get("byte_size") or -1) != expected_size
    ):
        raise FiveSourceShortPortfolioError(
            f"source manifest does not bind MP4: {expected_role}"
        )
    video_readback = readback.get("video")
    if (
        not isinstance(video_readback, dict)
        or video_readback.get("package_relative_path") != video_relative.as_posix()
        and video_readback.get("package_relative_path") != str(video_relative)
        or video_readback.get("sha256") != expected_hash
    ):
        raise FiveSourceShortPortfolioError(
            f"source readback does not bind MP4: {expected_role}"
        )
    source_identity = readback.get("source_identity")
    identity_value = ""
    if isinstance(source_identity, dict):
        identity_value = str(source_identity.get("identity") or "")
        if not identity_value:
            platform = str(source_identity.get("platform") or "").strip()
            provider_id = str(source_identity.get("provider_id") or "").strip()
            if platform and provider_id:
                identity_value = f"{platform}:{provider_id}"
    if identity_value != str(raw.get("video_identity") or ""):
        raise FiveSourceShortPortfolioError(
            f"source readback video identity mismatch: {expected_role}"
        )
    duration = _readback_duration(readback)
    title = str(raw.get("title") or "").strip()
    portfolio_slot = str(raw.get("portfolio_slot") or "").strip()
    video_identity = str(raw.get("video_identity") or "").strip()
    episode_identity = str(readback.get("episode_id") or "").strip()
    if not title or not portfolio_slot or not video_identity or not episode_identity:
        raise FiveSourceShortPortfolioError(
            f"candidate label/identity is incomplete: {expected_role}"
        )
    return {
        "role": expected_role,
        "title": title,
        "portfolio_slot": portfolio_slot,
        "video_identity": video_identity,
        "source_artifact_id": source_artifact,
        "source_state": source_state,
        "package_dir": package,
        "readback_path": readback_path,
        "manifest_path": manifest_path,
        "video_path": video_path,
        "video_sha256": expected_hash,
        "video_byte_size": expected_size,
        "duration_seconds": duration,
        "source_manifest_self_sha256": declared_self,
        "readback_sha256": expected_readback_sha,
        "manifest_sha256": expected_manifest_sha,
        "episode_identity": episode_identity,
    }


def _validate_source_manifest(
    *, package: Path, manifest: dict[str, Any], role: str
) -> None:
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise FiveSourceShortPortfolioError(
            f"source manifest has no payload rows: {role}"
        )
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise FiveSourceShortPortfolioError(
                f"source manifest payload row is invalid: {role}"
            )
        relative = _safe_relative_file(
            row.get("package_relative_path"), "source manifest payload"
        )
        name = relative.as_posix()
        if name in seen:
            raise FiveSourceShortPortfolioError(
                f"source manifest payload is duplicated: {role}"
            )
        seen.add(name)
        path = (package / relative).resolve()
        _require_within(path, package, "source manifest payload")
        _require_file(path, f"source manifest payload {name}")
        if (
            _sha256(path) != _sha_value(row.get("sha256"), "payload SHA-256")
            or path.stat().st_size
            != _positive_int(row.get("byte_size"), "payload byte size")
        ):
            raise FiveSourceShortPortfolioError(
                f"source manifest payload hash/size mismatch: {role}/{name}"
            )


def _validate_scorecard_row(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise FiveSourceShortPortfolioError("scorecard row must be an object")
    missing = [key for key in REQUIRED_SCORECARD_COLUMNS if key not in raw]
    if missing:
        raise FiveSourceShortPortfolioError(
            f"scorecard row is missing columns: {', '.join(missing)}"
        )
    if _BANNED_SCORECARD_KEYS.intersection(raw):
        raise FiveSourceShortPortfolioError(
            "scorecard must not declare winner, readiness, or universal policy"
        )
    row = {key: raw[key] for key in REQUIRED_SCORECARD_COLUMNS}
    if not str(row["portfolio_slot"] or "").strip():
        raise FiveSourceShortPortfolioError("scorecard slot is empty")
    _validate_sha_or_list(row["mp4_sha256"])
    if row["production_status"] != "not_accepted":
        raise FiveSourceShortPortfolioError(
            "scorecard production status must remain not_accepted"
        )
    if row["rights_status"] != "pending":
        raise FiveSourceShortPortfolioError(
            "scorecard rights status must remain pending"
        )
    if _positive_or_zero_int(row["render_count"], "render count") < 0:
        raise AssertionError("unreachable")
    if (
        _positive_or_zero_int(
            row["corrective_render_count"], "corrective render count"
        )
        < 0
    ):
        raise AssertionError("unreachable")
    return row


def _build_scorecard(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.out11.five_source_scorecard.v0",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "comparison_scope": "five_distinct_real_sources_internal_evidence_only",
        "columns": list(REQUIRED_SCORECARD_COLUMNS),
        "rows": rows,
        "row_count": 5,
        "review_media_count": 3,
        "winner_selected": False,
        "production_readiness_claimed": False,
        "universal_crop_claimed": False,
        "universal_caption_style_claimed": False,
        "universal_speaker_color_policy_claimed": False,
        "rights_or_publication_acceptance_claimed": False,
        "portfolio_subtitle_differentiation_status": "deferred",
        "portfolio_subtitle_differentiation_revisit_condition": (
            "after_combined_human_review_and_before_production_subtitle_design"
        ),
    }


def _copy_candidate_packages(
    *, stage: Path, candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for item in candidates:
        role = item["role"]
        video_relative = Path("candidates") / f"{role}.mp4"
        readback_relative = Path("evidence") / role / "source_readback.json"
        manifest_relative = Path("evidence") / role / "source_manifest.json"
        (stage / readback_relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item["video_path"], stage / video_relative)
        shutil.copyfile(item["readback_path"], stage / readback_relative)
        shutil.copyfile(item["manifest_path"], stage / manifest_relative)
        if (
            _sha256(stage / video_relative) != item["video_sha256"]
            or (stage / video_relative).stat().st_size != item["video_byte_size"]
        ):
            raise FiveSourceShortPortfolioError(
                f"candidate byte-copy verification failed: {role}"
            )
        copied.append(
            {
                "role": role,
                "title": item["title"],
                "portfolio_slot": item["portfolio_slot"],
                "video_identity": item["video_identity"],
                "source_artifact_id": item["source_artifact_id"],
                "source_state": item["source_state"],
                "duration_seconds": item["duration_seconds"],
                "video": {
                    "package_relative_path": video_relative.as_posix(),
                    "sha256": item["video_sha256"],
                    "byte_size": item["video_byte_size"],
                },
                "source_readback": {
                    "package_relative_path": readback_relative.as_posix(),
                    "sha256": _sha256(stage / readback_relative),
                },
                "source_manifest": {
                    "package_relative_path": manifest_relative.as_posix(),
                    "sha256": _sha256(stage / manifest_relative),
                    "self_sha256": item["source_manifest_self_sha256"],
                },
            }
        )
    return copied


def _render_html(readback: dict[str, Any], scorecard: dict[str, Any]) -> str:
    sections = "".join(_render_candidate_section(item) for item in readback["review_candidates"])
    context_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['portfolio_slot']))}</td>"
        f"<td>{escape(str(row['video_identity']))}</td>"
        f"<td>{escape(str(row['language']))}</td>"
        f"<td>{escape(str(row['selected_duration_seconds']))}</td>"
        f"<td>{escape(str(row['composition_strategy']))}</td>"
        f"<td>{escape(str(row['human_acceptance_status']))}</td>"
        "</tr>"
        for row in scorecard["rows"]
    )
    question = escape(REVIEW_QUESTION)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="clippipegen-artifact-id" content="{ARTIFACT_ID}"><title>OUT-11 five-source Short portfolio</title><style>
:root{{color-scheme:dark;font-family:"Yu Gothic UI","Noto Sans JP",sans-serif;background:#06101d;color:#eff7ff}}*{{box-sizing:border-box}}html,body{{margin:0;max-width:100%;overflow-x:hidden}}main{{width:min(980px,100%);margin:auto;padding:24px;overflow-wrap:anywhere}}section,details{{margin:22px 0;padding:18px;border:1px solid #30445f;border-radius:14px;background:#0d1a2c}}.candidate{{margin-top:38px}}video{{display:block;width:auto;height:min(74vh,810px);max-width:100%;aspect-ratio:9/16;margin:18px auto;background:#000}}code{{color:#9fe7ff;word-break:break-all}}.boundary{{color:#ffd166}}.table-wrap{{max-width:100%;overflow-x:auto}}table{{width:100%;min-width:760px;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #30445f;text-align:left;vertical-align:top}}details:not([open])>*:not(summary){{display:none}}@media(max-width:620px){{main{{padding:14px}}section,details{{padding:14px}}video{{height:min(70vh,690px)}}}}
</style></head><body data-artifact-id="{ARTIFACT_ID}"><main><h1>OUT-11 five-source Short portfolio</h1>
<p>OUT-08/09はaccepted internalの文脈だけを継承し、再視聴・再受理の対象にしません。以下の3本を上から順に確認してください。</p>
<p class="boundary">初期停止・ミュート・currentTime 0 / 自動再生なし / 音量上限25% / rights pending / production・thumbnail・public/publishing未承認</p>
{sections}
<section><h2>今回の一回の確認</h2><p data-review-question="1">{question}</p></section>
<details><summary>5-source scorecard（証拠・負債を表示）</summary><div class="table-wrap"><table><thead><tr><th>slot</th><th>video</th><th>language</th><th>duration</th><th>composition</th><th>human status</th></tr></thead><tbody>{context_rows}</tbody></table></div><p><a href="five_source_scorecard.json">全必須列を含むJSON</a></p></details>
<script>(()=>{{const maximumVolume={INITIAL_VOLUME_CEILING:.2f};const videos=Array.from(document.querySelectorAll("video[data-review-video]"));window.__clipPipeCombinedReview={{videoCount:videos.length,initializationComplete:false,playEvents:[]}};for(const video of videos){{video.defaultMuted=true;video.muted=true;video.pause();try{{video.currentTime=0;}}catch(_error){{}}video.volume=maximumVolume;video.addEventListener("loadedmetadata",()=>{{video.pause();if(video.currentTime!==0)video.currentTime=0;}},{{once:true}});video.addEventListener("volumechange",()=>{{if(video.volume>maximumVolume)video.volume=maximumVolume;}});video.addEventListener("play",()=>{{for(const other of videos){{if(other!==video)other.pause();}}window.__clipPipeCombinedReview.playEvents.push(video.id);}});}}window.__clipPipeCombinedReview.initializationComplete=true;}})();</script>
</main></body></html>"""


def _render_candidate_section(item: dict[str, Any]) -> str:
    role = escape(item["role"])
    video = item["video"]
    readback = item["source_readback"]
    manifest = item["source_manifest"]
    return (
        f'<section class="candidate" data-candidate-role="{role}">'
        f"<h2>{escape(item['portfolio_slot'])} — {escape(item['title'])}</h2>"
        f"<p>{escape(item['video_identity'])} / {item['duration_seconds']:.3f}s</p>"
        f'<p>exact MP4 SHA-256: <code data-video-sha256="{escape(video["sha256"])}">{escape(video["sha256"])}</code></p>'
        f'<video id="video-{role}" data-review-video="{role}" controls playsinline muted preload="metadata" '
        f'src="{escape(video["package_relative_path"])}?v={escape(video["sha256"][:16])}"></video>'
        "<details><summary>この候補の機械証拠</summary>"
        f'<p><a href="{escape(readback["package_relative_path"])}">source readback</a> / '
        f'<a href="{escape(manifest["package_relative_path"])}">source manifest</a></p>'
        f'<p>source artifact <code>{escape(item["source_artifact_id"])}</code> / state <code>{escape(item["source_state"])}</code> / byte size {video["byte_size"]}</p>'
        "</details></section>"
    )


def _review_access_contract(*, output: Path, root: Path) -> dict[str, Any]:
    relative = _relative(output, root).replace("/", "\\")
    return {
        "clean_human_url": f"http://{REVIEW_HOST}:{REVIEW_PORT}/index.html",
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
        "http_range_required_for_all_videos": True,
        "autoplay": False,
        "initial_paused": True,
        "initial_muted": True,
        "initial_current_time_seconds": 0,
        "maximum_volume": INITIAL_VOLUME_CEILING,
        "single_video_playback": True,
        "storage_restore": False,
    }


def _open_script(*, default_port: int = REVIEW_PORT) -> str:
    template = r"""param([switch]$Serve, [int]$Port = __DEFAULT_PORT__)
$ErrorActionPreference = 'Stop'
$serveScript = Join-Path $PSScriptRoot 'serve_preview.ps1'
$url = "http://127.0.0.1:$Port/index.html"
$canonical = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$serveScript`" -Port $Port"

function Get-ReviewProbeExitCode {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $serveScript -Port $Port -ProbeOnly *> $null
    return $LASTEXITCODE
}

$probe = Get-ReviewProbeExitCode
if ($probe -eq 0) { Start-Process -FilePath $url; return }
if ($probe -eq 5) { throw "Port $Port is occupied by an unrecognized process. No process was stopped." }
if (-not $Serve) {
    Write-Host "OUT-11 combined review server is not running."
    Write-Host "Start it in a foreground PowerShell and keep that window open:"
    Write-Host $canonical
    exit 2
}
$serverArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$serveScript`"",'-Port',"$Port")
$serverProcess = Start-Process -FilePath 'powershell.exe' -ArgumentList $serverArgs -PassThru
$deadline = [DateTime]::UtcNow.AddSeconds(20)
do {
    Start-Sleep -Milliseconds 400
    $serverProcess.Refresh()
    if ($serverProcess.HasExited) { throw "The foreground review server exited before becoming healthy." }
    $probe = Get-ReviewProbeExitCode
    if ($probe -eq 0) {
        Start-Process -FilePath $url
        Write-Host "Combined review opened at $url"
        Write-Host "Keep the foreground server PowerShell window open; use Ctrl+C to stop it."
        return
    }
} while ([DateTime]::UtcNow -lt $deadline)
throw "The foreground review server did not pass its identity and three-video Range gate."
"""
    return template.replace("__DEFAULT_PORT__", str(default_port))


def _serve_script(
    *, candidates: list[dict[str, Any]], default_port: int = REVIEW_PORT
) -> str:
    if len(candidates) != 3:
        raise FiveSourceShortPortfolioError(
            "server helper requires exactly three candidates"
        )
    expected_rows = "\n".join(
        "    @{ Name = '"
        + item["video"]["package_relative_path"]
        + "'; Sha256 = '"
        + item["video"]["sha256"]
        + "'; ByteSize = "
        + str(item["video"]["byte_size"])
        + " }"
        for item in candidates
    )
    template = r"""param([int]$Port = __DEFAULT_PORT__, [switch]$ProbeOnly)
$ErrorActionPreference = 'Stop'
$expectedArtifact = '__ARTIFACT_ID__'
$expectedVideos = @(
__EXPECTED_VIDEOS__
)
$url = "http://127.0.0.1:$Port/index.html"

function Confirm-ReviewPackage {
    $root = (Resolve-Path -LiteralPath $PSScriptRoot).Path
    $indexPath = Join-Path $root 'index.html'
    $manifestPath = Join-Path $root 'review_manifest.json'
    foreach ($path in @($indexPath, $manifestPath)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required review file is missing: $path" }
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.artifact_id -ne $expectedArtifact) { throw "Review manifest artifact identity mismatch." }
    if (@($manifest.candidate_videos).Count -ne 3) { throw "Review manifest must bind exactly three videos." }
    $index = Get-Content -LiteralPath $indexPath -Raw
    if (-not $index.Contains($expectedArtifact)) { throw "Review index artifact identity mismatch." }
    foreach ($expected in $expectedVideos) {
        $videoPath = Join-Path $root $expected.Name
        if (-not (Test-Path -LiteralPath $videoPath -PathType Leaf)) { throw "Required candidate video is missing: $videoPath" }
        $actual = Get-Item -LiteralPath $videoPath
        $actualSha = (Get-FileHash -LiteralPath $videoPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualSha -ne $expected.Sha256 -or $actual.Length -ne $expected.ByteSize) { throw "Current MP4 SHA-256/size mismatch. Media serving was refused: $($expected.Name)" }
        $manifestRow = @($manifest.candidate_videos | Where-Object { $_.package_relative_path -eq $expected.Name -and $_.sha256 -eq $expected.Sha256 -and $_.byte_size -eq $expected.ByteSize })
        if ($manifestRow.Count -ne 1) { throw "Review manifest video binding mismatch: $($expected.Name)" }
        if (-not $index.Contains($expected.Sha256)) { throw "Review index video identity mismatch: $($expected.Name)" }
    }
    return [pscustomobject]@{ Root = $root; Videos = $expectedVideos }
}

function Test-PortListener {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $connect = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne(400)) { return $false }
        $client.EndConnect($connect); return $true
    } catch { return $false } finally { $client.Dispose() }
}

function Test-ReviewServerIdentity($Videos) {
    try {
        $page = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        if ([int]$page.StatusCode -ne 200 -or -not $page.Content.Contains($expectedArtifact)) { return $false }
        foreach ($video in $Videos) {
            if (-not $page.Content.Contains($video.Sha256)) { return $false }
            $rangeEnd = [Math]::Min(1023, [long]$video.ByteSize - 1)
            $expectedLength = $rangeEnd + 1
            $request = [System.Net.HttpWebRequest]::Create("http://127.0.0.1:$Port/$($video.Name)")
            $request.Method = 'GET'; $request.Timeout = 3000; $request.AddRange(0, $rangeEnd)
            $range = [System.Net.HttpWebResponse]$request.GetResponse()
            try {
                if ([int]$range.StatusCode -ne 206) { return $false }
                if ($range.Headers['Content-Range'] -ne "bytes 0-$rangeEnd/$($video.ByteSize)") { return $false }
                if ([long]$range.ContentLength -ne $expectedLength) { return $false }
            } finally { $range.Close() }
        }
        return $true
    } catch { return $false }
}

$package = Confirm-ReviewPackage
$hasListener = Test-PortListener
if ($ProbeOnly) {
    if (-not $hasListener) { exit 4 }
    if (Test-ReviewServerIdentity -Videos $package.Videos) { exit 0 }
    exit 5
}
if ($hasListener) {
    if (Test-ReviewServerIdentity -Videos $package.Videos) {
        Write-Host "Verified existing OUT-11 combined review server at $url"
        Write-Host "Its owning foreground PowerShell remains responsible for server lifetime."
        exit 0
    }
    throw "Port $Port is occupied by an unrecognized process. No process was stopped and no alternate port was selected."
}
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
Write-Host "OUT-11 combined review URL: $url"
Write-Host "Keep this PowerShell window open during review. Press Ctrl+C to stop the server."
Push-Location -LiteralPath $repoRoot
try {
    & uvx python -m src.cli.serve_review --root $package.Root --port $Port
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
"""
    return (
        template.replace("__DEFAULT_PORT__", str(default_port))
        .replace("__ARTIFACT_ID__", ARTIFACT_ID)
        .replace("__EXPECTED_VIDEOS__", expected_rows)
    )


def _validate_staged_package(
    *, stage: Path, readback: dict[str, Any], manifest: dict[str, Any]
) -> None:
    required = (
        "index.html",
        "open_preview.ps1",
        "serve_preview.ps1",
        "review_readback.json",
        "review_manifest.json",
        "five_source_scorecard.json",
        "candidates/out10.mp4",
        "candidates/source04.mp4",
        "candidates/source05.mp4",
        "evidence/out10/source_readback.json",
        "evidence/out10/source_manifest.json",
        "evidence/source04/source_readback.json",
        "evidence/source04/source_manifest.json",
        "evidence/source05/source_readback.json",
        "evidence/source05/source_manifest.json",
    )
    for name in required:
        _require_file(stage / name, f"staged package file {name}")
    if _read_json(stage / "review_readback.json", "staged readback") != readback:
        raise FiveSourceShortPortfolioError("staged readback parse mismatch")
    parsed_manifest = _read_json(stage / "review_manifest.json", "staged manifest")
    if parsed_manifest != manifest:
        raise FiveSourceShortPortfolioError("staged manifest parse mismatch")
    if (
        (parsed_manifest.get("manifest_self_integrity") or {}).get("sha256")
        != _canonical_manifest_self_hash(parsed_manifest)
    ):
        raise FiveSourceShortPortfolioError("review manifest self-integrity mismatch")
    payload_names: set[str] = set()
    for row in parsed_manifest.get("files") or []:
        relative = _safe_relative_file(
            row.get("package_relative_path"), "review manifest payload"
        )
        name = relative.as_posix()
        if name in payload_names:
            raise FiveSourceShortPortfolioError("review manifest payload duplicated")
        payload_names.add(name)
        path = stage / relative
        _require_file(path, f"review manifest payload {name}")
        if (
            _sha256(path) != row.get("sha256")
            or path.stat().st_size != int(row.get("byte_size") or -1)
        ):
            raise FiveSourceShortPortfolioError(
                f"review manifest payload hash/size mismatch: {name}"
            )
    expected_payloads = {
        path.relative_to(stage).as_posix()
        for path in stage.rglob("*")
        if path.is_file() and path.name != "review_manifest.json"
    }
    if payload_names != expected_payloads:
        raise FiveSourceShortPortfolioError("review manifest coverage is incomplete")
    html = (stage / "index.html").read_text(encoding="utf-8")
    if html.count("<video ") != 3 or html.count("data-review-question=") != 1:
        raise FiveSourceShortPortfolioError("review page must have three videos and one question")
    if (
        re.search(r"\bautoplay\b", html, flags=re.IGNORECASE)
        or "localStorage" in html
        or "sessionStorage" in html
    ):
        raise FiveSourceShortPortfolioError("review page violates playback safety")
    if html.count("data-review-video=") != 3 or "other.pause()" not in html:
        raise FiveSourceShortPortfolioError("single-video playback control is incomplete")
    server = (stage / "serve_preview.ps1").read_text(encoding="utf-8")
    if server.count("@{ Name = 'candidates/") != 3:
        raise FiveSourceShortPortfolioError("server does not bind all three videos")
    if "Stop-Process" in server or "taskkill" in server.lower():
        raise FiveSourceShortPortfolioError("server must not kill a port owner")


def _manifest_file_rows(stage: Path) -> list[dict[str, Any]]:
    return [
        {
            "package_relative_path": path.relative_to(stage).as_posix(),
            "sha256": _sha256(path),
            "byte_size": path.stat().st_size,
        }
        for path in sorted(item for item in stage.rglob("*") if item.is_file())
    ]


def _manifest_row(manifest: dict[str, Any], name: str) -> dict[str, Any] | None:
    rows = [
        row
        for row in manifest.get("files") or []
        if isinstance(row, dict) and row.get("package_relative_path") == name
    ]
    return rows[0] if len(rows) == 1 else None


def _readback_duration(readback: dict[str, Any]) -> float:
    candidate = readback.get("candidate")
    if isinstance(candidate, dict) and candidate.get("duration_seconds") is not None:
        return _number(candidate["duration_seconds"], "candidate duration")
    render = readback.get("render")
    media = render.get("media") if isinstance(render, dict) else None
    if isinstance(media, dict) and media.get("duration_seconds") is not None:
        return _number(media["duration_seconds"], "render duration")
    raise FiveSourceShortPortfolioError("source readback duration is missing")


def _canonical_manifest_self_hash(manifest: dict[str, Any]) -> str:
    clone = json.loads(json.dumps(manifest))
    integrity = clone.get("manifest_self_integrity")
    if not isinstance(integrity, dict):
        raise FiveSourceShortPortfolioError("manifest self-integrity block is missing")
    integrity["sha256"] = None
    return hashlib.sha256(
        json.dumps(clone, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _payload_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _atomic_promote(*, stage: Path, output: Path) -> Path | None:
    if stage.parent != output.parent or not stage.name.startswith(
        f".{output.name}.staging-"
    ):
        raise FiveSourceShortPortfolioError("invalid OUT-11 staging directory")
    backup: Path | None = None
    if output.exists():
        backup = output.parent / f".{output.name}.backup-{uuid.uuid4().hex}"
        output.replace(backup)
    try:
        stage.replace(output)
    except Exception:
        if backup is not None and backup.exists() and not output.exists():
            backup.replace(output)
        raise
    return backup


def _remove_owned_tree(*, stage: Path, expected_parent: Path) -> None:
    resolved = stage.resolve()
    if resolved.parent != expected_parent.resolve() or not (
        resolved.name.startswith(".")
        and (".staging-" in resolved.name or ".backup-" in resolved.name)
    ):
        raise FiveSourceShortPortfolioError("refused to remove an unowned tree")
    shutil.rmtree(resolved)


def _safe_relative_file(value: Any, label: str) -> Path:
    raw = str(value or "")
    path = Path(raw)
    if (
        not raw
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise FiveSourceShortPortfolioError(f"unsafe {label} path: {raw!r}")
    return path


def _validate_sha_or_list(value: Any) -> None:
    values = value if isinstance(value, list) else [value]
    if not values or any(SHA256.fullmatch(str(item or "")) is None for item in values):
        raise FiveSourceShortPortfolioError("scorecard MP4 SHA-256 is invalid")


def _sha_value(value: Any, label: str) -> str:
    text = str(value or "")
    if SHA256.fullmatch(text) is None:
        raise FiveSourceShortPortfolioError(f"{label} is invalid")
    return text


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise FiveSourceShortPortfolioError(f"{label} must be a positive integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise FiveSourceShortPortfolioError(
            f"{label} must be a positive integer"
        ) from exc
    if number <= 0:
        raise FiveSourceShortPortfolioError(f"{label} must be a positive integer")
    return number


def _positive_or_zero_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise FiveSourceShortPortfolioError(f"{label} must be a non-negative integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise FiveSourceShortPortfolioError(
            f"{label} must be a non-negative integer"
        ) from exc
    if number < 0:
        raise FiveSourceShortPortfolioError(f"{label} must be a non-negative integer")
    return number


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise FiveSourceShortPortfolioError(f"{label} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise FiveSourceShortPortfolioError(f"{label} must be numeric") from exc


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FiveSourceShortPortfolioError(f"invalid {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise FiveSourceShortPortfolioError(f"{label} must be a JSON object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FiveSourceShortPortfolioError(f"{label} not found: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise FiveSourceShortPortfolioError(f"{label} not found: {path}")


def _require_within(path: Path, parent: Path, label: str) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise FiveSourceShortPortfolioError(f"{label} escapes allowed root") from exc


def _safe_identifier(value: str, label: str) -> None:
    if not value or SAFE_ID.fullmatch(value) is None:
        raise FiveSourceShortPortfolioError(f"unsafe {label}: {value!r}")
