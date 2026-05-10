"""INT-02c: local-media-audio FFmpeg adapter tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.integrations.asset_fetch import fake_audio, ffmpeg_audio


def test_build_plan_prefers_argument_without_spawning_subprocess():
    plan = ffmpeg_audio.build_plan(
        input_path="input.mov",
        output_path="materials/src/source.wav",
        ffmpeg_path="C:/bin/ffmpeg.exe",
        env={ffmpeg_audio.FFMPEG_ENV_VAR: "C:/env/ffmpeg.exe"},
    )

    assert plan.ffmpeg_path == "C:/bin/ffmpeg.exe"
    assert plan.path_source == "argument"
    assert plan.command == [
        "C:/bin/ffmpeg.exe",
        "-y",
        "-i",
        "input.mov",
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        "-acodec",
        "pcm_s16le",
        "materials/src/source.wav",
    ]
    assert plan.to_dict()["audio_format"]["codec"] == "pcm_s16le"


def test_discover_ffmpeg_uses_env_before_path_lookup():
    resolved, source = ffmpeg_audio.discover_ffmpeg(
        env={ffmpeg_audio.FFMPEG_ENV_VAR: "C:/env/ffmpeg.exe"}
    )

    assert resolved == "C:/env/ffmpeg.exe"
    assert source == "env:CLIPPIPE_FFMPEG"


def test_normalize_success_uses_fake_runner_and_reads_output_duration(tmp_path: Path):
    input_media = tmp_path / "input.mov"
    output_wav = tmp_path / "materials" / "src_audio" / "source.wav"
    input_media.write_bytes(b"local media placeholder")
    calls: list[list[str]] = []

    def runner(args, *, capture_output, text, timeout):
        calls.append(args)
        assert capture_output is True
        assert text is True
        if args == ["fake-ffmpeg", "-version"]:
            assert timeout == ffmpeg_audio.VERSION_TIMEOUT_SECONDS
            return subprocess.CompletedProcess(
                args,
                0,
                stdout="ffmpeg version fake\nconfiguration: test",
                stderr="",
            )
        assert timeout == ffmpeg_audio.COMMAND_TIMEOUT_SECONDS
        fake_audio.write_silent_wav(args[-1], duration_seconds=0.5)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="frame=1\n")

    result = ffmpeg_audio.normalize_local_media_audio(
        input_path=input_media,
        output_path=output_wav,
        ffmpeg_path="fake-ffmpeg",
        runner=runner,
    )

    assert calls[0] == ["fake-ffmpeg", "-version"]
    assert calls[1][0:4] == ["fake-ffmpeg", "-y", "-i", str(input_media)]
    assert output_wav.exists()
    assert result.ffmpeg_version == "ffmpeg version fake"
    assert result.exit_code == 0
    assert result.duration_seconds == 0.5
    assert result.stderr_digest is not None
    assert result.stderr_digest["tail"] == "frame=1\n"


def test_normalize_deletes_partial_output_on_failure(tmp_path: Path):
    input_media = tmp_path / "input.mov"
    output_wav = tmp_path / "materials" / "src_audio" / "source.wav"
    input_media.write_bytes(b"local media placeholder")

    def runner(args, *, capture_output, text, timeout):
        if args == ["fake-ffmpeg", "-version"]:
            return subprocess.CompletedProcess(
                args,
                0,
                stdout="ffmpeg version fake\n",
                stderr="",
            )
        output_wav.parent.mkdir(parents=True, exist_ok=True)
        output_wav.write_bytes(b"partial")
        return subprocess.CompletedProcess(
            args,
            1,
            stdout="",
            stderr="failed https://example.com/video?token=secret",
        )

    with pytest.raises(ffmpeg_audio.FfmpegError) as exc:
        ffmpeg_audio.normalize_local_media_audio(
            input_path=input_media,
            output_path=output_wav,
            ffmpeg_path="fake-ffmpeg",
            runner=runner,
        )

    assert "exit_code=1" in str(exc.value)
    assert "secret" not in str(exc.value)
    assert not output_wav.exists()


def test_version_failure_stops_before_normalization(tmp_path: Path):
    input_media = tmp_path / "input.mov"
    output_wav = tmp_path / "materials" / "src_audio" / "source.wav"
    input_media.write_bytes(b"local media placeholder")
    calls: list[list[str]] = []

    def runner(args, *, capture_output, text, timeout):
        calls.append(args)
        return subprocess.CompletedProcess(
            args,
            1,
            stdout="",
            stderr="version failed api_key=secret",
        )

    with pytest.raises(ffmpeg_audio.FfmpegError) as exc:
        ffmpeg_audio.normalize_local_media_audio(
            input_path=input_media,
            output_path=output_wav,
            ffmpeg_path="fake-ffmpeg",
            runner=runner,
        )

    assert calls == [["fake-ffmpeg", "-version"]]
    assert "version check failed" in str(exc.value)
    assert "secret" not in str(exc.value)
    assert not output_wav.exists()


def test_version_runner_exception_is_wrapped(tmp_path: Path):
    input_media = tmp_path / "input.mov"
    output_wav = tmp_path / "materials" / "src_audio" / "source.wav"
    input_media.write_bytes(b"local media placeholder")

    def runner(args, *, capture_output, text, timeout):
        raise FileNotFoundError("fake-ffmpeg")

    with pytest.raises(ffmpeg_audio.FfmpegError) as exc:
        ffmpeg_audio.normalize_local_media_audio(
            input_path=input_media,
            output_path=output_wav,
            ffmpeg_path="fake-ffmpeg",
            runner=runner,
        )

    assert "version check failed before exit code" in str(exc.value)
    assert not output_wav.exists()


def test_stderr_digest_scrubs_url_and_secretish_text():
    digest = ffmpeg_audio.build_stderr_digest(
        "download https://example.com/video?token=secret "
        "token=secret authorization=hidden bearer abc.def"
    )

    assert digest["algorithm"] == "sha256"
    assert "https://example.com" not in digest["tail"]
    assert "token=secret" not in digest["tail"]
    assert "authorization=hidden" not in digest["tail"]
    assert "abc.def" not in digest["tail"]
    assert "<url>" in digest["tail"]
    assert "<redacted>" in digest["tail"]
