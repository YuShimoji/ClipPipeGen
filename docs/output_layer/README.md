# Output Layer Readback

This directory holds output/video-layer readback artifacts. OUT-02 is the
tracked synthetic fixture baseline: it lets a reviewer inspect package shape
without external media. OUT-03 is the accepted single-cut real-local baseline.
OUT-04 is the accepted editorial baseline. OUT-05 is the accepted vertical
opening baseline. OUT-06 is the accepted-after-bounded-repair internal product slice: that
unchanged opening plus authoritative `cut_003` as one complete same-machine
1080x1920 internal narrative candidate, with the 2026-07-12 subtitle-wrap and
seekability findings repaired while rights, production, subtitle-design, public,
and publishing gates remain closed. OUT-07 is the parked, viable but noncanonical
cover predecessor. OUT-08 is the closed accepted-internal two-candidate baseline.
OUT-09 is the current human-review slice: one declarative vertical candidate from
a different real source/episode. A second bounded presentation repair removes
source-native caption pixels from foreground and background, uses a caption-free
canvas, and burns 27 short JSON3-timed cues while preserving range and endpoint.

Start here when resuming from another terminal:

- `OUT_09_SECOND_SOURCE_SHORT_REPEATABILITY.md` - active second-source caption-presentation repair, three-generation lineage, caption-free crop, JSON3 short-cue authority, media/mobile/browser evidence, exactly one human question, and closed gates.
- `OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md` - closed accepted-internal target-2/actual-2 baseline, exact unused-range authority, media/browser evidence, and closed gates.
- `OUT_07_INTERNAL_OPERATOR_DELIVERY_PACK.md` - parked OUT-07 closure, historical Thank semantic proxy, unchanged strict exact-baseline route, and closed external actions.
- `OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json` - tracked public URLs and structural annotations only; third-party pixels remain ignored locally.
- `OUT_06_COMPLETE_NARRATIVE_SHORT_DELIVERY_CANDIDATE.md` - accepted historical three-cut delivery-candidate contract, exact authority/timeline, build command, package, review surface, and closed gates.
- `OUT_05_VERTICAL_SHORT_INTERNAL_CANDIDATE.md` - accepted historical vertical candidate contract, exact real command, reframe/subtitle/audio readback, review surface, and closed gates.
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
ignored `review/out06_*` package. It is an accepted historical predecessor; the
active OUT-07 route starts from Planner007's separate explicit acceptance of the
current baseline bytes and does not inherit OUT-06 acceptance.

OUT-07 retains two explicit historical routes. The strict exact route keeps Planner007's
accepted 38.633333-second baseline SHA/size/duration, byte-copy, and acceptance-
inheritance gates unchanged. The separate Thank semantic direction-proxy route
uses a known source revision plus official caption/timing authority to render
one 1080x1920 source-frame-and-existing-subtitle direction, list/UI/4:5 previews,
and mapped-source evidence. It does not emit the baseline video or claim byte/
pixel equivalence, and it does not add headline, poster background, mask,
collage, or third-party pixels. `artifacts/ACTIVE_REBUILD.json` retains the
caption timing/hash contract without caption plaintext. Human review found the
single cover natural and provisionally usable for this episode, but did not
select or canonicalize it. OUT-07 is parked, its current entrypoint is removed,
and additional thumbnail iteration is prohibited until 3–5 real Shorts exist.
Upload, visibility, made-for-kids, public, publishing, production, and rights
decisions remain closed.

OUT-08 starts from updated main after that parked closure and does not refine a
cover. `build-real-unused-range-short-minibatch` validates current source,
caption, edit/cut, ledger, and rights authority; excludes the real ranges already
used by OUT-06; then atomically writes two H.264/AAC 1080x1920 review candidates,
subtitle sidecars, frame QA, navigation-only frames, scan/plan/readback/manifest,
and one direct-play page to a dedicated ignored `review/out08_*` package.
Candidate 01 uses `cut_004..cut_005`; candidate 02 uses the tail of `cut_006`,
`cut_007..cut_008`, and only the `sub_102` dependent payoff. `cut_009` remains
rejected and is not promoted. The navigation frames are not thumbnails. Human
review now decides whether each result is a coherent editing unit and whether
tempo, boundary, subtitle, or audio discomfort remains. Rights, production,
subtitle-design, public, publishing, and upload gates stay closed.

OUT-09 starts from the closed OUT-08 baseline but uses a different YouTube source
identity (`D4i4fjs9PWc`) and episode. `build-second-source-short-repeatability`
reads one declarative ignored plan, verifies six authority hashes, material
ledger provenance, a real imported caption transcript, context-passed cut
envelopes, allowed/excluded ranges, a caption/speech/scene-backed endpoint, and
an optional fail-closed composition policy before invoking the shared vertical
render path. The current ignored package has one 33.320-second H.264/AAC
1080x1920 candidate. Foreground and blurred background use only source
`0,0,640,286`, excluding the lower 74px native-caption band. The video burns 27
one-to-six-word JSON3 event/token-timed cues on an opaque plate; full-source blur
fallback and frosted caption surfaces are prohibited. The package includes
10-point frame QA, manifest/readback, and a single-video Range-capable review page. Human review is
pending; production, rights, public, publishing, thumbnail, and portability gates
remain closed. See `OUT_09_SECOND_SOURCE_SHORT_REPEATABILITY.md` for exact hashes,
commands, browser evidence, and the three-generation repair lineage.

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
