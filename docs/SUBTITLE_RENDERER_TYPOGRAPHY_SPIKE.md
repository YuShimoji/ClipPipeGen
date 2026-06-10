# Subtitle Renderer Typography Spike

This document separates subtitle mode classification from renderer-specific
typography numbers. It is a diagnostic spike only. It does not approve
production subtitle design, production render, creative use, rights, publishing,
or public use.

HTML/CSS output, when used, is a review-only prototype. CSS font size, padding,
shadow, transform, and box values must not be copied directly into YMM4,
Premiere, ASS, or FFmpeg production settings.

## Existing Context

- Current tracked presentation contract: `docs/SUBTITLE_PRESENTATION_CONTRACT.md`
- Current diagnostic contract id: `jp_clip_dialogue_reference_v0`
- Current diagnostic candidate id: `jp_clip_dialogue_badge_left_v0`
- Current generator modes already tracked:
  - `badge_left_dialogue`
  - `bottom_center_emphasis`
- Current `cut_003` boundary remains outside this spike:
  - `22.606 -> 49.566`
  - `sub_010..sub_029`
  - `sub_025..sub_029` response/referral block included
  - `sub_030` excluded

No repo-local reference screenshot was found for exact visual measurement in
this spike. Existing subtitle proof PNGs are treated as generated review
artifacts, not as external style reference screenshots.

## Subtitle Mode Taxonomy

| Mode | Primary Use | Visual Grammar | Renderer Question | Current Decision |
|---|---|---|---|---|
| `dialogue_badge_left` | Normal conversation where speaker identity is useful | Speaker badge or future face icon at left, dialogue anchored beside it | Can ASS/YMM4/Premiere keep badge and text aligned from measured text block? | Keep as a diagnostic dialogue mode; not universal |
| `bottom_center_emphasis` | Emphasis, short retorts, generic subtitle moments without a speaker badge | Large bottom-center subtitle with heavy outline | Can center anchoring and safe-area measurement survive export path differences? | Supported as an alternative mode |
| `reaction_caption` | Punchline or instant reaction such as `来ねぇ！！` | Strong central/lower caption, heavier stroke/shadow, may use tighter timing | Should this be a separate style slot instead of dialogue layout? | Treat `来ねぇ！！` as a reaction/emphasis candidate, not normal dialogue by default |
| `speaker_badge_stack` | Multiple speakers, face icon stack, or name-plate stack | Multiple identity markers with one active line or stacked lines | Can target renderer represent grouped identity assets and text without manual drift? | Deferred for production; useful as spike sample only |

`来ねぇ！！` should not automatically continue as `dialogue_badge_left`. Its
primary candidates are `reaction_caption` and `bottom_center_emphasis`, because
its editorial function is a punchline/reaction rather than ordinary speaker
continuity.

## Renderer Decision Matrix

| Candidate | Useful For | Strengths | Weaknesses | YMM4 / Premiere Connection | Bbox Measurement |
|---|---|---|---|---|---|
| ASS/libass + FFmpeg | Burned-in diagnostic proof and subtitle timing verification | Already integrated, deterministic enough for local proof, supports stroke and positioning | ASS units and libass font fallback do not map cleanly to YMM4 or Premiere controls | Indirect; values need translation and visual QA | Medium: can measure intended layout, but final glyph bbox is renderer-dependent |
| HTML/CSS + Playwright screenshot | Fast review mockups and layout exploration | Good for contact sheets, easy comparative layout, browser screenshot can capture bbox | CSS values are not production subtitle specs; browser font rendering differs from video tools | Weak; use only as review-only prototype | Medium to strong in browser, weak for production transfer |
| Pillow / Skia / Pango image drawing | Typography measurement spike and image overlay experiments | Direct pixel bbox readback; can produce isolated PNG overlays | Font shaping/fallback may differ from video editors; Pillow Japanese shaping is limited | Moderate as pre-rendered overlay asset; weak as editable subtitle | Strong for the generated bitmap, not proof of editor behavior |
| YMM4 `.ymmp` TextItem direct generation or patch | Editable YMM4 project output | Closest to YMM4 operation if schema is stable | Requires precise project schema handling and local editor verification | Strong for YMM4 once schema is pinned | Potentially strong after YMM4 render/probe, weak before render |
| Premiere MOGRT / Essential Graphics / image overlay | Premiere-centered editorial path | Can preserve editable graphics when built correctly; image overlay can be simple | MOGRT automation and Essential Graphics are toolchain-heavy; image overlay loses editability | Strong for Premiere after template path exists; image overlay is a fallback | Weak before Premiere render; good only for pre-rendered PNG bbox |

