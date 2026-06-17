---
id: subtitle-typography-decoration-comparison
title: Subtitle Typography Decoration Comparison
type: decision_packet
status: ed10j_font_audit_route_open
health: historical_reference
progress_pct: 100
last_touched: 2026-06-17
next_review_due: after_ed10j_kirinuki_font_audit_review
active_artifact: clip-ed10j-kirinuki-font-audit-001
source_of_truth: true
owner_lane: editing
related: docs/REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md, docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md, artifacts/ARTIFACTS.md
---

# Subtitle Typography Decoration Comparison

Last updated: 2026-06-17 JST

## Current Update - ED-10j Reopens Font Baseline Audit

The latest freeform review of `clip-ed10i-meiryo-overlay-proof-001` has been
consumed as a baseline-font judgement. The Meiryo proof is not accepted as the
normal subtitle baseline: it looks too thin, is not attractive enough as the
default subtitle face, and should not be treated as a minor outline-only tweak.

ED-10j now owns the next route:
`clip-ed10j-kirinuki-font-audit-001`. Meiryo remains visible only as a reviewed
reference candidate. The active comparison narrows normal-dialogue candidates
to local/no-download fonts first: BIZ UDGothic, Yu Gothic, Noto Sans JP, and
the reviewed Meiryo reference. M PLUS / Zen Kaku Gothic New / Dela Gothic One
stay in a later download/license-decision bucket until explicitly approved.

| Route | Current role | What it can decide | What stays closed |
|---|---|---|---|
| `clip-ed10g-noto-overlay-proof-001` | Previous diagnostic proof / reference only | Shows the Noto clean-outline baseline that was judged insufficient as-is | Production subtitle design, render, creative, rights, publishing, public use |
| `clip-ed10i-kirinuki-gothic-balance-001` | Consumed comparison / audit trail | Why the bottom candidate maps to `ed10i_meiryo_bold_fill_outline_balance` | Production subtitle design, render, creative, rights, publishing, public use |
| `clip-ed10i-meiryo-overlay-proof-001` | Reviewed reference proof | Shows why Meiryo should not be fixed as the normal subtitle baseline | Production subtitle design, render, creative, rights, publishing, public use |
| `clip-ed10j-kirinuki-font-audit-001` | Active font audit comparison | Which normal-dialogue gothic/sans candidate should become the next narrow overlay proof base | Production subtitle design, render, creative, rights, publishing, public use |

## これは何か

ED-10g の subtitle font-family / outline / shadow / placeholder badge
decoration 比較 packet です。`clip-typography-decoration-comparison-001` の
人間回答 `small_adjustment` を受け、次の diagnostic overlay proof base を
`noto_sans_jp_clean_outline` に絞った状態を記録します。

## 何のためにあるか

font size を再議論せず、accepted diagnostic size
`round(frame_height * 0.115)` を維持したまま、フォントと装飾の小調整だけを
判断できるようにするための page です。production font finality ではなく、
representative diagnostic proof の判断面です。

## 今の状態

`clip-ed10i-meiryo-overlay-proof-001` はレビュー済みで、normal subtitle
baseline としては不採用です。現在の active artifact は
`clip-ed10j-kirinuki-font-audit-001` で、次に overlay proof 化する候補を
freeform review で絞ります。

## これからどうなるか

1. ED-10j の font audit contact sheet を確認し、次の overlay proof 候補を
   freeform review で絞る。
2. Meiryo は reviewed reference としてのみ扱い、通常字幕 baseline に戻す
   場合は明示レビューを要求する。
3. representative coverage を広げるなら、dense/stress proof や production
   render / rights slice とは別に `cut_008` などの明示 target を起票する。
4. 追加比較が必要なら ED-10h registry から Google Fonts / OFL / system font
   candidates を選び、download なし route か許可付き download route を選ぶ。

## 使い方・確認方法

