import json
from pathlib import Path

from tools.benchmarks.build_benchmark_portfolio import TIERS, build


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_registry_denominator_and_output_family_coverage() -> None:
    registry = json.loads((REPO_ROOT / "docs/benchmarks/benchmark_registry.json").read_text(encoding="utf-8"))
    candidates = [candidate for family in registry["families"] for candidate in family["candidates"]]
    assert len(registry["families"]) == 15
    assert len(candidates) == 30
    assert len({family["family_id"] for family in registry["families"]}) == 15
    assert len({candidate["candidate_id"] for candidate in candidates}) == 30
    assert set(registry["tiers"]) == set(TIERS)
    actual_contracts = {family["contract_path"] for family in registry["families"]}
    assert "docs/output_layer/WIKI_TENSAKU_LONGFORM_FAMILY.md" in actual_contracts
    assert "docs/output_layer/S1_TWO_SOURCE_COMMON_CONTEXT_PROBE.md" in actual_contracts
    for number in range(1, 14):
        assert any(path.startswith(f"docs/output_layer/OUT_{number:02d}_") for path in actual_contracts)
    assert all(candidate["boundary"] for candidate in candidates)
    assert all(candidate["missing_upgrade_condition"] for candidate in candidates)


def test_builder_materializes_every_candidate_card(tmp_path: Path) -> None:
    portfolio = build(
        repo_root=REPO_ROOT,
        registry_path=REPO_ROOT / "docs/benchmarks/benchmark_registry.json",
        output_dir=tmp_path,
        observed_at="2026-08-04T12:00:00+09:00",
        hash_local_media=False,
    )
    assert portfolio["family_denominator"] == 15
    assert portfolio["candidate_denominator"] == 30
    assert portfolio["materialized_candidate_cards"] == 30
    assert portfolio["all_registered_candidates_materialized"] is True
    assert sum(portfolio["coverage_by_tier"].values()) == 30
    assert portfolio["coverage_by_tier"] == {
        "contract-only": 0,
        "static-reviewable": 5,
        "playable-proxy": 2,
        "fully-viewable": 23,
    }
    cards = list((tmp_path / "candidates").glob("*.html"))
    assert len(cards) == 30
    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "benchmark_portfolio.json").is_file()
    assert (tmp_path / "COVERAGE_LEDGER.md").is_file()
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "15 family / 30" in index
    assert "権利・production・公開・収益化・upload 承認は推定しません" in index
    wiki_002 = (tmp_path / "candidates/wiki-002.html").read_text(encoding="utf-8")
    assert "static-reviewable" in wiki_002
    assert "Do not retry cookies or OAuth" in wiki_002
    wiki_003 = (tmp_path / "candidates/wiki-003.html").read_text(encoding="utf-8")
    assert "candidate_specific_static_inputs_ready_no_network" in wiki_003
    assert "zero network requests" in wiki_003
    assert "Create candidate-specific 12-chapter inputs" not in wiki_003
    wiki_turn = (tmp_path / "candidates/wiki-turn-001.html").read_text(encoding="utf-8")
    assert "verified_13_of_13_correction_led_internal" in wiki_turn
    assert "fully-viewable" in wiki_turn
    assert "without network requests" in wiki_turn
    wiki_turn_2 = (tmp_path / "candidates/wiki-turn-002.html").read_text(encoding="utf-8")
    assert "verified_13_of_13_uncovered_correction_led_internal" in wiki_turn_2
    assert "zero overlap" in wiki_turn_2
    wiki_turn_3 = (tmp_path / "candidates/wiki-turn-003.html").read_text(encoding="utf-8")
    assert "verified_13_of_13_third_uncovered_correction_led_internal" in wiki_turn_3
    assert "slot 6" in wiki_turn_3


def test_checked_in_portfolio_matches_registry_and_keeps_episodes_untracked() -> None:
    portfolio = json.loads((REPO_ROOT / "docs/benchmarks/benchmark_portfolio.json").read_text(encoding="utf-8"))
    assert portfolio["family_denominator"] == 15
    assert portfolio["candidate_denominator"] == 30
    assert portfolio["all_registered_candidates_materialized"] is True
    assert portfolio["rights_publication_approval_inferred"] is False
    assert portfolio["episodes_paths_tracked_by_this_artifact"] is False
    assert len(list((REPO_ROOT / "docs/benchmarks/candidates").glob("*.html"))) == 30


def test_runtime_and_handoff_route_to_the_portfolio_without_erasing_parked_gates() -> None:
    runtime = (REPO_ROOT / "docs/RUNTIME_STATE.md").read_text(encoding="utf-8")
    handoff = (REPO_ROOT / "docs/CURRENT_HANDOFF.md").read_text(encoding="utf-8")
    for document in (runtime, handoff):
        assert "current_slice: SH-05" in document
        assert "active_artifact: clip-benchmark-portfolio-coverage-v1-001" in document
        assert "benchmark_family_denominator: 15" in document
        assert "benchmark_candidate_slot_denominator: 30" in document
        assert "benchmark_fully_viewable_count: 23" in document
        assert "benchmark_playable_proxy_count: 2" in document
        assert "benchmark_static_reviewable_count: 5" in document
        assert "wiki_second_external_state: BLOCKED_EXTERNAL" in document
        assert "wiki_third_artifact_id: clip-wiki-tensaku-longform-v1-003" in document
        assert "wiki_third_input_contract_validation: passed" in document
        assert "wiki_third_network_requests_performed: 0" in document
        assert "wiki_third_external_state: WAITING_EXACT_SOURCE_BYTES" in document
        assert "wiki_family_turn_artifact_id: clip-wiki-tensaku-family-turn-v1-001" in document
        assert "wiki_family_turn_validation: passed_13_of_13" in document
        assert "wiki_family_turn_network_requests_performed: 0" in document
        assert "wiki_family_turn_two_artifact_id: clip-wiki-tensaku-family-turn-v2-001" in document
        assert "wiki_family_turn_two_excluded_source_overlap_seconds: 0" in document
        assert "wiki_family_turn_three_artifact_id: clip-wiki-tensaku-family-turn-v3-001" in document
        assert "wiki_family_turn_three_excluded_source_overlap_seconds: 0" in document
        assert "s1_lane_status: parked_human_review_pending" in document
