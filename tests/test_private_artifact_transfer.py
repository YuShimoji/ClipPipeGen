from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path

import pytest

from src.cli.main import main
from src.pipeline import private_artifact_transfer as transfer_module
from src.pipeline.private_artifact_transfer import (
    MANIFEST_PATH,
    PrivateArtifactTransferError,
    _canonical_json_bytes,
    _manifest_self_digest,
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


def _rewrite_manifest(archive_path: Path, mutate) -> None:
    replacement = archive_path.with_suffix(".replacement.zip")
    with zipfile.ZipFile(archive_path, mode="r") as source:
        members = {
            info.filename: source.read(info.filename)
            for info in source.infolist()
            if info.filename != MANIFEST_PATH
        }
        manifest = json.loads(source.read(MANIFEST_PATH))
    mutate(manifest)
    manifest["manifest_self_integrity"]["sha256"] = _manifest_self_digest(manifest)
    with zipfile.ZipFile(replacement, mode="w") as target:
        for name, payload in members.items():
            target.writestr(name, payload)
        target.writestr(MANIFEST_PATH, _canonical_json_bytes(manifest))
    os.replace(replacement, archive_path)


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
        assert {
            entry["repo_relative_path"] for entry in manifest["payload"]["entries"]
        } == {
            "episodes/demo/artifacts/clip-demo-001/final_video.mp4",
            "episodes/demo/artifacts/clip-demo-001/run_manifest.json",
            "episodes/demo/corpus/source_video.mp4",
        }
    assert receipt_payload["archive_sha256"]
    assert receipt_payload["manifest_sha256"]
    assert receipt_payload["manifest_self_sha256"] == manifest[
        "manifest_self_integrity"
    ]["sha256"]


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("schema_version", "other.schema.v1"),
        ("bundle_id", "clip-other-transfer-v1-001"),
        ("artifact_id", "clip-other-001"),
        ("source_identity", "local:other"),
        ("repo_head", "b" * 40),
        ("manifest_self_sha256", "0" * 64),
        ("payload_file_count", 99),
        ("payload_file_count", True),
        ("payload_byte_size", 1),
        ("storage_class", "public"),
    ],
)
def test_verify_rejects_receipt_identity_substitution(
    tmp_path: Path, field: str, replacement: object
) -> None:
    archive, receipt = _build(tmp_path)
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload[field] = replacement
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(
        PrivateArtifactTransferError, match=f"receipt {field} does not match"
    ):
        verify_private_artifact_transfer(
            archive_path=archive,
            receipt_path=receipt,
        )


def test_build_refuses_overwrite_non_episode_and_secret_inputs(tmp_path: Path) -> None:
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

    secret = tmp_path / "episodes" / "demo" / ".env.production"
    secret.write_text("TOKEN=not-a-real-secret", encoding="utf-8")
    with pytest.raises(PrivateArtifactTransferError, match="secret-like"):
        build_private_artifact_transfer(
            bundle_id="clip-secret-private-transfer-v1-001",
            artifact_id="clip-demo-001",
            source_identity="local:demo-source",
            repo_head=REPO_HEAD,
            includes=[Path("episodes/demo/.env.production")],
            output_path=Path("episodes/demo/transfers/secret.zip"),
            base_dir=tmp_path,
        )


def test_build_removes_owned_archive_if_receipt_publish_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    includes = _fixture_tree(tmp_path)
    output = tmp_path / "episodes/demo/transfers/atomic.zip"
    real_replace = os.replace

    def fail_receipt_publish(source: Path | str, destination: Path | str) -> None:
        if Path(destination).name.endswith(".receipt.json"):
            raise OSError("simulated receipt publication failure")
        real_replace(source, destination)

    monkeypatch.setattr(transfer_module.os, "replace", fail_receipt_publish)
    with pytest.raises(OSError, match="simulated receipt publication failure"):
        build_private_artifact_transfer(
            bundle_id="clip-demo-private-transfer-v1-atomic",
            artifact_id="clip-demo-001",
            source_identity="local:demo-source",
            repo_head=REPO_HEAD,
            includes=includes,
            output_path=output.relative_to(tmp_path),
            base_dir=tmp_path,
        )
    assert not output.exists()
    assert not output.with_suffix(".zip.receipt.json").exists()
    assert list(output.parent.glob(".*.tmp")) == []


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
    archive, _receipt = _build(tmp_path)
    with zipfile.ZipFile(archive, mode="a") as bundle:
        bundle.writestr("../escape.txt", "unsafe")
    with pytest.raises(PrivateArtifactTransferError, match="unmanifested"):
        verify_private_artifact_transfer(
            archive_path=archive,
            receipt_path=None,
        )


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda manifest: manifest["transport"].__setitem__("public_sharing", 0),
            "transport boundary",
        ),
        (
            lambda manifest: manifest["closed_gates"].__setitem__(
                "rights_approval", 0
            ),
            "acceptance gates",
        ),
        (
            lambda manifest: manifest["restore_contract"].__setitem__(
                "existing_mismatched_files", "overwrite"
            ),
            "restore contract",
        ),
    ],
)
def test_verify_rejects_weakened_manifest_boundaries(
    tmp_path: Path, mutate, message: str
) -> None:
    archive, _receipt = _build(tmp_path)
    _rewrite_manifest(archive, mutate)

    with pytest.raises(PrivateArtifactTransferError, match=message):
        verify_private_artifact_transfer(archive_path=archive)


def test_verify_rejects_reparse_restore_root_before_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive, receipt = _build(tmp_path)
    restore_root = tmp_path / "receiving-checkout"
    real_is_reparse = transfer_module._is_reparse_point

    monkeypatch.setattr(
        transfer_module,
        "_is_reparse_point",
        lambda path: path == restore_root or real_is_reparse(path),
    )
    with pytest.raises(PrivateArtifactTransferError, match="restore root"):
        verify_private_artifact_transfer(
            archive_path=archive,
            receipt_path=receipt,
            restore_root=restore_root,
        )
    assert not restore_root.exists()


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
