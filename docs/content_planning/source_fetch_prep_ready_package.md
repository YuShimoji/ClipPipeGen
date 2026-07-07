# EWS-05 Human OK Fetch-Prep Ready Package

`clip-ews05-human-ok-fetch-prep-ready-package-v0-001` records the human
operator's source identity OK report for
`cpd01_bancho_marine_misunderstanding` and packages the EWS-03/EWS-04 machine
readback that makes the item ready for a future private/local fetch-prep plan.

The human report says the URL opens, the candidate intent is consistent, and
the content matches the explanation. This is only a source identity OK for the
next private/local planning gate. It does not authorize fetch/download,
transcript creation, render, thumbnail generation, upload, rights approval,
production use, or public use.

## Package Files

| Path | Purpose |
|---|---|
| `docs/content_planning/source_identity_human_ok_decision.json` | Human OK input/readback used by `record-source-identity-decision` in a tempdir smoke. |
| `docs/content_planning/source_fetch_prep_ready_package.json` | Portable package summary for the OK decision and ready fetch-prep plan state. |

## Readback

| Field | Value |
|---|---|
| source_candidate_id | `cpd01_bancho_marine_misunderstanding` |
| episode_id | `ep_seed_cpd01_bancho_marine_misunderstanding` |
| planning_label | `番長、船長を完全に勘違いする` |
| source_url | `https://www.youtube.com/watch?v=7J5aS_pcBj4` |
| identity_decision | `ok` |
| allows_fetch_prep | `true` |
| prep_state | `ready_for_future_private_fetch_plan` |
| next_gate | `explicit_private_fetch_smoke_approval_required` |
| fetch_authorized | `false` |
| media_downloaded | `false` |
| rights_approved | `false` |
| public_ready | `false` |

## Smoke Path

The validation smoke materializes only a tempdir skeleton, records
`source_identity.decision.json` from the tracked human OK decision input, then
runs `plan-source-fetch-prep`. The expected plan state is
`ready_for_future_private_fetch_plan`; all fetch/media/rights/public flags
remain false.

```powershell
python -m src.cli.main init-episode-workspace --plan docs/content_planning/episode_workspace_plan.json --target <tempdir> --materialize --format json
python -m src.cli.main record-source-identity-decision --workspace <tempdir>\ep_seed_cpd01_bancho_marine_misunderstanding --decision docs/content_planning/source_identity_human_ok_decision.json --format json
python -m src.cli.main plan-source-fetch-prep --workspace <tempdir>\ep_seed_cpd01_bancho_marine_misunderstanding --format json
```

No tracked `episodes/` files are part of this package.
