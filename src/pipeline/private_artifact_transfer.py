"""Build and verify private, offline artifact transfer bundles.

The payload stays outside Git.  Archive members retain repository-relative
``episodes/`` paths so an authenticated receiver can restore exact source and
review bytes into a fresh checkout without guessing where they belong.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from uuid import uuid4


SCHEMA_VERSION = "clippipegen.private_artifact_transfer.v1"
MANIFEST_PATH = "_clippipegen_transfer/manifest.json"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
COPY_CHUNK_BYTES = 1024 * 1024

FORBIDDEN_PARTS = {
    ".git",
    ".serena",
    ".playwright-mcp",
    ".credentials",
    "node_modules",
    "__pycache__",
}
FORBIDDEN_FILE_NAMES = {
    ".env",
    "cookies.txt",
    "youtube_client_secret.json",
    "youtube_oauth_token.json",
}


class PrivateArtifactTransferError(RuntimeError):
    """Fail-closed transfer bundle error with a stable stage."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(COPY_CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_stream(handle: Any) -> str:
    digest = hashlib.sha256()
    while chunk := handle.read(COPY_CHUNK_BYTES):
        digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _manifest_self_digest(payload: dict[str, Any]) -> str:
    clone = json.loads(json.dumps(payload))
    clone["manifest_self_integrity"]["sha256"] = None
    return hashlib.sha256(_canonical_json_bytes(clone)).hexdigest()


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _validate_payload_path(repo_relative_path: str) -> PurePosixPath:
    if "\\" in repo_relative_path or "\x00" in repo_relative_path:
        raise PrivateArtifactTransferError(
            "path_safety", "payload paths must use safe POSIX separators"
        )
    path = PurePosixPath(repo_relative_path)
    if path.is_absolute() or not path.parts or path.parts[0].casefold() != "episodes":
        raise PrivateArtifactTransferError(
            "path_safety", "private transfer payloads must stay under episodes/"
        )
    if any(part in ("", ".", "..") for part in path.parts):
        raise PrivateArtifactTransferError(
            "path_safety", f"unsafe payload path: {repo_relative_path}"
        )
    folded_parts = {part.casefold() for part in path.parts}
    if folded_parts & FORBIDDEN_PARTS:
        raise PrivateArtifactTransferError(
            "path_safety", f"forbidden local/runtime path: {repo_relative_path}"
        )
    file_name = path.name.casefold()
    if file_name in FORBIDDEN_FILE_NAMES or file_name.startswith(".env."):
        raise PrivateArtifactTransferError(
            "path_safety", f"secret-like file is forbidden: {repo_relative_path}"
        )
    return path


def _resolve_input(base_dir: Path, raw_path: Path) -> Path:
    if raw_path.is_absolute():
        raise PrivateArtifactTransferError(
            "input_preflight", "--include paths must be repository-relative"
        )
    candidate = base_dir / raw_path
    if not candidate.exists():
        raise PrivateArtifactTransferError(
            "input_preflight", f"included path does not exist: {raw_path.as_posix()}"
        )
    try:
        candidate.resolve(strict=True).relative_to(base_dir)
    except ValueError as exc:
        raise PrivateArtifactTransferError(
            "input_preflight", f"included path escapes the repository: {raw_path}"
        ) from exc
    return candidate


def _collect_payload_files(base_dir: Path, includes: Iterable[Path]) -> list[Path]:
    files: dict[str, Path] = {}
    for raw_path in includes:
        candidate = _resolve_input(base_dir, raw_path)
        candidates = [candidate] if candidate.is_file() else sorted(candidate.rglob("*"))
        for path in candidates:
            if _is_reparse_point(path):
                raise PrivateArtifactTransferError(
                    "input_preflight", f"reparse points are forbidden: {path}"
                )
            if not path.is_file():
                continue
            relative = path.relative_to(base_dir).as_posix()
            _validate_payload_path(relative)
            files[relative] = path
    if not files:
        raise PrivateArtifactTransferError(
            "input_preflight", "the transfer bundle would contain no files"
        )
    return [files[key] for key in sorted(files)]


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    return info


