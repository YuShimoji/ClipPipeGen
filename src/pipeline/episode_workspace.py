"""EWS-01 episode workspace spine builder.

This module turns the CPD-12 current work item into a local-only episode
workspace plan plus a thin automation contract. It never opens source URLs,
fetches media, creates transcripts/renders, or approves rights/public use.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .content_planning import display_path, write_json, write_text

PLAN_SCHEMA_ID = "clippipegen.episode_workspace_plan.v0"
CONTRACT_SCHEMA_ID = "clippipegen.automation_contract.v0"
MANIFEST_SCHEMA_ID = "clippipegen.episode_workspace_manifest.v0"
DEFAULT_ARTIFACT_ID = "clip-ews01-episode-workspace-spine-v0-001"
DEFAULT_CONTRACT_ARTIFACT_ID = "clip-ews01-thin-gate-contract-v0-001"
INSPECTOR_ARTIFACT_ID = "clip-ews02-episode-workspace-inspector-v0-001"
SOURCE_DECISION_ARTIFACT_ID = "clip-ews03-source-identity-decision-intake-v0-001"
SOURCE_FETCH_PREP_ARTIFACT_ID = "clip-ews04-source-fetch-prep-planner-v0-001"
DEFAULT_GENERATED_AT = "2026-07-07"
DEFAULT_PLAN_FILENAME = "episode_workspace_plan.json"
DEFAULT_CONTRACT_FILENAME = "automation_contract.json"
INSPECTION_SCHEMA_ID = "clippipegen.episode_workspace_inspection.v0"
SOURCE_DECISION_SCHEMA_ID = "clippipegen.source_identity_decision.v0"
SOURCE_FETCH_PREP_SCHEMA_ID = "clippipegen.source_fetch_prep_plan.v0"
SOURCE_DECISION_TEMPLATE_FILENAME = "source_identity_decision.template.json"
SOURCE_DECISION_RECORD_FILENAME = "source_identity.decision.json"
SOURCE_FETCH_PREP_PLAN_FILENAME = "source_fetch_prep_plan.json"
ALLOWED_SOURCE_IDENTITY_DECISIONS = ("pending", "ok", "ng", "hold")
MEDIA_LIKE_EXTENSIONS = {
    ".aac",
    ".ass",
    ".avi",
    ".flac",
    ".jpeg",
    ".jpg",
    ".m4a",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".png",
    ".srt",
    ".wav",
    ".webm",
}


class EpisodeWorkspaceError(ValueError):
    """Raised when an episode workspace plan or skeleton cannot be built."""


def build_episode_workspace_plan(
    *,
    operator_cockpit_path: Path,
    output_path: Path,
    contract_output_path: Path,
    base_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
    contract_artifact_id: str = DEFAULT_CONTRACT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Build the EWS-01 plan and thin gate contract from CPD-12 JSON."""

    cockpit = load_json_object(operator_cockpit_path, "operator cockpit")
    current = required_object(cockpit, "current_work_item", "operator cockpit")
    gate_readback = required_object(cockpit, "gate_readback", "operator cockpit")
    contract = build_automation_contract_payload(
        generated_at=generated_at,
        artifact_id=contract_artifact_id,
    )
    episode_id = derive_episode_id(current)
    paths = planned_paths(episode_id)
    blocked_true_gates = [
        item["action_id"] for item in contract["true_external_gates"]
    ]
    deferred_local_actions = [
        item["action_id"] for item in contract["deferred_local_actions"]
    ]
    source_url = clean_string(current.get("source_url"))
    fetch_authorized = bool(current.get("fetch_authorized"))

    plan = {
        "schema_id": PLAN_SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": {
            "operator_cockpit_json": display_path(operator_cockpit_path, base_dir),
            "operator_artifact_id": clean_string(cockpit.get("artifact_id")),
            "operator_ux_version": clean_string((cockpit.get("ux") or {}).get("version")),
            "current_work_item_id": clean_string(current.get("work_item_id")),
            "source_url_opened_by_worker": False,
            "network_required": False,
            "external_api_used": False,
        },
        "automation_contract": {
            "path": display_path(contract_output_path, base_dir),
            "artifact_id": contract["artifact_id"],
            "local_workspace_init_is_true_external_gate": False,
        },
        "episode_id": episode_id,
        "planned_slug": episode_id,
        "planning_label": clean_string(current.get("planning_label") or current.get("title")),
        "label_provenance": clean_string(current.get("label_provenance"))
        or "planning_label_unverified",
        "verified_video_title": "",
        "source_url": source_url,
        "source_url_state": clean_string(current.get("source_url_state")) or "unknown",
        "identity_state": clean_string(current.get("identity_state")) or "unverified",
        "fetch_authorized": False,
        "local_workspace_state": "planned",
        "planned_paths": paths,
        "next_allowed_local_action": {
            "action_id": "init_episode_workspace_explicit_target",
            "command": (
                "python -m src.cli.main init-episode-workspace --plan "
                f"{display_path(output_path, base_dir)} --target <tempdir> --materialize"
            ),
            "requires_explicit_target": True,
            "writes_media": False,
            "opens_source_url": False,
        },
        "deferred_local_actions": deferred_local_actions,
        "blocked_true_gates": blocked_true_gates,
        "thin_gate_contract_summary": (
            "Local JSON and explicit-target skeleton initialization are allowed; "
            "source opening/fetch/media/transcript/render/thumbnail processing are "
            "deferred local actions, while publication/auth/payment/legal/destructive "
            "operations remain true external gates."
        ),
        "readback": {
            "planning_label_is_verified_video_title": False,
            "source_url_opened_by_worker": False,
            "fetch_authorized": False,
            "media_downloaded": False,
            "transcript_generated": False,
            "render_generated": False,
            "thumbnail_generated": False,
            "oauth_or_credentials_used": False,
            "rights_approved": False,
            "production_ready": False,
            "public_ready": False,
            "operator_gate_readback": {
                "source_opened_by_worker": bool(gate_readback.get("source_opened_by_worker")),
                "media_downloaded": bool(gate_readback.get("media_downloaded")),
                "episode_dirs_created": bool(gate_readback.get("episode_dirs_created")),
            },
        },
        "skeleton": {
            "target_required": True,
            "default_target": "",
            "workspace_dir_name": episode_id,
            "materialized_by_plan_builder": False,
            "expected_files": [
                "episode_manifest.json",
                "README_NEXT.md",
                "source_identity.pending.json",
                "edit_plan_seed.json",
                "thumbnail_brief_seed.json",
            ],
        },
    }
    if fetch_authorized:
        plan["readback"]["operator_fetch_authorized_input_was_true"] = True
        plan["readback"]["fetch_authorized"] = False

    write_json(contract, contract_output_path)
    write_json(plan, output_path)
    return {
        "artifact_id": artifact_id,
        "contract_artifact_id": contract_artifact_id,
        "episode_id": episode_id,
        "output_path": output_path,
        "contract_output_path": contract_output_path,
        "payload": plan,
        "contract": contract,
    }


