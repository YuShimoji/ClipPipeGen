from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EPISODE_ROOT = REPO_ROOT / "episodes/wiki_tensaku_family_20260804"
IR_PATH = REPO_ROOT / (
    "docs/content_planning/wiki_tensaku_content_reframe_v1/"
    "wiki_tensaku_content_reframe_v1.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / (
    "docs/content_planning/wiki_tensaku_ep1_integrated_rough_cut_v1"
)

WORK_ORDER_ID = "CPG-WIKI-EP1-INTEGRATED-ROUGH-CUT-001"
PREFLIGHT_ID = "clip-wiki-tensaku-ep1-integrated-rough-cut-preflight-v1-001"
PLANNED_ARTIFACT_ID = "clip-wiki-tensaku-ep1-integrated-rough-cut-v1-001"
EXPECTED_IR_SHA256 = "af502873b54786c5225236e1e47a4e0d38873da0ec4566ed7156ee5a8361288f"
BLOCKED_STATUS = "BLOCKED_EXACT_SOURCE_MEDIA_REQUIRED"
READY_STATUS = "READY_TO_RENDER"

PROBE_IDENTITIES = [
    (
        "clip-wiki-tensaku-family-turn-v1-001",
        21_800_858,
        "1f965e537d5a767d8cfe5c456ed0481ea88a119743f207ada9764bbc0ebe3284",
    ),
    (
        "clip-wiki-tensaku-family-turn-v2-001",
        19_951_636,
        "2736f6ec5b4a779a70c978d7815639802dee2d294220fdbb592edb9d75fe2dca",
    ),
    (
        "clip-wiki-tensaku-family-turn-v3-001",
        20_605_376,
        "5abfd8e940bd8a2709e79aced38ab2e0e56b7f052f3d205512e082d2a8f8733b",
    ),
    (
        "clip-wiki-tensaku-family-turn-v4-001",
        18_884_819,
        "5fea3d14e476871f239d1ab42283fedd83546daf98e8c5a27f625506ba69ca40",
    ),
    (
        "clip-wiki-tensaku-family-turn-v5-001",
        19_964_780,
        "e192fcd6746d396c0c92b5952c274cf5afd07f47c0f5d3a17deecd33b658012c",
    ),
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def verify_file(path: Path, expected_bytes: int, expected_sha256: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"required file is missing: {display_path(path)}")
    actual_bytes = path.stat().st_size
    actual_sha256 = sha256_file(path)
    if actual_bytes != expected_bytes:
        raise ValueError(
            f"byte size changed for {display_path(path)}: {actual_bytes} != {expected_bytes}"
        )
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"sha256 changed for {display_path(path)}: {actual_sha256} != {expected_sha256}"
        )
    return {
        "path": display_path(path),
        "bytes": actual_bytes,
        "sha256": actual_sha256,
        "mtime_utc": path.stat().st_mtime,
    }


def validate_supplied_media(
    *, source_id: str, media_path: Path, receipt_path: Path
) -> dict[str, Any]:
    if not media_path.is_file() or not receipt_path.is_file():
        return {
            "state": "missing_exact_media_and_or_binding_receipt",
            "media_path": display_path(media_path),
            "media_present": media_path.is_file(),
            "receipt_path": display_path(receipt_path),
            "receipt_present": receipt_path.is_file(),
            "sha256": None,
            "bytes": None,
        }

    receipt = load_json(receipt_path)
    if receipt.get("source_identity") != source_id:
        raise ValueError(f"supplied receipt source identity mismatch: {display_path(receipt_path)}")
    expected_bytes = receipt.get("source_byte_size")
    expected_sha256 = receipt.get("source_sha256")
    if not isinstance(expected_bytes, int) or not isinstance(expected_sha256, str):
        raise ValueError(f"supplied receipt lacks exact byte/hash binding: {display_path(receipt_path)}")
    verified = verify_file(media_path, expected_bytes, expected_sha256)
    return {
        "state": "exact_media_bound_by_local_acquisition_receipt",
        "media_path": verified["path"],
        "media_present": True,
        "receipt_path": display_path(receipt_path),
        "receipt_present": True,
        "sha256": verified["sha256"],
        "bytes": verified["bytes"],
    }


def verify_probes() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for artifact_id, expected_bytes, expected_sha256 in PROBE_IDENTITIES:
        path = EPISODE_ROOT / f"artifacts/{artifact_id}/final_video.mp4"
        verified = verify_file(path, expected_bytes, expected_sha256)
        results.append(
            {
                "artifact_id": artifact_id,
                "path": verified["path"],
                "bytes": verified["bytes"],
                "sha256": verified["sha256"],
                "mtime_epoch_seconds": verified["mtime_utc"],
                "preservation_status": "unchanged_exact_probe_evidence",
            }
        )
    return results


