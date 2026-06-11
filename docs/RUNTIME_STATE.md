# Runtime State - ClipPipeGen

This file is the active resume surface. It should answer "where are we now?"
without requiring the reader to scan historical closeouts.

Long historical closeouts moved to [RUNTIME_HISTORY.md](RUNTIME_HISTORY.md).
Do not treat archived lane/slice labels or old action wording as current
instructions.

## Current Resume Capsule

- date: 2026-06-11 JST
- latest pushed implementation resume point before this handoff refresh:
  `87afbfd docs: note local subtitle report image paths`. This is the pushed
  subtitle_style_spike review-surface hardening state after the grid authority
  audit, visible element authority guardrail, guide overlay split,
  bbox-provenance readback, and local HTML image path audit. A later docs-only
  handoff refresh may be the newest commit; on another terminal, use
  `git log -1 --oneline --decorate` for the exact pulled HEAD.
- verified base before this refresh:
  origin/main parity in this workspace before this handoff refresh.
- latest subtitle wrapping / report-clarity refinement:
  the current tracked implementation keeps
  `japanese_boundary_font_bbox_pixel_wrap_v1` and
  `wrapping_authority=font_bbox_pixel_measurement_not_grid_cell_count`, but now
  also treats short suffix-only Japanese tail lines as suspicious when a nearby
  measured-safe break exists. The concrete current cut_003 readback is:
  `sub_013` wraps as `なんで来なかった` / `んすか！！`,
  `sub_017` wraps as `まあ謝るんなら許して` / `あげます`,
  `sub_024` remains `団長、ちなみに、他の` / `番長知ってますか？`, and
  `sub_025` remains `長(ちょう)？　長って` / `言った？`.
  `suffix_tail_prevention_applied_count=2`,
  `one_character_orphan_present=false`, and
  `suspicious_tail_line_present=false` in the regenerated cut_003 proof
  readback. The HTML reports now explain that repeated text across modes is
  comparison-only, `dialogue_badge_left` is the current normal
  speaker-identified dialogue mode, `bottom_center_emphasis` is for emphasis or
  strong one-liners, `reaction_caption` is for punchline/surprise/instant
  reaction, and `speaker_badge_stack` is a placeholder future stack. SPK/A/B
  badges are labeled temporary placeholders, not real face icons or production
  speaker identity design. The regenerated ignored artifacts remain local
  review-only evidence; production subtitle design/render, creative, rights,
  publishing, and public-use acceptance remain unaccepted.
- latest subtitle_style_spike review surface state:
  `1a9410d fix: clarify subtitle spike grid authority` confirms the old grid
  was visual-only, removes default grid lines from human samples, and exposes
  `grid_model=none`, `snap_to_grid=false`,
  `grid_visible_in_samples=false`, and
  `wrapping_authority=font_bbox_pixel_measurement_not_grid_cell_count`.
  `d00aff9 feat: add visible review authority guardrail` defines visible
  element authority classifications
  (`computational_authority`, `measured_readback`, `visual_guide_only`,
  `placeholder`, `decorative`) and labels A/B speaker badges as placeholder
  badges, not real face icons or final speaker identity design. `e3bdf3b feat:
  add subtitle guide overlay samples` separates clean default samples from
  explicit guide-overlay samples and documents
  `bottom_center_emphasis_guide_v0`,
  `dialogue_badge_left_guide_v0`,
  `speaker_badge_stack_guide_future`, and
  `status_caption_guide_future`. `505a33d feat: clarify subtitle bbox
  provenance` adds `measured_bbox_provenance`, per-sample `style_inputs`,
  `computed_layout`, and `measured_output`, plus a two-run determinism audit.
  `87afbfd docs: note local subtitle report image paths` records that the
  generated report uses sibling relative PNG refs that resolve locally; when
  images appear broken, the likely cause is opening the local HTML through a
  translation/proxy surface that cannot fetch the sibling PNG files.
