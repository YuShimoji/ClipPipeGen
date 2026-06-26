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
- current baseline target cut: `cut_003`
- current dense/stress target cut: `cut_008`
- current authority boundary: keep `cut_003=22.606 -> 49.566`,
  `sub_010..sub_029` included, and `sub_030` excluded; keep `cut_008`
  as the consumed dense/stress diagnostic pass route

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
  as `譚･縺ｭ縺・ｼ・ｼ～. This is tracked in the typography spike and is not the
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
lines, and now treats short suffix-only tails such as isolated `縺ｾ縺兪 or `縺義
plus punctuation as suspicious when a nearby measured-safe break is available.
Reports must read back selected `wrapped_lines`, `candidate_breaks`,
`selected_break_reason`, `orphan_prevention_applied`,
`suffix_tail_prevention_applied`, and any remaining `suspicious_tail_lines`.

This is a measurement and line-break authority only. Pillow
`ImageDraw.multiline_textbbox` is the measurement renderer, while the burned-in
proof is rendered through FFmpeg/libass. Reports must expose this
`renderer_gap` and must not describe Pillow bbox measurement as final
ASS/libass, YMM4, Premiere, or production typography readiness.

ED-10v records the current line-break behavior as accepted diagnostic readback
for the Keifont dense/stress proof. The reviewed evidence is `cut_008` /
`sub_096`, where the font-bbox wrapper selected two lines:
`荳狗阜繝句他繝灘・繧ｷ繧ｿ繝弱ワ繧ｭ繧ｵ` / `繝槭き縲Ａ. The user reviewed the corrected
multiline/dense-stress proof and said the subtitle display is good and all pass.
This closes the current visual review loop for diagnostic dense/stress behavior,
but it does not freeze the algorithm as final production subtitle design.

Future tuning should stay policy/readback-driven rather than ad hoc to a single
frame. The bounded areas are line length, maximum line count, orphan control,
short suffix-tail control, safe-area pressure, and rapid cue replacement. Any
future change should preserve the selected `wrapped_lines`, break reason, and
renderer-gap readback so the visual proof can explain why a line broke.

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

## Current Cut_003 Diagnostic Acceptance

Human review accepted only the current `cut_003` diagnostic burned-in proof
readability baseline. Record this as
`diagnostic_subtitle_wrapping_readability_acceptance=true` for `cut_003`.

The accepted scope is limited to current cut_003 diagnostic burned-in proof
readability. It covers the current diagnostic proof's
wrapping/readability/safe-area/timing impression only, and it does not approve
production subtitle design, production render, creative quality, rights,
publishing, or public use.

## Current Cut_008 Dense/Stress Diagnostic Pass

ED-10v consumes the latest review of
`clip-ed10r-keifont-dense-stress-proof-001`. The accepted diagnostic scope is:

- `cut_008` dense/stress readability
- `sub_096` multiline/wrap evidence
- current Keifont provisional subtitle route under the shown rapid cue and
  safe-area pressure

Keifont remains a diagnostic/provisional subtitle baseline. This is not a
production subtitle design acceptance, not production render acceptance, not
creative acceptance, not rights clearance, not publishing acceptance, and not
public-use permission.

The current axis is passed, so no further Review Card should be emitted for the
same `cut_008` evidence unless a new axis or changed evidence is introduced.
New review needs must be genuinely new, such as bounded decoration adjustment,
production limitation-lift, or a render-path probe.

## Current ED-10w Presentation Review Pack

ED-10w is the current new-axis review surface after the ED-10v pass. It uses
`clip-ed10r-keifont-dense-stress-proof-001` as source evidence and emits
`clip-ed10w-subtitle-presentation-review-pack-001` for one freeform judgement.
It does not reopen the general Keifont review on `cut_002` / `cut_003`, and it
does not ask for another pass/fail judgement on the same `cut_008` multiline
evidence.

The bounded presentation candidates are:

- `ed10w_current_pass_reference`
- `ed10w_lighter_outline_shadow_pressure`
- `ed10w_badge_label_pressure_adjustment`
- `ed10w_balanced_combined_low_risk`

ED-10x records a reviewability correction for these candidates. Full-frame
candidate images alone are not sufficient when the bounded deltas are difficult
to perceive. The review pack must surface compact subtitle-body crops, compact
SPK badge crops, and actual style delta readback for Candidate 0-3. Candidate
0 remains the current baseline reference; Candidate 1 must visibly change
outline/shadow readback; Candidate 2 must visibly change badge pressure
readback; Candidate 3 must combine both axes. These remain bounded diagnostic
contrasts, not a broad style gallery and not production subtitle design.

