"""OUT-07 internal operator delivery pack.

This slice packages the already accepted OUT-06 video without re-rendering and
retains the former source-frame-derived thumbnails as user-rejected evidence
beside a closed-gate Japanese metadata draft.  It is an internal operator
handoff surface only; it performs no
upload, public/publishing action, rights approval, thumbnail upload, visibility
choice, or made-for-kids decision.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import uuid
from html import escape
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny
from src.integrations.render.vertical_short_candidate import (
    _atomic_promote,
    _cleanup_internal_directory,
    _relative,
    _sha256,
    _tree_digest,
    _write_text,
)


ARTIFACT_ID = "clip-out07-internal-operator-delivery-pack-v0-001"
SCHEMA_VERSION = "clippipegen.out07.operator_delivery_pack.v0"
STATE = "internal_operator_delivery_pack_review_ready"
EXPECTED_OUT06_ARTIFACT_ID = "clip-out06-complete-narrative-short-delivery-candidate-v0-001"
EXPECTED_OUT06_VIDEO_SHA256 = (
    "02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0"
)
SOURCE_VIDEO_RELATIVE = (
    "episodes/jp_pilot01_hololive_bancho_20260525/"
    "materials/src_video_jp_pilot01/source_video.mp4"
)
SOURCE_VIDEO_SHA256 = (
    "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
)
DEFAULT_PORT = 8070
OUTPUT_NAME_PREFIX = "out07_"


class OperatorDeliveryPackError(Exception):
    """Raised when OUT-07 cannot be built without scope or evidence drift."""


THUMBNAIL_DIRECTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "context",
        "label": "context",
        "source_cut_id": "cut_001",
        "source_seconds": 7.70,
        "source_subtitle_ids": ["sub_006"],
        "supporting_segment_ids": ["seg_000006"],
        "visible_text": ["体育館裏で", "待ってます！！"],
        "short_caption": "呼び出し",
        "selection_role": "setup_context",
        "rationale": "呼び出しの発端を伝えるが、対立の引きは tension より弱い。",
        "decision_status": "user_rejected",
        "rejection_reason": "後ろ向きの人物が主役で、Shorts posterとして視線が成立しない。",
    },
    {
        "id": "tension",
        "label": "tension",
        "source_cut_id": "cut_003",
        "source_seconds": 25.35,
        "source_subtitle_ids": ["sub_013", "sub_014"],
        "supporting_segment_ids": ["seg_000013", "seg_000014"],
        "visible_text": ["なんで", "来なかった！？"],
        "short_caption": "来なかった理由",
        "selection_role": "rejected_legacy_conflict_hook",
        "rationale": "呼び出したのに来ない主摩擦を示す旧案だが、ユーザー不採用のため候補外。",
        "decision_status": "user_rejected",
        "rejection_reason": "場面スクリーンショットへ文字を載せた構成で、参照構図の再構成になっていない。",
    },
    {
        "id": "payoff",
        "label": "payoff",
        "source_cut_id": "cut_003",
        "source_seconds": 37.05,
        "source_subtitle_ids": ["sub_022", "sub_028"],
        "supporting_segment_ids": ["seg_000022", "seg_000028"],
        "visible_text": ["団長", "倒したど～！！"],
        "short_caption": "結果",
        "selection_role": "payoff_spoiler",
        "rationale": "結果の勢いは強いが、視聴前に結末を出しすぎるため推奨から外す。",
        "decision_status": "user_rejected",
        "rejection_reason": "場面スクリーンショットへ文字を載せた構成で、小さい補助文字も残る。",
    },
)

EPISODE_COPY_PLAN: dict[str, Any] = {
    "title": "番長、団長を呼び出すも来ない！？",
    "description_lines": [
        "番長のはじめが団長を体育館裏へ呼び出し、「倒してやる！！」と意気込みます。",
        "ところが団長は来ず、待ち続けたはじめが「なんで来なかったんすか！！」と問いかけます。",
        "最後は“はじめの勝ち”で決着し、次の番長を探し始めます。",
    ],
    "tags": ["ホロライブ", "はじめ", "番長", "団長", "体育館裏", "呼び出し", "来なかった理由"],
    "evidence_trace": [
        {
            "claim": "はじめが団長を体育館裏へ呼び出す",
            "source_cut_ids": ["cut_001", "cut_002"],
            "subtitle_ids": ["sub_002", "sub_004", "sub_006", "sub_008", "sub_009"],
            "source_segment_ids": [
                "seg_000002",
                "seg_000004",
                "seg_000006",
                "seg_000008",
                "seg_000009",
            ],
        },
        {
            "claim": "団長が呼び出し場所に来ず、はじめが理由を問いかける",
            "source_cut_ids": ["cut_003"],
            "subtitle_ids": ["sub_010", "sub_013", "sub_014"],
            "source_segment_ids": ["seg_000010", "seg_000013", "seg_000014"],
        },
        {
            "claim": "はじめの勝ちとして決着する",
            "source_cut_ids": ["cut_003"],
            "subtitle_ids": ["sub_019", "sub_020", "sub_021", "sub_022"],
            "source_segment_ids": [
                "seg_000019",
                "seg_000020",
                "seg_000021",
                "seg_000022",
            ],
        },
        {
            "claim": "はじめが次の番長を探し始める",
            "source_cut_ids": ["cut_003"],
            "subtitle_ids": ["sub_024", "sub_026", "sub_027", "sub_028"],
            "source_segment_ids": [
                "seg_000024",
                "seg_000026",
                "seg_000027",
                "seg_000028",
            ],
        },
    ],
}


def build_operator_delivery_pack(
    *,
    episode_dir: str | Path,
    output_dir: str | Path,
    out06_readback_path: str | Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    runner: ffmpeg_tiny.Runner = subprocess.run,
) -> dict[str, Any]:
    root = Path(base_dir or Path.cwd()).resolve()
    episode = _resolved(root, Path(episode_dir))
    output = _resolved(root, Path(output_dir))
    out06_readback = _resolved(root, Path(out06_readback_path))
    _require_directory(episode, "episode directory")
    _validate_output_directory(episode, output)
    _require_file(out06_readback, "OUT-06 readback")

    authority = _load_authority(root=root, episode=episode, out06_readback=out06_readback)
    for input_path in authority["input_paths"]:
        _reject_overlap(output, input_path, "OUT-07 output must not overlap an input")
    protected_paths = _protected_paths(episode)
    for protected_path in protected_paths.values():
        _reject_overlap(output, protected_path, "OUT-07 output must not overlap protected evidence")
    protected_before = {
        label: _tree_digest(path, root=root) for label, path in protected_paths.items()
    }
    input_hashes_before = {
        _relative(path, root): _sha256(path) for path in authority["input_paths"]
    }

    review_dir = episode / "review"
    stage = review_dir / f".{output.name}.staging-{uuid.uuid4().hex}"
    backup: Path | None = None
    try:
        stage.mkdir(parents=False, exist_ok=False)
        assets = stage / "assets"
        assets.mkdir()
        work = stage / ".work"
        work.mkdir()

        video_path = assets / "complete_narrative_short.mp4"
        shutil.copyfile(authority["out06_video_path"], video_path)
        if _sha256(video_path) != EXPECTED_OUT06_VIDEO_SHA256:
            raise OperatorDeliveryPackError("packaged OUT-06 video hash changed")

        thumbnail_records = _build_thumbnails(
            root=root,
            stage=stage,
            output=output,
            assets=assets,
            work=work,
            source_video_path=authority["source_video_path"],
            source_video_sha256=authority["source_video_sha256"],
            ffmpeg_path=ffmpeg_path,
            runner=runner,
        )
        final_paths = {
            "video": output / "assets" / "complete_narrative_short.mp4",
            "thumbnail_context": output / "assets" / "thumbnail_context_1280x720.jpg",
            "thumbnail_tension": output / "assets" / "thumbnail_tension_1280x720.jpg",
            "thumbnail_payoff": output / "assets" / "thumbnail_payoff_1280x720.jpg",
            "thumbnail_contact_sheet": output / "assets" / "thumbnail_direction_contact_sheet.jpg",
            "thumbnail_plan": output / "thumbnail_plan.json",
            "publish_draft": output / "publish_draft.json",
            "readback": output / "operator_delivery_readback.json",
            "manifest": output / "delivery_manifest.json",
            "index": output / "index.html",
            "open": output / "open_delivery.ps1",
            "serve": output / "serve_delivery.ps1",
        }
        publish_draft = _publish_draft(
            root=root,
            episode=episode,
            authority=authority,
            thumbnails=thumbnail_records,
            final_paths=final_paths,
        )
        thumbnail_plan = _thumbnail_plan(thumbnail_records)
        _write_json(stage / "thumbnail_plan.json", thumbnail_plan)
        _write_json(stage / "publish_draft.json", publish_draft)
        readback = _operator_readback(
            root=root,
            episode=episode,
            output=output,
            authority=authority,
            protected=protected_before,
            input_hashes=input_hashes_before,
            thumbnails=thumbnail_records,
            publish_draft=publish_draft,
            final_paths=final_paths,
        )
        _write_json(stage / "operator_delivery_readback.json", readback)
        _write_text(stage / "index.html", _render_html(readback, publish_draft, thumbnail_records))
        _write_text(stage / "open_delivery.ps1", _open_script())
        _write_text(stage / "serve_delivery.ps1", _serve_script())
        _cleanup_internal_directory(work, expected_parent=stage)
        manifest = _delivery_manifest(stage=stage, output=output, readback=readback)
        _write_json(stage / "delivery_manifest.json", manifest)
        _validate_bundle(stage)

        protected_after = {
            label: _tree_digest(path, root=root) for label, path in protected_paths.items()
        }
        if protected_after != protected_before:
            raise OperatorDeliveryPackError("protected evidence changed during OUT-07 build")
        input_hashes_after = {
            _relative(path, root): _sha256(path) for path in authority["input_paths"]
        }
        if input_hashes_after != input_hashes_before:
            raise OperatorDeliveryPackError("authority input changed during OUT-07 build")
        try:
            backup = _atomic_promote(stage, output)
        except PermissionError as exc:
            raise OperatorDeliveryPackError(
                "OUT-07 output is in use; stop the retained delivery server and rerun"
            ) from exc
    except Exception:
        if stage.exists():
            _cleanup_internal_directory(stage, expected_parent=review_dir)
        raise
    finally:
        if backup is not None and backup.exists():
            _cleanup_internal_directory(backup, expected_parent=review_dir)

    final_readback = _read_json(output / "operator_delivery_readback.json", "OUT-07 readback")
    return {
        "artifact_id": ARTIFACT_ID,
        "output_dir": output,
        "readback_path": output / "operator_delivery_readback.json",
        "manifest_path": output / "delivery_manifest.json",
        "index_path": output / "index.html",
        "readback": final_readback,
    }


def _build_thumbnails(
    *,
    root: Path,
    stage: Path,
    output: Path,
    assets: Path,
    work: Path,
    source_video_path: Path,
    source_video_sha256: str,
    ffmpeg_path: str | Path | None,
    runner: ffmpeg_tiny.Runner,
) -> list[dict[str, Any]]:
    from PIL import Image, ImageDraw, ImageFont

    font_path = _font_path()
    font_big = ImageFont.truetype(str(font_path), 88)
    font_small = ImageFont.truetype(str(font_path), 30)
    records: list[dict[str, Any]] = []
    for direction in THUMBNAIL_DIRECTIONS:
        frame_path = work / f"{direction['id']}_source_frame.png"
        _extract_source_frame(
            source_video_path=source_video_path,
            seconds=float(direction["source_seconds"]),
            frame_path=frame_path,
            ffmpeg_path=ffmpeg_path,
            runner=runner,
        )
        image = Image.open(frame_path).convert("RGB")
        image = _fit_1280x720(image)
        extracted_frame_hash = hashlib.sha256(image.tobytes()).hexdigest()
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rectangle((0, 0, 1280, 720), fill=(0, 0, 0, 54))
        draw.rounded_rectangle((54, 416, 1010, 666), radius=28, fill=(0, 0, 0, 168))
        y = 432
        for line in direction["visible_text"]:
            _draw_text_with_outline(draw, (82, y), line, font_big)
            y += 92
        draw.text((84, 626), str(direction["short_caption"]), font=font_small, fill=(255, 233, 95, 255))
        file_name = f"thumbnail_{direction['id']}_1280x720.jpg"
        out = assets / file_name
        image.save(out, format="JPEG", quality=92, subsampling=0, optimize=False, progressive=False)
        if image.size != (1280, 720) or image.mode != "RGB":
            raise OperatorDeliveryPackError("thumbnail dimensions or mode invalid")
        records.append(
            {
                "direction_id": direction["id"],
                "label": direction["label"],
                "path": _relative(output / "assets" / file_name, root),
                "source_cut_id": direction["source_cut_id"],
                "source_seconds": direction["source_seconds"],
                "source_subtitle_ids": direction["source_subtitle_ids"],
                "supporting_segment_ids": direction["supporting_segment_ids"],
                "visible_text": direction["visible_text"],
                "selection_role": direction["selection_role"],
                "rationale": direction["rationale"],
                "decision_status": direction["decision_status"],
                "rejection_reason": direction["rejection_reason"],
                "font": f"{font_path.name} (local system font)",
                "layout": "source_frame_fit_1280x720_left_lower_high_contrast_text",
                "source_video_sha256": source_video_sha256,
                "extracted_frame_sha256": extracted_frame_hash,
                "sha256": _sha256(out),
                "width": 1280,
                "height": 720,
                "mode": "RGB",
                "format": "JPEG",
            }
        )
    contact_sheet = assets / "thumbnail_direction_contact_sheet.jpg"
    _write_contact_sheet(records, contact_sheet)
    for record in records:
        record["contact_sheet_path"] = _relative(
            output / "assets" / "thumbnail_direction_contact_sheet.jpg", root
        )
        record["contact_sheet_sha256"] = _sha256(contact_sheet)
    return records


def _write_contact_sheet(records: list[dict[str, Any]], out: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(str(_font_path()), 22)
    thumb_w, thumb_h = 320, 180
    canvas = Image.new("RGB", (thumb_w * 3, 260), (18, 18, 18))
    draw = ImageDraw.Draw(canvas)
    for index, record in enumerate(records):
        image = Image.open(out.parent / f"thumbnail_{record['direction_id']}_1280x720.jpg").convert("RGB")
        small = image.resize((thumb_w, thumb_h))
        x = index * thumb_w
        canvas.paste(small, (x, 0))
        label = f"{record['label']} / user rejected"
        draw.text((x + 10, 194), label, font=font, fill=(255, 255, 255))
        draw.text((x + 10, 224), "320x180 check", font=font, fill=(210, 210, 210))
    canvas.save(out, format="JPEG", quality=92, subsampling=0, optimize=False, progressive=False)


def _publish_draft(
    *,
    root: Path,
    episode: Path,
    authority: dict[str, Any],
    thumbnails: list[dict[str, Any]],
    final_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.out07.publish_draft.v0",
        "artifact_id": ARTIFACT_ID,
        "episode_id": episode.name,
        "status": "internal_operator_draft",
        "language": "ja",
        "title": EPISODE_COPY_PLAN["title"],
        "description": "\n".join(EPISODE_COPY_PLAN["description_lines"]),
        "tags": EPISODE_COPY_PLAN["tags"],
        "evidence_trace": EPISODE_COPY_PLAN["evidence_trace"],
        "video": {
            "path": _relative(final_paths["video"], root),
            "sha256": authority["out06_video_sha256"],
        },
        "selected_thumbnail": None,
        "poster_decision_status": "human_selection_required",
        "rejected_thumbnail_ids": [item["direction_id"] for item in thumbnails],
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


def _thumbnail_plan(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.out07.thumbnail_plan.v0",
        "status": "user_rejected_evidence",
        "direction_count": len(records),
        "selected_direction_id": None,
        "recommended_direction_id": None,
        "recommendation_reason": None,
        "successor_artifact_id": "clip-out07-shorts-poster-frame-direction-proof-v0-001",
        "directions": records,
        "constraints": {
            "ai_imagery": False,
            "external_downloads": False,
            "unverified_logos": False,
            "arrows_or_circles": False,
            "source_frame_derived": True,
            "output_width": 1280,
            "output_height": 720,
            "mode": "RGB",
        },
    }


def _operator_readback(
    *,
    root: Path,
    episode: Path,
    output: Path,
    authority: dict[str, Any],
    protected: dict[str, Any],
    input_hashes: dict[str, str],
    thumbnails: list[dict[str, Any]],
    publish_draft: dict[str, Any],
    final_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "episode_id": episode.name,
        "source_class": "accepted_out06_video_plus_verified_source_frames",
        "review_entrypoint": _relative(final_paths["index"], root),
        "operator_delivery_readback": _relative(final_paths["readback"], root),
        "delivery_manifest": _relative(final_paths["manifest"], root),
        "open_command": _powershell_command(final_paths["open"], root),
        "serve_command": _powershell_command(final_paths["serve"], root),
        "default_port": DEFAULT_PORT,
        "video": {
            "source_path": _relative(authority["out06_video_path"], root),
            "packaged_path": _relative(final_paths["video"], root),
            "source_sha256": authority["out06_video_sha256"],
            "packaged_sha256": EXPECTED_OUT06_VIDEO_SHA256,
            "byte_identical_copy": True,
            "rerendered": False,
            "remuxed": False,
            "transcoded": False,
        },
        "thumbnail": {
            "direction_count": len(thumbnails),
            "decision_status": "user_rejected",
            "selected_direction_id": None,
            "recommended_direction_id": None,
            "recommended": None,
            "directions": thumbnails,
            "contact_sheet": {
                "path": _relative(final_paths["thumbnail_contact_sheet"], root),
                "sha256": thumbnails[0]["contact_sheet_sha256"],
                "reduced_size_legibility": "inspected_320x180_contact_sheet",
            },
        },
        "metadata": publish_draft,
        "gates": {
            "internal_operator_draft": True,
            "operator_copy_ready": True,
            "publish_ready": False,
            "source_attribution_status": "operator_decision_required",
            "production_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "public_or_publishing_acceptance": False,
            "rights_status": "pending",
            "upload_attempted": False,
            "thumbnail_upload_attempted": False,
            "metadata_update_attempted": False,
            "visibility_update_attempted": False,
            "visibility": "operator_decision_required",
            "made_for_kids": "operator_decision_required",
            "scheduled_at": None,
        },
        "protected_evidence": protected,
        "input_hashes": input_hashes,
        "regeneration_command": (
            "uvx --with Pillow python -m src.cli.main build-operator-delivery-pack "
            f"--episode-dir {_relative(episode, root)} --output-dir {_relative(output, root)} "
            f"--out06-readback {_relative(authority['out06_readback_path'], root)} --format json"
        ),
        "storage": {
            "class": "ignored_local_retained_same_machine",
            "episodes_tracked": False,
            "portable_across_clones": False,
        },
    }


def _delivery_manifest(*, stage: Path, output: Path, readback: dict[str, Any]) -> dict[str, Any]:
    files = []
    for path in sorted(p for p in stage.rglob("*") if p.is_file() and p.name != "delivery_manifest.json"):
        files.append(
            {
                "package_relative_path": path.relative_to(stage).as_posix(),
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest: dict[str, Any] = {
        "schema_version": "clippipegen.delivery_manifest.v1",
        "artifact_id": ARTIFACT_ID,
        "state": STATE,
        "output_dir_name": output.name,
        "files": files,
        "closed_gates": readback["gates"],
    }
    manifest["manifest_self_integrity"] = {"sha256": _canonical_manifest_self_hash(manifest)}
    return manifest


def _canonical_manifest_self_hash(manifest: dict[str, Any]) -> str:
    canonical = json.loads(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    canonical.pop("manifest_self_integrity", None)
    data = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _render_html(readback: dict[str, Any], publish: dict[str, Any], thumbnails: list[dict[str, Any]]) -> str:
    video_path = "assets/complete_narrative_short.mp4"
    title = publish["title"]
    description = publish["description"]
    tags = ", ".join(publish["tags"])
    thumb_rows = "\n".join(
        f"<tr><td>{escape(t['label'])}</td><td>{escape(t['source_cut_id'])}</td><td>{escape(', '.join(t['source_subtitle_ids']))}</td><td><code>{escape(t['sha256'])}</code></td><td>{escape(t['rationale'])}</td></tr>"
        for t in thumbnails
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OUT-07 オペレーター納品パック</title>
<style>
body{{margin:0;background:#101114;color:#f5f5f5;font-family:system-ui,'Yu Gothic',sans-serif;}}
main{{max-width:1080px;margin:0 auto;padding:24px;}}
.spine{{display:flex;flex-direction:column;gap:24px;}}
section{{background:#181a20;border:1px solid #30333d;border-radius:18px;padding:20px;}}
img,video{{max-width:100%;height:auto;border-radius:14px;background:#000;}}
video{{width:380px;max-height:70vh;}}
textarea{{width:100%;min-height:92px;background:#0d0e12;color:#fff;border:1px solid #444;border-radius:10px;padding:10px;}}
button{{background:#ffd84d;color:#111;border:0;border-radius:999px;padding:8px 14px;font-weight:700;cursor:pointer;}}
.badge{{display:inline-block;background:#302b12;color:#ffe887;border:1px solid #665a25;border-radius:999px;padding:4px 10px;margin:2px;}}
.copyrow{{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:start;}}
table{{width:100%;border-collapse:collapse;font-size:14px}}td,th{{border-top:1px solid #333;padding:8px;text-align:left;vertical-align:top}}
details{{border-top:1px solid #333;padding-top:12px}}code{{overflow-wrap:anywhere}}
</style></head><body><main class="spine">
<section id="rejected-thumbnail-evidence"><p class="badge">OUT-07 旧16:9案</p>
<h1>オペレーター納品パック</h1><h2>3案はユーザー不採用</h2>
<img id="rejected-thumbnail-sheet" src="assets/thumbnail_direction_contact_sheet.jpg" alt="不採用になった旧16:9サムネイル3案">
<p>context／tension／payoffはいずれも選択・推奨対象から除外済みです。次の判断対象は別artifactの9:16 Shorts poster方向proofです。</p></section>
<section id="copy-metadata"><h2>コピー用メタデータ</h2>
<label for="copy-title">タイトル</label><div class="copyrow"><textarea id="copy-title" readonly>{escape(title)}</textarea><button data-copy-target="copy-title" data-copy-label="タイトル">コピー</button></div>
<label for="copy-description">説明文</label><div class="copyrow"><textarea id="copy-description" readonly>{escape(description)}</textarea><button data-copy-target="copy-description" data-copy-label="説明文">コピー</button></div>
<label for="copy-tags">タグ</label><div class="copyrow"><textarea id="copy-tags" readonly>{escape(tags)}</textarea><button data-copy-target="copy-tags" data-copy-label="タグ">コピー</button></div>
<p id="copy-status" role="status">タイトル・説明文・タグを個別にコピーできます。</p></section>
<section id="accepted-video"><h2>採用済みOUT-06動画</h2><video id="delivery-video" controls preload="metadata" src="{video_path}"></video>
<p>OUT-06で採用済みの動画を、バイト列を変えずに収録しています。</p></section>
<section id="operator-status"><h2>オペレーター向け状態</h2>
<p><span class="badge">内部ドラフト</span><span class="badge">コピー項目は技術的に準備済み</span><span class="badge">公開準備は未完了</span><span class="badge">権利確認待ち</span></p>
<p>出典表記はオペレーター判断待ちです。制作採用・公開・アップロード・サムネイル設定・公開範囲・子ども向け設定はいずれも未承認または未実施です。</p>
<p>poster選択、title／description／tagsの採用、公開可否はいずれも未判断です。</p></section>
<section><details><summary>比較・来歴・manifest</summary>
<table><tr><th>方向</th><th>cut</th><th>字幕ID</th><th>sha256</th><th>選定理由</th></tr>{thumb_rows}</table>
<p><img src="assets/thumbnail_direction_contact_sheet.jpg" alt="サムネイル比較シート"></p>
<p>動画SHA-256: <code>{escape(readback['video']['packaged_sha256'])}</code></p>
<p>Manifest: <code>delivery_manifest.json</code> / Readback: <code>operator_delivery_readback.json</code></p>
</details></section>
<script>
document.querySelectorAll('button[data-copy-target]').forEach((button) => {{
  button.addEventListener('click', async () => {{
    const target = document.getElementById(button.dataset.copyTarget);
    const status = document.getElementById('copy-status');
    try {{
      if (new URLSearchParams(location.search).has('qa-copy-deny')) {{
        throw new Error('qa-copy-deny');
      }}
      await navigator.clipboard.writeText(target.value);
      status.textContent = 'コピーしました：' + button.dataset.copyLabel;
    }} catch (error) {{
      target.focus();
      target.select();
      document.execCommand('copy');
      status.textContent = 'コピーできるようにテキストを選択しました。Ctrl+Cでコピーしてください。';
    }}
  }});
}});
const params = new URLSearchParams(location.search);
if (params.has('qa-seek')) {{
  const video = document.getElementById('delivery-video');
  document.body.dataset.qaSeekStatus = 'pending';
  video.muted = true;
  const ratio = Number(params.get('qa-seek'));
  const run = async () => {{
    const target = Math.max(0, Math.min(video.duration - 0.05, video.duration * ratio));
    const done = new Promise(resolve => {{
      video.addEventListener('seeked', () => resolve('seeked'), {{once:true}});
      setTimeout(() => resolve('timeout'), 5000);
    }});
    video.currentTime = target;
    const status = await done;
    let playStatus = 'not_attempted';
    try {{ await video.play(); playStatus = 'resumed'; }} catch (e) {{ playStatus = 'play_failed:' + (e && e.name ? e.name : 'unknown'); }}
    document.body.dataset.qaSeek = JSON.stringify({{status, ratio, target, currentTime: video.currentTime, delta: Math.abs(video.currentTime-target), duration: video.duration, playStatus, readyState: video.readyState, mediaError: video.error ? video.error.message : null}});
    document.body.dataset.qaSeekStatus = status;
  }};
  if (Number.isFinite(video.duration) && video.duration > 0) run(); else video.addEventListener('loadedmetadata', run, {{once:true}});
}}
</script>
</main></body></html>"""


