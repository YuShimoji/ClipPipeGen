from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/build_wiki_selected_opening_successor.py"
SPEC = importlib.util.spec_from_file_location("wiki_selected_opening_successor", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_current_exact_inputs_and_selected_opening_are_bound() -> None:
    evidence = MODULE.verify_inputs(REPO_ROOT)

    assert evidence["parent_timeline"]["cuts"][0]["source_in_seconds"] == 2530.319
    assert evidence["closing_caption"]["provider_event_id"] == "event_001639"
    assert evidence["closing_caption"]["source_end_seconds"] == 2865.599
    assert evidence["next_topic_caption"]["provider_event_id"] == "event_001641"
    assert evidence["next_topic_caption"]["source_start_seconds"] == 2865.599


def test_successor_timeline_excises_provider_overlap_without_new_semantic_claim() -> (
    None
):
    evidence = MODULE.verify_inputs(REPO_ROOT)
    timeline = MODULE.build_successor_timeline(evidence["parent_timeline"])

    assert timeline["artifact_id"] == MODULE.ARTIFACT_ID
    assert timeline["output_duration_seconds"] == 335.28
    assert timeline["endpoint_extension_seconds"] == 0
    assert timeline["cuts"][-1]["source_out_seconds"] == 2865.599
    assert timeline["cuts"][-1]["output_out_seconds"] == 335.28
    assert "semantic completion" in timeline["causal_order_note"]


def test_subtitle_successor_removes_only_the_next_topic_cue() -> None:
    evidence = MODULE.verify_inputs(REPO_ROOT)
    parent_ass = evidence["parent"] / "editorial_subtitles.ass"

    successor = MODULE.trimmed_ass(parent_ass)

    assert "でもねえいやというねものが" in successor
    assert "うん他なんかないの乳首を国境は" not in successor
    assert successor.count("Dialogue:") == 96


def test_successor_caption_contract_recomputes_counts_and_references() -> None:
    timeline = {
        "cuts": [
            {"cut_id": "cut_001", "caption_ids": ["caption_0001"]},
            {
                "cut_id": "cut_002",
                "caption_ids": ["caption_0002", "caption_0003"],
            },
        ]
    }
    readback = {
        "cue_count": 3,
        "provider_event_count_in_range": 3,
        "authority": {"display_cue_count": 3, "provider_event_count_in_range": 3},
        "rolling_overlap_resolution": {
            "cue_count": 3,
            "provider_event_count_in_range": 3,
        },
        "items": [
            {
                "caption_id": "caption_0001",
                "provider_event_id": "event_0001",
                "output_start_seconds": 0.0,
            },
            {
                "caption_id": "caption_0002",
                "provider_event_id": "event_0002",
                "output_start_seconds": 5.0,
            },
        ],
    }

    repaired_timeline, repaired_readback = MODULE.reconcile_successor_caption_contract(
        timeline, readback, endpoint_seconds=10.0
    )

    assert repaired_timeline["cuts"][-1]["caption_ids"] == ["caption_0002"]
    assert repaired_readback["cue_count"] == 2
    assert repaired_readback["provider_event_count_in_range"] == 2
    assert repaired_readback["authority"]["display_cue_count"] == 2
    assert repaired_readback["rolling_overlap_resolution"]["cue_count"] == 2
    assert repaired_readback["excluded_next_topic_event_id"] == "event_001641"
