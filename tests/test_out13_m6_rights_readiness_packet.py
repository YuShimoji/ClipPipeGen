from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = (
    ROOT / "docs" / "rights" / "out13_m6_rights_decision_readiness_packet.json"
)
RUNTIME_PATH = ROOT / "docs" / "RUNTIME_STATE.md"
HANDOFF_PATH = ROOT / "docs" / "CURRENT_HANDOFF.md"

EXPECTED_MATERIAL_IDS = {
    "out13-source-visual-stream",
    "out13-source-audio-stream",
    "out13-normalized-source-audio-derivative",
    "out13-provider-caption-text",
    "out13-transcript-derivative",
    "out13-keifont-glyph-rendering",
    "out13-generated-editorial-and-subtitle-layers",
    "out13-source-embedded-rights-concerns",
}
EXPECTED_RANGES = {
    "cut_001": (2.453, 17.167),
    "cut_002": (22.606, 24.041),
    "cut_003": (25.109, 49.566),
    "cut_004": (50.868, 79.163),
    "cut_005": (81.298, 94.945),
    "cut_006": (95.345, 116.467),
    "cut_007": (116.934, 142.059),
}
EXPECTED_OMISSIONS = (
    (0.0, 2.453),
    (17.167, 22.606),
    (24.041, 25.109),
    (49.566, 50.868),
    (79.163, 81.298),
    (94.945, 95.345),
    (116.467, 116.934),
    (142.059, 164.768798),
)
TECHNICAL_LOCATORS = {
    "source_video",
    "source_video_fetch_receipt",
    "source_audio",
    "source_audio_fetch_receipt",
    "material_ledger",
    "provider_caption_json3",
    "caption_provenance",
    "caption_acquisition_receipt",
    "transcript",
    "transcript_authority_snapshot",
    "authority_binding",
    "editorial_plan",
    "timeline_ir",
    "provenance_snapshot",
    "caption_readback",
    "validation_readback",
    "run_manifest",
}


def _packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


