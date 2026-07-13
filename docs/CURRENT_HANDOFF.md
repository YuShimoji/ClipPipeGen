---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT07_REINSTANTIATED_BASELINE_ACCEPTED_NATIVE_SHORTS_COVER_OPERATOR_PACK_REVIEW_READY
progress_pct: 92
last_touched: 2026-07-13
current_slice: OUT-07
phase: native_shorts_cover_operator_pack_review_ready
canonical_status: branch_review_pending_human_cover_direction
active_branch: codex/out-07-internal-operator-delivery-pack-v0
current_title: OUT-07 accepted baseline and native Shorts cover operator review
human_entrypoint: http://127.0.0.1:8071/index.html
review_open_command: powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_shorts_poster_frame_direction_proof\open_preview.ps1 -Serve -Port 8071
machine_readback: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/poster_direction_readback.json
operator_readback: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/operator_delivery_readback.json
decision_required: approve_native_shorts_cover_direction_or_describe_discomfort
review_status: accepted_baseline_native_cover_package_verified_cover_decision_pending
remote_code_complete: true
local_artifact_available: true
cross_machine_resume_class: conditional_reacquire
active_rebuild_contract: artifacts/ACTIVE_REBUILD.json
evidence_revision: planner007-e2206cef-20260525
accepted_baseline_sha256: 2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18
recommended_cover_path: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/native_shorts_cover_1080x1920.png
recommended_cover_sha256: 6d8cf92ae49658a9eacb98e7a6e584aa69d2a4ecbb56b553c93eec69e6a3a174
recommended_cover_timestamp_seconds: 11.930
recommended_cover_selection_status: recommended_pending_human_acceptance
last_verified_host: DESKTOP-U9P4LKJ
last_verified_host_label: Planner007
local_artifact_evidence_receipt: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/combined_review_manifest.json
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
public_or_publishing_acceptance: false
next_review_due: native_shorts_cover_direction_human_review
next_action: Open the localhost review and answer the single cover-direction question; describe only any discomfort with the accepted-video frame plus existing subtitle.
active_artifact: clip-out07-shorts-poster-frame-direction-proof-v0-001
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, artifacts/ACTIVE_REBUILD.json, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
---

# Current Handoff - ClipPipeGen

## What This Is

This is the short re-entry note for the active OUT-07 branch. The authoritative
state is [RUNTIME_STATE.md](RUNTIME_STATE.md), and the cross-machine recovery
contract is [ACTIVE_REBUILD.json](../artifacts/ACTIVE_REBUILD.json). The only
pending human judgement is the native Shorts cover direction.

## Current State

Planner007 explicitly accepted the current vertical baseline on 2026-07-13
JST for content/narrative, timing/tempo, cut continuity, A/V continuity,
subtitle timing/readability, and visual integrity. Its SHA-256 is
`2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`
and its duration is about 38.633333 seconds. The active package copies those
bytes without rerender, remux, transcode, edit, subtitle, audio, or timing
changes. Historical OUT-06 acceptance is not inherited.

The only recommended cover is the accepted video's frame at 11.930 seconds,
with the already-burned-in `sub_010` line. It adds no headline, logo, CTA,
background replacement, mask, cutout, collage, invented person, or third-party
pixel. Three timestamps were compared internally, but alternatives were not
exported. The prior A/B/C are retained only as folded hash evidence with
`superseded_by_user_short_context_reframe`; this is not a quality rejection and
they must not be offered again. Historical context/tension/payoff remains
separately `user_rejected`.

The unchanged title, description, tags, and evidence trace are present as
operator readback. The recommended cover is still
`selected_by_human=false`; `selected_thumbnail=null`, `publish_ready=false`,
all external-action gates are closed, and all attempt flags are false.

## Open and Review

Start or reopen the retained byte-range server:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_shorts_poster_frame_direction_proof\open_preview.ps1 -Serve -Port 8071
```

Then use `http://127.0.0.1:8071/index.html`. The page asks exactly one thing:

> Shorts一覧用coverとして、映像由来フレーム＋既存字幕だけのこの方向を採用してよいか。違和感があれば自由記述してください。

The baseline SHA, metadata, source mapping, gates, and old A/B/C are readback
context only; do not turn them into additional questions.

## Next

After a positive cover decision, H1 can record the final cover selection, run
the closure/full suite, and prepare the main-branch decision. H2 is only for a
real other-host recovery and must reacquire official captions before rebuilding
semantic media. H3 remains rights, production, public/publishing, or external
system work and is not authorized by this handoff.

## Constraints / Risks

- `episodes/` stays ignored and untracked; the review package is retained local
  evidence, not a Git payload.
- The tracked contract retains subtitle IDs, timing, segment locators, hashes,
  and wrap break indices, but no 29-line caption plaintext snapshot. Missing
  ignored authority must stop as `caption_authority_reacquire_required`.
- Another host must also restore the exact accepted 21,669,538-byte baseline
  through an authorized retained-artifact channel; absence stops as
  `accepted_baseline_reacquire_required`, and rerender is not an alternative.
- Earlier commits may still contain the removed plaintext snapshot. This tip
  makes no history-scrub claim.
- Rights remain pending. Production, public/publishing, upload/visibility, and
  made-for-kids decisions remain closed and unattempted.
