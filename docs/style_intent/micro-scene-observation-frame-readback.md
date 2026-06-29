# ED-10av Micro-Scene Observation Frame Readback

This tracked readback consumes the user's freeform observation after opening the ED-10au specimen. It records that the file opens and reads as a real scene, separates expectation/review-frame warnings from approval, and keeps subtitle/player-UI overlap as an unverified classification issue.

## Source Chain

- artifact_id: `clip-ed10av-micro-scene-observation-frame-readback-001`
- feature_id: `ED-10av`
- status: `micro_scene_observation_frame_readback_ready`
- source_representative_micro_scene_internal_review_specimen_artifact_id: `clip-ed10au-representative-micro-scene-internal-review-specimen-001`
- source_internal_review_observation_readback_artifact_id: `clip-ed10at-internal-review-observation-readback-001`
- source_internal_review_video_candidate_access_sheet_artifact_id: `clip-ed10as-internal-review-access-sheet-fullpath-001`
- source_internal_review_video_candidate_package_artifact_id: `clip-ed10ar-internal-review-video-candidate-package-001`
- active_diagnostic_proof_source_artifact_id: `clip-ed10af-l2-render-path-selector-probe-001`
- source_specimen_status: `representative_micro_scene_internal_review_specimen_ready`
- source_scene_id: `ed10au_real_transcript_micro_scene_sub_004_to_sub_006`
- source_text: `real_transcript_sub_004_to_sub_006`
- source_access_state: `verified_present`
- source_access_evidence_level: `file_exists_and_ffprobe_metadata`

## User Observation Readback

- opened_ed10au_specimen: `true`
- development_target_looks_different: `true`
- evaluation_frame_unclear: `true`
- looks_like_real_scene_not_earlier_diagnostic_cue_memo: `true`
- subtitle_area_appears_large_low_or_possibly_player_ui_overlapped: `true`
- overlap_verified_by_agent: `false`
- screenshot_available_to_agent: `false`

Preserved raw observation points:

- development target looks different
- unclear how to evaluate
- looks like a real scene, not earlier diagnostic cue/memo
- subtitle area appears large / low / possibly overlapped by player UI

## Classification

| axis | classification | basis | approval implication |
|---|---|---|---|
| openability | pass | The user opened the ED-10au representative micro-scene specimen. | access and observation only |
| actual_micro_scene_content | pass | The user observed a real scene rather than the earlier cue/memo diagnostic probe. | actual micro-scene content is visible, not accepted |
| user_expectation_mismatch | warning | The user said the development target looks different. | expectation mismatch requires review-frame clarification |
| review_purpose_clarity | partial_or_fail | The user said it is unclear how to evaluate the artifact. | review frame is not clear enough for acceptance |
| visual_source_framing | warning | The specimen looks like a real 3D scene, which may differ from the expected development target. | source or visual framing may need clarification before v2 |
| subtitle_lower_area_player_ui_overlap | needs_classification_not_verified | The user reported the subtitle area appears large or low and may overlap with player UI, but no screenshot evidence is available in this slice. | do not claim subtitle layout is broken until a screenshot/capture separates rendered layout from media-player chrome |
| artifact_semantics | observation_frame_readback_not_approval | This slice records a freeform observation and routes next axes; it does not request or infer approval. | not production, public, rights, publishing, monetization, or micro-scene acceptance |

## Subtitle / Player UI Risk

- risk_status: `needs_classification_not_verified`
- reported_by_user: `true`
- overlap_verified_by_agent: `false`
- screenshot_available_to_agent: `false`
- layout_broken_claimed: `false`
- player_ui_overlap_confirmed: `false`
- next_route_id: `subtitle-layout-screenshot-capture`
- separation_required: Separate rendered subtitle safe-area/layout from media-player control overlay before making a layout failure claim.

## Review Frame

- status: `partial_or_fail`
- problem: user could open the specimen but did not know how to evaluate it
- expectation_mismatch: `warning`
- specimen_acceptable_but_confusing_route: `review-frame-clarification`
- approval_inferred: `false`

## Next Practical Axis

- recommended_route_id: `review-frame-clarification`
- recommended_route_condition: Use when the specimen is openable and has real scene content, but the user cannot tell what judgement the artifact is asking for.
- alternate_route_id: `subtitle-layout-screenshot-capture`
- alternate_route_condition: Use when the lower subtitle/player UI risk needs evidence; capture or inspect a frame before calling the rendered layout wrong.
- conditional_route_id: `representative-micro-scene-v2`
- conditional_route_condition: Use only if the source scene or visual framing is materially wrong after the review frame is clarified.
- render_gap_route_id: `final-render-path-stage-4`
- render_gap_route_condition: Use only if a concrete render-path gap is found, not for general expectation mismatch.
- stage_7_continuation_allowed_now: `false`
- new_render_allowed_in_this_slice: `false`

## Review Policy / Render Gate

- user_review_requested_now: `false`
- fixed_form_required: `false`
- screenshot_required: `false`
- stage_7_freeform_normalizer_used: `false`
- do_not_ask_user_for_another_review_now: `true`
- source_new_render_run: `true`
- new_render_run: `false`
- new_media_created: `false`
- episodes_tracked: `false`

## Validation

- source_specimen_read: `true`
- source_openability_passed: `true`
- actual_micro_scene_content_classified_pass: `true`
- user_observation_preserved: `true`
- expectation_mismatch_classified_warning: `true`
- review_purpose_clarity_partial_or_fail: `true`
- visual_source_framing_warning_recorded: `true`
- subtitle_player_ui_overlap_needs_classification: `true`
- subtitle_player_ui_overlap_not_verified: `true`
- no_layout_broken_claim: `true`
- no_approval_inferred: `true`
- no_new_render: `true`
- no_new_media: `true`
- no_stage_7_normalizer: `true`
- episodes_tracking_boundary_preserved: `true`
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
- tracked_binary_artifact_created: `false`
- episodes_tracked: `false`
- stage_7_freeform_normalizer_used: `false`