def _packet_errors(packet: dict) -> list[str]:
    errors: list[str] = []
    readiness_states = set(packet["controlled_vocabularies"]["readiness_states"])
    owner_verdicts = set(packet["controlled_vocabularies"]["owner_verdicts"])
    materials = packet.get("material_inventory", [])
    ranges = packet.get("source_range_inventory", [])
    material_ids = [row.get("material_id") for row in materials]
    range_ids = [row.get("range_id") for row in ranges]

    if len(material_ids) != len(set(material_ids)):
        errors.append("duplicate_material_id")
    if len(range_ids) != len(set(range_ids)):
        errors.append("duplicate_range_id")

    if packet.get("packet_readiness_status") in {
        "READY_FOR_HUMAN_RIGHTS_DECISION",
        "M6_CLOSED_DENY_EXACT_ARTIFACT",
    }:
        if set(material_ids) != EXPECTED_MATERIAL_IDS:
            errors.append("ready_packet_material_inventory_incomplete")
        if set(range_ids) != set(EXPECTED_RANGES):
            errors.append("ready_packet_range_inventory_incomplete")
        if len(packet.get("omitted_source_ranges", [])) != len(EXPECTED_OMISSIONS):
            errors.append("ready_packet_omission_inventory_incomplete")

    authority_ids = {
        row["authority_id"] for row in packet.get("primary_authorities", [])
    }
    known_locators = set(packet.get("evidence_locators", {})) | authority_ids
    for row in materials:
        for required_field in (
            "material_id",
            "technical_identity",
            "provenance_identity",
            "asserted_owner",
            "permission_status",
            "usage_scope",
            "readiness_state",
            "owner_verdict",
            "evidence_locators",
        ):
            if required_field not in row:
                errors.append(
                    f"missing_material_field={row.get('material_id')}:{required_field}"
                )
        if not row.get("evidence_classes"):
            errors.append(f"missing_material_evidence_class={row.get('material_id')}")
        if not row.get("usage_scope"):
            errors.append(f"missing_material_usage_scope={row.get('material_id')}")
        if row.get("readiness_state") not in readiness_states:
            errors.append(f"bad_material_readiness={row.get('material_id')}")
        if row.get("owner_verdict") not in owner_verdicts:
            errors.append(f"bad_material_verdict={row.get('material_id')}")
        if row.get("technical_provenance_is_permission_evidence") is not False:
            errors.append(f"technical_promoted={row.get('material_id')}")
        unknown = set(row.get("evidence_locators", [])) - known_locators
        if unknown:
            errors.append(f"unknown_material_locator={row.get('material_id')}")
        if set(row.get("permission_evidence_locators", [])) & TECHNICAL_LOCATORS:
            errors.append(f"technical_locator_used_as_permission={row.get('material_id')}")

    for row in ranges:
        range_id = row.get("range_id")
        if row.get("readiness_state") not in readiness_states:
            errors.append(f"bad_range_readiness={range_id}")
        if row.get("owner_verdict") not in owner_verdicts:
            errors.append(f"bad_range_verdict={range_id}")
        if not set(row.get("incorporated_material_ids", [])) <= set(material_ids):
            errors.append(f"unknown_range_material={range_id}")
        unknown = set(row.get("evidence_locators", [])) - known_locators
        if unknown:
            errors.append(f"unknown_range_locator={range_id}")

    decision = packet.get("owner_decision_surface", {})
    boundary = packet.get("decision_boundary", {})
    if boundary.get("rights_approved") is True and not decision.get(
        "decision_authority_evidence_locator"
    ):
        errors.append("rights_approval_without_authority")
    approval_or_ready_claimed = (
        boundary.get("rights_approved") is True
        or packet.get("rights_ready") is True
        or packet.get("readiness_assessment", {}).get("rights_approval_claimed")
        is True
    )
    if approval_or_ready_claimed:
        if set(material_ids) != EXPECTED_MATERIAL_IDS:
            errors.append("approval_or_rights_ready_material_inventory_incomplete")
        if set(range_ids) != set(EXPECTED_RANGES):
            errors.append("approval_or_rights_ready_range_inventory_incomplete")
    if packet.get("packet_readiness_status") == "READY_FOR_HUMAN_RIGHTS_DECISION":
        if decision.get("overall_owner_verdict") != "undecided":
            errors.append("ready_packet_prefills_owner_verdict")
        if boundary.get("rights_approved") is not False:
            errors.append("ready_packet_claims_rights_approval")
    if packet.get("packet_readiness_status") == "M6_CLOSED_DENY_EXACT_ARTIFACT":
        decision_events = packet.get("decision_history", [])
        if len(decision_events) != 1:
            errors.append("closed_deny_requires_one_decision_event")
            return errors
        event = decision_events[0]
        exact_fields = {
            "starting_packet_revision": (
                "dac5f7fb715cb3a7acd6c982a80cb916492e7880"
            ),
            "packet_id": "clip-out13-m6-rights-decision-readiness-v1-001",
            "artifact_id": "clip-out13-editorial-video-candidate-v1-005",
            "exact_media_sha256": (
                "a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5"
            ),
            "decision_evidence_locator": (
                "docs/rights/out13_m6_rights_decision_readiness_packet.json"
                "#/decision_history/0"
            ),
        }
        for field, expected in exact_fields.items():
            if event.get(field) != expected:
                errors.append(f"closed_deny_exact_binding_mismatch={field}")
        for field in (
            "public_use_verdict",
            "monetized_youtube_verdict",
            "publication_decision",
            "monetization_decision",
            "overall_owner_verdict",
        ):
            if event.get(field) != "deny":
                errors.append(f"closed_deny_verdict_mismatch={field}")
        if event.get("rights_approval") != "not_granted":
            errors.append("closed_deny_launders_rights_approval")
        if boundary.get("rights_approved") is not False:
            errors.append("closed_deny_claims_rights_approved")
        if decision.get("overall_owner_verdict") != "deny":
            errors.append("closed_deny_owner_surface_mismatch")
        if any(row.get("owner_verdict") != "undecided" for row in materials + ranges):
            errors.append("closed_deny_launders_material_or_range_verdict")
        if event.get("successor_requirement", {}).get(
            "successor_created_or_specified_by_this_event"
        ) is not False:
            errors.append("closed_deny_improperly_specifies_successor")
        successor = event.get("successor_requirement", {})
        if not all(
            successor.get(field) is True
            for field in (
                "required_before_new_public_or_monetized_consideration",
                "materially_distinct_successor_required",
                "new_artifact_identity_required",
                "fresh_transformation_and_content_strategy_required",
                "fresh_material_and_range_inventory_required",
                "fresh_editorial_and_rights_review_required",
            )
        ):
            errors.append("closed_deny_generalizes_or_weakens_successor_boundary")
        if "No future or materially distinct artifact is denied." not in event.get(
            "non_claims", []
        ):
            errors.append("closed_deny_generalizes_future_artifact")
        assessment = packet.get("readiness_assessment", {})
        if (
            assessment.get("internal_editorial_acceptance_preserved") is not True
            or assessment.get("human_review_pending") is not False
        ):
            errors.append("closed_deny_reopens_or_drops_m2_acceptance")
        if boundary.get("public_default") != "off":
            errors.append("closed_deny_public_default_not_off")
        if boundary.get("excluded_from_production_publish_upload_release_candidate_sets") is not True:
            errors.append("closed_deny_candidate_set_exclusion_missing")
    return errors


