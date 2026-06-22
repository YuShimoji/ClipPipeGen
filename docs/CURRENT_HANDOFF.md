---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: ed10w_subtitle_presentation_review_pack_ready
progress_pct: 100
last_touched: 2026-06-23
next_review_due: review_ed10w_subtitle_presentation_pack
active_artifact: clip-ed10w-subtitle-presentation-review-pack-001
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, docs/dashboard/project-status.json, docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md, artifacts/ARTIFACTS.md
---

# Current Handoff - ClipPipeGen

## What This Is

This page is a short transfer surface for a different terminal or agent. The
authoritative resume surface remains [RUNTIME_STATE.md](RUNTIME_STATE.md).
Use this page to avoid replaying stale font-family prompts after the project
has advanced to the ED-10w subtitle presentation review pack route.

## Current State

The active artifact is `clip-ed10w-subtitle-presentation-review-pack-001`.

ED-10w is now the current handoff target. It consumes ED-10v as a passed
diagnostic dense/stress + multiline/wrap source proof and creates one new
review surface:
`episodes/.../subtitle_presentation_review_pack.html`. The root launcher
`.\open-current-proof.ps1` opens that pack when the ignored same-machine file
exists; otherwise it falls back to the retained ED-10v focused proof. The pack
does not ask for another general Keifont review on `cut_002` / `cut_003`, and
does not ask for another pass/fail judgement on the same `cut_008` multiline
evidence.

The only current ED-10w judgement is a freeform subtitle presentation choice:
keep the current pass, lighten outline/shadow pressure, adjust badge label
pressure, or use the balanced low-risk combination. A render-path readiness
card is included as a diagnostic planning probe only. It is not production
render acceptance.

ED-10j already consumed the freeform review that removed Meiryo from normal
subtitle baseline candidates. ED-10j readback also resolved the blue badge /
accent candidate to `ed10j_noto_sans_jp_local_telop_candidate`, not the Meiryo
reference. BIZ UDGothic became the ED-10k proof base.

ED-10k already generated the BIZ UDGothic diagnostic overlay proof for
`cut_002` and `cut_003`, and that proof was reviewed as not accepted for the
normal-dialogue baseline. The review says BIZ is too hard or rigid, the text
still reads thin, and the black outline pressure is too strong.

ED-10l is the current comparison/readback route and ED-10n is the current proof
route. HKCU registry and `%LOCALAPPDATA%\Microsoft\Windows\Fonts` readback now
resolve all four normal-dialogue ED-10l candidates as real requested fonts:
Keifont, 851 Chikara Yowaku, M+ FONTS, and Yasashisa Gothic. The regenerated
comparison is valid requested-font visual evidence on this same machine.

ED-10n generated the Keifont overlay proof for `cut_002` and `cut_003` using
`ed10l_keifont_pop_dialogue_candidate`. The latest review says Keifont is a
clear improvement and usable enough to compare seriously; the bottleneck is now
review UX and serial font comparison.

ED-10o generated a one-shot focused review surface. It compares Keifont, 851
Chikara Yowaku, and Yasashisa Gothic on the same lines in a subtitle-area crop
matrix, with Keifont preserved as current lead. M PLUS is excluded because its
registry readback is `M PLUS 1 Thin` via a variable font file; it needs a pinned
non-thin weight/style before baseline comparison. No font binary was
downloaded, installed, copied, vendored, staged, or committed by Codex.

ED-10o was then reviewed as easier to see. That accepts the focused review
surface as the preferred review direction, not final subtitle design or
production acceptance. Because the user did not promote 851 Chikara Yowaku or
Yasashisa Gothic over Keifont, ED-10p keeps Keifont as the provisional
normal-dialogue lead and regenerates the representative proof for `cut_002` /
`cut_003`.

ED-10q fixed the current proof review-surface regression reported after the
user ran `.\open-current-proof.ps1`: the launcher now opens
`current_proof_focused_review.html`, which starts with Review Focus, target
lines, subtitle-area evidence, the ED-10o reference, and Review Debt for
`cut_008` dense/stress coverage. The old detailed/debug overlay report remains
available from the focused page, but it is no longer the primary first view.

2026-06-22 ED-10u handoff refresh: Keifont review history is now consumed as
diagnostic representative normal-dialogue provisional baseline evidence. The
user already judged the Keifont proof clearly improved and video-usable, and
also judged the ED-10o font/review surface easier to see. ED-10q is recorded
as page-format regression repair, not font-quality review. Do not request
another general Keifont acceptance pass on `cut_002` / `cut_003`.

ED-10t regenerated the dense/stress route after the user installed Keifont and
the related ED-10l fonts for the current Windows user; same-machine generation
now resolves `requested=Keifont` and `resolved=Keifont` with
`candidate_primary_font_file_found`. ED-10u then consumed the user's note that
the visible proof did not appear to contain two-line subtitles. The cut itself
is still valid: font-bbox readback finds `sub_096` in `cut_008`, displayed at
`8.008-9.776`, wrapping as `下界ニ呼ビ出シタノハキサ` / `マカ。`. The focused HTML
now adds `Multiline / Wrap Evidence` near the top with a compact
`sample_multiline_wrap_1.png` screenshot capped at 220px by default. Review is
therefore allowed only for the corrected `cut_008` multiline/dense-stress axis.

