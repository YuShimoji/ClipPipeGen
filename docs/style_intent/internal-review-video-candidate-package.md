# ED-10ar Internal Review Video Candidate Package

Artifact: `clip-ed10ar-internal-review-video-candidate-package-001`

## What This Is

ED-10ar assembles a tracked readback for the smallest internal-review video
candidate package. It uses Existing Output First: the same-machine ignored
diagnostic MP4, ASS, and local manifest from the render path selector probe are
already present, so no new render was run.

This is diagnostic-only and internal-review-only. It is not a production render,
not a public-use artifact, not a YouTube publish package, and not a user
decision request.

## Package Contents

| Item | Status | Path |
|---|---|---|
| Video | `present_same_machine_ignored_local` | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| ASS | `present_same_machine_ignored_local` | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| Local manifest | `present_same_machine_ignored_local` | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |

Local manifest readback:

- `status=local_ignored_probe_generated`
- `duration_seconds=4.2`
- `container=mov,mp4,m4a,3gp,3g2,mj2`
- `video_codec=h264`
- `audio_codec=aac`
- `resolution=1920x1080`
- `fps=30.0`
- `frame_rate=30/1`
- `stream_count=2`
- `ffmpeg_path_source=PATH`
- `ffprobe_path_source=PATH`
- `selected_profile_id=mp4_h264_aac`
- `selected_attempt_status=succeeded`
- `selected_attempt_exit_code=0`
- `ignored_by_git=true`
- `tracked_binary_artifact_created=false`

## Source Evidence

- Stage-5 source: `clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001`
- Stage-4 source: `clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001`
- Stage-3 render-path rehearsal: `clip-ed10al-final-render-path-stage-3-rehearsal-001`
- Active diagnostic source: `clip-ed10af-l2-render-path-selector-probe-001`

## What It Proves

- A same-machine ignored diagnostic MP4 exists.
- The ASS subtitle source and local manifest exist beside the MP4.
- The local manifest records duration, container, codec, resolution, fps, and
  stream count metadata.

## What It Does Not Prove

- Production subtitle design acceptance.
- Production render acceptance.
- Creative acceptance.
- Rights, publishing, public-use, or monetization permission.
- YouTube publish package readiness.

## Boundaries

- `diagnostic_only=true`
- `internal_review_only=true`
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `youtube_publish_package_created=false`
- `final_render_path_approved=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## Next

Next route: `optional-internal-review-video-observation`

Use `final-render-path-stage-4` only if a concrete diagnostic gap appears.
