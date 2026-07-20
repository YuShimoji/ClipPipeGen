from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.integrations.render import five_source_short_portfolio as out11


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _source_package(
    root: Path,
    *,
    role: str,
    artifact_id: str,
    state: str,
    video_identity: str,
    duration: float,
) -> dict[str, Any]:
    package = root / "source_packages" / role
    package.mkdir(parents=True)
    portfolio_slot = {
        "out10": "OUT-10",
        "source04": "SOURCE-04",
        "source05": "SOURCE-05",
    }[role]
    video = package / "candidate_01.mp4"
    video.write_bytes((f"mp4-{role}-".encode("ascii") * 220)[:1536])
    video_sha = out11._sha256(video)
    readback = {
        "schema_version": f"fixture.{role}.v0",
        "artifact_id": artifact_id,
        "state": state,
        "episode_id": f"fixture-{portfolio_slot.lower()}",
        "source_identity": {"identity": video_identity},
        "candidate": {"duration_seconds": duration},
        "video": {
            "package_relative_path": "candidate_01.mp4",
            "sha256": video_sha,
        },
    }
    if role == "out10":
        platform, provider_id = video_identity.split(":", maxsplit=1)
        readback["source_identity"] = {
            "platform": platform,
            "provider_id": provider_id,
        }
    readback_path = package / "candidate_readback.json"
    _write_json(readback_path, readback)
    manifest = {
        "schema_version": f"fixture.{role}.v0",
        "artifact_id": artifact_id,
        "state": state,
        "files": [
            {
                "package_relative_path": "candidate_01.mp4",
                "sha256": video_sha,
                "byte_size": video.stat().st_size,
            },
            {
                "package_relative_path": "candidate_readback.json",
                "sha256": out11._sha256(readback_path),
                "byte_size": readback_path.stat().st_size,
            },
        ],
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    manifest["manifest_self_integrity"]["sha256"] = (
        out11._canonical_manifest_self_hash(manifest)
    )
    manifest_path = package / "candidate_manifest.json"
    _write_json(manifest_path, manifest)
    return {
        "role": role,
        "title": {
            "out10": "OUT-10 final endpoint repair",
            "source04": "Fourth real source",
            "source05": "Fifth real source",
        }[role],
        "portfolio_slot": portfolio_slot,
        "video_identity": video_identity,
        "source_artifact_id": artifact_id,
        "source_state": state,
        "package_dir": package.relative_to(root).as_posix(),
        "readback_relative_path": "candidate_readback.json",
        "manifest_relative_path": "candidate_manifest.json",
        "video_relative_path": "candidate_01.mp4",
        "video_sha256": video_sha,
        "video_byte_size": video.stat().st_size,
        "readback_sha256": out11._sha256(readback_path),
        "manifest_sha256": out11._sha256(manifest_path),
        "duration": duration,
    }


def _scorecard_row(
    *,
    slot: str,
    video_identity: str,
    duration: float | list[float],
    mp4_sha256: str | list[str],
    human_status: str,
    render_count: int,
) -> dict[str, Any]:
    return {
        "portfolio_slot": slot,
        "source_identity": {"platform": "youtube", "official": True},
        "video_identity": video_identity,
        "episode_identity": f"fixture-{slot.lower()}",
        "language": "ja" if slot != "SOURCE-05" else "id",
        "source_resolution": "1920x1080",
        "source_aspect": "16:9",
        "selected_duration_seconds": duration,
        "transcript_caption_authority": "official_youtube_json3",
        "native_baked_caption_status": "observed",
        "speaker_count": 2 if slot != "SOURCE-05" else "unknown",
        "speaker_identity_authority": "official_metadata_or_unknown",
        "cue_count": 12,
        "average_cue_length_seconds": 1.8,
        "maximum_cue_length_seconds": 3.2,
        "composition_strategy": "source_specific_observed_fit",
        "caption_handling": "single_authority_overlay",
        "endpoint_evidence": "preflight_and_agent_selection",
        "render_count": render_count,
        "corrective_render_count": 0,
        "mp4_sha256": mp4_sha256,
        "human_acceptance_status": human_status,
        "source_specific_debt": "human_semantic_review_pending",
        "reusable_validation": ["manifest", "decode", "range"],
        "source_specific_human_judgment": ["composition", "endpoint"],
        "important_content_conflict": False,
        "production_status": "not_accepted",
        "rights_status": "pending",
    }


def _fixture(tmp_path: Path) -> tuple[Path, Path, dict[str, Any]]:
    candidates = [
        _source_package(
            tmp_path,
            role="out10",
            artifact_id="clip-out10-test",
            state="OUT10_FINAL_UTTERANCE_ENDPOINT_REPAIR_READY_FOR_COMBINED_REVIEW",
            video_identity="youtube:TlnviOwLRmk",
            duration=30.014,
        ),
        _source_package(
            tmp_path,
            role="source04",
            artifact_id="clip-source04-test",
            state="SOURCE_ADAPTIVE_SHORT_REVIEW_READY",
            video_identity="youtube:PQ54uUV41-k",
            duration=22.4,
        ),
        _source_package(
            tmp_path,
            role="source05",
            artifact_id="clip-source05-test",
            state="SOURCE_ADAPTIVE_SHORT_REVIEW_READY",
            video_identity="youtube:gUwJBRUIWow",
            duration=34.8,
        ),
    ]
    context08 = _scorecard_row(
        slot="OUT-08",
        video_identity="youtube:7J5aS_pcBj4",
        duration=[28.266667, 53.466667],
        mp4_sha256=["1" * 64, "2" * 64],
        human_status="accepted_internal",
        render_count=2,
    )
    context09 = _scorecard_row(
        slot="OUT-09",
        video_identity="youtube:D4i4fjs9PWc",
        duration=33.333008,
        mp4_sha256="3" * 64,
        human_status="accepted_internal",
        render_count=1,
    )
    rows = [context08, context09]
    for item in candidates:
        rows.append(
            _scorecard_row(
                slot=item["portfolio_slot"],
                video_identity=item["video_identity"],
                duration=item["duration"],
                mp4_sha256=item["video_sha256"],
                human_status="human_review_pending",
                render_count=1,
            )
        )
        item.pop("duration")
    config = {
        "schema_version": out11.CONFIG_SCHEMA_VERSION,
        "artifact_id": out11.ARTIFACT_ID,
        "state": out11.STATE,
        "review_question": out11.REVIEW_QUESTION,
        "accepted_context_only_slots": ["OUT-08", "OUT-09"],
        "review_candidates": candidates,
        "scorecard_rows": rows,
        "boundaries": {
            "rights_acceptance": False,
            "production_acceptance": False,
            "thumbnail_acceptance": False,
            "public_or_publishing_acceptance": False,
            "winner_selected": False,
            "universal_crop_claimed": False,
            "universal_caption_style_claimed": False,
            "universal_speaker_color_policy_claimed": False,
            "human_review_pending": True,
            "acceptance_granted": False,
        },
    }
    config_path = tmp_path / "out11_config.json"
    _write_json(config_path, config)
    output = (
        tmp_path
        / "episodes"
        / "out11_fixture"
        / "review"
        / "out11_five_source_short_portfolio"
    )
    return config_path, output, config


def test_builds_package_contained_three_video_review_and_five_rows(
    tmp_path: Path,
) -> None:
    config_path, output, config = _fixture(tmp_path)

    result = out11.build_five_source_short_portfolio(
        config_path=config_path,
        output_dir=output,
        base_dir=tmp_path,
    )

    assert result["artifact_id"] == out11.ARTIFACT_ID
    assert result["state"] == out11.STATE
    readback = json.loads((output / "review_readback.json").read_text("utf-8"))
    scorecard = json.loads(
        (output / "five_source_scorecard.json").read_text("utf-8")
    )
    manifest = json.loads((output / "review_manifest.json").read_text("utf-8"))
    assert readback["review_question"] == out11.REVIEW_QUESTION
    assert readback["review_question_count"] == 1
    assert len(readback["review_candidates"]) == 3
    assert scorecard["row_count"] == 5
    assert len(scorecard["rows"]) == 5
    assert scorecard["columns"] == list(out11.REQUIRED_SCORECARD_COLUMNS)
    assert scorecard["winner_selected"] is False
    assert scorecard["production_readiness_claimed"] is False
    assert manifest["manifest_self_integrity"]["sha256"] == (
        out11._canonical_manifest_self_hash(manifest)
    )
    assert len(manifest["candidate_videos"]) == 3

    for item in config["review_candidates"]:
        copied = output / "candidates" / f"{item['role']}.mp4"
        source = tmp_path / item["package_dir"] / item["video_relative_path"]
        assert copied.read_bytes() == source.read_bytes()
        assert out11._sha256(copied) == item["video_sha256"]
        assert copied.stat().st_size == item["video_byte_size"]

    manifest_payloads = {
        row["package_relative_path"] for row in manifest["files"]
    }
    actual_payloads = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and path.name != "review_manifest.json"
    }
    assert manifest_payloads == actual_payloads


