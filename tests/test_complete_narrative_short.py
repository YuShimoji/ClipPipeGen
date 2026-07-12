from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.integrations.render import complete_narrative_short as cns


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path) -> dict[str, Path | str]:
    root = tmp_path
    episode = root / "episodes" / "ep_out06_fixture"
    review = episode / "review"
    out03 = review / "out03_real_local_selected_cut_proof"
    out04_dir = review / "out04_editorial_representative_sequence"
    out05_dir = review / "out05_vertical_short_internal_candidate"
    human = review / "jp_pilot01r3_cut_review" / "human_preview_session"
    for path in (out03, out04_dir, out05_dir, human):
        path.mkdir(parents=True, exist_ok=True)
        (path / "protected.txt").write_text(path.name, encoding="utf-8")

    source_video = episode / "materials" / "src_video" / "source_video.mp4"
    source_audio = episode / "materials" / "src_audio" / "source.wav"
    source_video.parent.mkdir(parents=True)
    source_audio.parent.mkdir(parents=True)
    source_video.write_bytes(b"fixture-source-video")
    source_audio.write_bytes(b"fixture-source-audio")

    timeline = [
        {
            "id": "cut_001",
            "source_start_seconds": 2.453,
            "source_end_seconds": 9.293,
            "sequence_start_seconds": 0.000,
            "sequence_end_seconds": 6.840,
            "duration_seconds": 6.840,
            "transition_in": "sequence_start",
            "context_status": "passed",
        },
        {
            "id": "cut_002",
            "source_start_seconds": 12.329,
            "source_end_seconds": 17.167,
            "sequence_start_seconds": 6.840,
            "sequence_end_seconds": 11.678,
            "duration_seconds": 4.838,
            "transition_in": "hard_cut",
            "context_status": "passed",
        },
    ]
    opening_texts = (
        "もしもし？",
        "はじめです！",
        "今どこですか？",
        "体育館裏で待ってます！！",
        "わかりました！",
        "向かいます！",
        "押忍！",
        "団長！",
        "ホロライブの番長として",
    )
    opening_subtitles = []
    for index, text in enumerate(opening_texts, start=1):
        cut_id = "cut_001" if index <= 7 else "cut_002"
        if cut_id == "cut_001":
            sequence_start = (index - 1) * 0.8
            source_start = 2.453 + sequence_start
        else:
            sequence_start = 6.840 + (index - 8) * 1.2
            source_start = 12.329 + (index - 8) * 1.2
        sequence_end = min(sequence_start + 0.7, 11.678)
        opening_subtitles.append(
            {
                "id": f"sub_{index:03d}",
                "cut_id": cut_id,
                "sequence_start_seconds": sequence_start,
                "sequence_end_seconds": sequence_end,
                "source_start_seconds": source_start,
                "source_end_seconds": source_start + (sequence_end - sequence_start),
                "text": text,
                "source_type": "imported_subtitle_track",
                "source_segment_ids": [f"seg_{index:06d}"],
            }
        )
    out04 = {
        "artifact_id": "clip-out04-editorial-representative-sequence-v0-001",
        "timeline": timeline,
        "subtitles": opening_subtitles,
    }
    out04_path = out04_dir / "sequence_readback.json"
    _write_json(out04_path, out04)
    out04_hash = cns._sha256(out04_path)

    edit_subtitles = []
    transcript_segments = []
    cut3_texts = [f"追加字幕{index}" for index in range(10, 30)]
    cut3_texts[0] = "来ねぇ！！"
    cut3_texts[3] = "なんで来なかったんすか！！"
    cut3_texts[4] = "ずっと待ってたんすよ！！"
    cut3_texts[9] = "はじめの勝ちってことでいいですね？"
    cut3_texts[14] = "団長、ちなみに、他の番長知ってますか？"
    cut3_texts[18] = "マリンならあっちにいたよ"
    cut3_texts[-1] = "ありがとうございますー！"
    for offset, index in enumerate(range(10, 30)):
        start = 22.606 + offset * 1.25
        end = start + 0.9
        if index == 29:
            end = 49.566
        subtitle = {
            "id": f"sub_{index:03d}",
            "cut_id": "cut_003",
            "start_seconds": start,
            "end_seconds": end,
            "text": cut3_texts[offset],
            "source_type": "imported_subtitle_track",
            "source_segment_ids": [f"seg_{index:06d}"],
        }
        edit_subtitles.append(subtitle)
        transcript_segments.append(
            {
                "id": f"seg_{index:06d}",
                "start_seconds": start,
                "end_seconds": end,
                "text": cut3_texts[offset],
                "review_status": "accepted",
            }
        )
    edit_subtitles.append(
        {
            "id": "sub_030",
            "cut_id": "cut_004",
            "start_seconds": 50.868,
            "end_seconds": 53.904,
            "text": "excluded",
            "source_type": "imported_subtitle_track",
            "source_segment_ids": ["seg_000030"],
        }
    )
    transcript_segments.append(
        {
            "id": "seg_000030",
            "start_seconds": 50.868,
            "end_seconds": 53.904,
            "text": "excluded",
            "review_status": "accepted",
        }
    )
    edit_pack = {
        "cut_candidates": [
            {
                "id": "cut_003",
                "start_seconds": 22.606,
                "end_seconds": 49.566,
                "context_check": {
                    "status": "needs_review",
                    "notes": ["retained context risk"],
                },
            }
        ],
        "subtitles": edit_subtitles,
    }
    transcript = {"segments": transcript_segments}
    decision = {
        "decisions": [
            {
                "cut_id": "cut_003",
                "final_cut_decision": "keep",
                "context_status": "needs_review",
                "decision_reason": "strong candidate arc",
                "manual_override_reason": "retain visible context risk as a candidate",
            }
        ]
    }
    proxy = {
        "revisions": [
            {
                "cut_id": "cut_003",
                "proxy_decision": "proceed_with_limitations",
                "context_risk_handling": "keep_retained_risk_visible",
                "operator_note": "retained limitation remains visible",
            }
        ]
    }
    _write_json(episode / "edit_pack.json", edit_pack)
    _write_json(episode / "transcript.json", transcript)
    _write_json(episode / cns.DECISION_PACKET_RELATIVE, decision)
    _write_json(episode / cns.PROXY_AUTHORITY_RELATIVE, proxy)
    _write_json(episode / "rights_manifest.json", {"compliance_check": {"status": "pending"}})
    _write_json(episode / "material_ledger.json", {"materials": []})

    out05_video = out05_dir / "assets" / "vertical_short_candidate.mp4"
    out05_video.parent.mkdir(parents=True)
    out05_video.write_bytes(b"accepted-out05-video")
    recorded_inputs = {
        cns._relative(source_video, root): cns._sha256(source_video),
        cns._relative(source_audio, root): cns._sha256(source_audio),
    }
    out05 = {
        "artifact_id": cns.EXPECTED_OUT05_ARTIFACT_ID,
        "timeline": {
            "ordered_cut_ids": ["cut_001", "cut_002"],
            "expected_duration_seconds": 11.678,
            "hard_cut_seconds": 6.840,
        },
        "subtitle": {"count": 9},
        "reframe": {
            "selected_option": "full_16_9_fit_source_derived_blurred_canvas"
        },
        "boundaries": {
            "internal_review_only": True,
            "production_candidate": False,
            "production_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "rights_status": "pending",
            "public_ready": False,
            "publishing": False,
            "publish_attempted": False,
        },
        "render": {
            "output_path": cns._relative(out05_video, root),
            "output_sha256": cns._sha256(out05_video),
        },
        "predecessor": {
            "readback_path": cns._relative(out04_path, root),
            "readback_sha256": out04_hash,
        },
        "input_hashes": recorded_inputs,
    }
    predecessor = out05_dir / "candidate_readback.json"
    _write_json(predecessor, out05)
    return {
        "root": root,
        "episode": episode,
        "output": review / "out06_complete_narrative_short_delivery_candidate",
        "predecessor": predecessor,
        "predecessor_hash": cns._sha256(predecessor),
        "predecessor_video_hash": cns._sha256(out05_video),
        "out04_hash": out04_hash,
    }


