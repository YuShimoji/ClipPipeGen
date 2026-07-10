# OUT-02 Handoff - Local Fixture Output Proof Smoke

Last updated: 2026-07-09 JST

This is the scoped resume packet for the OUT-02 output/video branch. It keeps
the branch context, proof artifacts, validation, and next routes in the project
so another terminal can continue without the previous chat.

## Branch To Pull

Use the OUT-02 branch when resuming this slice:

```powershell
git fetch --prune origin
git switch codex/out-02-local-fixture-output-proof-smoke-v0
git pull --ff-only
git status --short --branch
git log -1 --oneline --decorate
git ls-files episodes
```

Expected state:

- Branch: `codex/out-02-local-fixture-output-proof-smoke-v0`
- Remote: `origin/codex/out-02-local-fixture-output-proof-smoke-v0`
- Proof implementation commit: `2dd7162 Add OUT-02 local fixture output proof`
- Latest branch head: use `git log -1 --oneline --decorate` after pull; later
  handoff-only commits are expected on this branch.
- `git ls-files episodes`: empty
- No tracked source media, rendered media, or local episode artifacts

## What OUT-02 Contains

OUT-02 turns the OUT-01 `proof_missing` readback into a tracked, inspectable
local fixture proof package. The package is synthetic fixture data only. It
does not open source URLs, fetch/download external media, run yt-dlp, use
OAuth/API, approve rights, create production render, mark public-ready, upload,
or track `episodes/`.

Tracked proof artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Proof manifest | `docs/output_layer/local_fixture_output_proof/proof_manifest.json` | Machine-readable proof boundary, artifact map, selected cuts, and closed gates |
| Proof readback | `docs/output_layer/local_fixture_output_proof/proof_readback.json` | Parseable reviewer readback for title card, subtitle band, segments, and export notes |
| Timeline HTML | `docs/output_layer/local_fixture_output_proof/proof_timeline.html` | Static human-readable proof surface with no video player, form, or execution controls |
| Fixture edit pack | `docs/output_layer/local_fixture_output_proof/fixture_edit_pack.json` | Synthetic selected-cut fixture shaped like an edit-pack handoff |
| Fixture subtitles | `docs/output_layer/local_fixture_output_proof/fixture_subtitles.srt` | Synthetic subtitle draft for the fixture timeline |
| Package README | `docs/output_layer/local_fixture_output_proof/README.md` | Human readback for what the proof does and does not prove |
| Gap log | `docs/output_layer/video_output_gap_log.json` | Machine-readable capability matrix, gap delta, proof status, and recommended next slice |
| Capability matrix | `docs/output_layer/output_capability_matrix.md` | Human-readable output-layer capability and gap table |
| Local readback | `docs/output_layer/local_output_readback.html` | Top-level static readback that links the proof package |

The artifact id is `clip-out02-local-fixture-output-proof-smoke-v0-001`.

## Current Readback

The generated report intentionally says:

- `proof_status=local_fixture_output_proof_present`
- `source_kind=synthetic_fixture`
- `external_media_used=false`
- `network_used=false`
- `fetch_authorized=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`
- `recommended_next_slice=OUT-03-selected-cut-proof-link`

Current fixture rows:

| Fixture piece | Readback |
|---|---|
| selected cuts | `cut_fixture_001`, `cut_fixture_002`, `cut_fixture_003` |
| timeline duration | `9.6` seconds |
| subtitle drafts | 3 synthetic SRT/JSON rows |
| visual surfaces | title card, subtitle band, segment list, export-readiness notes |

## What OUT-02 Closes And Leaves Open

| State | Meaning | Next pressure |
|---|---|---|
| Closed | Portable proof artifact is now present and parseable | Review `proof_timeline.html` and JSON readback |
| Remaining local gap | Real source video/audio is absent | Requires approved local material or private fetch smoke |
| Remaining local gap | Real transcript is absent | Requires transcript route after material/source decision |
| Remaining output gap | Production render is absent | Requires separate final-render/output review route |
| True gate | Rights approval is absent | Requires explicit human-owned rights/material-use clearance |
| True gate | Public upload/OAuth is absent | Requires publishing decision packet before any upload |

## Validation Already Run

The following checks passed on this branch:

```powershell
python -m src.cli.main build-output-layer-gap-report --format json
python -m json.tool docs/output_layer/video_output_gap_log.json
python -m json.tool docs/output_layer/local_fixture_output_proof/proof_manifest.json
python -m json.tool docs/output_layer/local_fixture_output_proof/proof_readback.json
python -m json.tool docs/output_layer/local_fixture_output_proof/fixture_edit_pack.json
python -m pytest -q tests/test_output_layer_gap_report.py tests/test_asset_fetch_boundary.py
git diff --check
git ls-files episodes
```

Observed results:

- CLI returned `local_fixture_output_proof_present`, 10 capability rows, 7 gap rows, and `OUT-03-selected-cut-proof-link`.
- JSON parse passed for the gap log, proof manifest, proof readback, and fixture edit pack.
- Targeted pytest returned `11 passed`.
- `git diff --check` passed.
- `git ls-files episodes` printed nothing.

## Do Not Cross These Gates

Do not do any of the following from this handoff without explicit human
approval:

- Open or fetch source URLs.
- Download video/audio or run source acquisition.
- Run yt-dlp.
- Generate a transcript from real external media.
- Render production media or claim production render acceptance.
- Upload, publish, set thumbnails, use OAuth/API keys, or touch payment.
- Approve rights, legal status, public readiness, production readiness, or creative acceptance.
- Track files under `episodes/`.
- Edit NLMYTGen files or other repos.
- Reset, clean, force-push, rewrite history, or discard unrelated work.

## Next Local Routes

| Route | Bottleneck reduced | What it enables |
|---|---|---|
| `OUT-03-selected-cut-proof-link` | The proof package exists, but selected cut ids are not yet a first-class route into the proof surface | Reviewers can jump from an edit decision to exact proof JSON/HTML |
| `EDIT-01-edit-operation-matrix` | Edit semantics are still fixture/readback-only | Later real transcript/edit work can map operations to proof requirements |
| `future-local-material-proof-or-private-fetch-smoke` | Synthetic proof does not verify real pixels/audio/source-ledger linkage | A later approved material route can produce real diagnostic output without public claims |
| `rights-material-use-clearance` | Public/production value is blocked by rights/public-use gates | Human-owned rights decision can be separated from local diagnostic success |

## Remote Verification Commands

Run these after pulling on another terminal:

```powershell
git status --short --branch
git rev-parse --short HEAD
git ls-files episodes
python -m json.tool docs/output_layer/video_output_gap_log.json
python -m json.tool docs/output_layer/local_fixture_output_proof/proof_manifest.json
python -m json.tool docs/output_layer/local_fixture_output_proof/proof_readback.json
python -m json.tool docs/output_layer/local_fixture_output_proof/fixture_edit_pack.json
python -m pytest -q tests/test_output_layer_gap_report.py tests/test_asset_fetch_boundary.py
```

Expected tracked state:

- branch is `codex/out-02-local-fixture-output-proof-smoke-v0`
- head is `2dd7162` or a later handoff-only commit on the same branch
- `git ls-files episodes` prints nothing
- proof JSON parses
- targeted tests pass
