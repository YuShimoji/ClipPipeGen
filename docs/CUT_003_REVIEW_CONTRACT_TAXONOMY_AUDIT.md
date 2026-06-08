# cut_003 Review Contract Taxonomy Audit

Last updated: 2026-06-08 JST

This tracked note preserves the local audit context for resuming from another
terminal. The detailed JSON/HTML audit files exist in the ignored R3 review
directory on this machine, but `episodes/` must remain untracked.

Ignored local audit files:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/review_contract_taxonomy_audit_cut_003.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/review_contract_taxonomy_audit_cut_003.html
```

## Classification

`blocked_required_gate_failure_stale_subtitle_overlay_proof`

The current ignored `edit_pack.json`, `cut_review_packet.json`,
`cut_decision_packet.json`, `chapter_revision_board.json`, and scoped proxy
handoff read `cut_003` as the current boundary-adjusted candidate
`22.606 -> 49.566` with `sub_010..sub_029`. The subtitle-overlay proof media
and its proof report do not yet match that authority: the local
`subtitle_overlay_visual_proof_report.json` and `subtitle_overlay_visual_proof_cut_003.srt`
still read `22.606 -> 41.725` with `sub_010..sub_024`.

That makes the Review Contract Taxonomy blocked for current cut_003 proof
review. The stale proof is still diagnostic-only evidence for the older partial
range, but it is not suitable as current operator decision input for the added
response/referral block. It is not production render acceptance, subtitle
design acceptance, creative acceptance, publishing acceptance, rights approval,
or public-use permission.

## Current Authority Versus Proof

| Item | Current authority | Proof/readback currently present |
|---|---|---|
| authority source | `edit_pack.json` | `subtitle_overlay_visual_proof_report.json` / `.srt` |
| cut | `cut_003` | `cut_003` row exists in a `cut_002,cut_003` report |
| range | `22.606 -> 49.566` | `22.606 -> 41.725` |
| duration | `26.96` | `19.119` |
| included subtitles | `sub_010..sub_029` | `sub_010..sub_024` |
| response/referral block | `sub_025..sub_029` included | absent |
| excluded next item | `seg_000030` / `sub_030` belongs to `cut_004` | also absent from the stale proof |
| style direction | `jp_clip_readable_v1` | `jp_clip_readable_v1` |
| rights | `pending` | `pending` |
| production candidate | `false` | `false` |
| production usage allowed | `false` | `false` |

`seg_000030` / `sub_030` belongs to `cut_004`, which remains deferred because
`resegmentation_target=true`.

## Required Gates

| Gate | Result | Evidence |
|---|---|---|
| `target_cut_is_cut_003` | passed | `subtitle_overlay_visual_proof_report.json` has `cut_results[cut_id=cut_003]`; the report also targets `cut_002` |
| `range_matches_current_authority` | failed | `edit_pack.json` reads `22.606 -> 49.566`; proof reads `22.606 -> 41.725` |
| `subtitles_sub_010_to_sub_029_included` | failed | `edit_pack.json` includes `sub_010..sub_029`; proof/SRT include only `sub_010..sub_024` |
| `added_response_referral_block_included` | failed | `sub_025..sub_029` and their text are absent from the proof/SRT |
| `seg_000030_sub_030_excluded` | passed | current `cut_004` owns `seg_000030..seg_000034` and `sub_030..sub_034`; proof also excludes `sub_030` |
| `style_direction_preset_readback` | passed with scope limit | `jp_clip_readable_v1`, but only for the stale proof range |
| `production_candidate_false` | passed | `false` |
| `rights_status_pending` | passed | `pending` |
| `production_usage_allowed_false` | passed | `false` |

Positive boundary flags cannot compensate for missing proof evidence. Any
`blocking_limitations=none_detected` readback is not evidence-backed for the
current local artifact set until the proof is regenerated or otherwise replaced
with current `22.606 -> 49.566` evidence.

## Human Review Still Required

These remain `required_not_automated` and have not passed:

- readability
- subtitle density
- timing sync impression
- response/referral block closure
- retained context risk interpretation

The response/referral closure item cannot be reviewed from the current stale
proof media because the proof ends before `sub_025..sub_029`.

Watch-only items remain visible:

- retained context risk visible
- cut_004 proof deferred / `resegmentation_target=true`
- diagnostic only
- line width watch
- unpinned typography parameters

The line-width and typography readbacks are watch-only and currently cover the
stale proof range, not the full boundary-adjusted `cut_003`.

## Historical And Stale Surfaces

| Surface | Audit classification | Do not use for |
|---|---|---|
| `subtitle_overlay_visual_proof_cut_003.mp4` / `.png` / `.srt` | `stale_for_current_cut_003_validation` | response/referral block visual review |
| `subtitle_overlay_visual_proof_report.json` cut_003 row | `stale_for_current_cut_003_validation` | current proof-level taxonomy pass |
| `visual_proof_cut_003.png` | `historical_only` | current cut_003 validation |
| old R3 tiny render manifest | `stale_reference` | current cut_003 validation |
| `chapter_revision_board.json` cut_003 entry | range current at `22.606 -> 49.566` | proof acceptance |
| `cut_002_cut_003_operator_proxy_decision_handoff.json` cut_003 entry | timing/subtitle text current, nested visual proof inherited from stale proof | final visual/proof decision |

The safe path is to regenerate only the ignored cut_003 subtitle-overlay proof
from the current `edit_pack.json`, then rerun this taxonomy audit. Do not stage
`episodes/`.

## What Can Be Inspected Now

The current decision packets, chapter board, and scoped proxy handoff can be
used to inspect current text/timing readback for `cut_003`, but the
subtitle-overlay proof itself is stale. Do not ask the operator for final
cut_003 visual/proxy acceptance from this proof state.

## Resume Prompt

```text
Scope: ClipPipeGen only. Do not read, edit, import, or copy files from NLMYTGen.
Current cut_003 Review Contract Taxonomy is blocked because the current authority is edit_pack cut_003=22.606 -> 49.566 with sub_010..sub_029, but subtitle_overlay_visual_proof_report.json and subtitle_overlay_visual_proof_cut_003.srt still read 22.606 -> 41.725 with sub_010..sub_024.
Regenerate only the ignored cut_003 subtitle-overlay proof/readback from the current edit_pack authority, keeping sub_030 excluded, rights_status=pending, production_candidate=false, production_usage_allowed=false, and operator fields blank/default.
Do not mutate transcript, official subtitle evidence, source media, typography/style acceptance, operator patches, rights/publication state, or cut timing. Do not stage episodes/. Parse JSON/HTML/SRT outputs, rerun the narrow taxonomy audit, confirm git ls-files episodes remains empty, and only then decide whether the proof-level taxonomy can become human-review input.
```
