# Artifact Registry

This registry points to reviewable artifacts without pretending that ignored
local files are portable across clones.

Normal open order is `.\open-dashboard.ps1` first, choose the artifact from the
dashboard, then use an artifact-specific launcher. For the current ED-10z
tiny render-path-nearer probe pack, use `.\open-current-proof.ps1`; if that
ignored local pack is absent, the launcher falls back to the retained ED-10v
focused proof on this machine;
for the accepted ED-10o focused comparison
reference, use
`episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1`;
for the supporting regenerated ED-10l real-font comparison, use
`episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1`;
the reviewed ED-10k BIZ proof is now a reference entry, not the current proof
opened by the root launcher.

## `clip-cpd10-candidate-ledger-readability-v0-001`

| Field | Value |
|---|---|
| title | ClipPipeGen Operator Cockpit / Candidate Ledger Readability v0 |
| purpose | Preserve the accepted CPD-09 Briefing Board while making the lower Candidate Ledger readable for Japanese text-heavy candidate states. |
| storage class | Tracked local planning artifact; portable CPD-01 through CPD-05 consolidation JSON/HTML. Supersedes the CPD-09 ledger table in the same output path. |
| repo_relative_path | `docs/content_planning/operator_cockpit.html` |
| machine_output | `docs/content_planning/operator_cockpit.json` |
| source_inputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/episode_seed_drafts.json`; `docs/content_planning/episode_seed_source_resolution.json`; `docs/content_planning/episode_init_plan.json`; `docs/content_planning/source_inspection_packet.json`; `docs/content_planning/source_inspection_decisions.template.json` |
| open_command | `start docs\content_planning\operator_cockpit.html` |
| generated_from | `build-operator-cockpit` reading local CPD planning artifacts only. |
| validation_command | `uvx python -m src.cli.main build-operator-cockpit --format json` plus `uvx pytest -q tests/test_operator_cockpit.py`. |
| review_status | Ready as the normal human entry point for CPD planning review after the ledger readability repair. The visible Candidate Ledger is stacked/responsive, keeps Japanese titles as full phrase lines, and de-emphasizes machine IDs in a code strip. Source-missing ideas remain not video-backed. |
| next_action | Open the cockpit first, confirm the Candidate Ledger titles read normally, then inspect the single source-backed item through the Primary Review Script or fill source URLs for unresolved ideas before rerunning CPD-03 through CPD-10. |

Boundary flags remain false or pending:

- `source_url_opened_by_worker=false`
- `source_opened_by_worker=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-cpd09-operator-briefing-board-v0-001`

| Field | Value |
|---|---|
| title | ClipPipeGen Operator Cockpit / Briefing Board Usage-Frequency IA v0 |
| purpose | Give humans one dark-mode content-planning briefing board with an annotated flow, one primary source-identity action, and a compact candidate ledger that does not make source-missing ideas look video-backed. |
| storage class | Tracked local planning artifact; portable CPD-01 through CPD-05 consolidation JSON/HTML. Supersedes the CPD-08 Operator Home / Action Queue layout in the same output path. |
| repo_relative_path | `docs/content_planning/operator_cockpit.html` |
| machine_output | `docs/content_planning/operator_cockpit.json` |
| source_inputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/episode_seed_drafts.json`; `docs/content_planning/episode_seed_source_resolution.json`; `docs/content_planning/episode_init_plan.json`; `docs/content_planning/source_inspection_packet.json`; `docs/content_planning/source_inspection_decisions.template.json` |
| open_command | `start docs\content_planning\operator_cockpit.html` |
| generated_from | `build-operator-cockpit` reading local CPD planning artifacts only. |
| validation_command | `uvx python -m src.cli.main build-operator-cockpit --format json` plus `uvx pytest -q tests/test_operator_cockpit.py`. |
| review_status | Ready as the normal human entry point for CPD planning review. Top screen is a Briefing Board with usage-frequency IA, not a card grid, wide status table, or folded archive. Only `cpd01_bancho_marine_misunderstanding` has a known source URL; JP/EN phrase gap and other unresolved ideas are not source-backed video candidates. |
| next_action | Open the cockpit first, read the Briefing Board annotated flow, then inspect the single source-backed item through the Primary Review Script or fill source URLs for unresolved ideas before rerunning CPD-03 and CPD-04. |

Boundary flags remain false or pending:

- `source_url_opened_by_worker=false`
- `source_opened_by_worker=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-cpd01-content-candidate-dashboard-v0-001`

| Field | Value |
|---|---|
| title | CPD-01 Content Candidate / Channel Strategy Dashboard v0 |
| purpose | Make "what should we clip next?" reviewable before source fetch, editing, thumbnail, or publishing lanes. |
| storage class | Tracked local planning artifact; portable fixture-generated JSON/HTML. |
| repo_relative_path | `docs/content_planning/content_dashboard.html` |
| machine_outputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/channel_strategy.json` |
| source_fixture | `samples/content_planning/content_candidates_fixture.json` |
| open_command | `start docs\content_planning\content_dashboard.html` |
| generated_from | `build-content-candidate-dashboard` reading offline fixture/manual seed metadata. |
| validation_command | `uvx python -m src.cli.main build-content-candidate-dashboard --format json` plus `uvx pytest -q tests/test_content_planning.py`. |
| review_status | Ready for operator review as planning readback only. It is not source fetch, production render, creative acceptance, rights approval, publishing acceptance, public use, or monetization approval. |
| next_action | Review the top candidate, then decide whether to create an episode seed or add a public metadata adapter behind an explicit offline-safe flag. |

Boundary flags remain false or pending:

- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `media_downloaded=false`
- `oauth_or_credentials_used=false`

## `clip-cpd02-candidate-to-episode-seed-bridge-v0-001`

| Field | Value |
|---|---|
| title | CPD-02 Candidate-to-Episode Seed Bridge v0 |
| purpose | Convert CPD-01 candidate records into deterministic draft episode seed records before any source fetch, transcript, edit, thumbnail, render, or publishing lane runs. |
| storage class | Tracked local planning artifact; portable candidate-derived JSON/HTML. |
| repo_relative_path | `docs/content_planning/episode_seed_dashboard.html` |
| machine_output | `docs/content_planning/episode_seed_drafts.json` |
| source_candidate_json | `docs/content_planning/content_candidates.json` |
| open_command | `start docs\content_planning\episode_seed_dashboard.html` |
| generated_from | `build-episode-seed-drafts` reading CPD-01 candidate JSON. |
| validation_command | `uvx python -m src.cli.main build-episode-seed-drafts --format json` plus `uvx pytest -q tests/test_episode_seed_bridge.py`. |
| review_status | Ready for operator review as draft planning readback only. No episode folders, media, transcripts, edit packs, renders, thumbnails, uploads, rights approval, production acceptance, or public-use permission are created. |
| next_action | Inspect the top seed and decide whether a later slice should resolve source metadata, initialize a real episode skeleton, or hold/reject the seed. |

Boundary flags remain false or pending:

- `status=draft`
- `source_media_state=not_fetched`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `oauth_or_credentials_used=false`

## `clip-cpd03-source-metadata-resolver-v0-001`

| Field | Value |
|---|---|
| title | CPD-03 Source Metadata Resolver / Manual Source Intake v0 |
| purpose | Resolve CPD-02 draft seed source URL state before any source fetch, transcript, episode initialization, thumbnail, render, or publishing lane runs. |
| storage class | Tracked local planning artifact; portable seed-derived JSON/HTML plus blank manual registry template. |
| repo_relative_path | `docs/content_planning/source_resolution_dashboard.html` |
| machine_output | `docs/content_planning/episode_seed_source_resolution.json` |
| manual_registry_template | `docs/content_planning/source_metadata_registry.template.json` |
| source_seed_json | `docs/content_planning/episode_seed_drafts.json` |
| open_command | `start docs\content_planning\source_resolution_dashboard.html` |
| generated_from | `resolve-episode-seed-sources` reading CPD-02 episode seed draft JSON and an optional local manual registry. |
| validation_command | `uvx python -m src.cli.main resolve-episode-seed-sources --format json` plus `uvx pytest -q tests/test_source_metadata_resolver.py`. |
| review_status | Ready for operator review as source-resolution readback only. No media fetch, public API/OAuth lookup, episode folder, transcript, edit pack, render, thumbnail, rights approval, production acceptance, or public-use permission is created. |
| next_action | Fill real source URLs for unresolved seed records in a local manual registry, rerun CPD-03, then decide whether a later dry-run should initialize an episode skeleton for a resolved seed. |

Boundary flags remain false or pending:

- `source_media_state=not_fetched`
- `network_required=false`
- `external_api_used=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `oauth_or_credentials_used=false`
- `rights_approved=false`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-cpd04-init-episode-dry-run-plan-v0-001`

| Field | Value |
|---|---|
| title | CPD-04 Init Episode Dry-Run Plan v0 |
| purpose | Convert CPD-03 source-resolved records into reviewable episode initialization plans without creating real episode folders or downstream production artifacts. |
| storage class | Tracked local planning artifact; portable source-resolution-derived JSON/HTML. |
| repo_relative_path | `docs/content_planning/episode_init_plan_dashboard.html` |
| machine_output | `docs/content_planning/episode_init_plan.json` |
| source_resolution_json | `docs/content_planning/episode_seed_source_resolution.json` |
| seed_enrichment_json | `docs/content_planning/episode_seed_drafts.json` |
| open_command | `start docs\content_planning\episode_init_plan_dashboard.html` |
| generated_from | `build-episode-init-plan` reading CPD-03 source resolution JSON and optional CPD-02 seed draft enrichment. |
| validation_command | `uvx python -m src.cli.main build-episode-init-plan --format json` plus `uvx pytest -q tests/test_episode_init_plan.py`. |
| review_status | Ready for operator review as dry-run initialization readback only. No episode folder, rights manifest, material ledger, fetch receipt, source media, transcript, edit pack, thumbnail, render, upload, rights approval, production acceptance, or public-use permission is created. |
| next_action | Review the single ready dry-run plan and decide whether a later slice should run real source inspection / `init-episode`, while unresolved records stay behind manual source intake. |

Boundary flags remain false or pending:

- `dry_run=true`
- `source_media_state=not_fetched`
- `transcript_state=not_generated`
- `material_ledger_state=planned_only`
- `edit_pack_state=planned_only`
- `thumbnail_state=planned_only`
- `network_required=false`
- `external_api_used=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_manifest_created=false`
- `material_ledger_created=false`
- `fetch_receipt_created=false`
- `oauth_or_credentials_used=false`
- `rights_approved=false`
- `production_ready=false`
- `publishing_acceptance=false`
- `public_ready=false`

## `clip-cpd05-source-inspection-packet-v0-001`

| Field | Value |
|---|---|
| title | CPD-05 Source Inspection Packet / Decision Registry v0 |
| purpose | Convert ready CPD-04 dry-run episode init plans into operator source inspection packets and a blank decision registry template before any future gated source action. |
| storage class | Tracked local planning artifact; portable episode-init-plan-derived JSON/HTML/template. |
| repo_relative_path | `docs/content_planning/source_inspection_packet_dashboard.html` |
| machine_output | `docs/content_planning/source_inspection_packet.json` |
| decision_template | `docs/content_planning/source_inspection_decisions.template.json` |
| source_episode_init_plan | `docs/content_planning/episode_init_plan.json` |
| open_command | `start docs\content_planning\source_inspection_packet_dashboard.html` |
| generated_from | `build-source-inspection-packet` reading CPD-04 episode init plan JSON. |
| validation_command | `uvx python -m src.cli.main build-source-inspection-packet --format json` plus `uvx pytest -q tests/test_source_inspection_packet.py`. |
| review_status | Ready for operator source identity review as an inspection packet only. The worker did not open the source URL, authorize future private/local fetch, create episode folders, generate episode artifacts, approve rights, or mark anything production/public ready. |
| next_action | Open the dashboard, inspect the single ready source URL manually, then fill `source_inspection_decisions.template.json` only if a later gated slice should proceed. |

Boundary flags remain false or pending:

- `dry_run=true`
- `source_opened_by_worker=false`
- `source_media_state=not_fetched`
- `fetch_authorized=false`
- `network_required=false`
- `external_api_used=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_manifest_created=false`
- `material_ledger_created=false`
- `fetch_receipt_created=false`
- `transcript_generated=false`
- `edit_pack_created=false`
- `oauth_or_credentials_used=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-review-acceptance-gate-001`

| Field | Value |
|---|---|
| title | ED-10f Representative Subtitle Design Review Gate |
| purpose | Track the representative subtitle design review gate that consumed the SH-08 human response as `adjust_boundary` and sent font-family / decoration to ED-10g. |
| storage class | Tracked decision/readback artifact; references local proof evidence but is portable as docs. |
| repo_relative_path | `docs/REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md` |
| related_local_artifact | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/index.html` |
| generated_from | Parser-first readback plus human response consumption recorded in tracked docs. |
| validation_command | `uvx pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py` |
| latest_validation_result | `18 passed, 8 skipped` on the 2026-06-16 targeted local validation path before the v1.5 dashboard slice. |
| review_status | Human response consumed as `adjust_boundary`; ED-10f is diagnostic / representative only and has successor work in ED-10g / ED-10h. |
| next_action | Use ED-10g Noto overlay proof for current visual judgement; use ED-10h registry only if the font universe must widen after that judgement. |

