# TRI-01 Safety Overcapture Report

artifact_id: `clip-tri01-safety-overcapture-triage-v0-001`
generated_at: `2026-07-08`

TRI-01 is a readback-only triage. It does not change fetch, render, rights, publishing, credential, git, or media-tracking behavior.

## Classification Counts

| Classification | Count |
|---|---:|
| `true_external_gate` | 5 |
| `deferred_local_action` | 5 |
| `allowed_local_action` | 6 |
| `overcapture_candidate` | 6 |

## Highest Priority Overcapture Candidates

| ID | Priority | File | Recommended action |
|---|---|---|---|
| `tri_overcapture_help_text_word_absence` | `P1` | `tests/test_source_video_fetch.py` | Assert absence of render/encode options or callable paths rather than absence of the words in explanatory help. |
| `tri_overcapture_pipeline_term_scan` | `P1` | `tests/test_asset_fetch_boundary.py` | Replace or supplement the literal scan with import/call-site checks and a narrow allowlist for docs/readback prose. |

## Findings

| ID | Classification | Priority | File / pattern | Recommended action |
|---|---|---|---|---|
| `tri_true_public_publication_gate` | `true_external_gate` | `P0` | `docs/AUTOMATION_BOUNDARY.md`<br>Production/public operations are hard-gated beyond this boundary | Keep this as a strict external gate and point repeated docs back to the canonical boundary instead of restating it everywhere. |
| `tri_true_oauth_credentials_gate` | `true_external_gate` | `P0` | `origin/codex/ews-05-human-ok-fetch-prep-ready-v0:docs/content_planning/automation_contract.json`<br>oauth_api_keys_credentials | Keep as a true gate in the thin automation contract; do not duplicate credential rules in every handoff. |
| `tri_true_rights_public_claim_gate` | `true_external_gate` | `P0` | `docs/AUTOMATION_BOUNDARY.md`<br>rights / publishing acceptance slice | Keep strict, but express it once as a canonical contract key that downstream docs reference. |
| `tri_true_destructive_git_cross_repo_gate` | `true_external_gate` | `P0` | `AGENTS.md`<br>destructive git operations / cross-project scope boundary | Keep as a stop condition. TRI follow-up work should remain path-scoped and ClipPipeGen-only. |
| `tri_true_episode_media_tracking_gate` | `true_external_gate` | `P0` | `docs/RUNTIME_STATE.md`<br>Do not stage episodes/ | Keep strict and continue validating with git ls-files episodes. |
| `tri_deferred_source_url_opening` | `deferred_local_action` | `P1` | `docs/content_planning/README.md`<br>CPD-05 does not open source URLs | Classify URL opening as deferred local/human action in the thin contract, separate from true publication gates. |
| `tri_deferred_private_source_fetch_smoke` | `deferred_local_action` | `P1` | `origin/codex/ews-05-human-ok-fetch-prep-ready-v0:docs/CURRENT_HANDOFF.md`<br>explicit_private_fetch_smoke_approval_required | Keep private fetch smoke as a later explicit slice, with receipt and rollback readback. |
| `tri_deferred_transcript_after_material` | `deferred_local_action` | `P2` | `origin/codex/ews-05-human-ok-fetch-prep-ready-v0:docs/content_planning/automation_contract.json`<br>"action_id": "transcript" | Keep transcript as deferred in planning contracts; allow it only in a local episode-material slice. |
| `tri_deferred_render_after_source_material` | `deferred_local_action` | `P2` | `origin/codex/ews-05-human-ok-fetch-prep-ready-v0:docs/content_planning/automation_contract.json`<br>"action_id": "render" | Keep render deferred for planning; route later work through render-tiny-proof with production_candidate=false. |
| `tri_deferred_gui_fetch_button` | `deferred_local_action` | `P2` | `docs/ASSET_FETCH_BOUNDARY.md`<br>GUI fetch button is unimplemented | Keep deferred until the GUI contract can show exact command, source, output, and rollback information. |
| `tri_allowed_diagnostic_pending_rights` | `allowed_local_action` | `P1` | `docs/AUTOMATION_BOUNDARY.md`<br>Local diagnostic processing is allowed while rights_manifest.compliance_check.status is pending | Keep allowed local diagnostics explicit while preserving production/public claim gates. |
| `tri_allowed_dry_run_fetch_plans` | `allowed_local_action` | `P1` | `tests/test_source_audio_fetch.py; tests/test_source_video_fetch.py`<br>dry_run_writes_nothing / will_call_subprocess is False | Keep dry-run as allowed local action and preserve no-write/no-subprocess tests. |
| `tri_allowed_local_preview_pack` | `allowed_local_action` | `P1` | `tests/test_asset_fetch_boundary.py`<br>test_build_local_preview_pack_exposes_no_external_fetch_or_output_generation | Keep preview pack allowed and assert it does not expose external fetch or output-generation modes. |
| `tri_allowed_source_identity_decision_record` | `allowed_local_action` | `P1` | `origin/codex/ews-05-human-ok-fetch-prep-ready-v0:docs/content_planning/automation_contract.json`<br>source_identity_decision_record | Keep as allowed local action and require later slices to consume the record without auto-authorizing fetch. |
| `tri_allowed_source_registry_stub` | `allowed_local_action` | `P2` | `origin/codex/hub-01-external-source-registry-v0:docs/CURRENT_HANDOFF.md`<br>network_used=false, media_downloaded=false, rights_approved=false, public_ready=false | Keep registry build allowed, with no auto-advance to source identity OK or fetch-ready. |
| `tri_allowed_rights_snapshot_not_hard_gate` | `allowed_local_action` | `P1` | `tests/test_source_audio_fetch.py; tests/test_source_video_fetch.py`<br>rights_snapshot["hard_gate"] is False | Keep snapshot readback and hard_gate=false together; do not convert it into production acceptance. |
| `tri_overcapture_pipeline_term_scan` | `overcapture_candidate` | `P1` | `tests/test_asset_fetch_boundary.py`<br>forbidden_terms = ("ffmpeg", "yt-dlp", "youtube-dl") across src/pipeline/*.py | Replace or supplement the literal scan with import/call-site checks and a narrow allowlist for docs/readback prose. |
| `tri_overcapture_help_text_word_absence` | `overcapture_candidate` | `P1` | `tests/test_source_video_fetch.py`<br>"render" not in help_text and "encode" not in help_text | Assert absence of render/encode options or callable paths rather than absence of the words in explanatory help. |
| `tri_overcapture_exact_doc_string_contracts` | `overcapture_candidate` | `P2` | `tests/test_asset_fetch_boundary.py`<br>required strings in ASSET_FETCH_BOUNDARY.md, YTDLP_AUDIO_SPEC.md, and YTDLP_VIDEO_SPEC.md | Move invariant checks to structured keys or focused section markers; keep prose free to compress historical caveats. |
| `tri_overcapture_spec_only_history_conflict` | `overcapture_candidate` | `P2` | `docs/ASSET_FETCH_BOUNDARY.md`<br>spec only paragraphs preserved beside later implemented notes | Compress historical status into a versioned status table while keeping active mode contracts and receipt requirements. |
| `tri_overcapture_dashboard_boundary_term_heuristic` | `overcapture_candidate` | `P2` | `src/pipeline/docs_dashboard.py`<br>BOUNDARY_TERMS and over_guarded doc health finding | Teach the dashboard to recognize canonical contract references separately from repeated free-text caveats. |
| `tri_overcapture_handoff_caveat_repetition` | `overcapture_candidate` | `P2` | `docs/CURRENT_HANDOFF.md; docs/RUNTIME_STATE.md`<br>repeated production/public/rights/publishing/monetization caveat chains | Reference a thin automation contract for repeated gates and keep only the current slice deltas in handoff prose. |

## Execution-Path Tests

| Test | File | Why it matters |
|---|---|---|
| `test_fetch_source_audio_ytdlp_audio_dry_run_writes_nothing` | `tests/test_source_audio_fetch.py` | Checks no write/no subprocess dry-run command planning. |
| `test_fetch_source_audio_ytdlp_audio_creates_receipt_without_rights_hard_gate` | `tests/test_source_audio_fetch.py` | Checks receipt/sidecar/ledger behavior and rights snapshot readback. |
| `test_fetch_source_video_yt_dlp_video_creates_artifacts` | `tests/test_source_video_fetch.py` | Checks source video artifact creation, scrubbed receipt, and ledger output. |
| `test_fetch_source_video_yt_dlp_video_unsupported_container_no_writes` | `tests/test_source_video_fetch.py` | Checks cleanup/no-write behavior on unsupported container failure. |
| `test_receipt_preserves_evidence_and_production_boundaries` | `tests/test_boundary_recommendation_apply.py` | Checks mutation boundaries and production_usage_allowed=false readback. |

## Wording-Only Or Hybrid Tests

| Test | File | Why it can overcapture |
|---|---|---|
| `test_ytdlp_audio_spec_keeps_url_fetch_boundaries_explicit` | `tests/test_asset_fetch_boundary.py` | Mostly checks doc wording/contract phrases. |
| `test_ytdlp_video_spec_keeps_url_fetch_boundaries_explicit` | `tests/test_asset_fetch_boundary.py` | Mostly checks doc wording/contract phrases. |
| `test_ffmpeg_and_ytdlp_do_not_enter_pipeline_or_editing_cli` | `tests/test_asset_fetch_boundary.py` | Structural intent, but currently implemented as literal term scanning. |
| `test_fetch_source_video_help_exposes_yt_dlp_video_options` | `tests/test_source_video_fetch.py` | Hybrid CLI contract; render/encode checks are word absence. |
| `test_docs_dashboard_detects_unclear_and_over_guarded_docs` | `tests/test_docs_dashboard.py` | Docs-health heuristic checks prose shape rather than runtime behavior. |

## Safety That Should Remain Strict

- Public upload, publishing, visibility change, public thumbnail setting, and public-ready claims.
- OAuth, API keys, credentials, login-backed services, payment, and paid provider use.
- Rights/legal approval claims and any conversion of pending rights into production use.
- Destructive git operations, history rewrite, broad cleanup, and cross-repo edits.
- Tracking ignored episodes media, rendered media, subtitle payloads, or source assets in Git.
- Secret-bearing URLs, full stderr, signed tokens, or credentials in receipts and command summaries.

## Compression Targets

| Target | Compress | Keep explicit |
|---|---|---|
| `docs/content_planning/automation_contract.json or equivalent` | Repeated allowed/deferred/true-gate lists across handoffs and planning docs. | Current slice deltas and any true stop condition. |
| `docs/AUTOMATION_BOUNDARY.md` | Historical per-slice repetition into current allowed/deferred/strict tables. | Integration ownership and production/public hard gates. |
| `docs/ASSET_FETCH_BOUNDARY.md` | Spec-only historical paragraphs now followed by implemented INT-02e/INT-02h notes. | Active mode contracts, dry-run, receipt, rollback, URL scrub, and tool containment. |
| `docs/CURRENT_HANDOFF.md and docs/RUNTIME_STATE.md` | Repeated production/public/rights/publishing caveat chains into a pointer to the thin contract. | The active artifact, current next gate, and tracked episodes prohibition. |
| `src/pipeline/docs_dashboard.py` | Term-frequency over_guarded detection into contract-reference-aware docs health. | Warnings for stale or unclear docs that do not expose a current next action. |

## Validation Plan

- `python -m tools.triage.build_safety_overcapture_report --output-json docs/triage/safety_overcapture_report.json --output-md docs/triage/safety_overcapture_report.md --format json`
- `python -m json.tool docs/triage/safety_overcapture_report.json`
- `python -m pytest -q tests/test_safety_overcapture_triage.py`
- `git diff --check`
- `git ls-files episodes`
