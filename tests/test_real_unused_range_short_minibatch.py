from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import build_real_unused_range_short_minibatch as batch_cli
from src.integrations.render import real_unused_range_short_minibatch as batch


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path) -> dict[str, Path | str]:
    root = tmp_path
    episode = root / "episodes" / batch.EPISODE_ID
    review = episode / "review"
    source_video = (
        episode / "materials" / batch.SOURCE_VIDEO_MATERIAL_ID / "source_video.mp4"
    )
    source_audio = episode / "materials" / batch.SOURCE_AUDIO_MATERIAL_ID / "source.wav"
    source_video.parent.mkdir(parents=True)
    source_audio.parent.mkdir(parents=True)
    source_video.write_bytes(b"out08-source-video")
    source_audio.write_bytes(b"out08-source-audio")

    cut_ranges = {
        "cut_001": (2.453, 9.293),
        "cut_002": (12.329, 17.167),
        "cut_003": (22.606, 49.566),
        "cut_004": (50.868, 60.277),
        "cut_005": (60.277, 79.163),
        "cut_006": (79.163, 98.315),
        "cut_007": (98.315, 116.467),
        "cut_008": (116.934, 135.219),
        "cut_009": (135.219, 144.000),
    }
    cuts = [
        {
            "id": cut_id,
            "start_seconds": start,
            "end_seconds": end,
            "context_check": {
                "status": "needs_review" if cut_id >= "cut_003" else "passed"
            },
        }
        for cut_id, (start, end) in cut_ranges.items()
    ]
    subtitle_specs = (
        ("sub_030", "cut_004", 50.868, 55.000),
        ("sub_034", "cut_004", 55.000, 60.277),
        ("sub_035", "cut_005", 60.277, 70.000),
        ("sub_047", "cut_005", 70.000, 79.163),
        ("sub_048", "cut_006", 81.298, 89.000),
        ("sub_059", "cut_006", 89.000, 98.315),
        ("sub_060", "cut_007", 98.315, 107.000),
        ("sub_068", "cut_007", 107.000, 116.467),
        ("sub_069", "cut_008", 116.934, 126.000),
        ("sub_101", "cut_008", 126.000, 135.219),
        ("sub_102", "cut_009", 137.054, 138.055),
    )
    subtitles = []
    segments = []
    for subtitle_id, cut_id, start, end in subtitle_specs:
        number = int(subtitle_id.split("_")[1])
        segment_id = f"seg_{number:06d}"
        text = f"候補字幕{number}"
        subtitles.append(
            {
                "id": subtitle_id,
                "cut_id": cut_id,
                "start_seconds": start,
                "end_seconds": end,
                "text": text,
                "source_type": "imported_subtitle_track",
                "source_segment_ids": [segment_id],
            }
        )
        segments.append(
            {
                "id": segment_id,
                "start_seconds": start,
                "end_seconds": end,
                "text": text,
                "review_status": "accepted",
            }
        )
    _write_json(
        episode / "edit_pack.json",
        {
            "episode_id": batch.EPISODE_ID,
            "cut_candidates": cuts,
            "subtitles": subtitles,
        },
    )
    _write_json(
        episode / "transcript.json",
        {
            "stt": {
                "engine": "subtitle_track",
                "provider": "youtube_subtitles",
                "real_transcript": True,
            },
            "review": {"status": "accepted"},
            "segments": segments,
        },
    )
    video_relative = source_video.relative_to(root).as_posix()
    audio_relative = source_audio.relative_to(root).as_posix()
    _write_json(
        episode / "material_ledger.json",
        {
            "materials": [
                {
                    "id": batch.SOURCE_VIDEO_MATERIAL_ID,
                    "kind": "source_video",
                    "registered_by": "tool:asset_fetch_local_video",
                    "file_path": video_relative,
                    "hash_sha256": batch._sha256(source_video),
                },
                {
                    "id": batch.SOURCE_AUDIO_MATERIAL_ID,
                    "kind": "source_audio",
                    "registered_by": "tool:asset_fetch_local_audio",
                    "file_path": audio_relative,
                    "hash_sha256": batch._sha256(source_audio),
                },
            ]
        },
    )
    _write_json(
        episode / "rights_manifest.json",
        {
            "source_video": {"url": batch.SOURCE_URL},
            "compliance_check": {"status": "pending"},
        },
    )
    caption = episode / batch.CAPTION_RELATIVE
    _write_json(caption, {"events": [{"tStartMs": 0, "segs": [{"utf8": "fixture"}]}]})
    decisions = [
        {
            "cut_id": cut_id,
            "final_cut_decision": "reject"
            if cut_id == "cut_009"
            else "needs_adjustment",
            "context_status": "needs_review",
            "decision_reason": (
                "Standalone fragment rejected; better treated as dependent payoff"
                if cut_id == "cut_009"
                else "usable after bounded range planning"
            ),
        }
        for cut_id in (*batch.ELIGIBLE_CUT_IDS, "cut_009")
    ]
    _write_json(
        episode / batch.DECISION_RELATIVE,
        {
            "episode_id": batch.EPISODE_ID,
            "source_identity": {
                "youtube_id": batch.SOURCE_PROVIDER_ID,
                "source_video_material_id": batch.SOURCE_VIDEO_MATERIAL_ID,
                "subtitle_track": (episode / batch.CAPTION_RELATIVE)
                .relative_to(root)
                .as_posix(),
            },
            "decisions": decisions,
        },
    )
    _write_json(
        episode / batch.BOUNDARY_RELATIVE,
        {
            "schema_version": "v1",
            "artifact_kind": "cut_boundary_recommendation_report_v0",
            "episode_id": batch.EPISODE_ID,
            "recommendation": {
                "cut_id": "cut_003",
                "recommended_start_seconds": 22.606,
                "recommended_end_seconds": 49.566,
            },
        },
    )
    plan = review / "out08_candidate_plan_input.json"
    _write_json(
        plan,
        {
            "schema_version": "clippipegen.out08.candidate_plan_input.v0",
            "episode_id": batch.EPISODE_ID,
            "source_id": batch.SOURCE_PROVIDER_ID,
            "candidates": [
                {
                    "candidate_id": "candidate_01",
                    "rationale": "cut_004 と cut_005 を一つの展開として確認する。",
                    "narrative_arc": {
                        "setup": "cut_004 で次の話題を提示",
                        "development": "cut_005 で展開",
                        "payoff": "cut_005 末尾で一区切り",
                    },
                    "ranges": [
                        {
                            "source_start_seconds": 50.868,
                            "source_end_seconds": 79.163,
                            "authority_cut_ids": ["cut_004", "cut_005"],
                            "boundary_basis": "cut_authority",
                        }
                    ],
                },
                {
                    "candidate_id": "candidate_02",
                    "rationale": "挨拶から勝利の dependent payoff までを確認する。",
                    "narrative_arc": {
                        "setup": "cut_006 後半の挨拶",
                        "development": "cut_007 と cut_008",
                        "payoff": "sub_102 の勝利だけを dependent payoff として使用",
                    },
                    "ranges": [
                        {
                            "source_start_seconds": 81.298,
                            "source_end_seconds": 98.315,
                            "authority_cut_ids": ["cut_006"],
                            "boundary_basis": "subtitle_aligned_derivation",
                        },
                        {
                            "source_start_seconds": 98.315,
                            "source_end_seconds": 116.467,
                            "authority_cut_ids": ["cut_007"],
                            "boundary_basis": "cut_authority",
                        },
                        {
                            "source_start_seconds": 116.934,
                            "source_end_seconds": 135.219,
                            "authority_cut_ids": ["cut_008"],
                            "boundary_basis": "cut_authority",
                        },
                        {
                            "source_start_seconds": 137.054,
                            "source_end_seconds": 138.055,
                            "authority_cut_ids": ["cut_009"],
                            "boundary_basis": "dependent_payoff_subtitle",
                            "dependent_payoff_only": True,
                        },
                    ],
                },
            ],
        },
    )
    return {
        "root": root,
        "episode": episode,
        "output": review / "out08_real_unused_range_short_minibatch",
        "plan": plan,
        "source_audio": source_audio,
        "source_hash": batch._sha256(source_video),
        "audio_hash": batch._sha256(source_audio),
        "caption_hash": batch._sha256(caption),
    }


