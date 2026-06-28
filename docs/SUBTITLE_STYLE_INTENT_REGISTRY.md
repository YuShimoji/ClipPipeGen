---
id: subtitle-style-intent-registry
title: Subtitle Style Intent Registry
type: design_readback
status: diagnostic_intent_registry_ready
health: internal_review_video_candidate_package_ready
progress_pct: 100
last_touched: 2026-06-28
active_artifact: clip-ed10ar-internal-review-video-candidate-package-001
source_stage5_artifact: clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001
related: docs/SUBTITLE_PRESENTATION_CONTRACT.md, docs/style_intent/internal-review-video-candidate-package.json, docs/style_intent/internal-review-video-candidate-package.md, docs/style_intent/subtitle-style-intent-registry.json, docs/style_intent/subtitle-preset-selector.json, docs/style_intent/subtitle-visual-selector-proof.json, docs/style_intent/subtitle-style-family-palette-proof.json, docs/style_intent/subtitle-render-path-selector-contract.json, docs/style_intent/subtitle-render-path-selector-contract.md, docs/style_intent/subtitle-render-path-selector-probe.json, docs/style_intent/subtitle-render-path-selector-probe.md, docs/style_intent/subtitle-final-render-path-stage-3.json, docs/style_intent/subtitle-final-render-path-stage-3.md, docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.json, docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.md, artifacts/ARTIFACTS.md
---

# Subtitle Style Intent Registry

## Current ED-10ar Style Intent Registry Link

ED-10ar checkpoint, 2026-06-28 JST: `clip-ed10ar-internal-review-video-candidate-package-001` is the latest tracked package. It consumes ED-10aq as the active stage-5 source and uses Existing Output First: the same-machine ignored diagnostic MP4, ASS, and local manifest already exist, so `new_render_run=false`. It is internal-review-only, asks for no user decision now, asks for no fixed form, emits no fixed-choice or binary-choice rows, requires no screenshot, tracks no `episodes/` media, and keeps production/public/rights gates false or pending. Next route is `optional-internal-review-video-observation`; use `final-render-path-stage-4` only for a concrete diagnostic gap.

## What This Is

This registry converts future subtitle styling work from tiny numeric deltas
into semantic intent. It records the vocabulary an agent can use when proposing
emotion expression, speaker-specific badge/accent treatment, and readability
presets without asking the operator to judge every 1px outline, shadow, or
opacity adjustment.

The machine-readable readback is
[`docs/style_intent/subtitle-style-intent-registry.json`](style_intent/subtitle-style-intent-registry.json).

## Current State

ED-10aa keeps ED-10z as the current render-path-nearer probe while adding a
separate intent registry artifact:
`clip-ed10aa-subtitle-style-intent-registry-001`. Candidate 2 remains the
normal dialogue lead, Candidate 0 remains fallback, and Candidate 1 / 3 remain
held because the consumed review says they read too thin. This document does
not reopen the Candidate 0-3 comparison.

The default body text color stays stable. Speaker or character-specific color
should usually appear first in speaker badge and accent surfaces, not in the
body glyph fill. Body text color changes require a new style-family, palette,
or production-route review.

ED-10af remains the active registry route artifact through the L2 selector probe.
ED-10ag adds a L2 tiny render-path probe that consumes the restored
ED-10af dry-read as six-preset static source coverage and reuses the ED-10af
three-example L2 FFmpeg/libass selector probe as Existing Output First evidence.
The ED-10ag surface records `new_render_run=false` while keeping the route
diagnostic only.

ED-10ah adds `clip-ed10ah-production-limitation-lift-entry-001` as a tracked
gate-separation entry after the user accepted the opened surface as acceptable
enough and preferred forward progress over more layout polish. It does not
change the active artifact: ED-10af remains the active diagnostic render-path
proof and ED-10ag remains lineage/observation support. ED-10ah records that
diagnostic render-path proof is available while production subtitle design,
production render, creative acceptance, rights, publishing, and public-use
permission remain false or pending. The next executable route is
`production-limitation-lift-stage-1` or `final-render-path-readiness`, not a
production/public approval.

ED-10ah also adds
`clip-ed10ah-render-readiness-separation-readback-001` as the narrow
render-readiness readback at
[`docs/style_intent/subtitle-render-readiness-separation.json`](style_intent/subtitle-render-readiness-separation.json)
and
[`docs/style_intent/subtitle-render-readiness-separation.md`](style_intent/subtitle-render-readiness-separation.md).
It is the quick handoff answer for what ED-10ag proves, what ED-10ag does not
prove, and which later explicit milestone may trigger a new render.

