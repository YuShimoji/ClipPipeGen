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


def test_operator_cockpit_builds_home_funnel_and_preserves_boundaries(tmp_path: Path):
    result = build_cockpit(tmp_path)

    payload = json.loads(result["output_path"].read_text(encoding="utf-8"))
    html = result["dashboard_path"].read_text(encoding="utf-8")

    assert payload["schema_id"] == "clippipegen.operator_cockpit.v0"
    assert payload["title"] == "ClipPipeGen Operator Cockpit / Content Planning Review"
    assert payload["artifact_id"] == "clip-cpd08-operator-home-funnel-meters-v0-001"
    assert payload["ux"]["version"] == "v3_home_funnel_meters_v0"
    assert payload["ux"]["layout"] == "operator_home_funnel_meters"
    assert payload["ux"]["default_theme"] == "dark"
    assert payload["ux"]["theme_toggle"] is True
    assert payload["ux"]["home_area"] == "visible"
    assert payload["ux"]["action_queue"] == "visible"
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

    metric_by_id = {item["metric_id"]: item for item in payload["home_metrics"]}
    assert set(metric_by_id) == {
        "total_candidates",
        "source_backed",
        "source_missing_ideas",
        "blocked_or_hold",
        "inspectable_packets",
        "fetch_authorized",
        "media_downloaded",
        "episode_dirs_created",
    }
    assert metric_by_id["source_backed"]["value"] == 1
    assert metric_by_id["source_backed"]["href"] == "#primary-review"
    assert metric_by_id["source_missing_ideas"]["value"] == 3
    assert metric_by_id["source_missing_ideas"]["href"] == "#source-missing"
    assert metric_by_id["blocked_or_hold"]["value"] == 1
    assert metric_by_id["blocked_or_hold"]["href"] == "#blocked-hold"
    assert metric_by_id["fetch_authorized"]["value"] == 0
    assert metric_by_id["media_downloaded"]["value"] == 0
    assert metric_by_id["episode_dirs_created"]["value"] == 0

    assert [stage["stage_id"] for stage in payload["funnel_stages"]] == [
        "idea_candidates",
        "source_backed",
        "human_review_waiting",
        "private_local_review_waiting",
        "edit_render_not_started",
    ]
    assert [stage["count"] for stage in payload["funnel_stages"]] == [5, 1, 1, 0, 0]
    assert payload["funnel_stages"][1]["href"] == "#primary-review"
    assert payload["funnel_stages"][3]["status"] == "locked"

    assert [item["priority"] for item in payload["action_queue"]] == [
        "primary",
        "secondary",
        "hold",
    ]
    assert payload["action_queue"][0]["href"] == "#primary-review"
    assert payload["action_queue"][0]["count"] == 1
    assert payload["action_queue"][1]["href"] == "#source-missing"
    assert payload["action_queue"][2]["href"] == "#blocked-hold"
    assert {item["section_id"] for item in payload["section_links"]} >= {
        "primary-review",
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
    assert "Operator Home / Funnel Meters v0" in html
    assert 'id="operator-home"' in html
    assert "Candidate Funnel" in html
    assert 'id="action-queue"' in html
    assert "Action Queue" in html
    assert 'href="#primary-review"' in html
    assert 'href="#source-missing"' in html
    assert 'href="#blocked-hold"' in html
    assert 'id="primary-review"' in html
    assert 'id="primary-review-card"' in html
    assert 'id="candidate-state-board"' in html
    assert 'id="source-missing"' in html
    assert 'id="blocked-hold"' in html
    assert 'id="safety-boundary"' in html
    assert 'id="developer-appendix"' in html
    assert "not video-backed" in html
    assert "cpd01_jp_en_phrase_gap" in html
    assert "do_not_treat_as_video-backed_candidate" not in html
    assert "content_dashboard.html" in html
    assert "source_inspection_packet_dashboard.html" in html
    assert "artifact_id:" not in html[: html.index('id="developer-appendix"')]

    home_area = html[html.index('id="operator-home"') : html.index('id="action-queue"')]
    action_area = html[html.index('id="action-queue"') : html.index('id="primary-review"')]
    assert "<table>" not in home_area
    assert "<table>" not in action_area
    assert html.index('id="operator-home"') < html.index('id="action-queue"')
    assert html.index('id="action-queue"') < html.index('id="primary-review"')
    assert html.index('id="primary-review"') < html.index('id="candidate-state-board"')
    assert html.index('id="candidate-state-board"') < html.index('id="safety-boundary"')
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
    assert payload["artifact_id"] == "clip-cpd08-operator-home-funnel-meters-v0-001"
    assert payload["total_candidates"] == 5
    assert payload["source_backed_count"] == 1
    assert payload["source_missing_count"] == 4
    assert payload["source_missing_idea_backlog_count"] == 3
    assert payload["blocked_or_hold_count"] == 1
    assert payload["home_metric_count"] == 8
    assert payload["funnel_stage_count"] == 5
    assert payload["action_queue_count"] == 3
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
