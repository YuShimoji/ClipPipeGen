# ED-10bb Thank ED-10ba V2 Local Access Recovery Readback

This tracked readback records actual Thank-terminal access recovery for the
ED-10ba v2 specimen. The run executed from the requested repo root
`C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`, found the ignored
v2 MP4/ASS/local manifest absent at first, verified all required source inputs,
regenerated only through the bounded ED-10ba v2 writer, and verified the final
MP4 with ffprobe.

## Identity

- artifact_id: `clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001`
- feature_id: `ED-10bb`
- status: `thank_ed10ba_v2_local_access_recovery_verified_present`
- source artifact: `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`
- classification: `current_host_ignored_media_absent_then_regenerated`
- final access_state: `verified_present`

## Access Reality

| Checked surface | Result | Meaning |
|---|---|---|
| Thank repo root | present | The run happened from the requested root, not PLANNER007. |
| ED-10ba tracked files | present | The v2 readback, Markdown, launcher, dashboard JSON, current handoff, and runtime state exist after pull. |
| Initial Thank MP4/ASS/local manifest | absent | This was current-host ignored media absence, not a Git tracked-file failure. |
| Source video/audio/transcript/edit_pack | present | Bounded regeneration was allowed without asking the user to search manually. |
| Final Thank MP4/ASS/local manifest | present | Access recovery is complete for this host. |
| Git media boundary | clean | `git ls-files episodes` remains empty. |

## Current Thank Paths

- MP4: `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`
- ASS: `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.ass`
- local manifest: `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment\representative_micro_scene_v2_cut_window_review_purpose_alignment.local.json`

Final readback:

- MP4 size: `4627079` bytes
- ASS size: `1529` bytes
- local manifest size: `13824` bytes
- duration: `11.9s`
- video: H.264, `1920x1080`, `30/1` fps
- audio: AAC, `16000` Hz, mono

## Regeneration

The initial media state was `current_host_ignored_media_absent`. The following
source inputs were present:

- `episodes\jp_pilot01_hololive_bancho_20260525\materials\src_video_jp_pilot01\source_video.mp4`
- `episodes\jp_pilot01_hololive_bancho_20260525\materials\src_audio_jp_pilot01\source.wav`
- `episodes\jp_pilot01_hololive_bancho_20260525\transcript.json`
- `episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json`

The bounded writer exists in
`src/integrations/render/subtitle_preset_selector.py`:

`write_representative_micro_scene_v2_cut_window_review_purpose_alignment_local_artifacts`

Command used:

```powershell
uvx python -c "from pathlib import Path; from src.integrations.render import subtitle_preset_selector as s; s.write_representative_micro_scene_v2_cut_window_review_purpose_alignment_local_artifacts(base_dir=Path.cwd(), ffmpeg_path='ffmpeg', ffprobe_path='ffprobe')"
```

## Open Command

Use this only when a later supervisor asks for freeform v2 observation:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1
```

## Boundary Readback

- new_render_run: `true`
- new_media_created: `true`
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
- tracked_ed10ba_files_present: `true`
- initial_thank_outputs_present: `false`
- thank_source_inputs_verified: `true`
- builder_entrypoint_present: `true`
- regeneration_attempted: `true`
- regeneration_completed: `true`
- final_access_state: `verified_present`
- ffprobe_completed: `true`
- user_not_asked_to_search_again: `true`
- all_checks_passed_for_current_session_readback: `true`
