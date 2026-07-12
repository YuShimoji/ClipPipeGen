from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image

from src.integrations.render import operator_delivery_pack as odp


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path, monkeypatch) -> dict[str, Path]:
    root = tmp_path
    episode = root / "episodes" / "jp_pilot01_hololive_bancho_20260525"
    review = episode / "review"
    for relative in (
        "jp_pilot01r3_cut_review/human_preview_session",
        "out03_real_local_selected_cut_proof",
        "out04_editorial_representative_sequence",
        "out05_vertical_short_internal_candidate",
        "out06_complete_narrative_short_delivery_candidate/assets",
    ):
        path = review / relative
        path.mkdir(parents=True, exist_ok=True)
        (path / "protected.txt").write_text(relative, encoding="utf-8")

    out06_video = (
        review
        / "out06_complete_narrative_short_delivery_candidate"
        / "assets"
        / "complete_narrative_short.mp4"
    )
    out06_video.write_bytes(b"accepted-out06-video")
    source_video = episode / "materials" / "src_video_jp_pilot01" / "source_video.mp4"
    source_video.parent.mkdir(parents=True, exist_ok=True)
    source_video.write_bytes(b"source-video")
    monkeypatch.setattr(odp, "EXPECTED_OUT06_VIDEO_SHA256", odp._sha256(out06_video))
    monkeypatch.setattr(odp, "SOURCE_VIDEO_SHA256", odp._sha256(source_video))

    out06_readback = review / "out06_complete_narrative_short_delivery_candidate" / "candidate_readback.json"
    _write_json(
        out06_readback,
        {
            "artifact_id": odp.EXPECTED_OUT06_ARTIFACT_ID,
            "outputs": {
                "video": {
                    "path": odp._relative(out06_video, root),
                    "sha256": odp._sha256(out06_video),
                }
            },
        },
    )
    return {
        "root": root,
        "episode": episode,
        "out06_readback": out06_readback,
        "output": review / "out07_internal_operator_delivery_pack",
        "out06_video": out06_video,
    }


def _fake_runner(command, **_kwargs):
    frame_path = Path(command[-1])
    Image.new("RGB", (1280, 720), (70, 90, 120)).save(frame_path, format="PNG")
    return subprocess.CompletedProcess(command, 0, "", "")


def test_operator_delivery_pack_copies_video_and_builds_manifest(tmp_path: Path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)
    result = odp.build_operator_delivery_pack(
        episode_dir=fixture["episode"],
        output_dir=fixture["output"],
        out06_readback_path=fixture["out06_readback"],
        base_dir=fixture["root"],
        runner=_fake_runner,
    )
    output = fixture["output"]
    assert result["artifact_id"] == odp.ARTIFACT_ID
    assert all((output / relative).is_file() for relative in odp.REQUIRED_PACKAGE_FILES)
    assert (output / "assets" / "complete_narrative_short.mp4").read_bytes() == fixture[
        "out06_video"
    ].read_bytes()
    readback = json.loads((output / "operator_delivery_readback.json").read_text(encoding="utf-8"))
    assert readback["video"]["byte_identical_copy"] is True
    assert readback["video"]["rerendered"] is False
    assert readback["thumbnail"]["direction_count"] == 3
    assert readback["thumbnail"]["recommended_direction_id"] == "tension"
    assert readback["metadata"]["publish_ready"] is False
    assert readback["metadata"]["visibility"] == "operator_decision_required"
    manifest = json.loads((output / "delivery_manifest.json").read_text(encoding="utf-8"))
    assert {item["package_relative_path"] for item in manifest["files"]} == set(
        odp.REQUIRED_PACKAGE_FILES
    ) - {"delivery_manifest.json"}
    assert manifest["manifest_self_integrity"]["sha256"] == odp._canonical_manifest_self_hash(
        manifest
    )


def test_operator_delivery_pack_rejects_output_overlap(tmp_path: Path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)
    try:
        odp.build_operator_delivery_pack(
            episode_dir=fixture["episode"],
            output_dir=fixture["episode"] / "review" / "out06_complete_narrative_short_delivery_candidate",
            out06_readback_path=fixture["out06_readback"],
            base_dir=fixture["root"],
            runner=_fake_runner,
        )
    except odp.OperatorDeliveryPackError as exc:
        assert "start with out07" in str(exc) or "overlap" in str(exc)
    else:
        raise AssertionError("expected overlap rejection")
