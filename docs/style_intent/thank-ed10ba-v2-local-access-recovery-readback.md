# ED-10bb Thank ED-10ba V2 Local Access Recovery Readback

This tracked readback preserves the access reality for the requested Thank-terminal recovery of ED-10ba. The request targeted `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`, but this run executed from `C:\Users\PLANNER007\ClipPipeGen`. The expected Thank repository root was not visible from this session, so the Thank-host MP4/ASS/local manifest and source inputs could not be verified or regenerated here.

## Identity

- artifact_id: `clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001`
- feature_id: `ED-10bb`
- status: `thank_ed10ba_v2_local_access_recovery_blocked_current_session_not_on_thank`
- source artifact: `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`
- classification: `thank_repo_root_not_visible_from_current_session`

## Access Reality

| Checked surface | Result | Meaning |
|---|---|---|
| Current repo root | `C:\Users\PLANNER007\ClipPipeGen` | This was not the requested Thank root. |
| Expected Thank root | not visible | The check cannot honestly classify Thank ignored media as present or absent. |
| ED-10ba tracked files | present | Git state for the v2 readback and launcher is available after pull. |
| Thank MP4/ASS/local manifest | not accessible from this session | No rerender was attempted because it would affect the wrong host. |
| PLANNER007 MP4/ASS/local manifest | present | Reference only; not Thank-host recovery evidence. |

This is deliberately not classified as `current_host_ignored_media_absent`: the expected Thank repo root itself is not visible from the current PLANNER007 session.

## Thank Paths To Check Next

- MP4: `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`
- ASS: `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.ass`
- local manifest: `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.local.json`

Required source inputs on Thank, if regeneration is needed:

- `episodes\jp_pilot01_hololive_bancho_20260525\materials\src_video_jp_pilot01\source_video.mp4`
- `episodes\jp_pilot01_hololive_bancho_20260525\materials\src_audio_jp_pilot01\source.wav`
- `episodes\jp_pilot01_hololive_bancho_20260525\transcript.json`
- `episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json`

## PLANNER007 Reference Only

The ED-10ba v2 specimen is present on PLANNER007 at:

`C:\Users\PLANNER007\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`

Reference metadata: size `4723658` bytes, duration `11.9s`, H.264/AAC, 1920x1080, 30fps. The ASS is `1529` bytes and the local manifest is `13681` bytes. This proves the ED-10ba path is reproducible and present on PLANNER007 only; it is not evidence that the Thank terminal already has the ignored media.

## Builder Entrypoint

The bounded writer exists in `src/integrations/render/subtitle_preset_selector.py`:

`write_representative_micro_scene_v2_cut_window_review_purpose_alignment_local_artifacts`

If and only if the next terminal is actually the Thank repo root and all required source inputs are present, run:

```powershell
uvx python -c "from pathlib import Path; from src.integrations.render import subtitle_preset_selector as s; s.write_representative_micro_scene_v2_cut_window_review_purpose_alignment_local_artifacts(base_dir=Path.cwd(), ffmpeg_path='ffmpeg', ffprobe_path='ffprobe')"
```

## Boundary Readback

- new_render_run: `false`
- new_media_created: `false`
- wrong_host_regeneration: `false`
- episodes_tracked: `false`
- screenshot_capture_created: `false`
- final_render_path_stage_4: `false`
- stage_7_freeform_normalizer_used: `false`
- production_render_acceptance: `false`
- public_use_permission: `false`
- rights_status: `pending`
- micro_scene_accepted: `false`
- user_review_requested_now: `false`

## Validation

- repo_root_verified_current_session: `true`
- origin_main_parity_before_readback: `0 0`
- tracked_ed10ba_files_present: `true`
- expected_thank_repo_root_visible: `false`
- builder_entrypoint_present: `true`
- regeneration_attempted: `false`
- wrong_host_regeneration_avoided: `true`
- user_not_asked_to_search_again: `true`
- all_checks_passed_for_current_session_readback: `true`