def build_preflight() -> dict[str, Any]:
    actual_ir_sha256 = sha256_file(IR_PATH)
    if actual_ir_sha256 != EXPECTED_IR_SHA256:
        raise ValueError(
            f"canonical IR identity changed: {actual_ir_sha256} != {EXPECTED_IR_SHA256}"
        )
    plan = load_json(IR_PATH)
    episodes = {item["episode_id"]: item for item in plan["episode_chapter_map"]}
    if "E1" not in episodes:
        raise ValueError("canonical IR lacks Episode E1")
    episode = episodes["E1"]
    if episode["clip_ids"] != ["CU-01", "CU-02", "CU-03"]:
        raise ValueError("Episode E1 ClipUnit order changed")

    clips = {item["clip_id"]: item for item in plan["narrative_assembly_ir"]["clip_units"]}
    sources = {item["source_id"]: item for item in plan["corpus_inventory"]["sources"]}
    mappings: list[dict[str, Any]] = []
    missing_dependencies: list[dict[str, Any]] = []

    for clip_id in episode["clip_ids"]:
        clip = clips[clip_id]
        source = sources[clip["source_id"]]
        caption_path = REPO_ROOT / source["captions"]["repo_relative_ignored_path"]
        caption = verify_file(
            caption_path,
            int(source["captions"]["bytes"]),
            source["captions"]["sha256"],
        )

        media = source["media"]
        if media["state"] == "exact_source_bytes_available":
            media_path = REPO_ROOT / media["repo_relative_ignored_path"]
            exact_media = verify_file(media_path, int(media["bytes"]), media["sha256"])
            media_resolution = {
                "state": "exact_media_ready",
                "media_path": exact_media["path"],
                "media_present": True,
                "receipt_path": (
                    f"episodes/wiki_tensaku_family_20260804/corpus/materials/"
                    f"{clip['source_id'].split(':', 1)[1]}/acquisition_receipt.json"
                ),
                "receipt_present": True,
                "bytes": exact_media["bytes"],
                "sha256": exact_media["sha256"],
            }
        else:
            video_id = clip["source_id"].split(":", 1)[1]
            media_path = EPISODE_ROOT / f"corpus/materials/{video_id}/source_video.mp4"
            receipt_path = EPISODE_ROOT / f"corpus/materials/{video_id}/acquisition_receipt.json"
            media_resolution = validate_supplied_media(
                source_id=clip["source_id"],
                media_path=media_path,
                receipt_path=receipt_path,
            )
            if media_resolution["state"] != "exact_media_bound_by_local_acquisition_receipt":
                missing_dependencies.append(
                    {
                        "dependency_id": f"{clip_id}-exact-source-media",
                        "clip_id": clip_id,
                        "source_id": clip["source_id"],
                        "required_range": clip["source_timestamp"],
                        "expected_media_path": display_path(media_path),
                        "expected_receipt_path": display_path(receipt_path),
                        "caption_only_evidence": caption,
                        "reason": (
                            "canonical ClipUnit requires source video, but only exact automatic caption bytes "
                            "are locally present"
                        ),
                        "prohibited_substitutions": [
                            "unrelated source fragment",
                            "old Turn 1-5 fixed 25-second cut",
                            "caption-only synthetic video",
                            "guessed or externally fetched media",
                        ],
                    }
                )

        mappings.append(
            {
                "chapter_number": clip["chapter_number"],
                "clip_id": clip_id,
                "chapter_title": clip["chapter_title"],
                "source_id": clip["source_id"],
                "source_timestamp": clip["source_timestamp"],
                "media_resolution": media_resolution,
                "caption_identity": caption,
                "setup": clip["setup"],
                "core_statement": clip["core_statement"],
                "payoff_or_conclusion": clip["payoff_or_conclusion"],
                "transition_in": clip["transition_in"],
                "transition_out": clip["transition_out"],
                "old_probe_reuse_policy": (
                    "support-only; never concatenate the old fixed cut; use only inside this "
                    "context-complete source range"
                ),
            }
        )

    status = BLOCKED_STATUS if missing_dependencies else READY_STATUS
    planned_source_seconds = sum(
        item["source_timestamp"]["requested_duration_seconds"] for item in mappings
    )
    probe_readback = verify_probes()

    return {
        "schema_version": "clippipegen.wiki_tensaku_ep1_integrated_preflight.v1",
        "work_order_id": WORK_ORDER_ID,
        "preflight_id": PREFLIGHT_ID,
        "planned_artifact_id": PLANNED_ARTIFACT_ID,
        "status": status,
        "s_verdict": {
            "verdict": "content_continue",
            "scope": "approved_for_production_entry_only",
            "human_artistic_acceptance": "pending_revise",
            "final_delivery_acceptance": "not_granted",
        },
        "acceptance_score": {
            "current_points": 82,
            "fixed_weight_total": 100,
            "s_content_review_points": 8,
            "integrated_render_points": 0,
            "technical_qa_points": 0,
            "final_content_acceptance_points": 0,
        },
        "canonical_ir": {
            "path": display_path(IR_PATH),
            "sha256": actual_ir_sha256,
            "artifact_id": plan["artifact_id"],
        },
        "episode": {
            "episode_id": episode["episode_id"],
            "title": episode["title"],
            "thesis": episode["thesis"],
            "viewer_question": episode["viewer_question"],
            "clip_ids": episode["clip_ids"],
            "planned_source_seconds": planned_source_seconds,
            "runtime_rule": (
                "continuous setup-through-payoff runtime determined by context-complete ranges and "
                "actual transitions; no arbitrary 300-second target"
            ),
        },
        "clipunit_source_map": mappings,
        "missing_dependency_count": len(missing_dependencies),
        "missing_dependencies": missing_dependencies,
        "render": {
            "performed": False,
            "output_path": None,
            "output_sha256": None,
            "output_bytes": None,
            "output_duration_seconds": None,
            "reason": (
                "mandatory exact-media preflight is blocked"
                if missing_dependencies
                else "preflight tool never renders; proceed with the integrated renderer"
            ),
        },
        "product_iteration": {
            "integrated_product_iteration_before": 0,
            "integrated_product_iteration_after": 0,
            "counts_as_integrated_product_iteration": False,
            "reason": "no continuous integrated MP4 exists",
        },
        "probe_preservation_readback": probe_readback,
        "resume_contract": {
            "required_dependency": (
                "exact locally supplied source bytes and exact acquisition receipt for "
                "youtube:Ocqg-RpQURY"
            ),
            "required_media_path": (
                "episodes/wiki_tensaku_family_20260804/corpus/materials/"
                "Ocqg-RpQURY/source_video.mp4"
            ),
            "required_receipt_path": (
                "episodes/wiki_tensaku_family_20260804/corpus/materials/"
                "Ocqg-RpQURY/acquisition_receipt.json"
            ),
            "receipt_requirements": [
                "source_identity equals youtube:Ocqg-RpQURY",
                "source_byte_size equals the supplied file size",
                "source_sha256 equals the supplied file SHA-256",
            ],
            "resume_command": (
                "uv run --no-project python scripts/"
                "preflight_wiki_tensaku_ep1_integrated_rough_cut.py"
            ),
            "ready_condition": "status becomes READY_TO_RENDER with all three ClipUnits exact-media-ready",
            "external_acquisition_authorized": False,
        },
        "next_s_event": {
            "current_state": "NOT_ROUTABLE_NO_INTEGRATED_MP4",
            "event": (
                "after exact source delivery, READY_TO_RENDER preflight, one continuous Episode 1 "
                "render, and technical QA, Coordinator routes the exact MP4 review packet to S"
            ),
            "required_packet_fields": [
                "artifact_id/path/SHA-256/bytes/duration/streams",
                "canonical IR SHA-256",
                "chapter/ClipUnit/source-time/transition/deviation map",
                "full A/V decode and continuity/black/silence evidence",
                "human_artistic_acceptance=pending_revise",
            ],
            "verdicts": [
                "content_accept",
                "content_bounded_repair",
                "content_reframe",
            ],
        },
        "boundaries": {
            "mp4_generated": False,
            "old_probe_modified": False,
            "external_fetch_attempted": False,
            "drive_upload_attempted": False,
            "rights_or_publication_inferred": False,
        },
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Wiki添削 Episode 1 integrated rough-cut preflight",
        "",
        f"Work Order: `{result['work_order_id']}`",
        "",
        f"Status: **{result['status']}**",
        "",
        "Sの`content_continue`はproduction entryだけを許可した。human artistic acceptanceと"
        "final delivery acceptanceは未付与。mandatory preflightでCU-02のexact source mediaが"
        "解決できないため、MP4は生成していない。",
        "",
        "## Episode 1 mapping",
        "",
        "| Chapter | ClipUnit | Source/time | Media | Content connection |",
        "|---:|---|---|---|---|",
    ]
    for item in result["clipunit_source_map"]:
        timestamp = item["source_timestamp"]
        lines.append(
            f"| {item['chapter_number']} | `{item['clip_id']}` {item['chapter_title']} | "
            f"`{item['source_id']}` {timestamp['requested_start_seconds']}–"
            f"{timestamp['requested_end_seconds']}s | {item['media_resolution']['state']} | "
            f"{item['payoff_or_conclusion']} → {item['transition_out']} |"
        )
    lines += [
        "",
        "## Exact blocker",
        "",
    ]
    for dependency in result["missing_dependencies"]:
        lines += [
            f"- `{dependency['clip_id']}` requires `{dependency['source_id']}` "
            f"{dependency['required_range']['requested_start_seconds']}–"
            f"{dependency['required_range']['requested_end_seconds']}s.",
            f"- Expected media: `{dependency['expected_media_path']}` (missing).",
            f"- Expected receipt: `{dependency['expected_receipt_path']}` (missing).",
            f"- Caption SHA-256: `{dependency['caption_only_evidence']['sha256']}` is present, "
            "but captions do not substitute for source video.",
        ]
    lines += [
        "",
        "## Resume",
        "",
        "Exact source bytes and a receipt binding source identity, byte size, and SHA-256 must be"
        " explicitly supplied at the recorded paths. This preflight performs no network acquisition.",
        "",
        f"Run: `{result['resume_contract']['resume_command']}`",
        "",
        "Only `READY_TO_RENDER` permits the integrated renderer. Until then,"
        " `integrated_product_iteration=0`, score `82/100`, and no S MP4 review packet exists.",
        "",
        "## Preserved probes",
        "",
    ]
    for probe in result["probe_preservation_readback"]:
        lines.append(
            f"- `{probe['artifact_id']}`: {probe['bytes']} bytes / SHA-256 `{probe['sha256']}`"
        )
    lines.append("")
    return "\n".join(lines)


