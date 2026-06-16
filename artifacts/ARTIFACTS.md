# Artifact Registry

This registry points to reviewable artifacts without pretending that ignored
local files are portable across clones.

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
| next_action | Use `noto_sans_jp_clean_outline` as the selected next diagnostic overlay proof base for `cut_002` / `cut_003`; inspect the generated overlay proof before any further subtitle-design judgment. |

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

## `clip-ed10g-noto-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10g Noto Sans JP Diagnostic Overlay Proof |
| purpose | Apply the selected `noto_sans_jp_clean_outline` typography / decoration base to the `cut_002` / `cut_003` diagnostic subtitle overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | `powershell -NoProfile -Command "Invoke-Item -LiteralPath 'episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_overlay_visual_proof_report.html'"` |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id noto_sans_jp_clean_outline` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id noto_sans_jp_clean_outline --format json` plus targeted tests. |
| latest_validation_result | `git diff --check` clean; `uvx pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py` -> `18 passed, 8 skipped`; Pillow-enabled supplement `uvx --with pillow pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py` -> `13 passed`. |
| latest_local_smoke | Same-machine generation on 2026-06-16 JST returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=noto_sans_jp_clean_outline`, `typography_decoration_candidate_id=noto_sans_jp_clean_outline`, `subtitle_overlay_available_count=2`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`. JSON readback resolved the `Noto Sans JP` route with `font_file_status=candidate_primary_font_file_found`, `font_size=124`, `font_size.readback=round(frame_height * 0.115)`, `outline=11`, `outline.readback=max(2, round(font_size * 0.086))`, `bbox_wrapping_applied=true`, `explicit_ass_line_breaks=true`, `one_character_orphan_present=false`, and `suspicious_tail_line_present=false`. Both target cuts had MP4/PNG/ASS assets, the `cut_002` and `cut_003` PNG frames were inspected as nonblank 1920x1080 local visual artifacts, and a readback-based bbox/safe-area check reported no computed failures. |
| review_status | Generated and awaiting human diagnostic / representative visual review. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Ask one focused question against the generated overlay proof: whether the selected Noto clean-outline small adjustment is acceptable for diagnostic / representative review on `cut_002` / `cut_003`. |

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