2026-06-22 ED-10v handoff refresh: the user reviewed that corrected ED-10u
surface and said the subtitle display is good and all pass. Treat this as a
diagnostic dense/stress + multiline/wrap pass for the current Keifont subtitle
route. Do not emit another Review Card for this same `cut_008` evidence, and
do not reopen general Keifont acceptance from `cut_002` / `cut_003`. Line-break
behavior may be refined as more material appears, but that is now a
policy/readback or bounded adjustment topic, not a repeat acceptance review.
Future NLMYTGen sharing is only a design consideration in this slice; do not
read, edit, import from, or extract a shared package with NLMYTGen here.

Review Memory Ledger: Keifont normal-dialogue direction has `prior_review_count=3+`
and is accepted only for diagnostic representative review / provisional
normal-dialogue baseline plus diagnostic dense/stress pass. Production subtitle
design, production render, creative acceptance, rights, publishing, and public
use remain unaccepted. The current dense/stress axis is closed. Next valid
review axes must be new: line-break policy readback/tuning, bounded decoration
adjustment, production limitation-lift, or render-path probe.

## Resume Order

1. Read [RUNTIME_STATE.md](RUNTIME_STATE.md).
2. Read [SUBTITLE_FONT_CANDIDATE_SWEEP.md](SUBTITLE_FONT_CANDIDATE_SWEEP.md).
3. Read [artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md).
4. Open [dashboard/index.html](dashboard/index.html), or run:

```powershell
.\open-dashboard.ps1
```

## Next Move

Review `clip-ed10w-subtitle-presentation-review-pack-001` once, as a new-axis
subtitle presentation pack. Do not request another review of the corrected
ED-10u `cut_008` multiline/dense-stress surface; ED-10v records it as passed.
Do not reopen general font-family acceptance from `cut_002` / `cut_003`.

Good immediate routes:

| Route | Why it helps | What it should enable |
|---|---|---|
| `ed10w_subtitle_presentation_review_pack` | Combines bounded decoration candidates with render-path readiness in one page | A single freeform review can choose the next subtitle presentation move without replaying old proof acceptance |
| render-path readiness probe | Keeps renderer work tiny and diagnostic | A later slice can test output-readiness without claiming production render acceptance |
| production limitation-lift route | Separates diagnostic proof from public/render/rights decisions | Production subtitle design, render, rights, publishing, and public-use gates can be judged explicitly later |

Keep `ed10l_851_chikara_zuyoku_emphasis_candidate` outside the normal dialogue
baseline; it belongs to emphasis / shout / tsukkomi.

## Artifact Access

These local `episodes/` paths are same-machine evidence and may be absent on a
fresh clone. Their absence is not a Git failure.

| Artifact | Role | Open command |
|---|---|---|
| `clip-ed10w-subtitle-presentation-review-pack-001` | Current one-pass presentation review pack with bounded decoration candidates and render-path readiness card | `.\open-current-proof.ps1` -> `episodes/.../subtitle_presentation_review_pack.html` |
| `clip-ed10r-keifont-dense-stress-proof-001` | Consumed cut_008 multiline/dense-stress diagnostic pass with valid Keifont evidence and compact `sub_096` screenshot evidence | Fallback from `.\open-current-proof.ps1` -> `episodes/.../current_proof_focused_review.html` |
| `clip-ed10p-keifont-lead-representative-proof-001` | Consumed provisional normal-dialogue baseline evidence | See artifact registry; do not request another general cut_002/cut_003 Keifont review |
| `clip-ed10o-multifont-focused-review-001` | Accepted focused review UX direction / font comparison reference | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1` |
| `clip-ed10n-keifont-overlay-proof-001` | Earlier Keifont proof reference | See artifact registry; root launcher now opens ED-10r dense/stress proof |
| `clip-ed10l-known-kirinuki-font-pack-001` | Regenerated real-font comparison/readback evidence | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1` |
| `clip-ed10k-biz-overlay-proof-001` | Reviewed rejected BIZ reference | See artifact registry; root launcher no longer opens old BIZ/ED-10n proof surfaces |
| `clip-ed10j-kirinuki-font-audit-001` | Consumed Meiryo removal / BIZ selection audit trail | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1` |

## Remote Verification Commands

Run these after pulling on another terminal:

```powershell
git status --short --branch
git rev-list --left-right --count HEAD...origin/main
git ls-files episodes
uvx python -m json.tool docs\dashboard\project-status.json
uvx python -m json.tool docs\font_candidates\subtitle-font-candidates.json
uvx pytest -q tests/test_docs_dashboard.py tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py
```

Expected tracked state:

- branch is `main`
- `HEAD...origin/main` is `0 0`
- `git ls-files episodes` prints nothing
- dashboard JSON parses
- font candidate JSON parses
- targeted tests pass, with optional skips depending on local media and Pillow

## Constraints / Risks

- Do not track `episodes/`, source media, generated MP4/PNG/SRT/ASS payloads,
  or font binaries without explicit policy approval.
- Do not edit or read NLMYTGen files for this route.
- Do not claim production subtitle design, production render, creative,
  rights, publishing, upload, or public-use acceptance.
- Rights remain `pending`, and `production_candidate=false`.
