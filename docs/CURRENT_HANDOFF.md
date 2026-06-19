---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: ed10m_keifont_route_prepared_user_install_required
progress_pct: 92
last_touched: 2026-06-20
next_review_due: after_ed10m_keifont_user_install_readback
active_artifact: clip-ed10l-known-kirinuki-font-pack-001
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

The active artifact is `clip-ed10l-known-kirinuki-font-pack-001`.

ED-10j already consumed the freeform review that removed Meiryo from normal
subtitle baseline candidates. ED-10j readback also resolved the blue badge /
accent candidate to `ed10j_noto_sans_jp_local_telop_candidate`, not the Meiryo
reference. BIZ UDGothic became the ED-10k proof base.

ED-10k already generated the BIZ UDGothic diagnostic overlay proof for
`cut_002` and `cut_003`, and that proof was reviewed as not accepted for the
normal-dialogue baseline. The review says BIZ is too hard or rigid, the text
still reads thin, and the black outline pressure is too strong.

ED-10l is therefore the current route. It audits known Japanese YouTube
kirinuki / telop font candidates, but the latest local readback confirms the
current contact sheet is fallback evidence only: the requested ED-10l fonts
were not installed, and the visible samples resolved to `NotoSansJP-VF.ttf`.
Do not select a visual candidate from those PNGs.

ED-10m prepares the first real-font source/license/install/readback route. The
selected route is `ed10l_keifont_pop_dialogue_candidate`. The official Keifont
page is the source target, and local readback still shows
`C:\Windows\Fonts\keifont.ttf` / `C:\Windows\Fonts\Keifont.ttf` missing. No
font binary was downloaded, installed, copied, vendored, staged, or committed.

## Resume Order

1. Read [RUNTIME_STATE.md](RUNTIME_STATE.md).
2. Read [SUBTITLE_FONT_CANDIDATE_SWEEP.md](SUBTITLE_FONT_CANDIDATE_SWEEP.md).
3. Read [artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md).
4. Open [dashboard/index.html](dashboard/index.html), or run:

```powershell
.\open-dashboard.ps1
```

## Next Move

Use the Keifont source / license / install / readback route first, then
regenerate the ED-10l comparison or overlay proof only after the requested font
file resolves.

Good immediate candidates to route:

| Candidate route | Why it helps | Required before proof |
|---|---|---|
| `ed10l_keifont_pop_dialogue_candidate` | Strong pop/kirinuki normal-dialogue direction | User source/license inspection, local install, `keifont.ttf` / `Keifont.ttf` readback |
| `ed10l_851_chikara_yowaku_dialogue_candidate` | Softer handwritten route that avoids rigid BIZ feel | Official source, license note, installed font readback |
| `ed10l_m_plus_fonts_dialogue_candidate` | More reproducible OFL-backed route | Exact family/file/weight choice, source/license readback |

Keep `ed10l_851_chikara_zuyoku_emphasis_candidate` outside the normal dialogue
baseline; it belongs to emphasis / shout / tsukkomi.

## Artifact Access

These local `episodes/` paths are same-machine evidence and may be absent on a
fresh clone. Their absence is not a Git failure.

| Artifact | Role | Open command |
|---|---|---|
| `clip-ed10l-known-kirinuki-font-pack-001` | Current fallback/readback evidence | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1` |
| `clip-ed10k-biz-overlay-proof-001` | Reviewed rejected BIZ reference | `.\open-current-proof.ps1` |
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
