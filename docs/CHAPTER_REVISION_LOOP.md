# Chapter Revision Loop v0

Chapter Revision Loop v0 turns the JP-Pilot R3 candidate seed set into an
operator-editable working surface. It is not production acceptance, not rights
approval, not publishing, and not a render command.

The loop exists because a review report alone is easy to strand. The operator
needs a place to say what a chapter should do next: keep the candidate, rewrite
the editorial layer, request display subtitle changes, ask for a cut boundary
adjustment, split or merge a chapter, reject the candidate, or route the work
back to source selection, rights review, render planning, or NLMYTGen handoff.

## Artifacts

For JP-Pilot R3 the generated files live under the ignored local review
directory:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_board.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_board.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_patch.template.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_patch.template.csv
```

An optional `chapter_revision_patch.example.json` may also be generated. It is
a non-authoritative sample and must not be treated as an operator decision.

## CLI

```powershell
python -m src.cli.main build-chapter-revision-board `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

The command reads existing R3 review artifacts and writes a static HTML board
plus JSON/CSV patch templates. It does not access YouTube, fetch media, run
yt-dlp, render video, open Electron, save in a browser, publish, set a
thumbnail, or approve rights.

`regenerated_r3_baseline_acceptance.*` and
`production_subtitle_render_acceptance_plan.*` are optional enrichment
artifacts for later downstream acceptance planning. When the cut review packet,
evidence summary, non-repo handoff, and speed-first decision artifacts exist,
the board still generates without those optional files. In that case the JSON
uses `board_status="generated_with_warnings"` and lists the missing files in
`missing_optional_artifacts[]`; the HTML top summary repeats the warning. The
operator can still write chapter revision input, but the missing optional
readbacks should be supplied or regenerated before downstream acceptance
planning.

## Source Evidence vs Editorial Layer

The source transcript and official subtitle track remain evidence. The board
and patch template do not provide a source transcript mutation field. Operator
changes belong to a separate editorial layer:

- `editorial_intent`: what the operator wants the chapter to accomplish.
- `script_override`: optional editorial rewrite text, not a transcript edit.
- `display_subtitle_request`: requested subtitle surface wording or behavior.
- `boundary_request` / `boundary_adjustment`: request for later edit_pack or
  cut-range work, not an immediate mutation.

The Agent must not invent `editorial_intent`, `script_override`,
`display_subtitle_request`, or operator notes. Defaults stay empty or
`undecided`.

## Chapter Mapping

JP-Pilot R3 maps `cut_001` through `cut_009` to stable chapter ids `ch_001`
through `ch_009`. All current decisions remain `accept_candidate` candidate
seeds from the speed-first operator instruction. The six original
`needs_review` context results remain `retained_context_risk=true`; this board
does not rewrite them to `passed`.

Representative roles are carried for review planning:

| Cut | Role |
|---|---|
| `cut_009` | `short_passed_representative` |
| `cut_004` | `retained_context_risk_representative` |
| `cut_008` | `dense_subtitle_representative` |

## Downstream Use

The patch is meant to be read by a later normalization/application step. That
later step can decide how reviewed operator input affects `edit_pack`,
subtitle drafts, editorial script, render planning, NLMYTGen handoff, rights
review, or source selection.

`rights_blocked` is only a route to rights review. It does not unlock
production use. `production_candidate_request` is only a request field; while
rights remain pending, the actual boundary flags stay `production_candidate=false`,
`creative_acceptance=false`, and `publish_acceptance=false`.

## Boundaries

- No production render.
- No production subtitle design acceptance.
- No source transcript or official subtitle track mutation.
- No publishing, OAuth, visibility change, or thumbnail setting.
- No rights approval.
- No browser-internal save workflow or Electron operation.
- No all-cuts creative or production acceptance.
