from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from src.integrations.render import evidence_linked_comparison as comparison


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_source(
    root: Path,
    *,
    source_id: str,
    source_identity: str,
    archive_date: str,
    member: str,
    provider_channel: str,
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
            f"color=c={color}:s=640x360:r=30:d=8",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=48000:cl=stereo:d=8",
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
    provider_metadata = source_dir / "provider_metadata.json"
    caption = source_dir / "caption.json3"
    snapshot = source_dir / "processing_snapshot.json"
    identity_binding = source_dir / "source_identity_binding.json"
    _write_json(receipt, {"source_identity": source_identity})
    _write_json(ledger, {"materials": [{"hash_sha256": _sha(media)}]})
    _write_json(
        provider_metadata,
        {
            "id": source_identity.removeprefix("youtube:"),
            "upload_date": archive_date.replace("-", ""),
            "channel": provider_channel,
            "was_live": True,
            "availability": "public",
        },
    )
    _write_json(
        caption,
        {
            "events": [
                {
                    "tStartMs": index * 500,
                    "dDurationMs": 900,
                    "segs": [
                        {
                            "utf8": (
                                f"{member} {archive_date} transcript evidence {index}"
                            )
                        }
                    ],
                }
                for index in range(16)
            ]
        },
    )
    _write_json(
        snapshot,
        {
            "source_identity": source_identity,
            "user_granted_processing_scope": "local_private_review_only",
            "underlying_rights_status": "pending_or_unverified",
            "public_use": "not_authorized",
            "monetized_use": "not_authorized",
            "rights_clearance": False,
            "rights_approval": False,
        },
    )
    _write_json(
        identity_binding,
        {
            "source_identity": source_identity,
            "media_sha256": _sha(media),
            "fetch_receipt_sha256": _sha(receipt),
            "material_ledger_sha256": _sha(ledger),
        },
    )
    locators = {
        "media": media,
        "fetch_receipt": receipt,
        "material_ledger": ledger,
        "provider_metadata": provider_metadata,
        "caption": caption,
        "processing_snapshot": snapshot,
        "identity_binding": identity_binding,
    }
    source = {
        "source_id": source_id,
        "source_identity": source_identity,
        "archive_date": archive_date,
        "member": member,
        "provider_channel": provider_channel,
    }
    for name, path in locators.items():
        source[name] = {
            "path": path.relative_to(root).as_posix(),
            "sha256": _sha(path),
        }
    source["media"]["duration_seconds"] = 8.0
    source["processing_snapshot"].update(
        {
            "user_granted_processing_scope": "local_private_review_only",
            "underlying_rights_status": "pending_or_unverified",
            "public_use": "not_authorized",
            "monetized_use": "not_authorized",
            "rights_clearance": False,
            "rights_approval": False,
        }
    )
    return source


def _direction(*, artifact_id: str) -> dict:
    return {
        "schema_version": comparison.DIRECTION_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "subject_line": "架空メンバーの二週比較",
        "date_line": "2026-08-01 → 2026-08-08",
        "comparison_question": "第一印象は一週後にどう更新されたか",
        "thesis": "第一印象と理解更新を同じ画面で見る",
        "viewer_benefit": "二つの発言の対応を映像と音声から追える",
        "source_dates": ["2026-08-01", "2026-08-08"],
        "private_review_only": True,
        "human_review_pending": True,
    }


def _plan(
    *,
    artifact_id: str,
    direction_sha256: str,
    sources: list[dict],
) -> dict:
    first, second = sources
    return {
        "schema_version": comparison.PLAN_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "predeclared_direction_sha256": direction_sha256,
        "title_duration_seconds": 5.0,
        "transition_duration_seconds": 2.0,
        "sources": sources,
        "comparison_beats": [
            {
                "beat_id": "beat_001",
                "proposition": "第一印象では見た目の分かりやすさに気づいた",
                "why_informative": "後日の評価と並べる基準になる",
                "transition_label": "比較1 第一印象",
                "transition_kind": "comparison_proposition_change",
                "active_audio_source_id": first["source_id"],
                "evidence": [
                    {
                        "role": "primary_quote",
                        "source_id": first["source_id"],
                        "source_in": 0.5,
                        "source_out": 2.5,
                        "visible_source_label": (
                            f"{first['member']}｜{first['archive_date']}｜"
                            f"{first['source_identity']}"
                        ),
                        "audio_mode": "foreground",
                    },
                    {
                        "role": "paired_evidence",
                        "source_id": second["source_id"],
                        "source_in": 0.75,
                        "source_out": 2.75,
                        "visible_source_label": (
                            f"{second['member']}｜{second['archive_date']}｜"
                            f"{second['source_identity']}"
                        ),
                        "audio_mode": "muted_reference",
                    },
                ],
            },
            {
                "beat_id": "beat_002",
                "proposition": "一週後は文脈を含めた理解へ更新された",
                "why_informative": "初見の感想と後日の理解を直接比較できる",
                "transition_label": "比較2 理解更新",
                "transition_kind": "comparison_proposition_change",
                "active_audio_source_id": second["source_id"],
                "evidence": [
                    {
                        "role": "primary_quote",
                        "source_id": second["source_id"],
                        "source_in": 3.0,
                        "source_out": 5.0,
                        "visible_source_label": (
                            f"{second['member']}｜{second['archive_date']}｜"
                            f"{second['source_identity']}"
                        ),
                        "audio_mode": "foreground",
                    },
                    {
                        "role": "paired_evidence",
                        "source_id": first["source_id"],
                        "source_in": 3.25,
                        "source_out": 5.25,
                        "visible_source_label": (
                            f"{first['member']}｜{first['archive_date']}｜"
                            f"{first['source_identity']}"
                        ),
                        "audio_mode": "muted_reference",
                    },
                ],
            },
        ],
        "excluded_assets": sorted(comparison.REQUIRED_EXCLUSIONS),
        "review_labels": {
            "private_review_only": True,
            "human_review_pending": True,
            "rights_approval": "not_granted",
            "production_approval": False,
            "public_use": False,
            "monetized_use": False,
            "publication_approval": False,
            "upload_attempted": False,
        },
    }


@pytest.fixture
def comparison_inputs(tmp_path: Path) -> tuple[dict, dict, Path, Path]:
    artifact_id = "clip-s2-generic-comparison-v1-001"
    direction = _direction(artifact_id=artifact_id)
    direction_path = tmp_path / "direction.json"
    _write_json(direction_path, direction)
    sources = [
        _make_source(
            tmp_path,
            source_id="alpha_stream",
            source_identity="youtube:fixture-alpha",
            archive_date="2026-08-01",
            member="架空メンバー",
            provider_channel="Fixture Channel Alpha",
            color="0x315A84",
        ),
        _make_source(
            tmp_path,
            source_id="beta_stream",
            source_identity="youtube:fixture-beta",
            archive_date="2026-08-08",
            member="架空メンバー",
            provider_channel="Fixture Channel Beta",
            color="0x844A31",
        ),
    ]
    plan = _plan(
        artifact_id=artifact_id,
        direction_sha256=_sha(direction_path),
        sources=sources,
    )
    plan_path = tmp_path / "plan.json"
    _write_json(plan_path, plan)
    return direction, plan, direction_path, plan_path


def test_plan_rejects_unbound_or_duplicate_evidence(
    comparison_inputs: tuple[dict, dict, Path, Path],
) -> None:
    direction, plan, direction_path, _ = comparison_inputs
    unbound = copy.deepcopy(plan)
    unbound["comparison_beats"][0]["evidence"][1]["source_id"] = "missing"
    with pytest.raises(
        comparison.EvidenceLinkedComparisonError,
        match="unbound or duplicate evidence",
    ):
        comparison.validate_comparison_plan(
            unbound,
            direction=direction,
            direction_sha256=_sha(direction_path),
        )

    duplicate = copy.deepcopy(plan)
    duplicate["comparison_beats"][0]["evidence"][1]["source_id"] = (
        duplicate["comparison_beats"][0]["evidence"][0]["source_id"]
    )
    with pytest.raises(
        comparison.EvidenceLinkedComparisonError,
        match="unbound or duplicate evidence",
    ):
        comparison.validate_comparison_plan(
            duplicate,
            direction=direction,
            direction_sha256=_sha(direction_path),
        )


def test_plan_rejects_mismatched_label_and_multiple_audio_owners(
    comparison_inputs: tuple[dict, dict, Path, Path],
) -> None:
    direction, plan, direction_path, _ = comparison_inputs
    bad_label = copy.deepcopy(plan)
    bad_label["comparison_beats"][0]["evidence"][1][
        "visible_source_label"
    ] = "wrong source"
    with pytest.raises(
        comparison.EvidenceLinkedComparisonError,
        match="source label does not match",
    ):
        comparison.validate_comparison_plan(
            bad_label,
            direction=direction,
            direction_sha256=_sha(direction_path),
        )

    overlapping_audio = copy.deepcopy(plan)
    overlapping_audio["comparison_beats"][0]["evidence"][1][
        "audio_mode"
    ] = "foreground"
    with pytest.raises(
        comparison.EvidenceLinkedComparisonError,
        match="exactly one foreground audio owner",
    ):
        comparison.validate_comparison_plan(
            overlapping_audio,
            direction=direction,
            direction_sha256=_sha(direction_path),
        )


def test_plan_rejects_unmarked_source_swap(
    comparison_inputs: tuple[dict, dict, Path, Path],
) -> None:
    direction, plan, direction_path, _ = comparison_inputs
    unmarked = copy.deepcopy(plan)
    unmarked["comparison_beats"][1]["transition_kind"] = "same_proposition"
    with pytest.raises(
        comparison.EvidenceLinkedComparisonError,
        match="without a marked transition",
    ):
        comparison.validate_comparison_plan(
            unmarked,
            direction=direction,
            direction_sha256=_sha(direction_path),
        )


def test_builds_generic_private_comparison_bundle(
    tmp_path: Path,
    comparison_inputs: tuple[dict, dict, Path, Path],
) -> None:
    _, plan, direction_path, plan_path = comparison_inputs
    output_dir = tmp_path / "artifact"
    result = comparison.build_evidence_linked_comparison(
        plan_path=plan_path,
        direction_path=direction_path,
        output_dir=output_dir,
        review_port=8094,
        base_dir=tmp_path,
    )

    assert result["artifact_id"] == "clip-s2-generic-comparison-v1-001"
    assert result["state"] == comparison.READY_STATE
    assert result["beat_count"] == 2
    assert result["final_video"].is_file()
    assert result["review_index"].is_file()

    timeline = json.loads(
        (output_dir / "comparison_timeline.json").read_text(encoding="utf-8")
    )
    assert all(len(beat["concurrent_source_ids"]) == 2 for beat in timeline["beats"])
    assert all(beat["foreground_audio_owner_count"] == 1 for beat in timeline["beats"])
    assert all(timeline["layout_checks"].values())
    assert [
        row["event_type"]
        for row in timeline["inspection_targets"]
        if row["event_type"] == "comparison_transition"
    ] == ["comparison_transition", "comparison_transition"]

    transcript = json.loads(
        (output_dir / "transcript_context.json").read_text(encoding="utf-8")
    )
    assert all(
        evidence["selected_cues"]
        and evidence["selected_text"]
        and evidence["source_range"]
        for beat in transcript["beats"]
        for evidence in beat["evidence"]
    )
    provenance = json.loads(
        (output_dir / "provenance_snapshot.json").read_text(encoding="utf-8")
    )
    assert [row["source_identity"] for row in provenance["sources"]] == [
        "youtube:fixture-alpha",
        "youtube:fixture-beta",
    ]
    assert all(
        beat["transcript_context_present"] for beat in provenance["beat_bindings"]
    )

    readback = json.loads(
        (output_dir / "media_readback.json").read_text(encoding="utf-8")
    )
    assert readback["status"] == "passed"
    assert readback["metadata"]["resolution"] == "1920x1080"
    assert readback["checks"]["actual_content_16_9_layout"] is True
    assert readback["checks"]["source_legible_at_review_size"] is True
    assert readback["checks"]["full_non_audible_decode"] is True

    review_html = result["review_index"].read_text(encoding="utf-8")
    video_tag = comparison.re.search(r"<video\b[^>]*>", review_html)
    assert video_tag
    assert " muted" in video_tag.group(0)
    assert "autoplay" not in video_tag.group(0)
    assert 'src="../final_video.mp4"' in video_tag.group(0)
    assert "C:\\" not in review_html

    manifest = json.loads(
        (output_dir / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["comparison"]["concurrent_source_panels"] is True
    assert manifest["comparison"]["foreground_audio_owner_per_beat"] == 1
    comparison.validate_run_manifest(output_dir)
    assert (
        output_dir / "review" / "evidence" / "comparison_contact_sheet.jpg"
    ).is_file()
    assert [source["member"] for source in plan["sources"]] == [
        "架空メンバー",
        "架空メンバー",
    ]
