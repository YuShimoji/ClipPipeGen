# ED-10as Internal Review Video Candidate Access Sheet

Artifact: `clip-ed10as-internal-review-access-sheet-fullpath-001`

Status: `ready_for_optional_user_review`

Action type: `USER_OPEN_ONLY_LATER`

## What This Is

This sheet gives exact current-host access to the ED-10ar internal review video
candidate. It does not create a new render, replay, production approval,
public-use approval, or YouTube publish package.

Source package: `clip-ed10ar-internal-review-video-candidate-package-001`

## Current-Host Paths

Folder:

`C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe`

MP4:

`C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe\subtitle_render_path_selector_probe.mp4`

ASS:

`C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe\subtitle_render_path_selector_probe.ass`

Manifest:

`C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen\episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe\subtitle_render_path_selector_probe.local.json`

## Open Command

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\operator\open_internal_review_video_candidate.ps1
```

Fallbacks:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\operator\open_internal_review_video_candidate.ps1 -OpenFolder
powershell -ExecutionPolicy Bypass -File scripts\operator\open_internal_review_video_candidate.ps1 -OpenManifest
powershell -ExecutionPolicy Bypass -File scripts\operator\open_internal_review_video_candidate.ps1 -OpenAss
```

## Later Observation Contract

Steps:

1. Run the launcher command from the repo root when a later supervisor asks for observation.
2. Confirm the MP4 opens; use `-OpenFolder` only if the default player does not launch.
3. Answer freely in one sentence or a few bullets.

Look for:

1. Does the MP4 open and show a coherent 4.2s internal review candidate?
2. Are subtitles, audio, and layout present enough to understand what is being tested?
3. Is the next problem mainly script/offer clarity, timing/audio, visual layout, or render path?

Answer style: freeform. One sentence is enough.

Not needed: production judgment, rights/public-use decision, fixed form,
screenshot, commit, or rerender.

## Post-Observation Relay

When a later freeform observation arrives, extract only:

- openability
- subtitle/audio/layout observation
- next problem category

Do not infer production approval, rights/public-use approval, publishing
readiness, or monetization readiness from the observation.

## Boundaries

- `new_render=false`
- `new_replay=false`
- `media_modified=false`
- `episodes_tracked=false`
- `production_acceptance=false`
- `rights_public_use_approval=false`
- `publishing_acceptance=false`
- `monetization_acceptance=false`
- `youtube_publish_package_created=false`
