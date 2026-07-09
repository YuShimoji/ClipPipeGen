# External Sources

HUB-01 is an offline source intake stub. It normalizes local RSS XML and manual
JSON fixtures into a source candidate registry that later CPD/HUB slices can
review. It does not fetch live RSS feeds, open source URLs, call YouTube or
other metadata APIs, download media, generate transcripts, render, create
thumbnails, upload, approve rights, or mark anything production/public ready.

## Current Artifact

| Field | Value |
|---|---|
| artifact_id | `clip-hub01-external-source-registry-v0-001` |
| registry JSON | `docs/external_sources/external_source_registry.json` |
| RSS fixture | `samples/external_sources/rss_fixture.xml` |
| manual seeds | `samples/external_sources/manual_source_seeds.json` |
| CLI | `uvx python -m src.cli.main build-external-source-registry --format json` |

## Regenerate

```powershell
uvx python -m src.cli.main build-external-source-registry --format json
```

Optional paths:

```powershell
uvx python -m src.cli.main build-external-source-registry `
  --rss-fixture samples/external_sources/rss_fixture.xml `
  --manual-seeds samples/external_sources/manual_source_seeds.json `
  --output docs/external_sources/external_source_registry.json `
  --format json
```

## Readback

The registry records `rss_item` and `manual_seed` rows with source URL/title/feed
metadata, tags, language hints, confidence, candidate state, provenance, and the
next local action. Every row keeps:

- `network_used=false`
- `media_downloaded=false`
- `rights_approved=false`
- `public_ready=false`

Manual and RSS rows are unverified candidate metadata. They do not automatically
advance CPD/EWS candidates to source identity OK or fetch-ready state. HUB-02 can
later map reviewed registry rows into CPD/EWS planning, but this slice only
creates the local registry and parseable readback.