def test_review_html_is_linear_safe_and_evidence_is_folded(tmp_path: Path) -> None:
    config_path, output, _config = _fixture(tmp_path)
    out11.build_five_source_short_portfolio(
        config_path=config_path,
        output_dir=output,
        base_dir=tmp_path,
    )

    html = (output / "index.html").read_text("utf-8")
    assert html.count("<video ") == 3
    assert html.count("data-review-question=") == 1
    assert out11.REVIEW_QUESTION in html
    assert "autoplay" not in html.lower()
    assert "localStorage" not in html
    assert "sessionStorage" not in html
    assert html.count(" controls playsinline muted preload=\"metadata\"") == 3
    assert "video.currentTime=0" in html
    assert "other.pause()" in html
    assert "const maximumVolume=0.25" in html
    assert html.count("<details>") == 4
    assert "<details open" not in html
    for path in (output / "candidates").glob("*.mp4"):
        assert out11._sha256(path) in html


def test_server_binds_hash_and_size_for_all_three_videos(tmp_path: Path) -> None:
    config_path, output, config = _fixture(tmp_path)
    out11.build_five_source_short_portfolio(
        config_path=config_path,
        output_dir=output,
        base_dir=tmp_path,
    )

    server = (output / "serve_preview.ps1").read_text("utf-8")
    opener = (output / "open_preview.ps1").read_text("utf-8")
    assert "[int]$Port = 8074" in server
    assert server.count("@{ Name = 'candidates/") == 3
    assert "$request.AddRange(0, $rangeEnd)" in server
    assert "[int]$range.StatusCode -ne 206" in server
    assert "No process was stopped" in server
    assert "Stop-Process" not in server
    assert "taskkill" not in server.lower()
    assert "[switch]$Serve" in opener
    assert "-ProbeOnly" in opener
    for item in config["review_candidates"]:
        assert item["video_sha256"] in server
        assert str(item["video_byte_size"]) in server


