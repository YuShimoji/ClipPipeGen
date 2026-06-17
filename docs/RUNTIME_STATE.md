---
id: runtime-state
title: Runtime State - ClipPipeGen
type: resume_surface
status: current_capsule
health: active
progress_pct: 80
last_touched: 2026-06-16
next_review_due: before_dense_stress_or_limitation_lift
active_artifact: clip-ed10g-noto-overlay-proof-001
source_of_truth: true
owner_lane: shared_infra
related: docs/index.md, docs/dashboard/project-status.json, docs/SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md, docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md
---

# Runtime State - ClipPipeGen

This file is the active resume surface. It should answer "where are we now?"
without requiring the reader to scan historical closeouts.

Long historical closeouts moved to [RUNTIME_HISTORY.md](RUNTIME_HISTORY.md).
Do not treat archived lane/slice labels or old action wording as current
instructions.

## What This Is

This is the current resume capsule for ClipPipeGen. It is not the full
history; it is the first page to read when deciding what artifact is active,
what human judgement has already been consumed, and which narrow route can move
next.

Older closeouts stay below as temporary notes or in
[RUNTIME_HISTORY.md](RUNTIME_HISTORY.md). The capsule below is authoritative
for restart decisions.

## Current Capsule

Active artifact: `clip-ed10g-noto-overlay-proof-001`

Current judgement: the `noto_sans_jp_clean_outline` proof for `cut_002` /
`cut_003` is accepted as the current diagnostic / representative subtitle
base. This consumes the human visual judgement for this proof only.

Current proof readback:

- target cuts: `cut_002`, `cut_003`
- selected base: `noto_sans_jp_clean_outline`
- size rule: `round(frame_height * 0.115)`; readback `font_size=124`
- outline rule: `max(2, round(font_size * 0.086))`; readback `outline=11`
- font route: `Noto Sans JP`; `font_file_status=candidate_primary_font_file_found`
- overlay coverage: `all_target_cuts_have_overlay=true`

This acceptance is not production subtitle design acceptance and does not lift
production render, creative, rights, publishing, upload, or public-use gates.

## Next

1. Treat ED-10g as accepted for the diagnostic base and do not reopen
   `noto_sans_jp_clean_outline` unless a new visual defect is found.
2. If representative coverage must widen, create a separate dense/stress proof
   route for `cut_008` or another explicitly scoped target.
3. If moving toward production/public use, run a separate limitation-lift route
   for production render, rights, publishing, and public-use decisions.

## Constraints / Risks

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `production_candidate=false`
- `production_usage_allowed=false`
- `rights_status=pending`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `episodes/` remains ignored same-machine evidence and must not be staged.
- Font binaries are not vendored unless license metadata and repo policy are
  explicitly approved.

## Navigation

- Human-readable entry: [index.md](index.md)
- Static dashboard: [dashboard/index.html](dashboard/index.html)
- Machine-readable dashboard: [dashboard/project-status.json](dashboard/project-status.json)
- Feature table: [features/index.md](features/index.md)
- Artifact registry: [../artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md)

Repo-root launcher order for a fresh terminal:

1. `.\open-dashboard.ps1`
2. choose the artifact or doc from the dashboard
3. use artifact-specific launchers only when needed:
   `.\open-artifacts.ps1`, `.\open-current-proof.ps1`, or
   `.\open-font-candidates.ps1`

Regenerate the docs dashboard with:

```powershell
uvx python -m src.cli.main build-docs-dashboard --format json
```

## Implementation Notes

`episodes/` は同端末 review evidence であり、public Git の authority では
ありません。tracked docs/code/tests が remote evidence、ignored local reports
が same-machine readback です。Dashboard は tracked Markdown と registry を
読むだけで、source media や production acceptance を変更しません。

## Decision Log

- 2026-06-16: ED-10g の selected proof base を
  `noto_sans_jp_clean_outline` として保持し、次の font universe 拡張を
  `ED-10h` として切り出す。
- 2026-06-16: Human visual judgement accepted
  `clip-ed10g-noto-overlay-proof-001` as the diagnostic / representative base
  for `cut_002` / `cut_003`; production/public/rights gates remain closed.
- 2026-06-16: Review surface launchers added and pushed. Normal open order is
  `.\open-dashboard.ps1`, then dashboard artifact selection, then
  artifact-specific launchers only when needed. This records navigation only;
  it does not mutate source media, transcript, official subtitle evidence,
  rights, publishing, upload, or production acceptance state.
