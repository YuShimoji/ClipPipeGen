---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: grill_me_adoption_review_frame_plan_ready
progress_pct: 100
last_touched: 2026-06-29
next_review_due: none_review_frame_plan_only
active_artifact: clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001
source_micro_scene_observation_frame_readback: clip-ed10av-micro-scene-observation-frame-readback-001
source_representative_micro_scene_specimen: clip-ed10au-representative-micro-scene-internal-review-specimen-001
source_internal_review_observation_readback: clip-ed10at-internal-review-observation-readback-001
source_internal_review_access_sheet: clip-ed10as-internal-review-access-sheet-fullpath-001
source_internal_review_package: clip-ed10ar-internal-review-video-candidate-package-001
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, docs/dashboard/project-status.json, docs/SUBTITLE_STYLE_INTENT_REGISTRY.md, docs/SUBTITLE_PRESENTATION_CONTRACT.md, docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.json, docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md, docs/style_intent/micro-scene-observation-frame-readback.json, docs/style_intent/micro-scene-observation-frame-readback.md, docs/style_intent/representative-micro-scene-internal-review-specimen.json, docs/style_intent/representative-micro-scene-internal-review-specimen.md, docs/style_intent/internal-review-video-observation-readback.json, docs/style_intent/internal-review-video-observation-readback.md, docs/style_intent/internal-review-video-candidate-access-sheet.json, docs/style_intent/internal-review-video-candidate-access-sheet.md, docs/style_intent/internal-review-video-candidate-package.json, docs/style_intent/internal-review-video-candidate-package.md, scripts/operator/open_representative_micro_scene_internal_review_specimen.ps1, scripts/operator/open_internal_review_video_candidate.ps1, artifacts/ARTIFACTS.md
---

# Current Handoff - ClipPipeGen

## Current ED-10aw Grill-me Adoption Readback and Review-Frame Clarification Plan

ED-10aw checkpoint, 2026-06-29 JST:
`clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001`
is the active tracked handoff artifact. It consumes ED-10av, classifies the
local untracked Grill-me files as a bounded helper only, and records that
`.agents/skills/grill-me/SKILL.md` plus `skills-lock.json` are not staged
project resources.

Use Grill-me only as a short adversarial gate around plan, diff, report, or
freeform-observation readback. Its output may contain a verdict plus at most
three blockers, warnings, and required fixes. It must not emit a next-Agent
prompt, add nested prompt text to an AGENT_REPORT, override project docs, turn
access guesses into evidence, or imply production/public/rights/publishing
approval.

The next practical route is `review-frame-clarification`: explain what the
ED-10au/ED-10av specimen is asking the reviewer to judge before any rerender.
Use `subtitle-layout-screenshot-capture` only when classifying the lower
subtitle/player-UI risk, `representative-micro-scene-v2` only for confirmed
source/scene mismatch, and `final-render-path-stage-4` only for a concrete
render-path gap. ED-10aw creates no render, media, screenshot, `episodes/`
tracking, stage-7 normalizer, user review request, or approval.

## Current ED-10av Micro-Scene Observation Frame Readback

ED-10av checkpoint, 2026-06-29 JST:
`clip-ed10av-micro-scene-observation-frame-readback-001` is the source tracked
observation-frame readback for ED-10aw. It consumes the user's freeform observation after opening the
ED-10au specimen: the target looked different, evaluation was unclear, it
looked like a real scene rather than the earlier diagnostic cue/memo, and the
subtitle area appeared large/low or possibly overlapped by media-player UI.

ED-10av records openability and actual micro-scene content as pass, expectation
mismatch and visual/source framing as warnings, review-purpose clarity as
partial/fail, and subtitle lower-area/player-UI overlap as
`needs_classification_not_verified`. It creates no render, replay, media, or
screenshot, tracks no `episodes/` file, uses no stage-7 normalizer, asks for no
additional user review now, and grants no production/public/rights/publishing/
monetization or micro-scene approval. The next practical axis is
`review-frame-clarification`; use `subtitle-layout-screenshot-capture` only to
verify the lower subtitle/player-UI risk, `representative-micro-scene-v2` only
for confirmed source/scene mismatch, and `final-render-path-stage-4` only for a
concrete render-path gap.

## Source ED-10au Representative Micro-Scene Internal Review Specimen

ED-10au checkpoint, 2026-06-29 JST:
`clip-ed10au-representative-micro-scene-internal-review-specimen-001` is the
source specimen readback. It consumes ED-10at's observation that the previous
internal review MP4 opened but read as a chopped cue-label memo, then creates a
9.18 second bounded specimen with actual transcript subtitles `sub_004` to
`sub_006`: `団長、ちなみに、他の番長知ってますか？ 長？ 長って言った？`,
`倒して回ってるんです！`, and
`長…長… 船長のことかな？ マリンならあっちにいたよ`.

The ignored local MP4 is verified present with ffprobe metadata and size
`3538973` bytes at
`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.mp4`.
The launcher is
`scripts/operator/open_representative_micro_scene_internal_review_specimen.ps1`.
No user review is requested now. A later review, if explicitly requested, stays
freeform with at most three look-for points and should classify the next fix as
script, timing/audio, visual layout, or render path. The specimen tracks no
media, keeps `episodes/` untracked, does not use stage-7, and grants no
production/public/rights/publishing/monetization approval.

## Current ED-10at Internal Review Observation Readback

ED-10at checkpoint, 2026-06-29 JST:
`clip-ed10at-internal-review-observation-readback-001` is a source tracked
readback. It consumes the user's freeform observation after opening the
ED-10as / ED-10ar internal review MP4: the MP4 opened, duration was short as
expected, and the visible subtitles were exactly `NORMAL DIALOGUE CUE`,
`SHOUT HIGH INTENSITY`, and `LOW PRESSURE WHISPER CUE`.

The warning side is preserved too: the scenes looked chopped or abrupt, the
artifact looked memo-like, it differed considerably from prior artifacts, and
the user did not know how to evaluate it. This is diagnostic cue-probe
readback, not representative episode/video review and not production/public
approval. It creates no render, replay, media, tracked `episodes/` file, or
stage-7 normalizer. The earlier ED-10ak/ED-10af-only anchor was stale checkout
drift; current authority source is ED-10as access sheet plus ED-10ar package.

## Current ED-10as Internal Review Access Sheet Fullpath / Access Recovery

