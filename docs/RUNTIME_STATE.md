# Runtime State - ClipPipeGen

This file is the active resume surface. It should answer "where are we now?"
without requiring the reader to scan historical closeouts.

Long historical closeouts moved to [RUNTIME_HISTORY.md](RUNTIME_HISTORY.md).
Do not treat archived lane/slice labels or old action wording as current
instructions.

## Current Resume Capsule

- date: 2026-06-04 JST
- latest pushed resume point:
  current `main` after the 2026-06-04 representative visual proof reviewability
  correction; confirm with `git log -1 --oneline --decorate`.
- previous pushed resume point:
  `21f7792 feat: add R3 proxy decision handoff generator`
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
  A scoped 2026-06-04 Verify regenerated local diagnostic subtitle-overlay
  proof for `cut_002` / `cut_003` only. The refreshed
  `representative_visual_proof_report.*`, `visual_proof_cut_002.png`,
  `visual_proof_cut_003.png`, and `visual_proof_contact_sheet.png` exist, but
  `visual_proof_cut_001.png` is missing. Global status remains
  `review_blocked_missing_artifacts`; this is not `review_ready`.
- latest local proxy decision handoff:
  ED-10d adds the tracked `build-operator-proxy-decision-handoff` CLI and
  generator. `cut_002` / `cut_003` now have ignored text/proxy review files,
  operator proxy decision handoff files, and scoped Chapter Revision Patch
  templates. They preserve operator fields as blank, `undecided`, `noop`, or
  `none`, keep `cut_003` retained context risk, and read back source media as
  available from `material_ledger.json`. This handoff predates the narrow
  `cut_002` / `cut_003` overlay Verify and still must not be treated as
  operator decision, creative acceptance, or production acceptance.
- current bottleneck: missing `visual_proof_cut_001.png` blocks the original
  representative visual proof set. The next operator-facing surface is the
  scoped `representative_visual_proof_report.html` for `cut_002` / `cut_003`
  inspection, not `cut_review_report.html` as a global review-ready surface.
- reviewability rule: if the refreshed representative visual proof report
  records `review_blocked_missing_artifacts`, `status-episode` must also report
  `review_blocked_missing_artifacts` until the missing proof is resolved or
  explicitly waived by an operator decision.
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

On 2026-06-04 JST, ED-10d made the scoped `cut_002` / `cut_003`
text/proxy decision handoff reproducible from tracked code and regenerated the
ignored local artifacts:

- `cut_002_cut_003_text_proxy_review.json` / `.html`
- `cut_002_cut_003_operator_proxy_decision_handoff.json` / `.html`
- `chapter_revision_patch.cut_002_cut_003_proxy.template.json` / `.csv`

These files are also ignored local artifacts under the same R3 review
directory. They record `source_media_status=available_from_material_ledger` for
`materials/src_video_jp_pilot01/source_video.mp4` and
`materials/src_audio_jp_pilot01/source.wav`, while preserving
`visual_proof_status=blocked_no_cut_002_cut_003_overlay_proof`. The older
root-level source media paths are not the current source of truth. This handoff
does not create production, creative, publishing, rights, typography,
safe-area, or timing acceptance.

Later on 2026-06-04 JST, a narrow Verify regenerated diagnostic subtitle-overlay
proof only for `cut_002` / `cut_003`. It used existing source media from
`material_ledger.json` and JSON-readable upstream inputs `edit_pack.json`,
`cut_decision_packet.json`, and `chapter_revision_board.json`. The generated
local ignored artifacts are:

- `representative_visual_proof_report.json` / `.html`
- `visual_proof_cut_002.png`
- `visual_proof_cut_003.png`
- `visual_proof_contact_sheet.png`

`visual_proof_cut_001.png` remains missing and was not regenerated by the
narrow instruction. The refreshed report records
`scope=cut_002_cut_003_diagnostic_subtitle_overlay_verify`,
`proof_generation_succeeded=true`, `restore_succeeded=false`,
`review_state=review_blocked_missing_artifacts`, `rights_status=pending`, and
`production_candidate=false`. This is local diagnostic overlay evidence only;
it is not production render acceptance, subtitle design acceptance, creative
acceptance, publishing acceptance, rights approval, or public-use permission.

Regenerate them, when the required local R3 artifacts are present, with:

```powershell
uvx python -m src.cli.main build-operator-proxy-decision-handoff `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

## What To Read First

When the refreshed representative visual proof report records
`review_blocked_missing_artifacts`, start with this scoped surface:

1. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html`

Use it only for visual inspection of the regenerated `cut_002` / `cut_003`
diagnostic overlay frames. Do not send the operator to `cut_review_report.html`
as if the workspace were globally `review_ready`.

When the missing `cut_001` proof issue is resolved or explicitly waived, and
the R3 review artifacts are otherwise present, use the local ignored review
reports in this order:

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

1. Review: scoped representative diagnostic visual proof
   - Open `representative_visual_proof_report.html` for `cut_002` / `cut_003`.
   - Confirm only local diagnostic readability / safe-area / timing impressions.
   - Keep `review_ready=false`, `rights=pending`, and
     `production_candidate=false`.
2. Resolve or waive: missing `visual_proof_cut_001.png`
   - Regenerate the missing diagnostic proof or record an explicit operator
     waiver before opening the global operator review gate.
3. Advance: `cut_002` / `cut_003` operator proxy decision
   - After scoped visual inspection, use
     `cut_002_cut_003_operator_proxy_decision_handoff.html` and the scoped patch
     templates for routing decisions.
   - Operator-owned fields remain blank / `undecided` until the operator fills
     them.
4. Advance: adjustment loop for retained R3 cuts
   - Use for `cut_004` through `cut_008`.
   - Review boundaries, density, and whether any cut should merge/split before
     it can re-enter candidate status.
5. Verify: regenerated render comparison
   - Use when a workspace must compare regenerated diagnostics to prior R3
     artifacts.
   - Define when exact SHA-256 matters and when metadata approximate comparison
     is acceptable.
6. Clear Rights: rights approval path
   - Use before any production/public usage claim.
   - Keep this separate from local diagnostic success.
7. Prepare: publishing / OAuth / thumbnail
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
