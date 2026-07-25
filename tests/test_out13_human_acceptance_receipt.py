from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT / "docs" / "output_layer" / "out13_human_acceptance_receipt.json"
)
EXPECTED_MEDIA_SHA256 = (
    "a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5"
)
EXPECTED_CONTEXT_ID = (
    "out13_candidate_005_internal_full_view_editorial_visual_review_v1"
)


def _load_receipt() -> dict:
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def _resolve_review_gate(
    receipt: dict,
    *,
    media_sha256: str,
    review_context_id: str,
    requested_dimensions: set[str],
    changed_dimensions: set[str] | None = None,
    affected_timestamps: list[list[float]] | None = None,
) -> dict:
    accepted_dimensions = set(receipt["review_context"]["accepted_dimensions"])
    same_identity = (
        media_sha256 == receipt["review_context"]["media_sha256"]
        and review_context_id == receipt["review_context"]["context_id"]
        and requested_dimensions <= accepted_dimensions
    )
    changed = changed_dimensions or set()
    reopened_dimensions = requested_dimensions & changed if same_identity else requested_dimensions
    return {
        "human_review_pending": bool(reopened_dimensions),
        "inherited_dimensions": sorted(requested_dimensions - reopened_dimensions),
        "reopened_dimensions": sorted(reopened_dimensions),
        "affected_timestamps": affected_timestamps or [],
    }


def test_out13_acceptance_receipt_binds_user_verdict_to_exact_media_and_scope() -> (
    None
):
    receipt = _load_receipt()

    assert receipt["schema_version"] == (
        "clippipegen.out13.human_acceptance_receipt.v1"
    )
    assert receipt["artifact_id"] == "clip-out13-editorial-video-candidate-v1-005"
    assert receipt["decision_source"] == "user_statement_in_supervising_thread"
    assert receipt["decision_authority"] == "user"
    assert receipt["verdict"] == "accept"
    assert receipt["review_context"] == {
        "context_id": EXPECTED_CONTEXT_ID,
        "scope": "internal_full_view_editorial_visual_review",
        "procedure_source": "docs/CURRENT_HANDOFF.md",
        "media_sha256": EXPECTED_MEDIA_SHA256,
        "media_byte_size": 82594810,
        "media_duration_seconds": 128.833333,
        "accepted_dimensions": [
            "editorial_composition",
            "editorial_flow",
            "subtitle_presentation",
            "picture_quality_for_internal_editorial_use",
            "audio_quality_for_internal_editorial_use",
        ],
    }
    assert receipt["human_review_pending"] is False
    assert receipt["acceptance_granted"] is True
    assert receipt["main_integration_approved"] is False
    assert not any(receipt["closed_gates"].values())


def test_same_media_context_and_dimensions_do_not_reopen_human_review() -> None:
    receipt = _load_receipt()
    requested_dimensions = set(receipt["review_context"]["accepted_dimensions"])

    result = _resolve_review_gate(
        receipt,
        media_sha256=EXPECTED_MEDIA_SHA256,
        review_context_id=EXPECTED_CONTEXT_ID,
        requested_dimensions=requested_dimensions,
    )

    assert result == {
        "human_review_pending": False,
        "inherited_dimensions": sorted(requested_dimensions),
        "reopened_dimensions": [],
        "affected_timestamps": [],
    }
    assert receipt["acceptance_inheritance"][
        "package_revision_change_alone_reopens_review"
    ] is False
    assert receipt["acceptance_inheritance"][
        "implementation_revision_change_alone_reopens_review"
    ] is False
    assert receipt["deduplicated_review_targets"][0]["artifact_id"].endswith("-004")
    assert receipt["deduplicated_review_targets"][0]["human_review_pending"] is False


def test_future_bounded_repair_reopens_only_affected_dimension_and_timestamps() -> (
    None
):
    receipt = _load_receipt()
    requested_dimensions = set(receipt["review_context"]["accepted_dimensions"])

    result = _resolve_review_gate(
        receipt,
        media_sha256=EXPECTED_MEDIA_SHA256,
        review_context_id=EXPECTED_CONTEXT_ID,
        requested_dimensions=requested_dimensions,
        changed_dimensions={"subtitle_presentation"},
        affected_timestamps=[[42.0, 47.5]],
    )

    assert result["human_review_pending"] is True
    assert result["reopened_dimensions"] == ["subtitle_presentation"]
    assert result["affected_timestamps"] == [[42.0, 47.5]]
    assert set(result["inherited_dimensions"]) == requested_dimensions - {
        "subtitle_presentation"
    }


def test_current_state_closes_m2_and_m4_without_opening_external_gates() -> None:
    runtime = (ROOT / "docs" / "RUNTIME_STATE.md").read_text(encoding="utf-8")
    handoff = (ROOT / "docs" / "CURRENT_HANDOFF.md").read_text(encoding="utf-8")

    for text in (runtime, handoff):
        assert "human_review_pending: false" in text
        assert "editorial_acceptance_granted: true" in text
        assert (
            "acceptance_receipt: "
            "docs/output_layer/out13_human_acceptance_receipt.json"
            in text
        )
        assert "main_integration_approved: true" in text
        assert "m4_main_integration_status: complete" in text
        assert "m5_integrated_baseline_verification_status: passed" in text
        assert "m6_rights_status: not_started_rights_pending" in text
        assert "rights_approval: pending" in text
        assert "production_acceptance: false" in text
        assert "public_or_publishing_acceptance: false" in text
        assert "this_commit_after_push" not in text


def test_out13_current_contract_uses_bounded_local_threat_model_wording() -> None:
    contract = (
        ROOT / "docs" / "output_layer" / "OUT_13_EDITORIAL_VIDEO_CANDIDATE.md"
    ).read_text(encoding="utf-8")

    assert "local threat model" in contract
    assert "exact-byte/content consistency" in contract
    assert "永久に不変化" not in contract
    assert "trust root" not in contract
    assert "現在の`DESKTOP-U9P4LKJ` checkoutにはcandidate 004 / 005" not in contract
