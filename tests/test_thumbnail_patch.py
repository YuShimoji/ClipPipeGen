"""TH-01 / SH-01: thumbnail_patch + nlmytgen_bridge の最小テスト。

NLMYTGen subprocess は monkeypatch でモックする。
"""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path
from typing import Any

import pytest

from src.pipeline import nlmytgen_bridge as bridge
from src.pipeline import thumbnail_patch as tp
from src.pipeline.material_ledger import (
    build_skeleton as build_ledger_skeleton,
    compute_sha256,
    register_material,
)
from src.pipeline.material_sidecar import save_sidecar
from src.pipeline.rights_manifest import (
    build_skeleton as build_rights_skeleton,
    save_rights_manifest,
    set_compliance_status,
)


# --- helpers ---


def _make_png(color_type: int = 6) -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, color_type, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    raw = b"\x00" + b"\xff" * bpp
    compressed = zlib.compress(raw)
    idat_crc = zlib.crc32(b"IDAT" + compressed)
    idat = struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", idat_crc)
    iend_crc = zlib.crc32(b"IEND")
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)
    return sig + ihdr + idat + iend


def _passable_sidecar(asset_id: str, asset_path: str, asset_hash: str) -> dict:
    return {
        "schema_version": "v1",
        "asset_id": asset_id,
        "asset_path": asset_path,
        "asset_hash_sha256": asset_hash,
        "source": {
            "kind": "official_clip_permitted_source",
            "retrieved_at": "2026-05-06T11:00:00+09:00",
            "retrieved_by": "user:tester",
            "retrieval_method": "manual_screenshot",
        },
        "license": {
            "kind": "guideline_permitted",
            "guideline_url": "https://www.hololive.tv/terms",
            "guideline_version_checked_at": "2026-05-06",
        },
        "usage_conditions": ["credit_required"],
        "restrictions": {
            "thumbnail_use": "allowed",
            "commercial_use": "guideline_dependent",
            "modification": "allowed_minor_only",
            "redistribution": "denied",
        },
        "attribution_text": "© hololive production",
        "derived_from": None,
    }


def _build_passable_episode(tmp_path: Path, monkeypatch) -> dict[str, Path]:
    """rights_manifest (passed) + material_ledger (1 transparent png) + base ymmp 風ファイル を作る。

    register_material は cwd 基準で file_path を解決するので、tmp_path に chdir しておく。
    """
    monkeypatch.chdir(tmp_path)
    ep_dir = tmp_path / "episodes" / "ep_t1"
    ep_dir.mkdir(parents=True, exist_ok=True)

    # rights_manifest
    rights = build_rights_skeleton("ep_t1")
    rights["source_video"].update(
        url="https://www.youtube.com/watch?v=AAA",
        title="t",
        channel="c",
        channel_id="UC0001",
        vod_status="public",
    )
    rights["talents"] = [
        {
            "name": "Talent",
            "agency": "hololive",
            "guideline_url": "https://www.hololive.tv/terms",
            "guideline_version_checked_at": "2026-05-06",
        }
    ]
    rights = set_compliance_status(rights, status="passed", checked_by="user:tester")
    rights_path = ep_dir / "rights_manifest.json"
    save_rights_manifest(rights, rights_path)

    # material
    img = tmp_path / "materials" / "mat_001" / "x.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    img.write_bytes(_make_png(color_type=6))
    sc_path = tmp_path / "materials" / "mat_001" / "sidecar.json"
    save_sidecar(
        _passable_sidecar(
            "mat_001", "materials/mat_001/x.png", compute_sha256(img)
        ),
        sc_path,
    )
    ledger = build_ledger_skeleton("ep_t1")
    ledger = register_material(
        ledger,
        kind="character_image",
        subkind="transparent_png",
        file_path="materials/mat_001/x.png",
        sidecar_path="materials/mat_001/sidecar.json",
        intended_uses=["thumbnail"],
        registered_by="user:tester",
        rights_manifest_id="ep_t1",
        rights_status_at_registration="passed",
    )
    ledger_path = ep_dir / "material_ledger.json"
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")

    # base template (only path needs to exist; subprocess is mocked)
    base_ymmp = tmp_path / "templates" / "thumbnail" / "base.ymmp"
    base_ymmp.parent.mkdir(parents=True, exist_ok=True)
    base_ymmp.write_text("{}", encoding="utf-8")

    return {
        "tmp_path": tmp_path,
        "ep_dir": ep_dir,
        "rights_path": rights_path,
        "ledger_path": ledger_path,
        "base_ymmp": base_ymmp,
    }