ED-10as checkpoint, 2026-06-28 JST: `clip-ed10as-internal-review-access-sheet-fullpath-001` is a source tracked access sheet. It consumes ED-10ar and records exact current-host full paths for the ignored MP4, ASS, and local manifest, plus `scripts/operator/open_internal_review_video_candidate.ps1`. It creates no render, replay, or media, tracks no `episodes/` files, asks for no user decision now, and keeps production/public/rights/publishing/monetization gates false or pending. Later observation, if requested, stays freeform with at most three look-for points.

2026-06-29 JST access recovery: the older ED-10ar stage-6 freeform request
paths are absent on current `main` and should be treated as stale external
prompt/resource references. They were added in `62a1581` and removed in
`32b1d33` when ED-10ar became
`clip-ed10ar-internal-review-video-candidate-package-001`. Current `main` and
`origin/main` matched at `cffc5b33ea0f993d9fddef65a6facf8bdbdf3ec5` during the
readback. Classification is `stale_path`; it is not a branch/worktree mismatch
and not missing ignored local media. Do not ask the user to search for those
old files again. Update stale 監修側/project-resource references to the current
ED-10as/ED-10ar artifacts, or restore the old stage-6 files only under an
explicit future repair instruction. The exact retired paths are recorded in
[HANDOFF.md](HANDOFF.md), while this current handoff keeps only the active
ED-10as/ED-10ar names. Do not create a stage-7 normalizer from this handoff.

## What This Is

This page is a short transfer surface for a different terminal or agent. The
authoritative resume surface remains [RUNTIME_STATE.md](RUNTIME_STATE.md).
Use this page to avoid replaying stale font-family, Candidate 0-3 comparison,
layout-polish, stale stage-6 freeform-request paths, or stale static prompts
after the project has advanced to the
ED-10ai final render-path readiness packet.
ED-10aj final render-path stage-1 packet.
ED-10ak final render-path stage-2 replayability packet.
ED-10al final render-path stage-3 diagnostic rehearsal packet.
ED-10am production limitation-lift stage-1 preparation packet.
ED-10an production limitation-lift stage-2 decision packet.
ED-10ao production limitation-lift stage-3 owner-review prep packet.
ED-10ap production limitation lift stage-4 user decision-card readback.
ED-10aq production limitation lift stage-5 user-decision-ready readback.
ED-10ar internal review video candidate package.
ED-10as internal review access sheet with current-host full paths.
ED-10at internal review observation readback.
ED-10au representative micro-scene internal review specimen.
ED-10av micro-scene observation frame readback.

## Current State

The active artifact is
`clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001`.

The source micro-scene observation frame readback is
`clip-ed10av-micro-scene-observation-frame-readback-001`.

The source representative micro-scene specimen is
`clip-ed10au-representative-micro-scene-internal-review-specimen-001`.

The source observation readback is
`clip-ed10at-internal-review-observation-readback-001`.

The source access sheet is
`clip-ed10as-internal-review-access-sheet-fullpath-001`.

The source internal review package is
`clip-ed10ar-internal-review-video-candidate-package-001`.

ED-10aw records
`clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001`
at
`docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.json`
and
`docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md`.
It classifies Grill-me as a bounded local helper with capped verdict output,
forbids next-Agent prompts and nested AGENT_REPORT prompts, keeps the untracked
skill files unstaged, and prepares `review-frame-clarification` as the first
default route. It creates no render/media/screenshot, asks for no new user
review, and infers no production/public/rights approval.

ED-10av records
`clip-ed10av-micro-scene-observation-frame-readback-001`
at
`docs/style_intent/micro-scene-observation-frame-readback.json`
and
`docs/style_intent/micro-scene-observation-frame-readback.md`.
It classifies the opened ED-10au specimen observation as pass for openability
and actual micro-scene content, warning for expectation mismatch and
visual/source framing, partial/fail for review-purpose clarity, and
needs-classification for lower subtitle/player-UI overlap. It creates no
render/media/screenshot, asks for no further user review now, and infers no
approval.

ED-10au source records
`clip-ed10au-representative-micro-scene-internal-review-specimen-001`
at
`docs/style_intent/representative-micro-scene-internal-review-specimen.json`
and
`docs/style_intent/representative-micro-scene-internal-review-specimen.md`.
It records a verified local specimen MP4, ASS, manifest, launcher, real
Japanese transcript content, and closed or pending approval gates. It asks for
no user work now.

ED-10at records
`clip-ed10at-internal-review-observation-readback-001`
at
`docs/style_intent/internal-review-video-observation-readback.json`
and
`docs/style_intent/internal-review-video-observation-readback.md`.
It classifies the observation as openability/duration/cue visibility pass for
diagnostic purposes, chopped/memo-like continuity warning, and partial/fail
review guidance clarity. It does not infer production subtitle design,
production render, creative, rights, publishing, monetization, or public-use
approval.

ED-10as records
`clip-ed10as-internal-review-access-sheet-fullpath-001`
at
`docs/style_intent/internal-review-video-candidate-access-sheet.json`
and
`docs/style_intent/internal-review-video-candidate-access-sheet.md`.
It gives exact current-host full paths for the MP4, ASS, and manifest under
ignored `episodes/` local evidence and adds
`scripts/operator/open_internal_review_video_candidate.ps1`. It creates no
new render/replay/media, tracks no `episodes/` files, and does not approve
production, rights/public-use, publishing, or monetization.

ED-10ar records
`clip-ed10ar-internal-review-video-candidate-package-001`
at
`docs/style_intent/internal-review-video-candidate-package.json`
and
`docs/style_intent/internal-review-video-candidate-package.md`.
It consumes ED-10aq as the stage-5 user-decision-ready source and records the
existing ignored diagnostic video candidate package: MP4, ASS, and local
manifest are present on this machine, with duration 4.2 seconds, H.264/AAC,
1920x1080, 30fps, and two streams. It runs no new render, emits no fixed form,
no fixed-choice rows, no binary-choice rows, no required labels, no screenshot
request, and no hidden schema as user input. It tracks no media, keeps
`episodes/` untracked, and does not approve production subtitle design,
production render, creative, rights, publishing, public use, or monetization.
The next executable route is `optional-internal-review-video-observation`, with
`final-render-path-stage-4` reserved only for a concrete diagnostic gap.

ED-10aq records
`clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001` at
`docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.json`
and
`docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.md`.
It consumes ED-10ap as the stage-4 user decision-card source and makes the
later short freeform user review request ready without asking for that decision
now. It records answer_style=freeform, max_look_for_points<=3, no fixed form,
no fixed-choice rows, no screenshot requirement, no hidden schema exposure, no
render/replay/media, no tracked media, and closed production/rights/public-use
approval gates. ED-10ar now consumes it as the source for the internal review
video candidate package, with `final-render-path-stage-4` reserved only for a
concrete diagnostic gap.

