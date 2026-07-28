from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from src.integrations.render import persona_led_stream_digest as digest


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _direction() -> dict:
    return {
        "schema_version": digest.DIRECTION_SCHEMA_VERSION,
        "artifact_id": digest.ARTIFACT_ID,
        "primary_persona": "大空スバルのファン who wants a condensed catch-up",
        "member": "大空スバル",
        "source_archive_dates": ["2026-07-18", "2026-07-25"],
        "concept": "大空スバルの2026-07-18〜2026-07-25ドラゴンボール初見キャッチアップ",
        "title_line": "大空スバルの2週間",
        "subtitle_line": "2026-07-18 → 2026-07-25 / ドラゴンボール初見の変化",
        "viewer_benefit": "二週の発見と印象の変化を短時間で追える。",
        "both_sources_necessary": "初読の発見と一週後の更新は重複しない。",
        "orientation": "concept_first",
        "claims_latest": False,
    }


def _make_source(
    root: Path,
    *,
    source_id: str,
    source_identity: str,
    archive_date: str,
    color: str,
) -> dict:
    ffmpeg = shutil.which("ffmpeg")
    assert ffmpeg
    source_dir = root / source_id
    media = source_dir / "source_video.mp4"
    source_dir.mkdir(parents=True)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"color=c={color}:s=640x360:r=30:d=6",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=48000:cl=stereo:d=6",
            "-shortest",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(media),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    receipt = source_dir / "fetch_receipt.json"
    ledger = source_dir / "material_ledger.json"
    provider_metadata = source_dir / "source.info.json"
    snapshot = source_dir / "processing_snapshot.json"
    identity_binding = source_dir / "source_identity_binding.json"
    caption = source_dir / "caption.json3"
    _write_json(receipt, {"source_identity": source_identity})
    _write_json(ledger, {"materials": [{"hash_sha256": _sha(media)}]})
    _write_json(
        provider_metadata,
        {
            "id": source_identity.removeprefix("youtube:"),
            "upload_date": archive_date.replace("-", ""),
            "channel": "Subaru Ch. 大空スバル",
            "was_live": True,
            "availability": "public",
        },
    )
    snapshot_payload = {
        "source_identity": source_identity,
        "user_granted_processing_scope": "local_private_review_only",
        "underlying_rights_status": "pending_or_unverified",
        "public_use": "not_authorized",
        "monetized_use": "not_authorized",
        "rights_clearance": False,
        "rights_approval": False,
    }
    if source_identity == "youtube:ib3DwHDI71Q":
        snapshot_payload["authority_id"] = (
            "CPG-AUTH-20260728-IB3DWH-PRIVATE-ACQUISITION-01"
        )
    else:
        snapshot_payload["acquisition_effect_this_mission"] = (
            "not_attempted_reused_existing"
        )
    _write_json(snapshot, snapshot_payload)
    _write_json(
        identity_binding,
        {
            "source_identity": source_identity,
            "media_sha256": _sha(media),
            "fetch_receipt_sha256": _sha(receipt),
            "material_ledger_sha256": _sha(ledger),
        },
    )
    _write_json(
        caption,
        {
            "events": [
                {
                    "tStartMs": index * 500,
                    "dDurationMs": 900,
                    "segs": [{"utf8": f"{archive_date} 字幕 {index}"}],
                }
                for index in range(12)
            ]
        },
    )
    return {
        "source_id": source_id,
        "source_identity": source_identity,
        "archive_date": archive_date,
        "member": "大空スバル",
        "ordinary_livestream": True,
        "official_animation": False,
        "fixture": False,
        "media": {
            "path": media.relative_to(root).as_posix(),
            "sha256": _sha(media),
            "duration_seconds": 6.0,
        },
        "fetch_receipt": {
            "path": receipt.relative_to(root).as_posix(),
            "sha256": _sha(receipt),
        },
        "material_ledger": {
            "path": ledger.relative_to(root).as_posix(),
            "sha256": _sha(ledger),
        },
        "provider_metadata": {
            "path": provider_metadata.relative_to(root).as_posix(),
            "sha256": _sha(provider_metadata),
        },
        "caption": {
            "path": caption.relative_to(root).as_posix(),
            "sha256": _sha(caption),
        },
        "processing_snapshot": {
            "path": snapshot.relative_to(root).as_posix(),
            "sha256": _sha(snapshot),
            "user_granted_processing_scope": "local_private_review_only",
            "underlying_rights_status": "pending_or_unverified",
            "public_use": "not_authorized",
            "monetized_use": "not_authorized",
            "rights_clearance": False,
            "rights_approval": False,
        },
        "identity_binding": {
            "path": identity_binding.relative_to(root).as_posix(),
            "sha256": _sha(identity_binding),
        },
    }


