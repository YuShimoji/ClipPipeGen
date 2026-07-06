# CPD Content Planning Dashboards

## What This Is

CPD-01 is a local/offline-first planning surface for deciding what ClipPipeGen
should inspect next. It converts fixture or manual seed metadata into candidate
cards, transparent scoring, channel strategy cards, JSON output, and a static
HTML dashboard.

CPD-02 bridges those candidate cards into draft episode seed records. The seed
drafts show what would be inspected, fetched, transcribed, edited, and
thumbnailed later, but they do not perform those operations.

CPD-03 resolves source metadata for those draft episode seeds at the planning
boundary. It parses already-known source URLs, marks missing/invalid URLs, and
writes a manual source registry template for operator intake without contacting
YouTube or downloading media.

CPD-04 turns source-resolved records into dry-run episode initialization plans.
It shows the exact episode root and later artifact paths that would be used, but
does not create those folders or files.

CPD-05 turns ready CPD-04 dry-run plans into source inspection packet records,
a blank decision registry template, and a static dashboard. It lets an operator
review the source URL and decide whether a later gated slice should proceed,
without opening the URL or authorizing fetch inside this slice.

CPD-06 consolidates CPD-01 through CPD-05 into the single human-facing operator
cockpit. It puts the one source-backed candidate first, separates missing-URL
ideas from blocked/hold items, and moves the individual CPD dashboards into an
internal appendix.

CPD-07 revises that same operator cockpit into a vertical Primary Review Card
with native dark mode. It is a UX layer only, not a new fetch/init/source review
pipeline stage.

CPD-08 turns the polished CPD-07 surface into an Operator Home. It keeps dark
mode and the Primary Review Card, then adds visible funnel meters, an Action
Queue, and links from the top-level state to the detailed candidate sections.
It is information architecture only, not a source review result.

CPD-09 keeps the same entrypoint but changes the first screen into a Briefing
Board. It replaces the card-heavy home with an annotated flow, one Primary
Review Script, usage-frequency navigation, and a compact Candidate Ledger for
source-missing and hold items.

CPD-10 keeps the accepted Briefing Board and repairs the visible Candidate
Ledger so Japanese titles stay readable as phrases. It replaces the previous
wide ledger table with stacked, responsive rows, Japanese operator-facing state
labels, and de-emphasized machine IDs.

CPD-11 turns that same cockpit into a reusable Review Workbench view shell. It
keeps the current source action and readable Candidate Ledger, but moves
source-waiting items into Backlog mode, closed gates into System mode, and
reduces case-specific explanatory copy in the default view.

If you are reviewing as a human, open the CPD-11 operator cockpit first. The
older CPD HTML pages are retained as internal readback and should not be used as
separate report surfaces unless debugging a specific planning stage.

This is upstream planning only. It does not download video/audio, render media,
publish, use OAuth, set thumbnails, approve rights, or mark any candidate as
production/public usable.

## Current Artifacts

| Field | Value |
|---|---|
| CPD-01 artifact_id | `clip-cpd01-content-candidate-dashboard-v0-001` |
| CPD-02 artifact_id | `clip-cpd02-candidate-to-episode-seed-bridge-v0-001` |
| CPD-03 artifact_id | `clip-cpd03-source-metadata-resolver-v0-001` |
| CPD-04 artifact_id | `clip-cpd04-init-episode-dry-run-plan-v0-001` |
| CPD-05 artifact_id | `clip-cpd05-source-inspection-packet-v0-001` |
| CPD-06 artifact_id | `clip-cpd06-operator-cockpit-consolidation-v0-001` |
| CPD-07 artifact_id | `clip-cpd07-operator-cockpit-ux-v2-dark-mode-v0-001` |
| CPD-08 artifact_id | `clip-cpd08-operator-home-funnel-meters-v0-001` |
| CPD-09 artifact_id | `clip-cpd09-operator-briefing-board-v0-001` |
| CPD-10 artifact_id | `clip-cpd10-candidate-ledger-readability-v0-001` |
| CPD-11 artifact_id | `clip-cpd11-operator-view-shell-v0-001` |
| fixture | `samples/content_planning/content_candidates_fixture.json` |
| operator cockpit HTML | `docs/content_planning/operator_cockpit.html` |
| operator cockpit JSON | `docs/content_planning/operator_cockpit.json` |
| content candidate JSON | `docs/content_planning/content_candidates.json` |
| channel strategy JSON | `docs/content_planning/channel_strategy.json` |
| content dashboard HTML | `docs/content_planning/content_dashboard.html` |
| episode seed draft JSON | `docs/content_planning/episode_seed_drafts.json` |
| episode seed dashboard HTML | `docs/content_planning/episode_seed_dashboard.html` |
| source resolution JSON | `docs/content_planning/episode_seed_source_resolution.json` |
| source resolution dashboard HTML | `docs/content_planning/source_resolution_dashboard.html` |
| manual source registry template | `docs/content_planning/source_metadata_registry.template.json` |
| episode init dry-run plan JSON | `docs/content_planning/episode_init_plan.json` |
| episode init dry-run dashboard HTML | `docs/content_planning/episode_init_plan_dashboard.html` |
| source inspection packet JSON | `docs/content_planning/source_inspection_packet.json` |
| source inspection dashboard HTML | `docs/content_planning/source_inspection_packet_dashboard.html` |
| source inspection decision template | `docs/content_planning/source_inspection_decisions.template.json` |

## Regenerate

Content candidate dashboard:

```powershell
uvx python -m src.cli.main build-content-candidate-dashboard --format json
```

Episode seed drafts:

```powershell
uvx python -m src.cli.main build-episode-seed-drafts --format json
```

Source resolution records and manual source intake template:

```powershell
uvx python -m src.cli.main resolve-episode-seed-sources --format json
```