The render-path readiness card in the pack is a diagnostic planning probe only.
It may justify a later tiny render-path slice, but it does not approve
ASS/libass, YMM4, Premiere, production render, publishing, or public use.

## Current ED-10y Candidate 2 Carry-Forward

ED-10y consumes the latest freeform review of the ED-10w/ED-10x pack. The
review says Candidate 0 and Candidate 2 are acceptable/good, while Candidate 1
and Candidate 3 look too thin compared with 0 and 2. It also records that the
full-frame context was still somewhat small, so the current pack layout keeps
compact crops as the first evidence but allows larger full-frame detail views.

Current bounded-decoration state:

- lead candidate: `ed10w_badge_label_pressure_adjustment`
- fallback/reference: `ed10w_current_pass_reference`
- held references: `ed10w_lighter_outline_shadow_pressure`,
  `ed10w_balanced_combined_low_risk`
- same Candidate 0-3 comparison review allowed: `false`
- user review required now: `false`

Candidate 2 is only a provisional bounded-decoration lead for the diagnostic
Keifont route. It carries forward the current subtitle body treatment and
reduces placeholder SPK badge/label pressure. It does not approve production
subtitle design, production render, creative use, rights, publishing, or public
use.

The ED-10y pack may include a tiny FFmpeg/libass diagnostic render-path-nearer
probe for Candidate 2. That probe is readback only; it does not lift production
render or public-use gates.

## Current ED-10z Tiny Render-Path-Nearer Probe

ED-10z preserves `clip-ed10y-candidate2-carry-forward-001` as the
source/previous artifact and records `clip-ed10z-tiny-render-path-nearer-probe-001`
as the current local diagnostic readback. The profile
`ed10z_tiny_render_path_nearer_probe` keeps Candidate 2
(`ed10w_badge_label_pressure_adjustment`) as the lead treatment and passes it
through the current FFmpeg/libass diagnostic path. Candidate 0 remains
fallback/reference, and Candidate 1 / Candidate 3 remain held references
because the consumed review says they read too thin.

The ED-10z pack must not reopen the same Candidate 0-3 comparison and must not
emit a new Review Card. When the ignored local proof files are materialized
with FFmpeg/FFprobe available, its `render_path_readiness.status` is
`ed10z_tiny_render_path_nearer_probe_completed`, which means the tiny local
probe completed as diagnostic evidence only. A production limitation-lift,
final render-path, rights, publishing, or public-use decision needs a separate
future route.

## Current ED-10ab Preset Selector

ED-10ab records `clip-ed10ab-subtitle-preset-selector-001` as a tracked
selector/readback artifact. It consumes the ED-10aa semantic axes
(`speaker_id`, `speaker_role`, `emotion`, `intensity`, `utterance_role`,
`readability_priority`) and returns token candidates for font family role, font
size scale, outline/shadow strength, badge color, accent color, backplate/box,
motion placeholder, safe-area/line-break behavior, and stable body text color.

The selector is deterministic and does not ask for raw numeric outline, shadow,
or opacity review. Character-specific color must appear first in badge/accent
tokens, not body glyph fill. Human review is required only for new style
families, new palettes, body text color policy changes, production-route
changes, rights, publishing, or public-use decisions.

ED-10ab is selector/readback only. It does not run a new render, does not
create a new visual proof, does not reopen the Candidate 0-3 comparison, and
does not approve production subtitle design, production render, creative use,
rights, publishing, or public use.

## Current ED-10ac Visual Selector Proof

ED-10ac records `clip-ed10ac-visual-selector-proof-001` as a tracked static
JSON/HTML proof. It consumes the ED-10ab examples and shows how neutral,
shout, whisper, ominous, narration, and system note presets differ by badge
token, accent token, backplate/box token, font size scale, outline/shadow
token, motion placeholder, and safe-area/line-break behavior.

The proof keeps body subtitle text color stable across every example with
`stable_default_body_text`. Character and emotion color remains badge/accent
first, not body glyph fill. ED-10ac uses L1 Existing Output First and does not
run a new render because the selector differences can be inspected in tracked
static readback.

