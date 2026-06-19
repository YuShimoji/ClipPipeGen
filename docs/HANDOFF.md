# ClipPipeGen Handoff

Last updated: 2026-06-19 JST

This file is the shortest project-local handoff for resuming from another terminal. It complements `AGENTS.md`, `README.md`, and `docs/RUNTIME_STATE.md`; it does not replace them. Operator-facing restart and review responses follow `docs/OPERATOR_REVIEW_UX.md`.

Resume-first rule: on restart, read `docs/RUNTIME_STATE.md` and its Current Resume Capsule before using older handoff notes. Long historical closeouts now live in `docs/RUNTIME_HISTORY.md`; do not treat archived `current_slice` / `next_action` entries as current instructions.

## Immediate Resume Capsule - 2026-06-19 ED-10l Font Fallback Audit

Fresh terminal setup:

```powershell
git fetch --prune origin
git checkout main
git pull --ff-only origin main
git status --short --branch
git rev-list --left-right --count HEAD...origin/main
git log -1 --oneline --decorate
git ls-files episodes
```

Expected state after pulling this handoff:

- Branch: `main`
- Upstream: `origin/main`
- `HEAD...origin/main`: `0 0`
- `git ls-files episodes`: empty
- Latest sync point: ED-10l known kirinuki font fallback audit handoff
- Expected latest commit: ED-10l fallback/readback audit commit; verify with
  `git log -1 --oneline --decorate`

Known same-machine caveat: this local repository currently has a broken
`refs/codex/turn-diffs/checkpoints/...` checkpoint ref, so `git fetch --prune
origin` can fail with `fatal: bad object refs/codex/...`. The final push still
succeeded, and `git ls-remote origin refs/heads/main` matched local
`HEAD=774c590f0125e85233d29cdfe1aa5f0e1d5eb054`. If fetch fails only on that
local checkpoint ref, verify remote parity with:

```powershell
git ls-remote origin refs/heads/main
git rev-list --left-right --count "HEAD...origin/main"
git log -1 --oneline --decorate
```

Current active artifact is `clip-ed10l-known-kirinuki-font-pack-001`.
The ED-10k BIZ UDGothic proof has been reviewed and is not accepted as the
normal-dialogue subtitle baseline. The review says BIZ feels too hard/rigid,
the text remains thin, and the black outline pressure is too strong. This also
rejects the broader BIZ/Noto/Meiryo system-safe route for this use case; those
fonts remain reference/rejected evidence only.

ED-10l is the active route correction. It audits known Japanese YouTube
kirinuki/telop fonts before another overlay proof is selected:

- comparison profile: `ed10l_known_kirinuki_font_pack`
- artifact: `clip-ed10l-known-kirinuki-font-pack-001`
- target cuts: `cut_002`, `cut_003`
- normal-dialogue candidates:
  `ed10l_keifont_pop_dialogue_candidate`,
  `ed10l_851_chikara_yowaku_dialogue_candidate`,
  `ed10l_m_plus_fonts_dialogue_candidate`,
  `ed10l_yasashisa_gothic_goodfreefonts_candidate`
- separate emphasis/shout slot: `ed10l_851_chikara_zuyoku_emphasis_candidate`
- separate mood/literary slot:
  `ed10l_source_han_serif_mood_candidate`,
  `ed10l_shippori_mincho_mood_candidate`
- current selected proof base:
  `pending_real_font_install_readback_after_fallback_confirmation`
- recommended first route:
  `ed10l_keifont_pop_dialogue_candidate`
- target fonts found locally on 2026-06-19 JST: none
- current generated ED-10l normal-dialogue samples resolved to
  `NotoSansJP-VF.ttf` with
  `requested_candidate_font_missing_used_font_file_found`
- generated samples are fallback/missing-font evidence and are invalid for
  target-font visual selection until real font install readback exists

Open order:

1. `.\open-dashboard.ps1`
2. choose the ED-10l known-font pack artifact from the dashboard only to inspect
   fallback/readback evidence
3. if the same-machine ignored artifact is present, open it with:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1
```

If a fresh checkout does not have `episodes/`, treat that as local evidence
absence, not a Git failure. Regenerate local retained artifacts only when the
upstream episode artifacts are present. For the reviewed ED-10k BIZ reference
proof, use:

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --typography-decoration-candidate-id ed10j_biz_udgothic_bold_telop_candidate `
  --format json
```

For the ED-10l comparison artifact, use:

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison `
  --comparison-profile ed10l_known_kirinuki_font_pack `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

Review card for the next human response:

- target: `clip-ed10l-known-kirinuki-font-pack-001`
- do not choose from the current fallback contact sheet; it rendered
  `NotoSansJP-VF.ttf`, not the requested ED-10l fonts
- choose or prepare which known normal-dialogue font should get official
  source/license/install/readback first
- regenerate the visual proof only after the requested font file resolves
- keep `851チカラヅヨク` in emphasis/shout/tsukkomi and keep
  `源ノ明朝` / `しっぽり明朝` in mood/literary; do not collapse those into
  normal-dialogue baseline acceptance
- freeform review is enough; do not ask for fixed accept/reject labels
- after review, capture official source/license/install notes before any real
  font file enters a reproducible proof route

Tracked context surfaces:

| Surface | Purpose |
|---|---|
| `docs/RUNTIME_STATE.md` | current resume capsule and ED-10l review route |
| `docs/index.md` | human-facing wiki entrance and open-surface order |
| `docs/dashboard/index.html` | generated project dashboard |
| `docs/dashboard/project-status.json` | machine-readable dashboard state |
| `docs/features/index.md` | generated feature progress table |
| `artifacts/ARTIFACTS.md` | artifact registry and ED-10l known-font entry |
| `docs/SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md` | route change from ED-10k BIZ rejection to ED-10l known-font audit |
| `docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md` | candidate registry and known-font source/readback |
| `docs/font_candidates/subtitle-font-candidates.json` | machine-readable candidate registry |

Validation at handoff creation:

- `uvx pytest -q tests/test_docs_dashboard.py tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py`
  -> `23 passed, 14 skipped`
- `uvx --with pillow pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py`
  -> `21 passed`
- JSON parse checks passed for dashboard, font registry, and the same-machine
  ED-10l local report
- `git diff --check` clean
- `git ls-files episodes` empty
- final `HEAD...origin/main=0 0`

Boundary flags remain closed: `production_subtitle_design_acceptance=false`,
`production_render_acceptance=false`, `creative_acceptance=false`,
`production_candidate=false`, `production_usage_allowed=false`,
`rights_status=pending`, `publishing_acceptance=false`, and
`public_use_permission=false`.

## Immediate Resume Capsule - 2026-06-16 Open Surface Sync

Fresh terminal setup:

```powershell
git fetch --prune origin
git checkout main
git pull --ff-only origin main
git status --short --branch
git rev-list --left-right --count HEAD...origin/main
git log -1 --oneline --decorate
git ls-files episodes
```

Expected state after pulling this handoff refresh:

- Branch: `main`
- Upstream: `origin/main`
- `HEAD...origin/main`: `0 0`
- `git ls-files episodes`: empty
- Latest implementation sync point before this docs-only handoff refresh:
  `f4f67cb chore: add review surface launchers`

Current open order:

1. `.\open-dashboard.ps1`
2. choose the artifact or doc from the dashboard
3. use the artifact-specific launcher only when needed:
   `.\open-artifacts.ps1`, `.\open-current-proof.ps1`, or
   `.\open-font-candidates.ps1`

Current active artifact is `clip-ed10g-noto-overlay-proof-001`.
`noto_sans_jp_clean_outline` is accepted as the current diagnostic /
representative subtitle base for `cut_002` / `cut_003` only. This consumed
human visual judgement as `accept_diagnostic_base`; it did not approve
production subtitle design, production render, creative quality, rights,
publishing, upload, or public use.

Tracked surfaces now holding the context:

| Surface | Purpose |
|---|---|
| `docs/RUNTIME_STATE.md` | current resume capsule and next route boundaries |
| `docs/index.md` | human-facing wiki entrance and open-surface order |
| `docs/dashboard/index.html` | generated project dashboard |
| `docs/dashboard/project-status.json` | machine-readable dashboard state |
| `docs/features/index.md` | generated feature progress table |
| `artifacts/ARTIFACTS.md` | artifact registry and open commands |
| `docs/SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md` | consumed ED-10g decision packet |
| `docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md` | ED-10h font candidate registry |

Latest launcher validation before this handoff refresh:

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\open-dashboard.ps1`
  opened `docs\dashboard\index.html`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\open-artifacts.ps1`
  opened `artifacts\ARTIFACTS.md`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\open-current-proof.ps1`
  opened the retained ignored ED-10g proof on this machine. In a fresh
  terminal without retained `episodes/` evidence, the expected behavior is a
  clear message pointing back to `.\open-dashboard.ps1` and
  `.\open-artifacts.ps1`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\open-font-candidates.ps1`
  parsed 19 font candidates and opened `docs\SUBTITLE_FONT_CANDIDATE_SWEEP.md`.
- `uvx pytest -q tests/test_docs_dashboard.py tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py`
  returned `21 passed, 8 skipped`.

Next useful routes are separate choices, not a reopening of the accepted
`cut_002` / `cut_003` base:

- Advance: create a dense/stress proof route for `cut_008` or another explicit
  target if representative coverage must widen.
- Audit: use dashboard doc-health findings to shorten or clarify
  `docs/RUNTIME_STATE.md`, `docs/FEATURE_REGISTRY.md`, or other high-friction
  docs.
- Explore: choose the ED-10h font route, either no-download local/system
  comparison or an explicitly approved download route with license metadata.
- Verify: run a separate limitation-lift route for production render,
  production subtitle design, rights, publishing, or public-use acceptance.

## Current Sync Point

- Branch: `main`
- Upstream: `origin/main`
- Latest synced base before this handoff refresh:
  `861cce8 (origin/main) feat: record ED-10g small adjustment route`.
  A fresh terminal should run `git fetch --prune origin`,
  `git checkout main`, and `git pull --ff-only origin main`, then confirm
  `git rev-list --left-right --count HEAD...origin/main` returns `0 0`.
- Latest active review state:
  SH-08 / `clip-human-preview-session-001` has consumed the human answer as
  `adjust_boundary`, not as production subtitle design acceptance. Font size is
  accepted only for the current diagnostic / representative route:
  `font_size=accepted_for_diagnostic_representative_review`. `font_family` and
  `decoration` remain unresolved and moved to ED-10g.
- Latest successor slice:
  `ED-10g: Subtitle Typography Decoration Comparison v0` is now the active
  narrow route. The tracked generator is
  `build-subtitle-typography-decoration-comparison`; the tracked decision
  packet is
  [SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md](SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md);
  the artifact registry entry is `clip-typography-decoration-comparison-001`
  in [../artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md).
- Latest ED-10g human response:
  `small_adjustment` is consumed for `clip-typography-decoration-comparison-001`.
  It preserves the accepted diagnostic font-size direction and keeps
  font-family / decoration unresolved until a concrete adjusted candidate is
  selected. The regenerated comparison JSON/HTML now separates
  `human_decision_readback.selected_response=adjust_boundary` from
  `comparison_response_readback.selected_response=small_adjustment` and writes
  `next_diagnostic_overlay_proof_route` for the next diagnostic overlay proof.
- Same-machine local proof generated before handoff:
  ignored
  `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison/`
  contains 4 candidates, 16 PNG samples, a contact sheet, JSON/HTML report,
  and `open_comparison.ps1`. On 2026-06-16 JST this checkout refreshed the
  artifact with the current tracked generator and confirmed
  `comparison_response_readback.selected_response=small_adjustment`,
  `next_diagnostic_overlay_proof_route.route_kind=small_adjustment_diagnostic_overlay_proof`,
  `font_size_policy.value=124`, and safe-area readback for all generated sample
  text boxes. This directory is not tracked. Another terminal can regenerate it
  with:

```powershell
uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_typography_decoration_comparison `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

- Open the local comparison artifact, when present, with:

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_typography_decoration_comparison\open_comparison.ps1
```

