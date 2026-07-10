---
id: workflow-reform-handoff
title: Workflow Reform and Cross-Terminal Handoff
type: handoff
status: current
health: out02_ready_with_workflow_reform_decision_pending
last_touched: 2026-07-10
active_artifact: clip-out02-local-fixture-output-proof-smoke-v0-001
active_branch: codex/out-02-local-fixture-output-proof-smoke-v0
current_slice: OUT-02
phase: handoff_ready
human_entrypoint: docs/output_layer/local_fixture_output_proof/proof_timeline.html
machine_readback: docs/output_layer/local_fixture_output_proof/proof_readback.json
next_action: Choose the workflow-reform entry point before opening another feature slice.
decision_required: excise_control_plane_or_verify_main_integration_or_advance_dev_reproducibility_or_explore_next_visible_slice
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, docs/CURRENT_HANDOFF.md, docs/output_layer/OUT_02_HANDOFF.md, docs/triage/safety_overcapture_report.md, docs/AGENT_OPERATION_CONTRACT.md, docs/PROMPT_CHANGE_MANAGEMENT.md, artifacts/ARTIFACTS.md
---

# Workflow Reform and Cross-Terminal Handoff

This handoff preserves the remote-sync, development-readiness, and workflow
audit completed on 2026-07-10 JST. It is the current detailed context packet;
`docs/RUNTIME_STATE.md` remains the active resume surface.

## Resume From Another Terminal

Run the following from the ClipPipeGen repository, then read this file before
starting a new feature slice:

```powershell
git fetch --prune origin
git switch codex/out-02-local-fixture-output-proof-smoke-v0
git pull --ff-only
git status --short --branch
git log -1 --oneline --decorate
git rev-list --left-right --count origin/main...HEAD
```

Expected state at handoff creation:

| Check | Expected readback |
|---|---|
| Active branch | `codex/out-02-local-fixture-output-proof-smoke-v0` |
| Pre-handoff baseline | `efb625e Refresh OUT-02 handoff surfaces` |
| Upstream divergence before this handoff commit | `0 0` |
| Relationship to `origin/main` | branch is 23 commits ahead; main has no commits absent from this branch |
| Tracked episode artifacts | `git ls-files episodes` prints nothing |
| Worktree policy | preserve the retained human preview session; remove only path-scoped cache/temp files when safe |

After this handoff is committed and pushed, use the pulled branch HEAD rather
than the pre-handoff baseline above as the authoritative commit.

## What Is Ready Now

The active delivery is OUT-02, a tracked synthetic local fixture output proof.
It connects three selected-cut fixture rows, subtitle drafts, a static timeline,
and machine-readable output-gap readback. Its primary review entry is:

```text
docs/output_layer/local_fixture_output_proof/proof_timeline.html
```

Its machine readback is:

```text
docs/output_layer/local_fixture_output_proof/proof_readback.json
```

The fixture proves package/readback shape only. It does not establish real
source-media linkage, real transcript quality, production render, rights
approval, public readiness, or upload readiness. The existing product-next
route is `OUT-03-selected-cut-proof-link`; do not treat that route as selected
until the workflow-reform choice below is made.

INT-01 remains the integration base beneath OUT-02 and preserves the TRI-01
safety triage, HUB-01 external-source registry, OUT-01 gap logger, and EWS-05
human-OK fetch-prep package. The shared CLI dispatcher retains each lane.

## Local State That Must Survive

