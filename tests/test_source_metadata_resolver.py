from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.source_metadata_resolver import (
    SourceMetadataResolverError,
    resolve_episode_seed_sources,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CPD02_SEEDS = REPO_ROOT / "docs" / "content_planning" / "episode_seed_drafts.json"


def test_source_metadata_resolver_writes_resolution_json_html_and_template(tmp_path: Path):
    result = resolve_episode_seed_sources(
        input_path=CPD02_SEEDS,
        output_path=tmp_path / "episode_seed_source_resolution.json",
        dashboard_path=tmp_path / "source_resolution_dashboard.html",
        registry_path=tmp_path / "source_metadata_registry.json",
        registry_template_path=tmp_path / "source_metadata_registry.template.json",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    payload = json.loads(result["output_path"].read_text(encoding="utf-8"))
    template = json.loads(result["registry_template_path"].read_text(encoding="utf-8"))
    html = result["dashboard_path"].read_text(encoding="utf-8")

    assert payload["schema_id"] == "clippipegen.source_metadata_resolver.v0"
    assert payload["summary"]["record_count"] == 5
    assert payload["summary"]["resolved_source_url_count"] == 1
    assert payload["summary"]["source_url_missing_count"] == 4
    assert payload["summary"]["manual_intake_required_count"] == 4
    assert payload["gate_readback"]["network_required"] is False
    assert payload["gate_readback"]["external_api_used"] is False
    assert payload["gate_readback"]["media_downloaded"] is False
    assert payload["gate_readback"]["episode_dirs_created"] is False
    assert payload["gate_readback"]["rights_approved"] is False
    assert payload["gate_readback"]["public_use_permission"] is False

    records = {record["seed_id"]: record for record in payload["source_resolution_records"]}
    top = records["seed_cpd01_bancho_marine_misunderstanding"]
    assert top["source_url_state"] == "present"
    assert top["source_url_origin"] == "episode_seed_drafts"
    assert top["source_metadata_state"] == "resolved_from_seed_url"
    assert top["video_id"] == "7J5aS_pcBj4"
    assert top["source_media_state"] == "not_fetched"
    assert top["manual_intake_required"] is False
    assert top["rights_readback"]["approved"] is False
    assert top["approval_state"]["public_ready"] is False
    assert top["next_action"] == "ready_for_source_inspection_without_fetch"

    missing = records["seed_cpd01_jp_en_phrase_gap"]
    assert missing["source_url"] == ""
    assert missing["source_url_state"] == "missing"
    assert missing["confidence"] == "query_only"
    assert missing["manual_intake_required"] is True
    assert "source_url" in missing["manual_intake_fields_needed"]
    assert "日本語の一言" in missing["lookup_query"]

    assert template["schema_id"] == "clippipegen.source_metadata_registry.template.v0"
    assert template["entry_count"] == 4
    assert len(template["entries"]) == 4
    assert all(entry["source_url"] == "" for entry in template["entries"])
    assert "VIDEO_ID_PLACEHOLDER" not in json.dumps(template, ensure_ascii=False)

    assert "CPD-03 Source Metadata Resolver v0" in html
    assert "元動画URL状態" in html
    assert "検索query" in html
    assert "media_downloaded</th><td>false" in html
    assert "public_use_permission=false" in html


def test_source_metadata_resolver_uses_manual_registry_without_fetch(tmp_path: Path):
    registry_path = tmp_path / "source_metadata_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_id": "clippipegen.source_metadata_registry.v0",
                "entries": [
                    {
                        "seed_id": "seed_cpd01_jp_en_phrase_gap",
                        "candidate_id": "cpd01_jp_en_phrase_gap",
                        "source_url": "https://youtu.be/MANUAL12345A",
                        "source_title": "operator supplied source title",
                        "channel_name": "operator supplied channel",
                        "verification_status": "unverified",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = resolve_episode_seed_sources(
        input_path=CPD02_SEEDS,
        output_path=tmp_path / "episode_seed_source_resolution.json",
        dashboard_path=tmp_path / "source_resolution_dashboard.html",
        registry_path=registry_path,
        registry_template_path=tmp_path / "source_metadata_registry.template.json",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    payload = result["payload"]
    records = {record["seed_id"]: record for record in payload["source_resolution_records"]}
    manual = records["seed_cpd01_jp_en_phrase_gap"]

    assert payload["summary"]["resolved_source_url_count"] == 2
    assert payload["summary"]["source_url_missing_count"] == 3
    assert payload["summary"]["manual_intake_required_count"] == 3
    assert payload["summary"]["registry_entry_used_count"] == 1
    assert manual["source_url_state"] == "present"
    assert manual["source_url_origin"] == "manual_registry"
    assert manual["source_metadata_state"] == "resolved_from_manual_registry"
    assert manual["video_id"] == "MANUAL12345A"
    assert manual["manual_intake_required"] is False
    assert manual["source_media_state"] == "not_fetched"
    assert payload["gate_readback"]["network_required"] is False
    assert payload["gate_readback"]["media_downloaded"] is False


def test_source_metadata_resolver_rejects_missing_seed_array(tmp_path: Path):
    bad_input = tmp_path / "bad.json"
    bad_input.write_text('{"schema_id":"bad"}', encoding="utf-8")

    with pytest.raises(SourceMetadataResolverError, match="episode_seed_drafts"):
        resolve_episode_seed_sources(
            input_path=bad_input,
            output_path=tmp_path / "episode_seed_source_resolution.json",
            dashboard_path=tmp_path / "source_resolution_dashboard.html",
            registry_path=tmp_path / "source_metadata_registry.json",
            registry_template_path=tmp_path / "source_metadata_registry.template.json",
            base_dir=REPO_ROOT,
            generated_at="test-run",
        )


def test_resolve_episode_seed_sources_cli_writes_outputs(tmp_path: Path):
    output_path = tmp_path / "episode_seed_source_resolution.json"
    dashboard_path = tmp_path / "source_resolution_dashboard.html"
    template_path = tmp_path / "source_metadata_registry.template.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "resolve-episode-seed-sources",
            "--input",
            str(CPD02_SEEDS),
            "--output",
            str(output_path),
            "--dashboard",
            str(dashboard_path),
            "--registry",
            str(tmp_path / "source_metadata_registry.json"),
            "--registry-template",
            str(template_path),
            "--generated-at",
            "test-run",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["artifact_id"] == "clip-cpd03-source-metadata-resolver-v0-001"
    assert payload["record_count"] == 5
    assert payload["resolved_source_url_count"] == 1
    assert payload["source_url_missing_count"] == 4
    assert payload["manual_intake_required_count"] == 4
    assert payload["network_required"] is False
    assert payload["external_api_used"] is False
    assert payload["media_downloaded"] is False
    assert payload["episode_dirs_created"] is False
    assert payload["production_candidate"] is False
    assert payload["public_use_permission"] is False
    assert output_path.exists()
    assert dashboard_path.exists()
    assert template_path.exists()