## `clip-human-preview-session-001`

| Field | Value |
|---|---|
| title | SH-08 Human Preview Session Bundle |
| purpose | Single local entry point for diagnostic / representative review of the current `cut_002` / `cut_003` subtitle overlay evidence. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/index.html` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session\open_preview.ps1` |
| fallback_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session\serve_preview.ps1 -Port 8000` |
| generated_from | `build-human-preview-session` / `build-episode-review-bundle` reading existing ignored episode and review artifacts. |
| validation_command | `uvx pytest -q tests/test_episode_review_bundle.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_status.py` |
| latest_validation_result | `18 passed, 8 skipped` on the 2026-06-16 targeted local validation path. |
| latest_local_smoke | Same-machine parser readback confirmed `review_ready=true`, `state=diagnostic_only`, `target_cuts=[cut_002, cut_003]`, `missing_artifacts=[]`, `<video controls>`, and `cut_002` / `cut_003` MP4 assets. Localhost preview smoke succeeded in the retained workspace. |
| review_status | Human response consumed as `adjust_boundary`; ED-10g successor response `small_adjustment` is now recorded separately. Diagnostic / representative only. |
| next_action | Follow the ED-10g small-adjustment route; do not regenerate SH-08 unless the active preview session itself must be inspected again. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked builder, docs, and tests. It cannot directly
verify the ignored local MP4/PNG assets themselves, so local artifact existence
must be verified with the open command or manifest readback on the retaining
machine. `git ls-files episodes` should remain empty.

## `clip-typography-decoration-comparison-001`

| Field | Value |
|---|---|
| title | ED-10g Subtitle Typography Decoration Comparison v0 |
| purpose | Compare font-family and decorative treatment candidates while preserving the accepted diagnostic font-size direction for `cut_002` / `cut_003`. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison/subtitle_typography_decoration_comparison_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison/subtitle_typography_decoration_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_typography_decoration_comparison\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text, plus tracked ED-10g response readback for `small_adjustment`. |
| validation_command | `uvx --with pillow pytest -q tests/test_subtitle_style_spike.py` plus normal project validation. |
| latest_validation_result | `7 passed` for the Pillow-enabled style-spike path; normal no-Pillow path can skip PNG generation tests. |
| latest_local_smoke | Same-machine refresh on 2026-06-16 JST produced 4 candidates, 16 PNG samples, JSON/HTML report, contact sheet, and `open_comparison.ps1`; `comparison_response_readback.selected_response=small_adjustment`, `selected_candidate_for_next_proof_base=noto_sans_jp_clean_outline`, `next_diagnostic_overlay_proof_route.route_kind=small_adjustment_diagnostic_overlay_proof`, `small_adjustment_decision_packet.decision_state=selected_for_next_diagnostic_overlay_proof_base`, `font_size_policy.value=124`, `production_subtitle_design_acceptance=false`, `rights_status=pending`. The persisted JSON is ASCII-escaped and parsed successfully with Windows PowerShell `ConvertFrom-Json`; the contact sheet was inspected as a nonblank local visual artifact. Other worktrees may lack this ignored artifact and must treat absence as local evidence absence, not a tracked Git failure. |
| review_status | Human response consumed as `small_adjustment`; diagnostic / representative only. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Treat this as historical ED-10g comparison context. Use `clip-ed10i-kirinuki-gothic-balance-001` for the current body/outline balance decision. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, and tests. It cannot
directly verify the ignored PNG/HTML comparison artifacts themselves, so local
artifact existence must be verified with the open command or JSON report
readback on the retaining machine. `git ls-files episodes` should remain empty.

## `clip-ed10i-kirinuki-gothic-balance-001`

| Field | Value |
|---|---|
| title | ED-10i Kirinuki Gothic Weight Balance Comparison v0 |
| purpose | Consume the latest human review that the current Noto clean-outline proof is not accepted as-is, then compare a narrow gothic/sans set by glyph body weight, outline thickness, and fill/outline balance. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_gothic_balance_comparison/subtitle_kirinuki_gothic_balance_comparison_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_gothic_balance_comparison/subtitle_kirinuki_gothic_balance_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10i_kirinuki_gothic_balance` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10i human review readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10i_kirinuki_gothic_balance --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10i generation returned `artifact_id=clip-ed10i-kirinuki-gothic-balance-001`, `candidate_count=4`, `sample_count=16`, `font_size.value=124`, `recommended_default_candidate_id=ed10i_biz_udgothic_bold_balanced_outline`, `production_candidate=false`, and `rights_status=pending`; JSON parsed successfully and the contact sheet was inspected as nonblank local visual evidence. |
| review_status | Human review consumed: the bottom-most gothic candidate was selected as closest to ideal and resolved from local JSON as `ed10i_meiryo_bold_fill_outline_balance`. This comparison remains the audit trail for that choice. |
| next_action | Use `clip-ed10i-meiryo-overlay-proof-001` for the current visual judgement. Reopen this comparison only if the candidate mapping or a bounded body/outline adjustment needs audit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests. It cannot directly verify the ignored PNG/HTML comparison artifacts
themselves, so local artifact existence must be verified with the open command
or JSON report readback on the retaining machine. `git ls-files episodes`
should remain empty.

## `clip-ed10i-meiryo-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10i Meiryo Selected Diagnostic Overlay Proof |
| purpose | Apply the human-selected bottom ED-10i candidate, `ed10i_meiryo_bold_fill_outline_balance`, to the `cut_002` / `cut_003` diagnostic subtitle overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id ed10i_meiryo_bold_fill_outline_balance` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10i_meiryo_bold_fill_outline_balance --format json` plus targeted tests. |
| latest_validation_result | Same-machine generation returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10i_meiryo_bold_fill_outline_balance`, `typography_decoration_candidate_id=ed10i_meiryo_bold_fill_outline_balance`, `subtitle_overlay_available_count=2`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`; JSON parsed successfully. |
| latest_local_smoke | Same-machine readback resolved `font_family_route.requested=Meiryo`, `font_family_route.font_file_status=candidate_primary_font_file_found`, `font_size=124`, `outline=9`, `bbox_wrapping_applied=true`, and target MP4/PNG artifacts for `cut_002` and `cut_003`. The generated PNG frames were inspected as nonblank 1920x1080 local visual artifacts. |
| human_visual_judgement | Freeform review consumed: the proof looks too thin and is not attractive enough as the normal subtitle baseline; the issue may be baseline font choice, not only outline tuning. |
| review_status | Reviewed and not accepted as the normal subtitle baseline. Meiryo is now an audited reference candidate only. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Use `clip-ed10j-kirinuki-font-audit-001` to review stronger normal-dialogue font candidates before generating another narrow overlay proof. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored MP4/PNG/ASS files themselves. Other worktrees should
treat missing `episodes/` proof assets as local evidence absence, not as a
tracked Git failure.

## `clip-ed10j-kirinuki-font-audit-001`

| Field | Value |
|---|---|
| title | ED-10j Kirinuki Subtitle Font Research & Candidate Audit v0 |
| purpose | Consume the reviewed Meiryo overlay proof as not accepted for the normal subtitle baseline, then compare a no-download normal-dialogue gothic/sans shortlist before another overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_font_audit/subtitle_kirinuki_font_audit_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_font_audit/subtitle_kirinuki_font_audit_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10j_kirinuki_font_audit` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10j freeform review readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10j_kirinuki_font_audit --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10j regeneration returned `artifact_id=clip-ed10j-kirinuki-font-audit-001`, `candidate_count=4`, `sample_count=16`, `font_size.value=124`, `selected_candidate_for_next_proof_base=ed10j_biz_udgothic_bold_telop_candidate`, `blue_badge_candidate_id=ed10j_noto_sans_jp_local_telop_candidate`, `blue_badge_is_meiryo_reference=false`, `production_candidate=false`, and `rights_status=pending`; JSON parsed successfully and the contact sheet was inspected as nonblank local visual evidence. |
| review_status | Freeform review consumed: Meiryo is removed from normal baseline candidates, the remaining non-Meiryo candidates are close enough to avoid prolonging the audit, and BIZ UDGothic is selected as the default next proof base. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Treat this as consumed audit trail. ED-10k already tested BIZ, and ED-10l is the current known-font route correction. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests. It cannot directly verify the ignored PNG/HTML comparison artifacts
themselves, so local artifact existence must be verified with the open command
or JSON report readback on the retaining machine. `git ls-files episodes`
should remain empty.

## `clip-ed10k-biz-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10k BIZ UDGothic Diagnostic Overlay Proof |
| purpose | Apply the ED-10j selected default `ed10j_biz_udgothic_bold_telop_candidate` to the `cut_002` / `cut_003` diagnostic subtitle overlay proof after Meiryo was removed from normal subtitle candidates. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id ed10j_biz_udgothic_bold_telop_candidate` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10j_biz_udgothic_bold_telop_candidate --format json` plus targeted tests. |
| latest_validation_result | Same-machine generation returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10j_biz_udgothic_bold_telop_candidate`, `typography_decoration_candidate_id=ed10j_biz_udgothic_bold_telop_candidate`, `subtitle_overlay_available_count=2`, `all_target_cuts_have_overlay=true`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`; JSON parsed successfully. |
| latest_local_smoke | Same-machine readback resolved `font_family_route.requested=BIZ UDGothic`, `font_family_route.font_file_status=candidate_primary_font_file_found`, `font_size=124`, `outline=8`, `ed10j_kirinuki_font_audit_candidate=true`, `explicit_line_breaks_passed_to_ass=true`, `one_character_orphan_present=false`, and `suspicious_tail_line_present=false`. The `cut_002` and `cut_003` PNG frames were inspected as nonblank 1920x1080 local visual artifacts. |
| review_status | Freeform review consumed: BIZ UDGothic is not accepted as the normal subtitle baseline because it reads too hard/rigid, the text remains thin, and the black outline pressure is too strong. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Keep this as reviewed rejected reference evidence. Use `clip-ed10l-known-kirinuki-font-pack-001` for the current normal-dialogue font route decision. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked code, docs, dashboard metadata, and tests but
not the ignored MP4/PNG/ASS files themselves. Other worktrees should treat
missing `episodes/` proof assets as local evidence absence, not as a tracked
Git failure.

