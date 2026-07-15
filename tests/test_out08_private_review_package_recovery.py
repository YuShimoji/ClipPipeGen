from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

from src.cli.serve_review import RangeRequestHandler
from src.pipeline.out08_private_review_package_recovery import (
    Out08PrivateRecoveryError,
    canonical_manifest_self_hash,
    export_package,
    import_package,
    probe_host,
    validate_package,
)


EXPECTED_FILES = [
    "batch_manifest.json",
    "batch_readback.json",
    "candidate_01.mp4",
    "candidate_01_frame_qa.jpg",
    "candidate_01_navigation.jpg",
    "candidate_01_subtitles.ass",
    "candidate_01_subtitles.srt",
    "candidate_02.mp4",
    "candidate_02_frame_qa.jpg",
    "candidate_02_navigation.jpg",
    "candidate_02_subtitles.ass",
    "candidate_02_subtitles.srt",
    "candidate_plan.json",
    "candidate_scan_readback.json",
    "index.html",
    "open_preview.ps1",
    "serve_preview.ps1",
]
REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def exact_package(tmp_path: Path) -> tuple[Path, Path, dict]:
    repo_root = tmp_path / "source-repo"
    package_relative = "episodes/fixture/review/out08_real_unused_range_short_minibatch"
    package = repo_root / package_relative
    package.mkdir(parents=True)
    candidate_bytes = {
        "candidate_01": b"candidate one exact bytes",
        "candidate_02": b"candidate two exact bytes",
    }
    candidate_hashes = {
        key: hashlib.sha256(value).hexdigest() for key, value in candidate_bytes.items()
    }
    source_hash = hashlib.sha256(b"Thank source identity").hexdigest()
    artifact_id = "clip-out08-real-unused-range-short-minibatch-v0-001"
    contract = {
        "schema_version": "clippipegen.out08.private_review_package_recovery.v0",
        "artifact_id": "clip-out08-private-review-package-recovery-v0-test",
        "source_artifact_id": artifact_id,
        "source_package": {
            "repo_relative_path": package_relative,
            "expected_file_count": 17,
            "manifest_payload_count": 16,
            "expected_files": EXPECTED_FILES,
            "batch_manifest_schema": "clippipegen.out08.batch_manifest.v0",
            "batch_manifest_self_integrity_sha256": "0" * 64,
        },
        "candidate_identity": {
            candidate_id: {
                "package_relative_path": f"{candidate_id}.mp4",
                "sha256": candidate_hashes[candidate_id],
            }
            for candidate_id in ("candidate_01", "candidate_02")
        },
        "source_identity": {
            "last_verified_source_video_sha256": source_hash,
        },
        "cut_009_exclusion": {
            "cut_id": "cut_009",
            "final_decision": "reject",
            "reject_interval_start_seconds": 135.219,
            "reject_interval_end_seconds": 144.0,
            "candidate_02_max_source_end_seconds": 135.219,
            "status": "fully_excluded_no_source_time_overlap",
        },
        "host_contract": {
            "last_verified_host_label": "Thank",
            "last_verified_host_name": "THANK-FIXTURE",
            "host_receipt_repo_relative_path": (
                "episodes/fixture/review/out08_private_recovery_host_receipt.json"
            ),
        },
        "archive_contract": {
            "transfer_receipt_filename": "out08_private_transfer_receipt.json",
        },
    }

    (package / "candidate_01.mp4").write_bytes(candidate_bytes["candidate_01"])
    (package / "candidate_02.mp4").write_bytes(candidate_bytes["candidate_02"])
    for name in EXPECTED_FILES:
        if name in {
            "batch_manifest.json",
            "batch_readback.json",
            "candidate_plan.json",
            "candidate_01.mp4",
            "candidate_02.mp4",
        }:
            continue
        (package / name).write_bytes(f"fixture:{name}\n".encode())

    ranges = {
        "candidate_01": [
            {
                "source_start_seconds": 100.0,
                "source_end_seconds": 110.0,
                "authority_cut_ids": ["cut_007"],
            }
        ],
        "candidate_02": [
            {
                "source_start_seconds": 123.0,
                "source_end_seconds": 135.219,
                "authority_cut_ids": ["cut_008"],
            }
        ],
    }
    readback = {
        "artifact_id": artifact_id,
        "actual_candidate_count": 2,
        "source_identity": {"source_video": {"sha256": source_hash}},
        "candidates": [
            {
                "candidate_id": candidate_id,
                "video": {
                    "package_relative_path": f"{candidate_id}.mp4",
                    "sha256": candidate_hashes[candidate_id],
                },
                "source_ranges": ranges[candidate_id],
            }
            for candidate_id in ("candidate_01", "candidate_02")
        ],
        "boundaries": {
            "internal_review_only": True,
            "human_review_pending": True,
            "production_candidate": False,
            "production_acceptance": False,
            "production_subtitle_design_acceptance": False,
            "rights_status": "pending",
            "public_ready": False,
            "publishing_acceptance": False,
            "publish_attempted": False,
            "navigation_frames_are_thumbnails": False,
            "cut009_final_cut_decision": "reject",
            "authority_mutated": False,
        },
    }
    plan = {
        "artifact_id": artifact_id,
        "actual_candidate_count": 2,
        "cut009_final_cut_decision": "reject",
        "candidates": [
            {
                "candidate_id": candidate_id,
                "timeline": ranges[candidate_id],
                "cut009_rejection_preserved": True,
            }
            for candidate_id in ("candidate_01", "candidate_02")
        ],
    }
    _write_json(package / "batch_readback.json", readback)
    _write_json(package / "candidate_plan.json", plan)
    _rebuild_manifest(package, contract)
    return repo_root, package, contract


