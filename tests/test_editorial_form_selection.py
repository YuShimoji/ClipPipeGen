from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.cli import build_common_context_probe, build_evidence_linked_comparison
from src.cli import main as cli_main
from src.pipeline import editorial_form_selection as forms


def _activity_plan() -> dict:
    return {
        "schema_version": forms.PLAN_SCHEMA_VERSION,
        "variant_id": forms.ACTIVITY_CHRONOLOGY_VARIANT_ID,
        "primary_axis": forms.ACTIVITY_CHRONOLOGY_PRIMARY_AXIS,
        "units": [
            {
                "unit_id": "activity_001",
                "topic": "配信で作品を初めて読む",
                "source": {
                    "source_id": "stream_alpha",
                    "source_locator": "youtube:fixture-alpha",
                    "source_in": 10.0,
                    "source_out": 20.0,
                    "timepoint": "2026-08-01",
                },
                "context": {
                    "source_in": 8.0,
                    "source_out": 22.0,
                    "basis": "continuous_source_excerpt",
                },
                "connection_basis": "footage_and_order",
                "subtitle_dependency": False,
                "quote": {
                    "text": "初めて読んだ。",
                    "attribution": "Fixture Channel Alpha",
                    "source_locator": "youtube:fixture-alpha",
                    "source_in": 14.0,
                    "source_out": 16.0,
                },
            },
            {
                "unit_id": "activity_002",
                "topic": "後日の配信で続きを読み返す",
                "source": {
                    "source_id": "stream_beta",
                    "source_locator": "youtube:fixture-beta",
                    "source_in": 30.0,
                    "source_out": 42.0,
                    "timepoint": "2026-08-08",
                },
                "context": {
                    "source_in": 27.0,
                    "source_out": 45.0,
                    "basis": "continuous_source_excerpt",
                },
                "connection_basis": "direct_attributable_quote",
                "subtitle_dependency": False,
                "temporal_bridge_from_previous": {
                    "relation": "one_week_later",
                    "caption": "一週間後、続きを読み返す",
                },
                "quote": {
                    "text": "続きを読み返した。",
                    "attribution": "Fixture Channel Beta",
                    "source_in": 34.0,
                    "source_out": 37.0,
                },
            },
        ],
    }


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_variant_registry_is_plural_and_has_explicit_activity_identifier() -> None:
    assert forms.ACTIVITY_CHRONOLOGY_VARIANT_ID == "activity_chronology"
    assert set(forms.EDITORIAL_FORM_VARIANTS) == {
        "activity_chronology",
        "common_context_argument",
        "evidence_linked_comparison",
    }
    selection = forms.select_editorial_form("activity_chronology")
    assert selection["global_default_changed"] is False
    assert selection["primary_axis"] == "observable_activity_chronology"


