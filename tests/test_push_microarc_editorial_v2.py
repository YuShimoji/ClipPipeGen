from __future__ import annotations

import pytest

from src.integrations.render.push_microarc_editorial_v2 import (
    KNOWN_V1_LOCI,
    PushMicroarcEditorialV2Error,
    _reuse_completed_render_for_validation_retry,
    build_timeline,
    build_timing_readback,
    remap_canonical_transcript,
    strip_non_speech_annotations,
    validate_candidate_selection,
    validate_v1_human_decision,
)

CUTS = [
    [2276.48, 2326.76],
    [2392.92, 2457.8],
    [2468.88, 2521.44],
    [2556.2, 2632.48],
    [2645.2, 2737.28],
    [2775.4, 2806.0],
    [2841.24, 2861.0],
    [2886.32, 2905.04],
]


def _selection() -> dict:
    score = {
        "narrative_completeness": 20,
        "punchline_payoff_clarity": 15,
        "opening_hook_comprehension": 10,
        "beat_density": 9,
        "title_to_content_congruence": 10,
        "thumbnail_articulability": 9,
        "observed_demand_corroboration": 7,
        "differentiation_editorial_whitespace": 8,
        "transcript_media_feasibility": 5,
        "total": 93,
    }
    candidates = [
        {
            "candidate_id": "C3",
            "hard_gates": "passed",
            "disposition": "selected",
            "score": score,
            "planned_cuts_seconds": CUTS,
        }
    ]
    candidates.extend(
        {
            "candidate_id": f"C{index}",
            "hard_gates": "passed",
            "disposition": "not_selected",
        }
        for index in (1, 2, 4, 5, 6)
    )
    return {
        "selection_policy": {
            "score_weights": {
                "narrative_completeness": 20,
                "punchline_payoff_clarity": 15,
                "opening_hook_comprehension": 10,
                "beat_density": 10,
                "title_to_content_congruence": 10,
                "thumbnail_articulability": 10,
                "observed_demand_corroboration": 10,
                "differentiation_editorial_whitespace": 10,
                "transcript_media_feasibility": 5,
            }
        },
        "stream_identities": [{"stream_id": str(index)} for index in range(3)],
        "candidates": candidates,
        "winner": {"candidate_id": "C3"},
    }


def test_candidate_pool_gate_and_current_source_exclusion_are_enforced() -> None:
    result = validate_candidate_selection(_selection())
    assert result["stream_identity_count"] == 3
    assert result["episode_candidate_count"] == 6
    assert result["winner_score"] == 93
    assert result["planned_cut_count"] == 8
    assert result["v1_overlap_seconds"] == 0
    assert result["v1_excluded_fraction"] == 1.0


def test_rejected_v1_contiguous_span_cannot_pass_as_v2() -> None:
    payload = _selection()
    winner = payload["candidates"][0]
    winner["planned_cuts_seconds"] = [[786.36, 1487.52]]
    with pytest.raises(PushMicroarcEditorialV2Error):
        validate_candidate_selection(payload)


def test_candidate_selection_rejects_a_mutated_score_rubric() -> None:
    payload = _selection()
    payload["selection_policy"]["score_weights"]["beat_density"] = 11
    with pytest.raises(PushMicroarcEditorialV2Error):
        validate_candidate_selection(payload)


def test_v1_decision_requires_rejection_and_active_quarantine() -> None:
    payload = {
        "record_mode": "append_only_events",
        "artifact_id": "clip-out14-push-microarc-stream-v1-001",
        "v1_final_video_sha256": (
            "1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f"
        ),
        "events": [
            {
                "editorial_dimension": {
                    "status": "rejected",
                    "canonical": False,
                    "default_candidate": False,
                    "release_candidate": False,
                    "unmentioned_regions": "not_accepted",
                }
            }
        ],
        "quarantine": {
            "quarantine_id": "out14-contiguous-auto-caption-unstructured-v1",
            "status": "ACTIVE",
            "cosmetic_fix_is_not_escape": True,
        },
    }
    assert validate_v1_human_decision(payload)["status"] == "passed"
    payload["events"][0]["editorial_dimension"]["status"] = "accepted"
    with pytest.raises(PushMicroarcEditorialV2Error):
        validate_v1_human_decision(payload)


