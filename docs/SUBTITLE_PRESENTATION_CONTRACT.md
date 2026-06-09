# Subtitle Presentation Contract

This contract is the tracked reference surface for diagnostic JP clip subtitle
presentation. It guides the `build-subtitle-overlay-visual-proof` diagnostic
candidate only. It does not approve production subtitle design, production
render, creative use, rights, publishing, or public use.

## Contract

- contract_id: `jp_clip_dialogue_reference_v0`
- active diagnostic candidate: `jp_clip_dialogue_badge_left_v0`
- scope: dialogue subtitles in local diagnostic proof artifacts under
  `src/integrations/render/`
- current target cut: `cut_003`
- current authority boundary: keep `cut_003=22.606 -> 49.566`,
  `sub_010..sub_029` included, and `sub_030` excluded

## Dialogue Subtitle Style

The diagnostic dialogue subtitle should be visibly different from restrained
film subtitles. The target is a large, heavy-outlined Japanese clip subtitle
that can be judged for YouTube-style readability on a smartphone review path.

The preferred non-POV speaker pattern is:

1. speaker face icon
2. large left-aligned dialogue subtitle beside that identity element
3. previous line disappears when the next subtitle appears

If real speaker face icon assets are not available in the current local
`material_ledger.json`, the allowed diagnostic fallback is a small speaker
badge or placeholder box in the same position. The fallback must be reported as
a fallback, not as final speaker identity design.

## Explanatory Captions

Separate status/explanatory captions are explicitly deferred. They may need a
different placement and visual hierarchy later, but this contract does not
accept or require that path in the current slice.

## Deferred Patterns

- real member face icon asset acquisition
- multiple speaker icon stacks
- per-speaker color sourced from actual member image colors
- emotion-specific font switching
- animated subtitle motion
- production safe-area and typography polish

## Review And Non-Acceptance

Reports must use subtitle-bearing sample frames, including early, middle,
response/referral, and final active cues when those cues exist.

The report must keep these states false or pending until a separate acceptance
slice explicitly changes them:

- `production_subtitle_design_acceptance=false`
- `production_candidate=false`
- `rights_status=pending`
- `production_usage_allowed=false`
- creative acceptance is not granted
- publishing or public-use permission is not granted