def _passable_input(paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "episode_id": "ep_t1",
        "rights_manifest_path": "episodes/ep_t1/rights_manifest.json",
        "material_ledger_path": "episodes/ep_t1/material_ledger.json",
        "base_template": {
            "ymmp_path": "templates/thumbnail/base.ymmp",
            "template_version": "v1",
        },
        "slots": [
            {
                "slot_id": "thumb.text.title",
                "kind": "text",
                "value": "ぺこら、まさかの大爆笑事件",
                "source_material_id": None,
            },
            {
                "slot_id": "thumb.image.character",
                "kind": "image",
                "value": None,
                "source_material_id": "mat_001",
            },
        ],
        "output": {
            "ymmp_path": "episodes/ep_t1/thumbnail_patched.ymmp",
            "overwrite_existing": False,
        },
    }


# --- bridge ---


def test_bridge_config_missing_raises(tmp_path: Path):
    with pytest.raises(bridge.BridgeConfigError):
        bridge.BridgeConfig.load(tmp_path / "missing.json")


def test_bridge_config_invalid_root_raises(tmp_path: Path):
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(
        json.dumps({"nlmytgen_root": str(tmp_path / "no_such_dir"), "python_executable": "python"}),
        encoding="utf-8",
    )
    with pytest.raises(bridge.BridgeConfigError, match="does not exist"):
        bridge.BridgeConfig.load(cfg_path)


def test_call_nlmytgen_propagates_nonzero_exit(monkeypatch, tmp_path: Path):
    fake_root = tmp_path / "nlmytgen"
    (fake_root / "src" / "cli").mkdir(parents=True, exist_ok=True)
    (fake_root / "src" / "cli" / "main.py").write_text("# stub", encoding="utf-8")
    cfg = bridge.BridgeConfig(nlmytgen_root=fake_root, python_executable="python")

    class Result:
        returncode = 2
        stdout = ""
        stderr = "boom"

    monkeypatch.setattr(bridge.subprocess, "run", lambda *a, **kw: Result())
    with pytest.raises(bridge.BridgeExecutionError, match="exited with 2"):
        bridge.call_nlmytgen("audit-thumbnail-template", ["x.ymmp"], config=cfg)


# --- orchestrator ---


def _mock_bridge_for_success(monkeypatch, image_files: list[str]):
    """成功経路を再現する monkeypatch。"""

    def fake_audit(_path, *, config=None):
        return {
            "slot_count": 2,
            "slots": [
                {"kind": "text", "id": "title"},
                {"kind": "image", "id": "character"},
            ],
            "errors": [],
        }

    def fake_patch(_path, _payload, *, output_path, dry_run, config, work_dir):
        # NLMYTGen が書く想定の output ファイルを実際に作る（readback で存在を期待しないが安全）
        Path(output_path).write_text("{}", encoding="utf-8")
        return {
            "applied": True,
            "file_readback": [
                {"slot": "thumb.text.title", "match": True},
                {"slot": "thumb.image.character", "match": True, "applied_path": image_files[0]},
            ],
        }

    monkeypatch.setattr(tp.bridge, "audit_thumbnail_template", fake_audit)
    monkeypatch.setattr(tp.bridge, "patch_thumbnail_template", fake_patch)


def test_apply_thumbnail_patch_happy_path(monkeypatch, tmp_path: Path):
    paths = _build_passable_episode(tmp_path, monkeypatch)
    payload = _passable_input(paths)
    _mock_bridge_for_success(monkeypatch, [str(tmp_path / "materials/mat_001/x.png")])

    result = tp.apply_thumbnail_patch(
        payload,
        base_dir=tmp_path,
        config=bridge.BridgeConfig(
            nlmytgen_root=tmp_path, python_executable="python"
        ),
        work_dir=tmp_path / "_tmp" / "tp",
    )
    assert result["compliance_gate"]["status"] == "passed"
    assert result["material_validation"]["all_resolved"] is True
    assert result["audit_result"]["passed"] is True
    assert not result["patch_result"]["errors"]
    assert result["patch_result"]["output_ymmp_path"]
    # readback
    matches = [s["readback_match"] for s in result["patch_result"]["applied_slots"]]
    assert all(m is True for m in matches)


