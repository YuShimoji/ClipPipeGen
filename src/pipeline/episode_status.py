"""SH-02-lite: episode status adapter for the GUI MVP.

Full episode_pack is intentionally postponed until Editing / Publishing exist.
This module only reads current Slice 1 artifacts and returns operator-facing
status for the GUI.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import material_ledger as ledger_mod
from . import nlmytgen_bridge as bridge
from .rights_manifest import (
    evaluate_compliance_auto_fail,
    load_rights_manifest,
    validate_rights_manifest,
)
from .thumbnail_patch import (
    load_thumbnail_patch_input,
    validate_thumbnail_patch_input,
)
from .edit_pack import load_edit_pack, validate_edit_pack
from .transcript import (
    count_segment_review_statuses,
    load_transcript,
    validate_transcript,
)

SCHEMA_VERSION = "v1"


def build_episode_status(
    *,
    episode_dir: str | Path,
    base_dir: str | Path = ".",
    bridge_config_path: str | Path = bridge.CONFIG_PATH_DEFAULT,
) -> dict[str, Any]:
    """Return a compact status object for one episode directory."""
    base = Path(base_dir)
    ep_dir = Path(episode_dir)
    if not ep_dir.is_absolute():
        ep_dir = base / ep_dir

    status: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "episode_dir": _display_path(ep_dir, base),
        "episode_id": None,
        "artifacts": {},
        "rights": {"state": "missing"},
        "materials": {"state": "missing"},
        "editing": {"state": "missing"},
        "thumbnail": {"state": "missing"},
        "operator_review": {},
        "settings": {"bridge_config": _bridge_config_status(bridge_config_path)},
        "next_action": {},
    }

    rights_path = ep_dir / "rights_manifest.json"
    ledger_path = ep_dir / "material_ledger.json"
    edit_pack_path = ep_dir / "edit_pack.json"
    transcript_path = ep_dir / "transcript.json"
    thumb_input_path = ep_dir / "thumbnail_patch_input.json"
    thumb_result_path = ep_dir / "thumbnail_patch_result.json"

    status["artifacts"] = {
        "rights_manifest": _artifact(rights_path, base),
        "material_ledger": _artifact(ledger_path, base),
        "edit_pack": _artifact(edit_pack_path, base),
        "transcript": _artifact(transcript_path, base),
        "thumbnail_patch_input": _artifact(thumb_input_path, base),
        "thumbnail_patch_result": _artifact(thumb_result_path, base),
    }

    if rights_path.exists():
        _fill_rights_status(status, rights_path)
    if ledger_path.exists():
        _fill_material_status(status, ledger_path, base)
    if edit_pack_path.exists():
        _fill_editing_status(status, edit_pack_path)
    _fill_transcript_status(status, transcript_path)
    if thumb_input_path.exists():
        _fill_thumbnail_input_status(status, thumb_input_path)
    if thumb_result_path.exists():
        _fill_thumbnail_result_status(status, thumb_result_path)

    status["operator_review"] = _operator_review_status(ep_dir, base, status)
    status["next_action"] = _choose_next_action(status)
    return status


def _artifact(path: Path, base: Path) -> dict[str, Any]:
    return {
        "path": _display_path(path, base),
        "exists": path.exists(),
    }


def _display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _bridge_config_status(config_path: str | Path) -> dict[str, Any]:
    path = Path(config_path)
    out: dict[str, Any] = {
        "path": str(path).replace("\\", "/"),
        "exists": path.exists(),
        "ready": False,
    }
    if not path.exists():
        out["message"] = "config/nlmytgen_path.json is missing"
        return out
    try:
        bridge.BridgeConfig.load(path)
    except bridge.BridgeConfigError as exc:
        out["message"] = str(exc)
        return out
    out["ready"] = True
    out["message"] = "NLMYTGen bridge config looks ready"
    return out


def _fill_rights_status(status: dict[str, Any], rights_path: Path) -> None:
    manifest = load_rights_manifest(rights_path)
    status["episode_id"] = manifest.get("episode_id")
    schema_issues = validate_rights_manifest(manifest)
    review_notes = evaluate_compliance_auto_fail(manifest)
    compliance = manifest.get("compliance_check") or {}
    state = "ready"
    if schema_issues:
        state = "blocked"

    status["rights"] = {
        "state": state,
        "compliance_status": compliance.get("status"),
        "schema_issues": [i.to_dict() for i in schema_issues],
        "review_notes": [i.to_dict() for i in review_notes],
    }


def _fill_material_status(status: dict[str, Any], ledger_path: Path, base: Path) -> None:
    ledger = ledger_mod.load_ledger(ledger_path)
    issues = ledger_mod.audit_ledger(ledger, base_dir=base)
    materials = ledger.get("materials") or []
    state = "ready"
    if issues:
        state = "blocked"
    elif not materials:
        state = "missing"

    status["materials"] = {
        "state": state,
        "materials_count": len(materials),
        "audit_issues_count": len(issues),
        "audit_issues": [i.to_dict() for i in issues],
    }


def _fill_editing_status(status: dict[str, Any], edit_pack_path: Path) -> None:
    pack = load_edit_pack(edit_pack_path)
    issues = validate_edit_pack(pack)
    selected = pack.get("selected_cut_ids") or []
    candidates = pack.get("cut_candidates") or []
    subtitles = pack.get("subtitles") or []
    context_checks = _context_check_counts(candidates)
    state = "ready"
    if issues:
        state = "blocked"
    elif not candidates:
        state = "manual_needed"

    status["editing"] = {
        "state": state,
        "cut_candidates_count": len(candidates),
        "selected_cuts_count": len(selected),
        "subtitles_count": len(subtitles),
        "context_checks": context_checks,
        "schema_issues_count": len(issues),
        "schema_issues": [i.to_dict() for i in issues],
    }


def _fill_transcript_status(status: dict[str, Any], transcript_path: Path) -> None:
    editing = status.get("editing") or {}
    if not transcript_path.exists():
        editing["transcript"] = {
            "state": "missing",
            "segments_count": 0,
            "review_status": "missing",
            "reviewed_by": None,
            "reviewed_at": None,
            "segment_review_counts": count_segment_review_statuses([]),
            "schema_issues_count": 0,
            "schema_issues": [],
        }
        status["editing"] = editing
        return

    transcript = load_transcript(transcript_path)
    issues = validate_transcript(transcript)
    segments = transcript.get("segments") if isinstance(transcript.get("segments"), list) else []
    review = transcript.get("review") if isinstance(transcript.get("review"), dict) else {}
    editing["transcript"] = {
        "state": "ready" if not issues else "blocked",
        "segments_count": len(segments),
        "review_status": review.get("status", "unknown"),
        "reviewed_by": review.get("reviewed_by"),
        "reviewed_at": review.get("reviewed_at"),
        "segment_review_counts": count_segment_review_statuses(segments),
        "schema_issues_count": len(issues),
        "schema_issues": [i.to_dict() for i in issues],
        "engine": (transcript.get("stt") or {}).get("engine"),
        "language": transcript.get("language"),
    }
    status["editing"] = editing


def _fill_thumbnail_input_status(status: dict[str, Any], input_path: Path) -> None:
    payload = load_thumbnail_patch_input(input_path)
    issues = validate_thumbnail_patch_input(payload)
    status["thumbnail"] = {
        "state": "ready" if not issues else "blocked",
        "input_schema_issues": [i.to_dict() for i in issues],
        "slots_count": len(payload.get("slots") or []),
        "result_errors": [],
    }


def _fill_thumbnail_result_status(status: dict[str, Any], result_path: Path) -> None:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    errors = (result.get("patch_result") or {}).get("errors") or []
    thumb = status.get("thumbnail") or {}
    thumb.update(
        {
            "state": "ready" if not errors else "blocked",
            "result_errors": errors,
            "readback": (result.get("patch_result") or {}).get("applied_slots", []),
        }
    )
    status["thumbnail"] = thumb


def _operator_review_status(ep_dir: Path, base: Path, status: dict[str, Any]) -> dict[str, Any]:
    review_dir = ep_dir / "review" / "jp_pilot01r3_cut_review"
    required = {
        "cut_review_report": review_dir / "cut_review_report.html",
        "evidence_summary": review_dir / "evidence_summary.html",
        "non_repo_artifact_handoff": review_dir / "non_repo_artifact_handoff.html",
    }
    artifacts = {
        name: {
            "path": _display_path(path, base),
            "exists": path.exists() and path.is_file(),
        }
        for name, path in required.items()
    }
    missing = [item["path"] for item in artifacts.values() if not item["exists"]]
    review_ready = not missing
    rights_status = (status.get("rights") or {}).get("compliance_status") or "unknown"
    return {
        "review_surface": "jp_pilot01r3_cut_review",
        "reviewability": "review_ready" if review_ready else "review_blocked_missing_artifacts",
        "review_ready": review_ready,
        "missing_review_artifacts": missing,
        "next_human_action": (
            "Open cut_review_report.html and respond in natural language with cut/context judgment."
            if review_ready
            else "Restore or regenerate ignored R3 review artifacts before final cut/context review; Git alone cannot start R3 review."
        ),
        "recovery_doc": "docs/NON_REPO_ARTIFACT_HANDOFF.md",
        "production_candidate": False,
        "rights_status": rights_status,
        "artifacts": artifacts,
    }


def _choose_next_action(status: dict[str, Any]) -> dict[str, str]:
    if not status["artifacts"]["rights_manifest"]["exists"]:
        return {
            "owner": "assistant",
            "action": "Run init-episode or create rights_manifest.json",
            "reason": "rights_manifest is the first episode metadata artifact",
        }
    if status["rights"]["state"] == "blocked":
        return {
            "owner": "both",
            "action": "Fix rights_manifest schema issues",
            "reason": "downstream lanes need readable rights data",
        }
    if not status["artifacts"]["material_ledger"]["exists"]:
        return {
            "owner": "assistant",
            "action": "Register thumbnail material with sidecar",
            "reason": "thumbnail image slots need a ledger material id",
        }
    if status["materials"]["state"] == "missing":
        return {
            "owner": "assistant",
            "action": "Register thumbnail material with sidecar",
            "reason": "material_ledger exists but has no registered materials yet",
        }
    if status["materials"]["state"] == "blocked":
        return {
            "owner": "both",
            "action": "Fix material ledger / sidecar issues",
            "reason": "thumbnail slots need resolvable material files and sidecars",
        }
    if not status["artifacts"]["edit_pack"]["exists"]:
        return {
            "owner": "assistant",
            "action": "Create edit_pack.json",
            "reason": "Editing lane now has a schema for cut candidates and subtitle drafts",
        }
    if status["editing"]["state"] == "blocked":
        return {
            "owner": "both",
            "action": "Fix edit_pack schema issues",
            "reason": "cut candidates and subtitle drafts must validate before later detection/export work",
        }
    transcript = (status["editing"] or {}).get("transcript") or {}
    context_checks = (status["editing"] or {}).get("context_checks") or {}
    if (
        transcript.get("state") == "ready"
        and status["editing"].get("cut_candidates_count", 0) > 0
        and context_checks.get("not_checked_count", 0) > 0
    ):
        return {
            "owner": "assistant",
            "action": "Run check-cut-context for transcript-based cut review",
            "reason": "cut boundaries should be checked against adjacent transcript context before downstream export",
        }
    if context_checks.get("failed_count", 0) > 0:
        return {
            "owner": "both",
            "action": "Fix or replace failed cut candidates",
            "reason": "ED-03 found cut boundaries or source segment links that fail context review",
        }
    if context_checks.get("needs_review_count", 0) > 0:
        return {
            "owner": "user",
            "action": "Review ED-03 context notes and choose final cuts",
            "reason": "nearby transcript segments may contain setup or continuation context",
        }
    if not status["artifacts"]["thumbnail_patch_input"]["exists"]:
        return {
            "owner": "assistant",
            "action": "Create thumbnail_patch_input.json",
            "reason": "patch-thumbnail needs explicit slot values and output target",
        }
    if status["thumbnail"]["state"] == "blocked":
        return {
            "owner": "both",
            "action": "Fix thumbnail input or patch result errors",
            "reason": "readback / slot patch must be clean before YMM4 review",
        }
    if not status["artifacts"]["thumbnail_patch_result"]["exists"]:
        return {
            "owner": "assistant",
            "action": "Run patch-thumbnail after YMM4 base template is ready",
            "reason": "thumbnail patch has not been executed for this episode",
        }
    return {
        "owner": "user",
        "action": "Open patched .ymmp in YMM4 and perform final visual acceptance",
        "reason": "composition and final thumbnail judgement happen in the creative tool",
    }


def _context_check_counts(candidates: list[Any]) -> dict[str, int]:
    counts = {
        "not_checked_count": 0,
        "passed_count": 0,
        "needs_review_count": 0,
        "failed_count": 0,
    }
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        context = candidate.get("context_check") or {}
        status = context.get("status")
        if status == "passed":
            counts["passed_count"] += 1
        elif status == "needs_review":
            counts["needs_review_count"] += 1
        elif status == "failed":
            counts["failed_count"] += 1
        else:
            counts["not_checked_count"] += 1
    return counts
