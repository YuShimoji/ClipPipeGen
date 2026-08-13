from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from src.cli.main import main
from src.pipeline.portable_review_proof import (
    EXPECTATION_SCHEMA,
    OUTER_MANIFEST_SCHEMA,
    PortableReviewProofError,
    verify_portable_review_proof,
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
    assert result["package_file_count"] == 70
    assert result["semantic_winner_selected"] is False
    assert len(result["retained_media"]) == 4
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