def build_automation_contract_payload(*, generated_at: str, artifact_id: str) -> dict[str, Any]:
    """Build the thin local/external action contract."""

    allowed = [
        ("json_generation", "Generate tracked JSON readback from existing local planning artifacts."),
        ("local_cli", "Run local CLI commands that read/write planning artifacts."),
        ("tempdir_skeleton", "Materialize empty skeleton files under an explicit tempdir target."),
        ("ignored_local_workspace_skeleton", "Materialize empty skeleton files under an explicit ignored local workspace target."),
        ("source_identity_decision_record", "Prepare and record local source identity decision JSON."),
        ("docs_readme", "Update compact docs/readme pointers to generated artifacts."),
        ("targeted_tests", "Run targeted tests and JSON parse checks."),
    ]
    deferred = [
        ("source_url_opening", "Human/source identity review may open the URL later; this slice does not."),
        ("source_fetch_download", "Video/audio fetch and download remain later local integration work."),
        ("transcript", "Transcript generation remains later work after local media exists."),
        ("render", "Diagnostic or production render is not part of this slice."),
        ("thumbnail_proof", "Thumbnail proof or image generation remains later work."),
        ("local_media_processing", "Local media conversion and processing remain outside this slice."),
    ]
    true_gates = [
        ("public_upload_publication", "Public upload, visibility, publishing, and monetization."),
        ("oauth_api_keys_credentials", "OAuth, API keys, credentials, and login-backed services."),
        ("payment", "Paid services or payment actions."),
        ("legal_rights_approval_claims", "Legal judgement, rights approval, or public-ready claims."),
        ("destructive_git", "Force push, reset, history rewrite, or broad destructive cleanup."),
        ("cross_repo_edits", "Cross-repository edits outside ClipPipeGen."),
        ("irreversible_source_overwrite", "Irreversible overwrite of source or operator-authored evidence."),
    ]
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "contract_type": "thin_gate_contract",
        "allowed_local_actions": contract_rows(allowed),
        "deferred_local_actions": contract_rows(deferred),
        "true_external_gates": contract_rows(true_gates),
        "classification_readback": {
            "local_episode_workspace_init": "allowed_local_actions",
            "local_episode_workspace_init_is_true_external_gate": False,
            "safety_ui_policy": "compact_contract_reference_only",
        },
    }


