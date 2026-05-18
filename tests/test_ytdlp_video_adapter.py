"""INT-02h: yt-dlp-video asset_fetch adapter tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src.integrations.asset_fetch import yt_dlp_video


_FFPROBE_VIDEO_PAYLOAD = {
    "format": {
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "format_long_name": "QuickTime / MOV",
        "duration": "5.0",
    },
    "streams": [
        {
            "codec_type": "video",
            "codec_name": "h264",
            "codec_long_name": "H.264 / AVC",
            "width": 1280,
            "height": 720,
            "avg_frame_rate": "30000/1001",
        },
        {
            "codec_type": "audio",
            "codec_name": "aac",
            "codec_long_name": "AAC",
        },
    ],
}


def test_discover_yt_dlp_prefers_argument_then_env_then_path():
    resolved, source = yt_dlp_video.discover_yt_dlp(
        yt_dlp_path="C:/bin/yt-dlp.exe",
        env={yt_dlp_video.YTDLP_ENV_VAR: "C:/env/yt-dlp.exe"},
    )
    assert (resolved, source) == ("C:/bin/yt-dlp.exe", "argument")

    resolved, source = yt_dlp_video.discover_yt_dlp(
        env={yt_dlp_video.YTDLP_ENV_VAR: "C:/env/yt-dlp.exe"}
    )
    assert (resolved, source) == ("C:/env/yt-dlp.exe", "env:CLIPPIPE_YTDLP")


def test_build_plan_does_not_call_subprocess_and_scrubs_url(tmp_path: Path):
    out_dir = tmp_path / "materials" / "src_video"

    plan = yt_dlp_video.build_plan(
        source_url="https://www.youtube.com/watch?v=AAA&token=secret#frag",
        output_dir=out_dir,
        yt_dlp_path="C:/bin/yt-dlp.exe",
        ffprobe_path="C:/bin/ffprobe.exe",
    )

    readback = plan.to_dict()
    assert plan.yt_dlp_path == "C:/bin/yt-dlp.exe"
    assert plan.yt_dlp_path_source == "argument"
    assert plan.ffprobe_path == "C:/bin/ffprobe.exe"
    assert plan.ffprobe_path_source == "argument"
    assert plan.format_selector == yt_dlp_video.DEFAULT_FORMAT_SELECTOR
    assert plan.allowed_containers == yt_dlp_video.ALLOWED_CONTAINERS
    assert plan.yt_dlp_command is not None
    assert plan.yt_dlp_command[-1] == (
        "https://www.youtube.com/watch?v=AAA&token=secret#frag"
    )
    # readback / summary scrub query/fragment/token
    assert readback["source_url"] == (
        "https://www.youtube.com/watch?<query:redacted>#<fragment:redacted>"
    )
    assert "token=secret" not in json.dumps(readback)
    assert "v=AAA" not in readback["source_url"]
    assert "<url>" in plan.yt_dlp_command_summary
    assert "https://www.youtube.com" not in plan.yt_dlp_command_summary
    assert any("dry-run does not call network" in w for w in plan.warnings)
    assert any("no separate intermediate is retained" in w for w in plan.warnings)
    assert any("ffprobe metadata readback only" in w for w in plan.warnings)


def test_build_plan_includes_format_selector_and_print_marker(tmp_path: Path):
    plan = yt_dlp_video.build_plan(
        source_url="https://example.test/video.mp4",
        output_dir=tmp_path,
        yt_dlp_path="C:/bin/yt-dlp.exe",
        ffprobe_path="C:/bin/ffprobe.exe",
        format_selector="best[ext=mkv]",
    )
    assert "-f" in plan.yt_dlp_command
    assert plan.yt_dlp_command[plan.yt_dlp_command.index("-f") + 1] == "best[ext=mkv]"
    assert "--print" in plan.yt_dlp_command
    print_idx = plan.yt_dlp_command.index("--print")
    assert plan.yt_dlp_command[print_idx + 1].startswith(
        f"after_video:{yt_dlp_video.CHOSEN_FORMAT_MARKER}"
    )
    assert "-o" in plan.yt_dlp_command
    output_template = plan.yt_dlp_command[plan.yt_dlp_command.index("-o") + 1]
    assert output_template.endswith("/source_video.%(ext)s")
    assert plan.output_template.endswith("/source_video.%(ext)s")


def test_fetch_url_video_success_writes_mp4_and_reads_metadata(tmp_path: Path):
    out_dir = tmp_path / "materials" / "src_video_yt"
    chosen_line = "\t".join(
        [
            yt_dlp_video.CHOSEN_FORMAT_MARKER,
            "299",
            "mp4",
            "avc1.640028",
            "mp4a.40.2",
            "1280",
            "720",
            "29.97",
            "1234567",
            "1080p",
        ]
    )

    def runner(args, *, capture_output, text, timeout):
        assert capture_output is True
        assert text is True
        if args == ["fake-ytdlp", "--version"]:
            return subprocess.CompletedProcess(
                args, 0, stdout="2026.05.01\n", stderr=""
            )
        if args[0] == "fake-ytdlp":
            assert timeout == yt_dlp_video.COMMAND_TIMEOUT_SECONDS
            template = args[args.index("-o") + 1]
            produced = Path(template.replace("%(ext)s", "mp4"))
            produced.parent.mkdir(parents=True, exist_ok=True)
            produced.write_bytes(b"video bytes")
            return subprocess.CompletedProcess(
                args,
                0,
                stdout=f"some other log line\n{chosen_line}\n",
                stderr="download ok\n",
            )
        if args[0] == "fake-ffprobe" and "-version" in args:
            return subprocess.CompletedProcess(
                args, 0, stdout="ffprobe version fake\n", stderr=""
            )
        # ffprobe metadata probe
        assert args[0] == "fake-ffprobe"
        assert "-show_streams" in args
        return subprocess.CompletedProcess(
            args,
            0,
            stdout=json.dumps(_FFPROBE_VIDEO_PAYLOAD),
            stderr="",
        )

    result = yt_dlp_video.fetch_url_video(
        source_url="https://www.youtube.com/watch?v=AAA",
        output_dir=out_dir,
        yt_dlp_path="fake-ytdlp",
        ffprobe_path="fake-ffprobe",
        runner=runner,
    )

    assert result.output_path == out_dir / "source_video.mp4"
    assert result.output_path.exists()
    assert result.container == "mp4"
    assert result.intermediate_retained is False
    assert result.yt_dlp_version == "2026.05.01"
    assert result.yt_dlp_exit_code == 0
    assert result.chosen_format["format_id"] == "299"
    assert result.chosen_format["ext"] == "mp4"
    assert result.chosen_format["width"] == 1280
    assert result.chosen_format["height"] == 720
    assert result.chosen_format["fps"] == pytest.approx(29.97)
    assert result.chosen_format["filesize"] == 1234567
    assert result.chosen_format["format_note"] == "1080p"
    assert result.metadata["video_codec"] == "h264"
    assert result.metadata["resolution"] == "1280x720"
    assert any("not production/creative/publish acceptance" in w for w in result.warnings)
    assert result.stderr_digest["algorithm"] == "sha256"


def test_fetch_url_video_rejects_unsupported_container_and_cleans_up(tmp_path: Path):
    out_dir = tmp_path / "materials" / "src_video_unsupported"

    def runner(args, *, capture_output, text, timeout):
        if args == ["fake-ytdlp", "--version"]:
            return subprocess.CompletedProcess(args, 0, stdout="2026.05.01\n", stderr="")
        if args[0] == "fake-ytdlp":
            template = args[args.index("-o") + 1]
            produced = Path(template.replace("%(ext)s", "flv"))
            produced.parent.mkdir(parents=True, exist_ok=True)
            produced.write_bytes(b"flv bytes")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected subprocess call: {args}")

    with pytest.raises(yt_dlp_video.YtDlpVideoError) as exc:
        yt_dlp_video.fetch_url_video(
            source_url="https://example.test/video",
            output_dir=out_dir,
            yt_dlp_path="fake-ytdlp",
            ffprobe_path="fake-ffprobe",
            runner=runner,
        )

    assert "unsupported container" in str(exc.value)
    assert not (out_dir / "source_video.flv").exists()


def test_fetch_url_video_cleans_up_on_ytdlp_failure(tmp_path: Path):
    out_dir = tmp_path / "materials" / "src_video_fail"

    def runner(args, *, capture_output, text, timeout):
        if args == ["fake-ytdlp", "--version"]:
            return subprocess.CompletedProcess(args, 0, stdout="2026.05.01\n", stderr="")
        if args[0] == "fake-ytdlp":
            template = args[args.index("-o") + 1]
            partial = Path(template.replace("%(ext)s", "mp4"))
            partial.parent.mkdir(parents=True, exist_ok=True)
            # leave a partial download
            partial.write_bytes(b"partial")
            return subprocess.CompletedProcess(
                args,
                1,
                stdout="",
                stderr="ERROR fetch https://example.test/video?token=secret",
            )
        raise AssertionError(f"unexpected subprocess call: {args}")

    with pytest.raises(yt_dlp_video.YtDlpVideoError) as exc:
        yt_dlp_video.fetch_url_video(
            source_url="https://example.test/video?token=secret",
            output_dir=out_dir,
            yt_dlp_path="fake-ytdlp",
            ffprobe_path="fake-ffprobe",
            runner=runner,
        )

    assert "exit_code=1" in str(exc.value)
    assert "secret" not in str(exc.value)
    assert not (out_dir / "source_video.mp4").exists()


def test_fetch_url_video_cleans_up_on_probe_failure(tmp_path: Path):
    out_dir = tmp_path / "materials" / "src_video_probe_fail"

    def runner(args, *, capture_output, text, timeout):
        if args == ["fake-ytdlp", "--version"]:
            return subprocess.CompletedProcess(args, 0, stdout="2026.05.01\n", stderr="")
        if args[0] == "fake-ytdlp":
            template = args[args.index("-o") + 1]
            produced = Path(template.replace("%(ext)s", "mkv"))
            produced.parent.mkdir(parents=True, exist_ok=True)
            produced.write_bytes(b"mkv bytes")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        if args[0] == "fake-ffprobe" and "-version" in args:
            return subprocess.CompletedProcess(
                args, 0, stdout="ffprobe version fake\n", stderr=""
            )
        # probe failure
        return subprocess.CompletedProcess(
            args, 1, stdout="", stderr="ffprobe parse error\n"
        )

    with pytest.raises(yt_dlp_video.YtDlpVideoError) as exc:
        yt_dlp_video.fetch_url_video(
            source_url="https://example.test/video",
            output_dir=out_dir,
            yt_dlp_path="fake-ytdlp",
            ffprobe_path="fake-ffprobe",
            runner=runner,
        )

    assert "ffprobe metadata read failed" in str(exc.value)
    assert not (out_dir / "source_video.mkv").exists()


def test_fetch_url_video_rejects_non_http_url(tmp_path: Path):
    with pytest.raises(yt_dlp_video.YtDlpVideoError) as exc:
        yt_dlp_video.fetch_url_video(
            source_url="file:///tmp/input.mp4",
            output_dir=tmp_path,
            yt_dlp_path="fake-ytdlp",
            ffprobe_path="fake-ffprobe",
        )

    assert "http(s) URL" in str(exc.value)


def test_fetch_url_video_refuses_to_overwrite_existing_source_video(tmp_path: Path):
    out_dir = tmp_path / "materials" / "src_video_existing"
    out_dir.mkdir(parents=True)
    existing = out_dir / "source_video.mp4"
    existing.write_bytes(b"already here")

    def runner(args, *, capture_output, text, timeout):
        if args == ["fake-ytdlp", "--version"]:
            return subprocess.CompletedProcess(args, 0, stdout="2026.05.01\n", stderr="")
        raise AssertionError(
            "fetch_url_video must refuse to call yt-dlp when source_video.* exists"
        )

    with pytest.raises(yt_dlp_video.YtDlpVideoError) as exc:
        yt_dlp_video.fetch_url_video(
            source_url="https://example.test/video",
            output_dir=out_dir,
            yt_dlp_path="fake-ytdlp",
            ffprobe_path="fake-ffprobe",
            runner=runner,
        )

    assert "already contains source_video" in str(exc.value)
    assert existing.exists()