## `clip-ed10l-known-kirinuki-font-pack-001`

| Field | Value |
|---|---|
| title | ED-10l Known Kirinuki Font Pack Audit v0 |
| purpose | Consume the reviewed ED-10k BIZ proof as not accepted, then audit known Japanese YouTube kirinuki/telop font candidates for the normal-dialogue baseline before another overlay proof is selected. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_known_kirinuki_font_pack_comparison/subtitle_known_kirinuki_font_pack_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_known_kirinuki_font_pack_comparison/subtitle_known_kirinuki_font_pack_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10l_known_kirinuki_font_pack` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10l route-correction readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10l_known_kirinuki_font_pack --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10n regeneration returned `artifact_id=clip-ed10l-known-kirinuki-font-pack-001`, `comparison_profile=ed10l_known_kirinuki_font_pack`, `sample_count=16`, `candidate_count=4`, `font_size.value=124`, `selected_candidate_for_next_proof_base=ed10l_keifont_pop_dialogue_candidate`, `comparison_response_readback.selected_response=per_user_font_readback_valid_route_to_keifont_overlay_proof`, `font_visual_comparison_validity=valid_requested_font_visual_evidence`, `all_candidates_valid_real_font=true`, `production_candidate=false`, and `rights_status=pending`; JSON parsed successfully. |
| review_status | Regenerated as valid requested-font comparison/readback evidence after HKCU/per-user font resolver support. It supports ED-10n proof routing but is not itself production subtitle design acceptance. |
| next_action | Use `clip-ed10n-keifont-overlay-proof-001` for current human visual judgement. Return to this comparison only if Keifont is rejected and another ED-10l candidate should be promoted. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests. It cannot directly verify the ignored PNG/HTML comparison artifacts
themselves, so local artifact existence must be verified with the open command
or JSON report readback on the retaining machine. `git ls-files episodes`
should remain empty.

## `clip-ed10n-keifont-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10n Keifont Real-Font Diagnostic Overlay Proof |
| purpose | Apply the per-user resolved `ed10l_keifont_pop_dialogue_candidate` to the `cut_002` / `cut_003` diagnostic subtitle overlay proof after ED-10l real-font readback became valid. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --format json` plus targeted tests. |
| latest_validation_result | Same-machine generation returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `typography_decoration_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `subtitle_overlay_available_count=2`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`; JSON parsed successfully. |
| latest_local_smoke | Same-machine readback resolved `font_family_route.requested=Keifont`, `font_family_route.resolved=Keifont`, `font_family_route.resolved_font_file=C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\keifont.ttf`, `font_file_status=candidate_primary_font_file_found`, and target MP4/PNG artifacts for `cut_002` and `cut_003`. |
| review_status | Available and requires human visual review. It is not production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Review the visible Keifont proof and answer whether it should proceed, get one bounded adjustment, or be replaced by another ED-10l candidate. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored MP4/PNG/ASS files themselves. Other worktrees should
treat missing `episodes/` proof assets as local evidence absence, not as a
tracked Git failure. `git ls-files episodes` should remain empty.

## `clip-ed10o-multifont-focused-review-001`

| Field | Value |
|---|---|
| title | ED-10o Multi-font Focused Review Surface |
| purpose | Consume the latest Keifont review as improved and usable enough for serious review, then move the bottleneck to a compact one-shot comparison of Keifont, 851 Chikara Yowaku, and Yasashisa Gothic on the same subtitle lines. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_multifont_focused_review/subtitle_multifont_focused_review_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_multifont_focused_review/subtitle_multifont_focused_review_matrix.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10o_multifont_focused_review` reading the existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10n review readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10o_multifont_focused_review --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10o generation returned `artifact_id=clip-ed10o-multifont-focused-review-001`, `comparison_profile=ed10o_multifont_focused_review`, `sample_count=12`, `candidate_count=3`, `focused_review_surface.status=focused_review_surface_generated`, `focused_review_surface.primary_visual=subtitle_area_crop_matrix`, `selected_candidate_for_next_proof_base=ed10l_keifont_pop_dialogue_candidate`, `font_visual_comparison_validity=valid_requested_font_visual_evidence`, `all_candidates_valid_real_font=true`, `excluded_candidates[0].candidate_id=ed10l_m_plus_fonts_dialogue_candidate`, `production_candidate=false`, and `rights_status=pending`; JSON and HTML parsed successfully and the focused matrix PNG was inspected as a nonblank local visual artifact. |
| review_status | Human review consumed as focused review surface accepted/easier to see. Keifont remains the lead entering ED-10p, with 851 Chikara Yowaku and Yasashisa Gothic preserved as alternates. This is not final baseline or production subtitle design acceptance. |
| next_action | Use as the accepted review UX direction and historical comparison reference while reviewing `clip-ed10r-keifont-dense-stress-proof-001`. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

M+ is intentionally excluded from this one-shot comparison because current
readback resolves to `M PLUS 1 Thin` via `MPLUS1-VariableFont_wght.ttf`; it
should be reintroduced only after an exact non-thin weight/style route is
pinned. Remote Git can verify the tracked generator, docs, dashboard metadata,
and tests but not the ignored PNG/HTML artifacts themselves. Other worktrees
should treat missing `episodes/` review assets as local evidence absence, not
as a tracked Git failure. `git ls-files episodes` should remain empty.

## `clip-ed10p-keifont-lead-representative-proof-001`

| Field | Value |
|---|---|
| title | ED-10p Keifont Lead Representative Proof |
| purpose | Consume the ED-10o review that the font comparison and review screen are easier to see, keep Keifont as diagnostic representative normal-dialogue provisional baseline evidence, and preserve the `cut_002` / `cut_003` proof history without reopening general acceptance. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/current_proof_focused_review.html` |
| detailed_overlay_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| representative_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html` |
| open_command | `.\open-current-proof.ps1` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10p_keifont_lead_representative_proof --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_002 --target-cut cut_003` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10p_keifont_lead_representative_proof --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10q regeneration returned `artifact_id=clip-ed10p-keifont-lead-representative-proof-001`, `proof_profile=ed10p_keifont_lead_representative_proof`, `source_review_artifact_id=clip-ed10o-multifont-focused-review-001`, `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `typography_decoration_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `subtitle_overlay_available_count=2`, `focused_review_html=episodes/.../current_proof_focused_review.html`, `focused_proof_review.status=representative_keifont_lead_proof_ready`, `review_debt[0].debt_id=cut_008_dense_stress_proof`, `production_candidate=false`, and `rights_status=pending`; focused HTML readback confirmed Review Focus before subtitle-area evidence and Detailed Reports, ED-10o reference link present, cut_002/cut_003 evidence present, cut_008 debt present, and old debug cut table absent from the focused page. |
| review_status | Consumed as provisional normal-dialogue baseline evidence. ED-10q restored the focused page after the old-layout regression, but ED-10q was not font-quality review. Do not request another general Keifont acceptance pass on `cut_002` / `cut_003`. Final baseline, production render, creative, rights, publishing, and public-use gates remain closed. |
| next_action | Use `clip-ed10r-keifont-dense-stress-proof-001` for the active review. Keep this artifact as history and baseline evidence only. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

`cut_008` Review Debt has moved to ED-10r as the current narrow dense/stress
proof. Remote Git can verify the tracked builder, docs, dashboard metadata,
and tests but not the ignored MP4/PNG/ASS artifacts themselves. Other worktrees
should treat missing `episodes/` proof assets as local evidence absence, not
as a tracked Git failure. `git ls-files episodes` should remain empty.

## `clip-ed10af-render-contract-consumer-dry-read-001`

| Field | Value |
|---|---|
| title | ED-10af Render Contract Consumer Dry-Read |
| purpose | Preserve the L0 static consumer payload evidence that was originally added in commit `7e96a28`, before the active L2 probe existed. |
| storage class | Tracked JSON/Markdown predecessor readback; no local media output. |
| repo_relative_path | `docs/style_intent/subtitle-render-contract-consumer-dry-read.md` |
| metadata_json | `docs/style_intent/subtitle-render-contract-consumer-dry-read.json` |
| open_command | `see docs\style_intent\subtitle-render-contract-consumer-dry-read.md` |
| predecessor_commit | `7e96a28 Add ED-10af render contract consumer dry read` |
| successor_artifact | `clip-ed10af-l2-render-path-selector-probe-001` |
| source_render_path_selector_contract_artifact | `clip-ed10ae-render-path-selector-contract-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` dry-read builder plus restored tracked readback files. |
| generated_from | ED-10af dry-read commit `7e96a28`; restored as predecessor evidence after the L2 probe replaced the active surface. |
| validation_command | Parse dry-read JSON, ED-10ag L2 readback JSON, ED-10af probe JSON, and dashboard JSON; run targeted subtitle/dashboard/review tests; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Restored JSON reports six static consumer payloads, `render_level=L0 No Render`, `consumer_dry_read_only=true`, no render boundary leakage, no production/public boundary leakage, and `all_payloads_consumer_ready=true`. |
| review_status | Superseded by the L2 selector probe, but not invalidated. Keep as predecessor source evidence for the full six-example contract consumer payload. |
| next_action | Use only as static predecessor evidence. The active artifact remains `clip-ed10af-l2-render-path-selector-probe-001`. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10af-l2-render-path-selector-probe-001`

| Field | Value |
|---|---|
| title | ED-10af L2 Render Path Selector Probe |
| purpose | Consume the ED-10ae render-path selector contract into a tiny FFmpeg/libass diagnostic path for normal dialogue, shout, and whisper semantic examples. |
| storage class | Tracked JSON/Markdown readback plus ignored same-machine ASS/MP4/manifest evidence. |
| repo_relative_path | `docs/style_intent/subtitle-render-path-selector-probe.md` |
| metadata_json | `docs/style_intent/subtitle-render-path-selector-probe.json` |
| open_command | `see docs\style_intent\subtitle-render-path-selector-probe.md` |
| local_ignored_ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| local_ignored_video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| local_ignored_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| | predecessor_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_render_path_selector_contract_artifact | `clip-ed10ae-render-path-selector-contract-probe-001` |
| source_style_family_palette_artifact | `clip-ed10ad-style-family-palette-axis-proof-001` |
| source_visual_selector_artifact | `clip-ed10ac-visual-selector-proof-001` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10af L2 selector probe using ED-10ae contract entries and existing ignored local source media. |
| validation_command | Parse ED-10af probe JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Local ignored FFmpeg/libass probe generated ASS/MP4/manifest; metadata readback reports 1920x1080, 4.2s, h264/aac. Tracked JSON reports 3 examples, stable body text, badge/accent/backplate route, safe-area/line-break metadata, and closed production/public boundaries. |
| review_status | No Review Card and no user-side judgement requested. This is diagnostic render-path readback only. |
| next_action | Use this L2 selector probe readback before opening a separate production limitation-lift, final render-path, rights, publishing, or public-use route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10ag-lineage-and-observation-surface-001`

| Field | Value |
|---|---|
| title | ED-10ag Lineage and Observation Surface |
| purpose | Record that the restored ED-10af dry-read remains predecessor evidence while the active ED-10af L2 selector probe supplies bounded render-path proof. |
| storage class | Tracked JSON/Markdown lineage and observation surface; references ignored same-machine ASS/MP4/manifest/contact-sheet evidence only. |
| repo_relative_path | `docs/style_intent/subtitle-render-path-lineage-observation-surface.md` |
| metadata_json | `docs/style_intent/subtitle-render-path-lineage-observation-surface.json` |
| open_command | `see docs\style_intent\subtitle-render-path-lineage-observation-surface.md` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_dry_read_commit | `7e96a28` |
| source_l2_selector_probe_artifact | `clip-ed10af-l2-render-path-selector-probe-001` |
| source_render_path_selector_contract_artifact | `clip-ed10ae-render-path-selector-contract-probe-001` |
| local_ignored_ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| local_ignored_video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| local_ignored_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| local_ignored_contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |
| generated_from | ED-10ag Existing Output First lineage surface using the restored ED-10af dry-read and the existing active ED-10af L2 selector probe; no new render was run. |
| validation_command | Parse ED-10ag lineage JSON, ED-10af probe JSON, restored dry-read JSON, and dashboard JSON; run targeted subtitle/dashboard/review tests; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | ED-10ag JSON reports `existing_output_first_reused=true`, `new_render_run=false`, `source_probe_new_render_run=true`, `dry_read_all_payloads_consumer_ready=true`, `stable_body_text_preserved=true`, `production_public_boundary_closed=true`, and `episodes_tracked=false`. |
| review_status | No Review Card and no required user-side observation. The artifact is bounded lineage/observation technical readback, not new subtitle design or render acceptance. |
| next_action | Use this surface to inspect the predecessor/current artifact relationship and local ignored proof paths before opening any production limitation-lift, final render-path, rights, publishing, or public-use route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10ah-production-limitation-lift-entry-001`