def test_real_cli_selection_serializes_source_and_time_attributed_ir(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path = tmp_path / "activity_plan.json"
    output_path = tmp_path / "normalized_ir.json"
    _write_json(plan_path, _activity_plan())

    result = cli_main.main(
        [
            "select-editorial-form",
            "--variant",
            "activity_chronology",
            "--plan",
            str(plan_path),
            "--output",
            str(output_path),
            "--format",
            "json",
        ]
    )

    assert result == 0
    cli_readback = json.loads(capsys.readouterr().out)
    assert cli_readback["status"] == "normalized"
    assert cli_readback["unit_count"] == 2
    normalized = json.loads(output_path.read_text(encoding="utf-8"))
    assert normalized["variant_id"] == "activity_chronology"
    assert normalized["primary_axis"] == "observable_activity_chronology"
    assert normalized["units"][1]["source_attribution"] == {
        "context_basis": "continuous_source_excerpt",
        "context_range": [27.0, 45.0],
        "selected_range": [30.0, 42.0],
        "source_id": "stream_beta",
        "source_locator": "youtube:fixture-beta",
        "timepoint": "2026-08-08",
    }
    assert normalized["units"][1]["quote"]["source_range"] == [34.0, 37.0]
    assert normalized["capability_boundaries"]["human_creative_acceptance"] is False


def test_multi_topic_unit_identifies_structural_rule_and_unit() -> None:
    plan = _activity_plan()
    plan["units"][1]["topics"] = [
        "後日の配信で続きを読み返す",
        "別企画を振り返る",
    ]
    with pytest.raises(forms.EditorialFormValidationError) as caught:
        forms.normalize_editorial_form_plan(
            plan,
            variant_id="activity_chronology",
        )
    assert caught.value.rule == "one_topic_per_unit"
    assert caught.value.locator == "unit:activity_002"


def test_abstract_growth_primary_axis_is_not_admitted() -> None:
    plan = _activity_plan()
    plan["primary_axis"] = "personal_growth_and_changing_ideas"
    with pytest.raises(forms.EditorialFormValidationError) as caught:
        forms.normalize_editorial_form_plan(
            plan,
            variant_id="activity_chronology",
        )
    assert caught.value.rule == "observable_activity_primary_axis"
    assert caught.value.locator == "primary_axis"


def test_overlong_ordinary_temporal_connection_needs_structure() -> None:
    plan = _activity_plan()
    plan["units"][1]["temporal_bridge_from_previous"]["caption"] = "長" * 49
    with pytest.raises(forms.EditorialFormValidationError) as caught:
        forms.normalize_editorial_form_plan(
            plan,
            variant_id="activity_chronology",
        )
    assert caught.value.rule == "ordinary_temporal_bridge_limit"
    assert caught.value.locator == ("unit:activity_002/source:youtube:fixture-beta")


def test_beyond_one_week_relation_needs_structure() -> None:
    plan = _activity_plan()
    plan["units"][1]["temporal_bridge_from_previous"]["relation"] = "one_month_later"
    with pytest.raises(forms.EditorialFormValidationError) as caught:
        forms.normalize_editorial_form_plan(
            plan,
            variant_id="activity_chronology",
        )
    assert caught.value.rule == "ordinary_temporal_bridge_limit"
    assert caught.value.locator == ("unit:activity_002/source:youtube:fixture-beta")


def test_structurally_justified_temporal_exception_is_explicit() -> None:
    plan = _activity_plan()
    bridge = plan["units"][1]["temporal_bridge_from_previous"]
    bridge["caption"] = "長" * 60
    bridge["structural_justification"] = (
        "source chronology cannot otherwise expose the documented hiatus"
    )
    normalized = forms.normalize_editorial_form_plan(
        plan,
        variant_id="activity_chronology",
    )
    assert normalized["units"][1]["temporal_bridge_from_previous"] == {
        "caption": "長" * 60,
        "relation": "one_week_later",
        "structural_justification": (
            "source chronology cannot otherwise expose the documented hiatus"
        ),
    }


def test_subtitle_only_connection_reports_source_locator() -> None:
    plan = _activity_plan()
    plan["units"][1]["connection_basis"] = "subtitle_only"
    plan["units"][1]["subtitle_dependency"] = True
    with pytest.raises(forms.EditorialFormValidationError) as caught:
        forms.normalize_editorial_form_plan(
            plan,
            variant_id="activity_chronology",
        )
    assert caught.value.rule == "subtitle_cannot_compensate_for_connection"
    assert caught.value.locator == ("unit:activity_002/source:youtube:fixture-beta")


def test_cli_failure_names_rule_and_locator_without_creative_verdict(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan = _activity_plan()
    plan["units"][1]["topics"] = ["topic one", "topic two"]
    plan_path = tmp_path / "invalid.json"
    _write_json(plan_path, plan)

    result = cli_main.main(
        [
            "select-editorial-form",
            "--variant",
            "activity_chronology",
            "--plan",
            str(plan_path),
            "--output",
            str(tmp_path / "ir.json"),
        ]
    )

    assert result == 2
    error = capsys.readouterr().err
    assert "rule=one_topic_per_unit" in error
    assert "locator=unit:activity_002" in error
    assert "creative rejection" not in error.lower()


def test_existing_non_activity_paths_remain_selectable_and_unchanged(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli_main.SUBCOMMANDS["build-evidence-linked-comparison"] is (
        build_evidence_linked_comparison.run
    )
    assert cli_main.SUBCOMMANDS["build-common-context-probe"] is (
        build_common_context_probe.run
    )
    assert "select-editorial-form" in cli_main.SUBCOMMANDS

    result = cli_main.main(
        [
            "select-editorial-form",
            "--variant",
            "evidence_linked_comparison",
            "--format",
            "json",
        ]
    )
    assert result == 0
    readback = json.loads(capsys.readouterr().out)
    assert readback["status"] == "existing_entry_path_preserved"
    assert readback["selection"]["entry_command"] == (
        "build-evidence-linked-comparison"
    )
    assert readback["selection"]["global_default_changed"] is False


def test_unsupported_schema_is_a_schema_failure() -> None:
    plan = copy.deepcopy(_activity_plan())
    plan["schema_version"] = "clippipegen.editorial_form_plan.v999"
    with pytest.raises(forms.EditorialFormValidationError) as caught:
        forms.normalize_editorial_form_plan(
            plan,
            variant_id="activity_chronology",
        )
    assert caught.value.rule == "plan_schema"
    assert caught.value.locator == "schema_version"