def build_private_artifact_transfer(
    *,
    bundle_id: str,
    artifact_id: str,
    source_identity: str,
    repo_head: str,
    includes: Iterable[Path],
    output_path: Path,
    base_dir: Path,
) -> dict[str, Any]:
    """Create one immutable ZIP plus an adjacent exact-hash receipt."""

    base_dir = base_dir.resolve(strict=True)
    if not bundle_id.startswith("clip-") or not artifact_id.startswith("clip-"):
        raise PrivateArtifactTransferError(
            "input_preflight", "bundle_id and artifact_id must be clip-* identities"
        )
    if len(repo_head) != 40 or any(char not in "0123456789abcdef" for char in repo_head):
        raise PrivateArtifactTransferError(
            "input_preflight", "repo_head must be a lowercase 40-character Git SHA"
        )
    if output_path.is_absolute():
        raise PrivateArtifactTransferError(
            "input_preflight", "--output must be repository-relative"
        )
    output_path = base_dir / output_path
    output_relative = output_path.relative_to(base_dir).as_posix()
    _validate_payload_path(output_relative)
    if output_path.suffix.casefold() != ".zip":
        raise PrivateArtifactTransferError(
            "input_preflight", "--output must end in .zip"
        )
    receipt_path = output_path.with_suffix(output_path.suffix + ".receipt.json")
    if output_path.exists() or receipt_path.exists():
        raise PrivateArtifactTransferError(
            "input_preflight", "immutable output or receipt already exists"
        )

    payload_files = _collect_payload_files(base_dir, includes)
    payload_entries: list[dict[str, Any]] = []
    for path in payload_files:
        relative = path.relative_to(base_dir).as_posix()
        payload_entries.append(
            {
                "repo_relative_path": relative,
                "byte_size": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "artifact_id": artifact_id,
        "source_identity": source_identity,
        "repo_head": repo_head,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "transport": {
            "class": "private_authenticated_or_offline_transfer_only",
            "public_sharing": False,
            "git_tracking": False,
            "upload_is_publication": False,
        },
        "payload": {
            "path_root": "repository_root",
            "file_count": len(payload_entries),
            "byte_size": sum(entry["byte_size"] for entry in payload_entries),
            "entries": payload_entries,
        },
        "closed_gates": {
            "rights_approval": False,
            "production_acceptance": False,
            "public_or_publishing_acceptance": False,
            "monetized_use": False,
        },
        "restore_contract": {
            "existing_exact_files": "reuse",
            "existing_mismatched_files": "fail_closed_without_overwrite",
            "missing_files": "restore_after_full_archive_verification",
        },
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    manifest["manifest_self_integrity"]["sha256"] = _manifest_self_digest(manifest)
    manifest_bytes = _canonical_json_bytes(manifest)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(f".{output_path.name}.{uuid4().hex}.tmp")
    try:
        with zipfile.ZipFile(temp_path, mode="w", allowZip64=True) as archive:
            for path, entry in zip(payload_files, payload_entries, strict=True):
                with path.open("rb") as source, archive.open(
                    _zip_info(entry["repo_relative_path"]), mode="w"
                ) as target:
                    shutil.copyfileobj(source, target, length=COPY_CHUNK_BYTES)
            archive.writestr(_zip_info(MANIFEST_PATH), manifest_bytes)
        os.replace(temp_path, output_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "artifact_id": artifact_id,
        "source_identity": source_identity,
        "repo_head": repo_head,
        "archive_name": output_path.name,
        "archive_byte_size": output_path.stat().st_size,
        "archive_sha256": _sha256_file(output_path),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "manifest_self_sha256": manifest["manifest_self_integrity"]["sha256"],
        "payload_file_count": len(payload_entries),
        "payload_byte_size": manifest["payload"]["byte_size"],
        "storage_class": "ignored_private_transfer_ready_not_publication",
    }
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "state": "PRIVATE_ARTIFACT_TRANSFER_BUILT",
        "archive": output_path,
        "receipt": receipt_path,
        **receipt,
    }


def _read_and_validate_manifest(archive: zipfile.ZipFile) -> tuple[dict[str, Any], bytes]:
    infos = archive.infolist()
    names = [info.filename for info in infos]
    if len(names) != len(set(name.casefold() for name in names)):
        raise PrivateArtifactTransferError(
            "archive_validation", "duplicate or case-colliding archive member"
        )
    if MANIFEST_PATH not in names:
        raise PrivateArtifactTransferError(
            "archive_validation", "transfer manifest is missing"
        )
    manifest_info = archive.getinfo(MANIFEST_PATH)
    if manifest_info.file_size > 16 * 1024 * 1024:
        raise PrivateArtifactTransferError(
            "archive_validation", "transfer manifest is unexpectedly large"
        )
    manifest_bytes = archive.read(MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise PrivateArtifactTransferError(
            "archive_validation", "transfer manifest is invalid JSON"
        ) from exc
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise PrivateArtifactTransferError(
            "archive_validation", "unsupported transfer schema"
        )
    expected_self = manifest.get("manifest_self_integrity", {}).get("sha256")
    if expected_self != _manifest_self_digest(manifest):
        raise PrivateArtifactTransferError(
            "archive_validation", "manifest self-integrity mismatch"
        )
    return manifest, manifest_bytes


def verify_private_artifact_transfer(
    *,
    archive_path: Path,
    receipt_path: Path | None = None,
    restore_root: Path | None = None,
) -> dict[str, Any]:
    """Verify an archive and optionally restore missing files without overwrite."""

    archive_path = archive_path.resolve(strict=True)
    archive_sha256 = _sha256_file(archive_path)
    receipt: dict[str, Any] | None = None
    if receipt_path is not None:
        receipt = json.loads(receipt_path.resolve(strict=True).read_text(encoding="utf-8"))
        if receipt.get("archive_sha256") != archive_sha256:
            raise PrivateArtifactTransferError(
                "receipt_validation", "archive SHA does not match the receipt"
            )
        if receipt.get("archive_byte_size") != archive_path.stat().st_size:
            raise PrivateArtifactTransferError(
                "receipt_validation", "archive size does not match the receipt"
            )

    with zipfile.ZipFile(archive_path, mode="r") as archive:
        manifest, manifest_bytes = _read_and_validate_manifest(archive)
        entries = manifest.get("payload", {}).get("entries")
        if not isinstance(entries, list) or not entries:
            raise PrivateArtifactTransferError(
                "archive_validation", "manifest payload entries are missing"
            )
        expected_names = {MANIFEST_PATH}
        total_bytes = 0
        for entry in entries:
            relative = str(entry.get("repo_relative_path", ""))
            _validate_payload_path(relative)
            expected_names.add(relative)
            try:
                info = archive.getinfo(relative)
            except KeyError as exc:
                raise PrivateArtifactTransferError(
                    "archive_validation", f"payload member is missing: {relative}"
                ) from exc
            if info.is_dir() or info.file_size != entry.get("byte_size"):
                raise PrivateArtifactTransferError(
                    "archive_validation", f"payload size mismatch: {relative}"
                )
            with archive.open(info, mode="r") as handle:
                actual_sha = _sha256_stream(handle)
            if actual_sha != entry.get("sha256"):
                raise PrivateArtifactTransferError(
                    "archive_validation", f"payload SHA mismatch: {relative}"
                )
            total_bytes += info.file_size
        archive_names = {info.filename for info in archive.infolist()}
        if archive_names != expected_names:
            raise PrivateArtifactTransferError(
                "archive_validation", "archive contains unmanifested members"
            )
        payload = manifest["payload"]
        if payload.get("file_count") != len(entries) or payload.get("byte_size") != total_bytes:
            raise PrivateArtifactTransferError(
                "archive_validation", "payload aggregate counts do not match"
            )
        if receipt is not None and receipt.get("manifest_sha256") != hashlib.sha256(
            manifest_bytes
        ).hexdigest():
            raise PrivateArtifactTransferError(
                "receipt_validation", "manifest SHA does not match the receipt"
            )

        restored = 0
        existing = 0
        restore_targets: list[tuple[dict[str, Any], Path]] = []
        root = restore_root.resolve() if restore_root is not None else None
        if root is not None:
            root.mkdir(parents=True, exist_ok=True)
            for entry in entries:
                relative = PurePosixPath(entry["repo_relative_path"])
                target = root.joinpath(*relative.parts)
                try:
                    target.resolve(strict=False).relative_to(root)
                except ValueError as exc:
                    raise PrivateArtifactTransferError(
                        "restore_preflight", f"restore path escapes root: {relative}"
                    ) from exc
                for parent in target.parents:
                    if parent == root.parent:
                        break
                    if parent.exists() and _is_reparse_point(parent):
                        raise PrivateArtifactTransferError(
                            "restore_preflight", f"restore parent is a reparse point: {parent}"
                        )
                    if parent == root:
                        break
                if target.exists():
                    if not target.is_file() or target.stat().st_size != entry["byte_size"]:
                        raise PrivateArtifactTransferError(
                            "restore_preflight", f"existing restore target conflicts: {relative}"
                        )
                    if _sha256_file(target) != entry["sha256"]:
                        raise PrivateArtifactTransferError(
                            "restore_preflight", f"existing restore target SHA conflicts: {relative}"
                        )
                    existing += 1
                else:
                    restore_targets.append((entry, target))

            for entry, target in restore_targets:
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary: Path | None = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb", delete=False, dir=target.parent, prefix=f".{target.name}."
                    ) as output:
                        temporary = Path(output.name)
                        with archive.open(entry["repo_relative_path"], mode="r") as source:
                            shutil.copyfileobj(source, output, length=COPY_CHUNK_BYTES)
                    os.replace(temporary, target)
                    restored += 1
                except Exception:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
                    raise

    return {
        "state": "PRIVATE_ARTIFACT_TRANSFER_VERIFIED",
        "bundle_id": manifest["bundle_id"],
        "artifact_id": manifest["artifact_id"],
        "source_identity": manifest["source_identity"],
        "repo_head": manifest["repo_head"],
        "archive": archive_path,
        "archive_byte_size": archive_path.stat().st_size,
        "archive_sha256": archive_sha256,
        "payload_file_count": manifest["payload"]["file_count"],
        "payload_byte_size": manifest["payload"]["byte_size"],
        "restored_file_count": restored,
        "existing_exact_file_count": existing,
        "restore_root": root,
    }


def split_private_artifact_transfer(
    *,
    archive_path: Path,
    part_size_bytes: int,
) -> dict[str, Any]:
    """Split one verified archive into small, independently hashed transport parts."""

    archive_path = archive_path.resolve(strict=True)
    if part_size_bytes < 1024 * 1024:
        raise PrivateArtifactTransferError(
            "parts_preflight", "part_size_bytes must be at least 1 MiB"
        )
    manifest_path = archive_path.with_suffix(archive_path.suffix + ".parts.json")
    if manifest_path.exists():
        raise PrivateArtifactTransferError(
            "parts_preflight", "immutable parts manifest already exists"
        )

    part_entries: list[dict[str, Any]] = []
    created_parts: list[Path] = []
    try:
        with archive_path.open("rb") as source:
            index = 1
            while chunk := source.read(part_size_bytes):
                part_path = archive_path.with_name(
                    f"{archive_path.name}.part{index:04d}"
                )
                if part_path.exists():
                    raise PrivateArtifactTransferError(
                        "parts_preflight", f"immutable part already exists: {part_path.name}"
                    )
                temporary = part_path.with_name(f".{part_path.name}.{uuid4().hex}.tmp")
                temporary.write_bytes(chunk)
                os.replace(temporary, part_path)
                created_parts.append(part_path)
                part_entries.append(
                    {
                        "index": index,
                        "name": part_path.name,
                        "byte_size": len(chunk),
                        "sha256": hashlib.sha256(chunk).hexdigest(),
                    }
                )
                index += 1
    except Exception:
        for path in created_parts:
            path.unlink(missing_ok=True)
        raise

    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "private_artifact_transfer_parts",
        "archive_name": archive_path.name,
        "archive_byte_size": archive_path.stat().st_size,
        "archive_sha256": _sha256_file(archive_path),
        "part_size_bytes": part_size_bytes,
        "part_count": len(part_entries),
        "parts": part_entries,
        "assembly": {
            "order": "index_ascending",
            "existing_output": "fail_closed_without_overwrite",
            "post_assembly": "verify_archive_sha_then_run_verify_private_artifact_transfer",
        },
        "manifest_self_integrity": {
            "algorithm": "sha256-canonical-json-self-null",
            "sha256": None,
        },
    }
    payload["manifest_self_integrity"]["sha256"] = _manifest_self_digest(payload)
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "state": "PRIVATE_ARTIFACT_TRANSFER_SPLIT",
        "parts_manifest": manifest_path,
        "archive": archive_path,
        **{key: value for key, value in payload.items() if key != "parts"},
        "parts": created_parts,
    }