- Production / public boundaries after handoff remain unchanged:
  `production_subtitle_design_acceptance=false`,
  `production_render_acceptance=false`, `creative_acceptance=false`,
  `rights_status=pending`, `publishing_acceptance=false`, and
  `public_use_permission=false`. `episodes/` remains ignored and
  `git ls-files episodes` must remain empty.
- Current small-adjustment decision packet:
  [SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md](SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md)
  lists four narrow diagnostic routes and defaults the next proof base to
  `noto_sans_jp_clean_outline` unless the human chooses another font-family /
  decoration adjustment. `current_yu_gothic_heavy_outline` stays reference-only;
  `meiryo_bold_soft_shadow` and `gothic_high_contrast_minimal_badge` remain
  alternates. The next overlay proof should still target only `cut_002` /
  `cut_003` and must not reopen font size.
- Latest validation for this handoff refresh:
  `uvx pytest -q tests/test_episode_review_bundle.py tests/test_subtitle_overlay_visual_proof.py tests/test_subtitle_style_spike.py tests/test_episode_status.py`
  -> `17 passed, 8 skipped`; `git diff --check` clean; `git ls-files episodes`
  empty. The pushed branch should end with `HEAD...origin/main = 0 0`.
- Latest pushed sync point before this representative subtitle design readback
  refresh: `87eba6a docs: record cut003 diagnostic readability acceptance`;
  after pulling from another terminal, run `git log -1 --oneline --decorate`
  because this docs-only handoff refresh may be newer.
- Latest subtitle_style_spike review-surface hardening: the renderer spike is
  now guarded against false visual authority. `1a9410d` closes the grid audit
  with `grid_model=none`, `snap_to_grid=false`,
  `grid_visible_in_samples=false`, and
  `wrapping_authority=font_bbox_pixel_measurement_not_grid_cell_count`.
  `d00aff9` adds visible element authority classes
  (`computational_authority`, `measured_readback`, `visual_guide_only`,
  `placeholder`, `decorative`) and labels A/B speaker badges as placeholders,
  not real face icons or final speaker identity design. `e3bdf3b` splits clean
  default samples from explicit guide-overlay samples for subtitle/face-icon
  review aids. `505a33d` adds `measured_bbox_provenance`, `style_inputs`,
  `computed_layout`, and `measured_output`, with deterministic two-run bbox
  readback. `87afbfd` records that local report images use sibling relative PNG
  refs; open the HTML directly from the local filesystem, not through a
  translation/proxy surface, when checking image rendering.
- Latest completed feature slice: `ED-10` official subtitle track import / transcript alignment. It adds `import-subtitle-track`, currently for YouTube JSON3 subtitle tracks, and writes transcript-compatible artifacts with `stt.engine="subtitle_track"`.
- Latest completed diagnostic slice: `JP-Pilot-01R3` official-caption rerun. It imported the official Japanese subtitle track for the ignored JP-Pilot episode, produced 105 transcript segments, regenerated 9 selected cuts, 105 subtitle drafts, NLE CSV 9 rows, and a 6.84s 1080p diagnostic render.
- Latest completed operator UX slice: `SH-07` operator review UX separation. It adds `docs/OPERATOR_REVIEW_UX.md`, moves restart/report order to Reviewability first, places recovery/reproduction commands in appendix/details, adds `operator_review` readback to `status-episode`, and keeps natural-language cut review acceptable before any structured decision patch.
- Latest completed chapter revision slice: `ED-10b` Chapter Revision Loop v0. It adds `build-chapter-revision-board`, `src/pipeline/chapter_revision_board.py`, `docs/CHAPTER_REVISION_LOOP.md`, `docs/SCHEMAS/v1/chapter_revision_patch.md`, and tests. It generates a static board plus JSON/CSV patch templates from existing R3 review artifacts.
- Latest completed cut decision slice: `ED-10c` R3 Cut Decision Packet. It adds `build-cut-decision-packet`, `src/pipeline/cut_decision_packet.py`, and `status-episode.final_cut_decision` readback. The current R3 triage is `keep`: `cut_001`, `cut_002`, `cut_003`; `needs_adjustment`: `cut_004`-`cut_008`; `reject`: `cut_009`.
- Latest completed proxy decision slice: `ED-10d` cut_002/cut_003 proxy decision handoff generator. Commit `21f7792 feat: add R3 proxy decision handoff generator` adds `build-operator-proxy-decision-handoff`, `src/pipeline/operator_proxy_decision_handoff.py`, and tests. It regenerates text/proxy review, operator proxy decision handoff, and scoped Chapter Revision Patch templates from tracked code instead of relying on unreproducible local-only handoff files.
- Latest local evidence slice: scoped subtitle-overlay visual proof for explicit target cuts `cut_002` / `cut_003`. Local ignored `subtitle_overlay_visual_proof_report.*`, target cut proof MP4/PNG artifacts, subtitle-bearing sample frames, and refreshed `representative_visual_proof_report.*` exist under the R3 review directory. The accepted current cut_003 proof/readback is `22.606 -> 49.566` with `sub_010..sub_029`, response/referral block `sub_025..sub_029` included, and `sub_030` excluded. The latest Subtitle Design / Review UX probe adds [SUBTITLE_PRESENTATION_CONTRACT.md](SUBTITLE_PRESENTATION_CONTRACT.md) (`jp_clip_dialogue_reference_v0`) and updates cut_003 to the diagnostic ASS candidate `jp_clip_dialogue_badge_left_v0`: `ClipPipeSpeakerBadge` plus `ClipPipeDialogueLeft`, formula-based `badge_left_dialogue` layout from the probed 1920x1080 frame (`font_size=124`, `outline=12`, `bottom_margin=97`, `horizontal_margin=106`, `badge=124x87`, `badge_text_gap=37`, `line_height=143`), left-aligned dialogue beside a speaker badge placeholder, replacement-style timing, and early/middle/response-referral/final sample frame extraction. Left alignment is conditional to the `badge_left_dialogue` mode rather than universal; `bottom_center_emphasis` remains supported in contract/readback. Real face icon assets are not present in the current material ledger, so the preferred non-POV face-icon pattern is explicitly approximated with a fallback. SRT text stays in `subtitle_overlay_reference/` as reference-only material so VLC does not auto-display a same-basename sidecar SRT. Previous proof artifacts are archived under the same reference directory for comparison. This remains diagnostic-only and not production subtitle design acceptance.
- Latest limited human acceptance: human review accepted the current `cut_003`
  diagnostic burned-in subtitle proof readability baseline for diagnostic
  review only. Record this as
  `diagnostic_subtitle_wrapping_readability_acceptance=true` for `cut_003`.
  The accepted scope is limited to current cut_003 diagnostic burned-in proof
  readability. It does not accept production subtitle design, production
  render, creative quality, rights approval, publishing, or public use. The
  boundary flags remain `production_subtitle_design_acceptance=false`,
  `production_render_acceptance=false`, `creative_acceptance=false`,
  `rights_status=pending`, `production_candidate=false`,
  `production_usage_allowed=false`, `publishing_acceptance=false`, and
  `public_use_permission=false`.
- Limitation-lift conditions after this diagnostic acceptance: production
  subtitle design acceptance requires representative subtitle design review
  across relevant cuts/scenes, including font, size, outline, color, speaker
  identity, mode selection, and safe area. Production render acceptance requires
  final render-path output review, not only diagnostic proof. Creative
  acceptance requires whole-video or representative-sequence editorial review.
  Rights approval requires explicit rights/material-use clearance.
  Publishing/public-use permission requires both production acceptance and
  rights approval.
- Latest representative subtitle design review / kept-cut Verify:
  [REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md](REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md)
  selects `cut_002`, `cut_003`, and `cut_008` as the smallest representative
  set. The same-machine ignored artifacts now include a Pillow-enabled combined
  `subtitle_overlay_visual_proof_report.*` for `cut_002` and `cut_003` with
  `target_cuts=[cut_002, cut_003]`, `all_target_cuts_have_overlay=true`,
  `jp_clip_dialogue_badge_left_v0`, explicit ASS line breaks, font-bbox
  wrapping readback, visible `renderer_gap`, `production_candidate=false`,
  `rights_status=pending`, and `production_subtitle_design_acceptance=false`.
  The current contract is representative-review-ready for the already-kept
  proof surfaces `cut_002` and `cut_003` only. `cut_003` remains the accepted
  diagnostic baseline only; `cut_008` is still blocked by `needs_adjustment`
  and missing representative proof.
- Latest local proxy decision handoff: ignored `cut_002_cut_003_text_proxy_review.json` / `.html`, `cut_002_cut_003_operator_proxy_decision_handoff.json` / `.html`, and scoped `chapter_revision_patch.cut_002_cut_003_proxy.template.json` / `.csv` exist. Source media is available from `material_ledger.json` material paths. The regenerated handoff reads `visual_proof_status=available_requires_human_review`; `proxy_decision` now includes `proceed_with_limitations` for candidate routing with visible limitations/watch items; templates remain blank/default. The accepted filled operator patch is stored separately as `chapter_revision_patch.cut_002_cut_003_proxy.operator.json` / `.operator.csv` / `.operator.html` and is the current local decision authority for cut_003; `cut_003` retained context risk remains active.
- Latest boundary recommendation applier: `ED-10e` adds `apply-boundary-recommendation`, which validates an operator-owned boundary recommendation against `edit_pack.json` and writes a dry-run/blocking/apply receipt. Mutation remains explicit only: `--apply --overlap-policy shrink_or_split_cut_004 --transcript`. The current same-machine ignored JP-Pilot edit_pack has applied `cut_003` `22.606 -> 49.566`, shrunk `cut_004` to `50.868 -> 60.277`, moved `sub_025..sub_029` to `cut_003`, and kept `sub_030` on `cut_004`. Transcript, official subtitle evidence, source media, typography, proof, and render were not mutated.
- Latest local downstream refresh after ED-10e: the same-machine ignored artifact set now has regenerated context/review/evidence/decision/chapter/proxy/NLE readbacks for the applied `cut_003` boundary. `cut_003` is `22.606 -> 49.566`, owns `seg_000010..seg_000029` and `sub_010..sub_029`, and remains `context_status=needs_review` / `retained_context_risk=true` / `final_cut_decision=keep`. `cut_004` is `50.868 -> 60.277`, owns `seg_000030..seg_000034` and `sub_030..sub_034`, remains `final_cut_decision=needs_adjustment`, and keeps `resegmentation_target=true`. The ED-06 NLE export has been regenerated and its CSV/report title/reason now matches these current ranges after an ignored-only `edit_pack.reason` cleanup.
- Latest Review Contract Taxonomy audit: [CUT_003_REVIEW_CONTRACT_TAXONOMY_AUDIT.md](CUT_003_REVIEW_CONTRACT_TAXONOMY_AUDIT.md) preserves the current audit surface. The regenerated cut_003 proof/readback matches current authority (`22.606 -> 49.566`, `sub_010..sub_029`, `sub_025..sub_029` included, `sub_030` excluded), and the required proof-level gates passed with `blocking_limitations=none_detected`. Human review accepted clip length and scene closure for diagnostic candidate review only.
- Latest cut_003 operator decision closure: the filled `.operator.*` patch reads `cut_003.proxy_decision=proceed_with_limitations`, `cut_003.context_risk_handling=keep_retained_risk_visible`, `boundary_request=none`, `analyst_action=noop`, and `downstream_target=none`. It records `subtitle_visual_readability=needs_adjustment`, `embedded_subtitle_too_small_for_youtube=true`, `sidecar_srt_player_display_can_confuse_review=true`, `source_timeline_context_preview_requested=true`, and `production_subtitle_design_acceptance=false`. `cut_002` remains unchanged; scoped `.template.*` files remain blank/default.
- The ignored `.operator.*` patch was not mutated. Its older
  `subtitle_visual_readability=needs_adjustment` remains a historical operator
  patch field, while the tracked docs now record a later, separate human review
  result for the current diagnostic burned-in proof readability baseline only.
  This separate acceptance does not reopen the cut boundary or change the
  operator decision.
