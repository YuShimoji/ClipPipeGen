# ClipPipeGen Handoff

Last updated: 2026-05-25 JST

This file is the shortest project-local handoff for resuming from another terminal. It complements `AGENTS.md`, `README.md`, and `docs/RUNTIME_STATE.md`; it does not replace them.

## Current Sync Point

- Branch: `main`
- Upstream: `origin/main`
- Latest completed feature slice: `ED-09` transcript review / correction workflow. `review-transcript` now applies v1 review patches to transcript text/status/notes, `status-episode` reads transcript review counts, and `export-nle` reports transcript review state instead of a fixed unreviewed warning.
- Current recommended decision: verify the ED-09 path on JP-Pilot-01 by creating a small review patch, running `review-transcript --dry-run`, then regenerating cuts/subtitles/NLE/render with existing `--replace-auto` flags. Next choices after that are STT provider comparison or production render/subtitle design, depending on the corrected transcript result.
- JP-Pilot-01 rights note: the ignored episode proved fetch/edit/render/export plumbing, but its `rights_manifest.json` remained skeleton/fetch readback pending and was not schema-passed rights approval.
- Sync commit: ED-09 transcript review / correction closeout on `main` (see latest `git log --oneline -1` after pull)
- Latest implementation slice: current `main` — ED-09 done。`review-transcript` CLI と pipeline patch 適用、`status-episode` review readback、`export-nle` warning 更新、docs registry 更新を含む
- Previous feature slice: `JP-Pilot-01` Japanese public VOD diagnostic
  1. `transcribe-audio --engine vosk --language ja --model vosk-model-small-ja-0.22` は language/model check passed で 26 segments を生成
  2. `generate-cuts` は 6 selected cuts、`check-cut-context` は 3 passed / 3 needs_review、`generate-subtitles` は 17 real_transcript subtitle drafts
  3. `render-tiny-proof --burn-in-subtitles diagnostic` は 6.6s / 1080p render、`export-nle` は 6 CSV rows、`audit-material-ledger` は ok
- Previous recommendation resolved by ED-09: JP-Pilot-01 showed that raw Vosk JP transcript needed human correction before cuts / subtitles / NLE / render could be judged. That correction entry point now exists; the remaining question is whether corrected transcript quality is enough to move toward production render/subtitle design or whether STT provider comparison should come first.
- Latest completed feature-slice closeout before this handoff note: ED-07c language/model validation closeout
- Latest local verification: 2026-05-25 JST ED-09 closeout; `uvx pytest -q` (188 passed), `npm run smoke` OK, `npm run smoke:electron` OK, `git diff --check` clean.
- Working tree expectation after pull: clean

## Resume on another terminal

```powershell
git checkout main
git pull --ff-only origin main
# read these to pick up state:
#   docs/HANDOFF.md
#   docs/RUNTIME_STATE.md
#   docs/HOLOEN_PILOT.md  # HoloEN-01 runbook / URL selection / acceptance
#   docs/FEATURE_REGISTRY.md
```

HoloEN-01 and JP-Pilot-01 are already done. For another fresh pilot, assistant may self-select a low-risk public VOD following the same exclusion rules documented in `docs/HOLOEN_PILOT.md` and `docs/JP_PILOT.md`, or operator may supply a URL explicitly.

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

ED-06 is complete as a minimal external editing handoff. `export-nle` consumes `edit_pack.json` and writes a CSV cut list plus readback files:

- The chosen export format is `csv_cut_list_v1`, backed by `nle_cut_list.csv`.
- The export includes cut id, selected state, title/reason, start/end/duration seconds, source type, confidence, context status, source segment ids, subtitle ids/text/ranges, and source audio refs.
- When a sibling or explicit `preview_manifest.json` exists, the export carries source audio provenance such as provider, mode, source URL, output hash, and rights status snapshot.
- `nle_export_manifest.json` and `nle_export_report.html` read back the generated artifact paths and warnings.
- Fake / fixture transcript derived exports keep `production_edit_candidate=false` and warning text; the output can leave ClipPipeGen for external review, but it is not production edit acceptance.

ED-07b is complete as a real transcript plumbing proof. `transcribe-audio --engine vosk` is an optional local STT path that consumes an existing `source.wav` and writes a `transcript.json` with provider/model/source-audio readback:

- The adapter lives under `src/integrations/stt/` and is optional; Vosk and its model are not vendored into the repo.
- `transcribe-audio --dry-run --format json` preflights provider importability, model directory, and mono 16-bit PCM WAV shape. Missing provider/model is an explicit failure, not a fallback to fixture data.
- `transcript.json` now records `stt.provider`, `stt.model`, `stt.real_transcript`, `stt.segment_count`, top-level `segment_count`, and source audio duration/sample rate/channel readback when available.
- The same transcript feeds `generate-cuts`, `check-cut-context`, `generate-subtitles`, and `export-nle`.
- ED-06 export now reads sibling or explicit `transcript.json` and carries transcript provider/engine/model/real flag/segment count/duration into CSV, manifest, and HTML report.
- This is still not STT quality, creative edit, rights, render, or publishing acceptance. Real transcript output remains draft/unreviewed unless a human review slice marks it otherwise.

INT-02f is complete as local source video acquisition. `fetch-source-video --mode local-media-video` consumes an existing local video file, copies it into the episode material directory, and records provenance plus technical metadata:

- The output file is `materials/<material_id>/source_video.<ext>`; the input extension is preserved.
- The command writes `sidecar.json`, `fetch_receipt.json`, and a `material_ledger.json` entry with `kind="source_video"`, `subkind="source_video_original"`, and `intended_uses=["editing_video"]`.
- FFprobe metadata is read back into receipt and sidecar: duration, container, video codec, audio codec if present, resolution, fps/frame_rate, and stream counts.
- Rights status is stored as a snapshot with `hard_gate=false`; pending rights and smoke/local fixture materials are not production/creative/publish acceptance.
- This is not render/encode. It does not cut, concat, burn subtitles, add a GUI fetch button, fetch URL video, or publish.

OUT-01 is complete as a tiny diagnostic render proof. `render-tiny-proof` consumes an existing `source_video` material, a `source_audio` material, and `edit_pack.json`, then writes a short rendered artifact plus readback files:

- The output directory is `episodes/<episode_id>/renders/<output_id>/`.
- The rendered file is `rendered_video.mp4` by default, with `.mkv` available when the environment needs it.
- The command writes `render_receipt.json`, `render_manifest.json`, and `render_report.html`.
- Timeline mapping uses the first selected cut from `edit_pack.json`; if the cut range exceeds source video/audio duration or `--duration-sec`, it clamps to the shortest available diagnostic range and records warnings.
- Output metadata is probed with FFprobe: duration, container, video codec, audio codec, resolution, fps, and stream counts.
- This is not production render, creative acceptance, subtitle burn-in, GUI render action, URL video fetch, or publishing.

OUT-01a is complete as render preflight / fallback readback hardening. The same `render-tiny-proof` output path now makes failure diagnosis visible instead of only proving one successful render:

- FFmpeg and FFprobe are discovered and version-checked before render; missing tools classify as `environment_missing_ffmpeg` / `environment_missing_ffprobe`.
- Auto render profiles prefer `mp4 / libx264 / aac`, then codec fallback, with `mkv` fallback candidates preserved in the command plan.
- Each attempted profile records status, selected flag, failure reason, command summary, and stderr digest in receipt / manifest.
- Failed render attempts after context resolution still write `render_receipt.json`, `render_manifest.json`, and `render_report.html` with `failure_classification`.
- Fresh ignored smoke episode `episodes/out01a_hardened_smoke_20260513` regenerated `renders/out01a_hardened/rendered_video.mp4`; output readback was duration `2.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `160x90`, fps `15.0`, stream count `2`.
- This remains diagnostic render subsystem hardening, not production render, creative acceptance, subtitle burn-in, URL video acquisition, GUI render action, or publishing.

OUT-01b is complete as a longer local video render smoke. It keeps the OUT-01a render path and uses local fixture media to exercise duration / stream / timeline mapping without adding URL video acquisition or subtitle burn-in:

- Fresh ignored smoke episode `episodes/out01b_long_local_render_smoke_20260513` uses synthetic local input `_tmp/out01b_long_local_input.mp4` and registers source video material `src_video_out01b_long_local`.
- Source video readback: duration `14.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`.
- Source audio material `src_audio_out01b_long_local` is normalized to `source.wav`; render manifest readback records duration `14.016`, codec `pcm_s16le`, sample rate `16000`, channels `1`.
- Selected cut `cut_out01b_long_001` maps `1.0` -> `13.0` seconds with duration target `12.0`; timeline policy remains `single_selected_cut_clamped_to_shortest_input_no_loop_no_speed_change_no_subtitle_burn_in`, and clamp did not occur.
- Render output `renders/out01b_long_local/rendered_video.mp4` readback: duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`.
- Selected profile is `mp4_h264_aac`; attempted profile list is `mp4_h264_aac`; fallback did not occur. Receipt / manifest / report still expose FFmpeg/FFprobe preflight, attempts, selected profile, warnings, and non-production status.
- This remains diagnostic render coverage, not production render, creative acceptance, subtitle burn-in, URL video acquisition, GUI render action, or publishing.