def test_exact_package_validates_and_exports_deterministically(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package
    first = tmp_path / "private-one" / "out08.zip"
    second = tmp_path / "private-two" / "out08.zip"

    validation = validate_package(
        package_path=package, contract=contract, repo_root=repo_root
    )
    export_package(
        package_path=package,
        destination=first,
        contract=contract,
        repo_root=repo_root,
        host_name="THANK-FIXTURE",
    )
    export_package(
        package_path=package,
        destination=second,
        contract=contract,
        repo_root=repo_root,
        host_name="thank-fixture",
    )

    assert validation["status"] == "package_verified_exact"
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == sorted(
            EXPECTED_FILES + ["out08_private_transfer_receipt.json"]
        )
        assert {info.date_time for info in archive.infolist()} == {
            (1980, 1, 1, 0, 0, 0)
        }


def test_tracked_contract_preserves_thank_candidate_identity() -> None:
    contract = json.loads(
        (
            REPO_ROOT
            / "docs/output_layer/out08_private_review_package_recovery_contract.json"
        ).read_text(encoding="utf-8")
    )

    assert contract["source_package"]["expected_files"] == EXPECTED_FILES
    assert contract["source_package"]["expected_file_count"] == 17
    assert contract["source_package"]["manifest_payload_count"] == 16
    assert contract["source_package"]["batch_manifest_self_integrity_sha256"] == (
        "22c7137d81361f662a3053fbd796837f16a58473ba0ecbcb99bb0e031499b4a4"
    )
    assert contract["candidate_identity"]["candidate_01"]["sha256"] == (
        "f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a"
    )
    assert contract["candidate_identity"]["candidate_02"]["sha256"] == (
        "47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b"
    )
    assert contract["cut_009_exclusion"] == {
        "cut_id": "cut_009",
        "final_decision": "reject",
        "reject_interval_start_seconds": 135.219,
        "reject_interval_end_seconds": 144.0,
        "candidate_02_max_source_end_seconds": 135.219,
        "status": "fully_excluded_no_source_time_overlap",
    }


def test_git_tracks_no_episode_payload_or_media_archive() -> None:
    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    private_suffixes = (".mp4", ".mov", ".mkv", ".avi", ".webm", ".zip", ".7z", ".rar")

    assert not [path for path in tracked if path.startswith("episodes/")]
    assert not [path for path in tracked if path.lower().endswith(private_suffixes)]


def test_export_requires_last_verified_host(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        export_package(
            package_path=package,
            destination=tmp_path / "private" / "out08.zip",
            contract=contract,
            repo_root=repo_root,
            host_name="PLANNER-FIXTURE",
        )
    assert caught.value.category == "source_host_mismatch"


@pytest.mark.parametrize("mutation", ["missing", "extra"])
def test_package_allowlist_fails_closed(
    exact_package: tuple[Path, Path, dict], mutation: str
) -> None:
    repo_root, package, contract = exact_package
    if mutation == "missing":
        (package / "candidate_01_navigation.jpg").unlink()
    else:
        (package / "unknown.txt").write_text("no", encoding="utf-8")

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        validate_package(package_path=package, contract=contract, repo_root=repo_root)
    assert caught.value.category == "package_present_invalid"


@pytest.mark.parametrize(
    ("bad_name", "expected_category"),
    [
        ("../candidate_01.mp4", "path_traversal"),
        ("unknown.txt", "archive_allowlist_mismatch"),
        ("CANDIDATE_01.MP4", "archive_case_collision"),
    ],
)
def test_archive_rejects_unsafe_or_unknown_entries(
    exact_package: tuple[Path, Path, dict],
    tmp_path: Path,
    bad_name: str,
    expected_category: str,
) -> None:
    repo_root, package, contract = exact_package
    good_archive = tmp_path / "private" / "good.zip"
    export_package(
        package_path=package,
        destination=good_archive,
        contract=contract,
        repo_root=repo_root,
        host_name="THANK-FIXTURE",
    )
    bad_archive = tmp_path / f"bad-{expected_category}.zip"
    entries = _archive_entries(good_archive)
    if expected_category == "archive_case_collision":
        entries.append((bad_name, b"collision"))
    elif expected_category == "archive_allowlist_mismatch":
        entries.append((bad_name, b"unknown"))
    else:
        entries[0] = (bad_name, entries[0][1])
    _write_archive(bad_archive, entries)

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        import_package(
            archive_path=bad_archive,
            package_path=tmp_path
            / "target"
            / contract["source_package"]["repo_relative_path"],
            contract=contract,
            repo_root=tmp_path / "target",
        )
    assert caught.value.category == expected_category


def test_archive_rejects_duplicate_entry(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package
    good_archive = tmp_path / "private" / "good.zip"
    export_package(
        package_path=package,
        destination=good_archive,
        contract=contract,
        repo_root=repo_root,
        host_name="THANK-FIXTURE",
    )
    bad_archive = tmp_path / "duplicate.zip"
    entries = _archive_entries(good_archive)
    entries.append(entries[0])
    with pytest.warns(UserWarning, match="Duplicate name"):
        _write_archive(bad_archive, entries)

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        import_package(
            archive_path=bad_archive,
            package_path=tmp_path
            / "target"
            / contract["source_package"]["repo_relative_path"],
            contract=contract,
            repo_root=tmp_path / "target",
        )
    assert caught.value.category == "archive_duplicate_entry"


def test_archive_rejects_symlink_entry(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package
    good_archive = tmp_path / "private" / "good.zip"
    export_package(
        package_path=package,
        destination=good_archive,
        contract=contract,
        repo_root=repo_root,
        host_name="THANK-FIXTURE",
    )
    bad_archive = tmp_path / "symlink.zip"
    entries = _archive_entries(good_archive)
    _write_archive(bad_archive, entries, symlink_name=entries[0][0])

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        import_package(
            archive_path=bad_archive,
            package_path=tmp_path
            / "target"
            / contract["source_package"]["repo_relative_path"],
            contract=contract,
            repo_root=tmp_path / "target",
        )
    assert caught.value.category == "archive_link_entry"


def test_corrupt_archive_is_rejected(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    _, _, contract = exact_package
    archive = tmp_path / "corrupt.zip"
    archive.write_bytes(b"not a zip")
    target_root = tmp_path / "target"

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        import_package(
            archive_path=archive,
            package_path=target_root / contract["source_package"]["repo_relative_path"],
            contract=contract,
            repo_root=target_root,
        )
    assert caught.value.category == "archive_corrupt"


def test_import_rejects_archive_stored_inside_target_repo(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package
    external_archive = tmp_path / "private" / "out08.zip"
    export_package(
        package_path=package,
        destination=external_archive,
        contract=contract,
        repo_root=repo_root,
        host_name="THANK-FIXTURE",
    )
    target_root = tmp_path / "target"
    target_root.mkdir()
    inside_archive = target_root / "out08.zip"
    inside_archive.write_bytes(external_archive.read_bytes())

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        import_package(
            archive_path=inside_archive,
            package_path=target_root / contract["source_package"]["repo_relative_path"],
            contract=contract,
            repo_root=target_root,
        )
    assert caught.value.category == "archive_inside_repo"


def test_candidate_hash_mismatch_is_rejected(
    exact_package: tuple[Path, Path, dict],
) -> None:
    repo_root, package, contract = exact_package
    (package / "candidate_01.mp4").write_bytes(b"different candidate bytes")
    _rebuild_manifest(package, contract)

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        validate_package(package_path=package, contract=contract, repo_root=repo_root)
    assert caught.value.category == "candidate_hash_mismatch"


def test_manifest_self_integrity_mismatch_is_rejected(
    exact_package: tuple[Path, Path, dict],
) -> None:
    repo_root, package, contract = exact_package
    manifest_path = package / "batch_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["manifest_self_integrity"]["sha256"] = "f" * 64
    _write_json(manifest_path, manifest)

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        validate_package(package_path=package, contract=contract, repo_root=repo_root)
    assert caught.value.category == "manifest_self_integrity_mismatch"


def test_cut_009_overlap_is_rejected(exact_package: tuple[Path, Path, dict]) -> None:
    repo_root, package, contract = exact_package
    plan_path = package / "candidate_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["candidates"][1]["timeline"][0]["source_end_seconds"] = 136.0
    _write_json(plan_path, plan)
    _rebuild_manifest(package, contract)

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        validate_package(package_path=package, contract=contract, repo_root=repo_root)
    assert caught.value.category == "cut_009_overlap"


def test_import_promotes_atomically_and_preserves_exact_existing_package(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package
    archive = tmp_path / "private" / "out08.zip"
    export_package(
        package_path=package,
        destination=archive,
        contract=contract,
        repo_root=repo_root,
        host_name="THANK-FIXTURE",
    )
    target_root = tmp_path / "target"
    target_package = target_root / contract["source_package"]["repo_relative_path"]
    port = _free_port()

    first = import_package(
        archive_path=archive,
        package_path=target_package,
        contract=contract,
        repo_root=target_root,
        port=port,
        host_name="PLANNER-FIXTURE",
    )
    second = import_package(
        archive_path=archive,
        package_path=target_package,
        contract=contract,
        repo_root=target_root,
        port=port,
        host_name="PLANNER-FIXTURE",
    )

    assert first["status"] == "package_imported_atomically"
    assert first["atomic_promotion"] is True
    assert second["status"] == "existing_valid_package_preserved"
    assert second["existing_valid_package_preserved"] is True
    assert not list(target_package.parent.glob(".*.import-staging-*"))


def test_import_preserves_invalid_existing_package(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package
    archive = tmp_path / "private" / "out08.zip"
    export_package(
        package_path=package,
        destination=archive,
        contract=contract,
        repo_root=repo_root,
        host_name="THANK-FIXTURE",
    )
    target_root = tmp_path / "target"
    target_package = target_root / contract["source_package"]["repo_relative_path"]
    target_package.mkdir(parents=True)
    marker = target_package / "do-not-overwrite.txt"
    marker.write_text("preserve me", encoding="utf-8")

    with pytest.raises(Out08PrivateRecoveryError) as caught:
        import_package(
            archive_path=archive,
            package_path=target_package,
            contract=contract,
            repo_root=target_root,
            port=_free_port(),
        )
    assert caught.value.category == "existing_package_invalid"
    assert marker.read_text(encoding="utf-8") == "preserve me"
    assert not list(target_package.parent.glob(".*.import-staging-*"))


def test_probe_records_sanitized_missing_state(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    _, _, contract = exact_package
    target_root = tmp_path / "target"
    missing = target_root / contract["source_package"]["repo_relative_path"]

    result = probe_host(
        package_path=missing,
        contract=contract,
        repo_root=target_root,
        port=_free_port(),
        host_name="PLANNER-FIXTURE",
    )
    receipt = target_root / contract["host_contract"]["host_receipt_repo_relative_path"]
    receipt_text = receipt.read_text(encoding="utf-8")

    assert result["package_status"] == "package_missing"
    assert result["server_status"] == "server_stopped"
    assert result["access_status"] == "recovery_kit_ready_package_not_yet_imported"
    assert str(target_root) not in receipt_text
    assert "private_transfer_performed" in receipt_text
    assert not list(receipt.parent.glob(f".{receipt.name}.staging-*"))


def test_probe_verifies_exact_running_range_server(
    exact_package: tuple[Path, Path, dict],
) -> None:
    repo_root, package, contract = exact_package
    server = ThreadingHTTPServer(("127.0.0.1", 0), RangeRequestHandler)
    server.root = package  # type: ignore[attr-defined]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = probe_host(
            package_path=package,
            contract=contract,
            repo_root=repo_root,
            port=int(server.server_address[1]),
            host_name="PLANNER-FIXTURE",
            write_receipt=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert result["package_status"] == "package_verified_exact"
    assert result["server_status"] == "server_running_verified"
    assert result["access_status"] == "exact_package_and_server_verified"
    assert result["human_review_accessible"] is True


def test_probe_classifies_wrong_server_as_host_unknown(
    exact_package: tuple[Path, Path, dict], tmp_path: Path
) -> None:
    repo_root, package, contract = exact_package
    wrong_root = tmp_path / "wrong-server-root"
    wrong_root.mkdir()
    server = ThreadingHTTPServer(("127.0.0.1", 0), RangeRequestHandler)
    server.root = wrong_root  # type: ignore[attr-defined]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = probe_host(
            package_path=package,
            contract=contract,
            repo_root=repo_root,
            port=int(server.server_address[1]),
            host_name="PLANNER-FIXTURE",
            write_receipt=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert result["package_status"] == "package_verified_exact"
    assert result["server_status"] == "host_unknown"
    assert result["access_status"] == "host_unknown"
    assert result["classifications"].count("host_unknown") == 1
    assert result["human_review_accessible"] is False


def _rebuild_manifest(package: Path, contract: dict) -> None:
    payload_names = sorted(set(EXPECTED_FILES) - {"batch_manifest.json"})
    entries = []
    package_relative = contract["source_package"]["repo_relative_path"]
    for name in payload_names:
        data = (package / name).read_bytes()
        entries.append(
            {
                "package_relative_path": name,
                "repo_relative_path": f"{package_relative}/{name}",
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    manifest = {
        "schema_version": "clippipegen.out08.batch_manifest.v0",
        "artifact_id": contract["source_artifact_id"],
        "files": entries,
        "file_hash_coverage": {
            "status": "complete",
            "byte_hashed_payload_file_count": len(entries),
        },
        "manifest_self_integrity": {"sha256": None},
    }
    manifest["manifest_self_integrity"]["sha256"] = canonical_manifest_self_hash(
        manifest
    )
    contract["source_package"]["batch_manifest_self_integrity_sha256"] = manifest[
        "manifest_self_integrity"
    ]["sha256"]
    _write_json(package / "batch_manifest.json", manifest)


def _archive_entries(path: Path) -> list[tuple[str, bytes]]:
    with zipfile.ZipFile(path) as archive:
        return [(info.filename, archive.read(info)) for info in archive.infolist()]


def _write_archive(
    path: Path,
    entries: list[tuple[str, bytes]],
    *,
    symlink_name: str | None = None,
) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o120777 if name == symlink_name else 0o100600) << 16
            archive.writestr(info, data)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])