def _fake_render(**kwargs) -> dict:
    video = Path(kwargs["video_path"])
    frame_sheet = Path(kwargs["frame_sheet_path"])
    video.write_bytes(b"complete-narrative-video")
    frame_sheet.write_bytes(b"frame-qa")
    return {
        "media": {
            "video_codec": "h264",
            "audio_codec": "aac",
            "width": 1080,
            "height": 1920,
            "fps": 30.0,
            "duration_seconds": 38.650,
            "stream_counts": {"video": 1, "audio": 1, "other": 0},
            "pixel_format": "yuv420p",
        },
        "selected_video_encoder": "libx264",
        "attempts": [{"video_codec": "libx264", "status": "passed", "exit_code": 0}],
        "duration_matches_expected": True,
        "full_decode": {"status": "passed", "exit_code": 0, "stderr_empty": True},
        "faststart": {"status": "passed", "moov_before_mdat": True},
        "audio": {
            "measurement_method": "fixture",
            "input_measurement": {"integrated_lufs": -18.0, "true_peak_dbtp": -2.0},
            "decision": "normalize_clear_loudness_gap_to_internal_candidate_target",
            "normalization_applied": True,
            "target": {"integrated_lufs": -14.0, "true_peak_dbtp_max": -1.0},
            "output_measurement": {"integrated_lufs": -14.1, "true_peak_dbtp": -1.5},
        },
        "frame_samples": [
            {"label": label, "seconds": seconds, "status": "extracted"}
            for label, seconds in cns.FRAME_SAMPLES
        ],
    }


