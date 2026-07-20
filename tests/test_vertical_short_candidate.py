from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.integrations.render import vertical_short_candidate as vsc
from src.integrations.render.subtitle_overlay_visual_proof import _ass_text


SUBTITLES = [
    ("sub_001", "cut_001", 0.000, 0.867, "もしもし？"),
    ("sub_002", "cut_001", 0.867, 1.601, "はじめです！"),
    ("sub_003", "cut_001", 1.601, 2.369, "…はい？"),
    ("sub_004", "cut_001", 2.369, 3.103, "はじめです！！"),
    ("sub_005", "cut_001", 3.103, 4.838, "なんと…？ もう一度いいですか？"),
    ("sub_006", "cut_001", 4.838, 6.072, "体育館裏で待ってます！！"),
    ("sub_007", "cut_001", 6.072, 6.840, "なんて？？"),
    ("sub_008", "cut_002", 6.840, 8.809, "ふっふっふ😏 呼び出してやったぞ😏"),
    (
        "sub_009",
        "cut_002",
        8.809,
        11.678,
        "ホロライブの番長として、 団長を倒してやる！！",
    ),
]


@pytest.mark.parametrize(
    ("integrated_lufs", "true_peak_dbtp", "expected"),
    [
        (-16.61, -2.79, True),
        (-14.0, -2.0, False),
        (-12.6, -2.0, True),
        (-14.0, -0.9, True),
    ],
)
def test_loudness_normalization_window_matches_final_qa(
    integrated_lufs: float,
    true_peak_dbtp: float,
    expected: bool,
) -> None:
    assert (
        vsc._should_normalize_loudness(
            {
                "integrated_lufs": integrated_lufs,
                "true_peak_dbtp": true_peak_dbtp,
            }
        )
        is expected
    )


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path) -> dict[str, Path | str]:
    episode = tmp_path / "episodes" / "episode_001"
    review = episode / "review"
    out04 = review / "out04_editorial_representative_sequence"
    out04_video = out04 / "assets" / "editorial_sequence.mp4"
    out04_video.parent.mkdir(parents=True)
    out04_video.write_bytes(b"accepted-out04-video")
    (review / "out03_real_local_selected_cut_proof").mkdir(parents=True)
    (review / "out03_real_local_selected_cut_proof" / "proof.txt").write_text("out03")
    human = review / "jp_pilot01r3_cut_review" / "human_preview_session"
    human.mkdir(parents=True)
    (human / "manifest.txt").write_text("protected")

    source_video = episode / "materials" / "video" / "source_video.mp4"
    source_audio = episode / "materials" / "audio" / "source.wav"
    source_video.parent.mkdir(parents=True)
    source_audio.parent.mkdir(parents=True)
    source_video.write_bytes(b"source-video")
    source_audio.write_bytes(b"source-audio")
    ledger = {
        "materials": [
            {
                "id": "source_video",
                "kind": "source_video",
                "file_path": source_video.relative_to(tmp_path).as_posix(),
                "hash_sha256": vsc._sha256(source_video),
                "registered_by": "tool:asset_fetch_local_video",
            },
            {
                "id": "source_audio",
                "kind": "source_audio",
                "file_path": source_audio.relative_to(tmp_path).as_posix(),
                "hash_sha256": vsc._sha256(source_audio),
                "registered_by": "tool:asset_fetch_local_audio",
            },
        ]
    }
    paths = {
        "edit_pack": episode / "edit_pack.json",
        "transcript": episode / "transcript.json",
        "material_ledger": episode / "material_ledger.json",
        "rights_manifest": episode / "rights_manifest.json",
        "cut_decisions": review
        / "jp_pilot01r3_cut_review"
        / "cut_decision_packet.json",
    }
    _write_json(paths["edit_pack"], {"episode_id": "episode_001"})
    _write_json(paths["transcript"], {"segments": []})
    _write_json(paths["material_ledger"], ledger)
    _write_json(paths["rights_manifest"], {"compliance_check": {"status": "pending"}})
    _write_json(paths["cut_decisions"], {"cuts": []})
    timeline = [
        {
            "id": "cut_001",
            "source_start_seconds": 2.453,
            "source_end_seconds": 9.293,
            "sequence_start_seconds": 0.000,
            "sequence_end_seconds": 6.840,
            "transition_in": "sequence_start",
        },
        {
            "id": "cut_002",
            "source_start_seconds": 12.329,
            "source_end_seconds": 17.167,
            "sequence_start_seconds": 6.840,
            "sequence_end_seconds": 11.678,
            "transition_in": "hard_cut",
        },
    ]
    subtitles = [
        {
            "id": subtitle_id,
            "cut_id": cut_id,
            "sequence_start_seconds": start,
            "sequence_end_seconds": end,
            "text": text,
            "source_type": "imported_subtitle_track",
            "source_segment_ids": [f"seg_{index:06d}"],
        }
        for index, (subtitle_id, cut_id, start, end, text) in enumerate(
            SUBTITLES, start=1
        )
    ]
    predecessor = {
        "artifact_id": vsc.EXPECTED_OUT04_ARTIFACT_ID,
        "episode_id": "episode_001",
        "machine_readback": (out04 / "sequence_readback.json")
        .relative_to(tmp_path)
        .as_posix(),
        "ordered_cut_ids": list(vsc.EXPECTED_CUT_IDS),
        "expected_duration_seconds": vsc.EXPECTED_DURATION_SECONDS,
        "timeline": timeline,
        "subtitles": subtitles,
        "render": {
            "output_path": out04_video.relative_to(tmp_path).as_posix(),
            "output_sha256": vsc._sha256(out04_video),
        },
        "input_artifacts": {
            label: {
                "path": path.relative_to(tmp_path).as_posix(),
                "sha256": vsc._sha256(path),
            }
            for label, path in paths.items()
        },
        "materials": {
            "source_video": {"id": "source_video", "sha256": vsc._sha256(source_video)},
            "source_audio": {"id": "source_audio", "sha256": vsc._sha256(source_audio)},
        },
        "boundaries": {"rights_status": "pending"},
    }
    predecessor_path = out04 / "sequence_readback.json"
    _write_json(predecessor_path, predecessor)
    return {
        "root": tmp_path,
        "episode": episode,
        "output": review / "out05_vertical_short_internal_candidate",
        "predecessor": predecessor_path,
        "predecessor_hash": vsc._sha256(predecessor_path),
        "out04_video_hash": vsc._sha256(out04_video),
        "subtitle_hash": vsc._subtitle_semantic_hash(subtitles),
        "source_video": source_video,
    }


