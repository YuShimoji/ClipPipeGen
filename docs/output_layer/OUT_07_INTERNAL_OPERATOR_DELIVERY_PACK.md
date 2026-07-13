# OUT-07 Native Shorts Cover Review Routes

## Current Thank semantic direction proxy route

The current tracked state is
`OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY`. It keeps the
same artifact ID, branch, slice, and lane, while adding evidence revision
`thank-6f78657e-native-cover-direction-proxy-v1`. This route uses the known
Thank source revision
`6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`;
it does not claim byte equivalence to the Planner source revision.

The route validates the official caption SHA and hash-only `sub_010` timing /
segment / cut contract, maps source `22.858s` to sequence `11.930s`, and decodes
the nearest 30fps frame at `22.866667s`. It reuses the established source-
derived 9:16 reframe, Keifont, and subtitle presentation to render one
1080x1920 direction proxy. It adds no poster-specific abstract background,
headline, mask, collage, or third-party pixel. Planner-known hashes differ, so
the honest classification is `cover_direction_semantic_proxy`; local scene and
authority are directly observed, while continuity to Planner is an inference
and Planner pixel equivalence remains unknown. The proxy SHA is
`e7aaae24401b5b6c75e13926329af19c8a59008dd3c93229735d7465da2f18da`.

Build the ignored package through its separate two-build route:

```powershell
python -m src.cli.main build-out07-direction-proxy `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --verify-determinism `
  --format json
```

The local-only package is:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/
```

It contains the single proxy, list preview, Shorts UI overlap preview, center
4:5 crop, mapped source frame, machine readback, deterministic core/receipt,
manifest, scripts, and one simple `index.html`. The page does not include the
exact baseline video or former candidate directions. Thank can open it at
`http://127.0.0.1:8071/index.html`; `portable_entrypoint=null`.

The only question is:

> このThank source revisionによる同一時刻・同一字幕のShorts一覧cover方向を採用してよいか。違和感があれば自由記述してください。

The exact baseline remains unavailable on Thank while its Planner acceptance
remains a historical accepted fact. Proxy ACCEPT cannot flow into baseline
bytes, A/V, full-track subtitles, metadata, rights, production, public, or
publishing acceptance.

## Strict exact accepted-baseline route (unchanged)

The active artifact remains
`clip-out07-shorts-poster-frame-direction-proof-v0-001` on branch
`codex/out-07-internal-operator-delivery-pack-v0`. Planner007 explicitly
accepted the current baseline on 2026-07-13 JST. The accepted bytes are fixed
at:

- source YouTube ID: `7J5aS_pcBj4`
- qualified source SHA-256: `e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`
- accepted baseline SHA-256: `2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`
- accepted baseline size: `21,669,538` bytes
- accepted baseline duration: about `38.633333s`

The package and media below are last-verified Planner007 strict-route evidence.
They are not available on Thank. This route still requires restoration of the
exact accepted baseline before it can run; the semantic proxy route above does
not weaken or satisfy this precondition.

The acceptance covers content/narrative, timing/tempo, cut continuity, A/V
continuity, subtitle timing/readability, and visual integrity. It does not
inherit historical OUT-06 acceptance and does not grant rights, production,
public/publishing, upload/visibility, or made-for-kids approval.

`src/integrations/render/out07_native_cover.py` verifies the retained baseline,
copies it byte-for-byte, and extracts one decoded frame. It never rerenders,
remuxes, transcodes, edits, or retimes the MP4, subtitles, or audio.

## Strict exact cover direction

The selected internal recommendation is the accepted baseline at `11.930s`,
mapped to current source time `22.858s` in `cut_003`, with existing burn-in cue
`sub_010`. The cover adds no separate catchcopy, long-form headline, small
label, logo, CTA, abstract background, geometry, gradient, background
replacement, mask, sticker cutout, collage, invented person, or third-party
pixel.

The canonical frame fingerprints are:

| Evidence surface | Timestamp | Profile | SHA-256 |
|---|---:|---|---|
| accepted baseline | 11.930s | `raw_rgb24_320x180_bilinear` | `d2187bfb68f14b2eebfea2249061c7130a5bc5a6e25fbb0d5592782c9cb33062` |
| mapped current source | 22.858s | `raw_rgb24_320x180_bilinear` | `c44c9258b165dda344dab75a68e9f8ee0a0b0c265f2264492275da0de74b64d3` |