ED-10ap records
`clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001` at
`docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.json`
and
`docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.md`.
It consumes ED-10ao as the owner-review prep source and converts the three
owner-review entries into a future short freeform user decision card for
subtitle design / visual acceptance, production render readiness, and rights /
publishing / public-use clearance.

The ED-10ap packet records each topic's plain-language future question shape,
available and missing evidence, safe freeform answer hints, internal
normalization hints, stop boundary, and unsafe-overclaiming examples. It
requests no immediate user decision, emits no fixed user form or fixed-choice
rows, requires no screenshot path, exposes no hidden schema as user input, runs
no render, tracks no media, keeps `episodes/` untracked, and does not approve
production subtitle design, production render, creative, rights, publishing, or
public use. The next executable route is
`production-limitation-lift-stage-5-user-decision-ready`, with
`final-render-path-stage-4` reserved only for a concrete diagnostic gap.

ED-10ao records
`clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001` at
`docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.json`
and
`docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md`.
It consumes ED-10an as the source decision packet and converts the three
bounded decision groups into owner-review preparation entries for subtitle
design / visual acceptance, production render readiness, and rights /
publishing / public-use clearance.

The ED-10ao packet requests no immediate user decision, emits no fixed form,
runs no render, tracks no media, keeps `episodes/` untracked, and does not
approve production subtitle design, production render, creative, rights,
publishing, or public use. The next executable route is
`production-limitation-lift-stage-4-user-decision-card`, with
`final-render-path-stage-4` reserved only for a concrete diagnostic gap.

ED-10an records
`clip-ed10an-production-limitation-lift-stage-2-decision-packet-001` at
`docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.json`
and
`docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md`.
It consumes ED-10am as the source gate matrix and groups the remaining decisions
into three bounded decision-preparation groups: subtitle design / visual
acceptance, production render readiness, and rights / publishing / public-use
clearance.

The ED-10an packet requests no immediate user decision, runs no render, tracks
no media, keeps `episodes/` untracked, and does not approve production subtitle
design, production render, creative, rights, publishing, or public use. It
preserves ED-10al diagnostic metadata (`4.2s`, `1920x1080`, `h264`, `aac`, two
streams) and the survival readback as diagnostic evidence only. The next
executable route is `production-limitation-lift-stage-3-owner-review-prep`,
with `final-render-path-stage-4` reserved only for a concrete diagnostic gap.

ED-10am records `clip-ed10am-production-limitation-lift-stage-1-001` at
`docs/style_intent/subtitle-production-limitation-lift-stage-1.json` and
`docs/style_intent/subtitle-production-limitation-lift-stage-1.md`. It consumes
ED-10al as primary diagnostic rehearsal evidence and separates nine gates:
diagnostic rehearsal evidence, production subtitle design acceptance,
production render acceptance, creative acceptance, rights status, publishing
acceptance, public-use permission, tracked media boundary, and same-machine
ignored evidence boundary.

The ED-10am packet records current status, source evidence, missing evidence,
next decision owner, whether the agent can progress without user judgement, and
unsafe-overclaiming examples for each gate. It runs no render, tracks no media,
keeps `episodes/` untracked, and does not approve production subtitle design,
production render, creative, rights, publishing, or public use. The next
executable route is `production-limitation-lift-stage-2-decision-packet`, with
`final-render-path-stage-4` reserved for genuinely needed extra diagnostic
evidence.

ED-10al records `clip-ed10al-final-render-path-stage-3-rehearsal-001` at
`docs/style_intent/subtitle-final-render-path-stage-3.json` and
`docs/style_intent/subtitle-final-render-path-stage-3.md`. It consumes ED-10ak
as the stage-2 source and runs one bounded FFmpeg/libass diagnostic rehearsal
because local source video/audio were present while the ED-10af same-machine
ASS/MP4/manifest outputs were absent before the slice. It generated ignored
ASS, MP4, and manifest outputs under the existing ED-10af selector-probe
directory; the ED-10ag contact-sheet path remains recorded but was not generated
by this stage-3 helper.

The rehearsal readback records the exact invocation family, exact FFmpeg command
summary, output metadata (`4.2s`, `1920x1080`, `h264`, `aac`, two streams), and
survival checks for ASS/style tokens, stable body text, badge/accent/backplate
routing, and line-break/safe-area metadata. Production subtitle design,
production render, creative acceptance, rights, publishing, and public-use gates
remain false or pending. The next executable route is
`production-limitation-lift-stage-1` or `final-render-path-stage-4`; neither
route approves production/public use.

ED-10ak records `clip-ed10ak-final-render-path-stage-2-replayability-001` at
`docs/style_intent/subtitle-final-render-path-stage-2.json` and
`docs/style_intent/subtitle-final-render-path-stage-2.md`. It consumes ED-10aj
as the stage-1 source and records how the selected FFmpeg/libass diagnostic
subtitle overlay path can be inspected or replayed by a later agent/operator.
It uses Existing Output First: ED-10ak runs no replay/render, tracks no proof
media, and treats same-machine local media absence on a fresh clone as non-fatal
for tracked docs.

The ED-10ak operation matrix keeps the selected path, tracked inputs,
same-machine local inputs, ignored output paths, expected output types, command
family, validation/readback commands, fresh-clone absence behavior,
diagnostic-only scope, and missing production render approvals explicit. The
next executable route is `final-render-path-stage-3` or
`production-limitation-lift-stage-1`; neither route approves production/public
use.

ED-10aj records `clip-ed10aj-final-render-path-stage-1-001` at
`docs/style_intent/subtitle-final-render-path-stage-1.json` and
`docs/style_intent/subtitle-final-render-path-stage-1.md`. It consumes ED-10ai
as the readiness source and selects the FFmpeg/libass diagnostic subtitle
overlay path from ED-10af as the stage-1 final render-path candidate. This is
path selection and preparation only: no new render is run, no proof media is
tracked, and no production/public approval is inferred.

The ED-10aj checklist keeps ASS generation, semantic selector contract, stable
body text, badge/accent/backplate routing, line-break/safe-area metadata, local
ignored proof media, and no tracked binary media explicit. Production subtitle
design, production render, creative acceptance, rights, publishing, and
public-use decisions remain false or pending. The next executable route is
`final-render-path-stage-2` or `production-limitation-lift-stage-1`.

