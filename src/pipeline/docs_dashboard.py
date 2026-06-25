"""Docs v1.5 dashboard builder.

The dashboard is intentionally static and repo-local: it helps operators find
the current wiki entry points, active artifacts, and docs that need tightening.
It does not inspect ignored episode media or make production/public claims.
"""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_ID = "clippipegen.docs_dashboard.v1_5"
DEFAULT_GENERATED_AT = "2026-06-22"
FINDING_DISPLAY_LIMIT = 50
FEATURE_DISPLAY_LIMIT = 120
REQUIRED_FRONT_SECTIONS = {
    "what_it_is": ("## What This Is", "## これは何か"),
    "current_state": ("## Current State", "## Current Capsule", "## 今の状態"),
    "next": ("## Next", "## これからどうなるか", "## 次に進める入口"),
    "constraints_risks": ("## Constraints / Risks", "## Constraints/Risks"),
}
BOUNDARY_TERMS = (
    "production",
    "rights",
    "publishing",
    "public use",
    "acceptance",
    "承認",
    "権利",
    "公開",
)
PRIORITY_DOCS = (
    Path("README.md"),
    Path("docs/index.md"),
    Path("docs/RUNTIME_STATE.md"),
    Path("docs/FEATURE_REGISTRY.md"),
    Path("docs/EPISODE_REVIEW_WORKFLOW.md"),
    Path("docs/OPERATOR_REVIEW_UX.md"),
    Path("docs/SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md"),
    Path("docs/SUBTITLE_STYLE_INTENT_REGISTRY.md"),
    Path("docs/REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md"),
    Path("artifacts/ARTIFACTS.md"),
)
STATUS_PROGRESS = {
    "done": 100,
    "successor-lane": 100,
    "in_progress": 70,
    "approved": 25,
    "hold": 25,
    "proposed": 0,
    "rejected": 0,
}
STATUS_HEALTH = {
    "done": "stable",
    "successor-lane": "superseded",
    "in_progress": "active",
    "approved": "ready",
    "hold": "blocked",
    "proposed": "backlog",
    "rejected": "retired",
}


