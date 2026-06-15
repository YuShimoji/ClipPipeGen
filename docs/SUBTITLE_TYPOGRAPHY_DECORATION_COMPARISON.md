# Subtitle Typography Decoration Comparison

Last updated: 2026-06-15 JST

This packet consumes the `clip-human-preview-session-001` human answer as a
diagnostic / representative review decision. It does not approve production
subtitle design, production render, creative quality, rights, publishing,
public use, or upload.

## Decision Readback

Human response: `adjust_boundary`

Review note:

- Font size itself is acceptable for the current diagnostic / representative
  route.
- Font family selection remains unresolved.
- Decorative treatment remains unresolved.
- The next slice should preserve the accepted font-size direction and compare
  typography / decoration candidates.

| Axis | Current decision | Workflow effect |
|---|---|---|
| `font_size` | `accepted_for_diagnostic_representative_review` | Keep `round(frame_height * 0.115)` for the next diagnostic comparison proof. |
| `font_family` | `unresolved_needs_comparison` | Compare candidate Japanese font families before regenerating the subtitle overlay proof direction. |
| `decoration` | `unresolved_needs_comparison` | Compare outline, shadow, and placeholder speaker-badge accent treatment. |
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

Which font-family / decoration candidate should become the next diagnostic
subtitle overlay proof direction for `cut_002` / `cut_003`?

Allowed next answers for this comparison route:

- choose one candidate id
- request a small candidate adjustment
- reject all candidates and propose a different font/decor direction
- block because the comparison artifact is missing or unreadable

Keep this as diagnostic / representative review feedback only.
