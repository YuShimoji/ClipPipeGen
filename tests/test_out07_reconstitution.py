from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from src.integrations.render import complete_narrative_short as complete
from src.integrations.render import out07_reconstitution as rebuild
from src.integrations.render import shorts_poster_frame_proof as historical_poster


ROOT = Path(__file__).resolve().parents[1]


def _semantic_fixture() -> tuple[dict, dict, dict]:
    cuts = [
        {
            "id": "cut_001",
            "start_seconds": 2.453,
            "end_seconds": 9.293,
            "context_check": {"status": "passed"},
        },
        {
            "id": "cut_002",
            "start_seconds": 12.329,
            "end_seconds": 17.167,
            "context_check": {"status": "passed"},
        },
        {
            "id": "cut_003",
            "start_seconds": 22.606,
            "end_seconds": 49.566,
            "context_check": {"status": "needs_review"},
        },
    ]
    cut_ranges = {
        "cut_001": (2.453, 9.293, range(1, 8)),
        "cut_002": (12.329, 17.167, range(8, 10)),
        "cut_003": (22.606, 49.566, range(10, 30)),
    }
    subtitles = []
    segments = []
    for cut_id, (start, end, indexes) in cut_ranges.items():
        indexes = list(indexes)
        width = (end - start) / len(indexes)
        for offset, index in enumerate(indexes):
            item_start = start + offset * width
            item_end = (
                end if offset == len(indexes) - 1 else start + (offset + 1) * width
            )
            subtitle_id = f"sub_{index:03d}"
            segment_id = f"seg_{index:06d}"
            text = f"fixture {index}"
            subtitles.append(
                {
                    "id": subtitle_id,
                    "cut_id": cut_id,
                    "start_seconds": round(item_start, 6),
                    "end_seconds": round(item_end, 6),
                    "text": text,
                    "source_type": "imported_subtitle_track",
                    "source_segment_ids": [segment_id],
                }
            )
            segments.append(
                {
                    "id": segment_id,
                    "start_seconds": round(item_start, 6),
                    "end_seconds": round(item_end, 6),
                    "text": text,
                    "review_status": "accepted",
                }
            )
    subtitles.append(
        {
            "id": "sub_030",
            "cut_id": "cut_004",
            "start_seconds": 50.868,
            "end_seconds": 53.904,
            "text": "excluded",
            "source_segment_ids": ["seg_000030"],
        }
    )
    decisions = [
        {
            "cut_id": "cut_001",
            "final_cut_decision": "keep",
            "context_status": "passed",
        },
        {
            "cut_id": "cut_002",
            "final_cut_decision": "keep",
            "context_status": "passed",
        },
        {
            "cut_id": "cut_003",
            "final_cut_decision": "keep",
            "context_status": "needs_review",
            "manual_override_reason": "retain visible context risk for candidate review",
        },
    ]
    return (
        {"cut_candidates": cuts, "subtitles": subtitles},
        {"segments": segments},
        {"decisions": decisions},
    )


def test_revision_semantic_route_needs_no_historical_predecessor() -> None:
    edit_pack, transcript, decision = _semantic_fixture()

    timeline, subtitles = rebuild._semantic_timeline(
        edit_pack=edit_pack,
        transcript=transcript,
        decision=decision,
    )

    assert [item["id"] for item in timeline] == ["cut_001", "cut_002", "cut_003"]
    assert [item["sequence_end_seconds"] for item in timeline] == [6.84, 11.678, 38.638]
    assert [item["id"] for item in subtitles] == list(complete.EXPECTED_SUBTITLE_IDS)
    assert subtitles[-1]["sequence_end_seconds"] == 38.638
    assert all(item["id"] != "sub_030" for item in subtitles)


@pytest.mark.parametrize("drift", ["decision", "mapping", "sub030"])
def test_revision_semantic_route_rejects_authority_drift(drift: str) -> None:
    edit_pack, transcript, decision = _semantic_fixture()
    if drift == "decision":
        decision["decisions"][2]["final_cut_decision"] = "needs_adjustment"
    elif drift == "mapping":
        edit_pack["subtitles"][12]["source_segment_ids"] = ["seg_999999"]
    else:
        edit_pack["subtitles"][-1]["cut_id"] = "cut_003"

    with pytest.raises(rebuild.Out07ReconstitutionError):
        rebuild._semantic_timeline(
            edit_pack=edit_pack,
            transcript=transcript,
            decision=decision,
        )