def build_project_status(
    *,
    base_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
) -> dict[str, Any]:
    docs = _collect_docs(base_dir)
    all_findings = _doc_health_findings(docs)
    findings = all_findings[:FINDING_DISPLAY_LIMIT]
    features = _feature_rows(base_dir)
    artifacts = _artifact_rows(base_dir)
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": "v1.5",
        "generated_at": generated_at,
        "project": {
            "name": "ClipPipeGen",
            "wiki_entry": "docs/index.md",
            "dashboard_html": "docs/dashboard/index.html",
            "dashboard_json": "docs/dashboard/project-status.json",
        },
        "metadata_schema": {
            "doc_fields": [
                "path",
                "title",
                "line_count",
                "front_sections",
                "status",
            ],
            "finding_types": ["stale", "unclear", "over_guarded"],
            "boundary_policy": (
                "Production/public/rights caveats belong in Constraints / Risks "
                "instead of being repeated as the opening sentence of every doc."
            ),
        },
        "current_focus": {
            "feature_id": "ED-10ae",
            "artifact_id": "clip-ed10ae-render-path-selector-contract-probe-001",
            "source_style_family_palette_artifact_id": "clip-ed10ad-style-family-palette-axis-proof-001",
            "source_visual_selector_artifact_id": "clip-ed10ac-visual-selector-proof-001",
            "source_selector_artifact_id": "clip-ed10ab-subtitle-preset-selector-001",
            "source_style_intent_artifact_id": "clip-ed10aa-subtitle-style-intent-registry-001",
            "source_render_path_artifact_id": "clip-ed10z-tiny-render-path-nearer-probe-001",
            "source_review_artifact_id": "clip-ed10y-candidate2-carry-forward-001",
            "source_previous_artifact_id": "clip-ed10y-candidate2-carry-forward-001",
            "source_comparison_artifact_id": "clip-ed10o-multifont-focused-review-001",
            "source_proof_artifact_id": "clip-ed10r-keifont-dense-stress-proof-001",
            "state": "render_path_selector_contract_ready",
            "human_visual_judgement": "ed10w_candidate2_lead_freeform_review_consumed_then_ed10z_probe_completed",
            "latest_review_consumed": "ed10w_user_review_candidate0_and_2_good_candidate1_and_3_too_thin",
            "target_cuts": ["cut_008"],
            "accepted_size_rule": "round(frame_height * 0.115)",
            "selected_typography_base": "ed10l_keifont_pop_dialogue_candidate",
            "selected_source_license_install_route": "ed10l_keifont_pop_dialogue_candidate",
            "route_status": "ed10ae_render_path_selector_contract_ready_l0_no_render",
            "user_action_type": "NO_USER_ACTION_STATIC_READBACK_ONLY",
            "next_review_action_type": "NO_REVIEW_CARD_REVIEW_CONSUMED",
            "selected_typography_source": "ed10y_candidate2_carry_forward_source_state",
            "preferred_direction": "candidate2_badge_pressure_adjustment_with_candidate0_fallback",
            "main_issue": "static_selector_to_render_path_contract_readback",
            "current_visual_comparison_validity": "valid_requested_keifont_visual_evidence",
            "current_lead_candidate_id": "ed10w_badge_label_pressure_adjustment",
            "fallback_reference_candidate_id": "ed10w_current_pass_reference",
            "held_reference_candidate_ids": [
                "ed10w_lighter_outline_shadow_pressure",
                "ed10w_balanced_combined_low_risk",
            ],
            "lead_status": "provisional_bounded_decoration_lead",
            "font_visual_evidence_status": "valid_requested_keifont_visual_evidence_on_current_windows_profile",
            "local_generation_status": "ed10ae_render_path_contract_ready_no_render",
            "user_review_status": "consumed_no_user_review_required_now",
            "multiline_wrap_evidence_status": "passed_diagnostic_review",
            "multiline_wrap_evidence": {
                "status": "passed_diagnostic_review",
                "target_cut_id": "cut_008",
                "subtitle_id": "sub_096",
                "wrapped_line_count": 2,
                "screenshot_role": "multiline_wrap_1",
                "screenshot_default_max_width_px": 220,
                "review_implication": "cut_008 multiline/wrap evidence already passed; ED-10w does not ask for the same pass again.",
            },
            "bounded_decoration_candidates": [
                "ed10w_current_pass_reference",
                "ed10w_lighter_outline_shadow_pressure",
                "ed10w_badge_label_pressure_adjustment",
                "ed10w_balanced_combined_low_risk",
            ],
            "candidate_delta_visibility": {
                "status": "consumed_candidate2_probe_profile_ready_after_ed10y",
                "source_review": (
                    "Candidate 0 and Candidate 2 are acceptable/good; Candidate "
                    "1 and Candidate 3 read too thin; full-frame context was "
                    "still somewhat small."
                ),
                "default_evidence": [
                    "compact subtitle body crops",
                    "compact SPK badge crops",
                    "actual style parameter delta readback",
                ],
                "full_frame_evidence": "larger details view retained from ED-10y source state",
                "candidate_delta_expectation": {
                    "candidate_0": "baseline reference; no visual delta",
                    "candidate_1": "outline/shadow visibly lighter than baseline",
                    "candidate_2": "SPK badge text/background opacity visibly reduced",
                    "candidate_3": "combined outline/shadow and SPK badge pressure reduction",
                },
            },
            "render_path_readiness": {
                "status": "ed10z_actual_generation_available_requires_human_review_after_explicit_ffmpeg_ffprobe_paths",
                "recommended_minimal_next_route": "use_ed10z_as_local_readback_then_open_separate_limitation_lift_or_final_render_path_route_if_needed",
                "latest_actual_rerun": {
                    "visual_proof_status": "available_requires_human_review",
                    "review_card_status": "withheld_tiny_render_path_nearer_probe_completed",
                    "subtitle_overlay_available_count": 1,
                    "focused_proof_review_status": "tiny_render_path_nearer_probe_completed",
                },
                "not_accepted": [
                    "production_subtitle_design_acceptance",
                    "production_render_acceptance",
                    "creative_acceptance",
                    "rights_clearance",
                    "publishing_acceptance",
                    "public_use_permission",
                ],
            },
            "subtitle_style_intent_registry": {
                "status": "diagnostic_intent_registry_ready",
                "artifact_id": "clip-ed10aa-subtitle-style-intent-registry-001",
                "doc": "docs/SUBTITLE_STYLE_INTENT_REGISTRY.md",
                "metadata_json": "docs/style_intent/subtitle-style-intent-registry.json",
                "axes": [
                    "speaker_id",
                    "speaker_role",
                    "emotion",
                    "intensity",
                    "utterance_role",
                    "readability_priority",
                ],
                "body_text_color_policy": "stable_by_default",
                "character_color_policy": "speaker_badge_and_accent_before_body_text",
                "agent_proposal_rule": "map_semantic_tags_to_presets_without_raw_numeric_review",
                "human_review_required_for": [
                    "new_style_family",
                    "new_color_palette",
                    "body_text_color_policy_change",
                    "production_route_change",
                    "rights_or_publication_decision",
                ],
            },
            "subtitle_preset_selector": {
                "status": "diagnostic_preset_selector_ready",
                "artifact_id": "clip-ed10ab-subtitle-preset-selector-001",
                "implementation": "src/integrations/render/subtitle_preset_selector.py",
                "metadata_json": "docs/style_intent/subtitle-preset-selector.json",
                "source_registry_artifact_id": "clip-ed10aa-subtitle-style-intent-registry-001",
                "input_axes": [
                    "speaker_id",
                    "speaker_role",
                    "emotion",
                    "intensity",
                    "utterance_role",
                    "readability_priority",
                ],
                "output_style_tokens": [
                    "font_family_role",
                    "font_size_scale",
                    "outline_shadow_strength",
                    "badge_color_token",
                    "accent_color_token",
                    "backplate_box_token",
                    "motion_primitive",
                    "safe_area_line_break_behavior",
                    "body_text_color_token",
                ],
                "example_ids": [
                    "neutral_dialogue_intensity_0",
                    "shout_intensity_2",
                    "whisper_intensity_1",
                    "ominous_intensity_2",
                    "narration_intensity_0",
                    "system_note_intensity_0",
                ],
                "body_text_color_policy": "stable_default_body_text",
                "character_color_policy": "badge_and_accent_first",
                "new_render_run": False,
            },
            "subtitle_visual_selector_proof": {
                "status": "visual_selector_proof_ready",
                "artifact_id": "clip-ed10ac-visual-selector-proof-001",
                "source_selector_artifact_id": "clip-ed10ab-subtitle-preset-selector-001",
                "metadata_json": "docs/style_intent/subtitle-visual-selector-proof.json",
                "html": "docs/style_intent/subtitle-visual-selector-proof.html",
                "proof_kind": "tracked_static_html_json_readback",
                "example_ids": [
                    "neutral_dialogue_intensity_0",
                    "shout_intensity_2",
                    "whisper_intensity_1",
                    "ominous_intensity_2",
                    "narration_intensity_0",
                    "system_note_intensity_0",
                ],
                "visual_differentiators": [
                    "badge_color_token",
                    "accent_color_token",
                    "backplate_box_token",
                    "font_size_scale",
                    "outline_shadow_strength",
                    "motion_primitive",
                    "safe_area_line_break_behavior",
                ],
                "body_text_color_policy": "stable_default_body_text",
                "character_color_policy": "badge_and_accent_first",
                "existing_output_first_considered": True,
                "new_render_run": False,
            },
            "subtitle_style_family_palette_axis_proof": {
                "status": "style_family_palette_axis_proof_ready",
                "artifact_id": "clip-ed10ad-style-family-palette-axis-proof-001",
                "source_visual_selector_artifact_id": "clip-ed10ac-visual-selector-proof-001",
                "metadata_json": "docs/style_intent/subtitle-style-family-palette-proof.json",
                "html": "docs/style_intent/subtitle-style-family-palette-proof.html",
                "proof_kind": "tracked_static_html_json_readback",
                "example_ids": [
                    "neutral_dialogue_intensity_0",
                    "shout_intensity_2",
                    "whisper_intensity_1",
                    "ominous_intensity_2",
                    "narration_intensity_0",
                    "system_note_intensity_0",
                ],
                "style_family_axis": [
                    "dialogue_current_keifont_family",
                    "emphasis_energy_family",
                    "quiet_soft_readability_family",
                    "ominous_inner_voice_family",
                    "narration_family",
                    "system_note_family",
                ],
                "palette_axis": [
                    "speaker_identity_blue",
                    "high_energy_warm",
                    "quiet_cool",
                    "ominous_dark",
                    "narration_neutral_green",
                    "system_neutral",
                ],
                "body_text_color_policy": "stable_default_body_text",
                "palette_surfaces": [
                    "badge_color_token",
                    "accent_color_token",
                    "backplate_box_token",
                ],
                "new_style_family_created": False,
                "new_palette_created": False,
                "existing_output_first_considered": True,
                "new_render_run": False,
            },
            "subtitle_render_path_selector_contract": {
                "status": "render_path_selector_contract_ready",
                "artifact_id": "clip-ed10ae-render-path-selector-contract-probe-001",
                "source_style_family_palette_artifact_id": "clip-ed10ad-style-family-palette-axis-proof-001",
                "metadata_json": "docs/style_intent/subtitle-render-path-selector-contract.json",
                "doc": "docs/style_intent/subtitle-render-path-selector-contract.md",
                "contract_kind": "static_selector_to_render_path_readback",
                "render_level": "L0 No Render",
                "example_ids": [
                    "neutral_dialogue_intensity_0",
                    "shout_intensity_2",
                    "whisper_intensity_1",
                    "ominous_intensity_2",
                    "narration_intensity_0",
                    "system_note_intensity_0",
                ],
                "semantic_fields": [
                    "semantic_preset_id",
                    "preset_key",
                    "speaker_id",
                    "speaker_role",
                    "emotion",
                    "intensity",
                    "utterance_role",
                    "readability_priority",
                ],
                "style_axis_fields": [
                    "family_id",
                    "palette_route",
                    "font_family_role",
                    "font_size_scale",
                    "outline_shadow_strength",
                ],
                "color_surface_fields": [
                    "badge_color_token",
                    "accent_color_token",
                    "backplate_box_token",
                    "body_text_color_token",
                    "body_text_color_changed",
                ],
                "motion_line_break_fields": [
                    "motion_primitive",
                    "safe_area_line_break_behavior",
                ],
                "later_l2_tiny_render_trigger": "not_triggered_in_this_slice",
                "new_render_run": False,
            },
            "review_surface_layout_debt": {
                "status": "recorded_minimal_primary_layout_improvement_applied",
                "issue": "primary Candidate Visual Evidence samples remained too small/compressed",
                "safe_improvement": "avoid cramped four-column grid; keep Candidate 2 lead and Candidate 0 fallback prominent; keep Candidate 1/3 secondary/collapsible",
                "same_candidate_review_reopened": False,
            },
            "line_break_policy_readback": {
                "status": "diagnostic_policy_recorded",
                "authority": "japanese_boundary_font_bbox_pixel_wrap_v1",
                "measurement_authority": "font_bbox_pixel_measurement_not_grid_cell_count",
                "accepted_evidence": "cut_008/sub_096 two-line wrap",
                "accepted_scope": "diagnostic_dense_stress_multiline_wrap_pass",
                "future_tuning_areas": [
                    "line_length",
                    "max_lines",
                    "orphan_control",
                    "short_suffix_tail_control",
                    "safe_area_pressure",
                    "rapid_cue_replacement",
                    "outline_shadow_badge_pressure",
                ],
                "shared_policy_note": (
                    "Keep line-break/layout/decoration policy structured for "
                    "future NLMYTGen sharing consideration; ED-10z does not read, "
                    "edit, or depend on NLMYTGen files and does not extract a "
                    "shared package."
                ),
            },
            "review_memory": {
                "subject": "ED-10w bounded subtitle presentation candidates",
                "prior_review_count": "3+",
                "latest_freeform_review_consumed": True,
                "latest_freeform_review_summary": (
                    "Candidate 0 and Candidate 2 are acceptable/good; Candidate "
                    "1 and Candidate 3 look too thin; the same Candidate 0-3 "
                    "comparison should not be repeated."
                ),
                "lead_candidate": "ed10w_badge_label_pressure_adjustment",
                "fallback_reference": "ed10w_current_pass_reference",
                "held_references": [
                    "ed10w_lighter_outline_shadow_pressure",
                    "ed10w_balanced_combined_low_risk",
                ],
                "accepted_scope": [
                    "diagnostic_representative_review",
                    "provisional_normal_dialogue_baseline",
                    "diagnostic_dense_stress_pass",
                    "diagnostic_multiline_wrap_pass",
                    "candidate2_bounded_badge_pressure_adjustment_lead",
                    "tiny_render_path_nearer_probe_profile_readback",
                ],
                "not_accepted_scope": [
                    "production_subtitle_design",
                    "production_render",
                    "creative_acceptance",
                    "rights",
                    "publishing",
                    "public_use",
                ],
                "next_nonredundant_axis": [
                    "production_limitation_lift",
                    "final_render_path_probe",
                    "future_shared_subtitle_layout_policy",
                ],
                "repeated_general_review": False,
                "repeated_cut_008_review_allowed": False,
                "same_candidate_comparison_review_allowed": False,
                "review_reset_trigger_active": [
                    "new_axis_or_changed_evidence_only"
                ],
                "current_blocker": "none_for_tiny_render_path_nearer_probe",
                "font_evidence_gate": "valid_requested_keifont_visual_evidence",
            },
            "review_card": {
                "status": "withheld_latest_review_already_consumed",
                "action_type": "NO_REVIEW_CARD_REVIEW_CONSUMED",
                "target": "clip-ed10ae-render-path-selector-contract-probe-001",
                "artifact_id": "clip-ed10ae-render-path-selector-contract-probe-001",
                "axis": "render_path_selector_contract_readback",
                "prior_review_count": "3+",
                "prior_signal_summary": "Keifont normal dialogue and dense/multiline route passed diagnostically.",
                "what_changed": "ED-10ae maps the static selector, family, palette, color surface, motion, and line-break fields to a no-render render-adapter input contract.",
                "what_this_review_decides": [],
                "not_asking": [
                    "Candidate 0-3 comparison review",
                    "general Keifont acceptance",
                    "cut_002 / cut_003 review",
                    "same cut_008 dense/multiline pass",
                    "production subtitle design acceptance",
                ],
                "input_mode": "none",
                "completion_signal": "use the selector-to-render-path contract before a later L2 tiny render probe; production, rights, publishing, and public-use routes remain separate",
            },
            "lead_fallback_readback": {
                "status": "candidate2_promoted_to_tiny_render_path_nearer_probe_lead",
                "lead_candidate": "ed10w_badge_label_pressure_adjustment",
                "fallback_reference": "ed10w_current_pass_reference",
                "held_references": [
                    "ed10w_lighter_outline_shadow_pressure",
                    "ed10w_balanced_combined_low_risk",
                ],
            },
            "review_surface_direction": "render_path_selector_contract_static_readback_no_render",
            "focused_review_html": "episodes/.../subtitle_presentation_review_pack.html",
            "review_debt": [
                {
                    "debt_id": "production_limitation_lift",
                    "status": "not_started_after_tiny_probe",
                    "next_action": "start a separate limitation-lift/final render-path route only after explicit acceptance scope is opened",
                }
            ],
            "emoji_treatment": "neutral_ignore_for_evaluation",
            "production_candidate": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "production_usage_allowed": False,
            "publishing_acceptance": False,
            "public_use_permission": False,
            "rights_status": "pending",
        },
        "open_surfaces": _open_surfaces(),
        "wiki_entrypoints": _wiki_entrypoints(),
        "features": features,
        "feature_summary": _feature_summary(features),
        "active_artifacts": artifacts,
        "artifact_summary": _artifact_summary(artifacts),
        "artifact_coverage": _artifact_coverage(features, artifacts),
        "next_review_items": _next_review_items(),
        "docs": docs,
        "doc_health": {
            "finding_count": len(findings),
            "finding_total": len(all_findings),
            "finding_limit": FINDING_DISPLAY_LIMIT,
            "findings_truncated": len(all_findings) > FINDING_DISPLAY_LIMIT,
            "findings": findings,
        },
        "top_next_improvements": _top_next_improvements(),
    }


