# ED-10am Production Limitation-Lift Stage 1

This tracked packet converts the ED-10al diagnostic final-path rehearsal into production limitation-lift preparation. It is not production subtitle design acceptance, production render acceptance, creative acceptance, rights clearance, publishing acceptance, or public-use permission.

- artifact_id: `clip-ed10am-production-limitation-lift-stage-1-001`
- status: `production_limitation_lift_stage_1_packet_ready`

## Primary Diagnostic Evidence

- primary_diagnostic_rehearsal_artifact_id: `clip-ed10al-final-render-path-stage-3-rehearsal-001`
- stage_2_source_artifact_id: `clip-ed10ak-final-render-path-stage-2-replayability-001`
- active_diagnostic_proof_source_artifact_id: `clip-ed10af-l2-render-path-selector-probe-001`
- selected_render_path: `ffmpeg/libass diagnostic subtitle overlay path`
- rehearsal_status: `diagnostic_rehearsal_completed`
- command_family: `ffmpeg with libass subtitles filter plus ffprobe readback`
- why_diagnostic_only: The rehearsal uses ignored local source media and writes ignored local diagnostic proof only. It does not approve production subtitle design, production render, creative use, rights, publishing, or public use.

Generated ignored outputs:

| output | same-machine path |
|---|---|
| ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |

Recorded ignored outputs:

| output | same-machine path |
|---|---|
| ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |

## Output Metadata

- duration_seconds: `4.2`
- video_codec: `h264`
- audio_codec: `aac`
- width: `1920`
- height: `1080`
- resolution: `1920x1080`
- fps: `30.0`
- frame_rate: `30/1`
- stream_count: `2`

## Survival Readback

- ass_subtitle_style_tokens_survived: `true`
- stable_body_text_policy_survived: `true`
- badge_accent_backplate_route_survived: `true`
- line_break_safe_area_metadata_survived: `true`
- production_public_gates_still_closed: `true`

## Gate Matrix

| gate | current status | source evidence | missing evidence | next decision owner | agent can progress without user judgement | unsafe overclaiming |
|---|---|---|---|---|---|---|
| diagnostic_render_path_rehearsal_evidence | available_diagnostic_only | ED-10al artifact: clip-ed10al-final-render-path-stage-3-rehearsal-001<br>selected path: ffmpeg/libass diagnostic subtitle overlay path<br>generated ignored outputs: ass, manifest, video<br>metadata: 4.2s / 1920x1080 / h264 / aac<br>style tokens survived: True<br>stable body text survived: True<br>badge/accent/backplate route survived: True<br>line-break/safe-area metadata survived: True | Production subtitle design acceptance.<br>Production render acceptance.<br>Creative, rights, publishing, and public-use decisions. | Agent | true | Treating ED-10al diagnostic output as production render approval.<br>Treating style-token survival as final production subtitle design acceptance. |
| production_subtitle_design_acceptance | not_accepted | ED-10al records style-token, stable body text, badge/accent/backplate, and safe-area survival.<br>Prior user observation allows forward progress without reopening display/layout polish. | Explicit human acceptance that the subtitle design is production-ready.<br>Any required representative production-sequence typography review. | User | false | Claiming production subtitle design acceptance from diagnostic survival readback.<br>Reopening old layout polish as if ED-10am required it. |
| production_render_acceptance | not_accepted | ED-10al generated a 4.2s ignored diagnostic MP4 and local manifest.<br>FFmpeg/libass command family and output metadata are recorded. | Accepted final production render output.<br>Final production render command, manifest, and human review result. | User | false | Describing the ignored diagnostic MP4 as a production render.<br>Using output metadata alone as render acceptance. |
| creative_acceptance | not_accepted | The diagnostic presentation path is acceptable enough to move forward.<br>No old candidate or cut review axis is reopened by ED-10am. | Explicit creative approval for production use.<br>Any final editorial or representative-sequence acceptance packet. | User | false | Treating forward-progress preference as creative acceptance.<br>Treating diagnostic rehearsal completion as editorial approval. |
| rights_status | pending | ED-10al and ED-10am make no rights clearance claim.<br>Ignored proof outputs stay same-machine diagnostic evidence. | Rights clearance or owner decision for source material and distribution context.<br>Publication-specific material-use clearance. | Rights | false | Inferring rights clearance from local diagnostic generation.<br>Treating ignored proof media as public-use permission. |
| publishing_acceptance | not_accepted | No upload, visibility, platform metadata, or scheduling action occurs in ED-10al/ED-10am. | Human publication decision.<br>Platform/account-specific publishing acceptance and final metadata decision. | Publication | false | Preparing upload/public release actions from diagnostic evidence.<br>Claiming publishing readiness before rights and production gates are explicit. |
| public_use_permission | not_allowed | Production design, render, creative, rights, and publishing gates remain false or pending. | All upstream acceptances required for public use.<br>Explicit public-use permission. | Publication | false | Granting public-use permission from local diagnostic proof.<br>Combining partial gate evidence into public-ready status. |
| tracked_media_boundary | closed_no_tracked_media | ED-10am creates tracked JSON/Markdown only.<br>ED-10al recorded `tracked_binary_artifact_created=false` and `episodes_tracked=false`. | none | Agent | true | Adding ignored ASS/MP4/manifest/contact-sheet outputs to Git.<br>Moving same-machine media into tracked docs as binary artifacts. |
| same_machine_ignored_evidence_boundary | available_same_machine_only | ED-10al generated ignored ASS/MP4/manifest outputs on this machine.<br>The contact-sheet path is recorded but not generated by the stage-3 helper. | A production artifact store or portable media package, if later required.<br>Fresh-clone local media availability. | Agent | true | Claiming same-machine ignored outputs are portable tracked artifacts.<br>Treating fresh-clone absence as a failure of this tracked packet. |

## ED-10al Does Not Prove

- final production subtitle design acceptance
- production render acceptance
- creative acceptance
- rights clearance
- publishing readiness
- public-use permission

## Next Executable Route

- route_id: `production-limitation-lift-stage-2-decision-packet`
- alternate_route_id: `final-render-path-stage-4`
- alternate_route_condition: Use only if additional diagnostic evidence is genuinely needed before preparing decision packets.
- agent_can_start_without_user_judgement: `true`
- purpose: Turn the separated gates into explicit decision packets for human, rights, publication, and public-use owners without approving those decisions.

- Carry forward ED-10al as diagnostic evidence only.
- Prepare at most the next explicit decision packet for the blocking gate.
- Keep production/public claims closed until the relevant owner answers.

This route must not:

- approve production subtitle design
- approve production render
- approve creative use
- claim rights clearance
- claim publishing readiness
- grant public-use permission
- track ignored media under episodes/
- reopen old layout or candidate-comparison reviews

## Validation

- gate_names_present: `true`
- stage3_source_preserved: `true`
- diagnostic_evidence_linked: `true`
- production_public_non_approval_explicit: `true`
- owners_present: `true`
- unsafe_overclaiming_present: `true`
- tracked_media_boundary_closed: `true`
- same_machine_ignored_boundary_recorded: `true`
- next_executable_route_defined: `true`
- all_checks_passed: `true`

## Boundary

- production_subtitle_design_acceptance: `false`
- production_render_acceptance: `false`
- creative_acceptance: `false`
- rights_status: `pending`
- publishing_acceptance: `false`
- public_use_permission: `false`
- tracked_binary_artifact_created: `false`
- episodes_tracked: `false`
- new_render_created: `false`
- new_rehearsal_run: `false`
- final_render_path_approved: `false`
