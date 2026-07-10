# ClipPipeGen Docs Wiki

## What This Is

This is the human-facing wiki entrance for ClipPipeGen. It points to the
current resume surface, active review artifacts, feature status, and contracts
without requiring a reader to scan every historical Markdown file.

ClipPipeGen is a production-assist pipeline for connecting source media,
rights readback, transcript/subtitles, cut candidates, diagnostic review
artifacts, NLE handoff, and later publishing surfaces. The docs are organized
around workflow decisions, not only around file names.

## Current State

Current active focus is `OUT-02` on
`codex/out-02-local-fixture-output-proof-smoke-v0`. Its artifact is
`clip-out02-local-fixture-output-proof-smoke-v0-001`: a tracked synthetic
output-proof package with a static timeline and machine-readable readback.

The complete 2026-07-10 cross-terminal context is
[WORKFLOW_REFORM_HANDOFF.md](WORKFLOW_REFORM_HANDOFF.md). Read it after the
Runtime State before selecting another feature slice. It records the verified
development environment, the retained local-preview boundary, the workflow
friction audit, and the four decision-pending next routes. The CPD-12 cockpit
remains an upstream planning artifact, not the active resume focus.

Start here:

| Need | Entry |
|---|---|
| Current resume capsule | [RUNTIME_STATE.md](RUNTIME_STATE.md) |
| Current detailed handoff | [WORKFLOW_REFORM_HANDOFF.md](WORKFLOW_REFORM_HANDOFF.md) |
| Current terminal handoff | [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md) |
| Generated docs dashboard (legacy current focus until Excise) | [dashboard/index.html](dashboard/index.html) |
| Content planning Review Console / operator cockpit | [content_planning/operator_cockpit.html](content_planning/operator_cockpit.html) |
| Content planning dashboard | [content_planning/content_dashboard.html](content_planning/content_dashboard.html) |
| Episode seed drafts | [content_planning/episode_seed_dashboard.html](content_planning/episode_seed_dashboard.html) |
| Source resolution dashboard | [content_planning/source_resolution_dashboard.html](content_planning/source_resolution_dashboard.html) |
| Episode init dry-run plan | [content_planning/episode_init_plan_dashboard.html](content_planning/episode_init_plan_dashboard.html) |
| Source inspection packet | [content_planning/source_inspection_packet_dashboard.html](content_planning/source_inspection_packet_dashboard.html) |
| Content planning notes | [content_planning/README.md](content_planning/README.md) |
| Dashboard metadata | [dashboard/project-status.json](dashboard/project-status.json) |
| Feature progress table | [features/index.md](features/index.md) |
| Reviewable artifact registry | [../artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md) |
| Feature status authority | [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md) |
| Subtitle font candidate registry | [SUBTITLE_FONT_CANDIDATE_SWEEP.md](SUBTITLE_FONT_CANDIDATE_SWEEP.md) |
| Operator review shape | [OPERATOR_REVIEW_UX.md](OPERATOR_REVIEW_UX.md) |
| Review workflow map | [EPISODE_REVIEW_WORKFLOW.md](EPISODE_REVIEW_WORKFLOW.md) |

## Open Surfaces

Current normal order:

1. Read [RUNTIME_STATE.md](RUNTIME_STATE.md).
2. Read [WORKFLOW_REFORM_HANDOFF.md](WORKFLOW_REFORM_HANDOFF.md).
3. Open the OUT-02 proof timeline if review is needed.
4. Use the generated dashboard only for its retained feature/artifact history
   until the selected Excise slice makes it Runtime-driven.

| Command | Opens | Use when |
|---|---|---|
| `.\open-dashboard.ps1` | `docs/dashboard/index.html` | Retained historical dashboard; its current-focus generator is not Runtime-driven yet. |
| `start docs\WORKFLOW_REFORM_HANDOFF.md` | `docs/WORKFLOW_REFORM_HANDOFF.md` | Current detailed cross-terminal context, verified environment, and decision-pending routes. |
| `.\open-artifacts.ps1` | `artifacts/ARTIFACTS.md` | You need the artifact registry entry and exact open/readback notes. |
| `.\open-current-proof.ps1` | ignored local ED-10v consumed proof if present | Use as retained evidence for the passed `cut_008` multiline/dense-stress proof; do not emit another Review Card for the same `sub_096` evidence. Missing proof is reported clearly and is not a Git failure. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1` | ignored local ED-10o focused comparison if present | You need the accepted same-line comparison reference; it is not a request to rerun general Keifont acceptance. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1` | ignored local ED-10l known-font comparison if present | You need source/readback history for known kirinuki/telop font candidates, not the current proof target. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1` | ignored local ED-10j font audit if present | You need to audit the consumed contact sheet, including Meiryo reference demotion and the BIZ default selection. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison\open_comparison.ps1` | ignored local ED-10i gothic balance comparison if present | You need to audit why the bottom candidate resolved to Meiryo. |
| `.\open-font-candidates.ps1` | `docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md` | You are deciding whether ED-10h should use local-only fonts or approved font downloads. |

Regenerate the dashboard only after tracked docs/artifact registry changes:

```powershell
uvx python -m src.cli.main build-docs-dashboard --format json
```

## Next

Use CPD-12 as the current content-planning entrypoint: open the Review Console
first, review the one planning-label source item only as OK / NG / HOLD, use
Backlog for URL-waiting ideas, and use System for closed-gate/internal
readback. Use the dashboard to identify stale / unclear / over-guarded docs
only when the current CPD review surface is not being advanced. A good docs update
should make the first screen of a major doc answer:

- what the page is for
- what is true now
- what can happen next
- what constraints or risks limit the next decision

For new feature docs, start from [_templates/feature.md](_templates/feature.md)
instead of copying an older long-form handoff.

## Constraints / Risks

- Local `episodes/` artifacts are same-machine evidence and remain ignored by
  Git.
- Diagnostic proof success is not production render acceptance, production
  subtitle design acceptance, creative acceptance, rights approval, publishing
  acceptance, or public-use permission.
- Long historical closeouts belong in archive/history surfaces, not in the
  first page a human has to read.
- Visual structure diagrams should start as Mermaid, SVG, HTML, or CSS meaning
  slots before any Inkscape polish. If third-party visual assets are used, keep
  source, license, attribution, and adoption reason in the artifact manifest.