def test_non_speech_annotations_are_removed_without_removing_speech() -> None:
    value = strip_non_speech_annotations(
        "これでさ、[笑い][息をのむ音] めちゃめちゃ笑ってて"
    )
    assert value == "これでさ、 めちゃめちゃ笑ってて"
    assert "[笑い]" not in value
    assert "[息をのむ音]" not in value


def test_absolute_provider_times_map_to_trimmed_hd_source_and_output() -> None:
    timeline = build_timeline(
        _selection(),
        source_identity="youtube:rltNvZ_FY8Q",
        source_sha256="a" * 64,
        source_duration_seconds=642.0,
        source_media_offset_seconds=2268.0,
    )
    assert timeline["cuts"][0]["provider_source_in_seconds"] == 2276.48
    assert timeline["cuts"][0]["source_in_seconds"] == 8.48
    assert timeline["cuts"][0]["output_in_seconds"] == 0
    assert timeline["output_duration_seconds"] == pytest.approx(405.16)
    assert all(
        float(locus["source_out_seconds"])
        < float(timeline["cuts"][0]["provider_source_in_seconds"])
        for locus in KNOWN_V1_LOCI
    )


def test_canonical_speech_mapping_filters_annotations_and_uses_provider_clock() -> None:
    timeline = build_timeline(
        _selection(),
        source_identity="youtube:rltNvZ_FY8Q",
        source_sha256="a" * 64,
        source_duration_seconds=642.0,
        source_media_offset_seconds=2268.0,
    )
    transcript = {
        "segments": [
            {
                "segment_id": "canonical_001",
                "source_start_seconds": 2277.0,
                "source_end_seconds": 2280.0,
                "text": "Discordってさ、使ってる？[息をのむ音]",
                "confidence": 0.9,
            }
        ]
    }
    rows = remap_canonical_transcript(transcript, timeline)
    assert rows[0]["source_start_seconds"] == 2277.0
    assert rows[0]["media_start_seconds"] == 9.0
    assert rows[0]["output_start_seconds"] == pytest.approx(0.52)
    assert rows[0]["text"] == "Discordってさ、使ってる？"


def test_word_timing_remap_excludes_unheard_boundary_words_and_chunks_long_cues() -> None:
    timeline = build_timeline(
        _selection(),
        source_identity="youtube:rltNvZ_FY8Q",
        source_sha256="a" * 64,
        source_duration_seconds=642.0,
        source_media_offset_seconds=2268.03,
    )
    transcript = {
        "segments": [
            {
                "segment_id": "canonical_boundary",
                "source_start_seconds": 2275.0,
                "source_end_seconds": 2284.0,
                "text": "聞こえない前置き ディスコードってさ使ってる 聞こえない後半",
                "confidence": 0.9,
                "words": [
                    {
                        "source_start_seconds": 2275.0,
                        "source_end_seconds": 2276.2,
                        "text": "聞こえない前置き",
                    },
                    {
                        "source_start_seconds": 2276.6,
                        "source_end_seconds": 2276.8,
                        "text": "ディ",
                    },
                    {
                        "source_start_seconds": 2276.8,
                        "source_end_seconds": 2277.0,
                        "text": "ス",
                    },
                    {
                        "source_start_seconds": 2277.0,
                        "source_end_seconds": 2277.4,
                        "text": "コード",
                    },
                    {
                        "source_start_seconds": 2277.4,
                        "source_end_seconds": 2278.0,
                        "text": "ってさ",
                    },
                    {
                        "source_start_seconds": 2278.0,
                        "source_end_seconds": 2278.8,
                        "text": "使ってる",
                    },
                    {
                        "source_start_seconds": 2327.0,
                        "source_end_seconds": 2328.0,
                        "text": "聞こえない後半",
                    },
                ],
            }
        ]
    }
    rows = remap_canonical_transcript(transcript, timeline)
    assert len(rows) == 1
    assert rows[0]["source_start_seconds"] == 2276.6
    assert rows[0]["media_start_seconds"] == pytest.approx(8.57)
    assert rows[0]["text"] == "Discordってさ使ってる"
    assert rows[0]["word_timed_chunk"] is True


