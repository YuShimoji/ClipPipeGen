from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import main as cli_main
from src.integrations.render import generated_video_challenge as challenge
from src.integrations.render.vertical_short_candidate import (
    VerticalShortCandidateError,
    build_vertical_subtitle_presentation,
)


def _subtitle(subtitle_id: str, text: str, start: float) -> dict[str, object]:
    return {
        "id": subtitle_id,
        "cut_id": "cut_003",
        "sequence_start_seconds": start,
        "sequence_end_seconds": start + 1.0,
        "text": text,
        "source_text": text,
        "source_type": "imported_subtitle_track",
        "source_segment_ids": [f"seg_{subtitle_id[-3:]}"],
    }


def test_challenge_mechanical_profile_limits_known_long_cues_to_two_lines() -> None:
    subtitles = [
        _subtitle("sub_009", "ホロライブの番長として、 団長を倒してやる！！", 0.0),
        _subtitle("sub_013", "なんで来なかったんすか！！", 1.0),
        _subtitle("sub_024", "団長、ちなみに、他の番長知ってますか？", 2.0),
        _subtitle("sub_029", "ありがとうございますー！", 3.0),
    ]

    layout, items, selector = build_vertical_subtitle_presentation(
        subtitles,
        application_key="generated_video_challenge_application",
        dimension_source="test_generated_video_challenge",
        line_break_hints=challenge.MECHANICAL_LINE_BREAK_HINTS,
        font_size_override=challenge.FONT_SIZE,
        maximum_lines=challenge.MAXIMUM_LINES,
    )
    readback = challenge.validate_mechanical_subtitles(
        items,
        maximum_lines=challenge.MAXIMUM_LINES,
        minimum_display_seconds=challenge.MINIMUM_DISPLAY_SECONDS,
    )

    assert layout["values"]["font_size"] == 76
    assert selector["generated_video_challenge_application"][
        "mechanical_maximum_lines"
    ] == 2
    assert readback["maximum_line_count"] == 2
    assert all(len(item["wrapped_lines"]) <= 2 for item in items)
    assert next(item for item in items if item["subtitle_id"] == "sub_024")[
        "wrapped_lines"
    ] == ["団長、ちなみに、", "他の番長知ってますか？"]


def test_challenge_mechanical_profile_rejects_one_character_final_line() -> None:
    with pytest.raises(challenge.GeneratedVideoChallengeError, match="one-character"):
        challenge.validate_mechanical_subtitles(
            [
                {
                    "subtitle_id": "sub_bad",
                    "wrapped_lines": ["長い本文", "字"],
                    "display_start_seconds": 0.0,
                    "display_end_seconds": 1.0,
                    "font_bbox_wrap_readback": {
                        "selected_wrapped_lines": ["長い本文", "字"]
                    },
                    "suspicious_tail_line_present": False,
                }
            ],
            maximum_lines=2,
            minimum_display_seconds=0.5,
        )


def test_challenge_mechanical_profile_accepts_short_exclamation_window() -> None:
    result = challenge.validate_mechanical_subtitles(
        [
            {
                "subtitle_id": "sub_short",
                "wrapped_lines": ["団長！！"],
                "display_start_seconds": 0.0,
                "display_end_seconds": 0.467,
                "font_bbox_wrap_readback": {"selected_wrapped_lines": ["団長！！"]},
                "suspicious_tail_line_present": False,
            }
        ],
        maximum_lines=2,
        minimum_display_seconds=challenge.MINIMUM_DISPLAY_SECONDS,
    )

    assert result["minimum_display_seconds"] == 0.467


def test_shared_vertical_profile_defaults_stay_bounded() -> None:
    with pytest.raises(VerticalShortCandidateError, match="maximum_lines"):
        build_vertical_subtitle_presentation(
            [_subtitle("sub_001", "test", 0.0)],
            application_key="test",
            dimension_source="test",
            maximum_lines=4,
        )
    with pytest.raises(VerticalShortCandidateError, match="font_size_override"):
        build_vertical_subtitle_presentation(
            [_subtitle("sub_001", "test", 0.0)],
            application_key="test",
            dimension_source="test",
            font_size_override=24,
        )