def write_project_status(
    *,
    base_dir: Path,
    output_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
) -> dict[str, Any]:
    status = build_project_status(base_dir=base_dir, generated_at=generated_at)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "project-status.json"
    html_path = output_dir / "index.html"
    features_path = output_dir.parent / "features" / "index.md"
    _write_text_lf(
        json_path,
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(html_path, render_dashboard_html(status))
    features_path.parent.mkdir(parents=True, exist_ok=True)
    _write_text_lf(features_path, render_features_index_markdown(status))
    return {
        "status": status,
        "json_path": json_path,
        "html_path": html_path,
        "features_path": features_path,
    }


def render_dashboard_html(status: dict[str, Any]) -> str:
    focus = status["current_focus"]
    findings = status["doc_health"]["findings"]
    docs = status["docs"]
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>ClipPipeGen Docs Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; line-height: 1.5; color: #20242a; }}
    table {{ border-collapse: collapse; table-layout: fixed; width: 100%; margin: 12px 0 24px; }}
    th, td {{ border: 1px solid #c8d0d9; padding: 8px; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ background: #edf2f7; text-align: left; }}
    .status {{ display: inline-block; padding: 2px 6px; border: 1px solid #9eb3c7; background: #f4f8fb; }}
    .warn {{ color: #7a4100; }}
    code {{ background: #f3f3f3; padding: 1px 4px; white-space: normal; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>ClipPipeGen Docs Dashboard</h1>
  <p>Generated from <code>{escape(status["schema_id"])}</code> at {escape(status["generated_at"])}.</p>
  <section>
    <h2>Current Focus</h2>
    <p><span class="status">{escape(focus["state"])}</span></p>
    <table>
      <tr><th>feature</th><td>{escape(focus["feature_id"])}</td></tr>
      <tr><th>artifact</th><td>{escape(focus["artifact_id"])}</td></tr>
      <tr><th>targets</th><td>{escape(", ".join(focus["target_cuts"]))}</td></tr>
      <tr><th>typography base</th><td>{escape(focus["selected_typography_base"])}</td></tr>
      <tr><th>source/install route</th><td>{escape(focus["selected_source_license_install_route"])}</td></tr>
      <tr><th>route status</th><td>{escape(focus["route_status"])}</td></tr>
      <tr><th>user action</th><td>{escape(focus["user_action_type"])}</td></tr>
      <tr><th>next review</th><td>{escape(focus["next_review_action_type"])}</td></tr>
      <tr><th>rights / production</th><td>rights={escape(focus["rights_status"])}; production_candidate={escape(str(focus["production_candidate"]).lower())}</td></tr>
    </table>
  </section>
  <section>
    <h2>Open Surfaces</h2>
    <p>Normal order: run <code>.\\open-dashboard.ps1</code>, choose an artifact, then use an artifact-specific launcher only when needed.</p>
    {_open_surfaces_table_html(status["open_surfaces"])}
  </section>
  <section>
    <h2>Feature Progress</h2>
    {_features_table_html(status["features"])}
  </section>
  <section>
    <h2>Active Artifacts</h2>
    {_artifacts_table_html(status["active_artifacts"])}
    <p>Artifact coverage: {escape(str(status["artifact_coverage"]["features_with_artifact_count"]))} feature rows mention registered artifacts; current focus artifact registered={escape(str(status["artifact_coverage"]["current_focus_artifact_registered"]).lower())}.</p>
  </section>
  <section>
    <h2>Next Review Items</h2>
    {_review_items_table_html(status["next_review_items"])}
  </section>
  <section>
    <h2>Wiki Entrypoints</h2>
    {_entrypoint_list_html(status["wiki_entrypoints"])}
  </section>
  <section>
    <h2>Doc Health Findings</h2>
    <p class="warn">{len(findings)} of {escape(str(status["doc_health"]["finding_total"]))} stale / unclear / over-guarded findings shown.</p>
    {_findings_table_html(findings)}
  </section>
  <section>
    <h2>Tracked Docs</h2>
    {_docs_table_html(docs)}
  </section>
  <section>
    <h2>Next Improvements</h2>
    {_improvements_table_html(status["top_next_improvements"])}
  </section>
</body>
</html>
"""


def _write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def render_features_index_markdown(status: dict[str, Any]) -> str:
    rows = [
        "| id | title | status | health | progress_pct | active_artifact | next_action |",
        "|---|---|---|---|---:|---|---|",
    ]
    for feature in status["features"]:
        rows.append(
            "| "
            + " | ".join(
                [
                    _md(feature["id"]),
                    _md(feature["title"]),
                    _md(feature["status"]),
                    _md(feature["health"]),
                    str(feature["progress_pct"]),
                    _md(feature.get("active_artifact") or ""),
                    _md(feature["next_action"]),
                ]
            )
            + " |"
        )
    return (
        "# Feature Dashboard\n\n"
        "This generated index is the scan-friendly v1.5 view of "
        "[../FEATURE_REGISTRY.md](../FEATURE_REGISTRY.md). Edit the registry "
        "or dashboard builder, then regenerate instead of hand-editing this "
        "table.\n\n"
        "## Current Focus\n\n"
        f"- feature: `{status['current_focus']['feature_id']}`\n"
        f"- artifact: `{status['current_focus']['artifact_id']}`\n"
        f"- state: `{status['current_focus']['state']}`\n\n"
        "## Feature Table\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _collect_docs(base_dir: Path) -> list[dict[str, Any]]:
    paths = list(PRIORITY_DOCS)
    paths.extend(sorted(Path("docs").glob("*.md")))
    seen: set[str] = set()
    docs: list[dict[str, Any]] = []
    for relative in paths:
        key = str(relative).replace("\\", "/")
        if key in seen:
            continue
        seen.add(key)
        path = base_dir / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        front_matter = _front_matter(text)
        docs.append(
            {
                "path": key,
                "title": _title(text, fallback=relative.stem),
                "line_count": len(text.splitlines()),
                "metadata": front_matter,
                "front_sections": _front_sections(text),
                "boundary_term_count": _boundary_term_count(text),
                "status": front_matter.get("status") or _doc_status(text),
            }
        )
    return docs


def _front_sections(text: str) -> dict[str, bool]:
    return {
        key: any(marker in text for marker in markers)
        for key, markers in REQUIRED_FRONT_SECTIONS.items()
    }


def _doc_health_findings(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for doc in docs:
        missing = [
            key for key, exists in doc["front_sections"].items() if exists is not True
        ]
        if missing and doc["path"] in {str(path).replace("\\", "/") for path in PRIORITY_DOCS}:
            findings.append(
                {
                    "type": "unclear",
                    "path": doc["path"],
                    "detail": "Missing v1.5 front sections: " + ", ".join(missing),
                    "suggested_fix": "Add What This Is / Current State / Next / Constraints / Risks before historical detail.",
                }
            )
        if doc["line_count"] > 450 and doc["path"] != "docs/RUNTIME_HISTORY.md":
            findings.append(
                {
                    "type": "stale",
                    "path": doc["path"],
                    "detail": f"Long active doc ({doc['line_count']} lines) is likely carrying history.",
                    "suggested_fix": "Move older closeouts to archive/history and keep this page as a pointer or dashboard surface.",
                }
            )
        if doc["boundary_term_count"] >= 18 and not doc["front_sections"].get(
            "constraints_risks"
        ):
            findings.append(
                {
                    "type": "over_guarded",
                    "path": doc["path"],
                    "detail": f"Boundary terms appear {doc['boundary_term_count']} times without a front Constraints / Risks section.",
                    "suggested_fix": "Collect repeated caveats into Constraints / Risks and keep the opening action-oriented.",
                }
            )
    return findings


def _feature_rows(base_dir: Path) -> list[dict[str, Any]]:
    path = base_dir / "docs/FEATURE_REGISTRY.md"
    if not path.exists():
        return []
    features: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] in {"ID", "---"}:
            continue
        feature_id = _clean_markdown(cells[0])
        if feature_id in seen or "-" not in feature_id:
            continue
        seen.add(feature_id)
        title = _clean_markdown(cells[1])
        status = _clean_markdown(cells[2])
        summary = _clean_markdown(cells[3])
        active_artifact = _first_artifact_id(cells[3])
        if feature_id == "ED-10g":
            active_artifact = "clip-ed10g-noto-overlay-proof-001"
        if feature_id == "ED-10i":
            active_artifact = "clip-ed10i-meiryo-overlay-proof-001"
        if feature_id == "ED-10j":
            active_artifact = "clip-ed10j-kirinuki-font-audit-001"
        if feature_id == "ED-10k":
            active_artifact = "clip-ed10k-biz-overlay-proof-001"
        if feature_id == "ED-10l":
            active_artifact = "clip-ed10l-known-kirinuki-font-pack-001"
        if feature_id == "ED-10m":
            active_artifact = "clip-ed10l-known-kirinuki-font-pack-001"
        if feature_id == "ED-10n":
            active_artifact = "clip-ed10n-keifont-overlay-proof-001"
        if feature_id == "ED-10o":
            active_artifact = "clip-ed10o-multifont-focused-review-001"
        if feature_id == "ED-10p":
            active_artifact = "clip-ed10p-keifont-lead-representative-proof-001"
        if feature_id == "ED-10q":
            active_artifact = "clip-ed10p-keifont-lead-representative-proof-001"
        if feature_id == "ED-10r":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10t":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10u":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10v":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10w":
            active_artifact = "clip-ed10w-subtitle-presentation-review-pack-001"
        if feature_id == "ED-10y":
            active_artifact = "clip-ed10y-candidate2-carry-forward-001"
        if feature_id == "ED-10z":
            active_artifact = "clip-ed10z-tiny-render-path-nearer-probe-001"
        if feature_id == "ED-10aa":
            active_artifact = "clip-ed10aa-subtitle-style-intent-registry-001"
        if feature_id == "ED-10ab":
            active_artifact = "clip-ed10ab-subtitle-preset-selector-001"
        if feature_id == "ED-10ac":
            active_artifact = "clip-ed10ac-visual-selector-proof-001"
        features.append(
            {
                "id": feature_id,
                "title": title,
                "status": status,
                "health": _feature_health(feature_id, status, summary),
                "progress_pct": _feature_progress(feature_id, status),
                "active_artifact": active_artifact,
                "next_action": _feature_next_action(feature_id, status, summary),
                "summary_excerpt": _truncate(summary, 220),
                "source_path": "docs/FEATURE_REGISTRY.md",
            }
        )
    return features[:FEATURE_DISPLAY_LIMIT]


def _feature_summary(features: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for feature in features:
        status = feature["status"]
        counts[status] = counts.get(status, 0) + 1
    return {"feature_count": len(features), "status_counts": counts}


def _artifact_rows(base_dir: Path) -> list[dict[str, Any]]:
    path = base_dir / "artifacts/ARTIFACTS.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## `([^`]+)`\s*$", text, flags=re.MULTILINE))
    rows: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        fields = _artifact_fields(block)
        rows.append(
            {
                "artifact_id": match.group(1),
                "title": fields.get("title", ""),
                "purpose": fields.get("purpose", ""),
                "storage_class": fields.get("storage class", ""),
                "repo_relative_path": fields.get("repo_relative_path", ""),
                "open_command": fields.get("open_command", ""),
                "review_status": fields.get("review_status", ""),
                "next_action": fields.get("next_action", ""),
            }
        )
    return rows


def _artifact_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [artifact["artifact_id"] for artifact in artifacts]
    return {"artifact_ids": ids, "artifact_count": len(ids)}


def _artifact_coverage(
    features: list[dict[str, Any]], artifacts: list[dict[str, Any]]
) -> dict[str, Any]:
    artifact_ids = {artifact["artifact_id"] for artifact in artifacts}
    mentioned = [
        feature for feature in features if feature.get("active_artifact") in artifact_ids
    ]
    current_focus_registered = (
        "clip-ed10ac-visual-selector-proof-001" in artifact_ids
    )
    return {
        "registered_artifact_count": len(artifact_ids),
        "features_with_artifact_count": len(mentioned),
        "current_focus_artifact_registered": current_focus_registered,
        "missing_registered_artifact_mentions": [
            feature["id"]
            for feature in features
            if feature.get("active_artifact")
            and feature.get("active_artifact") not in artifact_ids
        ],
    }


def _wiki_entrypoints() -> list[dict[str, str]]:
    return [
        {
            "path": "docs/index.md",
            "role": "Human-readable wiki front door.",
        },
        {
            "path": "docs/features/index.md",
            "role": "Generated feature progress table.",
        },
        {
            "path": "docs/dashboard/index.html",
            "role": "Status dashboard generated from project metadata.",
        },
        {
            "path": "docs/RUNTIME_STATE.md",
            "role": "Current resume capsule and next action.",
        },
        {
            "path": "artifacts/ARTIFACTS.md",
            "role": "Reviewable local artifact registry.",
        },
        {
            "path": "docs/FEATURE_REGISTRY.md",
            "role": "Feature status authority.",
        },
    ]


def _next_review_items() -> list[dict[str, str]]:
    return [
        {
            "item": "ED-10ae render-path selector contract",
            "artifact": "clip-ed10ae-render-path-selector-contract-probe-001",
            "question": "Are selector, family, palette, color-surface, motion, and line-break fields ready as a static input contract before any render probe?",
            "next_route": "Use this contract before a later L2 tiny render-path probe; do not infer actual render or production readiness.",
        },
        {
            "item": "ED-10ad style-family / palette axis proof",
            "artifact": "clip-ed10ad-style-family-palette-axis-proof-001",
            "question": "Can the six semantic presets be grouped by style family and palette route while body text color stays stable?",
            "next_route": "Use this static axis proof before any later render-path probe or separate style-family, palette, production, rights, publishing, or public-use route.",
        },
        {
            "item": "ED-10ac visual selector proof",
            "artifact": "clip-ed10ac-visual-selector-proof-001",
            "question": "Can the six semantic preset examples be inspected as badge/accent/backplate/size/motion/line-break differences while body text color stays stable?",
            "next_route": "Use this static proof for optional open-only observation before opening any new style-family, palette, production, rights, publishing, or public-use route.",
        },
        {
            "item": "ED-10ab subtitle preset selector",
            "artifact": "clip-ed10ab-subtitle-preset-selector-001",
            "question": "Can the six semantic intent axes map deterministically to style token candidates without raw numeric review?",
            "next_route": "Use as source selector for ED-10ac and future visual style proof work.",
        },
        {
            "item": "ED-10aa subtitle style intent registry",
            "artifact": "clip-ed10aa-subtitle-style-intent-registry-001",
            "question": "Can future subtitle styling map speaker/emotion/readability tags to presets without asking for tiny numeric adjustments?",
            "next_route": "Use as source registry for ED-10ab; ED-10z already has refreshed same-machine local readback.",
        },
        {
            "item": "ED-10z tiny render-path-nearer probe",
            "artifact": "clip-ed10z-tiny-render-path-nearer-probe-001",
            "question": "Has Candidate 2 been passed through the current diagnostic render path without reopening the Candidate 0-3 comparison?",
            "next_route": "Use the probe as local readback only; open production limitation-lift or final render-path work as a separate route.",
        },
        {
            "item": "ED-10v dense/stress pass and line-break policy readback",
            "artifact": "clip-ed10r-keifont-dense-stress-proof-001",
            "question": "Is the ED-10u cut_008 multiline/dense-stress pass preserved as prior state?",
            "next_route": "Use as source evidence only; ED-10z owns the current tiny render-path-nearer readback.",
        },
        {
            "item": "ED-10p Keifont representative proof baseline",
            "artifact": "clip-ed10p-keifont-lead-representative-proof-001",
            "question": "Is the ED-10n/ED-10o Keifont review history recorded as consumed rather than reopened?",
            "next_route": "Use as diagnostic representative normal-dialogue provisional baseline; do not request another general cut_002/cut_003 Keifont acceptance review.",
        },
        {
            "item": "ED-10o multi-font focused review reference",
            "artifact": "clip-ed10o-multifont-focused-review-001",
            "question": "Does the accepted focused review surface remain useful as the historical comparison reference?",
            "next_route": "Use the same-line matrix as reference only; it does not by itself approve a final baseline or production use.",
        },
        {
            "item": "ED-10n Keifont overlay proof",
            "artifact": "clip-ed10n-keifont-overlay-proof-001",
            "question": "Does the earlier Keifont overlay proof remain consistent with the provisional baseline record?",
            "next_route": "Use as consumed historical proof reference; ED-10r is now the current review entry.",
        },
        {
            "item": "ED-10l real-font comparison readback",
            "artifact": "clip-ed10l-known-kirinuki-font-pack-001",
            "question": "Does the real-font contact sheet confirm the per-user font resolver is using requested fonts rather than fallback?",
            "next_route": "Use the comparison only as readback support for the Keifont proof route unless another candidate must be promoted.",
        },
        {
            "item": "ED-10k BIZ UDGothic overlay proof",
            "artifact": "clip-ed10k-biz-overlay-proof-001",
            "question": "Was BIZ correctly kept as a reviewed rejected reference instead of the normal-dialogue baseline?",
            "next_route": "Use only as reference evidence for why the system-safe route was stopped.",
        },
        {
            "item": "ED-10j kirinuki font audit",
            "artifact": "clip-ed10j-kirinuki-font-audit-001",
            "question": "Was the no-download audit consumed correctly, including Meiryo reference demotion and BIZ default selection?",
            "next_route": "Use the contact-sheet readback only for audit; do not prolong the comparison unless the BIZ proof fails.",
        },
        {
            "item": "ED-10h font candidate sweep",
            "artifact": "clip-subtitle-font-candidate-sweep-001",
            "question": "Should Google Fonts / OFL candidates be downloaded or only compared when already local?",
            "next_route": "Use the candidate registry before any font binary enters Git.",
        },
        {
            "item": "Docs v1.5 cleanup",
            "artifact": "docs/dashboard/project-status.json",
            "question": "Which high-friction doc should be shortened or front-mattered next?",
            "next_route": "Use doc-health findings instead of hand-scanning Markdown history.",
        },
    ]


def _top_next_improvements() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "path": "docs/HANDOFF.md",
            "why": "Long historical handoff still competes with the active wiki/dashboard entry.",
            "next_move": "Convert it to a short pointer and archive the remaining history.",
        },
        {
            "rank": 2,
            "path": "artifacts/ARTIFACTS.md",
            "why": "The registry is the active artifact map but still lacks v1.5 front sections.",
            "next_move": "Add What This Is / Current State / Next / Constraints before older artifact detail.",
        },
        {
            "rank": 3,
            "path": "docs/FEATURE_REGISTRY.md",
            "why": "Feature rows are authoritative but hard to scan as a wiki page.",
            "next_move": "Generate per-feature pages from docs/_templates/feature.md.",
        },
    ]


def _open_surfaces() -> list[dict[str, str]]:
    return [
        {
            "label": "Dashboard",
            "command": ".\\open-dashboard.ps1",
            "target": "docs/dashboard/index.html",
            "when_to_use": "Start here for current focus, feature progress, active artifacts, and doc-health findings.",
        },
        {
            "label": "Artifacts",
            "command": ".\\open-artifacts.ps1",
            "target": "artifacts/ARTIFACTS.md",
            "when_to_use": "Use after the dashboard when an artifact needs its registry entry or open command.",
        },
        {
            "label": "Render Path Selector Contract",
            "command": "see docs\\style_intent\\subtitle-render-path-selector-contract.md",
            "target": "docs/style_intent/subtitle-render-path-selector-contract.md",
            "when_to_use": (
                "Use to inspect which selector, family, palette, color, motion, "
                "and line-break fields a later render adapter would receive; "
                "this is L0 static readback, not an actual render pass."
            ),
        },
        {
            "label": "Style Family Palette Proof",
            "command": "see docs\\style_intent\\subtitle-style-family-palette-proof.html",
            "target": "docs/style_intent/subtitle-style-family-palette-proof.html",
            "when_to_use": (
                "Use to inspect the ED-10ad family and palette axes while "
                "body subtitle text color remains stable and palette changes "
                "stay on badge, accent, and backplate surfaces."
            ),
        },
        {
            "label": "Visual Selector Proof",
            "command": "see docs\\style_intent\\subtitle-visual-selector-proof.html",
            "target": "docs/style_intent/subtitle-visual-selector-proof.html",
            "when_to_use": (
                "Use to inspect the ED-10ab semantic presets as badge, accent, "
                "backplate, size, motion, and line-break token differences "
                "while body subtitle text color stays stable."
            ),
        },
        {
            "label": "Preset Selector",
            "command": "see docs\\style_intent\\subtitle-preset-selector.json",
            "target": "docs/style_intent/subtitle-preset-selector.json",
            "when_to_use": (
                "Use before visual selector work to inspect deterministic "
                "speaker, emotion, intensity, utterance role, and readability "
                "token mappings."
            ),
        },
        {
            "label": "Style Intent Registry",
            "command": "see docs\\SUBTITLE_STYLE_INTENT_REGISTRY.md",
            "target": "docs/SUBTITLE_STYLE_INTENT_REGISTRY.md",
            "when_to_use": (
                "Use before future subtitle style work so speaker, emotion, "
                "intensity, utterance role, and readability tags map to presets "
                "instead of repeated tiny numeric review loops."
            ),
        },
        {
            "label": "Tiny Render-Path Probe",
            "command": ".\\open-current-proof.ps1",
            "target": "episodes/.../subtitle_presentation_review_pack.html",
            "when_to_use": (
                "Use as the ED-10z local readback that passes Candidate 2 "
                "through the current diagnostic render path while preserving "
                "Candidate 0 as fallback and Candidate 1/3 as held references."
            ),
        },
        {
            "label": "Multi-font Focused Review Reference",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_multifont_focused_review\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_multifont_focused_review/"
                "subtitle_multifont_focused_review_report.html"
            ),
            "when_to_use": (
                "Use as the accepted ED-10o same-line comparison reference; "
                "it does not mean final baseline or production acceptance."
            ),
        },
        {
            "label": "Known Font Pack",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_known_kirinuki_font_pack_comparison\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_known_kirinuki_font_pack_comparison/"
                "subtitle_known_kirinuki_font_pack_report.html"
            ),
            "when_to_use": (
                "Use as ED-10l/ED-10n readback evidence that the requested "
                "per-user fonts resolve in the regenerated comparison."
            ),
        },
        {
            "label": "BIZ Proof Reference",
            "command": "see artifact registry for archived previous proof paths",
            "target": "artifacts/ARTIFACTS.md",
            "when_to_use": (
                "Use only as the reviewed ED-10k reference that explains why the "
                "system-safe BIZ route stopped; open-current-proof now points to ED-10r."
            ),
        },
        {
            "label": "Font Audit",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_kirinuki_font_audit\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_kirinuki_font_audit/"
                "subtitle_kirinuki_font_audit_report.html"
            ),
            "when_to_use": "Use only to audit the consumed ED-10j contact sheet and candidate mapping.",
        },
        {
            "label": "Gothic Balance",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_kirinuki_gothic_balance_comparison\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_kirinuki_gothic_balance_comparison/"
                "subtitle_kirinuki_gothic_balance_comparison_report.html"
            ),
            "when_to_use": (
                "Use on the machine retaining ignored ED-10i comparison artifacts "
                "to judge gothic glyph body versus outline balance."
            ),
        },
        {
            "label": "Font Candidates",
            "command": ".\\open-font-candidates.ps1",
            "target": "docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md",
            "when_to_use": "Use when ED-10h font universe or local/system font availability is the next question.",
        },
    ]


def _title(text: str, *, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def _doc_status(text: str) -> str:
    if "generated_requires_human_review" in text:
        return "review_ready_diagnostic"
    if "in_progress" in text:
        return "in_progress"
    if "done" in text:
        return "contains_done_history"
    return "reference"


def _boundary_term_count(text: str) -> int:
    lower = text.lower()
    return sum(lower.count(term.lower()) for term in BOUNDARY_TERMS)


def _clean_markdown(value: str) -> str:
    cleaned = value.replace("**", "").replace("`", "")
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"<([^>]+)>", r"\1", cleaned)
    return " ".join(cleaned.split())


def _first_artifact_id(value: str) -> str:
    match = re.search(r"`(clip-[a-z0-9-]+-\d+)`", value)
    if match:
        return match.group(1)
    match = re.search(r"(clip-[a-z0-9-]+-\d+)", value)
    return match.group(1) if match else ""


def _feature_health(feature_id: str, status: str, summary: str) -> str:
    if feature_id == "ED-10g":
        return "accepted_diagnostic_base"
    if feature_id == "ED-10h":
        return "defined_not_generated"
    if feature_id == "ED-10i":
        return "reviewed_not_accepted_as_normal_baseline"
    if feature_id == "ED-10j":
        return "font_audit_consumed_biz_selected"
    if feature_id == "ED-10k":
        return "reviewed_not_accepted_as_normal_baseline"
    if feature_id == "ED-10l":
        return "per_user_font_readback_valid_comparison"
    if feature_id == "ED-10m":
        return "keifont_route_prepared_user_install_completed_by_user"
    if feature_id == "ED-10n":
        return "keifont_overlay_proof_ready_for_human_review"
    if feature_id == "ED-10o":
        return "focused_review_surface_accepted_reference"
    if feature_id == "ED-10p":
        return "keifont_lead_representative_proof_ready"
    if feature_id == "ED-10q":
        return "current_proof_focused_review_restored"
    if feature_id == "ED-10r":
        return "superseded_by_ed10u_multiline_evidence_correction"
    if feature_id == "ED-10t":
        return "keifont_dense_stress_proof_review_ready"
    if feature_id == "ED-10u":
        return "superseded_by_ed10v_dense_stress_pass"
    if feature_id == "ED-10v":
        return "dense_stress_pass_linebreak_policy_recorded"
    if feature_id == "ED-10w":
        return "subtitle_presentation_review_pack_ready"
    if feature_id == "ED-10y":
        return "candidate2_carry_forward_ready"
    if feature_id == "ED-10z":
        return "tiny_render_path_nearer_probe_ready"
    if feature_id == "ED-10aa":
        return "subtitle_style_intent_registry_ready"
    if feature_id == "ED-10ab":
        return "subtitle_preset_selector_ready"
    if feature_id == "ED-10ac":
        return "visual_selector_proof_ready"
    if feature_id == "ED-10ad":
        return "style_family_palette_axis_proof_ready"
    if feature_id == "ED-10ae":
        return "render_path_selector_contract_ready"
    if "blocked" in summary or status == "hold":
        return "blocked"
    return STATUS_HEALTH.get(status, "unknown")


def _feature_progress(feature_id: str, status: str) -> int:
    if feature_id == "ED-10g":
        return 100
    if feature_id == "ED-10h":
        return 15
    if feature_id == "ED-10i":
        return 100
    if feature_id == "ED-10j":
        return 100
    if feature_id == "ED-10k":
        return 100
    if feature_id == "ED-10l":
        return 100
    if feature_id == "ED-10m":
        return 100
    if feature_id == "ED-10n":
        return 95
    if feature_id == "ED-10o":
        return 100
    if feature_id == "ED-10p":
        return 100
    if feature_id == "ED-10q":
        return 100
    if feature_id == "ED-10r":
        return 100
    if feature_id == "ED-10t":
        return 100
    if feature_id == "ED-10u":
        return 100
    if feature_id == "ED-10v":
        return 100
    if feature_id == "ED-10w":
        return 100
    if feature_id == "ED-10y":
        return 100
    if feature_id == "ED-10z":
        return 100
    if feature_id == "ED-10aa":
        return 100
    if feature_id == "ED-10ab":
        return 100
    if feature_id == "ED-10ac":
        return 100
    if feature_id == "ED-10ad":
        return 100
    if feature_id == "ED-10ae":
        return 100
    return STATUS_PROGRESS.get(status, 0)


def _feature_next_action(feature_id: str, status: str, summary: str) -> str:
    if feature_id == "ED-10g":
        return "Keep as historical diagnostic proof; the latest human review sends styling to ED-10i."
    if feature_id == "ED-10h":
        return "Use the font candidate registry to choose a no-download or download-approved sweep route."
    if feature_id == "ED-10i":
        return "Keep the Meiryo proof as reviewed reference; do not treat it as the normal subtitle baseline."
    if feature_id == "ED-10j":
        return "Keep as consumed audit trail; BIZ UDGothic selection was superseded by ED-10k review."
    if feature_id == "ED-10k":
        return "Keep as reviewed rejected reference; do not treat BIZ as the normal-dialogue baseline."
    if feature_id == "ED-10l":
        return "Keep as regenerated real-font comparison; use ED-10n Keifont proof for current visual judgement."
    if feature_id == "ED-10m":
        return "Keep as source/license route record; ED-10n consumed the per-user font readback."
    if feature_id == "ED-10n":
        return "Keep as earlier lead proof reference; ED-10q is now the focused current review surface for the ED-10p artifact."
    if feature_id == "ED-10o":
        return "Keep as accepted focused review-surface reference; it is not final baseline or production acceptance."
    if feature_id == "ED-10p":
        return "Keep as consumed Keifont provisional baseline evidence; ED-10u is now the multiline/dense-stress review route."
    if feature_id == "ED-10q":
        return "Keep as the page-format regression fix; do not treat it as new Keifont font-quality review."
    if feature_id == "ED-10r":
        return "Superseded by ED-10u focused multiline evidence correction; review only corrected cut_008 multiline/dense-stress behavior."
    if feature_id == "ED-10t":
        return "Superseded by ED-10u focused multiline evidence correction; keep font readback as valid."
    if feature_id == "ED-10u":
        return "Consumed by ED-10v user pass; keep as the corrected evidence surface."
    if feature_id == "ED-10v":
        return "Current dense/stress axis is passed; continue only through a new axis such as line-break policy tuning, bounded decoration adjustment, or production limitation-lift."
    if feature_id == "ED-10w":
        return "Use the crop-first review pack to choose Candidate 0 baseline, Candidate 1/2/3 bounded adjustment, or the next tiny render-path diagnostic probe."
    if feature_id == "ED-10y":
        return "Continue from Candidate 2 as provisional bounded-decoration lead; do not repeat the Candidate 0-3 review."
    if feature_id == "ED-10z":
        return "Use the Candidate 2 tiny render-path-nearer probe as local readback; open production limitation-lift or final render-path work only as a separate scope."
    if feature_id == "ED-10aa":
        return "Use the semantic style intent registry for future emotion/speaker/readability preset mapping; ED-10z actual local proof now exists and any limitation-lift/final render-path work should be a separate route."
    if feature_id == "ED-10ab":
        return "Use the deterministic preset selector as readback before future visual style proof; open new style-family, palette, production, rights, publishing, or public-use work as separate routes."
    if feature_id == "ED-10ac":
        return "Use the static visual selector proof for optional open-only observation; keep new style-family, palette, production, rights, publishing, and public-use decisions in separate routes."
    if feature_id == "ED-10ad":
        return "Use the style-family/palette axis proof as no-render static readback before a later render-path probe or separate production/rights/public-use route."
    if feature_id == "ED-10ae":
        return "Use the selector-to-render-path contract as L0 static readback before a later L2 tiny render-path probe; do not infer actual render or production readiness."
    if status == "done":
        return "Keep as reference unless a regression or successor lane appears."
    if status == "proposed":
        return "Promote to approved only after an explicit slice decision."
    if status == "in_progress":
        return "Finish current acceptance/readback and update artifact registry."
    return _truncate(summary, 120)


def _artifact_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2 or cells[0] in {"Field", "---"}:
            continue
        fields[_clean_markdown(cells[0]).lower()] = _clean_markdown(cells[1])
    return fields


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def _md(value: Any) -> str:
    text = str(value).replace("|", "\\|")
    return text.replace("\n", " ")


def _entrypoint_list_html(items: list[dict[str, str]]) -> str:
    entries = "\n".join(
        f"<li><code>{escape(item['path'])}</code>: {escape(item['role'])}</li>"
        for item in items
    )
    return f"<ul>{entries}</ul>"


def _features_table_html(features: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(feature['id'])}</code></td>"
        f"<td>{escape(feature['title'])}</td>"
        f"<td>{escape(feature['status'])}</td>"
        f"<td>{escape(feature['health'])}</td>"
        f"<td>{escape(str(feature['progress_pct']))}%</td>"
        f"<td><code>{escape(feature.get('active_artifact') or '')}</code></td>"
        f"<td>{escape(feature['next_action'])}</td>"
        "</tr>"
        for feature in features
    )
    return (
        "<table><tr><th>id</th><th>title</th><th>status</th><th>health</th>"
        "<th>progress</th><th>active artifact</th><th>next action</th></tr>"
        f"{rows}</table>"
    )


def _artifacts_table_html(artifacts: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(artifact['artifact_id'])}</code></td>"
        f"<td>{escape(artifact.get('title') or '')}</td>"
        f"<td>{escape(artifact.get('storage_class') or '')}</td>"
        f"<td><code>{escape(artifact.get('repo_relative_path') or '')}</code></td>"
        f"<td><code>{escape(artifact.get('open_command') or '')}</code></td>"
        f"<td>{escape(artifact.get('next_action') or '')}</td>"
        "</tr>"
        for artifact in artifacts
    )
    return (
        "<table><tr><th>artifact</th><th>title</th><th>storage</th>"
        "<th>path</th><th>open command</th><th>next action</th></tr>"
        f"{rows}</table>"
    )


def _open_surfaces_table_html(items: list[dict[str, str]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(item['label'])}</td>"
        f"<td><code>{escape(item['command'])}</code></td>"
        f"<td><code>{escape(item['target'])}</code></td>"
        f"<td>{escape(item['when_to_use'])}</td>"
        "</tr>"
        for item in items
    )
    return (
        "<table><tr><th>surface</th><th>command</th><th>target</th>"
        "<th>when to use</th></tr>"
        f"{rows}</table>"
    )


def _review_items_table_html(items: list[dict[str, str]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(item['item'])}</td>"
        f"<td><code>{escape(item['artifact'])}</code></td>"
        f"<td>{escape(item['question'])}</td>"
        f"<td>{escape(item['next_route'])}</td>"
        "</tr>"
        for item in items
    )
    return (
        "<table><tr><th>item</th><th>artifact</th><th>question</th>"
        "<th>next route</th></tr>"
        f"{rows}</table>"
    )


def _findings_table_html(findings: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(item['type'])}</td>"
        f"<td><code>{escape(item['path'])}</code></td>"
        f"<td>{escape(item['detail'])}</td>"
        f"<td>{escape(item['suggested_fix'])}</td>"
        "</tr>"
        for item in findings
    )
    return f"<table><tr><th>type</th><th>path</th><th>detail</th><th>suggested fix</th></tr>{rows}</table>"


def _docs_table_html(docs: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(doc['path'])}</code></td>"
        f"<td>{escape(doc['title'])}</td>"
        f"<td>{escape(str(doc['line_count']))}</td>"
        f"<td>{escape(json.dumps(doc['front_sections'], ensure_ascii=False))}</td>"
        f"<td>{escape(doc['status'])}</td>"
        "</tr>"
        for doc in docs
    )
    return f"<table><tr><th>path</th><th>title</th><th>lines</th><th>front sections</th><th>status</th></tr>{rows}</table>"


def _improvements_table_html(items: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item['rank']))}</td>"
        f"<td><code>{escape(item['path'])}</code></td>"
        f"<td>{escape(item['why'])}</td>"
        f"<td>{escape(item['next_move'])}</td>"
        "</tr>"
        for item in items
    )
    return f"<table><tr><th>rank</th><th>path</th><th>why</th><th>next move</th></tr>{rows}</table>"
