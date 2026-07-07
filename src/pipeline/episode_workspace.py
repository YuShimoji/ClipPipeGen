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
DEFAULT_GENERATED_AT = "2026-07-07"
DEFAULT_PLAN_FILENAME = "episode_workspace_plan.json"
DEFAULT_CONTRACT_FILENAME = "automation_contract.json"


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


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
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
