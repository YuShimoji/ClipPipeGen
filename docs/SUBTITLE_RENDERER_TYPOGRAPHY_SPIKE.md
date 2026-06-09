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