def test_m6_packet_binds_exact_deny_and_does_not_claim_rights_approval() -> None:
    packet = _packet()

    assert _packet_errors(packet) == []
    assert packet["schema_version"] == (
        "clippipegen.out13.m6_rights_decision_readiness.v1"
    )
    assert packet["packet_readiness_status"] == "M6_CLOSED_DENY_EXACT_ARTIFACT"
    assert packet["baseline"]["main_revision_at_start"] == (
        "5bd6e65318df129bebc87291c2ae733f143ed8d8"
    )
    assert packet["baseline"]["accepted_feature_revision"] == (
        "18641fe917b084259869263e8db05d78325aa2db"
    )
    assert packet["baseline"]["packet_revision_locator"] == (
        "refs/heads/codex/m6-rights-decision-readiness-v1:"
        "docs/rights/out13_m6_rights_decision_readiness_packet.json"
    )
    assert packet["baseline"]["artifact_id"] == (
        "clip-out13-editorial-video-candidate-v1-005"
    )
    assert packet["baseline"]["accepted_media_sha256"] == (
        "a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5"
    )
    assert packet["decision_boundary"]["rights_approved"] is False
    assert packet["decision_boundary"]["rights_approval"] == "not_granted"
    assert packet["decision_boundary"]["public_use_verdict"] == "deny"
    assert packet["decision_boundary"]["monetized_youtube_verdict"] == "deny"
    assert packet["owner_decision_surface"]["overall_owner_verdict"] == "deny"
    assert packet["readiness_assessment"]["rights_approval_claimed"] is False
    assert packet["readiness_assessment"]["technical_provenance_separated_from_permission"]
    assert set(packet["controlled_vocabularies"]["evidence_classes"]) == {
        "technical_provenance",
        "content_identity",
        "content_observation",
        "primary_terms",
        "license_or_terms_evidence",
        "owner_representation",
        "permission_or_owner_authority",
        "attribution_obligation",
        "territorial_platform_monetization_restriction",
        "unresolved_legal_or_policy_question",
        "editorial_acceptance",
        "platform_policy",
    }
    assert {
        row["authority_id"] for row in packet["primary_authorities"]
    } == {
        "cover-hololive-derivative-works-guidelines",
        "keifont-primary-distribution-terms",
        "youtube-terms",
        "youtube-channel-monetization-policies",
        "youtube-content-monetization-rights",
    }