## Spike Output Contract

The spike generator writes ignored local artifacts only. Each sample readback
must include:

- output image path
- canvas size
- subtitle mode
- text
- font family and fallback status
- requested font size
- measured bbox
- safe-area margin
- outline/stroke and shadow readback
- `review_only=true`
- `production_candidate=false`
- `production_compatible=false`
- target renderer candidate
- transfer risk for YMM4/Premiere/ASS

## Grid Authority

The spike does not use a layout grid. No text, badge, safe area, wrapping, or
bbox check is snapped to grid cells. Japanese wrapping remains based on measured
font pixel bbox behavior, not grid cell count or character count alone.

The report must expose `grid_readback.grid_model="none"` and
`snap_to_grid=false` so the review surface cannot imply hidden grid authority.
The sample images should show the safe-area rectangle and measured bbox
readback as the actual review authority, not a decorative grid.

## Visible Review Element Authority

Every visible review element in the spike must declare one of these authority
classes:

- `computational_authority`: the element or its directly reported fields are
  used to calculate the sample layout.
- `measured_readback`: the element visualizes or reports measured values; it is
  evidence, not a separate design system.
- `visual_guide_only`: the element helps human orientation and must not be read
  as a layout calculation rule.
- `placeholder`: the element reserves or illustrates a future production asset
  or identity role, but is not the final asset.
- `decorative`: the element has no layout or design authority.

Current subtitle_style_spike visible elements are classified as follows:

| Element | Authority Class | Reviewer Meaning |
|---|---|---|
| drawn subtitle text block | `computational_authority` | Positioned from measured font bbox, wrapping width, safe-area margins, and mode anchor inside this review-only bitmap spike |
| safe-area rectangle | `measured_readback` | Shown in guide overlay samples only; the drawn rectangle is readback, not a separate grid or design system |
| measured text bbox readback | `measured_readback` | JSON/HTML evidence and guide-overlay bbox for the generated bitmap; not an editor-portable bbox contract |
| SPK/A/B speaker badges | `placeholder` | Placeholder speaker badges only; not real face icons, final speaker identity design, or production artwork |
| speaker badge accent color | `placeholder` | Fixed sample accent, not derived from real member assets or a production palette |
| layout grid | `visual_guide_only` and hidden by default | No grid is drawn in default samples and no sample snaps to grid |
| sample mode labels | `visual_guide_only` | HTML routing labels for review, not layout rules or production style names |
| sample background and HTML image frame | `decorative` | Page/image readability aids with no subtitle layout meaning |
| frame center / thirds lines | `visual_guide_only` | Guide-overlay orientation aids only; not snap lines |
| lower subtitle zone | `visual_guide_only` | Bottom-center review zone only; not a wrapping algorithm |
| subtitle baseline guides | `measured_readback` | Derived line-height / text-position readback; not a font-engine baseline guarantee |
| badge slot guide | `placeholder` | Placeholder badge/icon slot readback for future identity assets; not a real face icon |
| badge center / text start / badge-to-text gap guides | `measured_readback` | Current sample alignment readback, not production editor coordinates |

If a future sample displays a grid, guide, badge, color, frame, or label that is
not listed here, the JSON/HTML report must classify it before it can appear in
human review output. If an element claims computational authority, related
fields and tests must cover that authority. Placeholder speaker badges must
continue to say that real face icons are unavailable to this spike unless a
later slice adds actual identity assets.

