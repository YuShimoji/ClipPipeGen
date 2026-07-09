# Thread Registry - ClipPipeGen Parallel Lane Sync

This registry records the active integration branch and the parallel lane
outputs it carries. It is a resume surface, not an approval surface: source
URLs, fetch/download, media generation, rights/publication, and production gates
remain closed.

| thread_id | lane_id | active_or_completed_slice | repo | branch | HEAD | worktree_or_terminal | target_artifact | weight | status | conflict_scope | next_action |
|---|---|---|---|---|---:|---|---|---|---|---|---|
| `clip-int-01-parallel-lane-aggregation-v0` | `INT-01` | active integration slice | `ClipPipeGen` | `codex/int-01-parallel-lane-aggregation-v0` | `branch_head_after_push` | `C:/Users/PLANNER007/ClipPipeGen` | `clip-int01-parallel-lane-aggregation-v0-001` | W5 | integrated | Central docs, dashboard, artifact registry, and shared CLI dispatcher | Push branch, then review before any main merge |
| `clip-tri-01-safety-overcapture-triage-v0` | `TRI-01` | completed safety overcapture triage | `ClipPipeGen` | `codex/tri-01-safety-overcapture-triage-v0` | `b04e422` | remote source branch | `clip-tri01-safety-overcapture-triage-v0-001` | W4 | integrated | none in merge | Keep as safety review evidence for future acceptance/public readiness decisions |
| `clip-hub-01-external-source-registry-v0` | `HUB-01` | completed external source registry | `ClipPipeGen` | `codex/hub-01-external-source-registry-v0` | `4f780d5` | remote source branch | `clip-hub01-external-source-registry-v0-001` | W4 | integrated | `docs/CURRENT_HANDOFF.md`, `docs/RUNTIME_STATE.md`, `docs/dashboard/*`, `src/cli/main.py`, `artifacts/ARTIFACTS.md` | Review registry rows before HUB-02 maps anything into CPD source planning |
| `clip-out-01-output-layer-gap-logger-v0` | `OUT-01` | completed output layer gap logger | `ClipPipeGen` | `codex/out-01-output-layer-gap-logger-v0` | `e903120` | remote source branch | `clip-out01-output-layer-gap-logger-v0-001` | W4 | integrated | `src/cli/main.py` | Use this integration branch as OUT-02 base after review |
| `clip-ews-05-human-ok-fetch-prep-ready-v0` | `EWS-05` | completed human OK fetch-prep package | `ClipPipeGen` | `codex/ews-05-human-ok-fetch-prep-ready-v0` | `d2adc66` | remote source branch | `clip-ews05-human-ok-fetch-prep-ready-package-v0-001` | W5 | integrated | `artifacts/ARTIFACTS.md`, `docs/CURRENT_HANDOFF.md`, `docs/RUNTIME_STATE.md`, `docs/dashboard/*`, `src/cli/main.py` | Require explicit private fetch smoke approval before any fetch/download lane |
| `clip-out-02-local-fixture-output-proof-smoke-v0` | `OUT-02` | completed local fixture proof smoke | `ClipPipeGen` | `codex/out-02-local-fixture-output-proof-smoke-v0` | `branch_head_after_push` | `C:/Users/PLANNER007/ClipPipeGen` | `clip-out02-local-fixture-output-proof-smoke-v0-001` | W5 | completed | `docs/output_layer/*`, `tools/output_layer/build_output_layer_gap_report.py`, `tests/test_output_layer_gap_report.py` | Review the local fixture proof package, then use `OUT-03-selected-cut-proof-link` if the next output-layer move is selected-cut traceability |

## Integration Notes

- Preferred merge order was followed: TRI, HUB, OUT, then EWS.
- The integration branch was created from latest `origin/main` because no remote
  INT-01 branch existed.
- No source URL was opened, no live RSS was fetched, no media was downloaded,
  no credentials/OAuth were used, and no production/public/rights decision was
  made.
- `episodes/` must remain ignored and untracked.
