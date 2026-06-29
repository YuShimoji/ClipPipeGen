# ED-10ax Review-Frame Clarification Surface

This tracked surface turns ED-10aw's plan into a concrete readback frame for the ED-10au/ED-10av micro-scene specimen. It clarifies what a later reviewer should judge, what the surface is not asking, and which next axis to use without creating new media or asking the user now.

## Source Chain

- artifact_id: `clip-ed10ax-review-frame-clarification-surface-001`
- feature_id: `ED-10ax`
- status: `review_frame_clarification_surface_ready`
- source_grill_me_adoption_review_frame_clarification_plan_artifact_id: `clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001`
- source_micro_scene_observation_frame_readback_artifact_id: `clip-ed10av-micro-scene-observation-frame-readback-001`
- source_representative_micro_scene_internal_review_specimen_artifact_id: `clip-ed10au-representative-micro-scene-internal-review-specimen-001`
- source_internal_review_observation_readback_artifact_id: `clip-ed10at-internal-review-observation-readback-001`
- source_internal_review_video_candidate_access_sheet_artifact_id: `clip-ed10as-internal-review-access-sheet-fullpath-001`
- source_internal_review_video_candidate_package_artifact_id: `clip-ed10ar-internal-review-video-candidate-package-001`

## What To Judge

Primary friction: The specimen opened and looked like real scene content, but the reviewer could not tell what evaluation was expected.

- Whether the ED-10au specimen is understandable as a bounded micro-scene review surface.
- Which axis best explains the current friction: review framing, subtitle layout, source scene, timing/audio, or render path.
- Which one next axis should be used before any rerender, screenshot capture, v2 specimen, or render-path stage-4 work.

## What This Is Not Asking

- production/public/rights/publishing/monetization approval
- production subtitle design acceptance
- micro-scene acceptance
- fixed form or yes/no table completion
- new render or replay
- new media or tracked episodes artifact
- screenshot capture unless lower subtitle/player-UI risk is being classified
- representative micro-scene v2 unless source/scene mismatch is confirmed
- stage-7 freeform normalizer

## ED-10av Observation Interpretation

| observation | classification | meaning | approval implication |
|---|---|---|---|
| user opened ED-10au | access_observed | The specimen can be opened for review framing. | not approval |
| looks like a real scene, not earlier diagnostic cue/memo | actual_micro_scene_content_visible | The specimen is no longer the cue-label memo probe; it has real scene content to frame. | visible content is not acceptance |
| development target looks different | expectation_or_source_framing_warning | Clarify the review target before deciding whether a v2 specimen is justified. | not source/scene failure by itself |
| unclear how to evaluate | review_frame_clarity_failure | ED-10ax is the first default route. | not a pass/fail judgement on the specimen |
| subtitle area appears large / low / possibly overlapped by player UI | reported_unverified_layout_risk | Only screenshot/capture work can separate rendered subtitle placement from media-player chrome. | do not claim layout broken |

Preserved ED-10av observation points:

- development target looks different
- unclear how to evaluate
- looks like a real scene, not earlier diagnostic cue/memo
- subtitle area appears large / low / possibly overlapped by player UI

## Later User-Facing Review Frame

- status: `ready_for_later_use_not_asked_now`
- input_mode: `freeform_if_later_requested`
- max_look_for_points: `3`
- user_review_requested_now: `false`
- fixed_form_required: `false`
- yes_no_required: `false`
- review_prompt: Please describe what feels unclear or useful in this micro-scene review surface. A short freeform note is enough.

Future look-for points:

- Does the specimen's purpose make sense as a micro-scene review?
- Is the main issue review framing, subtitle layout, source scene, timing/audio, or render path?
- What one next axis would reduce review friction most?

## Route Decision Rules

| route | default order | enabled now | condition |
|---|---|---:|---|
| review-frame-clarification | first | true | The specimen opens and contains real scene content, but the reviewer cannot tell what judgement the surface is asking for. |
| subtitle-layout-screenshot-capture | conditional | false | Use only to classify whether the reported lower subtitle area is a rendered layout problem or media-player UI overlap. |
| representative-micro-scene-v2 | conditional | false | Use only after the source scene or visual framing is confirmed materially wrong. |
| final-render-path-stage-4 | conditional | false | Use only when a concrete render-path gap is found; do not use it for general expectation mismatch. |

## Grill-me Check

- bounded_use: `local_helper_not_repo_policy`
- plan_grill_verdict: `PASS`
- next_agent_prompt_allowed: `false`
- nested_prompt_allowed: `false`
- diff_grill_required_before_commit: `true`
- report_grill_required_before_final_report: `true`

## Review Policy / Render Gate

- user_review_requested_now: `false`
- fixed_form_required: `false`
- yes_no_required: `false`
- screenshot_required_now: `false`
- stage_7_freeform_normalizer_used: `false`
- new_render_run: `false`
- new_media_created: `false`
- episodes_tracked: `false`

## Validation

- source_ed10aw_read: `true`
- source_ed10av_read: `true`
- review_frame_clarification_added: `true`
- future_look_for_points_max_3: `true`
- no_fixed_form: `true`
- no_approval_inferred: `true`
- no_new_render: `true`
- no_new_media: `true`
- no_tracked_episodes: `true`
- grill_me_local_helper_not_policy: `true`
- route_default_review_frame_first: `true`
- screenshot_capture_conditional: `true`
- representative_v2_conditional: `true`
- final_render_path_stage4_conditional: `true`
- stage_7_not_used: `true`
- all_checks_passed: `true`

## Boundary

- production_subtitle_design_acceptance: `false`
- production_render_acceptance: `false`
- creative_acceptance: `false`
- rights_status: `pending`
- publishing_acceptance: `false`
- public_use_permission: `false`
- monetization_acceptance: `false`
- production_candidate: `false`
- production_usage_allowed: `false`
- micro_scene_accepted: `false`
- user_observation_converted_to_approval: `false`
- layout_broken_claimed: `false`
- player_ui_overlap_confirmed: `false`
- new_render_run: `false`
- new_media_created: `false`
- episodes_tracked: `false`
- stage_7_freeform_normalizer_used: `false`
- fixed_form_required: `false`
- yes_no_required: `false`
- grill_me_project_resource_authority: `false`
- grill_me_skill_files_staged: `false`
- next_agent_prompt_allowed: `false`
- agent_report_nested_prompt_allowed: `false`
