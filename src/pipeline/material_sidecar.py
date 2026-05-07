"""material_sidecar schema v1: 1素材1個の出典・ライセンス・利用条件。

正本仕様: docs/SCHEMAS/v1/material_sidecar.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .validation import ValidationIssue

SCHEMA_VERSION = "v1"

VALID_SOURCE_KINDS = {
    "official_clip_permitted_source",
    "official_promotional_material",
    "licensed_stock",
    "creative_commons",
    "user_created",
    "derived_from_other_asset",
    "unverified",
}

VALID_LICENSE_KINDS = {
    "guideline_permitted",
    "cc_by",
    "cc_by_sa",
    "cc0",
    "commercial",
    "proprietary",
    "fair_use_claimed",
    "unknown",
}

VALID_USAGE_CONDITIONS = {
    "credit_required",
    "source_link_required",
    "no_misleading_thumbnail",
    "no_membership_only_content",
    "no_political_use",
    "no_adult_content",
    "monetization_subject_to_guideline",
    "none",
}

VALID_RESTRICTION_VALUES = {
    "allowed",
    "denied",
    "guideline_dependent",
    "allowed_minor_only",
    "requires_explicit_permission",
}

REQUIRED_RESTRICTION_KEYS = (
    "thumbnail_use",
    "commercial_use",
    "modification",
    "redistribution",
)


class SidecarUsageError(Exception):
    """Legacy compatibility exception.

    Sidecar source/license/restriction values are no longer hard usage gates.
    """


def load_sidecar(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_sidecar(sidecar: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(sidecar, f, ensure_ascii=False, indent=2)
        f.write("\n")


def validate_sidecar(sidecar: dict[str, Any]) -> list[ValidationIssue]:
    """構造バリデーション。utility 関係（hash や derived_from の original 解決）は ledger 側で行う。"""
    issues: list[ValidationIssue] = []

    if sidecar.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                code="SIDECAR_SCHEMA_VERSION",
                field="schema_version",
                message=f"expected {SCHEMA_VERSION!r}",
            )
        )

    for required in ("asset_id", "asset_path", "asset_hash_sha256", "attribution_text"):
        if not sidecar.get(required):
            issues.append(
                ValidationIssue(
                    code="SIDECAR_FIELD_MISSING",
                    field=required,
                    message=f"{required} is required",
                )
            )

    issues.extend(_validate_source(sidecar.get("source")))
    issues.extend(_validate_license(sidecar.get("license")))
    issues.extend(_validate_usage_conditions(sidecar.get("usage_conditions")))
    issues.extend(_validate_restrictions(sidecar.get("restrictions")))
    issues.extend(_validate_derived_from(sidecar.get("derived_from")))

    return issues


def _validate_source(src: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(src, dict):
        return [
            ValidationIssue(
                code="SIDECAR_SOURCE_MISSING",
                field="source",
                message="source object is required",
            )
        ]
    if src.get("kind") not in VALID_SOURCE_KINDS:
        issues.append(
            ValidationIssue(
                code="SIDECAR_SOURCE_KIND_INVALID",
                field="source.kind",
                message=f"must be one of {sorted(VALID_SOURCE_KINDS)}",
            )
        )
    for required in ("retrieved_at", "retrieved_by", "retrieval_method"):
        if not src.get(required):
            issues.append(
                ValidationIssue(
                    code="SIDECAR_SOURCE_FIELD_MISSING",
                    field=f"source.{required}",
                    message=f"{required} is required",
                )
            )
    return issues


def _validate_license(lic: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(lic, dict):
        return [
            ValidationIssue(
                code="SIDECAR_LICENSE_MISSING",
                field="license",
                message="license object is required",
            )
        ]
    if lic.get("kind") not in VALID_LICENSE_KINDS:
        issues.append(
            ValidationIssue(
                code="SIDECAR_LICENSE_KIND_INVALID",
                field="license.kind",
                message=f"must be one of {sorted(VALID_LICENSE_KINDS)}",
            )
        )
    if lic.get("kind") == "guideline_permitted":
        if not lic.get("guideline_url"):
            issues.append(
                ValidationIssue(
                    code="SIDECAR_LICENSE_GUIDELINE_URL_MISSING",
                    field="license.guideline_url",
                    message="guideline_url is required when license.kind=guideline_permitted",
                )
            )
        if not lic.get("guideline_version_checked_at"):
            issues.append(
                ValidationIssue(
                    code="SIDECAR_LICENSE_GUIDELINE_VERSION_MISSING",
                    field="license.guideline_version_checked_at",
                    message="guideline_version_checked_at is required",
                )
            )
    return issues


def _validate_usage_conditions(items: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(items, list) or not items:
        return [
            ValidationIssue(
                code="SIDECAR_USAGE_CONDITIONS_EMPTY",
                field="usage_conditions",
                message="at least one usage_condition is required (use ['none'] for unrestricted)",
            )
        ]
    for i, c in enumerate(items):
        if c not in VALID_USAGE_CONDITIONS:
            issues.append(
                ValidationIssue(
                    code="SIDECAR_USAGE_CONDITION_INVALID",
                    field=f"usage_conditions[{i}]",
                    message=f"must be one of {sorted(VALID_USAGE_CONDITIONS)}",
                )
            )
    return issues


def _validate_restrictions(r: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(r, dict):
        return [
            ValidationIssue(
                code="SIDECAR_RESTRICTIONS_MISSING",
                field="restrictions",
                message="restrictions object is required",
            )
        ]
    for key in REQUIRED_RESTRICTION_KEYS:
        v = r.get(key)
        if v is None:
            issues.append(
                ValidationIssue(
                    code="SIDECAR_RESTRICTION_MISSING",
                    field=f"restrictions.{key}",
                    message=f"{key} is required",
                )
            )
        elif v not in VALID_RESTRICTION_VALUES:
            issues.append(
                ValidationIssue(
                    code="SIDECAR_RESTRICTION_VALUE_INVALID",
                    field=f"restrictions.{key}",
                    message=f"must be one of {sorted(VALID_RESTRICTION_VALUES)}",
                )
            )
    return issues


def _validate_derived_from(d: Any) -> list[ValidationIssue]:
    if d is None:
        return []
    issues: list[ValidationIssue] = []
    if not isinstance(d, dict):
        return [
            ValidationIssue(
                code="SIDECAR_DERIVED_FROM_INVALID",
                field="derived_from",
                message="must be object or null",
            )
        ]
    for required in ("original_asset_id", "derivation_kind", "derived_at"):
        if not d.get(required):
            issues.append(
                ValidationIssue(
                    code="SIDECAR_DERIVED_FROM_FIELD_MISSING",
                    field=f"derived_from.{required}",
                    message=f"{required} is required when derived_from is set",
                )
            )
    return issues


def assert_usable_for_thumbnail(sidecar: dict[str, Any]) -> None:
    """Legacy no-op: sidecar policy values are readback, not execution blockers."""
    _ = sidecar
    return None


def restrictions_are_at_least_as_strict(
    derived: dict[str, Any], original: dict[str, Any]
) -> list[ValidationIssue]:
    """Legacy no-op: derived restriction values are not hard-blocking."""
    _ = derived
    _ = original
    return []
