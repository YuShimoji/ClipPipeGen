# cut_003 Review Contract Taxonomy Audit

Last updated: 2026-06-11 JST

This tracked note preserves the local audit context for resuming from another
terminal. Detailed JSON/HTML proof artifacts live under the ignored R3 review
directory on this machine, but `episodes/` must remain untracked.

Ignored local audit/proof files include:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_003.mp4
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_003.png
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/review_contract_taxonomy_audit_cut_003.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/review_contract_taxonomy_audit_cut_003.html
```

## Classification

`current_cut_003_diagnostic_readability_baseline_accepted`

The previous stale-proof blocker has been resolved by the later regenerated
cut_003 subtitle-overlay visual proof. Current ignored readback now matches the
authority boundary:

| Item | Current readback |
|---|---|
| cut | `cut_003` |
| range | `22.606 -> 49.566` |
| included subtitles | `sub_010..sub_029` |
| response/referral block | `sub_025..sub_029` included |
| excluded next item | `sub_030` excluded and remains outside `cut_003` |
| diagnostic candidate | `jp_clip_dialogue_badge_left_v0` |
| selected mode | `badge_left_dialogue` |
| renderer | `ffmpeg_subtitles_filter_ass` |
| wrapping algorithm | `japanese_boundary_font_bbox_pixel_wrap_v1` |
| explicit ASS line breaks | `true` |
| one-character orphan lines | absent |
| suffix-tail prevention | applied; current report count `2` |
| renderer gap | visible: `controlled_line_breaks_carried_renderer_bbox_not_claimed` |
| rights | `pending` |
| production candidate | `false` |
| production usage allowed | `false` |

Human review accepted the current cut_003 diagnostic burned-in subtitle proof
readability baseline only. Record this as
`diagnostic_subtitle_wrapping_readability_acceptance=true` for `cut_003`.

This does not accept production subtitle design, production render, creative
quality, rights approval, publishing, or public use.

## Gates

| Gate | Result | Evidence |
|---|---|---|
| `target_cut_is_cut_003` | passed | `subtitle_overlay_visual_proof_report.json` targets `cut_003` |
| `range_matches_current_authority` | passed | proof range reads `22.606 -> 49.566` |
| `subtitles_sub_010_to_sub_029_included` | passed | proof subtitle source reads `sub_010..sub_029` |
| `added_response_referral_block_included` | passed | sample/readback includes `sub_025..sub_029`; response/referral sample is `sub_025` |
| `sub_030_excluded` | passed | current proof excludes `sub_030` |
| `style_direction_preset_readback` | passed with scope limit | diagnostic candidate `jp_clip_dialogue_badge_left_v0` under `jp_clip_dialogue_reference_v0` |
| `production_candidate_false` | passed | `false` |
| `rights_status_pending` | passed | `pending` |
| `production_usage_allowed_false` | passed | `false` |

## Remaining Limits

The accepted scope is limited to current cut_003 diagnostic burned-in proof
readability. It covers the current proof's wrapping/readability/safe-area/timing
impression at the diagnostic proof level only.

These remain unaccepted:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Retained context risk remains visible through the operator decision route:
`proxy_decision=proceed_with_limitations` and
`context_risk_handling=keep_retained_risk_visible`.

## Representative Review Link

The first cross-scene subtitle design review start is tracked in
[REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md](REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md).
That review selects `cut_002`, `cut_003`, and `cut_008` as the smallest
representative set, but concludes that the current contract is not yet proven
stable beyond `cut_003`.

## Resume Prompt

```text
Scope: ClipPipeGen only. Do not read, edit, import, or copy files from NLMYTGen.
Current cut_003 diagnostic burned-in proof readability is accepted only for the current cut_003 diagnostic proof baseline. Keep cut_003=22.606 -> 49.566, sub_010..sub_029 included, sub_030 excluded, proxy_decision=proceed_with_limitations, context_risk_handling=keep_retained_risk_visible, renderer_gap visible, rights_status=pending, production_candidate=false, production_usage_allowed=false, and production_subtitle_design_acceptance=false.
Continue with the representative subtitle design review route: verify a current-contract comparison proof for cut_002 and keep cut_008 blocked until its needs_adjustment state is explicitly handled. Do not stage episodes/.
```
