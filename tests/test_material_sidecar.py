"""MS-02: material_sidecar の最小テスト。"""

from __future__ import annotations

import pytest

from src.pipeline.material_sidecar import (
    SidecarUsageError,
    assert_usable_for_thumbnail,
    restrictions_are_at_least_as_strict,
    validate_sidecar,
)


def _passable_sidecar() -> dict:
    return {
        "schema_version": "v1",
        "asset_id": "mat_001",
        "asset_path": "materials/mat_001/x.png",
        "asset_hash_sha256": "0" * 64,
        "source": {
            "kind": "official_clip_permitted_source",
            "url": "https://www.youtube.com/watch?v=AAA",
            "retrieved_at": "2026-05-06T11:00:00+09:00",
            "retrieved_by": "user:tester",
            "retrieval_method": "manual_screenshot",
        },
        "license": {
            "kind": "guideline_permitted",
            "guideline_url": "https://www.hololive.tv/terms",
            "guideline_version_checked_at": "2026-05-06",
        },
        "usage_conditions": ["credit_required", "source_link_required"],
        "restrictions": {
            "thumbnail_use": "allowed",
            "commercial_use": "guideline_dependent",
            "modification": "allowed_minor_only",
            "redistribution": "denied",
        },
        "attribution_text": "© hololive production",
        "derived_from": None,
    }


def test_passable_sidecar_validates_clean():
    assert validate_sidecar(_passable_sidecar()) == []


def test_unverified_source_blocks_thumbnail():
    sc = _passable_sidecar()
    sc["source"]["kind"] = "unverified"
    with pytest.raises(SidecarUsageError, match="unverified"):
        assert_usable_for_thumbnail(sc)


def test_unknown_license_blocks_thumbnail():
    sc = _passable_sidecar()
    sc["license"]["kind"] = "unknown"
    with pytest.raises(SidecarUsageError, match="unknown"):
        assert_usable_for_thumbnail(sc)


def test_thumbnail_use_denied_blocks_thumbnail():
    sc = _passable_sidecar()
    sc["restrictions"]["thumbnail_use"] = "denied"
    with pytest.raises(SidecarUsageError, match="thumbnail_use"):
        assert_usable_for_thumbnail(sc)


def test_empty_usage_conditions_is_invalid():
    sc = _passable_sidecar()
    sc["usage_conditions"] = []
    issues = validate_sidecar(sc)
    assert any(i.code == "SIDECAR_USAGE_CONDITIONS_EMPTY" for i in issues)


def test_derived_restrictions_must_be_at_least_as_strict():
    original = _passable_sidecar()
    original["restrictions"]["thumbnail_use"] = "denied"

    derived = _passable_sidecar()
    derived["restrictions"]["thumbnail_use"] = "allowed"  # 緩めている

    issues = restrictions_are_at_least_as_strict(derived, original)
    assert any(
        i.code == "DERIVED_RESTRICTION_LOOSER_THAN_ORIGINAL"
        and i.field == "restrictions.thumbnail_use"
        for i in issues
    )
