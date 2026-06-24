---
id: runtime-state
title: Runtime State - ClipPipeGen
type: resume_surface
status: current_capsule
health: ed10z_tiny_render_path_nearer_probe_ready
progress_pct: 100
last_touched: 2026-06-24
next_review_due: none_probe_readback_only
active_artifact: clip-ed10z-tiny-render-path-nearer-probe-001
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

Active artifact: `clip-ed10z-tiny-render-path-nearer-probe-001`

ED-10z current checkpoint, 2026-06-24 JST: the active artifact is now
`clip-ed10z-tiny-render-path-nearer-probe-001`. It preserves
`clip-ed10y-candidate2-carry-forward-001` as the source/previous artifact and
passes Candidate 2 (`ed10w_badge_label_pressure_adjustment`) through the
current FFmpeg/libass diagnostic path as a tiny render-path-nearer probe.
Candidate 0 remains fallback/reference, Candidate 1 and Candidate 3 remain
held because the consumed review says they read too thin, and the Candidate
0-3 comparison is closed. This is local diagnostic readback only; it does not
approve production subtitle design, production render, creative use, rights,
publishing, or public use. The next valid movement is a separate production
limitation-lift, final render-path, or policy/readback route, not another
review card for the same candidates.

This turn's actual non-dry-run proof materialization is blocked by the local
tool environment: `ffprobe` is not on PATH and `CLIPPIPE_FFPROBE` is unset.
The ED-10z dry-run and targeted fake-runner tests validate the profile/artifact
route, but ignored local HTML/JSON/PNG/MP4 proof files need FFmpeg/FFprobe
provided through PATH, env, or explicit CLI paths before they can be refreshed.

ED-10y implementation checkpoint, 2026-06-24 JST: commit `0cf35da` was pushed
to `origin/main` and local/remote parity was verified with
`git rev-list --left-right --count "HEAD...origin/main"` -> `0 0`. This
implementation checkpoint includes the ED-10y Candidate 2 carry-forward
generator/profile changes, dashboard/doc refresh, launcher update, and
targeted validation. This handoff note is part of a later successor commit, so
a fresh terminal should `git pull --ff-only`, read this file, then use
`docs/CURRENT_HANDOFF.md` and `artifacts/ARTIFACTS.md` for the compact restart
packet. Keep `episodes/` as ignored same-machine evidence; `git ls-files
episodes` must remain empty.

Previous handoff checkpoint, 2026-06-24: ED-10y has consumed the latest
freeform review of the ED-10w/ED-10x subtitle presentation pack. Candidate 2
(`ed10w_badge_label_pressure_adjustment`) is now the provisional
bounded-decoration lead. Candidate 0 (`ed10w_current_pass_reference`) remains
the fallback/current-baseline reference. Candidate 1 and Candidate 3 are held
for the current path because the review says they look too thin compared with
0 and 2.

The current `subtitle_presentation_review_pack.html` path is still the root
launcher target, but it is no longer asking for the same Candidate 0-3 review.
It is a Candidate 2 carry-forward/readback surface with Candidate 2 lead and
Candidate 0 fallback visible at a glance, larger full-frame detail views, and a
tiny Candidate 2 diagnostic render-path-nearer probe. The probe remains
diagnostic only; it does not approve production subtitle design, production
render, creative use, rights, publishing, or public use.

Previous handoff checkpoint, 2026-06-23: ED-10w was the review surface before
the ED-10y review consumption. It packaged one new review axis after the ED-10v
diagnostic pass: bounded
subtitle decoration adjustment plus render-path readiness. The pack is generated
as
`episodes/.../subtitle_presentation_review_pack.html` and is opened by
`.\open-current-proof.ps1` when the ignored local artifact is present. The older
ED-10r/ED-10v `current_proof_focused_review.html` remains retained source
evidence and launcher fallback, not the primary review request.

ED-10x consumes the latest review of that pack: Candidate 0-3 images were
visible and reviewed in order, but the visual differences were almost
indistinguishable. Treat the previous candidate image generation as technically
working but not reviewable enough. The current regenerated pack keeps the same
artifact/path and makes the deltas visible with compact subtitle-body crops,
compact SPK badge crops, and actual style parameter delta readback.

