---
id: subtitle-typography-decoration-comparison
title: Subtitle Typography Decoration Comparison
type: decision_packet
status: generated_requires_human_review
health: review_ready_diagnostic
progress_pct: 85
last_touched: 2026-06-16
next_review_due: before_ed10h_candidate_sweep
active_artifact: clip-ed10g-noto-overlay-proof-001
source_of_truth: true
owner_lane: editing
related: docs/REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md, docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md, artifacts/ARTIFACTS.md
---

# Subtitle Typography Decoration Comparison

Last updated: 2026-06-16 JST

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

`clip-ed10g-noto-overlay-proof-001` は `cut_002` / `cut_003` に生成済みです。
現在の質問は「Noto Sans JP clean-outline をこの diagnostic /
representative base として受け入れるか」です。次に候補 universe を広げる
作業は [SUBTITLE_FONT_CANDIDATE_SWEEP.md](SUBTITLE_FONT_CANDIDATE_SWEEP.md)
の `ED-10h` に分離します。

## これからどうなるか

1. current proof を人間が visual review する。
2. 受け入れなら ED-10g を閉じ、dense/stress proof や production render /
   rights slice へ進む。
3. 追加比較が必要なら ED-10h registry から Google Fonts / OFL / system font
   candidates を選び、download なし route か許可付き download route を選ぶ。

## 使い方・確認方法

Primary local proof:

```powershell
powershell -NoProfile -Command "Invoke-Item -LiteralPath 'episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_overlay_visual_proof_report.html'"
```

Comparison contact sheet:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_typography_decoration_comparison\open_comparison.ps1
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
- 2026-06-16: broader font universe moved to `ED-10h` instead of changing the
  current selected proof base.

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
- The small-adjustment diagnostic overlay proof for `cut_002` / `cut_003` has
  been generated with the selected base and now needs human visual judgement.

| Axis | Current decision | Workflow effect |
|---|---|---|
| `font_size` | `accepted_for_diagnostic_representative_review` | Keep `round(frame_height * 0.115)` for the next diagnostic comparison proof. |
| `font_family` | `narrowed_to_noto_sans_jp_clean_outline_for_next_diagnostic_proof` | Use the Noto Sans JP route for the next diagnostic overlay proof, with local font fallback recorded in readback. |
| `decoration` | `narrowed_to_clean_outline_for_next_diagnostic_proof` | Use the clean outline / cool placeholder badge accent candidate for the next diagnostic overlay proof. |
| production/public gates | false or pending | No production subtitle design, render, rights, publishing, public-use, or upload acceptance is created. |

## Active Comparison Artifact

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
powershell -NoProfile -Command "Invoke-Item -LiteralPath 'episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_overlay_visual_proof_report.html'"
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

Review status: `generated_requires_human_review`. The proof is diagnostic /
representative only; production subtitle design acceptance, production render
acceptance, creative acceptance, rights approval, publishing acceptance, public
use, and upload remain false or pending.

Recommended next tracked route: inspect the adjusted diagnostic overlay proof
using `noto_sans_jp_clean_outline` as the selected base. If the local
comparison artifact is missing in another worktree, regenerate it only when
adjusted-candidate visual confirmation is needed before proof generation.

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

## Next Human Question

Is the generated `noto_sans_jp_clean_outline` diagnostic overlay proof for
`cut_002` / `cut_003` acceptable as the current small-adjustment base for
diagnostic / representative review?

Allowed next answers for that proof:

- accept this diagnostic proof base
- request a specific small adjustment to the selected base
- reject this base and choose one alternate candidate
- block because the overlay proof artifact is missing or unreadable

Keep this as diagnostic / representative review feedback only.
