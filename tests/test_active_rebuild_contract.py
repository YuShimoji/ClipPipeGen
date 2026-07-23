from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "artifacts" / "ACTIVE_REBUILD.json"
EXPECTED_BASELINE_SHA256 = (
    "2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18"
)
EXPECTED_SOURCE_SHA256 = (
    "e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889"
)
EXPECTED_CAPTION_SHA256 = (
    "3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919"
)


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_active_rebuild_contract_records_parked_noncanonical_cover_closure() -> None:
    contract = _contract()

    assert contract["schema_id"] == "clippipegen.active_rebuild.v1"
    assert contract["artifact_id"] == (
        "clip-out07-shorts-poster-frame-direction-proof-v0-001"
    )
    assert contract["episode_id"] == "jp_pilot01_hololive_bancho_20260525"
    assert contract["resume_class"] == "parked_predecessor"
    assert contract["state"] == (
        "OUT07_PARKED_WITH_VIABLE_NONCANONICAL_COVER_AND_MAIN_LANDED"
    )
    assert contract["handoff"]["from_state"] == (
        "OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY"
    )
    assert contract["handoff"]["cover_direction_review_available"] is False
    assert contract["handoff"]["next_human_decision"] is None
    assert contract["source_identity"]["provider_id"] == "7J5aS_pcBj4"
    assert contract["source_identity"]["current_media_revision"]["sha256"] == (
        EXPECTED_SOURCE_SHA256
    )

    baseline = contract["accepted_baseline"]
    assert baseline["sha256"] == EXPECTED_BASELINE_SHA256
    assert baseline["accepted_by"] == "Planner007"
    assert baseline["accepted_on"] == "2026-07-13 JST"
    assert baseline["historical_out06_acceptance_inherited"] is False
    assert baseline["rights_status"] == "pending"
    assert baseline["production_acceptance"] is False
    assert baseline["public_or_publishing_acceptance"] is False

    cover = contract["active_cover_direction"]
    assert cover["kind"] == (
        "thank_source_frame_plus_existing_subtitle_semantic_direction_proxy"
    )
    assert cover["baseline_seconds"] == 11.93
    assert cover["subtitle_id"] == "sub_010"
    assert cover["selection_status"] == "deferred"
    assert cover["proxy_classification"] == "cover_direction_semantic_proxy"
    assert cover["semantic_continuity_is_inference"] is True
    assert cover["planner_pixel_equivalence"] == "unknown"
    assert cover["exact_baseline_available"] is False
    assert cover["cover_direction_review_available"] is False
    assert cover["historical_cover_direction_evidence_available"] is True
    assert cover["selected_by_human"] is False
    assert cover["old_active_abc_status"] == (
        "superseded_by_user_short_context_reframe"
    )
    required = set(contract["required_outputs"])
    assert {
        "native_shorts_cover_1080x1920.png",
        "cover_shorts_ui_overlay_preview.jpg",
        "mapped_source_frame_1920x1080.png",
        "operator_delivery_readback.json",
    } <= required

    proxy = contract["semantic_direction_proxy"]
    assert proxy["route"] == "separate_from_strict_exact_reconstitution"
    assert proxy["local_source_sha256"] == (
        "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
    )
    assert proxy["planner_source_sha256"] == EXPECTED_SOURCE_SHA256
    assert proxy["byte_equivalence_claimed"] is False
    assert proxy["caption_sha256"] == EXPECTED_CAPTION_SHA256
    assert proxy["proxy_classification"] == "cover_direction_semantic_proxy"
    assert proxy["exact_baseline_available"] is False
    assert proxy["accepted_baseline_status"] == "accepted_historical_fact"
    assert proxy["cover_direction_review_available"] is False
    assert proxy["historical_cover_direction_evidence_available"] is True
    assert proxy["cover_direction_acceptance"] == "not_granted"
    assert proxy["human_review_decision"] == "PARK_PROVISIONAL_USABLE"
    assert proxy["acceptance_granted"] is False
    assert proxy["historical_local_evidence"] is True
    assert proxy["artifact_disposition"] == (
        "retained_historical_ignored_local_evidence"
    )
    assert proxy["current_iteration_allowed"] is False
    assert proxy["machine_readback"] is None
    assert proxy["historical_machine_readback"].endswith(
        "out07_native_shorts_cover_direction_proxy/cover_direction_proxy_readback.json"
    )
    assert proxy["portable_entrypoint"] is None

    closure = contract["human_review_closure"]
    assert closure == {
        "review_result": "PARK_PROVISIONAL_USABLE",
        "reviewed_by_human": True,
        "viable_candidate": True,
        "provisionally_usable_for_episode": True,
        "acceptance_granted": False,
        "human_selected": False,
        "selected_thumbnail": None,
        "selection_status": "deferred",
        "canonical_pattern": False,
        "default_template": False,
        "reuse_as_standard": False,
        "final_thumbnail_system_acceptance": False,
        "reference_collection_process_valid": True,
        "reference_to_output_lineage": "weak",
        "accidental_success_not_ruled_out": True,
        "revisit_after_real_short_count": "3_to_5",
        "additional_OUT07_thumbnail_iteration": "prohibited",
        "additional_out07_thumbnail_iteration_allowed": False,
        "revisit_count_min": 3,
        "revisit_count_max": 5,
        "thumbnail_is_active_product": False,
        "reference_corpus_role": "concrete_examples_not_canonical_design_rules",
    }

    strict = contract["strict_exact_route"]
    assert strict["accepted_baseline_sha256"] == EXPECTED_BASELINE_SHA256
    assert strict["byte_copy_only"] is True
    assert strict["acceptance_inheritance_requires_exact_hash"] is True
    assert strict["available_on_thank"] is False
    assert strict["validation_weakened"] is False


