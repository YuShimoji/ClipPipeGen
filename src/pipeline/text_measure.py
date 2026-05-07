"""ED-05: subtitle width measurement (East Asian Width based).

Why this lives in ClipPipeGen instead of bridging NLMYTGen
---------------------------------------------------------
NLMYTGen has `EastAsianWidthMeasurer` / `WpfTextMeasurer` inside
`src/pipeline/text_measure.py`, but no standalone CLI exposes them
(measurement is embedded in `build-csv`). Until NLMYTGen exposes
a `measure-text` CLI (see `docs/proposals/0002-...`), we keep a
small stdlib-only EAW measurer here. This is intentional
duplication, kept minimal so future replacement by a NLMYTGen
bridge is straightforward.

Scope
-----
- Subtitle planning side: how many EAW units does this text
  occupy? Will it overflow at a given wrap target?
- Not pixel-perfect YMM4 layout. For that, the user still has
  the option to run NLMYTGen's `build-csv --measure-backend wpf`
  pipeline, and we propose a standalone CLI for closer bridging.

Conventions
-----------
- EAW codes "F" / "W" -> 2 units (full-width).
- "Na" / "H" / "N" -> 1 unit (narrow / half-width / neutral).
- "A" (Ambiguous) defaults to 1 unit (more useful for ASCII-heavy
  subtitles); callers can override via `ambiguous_width=2` if
  they want CJK-style ambiguous treatment.
- Wrapping is greedy by EAW units, breaks on whitespace when
  available. CJK strings without whitespace fall back to char-by-
  char break (typical for Japanese subtitles).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Iterable


@dataclass
class SubtitleMeasurement:
    text: str
    total_chars: int
    total_eaw_units: int
    wrap_eaw: int | None
    lines: list["MeasuredLine"]
    longest_line_eaw: int
    needs_wrap: bool

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "total_chars": self.total_chars,
            "total_eaw_units": self.total_eaw_units,
            "wrap_eaw": self.wrap_eaw,
            "longest_line_eaw": self.longest_line_eaw,
            "needs_wrap": self.needs_wrap,
            "lines": [line.to_dict() for line in self.lines],
        }


@dataclass
class MeasuredLine:
    text: str
    eaw_units: int
    overflows: bool

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "eaw_units": self.eaw_units,
            "overflows": self.overflows,
        }


def char_eaw_width(ch: str, *, ambiguous_width: int = 1) -> int:
    """Return EAW unit width of a single character. Default: A=1."""
    if not ch:
        return 0
    code = unicodedata.east_asian_width(ch)
    if code in ("F", "W"):
        return 2
    if code == "A":
        return ambiguous_width
    # "Na", "H", "N"
    return 1


def text_eaw_width(text: str, *, ambiguous_width: int = 1) -> int:
    return sum(char_eaw_width(c, ambiguous_width=ambiguous_width) for c in text)


def wrap_by_eaw(
    text: str,
    *,
    wrap_eaw: int,
    ambiguous_width: int = 1,
) -> list[str]:
    """Greedy wrap by EAW units. Whitespace-aware; falls back to char break.

    Returns a list of wrapped line strings. Newlines in input are honored
    as hard breaks.
    """
    if wrap_eaw <= 0:
        raise ValueError("wrap_eaw must be positive")

    out: list[str] = []
    for paragraph in text.splitlines() or [text]:
        out.extend(_wrap_single(paragraph, wrap_eaw, ambiguous_width))
    return out


def _wrap_single(
    paragraph: str, wrap_eaw: int, ambiguous_width: int
) -> list[str]:
    if not paragraph:
        return [""]

    width = lambda s: text_eaw_width(s, ambiguous_width=ambiguous_width)

    if width(paragraph) <= wrap_eaw:
        return [paragraph]

    # whitespace-tokenised wrap when possible
    if any(c.isspace() for c in paragraph):
        tokens = _tokenise_keep_spaces(paragraph)
        lines: list[str] = []
        current = ""
        for tok in tokens:
            candidate = current + tok
            if width(candidate) <= wrap_eaw:
                current = candidate
                continue
            if current:
                lines.append(current.rstrip())
                current = tok.lstrip() if tok.isspace() else tok
            else:
                # single token already over — char-break this token
                lines.extend(_char_break(tok, wrap_eaw, ambiguous_width))
                current = ""
        if current:
            lines.append(current.rstrip())
        return lines

    # CJK fallback: char-by-char
    return _char_break(paragraph, wrap_eaw, ambiguous_width)


def _tokenise_keep_spaces(s: str) -> list[str]:
    out: list[str] = []
    buf = ""
    in_space = False
    for c in s:
        is_sp = c.isspace()
        if buf and (is_sp != in_space):
            out.append(buf)
            buf = ""
        buf += c
        in_space = is_sp
    if buf:
        out.append(buf)
    return out


def _char_break(s: str, wrap_eaw: int, ambiguous_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    cur_w = 0
    for ch in s:
        w = char_eaw_width(ch, ambiguous_width=ambiguous_width)
        if cur_w + w > wrap_eaw and current:
            lines.append(current)
            current = ""
            cur_w = 0
        current += ch
        cur_w += w
    if current:
        lines.append(current)
    return lines


def measure_subtitle(
    text: str,
    *,
    wrap_eaw: int | None = None,
    ambiguous_width: int = 1,
) -> SubtitleMeasurement:
    """Measure a subtitle text. If wrap_eaw given, also compute wrapped lines."""
    total_chars = len(text)
    total_eaw = text_eaw_width(text, ambiguous_width=ambiguous_width)

    if wrap_eaw is None:
        line_strs = text.splitlines() or ([text] if text else [])
    else:
        line_strs = wrap_by_eaw(text, wrap_eaw=wrap_eaw, ambiguous_width=ambiguous_width)

    measured_lines: list[MeasuredLine] = []
    for s in line_strs:
        w = text_eaw_width(s, ambiguous_width=ambiguous_width)
        overflows = wrap_eaw is not None and w > wrap_eaw
        measured_lines.append(MeasuredLine(text=s, eaw_units=w, overflows=overflows))

    longest = max((line.eaw_units for line in measured_lines), default=0)
    needs_wrap = wrap_eaw is not None and (
        total_eaw > wrap_eaw or any(line.overflows for line in measured_lines)
    )

    return SubtitleMeasurement(
        text=text,
        total_chars=total_chars,
        total_eaw_units=total_eaw,
        wrap_eaw=wrap_eaw,
        lines=measured_lines,
        longest_line_eaw=longest,
        needs_wrap=needs_wrap,
    )