`episodes/` is intentionally ignored. The following retained human-review
session exists on this machine and is not disposable cache:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/
```

Do not delete, stage, or claim remote portability for this directory. Remote
Git can verify the tracked builder, docs, code, and tests only; ignored media
and previews require same-machine readback.

If another device needs the actual MP4/PNG/SRT/ASS preview assets, use an
explicit private artifact-transfer mechanism and the existing non-repo manifest
readback. Do not solve that transfer by staging `episodes/` into Git.

## Development Readiness Verified

| Area | Result | Notes |
|---|---|---|
| Python | 3.11.0 available | Meets the repository's Python 3.10+ requirement. |
| Full Python suite | `370 passed, 16 skipped` | Optional image tests are skipped in the default `uvx` environment. |
| Pillow visual suite | `85 passed` | Run with `uvx --with pillow`. |
| OUT-02 targeted tests | `11 passed` | Output-layer and asset-fetch boundary coverage. |
| GUI smoke | Node and Electron smoke passed | Node 22.19.0, npm 10.9.3, Electron 42.0.0. |
| Media tooling | FFmpeg/FFprobe 8.1.1; yt-dlp 2026.03.17 | Available, but no real-media operation was run during this handoff. |
| JSON/readback | Four OUT-02 JSON files parse | Gap log, proof manifest, proof readback, fixture edit pack. |
| Git hygiene | `git diff --check` and `git ls-files episodes` passed | No tracked episode media. |

Real Vosk STT remains conditional because its Python package/model are not
configured locally. The NLMYTGen bridge remains conditional because
`config/nlmytgen_path.json` is absent. Python dependencies are not yet locked
or version-pinned; the GUI has `package-lock.json`, but fresh-clone setup should
eventually standardize on `npm ci`.

## Why Development Slowed Down

| Friction | Evidence captured in the repository | Working diagnosis |
|---|---|---|
| Safety overcapture | TRI-01 identifies 5 true external gates and 6 overcapture candidates. Some tests assert absence of words rather than absence of unsafe calls. | Repeated caveats and prose contracts make permitted reversible work look blocked. |
| Prompt and slice fragmentation | In the last 100 commits, ED-10 consumed 70 commits and 44 suffixes in 14 days. | Small revisions became new slices, artifacts, and handoffs instead of one outcome batch. |
| Current-state drift | Runtime starts with OUT-02; the Wiki/dashboard pointed at CPD-12; later handoff sections still listed ED-10 routes. | Multiple manual current-state surfaces were treated as co-equal authorities. |
| Wiki freshness failure | `src/pipeline/docs_dashboard.py` fixed the date and CPD-12 focus; tests protected that fixed value. | Rebuilding the dashboard could not make it follow the active branch. |
| Visual revision loop | Subtitle exploration moved through Noto, Meiryo, BIZ, known-font, and Keifont routes after full artifacts existed. | Direction, review axes, and exit conditions were not selected before broad implementation. |

The audit measured 51% of changed lines in the recent 100-commit window as
docs/artifacts. The central dashboard, Runtime, artifact registry, Current
Handoff, and generated feature index were updated on most commits, yet still
disagreed. This is a workflow/control-plane issue, not a request for agents to
write more duplicated documentation.

## Recommended Operating Model

Use one outcome-sized execution prompt per slice:

```text
ORIENT -> EXPLORE (only for user-visible ambiguity) -> CHARTER -> EXECUTE
-> REVIEW_READY -> ACCEPT | POLISH_ONCE | REFRAME | PARK -> CLOSE -> STEER
```

| Role | Owns | Does not own |
|---|---|---|
| Supervising AI | Outcome, priority, selected direction, acceptance, and true stop conditions | Step-by-step implementation instruction or a new prompt for every minor delta |
| Development AI | Reversible implementation choices, related fixes, validation, review entry, state sync, commit/push | Choosing an unreviewed large design direction or making public/rights decisions |
| User | Product direction, external-gate decisions, final accept/reframe judgement | File-by-file tracking or routine documentation synchronization |

The execution prompt must name the achieved user/consumer state, selected
direction, in-scope and out-of-scope work, authority to make reversible local
changes, true stops, acceptance checks, one review entry, and required state
synchronization. Keep minor discoveries in a MICRO-SPEC inbox; batch them at
close or when five accumulate. New feature/artifact IDs are for changed
consumer value, not for each polish pass.

True stops remain destructive Git or unreviewed large deletion, dependency
addition, DB/auth/API contract change, credentials/OAuth/payment, public upload
or visibility change, rights/legal/production acceptance, cross-repo work,
active-preview deletion, and a genuine product-spec conflict. Initial test
failures, pending-rights local diagnostic work, minor UI choices, optional
artifact absence, related docs, and state generation should not stop the
execution loop.

## User-Visible Work Must Explore Before It Expands

For layout, color, typography, animation, language, or content-shape work,
offer three low-cost directions before building the whole artifact:

| Direction | Purpose |
|---|---|
| Advance | Complete the current direction with the least conceptual change. |
| Shift | Change hierarchy, interaction, or presentation structure. |
| Create | Extend into an adjacent audience, format, or content opportunity. |

Each direction needs a representative specimen, user benefit, cost, reversibility,
and what it unlocks. Build only a 10-20% representative surface after selection.
Review results are `ACCEPT`, `POLISH` (one bundled pass by default), `REFRAME`
(return to exploration), or `PARK`. A changed intent is a reframe, not a chain
of pixel-level patches.

Trigger a small Exploration Pulse every two slices, after two consecutive
same-lane slices, or when revision work exceeds roughly 20%. Rotate among
layout/review flow, JP/EN and CJK/Latin typography, color/contrast, font roles
and licensing, reduced-motion-aware animation, vertical/Shorts variants,
bilingual subtitles, playlist/metadata packs, and removal/automation ideas.
Keep at most five deferred ideas; promote, discard, or retain them with a reason.

## State and Wiki Reform: Recommended First Slice

Do not add another manual status ledger. Use the existing
`docs/RUNTIME_STATE.md` front matter as the sole current-state input, limited
to fields such as `current_slice`, `phase`, `active_branch`, `active_artifact`,
`last_verified_at`, `human_entrypoint`, `machine_readback`, `next_action`, and
`decision_required`.

Generate the current portions of `CURRENT_HANDOFF.md`, `docs/index.md`, the
dashboard JSON/HTML, the feature index, and the current Thread Registry row
from that input. Keep Runtime under 150 lines and Current Handoff under 100
lines; archive old closeouts instead of leaving them under a later `Current`
heading. A `close-slice` workflow should update all derived surfaces, confirm
the active artifact exists in the registry, and fail validation if a generated
surface no longer matches the canonical fields.

An external status page should be a generated mirror (for example GitHub Pages),
not another manually maintained Wiki. It must show both the active development
branch and the main-integrated state so a branch 23 commits ahead of main is not
misrepresented as main.

Known reconciliation issue: legacy OUT-02/OUT-03 rows in
`docs/FEATURE_REGISTRY.md` do not yet use the same naming semantics as the
current OUT-02 branch and `OUT-03-selected-cut-proof-link` recommendation.
Preserve them for now; reconcile the feature registry only in the selected
Excise/control-plane or explicit specification-reconciliation slice.

## Decision Status and Next Entry Points

The user has requested workflow optimization and preservation of this context.
The implementation order has not yet been selected. The recommended first move
is **Excise**, because control-plane drift currently makes every later slice
more expensive.

| Entry point | Bottleneck reduced | Enables |
|---|---|---|
| Excise (recommended) | Duplicate current-state surfaces and dashboard hardcode | One state update can keep Runtime, Wiki, dashboard, and handoff aligned. |
| Verify | Active branch is 23 commits ahead of main | A deliberate main-integration review without merging by assumption. |
| Advance | Python environment is not locked and verification is dispersed | A reproducible developer profile and one verify command; dependency changes require explicit approval. |
| Explore | Next visible feature could repeat the post-build revision loop | Three direction specimens before another broad visual/content implementation. |

Until an entry point is selected, do not start a new feature slice merely to
produce another handoff or readback artifact.

## Guardrails for the Next Terminal

- Read `AGENTS.md`, `docs/RUNTIME_STATE.md`, this handoff, and
  `docs/output_layer/OUT_02_HANDOFF.md` before changing scope.
- Keep `episodes/` ignored and preserve the retained preview session.
- Do not merge/rebase/reset/force-push or edit another repository without the
  corresponding user authority.
- Do not treat OUT-02 synthetic proof as real-media, rights, production, or
  publication acceptance.
- If implementing the recommended Excise slice, update the dashboard builder
  and its tests together; do not manually patch generated dashboard output as
  the lasting fix.