The ED-10w Review Card asks for one freeform judgement on four bounded
presentation candidates:

- `ed10w_current_pass_reference`
- `ed10w_lighter_outline_shadow_pressure`
- `ed10w_badge_label_pressure_adjustment`
- `ed10w_balanced_combined_low_risk`

It also includes a render-path readiness decision card. That card is a
diagnostic planning/readiness probe only; it does not approve production
subtitle design, production render, creative use, rights, publishing, or public
use. ED-10w does not read, edit, import from, or extract a shared package with
NLMYTGen.

Current handoff checkpoint, 2026-06-22: ED-10q has been consumed as a
page-format regression fix, not as a new Keifont font-quality review. The
Keifont review history is already sufficient for the next diagnostic step:
the user judged the Keifont proof clearly improved and video-usable, and also
judged the ED-10o font/review screen easier to see. Do not ask for another
general Keifont acceptance pass on `cut_002` / `cut_003`. Treat
`ed10l_keifont_pop_dialogue_candidate` as a diagnostic representative
normal-dialogue provisional baseline, while keeping production subtitle design,
production render, creative acceptance, rights, publishing, and public-use
gates false or pending.

The active route is ED-10v: the ED-10u corrected dense/stress proof has now
been reviewed and passed. The proof profile remains
`ed10r_keifont_dense_stress_proof`, and it is intentionally narrow: it only
accepts `--target-cut cut_008`. The current Windows profile resolves Keifont
correctly, with `font_visual_evidence.status=valid_requested_keifont_visual_evidence`,
`requested=Keifont`, `resolved=Keifont`, and
`font_file_status=candidate_primary_font_file_found`.

ED-10u inspected the generated cut and found that `cut_008` does contain one
real multiline/wrap cue: `sub_096`, displayed at `8.008-9.776`, wrapping as
`下界ニ呼ビ出シタノハキサ` / `マカ。`. The earlier focused page did not surface a
frame from that cue, so the user could not reasonably judge multiline behavior.
`current_proof_focused_review.html` now places a `Multiline / Wrap Evidence`
section near the top, before the broader evidence, with a compact screenshot
for `sample_multiline_wrap_1.png` capped at 220px by default.

ED-10v consumes the latest user review of that corrected surface: subtitle
display is good, all pass. This is accepted only as a diagnostic
dense/stress + multiline/wrap pass for the current Keifont subtitle route. Do
not emit another Review Card for the same `cut_008` evidence and do not reopen
general Keifont acceptance on `cut_002` / `cut_003`. Future work may refine
line-break behavior as more material appears, but that should be handled as a
policy/readback or bounded adjustment slice, not as a replay of the current
review.

Review Memory Ledger: Keifont normal-dialogue direction has `prior_review_count=3+`
and is accepted only as `diagnostic_representative_review` /
`provisional_normal_dialogue_baseline` plus
`diagnostic_dense_stress_pass`. It is not accepted for production subtitle
design, production render, creative acceptance, rights, publishing, or public
use. The current dense/stress axis is closed as diagnostic pass. Next
non-redundant axes are line-break policy readback, bounded decoration
adjustment, future shared subtitle layout policy, production limitation-lift,
or render-path probe.

Remote handoff checkpoint, 2026-06-19: if a pasted or queued prompt asks to
generate `clip-ed10k-biz-overlay-proof-001`, treat that prompt as stale unless
the user explicitly says to rewind. ED-10k is already generated, reviewed, and
rejected as the normal-dialogue baseline. Continue from ED-10o multi-font
focused review instead.

Current judgement: the ED-10k BIZ UDGothic overlay proof has now been reviewed
and is not accepted as the normal-dialogue subtitle baseline. The review says
the BIZ route feels too hard/rigid, the text still reads thin, and the black
outline pressure is too strong. This also rejects the broader BIZ/Noto/Meiryo
system-safe route for this use case. BIZ remains a reviewed reference, not the
current baseline.

The prior active route, ED-10q, restored `current_proof_focused_review.html`
after the root launcher appeared to open the old detailed/debug report layout.
That fix remains valid, but it is historical. Its purpose was review-surface
repair, not a re-vote on Keifont quality.

