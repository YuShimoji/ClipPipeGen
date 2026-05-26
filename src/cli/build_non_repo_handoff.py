"""build-non-repo-handoff subcommand: local binary artifact handoff."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline.non_repo_artifact_handoff import (
    DEFAULT_HANDOFF_KIND,
    DEFAULT_GIT_POLICY,
    NonRepoArtifactHandoffError,
    build_non_repo_artifact_handoff,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-non-repo-handoff",
        description=(
            "Build machine-readable and human-readable handoff metadata for a local "
            "artifact that must not be committed to Git."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--artifact-path")
    parser.add_argument("--artifact-id")
    parser.add_argument("--artifact-kind", default=DEFAULT_HANDOFF_KIND)
    parser.add_argument("--git-policy", default=DEFAULT_GIT_POLICY)
    parser.add_argument("--generated-by-command")
    parser.add_argument("--render-manifest")
    parser.add_argument("--render-receipt")
    parser.add_argument("--render-report")
    parser.add_argument("--transcript")
    parser.add_argument("--edit-pack")
    parser.add_argument("--rights-manifest")
    parser.add_argument("--material-ledger")
    parser.add_argument("--nle-manifest")
    parser.add_argument("--output-dir")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    episode_dir = Path(args.episode_dir)
    render_manifest_path = Path(args.render_manifest) if args.render_manifest else None
    render_receipt_path = (
        Path(args.render_receipt)
        if args.render_receipt
        else render_manifest_path.parent / "render_receipt.json"
        if render_manifest_path
        else None
    )
    render_report_path = (
        Path(args.render_report)
        if args.render_report
        else render_manifest_path.parent / "render_report.html"
        if render_manifest_path
        else None
    )
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else episode_dir / "review" / "non_repo_artifact_handoff"
    )

    try:
        result = build_non_repo_artifact_handoff(
            episode_dir=episode_dir,
            artifact_path=Path(args.artifact_path) if args.artifact_path else None,
            artifact_id=args.artifact_id,
            artifact_kind=args.artifact_kind,
            git_policy=args.git_policy,
            generated_by_command=args.generated_by_command,
            render_manifest_path=render_manifest_path,
            render_receipt_path=render_receipt_path,
            render_report_path=render_report_path,
            transcript_path=Path(args.transcript) if args.transcript else None,
            edit_pack_path=Path(args.edit_pack) if args.edit_pack else None,
            rights_manifest_path=Path(args.rights_manifest) if args.rights_manifest else None,
            material_ledger_path=Path(args.material_ledger) if args.material_ledger else None,
            nle_manifest_path=Path(args.nle_manifest) if args.nle_manifest else None,
            output_dir=output_dir,
            base_dir=Path.cwd(),
        )
    except (OSError, json.JSONDecodeError, NonRepoArtifactHandoffError) as exc:
        print(f"build-non-repo-handoff failed: {exc}", file=sys.stderr)
        return 1

    manifest = result["manifest"]
    artifact = manifest["artifact"]
    boundary = manifest["boundary"]
    payload = {
        "schema_version": "v1",
        "episode_id": manifest["episode_id"],
        "artifact_id": manifest["artifact_id"],
        "artifact_kind": artifact["artifact_kind"],
        "exists": artifact["exists"],
        "size_bytes": artifact["size_bytes"],
        "sha256": artifact["sha256"],
        "git_policy": artifact["git_policy"],
        "production_candidate": boundary["production_candidate"],
        "rights_status": boundary["rights_status"],
        "transferable_by_git": manifest["handoff_status"]["transferable_by_git"],
        "manifest": str(result["manifest_path"]).replace("\\", "/"),
        "report": str(result["report_path"]).replace("\\", "/"),
    }
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"episode_id: {payload['episode_id']}")
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"artifact_kind: {payload['artifact_kind']}")
        print(f"exists: {str(payload['exists']).lower()}")
        print(f"size_bytes: {payload['size_bytes']}")
        print(f"sha256: {payload['sha256']}")
        print(f"git_policy: {payload['git_policy']}")
        print(f"production_candidate: {str(payload['production_candidate']).lower()}")
        print(f"rights_status: {payload['rights_status']}")
        print(f"transferable_by_git: {str(payload['transferable_by_git']).lower()}")
        print(f"manifest: {payload['manifest']}")
        print(f"report: {payload['report']}")
    return 0