- current review boundary state:
  `cut_003` boundary and operator decision remain closed. The accepted route is
  still diagnostic candidate review only: no cut timing change, transcript
  mutation, official subtitle evidence mutation, source media mutation,
  production subtitle design acceptance, production render acceptance,
  creative acceptance, rights approval, publishing acceptance, or public-use
  permission has been added. `production_candidate=false`,
  `rights_status=pending`, `production_usage_allowed=false`, and
  `production_subtitle_design_acceptance=false` remain active.
- latest implementation post-push sync validation:
  2026-06-10 JST local readback before this handoff refresh:
  `git status --short --branch` -> `## main...origin/main`;
  `git rev-list --left-right --count HEAD...origin/main` -> `0 0`;
  `git log -1 --oneline --decorate` ->
  `87afbfd (HEAD -> main, origin/main, origin/HEAD) docs: note local subtitle report image paths`;
  `git ls-files episodes` empty. Targeted validation across the recent subtitle
  spike changes included `uvx --with pillow pytest -q
  tests/test_subtitle_style_spike.py` -> 2 passed, `uvx pytest -q
  tests/test_subtitle_style_spike.py -rs` -> 1 passed / 1 intentional Pillow
  skip, `git diff --check` clean, and JSON/HTML readbacks confirming visible
  element authority, placeholder badge labeling, guide overlay separation,
  bbox provenance, deterministic measurement output, and local image refs.
  Ignored generated artifacts under `episodes/` and `_tmp/` were not staged.
- previous pushed resume point:
  `f6fcf5b feat: add subtitle typography measurement spike`
- latest resume-surface sync validation:
  2026-06-09 JST local readback in this workspace:
  `git status --short --branch` -> `## main...origin/main`;
  `git ls-files episodes` empty. Targeted local readbacks parsed the accepted
  ignored filled operator patch
  `chapter_revision_patch.cut_002_cut_003_proxy.operator.json`, matching
  `.operator.csv`, and `.operator.html`. The filled patch reads
  `cut_003.proxy_decision=proceed_with_limitations`,
  `cut_003.context_risk_handling=keep_retained_risk_visible`,
  `boundary_request=none`, `analyst_action=noop`, and
  `downstream_target=none`. It keeps retained context risk visible and records
  that human review accepted cut length and response/referral closure for
  diagnostic candidate review. The same note records the unresolved subtitle
  design/readability limitation:
  `subtitle_visual_readability=needs_adjustment`,
  `embedded_subtitle_too_small_for_youtube=true`,
  `sidecar_srt_player_display_can_confuse_review=true`,
  `source_timeline_context_preview_requested=true`, and
  `production_subtitle_design_acceptance=false`. The scoped template
  `.template.json` / `.template.csv` stayed blank/default. `cut_002` stayed
  unchanged with `proxy_decision=proceed_with_limitations`,
  `context_risk_handling=undecided`, and its existing long-line watch note.
  This is a cut/content proxy decision only; it is not production subtitle
  design acceptance, production render acceptance, creative acceptance, rights
  approval, publishing acceptance, or public-use permission.
- latest subtitle design / review UX validation:
  2026-06-09 JST local readback in this workspace: the tracked
  `build-subtitle-overlay-visual-proof` generator now follows
  [SUBTITLE_PRESENTATION_CONTRACT.md](SUBTITLE_PRESENTATION_CONTRACT.md)
  (`jp_clip_dialogue_reference_v0`) for diagnostic proof only. The active
  diagnostic candidate is `jp_clip_dialogue_badge_left_v0`: a large
  heavy-outlined, left-aligned dialogue subtitle beside a speaker badge
  placeholder. The material ledger has only source video/audio, so real member
  face icons were unavailable and the preferred non-POV face-icon pattern is
  approximated with an explicit fallback. The ignored local style probe
  regenerates only `cut_003`, keeps the reference SRT under
  `subtitle_overlay_reference/`, extracts subtitle-bearing sample frames for
  early / middle / response-referral / final active cues, and records
  replacement-style display timing. Readback fields include
  `subtitle_presentation_contract.contract_id=jp_clip_dialogue_reference_v0`,
  `style_candidate_id=jp_clip_dialogue_badge_left_v0`,
  `font_size=round(frame_height*0.115)=124` for the 1920x1080 source,
  `outline=max(2, round(font_size*0.096))=12`,
  `alignment=speaker_badge_left_aligned_dialogue`,
  `left_alignment_is_universal=false`,
  `speaker_identity_presentation.fallback_used=true`,
  `sample_frame_selection.includes_response_referral_block=true`,
  `production_subtitle_design_acceptance=false`,
  `production_candidate=false`, `rights_status=pending`, and
  `production_usage_allowed=false`. Existing previous proof frame/video/SRT are
  archived under `subtitle_overlay_reference/` for comparison in the same HTML
  report. Human review still decides diagnostic readability only; no production
  subtitle design acceptance is claimed.