def verify_private_artifact_parts(
    *,
    parts_manifest_path: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Verify transport parts and optionally assemble the original archive."""

    parts_manifest_path = parts_manifest_path.resolve(strict=True)
    manifest = json.loads(parts_manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("kind") != "private_artifact_transfer_parts"
    ):
        raise PrivateArtifactTransferError(
            "parts_validation", "unsupported parts manifest"
        )
    if manifest.get("manifest_self_integrity", {}).get("sha256") != _manifest_self_digest(
        manifest
    ):
        raise PrivateArtifactTransferError(
            "parts_validation", "parts manifest self-integrity mismatch"
        )
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        raise PrivateArtifactTransferError(
            "parts_validation", "parts manifest contains no parts"
        )
    if manifest.get("part_count") != len(parts):
        raise PrivateArtifactTransferError(
            "parts_validation", "part count mismatch"
        )

    expected_indexes = list(range(1, len(parts) + 1))
    if [entry.get("index") for entry in parts] != expected_indexes:
        raise PrivateArtifactTransferError(
            "parts_validation", "parts are not indexed contiguously"
        )
    names = [str(entry.get("name", "")) for entry in parts]
    if len(names) != len(set(name.casefold() for name in names)):
        raise PrivateArtifactTransferError(
            "parts_validation", "duplicate or case-colliding part name"
        )
    for name in names:
        if PurePosixPath(name).name != name or "\\" in name or "\x00" in name:
            raise PrivateArtifactTransferError(
                "parts_validation", f"unsafe part name: {name}"
            )

    combined_digest = hashlib.sha256()
    total_bytes = 0
    part_paths: list[Path] = []
    for entry, name in zip(parts, names, strict=True):
        part_path = parts_manifest_path.parent / name
        if not part_path.is_file():
            raise PrivateArtifactTransferError(
                "parts_validation", f"transfer part is missing: {name}"
            )
        if part_path.stat().st_size != entry.get("byte_size"):
            raise PrivateArtifactTransferError(
                "parts_validation", f"transfer part size mismatch: {name}"
            )
        part_digest = hashlib.sha256()
        with part_path.open("rb") as handle:
            while chunk := handle.read(COPY_CHUNK_BYTES):
                part_digest.update(chunk)
                combined_digest.update(chunk)
                total_bytes += len(chunk)
        if part_digest.hexdigest() != entry.get("sha256"):
            raise PrivateArtifactTransferError(
                "parts_validation", f"transfer part SHA mismatch: {name}"
            )
        part_paths.append(part_path)
    if total_bytes != manifest.get("archive_byte_size"):
        raise PrivateArtifactTransferError(
            "parts_validation", "assembled archive size mismatch"
        )
    if combined_digest.hexdigest() != manifest.get("archive_sha256"):
        raise PrivateArtifactTransferError(
            "parts_validation", "assembled archive SHA mismatch"
        )

    assembled: Path | None = None
    if output_path is not None:
        output_path = output_path.resolve(strict=False)
        if output_path.exists():
            raise PrivateArtifactTransferError(
                "parts_assembly", "assembly output already exists"
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_name(f".{output_path.name}.{uuid4().hex}.tmp")
        try:
            with temporary.open("wb") as output:
                for part_path in part_paths:
                    with part_path.open("rb") as source:
                        shutil.copyfileobj(source, output, length=COPY_CHUNK_BYTES)
            if _sha256_file(temporary) != manifest["archive_sha256"]:
                raise PrivateArtifactTransferError(
                    "parts_assembly", "assembled temporary archive SHA mismatch"
                )
            os.replace(temporary, output_path)
            assembled = output_path
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    return {
        "state": "PRIVATE_ARTIFACT_TRANSFER_PARTS_VERIFIED",
        "parts_manifest": parts_manifest_path,
        "archive_name": manifest["archive_name"],
        "archive_byte_size": manifest["archive_byte_size"],
        "archive_sha256": manifest["archive_sha256"],
        "part_count": len(parts),
        "assembled_archive": assembled,
    }
