# ED-10ag Lineage and Observation Surface

This tracked surface keeps the ED-10af L2 selector probe as the active artifact, preserves the restored ED-10af dry-read as predecessor evidence from commit `7e96a28`, and records same-machine observation paths without running a new render.

## Source Artifacts

- active artifact: `clip-ed10af-l2-render-path-selector-probe-001`
- predecessor dry-read artifact: `clip-ed10af-render-contract-consumer-dry-read-001`
- predecessor source commit: `7e96a28`
- predecessor invalidated: `false`
- predecessor superseded_by: `clip-ed10af-l2-render-path-selector-probe-001`
- source render-path contract: `clip-ed10ae-render-path-selector-contract-probe-001`
- render level: `lineage_only_no_new_render`

## Existing Output First

- decision: `preserve_active_ed10af_l2_probe_and_record_lineage_no_rerender`
- reason: The active ED-10af L2 selector probe already contains a local ignored ASS/MP4/manifest render-path readback for neutral, shout, and whisper representative payloads. ED-10ag records the active/predecessor relationship and same-machine observation commands without running ffmpeg again.
- source_probe_local_status: `local_ignored_probe_generated`
- source_probe_new_render_run: `true`
- new_render_run: `false`

## Observation Surface

- same_machine_only: `true`
- may_be_absent_on_other_clone: `true`
- user_review_required: `false`
- dry-read payloads: `6` / `6`
- selected examples: `3`
- local probe status: `local_ignored_probe_generated`

| output | repo-relative path |
|---|---|
| ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |

| output | open command |
|---|---|
| ass | `notepad "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe\subtitle_render_path_selector_probe.ass"` |
| video | `Start-Process "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe\subtitle_render_path_selector_probe.mp4"` |
| manifest | `notepad "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe\subtitle_render_path_selector_probe.local.json"` |
| contact_sheet | `Start-Process "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe\subtitle_render_path_selector_probe_contact_sheet.jpg"` |

| example | role | family | palette | body text |
|---|---|---|---|---|
| neutral_dialogue_intensity_0 | normal_dialogue | current dialogue family | speaker_identity_blue | stable_default_body_text |
| shout_intensity_2 | shout_high_intensity | high-energy emphasis family | high_energy_warm | stable_default_body_text |
| whisper_intensity_1 | low_pressure_whisper | quiet readable dialogue family | quiet_cool | stable_default_body_text |

## Render Gate

- level: `lineage_only_no_new_render`
- existing_output_first_reused: `true`
- new_render_run: `false`
- source_probe_new_render_run: `true`
- tracked_binary_artifact_created: `false`

## Validation

- active_artifact_preserved: `true`
- predecessor_lineage_present: `true`
- observation_paths_present: `true`
- contact_sheet_path_recorded: `true`
- dry_read_all_payloads_consumer_ready: `true`
- source_probe_all_checks_passed: `true`
- selected_examples_covered_by_dry_read: `true`
- stable_body_text_preserved: `true`
- badge_accent_backplate_route_preserved: `true`
- safe_area_line_break_metadata_survived: `true`
- production_public_boundary_closed: `true`
- all_checks_passed: `true`

## Boundary

- human_review_required: `false`
- production_subtitle_design_acceptance: `false`
- production_render_acceptance: `false`
- creative_acceptance: `false`
- rights_status: `pending`
- publishing_acceptance: `false`
- public_use_permission: `false`
- diagnostic_local_ignored_render_reused: `true`
- episodes_tracked: `false`