ED-10l route readback:

- target cuts: `cut_002`, `cut_003`
- comparison profile: `ed10l_known_kirinuki_font_pack`
- active artifact: `clip-ed10l-known-kirinuki-font-pack-001`
- normal-dialogue candidates:
  `ed10l_keifont_pop_dialogue_candidate`,
  `ed10l_851_chikara_yowaku_dialogue_candidate`,
  `ed10l_m_plus_fonts_dialogue_candidate`,
  `ed10l_yasashisa_gothic_goodfreefonts_candidate`
- separate emphasis/shout slot: `ed10l_851_chikara_zuyoku_emphasis_candidate`
- separate mood/literary slot:
  `ed10l_source_han_serif_mood_candidate`,
  `ed10l_shippori_mincho_mood_candidate`
- size rule: keep `round(frame_height * 0.115)` as a comparison constant
- local availability basis: HKCU registry, `%LOCALAPPDATA%/Microsoft/Windows/Fonts`,
  and `C:/Windows/Fonts`
- ED-10n regenerated samples are valid requested-font visual evidence on this
  same machine; earlier fallback-only samples remain historical readback only
- latest ED-10l review was consumed as a fallback suspicion, not as a candidate
  preference: all visible candidates looked too thin / close to BIZ because the
  target fonts were not actually resolving
- current ED-10n sample readback confirms all four normal-dialogue candidates
  resolved to requested per-user font files with
  `candidate_primary_font_file_found`
- Keifont resolved to
  `C:/Users/thank/AppData/Local/Microsoft/Windows/Fonts/keifont.ttf`, and
  `clip-ed10n-keifont-overlay-proof-001` was generated as the current review
  proof
- M PLUS resolved via registry as `M PLUS 1 Thin` /
  `MPLUS1-VariableFont_wght.ttf`; do not treat it as a winner until exact
  weight/style is pinned
- ED-10o excludes M+ from the one-shot baseline comparison with
  `reason=weight_style_unresolved`
- ED-10o focused review surface uses rows as sample lines and columns as font
  candidates, with subtitle-area crops as the primary visual
- ED-10o human review was consumed as:
  `focused_review_surface_accepted_as_review_direction`
- ED-10p generated `clip-ed10p-keifont-lead-representative-proof-001` using
  `ed10l_keifont_pop_dialogue_candidate`; it is now consumed as provisional
  normal-dialogue baseline evidence
- ED-10q fixed the current-proof launcher/page regression: `.\open-current-proof.ps1`
  now opens `episodes/.../current_proof_focused_review.html`, where Review
  Focus and subtitle-area evidence appear before detailed/debug reports
- ED-10r owns `cut_008` as the current dense/stress proof route; do not replay
  general Keifont review on `cut_002` / `cut_003`
- ED-10t regenerated the ED-10r proof after PLANNER007 installed Keifont; the
  current report reads `requested=Keifont`, `resolved=Keifont`, and
  `font_visual_evidence.status=valid_requested_keifont_visual_evidence`
- ED-10u consumed the user's note that the visible proof did not show two-line
  subtitles, kept `cut_008` as the correct target because font-bbox readback
  found `sub_096` wrapping to two lines, and added compact multiline screenshot
  evidence near the top of `current_proof_focused_review.html`
- ED-10v consumed the user's pass review of that corrected surface; no further
  Review Card should be emitted for the same `cut_008` evidence unless a new
  axis or changed evidence is introduced
- line-break policy/readback is now recorded in
  `docs/SUBTITLE_PRESENTATION_CONTRACT.md`; future NLMYTGen sharing is only a
  design consideration in this slice, with no NLMYTGen reads, edits, imports,
  or shared package extraction
- no font binary was downloaded, installed, copied, vendored, staged, or
  committed by Codex; local font files remain same-machine evidence only

Tracked self-diagnosis: the previous exploration over-weighted
system-safe/generic readable fonts, conflated safe/reproducible with visually
strong kirinuki design, did not elevate user known-good domain knowledge early
enough, and treated general font documentation as sufficient for telop needs.
ED-10l corrects that by separating design suitability from license/install/
reproducibility notes.