Primary local proof:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1
```

Reviewed Meiryo reference:

```powershell
.\open-current-proof.ps1
```

## 実装・設計メモ

The tracked generator keeps `human_decision_readback.selected_response` and
`comparison_response_readback.selected_response` separate so the SH-08
`adjust_boundary` answer and the ED-10g `small_adjustment` answer do not blur
together.

## Decision Log

- 2026-06-16: `small_adjustment` consumed.
- 2026-06-16: `noto_sans_jp_clean_outline` selected as next diagnostic overlay
  proof base.
- 2026-06-16: human visual judgement accepted
  `clip-ed10g-noto-overlay-proof-001` as the diagnostic / representative base
  for `cut_002` / `cut_003`.
- 2026-06-16: broader font universe moved to `ED-10h` instead of changing the
  current selected proof base.
- 2026-06-17: new human review superseded the ED-10g styling direction only.
  The current Noto clean-outline proof is not accepted as-is; the next route is
  ED-10i kirinuki gothic weight / outline balance comparison.
- 2026-06-17: ED-10i contact sheet review selected the bottom-most gothic
  candidate as closest to ideal. Local JSON resolves it to
  `ed10i_meiryo_bold_fill_outline_balance`; a selected-candidate overlay proof
  was generated for `cut_002` / `cut_003`.
- 2026-06-17: freeform review of the Meiryo overlay proof consumed as
  reviewed-not-accepted for the normal subtitle baseline. ED-10j opens the
  kirinuki normal-dialogue font audit and demotes Meiryo to reference.

## Constraints / Risks

- This is diagnostic / representative only.
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `production_candidate=false`
- `production_usage_allowed=false`
- `rights_status=pending`
- `episodes/` artifacts are local retained evidence and must not be staged.

## Changelog

- 2026-06-16: Added v1.5 metadata and ED-10h successor pointer.

This packet was generated from the `clip-human-preview-session-001` human
answer `adjust_boundary`, then received the ED-10g comparison response
`small_adjustment`. The new response asks for a next diagnostic overlay proof
route that preserves the accepted font-size direction and adopts
`noto_sans_jp_clean_outline` as the next diagnostic overlay proof base. It
does not approve production subtitle design, production render, creative
quality, rights, publishing, public use, or upload.

## Decision Readback

Source response consumed by this packet: `adjust_boundary`

ED-10g human response consumed: `small_adjustment`

Review note:

- Font size itself is acceptable for the current diagnostic / representative
  route.
- Font family is narrowed to `noto_sans_jp_clean_outline` for the next
  diagnostic overlay proof.
- Decorative treatment is narrowed to that candidate's clean outline and cool
  placeholder badge accent for the next diagnostic overlay proof.
- This is not production subtitle design acceptance.
- The small-adjustment diagnostic overlay proof for `cut_002` / `cut_003` was
  accepted as a historical diagnostic / representative base before later
  styling reviews superseded it.

| Axis | Current decision | Workflow effect |
|---|---|---|
| `font_size` | `accepted_for_diagnostic_representative_review` | Keep `round(frame_height * 0.115)` for the next diagnostic comparison proof. |
| `font_family` | `narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof` | Use the Noto Sans JP route for the next diagnostic overlay proof, with local font fallback recorded in readback. |
| `decoration` | `narrowed_to_clean_outline_for_next_diagnostic_proof` | Use the clean outline / cool placeholder badge accent candidate for the next diagnostic overlay proof. |
| human visual judgement | `accept_diagnostic_base` | The selected proof base can carry forward for diagnostic / representative review only. |
| production/public gates | false or pending | No production subtitle design, render, rights, publishing, public-use, or upload acceptance is created. |

## Historical ED-10i Comparison Artifact

The ED-10i comparison audit artifact is
`clip-ed10i-kirinuki-gothic-balance-001`. It remains the audit trail for how
the bottom row resolved to Meiryo, but the active route is now ED-10j.

Primary local report:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_gothic_balance_comparison/subtitle_kirinuki_gothic_balance_comparison_report.html
```

Open command:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison\open_comparison.ps1
```

Generated command:

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison `
  --comparison-profile ed10i_kirinuki_gothic_balance `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

The candidate set is deliberately small: current Noto reference, BIZ UDGothic
Bold balanced outline, Yu Gothic Bold thinner outline, and Meiryo Bold
fill/outline balance. Font size, placement, wrapping, source media, transcript,
official subtitle evidence, rights, publishing, upload, and production state
remain unchanged.

## Reviewed ED-10i Overlay Proof

Artifact id: `clip-ed10i-meiryo-overlay-proof-001`

The reviewed proof applies `ed10i_meiryo_bold_fill_outline_balance` to
`cut_002` / `cut_003`. The follow-up freeform review did not accept it as the
normal subtitle baseline. It reuses the existing subtitle overlay proof surface
and does not regenerate SH-08.

Primary local report:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html
```

Open command:

```powershell
.\open-current-proof.ps1
```

