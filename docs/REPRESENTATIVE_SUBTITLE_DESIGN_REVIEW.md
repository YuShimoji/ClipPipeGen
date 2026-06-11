# Representative Subtitle Design Review

Last updated: 2026-06-11 JST

This note records the smallest representative diagnostic subtitle design review
start after the `cut_003` diagnostic burned-in proof readability acceptance.
It does not approve production subtitle design, production render, creative
quality, rights, publishing, or public use.

## Route

The selected route is docs/readback only. Existing artifacts were sufficient to
choose representative targets and identify blockers, but not sufficient to say
that the current subtitle presentation contract is stable across more than
`cut_003`.

No proof or render was regenerated in this slice. The established
`build-subtitle-overlay-visual-proof` command writes the shared
`subtitle_overlay_visual_proof_report.*` and updates
`representative_visual_proof_report.*`; running it for `cut_002` alone would
replace the current report target from `cut_003` to `cut_002`. A regeneration
slice should therefore be explicit about whether it is producing a fresh
combined `cut_002` / `cut_003` representative proof surface.

## Inputs Read

- `docs/RUNTIME_STATE.md`
- `docs/HANDOFF.md`
- `docs/SUBTITLE_PRESENTATION_CONTRACT.md`
- `docs/CUT_003_REVIEW_CONTRACT_TAXONOMY_AUDIT.md`
- `episodes/jp_pilot01_hololive_bancho_20260525/edit_pack.json`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_packet.json`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_review_packet.json`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.json`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.json`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/production_subtitle_render_acceptance_report.json`
- `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_operator_proxy_decision_handoff.json`
- `status-episode --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --format json`

All `episodes/` files are ignored local artifacts and must remain untracked.

## Representative Targets

| target | why selected | review purpose | current evidence | design-review state |
|---|---|---|---|---|
| `cut_002` | kept comparison cut with `context_status=passed` and a short subtitle surface | dialogue readability, safe area / position, timing impression, comparison against the accepted `cut_003` baseline | `representative_visual_proof_report.json` has `visual_proof_status=available_requires_human_review` and `visual_proof_cut_002.png` exists | eligible as a comparison target, but blocked for current-contract stability because there is no current `jp_clip_dialogue_badge_left_v0` detailed overlay proof/readback for this cut |
| `cut_003` | accepted diagnostic baseline and current target in `SUBTITLE_PRESENTATION_CONTRACT.md` | dialogue readability, speaker badge fallback, line wrapping / suffix-tail behavior, safe area / position, timing impression, response/referral block coverage | `subtitle_overlay_visual_proof_report.json` targets `cut_003`, range `22.606 -> 49.566`, `sub_010..sub_029`, `jp_clip_dialogue_badge_left_v0`, explicit ASS line breaks, `renderer_gap` visible | accepted only as `diagnostic_subtitle_wrapping_readability_acceptance=true` for current diagnostic proof readability; not production design |
| `cut_008` | current `needs_adjustment` dense-subtitle stress case: 33 subtitles, high subtitle density, current decision packet says split or rewrite before production-adjacent acceptance | reading load, line wrapping pressure, safe area under density, timing impression | current decision/readback exists, but no current subtitle-overlay proof for this contract | blocked before design review by `needs_adjustment` state and missing representative proof; use only to define the next adjustment/proof prerequisite |

## Review Readback

The current subtitle presentation contract is not yet proven stable across
representative scenes. The only current detailed proof for
`jp_clip_dialogue_badge_left_v0` is `cut_003`.

`badge_left_dialogue` is sufficiently reviewable on `cut_003` for diagnostic
readability only. It is not yet cross-cut stable because `cut_002` lacks a
current detailed overlay proof with the same contract candidate.

`bottom_center_emphasis` and `reaction_caption` remain supported/defined modes,
but they are not accepted design modes from the current representative proof
set. They require a representative proof target where the mode is actually
selected.

The speaker identity path remains a fallback. Real face icon assets are not
available in the current material ledger, so `SPK`/badge presentation is still
a diagnostic placeholder and not production speaker identity design.

The dense/reading-load path is blocked by current cut state. `cut_008` is the
best small stress target for density, but it should not be used to lift
subtitle design acceptance until its adjustment/split/rewrite route is chosen
or a deliberately diagnostic proof is requested with the limitation visible.

## Current Boundary

- `diagnostic_subtitle_wrapping_readability_acceptance=true` for `cut_003`
  only.
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `renderer_gap` remains visible and must not be hidden.

## Limitation-Lift Evidence Still Required

To lift `production_subtitle_design_acceptance=false`, the next evidence must
include representative subtitle design review across relevant cuts/scenes with
current-contract proof/readback for at least:

- a kept comparison cut such as `cut_002`
- the accepted baseline `cut_003`
- a dense or otherwise stressful subtitle surface after its cut-adjustment
  state is explicitly handled

The review must cover font, size, outline, color, speaker identity, mode
selection, safe area, line wrapping, timing impression, and the visible
`renderer_gap`. It must keep rights/publication state separate.

## Smallest Next Slice

The narrowest next proof route is a deliberate Verify slice that regenerates a
fresh combined diagnostic subtitle-overlay proof for `cut_002` and `cut_003`
under the current contract, then parses JSON/HTML and re-reads both cuts as one
representative surface. That slice should keep `episodes/` ignored, preserve
all production/public flags as false or pending, and explicitly report whether
the refreshed `cut_003` proof is still the same human-reviewed baseline or a
new proof requiring re-review.
