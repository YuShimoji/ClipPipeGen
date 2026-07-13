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


def test_reference_corpus_has_current_vertical_exact_surface_coverage() -> None:
    corpus = _corpus()
    summary = proof.validate_reference_corpus(corpus)

    assert summary["stored_reference_count"] == 51
    assert summary["reference_count"] == 50
    assert summary["inactive_duplicate_reference_count"] == 1
    assert summary["channel_count"] == 41
    assert summary["query_strategy_count"] == 4
    assert summary["native_vertical_exact_surface_count"] == 27
    assert summary["native_vertical_exact_surface_channel_count"] == 24
    assert summary["recent_180_day_native_vertical_exact_surface_count"] == 22
    assert summary["conventional_16_9_secondary_count"] == 20
    assert summary["conventional_16_9_ratio"] == 0.4
    assert summary["max_references_per_channel"] == 3
    assert summary["success_proxy_is_causal_proof"] is False
    assert corpus["surface_observation"]["youtube_verified"] is False
    assert corpus["success_proxy_policy"]["view_count_is_causal_proof"] is False

    references = proof._reference_entries(corpus)
    exact = [
        entry
        for entry in references
        if entry["target_surface"]
        == "native_vertical_exact_youtube_search_shorts_card"
    ]
    assert len(exact) == 27
    assert all(entry["surface_evidence_path"] for entry in exact)
    assert all(entry["face_occupancy_ratio"] is not None for entry in exact)
    assert all(entry["subject_position"] for entry in exact)
    assert all(entry["text_region"] for entry in exact)
    assert all(entry["background_treatment"] for entry in exact)
    assert all(entry["repeated_layout_usage"] for entry in exact)


def test_candidate_directions_are_research_derived_safe_and_traceable() -> None:
    corpus = _corpus()
    references = proof._reference_entries(corpus)
    specs = proof.candidate_specs_from_corpus(corpus, references=references)
    proof.validate_candidate_specs(specs, references=references)

    assert [spec["candidate_id"] for spec in specs] == ["A", "B", "C"]
    assert len({spec["family_id"] for spec in specs}) == 3
    assert specs[2]["essential_text_block_count"] == 2
    for spec in specs:
        assert "back" not in spec["dominant_face_orientation"]
        assert spec["speaker"] == spec["emotional_subject"]
        assert spec["primary_exemplar_id"] in spec["reference_ids"]
        assert len(spec["reference_ids"]) >= 3
        assert spec["primary_exemplar_proportions"]
        assert spec["copy_evidence"]["subtitle_ids"]
        assert spec["copy_evidence"]["segment_ids"]

    research_renamed = list(deepcopy(specs))
    research_renamed[0]["family_id"] = "later_research_derived_family_name"
    proof.validate_candidate_specs(tuple(research_renamed), references=references)

    unsafe = list(deepcopy(specs))
    unsafe[0]["essential_bounds"] = [0, 200, 1080, 1600]
    try:
        proof.validate_candidate_specs(tuple(unsafe), references=references)
    except proof.ShortsPosterFrameProofError as exc:
        assert "safe area" in str(exc)
    else:
        raise AssertionError("expected unsafe essential bounds to be rejected")


def test_manual_masks_and_poster_renderers_preserve_source_pixels() -> None:
    source = Image.new("RGB", (1920, 1080), (235, 190, 80))
    noel_source = Image.new("RGB", (1920, 1080), (80, 100, 140))
    hajime, hajime_mask, hajime_info = proof._manual_subject_cutout(
        source, subject="hajime_macro"
    )
    noel, noel_mask, noel_info = proof._manual_subject_cutout(
        noel_source, subject="noel_three_quarter"
    )
    images = [proof._poster_a(hajime), proof._poster_b(noel, hajime), proof._poster_c(hajime)]
    try:
        assert hajime.mode == "RGBA"
        assert noel.mode == "RGBA"
        assert hajime_mask.mode == noel_mask.mode == "L"
        assert hajime_mask.getextrema()[1] == noel_mask.getextrema()[1] == 255
        assert hajime_info["person_pixels_generated_or_modified"] is False
        assert noel_info["person_pixels_generated_or_modified"] is False
        assert all(image.size == proof.CANVAS for image in images)
        assert all(image.mode == "RGB" for image in images)
        assert len({image.getpixel((10, 10)) for image in images}) == 3
    finally:
        for image in images:
            image.close()
        hajime.close()
        hajime_mask.close()
        noel.close()
        noel_mask.close()
        source.close()
        noel_source.close()


def test_platform_preview_assets_have_required_dimensions(tmp_path: Path) -> None:
    image = Image.new("RGB", proof.CANVAS, (25, 45, 75))
    try:
        readback = proof._write_platform_previews(
            image=image,
            candidate_id="A",
            stage=tmp_path,
            output=tmp_path,
            root=tmp_path,
        )
        assert readback["channel_search_tile"]["dimensions"] == [405, 720]
        assert readback["center_4_5_heuristic"]["official_guarantee"] is False
        assert readback["shorts_playback_ui_overlay"]["approximation"] is True
        with Image.open(tmp_path / "preview_A_channel_search_tile.jpg") as preview:
            assert preview.size == (405, 720)
        with Image.open(tmp_path / "preview_A_center_4_5.jpg") as preview:
            assert preview.size == (320, 400)
        with Image.open(tmp_path / "preview_A_shorts_ui_overlay.jpg") as preview:
            assert preview.size == (405, 720)
    finally:
        image.close()


def test_review_html_keeps_candidates_first_and_evidence_folded() -> None:
    specs = proof.candidate_specs_from_corpus(_corpus())
    readback = {
        "candidates": [dict(spec) for spec in specs],
        "reference_corpus": {
            "reference_count": 50,
            "channel_count": 41,
            "native_vertical_exact_surface_count": 27,
            "conventional_16_9_secondary_count": 20,
        },
    }
    html = proof._render_html(readback)

    assert html.count('class="candidate"') == 3
    assert html.count("<video") == 3
    assert html.count(proof.REVIEW_QUESTION) == 1
    assert html.index('id="candidates"') < html.index("platform preview 一覧")
    assert html.index("platform preview 一覧") < html.index("末尾transition proof")
    assert html.index("末尾transition proof") < html.index('id="evidence"')
    assert "<details open" not in html
    assert "channel / search 405×720" in html
    assert "center 4:5 heuristic" in html
    assert "Shorts playback UI overlay" in html
    assert "hard cut" not in html.lower()


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