Generated command:

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --typography-decoration-candidate-id ed10i_meiryo_bold_fill_outline_balance `
  --format json
```

ED-10i same-machine readback: `style_candidate_id` and
`typography_decoration_candidate_id` are both
`ed10i_meiryo_bold_fill_outline_balance`, `font_size.value=124`,
`outline.value=9`, `font_family_route.requested=Meiryo`,
`font_family_route.font_file_status=candidate_primary_font_file_found`,
`subtitle_overlay_available_count=2`,
`visual_proof_status=available_requires_human_review`,
`production_candidate=false`, and `rights_status=pending`.

Artifact id: `clip-typography-decoration-comparison-001`

Storage class: local retained artifact; same-machine evidence only.

Primary local report:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison/subtitle_typography_decoration_comparison_report.html
```

Open command:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_typography_decoration_comparison\open_comparison.ps1
```

The generated report contains 4 candidates and 16 PNG samples for `cut_002` /
`cut_003` review text. The contact sheet is:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison/subtitle_typography_decoration_contact_sheet.png
```

Current worktree readback on 2026-06-16 JST: the local ignored comparison JSON
was refreshed with the current tracked generator, without regenerating SH-08.
It records `comparison_response_readback.selected_response=small_adjustment`,
`next_diagnostic_overlay_proof_route.route_kind=small_adjustment_diagnostic_overlay_proof`,
`selected_candidate_for_next_proof_base=noto_sans_jp_clean_outline`,
`font_size_policy.value=124`, `candidate_count=4`, `sample_count=16`, and false
/ pending production-public flags. The contact sheet was inspected as a
nonblank same-machine visual artifact, and all generated sample text boxes
reported inside the safe area. This is local retained evidence only, not a Git
portable artifact.

Tracked generator readback now keeps these two decisions separate:
`human_decision_readback.selected_response=adjust_boundary` records the source
SH-08 / ED-10f response, while
`comparison_response_readback.selected_response=small_adjustment` records the
ED-10g comparison response. The regenerated JSON/HTML also includes
`next_diagnostic_overlay_proof_route` and
`small_adjustment_decision_packet` so a future local comparison artifact can
point directly to the small-adjustment diagnostic overlay proof route, carry
`noto_sans_jp_clean_outline` as the selected next proof base, and still avoid
any production acceptance claim. The persisted report JSON is ASCII-escaped for
stable Windows PowerShell and Python parser readback; the HTML remains the
human-readable surface.

## Candidates

| Candidate | Font family route | Decoration route | Why it exists |
|---|---|---|---|
| `current_yu_gothic_heavy_outline` | Yu Gothic heavy/bold route | current heavy outline and yellow placeholder speaker badge | Baseline against the current diagnostic proof direction. |
| `noto_sans_jp_clean_outline` | Noto Sans JP route, with local fallback if unavailable | slightly cleaner outline and cool placeholder badge accent | Tests whether a cleaner modern Japanese face reads better without changing size. |
| `meiryo_bold_soft_shadow` | Meiryo Bold route | lighter outline with stronger soft-shadow readback | Tests whether softness reduces heaviness while preserving readability. |
| `gothic_high_contrast_minimal_badge` | MS Gothic route, with local fallback if unavailable | stronger contrast with quieter badge block | Tests high-contrast text while reducing badge decoration weight. |

All candidates preserve:

- `font_size` formula: `round(frame_height * 0.115)`
- `badge_left_dialogue` placement
- font-bbox Japanese wrapping authority
- placeholder-only speaker badge status
- false / pending production, rights, publishing, and public-use flags

## Small-Adjustment Decision Packet

The adjusted candidate is now selected for the next diagnostic overlay proof:
`noto_sans_jp_clean_outline`. The other candidates remain comparison context if
the next proof needs a fallback or alternate review path.

| Option | Use as | Adoption reason | Watch item |
|---|---|---|---|
| `current_yu_gothic_heavy_outline` | Reference only | Keeps the accepted diagnostic baseline visible for comparison. | Does not satisfy the request to refine font family / decoration by itself. |
| `noto_sans_jp_clean_outline` | Selected next proof base | Smallest readable adjustment: cleaner modern Japanese face, slightly lighter outline, cooler placeholder badge, and unchanged accepted size / placement. | Font availability can fall back locally; proof must record the resolved font file. |
| `meiryo_bold_soft_shadow` | Alternate if the default still feels too heavy | Preserves readable boldness while testing softer decoration and stronger shadow. | Shadow softness may reduce crispness on fast video motion. |
| `gothic_high_contrast_minimal_badge` | Alternate if badge decoration is the main concern | Reduces badge visual weight while keeping high contrast text. | MS Gothic can feel more mechanical; use only if high contrast matters more than warmth. |

Rejected routes for this slice:

- Regenerating SH-08 `human_preview_session/`: not required for this ED-10g
  small-adjustment route.
- Treating `small_adjustment` as production subtitle design acceptance:
  explicitly out of scope.
- Adding `cut_008` dense/stress proof now: still a separate route unless the
  next review explicitly widens scope.
- Mutating source media, transcript, official subtitle evidence, rights,
  publishing, public use, or upload state: outside this diagnostic proof route.

## Adjusted Diagnostic Overlay Proof

The current proof route is a small-adjustment route, not a SH-08
preview-session regeneration route.

| Route element | Decision |
|---|---|
| target cuts | Keep `cut_002` and `cut_003` as the diagnostic / representative proof targets. |
| font size | Preserve `round(frame_height * 0.115)` and do not reopen size as the primary question. |
| selected proof base | Use `noto_sans_jp_clean_outline` for the next diagnostic overlay proof. |
| font family | Narrow to the Noto Sans JP route, while recording the local resolved font file or fallback. |
| decoration | Narrow to clean outline plus cool placeholder badge accent for this diagnostic proof. |
| artifact boundary | Treat `subtitle_typography_decoration_comparison/` as ignored local review evidence; do not stage `episodes/`. |
| acceptance boundary | Keep production subtitle design, production render, creative, rights, publishing, public-use, and upload acceptance false or pending. |

Artifact id: `clip-ed10g-noto-overlay-proof-001`

Storage class: local retained artifact; same-machine evidence only.

Primary local report:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html
```

