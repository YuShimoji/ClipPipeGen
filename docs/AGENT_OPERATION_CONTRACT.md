# Agent Operation Contract

This contract records how Codex-style agents should work in ClipPipeGen. It is
not a replacement for project invariants; it explains how to keep working
without losing artifact reviewability or crossing production/public boundaries.

## Authority Order

When instructions differ, use this order:

1. Current user message and attached task.
2. [AGENTS.md](../AGENTS.md).
3. [docs/INVARIANTS.md](INVARIANTS.md).
4. [docs/AUTOMATION_BOUNDARY.md](AUTOMATION_BOUNDARY.md).
5. Active resume state in [docs/RUNTIME_STATE.md](RUNTIME_STATE.md).
6. Feature and artifact-specific contracts, such as
   [docs/REVIEW_ARTIFACT_BUNDLE_CONTRACT.md](REVIEW_ARTIFACT_BUNDLE_CONTRACT.md)
   and [artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md).

If a later task intentionally changes an older project rule, update the
project-local docs in the same slice so future agents do not have to infer the
new rule from chat history.

## Self-Running Loop

Agents should continue through implementation, related docs, local validation,
and cleanup when all of the following are true:

- the next improvement is clear
- the change is reversible
- the work stays inside ClipPipeGen
- the work does not require rights/publication judgment, credentials, or
  destructive operations
- the active retained preview session can be preserved

Do not stop just because the first test run fails, a self-review finds a small
gap, or a report can be made clearer. Form a cause hypothesis, apply one
scoped fix, and rerun the relevant validation. Stop after repeated blockers
only when the same blocker recurs after scoped fixes and the next action would
leave the allowed scope.

## True Stop Conditions

Stop and ask the user before:

- destructive git operations, force push, reset, history rewrite, or
  unreviewed large deletion
- public upload, OAuth, credential handling, payment, rights approval,
  visibility change, or production/public acceptance
- reading or editing NLMYTGen files
- mutating source-derived `episodes/` artifacts when the task is docs-only
- filling a human decision template without a human answer
- deleting the active retained `human_preview_session/`

## Conditions That Should Not Stop Work

These should be handled inside the loop:

- unrelated dirty tracked files that can be restored safely
- unrelated untracked files that can be deleted with path-scoped cleanup
- cache/temp files such as `.pytest_cache`, `__pycache__`, and `_tmp`
- missing optional local artifacts, when the contract says to report them as
  missing instead of treating them as production blockers
- initial test failures with a narrow, reversible cause hypothesis
- report wording that needs a clearer artifact path or open command

## Visual Artifact Workflow

Visual work must end in a reviewable artifact, not a scattered path list.

For SH-08, the current single local entry point is:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/index.html
```

Use the retained open command first:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session\open_preview.ps1
```

Use the server fallback only when file open is unstable:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session\serve_preview.ps1 -Port 8000
```

Do not ask a human to search through local HTML/MP4 files when a manifest,
single entry point, or open command exists.

## Artifact Manifest Requirement

Tracked docs may reference ignored local artifacts only with a manifest
boundary. The report must state whether the artifact is:

- tracked and portable
- local retained and same-machine only
- missing and requiring regeneration

The tracked artifact registry is [artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md).
It must not claim that ignored local files exist on every clone.

## Report Format

For non-trivial tasks, reports should cover these sections with real content.
Use natural Japanese headings and omit empty sections when they do not apply:

1. Summary
2. Changed files
3. Artifacts
   - artifact_id
   - repo_relative_path
   - preview_url or open_command
   - screenshot/contact-sheet/storyboard when applicable
4. Commands run and results
5. Validation
6. Decision packet, if user judgment is needed
7. Blockers, only for true stop conditions
8. Next complete prompt for another Agent, only when the user asks for a handoff

Do not use the section list as a thin template. Each included section must help
the reader decide what can happen next without opening files.

## Prohibited Report Contents

Do not include:

- internal reasoning settings or hidden analysis
- model UI words or depth labels
- unsupported production/public acceptance claims
- unverified absolute local paths as authority
- long raw logs when a concise result readback is enough
- monitoring-only comments inside an Agent execution prompt

When writing a code block intended for another Agent, include only execution
instructions. Rationale, supervision notes, and review comments belong outside
that code block.
