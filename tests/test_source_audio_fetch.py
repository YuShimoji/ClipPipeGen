"""INT-02a: fake source audio fetch contract tests."""

from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

from src.pipeline.material_ledger import load_ledger
from src.pipeline.rights_manifest import (
    build_skeleton,
    save_rights_manifest,
    set_compliance_status,
)
from src.pipeline.transcript import load_transcript


REPO_ROOT = Path(__file__).resolve().parent.parent


def _rights_passed(episode_id: str) -> dict:
    manifest = build_skeleton(episode_id)
    manifest["source_video"].update(
        url="https://www.youtube.com/watch?v=AAA",
        title="source",
        channel="channel",
        channel_id="UC0001",
        vod_status="public",
    )
    manifest["talents"] = [
        {
            "name": "Talent",
            "agency": "hololive",
            "guideline_url": "https://www.hololive.tv/terms",
            "guideline_version_checked_at": "2026-05-10",
        }
    ]
    return set_compliance_status(manifest, status="passed", checked_by="user:tester")


def _prepare_episode(tmp_path: Path, episode_id: str = "ep_audio") -> tuple[Path, Path]:
    root = tmp_path / "episodes"
    ep_dir = root / episode_id
    ep_dir.mkdir(parents=True)
    save_rights_manifest(_rights_passed(episode_id), ep_dir / "rights_manifest.json")
    return root, ep_dir


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "src.cli.main", *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )


def _fetch_args(root: Path, episode_id: str, material_id: str = "src_audio_001") -> list[str]:
    return [
        "fetch-source-audio",
        "--episode-id",
        episode_id,
        "--root",
        str(root),
        "--source-url",
        "https://www.youtube.com/watch?v=AAA",
        "--material-id",
        material_id,
        "--mode",
        "fake",
    ]