def test_historical_fixed_hash_path_remains_distinct() -> None:
    assert historical_poster.SOURCE_VIDEO_SHA256 == rebuild.HISTORICAL_SOURCE_SHA256
    assert historical_poster.ACCEPTED_VIDEO_SHA256 == (
        rebuild.HISTORICAL_ACCEPTED_BASELINE_SHA256
    )
    assert rebuild.CURRENT_SOURCE_SHA256 != historical_poster.SOURCE_VIDEO_SHA256


def test_canonical_digest_is_stable_and_reference_evidence_is_separable() -> None:
    core = {"source": rebuild.CURRENT_SOURCE_SHA256, "files": [{"sha256": "a" * 64}]}
    same_core = deepcopy(core)
    references = {
        "references": [{"url": "https://example.invalid/a", "sha256": "b" * 64}]
    }

    assert rebuild._canonical_digest(core) == rebuild._canonical_digest(same_core)
    assert rebuild._canonical_digest(core) != rebuild._canonical_digest(references)


def test_tracked_semantic_authority_is_complete_but_contains_no_caption_text() -> None:
    contract = json.loads(
        (ROOT / "artifacts" / "ACTIVE_REBUILD.json").read_text(encoding="utf-8")
    )

    timeline, subtitles, decision, proxy = rebuild._semantic_authority_from_contract(
        contract
    )

    assert [item["id"] for item in timeline] == list(complete.EXPECTED_CUT_IDS)
    assert [item["id"] for item in subtitles] == list(complete.EXPECTED_SUBTITLE_IDS)
    assert all("text" not in item and "wrapped_lines" not in item for item in subtitles)
    assert all(len(item["text_sha256"]) == 64 for item in subtitles)
    assert subtitles[-1]["sequence_end_seconds"] == 38.638
    assert [item["cut_id"] for item in decision["decisions"]] == list(
        complete.EXPECTED_CUT_IDS
    )
    assert proxy["status"] == "validated_from_tracked_rebuild_contract"


