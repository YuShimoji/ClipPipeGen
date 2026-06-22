---
id: subtitle-font-candidate-sweep
title: Subtitle Font Candidate Sweep v0
type: candidate_registry
status: in_progress
health: ed10u_dense_stress_multiline_evidence_review_ready
progress_pct: 100
last_touched: 2026-06-22
next_review_due: after_ed10u_cut_008_multiline_dense_stress_review
active_artifact: clip-ed10r-keifont-dense-stress-proof-001
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
  `ed10l_keifont_pop_dialogue_candidate`
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
- Local font readback now includes HKCU registry,
  `%LOCALAPPDATA%\Microsoft\Windows\Fonts`, and `C:\Windows\Fonts`.
- ED-10n regenerated the ED-10l comparison after per-user font readback; the
  normal-dialogue samples now resolve to requested candidate font files and are
  valid same-machine visual evidence.
- Font binaries were not downloaded, copied, or vendored.
- ED-10n selected `ed10l_keifont_pop_dialogue_candidate` for the real-font
  overlay proof, and the latest review says Keifont is clearly improved.
- ED-10o is now the current review surface: a one-shot same-line comparison of
  Keifont, 851 Chikara Yowaku, and Yasashisa Gothic.
- ED-10o review surface was accepted as easier to see; ED-10p now keeps
  Keifont as provisional lead and regenerates the representative proof.
- ED-10q restored the current proof launcher/review page after the old-layout
  regression: `.\open-current-proof.ps1` now opens
  `current_proof_focused_review.html`, with Review Focus, target lines,
  subtitle-area evidence, ED-10o reference, and `cut_008` Review Debt before
  detailed/debug reports.
- ED-10t regenerated the ED-10r dense/stress proof after the current Windows
  user `PLANNER007` installed Keifont and the related ED-10l font candidates.
  The resolver now reports `requested=Keifont`, `resolved=Keifont`, and
  `font_visual_evidence.status=valid_requested_keifont_visual_evidence`.
  Review only `cut_008` dense/stress behavior; do not ask for another general
  Keifont review on `cut_002` / `cut_003`.
- ED-10u consumed the user's review note that the visible proof did not appear
  to show two-line subtitles. `cut_008` remains the right dense/stress target:
  font-bbox readback finds `sub_096` wrapping to two lines
  (`下界ニ呼ビ出シタノハキサ` / `マカ。`). The focused page now surfaces that cue
  as compact `Multiline / Wrap Evidence` near the top, with the screenshot
  capped at 220px by default.
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
| normal dialogue baseline | `ed10l_keifont_pop_dialogue_candidate`, `ed10l_851_chikara_yowaku_dialogue_candidate`, `ed10l_m_plus_fonts_dialogue_candidate`, `ed10l_yasashisa_gothic_goodfreefonts_candidate` | Pending real font source/license/install/readback before visual proof |
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

## ED-10m Real Font Source / License / Install Route

ED-10m keeps the ED-10l contact sheet as fallback evidence and chooses the
first real-font route before any visual proof regeneration. The selected route
is `ed10l_keifont_pop_dialogue_candidate` because its official page confirms a
normal-dialogue pop/kirinuki direction, Apache License 2.0, and no special
commercial-use restriction. The route still requires user-owned local install;
Codex did not download, install, vendor, or commit any font binary.

