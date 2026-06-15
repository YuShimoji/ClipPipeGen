# Representative Subtitle Design Review

Last updated: 2026-06-15 JST

This note records the smallest representative diagnostic subtitle design review
start after the `cut_003` diagnostic burned-in proof readability acceptance.
It does not approve production subtitle design, production render, creative
quality, rights, publishing, or public use.

## Active Artifact: `clip-review-acceptance-gate-001`

- Slice label: `ED-10f: Representative Subtitle Design Review v1`
- Current packet state: `human_response_adjust_boundary_font_family_decoration`
- Dense/stress state: `representative_review_blocked_missing_dense_stress_proof`
  for `cut_008`
- Packet created from parser-first readback on 2026-06-15 JST before this docs
  update: `HEAD=8f6f518 (main, origin/main)`, `HEAD...origin/main=0 0`,
  `git status --short --branch` was `## main...origin/main`, and
  `git ls-files episodes` returned no paths.

The registry was checked before assigning the slice label: `ED-10b` is already
the R3 chapter revision board / patch template, and `ED-10f` was unused before
this packet. The packet is a diagnostic / representative review gate only. It
does not consume or create human production acceptance.

### Parser-First Episode Readback

`status-episode --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --format json`
reported `reviewability=review_ready`, `review_ready=true`, no missing review
artifacts, `rights_status=pending`, and `production_candidate=false`.

| field | readback |
|---|---|
| transcript | `segments_count=105`, `engine=subtitle_track`, `language=ja`, `review_status=needs_review`, `accepted_count=105` |
| editing | `selected_cuts_count=9`, `subtitles_count=105`, context `passed=3` / `needs_review=6` |
| final cut decision | keep `cut_001`, `cut_002`, `cut_003`; needs adjustment `cut_004`-`cut_008`; reject `cut_009` |
| next action | choose one narrow limitation-lift slice; production candidate remains false |

Existing proof was sufficient. The combined
`subtitle_overlay_visual_proof_report.json` already has
`target_cuts=[cut_002, cut_003]`, `subtitle_overlay_available_count=2`, and
`all_target_cuts_have_overlay=true`, so this packet does not regenerate proof.

### Representative Gate Targets

| target | current evidence | design-review state | status | this artifact can decide | this artifact cannot decide |
|---|---|---|---|---|---|
| `cut_002` | `edit_pack` range `12.329 -> 17.167`, `sub_008..sub_009`, context `passed`; combined overlay proof has PNG/MP4/ASS/SRT/sample frames, `available_diagnostic_subtitle_overlay`, font-bbox wrapping applied, and no one-character orphan / suspicious tail line | kept comparison target for readability, safe area, timing impression, and comparison against `cut_003` | ready as diagnostic representative evidence | whether the current `badge_left_dialogue` direction is acceptable enough as a representative comparison target | production subtitle design, production render, rights, publishing, public use, or dense/stress coverage |
| `cut_003` | `edit_pack` range `22.606 -> 49.566`, `sub_010..sub_029`, response/referral block `sub_025..sub_029`, context `needs_review` retained; combined overlay proof has current diagnostic evidence, explicit ASS line breaks, suffix-tail prevention count `2`, and accepted diagnostic readability baseline | accepted only for current diagnostic burned-in readability baseline; now used as the comparison baseline for representative review | ready as diagnostic baseline evidence | whether the current baseline can carry forward as representative subtitle design evidence for kept proof surfaces | any generalized production subtitle design acceptance or creative / rights / publishing acceptance |
| `cut_008` | `edit_pack` range `116.934 -> 135.219`, `sub_069..sub_101`, 33 subtitles, subtitle density `1.805`, context `needs_review`; current combined overlay proof does not target it | dense / stress candidate, but its cut state and current proof coverage are not ready | blocked: `representative_review_blocked_missing_dense_stress_proof` | that dense/stress evidence is still required before widening representative scope | a pass/fail design judgment, because current proof is missing and the cut is still `needs_adjustment` |

### Subtitle Design Axes

