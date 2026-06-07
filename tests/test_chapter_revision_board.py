"""Chapter revision board generation tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.chapter_revision_board import build_chapter_revision_board


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_chapter_revision_board_generates_nine_chapters_and_keeps_boundaries(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)

    result = build_chapter_revision_board(
        episode_dir=episode_dir,
        review_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        output_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        base_dir=tmp_path,
    )

    board = result["board"]
    chapters = board["chapters"]
    assert board["board_kind"] == "chapter_revision_board_v0"
    assert board["board_status"] == "generated"
    assert board["generated_with_warnings"] is False
    assert board["missing_optional_artifacts"] == []
    assert board["boundary_flags"]["production_candidate"] is False
    assert board["boundary_flags"]["creative_acceptance"] is False
    assert board["boundary_flags"]["publish_acceptance"] is False
    assert board["boundary_flags"]["rights_status"] == "pending"
    assert board["summary"]["chapter_count"] == 9
    assert board["summary"]["retained_context_risk_count"] == 6
    assert board["summary"]["candidate_seed_count"] == 9
    assert board["summary"]["current_decision"] == "mixed"
    assert board["summary"]["current_decision_counts"] == {
        "keep": 3,
        "needs_adjustment": 5,
        "reject": 1,
    }
    assert board["summary"]["speed_pass_role"] == "historical_candidate_seed_evidence_only"
    assert board["summary"]["all_cuts_candidate_seed_only"] is False
    assert board["summary"]["historical_speed_pass_all_cuts_candidate_seed_only"] is True
    assert [chapter["chapter_id"] for chapter in chapters] == [f"ch_{i:03d}" for i in range(1, 10)]
    assert [chapter["source_cut_id"] for chapter in chapters] == [f"cut_{i:03d}" for i in range(1, 10)]
    assert chapters[2]["current_decision"] == "keep"
    assert chapters[3]["current_decision"] == "needs_adjustment"
    assert chapters[8]["current_decision"] == "reject"
    assert {chapter["decision_source"] for chapter in chapters} == {"cut_decision_packet"}
    assert sum(1 for chapter in chapters if chapter["retained_context_risk"]) == 6
    assert chapters[3]["representative_role"] == "retained_context_risk_representative"
    assert chapters[7]["representative_role"] == "dense_subtitle_representative"
    assert chapters[8]["representative_role"] == "short_passed_representative"
    assert result["board_path"].exists()
    assert result["board_html_path"].exists()


def test_patch_template_defaults_are_empty_and_do_not_patch_source_transcript(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)

    result = build_chapter_revision_board(
        episode_dir=episode_dir,
        review_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        output_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        base_dir=tmp_path,
    )

    board = result["board"]
    patch = result["patch_template"]
    assert len(patch["revisions"]) == 9
    assert board["chapters"][0]["operator_fields"]["editorial_intent"] == ""
    assert board["chapters"][0]["operator_fields"]["script_override"] == ""
    for revision in patch["revisions"]:
        assert revision["chapter_action"] == "undecided"
        assert revision["editorial_intent"] == ""
        assert revision["script_override"] == ""
        assert revision["display_subtitle_request"] == ""
        assert revision["boundary_adjustment"]["mode"] == "none"
        assert revision["rollback_signal"] == "undecided"
        assert revision["analyst_action"] == "undecided"
        assert revision["downstream_target"] == []
        assert revision["production_candidate_request"] is False
    forbidden_keys = {
        "source_transcript_patch",
        "transcript_override",
        "official_subtitle_track_patch",
        "subtitle_track_override",
    }
    assert forbidden_keys.isdisjoint(_recursive_keys(patch))
    assert "script_override" in _recursive_keys(patch)


def test_chapter_revision_board_html_and_csv_are_operator_visible(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)

    result = build_chapter_revision_board(
        episode_dir=episode_dir,
        review_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        output_dir=episode_dir / "review" / "jp_pilot01r3_cut_review",
        base_dir=tmp_path,
    )

    html = result["board_html_path"].read_text(encoding="utf-8")
    csv_text = result["patch_csv_path"].read_text(encoding="utf-8")
    assert "not production acceptance" in html
    assert "rights pending" in html
    assert "production_candidate=false" in html
    assert "Decision Vocabulary" in html
    assert "Downstream Impact Guide" in html
    assert "No source transcript or official subtitle track is mutated" in html
    assert csv_text.splitlines()[0].startswith(
        "chapter_id,cut_id,chapter_action,editorial_intent,script_override"
    )
    assert "ch_001,cut_001,undecided" in csv_text


def test_chapter_revision_board_generates_with_warnings_without_baseline_acceptance(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    (review_dir / "regenerated_r3_baseline_acceptance.json").unlink()
    (review_dir / "regenerated_r3_baseline_acceptance.html").unlink()

    result = build_chapter_revision_board(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )

    board = result["board"]
    html = result["board_html_path"].read_text(encoding="utf-8")
    assert board["board_status"] == "generated_with_warnings"
    assert board["generated_with_warnings"] is True
    assert board["summary"]["chapter_count"] == 9
    assert board["summary"]["retained_context_risk_count"] == 6
    assert "regenerated_r3_baseline_acceptance.json" in board["missing_optional_artifacts"][0]
    assert any("regenerated_r3_baseline_acceptance.html" in p for p in board["missing_optional_artifacts"])
    assert "Generated with warnings: optional baseline/acceptance plan artifacts missing." in html
    assert "regenerated_r3_baseline_acceptance.json" in html
    assert result["patch_template_path"].exists()
    assert result["patch_csv_path"].exists()


def test_chapter_revision_board_generates_with_warnings_without_acceptance_plan(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    (review_dir / "production_subtitle_render_acceptance_plan.json").unlink()
    (review_dir / "production_subtitle_render_acceptance_plan.html").unlink()

    result = build_chapter_revision_board(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )

    board = result["board"]
    html = result["board_html_path"].read_text(encoding="utf-8")
    assert board["board_status"] == "generated_with_warnings"
    assert board["generated_with_warnings"] is True
    assert board["boundary_flags"]["production_candidate"] is False
    assert board["boundary_flags"]["rights_status"] == "pending"
    assert any(
        "production_subtitle_render_acceptance_plan.json" in p
        for p in board["missing_optional_artifacts"]
    )
    assert "production_subtitle_render_acceptance_plan.html" in html
    assert {revision["chapter_action"] for revision in result["patch_template"]["revisions"]} == {
        "undecided"
    }


def test_chapter_revision_board_prefers_current_review_and_decision_packets_over_stale_speed_pass(
    tmp_path: Path,
):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    packet_path = review_dir / "cut_review_packet.json"
    decision_path = review_dir / "cut_decision_packet.json"
    speed_path = review_dir / "cut_decision_speed_pass.json"
    edit_pack_path = episode_dir / "edit_pack.json"

    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    decision_packet = json.loads(decision_path.read_text(encoding="utf-8"))
    speed = json.loads(speed_path.read_text(encoding="utf-8"))
    edit_pack = json.loads(edit_pack_path.read_text(encoding="utf-8"))

    _replace_cut(
        packet["cuts"],
        "cut_003",
        start_seconds=22.606,
        end_seconds=49.566,
        duration_seconds=26.96,
        subtitle_event_count=20,
        subtitle_density_per_second=0.742,
        subtitle_chars_per_second=6.25,
        context_status="needs_review",
    )
    _replace_cut(
        packet["cuts"],
        "cut_004",
        start_seconds=50.868,
        end_seconds=60.277,
        duration_seconds=9.409,
        subtitle_event_count=5,
        subtitle_density_per_second=0.531,
        subtitle_chars_per_second=5.9,
        context_status="needs_review",
    )
    _replace_cut_decision(
        decision_packet["decisions"],
        "cut_003",
        final_cut_decision="keep",
        duration_seconds=26.96,
        manual_override_reason=(
            "Keep candidate with retained context risk visible after boundary/context review."
        ),
    )
    _replace_cut_decision(
        decision_packet["decisions"],
        "cut_004",
        final_cut_decision="needs_adjustment",
        duration_seconds=9.409,
        adjustment_recommendation="review segmentation before promotion",
    )
    _replace_cut(
        speed["cuts"],
        "cut_003",
        start_seconds=22.606,
        end_seconds=41.725,
        duration_seconds=19.119,
        final_decision="accept_candidate",
    )
    _replace_cut(
        speed["cuts"],
        "cut_004",
        start_seconds=41.725,
        end_seconds=60.277,
        duration_seconds=18.552,
        final_decision="accept_candidate",
    )
    edit_pack["cut_candidates"] = [
        {"id": "cut_003", "resegmentation_target": False},
        {"id": "cut_004", "resegmentation_target": True},
    ]

    _write_json(packet, packet_path)
    _write_json(decision_packet, decision_path)
    _write_json(speed, speed_path)
    _write_json(edit_pack, edit_pack_path)

    result = build_chapter_revision_board(
        episode_dir=episode_dir,
        review_dir=review_dir,
        output_dir=review_dir,
        base_dir=tmp_path,
    )

    board = result["board"]
    board_text = result["board_path"].read_text(encoding="utf-8")
    cut_003 = _chapter(board, "cut_003")
    cut_004 = _chapter(board, "cut_004")

    assert cut_003["source_start_seconds"] == 22.606
    assert cut_003["source_end_seconds"] == 49.566
    assert cut_003["duration_seconds"] == 26.96
    assert cut_003["subtitle_count"] == 20
    assert cut_003["current_decision"] == "keep"
    assert cut_003["decision_scope"] == "current_cut_decision"
    assert cut_003["manual_override_reason"]
    assert "19.119" not in cut_003["manual_override_reason"]
    assert cut_003["decision_source"] == "cut_decision_packet"
    assert cut_003["historical_candidate_seed_decision"] == {
        "source": "cut_decision_speed_pass",
        "final_decision": "accept_candidate",
        "decision_scope": "candidate_seed_only",
        "timing_authority": "not_current_authority",
        "historical_only": True,
    }
    assert cut_004["source_start_seconds"] == 50.868
    assert cut_004["source_end_seconds"] == 60.277
    assert cut_004["duration_seconds"] == 9.409
    assert cut_004["subtitle_count"] == 5
    assert cut_004["current_decision"] == "needs_adjustment"
    assert cut_004["resegmentation_target"] is True
    assert "resegmentation_target" in cut_004["current_risks"]
    assert "19.119" not in board_text


def test_build_chapter_revision_board_cli_writes_json_html_and_templates(tmp_path: Path):
    episode_dir = _write_episode(tmp_path)
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-chapter-revision-board",
            "--episode-dir",
            str(episode_dir),
            "--review-dir",
            str(review_dir),
            "--output-dir",
            str(review_dir),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["board_status"] == "generated"
    assert payload["generated_with_warnings"] is False
    assert payload["missing_optional_artifacts"] == []
    assert payload["chapter_count"] == 9
    assert payload["retained_context_risk_count"] == 6
    assert payload["production_candidate"] is False
    assert payload["rights_status"] == "pending"
    assert Path(payload["board"]).exists()
    assert Path(payload["board_html"]).exists()
    assert Path(payload["patch_template"]).exists()
    assert Path(payload["patch_csv"]).exists()


def test_chapter_revision_loop_docs_record_editorial_layer_boundary():
    doc = (REPO_ROOT / "docs" / "CHAPTER_REVISION_LOOP.md").read_text(encoding="utf-8")
    schema_doc = (REPO_ROOT / "docs" / "SCHEMAS" / "v1" / "chapter_revision_patch.md").read_text(
        encoding="utf-8"
    )
    assert "source transcript" in doc
    assert "editorial layer" in doc
    assert "not production acceptance" in doc
    assert "source transcript mutation" in schema_doc
    assert "script_override" in schema_doc


def _write_episode(tmp_path: Path) -> Path:
    episode_dir = tmp_path / "episodes" / "jp_pilot01_hololive_bancho_20260525"
    review_dir = episode_dir / "review" / "jp_pilot01r3_cut_review"
    review_dir.mkdir(parents=True)
    _write_json(_rights_manifest(), episode_dir / "rights_manifest.json")
    _write_json(_transcript(), episode_dir / "transcript.json")
    _write_json(_edit_pack(), episode_dir / "edit_pack.json")
    _write_json({"schema_version": "v1", "episode_id": episode_dir.name, "materials": []}, episode_dir / "material_ledger.json")
    _write_review_artifacts(review_dir, episode_dir.name)
    return episode_dir


def _write_review_artifacts(review_dir: Path, episode_id: str) -> None:
    packet = _cut_review_packet(episode_id)
    speed = _speed_pass(episode_id)
    source_identity = packet["source_identity"]
    _write_json(packet, review_dir / "cut_review_packet.json")
    _write_json(_cut_decision_packet(episode_id), review_dir / "cut_decision_packet.json")
    _write_json(
        {
            "schema_version": "v1",
            "artifact_kind": "ed10_r3_evidence_summary",
            "episode_id": episode_id,
            "source_identity": source_identity,
            "production_candidate": False,
            "metrics": {"rights": {"status": "pending"}},
        },
        review_dir / "evidence_summary.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "artifact_kind": "non_repo_artifact_handoff",
            "episode_id": episode_id,
            "source_identity": source_identity,
            "boundary": {"production_candidate": False, "rights_status": "pending"},
        },
        review_dir / "non_repo_artifact_handoff.json",
    )
    _write_json(speed, review_dir / "cut_decision_speed_pass.json")
    _write_json(
        {
            "schema_version": "v1",
            "artifact_kind": "regenerated_r3_baseline_acceptance",
            "episode_id": episode_id,
            "source_identity": source_identity,
            "byte_exact_equivalence_to_original_r3": "not_claimed",
        },
        review_dir / "regenerated_r3_baseline_acceptance.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "artifact_kind": "production_subtitle_render_acceptance_plan",
            "episode_id": episode_id,
            "source_identity": source_identity,
            "boundary_flags": {
                "production_candidate": False,
                "creative_acceptance": False,
                "publish_acceptance": False,
                "rights_status": "pending",
            },
        },
        review_dir / "production_subtitle_render_acceptance_plan.json",
    )
    for name in [
        "cut_review_report.html",
        "evidence_summary.html",
        "non_repo_artifact_handoff.html",
        "cut_decision_report.html",
        "cut_decision_speed_pass.html",
        "regenerated_r3_baseline_acceptance.html",
        "production_subtitle_render_acceptance_plan.html",
    ]:
        (review_dir / name).write_text("<!doctype html><p>fixture</p>", encoding="utf-8")


def _cut_review_packet(episode_id: str) -> dict:
    cuts = []
    for i in range(1, 10):
        cut_id = f"cut_{i:03d}"
        status = "passed" if i in {1, 2, 9} else "needs_review"
        subtitle_count = 33 if i == 8 else (4 if i == 9 else 6 + i)
        duration = 5.0 if i == 9 else 18.0
        cuts.append(
            {
                "cut_id": cut_id,
                "selected": True,
                "start_seconds": float(i),
                "end_seconds": float(i) + duration,
                "duration_seconds": duration,
                "context_status": status,
                "context_notes": [f"{status} fixture"],
                "subtitle_event_count": subtitle_count,
                "subtitle_density_per_second": round(subtitle_count / duration, 3),
                "subtitle_char_count": subtitle_count * 8,
                "subtitle_chars_per_second": 18.0 if i == 8 else 6.0,
                "subtitle_preview": [f"subtitle {i} a", f"subtitle {i} b"],
                "segment_text_preview": [f"segment {i} a", f"segment {i} b"],
                "suggested_human_review_focus": "fixture focus",
            }
        )
    return {
        "schema_version": "v1",
        "artifact_kind": "cut_review_packet",
        "episode_id": episode_id,
        "source_identity": _source_identity(),
        "summary": {
            "cut_count": 9,
            "context_counts": {"passed": 3, "needs_review": 6, "failed": 0, "not_checked": 0},
            "rights_status": "pending",
            "production_candidate": False,
        },
        "cuts": cuts,
    }


def _speed_pass(episode_id: str) -> dict:
    cuts = []
    for i in range(1, 10):
        cut_id = f"cut_{i:03d}"
        status = "passed" if i in {1, 2, 9} else "needs_review"
        cuts.append(
            {
                "cut_id": cut_id,
                "start_seconds": float(i),
                "end_seconds": float(i) + (5.0 if i == 9 else 18.0),
                "duration_seconds": 5.0 if i == 9 else 18.0,
                "original_context_status": status,
                "final_decision": "accept_candidate",
                "decision_scope": "candidate_seed_only",
                "retained_context_risk": status == "needs_review",
            }
        )
    return {
        "schema_version": "v1",
        "artifact_kind": "r3_speed_first_candidate_decision",
        "episode_id": episode_id,
        "decision_policy": "speed_first_sample_expansion",
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": "pending",
        "source_identity": _source_identity(),
        "summary": {
            "cut_count": 9,
            "accept_candidate_count": 9,
            "retained_context_risk_count": 6,
        },
        "cuts": cuts,
    }


def _cut_decision_packet(episode_id: str) -> dict:
    decisions = []
    for i in range(1, 10):
        cut_id = f"cut_{i:03d}"
        status = "passed" if i in {1, 2, 9} else "needs_review"
        if i in {1, 2, 3}:
            final_decision = "keep"
        elif i == 9:
            final_decision = "reject"
        else:
            final_decision = "needs_adjustment"
        decisions.append(
            {
                "cut_id": cut_id,
                "start_seconds": float(i),
                "end_seconds": float(i) + (5.0 if i == 9 else 18.0),
                "duration_seconds": 5.0 if i == 9 else 18.0,
                "context_status": status,
                "subtitle_event_count": 33 if i == 8 else (4 if i == 9 else 6 + i),
                "final_cut_decision": final_decision,
                "manual_override_reason": (
                    "keep candidate with retained context risk visible"
                    if final_decision == "keep"
                    else None
                ),
                "adjustment_recommendation": (
                    "review before downstream promotion"
                    if final_decision == "needs_adjustment"
                    else None
                ),
                "production_candidate": False,
                "rights_status": "pending",
            }
        )
    return {
        "schema_version": "v1",
        "artifact_kind": "cut_decision_packet",
        "episode_id": episode_id,
        "decision_policy": "manual_review_surface",
        "production_candidate": False,
        "rights_status": "pending",
        "source_identity": _source_identity(),
        "summary": {
            "cut_count": 9,
            "decision_counts": {"keep": 3, "needs_adjustment": 5, "reject": 1},
        },
        "decisions": decisions,
    }


def _replace_cut(cuts: list[dict], cut_id: str, **updates) -> None:
    for cut in cuts:
        if cut.get("cut_id") == cut_id:
            cut.update(updates)
            return
    raise AssertionError(f"missing cut fixture: {cut_id}")


def _replace_cut_decision(decisions: list[dict], cut_id: str, **updates) -> None:
    for decision in decisions:
        if decision.get("cut_id") == cut_id:
            decision.update(updates)
            return
    raise AssertionError(f"missing decision fixture: {cut_id}")


def _chapter(board: dict, cut_id: str) -> dict:
    for chapter in board["chapters"]:
        if chapter.get("source_cut_id") == cut_id:
            return chapter
    raise AssertionError(f"missing chapter: {cut_id}")


def _edit_pack() -> dict:
    subtitles = []
    for i in range(1, 10):
        count = 33 if i == 8 else 4
        for n in range(count):
            subtitles.append(
                {
                    "id": f"sub_{i:03d}_{n:03d}",
                    "cut_id": f"cut_{i:03d}",
                    "start_seconds": float(i) + n * 0.1,
                    "end_seconds": float(i) + n * 0.1 + 0.08,
                    "text": "dense subtitle text that should wrap" if i == 8 and n == 0 else f"text {i}-{n}",
                    "source_type": "imported_subtitle_track",
                    "draft": True,
                    "diagnostic": True,
                    "production_subtitle_design": False,
                }
            )
    return {
        "schema_version": "v1",
        "episode_id": "jp_pilot01_hololive_bancho_20260525",
        "cut_candidates": [],
        "selected_cut_ids": [f"cut_{i:03d}" for i in range(1, 10)],
        "subtitles": subtitles,
    }


def _transcript() -> dict:
    return {
        "schema_version": "v1",
        "episode_id": "jp_pilot01_hololive_bancho_20260525",
        "stt": {
            "engine": "subtitle_track",
            "provider": "youtube_subtitles",
            "model": "episodes/jp/source_subs/7J5aS_pcBj4.ja.json3",
            "real_transcript": True,
        },
        "segments": [],
    }


def _rights_manifest() -> dict:
    return {
        "schema_version": "v1",
        "episode_id": "jp_pilot01_hololive_bancho_20260525",
        "source_video": {
            "url": "https://www.youtube.com/watch?v=7J5aS_pcBj4",
            "title": "fixture title",
            "channel": "fixture channel",
        },
        "compliance_check": {"status": "pending"},
    }


def _source_identity() -> dict:
    return {
        "source_video_identity": "fixture title",
        "source_video_title": "fixture title",
        "source_video_channel": "fixture channel",
        "youtube_id": "7J5aS_pcBj4",
        "source_url": "https://www.youtube.com/watch?v=7J5aS_pcBj4",
        "subtitle_track": "episodes/jp/source_subs/7J5aS_pcBj4.ja.json3",
        "transcript_source": "imported subtitle track / youtube_subtitles",
        "transcript_engine": "subtitle_track",
        "transcript_provider": "youtube_subtitles",
        "source_video_material_id": "src_video_jp_pilot01",
        "source_audio_material_id": "src_audio_jp_pilot01",
    }


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _recursive_keys(value) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key))
            keys.update(_recursive_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_recursive_keys(item))
    return keys