OUT-01c is complete as subtitle burn-in diagnostic. It keeps the OUT-01a / OUT-01b render path and adds only an optional diagnostic overlay mode:

- CLI shape is `render-tiny-proof --burn-in-subtitles diagnostic`; default remains `off`.
- Subtitle source priority is `edit_pack.subtitles[]` first, then sibling `transcript.json` segments as diagnostic fallback. No hardcoded drawtext string is accepted as proof.
- The CLI writes `diagnostic_subtitles.srt` into the render output directory and passes it to FFmpeg's `subtitles` filter.
- `render_receipt.json`, `render_manifest.json`, and `render_report.html` now expose `subtitle_burn_in.status`, `subtitle_source_ref`, `subtitle_overlay_policy`, rendered timeline subtitle items, selected profile, attempted profiles, fallback status, and output metadata.
- Fresh ignored smoke episode `episodes/out01c_subtitle_burnin_smoke_20260513` generated `renders/out01c_subtitle_burnin/rendered_video.mp4` from local source video `src_video_out01c_subtitle`, source audio `src_audio_out01c_subtitle`, selected cut `cut_out01c_subtitle_001`, and generated edit_pack subtitle drafts `sub_001` / `sub_002` / `sub_003`.
- Output readback was duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`; selected/attempted profile was `mp4_h264_aac`; fallback did not occur.
- This remains diagnostic visual proof. It is not production subtitle design, typography polish, safe-area/layout acceptance, creative edit acceptance, URL video acquisition, GUI render action, or publishing.

OUT-01d is complete as subtitle timing / font-filter preflight hardening. It keeps the OUT-01c diagnostic overlay path and makes the timing and environment diagnosis explicit:

- Subtitle item readback now includes original source timeline start/end, rendered timeline start/end, render_start offset, and status.
- Possible item statuses are `included`, `clamped_to_render_window`, `skipped_before_render_window`, `skipped_after_render_window`, `invalid_timing`, and `empty_text`.
- Only `included` / `clamped_to_render_window` items are written to `diagnostic_subtitles.srt`; skipped / invalid / empty items remain in receipt / manifest / report readback.
- `subtitle_burn_in.timing_mapping` records the mapping policy, render window, offset, status counts, renderable count, and skipped/invalid count.
- `subtitle_burn_in.filter_preflight` records FFmpeg subtitles filter validation mode, SRT UTF-8 write status, path escaping policy, and failure detail buckets for subtitles filter / libass / fontconfig / font provider / SRT parsing / path escaping failures.
- Fresh ignored smoke episode `episodes/out01d_timing_font_preflight_smoke_20260514` generated `renders/out01d_timing_font_preflight/rendered_video.mp4` from local source video `src_video_out01d_timing`, source audio `src_audio_out01d_timing`, selected cut `cut_out01d_timing_001`, and edit_pack subtitle drafts that exercise included / clamped / skipped timing.
- Output readback was duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`; selected/attempted profile was `mp4_h264_aac`; fallback did not occur; filter status was `passed_by_successful_render`.
- This remains diagnostic render hardening. It is not production subtitle design, typography polish, safe-area/layout acceptance, creative edit acceptance, URL video acquisition, GUI render action, or publishing.

ED-08 / OUT-01e is complete as real STT subtitle draft linkage and diagnostic render smoke. It keeps ED-07b real transcript plumbing and OUT-01d timing diagnostics, but connects them through `edit_pack.subtitles[]`:

- `generate-subtitles` reads `transcript.stt.real_transcript=true` and writes subtitle drafts with `source_type="real_transcript"`, `source_segment_ids[]`, `draft=true`, `diagnostic=true`, `not_production_subtitle_design=true`, and `production_subtitle_design=false`.
- Fake / fixture transcript inputs stay `source_type="transcript_segments"` and do not become production candidates.
- `render-tiny-proof --burn-in-subtitles diagnostic` still prioritizes `edit_pack.subtitles[]`, but now reads subtitle provenance into `subtitle_burn_in.source_ref.subtitle_source_type`, `subtitle_source_types[]`, `derived_from_real_transcript`, transcript provider/model, and `source_segment_ids[]`.
- OUT-01d timing mapping remains intact: original/render time, render_start offset, status counts, included/clamped/skipped/invalid/empty statuses, filter preflight, and disabled burn-in behavior are still tested.
- Fresh ignored smoke episode `episodes/out01e_real_transcript_subtitle_smoke_20260516` used synthetic local TTS audio normalized to `source.wav`, Vosk model `_tmp/stt_models/vosk-model-small-en-us-0.15`, source audio material `src_audio_out01e_real_stt`, and local source video material `src_video_out01e_local`.
- Smoke output `renders/out01e_real_transcript_subtitle_render/rendered_video.mp4` was generated with `subtitle_burn_in.status=enabled`, `derived_from_real_transcript=true`, status counts `included=1`, output duration `8.82`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24/1`, stream count `2`.
- This remains diagnostic linkage. It is not STT quality acceptance, transcript correction UI, production subtitle design, creative acceptance, URL video acquisition, GUI render action, publishing, FCPXML, or Resolve XML.

JP-Pilot-01 is complete as a Japanese public VOD diagnostic. It reused the existing URL/source media, Vosk JP, edit_pack, subtitle, render, and NLE export path without adding new production surfaces:

- Selected source: official hololive short anime `【アニメ】押忍！！ば～んちょ だじぇ！` at <https://www.youtube.com/watch?v=7J5aS_pcBj4>.
- Ignored episode `episodes/jp_pilot01_hololive_bancho_20260525` generated `source_video.mp4`, `source.wav`, `transcript.json`, `edit_pack.json`, `renders/jp_pilot01_diagnostic_render/rendered_video.mp4`, and `exports/jp_pilot01/nle_cut_list.csv`.
- Readback: 26 transcript segments, speech coverage about 51.4%, 6 selected cut candidates, 3 passed / 3 needs_review, 17 subtitle drafts, 6.6s 1080p diagnostic render, 6 NLE CSV rows, ledger audit ok.
- The transcript is technically real but not creatively acceptable as-is; the next bottleneck is transcript review / correction, not render polish or publishing.

## Production Gap Readback

ClipPipeGen is not finished when it can only produce docs, receipts, ledgers, or read-only reports. The final shape is a production-assist pipeline that carries URL / local-media source material through an episode:

`source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles / thumbnail / NLE export / render / publishing`

Current state against that final shape:

| Area | Current state | Remaining production gap |
|---|---|---|
| Source audio | URL and local media can become `source.wav` with receipt / sidecar / ledger proof | Technical acquisition proof is not creative, production, or publishing acceptance |
| Source video | Local video and URL video can become `source_video.<ext>` with receipt / sidecar / ledger proof and FFprobe metadata | Technical acquisition proof is not creative, production, or publishing acceptance |
| Preview surface | Local preview pack, GUI read-only ingest, and SH-05d existing-source-audio bridge exist | The surface still uses fake / fixture transcript and draft edit_pack, so it is not final edit acceptance |
| Transcript | `transcribe-audio --engine fake` and optional `--engine vosk --model <path>` exist; JP-Pilot-01 proves Vosk JP can process a public Japanese VOD | STT quality review / correction workflow is now the main bottleneck; real transcript output remains unreviewed draft |
| Edit pack | `transcript.json` can feed cut candidates, context checks, subtitles, and ED-06 CSV export; JP-Pilot-01 produced 6 cuts and 17 real_transcript subtitle drafts | 3/6 cuts needed review, so corrected transcript and human review readback should come before production edit acceptance |
| NLE / render | Minimal CSV cut list export exists; OUT-01b can produce a diagnostic video; OUT-01c/OUT-01d can burn and diagnose subtitle timing; JP-Pilot-01 burned JP real STT subtitles into a diagnostic 1080p render | No FCPXML / Resolve XML, no production subtitle design, no STT quality acceptance, and no production render acceptance |
| Publishing | Not implemented | Upload / metadata / thumbnail setting / publish receipt are future integration work |

The project should continue only if the next slices add or connect real production-adjacent artifacts. A slice that only adds more policy, boundary text, report polish, or GUI read-only state without connecting `source.wav`, `transcript.json`, `edit_pack.json`, `preview_manifest.json`, NLE export, or rendered video should be treated as drift.

## Key Files

- `src/integrations/asset_fetch/yt_dlp_audio.py` — yt-dlp source-audio fetch adapter.
- `src/integrations/asset_fetch/source_video.py` — local source video copy/probe adapter.
- `src/integrations/render/ffmpeg_tiny.py` — OUT-01 FFmpeg/FFprobe tiny render adapter.
- `src/cli/fetch_source_audio.py` — `--mode yt-dlp-audio` CLI wiring, sidecar / receipt / ledger write.
- `src/cli/fetch_source_video.py` — `--mode local-media-video` CLI wiring, sidecar / receipt / ledger write.
- `src/cli/render_tiny_proof.py` — `render-tiny-proof` CLI wiring, receipt / manifest / report write.
- `src/pipeline/subtitle_generation.py` — transcript segments to `edit_pack.subtitles[]` draft generation, including real transcript source readback.
- `src/cli/build_local_preview_pack.py` — local preview pack orchestration and `--use-existing-source-audio` bridge.
- `src/pipeline/preview_pack.py` — preview manifest / report generation and source audio provenance readback.
- `src/pipeline/nle_export.py` — ED-06 CSV cut list / manifest / HTML readback generation.
- `src/cli/export_nle.py` — `export-nle` CLI.
- `src/integrations/stt/vosk_adapter.py` — optional Vosk provider preflight / WAV read / transcript segment conversion.
- `src/cli/transcribe_audio.py` — `fake` and optional `vosk` transcript generation CLI.
- `src/pipeline/transcript.py` — transcript schema builder / validator with real transcript metadata readback.
- `gui/preview_reader.cjs` — read-only preview manifest ingest and artifact link validation.
- `docs/SCHEMAS/v1/nle_export.md` — ED-06 artifact contract and boundary.
- `docs/RUNTIME_STATE.md` — current state and next recommended action.
- `docs/FEATURE_REGISTRY.md` — feature status table and transition log.
- `docs/ASSET_FETCH_BOUNDARY.md` — asset_fetch, FFmpeg, yt-dlp, GUI, STT, Editing boundaries.
- `docs/AUTOMATION_BOUNDARY.md` — automation map and forbidden surfaces.
- `docs/PREVIEW_PACK.md` — next downstream review surface boundary.
- `docs/JP_PILOT.md` — JP-Pilot-01 runbook, readback, stagnation audit, and next-entry comparison.

## Validation Already Run

Latest validation for ED-09 closeout:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results:

- `uvx pytest -q` -> `188 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors

Latest validation for JP-Pilot-01 closeout:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
ffprobe -v error -print_format json -show_format -show_streams episodes/jp_pilot01_hololive_bancho_20260525/renders/jp_pilot01_diagnostic_render/rendered_video.mp4
python -m src.cli.main audit-material-ledger --episode-id jp_pilot01_hololive_bancho_20260525 --format json
```

Results:

- `uvx pytest -q` -> `178 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors
- JP-Pilot-01 render FFprobe readback -> duration `6.600000`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `1920x1080`, fps `30/1`, stream count `2`
- JP-Pilot-01 ledger audit -> `ok=true`, issues `[]`, materials `2`

Latest validation for ED-08 / OUT-01e closeout:

```powershell
uvx pytest -q tests/test_subtitle_generation.py tests/test_real_transcript_pipeline.py
uvx pytest -q tests/test_edit_pack.py
uvx pytest -q tests/test_tiny_render.py
uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py
uvx pytest -q tests/test_nle_export.py
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
ffprobe -v error -print_format json -show_format -show_streams episodes/out01e_real_transcript_subtitle_smoke_20260516/renders/out01e_real_transcript_subtitle_render/rendered_video.mp4
```

Results:

- `uvx pytest -q tests/test_subtitle_generation.py tests/test_real_transcript_pipeline.py` -> `8 passed`
- `uvx pytest -q tests/test_edit_pack.py` -> `10 passed`
- `uvx pytest -q tests/test_tiny_render.py` -> `20 passed`
- `uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py` -> `13 passed`
- `uvx pytest -q tests/test_nle_export.py` -> `3 passed`
- `uvx pytest -q` -> `156 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors
- rendered video FFprobe readback -> duration `8.82`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24/1`, stream count `2`

Additional OUT-01e readback:

- ignored `episodes/out01e_real_transcript_subtitle_smoke_20260516` readback -> local diagnostic TTS WAV was normalized to `materials/src_audio_out01e_real_stt/source.wav`, Vosk generated `transcript.json` with `real_transcript=true`, `generate-cuts` selected `cut_001`, `generate-subtitles` wrote one `edit_pack.subtitles[]` item with `source_type="real_transcript"` and `source_segment_ids=["seg_000001"]`, then `render-tiny-proof --burn-in-subtitles diagnostic` generated `renders/out01e_real_transcript_subtitle_render/rendered_video.mp4`
- transcript readback -> provider `vosk`, model `_tmp/stt_models/vosk-model-small-en-us-0.15`, segment count `1`, source audio duration `9.8028125`, warning `real STT plumbing proof only; transcript quality is not creative acceptance`
- subtitle burn-in readback -> `subtitle_burn_in.status=enabled`, `source_ref.source_type=edit_pack_subtitles`, `source_ref.subtitle_source_type=real_transcript`, `derived_from_real_transcript=true`, `transcript_real_transcript=true`, `transcript_provider=vosk`, `source_segment_ids=["seg_000001"]`
- timing readback -> `render_start_offset_seconds=0.09`, render duration `8.82`, status counts `{"included": 1}`, item `sub_001` maps original `0.09 -> 8.91` to render `0.0 -> 8.82`
- warnings remain expected: diagnostic-only render, duration target unmet because the available real transcript/source audio range is shorter than the default target, source video/audio duration mismatch, draft edit_pack review status, pending source material rights