def _fake_render(**kwargs) -> dict:
    video = Path(kwargs["video_path"])
    frame_sheet = Path(kwargs["frame_sheet_path"])
    video.write_bytes(f"video:{video.stem}".encode())
    frame_sheet.write_bytes(f"frames:{video.stem}".encode())
    duration = float(kwargs["expected_duration"])
    return {
        "media": {
            "video_codec": "h264",
            "audio_codec": "aac",
            "width": 1080,
            "height": 1920,
            "fps": 30.0,
            "duration_seconds": duration,
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
            for label, seconds in kwargs["frame_samples"]
        ],
    }


def _fake_navigation(**kwargs) -> dict:
    Path(kwargs["output_path"]).write_bytes(b"navigation")
    return {
        "status": "passed",
        "source": "final_candidate_frame",
        "seconds": kwargs["seconds"],
    }


def _build(fixture: dict[str, Path | str], **overrides):
    args = {
        "episode_dir": fixture["episode"],
        "output_dir": fixture["output"],
        "candidate_plan_input_path": fixture["plan"],
        "base_dir": fixture["root"],
        "render_executor": _fake_render,
        "navigation_executor": _fake_navigation,
        "expected_source_video_sha256": fixture["source_hash"],
        "expected_source_audio_sha256": fixture["audio_hash"],
        "expected_caption_sha256": fixture["caption_hash"],
    }
    args.update(overrides)
    return batch.build_real_unused_range_short_minibatch(**args)


