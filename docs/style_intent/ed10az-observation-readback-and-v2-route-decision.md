# ED-10az Observation Readback and V2 Route Decision

Artifact: `clip-ed10az-observation-readback-and-v2-route-decision-001`
Status: `observation_readback_v2_route_decision_ready`
Source review frame: `clip-ed10ax-review-frame-clarification-surface-001`
Source access recovery: `clip-ed10ay-thank-ed10au-local-access-recovery-readback-001`
Source specimen: `clip-ed10au-representative-micro-scene-internal-review-specimen-001`

## What Was Observed

The user opened the recovered ED-10au MP4 directly through the command. The
video opened successfully, so openability and the ED-10ay local recovery pass.
The observation does not approve the specimen.

The main user friction is not vague visual discomfort. The user could not tell what should be judged from this video.
If the target is cut quality, both ends appear cut too tightly even though the
window aligns with subtitle timing. The subtitle direction also does not match
what would be useful for a clipping/cutout video, so the user does not know how
to evaluate it.

Audio is original source audio, so it is unlikely to be broken and is not a
meaningful evaluation axis here. The subtitle is not broken, but it looks
almost the same as ordinary YouTube subtitles. VLC screenshot context shows the
ED-10au micro-scene with a large black-box Japanese subtitle near the bottom;
that context does not by itself prove layout failure.

## Classification

| axis | classification | effect |
|---|---|---|
| access/openability | `pass` | The user opened the recovered MP4. |
| ED-10ay recovery | `pass` | Same-host access recovery worked. |
| basic subtitle render | `pass_or_nonblocking` | The subtitle was not observed broken. |
| audio path | `non_informative_pass_by_source_reuse` | Source audio reuse is not the first failure axis. |
| review-frame clarity | `fail_or_partial` | The user still could not tell what to judge. |
| cut-window/source-scene framing | `warning_or_v2_candidate` | Both ends feel too tight if the target is cut quality. |
| subtitle strategy | `mismatch_for_clipping_review` | The subtitle treatment does not help evaluate clipping usefulness. |
| subtitle layout/screenshot route | `conditional_only_not_primary` | Screenshot context alone does not prove layout failure. |
| render-path-stage-4 route | `conditional_only_not_primary` | No concrete render-path gap was observed. |
| approval | `false_or_pending` | No production/public/rights/publishing/monetization approval is inferred. |
| micro-scene acceptance | `false` | The current specimen is not accepted. |

## Route Decision

The first recommended route is
`representative-micro-scene-v2-cut-window-and-review-purpose-alignment`.

This route is now enabled because the user has confirmed the mismatch ED-10ax
was waiting to classify: the specimen opens and renders, but its cut window and
subtitle strategy do not make the intended clipping/cutout review target clear.

Conditional routes stay closed as first moves:

- `subtitle-layout-screenshot-capture` is only for separating rendered subtitle
  placement from VLC/player UI or black-box subtitle presentation.
- `final-render-path-stage-4` is only for a concrete render-path gap.
- `timing-audio-check` is not first because the audio is source reuse and was
  not observed broken.
- Another pure review-frame packet is not first unless v2 cannot be designed.

## V2 Design Constraints

The v2 specimen should evaluate cut-window and clipping-review usefulness, not
just subtitle burn-in. It should avoid cutting exactly at subtitle boundaries
when that makes both ends feel too tight, and it may include modest pre-roll and
post-roll handles if source timing allows.

The subtitle treatment remains diagnostic/internal-review only. It must not
claim final production subtitle design, production render acceptance, creative
acceptance, rights clearance, publishing acceptance, public-use permission, or
monetization acceptance. If a later slice renders v2, MP4/ASS/manifest outputs
must remain ignored under `episodes/`; no media should be tracked.

Next implementation route inside the tracked readback:
`route_decision.first_recommended_route_id` and
`v2_design_constraints.next_v2_implementation_route`.

## Boundaries

- `user_review_requested_now: false`
- `new_render_run: false`
- `new_media_created: false`
- `tracked_binary_artifact_created: false`
- `episodes_tracked: false`
- `representative_micro_scene_v2_created: false`
- `representative_micro_scene_v2_enabled: true`
- `screenshot_capture_created: false`
- `subtitle_layout_screenshot_capture_required_now: false`
- `final_render_path_stage_4_required_now: false`
- `timing_audio_first_route: false`
- `stage_7_freeform_normalizer_used: false`
- `production_subtitle_design_acceptance: false`
- `production_render_acceptance: false`
- `creative_acceptance: false`
- `rights_status: pending`
- `publishing_acceptance: false`
- `public_use_permission: false`
- `monetization_acceptance: false`
- `micro_scene_accepted: false`
- `user_observation_converted_to_approval: false`