- Latest subtitle renderer / typography measurement spike: commit `f6fcf5b feat: add subtitle typography measurement spike` adds [SUBTITLE_RENDERER_TYPOGRAPHY_SPIKE.md](SUBTITLE_RENDERER_TYPOGRAPHY_SPIKE.md), `src/integrations/render/subtitle_style_spike.py`, and `tests/test_subtitle_style_spike.py`. Later commits harden the same spike so the report distinguishes actual layout authority from measured readback, visual guide overlays, placeholders, and decorative aids. The report records 16 clean review samples plus explicit guide-overlay samples, bbox and safe-area readback, `review_only=true`, `production_candidate=false`, and `production_compatible=false`. `来ねぇ！！` should be considered `reaction_caption` / `bottom_center_emphasis` first, not ordinary `dialogue_badge_left`. ASS/libass remains the existing diagnostic proof path; Pillow/PNG remains review-only measurement support and is not claimed to match YMM4, Premiere, ASS, or FFmpeg production rendering.
- Current recommended decision: treat cut_003 boundary, operator decision, and
  current diagnostic burned-in proof readability as closed for this diagnostic
  baseline. The next work should choose a limitation-lift route instead of
  re-judging the same proof: representative subtitle design review across
  cuts/scenes, final render-path output review, whole-video or
  representative-sequence editorial review, or explicit rights/material-use
  clearance. A fresh checkout or workspace missing ignored artifacts may still
  report `review_blocked_missing_artifacts`; either state remains
  diagnostic-only and not production, creative, publishing, or rights
  acceptance.
- Next human review answers to collect are now limitation-lift answers:
  whether representative subtitle design across relevant cuts/scenes is
  accepted, whether final render-path output is accepted, whether whole-video
  or representative-sequence editorial quality is accepted, and whether
  explicit rights/material-use clearance exists. These answers must not be
  inferred from the current cut_003 diagnostic proof.
- JP-Pilot-01 rights note: the ignored episode now has source / talent / disclosure readback and no schema issues, but rights approval remains pending and publishing / production acceptance is still out of scope.
- Current pushed implementation resume point before this representative
  subtitle design readback refresh:
  `87eba6a docs: record cut003 diagnostic readability acceptance`, with
  `HEAD`, `origin/main`, and `origin/HEAD` aligned in this workspace before this
  docs refresh. A later docs-only handoff commit may be newest; use
  `git log -1 --oneline --decorate` after pulling for the exact current HEAD.
- Verified base after this refresh: `git status --short --branch` -> `## main...origin/main`; `git rev-list --left-right --count HEAD...origin/main` -> `0 0`; `git ls-files episodes` empty.
- Previous pushed resume point: `cfd3cb4 Merge remote-tracking branch 'origin/main'`.
- Latest implementation slice before ED-10: ED-09 done。`review-transcript` CLI と pipeline patch 適用、`status-episode` review readback、`export-nle` warning 更新、docs registry 更新を含む
- Previous feature slice: `JP-Pilot-01` Japanese public VOD diagnostic
  1. `transcribe-audio --engine vosk --language ja --model vosk-model-small-ja-0.22` は language/model check passed で 26 segments を生成
  2. `generate-cuts` は 6 selected cuts、`check-cut-context` は 3 passed / 3 needs_review、`generate-subtitles` は 17 real_transcript subtitle drafts
  3. `render-tiny-proof --burn-in-subtitles diagnostic` は 6.6s / 1080p render、`export-nle` は 6 CSV rows、`audit-material-ledger` は ok
- Previous recommendation resolved by ED-10 / JP-Pilot-01R3: official subtitle events can now enter the transcript/cuts/subtitle/NLE/render pipeline without being constrained to Vosk segment coverage.
- Latest completed feature-slice closeout before this handoff note: ED-07c language/model validation closeout
- Latest local verification: 2026-06-01 JST Chapter Revision Loop closeout; `uvx pytest -q` (206 passed), `npm run smoke` OK, `npm run smoke:electron` OK, `git diff --check` clean, `git ls-files episodes` empty. Staged-path guard before commit found no `episodes/`, rendered video, source media, subtitle payloads, `.json3`, rights payload, or large binary paths.
- Latest scoped visual proof validation: 2026-06-07 JST; `uvx python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --format json` regenerated the local ignored subtitle-overlay proof. Readback confirmed `source_media_status=available_from_material_ledger`, `style_direction_preset=jp_clip_readable_v1`, `subtitle_overlay_available_count=2`, `all_target_cuts_have_overlay=true`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`. HTML readback embeds or directly links the contact sheet plus proof PNG/MP4 artifacts.
- Latest proxy handoff validation: 2026-06-07 JST; `uvx python -m src.cli.main build-operator-proxy-decision-handoff --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --format json` regenerated the local ignored `cut_002` / `cut_003` text/proxy review, operator proxy handoff, and scoped patch template. JSON and CSV readback confirmed `source_media_status=available_from_material_ledger`, `visual_proof_status=available_requires_human_review`, `style_preset=jp_clip_readable_v1`, `proxy_decision.allowed_values` includes `proceed_with_limitations`, template defaults still blank/undecided, `cut_003.context_status=needs_review`, `cut_003.retained_context_risk=true`, `production_candidate=false`, and `rights_status=pending`. `uvx pytest -q tests/test_operator_proxy_decision_handoff.py` -> 2 passed, and `git ls-files episodes` remained empty. On this Windows workspace, prefer `uvx python -m ...` if bare `python` resolves to the WindowsApps shim.
- Latest boundary recommendation validation: 2026-06-07 JST; `uvx python -m src.cli.main apply-boundary-recommendation --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --recommendation-report episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\cut_003_boundary_recommendation_report.json --cut-id cut_003 --output-receipt episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\cut_003_boundary_apply_receipt.shrink_or_split_cut_004.json --apply --overlap-policy shrink_or_split_cut_004 --format json` wrote ignored receipt JSON/HTML with `status=applied`, `selected_policy=shrink_or_split_cut_004`, `edit_pack_mutated=true`, `cut_003=22.606->49.566`, `cut_004=50.868->60.277`, `sub_025..sub_029 -> cut_003`, `sub_030 -> cut_004`, `transcript_not_mutated=true`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`. `uvx pytest -q tests/test_boundary_recommendation_apply.py` -> 9 passed; `validate-edit-pack` -> `schema_ok=true`.
- Latest sync/readiness validation: 2026-06-07 JST in this workspace; `git rev-list --left-right --count HEAD...origin/main` -> `0 0` before this local refresh; `status-episode` -> `operator_review.review_ready=true`, `reviewability=review_ready`, no missing review artifacts, `rights_status=pending`, `production_candidate=false`, keep cuts `cut_001`, `cut_002`, `cut_003`; `uvx pytest -q` -> 217 passed; `npm run smoke` -> OK; `npm run smoke:electron` -> OK; `git diff --check` clean aside from CRLF warnings; `git ls-files episodes` empty. This readiness depends on ignored local artifacts and must be rechecked on fresh checkout or another workspace.
- Latest local NLE reason/readback validation: 2026-06-08 JST; `uvx python -m src.cli.main export-nle --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --output-dir episodes\jp_pilot01_hololive_bancho_20260525\exports\jp_pilot01r3_subtitle_import --format json` regenerated ignored `nle_cut_list.csv`, `nle_export_manifest.json`, and `nle_export_report.html` after updating only `cut_003` / `cut_004` `edit_pack.reason` text. CSV readback confirmed `cut_003=22.606->49.566`, `source_segment_ids=seg_000010..seg_000029`, `subtitle_ids=sub_010..sub_029`; `cut_004=50.868->60.277`, `source_segment_ids=seg_000030..seg_000034`, `subtitle_ids=sub_030..sub_034`; `production_edit_candidate=false`. `git ls-files episodes` remained empty.
- Latest taxonomy/operator validation: 2026-06-09 JST; parsed the filled `chapter_revision_patch.cut_002_cut_003_proxy.operator.json`, `.operator.csv`, and `.operator.html`, plus the scoped template `.template.json` / `.template.csv`. Readback confirmed the accepted cut_003 proxy decision, retained context risk handling, subtitle readability limitation, sidecar SRT review-confusion note, source timeline context preview request, cut_002 unchanged state, and blank/default templates.
- Latest subtitle design / review UX validation: 2026-06-09 JST; `build-subtitle-overlay-visual-proof --target-cut cut_003 --format json` regenerated ignored local cut_003 proof/readback with `renderer=ffmpeg_subtitles_filter_ass`, `subtitle_presentation_contract.contract_id=jp_clip_dialogue_reference_v0`, `style_candidate_id=jp_clip_dialogue_badge_left_v0`, formula-based `font_size=124`, `outline=12`, `alignment=speaker_badge_left_aligned_dialogue`, `left_alignment_is_universal=false`, `speaker_identity_presentation.fallback_used=true`, `sample_frame_selection.includes_response_referral_block=true`, reference-only SRT under `subtitle_overlay_reference/`, same-basename `.srt` absent, previous proof artifacts linked for comparison, `production_subtitle_design_acceptance=false`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`. Targeted tests for the formula slice: `uvx pytest -q tests/test_subtitle_overlay_visual_proof.py` -> 3 passed.
- Latest subtitle renderer spike validation: 2026-06-10 JST; targeted checks across the grid audit, visible element authority guardrail, guide overlay split, bbox provenance, and local image-path audit confirmed JSON/HTML readback for authority classifications, placeholder A/B badges, visual-guide-only overlays, measured bbox provenance, deterministic two-run measurement, and sibling PNG refs. Validation included `uvx --with pillow pytest -q tests/test_subtitle_style_spike.py` -> 2 passed, `uvx pytest -q tests/test_subtitle_style_spike.py -rs` -> 1 passed / 1 intentional Pillow skip, `git diff --check` clean, and `git ls-files episodes` empty. Ignored regenerated local artifacts under `episodes/` and `_tmp/` must remain uncommitted.
- Working tree expectation after pull: clean

## Non-Repo Artifact Handoff

JP-Pilot R3 の `rendered_video.mp4` は diagnostic artifact であり、Git に含めない。別端末へ引き継ぐときは、動画本体ではなく `build-non-repo-handoff` が出す manifest/report で local path、size、sha256、source identity、再生成 command、rights/production boundary、missing 時の扱いを確認する。手順の正本は [NON_REPO_ARTIFACT_HANDOFF.md](NON_REPO_ARTIFACT_HANDOFF.md)。

R3 の既定出力先は ignored local episode 配下の `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/non_repo_artifact_handoff.json` と `non_repo_artifact_handoff.html`。fresh checkout に動画や ignored episode が無い場合は missing として扱い、manifest の regeneration command と dependency artifacts が揃うまで production / creative / publish acceptance へ進めない。

別端末の意味は三つに分ける。same machine / same workspace では ignored `episodes/` が残っていれば照合できる。different machine では Git 外の許可された transfer 経路で episode artifacts を移した場合だけ hash / size / source identity を照合できる。fresh checkout only では generator / schema / docs / tests だけがあり、R3 固有 manifest/report、`rendered_video.mp4`、source media、subtitle track、render manifest は無いので、必要な upstream artifacts が揃うまで missing のまま扱う。

R3 source identity readback は YouTube ID `7J5aS_pcBj4`、subtitle track `source_subs/7J5aS_pcBj4.ja.json3`、transcript source `imported subtitle track / youtube_subtitles`、source video material id `src_video_jp_pilot01`、source audio material id `src_audio_jp_pilot01`、rights status `pending`、production usage `not allowed until rights approval`。title / URL が local metadata に無い場合は `unknown` とし、外部検索や新規 download で埋めない。

## Chapter Revision Loop v0

Chapter Revision Loop v0 is now the current operator decision surface for
JP-Pilot R3. It prevents the review packet from becoming a read-only ledger:
the operator can write chapter-level intent, script/display subtitle requests,
boundary requests, rollback signals, analyst actions, downstream targets, and
notes into a machine-readable patch template.

Generated ignored local artifacts, when the R3 review directory is present:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_board.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_board.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_patch.template.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_patch.template.csv
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_patch.example.json
```