ED-10ai records `clip-ed10ai-final-render-path-readiness-packet-001` at
`docs/style_intent/subtitle-final-render-path-readiness.json` and
`docs/style_intent/subtitle-final-render-path-readiness.md`. It consumes the
ED-10ah gate entry and answers what is ready before a later final render-path
stage: ED-10af diagnostic proof, selector/semantic style contract, ED-10ae
render adapter input contract, local ignored proof media paths, and ED-10ag
lineage/predecessor evidence are available. Production subtitle design,
production render, creative acceptance, rights, publishing, and public-use
decisions remain missing or pending.

ED-10ai runs no render, tracks no proof media, and requests no display/layout
review. The next executable route is `final-render-path-stage-1` or
`production-limitation-lift-stage-1`; both remain preparation routes and do not
approve production/public use.

ED-10ah now also records
`clip-ed10ah-render-readiness-separation-readback-001` at
`docs/style_intent/subtitle-render-readiness-separation.json` and
`docs/style_intent/subtitle-render-readiness-separation.md`. Use this first
when the next terminal needs the narrow answer to "what did ED-10ag prove, what
did it not prove, and when is the next render allowed?" It confirms ED-10ag
reused existing ED-10af L2 diagnostic output, ran no new render, created no
tracked proof media, and did not approve production subtitle design,
production render, creative use, rights, publishing, public use, or final
subtitle style.

ED-10ah records `clip-ed10ah-production-limitation-lift-entry-001` at
`docs/style_intent/subtitle-production-limitation-lift-entry.json` and
`docs/style_intent/subtitle-production-limitation-lift-entry.md`. It consumes
the user observation that the opened review/observation surface is acceptable
enough and forward progress is preferred over more display/layout polish.

ED-10ah keeps ED-10af as the active diagnostic render-path proof, keeps ED-10ag
as lineage and same-machine observation support, and preserves the restored
ED-10af dry-read from commit `7e96a28` as predecessor evidence. It separates the
next route into seven gates: diagnostic render-path proof, production subtitle
design acceptance, production render acceptance, creative acceptance, rights
status, publishing acceptance, and public-use permission. Diagnostic proof is
available; production/public gates remain false or pending. The next executable
route is `production-limitation-lift-stage-1` or `final-render-path-readiness`,
with no new render, no proof media tracked in Git, and no production/public
approval inferred.

ED-10ag records Existing Output First reuse of the active ED-10af L2 selector
probe. The earlier ED-10af dry-read
`clip-ed10af-render-contract-consumer-dry-read-001` remains source coverage for
all six semantic presets at
`docs/style_intent/subtitle-render-contract-consumer-dry-read.json` and
`docs/style_intent/subtitle-render-contract-consumer-dry-read.md`. The tracked
ED-10ag lineage and observation surface is
`docs/style_intent/subtitle-render-path-lineage-observation-surface.json` and
`docs/style_intent/subtitle-render-path-lineage-observation-surface.md`; it
records no new render and lists the local ignored ASS/MP4/manifest/contact-sheet
evidence from the source probe.

ED-10af adds a tracked L2 render-path selector probe at `docs/style_intent/subtitle-render-path-selector-probe.json` and
`docs/style_intent/subtitle-render-path-selector-probe.md`. It consumes the ED-10ae render-path selector contract and selects
normal dialogue, shout / high intensity, and low-pressure whisper examples for a
tiny FFmpeg/libass diagnostic path. The probe preserves `stable_default_body_text`,
routes semantic color through badge/accent/backplate surfaces first, and carries
family / palette / font / size / outline, motion, safe-area, and line-break
metadata into readback.

Existing ignored source video/audio were present, so ED-10af generated local-only
ASS, MP4, and manifest evidence at `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass`, `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4`, and
`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json`. Those files are same-machine diagnostic evidence under
ignored `episodes/`; they are not tracked and do not approve production subtitle
design, production render, creative use, rights, publishing, or public use.

ED-10ae adds a tracked static selector-to-render-path contract at
`docs/style_intent/subtitle-render-path-selector-contract.json` and
`docs/style_intent/subtitle-render-path-selector-contract.md`. It consumes the
ED-10ad style-family / palette proof and lists the exact fields a later render
adapter would receive: semantic preset id, preset key, speaker/emotion/
readability axes, family id, palette route, font family role, font size scale,
outline/shadow strength, badge/accent/backplate tokens, stable body text color
policy, motion primitive, and safe-area / line-break behavior. All six
semantic presets remain represented, `stable_default_body_text` is preserved,
and badge/accent/backplate surfaces remain the color route. ED-10ae is L0 No
Render: no video, audio, frame, ASS, or episode artifact was generated. A later
L2 tiny render-path probe is a separate milestone. Production subtitle design,
production render, creative use, rights, publishing, and public use remain
closed or pending.

ED-10ad adds a tracked static style-family / palette axis proof at
`docs/style_intent/subtitle-style-family-palette-proof.json` and
`docs/style_intent/subtitle-style-family-palette-proof.html`. It consumes the
ED-10ac visual selector proof and keeps the same neutral / shout / whisper /
ominous / narration / system note examples, then groups them by family and
palette route. The family groups are dialogue current Keifont, emphasis
energy, quiet soft readability, ominous inner voice, narration, and system
note. The palette routes are speaker identity blue, high energy warm, quiet
cool, ominous dark, narration neutral green, and system neutral. Body subtitle
text color remains `stable_default_body_text`; palette variation stays on
badge, accent, and backplate surfaces. No render was run. No new style family
or new palette was approved. Production subtitle design, production render,
creative use, rights, publishing, and public use remain closed or pending.

ED-10ac adds a tracked static visual selector proof at
`docs/style_intent/subtitle-visual-selector-proof.json` and
`docs/style_intent/subtitle-visual-selector-proof.html`. It uses the ED-10ab
examples to make neutral / shout / whisper / ominous / narration / system note
differences visible as badge, accent, backplate, size, outline/shadow, motion,
and line-break token readback. Body subtitle text color remains stable across
all six examples; speaker and emotion color remain badge/accent-first. No new
render was run because L1 Existing Output First was sufficient for this static
proof. This does not approve production subtitle design, production render,
creative use, rights, publishing, or public use. Optional user-side work is
open-only freeform observation, maximum 3 points, not a required Review Card.