def _load_authority(*, root: Path, episode: Path, out06_readback: Path) -> dict[str, Any]:
    readback = _read_json(out06_readback, "OUT-06 readback")
    if readback.get("artifact_id") != EXPECTED_OUT06_ARTIFACT_ID:
        raise OperatorDeliveryPackError("unexpected OUT-06 artifact")
    out06_video = _resolved(root, Path(str(readback.get("outputs", {}).get("video", {}).get("path", ""))))
    _require_file(out06_video, "OUT-06 video")
    out06_hash = _sha256(out06_video)
    if out06_hash != EXPECTED_OUT06_VIDEO_SHA256:
        raise OperatorDeliveryPackError("accepted OUT-06 video hash mismatch")
    source_video = root / SOURCE_VIDEO_RELATIVE
    _require_file(source_video, "source video")
    source_hash = _sha256(source_video)
    if source_hash != SOURCE_VIDEO_SHA256:
        raise OperatorDeliveryPackError("source video hash mismatch")
    return {
        "out06_readback_path": out06_readback,
        "out06_video_path": out06_video,
        "out06_video_sha256": out06_hash,
        "source_video_path": source_video,
        "source_video_sha256": source_hash,
        "input_paths": [out06_readback, out06_video, source_video],
    }


def _extract_source_frame(
    *,
    source_video_path: Path,
    seconds: float,
    frame_path: Path,
    ffmpeg_path: str | Path | None,
    runner: ffmpeg_tiny.Runner,
) -> None:
    command = [
        str(ffmpeg_path or "ffmpeg"),
        "-y",
        "-ss",
        f"{seconds:.3f}",
        "-i",
        str(source_video_path),
        "-frames:v",
        "1",
        "-vf",
        "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=rgb24",
        str(frame_path),
    ]
    result = runner(command, capture_output=True, text=True, timeout=ffmpeg_tiny.COMMAND_TIMEOUT_SECONDS)
    if result.returncode != 0 or not frame_path.is_file():
        raise OperatorDeliveryPackError(f"failed to extract source frame at {seconds:.3f}s")


