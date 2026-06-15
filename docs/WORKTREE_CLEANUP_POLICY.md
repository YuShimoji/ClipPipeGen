# Worktree Cleanup Policy

This policy keeps ClipPipeGen slice work from mixing with unrelated local
state while preserving active human review evidence.

## Active Allowlist

The current active retained preview session is protected from cleanup until the
human decision is consumed or the operator explicitly retires it:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/
```

This directory is ignored by Git, but it is not disposable cache while the
review is pending. It may contain copied MP4/PNG/SRT/ASS assets used by
`index.html`, `review_manifest.json`, `decision_request.json`, and the blank
`decision_template.json`.

## Strong Cleanup

Before code or docs changes, classify the worktree into:

- active-scope tracked files
- unrelated tracked modifications
- untracked files
- ignored generated/cache files
- active retained preview session artifacts

Restore unrelated tracked modifications with `git restore -- <path>`.
Delete unrelated untracked files with a path-scoped cleanup such as
`git clean -fd -- <path>`. Remove cache/temp artifacts such as
`.pytest_cache`, `__pycache__`, `_tmp`, and local browser automation state when
they are not needed for the active report.

Do not run broad ignored cleanup such as `git clean -fdX` while an active
preview session is retained. Broad ignored cleanup can remove `episodes/`
artifacts that are valid local review evidence.

## Public Git Hygiene

`episodes/` stays ignored by default because it may contain raw source media,
diagnostic render outputs, subtitle payloads, and other source-derived
artifacts. `git ls-files episodes` should remain empty unless a separate
private/artifact-store strategy has been approved.

Remote Git can verify the tracked builder, docs, and tests. It cannot directly
verify ignored local preview assets, so reports must separate remote evidence
from same-machine local readback.
