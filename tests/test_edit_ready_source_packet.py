"""Edit-ready Source Packet contract and one-command orchestration tests."""

from __future__ import annotations

import json
import shutil
import wave
from pathlib import Path

import pytest

from src.cli import build_edit_ready_source_packet
from src.cli.main import SUBCOMMANDS
from src.pipeline.edit_ready_source_packet import (
    READY_STATE,
    SourcePacketBlocked,
    parse_youtube_json3_caption,
    sha256_file,
)
from src.pipeline.rights_manifest import build_skeleton, save_rights_manifest
from src.pipeline.transcript import build_transcript, save_transcript


def _caption(
    events: list[dict] | None = None,
) -> dict:
    return {
        "events": events
        or [
            {
                "id": "event-1",
                "tStartMs": 0,
                "dDurationMs": 4000,
                "segs": [{"utf8": "最初の字幕"}],
            },
            {
                "id": "event-2",
                "tStartMs": 4500,
                "dDurationMs": 3500,
                "segs": [{"utf8": "次の字幕"}],
            },
        ]
    }


def _parse(payload: dict, *, duration: float = 10.0, language: str = "ja"):
    return parse_youtube_json3_caption(
        payload,
        language=language,
        provider_locator="youtube-caption:video-id:ja",
        source_duration_seconds=duration,
    )


def test_caption_normalization_preserves_raw_event_mapping():
    segments, readback = _parse(_caption())

    assert len(segments) == 2
    assert segments[0]["text"] == "最初の字幕"
    assert "source_caption_event_id=event-1" in segments[0]["notes"]
    assert readback["coverage_ratio"] == 0.75
    assert readback["segment_count"] == 2


@pytest.mark.parametrize(
    ("events", "code"),
    [
        (
            [
                {
                    "id": "bad",
                    "tStartMs": -1,
                    "dDurationMs": 1000,
                    "segs": [{"utf8": "text"}],
                }
            ],
            "caption_time_range_invalid",
        ),
        (
            [
                {
                    "id": "later",
                    "tStartMs": 2000,
                    "dDurationMs": 1000,
                    "segs": [{"utf8": "later"}],
                },
                {
                    "id": "earlier",
                    "tStartMs": 1000,
                    "dDurationMs": 1000,
                    "segs": [{"utf8": "earlier"}],
                },
            ],
            "caption_order_invalid",
        ),
        (
            [
                {
                    "id": "same",
                    "tStartMs": 0,
                    "dDurationMs": 1000,
                    "segs": [{"utf8": "one"}],
                },
                {
                    "id": "same",
                    "tStartMs": 1000,
                    "dDurationMs": 1000,
                    "segs": [{"utf8": "two"}],
                },
            ],
            "caption_duplicate_id",
        ),
        (
            [
                {
                    "id": "empty",
                    "tStartMs": 0,
                    "dDurationMs": 1000,
                    "segs": [{"utf8": " \u200b "}],
                }
            ],
            "caption_text_empty",
        ),
        (
            [
                {
                    "id": "overflow",
                    "tStartMs": 9000,
                    "dDurationMs": 2000,
                    "segs": [{"utf8": "overflow"}],
                }
            ],
            "caption_outside_source_duration",
        ),
        (
            [
                {
                    "id": "tiny",
                    "tStartMs": 0,
                    "dDurationMs": 100,
                    "segs": [{"utf8": "tiny"}],
                }
            ],
            "caption_coverage_too_low",
        ),
    ],
)
def test_caption_validation_fails_closed(events: list[dict], code: str):
    with pytest.raises(SourcePacketBlocked) as exc:
        _parse({"events": events})

    assert exc.value.code == code


def test_caption_language_mismatch_fails_closed():
    with pytest.raises(SourcePacketBlocked) as exc:
        parse_youtube_json3_caption(
            _caption(),
            language="en",
            provider_locator="youtube-caption:video-id:ja",
            source_duration_seconds=10.0,
        )

    assert exc.value.code == "caption_language_mismatch"


def test_dispatcher_registers_one_command_source_packet():
    assert (
        SUBCOMMANDS["build-edit-ready-source-packet"]
        is build_edit_ready_source_packet.run
    )


