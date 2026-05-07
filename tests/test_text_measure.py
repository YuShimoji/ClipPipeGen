"""ED-05: minimum tests for EAW subtitle width measurement.

positive 1 + critical negatives. Don't pad coverage.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.text_measure import (
    char_eaw_width,
    measure_subtitle,
    text_eaw_width,
    wrap_by_eaw,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_ascii_is_one_unit_per_char():
    assert char_eaw_width("a") == 1
    assert char_eaw_width("Z") == 1
    assert text_eaw_width("hello") == 5


def test_japanese_is_two_units_per_char():
    assert char_eaw_width("あ") == 2
    assert char_eaw_width("漢") == 2
    assert text_eaw_width("ぺこら") == 6


def test_mixed_text_sums_correctly():
    # "ab漢字" -> 1 + 1 + 2 + 2 = 6
    assert text_eaw_width("ab漢字") == 6


def test_ambiguous_default_is_one_but_overridable():
    # § (U+00A7) is "A" (Ambiguous)
    assert char_eaw_width("§") == 1
    assert char_eaw_width("§", ambiguous_width=2) == 2


def test_measure_below_wrap_target_does_not_need_wrap():
    m = measure_subtitle("hello", wrap_eaw=40)
    assert m.needs_wrap is False
    assert m.total_eaw_units == 5
    assert len(m.lines) == 1
    assert m.lines[0].overflows is False


def test_measure_above_wrap_target_wraps_japanese_at_char_break():
    text = "あ" * 30  # 60 EAW units
    m = measure_subtitle(text, wrap_eaw=40)
    assert m.needs_wrap is True
    assert m.total_eaw_units == 60
    # 30 chars * 2 units = 60. wrap at 40 -> first line max 20 chars (40 units), then 10 chars (20 units)
    assert len(m.lines) == 2
    assert m.lines[0].eaw_units <= 40
    assert m.lines[1].eaw_units <= 40
    assert sum(line.eaw_units for line in m.lines) == 60
    assert all(not line.overflows for line in m.lines)


def test_wrap_with_whitespace_breaks_on_space():
    text = "hello world example sentence"
    lines = wrap_by_eaw(text, wrap_eaw=12)
    # greedy whitespace-aware wrap; each line <= 12
    for line in lines:
        assert text_eaw_width(line) <= 12
    rejoined = " ".join(lines)
    # all original tokens are preserved
    assert sorted(rejoined.split()) == sorted(text.split())


def test_invalid_wrap_eaw_raises():
    import pytest

    with pytest.raises(ValueError):
        wrap_by_eaw("text", wrap_eaw=0)


def test_cli_text_only(tmp_path: Path):
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "measure-subtitle-width",
            "--text",
            "ぺこら、まさかの大爆笑",
            "--wrap-eaw",
            "20",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    payload = json.loads(res.stdout)
    assert payload["total_chars"] == len("ぺこら、まさかの大爆笑")
    assert payload["total_eaw_units"] == 22
    assert payload["wrap_eaw"] == 20
    assert payload["needs_wrap"] is True
    assert res.returncode == 1  # exit 1 == needs_wrap


def test_cli_no_wrap_target_is_zero_when_short(tmp_path: Path):
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "measure-subtitle-width",
            "--text",
            "hi",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    payload = json.loads(res.stdout)
    assert payload["total_eaw_units"] == 2
    assert payload["wrap_eaw"] is None
    assert payload["needs_wrap"] is False
    assert res.returncode == 0