def test_build_two_candidate_atomic_package_and_manifest(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    result = _build(fixture)
    output = Path(fixture["output"])
    readback = result["readback"]
    assert readback["target_candidate_count"] == 2
    assert readback["actual_candidate_count"] == 2
    assert [item["semantic_duration_seconds"] for item in readback["candidates"]] == [
        28.295,
        54.455,
    ]
    assert readback["candidates"][1]["dependent_payoff_sub102_consumed"] is True
    assert readback["boundaries"]["cut009_final_cut_decision"] == "reject"
    for candidate in readback["candidates"]:
        navigation = candidate["navigation_frame"]
        assert navigation["role"] == "navigation_only"
        assert navigation["human_thumbnail_review_required"] is False
        assert navigation["thumbnail_acceptance_claimed"] is False

    html = (output / "index.html").read_text(encoding="utf-8")
    assert html.count("<video ") == 2
    assert html.count(batch.REVIEW_QUESTION) == 1
    assert "grid-template" not in html
    assert str(fixture["root"]) not in html
    serve_script = (output / "serve_preview.ps1").read_text(encoding="utf-8")
    assert "..\\..\\..\\.." in serve_script
    assert "Push-Location $repoRoot" in serve_script

    manifest = json.loads((output / "batch_manifest.json").read_text(encoding="utf-8"))
    actual_payloads = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and path.name != "batch_manifest.json"
    }
    assert {
        item["package_relative_path"] for item in manifest["files"]
    } == actual_payloads
    for item in manifest["files"]:
        assert batch._sha256(output / item["package_relative_path"]) == item["sha256"]
    assert manifest["manifest_self_integrity"][
        "sha256"
    ] == batch._canonical_manifest_self_hash(manifest)
    for path in output.glob("*.json"):
        assert str(fixture["root"]) not in path.read_text(encoding="utf-8")