def test_apply_thumbnail_patch_blocks_when_compliance_pending(monkeypatch, tmp_path: Path):
    paths = _build_passable_episode(tmp_path, monkeypatch)
    # Down-grade compliance to pending
    rights = json.loads(paths["rights_path"].read_text(encoding="utf-8"))
    rights["compliance_check"]["status"] = "pending"
    paths["rights_path"].write_text(json.dumps(rights, ensure_ascii=False), encoding="utf-8")
    payload = _passable_input(paths)
    _mock_bridge_for_success(monkeypatch, [])

    result = tp.apply_thumbnail_patch(
        payload,
        base_dir=tmp_path,
        config=bridge.BridgeConfig(
            nlmytgen_root=tmp_path, python_executable="python"
        ),
        work_dir=tmp_path / "_tmp" / "tp",
    )
    assert result["compliance_gate"]["status"] == "failed"
    assert "COMPLIANCE_GATE_FAILED" in result["patch_result"]["errors"]


def test_apply_thumbnail_patch_blocks_when_thumbnail_use_denied(
    monkeypatch, tmp_path: Path
):
    paths = _build_passable_episode(tmp_path, monkeypatch)
    # Tamper sidecar to deny thumbnail_use
    sc_path = tmp_path / "materials/mat_001/sidecar.json"
    sc = json.loads(sc_path.read_text(encoding="utf-8"))
    sc["restrictions"]["thumbnail_use"] = "denied"
    sc_path.write_text(json.dumps(sc, ensure_ascii=False), encoding="utf-8")

    payload = _passable_input(paths)
    _mock_bridge_for_success(monkeypatch, [])

    result = tp.apply_thumbnail_patch(
        payload,
        base_dir=tmp_path,
        config=bridge.BridgeConfig(
            nlmytgen_root=tmp_path, python_executable="python"
        ),
        work_dir=tmp_path / "_tmp" / "tp",
    )
    assert result["compliance_gate"]["status"] == "passed"
    assert result["material_validation"]["all_resolved"] is False
    assert "MATERIAL_VALIDATION_FAILED" in result["patch_result"]["errors"]


def test_apply_thumbnail_patch_detects_missing_slot(monkeypatch, tmp_path: Path):
    paths = _build_passable_episode(tmp_path, monkeypatch)
    payload = _passable_input(paths)

    def fake_audit(_path, *, config=None):
        # only title exists; character is missing
        return {"slot_count": 1, "slots": [{"kind": "text", "id": "title"}], "errors": []}

    monkeypatch.setattr(tp.bridge, "audit_thumbnail_template", fake_audit)

    result = tp.apply_thumbnail_patch(
        payload,
        base_dir=tmp_path,
        config=bridge.BridgeConfig(
            nlmytgen_root=tmp_path, python_executable="python"
        ),
        work_dir=tmp_path / "_tmp" / "tp",
    )
    assert result["audit_result"]["passed"] is False
    assert "thumb.image.character" in result["audit_result"]["missing_slots"]
    assert "BRIDGE_AUDIT_MISSING_SLOTS" in result["patch_result"]["errors"]


def test_input_validator_rejects_bad_slot_id(tmp_path: Path):
    payload = {
        "schema_version": "v1",
        "episode_id": "ep_t1",
        "rights_manifest_path": "x.json",
        "material_ledger_path": "y.json",
        "base_template": {"ymmp_path": "b.ymmp"},
        "slots": [{"slot_id": "bad", "kind": "text", "value": "v"}],
        "output": {"ymmp_path": "out.ymmp"},
    }
    issues = tp.validate_thumbnail_patch_input(payload)
    assert any(i.code == "THUMB_SLOT_ID_INVALID" for i in issues)
