"""TH-01: thumbnail_patch_input から NLMYTGen bridge 経由で slot patch を実行する。

正本仕様: docs/SCHEMAS/v1/thumbnail_patch_input.md

フロー:
  1. rights manifest readback (status is recorded, not gated)
  2. material validation (file/sidecar resolution per slot)
  3. NLMYTGen audit-thumbnail-template (slot existence)
  4. NLMYTGen patch-thumbnail-template
  5. readback parse
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import material_ledger as ledger_mod
from . import material_sidecar as sidecar_mod
from . import nlmytgen_bridge as bridge
from .rights_manifest import load_rights_manifest
from .validation import ValidationIssue


SCHEMA_VERSION = "v1"
SLOT_ID_PATTERN = re.compile(r"^thumb\.(text|image|color|transform)\.[a-z0-9_]+$")
VALID_SLOT_KINDS = {"text", "image", "color", "transform"}


class ThumbnailPatchError(Exception):
    pass


def load_thumbnail_patch_input(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_thumbnail_patch_input(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if payload.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                code="THUMB_INPUT_SCHEMA_VERSION",
                field="schema_version",
                message=f"expected {SCHEMA_VERSION!r}",
            )
        )
    for required in (
        "episode_id",
        "rights_manifest_path",
        "material_ledger_path",
    ):
        if not payload.get(required):
            issues.append(
                ValidationIssue(
                    code="THUMB_INPUT_FIELD_MISSING",
                    field=required,
                    message=f"{required} is required",
                )
            )

    base_template = payload.get("base_template") or {}
    if not isinstance(base_template, dict) or not base_template.get("ymmp_path"):
        issues.append(
            ValidationIssue(
                code="THUMB_INPUT_BASE_TEMPLATE_MISSING",
                field="base_template.ymmp_path",
                message="base_template.ymmp_path is required",
            )
        )

    slots = payload.get("slots")
    if not isinstance(slots, list) or not slots:
        issues.append(
            ValidationIssue(
                code="THUMB_INPUT_SLOTS_EMPTY",
                field="slots",
                message="slots[] must contain at least one entry",
            )
        )
    else:
        for i, slot in enumerate(slots):
            issues.extend(_validate_slot(slot, i))

    output = payload.get("output") or {}
    if not isinstance(output, dict) or not output.get("ymmp_path"):
        issues.append(
            ValidationIssue(
                code="THUMB_INPUT_OUTPUT_MISSING",
                field="output.ymmp_path",
                message="output.ymmp_path is required",
            )
        )

    return issues


def _validate_slot(slot: Any, index: int) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    prefix = f"slots[{index}]"
    if not isinstance(slot, dict):
        return [
            ValidationIssue(
                code="THUMB_SLOT_NOT_OBJECT",
                field=prefix,
                message="slot must be an object",
            )
        ]
    sid = slot.get("slot_id", "")
    if not sid or not SLOT_ID_PATTERN.match(sid):
        issues.append(
            ValidationIssue(
                code="THUMB_SLOT_ID_INVALID",
                field=f"{prefix}.slot_id",
                message=(
                    "slot_id must match thumb.(text|image|color|transform).<lowercase id>"
                ),
            )
        )
    kind = slot.get("kind")
    if kind not in VALID_SLOT_KINDS:
        issues.append(
            ValidationIssue(
                code="THUMB_SLOT_KIND_INVALID",
                field=f"{prefix}.kind",
                message=f"kind must be one of {sorted(VALID_SLOT_KINDS)}",
            )
        )
    if kind == "image":
        if not slot.get("source_material_id"):
            issues.append(
                ValidationIssue(
                    code="THUMB_SLOT_MATERIAL_ID_REQUIRED",
                    field=f"{prefix}.source_material_id",
                    message="source_material_id is required for kind=image",
                )
            )
    elif kind in ("text", "color", "transform"):
        if slot.get("value") in (None, ""):
            issues.append(
                ValidationIssue(
                    code="THUMB_SLOT_VALUE_REQUIRED",
                    field=f"{prefix}.value",
                    message=f"value is required for kind={kind}",
                )
            )
    return issues


def apply_thumbnail_patch(
    payload: dict[str, Any],
    *,
    base_dir: str | Path = ".",
    config: bridge.BridgeConfig | None = None,
    work_dir: Path | None = None,
) -> dict[str, Any]:
    """thumbnail_patch_input.json の中身を受け取り、result dict を返す。

    各段階で fail した場合は result の該当 section に error を残し、
    後段は実行しない。`patch_result.errors[]` が非空なら overall fail。
    """
    base = Path(base_dir)
    work = work_dir or Path("_tmp/thumbnail_patch")

    schema_issues = validate_thumbnail_patch_input(payload)

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "input_schema": {"ok": not schema_issues, "issues": [i.to_dict() for i in schema_issues]},
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "rights_readback": {"status": "read", "rights_manifest_status": None},
        "material_validation": {"all_resolved": False, "violations": []},
        "audit_result": {"passed": False, "missing_slots": [], "extra_slots": []},
        "patch_result": {"output_ymmp_path": None, "applied_slots": [], "errors": []},
    }
    if schema_issues:
        result["patch_result"]["errors"].append("INPUT_SCHEMA_INVALID")
        return result

    # 1. rights manifest readback
    rights_path = base / payload["rights_manifest_path"]
    try:
        rights = load_rights_manifest(rights_path)
    except FileNotFoundError:
        result["rights_readback"] = {
            "status": "failed",
            "error": f"rights_manifest not found: {rights_path}",
        }
        result["patch_result"]["errors"].append("RIGHTS_MANIFEST_NOT_FOUND")
        return result
    result["rights_readback"] = {
        "status": "read",
        "rights_manifest_status": (rights.get("compliance_check") or {}).get("status"),
    }

    # 2. material validation
    ledger_path = base / payload["material_ledger_path"]
    if not ledger_path.exists():
        result["material_validation"] = {
            "all_resolved": False,
            "violations": [{"reason": f"ledger not found: {ledger_path}"}],
        }
        result["patch_result"]["errors"].append("MATERIAL_LEDGER_NOT_FOUND")
        return result
    ledger = ledger_mod.load_ledger(ledger_path)

    violations: list[dict[str, str]] = []
    image_slot_files: dict[str, str] = {}
    for slot in payload["slots"]:
        if slot["kind"] != "image":
            continue
        mid = slot["source_material_id"]
        try:
            ledger_mod.assert_thumbnail_usable(ledger, mid, base_dir=base)
        except (ledger_mod.LedgerError, sidecar_mod.SidecarUsageError) as exc:
            violations.append(
                {
                    "slot_id": slot["slot_id"],
                    "material_id": mid,
                    "reason": str(exc),
                }
            )
            continue
        # resolve file path for the material
        for m in ledger.get("materials", []):
            if m.get("id") == mid:
                image_slot_files[slot["slot_id"]] = str((base / m["file_path"]).resolve())
                break

    result["material_validation"] = {
        "all_resolved": not violations,
        "violations": violations,
    }
    if violations:
        result["patch_result"]["errors"].append("MATERIAL_VALIDATION_FAILED")
        return result

    # 3. NLMYTGen audit
    base_ymmp = (base / payload["base_template"]["ymmp_path"]).resolve()
    try:
        audit = bridge.audit_thumbnail_template(base_ymmp, config=config)
    except bridge.BridgeExecutionError as exc:
        result["audit_result"] = {
            "passed": False,
            "error": str(exc),
            "stderr_tail": (exc.stderr or "")[-500:],
        }
        result["patch_result"]["errors"].append("BRIDGE_AUDIT_FAILED")
        return result

    audit_slot_ids = {
        f"thumb.{s.get('kind') or s.get('slot_type')}.{s.get('id') or s.get('slot_id')}"
        for s in audit.get("slots", [])
        if isinstance(s, dict)
    }
    requested_ids = {s["slot_id"] for s in payload["slots"]}
    missing = sorted(requested_ids - audit_slot_ids)
    extra = sorted(audit_slot_ids - requested_ids)
    audit_passed = not missing
    result["audit_result"] = {
        "passed": audit_passed,
        "missing_slots": missing,
        "extra_slots": extra,
    }
    if not audit_passed:
        result["patch_result"]["errors"].append("BRIDGE_AUDIT_MISSING_SLOTS")
        return result

    # 4. patch
    patch_payload = _build_patch_payload(payload["slots"], image_slot_files)
    output_ymmp = (base / payload["output"]["ymmp_path"]).resolve()
    if output_ymmp.exists() and not payload["output"].get("overwrite_existing"):
        result["patch_result"]["errors"].append("OUTPUT_EXISTS_NO_OVERWRITE")
        return result
    output_ymmp.parent.mkdir(parents=True, exist_ok=True)
    try:
        patch_response = bridge.patch_thumbnail_template(
            base_ymmp,
            patch_payload,
            output_path=output_ymmp,
            dry_run=False,
            config=config,
            work_dir=work,
        )
    except bridge.BridgeExecutionError as exc:
        result["patch_result"]["errors"].append("BRIDGE_PATCH_FAILED")
        result["patch_result"]["bridge_error"] = str(exc)
        result["patch_result"]["stderr_tail"] = (exc.stderr or "")[-500:]
        return result

    # 5. readback (NLMYTGen patch response includes file_readback when -o is used)
    applied: list[dict[str, Any]] = []
    for slot in payload["slots"]:
        readback = _extract_readback(patch_response, slot)
        applied.append(
            {
                "slot_id": slot["slot_id"],
                "kind": slot["kind"],
                "applied_value": slot.get("value"),
                "applied_path": image_slot_files.get(slot["slot_id"]),
                "readback_match": readback,
            }
        )
    result["patch_result"]["output_ymmp_path"] = str(output_ymmp)
    result["patch_result"]["applied_slots"] = applied

    if any(s["readback_match"] is False for s in applied):
        result["patch_result"]["errors"].append("READBACK_MISMATCH")

    return result


def _build_patch_payload(
    slots: list[dict[str, Any]],
    image_slot_files: dict[str, str],
) -> dict[str, Any]:
    """ClipPipeGen の slots[] を NLMYTGen patch JSON 形式に変換する。

    flat 形式（{"slots": {"thumb.text.title": "..."}}）を採用。
    """
    out: dict[str, Any] = {"slots": {}}
    for slot in slots:
        sid = slot["slot_id"]
        kind = slot["kind"]
        if kind == "text":
            out["slots"][sid] = {"slot_type": "text", "value": slot["value"]}
        elif kind == "image":
            out["slots"][sid] = {
                "slot_type": "image",
                "file_path": image_slot_files[sid],
            }
        elif kind == "color":
            out["slots"][sid] = {"slot_type": kind, "color": slot["value"]}
        elif kind == "transform":
            out["slots"][sid] = {"slot_type": kind, "geometry": slot["value"]}
    return out


def _extract_readback(patch_response: dict[str, Any], slot: dict[str, Any]) -> bool | None:
    """NLMYTGen patch response から該当 slot の readback 一致を取り出す。

    NLMYTGen の出力構造に強く依存しないよう、不明なら None を返す。
    """
    file_readback = patch_response.get("file_readback")
    if not isinstance(file_readback, list):
        # text/image_changes 等のフィールドだけ見える場合は照合できないので保守的に None
        return None
    sid = slot["slot_id"]
    for r in file_readback:
        if not isinstance(r, dict):
            continue
        if r.get("slot") == sid or r.get("slot_id") == sid:
            return bool(r.get("match", r.get("ok", False)))
    return None
