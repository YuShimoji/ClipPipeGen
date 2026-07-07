from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.pipeline.external_source_registry import (
    ExternalSourceRegistryError,
    build_external_source_registry,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
RSS_FIXTURE = REPO_ROOT / "samples" / "external_sources" / "rss_fixture.xml"
MANUAL_SEEDS = REPO_ROOT / "samples" / "external_sources" / "manual_source_seeds.json"


def test_external_source_registry_normalizes_rss_and_manual_fixtures(tmp_path: Path):
    result = build_external_source_registry(
        rss_fixture_path=RSS_FIXTURE,
        manual_seeds_path=MANUAL_SEEDS,
        output_path=tmp_path / "external_source_registry.json",
        base_dir=REPO_ROOT,
        generated_at="test-run",
    )

    payload = json.loads(result["output_path"].read_text(encoding="utf-8"))

    assert payload["schema_id"] == "clippipegen.external_source_registry.v0"
    assert payload["artifact_id"] == "clip-hub01-external-source-registry-v0-001"
    assert payload["summary"]["record_count"] == 4
    assert payload["summary"]["rss_item_count"] == 2
    assert payload["summary"]["manual_seed_count"] == 2
    assert payload["summary"]["source_candidate_count"] == 3
    assert payload["summary"]["needs_review_count"] == 1
    assert payload["summary"]["network_used_count"] == 0
    assert payload["summary"]["media_downloaded_count"] == 0
    assert payload["summary"]["rights_approved_count"] == 0
    assert payload["summary"]["public_ready_count"] == 0

    gates = payload["gate_readback"]
    assert gates["network_required"] is False
    assert gates["network_used"] is False
    assert gates["external_api_used"] is False
    assert gates["source_urls_opened"] is False
    assert gates["media_downloaded"] is False
    assert gates["rights_approved"] is False
    assert gates["public_ready"] is False
    assert gates["production_ready"] is False

    records = {record["source_candidate_id"]: record for record in payload["external_source_records"]}
    rss = records["hub01_rss_hololive_sample_animation"]
    assert rss["source_kind"] == "rss_item"
    assert rss["source_url"] == "https://example.invalid/hololive-sample-animation-source"
    assert rss["channel_or_feed"] == "HUB-01 Local Fixture Feed"
    assert rss["source_confidence"] == "fixture_metadata_unverified"
    assert rss["candidate_state"] == "source_candidate"
    assert rss["provenance"] == "fixture"
    assert rss["network_used"] is False
    assert rss["media_downloaded"] is False
    assert rss["rights_approved"] is False
    assert rss["public_ready"] is False
    assert "sample-metadata" in rss["tags"]

    manual = records["hub_manual_jp_en_phrase_gap_seed"]
    assert manual["source_kind"] == "manual_seed"
    assert manual["source_url"] == ""
    assert manual["candidate_state"] == "needs_review"
    assert manual["provenance"] == "manual_seed"
    assert manual["next_local_action"] == "operator_source_review_required"


def test_external_source_registry_cli_writes_json(tmp_path: Path):
    output_path = tmp_path / "external_source_registry.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "build-external-source-registry",
            "--rss-fixture",
            str(RSS_FIXTURE),
            "--manual-seeds",
            str(MANUAL_SEEDS),
            "--output",
            str(output_path),
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
    cli_payload = json.loads(completed.stdout)
    assert cli_payload["artifact_id"] == "clip-hub01-external-source-registry-v0-001"
    assert cli_payload["record_count"] == 4
    assert cli_payload["rss_item_count"] == 2
    assert cli_payload["manual_seed_count"] == 2
    assert cli_payload["source_candidate_count"] == 3
    assert cli_payload["needs_review_count"] == 1
    assert cli_payload["network_used"] is False
    assert cli_payload["source_urls_opened"] is False
    assert cli_payload["media_downloaded"] is False
    assert cli_payload["rights_approved"] is False
    assert cli_payload["public_ready"] is False
    assert output_path.exists()


def test_external_source_registry_rejects_bad_rss(tmp_path: Path):
    bad_rss = tmp_path / "bad.xml"
    bad_rss.write_text("<rss><item></rss>", encoding="utf-8")

    with pytest.raises(ExternalSourceRegistryError, match="valid XML"):
        build_external_source_registry(
            rss_fixture_path=bad_rss,
            manual_seeds_path=MANUAL_SEEDS,
            output_path=tmp_path / "external_source_registry.json",
            base_dir=REPO_ROOT,
            generated_at="test-run",
        )
