from __future__ import annotations

from pathlib import Path

from src.integrations.render.push_microarc_editorial_v3 import (
    ARTIFACT_ID,
    DESIGN_SIGNATURE,
    LAUGHTER_EVENTS,
    QUOTE_SPECS,
    SEGMENTATION_GROUP_SPECS,
    TRANSITION_SPECS,
    _motion_offsets,
    _protected_boundary_hits,
    _safe_two_line_wrap,
    build_caption_event_ledger,
    render_filter_complex,
)


def _caption(caption_id: str, start: float, end: float, text: str) -> dict:
    return {
        "caption_id": caption_id,
        "cut_id": "out14_v2_cut_001",
        "output_start_seconds": start,
        "output_end_seconds": end,
        "text": text,
        "word_timed_chunk": True,
    }


def _presentation(caption_id: str, start: float, end: float) -> dict:
    return {
        "subtitle_id": caption_id,
        "display_start_seconds": start,
        "display_end_seconds": end,
        "wrapped_lines": ["placeholder"],
    }


def test_known_within_word_split_is_repaired_at_word_boundary() -> None:
    readback = {
        "cue_count": 2,
        "items": [
            _caption("speech_0003", 7.98, 12.64, "Discordってさああのーなん"),
            _caption("speech_0004", 12.64, 15.04, "か最近プロフィール装飾できるんよ"),
        ],
    }
    presentation = {
        "items": [
            _presentation("speech_0003", 7.98, 12.64),
            _presentation("speech_0004", 12.64, 15.04),
        ]
    }
    result = build_caption_event_ledger(readback, presentation)
    assert result["within_word_split_count"] == 0
    assert result["items"][0]["display_text"].endswith("なんか")
    assert result["items"][0]["display_end_seconds"] == 12.72
    assert result["items"][1]["display_start_seconds"] == 12.72
    assert result["changed_timing_p95_absolute_ms"] == 80
    assert result["changed_timing_median_ms"] == 80


def test_full_ledger_segmentation_model_covers_multiple_sections() -> None:
    grouped_ids = {
        caption_id
        for spec in SEGMENTATION_GROUP_SPECS
        for caption_id in spec["caption_ids"]
    }
    assert len(SEGMENTATION_GROUP_SPECS) >= 20
    assert {"speech_0005", "speech_0075", "speech_0139"} <= grouped_ids
    assert _protected_boundary_hits("レッドカ", "ード持ってる") == ["レッドカード"]
    assert _protected_boundary_hits("話を聞", "いてたら") == ["聞いてたら"]


def test_phrase_aware_wrap_uses_at_most_two_safe_lines() -> None:
    lines = _safe_two_line_wrap(
        "なんかレッドカード持ってるから、こいつ本当にそう思ってるかみたい"
    )
    assert len(lines) == 2
    assert not _protected_boundary_hits(lines[0], lines[1])
    assert not lines[1].startswith(("、", "。", "ゃ", "ゅ", "ょ", "っ", "ー"))


def test_full_audit_group_removes_midword_boundary_without_timing_drift() -> None:
    result = build_caption_event_ledger(
        {
            "cue_count": 2,
            "items": [
                _caption("speech_0009", 27.57, 30.45, "結構気に入って使っててでも結構長"),
                _caption("speech_0010", 30.45, 31.47, "いこと使ってたから"),
            ],
        },
        {
            "items": [
                _presentation("speech_0009", 27.57, 30.45),
                _presentation("speech_0010", 30.45, 31.47),
            ]
        },
    )
    assert result["cue_count"] == 1
    assert result["merged_internal_boundary_count"] == 1
    assert result["within_word_split_count"] == 0
    assert result["items"][0]["caption_ids"] == ["speech_0009", "speech_0010"]
    assert result["items"][0]["display_start_seconds"] == 27.57
    assert result["items"][0]["display_end_seconds"] == 31.47


def test_verified_quote_has_identity_evidence_and_distinct_style() -> None:
    caption_id = "speech_0018"
    result = build_caption_event_ledger(
        {"cue_count": 1, "items": [_caption(caption_id, 48.02, 50.28, "僕がいいの選んであげるよとか言い")]},
        {"items": [_presentation(caption_id, 48.02, 50.28)]},
    )
    row = result["items"][0]
    assert row["quoted_identity"] == "猫又おかゆ"
    assert row["speech_role"] == "quoted_verbatim"
    assert row["style_role"] != "normal_speech"
    assert row["evidence"]
    assert result["quoted_distinct_treatment_coverage"] == 1.0


def test_paraphrase_is_not_styled_as_verified_member_speech() -> None:
    result = build_caption_event_ledger(
        {"cue_count": 1, "items": [_caption("speech_0040", 116.6, 118.98, "これに関してご意見ありますか")]},
        {"items": [_presentation("speech_0040", 116.6, 118.98)]},
    )
    row = result["items"][0]
    assert row["speech_role"] == "paraphrase"
    assert row["quoted_identity"] is None
    assert row["style_role"] == "normal_speech"


def test_strong_laughter_motion_is_deterministic_and_bounded() -> None:
    seed = next(row["motion_seed"] for row in LAUGHTER_EVENTS if row["motion_seed"])
    first = _motion_offsets(seed)
    second = _motion_offsets(seed)
    assert first == second
    assert all(-4 <= x <= 4 and -4 <= y <= 4 for _, x, y in first)


def test_transition_contract_covers_all_eight_cut_starts_and_material_bridges() -> None:
    assert len(TRANSITION_SPECS) == 8
    assert {row["transition_id"] for row in TRANSITION_SPECS} == {
        f"transition_{index:03d}" for index in range(1, 9)
    }
    material = {
        row["transition_id"]: row
        for row in TRANSITION_SPECS
        if row["transition_id"] in {"transition_004", "transition_008"}
    }
    assert material["transition_004"]["visual"] == "cyan_directional_bridge"
    assert material["transition_008"]["visual"] == "source_anchored_explanation_panel"
    assert "black" not in material["transition_008"]["visual"]


def test_filter_preserves_cut_durations_and_adds_audio_microfades(tmp_path: Path) -> None:
    cuts = [
        {"source_in_seconds": 8.45, "source_out_seconds": 58.73},
        {"source_in_seconds": 124.89, "source_out_seconds": 189.77},
    ]
    ass = tmp_path / "presentation.ass"
    ass.write_text("", encoding="utf-8")
    font = tmp_path / "font.ttf"
    font.write_bytes(b"font")
    value = render_filter_complex(
        cuts=cuts,
        ass_path=ass,
        font_file=font,
        output_width=1920,
        output_height=1080,
    )
    assert "concat=n=2:v=1:a=1" in value
    assert value.count("afade=t=in") == 2
    assert "scale=1920:1080" in value


def test_contract_identities_are_stable() -> None:
    assert ARTIFACT_ID == "clip-out14-push-microarc-editorial-v3-001"
    assert DESIGN_SIGNATURE == "CPG-OUT14-V3-DIRSIG-20260727-A"
    assert len(QUOTE_SPECS) == 5