def _plan(root: Path, direction_path: Path) -> dict:
    first = _make_source(
        root,
        source_id="subaru_20260718",
        source_identity="youtube:ib3DwHDI71Q",
        archive_date="2026-07-18",
        color="0x254b6e",
    )
    second = _make_source(
        root,
        source_id="subaru_20260725",
        source_identity="youtube:rltNvZ_FY8Q",
        archive_date="2026-07-25",
        color="0x6e3e25",
    )
    return {
        "schema_version": digest.PLAN_SCHEMA_VERSION,
        "artifact_id": digest.ARTIFACT_ID,
        "predeclared_direction_sha256": _sha(direction_path),
        "concept": _direction()["concept"],
        "title_duration_seconds": 4.0,
        "sources": [first, second],
        "cuts": [
            {
                "cut_id": "cut_001",
                "source_id": "subaru_20260718",
                "source_in": 0.2,
                "source_out": 1.5,
                "topic": "初読の発見",
                "immediate_function": "読みやすさの第一印象を示す",
                "section_label": "7/18 初読の発見",
                "transition_basis": "sequence_start",
                "transition_explanation": "opening conceptから最初の根拠へ進む",
            },
            {
                "cut_id": "cut_002",
                "source_id": "subaru_20260718",
                "source_in": 2.0,
                "source_out": 3.3,
                "topic": "初読の発見",
                "immediate_function": "同じ読みやすさを具体化する",
                "section_label": "絵だけでも追える",
                "transition_basis": "same_topic_continuation",
                "transition_explanation": "同じ発見の具体化",
            },
            {
                "cut_id": "cut_003",
                "source_id": "subaru_20260725",
                "source_in": 0.2,
                "source_out": 1.5,
                "topic": "一週後の更新",
                "immediate_function": "原作とゲームを経た更新を示す",
                "section_label": "7/25 一週後の更新",
                "transition_basis": "explicit_topic_change",
                "transition_explanation": "日付と段階の変化を表示する",
            },
            {
                "cut_id": "cut_004",
                "source_id": "subaru_20260725",
                "source_in": 2.0,
                "source_out": 3.3,
                "topic": "人物理解の更新",
                "immediate_function": "文脈で印象が変わる結論を示す",
                "section_label": "文脈で人物像が変わる",
                "transition_basis": "explicit_topic_change",
                "transition_explanation": "同じ週の別観点を明示する",
            },
        ],
        "excluded_assets": [
            "official_animation",
            "fixture_media",
            "tts",
            "generated_narration",
            "new_music",
            "ai_imagery",
            "promotional_cta",
        ],
        "review_labels": {
            "private_review_only": True,
            "human_review_pending": True,
            "rights_approval": "not_granted",
            "public_use": False,
            "monetized_use": False,
        },
    }


def test_direction_rejects_latest_claim() -> None:
    direction = _direction()
    direction["concept"] += " 最新"
    direction["claims_latest"] = True
    with pytest.raises(digest.PersonaLedStreamDigestError):
        digest.validate_predeclared_direction(direction)


def test_plan_rejects_another_source(tmp_path: Path) -> None:
    direction_path = tmp_path / "direction.json"
    _write_json(direction_path, _direction())
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg unavailable")
    plan = _plan(tmp_path, direction_path)
    plan["sources"][1]["source_identity"] = "youtube:another"
    with pytest.raises(digest.PersonaLedStreamDigestError):
        digest.validate_digest_plan(plan, direction_sha256=_sha(direction_path))


def test_registry_quarantines_rejected_predecessor_and_routes_successor() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = (root / "artifacts" / "ARTIFACTS.md").read_text(encoding="utf-8")
    predecessor = (
        root / "docs" / "output_layer" / "S1_TWO_SOURCE_COMMON_CONTEXT_PROBE.md"
    ).read_text(encoding="utf-8")
    runtime = (root / "docs" / "RUNTIME_STATE.md").read_text(encoding="utf-8")
    successor_section = registry.split(f"## `{digest.ARTIFACT_ID}`", 1)[1].split(
        "\n## `", 1
    )[0]
    predecessor_section = registry.split(
        "## `clip-s1-two-source-common-context-probe-v1-001`", 1
    )[1].split("\n## `", 1)[0]

    assert "active_candidate=true" in successor_section
    assert "default_candidate=false" in successor_section
    assert "rejected_superseded_historical_evidence" in predecessor_section
    assert "active_candidate=false" in predecessor_section
    assert "default_candidate=false" in predecessor_section
    assert "`reject / BLOCK_CURRENT / superseded / not bounded_repair`" in predecessor
    assert "bafe25afe0d2cad0cfaa0a2bda432b7ac0ef8471" in predecessor
    assert f"s1_predecessor_artifact: {digest.ARTIFACT_ID}" in runtime
    assert f"active_artifact: {digest.ARTIFACT_ID}" not in runtime
    assert "active_artifact: clip-s2-subaru-evidence-linked-comparison-v1-002" in runtime
    assert (
        "rejected_predecessor_artifact: "
        "clip-s1-two-source-common-context-probe-v1-001"
    ) in runtime


@pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="ffmpeg/ffprobe unavailable",
)
def test_builds_private_muted_portable_review_bundle(tmp_path: Path) -> None:
    direction_path = tmp_path / "direction.json"
    plan_path = tmp_path / "plan.json"
    _write_json(direction_path, _direction())
    _write_json(plan_path, _plan(tmp_path, direction_path))
    result = digest.build_persona_led_stream_digest(
        plan_path=plan_path,
        direction_path=direction_path,
        output_dir=Path("artifact"),
        base_dir=tmp_path,
        review_port=18791,
    )
    assert result["state"] == digest.READY_STATE
    assert result["cut_count"] == 4
    assert result["source_switch_count"] == 1
    review_html = (tmp_path / "artifact" / "review" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "<video" in review_html
    assert " muted" in review_html
    assert " autoplay" not in review_html
    assert 'src="../final_video.mp4"' in review_html
    assert "C:\\" not in review_html
    manifest = json.loads(
        (tmp_path / "artifact" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["private_review_only"] is True
    assert manifest["human_review_pending"] is True
    assert manifest["rights_approval"] == "not_granted"
    digest.validate_run_manifest(tmp_path / "artifact")
