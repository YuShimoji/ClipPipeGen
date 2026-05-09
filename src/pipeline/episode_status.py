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
from .transcript import load_transcript, validate_transcript

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
        "schema_issues_count": len(issues),
        "schema_issues": [i.to_dict() for i in issues],
    }


def _fill_transcript_status(status: dict[str, Any], transcript_path: Path) -> None:
    editing = status.get("editing") or {}
    if not transcript_path.exists():
        editing["transcript"] = {
            "state": "missing",
            "segments_count": 0,
            "schema_issues_count": 0,
            "schema_issues": [],
        }
        status["editing"] = editing
        return

    transcript = load_transcript(transcript_path)
    issues = validate_transcript(transcript)
    segments = transcript.get("segments") if isinstance(transcript.get("segments"), list) else []
    editing["transcript"] = {
        "state": "ready" if not issues else "blocked",
        "segments_count": len(segments),
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
