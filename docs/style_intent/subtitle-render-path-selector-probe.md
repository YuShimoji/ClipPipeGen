# ED-10af L2 Render Path Selector Probe

This tracked probe consumes the ED-10ae selector-to-render contract and selects three representative semantic presets for a tiny FFmpeg/libass diagnostic path: normal dialogue, shout/high-intensity, and low-pressure whisper. The local media outputs are ignored same-machine evidence; this document is the tracked readback.

## Render Gate

- level: `L2 tiny render path selector probe`
- new_render_run: `true`
- diagnostic_only: `true`
- tracked_binary_artifact_created: `false`
- production_render_acceptance: `false`
- public_use_permission: `false`

## Local Ignored Outputs

- status: `local_ignored_probe_generated`
- ASS: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass`
- video: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4`
- manifest: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json`

## Probe Rows

| semantic preset | ASS cue text | family | palette | body text | line-break |
|---|---|---|---|---|---|
| `neutral_dialogue_intensity_0` | `NORMAL DIALOGUE CUE` | `dialogue_current_keifont_family` | `speaker_identity_blue` | `stable_default_body_text` | `high_readability` |
| `shout_intensity_2` | `SHOUT HIGH INTENSITY` | `emphasis_energy_family` | `high_energy_warm` | `stable_default_body_text` | `prefer_shorter_lines_max_two` |
| `whisper_intensity_1` | `LOW PRESSURE\NWHISPER CUE` | `quiet_soft_readability_family` | `quiet_cool` | `stable_default_body_text` | `normal` |

## Validation

- source_contract_referenced: `true`
- selected_example_count: `3`
- stable_body_text_preserved: `true`
- badge_accent_backplate_route_preserved: `true`
- safe_area_line_break_metadata_survived: `true`
- production_public_boundary_closed: `true`
- tracked_binary_artifact_created: `false`

## Boundary

The probe preserves `stable_default_body_text`; semantic variation stays badge/accent/backplate-first. The generated ASS/MP4/manifest paths stay under ignored `episodes/` and do not approve production subtitle design, production render, creative use, rights, publishing, or public use.