| Field | Value |
|---|---|
| title | ED-10ah Production Limitation-Lift Entry |
| purpose | Separate diagnostic render-path proof from production subtitle design acceptance, production render acceptance, creative acceptance, rights status, publishing acceptance, and public-use permission. |
| storage class | Tracked JSON/Markdown gate-separation artifact; references ignored same-machine proof media only. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-entry.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-entry.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-entry.md` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_dry_read_commit | `7e96a28` |
| local_ignored_ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| local_ignored_video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| local_ignored_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| local_ignored_contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |
| generated_from | ED-10ah consumes the user observation that the opened surface is acceptable enough and forward progress is preferred; it preserves ED-10af as active diagnostic proof and ED-10ag as lineage support. |
| validation_command | Parse ED-10ah, ED-10ag, ED-10af probe, restored dry-read JSON, and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | ED-10ah JSON reports all seven gate names present, `active_diagnostic_source_preserved=true`, `lineage_support_not_production_proof=true`, `dry_read_predecessor_preserved=true`, `production_public_boundary_closed=true`, `new_render_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card. Display/layout polish is deferred by user observation; the artifact is a gate entry, not production/public approval. |
| next_action | Start `production-limitation-lift-stage-1` or `final-render-path-readiness` from this gate matrix while keeping production subtitle design, production render, creative, rights, publishing, and public-use decisions explicit. |

Boundary flags remain false or pending:

- `diagnostic_render_path_proof=available_diagnostic_only`
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10ah-render-readiness-separation-readback-001`

| Field | Value |
|---|---|
| title | ED-10ah Render Readiness Separation Readback |
| type | Tracked JSON/Markdown bounded readiness readback |
| status | `render_readiness_separation_readback_ready` |
| storage class | Tracked JSON/Markdown only; references ignored same-machine diagnostic render evidence but creates no media. |
| repo_relative_path | `docs/style_intent/subtitle-render-readiness-separation.md` |
| metadata_json | `docs/style_intent/subtitle-render-readiness-separation.json` |
| open_command | `see docs\style_intent\subtitle-render-readiness-separation.md` |
| source_l2_selector_probe | `clip-ed10af-l2-render-path-selector-probe-001` |
| source_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_limitation_lift_entry | `clip-ed10ah-production-limitation-lift-entry-001` |
| render_gate | L1/L2 Existing Output Observation / reused diagnostic readback; new render false. |
| generated_from | ED-10ah render-readiness cleanup using existing ED-10af/ED-10ag/ED-10ah tracked readbacks only. |
| validation_command | Parse ED-10ah readiness separation JSON plus related style proof / dry-read / render probe / dashboard files; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records proven scope, not-proven scope, render gate, later explicit render trigger, closed production boundary, closed rights/public-use boundary, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This is not production subtitle design, production render, creative, rights, publishing, public-use, or final subtitle style acceptance. |
| next_action | Use this readback to start a later explicit `final-render-path-readiness` or `production-limitation-lift-stage-1` milestone without inferring production/public approval. |

## `clip-ed10ai-final-render-path-readiness-packet-001`

| Field | Value |
|---|---|
| title | ED-10ai Final Render-Path Readiness Packet |
| purpose | Classify what is ready for a later final render-path route and what remains missing before production/public use can be considered. |
| storage class | Tracked JSON/Markdown readiness packet; references ignored same-machine diagnostic media only. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-readiness.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-readiness.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-readiness.md` |
| source_gate_entry | `clip-ed10ah-production-limitation-lift-entry-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_selector_contract | `clip-ed10ab-subtitle-preset-selector-001` |
| source_render_adapter_input_contract | `clip-ed10ae-render-path-selector-contract-probe-001` |
| generated_from | ED-10ai uses ED-10ah gate separation plus ED-10af/ED-10ag diagnostic evidence to prepare `final-render-path-stage-1` without running a render or approving production/public use. |
| validation_command | Parse ED-10ai readiness JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records all required readiness rows, ED-10af active diagnostic source, ED-10ah gate source, ED-10ag lineage, `7e96a28` dry-read predecessor, selector/render-contract evidence, closed production/public boundaries, `new_render_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This packet is preparation only, not production subtitle design, production render, creative, rights, publishing, or public-use approval. |
| next_action | Start `final-render-path-stage-1` or `production-limitation-lift-stage-1` from this readiness matrix while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10aj-final-render-path-stage-1-001`

| Field | Value |
|---|---|
| title | ED-10aj Final Render-Path Stage 1 |
| purpose | Select the stage-1 final render-path candidate from existing diagnostic evidence without approving production render or public use. |
| storage class | Tracked JSON/Markdown stage-1 packet; references ignored same-machine diagnostic media only. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-stage-1.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-stage-1.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-stage-1.md` |
| source_readiness_packet | `clip-ed10ai-final-render-path-readiness-packet-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_gate_entry | `clip-ed10ah-production-limitation-lift-entry-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| selected_path | FFmpeg/libass diagnostic subtitle overlay path, selected for stage-1 preparation only. |
| generated_from | ED-10aj uses ED-10ai readiness plus ED-10af/ED-10ag diagnostic evidence to define `final-render-path-stage-1` without running a render or approving production/public use. |
| validation_command | Parse ED-10aj stage-1 JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records all required stage-1 checklist rows, ED-10ai readiness source, ED-10af active diagnostic source, FFmpeg/libass candidate path, closed production/public boundaries, `new_render_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This packet is preparation only, not production subtitle design, production render, creative, rights, publishing, or public-use approval. |
| next_action | Start `final-render-path-stage-2` or `production-limitation-lift-stage-1` from this selected path while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `final_render_path_approved=false`

## `clip-ed10ak-final-render-path-stage-2-replayability-001`

| Field | Value |
|---|---|
| title | ED-10ak Final Render-Path Stage 2 Replayability |
| purpose | Record how a later agent/operator can inspect or replay the selected FFmpeg/libass diagnostic subtitle overlay path without approving production render or public use. |
| storage class | Tracked JSON/Markdown operation packet; references ignored same-machine diagnostic media only. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-stage-2.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-stage-2.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-stage-2.md` |
| source_stage_1_packet | `clip-ed10aj-final-render-path-stage-1-001` |
| source_readiness_packet | `clip-ed10ai-final-render-path-readiness-packet-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| selected_path | FFmpeg/libass diagnostic subtitle overlay path. |
| operation_matrix | Tracks selected path, tracked inputs, same-machine source inputs, ignored outputs, expected output types, command family, validation/readback commands, fresh-clone absence behavior, diagnostic-only scope, and missing production render approvals. |
| generated_from | ED-10ak uses ED-10aj stage-1 plus ED-10af/ED-10ag diagnostic evidence to define replayability/operation handoff without running a render/replay or approving production/public use. |
| validation_command | Parse ED-10ak stage-2 JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records all required operation rows, ED-10aj stage-1 source, ED-10af active diagnostic source, FFmpeg/libass command family, fresh-clone absence behavior, closed production/public boundaries, `new_render_run=false`, `new_replay_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This packet is replayability/readback only, not production subtitle design, production render, creative, rights, publishing, or public-use approval. |
| next_action | Start `final-render-path-stage-3` or `production-limitation-lift-stage-1` from this operation packet while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_replay_run=false`
- `final_render_path_approved=false`

## `clip-ed10al-final-render-path-stage-3-rehearsal-001`

| Field | Value |
|---|---|
| title | ED-10al Final Render-Path Stage 3 Diagnostic Rehearsal |
| purpose | Rehearse the selected FFmpeg/libass diagnostic subtitle overlay path from the ED-10ak replayability packet, record same-machine generated ignored outputs and metadata, and keep production/public gates closed. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-stage-3.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-stage-3.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-stage-3.md` |
| source_stage_2_packet | `clip-ed10ak-final-render-path-stage-2-replayability-001` |
| source_stage_1_packet | `clip-ed10aj-final-render-path-stage-1-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| generated_ignored_outputs | `subtitle_render_path_selector_probe.ass`, `subtitle_render_path_selector_probe.mp4`, `subtitle_render_path_selector_probe.local.json` under `episodes/.../subtitle_render_path_selector_probe/` |
| recorded_not_generated_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |
| generated_from | ED-10al uses the ED-10ak operation packet plus local source video/audio to run one bounded ignored FFmpeg/libass diagnostic rehearsal. |
| validation_command | Parse ED-10al stage-3 JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and generated local outputs are ignored. |
| latest_local_smoke | Same-machine rehearsal returned `status=local_ignored_probe_generated`, generated ignored ASS/MP4/manifest outputs, output metadata `duration_seconds=4.2`, `resolution=1920x1080`, `video_codec=h264`, `audio_codec=aac`, `stream_count=2`, style-token survival true, stable body text true, badge/accent/backplate route true, line-break/safe-area metadata true, `production_render_acceptance=false`, `public_use_permission=false`, and `episodes_tracked=false`. |
| review_status | No new Review Card. This is diagnostic rehearsal readback only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-1` or `final-render-path-stage-4` from this rehearsal packet while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_rehearsal_run=true`
- `final_render_path_approved=false`

## `clip-ed10as-internal-review-access-sheet-fullpath-001`

| field | value |
|---|---|
| title | ED-10as Internal Review Access Sheet Fullpath |
| purpose | Provide exact current-host full paths and a launcher for the ED-10ar internal review video candidate without creating render/replay/media or granting production/public/rights approval. |
| storage_class | tracked JSON/Markdown plus launcher script |
| repo_relative_path | docs/style_intent/internal-review-video-candidate-access-sheet.json; docs/style_intent/internal-review-video-candidate-access-sheet.md; scripts/operator/open_internal_review_video_candidate.ps1 |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_internal_review_video_candidate.ps1 |
| generated_from | ED-10as consumes ED-10ar and resolves the current-host full paths for the existing ignored MP4, ASS, and local manifest. |
| validation_command | Parse ED-10as and ED-10ar JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | MP4/ASS/manifest full paths resolved on current host; launcher command recorded; no render/replay/media modification; `episodes_tracked=false`; production/rights/public-use/publishing/monetization approvals remain false or pending. |
| review_status | access sheet only; no user review or decision requested now |
| next_action | Use the launcher only when a later supervisor asks for optional freeform observation. |

## `clip-ed10at-internal-review-observation-readback-001`

| field | value |
|---|---|
| title | ED-10at Internal Review Observation Readback |
| purpose | Consume the user's freeform observation after opening the ED-10as / ED-10ar internal review MP4 without turning it into production, public-use, rights, publishing, monetization, or approval state. |
| storage_class | tracked JSON/Markdown observation readback; no media artifact and no ignored episode output generated by this slice |
| repo_relative_path | docs/style_intent/internal-review-video-observation-readback.json; docs/style_intent/internal-review-video-observation-readback.md |
| open_command | see docs\\style_intent\\internal-review-video-observation-readback.md |
| generated_from | ED-10at consumes ED-10as access sheet plus ED-10ar internal review video candidate package, after repairing the stale local checkout assumption that had hidden those artifacts. |
| validation_command | Parse ED-10at, ED-10as, ED-10ar, and dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | Observation records `openability=pass`, `duration=expected_pass`, `subtitle_cue_coverage=pass_for_diagnostic_cue_probe`, `narrative_video_continuity=warning_not_representative_review`, `memo_like_appearance=warning_observed`, `review_guidance_clarity=partial_or_fail`, `new_render_run=false`, `new_media_created=false`, `stage_7_freeform_normalizer_used=false`, `user_observation_converted_to_approval=false`, and `episodes_tracked=false`. |
| review_status | observation readback only; no Review Card, no user-side work, no representative episode/video review, and no production/public approval |
| next_action | Build a representative micro-scene specimen with actual subtitle/script content only if continuing toward real internal review. Use `final-render-path-stage-4` only for a concrete render diagnostic gap; do not use stage-7 freeform normalization now. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10au-representative-micro-scene-internal-review-specimen-001`