def test_m6_packet_preserves_intended_use_and_records_project_decision_surface() -> (
    None
):
    packet = _packet()
    intended_use = packet["intended_use_proposition"]
    owner = packet["owner_decision_surface"]

    assert intended_use["current_authorization"] is False
    assert intended_use["platform"] == "YouTube"
    assert intended_use["visibility"] == "public"
    assert intended_use["monetization"] == "contemplated_requires_owner_verdict"
    assert intended_use["territory"] == "worldwide_proposed"
    assert intended_use["content_id_registration"] is False
    assert intended_use["thumbnail_reuse"] == "excluded_from_this_proposition"
    assert intended_use["source_credit"] == {
        "source_url": "https://www.youtube.com/watch?v=7J5aS_pcBj4",
        "source_title": "【アニメ】押忍！！ば～んちょ だじぇ！",
        "source_channel": "hololive ホロライブ - VTuber Group",
        "required_in_description": True,
    }
    assert owner["owner_identity"]["readiness_state"] == (
        "project_publication_deny_recorded_underlying_rightsholder_identity_not_asserted"
    )
    assert owner["owner_identity"]["authority_evidence_locator"] == (
        "docs/rights/out13_m6_rights_decision_readiness_packet.json"
        "#/decision_history/0"
    )
    assert owner["owner_identity"]["publisher_or_channel_legal_identity"] is None
    assert owner["packet_revision_locator"] == (
        packet["baseline"]["packet_revision_locator"]
    )
    assert set(owner["decision_subject"]["material_ids"]) == EXPECTED_MATERIAL_IDS
    assert set(owner["decision_subject"]["range_ids"]) == set(EXPECTED_RANGES)
    assert owner["available_verdicts"] == [
        "allow",
        "deny",
        "allow_with_restrictions",
        "undecided",
    ]
    assert owner["decision_receipt_locator"] == (
        "docs/rights/out13_m6_rights_decision_readiness_packet.json"
        "#/decision_history/0"
    )


def test_m6_decision_history_preserves_ready_state_and_exact_user_evidence() -> None:
    packet = _packet()
    event = packet["decision_history"][0]

    assert packet["status_history"][0] == {
        "status": "READY_FOR_HUMAN_RIGHTS_DECISION",
        "recorded_revision": "dac5f7fb715cb3a7acd6c982a80cb916492e7880",
        "packet_locator": (
            "dac5f7fb715cb3a7acd6c982a80cb916492e7880:"
            "docs/rights/out13_m6_rights_decision_readiness_packet.json"
        ),
        "meaning": (
            "The exact-artifact inventory and unresolved questions were ready for "
            "a human project publication decision; no rights approval was claimed."
        ),
    }
    assert event["supervisor_recommendation"] == (
        "1. deny — exact MP4の収益公開は行わず、後継版へ移る"
    )
    assert event["user_instruction"] == "推奨の1.で作業を継続してください。"
    assert event["decision_capacity"] == (
        "user_as_project_publication_decision_owner_not_asserted_as_"
        "underlying_source_rightsholder"
    )
    assert event["successor_requirement"]["materially_distinct_successor_required"]
    assert event["successor_requirement"]["new_artifact_identity_required"]
    assert not event["successor_requirement"]["successor_created_or_specified_by_this_event"]
    assert len(event["non_claims"]) == 4


def test_m6_packet_covers_exact_selected_and_omitted_source_ranges() -> None:
    packet = _packet()
    actual_ranges = {
        row["range_id"]: (
            row["source_seconds"]["start"],
            row["source_seconds"]["end"],
        )
        for row in packet["source_range_inventory"]
    }
    actual_omissions = tuple(
        (row["start"], row["end"]) for row in packet["omitted_source_ranges"]
    )

    assert actual_ranges == EXPECTED_RANGES
    assert actual_omissions == EXPECTED_OMISSIONS
    assert all(
        row["readiness_state"] == "content_observation_required"
        for row in packet["source_range_inventory"]
    )
    assert all(
        row["owner_verdict"] == "undecided"
        for row in packet["source_range_inventory"]
    )
    assert packet["readiness_assessment"]["range_coverage_ratio"] == 1.0
    assert packet["readiness_assessment"]["selected_source_duration_seconds"] == 128.795


def test_closed_packet_fails_semantics_when_material_or_range_is_removed() -> None:
    packet = _packet()
    missing_material = copy.deepcopy(packet)
    missing_material["material_inventory"].pop()
    missing_range = copy.deepcopy(packet)
    missing_range["source_range_inventory"].pop()

    assert "ready_packet_material_inventory_incomplete" in _packet_errors(
        missing_material
    )
    assert "ready_packet_range_inventory_incomplete" in _packet_errors(missing_range)


