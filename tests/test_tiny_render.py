"""OUT-01 tiny render proof tests."""

from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

import pytest

from src.cli import render_tiny_proof
from src.integrations.render import ffmpeg_tiny
from src.pipeline.edit_pack import add_cut_candidate, build_skeleton, save_edit_pack


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_ffmpeg_tiny_adapter_renders_and_probes_output(tmp_path: Path):
    source_video = tmp_path / "source_video.mp4"
    source_audio = tmp_path / "source.wav"
    output = tmp_path / "rendered_video.mp4"
    source_video.write_bytes(b"video")
    _write_wav(source_audio, seconds=2.0)

    result = ffmpeg_tiny.render_tiny_proof(
        source_video_path=source_video,
        source_audio_path=source_audio,
        output_path=output,
        start_seconds=0.25,
        duration_seconds=1.5,
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        runner=_fake_render_runner(output),
    )

    assert output.exists()
    assert result.metadata["duration_seconds"] == 1.5
    assert result.metadata["video_codec"] == "h264"
    assert result.metadata["audio_codec"] == "aac"
    assert result.metadata["resolution"] == "320x180"
    assert result.metadata["fps"] == 24.0
    assert result.command_summary.startswith("fake-ffmpeg -y -ss 0.25")
    assert result.preflight["status"] == "passed"
    assert result.selected_profile.profile_id == "mp4_h264_aac"
    assert result.fallback_used is False
    assert result.attempts[0].status == "succeeded"
    assert result.attempts[0].failure_reason is None


def test_ffmpeg_tiny_adapter_records_codec_fallback_attempt(tmp_path: Path):
    source_video = tmp_path / "source_video.mp4"
    source_audio = tmp_path / "source.wav"
    output = tmp_path / "rendered_video.mp4"
    source_video.write_bytes(b"video")
    _write_wav(source_audio, seconds=2.0)

    result = ffmpeg_tiny.render_tiny_proof(
        source_video_path=source_video,
        source_audio_path=source_audio,
        output_path=output,
        start_seconds=0.25,
        duration_seconds=1.5,
        ffmpeg_path="fake-ffmpeg",
        ffprobe_path="fake-ffprobe",
        runner=_fallback_render_runner(output),
    )

    assert output.exists()
    assert result.fallback_used is True
    assert result.selected_profile.profile_id == "mp4_openh264_aac"
    assert result.attempts[0].status == "failed"
    assert result.attempts[0].failure_reason == "codec_or_container_unsupported"
    assert result.attempts[1].status == "succeeded"
    assert any("fallback attempt" in warning for warning in result.warnings)


def test_ffmpeg_tiny_preflight_classifies_missing_ffmpeg(tmp_path: Path):
    source_video = tmp_path / "source_video.mp4"
    source_audio = tmp_path / "source.wav"
    source_video.write_bytes(b"video")
    _write_wav(source_audio, seconds=2.0)

    with pytest.raises(ffmpeg_tiny.TinyRenderError) as excinfo:
        ffmpeg_tiny.render_tiny_proof(
            source_video_path=source_video,
            source_audio_path=source_audio,
            output_path=tmp_path / "rendered_video.mp4",
            start_seconds=0.0,
            duration_seconds=1.0,
            env={"PATH": ""},
            runner=_fake_render_runner(tmp_path / "rendered_video.mp4"),
        )

    assert excinfo.value.failure_reason == "environment_missing_ffmpeg"
    assert excinfo.value.preflight["status"] == "failed"


def test_ffmpeg_tiny_preflight_classifies_missing_ffprobe(tmp_path: Path):
    source_video = tmp_path / "source_video.mp4"
    source_audio = tmp_path / "source.wav"
    source_video.write_bytes(b"video")
    _write_wav(source_audio, seconds=2.0)

    with pytest.raises(ffmpeg_tiny.TinyRenderError) as excinfo:
        ffmpeg_tiny.render_tiny_proof(
            source_video_path=source_video,
            source_audio_path=source_audio,
            output_path=tmp_path / "rendered_video.mp4",
            start_seconds=0.0,
            duration_seconds=1.0,
            ffmpeg_path="fake-ffmpeg",
            env={"PATH": ""},
            runner=_fake_render_runner(tmp_path / "rendered_video.mp4"),
        )

    assert excinfo.value.failure_reason == "environment_missing_ffprobe"


