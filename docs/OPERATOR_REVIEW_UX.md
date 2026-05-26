# Operator Review UX Contract

This document defines the restart and review response shape for ClipPipeGen operator-facing work. It keeps machine evidence available, but the first thing a human sees must be reviewability: what can be reviewed now, what is missing, and what decision is being asked for.

## Reviewability States

Use these states before listing proof commands or recovery commands.

| State | Meaning | First response behavior |
|---|---|---|
| `review_ready` | Required review reports and local review artifacts are present in this workspace. | Tell the operator what to inspect and what decision to make. |
| `review_blocked_missing_artifacts` | Git alone does not provide the ignored episode artifacts required for R3 review. | Do not send the operator to the review report first; name the missing artifacts and the restore/regenerate route. |
| `diagnostic_only` | The artifact is useful as local evidence, but not as creative, production, or publish acceptance. | Show the boundary before any command appendix. |
| `production_blocked_rights_pending` | Rights are readable but not approved for production/public use. | Keep production/public language blocked until a separate rights approval slice exists. |

## Restart Response Order

Every non-trivial restart report should start in this order:

1. What is possible in this workspace now.
2. What is missing.
3. What the user should look at next.
4. What the user should decide.
5. What the Agent must not do.
6. Evidence, recovery commands, and reproduction commands as appendix material.

Command lists are not the main review path. They belong under recovery, reproduction, or advanced appendix sections, or inside collapsed details in HTML.

## Cut Review Return Shape

The operator may respond in natural language. They do not need to start with JSON, strict `cut_001: accept_candidate` lines, or a complete machine-readable patch.

The Agent may later normalize the human review into a structured decision patch such as `accept_candidate`, `adjust_boundary`, or `reject`, but only after the operator has expressed the review judgment. The Agent must not auto-accept, auto-reject, or auto-adjust final cuts without that human review.

## HTML Report Roles

| Report | Primary role | Command location |
|---|---|---|
| `cut_review_report.html` | Human final cut/context review screen. | Commands stay out of the main path. |
| `evidence_summary.html` | Evidence and artifact inventory check. | Reproduction commands are appendix/details. |
| `non_repo_artifact_handoff.html` | Git-excluded artifact identity, missing state, and regeneration boundary. | Recovery/regeneration commands are appendix/details. |

`build-non-repo-handoff` creates the `non_repo_artifact_handoff` manifest/report. It is not a render command and does not recreate `rendered_video.mp4`; any render command belongs to the recovery appendix after missing inputs are understood.

If R3 artifacts are missing, final cut/context review is blocked. The response should not instruct the operator to open `cut_review_report.html` as the first action. It should show the missing state, the restoration route for ignored episode artifacts, and the regeneration conditions.

## Completion Wording

Use "complete" with a qualifier. `sync complete`, `handoff complete`, and `diagnostic complete` do not mean `review complete`, `production accepted`, `rights approved`, or `publish ready`.

For JP-Pilot R3, the current recommendation can remain final cut/context review, but only in a workspace where the review artifacts exist. In a fresh checkout or a workspace missing ignored episode artifacts, the first operator state is `review_blocked_missing_artifacts`.