def test_source_mp4_tamper_is_rejected_before_copy(tmp_path: Path) -> None:
    config_path, output, config = _fixture(tmp_path)
    source04 = config["review_candidates"][1]
    source_video = (
        tmp_path / source04["package_dir"] / source04["video_relative_path"]
    )
    source_video.write_bytes(source_video.read_bytes() + b"tamper")

    with pytest.raises(
        out11.FiveSourceShortPortfolioError,
        match="source manifest payload hash/size mismatch: source04/candidate_01.mp4",
    ):
        out11.build_five_source_short_portfolio(
            config_path=config_path,
            output_dir=output,
            base_dir=tmp_path,
        )
    assert not output.exists()


def test_source_manifest_self_hash_tamper_is_rejected(tmp_path: Path) -> None:
    config_path, output, config = _fixture(tmp_path)
    source05 = config["review_candidates"][2]
    manifest_path = tmp_path / source05["package_dir"] / source05[
        "manifest_relative_path"
    ]
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["tampered_note"] = True
    _write_json(manifest_path, manifest)
    source05["manifest_sha256"] = out11._sha256(manifest_path)
    _write_json(config_path, config)

    with pytest.raises(
        out11.FiveSourceShortPortfolioError,
        match="source manifest self-integrity mismatch: source05",
    ):
        out11.build_five_source_short_portfolio(
            config_path=config_path,
            output_dir=output,
            base_dir=tmp_path,
        )


def test_scorecard_missing_contract_column_is_rejected(tmp_path: Path) -> None:
    config_path, output, config = _fixture(tmp_path)
    del config["scorecard_rows"][4]["speaker_identity_authority"]
    _write_json(config_path, config)

    with pytest.raises(
        out11.FiveSourceShortPortfolioError,
        match="scorecard row is missing columns: speaker_identity_authority",
    ):
        out11.build_five_source_short_portfolio(
            config_path=config_path,
            output_dir=output,
            base_dir=tmp_path,
        )


def test_scorecard_cannot_declare_winner_or_production_readiness(
    tmp_path: Path,
) -> None:
    config_path, output, config = _fixture(tmp_path)
    config["scorecard_rows"][2]["winner"] = True
    _write_json(config_path, config)

    with pytest.raises(
        out11.FiveSourceShortPortfolioError,
        match="must not declare winner",
    ):
        out11.build_five_source_short_portfolio(
            config_path=config_path,
            output_dir=output,
            base_dir=tmp_path,
        )


def test_exact_combined_question_is_required(tmp_path: Path) -> None:
    config_path, output, config = _fixture(tmp_path)
    config["review_question"] += " fixed form"
    _write_json(config_path, config)

    with pytest.raises(
        out11.FiveSourceShortPortfolioError,
        match="combined review question is not exact",
    ):
        out11.build_five_source_short_portfolio(
            config_path=config_path,
            output_dir=output,
            base_dir=tmp_path,
        )
