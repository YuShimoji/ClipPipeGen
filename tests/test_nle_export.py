"""ED-06: minimal NLE export tests."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from src.pipeline.edit_pack import build_skeleton, save_edit_pack
from src.pipeline.nle_export import export_csv_cut_list


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_export_csv_cut_list_keeps_source_audio_and_preview_warnings(tmp_path: Path):
    episode_dir, edit_pack_path = _episode_fixture(tmp_path)

    result = export_csv_cut_list(
        edit_pack_path=edit_pack_path,
        output_dir=episode_dir / "exports" / "ed06",
        base_dir=tmp_path,
    )

    csv_path = result["csv_path"]
    manifest_path = result["manifest_path"]
    report_path = result["report_path"]
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")

    assert len(rows) == 1
    assert rows[0]["cut_id"] == "cut_002"
    assert rows[0]["selected"] == "true"
    assert rows[0]["title"] == "strong punchline"
    assert rows[0]["start_seconds"] == "12.5"
    assert rows[0]["end_seconds"] == "20"
    assert rows[0]["subtitle_text"] == "ここを外部編集へ渡す"
    assert rows[0]["source_audio_provider"] == "yt-dlp"
    assert rows[0]["source_audio_mode"] == "yt-dlp-audio"
    assert rows[0]["source_url"] == "https://example.test/watch"
    assert rows[0]["source_audio_sha256"] == "abc123"
    assert rows[0]["production_edit_candidate"] == "false"
    assert "fixture transcript means exported cuts remain preview-only." in rows[0]["warnings"]

    assert manifest["format"] == "csv_cut_list_v1"
    assert manifest["production_edit_candidate"] is False
    assert manifest["summary"]["cut_rows"] == 1
    assert manifest["outputs"]["csv_cut_list"].endswith("exports/ed06/nle_cut_list.csv")
    assert manifest["outputs"]["readback_manifest"].endswith("exports/ed06/nle_export_manifest.json")
    assert manifest["outputs"]["readback_report"].endswith("exports/ed06/nle_export_report.html")
    assert manifest["source_refs"]["source_audio"]["provider"] == "yt-dlp"
    assert manifest["source_refs"]["source_audio"]["source_url"] == "https://example.test/watch"
    assert "preview transcript is not acceptance material." in manifest["warnings"]
    assert "ED-06 NLE Export Readback" in report
    assert "not production edit acceptance" in report
    assert "https://example.test/watch" in report
    assert "abc123" in report


def test_export_csv_cut_list_without_selected_cuts_exports_all_for_review(tmp_path: Path):
    episode_dir, edit_pack_path = _episode_fixture(tmp_path, selected=False)

    result = export_csv_cut_list(
        edit_pack_path=edit_pack_path,
        output_dir=episode_dir / "exports" / "ed06",
        base_dir=tmp_path,
    )

    rows = list(csv.DictReader(result["csv_path"].open("r", encoding="utf-8")))
    assert [row["cut_id"] for row in rows] == ["cut_001", "cut_002"]
    assert all(row["selected"] == "true" for row in rows)
    assert "selected_cut_ids is empty; exporting all cut candidates for review." in result["manifest"]["warnings"]


def test_cli_export_nle_json_readback(tmp_path: Path):
    episode_dir, edit_pack_path = _episode_fixture(tmp_path)
    output_dir = episode_dir / "exports" / "ed06_cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "export-nle",
            "--edit-pack",
            str(edit_pack_path),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["format"] == "csv_cut_list_v1"
    assert payload["cut_rows"] == 1
    assert payload["production_edit_candidate"] is False
    assert Path(payload["csv_cut_list"]).exists()
    assert Path(payload["manifest"]).exists()
    assert Path(payload["report"]).exists()


def _episode_fixture(tmp_path: Path, *, selected: bool = True) -> tuple[Path, Path]:
    episode_dir = tmp_path / "episodes" / "ep_ed06"
    episode_dir.mkdir(parents=True)
    edit_pack_path = episode_dir / "edit_pack.json"
    pack = build_skeleton(
        "ep_ed06",
        rights_manifest_path=str(episode_dir / "rights_manifest.json").replace("\\", "/"),
        material_ledger_path=str(episode_dir / "material_ledger.json").replace("\\", "/"),
    )
    pack["editing_intent"]["topic"] = "ED-06 minimal export"
    pack["cut_candidates"] = [
        {
            "id": "cut_001",
            "start_seconds": 0.0,
            "end_seconds": 8.0,
            "source": "auto",
            "reason": "setup",
            "confidence": 0.78,
            "source_segment_ids": ["seg_001"],
            "context_check": {"status": "passed", "notes": []},
        },
        {
            "id": "cut_002",
            "start_seconds": 12.5,
            "end_seconds": 20.0,
            "source": "auto",
            "reason": "strong punchline",
            "confidence": 0.91,
            "source_segment_ids": ["seg_002", "seg_003"],
            "context_check": {"status": "passed", "notes": []},
        },
    ]
    pack["selected_cut_ids"] = ["cut_002"] if selected else []
    pack["subtitles"] = [
        {
            "id": "sub_001",
            "cut_id": "cut_002",
            "start_seconds": 12.5,
            "end_seconds": 15.0,
            "text": "ここを外部編集へ渡す",
            "source": "auto",
            "style_slot": "subtitle.default",
        }
    ]
    save_edit_pack(pack, edit_pack_path)
    _write_preview_manifest(episode_dir)
    return episode_dir, edit_pack_path


def _write_preview_manifest(episode_dir: Path) -> None:
    material_dir = episode_dir / "materials" / "src_audio_fixture"
    material_dir.mkdir(parents=True)
    (episode_dir / "material_ledger.json").write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "episode_id": "ep_ed06",
                "materials": [
                    {
                        "id": "src_audio_fixture",
                        "kind": "source_audio",
                        "file_path": str(material_dir / "source.wav").replace("\\", "/"),
                        "sidecar_path": str(material_dir / "sidecar.json").replace("\\", "/"),
                        "hash_sha256": "abc123",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (episode_dir / "preview_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "episode_id": "ep_ed06",
                "material": {
                    "material_id": "src_audio_fixture",
                    "source_wav": str(material_dir / "source.wav").replace("\\", "/"),
                    "fetch_receipt": str(material_dir / "fetch_receipt.json").replace("\\", "/"),
                    "sidecar": str(material_dir / "sidecar.json").replace("\\", "/"),
                    "material_ledger": str(episode_dir / "material_ledger.json").replace("\\", "/"),
                    "ledger_entry": {
                        "id": "src_audio_fixture",
                        "kind": "source_audio",
                        "hash_sha256": "abc123",
                    },
                },
                "source_audio_provenance": {
                    "mode": "yt-dlp-audio",
                    "provider": "yt-dlp",
                    "source_url": "https://example.test/watch",
                    "output_sha256": "abc123",
                    "rights_status_at_fetch": "pending",
                    "rights_hard_gate": False,
                },
                "transcript": {
                    "source": "fixture",
                    "not_for_acceptance": True,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