| field | value |
|---|---|
| title | ED-10au Representative Micro-Scene Internal Review Specimen |
| purpose | Replace the ED-10at cue-label memo probe with a bounded internal-review specimen that contains actual Japanese subtitle/script content and enough scene continuity for later freeform review. |
| storage_class | tracked JSON/Markdown readback plus launcher; ignored same-machine MP4/ASS/local manifest under `episodes/` |
| repo_relative_path | docs/style_intent/representative-micro-scene-internal-review-specimen.json; docs/style_intent/representative-micro-scene-internal-review-specimen.md; scripts/operator/open_representative_micro_scene_internal_review_specimen.ps1 |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_internal_review_specimen.ps1 |
| generated_from | ED-10au consumes ED-10at observation readback, ED-10as access sheet, ED-10ar candidate package, source video/audio from the local JP pilot episode, and real transcript subtitles `sub_004`-`sub_006`. |
| validation_command | Parse ED-10au, ED-10at, ED-10as, ED-10ar, and dashboard JSON; run targeted subtitle/dashboard/review tests; ffprobe the ignored MP4; git diff --check; git diff --cached --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | MP4 exists on current host at `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.mp4`, size `3538973` bytes, duration `9.18s`, resolution `1920x1080`, codecs `h264/aac`, access_state `verified_present`, and manifest_size_bytes `10743`. |
| review_status | access verified; no user review requested now; later observation must stay freeform with at most three look-for points |
| next_action | If a later supervisor asks for review, open the launcher and classify the next fix as script, timing/audio, visual layout, or render path; do not infer production/public approval. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10av-micro-scene-observation-frame-readback-001`

| field | value |
|---|---|
| title | ED-10av Micro-Scene Observation Frame Readback |
| purpose | Preserve the user's freeform observation after opening the ED-10au specimen and classify the next practical axis without treating the observation as approval. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, or media artifact |
| repo_relative_path | docs/style_intent/micro-scene-observation-frame-readback.json; docs/style_intent/micro-scene-observation-frame-readback.md |
| open_command | see docs\\style_intent\\micro-scene-observation-frame-readback.md |
| generated_from | ED-10av consumes `clip-ed10au-representative-micro-scene-internal-review-specimen-001`, preserving the user's observation that the development target looked different, evaluation was unclear, the artifact looked like a real scene rather than the earlier cue/memo probe, and the lower subtitle area may be affected by player UI. |
| validation_command | Parse ED-10av and source ED-10au JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render or media smoke is run in ED-10av. Source ED-10au remains the access-verified specimen; ED-10av records observation and classification only. |
| review_status | observation consumed as readback; not approval; no additional user review requested now |
| next_action | Clarify the review frame first; capture subtitle/player-UI evidence only if needed; build a v2 specimen only for confirmed source/scene mismatch; use final-render-path-stage-4 only for a concrete render-path gap. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `layout_broken_claimed=false`
- `player_ui_overlap_confirmed=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`
- `user_review_requested_now=false`

## `clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001`

| field | value |
|---|---|
| title | ED-10aw Grill-me Adoption Readback and Review-Frame Clarification Plan |
| purpose | Classify the local Grill-me skill as a bounded helper and prepare the next review-frame clarification direction without turning ED-10av observation into approval. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, media artifact, or skill-file staging |
| repo_relative_path | docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.json; docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md |
| open_command | see docs\\style_intent\\grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md |
| generated_from | ED-10aw consumes `clip-ed10av-micro-scene-observation-frame-readback-001`, records `.agents/skills/grill-me/SKILL.md` and `skills-lock.json` as untracked local helper files, and fixes the allowed Grill-me output contract before ED-10aw review-frame clarification work. |
| validation_command | Parse ED-10aw and source ED-10av JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render or media smoke is run in ED-10aw. The repo state was read as main aligned with origin/main, with only the untracked Grill-me helper and lock retained outside staging. |
| review_status | adoption boundary and review-frame direction ready; no additional user review requested now; not approval |
| next_action | Use review-frame-clarification first; capture subtitle/player-UI evidence, build a v2 specimen, or use final-render-path-stage-4 only if that specific condition is verified. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `next_agent_prompt_allowed=false`
- `agent_report_nested_prompt_allowed=false`
- `grill_me_project_resource_authority=false`
- `grill_me_skill_files_staged=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ay-thank-ed10au-local-access-recovery-readback-001`

| field | value |
|---|---|
| title | ED-10ay Thank ED-10au Local Access Recovery Readback |
| purpose | Record current-host recovery of the ignored ED-10au representative micro-scene MP4/ASS/local manifest on the Thank terminal after tracked ED-10ax and the launcher were present but the local media were absent. |
| storage_class | tracked JSON/Markdown readback; regenerated MP4/ASS/local manifest remain ignored same-machine evidence under `episodes/` |
| repo_relative_path | docs/style_intent/thank-ed10au-local-access-recovery-readback.json; docs/style_intent/thank-ed10au-local-access-recovery-readback.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_internal_review_specimen.ps1 |
| generated_from | ED-10ay consumes ED-10ax and ED-10au tracked readbacks plus Thank-host source video/audio/transcript/edit_pack availability, then runs the existing bounded ED-10au local artifact writer for the same ignored output path. |
| validation_command | Parse ED-10ay JSON and dashboard JSON; ffprobe the generated MP4; run targeted subtitle/dashboard/review tests if tracked files changed; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | Initial MP4/ASS/manifest state was absent on the Thank host; source video/audio/transcript/edit_pack were present; bounded regeneration succeeded; final MP4 exists at `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.mp4`, size `3443682`, duration `9.18s`, H.264/AAC, 1920x1080, 30fps; ASS and local manifest are present. |
| review_status | access recovery only; no user review requested now; not approval |
| next_action | Use the existing ED-10au launcher on this host when a later supervisor asks to open the specimen. Keep ED-10ax as the review-frame surface and use screenshot/v2/final-render routes only under their recorded conditions. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `ignored_local_media_only=true`
- `representative_micro_scene_v2_created=false`
- `screenshot_capture_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10az-observation-readback-and-v2-route-decision-001`

| field | value |
|---|---|
| title | ED-10az Observation Readback and V2 Route Decision |
| purpose | Consume the user's ED-10ax-guided observation after opening the recovered ED-10au MP4 and decide the next route without treating the observation as approval. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, media artifact, v2 specimen, or tracked `episodes/` output |
| repo_relative_path | docs/style_intent/ed10az-observation-readback-and-v2-route-decision.json; docs/style_intent/ed10az-observation-readback-and-v2-route-decision.md |
| open_command | see docs\\style_intent\\ed10az-observation-readback-and-v2-route-decision.md |
| generated_from | ED-10az consumes `clip-ed10ax-review-frame-clarification-surface-001`, `clip-ed10ay-thank-ed10au-local-access-recovery-readback-001`, `clip-ed10au-representative-micro-scene-internal-review-specimen-001`, and the user's freeform observation after opening the recovered MP4. |
| validation_command | Parse ED-10az JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render, screenshot, media, or v2 specimen is created in ED-10az. The source MP4 was opened by the user after ED-10ay recovery; ED-10az records observation and route decision only. |
| review_status | observation consumed as readback; not approval; no additional user review requested now |
| next_action | Design `representative-micro-scene-v2-cut-window-and-review-purpose-alignment`; keep subtitle-layout screenshot capture, final-render-path stage-4, timing/audio, and another pure review-frame packet conditional only. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `subtitle_layout_failure_claimed=false`
- `player_ui_overlap_confirmed=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `representative_micro_scene_v2_created=false`
- `representative_micro_scene_v2_enabled=true`
- `screenshot_capture_created=false`
- `subtitle_layout_screenshot_capture_required_now=false`
- `final_render_path_stage_4_required_now=false`
- `timing_audio_first_route=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10bc-thank-v2-open-command-repair-readback-001`

| field | value |
|---|---|
| title | ED-10bc Thank V2 Open Command Repair Readback |
| purpose | Record and repair the Thank-terminal launcher path where the ED-10ba v2 MP4 was verified present but did not open visibly for the user. |
| storage_class | tracked JSON/Markdown readback plus launcher script repair; MP4/ASS/local manifest remain ignored same-machine evidence |
| repo_relative_path | docs/style_intent/thank-v2-open-command-repair-readback.json; docs/style_intent/thank-v2-open-command-repair-readback.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 |
| generated_from | ED-10bc consumes `clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001` and `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`; it classifies the user-visible failure as `file_verified_but_user_visible_open_failed`, not media/render loss, after verifying MP4/ASS/local manifest presence and ffprobe readability. |
| validation_command | Capture pre-repair launcher stdout/stderr/exit code; verify MP4/ASS/local manifest and ffprobe; run repaired launcher `-NoInvoke` and default smoke; parse ED-10bc JSON and dashboard JSON; run targeted subtitle/dashboard tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | Repaired default launcher returned exit `0`, process name `vlc`, `open_attempt_status=start_process_attempted_not_observed`, and `classification=file_verified_but_user_visible_open_not_confirmed`; `-NoInvoke` prints path/size/fallback diagnostics without opening. |
| review_status | opener repaired with fallbacks; no immediate user review requested; no production/public/rights/publishing/monetization or micro-scene approval |
| next_action | If a later supervisor asks to view the v2 specimen, use the repaired opener first; if no player appears, use `-SelectVideo` or `-OpenFolder` before considering any media regeneration. |

Boundary flags remain false or pending:

- `new_v3_created=false`
- `new_render_run=false`
- `new_media_created=false`
- `screenshot_capture_created=false`
- `final_render_path_stage_4=false`
- `timing_audio_first_route=false`
- `stage_7_freeform_normalizer_used=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`

## `clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001`