- previous subtitle renderer / typography measurement spike:
  `f6fcf5b` adds [SUBTITLE_RENDERER_TYPOGRAPHY_SPIKE.md](SUBTITLE_RENDERER_TYPOGRAPHY_SPIKE.md),
  `src/integrations/render/subtitle_style_spike.py`, and
  `tests/test_subtitle_style_spike.py`. The spike separates subtitle mode
  taxonomy from renderer-specific values:
  `dialogue_badge_left`, `bottom_center_emphasis`, `reaction_caption`, and
  `speaker_badge_stack`. It records a renderer decision matrix for ASS/libass
  + FFmpeg, HTML/CSS screenshot prototypes, Pillow/Skia/Pango-style bitmap
  drawing, YMM4 `.ymmp` TextItem generation, and Premiere/MOGRT/image-overlay
  paths. Pillow is explicitly optional: the normal project test path can skip
  PNG generation when Pillow is not installed, while local Python with Pillow
  can generate ignored review-only PNG/JSON/HTML measurement artifacts under
  `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_style_spike/`.
  The report records 16 samples, bbox readback, safe-area readback,
  `review_only=true`, `production_candidate=false`, and
  `production_compatible=false`. `来ねぇ！！` is classified as
  `reaction_caption` / `bottom_center_emphasis` candidate, not ordinary
  `dialogue_badge_left` by default. ASS/libass remains the existing diagnostic
  proof path; Pillow/PNG is review-only measurement support and is not claimed
  to match YMM4, Premiere, ASS, or FFmpeg production rendering.
- next human review prompt:
  open the local file directly from the filesystem, not through a translation
  proxy or web-hosted viewer:
  `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_style_spike/subtitle_style_spike_report.html`
  First confirm the sibling PNG images render. Then review clean samples and
  explicit guide-overlay samples separately: the clean samples should not carry
  visual-only aids, while the guide-overlay samples may show safe-area/text-bbox
  aids only with authority labels and readback. Decide whether the current
  guides are helpful for subtitle placement / future face-icon work without
  implying layout authority. Only after that, choose the next narrow route:
  Japanese font-aware wrapping refinement, or port the same authority/provenance
  guardrail into `subtitle_overlay_visual_proof`. For the existing cut_003
  burned-in proof, open
  `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html`
  with player subtitle tracks disabled. Judge only the embedded burned-in
  subtitle. Answer whether the speaker-badge fallback plus left-aligned large
  subtitle is acceptable for diagnostic review, whether real face icons are
  required before the next candidate, whether text size/outline/position are
  readable enough for YouTube-style review, and whether the response/referral
  sample coverage is acceptable. Keep production subtitle design/render,
  creative, rights, publishing, and public-use acceptance unaccepted.
- previous resume-surface cleanup:
  `f725197 docs: update runtime resume commit readback`
- previous runtime docs refresh:
  `28f0256 docs: refresh operator review handoff`
- latest operator review implementation:
  `3d97e45 feat: improve operator review surfaces`
- latest chapter revision implementation:
  Chapter Revision Loop v0 adds a static board and JSON/CSV patch templates
  for R3 chapter-level operator decisions.
- latest cut decision implementation:
  R3 Cut Decision Packet classifies the 9 selected cuts into keep /
  needs_adjustment / reject and exposes `final_cut_decision` in
  `status-episode`.