def init_episode_workspace(
    *,
    plan_path: Path,
    target_root: Path,
    materialize: bool,
    force: bool = False,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Dry-run or materialize an empty local episode workspace skeleton."""

    plan = load_json_object(plan_path, "episode workspace plan")
    if clean_string(plan.get("schema_id")) != PLAN_SCHEMA_ID:
        raise EpisodeWorkspaceError("plan must be an EWS-01 episode workspace plan")
    episode_id = clean_string(plan.get("episode_id"))
    if not episode_id:
        raise EpisodeWorkspaceError("plan must contain episode_id")
    target_root = target_root.resolve()
    workspace_dir = target_root / episode_id
    files = skeleton_file_payloads(plan=plan, plan_path=plan_path)
    conflicts = [workspace_dir / rel for rel, _, _ in files if (workspace_dir / rel).exists()]
    if materialize and conflicts and not force:
        formatted = ", ".join(str(path) for path in conflicts)
        raise EpisodeWorkspaceError(f"refusing to overwrite existing skeleton files: {formatted}")

    created: list[dict[str, Any]] = []
    for rel, kind, payload in files:
        target = workspace_dir / rel
        if materialize:
            target.parent.mkdir(parents=True, exist_ok=True)
            if kind == "json":
                write_json(payload, target)
            else:
                write_text(str(payload), target)
        created.append(
            {
                "path": display_path(target, base_dir or Path.cwd()),
                "kind": kind,
                "exists": target.exists(),
                "would_write": True,
            }
        )

    return {
        "schema_id": "clippipegen.init_episode_workspace_result.v0",
        "episode_id": episode_id,
        "plan_path": display_path(plan_path, base_dir or Path.cwd()),
        "target_root": str(target_root),
        "workspace_dir": str(workspace_dir),
        "materialized": materialize,
        "force": force,
        "created_file_count": sum(1 for item in created if item["exists"]),
        "planned_file_count": len(created),
        "files": created,
        "side_effects": {
            "source_url_opened": False,
            "media_files_created": False,
            "source_receipt_created": False,
            "transcript_generated": False,
            "render_generated": False,
            "rights_approved": False,
        },
    }


def inspect_episode_workspace(
    *,
    workspace_path: Path,
    plan_path: Path,
    contract_path: Path | None = None,
    output_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Inspect a materialized local episode workspace skeleton without side effects."""

    base_dir = base_dir or Path.cwd()
    plan = load_json_object(plan_path, "episode workspace plan")
    if clean_string(plan.get("schema_id")) != PLAN_SCHEMA_ID:
        raise EpisodeWorkspaceError("plan must be an EWS-01 episode workspace plan")
    resolved_contract_path = resolve_contract_path(
        plan=plan,
        explicit_contract_path=contract_path,
        plan_path=plan_path,
    )
    contract = load_json_object(resolved_contract_path, "automation contract")
    if clean_string(contract.get("schema_id")) != CONTRACT_SCHEMA_ID:
        raise EpisodeWorkspaceError("contract must be an EWS-01 automation contract")

    workspace_root = workspace_path.resolve()
    expected_files = expected_skeleton_files(plan)
    present = [rel for rel in expected_files if (workspace_root / rel).is_file()]
    missing = [rel for rel in expected_files if not (workspace_root / rel).is_file()]
    unexpected_media_like = find_unexpected_media_like_files(workspace_root)

    manifest_path = workspace_root / "episode_manifest.json"
    source_identity_path = workspace_root / "source_identity.pending.json"
    manifest = load_json_object(manifest_path, "episode manifest") if manifest_path.exists() else {}
    source_identity = (
        load_json_object(source_identity_path, "source identity") if source_identity_path.exists() else {}
    )

    episode_id = (
        clean_string(manifest.get("episode_id"))
        or clean_string(plan.get("episode_id"))
        or clean_string(plan.get("planned_slug"))
    )
    manifest_state = derive_manifest_state(manifest)
    source_identity_state = derive_source_identity_state(source_identity, plan)
    skeleton_ready = not missing and not unexpected_media_like and bool(manifest)
    ready_for_source_identity_decision = skeleton_ready and source_identity_state == "pending"
    readiness_level = derive_readiness_level(
        skeleton_ready=skeleton_ready,
        source_identity_state=source_identity_state,
        missing=missing,
        unexpected_media_like=unexpected_media_like,
    )
    next_allowed_local_action = derive_next_allowed_local_action(
        plan=plan,
        skeleton_ready=skeleton_ready,
        ready_for_source_identity_decision=ready_for_source_identity_decision,
    )

    result = {
        "schema_id": INSPECTION_SCHEMA_ID,
        "artifact_id": INSPECTOR_ARTIFACT_ID,
        "workspace_id": episode_id,
        "episode_id": episode_id,
        "planned_slug": clean_string(plan.get("planned_slug")) or episode_id,
        "workspace_path": str(workspace_root),
        "workspace_root": str(workspace_root),
        "input_plan_path": display_path(plan_path, base_dir),
        "automation_contract_path": display_path(resolved_contract_path, base_dir),
        "manifest_state": manifest_state,
        "source_identity_state": source_identity_state,
        "source_url_state": clean_string(plan.get("source_url_state")) or "unknown",
        "fetch_authorized": bool(manifest.get("fetch_authorized")),
        "skeleton_files_present": [path.as_posix() for path in present],
        "missing_files": [path.as_posix() for path in missing],
        "readiness_level": readiness_level,
        "next_allowed_local_action": next_allowed_local_action,
        "deferred_local_actions": contract_action_ids(contract, "deferred_local_actions"),
        "true_external_gates": contract_action_ids(contract, "true_external_gates"),
        "files": {
            "present": [path.as_posix() for path in present],
            "missing": [path.as_posix() for path in missing],
            "unexpected_media_like": [display_path(path, workspace_root) for path in unexpected_media_like],
        },
        "states": {
            "workspace_state": derive_workspace_state(
                skeleton_ready=skeleton_ready,
                missing=missing,
                unexpected_media_like=unexpected_media_like,
            ),
            "manifest_state": manifest_state,
            "source_identity_state": source_identity_state,
            "source_url_state": clean_string(plan.get("source_url_state")) or "unknown",
            "media_state": "unexpected_media_like_detected"
            if unexpected_media_like
            else "not_present",
            "transcript_state": "not_present",
            "edit_pack_state": "seed_present"
            if (workspace_root / "edit_plan_seed.json").is_file()
            else "missing",
            "render_state": "not_present",
        },
        "readiness": {
            "skeleton_ready": skeleton_ready,
            "ready_for_source_identity_decision": ready_for_source_identity_decision,
            "ready_for_fetch": False,
            "blocked_by_true_gate": False,
            "readiness_level": readiness_level,
        },
        "thin_gate_contract": {
            "artifact_id": clean_string(contract.get("artifact_id")),
            "local_workspace_init_is_true_external_gate": bool(
                (contract.get("classification_readback") or {}).get(
                    "local_episode_workspace_init_is_true_external_gate"
                )
            ),
        },
        "side_effects": {
            "source_url_opened": False,
            "media_files_created": False,
            "transcript_generated": False,
            "render_generated": False,
            "thumbnail_generated": False,
            "rights_approved": False,
        },
    }
    if output_path is not None:
        write_json(result, output_path)
    return result


def prepare_source_identity_decision(
    *,
    workspace_path: Path,
    plan_path: Path,
    contract_path: Path | None = None,
    output_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Create a pending local source identity decision template."""

    base_dir = base_dir or Path.cwd()
    inspection = inspect_episode_workspace(
        workspace_path=workspace_path,
        plan_path=plan_path,
        contract_path=contract_path,
        base_dir=base_dir,
    )
    ensure_workspace_ready_for_decision(inspection)
    workspace_root = Path(inspection["workspace_root"])
    output_path = output_path or workspace_root / SOURCE_DECISION_TEMPLATE_FILENAME
    manifest = load_json_object(workspace_root / "episode_manifest.json", "episode manifest")
    result = source_identity_decision_payload(
        inspection=inspection,
        manifest=manifest,
        identity_decision="pending",
        reviewer="",
        reviewed_at=None,
        notes="",
        decision_source="template",
        input_decision_path=None,
        output_path=output_path,
        base_dir=base_dir,
    )
    result["allowed_decisions"] = list(ALLOWED_SOURCE_IDENTITY_DECISIONS)
    write_json(result, output_path)
    return result


def record_source_identity_decision(
    *,
    workspace_path: Path,
    decision_path: Path,
    plan_path: Path,
    contract_path: Path | None = None,
    output_path: Path | None = None,
    force: bool = False,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Validate and record a local source identity decision file."""

    base_dir = base_dir or Path.cwd()
    inspection = inspect_episode_workspace(
        workspace_path=workspace_path,
        plan_path=plan_path,
        contract_path=contract_path,
        base_dir=base_dir,
    )
    ensure_workspace_ready_for_decision(inspection)
    workspace_root = Path(inspection["workspace_root"])
    output_path = output_path or workspace_root / SOURCE_DECISION_RECORD_FILENAME
    if output_path.exists() and not force:
        raise EpisodeWorkspaceError(f"refusing to overwrite existing decision record: {output_path}")

    decision = load_json_object(decision_path, "source identity decision")
    identity_decision = validate_identity_decision(decision)
    reviewer = clean_string(decision.get("reviewer"))
    notes = clean_string(decision.get("notes"))
    if identity_decision == "ok" and not (reviewer or notes):
        raise EpisodeWorkspaceError("ok decision requires reviewer or notes")
    reviewed_at = decision.get("reviewed_at")
    if reviewed_at is not None and not isinstance(reviewed_at, str):
        raise EpisodeWorkspaceError("reviewed_at must be a string or null")

    manifest = load_json_object(workspace_root / "episode_manifest.json", "episode manifest")
    result = source_identity_decision_payload(
        inspection=inspection,
        manifest=manifest,
        identity_decision=identity_decision,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        notes=notes,
        decision_source="human_input_file",
        input_decision_path=decision_path,
        output_path=output_path,
        base_dir=base_dir,
    )
    result["input_decision_source"] = clean_string(decision.get("decision_source")) or "unknown"
    write_json(result, output_path)
    return result


def plan_source_fetch_prep(
    *,
    workspace_path: Path,
    plan_path: Path,
    contract_path: Path | None = None,
    decision_path: Path | None = None,
    output_path: Path | None = None,
    write_output: bool = True,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Build a local source fetch-prep plan without authorizing fetch."""

    base_dir = base_dir or Path.cwd()
    plan = load_json_object(plan_path, "episode workspace plan")
    if clean_string(plan.get("schema_id")) != PLAN_SCHEMA_ID:
        raise EpisodeWorkspaceError("plan must be an EWS-01 episode workspace plan")
    resolved_contract_path = resolve_contract_path(
        plan=plan,
        explicit_contract_path=contract_path,
        plan_path=plan_path,
    )
    contract = load_json_object(resolved_contract_path, "automation contract")
    if clean_string(contract.get("schema_id")) != CONTRACT_SCHEMA_ID:
        raise EpisodeWorkspaceError("contract must be an EWS-01 automation contract")

    inspection = inspect_episode_workspace(
        workspace_path=workspace_path,
        plan_path=plan_path,
        contract_path=resolved_contract_path,
        base_dir=base_dir,
    )
    workspace_root = Path(inspection["workspace_root"])
    manifest_path = workspace_root / "episode_manifest.json"
    manifest = load_json_object(manifest_path, "episode manifest") if manifest_path.exists() else {}
    resolved_decision_path = decision_path or workspace_root / SOURCE_DECISION_RECORD_FILENAME
    decision = (
        load_json_object(resolved_decision_path, "source identity decision")
        if resolved_decision_path.exists()
        else None
    )

    identity_decision = ""
    allows_fetch_prep = False
    if decision is not None:
        identity_decision = validate_identity_decision(decision)
        allows_fetch_prep = bool(decision.get("allows_fetch_prep"))
    prep_state, blocked_reason = source_fetch_prep_state(
        identity_decision=identity_decision,
        allows_fetch_prep=allows_fetch_prep,
        decision_present=decision is not None,
    )

    planned = plan.get("planned_paths") if isinstance(plan.get("planned_paths"), dict) else {}
    workspace_planned_root = clean_string(planned.get("workspace_root")) or clean_string(
        plan.get("planned_slug")
    )
    source_receipt_path = (
        clean_string(planned.get("source_receipt"))
        or f"{workspace_planned_root}/materials/source/source_receipt.pending.json"
    )
    material_ledger_path = (
        clean_string(planned.get("material_ledger"))
        or f"{workspace_planned_root}/material_ledger.json"
    )
    output_path = output_path or workspace_root / SOURCE_FETCH_PREP_PLAN_FILENAME

    payload = {
        "schema_id": SOURCE_FETCH_PREP_SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": SOURCE_FETCH_PREP_ARTIFACT_ID,
        "workspace_id": clean_string(inspection.get("workspace_id")),
        "episode_id": clean_string(inspection.get("episode_id")),
        "workspace_path": str(workspace_root),
        "plan_path": display_path(plan_path, base_dir),
        "inspection_artifact_id": clean_string(inspection.get("artifact_id")),
        "automation_contract_path": display_path(resolved_contract_path, base_dir),
        "decision_record_path": display_path(resolved_decision_path, base_dir),
        "fetch_prep_plan_path": display_path(output_path, base_dir),
        "planning_label": clean_string(manifest.get("planning_label"))
        or clean_string(plan.get("planning_label")),
        "source_url": clean_string(manifest.get("source_url")) or clean_string(plan.get("source_url")),
        "identity_decision": identity_decision or "missing",
        "allows_fetch_prep": allows_fetch_prep,
        "prep_state": prep_state,
        "blocked_reason": blocked_reason,
        "fetch_authorized": False,
        "media_downloaded": False,
        "rights_approved": False,
        "public_ready": False,
        "future_fetch_inputs": {
            "workspace_manifest_path": display_path(manifest_path, base_dir),
            "source_identity_decision_path": display_path(resolved_decision_path, base_dir),
            "automation_contract_path": display_path(resolved_contract_path, base_dir),
            "source_url": clean_string(manifest.get("source_url"))
            or clean_string(plan.get("source_url")),
            "planning_label": clean_string(manifest.get("planning_label"))
            or clean_string(plan.get("planning_label")),
            "fetch_authorized": False,
        },
        "future_receipt_paths": {
            "source_receipt": source_receipt_path,
            "source_fetch_preflight_receipt": (
                f"{workspace_planned_root}/materials/source/source_fetch_preflight.pending.json"
            ),
            "source_fetch_receipt": f"{workspace_planned_root}/materials/source/source_fetch_receipt.json",
        },
        "source_receipt_path": source_receipt_path,
        "material_ledger_path": material_ledger_path,
        "deferred_local_actions": contract_action_ids(contract, "deferred_local_actions"),
        "true_external_gates": contract_action_ids(contract, "true_external_gates"),
        "readback": {
            "workspace_readiness_level": clean_string(inspection.get("readiness_level")),
            "skeleton_ready": bool((inspection.get("readiness") or {}).get("skeleton_ready")),
            "source_identity_decision_present": decision is not None,
            "source_url_opened_by_worker": False,
            "future_fetch_plan_only": True,
        },
        "side_effects": {
            "url_opened": False,
            "source_url_opened": False,
            "media_created": False,
            "media_files_created": False,
            "transcript_created": False,
            "transcript_generated": False,
            "render_created": False,
            "render_generated": False,
            "thumbnail_created": False,
            "upload_created": False,
            "rights_approved": False,
        },
    }
    if write_output:
        write_json(payload, output_path)
    return payload


def skeleton_file_payloads(*, plan: dict[str, Any], plan_path: Path) -> list[tuple[Path, str, Any]]:
    episode_id = clean_string(plan["episode_id"])
    common = {
        "episode_id": episode_id,
        "planning_label": clean_string(plan.get("planning_label")),
        "label_provenance": clean_string(plan.get("label_provenance")),
        "source_url": clean_string(plan.get("source_url")),
        "identity_state": clean_string(plan.get("identity_state")),
        "fetch_authorized": False,
        "generated_from_plan": str(plan_path).replace("\\", "/"),
    }
    return [
        (
            Path("episode_manifest.json"),
            "json",
            {
                "schema_id": MANIFEST_SCHEMA_ID,
                "local_workspace_state": "initialized",
                "planning_label_is_verified_video_title": False,
                "media_files_expected": False,
                **common,
            },
        ),
        (
            Path("source_identity.pending.json"),
            "json",
            {
                "schema_id": "clippipegen.source_identity_pending.v0",
                "review_status": "pending",
                "source_url_opened_by_worker": False,
                "human_decision": None,
                **common,
            },
        ),
        (
            Path("edit_plan_seed.json"),
            "json",
            {
                "schema_id": "clippipegen.edit_plan_seed.v0",
                "status": "planned_only",
                "transcript_available": False,
                "edit_pack_created": False,
                "next_allowed_local_action": plan["next_allowed_local_action"]["action_id"],
                **common,
            },
        ),
        (
            Path("thumbnail_brief_seed.json"),
            "json",
            {
                "schema_id": "clippipegen.thumbnail_brief_seed.v0",
                "status": "planned_only",
                "thumbnail_generated": False,
                "source_image_available": False,
                **common,
            },
        ),
        (
            Path("README_NEXT.md"),
            "text",
            readme_next(plan),
        ),
    ]


def source_fetch_prep_state(
    *,
    identity_decision: str,
    allows_fetch_prep: bool,
    decision_present: bool,
) -> tuple[str, str | None]:
    if not decision_present:
        return "blocked", "source_identity_decision_missing"
    if identity_decision == "pending":
        return "blocked", "source_identity_pending"
    if identity_decision == "ng":
        return "blocked", "source_identity_rejected"
    if identity_decision == "hold":
        return "blocked", "source_identity_hold"
    if identity_decision == "ok" and allows_fetch_prep:
        return "ready_for_future_private_fetch_plan", None
    if identity_decision == "ok":
        return "blocked", "source_identity_fetch_prep_not_allowed"
    return "blocked", "source_identity_decision_invalid"


def readme_next(plan: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Episode Workspace: {clean_string(plan.get('episode_id'))}",
            "",
            "This is a local skeleton created from the EWS-01 plan.",
            "",
            "- The planning label is not a verified video title.",
            "- Source identity is still unverified.",
            "- Fetch, transcript, render, upload, OAuth/API, and rights approval are not done.",
            "- Use the automation contract before adding any new action.",
            "",
            f"Planning label: {clean_string(plan.get('planning_label'))}",
            f"Source URL state: {clean_string(plan.get('source_url_state'))}",
            f"Identity state: {clean_string(plan.get('identity_state'))}",
            "",
        ]
    )


def planned_paths(episode_id: str) -> dict[str, str]:
    root = f"episodes/{episode_id}"
    return {
        "workspace_root": root,
        "manifest": f"{root}/episode_manifest.json",
        "source_identity": f"{root}/source_identity.pending.json",
        "source_receipt": f"{root}/materials/source/source_receipt.pending.json",
        "material_ledger": f"{root}/material_ledger.json",
        "transcript": f"{root}/transcript.json",
        "edit_pack": f"{root}/edit_pack.json",
        "subtitle": f"{root}/subtitles.json",
        "thumbnail_brief": f"{root}/thumbnail_brief_seed.json",
        "preview_pack": f"{root}/review/preview_pack/preview_manifest.json",
    }


def contract_rows(rows: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"action_id": action_id, "description": description} for action_id, description in rows]


def expected_skeleton_files(plan: dict[str, Any]) -> list[Path]:
    skeleton = plan.get("skeleton") if isinstance(plan.get("skeleton"), dict) else {}
    expected = skeleton.get("expected_files") if isinstance(skeleton, dict) else None
    if not isinstance(expected, list) or not expected:
        expected = [
            "episode_manifest.json",
            "README_NEXT.md",
            "source_identity.pending.json",
            "edit_plan_seed.json",
            "thumbnail_brief_seed.json",
        ]
    return [Path(clean_string(item)) for item in expected if clean_string(item)]


def resolve_contract_path(
    *,
    plan: dict[str, Any],
    explicit_contract_path: Path | None,
    plan_path: Path,
) -> Path:
    if explicit_contract_path is not None:
        return explicit_contract_path
    contract_ref = plan.get("automation_contract")
    if isinstance(contract_ref, dict):
        contract_path = clean_string(contract_ref.get("path"))
        if contract_path:
            return Path(contract_path)
    return plan_path.parent / DEFAULT_CONTRACT_FILENAME


def contract_action_ids(contract: dict[str, Any], key: str) -> list[str]:
    rows = contract.get(key)
    if not isinstance(rows, list):
        return []
    return [clean_string(item.get("action_id")) for item in rows if isinstance(item, dict)]


def find_unexpected_media_like_files(workspace_root: Path) -> list[Path]:
    if not workspace_root.exists():
        return []
    return [
        path
        for path in sorted(workspace_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in MEDIA_LIKE_EXTENSIONS
    ]


def derive_manifest_state(manifest: dict[str, Any]) -> str:
    if not manifest:
        return "missing"
    return clean_string(manifest.get("local_workspace_state")) or "present"


def derive_source_identity_state(source_identity: dict[str, Any], plan: dict[str, Any]) -> str:
    if not source_identity:
        return "missing"
    review_status = clean_string(source_identity.get("review_status"))
    if review_status:
        return review_status
    return clean_string(source_identity.get("identity_state")) or clean_string(plan.get("identity_state")) or "unknown"


def derive_workspace_state(
    *,
    skeleton_ready: bool,
    missing: list[Path],
    unexpected_media_like: list[Path],
) -> str:
    if unexpected_media_like:
        return "unexpected_media_like_detected"
    if missing:
        return "planned_missing_files"
    if skeleton_ready:
        return "skeleton_ready"
    return "planned"


def derive_readiness_level(
    *,
    skeleton_ready: bool,
    source_identity_state: str,
    missing: list[Path],
    unexpected_media_like: list[Path],
) -> str:
    if unexpected_media_like:
        return "planned"
    if missing or not skeleton_ready:
        return "planned"
    if source_identity_state == "pending":
        return "source_identity_pending"
    return "skeleton_ready"


def derive_next_allowed_local_action(
    *,
    plan: dict[str, Any],
    skeleton_ready: bool,
    ready_for_source_identity_decision: bool,
) -> dict[str, Any]:
    if ready_for_source_identity_decision:
        return {
            "action_id": "prepare_source_identity_decision_template",
            "command": (
                "python -m src.cli.main prepare-source-identity-decision "
                "--workspace <workspace> --format json"
            ),
            "description": (
                "Create a pending local decision template before recording any "
                "human OK/NG/HOLD input."
            ),
            "opens_source_url": False,
            "fetches_media": False,
            "writes_media": False,
        }
    if not skeleton_ready:
        return dict(plan.get("next_allowed_local_action") or {})
    return {
        "action_id": "inspect_episode_workspace_again",
        "description": "Re-run the local inspector after the next workspace-side record changes.",
        "opens_source_url": False,
        "fetches_media": False,
        "writes_media": False,
    }


def ensure_workspace_ready_for_decision(inspection: dict[str, Any]) -> None:
    readiness = inspection.get("readiness") if isinstance(inspection.get("readiness"), dict) else {}
    if not readiness.get("skeleton_ready"):
        raise EpisodeWorkspaceError("workspace skeleton is not ready for source decision intake")
    if inspection.get("source_identity_state") != "pending":
        raise EpisodeWorkspaceError("source identity state must be pending for decision intake")


def validate_identity_decision(decision: dict[str, Any]) -> str:
    identity_decision = clean_string(decision.get("identity_decision")).lower()
    if identity_decision not in ALLOWED_SOURCE_IDENTITY_DECISIONS:
        allowed = ", ".join(ALLOWED_SOURCE_IDENTITY_DECISIONS)
        raise EpisodeWorkspaceError(f"identity_decision must be one of: {allowed}")
    return identity_decision


def source_identity_decision_payload(
    *,
    inspection: dict[str, Any],
    manifest: dict[str, Any],
    identity_decision: str,
    reviewer: str,
    reviewed_at: Any,
    notes: str,
    decision_source: str,
    input_decision_path: Path | None,
    output_path: Path,
    base_dir: Path,
) -> dict[str, Any]:
    allows_fetch_prep = identity_decision == "ok"
    payload = {
        "schema_id": SOURCE_DECISION_SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": SOURCE_DECISION_ARTIFACT_ID,
        "workspace_id": clean_string(inspection.get("workspace_id")),
        "episode_id": clean_string(inspection.get("episode_id")),
        "workspace_path": clean_string(inspection.get("workspace_path")),
        "decision_record_path": display_path(output_path, base_dir),
        "planning_label": clean_string(manifest.get("planning_label")),
        "label_provenance": clean_string(manifest.get("label_provenance")),
        "source_url": clean_string(manifest.get("source_url")),
        "source_url_state": clean_string(inspection.get("source_url_state")),
        "identity_decision": identity_decision,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "notes": notes,
        "allows_fetch_prep": allows_fetch_prep,
        "fetch_authorized": False,
        "rights_approved": False,
        "public_ready": False,
        "decision_source": decision_source,
        "inspection_artifact_id": clean_string(inspection.get("artifact_id")),
        "readiness_level": clean_string(inspection.get("readiness_level")),
        "deferred_local_actions": list(inspection.get("deferred_local_actions") or []),
        "true_external_gates": list(inspection.get("true_external_gates") or []),
        "side_effects": {
            "source_url_opened": False,
            "media_files_created": False,
            "transcript_generated": False,
            "render_generated": False,
            "thumbnail_generated": False,
            "rights_approved": False,
        },
    }
    if input_decision_path is not None:
        payload["input_decision_path"] = display_path(input_decision_path, base_dir)
    return payload


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise EpisodeWorkspaceError(f"{label} JSON is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EpisodeWorkspaceError(f"{label} JSON is not valid: {path}") from exc
    if not isinstance(payload, dict):
        raise EpisodeWorkspaceError(f"{label} JSON root must be an object")
    return payload


def required_object(payload: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise EpisodeWorkspaceError(f"{label} JSON must contain {key} object")
    return value


def derive_episode_id(current: dict[str, Any]) -> str:
    seed_id = clean_string(current.get("target_seed_id"))
    candidate_id = clean_string(current.get("target_candidate_id"))
    if seed_id:
        return slugify(f"ep_{seed_id}")
    if candidate_id:
        return slugify(f"ep_seed_{candidate_id}")
    return slugify(f"ep_{clean_string(current.get('work_item_id')) or 'workspace'}")


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "episode_workspace"


def clean_string(value: Any) -> str:
    return str(value or "").strip()