| field | value |
|---|---|
| title | ED-10bb Thank ED-10ba V2 Local Access Recovery Readback |
| purpose | Record actual Thank-terminal access recovery for ED-10ba without tracking ignored local media or treating access evidence as approval. |
| storage_class | tracked JSON/Markdown readback only; MP4/ASS/local manifest remain ignored same-machine evidence |
| repo_relative_path | docs/style_intent/thank-ed10ba-v2-local-access-recovery-readback.json; docs/style_intent/thank-ed10ba-v2-local-access-recovery-readback.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 |
| generated_from | ED-10bb consumes `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001` and records actual Thank-terminal recovery from `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`: initial ignored v2 MP4/ASS/local manifest absent, source video/audio/transcript/edit_pack present, bounded writer run, final `access_state=verified_present`. |
| validation_command | Parse ED-10bb JSON and dashboard JSON; verify ED-10ba tracked files are present; verify builder symbol exists; ffprobe the regenerated MP4; run targeted subtitle/dashboard tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | Thank-host regeneration completed on 2026-07-01 JST. Final MP4 exists with size `4627079`, duration `11.9s`, H.264/AAC, 1920x1080, 30fps; ASS size `1529`; local manifest size `13824`; `git ls-files episodes` remains empty. |
| review_status | access recovery complete with `verified_present`; no immediate user review requested; no production/public/rights/publishing/monetization or micro-scene approval |
| next_action | Use the opener only if a later supervisor asks for freeform v2 cut-window/review-purpose observation. Regenerate again only if the ignored outputs disappear and source inputs are still present. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `wrong_host_regeneration=false`
- `screenshot_capture_created=false`
- `final_render_path_stage_4=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`

| field | value |
|---|---|
| title | ED-10ba Representative Micro-Scene V2 Cut Window / Review Purpose Alignment |
| purpose | Produce a bounded v2 internal-review specimen that answers ED-10az: the recovered ED-10au MP4 opened, but the user could not tell what to judge, both cut edges felt too tight for cut-quality review, and the subtitle strategy did not clarify clipping/cutout usefulness. |
| storage_class | tracked JSON/Markdown readback plus launcher; generated MP4/ASS/local manifest remain ignored same-machine evidence under `episodes/` |
| repo_relative_path | docs/style_intent/representative-micro-scene-v2-cut-window-and-review-purpose-alignment.json; docs/style_intent/representative-micro-scene-v2-cut-window-and-review-purpose-alignment.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 |
| generated_from | ED-10ba consumes `clip-ed10az-observation-readback-and-v2-route-decision-001`, verifies the source video/audio/transcript/edit_pack on the current host, generates the ignored local v2 specimen with `write_representative_micro_scene_v2_cut_window_review_purpose_alignment_local_artifacts`, then records tracked access and review-purpose readback. |
| validation_command | Parse ED-10ba JSON and dashboard JSON; ffprobe the generated MP4; run targeted subtitle/dashboard tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | Bounded regeneration succeeded. Final MP4 exists at `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment/representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`, size `4723658`, duration `11.9s`, H.264/AAC, 1920x1080, 30fps. The ASS and local manifest are present in the same ignored folder. |
| review_status | v2 specimen ready for later freeform cut-window/review-purpose judgement; no immediate user review requested; not approval |
| next_action | Use the ED-10ba launcher only when a later supervisor asks to open the v2 specimen. Judge whether the wider `38.50s`-`50.40s` window and visible internal-review purpose label reduce review friction before considering subtitle strategy, screenshot capture, timing/audio, or render-path stage-4. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `subtitle_layout_failure_claimed=false`
- `player_ui_overlap_confirmed=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=true`
- `new_media_created=true`
- `representative_micro_scene_v2_created=true`
- `diagnostic_internal_review_subtitles_only=true`
- `screenshot_capture_created=false`
- `subtitle_layout_screenshot_capture_required_now=false`
- `final_render_path_stage_4_required_now=false`
- `timing_audio_first_route=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ax-review-frame-clarification-surface-001`

| field | value |
|---|---|
| title | ED-10ax Review-Frame Clarification Surface |
| purpose | Turn the ED-10aw plan into a concrete review-frame surface for the ED-10au specimen so a later reviewer knows what to judge, what not to judge, how to interpret ED-10av, and which next route to use. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, media artifact, v2 specimen, stage-7 normalizer, or skill-file staging |
| repo_relative_path | docs/style_intent/review-frame-clarification-surface.json; docs/style_intent/review-frame-clarification-surface.md |
| open_command | see docs\\style_intent\\review-frame-clarification-surface.md |
| generated_from | ED-10ax consumes `clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001` and `clip-ed10av-micro-scene-observation-frame-readback-001`, preserving the ED-10av observation as classification evidence rather than approval. |
| validation_command | Parse ED-10ax, ED-10aw, ED-10av, and dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render, screenshot, media, or v2 specimen is created in ED-10ax. The artifact records a later freeform review frame with exactly three look-for points and keeps Grill-me a local helper, not repo policy. |
| review_status | review-frame clarification surface ready for later use; no user review requested now; not approval |
| next_action | Use the ED-10ax surface for later freeform review. Use subtitle-layout-screenshot-capture only for lower subtitle/player-UI classification, representative-micro-scene-v2 only for confirmed source/scene mismatch, and final-render-path-stage-4 only for a concrete render-path gap. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `layout_broken_claimed=false`
- `player_ui_overlap_confirmed=false`
- `fixed_form_required=false`
- `yes_no_required=false`
- `next_agent_prompt_allowed=false`
- `agent_report_nested_prompt_allowed=false`
- `grill_me_project_resource_authority=false`
- `grill_me_skill_files_staged=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ar-internal-review-video-candidate-package-001`

| field | value |
|---|---|
| title | ED-10ar Internal Review Video Candidate Package |
| purpose | Assemble a tracked readback for an internal-review video candidate package from existing ignored diagnostic MP4/ASS/manifest output without running a new render or granting production/public/rights/render approval. |
| storage_class | tracked JSON/Markdown |
| repo_relative_path | docs/style_intent/internal-review-video-candidate-package.json; docs/style_intent/internal-review-video-candidate-package.md |
| open_command | notepad docs\\style_intent\\internal-review-video-candidate-package.md |
| generated_from | ED-10ar consumes ED-10aq stage-5 user-decision-ready and reuses the existing same-machine ignored ED-10af/ED-10al diagnostic MP4, ASS, and local manifest as the internal review video candidate package. |
| validation_command | Parse ED-10ar JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | Existing Output First: video/ASS/manifest are present under ignored `episodes/` paths, `duration_seconds=4.2`, `resolution=1920x1080`, `video_codec=h264`, `audio_codec=aac`, `stream_count=2`, `new_render_run=false`, `tracked_binary_artifact_created=false`, `episodes_tracked=false`, and production/rights/public-use/render approvals closed and separate. |
| review_status | internal-review video candidate package only; no user review or decision requested now |
| next_action | Use `optional-internal-review-video-observation` only for a later freeform observation, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |
## `clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001`

| field | value |
|---|---|
| title | ED-10aq Production Limitation Lift Stage 5 User Decision Ready |
| purpose | Verify that ED-10ap remains a freeform user decision surface only without asking for a decision now or granting production/public/rights/render approval. |
| storage_class | tracked JSON/Markdown |
| repo_relative_path | docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.json; docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.md |
| open_command | notepad docs\\style_intent\\subtitle-production-limitation-lift-stage-5-user-decision-ready.md |
| generated_from | ED-10aq consumes ED-10ap stage-4 user decision card and records gate checks, separation, and no-relapse guards. |
| validation_command | Parse ED-10aq JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | ED-10aq records answer_style=freeform, fixed_form_required=false, fixed_choice_rows_allowed=false, yes_no_rows_emitted=false, required_labels=[], screenshot_required=false, user_decision_requested_now=false, no render/replay/media, and production/rights/public-use/render approvals closed and separate. |
| review_status | stage-5 user-decision-ready packet only; no user decision requested now |
| next_action | Treat as complete stage-5 user-decision-ready packet; use final-render-path-stage-4 only if a concrete diagnostic gap is found. |

## `clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001`

| Field | Value |
|---|---|
| title | ED-10ap Production Limitation Lift Stage 4 User Decision Card |
| purpose | Convert the ED-10ao owner-review preparation entries into a future short stage-4 user decision card without approving production/public use or asking for a user decision now. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.json` |
| open_command | notepad docs\\style_intent\\subtitle-production-limitation-lift-stage-4-user-decision-card.md |
| source_owner_review_prep | `clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001` |
| source_decision_packet | `clip-ed10an-production-limitation-lift-stage-2-decision-packet-001` |
| source_gate_matrix | `clip-ed10am-production-limitation-lift-stage-1-001` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| decision_topics | subtitle design / visual acceptance; production render readiness; rights / publishing / public-use clearance |
| generated_from | ED-10ap uses ED-10ao owner-review groups and records plain-language future question shape, available and missing evidence, safe freeform answer hints, internal normalization hints, stop boundary, and unsafe overclaiming examples for each topic. |
| validation_command | Parse ED-10ap JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10ap has exactly three future decision topics, preserves ED-10ao and ED-10an source links, keeps future user answers freeform, emits no fixed user form or fixed-choice rows, requires no screenshot path, exposes no hidden schema as user input, and keeps all production/public flags false or pending. |
| review_status | No new Review Card. This is future user decision card only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Use `production-limitation-lift-stage-5-user-decision-ready`, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `user_decision_requested_now=false`
- `fixed_user_form_emitted=false`
- `fixed_choice_rows_emitted=false`
- `screenshot_required=false`
- `hidden_schema_exposed_to_user=false`
- `final_render_path_approved=false`

## `clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001`

| Field | Value |
|---|---|
| title | ED-10ao Production Limitation-Lift Stage 3 Owner-Review Prep |
| purpose | Convert the ED-10an three decision groups into owner-review preparation entries without approving production/public use or asking for a user decision now. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-stage-3-owner-review-prep.md` |
| source_decision_packet | `clip-ed10an-production-limitation-lift-stage-2-decision-packet-001` |
| source_gate_matrix | `clip-ed10am-production-limitation-lift-stage-1-001` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| owner_review_groups | subtitle design / visual acceptance; production render readiness; rights / publishing / public-use clearance |
| generated_from | ED-10ao uses ED-10an decision groups and records owner category, available evidence, missing evidence, safe next action, unsafe overclaiming, can-proceed-without-user-judgement, and must-stop-before-approval fields. |
| validation_command | Parse ED-10ao JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10ao groups exactly three owner-review entries, preserves ED-10an as the source decision packet, preserves ED-10am and ED-10al source links, emits no fixed user form, and keeps all production/public flags false or pending. |
| review_status | No new Review Card. This is owner-review preparation only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-4-user-decision-card`, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `user_decision_requested_now=false`
- `fixed_user_form_emitted=false`
- `fixed_choice_rows_emitted=false`
- `final_render_path_approved=false`

## `clip-ed10an-production-limitation-lift-stage-2-decision-packet-001`

| Field | Value |
|---|---|
| title | ED-10an Production Limitation-Lift Stage 2 Decision Packet |
| purpose | Convert the ED-10am nine-gate matrix into three bounded decision-preparation groups without approving production/public use. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-stage-2-decision-packet.md` |
| source_gate_matrix | `clip-ed10am-production-limitation-lift-stage-1-001` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| decision_groups | subtitle design / visual acceptance; production render readiness; rights / publishing / public-use clearance |
| generated_from | ED-10an uses ED-10am gate ownership, missing-evidence rows, and unsafe-overclaiming examples to prepare user-decision inputs without requesting immediate judgement. |
| validation_command | Parse ED-10an JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10an groups exactly three decision groups, preserves ED-10am as the source matrix, preserves ED-10al diagnostic metadata (`4.2s`, `1920x1080`, `h264`, `aac`, two streams), and keeps all production/public flags false or pending. |
| review_status | No new Review Card. This is decision-preparation readback only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-3-owner-review-prep`, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `user_decision_requested_now=false`
- `final_render_path_approved=false`

## `clip-ed10am-production-limitation-lift-stage-1-001`

| Field | Value |
|---|---|
| title | ED-10am Production Limitation-Lift Stage 1 |
| purpose | Convert ED-10al diagnostic final-path rehearsal evidence into a gate-by-gate production limitation-lift preparation packet without approving production/public use. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-1.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-1.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-stage-1.md` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| stage_2_source | `clip-ed10ak-final-render-path-stage-2-replayability-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| gates | diagnostic rehearsal evidence; production subtitle design acceptance; production render acceptance; creative acceptance; rights status; publishing acceptance; public-use permission; tracked media boundary; same-machine ignored evidence boundary |
| generated_from | ED-10am uses the ED-10al diagnostic rehearsal packet and records owners, missing evidence, and unsafe-overclaiming examples for each limitation-lift gate. |
| validation_command | Parse ED-10am JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10al source evidence remains `4.2s`, `1920x1080`, `h264`, `aac`, generated ignored ASS/MP4/manifest, and style-token/body/badge/safe-area survival true. ED-10am itself runs no render. |
| review_status | No new Review Card. This is decision-preparation readback only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-2-decision-packet`, or use `final-render-path-stage-4` only if more diagnostic evidence is genuinely needed. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `final_render_path_approved=false`

