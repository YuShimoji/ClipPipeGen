---
id: subtitle-font-candidate-sweep
title: Subtitle Font Candidate Sweep v0
type: candidate_registry
status: in_progress
health: ed10l_known_font_pack_audit_active
progress_pct: 90
last_touched: 2026-06-18
next_review_due: after_ed10l_known_font_pack_review
active_artifact: clip-ed10l-known-kirinuki-font-pack-001
source_of_truth: true
owner_lane: editing
related: docs/SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md, docs/font_candidates/subtitle-font-candidates.json, docs/FEATURE_REGISTRY.md
---

# Subtitle Font Candidate Sweep v0

## これは何か

`ED-10h: Subtitle Font Candidate Sweep v0`、`ED-10j: Kirinuki Subtitle Font
Research & Candidate Audit v0`、`ED-10k: BIZ UDGothic Overlay Proof v0`、
`ED-10l: Known Kirinuki Font Pack Audit v0` をつなぐ候補 registry です。
現在は ED-10k の BIZ proof 不採用レビューを消費し、system-safe/generic
readable fonts ではなく、既知の日本語 YouTube kirinuki/telop font pack を
通常字幕 baseline 候補として監査する段階です。

## 何のためにあるか

字幕の見た目を「その場で思いついた font name」ではなく、候補 class、license
status、local availability、reproducibility、intended use で比較できるように
します。これにより、次の overlay proof 生成前に「download なしで試す」
「license metadata を捕まえて download する」「local-only evidence に留める」
の判断を分けられます。

## 今の状態

- Current selected diagnostic proof base:
  `pending_ed10l_known_font_pack_review`
- Reviewed Meiryo proof:
  `clip-ed10i-meiryo-overlay-proof-001` is not accepted as the normal subtitle
  baseline.
- Reviewed BIZ proof:
  `clip-ed10k-biz-overlay-proof-001` is not accepted as the normal subtitle
  baseline.
- Consumed audit artifact:
  `clip-ed10j-kirinuki-font-audit-001`
- Active audit artifact:
  `clip-ed10l-known-kirinuki-font-pack-001`
- Preserved font size policy: `round(frame_height * 0.115)`
- 1080p readback: `font_size=124`
- Local font readback was limited to `C:\Windows\Fonts`.
- ED-10l target fonts were not installed locally on 2026-06-18 JST; generated
  samples therefore carry missing-font/fallback readback until a real install
  route is chosen.
- Font binaries were not downloaded, copied, or vendored.
- Machine-readable registry:
  [font_candidates/subtitle-font-candidates.json](font_candidates/subtitle-font-candidates.json)

This registry is not a production subtitle design acceptance.

## ED-10l Known Kirinuki Font Pack Audit

ED-10l consumes the latest freeform review as a route correction. BIZ UDGothic
was reviewed as too hard/rigid, thin, and black-outline-heavy for the normal
subtitle baseline. The route is no longer another BIZ/Noto/Meiryo tuning pass;
the issue is the candidate universe.

Tracked self-diagnosis:

- previous exploration biased toward system-safe / generic readable fonts
- safe/reproducible was conflated with strong kirinuki subtitle design
- user known-good domain knowledge was not elevated early enough
- general font documentation was treated as sufficient for telop usage needs

ED-10l separates usage slots:

| Slot | Candidates | Current role |
|---|---|---|
| normal dialogue baseline | `ed10l_keifont_pop_dialogue_candidate`, `ed10l_851_chikara_yowaku_dialogue_candidate`, `ed10l_m_plus_fonts_dialogue_candidate`, `ed10l_yasashisa_gothic_goodfreefonts_candidate` | Active review target |
| emphasis / shout / tsukkomi | `ed10l_851_chikara_zuyoku_emphasis_candidate` | Parked outside normal baseline |
| mood / literary | `ed10l_source_han_serif_mood_candidate`, `ed10l_shippori_mincho_mood_candidate` | Parked outside normal baseline |

Source pages inspected for ED-10l:

