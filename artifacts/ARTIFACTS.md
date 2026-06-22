# Artifact Registry

This registry points to reviewable artifacts without pretending that ignored
local files are portable across clones.

Normal open order is `.\open-dashboard.ps1` first, choose the artifact from the
dashboard, then use an artifact-specific launcher. For the current ED-10r
Keifont dense/stress proof on `cut_008`, use `.\open-current-proof.ps1`;
for the accepted ED-10o focused comparison
reference, use
`episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1`;
for the supporting regenerated ED-10l real-font comparison, use
`episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1`;
the reviewed ED-10k BIZ proof is now a reference entry, not the current proof
opened by the root launcher.

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

## `clip-ed10r-keifont-dense-stress-proof-001`

| Field | Value |
|---|---|
| title | ED-10r / ED-10u Keifont Dense/Stress Proof |
| purpose | Treat Keifont as diagnostic representative normal-dialogue provisional baseline from the ED-10n/ED-10o review history, avoid another general `cut_002` / `cut_003` acceptance review, and make the corrected `cut_008` multiline/dense-stress proof the current review target. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/current_proof_focused_review.html` |
| detailed_overlay_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| representative_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html` |
| open_command | `.\open-current-proof.ps1` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10r_keifont_dense_stress_proof --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10r_keifont_dense_stress_proof --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10u regeneration returned `artifact_id=clip-ed10r-keifont-dense-stress-proof-001`, `proof_profile=ed10r_keifont_dense_stress_proof`, `target_cuts=[cut_008]`, `visual_proof_status=available_requires_human_review`, `review_card_status=review_card_allowed_after_scope_checks`, `subtitle_overlay_available_count=1`, `focused_proof_review.status=dense_stress_keifont_proof_ready`, `font_visual_evidence.status=valid_requested_keifont_visual_evidence`, `requested_font_family=Keifont`, `resolved_font_family=Keifont`, `resolved_font_file=C:/Users/PLANNER007/AppData/Local/Microsoft/Windows/Fonts/keifont.ttf`, `multiline_wrap_evidence.status=multiline_wrap_evidence_surfaced`, `multiline_wrap_evidence.subtitle_id=sub_096`, `wrapped_line_count=2`, `screenshot_count=1`, `screenshot_role=multiline_wrap_1`, `screenshot_path=episodes/.../subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_008.sample_multiline_wrap_1.png`, `focused_html_multiline_image_max_width=220px`, `production_candidate=false`, and `rights_status=pending`. |
| review_memory | `prior_review_count=2+`; accepted scope is diagnostic representative review / provisional normal-dialogue baseline; not accepted scope is production subtitle design, production render, creative acceptance, rights, publishing, public use; next non-redundant axis is `dense_stress`; repeated general review is false; current blocker is `none_for_font_evidence`. |
| review_card | `USER_REVIEW_DENSE_STRESS_ONLY`: review the corrected `cut_008` multiline/dense-stress surface, especially the compact `sub_096` two-line screenshot, wrapping, rapid cue replacement, safe area, and bounded outline/shadow/badge pressure. Do not re-decide general Keifont acceptance from `cut_002` / `cut_003`. |
| review_status | Current dense/stress route is established, same-machine visual evidence is valid Keifont evidence, and ED-10u now surfaces real multiline/wrap evidence for the dense/stress axis. This is still diagnostic review, not production subtitle design, render, creative, rights, publishing, or public-use acceptance. |
| next_action | Open `.\open-current-proof.ps1` and review only the corrected `cut_008` multiline/dense-stress target. |

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
