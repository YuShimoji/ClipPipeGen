# ED-10bc Thank V2 Open Command Repair Readback

This tracked readback records the Thank-terminal opener failure for the ED-10ba
v2 specimen and the launcher repair. The media itself was verified present:
MP4, ASS, and local manifest exist under ignored `episodes/`, and ffprobe
confirms the MP4 as `11.9s`, H.264/AAC, 1920x1080, 30fps. The failure is
classified as `file_verified_but_user_visible_open_failed`, not as render or
asset loss.

## Identity

- artifact_id: `clip-ed10bc-thank-v2-open-command-repair-readback-001`
- feature_id: `ED-10bc`
- status: `thank_v2_open_command_repair_ready`
- source access artifact: `clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001`
- source v2 artifact: `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`
- classification: `file_verified_but_user_visible_open_failed`

## User Visible Failure

The user ran:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1
```

The video did not open visibly for the user. The pre-repair launcher was then
run from this terminal and returned exit code `0`, stdout with only the
`Opening ED-10ba representative micro-scene v2 MP4:` line and the MP4 path, and
empty stderr. That proves the script reached `Invoke-Item`; it does not prove
the player was visible to the user.

## Repo And Media State

| Surface | Result | Meaning |
|---|---|---|
| repo root | `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen` | The repair happened on the requested Thank terminal path. |
| origin parity before local update | `0 0` | Work started from `main` equal to `origin/main`. |
| MP4 | present, `4627079` bytes | The v2 specimen file is available locally. |
| ASS | present, `1529` bytes | Subtitle source for the v2 specimen is available locally. |
| local manifest | present, `13824` bytes | The local render/access metadata is available locally. |
| ffprobe | `11.9s`, H.264/AAC, 1920x1080, 30fps | Media is readable; this is not a render failure. |
| Git media boundary | `episodes_tracked=false` | Local media remains ignored same-machine evidence. |

## Launcher Repair

The launcher now prints the resolved repo root, MP4 path, existence, size,
attempt method, attempt status, classification, and fallback commands. It no
longer states that visible playback succeeded.

Default behavior uses:

```powershell
Start-Process -FilePath <mp4> -PassThru
```

The repaired default smoke returned exit code `0`, process name `vlc`,
`open_attempt_status=start_process_attempted_not_observed`, and
`classification=file_verified_but_user_visible_open_not_confirmed`. A separate
`-NoInvoke` diagnostic smoke returned exit code `0` with
`classification=path_print_only`.

Fallbacks:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -SelectVideo
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -OpenFolder
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -OpenManifest
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -OpenAss
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -PrintPath
powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -NoInvoke
```

## Boundary Readback

- new_v3_created: `false`
- new_render_run: `false`
- new_media_created: `false`
- screenshot_capture_created: `false`
- final_render_path_stage_4: `false`
- timing_audio_first_route: `false`
- stage_7_freeform_normalizer_used: `false`
- tracked_binary_artifact_created: `false`
- episodes_tracked: `false`
- production_render_acceptance: `false`
- public_use_permission: `false`
- rights_status: `pending`
- micro_scene_accepted: `false`
- user_review_requested_now: `false`

## Validation

- repo_root_verified_current_session: `true`
- local_media_verified_present: `true`
- ffprobe_completed: `true`
- pre_repair_launcher_run_captured: `true`
- post_repair_no_invoke_smoke_completed: `true`
- post_repair_default_smoke_completed: `true`
- json_parse_completed: `true`
- dashboard_json_parse_completed: `true`
- targeted_tests_completed: `true`
- git_diff_check_completed: `true`
- episodes_tracked: `false`
- all_checks_passed_for_current_session_readback: `true`
