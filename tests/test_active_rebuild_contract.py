from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "artifacts" / "ACTIVE_REBUILD.json"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_active_rebuild_contract_is_one_portable_machine_readable_route() -> None:
    contract = _contract()

    assert contract["schema_id"] == "clippipegen.active_rebuild.v1"
    assert contract["artifact_id"] == (
        "clip-out07-shorts-poster-frame-direction-proof-v0-001"
    )
    assert contract["episode_id"] == "jp_pilot01_hololive_bancho_20260525"
    assert contract["resume_class"] == "reacquirable"
    assert contract["source_identity"]["provider_id"] == "7J5aS_pcBj4"
    current = contract["source_identity"]["current_media_revision"]
    assert current["sha256"] == (
        "e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889"
    )
    assert current["byte_equivalence_to_historical_claimed"] is False
    assert contract["source_identity"]["historical_source_host_sha256"] == (
        "6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a"
    )

    dependencies = contract["dependencies"]
    assert {item["recovery_class"] for item in dependencies} == {
        "tracked",
        "reacquire",
        "derive",
        "private_only",
    }
    historical = next(
        item
        for item in dependencies
        if item["id"] == "historical_out03_out06_binary_packages"
    )
    assert historical["required"] is False
    optional_ids = {
        "historical_out03_out06_binary_packages",
        "official_caption_track_provenance",
    }
    assert all(
        item["required"] for item in dependencies if item["id"] not in optional_ids
    )
    keifont = next(
        item for item in dependencies if item["id"] == "keifont_render_dependency"
    )
    assert keifont["expected_sha256"] == (
        "d5795bdff960c2b2ec5727ffeb79d836f8f11dac3015f6e16089a912e9cced6f"
    )

    steps = [item["step"] for item in contract["builder_order"]]
    assert steps == [
        "inventory_material_chain_and_direct_authority",
        "reacquire_materials_if_missing_with_existing_asset_fetch_clis",
        "load_direct_or_tracked_semantic_authority",
        "qualify_source_media_revision",
        "rebuild_reinstantiated_baseline",
        "reconstruct_operator_publish_draft",
        "freeze_public_reference_revision",
        "build_source_pixel_posters_transitions_and_combined_review",
        "repeat_frozen_build_and_compare_digests",
    ]
    assert [item["position"] for item in contract["builder_order"]] == list(
        range(1, 10)
    )

    recovery = contract["fresh_clone_recovery"]
    assert len(recovery["commands"]) == 4
    assert "init-episode" in recovery["commands"][0]
    assert "fetch-source-video" in recovery["commands"][1]
    assert "fetch-source-audio" in recovery["commands"][2]
    assert "reconstitute-out07-review" in recovery["commands"][3]
    assert recovery["authority_mode_when_episode_derivatives_are_absent"] == (
        "tracked_rebuild_contract"
    )


def test_active_rebuild_contract_preserves_semantics_and_acceptance_boundary() -> None:
    contract = _contract()
    semantic = contract["semantic_contract"]
    media = contract["media_contract"]["baseline"]
    acceptance = contract["acceptance_inheritance"]

    assert semantic["cut_order"] == ["cut_001", "cut_002", "cut_003"]
    assert semantic["source_ranges_seconds"] == [
        [2.453, 9.293],
        [12.329, 17.167],
        [22.606, 49.566],
    ]
    assert semantic["sequence_boundaries_seconds"] == [6.84, 11.678]
    assert semantic["semantic_duration_seconds"] == 38.638
    assert semantic["subtitle_first_id"] == "sub_001"
    assert semantic["subtitle_last_id"] == "sub_029"
    assert semantic["excluded_subtitle_ids"] == ["sub_030"]
    assert len(semantic["reviewed_wrap_overrides"]) == 6
    assert media == {
        "duration_seconds": 38.638,
        "duration_tolerance_seconds": 0.2,
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "video_codec": "h264",
        "audio_codec": "aac",
        "subtitle_count": 29,
        "hard_cut_boundaries_seconds": [6.84, 11.678],
    }
    assert acceptance["historical_accepted_output_sha256"] == (
        "02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0"
    )
    assert acceptance[
        "historical_human_acceptance_carries_only_when_output_sha_matches"
    ]
    assert acceptance["nonmatching_output_class"] == "reinstantiated_baseline_candidate"
    assert acceptance["nonmatching_output_human_acceptance"] is False
    assert acceptance["rights_status"] == "pending"
    snapshot = contract["semantic_authority_snapshot"]
    assert [item["id"] for item in snapshot["timeline"]] == [
        "cut_001",
        "cut_002",
        "cut_003",
    ]
    assert [item["id"] for item in snapshot["subtitles"]] == [
        f"sub_{index:03d}" for index in range(1, 30)
    ]
    assert snapshot["subtitles"][-1]["sequence_end_seconds"] == 38.638
    assert snapshot["operator_proxy_authority"]["operator_fields_state"] == (
        "undecided"
    )


def test_active_rebuild_contract_has_no_host_secrets_or_pixel_payloads() -> None:
    contract = _contract()
    text = CONTRACT_PATH.read_text(encoding="utf-8")

    assert not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]", text)
    assert "C:\\Users" not in text
    assert contract["security_and_storage"] == {
        "absolute_host_paths_allowed": False,
        "credentials_allowed": False,
        "copyrighted_pixels_tracked_in_git": False,
        "third_party_reference_pixels_used_in_candidates": False,
        "episodes_must_remain_untracked": True,
    }
    assert "username" not in text.lower()
    assert "password" not in text.lower()
    assert all(
        not str(item["locator"]).startswith(("/", "\\"))
        for item in contract["dependencies"]
    )


def test_runtime_points_to_active_rebuild_contract_and_combined_review() -> None:
    runtime = (ROOT / "docs" / "RUNTIME_STATE.md").read_text(encoding="utf-8")

    assert "active_rebuild_contract: artifacts/ACTIVE_REBUILD.json" in runtime
    assert "remote_code_complete: true" in runtime
    assert "local_artifact_available: true" in runtime
    assert "cross_machine_resume_class: reacquirable" in runtime
    assert "last_verified_host: DESKTOP-U9P4LKJ" in runtime
    assert "last_verified_host_label: Planner007" in runtime
    assert "current_host:" not in runtime.split("---", 2)[1]