def _fit_1280x720(image: Any) -> Any:
    from PIL import Image

    image = image.convert("RGB")
    ratio = max(1280 / image.width, 720 / image.height)
    size = (int(round(image.width * ratio)), int(round(image.height * ratio)))
    image = image.resize(size, Image.Resampling.LANCZOS)
    left = (image.width - 1280) // 2
    top = (image.height - 720) // 2
    return image.crop((left, top, left + 1280, top + 720))


def _draw_text_with_outline(draw: Any, xy: tuple[int, int], text: str, font: Any) -> None:
    x, y = xy
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 240))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))


def _font_path() -> Path:
    candidates = (
        Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
        Path("C:/Windows/Fonts/YuGothB.ttc"),
        Path("C:/Windows/Fonts/meiryob.ttc"),
    )
    for path in candidates:
        if path.is_file():
            return path
    raise OperatorDeliveryPackError("no Japanese-capable local font found")


def _open_script() -> str:
    return f"""param([switch]$Serve, [int]$Port = {DEFAULT_PORT})
$ErrorActionPreference = 'Stop'
if ($Serve) {{
    & (Join-Path $PSScriptRoot 'serve_delivery.ps1') -Port $Port
    exit $LASTEXITCODE
}}
$index = Join-Path $PSScriptRoot 'index.html'
Write-Host "OUT-07 delivery entrypoint: $index"
Start-Process -FilePath $index
Write-Host "If local-file playback is blocked, rerun this command with -Serve."
"""


