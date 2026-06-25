# ED-10af Render Contract Consumer Dry-Read

This tracked dry-read consumes the ED-10ae render-path selector contract and normalizes the adapter-facing payload a later render adapter would receive. It is static readback only.

## Render Gate

- level: `L0 No Render`
- new_render_run: `false`
- consumer_dry_read_only: `true`
- next_render_level: `L2 tiny render path probe milestone`
- no video, audio, frame, ASS, render, or episode artifact is generated here.

## Consumer Payload Fields

- semantic: `semantic_preset_id`, `preset_key`, `speaker_id`, `speaker_role`, `emotion`, `intensity`, `utterance_role`, `readability_priority`
- style: `family_id`, `palette_route`, `font_family_role`, `font_size_scale`, `outline_shadow_strength`
- color surfaces: `badge_color_token`, `accent_color_token`, `backplate_box_token`, `body_text_color_policy_reference`, `body_text_color_token`, `body_text_color_changed`
- motion / line break: `motion_primitive`, `safe_area_line_break_behavior`
- boundaries: `render_boundary`, `production_public_boundary`

## Payload Rows

| semantic preset | family | palette | badge | accent | line-break |
|---|---|---|---|---|---|
| `neutral_dialogue_intensity_0` | `dialogue_current_keifont_family` | `speaker_identity_blue` | `speaker_bancho_badge_default` | `speaker_bancho_speaker_default_subtle_accent` | `high_readability` |
| `shout_intensity_2` | `emphasis_energy_family` | `high_energy_warm` | `speaker_bancho_badge_default` | `speaker_bancho_high_energy_accent` | `prefer_shorter_lines_max_two` |
| `whisper_intensity_1` | `quiet_soft_readability_family` | `quiet_cool` | `speaker_bancho_badge_default` | `speaker_bancho_quiet_accent` | `normal` |
| `ominous_intensity_2` | `ominous_inner_voice_family` | `ominous_dark` | `speaker_default_badge` | `dark_accent` | `maximum_readability` |
| `narration_intensity_0` | `narration_family` | `narration_neutral_green` | `narrator_badge_optional` | `narration_neutral_accent` | `high_readability` |
| `system_note_intensity_0` | `system_note_family` | `system_neutral` | `system_badge` | `system_accent` | `maximum_readability` |

## Static Drift Checks

- all_payloads_consumer_ready: `true`
- missing_required_fields: `0`
- type_mismatches: `0`
- body_text_color_policy_drift: `false`
- render_boundary_leakage: `false`
- production_public_boundary_leakage: `false`

## Readiness Separation

- subtitle_style_readiness: `selector_static_proof_render_path_contract_consumer_dry_read_ready`
- video_render_readiness: `not_run_no_render_pass_implied`
- production_readiness: `not_accepted`
- rights_public_use_readiness: `not_accepted`

## Boundary

This dry-read preserves `stable_default_body_text`, badge/accent/backplate-first color surfaces, family and palette routes, and all production / rights / public-use boundaries. A later L2 render probe is a separate milestone and is not triggered by this document.
