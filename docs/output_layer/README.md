# Output Layer Readback

This directory holds output/video-layer readback artifacts. OUT-02 is the
tracked synthetic fixture baseline: it lets a reviewer inspect package shape
without external media. OUT-03 is the accepted single-cut real-local baseline.
OUT-04 is the accepted editorial baseline. OUT-05 is the accepted vertical
opening baseline. OUT-06 is the accepted-after-bounded-repair internal product slice: that
unchanged opening plus authoritative `cut_003` as one complete same-machine
1080x1920 internal narrative candidate, with the 2026-07-12 subtitle-wrap and
seekability findings repaired while rights, production, subtitle-design, public,
and publishing gates remain closed.

Start here when resuming from another terminal:

- `OUT_07_INTERNAL_OPERATOR_DELIVERY_PACK.md` - current 9:16 poster-direction proof plus repaired legacy operator-pack state, frozen-reference regeneration, one review page, and closed external actions.
- `OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json` - tracked public URLs and structural annotations only; third-party pixels remain ignored locally.
- `OUT_06_COMPLETE_NARRATIVE_SHORT_DELIVERY_CANDIDATE.md` - current three-cut delivery-candidate contract, exact authority/timeline, build command, package, review surface, and closed gates.
- `OUT_05_VERTICAL_SHORT_INTERNAL_CANDIDATE.md` - current vertical candidate contract, exact real command, reframe/subtitle/audio readback, review surface, and closed gates.
- `OUT_04_EDITORIAL_REPRESENTATIVE_SEQUENCE.md` - accepted multi-cut sequence contract, exact real command, ordered timeline, review surface, and closed gates.
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

OUT-05 leaves the accepted OUT-04 bundle and every earlier protected surface
unchanged. `build-vertical-short-candidate` validates the exact predecessor
hashes and timeline, generates one ignored `review/out05_*` package through
atomic staging/promotion, and exposes a single `open_preview.ps1` entrypoint.

OUT-06 leaves OUT-05 and every earlier protected surface unchanged. It validates
the exact accepted opening, reads `cut_003` keep/needs-review/proxy authority,
reuses the data-driven vertical render boundary, and writes only a dedicated
ignored `review/out06_*` package, and now serves as the immutable video predecessor
for the OUT-07 internal operator delivery-pack slice.

OUT-07 keeps its historical fixed-hash builders unchanged and adds one explicit
Planner007 media-revision route. That route qualifies same-source identity and
timing without claiming historical byte equivalence, rebuilds the fixed
three-cut/29-subtitle baseline, and marks the differing output
`reinstantiated_baseline_candidate` with `human_acceptance=false`. The former
16:9 `context`/`tension`/`payoff` directions remain user-rejected evidence and
are not regenerated. The combined ignored page presents the baseline first,
then exactly three source-pixel 1080x1920 directions, platform previews, and
approximately 2.133s tail-to-poster clips. `artifacts/ACTIVE_REBUILD.json`
defines the exact semantic snapshot, dependency classes, existing
init/video/audio fetch commands, recovery order, and source-revision stop
gate; every host verifies its own ignored package. Human baseline readback
plus A/B/C or all-rejected selection is
required before integration. Upload, metadata acceptance, visibility,
made-for-kids, public, publishing, production, and rights decisions remain
closed.

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
