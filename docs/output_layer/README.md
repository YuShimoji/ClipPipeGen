# Output Layer Readback

This directory holds output/video-layer readback artifacts. OUT-02 is the
tracked synthetic fixture baseline: it lets a reviewer inspect package shape
without external media. OUT-03 is the accepted single-cut real-local baseline.
OUT-04 is the current product slice: two retained JP-Pilot cuts composed into
one same-machine editorial sequence while rights, production, public, and
publishing gates remain closed.

Start here when resuming from another terminal:

- `OUT_04_EDITORIAL_REPRESENTATIVE_SEQUENCE.md` - current multi-cut sequence contract, exact real command, ordered timeline, review surface, and closed gates.
- `OUT_03_REAL_LOCAL_SELECTED_CUT_PROOF.md` - accepted single-cut predecessor, exact CLI contract, evidence entrypoint, machine readback, and closed gates.
- `OUT_02_HANDOFF.md` - synthetic baseline branch, artifact, validation, gate, and next-route context.
- `OUT_01_HANDOFF.md` - branch, artifact, validation, gate, and next-route context.

Regenerate the current OUT-02 artifacts from the repository root:

```powershell
python -m src.cli.main build-output-layer-gap-report --format json
```

OUT-03 does not replace these tracked files. Its
`build-selected-cut-proof` command writes only to a dedicated ignored episode
review directory and exposes one `open_preview.ps1` entrypoint with a `-Serve`
fallback. The existing `jp_pilot01r3_cut_review/human_preview_session/` remains
untouched; see `OUT_03_REAL_LOCAL_SELECTED_CUT_PROOF.md` for the exact command
and evidence contract.

OUT-04 likewise leaves OUT-03 and the protected `human_preview_session/`
unchanged. `build-editorial-sequence` reads current keep/context/segment/
subtitle/material evidence, extracts source-level ranges through the render
integration, hard-cuts them in explicit order, and writes only a dedicated
ignored `review/out04_*` package.

Generated files:

- `video_output_gap_log.json` - machine-readable capability matrix, gap log, proof status, fixture proof summary, and recommended next slice.
- `output_capability_matrix.md` - reviewer-facing table of output-layer capabilities and blockers.
- `local_output_readback.html` - static top-level readback for quick local inspection.
- `local_fixture_output_proof/proof_manifest.json` - parseable proof boundary and artifact map.
- `local_fixture_output_proof/proof_readback.json` - parseable human/tool readback.
- `local_fixture_output_proof/proof_timeline.html` - static title-card, subtitle-band, selected-segment, and gate readback.
- `local_fixture_output_proof/fixture_edit_pack.json` - synthetic selected-cut fixture shaped like an edit-pack handoff.
- `local_fixture_output_proof/fixture_subtitles.srt` - synthetic subtitle draft for the fixture timeline.
- `local_fixture_output_proof/README.md` - package-level human readback.
