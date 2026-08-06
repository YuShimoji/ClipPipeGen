from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs/content_planning/wiki_tensaku_ep1_integrated_rough_cut_v1"
PREFLIGHT_PATH = OUTPUT_DIR / "preflight_receipt.json"
PACKAGE_PATH = OUTPUT_DIR / "package_receipt.json"
COORDINATOR_PATH = OUTPUT_DIR / "coordinator_resume_packet.json"
SCRIPT_PATH = REPO_ROOT / "scripts/preflight_wiki_tensaku_ep1_integrated_rough_cut.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_preflight_stops_on_exact_cu02_media_dependency() -> None:
    result = _load(PREFLIGHT_PATH)

    assert result["work_order_id"] == "CPG-WIKI-EP1-INTEGRATED-ROUGH-CUT-001"
    assert result["status"] == "BLOCKED_EXACT_SOURCE_MEDIA_REQUIRED"
    assert result["canonical_ir"]["sha256"] == (
        "af502873b54786c5225236e1e47a4e0d38873da0ec4566ed7156ee5a8361288f"
    )
    assert result["episode"]["episode_id"] == "E1"
    assert result["episode"]["clip_ids"] == ["CU-01", "CU-02", "CU-03"]
    assert result["episode"]["planned_source_seconds"] == 690

    mappings = result["clipunit_source_map"]
    assert [item["clip_id"] for item in mappings] == ["CU-01", "CU-02", "CU-03"]
    assert mappings[0]["media_resolution"]["state"] == "exact_media_ready"
    assert mappings[2]["media_resolution"]["state"] == "exact_media_ready"
    assert mappings[1]["media_resolution"]["state"] == (
        "missing_exact_media_and_or_binding_receipt"
    )
    assert mappings[1]["source_id"] == "youtube:Ocqg-RpQURY"
    assert mappings[1]["source_timestamp"]["requested_start_seconds"] == 390
    assert mappings[1]["source_timestamp"]["requested_end_seconds"] == 585

    assert result["missing_dependency_count"] == 1
    dependency = result["missing_dependencies"][0]
    assert dependency["clip_id"] == "CU-02"
    assert dependency["caption_only_evidence"]["sha256"] == (
        "a383ad8a545fe9a24da142dace96fe19f05bf834a03e1e52616a5332db3c3992"
    )
    assert dependency["expected_media_path"].endswith(
        "corpus/materials/Ocqg-RpQURY/source_video.mp4"
    )
    assert dependency["expected_receipt_path"].endswith(
        "corpus/materials/Ocqg-RpQURY/acquisition_receipt.json"
    )


def test_blocked_preflight_does_not_inflate_product_or_acceptance() -> None:
    result = _load(PREFLIGHT_PATH)

    assert result["s_verdict"]["verdict"] == "content_continue"
    assert result["s_verdict"]["scope"] == "approved_for_production_entry_only"
    assert result["s_verdict"]["human_artistic_acceptance"] == "pending_revise"
    assert result["acceptance_score"]["current_points"] == 82
    assert result["acceptance_score"]["integrated_render_points"] == 0
    assert result["acceptance_score"]["technical_qa_points"] == 0
    assert result["acceptance_score"]["final_content_acceptance_points"] == 0
    assert result["render"]["performed"] is False
    assert result["render"]["output_path"] is None
    assert result["product_iteration"]["integrated_product_iteration_after"] == 0
    assert result["product_iteration"]["counts_as_integrated_product_iteration"] is False
    assert result["boundaries"]["mp4_generated"] is False
    assert result["boundaries"]["external_fetch_attempted"] is False
    assert result["boundaries"]["drive_upload_attempted"] is False

    assert len(result["probe_preservation_readback"]) == 5
    assert all(
        item["preservation_status"] == "unchanged_exact_probe_evidence"
        for item in result["probe_preservation_readback"]
    )


def test_package_binds_portable_blocker_evidence_and_no_mp4() -> None:
    package = _load(PACKAGE_PATH)
    assert package["status"] == "BLOCKED_EXACT_SOURCE_MEDIA_REQUIRED"
    assert package["generated_mp4_count"] == 0
    assert len(package["members"]) == 3
    for member in package["members"]:
        path = REPO_ROOT / member["path"]
        assert path.stat().st_size == member["bytes"]
        assert _sha256(path) == member["sha256"]
    assert not list(OUTPUT_DIR.glob("*.mp4"))

    coordinator = _load(COORDINATOR_PATH)
    assert coordinator["technical_status"] == "PREFLIGHT_FAIL_CLOSED_NO_OUTPUT"
    assert coordinator["content_status"] == "S_CONTENT_CONTINUE_BUT_RENDER_DEPENDENCY_BLOCKED"
    assert coordinator["next_s_event"]["current_state"] == "NOT_ROUTABLE_NO_INTEGRATED_MP4"


def test_local_receipt_can_unlock_the_missing_source_without_network(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("ep1_preflight", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    media = tmp_path / "source_video.mp4"
    receipt = tmp_path / "acquisition_receipt.json"
    payload = b"exact-local-test-media"
    media.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    receipt.write_text(
        json.dumps(
            {
                "source_identity": "youtube:Ocqg-RpQURY",
                "source_byte_size": len(payload),
                "source_sha256": digest,
            }
        ),
        encoding="utf-8",
    )

    result = module.validate_supplied_media(
        source_id="youtube:Ocqg-RpQURY",
        media_path=media,
        receipt_path=receipt,
    )
    assert result["state"] == "exact_media_bound_by_local_acquisition_receipt"
    assert result["bytes"] == len(payload)
    assert result["sha256"] == digest
