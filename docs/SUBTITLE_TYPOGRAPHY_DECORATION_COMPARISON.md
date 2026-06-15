# Subtitle Typography Decoration Comparison

Last updated: 2026-06-16 JST

This packet was generated from the `clip-human-preview-session-001` human
answer `adjust_boundary`, then received the ED-10g comparison response
`small_adjustment`. The new response asks for a next diagnostic overlay proof
route that preserves the accepted font-size direction while keeping font family
and decorative treatment unresolved. It does not approve production subtitle
design, production render, creative quality, rights, publishing, public use, or
upload.

## Decision Readback

Source response consumed by this packet: `adjust_boundary`

ED-10g human response consumed: `small_adjustment`

Review note:

- Font size itself is acceptable for the current diagnostic / representative
  route.
- Font family selection remains unresolved and requires comparison or a
  concrete selection before the next overlay proof is regenerated.
- Decorative treatment remains unresolved and requires comparison or a
  concrete selection before the next overlay proof is regenerated.
- This is not production subtitle design acceptance.
- The next slice should preserve the accepted font-size direction and prepare a
  small-adjustment diagnostic overlay proof route for typography / decoration.

| Axis | Current decision | Workflow effect |
|---|---|---|
| `font_size` | `accepted_for_diagnostic_representative_review` | Keep `round(frame_height * 0.115)` for the next diagnostic comparison proof. |
| `font_family` | `unresolved_requires_comparison_or_selection` | Choose or refine a Japanese font-family route before regenerating the next subtitle overlay proof. |
| `decoration` | `unresolved_requires_comparison_or_selection` | Choose or refine outline, shadow, and placeholder speaker-badge accent treatment before regenerating the next subtitle overlay proof. |
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
was not present. That is a same-machine artifact boundary, not a tracked Git
failure. Because the human response is supplied explicitly as
`small_adjustment`, this decision can be recorded from tracked docs/tests
without regenerating SH-08 or the comparison artifact. Regenerate this packet
only when visual judgment or exact candidate readback is needed again.

Tracked generator readback now keeps these two decisions separate:
`human_decision_readback.selected_response=adjust_boundary` records the source
SH-08 / ED-10f response, while
`comparison_response_readback.selected_response=small_adjustment` records the
ED-10g comparison response. The regenerated JSON/HTML also includes
`next_diagnostic_overlay_proof_route` so a future local comparison artifact can
point directly to the small-adjustment diagnostic overlay proof route without
claiming production acceptance.

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

## Next Diagnostic Overlay Proof Route

The next proof route is a small-adjustment route, not a SH-08 preview-session
regeneration route.

| Route element | Decision |
|---|---|
| target cuts | Keep `cut_002` and `cut_003` as the diagnostic / representative proof targets. |
| font size | Preserve `round(frame_height * 0.115)` and do not reopen size as the primary question. |
| font family | Keep unresolved until a concrete family route or adjusted candidate is selected. |
| decoration | Keep unresolved until outline, shadow, and placeholder badge accent are selected or narrowed. |
| artifact boundary | Treat `subtitle_typography_decoration_comparison/` as ignored local review evidence; do not stage `episodes/`. |
| acceptance boundary | Keep production subtitle design, production render, creative, rights, publishing, public-use, and upload acceptance false or pending. |

Recommended next tracked route: define an adjusted diagnostic overlay proof
packet that carries the accepted size into the next `cut_002` / `cut_003`
subtitle overlay proof while varying only the unresolved font-family and
decoration axes. If the local comparison artifact is missing, regenerate it
only when the adjusted candidate needs visual confirmation before proof
generation.

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

## Next Human Question

Which concrete font-family / decoration adjustment should become the next
diagnostic subtitle overlay proof direction for `cut_002` / `cut_003`?

Allowed next answers for this small-adjustment route:

- choose one candidate id
- specify the small candidate adjustment to apply
- reject all candidates and propose a different font/decor direction
- block because the comparison artifact is missing or unreadable

Keep this as diagnostic / representative review feedback only.