ED-10ai adds `clip-ed10ai-final-render-path-readiness-packet-001` at
[`docs/style_intent/subtitle-final-render-path-readiness.json`](style_intent/subtitle-final-render-path-readiness.json)
and
[`docs/style_intent/subtitle-final-render-path-readiness.md`](style_intent/subtitle-final-render-path-readiness.md).
It consumes ED-10ah, keeps ED-10af as the active diagnostic proof source, and
records selector/semantic contract plus render adapter input contract evidence
before `final-render-path-stage-1`. Production subtitle design, production
render, creative acceptance, rights, publishing, and public-use remain missing
or pending.

ED-10aj adds `clip-ed10aj-final-render-path-stage-1-001` at
[`docs/style_intent/subtitle-final-render-path-stage-1.json`](style_intent/subtitle-final-render-path-stage-1.json)
and
[`docs/style_intent/subtitle-final-render-path-stage-1.md`](style_intent/subtitle-final-render-path-stage-1.md).
It consumes ED-10ai, selects the FFmpeg/libass diagnostic subtitle overlay path
from ED-10af as the stage-1 candidate, and preserves the semantic selector
contract, stable body text, badge/accent/backplate routing, and safe-area
metadata for preparation only. Production subtitle design, production render,
creative acceptance, rights, publishing, and public-use remain missing or
pending.

ED-10ak adds `clip-ed10ak-final-render-path-stage-2-replayability-001` at
[`docs/style_intent/subtitle-final-render-path-stage-2.json`](style_intent/subtitle-final-render-path-stage-2.json)
and
[`docs/style_intent/subtitle-final-render-path-stage-2.md`](style_intent/subtitle-final-render-path-stage-2.md).
It consumes ED-10aj and records the replayability/operation surface for the
selected FFmpeg/libass diagnostic path: tracked inputs, same-machine local
inputs, ignored outputs, expected output types, command family, readback
commands, fresh-clone absence behavior, and remaining production/public
limitations. It runs no new replay or render, keeps ED-10af active, and
prepares `final-render-path-stage-3` or
`production-limitation-lift-stage-1`.

ED-10al adds `clip-ed10al-final-render-path-stage-3-rehearsal-001` at
[`docs/style_intent/subtitle-final-render-path-stage-3.json`](style_intent/subtitle-final-render-path-stage-3.json)
and
[`docs/style_intent/subtitle-final-render-path-stage-3.md`](style_intent/subtitle-final-render-path-stage-3.md).
It consumes ED-10ak and runs one bounded ignored FFmpeg/libass diagnostic
rehearsal because local source video/audio were present and the ED-10af
same-machine ASS/MP4/manifest outputs were absent at slice start. It records
generated ASS/MP4/manifest paths, the recorded-but-not-generated contact-sheet
path, output metadata, and survival of ASS/style tokens, stable body text,
badge/accent/backplate routing, and line-break/safe-area metadata. It keeps
production/public gates closed and prepares `production-limitation-lift-stage-1`
or `final-render-path-stage-4`.

ED-10am adds `clip-ed10am-production-limitation-lift-stage-1-001` at
[`docs/style_intent/subtitle-production-limitation-lift-stage-1.json`](style_intent/subtitle-production-limitation-lift-stage-1.json)
and
[`docs/style_intent/subtitle-production-limitation-lift-stage-1.md`](style_intent/subtitle-production-limitation-lift-stage-1.md).
It consumes ED-10al as diagnostic rehearsal evidence and separates production
subtitle design, production render, creative, rights, publishing, public-use,
tracked media, and same-machine ignored evidence gates. It records next decision
owners and unsafe-overclaiming examples for each gate, runs no render, tracks no
media, and prepares `production-limitation-lift-stage-2-decision-packet` unless
`final-render-path-stage-4` is genuinely needed for more diagnostic evidence.

ED-10an adds
`clip-ed10an-production-limitation-lift-stage-2-decision-packet-001` at
[`docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.json`](style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.json)
and
[`docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md`](style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md).
It consumes ED-10am as the source gate matrix and groups the remaining
production/public decisions into subtitle design / visual acceptance,
production render readiness, and rights / publishing / public-use clearance.
It requests no immediate user decision, runs no render, tracks no media, keeps
production/public flags false or pending, and prepares
`production-limitation-lift-stage-3-owner-review-prep` unless
`final-render-path-stage-4` is needed for a concrete diagnostic gap.