The tracked generator is reproducible:

```powershell
python -m src.cli.main build-chapter-revision-board `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

The board no longer requires downstream acceptance enrichment artifacts before
operator input can start. `regenerated_r3_baseline_acceptance.*` and
`production_subtitle_render_acceptance_plan.*` are optional: if they are
missing while the cut review packet, evidence summary, non-repo handoff, and
speed-first decision artifacts are present, the generator writes
`chapter_revision_board.*` and patch templates with
`board_status=generated_with_warnings` plus `missing_optional_artifacts[]`.
This is still an operator input surface only; it does not create production
subtitle/render acceptance, rights approval, publishing acceptance, or a
production candidate.

Current R3 board readback:

| Item | State |
|---|---|
| chapter mapping | `cut_001`-`cut_009` map to `ch_001`-`ch_009` |
| current decision | `keep=3`, `needs_adjustment=5`, `reject=1`; `cut_decision_packet` is the current decision source |
| speed pass role | `cut_decision_speed_pass` is historical candidate-seed evidence only and must not override current timing/decision readback |
| retained risk | 6 original `needs_review` cuts remain `retained_context_risk=true` |
| representative roles | `cut_009=short_passed_representative`, `cut_004=retained_context_risk_representative`, `cut_008=dense_subtitle_representative` |
| operator defaults | blank strings, `undecided`, `boundary_request=none`, `downstream_target=[]` |
| boundary flags | `production_candidate=false`, `creative_acceptance=false`, `publish_acceptance=false`, `rights_status=pending` |

Important separation: source transcript and official subtitle track remain
evidence. `script_override` is editorial layer only,
`display_subtitle_request` is subtitle surface request, and boundary changes
are later `edit_pack` / cut-range requests. Do not add a source transcript
mutation field to the patch. The Agent must not invent creative intent or fill
`script_override` on behalf of the operator.

## R3 Cut Decision Packet

R3 Cut Decision Packet is the current bridge from broad candidate seeds to the
next explicitly selected limitation-lift slice. It writes the final cut
decision readback into ignored local artifacts:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_packet.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_report.html
```

The tracked generator is reproducible:

```powershell
python -m src.cli.main build-cut-decision-packet `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

Current R3 decision readback:

| Cut group | State | Why it matters |
|---|---|---|
| `cut_001`, `cut_002`, `cut_003` | `keep` | These are the only candidate cuts to carry into the next selected limitation-lift slice. |
| `cut_004`-`cut_008` | `needs_adjustment` | Context risk, boundary continuity, or subtitle density must be resolved before promotion. |
| `cut_009` | `reject` | Short, dependent closing beat; not useful for this 1-3 candidate pass. |

`cut_003` is the only kept cut whose original context status is
`needs_review`. The packet records an explicit manual override reason and keeps
the risk visible. This packet is not production acceptance, not rights approval,
not publishing acceptance, and does not set `production_candidate=true`.

## Kept Candidate Visual Proof

The current scoped visual proof mini-slice has local ignored readback reports:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/production_subtitle_render_acceptance_report.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/production_subtitle_render_acceptance_report.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_002.mp4
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_002.png
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_002.srt
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_003.mp4
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_003.png
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_cut_003.srt
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/visual_proof_cut_001.png
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/visual_proof_cut_002.png
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/visual_proof_cut_003.png
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/visual_proof_contact_sheet.png
```

In this same-machine workspace, the representative proof set is present and
`status-episode` reports `operator_review.review_ready=true`. Fresh checkouts
or workspaces missing ignored `episodes/` artifacts must still remain blocked
until the missing proof is restored/regenerated or explicitly waived.

Current visual proof readback:

| Cut | Proof source | Current meaning |
|---|---|---|
| `cut_001` | local representative visual proof frame present in this workspace | Keeps the global R3 review surface open here; still diagnostic only. |
| `cut_002` | regenerated diagnostic subtitle-overlay frame with `jp_clip_readable_v1` style direction readback | Available for human visual inspection only; `needs_wrap_watch=1` is a watch item, not automatic wrapping acceptance. |
| `cut_003` | regenerated diagnostic subtitle-overlay frame with `jp_clip_readable_v1` style direction readback | Available for human visual inspection only; retained context risk remains active. |

The visual proof reports keep `production_render_executed=false`,
`new_diagnostic_render_executed=true`, `production_candidate=false`,
`creative_acceptance=false`, `publish_acceptance=false`,
`rights_status=pending`, and `production_usage_allowed=false`. The PNGs and
reports are local ignored artifacts and must not be staged. The style direction
readback is a review contract for the diagnostic proof, not production subtitle
design acceptance.

## cut_002 / cut_003 Proxy Decision Handoff

The `cut_002` / `cut_003` kept cuts have a narrower local handoff so the
operator can decide how to route them without filling the whole Chapter
Revision Board. Generated ignored local artifacts:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_text_proxy_review.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_text_proxy_review.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_operator_proxy_decision_handoff.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_operator_proxy_decision_handoff.html
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_patch.cut_002_cut_003_proxy.template.json
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_patch.cut_002_cut_003_proxy.template.csv
```

The tracked generator is reproducible:

```powershell
uvx python -m src.cli.main build-operator-proxy-decision-handoff `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

Current proxy readback:

| Cut | Proxy state | Operator decision | What remains unresolved |
|---|---|---|---|
| `cut_002` | context `passed`, compact 4.838s setup beat, 2 subtitles, long-line watch visible | `proxy_decision=proceed_with_limitations`; no subtitle adjustment requested in this slice | watch item remains visible; no production subtitle/design/render acceptance |
| `cut_003` | text/timing/proof readback is current at `22.606 -> 49.566` with `sub_010..sub_029`, response/referral block `sub_025..sub_029` included, and `sub_030` excluded | accepted filled patch: `proxy_decision=proceed_with_limitations`; `context_risk_handling=keep_retained_risk_visible` | retained context risk remains visible; subtitle design/readability is `needs_adjustment`; no production subtitle/design/render acceptance |

Source media is present by material ledger readback:

```text
episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4
episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav
```

The old root-level paths `episodes/.../source_video.mp4` and
`episodes/.../source.wav` are not the current source of truth. The proxy
handoff was regenerated after the scoped style-direction proof refresh and now
reads back the diagnostic style preset and EAW line-width watch status from
`representative_visual_proof_report.html`. The proxy handoff still does not
pass typography, safe-area, timing sync, creative acceptance, production
acceptance, publishing acceptance, or rights approval.

The filled operator patch is intentionally separate from the blank/default
template files. Use
`chapter_revision_patch.cut_002_cut_003_proxy.operator.json`,
`chapter_revision_patch.cut_002_cut_003_proxy.operator.csv`, or
`chapter_revision_patch.cut_002_cut_003_proxy.operator.html` for the current
cut_003 decision readback in this same-machine workspace. Do not overwrite the
`.template.*` files with the filled decision.

The tracked ED-10e dry-run receipt command is:

```powershell
uvx python -m src.cli.main apply-boundary-recommendation `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json `
  --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json `
  --recommendation-report episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\cut_003_boundary_recommendation_report.json `
  --cut-id cut_003 `
  --output-receipt episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\cut_003_boundary_apply_receipt.shrink_or_split_cut_004.json `
  --apply `
  --overlap-policy shrink_or_split_cut_004 `
  --format json
