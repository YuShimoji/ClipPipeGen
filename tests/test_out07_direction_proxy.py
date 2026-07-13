from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import main as cli_main
from src.integrations.render import out07_direction_proxy as proxy
from src.integrations.render import out07_native_cover as strict


def test_proxy_route_is_separate_from_exact_route() -> None:
    assert proxy.ARTIFACT_ID == strict.ARTIFACT_ID
    assert proxy.DEFAULT_OUTPUT_NAME != strict.DEFAULT_OUTPUT_NAME
    assert proxy.LOCAL_SOURCE_SHA256 != proxy.PLANNER_SOURCE_SHA256
    assert proxy.ACCEPTED_BASELINE_SHA256 == strict.ACCEPTED_BASELINE_SHA256
    assert strict.SOURCE_VIDEO_SHA256 == proxy.PLANNER_SOURCE_SHA256
    assert proxy.EVIDENCE_REVISION == (
        "thank-6f78657e-native-cover-direction-proxy-v1"
    )


@pytest.mark.parametrize("locator", proxy.STRICT_EXACT_BASELINE_LOCATORS)
def test_proxy_detects_exact_baseline_at_every_strict_route_locator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, locator: Path
) -> None:
    baseline = tmp_path / locator
    baseline.parent.mkdir(parents=True)
    baseline.write_bytes(b"exact-baseline-fixture")
    monkeypatch.setattr(
        proxy.strict,
        "_sha256",
        lambda _: proxy.ACCEPTED_BASELINE_SHA256,
    )

    with pytest.raises(proxy.Out07DirectionProxyError, match="strict exact route"):
        proxy._assert_exact_baseline_absent(tmp_path)


def test_proxy_rejects_non_exact_media_at_strict_input_locator(tmp_path: Path) -> None:
    baseline = tmp_path / proxy.STRICT_EXACT_BASELINE_LOCATORS[0]
    baseline.parent.mkdir(parents=True)
    baseline.write_bytes(b"not-the-accepted-baseline")

    with pytest.raises(proxy.Out07DirectionProxyError, match="non-exact media"):
        proxy._assert_exact_baseline_absent(tmp_path)


@pytest.mark.parametrize(
    ("cover", "source", "rendered", "expected"),
    [
        (
            proxy.PLANNER_COVER_SHA256,
            proxy.PLANNER_SOURCE_FRAME_FINGERPRINT,
            proxy.PLANNER_BASELINE_FRAME_FINGERPRINT,
            "cover_visual_exact_reconstitution",
        ),
        (
            "0" * 64,
            proxy.PLANNER_SOURCE_FRAME_FINGERPRINT,
            proxy.PLANNER_BASELINE_FRAME_FINGERPRINT,
            "cover_pixel_equivalent_proxy",
        ),
        (
            "0" * 64,
            "1" * 64,
            "2" * 64,
            "cover_direction_semantic_proxy",
        ),
    ],
)
def test_proxy_classification_never_hides_hash_drift(
    cover: str, source: str, rendered: str, expected: str
) -> None:
    assert (
        proxy.classify_proxy(
            proxy_sha256=cover,
            source_frame_fingerprint=source,
            proxy_frame_fingerprint=rendered,
        )
        == expected
    )


def test_caption_mapping_rejects_text_hash_or_timing_drift() -> None:
    subtitle = {
        "id": proxy.SUBTITLE_ID,
        "cut_id": proxy.CUT_ID,
        "text": "drift",
        "source_start_seconds": proxy.SUBTITLE_SOURCE_START_SECONDS,
        "source_end_seconds": proxy.SUBTITLE_SOURCE_END_SECONDS,
        "sequence_start_seconds": proxy.SUBTITLE_SEQUENCE_START_SECONDS,
        "sequence_end_seconds": proxy.SUBTITLE_SEQUENCE_END_SECONDS,
    }
    contract = {
        "id": proxy.SUBTITLE_ID,
        "text_sha256": proxy.SUBTITLE_TEXT_SHA256,
    }
    cut = {
        "id": proxy.CUT_ID,
        "source_start_seconds": 22.606,
        "sequence_start_seconds": 11.678,
    }
    with pytest.raises(proxy.Out07DirectionProxyError, match="text hash"):
        proxy._validate_mapping(
            subtitle=subtitle,
            contract_subtitle=contract,
            cut=cut,
        )


def test_review_html_has_one_question_and_required_order_only() -> None:
    html = proxy._render_html(
        {"proxy_classification": "cover_direction_semantic_proxy"}
    )
    assert html.count(proxy.REVIEW_QUESTION) == 1
    ordered = (
        "cover_list_preview.jpg",
        proxy.PROXY_FILE,
        "cover_shorts_ui_overlay_preview.jpg",
        "cover_center_4x5.jpg",
        proxy.MAPPED_SOURCE_FILE,
        "evidence / readback",
        proxy.REVIEW_QUESTION,
    )
    positions = [html.index(value) for value in ordered]
    assert positions == sorted(positions)
    assert "reinstantiated_baseline.mp4" not in html
    assert "poster_A_1080x1920.jpg" not in html
    assert "poster_B_1080x1920.jpg" not in html
    assert "poster_C_1080x1920.jpg" not in html
    assert "overflow-x:hidden" in html


