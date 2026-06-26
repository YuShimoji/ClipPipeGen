# ED-10aj Final Render-Path Stage 1

This tracked stage-1 packet selects a final render-path candidate from existing diagnostic evidence. It does not approve production subtitle design, production render, creative use, rights, publishing, or public use.

## Stage-1 Candidate

- candidate_id: `ffmpeg_libass_diagnostic_path_stage_1`
- render_adapter_path: `ffmpeg/libass diagnostic subtitle overlay path`
- selection_status: `selected_for_stage_1_preparation_only`
- selected_from_artifact_id: `clip-ed10af-l2-render-path-selector-probe-001`
- source_policy: `existing_output_first_reuse_ed10af_ed10ag_ed10ai_no_new_render`
- stage_1_candidate_not_production_render: `true`
- reason: ED-10af already proves representative selector payloads can pass through FFmpeg/libass with ASS subtitle overlay output, while ED-10ai keeps production/public approvals closed.

## Source Evidence

- readiness packet: `clip-ed10ai-final-render-path-readiness-packet-001`
- active diagnostic proof source: `clip-ed10af-l2-render-path-selector-probe-001`
- lineage observation support: `clip-ed10ag-lineage-and-observation-surface-001`
- gate separation source: `clip-ed10ah-production-limitation-lift-entry-001`
- dry-read predecessor: `clip-ed10af-render-contract-consumer-dry-read-001`
- dry-read predecessor source commit: `7e96a28`
- selector semantic style contract: `clip-ed10ab-subtitle-preset-selector-001`
- render adapter input contract: `clip-ed10ae-render-path-selector-contract-probe-001`

| local output | same-machine path |
|---|---|
| ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |

## Stage-1 Checklist

| check | status | source artifact | evidence | missing before approval |
|---|---|---|---|---|
| render_adapter_path_selected | selected_for_stage_1_preparation | clip-ed10af-l2-render-path-selector-probe-001 | FFmpeg/libass diagnostic subtitle overlay path is selected from ED-10af as the stage-1 candidate.<br>Selection is preparation only and does not approve production render. | Production render acceptance remains missing. |
| subtitle_ass_generation_path_available | available_same_machine_diagnostic_only | clip-ed10af-l2-render-path-selector-probe-001 | ED-10af records an ignored ASS output path.<br>ASS path: episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass | Portable/tracked production ASS artifact strategy remains missing. |
| semantic_selector_contract_available | available | clip-ed10ab-subtitle-preset-selector-001 | The deterministic preset selector and ED-10ae render adapter input contract are available.<br>ED-10ai records selector/semantic and render adapter evidence as ready. | none |
| stable_body_text_policy_preserved | preserved | clip-ed10af-l2-render-path-selector-probe-001 | ED-10af validation keeps stable body text across selected examples.<br>body_text_color_policy: stable_default_body_text | none |
| badge_accent_backplate_routing_preserved | preserved | clip-ed10af-l2-render-path-selector-probe-001 | ED-10af preserves badge/accent/backplate-first semantic variation.<br>Body subtitle text color is not used as the primary semantic variation surface. | none |
| line_break_safe_area_metadata_preserved | preserved | clip-ed10af-l2-render-path-selector-probe-001 | ED-10af validation keeps safe-area line-break metadata.<br>Whisper selected example records ASS newline behavior. | none |
| local_ignored_proof_media_recorded | recorded_same_machine_may_be_absent_elsewhere | clip-ed10ag-lineage-and-observation-surface-001 | ED-10ag and ED-10ai record ignored ASS/MP4/manifest/contact-sheet paths.<br>same_machine_diagnostic_only_may_be_absent_on_other_clone | If absent on another clone, regenerate or observe under an explicit diagnostic route only. |
| no_tracked_binary_media | closed | clip-ed10ai-final-render-path-readiness-packet-001 | ED-10ai render gate records no tracked binary artifact.<br>episodes/ remains outside tracked artifact scope. | none |
| production_gates_still_closed | closed | clip-ed10ai-final-render-path-readiness-packet-001 | Production subtitle design, production render, and creative acceptance remain false. | Explicit production subtitle design acceptance.<br>Accepted production render output.<br>Explicit creative acceptance. |
| publishing_public_use_gates_still_closed | closed_or_pending | clip-ed10ai-final-render-path-readiness-packet-001 | Rights status remains pending.<br>Publishing acceptance and public-use permission remain false. | Rights clearance or owner decision.<br>Publishing acceptance.<br>Explicit public-use permission. |

## Still Missing Before Production Render Approval

- Explicit production subtitle design acceptance.
- Accepted final production render output.
- Final production render command/output manifest and review result.
- Explicit creative acceptance for production use.

## Still Missing Before Publishing/Public Use

- Rights clearance or owner decision.
- Publishing acceptance.
- Explicit public-use permission.

## Next Executable Route

- route_id: `final-render-path-stage-2`
- alternate_route_id: `production-limitation-lift-stage-1`
- agent_can_start_without_user_judgement: `true`
- purpose: Use the selected FFmpeg/libass diagnostic path candidate to prepare a later final render-path stage without granting production, publishing, or public-use approval.

- Carry ED-10aj selected path and checklist into final-render-path-stage-2.
- Keep ED-10ai missing production/public decision rows attached.
- Reuse ignored proof paths only as same-machine diagnostic evidence.

This route must not:

- approve production subtitle design
- approve production render
- approve creative use
- make rights claims
- upload or publish
- grant public-use permission
- request display/layout polish or old comparison reviews
- add episodes/ or binary proof media to Git

## Validation

- required_checklist_present: `true`
- readiness_source_preserved: `true`
- active_diagnostic_source_preserved: `true`
- stage_1_candidate_defined: `true`
- semantic_selector_contract_available: `true`
- local_ignored_proof_media_referenced: `true`
- no_tracked_binary_media: `true`
- production_public_boundary_closed: `true`
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
- final_render_path_approved: `false`
