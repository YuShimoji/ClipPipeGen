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

## Layout Modes

The current overlay proof generator selects one diagnostic presentation mode,
and the typography spike may repeat the same text across multiple modes for
comparison. Repeated text across modes is intentional comparison, not a
universal style rule. A generator run must read back which mode it selected;
left alignment is not a universal rule.

- `badge_left_dialogue`: recommended current mode for normal non-POV dialogue
  where a speaker identity element is coherent. The current `cut_003`
  diagnostic proof uses this mode with a fallback speaker badge because real
  face icon assets are not available.
- `bottom_center_emphasis`: large bottom-center emphasis subtitles for moments
  where a speaker badge or left anchor is not appropriate, such as emphasized
  dialogue or a strong one-liner.
- `reaction_caption`: punchline, surprise, or instant reaction treatment such
  as `来ねぇ！！`. This is tracked in the typography spike and is not the
  default for ordinary dialogue.
- `speaker_badge_stack`: comparison-only placeholder stack for multi-speaker or
  future face-icon/nameplate work. It is not production speaker identity
  design.

## Formula-Based Layout

Diagnostic subtitle sizing and placement must be derived from the probed video
frame dimensions, not from repeated hand tuning.

For `badge_left_dialogue`:

- `font_size = round(frame_height * 0.115)`
- `outline = max(2, round(font_size * 0.096))`
- `shadow = max(1, round(font_size * 0.018))`
- `horizontal_margin = round(frame_width * 0.055)`
- `bottom_margin = round(frame_height * 0.09)`
- `badge_width = round(font_size * 1.0)`
- `badge_height = round(font_size * 0.7)`
- `badge_font_size = round(font_size * 0.44)`
- `badge_text_gap = round(font_size * 0.3)`
- `line_height = round(font_size * 1.15)`
- `dialogue_x = horizontal_margin + badge_width + badge_text_gap`
- `dialogue_y = frame_height - bottom_margin - line_height * wrapped_line_count`
- `badge_center_x = horizontal_margin + round(badge_width / 2)`
- `badge_center_y = dialogue_y + round(line_height * 0.52)`

The badge vertical alignment rule is: align the badge center to the first
subtitle line's optical center. If a subtitle wraps to multiple lines, the
subtitle block moves upward to preserve the bottom margin, while the badge
stays aligned to the first line rather than drifting independently.

For `bottom_center_emphasis`:

- `font_size = round(frame_height * 0.125)`
- `outline`, `shadow`, and margins use the same font/frame-derived ratios
  unless a later tracked contract revision changes them.
- This mode is recorded for diagnostic support, but it is not selected for the
  current `cut_003` proof.

## Japanese Wrapping Readback

The diagnostic overlay proof carries the `subtitle_style_spike` wrapping
authority into its readback as `japanese_boundary_font_bbox_pixel_wrap_v1` when
Pillow is available. The selected `wrapped_lines` are passed to ASS as explicit
line breaks so the proof does not rely on uncontrolled subtitle renderer
wrapping.

The wrapper still chooses only measured-valid candidates: punctuation,
particle, and phrase-boundary preferences are applied after each candidate line
passes font bbox pixel-width measurement. It also avoids one-character orphan
lines, and now treats short suffix-only tails such as isolated `ます` or `か`
plus punctuation as suspicious when a nearby measured-safe break is available.
Reports must read back selected `wrapped_lines`, `candidate_breaks`,
`selected_break_reason`, `orphan_prevention_applied`,
`suffix_tail_prevention_applied`, and any remaining `suspicious_tail_lines`.

This is a measurement and line-break authority only. Pillow
`ImageDraw.multiline_textbbox` is the measurement renderer, while the burned-in
proof is rendered through FFmpeg/libass. Reports must expose this
`renderer_gap` and must not describe Pillow bbox measurement as final
ASS/libass, YMM4, Premiere, or production typography readiness.

## Speaker Badge Placeholder Semantics

When placeholder speaker badges appear as `SPK`, `A`, or `B`, the report must
state near the sample that they are temporary placeholders. They are not real
face icons, not production speaker identity design, and not evidence that real
member image assets have been acquired. Real face icon asset intake remains a
separate future slice.

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