- 2026-06-16: docs を v1.5 Wiki / Dashboard 入口へ寄せ、通常報告では
  next-Agent prompt を付けない運用へ戻す。

## Changelog

- 2026-06-16: Added v1.5 metadata and dashboard-facing front sections.
- 2026-06-16: Added repo-root open surface launchers and dashboard/artifact
  open command readback.

## Historical Resume Notes

Detailed historical resume notes were moved to [RUNTIME_HISTORY.md](RUNTIME_HISTORY.md)
on 2026-06-17 JST under `Archived Runtime Resume Notes - 2026-06-17`.
This page keeps the current capsule, current read order, candidate decision,
source identity, boundaries, next actions, and restart checklist.

## What To Read First

When this same-machine workspace has the ignored R3 reports and visual proof
artifacts, `status-episode` reports `review_ready`. Use the review reports in
the order below, and inspect the scoped overlay proof before filling the
`cut_002` / `cut_003` proxy decision fields.

If the refreshed representative visual proof report records
`review_blocked_missing_artifacts`, start with this scoped surface instead:

1. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html`

Use it only for visual inspection of the regenerated or partial diagnostic
overlay frames. Do not send the operator to `cut_review_report.html` as if the
workspace were globally `review_ready` while the report records a blocked
state.

When the representative proof artifacts are present or an explicit operator
waiver exists, and the R3 review artifacts are otherwise present, use the local
ignored review reports in this order:

1. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_review_report.html`
2. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/evidence_summary.html`
3. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/non_repo_artifact_handoff.html`
4. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_speed_pass.html`
5. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_report.html`
6. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/production_subtitle_render_acceptance_report.html`
7. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_text_proxy_review.html`
8. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_operator_proxy_decision_handoff.html`
9. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html`
10. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_board.html`

In that state, the review artifacts are readable and the speed-first candidate
decision can be confirmed from `cut_decision_speed_pass.json` / `.html`. This
decision is sample expansion only, not production, creative, publishing, or
rights acceptance.

If `chapter_revision_board.html` is present, it is the operator working board
for chapter-level decisions. The corresponding templates are
`chapter_revision_patch.template.json` and
`chapter_revision_patch.template.csv`; defaults are blank or `undecided`.
When the scoped proxy templates are present, use
`chapter_revision_patch.cut_002_cut_003_proxy.template.json` / `.csv` for the
first `cut_002` / `cut_003` operator decision pass instead of asking the
operator to fill all 9 chapters at once.

When this is a fresh checkout or those ignored reports are missing, do not send
the operator to the HTML report as if review is ready. Read these instead:

1. [OPERATOR_REVIEW_UX.md](OPERATOR_REVIEW_UX.md)
2. [NON_REPO_ARTIFACT_HANDOFF.md](NON_REPO_ARTIFACT_HANDOFF.md)
3. the restore or regenerate route recorded in the non-repo handoff docs and
   generated manifests

Git alone does not contain `episodes/` artifacts, source media, render outputs,
or R3 review reports.

## Current Candidate Decision

The current cut decision packet classifies the 9 R3 cuts into:

- `keep`: `cut_001`, `cut_002`, `cut_003`
- `needs_adjustment`: `cut_004`, `cut_005`, `cut_006`, `cut_007`, `cut_008`
- `reject`: `cut_009`

The earlier speed-first sample expansion carried all 9 R3 cuts forward as
`accept_candidate` candidate seeds. The newer triage narrows the next acceptance
slice to 3 kept candidates. It does not resolve the 6 context `needs_review`
results; `cut_003` is kept with a manual override reason and the remaining
`needs_review` cuts stay in `needs_adjustment`. This is not production
acceptance, creative acceptance, publishing acceptance, or rights approval.

Absent an explicit operator instruction like the one above, the Agent must not
auto-accept, auto-reject, or auto-adjust final cuts.

Review focus:

- previous setup: does the cut start with enough context?
- following payoff: does the cut end before the useful response lands?
- boundary adjustment: would a small start/end shift make the cut usable?

## Source Identity

- YouTube ID: `7J5aS_pcBj4`
- subtitle track: `source_subs/7J5aS_pcBj4.ja.json3`
- transcript source: imported subtitle track / `youtube_subtitles`
- source video material id: `src_video_jp_pilot01`
- source audio material id: `src_audio_jp_pilot01`
- source video material path:
  `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4`
- source audio material path:
  `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav`
- rights status: `pending`
- production usage: not allowed until approval
- source URL: `https://www.youtube.com/watch?v=7J5aS_pcBj4`
  (from existing local docs metadata; do not access YouTube to refresh it)
