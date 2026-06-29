# ED-10ay Thank ED-10au Local Access Recovery Readback

This tracked readback records current-host recovery of the ignored ED-10au
representative micro-scene specimen on the Thank terminal. It does not replace
the ED-10au specimen contract and does not change ED-10ax's review-frame
surface.

## What Was Checked

- artifact_id: `clip-ed10ay-thank-ed10au-local-access-recovery-readback-001`
- feature_id: `ED-10ay`
- host_scope: `Thank terminal`
- repo_root_current_host: `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`
- source_review_frame_clarification_surface_artifact_id: `clip-ed10ax-review-frame-clarification-surface-001`
- source_representative_micro_scene_internal_review_specimen_artifact_id: `clip-ed10au-representative-micro-scene-internal-review-specimen-001`

The ED-10ax JSON/Markdown files, ED-10au JSON/Markdown files, and
`scripts/operator/open_representative_micro_scene_internal_review_specimen.ps1`
were present. The ED-10au ignored MP4, ASS, and local manifest were initially
absent on this host. That was classified as
`current_host_ignored_media_absent`, not as a Git tracked-file failure.

## Source Inputs

The required local source inputs existed before regeneration:

| input | path | readback |
|---|---|---|
| source video | `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4` | present, 35281366 bytes, AV1, 1920x1080, 30/1 fps, 164.768798s |
| source audio | `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav` | present, 5270822 bytes, PCM s16le, 16000 Hz, mono, 164.71075s |
| transcript | `episodes/jp_pilot01_hololive_bancho_20260525/transcript.json` | present, schema v1, 105 segments, `stt.engine=subtitle_track` |
| edit pack | `episodes/jp_pilot01_hololive_bancho_20260525/edit_pack.json` | present, schema v1, 9 cuts, 105 subtitle drafts |

The current transcript/edit pack contains the same 39-49s source window by
content and timing under `seg_000024`-`seg_000029` and
`sub_024`-`sub_029`. ED-10au's tracked artifact keeps its own local scene event
labels `sub_004`-`sub_006`; this recovery did not rewrite those tracked
labels.

## Regeneration

Regeneration used the existing bounded builder:

```powershell
uvx python -c "from pathlib import Path; from src.integrations.render import subtitle_preset_selector as s; s.write_representative_micro_scene_internal_review_local_artifacts(base_dir=Path.cwd(), ffmpeg_path='ffmpeg', ffprobe_path='ffprobe')"
```

This wrote only the same ED-10au ignored local specimen paths under
`episodes/`. It did not create a representative v2 specimen, screenshot
capture, stage-7 normalizer, production/public/publishing artifact, or tracked
media.

## Final Access State

- access_state: `verified_present`
- target_exists: `true`
- access_evidence_level: `file_exists_and_ffprobe_metadata`
- launcher_or_open_command: `powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_internal_review_specimen.ps1`

| output | full current-host path | readback |
|---|---|---|
| MP4 | `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_internal_review_specimen\representative_micro_scene_internal_review_specimen.mp4` | 3443682 bytes, 9.18s, H.264/AAC, 1920x1080, 30/1 fps |
| ASS | `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_internal_review_specimen\representative_micro_scene_internal_review_specimen.ass` | 989 bytes |
| local manifest | `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_internal_review_specimen\representative_micro_scene_internal_review_specimen.local.json` | 10867 bytes, JSON parsed |

## Boundary

- production_subtitle_design_acceptance: `false`
- production_render_acceptance: `false`
- creative_acceptance: `false`
- rights_status: `pending`
- publishing_acceptance: `false`
- public_use_permission: `false`
- monetization_acceptance: `false`
- micro_scene_accepted: `false`
- tracked_binary_artifact_created: `false`
- episodes_tracked: `false`
- ignored_local_media_only: `true`
- representative_micro_scene_v2_created: `false`
- screenshot_capture_created: `false`
- stage_7_freeform_normalizer_used: `false`
- user_review_requested_now: `false`

## Validation

- repo root and `origin/main` parity verified before regeneration
- ED-10ax and ED-10au tracked files parsed or were present
- source inputs checked
- MP4/ASS/manifest regenerated to the same ignored ED-10au path
- ffprobe metadata captured for the generated MP4
- `git ls-files episodes` remained empty
- the user was not asked to search manually again