```

Current receipt readback is `status=applied`,
`selected_policy=shrink_or_split_cut_004`, `edit_pack_mutated=true`,
`cut_003=22.606 -> 49.566`, `cut_004=50.868 -> 60.277`,
`sub_025..sub_029 -> cut_003`, `sub_030 -> cut_004`,
`transcript_not_mutated=true`, `production_candidate=false`,
`rights_status=pending`, and `production_usage_allowed=false`. Context,
review/evidence, cut decision, chapter board, scoped proxy handoff, and NLE
export have now been regenerated from this ignored local edit pack. The
regenerated cut_003 proof/readback and taxonomy audit now match the current
`22.606 -> 49.566` authority. Treat stale `candidate_reason` prose in
`cut_review_packet.json` /
`cut_decision_packet.json` as a remaining narrow cleanup item if those fields
will be human-facing.

After the 2026-06-09 operator decision closure, treat the filled
`chapter_revision_patch.cut_002_cut_003_proxy.operator.*` artifacts as the
same-machine local authority for the narrow cut_003 proxy route. The decision
keeps retained context risk visible and keeps subtitle production design
unaccepted.

## Resume on another terminal

```powershell
git checkout main
git pull --ff-only origin main
# read these to pick up state:
#   docs/HANDOFF.md
#   docs/RUNTIME_STATE.md
#   docs/CHAPTER_REVISION_LOOP.md
#   docs/SCHEMAS/v1/chapter_revision_patch.md
#   docs/RUNTIME_HISTORY.md  # history/archive only; not the active resume surface
#   docs/HOLOEN_PILOT.md  # HoloEN-01 runbook / URL selection / acceptance
#   docs/FEATURE_REGISTRY.md
```

HoloEN-01 and JP-Pilot-01 are already done. For another fresh pilot, assistant may self-select a low-risk public VOD following the same exclusion rules documented in `docs/HOLOEN_PILOT.md` and `docs/JP_PILOT.md`, or operator may supply a URL explicitly.

Resume command:

```powershell
git checkout main
git pull --ff-only origin main
```

## What Is Now Done

INT-02e is complete. `fetch-source-audio --mode yt-dlp-audio` is limited to source-audio URL fetch only:

- yt-dlp runs only inside `src/integrations/asset_fetch/yt_dlp_audio.py`.
- FFmpeg still only normalizes the downloaded temporary media to `source.wav`.
- The downloaded intermediate is not retained.
- The receipt records yt-dlp + FFmpeg tools, download / normalize command summaries, source URL readback, output hash/duration, rollback files, and rights snapshot.
- Rights status is readback only and `hard_gate=false`.

Technical operator smoke used ignored episode `episodes/int02e_operator_smoke_20260512` and material `src_audio_ytdlp_001`. It generated `source.wav`, `sidecar.json`, `fetch_receipt.json`, and a `material_ledger.json` entry. The smoke URL is not creative acceptance or publishing approval.

SH-05d is complete. `build-local-preview-pack --use-existing-source-audio` consumes an existing `source_audio` material entry without re-downloading source media:

- The bridge resolves `source.wav` and `sidecar.json` from `material_ledger.json`.
- It detects sibling `fetch_receipt.json` and adds receipt / sidecar / ledger references to `preview_manifest.json`.
- The report adds `Source Audio Provenance` with mode, provider, command summary, source URL/local path, tool versions, rights snapshot, intermediate retention, and output hash.
- Fake / fixture transcript and the generated `edit_pack.json` are explicitly marked as preview-only, not production candidates.
- GUI Preview Pack ingest remains read-only; it can validate the new manifest fields and artifact links but does not run build, fetch, render, upload, or network/external acquisition workflows.
- Closeout smoke used ignored reproducible episode `episodes/sh05d_existing_source_audio_smoke_20260512`. It proves the bridge behavior without network / downloader. The original ignored INT-02e real smoke episode was not present locally, so a real INT-02e artifact smoke remains pending until those artifacts are regenerated or restored.

ED-06 is complete as a minimal external editing handoff. `export-nle` consumes `edit_pack.json` and writes a CSV cut list plus readback files:

- The chosen export format is `csv_cut_list_v1`, backed by `nle_cut_list.csv`.
- The export includes cut id, selected state, title/reason, start/end/duration seconds, source type, confidence, context status, source segment ids, subtitle ids/text/ranges, and source audio refs.
- When a sibling or explicit `preview_manifest.json` exists, the export carries source audio provenance such as provider, mode, source URL, output hash, and rights status snapshot.
- `nle_export_manifest.json` and `nle_export_report.html` read back the generated artifact paths and warnings.
- Fake / fixture transcript derived exports keep `production_edit_candidate=false` and warning text; the output can leave ClipPipeGen for external review, but it is not production edit acceptance.

ED-07b is complete as a real transcript plumbing proof. `transcribe-audio --engine vosk` is an optional local STT path that consumes an existing `source.wav` and writes a `transcript.json` with provider/model/source-audio readback:

- The adapter lives under `src/integrations/stt/` and is optional; Vosk and its model are not vendored into the repo.
- `transcribe-audio --dry-run --format json` preflights provider importability, model directory, and mono 16-bit PCM WAV shape. Missing provider/model is an explicit failure, not a fallback to fixture data.
- `transcript.json` now records `stt.provider`, `stt.model`, `stt.real_transcript`, `stt.segment_count`, top-level `segment_count`, and source audio duration/sample rate/channel readback when available.
- The same transcript feeds `generate-cuts`, `check-cut-context`, `generate-subtitles`, and `export-nle`.
- ED-06 export now reads sibling or explicit `transcript.json` and carries transcript provider/engine/model/real flag/segment count/duration into CSV, manifest, and HTML report.
- This is still not STT quality, creative edit, rights, render, or publishing acceptance. Real transcript output remains draft/unreviewed unless a human review slice marks it otherwise.

INT-02f is complete as local source video acquisition. `fetch-source-video --mode local-media-video` consumes an existing local video file, copies it into the episode material directory, and records provenance plus technical metadata:

- The output file is `materials/<material_id>/source_video.<ext>`; the input extension is preserved.
- The command writes `sidecar.json`, `fetch_receipt.json`, and a `material_ledger.json` entry with `kind="source_video"`, `subkind="source_video_original"`, and `intended_uses=["editing_video"]`.
- FFprobe metadata is read back into receipt and sidecar: duration, container, video codec, audio codec if present, resolution, fps/frame_rate, and stream counts.
- Rights status is stored as a snapshot with `hard_gate=false`; pending rights and smoke/local fixture materials are not production/creative/publish acceptance.
- This is not render/encode. It does not cut, concat, burn subtitles, add a GUI fetch button, fetch URL video, or publish.

OUT-01 is complete as a tiny diagnostic render proof. `render-tiny-proof` consumes an existing `source_video` material, a `source_audio` material, and `edit_pack.json`, then writes a short rendered artifact plus readback files:

- The output directory is `episodes/<episode_id>/renders/<output_id>/`.
- The rendered file is `rendered_video.mp4` by default, with `.mkv` available when the environment needs it.
- The command writes `render_receipt.json`, `render_manifest.json`, and `render_report.html`.
- Timeline mapping uses the first selected cut from `edit_pack.json`; if the cut range exceeds source video/audio duration or `--duration-sec`, it clamps to the shortest available diagnostic range and records warnings.
- Output metadata is probed with FFprobe: duration, container, video codec, audio codec, resolution, fps, and stream counts.
- This is not production render, creative acceptance, subtitle burn-in, GUI render action, URL video fetch, or publishing.

OUT-01a is complete as render preflight / fallback readback hardening. The same `render-tiny-proof` output path now makes failure diagnosis visible instead of only proving one successful render:

- FFmpeg and FFprobe are discovered and version-checked before render; missing tools classify as `environment_missing_ffmpeg` / `environment_missing_ffprobe`.
- Auto render profiles prefer `mp4 / libx264 / aac`, then codec fallback, with `mkv` fallback candidates preserved in the command plan.
- Each attempted profile records status, selected flag, failure reason, command summary, and stderr digest in receipt / manifest.
- Failed render attempts after context resolution still write `render_receipt.json`, `render_manifest.json`, and `render_report.html` with `failure_classification`.
- Fresh ignored smoke episode `episodes/out01a_hardened_smoke_20260513` regenerated `renders/out01a_hardened/rendered_video.mp4`; output readback was duration `2.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `160x90`, fps `15.0`, stream count `2`.
- This remains diagnostic render subsystem hardening, not production render, creative acceptance, subtitle burn-in, URL video acquisition, GUI render action, or publishing.

OUT-01b is complete as a longer local video render smoke. It keeps the OUT-01a render path and uses local fixture media to exercise duration / stream / timeline mapping without adding URL video acquisition or subtitle burn-in:

- Fresh ignored smoke episode `episodes/out01b_long_local_render_smoke_20260513` uses synthetic local input `_tmp/out01b_long_local_input.mp4` and registers source video material `src_video_out01b_long_local`.
- Source video readback: duration `14.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`.
- Source audio material `src_audio_out01b_long_local` is normalized to `source.wav`; render manifest readback records duration `14.016`, codec `pcm_s16le`, sample rate `16000`, channels `1`.
- Selected cut `cut_out01b_long_001` maps `1.0` -> `13.0` seconds with duration target `12.0`; timeline policy remains `single_selected_cut_clamped_to_shortest_input_no_loop_no_speed_change_no_subtitle_burn_in`, and clamp did not occur.
- Render output `renders/out01b_long_local/rendered_video.mp4` readback: duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`.
- Selected profile is `mp4_h264_aac`; attempted profile list is `mp4_h264_aac`; fallback did not occur. Receipt / manifest / report still expose FFmpeg/FFprobe preflight, attempts, selected profile, warnings, and non-production status.
- This remains diagnostic render coverage, not production render, creative acceptance, subtitle burn-in, URL video acquisition, GUI render action, or publishing.

OUT-01c is complete as subtitle burn-in diagnostic. It keeps the OUT-01a / OUT-01b render path and adds only an optional diagnostic overlay mode:

- CLI shape is `render-tiny-proof --burn-in-subtitles diagnostic`; default remains `off`.
- Subtitle source priority is `edit_pack.subtitles[]` first, then sibling `transcript.json` segments as diagnostic fallback. No hardcoded drawtext string is accepted as proof.
- The CLI writes `diagnostic_subtitles.srt` into the render output directory and passes it to FFmpeg's `subtitles` filter.
- `render_receipt.json`, `render_manifest.json`, and `render_report.html` now expose `subtitle_burn_in.status`, `subtitle_source_ref`, `subtitle_overlay_policy`, rendered timeline subtitle items, selected profile, attempted profiles, fallback status, and output metadata.
- Fresh ignored smoke episode `episodes/out01c_subtitle_burnin_smoke_20260513` generated `renders/out01c_subtitle_burnin/rendered_video.mp4` from local source video `src_video_out01c_subtitle`, source audio `src_audio_out01c_subtitle`, selected cut `cut_out01c_subtitle_001`, and generated edit_pack subtitle drafts `sub_001` / `sub_002` / `sub_003`.
- Output readback was duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`; selected/attempted profile was `mp4_h264_aac`; fallback did not occur.
- This remains diagnostic visual proof. It is not production subtitle design, typography polish, safe-area/layout acceptance, creative edit acceptance, URL video acquisition, GUI render action, or publishing.

OUT-01d is complete as subtitle timing / font-filter preflight hardening. It keeps the OUT-01c diagnostic overlay path and makes the timing and environment diagnosis explicit:

- Subtitle item readback now includes original source timeline start/end, rendered timeline start/end, render_start offset, and status.
- Possible item statuses are `included`, `clamped_to_render_window`, `skipped_before_render_window`, `skipped_after_render_window`, `invalid_timing`, and `empty_text`.
- Only `included` / `clamped_to_render_window` items are written to `diagnostic_subtitles.srt`; skipped / invalid / empty items remain in receipt / manifest / report readback.
- `subtitle_burn_in.timing_mapping` records the mapping policy, render window, offset, status counts, renderable count, and skipped/invalid count.
- `subtitle_burn_in.filter_preflight` records FFmpeg subtitles filter validation mode, SRT UTF-8 write status, path escaping policy, and failure detail buckets for subtitles filter / libass / fontconfig / font provider / SRT parsing / path escaping failures.
- Fresh ignored smoke episode `episodes/out01d_timing_font_preflight_smoke_20260514` generated `renders/out01d_timing_font_preflight/rendered_video.mp4` from local source video `src_video_out01d_timing`, source audio `src_audio_out01d_timing`, selected cut `cut_out01d_timing_001`, and edit_pack subtitle drafts that exercise included / clamped / skipped timing.
- Output readback was duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24.0`, stream count `2`; selected/attempted profile was `mp4_h264_aac`; fallback did not occur; filter status was `passed_by_successful_render`.
- This remains diagnostic render hardening. It is not production subtitle design, typography polish, safe-area/layout acceptance, creative edit acceptance, URL video acquisition, GUI render action, or publishing.

ED-08 / OUT-01e is complete as real STT subtitle draft linkage and diagnostic render smoke. It keeps ED-07b real transcript plumbing and OUT-01d timing diagnostics, but connects them through `edit_pack.subtitles[]`:

- `generate-subtitles` reads `transcript.stt.real_transcript=true` and writes subtitle drafts with `source_type="real_transcript"`, `source_segment_ids[]`, `draft=true`, `diagnostic=true`, `not_production_subtitle_design=true`, and `production_subtitle_design=false`.
- Fake / fixture transcript inputs stay `source_type="transcript_segments"` and do not become production candidates.
- `render-tiny-proof --burn-in-subtitles diagnostic` still prioritizes `edit_pack.subtitles[]`, but now reads subtitle provenance into `subtitle_burn_in.source_ref.subtitle_source_type`, `subtitle_source_types[]`, `derived_from_real_transcript`, transcript provider/model, and `source_segment_ids[]`.
- OUT-01d timing mapping remains intact: original/render time, render_start offset, status counts, included/clamped/skipped/invalid/empty statuses, filter preflight, and disabled burn-in behavior are still tested.
- Fresh ignored smoke episode `episodes/out01e_real_transcript_subtitle_smoke_20260516` used synthetic local TTS audio normalized to `source.wav`, Vosk model `_tmp/stt_models/vosk-model-small-en-us-0.15`, source audio material `src_audio_out01e_real_stt`, and local source video material `src_video_out01e_local`.
- Smoke output `renders/out01e_real_transcript_subtitle_render/rendered_video.mp4` was generated with `subtitle_burn_in.status=enabled`, `derived_from_real_transcript=true`, status counts `included=1`, output duration `8.82`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24/1`, stream count `2`.
- This remains diagnostic linkage. It is not STT quality acceptance, transcript correction UI, production subtitle design, creative acceptance, URL video acquisition, GUI render action, publishing, FCPXML, or Resolve XML.

ED-10 is complete as official subtitle track import / transcript alignment. It does not add a production subtitle surface; it converts a subtitle track into the existing transcript artifact shape so the established cut/subtitle/NLE/render path can consume it:

- CLI shape: `import-subtitle-track --base-transcript <path> --subtitle-track <path> --output <path> [--source-format youtube-json3] [--reviewed-by <id>] [--dry-run] [--force] [--format json]`.
- The first source format is YouTube JSON3. The importer writes `stt.engine="subtitle_track"`, `provider="youtube_subtitles"`, `engine_version="youtube-json3"`, and preserves base transcript source-audio readback.
- Segment notes keep alignment readback against the base transcript when overlap exists, and warnings call out unaligned or overlapping subtitle events.
- `generate-subtitles` now marks imported subtitle-track drafts as `source_type="imported_subtitle_track"`, and `export-nle` warnings say "subtitle track transcript" instead of mislabeling these artifacts as real STT.
- Rejected / accepted / review states remain conservative data flags. An imported official subtitle track is not typography, safe-area, production render, rights, creative, or publishing acceptance.

