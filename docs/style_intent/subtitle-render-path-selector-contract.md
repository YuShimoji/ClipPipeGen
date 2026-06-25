# ED-10ae Render Path Selector Contract Probe

This tracked contract connects the ED-10ab selector, ED-10ac visual selector proof, and ED-10ad family / palette proof to the fields a later render adapter would receive. It is static readback only.

## Render Gate

- level: `L0 No Render`
- new_render_run: `false`
- next_render_level: `L2 tiny render path probe milestone`
- no video, audio, frame, ASS, or episode artifact is generated here.

## Contract Fields

- semantic: `semantic_preset_id`, `preset_key`, `speaker_id`, `speaker_role`, `emotion`, `intensity`, `utterance_role`, `readability_priority`
- style: `family_id`, `palette_route`, `font_family_role`, `font_size_scale`, `outline_shadow_strength`
- color surfaces: `badge_color_token`, `accent_color_token`, `backplate_box_token`, `body_text_color_token`, `body_text_color_changed`
- motion / line break: `motion_primitive`, `safe_area_line_break_behavior`

## Preset Contract Rows

| semantic preset | preset key | family | palette | body text | line-break |
|---|---|---|---|---|---|
| `neutral_dialogue_intensity_0` | `character.dialogue.neutral.i0.high` | `dialogue_current_keifont_family` | `speaker_identity_blue` | `stable_default_body_text` | `high_readability` |
| `shout_intensity_2` | `character.dialogue.shout.i2.high` | `emphasis_energy_family` | `high_energy_warm` | `stable_default_body_text` | `prefer_shorter_lines_max_two` |
| `whisper_intensity_1` | `character.dialogue.whisper.i1.normal` | `quiet_soft_readability_family` | `quiet_cool` | `stable_default_body_text` | `normal` |
| `ominous_intensity_2` | `character.inner_voice.ominous.i2.maximum` | `ominous_inner_voice_family` | `ominous_dark` | `stable_default_body_text` | `maximum_readability` |
| `narration_intensity_0` | `narrator.narration.narration.i0.high` | `narration_family` | `narration_neutral_green` | `stable_default_body_text` | `high_readability` |
| `system_note_intensity_0` | `system.warning.system_note.i0.maximum` | `system_note_family` | `system_neutral` | `stable_default_body_text` | `maximum_readability` |

## Readiness Separation

- subtitle_style_readiness: `selector_static_proof_render_path_contract_ready`
- video_render_readiness: `not_run_no_render_pass_implied`
- production_readiness: `not_accepted`
- rights_public_use_readiness: `not_accepted`

## Boundary

This contract preserves `stable_default_body_text`, badge/accent-first character color, and all production / rights / public-use boundaries. A later L2 render probe is a separate milestone and is not triggered by this document.
