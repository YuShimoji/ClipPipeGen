import json
from pathlib import Path

from tools.benchmarks.build_benchmark_portfolio import TIERS, build


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_registry_denominator_and_output_family_coverage() -> None:
    registry = json.loads((REPO_ROOT / "docs/benchmarks/benchmark_registry.json").read_text(encoding="utf-8"))
    candidates = [candidate for family in registry["families"] for candidate in family["candidates"]]
    assert len(registry["families"]) == 15
    assert len(candidates) == 27
    assert len({family["family_id"] for family in registry["families"]}) == 15
    assert len({candidate["candidate_id"] for candidate in candidates}) == 27
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
    assert portfolio["candidate_denominator"] == 27
    assert portfolio["materialized_candidate_cards"] == 27
    assert portfolio["all_registered_candidates_materialized"] is True
    assert sum(portfolio["coverage_by_tier"].values()) == 27
    assert portfolio["coverage_by_tier"] == {
        "contract-only": 0,
        "static-reviewable": 5,
        "playable-proxy": 2,
        "fully-viewable": 20,
    }
    cards = list((tmp_path / "candidates").glob("*.html"))
    assert len(cards) == 27
    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "benchmark_portfolio.json").is_file()
    assert (tmp_path / "COVERAGE_LEDGER.md").is_file()
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "15 family / 27" in index
    assert "権利・production・公開・収益化・upload 承認は推定しません" in index
    wiki_002 = (tmp_path / "candidates/wiki-002.html").read_text(encoding="utf-8")
    assert "static-reviewable" in wiki_002
    assert "Do not retry cookies or OAuth" in wiki_002
    wiki_003 = (tmp_path / "candidates/wiki-003.html").read_text(encoding="utf-8")
    assert "candidate_specific_static_inputs_ready_no_network" in wiki_003
    assert "zero network requests" in wiki_003
    assert "Create candidate-specific 12-chapter inputs" not in wiki_003


def test_checked_in_portfolio_matches_registry_and_keeps_episodes_untracked() -> None:
    portfolio = json.loads((REPO_ROOT / "docs/benchmarks/benchmark_portfolio.json").read_text(encoding="utf-8"))
    assert portfolio["family_denominator"] == 15
    assert portfolio["candidate_denominator"] == 27
    assert portfolio["all_registered_candidates_materialized"] is True
    assert portfolio["rights_publication_approval_inferred"] is False
    assert portfolio["episodes_paths_tracked_by_this_artifact"] is False
    assert len(list((REPO_ROOT / "docs/benchmarks/candidates").glob("*.html"))) == 27


def test_runtime_and_handoff_route_to_the_portfolio_without_erasing_parked_gates() -> None:
    runtime = (REPO_ROOT / "docs/RUNTIME_STATE.md").read_text(encoding="utf-8")
    handoff = (REPO_ROOT / "docs/CURRENT_HANDOFF.md").read_text(encoding="utf-8")
    for document in (runtime, handoff):
        assert "current_slice: SH-05" in document
        assert "active_artifact: clip-benchmark-portfolio-coverage-v1-001" in document
        assert "benchmark_family_denominator: 15" in document
        assert "benchmark_candidate_slot_denominator: 27" in document
        assert "benchmark_fully_viewable_count: 20" in document
        assert "benchmark_playable_proxy_count: 2" in document
        assert "benchmark_static_reviewable_count: 5" in document
        assert "wiki_second_external_state: BLOCKED_EXTERNAL" in document
        assert "s1_lane_status: parked_human_review_pending" in document
