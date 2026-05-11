# ClipPipeGen Handoff

Last updated: 2026-05-11 JST

This file is the shortest project-local handoff for resuming from another terminal. It complements `AGENTS.md`, `README.md`, and `docs/RUNTIME_STATE.md`; it does not replace them.

## Current Sync Point

- Branch: `main`
- Upstream: `origin/main`
- Latest completed feature slice: `SH-05c GUI read-only preview pack ingest`
- Current feature slice: `INT-02e yt-dlp-audio source audio URL fetch` (assistant-side implementation in progress; real URL smoke awaits user URL selection and rights / terms review)
- SH-05c implementation commit before this handoff: `5a16f75 feat(SH-05c): add preview pack GUI ingest`
- Working tree expectation after pull: clean

Resume command:

```powershell
git checkout main
git pull --ff-only origin main
```

## What Is Now Done

SH-05c is complete. The GUI has a `Preview Pack` tab that reads an existing episode directory or `preview_manifest.json` and displays:

- manifest validation state
- Status Summary
- Decision Warnings
- Artifact Links
- transcript source and `not_for_acceptance`
- cut candidate count
- context status counts
- subtitle count
- local read-only links to `preview_report.html`, `source.wav`, `fetch_receipt.json`, `transcript.json`, and `edit_pack.json`

The GUI does not run `build-local-preview-pack`, fetch, render, upload, or any network/external acquisition workflow.

## Key Files

- `gui/preview_reader.cjs` — read-only preview manifest reader and lightweight validation.
- `gui/main.cjs` — IPC handler `preview:read`.
- `gui/preload.cjs` — exposes `readPreviewPack`.
- `gui/renderer.html` / `gui/renderer.js` / `gui/styles.css` — Preview Pack tab, warnings, artifact links.
- `gui/smoke.cjs` — GUI smoke checks for preview ingest and forbidden execution controls.
- `docs/RUNTIME_STATE.md` — current slice and next action.
- `docs/FEATURE_REGISTRY.md` — feature status table and transition log.
- `docs/PREVIEW_PACK.md` — SH-05 / SH-05b / SH-05b+ / SH-05c boundary and evidence summary.
- `docs/ASSET_FETCH_BOUNDARY.md` — asset_fetch, FFmpeg, yt-dlp, GUI, STT, Editing boundaries.
- `docs/AUTOMATION_BOUNDARY.md` — automation map and forbidden surfaces.

## Validation Already Run

Last validation for SH-05c:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results:

- `uvx pytest -q` -> `114 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors

Boundary grep was also run and returned no hits for direct FFmpeg / yt-dlp / fetch-video leakage in GUI, pipeline, STT, or Editing surfaces.

## Visual Evidence

SH-05c visual evidence was generated locally from the SH-05b smoke episode:

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

- `yt-dlp-audio` real URL operator smoke (requires user URL selection and rights / terms review)
- network fetch
- `fetch-source-video`
- GUI fetch button
- GUI-triggered `build-local-preview-pack`
- cut / concat
- subtitle burn-in
- rendered video preview
- render / encode
- creative acceptance
- rights hard gate

FFmpeg remains an `asset_fetch` local media audio normalization adapter only. It must not enter STT, Editing, GUI, render, cut, concat, or subtitle burn-in surfaces.

## Recommended Next Slice

Current recommended work:

`INT-02e yt-dlp-audio real URL operator smoke`, limited to source-audio URL fetch only.

Scope constraints for that next slice:

- Add only `fetch-source-audio --mode yt-dlp-audio` or equivalent successor. Assistant-side implementation is present; external smoke remains.
- Network access and yt-dlp execution must stay inside `src/integrations/asset_fetch/`.
- FFmpeg still only normalizes fetched media to `source.wav`.
- Do not add `fetch-source-video`.
- Do not add GUI fetch button.
- Do not connect URL fetch to `transcribe-audio`.
- Do not add render / encode / cut / concat / subtitle burn-in.
- Rights status remains readback, not a hard gate.

Default executor: assistant.
User input required only for smoke URL selection and rights / terms review.

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