Additional OUT-01d readback:

- ignored `episodes/out01d_timing_font_preflight_smoke_20260514` readback -> registered local source video `src_video_out01d_timing`, normalized source audio `src_audio_out01d_timing`, generated fake transcript segments, edited `edit_pack.subtitles[]` with diagnostic timing cases, selected `cut_out01d_timing_001`, then rendered `renders/out01d_timing_font_preflight/rendered_video.mp4`
- generated render paths: `episodes/out01d_timing_font_preflight_smoke_20260514/renders/out01d_timing_font_preflight/rendered_video.mp4`, `diagnostic_subtitles.srt`, `render_receipt.json`, `render_manifest.json`, and `render_report.html`
- subtitle source readback: `source_type=edit_pack_subtitles`, `path=episodes/out01d_timing_font_preflight_smoke_20260514/edit_pack.json`, status counts `skipped_before_render_window=1`, `clamped_to_render_window=2`, `included=2`, `skipped_after_render_window=1`
- subtitle timing readback: render_start offset `1.0`; SRT contains only included/clamped items; skipped items remain in manifest/report but are not written to SRT
- filter readback: `filter_preflight.status=passed_by_successful_render`, `srt_encoding.status=written`, failure detail empty on success
- selected/attempted profile: `mp4_h264_aac`; fallback did not occur; `subtitle_burn_in.status=enabled`
- remaining warnings say the render is diagnostic, subtitle overlay is not typography/safe-area/font polish, transcript is fake/fixture-derived, edit_pack review is draft, and rights are not production-ready

Last validation for OUT-01b closeout:

```powershell
uvx pytest -q tests/test_tiny_render.py
uvx pytest -q tests/test_source_video_fetch.py
uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py
uvx pytest -q tests/test_nle_export.py
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
ffprobe -v error -print_format json -show_format -show_streams episodes/out01b_long_local_render_smoke_20260513/renders/out01b_long_local/rendered_video.mp4
```

Results:

- `uvx pytest -q tests/test_tiny_render.py` -> `11 passed`
- `uvx pytest -q tests/test_source_video_fetch.py` -> `4 passed`
- `uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py` -> `13 passed`
- `uvx pytest -q tests/test_nle_export.py` -> `3 passed`
- `uvx pytest -q` -> `147 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors
- rendered video FFprobe readback -> duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24/1`, stream count `2`

Additional OUT-01b readback:

- ignored `episodes/out01b_long_local_render_smoke_20260513` readback -> registered local source video `src_video_out01b_long_local`, normalized source audio `src_audio_out01b_long_local`, selected `cut_out01b_long_001`, then rendered `renders/out01b_long_local/rendered_video.mp4`
- generated render paths: `episodes/out01b_long_local_render_smoke_20260513/renders/out01b_long_local/rendered_video.mp4`, `render_receipt.json`, `render_manifest.json`, and `render_report.html`
- source video readback: duration `14.0`, h264/aac, `640x360`, fps `24.0`, stream count `2`
- source audio readback: duration `14.016`, `pcm_s16le`, `16000` Hz, `1` channel
- timeline readback: selected range `1.0` -> `13.0`, duration target `12.0`, clamp `false`, fallback `false`, selected/attempted profile `mp4_h264_aac`
- remaining warnings say the render is diagnostic, subtitle burn-in is disabled, transcript readback is unavailable for this fixture, edit_pack review is draft, and rights are not production-ready

Last validation for INT-02f closeout:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results:

- `uvx pytest -q` -> `136 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors

Additional targeted readback:

- `uvx pytest -q tests/test_source_video_fetch.py tests/test_asset_fetch_boundary.py tests/test_material_ledger.py tests/test_source_audio_fetch.py tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_nle_export.py` -> targeted source-video acquisition / material ledger / source-audio / transcript / ED-06 export tests pass
- ignored `episodes/int02f_source_video_smoke_20260512` readback -> local `input_source_video.mkv` was copied into `source_video.mkv`, then `fetch_receipt.json`, `sidecar.json`, and `material_ledger.json` entry were generated
- generated source-video paths: `episodes/int02f_source_video_smoke_20260512/materials/src_video_local_smoke/source_video.mkv`, `fetch_receipt.json`, `sidecar.json`, and `episodes/int02f_source_video_smoke_20260512/material_ledger.json`
- metadata readback: duration `1.2`, container `matroska,webm`, video codec `mpeg4`, audio codec `null`, resolution `160x90`, fps `15.0`, stream count `1`
- remaining warnings say local source video was copied without render/encode, source video acquisition is not production/creative/publish acceptance, audio stream is absent, and rights status is `pending`
- `uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py` -> targeted transcript / STT adapter tests pass
- `uvx pytest -q tests/test_real_transcript_pipeline.py tests/test_cut_generation.py tests/test_context_check.py tests/test_subtitle_generation.py` -> targeted edit_pack / context / subtitle path tests pass
- `uvx pytest -q tests/test_nle_export.py` -> targeted ED-06 export tests pass
- ignored `episodes/ed07b_real_stt_smoke_20260512` readback -> Windows TTS `source.wav` was transcribed by Vosk into `transcript.json`, then flowed through cut generation, context check, subtitle generation, and ED-06 CSV export
- generated paths: `episodes/ed07b_real_stt_smoke_20260512/transcript.json`, `edit_pack.json`, `exports/ed06/nle_cut_list.csv`, `nle_export_manifest.json`, and `nle_export_report.html`
- manifest/report read back transcript provider `vosk`, model `_tmp/stt_models/vosk-model-small-en-us-0.15`, `real_transcript=true`, segment count, duration, source audio material id/path/hash, and `production_edit_candidate=false`
- remaining warnings say the export is a plumbing proof, real STT quality is not creative acceptance, and `edit_pack.review.status` is still `draft`
- `uvx pytest -q tests/test_preview_pack.py tests/test_asset_fetch_boundary.py` -> targeted preview/boundary tests pass
- existing source audio mode does not call `fetch-source-audio`
- `preview_manifest.json` includes `source_wav`, `fetch_receipt`, `sidecar`, `material_ledger`, `ledger_entry`, and `source_audio_provenance`
- `preview_report.html` includes `Source Audio Provenance` and production-candidate warnings for fake / fixture transcript and generated edit_pack
- ignored `episodes/sh05d_existing_source_audio_smoke_20260512` readback -> manifest provenance refs present, report provider/tool/URL/hash/rights snapshot visible, GUI reader `state=ready`
- real INT-02e artifact smoke -> pending because the prior ignored `episodes/int02e_operator_smoke_20260512` artifact was not present in this working tree

## Resume-Time Environment Drift (2026-05-12 secondary readback)

The earlier INT-02e closeout validation used a different shell/environment from one secondary readback on the same day. The drift items below remain useful context, but ED-07b is complete and PowerShell validation for this slice passed. Read this section before touching GUI / TH-01 walkthrough / INT-02e re-smoke work.

### Electron smoke drift can appear in git-bash

- Command: `npm run smoke:electron`. Also reproduced via `node_modules/electron/dist/electron.exe . --smoke` and `node_modules/electron/dist/electron.exe gui/main.cjs --smoke`.
- Result: `TypeError: Cannot read properties of undefined (reading 'handle')` at `gui/main.cjs:30` (`ipcMain.handle("episode:status", ...)`).
- Root signal: a probe script run via `electron.exe` shows `require('electron')` returning the binary path **string** instead of the Electron API object, so the destructured `app` / `BrowserWindow` / `ipcMain` are all undefined. `app.whenReady` is never reached because `ipcMain.handle` throws first.
- Environment: invoked from git-bash on Windows. `node_modules/electron/dist/version` reports `42.0.0`; `electron.exe --version` reports its bundled `v24.15.0` (Node). `gui/main.cjs` is unchanged since the INT-02e closeout.
- Status: PowerShell validation for ED-07b reports `npm run smoke:electron -> electron smoke: OK`. The git-bash-specific launcher drift is deferred and should not be mixed into production-pipeline slices.
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

- FCPXML / Resolve XML export
- GUI fetch button
- GUI export button
- GUI render button
- GUI-triggered `build-local-preview-pack`
- cut / concat
- production subtitle burn-in / subtitle design acceptance
- production render / full render pipeline
- rendered video preview surface beyond the diagnostic OUT-01 artifact
- render profile matrix beyond the minimal OUT-01a fallback set
- creative acceptance
- rights hard gate
- STT quality acceptance / GUI transcript review surface / speaker diarization

yt-dlp remains inside `asset_fetch` source-audio/source-video URL fetch. FFmpeg is allowed in `src/integrations/render/` only for OUT-01 diagnostic rendering, including OUT-01c diagnostic subtitle overlay, OUT-01d timing/filter readback, and OUT-01e real STT subtitle source readback, and in `src/integrations/asset_fetch/` for source-audio normalization; it must not enter STT, Editing core, GUI actions, or production subtitle/render surfaces.

## Recommended Next Slice

ED-09 で transcript review / correction の CLI と readback は入った。次は「補正済み transcript を downstream に戻した時、production render に進めるだけの判断材料になるか」を確かめる段階。

| # | 候補 | 観測根拠 | unblock 条件 | 推奨度 |
|:--:|---|---|---|:--:|
| 1 | JP-Pilot-01 corrected rerun | `review-transcript` が入ったので、Vosk JP の粗い transcript を小さく補正して cuts / subtitles / NLE / diagnostic render を比較できる | ignored artifact 上の小さな review patch と既存 `--replace-auto` 再生成 | ★★★★★ |
| 2 | whisper.cpp / OpenAI Whisper 採用比較 | Vosk EN/JP とも実コンテンツでは誤認識が workflow bottleneck。ED-09 により補正コストを測れる | 依存追加または API 契約判断 | ★★★★ |
| 3 | production subtitle/render acceptance | diagnostic burn-in はあるが typography / safe-area / full render policy が未定 | corrected transcript と selected cuts の受容性確認 | ★★★ |
| 4 | GUI fetch/render/export actions | CLI 経路は通るが operator が各 CLI を手動で連結する摩擦が残る | core artifact contract 維持、確認 dialog / receipt readback | ★★★ |
| 5 | `TH-01 walkthrough closeout` | サムネレーン user-owned acceptance 未踏 | 実 YMM4 .ymmp + `config/nlmytgen_path.json`（operator-owned） | ★★ |
| 6 | Publishing (INT-01 + PB-01..04) | 縦糸の出口接続 | YouTube OAuth credentials と production acceptance | ★★ |

`chosen_format` の archive.org extractor 限界、git-bash の electron smoke ドリフト、INT-02 umbrella status の drift は small Audit 候補として保留。ED-09 後に残る最大停滞は、corrected transcript の再投入結果をまだ JP-Pilot-01 で観測していないこと。

## 自律選定方針（assistant 権限）

`docs/HOLOEN_PILOT.md` に運用方針として固定済：assistant は HoloEN public VOD 候補を自律的に調査・選定し、risk が低いと判断した 1 本を diagnostic smoke の default として使ってよい。除外条件（COVER 公式 derivative works guidelines: members-only / paid / concert / song / 第三者 IP リスク高）は compliance として維持。

JP-Pilot-01 も同方針で完了済み。assistant が JP public VOD を自律選定し、actual smoke と quality scorecard を記録した。operator review は事後。

## Next Two-Slice Pressure

After `ED-09`, the project should deliberately move toward one of these production-adjacent bottlenecks:

| Candidate | Usefulness | Why it matters | Risk |
|---|---:|---|---|
| corrected JP-Pilot rerun | 9/10 | ED-09 is only valuable if corrected transcript text improves cuts, subtitles, NLE export, and diagnostic render readback | Keep it diagnostic; do not turn transcript approval into production acceptance |
| STT provider comparison | 8/10 | Vosk EN/JP quality limits may make human correction too expensive for repeated use | External dependency/API contract may require explicit operator decision |
| production subtitle/render acceptance | 7/10 | Diagnostic burn-in works, but typography/safe-area/full render policy is absent | Premature if corrected transcript still cannot support accepted cuts |
| GUI fetch/render/export actions | 6/10 | CLI pipeline works but is still operator-unfriendly when repeated end to end | Can accidentally expose unreviewed production actions; keep confirmation/readback strict |

Recommended continuation after `ED-09`: run a small corrected JP-Pilot rerun first, then choose provider comparison if correction cost remains high or production subtitle/render acceptance if corrected cuts become usable. Do not count docs-only policy expansion, read-only GUI panels, or audit log polish as production progress unless they connect a corrected transcript, selected cuts, NLE export, or rendered video artifact.

Any OUT follow-up must remain explicitly non-production until a later acceptance slice: no publishing, no GUI one-click publish, no broad renderer feature set, and no production candidate claims.

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
