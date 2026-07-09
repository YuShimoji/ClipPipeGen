# OUT-02 Local Fixture Output Proof

This package is a synthetic, local-only diagnostic proof for the output layer. It is designed to be inspectable as JSON, Markdown, SRT, and static HTML without relying on external source media.

- artifact_id: `clip-out02-local-fixture-output-proof-smoke-v0-001`
- proof_status: `local_fixture_output_proof_present`
- source_kind: `synthetic_fixture`
- external_media_used: `false`
- network_used: `false`
- fetch_authorized: `false`
- rights_approved: `false`
- public_ready: `false`
- production_ready: `false`

## Files

| file | purpose |
|---|---|
| `proof_manifest.json` | Machine-readable proof boundary and artifact map. |
| `proof_readback.json` | Human/reviewer readback as parseable JSON. |
| `proof_timeline.html` | Static title-card, subtitle-band, segment-list, and gate readback. |
| `fixture_edit_pack.json` | Synthetic selected-cut fixture shaped like an edit-pack handoff. |
| `fixture_subtitles.srt` | Synthetic subtitle draft for the fixture timeline. |

## What This Proves

OUT-02 closes the previous portable proof-artifact gap: a reviewer can now open the HTML timeline and a tool can parse the manifest/readback/edit-pack JSON without source media or network access.

## What Remains Outside This Proof

- `real_source_material_absent`
- `real_transcript_absent`
- `production_render_absent`
- `rights_approval_absent`
- `public_upload_gated`

## Readback

- The manifest is parseable JSON and records every external/public gate as false.
- The fixture edit pack carries selected cut ids, timing, speakers, subtitle text, and cut reasons.
- The HTML timeline is inspectable without opening a source URL, fetching media, or using a video player.