def test_ffmpeg_tiny_classifies_missing_inputs_and_bad_duration(tmp_path: Path):
    source_audio = tmp_path / "source.wav"
    _write_wav(source_audio, seconds=2.0)

    with pytest.raises(ffmpeg_tiny.TinyRenderError) as missing_video:
        ffmpeg_tiny.render_tiny_proof(
            source_video_path=tmp_path / "missing.mp4",
            source_audio_path=source_audio,
            output_path=tmp_path / "rendered_video.mp4",
            start_seconds=0.0,
            duration_seconds=1.0,
            ffmpeg_path="fake-ffmpeg",
            ffprobe_path="fake-ffprobe",
            runner=_fake_render_runner(tmp_path / "rendered_video.mp4"),
        )
    assert missing_video.value.failure_reason == "input_video_missing"

    source_video = tmp_path / "source_video.mp4"
    source_video.write_bytes(b"video")
    with pytest.raises(ffmpeg_tiny.TinyRenderError) as bad_duration:
        ffmpeg_tiny.render_tiny_proof(
            source_video_path=source_video,
            source_audio_path=source_audio,
            output_path=tmp_path / "rendered_video.mp4",
            start_seconds=0.0,
            duration_seconds=0.0,
            ffmpeg_path="fake-ffmpeg",
            ffprobe_path="fake-ffprobe",
            runner=_fake_render_runner(tmp_path / "rendered_video.mp4"),
        )
    assert bad_duration.value.failure_reason == "duration_or_timeline_mismatch"