Open command:

```powershell
.\open-current-proof.ps1
```

Generated command:

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --typography-decoration-candidate-id noto_sans_jp_clean_outline `
  --format json
```

Current readback on 2026-06-16 JST: `target_cuts=[cut_002, cut_003]`,
`style_candidate_id=noto_sans_jp_clean_outline`,
`typography_decoration_candidate_id=noto_sans_jp_clean_outline`,
`font_size.value=124`, `font_size.readback=round(frame_height * 0.115)`,
`outline.value=11`, `outline.readback=max(2, round(font_size * 0.086))`,
`font_family_route.requested=Noto Sans JP`,
`font_family_route.font_file_status=candidate_primary_font_file_found`,
`subtitle_overlay_available_count=2`,
`all_target_cuts_have_overlay=true`, `bbox_wrapping_applied=true`,
`explicit_ass_line_breaks=true`, `one_character_orphan_present=false`, and
`suspicious_tail_line_present=false`. The generated PNG frames for `cut_002`
and `cut_003` were inspected as nonblank 1920x1080 local visual artifacts, and
a readback-based bbox/safe-area check reported no computed failures.

Review status: `accepted_diagnostic_base`. The proof is diagnostic /
representative only; production subtitle design acceptance, production render
acceptance, creative acceptance, rights approval, publishing acceptance, public
use, and upload remain false or pending.

Recommended next tracked route: keep `noto_sans_jp_clean_outline` as the
accepted diagnostic base. If the local comparison artifact is missing in
another worktree, regenerate it only when adjusted-candidate visual
confirmation is needed for audit, not to reopen this consumed decision.

## Regeneration Command

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_typography_decoration_comparison `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

Pillow is an optional local review dependency for generating these PNG
artifacts. It is not a project-wide production renderer dependency.

## Overlay Proof Regeneration Command

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --typography-decoration-candidate-id noto_sans_jp_clean_outline `
  --format json
```

This refreshes the existing ignored `subtitle_overlay_visual_proof_report.*`
surface for the selected small-adjustment base. It does not regenerate SH-08
and does not mutate source media, transcript, official subtitle evidence,
rights, publishing, upload, or production acceptance state.

## Consumed Human Judgement

Human judgement: accept the generated `noto_sans_jp_clean_outline` diagnostic
overlay proof for `cut_002` / `cut_003` as the current small-adjustment base for
diagnostic / representative review.

This closes the ED-10g proof-choice question. Any further work must be a new
bounded route: dense/stress coverage, a specific visual defect adjustment, or a
separate production/public/rights limitation-lift slice. Keep this judgement as
diagnostic / representative review feedback only.
