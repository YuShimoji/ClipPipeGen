"""reconstitute-out07-review subcommand."""

from __future__ import annotations

import argparse
import json
import sys

from src.integrations.render.out07_reconstitution import (
    Out07ReconstitutionError,
    reconstitute_out07_review,
)


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="reconstitute-out07-review",
        description=(
            "Qualify the current episode media revision and rebuild one baseline-first "
            "OUT-07 poster review package without historical predecessor binaries."
        ),
    )
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--reference-corpus", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--baseline-output-dir")
    parser.add_argument("--reference-cache-dir")
    parser.add_argument("--fetch-missing-references", action="store_true")
    parser.add_argument("--verify-determinism", action="store_true")
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = reconstitute_out07_review(
            episode_dir=args.episode_dir,
            reference_corpus_path=args.reference_corpus,
            output_dir=args.output_dir,
            baseline_output_dir=args.baseline_output_dir,
            reference_cache_dir=args.reference_cache_dir,
            fetch_missing_references=args.fetch_missing_references,
            verify_determinism=args.verify_determinism,
            ffmpeg_path=args.ffmpeg_path,
            ffprobe_path=args.ffprobe_path,
        )
    except Out07ReconstitutionError as exc:
        print(f"reconstitute-out07-review failed: {exc}", file=sys.stderr)
        return 1
    payload = {
        "artifact_id": result["artifact_id"],
        "state": result["state"],
        "output_dir": str(result["output_dir"]),
        "index_path": str(result["index_path"]),
        "readback_path": str(result["readback_path"]),
        "manifest_path": str(result["manifest_path"]),
        "deterministic_core_digest": result["deterministic_core_digest"],
        "reference_evidence_digest": result["reference_evidence_digest"],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"artifact_id: {payload['artifact_id']}")
        print(f"state: {payload['state']}")
        print(f"review: {payload['index_path']}")
        print(f"deterministic_core_digest: {payload['deterministic_core_digest']}")
        print(f"reference_evidence_digest: {payload['reference_evidence_digest']}")
    return 0
