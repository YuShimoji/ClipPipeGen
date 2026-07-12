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
- artifact / episode / packaged-video / selected-thumbnail / subtitle and
  segment evidence: present in the machine draft
- upload / thumbnail upload / metadata update / visibility update attempts:
  `false`

## Review scope

Human review should stay to three dimensions:

1. 推奨tensionサムネが内容を正しく魅力的に伝え、誤認や過度な煽りがないか。
2. title・description・tagsが自然で内容と一致するか。
3. 一ページでコピー・画像・動画・根拠を確認でき、operator packとして使いやすいか。

Everything else remains closed: rights, production render, production subtitle
design, public readiness, upload, thumbnail upload, visibility, made-for-kids,
and publishing.

The episode-specific thumbnail times, visible thumbnail copy, and metadata plan
remain embedded in the OUT-07 builder. Extract them into a declarative input
before the first second-episode execution; do not expand this repair into a
general templating framework.
