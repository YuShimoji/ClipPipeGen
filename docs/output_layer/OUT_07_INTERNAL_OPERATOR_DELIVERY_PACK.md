# OUT-07 Internal Operator Delivery Pack

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
- `assets/thumbnail_recommended_1280x720.jpg`
- `assets/thumbnail_direction_contact_sheet.jpg`
- `thumbnail_plan.json`
- `publish_draft.json`
- `operator_delivery_readback.json`
- `delivery_manifest.json`
- `index.html`
- `open_delivery.ps1`
- `serve_delivery.ps1`

## Thumbnail plan

The package contains exactly three source-frame-derived 1280x720 RGB JPEG
directions:

| Direction | Source | Visible text | Role |
|---|---|---|---|
| `context` | `cut_001`, `sub_006` | `体育館裏で / 待ってます！！` | setup |
| `tension` | `cut_003`, `sub_013..sub_014` | `なんで / 来なかった！？` | recommended conflict hook |
| `payoff` | `cut_003`, `sub_022`, `sub_028` | `団長 / 倒したど～！！` | payoff spoiler |

`tension` is the single recommendation because it carries the main short-form
friction without exposing as much of the ending as `payoff`. The package uses no
AI imagery, external downloads, unverified logos, arrows/circles, or unrelated
assets.

## Metadata draft

`publish_draft.json` is Japanese-first and intentionally closed-gate:

- title: `番長、団長を呼び出すも来ない！？`
- status: `internal_operator_draft`
- language: `ja`
- operator_copy_ready: `true`
- publish_ready: `false`
- rights_status: `pending`
- visibility: `operator_decision_required`
- made_for_kids: `operator_decision_required`
- scheduled_at: `null`
- upload / thumbnail upload / metadata update / visibility update attempts:
  `false`

## Review scope

Human review should stay to three dimensions:

1. Is `tension` the right recommended thumbnail direction?
2. Is the Japanese title/description/tags copy acceptable as an internal draft?
3. Is this pack operator-complete for the next non-public delivery step?

Everything else remains closed: rights, production render, production subtitle
design, public readiness, upload, thumbnail upload, visibility, made-for-kids,
and publishing.