ED-10ao adds
`clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001` at
[`docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.json`](style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.json)
and
[`docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md`](style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md).
It consumes ED-10an and prepares future owner-review topics for subtitle
design / visual acceptance, production render readiness, and rights /
publishing / public-use clearance. It requests no immediate user decision,
emits no fixed form, runs no render, tracks no media, keeps production/public
flags false or pending, and prepares
`production-limitation-lift-stage-4-user-decision-card` unless
`final-render-path-stage-4` is needed for a concrete diagnostic gap.

ED-10ap adds
`clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001` at
[`docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.json`](style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.json)
and
[`docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.md`](style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.md).
It consumes ED-10ao and prepares a future short freeform user decision card for
subtitle design / visual acceptance, production render readiness, and rights /
publishing / public-use clearance. It requests no immediate user decision,
emits no fixed user form or fixed-choice rows, requires no screenshot path,
exposes no hidden schema as user input, runs no render, tracks no media, keeps
production/public flags false or pending, and prepares
`production-limitation-lift-stage-5-user-decision-ready` unless
`final-render-path-stage-4` is needed for a concrete diagnostic gap.

## Intent Axes

| Axis | Values / shape | Why it matters |
|---|---|---|
| `speaker_id` | stable string when known | lets character color/accent proposals attach to identity without changing body text color by default |
| `speaker_role` | `character`, `narrator`, `system`, `unknown` | separates dialogue, narration, and system notes before visual styling |
| `emotion` | `neutral`, `emphasis`, `shout`, `whisper`, `ominous`, `narration`, `system_note` | gives future agents semantic routes instead of raw px questions |
| `intensity` | `0` to `3` | scales a preset from baseline to rare high-impact cues |
| `utterance_role` | `dialogue`, `narration`, `sfx`, `quote`, `warning`, `inner_voice` | distinguishes speech from captions, warnings, and internal voice |
| `readability_priority` | `normal`, `high`, `maximum` | decides whether backplate, shorter lines, or stricter safe-area behavior should win |

## Token Mapping

| Semantic input | Token surfaces |
|---|---|
| normal dialogue | current Keifont route, frame-derived base size, Candidate 2 badge-pressure lead, Candidate 0 fallback |
| emotion / intensity | font size scale, outline/shadow strength token, accent color, optional backplate, motion primitive placeholder |
| speaker identity | speaker badge color first, accent color second, body text color stable unless a new palette/style route is opened |
| dense or high-risk readability | line-break policy, safe-area behavior, backplate/box, and line count before tiny outline deltas |
| narration / system note | optional or system badge, lower visual aggression, higher readability priority |

## Perceptual Weight

High-impact changes are position, size, line count, backplate/box, badge
presence, and visible accent blocks. Medium-impact changes are accent color,
outline color, and motion primitives. Low-impact changes are 1px outline,
1px shadow, and tiny opacity adjustments. Future prompts should treat low-impact
numeric tweaks as implementation details once the semantic preset is known.

## Agent Rule

When future subtitle work supplies semantic tags such as
`speaker_id=bancho`, `emotion=shout`, `intensity=2`,
`utterance_role=dialogue`, and `readability_priority=high`, the agent may map
those tags to an existing preset without asking for raw numeric parameters.
Human review is needed only for a new style family, a new color palette, body
text color policy changes, production-route changes, rights, publishing, or
public-use decisions.

## Preset Selector Readback

ED-10ab adds a deterministic selector artifact:
`clip-ed10ab-subtitle-preset-selector-001`. The selector readback lives at
[`docs/style_intent/subtitle-preset-selector.json`](style_intent/subtitle-preset-selector.json),
and the reusable implementation is
`src/integrations/render/subtitle_preset_selector.py`.

The selector consumes the six registry axes and returns token names for:

- `font_family_role`
- `font_size_scale`
- `outline_shadow_strength`
- `badge_color_token`
- `accent_color_token`
- `backplate_box_token`
- `motion_primitive`
- `safe_area_line_break_behavior`
- `body_text_color_token`

The selector keeps `body_text_color_token=stable_default_body_text` for all
current examples. Character-specific color first changes `badge_color_token`
and `accent_color_token`; it does not change body glyph fill. The examples
cover neutral dialogue intensity 0, shout intensity 2, whisper intensity 1,
ominous intensity 2, narration, and system note. This is readback only and
does not create a new visual proof.

