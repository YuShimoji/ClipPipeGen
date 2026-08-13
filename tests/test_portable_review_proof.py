from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from src.cli.main import main
from src.pipeline.portable_review_proof import (
    EXPECTATION_SCHEMA,
    HANDOFF_CONTRACT_SCHEMA,
    OUTER_MANIFEST_SCHEMA,
    PortableReviewProofError,
    verify_portable_review_proof,
    write_portable_review_handoff,
)


ARTIFACT_ID = "clip-fixture-portable-review-proof-v1-001"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_fixture(
    root: Path,
    *,
    extra_members: dict[str, bytes] | None = None,
    post_manifest_overrides: dict[str, bytes] | None = None,
) -> tuple[Path, Path, Path]:
    review = b"<!doctype html><title>exact review</title>"
    media = [b"media-one", b"media-two", b"media-three", b"media-four"]
    members: dict[str, bytes] = {
        "package/review/index.html": review,
        "package/review/open_review.ps1": b"param([switch]$NoOpen)\n",
        "package/review/serve_review.cjs": b"// fixture server\n",
        "package/proof_set_receipt.json": json.dumps(
            {"artifact_id": ARTIFACT_ID}
        ).encode(),
        **{
            f"package/media/proof_{index:02d}.mp4": payload
            for index, payload in enumerate(media, start=1)
        },
    }
    for index in range(1, 62):
        members[f"package/evidence/item_{index:02d}.json"] = (
            f'{{"item":{index}}}\n'.encode()
        )
    assert len(members) == 69
    manifest_payload = {
        "schema_version": "fixture.closed_package.v1",
        "files": [
            {
                "path": name.removeprefix("package/"),
                "byte_size": len(payload),
                "sha256": _sha(payload),
            }
            for name, payload in sorted(members.items())
        ],
        "file_count": len(members),
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    canonical = json.dumps(
        manifest_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    manifest_self_sha = _sha(canonical)
    manifest_payload["manifest_self_integrity"]["sha256"] = manifest_self_sha
    members["package/manifest.json"] = (
        json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    assert len(members) == 70
    if post_manifest_overrides:
        members.update(post_manifest_overrides)
    if extra_members:
        members.update(extra_members)

    archive = root / "ClipPipeGen-portable.zip"
    with zipfile.ZipFile(archive, mode="w") as bundle:
        for name, payload in members.items():
            bundle.writestr(name, payload)

    expectation = root / "expected.json"
    expectation.write_text(
        json.dumps(
            {
                "schema_version": EXPECTATION_SCHEMA,
                "artifact_id": ARTIFACT_ID,
                "source_identity": "local:fixture-source",
                "artifact_state": "NON_ADOPTED_REVIEW_PROOF",
                "package_root": "package",
                "physical_file_count": 70,
                "manifest": {
                    "payload_file_count": 69,
                    "self_sha256": manifest_self_sha,
                },
                "review_entrypoint": {
                    "path": "package/review/index.html",
                    "sha256": _sha(review),
                },
                "required_members": [
                    "package/review/index.html",
                    "package/review/open_review.ps1",
                    "package/review/serve_review.cjs",
                    "package/proof_set_receipt.json",
                ],
                "media": [
                    {
                        "ordinal": index,
                        "byte_size": len(payload),
                        "duration_seconds": float(index),
                        "sha256": _sha(payload),
                    }
                    for index, payload in enumerate(media, start=1)
                ],
                "closed_gates": {
                    "semantic_winner_selected": False,
                    "human_creative_acceptance": False,
                    "production_acceptance": False,
                    "public_or_publishing_acceptance": False,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    outer = root / "outer.json"
    outer.write_text(
        json.dumps(
            {
                "schema_version": OUTER_MANIFEST_SCHEMA,
                "artifact_id": ARTIFACT_ID,
                "archive_name": archive.name,
                "archive_byte_size": archive.stat().st_size,
                "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "package_root": "package",
                "package_file_count": 70,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return archive, outer, expectation


def _write_handoff_contract(root: Path, *, artifact_id: str = ARTIFACT_ID) -> Path:
    contract = root / "review-contract.json"
    dimensions = {
        key: {
            "question": f"Review {key}?",
            "checks": [f"Check {key} without selecting it mechanically."],
        }
        for key in ("opening", "endpoint", "subtitle_behavior", "overall_winner")
    }
    contract.write_text(
        json.dumps(
            {
                "schema_version": HANDOFF_CONTRACT_SCHEMA,
                "artifact_id": artifact_id,
                "artifact_state": "NON_ADOPTED_REVIEW_PROOF",
                "estimated_review_minutes": 12,
                "comparison_dimensions": dimensions,
                "reply_contract": {
                    "ACCEPT": "ACCEPT proof=<1|2|3|4>",
                    "REPAIR": "REPAIR proof=<1|2|3|4|all> issue=<required>",
                    "REJECT": "REJECT reason=<required>",
                },
                "after_reply": {
                    "ACCEPT": "Bind the human choice to exact identity.",
                    "REPAIR": "Repair only the named dimension.",
                    "REJECT": "Retain all four as non-adopted lineage.",
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return contract


def test_verify_and_extract_exact_package_only(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(
        tmp_path, extra_members={"project/README.md": b"project snapshot"}
    )
    target = tmp_path / "verified-review"
    result = verify_portable_review_proof(
        archive_path=archive,
        outer_manifest_path=outer,
        expectation_path=expectation,
        extract_to=target,
    )
    assert result["state"] == "PORTABLE_REVIEW_PROOF_VERIFIED"
    assert result["artifact_state"] == "NON_ADOPTED_REVIEW_PROOF"
    assert result["source_identity"] == "local:fixture-source"
    assert result["package_file_count"] == 70
    assert result["semantic_winner_selected"] is False
    assert len(result["retained_media"]) == 4
    assert result["retained_media"][0]["recorded_duration_seconds"] == 1.0
    assert result["review_entrypoint"] == target.resolve() / "package/review/index.html"
    assert result["review_entrypoint"].is_file()
    assert not (target / "project/README.md").exists()


def test_missing_archive_fails_at_input_preflight_without_creating_output(
    tmp_path: Path,
) -> None:
    target = tmp_path / "must-not-exist"
    with pytest.raises(PortableReviewProofError) as failure:
        verify_portable_review_proof(
            archive_path=tmp_path / "missing.zip",
            outer_manifest_path=tmp_path / "missing.outer.json",
            expectation_path=tmp_path / "missing.expected.json",
            extract_to=target,
        )
    assert failure.value.stage == "input_preflight"
    assert not target.exists()


def test_missing_tracked_expectation_fails_before_outer_or_extraction(
    tmp_path: Path,
) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    expectation.unlink()
    target = tmp_path / "must-not-exist"
    with pytest.raises(PortableReviewProofError) as failure:
        verify_portable_review_proof(
            archive_path=archive,
            outer_manifest_path=outer,
            expectation_path=expectation,
            extract_to=target,
        )
    assert failure.value.stage == "expectation_validation"
    assert not target.exists()


def test_missing_outer_manifest_fails_before_archive_extraction(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    outer.unlink()
    target = tmp_path / "must-not-exist"
    with pytest.raises(PortableReviewProofError) as failure:
        verify_portable_review_proof(
            archive_path=archive,
            outer_manifest_path=outer,
            expectation_path=expectation,
            extract_to=target,
        )
    assert failure.value.stage == "outer_manifest_validation"
    assert not target.exists()


def test_rejects_outer_archive_hash_mismatch(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    payload = json.loads(outer.read_text(encoding="utf-8"))
    payload["archive_sha256"] = "0" * 64
    outer.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(PortableReviewProofError, match="archive SHA mismatch"):
        verify_portable_review_proof(
            archive_path=archive,
            outer_manifest_path=outer,
            expectation_path=expectation,
        )


def test_rejects_path_unsafe_member_even_outside_package(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(
        tmp_path, extra_members={"../escape.txt": b"escape"}
    )
    with pytest.raises(PortableReviewProofError, match="unsafe archive member"):
        verify_portable_review_proof(
            archive_path=archive,
            outer_manifest_path=outer,
            expectation_path=expectation,
        )


def test_rejects_changed_media_even_when_outer_archive_matches(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    with zipfile.ZipFile(archive, mode="a") as bundle:
        bundle.writestr("package/media/proof_05.mp4", b"semantic replacement")
    outer_payload = json.loads(outer.read_text(encoding="utf-8"))
    outer_payload["archive_byte_size"] = archive.stat().st_size
    outer_payload["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    outer.write_text(json.dumps(outer_payload), encoding="utf-8")
    with pytest.raises(PortableReviewProofError, match="file count mismatch"):
        verify_portable_review_proof(
            archive_path=archive,
            outer_manifest_path=outer,
            expectation_path=expectation,
        )


def test_manifest_closure_rejects_changed_non_media_payload(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(
        tmp_path,
        post_manifest_overrides={
            "package/evidence/item_01.json": b'{"item":"changed"}\n'
        },
    )
    with pytest.raises(PortableReviewProofError, match="manifest payload mismatch"):
        verify_portable_review_proof(
            archive_path=archive,
            outer_manifest_path=outer,
            expectation_path=expectation,
        )


def test_rejects_existing_extraction_target_without_writing(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    target = tmp_path / "existing"
    target.mkdir()
    marker = target / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    with pytest.raises(PortableReviewProofError, match="already exists"):
        verify_portable_review_proof(
            archive_path=archive,
            outer_manifest_path=outer,
            expectation_path=expectation,
            extract_to=target,
        )
    assert marker.read_text(encoding="utf-8") == "keep"


def test_cli_returns_direct_review_route_without_opening_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    target = tmp_path / "cli-review"
    assert main(
        [
            "verify-portable-review-proof",
            "--archive",
            str(archive),
            "--outer-manifest",
            str(outer),
            "--expected",
            str(expectation),
            "--extract-to",
            str(target),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["state"] == "PORTABLE_REVIEW_PROOF_VERIFIED"
    assert payload["review_entrypoint"].endswith("package\\review\\index.html")
    assert "open_review.ps1" in payload["review_open_command"]


def test_verified_extraction_writes_atomic_coordinator_packet(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    extraction = tmp_path / "verified-review"
    verification = verify_portable_review_proof(
        archive_path=archive,
        outer_manifest_path=outer,
        expectation_path=expectation,
        extract_to=extraction,
    )
    output = tmp_path / "handoff"
    result = write_portable_review_handoff(
        verification=verification,
        contract_path=_write_handoff_contract(tmp_path),
        output_dir=output,
        reply_destination="video-coordinator:test-thread",
    )
    assert result["state"] == "PORTABLE_REVIEW_HANDOFF_WRITTEN"
    assert result["acceptance_ready"] is True
    packet = json.loads(
        (output / "coordinator_review_packet.json").read_text(encoding="utf-8")
    )
    assert packet["state"] == "ACCEPTANCE_PACKET_READY"
    assert packet["reply_destination"] == "video-coordinator:test-thread"
    assert packet["semantic_winner_selected"] is False
    assert len(packet["retained_media"]) == 4
    assert all(Path(item["local_path"]).is_file() for item in packet["retained_media"])
    markdown = (output / "coordinator_review_packet.md").read_text(encoding="utf-8")
    assert "## Open and compare" in markdown
    assert "### opening" in markdown
    assert "### endpoint" in markdown
    assert "### subtitle_behavior" in markdown
    assert "### overall_winner" in markdown
    assert "ACCEPT proof=" in markdown
    assert "REPAIR proof=" in markdown
    assert "REJECT reason=" in markdown


def test_handoff_requires_verified_extraction_and_writes_nothing(
    tmp_path: Path,
) -> None:
    output = tmp_path / "must-not-exist"
    with pytest.raises(PortableReviewProofError) as failure:
        write_portable_review_handoff(
            verification={
                "state": "PORTABLE_REVIEW_PROOF_VERIFIED",
                "artifact_id": ARTIFACT_ID,
            },
            contract_path=_write_handoff_contract(tmp_path),
            output_dir=output,
            reply_destination="video-coordinator:test-thread",
        )
    assert failure.value.stage == "handoff_preflight"
    assert not output.exists()


def test_handoff_rejects_contract_for_another_artifact(tmp_path: Path) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    verification = verify_portable_review_proof(
        archive_path=archive,
        outer_manifest_path=outer,
        expectation_path=expectation,
        extract_to=tmp_path / "verified-review",
    )
    output = tmp_path / "must-not-exist"
    with pytest.raises(PortableReviewProofError) as failure:
        write_portable_review_handoff(
            verification=verification,
            contract_path=_write_handoff_contract(
                tmp_path, artifact_id="clip-another-proof-001"
            ),
            output_dir=output,
            reply_destination="video-coordinator:test-thread",
        )
    assert failure.value.stage == "handoff_contract_validation"
    assert not output.exists()


def test_cli_writes_coordinator_packet_only_after_exact_verification(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    extraction = tmp_path / "cli-review"
    output = tmp_path / "cli-handoff"
    assert main(
        [
            "verify-portable-review-proof",
            "--archive",
            str(archive),
            "--outer-manifest",
            str(outer),
            "--expected",
            str(expectation),
            "--extract-to",
            str(extraction),
            "--review-contract",
            str(_write_handoff_contract(tmp_path)),
            "--handoff-dir",
            str(output),
            "--reply-destination",
            "video-coordinator:test-thread",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["handoff"]["state"] == "PORTABLE_REVIEW_HANDOFF_WRITTEN"
    assert payload["handoff"]["acceptance_ready"] is True
    assert (output / "verification_receipt.json").is_file()
    assert (output / "coordinator_review_packet.json").is_file()
    assert (output / "coordinator_review_packet.md").is_file()


def test_cli_missing_archive_never_creates_handoff_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "must-not-exist"
    assert main(
        [
            "verify-portable-review-proof",
            "--archive",
            str(tmp_path / "missing.zip"),
            "--outer-manifest",
            str(tmp_path / "missing.outer.json"),
            "--expected",
            str(tmp_path / "missing.expected.json"),
            "--extract-to",
            str(tmp_path / "must-not-extract"),
            "--review-contract",
            str(tmp_path / "missing.contract.json"),
            "--handoff-dir",
            str(output),
            "--reply-destination",
            "video-coordinator:test-thread",
        ]
    ) == 2
    assert "input_preflight" in capsys.readouterr().err
    assert not output.exists()


def test_cli_incomplete_handoff_args_fail_before_verification_or_extraction(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    archive, outer, expectation = _write_fixture(tmp_path)
    extraction = tmp_path / "must-not-extract"
    assert main(
        [
            "verify-portable-review-proof",
            "--archive",
            str(archive),
            "--outer-manifest",
            str(outer),
            "--expected",
            str(expectation),
            "--extract-to",
            str(extraction),
            "--handoff-dir",
            str(tmp_path / "incomplete-handoff"),
        ]
    ) == 2
    assert "handoff_preflight" in capsys.readouterr().err
    assert not extraction.exists()
