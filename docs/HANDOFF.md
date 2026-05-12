# ClipPipeGen Handoff

Last updated: 2026-05-12 JST

This file is the shortest project-local handoff for resuming from another terminal. It complements `AGENTS.md`, `README.md`, and `docs/RUNTIME_STATE.md`; it does not replace them.

## Current Sync Point

- Branch: `main`
- Upstream: `origin/main`
- Latest completed feature slice: `SH-05d source-audio preview bridge` (implemented; reproducible existing-source-audio smoke passed; real INT-02e artifact smoke pending until ignored artifact is available again)
- Current recommended decision: choose `ED-06 minimal NLE export` vs real STT adapter based on the next visible production bottleneck
- Latest completed feature-slice closeout before this handoff note: local SH-05d implementation in the current working tree
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

SH-05d is complete. `build-local-preview-pack --use-existing-source-audio` consumes an existing `source_audio` material entry without re-downloading source media:

- The bridge resolves `source.wav` and `sidecar.json` from `material_ledger.json`.
- It detects sibling `fetch_receipt.json` and adds receipt / sidecar / ledger references to `preview_manifest.json`.
- The report adds `Source Audio Provenance` with mode, provider, command summary, source URL/local path, tool versions, rights snapshot, intermediate retention, and output hash.
- Fake / fixture transcript and the generated `edit_pack.json` are explicitly marked as preview-only, not production candidates.
- GUI Preview Pack ingest remains read-only; it can validate the new manifest fields and artifact links but does not run build, fetch, render, upload, or network/external acquisition workflows.
- Closeout smoke used ignored reproducible episode `episodes/sh05d_existing_source_audio_smoke_20260512`. It proves the bridge behavior without network / downloader. The original ignored INT-02e real smoke episode was not present locally, so a real INT-02e artifact smoke remains pending until those artifacts are regenerated or restored.

## Production Gap Readback

ClipPipeGen is not finished when it can only produce docs, receipts, ledgers, or read-only reports. The final shape is a production-assist pipeline that carries URL / local-media source material through an episode:

`source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles / thumbnail / NLE export / render / publishing`

Current state against that final shape:

| Area | Current state | Remaining production gap |
|---|---|---|
| Source audio | URL and local media can become `source.wav` with receipt / sidecar / ledger proof | Technical acquisition proof is not creative, production, or publishing acceptance |
| Preview surface | Local preview pack, GUI read-only ingest, and SH-05d existing-source-audio bridge exist | The surface still uses fake / fixture transcript and draft edit_pack, so it is not final edit acceptance |
| Transcript | `transcribe-audio --engine fake` and fixture flows exist | No real STT adapter; fake / fixture transcript is not acceptance material |
| Edit pack | `transcript.json` can feed cut candidates, context checks, and subtitles | External editing handoff is still missing |
| NLE / render | Not implemented | No EDL/XML/FCPXML export and no mp4 / rendered video proof |
| Publishing | Not implemented | Upload / metadata / thumbnail setting / publish receipt are future integration work |

The project should continue only if the next slices add or connect real production-adjacent artifacts. A slice that only adds more policy, boundary text, report polish, or GUI read-only state without connecting `source.wav`, `transcript.json`, `edit_pack.json`, `preview_manifest.json`, NLE export, or rendered video should be treated as drift.

## Key Files

- `src/integrations/asset_fetch/yt_dlp_audio.py` — yt-dlp source-audio fetch adapter.
- `src/cli/fetch_source_audio.py` — `--mode yt-dlp-audio` CLI wiring, sidecar / receipt / ledger write.
- `src/cli/build_local_preview_pack.py` — local preview pack orchestration and `--use-existing-source-audio` bridge.
- `src/pipeline/preview_pack.py` — preview manifest / report generation and source audio provenance readback.
- `gui/preview_reader.cjs` — read-only preview manifest ingest and artifact link validation.
- `docs/RUNTIME_STATE.md` — current state and next recommended action.
- `docs/FEATURE_REGISTRY.md` — feature status table and transition log.
- `docs/ASSET_FETCH_BOUNDARY.md` — asset_fetch, FFmpeg, yt-dlp, GUI, STT, Editing boundaries.
- `docs/AUTOMATION_BOUNDARY.md` — automation map and forbidden surfaces.
- `docs/PREVIEW_PACK.md` — next downstream review surface boundary.

