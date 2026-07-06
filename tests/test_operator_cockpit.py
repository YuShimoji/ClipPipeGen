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


def test_operator_cockpit_classifies_source_grounding(tmp_path: Path):
    result = build_cockpit(tmp_path)

    payload = json.loads(result["output_path"].read_text(encoding="utf-8"))
    html = result["dashboard_path"].read_text(encoding="utf-8")

    assert payload["schema_id"] == "clippipegen.operator_cockpit.v0"
    assert payload["title"] == "ClipPipeGen Operator Cockpit / Content Planning Review"
    assert payload["artifact_id"] == "clip-cpd07-operator-cockpit-ux-v2-dark-mode-v0-001"
    assert payload["ux"]["version"] == "v2_dark_mode_v0"
    assert payload["ux"]["layout"] == "vertical_primary_review_card"
    assert payload["ux"]["default_theme"] == "dark"
    assert payload["ux"]["theme_toggle"] is True
    assert payload["summary"]["total_candidates"] == 5
    assert payload["summary"]["total_seed_drafts"] == 5
    assert payload["summary"]["source_url_present_count"] == 1
    assert payload["summary"]["source_backed_count"] == 1
    assert payload["summary"]["source_missing_count"] == 4
    assert payload["summary"]["source_missing_idea_backlog_count"] == 3
    assert payload["summary"]["blocked_or_hold_count"] == 1
    assert payload["summary"]["inspectable_packet_count"] == 1
    assert payload["summary"]["decision_template_entry_count"] == 1
    assert payload["summary"]["fetch_authorized_count"] == 0
    assert payload["summary"]["media_downloaded"] is False
    assert payload["summary"]["episode_dirs_created"] is False
    assert payload["summary"]["health"] == "ready_for_single_source_identity_review"
    assert payload["recommended_next_action"]["action_id"] == "inspect_single_source_backed_item"
    assert payload["recommended_next_action"]["user_work"] == "open_only"

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
    assert ready["inspection_packet_id"] == (
        "source_inspection_packet_ep_seed_cpd01_bancho_marine_misunderstanding"
    )
    assert ready["source_url"] == "https://www.youtube.com/watch?v=7J5aS_pcBj4"
    assert ready["video_id"] == "7J5aS_pcBj4"
    assert ready["provenance_state"] == "source_url_present_unreviewed"
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

    assert all(
        item["candidate_id"] != "cpd01_jp_en_phrase_gap"
        for item in source_backed
    )
    assert all(
        item["open_by_default"] is False
        for item in payload["buckets"]["internal_pipeline_artifact_only"]
    )

    assert "ClipPipeGen Operator Cockpit / Content Planning Review" in html
    assert 'data-theme="dark"' in html
    assert "--bg:" in html
    assert "--surface:" in html
    assert "toggleOperatorTheme" in html
    assert "localStorage" in html
    assert 'id="theme-toggle"' in html
    assert "今、人間が確認する動画は 1 件だけです。" in html
    assert "残り 4 件は元動画未特定の企画メモ" in html
    assert 'id="primary-review-card"' in html
    assert "今回確認する1件" in html
    assert "このURLは、「番長、船長を完全に勘違いする」の元動画として妥当か？" in html
    assert "判断ラベル（表示のみ）" in html
    assert "今は取得しない" in html
    assert "文字起こししない" in html
    assert "cpd01_jp_en_phrase_gap" in html
    assert "do_not_treat_as_video-backed_candidate" not in html
    assert "未特定の企画メモ" in html
    assert "元動画未確認。動画候補として扱わない。" in html
    assert 'id="safety-boundary"' in html
    assert "安全境界" in html
    assert 'id="developer-appendix"' in html
    assert "開発用詳細" in html
    assert "content_dashboard.html" in html
    assert "source_inspection_packet_dashboard.html" in html
    assert "source-backed" not in html
    assert "artifact_id:" not in html[: html.index('id="developer-appendix"')]
    primary = html[html.index('id="primary-review-card"') : html.index('id="source-missing-ideas"')]
    assert "<table>" not in primary
    assert html.index('id="primary-review-card"') < html.index('id="source-missing-ideas"')
    assert html.index('id="source-missing-ideas"') < html.index('id="safety-boundary"')
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
    assert payload["artifact_id"] == "clip-cpd07-operator-cockpit-ux-v2-dark-mode-v0-001"
    assert payload["total_candidates"] == 5
    assert payload["source_backed_count"] == 1
    assert payload["source_missing_count"] == 4
    assert payload["source_missing_idea_backlog_count"] == 3
    assert payload["blocked_or_hold_count"] == 1
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