def test_render_tiny_proof_cli_writes_video_receipt_manifest_and_report(
    tmp_path: Path,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)

    def fake_render_tiny_proof(**kwargs):
        output_path = Path(kwargs["output_path"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"rendered video")
        probe = ffmpeg_tiny.ProbeResult(
            ffprobe_path="C:/tools/ffprobe.exe",
            ffprobe_path_source="argument",
            ffprobe_version="ffprobe version test",
            command=["C:/tools/ffprobe.exe", "-show_streams", str(output_path)],
            command_summary="C:/tools/ffprobe.exe -show_streams rendered_video.mp4",
            exit_code=0,
            stderr_digest=_stderr_digest(),
            metadata=_output_metadata(),
        )
        profile = _render_profile(output_path)
        return ffmpeg_tiny.RenderResult(
            ffmpeg_path="C:/tools/ffmpeg.exe",
            ffmpeg_path_source="argument",
            ffmpeg_version="ffmpeg version test",
            ffprobe_path="C:/tools/ffprobe.exe",
            ffprobe_path_source="argument",
            ffprobe_version="ffprobe version test",
            command=["C:/tools/ffmpeg.exe", "-i", "source", str(output_path)],
            command_summary="C:/tools/ffmpeg.exe -i source rendered_video.mp4",
            attempts=[
                ffmpeg_tiny.CommandAttempt(
                    profile=profile,
                    command=["C:/tools/ffmpeg.exe", "-i", "source", str(output_path)],
                    command_summary="C:/tools/ffmpeg.exe -i source rendered_video.mp4",
                    status="succeeded",
                    exit_code=0,
                    stderr_digest=_stderr_digest(),
                    failure_reason=None,
                    selected=True,
                )
            ],
            selected_profile=profile,
            fallback_used=False,
            output_path=str(output_path).replace("\\", "/"),
            metadata=_output_metadata(),
            probe_result=probe,
            preflight=_tool_preflight(),
            warnings=["subtitle burn-in is intentionally disabled"],
        )

    monkeypatch.setattr(
        render_tiny_proof.ffmpeg_tiny,
        "render_tiny_proof",
        fake_render_tiny_proof,
    )

    result = render_tiny_proof.run(
        [
            "--episode-id",
            "ep_out01",
            "--root",
            str(root),
            "--source-video-material-id",
            "src_video_001",
            "--source-audio-material-id",
            "src_audio_001",
            "--edit-pack-path",
            str(ep_dir / "edit_pack.json"),
            "--output-id",
            "out01_tiny_render",
            "--duration-sec",
            "10",
            "--ffmpeg-path",
            "C:/tools/ffmpeg.exe",
            "--ffprobe-path",
            "C:/tools/ffprobe.exe",
        ]
    )

    assert result == 0
    output_dir = ep_dir / "renders" / "out01_tiny_render"
    video_path = output_dir / "rendered_video.mp4"
    receipt_path = output_dir / "render_receipt.json"
    manifest_path = output_dir / "render_manifest.json"
    report_path = output_dir / "render_report.html"
    assert video_path.exists()
    assert receipt_path.exists()
    assert manifest_path.exists()
    assert report_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["format"] == "tiny_render_proof_v1"
    assert manifest["production_candidate"] is False
    assert manifest["source_refs"]["source_video"]["material_id"] == "src_video_001"
    assert manifest["source_refs"]["source_audio"]["material_id"] == "src_audio_001"
    assert manifest["source_refs"]["transcript"]["real_transcript"] is True
    assert manifest["timeline_mapping"]["cut_id"] == "cut_001"
    assert manifest["timeline_mapping"]["render_duration_seconds"] == 1.75
    assert manifest["timeline_mapping"]["clamped"] is True
    assert manifest["output_metadata"]["video_codec"] == "h264"
    assert manifest["output_metadata"]["audio_codec"] == "aac"
    assert manifest["selected_render_profile"]["profile_id"] == "mp4_h264_aac"
    assert manifest["attempted_render_profiles"][0]["status"] == "succeeded"
    assert manifest["fallback_used"] is False
    assert manifest["subtitle_burn_in"] is False
    assert any("duration target unmet" in w for w in manifest["warnings"])
    assert any("not approved" in w for w in manifest["warnings"])

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["provider"] == "ffmpeg"
    assert receipt["mode"] == "tiny-render-proof"
    assert receipt["outputs"]["rendered_video"].endswith("rendered_video.mp4")
    assert receipt["commands"][0]["selected"] is True
    assert receipt["preflight"]["tool_preflight"]["status"] == "passed"
    assert "OUT-01 Tiny Render Proof" in report_path.read_text(encoding="utf-8")


def test_render_tiny_proof_cli_writes_failure_receipt_manifest_and_report(
    tmp_path: Path,
    monkeypatch,
):
    root, ep_dir = _prepare_episode(tmp_path)

    def fake_render_failure(**kwargs):
        output_path = Path(kwargs["output_path"])
        profile = _render_profile(output_path)
        attempt = ffmpeg_tiny.CommandAttempt(
            profile=profile,
            command=["C:/tools/ffmpeg.exe", "-i", "source", str(output_path)],
            command_summary="C:/tools/ffmpeg.exe -i source rendered_video.mp4",
            status="failed",
            exit_code=1,
            stderr_digest=_stderr_digest("Unknown encoder libx264"),
            failure_reason="codec_or_container_unsupported",
            selected=False,
        )
        raise ffmpeg_tiny.TinyRenderError(
            "ffmpeg render failed: exit_code=1",
            failure_reason="codec_or_container_unsupported",
            preflight=_tool_preflight(),
            attempts=[attempt],
        )

    monkeypatch.setattr(
        render_tiny_proof.ffmpeg_tiny,
        "render_tiny_proof",
        fake_render_failure,
    )

    result = render_tiny_proof.run(
        [
            "--episode-id",
            "ep_out01",
            "--root",
            str(root),
            "--source-video-material-id",
            "src_video_001",
            "--source-audio-material-id",
            "src_audio_001",
            "--edit-pack-path",
            str(ep_dir / "edit_pack.json"),
            "--output-id",
            "out01_tiny_render_failed",
            "--ffmpeg-path",
            "C:/tools/ffmpeg.exe",
            "--ffprobe-path",
            "C:/tools/ffprobe.exe",
        ]
    )

    assert result == 1
    output_dir = ep_dir / "renders" / "out01_tiny_render_failed"
    receipt = json.loads((output_dir / "render_receipt.json").read_text(encoding="utf-8"))
    manifest = json.loads((output_dir / "render_manifest.json").read_text(encoding="utf-8"))
    report = (output_dir / "render_report.html").read_text(encoding="utf-8")
    assert receipt["status"] == "failed"
    assert receipt["failure_classification"]["failure_reason"] == "codec_or_container_unsupported"
    assert manifest["attempted_render_profiles"][0]["failure_reason"] == "codec_or_container_unsupported"
    assert "codec_or_container_unsupported" in report


def test_render_tiny_proof_dry_run_writes_nothing(tmp_path: Path):
    root, ep_dir = _prepare_episode(tmp_path)

    result = render_tiny_proof.run(
        [
            "--episode-id",
            "ep_out01",
            "--root",
            str(root),
            "--source-video-material-id",
            "src_video_001",
            "--source-audio-material-id",
            "src_audio_001",
            "--edit-pack-path",
            str(ep_dir / "edit_pack.json"),
            "--output-id",
            "out01_tiny_render",
            "--ffmpeg-path",
            "C:/tools/ffmpeg.exe",
            "--ffprobe-path",
            "C:/tools/ffprobe.exe",
            "--dry-run",
        ]
    )

    assert result == 0
    assert not (ep_dir / "renders").exists()


def test_render_tiny_proof_cli_help_exposes_no_fetch_or_publish():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "render-tiny-proof", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    help_text = result.stdout.lower()
    assert "render-tiny-proof" in help_text
    assert "--source-video-material-id" in help_text
    assert "--source-audio-material-id" in help_text
    assert "--edit-pack-path" in help_text
    assert "subtitle" not in help_text
    assert "yt-dlp" not in help_text
    assert "publish" not in help_text


def _prepare_episode(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "episodes"
    ep_dir = root / "ep_out01"
    video_dir = ep_dir / "materials" / "src_video_001"
    audio_dir = ep_dir / "materials" / "src_audio_001"
    video_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)
    (video_dir / "source_video.mp4").write_bytes(b"video")
    _write_wav(audio_dir / "source.wav", seconds=5.0)
    _write_json(
        {
            "schema_version": "v1",
            "asset_id": "src_video_001",
            "asset_path": str(video_dir / "source_video.mp4").replace("\\", "/"),
            "asset_hash_sha256": "video-hash",
            "source": {
                "kind": "unverified",
                "url": None,
                "local_path": "C:/input/source_video.mp4",
                "retrieved_at": "2026-05-12T00:00:00+00:00",
                "retrieved_by": "test",
                "retrieval_method": "asset_fetch_local_media_video",
            },
            "license": {"kind": "unknown"},
            "usage_conditions": ["source_link_required"],
            "restrictions": {},
            "attribution_text": "test video",
            "media_metadata": {
                "duration_seconds": 2.0,
                "container": "mov,mp4,m4a,3gp,3g2,mj2",
                "video_codec": "h264",
                "audio_codec": None,
                "resolution": "320x180",
                "fps": 24.0,
                "stream_count": 1,
            },
        },
        video_dir / "sidecar.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "asset_id": "src_audio_001",
            "asset_path": str(audio_dir / "source.wav").replace("\\", "/"),
            "asset_hash_sha256": "audio-hash",
            "source": {
                "kind": "unverified",
                "local_path": "C:/input/source.wav",
                "retrieved_at": "2026-05-12T00:00:00+00:00",
                "retrieved_by": "test",
                "retrieval_method": "asset_fetch_local_media_audio",
            },
            "license": {"kind": "unknown"},
            "usage_conditions": ["source_link_required"],
            "restrictions": {},
            "attribution_text": "test audio",
        },
        audio_dir / "sidecar.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_out01",
            "material_id": "src_video_001",
            "mode": "local-media-video",
            "provider": "local-media",
            "input": {"source_url": None, "local_path": "C:/input/source_video.mp4"},
            "video_metadata": {
                "duration_seconds": 2.0,
                "container": "mov,mp4,m4a,3gp,3g2,mj2",
                "video_codec": "h264",
                "audio_codec": None,
                "resolution": "320x180",
                "fps": 24.0,
                "stream_count": 1,
            },
            "rights_snapshot": {"compliance_status_at_fetch": "pending", "hard_gate": False},
            "warnings": ["source video acquisition is not production/creative/publish acceptance"],
        },
        video_dir / "fetch_receipt.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_out01",
            "material_id": "src_audio_001",
            "mode": "local-media-audio",
            "provider": "local-media",
            "input": {"source_url": None, "local_path": "C:/input/source.wav"},
            "outputs": [{"duration_seconds": 5.0}],
            "rights_snapshot": {"compliance_status_at_fetch": "pending", "hard_gate": False},
        },
        audio_dir / "fetch_receipt.json",
    )
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_out01",
            "created_at": "2026-05-12T00:00:00+00:00",
            "updated_at": "2026-05-12T00:00:00+00:00",
            "materials": [
                {
                    "id": "src_video_001",
                    "kind": "source_video",
                    "subkind": "source_video_original",
                    "file_path": str(video_dir / "source_video.mp4").replace("\\", "/"),
                    "sidecar_path": str(video_dir / "sidecar.json").replace("\\", "/"),
                    "hash_sha256": "video-hash",
                    "byte_size": 5,
                    "intended_uses": ["editing_video"],
                    "registered_at": "2026-05-12T00:00:00+00:00",
                    "registered_by": "test",
                    "compliance_link": {
                        "rights_manifest_id": "ep_out01",
                        "compliance_status_at_registration": "pending",
                    },
                },
                {
                    "id": "src_audio_001",
                    "kind": "source_audio",
                    "subkind": "wav_pcm_16k_mono",
                    "file_path": str(audio_dir / "source.wav").replace("\\", "/"),
                    "sidecar_path": str(audio_dir / "sidecar.json").replace("\\", "/"),
                    "hash_sha256": "audio-hash",
                    "byte_size": 16044,
                    "intended_uses": ["editing_audio"],
                    "registered_at": "2026-05-12T00:00:00+00:00",
                    "registered_by": "test",
                    "compliance_link": {
                        "rights_manifest_id": "ep_out01",
                        "compliance_status_at_registration": "pending",
                    },
                },
            ],
        },
        ep_dir / "material_ledger.json",
    )
    pack = build_skeleton(
        "ep_out01",
        rights_manifest_path=str(ep_dir / "rights_manifest.json").replace("\\", "/"),
        material_ledger_path=str(ep_dir / "material_ledger.json").replace("\\", "/"),
    )
    pack = add_cut_candidate(
        pack,
        start_seconds=0.25,
        end_seconds=4.0,
        source="auto",
        reason="test cut",
        confidence=0.8,
        cut_id="cut_001",
        select=True,
    )
    save_edit_pack(pack, ep_dir / "edit_pack.json")
    _write_json(
        {
            "schema_version": "v1",
            "episode_id": "ep_out01",
            "source_audio": {
                "path": str(audio_dir / "source.wav").replace("\\", "/"),
                "material_id": "src_audio_001",
                "duration_seconds": 5.0,
            },
            "stt": {
                "engine": "vosk",
                "provider": "vosk",
                "model": "test-model",
                "real_transcript": True,
                "segment_count": 1,
            },
            "segment_count": 1,
            "segments": [
                {
                    "id": "seg_000001",
                    "start_seconds": 0.25,
                    "end_seconds": 4.0,
                    "text": "real transcript plumbing",
                    "review_status": "unreviewed",
                }
            ],
        },
        ep_dir / "transcript.json",
    )
    return root, ep_dir


