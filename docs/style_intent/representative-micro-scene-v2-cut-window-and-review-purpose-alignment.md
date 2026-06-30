# ED-10ba Representative Micro-Scene V2 Cut Window / Review Purpose Alignment

This tracked readback answers ED-10az by producing a bounded local v2 specimen that is easier to judge for cut-window and clipping/cutout review usefulness. The local MP4/ASS/manifest remain ignored same-machine evidence under `episodes/`; this document records what was produced, why the window changed, and which gates remain closed.

## Source Chain

- artifact_id: `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`
- feature_id: `ED-10ba`
- status: `representative_micro_scene_v2_cut_window_review_purpose_alignment_ready`
- source_observation_readback_and_v2_route_decision_artifact_id: `clip-ed10az-observation-readback-and-v2-route-decision-001`
- source_review_frame_clarification_surface_artifact_id: `clip-ed10ax-review-frame-clarification-surface-001`
- source_thank_access_recovery_artifact_id: `clip-ed10ay-thank-ed10au-local-access-recovery-readback-001`
- source_representative_micro_scene_internal_review_specimen_artifact_id: `clip-ed10au-representative-micro-scene-internal-review-specimen-001`

## Why This V2 Exists

ED-10az preserved that the recovered ED-10au MP4 opened and subtitles were not broken, but the user could not tell what to judge. If the target is cut quality, both ends felt too tightly cut; if the target is clipping/cutout usefulness, the ordinary YouTube-like subtitle strategy did not make the review purpose obvious.

- primary_question: `cut-window and clipping/cutout review usefulness`
- not_a_production_candidate: `true`
- not_an_approval_surface: `true`

## V2 Cut Window

- original_ED10au_window: `39.57-48.75s`
- v2_window: `38.50-50.40s`
- duration_seconds: `11.90`
- pre_roll_seconds_before_first_v2_subtitle: `0.656`
- post_roll_seconds_after_last_v2_subtitle: `0.834`
- start_not_exact_subtitle_boundary: `true`
- end_not_exact_subtitle_boundary: `true`
- reason: The v2 window keeps the same exchange but adds modest handles so cut-quality review does not start or end exactly on the primary subtitle boundaries.

| event | source subtitle | source time | local time | text |
|---|---|---:|---:|---|
| ed10ba_sub_024 | sub_024 | 39.156-41.725s | 0.656-3.225s | 団長、ちなみに、他の番長知ってますか？ |
| ed10ba_sub_025 | sub_025 | 41.725-43.360s | 3.225-4.860s | 長(ちょう)？ 長って言った？ |
| ed10ba_sub_026 | sub_026 | 43.360-44.762s | 4.860-6.262s | 倒して回ってるんです！ |
| ed10ba_sub_027 | sub_027 | 44.762-47.498s | 6.262-8.998s | 長…長… 船長のことかな？ |
| ed10ba_sub_028 | sub_028 | 47.498-48.999s | 8.998-10.499s | マリンならあっちにいたよ |
| ed10ba_sub_029 | sub_029 | 48.999-49.566s | 10.499-11.066s | ありがとうございますー！ |

## Subtitle And Audio Treatment

- diagnostic/internal-review subtitles only: `true`
- visible_purpose_label_included: `true`
- purpose_label_text: `INTERNAL CUT-WINDOW REVIEW V2 / diagnostic subtitles, not production design`
- ordinary_youtube_subtitle_mismatch_not_marked_solved: `true`
- source_audio_reused: `true`
- audio_first_failure_axis: `false`

## Access Sheet

- access_state: `verified_present`
- target_exists: `true`
- access_evidence_level: `file_exists_and_ffprobe_metadata`
- evidence_source: `local_render_result_probe`
- launcher_or_open_command: `powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1`
- folder_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment`
- folder_full_path_current_host: `C:\Users\PLANNER007\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment`
- mp4_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment/representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`
- mp4_full_path_current_host: `C:\Users\PLANNER007\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`
- mp4_size_bytes: `4723658`
- ass_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment/representative_micro_scene_v2_cut_window_review_purpose_alignment.ass`
- manifest_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment/representative_micro_scene_v2_cut_window_review_purpose_alignment.local.json`

## Local Render Readback

- local_status: `representative_micro_scene_v2_generated`
- render_command_summary: `ffmpeg -y -ss 38.5 -t 11.9 -i ./episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4 -ss 38.5 -t 11.9 -i ./episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav -map 0:v:0 -map 1:a:0 -vf scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p,subtitles=filename='./episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment/representative_micro_scene_v2_cut_window_review_purpose_alignment.ass' -c:v libx264 -c:a aac -shortest ./episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment/representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`
- duration_seconds: `11.9`
- resolution: `1920x1080`
- video_codec: `h264`
- audio_codec: `aac`
- episodes_tracked: `false`

## Later Freeform Review Frame

- input_mode: `freeform_if_later_requested`
- max_look_for_points: `3`
- user_review_requested_now: `false`

- Does the v2 window feel less tightly cut at both ends than ED-10au?
- Does the specimen make clipping/cutout review usefulness clearer than ED-10au?
- Is the next fix mainly cut-window, subtitle strategy, source-scene selection, or render/layout?

## Validation

- source_ed10az_read: `true`
- ed10az_v2_route_consumed: `true`
- v2_window_has_pre_roll: `true`
- v2_window_has_post_roll: `true`
- start_end_not_exact_subtitle_boundaries: `true`
- script_events_match_expected_source_ids: `true`
- diagnostic_subtitles_only: `true`
- visible_purpose_label_present: `true`
- audio_not_first_failure_axis: `true`
- local_specimen_produced_or_honestly_blocked: `true`
- access_state_verified_or_blocked: `true`
- review_frame_at_most_three_points: `true`
- no_screenshot_capture: `true`
- no_final_render_path_stage_4: `true`
- no_approval_inferred: `true`
- no_stage_7_normalizer: `true`
- tracked_media_boundary_closed: `true`
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
- tracked_binary_artifact_created: `false`
- episodes_tracked: `false`
- screenshot_capture_created: `false`
- subtitle_layout_screenshot_capture_required_now: `false`
- final_render_path_stage_4_required_now: `false`
- timing_audio_first_route: `false`
- stage_7_freeform_normalizer_used: `false`
