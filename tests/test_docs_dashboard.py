"""Docs v1.5 dashboard tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from src.pipeline.docs_dashboard import (
    _front_matter,
    build_project_status,
    write_project_status,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_front_matter_treats_yaml_null_as_unavailable() -> None:
    metadata = _front_matter("---\nhuman_entrypoint: null\nmachine_readback: ~\n---\n")

    assert metadata["human_entrypoint"] == ""
    assert metadata["machine_readback"] == ""


def test_docs_dashboard_omits_unavailable_current_focus_surface(tmp_path: Path) -> None:
    _write_fixture_docs(tmp_path)
    _write_runtime_state(
        tmp_path,
        human_entrypoint="null",
        review_open_command="null",
        machine_readback="null",
    )

    result = write_project_status(
        base_dir=tmp_path,
        output_dir=tmp_path / "docs" / "dashboard",
        generated_at="test-run",
    )
    status = result["status"]

    assert all(item["command"] and item["target"] for item in status["open_surfaces"])
    assert all(
        item["label"] != "FIX-01 Current Focus" for item in status["open_surfaces"]
    )
    html = result["html_path"].read_text(encoding="utf-8")
    assert "<th>entrypoint</th><td></td>" not in html
    assert "<th>machine readback</th><td></td>" not in html


def test_docs_dashboard_detects_unclear_and_over_guarded_docs(tmp_path: Path):
    _write_fixture_docs(tmp_path)

    result = write_project_status(
        base_dir=tmp_path,
        output_dir=tmp_path / "docs" / "dashboard",
        generated_at="test-run",
    )

    status = result["status"]
    findings = status["doc_health"]["findings"]
    assert status["schema_id"] == "clippipegen.docs_dashboard.v1_5"
    assert status["project"]["wiki_entry"] == "docs/index.md"
    focus = status["current_focus"]
    assert focus["feature_id"] == "FIX-01"
    assert focus["artifact_id"] == "clip-test-artifact"
    assert focus["state"] == "fixture_ready"
    assert focus["title"] == "Fixture Current Focus"
    assert focus["active_branch"] == "codex/fixture-current-state"
    assert focus["phase"] == "review_ready"
    assert focus["canonical_main_head"] == "fixture-main-head"
    assert focus["canonical_main_baseline"] == "Fixture accepted baseline"
    assert focus["canonical_status"] == "fixture_branch_review_pending"
    assert focus["review_status"] == "fixture_review_ready"
    assert focus["human_entrypoint"] == "docs/fixture_focus.html"
    assert focus["review_open_command"] == "start docs\\fixture_focus.html"
    assert focus["machine_readback"] == "docs/fixture_focus.json"
    assert focus["remote_code_complete"] == "true"
    assert focus["local_artifact_available"] == "true"
    assert focus["cross_machine_resume_class"] == "reacquirable"
    assert focus["active_rebuild_contract"] == "artifacts/ACTIVE_REBUILD.json"
    assert focus["accepted_baseline_sha256"] == "a" * 64
    assert focus["recommended_cover_path"] == "docs/fixture_cover.png"
    assert focus["recommended_cover_sha256"] == "b" * 64
    assert focus["recommended_cover_timestamp_seconds"] == "11.930"
    assert focus["recommended_cover_selection_status"] == (
        "recommended_pending_human_acceptance"
    )
    assert focus["handoff"] == "docs/CURRENT_HANDOFF.md"
    assert focus["last_verified_at"] == "2026-07-10"
    assert focus["decision_required"] == "fixture_decision"
    assert focus["next_review_action_type"] == "review_fixture_focus"
    assert focus["next_action"] == "Review the fixture current focus."
    assert focus["source_metadata"] == "docs/RUNTIME_STATE.md"
    assert [item["command"] for item in status["open_surfaces"][:3]] == [
        ".\\open-dashboard.ps1",
        "start docs\\fixture_focus.html",
        ".\\open-artifacts.ps1",
    ]
    assert status["open_surfaces"][1]["target"] == "docs/fixture_focus.html"
    assert status["open_surfaces"][1]["when_to_use"] == (
        "Review the fixture current focus."
    )
    assert status["next_review_items"][0]["artifact"] == "clip-test-artifact"
    assert status["next_review_items"][0]["next_route"] == (
        "Review the fixture current focus."
    )
    assert status["artifact_coverage"]["current_focus_artifact_registered"] is True
    assert (
        status["doc_health"]["finding_total"] >= status["doc_health"]["finding_count"]
    )
    assert status["doc_health"]["finding_limit"] == 50
    assert status["feature_summary"]["status_counts"]["done"] == 1
    assert status["features"][0]["id"] == "ED-01"
    assert status["features"][0]["progress_pct"] == 100
    assert status["artifact_coverage"]["registered_artifact_count"] == 1
    assert status["next_review_items"][0]["item"].startswith("FIX-01")
    assert status["next_review_items"][1]["artifact"] == (
        "clip-ed10bc-thank-v2-open-command-repair-readback-001"
    )
    assert "clip-test-artifact" in status["artifact_summary"]["artifact_ids"]
    assert {finding["type"] for finding in findings} >= {"unclear", "over_guarded"}
    assert result["json_path"].exists()
    assert result["html_path"].exists()
    assert result["features_path"].exists()

    persisted = json.loads(result["json_path"].read_text(encoding="utf-8"))
    html = result["html_path"].read_text(encoding="utf-8")
    features_index = result["features_path"].read_text(encoding="utf-8")
    assert persisted["generated_at"] == "test-run"
    assert [item["target"] for item in persisted["open_surfaces"][:3]] == [
        "docs/dashboard/index.html",
        "docs/fixture_focus.html",
        "artifacts/ARTIFACTS.md",
    ]
    assert persisted["current_focus"]["artifact_id"] == "clip-test-artifact"
    assert persisted["next_review_items"][0]["artifact"] == "clip-test-artifact"
    assert "Open Surfaces" in html
    assert "clip-test-artifact" in html
    assert "Review the fixture current focus." in html
    assert "subtitle_known_kirinuki_font_pack" in html
    assert "subtitle_kirinuki_font_audit" in html
    assert "Doc Health Findings" in html
    assert "Feature Progress" in html
    assert "Active Artifacts" in html
    assert "Next Review Items" in html
    assert (
        "clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001"
        in html
    )
    assert "clip-ed10au-representative-micro-scene-internal-review-specimen-001" in html
    assert "clip-ed10at-internal-review-observation-readback-001" in html
    assert "clip-ed10as-internal-review-access-sheet-fullpath-001" in html
    assert "clip-ed10ar-internal-review-video-candidate-package-001" in html
    assert (
        "clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001" in html
    )
    assert (
        "clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001" in html
    )
    assert "clip-ed10an-production-limitation-lift-stage-2-decision-packet-001" in html
    assert "clip-ed10am-production-limitation-lift-stage-1-001" in html
    assert "clip-ed10al-final-render-path-stage-3-rehearsal-001" in html
    assert "clip-ed10ak-final-render-path-stage-2-replayability-001" in html
    assert "clip-ed10aj-final-render-path-stage-1-001" in html
    assert "clip-ed10ai-final-render-path-readiness-packet-001" in html
    assert "clip-ed10ah-production-limitation-lift-entry-001" in html
    assert "clip-ed10ah-render-readiness-separation-readback-001" in html
    assert "clip-ed10r-keifont-dense-stress-proof-001" in html
    assert "clip-ed10z-tiny-render-path-nearer-probe-001" in html
    assert "clip-ed10aa-subtitle-style-intent-registry-001" in html
    assert "clip-ed10ab-subtitle-preset-selector-001" in html
    assert "clip-ed10ac-visual-selector-proof-001" in html
    assert "clip-ed10ad-style-family-palette-axis-proof-001" in html
    assert "clip-ed10ae-render-path-selector-contract-probe-001" in html
    assert "clip-ed10af-l2-render-path-selector-probe-001" in html
    assert "clip-ed10ag-lineage-and-observation-surface-001" in html
    assert "clip-ed10p-keifont-lead-representative-proof-001" in html
    assert "clip-ed10o-multifont-focused-review-001" in html
    assert "subtitle_multifont_focused_review" in html
    assert "clip-ed10n-keifont-overlay-proof-001" in html
    assert "clip-ed10l-known-kirinuki-font-pack-001" in html
    assert "| ED-01 | Editing | done | stable | 100 |  |" in features_index


def test_docs_dashboard_default_state_follows_runtime_front_matter(tmp_path: Path):
    _write_fixture_docs(tmp_path)

    initial = build_project_status(base_dir=tmp_path)

    assert initial["generated_at"] == "2026-07-10"
    assert initial["current_focus"]["feature_id"] == "FIX-01"
    assert initial["current_focus"]["artifact_id"] == "clip-test-artifact"

    _write_runtime_state(
        tmp_path,
        health="fixture_updated",
        last_touched="2026-07-12",
        last_verified_at="2026-07-11",
        current_slice="FIX-02",
        active_branch="codex/fixture-updated-state",
        current_title="Updated Fixture Current Focus",
        human_entrypoint="docs/updated_fixture_focus.html",
        review_open_command="start docs\\updated_fixture_focus.html",
        machine_readback="docs/updated_fixture_focus.json",
        active_artifact="clip-updated-test-artifact",
        next_review_due="review_updated_fixture_focus",
        next_action="Review the updated fixture current focus.",
        decision_required="updated_fixture_decision",
    )

    updated = build_project_status(base_dir=tmp_path)
    focus = updated["current_focus"]

    assert updated["generated_at"] == "2026-07-11"
    assert focus["feature_id"] == "FIX-02"
    assert focus["artifact_id"] == "clip-updated-test-artifact"
    assert focus["state"] == "fixture_updated"
    assert focus["active_branch"] == "codex/fixture-updated-state"
    assert focus["title"] == "Updated Fixture Current Focus"
    assert focus["human_entrypoint"] == "docs/updated_fixture_focus.html"
    assert focus["review_open_command"] == "start docs\\updated_fixture_focus.html"
    assert focus["machine_readback"] == "docs/updated_fixture_focus.json"
    assert focus["next_action"] == "Review the updated fixture current focus."
    assert updated["open_surfaces"][1]["target"] == ("docs/updated_fixture_focus.html")
    assert updated["open_surfaces"][1]["when_to_use"] == (
        "Review the updated fixture current focus."
    )
    assert updated["next_review_items"][0]["artifact"] == ("clip-updated-test-artifact")
    assert updated["next_review_items"][0]["next_route"] == (
        "Review the updated fixture current focus."
    )


def test_docs_dashboard_default_generation_is_deterministic(tmp_path: Path):
    _write_fixture_docs(tmp_path)
    output_dir = tmp_path / "docs" / "dashboard"

    first = write_project_status(base_dir=tmp_path, output_dir=output_dir)
    first_bytes = {
        key: first[key].read_bytes()
        for key in ("json_path", "html_path", "features_path")
    }

    second = write_project_status(base_dir=tmp_path, output_dir=output_dir)
    second_bytes = {
        key: second[key].read_bytes()
        for key in ("json_path", "html_path", "features_path")
    }

    assert second["status"]["generated_at"] == "2026-07-10"
    assert second_bytes == first_bytes


def test_artifact_registry_open_commands_are_not_polluted_by_ed10aq_notepad():
    text = (REPO_ROOT / "artifacts" / "ARTIFACTS.md").read_text(encoding="utf-8")
    stage5_open = (
        "notepad docs\\\\style_intent\\\\"
        "subtitle-production-limitation-lift-stage-5-user-decision-ready.md"
    )

    assert text.count(stage5_open) == 1
    assert f"| open_command | {stage5_open} |```" not in text
    assert f"| open_command | {stage5_open} |Historical" not in text
    assert f"| open_command | {stage5_open} |Fallback" not in text


def test_ed10az_route_decision_is_registered_in_dashboard_inputs():
    status = build_project_status(base_dir=REPO_ROOT, generated_at="test-run")

    feature_by_id = {item["id"]: item for item in status["features"]}
    assert feature_by_id["ED-10az"]["active_artifact"] == (
        "clip-ed10az-observation-readback-and-v2-route-decision-001"
    )

    artifact_ids = set(status["artifact_summary"]["artifact_ids"])
    assert "clip-ed10az-observation-readback-and-v2-route-decision-001" in artifact_ids
    artifact_by_id = {item["artifact_id"]: item for item in status["active_artifacts"]}
    assert artifact_by_id["clip-ed10az-observation-readback-and-v2-route-decision-001"][
        "repo_relative_path"
    ] == (
        "docs/style_intent/ed10az-observation-readback-and-v2-route-decision.json; "
        "docs/style_intent/ed10az-observation-readback-and-v2-route-decision.md"
    )


def test_ed10bc_resume_surfaces_are_current_and_ed10ba_sources_remain_linked():
    current_out09_artifact = "clip-out09-second-source-short-repeatability-v0-001"
    current_out06_artifact = (
        "clip-out06-complete-narrative-short-delivery-candidate-v0-001"
    )
    accepted_out05_artifact = "clip-out05-vertical-short-internal-candidate-v0-001"
    current_out04_artifact = "clip-out04-editorial-representative-sequence-v0-001"
    current_out03_artifact = "clip-out03-real-local-selected-cut-proof-v0-001"
    baseline_out02_artifact = "clip-out02-local-fixture-output-proof-smoke-v0-001"
    current_int_artifact = "clip-int01-parallel-lane-aggregation-v0-001"
    current_ews_artifact = "clip-ews05-human-ok-fetch-prep-ready-package-v0-001"
    current_ews_fetch_prep_artifact = "clip-ews04-source-fetch-prep-planner-v0-001"
    current_ews_decision_artifact = "clip-ews03-source-identity-decision-intake-v0-001"
    current_ews_inspector_artifact = "clip-ews02-episode-workspace-inspector-v0-001"
    current_ews_spine_artifact = "clip-ews01-episode-workspace-spine-v0-001"
    current_cpd_artifact = "clip-cpd12-minimal-review-console-v0-001"
    active_artifact = "clip-ed10bc-thank-v2-open-command-repair-readback-001"
    active_json = "docs/style_intent/thank-v2-open-command-repair-readback.json"
    active_md = "docs/style_intent/thank-v2-open-command-repair-readback.md"
    source_access_artifact = (
        "clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001"
    )
    source_access_json = (
        "docs/style_intent/thank-ed10ba-v2-local-access-recovery-readback.json"
    )
    source_access_md = (
        "docs/style_intent/thank-ed10ba-v2-local-access-recovery-readback.md"
    )
    source_v2_artifact = "clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001"
    source_v2_json = "docs/style_intent/representative-micro-scene-v2-cut-window-and-review-purpose-alignment.json"
    source_v2_md = "docs/style_intent/representative-micro-scene-v2-cut-window-and-review-purpose-alignment.md"
    active_launcher = (
        "open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1"
    )
    route_decision = "clip-ed10az-observation-readback-and-v2-route-decision-001"
    route_decision_json = (
        "docs/style_intent/ed10az-observation-readback-and-v2-route-decision.json"
    )
    review_frame_surface = "clip-ed10ax-review-frame-clarification-surface-001"
    source_review_frame_plan = (
        "clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001"
    )
    source_plan_json = "docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.json"
    source_plan_md = "docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md"
    source_frame_readback = "clip-ed10av-micro-scene-observation-frame-readback-001"
    source_specimen = (
        "clip-ed10au-representative-micro-scene-internal-review-specimen-001"
    )
    observation_artifact = "clip-ed10at-internal-review-observation-readback-001"
    access_artifact = "clip-ed10as-internal-review-access-sheet-fullpath-001"
    source_artifact = "clip-ed10ar-internal-review-video-candidate-package-001"

    for path in [
        REPO_ROOT / "docs" / "CURRENT_HANDOFF.md",
        REPO_ROOT / "docs" / "RUNTIME_STATE.md",
        REPO_ROOT / "docs" / "SUBTITLE_STYLE_INTENT_REGISTRY.md",
        REPO_ROOT / "docs" / "SUBTITLE_PRESENTATION_CONTRACT.md",
    ]:
        text = path.read_text(encoding="utf-8")

        if path.name == "CURRENT_HANDOFF.md":
            assert f"active_artifact: {current_out09_artifact}" in text
            assert "local_artifact_available: true" in text
            assert "human_entrypoint: http://127.0.0.1:8072/index.html" in text
            assert "latest_out06_complete_narrative_short" not in text
            continue

        if path.name in {"CURRENT_HANDOFF.md", "RUNTIME_STATE.md"}:
            assert f"active_artifact: {current_out09_artifact}" in text
            assert (
                "historical_source_host_out06_artifact: "
                f"{current_out06_artifact}" in text
            )
            assert (
                "latest_out05_vertical_short_internal_candidate_artifact: "
                f"{accepted_out05_artifact}" in text
            )
            assert (
                "latest_out04_editorial_representative_sequence_artifact: "
                f"{current_out04_artifact}" in text
            )
            assert (
                "latest_out03_real_local_selected_cut_proof_artifact: "
                f"{current_out03_artifact}" in text
            )
            assert (
                "latest_out02_local_fixture_output_proof_artifact: "
                f"{baseline_out02_artifact}" in text
            )
            assert (
                "latest_int01_parallel_lane_aggregation_artifact: "
                f"{current_int_artifact}" in text
            )
            assert (
                f"latest_human_ok_fetch_prep_ready_artifact: {current_ews_artifact}"
                in text
            )
            assert (
                "latest_source_fetch_prep_planner_artifact: "
                f"{current_ews_fetch_prep_artifact}" in text
            )
            assert (
                "latest_source_identity_decision_intake_artifact: "
                f"{current_ews_decision_artifact}" in text
            )
            assert (
                f"latest_episode_workspace_inspector_artifact: {current_ews_inspector_artifact}"
                in text
            )
            assert (
                f"latest_episode_workspace_spine_artifact: {current_ews_spine_artifact}"
                in text
            )
            assert (
                f"latest_content_planning_operator_cockpit_artifact: {current_cpd_artifact}"
                in text
            )
        elif path.name != "SUBTITLE_PRESENTATION_CONTRACT.md":
            assert f"active_artifact: {active_artifact}" in text

        if path.name != "SUBTITLE_PRESENTATION_CONTRACT.md":
            assert (
                f"latest_thank_v2_open_command_repair_artifact: {active_artifact}"
                in text
            )
            assert (
                f"latest_thank_ed10ba_v2_access_recovery_artifact: {source_access_artifact}"
                in text
            )
            assert (
                f"latest_v2_cut_window_review_purpose_artifact: {source_v2_artifact}"
                in text
            )
            assert f"source_review_frame_plan: {source_review_frame_plan}" in text
            assert (
                f"source_micro_scene_observation_frame_readback: {source_frame_readback}"
                in text
            )
            assert (
                f"source_internal_review_observation_readback: {observation_artifact}"
                in text
            )
            assert active_artifact in text
            assert active_json in text
            assert active_md in text
            assert source_access_artifact in text
            assert source_access_json in text
            assert source_access_md in text
            assert source_v2_artifact in text
            assert source_v2_json in text
            assert source_v2_md in text
            assert active_launcher in text
            assert route_decision in text
            assert route_decision_json in text
            assert review_frame_surface in text
        assert source_review_frame_plan in text
        assert (
            source_plan_json in text or path.name == "SUBTITLE_PRESENTATION_CONTRACT.md"
        )
        assert (
            source_plan_md in text or path.name == "SUBTITLE_PRESENTATION_CONTRACT.md"
        )
        assert source_frame_readback in text
        assert source_specimen in text
        assert observation_artifact in text
        assert access_artifact in text
        assert source_artifact in text
        assert "open_representative_micro_scene_internal_review_specimen.ps1" in text
        assert "open_internal_review_video_candidate.ps1" in text
        assert "stage-6-user-freeform-review-request" not in text
        assert f"Active artifact: `{observation_artifact}`" not in text
        assert f"The active artifact is\n`{observation_artifact}`." not in text
        assert f"Active artifact: `{access_artifact}`" not in text
        assert f"The active artifact is\n`{access_artifact}`." not in text
        assert f"Active artifact: `{source_artifact}`" not in text
        assert f"The active artifact is\n`{source_artifact}`." not in text
        assert f"Active artifact: `{source_frame_readback}`" not in text
        assert f"The active artifact is\n`{source_frame_readback}`." not in text
        assert f"Active artifact: `{source_review_frame_plan}`" not in text
        assert f"The active artifact is\n`{source_review_frame_plan}`." not in text


def test_build_docs_dashboard_cli_writes_outputs(tmp_path: Path):
    _write_fixture_docs(tmp_path)
    output_dir = tmp_path / "docs" / "dashboard"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-docs-dashboard",
            "--output-dir",
            str(output_dir),
            "--generated-at",
            "cli-test",
            "--format",
            "json",
        ],
        cwd=str(tmp_path),
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "clippipegen.docs_dashboard.v1_5"
    assert payload["generated_at"] == "cli-test"
    assert payload["dashboard_json"].endswith("project-status.json")
    assert payload["dashboard_html"].endswith("index.html")
    assert payload["features_index"].endswith("features/index.md")
    assert payload["feature_count"] == 1
    assert payload["artifact_count"] == 1
    assert payload["finding_total"] >= payload["finding_count"]
    assert isinstance(payload["findings_truncated"], bool)
    assert (output_dir / "project-status.json").exists()
    assert (output_dir / "index.html").exists()
    assert (tmp_path / "docs" / "features" / "index.md").exists()


def test_open_current_proof_launcher_targets_focused_review_surface():
    launcher = (REPO_ROOT / "open-current-proof.ps1").read_text(encoding="utf-8")

    assert "subtitle_presentation_review_pack.html" in launcher
    assert "current_proof_focused_review.html" in launcher
    relative_target_line = next(
        line for line in launcher.splitlines() if line.startswith("$relativeTarget")
    )
    assert "subtitle_presentation_review_pack.html" in relative_target_line
    assert "current_proof_focused_review.html" not in relative_target_line
    assert "subtitle_overlay_visual_proof_report.html" not in relative_target_line


def test_subtitle_style_intent_registry_is_machine_readable():
    registry_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-style-intent-registry.json"
    )

    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    assert registry["artifact_id"] == "clip-ed10aa-subtitle-style-intent-registry-001"
    assert registry["active_normal_dialogue_lead"] == (
        "ed10w_badge_label_pressure_adjustment"
    )
    assert set(registry["axes"]) == {
        "speaker_id",
        "speaker_role",
        "emotion",
        "intensity",
        "utterance_role",
        "readability_priority",
    }
    assert registry["axes"]["emotion"]["values"] == [
        "neutral",
        "emphasis",
        "shout",
        "whisper",
        "ominous",
        "narration",
        "system_note",
    ]
    assert registry["body_text_color_policy"]["default"] == "stable"
    assert (
        registry["agent_rule"]["semantic_tags_to_presets_without_numeric_review"]
        is True
    )
    assert "new_color_palette" in registry["agent_rule"]["human_review_required_for"]
    assert "font_size" in registry["perceptual_impact"]["high"]
    assert "one_pixel_outline_delta" in registry["perceptual_impact"]["low"]
    assert registry["review_surface_layout_debt"]["not_a_new_review_request"] is True
    assert registry["boundaries"]["broad_renderer_style_system_built"] is False
    assert registry["boundaries"]["production_render_acceptance"] is False


def test_subtitle_preset_selector_readback_is_machine_readable():
    selector_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-preset-selector.json"
    )

    selector = json.loads(selector_path.read_text(encoding="utf-8"))
    examples = {item["example_id"]: item for item in selector["examples"]}

    assert selector["artifact_id"] == "clip-ed10ab-subtitle-preset-selector-001"
    assert selector["source_registry_artifact_id"] == (
        "clip-ed10aa-subtitle-style-intent-registry-001"
    )
    assert selector["source_render_path_artifact_id"] == (
        "clip-ed10z-tiny-render-path-nearer-probe-001"
    )
    assert selector["input_axes"] == [
        "speaker_id",
        "speaker_role",
        "emotion",
        "intensity",
        "utterance_role",
        "readability_priority",
    ]
    assert "badge_color_token" in selector["output_style_tokens"]
    assert selector["selector_contract"]["deterministic"] is True
    assert selector["selector_contract"]["body_text_color_default"] == (
        "stable_default_body_text"
    )
    assert selector["selector_contract"]["character_color_first_surfaces"] == [
        "badge_color_token",
        "accent_color_token",
    ]
    assert selector["selector_contract"]["same_candidate_comparison_reopened"] is False
    assert (
        examples["neutral_dialogue_intensity_0"]["style_tokens"][
            "body_text_color_changed"
        ]
        is False
    )
    assert examples["shout_intensity_2"]["style_tokens"]["font_size_scale"] == 1.16
    assert (
        examples["whisper_intensity_1"]["style_tokens"]["outline_shadow_strength"]
        == "soft_readable"
    )
    assert (
        examples["ominous_intensity_2"]["style_tokens"]["safe_area_line_break_behavior"]
        == "maximum_readability"
    )
    assert (
        examples["narration_intensity_0"]["style_tokens"]["font_family_role"]
        == "narration_current_family_role"
    )
    assert (
        examples["system_note_intensity_0"]["style_tokens"]["badge_color_token"]
        == "system_badge"
    )
    assert selector["render_gate"]["new_render_run"] is False
    assert selector["boundaries"]["new_render_created"] is False
    assert selector["boundaries"]["production_subtitle_design_acceptance"] is False


def test_subtitle_visual_selector_proof_is_machine_readable():
    proof_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-visual-selector-proof.json"
    )

    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    examples = {item["example_id"]: item for item in proof["examples"]}

    assert proof["artifact_id"] == "clip-ed10ac-visual-selector-proof-001"
    assert proof["source_selector_artifact_id"] == (
        "clip-ed10ab-subtitle-preset-selector-001"
    )
    assert proof["status"] == "visual_selector_proof_ready"
    assert proof["proof_kind"] == "tracked_static_html_json_readback"
    assert proof["existing_output_first"]["considered"] is True
    assert proof["existing_output_first"]["new_render_run"] is False
    assert proof["body_text_color_policy"]["stable_across_examples"] is True
    assert proof["body_text_color_policy"]["changed_in_any_example"] is False
    assert proof["body_text_color_policy"]["character_color_first_surfaces"] == [
        "badge_color_token",
        "accent_color_token",
    ]
    assert proof["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert examples["shout_intensity_2"]["visual_sample"]["font_size_percent"] == 116
    assert (
        examples["whisper_intensity_1"]["readback_tokens"]["backplate_box_token"]
        == "soft"
    )
    assert (
        examples["system_note_intensity_0"]["readback_tokens"]["body_text_color_token"]
        == "stable_default_body_text"
    )
    assert proof["review_policy"]["human_review_required"] is False
    assert proof["render_gate"]["new_render_run"] is False
    assert proof["boundaries"]["production_render_acceptance"] is False


def test_subtitle_style_family_palette_axis_proof_is_machine_readable():
    proof_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-style-family-palette-proof.json"
    )

    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    examples = {item["example_id"]: item for item in proof["examples"]}

    assert proof["artifact_id"] == "clip-ed10ad-style-family-palette-axis-proof-001"
    assert proof["source_visual_selector_artifact_id"] == (
        "clip-ed10ac-visual-selector-proof-001"
    )
    assert proof["status"] == "style_family_palette_axis_proof_ready"
    assert proof["proof_kind"] == "tracked_static_html_json_readback"
    assert proof["axis_contract"]["body_text_color_policy"] == (
        "stable_default_body_text"
    )
    assert proof["axis_contract"]["new_palette_created"] is False
    assert proof["axis_contract"]["new_style_family_created"] is False
    assert proof["axis_contract"]["character_color_first_surfaces"] == [
        "badge_color_token",
        "accent_color_token",
    ]
    assert proof["body_text_color_policy"]["stable_across_examples"] is True
    assert proof["body_text_color_policy"]["changed_in_any_example"] is False
    assert proof["existing_output_first"]["level"] == (
        "L0 No Render / Existing Output First"
    )
    assert proof["existing_output_first"]["new_render_run"] is False
    assert proof["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert examples["neutral_dialogue_intensity_0"]["family_group"] == (
        "dialogue_current_keifont_family"
    )
    assert examples["shout_intensity_2"]["palette_route"] == "high_energy_warm"
    assert examples["ominous_intensity_2"]["palette_route"] == "ominous_dark"
    assert examples["system_note_intensity_0"]["family_group"] == ("system_note_family")
    assert {
        example["palette_surfaces"]["body_text_color_token"]
        for example in proof["examples"]
    } == {"stable_default_body_text"}
    assert proof["review_policy"]["human_review_required"] is False
    assert proof["review_policy"]["user_side_work"] == "none"
    assert proof["render_gate"]["new_render_run"] is False
    assert proof["boundaries"]["production_render_acceptance"] is False


def test_subtitle_render_path_selector_contract_is_machine_readable():
    contract_path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "subtitle-render-path-selector-contract.json"
    )

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    entries = {
        item["semantic_preset_id"]: item for item in contract["contract_entries"]
    }

    assert contract["artifact_id"] == (
        "clip-ed10ae-render-path-selector-contract-probe-001"
    )
    assert contract["source_style_family_palette_artifact_id"] == (
        "clip-ed10ad-style-family-palette-axis-proof-001"
    )
    assert contract["status"] == "render_path_selector_contract_ready"
    assert contract["contract_kind"] == "static_selector_to_render_path_readback"
    assert contract["render_level"] == "L0 No Render"
    assert (
        "semantic_preset_id"
        in contract["render_adapter_input_contract"]["semantic_fields"]
    )
    assert (
        "palette_route"
        in contract["render_adapter_input_contract"]["style_axis_fields"]
    )
    assert (
        "body_text_color_token"
        in contract["render_adapter_input_contract"]["color_surface_fields"]
    )
    assert (
        "safe_area_line_break_behavior"
        in contract["render_adapter_input_contract"]["motion_line_break_fields"]
    )
    assert contract["examples_represented"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
        "ominous_intensity_2",
        "narration_intensity_0",
        "system_note_intensity_0",
    ]
    assert (
        entries["shout_intensity_2"]["render_adapter_input"]["style"]["family_id"]
        == "emphasis_energy_family"
    )
    assert (
        entries["ominous_intensity_2"]["render_adapter_input"]["style"]["palette_route"]
        == "ominous_dark"
    )
    assert {
        entry["render_adapter_input"]["color_surfaces"]["body_text_color_token"]
        for entry in contract["contract_entries"]
    } == {"stable_default_body_text"}
    assert {
        entry["contract_assertions"]["render_artifact_created"]
        for entry in contract["contract_entries"]
    } == {False}
    assert contract["later_l2_render_path_probe_trigger"]["status"] == (
        "not_triggered_in_this_slice"
    )
    assert (
        "HTML proof updates"
        in contract["later_l2_render_path_probe_trigger"]["not_triggered_by"]
    )
    assert contract["render_gate"]["new_render_run"] is False
    assert contract["readiness_separation"]["production_readiness"] == "not_accepted"
    assert contract["boundaries"]["production_render_acceptance"] is False


def test_subtitle_render_path_selector_probe_is_machine_readable():
    probe_path = (
        REPO_ROOT / "docs" / "style_intent" / "subtitle-render-path-selector-probe.json"
    )
    probe = json.loads(probe_path.read_text(encoding="utf-8"))

    assert probe["artifact_id"] == "clip-ed10af-l2-render-path-selector-probe-001"
    assert probe["source_render_path_selector_contract_artifact_id"] == (
        "clip-ed10ae-render-path-selector-contract-probe-001"
    )
    assert probe["status"] == "l2_render_path_selector_probe_ready"
    assert probe["probe_kind"] == "tiny_ffmpeg_libass_selector_probe_readback"
    assert probe["render_level"] == "L2 tiny render path selector probe"
    assert probe["selected_example_ids"] == [
        "neutral_dialogue_intensity_0",
        "shout_intensity_2",
        "whisper_intensity_1",
    ]
    assert probe["selected_example_count"] == 3
    assert probe["validation"]["source_contract_referenced"] is True
    assert probe["validation"]["stable_body_text_preserved"] is True
    assert probe["validation"]["badge_accent_backplate_route_preserved"] is True
    assert probe["validation"]["safe_area_line_break_metadata_survived"] is True
    assert probe["validation"]["production_public_boundary_closed"] is True
    assert probe["validation"]["tracked_binary_artifact_created"] is False
    assert probe["validation"]["all_checks_passed"] is True
    assert {
        example["color_surfaces"]["body_text_color_token"]
        for example in probe["examples"]
    } == {"stable_default_body_text"}
    assert all(
        example["assertions"]["badge_accent_backplate_preserved"]
        for example in probe["examples"]
    )
    assert any(
        example["line_break"]["ass_text_contains_line_break"]
        for example in probe["examples"]
    )
    assert probe["local_probe"]["status"] == "local_ignored_probe_generated"
    assert (
        "subtitle_render_path_selector_probe.ass"
        in probe["local_probe"]["outputs"]["ass"]
    )
    assert (
        "subtitle_render_path_selector_probe.mp4"
        in probe["local_probe"]["outputs"]["video"]
    )
    assert probe["render_gate"]["new_render_run"] is True
    assert probe["render_gate"]["tracked_binary_artifact_created"] is False
    assert probe["boundaries"]["production_render_acceptance"] is False
    assert probe["boundaries"]["rights_status"] == "pending"
    assert probe["boundaries"]["public_use_permission"] is False
    assert probe["boundaries"]["tracked_binary_artifact_created"] is False
    assert probe["boundaries"]["episodes_tracked"] is False


def test_subtitle_font_candidate_registry_is_machine_readable():
    registry_path = (
        REPO_ROOT / "docs" / "font_candidates" / "subtitle-font-candidates.json"
    )

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    candidate_ids = {candidate["candidate_id"] for candidate in registry["candidates"]}

    assert registry["artifact_id"] == "clip-subtitle-font-candidate-sweep-001"
    assert registry["current_selected_diagnostic_overlay_proof_base"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert registry["font_size_policy"]["formula"] == "round(frame_height * 0.115)"
    assert registry["boundary_flags"]["font_binaries_downloaded"] is False
    assert registry["boundary_flags"]["production_candidate"] is False
    assert registry["ed10i_narrow_slice"]["artifact_id"] == (
        "clip-ed10i-kirinuki-gothic-balance-001"
    )
    assert registry["ed10i_narrow_slice"]["recommended_default_candidate_id"] == (
        "ed10i_biz_udgothic_bold_balanced_outline"
    )
    assert registry["ed10i_narrow_slice"]["selected_candidate_id"] == (
        "ed10i_meiryo_bold_fill_outline_balance"
    )
    assert registry["ed10i_narrow_slice"]["selected_overlay_artifact_id"] == (
        "clip-ed10i-meiryo-overlay-proof-001"
    )
    assert registry["ed10i_narrow_slice"]["selected_overlay_review_status"] == (
        "reviewed_not_accepted_as_normal_baseline"
    )
    assert registry["ed10j_research_audit_slice"]["artifact_id"] == (
        "clip-ed10j-kirinuki-font-audit-001"
    )
    assert registry["ed10j_research_audit_slice"][
        "recommended_default_candidate_id"
    ] == ("ed10j_biz_udgothic_bold_telop_candidate")
    assert registry["ed10j_research_audit_slice"]["selected_candidate_id"] == (
        "ed10j_biz_udgothic_bold_telop_candidate"
    )
    assert registry["ed10j_research_audit_slice"]["selected_overlay_artifact_id"] == (
        "clip-ed10k-biz-overlay-proof-001"
    )
    assert (
        registry["ed10j_research_audit_slice"]["badge_color_readback"][
            "blue_badge_candidate_id"
        ]
        == "ed10j_noto_sans_jp_local_telop_candidate"
    )
    assert (
        registry["ed10j_research_audit_slice"]["badge_color_readback"][
            "blue_badge_is_meiryo_reference"
        ]
        is False
    )
    assert registry["ed10k_overlay_proof_slice"]["review_status"] == (
        "reviewed_not_accepted_as_normal_baseline"
    )
    assert registry["ed10l_known_font_pack_slice"]["artifact_id"] == (
        "clip-ed10l-known-kirinuki-font-pack-001"
    )
    assert registry["ed10l_known_font_pack_slice"][
        "recommended_default_candidate_id"
    ] == ("ed10l_keifont_pop_dialogue_candidate")
    assert (
        registry["ed10l_known_font_pack_slice"][
            "selected_source_license_install_route_candidate_id"
        ]
        == "ed10l_keifont_pop_dialogue_candidate"
    )
    assert (
        registry["ed10m_real_font_source_license_install_route"][
            "selected_candidate_id"
        ]
        == "ed10l_keifont_pop_dialogue_candidate"
    )
    assert (
        registry["ed10m_real_font_source_license_install_route"][
            "font_binaries_downloaded"
        ]
        is False
    )
    assert registry["ed10l_known_font_pack_slice"]["selected_candidate_id"] == (
        "ed10l_keifont_pop_dialogue_candidate"
    )
    assert registry["ed10l_known_font_pack_slice"]["review_status"] == (
        "per_user_font_readback_valid_keifont_proof_generated"
    )
    assert (
        registry["ed10l_known_font_pack_slice"][
            "candidate_selection_from_current_pngs_allowed"
        ]
        is True
    )
    assert registry["ed10l_known_font_pack_slice"][
        "current_visual_comparison_validity"
    ] == ("valid_requested_font_visual_evidence_after_per_user_font_readback")
    assert (
        registry["ed10l_known_font_pack_slice"]["self_diagnosis"][
            "candidate_universe_bias"
        ]
        == "system_safe_generic_readability"
    )
    assert registry["ed10l_known_font_pack_slice"]["local_font_readback"][
        "target_fonts_found"
    ] == ["Keifont", "851 Chikara Yowaku", "M+ FONTS", "Yasashisa Gothic"]
    assert (
        registry["ed10m_real_font_source_license_install_route"][
            "local_font_file_found"
        ]
        is True
    )
    assert (
        registry["ed10n_per_user_font_readback_and_real_proof"][
            "selected_overlay_candidate_id"
        ]
        == "ed10l_keifont_pop_dialogue_candidate"
    )
    assert (
        registry["ed10n_per_user_font_readback_and_real_proof"][
            "font_binaries_copied_or_vendored"
        ]
        is False
    )
    assert registry["ed10o_multifont_focused_review"]["artifact_id"] == (
        "clip-ed10o-multifont-focused-review-001"
    )
    assert registry["ed10o_multifont_focused_review"]["review_surface_status"] == (
        "focused_review_surface_accepted_as_review_direction"
    )
    assert (
        registry["ed10o_multifont_focused_review"]["human_review_consumed"][
            "focused_review_surface_easier_to_understand"
        ]
        is True
    )
    assert (
        registry["ed10o_multifont_focused_review"]["human_review_consumed"][
            "final_baseline_acceptance"
        ]
        is False
    )
    assert (
        registry["ed10o_multifont_focused_review"]["source_proof_artifact_id"]
        == "clip-ed10n-keifont-overlay-proof-001"
    )
    assert registry["ed10o_multifont_focused_review"]["primary_visual"] == (
        "subtitle_area_crop_matrix"
    )
    assert (
        registry["ed10o_multifont_focused_review"]["current_lead_candidate_id"]
        == "ed10l_keifont_pop_dialogue_candidate"
    )
    assert registry["ed10o_multifont_focused_review"]["included_candidate_ids"] == [
        "ed10l_keifont_pop_dialogue_candidate",
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    ]
    assert registry["ed10o_multifont_focused_review"]["excluded_candidates"] == [
        {
            "candidate_id": "ed10l_m_plus_fonts_dialogue_candidate",
            "reason": "weight_style_unresolved",
            "readback": "M PLUS 1 Thin via MPLUS1-VariableFont_wght.ttf",
            "next_action": (
                "pin an exact non-thin M+ weight/style before including it "
                "in baseline comparison"
            ),
        }
    ]
    assert (
        registry["ed10o_multifont_focused_review"][
            "production_subtitle_design_acceptance"
        ]
        is False
    )
    assert (
        registry["ed10o_multifont_focused_review"]["font_binaries_copied_or_vendored"]
        is False
    )
    assert registry["ed10p_keifont_lead_representative_proof"]["artifact_id"] == (
        "clip-ed10p-keifont-lead-representative-proof-001"
    )
    assert (
        registry["ed10p_keifont_lead_representative_proof"]["source_review_artifact_id"]
        == "clip-ed10o-multifont-focused-review-001"
    )
    assert registry["ed10p_keifont_lead_representative_proof"]["proof_profile"] == (
        "ed10p_keifont_lead_representative_proof"
    )
    assert registry["ed10p_keifont_lead_representative_proof"][
        "current_review_page"
    ].endswith("current_proof_focused_review.html")
    assert registry["ed10p_keifont_lead_representative_proof"][
        "detailed_overlay_report"
    ].endswith("subtitle_overlay_visual_proof_report.html")
    assert (
        registry["ed10p_keifont_lead_representative_proof"]["current_lead_candidate_id"]
        == "ed10l_keifont_pop_dialogue_candidate"
    )
    assert registry["ed10p_keifont_lead_representative_proof"]["lead_status"] == (
        "diagnostic_representative_normal_dialogue_provisional_baseline"
    )
    assert (
        registry["ed10p_keifont_lead_representative_proof"]["review_surface_direction"]
        == "ed10o_focused_matrix_accepted_as_preferred_review_direction"
    )
    assert registry["ed10p_keifont_lead_representative_proof"][
        "included_candidate_ids"
    ] == ["ed10l_keifont_pop_dialogue_candidate"]
    assert registry["ed10p_keifont_lead_representative_proof"][
        "alternates_preserved"
    ] == [
        "ed10l_851_chikara_yowaku_dialogue_candidate",
        "ed10l_yasashisa_gothic_goodfreefonts_candidate",
    ]
    assert (
        registry["ed10p_keifont_lead_representative_proof"]["review_debt"][0]["debt_id"]
        == "cut_008_dense_stress_proof"
    )
    assert (
        registry["ed10p_keifont_lead_representative_proof"]["review_debt"][0]["status"]
        == "superseded_by_ed10r_current_target"
    )
    assert (
        registry["ed10p_keifont_lead_representative_proof"][
            "keifont_general_acceptance_reopened"
        ]
        is False
    )
    assert (
        registry["ed10p_keifont_lead_representative_proof"][
            "production_subtitle_design_acceptance"
        ]
        is False
    )
    assert (
        registry["ed10p_keifont_lead_representative_proof"][
            "font_binaries_copied_or_vendored"
        ]
        is False
    )
    assert registry["ed10q_current_proof_focused_review_fix"]["feature_id"] == (
        "ED-10q"
    )
    assert registry["ed10q_current_proof_focused_review_fix"]["artifact_id"] == (
        "clip-ed10p-keifont-lead-representative-proof-001"
    )
    assert registry["ed10q_current_proof_focused_review_fix"][
        "launcher_target"
    ].endswith("current_proof_focused_review.html")
    assert (
        registry["ed10q_current_proof_focused_review_fix"]["debug_tables_primary"]
        is False
    )
    assert (
        registry["ed10q_current_proof_focused_review_fix"]["first_view_order"][0]
        == "Review Focus: Current Proof"
    )
    assert (
        registry["ed10q_current_proof_focused_review_fix"][
            "production_subtitle_design_acceptance"
        ]
        is False
    )
    assert registry["ed10r_keifont_dense_stress_proof"]["feature_id"] == "ED-10v"
    assert registry["ed10r_keifont_dense_stress_proof"]["artifact_id"] == (
        "clip-ed10r-keifont-dense-stress-proof-001"
    )
    assert registry["ed10r_keifont_dense_stress_proof"]["proof_profile"] == (
        "ed10r_keifont_dense_stress_proof"
    )
    assert registry["ed10r_keifont_dense_stress_proof"]["target_cut_ids"] == ["cut_008"]
    assert registry["ed10r_keifont_dense_stress_proof"]["baseline_scope"] == (
        "diagnostic_representative_normal_dialogue_provisional"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"][
            "keifont_general_acceptance_reopened"
        ]
        is False
    )
    assert registry["ed10r_keifont_dense_stress_proof"]["user_action_type"] == (
        "NO_REVIEW_CARD_CURRENT_AXIS_PASSED"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["next_review_action_type"]
        == "NEW_AXIS_ONLY"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
            "prior_review_count"
        ]
        == "3+"
    )
    assert (
        "linebreak_policy_readback"
        in registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
            "next_nonredundant_axis"
        ]
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
            "repeated_general_review"
        ]
        is False
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_memory"]["current_blocker"]
        == "none_for_diagnostic_dense_stress"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_memory"][
            "font_evidence_gate"
        ]
        == "valid_requested_keifont_visual_evidence"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_debt"][0]["status"]
        == "closed_diagnostic_pass"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"][
            "current_workspace_font_visual_evidence"
        ]["status"]
        == "valid_requested_keifont_visual_evidence"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["multiline_wrap_evidence"][
            "status"
        ]
        == "passed_diagnostic_review"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["multiline_wrap_evidence"][
            "subtitle_id"
        ]
        == "sub_096"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["multiline_wrap_evidence"][
            "default_display_max_width_px"
        ]
        == 220
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["line_break_policy_readback"][
            "status"
        ]
        == "diagnostic_policy_recorded"
    )
    assert (
        "NLMYTGen"
        in registry["ed10r_keifont_dense_stress_proof"]["line_break_policy_readback"][
            "nlmytgen_portability_note"
        ]
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_card"]["action_type"]
        == "NO_REVIEW_CARD_CURRENT_AXIS_PASSED"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_card"]["status"]
        == "withheld_no_redundant_review_after_pass"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["review_card"]["axis"]
        == "dense_stress"
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"][
            "production_subtitle_design_acceptance"
        ]
        is False
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["production_render_acceptance"]
        is False
    )
    assert (
        registry["ed10r_keifont_dense_stress_proof"]["font_binaries_copied_or_vendored"]
        is False
    )
    assert registry["ed10w_subtitle_presentation_review_pack"]["feature_id"] == (
        "ED-10w"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"]["artifact_id"] == (
        "clip-ed10w-subtitle-presentation-review-pack-001"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"]["proof_profile"] == (
        "ed10w_subtitle_presentation_review_pack"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "current_review_page"
    ].endswith("subtitle_presentation_review_pack.html")
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "bounded_decoration_candidates"
    ] == [
        "ed10w_current_pass_reference",
        "ed10w_lighter_outline_shadow_pressure",
        "ed10w_badge_label_pressure_adjustment",
        "ed10w_balanced_combined_low_risk",
    ]
    assert (
        registry["ed10w_subtitle_presentation_review_pack"]["render_path_readiness"][
            "status"
        ]
        == "decision_card_included_no_production_claim"
    )
    assert (
        registry["ed10w_subtitle_presentation_review_pack"][
            "candidate_delta_visibility"
        ]["status"]
        == "reviewable_after_ed10x_fix"
    )
    assert registry["ed10w_subtitle_presentation_review_pack"][
        "candidate_delta_visibility"
    ]["candidate_3_expected_delta"] == (
        "combined_outline_shadow_and_badge_pressure_reduction"
    )
    assert (
        registry["ed10w_subtitle_presentation_review_pack"]["review_card"]["status"]
        == "emitted_nonredundant_new_axis"
    )
    assert (
        registry["ed10w_subtitle_presentation_review_pack"][
            "keifont_general_acceptance_reopened"
        ]
        is False
    )
    assert (
        registry["ed10w_subtitle_presentation_review_pack"][
            "production_subtitle_design_acceptance"
        ]
        is False
    )
    assert (
        registry["ed10w_subtitle_presentation_review_pack"][
            "production_render_acceptance"
        ]
        is False
    )
    assert (
        registry["ed10w_subtitle_presentation_review_pack"][
            "font_binaries_copied_or_vendored"
        ]
        is False
    )
    assert registry["ed10y_candidate2_carry_forward"]["feature_id"] == "ED-10y"
    assert registry["ed10y_candidate2_carry_forward"]["artifact_id"] == (
        "clip-ed10y-candidate2-carry-forward-001"
    )
    assert registry["ed10y_candidate2_carry_forward"]["proof_profile"] == (
        "ed10y_candidate2_carry_forward"
    )
    assert registry["ed10y_candidate2_carry_forward"]["current_lead_candidate_id"] == (
        "ed10w_badge_label_pressure_adjustment"
    )
    assert (
        registry["ed10y_candidate2_carry_forward"]["fallback_reference_candidate_id"]
        == "ed10w_current_pass_reference"
    )
    assert registry["ed10y_candidate2_carry_forward"][
        "held_reference_candidate_ids"
    ] == [
        "ed10w_lighter_outline_shadow_pressure",
        "ed10w_balanced_combined_low_risk",
    ]
    assert (
        registry["ed10y_candidate2_carry_forward"]["review_memory"][
            "latest_freeform_review_consumed"
        ]
        is True
    )
    assert (
        registry["ed10y_candidate2_carry_forward"]["review_memory"][
            "same_candidate_comparison_review_allowed"
        ]
        is False
    )
    assert (
        registry["ed10y_candidate2_carry_forward"]["render_path_readiness"]["status"]
        == "candidate2_tiny_render_path_nearer_diagnostic_probe_completed"
    )
    assert (
        registry["ed10y_candidate2_carry_forward"]["review_card"]["action_type"]
        == "NO_REVIEW_CARD_REVIEW_CONSUMED"
    )
    assert (
        registry["ed10y_candidate2_carry_forward"][
            "production_subtitle_design_acceptance"
        ]
        is False
    )
    assert (
        registry["ed10y_candidate2_carry_forward"]["font_binaries_copied_or_vendored"]
        is False
    )
    assert registry["ed10z_tiny_render_path_nearer_probe"]["feature_id"] == "ED-10z"
    assert registry["ed10z_tiny_render_path_nearer_probe"]["artifact_id"] == (
        "clip-ed10z-tiny-render-path-nearer-probe-001"
    )
    assert registry["ed10z_tiny_render_path_nearer_probe"]["proof_profile"] == (
        "ed10z_tiny_render_path_nearer_probe"
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"]["source_previous_artifact_id"]
        == "clip-ed10y-candidate2-carry-forward-001"
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"]["current_lead_candidate_id"]
        == "ed10w_badge_label_pressure_adjustment"
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"][
            "fallback_reference_candidate_id"
        ]
        == "ed10w_current_pass_reference"
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"]["render_path_readiness"][
            "status"
        ]
        == "ed10z_tiny_render_path_nearer_probe_completed"
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"][
            "actual_materialization_status"
        ]["status"]
        == "blocked_environment_missing_ffprobe"
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"]["review_card"]["action_type"]
        == "NO_REVIEW_CARD_REVIEW_CONSUMED"
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"]["production_render_acceptance"]
        is False
    )
    assert (
        registry["ed10z_tiny_render_path_nearer_probe"][
            "font_binaries_copied_or_vendored"
        ]
        is False
    )
    assert "noto_sans_jp_clean_outline" in candidate_ids
    assert "ed10i_reference_noto_clean_outline" in candidate_ids
    assert "ed10i_biz_udgothic_bold_balanced_outline" in candidate_ids
    assert "ed10i_yu_gothic_bold_thin_outline" in candidate_ids
    assert "ed10i_meiryo_bold_fill_outline_balance" in candidate_ids
    assert "ed10j_reference_meiryo_reviewed_not_baseline" in candidate_ids
    assert "ed10j_biz_udgothic_bold_telop_candidate" in candidate_ids
    assert "ed10j_yu_gothic_bold_system_candidate" in candidate_ids
    assert "ed10j_noto_sans_jp_local_telop_candidate" in candidate_ids
    assert "ed10l_keifont_pop_dialogue_candidate" in candidate_ids
    assert "ed10l_851_chikara_yowaku_dialogue_candidate" in candidate_ids
    assert "ed10l_m_plus_fonts_dialogue_candidate" in candidate_ids
    assert "ed10l_yasashisa_gothic_goodfreefonts_candidate" in candidate_ids
    assert "ed10l_851_chikara_zuyoku_emphasis_candidate" in candidate_ids
    assert "ed10l_source_han_serif_mood_candidate" in candidate_ids
    assert "ed10l_shippori_mincho_mood_candidate" in candidate_ids
    assert "m_plus_1p_bold" in candidate_ids
    assert "dela_gothic_one_emphasis" in candidate_ids
    assert "noto_serif_jp_narration_local" in candidate_ids


def test_subtitle_presentation_contract_records_ed10v_linebreak_policy():
    text = (REPO_ROOT / "docs" / "SUBTITLE_PRESENTATION_CONTRACT.md").read_text(
        encoding="utf-8"
    )

    assert "ED-10v records the current line-break behavior" in text
    assert "Current Cut_008 Dense/Stress Diagnostic Pass" in text
    assert "Current ED-10w Presentation Review Pack" in text
    assert "Current ED-10y Candidate 2 Carry-Forward" in text
    assert "Current ED-10z Tiny Render-Path-Nearer Probe" in text
    assert "Current ED-10ag Lineage and Observation Surface" in text
    assert "Current ED-10ah Production Limitation-Lift Entry" in text
    assert "Current ED-10ai Final Render-Path Readiness Packet" in text
    assert "Current ED-10aj Final Render-Path Stage 1" in text
    assert "Current ED-10ak Final Render-Path Stage 2 Replayability" in text
    assert "Current ED-10am Production Limitation-Lift Stage 1" in text
    assert "Current ED-10an Production Limitation-Lift Stage 2 Decision Packet" in text
    assert (
        "Current ED-10ao Production Limitation-Lift Stage 3 Owner-Review Prep" in text
    )
    assert "Current ED-10as Internal Review Access Sheet Fullpath" in text
    assert "Current ED-10at Internal Review Observation Readback" in text
    assert "Current ED-10av Micro-Scene Observation Frame Readback" in text
    assert "Source ED-10au Representative Micro-Scene Internal Review Specimen" in text
    assert "clip-ed10z-tiny-render-path-nearer-probe-001" in text
    assert "clip-ed10w-subtitle-presentation-review-pack-001" in text
    assert "clip-ed10af-render-contract-consumer-dry-read-001" in text
    assert "clip-ed10af-l2-render-path-selector-probe-001" in text
    assert "clip-ed10ag-lineage-and-observation-surface-001" in text
    assert "clip-ed10ah-production-limitation-lift-entry-001" in text
    assert "clip-ed10ai-final-render-path-readiness-packet-001" in text
    assert "clip-ed10aj-final-render-path-stage-1-001" in text
    assert "clip-ed10ak-final-render-path-stage-2-replayability-001" in text
    assert "clip-ed10al-final-render-path-stage-3-rehearsal-001" in text
    assert "clip-ed10am-production-limitation-lift-stage-1-001" in text
    assert "clip-ed10an-production-limitation-lift-stage-2-decision-packet-001" in text
    assert (
        "clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001" in text
    )
    assert "clip-ed10as-internal-review-access-sheet-fullpath-001" in text
    assert "clip-ed10ar-internal-review-video-candidate-package-001" in text
    assert "clip-ed10at-internal-review-observation-readback-001" in text
    assert "clip-ed10au-representative-micro-scene-internal-review-specimen-001" in text
    assert "clip-ed10av-micro-scene-observation-frame-readback-001" in text
    assert (
        "clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001"
        in text
    )
    assert "internal-review-video-observation-readback.json" in text
    assert "internal-review-video-observation-readback.md" in text
    assert (
        "grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.json"
        in text
    )
    assert (
        "grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md"
        in text
    )
    assert "micro-scene-observation-frame-readback.json" in text
    assert "micro-scene-observation-frame-readback.md" in text
    assert "representative-micro-scene-internal-review-specimen.json" in text
    assert "representative-micro-scene-internal-review-specimen.md" in text
    assert "open_representative_micro_scene_internal_review_specimen.ps1" in text
    assert (
        "clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001" in text
    )
    assert "final-render-path-stage-1" in text
    assert "final-render-path-stage-2" in text
    assert "final-render-path-stage-3" in text
    assert "final-render-path-stage-4" in text
    assert "production-limitation-lift-stage-1" in text
    assert "production-limitation-lift-stage-2-decision-packet" in text
    assert "production-limitation-lift-stage-3-owner-review-prep" in text
    assert "production-limitation-lift-stage-4-user-decision-card" in text
    assert "ed10w_badge_label_pressure_adjustment" in text
    assert "ed10w_balanced_combined_low_risk" in text
    assert "diagnostic dense/stress behavior" in text
    assert "`sub_096` multiline/wrap evidence" in text
    assert "Future Shared Line-Break Policy Note" in text
    compact_text = " ".join(text.split())
    assert "do not read, edit, or depend on NLMYTGen files" in compact_text


def _write_fixture_docs(base: Path) -> None:
    (base / "docs").mkdir(parents=True)
    (base / "artifacts").mkdir()
    (base / "README.md").write_text(
        "# Fixture\n\n## What This Is\nA fixture.\n\n## Current State\nReady.\n\n"
        "## Next\nContinue.\n\n## Constraints / Risks\nNone.\n",
        encoding="utf-8",
    )
    (base / "docs" / "index.md").write_text(
        "# Docs Index\n\n## What This Is\nA front door.\n\n## Current State\nReady.\n\n"
        "## Next\nUse dashboard.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    _write_runtime_state(base)
    (base / "docs" / "FEATURE_REGISTRY.md").write_text(
        "# Feature Registry\n\n| ID | Name | Status | Summary |\n"
        "|---|---|---|---|\n| ED-01 | Editing | done | ok |\n",
        encoding="utf-8",
    )
    boundary_sentence = (
        "production rights publishing public use acceptance "
        "隰・ｽｿ髫ｱ繝ｻ隶難ｽｩ陋ｻ・ｩ 陷茨ｽｬ鬮｢繝ｻ"
    )
    (base / "docs" / "EPISODE_REVIEW_WORKFLOW.md").write_text(
        "# Episode Review Workflow\n\n" + boundary_sentence * 4,
        encoding="utf-8",
    )
    (base / "docs" / "OPERATOR_REVIEW_UX.md").write_text(
        "# Operator Review UX\n\n## What This Is\nUX.\n\n## Current State\nReady.\n\n"
        "## Next\nUse it.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    (base / "docs" / "SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md").write_text(
        "# Subtitle Typography\n\n## What This Is\nCompare.\n\n## Current State\nReady.\n\n"
        "## Next\nReview.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    (base / "docs" / "REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md").write_text(
        "# Representative Review\n\n## What This Is\nReview.\n\n## Current State\nReady.\n\n"
        "## Next\nReview.\n\n## Constraints / Risks\nDiagnostic only.\n",
        encoding="utf-8",
    )
    (base / "artifacts" / "ARTIFACTS.md").write_text(
        "# Artifact Registry\n\n## `clip-test-artifact`\n",
        encoding="utf-8",
    )


def _write_runtime_state(base: Path, **overrides: str) -> None:
    metadata = {
        "id": "runtime-state",
        "title": "Runtime State - Fixture",
        "type": "resume_surface",
        "status": "current_capsule",
        "health": "fixture_ready",
        "last_touched": "2026-07-10",
        "current_slice": "FIX-01",
        "phase": "review_ready",
        "canonical_main_head": "fixture-main-head",
        "canonical_main_baseline": "Fixture accepted baseline",
        "canonical_status": "fixture_branch_review_pending",
        "review_status": "fixture_review_ready",
        "active_branch": "codex/fixture-current-state",
        "current_title": "Fixture Current Focus",
        "human_entrypoint": "docs/fixture_focus.html",
        "review_open_command": "start docs\\fixture_focus.html",
        "review_server_restart_command": "fixture-restart",
        "machine_readback": "docs/fixture_focus.json",
        "remote_code_complete": "true",
        "local_artifact_available": "true",
        "cross_machine_resume_class": "reacquirable",
        "active_rebuild_contract": "artifacts/ACTIVE_REBUILD.json",
        "evidence_revision": "fixture-r1",
        "accepted_baseline_sha256": "a" * 64,
        "recommended_cover_path": "docs/fixture_cover.png",
        "recommended_cover_sha256": "b" * 64,
        "recommended_cover_timestamp_seconds": "11.930",
        "recommended_cover_selection_status": "recommended_pending_human_acceptance",
        "last_verified_host": "fixture-host",
        "local_artifact_evidence_receipt": "docs/fixture_manifest.json",
        "current_handoff": "docs/CURRENT_HANDOFF.md",
        "decision_required": "fixture_decision",
        "last_verified_at": "2026-07-10",
        "next_review_due": "review_fixture_focus",
        "active_artifact": "clip-test-artifact",
        "next_action": "Review the fixture current focus.",
        "source_of_truth": "true",
    }
    metadata.update(overrides)
    front_matter = "\n".join(f"{key}: {value}" for key, value in metadata.items())
    (base / "docs" / "RUNTIME_STATE.md").write_text(
        "\ufeff---\n"
        + front_matter
        + "\n---\n\n# Runtime State\n\n"
        + "This page lacks the v1.5 front sections.\n",
        encoding="utf-8",
    )


def test_docs_dashboard_current_focus_registration_uses_runtime_artifact(
    tmp_path: Path,
):
    _write_fixture_docs(tmp_path)
    _write_runtime_state(tmp_path, active_artifact="clip-runtime-current-artifact")
    (tmp_path / "artifacts" / "ARTIFACTS.md").write_text(
        "# Artifact Registry\n\n## `clip-ed10r-keifont-dense-stress-proof-001`\n",
        encoding="utf-8",
    )

    status = build_project_status(base_dir=tmp_path, generated_at="test-run")

    assert status["current_focus"]["artifact_id"] == "clip-runtime-current-artifact"
    assert status["artifact_coverage"]["current_focus_artifact_registered"] is False


def test_artifact_registry_records_content_planning_and_ed10ah_sources():
    status = build_project_status(base_dir=REPO_ROOT, generated_at="test-run")
    artifact_ids = set(status["artifact_summary"]["artifact_ids"])

    assert status["current_focus"]["canonical_main_head"] == (
        "resolve_origin_main_at_resume"
    )
    assert status["current_focus"]["canonical_main_baseline"] == (
        "OUT-08 accepted internal closure from source tip "
        "2d45bd8d9ff5cb5f2efcdeeaa839b4ef000e96a2"
    )
    assert status["current_focus"]["canonical_status"] == (
        "out09_bounded_repair_review_ready"
    )
    assert status["current_focus"]["review_status"] == (
        "OUT09_SUBTITLE_AUTHORITY_AND_ENDPOINT_REPAIRED_REVIEW_READY"
    )
    assert status["current_focus"]["decision_required"] == (
        "one_bounded_out09_repair_question"
    )
    assert status["current_focus"]["next_review_action_type"] == (
        "OUT09_ONE_BOUNDED_REPAIR_QUESTION"
    )
    assert status["current_focus"]["human_entrypoint"] == (
        "http://127.0.0.1:8072/index.html"
    )
    assert status["current_focus"]["review_open_command"] == (
        "powershell -ExecutionPolicy Bypass -File "
        "episodes\\holoen01_kronii_wisdomteeth_out09_20260718\\review\\"
        "out09_second_source_short_repeatability\\open_preview.ps1 -Port 8072"
    )
    assert status["current_focus"]["machine_readback"] == (
        "episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/"
        "out09_second_source_short_repeatability/candidate_readback.json"
    )
    assert status["current_focus"]["remote_code_complete"] == "true"
    assert status["current_focus"]["local_artifact_available"] == "true"
    assert status["current_focus"]["portable_local_artifact_available"] == "false"
    assert status["current_focus"]["portable_entrypoint"] == ""
    assert status["current_focus"]["exact_baseline_available"] == ""
    assert status["current_focus"]["accepted_baseline_status"] == ""
    assert status["current_focus"]["cover_direction_review_available"] == ""
    assert status["current_focus"]["cover_direction_acceptance"] == ""
    assert status["current_focus"]["proxy_classification"] == ""
    assert status["current_focus"]["source_byte_equivalence_claimed"] == ""
    assert status["current_focus"]["review_server_status"] == (
        "running_localhost_8072_at_last_verification"
    )
    assert (
        status["current_focus"]["last_verified_host_local_artifact_available"] == "true"
    )
    assert status["current_focus"]["last_verified_host_entrypoint"] == (
        "http://127.0.0.1:8072/index.html"
    )
    assert status["current_focus"]["local_verified_host"] == "DESKTOP-H53P1T4"
    assert status["current_focus"]["pause_reason"] == ""
    assert status["current_focus"]["accepted_baseline_recovery_status"] == ""
    assert status["current_focus"]["cover_review_status"] == ""
    current_surfaces = [
        item
        for item in status["open_surfaces"]
        if item["label"] == "OUT-08 Current Focus"
    ]
    assert current_surfaces == []
    assert status["current_focus"]["cross_machine_resume_class"] == (
        "tracked_builder_docs_portable_ignored_review_payload_same_machine_only"
    )
    assert status["current_focus"]["active_rebuild_contract"] == ""
    assert status["current_focus"]["accepted_baseline_sha256"] == ""
    assert status["current_focus"]["recommended_cover_path"] == ""
    assert status["current_focus"]["recommended_cover_sha256"] == ""
    assert status["current_focus"]["recommended_cover_timestamp_seconds"] == ""
    assert status["current_focus"]["recommended_cover_selection_status"] == ""
    assert status["current_focus"]["artifact_id"] == (
        "clip-out09-second-source-short-repeatability-v0-001"
    )
    assert "clip-out09-second-source-short-repeatability-v0-001" in artifact_ids
    assert "clip-out08-real-unused-range-short-minibatch-v0-001" in artifact_ids
    assert "clip-out07-shorts-poster-frame-direction-proof-v0-001" in artifact_ids
    assert "clip-out07-internal-operator-delivery-pack-v0-001" in artifact_ids
    assert (
        "clip-out06-complete-narrative-short-delivery-candidate-v0-001" in artifact_ids
    )
    assert "clip-out05-vertical-short-internal-candidate-v0-001" in artifact_ids
    assert "clip-out04-editorial-representative-sequence-v0-001" in artifact_ids
    assert "clip-out03-real-local-selected-cut-proof-v0-001" in artifact_ids
    assert "clip-cpd12-minimal-review-console-v0-001" in artifact_ids
    assert "clip-cpd11-operator-view-shell-v0-001" in artifact_ids
    assert "clip-cpd10-candidate-ledger-readability-v0-001" in artifact_ids
    assert "clip-cpd09-operator-briefing-board-v0-001" in artifact_ids
    assert "clip-cpd01-content-candidate-dashboard-v0-001" in artifact_ids
    assert "clip-cpd02-candidate-to-episode-seed-bridge-v0-001" in artifact_ids
    assert "clip-cpd03-source-metadata-resolver-v0-001" in artifact_ids
    assert "clip-cpd04-init-episode-dry-run-plan-v0-001" in artifact_ids
    assert "clip-cpd05-source-inspection-packet-v0-001" in artifact_ids
    assert "clip-ed10af-l2-render-path-selector-probe-001" in artifact_ids
    assert "clip-ed10af-render-contract-consumer-dry-read-001" in artifact_ids
    assert "clip-ed10ag-lineage-and-observation-surface-001" in artifact_ids
    assert "clip-ed10ah-production-limitation-lift-entry-001" in artifact_ids
    assert "clip-ed10ah-render-readiness-separation-readback-001" in artifact_ids
    assert "clip-ed10ai-final-render-path-readiness-packet-001" in artifact_ids
    assert "clip-ed10aj-final-render-path-stage-1-001" in artifact_ids
    assert "clip-ed10ak-final-render-path-stage-2-replayability-001" in artifact_ids
    assert "clip-ed10al-final-render-path-stage-3-rehearsal-001" in artifact_ids
    assert "clip-ed10am-production-limitation-lift-stage-1-001" in artifact_ids
    assert (
        "clip-ed10an-production-limitation-lift-stage-2-decision-packet-001"
        in artifact_ids
    )
    assert (
        "clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001"
        in artifact_ids
    )
    assert "clip-ed10as-internal-review-access-sheet-fullpath-001" in artifact_ids
    assert "clip-ed10ar-internal-review-video-candidate-package-001" in artifact_ids
    assert (
        "clip-ed10au-representative-micro-scene-internal-review-specimen-001"
        in artifact_ids
    )
    assert "clip-ed10av-micro-scene-observation-frame-readback-001" in artifact_ids
    assert (
        "clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001"
        in artifact_ids
    )
    assert "clip-ed10ax-review-frame-clarification-surface-001" in artifact_ids
    assert (
        "clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001"
        in artifact_ids
    )
    assert (
        "clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001" in artifact_ids
    )
    assert "clip-ed10bc-thank-v2-open-command-repair-readback-001" in artifact_ids
    assert "clip-ed10at-internal-review-observation-readback-001" in artifact_ids
    assert (
        "clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001"
        in artifact_ids
    )
    assert status["artifact_coverage"]["current_focus_artifact_registered"] is True

    artifact_by_id = {item["artifact_id"]: item for item in status["active_artifacts"]}
    cpd12 = artifact_by_id["clip-cpd12-minimal-review-console-v0-001"]
    assert cpd12["repo_relative_path"] == "docs/content_planning/operator_cockpit.html"
    assert (
        cpd12["open_command"] == "start docs\\content_planning\\operator_cockpit.html"
    )


def test_ed10ar_internal_review_video_candidate_package_is_bounded_and_non_approving():
    path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "internal-review-video-candidate-package.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["artifact_id"] == (
        "clip-ed10ar-internal-review-video-candidate-package-001"
    )
    assert payload["feature_id"] == "ED-10ar"
    assert payload["source_stage5_user_decision_ready_artifact_id"] == (
        "clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001"
    )
    assert payload["source_stage4_user_decision_card_artifact_id"] == (
        "clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001"
    )
    assert payload["existing_output_first"]["sufficient"] is True
    assert payload["existing_output_first"]["new_render_run"] is False
    assert payload["package_contents"]["video"]["status"] == (
        "present_same_machine_ignored_local"
    )
    assert payload["package_contents"]["video"]["duration_seconds"] == 4.2
    assert payload["package_contents"]["video"]["resolution"] == "1920x1080"
    assert payload["package_contents"]["subtitle_ass"]["status"] == (
        "present_same_machine_ignored_local"
    )
    assert payload["package_contents"]["local_manifest"]["status"] == (
        "present_same_machine_ignored_local"
    )
    assert payload["human_burden_hygiene"]["answer_style"] == "freeform"
    assert payload["human_burden_hygiene"]["template_required"] is False
    assert payload["human_burden_hygiene"]["max_required_points"] == 3
    assert payload["human_burden_hygiene"]["fixed_form_required"] is False
    assert payload["human_burden_hygiene"]["fixed_choice_rows_allowed"] is False
    assert payload["human_burden_hygiene"]["fixed_choice_rows_emitted"] is False
    assert payload["human_burden_hygiene"]["binary_choice_rows_emitted"] is False
    assert payload["human_burden_hygiene"]["yes_no_rows_emitted"] is False
    assert payload["human_burden_hygiene"]["required_labels"] == []
    assert payload["human_burden_hygiene"]["screenshot_required"] is False
    assert payload["human_burden_hygiene"]["user_decision_requested_now"] is False
    assert payload["boundaries"]["production_subtitle_design_acceptance"] is False
    assert payload["boundaries"]["production_render_acceptance"] is False
    assert payload["boundaries"]["creative_acceptance"] is False
    assert payload["boundaries"]["rights_status"] == "pending"
    assert payload["boundaries"]["publishing_acceptance"] is False
    assert payload["boundaries"]["public_use_permission"] is False
    assert payload["boundaries"]["monetization_acceptance"] is False
    assert payload["boundaries"]["final_render_path_approved"] is False
    assert payload["boundaries"]["episodes_tracked"] is False
    assert (
        payload["next_executable_route"] == "optional-internal-review-video-observation"
    )
    serialized = json.dumps(payload, ensure_ascii=False)
    assert ("yes_no" + "_unclear") not in serialized
    assert ('"decision' + '_card":') not in serialized
    assert "stage-6-user-freeform-review-request" not in serialized


def test_ed10as_internal_review_access_sheet_records_full_paths_and_boundaries():
    path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "internal-review-video-candidate-access-sheet.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["artifact_id"] == (
        "clip-ed10as-internal-review-access-sheet-fullpath-001"
    )
    assert payload["feature_id"] == "ED-10as"
    assert payload["status"] == "ready_for_optional_user_review"
    assert payload["action_type"] == "USER_OPEN_ONLY_LATER"
    assert payload["source_internal_review_video_candidate_package_artifact_id"] == (
        "clip-ed10ar-internal-review-video-candidate-package-001"
    )
    assert payload["folder_full_path_current_host"].endswith(
        "subtitle_render_path_selector_probe"
    )
    assert payload["media"]["mp4"]["file_full_path_current_host"].endswith(
        "subtitle_render_path_selector_probe.mp4"
    )
    assert payload["media"]["mp4"]["status"] == "present_current_host"
    assert payload["media"]["ass"]["status"] == "present_current_host"
    assert payload["media"]["manifest"]["status"] == "present_current_host"
    assert payload["launcher_or_open_command"] == (
        "powershell -ExecutionPolicy Bypass -File "
        "scripts\\operator\\open_internal_review_video_candidate.ps1"
    )
    assert len(payload["steps"]) == 3
    assert len(payload["look_for"]) == 3
    assert payload["answer_style"] == "freeform"
    assert payload["answer_hint"] == "One sentence is enough."
    assert "Post-Observation Relay" == payload["post_observation_relay"]["relay_label"]
    assert payload["boundaries"]["new_render"] is False
    assert payload["boundaries"]["new_replay"] is False
    assert payload["boundaries"]["media_modified"] is False
    assert payload["boundaries"]["episodes_tracked"] is False
    assert payload["boundaries"]["production_acceptance"] is False
    assert payload["boundaries"]["rights_public_use_approval"] is False
    assert payload["boundaries"]["publishing_acceptance"] is False
    assert payload["boundaries"]["monetization_acceptance"] is False

    script = (
        REPO_ROOT / "scripts" / "operator" / "open_internal_review_video_candidate.ps1"
    )
    script_text = script.read_text(encoding="utf-8")
    assert "Invoke-Item -LiteralPath $video" in script_text
    assert "OpenFolder" in script_text


def test_ed10at_internal_review_observation_readback_is_bounded_and_non_approving():
    path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "internal-review-video-observation-readback.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["artifact_id"] == (
        "clip-ed10at-internal-review-observation-readback-001"
    )
    assert payload["feature_id"] == "ED-10at"
    assert (
        payload["source_internal_review_video_candidate_access_sheet_artifact_id"]
        == "clip-ed10as-internal-review-access-sheet-fullpath-001"
    )
    assert (
        payload["source_internal_review_video_candidate_package_artifact_id"]
        == "clip-ed10ar-internal-review-video-candidate-package-001"
    )
    assert payload["source_context"]["requested_access_sheet_files_present"] is True
    assert (
        payload["source_context"]["requested_candidate_package_files_present"] is True
    )
    assert payload["source_context"]["stale_checkout_anchor_repaired"] is True
    assert payload["user_observation"]["opened_mp4"] is True
    assert (
        payload["user_observation"]["reported_duration_matches_short_expectation"]
        is True
    )
    assert payload["user_observation"]["reported_subtitles_all_present"] == [
        "NORMAL DIALOGUE CUE",
        "SHOUT HIGH INTENSITY",
        "LOW PRESSURE WHISPER CUE",
    ]
    by_axis = {item["axis"]: item for item in payload["observation_classifications"]}
    assert by_axis["openability"]["classification"] == "pass"
    assert by_axis["duration"]["classification"] == "expected_pass"
    assert by_axis["subtitle_cue_coverage"]["classification"] == (
        "pass_for_diagnostic_cue_probe"
    )
    assert by_axis["subtitle_cue_coverage"]["actual_script_content_present"] is False
    assert by_axis["narrative_video_continuity"]["classification"] == (
        "warning_not_representative_review"
    )
    assert by_axis["memo_like_appearance"]["classification"] == "warning_observed"
    assert by_axis["review_guidance_clarity"]["classification"] == "partial_or_fail"
    assert by_axis["artifact_semantics"]["classification"] == (
        "diagnostic_subtitle_render_path_cue_probe"
    )
    assert payload["next_practical_axis"]["recommended_route_id"] == (
        "representative-micro-scene-internal-review-specimen"
    )
    assert payload["next_practical_axis"]["alternate_route_id"] == (
        "final-render-path-stage-4"
    )
    assert payload["next_practical_axis"]["do_not_use_route_id"] == (
        "stage-7-freeform-normalizer"
    )
    assert payload["review_policy"]["fixed_form_required"] is False
    assert payload["review_policy"]["yes_no_required"] is False
    assert payload["review_policy"]["screenshot_required"] is False
    assert payload["review_policy"]["stage_7_freeform_normalizer_used"] is False
    assert payload["render_gate"]["new_render_run"] is False
    assert payload["render_gate"]["new_media_created"] is False
    assert payload["render_gate"]["episodes_tracked"] is False
    assert payload["boundaries"]["production_subtitle_design_acceptance"] is False
    assert payload["boundaries"]["production_render_acceptance"] is False
    assert payload["boundaries"]["creative_acceptance"] is False
    assert payload["boundaries"]["rights_status"] == "pending"
    assert payload["boundaries"]["publishing_acceptance"] is False
    assert payload["boundaries"]["public_use_permission"] is False
    assert payload["boundaries"]["monetization_acceptance"] is False
    assert payload["boundaries"]["user_observation_converted_to_approval"] is False
    assert payload["validation"]["all_checks_passed"] is True


def test_ed10au_representative_micro_scene_specimen_is_access_verified_and_bounded():
    path = (
        REPO_ROOT
        / "docs"
        / "style_intent"
        / "representative-micro-scene-internal-review-specimen.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    scene = payload["micro_scene"]
    access = payload["access_sheet"]

    assert payload["artifact_id"] == (
        "clip-ed10au-representative-micro-scene-internal-review-specimen-001"
    )
    assert payload["feature_id"] == "ED-10au"
    assert payload["source_internal_review_observation_readback_artifact_id"] == (
        "clip-ed10at-internal-review-observation-readback-001"
    )
    assert (
        payload["source_internal_review_video_candidate_access_sheet_artifact_id"]
        == "clip-ed10as-internal-review-access-sheet-fullpath-001"
    )
    assert (
        payload["source_internal_review_video_candidate_package_artifact_id"]
        == "clip-ed10ar-internal-review-video-candidate-package-001"
    )
    assert payload["source_context"]["source_text"] == (
        "real_transcript_sub_004_to_sub_006"
    )
    assert payload["source_context"]["source_episode_segment"][
        "source_subtitle_ids"
    ] == [
        "sub_004",
        "sub_005",
        "sub_006",
    ]
    assert scene["actual_script_content_present"] is True
    assert scene["cue_labels_used_as_main_content"] is False
    assert scene["script_event_count"] == 3
    assert scene["duration_seconds"] == 9.18
    assert [event["source_subtitle_id"] for event in scene["script_events"]] == [
        "sub_004",
        "sub_005",
        "sub_006",
    ]
    script_text = "\n".join(event["text"] for event in scene["script_events"])
    assert "団長" in script_text
    assert "倒して回ってるんです" in script_text
    assert "マリンならあっちにいたよ" in script_text
    for cue_label in scene["forbidden_cue_labels"]:
        assert cue_label not in script_text
    assert access["access_state"] == "verified_present"
    assert access["target_exists"] is True
    assert access["access_evidence_level"] == "file_exists_and_ffprobe_metadata"
    assert access["evidence_source"] == "local_render_result_probe"
    assert access["mp4_size_bytes"] > 0
    assert access["manifest_size_bytes"] > 0
    assert access["launcher_or_open_command"] == (
        "powershell -ExecutionPolicy Bypass -File "
        "scripts\\operator\\open_representative_micro_scene_internal_review_specimen.ps1"
    )
    assert payload["render_gate"]["new_render_run"] is True
    assert payload["render_gate"]["new_media_created"] is True
    assert payload["render_gate"]["tracked_binary_artifact_created"] is False
    assert payload["render_gate"]["episodes_tracked"] is False
    assert payload["review_guidance"]["answer_style"] == "freeform"
    assert len(payload["review_guidance"]["look_for"]) <= 3
    assert payload["review_guidance"]["user_review_requested_now"] is False
    assert payload["boundaries"]["stage_7_freeform_normalizer_used"] is False
    assert payload["boundaries"]["tracked_binary_artifact_created"] is False
    assert payload["boundaries"]["episodes_tracked"] is False
    assert payload["boundaries"]["production_render_acceptance"] is False
    assert payload["boundaries"]["public_use_permission"] is False
    assert payload["boundaries"]["rights_status"] == "pending"
    assert payload["validation"]["all_checks_passed"] is True