def test_readback_separates_historical_acceptance_from_proxy_review() -> None:
    context = {
        "actual_decode_timestamp": proxy.SOURCE_TIMESTAMP_SECONDS,
        "layout": {
            "diagnostic_ass_style": {
                "candidate_id": "ed10l_keifont_pop_dialogue_candidate",
                "font_name": "Keifont",
                "font_file_status": "candidate_primary_font_file_found",
            }
        },
        "source_probe": {
            "duration_seconds": 164.768798,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
        },
    }
    readback = proxy._readback_payload(
        context=context,
        proxy_sha="a" * 64,
        source_fingerprint="b" * 64,
        proxy_fingerprint="c" * 64,
        classification="cover_direction_semantic_proxy",
        neighborhood=[],
    )
    assert readback["exact_baseline_available"] is False
    assert readback["accepted_baseline_status"] == "accepted_historical_fact"
    assert readback["baseline_acceptance_reopened"] is False
    assert readback["cover_direction_review_available"] is True
    assert readback["cover_direction_acceptance"] == "pending"
    assert readback["byte_equivalence_claimed"] is False
    assert readback["source_frame_only"] is True
    assert readback["existing_subtitle_only"] is True
    assert readback["poster_added_abstract_background"] is False
    assert readback["poster_added_auxiliary_text"] is False
    assert readback["masks_used"] is False
    assert readback["third_party_pixels_used"] is False
    assert readback["rights_status"] == "pending"
    assert readback["production_acceptance"] is False
    assert readback["public_or_publishing_acceptance"] is False
    assert readback["all_external_attempts"] is False
    assert "text" not in readback["subtitle_authority"]

    core = proxy._deterministic_core(readback)
    assert "local_host_receipt" not in core
    assert proxy._canonical_digest(core) == proxy._canonical_digest(core)


def test_two_build_byte_drift_stops_before_promotion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    episode = tmp_path / "episodes" / proxy.EPISODE_ID
    episode.mkdir(parents=True)
    monkeypatch.setattr(
        proxy.strict,
        "_resolve_executable",
        lambda *_: "fixture-tool",
    )
    monkeypatch.setattr(proxy, "_validate_inputs", lambda **_: {})
    builds = iter(
        (
            {
                "core_digest": "c" * 64,
                "package_digest": "d" * 64,
                "file_hashes": {"index.html": "1" * 64},
            },
            {
                "core_digest": "c" * 64,
                "package_digest": "d" * 64,
                "file_hashes": {"index.html": "2" * 64},
            },
        )
    )
    monkeypatch.setattr(proxy, "_build_once", lambda **_: next(builds))
    promoted: list[bool] = []
    monkeypatch.setattr(
        proxy,
        "_promote_validated_package",
        lambda **_: promoted.append(True),
    )

    with pytest.raises(proxy.Out07DirectionProxyError, match="package bytes changed"):
        proxy.build_out07_direction_proxy(
            episode_dir=episode,
            verify_determinism=True,
            base_dir=tmp_path,
        )
    assert promoted == []


def test_manifest_detects_tampering(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("stable", encoding="utf-8")
    proxy._write_manifest(
        tmp_path,
        core_digest="c" * 64,
        package_digest="d" * 64,
    )
    payload = proxy.validate_manifest(tmp_path / proxy.MANIFEST_FILE)
    assert payload["manifest_self_integrity"]["status"] == "passed"

    (tmp_path / "index.html").write_text("changed", encoding="utf-8")
    with pytest.raises(proxy.Out07DirectionProxyError, match="manifest mismatch"):
        proxy.validate_manifest(tmp_path / proxy.MANIFEST_FILE)


def test_failed_promotion_restores_prior_proxy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "proxy"
    output.mkdir()
    (output / "marker.txt").write_text("prior", encoding="utf-8")
    stage = tmp_path / ".proxy.proxy-pass-test"
    stage.mkdir()
    (stage / "marker.txt").write_text("new", encoding="utf-8")

    def fail_validation(_: Path) -> None:
        raise proxy.Out07DirectionProxyError("fixture validation failure")

    monkeypatch.setattr(proxy, "_validate_promoted_package", fail_validation)
    with pytest.raises(proxy.Out07DirectionProxyError, match="fixture validation"):
        proxy._promote_validated_package(stage=stage, output=output)
    assert (output / "marker.txt").read_text(encoding="utf-8") == "prior"


def test_cli_exposes_direction_proxy_without_replacing_exact_route(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli_main.main(["--help"]) == 0
    help_text = capsys.readouterr().out
    assert "build-out07-direction-proxy" in help_text
    assert "reconstitute-out07-review" in help_text

    with pytest.raises(SystemExit) as exc:
        cli_main.main(["build-out07-direction-proxy", "--help"])
    assert exc.value.code == 0
    sub_help = capsys.readouterr().out
    assert "--verify-determinism" in sub_help
    assert "--episode-dir" in sub_help


def test_contract_snapshot_contains_no_caption_plaintext() -> None:
    contract = json.loads(
        Path("artifacts/ACTIVE_REBUILD.json").read_text(encoding="utf-8")
    )
    row = next(
        item
        for item in contract["semantic_authority_snapshot"]["subtitles"]
        if item["id"] == proxy.SUBTITLE_ID
    )
    assert row["text_sha256"] == proxy.SUBTITLE_TEXT_SHA256
    assert "text" not in row
    assert "wrapped_lines" not in row