def test_technical_provenance_cannot_be_promoted_to_permission_evidence() -> None:
    packet = _packet()
    promoted = copy.deepcopy(packet)
    promoted["material_inventory"][0]["permission_evidence_locators"] = [
        "source_video_fetch_receipt"
    ]

    assert "technical_locator_used_as_permission=out13-source-visual-stream" in (
        _packet_errors(promoted)
    )


def test_rights_approval_requires_owner_authority_evidence() -> None:
    packet = _packet()
    invalid = copy.deepcopy(packet)
    invalid["decision_boundary"]["rights_approved"] = True

    assert "closed_deny_claims_rights_approved" in _packet_errors(invalid)


def test_closed_deny_rejects_permission_laundering_and_scope_widening() -> None:
    packet = _packet()
    rights_laundered = copy.deepcopy(packet)
    rights_laundered["decision_history"][0]["rights_approval"] = "granted"
    row_laundered = copy.deepcopy(packet)
    row_laundered["material_inventory"][0]["owner_verdict"] = "deny"
    successor_widened = copy.deepcopy(packet)
    successor_widened["decision_history"][0]["successor_requirement"][
        "successor_created_or_specified_by_this_event"
    ] = True
    future_generalized = copy.deepcopy(packet)
    future_generalized["decision_history"][0]["non_claims"].remove(
        "No future or materially distinct artifact is denied."
    )
    m2_reopened = copy.deepcopy(packet)
    m2_reopened["readiness_assessment"]["human_review_pending"] = True

    assert "closed_deny_launders_rights_approval" in _packet_errors(rights_laundered)
    assert "closed_deny_launders_material_or_range_verdict" in _packet_errors(
        row_laundered
    )
    assert "closed_deny_improperly_specifies_successor" in _packet_errors(
        successor_widened
    )
    assert "closed_deny_generalizes_future_artifact" in _packet_errors(
        future_generalized
    )
    assert "closed_deny_reopens_or_drops_m2_acceptance" in _packet_errors(m2_reopened)


def test_closed_deny_rejects_any_exact_identity_or_evidence_drift() -> None:
    packet = _packet()
    fields = (
        "starting_packet_revision",
        "packet_id",
        "artifact_id",
        "exact_media_sha256",
        "decision_evidence_locator",
    )

    for field in fields:
        drifted = copy.deepcopy(packet)
        drifted["decision_history"][0][field] = "drifted"
        assert f"closed_deny_exact_binding_mismatch={field}" in _packet_errors(
            drifted
        )


def test_rights_ready_or_approved_claim_fails_when_inventory_is_incomplete() -> None:
    packet = _packet()
    approved_missing_material = copy.deepcopy(packet)
    approved_missing_material["decision_boundary"]["rights_approved"] = True
    approved_missing_material["owner_decision_surface"][
        "decision_authority_evidence_locator"
    ] = "docs/rights/hypothetical-owner-receipt.json"
    approved_missing_material["material_inventory"].pop()
    ready_missing_range = copy.deepcopy(packet)
    ready_missing_range["rights_ready"] = True
    ready_missing_range["source_range_inventory"].pop()

    assert "approval_or_rights_ready_material_inventory_incomplete" in (
        _packet_errors(approved_missing_material)
    )
    assert "approval_or_rights_ready_range_inventory_incomplete" in (
        _packet_errors(ready_missing_range)
    )


def test_runtime_handoff_and_packet_agree_on_m6_decision_state() -> None:
    packet = _packet()
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")

    for text in (runtime, handoff):
        assert "canonical_status: m6_closed_deny_exact_artifact" in text
        assert "m6_rights_status: closed_deny_exact_artifact" in text
        assert (
            f"m6_packet_status: {packet['packet_readiness_status']}" in text
        )
        assert (
            "m6_packet: docs/rights/"
            "out13_m6_rights_decision_readiness_packet.json"
            in text
        )
        assert "rights_approval: not_granted" in text
        assert "public_use_verdict: deny" in text
        assert "monetized_youtube_verdict: deny" in text
        assert "production_acceptance: false" in text
        assert "public_or_publishing_acceptance: false" in text
