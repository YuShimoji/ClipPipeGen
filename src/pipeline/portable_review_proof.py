"""Fail-closed intake for an externally transported review proof package.

The transport archive may contain a wider project snapshot, but this module
extracts only the exact ``package/`` review surface described by a tracked
expectation. Hash verification is mechanical: it never assigns an editorial
winner or promotes a review proof to a finished episode.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


EXPECTATION_SCHEMA = "clippipegen.portable_review_proof_expectation.v1"
OUTER_MANIFEST_SCHEMA = "clippipegen.portable_review_outer_manifest.v1"
HANDOFF_CONTRACT_SCHEMA = "clippipegen.portable_review_handoff_contract.v1"
COPY_CHUNK_BYTES = 1024 * 1024


class PortableReviewProofError(RuntimeError):
    """Fail-closed portable review proof error with a stable stage."""

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


def _read_json(path: Path, *, stage: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortableReviewProofError(stage, f"invalid JSON file: {path}") from exc
    if not isinstance(payload, dict):
        raise PortableReviewProofError(stage, "JSON root must be an object")
    return payload


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_sha(value: object, *, field: str, stage: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise PortableReviewProofError(stage, f"{field} must be a lowercase SHA-256")
    return value


def _validate_member_name(name: str) -> PurePosixPath:
    if not name or "\\" in name or "\x00" in name or name.startswith("/"):
        raise PortableReviewProofError(
            "archive_validation", f"unsafe archive member path: {name!r}"
        )
    raw_parts = name.rstrip("/").split("/")
    if (
        not raw_parts
        or any(part in ("", ".", "..") for part in raw_parts)
        or raw_parts[0].endswith(":")
    ):
        raise PortableReviewProofError(
            "archive_validation", f"unsafe archive member path: {name!r}"
        )
    return PurePosixPath(*raw_parts)


def _validate_expectation(payload: dict[str, Any]) -> dict[str, Any]:
    stage = "expectation_validation"
    if payload.get("schema_version") != EXPECTATION_SCHEMA:
        raise PortableReviewProofError(stage, "unsupported expectation schema")
    artifact_id = payload.get("artifact_id")
    if not isinstance(artifact_id, str) or not artifact_id.startswith("clip-"):
        raise PortableReviewProofError(stage, "artifact_id must be a clip-* identity")
    source_identity = payload.get("source_identity")
    if not isinstance(source_identity, str) or ":" not in source_identity:
        raise PortableReviewProofError(stage, "source_identity must be an explicit identity")
    if payload.get("artifact_state") != "NON_ADOPTED_REVIEW_PROOF":
        raise PortableReviewProofError(
            stage, "artifact_state must remain NON_ADOPTED_REVIEW_PROOF"
        )
    package_root = payload.get("package_root")
    if package_root != "package":
        raise PortableReviewProofError(stage, "package_root must be exactly 'package'")
    file_count = payload.get("physical_file_count")
    if not _is_int(file_count) or file_count <= 0:
        raise PortableReviewProofError(stage, "physical_file_count must be positive")

    manifest = payload.get("manifest")
    review = payload.get("review_entrypoint")
    media = payload.get("media")
    required = payload.get("required_members")
    if not isinstance(manifest, dict) or not isinstance(review, dict):
        raise PortableReviewProofError(stage, "manifest and review_entrypoint are required")
    _validate_sha(
        manifest.get("self_sha256"), field="manifest.self_sha256", stage=stage
    )
    payload_file_count = manifest.get("payload_file_count")
    if (
        not _is_int(payload_file_count)
        or payload_file_count != file_count - 1
    ):
        raise PortableReviewProofError(
            stage, "manifest.payload_file_count must be physical_file_count minus one"
        )
    review_path = review.get("path")
    if review_path != "package/review/index.html":
        raise PortableReviewProofError(
            stage, "review entrypoint must remain package/review/index.html"
        )
    _validate_sha(review.get("sha256"), field="review_entrypoint.sha256", stage=stage)
    if not isinstance(required, list) or not required:
        raise PortableReviewProofError(stage, "required_members must be a non-empty list")
    required_names: list[str] = []
    for item in required:
        if not isinstance(item, str):
            raise PortableReviewProofError(stage, "required member paths must be strings")
        path = _validate_member_name(item)
        if not path.parts or path.parts[0] != package_root:
            raise PortableReviewProofError(stage, f"required member escapes package/: {item}")
        required_names.append(item)
    if len(required_names) != len({name.casefold() for name in required_names}):
        raise PortableReviewProofError(stage, "required member paths must be unique")
    if review_path not in required_names:
        raise PortableReviewProofError(stage, "review entrypoint must be required")

    if not isinstance(media, list) or len(media) != 4:
        raise PortableReviewProofError(stage, "exactly four retained MP4 identities are required")
    media_shas: set[str] = set()
    ordinals: set[int] = set()
    for item in media:
        if not isinstance(item, dict):
            raise PortableReviewProofError(stage, "media entries must be objects")
        ordinal = item.get("ordinal")
        byte_size = item.get("byte_size")
        duration_seconds = item.get("duration_seconds")
        if not _is_int(ordinal) or ordinal not in (1, 2, 3, 4):
            raise PortableReviewProofError(stage, "media ordinal must be 1 through 4")
        if not _is_int(byte_size) or byte_size <= 0:
            raise PortableReviewProofError(stage, "media byte_size must be positive")
        if (
            not isinstance(duration_seconds, (int, float))
            or isinstance(duration_seconds, bool)
            or duration_seconds <= 0
        ):
            raise PortableReviewProofError(stage, "media duration_seconds must be positive")
        sha = _validate_sha(item.get("sha256"), field="media.sha256", stage=stage)
        ordinals.add(ordinal)
        media_shas.add(sha)
    if ordinals != {1, 2, 3, 4} or len(media_shas) != 4:
        raise PortableReviewProofError(stage, "media ordinals and SHA identities must be unique")

    closed = payload.get("closed_gates")
    required_false = (
        "semantic_winner_selected",
        "human_creative_acceptance",
        "production_acceptance",
        "public_or_publishing_acceptance",
    )
    if not isinstance(closed, dict) or any(
        closed.get(key) is not False for key in required_false
    ):
        raise PortableReviewProofError(stage, "all semantic and production gates must remain false")
    return payload


def _validate_outer_manifest(
    payload: dict[str, Any], *, archive_path: Path, expectation: dict[str, Any]
) -> None:
    stage = "outer_manifest_validation"
    if payload.get("schema_version") != OUTER_MANIFEST_SCHEMA:
        raise PortableReviewProofError(stage, "unsupported outer manifest schema")
    if payload.get("artifact_id") != expectation["artifact_id"]:
        raise PortableReviewProofError(stage, "outer manifest artifact_id mismatch")
    if payload.get("archive_name") != archive_path.name:
        raise PortableReviewProofError(stage, "outer manifest archive_name mismatch")
    size = payload.get("archive_byte_size")
    if not _is_int(size) or size != archive_path.stat().st_size:
        raise PortableReviewProofError(stage, "outer manifest archive size mismatch")
    expected_sha = _validate_sha(
        payload.get("archive_sha256"), field="archive_sha256", stage=stage
    )
    if expected_sha != _sha256_file(archive_path):
        raise PortableReviewProofError(stage, "outer manifest archive SHA mismatch")
    if payload.get("package_root") != expectation["package_root"]:
        raise PortableReviewProofError(stage, "outer manifest package_root mismatch")
    if payload.get("package_file_count") != expectation["physical_file_count"]:
        raise PortableReviewProofError(stage, "outer manifest package file count mismatch")


def _is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    return stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK


def _canonical_manifest_self_hashes(manifest: dict[str, Any]) -> set[str]:
    clone = json.loads(json.dumps(manifest, ensure_ascii=False))
    integrity = clone.get("manifest_self_integrity")
    if not isinstance(integrity, dict):
        return set()
    integrity["sha256"] = None
    canonical = json.dumps(
        clone, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        hashlib.sha256(canonical).hexdigest(),
        hashlib.sha256(canonical + b"\n").hexdigest(),
    }


def _manifest_rows(manifest: dict[str, Any]) -> tuple[list[Any] | None, object]:
    rows = manifest.get("files")
    count = manifest.get("file_count")
    if isinstance(rows, list):
        return rows, count
    payload = manifest.get("payload")
    if isinstance(payload, dict):
        entries = payload.get("entries")
        if isinstance(entries, list):
            return entries, payload.get("file_count")
    return None, None


def _validate_package_manifest(
    *,
    archive: zipfile.ZipFile,
    package_names: set[str],
    hashes: dict[str, str],
    sizes: dict[str, int],
    expectation: dict[str, Any],
) -> str:
    expected_self = expectation["manifest"]["self_sha256"]
    candidates: list[tuple[str, dict[str, Any]]] = []
    for name in sorted(package_names):
        if not name.casefold().endswith(".json") or sizes[name] > 16 * 1024 * 1024:
            continue
        try:
            payload = json.loads(archive.read(name))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        declared = (payload.get("manifest_self_integrity") or {}).get("sha256")
        if declared == expected_self:
            candidates.append((name, payload))
    if len(candidates) != 1:
        raise PortableReviewProofError(
            "package_validation",
            "exactly one package manifest with the expected self SHA must be present",
        )
    manifest_path, manifest = candidates[0]
    if expected_self not in _canonical_manifest_self_hashes(manifest):
        raise PortableReviewProofError(
            "package_validation", "package manifest self-integrity mismatch"
        )

    rows, declared_count = _manifest_rows(manifest)
    expected_count = expectation["manifest"]["payload_file_count"]
    if rows is None or declared_count != expected_count or len(rows) != expected_count:
        raise PortableReviewProofError(
            "package_validation", "package manifest payload count mismatch"
        )
    manifest_names: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise PortableReviewProofError(
                "package_validation", "package manifest rows must be objects"
            )
        raw_path = row.get("repo_relative_path", row.get("path"))
        if not isinstance(raw_path, str):
            raise PortableReviewProofError(
                "package_validation", "package manifest row path is missing"
            )
        member_name = (
            raw_path
            if raw_path.startswith(expectation["package_root"] + "/")
            else expectation["package_root"] + "/" + raw_path
        )
        _validate_member_name(member_name)
        if member_name in manifest_names:
            raise PortableReviewProofError(
                "package_validation", "duplicate package manifest row path"
            )
        sha = _validate_sha(
            row.get("sha256"), field="package manifest row sha256", stage="package_validation"
        )
        byte_size = row.get("byte_size")
        if (
            member_name not in package_names
            or member_name == manifest_path
            or not _is_int(byte_size)
            or sizes[member_name] != byte_size
            or hashes[member_name] != sha
        ):
            raise PortableReviewProofError(
                "package_validation", f"package manifest payload mismatch: {member_name}"
            )
        manifest_names.add(member_name)
    if manifest_names != package_names - {manifest_path}:
        raise PortableReviewProofError(
            "package_validation", "package manifest does not close the package payload set"
        )
    return manifest_path


def _powershell_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _extract_package(
    *,
    archive: zipfile.ZipFile,
    package_infos: list[zipfile.ZipInfo],
    expected_hashes: dict[str, str],
    output_dir: Path,
) -> Path:
    output_dir = output_dir.resolve(strict=False)
    if output_dir.exists():
        raise PortableReviewProofError(
            "extraction_preflight", "extraction output already exists"
        )
    parent = output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    for candidate in (parent, *parent.parents):
        if candidate.exists() and _is_reparse_point(candidate):
            raise PortableReviewProofError(
                "extraction_preflight", f"extraction parent is a reparse point: {candidate}"
            )

    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=parent))
    try:
        for info in package_infos:
            relative = _validate_member_name(info.filename)
            target = temporary.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, mode="r") as source, target.open("xb") as sink:
                shutil.copyfileobj(source, sink, length=COPY_CHUNK_BYTES)
            if _sha256_file(target) != expected_hashes[info.filename]:
                raise PortableReviewProofError(
                    "extraction_validation", f"extracted SHA mismatch: {info.filename}"
                )
        os.replace(temporary, output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return output_dir


def verify_portable_review_proof(
    *,
    archive_path: Path,
    outer_manifest_path: Path,
    expectation_path: Path,
    extract_to: Path | None = None,
) -> dict[str, Any]:
    """Verify an exact non-adopted proof set and optionally extract only package/."""

    try:
        archive_path = archive_path.resolve(strict=True)
    except OSError as exc:
        raise PortableReviewProofError(
            "input_preflight", f"archive is unavailable: {archive_path}"
        ) from exc
    if not archive_path.is_file():
        raise PortableReviewProofError("input_preflight", "archive must be a file")
    expectation = _validate_expectation(
        _read_json(expectation_path, stage="expectation_validation")
    )
    outer = _read_json(outer_manifest_path, stage="outer_manifest_validation")
    _validate_outer_manifest(outer, archive_path=archive_path, expectation=expectation)

    package_prefix = expectation["package_root"] + "/"
    try:
        archive = zipfile.ZipFile(archive_path, mode="r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise PortableReviewProofError(
            "archive_validation", "transport is not a valid ZIP"
        ) from exc

    with archive:
        folded_names: set[str] = set()
        package_infos: list[zipfile.ZipInfo] = []
        for info in archive.infolist():
            path = _validate_member_name(info.filename)
            normalized = path.as_posix() + ("/" if info.is_dir() else "")
            folded = normalized.casefold()
            if folded in folded_names:
                raise PortableReviewProofError(
                    "archive_validation", "duplicate or case-colliding archive member"
                )
            folded_names.add(folded)
            if info.flag_bits & 0x1:
                raise PortableReviewProofError(
                    "archive_validation", f"encrypted archive member is forbidden: {info.filename}"
                )
            if _is_zip_symlink(info):
                raise PortableReviewProofError(
                    "archive_validation", f"symlink archive member is forbidden: {info.filename}"
                )
            if not info.is_dir() and info.filename.startswith(package_prefix):
                package_infos.append(info)

        if len(package_infos) != expectation["physical_file_count"]:
            raise PortableReviewProofError(
                "package_validation",
                "package file count mismatch: expected "
                f"{expectation['physical_file_count']}, got {len(package_infos)}",
            )
        package_names = {info.filename for info in package_infos}
        for required in expectation["required_members"]:
            if required not in package_names:
                raise PortableReviewProofError(
                    "package_validation", f"required package member is missing: {required}"
                )

        hashes: dict[str, str] = {}
        sizes: dict[str, int] = {}
        for info in package_infos:
            with archive.open(info, mode="r") as handle:
                hashes[info.filename] = _sha256_stream(handle)
            sizes[info.filename] = info.file_size

        review_path = expectation["review_entrypoint"]["path"]
        if hashes[review_path] != expectation["review_entrypoint"]["sha256"]:
            raise PortableReviewProofError("package_validation", "review HTML SHA mismatch")

        manifest_path = _validate_package_manifest(
            archive=archive,
            package_names=package_names,
            hashes=hashes,
            sizes=sizes,
            expectation=expectation,
        )

        actual_mp4 = sorted(
            name for name in package_names if name.casefold().endswith(".mp4")
        )
        if len(actual_mp4) != 4:
            raise PortableReviewProofError(
                "package_validation", "package must contain exactly four retained MP4 files"
            )
        media_by_sha = {item["sha256"]: item for item in expectation["media"]}
        located_media: list[dict[str, Any]] = []
        for name in actual_mp4:
            item = media_by_sha.get(hashes[name])
            if item is None or sizes[name] != item["byte_size"]:
                raise PortableReviewProofError(
                    "package_validation", f"MP4 identity mismatch: {name}"
                )
            located_media.append(
                {
                    "ordinal": item["ordinal"],
                    "path": name,
                    "byte_size": sizes[name],
                    "sha256": hashes[name],
                    "recorded_duration_seconds": item["duration_seconds"],
                }
            )
        if {item["sha256"] for item in located_media} != set(media_by_sha):
            raise PortableReviewProofError(
                "package_validation", "retained MP4 identity set is incomplete"
            )
        located_media.sort(key=lambda item: item["ordinal"])

        receipt_path = "package/proof_set_receipt.json"
        try:
            receipt = json.loads(archive.read(receipt_path))
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise PortableReviewProofError(
                "package_validation", "proof_set_receipt.json must be valid JSON"
            ) from exc
        if not isinstance(receipt, dict):
            raise PortableReviewProofError(
                "package_validation", "proof_set_receipt.json root must be an object"
            )
        receipt_artifact = receipt.get("artifact_id")
        if receipt_artifact is not None and receipt_artifact != expectation["artifact_id"]:
            raise PortableReviewProofError(
                "package_validation", "proof receipt artifact_id mismatch"
            )

        extracted_root: Path | None = None
        if extract_to is not None:
            extracted_root = _extract_package(
                archive=archive,
                package_infos=package_infos,
                expected_hashes=hashes,
                output_dir=extract_to,
            )

    review_entrypoint = (
        extracted_root / PurePosixPath(review_path) if extracted_root is not None else None
    )
    open_script = (
        extracted_root / "package" / "review" / "open_review.ps1"
        if extracted_root is not None
        else None
    )
    return {
        "state": "PORTABLE_REVIEW_PROOF_VERIFIED",
        "artifact_id": expectation["artifact_id"],
        "artifact_state": expectation["artifact_state"],
        "source_identity": expectation["source_identity"],
        "archive": archive_path,
        "archive_byte_size": archive_path.stat().st_size,
        "archive_sha256": outer["archive_sha256"],
        "package_file_count": len(package_infos),
        "package_manifest_path": manifest_path,
        "package_manifest_self_sha256": expectation["manifest"]["self_sha256"],
        "review_html_sha256": expectation["review_entrypoint"]["sha256"],
        "retained_media": located_media,
        "extracted_root": extracted_root,
        "review_entrypoint": review_entrypoint,
        "review_open_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            f"{_powershell_literal(open_script)}"
            if open_script is not None
            else None
        ),
        "review_server_restart_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            f"{_powershell_literal(open_script)} -NoOpen"
            if open_script is not None
            else None
        ),
        "semantic_winner_selected": False,
        "human_creative_acceptance": False,
        "production_acceptance": False,
        "public_or_publishing_acceptance": False,
    }


def _validate_handoff_contract(
    payload: dict[str, Any], *, artifact_id: str
) -> dict[str, Any]:
    stage = "handoff_contract_validation"
    if payload.get("schema_version") != HANDOFF_CONTRACT_SCHEMA:
        raise PortableReviewProofError(stage, "unsupported handoff contract schema")
    if payload.get("artifact_id") != artifact_id:
        raise PortableReviewProofError(stage, "handoff contract artifact_id mismatch")
    if payload.get("artifact_state") != "NON_ADOPTED_REVIEW_PROOF":
        raise PortableReviewProofError(
            stage, "handoff contract must retain NON_ADOPTED_REVIEW_PROOF"
        )
    minutes = payload.get("estimated_review_minutes")
    if not _is_int(minutes) or minutes <= 0 or minutes > 30:
        raise PortableReviewProofError(
            stage, "estimated_review_minutes must be between 1 and 30"
        )
    dimensions = payload.get("comparison_dimensions")
    required_dimensions = ("opening", "endpoint", "subtitle_behavior", "overall_winner")
    if not isinstance(dimensions, dict) or set(dimensions) != set(required_dimensions):
        raise PortableReviewProofError(
            stage, "opening, endpoint, subtitle_behavior, and overall_winner are required"
        )
    for key in required_dimensions:
        dimension = dimensions[key]
        if (
            not isinstance(dimension, dict)
            or not isinstance(dimension.get("question"), str)
            or not dimension["question"].strip()
            or not isinstance(dimension.get("checks"), list)
            or not dimension["checks"]
            or not all(
                isinstance(item, str) and item.strip() for item in dimension["checks"]
            )
        ):
            raise PortableReviewProofError(
                stage, f"comparison dimension is incomplete: {key}"
            )
    reply = payload.get("reply_contract")
    if not isinstance(reply, dict) or set(reply) != {"ACCEPT", "REPAIR", "REJECT"}:
        raise PortableReviewProofError(
            stage, "reply_contract must define ACCEPT, REPAIR, and REJECT"
        )
    if not all(isinstance(value, str) and value.strip() for value in reply.values()):
        raise PortableReviewProofError(stage, "reply_contract entries must be non-empty")
    transitions = payload.get("after_reply")
    if (
        not isinstance(transitions, dict)
        or set(transitions) != {"ACCEPT", "REPAIR", "REJECT"}
        or not all(
            isinstance(value, str) and value.strip() for value in transitions.values()
        )
    ):
        raise PortableReviewProofError(
            stage, "after_reply must define all three bounded transitions"
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _review_packet_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# ClipPipeGen exact four-way review packet",
        "",
        f"- artifact: `{packet['artifact_id']}`",
        f"- source: `{packet['source_identity']}`",
        f"- state: `{packet['artifact_state']}`",
        f"- estimated review time: {packet['estimated_review_minutes']} minutes",
        f"- reply destination: `{packet['reply_destination']}`",
        "- boundary: four exact proofs are verified but remain non-adopted; "
        "opening, endpoint, and winner are human-owned.",
        "",
        "## Open and compare",
        "",
        f"1. Run `{packet['review_open_command']}`.",
        "2. Play all four proofs once without selecting a winner.",
        "3. Recheck only the opening, the final endpoint, and subtitle behavior.",
        "4. Return one of the three reply forms below to the named Coordinator.",
        "",
        "## Exact retained proofs",
        "",
        "| Proof | Duration | Exact local path | SHA-256 |",
        "|---:|---:|---|---|",
    ]
    for item in packet["retained_media"]:
        lines.append(
            f"| {item['ordinal']} | {item['recorded_duration_seconds']:.3f}s | "
            f"`{item['local_path']}` | `{item['sha256']}` |"
        )
    lines.extend(["", "## Focused checks", ""])
    for key, dimension in packet["comparison_dimensions"].items():
        lines.append(f"### {key}")
        lines.append("")
        lines.append(dimension["question"])
        lines.append("")
        for check in dimension["checks"]:
            lines.append(f"- {check}")
        lines.append("")
    lines.extend(["## Minimal reply", ""])
    for disposition in ("ACCEPT", "REPAIR", "REJECT"):
        lines.append(f"- `{packet['reply_contract'][disposition]}`")
    lines.extend(["", "## After the reply", ""])
    for disposition in ("ACCEPT", "REPAIR", "REJECT"):
        lines.append(f"- **{disposition}:** {packet['after_reply'][disposition]}")
    lines.extend(
        [
            "",
            "Hashes, tests, and this packet establish identity and integrity "
            "only; they do not replace the viewing decision.",
            "",
        ]
    )
    return "\n".join(lines)


def write_portable_review_handoff(
    *,
    verification: dict[str, Any],
    contract_path: Path,
    output_dir: Path,
    reply_destination: str,
) -> dict[str, Any]:
    """Atomically write a Coordinator packet only after exact proof verification."""

    stage = "handoff_preflight"
    if verification.get("state") != "PORTABLE_REVIEW_PROOF_VERIFIED":
        raise PortableReviewProofError(stage, "exact proof verification is required")
    review_entrypoint = verification.get("review_entrypoint")
    open_command = verification.get("review_open_command")
    extracted_root = verification.get("extracted_root")
    if (
        not isinstance(review_entrypoint, Path)
        or not review_entrypoint.is_file()
        or not isinstance(extracted_root, Path)
        or not isinstance(open_command, str)
        or not open_command
    ):
        raise PortableReviewProofError(
            stage, "verified extraction and a direct review route are required"
        )
    if not isinstance(reply_destination, str) or not reply_destination.strip():
        raise PortableReviewProofError(stage, "reply_destination is required")
    contract = _validate_handoff_contract(
        _read_json(contract_path, stage="handoff_contract_validation"),
        artifact_id=verification["artifact_id"],
    )
    output_dir = output_dir.resolve(strict=False)
    if output_dir.exists():
        raise PortableReviewProofError(stage, "handoff output already exists")
    parent = output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    for candidate in (parent, *parent.parents):
        if candidate.exists() and _is_reparse_point(candidate):
            raise PortableReviewProofError(
                stage, f"handoff output parent is a reparse point: {candidate}"
            )

    retained_media: list[dict[str, Any]] = []
    for item in verification["retained_media"]:
        local_path = extracted_root.joinpath(*PurePosixPath(item["path"]).parts)
        if not local_path.is_file() or _sha256_file(local_path) != item["sha256"]:
            raise PortableReviewProofError(
                stage, f"verified retained proof is unavailable: {item['path']}"
            )
        retained_media.append({**item, "local_path": str(local_path)})
    packet = {
        "schema_version": HANDOFF_CONTRACT_SCHEMA,
        "state": "ACCEPTANCE_PACKET_READY",
        "acceptance_ready": True,
        "artifact_id": verification["artifact_id"],
        "artifact_state": verification["artifact_state"],
        "source_identity": verification["source_identity"],
        "review_entrypoint": str(review_entrypoint),
        "review_open_command": open_command,
        "review_server_restart_command": verification[
            "review_server_restart_command"
        ],
        "estimated_review_minutes": contract["estimated_review_minutes"],
        "retained_media": retained_media,
        "comparison_dimensions": contract["comparison_dimensions"],
        "reply_destination": reply_destination.strip(),
        "reply_contract": contract["reply_contract"],
        "after_reply": contract["after_reply"],
        "semantic_winner_selected": False,
        "human_creative_acceptance": False,
        "production_acceptance": False,
        "public_or_publishing_acceptance": False,
    }
    receipt = {
        "schema_version": "clippipegen.portable_review_verification_receipt.v1",
        "state": verification["state"],
        "artifact_id": verification["artifact_id"],
        "source_identity": verification["source_identity"],
        "archive_sha256": verification["archive_sha256"],
        "archive_byte_size": verification["archive_byte_size"],
        "package_file_count": verification["package_file_count"],
        "package_manifest_self_sha256": verification[
            "package_manifest_self_sha256"
        ],
        "review_html_sha256": verification["review_html_sha256"],
        "retained_media": retained_media,
        "acceptance_ready": True,
        "creative_acceptance_recorded": False,
    }

    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=parent))
    try:
        _write_json(temporary / "verification_receipt.json", receipt)
        _write_json(temporary / "coordinator_review_packet.json", packet)
        (temporary / "coordinator_review_packet.md").write_text(
            _review_packet_markdown(packet), encoding="utf-8"
        )
        os.replace(temporary, output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {
        "state": "PORTABLE_REVIEW_HANDOFF_WRITTEN",
        "output_dir": output_dir,
        "verification_receipt": output_dir / "verification_receipt.json",
        "coordinator_review_packet_json": output_dir
        / "coordinator_review_packet.json",
        "coordinator_review_packet_markdown": output_dir
        / "coordinator_review_packet.md",
        "reply_destination": reply_destination.strip(),
        "acceptance_ready": True,
    }
