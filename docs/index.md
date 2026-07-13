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

Current focus is `OUT-07` on
`codex/out-07-internal-operator-delivery-pack-v0`. The active review artifact is
`clip-out07-shorts-poster-frame-direction-proof-v0-001`. Thank の既知 source
revision から、source `22.858s`／sequence `11.930s`／`cut_003`／`sub_010`
を照合した単一 cover direction proxy が local review-ready になった。
Planner-known pixel hash とは一致しないため分類は
`cover_direction_semantic_proxy`。Planner007 の exact accepted baseline は
historical accepted fact のままだが Thank には存在せず、strict exact route
も変更していない。人間判断はこの proxy の cover 方向だけである。

`RUNTIME_STATE.md` is the current-state source for the generated dashboard.
Canonical `main` is the OUT-06 accepted-after-bounded-repair baseline. OUT-07
remains unmerged for operator review. The CPD-12 cockpit remains an upstream
planning artifact, not the active resume focus.

Start here:

| Need | Entry |
|---|---|
| Current resume capsule | [RUNTIME_STATE.md](RUNTIME_STATE.md) |
| Current terminal handoff | [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md) |
| Supervising review status | [SUPERVISOR_STATUS_REPORT.md](SUPERVISOR_STATUS_REPORT.md) |
| Generated docs dashboard | [dashboard/index.html](dashboard/index.html) |
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
| Cross-machine active rebuild contract | [../artifacts/ACTIVE_REBUILD.json](../artifacts/ACTIVE_REBUILD.json) |
| Feature status authority | [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md) |
| Subtitle font candidate registry | [SUBTITLE_FONT_CANDIDATE_SWEEP.md](SUBTITLE_FONT_CANDIDATE_SWEEP.md) |
| Operator review shape | [OPERATOR_REVIEW_UX.md](OPERATOR_REVIEW_UX.md) |
| Review workflow map | [EPISODE_REVIEW_WORKFLOW.md](EPISODE_REVIEW_WORKFLOW.md) |

## Open Surfaces

Normal order:

1. Run `.\open-dashboard.ps1`.
2. Choose the Runtime-driven current artifact or another registered artifact.
3. Use an artifact-specific launcher only when needed.

| Command | Opens | Use when |
|---|---|---|
| `.\open-dashboard.ps1` | `docs/dashboard/index.html` | Default start for Runtime-driven current focus, feature progress, active artifacts, and doc-health findings. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_native_shorts_cover_direction_proxy\open_preview.ps1 -Port 8071` | Thank OUT-07 semantic cover direction proxy | Opens the local-only single-direction page. It is not an exact-baseline or portable entrypoint. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_internal_operator_delivery_pack\open_delivery.ps1 -Serve` | ignored OUT-07 predecessor operator pack | Reopen the port-8070 metadata/video provenance pack only when predecessor evidence is needed; its rejected 16:9 directions are not current candidates. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out06_complete_narrative_short_delivery_candidate\open_preview.ps1 -Serve` | ignored OUT-06 repaired complete narrative short | Open the seekable localhost review route for the repaired 38.633333-second `cut_001 -> cut_002 -> cut_003` internal short. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out04_editorial_representative_sequence\open_preview.ps1` | ignored accepted OUT-04 editorial sequence | Reopen the accepted single 11.678-second `cut_001 -> cut_002` sequence if predecessor evidence is needed. |
| `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out03_real_local_selected_cut_proof\open_preview.ps1` | ignored accepted OUT-03 real-local selected-cut proof | Reopen the accepted `cut_002` evidence if needed; add `-Serve` only when local-file playback is blocked. |
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

OUT-07 is ready for one Thank-host semantic cover-direction review even though
the exact accepted baseline is absent. The next human decision is only whether
to ACCEPT or REFRAME the source-derived frame plus its existing subtitle as the
Shorts list cover direction. Do not reopen title/description/tags, baseline acceptance, production/
public use, thumbnail upload, metadata publication, visibility, made-for-kids,
publishing, upload, or rights approval.
Use the dashboard to return to tracked project context. A good docs update should make
the first screen of a major doc answer:

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
