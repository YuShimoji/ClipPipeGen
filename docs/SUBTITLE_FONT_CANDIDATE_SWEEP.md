---
id: subtitle-font-candidate-sweep
title: Subtitle Font Candidate Sweep v0
type: candidate_registry
status: approved
health: defined_not_generated
progress_pct: 15
last_touched: 2026-06-17
next_review_due: after_ed10i_meiryo_overlay_visual_judgement
active_artifact: clip-subtitle-font-candidate-sweep-001
source_of_truth: true
owner_lane: editing
related: docs/SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md, docs/font_candidates/subtitle-font-candidates.json, docs/FEATURE_REGISTRY.md
---

# Subtitle Font Candidate Sweep v0

## これは何か

`ED-10h: Subtitle Font Candidate Sweep v0` の候補 registry です。ED-10g で
選ばれた `noto_sans_jp_clean_outline` を current diagnostic overlay proof
base として保持したまま、次に比較対象を Google Fonts / OFL / free fonts /
local installed fonts へ広げるための土台を置きます。

## 何のためにあるか

字幕の見た目を「その場で思いついた font name」ではなく、候補 class、license
status、local availability、reproducibility、intended use で比較できるように
します。これにより、次の overlay proof 生成前に「download なしで試す」
「license metadata を捕まえて download する」「local-only evidence に留める」
の判断を分けられます。

## 今の状態

- Current selected diagnostic proof base:
  `ed10i_meiryo_bold_fill_outline_balance`
- Preserved font size policy: `round(frame_height * 0.115)`
- 1080p readback: `font_size=124`
- Local font readback was limited to `C:\Windows\Fonts`.
- Font binaries were not downloaded, copied, or vendored.
- Machine-readable registry:
  [font_candidates/subtitle-font-candidates.json](font_candidates/subtitle-font-candidates.json)

This registry is not a production subtitle design acceptance.

## ED-10i Narrow Gothic Slice

ED-10i does not run the full ED-10h font universe. It uses a narrow
gothic/sans-only set already available on this machine:

| Candidate | Role in ED-10i | Portability note |
|---|---|---|
| `ed10i_reference_noto_clean_outline` | Current reference that was judged not accepted as-is | Local Noto Sans JP file readback only |
| `ed10i_biz_udgothic_bold_balanced_outline` | Recommended default for thicker glyph body with restrained outline | Local BIZ UDGothic Bold file readback only |
| `ed10i_yu_gothic_bold_thin_outline` | Thinner-outline variant using a familiar Windows gothic route | Local Yu Gothic Bold file readback only |
| `ed10i_meiryo_bold_fill_outline_balance` | Selected bottom candidate and current diagnostic overlay proof base | Local Meiryo Bold file readback only |

Emoji rendering is intentionally ignored in ED-10i. No font binaries are
downloaded, copied, vendored, or made portable through Git in this slice.
The selected overlay proof is `clip-ed10i-meiryo-overlay-proof-001`; the
comparison artifact remains the audit trail for how the bottom row resolved to
this candidate id.

## これからどうなるか

1. **No-download local sweep**: compare only candidates with
   `file_status=local_only` on this machine. This is fastest, but not portable.
2. **Google Fonts / OFL sweep**: request permission to download specific
   families, capture license/version/source metadata, and keep binaries out of
   public Git unless a repo policy is approved.
3. **Hybrid sweep**: use local system fonts for quick proof, then reproduce the
   selected family through a licensed pinned source later.

## 使い方・確認方法

Open the registry overview:

```powershell
.\open-font-candidates.ps1
```

Parse the registry:

```powershell
python -m json.tool docs\font_candidates\subtitle-font-candidates.json
```

Check the current local font readback:

```powershell
Get-ChildItem C:\Windows\Fonts -File |
  Where-Object { $_.Name -match 'Noto|BIZ|YuGoth|Meiryo|msgothic|msmincho' } |
  Select-Object Name
```

Regenerate docs dashboard after registry edits:

```powershell
uvx python -m src.cli.main build-docs-dashboard --format json
```

## 実装・設計メモ

`source_type=google_fonts` means the family is a candidate from the Google Fonts
/ OFL universe, not that the file is present locally. `source_type=local_system`
means this machine has a matching file under the local system font directory.
Only local filesystem readback can set `file_status=local_only`; missing Google
Fonts candidates stay `missing` until a download route is explicitly approved.

`can_reproduce_on_other_terminal=false` is expected for local-only fonts. To
make a candidate reproducible, a future slice needs pinned source URL, exact
license text or metadata, file hash, and a decision on whether binaries stay
outside public Git.

## Decision Log

- 2026-06-16: Created ED-10h registry after ED-10g selected
  `noto_sans_jp_clean_outline` for the current diagnostic overlay proof.
- 2026-06-16: No third-party font binaries were downloaded or vendored.
- 2026-06-17: Added ED-10i narrow gothic/sans candidate set after human review
  rejected the current Noto clean-outline styling as-is.
- 2026-06-17: Consumed the ED-10i contact-sheet review: the bottom-most gothic
  candidate was selected as closest to ideal and resolved to
  `ed10i_meiryo_bold_fill_outline_balance`.

## Constraints / Risks

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `production_candidate=false`
- `production_usage_allowed=false`
- `rights_status=pending`
- Font availability is not portable unless the registry records a reproducible
  source and the repo policy approves how the file is stored.
- License status in this registry is a routing label for candidate selection,
  not legal approval for public production use.

## Changelog

- 2026-06-16: Initial candidate universe and same-machine local font readback.