The JP-Pilot R3 review packet surface is also available. `build-cut-review-packet` reads the R3 `edit_pack.json`, `transcript.json`, NLE manifest, render manifest, and rights manifest, then writes a machine-readable packet and an HTML report for final cut/context review:

- Local ignored output: `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/`
- Files: `cut_review_packet.json`, `cut_review_report.html`, `evidence_summary.json`, `evidence_summary.html`
- Readback: 9 selected cuts, context 3 passed / 6 needs_review, 105 imported subtitle drafts, rights `pending`, render `production_candidate=false`
- This packet deliberately keeps every `decision_placeholder.final_decision` as `undecided`; it is handoff material, not agent acceptance.
- The 2026-05-30 speed-first operator decision is recorded separately in local ignored `cut_decision_speed_pass.json` / `.html`: all 9 cuts are `accept_candidate` candidate seeds only, `needs_review` remains retained risk, and production / creative / publishing / rights acceptance remain false or pending.

JP-Pilot-01 is complete as a Japanese public VOD diagnostic. It reused the existing URL/source media, Vosk JP, edit_pack, subtitle, render, and NLE export path without adding new production surfaces:

- Selected source: official hololive short anime `【アニメ】押忍！！ば～んちょ だじぇ！` at <https://www.youtube.com/watch?v=7J5aS_pcBj4>.
- Ignored episode `episodes/jp_pilot01_hololive_bancho_20260525` generated `source_video.mp4`, `source.wav`, `transcript.json`, `edit_pack.json`, `renders/jp_pilot01_diagnostic_render/rendered_video.mp4`, and `exports/jp_pilot01/nle_cut_list.csv`.
- Readback: 26 transcript segments, speech coverage about 51.4%, 6 selected cut candidates, 3 passed / 3 needs_review, 17 subtitle drafts, 6.6s 1080p diagnostic render, 6 NLE CSV rows, ledger audit ok.
- The transcript is technically real but not creatively acceptable as-is. ED-09 added the review / correction entry point; JP-Pilot-01R proved a 7-segment corrected rerun; JP-Pilot-01R2 expanded coverage to accepted 25 / rejected 1 / unreviewed 0 and narrowed selected cuts to 10.86s-23.13s with all context checks passed. ED-10 / JP-Pilot-01R3 then imported the official subtitle track directly, producing 105 subtitle-track segments, 9 selected cuts, 105 subtitle drafts, NLE CSV 9 rows, and a 6.84s diagnostic render. The current bottleneck is parser-first reviewability/readback plus one explicitly selected limitation-lift slice for this captioned source.

## Production Gap Readback

ClipPipeGen is not finished when it can only produce docs, receipts, ledgers, or read-only reports. The final shape is a production-assist pipeline that carries URL / local-media source material through an episode:

`source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles / thumbnail / NLE export / render / publishing`

Current state against that final shape:

| Area | Current state | Remaining production gap |
|---|---|---|
| Source audio | URL and local media can become `source.wav` with receipt / sidecar / ledger proof | Technical acquisition proof is not creative, production, or publishing acceptance |
| Source video | Local video and URL video can become `source_video.<ext>` with receipt / sidecar / ledger proof and FFprobe metadata | Technical acquisition proof is not creative, production, or publishing acceptance |
| Preview surface | Local preview pack, GUI read-only ingest, and SH-05d existing-source-audio bridge exist | The surface still uses fake / fixture transcript and draft edit_pack, so it is not final edit acceptance |
| Transcript | `transcribe-audio --engine fake`, optional `--engine vosk --model <path>`, ED-09 review patches, and ED-10 `import-subtitle-track` exist. JP-Pilot-01R3 has 105 official subtitle-track segments with source-audio and alignment readback | Official captions can now enter the artifact path, but imported subtitle tracks are still review data and not creative or production subtitle acceptance; sources without official captions still need STT comparison |
| Edit pack | `transcript.json` can feed cut candidates, context checks, subtitles, and ED-06 CSV export; JP-Pilot-01R3 produced 9 cuts, 105 subtitle drafts, and NLE CSV 9 rows. The 2026-05-30 operator instruction carries all 9 as speed-first `accept_candidate` seeds | Creative cut acceptance and production subtitle design are still missing; R3 still has 6 context `needs_review` cuts retained as risk before production acceptance |
| NLE / render | Minimal CSV cut list export exists; OUT-01b can produce a diagnostic video; OUT-01c/OUT-01d can burn and diagnose subtitle timing; JP-Pilot-01 burned JP real STT subtitles into a diagnostic 1080p render | No FCPXML / Resolve XML, no production subtitle design, no STT quality acceptance, and no production render acceptance |
| Publishing | Not implemented | Upload / metadata / thumbnail setting / publish receipt are future integration work |

The project should continue only if the next slices add or connect real production-adjacent artifacts. A slice that only adds more policy, boundary text, report polish, or GUI read-only state without connecting `source.wav`, `transcript.json`, `edit_pack.json`, `preview_manifest.json`, NLE export, or rendered video should be treated as drift.

## Key Files

- `src/integrations/asset_fetch/yt_dlp_audio.py` — yt-dlp source-audio fetch adapter.
- `src/integrations/asset_fetch/source_video.py` — local source video copy/probe adapter.
- `src/integrations/render/ffmpeg_tiny.py` — OUT-01 FFmpeg/FFprobe tiny render adapter.
- `src/cli/fetch_source_audio.py` — `--mode yt-dlp-audio` CLI wiring, sidecar / receipt / ledger write.
- `src/cli/fetch_source_video.py` — `--mode local-media-video` CLI wiring, sidecar / receipt / ledger write.
- `src/cli/render_tiny_proof.py` — `render-tiny-proof` CLI wiring, receipt / manifest / report write.
- `src/pipeline/subtitle_generation.py` — transcript segments to `edit_pack.subtitles[]` draft generation, including real transcript source readback.
- `src/cli/import_subtitle_track.py` — `import-subtitle-track` CLI wiring for subtitle-track-to-transcript import.
- `src/pipeline/subtitle_import.py` — ED-10 YouTube JSON3 parser, base transcript alignment, warnings, and transcript artifact generation.
- `src/cli/build_cut_review_packet.py` — review packet CLI for selected-cut human review handoff.
- `src/pipeline/cut_review_packet.py` — cut review packet / evidence summary JSON and HTML generation.
- `docs/SCHEMAS/v1/cut_review_packet.md` — cut review packet shape and boundary.
- `src/cli/build_local_preview_pack.py` — local preview pack orchestration and `--use-existing-source-audio` bridge.
- `src/pipeline/preview_pack.py` — preview manifest / report generation and source audio provenance readback.
- `src/pipeline/nle_export.py` — ED-06 CSV cut list / manifest / HTML readback generation.
- `src/cli/export_nle.py` — `export-nle` CLI.
- `src/integrations/stt/vosk_adapter.py` — optional Vosk provider preflight / WAV read / transcript segment conversion.
- `src/cli/transcribe_audio.py` — `fake` and optional `vosk` transcript generation CLI.
- `src/pipeline/transcript.py` — transcript schema builder / validator with real transcript metadata readback.
- `gui/preview_reader.cjs` — read-only preview manifest ingest and artifact link validation.
- `docs/SCHEMAS/v1/nle_export.md` — ED-06 artifact contract and boundary.
- `docs/RUNTIME_STATE.md` — current state and next recommended action.
- `docs/FEATURE_REGISTRY.md` — feature status table and transition log.
- `docs/ASSET_FETCH_BOUNDARY.md` — asset_fetch, FFmpeg, yt-dlp, GUI, STT, Editing boundaries.
- `docs/AUTOMATION_BOUNDARY.md` — automation map and forbidden surfaces.
- `docs/PREVIEW_PACK.md` — next downstream review surface boundary.
- `docs/JP_PILOT.md` — JP-Pilot-01 runbook, readback, stagnation audit, and next-entry comparison.

## Validation Already Run

Latest validation for ED-10 / JP-Pilot-01R3 closeout:

```powershell
python -m src.cli.main import-subtitle-track --base-transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.jp_pilot01r2_20260526.json --subtitle-track episodes\jp_pilot01_hololive_bancho_20260525\source_subs\7J5aS_pcBj4.ja.json3 --output episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --reviewed-by codex:jp-pilot01r3 --force --format json
python -m src.cli.main generate-cuts --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --target-duration-seconds 18 --min-duration-seconds 4 --max-duration-seconds 28 --gap-threshold-seconds 2.5 --max-candidates 10 --replace-auto --select-generated --format json
python -m src.cli.main check-cut-context --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --selected-cuts-only --format json
python -m src.cli.main generate-subtitles --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --selected-cuts-only --replace-auto --format json
python -m src.cli.main export-nle --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --output-dir episodes\jp_pilot01_hololive_bancho_20260525\exports\jp_pilot01r3_subtitle_import --format json
python -m src.cli.main render-tiny-proof --episode-id jp_pilot01_hololive_bancho_20260525 --source-video-material-id src_video_jp_pilot01 --source-audio-material-id src_audio_jp_pilot01 --edit-pack-path episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --output-id jp_pilot01r3_subtitle_import_diagnostic_render --duration-sec 6.84 --burn-in-subtitles diagnostic --force --format json
python -m src.cli.main build-cut-review-packet --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --nle-manifest episodes\jp_pilot01_hololive_bancho_20260525\exports\jp_pilot01r3_subtitle_import\nle_export_manifest.json --render-manifest episodes\jp_pilot01_hololive_bancho_20260525\renders\jp_pilot01r3_subtitle_import_diagnostic_render\render_manifest.json --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --format json
python -m src.cli.main validate-transcript --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --format json
python -m src.cli.main validate-edit-pack --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --format json
python -m src.cli.main validate-rights --rights-manifest episodes\jp_pilot01_hololive_bancho_20260525\rights_manifest.json --format json
python -m src.cli.main audit-material-ledger --episode-id jp_pilot01_hololive_bancho_20260525 --root episodes --format json
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results: import dry-run/apply `schema_ok=true`, imported segments 105, aligned 68, unaligned 37, overlapping 1, segment review counts accepted 105 / needs_fix 0 / rejected 0 / unreviewed 0. Downstream produced 9 selected cuts, context 3 passed / 6 needs_review / 0 failed, 105 `imported_subtitle_track` subtitle drafts, NLE CSV 9 rows, and a 6.84s / 1920x1080 diagnostic render with 7 rendered subtitle items. The review packet writes 9 cut entries with undecided decision placeholders plus an evidence summary that records rights `pending` and diagnostic render `production_candidate=false`. Transcript/edit/rights schemas passed and ledger audit was OK. Full validation: `uvx pytest -q` -> 193 passed, `npm run smoke` -> OK, `npm run smoke:electron` -> OK, `git diff --check` -> clean.

Latest validation for JP-Pilot-01R2 closeout:

```powershell
python -m src.cli.main review-transcript --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --patch episodes\jp_pilot01_hololive_bancho_20260525\transcript_review_patch_jp_pilot01r2.json --reviewed-by codex:jp-pilot01r2 --dry-run --format json
python -m src.cli.main generate-cuts --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --target-duration-seconds 18 --min-duration-seconds 5 --max-duration-seconds 28 --gap-threshold-seconds 2.5 --max-candidates 5 --replace-auto --select-generated --format json
python -m src.cli.main check-cut-context --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --selected-cuts-only --format json
python -m src.cli.main generate-subtitles --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --selected-cuts-only --replace-auto --format json
python -m src.cli.main export-nle --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --output-dir episodes\jp_pilot01_hololive_bancho_20260525\exports\jp_pilot01r2_narrowed --format json
python -m src.cli.main render-tiny-proof --episode-id jp_pilot01_hololive_bancho_20260525 --source-video-material-id src_video_jp_pilot01 --source-audio-material-id src_audio_jp_pilot01 --edit-pack-path episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --output-id jp_pilot01r2_narrowed_diagnostic_render --duration-sec 23.13 --burn-in-subtitles diagnostic --force --format json
python -m src.cli.main validate-transcript --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --format json
python -m src.cli.main validate-edit-pack --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --format json
python -m src.cli.main validate-rights --rights-manifest episodes\jp_pilot01_hololive_bancho_20260525\rights_manifest.json --format json
python -m src.cli.main audit-material-ledger --episode-id jp_pilot01_hololive_bancho_20260525 --format json
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results: review dry-run `schema_ok=true` / updated 19 / accepted 25 / rejected 1 / unreviewed 0, selected cuts 5, context 5 passed / 0 needs_review, subtitle drafts 21, NLE CSV 5 rows, diagnostic render 23.13s / 1080p / clamped=false, transcript/edit/rights schemas OK, ledger audit ok, full tests `188 passed`, GUI smoke OK, Electron smoke OK, diff check clean.