At most three timestamps are compared internally; only this recommended frame
is exported. The active prior A/B/C are retained by hash as
`superseded_by_user_short_context_reframe`. That state records a Shorts-context
reframe, not a quality rejection, and those candidates must not be returned for
selection. Historical context/tension/payoff remains separately
`user_rejected`.

## Strict exact build and package

Run the fixed-input two-build route:

```powershell
python -m src.cli.main reconstitute-out07-review `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --reference-corpus docs/output_layer/OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json `
  --verify-determinism `
  --format json
```

The active ignored output is the single review directory:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/
```

Its review-facing files are:

| File | Purpose |
|---|---|
| `reinstantiated_baseline.mp4` | byte-identical copy of the accepted baseline |
| `native_shorts_cover_1080x1920.png` | only recommended cover output |
| `cover_list_preview.jpg` | 405x720 list-scale preview only |
| `cover_shorts_ui_overlay_preview.jpg` | generic Shorts-UI overlap survival preview only |
| `cover_center_4x5.jpg` | center 4:5 crop heuristic only |
| `mapped_source_frame_1920x1080.png` | unmodified mapped-source frame for timestamp/fingerprint comparison |
| `baseline_acceptance.json` / `baseline_readback.json` | explicit acceptance and unchanged-byte proof |
| `publish_draft.json` / `operator_delivery_readback.json` | unchanged metadata, recommended cover, and closed gates |
| `superseded_poster_evidence.json` | non-returnable old A/B/C and historical rejected-direction hashes/status |
| `poster_direction_readback.json` | active one-question review contract |
| `determinism_receipt.json` / `combined_review_manifest.json` | two-build digest and file/self-integrity proof |
| `index.html` | list preview, 9:16, center 4:5, source comparison, metadata, baseline SHA, then folded provenance/gates/history |

The last-verified Planner007 host used this byte-range localhost route; its
server was stopped for the durable handoff, so this is not a portable current
entrypoint:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_shorts_poster_frame_direction_proof\open_preview.ps1 -Serve -Port 8071
```

The page asks exactly:

> Shorts一覧用coverとして、映像由来フレーム＋既存字幕だけのこの方向を採用してよいか。違和感があれば自由記述してください。

It does not re-question the baseline, metadata, rights, production, or public
state.

## Caption authority and cross-machine recovery

`artifacts/ACTIVE_REBUILD.json` no longer stores the bulk 29-line caption
plaintext snapshot. It retains IDs, cut and source/sequence timing, segment
IDs, per-text SHA-256, caption payload digest, wrap break indices, source
locator, recovery class/command, and mismatch rules. Actual text is loaded from
the ignored official JSON3 authority or reacquired from the source. If it is
absent, semantic rebuild stops with
`caption_authority_reacquire_required`; cross-machine resume is therefore
`conditional_reacquire`.

Earlier commits may still contain the former tracked plaintext snapshot. No
history scrub is claimed.

A different host must restore the exact 21,669,538-byte accepted baseline
artifact and verify `2c1c59...2d18` before the strict exact package command can
run. That route cannot recreate it by rendering. The Thank semantic proxy does
not require or emit the baseline video. A real conditional retained-artifact
recovery proof is H2 successor work, not a claim made by the current H0 package.

## Strict exact determinism and gates

Two fixed-input builds must match both core and package digests. The active
receipt records core `35d91185...e05f6` and package `a849d66d...43303`, followed
by per-file manifest and manifest self-integrity validation. The tracked
reference corpus is observation-only in this route; no new crawl or third-party
reference pixel is loaded into the cover.

The metadata draft remains unchanged. `selected_thumbnail=null`, the cover is
`recommended_pending_human_acceptance`, `selected_by_human=false`, and
`publish_ready=false`. Rights are pending, every production/public/external
action gate is closed, and upload, thumbnail upload, visibility,
made-for-kids, publish, and other external mutations are all unattempted.

## Historical predecessor

`clip-out07-internal-operator-delivery-pack-v0-001` and its fixed-hash builder
remain historical evidence. They are not the active readback ID and do not
replace the current single proxy review directory. They may be consulted for
lineage only; current human review begins with the Thank semantic direction
proxy above.
