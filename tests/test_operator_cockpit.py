from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.operator_cockpit import OperatorCockpitError, build_operator_cockpit


REPO_ROOT = Path(__file__).resolve().parent.parent
CPD_DIR = REPO_ROOT / "docs" / "content_planning"


def build_cockpit(tmp_path: Path):
    return build_operator_cockpit(
        candidates_path=CPD_DIR / "content_candidates.json",
        seed_path=CPD_DIR / "episode_seed_drafts.json",
        source_resolution_path=CPD_DIR / "episode_seed_source_resolution.json",
        episode_init_plan_path=CPD_DIR / "episode_init_plan.json",
        source_inspection_packet_path=CPD_DIR / "source_inspection_packet.json",
        decision_template_path=CPD_DIR / "source_inspection_decisions.template.json",
        output_path=tmp_path / "operator_cockpit.json",
        dashboard_path=tmp_path / "operator_cockpit.html",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )


def test_operator_cockpit_builds_briefing_board_and_preserves_boundaries(tmp_path: Path):
    result = build_cockpit(tmp_path)

    payload = json.loads(result["output_path"].read_text(encoding="utf-8"))
    html = result["dashboard_path"].read_text(encoding="utf-8")

    assert payload["schema_id"] == "clippipegen.operator_cockpit.v0"
    assert payload["title"] == "ClipPipeGen Operator Cockpit / Content Planning Review"
    assert payload["artifact_id"] == "clip-cpd10-candidate-ledger-readability-v0-001"
    assert payload["ux"]["version"] == "v5_ledger_readability_v0"
    assert payload["ux"]["layout"] == "operator_briefing_board_ledger_readability"
    assert payload["ux"]["default_theme"] == "dark"
    assert payload["ux"]["theme_toggle"] is True
    assert payload["ux"]["briefing_board"] == "visible"
    assert payload["ux"]["annotated_flow"] == "visible"
    assert payload["ux"]["candidate_ledger"] == "responsive_stacked"
    assert payload["ux"]["ledger_layout"] == "responsive_ledger_stacked"
    assert payload["ux"]["title_wrapping_guard"] is True
    assert payload["ux"]["id_wrapping_scope"] == "code_strip_only"
    assert payload["ux"]["usage_frequency_ia"] is True
    assert payload["ux"]["developer_appendix_default"] == "collapsed"

    summary = payload["summary"]
    assert summary["total_candidates"] == 5
    assert summary["total_seed_drafts"] == 5
    assert summary["source_url_present_count"] == 1
    assert summary["source_backed_count"] == 1
    assert summary["source_missing_count"] == 4
    assert summary["source_missing_idea_backlog_count"] == 3
    assert summary["blocked_or_hold_count"] == 1
    assert summary["inspectable_packet_count"] == 1
    assert summary["decision_template_entry_count"] == 1
    assert summary["fetch_authorized_count"] == 0
    assert summary["media_downloaded"] is False
    assert summary["episode_dirs_created"] is False
    assert summary["health"] == "ready_for_single_source_identity_review"
    assert payload["recommended_next_action"]["action_id"] == "inspect_single_source_backed_item"
    assert payload["recommended_next_action"]["user_work"] == "open_only"

    briefing = payload["briefing"]
    assert briefing["briefing_id"] == "cpd10_operator_briefing"
    assert briefing["primary_action"]["href"] == "#primary-review"
    assert briefing["primary_action"]["state"] == "human_review_waiting"
    assert briefing["flow_stage_count"] == 5
    assert "fetch / download / transcript / render / upload / rights approval" in briefing["locked_line"]

    assert [stage["stage_id"] for stage in payload["annotated_flow"]] == [
        "ideas",
        "source_backed",
        "human_review_waiting",
        "private_local_review",
        "edit_render_public",
    ]
    assert [stage["count"] for stage in payload["annotated_flow"]] == [5, 1, 1, 0, 0]
    assert payload["annotated_flow"][1]["href"] == "#primary-review"
    assert payload["annotated_flow"][2]["is_bottleneck"] is True
    assert payload["annotated_flow"][3]["status"] == "locked"

    assert [item["frequency"] for item in payload["usage_frequency_sections"]] == [
        "常用",
        "常用",
        "必要時",
        "開発用",
    ]
    assert payload["usage_frequency_sections"][2]["section_id"] == "candidate-ledger"
    ledger_by_id = {item["candidate_id"]: item for item in payload["candidate_ledger"]}
    assert len(ledger_by_id) == 5
    assert ledger_by_id["cpd01_bancho_marine_misunderstanding"]["video_backed"] is True
    assert ledger_by_id["cpd01_bancho_marine_misunderstanding"]["href"] == "#primary-review"
    assert ledger_by_id["cpd01_bancho_marine_misunderstanding"]["source_state_label"] == "URLあり・同一性未確認"
    assert ledger_by_id["cpd01_bancho_marine_misunderstanding"]["review_state_label"] == "人間確認待ち"
    assert ledger_by_id["cpd01_jp_en_phrase_gap"]["ledger_group"] == "source_missing"
    assert ledger_by_id["cpd01_jp_en_phrase_gap"]["video_backed"] is False
    assert ledger_by_id["cpd01_jp_en_phrase_gap"]["review_state"] == "not_reviewable_as_video"
    assert ledger_by_id["cpd01_jp_en_phrase_gap"]["review_state_label"] == "動画候補として未確認"
    assert ledger_by_id["cpd01_jp_en_phrase_gap"]["operator_use_label"] == "URL入力待ち"
    assert ledger_by_id["cpd01_song_moment_hold"]["ledger_group"] == "blocked_hold"
    assert ledger_by_id["cpd01_song_moment_hold"]["operator_use_label"] == "権利routeなしでは進めない"

    assert payload["action_script"]["script_id"] == "single_source_identity_check"
    assert payload["action_script"]["source_url"] == "https://www.youtube.com/watch?v=7J5aS_pcBj4"
    assert payload["action_script"]["visual_choices"][0]["label"] == "OK"
    assert all(marker["marker"] == "[ ]" for marker in payload["action_script"]["unverified_markers"])
    assert {item["section_id"] for item in payload["section_links"]} >= {
        "briefing-board",
        "primary-review",
        "candidate-ledger",
        "source-missing",
        "blocked-hold",
        "safety-boundary",
        "developer-appendix",
    }

    gates = payload["gate_readback"]
    assert gates["source_opened_by_worker"] is False
    assert gates["network_required"] is False
    assert gates["external_api_used"] is False
    assert gates["media_downloaded"] is False
    assert gates["episode_dirs_created"] is False
    assert gates["fetch_authorized"] is False
    assert gates["rights_approved"] is False
    assert gates["production_ready"] is False
    assert gates["public_ready"] is False
    assert gates["transcript_generated"] is False
    assert gates["render_generated"] is False

    source_backed = payload["buckets"]["source_backed_ready_for_human_inspection"]
    assert len(source_backed) == 1
    ready = source_backed[0]
    assert ready["candidate_id"] == "cpd01_bancho_marine_misunderstanding"
    assert ready["seed_id"] == "seed_cpd01_bancho_marine_misunderstanding"
    assert ready["source_url"] == "https://www.youtube.com/watch?v=7J5aS_pcBj4"
    assert ready["video_id"] == "7J5aS_pcBj4"
    assert ready["source_grounding_status"] == "source_url_present_but_identity_unchecked_by_worker"
    assert ready["source_open_state"] == "not_opened_by_worker"
    assert ready["decision_state"] == "pending"
    assert ready["human_action"] == "open_source_url_and_check_identity"
    assert ready["not_yet"] == ["fetch", "transcript", "render", "public", "rights"]
    assert ready["fetch_authorized"] is False
    assert ready["rights_status"] == "pending"
    assert ready["rights_approved"] is False
    assert ready["production_ready"] is False
    assert ready["public_ready"] is False

    backlog = payload["buckets"]["source_missing_idea_backlog"]
    backlog_by_id = {item["candidate_id"]: item for item in backlog}
    assert set(backlog_by_id) == {
        "cpd01_jp_en_phrase_gap",
        "cpd01_reaction_face_chain",
        "cpd01_game_fail_micro_arc",
    }
    phrase_gap = backlog_by_id["cpd01_jp_en_phrase_gap"]
    assert phrase_gap["source_url_state"] == "missing"
    assert phrase_gap["grounding_status"] == "not_grounded_to_source"
    assert phrase_gap["warning"] == "do_not_treat_as_video-backed_candidate"
    assert "source_url" in phrase_gap["required_before_progress"]
    assert "manual_topic_seed: JP/EN phrase gap" in phrase_gap["idea_basis"]

    blocked = payload["buckets"]["blocked_or_hold"]
    assert [item["candidate_id"] for item in blocked] == ["cpd01_song_moment_hold"]
    assert blocked[0]["reason"] == "song_or_music_rights_sensitive"
    assert blocked[0]["grounding_status"] == "not_grounded_to_source"
    assert blocked[0]["warning"] == "do_not_treat_as_video-backed_candidate"
    assert all(item["open_by_default"] is False for item in payload["buckets"]["internal_pipeline_artifact_only"])

    assert "ClipPipeGen Operator Cockpit / Content Planning Review" in html
    assert 'data-theme="dark"' in html
    assert "--bg:" in html
    assert "--surface:" in html
    assert "toggleOperatorTheme" in html
    assert "localStorage" in html
    assert 'id="theme-toggle"' in html
    assert "Briefing Board / Usage-Frequency IA v0" in html
    assert 'id="briefing-board"' in html
    assert "常用 / Briefing Board" in html
    assert "annotated flow" in html
    assert "Primary Review Script" in html
    assert 'id="candidate-ledger"' in html
    assert "Candidate Ledger" in html
    assert 'href="#primary-review"' in html
    assert 'href="#source-missing"' in html
    assert 'href="#blocked-hold"' in html
    assert 'id="primary-review"' in html
    assert 'id="primary-review-card"' in html
    assert 'id="source-missing"' in html
    assert 'id="blocked-hold"' in html
    assert 'id="safety-boundary"' in html
    assert 'id="developer-appendix"' in html
    assert "not video-backed" in html
    assert "cpd01_jp_en_phrase_gap" in html
    assert "番長、船長を完全に勘違いする" in html
    assert "日本語の一言で EN 組が固まる" in html
    assert "表情が一瞬で変わるホロメン" in html
    assert "失敗したのに立て直しが早すぎる" in html
    assert "歌の合間に急に本音が出る" in html
    assert "URLあり・同一性未確認" in html
    assert "動画候補として未確認" in html
    assert "権利routeなしでは進めない" in html
    assert "do_not_treat_as_video-backed_candidate" not in html
    assert "checkmark" not in html
    assert "✓" not in html
    assert "Operator Home / Funnel Meters v0" not in html
    assert 'id="operator-home"' not in html
    assert "Action Queue" not in html
    assert 'id="action-queue"' not in html
    assert "meter-grid" not in html
    assert "queue-grid" not in html
    assert "content_dashboard.html" in html
    assert "source_inspection_packet_dashboard.html" in html
    assert "artifact_id:" not in html[: html.index('id="developer-appendix"')]

    ledger_area = html[html.index('id="candidate-ledger"') : html.index('id="safety-boundary"')]
    assert '<table class="ledger-table">' not in ledger_area
    assert "<table>" not in ledger_area
    assert 'class="ledger-list"' in ledger_area
    assert ledger_area.count('class="ledger-item') == 5
    assert 'class="ledger-title"' in ledger_area
    assert 'class="code-strip"' in ledger_area
    assert "source_url_present_identity_unchecked" not in ledger_area
    assert "human_review_pending" not in ledger_area
    assert "source_url_intake_backlog" not in ledger_area
    assert "word-break:break-all" in html
    assert ".code-strip code" in html
    assert ".ledger-title" in html
    assert ".ledger-title{font-size:18px;line-height:1.48;letter-spacing:0;word-break:normal;overflow-wrap:normal" in html

    briefing_area = html[html.index('id="briefing-board"') : html.index('id="primary-review"')]
    assert "<table>" not in briefing_area
    assert html.index('id="briefing-board"') < html.index('id="primary-review"')
    assert html.index('id="primary-review"') < html.index('id="candidate-ledger"')
    assert html.index('id="candidate-ledger"') < html.index('id="safety-boundary"')
    assert html.index('id="safety-boundary"') < html.index('id="developer-appendix"')
    assert "<details open" not in html
    assert not (tmp_path / "episodes").exists()


