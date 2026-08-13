"""Select and validate reusable editorial-form variants.

This module owns structural selection only.  It does not render media, infer
creative acceptance, or replace the existing form-specific build commands.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

ACTIVITY_CHRONOLOGY_VARIANT_ID = "activity_chronology"
ACTIVITY_CHRONOLOGY_PRIMARY_AXIS = "observable_activity_chronology"
PLAN_SCHEMA_VERSION = "clippipegen.editorial_form_plan.v1"
IR_SCHEMA_VERSION = "clippipegen.editorial_form_ir.v1"
MAX_ORDINARY_BRIDGE_CAPTION_CHARACTERS = 48
MAX_JUSTIFIED_BRIDGE_CAPTION_CHARACTERS = 160
ORDINARY_TEMPORAL_RELATIONS = {
    "same_day",
    "next_day",
    "within_one_week",
    "one_week_later",
}

EDITORIAL_FORM_VARIANTS: dict[str, dict[str, Any]] = {
    "common_context_argument": {
        "variant_id": "common_context_argument",
        "selection_mode": "existing_build_path_unchanged",
        "entry_command": "build-common-context-probe",
        "primary_axis": "evidence_grounded_argument",
    },
    "evidence_linked_comparison": {
        "variant_id": "evidence_linked_comparison",
        "selection_mode": "existing_build_path_unchanged",
        "entry_command": "build-evidence-linked-comparison",
        "primary_axis": "concurrent_evidence_comparison",
    },
    ACTIVITY_CHRONOLOGY_VARIANT_ID: {
        "variant_id": ACTIVITY_CHRONOLOGY_VARIANT_ID,
        "selection_mode": "normalize_and_validate",
        "entry_command": ("select-editorial-form --variant activity_chronology"),
        "primary_axis": ACTIVITY_CHRONOLOGY_PRIMARY_AXIS,
    },
}

ALLOWED_CONNECTION_BASES = {
    "direct_attributable_quote",
    "footage_and_order",
}


class EditorialFormValidationError(ValueError):
    """A structural validation failure with a machine-readable locator."""

    def __init__(self, message: str, *, rule: str, locator: str) -> None:
        super().__init__(message)
        self.rule = rule
        self.locator = locator


def select_editorial_form(variant_id: str) -> dict[str, Any]:
    """Return one explicit family member without introducing a new default."""

    spec = EDITORIAL_FORM_VARIANTS.get(variant_id)
    if spec is None:
        raise EditorialFormValidationError(
            f"unknown editorial form variant: {variant_id or '<empty>'}",
            rule="variant_selection",
            locator="variant_id",
        )
    selection = json.loads(json.dumps(spec))
    selection["family_variant_ids"] = sorted(EDITORIAL_FORM_VARIANTS)
    selection["global_default_changed"] = False
    return selection


def normalize_editorial_form_plan(
    plan: dict[str, Any],
    *,
    variant_id: str,
) -> dict[str, Any]:
    """Validate and normalize a plan for the explicitly selected variant."""

    selection = select_editorial_form(variant_id)
    if variant_id != ACTIVITY_CHRONOLOGY_VARIANT_ID:
        raise EditorialFormValidationError(
            (
                f"{variant_id} keeps its existing entry command "
                f"{selection['entry_command']}"
            ),
            rule="existing_variant_entry_path",
            locator=f"variant:{variant_id}",
        )
    return _normalize_activity_chronology(plan, selection=selection)


def _normalize_activity_chronology(
    plan: dict[str, Any],
    *,
    selection: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise EditorialFormValidationError(
            "editorial form plan must be a JSON object",
            rule="plan_schema",
            locator="plan",
        )
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise EditorialFormValidationError(
            "unsupported editorial form plan schema",
            rule="plan_schema",
            locator="schema_version",
        )
    if plan.get("variant_id") != ACTIVITY_CHRONOLOGY_VARIANT_ID:
        raise EditorialFormValidationError(
            "plan variant_id does not match the explicit selection",
            rule="variant_selection",
            locator="variant_id",
        )
    if plan.get("primary_axis") != ACTIVITY_CHRONOLOGY_PRIMARY_AXIS:
        raise EditorialFormValidationError(
            "activity_chronology requires observable activities as primary axis",
            rule="observable_activity_primary_axis",
            locator="primary_axis",
        )

    units = plan.get("units")
    if not isinstance(units, list) or not units:
        raise EditorialFormValidationError(
            "activity_chronology requires at least one activity unit",
            rule="activity_units",
            locator="units",
        )

    normalized_units: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    previous_timepoint: date | datetime | None = None
    for index, raw_unit in enumerate(units):
        unit_locator = f"units[{index}]"
        unit = _mapping(raw_unit, rule="activity_units", locator=unit_locator)
        unit_id = _text(
            unit.get("unit_id"),
            rule="activity_unit_identity",
            locator=f"{unit_locator}.unit_id",
        )
        if unit_id in seen_ids:
            raise EditorialFormValidationError(
                f"duplicate activity unit id: {unit_id}",
                rule="activity_unit_identity",
                locator=f"unit:{unit_id}",
            )
        seen_ids.add(unit_id)

        topic = unit.get("topic")
        declared_topics = unit.get("topics")
        if not isinstance(topic, str) or not topic.strip():
            raise EditorialFormValidationError(
                f"unit {unit_id} requires one non-empty activity topic",
                rule="one_topic_per_unit",
                locator=f"unit:{unit_id}",
            )
        if declared_topics is not None and (
            not isinstance(declared_topics, list)
            or len(declared_topics) != 1
            or declared_topics[0] != topic
        ):
            raise EditorialFormValidationError(
                f"unit {unit_id} contains more than one activity topic",
                rule="one_topic_per_unit",
                locator=f"unit:{unit_id}",
            )

        source = _mapping(
            unit.get("source"),
            rule="source_attribution",
            locator=f"unit:{unit_id}.source",
        )
        source_id = _text(
            source.get("source_id"),
            rule="source_attribution",
            locator=f"unit:{unit_id}.source.source_id",
        )
        source_locator = _text(
            source.get("source_locator"),
            rule="source_attribution",
            locator=f"unit:{unit_id}/source:{source_id}",
        )
        evidence_locator = f"unit:{unit_id}/source:{source_locator}"
        source_in = _number(
            source.get("source_in"),
            rule="source_time_attribution",
            locator=evidence_locator,
        )
        source_out = _number(
            source.get("source_out"),
            rule="source_time_attribution",
            locator=evidence_locator,
        )
        if source_in < 0 or source_out <= source_in:
            raise EditorialFormValidationError(
                f"unit {unit_id} has an invalid attributed source range",
                rule="source_time_attribution",
                locator=evidence_locator,
            )
        timepoint_text = _text(
            source.get("timepoint"),
            rule="chronological_order",
            locator=evidence_locator,
        )
        timepoint = _parse_timepoint(timepoint_text, locator=evidence_locator)
        if previous_timepoint is not None and _time_sort_key(
            timepoint
        ) < _time_sort_key(previous_timepoint):
            raise EditorialFormValidationError(
                f"unit {unit_id} moves backwards in activity chronology",
                rule="chronological_order",
                locator=evidence_locator,
            )
        previous_timepoint = timepoint

        context = _mapping(
            unit.get("context"),
            rule="contextual_coherence",
            locator=evidence_locator,
        )
        context_in = _number(
            context.get("source_in"),
            rule="contextual_coherence",
            locator=evidence_locator,
        )
        context_out = _number(
            context.get("source_out"),
            rule="contextual_coherence",
            locator=evidence_locator,
        )
        context_basis = _text(
            context.get("basis"),
            rule="contextual_coherence",
            locator=evidence_locator,
        )
        if (
            context_in < 0
            or context_out <= context_in
            or context_in > source_in
            or context_out < source_out
        ):
            raise EditorialFormValidationError(
                f"unit {unit_id} context does not contain its selected source range",
                rule="contextual_coherence",
                locator=evidence_locator,
            )

        source_panels = unit.get("source_panels")
        if source_panels is not None and (
            not isinstance(source_panels, list) or len(source_panels) > 1
        ):
            raise EditorialFormValidationError(
                f"unit {unit_id} cannot manufacture a collage connection",
                rule="single_activity_surface",
                locator=evidence_locator,
            )

        connection_basis = _text(
            unit.get("connection_basis"),
            rule="connection_basis",
            locator=evidence_locator,
        )
        if connection_basis not in ALLOWED_CONNECTION_BASES:
            raise EditorialFormValidationError(
                f"unit {unit_id} has an obscure or subtitle-dependent connection",
                rule="subtitle_cannot_compensate_for_connection",
                locator=evidence_locator,
            )
        if unit.get("subtitle_dependency") is not False:
            raise EditorialFormValidationError(
                f"unit {unit_id} must remain legible without subtitle compensation",
                rule="subtitle_cannot_compensate_for_connection",
                locator=evidence_locator,
            )
        for forbidden_key in ("abstract_growth_connective", "authorial_thesis"):
            if unit.get(forbidden_key):
                raise EditorialFormValidationError(
                    f"unit {unit_id} contains an abstract governing connective",
                    rule="observable_activity_primary_axis",
                    locator=evidence_locator,
                )

        bridge = _normalize_temporal_bridge(
            unit.get("temporal_bridge_from_previous"),
            unit_id=unit_id,
            evidence_locator=evidence_locator,
            is_first=index == 0,
        )
        quote = _normalize_quote(
            unit.get("quote"),
            unit_id=unit_id,
            source_locator=source_locator,
            selected_in=source_in,
            selected_out=source_out,
            evidence_locator=evidence_locator,
        )
        normalized_units.append(
            {
                "unit_id": unit_id,
                "sequence_index": index,
                "topic": topic.strip(),
                "source_attribution": {
                    "source_id": source_id,
                    "source_locator": source_locator,
                    "timepoint": timepoint_text,
                    "selected_range": [source_in, source_out],
                    "context_range": [context_in, context_out],
                    "context_basis": context_basis,
                },
                "connection_basis": connection_basis,
                "subtitle_dependency": False,
                "temporal_bridge_from_previous": bridge,
                "quote": quote,
            }
        )

    return {
        "schema_version": IR_SCHEMA_VERSION,
        "variant_id": ACTIVITY_CHRONOLOGY_VARIANT_ID,
        "selection": selection,
        "primary_axis": ACTIVITY_CHRONOLOGY_PRIMARY_AXIS,
        "structural_policy": {
            "one_topic_per_unit": True,
            "source_and_time_attribution_retained": True,
            "contextual_coherence_retained": True,
            "footage_and_order_first": True,
            "ordinary_temporal_bridge_caption_max_characters": (
                MAX_ORDINARY_BRIDGE_CAPTION_CHARACTERS
            ),
            "subtitles_may_compensate_for_obscure_connection": False,
            "abstract_growth_primary_axis_allowed": False,
            "simultaneous_collage_connection_allowed": False,
        },
        "units": normalized_units,
        "capability_boundaries": {
            "human_creative_acceptance": False,
            "production_readiness": False,
            "rights_clearance": False,
            "publication_or_upload": False,
        },
    }


def _normalize_temporal_bridge(
    value: Any,
    *,
    unit_id: str,
    evidence_locator: str,
    is_first: bool,
) -> dict[str, Any] | None:
    if value is None:
        return None
    bridge = _mapping(
        value,
        rule="temporal_bridge",
        locator=evidence_locator,
    )
    if is_first:
        raise EditorialFormValidationError(
            f"first activity unit {unit_id} cannot bridge from a previous unit",
            rule="temporal_bridge",
            locator=evidence_locator,
        )
    relation = _text(
        bridge.get("relation"),
        rule="temporal_bridge",
        locator=evidence_locator,
    )
    caption_value = bridge.get("caption")
    caption = (
        ""
        if caption_value is None
        else _text(
            caption_value,
            rule="temporal_bridge",
            locator=evidence_locator,
        )
    )
    captions = bridge.get("captions")
    if captions is not None and (
        not isinstance(captions, list)
        or len(captions) > 1
        or (captions and captions[0] != caption)
    ):
        raise EditorialFormValidationError(
            f"unit {unit_id} has more than one temporal explanatory caption",
            rule="ordinary_temporal_bridge_limit",
            locator=evidence_locator,
        )
    justification_value = bridge.get("structural_justification")
    if justification_value is not None and not isinstance(justification_value, str):
        raise EditorialFormValidationError(
            f"unit {unit_id} has an invalid temporal structural justification",
            rule="ordinary_temporal_bridge_limit",
            locator=evidence_locator,
        )
    justification = str(justification_value or "").strip() or None
    if relation not in ORDINARY_TEMPORAL_RELATIONS and justification is None:
        raise EditorialFormValidationError(
            f"unit {unit_id} temporal relation exceeds the ordinary one-week bridge",
            rule="ordinary_temporal_bridge_limit",
            locator=evidence_locator,
        )
    limit = (
        MAX_JUSTIFIED_BRIDGE_CAPTION_CHARACTERS
        if justification
        else MAX_ORDINARY_BRIDGE_CAPTION_CHARACTERS
    )
    if len(caption) > limit:
        suffix = " even with its structural justification" if justification else ""
        raise EditorialFormValidationError(
            f"unit {unit_id} temporal caption is overlong{suffix}",
            rule="ordinary_temporal_bridge_limit",
            locator=evidence_locator,
        )
    return {
        "relation": relation,
        "caption": caption or None,
        "structural_justification": justification,
    }


def _normalize_quote(
    value: Any,
    *,
    unit_id: str,
    source_locator: str,
    selected_in: float,
    selected_out: float,
    evidence_locator: str,
) -> dict[str, Any] | None:
    if value is None:
        return None
    quote = _mapping(
        value,
        rule="quote_attribution",
        locator=evidence_locator,
    )
    text = _text(
        quote.get("text"),
        rule="quote_attribution",
        locator=evidence_locator,
    )
    attribution = _text(
        quote.get("attribution"),
        rule="quote_attribution",
        locator=evidence_locator,
    )
    quote_in = _number(
        quote.get("source_in"),
        rule="quote_attribution",
        locator=evidence_locator,
    )
    quote_out = _number(
        quote.get("source_out"),
        rule="quote_attribution",
        locator=evidence_locator,
    )
    bound_locator = quote.get("source_locator", source_locator)
    if (
        bound_locator != source_locator
        or quote_in < selected_in
        or quote_out > selected_out
        or quote_out <= quote_in
    ):
        raise EditorialFormValidationError(
            f"unit {unit_id} quote is outside its attributed activity evidence",
            rule="quote_attribution",
            locator=evidence_locator,
        )
    return {
        "text": text,
        "attribution": attribution,
        "source_locator": source_locator,
        "source_range": [quote_in, quote_out],
    }


def _mapping(value: Any, *, rule: str, locator: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EditorialFormValidationError(
            "expected an object",
            rule=rule,
            locator=locator,
        )
    return value


def _text(value: Any, *, rule: str, locator: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EditorialFormValidationError(
            "expected non-empty text",
            rule=rule,
            locator=locator,
        )
    return value.strip()


def _number(value: Any, *, rule: str, locator: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EditorialFormValidationError(
            "expected a numeric source time",
            rule=rule,
            locator=locator,
        )
    return float(value)


def _parse_timepoint(value: str, *, locator: str) -> date | datetime:
    try:
        if "T" in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return date.fromisoformat(value)
    except ValueError as exc:
        raise EditorialFormValidationError(
            "timepoint must be an ISO date or datetime",
            rule="chronological_order",
            locator=locator,
        ) from exc


def _time_sort_key(value: date | datetime) -> str:
    return value.isoformat()