def test_challenge_destination_refuses_existing_output_before_source_preflight(
    tmp_path: Path,
) -> None:
    episode = tmp_path / challenge.source_authority.EPISODE_ID
    review = episode / "review"
    output = review / challenge.DEFAULT_OUTPUT_NAME
    output.mkdir(parents=True)

    with pytest.raises(challenge.GeneratedVideoChallengeError, match="refusing overwrite"):
        challenge.build_generated_video_challenge(
            episode_dir=episode,
            output_dir=output,
            base_dir=tmp_path,
        )


def test_manifest_validation_detects_payload_tampering(tmp_path: Path) -> None:
    package = tmp_path / "package"
    for name in challenge.REQUIRED_FILES:
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if name == "validation_readback.json":
            path.write_text(
                json.dumps(
                    {
                        "state": challenge.STATE,
                        "human_viewing_claimed": False,
                        "production_acceptance": False,
                        "public_ready": False,
                    }
                ),
                encoding="utf-8",
            )
        elif name == "generation_receipt.json":
            path.write_text(
                json.dumps(
                    {
                        "serve_command": "python -m src.cli.serve_review --root package --port 8077"
                    }
                ),
                encoding="utf-8",
            )
        elif name == "review/serve_review.ps1":
            path.write_text(
                "python -m src.cli.serve_review --root $packageRoot --port $Port\n",
                encoding="utf-8",
            )
        else:
            path.write_bytes(name.encode("utf-8"))
    video = package / "assets/challenge.mp4"
    receipt = {
        "video_sha256": challenge._sha256(video),
        "serve_command": "python -m src.cli.serve_review --root package --port 8077",
    }
    (package / "generation_receipt.json").write_text(
        json.dumps(receipt), encoding="utf-8"
    )
    manifest = challenge._manifest(stage=package, output=package, root=tmp_path)
    challenge._write_json(package / "manifest.json", manifest)

    challenge.validate_challenge_package(package)
    (package / "review/index.html").write_text("tampered", encoding="utf-8")
    with pytest.raises(challenge.GeneratedVideoChallengeError, match="manifest mismatch"):
        challenge.validate_challenge_package(package)


def test_cli_registers_generated_video_challenge(capsys: pytest.CaptureFixture[str]) -> None:
    assert "build-generated-video-challenge" in cli_main.SUBCOMMANDS
    with pytest.raises(SystemExit) as exc:
        cli_main.main(["build-generated-video-challenge", "--help"])
    assert exc.value.code == 0
    help_text = capsys.readouterr().out
    assert "without" in help_text
    assert "substituting" in help_text


def test_portable_policy_contains_no_runtime_task_id() -> None:
    text = Path("docs/AUTOMATION_BOUNDARY.md").read_text(encoding="utf-8")
    assert "build-generated-video-challenge" in text
    assert "video-coordinator-thread:" not in text
    assert "NON_ADOPTED_REVIEW_PROOF" not in text


def test_review_server_command_uses_callable_module() -> None:
    output = Path("episodes/example/review/development_generated_video_challenge_v1")
    command = challenge._serve_command(output=output, root=Path("."))
    script = challenge._serve_script()

    assert "python -m src.cli.serve_review" in command
    assert "python -m src.cli.serve_review" in script
    assert "src.cli.main serve-review" not in command
    assert "src.cli.main serve-review" not in script


def test_portable_expectation_keeps_exact_local_only_reentry() -> None:
    expectation = json.loads(
        Path(
            "docs/review_intake/clip-development-generated-video-challenge-v1-001.expected.json"
        ).read_text(encoding="utf-8")
    )

    assert expectation["artifact_id"] == challenge.CHALLENGE_ID
    assert expectation["source_identity"]["provider_id"] == "7J5aS_pcBj4"
    assert expectation["video"]["sha256"] == (
        "eff74435a27a61d49815709895592540fc14e5b725f675e7c4cf606133ba9e63"
    )
    assert expectation["local_package"]["local_only"] is True
    assert expectation["transport_reentry"]["archive_created"] is False
    assert expectation["transport_reentry"]["do_not_regenerate_as_same_identity"] is True
    assert expectation["not_replacements"] == list(challenge.NOT_REPLACEMENTS)
    portable_text = json.dumps(expectation, ensure_ascii=False)
    assert "video-coordinator-thread:" not in portable_text
    assert "C:\\Users\\PLANNER007" not in portable_text