def _fake_render(**kwargs) -> dict:
    kwargs["video_path"].write_bytes(b"fake-h264-aac-vertical")
    kwargs["compare_sheet_path"].write_bytes(b"fake-compare-jpeg")
    kwargs["frame_sheet_path"].write_bytes(b"fake-frame-jpeg")
    return {
        "media": {
            "duration_seconds": 11.678,
            "video_codec": "h264",
            "audio_codec": "aac",
            "width": 1080,
            "height": 1920,
            "resolution": "1080x1920",
            "fps": 30.0,
            "stream_counts": {"video": 1, "audio": 1, "other": 0},
            "pixel_format": "yuv420p",
        },
        "selected_video_encoder": "libx264",
        "attempts": [{"video_codec": "libx264", "status": "passed", "exit_code": 0}],
        "duration_matches_expected": True,
        "full_decode": {"status": "passed", "exit_code": 0, "stderr_empty": True},
        "audio": {
            "input_measurement": {"integrated_lufs": -19.22, "true_peak_dbtp": -2.11},
            "decision": "normalize_clear_loudness_gap_to_internal_candidate_target",
            "normalization_applied": True,
            "target": {"integrated_lufs": -14.0, "true_peak_dbtp_max": -1.0},
            "output_measurement": {"integrated_lufs": -14.2, "true_peak_dbtp": -1.4},
        },
        "frame_samples": [{"label": "start", "seconds": 0.25, "status": "extracted"}],
    }