def test_operator_cockpit_rejects_missing_required_arrays(tmp_path: Path):
    bad_candidates = tmp_path / "content_candidates.json"
    bad_candidates.write_text('{"schema_id":"bad"}', encoding="utf-8")

    with pytest.raises(OperatorCockpitError, match="candidates"):
        build_operator_cockpit(
            candidates_path=bad_candidates,
            seed_path=CPD_DIR / "episode_seed_drafts.json",
            source_resolution_path=CPD_DIR / "episode_seed_source_resolution.json",
            episode_init_plan_path=CPD_DIR / "episode_init_plan.json",
            source_inspection_packet_path=CPD_DIR / "source_inspection_packet.json",
            decision_template_path=CPD_DIR / "source_inspection_decisions.template.json",
            output_path=tmp_path / "operator_cockpit.json",
            dashboard_path=tmp_path / "operator_cockpit.html",
            base_dir=REPO_ROOT,
            generated_at="test-run",
        )


def test_build_operator_cockpit_cli_writes_outputs(tmp_path: Path):
    output_path = tmp_path / "operator_cockpit.json"
    dashboard_path = tmp_path / "operator_cockpit.html"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-operator-cockpit",
            "--output",
            str(output_path),
            "--dashboard",
            str(dashboard_path),
            "--generated-at",
            "test-run",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["artifact_id"] == "clip-cpd10-candidate-ledger-readability-v0-001"
    assert payload["total_candidates"] == 5
    assert payload["source_backed_count"] == 1
    assert payload["source_missing_count"] == 4
    assert payload["source_missing_idea_backlog_count"] == 3
    assert payload["blocked_or_hold_count"] == 1
    assert payload["briefing_present"] is True
    assert payload["ux_version"] == "v5_ledger_readability_v0"
    assert payload["ledger_layout"] == "responsive_ledger_stacked"
    assert payload["title_wrapping_guard"] is True
    assert payload["annotated_flow_stage_count"] == 5
    assert payload["usage_frequency_section_count"] == 4
    assert payload["candidate_ledger_row_count"] == 5
    assert payload["action_script_id"] == "single_source_identity_check"
    assert payload["recommended_next_action"] == "inspect_single_source_backed_item"
    assert payload["source_opened_by_worker"] is False
    assert payload["network_required"] is False
    assert payload["external_api_used"] is False
    assert payload["media_downloaded"] is False
    assert payload["episode_dirs_created"] is False
    assert payload["fetch_authorized"] is False
    assert payload["rights_approved"] is False
    assert payload["production_ready"] is False
    assert payload["public_ready"] is False
    assert output_path.exists()
    assert dashboard_path.exists()