- latest local visual proof readback:
  `build-subtitle-overlay-visual-proof` has regenerated ignored local
  diagnostic subtitle-overlay proof for explicit target cuts `cut_002` and
  `cut_003`. The refreshed `subtitle_overlay_visual_proof_report.*`,
  `subtitle_overlay_visual_proof_cut_002.*`,
  `subtitle_overlay_visual_proof_cut_003.*`, and
  `representative_visual_proof_report.*` exist under the R3 review directory.
  In the current local ignored artifact set, `status-episode` reports
  `operator_review.review_ready=true`; do not infer reviewability for a fresh
  checkout because it remains workspace-local and depends on ignored
  `episodes/` artifacts. The accepted current cut_003 proof/readback is
  `22.606 -> 49.566` with `sub_010..sub_029`, the
  response/referral block `sub_025..sub_029` included, and `sub_030` excluded.
  It is diagnostic proof evidence only and does not accept production subtitle
  design.
- latest diagnostic subtitle style readback:
  `jp_clip_readable_v1` remains the broad diagnostic direction, while
  `jp_clip_dialogue_reference_v0` is the tracked presentation contract for the
  current proof candidate. The current cut_003 probe uses an explicit ASS file
  with `ClipPipeSpeakerBadge` and `ClipPipeDialogueLeft` styles. The layout is
  formula-based from the probed 1920x1080 frame: `font_size=124`,
  `outline=12`, `bottom_margin=97`, `horizontal_margin=106`,
  `badge=124x87`, `badge_text_gap=37`, `line_height=143`, and
  `badge_center_y=dialogue_y + round(line_height*0.52)`. Left alignment is
  conditional to `badge_left_dialogue`; `bottom_center_emphasis` remains a
  supported alternative mode. Reference SRT remains away from the video
  basename and the VLC sidecar warning remains present. This does not create
  production subtitle design acceptance, production render acceptance, creative
  acceptance, rights approval, or public-use permission. The single human
  review entry point for this slice is
  `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html`.
- latest local proxy decision handoff:
  ED-10d adds the tracked `build-operator-proxy-decision-handoff` CLI and
  generator. `cut_002` / `cut_003` now have ignored text/proxy review files,
  operator proxy decision handoff files, and scoped Chapter Revision Patch
  templates. Templates preserve operator fields as blank, `undecided`, `noop`,
  or `none`; the filled operator patch is the current decision authority. The
  handoff keeps `cut_003` retained context risk and reads back source media as
  available from `material_ledger.json`. After the scoped overlay proof run,
  the regenerated ED-10d handoff reads
  `visual_proof_status=available_requires_human_review`. The scoped
  `proxy_decision` allowed values now include `proceed_with_limitations` for
  candidate-lane routing where explicit limitations or watch items remain
  visible. The timing and subtitle text readback for `cut_003` is current at
  `22.606 -> 49.566`. The accepted filled operator patch is stored separately
  as `.operator.json` / `.operator.csv` / `.operator.html`; templates remain
  blank/default and must not be overwritten with filled decisions. This filled
  patch records the narrow cut_003 route as
  `proxy_decision=proceed_with_limitations` and
  `context_risk_handling=keep_retained_risk_visible`, with subtitle visual
  readiness still `needs_adjustment`. This is still not creative acceptance,
  production acceptance, publishing acceptance, or rights approval. The narrow
  enum/readback validation ran
  `uvx pytest -q tests/test_operator_proxy_decision_handoff.py` -> 2 passed,
  regenerated the ignored ED-10d handoff/template artifacts, confirmed template
  defaults remain blank/undecided,
  `production_candidate=false`, `rights_status=pending`, and
  `git ls-files episodes` empty.