## Validation Already Run

Last validation for SH-05d:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results:

- `uvx pytest -q` -> `123 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors

Additional targeted readback:

- `uvx pytest -q tests/test_preview_pack.py tests/test_asset_fetch_boundary.py` -> targeted preview/boundary tests pass
- existing source audio mode does not call `fetch-source-audio`
- `preview_manifest.json` includes `source_wav`, `fetch_receipt`, `sidecar`, `material_ledger`, `ledger_entry`, and `source_audio_provenance`
- `preview_report.html` includes `Source Audio Provenance` and production-candidate warnings for fake / fixture transcript and generated edit_pack
- ignored `episodes/sh05d_existing_source_audio_smoke_20260512` readback -> manifest provenance refs present, report provider/tool/URL/hash/rights snapshot visible, GUI reader `state=ready`
- real INT-02e artifact smoke -> pending because the prior ignored `episodes/int02e_operator_smoke_20260512` artifact was not present in this working tree

## Resume-Time Environment Drift (2026-05-12 secondary readback)

The earlier INT-02e closeout validation used a different shell/environment from one secondary readback on the same day. The drift items below remain useful context, but SH-05d is complete and PowerShell validation for this slice passed. Read this section before touching GUI / TH-01 walkthrough / INT-02e re-smoke work.

### Electron smoke now fails in this environment

- Command: `npm run smoke:electron`. Also reproduced via `node_modules/electron/dist/electron.exe . --smoke` and `node_modules/electron/dist/electron.exe gui/main.cjs --smoke`.
- Result: `TypeError: Cannot read properties of undefined (reading 'handle')` at `gui/main.cjs:30` (`ipcMain.handle("episode:status", ...)`).
- Root signal: a probe script run via `electron.exe` shows `require('electron')` returning the binary path **string** instead of the Electron API object, so the destructured `app` / `BrowserWindow` / `ipcMain` are all undefined. `app.whenReady` is never reached because `ipcMain.handle` throws first.
- Environment: invoked from git-bash on Windows. `node_modules/electron/dist/version` reports `42.0.0`; `electron.exe --version` reports its bundled `v24.15.0` (Node). `gui/main.cjs` is unchanged since the INT-02e closeout.
- Status of the HANDOFF claim `npm run smoke:electron -> electron smoke: OK`: currently inaccurate from git-bash on this machine, but PowerShell validation after SH-05d passed. Resolution of the git-bash-specific launcher drift is deferred and should not be mixed into production-pipeline slices.
- Impact on SH-05d: none. SH-05d is CLI / pipeline / preview artifact work and does not depend on changing the Electron main-process boot path. GUI Preview Pack visual re-check on the SH-05d output is a follow-up, not a SH-05d blocker.

### TH-01 real walkthrough still depends on `config/nlmytgen_path.json`

- File present: `config/nlmytgen_path.json.example` only. The real `config/nlmytgen_path.json` is `.gitignore`d by design.
- Without that real config, `audit-thumbnail` / `patch-thumbnail` cannot reach the NLMYTGen CLI bridge, so the user-owned TH-01 acceptance step in `FIRST_SLICE.md` DoR (real YMM4 base template `.ymmp` → end-to-end walkthrough) cannot be replayed here.
- This is independent of SH-05d. SH-05d consumes existing source-audio / preview-pack artifacts and does not touch the NLMYTGen bridge. TH-01 acceptance and SH-05d run on separate timelines.

### INT-02e re-smoke needs ffmpeg + yt-dlp on PATH

- `which ffmpeg` / `which yt-dlp` in the current git-bash shell both return not-found.
- The previous INT-02e real smoke used `uv tool install yt-dlp` (yt-dlp `2026.03.17`) and gyan.dev FFmpeg `8.0.1-full_build` resolved through the user's PowerShell / system PATH. Reproducing the smoke needs either the same `uv tool install` path, the user's PowerShell environment where these tools already resolved, or an equivalent local install.
- Python tests are unaffected: `tests/test_ytdlp_audio_adapter.py` / `tests/test_ffmpeg_audio_adapter.py` / `tests/test_asset_fetch_boundary.py` use fake runners and monkeypatch and do not call the real binaries.
- SH-05d does not require a fresh INT-02e fetch. The bridge consumes existing `source.wav`, `fetch_receipt.json`, `sidecar.json`, and `material_ledger.json` produced by earlier runs. A re-smoke of INT-02e is only needed if the input artifact set has to be regenerated for some other reason.

## Visual Evidence

SH-05c visual evidence was previously generated locally from the SH-05b smoke episode:

- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_tab.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_artifacts.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_readback.json`