def _fake_post(**kwargs) -> dict:
    Path(kwargs["poster_path"]).write_bytes(b"poster")
    return {
        "status": "passed",
        "poster": {
            "source": "final_render_frame",
            "seconds": 37.8,
            "decorated_thumbnail": False,
            "status": "extracted",
        },
        "boundary_analysis": [
            {
                "boundary_seconds": boundary,
                "status": "passed",
                "click_risk": False,
                "digital_dropout_risk": False,
            }
            for boundary in kwargs["boundaries"]
        ],
        "sync": {"status": "passed", "boundaries_seconds": list(kwargs["boundaries"])},
    }


def _build(fixture: dict[str, Path | str], **overrides):
    args = {
        "episode_dir": fixture["episode"],
        "output_dir": fixture["output"],
        "predecessor_readback_path": fixture["predecessor"],
        "base_dir": fixture["root"],
        "render_executor": _fake_render,
        "post_render_executor": _fake_post,
        "expected_predecessor_sha256": fixture["predecessor_hash"],
        "expected_predecessor_video_sha256": fixture["predecessor_video_hash"],
        "expected_out04_sha256": fixture["out04_hash"],
    }
    args.update(overrides)
    return cns.build_complete_narrative_short(**args)


def test_build_complete_narrative_short_atomic_package(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    result = _build(fixture)
    output = Path(fixture["output"])
    assert result["artifact_id"] == cns.ARTIFACT_ID
    assert all((output / relative).is_file() for relative in cns.REQUIRED_PACKAGE_FILES)
    readback = result["readback"]
    assert readback["timeline"]["ordered_cut_ids"] == ["cut_001", "cut_002", "cut_003"]
    assert readback["timeline"]["semantic_duration_seconds"] == 38.638
    assert readback["subtitle"]["count"] == 29
    assert readback["subtitle"]["ids"] == list(cns.EXPECTED_SUBTITLE_IDS)
    assert readback["cut003_authority"]["proxy_decision"] == "proceed_with_limitations"
    assert readback["boundaries"] == cns._closed_gates()
    assert readback["serve_command"].endswith("serve_preview.ps1")


def test_out06_reviewed_wraps_are_repaired_in_package_readback(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    readback = _build(fixture)["readback"]
    by_id = {item["subtitle_id"]: item for item in readback["subtitle"]["items"]}
    expected = {
        "sub_013": ["なんで", "来なかった", "んすか！！"],
        "sub_014": ["ずっと", "待ってたんすよ！！"],
        "sub_019": ["はじめの勝ちって", "ことでいいですね？"],
        "sub_024": ["団長、ちなみに、", "他の番長", "知ってますか？"],
        "sub_028": ["マリンなら", "あっちにいたよ"],
        "sub_029": ["ありがとう", "ございますー！"],
    }
    for subtitle_id, lines in expected.items():
        item = by_id[subtitle_id]
        assert item["wrapped_lines"] == lines
        assert "".join(lines) == item["text"]
        assert item["vertical_balance_readback"]["line_break_hint"]["status"] == (
            "applied_preferred_lines"
        )


def test_manifest_hashes_every_payload_and_declares_self_integrity(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    _build(fixture)
    output = Path(fixture["output"])
    manifest = json.loads((output / "delivery_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) == len(cns.REQUIRED_PACKAGE_FILES) - 1
    for item in manifest["files"]:
        assert cns._sha256(output / item["package_relative_path"]) == item["sha256"]
    assert manifest["manifest_self_integrity"]["sha256"] == cns._canonical_manifest_self_hash(
        manifest
    )
    assert manifest["closed_gates"] == cns._closed_gates()


def test_cut003_authority_conflict_stops_before_output(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    decision_path = Path(fixture["episode"]) / cns.DECISION_PACKET_RELATIVE
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["decisions"][0]["final_cut_decision"] = "needs_adjustment"
    _write_json(decision_path, decision)
    with pytest.raises(cns.CompleteNarrativeShortError, match="keep/needs_review"):
        _build(fixture)
    assert not Path(fixture["output"]).exists()


def test_sub030_cannot_move_into_cut003(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    edit_path = Path(fixture["episode"]) / "edit_pack.json"
    edit = json.loads(edit_path.read_text(encoding="utf-8"))
    edit["subtitles"][-1]["cut_id"] = "cut_003"
    _write_json(edit_path, edit)
    with pytest.raises(cns.CompleteNarrativeShortError, match="sub_030 exclusion"):
        _build(fixture)


@pytest.mark.parametrize("name", ("out06_../escape", "other_name", "out06_bad name"))
def test_output_directory_rejects_unsafe_name(tmp_path: Path, name: str) -> None:
    fixture = _fixture(tmp_path)
    output = Path(fixture["episode"]) / "review" / name
    with pytest.raises(cns.CompleteNarrativeShortError):
        _build(fixture, output_dir=output)


def test_render_failure_preserves_existing_output(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    output = Path(fixture["output"])
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("existing", encoding="utf-8")

    def fail_render(**_kwargs):
        raise cns.CompleteNarrativeShortError("fixture render failure")

    with pytest.raises(cns.CompleteNarrativeShortError, match="fixture render failure"):
        _build(fixture, render_executor=fail_render)
    assert marker.read_text(encoding="utf-8") == "existing"
    assert not list(output.parent.glob(f".{output.name}.staging-*"))


def test_preview_lock_failure_is_normalized_and_preserves_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _fixture(tmp_path)
    output = Path(fixture["output"])
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("existing", encoding="utf-8")

    def locked_promote(*_args, **_kwargs):
        raise PermissionError("fixture preview lock")

    monkeypatch.setattr(cns, "_atomic_promote", locked_promote)
    with pytest.raises(cns.CompleteNarrativeShortError, match="preview server"):
        _build(fixture)
    assert marker.read_text(encoding="utf-8") == "existing"
    assert not list(output.parent.glob(f".{output.name}.staging-*"))


def test_protected_out05_overlap_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    protected = Path(fixture["episode"]) / "review" / "out05_vertical_short_internal_candidate"
    with pytest.raises(cns.CompleteNarrativeShortError, match="start with out06"):
        _build(fixture, output_dir=protected)