- latest boundary recommendation applier:
  ED-10e adds the tracked `apply-boundary-recommendation` CLI and
  `src/pipeline/boundary_recommendation_apply.py`. It consumes an
  operator-owned boundary recommendation report plus current `edit_pack.json`
  and writes a dry-run/blocking/apply receipt with current range validation,
  requested range readback, selected cut overlap detection, explicit overlap
  policy readback, subtitle reassignment readback, and production/rights
  boundary flags. Default remains safe: mutation requires explicit
  `--apply --overlap-policy shrink_or_split_cut_004 --transcript`. The actual
  same-machine local run wrote ignored
  `cut_003_boundary_apply_receipt.shrink_or_split_cut_004.json` / `.html` with
  `status=applied`: `cut_003` is now `22.606 -> 49.566` and owns
  `seg_000025..seg_000029`; `seg_000030` remains excluded from `cut_003`;
  `cut_004` is now `50.868 -> 60.277`, keeps `seg_000030..seg_000034`, and has
  `resegmentation_target=true`; `sub_025..sub_029` now point to `cut_003` and
  `sub_030` remains `cut_004`. It did not mutate transcript, official subtitle
  evidence, source media, typography, proof, or render artifacts. Validation:
  `uvx pytest -q tests/test_boundary_recommendation_apply.py` -> 9 passed;
  `validate-edit-pack` -> `schema_ok=true`.
- latest local downstream regeneration after the `cut_003` boundary apply:
  the current ignored authority now includes `edit_pack.json`,
  `cut_review_packet.json`, `evidence_summary.json`, corrected
  `cut_decision_packet.json`, regenerated `chapter_revision_board.json`,
  refreshed scoped `cut_002` / `cut_003` proxy handoff artifacts, and a
  regenerated ED-06 NLE export. `cut_003` is `22.606 -> 49.566` with
  `seg_000010..seg_000029` and `sub_010..sub_029`; `cut_004` is
  `50.868 -> 60.277` with `seg_000030..seg_000034`, `sub_030..sub_034`, and
  `resegmentation_target=true`. The latest ignored-only cleanup also updated
  `edit_pack.cut_candidates[].reason` for `cut_003` / `cut_004` so the NLE
  CSV/report title/reason matches the current ranges. `cut_review_packet.json`
  and `cut_decision_packet.json` still contain stale `candidate_reason` prose
  for those cuts; treat that as the next narrow readback-cleanup watch item if
  those packet fields will be human-facing.
- latest Review Contract Taxonomy audit:
  the regenerated cut_003 proof/readback now matches current authority:
  `22.606 -> 49.566`, `sub_010..sub_029`,
  response/referral block `sub_025..sub_029` included, and `sub_030` excluded.
  The taxonomy audit passed the required gates with
  `blocking_limitations=none_detected` for proof-level gates. Human review
  accepted length and scene closure for diagnostic candidate review, but did
  not accept production subtitle design/readability. Keep
  [CUT_003_REVIEW_CONTRACT_TAXONOMY_AUDIT.md](CUT_003_REVIEW_CONTRACT_TAXONOMY_AUDIT.md)
  as the tracked audit-summary surface; the accepted filled decision itself is
  the ignored `.operator.*` patch, not the blank template.
- current bottleneck: cut_003 boundary and operator decision remain closed, and
  the separate Subtitle Design / Review UX diagnostic style probe is ready for
  human readability review. The remaining decision is whether the embedded
  burned-in subtitle inside the proof video is closer to YouTube-readable
  review style than the previous small/movie-subtitle-like proof, while keeping
  the reference SRT disabled as a player subtitle track. Rights remain pending,
  production/public use remains disallowed, and production subtitle design
  acceptance remains false until explicit human approval.
- reviewability rule: report `review_ready` only when the ignored R3 reports
  and representative visual proof artifacts are present in the current
  workspace. Fresh checkouts or workspaces missing ignored `episodes/`
  artifacts remain `review_blocked_missing_artifacts`.
- rights: `pending`
- production_candidate: `false`

ED-10 solved the caption-completeness blocker for this source by importing the
official YouTube JSON3 subtitle track into a transcript-compatible artifact.
SH-07 then made the operator review path Reviewability-first. On 2026-05-30
JST, the operator explicitly bypassed strict individual R3 cut review for
speed-first sample expansion. All 9 generated R3 cuts are accepted only as
`accept_candidate` candidate seeds; the 6 `needs_review` context results remain
retained risk and are not rewritten to `passed`.

Chapter Revision Loop v0 now gives those 9 candidate seeds stable chapter ids
`ch_001` through `ch_009` and keeps operator-written intent separate from the
source transcript and official subtitle track.