def _fake_render_runner(output: Path):
    def runner(
        args: list[str],
        *,
        capture_output: bool,
        text: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        assert capture_output is True
        assert text is True
        assert timeout > 0
        if args == ["fake-ffmpeg", "-version"]:
            return subprocess.CompletedProcess(args, 0, stdout="ffmpeg version test\n", stderr="")
        if args == ["fake-ffprobe", "-version"]:
            return subprocess.CompletedProcess(args, 0, stdout="ffprobe version test\n", stderr="")
        if args[0] == "fake-ffmpeg":
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        if args[0] == "fake-ffprobe":
            return subprocess.CompletedProcess(
                args,
                0,
                stdout=json.dumps(
                    {
                        "format": {
                            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                            "format_long_name": "QuickTime / MOV",
                            "duration": "1.5",
                        },
                        "streams": [
                            {
                                "codec_type": "video",
                                "codec_name": "h264",
                                "codec_long_name": "H.264 / AVC",
                                "width": 320,
                                "height": 180,
                                "avg_frame_rate": "24/1",
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
        raise AssertionError(args)

    return runner


def _fallback_render_runner(output: Path):
    def runner(
        args: list[str],
        *,
        capture_output: bool,
        text: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        assert capture_output is True
        assert text is True
        assert timeout > 0
        if args == ["fake-ffmpeg", "-version"]:
            return subprocess.CompletedProcess(args, 0, stdout="ffmpeg version test\n", stderr="")
        if args == ["fake-ffprobe", "-version"]:
            return subprocess.CompletedProcess(args, 0, stdout="ffprobe version test\n", stderr="")
        if args[0] == "fake-ffmpeg":
            video_codec = args[args.index("-c:v") + 1]
            if video_codec == "libx264":
                return subprocess.CompletedProcess(
                    args,
                    1,
                    stdout="",
                    stderr="Unknown encoder 'libx264'",
                )
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        if args[0] == "fake-ffprobe":
            return _fake_render_runner(output)(args, capture_output=capture_output, text=text, timeout=timeout)
        raise AssertionError(args)

    return runner


def _write_wav(path: Path, *, seconds: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16000
    frames = int(sample_rate * seconds)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * frames)


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _output_metadata() -> dict:
    return {
        "duration_seconds": 1.75,
        "container": "mov,mp4,m4a,3gp,3g2,mj2",
        "container_long_name": "QuickTime / MOV",
        "video_codec": "h264",
        "video_codec_long_name": "H.264 / AVC",
        "audio_codec": "aac",
        "audio_codec_long_name": "AAC",
        "width": 320,
        "height": 180,
        "resolution": "320x180",
        "fps": 24.0,
        "frame_rate": "24/1",
        "stream_count": 2,
        "stream_counts": {"video": 1, "audio": 1, "other": 0},
    }


def _render_profile(output_path: Path) -> ffmpeg_tiny.RenderProfile:
    return ffmpeg_tiny.RenderProfile(
        profile_id="mp4_h264_aac",
        container="mp4",
        video_codec="libx264",
        audio_codec="aac",
        output_path=str(output_path).replace("\\", "/"),
    )


def _tool_preflight() -> dict:
    return {
        "status": "passed",
        "failure_reason": None,
        "ffmpeg": {
            "name": "ffmpeg",
            "path": "C:/tools/ffmpeg.exe",
            "path_source": "argument",
            "available": True,
            "version": "ffmpeg version test",
            "status": "passed",
            "failure_reason": None,
            "stderr_digest": _stderr_digest(),
            "command_summary": "C:/tools/ffmpeg.exe -version",
            "exit_code": 0,
        },
        "ffprobe": {
            "name": "ffprobe",
            "path": "C:/tools/ffprobe.exe",
            "path_source": "argument",
            "available": True,
            "version": "ffprobe version test",
            "status": "passed",
            "failure_reason": None,
            "stderr_digest": _stderr_digest(),
            "command_summary": "C:/tools/ffprobe.exe -version",
            "exit_code": 0,
        },
    }


def _stderr_digest(tail: str = "") -> dict:
    return {
        "algorithm": "sha256",
        "sha256": "0" * 64,
        "tail": tail,
        "tail_chars": 1000,
        "truncated": False,
    }

