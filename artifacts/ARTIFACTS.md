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
| latest_validation_result | `17 passed, 8 skipped` on the 2026-06-16 targeted local validation path. |
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
| latest_local_smoke | Prior same-machine generation produced 4 candidates, 16 PNG samples, JSON/HTML report, contact sheet, and `open_comparison.ps1`; `font_size_policy.value=124`, `production_subtitle_design_acceptance=false`, `rights_status=pending`. Current worktrees may lack this ignored artifact and must treat absence as local evidence absence, not a tracked Git failure. |
| review_status | Human response consumed as `small_adjustment`; diagnostic / representative only. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Use the generator's `next_diagnostic_overlay_proof_route` readback to define or generate the next small-adjustment diagnostic overlay proof route for `cut_002` / `cut_003`, preserving accepted font size while selecting or refining font-family and decoration axes. |

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
