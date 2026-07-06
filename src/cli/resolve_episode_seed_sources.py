"""resolve-episode-seed-sources subcommand."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.source_metadata_resolver import (
    DEFAULT_ARTIFACT_ID,
    DEFAULT_DASHBOARD_FILENAME,
    DEFAULT_GENERATED_AT,
    DEFAULT_OUTPUT_FILENAME,
    DEFAULT_REGISTRY_FILENAME,
    DEFAULT_REGISTRY_TEMPLATE_FILENAME,
    SourceMetadataResolverError,
    resolve_episode_seed_sources,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="resolve-episode-seed-sources",
        description=(
            "Build CPD-03 source resolution records from CPD-02 episode seeds. "
            "This writes planning/review artifacts only; it does not fetch media, "
            "call public APIs, create episode folders, approve rights, render, "
            "thumbnail, or publish."
        ),
    )
    parser.add_argument(
        "--input",
        default="docs/content_planning/episode_seed_drafts.json",
        help="CPD-02 episode_seed_drafts.json path.",
    )
    parser.add_argument(
        "--output",
        default=f"docs/content_planning/{DEFAULT_OUTPUT_FILENAME}",
        help="Output source resolution JSON path.",
    )
    parser.add_argument(
        "--dashboard",
        default=f"docs/content_planning/{DEFAULT_DASHBOARD_FILENAME}",
        help="Output static HTML dashboard path.",
    )
    parser.add_argument(
        "--registry",
        default=f"docs/content_planning/{DEFAULT_REGISTRY_FILENAME}",
        help="Optional human-filled source metadata registry JSON.",
    )
    parser.add_argument(
        "--registry-template",
        default=f"docs/content_planning/{DEFAULT_REGISTRY_TEMPLATE_FILENAME}",
        help="Output manual source registry template JSON path.",
    )
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--artifact-id", default=DEFAULT_ARTIFACT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        result = resolve_episode_seed_sources(
            input_path=Path(args.input),
            output_path=Path(args.output),
            dashboard_path=Path(args.dashboard),
            registry_path=Path(args.registry),
            registry_template_path=Path(args.registry_template),
            base_dir=Path.cwd(),
            generated_at=args.generated_at,
            artifact_id=args.artifact_id,
        )
    except (OSError, SourceMetadataResolverError) as exc:
        print(f"resolve-episode-seed-sources failed: {exc}", file=sys.stderr)
        return 1

    summary = result["payload"]["summary"]
    gates = result["payload"]["gate_readback"]
    payload = {
        "schema_id": result["payload"]["schema_id"],
        "artifact_id": result["artifact_id"],
        "record_count": result["record_count"],
        "resolved_source_url_count": summary["resolved_source_url_count"],
        "source_url_missing_count": summary["source_url_missing_count"],
        "manual_intake_required_count": result["manual_intake_required_count"],
        "source_resolution_json": str(result["output_path"]).replace("\\", "/"),
        "dashboard_html": str(result["dashboard_path"]).replace("\\", "/"),
        "registry_template_json": str(result["registry_template_path"]).replace("\\", "/"),
        "network_required": gates["network_required"],
        "external_api_used": gates["external_api_used"],
        "media_downloaded": gates["media_downloaded"],
        "episode_dirs_created": gates["episode_dirs_created"],
        "production_candidate": gates["production_candidate"],
        "public_use_permission": gates["public_use_permission"],
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"schema_id: {payload['schema_id']}")
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"record_count: {payload['record_count']}")
        print(f"resolved_source_url_count: {payload['resolved_source_url_count']}")
        print(f"source_url_missing_count: {payload['source_url_missing_count']}")
        print(f"manual_intake_required_count: {payload['manual_intake_required_count']}")
        print(f"source_resolution_json: {payload['source_resolution_json']}")
        print(f"dashboard_html: {payload['dashboard_html']}")
        print(f"registry_template_json: {payload['registry_template_json']}")
        print(f"network_required: {str(payload['network_required']).lower()}")
        print(f"external_api_used: {str(payload['external_api_used']).lower()}")
        print(f"media_downloaded: {str(payload['media_downloaded']).lower()}")
        print(f"episode_dirs_created: {str(payload['episode_dirs_created']).lower()}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(f"public_use_permission: {str(payload['public_use_permission']).lower()}")
    return 0
