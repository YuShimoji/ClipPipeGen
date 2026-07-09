# OUT-01 Output Capability Matrix

Readback-only matrix for the output/video layer. This artifact does not fetch media, run render, or claim production readiness.

- artifact_id: `clip-out01-output-layer-gap-logger-v0-001`
- generated_at: `2026-07-08T06:41:49.713798+00:00`
- proof_status: `proof_missing`
- production_ready: `false`
- public_ready: `false`

| capability_id | current_state | evidence_path | missing_input | next_local_action | blocked_by_true_gate | notes |
|---|---|---|---|---|---|---|
| source_material_presence | absent | docs/RUNTIME_STATE.md | Concrete local source_video/source_audio materials and ledger entries for a target episode. | Use a later approved local-material intake/proof slice with operator-supplied files. | false | The current repo state can describe output gaps, but it has no tracked media to prove. |
| transcript_readiness | local_ready | docs/SCHEMAS/v1/transcript.md | A reviewed transcript for the target episode source audio. | Validate or create transcript.json from local audio/fixture, then review it before acceptance. | false | Transcript schema and CLI paths exist; this OUT slice did not ingest media or make a transcript. |
| edit_pack_readiness | local_ready | docs/SCHEMAS/v1/edit_pack.md | An edit_pack connected to the reviewed transcript with selected cuts. | Generate/validate cut candidates and selected_cut_ids after transcript review. | false | Editing artifacts are local diagnostics until human acceptance. |
| subtitle_readiness | local_ready | src/cli/generate_subtitles.py | Subtitle entries linked to selected cuts and reviewed for timing/text. | Generate subtitle drafts from transcript segments, then run review/proof readbacks. | false | Subtitle generation can support local proof; it is not a publication decision. |
| thumbnail_brief_readiness | planned | src/pipeline/episode_init_plan.py | A concrete thumbnail brief artifact and selected source imagery/material refs. | Promote thumbnail brief seed fields into an operator-reviewable output-layer artifact. | false | Planning code references thumbnail intent, but OUT has no current thumbnail proof surface. |
| preview_pack_readiness | local_ready | docs/PREVIEW_PACK.md | A target episode with local media or existing source audio material. | Build a read-only local preview pack once operator-supplied material exists. | false | Preview pack is useful readback, but it is not a rendered video proof. |
| nle_export_readiness | local_ready | docs/SCHEMAS/v1/nle_export.md | A validated edit_pack with selected cuts and optional transcript refs. | Export CSV/JSON/HTML cut-list readback for human review or NLE handoff. | false | NLE export proves edit structure, not final encoded video. |
| local_render_proof_readiness | local_ready | docs/SCHEMAS/v1/tiny_render.md | Source video, source audio, edit_pack, selected cut, and optional subtitle source. | Run a narrow diagnostic proof only after local materials are explicitly available. | false | The code path exists for local diagnostics; OUT-01 created a no-media proof_missing readback instead. |
| public_upload_readiness | gated | docs/AUTOMATION_BOUNDARY.md | Rights acceptance, publication judgment, account/OAuth setup, and public target selection. | Keep public/upload out of local proof work; prepare only decision packets for human review. | true | This is a true gate, not a missing local automation task. |

## Gap Log

| gap_id | status | missing_input | local_vs_true_gate | suggested_next_slice | validation |
|---|---|---|---|---|---|
| gap_source_material_absent | gap | No concrete local source_video/source_audio materials are present for this slice. | Local gap; operator-supplied files can unblock a diagnostic proof without public approval. | OUT-02-local-fixture-output-proof-smoke | A later proof run records source material ids and leaves git ls-files episodes empty. |
| gap_current_no_proof_artifact | proof_missing | No current portable render/proof manifest is available in tracked docs/artifacts. | Local gap; not a rights/publication gate while proof remains diagnostic. | OUT-02-local-fixture-output-proof-smoke | Generated proof manifest remains production_ready=false and public_ready=false. |
| gap_thumbnail_brief_only_planned | gap | A reviewable thumbnail brief/output artifact tied to selected source materials. | Local planning gap; final use still depends on human rights/creative acceptance. | TH-OUT-thumbnail-brief-readback | Brief JSON/HTML names source refs, intended crop/text, and acceptance boundaries. |
| confirm_preview_pack_ready_not_video | confirmation | A concrete local media target is still needed to run it. | Local confirmation; no true gate unless public/production claims are added. | SH-preview-pack-to-output-readback-link | Preview report remains read-only and contains no public upload behavior. |
| confirm_nle_export_ready_not_encoded_output | confirmation | An edit_pack with selected cuts for a real target episode. | Local confirmation; production/public acceptance remains outside the export. | EDIT-to-OUT-selected-cut-proof-link | CSV/HTML readback points to selected cuts and keeps production flags false. |
| gap_public_upload_true_gate | true_gate | Rights decision, publication approval, account/OAuth, and target channel. | True gate; local automation can only prepare review packets. | PB-decision-packet-before-upload | Upload/public fields stay blocked until human-owned acceptance is recorded. |
| recommend_next_out_slice | recommendation | A small approved local fixture/material bundle for a diagnostic proof run. | Local action; it should still avoid source fetching and public publication. | OUT-02-local-fixture-output-proof-smoke | Run targeted CLI/tests and attach generated proof readback to docs or artifacts. |

## Recommended Next Slice

- slice_id: `OUT-02-local-fixture-output-proof-smoke`
- lane: `OUTPUT_VIDEO`
- goal: Run the smallest approved local-material proof using explicit local source video, source audio, edit_pack, and subtitle inputs.
- why_next: It converts the current proof_missing readback into a concrete local render/proof receipt without crossing rights, network, or public gates.
