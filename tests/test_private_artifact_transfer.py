from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from src.cli.main import main
from src.pipeline.private_artifact_transfer import (
    MANIFEST_PATH,
    PrivateArtifactTransferError,
    build_private_artifact_transfer,
    verify_private_artifact_transfer,
)


REPO_HEAD = "a" * 40


def _fixture_tree(root: Path) -> list[Path]:
    source = root / "episodes" / "demo" / "corpus" / "source_video.mp4"
    artifact = root / "episodes" / "demo" / "artifacts" / "clip-demo-001"
    source.parent.mkdir(parents=True)
    artifact.mkdir(parents=True)
    source.write_bytes(b"source-bytes\x00\x01")
    (artifact / "final_video.mp4").write_bytes(b"rendered-bytes")
    (artifact / "run_manifest.json").write_text(
        json.dumps({"artifact_id": "clip-demo-001"}), encoding="utf-8"
    )
    return [Path("episodes/demo/corpus"), Path("episodes/demo/artifacts/clip-demo-001")]


def _build(root: Path) -> tuple[Path, Path]:
    result = build_private_artifact_transfer(
        bundle_id="clip-demo-private-transfer-v1-001",
        artifact_id="clip-demo-001",
        source_identity="local:demo-source",
        repo_head=REPO_HEAD,
        includes=_fixture_tree(root),
        output_path=Path("episodes/demo/transfers/clip-demo-private-transfer-v1-001.zip"),
        base_dir=root,
    )
    return result["archive"], result["receipt"]


def test_build_verify_restore_and_reuse_exact_files(tmp_path: Path) -> None:
    archive, receipt = _build(tmp_path)
    verified = verify_private_artifact_transfer(
        archive_path=archive,
        receipt_path=receipt,
    )
    assert verified["state"] == "PRIVATE_ARTIFACT_TRANSFER_VERIFIED"
    assert verified["payload_file_count"] == 3
    assert verified["restored_file_count"] == 0

    restore_root = tmp_path / "receiving-checkout"
    restored = verify_private_artifact_transfer(
        archive_path=archive,
        receipt_path=receipt,
        restore_root=restore_root,
    )
    assert restored["restored_file_count"] == 3
    assert restored["existing_exact_file_count"] == 0
    assert (
        restore_root / "episodes/demo/artifacts/clip-demo-001/final_video.mp4"
    ).read_bytes() == b"rendered-bytes"

    repeated = verify_private_artifact_transfer(
        archive_path=archive,
        receipt_path=receipt,
        restore_root=restore_root,
    )
    assert repeated["restored_file_count"] == 0
    assert repeated["existing_exact_file_count"] == 3


def test_manifest_and_receipt_bind_the_exact_archive(tmp_path: Path) -> None:
    archive, receipt = _build(tmp_path)
    receipt_payload = json.loads(receipt.read_text(encoding="utf-8"))
    with zipfile.ZipFile(archive) as bundle:
        manifest_bytes = bundle.read(MANIFEST_PATH)
        manifest = json.loads(manifest_bytes)
        assert manifest["repo_head"] == REPO_HEAD
        assert manifest["transport"]["public_sharing"] is False
        assert manifest["closed_gates"]["rights_approval"] is False
        assert {entry["repo_relative_path"] for entry in manifest["payload"]["entries"]} == {
            "episodes/demo/artifacts/clip-demo-001/final_video.mp4",
            "episodes/demo/artifacts/clip-demo-001/run_manifest.json",
            "episodes/demo/corpus/source_video.mp4",
        }
    assert receipt_payload["archive_sha256"]
    assert receipt_payload["manifest_sha256"]


def test_build_refuses_overwrite_and_non_episode_inputs(tmp_path: Path) -> None:
    archive, _receipt = _build(tmp_path)
    with pytest.raises(PrivateArtifactTransferError, match="already exists"):
        build_private_artifact_transfer(
            bundle_id="clip-demo-private-transfer-v1-001",
            artifact_id="clip-demo-001",
            source_identity="local:demo-source",
            repo_head=REPO_HEAD,
            includes=[Path("episodes/demo/corpus")],
            output_path=archive.relative_to(tmp_path),
            base_dir=tmp_path,
        )

    forbidden = tmp_path / ".serena" / "project.yml"
    forbidden.parent.mkdir()
    forbidden.write_text("private", encoding="utf-8")
    with pytest.raises(PrivateArtifactTransferError, match="episodes"):
        build_private_artifact_transfer(
            bundle_id="clip-forbidden-private-transfer-v1-001",
            artifact_id="clip-demo-001",
            source_identity="local:demo-source",
            repo_head=REPO_HEAD,
            includes=[Path(".serena/project.yml")],
            output_path=Path("episodes/demo/transfers/forbidden.zip"),
            base_dir=tmp_path,
        )


def test_verify_fails_closed_before_overwriting_conflicting_restore_target(
    tmp_path: Path,
) -> None:
    archive, receipt = _build(tmp_path)
    restore_root = tmp_path / "receiving-checkout"
    conflict = restore_root / "episodes/demo/corpus/source_video.mp4"
    conflict.parent.mkdir(parents=True)
    conflict.write_bytes(b"different")

    with pytest.raises(PrivateArtifactTransferError, match="conflicts"):
        verify_private_artifact_transfer(
            archive_path=archive,
            receipt_path=receipt,
            restore_root=restore_root,
        )
    assert conflict.read_bytes() == b"different"
    assert not (
        restore_root / "episodes/demo/artifacts/clip-demo-001/final_video.mp4"
    ).exists()


def test_verify_rejects_unmanifested_archive_members(tmp_path: Path) -> None:
    archive, receipt = _build(tmp_path)
    with zipfile.ZipFile(archive, mode="a") as bundle:
        bundle.writestr("../escape.txt", "unsafe")
    with pytest.raises(PrivateArtifactTransferError, match="unmanifested"):
        verify_private_artifact_transfer(
            archive_path=archive,
            receipt_path=None,
        )


def test_cli_build_and_verify_json(tmp_path: Path, monkeypatch, capsys) -> None:
    includes = _fixture_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    output = "episodes/demo/transfers/cli.zip"
    argv = [
        "build-private-artifact-transfer",
        "--bundle-id",
        "clip-demo-private-transfer-v1-002",
        "--artifact-id",
        "clip-demo-001",
        "--source-identity",
        "local:demo-source",
        "--repo-head",
        REPO_HEAD,
    ]
    for include in includes:
        argv.extend(("--include", include.as_posix()))
    argv.extend(("--output", output, "--format", "json"))
    assert main(argv) == 0
    build_payload = json.loads(capsys.readouterr().out)
    assert build_payload["state"] == "PRIVATE_ARTIFACT_TRANSFER_BUILT"

    assert main(
        [
            "verify-private-artifact-transfer",
            "--archive",
            output,
            "--receipt",
            output + ".receipt.json",
            "--format",
            "json",
        ]
    ) == 0
    verify_payload = json.loads(capsys.readouterr().out)
    assert verify_payload["state"] == "PRIVATE_ARTIFACT_TRANSFER_VERIFIED"
