# OUT-03 Real-Local Selected-Cut Review Proof

OUT-03 is the next observable output-layer slice after the tracked OUT-02
synthetic baseline. It packages one retained, real-local JP-Pilot cut for human
review without fetching again, changing the source episode, or claiming
production acceptance.

## Observable result

A successful run creates one ignored review package for `cut_002` at:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out03_real_local_selected_cut_proof/
```

The package has one operator entrypoint, `open_preview.ps1`. Run it normally
to open the local preview; if direct local-file opening is unavailable, use the
same script with `-Serve` to open a localhost preview. The generated
`serve_preview.ps1` is an internal helper called by that entrypoint, not a
second operator route.

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out03_real_local_selected_cut_proof\open_preview.ps1
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out03_real_local_selected_cut_proof\open_preview.ps1 -Serve
```

## Command contract

All five path/selection arguments are required. The dedicated output directory
must remain ignored and must not reuse or overwrite the retained
`human_preview_session/`.

```powershell
uvx python -m src.cli.main build-selected-cut-proof `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out03_real_local_selected_cut_proof `
  --cut-id cut_002 `
  --proof-video episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_002.mp4 `
  --proof-source-readback episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.json
```

The command validates the selected-cut/transcript/subtitle/material/proof
linkage, probes the proof media, and writes only the dedicated ignored bundle.

## Evidence and machine readback

Unlike OUT-02, the proof video comes from retained real source material. Its
episode transcript provenance must be carried into
`proof_readback.json` as `subtitle_track` /
`youtube_subtitles` with `real_transcript=true`. The readback must also record:

- `cut_id=cut_002` and the resolved source timing;
- the episode, proof-video, and proof-source-readback paths;
- the generated preview and `open_preview.ps1` paths;
- same-machine/local-retained storage and non-portability across clones;
- `diagnostic_only=true`, `rights_status=pending`,
  `production_candidate=false`, `production_ready=false`,
  `public_ready=false`, and `publish_attempted=false`.

The HTML preview and machine readback prove that the selected real-local cut is
reviewable. They do not approve the edit, subtitle design, rights, production
render, public use, upload, or publishing.

## Boundary from OUT-02

| Slice | Input | Proof value | Storage |
|---|---|---|---|
| OUT-02 | Synthetic fixture cuts and subtitles | Tracked package/readback shape | Portable tracked docs |
| OUT-03 | Retained real-local JP-Pilot `cut_002` and real transcript provenance | Same-machine selected-cut review proof | Dedicated ignored review directory |

The active retained session at
`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/`
is an input-side reference only. OUT-03 must not delete, overwrite, regenerate,
or otherwise mutate it, and nothing under `episodes/` may be tracked.