def test_long_prefix_cannot_split_discord_inside_the_lexical_unit() -> None:
    timeline = build_timeline(
        _selection(),
        source_identity="youtube:rltNvZ_FY8Q",
        source_sha256="a" * 64,
        source_duration_seconds=642.0,
        source_media_offset_seconds=2268.03,
    )
    transcript = {
        "segments": [
            {
                "segment_id": "canonical_discord",
                "source_start_seconds": 2276.48,
                "source_end_seconds": 2281.0,
                "text": "ちょあのさあみんなさあDiscordってさあ使ってる",
                "confidence": 0.9,
                "words": [
                    {
                        "source_start_seconds": 2276.48 + index * 0.2,
                        "source_end_seconds": 2276.68 + index * 0.2,
                        "text": text,
                    }
                    for index, text in enumerate(
                        ("ちょ", "あの", "さあ", "みんな", "さあ", "デ", "ス", "コード", "って", "さあ", "使ってる")
                    )
                ],
            }
        ]
    }
    rows = remap_canonical_transcript(transcript, timeline)
    discord_row = next(row for row in rows if "Discord" in row["text"])
    assert discord_row["text"].startswith("Discord")
    assert all("Discor" not in row["text"].replace("Discord", "") for row in rows)
    assert all(row["text"] != "d" for row in rows)


def test_completed_render_recovery_is_exact_artifact_scoped(tmp_path) -> None:
    artifact_id = "clip-out14-push-microarc-editorial-v2-001"
    artifact_root = tmp_path / "artifacts"
    recovered = artifact_root / f".{artifact_id}.failed-deadbeef" / "final_video.mp4"
    recovered.parent.mkdir(parents=True)
    recovered.write_bytes(b"completed render bytes")
    stage = artifact_root / f".{artifact_id}.staging-cafebabe"
    stage.mkdir()
    staged = stage / "final_video.mp4"
    result = _reuse_completed_render_for_validation_retry(
        artifact_id=artifact_id,
        recovered_path=recovered,
        stage_video_path=staged,
        artifact_root=artifact_root,
    )
    assert result["recovery_copy_mode"] == "same_volume_hardlink"
    assert staged.read_bytes() == recovered.read_bytes()
    assert staged.stat().st_ino == recovered.stat().st_ino


def test_timing_gate_requires_three_anchors_per_section_and_passes_target() -> None:
    timeline = build_timeline(
        _selection(),
        source_identity="youtube:rltNvZ_FY8Q",
        source_sha256="a" * 64,
        source_duration_seconds=642.0,
        source_media_offset_seconds=2268.0,
    )
    anchors = []
    for cut in timeline["cuts"]:
        for index in range(3):
            anchors.append(
                {
                    "anchor_id": f"{cut['cut_id']}_{index}",
                    "section": cut["section"],
                    "canonical_source_onset_seconds": (
                        cut["provider_source_in_seconds"] + index + 0.2
                    ),
                    "rendered_output_onset_seconds": (
                        cut["output_in_seconds"] + index + 0.2
                    ),
                    "rendered_onset_error_ms": 0.0,
                    "provider_signed_onset_error_ms": 420.0,
                }
            )
    result = build_timing_readback(
        {
            "method": {
                "engine": "faster-whisper",
                "model": "small",
            },
            "timing_anchors": anchors,
        },
        [{"caption_id": "speech_0001"}],
        timeline,
    )
    assert result["anchor_count"] == 24
    assert result["rendered_median_signed_onset_error_ms"] == 0.0
    assert result["rendered_absolute_onset_error_p95_ms"] == 0.0
    assert result["provider_caption_diagnostic"]["systematic_late_bias_observed"]
    assert result["viewer_facing_non_speech_annotation_count"] == 0