ED-10ac does not reopen the Candidate 0-3 comparison, does not emit a required
Review Card, and does not approve production subtitle design, production
render, creative use, rights, publishing, or public use. If opened by the
operator, the only expected input is optional freeform observation, maximum 3
points.

## Current ED-10ad Style Family / Palette Axis Proof

ED-10ad records `clip-ed10ad-style-family-palette-axis-proof-001` as a
tracked static JSON/HTML proof. It consumes the ED-10ac visual selector proof
and groups the six semantic presets by style family and palette route before
any later render-path probe.

The current family groups are dialogue current Keifont, emphasis energy, quiet
soft readability, ominous inner voice, narration, and system note. The current
palette routes are speaker identity blue, high energy warm, quiet cool,
ominous dark, narration neutral green, and system neutral. These routes are
readback vocabulary only; ED-10ad does not create or approve a new style
family or new palette.

Body subtitle text color remains `stable_default_body_text` across every
example. Palette expression stays on badge, accent, and backplate surfaces.
ED-10ad uses L0 No Render / Existing Output First, does not ask the operator
for visual review, and does not approve production subtitle design,
production render, creative use, rights, publishing, or public use.

## Current ED-10ae Render Path Selector Contract Probe

ED-10ae records `clip-ed10ae-render-path-selector-contract-probe-001` as a
tracked static JSON/Markdown contract. It consumes the ED-10ad style-family /
palette axis proof and states the selector fields a later render adapter would
receive before any tiny render-path probe is opened.

The contract readback covers semantic preset id, preset key, speaker/emotion/
readability axes, family id, palette route, font family role, font size scale,
outline/shadow strength, badge color, accent color, backplate/box, stable body
text color policy, motion primitive, and safe-area / line-break behavior for
the same six semantic examples. Body subtitle text color remains
`stable_default_body_text`; speaker or emotion color remains badge/accent and
backplate first.

ED-10ae is L0 No Render. It does not create a video, audio, frame, ASS, or
episode artifact, and it does not imply FFmpeg/libass, YMM4, Premiere, or final
production-render readiness. The later L2 tiny render-path probe trigger is a
separate milestone. ED-10ae does not approve production subtitle design,
production render, creative use, rights, publishing, or public use.

## Current ED-10af L2 Render Path Selector Probe

ED-10af records `clip-ed10af-l2-render-path-selector-probe-001` as a tracked JSON/Markdown L2 diagnostic probe. It
consumes the ED-10ae render-path selector contract and selects normal dialogue,
shout / high intensity, and low-pressure whisper examples for a tiny
FFmpeg/libass readback path.

The probe carries semantic preset id, preset key, family id, palette route, font
role, size / outline metadata, badge/accent/backplate fields, stable body text
color, motion metadata, and safe-area / line-break metadata. Body subtitle text
color remains `stable_default_body_text`; speaker or emotion color remains
badge/accent and backplate first.

ED-10af generated same-machine ignored ASS, MP4, and local manifest evidence at
`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass`, `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4`, and `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json`. These are diagnostic proof
outputs only and remain outside Git. ED-10af does not approve production
subtitle design, production render, creative use, rights, publishing, or public
use.

## Current ED-10ag Lineage and Observation Surface

ED-10ag records `clip-ed10ag-lineage-and-observation-surface-001` as a tracked
lineage and same-machine observation surface. The active artifact remains
`clip-ed10af-l2-render-path-selector-probe-001`; the restored
`clip-ed10af-render-contract-consumer-dry-read-001` remains predecessor evidence
rather than a deleted or invalidated route.

The dry-read remains useful because it proves all six ED-10ae contract payloads
can be normalized without media output. The ED-10af L2 selector probe supplies
bounded FFmpeg/libass render-path evidence for three representative examples:
neutral, shout, and whisper. ED-10ag applies Existing Output First, so it records
lineage and observation access without running ffmpeg again.

The ED-10ag surface lists the reused local ignored ASS, MP4, manifest, and
contact-sheet paths. Those files may be absent on another clone and are diagnostic
same-machine evidence only. ED-10ag records
`new_render_run=false`, does not request user review, does not create tracked
binary media, and does not approve production subtitle design, production
render, creative use, rights, publishing, or public-use decisions.

## Current ED-10ah Production Limitation-Lift Entry

