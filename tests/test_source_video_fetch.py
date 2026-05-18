"""INT-02f/INT-02h source video acquisition contract tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.cli import fetch_source_video
from src.integrations.asset_fetch import source_video, yt_dlp_video
from src.pipeline.material_ledger import load_ledger
from src.pipeline.rights_manifest import build_skeleton, save_rights_manifest


REPO_ROOT = Path(__file__).resolve().parent.parent


def _prepare_episode(tmp_path: Path, episode_id: str = "ep_video") -> tuple[Path, Path]:
    root = tmp_path / "episodes"
    ep_dir = root / episode_id
    ep_dir.mkdir(parents=True)
    manifest = build_skeleton(episode_id)
    manifest["source_video"].update(
        url="https://www.youtube.com/watch?v=VIDEO",
        title="source video",
        channel="channel",
        channel_id="UC0001",
        vod_status="public",
    )
    save_rights_manifest(manifest, ep_dir / "rights_manifest.json")
    return root, ep_dir


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "src.cli.main", *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )


def test_source_video_adapter_copies_and_probes_metadata(tmp_path: Path):
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "material" / "source_video.mp4"
    input_path.write_bytes(b"video bytes")

    result = source_video.copy_local_media_video(
        input_path=input_path,
        output_path=output_path,
        ffprobe_path="C:/tools/ffprobe.exe",
        runner=_fake_ffprobe_runner,
    )

    assert output_path.read_bytes() == b"video bytes"
    assert result.copied is True
    assert result.metadata["duration_seconds"] == 2.5
    assert result.metadata["video_codec"] == "h264"
    assert result.metadata["audio_codec"] == "aac"
    assert result.metadata["resolution"] == "1280x720"
    assert result.metadata["fps"] == 29.97003
    assert result.metadata["stream_count"] == 2


def test_fetch_source_video_local_media_creates_sidecar_receipt_and_ledger(
    tmp_path: Path,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)
    source_path = tmp_path / "input local.mp4"
    source_path.write_bytes(b"local source video")

    def fake_copy_local_media_video(*, input_path, output_path, ffprobe_path):
        assert Path(input_path) == source_path
        assert ffprobe_path == "C:/tools/ffprobe.exe"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(source_path.read_bytes())
        probe = source_video.ProbeResult(
            ffprobe_path="C:/tools/ffprobe.exe",
            ffprobe_path_source="argument",
            ffprobe_version="ffprobe version test",
            command=["C:/tools/ffprobe.exe", "-show_streams", str(output_path)],
            command_summary="C:/tools/ffprobe.exe -show_streams source_video.mp4",
            exit_code=0,
            stderr_digest={
                "algorithm": "sha256",
                "sha256": "0" * 64,
                "tail": "",
                "tail_chars": 800,
                "truncated": False,
            },
            metadata=_metadata(),
            warnings=[],
        )
        return source_video.LocalVideoResult(
            source_path=str(source_path).replace("\\", "/"),
            output_path=str(output_path).replace("\\", "/"),
            copied=True,
            byte_size=Path(output_path).stat().st_size,
            probe_result=probe,
            warnings=[
                "local-media-video copies the source file without render/encode",
                "source video acquisition is not production/creative/publish acceptance",
            ],
        )

    monkeypatch.setattr(
        fetch_source_video.source_video,
        "copy_local_media_video",
        fake_copy_local_media_video,
    )

    result = fetch_source_video.run(
        [
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-path",
            str(source_path),
            "--material-id",
            "src_video_local",
            "--mode",
            "local-media-video",
            "--ffprobe-path",
            "C:/tools/ffprobe.exe",
        ]
    )

    assert result == 0
    material_dir = ep_dir / "materials" / "src_video_local"
    video_path = material_dir / "source_video.mp4"
    sidecar_path = material_dir / "sidecar.json"
    receipt_path = material_dir / "fetch_receipt.json"
    assert video_path.exists()
    assert sidecar_path.exists()
    assert receipt_path.exists()

    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["source"]["retrieval_method"] == "asset_fetch_local_media_video"
    assert sidecar["source"]["local_path"] == str(source_path)
    assert sidecar["media_metadata"]["video_codec"] == "h264"
    assert "not production/creative/publish acceptance" in " | ".join(sidecar["warnings"])

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["mode"] == "local-media-video"
    assert receipt["provider"] == "local-media"
    assert receipt["source_url"] is None
    assert receipt["input"] == {
        "source_url": None,
        "local_path": str(source_path).replace("\\", "/"),
    }
    assert receipt["tools"][0]["name"] == "ffprobe"
    assert receipt["outputs"][0]["metadata"]["resolution"] == "1280x720"
    assert receipt["video_metadata"]["fps"] == 29.97003
    assert receipt["rights_snapshot"] == {
        "compliance_status_at_fetch": "pending",
        "hard_gate": False,
    }
    assert any("rights status at fetch is pending" in w for w in receipt["warnings"])

    ledger = load_ledger(ep_dir / "material_ledger.json")
    entry = ledger["materials"][0]
    assert entry["id"] == "src_video_local"
    assert entry["kind"] == "source_video"
    assert entry["subkind"] == "source_video_original"
    assert entry["intended_uses"] == ["editing_video"]
    assert entry["file_path"].endswith("materials/src_video_local/source_video.mp4")

    audit = _run_cli(
        [
            "audit-material-ledger",
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--format",
            "json",
        ]
    )
    assert audit.returncode == 0, audit.stderr
    assert json.loads(audit.stdout)["ok"] is True


def test_fetch_source_video_dry_run_writes_nothing(tmp_path: Path, capsys, monkeypatch):
    root, ep_dir = _prepare_episode(tmp_path)
    source_path = tmp_path / "input.mp4"
    source_path.write_bytes(b"local source video")

    def fail_if_called(**_kwargs):
        raise AssertionError("dry-run must not copy or probe source video")

    monkeypatch.setattr(
        fetch_source_video.source_video,
        "copy_local_media_video",
        fail_if_called,
    )

    result = fetch_source_video.run(
        [
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-path",
            str(source_path),
            "--material-id",
            "src_video_local",
            "--mode",
            "local-media-video",
            "--ffprobe-path",
            "C:/tools/ffprobe.exe",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert result == 0
    assert payload["will_write"] is False
    assert payload["will_call_subprocess"] is False
    assert payload["source_path_exists"] is True
    assert payload["output_path"].endswith("materials/src_video_local/source_video.mp4")
    assert payload["output_contract"]["kind"] == "source_video"
    assert payload["output_contract"]["render_or_encode"] is False
    assert payload["command_plan"]["ffprobe_path"] == "C:/tools/ffprobe.exe"
    assert not (ep_dir / "materials").exists()
    assert not (ep_dir / "material_ledger.json").exists()


def test_fetch_source_video_local_media_rejects_source_url(tmp_path: Path):
    root, _ = _prepare_episode(tmp_path)
    source_path = tmp_path / "input.mp4"
    source_path.write_bytes(b"local source video")

    result = _run_cli(
        [
            "fetch-source-video",
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-path",
            str(source_path),
            "--source-url",
            "https://example.test/video.mp4",
            "--material-id",
            "src_video_local",
            "--mode",
            "local-media-video",
        ]
    )

    assert result.returncode == 2
    assert "does not accept --source-url" in result.stderr


def _fake_ffprobe_runner(
    args: list[str],
    *,
    capture_output: bool,
    text: bool,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    assert capture_output is True
    assert text is True
    assert timeout > 0
    if "-version" in args:
        return subprocess.CompletedProcess(args, 0, stdout="ffprobe version test\n", stderr="")
    return subprocess.CompletedProcess(
        args,
        0,
        stdout=json.dumps(
            {
                "format": {
                    "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                    "format_long_name": "QuickTime / MOV",
                    "duration": "2.5",
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
        ),
        stderr="",
    )


def _metadata() -> dict:
    return {
        "duration_seconds": 2.5,
        "container": "mov,mp4,m4a,3gp,3g2,mj2",
        "container_long_name": "QuickTime / MOV",
        "video_codec": "h264",
        "video_codec_long_name": "H.264 / AVC",
        "audio_codec": "aac",
        "audio_codec_long_name": "AAC",
        "width": 1280,
        "height": 720,
        "resolution": "1280x720",
        "fps": 29.97003,
        "frame_rate": "30000/1001",
        "stream_count": 2,
        "stream_counts": {
            "video": 1,
            "audio": 1,
            "other": 0,
        },
    }


# ---------------------------------------------------------------------------
# INT-02h: yt-dlp-video mode tests
# ---------------------------------------------------------------------------


def _fake_yt_dlp_video_result(
    *,
    output_path: Path,
    container: str = "mp4",
) -> yt_dlp_video.YtDlpVideoResult:
    probe = source_video.ProbeResult(
        ffprobe_path="C:/tools/ffprobe.exe",
        ffprobe_path_source="argument",
        ffprobe_version="ffprobe version test",
        command=[
            "C:/tools/ffprobe.exe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(output_path),
        ],
        command_summary=(
            "C:/tools/ffprobe.exe -v error -print_format json "
            f"-show_format -show_streams {output_path.as_posix()}"
        ),
        exit_code=0,
        stderr_digest={
            "algorithm": "sha256",
            "sha256": "0" * 64,
            "tail": "",
            "tail_chars": 800,
            "truncated": False,
        },
        metadata=_metadata(),
        warnings=[],
    )
    return yt_dlp_video.YtDlpVideoResult(
        yt_dlp_path="C:/tools/yt-dlp.exe",
        yt_dlp_path_source="argument",
        yt_dlp_version="2026.05.01",
        yt_dlp_command=[
            "C:/tools/yt-dlp.exe",
            "--no-playlist",
            "--no-progress",
            "-f",
            yt_dlp_video.DEFAULT_FORMAT_SELECTOR,
            "--print",
            yt_dlp_video.CHOSEN_FORMAT_PRINT_TEMPLATE,
            "-o",
            f"{output_path.parent.as_posix()}/source_video.%(ext)s",
            "https://www.youtube.com/watch?v=VIDEO",
        ],
        yt_dlp_command_summary=(
            "C:/tools/yt-dlp.exe --no-playlist --no-progress -f "
            f"{yt_dlp_video.DEFAULT_FORMAT_SELECTOR} --print <print> "
            f"-o {output_path.parent.as_posix()}/source_video.%(ext)s <url>"
        ),
        yt_dlp_exit_code=0,
        yt_dlp_stderr_digest={
            "algorithm": "sha256",
            "sha256": "f" * 64,
            "tail": "",
            "tail_chars": 800,
            "truncated": False,
        },
        format_selector=yt_dlp_video.DEFAULT_FORMAT_SELECTOR,
        chosen_format={
            "format_id": "299",
            "ext": container,
            "vcodec": "avc1.640028",
            "acodec": "mp4a.40.2",
            "width": 1280,
            "height": 720,
            "fps": 29.97,
            "filesize": 1234567,
            "format_note": "1080p",
        },
        output_path=output_path,
        output_byte_size=output_path.stat().st_size if output_path.exists() else 0,
        container=container,
        probe_result=probe,
        intermediate_retained=False,
        warnings=[
            "source video URL fetch is not production/creative/publish acceptance",
        ],
        stderr_digest={
            "algorithm": "sha256",
            "sha256": "a" * 64,
            "tail": "",
            "tail_chars": 800,
            "truncated": False,
        },
    )


def test_fetch_source_video_yt_dlp_dry_run_writes_nothing(
    tmp_path: Path,
    capsys,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)

    def fail_if_called(**_kwargs):
        raise AssertionError("dry-run must not call yt-dlp")

    monkeypatch.setattr(
        fetch_source_video.yt_dlp_video,
        "fetch_url_video",
        fail_if_called,
    )

    result = fetch_source_video.run(
        [
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-url",
            "https://www.youtube.com/watch?v=AAA&token=secret",
            "--material-id",
            "src_video_yt",
            "--mode",
            "yt-dlp-video",
            "--yt-dlp-path",
            "C:/tools/yt-dlp.exe",
            "--ffprobe-path",
            "C:/tools/ffprobe.exe",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert result == 0
    assert payload["mode"] == "yt-dlp-video"
    assert payload["will_write"] is False
    assert payload["will_call_subprocess"] is False
    assert payload["format_selector"] == yt_dlp_video.DEFAULT_FORMAT_SELECTOR
    assert payload["allowed_containers"] == list(yt_dlp_video.ALLOWED_CONTAINERS)
    assert payload["output_path"].endswith(
        "materials/src_video_yt/source_video.<ext-chosen-by-yt-dlp>"
    )
    assert "token=secret" not in json.dumps(payload)
    assert payload["source_url"] == "https://www.youtube.com/watch?<query:redacted>"
    assert payload["command_plan"]["yt_dlp_path"] == "C:/tools/yt-dlp.exe"
    assert payload["command_plan"]["ffprobe_path"] == "C:/tools/ffprobe.exe"
    assert payload["output_contract"]["render_or_encode"] is False
    assert not (ep_dir / "materials").exists()
    assert not (ep_dir / "material_ledger.json").exists()


def test_fetch_source_video_yt_dlp_video_creates_artifacts(
    tmp_path: Path,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)
    source_url = "https://www.youtube.com/watch?v=VIDEO&sig=secret"

    def fake_fetch_url_video(
        *,
        source_url,
        output_dir,
        yt_dlp_path,
        ffprobe_path,
        format_selector,
    ):
        assert source_url == "https://www.youtube.com/watch?v=VIDEO&sig=secret"
        assert format_selector == yt_dlp_video.DEFAULT_FORMAT_SELECTOR
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        produced = out_dir / "source_video.mp4"
        produced.write_bytes(b"yt-dlp downloaded video")
        return _fake_yt_dlp_video_result(output_path=produced)

    monkeypatch.setattr(
        fetch_source_video.yt_dlp_video,
        "fetch_url_video",
        fake_fetch_url_video,
    )

    result = fetch_source_video.run(
        [
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-url",
            source_url,
            "--material-id",
            "src_video_yt",
            "--mode",
            "yt-dlp-video",
            "--yt-dlp-path",
            "C:/tools/yt-dlp.exe",
            "--ffprobe-path",
            "C:/tools/ffprobe.exe",
        ]
    )

    assert result == 0
    material_dir = ep_dir / "materials" / "src_video_yt"
    video_path = material_dir / "source_video.mp4"
    sidecar_path = material_dir / "sidecar.json"
    receipt_path = material_dir / "fetch_receipt.json"
    assert video_path.exists()
    assert sidecar_path.exists()
    assert receipt_path.exists()

    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["source"]["retrieval_method"] == "asset_fetch_yt_dlp_video"
    assert sidecar["source"]["url"] == "https://www.youtube.com/watch?<query:redacted>"
    assert sidecar["source"]["local_path"] is None
    assert "secret" not in json.dumps(sidecar)
    assert sidecar["chosen_format"]["ext"] == "mp4"
    assert sidecar["media_metadata"]["video_codec"] == "h264"

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["mode"] == "yt-dlp-video"
    assert receipt["provider"] == "yt-dlp"
    assert receipt["source_url"] == "https://www.youtube.com/watch?<query:redacted>"
    assert receipt["container"] == "mp4"
    assert receipt["intermediate"]["retained"] is False
    assert receipt["source_pipeline"]["intermediate_retained"] is False
    assert {t["name"] for t in receipt["tools"]} == {"yt-dlp", "ffprobe"}
    assert receipt["input"]["format_selector"] == yt_dlp_video.DEFAULT_FORMAT_SELECTOR
    assert receipt["input"]["allowed_containers"] == list(
        yt_dlp_video.ALLOWED_CONTAINERS
    )
    assert receipt["chosen_format"]["ext"] == "mp4"
    assert receipt["video_metadata"]["resolution"] == "1280x720"
    assert receipt["rights_snapshot"] == {
        "compliance_status_at_fetch": "pending",
        "hard_gate": False,
        "production_acceptance": False,
    }
    assert "secret" not in json.dumps(receipt)

    ledger = load_ledger(ep_dir / "material_ledger.json")
    entry = ledger["materials"][0]
    assert entry["id"] == "src_video_yt"
    assert entry["kind"] == "source_video"
    assert entry["subkind"] == "source_video_original"
    assert entry["intended_uses"] == ["editing_video"]
    assert entry["file_path"].endswith("materials/src_video_yt/source_video.mp4")


def test_fetch_source_video_yt_dlp_video_conflict_without_force(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    root, ep_dir = _prepare_episode(tmp_path)
    material_dir = ep_dir / "materials" / "src_video_yt"
    material_dir.mkdir(parents=True)
    existing = material_dir / "source_video.mp4"
    existing.write_bytes(b"already here")

    def fail_if_called(**_kwargs):
        raise AssertionError("conflict check must short-circuit before yt-dlp")

    monkeypatch.setattr(
        fetch_source_video.yt_dlp_video,
        "fetch_url_video",
        fail_if_called,
    )

    result = fetch_source_video.run(
        [
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-url",
            "https://www.youtube.com/watch?v=VIDEO",
            "--material-id",
            "src_video_yt",
            "--mode",
            "yt-dlp-video",
        ]
    )

    err = capsys.readouterr().err
    assert result == 1
    assert "source_video.mp4" in err
    assert existing.read_bytes() == b"already here"


def test_fetch_source_video_yt_dlp_video_rejects_source_path(tmp_path: Path):
    root, _ = _prepare_episode(tmp_path)
    fake_input = tmp_path / "input.mp4"
    fake_input.write_bytes(b"local")

    result = _run_cli(
        [
            "fetch-source-video",
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-url",
            "https://www.youtube.com/watch?v=VIDEO",
            "--source-path",
            str(fake_input),
            "--material-id",
            "src_video_yt",
            "--mode",
            "yt-dlp-video",
        ]
    )

    assert result.returncode == 2
    assert "does not accept --source-path" in result.stderr


def test_fetch_source_video_yt_dlp_video_passes_with_rights_pending(
    tmp_path: Path,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)

    def fake_fetch_url_video(
        *,
        source_url,
        output_dir,
        yt_dlp_path,
        ffprobe_path,
        format_selector,
    ):
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        produced = out_dir / "source_video.mp4"
        produced.write_bytes(b"video")
        return _fake_yt_dlp_video_result(output_path=produced)

    monkeypatch.setattr(
        fetch_source_video.yt_dlp_video,
        "fetch_url_video",
        fake_fetch_url_video,
    )

    # rights_manifest from _prepare_episode keeps compliance status at "pending".
    result = fetch_source_video.run(
        [
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-url",
            "https://www.youtube.com/watch?v=VIDEO",
            "--material-id",
            "src_video_yt",
            "--mode",
            "yt-dlp-video",
        ]
    )

    assert result == 0
    receipt = json.loads(
        (ep_dir / "materials" / "src_video_yt" / "fetch_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    assert receipt["rights_snapshot"]["compliance_status_at_fetch"] == "pending"
    assert receipt["rights_snapshot"]["hard_gate"] is False
    assert any(
        "rights status at fetch is pending" in w for w in receipt["warnings"]
    )


def test_fetch_source_video_yt_dlp_video_unsupported_container_no_writes(
    tmp_path: Path,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)

    def fake_fetch_url_video(**_kwargs):
        raise yt_dlp_video.YtDlpVideoError(
            "yt-dlp chose an unsupported container (produced 'source_video.flv', "
            "allowed ['mp4', 'mkv', 'webm'])"
        )

    monkeypatch.setattr(
        fetch_source_video.yt_dlp_video,
        "fetch_url_video",
        fake_fetch_url_video,
    )

    result = fetch_source_video.run(
        [
            "--episode-id",
            "ep_video",
            "--root",
            str(root),
            "--source-url",
            "https://www.youtube.com/watch?v=VIDEO",
            "--material-id",
            "src_video_yt",
            "--mode",
            "yt-dlp-video",
        ]
    )

    assert result == 1
    material_dir = ep_dir / "materials" / "src_video_yt"
    assert not (material_dir / "sidecar.json").exists()
    assert not (material_dir / "fetch_receipt.json").exists()
    assert not (ep_dir / "material_ledger.json").exists()


def test_fetch_source_video_help_exposes_yt_dlp_video_options():
    result = _run_cli(["fetch-source-video", "--help"])
    assert result.returncode == 0, result.stderr
    help_text = result.stdout.lower()
    assert "yt-dlp-video" in help_text
    assert "local-media-video" in help_text
    assert "--source-url" in help_text
    assert "--format-selector" in help_text
    assert "--yt-dlp-path" in help_text
    assert "--ffprobe-path" in help_text
    assert "render" not in help_text
    assert "encode" not in help_text
