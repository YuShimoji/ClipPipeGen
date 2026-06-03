# Runtime State - ClipPipeGen

This file is the active resume surface. It should answer "where are we now?"
without requiring the reader to scan historical closeouts.

Long historical closeouts moved to [RUNTIME_HISTORY.md](RUNTIME_HISTORY.md).
Do not treat archived lane/slice labels or old action wording as current
instructions.

## Current Resume Capsule

- date: 2026-06-03 JST
- latest resume-surface cleanup:
  `f725197 docs: update runtime resume commit readback`
- previous runtime docs refresh:
  `28f0256 docs: refresh operator review handoff`
- latest operator review implementation:
  `3d97e45 feat: improve operator review surfaces`
- latest chapter revision implementation:
  Chapter Revision Loop v0 adds a static board and JSON/CSV patch templates
  for R3 chapter-level operator decisions.
- latest cut decision implementation:
  R3 Cut Decision Packet classifies the 9 selected cuts into keep /
  needs_adjustment / reject and exposes `final_cut_decision` in
  `status-episode`.
- latest local visual proof readback:
  JP-Pilot R3 kept cuts now have local ignored acceptance/readback reports for
  `cut_001` through `cut_003`. `cut_001` has an existing diagnostic render frame
  with subtitle overlay; `cut_002` and `cut_003` have source-frame-only proof
  and still need subtitle-overlay representative diagnostic evidence.
- current bottleneck: representative diagnostic proof with subtitle overlay for
  `cut_002` / `cut_003`, plus human review of `cut_001` readability,
  safe-area, and timing; rights remain pending before any production/public use
- reviewability rule: if the ignored R3 review artifacts are present, report
  `review_ready`; if they are missing, report
  `review_blocked_missing_artifacts`
- rights: `pending`
- production_candidate: `false`

ED-10 solved the caption-completeness blocker for this source by importing the
official YouTube JSON3 subtitle track into a transcript-compatible artifact.
SH-07 then made the operator review path Reviewability-first. On 2026-05-30
JST, the operator explicitly bypassed strict individual R3 cut review for
speed-first sample expansion. All 9 generated R3 cuts are accepted only as
`accept_candidate` candidate seeds; the 6 `needs_review` context results remain
retained risk and are not rewritten to `passed`.

Chapter Revision Loop v0 now gives those 9 candidate seeds stable chapter ids
`ch_001` through `ch_009` and keeps operator-written intent separate from the
source transcript and official subtitle track.

On 2026-06-02 JST, the operator advanced from speed-first sample expansion to
candidate triage. `cut_001`, `cut_002`, and `cut_003` are kept only as
candidates for the next acceptance slice. `cut_004` through `cut_008` are
`needs_adjustment`; `cut_009` is rejected. `cut_003` keeps its original
`needs_review` context status and requires the recorded manual override reason.
This is still not production acceptance, creative acceptance, publishing
acceptance, or rights approval.

On 2026-06-03 JST, local ignored reports were created for the kept candidate
mini-slice:

- `production_subtitle_render_acceptance_report.json` / `.html`
- `representative_visual_proof_report.json` / `.html`
- `visual_proof_cut_001.png`
- `visual_proof_cut_002.png`
- `visual_proof_cut_003.png`
- `visual_proof_contact_sheet.png`

These are under
`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/`
and are intentionally not in Git. The readback is conservative: `cut_001` has
subtitle-overlay diagnostic-frame evidence only, while `cut_002` and `cut_003`
are source-frame-only and do not prove subtitle typography, safe-area, line
wrapping, or timing sync. `cut_003` keeps retained context risk.

## What To Read First

When the R3 review artifacts are present, start with the local ignored review
reports in this order:

1. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_review_report.html`
2. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/evidence_summary.html`
3. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/non_repo_artifact_handoff.html`
4. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_speed_pass.html`
5. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_report.html`
6. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/production_subtitle_render_acceptance_report.html`
7. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html`
8. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_board.html`

In that state, the review artifacts are readable and the speed-first candidate
decision can be confirmed from `cut_decision_speed_pass.json` / `.html`. This
decision is sample expansion only, not production, creative, publishing, or
rights acceptance.

If `chapter_revision_board.html` is present, it is the operator working board
for chapter-level decisions. The corresponding templates are
`chapter_revision_patch.template.json` and
`chapter_revision_patch.template.csv`; defaults are blank or `undecided`.

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

1. Verify: representative diagnostic visual proof
   - Use for `cut_002` and `cut_003`, which currently have source-frame-only
     proof and no subtitle overlay.
   - Generate or inspect diagnostic subtitle-overlay evidence without claiming
     production render or production acceptance.
2. Review: kept cut visual proof readback
   - Use for `cut_001`, which has a diagnostic subtitle-overlay frame.
   - Human review should record readability, safe-area, and timing judgment
     while keeping `production_candidate=false`.
3. Advance: adjustment loop for retained R3 cuts
   - Use for `cut_004` through `cut_008`.
   - Review boundaries, density, and whether any cut should merge/split before
     it can re-enter candidate status.
4. Verify: regenerated render comparison
   - Use when a workspace must compare regenerated diagnostics to prior R3
     artifacts.
   - Define when exact SHA-256 matters and when metadata approximate comparison
     is acceptable.
5. Clear Rights: rights approval path
   - Use before any production/public usage claim.
   - Keep this separate from local diagnostic success.
6. Prepare: publishing / OAuth / thumbnail
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
   commands.
3. Keep `rights=pending` and `production_candidate=false` visible.
4. Do not classify final cuts without explicit operator instruction. The
   2026-05-30 speed-first instruction applies only to candidate seeds, not
   production-approved cuts.
5. If the Chapter Revision Board exists, treat `script_override` as editorial
   layer only and do not add source transcript mutation fields.
6. Do not stage `episodes/`, source media, rendered video, subtitle payloads, or
   other large local artifacts.