ED-10ab adds a deterministic subtitle preset selector in
`src/integrations/render/subtitle_preset_selector.py` with a tracked readback
at `docs/style_intent/subtitle-preset-selector.json`. It consumes the ED-10aa
axes (`speaker_id`, `speaker_role`, `emotion`, `intensity`, `utterance_role`,
`readability_priority`) and returns token candidates for font family role, font
size scale, outline/shadow strength, badge color, accent color, backplate/box,
motion placeholder, safe-area/line-break behavior, and stable body text color.
The examples cover neutral dialogue intensity 0, shout intensity 2, whisper
intensity 1, ominous intensity 2, narration, and system note. ED-10ab did not
run a new render; it uses the existing ED-10z readback as visual source under
the L1 Existing Output First gate.

ED-10aa adds a subtitle style intent registry in
`docs/SUBTITLE_STYLE_INTENT_REGISTRY.md` and
`docs/style_intent/subtitle-style-intent-registry.json`. Future subtitle style
work should use semantic tags (`speaker_id`, `speaker_role`, `emotion`,
`intensity`, `utterance_role`, `readability_priority`) and map them to presets
instead of asking for repeated tiny outline/shadow/opacity judgements. Body
text color remains stable by default; character-specific color should normally
appear first in speaker badge/accent surfaces. Human review is reserved for new
style families, new palettes, body text color policy changes, production-route
changes, rights, publishing, or public-use decisions.

ED-10z remains the current render-path-nearer probe source. It consumes
`clip-ed10y-candidate2-carry-forward-001` as source/previous and records a tiny
diagnostic probe for Candidate 2 (`ed10w_badge_label_pressure_adjustment`).
Candidate 0 remains fallback/current-baseline reference. Candidate 1 and
Candidate 3 remain held because the consumed review says they read too thin
compared with 0 and 2. The same Candidate 0-3 comparison should not be repeated.
Neither ED-10aa nor ED-10z approves production subtitle design, production
render, creative use, rights, publishing, upload, or public use.

Layout note for this handoff: ED-10aa records that Candidate Visual Evidence
primary samples were too small/compressed. The generator now avoids a cramped
four-column primary grid, keeps Candidate 2 lead and Candidate 0 fallback more
prominent, and treats Candidate 1 / 3 as secondary held references. This is
development readback, not a new review card.

Validation note for this handoff: the ED-10z actual rerun now succeeds when
explicit FFmpeg/FFprobe paths are supplied. It returned
`visual_proof_status=available_requires_human_review`,
`review_card_status=withheld_tiny_render_path_nearer_probe_completed`,
`subtitle_overlay_available_count=1`, and
`focused_proof_review.status=tiny_render_path_nearer_probe_completed`.
Treat `subtitle_presentation_review_pack.html` / `.json` as refreshed
same-machine local evidence only; production subtitle design, production
render, creative use, rights, publishing, upload, and public use remain closed.

ED-10y implementation checkpoint, 2026-06-24 JST: `0cf35da` was pushed to
`origin/main`. This handoff note is part of a later successor commit. A
separate terminal can resume by pulling `main`, confirming `HEAD...origin/main`
is `0 0`, then opening `.\open-current-proof.ps1` if the ignored same-machine
`episodes/` artifacts are present. The tracked implementation checkpoint
contains the ED-10y generator/profile changes, dashboard refresh, launcher
label update, and tests. The local proof pack remains ignored same-machine
evidence, not Git authority.

ED-10y consumes the latest freeform review of the ED-10w/ED-10x presentation
pack. Candidate 2 (`ed10w_badge_label_pressure_adjustment`) is now the
provisional bounded-decoration lead. Candidate 0
(`ed10w_current_pass_reference`) remains fallback/current-baseline reference.
Candidate 1 and Candidate 3 are held because they read too thin compared with
0 and 2. The same Candidate 0-3 comparison should not be repeated.

The current launcher still opens
`episodes/.../subtitle_presentation_review_pack.html`, but the page is now a
Candidate 2 carry-forward/readback surface. It keeps Candidate 2 lead and
Candidate 0 fallback visible at a glance, allows larger full-frame detail
views, and records a tiny Candidate 2 diagnostic render-path-nearer probe. The
probe does not approve production subtitle design, production render, creative
use, rights, publishing, or public use.

ED-10w is now a consumed source review target. It consumes ED-10v as a passed
diagnostic dense/stress + multiline/wrap source proof and creates one new
review surface:
`episodes/.../subtitle_presentation_review_pack.html`. The root launcher
`.\open-current-proof.ps1` opens that pack when the ignored same-machine file
exists; otherwise it falls back to the retained ED-10v focused proof. The pack
does not ask for another general Keifont review on `cut_002` / `cut_003`, and
does not ask for another pass/fail judgement on the same `cut_008` multiline
evidence.

ED-10x consumed the latest review that Candidate 0-3 images were present but
their differences were almost indistinguishable. Candidate image generation is
therefore treated as technically working but not reviewable enough in the old
full-frame-only view. The regenerated pack now surfaces compact subtitle-body
crops, SPK badge crops, and actual style delta readback before the secondary
full-frame context.

The only current ED-10w judgement is a freeform subtitle presentation choice:
keep the current pass, lighten outline/shadow pressure, adjust badge label
pressure, or use the balanced low-risk combination. A render-path readiness
card is included as a diagnostic planning probe only. It is not production
render acceptance.

ED-10j already consumed the freeform review that removed Meiryo from normal
subtitle baseline candidates. ED-10j readback also resolved the blue badge /
accent candidate to `ed10j_noto_sans_jp_local_telop_candidate`, not the Meiryo
reference. BIZ UDGothic became the ED-10k proof base.

ED-10k already generated the BIZ UDGothic diagnostic overlay proof for
`cut_002` and `cut_003`, and that proof was reviewed as not accepted for the
normal-dialogue baseline. The review says BIZ is too hard or rigid, the text
still reads thin, and the black outline pressure is too strong.

ED-10l is the current comparison/readback route and ED-10n is the current proof
route. HKCU registry and `%LOCALAPPDATA%\Microsoft\Windows\Fonts` readback now
resolve all four normal-dialogue ED-10l candidates as real requested fonts:
Keifont, 851 Chikara Yowaku, M+ FONTS, and Yasashisa Gothic. The regenerated
comparison is valid requested-font visual evidence on this same machine.

ED-10n generated the Keifont overlay proof for `cut_002` and `cut_003` using
`ed10l_keifont_pop_dialogue_candidate`. The latest review says Keifont is a
clear improvement and usable enough to compare seriously; the bottleneck is now
review UX and serial font comparison.

