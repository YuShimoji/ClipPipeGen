"""INT-02 source audio fetch contract tests."""

from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

from src.cli import fetch_source_audio
from src.integrations.asset_fetch import fake_audio
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


def test_fetch_source_audio_local_media_audio_uses_ffmpeg_adapter_without_real_ffmpeg(
    tmp_path: Path,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)
    source_media = tmp_path / "input local.mov"
    source_media.write_bytes(b"local media placeholder")

    def fake_normalize_local_media_audio(*, input_path, output_path, ffmpeg_path):
        assert Path(input_path) == source_media
        assert ffmpeg_path == "C:/tools/ffmpeg.exe"
        fake_audio.write_silent_wav(output_path, duration_seconds=2.0)
        return fetch_source_audio.ffmpeg_audio.NormalizeResult(
            ffmpeg_path="C:/tools/ffmpeg.exe",
            ffmpeg_path_source="argument",
            ffmpeg_version="ffmpeg version test",
            command=[
                "C:/tools/ffmpeg.exe",
                "-y",
                "-i",
                str(source_media),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-sample_fmt",
                "s16",
                "-acodec",
                "pcm_s16le",
                str(ep_dir / "materials" / "src_audio_local" / "source.wav"),
            ],
            command_summary="C:/tools/ffmpeg.exe -y -i input local.mov ... source.wav",
            exit_code=0,
            stderr_digest={
                "algorithm": "sha256",
                "sha256": "0" * 64,
                "tail": "ok",
                "tail_chars": 800,
                "truncated": False,
            },
            duration_seconds=2.0,
            warnings=[
                "input duration is not probed in INT-02c; "
                "output WAV duration is read after normalization"
            ],
        )

    monkeypatch.setattr(
        fetch_source_audio.ffmpeg_audio,
        "normalize_local_media_audio",
        fake_normalize_local_media_audio,
    )

    result = fetch_source_audio.run(
        [
            "--episode-id",
            "ep_audio",
            "--root",
            str(root),
            "--local-media",
            str(source_media),
            "--material-id",
            "src_audio_local",
            "--mode",
            "local-media-audio",
            "--ffmpeg-path",
            "C:/tools/ffmpeg.exe",
        ]
    )

    assert result == 0
    material_dir = ep_dir / "materials" / "src_audio_local"
    audio_path = material_dir / "source.wav"
    sidecar_path = material_dir / "sidecar.json"
    receipt_path = material_dir / "fetch_receipt.json"

    with wave.open(str(audio_path), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getframerate() == 16000
        assert wav.getsampwidth() == 2
        assert wav.getnframes() == 32000

    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["source"]["url"] is None
    assert sidecar["source"]["local_path"] == str(source_media)
    assert sidecar["source"]["retrieval_method"] == "asset_fetch_local_media_audio"

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["mode"] == "local-media-audio"
    assert receipt["provider"] == "local-media"
    assert receipt["source_url"] is None
    assert receipt["tools"] == [
        {
            "name": "ffmpeg",
            "path": "C:/tools/ffmpeg.exe",
            "path_source": "argument",
            "version": "ffmpeg version test",
        }
    ]
    assert receipt["commands"] == [
        {
            "summary": "C:/tools/ffmpeg.exe -y -i input local.mov ... source.wav",
            "exit_code": 0,
        }
    ]
    assert receipt["input"]["source_url"] is None
    assert receipt["input"]["local_path"] == str(source_media).replace("\\", "/")
    assert receipt["outputs"][0]["duration_seconds"] == 2.0
    assert receipt["warnings"]
    assert receipt["stderr_digest"]["tail"] == "ok"
    assert receipt["rollback"]["files"] == [
        receipt["preflight"]["output_path"],
        receipt["preflight"]["sidecar_path"],
        receipt["preflight"]["receipt_path"],
    ]

    ledger = load_ledger(ep_dir / "material_ledger.json")
    entry = ledger["materials"][0]
    assert entry["id"] == "src_audio_local"
    assert entry["kind"] == "source_audio"
    assert entry["subkind"] == "wav_pcm_16k_mono"
    assert entry["intended_uses"] == ["editing_audio"]


def test_fetch_source_audio_local_media_audio_dry_run_writes_nothing(
    tmp_path: Path,
    capsys,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)
    source_media = tmp_path / "input.mp4"
    source_media.write_bytes(b"local media placeholder")

    def fail_if_called(**_kwargs):
        raise AssertionError("dry-run must not run FFmpeg normalization")

    monkeypatch.setattr(
        fetch_source_audio.ffmpeg_audio,
        "normalize_local_media_audio",
        fail_if_called,
    )

    result = fetch_source_audio.run(
        [
            "--episode-id",
            "ep_audio",
            "--root",
            str(root),
            "--local-media",
            str(source_media),
            "--material-id",
            "src_audio_local",
            "--mode",
            "local-media-audio",
            "--ffmpeg-path",
            "C:/tools/ffmpeg.exe",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert result == 0
    assert payload["will_write"] is False
    assert payload["will_call_subprocess"] is False
    assert payload["local_media_exists"] is True
    assert payload["command_plan"]["ffmpeg_path"] == "C:/tools/ffmpeg.exe"
    assert payload["command_plan"]["path_source"] == "argument"
    assert payload["command_plan"]["command"]
    assert not (ep_dir / "materials").exists()
    assert not (ep_dir / "material_ledger.json").exists()


def test_fetch_source_audio_local_media_audio_rejects_source_url(tmp_path: Path):
    root, _ = _prepare_episode(tmp_path)
    source_media = tmp_path / "input.mp4"
    source_media.write_bytes(b"local media placeholder")

    result = _run_cli(
        [
            "fetch-source-audio",
            "--episode-id",
            "ep_audio",
            "--root",
            str(root),
            "--source-url",
            "https://www.youtube.com/watch?v=AAA",
            "--local-media",
            str(source_media),
            "--material-id",
            "src_audio_local",
            "--mode",
            "local-media-audio",
        ]
    )

    assert result.returncode == 2
    assert "does not accept --source-url" in result.stderr


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