def test_fetch_source_audio_fake_creates_wav_sidecar_receipt_and_ledger(tmp_path: Path):
    root, ep_dir = _prepare_episode(tmp_path)

    result = _run_cli(_fetch_args(root, "ep_audio"))

    assert result.returncode == 0, result.stderr
    material_dir = ep_dir / "materials" / "src_audio_001"
    audio_path = material_dir / "source.wav"
    sidecar_path = material_dir / "sidecar.json"
    receipt_path = material_dir / "fetch_receipt.json"
    ledger_path = ep_dir / "material_ledger.json"
    assert audio_path.exists()
    assert sidecar_path.exists()
    assert receipt_path.exists()
    assert ledger_path.exists()

    with wave.open(str(audio_path), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getframerate() == 16000
        assert wav.getsampwidth() == 2
        assert wav.getnframes() == 16000

    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["source"]["kind"] == "unverified"
    assert sidecar["source"]["retrieval_method"] == "asset_fetch_fake"
    assert sidecar["license"]["kind"] == "unknown"
    assert sidecar["usage_conditions"] == ["source_link_required"]

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["mode"] == "fake"
    assert receipt["provider"] == "asset_fetch_fake"
    assert receipt["tools"] == []
    assert receipt["commands"] == []
    assert receipt["input"] == {
        "source_url": "https://www.youtube.com/watch?v=AAA",
        "local_path": None,
    }
    assert receipt["outputs"] == [
        {
            "path": receipt["preflight"]["output_path"],
            "sha256": receipt["sha256"],
            "byte_size": receipt["byte_size"],
            "duration_seconds": 1.0,
        }
    ]
    assert receipt["warnings"] == []
    assert receipt["stderr_digest"] is None
    assert receipt["rollback"]["files"] == [
        receipt["preflight"]["output_path"],
        receipt["preflight"]["sidecar_path"],
        receipt["preflight"]["receipt_path"],
    ]

    ledger = load_ledger(ledger_path)
    assert len(ledger["materials"]) == 1
    entry = ledger["materials"][0]
    assert entry["id"] == "src_audio_001"
    assert entry["kind"] == "source_audio"
    assert entry["subkind"] == "wav_pcm_16k_mono"
    assert entry["intended_uses"] == ["editing_audio"]
    assert entry["compliance_link"]["compliance_status_at_registration"] == "passed"

    audit = _run_cli(
        [
            "audit-material-ledger",
            "--episode-id",
            "ep_audio",
            "--root",
            str(root),
            "--format",
            "json",
        ]
    )
    assert audit.returncode == 0, audit.stderr
    assert json.loads(audit.stdout)["ok"] is True


def test_fetch_source_audio_dry_run_writes_nothing(tmp_path: Path):
    root, ep_dir = _prepare_episode(tmp_path)

    result = _run_cli([*_fetch_args(root, "ep_audio"), "--dry-run"])

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["will_write"] is False
    assert payload["output_path"].endswith("materials/src_audio_001/source.wav")
    assert not (ep_dir / "materials").exists()
    assert not (ep_dir / "material_ledger.json").exists()


def test_fetch_source_audio_duplicate_material_id_fails_without_force(tmp_path: Path):
    root, _ = _prepare_episode(tmp_path)
    first = _run_cli(_fetch_args(root, "ep_audio"))
    assert first.returncode == 0, first.stderr

    duplicate = _run_cli(_fetch_args(root, "ep_audio"))

    assert duplicate.returncode != 0
    assert "refused to overwrite/register existing artifact" in duplicate.stderr
    assert "material_id=src_audio_001" in duplicate.stderr


def test_fetch_source_audio_missing_rights_manifest_fails(tmp_path: Path):
    root = tmp_path / "episodes"
    (root / "ep_audio").mkdir(parents=True)

    result = _run_cli(_fetch_args(root, "ep_audio"))

    assert result.returncode != 0
    assert "rights_manifest not found" in result.stderr


def test_fetch_source_audio_force_refreshes_same_material_and_preserves_others(tmp_path: Path):
    root, ep_dir = _prepare_episode(tmp_path)
    first = _run_cli(_fetch_args(root, "ep_audio", "src_audio_001"))
    second = _run_cli(_fetch_args(root, "ep_audio", "src_audio_002"))
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr

    forced = _run_cli([*_fetch_args(root, "ep_audio", "src_audio_001"), "--force"])

    assert forced.returncode == 0, forced.stderr
    ledger = load_ledger(ep_dir / "material_ledger.json")
    material_ids = sorted(m["id"] for m in ledger["materials"])
    assert material_ids == ["src_audio_001", "src_audio_002"]


def test_generated_source_audio_can_feed_transcribe_audio_fake(tmp_path: Path):
    root, ep_dir = _prepare_episode(tmp_path)
    fetched = _run_cli(_fetch_args(root, "ep_audio"))
    assert fetched.returncode == 0, fetched.stderr

    fixture_path = tmp_path / "segments.json"
    fixture_path.write_text(
        json.dumps(
            [
                {
                    "start_seconds": 0.0,
                    "end_seconds": 1.0,
                    "text": "素材契約から字幕へ",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    transcript_path = ep_dir / "transcript.json"
    audio_path = ep_dir / "materials" / "src_audio_001" / "source.wav"

    result = _run_cli(
        [
            "transcribe-audio",
            "--episode-id",
            "ep_audio",
            "--source-audio",
            str(audio_path),
            "--output",
            str(transcript_path),
            "--language",
            "ja",
            "--engine",
            "fake",
            "--fixture-segments",
            str(fixture_path),
            "--material-ledger",
            str(ep_dir / "material_ledger.json"),
            "--material-id",
            "src_audio_001",
        ]
    )

    assert result.returncode == 0, result.stderr
    transcript = load_transcript(transcript_path)
    assert transcript["source_audio"]["material_id"] == "src_audio_001"
    assert transcript["segments"][0]["text"] == "素材契約から字幕へ"
