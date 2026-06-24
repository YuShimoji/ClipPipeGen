---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: visual_selector_proof_ready
progress_pct: 100
last_touched: 2026-06-24
next_review_due: none_probe_readback_only
active_artifact: clip-ed10ac-visual-selector-proof-001
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, docs/dashboard/project-status.json, docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md, artifacts/ARTIFACTS.md
---

# Current Handoff - ClipPipeGen

## What This Is

This page is a short transfer surface for a different terminal or agent. The
authoritative resume surface remains [RUNTIME_STATE.md](RUNTIME_STATE.md).
Use this page to avoid replaying stale font-family or Candidate 0-3 comparison
prompts after the project has advanced to the ED-10ab subtitle preset selector
route.

## Current State

The active artifact is `clip-ed10ac-visual-selector-proof-001`.

ED-10ac adds a tracked static visual selector proof at
`docs/style_intent/subtitle-visual-selector-proof.json` and
`docs/style_intent/subtitle-visual-selector-proof.html`. It uses the ED-10ab
examples to make neutral / shout / whisper / ominous / narration / system note
differences visible as badge, accent, backplate, size, outline/shadow, motion,
and line-break token readback. Body subtitle text color remains stable across
all six examples; speaker and emotion color remain badge/accent-first. No new
render was run because L1 Existing Output First was sufficient for this static
proof. This does not approve production subtitle design, production render,
creative use, rights, publishing, or public use. Optional user-side work is
open-only freeform observation, maximum 3 points, not a required Review Card.

ED-10ab adds a deterministic subtitle preset selector in
`src/integrations/render/subtitle_preset_selector.py` with a tracked readback
at `docs/style_intent/subtitle-preset-selector.json`. It consumes the ED-10aa
axes (`speaker_id`, `speaker_role`, `emotion`, `intensity`, `utterance_role`,
`readability_priority`) and returns token candidates for font family role, font
size scale, outline/shadow strength, badge color, accent color, backplate/box,
motion placeholder, safe-area/line-break behavior, and stable body text color.
The examples cover neutral dialogue intensity 0, shout intensity 2, whisper
intensity 1, ominous intensity 2, narration, and system note. ED-10ab did not
run a new render; it uses the existing ED-10z readback as visual source under
the L1 Existing Output First gate.

ED-10aa adds a subtitle style intent registry in
`docs/SUBTITLE_STYLE_INTENT_REGISTRY.md` and
`docs/style_intent/subtitle-style-intent-registry.json`. Future subtitle style
work should use semantic tags (`speaker_id`, `speaker_role`, `emotion`,
`intensity`, `utterance_role`, `readability_priority`) and map them to presets
instead of asking for repeated tiny outline/shadow/opacity judgements. Body
text color remains stable by default; character-specific color should normally
appear first in speaker badge/accent surfaces. Human review is reserved for new
style families, new palettes, body text color policy changes, production-route
changes, rights, publishing, or public-use decisions.

ED-10z remains the current render-path-nearer probe source. It consumes
`clip-ed10y-candidate2-carry-forward-001` as source/previous and records a tiny
diagnostic probe for Candidate 2 (`ed10w_badge_label_pressure_adjustment`).
Candidate 0 remains fallback/current-baseline reference. Candidate 1 and
Candidate 3 remain held because the consumed review says they read too thin
compared with 0 and 2. The same Candidate 0-3 comparison should not be repeated.
Neither ED-10aa nor ED-10z approves production subtitle design, production
render, creative use, rights, publishing, upload, or public use.

Layout note for this handoff: ED-10aa records that Candidate Visual Evidence
primary samples were too small/compressed. The generator now avoids a cramped
four-column primary grid, keeps Candidate 2 lead and Candidate 0 fallback more
prominent, and treats Candidate 1 / 3 as secondary held references. This is
development readback, not a new review card.

Validation note for this handoff: the ED-10z actual rerun now succeeds when
explicit FFmpeg/FFprobe paths are supplied. It returned
`visual_proof_status=available_requires_human_review`,
`review_card_status=withheld_tiny_render_path_nearer_probe_completed`,
`subtitle_overlay_available_count=1`, and
`focused_proof_review.status=tiny_render_path_nearer_probe_completed`.
Treat `subtitle_presentation_review_pack.html` / `.json` as refreshed
same-machine local evidence only; production subtitle design, production
render, creative use, rights, publishing, upload, and public use remain closed.

ED-10y implementation checkpoint, 2026-06-24 JST: `0cf35da` was pushed to
`origin/main`. This handoff note is part of a later successor commit. A
separate terminal can resume by pulling `main`, confirming `HEAD...origin/main`
is `0 0`, then opening `.\open-current-proof.ps1` if the ignored same-machine
`episodes/` artifacts are present. The tracked implementation checkpoint
contains the ED-10y generator/profile changes, dashboard refresh, launcher
label update, and tests. The local proof pack remains ignored same-machine
evidence, not Git authority.

