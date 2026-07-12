from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from PIL import Image

from src.integrations.render import shorts_poster_frame_proof as proof


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = (
    ROOT / "docs" / "output_layer" / "OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json"
)


def _corpus() -> dict:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_reference_corpus_has_bounded_multi_source_support() -> None:
    corpus = _corpus()
    summary = proof.validate_reference_corpus(corpus)

    assert summary == {
        "reference_count": 24,
        "channel_count": 17,
        "query_strategy_count": 3,
        "latest_120_day_count": 18,
        "date_coverage": ["2023-09-04", "2026-07-10"],
        "target_surfaces": {
            "conventional_16_9_secondary_reference": 21,
            "native_vertical_short_poster_reference": 3,
        },
        "family_counts": {
            "hero_with_reaction_inset": 8,
            "opposed_dialogue": 7,
            "single_reaction_hero": 9,
        },
    }
    assert corpus["reference_priority"] == ["user_supplied", "research_collected"]
    assert all(entry["translation_note"] for entry in corpus["references"])


def test_candidate_specs_are_distinct_safe_and_traceable() -> None:
    proof.validate_candidate_specs(proof.CANDIDATE_SPECS)

    assert [spec["candidate_id"] for spec in proof.CANDIDATE_SPECS] == ["A", "B", "C"]
    assert len({spec["family_id"] for spec in proof.CANDIDATE_SPECS}) == 3
    for spec in proof.CANDIDATE_SPECS:
        assert spec["essential_text_block_count"] == 1
        assert "back" not in spec["dominant_face_orientation"]
        assert len(spec["reference_ids"]) >= 3
        assert spec["copy_evidence"]["subtitle_ids"]
        assert spec["copy_evidence"]["segment_ids"]

    unsafe = list(deepcopy(proof.CANDIDATE_SPECS))
    unsafe[0]["essential_bounds"] = [0, 200, 1080, 1600]
    try:
        proof.validate_candidate_specs(tuple(unsafe))
    except proof.ShortsPosterFrameProofError as exc:
        assert "safe area" in str(exc)
    else:
        raise AssertionError("expected unsafe essential bounds to be rejected")


def test_poster_renderers_produce_original_vertical_rgb_compositions() -> None:
    noel = Image.new("RGB", (1920, 1080), (80, 100, 140))
    hajime = Image.new("RGB", (1920, 1080), (235, 190, 80))

    images = [
        proof._poster_a(hajime),
        proof._poster_b(noel, hajime),
        proof._poster_c(noel, hajime),
    ]
    try:
        assert all(image.size == proof.CANVAS for image in images)
        assert all(image.mode == "RGB" for image in images)
        assert len({image.getpixel((10, 10)) for image in images}) == 3
    finally:
        for image in images:
            image.close()
        noel.close()
        hajime.close()


def test_review_html_keeps_candidates_first_and_evidence_folded() -> None:
    readback = {
        "candidates": [
            {
                **spec,
                "source_frame_timestamps": spec["source_frame_timestamps"],
            }
            for spec in proof.CANDIDATE_SPECS
        ],
        "reference_corpus": {"channel_count": 17},
    }
    html = proof._render_html(readback)

    assert html.count('class="candidate"') == 3
    assert html.count("<video") == 3
    assert html.count(proof.REVIEW_QUESTION) == 1
    assert html.index('id="candidates"') < html.index("末尾transition proof")
    assert html.index("末尾transition proof") < html.index('id="evidence"')
    assert "<details open" not in html
    assert "180×320" in html
    assert "center 4:5 / 160×200" in html


def test_cli_exposes_poster_proof_help() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-shorts-poster-frame-proof",
            "--help",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0
    assert "--fetch-missing-references" in result.stdout
    assert "--reference-cache-dir" in result.stdout
