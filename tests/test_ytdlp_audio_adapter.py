"""INT-02e: yt-dlp-audio asset_fetch adapter tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.integrations.asset_fetch import fake_audio, ffmpeg_audio, yt_dlp_audio


def test_build_plan_prefers_argument_paths_without_spawning_subprocess():
    plan = yt_dlp_audio.build_plan(
        source_url="https://www.youtube.com/watch?v=AAA&token=secret",
        output_path="materials/src/source.wav",
        yt_dlp_path="C:/bin/yt-dlp.exe",
        ffmpeg_path="C:/bin/ffmpeg.exe",
        env={yt_dlp_audio.YTDLP_ENV_VAR: "C:/env/yt-dlp.exe"},
    )

    readback = plan.to_dict()
    assert plan.yt_dlp_path == "C:/bin/yt-dlp.exe"
    assert plan.yt_dlp_path_source == "argument"
    assert plan.yt_dlp_command is not None
    assert plan.yt_dlp_command[0] == "C:/bin/yt-dlp.exe"
    assert plan.yt_dlp_command[-1] == "https://www.youtube.com/watch?v=AAA&token=secret"
    assert readback["source_url"] == "https://www.youtube.com/watch?<query:redacted>"
    assert readback["yt_dlp_command"][-1] == "https://www.youtube.com/watch?<query:redacted>"
    assert "token=secret" not in str(readback)
    assert plan.yt_dlp_command_summary is not None
    assert "https://www.youtube.com" not in plan.yt_dlp_command_summary
    assert "<url>" in plan.yt_dlp_command_summary
    assert plan.ffmpeg_plan.ffmpeg_path == "C:/bin/ffmpeg.exe"
    assert "dry-run does not call network" in " ".join(plan.warnings)


def test_discover_ytdlp_uses_env_before_path_lookup():
    resolved, source = yt_dlp_audio.discover_yt_dlp(
        env={yt_dlp_audio.YTDLP_ENV_VAR: "C:/env/yt-dlp.exe"}
    )

    assert resolved == "C:/env/yt-dlp.exe"
    assert source == "env:CLIPPIPE_YTDLP"


def test_fetch_url_audio_success_uses_temp_intermediate_and_normalizes(tmp_path: Path):
    output_wav = tmp_path / "materials" / "src_audio" / "source.wav"
    calls: list[list[str]] = []

    def runner(args, *, capture_output, text, timeout):
        calls.append(args)
        assert capture_output is True
        assert text is True
        if args == ["fake-ytdlp", "--version"]:
            assert timeout == yt_dlp_audio.VERSION_TIMEOUT_SECONDS
            return subprocess.CompletedProcess(args, 0, stdout="2026.05.01\n", stderr="")
        if args == ["fake-ffmpeg", "-version"]:
            assert timeout == ffmpeg_audio.VERSION_TIMEOUT_SECONDS
            return subprocess.CompletedProcess(args, 0, stdout="ffmpeg version fake\n", stderr="")
        if args[0] == "fake-ytdlp":
            assert timeout == yt_dlp_audio.COMMAND_TIMEOUT_SECONDS
            template = args[args.index("-o") + 1]
            intermediate = Path(template.replace("%(ext)s", "webm"))
            intermediate.parent.mkdir(parents=True, exist_ok=True)
            intermediate.write_bytes(b"downloaded media")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="download ok\n")
        assert args[0] == "fake-ffmpeg"
        assert timeout == ffmpeg_audio.COMMAND_TIMEOUT_SECONDS
        fake_audio.write_silent_wav(args[-1], duration_seconds=0.75)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="normalize ok\n")

    result = yt_dlp_audio.fetch_url_audio(
        source_url="https://www.youtube.com/watch?v=AAA",
        output_path=output_wav,
        yt_dlp_path="fake-ytdlp",
        ffmpeg_path="fake-ffmpeg",
        runner=runner,
    )

    assert calls[0] == ["fake-ytdlp", "--version"]
    assert calls[1][0] == "fake-ytdlp"
    assert calls[2] == ["fake-ffmpeg", "-version"]
    assert calls[3][0:4] == ["fake-ffmpeg", "-y", "-i", calls[3][3]]
    assert output_wav.exists()
    assert result.yt_dlp_version == "2026.05.01"
    assert result.yt_dlp_exit_code == 0
    assert result.downloaded_intermediate_name == "source.webm"
    assert result.downloaded_intermediate_byte_size == len(b"downloaded media")
    assert result.intermediate_retained is False
    assert result.ffmpeg_result.duration_seconds == 0.75
    assert "deleted after normalization" in " ".join(result.warnings)
    assert result.stderr_digest["algorithm"] == "sha256"


def test_fetch_url_audio_rejects_non_http_url(tmp_path: Path):
    with pytest.raises(yt_dlp_audio.YtDlpAudioError) as exc:
        yt_dlp_audio.fetch_url_audio(
            source_url="file:///tmp/input.mp4",
            output_path=tmp_path / "source.wav",
            yt_dlp_path="fake-ytdlp",
            ffmpeg_path="fake-ffmpeg",
        )

    assert "http(s) URL" in str(exc.value)


def test_ytdlp_failure_does_not_leave_source_wav(tmp_path: Path):
    output_wav = tmp_path / "materials" / "src_audio" / "source.wav"

    def runner(args, *, capture_output, text, timeout):
        if args == ["fake-ytdlp", "--version"]:
            return subprocess.CompletedProcess(args, 0, stdout="2026.05.01\n", stderr="")
        return subprocess.CompletedProcess(
            args,
            1,
            stdout="",
            stderr="failed https://example.com/video?token=secret",
        )

    with pytest.raises(yt_dlp_audio.YtDlpAudioError) as exc:
        yt_dlp_audio.fetch_url_audio(
            source_url="https://www.youtube.com/watch?v=AAA",
            output_path=output_wav,
            yt_dlp_path="fake-ytdlp",
            ffmpeg_path="fake-ffmpeg",
            runner=runner,
        )

    assert "exit_code=1" in str(exc.value)
    assert "secret" not in str(exc.value)
    assert not output_wav.exists()


def test_scrub_url_for_readback_removes_query_fragment_and_userinfo():
    scrubbed = yt_dlp_audio.scrub_url_for_readback(
        "https://user:password@example.com/watch?v=AAA&token=secret#frag"
    )

    assert scrubbed == (
        "https://<userinfo:redacted>@example.com/watch"
        "?<query:redacted>#<fragment:redacted>"
    )
    assert "password" not in scrubbed
    assert "token=secret" not in scrubbed
    assert "v=AAA" not in scrubbed