ED-10o generated a one-shot focused review surface. It compares Keifont, 851
Chikara Yowaku, and Yasashisa Gothic on the same lines in a subtitle-area crop
matrix, with Keifont preserved as current lead. M PLUS is excluded because its
registry readback is `M PLUS 1 Thin` via a variable font file; it needs a pinned
non-thin weight/style before baseline comparison. No font binary was
downloaded, installed, copied, vendored, staged, or committed by Codex.

ED-10o was then reviewed as easier to see. That accepts the focused review
surface as the preferred review direction, not final subtitle design or
production acceptance. Because the user did not promote 851 Chikara Yowaku or
Yasashisa Gothic over Keifont, ED-10p keeps Keifont as the provisional
normal-dialogue lead and regenerates the representative proof for `cut_002` /
`cut_003`.

ED-10q fixed the current proof review-surface regression reported after the
user ran `.\open-current-proof.ps1`: the launcher now opens
`current_proof_focused_review.html`, which starts with Review Focus, target
lines, subtitle-area evidence, the ED-10o reference, and Review Debt for
`cut_008` dense/stress coverage. The old detailed/debug overlay report remains
available from the focused page, but it is no longer the primary first view.

2026-06-22 ED-10u handoff refresh: Keifont review history is now consumed as
diagnostic representative normal-dialogue provisional baseline evidence. The
user already judged the Keifont proof clearly improved and video-usable, and
also judged the ED-10o font/review surface easier to see. ED-10q is recorded
as page-format regression repair, not font-quality review. Do not request
another general Keifont acceptance pass on `cut_002` / `cut_003`.

