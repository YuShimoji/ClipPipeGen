"""Local Vosk STT adapter.

This adapter is intentionally optional: the repo does not depend on Vosk at
install time. CLI preflight reports missing provider/model explicitly instead
of falling back to fake transcript data.
"""

from __future__ import annotations

import importlib
import json
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class VoskSttError(Exception):
    """Raised when local Vosk STT cannot run."""


@dataclass
class AudioInfo:
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    sample_width_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "duration_seconds": self.duration_seconds,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
            "sample_width_bytes": self.sample_width_bytes,
        }


@dataclass
class VoskTranscriptResult:
    segments: list[dict[str, Any]]
    audio_info: AudioInfo
    engine_version: str
    model_readback: str
    params: dict[str, Any]
    warnings: list[str]


def preflight_vosk(*, source_audio_path: Path, model_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    provider_available = importlib.util.find_spec("vosk") is not None
    audio_info: AudioInfo | None = None

    if not provider_available:
        issues.append("provider 'vosk' is not importable; run with a Python environment that includes vosk")
    if not model_path.exists() or not model_path.is_dir():
        issues.append(f"Vosk model directory not found: {model_path}")
    try:
        audio_info = read_wav_info(source_audio_path)
        if audio_info.channels != 1:
            issues.append("Vosk input must be mono PCM WAV")
        if audio_info.sample_width_bytes != 2:
            issues.append("Vosk input must be 16-bit PCM WAV")
    except VoskSttError as exc:
        issues.append(str(exc))

    return {
        "provider": "vosk",
        "provider_available": provider_available,
        "model_path": str(model_path).replace("\\", "/"),
        "source_audio": str(source_audio_path).replace("\\", "/"),
        "audio": audio_info.to_dict() if audio_info else None,
        "ok": not issues,
        "issues": issues,
    }


def read_wav_info(path: Path) -> AudioInfo:
    try:
        with wave.open(str(path), "rb") as wav:
            sample_rate = wav.getframerate()
            frames = wav.getnframes()
            return AudioInfo(
                duration_seconds=frames / sample_rate if sample_rate else 0.0,
                sample_rate_hz=sample_rate,
                channels=wav.getnchannels(),
                sample_width_bytes=wav.getsampwidth(),
            )
    except (OSError, wave.Error) as exc:
        raise VoskSttError(f"source audio must be a readable WAV file: {path} ({exc})") from exc


def try_read_wav_info(path: Path) -> AudioInfo | None:
    try:
        return read_wav_info(path)
    except VoskSttError:
        return None


def transcribe_vosk(
    *,
    source_audio_path: Path,
    model_path: Path,
    language: str,
    vosk_module: Any | None = None,
) -> VoskTranscriptResult:
    preflight = preflight_vosk(source_audio_path=source_audio_path, model_path=model_path)
    if not preflight["ok"] and vosk_module is None:
        raise VoskSttError("; ".join(preflight["issues"]))

    audio_info = read_wav_info(source_audio_path)
    if audio_info.channels != 1 or audio_info.sample_width_bytes != 2:
        raise VoskSttError("Vosk input must be mono 16-bit PCM WAV")

    vosk = vosk_module or importlib.import_module("vosk")
    if hasattr(vosk, "SetLogLevel"):
        vosk.SetLogLevel(-1)
    model = vosk.Model(str(model_path))
    recognizer = vosk.KaldiRecognizer(model, audio_info.sample_rate_hz)
    if hasattr(recognizer, "SetWords"):
        recognizer.SetWords(True)

    payloads: list[dict[str, Any]] = []
    with wave.open(str(source_audio_path), "rb") as wav:
        while True:
            data = wav.readframes(4000)
            if not data:
                break
            if recognizer.AcceptWaveform(data):
                payloads.append(_json_result(recognizer.Result()))
        payloads.append(_json_result(recognizer.FinalResult()))

    segments = _segments_from_payloads(payloads, audio_info.duration_seconds)
    warnings: list[str] = []
    if not segments:
        warnings.append("Vosk produced no transcript segments; downstream edit generation needs manual review")

    model_readback = str(model_path).replace("\\", "/")
    return VoskTranscriptResult(
        segments=segments,
        audio_info=audio_info,
        engine_version=str(getattr(vosk, "__version__", "unknown")),
        model_readback=model_readback,
        params={
            "provider": "vosk",
            "language": language,
            "model_path": model_readback,
            "word_timing": True,
            "source_format": audio_info.to_dict(),
        },
        warnings=warnings,
    )


def _json_result(value: str) -> dict[str, Any]:
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _segments_from_payloads(
    payloads: list[dict[str, Any]],
    duration_seconds: float,
) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    fallback_start = 0.0
    for payload in payloads:
        text = str(payload.get("text") or "").strip()
        if not text:
            continue
        words = payload.get("result") if isinstance(payload.get("result"), list) else []
        timed_words = [w for w in words if isinstance(w, dict)]
        if timed_words:
            start = float(timed_words[0].get("start", fallback_start))
            end = float(timed_words[-1].get("end", max(start + 0.001, fallback_start)))
            confidences = [
                float(word["conf"])
                for word in timed_words
                if isinstance(word.get("conf"), (int, float))
            ]
            confidence = round(sum(confidences) / len(confidences), 6) if confidences else None
        else:
            start = fallback_start
            end = max(start + 0.001, duration_seconds)
            confidence = None
        fallback_start = max(fallback_start, end)
        segments.append(
            {
                "start_seconds": round(start, 6),
                "end_seconds": round(end, 6),
                "text": text,
                "confidence": confidence,
            }
        )
    return segments