def _serve_script() -> str:
    return f"""param([int]$Port = {DEFAULT_PORT})
$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port/index.html"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\\..\\..\\..')
Write-Host "OUT-07 delivery URL: $url"
Write-Host "OUT-07 delivery root: $PSScriptRoot"
Start-Process -FilePath $url
Push-Location $repoRoot
try {{
    uvx python -m src.cli.serve_review --root $PSScriptRoot --port $Port
}} finally {{
    Pop-Location
}}
"""


REQUIRED_PACKAGE_FILES = (
    "assets/complete_narrative_short.mp4",
    "assets/thumbnail_context_1280x720.jpg",
    "assets/thumbnail_tension_1280x720.jpg",
    "assets/thumbnail_payoff_1280x720.jpg",
    "assets/thumbnail_direction_contact_sheet.jpg",
    "thumbnail_plan.json",
    "publish_draft.json",
    "operator_delivery_readback.json",
    "delivery_manifest.json",
    "index.html",
    "open_delivery.ps1",
    "serve_delivery.ps1",
)


def _validate_bundle(stage: Path) -> None:
    for relative in REQUIRED_PACKAGE_FILES:
        _require_file(stage / relative, relative)
    _validate_publish_draft(stage)
    manifest = _read_json(stage / "delivery_manifest.json", "delivery manifest")
    names = {item["package_relative_path"] for item in manifest["files"]}
    if names != set(REQUIRED_PACKAGE_FILES) - {"delivery_manifest.json"}:
        raise OperatorDeliveryPackError("manifest file list does not match required package files")
    if manifest["manifest_self_integrity"]["sha256"] != _canonical_manifest_self_hash(manifest):
        raise OperatorDeliveryPackError("manifest self-integrity hash mismatch")


