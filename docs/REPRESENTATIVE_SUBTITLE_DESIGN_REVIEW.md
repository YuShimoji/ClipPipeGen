# Representative Subtitle Design Review

Last updated: 2026-06-11 JST

This note records the smallest representative diagnostic subtitle design review
start after the `cut_003` diagnostic burned-in proof readability acceptance.
It does not approve production subtitle design, production render, creative
quality, rights, publishing, or public use.

## Route

The first route was docs/readback only: existing artifacts were sufficient to
choose representative targets and identify blockers, but not sufficient to say
that the current subtitle presentation contract was stable beyond `cut_003`.

The follow-up Verify route regenerated the shared
`subtitle_overlay_visual_proof_report.*` and refreshed
`representative_visual_proof_report.*` explicitly for combined targets
`cut_002` and `cut_003`. The useful command is:

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

The generated artifacts remain ignored local diagnostic proof only. The
Pillow-enabled run is required for current font-bbox wrapping readback; running
without Pillow falls back and does not preserve the accepted suffix-tail
readback.

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
| `cut_002` | kept comparison cut with `context_status=passed` and a short subtitle surface | dialogue readability, safe area / position, timing impression, comparison against the accepted `cut_003` baseline | combined `subtitle_overlay_visual_proof_report.json` targets `cut_002` and `cut_003`; `cut_002` has `jp_clip_dialogue_badge_left_v0`, `ffmpeg_subtitles_filter_ass`, font-bbox wrapped lines, resolved PNG/MP4/sample links, `renderer_gap` visible | representative-review-ready as a diagnostic comparison target only; not production design |
| `cut_003` | accepted diagnostic baseline and current target in `SUBTITLE_PRESENTATION_CONTRACT.md` | dialogue readability, speaker badge fallback, line wrapping / suffix-tail behavior, safe area / position, timing impression, response/referral block coverage | combined `subtitle_overlay_visual_proof_report.json` targets `cut_003`, range `22.606 -> 49.566`, `sub_010..sub_029`, response/referral block `sub_025..sub_029`, `jp_clip_dialogue_badge_left_v0`, explicit ASS line breaks, `renderer_gap` visible | accepted only as `diagnostic_subtitle_wrapping_readability_acceptance=true` for current diagnostic proof readability; not production design |
| `cut_008` | current `needs_adjustment` dense-subtitle stress case: 33 subtitles, high subtitle density, current decision packet says split or rewrite before production-adjacent acceptance | reading load, line wrapping pressure, safe area under density, timing impression | current decision/readback exists, but no current subtitle-overlay proof for this contract | blocked before design review by `needs_adjustment` state and missing representative proof; use only to define the next adjustment/proof prerequisite |

## Review Readback

The current subtitle presentation contract is representative-review-ready for
the already-kept diagnostic proof surfaces `cut_002` and `cut_003` only. This
means the operator can now compare the current `badge_left_dialogue` contract
across the short kept comparison cut and the accepted diagnostic baseline
without regenerating another proof.

`badge_left_dialogue` is sufficiently represented for diagnostic review on
`cut_002` and `cut_003`. It is not yet production-accepted and is not proven
for dense or needs-adjustment cuts.

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
include human representative subtitle design review across relevant cuts/scenes.
Current-contract proof/readback now exists for:

- kept comparison `cut_002`
- accepted diagnostic baseline `cut_003`

Still missing before production subtitle design acceptance can be lifted:

- an explicit human design acceptance decision, not only parser/readback
  verification
- a dense or otherwise stressful subtitle surface after its cut-adjustment
  state is explicitly handled

The review must cover font, size, outline, color, speaker identity, mode
selection, safe area, line wrapping, timing impression, and the visible
`renderer_gap`. It must keep rights/publication state separate.

## Smallest Next Slice

The narrowest next action is human visual review of the combined `cut_002` /
`cut_003` diagnostic proof surface. Keep the decision limited to subtitle
design/readability review and keep production/public flags false or pending.

The next proof expansion, if needed, is a separate `cut_008` adjustment/stress
route after its `needs_adjustment` state is explicitly handled.