def coordinator_packet(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "clippipegen.wiki_tensaku_ep1_coordinator_resume.v1",
        "work_order_id": result["work_order_id"],
        "preflight_id": result["preflight_id"],
        "planned_artifact_id": result["planned_artifact_id"],
        "status": result["status"],
        "canonical_ir": result["canonical_ir"],
        "episode": result["episode"],
        "missing_dependencies": result["missing_dependencies"],
        "render": result["render"],
        "product_iteration": result["product_iteration"],
        "acceptance_score": result["acceptance_score"],
        "resume_contract": result["resume_contract"],
        "next_s_event": result["next_s_event"],
        "content_status": "S_CONTENT_CONTINUE_BUT_RENDER_DEPENDENCY_BLOCKED",
        "technical_status": "PREFLIGHT_FAIL_CLOSED_NO_OUTPUT",
    }


def write_outputs(result: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "preflight_receipt.json": json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        "preflight_report.md": render_markdown(result),
        "coordinator_resume_packet.json": json.dumps(
            coordinator_packet(result), ensure_ascii=False, indent=2
        )
        + "\n",
    }
    for name, payload in payloads.items():
        (output_dir / name).write_text(payload, encoding="utf-8", newline="\n")

    canonical_dir = DEFAULT_OUTPUT_DIR
    members = []
    for name in payloads:
        path = output_dir / name
        members.append(
            {
                "path": display_path(canonical_dir / name),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    package = {
        "schema_version": "clippipegen.wiki_tensaku_ep1_preflight_package.v1",
        "work_order_id": WORK_ORDER_ID,
        "preflight_id": PREFLIGHT_ID,
        "status": result["status"],
        "members": members,
        "generated_mp4_count": 0,
    }
    (output_dir / "package_receipt.json").write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return package


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed exact-media preflight for Wiki添削 Episode 1"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--expect-status", choices=[BLOCKED_STATUS, READY_STATUS])
    args = parser.parse_args()

    result = build_preflight()
    if args.expect_status and result["status"] != args.expect_status:
        raise ValueError(f"unexpected preflight status: {result['status']}")

    if args.check:
        temp_dir = args.output_dir.parent / f".{args.output_dir.name}.check"
        if temp_dir.exists():
            raise ValueError(f"check directory already exists: {temp_dir}")
        write_outputs(result, temp_dir)
        names = {
            "preflight_receipt.json",
            "preflight_report.md",
            "coordinator_resume_packet.json",
            "package_receipt.json",
        }
        try:
            for name in names:
                if (temp_dir / name).read_bytes() != (args.output_dir / name).read_bytes():
                    raise ValueError(f"tracked output is stale: {name}")
        finally:
            for path in temp_dir.iterdir():
                path.unlink()
            temp_dir.rmdir()
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "missing_dependency_count": result["missing_dependency_count"],
                    "generated_mp4_count": 0,
                    "integrated_product_iteration_after": 0,
                },
                ensure_ascii=False,
            )
        )
        return 0

    package = write_outputs(result, args.output_dir)
    print(json.dumps(package, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
