---
id: subtitle-style-intent-registry
title: Subtitle Style Intent Registry
type: design_readback
status: diagnostic_intent_registry_ready
health: semantic_style_control_ready_for_future_mapping
progress_pct: 100
last_touched: 2026-06-25
active_artifact: clip-ed10ae-render-path-selector-contract-probe-001
related: docs/SUBTITLE_PRESENTATION_CONTRACT.md, docs/style_intent/subtitle-style-intent-registry.json, docs/style_intent/subtitle-preset-selector.json, docs/style_intent/subtitle-visual-selector-proof.json, docs/style_intent/subtitle-style-family-palette-proof.json, docs/style_intent/subtitle-render-path-selector-contract.json, docs/style_intent/subtitle-render-path-selector-contract.md, artifacts/ARTIFACTS.md
---

# Subtitle Style Intent Registry

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

ED-10ae is the current successor readback for this registry route. It converts
the ED-10ad family / palette proof into a static selector-to-render-path input
contract without running render or creating video/audio/frame/ASS/episode
artifacts.

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
