"""Fake source-audio generator for INT-02a.

This does not download anything. It writes a deterministic silent PCM WAV so
the asset_fetch contract can be tested before real yt-dlp / ffmpeg integration.
"""

from __future__ import annotations

import wave
from pathlib import Path

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_WIDTH_BYTES = 2
DURATION_SECONDS = 1.0
SUBKIND = "wav_pcm_16k_mono"


def write_silent_wav(
    path: str | Path,
    *,
    duration_seconds: float = DURATION_SECONDS,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    channels: int = CHANNELS,
    sample_width_bytes: int = SAMPLE_WIDTH_BYTES,
) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    frames = int(duration_seconds * sample_rate_hz)
    silence = b"\x00" * frames * channels * sample_width_bytes
    with wave.open(str(p), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width_bytes)
        wav.setframerate(sample_rate_hz)
        wav.writeframes(silence)
