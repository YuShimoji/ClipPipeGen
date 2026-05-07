"""material_ledger schema v1: 素材横断台帳。

正本仕様: docs/SCHEMAS/v1/material_ledger.md

MS-01 (CRUD + audit) と MS-03 (透過PNG受け入れ) の中心実装。
"""

from __future__ import annotations

import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from . import material_sidecar as sidecar_mod
from .validation import ValidationIssue

SCHEMA_VERSION = "v1"

VALID_KINDS = {
    "source_video",
    "source_audio",
    "character_image",
    "background_image",
    "logo",
    "font_asset",
    "bgm",
    "se",
    "attribution_text",
    "other",
}

VALID_INTENDED_USES = {
    "thumbnail",
    "editing_overlay",
    "editing_bg",
    "editing_audio",
    "description_text",
    "reference_only",
}


class LedgerError(Exception):
    """ledger 操作上の問題（重複登録・素材未検出など）。"""


def load_ledger(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_ledger(ledger: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_skeleton(episode_id: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "created_at": now,
        "updated_at": now,
        "materials": [],
    }


def compute_sha256(path: str | Path, *, chunk_size: int = 1 << 16) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# --- PNG transparency check (MS-03) ---


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_COLOR_TYPES_WITH_ALPHA = {4, 6}  # 4: gray+alpha, 6: RGBA


def is_transparent_png(path: str | Path) -> bool:
    """PNG ヘッダを読み、color_type が alpha 込み（4 or 6）かを判定する。

    color_type=3 (indexed) + tRNS chunk は v1 では対象外（よくある bg-removal の
    出力は RGBA = color_type 6 なので、この単純判定で十分）。
    """
    p = Path(path)
    with p.open("rb") as f:
        head = f.read(26)
    if len(head) < 26 or head[:8] != PNG_SIGNATURE:
        return False
    # bytes 16..24 = IHDR data: width(4) height(4) bit_depth(1) color_type(1)...
    color_type = head[25]
    return color_type in PNG_COLOR_TYPES_WITH_ALPHA


# --- registration ---


def _next_material_id(ledger: dict[str, Any]) -> str:
    n = len(ledger.get("materials", [])) + 1
    return f"mat_{n:03d}"


def register_material(
    ledger: dict[str, Any],
    *,
    kind: str,
    file_path: str | Path,
    sidecar_path: str | Path,
    intended_uses: Iterable[str],
    registered_by: str,
    rights_manifest_id: str,
    rights_status_at_registration: str,
    subkind: str | None = None,
    material_id: str | None = None,
) -> dict[str, Any]:
    """ledger に素材を追加し、更新後の ledger を返す（in-place ではない）。

    sidecar の構造バリデーションと、subkind=transparent_png の場合の PNG
    アルファチェックを強制する。
    """
    if kind not in VALID_KINDS:
        raise LedgerError(f"invalid kind: {kind}")
    intended_uses_list = list(intended_uses)
    if not intended_uses_list:
        raise LedgerError("at least one intended_use is required")
    for u in intended_uses_list:
        if u not in VALID_INTENDED_USES:
            raise LedgerError(f"invalid intended_use: {u}")

    file_p = Path(file_path)
    sidecar_p = Path(sidecar_path)
    if not file_p.exists():
        raise LedgerError(f"file not found: {file_p}")
    if not sidecar_p.exists():
        raise LedgerError(f"sidecar not found: {sidecar_p}")

    sidecar = sidecar_mod.load_sidecar(sidecar_p)
    sidecar_issues = sidecar_mod.validate_sidecar(sidecar)
    if sidecar_issues:
        raise LedgerError(
            "sidecar invalid: "
            + ", ".join(f"{i.code}@{i.field}" for i in sidecar_issues)
        )

    asset_hash = compute_sha256(file_p)
    if sidecar.get("asset_hash_sha256") != asset_hash:
        raise LedgerError(
            f"sidecar asset_hash_sha256 does not match file "
            f"(sidecar={sidecar.get('asset_hash_sha256')!r}, actual={asset_hash!r})"
        )

    # MS-03: 透過PNG enforcement
    if kind == "character_image" and subkind == "transparent_png":
        if not is_transparent_png(file_p):
            raise LedgerError(
                f"file {file_p} is declared as transparent_png but PNG color_type "
                "is not 4/6 (RGBA or gray+alpha)"
            )

    chosen_id = material_id or _next_material_id(ledger)
    if any(m.get("id") == chosen_id for m in ledger.get("materials", [])):
        raise LedgerError(f"material id already exists: {chosen_id}")

    if sidecar.get("asset_id") != chosen_id:
        raise LedgerError(
            f"sidecar.asset_id ({sidecar.get('asset_id')!r}) "
            f"does not match material id ({chosen_id!r})"
        )

    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": chosen_id,
        "kind": kind,
        "subkind": subkind,
        "file_path": str(file_p).replace("\\", "/"),
        "sidecar_path": str(sidecar_p).replace("\\", "/"),
        "hash_sha256": asset_hash,
        "byte_size": file_p.stat().st_size,
        "intended_uses": intended_uses_list,
        "registered_at": now,
        "registered_by": registered_by,
        "compliance_link": {
            "rights_manifest_id": rights_manifest_id,
            "compliance_status_at_registration": rights_status_at_registration,
        },
    }

    new_ledger = dict(ledger)
    new_ledger["materials"] = list(ledger.get("materials", [])) + [entry]
    new_ledger["updated_at"] = now
    return new_ledger


# --- audit ---


def audit_ledger(
    ledger: dict[str, Any],
    *,
    base_dir: str | Path = ".",
) -> list[ValidationIssue]:
    """ledger 全体の整合性チェック。

    - hash_sha256 がファイルと一致するか
    - sidecar が schema を満たすか
    - sidecar.asset_id が material.id と一致するか
    - derived_from がある場合、original_asset_id が ledger に存在し restrictions を継承しているか
    - sidecar policy fields are read back but do not block thumbnail use
    """
    issues: list[ValidationIssue] = []
    base = Path(base_dir)

    if ledger.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                code="LEDGER_SCHEMA_VERSION",
                field="schema_version",
                message=f"expected {SCHEMA_VERSION!r}",
            )
        )

    materials = ledger.get("materials") or []
    if not isinstance(materials, list):
        issues.append(
            ValidationIssue(
                code="LEDGER_MATERIALS_NOT_LIST",
                field="materials",
                message="must be array",
            )
        )
        return issues

    seen_ids: set[str] = set()
    sidecars_by_id: dict[str, dict[str, Any]] = {}

    for i, m in enumerate(materials):
        prefix = f"materials[{i}]"
        if not isinstance(m, dict):
            issues.append(
                ValidationIssue(
                    code="LEDGER_ENTRY_NOT_OBJECT",
                    field=prefix,
                    message="must be object",
                )
            )
            continue

        mid = m.get("id")
        if not mid:
            issues.append(
                ValidationIssue(code="LEDGER_ID_MISSING", field=f"{prefix}.id", message="id is required")
            )
            continue
        if mid in seen_ids:
            issues.append(
                ValidationIssue(
                    code="LEDGER_ID_DUPLICATE",
                    field=f"{prefix}.id",
                    message=f"id {mid!r} duplicated",
                )
            )
        seen_ids.add(mid)

        if m.get("kind") not in VALID_KINDS:
            issues.append(
                ValidationIssue(
                    code="LEDGER_KIND_INVALID",
                    field=f"{prefix}.kind",
                    message=f"must be one of {sorted(VALID_KINDS)}",
                )
            )

        intended = m.get("intended_uses") or []
        if not intended:
            issues.append(
                ValidationIssue(
                    code="LEDGER_INTENDED_USES_EMPTY",
                    field=f"{prefix}.intended_uses",
                    message="must have at least one entry",
                )
            )

        file_rel = m.get("file_path")
        if not file_rel:
            issues.append(
                ValidationIssue(
                    code="LEDGER_FILE_PATH_MISSING",
                    field=f"{prefix}.file_path",
                    message="file_path is required",
                )
            )
        else:
            file_p = base / file_rel
            if not file_p.exists():
                issues.append(
                    ValidationIssue(
                        code="LEDGER_FILE_NOT_FOUND",
                        field=f"{prefix}.file_path",
                        message=f"file not found: {file_p}",
                    )
                )
            else:
                actual = compute_sha256(file_p)
                if actual != m.get("hash_sha256"):
                    issues.append(
                        ValidationIssue(
                            code="LEDGER_HASH_MISMATCH",
                            field=f"{prefix}.hash_sha256",
                            message=f"expected {m.get('hash_sha256')!r}, got {actual!r}",
                        )
                    )

        sidecar_rel = m.get("sidecar_path")
        if not sidecar_rel:
            issues.append(
                ValidationIssue(
                    code="LEDGER_SIDECAR_PATH_MISSING",
                    field=f"{prefix}.sidecar_path",
                    message="sidecar_path is required",
                )
            )
        else:
            sidecar_p = base / sidecar_rel
            if not sidecar_p.exists():
                issues.append(
                    ValidationIssue(
                        code="LEDGER_SIDECAR_NOT_FOUND",
                        field=f"{prefix}.sidecar_path",
                        message=f"sidecar not found: {sidecar_p}",
                    )
                )
            else:
                sc = sidecar_mod.load_sidecar(sidecar_p)
                sc_issues = sidecar_mod.validate_sidecar(sc)
                for si in sc_issues:
                    issues.append(
                        ValidationIssue(
                            code="LEDGER_SIDECAR_" + si.code,
                            field=f"{prefix}.sidecar:{si.field}",
                            message=si.message,
                        )
                    )
                if sc.get("asset_id") != mid:
                    issues.append(
                        ValidationIssue(
                            code="LEDGER_SIDECAR_ASSET_ID_MISMATCH",
                            field=f"{prefix}.sidecar.asset_id",
                            message=(
                                f"sidecar asset_id {sc.get('asset_id')!r} "
                                f"!= material id {mid!r}"
                            ),
                        )
                    )
                sidecars_by_id[mid] = sc

    # derived_from inheritance check
    for i, m in enumerate(materials):
        if not isinstance(m, dict):
            continue
        sc = sidecars_by_id.get(m.get("id"))
        if not sc:
            continue
        derived = sc.get("derived_from")
        if not derived:
            continue
        original_id = derived.get("original_asset_id")
        if not original_id:
            continue
        original_sc = sidecars_by_id.get(original_id)
        if not original_sc:
            issues.append(
                ValidationIssue(
                    code="LEDGER_DERIVED_ORIGINAL_NOT_FOUND",
                    field=f"materials[{i}].sidecar.derived_from.original_asset_id",
                    message=(
                        f"original_asset_id {original_id!r} not found in ledger"
                    ),
                )
            )
            continue
        for si in sidecar_mod.restrictions_are_at_least_as_strict(sc, original_sc):
            issues.append(
                ValidationIssue(
                    code=si.code,
                    field=f"materials[{i}].sidecar.{si.field}",
                    message=si.message,
                )
            )

    return issues


def assert_thumbnail_usable(ledger: dict[str, Any], material_id: str, *, base_dir: str | Path = ".") -> None:
    """Resolve thumbnail material existence and sidecar schema before use."""
    base = Path(base_dir)
    for m in ledger.get("materials", []):
        if m.get("id") != material_id:
            continue
        sc_path = base / m.get("sidecar_path", "")
        if not sc_path.exists():
            raise LedgerError(f"sidecar not found for {material_id!r}: {sc_path}")
        sc = sidecar_mod.load_sidecar(sc_path)
        issues = sidecar_mod.validate_sidecar(sc)
        if issues:
            raise LedgerError(
                "sidecar invalid: "
                + ", ".join(f"{i.code}@{i.field}" for i in issues)
            )
        return
    raise LedgerError(f"material id not found: {material_id}")