def _validate_publish_draft(stage: Path) -> None:
    publish = _read_json(stage / "publish_draft.json", "publish draft")
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
        "selected_thumbnail",
        "source_attribution_status",
        "source_title",
        "source_url",
        "operator_copy_ready",
        "publish_ready",
        "rights_status",
        "production_acceptance",
        "production_subtitle_design_acceptance",
        "public_or_publishing_acceptance",
        "upload_attempted",
        "thumbnail_upload_attempted",
        "metadata_update_attempted",
        "visibility_update_attempted",
        "visibility",
        "made_for_kids",
        "scheduled_at",
    }
    missing = sorted(required - publish.keys())
    if missing:
        raise OperatorDeliveryPackError(f"publish draft missing required fields: {missing}")

    copied_text = "\n".join(
        [str(publish["title"]), str(publish["description"]), *map(str, publish["tags"])]
    ).lower()
    banned_copy_terms = (
        "内部確認用",
        "operator判断前",
        "operator 判断前",
        "公開判断ではありません",
        "未実施",
        "visibility",
        "made for kids",
        "ショート候補",
        "内部レビュー",
    )
    if any(term.lower() in copied_text for term in banned_copy_terms):
        raise OperatorDeliveryPackError("copied metadata contains operator-only language")
    description_lines = str(publish["description"]).splitlines()
    if not 2 <= len(description_lines) <= 4 or any(not line.strip() for line in description_lines):
        raise OperatorDeliveryPackError("publish description must contain 2-4 content lines")
    if not isinstance(publish["tags"], list) or not 5 <= len(publish["tags"]) <= 10:
        raise OperatorDeliveryPackError("publish tags must contain 5-10 content terms")
    if not isinstance(publish["evidence_trace"], list) or not publish["evidence_trace"]:
        raise OperatorDeliveryPackError("publish evidence trace is missing")

    video = publish["video"]
    packaged_video = stage / "assets" / "complete_narrative_short.mp4"
    if (
        video.get("sha256") != _sha256(packaged_video)
        or not str(video.get("path", "")).endswith("/assets/complete_narrative_short.mp4")
    ):
        raise OperatorDeliveryPackError("publish video provenance mismatch")
    if publish["selected_thumbnail"] is not None:
        raise OperatorDeliveryPackError("user-rejected thumbnail must not remain selected")
    if publish.get("poster_decision_status") != "human_selection_required":
        raise OperatorDeliveryPackError("poster decision must remain pending human selection")
    if publish.get("rejected_thumbnail_ids") != ["context", "tension", "payoff"]:
        raise OperatorDeliveryPackError("rejected thumbnail evidence mismatch")

    expected_gates = {
        "source_attribution_status": "operator_decision_required",
        "operator_copy_ready": True,
        "publish_ready": False,
        "rights_status": "pending",
        "production_acceptance": False,
        "production_subtitle_design_acceptance": False,
        "public_or_publishing_acceptance": False,
        "upload_attempted": False,
        "thumbnail_upload_attempted": False,
        "metadata_update_attempted": False,
        "visibility_update_attempted": False,
        "visibility": "operator_decision_required",
        "made_for_kids": "operator_decision_required",
        "scheduled_at": None,
    }
    if any(publish.get(key) != value for key, value in expected_gates.items()):
        raise OperatorDeliveryPackError("publish gate readback mismatch")
    if publish["source_title"] is not None or publish["source_url"] is not None:
        raise OperatorDeliveryPackError("unresolved source attribution must remain null")