def test_used_range_is_rejected_before_render(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    edit_path = Path(fixture["episode"]) / "edit_pack.json"
    edit = json.loads(edit_path.read_text(encoding="utf-8"))
    cut4 = next(item for item in edit["cut_candidates"] if item["id"] == "cut_004")
    cut4["start_seconds"] = 5.0
    cut4["end_seconds"] = 8.0
    _write_json(edit_path, edit)
    plan_path = Path(fixture["plan"])
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["candidates"] = [plan["candidates"][0]]
    plan["candidates"][0]["ranges"] = [
        {
            "source_start_seconds": 5.0,
            "source_end_seconds": 79.163,
            "authority_cut_ids": ["cut_004", "cut_005"],
            "boundary_basis": "cut_authority",
        }
    ]
    _write_json(plan_path, plan)
    called = False

    def renderer(**_kwargs):
        nonlocal called
        called = True
        return {}

    with pytest.raises(batch.RealUnusedRangeShortMinibatchError, match="used range"):
        _build(fixture, render_executor=renderer)
    assert called is False
    assert not Path(fixture["output"]).exists()


def test_source_audio_fixed_hash_rejects_coordinated_ledger_replacement(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    source_audio = Path(fixture["source_audio"])
    source_audio.write_bytes(b"coordinated-audio-replacement")
    ledger_path = Path(fixture["episode"]) / "material_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    audio = next(
        item
        for item in ledger["materials"]
        if item["id"] == batch.SOURCE_AUDIO_MATERIAL_ID
    )
    audio["hash_sha256"] = batch._sha256(source_audio)
    _write_json(ledger_path, ledger)

    with pytest.raises(
        batch.RealUnusedRangeShortMinibatchError,
        match="source audio SHA-256 changed",
    ):
        _build(fixture)
    assert not Path(fixture["output"]).exists()


def test_non_dependent_cut009_use_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan_path = Path(fixture["plan"])
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["candidates"] = [plan["candidates"][0]]
    plan["candidates"][0]["ranges"] = [
        {
            "source_start_seconds": 135.219,
            "source_end_seconds": 144.0,
            "authority_cut_ids": ["cut_009"],
            "boundary_basis": "cut_authority",
        }
    ]
    _write_json(plan_path, plan)
    with pytest.raises(
        batch.RealUnusedRangeShortMinibatchError, match="cut_004..cut_008"
    ):
        _build(fixture)
    assert not Path(fixture["output"]).exists()


def test_second_render_failure_preserves_existing_package(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    output = Path(fixture["output"])
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("existing", encoding="utf-8")
    count = 0

    def fail_second(**kwargs):
        nonlocal count
        count += 1
        if count == 2:
            raise batch.RealUnusedRangeShortMinibatchError(
                "fixture second render failure"
            )
        return _fake_render(**kwargs)

    with pytest.raises(
        batch.RealUnusedRangeShortMinibatchError, match="second render failure"
    ):
        _build(fixture, render_executor=fail_second)
    assert marker.read_text(encoding="utf-8") == "existing"
    assert not list(output.parent.glob(f".{output.name}.staging-*"))


def test_out08_reviewed_wrap_repairs_preserve_source_text() -> None:
    samples = (
        ("sub_038", "お店屋さんごっこかな～？😄", ["お店屋さん", "ごっこかな～？😄"]),
        ("sub_045", "ありがとうございました～！", ["ありがとう", "ございました～！"]),
        (
            "sub_061",
            "こんなゾクゾクするバトルは 久しぶりだ…！",
            ["こんなゾクゾクする", "バトルは", "久しぶりだ…！"],
        ),
        ("sub_063", "番長の血がよぉぉぉーーー！！！", ["番長の血が", "よぉぉぉーーー！！！"]),
        (
            "sub_064",
            "はじめ様がなんか ホニャホニャ言ってる…",
            ["はじめ様がなんか", "ホニャホニャ", "言ってる…"],
        ),
        (
            "sub_067",
            "そして、さっきのはじめちゃんの 特殊なイントネーションが",
            ["そして、さっきの", "はじめちゃんの特殊", "なイントネーションが"],
        ),
        ("sub_096", "下界ニ呼ビ出シタノハキサマカ。", ["下界ニ呼ビ出シタ", "ノハキサマカ。"]),
        ("sub_098", "はじめはリグロスの番長！", ["はじめは", "リグロスの番長！"]),
    )
    semantic = [
        {
            "id": subtitle_id,
            "cut_id": "cut_008",
            "sequence_start_seconds": float(index),
            "sequence_end_seconds": float(index + 1),
            "text": text,
            "source_type": "imported_subtitle_track",
            "source_segment_ids": [f"seg_{index:06d}"],
        }
        for index, (subtitle_id, text, _lines) in enumerate(samples)
    ]

    _layout, items, _selector = batch._build_out08_subtitle_presentation(semantic)
    by_id = {item["subtitle_id"]: item for item in items}
    for subtitle_id, source_text, expected_lines in samples:
        item = by_id[subtitle_id]
        assert item["source_text"] == source_text
        assert item["wrapped_lines"] == expected_lines, item[
            "vertical_balance_readback"
        ]
        assert item["vertical_balance_readback"]["line_break_hint"]["status"] == (
            "applied_preferred_lines"
        )


def test_cli_converts_shared_render_error_to_controlled_exit(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_build(**_kwargs):
        raise batch.VerticalShortCandidateError("fixture probe failure")

    monkeypatch.setattr(
        batch_cli,
        "build_real_unused_range_short_minibatch",
        fail_build,
    )
    exit_code = batch_cli.run(
        [
            "--episode-dir",
            "episode",
            "--output-dir",
            "output",
            "--candidate-plan-input",
            "plan.json",
        ]
    )

    assert exit_code == 2
    assert "fixture probe failure" in capsys.readouterr().err
