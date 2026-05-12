# ClipPipeGen Handoff

Last updated: 2026-05-12 JST

This file is the shortest project-local handoff for resuming from another terminal. It complements `AGENTS.md`, `README.md`, and `docs/RUNTIME_STATE.md`; it does not replace them.

## Current Sync Point

- Branch: `main`
- Upstream: `origin/main`
- Latest completed feature slice: `INT-02e yt-dlp-audio source audio URL fetch`
- Current recommended feature slice: `SH-05d source-audio preview bridge` (proposed; connect fetched `source.wav` / receipt / ledger to local preview pack review surface)
- Latest completed feature-slice closeout before this handoff note: `7659ef1 docs(INT-02e): close yt-dlp audio smoke`
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

## Production Gap Readback

ClipPipeGen is not finished when it can only produce docs, receipts, ledgers, or read-only reports. The final shape is a production-assist pipeline that carries URL / local-media source material through an episode:

`source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles / thumbnail / NLE export / render / publishing`

Current state against that final shape:

| Area | Current state | Remaining production gap |
|---|---|---|
| Source audio | URL and local media can become `source.wav` with receipt / sidecar / ledger proof | Technical acquisition proof is not creative, production, or publishing acceptance |
| Preview surface | Local preview pack and GUI read-only ingest exist | INT-02e fetched `source.wav` is not yet directly connected to the preview pack review surface |
| Transcript | `transcribe-audio --engine fake` and fixture flows exist | No real STT adapter; fake / fixture transcript is not acceptance material |
| Edit pack | `transcript.json` can feed cut candidates, context checks, and subtitles | External editing handoff is still missing |
| NLE / render | Not implemented | No EDL/XML/FCPXML export and no mp4 / rendered video proof |
| Publishing | Not implemented | Upload / metadata / thumbnail setting / publish receipt are future integration work |

The project should continue only if the next slices add or connect real production-adjacent artifacts. A slice that only adds more policy, boundary text, report polish, or GUI read-only state without connecting `source.wav`, `transcript.json`, `edit_pack.json`, `preview_manifest.json`, NLE export, or rendered video should be treated as drift.

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

Acceptance for that next slice:

- An episode that already contains INT-02e outputs can be used without re-downloading source media.
- Existing `source.wav`, `fetch_receipt.json`, `sidecar.json`, and `material_ledger.json` are visible from the preview surface / `preview_manifest.json` / `preview_report.html`.
- The operator can decide whether the fetched source audio is ready for the next editing decision.
- The bridge reaches or connects at least one real artifact: `source.wav`, `transcript.json`, `edit_pack.json`, or `preview_manifest.json`.

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

## Next Two-Slice Pressure

After `SH-05d`, the project should deliberately move toward one of these production-adjacent artifacts:

| Candidate | Usefulness | Why it matters | Risk |
|---|---:|---|---|
| Real STT adapter / real transcript path | 9/10 | Escapes fake / fixture transcript and lets `source.wav` become usable editing text | Engine / model setup and runtime variance |
| `ED-06` minimal NLE export | 8/10 | Lets `edit_pack.json` leave ClipPipeGen and enter an external editor | Can still be fake-transcript-derived if chosen before real STT |
| `OUT-01` tiny render proof | 7/10 | Produces an actual video artifact | Audio-only source makes this weak unless source video or a deliberate visual proof is added |

Recommended continuation after `SH-05d`: prefer `ED-06` if the goal is the fastest external editing handoff, or real STT if transcript correctness is the bottleneck. Do not count GUI read-only display or audit log expansion as progress toward video production.

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
