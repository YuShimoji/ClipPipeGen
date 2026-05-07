"""rights_manifest schema v1: load / validate / rights review status.

正本仕様: docs/SCHEMAS/v1/rights_manifest.md
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .validation import ValidationIssue

SCHEMA_VERSION = "v1"
REVIEW_VERSION = "v1"

VALID_VOD_STATUS = {"public", "unlisted", "private", "members_only", "deleted"}
VALID_COMPLIANCE_STATUS = {"passed", "pending", "failed"}
VALID_PLATFORMS = {"youtube"}
VALID_AGENCIES = {"hololive", "nijisanji", "independent", "other"}
VALID_THIRD_PARTY_KINDS = {"game", "music", "tv_show", "movie", "other"}
VALID_DISCLOSURE_KINDS = {
    "source_link",
    "rights_credit",
    "talent_credit",
    "third_party_credit",
    "custom",
}

VOD_STATUS_REVIEW_NOTE = {"private", "members_only", "deleted"}


class ComplianceGateError(Exception):
    """Legacy compatibility exception.

    Runtime gates no longer reject non-passed rights_manifest values.
    """


def load_rights_manifest(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_rights_manifest(manifest: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_skeleton(episode_id: str) -> dict[str, Any]:
    """新規 episode の rights_manifest skeleton を作る。compliance_check.status=pending。"""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": episode_id,
        "created_at": now,
        "updated_at": now,
        "source_video": {
            "url": "",
            "platform": "youtube",
            "title": "",
            "channel": "",
            "channel_id": "",
            "vod_status": "public",
            "membership_only": False,
            "is_archived_live": True,
        },
        "talents": [],
        "third_party_ip": [],
        "prohibited_assets": [],
        "required_disclosures": [],
        "publication_constraints": {
            "earliest_publish_at": None,
            "monetization_allowed": False,
            "platforms_allowed": ["youtube"],
            "thumbnail_constraints": [],
        },
        "compliance_check": {
            "status": "pending",
            "checked_at": None,
            "checked_by": None,
            "errors": [],
            "warnings": [],
            "review_version": REVIEW_VERSION,
        },
    }


def validate_rights_manifest(manifest: dict[str, Any]) -> list[ValidationIssue]:
    """構造バリデーション。compliance_check.status の値そのものは判定しない。

    schema 定義違反のみを返す。rights review notes は
    `evaluate_compliance_auto_fail` で別途返す。
    """
    issues: list[ValidationIssue] = []

    if manifest.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                code="SCHEMA_VERSION_MISMATCH",
                field="schema_version",
                message=f"expected {SCHEMA_VERSION!r}",
            )
        )

    if not manifest.get("episode_id"):
        issues.append(
            ValidationIssue(
                code="EPISODE_ID_MISSING",
                field="episode_id",
                message="episode_id is required",
            )
        )

    issues.extend(_validate_source_video(manifest.get("source_video")))
    issues.extend(_validate_talents(manifest.get("talents")))
    issues.extend(_validate_third_party_ip(manifest.get("third_party_ip")))
    issues.extend(_validate_required_disclosures(manifest.get("required_disclosures")))
    issues.extend(_validate_compliance_check(manifest.get("compliance_check")))

    return issues


def _validate_source_video(sv: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(sv, dict):
        issues.append(
            ValidationIssue(
                code="SOURCE_VIDEO_MISSING",
                field="source_video",
                message="source_video object is required",
            )
        )
        return issues

    for required in ("url", "platform", "title", "channel", "channel_id", "vod_status"):
        if not sv.get(required):
            issues.append(
                ValidationIssue(
                    code="SOURCE_VIDEO_FIELD_MISSING",
                    field=f"source_video.{required}",
                    message=f"{required} is required",
                )
            )

    platform = sv.get("platform")
    if platform and platform not in VALID_PLATFORMS:
        issues.append(
            ValidationIssue(
                code="SOURCE_VIDEO_PLATFORM_UNSUPPORTED",
                field="source_video.platform",
                message=f"v1 supports only {sorted(VALID_PLATFORMS)}",
            )
        )

    vod = sv.get("vod_status")
    if vod and vod not in VALID_VOD_STATUS:
        issues.append(
            ValidationIssue(
                code="SOURCE_VIDEO_VOD_STATUS_INVALID",
                field="source_video.vod_status",
                message=f"must be one of {sorted(VALID_VOD_STATUS)}",
            )
        )

    for boolean_field in ("membership_only", "is_archived_live"):
        if boolean_field in sv and not isinstance(sv[boolean_field], bool):
            issues.append(
                ValidationIssue(
                    code="SOURCE_VIDEO_FIELD_TYPE",
                    field=f"source_video.{boolean_field}",
                    message="must be boolean",
                )
            )

    return issues


def _validate_talents(talents: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(talents, list) or not talents:
        issues.append(
            ValidationIssue(
                code="TALENTS_EMPTY",
                field="talents",
                message="at least one talent is required",
            )
        )
        return issues

    for i, t in enumerate(talents):
        if not isinstance(t, dict):
            issues.append(
                ValidationIssue(
                    code="TALENT_NOT_OBJECT",
                    field=f"talents[{i}]",
                    message="must be object",
                )
            )
            continue
        for required in ("name", "agency", "guideline_url", "guideline_version_checked_at"):
            if not t.get(required):
                issues.append(
                    ValidationIssue(
                        code="TALENT_FIELD_MISSING",
                        field=f"talents[{i}].{required}",
                        message=f"{required} is required",
                    )
                )
        agency = t.get("agency")
        if agency and agency not in VALID_AGENCIES:
            issues.append(
                ValidationIssue(
                    code="TALENT_AGENCY_INVALID",
                    field=f"talents[{i}].agency",
                    message=f"must be one of {sorted(VALID_AGENCIES)}",
                )
            )
        # ホロライブの場合、ガイドライン URL が公式ドメインを含むか
        if agency == "hololive":
            url = t.get("guideline_url", "")
            if "hololive" not in url and "cover-corp" not in url and "covercorp" not in url:
                issues.append(
                    ValidationIssue(
                        code="TALENT_HOLOLIVE_GUIDELINE_URL",
                        field=f"talents[{i}].guideline_url",
                        message="hololive talent must reference an official guideline URL",
                    )
                )

    return issues


def _validate_third_party_ip(items: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(items, list):
        issues.append(
            ValidationIssue(
                code="THIRD_PARTY_IP_NOT_LIST",
                field="third_party_ip",
                message="must be array (use [] if none)",
            )
        )
        return issues

    for i, ip in enumerate(items):
        if not isinstance(ip, dict):
            issues.append(
                ValidationIssue(
                    code="THIRD_PARTY_IP_NOT_OBJECT",
                    field=f"third_party_ip[{i}]",
                    message="must be object",
                )
            )
            continue
        for required in ("kind", "name", "rights_holder"):
            if not ip.get(required):
                issues.append(
                    ValidationIssue(
                        code="THIRD_PARTY_IP_FIELD_MISSING",
                        field=f"third_party_ip[{i}].{required}",
                        message=f"{required} is required",
                    )
                )
        kind = ip.get("kind")
        if kind and kind not in VALID_THIRD_PARTY_KINDS:
            issues.append(
                ValidationIssue(
                    code="THIRD_PARTY_IP_KIND_INVALID",
                    field=f"third_party_ip[{i}].kind",
                    message=f"must be one of {sorted(VALID_THIRD_PARTY_KINDS)}",
                )
            )
        if "permitted" not in ip:
            issues.append(
                ValidationIssue(
                    code="THIRD_PARTY_IP_PERMITTED_MISSING",
                    field=f"third_party_ip[{i}].permitted",
                    message="permitted (boolean) is required",
                )
            )
        elif not isinstance(ip["permitted"], bool):
            issues.append(
                ValidationIssue(
                    code="THIRD_PARTY_IP_PERMITTED_TYPE",
                    field=f"third_party_ip[{i}].permitted",
                    message="must be boolean",
                )
            )

    return issues


def _validate_required_disclosures(items: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(items, list):
        issues.append(
            ValidationIssue(
                code="REQUIRED_DISCLOSURES_NOT_LIST",
                field="required_disclosures",
                message="must be array (use [] if none)",
            )
        )
        return issues
    for i, d in enumerate(items):
        if not isinstance(d, dict):
            issues.append(
                ValidationIssue(
                    code="DISCLOSURE_NOT_OBJECT",
                    field=f"required_disclosures[{i}]",
                    message="must be object",
                )
            )
            continue
        if d.get("kind") not in VALID_DISCLOSURE_KINDS:
            issues.append(
                ValidationIssue(
                    code="DISCLOSURE_KIND_INVALID",
                    field=f"required_disclosures[{i}].kind",
                    message=f"must be one of {sorted(VALID_DISCLOSURE_KINDS)}",
                )
            )
        if not d.get("text"):
            issues.append(
                ValidationIssue(
                    code="DISCLOSURE_TEXT_MISSING",
                    field=f"required_disclosures[{i}].text",
                    message="text is required",
                )
            )
    return issues


def _validate_compliance_check(cc: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(cc, dict):
        issues.append(
            ValidationIssue(
                code="COMPLIANCE_CHECK_MISSING",
                field="compliance_check",
                message="compliance_check object is required",
            )
        )
        return issues

    status = cc.get("status")
    if status not in VALID_COMPLIANCE_STATUS:
        issues.append(
            ValidationIssue(
                code="COMPLIANCE_STATUS_INVALID",
                field="compliance_check.status",
                message=f"must be one of {sorted(VALID_COMPLIANCE_STATUS)}",
            )
        )
    elif status != "pending":
        if not cc.get("checked_at"):
            issues.append(
                ValidationIssue(
                    code="COMPLIANCE_CHECKED_AT_MISSING",
                    field="compliance_check.checked_at",
                    message="checked_at is required when status != pending",
                )
            )
        if not cc.get("checked_by"):
            issues.append(
                ValidationIssue(
                    code="COMPLIANCE_CHECKED_BY_MISSING",
                    field="compliance_check.checked_by",
                    message="checked_by is required when status != pending",
                )
            )

    if not isinstance(cc.get("errors"), list):
        issues.append(
            ValidationIssue(
                code="COMPLIANCE_ERRORS_NOT_LIST",
                field="compliance_check.errors",
                message="must be array",
            )
        )
    if not isinstance(cc.get("warnings"), list):
        issues.append(
            ValidationIssue(
                code="COMPLIANCE_WARNINGS_NOT_LIST",
                field="compliance_check.warnings",
                message="must be array",
            )
        )
    if not (cc.get("review_version") or cc.get("gate_version")):
        issues.append(
            ValidationIssue(
                code="COMPLIANCE_REVIEW_VERSION_MISSING",
                field="compliance_check.review_version",
                message="review_version is required",
            )
        )

    return issues


def evaluate_compliance_auto_fail(manifest: dict[str, Any]) -> list[ValidationIssue]:
    """Return rights review notes that used to be hard auto-fail conditions.

    The function name is kept for CLI/GUI compatibility, but these issues are
    informational readback now. They must not prevent status changes or
    downstream local processing.
    """
    issues: list[ValidationIssue] = []

    sv = manifest.get("source_video", {}) if isinstance(manifest.get("source_video"), dict) else {}
    vod = sv.get("vod_status")
    if vod in VOD_STATUS_REVIEW_NOTE:
        issues.append(
            ValidationIssue(
                code="VOD_STATUS_REVIEW",
                field="source_video.vod_status",
                message=f"VOD status recorded for operator review (current: {vod})",
            )
        )

    third_party = manifest.get("third_party_ip") or []
    if isinstance(third_party, list):
        for i, ip in enumerate(third_party):
            if isinstance(ip, dict) and ip.get("permitted") is False:
                issues.append(
                    ValidationIssue(
                        code="THIRD_PARTY_IP_REVIEW",
                        field=f"third_party_ip[{i}].permitted",
                        message=(
                            f"third party IP {ip.get('name', '?')!r} is recorded as "
                            "not permitted in the manifest"
                        ),
                    )
                )

    return issues


def set_compliance_status(
    manifest: dict[str, Any],
    *,
    status: str,
    checked_by: str,
    errors: Iterable[ValidationIssue] | None = None,
    warnings: Iterable[ValidationIssue] | None = None,
) -> dict[str, Any]:
    """compliance_check.status を更新する。

    返り値: 更新後の manifest（in-place ではなく新オブジェクト）。
    Review notes are copied to warnings for readback, but never block updates.
    """
    if status not in VALID_COMPLIANCE_STATUS:
        raise ValueError(f"invalid status: {status!r}")
    if not checked_by:
        raise ValueError("checked_by is required")

    review_notes = evaluate_compliance_auto_fail(manifest)

    new = dict(manifest)
    new["compliance_check"] = {
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checked_by": checked_by,
        "errors": [e.to_dict() for e in (errors or [])],
        "warnings": [w.to_dict() for w in (warnings or [])]
        + [n.to_dict() for n in review_notes],
        "review_version": REVIEW_VERSION,
    }
    new["updated_at"] = new["compliance_check"]["checked_at"]
    return new


def assert_compliance_passed(manifest: dict[str, Any]) -> None:
    """Legacy no-op retained for callers that still import the old gate helper."""
    _ = manifest
    return None