ED-10y consumes the latest freeform review of the ED-10w/ED-10x presentation
pack. Candidate 2 (`ed10w_badge_label_pressure_adjustment`) is now the
provisional bounded-decoration lead. Candidate 0
(`ed10w_current_pass_reference`) remains fallback/current-baseline reference.
Candidate 1 and Candidate 3 are held because they read too thin compared with
0 and 2. The same Candidate 0-3 comparison should not be repeated.

The current launcher still opens
`episodes/.../subtitle_presentation_review_pack.html`, but the page is now a
Candidate 2 carry-forward/readback surface. It keeps Candidate 2 lead and
Candidate 0 fallback visible at a glance, allows larger full-frame detail
views, and records a tiny Candidate 2 diagnostic render-path-nearer probe. The
probe does not approve production subtitle design, production render, creative
use, rights, publishing, or public use.

ED-10w is now a consumed source review target. It consumes ED-10v as a passed
diagnostic dense/stress + multiline/wrap source proof and creates one new
review surface:
`episodes/.../subtitle_presentation_review_pack.html`. The root launcher
`.\open-current-proof.ps1` opens that pack when the ignored same-machine file
exists; otherwise it falls back to the retained ED-10v focused proof. The pack
does not ask for another general Keifont review on `cut_002` / `cut_003`, and
does not ask for another pass/fail judgement on the same `cut_008` multiline
evidence.

ED-10x consumed the latest review that Candidate 0-3 images were present but
their differences were almost indistinguishable. Candidate image generation is
therefore treated as technically working but not reviewable enough in the old
full-frame-only view. The regenerated pack now surfaces compact subtitle-body
crops, SPK badge crops, and actual style delta readback before the secondary
full-frame context.

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

Continue from `clip-ed10z-tiny-render-path-nearer-probe-001`. The latest
presentation review is already consumed and Candidate 2 has now passed through
the current diagnostic render path, so do not request another Candidate 0-3
comparison, another review of the corrected ED-10u `cut_008`
multiline/dense-stress surface, or general font-family acceptance from
`cut_002` / `cut_003`.

Good immediate routes:

| Route | Why it helps | What it should enable |
|---|---|---|
| `ed10z_tiny_render_path_nearer_probe` | Records Candidate 2 through the current diagnostic render path while keeping Candidate 0 fallback and Candidate 1/3 held | Another terminal can continue from probe readback without replaying the same comparison review |
| Audit ED-10y source state | Keeps the carry-forward source and probe artifact separated | A later slice can compare source/readback without treating ED-10z as production acceptance |
| FFmpeg/FFprobe tool-path rerun | Removes the current environment blocker for actual ignored proof materialization | The ED-10z HTML/JSON/PNG/MP4 proof files can be regenerated on this machine |
| production limitation-lift route | Separates diagnostic proof from public/render/rights decisions | Production subtitle design, render, rights, publishing, and public-use gates can be judged explicitly later |

Keep `ed10l_851_chikara_zuyoku_emphasis_candidate` outside the normal dialogue
baseline; it belongs to emphasis / shout / tsukkomi.

## Artifact Access

These local `episodes/` paths are same-machine evidence and may be absent on a
fresh clone. Their absence is not a Git failure.

| Artifact | Role | Open command |
|---|---|---|
| `clip-ed10z-tiny-render-path-nearer-probe-001` | Current tiny render-path-nearer diagnostic probe using Candidate 2, with Candidate 0 fallback and Candidate 1/3 held | `.\open-current-proof.ps1` -> `episodes/.../subtitle_presentation_review_pack.html` |
| `clip-ed10y-candidate2-carry-forward-001` | Source/previous Candidate 2 lead carry-forward pack with Candidate 0 fallback | Same local path history; ED-10z is the current readback |
| `clip-ed10w-subtitle-presentation-review-pack-001` | Consumed one-pass presentation review pack that selected Candidate 2 as lead and Candidate 0 as fallback | Same local path/history; do not request the same comparison again |
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
- latest pushed checkpoint is `ce24fcc` or a later successor commit
- ED-10z dry-run JSON reads `artifact_id=clip-ed10z-tiny-render-path-nearer-probe-001`,
  `review_card.action_type=NO_REVIEW_CARD_REVIEW_CONSUMED`, lead
  `ed10w_badge_label_pressure_adjustment`, fallback
  `ed10w_current_pass_reference`
- ED-10z actual rerun with explicit FFmpeg/FFprobe paths reads
  `visual_proof_status=available_requires_human_review` and
  `focused_proof_review.status=tiny_render_path_nearer_probe_completed`

## Constraints / Risks

- Do not track `episodes/`, source media, generated MP4/PNG/SRT/ASS payloads,
  or font binaries without explicit policy approval.
- Do not edit or read NLMYTGen files for this route.
- Do not claim production subtitle design, production render, creative,
  rights, publishing, upload, or public-use acceptance.
- Rights remain `pending`, and `production_candidate=false`.