Episode initialization dry-run plans:

```powershell
uvx python -m src.cli.main build-episode-init-plan --format json
```

Source inspection packets and blank decision registry template:

```powershell
uvx python -m src.cli.main build-source-inspection-packet --format json
```

Operator cockpit:

```powershell
uvx python -m src.cli.main build-operator-cockpit --format json
```

Optional output location:

```powershell
uvx python -m src.cli.main build-content-candidate-dashboard `
  --input samples/content_planning/content_candidates_fixture.json `
  --output-dir docs/content_planning `
  --format json
```

Optional seed selection:

```powershell
uvx python -m src.cli.main build-episode-seed-drafts `
  --input docs/content_planning/content_candidates.json `
  --output docs/content_planning/episode_seed_drafts.json `
  --dashboard docs/content_planning/episode_seed_dashboard.html `
  --candidate-id cpd01_bancho_marine_misunderstanding `
  --format json
```

Optional manual source registry input:

```powershell
uvx python -m src.cli.main resolve-episode-seed-sources `
  --input docs/content_planning/episode_seed_drafts.json `
  --registry docs/content_planning/source_metadata_registry.json `
  --registry-template docs/content_planning/source_metadata_registry.template.json `
  --output docs/content_planning/episode_seed_source_resolution.json `
  --dashboard docs/content_planning/source_resolution_dashboard.html `
  --format json
```

Optional episode init plan paths:

```powershell
uvx python -m src.cli.main build-episode-init-plan `
  --input docs/content_planning/episode_seed_source_resolution.json `
  --seed-input docs/content_planning/episode_seed_drafts.json `
  --output docs/content_planning/episode_init_plan.json `
  --dashboard docs/content_planning/episode_init_plan_dashboard.html `
  --format json
```

Optional source inspection packet paths:

```powershell
uvx python -m src.cli.main build-source-inspection-packet `
  --input docs/content_planning/episode_init_plan.json `
  --output docs/content_planning/source_inspection_packet.json `
  --dashboard docs/content_planning/source_inspection_packet_dashboard.html `
  --decision-template docs/content_planning/source_inspection_decisions.template.json `
  --format json
```

Optional operator cockpit paths:

```powershell
uvx python -m src.cli.main build-operator-cockpit `
  --candidates docs/content_planning/content_candidates.json `
  --seeds docs/content_planning/episode_seed_drafts.json `
  --source-resolution docs/content_planning/episode_seed_source_resolution.json `
  --episode-init-plan docs/content_planning/episode_init_plan.json `
  --source-inspection-packet docs/content_planning/source_inspection_packet.json `
  --decision-template docs/content_planning/source_inspection_decisions.template.json `
  --output docs/content_planning/operator_cockpit.json `
  --dashboard docs/content_planning/operator_cockpit.html `
  --format json
```

## Review Boundary

- `rights_readback.status=pending`, `unverified`, or `unknown` is allowed as
  readback for candidate planning.
- Public use, publishing, monetization, production render, production subtitle
  design, and rights acceptance remain separate gates.
- Manual seed candidates are not source truth. They require public source
  metadata and human review before episode seed creation.
- Strategy cards are directional planning records, not executable prompts.
- Episode seed drafts use planned later paths only. They do not create
  `episodes/` folders, material files, transcripts, edit packs, renders,
  thumbnails, or upload state.
- Source resolution records parse existing URLs and prepare human intake for
  missing URLs only. They do not search the web, call YouTube APIs, fetch media,
  initialize episode skeletons, or approve source/rights/public use.
- `source_metadata_registry.template.json` is a blank operator intake template.
  Fill it only with real, human-confirmed public source metadata before rerunning
  CPD-03 with `--registry`.
- Episode init plans are dry-run records. `planned_episode_root` and
  `planned_artifacts` are strings only; CPD-04 does not create `episodes/`
  folders, `rights_manifest.json`, `material_ledger.json`, fetch receipts,
  transcripts, edit packs, thumbnail briefs, preview packs, renders, or uploads.
- Source inspection packets are pre-review records only. CPD-05 does not open
  source URLs, authorize future private/local fetch, create real episode
  artifacts, approve rights, or mark sources as production/public usable.
- `source_inspection_decisions.template.json` starts with `decision=pending`,
  `approve_future_private_fetch=false`, and null review result fields. Fill it
  only after a human/operator source inspection.
- The operator cockpit is the normal human entry point. The individual CPD
  HTML/JSON files remain linked as internal artifacts only; they should not be
  treated as separate human report requests.
- CPD-11 cockpit HTML defaults to native dark mode, includes a local
  Light/Dark toggle, and starts with a reusable Review Workbench. Review,
  Backlog, and System modes separate the current source action from unresolved
  ideas and closed-gate/internal readback. Older CPD-01 through CPD-05
  dashboards remain developer readback surfaces.
- The JP/EN phrase-gap idea is currently `source_missing_idea_backlog`, not a
  source-backed video candidate. It needs a real `source_url` and source
  metadata before any fetch/init lane can continue.

## Next Useful Moves

1. Open `docs/content_planning/operator_cockpit.html` first. It shows the
   Review Workbench, state rail, Review / Backlog / System mode links, and the
   collapsed responsive Candidate Ledger with native dark mode.
2. Review the single ready source URL as a human/operator source identity
   check from Review mode only. This is still just OK / NG / HOLD source
   identity judgement, not fetch or approval.
3. Fill `source_inspection_decisions.template.json` only after that review, then
   decide whether a later gated slice may run real source inspection/fetch/init.
4. Fill real source URLs for unresolved seed records in a local
   `source_metadata_registry.json`, then rerun CPD-03 and CPD-04.
5. Add a read-only public metadata adapter behind an explicit flag, keeping
   fixture tests offline.