| Source | Use in ED-10l | Handling note |
|---|---|---|
| [Keifont official specimen](https://font.sumomo.ne.jp/font_1.html) | Strong pop/kirinuki normal-dialogue candidate | Install/source/license readback required |
| [851 Chikara Yowaku official](https://pm85122.onamae.jp/851ch-yw.html) | Soft/weak dialogue candidate | Install/readback required |
| [M+ FONTS official](https://mplusfonts.github.io/) | OFL-backed reproducible candidate route | Choose exact installed file/weight before proof |
| [GoodFreeFonts YouTube subtitle roundup](https://goodfreefonts.com/820/) | User-provided candidate-universe correction | Index only; official source/license capture still required |
| [851 Chikara Dzuyoku official](https://pm85122.onamae.jp/851ch-dz.html) | Emphasis/shout/tsukkomi reference | Not normal baseline |
| [Source Han Serif JP](https://source.typekit.com/source-han-serif/jp/) / [Shippori Mincho](https://fontdasu.com/shippori-mincho/) | Mood/literary references | Not normal baseline |

## ED-10j Kirinuki Font Audit

ED-10j consumes the latest freeform review as a route change, not a minor
Meiryo tweak. The reviewed Meiryo proof looked too thin and not attractive
enough for the default / normal subtitle face, so Meiryo is now an audited
reference candidate rather than the current baseline.

Research-backed readback is intentionally small and bounded:

| Source | What it supports | How ED-10j uses it |
|---|---|---|
| [Microsoft Learn: Meiryo](https://learn.microsoft.com/en-us/typography/font-list/meiryo) | Meiryo is a clean screen/body-text face optimized for reading | Explains why it can be legible but still weak as an aspirational kirinuki subtitle baseline |
| [Google Fonts: BIZ UDGothic](https://fonts.google.com/specimen/BIZ+UDGothic) | BIZ UDGothic is a legibility-oriented gothic family with regular/bold route | Makes BIZ UDGothic the safest no-download body-first candidate |
| [Google Fonts: M PLUS 1p](https://fonts.google.com/specimen/M+PLUS+1p) | M PLUS has heavier weights from Thin to Black | Keeps M PLUS in later-download bucket for a likely stronger telop-like body |
| [Google Fonts: Zen Kaku Gothic New](https://fonts.google.com/specimen/Zen+Kaku+Gothic+New) | Contemporary Japanese gothic family | Keeps Zen Kaku Gothic New in later-download bucket for normal-dialogue exploration |
| [Google Fonts: Dela Gothic One](https://fonts.google.com/specimen/Dela+Gothic+One) | Very thick gothic body intended for strong display use | Records it as emphasis/display reference, not the normal-dialogue baseline |

ED-10j freeform review is now consumed. JSON/readback confirmed that the blue
badge/accent candidate is `ed10j_noto_sans_jp_local_telop_candidate`, while
the Meiryo reference is `ed10j_reference_meiryo_reviewed_not_baseline`. The
visual review still removes Meiryo from the normal baseline candidate path, and
because no stronger preference was stated among the remaining candidates, the
recommended default BIZ route becomes ED-10k's proof base.

Current no-download shortlist after Meiryo demotion:

| Candidate | Bucket | Current role |
|---|---|---|
| `ed10j_reference_meiryo_reviewed_not_baseline` | reviewed reference only | Not a normal baseline candidate |
| `ed10j_biz_udgothic_bold_telop_candidate` | likely video/telop-friendly local | Selected ED-10k proof base |
| `ed10j_yu_gothic_bold_system_candidate` | system/default safe | Familiar Windows gothic comparison; watch for default-OS feel |
| `ed10j_noto_sans_jp_local_telop_candidate` | likely video/telop-friendly local | Modern local sans comparison; may need heavier weight later |

Later download / license decision bucket:

| Candidate | Why not generated now |
|---|---|
| `m_plus_1p_bold` / `m_plus_2p_bold` | Promising heavier Japanese sans route, but not locally available |
| `zen_kaku_gothic_new_bold` | Plausible normal-dialogue gothic route, but not locally available |
| `dela_gothic_one_emphasis` | Too display/emphasis-oriented for baseline; useful only after normal-dialogue route is stable |

## ED-10i Narrow Gothic Slice

ED-10i does not run the full ED-10h font universe. It uses a narrow
gothic/sans-only set already available on this machine:

| Candidate | Role in ED-10i | Portability note |
|---|---|---|
| `ed10i_reference_noto_clean_outline` | Current reference that was judged not accepted as-is | Local Noto Sans JP file readback only |
| `ed10i_biz_udgothic_bold_balanced_outline` | Recommended default for thicker glyph body with restrained outline | Local BIZ UDGothic Bold file readback only |
| `ed10i_yu_gothic_bold_thin_outline` | Thinner-outline variant using a familiar Windows gothic route | Local Yu Gothic Bold file readback only |
| `ed10i_meiryo_bold_fill_outline_balance` | Reviewed reference after follow-up proof; not normal baseline | Local Meiryo Bold file readback only |

Emoji rendering is intentionally ignored in ED-10i. No font binaries are
downloaded, copied, vendored, or made portable through Git in this slice.
The selected overlay proof was `clip-ed10i-meiryo-overlay-proof-001`; the
follow-up freeform review did not accept it as the normal subtitle baseline.
The comparison artifact remains the audit trail for how the bottom row resolved
to this candidate id.

## これからどうなるか

1. **ED-10l known-font review**: inspect the known kirinuki font pack comparison
   and decide which normal-dialogue candidate should get a real install/proof
   route.
2. **Official source/license capture**: before installing or pinning any font,
   capture source URL, license/version notes, and local file readback.
3. **Google Fonts / OFL sweep**: request permission to download specific
   families, capture license/version/source metadata, and keep binaries out of
   public Git unless a repo policy is approved.
4. **Hybrid sweep**: use local system fonts for quick proof, then reproduce the
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
  Where-Object { $_.Name -match 'Noto|BIZ|YuGoth|Meiryo|msgothic|msmincho|UDDigi' } |
  Select-Object Name
```

Open the ED-10j audit artifact on the retaining machine:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1
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
- 2026-06-17: Consumed the ED-10i Meiryo overlay freeform review: Meiryo is not
  accepted as the normal subtitle baseline and is demoted to reviewed
  reference. ED-10j opens a no-download kirinuki normal-dialogue font audit.
- 2026-06-17: Consumed the ED-10j font audit freeform review: Meiryo is removed
  from the normal baseline candidate path, blue badge/accent readback maps to
  Noto rather than Meiryo, and BIZ UDGothic is selected as the recommended
  default for ED-10k overlay proof.

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