def test_hash_only_contract_rehydrates_from_caption_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract_rows = []
    events = []
    digest_rows = []
    for index in range(1, 30):
        subtitle_id = f"sub_{index:03d}"
        separator = "\u3000" if index in {20, 25} else " "
        text = f"fixture{separator}caption {index}"
        start = (index - 1) * 0.25
        end = start + 0.25
        text_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        contract_rows.append(
            {
                "id": subtitle_id,
                "cut_id": "cut_001",
                "source_segment_ids": [f"seg_{index:06d}"],
                "source_start_seconds": start,
                "source_end_seconds": end,
                "sequence_start_seconds": start,
                "sequence_end_seconds": end,
                "text_sha256": text_sha256,
            }
        )
        events.append(
            {
                "tStartMs": int(start * 1000),
                "dDurationMs": 250,
                "segs": [{"utf8": f"\u200b{text}\u200b"}],
            }
        )
        digest_rows.append({"id": subtitle_id, "text_sha256": text_sha256})
    digest = hashlib.sha256(
        json.dumps(digest_rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    monkeypatch.setattr(rebuild, "CAPTION_PAYLOAD_DIGEST", digest)

    hydrated = rebuild._rehydrate_semantic_subtitles_from_caption(
        subtitle_contract=contract_rows,
        subtitle_track={"events": events},
    )

    assert len(hydrated) == 29
    assert hydrated[0]["text"] == "fixture caption 1"
    assert hydrated[19]["text"] == "fixture\u3000caption 20"
    assert hydrated[24]["text"] == "fixture\u3000caption 25"
    assert hydrated[-1]["text"] == "fixture caption 29"


def test_episode_identity_validator_rejects_transcript_or_edit_pack_drift() -> None:
    with pytest.raises(rebuild.Out07ReconstitutionError):
        rebuild._validate_episode_identity(
            episode_id=rebuild.EPISODE_ID,
            values={
                "rights": rebuild.EPISODE_ID,
                "decision": rebuild.EPISODE_ID,
                "edit_pack": "different_episode",
                "transcript": rebuild.EPISODE_ID,
                "operator_proxy": rebuild.EPISODE_ID,
            },
        )


def test_contract_authority_fallback_requires_caption_reacquisition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path
    contract_dir = root / "artifacts"
    contract_dir.mkdir()
    contract_dir.joinpath("ACTIVE_REBUILD.json").write_text(
        (ROOT / "artifacts" / "ACTIVE_REBUILD.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    episode = root / "episodes" / rebuild.EPISODE_ID
    video_dir = episode / "materials" / rebuild.SOURCE_MATERIAL_ID
    audio_dir = episode / "materials" / rebuild.AUDIO_MATERIAL_ID
    video_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)
    video = video_dir / "source_video.mp4"
    audio = audio_dir / "source.wav"
    video.write_bytes(b"video fixture")
    audio.write_bytes(b"audio fixture")

    def rel(path: Path) -> str:
        return path.relative_to(root).as_posix()

    video_sidecar = video_dir / "sidecar.json"
    audio_sidecar = audio_dir / "sidecar.json"
    video_receipt = video_dir / "fetch_receipt.json"
    audio_receipt = audio_dir / "fetch_receipt.json"
    video_sidecar.write_text(
        json.dumps(
            {
                "asset_id": rebuild.SOURCE_MATERIAL_ID,
                "asset_path": rel(video),
                "asset_hash_sha256": rebuild.CURRENT_SOURCE_SHA256,
            }
        ),
        encoding="utf-8",
    )
    audio_sidecar.write_text(
        json.dumps(
            {
                "asset_id": rebuild.AUDIO_MATERIAL_ID,
                "asset_path": rel(audio),
                "asset_hash_sha256": rebuild.CURRENT_AUDIO_SHA256,
            }
        ),
        encoding="utf-8",
    )
    video_receipt.write_text(
        json.dumps(
            {
                "material_id": rebuild.SOURCE_MATERIAL_ID,
                "output_path": rel(video),
                "sha256": rebuild.CURRENT_SOURCE_SHA256,
                "mode": "yt-dlp-video",
                "video_metadata": {"duration_seconds": 164.768798},
            }
        ),
        encoding="utf-8",
    )
    audio_receipt.write_text(
        json.dumps(
            {
                "material_id": rebuild.AUDIO_MATERIAL_ID,
                "output_path": rel(audio),
                "sha256": rebuild.CURRENT_AUDIO_SHA256,
                "mode": "yt-dlp-audio",
            }
        ),
        encoding="utf-8",
    )
    episode.joinpath("material_ledger.json").write_text(
        json.dumps(
            {
                "materials": [
                    {
                        "id": rebuild.SOURCE_MATERIAL_ID,
                        "file_path": rel(video),
                        "sidecar_path": rel(video_sidecar),
                        "hash_sha256": rebuild.CURRENT_SOURCE_SHA256,
                    },
                    {
                        "id": rebuild.AUDIO_MATERIAL_ID,
                        "file_path": rel(audio),
                        "sidecar_path": rel(audio_sidecar),
                        "hash_sha256": rebuild.CURRENT_AUDIO_SHA256,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    episode.joinpath("rights_manifest.json").write_text(
        json.dumps({"episode_id": rebuild.EPISODE_ID}), encoding="utf-8"
    )
    original_sha256 = rebuild._sha256

    def fixture_sha256(path: Path) -> str:
        if path == video:
            return rebuild.CURRENT_SOURCE_SHA256
        if path == audio:
            return rebuild.CURRENT_AUDIO_SHA256
        return original_sha256(path)

    monkeypatch.setattr(rebuild, "_sha256", fixture_sha256)

    with pytest.raises(
        rebuild.Out07ReconstitutionError,
        match="caption_authority_reacquire_required",
    ):
        rebuild.load_current_episode_authority(
            episode_dir=episode,
            base_dir=root,
            execute_media_checks=False,
        )

    assert not (episode / "review").exists()
    assert rebuild._ensure_review_directory(episode) == episode / "review"
    assert (episode / "review").is_dir()


@pytest.mark.parametrize("byte_identical", [False, True])
def test_combined_readback_preserves_hash_gated_acceptance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    byte_identical: bool,
) -> None:
    monkeypatch.setattr(rebuild, "_verified_host", lambda: "fixture-host")
    readback = {"accepted_video": {}, "storage": {}, "gates": {}}
    classification = (
        "historical_byte_identical_acceptance_carried_forward"
        if byte_identical
        else "reinstantiated_baseline_candidate"
    )
    baseline_data = {
        "render": {"sha256": "a" * 64},
        "acceptance_inheritance": {
            "classification": classification,
            "byte_identical_to_historical_accepted_output": byte_identical,
            "human_acceptance": byte_identical,
        },
    }
    output = tmp_path / "episodes" / rebuild.EPISODE_ID / "review" / "combined"
    authority = {
        "source_hash": rebuild.CURRENT_SOURCE_SHA256,
        "episode": tmp_path / "episodes" / rebuild.EPISODE_ID,
    }
    reference_manifest = {
        "fetch_revision": {"revision_id": "fixture", "failure_count": 0},
        "reference_evidence_digest": "b" * 64,
    }

    rebuild._apply_revision_readback(
        readback=readback,
        root=tmp_path,
        output=output,
        authority=authority,
        baseline_data=baseline_data,
        reference_manifest=reference_manifest,
    )

    assert readback["baseline"]["human_acceptance"] is byte_identical
    assert readback["accepted_video"]["human_acceptance"] is byte_identical
    assert readback["portability"]["last_verified_host"] == "fixture-host"


@pytest.mark.parametrize("byte_identical", [False, True])
def test_hash_gated_acceptance_is_consistent_in_plan_and_manifests(
    tmp_path: Path, byte_identical: bool
) -> None:
    edit_pack, transcript, decision = _semantic_fixture()
    _, subtitles = rebuild._semantic_timeline(
        edit_pack=edit_pack,
        transcript=transcript,
        decision=decision,
    )
    presentation = [
        {
            "subtitle_id": item["id"],
            "display_start_seconds": item["sequence_start_seconds"],
            "display_end_seconds": item["sequence_end_seconds"],
            "wrapped_lines": [item["text"]],
        }
        for item in subtitles
    ]
    authority = {
        "episode": tmp_path / rebuild.EPISODE_ID,
        "semantic_subtitles": subtitles,
        "decision": decision,
        "proxy_authority": {"status": "fixture"},
        "timeline": [],
    }
    plan = rebuild._baseline_plan(authority=authority, subtitle_items=presentation)
    plan["cut003_limitation"]["new_human_acceptance_required"] = not byte_identical
    plan["boundaries"] = rebuild._closed_gates(human_baseline_acceptance=byte_identical)

    output = tmp_path / "combined"
    output.mkdir()
    (output / "payload.txt").write_text("fixture", encoding="utf-8")
    manifest = rebuild._combined_manifest(
        output=output,
        root=tmp_path,
        human_baseline_acceptance=byte_identical,
    )

    assert plan["cut003_limitation"]["new_human_acceptance_required"] is (
        not byte_identical
    )
    assert plan["boundaries"]["human_baseline_acceptance"] is byte_identical
    assert manifest["gates"]["human_baseline_acceptance"] is byte_identical


def test_combined_html_is_baseline_first_with_exactly_two_questions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rebuild.poster,
        "_render_html",
        lambda _: (
            "<html><head><title>fixture</title></head><body><header>old</header>"
            '<section id="candidates"></section><script>\nconst media=[];</script>'
            "</body></html>"
        ),
    )
    html = rebuild._combined_html(
        {
            "baseline": {
                "byte_identical_to_historical_accepted_output": False,
                "sha256": "a" * 64,
            },
            "media_revision": {"current_source_sha256": "b" * 64},
        }
    )

    assert html.count('class="question"') == 2
    assert html.index('id="reinstantiated-baseline"') < html.index('id="candidates"')
    assert '<link rel="icon" href="data:,">' in html
    assert "旧動画のbyte acceptanceは自動継承していません" in html


def test_portable_payload_scrubs_external_absolute_paths(tmp_path: Path) -> None:
    portable = rebuild._portable_payload(
        {
            "font_file": r"C:\Users\operator\Fonts\keifont.ttf",
            "repo_file": str(tmp_path / "artifact.json"),
        },
        root=tmp_path,
    )

    assert portable["font_file"] == "external_dependency/keifont.ttf"
    assert portable["repo_file"] == "artifact.json"


def test_reconstitution_cli_exposes_revision_and_determinism_controls() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "reconstitute-out07-review",
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
    assert "--verify-determinism" in result.stdout
