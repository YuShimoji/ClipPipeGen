# OUT-02 Output Capability Matrix

Readback matrix for the output/video layer after a local synthetic fixture proof package has been generated. This artifact does not fetch media, run production render, approve rights, or claim public readiness.

- artifact_id: `clip-out02-local-fixture-output-proof-smoke-v0-001`
- generated_at: `2026-07-09T08:54:28.950688+00:00`
- proof_status: `local_fixture_output_proof_present`
- source_kind: `synthetic_fixture`
- external_media_used: `false`
- network_used: `false`
- production_ready: `false`
- public_ready: `false`

## Local Fixture Output Proof

| artifact | path |
|---|---|
| proof_manifest | `docs/output_layer/local_fixture_output_proof/proof_manifest.json` |
| proof_readback | `docs/output_layer/local_fixture_output_proof/proof_readback.json` |
| proof_timeline | `docs/output_layer/local_fixture_output_proof/proof_timeline.html` |
| fixture_edit_pack | `docs/output_layer/local_fixture_output_proof/fixture_edit_pack.json` |
| fixture_subtitles | `docs/output_layer/local_fixture_output_proof/fixture_subtitles.srt` |
| readme | `docs/output_layer/local_fixture_output_proof/README.md` |

## Capability Matrix

| capability_id | current_state | evidence_path | missing_input | next_local_action | blocked_by_true_gate | notes |
|---|---|---|---|---|---|---|
| source_material_presence | fixture_only | docs/output_layer/local_fixture_output_proof/proof_manifest.json | Real source_video/source_audio materials remain absent for this slice. | Use a later approved local-material or private-fetch smoke slice for real source proof. | false | OUT-02 uses synthetic fixture data only; it does not prove real media availability. |
| transcript_readiness | fixture_only | docs/output_layer/local_fixture_output_proof/proof_manifest.json | A real or reviewed transcript for an actual target source is still absent. | Link selected cuts to real transcript rows only after local material/transcript approval. | false | Fixture subtitles prove readback shape, not STT or transcript quality. |
| edit_pack_readiness | fixture_only | docs/output_layer/local_fixture_output_proof/fixture_edit_pack.json | A real edit_pack connected to reviewed transcript and source media remains absent. | Use OUT-03 to connect selected_cut_ids to proof/readback artifacts. | false | Fixture edit pack carries selected cuts, timing, speakers, subtitles, and reasons. |
| subtitle_readiness | fixture_only | docs/output_layer/local_fixture_output_proof/fixture_subtitles.srt | Production subtitle design and real subtitle timing review remain absent. | Keep subtitle design acceptance separate from fixture proof and real output review. | false | Fixture SRT is diagnostic readback only. |
| local_fixture_output_proof | fixture_only | docs/output_layer/local_fixture_output_proof/proof_manifest.json | None for the synthetic fixture proof package. | Use OUT-03 to link selected cuts to the proof surface. | false | OUT-02 closes the portable proof artifact gap without external media. |
| thumbnail_brief_readiness | planned | src/pipeline/episode_init_plan.py | A reviewable thumbnail brief/output artifact tied to selected source materials. | Promote thumbnail brief seed fields into an operator-reviewable output-layer artifact later. | false | Thumbnail output remains a separate planning/readback lane. |
| preview_pack_readiness | local_ready | docs/PREVIEW_PACK.md | A target episode with local media or existing source audio material. | Build a read-only local preview pack once operator-supplied material exists. | false | Preview pack is useful readback, but it is not this fixture proof or a rendered video proof. |
| nle_export_readiness | local_ready | docs/SCHEMAS/v1/nle_export.md | A validated edit_pack with selected cuts and optional transcript refs. | Export CSV/JSON/HTML cut-list readback for human review or NLE handoff. | false | NLE export proves edit structure, not final encoded video. |
| local_render_proof_readiness | local_ready | docs/SCHEMAS/v1/tiny_render.md | Real or approved local source video/audio and edit_pack inputs for an encoded diagnostic proof. | Run a narrow diagnostic render only after local materials are explicitly available. | false | OUT-02 is a static fixture proof; production render remains out of scope. |
| public_upload_readiness | gated | docs/AUTOMATION_BOUNDARY.md | Rights acceptance, publication judgment, account/OAuth setup, and public target selection. | Keep public/upload out of local proof work; prepare only decision packets for human review. | true | This is a true gate, not a missing local automation task. |

## Gap Log

| gap_id | status | evidence_path | missing_input | local_vs_true_gate | suggested_next_slice | validation |
|---|---|---|---|---|---|---|
| gap_current_no_proof_artifact | local_fixture_output_proof_present | docs/output_layer/local_fixture_output_proof/proof_manifest.json | Closed for synthetic fixture proof; real media proof remains a separate gap. | Local fixture gap closed; no rights/publication gate crossed. | OUT-03-selected-cut-proof-link | Parse manifest/readback/edit-pack JSON and inspect proof_timeline.html. |
| gap_real_source_material_absent | remaining_gap | docs/RUNTIME_STATE.md | Real source_video/source_audio materials are absent from this proof. | Local gap until operator-supplied material or an approved private fetch smoke exists. | future-local-material-proof-or-private-fetch-smoke | A later run records material ids and leaves git ls-files episodes empty. |
| gap_real_transcript_absent | remaining_gap | docs/SCHEMAS/v1/transcript.md | Real or reviewed transcript rows for a target source are absent. | Local gap; transcript work can remain diagnostic while rights/public gates stay closed. | EDIT-01-edit-operation-matrix | Transcript-linked selected cuts preserve production/public flags as false. |
| gap_production_render_absent | remaining_gap | docs/AUTOMATION_BOUNDARY.md | No production render or production subtitle burn-in acceptance exists. | Diagnostic render can be local; production acceptance is a separate human gate. | final-render-path-output-review-after-local-material | Any later render manifest keeps production_candidate=false until accepted. |
| gap_rights_approval_absent | true_gate | docs/INVARIANTS.md | Rights/legal/public-use approval remains absent. | True gate; requires explicit human-owned approval. | rights-material-use-clearance | rights_approved remains false until a dedicated acceptance record exists. |
| gap_public_upload_true_gate | true_gate | docs/AUTOMATION_BOUNDARY.md | Publication approval, account/OAuth, and target channel remain absent. | True gate; local automation can only prepare review packets. | PB-decision-packet-before-upload | Upload/public fields stay blocked until human-owned acceptance is recorded. |
| recommend_next_out_slice | recommendation | docs/output_layer/local_fixture_output_proof/proof_manifest.json | A selected-cut-to-proof link is not yet represented as a first-class output route. | Local action; it should still avoid source fetching and public publication. | OUT-03-selected-cut-proof-link | Readback links selected_cut_ids to proof_timeline.html and JSON artifacts. |

## Recommended Next Slice

- slice_id: `OUT-03-selected-cut-proof-link`
- lane: `OUTPUT_VIDEO`
- goal: Link selected cut ids to local proof/readback artifacts so a reviewer can move from an edit decision to the exact proof surface without hunting.
- why_next: OUT-02 proves the portable fixture package shape. The next shortest output-layer unlock is connecting selected cuts to that proof surface while real source, transcript, production render, rights, and upload gates remain separate.