def _protected_paths(episode: Path) -> dict[str, Path]:
    review = episode / "review"
    paths = {
        "human_preview_session": review / "jp_pilot01r3_cut_review" / "human_preview_session",
        "out03_real_local_selected_cut_proof": review / "out03_real_local_selected_cut_proof",
        "out04_editorial_representative_sequence": review / "out04_editorial_representative_sequence",
        "out05_vertical_short_internal_candidate": review / "out05_vertical_short_internal_candidate",
        "out06_complete_narrative_short_delivery_candidate": review / "out06_complete_narrative_short_delivery_candidate",
    }
    for label, path in paths.items():
        _require_directory(path, f"protected {label}")
    return paths


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OperatorDeliveryPackError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise OperatorDeliveryPackError(f"invalid {label}: expected object")
    return value


def _resolved(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise OperatorDeliveryPackError(f"{label} is missing: {path}")


def _require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise OperatorDeliveryPackError(f"{label} is missing: {path}")


def _validate_output_directory(episode: Path, output: Path) -> None:
    review = (episode / "review").resolve()
    if output.parent != review:
        raise OperatorDeliveryPackError("output directory must be a direct episode/review child")
    if not output.name.startswith(OUTPUT_NAME_PREFIX):
        raise OperatorDeliveryPackError("output directory name must start with out07_")


def _reject_overlap(output: Path, input_path: Path, message: str) -> None:
    output_resolved = output.resolve()
    input_resolved = input_path.resolve()
    if _is_relative_to(output_resolved, input_resolved) or _is_relative_to(input_resolved, output_resolved):
        raise OperatorDeliveryPackError(message)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _powershell_command(path: Path, root: Path) -> str:
    relative = _relative(path, root).replace("/", "\\")
    return f"powershell -ExecutionPolicy Bypass -File {relative}"