These are intentionally ignored scratch artifacts and are not pushed. The project-local context and reproduction path are preserved in `docs/PREVIEW_PACK.md` and `docs/RUNTIME_STATE.md`.

Readback from the visual evidence:

- GUI state: `ready`
- validation issues: `0`
- artifact links: 6 entries in the old SH-05c evidence; new SH-05d manifests expose sidecar and material ledger links as well
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

SH-05d is no longer the next slice; it is done. The next useful move should produce or export a production-adjacent artifact rather than adding more read-only surface.

Recommended default: `ED-06 minimal NLE export` if there is no concrete transcript-quality blocker. It turns existing `edit_pack.json` into an artifact that can leave ClipPipeGen and enter an external editor.

Alternative: real STT adapter if the producer is already correcting fake / fixture transcript text before cut, subtitle, or context decisions can be trusted.

## Next Two-Slice Pressure

After `SH-05d`, the project should deliberately move toward one of these production-adjacent artifacts:

| Candidate | Usefulness | Why it matters | Risk |
|---|---:|---|---|
| Real STT adapter / real transcript path | 9/10 | Escapes fake / fixture transcript and lets `source.wav` become usable editing text | Engine / model setup and runtime variance |
| `ED-06` minimal NLE export | 8/10 | Lets `edit_pack.json` leave ClipPipeGen and enter an external editor | Can still be fake-transcript-derived if chosen before real STT |
| `OUT-01` tiny render proof | 7/10 | Produces an actual video artifact | Audio-only source makes this weak unless source video or a deliberate visual proof is added |

Recommended continuation after `SH-05d`: prefer `ED-06` if the goal is the fastest external editing handoff, or real STT if transcript correctness is the bottleneck. Do not count GUI read-only display or audit log expansion as progress toward video production.

### Decision criteria after SH-05d (`ED-06` vs real STT)

The choice between `ED-06` and a real STT adapter after SH-05d should be made from observable production signals, not from speculative quality.

Prefer **`ED-06` minimal NLE export** when:

- The producer's bottleneck is "I cannot get `edit_pack.json` into Resolve / Premiere / DaVinci," i.e. pipeline outputs accumulate inside ClipPipeGen with no downstream consumer.
- The current fake / fixture transcript is acceptable as a placeholder for editing decisions because the operator re-times manually in the NLE anyway.
- The deciding factor is "shortest path to the first artifact that leaves ClipPipeGen."

Prefer **real STT adapter** when:

- The operator is visibly hand-correcting `transcript.json` before it is useful for cuts or subtitles, i.e. the transcript itself is the bottleneck.
- `ED-04 generate-subtitles` output is being treated as "structure only, ignore text" downstream.
- A nearby slice (subtitle review, context check, or cut tuning) is repeatedly stalled on transcript correctness rather than on missing tooling.

Tiebreaker when both signals are weak: default to `ED-06`. It has lower environment-setup cost than a real STT engine and directly converts existing pipeline outputs into a production-adjacent artifact. Real STT introduces engine / model / runtime variance and is better triggered by a concrete transcript-correctness pain.

`OUT-01` tiny render proof stays a later candidate. Without source-video acquisition, an audio-only render demonstration is weak; reorder only when source video moves.

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