On 2026-06-02 JST, the operator advanced from speed-first sample expansion to
candidate triage. `cut_001`, `cut_002`, and `cut_003` are kept only as
candidates for the next acceptance slice. `cut_004` through `cut_008` are
`needs_adjustment`; `cut_009` is rejected. `cut_003` keeps its original
`needs_review` context status and requires the recorded manual override reason.
This is still not production acceptance, creative acceptance, publishing
acceptance, or rights approval.

On 2026-06-03 JST, local ignored reports were created for the kept candidate
mini-slice:

- `production_subtitle_render_acceptance_report.json` / `.html`
- `representative_visual_proof_report.json` / `.html`
- `visual_proof_cut_001.png`
- `visual_proof_cut_002.png`
- `visual_proof_cut_003.png`
- `visual_proof_contact_sheet.png`

These are under
`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/`
and are intentionally not in Git. The readback is conservative: `cut_001` has
subtitle-overlay diagnostic-frame evidence only, while `cut_002` and `cut_003`
are source-frame-only and do not prove subtitle typography, safe-area, line
wrapping, or timing sync. `cut_003` keeps retained context risk.

On 2026-06-04 JST, ED-10d made the scoped `cut_002` / `cut_003`
text/proxy decision handoff reproducible from tracked code and regenerated the
ignored local artifacts:

- `cut_002_cut_003_text_proxy_review.json` / `.html`
- `cut_002_cut_003_operator_proxy_decision_handoff.json` / `.html`
- `chapter_revision_patch.cut_002_cut_003_proxy.template.json` / `.csv`

These files are also ignored local artifacts under the same R3 review
directory. They record `source_media_status=available_from_material_ledger` for
`materials/src_video_jp_pilot01/source_video.mp4` and
`materials/src_audio_jp_pilot01/source.wav`, while preserving
`visual_proof_status=blocked_no_cut_002_cut_003_overlay_proof`. The older
root-level source media paths are not the current source of truth. This handoff
does not create production, creative, publishing, rights, typography,
safe-area, or timing acceptance.

Later on 2026-06-04 JST, a narrow Verify regenerated diagnostic subtitle-overlay
proof only for `cut_002` / `cut_003`. It used existing source media from
`material_ledger.json` and JSON-readable upstream inputs `edit_pack.json`,
`cut_decision_packet.json`, and `chapter_revision_board.json`. The generated
local ignored artifacts are:

- `representative_visual_proof_report.json` / `.html`
- `visual_proof_cut_002.png`
- `visual_proof_cut_003.png`
- `visual_proof_contact_sheet.png`

`visual_proof_cut_001.png` remains missing and was not regenerated by the
narrow instruction. The refreshed report records
`scope=cut_002_cut_003_diagnostic_subtitle_overlay_verify`,
`proof_generation_succeeded=true`, `restore_succeeded=false`,
`review_state=review_blocked_missing_artifacts`, `rights_status=pending`, and
`production_candidate=false`. This is local diagnostic overlay evidence only;
it is not production render acceptance, subtitle design acceptance, creative
acceptance, publishing acceptance, rights approval, or public-use permission.

On 2026-06-07 JST, the tracked
`build-subtitle-overlay-visual-proof` generator was rerun for explicit target
cuts `cut_002` and `cut_003`. It used
`materials/src_video_jp_pilot01/source_video.mp4`,
`materials/src_audio_jp_pilot01/source.wav`, `edit_pack.json`,
`material_ledger.json`, and the existing representative visual proof readback.
The regenerated ignored local artifacts are:

- `subtitle_overlay_visual_proof_report.json` / `.html`
- `subtitle_overlay_visual_proof_cut_002.mp4` / `.png` / `.srt`
- `subtitle_overlay_visual_proof_cut_003.mp4` / `.png` / `.srt`
- `representative_visual_proof_report.json` / `.html`

