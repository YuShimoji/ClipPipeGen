# Artifact Registry

This registry points to reviewable artifacts without pretending that ignored
local files are portable across clones.

Normal open order is `.\open-dashboard.ps1` first, choose the artifact from the
dashboard, then use an artifact-specific launcher such as
`.\open-current-proof.ps1` only when the local ignored proof is needed.

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
| open_command | `.\open-current-proof.ps1` |
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
| next_action | Treat this as consumed audit trail. Use `clip-ed10k-biz-overlay-proof-001` for the current visual judgement; reopen the contact sheet only if the BIZ proof fails and a fallback candidate is needed. |

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
| open_command | `.\open-current-proof.ps1` |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id ed10j_biz_udgothic_bold_telop_candidate` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10j_biz_udgothic_bold_telop_candidate --format json` plus targeted tests. |
| latest_validation_result | Same-machine generation returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10j_biz_udgothic_bold_telop_candidate`, `typography_decoration_candidate_id=ed10j_biz_udgothic_bold_telop_candidate`, `subtitle_overlay_available_count=2`, `all_target_cuts_have_overlay=true`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`; JSON parsed successfully. |
| latest_local_smoke | Same-machine readback resolved `font_family_route.requested=BIZ UDGothic`, `font_family_route.font_file_status=candidate_primary_font_file_found`, `font_size=124`, `outline=8`, `ed10j_kirinuki_font_audit_candidate=true`, `explicit_line_breaks_passed_to_ass=true`, `one_character_orphan_present=false`, and `suspicious_tail_line_present=false`. The `cut_002` and `cut_003` PNG frames were inspected as nonblank 1920x1080 local visual artifacts. |
| review_status | Generated and requires freeform human visual review. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Review the BIZ UDGothic proof for body weight, outline pressure, and whether it feels like an intentional kirinuki normal-dialogue subtitle base. Freeform review is enough. |

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

## `clip-ed10g-noto-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10g Noto Sans JP Diagnostic Overlay Proof |
| purpose | Apply the selected `noto_sans_jp_clean_outline` typography / decoration base to the `cut_002` / `cut_003` diagnostic subtitle overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | `.\open-current-proof.ps1` |
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