def _build(fixture: dict[str, Path | str], **overrides):
    kwargs = {
        "episode_dir": fixture["episode"],
        "output_dir": fixture["output"],
        "predecessor_readback_path": fixture["predecessor"],
        "base_dir": fixture["root"],
        "render_executor": _fake_render,
        "expected_predecessor_sha256": fixture["predecessor_hash"],
        "expected_predecessor_video_sha256": fixture["out04_video_hash"],
        "expected_subtitle_semantic_sha256": fixture["subtitle_hash"],
    }
    kwargs.update(overrides)
    return vsc.build_vertical_short_candidate(**kwargs)


def test_build_vertical_short_candidate_normal_atomic_package(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    result = _build(fixture)
    output = fixture["output"]
    assert result["artifact_id"] == vsc.ARTIFACT_ID
    assert (output / "assets" / "vertical_short_candidate.mp4").is_file()
    assert (output / "vertical_short_subtitles.ass").is_file()
    assert (output / "vertical_short_subtitles.srt").is_file()
    assert (output / "reframe_plan.json").is_file()
    assert (output / "candidate_readback.json").is_file()
    assert (output / "assets" / "frame_qa_contact_sheet.jpg").is_file()
    assert (output / "index.html").read_text(encoding="utf-8").count("<video ") == 1
    assert result["readback"]["boundaries"]["production_candidate"] is False
    assert result["readback"]["boundaries"]["rights"] == "pending"


def test_atomic_render_failure_preserves_existing_output(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    output = fixture["output"]
    output.mkdir()
    (output / "sentinel.txt").write_text("keep", encoding="utf-8")

    def fail_render(**_kwargs):
        raise RuntimeError("simulated render failure")

    with pytest.raises(RuntimeError, match="simulated render failure"):
        _build(fixture, render_executor=fail_render)
    assert (output / "sentinel.txt").read_text(encoding="utf-8") == "keep"
    assert not list(output.parent.glob(f".{output.name}.staging-*"))


@pytest.mark.parametrize(
    "name",
    ["vertical_candidate", "out05_bad name", "out05_../escape"],
)
def test_output_directory_rejects_unsafe_name(tmp_path: Path, name: str) -> None:
    episode = tmp_path / "episode"
    review = episode / "review"
    review.mkdir(parents=True)
    with pytest.raises(vsc.VerticalShortCandidateError):
        vsc._validate_output_directory(episode, review / name)


def test_output_directory_rejects_traversal(tmp_path: Path) -> None:
    episode = tmp_path / "episode"
    (episode / "review").mkdir(parents=True)
    with pytest.raises(
        vsc.VerticalShortCandidateError, match="direct episode/review child"
    ):
        vsc._validate_output_directory(
            episode, (episode / "review" / ".." / "out05_bad").resolve()
        )


def test_overlap_and_protected_overwrite_are_rejected(tmp_path: Path) -> None:
    protected = (
        tmp_path / "episode" / "review" / "out04_editorial_representative_sequence"
    )
    protected.mkdir(parents=True)
    readback = protected / "sequence_readback.json"
    readback.write_text("{}")
    with pytest.raises(vsc.VerticalShortCandidateError, match="protected"):
        vsc._reject_overlap(protected, readback, "protected overwrite")


def test_subtitle_containment_wrap_and_safe_envelope() -> None:
    predecessor = [
        {
            "id": subtitle_id,
            "cut_id": cut_id,
            "sequence_start_seconds": start,
            "sequence_end_seconds": end,
            "text": text,
            "source_type": "imported_subtitle_track",
            "source_segment_ids": [],
        }
        for subtitle_id, cut_id, start, end, text in SUBTITLES
    ]
    layout, items, _selector = vsc._build_subtitle_presentation(predecessor)
    result = vsc._validate_subtitle_containment(
        items, expected_duration=vsc.EXPECTED_DURATION_SECONDS, layout=layout
    )
    assert result["status"] == "passed"
    assert result["subtitle_count"] == 9
    assert result["maximum_line_count"] <= 3
    assert all(check["estimated_top"] >= 1080 for check in result["checks"])
    assert all(
        item["vertical_balance_readback"].get("short_final_tail") is False
        for item in items
    )


def test_out06_reviewed_japanese_break_hints_are_measured_and_semantic() -> None:
    reviewed = [
        (
            "sub_013",
            "cut_003",
            14.181,
            15.549,
            "なんで来なかったんすか！！",
            ["なんで", "来なかった", "んすか！！"],
        ),
        (
            "sub_014",
            "cut_003",
            15.549,
            16.450,
            "ずっと待ってたんすよ！！",
            ["ずっと", "待ってたんすよ！！"],
        ),
        (
            "sub_019",
            "cut_003",
            21.855,
            23.924,
            "はじめの勝ちってことでいいですね？",
            ["はじめの勝ちって", "ことでいいですね？"],
        ),
        (
            "sub_024",
            "cut_003",
            28.228,
            30.797,
            "団長、ちなみに、他の番長知ってますか？",
            ["団長、ちなみに、", "他の番長", "知ってますか？"],
        ),
        (
            "sub_028",
            "cut_003",
            36.570,
            38.071,
            "マリンならあっちにいたよ",
            ["マリンなら", "あっちにいたよ"],
        ),
        (
            "sub_029",
            "cut_003",
            38.071,
            38.638,
            "ありがとうございますー！",
            ["ありがとう", "ございますー！"],
        ),
    ]
    predecessor = [
        {
            "id": subtitle_id,
            "cut_id": cut_id,
            "sequence_start_seconds": start,
            "sequence_end_seconds": end,
            "text": text,
            "source_type": "imported_subtitle_track",
            "source_segment_ids": [],
        }
        for subtitle_id, cut_id, start, end, text, _expected in reviewed
    ]
    layout, items, _selector = vsc._build_subtitle_presentation(predecessor)
    by_id = {item["subtitle_id"]: item for item in items}
    forbidden = {
        "sub_013": "なんで来|なかったんすか！！",
        "sub_014": "ずっと待|ってたんすよ！！",
        "sub_019": "はじめの勝ちってこ|とでいいですね？",
        "sub_024": "他の番長知|ってますか？",
        "sub_028": "マリン|ならあっちにいたよ",
        "sub_029": "ありがとうご|ざいますー！",
    }
    for subtitle_id, _cut_id, _start, _end, text, expected_lines in reviewed:
        item = by_id[subtitle_id]
        assert "".join(item["wrapped_lines"]) == text
        assert item["wrapped_lines"] == expected_lines
        assert "|".join(item["wrapped_lines"]) != forbidden[subtitle_id]
        assert item["wrapped_line_count"] <= 3
        assert item["vertical_balance_readback"]["line_break_hint"]["status"] == (
            "applied_preferred_lines"
        )
    result = vsc._validate_subtitle_containment(
        items, expected_duration=38.638, layout=layout, expected_count=6
    )
    assert result["status"] == "passed"


def test_subtitle_outside_candidate_is_rejected() -> None:
    predecessor = [
        {
            "id": subtitle_id,
            "cut_id": cut_id,
            "sequence_start_seconds": start,
            "sequence_end_seconds": end,
            "text": text,
            "source_type": "imported_subtitle_track",
            "source_segment_ids": [],
        }
        for subtitle_id, cut_id, start, end, text in SUBTITLES
    ]
    layout, items, _selector = vsc._build_subtitle_presentation(predecessor)
    items[-1]["display_end_seconds"] = 12.5
    with pytest.raises(vsc.VerticalShortCandidateError, match="outside candidate"):
        vsc._validate_subtitle_containment(
            items, expected_duration=vsc.EXPECTED_DURATION_SECONDS, layout=layout
        )


def test_ass_utf8_escaping_and_no_visible_placeholder(tmp_path: Path) -> None:
    assert _ass_text("日本語{字幕}\\path\n次") == "日本語\\{字幕\\}\\\\path\\N次"
    fixture = _fixture(tmp_path)
    _build(fixture)
    ass = (fixture["output"] / "vertical_short_subtitles.ass").read_text(
        encoding="utf-8"
    )
    events = [line for line in ass.splitlines() if line.startswith("Dialogue:")]
    assert len(events) == 9
    assert all(
        "SPK" not in line and "DIAGNOSTIC" not in line.upper() for line in events
    )
    assert "もしもし？" in ass


def test_font_fallback_status_is_read_back(monkeypatch: pytest.MonkeyPatch) -> None:
    original = vsc._diagnostic_ass_style_for_candidate(vsc.ED10L_KEIFONT_CANDIDATE_ID)
    fallback = {
        **original,
        "resolved_font_file": None,
        "font_file_status": "test_fallback",
    }
    monkeypatch.setattr(
        vsc, "_diagnostic_ass_style_for_candidate", lambda _candidate: fallback
    )
    predecessor = [
        {
            "id": subtitle_id,
            "cut_id": cut_id,
            "sequence_start_seconds": start,
            "sequence_end_seconds": end,
            "text": text,
            "source_type": "imported_subtitle_track",
            "source_segment_ids": [],
        }
        for subtitle_id, cut_id, start, end, text in SUBTITLES
    ]
    layout, _items, _selector = vsc._build_subtitle_presentation(predecessor)
    assert layout["diagnostic_ass_style"]["font_file_status"] == "test_fallback"


def test_reframe_plan_validation_and_full_fit_selection() -> None:
    plan = vsc._build_reframe_plan(
        {
            "ordered_cut_ids": list(vsc.EXPECTED_CUT_IDS),
            "expected_duration_seconds": vsc.EXPECTED_DURATION_SECONDS,
        }
    )
    vsc._validate_reframe_plan(plan)
    assert plan["selected_option"] == vsc.SELECTED_REFRAME
    assert (
        plan["comparison_scope"]
        == "still_frame_specimens_only_no_three_full_video_renders"
    )
    plan["timeline_preserved"]["new_cut_added"] = True
    with pytest.raises(vsc.VerticalShortCandidateError, match="must not add cuts"):
        vsc._validate_reframe_plan(plan)


def test_source_material_hash_mutation_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    fixture["source_video"].write_bytes(b"mutated-source")
    with pytest.raises(vsc.VerticalShortCandidateError, match="material hash mismatch"):
        _build(fixture)


def test_predecessor_subtitle_semantic_hash_detects_change() -> None:
    items = [
        {
            "id": subtitle_id,
            "sequence_start_seconds": start,
            "sequence_end_seconds": end,
            "text": text,
        }
        for subtitle_id, _cut_id, start, end, text in SUBTITLES
    ]
    baseline = vsc._subtitle_semantic_hash(items)
    items[-1]["text"] += "変更"
    assert vsc._subtitle_semantic_hash(items) != baseline


def test_render_validation_rejects_true_peak(tmp_path: Path) -> None:
    path = tmp_path / "candidate.mp4"
    result = _fake_render(
        video_path=path,
        compare_sheet_path=tmp_path / "compare.jpg",
        frame_sheet_path=tmp_path / "frames.jpg",
    )
    result["audio"]["output_measurement"]["true_peak_dbtp"] = -0.9
    with pytest.raises(vsc.VerticalShortCandidateError, match="true peak"):
        vsc._validate_render_result(result, video_path=path)
