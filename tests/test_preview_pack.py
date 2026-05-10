"""SH-05: local preview pack orchestrator."""

from __future__ import annotations

import json
import wave
from datetime import datetime, timezone
from pathlib import Path

from src.cli import build_local_preview_pack
from src.pipeline import preview_pack
from src.pipeline.material_ledger import compute_sha256


def _write_input(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"local media placeholder")


def _install_fake_fetch(monkeypatch) -> None:
    def fake_fetch(argv: list[str]) -> int:
        root = Path(_arg(argv, "--root"))
        episode_id = _arg(argv, "--episode-id")
        material_id = _arg(argv, "--material-id")
        local_media = _arg(argv, "--local-media")
        ep_dir = root / episode_id
        material_dir = ep_dir / "materials" / material_id
        material_dir.mkdir(parents=True, exist_ok=True)
        audio = material_dir / "source.wav"
        with wave.open(str(audio), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\0\0" * 16000)
        sha = compute_sha256(audio)
        sidecar = material_dir / "sidecar.json"
        sidecar.write_text(json.dumps({"asset_id": material_id}), encoding="utf-8")
        receipt = material_dir / "fetch_receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema_version": "v1",
                    "episode_id": episode_id,
                    "material_id": material_id,
                    "mode": "local-media-audio",
                    "provider": "local-media",
                    "input": {"source_url": None, "local_path": local_media},
                    "outputs": [{"path": str(audio), "sha256": sha, "duration_seconds": 1.0}],
                    "warnings": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        now = datetime.now(timezone.utc).isoformat()
        ledger = {
            "schema_version": "v1",
            "episode_id": episode_id,
            "created_at": now,
            "updated_at": now,
            "materials": [
                {
                    "id": material_id,
                    "kind": "source_audio",
                    "subkind": "wav_pcm_16k_mono",
                    "file_path": str(audio).replace("\\", "/"),
                    "sidecar_path": str(sidecar).replace("\\", "/"),
                    "hash_sha256": sha,
                    "byte_size": audio.stat().st_size,
                    "intended_uses": ["editing_audio"],
                    "registered_at": now,
                    "registered_by": "test",
                    "compliance_link": {
                        "rights_manifest_id": episode_id,
                        "compliance_status_at_registration": "pending",
                    },
                }
            ],
        }
        (ep_dir / "material_ledger.json").write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return 0

    monkeypatch.setattr(build_local_preview_pack.fetch_source_audio, "run", fake_fetch)


def _arg(argv: list[str], name: str) -> str:
    return argv[argv.index(name) + 1]


def test_build_local_preview_pack_creates_manifest_report_and_fake_transcript(
    tmp_path: Path,
    monkeypatch,
):
    _install_fake_fetch(monkeypatch)
    media = tmp_path / "input.wav"
    _write_input(media)
    root = tmp_path / "episodes"

    result = build_local_preview_pack.run(
        [
            "--episode-id",
            "ep_preview",
            "--root",
            str(root),
            "--local-media",
            str(media),
            "--material-id",
            "src_audio_preview",
        ]
    )

    assert result == 0
    ep_dir = root / "ep_preview"
    manifest = json.loads((ep_dir / "preview_manifest.json").read_text(encoding="utf-8"))
    report = (ep_dir / "preview_report.html").read_text(encoding="utf-8")

    assert (ep_dir / "materials" / "src_audio_preview" / "source.wav").exists()
    assert (ep_dir / "transcript.json").exists()
    assert (ep_dir / "edit_pack.json").exists()
    assert (ep_dir / "_preview_pack" / "deterministic_fake_segments.json").exists()
    assert manifest["input"]["kind"] == "local_media_file"
    assert manifest["material"]["material_id"] == "src_audio_preview"
    assert manifest["transcript"]["source"] == "deterministic_fake"
    assert manifest["transcript"]["not_for_acceptance"] is True
    assert manifest["cuts"]["candidate_count"] == 1
    assert manifest["subtitles"]["subtitle_count"] == 1
    assert preview_pack.validate_preview_manifest(manifest) == []
    assert "rights status is pending; this is readback only" in manifest["warnings"]
    assert "Status Summary" in report
    assert "Artifact Links" in report
    assert "Decision Warnings" in report
    assert "warning-panel" in report
    assert "deterministic_fake transcript is not acceptance material." in report
    assert "transcript.not_for_acceptance is true." in report
    assert "rights pending is readback only." in report
    assert "preview_manifest.json" in report
    assert "fetch_receipt.json" in report
    assert "transcript.json" in report
    assert "edit_pack.json" in report
    assert "<audio controls" in report
    assert "<button" not in report.lower()
    assert "<form" not in report.lower()
    assert "<video" not in report.lower()


def test_build_local_preview_pack_accepts_fixture_transcript(
    tmp_path: Path,
    monkeypatch,
):
    _install_fake_fetch(monkeypatch)
    media = tmp_path / "input.wav"
    fixture = tmp_path / "segments.json"
    _write_input(media)
    fixture.write_text(
        json.dumps(
            [
                {
                    "id": "seg_fixture_001",
                    "start_seconds": 0.0,
                    "end_seconds": 1.0,
                    "text": "ここが見どころです",
                }
            ]
        ),
        encoding="utf-8",
    )
    root = tmp_path / "episodes"

    result = build_local_preview_pack.run(
        [
            "--episode-id",
            "ep_fixture",
            "--root",
            str(root),
            "--local-media",
            str(media),
            "--material-id",
            "src_audio_fixture",
            "--transcript-fixture",
            str(fixture),
        ]
    )

    assert result == 0
    manifest = json.loads((root / "ep_fixture" / "preview_manifest.json").read_text(encoding="utf-8"))
    assert manifest["transcript"]["source"] == "fixture"
    assert manifest["transcript"]["not_for_acceptance"] is True
    assert not (root / "ep_fixture" / "_preview_pack" / "deterministic_fake_segments.json").exists()
    report = (root / "ep_fixture" / "preview_report.html").read_text(encoding="utf-8")
    assert "fixture transcript is not acceptance material." in report
    assert "ここが見どころです" in report
    assert "Not for acceptance" in report
    assert "Rights status" in report


def test_build_local_preview_pack_medium_japanese_fixture_keeps_report_readable(
    tmp_path: Path,
    monkeypatch,
):
    _install_fake_fetch(monkeypatch)
    media = tmp_path / "input.wav"
    fixture = tmp_path / "segments_medium_ja.json"
    _write_input(media)
    fixture.write_text(
        json.dumps(
            [
                {
                    "id": "seg_medium_001",
                    "start_seconds": 0.0,
                    "end_seconds": 1.0,
                    "text": "冒頭で配信者が今日の企画を説明し、視聴者の反応を拾いながら期待感を作ります。",
                    "confidence": 0.91,
                },
                {
                    "id": "seg_medium_002",
                    "start_seconds": 1.1,
                    "end_seconds": 2.2,
                    "text": "途中で予想外のコメントに気づき、笑いながら流れを変える場面があります。",
                    "confidence": 0.88,
                },
                {
                    "id": "seg_medium_003",
                    "start_seconds": 2.4,
                    "end_seconds": 3.5,
                    "text": "ここは切り抜き候補として見せ場が明確で、字幕案でも意味が崩れにくい部分です。",
                    "confidence": 0.9,
                },
                {
                    "id": "seg_medium_004",
                    "start_seconds": 3.6,
                    "end_seconds": 4.8,
                    "text": "最後に次の展開へつながる一言があり、文脈確認の材料としても使えます。",
                    "confidence": 0.87,
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    root = tmp_path / "episodes"

    result = build_local_preview_pack.run(
        [
            "--episode-id",
            "ep_medium_ja",
            "--root",
            str(root),
            "--local-media",
            str(media),
            "--material-id",
            "src_audio_medium_ja",
            "--transcript-fixture",
            str(fixture),
        ]
    )

    assert result == 0
    ep_dir = root / "ep_medium_ja"
    manifest = json.loads((ep_dir / "preview_manifest.json").read_text(encoding="utf-8"))
    report = (ep_dir / "preview_report.html").read_text(encoding="utf-8")

    assert preview_pack.validate_preview_manifest(manifest) == []
    assert manifest["transcript"]["source"] == "fixture"
    assert manifest["transcript"]["segment_count"] == 4
    assert manifest["transcript"]["not_for_acceptance"] is True
    assert manifest["cuts"]["candidate_count"] >= 1
    assert manifest["subtitles"]["subtitle_count"] == 4
    assert "ここは切り抜き候補として見せ場が明確" in report
    assert "fixture transcript is not acceptance material." in report
    assert "rights pending is readback only." in report
    assert "preview_manifest.json" in report
    assert "fetch_receipt.json" in report
    assert "<audio controls" in report
    assert "<button" not in report.lower()
    assert "<form" not in report.lower()
    assert "<video" not in report.lower()


def test_preview_manifest_validation_reports_schema_issues():
    issues = preview_pack.validate_preview_manifest(
        {
            "schema_version": "v0",
            "episode_id": "",
            "input": {"kind": "url"},
            "transcript": {"source": "fixture", "not_for_acceptance": False},
            "warnings": "not-a-list",
        }
    )

    assert "schema_version must be v1" in issues
    assert "episode_id must be a non-empty string" in issues
    assert "input.kind must be local_media_file" in issues
    assert "transcript.not_for_acceptance must be true" in issues
    assert "warnings must be a list" in issues


def test_build_local_preview_pack_rejects_url_input(tmp_path: Path):
    result = build_local_preview_pack.run(
        [
            "--episode-id",
            "ep_url",
            "--root",
            str(tmp_path / "episodes"),
            "--local-media",
            "https://example.test/watch",
            "--material-id",
            "src_audio_url",
        ]
    )

    assert result == 1


def test_build_local_preview_pack_refuses_existing_artifacts_without_force(
    tmp_path: Path,
    monkeypatch,
):
    _install_fake_fetch(monkeypatch)
    media = tmp_path / "input.wav"
    _write_input(media)
    root = tmp_path / "episodes"
    args = [
        "--episode-id",
        "ep_conflict",
        "--root",
        str(root),
        "--local-media",
        str(media),
        "--material-id",
        "src_audio_conflict",
    ]

    assert build_local_preview_pack.run(args) == 0
    assert build_local_preview_pack.run(args) == 1
    assert build_local_preview_pack.run([*args, "--force"]) == 0