| axis | current readback for `cut_002` / `cut_003` | review effect |
|---|---|---|
| font | ASS style readback `Yu Gothic`; measurement family `NotoSansJP-VF`; renderer glyph fallback remains provider-dependent | human review can assess visible readability, not production font finality |
| size | `font_size=124` from `round(frame_height * 0.115)` on 1920x1080 proof | candidate size is visible for diagnostic review |
| outline | `outline=12` from `max(2, round(font_size * 0.096))`, plus shadow `2` | candidate outline weight is visible for readability review |
| color | diagnostic ASS candidate color is visible in proof, but color is not production-approved | human may accept or request adjustment for the representative direction |
| speaker identity | real face icon assets unavailable; `SPK` speaker badge placeholder fallback is used | review can decide whether fallback evidence is acceptable, not production speaker identity |
| mode selection | selected mode `badge_left_dialogue`; `bottom_center_emphasis` remains supported but not accepted by this proof | this gate covers the current normal dialogue mode only |
| safe area | proof status `diagnostic_overlay_visible_human_review_required`; generated 1920x1080 PNG/MP4/sample frames exist | human review is still required for final safe-area judgment |
| line wrapping | `japanese_boundary_font_bbox_pixel_wrap_v1`, authority `font_bbox_pixel_measurement_not_grid_cell_count`, explicit ASS line breaks true, no one-character orphan or suspicious tail line | parser readback supports visual review; it does not remove renderer review |
| timing impression | subtitle timing items are included for both cuts; proof status remains `diagnostic_timing_overlay_generated_human_review_required` | human review can judge diagnostic timing impression |
| dense / stress evidence | absent for current proof; `cut_008` remains `needs_adjustment` with 33 subtitles | blocks widening representative design acceptance |
| visible `renderer_gap` | `controlled_line_breaks_carried_renderer_bbox_not_claimed`, `exists=true` | must stay visible; proof does not claim production typography readiness |

### Boundary Flags

- `diagnostic_subtitle_wrapping_readability_acceptance=true` for current
  `cut_003` diagnostic proof readability only.
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `renderer_gap` remains visible and must not be hidden.

### Manual Verification

Minimum file to open:

1. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html`

Optional direct proof files if the HTML viewer cannot play embedded media:

2. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_002.mp4`
3. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_003.mp4`

Ask exactly one human review question:

> Diagnostic / representative review の範囲で、現在の `cut_002` / `cut_003`
> `badge_left_dialogue` presentation を、代表字幕デザイン evidence として
> 次工程へ進めてよいですか？ production subtitle design / production render /
> rights / publishing / public use は承認しません。

Response options:

- `accept_candidate`: representative subtitle design evidence として次へ進める。ただし production/public flags は false/pending 維持。
- `adjust_boundary`: 文字サイズ、outline、safe area、mode selection、speaker identity fallback、wrapping などの指定箇所を修正して再 proof。
- `reject`: この字幕方向は代表 evidence として不採用。
- `blocked_missing_artifact`: 必要な proof / source media / ignored artifact が不足しているため判断不可。
- `blocked_missing_dense_stress_proof`: `cut_008` など dense/stress evidence がないため、代表範囲を広げる前に別スライスが必要。

### Human Response Consumed

Human response: `adjust_boundary`

The review accepted the current font-size direction only within the diagnostic
/ representative review route. The response does not approve production
subtitle design, production render, creative quality, rights, publishing,
public use, or upload.

| Axis | Decision readback | Next effect |
|---|---|---|
| `font_size` | `accepted_for_diagnostic_representative_review` | Preserve the current formula-derived size for the next diagnostic comparison proof. |
| `font_family` | `unresolved_needs_comparison` | Compare Japanese font-family candidates before regenerating the next overlay proof direction. |
| `decoration` | `unresolved_needs_comparison` | Compare outline, shadow, and placeholder speaker-badge accent treatment. |

The successor packet is
[SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md](SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md)
with artifact id `clip-typography-decoration-comparison-001`.

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

## Human Preview Session

The current human-facing entry point for the `cut_002` / `cut_003`
representative subtitle design review is:

`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/index.html`

Generate or refresh it with:

```powershell
uvx python -m src.cli.main build-human-preview-session `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

The generated session includes `review_manifest.json`, `decision_request.json`,
`decision_template.json`, `open_preview.ps1`, `serve_preview.ps1`, and copied
review assets under `assets/`. It is diagnostic / representative review only;
it does not accept production subtitle design, production render, creative
quality, rights, publishing, public use, or upload.

## Smallest Next Slice

The narrowest next action is parser-first review of the combined `cut_002` /
`cut_003` diagnostic proof surface, followed by one targeted human visual
question only if needed. The minimum visual file is
`subtitle_overlay_visual_proof_report.html`; the question is whether the
current `badge_left_dialogue` diagnostic presentation is acceptable as
representative subtitle design evidence for the kept proof surfaces. Keep the
decision limited to subtitle design/readability review and keep
production/public flags false or pending.

The next proof expansion, if needed, is a separate `cut_008` adjustment/stress
route after its `needs_adjustment` state is explicitly handled.