Readback confirmed `target_cuts=[cut_002, cut_003]`,
`source_media_status=available_from_material_ledger`,
`subtitle_overlay_available_count=2`, `all_target_cuts_have_overlay=true`,
`visual_proof_status=available_requires_human_review` after ED-10d
regeneration, `production_candidate=false`, `rights_status=pending`, and
`production_usage_allowed=false`. It also records
`style_direction.preset_name=jp_clip_readable_v1`, separates qualitative intent
from unpinned tactical style parameters, embeds/links the contact sheet and
proof PNG/MP4 artifacts in the HTML report, and flags `cut_002` as a
watch-only long-line risk at the EAW proxy threshold. This remains
diagnostic-only visual evidence and does not approve typography, safe-area,
timing sync, creative use, publishing, rights, or production render.

Regenerate the scoped overlay proof, when the required local R3 artifacts are
present, with:

```powershell
uvx python -m src.cli.main build-subtitle-overlay-visual-proof `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

Then regenerate the ED-10d proxy handoff with:

```powershell
uvx python -m src.cli.main build-operator-proxy-decision-handoff `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

## What To Read First

When this same-machine workspace has the ignored R3 reports and visual proof
artifacts, `status-episode` reports `review_ready`. Use the review reports in
the order below, and inspect the scoped overlay proof before filling the
`cut_002` / `cut_003` proxy decision fields.

If the refreshed representative visual proof report records
`review_blocked_missing_artifacts`, start with this scoped surface instead:

1. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html`

Use it only for visual inspection of the regenerated or partial diagnostic
overlay frames. Do not send the operator to `cut_review_report.html` as if the
workspace were globally `review_ready` while the report records a blocked
state.

When the representative proof artifacts are present or an explicit operator
waiver exists, and the R3 review artifacts are otherwise present, use the local
ignored review reports in this order:

1. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_review_report.html`
2. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/evidence_summary.html`
3. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/non_repo_artifact_handoff.html`
4. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_speed_pass.html`
5. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_report.html`
6. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/production_subtitle_render_acceptance_report.html`
7. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_text_proxy_review.html`
8. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_002_cut_003_operator_proxy_decision_handoff.html`
9. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html`
10. `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/chapter_revision_board.html`

In that state, the review artifacts are readable and the speed-first candidate
decision can be confirmed from `cut_decision_speed_pass.json` / `.html`. This
decision is sample expansion only, not production, creative, publishing, or
rights acceptance.

If `chapter_revision_board.html` is present, it is the operator working board
for chapter-level decisions. The corresponding templates are
`chapter_revision_patch.template.json` and
`chapter_revision_patch.template.csv`; defaults are blank or `undecided`.
When the scoped proxy templates are present, use
`chapter_revision_patch.cut_002_cut_003_proxy.template.json` / `.csv` for the
first `cut_002` / `cut_003` operator decision pass instead of asking the
operator to fill all 9 chapters at once.

When this is a fresh checkout or those ignored reports are missing, do not send
the operator to the HTML report as if review is ready. Read these instead:

1. [OPERATOR_REVIEW_UX.md](OPERATOR_REVIEW_UX.md)
2. [NON_REPO_ARTIFACT_HANDOFF.md](NON_REPO_ARTIFACT_HANDOFF.md)
3. the restore or regenerate route recorded in the non-repo handoff docs and
   generated manifests

Git alone does not contain `episodes/` artifacts, source media, render outputs,
or R3 review reports.

## Current Candidate Decision

The current cut decision packet classifies the 9 R3 cuts into:

- `keep`: `cut_001`, `cut_002`, `cut_003`
- `needs_adjustment`: `cut_004`, `cut_005`, `cut_006`, `cut_007`, `cut_008`
- `reject`: `cut_009`

The earlier speed-first sample expansion carried all 9 R3 cuts forward as
`accept_candidate` candidate seeds. The newer triage narrows the next acceptance
slice to 3 kept candidates. It does not resolve the 6 context `needs_review`
results; `cut_003` is kept with a manual override reason and the remaining
`needs_review` cuts stay in `needs_adjustment`. This is not production
acceptance, creative acceptance, publishing acceptance, or rights approval.

Absent an explicit operator instruction like the one above, the Agent must not
auto-accept, auto-reject, or auto-adjust final cuts.

Review focus:

- previous setup: does the cut start with enough context?
- following payoff: does the cut end before the useful response lands?
- boundary adjustment: would a small start/end shift make the cut usable?