def test_url_readback_scrubs_query_but_fingerprint_distinguishes_it():
    first = "https://example.com/video?id=one&token=secret-a"
    second = "https://example.com/video?id=one&token=secret-b"

    assert build_edit_ready_source_packet._safe_locator(first) == (
        "https://example.com/video"
    )
    assert build_edit_ready_source_packet._safe_locator(second) == (
        "https://example.com/video"
    )
    assert build_edit_ready_source_packet._locator_fingerprint(first) != (
        build_edit_ready_source_packet._locator_fingerprint(second)
    )


def test_one_command_build_resume_mismatch_and_integrity_guard(
    tmp_path: Path,
    monkeypatch,
):
    root, source, rights, caption = _inputs(tmp_path)
    calls = _install_fake_acquisition(monkeypatch)
    args = _args(root, source, rights, caption)

    assert build_edit_ready_source_packet.run(args) == 0
    assert calls == {"video": 1, "audio": 1}

    packet_dir = root / "packet-episode" / "source_packet" / "packet-001"
    packet_path = packet_dir / "source_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    report = (packet_dir / "source_packet_report.html").read_text(encoding="utf-8")
    assert packet["state"] == READY_STATE
    assert packet["authority"]["kind"] == "official_provider_caption"
    assert packet["normalized_transcript"]["segment_count"] == 2
    assert packet["normalized_transcript"]["coverage_ratio"] == 0.75
    assert packet["consumer_readiness"]["ready"] is True
    assert packet["acceptance_boundaries"]["rights_approval"] is False
    assert packet["acceptance_boundaries"]["public_or_publishing_readiness"] is False
    assert "<form" not in report
    assert "<button" not in report

    assert build_edit_ready_source_packet.run([*args, "--resume"]) == 0
    assert calls == {"video": 1, "audio": 1}

    source.write_bytes(b"different source input")
    assert build_edit_ready_source_packet.run([*args, "--resume"]) == 3
    assert calls == {"video": 1, "audio": 1}
    unchanged = json.loads(packet_path.read_text(encoding="utf-8"))
    assert unchanged["packet_integrity"] == packet["packet_integrity"]

    source.write_bytes(b"source input")
    normalized = packet_dir / "normalized_transcript.json"
    normalized.write_text("{}\n", encoding="utf-8")
    assert build_edit_ready_source_packet.run([*args, "--resume"]) == 3
    assert calls == {"video": 1, "audio": 1}