Latest validation for JP-Pilot-01R closeout:

```powershell
python -m src.cli.main review-transcript --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --patch episodes\jp_pilot01_hololive_bancho_20260525\transcript_review_patch_jp_pilot01r.json --reviewed-by codex:jp-pilot01r --dry-run --format json
python -m src.cli.main validate-transcript --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json --format json
python -m src.cli.main validate-edit-pack --edit-pack episodes\jp_pilot01_hololive_bancho_20260525\edit_pack.json --format json
python -m src.cli.main validate-rights --rights-manifest episodes\jp_pilot01_hololive_bancho_20260525\rights_manifest.json --format json
python -m src.cli.main audit-material-ledger --episode-id jp_pilot01_hololive_bancho_20260525 --format json
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results: review dry-run `schema_ok=true` / updated 7 / accepted 7, transcript/edit/rights schemas OK, ledger audit ok, full tests `188 passed`, GUI smoke OK, Electron smoke OK, diff check clean.

Latest validation for ED-09 closeout:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results:

- `uvx pytest -q` -> `188 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors

Latest validation for JP-Pilot-01 closeout:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
ffprobe -v error -print_format json -show_format -show_streams episodes/jp_pilot01_hololive_bancho_20260525/renders/jp_pilot01_diagnostic_render/rendered_video.mp4
python -m src.cli.main audit-material-ledger --episode-id jp_pilot01_hololive_bancho_20260525 --format json
```

Results:

- `uvx pytest -q` -> `178 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors
- JP-Pilot-01 render FFprobe readback -> duration `6.600000`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `1920x1080`, fps `30/1`, stream count `2`
- JP-Pilot-01 ledger audit -> `ok=true`, issues `[]`, materials `2`

Latest validation for ED-08 / OUT-01e closeout:

```powershell
uvx pytest -q tests/test_subtitle_generation.py tests/test_real_transcript_pipeline.py
uvx pytest -q tests/test_edit_pack.py
uvx pytest -q tests/test_tiny_render.py
uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py
uvx pytest -q tests/test_nle_export.py
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
ffprobe -v error -print_format json -show_format -show_streams episodes/out01e_real_transcript_subtitle_smoke_20260516/renders/out01e_real_transcript_subtitle_render/rendered_video.mp4
```

Results:

- `uvx pytest -q tests/test_subtitle_generation.py tests/test_real_transcript_pipeline.py` -> `8 passed`
- `uvx pytest -q tests/test_edit_pack.py` -> `10 passed`
- `uvx pytest -q tests/test_tiny_render.py` -> `20 passed`
- `uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py` -> `13 passed`
- `uvx pytest -q tests/test_nle_export.py` -> `3 passed`
- `uvx pytest -q` -> `156 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors
- rendered video FFprobe readback -> duration `8.82`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24/1`, stream count `2`

Additional OUT-01e readback:

- ignored `episodes/out01e_real_transcript_subtitle_smoke_20260516` readback -> local diagnostic TTS WAV was normalized to `materials/src_audio_out01e_real_stt/source.wav`, Vosk generated `transcript.json` with `real_transcript=true`, `generate-cuts` selected `cut_001`, `generate-subtitles` wrote one `edit_pack.subtitles[]` item with `source_type="real_transcript"` and `source_segment_ids=["seg_000001"]`, then `render-tiny-proof --burn-in-subtitles diagnostic` generated `renders/out01e_real_transcript_subtitle_render/rendered_video.mp4`
- transcript readback -> provider `vosk`, model `_tmp/stt_models/vosk-model-small-en-us-0.15`, segment count `1`, source audio duration `9.8028125`, warning `real STT plumbing proof only; transcript quality is not creative acceptance`
- subtitle burn-in readback -> `subtitle_burn_in.status=enabled`, `source_ref.source_type=edit_pack_subtitles`, `source_ref.subtitle_source_type=real_transcript`, `derived_from_real_transcript=true`, `transcript_real_transcript=true`, `transcript_provider=vosk`, `source_segment_ids=["seg_000001"]`
- timing readback -> `render_start_offset_seconds=0.09`, render duration `8.82`, status counts `{"included": 1}`, item `sub_001` maps original `0.09 -> 8.91` to render `0.0 -> 8.82`
- warnings remain expected: diagnostic-only render, duration target unmet because the available real transcript/source audio range is shorter than the default target, source video/audio duration mismatch, draft edit_pack review status, pending source material rights

Additional OUT-01d readback:

- ignored `episodes/out01d_timing_font_preflight_smoke_20260514` readback -> registered local source video `src_video_out01d_timing`, normalized source audio `src_audio_out01d_timing`, generated fake transcript segments, edited `edit_pack.subtitles[]` with diagnostic timing cases, selected `cut_out01d_timing_001`, then rendered `renders/out01d_timing_font_preflight/rendered_video.mp4`
- generated render paths: `episodes/out01d_timing_font_preflight_smoke_20260514/renders/out01d_timing_font_preflight/rendered_video.mp4`, `diagnostic_subtitles.srt`, `render_receipt.json`, `render_manifest.json`, and `render_report.html`
- subtitle source readback: `source_type=edit_pack_subtitles`, `path=episodes/out01d_timing_font_preflight_smoke_20260514/edit_pack.json`, status counts `skipped_before_render_window=1`, `clamped_to_render_window=2`, `included=2`, `skipped_after_render_window=1`
- subtitle timing readback: render_start offset `1.0`; SRT contains only included/clamped items; skipped items remain in manifest/report but are not written to SRT
- filter readback: `filter_preflight.status=passed_by_successful_render`, `srt_encoding.status=written`, failure detail empty on success
- selected/attempted profile: `mp4_h264_aac`; fallback did not occur; `subtitle_burn_in.status=enabled`
- remaining warnings say the render is diagnostic, subtitle overlay is not typography/safe-area/font polish, transcript is fake/fixture-derived, edit_pack review is draft, and rights are not production-ready

Last validation for OUT-01b closeout:

```powershell
uvx pytest -q tests/test_tiny_render.py
uvx pytest -q tests/test_source_video_fetch.py
uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py
uvx pytest -q tests/test_nle_export.py
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
ffprobe -v error -print_format json -show_format -show_streams episodes/out01b_long_local_render_smoke_20260513/renders/out01b_long_local/rendered_video.mp4
```

Results:

- `uvx pytest -q tests/test_tiny_render.py` -> `11 passed`
- `uvx pytest -q tests/test_source_video_fetch.py` -> `4 passed`
- `uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_real_transcript_pipeline.py` -> `13 passed`
- `uvx pytest -q tests/test_nle_export.py` -> `3 passed`
- `uvx pytest -q` -> `147 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors
- rendered video FFprobe readback -> duration `12.0`, container `mov,mp4,m4a,3gp,3g2,mj2`, video codec `h264`, audio codec `aac`, resolution `640x360`, fps `24/1`, stream count `2`

Additional OUT-01b readback:

- ignored `episodes/out01b_long_local_render_smoke_20260513` readback -> registered local source video `src_video_out01b_long_local`, normalized source audio `src_audio_out01b_long_local`, selected `cut_out01b_long_001`, then rendered `renders/out01b_long_local/rendered_video.mp4`
- generated render paths: `episodes/out01b_long_local_render_smoke_20260513/renders/out01b_long_local/rendered_video.mp4`, `render_receipt.json`, `render_manifest.json`, and `render_report.html`
- source video readback: duration `14.0`, h264/aac, `640x360`, fps `24.0`, stream count `2`
- source audio readback: duration `14.016`, `pcm_s16le`, `16000` Hz, `1` channel
- timeline readback: selected range `1.0` -> `13.0`, duration target `12.0`, clamp `false`, fallback `false`, selected/attempted profile `mp4_h264_aac`
- remaining warnings say the render is diagnostic, subtitle burn-in is disabled, transcript readback is unavailable for this fixture, edit_pack review is draft, and rights are not production-ready

Last validation for INT-02f closeout:

```powershell
uvx pytest -q
npm run smoke
npm run smoke:electron
git diff --check
```

Results:

- `uvx pytest -q` -> `136 passed`
- `npm run smoke` -> `gui smoke: OK`
- `npm run smoke:electron` -> `electron smoke: OK`
- `git diff --check` -> no whitespace errors

Additional targeted readback:

- `uvx pytest -q tests/test_source_video_fetch.py tests/test_asset_fetch_boundary.py tests/test_material_ledger.py tests/test_source_audio_fetch.py tests/test_transcript.py tests/test_vosk_stt_adapter.py tests/test_nle_export.py` -> targeted source-video acquisition / material ledger / source-audio / transcript / ED-06 export tests pass
- ignored `episodes/int02f_source_video_smoke_20260512` readback -> local `input_source_video.mkv` was copied into `source_video.mkv`, then `fetch_receipt.json`, `sidecar.json`, and `material_ledger.json` entry were generated
- generated source-video paths: `episodes/int02f_source_video_smoke_20260512/materials/src_video_local_smoke/source_video.mkv`, `fetch_receipt.json`, `sidecar.json`, and `episodes/int02f_source_video_smoke_20260512/material_ledger.json`
- metadata readback: duration `1.2`, container `matroska,webm`, video codec `mpeg4`, audio codec `null`, resolution `160x90`, fps `15.0`, stream count `1`
- remaining warnings say local source video was copied without render/encode, source video acquisition is not production/creative/publish acceptance, audio stream is absent, and rights status is `pending`
- `uvx pytest -q tests/test_transcript.py tests/test_vosk_stt_adapter.py` -> targeted transcript / STT adapter tests pass
- `uvx pytest -q tests/test_real_transcript_pipeline.py tests/test_cut_generation.py tests/test_context_check.py tests/test_subtitle_generation.py` -> targeted edit_pack / context / subtitle path tests pass
- `uvx pytest -q tests/test_nle_export.py` -> targeted ED-06 export tests pass
- ignored `episodes/ed07b_real_stt_smoke_20260512` readback -> Windows TTS `source.wav` was transcribed by Vosk into `transcript.json`, then flowed through cut generation, context check, subtitle generation, and ED-06 CSV export
- generated paths: `episodes/ed07b_real_stt_smoke_20260512/transcript.json`, `edit_pack.json`, `exports/ed06/nle_cut_list.csv`, `nle_export_manifest.json`, and `nle_export_report.html`
- manifest/report read back transcript provider `vosk`, model `_tmp/stt_models/vosk-model-small-en-us-0.15`, `real_transcript=true`, segment count, duration, source audio material id/path/hash, and `production_edit_candidate=false`
- remaining warnings say the export is a plumbing proof, real STT quality is not creative acceptance, and `edit_pack.review.status` is still `draft`
- `uvx pytest -q tests/test_preview_pack.py tests/test_asset_fetch_boundary.py` -> targeted preview/boundary tests pass
- existing source audio mode does not call `fetch-source-audio`
- `preview_manifest.json` includes `source_wav`, `fetch_receipt`, `sidecar`, `material_ledger`, `ledger_entry`, and `source_audio_provenance`
- `preview_report.html` includes `Source Audio Provenance` and production-candidate warnings for fake / fixture transcript and generated edit_pack
- ignored `episodes/sh05d_existing_source_audio_smoke_20260512` readback -> manifest provenance refs present, report provider/tool/URL/hash/rights snapshot visible, GUI reader `state=ready`
- real INT-02e artifact smoke -> pending because the prior ignored `episodes/int02e_operator_smoke_20260512` artifact was not present in this working tree

## Resume-Time Environment Drift (2026-05-12 secondary readback)

The earlier INT-02e closeout validation used a different shell/environment from one secondary readback on the same day. The drift items below remain useful context, but ED-07b is complete and PowerShell validation for this slice passed. Read this section before touching GUI / TH-01 walkthrough / INT-02e re-smoke work.

### Electron smoke drift can appear in git-bash

- Command: `npm run smoke:electron`. Also reproduced via `node_modules/electron/dist/electron.exe . --smoke` and `node_modules/electron/dist/electron.exe gui/main.cjs --smoke`.
- Result: `TypeError: Cannot read properties of undefined (reading 'handle')` at `gui/main.cjs:30` (`ipcMain.handle("episode:status", ...)`).
- Root signal: a probe script run via `electron.exe` shows `require('electron')` returning the binary path **string** instead of the Electron API object, so the destructured `app` / `BrowserWindow` / `ipcMain` are all undefined. `app.whenReady` is never reached because `ipcMain.handle` throws first.
- Environment: invoked from git-bash on Windows. `node_modules/electron/dist/version` reports `42.0.0`; `electron.exe --version` reports its bundled `v24.15.0` (Node). `gui/main.cjs` is unchanged since the INT-02e closeout.
- Status: PowerShell validation for ED-07b reports `npm run smoke:electron -> electron smoke: OK`. The git-bash-specific launcher drift is deferred and should not be mixed into production-pipeline slices.
- Impact on SH-05d: none. SH-05d is CLI / pipeline / preview artifact work and does not depend on changing the Electron main-process boot path. GUI Preview Pack visual re-check on the SH-05d output is a follow-up, not a SH-05d blocker.

### TH-01 real walkthrough still depends on `config/nlmytgen_path.json`

- File present: `config/nlmytgen_path.json.example` only. The real `config/nlmytgen_path.json` is `.gitignore`d by design.
- Without that real config, `audit-thumbnail` / `patch-thumbnail` cannot reach the NLMYTGen CLI bridge, so the user-owned TH-01 acceptance step in `FIRST_SLICE.md` DoR (real YMM4 base template `.ymmp` → end-to-end walkthrough) cannot be replayed here.
- This is independent of SH-05d. SH-05d consumes existing source-audio / preview-pack artifacts and does not touch the NLMYTGen bridge. TH-01 acceptance and SH-05d run on separate timelines.

### INT-02e re-smoke needs ffmpeg + yt-dlp on PATH

- `which ffmpeg` / `which yt-dlp` in the current git-bash shell both return not-found.
- The previous INT-02e real smoke used `uv tool install yt-dlp` (yt-dlp `2026.03.17`) and gyan.dev FFmpeg `8.0.1-full_build` resolved through the user's PowerShell / system PATH. Reproducing the smoke needs either the same `uv tool install` path, the user's PowerShell environment where these tools already resolved, or an equivalent local install.
- Python tests are unaffected: `tests/test_ytdlp_audio_adapter.py` / `tests/test_ffmpeg_audio_adapter.py` / `tests/test_asset_fetch_boundary.py` use fake runners and monkeypatch and do not call the real binaries.
- SH-05d does not require a fresh INT-02e fetch. The bridge consumes existing `source.wav`, `fetch_receipt.json`, `sidecar.json`, and `material_ledger.json` produced by earlier runs. A re-smoke of INT-02e is only needed if the input artifact set has to be regenerated for some other reason.

## Visual Evidence

SH-05c visual evidence was previously generated locally from the SH-05b smoke episode:

- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_tab.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_artifacts.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_readback.json`

