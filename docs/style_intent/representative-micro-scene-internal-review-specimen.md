# ED-10au Representative Micro-Scene Internal Review Specimen

This tracked readback creates the next bounded internal-review specimen after ED-10at. It uses actual Japanese transcript subtitle content instead of cue labels, renders a short ignored local MP4 for access verification, and keeps all production, rights, publishing, monetization, and public-use gates closed.

## Source Chain

- artifact_id: `clip-ed10au-representative-micro-scene-internal-review-specimen-001`
- feature_id: `ED-10au`
- status: `representative_micro_scene_internal_review_specimen_ready`
- source_internal_review_observation_readback_artifact_id: `clip-ed10at-internal-review-observation-readback-001`
- source_internal_review_video_candidate_access_sheet_artifact_id: `clip-ed10as-internal-review-access-sheet-fullpath-001`
- source_internal_review_video_candidate_package_artifact_id: `clip-ed10ar-internal-review-video-candidate-package-001`
- active_diagnostic_proof_source_artifact_id: `clip-ed10af-l2-render-path-selector-probe-001`
- source_text: `real_transcript_sub_004_to_sub_006`

## Micro-Scene

- scene_id: `ed10au_real_transcript_micro_scene_sub_004_to_sub_006`
- duration_seconds: `9.18`
- actual_script_content_present: `true`
- cue_labels_used_as_main_content: `false`
- scene_continuity_note: The three real transcript subtitles form a tiny exchange about other bancho, defeating them, and being pointed toward Marine.

| event | local time | subtitle text |
|---|---:|---|
| ed10au_sub_004 | 0.00-3.57s | 団長、ちなみに、他の番長知ってますか？ 長？ 長って言った？ |
| ed10au_sub_005 | 4.14-5.75s | 倒して回ってるんです！ |
| ed10au_sub_006 | 6.93-9.18s | 長…長… 船長のことかな？ マリンならあっちにいたよ |

## Access Sheet

- access_state: `verified_present`
- target_exists: `true`
- access_evidence_level: `file_exists_and_ffprobe_metadata`
- evidence_source: `local_render_result_probe`
- launcher_or_open_command: `powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_internal_review_specimen.ps1`
- folder_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen`
- folder_full_path_current_host: `C:\Users\PLANNER007\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_internal_review_specimen`
- mp4_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.mp4`
- mp4_full_path_current_host: `C:\Users\PLANNER007\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_internal_review_specimen\representative_micro_scene_internal_review_specimen.mp4`
- mp4_size_bytes: `3538973`
- ass_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.ass`
- manifest_repo_relative_path: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.local.json`

## Review Guidance

- answer_style: `freeform`
- max_look_for_points: `3`
- user_review_requested_now: `false`

- Does it read as an actual tiny scene rather than a cue memo?
- Are subtitle/script/audio/layout coherent enough for internal review?
- Is the next fix mainly script, timing/audio, visual layout, or render path?

## Local Render Readback

- local_status: `representative_micro_scene_generated`
- render_command_summary: `ffmpeg -y -ss 39.57 -t 9.18 -i ./episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4 -ss 39.57 -t 9.18 -i ./episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav -map 0:v:0 -map 1:a:0 -vf scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p,subtitles=filename='./episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.ass' -c:v libx264 -c:a aac -shortest ./episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.mp4`
- duration_seconds: `9.18`
- resolution: `1920x1080`
- video_codec: `h264`
- audio_codec: `aac`

## Validation

- ed10at_source_read: `true`
- representative_micro_scene_created: `true`
- actual_script_content_exists: `true`
- cue_labels_not_main_content: `true`
- review_guidance_at_most_three_points: `true`
- access_state_verified_or_classified: `true`
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
- tracked_binary_artifact_created: `false`
- episodes_tracked: `false`
- stage_7_freeform_normalizer_used: `false`
- user_observation_converted_to_approval: `false`