This audit/proof chain is not production subtitle design acceptance and does
not lift production render, creative, rights, publishing, upload, or public-use
gates.

## Next

1. Continue from `clip-ed10z-tiny-render-path-nearer-probe-001`: Candidate 2
   has now passed the current diagnostic render path as a tiny readback probe.
   Do not ask for another Candidate 0-3 comparison review.
2. Preserve `clip-ed10y-candidate2-carry-forward-001` as source/previous
   evidence. Treat ED-10z as diagnostic readback only, not production render
   acceptance. Rerun the ED-10z command after FFmpeg/FFprobe paths are
   available to materialize ignored local proof files.
3. Do not request another Review Card for the same ED-10u `cut_008`
   multiline/dense-stress evidence; ED-10v already records it as diagnostic
   pass.
4. If subtitle work continues beyond ED-10z, keep it on a genuinely new axis:
   production limitation-lift, final render-path probe, or policy/readback
   tuning from new evidence.
5. Keep line-break behavior policy/readback-driven: line length, max lines,
   orphan control, suffix-tail control, safe-area pressure, and rapid cue
   replacement are future bounded tuning areas.
6. Keep ED-10o as accepted review UX direction and reference evidence for why
   Keifont is the provisional normal-dialogue baseline while 851 Chikara
   Yowaku and Yasashisa Gothic remain alternates.
7. Keep BIZ/Noto/Meiryo visible only as reviewed rejected references unless the
   user explicitly reopens the system-safe route.
8. Keep 851 Chikara Dzuyoku and mincho/serif candidates in their separate
   emphasis/mood slots; do not collapse them into normal dialogue baseline
   acceptance.
9. Do not request another general `cut_002` / `cut_003` Keifont acceptance
   review unless the user explicitly reopens font-family selection.
10. If moving toward production/public use, run a separate limitation-lift route
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
   `.\open-artifacts.ps1`, current ED-10z tiny render-path probe via
   `.\open-current-proof.ps1`, ED-10o focused comparison reference via
   `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1`,
   regenerated ED-10l real-font comparison via
   `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1`,
   consumed ED-10j font audit via
   `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1`,
   `.\open-font-candidates.ps1`, or the ED-10i
   comparison helper:
   `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison\open_comparison.ps1`

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
- 2026-06-17: A new human review superseded the ED-10g styling direction only:
  the current Noto clean-outline proof is not accepted as-is. ED-10i now owns a
  narrow kirinuki gothic body/outline balance comparison with emoji excluded
  from the evaluation target. Production/public/rights gates remain closed.
- 2026-06-17: Human review of the ED-10i contact sheet selected the bottom-most
  gothic candidate as closest to ideal. Local JSON resolves it to
  `ed10i_meiryo_bold_fill_outline_balance`; a `cut_002` / `cut_003`
  diagnostic overlay proof was generated from that candidate for follow-up
  visual judgement. Production/public/rights gates remain closed.
- 2026-06-17: Freeform review of `clip-ed10i-meiryo-overlay-proof-001`
  consumed as not accepted for the normal subtitle baseline. Meiryo is demoted
  to reviewed reference, and ED-10j opens a kirinuki normal-dialogue font audit
  before any further bounded overlay proof. Production/public/rights gates
  remain closed.
- 2026-06-17: Freeform review of `clip-ed10j-kirinuki-font-audit-001`
  consumed. JSON/readback showed the blue badge/accent is the Noto candidate,
  not the Meiryo reference, but the actionable review still removes Meiryo from
  the normal subtitle baseline path and says the remaining candidates are close
  enough to stop prolonging the audit. BIZ UDGothic was selected as the
  recommended default for ED-10k overlay proof. Production/public/rights gates
  remain closed.
- 2026-06-18: Freeform review of `clip-ed10k-biz-overlay-proof-001` consumed
  as not accepted for the normal subtitle baseline. The review says BIZ is too
  hard/rigid, the text is thin, and the black outline is too strong; BIZ/Noto/
  Meiryo system-safe exploration is therefore kept as rejected reference for
  this use case. ED-10l opens a known Japanese kirinuki/telop font pack audit,
  with normal dialogue separated from emphasis/shout and mood/literary slots.
  Production/public/rights gates remain closed.
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