ED-10ah additionally records
`clip-ed10ah-render-readiness-separation-readback-001` as a bounded readback at
`docs/style_intent/subtitle-render-readiness-separation.json` and
`docs/style_intent/subtitle-render-readiness-separation.md`. This is the
separation surface for render readiness: ED-10ag proves that ED-10af dry-read
coverage can connect to the existing L2 diagnostic ASS/MP4/manifest/contact
sheet evidence, but it does not prove production subtitle design, production
render, creative acceptance, rights, publishing, public-use, or final style
acceptance. New render remains false for this checkpoint; the next render
trigger must be a later explicit milestone.

ED-10ah records `clip-ed10ah-production-limitation-lift-entry-001` as a tracked
gate-separation entry after the user confirmed the opened surface is acceptable
enough and forward progress should take priority over more display/layout
polish. It keeps `clip-ed10af-l2-render-path-selector-probe-001` as the active
diagnostic render-path proof and keeps
`clip-ed10ag-lineage-and-observation-surface-001` as lineage/observation
support, not production proof.

The ED-10ah entry separates seven gates: diagnostic render-path proof,
production subtitle design acceptance, production render acceptance, creative
acceptance, rights status, publishing acceptance, and public-use permission.
Diagnostic render-path proof is available. Production subtitle design,
production render, creative, rights, publishing, and public-use gates remain
false or pending. The next executable route is
`production-limitation-lift-stage-1` or `final-render-path-readiness`; neither
route is approval to publish or use the proof publicly.

## Current ED-10ai Final Render-Path Readiness Packet

ED-10ai records `clip-ed10ai-final-render-path-readiness-packet-001` as a
tracked readiness matrix at
`docs/style_intent/subtitle-final-render-path-readiness.json` and
`docs/style_intent/subtitle-final-render-path-readiness.md`. It consumes the
ED-10ah gate entry, preserves ED-10af as the active diagnostic proof source,
keeps ED-10ag as lineage/predecessor support, and links the selector/semantic
style contract plus ED-10ae render adapter input contract.

The ED-10ai packet says diagnostic proof, selector/semantic contract evidence,
render adapter input contract evidence, local ignored proof media paths, and
lineage/predecessor evidence are available. Production subtitle design,
production render, creative acceptance, rights, publishing, and public-use
decisions are still missing or pending. ED-10ai runs no render and does not
approve production/public use; it only prepares `final-render-path-stage-1` or
`production-limitation-lift-stage-1`.

## Current ED-10aj Final Render-Path Stage 1

ED-10aj records `clip-ed10aj-final-render-path-stage-1-001` as a tracked
stage-1 packet at `docs/style_intent/subtitle-final-render-path-stage-1.json`
and `docs/style_intent/subtitle-final-render-path-stage-1.md`. It consumes
ED-10ai as the readiness source and selects the FFmpeg/libass diagnostic
subtitle overlay path from ED-10af as the stage-1 final render-path candidate.

The ED-10aj checklist says ASS generation, semantic selector contract, stable
body text policy, badge/accent/backplate routing, line-break/safe-area
metadata, local ignored proof media, and no tracked binary media are ready for
stage-1 preparation. Production subtitle design, production render, creative
acceptance, rights, publishing, and public-use decisions remain missing or
pending. ED-10aj runs no render and does not approve production/public use; it
only prepares `final-render-path-stage-2` or
`production-limitation-lift-stage-1`.

## Future Shared Line-Break Policy Note

The subtitle line-break and layout policy should remain structured enough that a
future slice can evaluate sharing it with NLMYTGen. ED-10v, ED-10w, ED-10y, and ED-10z
do not read, edit, or depend on NLMYTGen files, and they do not extract a shared
package. Any later reuse should happen through an explicit boundary, contract,
or subprocess/API route rather than by mixing repository internals.

The production/public boundary remains:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## Review And Non-Acceptance

Reports must use subtitle-bearing sample frames, including early, middle,
response/referral, and final active cues when those cues exist.

The report must keep these states false or pending until a separate acceptance
slice explicitly changes them:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `production_candidate=false`
- `rights_status=pending`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## Limitation-Lift Conditions

Production subtitle design acceptance requires representative subtitle design
review across relevant cuts/scenes, including font, size, outline, color,
speaker identity, mode selection, and safe area.

Production render acceptance requires final render-path output review, not only
diagnostic proof.

Creative acceptance requires whole-video or representative-sequence editorial
review.

Rights approval requires explicit rights/material-use clearance.

Publishing/public-use permission requires both production acceptance and rights
approval.
