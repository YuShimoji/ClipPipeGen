from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.cli import main
from src.integrations.render import editorial_video_candidate as out13
from src.integrations.render.push_microarc_stream import (
    PLAN_SCHEMA_VERSION,
    PushMicroarcStreamError,
    _validate_artifact_id,
    build_creator_context_linkage,
    build_metadata_draft,
    validate_push_microarc_plan,
)


def _plan() -> dict:
    publication_time = datetime.fromtimestamp(1000, tz=timezone.utc).isoformat()
    evidence_ids = [f"ev_{index}" for index in range(1, 6)]
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "artifact_id": "clip-out14-push-microarc-stream-v1-001",
        "profile": "PUSH_MICROARC",
        "delivery_lane_axis": "push",
        "source_attributes": {
            "content": "free_talk",
            "collaboration": "solo",
            "talent_scope": "single_talent",
            "language": "ja",
        },
        "episode_premise": "A bounded complete premise.",
        "source": {
            "identity": "youtube:source",
            "sha256": "a" * 64,
            "duration_seconds": 1200.0,
            "title": "Completed public stream",
            "publication_time": publication_time,
            "url": "https://www.youtube.com/watch?v=source",
        },
        "selection": {
            "source_in_seconds": 100.0,
            "source_out_seconds": 500.0,
        },
        "evidence_spans": [
            {
                "id": evidence_id,
                "source_in_seconds": 100.0 + (index * 80.0),
                "source_out_seconds": 180.0 + (index * 80.0),
                "summary": f"evidence {index + 1}",
            }
            for index, evidence_id in enumerate(evidence_ids)
        ],
        "cuts": [
            {
                "output_order": 1,
                "cut_id": "cut_001",
                "source_in_seconds": 100.0,
                "source_out_seconds": 500.0,
                "section": "bounded_episode",
                "editorial_role": "complete_micro_arc",
                "selection_reason": "Preserves the complete premise.",
                "direct_evidence_segment_ids": evidence_ids,
                "context_evidence": {
                    "segment_ids": evidence_ids,
                    "continuity_note": "One continuous source range.",
                },
                "transition": "sequence_start",
            }
        ],
        "omitted_ranges": [
            {
                "source_in_seconds": 0.0,
                "source_out_seconds": 100.0,
                "transcript_segment_ids": [],
                "omission_reason": "Before the episode.",
                "intentional_editorial_omission": True,
            },
            {
                "source_in_seconds": 500.0,
                "source_out_seconds": 1200.0,
                "transcript_segment_ids": [],
                "omission_reason": "After the episode.",
                "intentional_editorial_omission": True,
            },
        ],
        "semantic_arc": [
            {
                "role": role,
                "source_in_seconds": 100.0 + (index * 80.0),
                "source_out_seconds": 180.0 + (index * 80.0),
                "summary": f"role {index + 1}",
            }
            for index, role in enumerate(
                (
                    "hook_or_inciting_situation",
                    "necessary_context",
                    "development_or_escalation",
                    "turn_payoff_or_resolution",
                    "completing_aftermath",
                )
            )
        ],
        "creator_context": {
            "items": [],
            "omission_reason": "The source explains the premise directly.",
        },
        "rendered_section_labels": [],
        "natural_duration_exception": None,
        "metadata": {"draft_title": "Draft clip title"},
    }


def _timeline(plan: dict) -> dict:
    transcript = {
        "segments": [
            {
                "id": row["id"],
                "start_seconds": row["source_in_seconds"],
                "end_seconds": row["source_out_seconds"],
                "text": row["summary"],
            }
            for row in plan["evidence_spans"]
        ]
    }
    captions = [
        {
            "event_id": "caption_001",
            "source_start_seconds": 100.0,
            "source_end_seconds": 500.0,
            "text": "provider caption",
        }
    ]
    return out13.build_editorial_timeline(
        plan=plan,
        source_identity="youtube:source",
        source_sha256="a" * 64,
        source_duration_seconds=1200.0,
        transcript=transcript,
        caption_events=captions,
        plan_schema_version=PLAN_SCHEMA_VERSION,
        profile_schema_version="clippipegen.out14.push_microarc_stream.v1",
        min_output_seconds=240.0,
        max_output_seconds=1080.0,
        min_selected_cuts=1,
        min_intentional_omitted_spans=2,
        max_source_utilization_ratio=0.5,
        min_semantic_section_count=1,
        selection_mode="push_microarc_closed_episode_chronological_v1",
    )


def test_push_microarc_contract_accepts_one_closed_five_role_episode():
    plan = _plan()
    result = validate_push_microarc_plan(
        plan=plan,
        timeline=_timeline(plan),
        source_info={
            "title": plan["source"]["title"],
            "release_timestamp": 1000,
        },
    )

    assert result["status"] == "passed"
    assert result["semantic_role_count"] == 5
    assert result["cut_count"] == 1
    assert result["creator_context_count"] == 0
    assert result["natural_duration_contract"]["exception_used"] is False


@pytest.mark.parametrize(
    "mutator",
    (
        lambda plan: plan.update(artifact_id="clip-out13-editorial-video-v4-001"),
        lambda plan: plan["semantic_arc"].reverse(),
        lambda plan: plan.update(rendered_section_labels=["結論"]),
        lambda plan: plan["creator_context"].update(
            items=[{"id": "creator_context:001"}]
        ),
    ),
)
def test_push_microarc_contract_rejects_identity_and_presentation_drift(mutator):
    plan = _plan()
    mutator(plan)

    with pytest.raises(PushMicroarcStreamError):
        validate_push_microarc_plan(
            plan=plan,
            timeline=_timeline(_plan()),
            source_info={
                "title": plan["source"]["title"],
                "release_timestamp": 1000,
            },
        )


def test_metadata_and_context_keep_source_authority_and_namespaces_separate():
    plan = _plan()
    info = {
        "id": "source",
        "title": plan["source"]["title"],
        "channel": "Talent channel",
    }

    metadata = build_metadata_draft(plan=plan, source_info=info)
    context = build_creator_context_linkage(plan)

    assert metadata["description"].splitlines()[0] == plan["source"]["url"]
    assert metadata["description"].splitlines()[1] == plan["source"]["title"]
    assert metadata["checks"]["unofficial_disclosure_present"] is True
    assert metadata["checks"]["no_endorsement_claim_present"] is True
    assert context["source_caption_namespace"] != context["creator_context_namespace"]
    assert context["creator_context_count"] == 0


def test_cli_registers_push_microarc_profile():
    assert "build-push-microarc-stream" in main.SUBCOMMANDS
    _validate_artifact_id("clip-out14-push-microarc-stream-v1-999")