## Source Identity

- YouTube ID: `7J5aS_pcBj4`
- subtitle track: `source_subs/7J5aS_pcBj4.ja.json3`
- transcript source: imported subtitle track / `youtube_subtitles`
- source video material id: `src_video_jp_pilot01`
- source audio material id: `src_audio_jp_pilot01`
- source video material path:
  `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4`
- source audio material path:
  `episodes/jp_pilot01_hololive_bancho_20260525/materials/src_audio_jp_pilot01/source.wav`
- rights status: `pending`
- production usage: not allowed until approval
- source URL: `https://www.youtube.com/watch?v=7J5aS_pcBj4`
  (from existing local docs metadata; do not access YouTube to refresh it)
- source title: unknown for this resume surface. Existing local docs preserve a
  title readback, but it is not refreshed here and should not be filled by
  external search.

## Boundaries

- Diagnostic render is not production, creative, or publish acceptance.
- Rights pending means production/public use is not allowed.
- `rendered_video.mp4`, source video/audio, subtitle track payloads, and
  episode artifacts must not be added to Git.
- `episodes/` is intentionally ignored.
- `build-non-repo-handoff` creates a manifest/report. It is not a render
  command and does not recreate `rendered_video.mp4`.
- Production render, publishing, OAuth, thumbnail setting, and rights approval
  are separate slices.
- R3 final cut review creates candidate seeds only; it does not make a
  production candidate.

## Next Actions

1. Review: current R3 review-ready surface
   - Open `cut_review_report.html` and `representative_visual_proof_report.html`
     in this same-machine workspace.
   - Confirm only local diagnostic readability / safe-area / line wrapping /
     timing impressions.
   - Keep `rights=pending`, `production_candidate=false`, and
     `production_usage_allowed=false`.
2. Advance: `cut_002` / `cut_003` operator proxy decision
   - `cut_002` is already in the candidate lane with
     `proxy_decision=proceed_with_limitations`; keep the long-line watch risk
     visible.
   - `cut_003` proxy decision is closed locally from the accepted filled
     `.operator.*` patch:
     `proxy_decision=proceed_with_limitations`,
     `context_risk_handling=keep_retained_risk_visible`; keep subtitle
     design/readability as a separate unaccepted limitation.
3. Advance: adjustment loop for retained R3 cuts
   - Use for `cut_004` through `cut_008`.
   - `cut_004` has been explicitly shrunk to start at `50.868s` and remains a
     resegmentation target before it can re-enter candidate status.
4. Verify: regenerated render comparison
   - Use when a workspace must compare regenerated diagnostics to prior R3
     artifacts.
   - Define when exact SHA-256 matters and when metadata approximate comparison
     is acceptable.
5. Clear Rights: rights approval path
   - Use before any production/public usage claim.
   - Keep this separate from local diagnostic success.
6. Prepare: publishing / OAuth / thumbnail
   - Keep this later until production acceptance and rights are no longer
     pending.

Publishing and OAuth work remain later; do not treat them as the immediate next
step.

## History / Archive Links

- Full historical closeouts:
  [RUNTIME_HISTORY.md](RUNTIME_HISTORY.md)
- Feature state:
  [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
- Operator response shape and reviewability states:
  [OPERATOR_REVIEW_UX.md](OPERATOR_REVIEW_UX.md)
- Non-repo artifact recovery and handoff boundary:
  [NON_REPO_ARTIFACT_HANDOFF.md](NON_REPO_ARTIFACT_HANDOFF.md)

## Restart Checklist

1. Check whether the R3 review artifacts exist in the ignored `episodes/`
   directory.
2. Report `review_ready` or `review_blocked_missing_artifacts` before listing
   commands.
3. Keep `rights=pending` and `production_candidate=false` visible.
4. Do not classify final cuts without explicit operator instruction. The
   2026-05-30 speed-first instruction applies only to candidate seeds, not
   production-approved cuts.
5. If the Chapter Revision Board exists, treat `script_override` as editorial
   layer only and do not add source transcript mutation fields.
6. Do not stage `episodes/`, source media, rendered video, subtitle payloads, or
   other large local artifacts.
