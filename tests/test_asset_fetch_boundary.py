"""INT-02b/INT-02c/INT-02d/INT-02e/INT-02g: asset_fetch boundary guards."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOUNDARY_DOC = REPO_ROOT / "docs" / "ASSET_FETCH_BOUNDARY.md"
YTDLP_AUDIO_SPEC = REPO_ROOT / "docs" / "YTDLP_AUDIO_SPEC.md"
YTDLP_VIDEO_SPEC = REPO_ROOT / "docs" / "YTDLP_VIDEO_SPEC.md"


def test_asset_fetch_boundary_spec_names_required_contracts():
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    required = [
        "INT-02b は **spec only**",
        "URL から元 media を取得する",
        "source audio を `source.wav`",
        "PCM WAV / mono / 16kHz / 16-bit",
        "`transcribe-audio`",
        "`generate-cuts`",
        "`check-cut-context`",
        "cut / concat / subtitle burn-in / render / encode",
        "`commands[].summary`",
        "`tools[].version`",
        "`stderr_digest`",
        "`rollback.files[]`",
        "INT-02d は **spec only**",
        "YTDLP_AUDIO_SPEC.md",
        "INT-02g は **spec only**",
        "YTDLP_VIDEO_SPEC.md",
        "INT-02g yt-dlp-video spec only",
        "INT-02h yt-dlp-video implementation boundary",
        "implemented in INT-02h",
    ]
    for needle in required:
        assert needle in text


def test_ytdlp_audio_spec_keeps_url_fetch_boundaries_explicit():
    text = YTDLP_AUDIO_SPEC.read_text(encoding="utf-8")

    required = [
        "INT-02d は **spec only**",
        "network fetch",
        "yt-dlp 実行",
        "URL input",
        "network access",
        "yt-dlp",
        "FFmpeg",
        "receipt",
        "権利確認",
        "人間責務",
        "GUI 非露出",
        "STT 非接続",
        "rights",
        "human responsibility",
        "GUI",
        "STT",
        "dry-run",
        "intermediate.retained=false",
        "transcribe-audio",
        "fetch-source-video",
        "creative acceptance",
    ]
    for needle in required:
        assert needle in text


def test_ytdlp_video_spec_keeps_url_fetch_boundaries_explicit():
    text = YTDLP_VIDEO_SPEC.read_text(encoding="utf-8")

    required = [
        "INT-02g は **spec only**",
        "network fetch",
        "yt-dlp 実行",
        "URL input",
        "network access",
        "yt-dlp",
        "FFprobe",
        "receipt",
        "権利確認",
        "人間責務",
        "GUI 非露出",
        "rights",
        "human responsibility",
        "GUI",
        "dry-run",
        "URL Scrub Contract",
        "intermediate_retained=false",
        "fetch-source-video --mode yt-dlp-video",
        "Format Selection Constraint",
        "ホワイトリスト",
        "transcribe-audio",
        "render-tiny-proof",
        "creative acceptance",
        "hard_gate",
        "production_acceptance",
        "INT-02h",
    ]
    for needle in required:
        assert needle in text


def test_fetch_source_audio_exposes_only_source_audio_modes():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "fetch-source-audio", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "{fake,local-media-audio,yt-dlp-audio}" in result.stdout
    assert "--local-media" in result.stdout
    assert "--ffmpeg-path" in result.stdout
    assert "--yt-dlp-path" in result.stdout
    assert "yt-dlp-audio" in result.stdout.lower()
    assert "fetch-source-video" not in result.stdout.lower()


def test_fetch_source_video_exposes_video_acquisition_modes_only():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "fetch-source-video", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    help_text = result.stdout.lower()
    assert "local-media-video" in help_text
    assert "yt-dlp-video" in help_text
    assert "--source-path" in help_text
    assert "--source-url" in help_text
    assert "--ffprobe-path" in help_text
    assert "--yt-dlp-path" in help_text
    assert "--format-selector" in help_text
    assert "render" not in help_text
    assert "encode" not in help_text


def test_build_local_preview_pack_exposes_no_external_fetch_or_output_generation():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "build-local-preview-pack", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    help_text = result.stdout.lower()
    assert "--local-media" in help_text
    assert "--transcript-fixture" in help_text
    assert "yt-dlp" not in help_text
    assert "fetch-source-video" not in help_text
    assert "network" not in help_text
    assert "render" not in help_text
    assert "encode" not in help_text


def test_ffmpeg_and_ytdlp_do_not_enter_pipeline_or_editing_cli():
    forbidden_terms = ("ffmpeg", "yt-dlp", "youtube-dl")
    pipeline_readback_only = {"docs_dashboard.py"}
    checked_files = [
        *[
            path
            for path in sorted((REPO_ROOT / "src" / "pipeline").glob("*.py"))
            if path.name not in pipeline_readback_only
        ],
        REPO_ROOT / "src" / "cli" / "transcribe_audio.py",
        REPO_ROOT / "src" / "cli" / "generate_cuts.py",
        REPO_ROOT / "src" / "cli" / "check_cut_context.py",
        REPO_ROOT / "src" / "cli" / "generate_subtitles.py",
        REPO_ROOT / "src" / "cli" / "build_local_preview_pack.py",
    ]

    violations: list[str] = []
    for path in checked_files:
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden_terms:
            if term in text:
                violations.append(f"{path.relative_to(REPO_ROOT)} contains {term}")

    assert violations == []
