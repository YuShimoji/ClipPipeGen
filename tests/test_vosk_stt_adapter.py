"""ED-07b: optional Vosk real-STT adapter tests."""

from __future__ import annotations

import json
import wave
from pathlib import Path

from src.integrations.stt.vosk_adapter import preflight_vosk, transcribe_vosk


def test_transcribe_vosk_with_injected_provider_returns_real_segments(tmp_path: Path):
    audio_path = tmp_path / "source.wav"
    model_path = tmp_path / "model"
    model_path.mkdir()
    _write_mono_wav(audio_path)

    result = transcribe_vosk(
        source_audio_path=audio_path,
        model_path=model_path,
        language="en",
        vosk_module=_FakeVosk,
    )

    assert result.engine_version == "fake-vosk-test"
    assert result.model_readback.endswith("model")
    assert result.audio_info.sample_rate_hz == 16000
    assert result.params["provider"] == "vosk"
    assert result.params["word_timing"] is True
    assert result.segments == [
        {
            "start_seconds": 0.1,
            "end_seconds": 0.8,
            "text": "real speech",
            "confidence": 0.825,
        }
    ]


def test_preflight_vosk_reports_missing_model_without_fixture_fallback(tmp_path: Path):
    audio_path = tmp_path / "source.wav"
    _write_mono_wav(audio_path)

    payload = preflight_vosk(
        source_audio_path=audio_path,
        model_path=tmp_path / "missing-model",
    )

    assert payload["ok"] is False
    assert any("model directory not found" in issue.lower() for issue in payload["issues"])
    assert payload["provider"] == "vosk"
    assert payload["audio"]["channels"] == 1


def _write_mono_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\0\0" * 1600)


class _FakeVosk:
    __version__ = "fake-vosk-test"

    @staticmethod
    def SetLogLevel(_level: int) -> None:
        return None

    class Model:
        def __init__(self, _path: str) -> None:
            return None

    class KaldiRecognizer:
        def __init__(self, _model: object, _sample_rate: int) -> None:
            return None

        def SetWords(self, _value: bool) -> None:
            return None

        def AcceptWaveform(self, _data: bytes) -> bool:
            return False

        def FinalResult(self) -> str:
            return json.dumps(
                {
                    "text": "real speech",
                    "result": [
                        {"word": "real", "start": 0.1, "end": 0.4, "conf": 0.8},
                        {"word": "speech", "start": 0.4, "end": 0.8, "conf": 0.85},
                    ],
                }
            )
