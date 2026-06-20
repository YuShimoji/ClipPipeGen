---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: ed10p_keifont_lead_representative_proof_ready
progress_pct: 100
last_touched: 2026-06-20
next_review_due: after_ed10p_keifont_human_review
active_artifact: clip-ed10p-keifont-lead-representative-proof-001
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, docs/dashboard/project-status.json, docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md, artifacts/ARTIFACTS.md
---

# Current Handoff - ClipPipeGen

## What This Is

This page is a short transfer surface for a different terminal or agent. The
authoritative resume surface remains [RUNTIME_STATE.md](RUNTIME_STATE.md).
Use this page to avoid replaying stale ED-10k prompts after the project has
already advanced to ED-10l.

## Current State

The active artifact is `clip-ed10p-keifont-lead-representative-proof-001`.

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
`cut_003`. The proof page now starts with Review Focus, target lines, the ED-10o
reference, and Review Debt for `cut_008` dense/stress coverage.

## Resume Order

1. Read [RUNTIME_STATE.md](RUNTIME_STATE.md).
2. Read [SUBTITLE_FONT_CANDIDATE_SWEEP.md](SUBTITLE_FONT_CANDIDATE_SWEEP.md).
3. Read [artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md).
4. Open [dashboard/index.html](dashboard/index.html), or run:

```powershell
.\open-dashboard.ps1
```

## Next Move

Open and review the ED-10p Keifont lead proof first. Decide whether Keifont
still works as the provisional normal-dialogue lead beyond the easiest sample,
whether body thickness / outline pressure are acceptable, and whether the new
focused proof page remains easy to judge.

Good immediate candidates to route:

| Candidate route | Why it helps | Required before proof |
|---|---|---|
| `ed10l_keifont_pop_dialogue_candidate` | Strong pop/kirinuki normal-dialogue direction | Current lead column in ED-10o |
| `ed10l_851_chikara_yowaku_dialogue_candidate` | Softer handwritten route that avoids rigid BIZ feel | Compare directly against Keifont in ED-10o |
| `ed10l_yasashisa_gothic_goodfreefonts_candidate` | Rounded gothic route | Compare directly against Keifont in ED-10o |
| `ed10l_m_plus_fonts_dialogue_candidate` | More reproducible OFL-backed route | Excluded until exact non-thin weight/style is pinned |

Keep `ed10l_851_chikara_zuyoku_emphasis_candidate` outside the normal dialogue
baseline; it belongs to emphasis / shout / tsukkomi.

## Artifact Access

These local `episodes/` paths are same-machine evidence and may be absent on a
fresh clone. Their absence is not a Git failure.

| Artifact | Role | Open command |
|---|---|---|
| `clip-ed10p-keifont-lead-representative-proof-001` | Current Keifont lead representative proof | `.\open-current-proof.ps1` |
| `clip-ed10o-multifont-focused-review-001` | Accepted focused review UX direction / font comparison reference | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1` |
| `clip-ed10n-keifont-overlay-proof-001` | Earlier Keifont proof reference | `.\open-current-proof.ps1` |
| `clip-ed10l-known-kirinuki-font-pack-001` | Regenerated real-font comparison/readback evidence | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1` |
| `clip-ed10k-biz-overlay-proof-001` | Reviewed rejected BIZ reference | See artifact registry; `open-current-proof.ps1` now points to ED-10n |
| `clip-ed10j-kirinuki-font-audit-001` | Consumed Meiryo removal / BIZ selection audit trail | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1` |

## Remote Verification Commands

Run these after pulling on another terminal:

```powershell
git status --short --branch
git rev-list --left-right --count HEAD...origin/main
git ls-files episodes
python -m json.tool docs\dashboard\project-status.json
python -m json.tool docs\font_candidates\subtitle-font-candidates.json
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
