# ED-10ak Final Render-Path Stage 2 Replayability

This tracked stage-2 packet records how a later agent/operator can inspect or replay the selected FFmpeg/libass diagnostic subtitle overlay path. It does not run a new render and does not approve production subtitle design, production render, creative use, rights, publishing, or public use.

## Replay Operation

- operation_id: `ffmpeg_libass_diagnostic_replay_operation`
- selected_render_path: `ffmpeg/libass diagnostic subtitle overlay path`
- operation_status: `replayability_packet_ready_no_new_replay`
- existing_output_first_reused: `true`
- new_replay_run: `false`
- replay_required_now: `false`
- diagnostic_only: `true`
- command_family: `ffmpeg with libass subtitles filter plus ffprobe readback`

## Required Tracked Inputs

- `docs/style_intent/subtitle-final-render-path-stage-1.json`
- `docs/style_intent/subtitle-final-render-path-readiness.json`
- `docs/style_intent/subtitle-render-path-selector-probe.json`
- `docs/style_intent/subtitle-render-path-lineage-observation-surface.json`
- `docs/style_intent/subtitle-render-contract-consumer-dry-read.json`
- `docs/style_intent/subtitle-render-path-selector-contract.json`
- `src/integrations/render/subtitle_preset_selector.py`
- `src/integrations/render/ffmpeg_tiny.py`

## Required Same-Machine Local Inputs

| input | same-machine path |
|---|---|
| source_video | `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4` |
| source_audio | `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav` |

## Ignored Output Paths

| output | path |
|---|---|
| ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |

## Operation Matrix

| row | area | status | source artifact | details |
|---|---|---|---|---|
| selected_render_path | selected render path | selected_for_replayability | clip-ed10aj-final-render-path-stage-1-001 | ffmpeg/libass diagnostic subtitle overlay path<br>Selected by ED-10aj as preparation only, not production render approval. |
| required_tracked_inputs | required tracked inputs | available | clip-ed10aj-final-render-path-stage-1-001 | docs/style_intent/subtitle-final-render-path-stage-1.json<br>docs/style_intent/subtitle-final-render-path-readiness.json<br>docs/style_intent/subtitle-render-path-selector-probe.json<br>docs/style_intent/subtitle-render-path-lineage-observation-surface.json<br>docs/style_intent/subtitle-render-contract-consumer-dry-read.json<br>docs/style_intent/subtitle-render-path-selector-contract.json<br>src/integrations/render/subtitle_preset_selector.py<br>src/integrations/render/ffmpeg_tiny.py |
| required_same_machine_local_inputs | required same-machine local inputs | same_machine_may_be_absent | clip-ed10af-l2-render-path-selector-probe-001 | source_video: episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4<br>source_audio: episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav |
| ignored_output_paths | ignored output paths | recorded_same_machine_may_be_absent | clip-ed10ag-lineage-and-observation-surface-001 | ass: episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass<br>video: episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4<br>manifest: episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json<br>contact_sheet: episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg |
| expected_output_types | expected output types | recorded | clip-ed10af-l2-render-path-selector-probe-001 | ass<br>mp4<br>local_manifest_json<br>contact_sheet_jpg |
| command_family | command or command family | recorded_from_source_probe | clip-ed10af-l2-render-path-selector-probe-001 | ffmpeg with libass subtitles filter plus ffprobe readback<br>Source probe command summary is retained for readback; ED-10ak does not rerun it. |
| validation_readback_commands | validation/readback commands | recorded | clip-ed10ak-final-render-path-stage-2-replayability-001 | uvx python -m json.tool docs\style_intent\subtitle-final-render-path-stage-2.json<br>uvx python -m json.tool docs\style_intent\subtitle-render-path-selector-probe.json<br>git ls-files episodes<br>git check-ignore -v -- episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4 episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg |
| fresh_clone_absence_behavior | absence behavior on fresh clone | non_fatal_for_tracked_docs | clip-ed10ai-final-render-path-readiness-packet-001 | Same-machine ignored media may be absent on a fresh clone. That absence is non-fatal for tracked docs; rerun only under a separate explicit diagnostic replay route. |
| diagnostic_only_scope | diagnostic-only scope | closed_to_production_public_use | clip-ed10aj-final-render-path-stage-1-001 | The operation packet reuses ignored diagnostic proof only.<br>It does not approve production subtitle design, production render, creative use, rights, publishing, or public use. |
| missing_before_production_render | missing before production render | missing | clip-ed10ai-final-render-path-readiness-packet-001 | Explicit production subtitle design acceptance.<br>Accepted final production render output.<br>Final production render command/output manifest and review result.<br>Explicit creative acceptance for production use. |

## Command Family

- command_family: `ffmpeg with libass subtitles filter plus ffprobe readback`
- source_probe_render_command_summary: `ffmpeg -y -ss 0 -t 4.2 -i ./episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4 -ss 0 -t 4.2 -i ./episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav -map 0:v:0 -map 1:a:0 -vf scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p,subtitles=filename='./episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass' -c:v libx264 -c:a aac -shortest ./episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4`

## Validation / Readback Commands

- `uvx python -m json.tool docs\style_intent\subtitle-final-render-path-stage-2.json`
- `uvx python -m json.tool docs\style_intent\subtitle-render-path-selector-probe.json`
- `git ls-files episodes`
- `git check-ignore -v -- episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4 episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg`

## Fresh Clone Absence Behavior

Same-machine ignored media may be absent on a fresh clone. That absence is non-fatal for tracked docs; rerun only under a separate explicit diagnostic replay route.

## Still Missing Before Production Render Approval

- Explicit production subtitle design acceptance.
- Accepted final production render output.
- Final production render command/output manifest and review result.
- Explicit creative acceptance for production use.

## Still Missing Before Publishing/Public Use

- Rights clearance or owner decision.
- Publishing acceptance.
- Explicit public-use permission.

## Handoff Routes

- primary_route_id: `final-render-path-stage-3`
- alternate_route_id: `production-limitation-lift-stage-1`
- stage_3_purpose: Prepare an actual final-path rehearsal from the replayability packet while retaining diagnostic and production boundaries.
- production_limitation_lift_stage_1_purpose: Prepare human, rights, publishing, and public-use decision packets without approving those decisions.
- neither_route_approves_production_public_use: `true`

## Validation

- required_rows_present: `true`
- stage1_source_preserved: `true`
- active_diagnostic_source_preserved: `true`
- operation_replayability_defined: `true`
- existing_output_first_applied: `true`
- local_ignored_outputs_referenced: `true`
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
- new_replay_run: `false`
- final_render_path_approved: `false`