These are intentionally ignored scratch artifacts and are not pushed. The project-local context and reproduction path are preserved in `docs/PREVIEW_PACK.md` and `docs/RUNTIME_STATE.md`.

Readback from the visual evidence:

- GUI state: `ready`
- validation issues: `0`
- artifact links: 6 entries in the old SH-05c evidence; new SH-05d manifests expose sidecar and material ledger links as well
- Preview Pack panel forms/buttons: `0`
- forbidden video element: `0`

## Hard Boundaries Still In Force

Not implemented / not accepted yet:

- FCPXML / Resolve XML export
- GUI fetch button
- GUI export button
- GUI render button
- GUI-triggered `build-local-preview-pack`
- cut / concat
- production subtitle burn-in / subtitle design acceptance
- production render / full render pipeline
- rendered video preview surface beyond the diagnostic OUT-01 artifact
- render profile matrix beyond the minimal OUT-01a fallback set
- creative acceptance
- rights hard gate
- STT quality acceptance / GUI transcript review surface / speaker diarization

yt-dlp remains inside `asset_fetch` source-audio/source-video URL fetch. FFmpeg is allowed in `src/integrations/render/` only for OUT-01 diagnostic rendering, including OUT-01c diagnostic subtitle overlay, OUT-01d timing/filter readback, OUT-01e real STT subtitle source readback, and OUT-01f cut-scoped subtitle-overlay visual proof, and in `src/integrations/asset_fetch/` for source-audio normalization; it must not enter STT, Editing core, GUI actions, or production subtitle/render surfaces.

## Recommended Next Slice

Current recommendation after ED-10g: consume `small_adjustment` as the human
response for `clip-typography-decoration-comparison-001`, preserve the accepted
diagnostic font-size direction, and prepare the next small-adjustment
diagnostic overlay proof route for `cut_002` / `cut_003`. The font-family and
decoration axes remain unresolved until a concrete adjusted candidate is
selected. If a worktree is missing ignored `episodes/` artifacts or the
comparison report JSON, treat that as same-machine local evidence absence, not
remote/tracked failure. Regenerate local artifacts only when visual candidate
readback is needed. Non-Repo Artifact Handoff remains infrastructure; it does
not make `rendered_video.mp4` transferable by Git and it does not create
production acceptance.

| # | Candidate | Why now | Unblocks | Urgency |
|:--:|---|---|---|:--:|
| 1 | Advance: ED-10g small-adjustment diagnostic overlay proof route | Human answered `small_adjustment`, not a concrete candidate id or production acceptance | Carries accepted font size forward while narrowing font-family and decoration before the next proof | Urgent |
| 2 | Audit: needs_adjustment / dense-stress route | `cut_008` is still the smallest dense stress target, but remains `needs_adjustment` | Defines whether a later stress proof is valid input to design acceptance | Medium |
| 3 | Verify: final render-path output or regenerated render comparison | Diagnostic proof and final render-path output are separate | Defines exact SHA-256 versus metadata approximate criteria without making production claims | Medium |
| 4 | Review: editorial representative-sequence quality | Creative/editorial acceptance is separate from subtitle design and render-path proof | Lets the operator judge sequence value without rights or production shortcutting | Medium |
| 5 | Clear Rights: rights/material-use approval path | Rights remain `pending`, so production/public use is not allowed | A separate path toward public or production use after production acceptance exists | Medium |
| 6 | Prepare: YMM4/Premiere handoff, publishing/OAuth/thumbnail, or GUI work | These are downstream surfaces, not the current proof/readback slice | Keeps handoff and tooling work from mixing with acceptance decisions | Low |

For the next human review, do not re-ask the already-consumed ED-10f
representative subtitle design question. Start from the ED-10g
`small_adjustment` response and ask only for the concrete font-family /
decoration adjustment needed for the next `cut_002` / `cut_003` diagnostic
overlay proof. Keep `rights_status=pending`, `production_candidate=false`, and
`production_subtitle_design_acceptance=false` unless a separate valid
acceptance slice changes them.

Human review can now be returned as `chapter_revision_patch.template.json` /
`.csv`, or as natural language that the Agent normalizes into that patch shape.
The operator can describe which chapters stay, which need boundary changes,
which need script/display subtitle work, which should split/merge, and which
should be dropped. The Agent must not auto-fill creative intent,
`script_override`, or final production decisions; it must not convert undecided
chapters into creative acceptance, and it must not treat the diagnostic render
as production output.

Regenerated render comparison can follow once chapter-level decisions are
clearer. Exact SHA-256 is useful only for the same local artifact identity;
re-renders may differ by environment, so a later Verify slice should define
duration / resolution / codec / timeline refs / subtitle source refs /
boundary flags as metadata approximate criteria.

## 自律選定方針（assistant 権限）

`docs/HOLOEN_PILOT.md` に運用方針として固定済：assistant は HoloEN public VOD 候補を自律的に調査・選定し、risk が低いと判断した 1 本を diagnostic smoke の default として使ってよい。除外条件（COVER 公式 derivative works guidelines: members-only / paid / concert / song / 第三者 IP リスク高）は compliance として維持。

JP-Pilot-01 も同方針で完了済み。assistant が JP public VOD を自律選定し、actual smoke と quality scorecard を記録した。operator review は事後。

## Next Two-Slice Pressure

After `ED-10 / JP-Pilot-01R3 / SH-06 / ED-10b`, the project should deliberately
move toward one of these production-adjacent bottlenecks:

| Candidate | Usefulness | Why it matters | Risk |
|---|---:|---|---|
| operator chapter revision patch | 9/10 | Board and templates exist, but operator-written decisions are still blank | Agent must not invent creative intent or script overrides |
| patch normalizer / applier | 8/10 | A patch should be able to flow back into edit_pack / subtitle drafts / render plan / NLMYTGen handoff | Must keep source transcript and official subtitle track immutable evidence |
| regenerated render comparison | 7/10 | Non-repo artifact handoff records SHA-256, but re-rendered diagnostic video may differ by environment | Must avoid treating hash drift alone as creative or production failure |
| representative subtitle design or final render-path acceptance | 7/10 | Official captions now enter the artifact path; typography/safe-area review and final render-path output are separate limitation-lift slices | Must not bundle subtitle design, render-path output, editorial quality, and rights clearance |
| rights approval path | 7/10 | Rights remain pending, so production/public use is not allowed | Must stay separate from local diagnostic success |

Recommended continuation after `ED-10 / JP-Pilot-01R3 / SH-06 / ED-10b`:
prefer operator chapter revision patch input first, then a patch
normalizer/applier, then regenerated render comparison if the handoff must be
replayed elsewhere, then one explicit limitation-lift slice at a time
(`representative_subtitle_design_review`, `final_render_path_output_review`,
`editorial_representative_sequence_review`, or
`rights_material_use_clearance`). Do
not count docs-only policy expansion, read-only GUI panels, or audit log polish
as production progress unless they connect operator decisions back to
`edit_pack`, subtitle drafts, render plans, NLE export, or NLMYTGen handoff.

Any OUT follow-up must remain explicitly non-production until a later acceptance slice: no publishing, no GUI one-click publish, no broad renderer feature set, and no production candidate claims.

## Quick Operator Check

After pulling on another terminal:

```powershell
git log -1 --oneline --decorate
git status --short --branch
git ls-files episodes
uvx pytest -q
npm run smoke
npm run smoke:electron
```

To regenerate the R3 Chapter Revision Board when the ignored R3 artifacts are
present locally:

```powershell
python -m src.cli.main build-chapter-revision-board `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

To inspect the GUI:

```powershell
npm start
```

Use the GUI `Preview Pack` tab with an existing episode directory or a `preview_manifest.json` path. A fresh checkout may not contain ignored smoke episodes; regenerate a local preview pack when visual inspection is needed.