## `clip-ed10ae-render-path-selector-contract-probe-001`

| Field | Value |
|---|---|
| title | ED-10ae Render Path Selector Contract Probe |
| purpose | Define the static selector-to-render-path input contract for a later render adapter without running render or creating video/audio/frame artifacts. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-render-path-selector-contract.md` |
| metadata_json | `docs/style_intent/subtitle-render-path-selector-contract.json` |
| open_command | `see docs\style_intent\subtitle-render-path-selector-contract.md` |
| source_style_family_palette_artifact | `clip-ed10ad-style-family-palette-axis-proof-001` |
| source_visual_selector_artifact | `clip-ed10ac-visual-selector-proof-001` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10ae bounded static contract/readback slice using ED-10ad examples and L0 No Render. |
| validation_command | Parse style intent registry, preset selector, ED-10ac proof, ED-10ad proof, ED-10ae contract, dashboard JSON, and font candidates; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | The tracked contract represents all six semantic presets and lists semantic preset id, preset key, speaker/emotion/readability axes, family id, palette route, font family role, font size scale, outline/shadow token, badge/accent/backplate/body text color tokens, motion primitive, and safe-area/line-break behavior. Body text color remains `stable_default_body_text`; no render artifact is created. |
| review_status | No Review Card and no user-side work. The contract is static readback only and records later L2 tiny render path probe triggers as a separate milestone. |
| next_action | Use this selector-to-render-path contract before opening a later L2 tiny render probe. Production limitation-lift, rights, publishing, and public-use clearance remain separate routes. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10ad-style-family-palette-axis-proof-001`

| Field | Value |
|---|---|
| title | ED-10ad Style Family / Palette Axis Proof |
| purpose | Group the ED-10ac semantic preset examples by style family and palette route without changing body text color policy or running a render. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-style-family-palette-proof.html` |
| metadata_json | `docs/style_intent/subtitle-style-family-palette-proof.json` |
| open_command | `see docs\style_intent\subtitle-style-family-palette-proof.html` |
| source_visual_selector_artifact | `clip-ed10ac-visual-selector-proof-001` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10ad bounded static proof/readback slice using ED-10ac examples and L0 No Render / Existing Output First. |
| validation_command | Parse style intent registry, preset selector, ED-10ac visual selector proof, ED-10ad style-family/palette proof, dashboard JSON, and font candidates; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | The tracked proof represents all six semantic presets and groups them into dialogue current Keifont, emphasis energy, quiet soft readability, ominous inner voice, narration, and system note families. Palette routes are speaker identity blue, high energy warm, quiet cool, ominous dark, narration neutral green, and system neutral. Body text color remains `stable_default_body_text`; palette variation stays on badge/accent/backplate surfaces. |
| review_status | No Review Card and no user-side work. The proof introduces no new style family, no new palette, no body text color policy change, no production route, and no rights, publishing, or public-use decision. |
| next_action | Use this static axis proof before a later render-path probe. Any actual new style family, new palette, body text color policy change, production limitation-lift, rights, publishing, or public-use clearance remains a separate route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10ac-visual-selector-proof-001`

| Field | Value |
|---|---|
| title | ED-10ac Visual Selector Proof |
| purpose | Make the ED-10ab semantic preset examples visually inspectable as token differences without reopening raw numeric review or running a new render. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-visual-selector-proof.html` |
| metadata_json | `docs/style_intent/subtitle-visual-selector-proof.json` |
| open_command | `see docs\style_intent\subtitle-visual-selector-proof.html` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10ac bounded visual selector proof slice using ED-10ab selector examples and L1 Existing Output First. |
| validation_command | Parse `docs/style_intent/subtitle-style-intent-registry.json`, parse `docs/style_intent/subtitle-preset-selector.json`, parse `docs/style_intent/subtitle-visual-selector-proof.json`, parse dashboard JSON, run targeted subtitle/dashboard/review tests, `git diff --check`, and verify `git ls-files episodes` remains empty. |
| latest_local_smoke | The tracked proof represents neutral dialogue intensity 0, shout intensity 2, whisper intensity 1, ominous intensity 2, narration intensity 0, and system note intensity 0. Each card shows intent axes, preset key, font family role, font size scale, outline/shadow token, badge color token, accent color token, backplate/box token, motion placeholder, safe-area/line-break behavior, stable body text color token, and human review status. |
| review_status | No Review Card. The proof introduces no new style family, palette, body text color policy, production route, rights, publishing, or public-use decision. Optional user-side work is open-only freeform observation, maximum 3 points. |
| next_action | Use this proof as the current tracked selector readback. Future movement should be a separate new axis such as style-family exploration, palette proposal, line-break policy tuning, production limitation-lift, final render-path probe, rights, publishing, or public-use clearance. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10ab-subtitle-preset-selector-001`

| Field | Value |
|---|---|
| title | ED-10ab Subtitle Preset Selector |
| purpose | Connect the ED-10aa semantic intent registry to a deterministic selector that maps subtitle intent axes to style token candidates without asking for repeated raw numeric reviews. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-preset-selector.json` |
| metadata_json | `docs/style_intent/subtitle-preset-selector.json` |
| open_command | `see docs\style_intent\subtitle-preset-selector.json` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | Prompt-authorized ED-10ab selector/readback slice consuming the ED-10aa axes and preserving ED-10z as existing visual evidence. |
| validation_command | Parse `docs/style_intent/subtitle-style-intent-registry.json`, parse `docs/style_intent/subtitle-preset-selector.json`, regenerate docs dashboard, run targeted subtitle/dashboard tests, `git diff --check`, and verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Selector examples cover neutral dialogue intensity 0, shout intensity 2, whisper intensity 1, ominous intensity 2, narration, and system note. Each returns font family role, font size scale, outline/shadow strength, badge color, accent color, backplate/box, motion placeholder, safe-area/line-break behavior, and stable body text color token. |
| review_status | No new Review Card. No new visual proof or style family is introduced, and the same Candidate 0-3 comparison remains closed. |
| next_action | Use this selector as a deterministic preset readback before any future visual selector proof. Open a separate route for new style family, new palette, body text color policy change, production route, rights, publishing, or public-use decisions. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10aa-subtitle-style-intent-registry-001`

| Field | Value |
|---|---|
| title | ED-10aa Subtitle Style Intent Registry |
| purpose | Record semantic subtitle style-control axes so future agents can map speaker, emotion, intensity, utterance role, and readability tags to presets instead of asking for repeated tiny numeric outline/shadow/opacity reviews. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/SUBTITLE_STYLE_INTENT_REGISTRY.md` |
| metadata_json | `docs/style_intent/subtitle-style-intent-registry.json` |
| open_command | `see docs\SUBTITLE_STYLE_INTENT_REGISTRY.md` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| source_previous_artifact | `clip-ed10y-candidate2-carry-forward-001` |
| source_proof_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| generated_from | Prompt-authorized ED-10aa design/readback slice consuming the latest review that Candidate 0/2 are acceptable, Candidate 1/3 are thin, primary review samples were too small, and future styling should move toward emotion/speaker/readability semantics. |
| validation_command | Parse `docs/style_intent/subtitle-style-intent-registry.json`, regenerate docs dashboard, run targeted subtitle/dashboard tests, `git diff --check`, and verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Registry records axes `speaker_id`, `speaker_role`, `emotion`, `intensity`, `utterance_role`, and `readability_priority`; maps them to font family, font size scale, outline/shadow, badge color, accent color, backplate/box, motion placeholder, and safe-area/line-break tokens; keeps body text color stable by default; and marks human review as required only for new style family, new color palette, body text color policy change, production-route change, rights, publishing, or public-use decisions. |
| review_status | No new Review Card. The same Candidate 0-3 comparison, Keifont acceptance, cut_002/cut_003 review, and cut_008/sub_096 pass remain closed. |
| next_action | Use this registry before future subtitle style work. ED-10z remains the current render-path-nearer probe source and now has refreshed same-machine local proof output; any limitation-lift or final render-path work should be opened as a separate route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10z-tiny-render-path-nearer-probe-001`

| Field | Value |
|---|---|
| title | ED-10z Tiny Render-Path-Nearer Probe |
| purpose | Preserve `clip-ed10y-candidate2-carry-forward-001` as source/previous state and pass Candidate 2 through the current FFmpeg/libass diagnostic path as a tiny local readback probe. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.html` |
| metadata_json | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.json` |
| open_command | `.\open-current-proof.ps1` |
| source_previous_artifact | `clip-ed10y-candidate2-carry-forward-001` |
| source_review_artifact | `clip-ed10y-candidate2-carry-forward-001` |
| source_proof_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10z_tiny_render_path_nearer_probe --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10z_tiny_render_path_nearer_probe --format json` plus targeted tests. |
| latest_local_smoke | ED-10z actual rerun with explicit FFmpeg/FFprobe paths returned `artifact_id=clip-ed10z-tiny-render-path-nearer-probe-001`, `proof_profile=ed10z_tiny_render_path_nearer_probe`, `source_review_artifact_id=clip-ed10y-candidate2-carry-forward-001`, `visual_proof_status=available_requires_human_review`, `review_card_status=withheld_tiny_render_path_nearer_probe_completed`, `focused_proof_review.status=tiny_render_path_nearer_probe_completed`, `subtitle_overlay_available_count=1`, Candidate 2 as current lead, Candidate 0 as fallback/reference, Candidate 1 / 3 as held references, and no same-candidate review request. |
| review_status | No new Review Card. The latest Candidate 0-3 review is already consumed; this is diagnostic probe readback only. |
| next_action | Use this as refreshed same-machine local readback only. Any production limitation-lift, final render-path, rights, publishing, or public-use decision remains a separate route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored HTML/JSON/PNG/MP4/ASS artifacts themselves. Other
worktrees should treat missing `episodes/` review assets as local evidence
absence, not as a tracked Git failure. `git ls-files episodes` should remain
empty.

## `clip-ed10y-candidate2-carry-forward-001`

| Field | Value |
|---|---|
| title | ED-10y Candidate 2 Carry-Forward Pack |
| purpose | Consume the latest ED-10w/ED-10x freeform review, promote Candidate 2 as provisional bounded-decoration lead, retain Candidate 0 as fallback, and hold Candidate 1 / 3 because they read too thin. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.html` |
| metadata_json | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.json` |
| open_command | `.\open-current-proof.ps1` |
| source_review_artifact | `clip-ed10w-subtitle-presentation-review-pack-001` |
| source_proof_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10y_candidate2_carry_forward --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10y_candidate2_carry_forward --format json` plus targeted tests. |
| latest_local_smoke | Same-machine ED-10y regeneration writes the same current `subtitle_presentation_review_pack.html` / `.json` path with `artifact_id=clip-ed10y-candidate2-carry-forward-001`, `review_card.action_type=NO_REVIEW_CARD_REVIEW_CONSUMED`, Candidate 2 as `provisional_bounded_decoration_lead`, Candidate 0 as `fallback_reference`, Candidate 1 / 3 as `held_reference`, and `render_path_readiness.status=candidate2_tiny_render_path_nearer_diagnostic_probe_completed`. Full-frame context is no longer constrained to the old cramped 220px proof width. |
| review_status | Latest freeform review consumed. Do not request another Candidate 0-3 comparison review, general Keifont acceptance, cut_002/cut_003 review, or the same cut_008 dense/multiline pass. |
| next_action | Use Candidate 2 as the provisional bounded-decoration lead. Next movement should be a genuinely new axis such as production limitation-lift or final render-path probe, not another same-candidate comparison. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored HTML/JSON/PNG/MP4/ASS artifacts themselves. Other
worktrees should treat missing `episodes/` review assets as local evidence
absence, not as a tracked Git failure. `git ls-files episodes` should remain
empty.