def test_fixture_transcript_is_blocked_before_acquisition(
    tmp_path: Path,
    monkeypatch,
):
    root, source, rights, _ = _inputs(tmp_path)
    calls = _install_fake_acquisition(monkeypatch)
    fixture_path = tmp_path / "fixture_transcript.json"
    fixture = build_transcript(
        "fixture-episode",
        source_audio_path="fixture.wav",
        source_audio_sha256="0" * 64,
        source_audio_duration_seconds=10.0,
        source_audio_sample_rate_hz=16000,
        source_audio_channels=1,
        language="ja",
        stt_engine="fake",
        stt_provider="fake",
        stt_engine_version="fake-v1",
        stt_params={},
        stt_warnings=[],
        segments=[
            {
                "id": "seg-1",
                "start_seconds": 0.0,
                "end_seconds": 5.0,
                "text": "fixture",
                "confidence": None,
                "speaker": None,
                "review_status": "unreviewed",
                "notes": [],
            }
        ],
        real_transcript=False,
    )
    save_transcript(fixture, fixture_path)

    result = build_edit_ready_source_packet.run(
        [
            "--packet-id",
            "packet-negative",
            "--episode-id",
            "packet-negative-episode",
            "--source-locator",
            str(source),
            "--source-identity",
            "local:fixture-negative",
            "--language",
            "ja",
            "--rights-manifest",
            str(rights),
            "--transcript",
            str(fixture_path),
            "--root",
            str(root),
            "--format",
            "json",
        ]
    )

    assert result == 3
    assert calls == {"video": 0, "audio": 0}
    blocked = json.loads(
        (
            root
            / "packet-negative-episode"
            / "source_packet"
            / "packet-negative"
            / "blocked_result.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        blocked["blocking_reason"]["code"]
        == "fixture_transcript_authority_forbidden"
    )
    assert blocked["consumer_readiness"]["ready"] is False


def _inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    root = tmp_path / "episodes"
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source input")
    rights = tmp_path / "rights.json"
    manifest = build_skeleton("source-rights")
    manifest["source_video"].update(
        url="https://www.youtube.com/watch?v=video-id",
        title="Packet source",
        channel="Source Channel",
        channel_id="UC_SOURCE",
        vod_status="public",
    )
    manifest["talents"] = [
        {
            "name": "Independent Source",
            "agency": "independent",
            "guideline_url": "https://example.com/source-guidelines",
            "guideline_version_checked_at": "2026-07-24",
        }
    ]
    save_rights_manifest(manifest, rights)
    caption = tmp_path / "caption.ja.json3"
    caption.write_text(
        json.dumps(_caption(), ensure_ascii=False),
        encoding="utf-8",
    )
    return root, source, rights, caption


def _args(root: Path, source: Path, rights: Path, caption: Path) -> list[str]:
    return [
        "--packet-id",
        "packet-001",
        "--episode-id",
        "packet-episode",
        "--source-locator",
        str(source),
        "--source-identity",
        "youtube:video-id",
        "--language",
        "ja",
        "--rights-manifest",
        str(rights),
        "--caption-track",
        str(caption),
        "--caption-authority",
        "provider_official",
        "--caption-provider-locator",
        "youtube-caption:video-id:ja",
        "--root",
        str(root),
        "--format",
        "json",
    ]


def _install_fake_acquisition(monkeypatch) -> dict[str, int]:
    calls = {"video": 0, "audio": 0}

    def fake_video(argv: list[str]) -> int:
        calls["video"] += 1
        root = Path(_arg(argv, "--root"))
        episode = _arg(argv, "--episode-id")
        source = Path(_arg(argv, "--source-path"))
        material_dir = root / episode / "materials" / "source_video"
        material_dir.mkdir(parents=True, exist_ok=True)
        output = material_dir / "source_video.mp4"
        shutil.copy2(source, output)
        _write_json(material_dir / "sidecar.json", {"asset_id": "source_video"})
        _write_json(
            material_dir / "fetch_receipt.json",
            {
                "mode": "local-media-video",
                "output_path": str(output),
                "sha256": sha256_file(output),
                "byte_size": output.stat().st_size,
                "video_metadata": {
                    "duration_seconds": 10.0,
                    "resolution": "1920x1080",
                },
                "warnings": [],
            },
        )
        _write_json(
            root / episode / "material_ledger.json",
            {"schema_version": "v1", "episode_id": episode, "materials": []},
        )
        return 0

    def fake_audio(argv: list[str]) -> int:
        calls["audio"] += 1
        root = Path(_arg(argv, "--root"))
        episode = _arg(argv, "--episode-id")
        material_dir = root / episode / "materials" / "source_audio"
        material_dir.mkdir(parents=True, exist_ok=True)
        output = material_dir / "source.wav"
        with wave.open(str(output), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\0\0" * 160000)
        _write_json(material_dir / "sidecar.json", {"asset_id": "source_audio"})
        _write_json(
            material_dir / "fetch_receipt.json",
            {
                "mode": "local-media-audio",
                "output_path": str(output),
                "sha256": sha256_file(output),
                "byte_size": output.stat().st_size,
                "outputs": [
                    {
                        "path": str(output),
                        "sha256": sha256_file(output),
                        "duration_seconds": 10.0,
                    }
                ],
                "warnings": [],
            },
        )
        return 0

    monkeypatch.setattr(
        build_edit_ready_source_packet.fetch_source_video,
        "run",
        fake_video,
    )
    monkeypatch.setattr(
        build_edit_ready_source_packet.fetch_source_audio,
        "run",
        fake_audio,
    )
    return calls


def _arg(argv: list[str], name: str) -> str:
    return argv[argv.index(name) + 1]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
