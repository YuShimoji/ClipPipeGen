from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.integrations.render import out07_native_cover as native


def test_native_cover_route_fixes_accepted_baseline_and_one_frame() -> None:
    assert native.ARTIFACT_ID == (
        "clip-out07-shorts-poster-frame-direction-proof-v0-001"
    )
    assert native.STATE == (
        "OUT07_REINSTANTIATED_BASELINE_ACCEPTED_NATIVE_SHORTS_COVER_"
        "OPERATOR_PACK_REVIEW_READY"
    )
    assert native.ACCEPTED_BASELINE_SHA256 == (
        "2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18"
    )
    assert len(native.FRAME_SURVEY) == 3
    recommended = [item for item in native.FRAME_SURVEY if item["recommended"]]
    assert recommended == [native.FRAME_SURVEY[0]]
    assert recommended[0]["baseline_seconds"] == 11.93
    assert recommended[0]["subtitle_id"] == "sub_010"


def test_acceptance_is_explicit_and_does_not_inherit_historical_out06() -> None:
    output = (
        Path("episodes") / native.EPISODE_ID / "review" / native.DEFAULT_OUTPUT_NAME
    )
    payload = native._baseline_acceptance_payload(output)

    assert payload["accepted_by"] == "Planner007"
    assert payload["acceptance_date"] == "2026-07-13 JST"
    assert payload["accepted_baseline"]["human_accepted"] is True
    assert payload["historical_acceptance_inheritance"] == {
        "byte_identical_to_historical_out06": False,
        "historical_out06_acceptance_inherited": False,
    }
    assert "rights_clearance" in payload["not_accepted"]
    assert "public_or_publishing_acceptance" in payload["not_accepted"]


def test_publish_gates_remain_closed_and_attempts_false() -> None:
    gates = native._closed_gates()
    attempts = native._attempt_flags()

    assert all(item["status"] == "closed" for item in gates.values())
    assert gates["rights"]["rights_status"] == "pending"
    assert all(value is False for value in attempts.values())
    assert attempts["metadata_update_attempted"] is False
    assert attempts["visibility_update_attempted"] is False


def test_old_candidates_are_not_quality_rejected_or_returned() -> None:
    evidence = native._legacy_evidence_payload()

    assert evidence["historical_operator_directions"]["status"] == "user_rejected"
    assert evidence["historical_operator_directions"]["return_for_selection"] is False
    for item in evidence["current_review_candidates"]:
        assert item["status"] == "superseded_by_user_short_context_reframe"
        assert item["quality_rejection"] is False
        assert item["return_for_selection"] is False


def test_review_html_has_one_question_and_cover_first_order() -> None:
    publish = {
        "title": "title",
        "description": "description",
        "tags": ["tag"],
        "evidence_trace": ["fixture"],
    }
    html = native._render_html({}, publish)

    assert html.count(native.REVIEW_QUESTION) == 1
    assert html.count("<video ") == 1
    assert html.index("cover_list_preview.jpg") < html.index(
        "cover_shorts_ui_overlay_preview.jpg"
    )
    assert html.index("cover_shorts_ui_overlay_preview.jpg") < html.index(
        "native_shorts_cover_1080x1920.png"
    )
    assert html.index("native_shorts_cover_1080x1920.png") < html.index(
        "cover_center_4x5.jpg"
    )
    assert html.index("cover_center_4x5.jpg") < html.index(
        "mapped_source_frame_1920x1080.png"
    )
    assert html.index("mapped_source_frame_1920x1080.png") < html.index(
        "reinstantiated_baseline.mp4"
    )
    assert "A/B/Cから選" not in html
    assert "baselineを受理" not in native.REVIEW_QUESTION
    assert "rightsを承認" not in native.REVIEW_QUESTION
    assert html.index("reinstantiated_baseline.mp4") < html.index(
        native.REVIEW_QUESTION
    )