def test_caption_contract_is_hash_only_and_conditionally_reacquired() -> None:
    contract = _contract()
    dependencies = {item["id"]: item for item in contract["dependencies"]}
    caption = dependencies["official_caption_track"]

    assert caption["required"] is True
    assert caption["recovery_class"] == "reacquire"
    assert caption["expected_sha256"] == EXPECTED_CAPTION_SHA256
    assert caption["on_missing"] == "caption_authority_reacquire_required"
    assert "yt-dlp --skip-download --write-subs" in caption["recovery_command"]

    snapshot = contract["semantic_authority_snapshot"]
    subtitles = snapshot["subtitles"]
    assert len(subtitles) == 29
    assert [item["id"] for item in subtitles] == [
        f"sub_{index:03d}" for index in range(1, 30)
    ]
    assert all("text" not in item and "wrapped_lines" not in item for item in subtitles)
    assert all(re.fullmatch(r"[0-9a-f]{64}", item["text_sha256"]) for item in subtitles)
    assert all(item["recovery_class"] == "reacquire" for item in subtitles)
    assert all(
        item["on_missing"] == "caption_authority_reacquire_required"
        for item in subtitles
    )
    assert snapshot["caption_payload_digest"] == (
        "e9a18053baf3b6d042f35a91bb18ee7c5b28c878ef9e9d66ce649563ce11c23b"
    )
    wraps = contract["semantic_contract"]["reviewed_wrap_break_indices"]
    assert wraps == {
        "sub_013": [3, 8],
        "sub_014": [3],
        "sub_019": [8],
        "sub_024": [8, 12],
        "sub_028": [5],
        "sub_029": [5],
    }

    recovery = contract["fresh_clone_recovery"]
    assert recovery["resume_class"] == "conditional_reacquire"
    assert recovery["proof_status"] == "H2_successor_data_only_not_executed_in_H0"
    assert recovery["on_caption_missing"] == "caption_authority_reacquire_required"
    assert len(recovery["authority_reacquisition_commands"]) == 4
    assert "write-subs" in recovery["authority_reacquisition_commands"][3]
    baseline_restore = recovery["accepted_baseline_restore_condition"]
    assert baseline_restore["sha256"] == EXPECTED_BASELINE_SHA256
    assert baseline_restore["rerender_allowed"] is False
    assert baseline_restore["on_missing"] == "accepted_baseline_reacquire_required"
    assert (
        "reconstitute-out07-review"
        in recovery["package_command_after_all_preconditions"]
    )
    assert contract["handoff"]["portable_availability"] == {
        "portable_local_artifact_available": False,
        "human_entrypoint": None,
        "review_open_command": None,
        "machine_readback": None,
    }
    assert contract["handoff"]["accepted_baseline_stop_gate"] == (
        "accepted_baseline_reacquire_required"
    )


