"""Subtitle renderer typography spike tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.integrations.render import subtitle_preset_selector as preset_selector
from src.integrations.render import subtitle_style_spike as spike


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_subtitle_style_spike_records_optional_pillow_boundary():
    assert spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE.startswith("Pillow is an optional")
    assert "review-only PNG measurement artifacts" in spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE
    assert "production renderer dependency" in spike.PILLOW_OPTIONAL_DEPENDENCY_MESSAGE


def test_subtitle_preset_selector_maps_semantic_intent_to_stable_tokens():
    selection = preset_selector.select_subtitle_preset(
        {
            "speaker_id": "Bancho",
            "speaker_role": "character",
            "emotion": "shout",
            "intensity": 2,
            "utterance_role": "dialogue",
            "readability_priority": "high",
        }
    )

    assert selection["preset_key"] == "character.dialogue.shout.i2.high"
    assert selection["style_tokens"]["font_family_role"] == (
        "current_keifont_dialogue_role"
    )
    assert selection["style_tokens"]["font_size_scale"] == 1.16
    assert selection["style_tokens"]["outline_shadow_strength"] == "strong"
    assert selection["style_tokens"]["badge_color_token"] == (
        "speaker_bancho_badge_default"
    )
    assert selection["style_tokens"]["accent_color_token"] == (
        "speaker_bancho_high_energy_accent"
    )
    assert selection["style_tokens"]["body_text_color_token"] == (
        "stable_default_body_text"
    )
    assert selection["style_tokens"]["body_text_color_changed"] is False
    assert selection["review_policy"]["human_review_required"] is False
    assert selection["review_policy"]["candidate_comparison_reopened"] is False
    assert selection["render_gate"]["new_render_required"] is False


def test_subtitle_preset_selector_readback_examples_match_tracked_json():
    readback = preset_selector.build_subtitle_preset_selector_readback()
    tracked_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-preset-selector.json"
    )
    tracked = json.loads(tracked_path.read_text(encoding="utf-8"))

    assert tracked["artifact_id"] == preset_selector.ARTIFACT_ID
    assert tracked["schema_id"] == preset_selector.SCHEMA_ID
    assert tracked["input_axes"] == readback["input_axes"]
    assert tracked["output_style_tokens"] == readback["output_style_tokens"]
    assert tracked["selector_contract"] == readback["selector_contract"]
    assert tracked["human_review_required_only_for"] == (
        readback["human_review_required_only_for"]
    )
    assert [item["example_id"] for item in tracked["examples"]] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert tracked["examples"] == readback["examples"]
    assert tracked["render_gate"]["new_render_run"] is False
    assert tracked["boundaries"]["production_render_acceptance"] is False


def test_subtitle_visual_selector_proof_matches_tracked_json():
    proof = preset_selector.build_subtitle_visual_selector_proof()
    tracked_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-visual-selector-proof.json"
    )
    tracked = json.loads(tracked_path.read_text(encoding="utf-8"))

    assert tracked["artifact_id"] == preset_selector.VISUAL_PROOF_ARTIFACT_ID
    assert tracked["schema_id"] == preset_selector.VISUAL_PROOF_SCHEMA_ID
    assert tracked["feature_id"] == "ED-10ac"
    assert tracked["source_selector_artifact_id"] == preset_selector.ARTIFACT_ID
    assert tracked["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert tracked["body_text_color_policy"] == proof["body_text_color_policy"]
    assert tracked["body_text_color_policy"]["stable_across_examples"] is True
    assert tracked["existing_output_first"]["considered"] is True
    assert tracked["existing_output_first"]["new_render_run"] is False
    assert tracked["render_gate"]["new_render_run"] is False
    assert tracked["review_policy"]["human_review_required"] is False
    assert tracked["review_policy"]["candidate_comparison_reopened"] is False
    assert tracked["examples"] == proof["examples"]
    assert {
        example["readback_tokens"]["body_text_color_token"]
        for example in tracked["examples"]
    } == {"stable_default_body_text"}
    assert {
        example["readback_tokens"]["body_text_color_changed"]
        for example in tracked["examples"]
    } == {False}


def test_subtitle_visual_selector_proof_html_is_static_readback():
    html_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-visual-selector-proof.html"
    )
    html = html_path.read_text(encoding="utf-8")

    assert "ED-10ac Visual Selector Proof" in html
    assert "clip-ed10ac-visual-selector-proof-001" in html
    assert "stable_default_body_text" in html
    assert "neutral_dialogue_intensity_0" in html
    assert "system_note_intensity_0" in html
    assert "New render run: <code>false</code>" in html
    assert "production subtitle design" in html


def test_subtitle_style_family_palette_axis_proof_matches_tracked_json():
    proof = preset_selector.build_subtitle_style_family_palette_axis_proof()
    tracked_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-style-family-palette-proof.json"
    )
    tracked = json.loads(tracked_path.read_text(encoding="utf-8"))

    assert tracked["artifact_id"] == preset_selector.STYLE_AXIS_PROOF_ARTIFACT_ID
    assert tracked["schema_id"] == preset_selector.STYLE_AXIS_PROOF_SCHEMA_ID
    assert tracked["feature_id"] == "ED-10ad"
    assert tracked["source_visual_selector_artifact_id"] == (
        preset_selector.VISUAL_PROOF_ARTIFACT_ID
    )
    assert tracked["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert tracked["axis_contract"]["body_text_color_policy"] == (
        "stable_default_body_text"
    )
    assert tracked["axis_contract"]["body_text_color_changed"] is False
    assert tracked["axis_contract"]["new_palette_created"] is False
    assert tracked["axis_contract"]["new_style_family_created"] is False
    assert tracked["body_text_color_policy"]["stable_across_examples"] is True
    assert tracked["existing_output_first"]["new_render_run"] is False
    assert tracked["render_gate"]["level"] == "L0 No Render / Existing Output First"
    assert tracked["render_gate"]["new_render_run"] is False
    assert tracked["review_policy"]["human_review_required"] is False
    assert tracked["examples"] == proof["examples"]
    assert {
        example["palette_surfaces"]["body_text_color_token"]
        for example in tracked["examples"]
    } == {"stable_default_body_text"}
    assert {
        example["axis_readback"]["palette_changes_body_text"]
        for example in tracked["examples"]
    } == {False}


def test_subtitle_style_family_palette_axis_proof_html_is_static_readback():
    html_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-style-family-palette-proof.html"
    )
    html = html_path.read_text(encoding="utf-8")

    assert "ED-10ad Style Family / Palette Axis Proof" in html
    assert "clip-ed10ad-style-family-palette-axis-proof-001" in html
    assert "dialogue_current_keifont_family" in html
    assert "high_energy_warm" in html
    assert "system_note_family" in html
    assert "stable_default_body_text" in html
    assert "New render run: <code>false</code>" in html
    assert "does not create a new palette" in html


def test_subtitle_render_path_selector_contract_matches_tracked_json():
    contract = preset_selector.build_subtitle_render_path_selector_contract()
    tracked_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-selector-contract.json"
    )
    tracked = json.loads(tracked_path.read_text(encoding="utf-8"))

    assert tracked["artifact_id"] == preset_selector.RENDER_PATH_CONTRACT_ARTIFACT_ID
    assert tracked["schema_id"] == preset_selector.RENDER_PATH_CONTRACT_SCHEMA_ID
    assert tracked["feature_id"] == "ED-10ae"
    assert tracked["source_style_family_palette_artifact_id"] == (
        preset_selector.STYLE_AXIS_PROOF_ARTIFACT_ID
    )
    assert tracked["render_level"] == "L0 No Render"
    assert tracked["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert tracked["render_adapter_input_contract"] == (
        contract["render_adapter_input_contract"]
    )
    assert tracked["contract_entries"] == contract["contract_entries"]
    assert {
        entry["render_adapter_input"]["color_surfaces"]["body_text_color_token"]
        for entry in tracked["contract_entries"]
    } == {"stable_default_body_text"}
    assert {
        entry["contract_assertions"]["render_artifact_created"]
        for entry in tracked["contract_entries"]
    } == {False}
    assert tracked["later_l2_render_path_probe_trigger"]["status"] == (
        "not_triggered_in_this_slice"
    )
    assert tracked["render_gate"]["new_render_run"] is False
    assert tracked["readiness_separation"]["video_render_readiness"] == (
        "not_run_no_render_pass_implied"
    )
    assert tracked["boundaries"]["production_render_acceptance"] is False


def test_subtitle_render_path_selector_contract_doc_is_static_readback():
    doc_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-selector-contract.md"
    )
    text = doc_path.read_text(encoding="utf-8")

    assert "ED-10ae Render Path Selector Contract Probe" in text
    assert "`semantic_preset_id`" in text
    assert "`font_size_scale`" in text
    assert "`stable_default_body_text`" in text
    assert "`L0 No Render`" in text
    assert "`L2 tiny render path probe milestone`" in text
    assert "no video, audio, frame, ASS, or episode artifact" in text


def test_subtitle_render_path_selector_probe_matches_tracked_json():
    tracked_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-selector-probe.json"
    )
    tracked = json.loads(tracked_path.read_text(encoding="utf-8"))
    probe = preset_selector.build_subtitle_render_path_selector_probe(
        local_probe=tracked["local_probe"]
    )

    assert tracked["artifact_id"] == preset_selector.RENDER_PATH_PROBE_ARTIFACT_ID
    assert tracked["schema_id"] == preset_selector.RENDER_PATH_PROBE_SCHEMA_ID
    assert tracked["feature_id"] == "ED-10af"
    assert tracked["source_render_path_selector_contract_artifact_id"] == (
        preset_selector.RENDER_PATH_CONTRACT_ARTIFACT_ID
    )
    assert tracked["probe_kind"] == "tiny_ffmpeg_libass_selector_probe_readback"
    assert tracked["render_level"] == "L2 tiny render path selector probe"
    assert tracked["selected_example_ids"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
    ]
    assert tracked["selected_example_count"] == 3
    assert tracked["examples"] == probe["examples"]
    assert tracked["validation"] == probe["validation"]
    assert tracked["validation"]["source_contract_referenced"] is True
    assert tracked["validation"]["stable_body_text_preserved"] is True
    assert tracked["validation"]["badge_accent_backplate_route_preserved"] is True
    assert tracked["validation"]["safe_area_line_break_metadata_survived"] is True
    assert tracked["validation"]["production_public_boundary_closed"] is True
    assert tracked["validation"]["tracked_binary_artifact_created"] is False
    assert tracked["validation"]["all_checks_passed"] is True
    assert {
        example["color_surfaces"]["body_text_color_token"]
        for example in tracked["examples"]
    } == {"stable_default_body_text"}
    assert all(
        example["assertions"]["badge_accent_backplate_preserved"]
        for example in tracked["examples"]
    )
    assert any(
        example["line_break"]["ass_text_contains_line_break"]
        for example in tracked["examples"]
    )
    assert tracked["local_probe"]["status"] == "local_ignored_probe_generated"
    assert "subtitle_render_path_selector_probe.ass" in tracked["local_probe"]["outputs"]["ass"]
    assert "subtitle_render_path_selector_probe.mp4" in tracked["local_probe"]["outputs"]["video"]
    assert tracked["render_gate"]["new_render_run"] is True
    assert tracked["render_gate"]["tracked_binary_artifact_created"] is False
    assert tracked["boundaries"]["production_render_acceptance"] is False
    assert tracked["boundaries"]["rights_status"] == "pending"
    assert tracked["boundaries"]["public_use_permission"] is False
    assert tracked["boundaries"]["tracked_binary_artifact_created"] is False
    assert tracked["boundaries"]["episodes_tracked"] is False


def test_subtitle_render_path_selector_probe_doc_records_l2_readback():
    doc_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-selector-probe.md"
    )
    text = doc_path.read_text(encoding="utf-8")

    assert "ED-10af L2 Render Path Selector Probe" in text
    assert "consumes the ED-10ae selector-to-render contract" in text
    assert "FFmpeg/libass diagnostic path" in text
    assert "`L2 tiny render path selector probe`" in text
    assert "local_ignored_probe_generated" in text
    assert "`neutral_dialogue_intensity_0`" in text
    assert "`shout_intensity_2`" in text
    assert "LOW PRESSURE\\NWHISPER CUE" in text
    assert "stable_default_body_text" in text
    assert "badge/accent/backplate-first" in text
    assert "do not approve production subtitle design" in text


def test_restored_render_contract_consumer_dry_read_records_static_payloads():
    dry_read_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-contract-consumer-dry-read.json"
    )
    dry_read_doc_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-contract-consumer-dry-read.md"
    )
    dry_read = json.loads(dry_read_path.read_text(encoding="utf-8"))
    dry_read_doc = dry_read_doc_path.read_text(encoding="utf-8")

    assert dry_read["artifact_id"] == (
        preset_selector.RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
    )
    assert dry_read["schema_id"] == (
        preset_selector.RENDER_CONTRACT_CONSUMER_DRY_READ_SCHEMA_ID
    )
    assert dry_read["feature_id"] == "ED-10af"
    assert dry_read["status"] == "render_contract_consumer_dry_read_ready"
    assert dry_read["render_gate"]["level"] == "L0 No Render"
    assert dry_read["render_gate"]["new_render_run"] is False
    assert dry_read["render_gate"]["consumer_dry_read_only"] is True
    assert len(dry_read["consumer_payloads"]) == 6
    assert dry_read["dry_read_validation"]["all_payloads_consumer_ready"] is True
    assert dry_read["dry_read_validation"]["render_boundary_leakage"] is False
    assert dry_read["dry_read_validation"][
        "production_public_boundary_leakage"
    ] is False
    assert dry_read["boundaries"]["production_render_acceptance"] is False
    assert dry_read["boundaries"]["episodes_tracked"] is False
    assert "ED-10af Render Contract Consumer Dry-Read" in dry_read_doc
    assert "L0 No Render" in dry_read_doc



def test_subtitle_render_path_lineage_observation_surface_matches_tracked_json():
    dry_read = json.loads(
        (
            REPO_ROOT
            / "docs"
            / "style_intent"
            / "subtitle-render-contract-consumer-dry-read.json"
        ).read_text(encoding="utf-8")
    )
    source_probe = json.loads(
        (
            REPO_ROOT
            / "docs"
            / "style_intent"
            / "subtitle-render-path-selector-probe.json"
        ).read_text(encoding="utf-8")
    )
    tracked_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-lineage-observation-surface.json"
    )
    tracked = json.loads(tracked_path.read_text(encoding="utf-8"))
    generated = preset_selector.build_subtitle_render_path_lineage_observation_surface(
        dry_read=dry_read,
        source_probe=source_probe,
    )

    assert tracked == generated
    assert tracked["artifact_id"] == (
        preset_selector.LINEAGE_OBSERVATION_ARTIFACT_ID
    )
    assert tracked["schema_id"] == preset_selector.LINEAGE_OBSERVATION_SCHEMA_ID
    assert tracked["feature_id"] == "ED-10ag"
    assert tracked["status"] == "lineage_observation_surface_ready"
    assert tracked["active_artifact_id"] == preset_selector.RENDER_PATH_PROBE_ARTIFACT_ID
    assert tracked["source_render_contract_consumer_dry_read_artifact_id"] == (
        preset_selector.RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
    )
    assert tracked["source_render_path_selector_probe_artifact_id"] == (
        preset_selector.RENDER_PATH_PROBE_ARTIFACT_ID
    )
    predecessor = tracked["lineage"]["predecessor_artifacts"][0]
    assert predecessor["artifact_id"] == (
        preset_selector.RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
    )
    assert predecessor["source_commit"] == "7e96a28"
    assert predecessor["invalidated"] is False
    assert predecessor["superseded_by"] == preset_selector.RENDER_PATH_PROBE_ARTIFACT_ID
    assert tracked["existing_output_first"]["decision"] == (
        "preserve_active_ed10af_l2_probe_and_record_lineage_no_rerender"
    )
    assert tracked["existing_output_first"]["new_render_run"] is False
    assert tracked["observation_surface"]["source_dry_read_payload_count"] == 6
    assert tracked["observation_surface"]["selected_example_count"] == 3
    assert tracked["observation_surface"]["same_machine_only"] is True
    assert tracked["observation_surface"]["may_be_absent_on_other_clone"] is True
    assert tracked["observation_surface"]["user_review_required"] is False
    assert tracked["observation_surface"]["local_probe_status"] == (
        "local_ignored_probe_generated"
    )
    assert "subtitle_render_path_selector_probe_contact_sheet.jpg" in tracked[
        "observation_surface"
    ]["local_outputs"]["contact_sheet"]
    assert len(tracked["observation_surface"]["open_commands"]) == 4
    assert tracked["validation"]["active_artifact_preserved"] is True
    assert tracked["validation"]["predecessor_lineage_present"] is True
    assert tracked["validation"]["observation_paths_present"] is True
    assert tracked["validation"]["contact_sheet_path_recorded"] is True
    assert tracked["validation"]["dry_read_all_payloads_consumer_ready"] is True
    assert tracked["validation"]["source_probe_all_checks_passed"] is True
    assert tracked["validation"]["selected_examples_covered_by_dry_read"] is True
    assert tracked["validation"]["stable_body_text_preserved"] is True
    assert tracked["validation"]["production_public_boundary_closed"] is True
    assert tracked["validation"]["all_checks_passed"] is True
    assert tracked["render_gate"]["level"] == "lineage_only_no_new_render"
    assert tracked["render_gate"]["new_render_run"] is False
    assert tracked["render_gate"]["existing_output_first_reused"] is True
    assert tracked["render_gate"]["source_probe_new_render_run"] is True
    assert tracked["boundaries"]["new_render_created"] is False
    assert tracked["boundaries"]["diagnostic_local_ignored_render_reused"] is True
    assert tracked["boundaries"]["episodes_tracked"] is False
    assert "subtitle_render_path_selector_probe.mp4" in tracked[
        "observation_surface"
    ]["local_outputs"]["video"]
    assert "subtitle_render_path_selector_probe.local.json" in tracked[
        "observation_surface"
    ]["local_outputs"]["manifest"]


def test_subtitle_render_path_lineage_observation_surface_doc_records_existing_output_first():
    doc_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-lineage-observation-surface.md"
    )
    text = doc_path.read_text(encoding="utf-8")

    assert "ED-10ag Lineage and Observation Surface" in text
    assert "Existing Output First" in text
    assert "new_render_run: `false`" in text
    assert "clip-ed10af-l2-render-path-selector-probe-001" in text
    assert "clip-ed10af-render-contract-consumer-dry-read-001" in text
    assert "predecessor source commit: `7e96a28`" in text
    assert "predecessor invalidated: `false`" in text
    assert "dry-read payloads: `6` / `6`" in text
    assert "local_ignored_probe_generated" in text
    assert "subtitle_render_path_selector_probe.mp4" in text
    assert "subtitle_render_path_selector_probe_contact_sheet.jpg" in text
    assert "Start-Process" in text
    assert "stable_body_text_preserved: `true`" in text
    assert "episodes_tracked: `false`" in text


def test_subtitle_production_limitation_lift_entry_matches_tracked_json():
    style_dir = REPO_ROOT / "docs" / "style_intent"
    dry_read = json.loads(
        (style_dir / "subtitle-render-contract-consumer-dry-read.json").read_text(
            encoding="utf-8"
        )
    )
    source_probe = json.loads(
        (style_dir / "subtitle-render-path-selector-probe.json").read_text(
            encoding="utf-8"
        )
    )
    lineage_surface = json.loads(
        (
            style_dir / "subtitle-render-path-lineage-observation-surface.json"
        ).read_text(encoding="utf-8")
    )
    tracked = json.loads(
        (style_dir / "subtitle-production-limitation-lift-entry.json").read_text(
            encoding="utf-8"
        )
    )
    generated = preset_selector.build_subtitle_production_limitation_lift_entry(
        dry_read=dry_read,
        source_probe=source_probe,
        lineage_surface=lineage_surface,
    )

    assert tracked == generated
    assert tracked["schema_id"] == preset_selector.PRODUCTION_LIMITATION_LIFT_SCHEMA_ID
    assert tracked["artifact_id"] == (
        preset_selector.PRODUCTION_LIMITATION_LIFT_ARTIFACT_ID
    )
    assert tracked["feature_id"] == "ED-10ah"
    assert tracked["status"] == "production_limitation_lift_entry_ready"
    assert tracked["active_artifact_id"] == preset_selector.RENDER_PATH_PROBE_ARTIFACT_ID
    assert tracked["source_lineage_observation_surface_artifact_id"] == (
        preset_selector.LINEAGE_OBSERVATION_ARTIFACT_ID
    )
    assert tracked["source_render_contract_consumer_dry_read_artifact_id"] == (
        preset_selector.RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
    )
    assert tracked["gate_names"] == list(
        preset_selector.PRODUCTION_LIMITATION_LIFT_GATE_NAMES
    )
    by_gate = {gate["gate_name"]: gate for gate in tracked["gate_matrix"]}
    assert by_gate["diagnostic_render_path_proof"]["current_status"] == (
        "available_diagnostic_only"
    )
    assert by_gate["diagnostic_render_path_proof"][
        "agent_can_progress_without_user_judgement"
    ] is True
    for gate_name in (
        "production_subtitle_design_acceptance",
        "production_render_acceptance",
        "creative_acceptance",
        "rights_status",
        "publishing_acceptance",
        "public_use_permission",
    ):
        assert by_gate[gate_name]["agent_can_progress_without_user_judgement"] is False
        assert by_gate[gate_name]["human_judgement_required"] is True
    assert by_gate["rights_status"]["current_status"] == "pending"
    assert by_gate["public_use_permission"]["current_status"] == "not_allowed"
    assert tracked["source_evidence"][
        "active_diagnostic_proof_source_artifact_id"
    ] == preset_selector.RENDER_PATH_PROBE_ARTIFACT_ID
    assert tracked["source_evidence"][
        "support_lineage_observation_surface_artifact_id"
    ] == preset_selector.LINEAGE_OBSERVATION_ARTIFACT_ID
    assert tracked["source_evidence"]["dry_read_predecessor_source_commit"] == "7e96a28"
    assert tracked["user_observation_consumed"][
        "display_surface_acceptable_enough"
    ] is True
    assert tracked["user_observation_consumed"]["layout_polish_deferred"] is True
    assert tracked["next_executable_route"]["route_id"] == (
        "production-limitation-lift-stage-1"
    )
    assert tracked["next_executable_route"]["alternate_route_id"] == (
        "final-render-path-readiness"
    )
    assert tracked["next_executable_route"][
        "agent_can_start_without_user_judgement"
    ] is True
    assert tracked["readiness_separation"][
        "production_subtitle_design_acceptance"
    ] is False
    assert tracked["readiness_separation"]["production_render_acceptance"] is False
    assert tracked["readiness_separation"]["creative_acceptance"] is False
    assert tracked["readiness_separation"]["rights_status"] == "pending"
    assert tracked["readiness_separation"]["publishing_acceptance"] is False
    assert tracked["readiness_separation"]["public_use_permission"] is False
    assert tracked["render_gate"]["new_render_run"] is False
    assert tracked["boundaries"]["production_usage_allowed"] is False
    assert tracked["boundaries"]["public_use_permission"] is False
    assert tracked["boundaries"]["tracked_binary_artifact_created"] is False
    assert tracked["boundaries"]["episodes_tracked"] is False
    assert tracked["validation"]["gate_names_present"] is True
    assert tracked["validation"]["active_diagnostic_source_preserved"] is True
    assert tracked["validation"]["lineage_support_not_production_proof"] is True
    assert tracked["validation"]["dry_read_predecessor_preserved"] is True
    assert tracked["validation"]["production_public_boundary_closed"] is True
    assert tracked["validation"]["all_checks_passed"] is True


def test_subtitle_production_limitation_lift_entry_doc_records_gate_matrix():
    text = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-production-limitation-lift-entry.md"
    ).read_text(encoding="utf-8")

    assert "ED-10ah Production Limitation-Lift Entry" in text
    assert "It is a route entry, not an approval." in text
    assert "display_surface_acceptable_enough: `true`" in text
    assert "layout_polish_deferred: `true`" in text
    assert "clip-ed10af-l2-render-path-selector-probe-001" in text
    assert "clip-ed10ag-lineage-and-observation-surface-001" in text
    assert "clip-ed10af-render-contract-consumer-dry-read-001" in text
    assert "dry-read predecessor source commit: `7e96a28`" in text
    assert "diagnostic_render_path_proof" in text
    assert "production_subtitle_design_acceptance" in text
    assert "production_render_acceptance" in text
    assert "creative_acceptance" in text
    assert "rights_status" in text
    assert "publishing_acceptance" in text
    assert "public_use_permission" in text
    assert "agent_can_start_without_user_judgement: `true`" in text
    assert "all_checks_passed: `true`" in text
    assert "episodes_tracked: `false`" in text


def test_subtitle_render_readiness_separation_records_ed10ag_boundary():
    readback = json.loads(
        (
            REPO_ROOT
            / "docs"
            / "style_intent"
            / "subtitle-render-readiness-separation.json"
        ).read_text(encoding="utf-8")
    )
    doc = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-readiness-separation.md"
    ).read_text(encoding="utf-8")

    assert readback["artifact_id"] == (
        "clip-ed10ah-render-readiness-separation-readback-001"
    )
    assert readback["feature_id"] == "ED-10ah"
    assert readback["new_render_run"] is False
    assert readback["existing_output_first_reused"] is True
    assert readback["source_artifacts"]["dry_read"] == (
        preset_selector.RENDER_CONTRACT_CONSUMER_DRY_READ_ARTIFACT_ID
    )
    assert readback["source_artifacts"]["l2_selector_probe"] == (
        preset_selector.RENDER_PATH_PROBE_ARTIFACT_ID
    )
    assert readback["source_artifacts"]["lineage_observation_surface"] == (
        preset_selector.LINEAGE_OBSERVATION_ARTIFACT_ID
    )
    assert "production render acceptance" in " ".join(
        readback["ed10ag_does_not_prove"]
    )
    assert readback["render_gate"]["next_render_trigger"] == (
        "later_explicit_milestone_only"
    )
    assert readback["boundaries"]["production_render_acceptance"] is False
    assert readback["boundaries"]["rights_status"] == "pending"
    assert readback["boundaries"]["public_use_permission"] is False
    assert readback["boundaries"]["episodes_tracked"] is False
    assert readback["human_burden_hygiene"]["user_work"] == "none"
    assert readback["validation"]["all_checks_passed"] is True
    assert "ED-10ah Render Readiness Separation Readback" in doc
    assert "`stable_default_body_text`" in doc
    assert "`later_explicit_milestone_only`" in doc


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_japanese_wrapper_prevents_one_character_orphan_when_measured_alternative_exists():
    image = spike.Image.new("RGB", (420, 180), (0, 0, 0))
    draw = spike.ImageDraw.Draw(image)
    _, font_path, _ = spike._select_font()
    font = spike._load_font(font_path, 42)
    text = "\u3042\u3044\u3046\u3048\u304a"
    spacing = 0
    stroke_width = 0
    max_width = spike._text_size(
        draw=draw,
        text=text[:-1],
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]
    if max_width >= spike._text_size(
        draw=draw,
        text=text,
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]:
        pytest.skip("selected font does not increase measured width for the orphan fixture")

    result = spike._wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )

    assert result.algorithm_name == "japanese_boundary_font_bbox_pixel_wrap_v1"
    assert result.orphan_prevention_applied is True
    assert result.selected_break_reason == "orphan_prevention_shifted_break"
    assert spike._visible_char_count(result.lines[-1]) > 1
    assert result.lines != ["\u3042\u3044\u3046\u3048", "\u304a"]
    assert all(width <= max_width for width in result.measured_width_by_line)
    assert any(candidate["would_leave_one_character_orphan"] for candidate in result.candidate_breaks)


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_japanese_wrapper_prevents_suffix_only_tail_when_measured_alternative_exists():
    image = spike.Image.new("RGB", (1920, 1080), (0, 0, 0))
    draw = spike.ImageDraw.Draw(image)
    _, font_path, _ = spike._select_font()
    if font_path is None:
        pytest.skip("Japanese font file is not available for suffix-tail fixture")
    font = spike._load_font(font_path, 124)
    spacing = 19
    stroke_width = 12
    text = "\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052\u307e\u3059"
    max_width = spike._text_size(
        draw=draw,
        text="\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052",
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]

    result = spike._wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )

    assert result.suffix_tail_prevention_applied is True
    assert result.selected_break_reason == "suffix_tail_prevention_shifted_break"
    assert result.lines != ["\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052", "\u307e\u3059"]
    assert result.lines[-1] in {"\u3042\u3052\u307e\u3059", "\u3066\u3042\u3052\u307e\u3059", "\u8a31\u3057\u3066\u3042\u3052\u307e\u3059"}
    assert result.suspicious_tail_line_present is False
    assert any(
        candidate["remaining_text"] == "\u307e\u3059"
        and candidate["would_leave_suspicious_tail_line"] is True
        for candidate in result.candidate_breaks
    )


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_japanese_wrapper_marks_question_particle_tail_suspicious():
    image = spike.Image.new("RGB", (1920, 1080), (0, 0, 0))
    draw = spike.ImageDraw.Draw(image)
    _, font_path, _ = spike._select_font()
    if font_path is None:
        pytest.skip("Japanese font file is not available for suffix-tail fixture")
    font = spike._load_font(font_path, 124)
    spacing = 19
    stroke_width = 12
    text = "\u306a\u3093\u3067\u6765\u306a\u304b\u3063\u305f\u3093\u3059\u304b\uff01\uff01"
    max_width = spike._text_size(
        draw=draw,
        text="\u306a\u3093\u3067\u6765\u306a\u304b\u3063\u305f\u3093\u3059",
        font=font,
        spacing=spacing,
        stroke_width=stroke_width,
    )[0]

    result = spike._wrap_text_to_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        spacing=spacing,
        stroke_width=stroke_width,
    )

    assert result.suffix_tail_prevention_applied is True
    assert result.lines == ["\u306a\u3093\u3067\u6765\u306a\u304b\u3063\u305f", "\u3093\u3059\u304b\uff01\uff01"]
    assert result.suspicious_tail_line_present is False
    assert any(
        candidate["remaining_text"] == "\u304b\uff01\uff01"
        and candidate["would_leave_suspicious_tail_line"] is True
        for candidate in result.candidate_breaks
    )


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_subtitle_style_spike_writes_png_json_and_html_readback(tmp_path: Path):
    output_dir = tmp_path / "subtitle_style_spike"

    report = spike.build_subtitle_style_spike(output_dir=output_dir, canvas_size=(640, 360))

    assert report["review_only"] is True
    assert report["production_candidate"] is False
    assert report["production_compatible"] is False
    assert report["production_subtitle_design_acceptance"] is False
    assert report["dependency_boundary"] == {
        "pillow": "optional_local_review_tool",
        "declared_project_dependency": False,
        "missing_dependency_behavior": "module import remains available; PNG generation raises explicit RuntimeError",
    }
    assert report["grid_readback"]["grid_model"] == "none"
    assert report["grid_readback"]["grid_visible_in_samples"] is False
    assert report["grid_readback"]["snap_to_grid"] is False
    assert report["grid_readback"]["bbox_grid_coords"] is None
    assert report["grid_readback"]["safe_area_grid_coords"] is None
    assert report["grid_readback"]["wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
    assert report["measured_bbox_provenance"]["status"] == "systematic_measured_readback"
    assert report["measured_bbox_provenance"]["source_function"] == "draw.multiline_textbbox"
    assert report["measured_bbox_provenance"]["hardcoded_per_sample"] is False
    assert report["measured_bbox_provenance"]["manual_adjustment"] is False
    assert report["measured_bbox_provenance"]["design_target"] is False
    assert report["measured_bbox_provenance"]["report_sections"] == [
        "style_inputs",
        "computed_layout",
        "measured_output",
    ]
    assert set(report["visible_element_authority_classes"]) == {
        "computational_authority",
        "measured_readback",
        "visual_guide_only",
        "placeholder",
        "decorative",
    }
    authority = {
        item["element_id"]: item
        for item in report["visible_element_authority"]
    }
    assert authority["subtitle_text_block"]["authority_class"] == "computational_authority"
    assert authority["subtitle_text_block"]["actual_layout_authority"] is True
    assert authority["safe_area_rectangle"]["authority_class"] == "measured_readback"
    assert authority["safe_area_rectangle"]["visible_in_clean_samples"] is False
    assert authority["safe_area_rectangle"]["visible_in_guide_overlay_samples"] is True
    assert authority["measured_text_bbox_readback"]["authority_class"] == "measured_readback"
    assert authority["placeholder_speaker_badge"]["authority_class"] == "placeholder"
    assert "not real face icons" in authority["placeholder_speaker_badge"]["meaning_for_reviewer"]
    assert authority["speaker_accent_color"]["authority_class"] == "placeholder"
    assert authority["layout_grid"]["authority_class"] == "visual_guide_only"
    assert authority["layout_grid"]["visible_in_default_samples"] is False
    assert authority["layout_grid"]["visible_in_guide_overlay_samples"] is False
    assert authority["frame_center_lines"]["authority_class"] == "visual_guide_only"
    assert authority["frame_center_lines"]["visible_in_guide_overlay_samples"] is True
    assert authority["frame_thirds_lines"]["authority_class"] == "visual_guide_only"
    assert authority["lower_subtitle_zone"]["authority_class"] == "visual_guide_only"
    assert authority["subtitle_baseline_guides"]["authority_class"] == "measured_readback"
    assert authority["badge_slot_guide"]["authority_class"] == "placeholder"
    assert authority["badge_center_line"]["authority_class"] == "measured_readback"
    assert authority["text_start_x_line"]["authority_class"] == "measured_readback"
    assert authority["badge_to_text_gap_guide"]["authority_class"] == "measured_readback"
    assert authority["sample_mode_label"]["authority_class"] == "visual_guide_only"
    assert authority["sample_background"]["authority_class"] == "decorative"
    assert authority["html_sample_image_frame"]["authority_class"] == "decorative"
    assert report["mode_decision"]["line"] == "\u6765\u306d\u3047\uff01\uff01"
    assert report["mode_decision"]["not_recommended_default"] == "dialogue_badge_left"
    assert set(report["mode_decision"]["recommended_modes"]) == {
        "reaction_caption",
        "bottom_center_emphasis",
    }
    assert set(report["taxonomy"]) == {
        "dialogue_badge_left",
        "bottom_center_emphasis",
        "reaction_caption",
        "speaker_badge_stack",
    }
    assert {row["candidate"] for row in report["renderer_decision_matrix"]} == {
        "ASS/libass + FFmpeg",
        "HTML/CSS + Playwright screenshot",
        "Pillow / Skia / Pango image drawing",
        "YMM4 .ymmp TextItem direct generation or patch",
        "Premiere MOGRT / Essential Graphics / image overlay",
    }

    samples = report["samples"]
    assert len(samples) == 16
    assert {sample["subtitle_mode"] for sample in samples} == {
        "dialogue_badge_left",
        "bottom_center_emphasis",
        "reaction_caption",
        "speaker_badge_stack",
    }
    for sample in samples:
        image_path = Path(sample["output_image_path"])
        assert image_path.exists()
        assert image_path.suffix == ".png"
        assert sample["sample_variant"] == "clean"
        assert sample["canvas_size"] == {"width": 640, "height": 360}
        assert sample["review_only"] is True
        assert sample["production_candidate"] is False
        assert sample["production_compatible"] is False
        assert sample["requested_font_size"] > 0
        assert sample["style_inputs"]["mode"] == sample["subtitle_mode"]
        assert (
            sample["style_inputs"]["font"]["requested_font_size"]["source"]
            == "formula_from_frame_height_and_mode_constant"
        )
        assert sample["style_inputs"]["font"]["requested_font_size"]["value"] == sample["requested_font_size"]
        assert sample["style_inputs"]["outline"]["stroke_width"]["value"] == sample["outline"]["stroke_width"]
        assert sample["style_inputs"]["safe_area_margin"]["x"]["value"] == sample["safe_area_margin"]["x"]
        assert sample["style_inputs"]["safe_area_margin"]["y"]["value"] == sample["safe_area_margin"]["y"]
        assert sample["style_inputs"]["line_height"]["value"] == sample["line_height"]
        assert sample["computed_layout"]["layout_anchor"] == sample["layout_anchor"]
        assert sample["wrap_algorithm"]["source_function"] == "_wrap_text_to_width"
        assert sample["wrap_algorithm"]["name"] == "japanese_boundary_font_bbox_pixel_wrap_v1"
        assert sample["computed_layout"]["wrap_algorithm"] == sample["wrap_algorithm"]
        assert sample["computed_layout"]["wrap_algorithm"]["not_grid_based"] is True
        assert sample["computed_layout"]["wrapped_text"] == sample["wrapped_text"]
        assert sample["computed_layout"]["wrapped_lines"] == sample["wrapped_lines"]
        assert sample["computed_layout"]["line_count"] == sample["line_count"]
        assert len(sample["measured_width_by_line"]) == sample["line_count"]
        assert sample["computed_layout"]["measured_width_by_line"] == sample["measured_width_by_line"]
        assert sample["computed_layout"]["candidate_breaks"] == sample["candidate_breaks"]
        assert sample["computed_layout"]["selected_break_reason"] == sample["selected_break_reason"]
        assert sample["computed_layout"]["orphan_prevention_applied"] == sample["orphan_prevention_applied"]
        assert (
            sample["computed_layout"]["suffix_tail_prevention_applied"]
            == sample["suffix_tail_prevention_applied"]
        )
        assert (
            sample["computed_layout"]["suspicious_tail_line_present"]
            == sample["suspicious_tail_line_present"]
        )
        assert sample["font_file_status"] == sample["font_fallback_status"]
        assert sample["computed_layout"]["text_start_position"]["x"] >= 0
        assert sample["computed_layout"]["text_start_position"]["y"] >= 0
        assert sample["measured_output"]["source_function"] == "draw.multiline_textbbox"
        assert sample["measured_output"]["manual_override"] is False
        assert sample["measured_output"]["hardcoded_per_sample"] is False
        assert sample["measured_output"]["design_target"] is False
        assert sample["measured_output"]["measured_bbox"] == sample["measured_bbox"]
        assert sample["measured_output"]["safe_area_status"] == sample["safe_area_status"]
        assert sample["measured_bbox"]["width"] > 0
        assert sample["measured_bbox"]["height"] > 0
        assert sample["safe_area_margin"]["x"] > 0
        assert sample["grid_model"] == "none"
        assert sample["layout_anchor"]
        assert sample["snap_to_grid"] is False
        assert sample["text_bbox_grid_coords"] is None
        assert sample["badge_bbox_grid_coords"] is None
        assert sample["safe_area_grid_coords"] is None
        assert sample["wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
        assert sample["outline"]["stroke_width"] > 0
        assert sample["shadow"]["offset_px"] > 0
        assert "subtitle_text_block" in sample["visible_element_authority_ids"]
        assert "safe_area_rectangle" not in sample["visible_element_authority_ids"]
        assert "measured_text_bbox_readback" not in sample["visible_element_authority_ids"]
        assert "frame_center_lines" not in sample["visible_element_authority_ids"]
        assert "sample_mode_label" in sample["visible_element_authority_ids"]
        assert "layout_grid" not in sample["visible_element_authority_ids"]
        assert sample["guide_overlay"]["enabled"] is False
        assert sample["speaker_identity_asset_status"]["real_face_icons_available"] is False
        assert (
            sample["speaker_identity_asset_status"]["production_speaker_identity_design"]
            is False
        )
        if sample["subtitle_mode"] in {"dialogue_badge_left", "speaker_badge_stack"}:
            assert "placeholder_speaker_badge" in sample["visible_element_authority_ids"]
            assert "speaker_accent_color" in sample["visible_element_authority_ids"]
            assert sample["style_inputs"]["badge"]["production_identity_asset"] is False
            assert sample["computed_layout"]["badge_slot"]["authority_class"] == "placeholder"
            assert sample["speaker_identity_asset_status"]["uses_speaker_badge"] is True
            assert sample["speaker_identity_asset_status"]["badge_role"] == "placeholder_speaker_badge"
            assert "placeholder speaker badges only" in sample["speaker_identity_asset_status"]["human_review_note"]
        else:
            assert "placeholder_speaker_badge" not in sample["visible_element_authority_ids"]
            assert sample["style_inputs"]["badge"] is None
            assert sample["speaker_identity_asset_status"]["uses_speaker_badge"] is False

    first_image = spike.Image.open(samples[0]["output_image_path"])
    assert first_image.getpixel((80, 10)) == (36, 39, 44)
    assert first_image.getpixel((35, 32)) == (36, 39, 44)

    guide_overlay = report["guide_overlay"]
    assert guide_overlay["contract_id"] == "subtitle_style_spike_layout_guide_overlay_v0"
    assert guide_overlay["role"] == "review_aid_not_japanese_wrapping_authority"
    assert guide_overlay["clean_samples_distinguishable"] is True
    assert {profile["guide_profile"] for profile in guide_overlay["implemented_profiles"]} == {
        "bottom_center_emphasis_guide_v0",
        "dialogue_badge_left_guide_v0",
    }
    assert {profile["guide_profile"] for profile in guide_overlay["documented_profiles"]} == {
        "speaker_badge_stack_guide_future",
        "status_caption_guide_future",
    }
    guided_samples = guide_overlay["guided_samples"]
    assert len(guided_samples) == 2
    assert {sample["subtitle_mode"] for sample in guided_samples} == {
        "bottom_center_emphasis",
        "dialogue_badge_left",
    }
    for sample in guided_samples:
        image_path = Path(sample["output_image_path"])
        assert image_path.exists()
        assert ".guide" in image_path.name
        assert sample["sample_variant"] == "guide_overlay"
        assert sample["guide_overlay"]["enabled"] is True
        assert sample["guide_overlay"]["snap_to_grid"] is False
        assert sample["guide_overlay"]["japanese_wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
        assert sample["guide_overlay"]["center_lines"]["vertical"]["authority_class"] == "visual_guide_only"
        assert sample["guide_overlay"]["thirds_lines"]["vertical"][0]["authority_class"] == "visual_guide_only"
        assert sample["guide_overlay"]["safe_area"]["authority_class"] == "measured_readback"
        assert sample["guide_overlay"]["text_bbox"]["authority_class"] == "measured_readback"
        assert sample["guide_overlay"]["baseline_lines"]
        assert "safe_area_rectangle" in sample["visible_element_authority_ids"]
        assert "frame_center_lines" in sample["visible_element_authority_ids"]
        assert "frame_thirds_lines" in sample["visible_element_authority_ids"]
        assert "subtitle_baseline_guides" in sample["visible_element_authority_ids"]
        assert "measured_text_bbox_readback" in sample["visible_element_authority_ids"]
        assert "layout_grid" not in sample["visible_element_authority_ids"]
    bottom_guide = next(
        sample for sample in guided_samples if sample["subtitle_mode"] == "bottom_center_emphasis"
    )
    assert bottom_guide["guide_overlay"]["guide_profile"] == "bottom_center_emphasis_guide_v0"
    assert bottom_guide["guide_overlay"]["lower_subtitle_zone"]["authority_class"] == "visual_guide_only"
    assert len(bottom_guide["guide_overlay"]["mode_baseline_targets"]["two_line"]) == 2
    dialogue_guide = next(
        sample for sample in guided_samples if sample["subtitle_mode"] == "dialogue_badge_left"
    )
    assert dialogue_guide["guide_overlay"]["guide_profile"] == "dialogue_badge_left_guide_v0"
    assert dialogue_guide["guide_overlay"]["badge_slot"]["authority_class"] == "placeholder"
    assert dialogue_guide["guide_overlay"]["badge_center_line"]["authority_class"] == "measured_readback"
    assert dialogue_guide["guide_overlay"]["text_start_x"]["authority_class"] == "measured_readback"
    assert dialogue_guide["guide_overlay"]["badge_to_text_gap"]["authority_class"] == "measured_readback"
    assert "badge_slot_guide" in dialogue_guide["visible_element_authority_ids"]
    guided_image = spike.Image.open(dialogue_guide["output_image_path"])
    safe = dialogue_guide["guide_overlay"]["safe_area"]
    assert guided_image.getpixel((safe["left"], safe["top"])) == spike.GUIDE_COLORS["safe_area"]

    json_path = output_dir / "subtitle_style_spike_report.json"
    html_path = output_dir / "subtitle_style_spike_report.html"
    assert json_path.exists()
    assert html_path.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert persisted["review_only"] is True
    assert persisted["production_candidate"] is False
    assert persisted["measured_bbox_provenance"]["status"] == "systematic_measured_readback"
    assert persisted["samples"][0]["measured_bbox"]["width"] > 0
    assert persisted["samples"][0]["measured_output"]["measured_bbox"] == persisted["samples"][0]["measured_bbox"]
    assert persisted["samples"][0]["wrap_algorithm"]["name"] == "japanese_boundary_font_bbox_pixel_wrap_v1"
    assert "candidate_breaks" in persisted["samples"][0]
    assert "measured_width_by_line" in persisted["samples"][0]
    assert len(persisted["guide_overlay"]["guided_samples"]) == 2
    html = html_path.read_text(encoding="utf-8")
    assert "review_only: true" in html
    assert "production_candidate: false" in html
    assert "grid authority: none" in html
    assert "snap-to-grid" in html
    assert "Visible Element Authority" in html
    assert "Measured Bbox Provenance" in html
    assert "style_inputs" in html
    assert "computed_layout" in html
    assert "measured_output" in html
    assert "japanese_boundary_font_bbox_pixel_wrap_v1" in html
    assert "orphan_prevention_applied" in html
    assert "suffix_tail_prevention_applied" in html
    assert "candidate_breaks" in html
    assert "placeholder speaker badges" in html
    assert "real face icons are unavailable" in html
    assert "comparison-only" in html
    assert "Repeated text" in html
    assert "intentional comparison" in html
    assert "clean sample" in html
    assert "guide overlay sample" in html
    assert "Guide Overlay Contract" in html
    assert "bottom_center_emphasis_guide_v0" in html
    assert "dialogue_badge_left_guide_v0" in html
    assert "decorative" in html
    assert "reaction_caption" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_preserves_accepted_font_size_boundary(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_typography_decoration_comparison"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "\u306a\u3093\u3067\u6765\u306a\u304b\u3063\u305f\u3093\u3059\u304b\uff01\uff01",
            "\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052\u307e\u3059",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
    )

    assert report["report_kind"] == "subtitle_typography_decoration_comparison"
    assert report["artifact_id"] == "clip-typography-decoration-comparison-001"
    assert report["human_decision_readback"]["selected_response"] == "adjust_boundary"
    assert report["human_decision_readback"]["font_size"] == (
        "accepted_for_diagnostic_representative_review"
    )
    assert report["human_decision_readback"]["font_family"] == (
        "unresolved_needs_comparison"
    )
    assert report["human_decision_readback"]["decoration"] == (
        "unresolved_needs_comparison"
    )
    assert report["comparison_response_readback"]["selected_response"] == "small_adjustment"
    assert report["comparison_response_readback"]["font_size"] == (
        "accepted_for_diagnostic_representative_review"
    )
    assert report["comparison_response_readback"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert report["comparison_response_readback"]["font_family"] == (
        "narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof"
    )
    assert report["comparison_response_readback"]["decoration"] == (
        "narrowed_to_clean_outline_for_next_diagnostic_proof"
    )
    assert report["comparison_response_readback"]["production_subtitle_design_acceptance"] is False
    assert report["production_candidate"] is False
    assert report["production_subtitle_design_acceptance"] is False
    assert report["production_render_acceptance"] is False
    assert report["creative_acceptance"] is False
    assert report["rights_status"] == "pending"
    assert report["publishing_acceptance"] is False
    assert report["public_use_permission"] is False
    assert report["font_size_policy"]["status"] == "preserved_from_human_review"
    assert report["font_size_policy"]["value"] == 41
    next_route = report["next_diagnostic_overlay_proof_route"]
    assert next_route["route_kind"] == "small_adjustment_diagnostic_overlay_proof"
    assert next_route["target_cuts"] == ["cut_002", "cut_003"]
    assert next_route["selected_candidate_for_next_proof_base"] == (
        "noto_sans_jp_clean_outline"
    )
    assert next_route["recommended_default_candidate_id"] == "noto_sans_jp_clean_outline"
    assert next_route["font_size"]["formula"] == "round(frame_height * 0.115)"
    assert next_route["font_size"]["status"] == (
        "preserve_accepted_diagnostic_representative_direction"
    )
    assert next_route["font_family"] == (
        "narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof"
    )
    assert next_route["decoration"] == (
        "narrowed_to_clean_outline_for_next_diagnostic_proof"
    )
    assert next_route["regenerate_sh08_required"] is False
    assert next_route["episodes_artifact_tracking_allowed"] is False
    assert next_route["production_subtitle_design_acceptance"] is False
    decision_packet = report["small_adjustment_decision_packet"]
    assert decision_packet["decision_state"] == (
        "selected_for_next_diagnostic_overlay_proof_base"
    )
    assert decision_packet["selected_candidate_for_next_proof_base"] == (
        "noto_sans_jp_clean_outline"
    )
    assert decision_packet["recommended_default_candidate_id"] == "noto_sans_jp_clean_outline"
    assert decision_packet["font_size"]["reopen_as_primary_axis"] is False
    assert decision_packet["smallest_next_proof_route"]["default_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert decision_packet["smallest_next_proof_route"]["selected_candidate_id"] == (
        "noto_sans_jp_clean_outline"
    )
    assert decision_packet["smallest_next_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert decision_packet["smallest_next_proof_route"]["regenerate_sh08_required"] is False
    assert {
        option["candidate_id"] for option in decision_packet["options"]
    } == {
        "current_yu_gothic_heavy_outline",
        "noto_sans_jp_clean_outline",
        "meiryo_bold_soft_shadow",
        "gothic_high_contrast_minimal_badge",
    }
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } == {
        "regenerate_sh08_human_preview_session",
        "claim_production_subtitle_design_acceptance",
        "add_cut_008_dense_stress_proof_now",
        "mutate_source_or_rights_or_publishing_state",
    }
    assert report["candidate_count"] == 4
    assert len(report["samples"]) == 8
    assert {sample["candidate_id"] for sample in report["samples"]} == {
        "current_yu_gothic_heavy_outline",
        "noto_sans_jp_clean_outline",
        "meiryo_bold_soft_shadow",
        "gothic_high_contrast_minimal_badge",
    }
    for sample in report["samples"]:
        assert Path(sample["output_image_path"]).exists()
        assert sample["sample_variant"] == "font_family_decoration_comparison"
        assert sample["subtitle_mode"] == "badge_left_dialogue"
        assert sample["font_size_status"] == "accepted_for_diagnostic_representative_review"
        assert sample["requested_font_size"] == 41
        assert sample["style_inputs"]["font_size_axis"] == "fixed_from_human_review"
        assert sample["style_inputs"]["font_family_axis"] == "comparison_candidate"
        assert sample["style_inputs"]["decoration_axis"] == "comparison_candidate"
        assert sample["wrap_algorithm"]["name"] == "japanese_boundary_font_bbox_pixel_wrap_v1"
        assert sample["wrapping_authority"] == "font_bbox_pixel_measurement_not_grid_cell_count"
        assert sample["production_subtitle_design_acceptance"] is False
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_typography_decoration_comparison_report.json"
    html_path = output_dir / "subtitle_typography_decoration_comparison_report.html"
    contact_sheet = output_dir / "subtitle_typography_decoration_contact_sheet.png"
    open_helper = output_dir / "open_comparison.ps1"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    assert open_helper.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["font_size_policy"]["value"] == 41
    assert persisted["comparison_response_readback"]["selected_response"] == "small_adjustment"
    assert persisted["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert persisted["next_diagnostic_overlay_proof_route"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert persisted["small_adjustment_decision_packet"][
        "recommended_default_candidate_id"
    ] == "noto_sans_jp_clean_outline"
    assert persisted["small_adjustment_decision_packet"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert persisted["outputs"]["html"].endswith(
        "subtitle_typography_decoration_comparison_report.html"
    )
    assert "open_comparison.ps1" in persisted["open_commands"]["open_comparison"]
    html = html_path.read_text(encoding="utf-8")
    assert "Source human readback: adjust_boundary" in html
    assert "ED-10g comparison response: small_adjustment" in html
    assert "Next Diagnostic Overlay Proof Route" in html
    assert "Small Adjustment Decision Packet" in html
    assert "noto_sans_jp_clean_outline" in html
    assert "small_adjustment_diagnostic_overlay_proof" in html
    assert "selected_for_next_diagnostic_overlay_proof_base" in html
    assert "production_subtitle_design_acceptance=false" in html
    assert "Current Yu Gothic heavy outline" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_small_adjustment_route(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_typography_decoration_comparison_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10g small adjustment smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-typography-decoration-comparison-001"
    assert payload["comparison_response"]["selected_response"] == "small_adjustment"
    assert payload["selected_candidate_for_next_proof_base"] == (
        "noto_sans_jp_clean_outline"
    )
    assert payload["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "small_adjustment_diagnostic_overlay_proof"
    )
    assert payload["next_diagnostic_overlay_proof_route"][
        "selected_candidate_for_next_proof_base"
    ] == "noto_sans_jp_clean_outline"
    assert payload["next_diagnostic_overlay_proof_route"]["target_cuts"] == [
        "cut_002",
        "cut_003",
    ]
    assert payload["small_adjustment_decision_packet"][
        "recommended_default_candidate_id"
    ] == "noto_sans_jp_clean_outline"
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_kirinuki_gothic_balance_profile_records_weight_outline_review(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_kirinuki_gothic_balance_comparison"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "\u306a\u3093\u3067\u6765\u306a\u304b\u3063\u305f\u3093\u3059\u304b\uff01\uff01",
            "\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052\u307e\u3059",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10i_kirinuki_gothic_balance",
    )

    assert report["report_kind"] == "subtitle_kirinuki_gothic_weight_balance_comparison"
    assert report["artifact_id"] == "clip-ed10i-kirinuki-gothic-balance-001"
    assert report["comparison_profile"] == "ed10i_kirinuki_gothic_balance"
    assert report["human_decision_readback"]["selected_response"] == (
        "not_accepted_as_is"
    )
    assert report["human_decision_readback"]["preferred_direction"] == (
        "kirinuki_youtube_style_gothic"
    )
    assert report["human_decision_readback"]["desired_adjustment"] == (
        "make_glyph_body_thicker_so_outline_does_not_dominate"
    )
    assert report["comparison_response_readback"]["emoji_treatment"] == (
        "neutral_ignore_for_evaluation"
    )
    assert report["comparison_response_readback"]["selected_candidate_for_next_proof_base"] == (
        "pending_ed10i_human_review"
    )
    assert report["candidate_count"] == 4
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10i_reference_noto_clean_outline",
        "ed10i_biz_udgothic_bold_balanced_outline",
        "ed10i_yu_gothic_bold_thin_outline",
        "ed10i_meiryo_bold_fill_outline_balance",
    }
    assert report["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "kirinuki_gothic_weight_balance_diagnostic_proof"
    )
    assert report["next_diagnostic_overlay_proof_route"][
        "recommended_default_candidate_id"
    ] == "ed10i_biz_udgothic_bold_balanced_outline"
    decision_packet = report["kirinuki_gothic_balance_decision_packet"]
    assert decision_packet["decision_state"] == "generated_requires_human_review"
    assert decision_packet["current_reference_not_accepted_as_is"] is True
    assert decision_packet["font_size"]["reopen_as_primary_axis"] is False
    assert decision_packet["emoji_treatment"]["optimize_in_this_slice"] is False
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } >= {
        "broaden_to_all_font_sweep",
        "optimize_emoji_rendering",
        "vendor_third_party_font_binaries",
        "claim_production_subtitle_design_acceptance",
    }
    assert len(report["samples"]) == 8
    for sample in report["samples"]:
        assert sample["sample_variant"] == "kirinuki_gothic_weight_balance_comparison"
        assert sample["style_inputs"]["body_weight_axis"]
        assert sample["style_inputs"]["outline_balance_axis"]
        assert sample["style_inputs"]["emoji_evaluation_scope"] == (
            "emoji_neutral_ignored_for_ed10i"
        )
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_kirinuki_gothic_balance_comparison_report.json"
    html_path = output_dir / "subtitle_kirinuki_gothic_balance_comparison_report.html"
    contact_sheet = output_dir / "subtitle_kirinuki_gothic_balance_contact_sheet.png"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["comparison_profile"] == "ed10i_kirinuki_gothic_balance"
    html = html_path.read_text(encoding="utf-8")
    assert "ED-10i Kirinuki Gothic Weight Balance Comparison" in html
    assert "Kirinuki Gothic Balance Decision Packet" in html
    assert "emoji_neutral_ignored_for_ed10i" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10i_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10i_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10i_kirinuki_gothic_balance",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10i kirinuki gothic balance smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10i-kirinuki-gothic-balance-001"
    assert payload["comparison_profile"] == "ed10i_kirinuki_gothic_balance"
    assert payload["comparison_response"]["selected_response"] == (
        "generate_narrow_kirinuki_gothic_balance_comparison"
    )
    assert payload["selected_candidate_for_next_proof_base"] == (
        "pending_ed10i_human_review"
    )
    assert payload["comparison_decision_packet"]["recommended_default_candidate_id"] == (
        "ed10i_biz_udgothic_bold_balanced_outline"
    )
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_kirinuki_font_audit_profile_consumes_meiryo_freeform_review(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_kirinuki_font_audit"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "\u56e3\u9577\u3001\u3061\u306a\u307f\u306b\u3001\u4ed6\u306e\u756a\u9577\u77e5\u3063\u3066\u307e\u3059\u304b\uff1f",
            "\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052\u307e\u3059",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10j_kirinuki_font_audit",
    )

    assert report["report_kind"] == "subtitle_kirinuki_font_research_candidate_audit"
    assert report["artifact_id"] == "clip-ed10j-kirinuki-font-audit-001"
    assert report["comparison_profile"] == "ed10j_kirinuki_font_audit"
    assert report["human_decision_readback"]["selected_response"] == (
        "freeform_review_not_accepted_as_normal_baseline"
    )
    assert report["human_decision_readback"][
        "current_meiryo_proof_accepted_as_normal_baseline"
    ] is False
    assert report["human_decision_readback"]["meiryo_role"] == (
        "reviewed_reference_candidate_not_selected_baseline"
    )
    assert report["comparison_response_readback"][
        "selected_candidate_for_next_proof_base"
    ] == "ed10j_biz_udgothic_bold_telop_candidate"
    assert report["comparison_response_readback"]["blue_badge_candidate_id"] == (
        "ed10j_noto_sans_jp_local_telop_candidate"
    )
    assert report["comparison_response_readback"]["blue_badge_is_meiryo_reference"] is False
    assert report["candidate_count"] == 4
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10j_reference_meiryo_reviewed_not_baseline",
        "ed10j_biz_udgothic_bold_telop_candidate",
        "ed10j_yu_gothic_bold_system_candidate",
        "ed10j_noto_sans_jp_local_telop_candidate",
    }
    assert report["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "ed10j_review_consumed_ed10k_biz_overlay_proof"
    )
    assert report["next_diagnostic_overlay_proof_route"][
        "selected_candidate_for_next_proof_base"
    ] == "ed10j_biz_udgothic_bold_telop_candidate"
    assert report["next_diagnostic_overlay_proof_route"][
        "selected_overlay_artifact_id"
    ] == "clip-ed10k-biz-overlay-proof-001"
    assert report["next_diagnostic_overlay_proof_route"][
        "recommended_default_candidate_id"
    ] == "ed10j_biz_udgothic_bold_telop_candidate"
    decision_packet = report["kirinuki_font_audit_decision_packet"]
    assert decision_packet["decision_state"] == "review_consumed_next_overlay_proof_selected"
    assert decision_packet["current_meiryo_proof_accepted_as_normal_baseline"] is False
    assert decision_packet["freeform_review_consumed"][
        "meiryo_removed_from_normal_baseline_candidates"
    ] is True
    assert decision_packet["badge_color_readback"]["blue_badge_candidate_id"] == (
        "ed10j_noto_sans_jp_local_telop_candidate"
    )
    assert decision_packet["badge_color_readback"]["blue_badge_is_meiryo_reference"] is False
    assert decision_packet["font_size"]["reopen_as_primary_axis"] is False
    assert decision_packet["emoji_treatment"]["optimize_in_this_slice"] is False
    assert {
        bucket["bucket"] for bucket in decision_packet["candidate_buckets"]
    } == {
        "system_default_safe",
        "reviewed_reference_only",
        "likely_video_telop_friendly_local",
        "local_only_reproducibility_weak",
        "later_download_license_decision",
    }
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } >= {
        "treat_meiryo_overlay_as_accepted_normal_baseline",
        "minor_meiryo_outline_tweak_only",
        "download_or_vendor_third_party_fonts_now",
        "broaden_to_narration_mincho_or_display_fonts",
        "claim_production_subtitle_design_acceptance",
    }
    assert len(report["samples"]) == 8
    for sample in report["samples"]:
        assert sample["sample_variant"] == "kirinuki_font_research_candidate_audit"
        assert sample["style_inputs"]["emoji_evaluation_scope"] == (
            "emoji_neutral_ignored_for_ed10j"
        )
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_kirinuki_font_audit_report.json"
    html_path = output_dir / "subtitle_kirinuki_font_audit_report.html"
    contact_sheet = output_dir / "subtitle_kirinuki_font_audit_contact_sheet.png"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["comparison_profile"] == "ed10j_kirinuki_font_audit"
    html = html_path.read_text(encoding="utf-8")
    assert "ED-10j Kirinuki Subtitle Font Research" in html
    assert "Kirinuki Font Audit Decision Packet" in html
    assert "reviewed_reference_candidate_not_selected_baseline" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_known_kirinuki_font_pack_profile_consumes_biz_freeform_review(
    tmp_path: Path,
):
    output_dir = tmp_path / "subtitle_known_kirinuki_font_pack_comparison"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "\u56e3\u9577\u3001\u3061\u306a\u307f\u306b\u3001\u4ed6\u306e\u756a\u9577\u77e5\u3063\u3066\u307e\u3059\u304b\uff1f",
            "\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052\u307e\u3059",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10l_known_kirinuki_font_pack",
    )

    assert report["report_kind"] == "subtitle_known_kirinuki_font_pack_audit"
    assert report["artifact_id"] == "clip-ed10l-known-kirinuki-font-pack-001"
    assert report["comparison_profile"] == "ed10l_known_kirinuki_font_pack"
    assert report["human_decision_readback"]["selected_response"] == (
        "freeform_review_biz_not_accepted_as_normal_baseline"
    )
    assert report["human_decision_readback"][
        "current_biz_proof_accepted_as_normal_baseline"
    ] is False
    assert report["human_decision_readback"]["system_safe_route_role"] == (
        "reference_rejected_for_this_use_case"
    )
    local_readback = report["known_kirinuki_font_pack_decision_packet"][
        "research_readback"
    ]["local_font_readback"]
    found_known_font_candidate_ids = set(local_readback["target_candidate_ids_found"])
    all_known_fonts_found = not local_readback["target_candidate_ids_missing"]
    any_known_fonts_found = bool(found_known_font_candidate_ids)
    assert report["comparison_response_readback"]["selected_response"] == (
        "per_user_font_readback_valid_route_to_keifont_overlay_proof"
        if all_known_fonts_found
        else "fallback_confirmed_route_to_font_install_readback"
    )
    assert report["comparison_response_readback"][
        "selected_candidate_for_next_proof_base"
    ] == (
        "ed10l_keifont_pop_dialogue_candidate"
        if all_known_fonts_found
        else "pending_real_font_install_readback_after_fallback_confirmation"
    )
    assert report["comparison_response_readback"][
        "candidate_selection_from_current_pngs_allowed"
    ] is all_known_fonts_found
    assert report["comparison_response_readback"][
        "recommended_default_candidate_id"
    ] == "ed10l_keifont_pop_dialogue_candidate"
    assert report["candidate_count"] == 4
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10l_keifont_pop_dialogue_candidate",
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_m_plus_fonts_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    }
    route = report["next_diagnostic_overlay_proof_route"]
    assert route["route_kind"] == (
        "ed10n_keifont_overlay_proof_after_per_user_font_readback"
        if all_known_fonts_found
        else "ed10l_known_font_pack_install_readback_before_visual_proof"
    )
    assert route["current_fallback_contact_sheet_role"] == (
        "real_font_visual_comparison_after_per_user_readback"
        if all_known_fonts_found
        else "readback_only_not_visual_selection"
    )
    assert route["recommended_default_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert route["font_binaries_downloaded"] is False
    decision_packet = report["known_kirinuki_font_pack_decision_packet"]
    if all_known_fonts_found:
        assert decision_packet["decision_state"] == (
            "per_user_font_readback_valid_real_font_evidence"
        )
        assert (
            decision_packet["selected_candidate_for_next_proof_base"]
            == "ed10l_keifont_pop_dialogue_candidate"
        )
        assert decision_packet["candidate_selection_from_current_pngs_allowed"] is True
    else:
        assert decision_packet["decision_state"] == (
            "font_fallback_confirmed_visual_selection_invalid"
        )
        assert (
            decision_packet["candidate_selection_from_current_pngs_allowed"] is False
        )
    assert decision_packet["current_biz_proof_accepted_as_normal_baseline"] is False
    assert decision_packet["self_diagnosis"]["candidate_universe_bias"] == (
        "system_safe_generic_readability"
    )
    assert decision_packet["self_diagnosis"][
        "safe_reproducible_conflated_with_strong_kirinuki_design"
    ] is True
    assert decision_packet["self_diagnosis"][
        "user_known_good_domain_knowledge_not_elevated_early_enough"
    ] is True
    assert {
        slot["slot"] for slot in decision_packet["usage_slots"]
    } == {
        "normal_dialogue_baseline",
        "emphasis_shout_tsukkomi",
        "mood_literary",
    }
    assert {
        bucket["bucket"] for bucket in decision_packet["candidate_buckets"]
    } == {
        "strong_design_candidates",
        "locally_available_now",
        "requires_download_install",
        "requires_explicit_license_handling",
        "reference_rejected_for_normal_baseline",
    }
    assert local_readback["font_readback_sources"] == [
        "HKCU:Software/Microsoft/Windows NT/CurrentVersion/Fonts",
        "HKLM:Software/Microsoft/Windows NT/CurrentVersion/Fonts",
        "%LOCALAPPDATA%/Microsoft/Windows/Fonts",
        "C:/Windows/Fonts",
    ]
    if all_known_fonts_found:
        assert set(local_readback["target_fonts_found"]) == {
            "Keifont",
            "851 Chikara Yowaku",
            "M+ FONTS",
            "Yasashisa Gothic",
        }
        assert local_readback["target_fonts_missing"] == []
        assert local_readback["current_png_valid_visual_evidence"] is True
        assert report["font_visual_comparison_validity"]["status"] == (
            "valid_requested_font_visual_evidence"
        )
        assert report["font_visual_comparison_validity"][
            "all_candidates_valid_real_font"
        ] is True
    else:
        assert local_readback["current_png_valid_visual_evidence"] is False
        expected_status = (
            "mixed_real_and_fallback_font_visual_evidence"
            if any_known_fonts_found
            else "invalid_fallback_render_not_target_font_visual_evidence"
        )
        assert report["font_visual_comparison_validity"]["status"] == (
            expected_status
        )
        assert report["font_visual_comparison_validity"][
            "all_candidates_valid_real_font"
        ] is False
        assert report["font_visual_comparison_validity"][
            "any_candidate_valid_real_font"
        ] is any_known_fonts_found
    assert {
        row["current_png_valid_visual_evidence"]
        for row in report["font_visual_comparison_validity"]["candidate_resolution"]
    } == (
        {True}
        if all_known_fonts_found
        else ({True, False} if any_known_fonts_found else {False})
    )
    assert {
        route["route"] for route in decision_packet["rejected_alternatives"]
    } >= {
        "treat_biz_udgothic_overlay_as_accepted_normal_baseline",
        "continue_biz_noto_meiryo_system_safe_tuning_as_main_route",
        "select_candidate_from_current_fallback_contact_sheet",
        "download_or_vendor_font_binaries_now",
        "claim_production_subtitle_design_acceptance",
    }
    assert len(report["samples"]) == 8
    for sample in report["samples"]:
        assert sample["sample_variant"] == (
            "known_kirinuki_font_pack_normal_dialogue_comparison"
        )
        assert sample["style_inputs"]["emoji_evaluation_scope"] == (
            "emoji_neutral_ignored_for_ed10l"
        )
        if all_known_fonts_found:
            assert sample["font_file_status"] == "candidate_primary_font_file_found"
            assert sample["font_fallback_status"] == "requested_candidate_font_file_found"
            assert sample["visual_comparison_validity"] == (
                "valid_requested_font_visual_evidence"
            )
        elif sample["candidate_id"] in found_known_font_candidate_ids:
            assert sample["font_file_status"] == "candidate_primary_font_file_found"
            assert sample["font_fallback_status"] == "requested_candidate_font_file_found"
            assert sample["visual_comparison_validity"] == (
                "valid_requested_font_visual_evidence"
            )
        else:
            assert sample["font_file_status"].startswith(
                "requested_candidate_font_missing_used_"
            )
            assert sample["font_fallback_status"] == (
                "requested_candidate_missing_fallback_font_used"
            )
            assert sample["visual_comparison_validity"] == (
                "invalid_fallback_render_not_target_font_visual_evidence"
            )
        assert sample["production_candidate"] is False

    json_path = output_dir / "subtitle_known_kirinuki_font_pack_report.json"
    html_path = output_dir / "subtitle_known_kirinuki_font_pack_report.html"
    contact_sheet = output_dir / "subtitle_known_kirinuki_font_pack_contact_sheet.png"
    assert json_path.exists()
    assert html_path.exists()
    assert contact_sheet.exists()
    persisted = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.read_text(encoding="utf-8").isascii()
    assert persisted["comparison_profile"] == "ed10l_known_kirinuki_font_pack"
    html = html_path.read_text(encoding="utf-8")
    assert "ED-10l Known Kirinuki Font Pack Audit" in html
    assert "Known Kirinuki Font Pack Decision Packet" in html
    assert "system_safe_generic_readability" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10j_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10j_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10j_kirinuki_font_audit",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10j kirinuki font audit smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10j-kirinuki-font-audit-001"
    assert payload["comparison_profile"] == "ed10j_kirinuki_font_audit"
    assert payload["comparison_response"]["selected_response"] == (
        "freeform_review_consumed_move_to_biz_overlay_proof"
    )
    assert payload["selected_candidate_for_next_proof_base"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert payload["comparison_decision_packet"]["recommended_default_candidate_id"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10l_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10l_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10l_known_kirinuki_font_pack",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10l known kirinuki font pack smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10l-known-kirinuki-font-pack-001"
    assert payload["comparison_profile"] == "ed10l_known_kirinuki_font_pack"
    all_known_fonts_found = not payload["comparison_decision_packet"][
        "research_readback"
    ]["local_font_readback"]["target_candidate_ids_missing"]
    assert payload["comparison_response"]["selected_response"] == (
        "per_user_font_readback_valid_route_to_keifont_overlay_proof"
        if all_known_fonts_found
        else "fallback_confirmed_route_to_font_install_readback"
    )
    assert payload["selected_candidate_for_next_proof_base"] == (
        "ed10l_keifont_pop_dialogue_candidate"
        if all_known_fonts_found
        else "pending_real_font_install_readback_after_fallback_confirmation"
    )
    assert payload["comparison_decision_packet"]["recommended_default_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert payload["comparison_decision_packet"]["self_diagnosis"][
        "candidate_universe_bias"
    ] == "system_safe_generic_readability"
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_multifont_focused_review_profile_builds_same_line_matrix(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10o_multifont"

    report = spike.build_subtitle_typography_decoration_comparison(
        output_dir=output_dir,
        sample_texts=[
            "\u306a\u3093\u3067\u6765\u306a\u304b\u3063\u305f\u3093\u3059\u304b\uff01\uff01",
            "\u307e\u3042\u8b1d\u308b\u3093\u306a\u3089\u8a31\u3057\u3066\u3042\u3052\u307e\u3059",
        ],
        canvas_size=(640, 360),
        base_dir=tmp_path,
        comparison_profile="ed10o_multifont_focused_review",
    )

    assert report["artifact_id"] == "clip-ed10o-multifont-focused-review-001"
    assert report["comparison_profile"] == "ed10o_multifont_focused_review"
    assert report["report_kind"] == "subtitle_multifont_focused_review_surface"
    assert report["candidate_count"] == 3
    assert len(report["samples"]) == 6
    assert {candidate["candidate_id"] for candidate in report["candidates"]} == {
        "ed10l_keifont_pop_dialogue_candidate",
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    }
    assert report["focused_review_surface"]["primary_visual"] == (
        "subtitle_area_crop_matrix"
    )
    assert report["focused_review_surface"]["current_lead_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert report["excluded_candidates"] == [
        {
            "candidate_id": "ed10l_m_plus_fonts_dialogue_candidate",
            "reason": "weight_style_unresolved",
            "readback": (
                "registry_display_name=M PLUS 1 Thin; "
                "file=MPLUS1-VariableFont_wght.ttf"
            ),
            "next_action": (
                "pin an exact non-thin M+ weight/style before including it "
                "in baseline comparison"
            ),
        }
    ]
    assert {
        sample["sample_text_index"] for sample in report["samples"]
    } == {1, 2}
    assert {
        sample["sample_variant"] for sample in report["samples"]
    } == {"ed10o_multifont_same_line_subtitle_area_comparison"}
    assert report["next_diagnostic_overlay_proof_route"]["route_kind"] == (
        "ed10o_multifont_review_then_bounded_next_proof"
    )
    assert report["production_subtitle_design_acceptance"] is False
    assert report["rights_status"] == "pending"

    html_path = output_dir / "subtitle_multifont_focused_review_report.html"
    matrix_path = output_dir / "subtitle_multifont_focused_review_matrix.png"
    assert html_path.exists()
    assert matrix_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "Review Focus" in html
    assert "Focused Matrix" in html
    assert "Excluded From This One-shot Comparison" in html
    assert "ed10l_m_plus_fonts_dialogue_candidate" in html


@pytest.mark.skipif(
    spike.Image is None,
    reason="Pillow optional local review tool is not installed",
)
def test_typography_decoration_comparison_cli_reports_ed10o_profile(
    tmp_path: Path,
):
    output_dir = tmp_path / "ed10o_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-subtitle-typography-decoration-comparison",
            "--comparison-profile",
            "ed10o_multifont_focused_review",
            "--output-dir",
            str(output_dir),
            "--target-cut",
            "cut_002",
            "--target-cut",
            "cut_003",
            "--sample-text",
            "ED-10o one-shot font comparison smoke",
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "clip-ed10o-multifont-focused-review-001"
    assert payload["comparison_profile"] == "ed10o_multifont_focused_review"
    assert payload["candidate_count"] == 3
    assert payload["comparison_response"]["selected_response"] == (
        "build_one_shot_multifont_focused_review_surface"
    )
    assert payload["focused_review_surface"]["primary_visual"] == (
        "subtitle_area_crop_matrix"
    )
    assert payload["excluded_candidates"][0]["reason"] == "weight_style_unresolved"
    assert payload["production_subtitle_design_acceptance"] is False
    assert Path(payload["outputs"]["html"]).exists()