## Layout Guide Overlay Contract

Clean samples and guide overlay samples are separate. Clean samples show the
subtitle treatment without guide lines. Guide overlay samples add explicit,
mode-aware review guides that help humans judge placement without reintroducing
grid cells or snap rules.

The guide overlay contract is `subtitle_style_spike_layout_guide_overlay_v0`.
It currently implements two profiles:

| Profile | Status | Guide Concepts |
|---|---|---|
| `bottom_center_emphasis_guide_v0` | implemented | frame center lines, thirds lines, safe-area rectangle, lower subtitle zone, one-line/two-line baseline target guides, actual baseline readback, text bbox |
| `dialogue_badge_left_guide_v0` | implemented | frame center lines, thirds lines, safe-area rectangle, subtitle baseline readback, placeholder badge slot, badge center line, text start x, badge-to-text gap, text bbox |
| `speaker_badge_stack_guide_future` | documented deferred | future multi-speaker icon/name-plate stack review |
| `status_caption_guide_future` | documented future/advanced | future explanatory/status caption placement review |

Guide overlays remain review aids. They do not make Japanese wrapping grid-,
cell-, or character-count based; wrapping remains
`font_bbox_pixel_measurement_not_grid_cell_count`. If a future guide claims
computational authority, its source fields and tests must be added in the same
slice.

## Local HTML Review Note

Open `subtitle_style_spike_report.html` directly from the local filesystem in
the same directory as the generated PNG files. The report uses local relative
image references such as `subtitle_style_spike.dialogue_badge_left.02.png`.
Browser translation/proxy pages may render the HTML text while blocking access
to those local sibling PNG files, which makes images look broken even when the
report and PNG artifacts are valid on disk.

## Measured Bbox Provenance

`measured_bbox` is a rendered-output measurement, not a design target. It is
computed after text placement with Pillow `ImageDraw.multiline_textbbox`; it is
not hardcoded per sample and should not be copied as editor coordinates without
renderer-specific validation.

Each sample report separates:

| Section | Contents | Review Meaning |
|---|---|---|
| `style_inputs` | mode, mode token constants, requested font size, outline, margin, line-height, and badge size formulas where applicable | Design inputs or formula-derived values used before drawing |
| `computed_layout` | layout anchor, wrap algorithm, wrapped lines, text start position, origin bbox, and placeholder badge slot where applicable | Placement decisions computed before final rendered measurement |
| `measured_output` | measured bbox, rendered bbox dimensions, safe-area status, and overflow readback | Output measurement from the generated bitmap |

Mode ratios such as `font_ratio`, `stroke_ratio`, `safe_x_ratio`,
`safe_y_ratio`, and `line_height_ratio` are mode-token constants. Values such
as requested font size, stroke width, safe-area margins, line height, and badge
sizes are formula-derived from those constants and the frame/font size.

## Pillow Dependency Handling

Pillow is an optional local review tool for this spike. It is not declared as a
project-wide dependency, because the normal ClipPipeGen pipeline and subtitle
overlay proof path do not require it.

If Pillow is unavailable, the tracked spike module remains importable, but PNG
generation must fail with an explicit missing-dependency message. Tests may
skip the PNG-generation case when Pillow is not installed, while still checking
that the module records the optional dependency boundary. This prevents the
spike from silently depending on one operator machine.

## Production Boundary

This spike can decide which subtitle mode deserves the next implementation
slice. It cannot decide final subtitle design, final render acceptance, creative
acceptance, rights approval, publishing acceptance, or public-use permission.

Before production work, at least one target path must be chosen:

1. ASS/libass remains the diagnostic proof path.
2. YMM4 project text generation is added as a tracked adapter.
3. Premiere template or image overlay handoff is specified.
4. Bitmap overlays are accepted as review-only or as a deliberate non-editable
   production compromise in a later acceptance slice.
