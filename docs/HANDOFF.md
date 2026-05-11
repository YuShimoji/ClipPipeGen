# ClipPipeGen Handoff

Last updated: 2026-05-12 JST

This file is the shortest project-local handoff for resuming from another terminal. It complements `AGENTS.md`, `README.md`, and `docs/RUNTIME_STATE.md`; it does not replace them.

## Current Sync Point

- Branch: `main`
- Upstream: `origin/main`
- Latest completed feature slice: `INT-02e yt-dlp-audio source audio URL fetch`
- Current recommended feature slice: `SH-05d source-audio preview bridge` (proposed; connect fetched `source.wav` / receipt / ledger to local preview pack review surface)
- INT-02e implementation baseline before smoke: `6669de6 test(INT-02e): lock URL scrub dry-run readback`
- Working tree expectation after pull: clean

Resume command:

```powershell
git checkout main
git pull --ff-only origin main
```

## What Is Now Done

INT-02e is complete. `fetch-source-audio --mode yt-dlp-audio` is limited to source-audio URL fetch only:

- yt-dlp runs only inside `src/integrations/asset_fetch/yt_dlp_audio.py`.
- FFmpeg still only normalizes the downloaded temporary media to `source.wav`.
- The downloaded intermediate is not retained.
- The receipt records yt-dlp + FFmpeg tools, download / normalize command summaries, source URL readback, output hash/duration, rollback files, and rights snapshot.
- Rights status is readback only and `hard_gate=false`.

Technical operator smoke used ignored episode `episodes/int02e_operator_smoke_20260512` and material `src_audio_ytdlp_001`. It generated `source.wav`, `sidecar.json`, `fetch_receipt.json`, and a `material_ledger.json` entry. The smoke URL is not creative acceptance or publishing approval.

SH-05c remains complete. The GUI Preview Pack tab reads an existing episode directory or `preview_manifest.json`; it does not run `build-local-preview-pack`, fetch, render, upload, or any network/external acquisition workflow.

## Key Files

- `src/integrations/asset_fetch/yt_dlp_audio.py` — yt-dlp source-audio fetch adapter.
- `src/cli/fetch_source_audio.py` — `--mode yt-dlp-audio` CLI wiring, sidecar / receipt / ledger write.
- `docs/RUNTIME_STATE.md` — current state and next recommended action.
- `docs/FEATURE_REGISTRY.md` — feature status table and transition log.
- `docs/ASSET_FETCH_BOUNDARY.md` — asset_fetch, FFmpeg, yt-dlp, GUI, STT, Editing boundaries.
- `docs/AUTOMATION_BOUNDARY.md` — automation map and forbidden surfaces.
- `docs/PREVIEW_PACK.md` — next downstream review surface boundary.

## Validation Already Run

Last validation for INT-02e:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results:

- `uvx pytest -q` -> `122 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors

Additional smoke readback:

- `yt-dlp --version` -> `2026.03.17`
- dry-run -> `will_write=false`, `will_call_subprocess=false`, URL query / fragment scrubbed, conflicts `[]`
- actual run -> `source.wav`, sidecar, receipt, ledger entry created
- Python `wave` readback -> mono / 16kHz / 16-bit / 2.07425 seconds
- `audit-material-ledger --format json` -> `ok=true`
- artifact hygiene -> smoke episode remains ignored under `episodes/`

## Visual Evidence

SH-05c visual evidence was previously generated locally from the SH-05b smoke episode:

- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_tab.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_artifacts.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_readback.json`

These are intentionally ignored scratch artifacts and are not pushed. The project-local context and reproduction path are preserved in `docs/PREVIEW_PACK.md` and `docs/RUNTIME_STATE.md`.

Readback from the visual evidence:

- GUI state: `ready`
- validation issues: `0`
- artifact links: 6 entries, all `exists`
- Preview Pack panel forms/buttons: `0`
- forbidden video element: `0`

## Hard Boundaries Still In Force

Not implemented / not accepted yet:

- `fetch-source-video`
- GUI fetch button
- GUI-triggered `build-local-preview-pack`
- cut / concat
- subtitle burn-in
- rendered video preview
- render / encode
- creative acceptance
- rights hard gate

yt-dlp and FFmpeg remain inside `asset_fetch` for source audio only. They must not enter STT, Editing, GUI, render, cut, concat, or subtitle burn-in surfaces.

## Recommended Next Slice

Current recommended work:

`SH-05d source-audio preview bridge`, limited to connecting already fetched source audio artifacts to the existing preview-pack review surface.

Scope constraints for that next slice:

- Consume existing `source.wav`, `fetch_receipt.json`, and `material_ledger.json`.
- Do not add a new downloader.
- Do not add `fetch-source-video`.
- Do not add GUI fetch button.
- Do not connect URL fetch to `transcribe-audio`.
- Do not add render / encode / cut / concat / subtitle burn-in.
- Rights status remains readback, not a hard gate.

Default executor: assistant.
User input is not required for the first design/implementation pass unless the bridge needs a production episode URL or creative acceptance.

## Quick Operator Check

After pulling on another terminal:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
```

To inspect the GUI:

```powershell
npm start
```

Use the GUI `Preview Pack` tab with an existing episode directory or a `preview_manifest.json` path. A fresh checkout may not contain ignored smoke episodes; regenerate a local preview pack when visual inspection is needed.