| Candidate | Intended slot | Source / license status | Local install/readback | Proof readiness | Risk / unknown |
|---|---|---|---|---|---|
| `ed10l_keifont_pop_dialogue_candidate` | normal dialogue baseline | Official source: [Keifont](https://font.sumomo.ne.jp/font_1.html). License/readback: Apache License 2.0; commercial use is not specially restricted. | Found at `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\keifont.ttf`. | Current ED-10n overlay proof base. | Source asks users to avoid usage that harms the reputation of the inspiration work; install is user-owned and no binary enters Git. |
| `ed10l_851_chikara_yowaku_dialogue_candidate` | normal dialogue baseline / softer dialogue | Official source: [851 Chikara Yowaku](https://pm85122.onamae.jp/851ch-yw.html). License/readback: commercial use including video is allowed; modification/free redistribution allowed, resale and authorship misrepresentation are not. | Found at `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\851CHIKARA-YOWAKU.ttf`. | Valid comparison candidate if Keifont is rejected. | May be too characterful for universal normal dialogue; keep separate from `851 Chikara Dzuyoku` emphasis slot. |
| `ed10l_m_plus_fonts_dialogue_candidate` | normal dialogue baseline / reproducible sans | Official source: [M+ FONTS](https://mplusfonts.github.io/). License/readback: SIL Open Font License route. | Found at `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\MPLUS1-VariableFont_wght.ttf`; registry display is `M PLUS 1 Thin`. | Do not promote until exact weight/style is pinned. | More reproducible than many free-font routes, but the current readback is not a selected bold/rounded proof route. |
| `ed10l_yasashisa_gothic_goodfreefonts_candidate` | normal dialogue baseline / rounded gothic | Official source now identified as [Yasashisa Gothic Bold V2 on BOOTH](https://booth.pm/ja/items/1833993), while GoodFreeFonts remains only an index. License/readback: BOOTH page says commercial/non-commercial and video use are allowed; the font is M+ FONTS-derived. | Found at `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\YasashisaGothicBold-V2.otf`. | Valid comparison candidate if Keifont is rejected. | Source was initially index-only in the registry; exact downloaded file and license/readme remain user-owned evidence. |

## ED-10n Per-user Font Readback and Keifont Proof

ED-10n fixes the earlier resolver blind spot. The target fonts were installed
per-user, not in `C:\Windows\Fonts`, so the generator now accepts HKCU registry
entries and `%LOCALAPPDATA%\Microsoft\Windows\Fonts` as local readback sources.
The ED-10l comparison was regenerated, then the Keifont overlay proof was
generated for `cut_002` / `cut_003`.

| Candidate | Registry display | Resolved file | Current handling |
|---|---|---|---|
| `ed10l_keifont_pop_dialogue_candidate` | `けいふぉんと (TrueType)` | `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\keifont.ttf` | Current ED-10n overlay proof base |
| `ed10l_851_chikara_yowaku_dialogue_candidate` | `851チカラヨワク (TrueType)` | `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\851CHIKARA-YOWAKU.ttf` | Valid comparison candidate; not selected yet |
| `ed10l_m_plus_fonts_dialogue_candidate` | `M PLUS 1 Thin (TrueType)` | `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\MPLUS1-VariableFont_wght.ttf` | Weight/style unpinned; do not treat as winner |
| `ed10l_yasashisa_gothic_goodfreefonts_candidate` | `やさしさゴシックボールドV2 Bold (TrueType)` | `C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\YasashisaGothicBold-V2.otf` | Valid comparison candidate; not selected yet |

## ED-10o Multi-font Focused Review

The latest user review changes the bottleneck from font thinness to review UX.
Keifont is preserved as the lead candidate, but the next review should compare
fonts in one shot rather than through another isolated single-font proof.

| Included candidate | Role in ED-10o | Review question |
|---|---|---|
| `ed10l_keifont_pop_dialogue_candidate` | Current lead | Does it still feel best when compared against alternatives on the same lines? |
| `ed10l_851_chikara_yowaku_dialogue_candidate` | Soft handwritten alternative | Is it more natural for usual dialogue, or too characterful? |
| `ed10l_yasashisa_gothic_goodfreefonts_candidate` | Rounded gothic alternative | Is it more stable/readable than Keifont without becoming generic? |

`ed10l_m_plus_fonts_dialogue_candidate` is excluded from ED-10o because current
registry readback is `M PLUS 1 Thin` via `MPLUS1-VariableFont_wght.ttf`; using
that as a baseline comparison would be misleading until a non-thin weight/style
is pinned.

ED-10o has now been reviewed as easier to see. This accepts the focused matrix
as the preferred review-surface direction. It does not accept a final baseline,
production subtitle design, production render, creative, rights, publishing, or
public-use state.

## ED-10p Keifont Provisional Baseline Evidence

ED-10p continues from the accepted ED-10o review surface direction. The user
had already judged the Keifont proof clearly improved and video-usable, and did
not select 851 Chikara Yowaku or Yasashisa Gothic over Keifont, so Keifont is
kept as diagnostic representative normal-dialogue provisional baseline
evidence. The generated artifact is
`clip-ed10p-keifont-lead-representative-proof-001`, produced with
`ed10l_keifont_pop_dialogue_candidate` for `cut_002` / `cut_003`.

ED-10q repaired the page shape for this artifact, but that was not a
font-quality review. Do not request another general Keifont acceptance pass on
`cut_002` / `cut_003`. Production subtitle design, render, creative, rights,
publishing, and public-use gates remain false or pending.

## ED-10r Keifont Dense/Stress Proof

ED-10r moves the remaining Review Debt into a narrow current proof:
`clip-ed10r-keifont-dense-stress-proof-001`. The proof profile is
`ed10r_keifont_dense_stress_proof`; it requires
`ed10l_keifont_pop_dialogue_candidate` and exactly `--target-cut cut_008`.

The review question is no longer "is Keifont generally acceptable on
`cut_002` / `cut_003`?" The question is whether `cut_008` stays readable under
dense/stress conditions: wrapping, rapid cue replacement, safe area, and
bounded outline/shadow/badge pressure. If it fails, create a bounded adjustment
slice rather than reopening the font-family sweep.

ED-10t regenerated this route after the current Windows user installed the
fonts. Current same-machine generation is valid Keifont visual evidence:
`requested=Keifont`, `resolved=Keifont`, `resolved_font_file=C:/Users/PLANNER007/AppData/Local/Microsoft/Windows/Fonts/keifont.ttf`,
and `font_visual_evidence.status=valid_requested_keifont_visual_evidence`.
ED-10u adds the missing multiline/wrap evidence requested by the user: `sub_096`
in `cut_008` is a real two-line cue, and the focused page now shows
`sample_multiline_wrap_1.png` in a compact evidence grid. Human review is now
allowed only for the corrected `cut_008` multiline/dense-stress axis.

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

1. **ED-10u multiline/dense-stress proof**: run `.\open-current-proof.ps1` and
   review the compact `sub_096` two-line screenshot plus `cut_008`
   dense/stress behavior.
2. **ED-10p baseline evidence**: keep the Keifont `cut_002` / `cut_003` proof
   as consumed history; do not ask for another general acceptance review.
3. **ED-10o focused review reference**: use the same-line matrix as accepted
   review UX direction and comparison evidence.
4. **Bounded follow-up**: if Keifont is still best but slightly off, adjust only
   one bounded axis such as outline pressure or badge treatment.
5. **Alternate ED-10l candidate**: if the user explicitly reopens font-family
   selection, promote that
   candidate into the next proof route.
6. **Google Fonts / OFL sweep**: request permission to download specific
   families, capture license/version/source metadata, and keep binaries out of
   public Git unless a repo policy is approved.
7. **Hybrid sweep**: use local system fonts for quick proof, then reproduce the
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
- 2026-06-19: Consumed the ED-10l "all candidates look thin / close to BIZ"
  feedback as missing-font fallback suspicion. Current sample readback resolves
  to `NotoSansJP-VF.ttf`, so candidate selection waits for real font
  source/license/install/readback and regenerated visual proof.
- 2026-06-20: ED-10m prepared the first real-font route:
  `ed10l_keifont_pop_dialogue_candidate`. Keifont source/license is recorded,
  local install/readback is still user-owned, and font binaries remain outside
  the repo.

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
