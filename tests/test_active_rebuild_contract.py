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


def test_active_rebuild_contract_points_to_accepted_native_cover_route() -> None:
    contract = _contract()

    assert contract["schema_id"] == "clippipegen.active_rebuild.v1"
    assert contract["artifact_id"] == (
        "clip-out07-shorts-poster-frame-direction-proof-v0-001"
    )
    assert contract["episode_id"] == "jp_pilot01_hololive_bancho_20260525"
    assert contract["resume_class"] == "conditional_reacquire"
    assert contract["state"] == (
        "OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY"
    )
    assert contract["handoff"]["from_state"] == (
        "OUT07_PAUSED_DURABLE_HANDOFF_ACCEPTED_BASELINE_MISSING"
    )
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
    assert cover["selection_status"] == (
        "semantic_direction_proxy_pending_human_acceptance"
    )
    assert cover["proxy_classification"] == "cover_direction_semantic_proxy"
    assert cover["semantic_continuity_is_inference"] is True
    assert cover["planner_pixel_equivalence"] == "unknown"
    assert cover["exact_baseline_available"] is False
    assert cover["cover_direction_review_available"] is True
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
    assert proxy["cover_direction_review_available"] is True
    assert proxy["cover_direction_acceptance"] == "pending"
    assert proxy["portable_entrypoint"] is None

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


def test_runtime_points_to_thank_semantic_proxy_review_state() -> None:
    runtime = (ROOT / "docs" / "RUNTIME_STATE.md").read_text(encoding="utf-8")

    assert "active_rebuild_contract: artifacts/ACTIVE_REBUILD.json" in runtime
    assert "remote_code_complete: true" in runtime
    assert "local_artifact_available: true" in runtime
    assert "portable_local_artifact_available: false" in runtime
    assert "human_entrypoint: http://127.0.0.1:8071/index.html" in runtime
    assert "portable_entrypoint: null" in runtime
    assert "out07_native_shorts_cover_direction_proxy" in runtime
    assert "cross_machine_resume_class: conditional_reacquire" in runtime
    assert "OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY" in runtime
    assert "exact_baseline_available: false" in runtime
    assert "accepted_baseline_status: accepted_historical_fact" in runtime
    assert "cover_direction_review_available: true" in runtime