- source title: unknown for this resume surface. Existing local docs preserve a
  title readback, but it is not refreshed here and should not be filled by
  external search.

## Boundaries

- Diagnostic render is not production, creative, or publish acceptance.
- Rights pending means production/public use is not allowed.
- `rendered_video.mp4`, source video/audio, subtitle track payloads, and
  episode artifacts must not be added to Git.
- `episodes/` is intentionally ignored.
- `build-non-repo-handoff` creates a manifest/report. It is not a render
  command and does not recreate `rendered_video.mp4`.
- Production render, publishing, OAuth, thumbnail setting, and rights approval
  are separate slices.
- R3 final cut review creates candidate seeds only; it does not make a
  production candidate.

## Next Actions

1. Advance: ED-10g small-adjustment diagnostic overlay proof route
   - `small_adjustment` and the follow-up choice of
     `noto_sans_jp_clean_outline` have been consumed for
     `clip-typography-decoration-comparison-001`.
   - Preserve the accepted diagnostic font-size direction
     `round(frame_height * 0.115)`.
   - Use
     [SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md](SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md);
     the adjusted `cut_002` / `cut_003` overlay proof is generated and ready
     for human visual judgement.
   - Do not reopen font size. If the proof needs revision, keep it to one
     bounded font-family / decoration adjustment or choose an alternate
     candidate route.
   - Keep `rights=pending`, `production_candidate=false`,
     `production_usage_allowed=false`, and all production/public acceptance
     flags false.
2. Audit: current reviewability and report readback
   - Parse `status-episode` plus current JSON/HTML/CSV/SRT reports before
     asking the operator to open files.
   - If human visual inspection is needed, list the minimum file set and the
     exact question. Do not ask the operator to hunt through generated
     artifacts.
3. Advance: `cut_002` / `cut_003` operator proxy decision
   - `cut_002` is already in the candidate lane with
     `proxy_decision=proceed_with_limitations`; keep the long-line watch risk
     visible.
   - `cut_003` proxy decision is closed locally from the accepted filled
     `.operator.*` patch:
     `proxy_decision=proceed_with_limitations`,
     `context_risk_handling=keep_retained_risk_visible`; keep subtitle
     design/readability as a separate unaccepted limitation.
4. Advance: adjustment loop for retained R3 cuts
   - Use for `cut_004` through `cut_008`.
   - `cut_004` has been explicitly shrunk to start at `50.868s` and remains a
     resegmentation target before it can re-enter candidate status.
5. Verify: final render-path output or regenerated render comparison
   - Use when a workspace must compare regenerated diagnostics to prior R3
     artifacts.
   - Define when exact SHA-256 matters and when metadata approximate comparison
     is acceptable.
6. Review: editorial representative-sequence quality
   - Keep this separate from subtitle design/readability and render-path
     output acceptance.
7. Clear Rights: rights approval path
   - Use before any production/public usage claim.
   - Keep this separate from local diagnostic success.
8. Prepare: YMM4/Premiere handoff, publishing / OAuth / thumbnail, or GUI work
   - Keep this later until production acceptance and rights are no longer
     pending.

Publishing and OAuth work remain later; do not treat them as the immediate next
step.

## History / Archive Links

- Full historical closeouts:
  [RUNTIME_HISTORY.md](RUNTIME_HISTORY.md)
- Feature state:
  [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
- Operator response shape and reviewability states:
  [OPERATOR_REVIEW_UX.md](OPERATOR_REVIEW_UX.md)
- Non-repo artifact recovery and handoff boundary:
  [NON_REPO_ARTIFACT_HANDOFF.md](NON_REPO_ARTIFACT_HANDOFF.md)

## Restart Checklist

1. Check whether the R3 review artifacts exist in the ignored `episodes/`
   directory.
2. Report `review_ready` or `review_blocked_missing_artifacts` before listing
   commands, and parse current report artifacts before asking the operator to
   open files.
3. Keep `rights=pending` and `production_candidate=false` visible.
4. Do not classify final cuts without explicit operator instruction. The
   2026-05-30 speed-first instruction applies only to candidate seeds, not
   production-approved cuts.
5. If human inspection is required, list the minimum file set and exact
   question being answered.
6. If the Chapter Revision Board exists, treat `script_override` as editorial
   layer only and do not add source transcript mutation fields.
7. Do not stage `episodes/`, source media, rendered video, subtitle payloads, or
   other large local artifacts.
