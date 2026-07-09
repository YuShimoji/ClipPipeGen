# INT-01 Parallel Lane Aggregation / Thread Registry Sync v0

`clip-int01-parallel-lane-aggregation-v0-001` records the integration of four
parallel ClipPipeGen lanes onto `codex/int-01-parallel-lane-aggregation-v0`.
The branch was created from latest `origin/main` because no remote INT-01
branch existed. It does not merge into main and does not create a PR.

## Source Branches

| Lane | Source branch | Head used | Prompt commit | Preserved artifact |
|---|---|---:|---:|---|
| TRI-01 | `origin/codex/tri-01-safety-overcapture-triage-v0` | `b04e422` | `b04e422` | `clip-tri01-safety-overcapture-triage-v0-001` |
| HUB-01 | `origin/codex/hub-01-external-source-registry-v0` | `4f780d5` | `cf0e846` | `clip-hub01-external-source-registry-v0-001` |
| OUT-01 | `origin/codex/out-01-output-layer-gap-logger-v0` | `e903120` | `774beb0` | `clip-out01-output-layer-gap-logger-v0-001` |
| EWS-05 | `origin/codex/ews-05-human-ok-fetch-prep-ready-v0` | `d2adc66` | `d2adc66` | `clip-ews05-human-ok-fetch-prep-ready-package-v0-001` |

HUB-01 and OUT-01 used the remote heads observed during integration; both had
handoff refresh commits beyond the prompt commit. That is intentional because
INT-01 is a remote-sync integration branch.

## Merge And Conflict Handling

| Merge step | Result | Conflict scope | Resolution |
|---|---|---|---|
| TRI-01 | fast-forward | none | Accepted the triage report, builder, README, and test as-is. |
| HUB-01 | clean merge | none | Preserved external source registry fixtures, CLI, pipeline, docs, dashboard updates, and test. |
| OUT-01 | merge conflict | `src/cli/main.py` | Kept both HUB and OUT imports/help/dispatch entries. |
| EWS-05 | merge conflicts | `artifacts/ARTIFACTS.md`, `docs/CURRENT_HANDOFF.md`, `docs/RUNTIME_STATE.md`, `docs/dashboard/*`, `src/cli/main.py` | Kept EWS package and CLI entries, kept HUB/OUT entries, made resume surfaces INT-01-facing, added this report plus registry, and regenerated dashboard outputs. |

The shared CLI dispatcher now exposes the lane commands together:
`build-external-source-registry`, `build-output-layer-gap-report`,
`build-episode-workspace-plan`, `init-episode-workspace`,
`inspect-episode-workspace`, `prepare-source-identity-decision`,
`record-source-identity-decision`, and `plan-source-fetch-prep`.

## Preserved Lane Artifacts

TRI-01 preserves `docs/triage/safety_overcapture_report.json`,
`docs/triage/safety_overcapture_report.md`, `docs/triage/README.md`,
`tools/triage/build_safety_overcapture_report.py`, and
`tests/test_safety_overcapture_triage.py`.

HUB-01 preserves `docs/external_sources/external_source_registry.json`, local
RSS/manual fixtures, the external source registry CLI/pipeline, and
`tests/test_external_source_registry.py`.

OUT-01 preserves `docs/output_layer/video_output_gap_log.json`,
`docs/output_layer/output_capability_matrix.md`,
`docs/output_layer/local_output_readback.html`,
`docs/output_layer/OUT_01_HANDOFF.md`, the output-layer report builder/CLI,
and `tests/test_output_layer_gap_report.py`.

EWS-05 preserves
`docs/content_planning/source_fetch_prep_ready_package.json`,
`docs/content_planning/source_fetch_prep_ready_package.md`,
`docs/content_planning/source_identity_human_ok_decision.json`, the episode
workspace CLI/pipeline, and `tests/test_episode_workspace.py`.

## Central Files

The integration touches central navigation and resume files:
`artifacts/ARTIFACTS.md`, `docs/CURRENT_HANDOFF.md`,
`docs/RUNTIME_STATE.md`, `docs/THREAD_REGISTRY.md`,
`docs/integration/int01_parallel_lane_aggregation_report.json`,
`docs/dashboard/index.html`, `docs/dashboard/project-status.json`,
`docs/features/index.md`, `docs/index.md`, and `src/cli/main.py`.

## Remaining Review Risk

The remaining risk is not a code conflict; it is review coordination. Four lane
contexts now share one resume surface, and the dashboard is regenerated from the
integrated tree. A manual review should accept that combined central surface
before this branch is promoted to main.

OUT-02 should base on `codex/int-01-parallel-lane-aggregation-v0` after that
review. Starting OUT-02 from `origin/main` alone would lose the OUT-01 gap log
and the context needed to avoid reopening closed EWS/HUB/TRI gates.

## Closed Gates

- No source URL was opened.
- No live RSS or external metadata fetch was performed.
- No media was downloaded.
- No transcript, render, thumbnail, upload, or public output was created.
- No OAuth, credential, payment, or rights/legal decision was made.
- No main merge or PR was created.

## Local Validation

Targeted validation passed:

| Check | Result |
|---|---|
| `python -m pytest -q tests/test_episode_workspace.py tests/test_external_source_registry.py tests/test_safety_overcapture_triage.py tests/test_output_layer_gap_report.py tests/test_docs_dashboard.py tests/test_asset_fetch_boundary.py` | `58 passed` |
| `python -m src.cli.main build-external-source-registry --format json` | Passed with 4 records and all network/media/rights/public flags false |
| `python -m src.cli.main build-output-layer-gap-report --format json` | Passed with `proof_status=proof_missing`, `production_ready=false`, `public_ready=false` |
| `python -m src.cli.main build-docs-dashboard --format json` | Passed with 120 features and 65 artifacts |
| `python -m src.cli.main build-episode-workspace-plan --format json` | Passed with planned local workspace and no worker URL opening or media download |
| JSON parse targets | Passed for HUB, TRI, OUT, EWS, and INT-01 JSON reports |
| `git diff --check` | Passed |
| `git ls-files episodes` | Passed with no tracked files |
