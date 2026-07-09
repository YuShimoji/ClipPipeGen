"""build-external-source-registry subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.external_source_registry import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_GENERATED_AT,
    DEFAULT_MANUAL_SEEDS,
    DEFAULT_OUTPUT,
    DEFAULT_RSS_FIXTURE,
    ExternalSourceRegistryError,
    build_external_source_registry,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-external-source-registry",
        description=(
            "Normalize local RSS/manual fixtures into an offline source registry. "
            "This does not fetch network RSS, open source URLs, download media, "
            "call public APIs, approve rights, render, thumbnail, upload, or publish."
        ),
    )
    parser.add_argument(
        "--rss-fixture",
        default=str(DEFAULT_RSS_FIXTURE),
        help="Local RSS XML fixture path.",
    )
    parser.add_argument(
        "--manual-seeds",
        default=str(DEFAULT_MANUAL_SEEDS),
        help="Local manual source seeds JSON path.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output external source registry JSON path.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = build_external_source_registry(
            rss_fixture_path=Path(args.rss_fixture),
            manual_seeds_path=Path(args.manual_seeds),
            output_path=Path(args.output),
            base_dir=Path.cwd(),
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
        )
    except (OSError, ExternalSourceRegistryError) as exc:
        print(f"build-external-source-registry failed: {exc}", file=sys.stderr)
        return 1

    payload = result["payload"]
    summary = payload["summary"]
    gates = payload["gate_readback"]
    cli_payload = {
        "schema_id": payload["schema_id"],
        "artifact_id": result["artifact_id"],
        "record_count": result["record_count"],
        "rss_item_count": summary["rss_item_count"],
        "manual_seed_count": summary["manual_seed_count"],
        "source_candidate_count": summary["source_candidate_count"],
        "needs_review_count": summary["needs_review_count"],
        "external_source_registry_json": str(result["output_path"]).replace("\\", "/"),
        "network_used": gates["network_used"],
        "source_urls_opened": gates["source_urls_opened"],
        "media_downloaded": gates["media_downloaded"],
        "rights_approved": gates["rights_approved"],
        "public_ready": gates["public_ready"],
    }
    if args.format == "json":
        json.dump(cli_payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {cli_payload['schema_id']}")
        print(f"artifact_id: {cli_payload['artifact_id']}")
        print(f"record_count: {cli_payload['record_count']}")
        print(f"rss_item_count: {cli_payload['rss_item_count']}")
        print(f"manual_seed_count: {cli_payload['manual_seed_count']}")
        print(f"source_candidate_count: {cli_payload['source_candidate_count']}")
        print(f"needs_review_count: {cli_payload['needs_review_count']}")
        print(f"external_source_registry_json: {cli_payload['external_source_registry_json']}")
        print(f"network_used: {str(cli_payload['network_used']).lower()}")
        print(f"source_urls_opened: {str(cli_payload['source_urls_opened']).lower()}")
        print(f"media_downloaded: {str(cli_payload['media_downloaded']).lower()}")
        print(f"rights_approved: {str(cli_payload['rights_approved']).lower()}")
        print(f"public_ready: {str(cli_payload['public_ready']).lower()}")
    return 0