def test_manifest_validates_files_and_self_integrity(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    native._write_manifest(tmp_path, core_digest="c" * 64, package_digest="d" * 64)

    payload = native.validate_manifest(tmp_path / "combined_review_manifest.json")
    assert payload["file_count"] == 2
    assert payload["manifest_self_integrity"]["status"] == "passed"

    (tmp_path / "a.txt").write_text("changed", encoding="utf-8")
    with pytest.raises(native.Out07NativeCoverError, match="manifest mismatch"):
        native.validate_manifest(tmp_path / "combined_review_manifest.json")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("state", "tampered", "self-integrity"),
        ("file_count", 3, "file_count"),
        ("deterministic_core_sha256", "0" * 64, "self-integrity"),
    ],
)
def test_manifest_rejects_metadata_tampering(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    native._write_manifest(tmp_path, core_digest="c" * 64, package_digest="d" * 64)
    path = tmp_path / "combined_review_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[field] = value
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(native.Out07NativeCoverError, match=message):
        native.validate_manifest(path)


def test_manifest_rejects_unlisted_file(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    native._write_manifest(tmp_path, core_digest="c" * 64, package_digest="d" * 64)
    (tmp_path / "unlisted.txt").write_text("extra", encoding="utf-8")

    with pytest.raises(native.Out07NativeCoverError, match="inventory mismatch"):
        native.validate_manifest(tmp_path / "combined_review_manifest.json")


def test_failed_promoted_package_validation_restores_prior_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "review"
    output.mkdir()
    (output / "prior.txt").write_text("accepted prior review", encoding="utf-8")
    stage = tmp_path / ".review.stage"
    stage.mkdir()
    (stage / "invalid.txt").write_text("invalid replacement", encoding="utf-8")

    def fail_validation(_: Path) -> None:
        raise native.Out07NativeCoverError("fixture validation failure")

    monkeypatch.setattr(native, "_validate_promoted_package", fail_validation)
    with pytest.raises(native.Out07NativeCoverError, match="fixture validation"):
        native._promote_validated_package(stage=stage, output=output)

    assert (output / "prior.txt").read_text(encoding="utf-8") == (
        "accepted prior review"
    )
    assert not stage.exists()
    assert list(tmp_path.glob(".review.backup-*")) == []
    assert list(tmp_path.glob(".review.failed-*")) == []


def test_publish_draft_preserves_flat_contract_and_source_frame_flags(
    tmp_path: Path,
) -> None:
    cover = tmp_path / "native_shorts_cover_1080x1920.png"
    cover.write_bytes(b"fixture cover")
    output = (
        Path("episodes") / native.EPISODE_ID / "review" / native.DEFAULT_OUTPUT_NAME
    )
    payload = native._publish_draft_payload(cover, output)
    reparsed = json.loads(json.dumps(payload))

    assert reparsed["schema_version"] == "clippipegen.out07.publish_draft.v0"
    assert reparsed["artifact_id"] == native.ARTIFACT_ID
    assert reparsed["title"]
    assert reparsed["description"]
    assert reparsed["tags"]
    assert reparsed["evidence_trace"]
    assert reparsed["video"]["sha256"] == native.ACCEPTED_BASELINE_SHA256
    assert reparsed["selected_thumbnail"] is None
    assert reparsed["publish_ready"] is False
    recommended = reparsed["recommended_cover"]
    assert recommended["source_frame_only"] is True
    assert recommended["poster_added_abstract_background"] is False
    assert recommended["poster_added_auxiliary_text"] is False
    assert recommended["source_frame_fingerprint"]["baseline_sha256"] == (
        native.BASELINE_FRAME_FINGERPRINT_SHA256
    )
    assert recommended["source_frame_fingerprint"]["mapped_source_sha256"] == (
        native.SOURCE_FRAME_FINGERPRINT_SHA256
    )


def test_operator_readback_contains_cover_source_and_exact_attempts(
    tmp_path: Path,
) -> None:
    cover = tmp_path / "native_shorts_cover_1080x1920.png"
    source_frame = tmp_path / "mapped_source_frame_1920x1080.png"
    baseline = tmp_path / "reinstantiated_baseline.mp4"
    cover.write_bytes(b"fixture cover")
    source_frame.write_bytes(b"fixture source")
    baseline.write_bytes(b"fixture baseline")
    output = (
        Path("episodes") / native.EPISODE_ID / "review" / native.DEFAULT_OUTPUT_NAME
    )
    publish = native._publish_draft_payload(cover, output)

    readback = native._operator_readback_payload(
        context={"reference_digest": "a" * 64},
        logical_output=output,
        cover=cover,
        source_frame=source_frame,
        baseline_copy=baseline,
        publish_draft=publish,
    )

    recommended = readback["recommended_cover"]
    assert recommended["source_frame_only"] is True
    assert recommended["source_frame_fingerprint"]["mapped_source_sha256"] == (
        native.SOURCE_FRAME_FINGERPRINT_SHA256
    )
    assert readback["source_comparison"]["frame_fingerprint_sha256"] == (
        native.SOURCE_FRAME_FINGERPRINT_SHA256
    )
    assert readback["attempts"]["metadata_update_attempted"] is False
    assert readback["attempts"]["visibility_update_attempted"] is False
