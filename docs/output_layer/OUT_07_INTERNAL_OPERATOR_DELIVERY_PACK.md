# OUT-07 Operator Pack and Media-Revision Combined Review

## Active Planner007 route

The active artifact is still
`clip-out07-shorts-poster-frame-direction-proof-v0-001`, but Planner007 uses the
explicit media-revision route in
`src/integrations/render/out07_reconstitution.py`. It qualifies the current
episode source, validates edit/transcript/decision/proxy/caption authority,
rebuilds the fixed 38.6-second baseline, and reconstructs the publish draft
without regenerating the
rejected 16:9 thumbnails, freezes public reference evidence, and generates a
baseline-first A/B/C review page. Missing historical OUT-03 through OUT-06
packages are not required.

```powershell
uvx --with Pillow python -m src.cli.main reconstitute-out07-review `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --reference-corpus docs/output_layer/OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json `
  --verify-determinism `
  --format json
```

Add `--fetch-missing-references` only for the first cache freeze. The portable
dependency/recovery order, exact semantic snapshot, and fresh-clone
init/video/audio/rebuild commands are machine-readable in
`artifacts/ACTIVE_REBUILD.json`. The generated baseline differs from historical
accepted OUT-06 bytes, so it is a `reinstantiated_baseline_candidate` with
`human_acceptance=false`; editorial timing and six wrap repairs carry, but byte
acceptance does not. The combined page at port 8071 asks exactly two freeform
questions: baseline anomaly readback, then A/B/C or all-rejected direction.

The fixed-hash operator pack documented below remains an unchanged historical
route. It is comparison evidence, not the current Planner007 input contract.

## Historical fixed-hash internal operator pack

OUT-07 creates one internal operator delivery pack from the accepted OUT-06
video. It does not rerender, remux, transcode, upload, publish, approve rights,
choose visibility, choose made-for-kids state, or set a public thumbnail.

The artifact ID is `clip-out07-internal-operator-delivery-pack-v0-001`. The
ignored same-machine package is:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack/
```

Use:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_internal_operator_delivery_pack\open_delivery.ps1 -Serve
```

The default localhost port is `8070`.

## Build command

```powershell
uvx --with Pillow python -m src.cli.main build-operator-delivery-pack `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack `
  --out06-readback episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/candidate_readback.json `
  --format json
```

The builder validates the accepted OUT-06 readback, accepted OUT-06 MP4 hash,
and source video hash. It copies the MP4 bytes into
`assets/complete_narrative_short.mp4`; the source and package SHA-256 are both
`02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0`.

## Package contents

- `assets/complete_narrative_short.mp4`
- `assets/thumbnail_context_1280x720.jpg`
- `assets/thumbnail_tension_1280x720.jpg`
- `assets/thumbnail_payoff_1280x720.jpg`
- `assets/thumbnail_direction_contact_sheet.jpg`
- `thumbnail_plan.json`
- `publish_draft.json`
- `operator_delivery_readback.json`
- `delivery_manifest.json`
- `index.html`
- `open_delivery.ps1`
- `serve_delivery.ps1`

## Rejected 16:9 thumbnail evidence

The package contains exactly three source-frame-derived 1280x720 RGB JPEG
directions:

| Direction | Source | Visible text | Role |
|---|---|---|---|
| `context` | `cut_001`, `sub_006` | `体育館裏で / 待ってます！！` | user rejected |
| `tension` | `cut_003`, `sub_013..sub_014` | `なんで / 来なかった！？` | user rejected |
| `payoff` | `cut_003`, `sub_022`, `sub_028` | `団長 / 倒したど～！！` | user rejected |

All three 16:9 directions are retained only as rejected evidence. The old
`thumbnail_recommended_1280x720.jpg` copy was removed,
`recommended_direction_id=null`, and `selected_thumbnail=null`. They must not
be repaired, recolored, relabeled, or returned as candidates.

## Metadata draft

`publish_draft.json` is Japanese-first. Its audience-facing copy contains only
content metadata; attribution, rights, production, public, publishing, and
attempt state remain separate operator-only fields:

- title: `番長、団長を呼び出すも来ない！？`
- description:
  - `番長のはじめが団長を体育館裏へ呼び出し、「倒してやる！！」と意気込みます。`
  - `ところが団長は来ず、待ち続けたはじめが「なんで来なかったんすか！！」と問いかけます。`
  - `最後は“はじめの勝ち”で決着し、次の番長を探し始めます。`
- tags: `ホロライブ`, `はじめ`, `番長`, `団長`, `体育館裏`, `呼び出し`, `来なかった理由`
- status: `internal_operator_draft`
- language: `ja`
- operator_copy_ready: `true`
- publish_ready: `false`
- rights_status: `pending`
- visibility: `operator_decision_required`
- made_for_kids: `operator_decision_required`
- scheduled_at: `null`
- source_attribution_status: `operator_decision_required`
- source_title / source_url: `null`
- artifact / episode / packaged-video / rejected-thumbnail / subtitle and
  segment evidence: present in the machine draft
- upload / thumbnail upload / metadata update / visibility update attempts:
  `false`

## Reference-derived Shorts poster direction proof

The current review artifact is
`clip-out07-shorts-poster-frame-direction-proof-v0-001`. It writes only to the
ignored same-machine package:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/
```

Regenerate from the frozen local reference cache with:

```powershell
uvx --with Pillow python -m src.cli.main build-shorts-poster-frame-proof `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof `
  --source-video episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4 `
  --accepted-video episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack/assets/complete_narrative_short.mp4 `
  --out07-publish-draft episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack/publish_draft.json `
  --reference-corpus docs/output_layer/OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json `
  --reference-cache-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_reference_cache `
  --format json
```

`--fetch-missing-references` is an explicit first-freeze action only. Normal
regeneration is network-free and refuses a missing frozen image. The tracked
corpus stores URLs and structural annotations only; third-party pixels stay in
the ignored cache and `reference_board.jpg`.

The package contains:

- `poster_A/B/C_1080x1920.jpg`
- `poster_direction_contact_sheet.jpg`
- `expression_contact_sheet_A/B/C.jpg`
- `subject_mask_inspection.jpg`
- `platform_preview_contact_sheet.jpg`
- `reference_board.jpg`
- `reference_manifest.json`
- `poster_direction_readback.json`
- `transition_A/B/C.mp4`
- `index.html`, `open_preview.ps1`, and `serve_preview.ps1`

A/B/C use three research-derived directions backed by primary and supporting
references. Candidates use retained source pixels, manual alpha masks without
generated or modified person pixels, project-local geometric treatment, and the
local Noto Sans JP Black weight. The package includes channel/search,
center-4:5 heuristic, and approximate Shorts playback UI previews; the 4:5
preview is not an official YouTube crop guarantee.

Each transition is review-only: accepted-video tail 1.75s, a shared 0.12s
dissolve, a 0.50s poster end-cap, and a 0.16s audio fade.
The complete accepted video remains byte-identical at
`02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0`.

## Current review scope

Human review has one freeform question:

> A/B/Cのどれが実用候補に最も近いか、または全案不採用か。末尾posterの出現が不自然な場合だけ併記してください。

Human selection is required before H1 can integrate any poster into the full
Short. Title, description, tags, rights, production render, production subtitle
design, public readiness, upload, thumbnail upload, visibility, made-for-kids,
and publishing remain pending or closed.

The episode-specific thumbnail times, visible thumbnail copy, and metadata plan
remain embedded in the OUT-07 builder. Extract them into a declarative input
before the first second-episode execution; do not expand this repair into a
general templating framework.
