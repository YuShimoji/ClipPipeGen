---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: out07_combined_review_ready_planner007
progress_pct: 88
last_touched: 2026-07-13
current_slice: OUT-07
phase: combined_baseline_and_poster_review_ready
canonical_status: branch_review_pending_human_combined_review
active_branch: codex/out-07-internal-operator-delivery-pack-v0
current_title: OUT-07 Planner007 media revision baseline and Shorts poster combined review
human_entrypoint: http://127.0.0.1:8071/index.html
review_open_command: powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_shorts_poster_frame_direction_proof\open_preview.ps1 -Serve -Port 8071
machine_readback: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/poster_direction_readback.json
decision_required: review_reinstantiated_baseline_then_choose_A_B_C_or_reject_all
review_status: planner007_combined_review_package_verified_human_decision_pending
remote_code_complete: true
local_artifact_available: true
cross_machine_resume_class: reacquirable
active_rebuild_contract: artifacts/ACTIVE_REBUILD.json
evidence_revision: planner007-e2206cef-20260525
last_verified_host: DESKTOP-U9P4LKJ
last_verified_host_label: Planner007
local_artifact_evidence_receipt: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/combined_review_manifest.json
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
public_or_publishing_acceptance: false
next_review_due: combined_baseline_and_poster_human_review
next_action: Open the combined localhost review, inspect the reinstantiated baseline first, then choose A/B/C or reject all; note any baseline or poster anomaly without granting production or rights acceptance.
active_artifact: clip-out07-shorts-poster-frame-direction-proof-v0-001
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, artifacts/ACTIVE_REBUILD.json, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
---

# Current Handoff - ClipPipeGen

## What This Is

This is a short re-entry note for the active OUT-07 branch. The authoritative
state is [RUNTIME_STATE.md](RUNTIME_STATE.md); the cross-machine reconstruction
contract is [ACTIVE_REBUILD.json](../artifacts/ACTIVE_REBUILD.json). Historical
OUT-03 through OUT-06 closeouts remain in Runtime history and are not required
to rebuild the current media revision.

## Current State

Planner007 source `e2206cef...1889` is qualified as the same YouTube episode
`7J5aS_pcBj4` with compatible timing, but not as a byte copy of historical
source `6f78657e...103a`. The current episode authority rebuilt the fixed
three-cut, 29-subtitle baseline and then generated poster A/B/C, platform
previews, masks, reference evidence, and transitions in one ignored local
package. The direct authority check includes transcript/edit episode identity,
official-caption content, and the operator-proxy limitation record. A fresh
clone can instead use the tracked semantic snapshot after the existing
source-video/audio fetch CLIs recreate the material chain.

The baseline output differs from historical accepted OUT-06 bytes, so it is
`reinstantiated_baseline_candidate`; human acceptance is false and must not be
inferred from the old package. The legacy 16:9 `context`, `tension`, and
`payoff` thumbnails remain rejected and were not regenerated. Two same-input
builds matched for both the source-derived deterministic core and the separate
reference evidence digest.

## Open and Review

Start the retained byte-range server:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_shorts_poster_frame_direction_proof\open_preview.ps1 -Serve -Port 8071
```

Then use `http://127.0.0.1:8071/index.html`. Review in this order:

1. Play and seek through the 38.6-second reinstantiated baseline. Report any
   new content, timing, subtitle, audio, or visual anomaly.
2. Compare A/B/C and their platform/transition previews. Choose the closest
   usable direction, or reject all; add poster discomfort only when present.

The page intentionally asks only those two freeform questions.

## Next

After human review, a later decision may select one poster for operator-pack
integration or return a bounded visual correction. Do not merge to main,
upload, publish, decide rights, or grant production acceptance from this
handoff.

## Constraints / Risks

- `episodes/` remains ignored and untracked; another machine must follow the
  active rebuild contract and verify its own local package.
- Third-party reference pixels remain only in ignored evidence cache/board and
  are never candidate pixels or Git payloads.
- Historical source/output hashes are comparison evidence, not current input
  requirements and not aliases for the Planner007 revision.
