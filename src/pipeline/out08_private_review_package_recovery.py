"""Dependency-free OUT-08 private review package recovery workflow.

This module transports an already verified ignored review package without
regenerating media or using Git.  It validates the exact package contract,
creates a deterministic ZIP with a sanitized receipt, imports through a
verified sibling staging directory, and records host-local access state under
the ignored ``episodes/`` tree.
"""

from __future__ import annotations

import copy
import hashlib
import http.client as http_client
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


DEFAULT_CONTRACT_PATH = Path(
    "docs/output_layer/out08_private_review_package_recovery_contract.json"
)
HOST_RECEIPT_SCHEMA = "clippipegen.out08.private_review_host_receipt.v0"
TRANSFER_RECEIPT_SCHEMA = "clippipegen.out08.private_transfer_receipt.v0"
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 20 * 1024 * 1024 * 1024
SERVER_PROBE_BYTES = 1024
CUT_TIME_TOLERANCE_SECONDS = 0.002


class Out08PrivateRecoveryError(RuntimeError):
    """Fail-closed recovery error with a stable operator category."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category


def load_contract(path: Path) -> dict[str, Any]:
    contract = _read_json(path, "recovery contract")
    if contract.get("schema_version") != (
        "clippipegen.out08.private_review_package_recovery.v0"
    ):
        _fail("contract_invalid", "recovery contract schema changed")
    source = contract.get("source_package")
    candidates = contract.get("candidate_identity")
    cut = contract.get("cut_009_exclusion")
    host = contract.get("host_contract")
    archive = contract.get("archive_contract")
    if not all(
        isinstance(value, dict) for value in (source, candidates, cut, host, archive)
    ):
        _fail("contract_invalid", "recovery contract sections are incomplete")
    if archive.get("format") != "zip" or archive.get("compression") != "stored":
        _fail("contract_invalid", "archive contract must use stored ZIP entries")
    if (
        archive.get("destination_must_be_explicit") is not True
        or archive.get("destination_inside_repo_allowed") is not False
        or archive.get("git_transport_allowed") is not False
        or archive.get("external_upload_performed") is not False
    ):
        _fail("contract_invalid", "archive transport boundaries changed")
    expected = source.get("expected_files")
    if (
        not isinstance(expected, list)
        or len(expected) != source.get("expected_file_count")
        or any(not isinstance(value, str) for value in expected)
        or len(set(expected)) != len(expected)
    ):
        _fail("contract_invalid", "expected package allowlist is invalid")
    for name in expected:
        _validate_flat_relative_name(name, "contract package filename")
    if "batch_manifest.json" not in expected:
        _fail("contract_invalid", "batch manifest is missing from allowlist")
    receipt_name = archive.get("transfer_receipt_filename")
    if not isinstance(receipt_name, str):
        _fail("contract_invalid", "transfer receipt filename is missing")
    _validate_flat_relative_name(receipt_name, "transfer receipt filename")
    if receipt_name in expected:
        _fail("contract_invalid", "transfer receipt collides with package allowlist")
    package_relative = source.get("repo_relative_path")
    host_receipt_relative = host.get("host_receipt_repo_relative_path")
    _validate_repo_relative_path(package_relative, "package path")
    _validate_repo_relative_path(host_receipt_relative, "host receipt path")
    for candidate_id in ("candidate_01", "candidate_02"):
        identity = candidates.get(candidate_id)
        if not isinstance(identity, dict):
            _fail("contract_invalid", f"{candidate_id} identity is missing")
        if identity.get("package_relative_path") not in expected:
            _fail("contract_invalid", f"{candidate_id} path is not allowlisted")
        _require_sha256(identity.get("sha256"), f"{candidate_id} SHA-256")
    _require_sha256(
        source.get("batch_manifest_self_integrity_sha256"),
        "batch manifest self-integrity",
    )
    return contract


def default_package_path(repo_root: Path, contract: dict[str, Any]) -> Path:
    relative = Path(contract["source_package"]["repo_relative_path"])
    return (repo_root / relative).resolve()


def default_host_receipt_path(repo_root: Path, contract: dict[str, Any]) -> Path:
    relative = Path(contract["host_contract"]["host_receipt_repo_relative_path"])
    return (repo_root / relative).resolve()


def validate_package(
    *, package_path: Path, contract: dict[str, Any], repo_root: Path
) -> dict[str, Any]:
    package = package_path.resolve()
    root = repo_root.resolve()
    _require_within(package, root, "OUT-08 package")
    if not package.is_dir():
        _fail("package_missing", "OUT-08 package directory is missing")

    expected = set(contract["source_package"]["expected_files"])
    actual: set[str] = set()
    casefold_names: set[str] = set()
    for entry in package.iterdir():
        if _is_link_or_reparse(entry):
            _fail(
                "package_present_invalid", f"link/reparse entry rejected: {entry.name}"
            )
        if not entry.is_file():
            _fail("package_present_invalid", f"unexpected non-file entry: {entry.name}")
        name = entry.name
        _validate_flat_relative_name(name, "package filename")
        folded = name.casefold()
        if folded in casefold_names:
            _fail("package_present_invalid", f"case-collision entry rejected: {name}")
        casefold_names.add(folded)
        actual.add(name)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        _fail(
            "package_present_invalid",
            f"package allowlist mismatch; missing={missing}; extra={extra}",
        )

    manifest_path = package / "batch_manifest.json"
    manifest = _read_json(manifest_path, "batch manifest")
    source_contract = contract["source_package"]
    if manifest.get("schema_version") != source_contract["batch_manifest_schema"]:
        _fail("manifest_invalid", "batch manifest schema changed")
    if manifest.get("artifact_id") != contract["source_artifact_id"]:
        _fail("manifest_invalid", "batch manifest artifact identity changed")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        _fail("manifest_invalid", "batch manifest files are missing")
    if len(entries) != source_contract["manifest_payload_count"]:
        _fail("manifest_invalid", "batch manifest payload count changed")
    expected_payloads = expected - {"batch_manifest.json"}
    by_name: dict[str, dict[str, Any]] = {}
    for item in entries:
        if not isinstance(item, dict):
            _fail("manifest_invalid", "batch manifest file entry is invalid")
        relative = item.get("package_relative_path")
        if not isinstance(relative, str):
            _fail("manifest_invalid", "batch manifest path is missing")
        _validate_flat_relative_name(relative, "batch manifest path")
        if relative in by_name or relative.casefold() in {
            value.casefold() for value in by_name
        }:
            _fail("manifest_invalid", f"duplicate manifest path rejected: {relative}")
        by_name[relative] = item
    if set(by_name) != expected_payloads:
        _fail("manifest_invalid", "batch manifest coverage does not match allowlist")
    coverage = manifest.get("file_hash_coverage") or {}
    if (
        coverage.get("status") != "complete"
        or coverage.get("byte_hashed_payload_file_count")
        != source_contract["manifest_payload_count"]
    ):
        _fail("manifest_invalid", "batch manifest hash coverage is incomplete")

    file_hashes: dict[str, str] = {}
    for name in sorted(expected_payloads):
        path = package / name
        digest = _sha256(path)
        file_hashes[name] = digest
        item = by_name[name]
        if item.get("sha256") != digest or item.get("bytes") != path.stat().st_size:
            _fail("manifest_hash_mismatch", f"manifest hash/size mismatch: {name}")
        repo_relative = item.get("repo_relative_path")
        _validate_repo_relative_path(repo_relative, "manifest repo-relative path")
    manifest_digest = _sha256(manifest_path)
    file_hashes["batch_manifest.json"] = manifest_digest
    declared_self = (manifest.get("manifest_self_integrity") or {}).get("sha256")
    calculated_self = canonical_manifest_self_hash(manifest)
    expected_self = source_contract["batch_manifest_self_integrity_sha256"]
    if declared_self != calculated_self:
        _fail("manifest_self_integrity_mismatch", "manifest canonical self-hash failed")
    if declared_self != expected_self:
        _fail(
            "manifest_identity_mismatch",
            "manifest identity differs from Thank evidence",
        )

    candidates = contract["candidate_identity"]
    for candidate_id, identity in sorted(candidates.items()):
        candidate_path = package / identity["package_relative_path"]
        if _sha256(candidate_path) != identity["sha256"]:
            _fail("candidate_hash_mismatch", f"{candidate_id} SHA-256 changed")

    readback = _read_json(package / "batch_readback.json", "batch readback")
    plan = _read_json(package / "candidate_plan.json", "candidate plan")
    _validate_candidate_documents(readback=readback, plan=plan, contract=contract)

    return {
        "status": "package_verified_exact",
        "artifact_id": contract["source_artifact_id"],
        "package_repo_relative_path": contract["source_package"]["repo_relative_path"],
        "file_count": len(actual),
        "manifest_payload_count": len(entries),
        "manifest_self_integrity_sha256": declared_self,
        "batch_manifest_file_sha256": manifest_digest,
        "candidate_hashes": {
            candidate_id: identity["sha256"]
            for candidate_id, identity in sorted(candidates.items())
        },
        "cut_009_exclusion": contract["cut_009_exclusion"]["status"],
        "package_tree_sha256": _tree_digest(file_hashes),
        "file_hashes": dict(sorted(file_hashes.items())),
    }


def export_package(
    *,
    package_path: Path,
    destination: Path,
    contract: dict[str, Any],
    repo_root: Path,
    host_name: str | None = None,
) -> dict[str, Any]:
    destination = destination.resolve()
    root = repo_root.resolve()
    if destination.suffix.lower() != ".zip":
        _fail("destination_invalid", "export destination must end in .zip")
    if _is_within(destination, root):
        _fail(
            "destination_invalid",
            "private archive destination must be outside the repo",
        )
    if destination.exists():
        _fail("destination_exists", "export destination already exists")

    resolved_host = _host_name(host_name)
    expected_host = str(contract["host_contract"]["last_verified_host_name"])
    if not resolved_host:
        _fail("host_unknown", "export host name could not be determined")
    if resolved_host.casefold() != expected_host.casefold():
        _fail(
            "source_host_mismatch",
            f"export requires last-verified host {expected_host}; got {resolved_host}",
        )
    resolved_host = expected_host

    before = validate_package(
        package_path=package_path, contract=contract, repo_root=repo_root
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    receipt = _transfer_receipt(
        contract=contract, validation=before, host_name=resolved_host
    )
    receipt_bytes = _json_bytes(receipt)
    temporary = destination.parent / f".{destination.name}.staging-{uuid.uuid4().hex}"
    try:
        with zipfile.ZipFile(temporary, "x", allowZip64=True) as archive:
            receipt_name = contract["archive_contract"]["transfer_receipt_filename"]
            archive_names = sorted(
                [*contract["source_package"]["expected_files"], receipt_name]
            )
            for name in archive_names:
                if name == receipt_name:
                    _write_zip_bytes(archive, name, receipt_bytes)
                else:
                    _write_zip_file(archive, name, package_path.resolve() / name)
        _validate_archive_structure(temporary, contract)
        after = validate_package(
            package_path=package_path, contract=contract, repo_root=repo_root
        )
        if before["package_tree_sha256"] != after["package_tree_sha256"]:
            _fail("source_package_mutated", "source package changed during export")
        temporary.replace(destination)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
    return {
        "status": "export_ready_for_private_copy",
        "archive": str(destination),
        "archive_sha256": _sha256(destination),
        "source_host_name": resolved_host,
        "package_tree_sha256": before["package_tree_sha256"],
        "package_file_count": before["file_count"],
        "media_regenerated": False,
        "upload_performed": False,
        "source_package_mutated": False,
    }


def import_package(
    *,
    archive_path: Path,
    package_path: Path,
    contract: dict[str, Any],
    repo_root: Path,
    start_server: bool = False,
    port: int = 8071,
    host_name: str | None = None,
) -> dict[str, Any]:
    archive_input = archive_path.absolute()
    package = package_path.resolve()
    root = repo_root.resolve()
    _require_within(package, root, "OUT-08 package")
    if not archive_input.is_file():
        _fail("archive_missing", "private transfer archive is missing")
    if _is_link_or_reparse(archive_input):
        _fail("archive_link_input", "linked/reparse archive input is rejected")
    archive_path = archive_input.resolve()
    if _is_within(archive_path, root):
        _fail("archive_inside_repo", "private transfer archive must remain outside Git")
    package.parent.mkdir(parents=True, exist_ok=True)
    stage = package.parent / f".{package.name}.import-staging-{uuid.uuid4().hex}"
    if stage.exists():
        _fail("staging_collision", "import staging directory already exists")
    stage.mkdir()
    promoted = False
    preserved_existing = False
    try:
        receipt = _extract_archive_to_stage(
            archive_path=archive_path,
            stage=stage,
            contract=contract,
        )
        staged = validate_package(package_path=stage, contract=contract, repo_root=root)
        _validate_transfer_receipt(receipt, contract=contract, validation=staged)

        if package.exists():
            try:
                existing = validate_package(
                    package_path=package, contract=contract, repo_root=root
                )
            except Out08PrivateRecoveryError as exc:
                _fail(
                    "existing_package_invalid",
                    f"existing package was preserved and import refused: {exc.category}",
                )
            if existing["package_tree_sha256"] != staged["package_tree_sha256"]:
                _fail(
                    "existing_package_unknown",
                    "existing valid package identity differs",
                )
            preserved_existing = True
            shutil.rmtree(stage)
        else:
            stage.replace(package)
            promoted = True

        verification = validate_package(
            package_path=package, contract=contract, repo_root=root
        )
        server_status = "server_stopped"
        if start_server:
            server_status = start_and_verify_server(
                package_path=package,
                port=port,
                repo_root=root,
            )
        probe = probe_host(
            package_path=package,
            contract=contract,
            repo_root=root,
            port=port,
            host_name=host_name,
            write_receipt=True,
        )
        if start_server and probe["server_status"] != "server_running_verified":
            _fail("server_probe_failed", "server did not remain verified after import")
        return {
            "status": (
                "existing_valid_package_preserved"
                if preserved_existing
                else "package_imported_atomically"
            ),
            "package_status": verification["status"],
            "package_repo_relative_path": verification["package_repo_relative_path"],
            "package_tree_sha256": verification["package_tree_sha256"],
            "server_status": server_status if start_server else probe["server_status"],
            "host_receipt_repo_relative_path": contract["host_contract"][
                "host_receipt_repo_relative_path"
            ],
            "atomic_promotion": promoted,
            "existing_valid_package_preserved": preserved_existing,
            "media_regenerated": False,
            "private_transfer_performed_by_tool": False,
        }
    finally:
        if stage.exists():
            _remove_stage(stage, expected_parent=package.parent)


def probe_host(
    *,
    package_path: Path,
    contract: dict[str, Any],
    repo_root: Path,
    port: int = 8071,
    host_name: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    resolved_host = _host_name(host_name)
    host_status = "host_known" if resolved_host else "host_unknown"
    validation: dict[str, Any] | None = None
    invalid_category: str | None = None
    if not package_path.exists():
        package_status = "package_missing"
    else:
        try:
            validation = validate_package(
                package_path=package_path, contract=contract, repo_root=repo_root
            )
            package_status = "package_verified_exact"
        except Out08PrivateRecoveryError as exc:
            package_status = "package_present_invalid"
            invalid_category = exc.category

    server_status = probe_server(
        package_path=package_path if validation is not None else None,
        port=port,
    )
    classifications = [package_status, server_status]
    if (
        host_status == "host_unknown" or server_status == "host_unknown"
    ) and "host_unknown" not in classifications:
        classifications.append("host_unknown")
    receipt = {
        "schema_version": HOST_RECEIPT_SCHEMA,
        "recovery_artifact_id": contract["artifact_id"],
        "source_artifact_id": contract["source_artifact_id"],
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_name": resolved_host,
        "host_status": host_status,
        "package_status": package_status,
        "package_invalid_category": invalid_category,
        "server_status": server_status,
        "classifications": classifications,
        "package_repo_relative_path": contract["source_package"]["repo_relative_path"],
        "candidate_hashes": {
            key: value["sha256"]
            for key, value in sorted(contract["candidate_identity"].items())
        },
        "manifest_self_integrity_sha256": contract["source_package"][
            "batch_manifest_self_integrity_sha256"
        ],
        "cut_009_exclusion": contract["cut_009_exclusion"]["status"],
        "access_status": (
            "host_unknown"
            if host_status == "host_unknown" or server_status == "host_unknown"
            else "exact_package_and_server_verified"
            if package_status == "package_verified_exact"
            and server_status == "server_running_verified"
            else "recovery_kit_ready_package_not_yet_imported"
            if package_status == "package_missing"
            else "package_verified_server_stopped"
            if package_status == "package_verified_exact"
            else "recovery_blocked_invalid_local_package"
        ),
        "human_review_accessible": package_status == "package_verified_exact"
        and server_status == "server_running_verified",
        "media_regenerated": False,
        "private_transfer_performed": False,
    }
    if validation is not None:
        receipt["package_tree_sha256"] = validation["package_tree_sha256"]
    if write_receipt:
        receipt_path = default_host_receipt_path(repo_root, contract)
        _require_within(receipt_path, repo_root.resolve(), "host receipt")
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(receipt_path, receipt)
    return receipt


def probe_server(*, package_path: Path | None, port: int) -> str:
    if not 1 <= int(port) <= 65535:
        _fail("port_invalid", "port must be between 1 and 65535")
    if package_path is None:
        try:
            with socket.create_connection(("127.0.0.1", int(port)), timeout=0.35):
                return "host_unknown"
        except OSError:
            return "server_stopped"
    try:
        index_bytes = (package_path / "index.html").read_bytes()
        with urlrequest.urlopen(
            f"http://127.0.0.1:{port}/index.html", timeout=1.0
        ) as response:
            if response.status != 200 or response.read() != index_bytes:
                return "host_unknown"
        expected = (package_path / "candidate_01.mp4").read_bytes()[:SERVER_PROBE_BYTES]
        request = urlrequest.Request(
            f"http://127.0.0.1:{port}/candidate_01.mp4",
            headers={"Range": f"bytes=0-{max(0, len(expected) - 1)}"},
        )
        with urlrequest.urlopen(request, timeout=1.0) as response:
            if response.status != 206 or response.read() != expected:
                return "host_unknown"
        return "server_running_verified"
    except urlerror.HTTPError:
        return "host_unknown"
    except (ValueError, http_client.HTTPException):
        return "host_unknown"
    except (OSError, urlerror.URLError, TimeoutError):
        return "server_stopped"


def start_and_verify_server(*, package_path: Path, port: int, repo_root: Path) -> str:
    current = probe_server(package_path=package_path, port=port)
    if current == "server_running_verified":
        return current
    if current == "host_unknown":
        _fail("server_port_conflict", "port is occupied by an unverified server")
    command = [
        sys.executable,
        "-m",
        "src.cli.serve_review",
        "--root",
        str(package_path),
        "--port",
        str(port),
    ]
    kwargs: dict[str, Any] = {
        "cwd": str(repo_root),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(command, **kwargs)
    for _ in range(50):
        status = probe_server(package_path=package_path, port=port)
        if status == "server_running_verified":
            return status
        if process.poll() is not None:
            break
        time.sleep(0.1)
    if process.poll() is None:
        process.terminate()
    _fail("server_start_failed", "localhost review server did not verify")


def canonical_manifest_self_hash(manifest: dict[str, Any]) -> str:
    payload = copy.deepcopy(manifest)
    payload.setdefault("manifest_self_integrity", {})["sha256"] = None
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_candidate_documents(
    *, readback: dict[str, Any], plan: dict[str, Any], contract: dict[str, Any]
) -> None:
    source_artifact = contract["source_artifact_id"]
    if readback.get("artifact_id") != source_artifact:
        _fail("candidate_identity_mismatch", "batch readback artifact changed")
    if plan.get("artifact_id") != source_artifact:
        _fail("candidate_identity_mismatch", "candidate plan artifact changed")
    if (
        readback.get("actual_candidate_count") != 2
        or plan.get("actual_candidate_count") != 2
    ):
        _fail("candidate_identity_mismatch", "candidate count changed")
    if plan.get("cut009_final_cut_decision") != "reject":
        _fail("cut_009_overlap", "candidate plan no longer preserves cut_009 reject")
    boundaries = readback.get("boundaries") or {}
    required_boundaries = {
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
    }
    if any(boundaries.get(key) != value for key, value in required_boundaries.items()):
        _fail("closed_gate_mismatch", "batch readback closed gates changed")

    expected_ids = {"candidate_01", "candidate_02"}
    readback_candidates = _candidate_map(readback.get("candidates"), "batch readback")
    plan_candidates = _candidate_map(plan.get("candidates"), "candidate plan")
    if set(readback_candidates) != expected_ids or set(plan_candidates) != expected_ids:
        _fail("candidate_identity_mismatch", "candidate IDs changed")
    for candidate_id, identity in contract["candidate_identity"].items():
        video = readback_candidates[candidate_id].get("video") or {}
        if (
            video.get("package_relative_path") != identity["package_relative_path"]
            or video.get("sha256") != identity["sha256"]
        ):
            _fail(
                "candidate_hash_mismatch", f"{candidate_id} readback identity changed"
            )
    for candidate_id, candidate in readback_candidates.items():
        _validate_ranges(candidate_id, candidate.get("source_ranges"), contract)
    for candidate_id, candidate in plan_candidates.items():
        _validate_ranges(candidate_id, candidate.get("timeline"), contract)
        if candidate.get("cut009_rejection_preserved") is not True:
            _fail("cut_009_overlap", f"{candidate_id} cut_009 guard changed")

    source_hash = contract["source_identity"]["last_verified_source_video_sha256"]
    source_video = (readback.get("source_identity") or {}).get("source_video")
    if not _contains_value(source_video, source_hash):
        _fail("source_identity_mismatch", "Thank source video identity is missing")


def _validate_ranges(candidate_id: str, ranges: Any, contract: dict[str, Any]) -> None:
    if not isinstance(ranges, list) or not ranges:
        _fail("cut_009_overlap", f"{candidate_id} source ranges are missing")
    cut = contract["cut_009_exclusion"]
    reject_start = float(cut["reject_interval_start_seconds"])
    reject_end = float(cut["reject_interval_end_seconds"])
    maximum_end = float(cut["candidate_02_max_source_end_seconds"])
    for item in ranges:
        if not isinstance(item, dict):
            _fail("cut_009_overlap", f"{candidate_id} source range is invalid")
        try:
            start = float(item["source_start_seconds"])
            end = float(item["source_end_seconds"])
        except (KeyError, TypeError, ValueError) as exc:
            raise Out08PrivateRecoveryError(
                "cut_009_overlap", f"{candidate_id} source range is invalid"
            ) from exc
        if end <= start:
            _fail("cut_009_overlap", f"{candidate_id} source range is not positive")
        if (
            start < reject_end - CUT_TIME_TOLERANCE_SECONDS
            and reject_start < end - CUT_TIME_TOLERANCE_SECONDS
        ):
            _fail("cut_009_overlap", f"{candidate_id} overlaps cut_009")
        authorities = item.get("authority_cut_ids") or []
        if cut["cut_id"] in authorities:
            _fail("cut_009_overlap", f"{candidate_id} names cut_009 authority")
        if candidate_id == "candidate_02" and end > (
            maximum_end + CUT_TIME_TOLERANCE_SECONDS
        ):
            _fail("cut_009_overlap", "candidate_02 extends beyond 135.219 seconds")


def _validate_archive_structure(path: Path, contract: dict[str, Any]) -> None:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            _validate_zip_infos(infos, contract)
            bad = archive.testzip()
            if bad is not None:
                _fail("archive_corrupt", f"archive CRC failed: {bad}")
            receipt_name = contract["archive_contract"]["transfer_receipt_filename"]
            try:
                _read_json_bytes(archive.read(receipt_name), "transfer receipt")
            except KeyError as exc:
                raise Out08PrivateRecoveryError(
                    "archive_missing_file", "transfer receipt is missing"
                ) from exc
    except zipfile.BadZipFile as exc:
        raise Out08PrivateRecoveryError(
            "archive_corrupt", "archive is not a valid ZIP"
        ) from exc


def _extract_archive_to_stage(
    *, archive_path: Path, stage: Path, contract: dict[str, Any]
) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            infos = archive.infolist()
            _validate_zip_infos(infos, contract)
            bad = archive.testzip()
            if bad is not None:
                _fail("archive_corrupt", f"archive CRC failed: {bad}")
            receipt_name = contract["archive_contract"]["transfer_receipt_filename"]
            receipt = _read_json_bytes(archive.read(receipt_name), "transfer receipt")
            for name in sorted(contract["source_package"]["expected_files"]):
                target = stage / name
                with archive.open(name, "r") as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
            return receipt
    except zipfile.BadZipFile as exc:
        raise Out08PrivateRecoveryError(
            "archive_corrupt", "archive is not a valid ZIP"
        ) from exc
    except KeyError as exc:
        raise Out08PrivateRecoveryError(
            "archive_missing_file", f"archive entry missing: {exc}"
        ) from exc


def _validate_zip_infos(infos: list[zipfile.ZipInfo], contract: dict[str, Any]) -> None:
    receipt_name = contract["archive_contract"]["transfer_receipt_filename"]
    expected = set(contract["source_package"]["expected_files"]) | {receipt_name}
    names: list[str] = []
    folded: set[str] = set()
    total_size = 0
    for info in infos:
        name = info.filename
        if info.is_dir():
            _fail("archive_unexpected_file", f"directory entry rejected: {name}")
        _validate_flat_relative_name(name, "archive entry")
        if name in names:
            _fail(
                "archive_duplicate_entry", f"duplicate archive entry rejected: {name}"
            )
        casefolded = name.casefold()
        if casefolded in folded:
            _fail("archive_case_collision", f"case collision rejected: {name}")
        names.append(name)
        folded.add(casefolded)
        total_size += int(info.file_size)
        if info.flag_bits & 0x1:
            _fail("archive_encrypted", f"encrypted entry rejected: {name}")
        if info.compress_type != zipfile.ZIP_STORED:
            _fail("archive_compression_invalid", f"compressed entry rejected: {name}")
        unix_type = (info.external_attr >> 16) & 0o170000
        if unix_type == stat.S_IFLNK:
            _fail("archive_link_entry", f"symlink entry rejected: {name}")
        if unix_type not in (0, stat.S_IFREG):
            _fail("archive_link_entry", f"non-regular entry rejected: {name}")
    if total_size > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
        _fail("archive_too_large", "archive uncompressed size exceeds recovery limit")
    actual = set(names)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        _fail(
            "archive_allowlist_mismatch",
            f"archive allowlist mismatch; missing={missing}; extra={extra}",
        )


def _transfer_receipt(
    *, contract: dict[str, Any], validation: dict[str, Any], host_name: str
) -> dict[str, Any]:
    return {
        "schema_version": TRANSFER_RECEIPT_SCHEMA,
        "recovery_artifact_id": contract["artifact_id"],
        "source_artifact_id": contract["source_artifact_id"],
        "source_host_label": contract["host_contract"]["last_verified_host_label"],
        "source_host_name": host_name,
        "package_repo_relative_path": validation["package_repo_relative_path"],
        "package_file_count": validation["file_count"],
        "manifest_payload_count": validation["manifest_payload_count"],
        "manifest_self_integrity_sha256": validation["manifest_self_integrity_sha256"],
        "batch_manifest_file_sha256": validation["batch_manifest_file_sha256"],
        "candidate_hashes": validation["candidate_hashes"],
        "cut_009_exclusion": validation["cut_009_exclusion"],
        "package_tree_sha256": validation["package_tree_sha256"],
        "package_files": sorted(validation["file_hashes"]),
        "media_regenerated": False,
        "source_package_mutated": False,
        "git_transport": False,
        "upload_performed": False,
    }


def _validate_transfer_receipt(
    receipt: dict[str, Any], *, contract: dict[str, Any], validation: dict[str, Any]
) -> None:
    expected_host = contract["host_contract"]["last_verified_host_name"]
    checks = {
        "schema_version": TRANSFER_RECEIPT_SCHEMA,
        "recovery_artifact_id": contract["artifact_id"],
        "source_artifact_id": contract["source_artifact_id"],
        "source_host_name": expected_host,
        "package_repo_relative_path": validation["package_repo_relative_path"],
        "package_file_count": validation["file_count"],
        "manifest_payload_count": validation["manifest_payload_count"],
        "manifest_self_integrity_sha256": validation["manifest_self_integrity_sha256"],
        "batch_manifest_file_sha256": validation["batch_manifest_file_sha256"],
        "candidate_hashes": validation["candidate_hashes"],
        "cut_009_exclusion": validation["cut_009_exclusion"],
        "package_tree_sha256": validation["package_tree_sha256"],
        "package_files": sorted(validation["file_hashes"]),
        "media_regenerated": False,
        "source_package_mutated": False,
        "git_transport": False,
        "upload_performed": False,
    }
    for key, expected in checks.items():
        actual = receipt.get(key)
        if key == "source_host_name" and isinstance(actual, str):
            if actual.casefold() == str(expected).casefold():
                continue
        if actual != expected:
            _fail("transfer_receipt_mismatch", f"transfer receipt changed: {key}")


def _write_zip_file(archive: zipfile.ZipFile, name: str, source: Path) -> None:
    info = _zip_info(name)
    with (
        archive.open(info, "w", force_zip64=True) as output,
        source.open("rb") as input_file,
    ):
        shutil.copyfileobj(input_file, output, length=1024 * 1024)


def _write_zip_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    archive.writestr(_zip_info(name), data)


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100600 << 16
    return info


def _candidate_map(values: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(values, list):
        _fail("candidate_identity_mismatch", f"{label} candidates are missing")
    mapped: dict[str, dict[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict) or not isinstance(item.get("candidate_id"), str):
            _fail("candidate_identity_mismatch", f"{label} candidate is invalid")
        candidate_id = item["candidate_id"]
        if candidate_id in mapped:
            _fail("candidate_identity_mismatch", f"duplicate candidate: {candidate_id}")
        mapped[candidate_id] = item
    return mapped


def _validate_flat_relative_name(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value or "\\" in value:
        _fail("path_traversal", f"invalid {label}")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or len(pure.parts) != 1
        or pure.parts[0] in (".", "..")
        or ":" in pure.parts[0]
    ):
        _fail("path_traversal", f"unsafe {label}: {value}")


def _validate_repo_relative_path(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value or "\\" in value:
        _fail("contract_invalid", f"invalid {label}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or ":" in pure.parts[0]:
        _fail("contract_invalid", f"unsafe {label}")


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    except OSError:
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _contains_value(value: Any, target: str) -> bool:
    if value == target:
        return True
    if isinstance(value, dict):
        return any(_contains_value(item, target) for item in value.values())
    if isinstance(value, list):
        return any(_contains_value(item, target) for item in value)
    return False


def _tree_digest(file_hashes: dict[str, str]) -> str:
    rows = [f"{name}\t{digest}" for name, digest in sorted(file_hashes.items())]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return _read_json_bytes(path.read_bytes(), label)
    except OSError as exc:
        raise Out08PrivateRecoveryError(
            "file_read_failed", f"cannot read {label}"
        ) from exc


def _read_json_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Out08PrivateRecoveryError("json_invalid", f"invalid {label}") from exc
    if not isinstance(payload, dict):
        _fail("json_invalid", f"{label} must be an object")
    return payload


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.parent / f".{path.name}.staging-{uuid.uuid4().hex}"
    try:
        temporary.write_bytes(_json_bytes(payload))
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _host_name(value: str | None = None) -> str | None:
    candidate = value if value is not None else socket.gethostname()
    candidate = str(candidate or "").strip()
    return candidate or None


def _require_sha256(value: Any, label: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _fail("contract_invalid", f"invalid {label}")


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _require_within(path: Path, parent: Path, label: str) -> None:
    if not _is_within(path, parent):
        _fail("path_outside_repo", f"{label} must remain inside the repo")


def _remove_stage(stage: Path, *, expected_parent: Path) -> None:
    if stage.parent != expected_parent or not stage.name.startswith(".out08_"):
        _fail("staging_cleanup_refused", "unsafe staging cleanup target")
    shutil.rmtree(stage)


def _fail(category: str, message: str) -> None:
    raise Out08PrivateRecoveryError(category, message)