## `clip-ed10w-subtitle-presentation-review-pack-001`

| Field | Value |
|---|---|
| title | ED-10w Subtitle Presentation Review Pack |
| purpose | Combine the already-passed ED-10v dense/stress evidence with one genuinely new review axis: bounded decoration adjustment plus render-path readiness. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.html` |
| metadata_json | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.json` |
| open_command | `.\open-current-proof.ps1` |
| source_review_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| source_comparison_artifact | `clip-ed10o-multifont-focused-review-001` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10w_subtitle_presentation_review_pack --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10w_subtitle_presentation_review_pack --format json` plus targeted tests. |
| latest_local_smoke | ED-10x regeneration keeps the same artifact/path and adds compact subtitle-body crops, SPK badge crops, and Candidate Delta Readback. Same-machine readback: Candidate 0 baseline `outline=7`, `shadow=2`, badge text opacity `1.0`; Candidate 1 `outline=5`, `shadow=1`; Candidate 2 badge text/background opacity `0.435/0.122`; Candidate 3 combines both axes. All Candidate 1-3 delta statuses are `visible`; full-frame images remain secondary click-through context. |
| review_card | One updated new-axis Review Card: `bounded_decoration_adjustment + render_path_readiness`. It asks whether Candidate 0 remains best, whether Candidate 1/2/3 is preferable, and whether the render-path probe should proceed. It does not ask for another general `cut_002` / `cut_003` Keifont review and does not ask for another pass/fail judgement on the same `cut_008` multiline evidence. |
| bounded_candidates | `ed10w_current_pass_reference`, `ed10w_lighter_outline_shadow_pressure`, `ed10w_badge_label_pressure_adjustment`, `ed10w_balanced_combined_low_risk` |
| render_path_readiness | Diagnostic decision card only. It may authorize a later tiny render-path probe, but it is not production render acceptance. |
| review_status | Ready for one freeform subtitle presentation review after ED-10x candidate-delta visibility fix. |
| next_action | Review the crop-first pack once and choose whether Candidate 0 remains best, Candidate 1/2/3 is preferable, or only the tiny render-path readiness probe should proceed. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored HTML/JSON/PNG/MP4/ASS artifacts themselves. Other
worktrees should treat missing `episodes/` review assets as local evidence
absence, not as a tracked Git failure. `git ls-files episodes` should remain
empty.

## `clip-ed10r-keifont-dense-stress-proof-001`

| Field | Value |
|---|---|
| title | ED-10r / ED-10u / ED-10v Keifont Dense/Stress Proof |
| purpose | Treat Keifont as diagnostic representative normal-dialogue provisional baseline from the ED-10n/ED-10o review history, avoid another general `cut_002` / `cut_003` acceptance review, and record the corrected `cut_008` multiline/dense-stress proof as ED-10v diagnostic pass. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/current_proof_focused_review.html` |
| detailed_overlay_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| representative_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html` |
| open_command | Fallback from `.\open-current-proof.ps1`; root launcher now opens the ED-10w review pack first. |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10r_keifont_dense_stress_proof --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10r_keifont_dense_stress_proof --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10u regeneration returned `artifact_id=clip-ed10r-keifont-dense-stress-proof-001`, `proof_profile=ed10r_keifont_dense_stress_proof`, `target_cuts=[cut_008]`, `visual_proof_status=available_requires_human_review`, `review_card_status=review_card_allowed_after_scope_checks`, `subtitle_overlay_available_count=1`, `focused_proof_review.status=dense_stress_keifont_proof_ready`, `font_visual_evidence.status=valid_requested_keifont_visual_evidence`, `requested_font_family=Keifont`, `resolved_font_family=Keifont`, `resolved_font_file=C:/Users/PLANNER007/AppData/Local/Microsoft/Windows/Fonts/keifont.ttf`, `multiline_wrap_evidence.status=multiline_wrap_evidence_surfaced`, `multiline_wrap_evidence.subtitle_id=sub_096`, `wrapped_line_count=2`, `screenshot_count=1`, `screenshot_role=multiline_wrap_1`, `screenshot_path=episodes/.../subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_008.sample_multiline_wrap_1.png`, `focused_html_multiline_image_max_width=220px`, `production_candidate=false`, and `rights_status=pending`. ED-10v then consumed the user review as `diagnostic_dense_stress_passed` for subtitle display / all-pass, without changing production/public gates. |
| review_memory | `prior_review_count=3+`; accepted scope is diagnostic representative review / provisional normal-dialogue baseline / diagnostic dense-stress pass; not accepted scope is production subtitle design, production render, creative acceptance, rights, publishing, public use; next non-redundant axes are linebreak policy readback, bounded decoration adjustment, future shared subtitle layout policy, production limitation-lift, or render-path probe; repeated general review is false. |
| review_card | Withheld after pass: do not emit another Review Card for the same corrected `cut_008` multiline/dense-stress evidence, and do not re-decide general Keifont acceptance from `cut_002` / `cut_003`. |
| review_status | ED-10v records current dense/stress + multiline/wrap route as diagnostic pass with valid same-machine Keifont evidence. This is still diagnostic review, not production subtitle design, render, creative, rights, publishing, or public-use acceptance. |
| next_action | Move only through a genuinely new axis: line-break policy tuning, bounded outline/shadow/badge adjustment, production limitation-lift, or render-path probe. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked code, docs, and tests but not the ignored
MP4/PNG/ASS files themselves. Other worktrees should treat missing
`episodes/` proof assets as local evidence absence, not as a tracked Git
failure. `git ls-files episodes` should remain empty.

## `clip-ed10g-noto-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10g Noto Sans JP Diagnostic Overlay Proof |
| purpose | Apply the selected `noto_sans_jp_clean_outline` typography / decoration base to the `cut_002` / `cut_003` diagnostic subtitle overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id noto_sans_jp_clean_outline` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id noto_sans_jp_clean_outline --format json` plus targeted tests. |
| latest_validation_result | `git diff --check` clean; `uvx pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py` -> `18 passed, 8 skipped`; Pillow-enabled supplement `uvx --with pillow pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py` -> `13 passed`. |
| latest_local_smoke | Same-machine generation on 2026-06-16 JST returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=noto_sans_jp_clean_outline`, `typography_decoration_candidate_id=noto_sans_jp_clean_outline`, `subtitle_overlay_available_count=2`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`. JSON readback resolved the `Noto Sans JP` route with `font_file_status=candidate_primary_font_file_found`, `font_size=124`, `font_size.readback=round(frame_height * 0.115)`, `outline=11`, `outline.readback=max(2, round(font_size * 0.086))`, `bbox_wrapping_applied=true`, `explicit_ass_line_breaks=true`, `one_character_orphan_present=false`, and `suspicious_tail_line_present=false`. Both target cuts had MP4/PNG/ASS assets, the `cut_002` and `cut_003` PNG frames were inspected as nonblank 1920x1080 local visual artifacts, and a readback-based bbox/safe-area check reported no computed failures. |
| human_visual_judgement | Accepted on 2026-06-16 JST for the ED-10g diagnostic route, then superseded for styling on 2026-06-17 by a new review that says the proof is not accepted as-is. |
| review_status | Historical diagnostic proof / current reference only. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Keep as historical reference. The current selected proof is `clip-ed10i-meiryo-overlay-proof-001`. |

`status-episode` can still report global `operator_review.review_ready=false`
because the broader R3 artifact set is missing legacy `visual_proof_cut_001.png`.
That global blocked state is separate from this scoped ED-10g `cut_002` /
`cut_003` proof readback.

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked code, docs, and tests but not the ignored
MP4/PNG/ASS files themselves. Other worktrees should treat missing
`episodes/` proof assets as local evidence absence, not as a tracked Git
failure.

## `clip-docs-dashboard-001`

| Field | Value |
|---|---|
| title | Docs Wiki Dashboard v1.5 |
| purpose | Make the tracked Markdown corpus readable as a project wiki/dashboard with current focus, feature progress, active artifacts, doc-health findings, and next review items. |
| storage class | Tracked docs artifact; portable Git evidence. |
| repo_relative_path | `docs/dashboard/index.html` |
| metadata_json | `docs/dashboard/project-status.json` |
| features_index | `docs/features/index.md` |
| open_command | `.\open-dashboard.ps1` |
| generated_from | `build-docs-dashboard` reading tracked Markdown registries and docs. |
| validation_command | `uvx python -m src.cli.main build-docs-dashboard --format json` plus `uvx pytest -q tests/test_docs_dashboard.py`. |
| latest_validation_result | 2026-06-16 v1.5 slice: dashboard regenerated; `project-status.json` parsed; Chrome headless screenshot inspected as readable/nonblank; `uvx pytest -q tests/test_docs_dashboard.py tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py` -> `21 passed, 8 skipped`. |
| review_status | Tracked dashboard entry is ready for operator navigation; not an episode media proof and not production/public acceptance. |
| next_action | Use this as the first docs navigation surface, then improve high-friction docs from the generated doc-health findings. |

## `clip-subtitle-font-candidate-sweep-001`

| Field | Value |
|---|---|
| title | ED-10h Subtitle Font Candidate Sweep v0 Registry |
| purpose | Define the next subtitle font candidate universe while preserving the current ED-10g selected diagnostic proof base. |
| storage class | Tracked docs/data artifact; no third-party font binaries vendored. |
| repo_relative_path | `docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md` |
| metadata_json | `docs/font_candidates/subtitle-font-candidates.json` |
| open_command | `.\open-font-candidates.ps1` |
| generated_from | Manual v1.5 registry definition plus same-machine Windows font directory readback for local availability. |
| validation_command | `python -m json.tool docs/font_candidates/subtitle-font-candidates.json` plus dashboard/tests. |
| latest_validation_result | 2026-06-16 v1.5 slice: `python -m json.tool docs/font_candidates/subtitle-font-candidates.json` ok; targeted docs/subtitle/review tests -> `21 passed, 8 skipped`. |
| review_status | Candidate registry defined. Downloads and vendoring are not approved; local font availability is same-machine readback only. |
| next_action | Choose whether ED-10h should run no-download local/system comparison first or request permission for Google Fonts downloads with captured license metadata. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