ED-10ac adds the current visual selector proof artifact:
`clip-ed10ac-visual-selector-proof-001`. The tracked proof lives at
[`docs/style_intent/subtitle-visual-selector-proof.json`](style_intent/subtitle-visual-selector-proof.json)
and
[`docs/style_intent/subtitle-visual-selector-proof.html`](style_intent/subtitle-visual-selector-proof.html).
It makes those six selector examples inspectable as static badge/accent/
backplate/size/motion/line-break differences while preserving stable body text
color. It does not run a new render or approve production/public use.

ED-10ad adds the style-family / palette axis proof artifact:
`clip-ed10ad-style-family-palette-axis-proof-001`. The tracked proof lives at
[`docs/style_intent/subtitle-style-family-palette-proof.json`](style_intent/subtitle-style-family-palette-proof.json)
and
[`docs/style_intent/subtitle-style-family-palette-proof.html`](style_intent/subtitle-style-family-palette-proof.html).
It groups the same six examples by family and palette route while preserving
`stable_default_body_text`. The routes are readback vocabulary only; they do
not approve a new style family or new palette.

ED-10ae adds the current render-path selector contract artifact:
`clip-ed10ae-render-path-selector-contract-probe-001`. The tracked contract
lives at
[`docs/style_intent/subtitle-render-path-selector-contract.json`](style_intent/subtitle-render-path-selector-contract.json)
and
[`docs/style_intent/subtitle-render-path-selector-contract.md`](style_intent/subtitle-render-path-selector-contract.md).
It lists the semantic, style-family, palette, color-surface, motion, and
line-break fields a later render adapter would receive. This is L0 static
readback only; the later L2 tiny render-path probe remains a separate
milestone, and production/public-use boundaries stay closed or pending.

ED-10af adds the current L2 render-path selector probe artifact:
`clip-ed10af-l2-render-path-selector-probe-001`. The tracked probe readback lives at
[`docs/style_intent/subtitle-render-path-selector-probe.json`](style_intent/subtitle-render-path-selector-probe.json)
and
[`docs/style_intent/subtitle-render-path-selector-probe.md`](style_intent/subtitle-render-path-selector-probe.md).
It consumes the ED-10ae contract and selects three semantic examples: neutral
dialogue, shout / high intensity, and low-pressure whisper.

The probe preserves `stable_default_body_text`, keeps semantic variation on
badge/accent/backplate surfaces, carries family/palette route plus motion and
line-break metadata, and records local ignored ASS/MP4/manifest evidence. It is
L2 diagnostic readback only; production/public-use boundaries remain closed or
pending.

ED-10ag adds the lineage and observation surface:
`clip-ed10ag-lineage-and-observation-surface-001`. The tracked surface lives at
[`docs/style_intent/subtitle-render-path-lineage-observation-surface.json`](style_intent/subtitle-render-path-lineage-observation-surface.json)
and
[`docs/style_intent/subtitle-render-path-lineage-observation-surface.md`](style_intent/subtitle-render-path-lineage-observation-surface.md).
It consumes the restored dry-read files, keeps the ED-10af L2 probe as active
render-path evidence, lists ASS / MP4 / manifest / contact-sheet paths, and records
`new_render_run=false` for ED-10ag. It does not request user review or change
any production, rights, publishing, or public-use boundary.

## Review Surface Layout Debt

The latest review also says the primary Candidate Visual Evidence samples were
still too small/compressed. The dropdown full-frame context helped, but it
should not be the only readable full-frame surface. ED-10aa records this as
layout debt and applies a small generator-side improvement: avoid a cramped
four-column primary grid, keep Candidate 2 lead and Candidate 0 fallback larger
and prominent by default, retain crop evidence, and make Candidate 1 / 3
secondary held references.

This is not another review request. It is a development note for future review
surfaces so the operator is not forced into repeated manual comparison loops.

## Next

Use this registry before opening another subtitle style slice. A future agent
can add a small preset selector or renderer readback that consumes these axes,
but ED-10aa intentionally does not build a broad renderer style system.

## Constraints / Risks

This artifact is diagnostic planning/readback only. It does not approve
production subtitle design, production render, creative use, rights, publishing,
or public use. It does not read or edit any other repository, and it does not
vendor font binaries or source media.