ED-10t regenerated the dense/stress route after the user installed Keifont and
the related ED-10l fonts for the current Windows user; same-machine generation
now resolves `requested=Keifont` and `resolved=Keifont` with
`candidate_primary_font_file_found`. ED-10u then consumed the user's note that
the visible proof did not appear to contain two-line subtitles. The cut itself
is still valid: font-bbox readback finds `sub_096` in `cut_008`, displayed at
`8.008-9.776`, wrapping as `荳狗阜繝句他繝灘・繧ｷ繧ｿ繝弱ワ繧ｭ繧ｵ` / `繝槭き縲Ａ. The focused HTML
now adds `Multiline / Wrap Evidence` near the top with a compact
`sample_multiline_wrap_1.png` screenshot capped at 220px by default. Review is
therefore allowed only for the corrected `cut_008` multiline/dense-stress axis.

2026-06-22 ED-10v handoff refresh: the user reviewed that corrected ED-10u
surface and said the subtitle display is good and all pass. Treat this as a
diagnostic dense/stress + multiline/wrap pass for the current Keifont subtitle
route. Do not emit another Review Card for this same `cut_008` evidence, and
do not reopen general Keifont acceptance from `cut_002` / `cut_003`. Line-break
behavior may be refined as more material appears, but that is now a
policy/readback or bounded adjustment topic, not a repeat acceptance review.
Future NLMYTGen sharing is only a design consideration in this slice; do not
read, edit, import from, or extract a shared package with NLMYTGen here.

Review Memory Ledger: Keifont normal-dialogue direction has `prior_review_count=3+`
and is accepted only for diagnostic representative review / provisional
normal-dialogue baseline plus diagnostic dense/stress pass. Production subtitle
design, production render, creative acceptance, rights, publishing, and public
use remain unaccepted. The current dense/stress axis is closed. Next valid
review axes must be new: line-break policy readback/tuning, bounded decoration
adjustment, production limitation-lift, or render-path probe.

## Resume Order

1. Read [RUNTIME_STATE.md](RUNTIME_STATE.md).
2. Read [SUBTITLE_FONT_CANDIDATE_SWEEP.md](SUBTITLE_FONT_CANDIDATE_SWEEP.md).
3. Read [artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md).
4. Open [dashboard/index.html](dashboard/index.html), or run:

```powershell
.\open-dashboard.ps1
```

## Next Move

Continue from
`clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001`
when the next terminal needs the latest active handoff. ED-10av remains the
source observation-frame readback, ED-10au remains the source specimen, ED-10at
remains the source observation readback, ED-10as remains the access sheet
source, and ED-10ar remains the internal review video package source.

Treat the ED-10aw artifact as tooling-adoption and review-frame planning only:
Grill-me is a local bounded helper, not repo policy; ED-10av observation is
classification only; no production, public, rights, publishing, monetization,
micro-scene, or subtitle design approval is inferred. Do not request another
user review, fixed form, yes/no response, screenshot, display polish, another
Candidate 0-3 comparison, another corrected ED-10u `cut_008` review, or
general `cut_002` / `cut_003` font-family acceptance from this handoff.

Use `review-frame-clarification` first if the specimen is acceptable but
confusing. Use `subtitle-layout-screenshot-capture` only to classify the lower
subtitle/player-UI risk. Use `representative-micro-scene-v2` only if
source/scene framing is materially wrong, and use `final-render-path-stage-4`
only for a concrete render diagnostic gap. Do not create a stage-7 normalizer
from this handoff.

Good immediate routes:

| Route | Why it helps | What it should enable |
|---|---|---|
| `review-frame-clarification` | The specimen opened and has real content, but the user did not know how to evaluate it | A later slice can define what judgement the review surface is asking for before rerendering |
| `subtitle-layout-screenshot-capture` | The lower subtitle/player-UI overlap is reported but unverified | A later slice can separate rendered subtitle placement from media-player chrome before claiming a layout failure |
| `representative-micro-scene-v2` | Only if source scene or visual framing is confirmed materially wrong | A later slice can replace the specimen for the right reason, not from vague expectation mismatch |
| `final-render-path-stage-4` | Only for a concrete render diagnostic gap after ED-10av/ED-10au/ED-10at/ED-10as/ED-10ar readback | A later slice can isolate a render-path issue without using stage-7 or implying approval |
| `optional-internal-review-video-observation` | Uses the completed ED-10ar internal review video candidate package | A later slice can record a freeform human observation without pre-approving production/public use |
| `production-limitation-lift-stage-5-user-decision-ready` | Current route already materialized by ED-10aq | Use only for backtracking or integrity repair of the current stage-5 packet |
| `production-limitation-lift-stage-4-user-decision-card` | Historical predecessor route now materialized by ED-10ap | Use only for backtracking to the stage-4 user decision-card source |
| `production-limitation-lift-stage-3-owner-review-prep` | Historical/current predecessor route now materialized by ED-10ao | Use only for backtracking to the owner-review prep source |
| `production-limitation-lift-stage-2-decision-packet` | Historical/current predecessor route now materialized by ED-10an | Use only for backtracking to the stage-2 decision packet source |
| `production-limitation-lift-stage-1` | Historical/current predecessor route now materialized by ED-10am | Use only for backtracking to the stage-1 limitation-lift source |
| `final-render-path-stage-3` | Historical/current predecessor route now materialized by ED-10al | Use only for backtracking to the stage-3 rehearsal source |
| `final-render-path-stage-2` | Uses ED-10aj selected FFmpeg/libass path plus checklist | Historical/current predecessor route now materialized by ED-10ak |
| `final-render-path-stage-1` | Uses ED-10ai to carry available diagnostic/contract evidence plus missing approval rows | Historical/current predecessor route now materialized by ED-10aj |
| `final-render-path-readiness` | Reuses ED-10af active proof and ED-10ag lineage support as source evidence | A later slice can state what is still missing before a production render route |
| `ed10ag_lineage_observation_surface` | Records Existing Output First reuse of the active ED-10af L2 selector probe while preserving the dry-read predecessor | Another terminal can inspect source and local proof paths without rerendering or opening production/public-use gates |
| `ed10z_tiny_render_path_nearer_probe` | Records Candidate 2 through the current diagnostic render path while keeping Candidate 0 fallback and Candidate 1/3 held | Another terminal can continue from probe readback without replaying the same comparison review |
| Audit ED-10y source state | Keeps the carry-forward source and probe artifact separated | A later slice can compare source/readback without treating ED-10z as production acceptance |
| FFmpeg/FFprobe tool-path rerun | Removes the current environment blocker for actual ignored proof materialization | The ED-10z HTML/JSON/PNG/MP4 proof files can be regenerated on this machine |
| production limitation-lift route | Separates diagnostic proof from public/render/rights decisions | Production subtitle design, render, rights, publishing, and public-use gates can be judged explicitly later |

Keep `ed10l_851_chikara_zuyoku_emphasis_candidate` outside the normal dialogue
baseline; it belongs to emphasis / shout / tsukkomi.

## Artifact Access

These local `episodes/` paths are same-machine evidence and may be absent on a
fresh clone. Their absence is not a Git failure.

| Artifact | Role | Open command |
|---|---|---|
| `clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001` | Active tracked ED-10aw tooling-adoption and review-frame clarification plan; keeps Grill-me bounded, forbids nested prompts, and sets review-frame clarification as first default without new media or approval | `see docs\style_intent\grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md` |
| `clip-ed10av-micro-scene-observation-frame-readback-001` | Source ED-10av observation-frame readback; records expectation mismatch, review-frame clarity failure, visual/source warning, and unverified lower subtitle/player-UI risk without approval | `see docs\style_intent\micro-scene-observation-frame-readback.md` |
| `clip-ed10au-representative-micro-scene-internal-review-specimen-001` | Source ED-10au specimen readback; records actual transcript subtitle content, verified ignored MP4/ASS/manifest access, launcher, and closed production/public gates | `powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_internal_review_specimen.ps1` |
| `clip-ed10at-internal-review-observation-readback-001` | Tracked ED-10at observation readback; records openability/duration/cue visibility as diagnostic passes and chopped/memo-like continuity plus user uncertainty as non-production warnings | `see docs\style_intent\internal-review-video-observation-readback.md` |
| `clip-ed10as-internal-review-access-sheet-fullpath-001` | Tracked ED-10as access sheet; records current-host full paths and a launcher for the ED-10ar internal review video candidate | `see docs\style_intent\internal-review-video-candidate-access-sheet.md` |
| `clip-ed10ar-internal-review-video-candidate-package-001` | Tracked ED-10ar internal review video candidate package; reuses existing ignored MP4/ASS/local manifest output without approving production/public use | `see docs\style_intent\internal-review-video-candidate-package.md` |
| `clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001` | Tracked ED-10aq user-decision-ready packet; consumes ED-10ap and prepares the later short freeform review request without asking for or approving production/public use | `see docs\style_intent\subtitle-production-limitation-lift-stage-5-user-decision-ready.md` |
| `clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001` | Tracked ED-10ap stage-4 user decision-card source; converts ED-10ao entries into future freeform decision topics without asking for or approving production/public use | `see docs\style_intent\subtitle-production-limitation-lift-stage-4-user-decision-card.md` |
| `clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001` | Tracked ED-10ao production limitation-lift stage-3 owner-review prep packet; converts ED-10an groups into future freeform review topics without approving production/public use | `see docs\style_intent\subtitle-production-limitation-lift-stage-3-owner-review-prep.md` |
| `clip-ed10an-production-limitation-lift-stage-2-decision-packet-001` | Tracked ED-10an production limitation-lift stage-2 decision packet; groups ED-10am gates into three decision-preparation groups without approving production/public use | `see docs\style_intent\subtitle-production-limitation-lift-stage-2-decision-packet.md` |
| `clip-ed10am-production-limitation-lift-stage-1-001` | Tracked ED-10am production limitation-lift stage-1 packet; separates ED-10al diagnostic evidence from production/render/creative/rights/publishing/public-use decisions and media boundaries | `see docs\style_intent\subtitle-production-limitation-lift-stage-1.md` |
| `clip-ed10al-final-render-path-stage-3-rehearsal-001` | Tracked ED-10al diagnostic rehearsal packet; records generated ignored ASS/MP4/manifest outputs, output metadata, style survival readback, and closed production/public gates | `see docs\style_intent\subtitle-final-render-path-stage-3.md` |
| `clip-ed10ak-final-render-path-stage-2-replayability-001` | Tracked ED-10ak replayability packet; records operation inputs/outputs/command family and fresh-clone absence behavior while keeping production/public gates closed | `see docs\style_intent\subtitle-final-render-path-stage-2.md` |
| `clip-ed10aj-final-render-path-stage-1-001` | Tracked ED-10aj stage-1 packet; selects the FFmpeg/libass diagnostic path as preparation only and keeps production/public gates closed | `see docs\style_intent\subtitle-final-render-path-stage-1.md` |
| `clip-ed10ai-final-render-path-readiness-packet-001` | Tracked ED-10ai readiness matrix; states what is ready for final render-path preparation and what remains missing | `see docs\style_intent\subtitle-final-render-path-readiness.md` |
| `clip-ed10ah-render-readiness-separation-readback-001` | Tracked ED-10ah render-readiness separation; states what ED-10ag proves, what remains unaccepted, and the later explicit render trigger | `see docs\style_intent\subtitle-render-readiness-separation.md` |
| `clip-ed10ah-production-limitation-lift-entry-001` | Tracked ED-10ah gate matrix; keeps ED-10af active, ED-10ag supportive, and production/public gates separate | `see docs\style_intent\subtitle-production-limitation-lift-entry.md` |
| `clip-ed10ag-lineage-and-observation-surface-001` | Tracked ED-10ag lineage and observation surface; keeps ED-10af L2 active and records no new render | `see docs\style_intent\subtitle-render-path-lineage-observation-surface.md` |
| `clip-ed10af-render-contract-consumer-dry-read-001` | Restored L0 dry-read source for all six semantic presets | `see docs\style_intent\subtitle-render-contract-consumer-dry-read.md` |
| `clip-ed10af-l2-render-path-selector-probe-001` | Source L2 selector probe with local ignored ASS/MP4/manifest evidence | `see docs\style_intent\subtitle-render-path-selector-probe.md` |
| `clip-ed10z-tiny-render-path-nearer-probe-001` | Current tiny render-path-nearer diagnostic probe using Candidate 2, with Candidate 0 fallback and Candidate 1/3 held | `.\open-current-proof.ps1` -> `episodes/.../subtitle_presentation_review_pack.html` |
| `clip-ed10y-candidate2-carry-forward-001` | Source/previous Candidate 2 lead carry-forward pack with Candidate 0 fallback | Same local path history; ED-10z is the current readback |
| `clip-ed10w-subtitle-presentation-review-pack-001` | Consumed one-pass presentation review pack that selected Candidate 2 as lead and Candidate 0 as fallback | Same local path/history; do not request the same comparison again |
| `clip-ed10r-keifont-dense-stress-proof-001` | Consumed cut_008 multiline/dense-stress diagnostic pass with valid Keifont evidence and compact `sub_096` screenshot evidence | Fallback from `.\open-current-proof.ps1` -> `episodes/.../current_proof_focused_review.html` |
| `clip-ed10p-keifont-lead-representative-proof-001` | Consumed provisional normal-dialogue baseline evidence | See artifact registry; do not request another general cut_002/cut_003 Keifont review |
| `clip-ed10o-multifont-focused-review-001` | Accepted focused review UX direction / font comparison reference | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1` |
| `clip-ed10n-keifont-overlay-proof-001` | Earlier Keifont proof reference | See artifact registry; root launcher now opens ED-10r dense/stress proof |
| `clip-ed10l-known-kirinuki-font-pack-001` | Regenerated real-font comparison/readback evidence | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1` |
| `clip-ed10k-biz-overlay-proof-001` | Reviewed rejected BIZ reference | See artifact registry; root launcher no longer opens old BIZ/ED-10n proof surfaces |
| `clip-ed10j-kirinuki-font-audit-001` | Consumed Meiryo removal / BIZ selection audit trail | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1` |

