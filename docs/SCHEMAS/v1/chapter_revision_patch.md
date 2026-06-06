# chapter_revision_patch.schema (v1)

`chapter_revision_patch_v0` records operator decisions for a chapter revision
board. It is a draft decision patch for later normalization and application.
It is not production acceptance, not rights approval, and not a direct source
transcript mutation format.

## Files

| File | Purpose |
|---|---|
| `chapter_revision_board.json` | Machine-readable board generated from R3 review evidence |
| `chapter_revision_board.html` | Static operator-readable working board |
| `chapter_revision_patch.template.json` | JSON decision patch template |
| `chapter_revision_patch.template.csv` | Spreadsheet-editable decision patch template |
| `chapter_revision_patch.example.json` | Optional non-authoritative sample |

## Top-Level Fields

```json
{
  "schema_version": "v1",
  "patch_kind": "chapter_revision_patch_v0",
  "episode_id": "jp_pilot01_hololive_bancho_20260525",
  "source_board_ref": "episodes/.../chapter_revision_board.json",
  "reviewed_by": null,
  "operator_name": null,
  "patch_status": "draft",
  "applies_to": {
    "regenerated_r3_baseline_acceptance": "regenerated_r3_baseline_acceptance.json",
    "cut_decision_speed_pass": "cut_decision_speed_pass.json"
  },
  "global_notes": "",
  "revisions": []
}
```

`patch_status` starts as `draft`. The template does not claim that any operator
has reviewed or approved the chapters.

## Revision Entry

Each `revisions[]` entry corresponds to one board chapter and source cut.

```json
{
  "chapter_id": "ch_001",
  "cut_id": "cut_001",
  "chapter_action": "undecided",
  "editorial_intent": "",
  "script_override": "",
  "display_subtitle_request": "",
  "boundary_adjustment": {
    "mode": "none",
    "start_delta_seconds": null,
    "end_delta_seconds": null,
    "merge_with_previous": false,
    "merge_with_next": false,
    "split_points_seconds": []
  },
  "rollback_signal": "undecided",
  "analyst_action": "undecided",
  "downstream_target": [],
  "operator_note": "",
  "priority": "normal",
  "confidence": "",
  "production_candidate_request": false,
  "rights_sensitive_note": ""
}
```

## Allowed Values

`chapter_action`:

- `undecided`
- `keep_as_candidate`
- `rewrite_script`
- `rewrite_display_subtitle`
- `adjust_boundary`
- `split_chapter`
- `merge_with_previous`
- `merge_with_next`
- `reject_candidate`
- `defer`
- `needs_visual_proof`

`rollback_signal`:

- `undecided`
- `local_rewrite_ok`
- `boundary_adjustment_ok`
- `split_chapter`
- `merge_with_previous`
- `merge_with_next`
- `source_not_suitable`
- `rights_blocked`
- `production_design_needed`
- `defer`

`analyst_action`:

- `undecided`
- `noop`
- `normalize_operator_notes`
- `apply_boundary_adjustment`
- `regenerate_subtitle_drafts`
- `rewrite_display_script_layer`
- `create_render_plan`
- `regenerate_representative_diagnostic`
- `create_nlmytgen_handoff`
- `escalate_rights_review`
- `mark_reject`
- `request_operator_clarification`

`downstream_target`:

- `edit_pack`
- `subtitle_drafts`
- `editorial_script`
- `render_plan`
- `nlmytgen_handoff`
- `rights_review`
- `source_selection`
- `none`

Scoped cut proxy patch templates (`chapter_revision_patch_cut_proxy_v0`) add
`proxy_decision` for `cut_002` / `cut_003` routing:

- `undecided`
- `proceed_without_visual_proof`
- `proceed_with_limitations`
- `needs_overlay_proof`
- `adjust_subtitle`
- `adjust_boundary`
- `defer`
- `reject_candidate`

`proceed_with_limitations` means the operator may keep the cut in the
candidate lane while explicit limitations or watch items remain visible. It is
diagnostic candidate routing only. It is not production subtitle design
acceptance, production render acceptance, creative acceptance, rights approval,
publishing acceptance, or public-use permission.

Scoped cut proxy patch templates also add `context_risk_handling`:

- `undecided`
- `keep_retained_risk_visible`
- `request_boundary_review`
- `needs_overlay_proof`
- `reject_due_to_context`
- `defer`

## Validation Notes

- The patch must not include a direct source transcript mutation field.
- `script_override` is an editorial layer override, not source evidence.
- `display_subtitle_request` is a subtitle surface request.
- `boundary_adjustment` is a request for later `edit_pack` or cut-range work,
  not an immediate mutation.
- `rights_blocked` routes the item to rights review and does not make
  production usage allowed.
- `production_candidate_request` defaults to `false`; it does not override
  `production_candidate=false`, `creative_acceptance=false`,
  `publish_acceptance=false`, or `rights_status=pending`.
- Empty strings and `undecided` defaults are expected until the operator writes
  actual decisions.

## CSV Columns

```text
chapter_id,cut_id,chapter_action,editorial_intent,script_override,display_subtitle_request,boundary_mode,start_delta_seconds,end_delta_seconds,merge_with_previous,merge_with_next,split_points_seconds,rollback_signal,analyst_action,downstream_target,operator_note,priority,confidence
```
