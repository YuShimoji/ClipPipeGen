"""Build the TRI-01 safety overcapture triage report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_ID = "clippipegen.safety_overcapture_triage.v0"
ARTIFACT_ID = "clip-tri01-safety-overcapture-triage-v0-001"
CLASSIFICATIONS = (
    "true_external_gate",
    "deferred_local_action",
    "allowed_local_action",
    "overcapture_candidate",
)
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


FINDINGS: list[dict[str, str]] = [
    {
        "id": "tri_true_public_publication_gate",
        "file": "docs/AUTOMATION_BOUNDARY.md",
        "line_or_pattern": "Production/public operations are hard-gated beyond this boundary",
        "classification": "true_external_gate",
        "why_it_matters": (
            "Upload, OAuth-backed publishing, visibility changes, public thumbnail "
            "setting, and public-ready claims leave the local diagnostic workflow."
        ),
        "risk_if_changed": (
            "Local planning or diagnostic success could be misread as permission to "
            "publish or expose media publicly."
        ),
        "recommended_action": (
            "Keep this as a strict external gate and point repeated docs back to the "
            "canonical boundary instead of restating it everywhere."
        ),
        "priority": "P0",
        "safe_next_slice": "rights_or_publishing_acceptance_slice_only",
    },
    {
        "id": "tri_true_oauth_credentials_gate",
        "file": (
            "origin/codex/ews-05-human-ok-fetch-prep-ready-v0:"
            "docs/content_planning/automation_contract.json"
        ),
        "line_or_pattern": "oauth_api_keys_credentials",
        "classification": "true_external_gate",
        "why_it_matters": (
            "Login-backed services, API keys, OAuth tokens, and credentials can create "
            "account or billing exposure outside repo-local automation."
        ),
        "risk_if_changed": (
            "A local helper could silently cross into authenticated service use or "
            "persist sensitive material in logs/artifacts."
        ),
        "recommended_action": (
            "Keep as a true gate in the thin automation contract; do not duplicate "
            "credential rules in every handoff."
        ),
        "priority": "P0",
        "safe_next_slice": "explicit_credentials_or_oauth_setup_slice",
    },
    {
        "id": "tri_true_rights_public_claim_gate",
        "file": "docs/AUTOMATION_BOUNDARY.md",
        "line_or_pattern": "rights / publishing acceptance slice",
        "classification": "true_external_gate",
        "why_it_matters": (
            "Rights approval and public-ready claims are judgement gates, not side "
            "effects of successful local fetch, transcript, render, or preview steps."
        ),
        "risk_if_changed": (
            "Pending or failed rights readback could be converted into production-use "
            "language by accident."
        ),
        "recommended_action": (
            "Keep strict, but express it once as a canonical contract key that downstream "
            "docs reference."
        ),
        "priority": "P0",
        "safe_next_slice": "rights_clearance_packet",
    },
    {
        "id": "tri_true_destructive_git_cross_repo_gate",
        "file": "AGENTS.md",
        "line_or_pattern": "destructive git operations / cross-project scope boundary",
        "classification": "true_external_gate",
        "why_it_matters": (
            "Reset, force push, history rewrite, and cross-repo edits can destroy user "
            "work or leave the ClipPipeGen scope."
        ),
        "risk_if_changed": (
            "A triage cleanup could remove unrelated local work or mutate NLMYTGen without "
            "an explicit cross-project request."
        ),
        "recommended_action": (
            "Keep as a stop condition. TRI follow-up work should remain path-scoped and "
            "ClipPipeGen-only."
        ),
        "priority": "P0",
        "safe_next_slice": "none_without_user_confirmation",
    },
    {
        "id": "tri_true_episode_media_tracking_gate",
        "file": "docs/RUNTIME_STATE.md",
        "line_or_pattern": "Do not stage episodes/",
        "classification": "true_external_gate",
        "why_it_matters": (
            "Ignored episode media, renders, subtitles, and local proof artifacts are "
            "same-machine evidence, not portable Git state."
        ),
        "risk_if_changed": (
            "Large or rights-sensitive media could enter Git and be pushed as if it were "
            "approved source material."
        ),
        "recommended_action": (
            "Keep strict and continue validating with git ls-files episodes."
        ),
        "priority": "P0",
        "safe_next_slice": "private_artifact_store_policy_if_needed",
    },
    {
        "id": "tri_deferred_source_url_opening",
        "file": "docs/content_planning/README.md",
        "line_or_pattern": "CPD-05 does not open source URLs",
        "classification": "deferred_local_action",
        "why_it_matters": (
            "Opening a known public URL for identity review is not the same as network "
            "fetch or media download, but it still needs an explicit human review moment."
        ),
        "risk_if_changed": (
            "Planning workers may either freeze unnecessarily or silently open external "
            "pages during offline-first slices."
        ),
        "recommended_action": (
            "Classify URL opening as deferred local/human action in the thin contract, "
            "separate from true publication gates."
        ),
        "priority": "P1",
        "safe_next_slice": "source_identity_review",
    },
    {
        "id": "tri_deferred_private_source_fetch_smoke",
        "file": (
            "origin/codex/ews-05-human-ok-fetch-prep-ready-v0:"
            "docs/CURRENT_HANDOFF.md"
        ),
        "line_or_pattern": "explicit_private_fetch_smoke_approval_required",
        "classification": "deferred_local_action",
        "why_it_matters": (
            "EWS-05 reaches fetch-prep readiness but still preserves fetch_authorized=false "
            "and media_downloaded=false."
        ),
        "risk_if_changed": (
            "A source identity OK record could be mistaken for actual fetch permission."
        ),
        "recommended_action": (
            "Keep private fetch smoke as a later explicit slice, with receipt and rollback "
            "readback."
        ),
        "priority": "P1",
        "safe_next_slice": "private_fetch_smoke_decision",
    },
    {
        "id": "tri_deferred_transcript_after_material",
        "file": (
            "origin/codex/ews-05-human-ok-fetch-prep-ready-v0:"
            "docs/content_planning/automation_contract.json"
        ),
        "line_or_pattern": '"action_id": "transcript"',
        "classification": "deferred_local_action",
        "why_it_matters": (
            "Transcription is local once media exists, but content-planning and "
            "fetch-prep slices should not jump into transcript generation."
        ),
        "risk_if_changed": (
            "Planning artifacts could start creating downstream episode evidence before "
            "source material is available and reviewed."
        ),
        "recommended_action": (
            "Keep transcript as deferred in planning contracts; allow it only in a local "
            "episode-material slice."
        ),
        "priority": "P2",
        "safe_next_slice": "local_transcript_generation_after_fetch",
    },
    {
        "id": "tri_deferred_render_after_source_material",
        "file": (
            "origin/codex/ews-05-human-ok-fetch-prep-ready-v0:"
            "docs/content_planning/automation_contract.json"
        ),
        "line_or_pattern": '"action_id": "render"',
        "classification": "deferred_local_action",
        "why_it_matters": (
            "Diagnostic render is allowed in the right lane, but it is not part of "
            "content-planning or fetch-prep readiness."
        ),
        "risk_if_changed": (
            "Workers may generate media proofs before the source/fetch/rights readback "
            "chain exists."
        ),
        "recommended_action": (
            "Keep render deferred for planning; route later work through render-tiny-proof "
            "with production_candidate=false."
        ),
        "priority": "P2",
        "safe_next_slice": "diagnostic_render_after_local_materials",
    },
    {
        "id": "tri_deferred_gui_fetch_button",
        "file": "docs/ASSET_FETCH_BOUNDARY.md",
        "line_or_pattern": "GUI fetch button is unimplemented",
        "classification": "deferred_local_action",
        "why_it_matters": (
            "A GUI-triggered fetch needs preflight, confirmation, receipt, rollback, and "
            "clear readback before it can be ergonomic."
        ),
        "risk_if_changed": (
            "Adding a button before the operator-visible contract exists would make media "
            "download feel like a casual UI action."
        ),
        "recommended_action": (
            "Keep deferred until the GUI contract can show exact command, source, output, "
            "and rollback information."
        ),
        "priority": "P2",
        "safe_next_slice": "gui_fetch_preflight_contract",
    },
    {
        "id": "tri_allowed_diagnostic_pending_rights",
        "file": "docs/AUTOMATION_BOUNDARY.md",
        "line_or_pattern": "Local diagnostic processing is allowed while rights_manifest.compliance_check.status is pending",
        "classification": "allowed_local_action",
        "why_it_matters": (
            "The project can keep moving on source fetch, transcript, cuts, context checks, "
            "subtitle drafts, NLE export, and diagnostic proof while rights stay as readback."
        ),
        "risk_if_changed": (
            "Over-blocking pending rights would prevent local evidence gathering and make "
            "review loops wait for legal/public decisions too early."
        ),
        "recommended_action": (
            "Keep allowed local diagnostics explicit while preserving production/public "
            "claim gates."
        ),
        "priority": "P1",
        "safe_next_slice": "diagnostic_local_work_with_rights_readback",
    },
    {
        "id": "tri_allowed_dry_run_fetch_plans",
        "file": "tests/test_source_audio_fetch.py; tests/test_source_video_fetch.py",
        "line_or_pattern": "dry_run_writes_nothing / will_call_subprocess is False",
        "classification": "allowed_local_action",
        "why_it_matters": (
            "Dry-run planning gives operators exact command and output readback without "
            "network, subprocess execution, or filesystem mutation."
        ),
        "risk_if_changed": (
            "Treating dry-run as unsafe would remove the safest way to review a future "
            "fetch operation."
        ),
        "recommended_action": (
            "Keep dry-run as allowed local action and preserve no-write/no-subprocess tests."
        ),
        "priority": "P1",
        "safe_next_slice": "fetch_preflight_review",
    },
    {
        "id": "tri_allowed_local_preview_pack",
        "file": "tests/test_asset_fetch_boundary.py",
        "line_or_pattern": "test_build_local_preview_pack_exposes_no_external_fetch_or_output_generation",
        "classification": "allowed_local_action",
        "why_it_matters": (
            "Read-only preview pack generation is an operator surface over existing local "
            "artifacts, not a fetch, render, upload, or acceptance step."
        ),
        "risk_if_changed": (
            "Preview tooling could be blocked with the same force as external media "
            "download even when it only summarizes existing state."
        ),
        "recommended_action": (
            "Keep preview pack allowed and assert it does not expose external fetch or "
            "output-generation modes."
        ),
        "priority": "P1",
        "safe_next_slice": "preview_surface_readback",
    },
    {
        "id": "tri_allowed_source_identity_decision_record",
        "file": (
            "origin/codex/ews-05-human-ok-fetch-prep-ready-v0:"
            "docs/content_planning/automation_contract.json"
        ),
        "line_or_pattern": "source_identity_decision_record",
        "classification": "allowed_local_action",
        "why_it_matters": (
            "Recording a human source identity decision as JSON is local state capture; it "
            "does not itself fetch, approve rights, or publish."
        ),
        "risk_if_changed": (
            "The workflow would need repeated chat memory instead of durable local decision "
            "records."
        ),
        "recommended_action": (
            "Keep as allowed local action and require later slices to consume the record "
            "without auto-authorizing fetch."
        ),
        "priority": "P1",
        "safe_next_slice": "source_identity_decision_intake",
    },
    {
        "id": "tri_allowed_source_registry_stub",
        "file": (
            "origin/codex/hub-01-external-source-registry-v0:"
            "docs/CURRENT_HANDOFF.md"
        ),
        "line_or_pattern": "network_used=false, media_downloaded=false, rights_approved=false, public_ready=false",
        "classification": "allowed_local_action",
        "why_it_matters": (
            "A local source registry can normalize fixture/manual rows for later review "
            "without live RSS fetch, metadata APIs, or media download."
        ),
        "risk_if_changed": (
            "Backlog/source discovery work may be blocked even when it is fixture-backed "
            "and non-authoritative."
        ),
        "recommended_action": (
            "Keep registry build allowed, with no auto-advance to source identity OK or "
            "fetch-ready."
        ),
        "priority": "P2",
        "safe_next_slice": "hub02_reviewed_registry_to_cpd_mapping",
    },
    {
        "id": "tri_allowed_rights_snapshot_not_hard_gate",
        "file": "tests/test_source_audio_fetch.py; tests/test_source_video_fetch.py",
        "line_or_pattern": 'rights_snapshot["hard_gate"] is False',
        "classification": "allowed_local_action",
        "why_it_matters": (
            "Fetch receipts preserve rights status as evidence while avoiding premature "
            "blocking of diagnostic local acquisition."
        ),
        "risk_if_changed": (
            "Local evidence gathering could stall on pending rights, or the opposite error "
            "could hide rights status entirely."
        ),
        "recommended_action": (
            "Keep snapshot readback and hard_gate=false together; do not convert it into "
            "production acceptance."
        ),
        "priority": "P1",
        "safe_next_slice": "receipt_readback_hardening",
    },
    {
        "id": "tri_overcapture_pipeline_term_scan",
        "file": "tests/test_asset_fetch_boundary.py",
        "line_or_pattern": 'forbidden_terms = ("ffmpeg", "yt-dlp", "youtube-dl") across src/pipeline/*.py',
        "classification": "overcapture_candidate",
        "why_it_matters": (
            "A broad literal scan can fail on explanatory strings or triage text even when "
            "there is no import, subprocess call, or executable media-tool path in the pipeline."
        ),
        "risk_if_changed": (
            "Removing the guard outright could let media-tool execution leak into editing "
            "core."
        ),
        "recommended_action": (
            "Replace or supplement the literal scan with import/call-site checks and a "
            "narrow allowlist for docs/readback prose."
        ),
        "priority": "P1",
        "safe_next_slice": "tri02_boundary_test_shape_rewrite",
    },
    {
        "id": "tri_overcapture_help_text_word_absence",
        "file": "tests/test_source_video_fetch.py",
        "line_or_pattern": '"render" not in help_text and "encode" not in help_text',
        "classification": "overcapture_candidate",
        "why_it_matters": (
            "A help message that says 'does not render or encode' could fail even though it "
            "communicates the correct safety boundary."
        ),
        "risk_if_changed": (
            "Loosening without replacement may allow real render/encode options to appear "
            "on fetch-source-video."
        ),
        "recommended_action": (
            "Assert absence of render/encode options or callable paths rather than absence "
            "of the words in explanatory help."
        ),
        "priority": "P1",
        "safe_next_slice": "tri02_cli_help_contract_test",
    },
    {
        "id": "tri_overcapture_exact_doc_string_contracts",
        "file": "tests/test_asset_fetch_boundary.py",
        "line_or_pattern": "required strings in ASSET_FETCH_BOUNDARY.md, YTDLP_AUDIO_SPEC.md, and YTDLP_VIDEO_SPEC.md",
        "classification": "overcapture_candidate",
        "why_it_matters": (
            "Exact wording tests preserve important boundaries but can block concise "
            "rewrites that keep the same executable contract."
        ),
        "risk_if_changed": (
            "Docs could drift away from the safety requirements if exact checks are removed "
            "without a structured replacement."
        ),
        "recommended_action": (
            "Move invariant checks to structured keys or focused section markers; keep prose "
            "free to compress historical caveats."
        ),
        "priority": "P2",
        "safe_next_slice": "tri02_structured_boundary_invariants",
    },
    {
        "id": "tri_overcapture_spec_only_history_conflict",
        "file": "docs/ASSET_FETCH_BOUNDARY.md",
        "line_or_pattern": "spec only paragraphs preserved beside later implemented notes",
        "classification": "overcapture_candidate",
        "why_it_matters": (
            "Historical 'spec only' language remains near implemented INT-02e/INT-02h "
            "status, which can make implemented local fetch modes look forbidden."
        ),
        "risk_if_changed": (
            "Deleting history blindly could erase the reason fetch is isolated inside "
            "asset_fetch."
        ),
        "recommended_action": (
            "Compress historical status into a versioned status table while keeping active "
            "mode contracts and receipt requirements."
        ),
        "priority": "P2",
        "safe_next_slice": "tri03_asset_fetch_boundary_docs_compression",
    },
    {
        "id": "tri_overcapture_dashboard_boundary_term_heuristic",
        "file": "src/pipeline/docs_dashboard.py",
        "line_or_pattern": "BOUNDARY_TERMS and over_guarded doc health finding",
        "classification": "overcapture_candidate",
        "why_it_matters": (
            "The dashboard usefully detects caveat-heavy docs, but term frequency alone "
            "can flag necessary strict gate language as over-guarded."
        ),
        "risk_if_changed": (
            "Removing the heuristic would hide genuine docs bloat and stale safety copy."
        ),
        "recommended_action": (
            "Teach the dashboard to recognize canonical contract references separately "
            "from repeated free-text caveats."
        ),
        "priority": "P2",
        "safe_next_slice": "tri03_docs_dashboard_contract_reference_detection",
    },
    {
        "id": "tri_overcapture_handoff_caveat_repetition",
        "file": "docs/CURRENT_HANDOFF.md; docs/RUNTIME_STATE.md",
        "line_or_pattern": "repeated production/public/rights/publishing/monetization caveat chains",
        "classification": "overcapture_candidate",
        "why_it_matters": (
            "Resume surfaces repeat long caveat chains so often that the next executable "
            "local action becomes harder to see."
        ),
        "risk_if_changed": (
            "Over-compression could hide true gates from a fresh terminal."
        ),
        "recommended_action": (
            "Reference a thin automation contract for repeated gates and keep only the "
            "current slice deltas in handoff prose."
        ),
        "priority": "P2",
        "safe_next_slice": "tri03_resume_surface_safety_compression",
    },
]


EXECUTION_PATH_TESTS = [
    {
        "file": "tests/test_source_audio_fetch.py",
        "test": "test_fetch_source_audio_ytdlp_audio_dry_run_writes_nothing",
        "why": "Checks no write/no subprocess dry-run command planning.",
    },
    {
        "file": "tests/test_source_audio_fetch.py",
        "test": "test_fetch_source_audio_ytdlp_audio_creates_receipt_without_rights_hard_gate",
        "why": "Checks receipt/sidecar/ledger behavior and rights snapshot readback.",
    },
    {
        "file": "tests/test_source_video_fetch.py",
        "test": "test_fetch_source_video_yt_dlp_video_creates_artifacts",
        "why": "Checks source video artifact creation, scrubbed receipt, and ledger output.",
    },
    {
        "file": "tests/test_source_video_fetch.py",
        "test": "test_fetch_source_video_yt_dlp_video_unsupported_container_no_writes",
        "why": "Checks cleanup/no-write behavior on unsupported container failure.",
    },
    {
        "file": "tests/test_boundary_recommendation_apply.py",
        "test": "test_receipt_preserves_evidence_and_production_boundaries",
        "why": "Checks mutation boundaries and production_usage_allowed=false readback.",
    },
]

WORDING_ONLY_OR_HYBRID_TESTS = [
    {
        "file": "tests/test_asset_fetch_boundary.py",
        "test": "test_ytdlp_audio_spec_keeps_url_fetch_boundaries_explicit",
        "why": "Mostly checks doc wording/contract phrases.",
    },
    {
        "file": "tests/test_asset_fetch_boundary.py",
        "test": "test_ytdlp_video_spec_keeps_url_fetch_boundaries_explicit",
        "why": "Mostly checks doc wording/contract phrases.",
    },
    {
        "file": "tests/test_asset_fetch_boundary.py",
        "test": "test_ffmpeg_and_ytdlp_do_not_enter_pipeline_or_editing_cli",
        "why": "Structural intent, but currently implemented as literal term scanning.",
    },
    {
        "file": "tests/test_source_video_fetch.py",
        "test": "test_fetch_source_video_help_exposes_yt_dlp_video_options",
        "why": "Hybrid CLI contract; render/encode checks are word absence.",
    },
    {
        "file": "tests/test_docs_dashboard.py",
        "test": "test_docs_dashboard_detects_unclear_and_over_guarded_docs",
        "why": "Docs-health heuristic checks prose shape rather than runtime behavior.",
    },
]


STRICT_SAFETY_AREAS = [
    "Public upload, publishing, visibility change, public thumbnail setting, and public-ready claims.",
    "OAuth, API keys, credentials, login-backed services, payment, and paid provider use.",
    "Rights/legal approval claims and any conversion of pending rights into production use.",
    "Destructive git operations, history rewrite, broad cleanup, and cross-repo edits.",
    "Tracking ignored episodes media, rendered media, subtitle payloads, or source assets in Git.",
    "Secret-bearing URLs, full stderr, signed tokens, or credentials in receipts and command summaries.",
]

COMPRESSION_TARGETS = [
    {
        "target": "docs/content_planning/automation_contract.json or equivalent",
        "compress": (
            "Repeated allowed/deferred/true-gate lists across handoffs and planning docs."
        ),
        "keep_explicit": "Current slice deltas and any true stop condition.",
    },
    {
        "target": "docs/AUTOMATION_BOUNDARY.md",
        "compress": (
            "Historical per-slice repetition into current allowed/deferred/strict tables."
        ),
        "keep_explicit": "Integration ownership and production/public hard gates.",
    },
    {
        "target": "docs/ASSET_FETCH_BOUNDARY.md",
        "compress": (
            "Spec-only historical paragraphs now followed by implemented INT-02e/INT-02h notes."
        ),
        "keep_explicit": "Active mode contracts, dry-run, receipt, rollback, URL scrub, and tool containment.",
    },
    {
        "target": "docs/CURRENT_HANDOFF.md and docs/RUNTIME_STATE.md",
        "compress": (
            "Repeated production/public/rights/publishing caveat chains into a pointer to the thin contract."
        ),
        "keep_explicit": "The active artifact, current next gate, and tracked episodes prohibition.",
    },
    {
        "target": "src/pipeline/docs_dashboard.py",
        "compress": (
            "Term-frequency over_guarded detection into contract-reference-aware docs health."
        ),
        "keep_explicit": "Warnings for stale or unclear docs that do not expose a current next action.",
    },
]


def _count_by_classification(findings: list[dict[str, str]]) -> dict[str, int]:
    return {
        classification: sum(
            1 for finding in findings if finding["classification"] == classification
        )
        for classification in CLASSIFICATIONS
    }


def _highest_priority_overcapture(
    findings: list[dict[str, str]],
) -> list[dict[str, str]]:
    overcapture = [
        finding
        for finding in findings
        if finding["classification"] == "overcapture_candidate"
    ]
    overcapture.sort(key=lambda item: (PRIORITY_ORDER[item["priority"]], item["id"]))
    top_priority = PRIORITY_ORDER[overcapture[0]["priority"]]
    return [
        {
            "id": finding["id"],
            "priority": finding["priority"],
            "file": finding["file"],
            "recommended_action": finding["recommended_action"],
        }
        for finding in overcapture
        if PRIORITY_ORDER[finding["priority"]] == top_priority
    ]


def build_report(*, generated_at: str = "2026-07-08") -> dict[str, Any]:
    findings = [dict(finding) for finding in FINDINGS]
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": ARTIFACT_ID,
        "generated_at": generated_at,
        "scope": {
            "active_slice": "TRI-01 Safety Overcapture / Constraint Triage v0",
            "repo": "ClipPipeGen",
            "behavior_changed": False,
            "safety_behavior_loosened": False,
            "base_reference": "origin/main as fetched on 2026-07-08",
            "working_branch": "codex/tri-01-safety-overcapture-triage-v0",
            "reference_branches": [
                "origin/codex/ews-05-human-ok-fetch-prep-ready-v0",
                "origin/codex/hub-01-external-source-registry-v0",
            ],
        },
        "summary": {
            "count_by_classification": _count_by_classification(findings),
            "highest_priority_overcapture_candidates": (
                _highest_priority_overcapture(findings)
            ),
            "tests_likely_execution_path": EXECUTION_PATH_TESTS,
            "tests_likely_wording_only_or_hybrid": WORDING_ONLY_OR_HYBRID_TESTS,
            "places_safety_should_remain_strict": STRICT_SAFETY_AREAS,
            "places_safety_should_be_compressed": COMPRESSION_TARGETS,
        },
        "findings": findings,
        "validation_plan": [
            "python -m tools.triage.build_safety_overcapture_report --output-json docs/triage/safety_overcapture_report.json --output-md docs/triage/safety_overcapture_report.md --format json",
            "python -m json.tool docs/triage/safety_overcapture_report.json",
            "python -m pytest -q tests/test_safety_overcapture_triage.py",
            "git diff --check",
            "git ls-files episodes",
        ],
        "limitations": [
            "This triage does not change runtime safety behavior.",
            "Remote branch references are readback evidence only and are not merged by this artifact.",
            "Overcapture candidates are recommendations for later slices, not test loosening in TRI-01.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    counts = summary["count_by_classification"]
    findings = report["findings"]
    top = summary["highest_priority_overcapture_candidates"]
    lines = [
        "# TRI-01 Safety Overcapture Report",
        "",
        f"artifact_id: `{report['artifact_id']}`",
        f"generated_at: `{report['generated_at']}`",
        "",
        "TRI-01 is a readback-only triage. It does not change fetch, render, "
        "rights, publishing, credential, git, or media-tracking behavior.",
        "",
        "## Classification Counts",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for classification in CLASSIFICATIONS:
        lines.append(f"| `{classification}` | {counts[classification]} |")
    lines.extend(
        [
            "",
            "## Highest Priority Overcapture Candidates",
            "",
            "| ID | Priority | File | Recommended action |",
            "|---|---|---|---|",
        ]
    )
    for item in top:
        lines.append(
            "| `{id}` | `{priority}` | `{file}` | {recommended_action} |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            "| ID | Classification | Priority | File / pattern | Recommended action |",
            "|---|---|---|---|---|",
        ]
    )
    for finding in findings:
        file_pattern = f"`{finding['file']}`<br>{finding['line_or_pattern']}"
        lines.append(
            "| `{id}` | `{classification}` | `{priority}` | {file_pattern} | {recommended_action} |".format(
                file_pattern=file_pattern,
                **finding,
            )
        )
    lines.extend(
        [
            "",
            "## Execution-Path Tests",
            "",
            "| Test | File | Why it matters |",
            "|---|---|---|",
        ]
    )
    for item in summary["tests_likely_execution_path"]:
        lines.append(f"| `{item['test']}` | `{item['file']}` | {item['why']} |")
    lines.extend(
        [
            "",
            "## Wording-Only Or Hybrid Tests",
            "",
            "| Test | File | Why it can overcapture |",
            "|---|---|---|",
        ]
    )
    for item in summary["tests_likely_wording_only_or_hybrid"]:
        lines.append(f"| `{item['test']}` | `{item['file']}` | {item['why']} |")
    lines.extend(
        [
            "",
            "## Safety That Should Remain Strict",
            "",
        ]
    )
    for item in summary["places_safety_should_remain_strict"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Compression Targets",
            "",
            "| Target | Compress | Keep explicit |",
            "|---|---|---|",
        ]
    )
    for item in summary["places_safety_should_be_compressed"]:
        lines.append(
            f"| `{item['target']}` | {item['compress']} | {item['keep_explicit']} |"
        )
    lines.extend(
        [
            "",
            "## Validation Plan",
            "",
        ]
    )
    for command in report["validation_plan"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines) + "\n"


def write_report(
    *,
    output_json: Path,
    output_md: Path,
    generated_at: str = "2026-07-08",
) -> dict[str, Any]:
    report = build_report(generated_at=generated_at)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    _write_text_lf(
        output_json,
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(output_md, render_markdown(report))
    return report


def _write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("docs/triage/safety_overcapture_report.json"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("docs/triage/safety_overcapture_report.md"),
    )
    parser.add_argument("--generated-at", default="2026-07-08")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)

    report = write_report(
        output_json=args.output_json,
        output_md=args.output_md,
        generated_at=args.generated_at,
    )
    if args.format == "json":
        print(
            json.dumps(
                {
                    "artifact_id": report["artifact_id"],
                    "json_path": str(args.output_json),
                    "markdown_path": str(args.output_md),
                    "finding_count": len(report["findings"]),
                    "count_by_classification": report["summary"][
                        "count_by_classification"
                    ],
                    "behavior_changed": report["scope"]["behavior_changed"],
                    "safety_behavior_loosened": report["scope"][
                        "safety_behavior_loosened"
                    ],
                },
                ensure_ascii=False,
            )
        )
    else:
        print(f"wrote {args.output_json} and {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