## Remote Verification Commands

Run these after pulling on another terminal:

```powershell
git status --short --branch
git rev-list --left-right --count HEAD...origin/main
git ls-files episodes
uvx python -m json.tool docs\dashboard\project-status.json
uvx python -m json.tool docs\style_intent\subtitle-render-contract-consumer-dry-read.json
uvx python -m json.tool docs\style_intent\subtitle-render-path-selector-probe.json
uvx python -m json.tool docs\style_intent\subtitle-render-path-lineage-observation-surface.json
uvx python -m json.tool docs\style_intent\subtitle-production-limitation-lift-entry.json
uvx python -m json.tool docs\style_intent\subtitle-final-render-path-readiness.json
uvx python -m json.tool docs\style_intent\subtitle-final-render-path-stage-1.json
uvx python -m json.tool docs\style_intent\subtitle-final-render-path-stage-2.json
uvx python -m json.tool docs\style_intent\subtitle-final-render-path-stage-3.json
uvx python -m json.tool docs\style_intent\subtitle-production-limitation-lift-stage-1.json
uvx python -m json.tool docs\style_intent\subtitle-production-limitation-lift-stage-2-decision-packet.json
uvx python -m json.tool docs\style_intent\subtitle-production-limitation-lift-stage-3-owner-review-prep.json
uvx python -m json.tool docs\style_intent\subtitle-production-limitation-lift-stage-4-user-decision-card.json
uvx python -m json.tool docs\font_candidates\subtitle-font-candidates.json
uvx pytest -q tests/test_docs_dashboard.py tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py
```

Expected tracked state:

- branch is `main`
- `HEAD...origin/main` is `0 0`
- `git ls-files episodes` prints nothing
- dashboard JSON parses
- restored dry-read JSON parses
- ED-10af L2 tiny render-path probe JSON parses
- ED-10ag lineage observation JSON parses
- ED-10ah production limitation-lift entry JSON parses
- ED-10ai final render-path readiness JSON parses
- ED-10aj final render-path stage-1 JSON parses
- ED-10ak final render-path stage-2 replayability JSON parses
- ED-10al final render-path stage-3 diagnostic rehearsal JSON parses
- ED-10am production limitation-lift stage-1 JSON parses
- ED-10an production limitation-lift stage-2 decision packet JSON parses
- ED-10ao production limitation-lift stage-3 owner-review prep JSON parses
- ED-10ap production limitation lift stage-4 user decision-card JSON parses
- font candidate JSON parses
- targeted tests pass, with optional skips depending on local media and Pillow
- latest pushed checkpoint is the ED-10ap successor commit
- ED-10z dry-run JSON reads `artifact_id=clip-ed10z-tiny-render-path-nearer-probe-001`,
  `review_card.action_type=NO_REVIEW_CARD_REVIEW_CONSUMED`, lead
  `ed10w_badge_label_pressure_adjustment`, fallback
  `ed10w_current_pass_reference`
- ED-10z actual rerun with explicit FFmpeg/FFprobe paths reads
  `visual_proof_status=available_requires_human_review` and
  `focused_proof_review.status=tiny_render_path_nearer_probe_completed`

## Constraints / Risks

- Do not track `episodes/`, source media, generated MP4/PNG/SRT/ASS payloads,
  or font binaries without explicit policy approval.
- Do not edit or read NLMYTGen files for this route.
- Do not claim production subtitle design, production render, creative,
  rights, publishing, upload, or public-use acceptance.
- Rights remain `pending`, and `production_candidate=false`.
