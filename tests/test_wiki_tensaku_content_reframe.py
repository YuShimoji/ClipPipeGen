from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = REPO_ROOT / "docs/content_planning/wiki_tensaku_content_reframe_v1"
PLAN_PATH = ARTIFACT_DIR / "wiki_tensaku_content_reframe_v1.json"
RECEIPT_PATH = ARTIFACT_DIR / "wiki_tensaku_content_reframe_v1.receipt.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_content_reframe_is_pre_render_and_uses_fixed_acceptance_weights() -> None:
    plan = _load(PLAN_PATH)

    assert plan["work_order_id"] == "CPG-WIKI-CONTENT-REFRAME-001"
    assert plan["artifact_class"] == "diagnostic_pre_render_content_design"
    assert plan["finished_video"] is False
    assert plan["generated_mp4_count"] == 0
    assert plan["human_artistic_acceptance"] == "revise"
    assert plan["classification_correction"]["integrated_product_iterations"] == 0
    assert plan["classification_correction"]["content_accepted_deliverables"] == 0

    score = plan["acceptance_score"]
    assert score["fixed_weight_total"] == 100
    assert sum(item["weight"] for item in score["units"]) == 100
    assert score["earned_points"] == 74
    assert [item["score"] for item in score["units"][:6]] == [1.0] * 6
    assert [item["score"] for item in score["units"][6:]] == [0.0] * 4


def test_episode_family_and_clip_units_are_context_complete() -> None:
    plan = _load(PLAN_PATH)
    proposal = plan["final_deliverable_proposal"]
    episodes = plan["episode_chapter_map"]
    ir = plan["narrative_assembly_ir"]

    assert proposal["selected_topology"] == "thematic_episode_family"
    assert proposal["planned_final_artifact_count"] == 4
    assert "300-second" in proposal["prohibited_topology"]
    assert len(episodes) == 4
    assert sum(len(episode["chapters"]) for episode in episodes) == 13
    assert ir["clip_unit_count"] == 13

    required_clip_fields = {
        "clip_id",
        "source_id",
        "source_timestamp",
        "topic",
        "speaker",
        "setup",
        "core_statement",
        "payoff_or_conclusion",
        "required_prior_context",
        "required_following_context",
        "chapter_contribution",
        "transition_in",
        "transition_out",
        "selection_reason",
        "exclusion_risk",
    }
    for clip in ir["clip_units"]:
        assert required_clip_fields <= clip.keys()
        assert all(clip[field] for field in required_clip_fields - {"source_timestamp"})
        timestamp = clip["source_timestamp"]
        assert timestamp["requested_duration_seconds"] >= 120
        assert timestamp["caption_aligned_end_seconds"] > timestamp["caption_aligned_start_seconds"]
        assert clip["caption_readback"]["event_count"] > 0
        assert clip["caption_readback"]["setup_excerpt"]
        assert clip["caption_readback"]["core_excerpt"]
        assert clip["caption_readback"]["payoff_excerpt"]

    for episode in episodes:
        for field in (
            "thesis",
            "viewer_question",
            "setup",
            "evidence",
            "interpretation",
            "conclusion",
            "transition_to_next",
        ):
            assert episode[field]
        for chapter in episode["chapters"]:
            for field in (
                "thesis",
                "viewer_question",
                "setup",
                "evidence",
                "interpretation",
                "conclusion",
                "transition_to_next",
            ):
                assert chapter[field]

    assert ir["setup_complete_count"] == 13
    assert ir["core_complete_count"] == 13
    assert ir["payoff_complete_count"] == 13
    assert ir["transition_in_complete_count"] == 13
    assert ir["transition_out_complete_count"] == 13
    assert len(plan["continuous_rough_cut_edit_script"]) == 13


def test_corpus_identity_and_probe_reclassification_are_fail_closed() -> None:
    plan = _load(PLAN_PATH)
    corpus = plan["corpus_inventory"]

    assert corpus["known_source_count"] == 3
    assert corpus["exact_media_source_count"] == 1
    assert corpus["missing_exact_media_source_count"] == 2
    assert corpus["exact_caption_source_count"] == 3
    assert {item["source_id"] for item in corpus["sources"]} == {
        "youtube:1AcId5Yja10",
        "youtube:82iRbxjvbww",
        "youtube:Ocqg-RpQURY",
    }
    assert {
        item["source_id"]
        for item in corpus["sources"]
        if item["media"]["state"] == "exact_source_bytes_unavailable"
    } == {"youtube:82iRbxjvbww", "youtube:Ocqg-RpQURY"}

    probes = plan["probe_reclassification"]
    assert len(probes) == 5
    for probe in probes:
        assert probe["turn_class"] == "SOURCE_SELECTION_AND_RENDER_PROBE"
        assert probe["product_authority"] == "non-final"
        assert probe["technical_evidence"] == "preserved"
        assert probe["human_artistic_acceptance"] == "revise"
        assert probe["final_product_status"] == "not accepted"
        assert probe["receipt_rewrite"] is False

    reuse = plan["turn_1_to_5_reuse_review"]
    assert reuse["probe_cut_count"] == 60
    assert reuse["proposed_for_contextual_reuse_count"] == 20
    assert reuse["excluded_from_current_assembly_count"] == 40
    assert len(reuse["proposed_for_contextual_reuse"]) == 20
    assert len(reuse["excluded_from_current_assembly"]) == 40


def test_receipt_binds_all_review_members_and_no_mp4_is_tracked_here() -> None:
    receipt = _load(RECEIPT_PATH)
    assert receipt["generated_mp4_count"] == 0
    assert receipt["immutable_probe_count_verified"] == 5
    assert receipt["source_identity_count_verified"] == 3
    assert not list(ARTIFACT_DIR.glob("*.mp4"))

    for member in receipt["members"]:
        path = REPO_ROOT / member["path"]
        assert path.stat().st_size == member["bytes"]
        assert _sha256(path) == member["sha256"]
