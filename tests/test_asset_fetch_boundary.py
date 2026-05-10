"""INT-02b: asset_fetch boundary spec guards."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOUNDARY_DOC = REPO_ROOT / "docs" / "ASSET_FETCH_BOUNDARY.md"


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
    ]
    for needle in required:
        assert needle in text


def test_fetch_source_audio_exposes_fake_mode_only_before_real_downloader():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "fetch-source-audio", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "{fake}" in result.stdout
    assert "yt-dlp" not in result.stdout.lower()
    assert "ffmpeg" not in result.stdout.lower()


def test_ffmpeg_and_ytdlp_do_not_enter_pipeline_or_editing_cli():
    forbidden_terms = ("ffmpeg", "yt-dlp", "youtube-dl")
    checked_files = [
        *sorted((REPO_ROOT / "src" / "pipeline").glob("*.py")),
        REPO_ROOT / "src" / "cli" / "transcribe_audio.py",
        REPO_ROOT / "src" / "cli" / "generate_cuts.py",
        REPO_ROOT / "src" / "cli" / "check_cut_context.py",
        REPO_ROOT / "src" / "cli" / "generate_subtitles.py",
    ]

    violations: list[str] = []
    for path in checked_files:
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden_terms:
            if term in text:
                violations.append(f"{path.relative_to(REPO_ROOT)} contains {term}")

    assert violations == []