def test_current_tip_declares_history_boundary_without_scrub_claim() -> None:
    contract = _contract()
    boundary = contract["history_boundary"]
    assert (
        boundary["current_tracked_tip_contains_bulk_caption_plaintext_snapshot"]
        is False
    )
    assert boundary["prior_commits_may_still_contain_caption_plaintext"] is True
    assert boundary["history_scrub_claimed"] is False


def test_active_rebuild_contract_has_no_host_secrets_or_pixel_payloads() -> None:
    contract = _contract()
    text = CONTRACT_PATH.read_text(encoding="utf-8")

    assert not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]", text)
    assert "C:\\Users" not in text
    assert contract["security_and_storage"] == {
        "absolute_host_paths_allowed": False,
        "credentials_allowed": False,
        "copyrighted_pixels_tracked_in_git": False,
        "third_party_reference_pixels_used_in_cover": False,
        "episodes_must_remain_untracked": True,
    }
    assert "username" not in text.lower()
    assert "password" not in text.lower()


def test_runtime_points_to_out13_editorial_video_and_keeps_out07_rebuild_contract_parked() -> (
    None
):
    runtime = (ROOT / "docs" / "RUNTIME_STATE.md").read_text(encoding="utf-8")

    assert "active_rebuild_contract: null" in runtime
    assert (
        "parked_predecessor_rebuild_contract: artifacts/ACTIVE_REBUILD.json" in runtime
    )
    assert "remote_code_complete: true" in runtime
    assert "local_artifact_available: true" in runtime
    assert "portable_local_artifact_available: false" in runtime
    assert (
        "human_entrypoint: "
        "episodes/out13_editorial_video_candidate_20260723/review/"
        "out13_editorial_video_candidate_v003/review/index.html"
        in runtime
    )
    assert "portable_entrypoint: null" in runtime
    assert (
        "cross_machine_resume_class: "
        "tracked_code_docs_portable_exact_inputs_plan_and_output_require_"
        "private_transfer_or_new_identity_build"
        in runtime
    )
    assert "health: OUT13_EVIDENCE_BOUND_REVIEWABLE_ON_THANK_V1" in runtime
    assert "current_slice: OUT-13" in runtime
    assert (
        "canonical_status: "
        "evidence_bound_editorial_candidate_reviewable_on_thank_v1"
        in runtime
    )
    assert "active_artifact: clip-out13-editorial-video-candidate-v1-003" in runtime
    assert (
        "review_status: "
        "machine_validated_worker_sample_observed_human_editorial_review_pending"
        in runtime
    )
    assert "automation_acceptance_granted: true" in runtime
    assert "acceptance_granted: false" in runtime
    assert "out13_source_identity: youtube:7J5aS_pcBj4" in runtime
    assert (
        "out13_source_sha256: "
        "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
        in runtime
    )
    assert "out13_cut_count: 7" in runtime
    assert "out13_semantic_section_count: 5" in runtime
    assert "out13_output_duration_seconds: 128.833333" in runtime
    assert (
        "out13_output_sha256: "
        "a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5"
        in runtime
    )
    assert "out13_validation_status: passed" in runtime
    assert "out13_mapping_coverage_ratio: 1.0" in runtime
    assert "out13_resolved_font_family: Keifont" in runtime
    assert "out13_resolved_maximum_lines: 2" in runtime
    assert "out13_resume_render_executed: false" in runtime
    assert "out13_historical_source_host_resume_render_executed: false" in runtime
    assert "out13_review_mobile_overflow: false" in runtime
    assert "out13_rights_status: pending_or_snapshot_only" in runtime
    assert "out13_production_acceptance: false" in runtime
    assert "out13_public_or_publishing_acceptance: false" in runtime
    # OUT-12 remains the operational predecessor evidence.
    assert "out12_source_identity: youtube:gUwJBRUIWow" in runtime
    assert (
        "out12_source_sha256: "
        "8decc04ddcd805cadb77100eb5f7cbf2dc9883a32cb42aba0ed4c216fd0037cf"
        in runtime
    )
    assert "out12_cut_count: 11" in runtime
    assert "out12_output_duration_seconds: 260.693767" in runtime
    assert (
        "out12_output_sha256: "
        "5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584"
        in runtime
    )
    assert "out12_validation_status: passed" in runtime
    assert "out12_mapping_coverage_ratio: 1.0" in runtime
    assert "out12_resume_render_executed: false" in runtime
    assert "out12_review_mobile_overflow: false" in runtime
    assert "out12_rights_status: pending_or_snapshot_only" in runtime
    assert "out12_production_acceptance: false" in runtime
    assert "out12_public_or_publishing_acceptance: false" in runtime
    # OUT-10/11 remain exact historical closure evidence.
    assert "out10_inventory_count: 5" in runtime
    assert "out10_distinct_source_preflight_count: 3" in runtime
    assert "out10_eligible_source_count: 1" in runtime
    assert "out10_external_acquisition_required: false" in runtime
    assert "out10_external_acquisition_authorized: true" in runtime
    assert "out10_candidate_generated: true" in runtime
    assert "out11_scorecard_row_count: 5" in runtime
    assert "out11_review_media_count: 2" in runtime
    assert "out11_accepted_receipt_count: 1" in runtime
    assert "out11_review_question_count: 1" in runtime
    assert "out07_review_result: PARK_PROVISIONAL_USABLE" in runtime
    assert "subtitle_display_authority: official_json3_event_text_and_timing" in runtime
    assert "additional_subtitle_burn_in: true" in runtime
    assert "source_native_caption_pixels_suppressed: false" in runtime
    assert "full_source_blur_fallback_allowed: false" in runtime
    assert "additional_blur_or_frosted_caption_surface: false" in runtime
    assert (
        "candidate_01_sha256: "
        "62d4b45b26c2833e8a939a8f3d1954a4ea79047436f08d8f999269b539697cdd" in runtime
    )
    assert (
        "candidate_02_sha256: "
        "b4a01413202e3e177a11dc42754d38f5a4b7b10cd7c7bec0aa43536d440a4969" in runtime
    )
    assert (
        "out11_source04_mp4_sha256: "
        "465d732c05cf29f42e89c5b0564a0d6a15f3814b70073ff9039a27a93f916524" in runtime
    )
    assert "optional_recovery_merged: false" in runtime
    assert "out07_selection_status: deferred" in runtime
    assert "out07_canonical_pattern: false" in runtime
    assert "out07_default_template: false" in runtime
    assert "out07_reuse_as_standard: false" in runtime
    assert "out07_final_thumbnail_system_acceptance: false" in runtime
    assert "out07_additional_thumbnail_iteration: prohibited" in runtime
    assert "out07_revisit_after_real_short_count: 3_to_5" in runtime


def test_out10_inventory_receipt_stops_without_fabricating_a_candidate() -> None:
    path = ROOT / "docs" / "output_layer" / "out10_third_source_inventory_receipt.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert receipt["state"] == "NO_ELIGIBLE_LOCAL_THIRD_SOURCE_DECISION_READY"
    assert receipt["scope"]["inventory_count"] == 5
    assert receipt["scope"]["distinct_source_preflight_count"] == 3
    assert receipt["scope"]["render_execution_count"] == 0
    assert len(receipt["inventory"]) == 5
    assert sum(item["preflight"] == "completed" for item in receipt["inventory"]) == 3
    assert receipt["decision"]["eligible_local_third_source_count"] == 0
    assert receipt["decision"]["external_acquisition_required"] is True
    assert receipt["decision"]["external_acquisition_authorized"] is False
    assert receipt["selected_source"] is None
    assert receipt["selected_slice"] is None
    assert receipt["candidate_media"] is None
    assert receipt["portfolio_scorecard"]["status"] == (
        "not_created_no_third_source_candidate"
    )
