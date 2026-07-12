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
    assert readback["gates"]["public_or_publishing_acceptance"] is False
    manifest = json.loads((output / "delivery_manifest.json").read_text(encoding="utf-8"))
    assert {item["package_relative_path"] for item in manifest["files"]} == set(
        odp.REQUIRED_PACKAGE_FILES
    ) - {"delivery_manifest.json"}
    assert manifest["manifest_self_integrity"]["sha256"] == odp._canonical_manifest_self_hash(
        manifest
    )


def test_operator_delivery_pack_separates_copy_from_operator_state(
    tmp_path: Path, monkeypatch
) -> None:
    fixture = _fixture(tmp_path, monkeypatch)
    odp.build_operator_delivery_pack(
        episode_dir=fixture["episode"],
        output_dir=fixture["output"],
        out06_readback_path=fixture["out06_readback"],
        base_dir=fixture["root"],
        runner=_fake_runner,
    )
    output = fixture["output"]
    publish = json.loads((output / "publish_draft.json").read_text(encoding="utf-8"))

    required = {
        "schema_version",
        "artifact_id",
        "episode_id",
        "status",
        "language",
        "title",
        "description",
        "tags",
        "evidence_trace",
        "video",
        "selected_thumbnail",
        "source_attribution_status",
        "source_title",
        "source_url",
        "operator_copy_ready",
        "publish_ready",
        "rights_status",
        "production_acceptance",
        "production_subtitle_design_acceptance",
        "public_or_publishing_acceptance",
        "upload_attempted",
        "thumbnail_upload_attempted",
        "metadata_update_attempted",
        "visibility_update_attempted",
        "visibility",
        "made_for_kids",
        "scheduled_at",
    }
    assert required <= publish.keys()
    assert publish["artifact_id"] == odp.ARTIFACT_ID
    assert publish["episode_id"] == "jp_pilot01_hololive_bancho_20260525"
    assert publish["title"] == "番長、団長を呼び出すも来ない！？"
    assert len(publish["description"].splitlines()) == 3
    assert publish["tags"] == [
        "ホロライブ",
        "はじめ",
        "番長",
        "団長",
        "体育館裏",
        "呼び出し",
        "来なかった理由",
    ]
    assert len(publish["evidence_trace"]) == 4
    assert all(item["subtitle_ids"] for item in publish["evidence_trace"])
    assert all(item["source_segment_ids"] for item in publish["evidence_trace"])
    assert publish["video"]["sha256"] == odp._sha256(
        output / "assets" / "complete_narrative_short.mp4"
    )
    selected = publish["selected_thumbnail"]
    assert selected == {
        "candidate_id": "tension",
        "path": odp._relative(
            output / "assets" / "thumbnail_recommended_1280x720.jpg", fixture["root"]
        ),
        "sha256": odp._sha256(output / "assets" / "thumbnail_recommended_1280x720.jpg"),
        "source_cut_id": "cut_003",
        "source_seconds": 25.35,
        "evidence": {
            "subtitle_ids": ["sub_013", "sub_014"],
            "segment_ids": ["seg_000013", "seg_000014"],
        },
    }
    copied = "\n".join([publish["title"], publish["description"], *publish["tags"]]).lower()
    for banned in (
        "内部確認用",
        "operator判断前",
        "公開判断ではありません",
        "未実施",
        "visibility",
        "made for kids",
        "ショート候補",
        "内部レビュー",
    ):
        assert banned.lower() not in copied
    assert publish["source_attribution_status"] == "operator_decision_required"
    assert publish["source_title"] is None
    assert publish["source_url"] is None
    assert publish["operator_copy_ready"] is True
    assert publish["publish_ready"] is False
    assert publish["public_or_publishing_acceptance"] is False

    html = (output / "index.html").read_text(encoding="utf-8")
    assert html.index('id="recommended"') < html.index('id="copy-metadata"')
    assert html.index('id="copy-metadata"') < html.index('id="accepted-video"')
    assert html.index('id="accepted-video"') < html.index('id="operator-status"')
    assert html.index('id="operator-status"') < html.index("<details>")
    assert html.count("<details") == 1
    assert "<details open" not in html
    assert html.count("data-copy-target=") == 3
    assert html.count(">コピー</button>") == 3
    assert "コピーしました：" in html
    assert "テキストを選択しました。Ctrl+Cでコピーしてください。" in html
    assert "採用済みOUT-06動画" in html
    assert "推奨tensionサムネが内容を正しく魅力的に伝え、誤認や過度な煽りがないか。" in html
    assert "title・description・tagsが自然で内容と一致するか。" in html
    assert (
        "一ページでコピー・画像・動画・根拠を確認でき、operator packとして使いやすいか。"
        in html
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
