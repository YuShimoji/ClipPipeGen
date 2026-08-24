from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ARTIFACT_ID = "clip-wiki-selected-opening-current-basis-v1-001"
PARENT_ARTIFACT_ID = "clip-wiki-cu04-subtitle-timing-measurement-repair-v1-001"
SOURCE_IDENTITY = "youtube:1AcId5Yja10"
SOURCE_IN_SECONDS = 2530.319
SOURCE_OUT_SECONDS = 2865.599
OUTPUT_DURATION_SECONDS = 335.28

SOURCE_VIDEO_RELATIVE = Path(
    "episodes/wiki_tensaku_family_20260804/corpus/materials/"
    "1AcId5Yja10/source_video.mp4"
)
SOURCE_CAPTION_RELATIVE = Path(
    "episodes/wiki_tensaku_family_20260804/corpus/captions/1AcId5Yja10.ja.json3"
)
PARENT_PACKAGE_RELATIVE = Path(
    "episodes/integrated_checklist_reverse_test_20260811/artifacts/"
    "cpg-integrated-checklist-reverse-test-v1/successors/"
    "cpg-cu04-subtitle-timing-measurement-repair-v1/package"
)
DEFAULT_OUTPUT_RELATIVE = Path(
    "episodes/integrated_checklist_reverse_test_20260811/artifacts/"
    "cpg-integrated-checklist-reverse-test-v1/successors/"
    "cpg-wiki-selected-opening-current-basis-v1/package"
)

EXPECTED_SHA256 = {
    "source_video": "a994228674d0a6756f8747cf6a07b2cc4c4601fdbf98d5ca0bea3ee2f32060e7",
    "source_caption": "f58c248f23b29845a94ae01b789f122c8759687125375a2650cc7a8074107e4f",
    "parent_video": "bd5956f17ef6c552542b7475e23b87c50c804378f3df864f3de53cb07f0ad272",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def verify_inputs(repo_root: Path) -> dict:
    source_video = repo_root / SOURCE_VIDEO_RELATIVE
    source_caption = repo_root / SOURCE_CAPTION_RELATIVE
    parent = repo_root / PARENT_PACKAGE_RELATIVE
    parent_video = parent / "final_video.mp4"
    for path in (source_video, source_caption, parent_video):
        if not path.is_file():
            raise RuntimeError(f"required exact input is missing: {path}")

    observed = {
        "source_video": sha256(source_video),
        "source_caption": sha256(source_caption),
        "parent_video": sha256(parent_video),
    }
    for key, expected in EXPECTED_SHA256.items():
        if observed[key] != expected:
            raise RuntimeError(
                f"exact input hash mismatch for {key}: "
                f"expected={expected} observed={observed[key]}"
            )

    parent_receipt = load_json(parent / "artifact_receipt.json")
    parent_timeline = load_json(parent / "timeline_ir.json")
    caption_readback = load_json(parent / "caption_readback.json")
    if parent_receipt["artifact_id"] != PARENT_ARTIFACT_ID:
        raise RuntimeError("parent artifact identity mismatch")
    if parent_timeline["source_identity"] != SOURCE_IDENTITY:
        raise RuntimeError("parent source identity mismatch")
    if parent_timeline["cuts"][0]["source_in_seconds"] != SOURCE_IN_SECONDS:
        raise RuntimeError("selected opening is not the current parent entry")

    by_event = {item["provider_event_id"]: item for item in caption_readback["items"]}
    closing = by_event.get("event_001639")
    next_topic = by_event.get("event_001641")
    if not closing or not next_topic:
        raise RuntimeError("required endpoint caption evidence is missing")
    if closing["source_end_seconds"] != SOURCE_OUT_SECONDS:
        raise RuntimeError("event_001639 effective display end mismatch")
    if next_topic["source_start_seconds"] != SOURCE_OUT_SECONDS:
        raise RuntimeError("event_001641 next-topic onset mismatch")
    if closing["provider_source_end_seconds"] <= SOURCE_OUT_SECONDS:
        raise RuntimeError("expected rolling provider overlap is absent")
    if closing["adjustment"] != "previous_display_closed_at_next_provider_cue_start":
        raise RuntimeError("rolling overlap normalization contract mismatch")

    return {
        "source_video": source_video,
        "source_caption": source_caption,
        "parent": parent,
        "parent_video": parent_video,
        "parent_receipt": parent_receipt,
        "parent_timeline": parent_timeline,
        "caption_readback": caption_readback,
        "observed_sha256": observed,
        "closing_caption": closing,
        "next_topic_caption": next_topic,
    }


def build_successor_timeline(parent_timeline: dict) -> dict:
    timeline = deepcopy(parent_timeline)
    timeline["artifact_id"] = ARTIFACT_ID
    timeline["requested_target_duration_seconds"] = OUTPUT_DURATION_SECONDS
    timeline["output_duration_seconds"] = OUTPUT_DURATION_SECONDS
    timeline["selection_mode"] = (
        "selected_opening_continuous_source_range_with_provider_overlap_excised"
    )
    timeline["causal_order_note"] = (
        "Chronology is preserved. The user selected the existing 2530.319 opening. "
        "The endpoint follows the normalized next-provider-cue boundary; it does not "
        "treat provider rolling duration as proof of semantic completion."
    )
    timeline["endpoint_extension_seconds"] = 0.0
    final_cut = timeline["cuts"][-1]
    final_cut["source_out_seconds"] = SOURCE_OUT_SECONDS
    final_cut["output_out_seconds"] = OUTPUT_DURATION_SECONDS
    final_cut["duration_seconds"] = round(
        SOURCE_OUT_SECONDS - final_cut["source_in_seconds"], 3
    )
    final_cut["selection_reason"] = (
        "End at the normalized start of the next provider cue. Provider rolling "
        "duration is retained as technical provenance only, not promoted to a "
        "semantic-completion claim."
    )
    final_cut["continuity_context"] = (
        "event_001639 is displayed through 2865.599; event_001641 begins at the "
        "same source time and belongs to the next listed topic."
    )
    return timeline


def reconcile_successor_caption_contract(
    timeline: dict, caption_readback: dict, *, endpoint_seconds: float
) -> tuple[dict, dict]:
    """Return internally consistent timeline/caption readback copies.

    The parent package can contain display-only or zero-duration cue references that
    disappear when the successor endpoint is shortened.  A successor must derive all
    cue counts and navigation references from the retained item set instead of carrying
    the parent's aggregate counters forward.
    """

    reconciled_timeline = deepcopy(timeline)
    reconciled_readback = deepcopy(caption_readback)
    retained = [
        item
        for item in reconciled_readback["items"]
        if item["output_start_seconds"] < endpoint_seconds
    ]
    retained_ids = {item["caption_id"] for item in retained}

    reconciled_readback["items"] = retained
    reconciled_readback["cue_count"] = len(retained)
    reconciled_readback["provider_event_count_in_range"] = len(retained)
    reconciled_readback["successor_endpoint_seconds"] = endpoint_seconds
    reconciled_readback["excluded_next_topic_event_id"] = "event_001641"

    authority = reconciled_readback.get("authority")
    if isinstance(authority, dict):
        authority["display_cue_count"] = len(retained)
        authority["provider_event_count_in_range"] = len(retained)
    resolution = reconciled_readback.get("rolling_overlap_resolution")
    if isinstance(resolution, dict):
        resolution["cue_count"] = len(retained)
        resolution["provider_event_count_in_range"] = len(retained)

    for cut in reconciled_timeline["cuts"]:
        cut["caption_ids"] = [
            caption_id
            for caption_id in cut.get("caption_ids", [])
            if caption_id in retained_ids
        ]

    referenced_ids = {
        caption_id
        for cut in reconciled_timeline["cuts"]
        for caption_id in cut.get("caption_ids", [])
    }
    if referenced_ids != retained_ids:
        missing = sorted(retained_ids - referenced_ids)
        dangling = sorted(referenced_ids - retained_ids)
        raise RuntimeError(
            "successor caption contract mismatch: "
            f"missing={missing} dangling={dangling}"
        )
    return reconciled_timeline, reconciled_readback


def trimmed_ass(parent_ass: Path) -> str:
    lines = parent_ass.read_text(encoding="utf-8-sig").splitlines()
    retained = [
        line
        for line in lines
        if not (
            line.startswith("Dialogue:") and "うん他なんかないの乳首を国境は" in line
        )
    ]
    if len(retained) != len(lines) - 1:
        raise RuntimeError("expected exactly one next-topic subtitle cue to be excised")
    return "\n".join(retained) + "\n"


def run_checked(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def probe_media(ffprobe: str, video_path: Path) -> dict:
    completed = run_checked(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_type,codec_name,width,height,start_time,duration",
            "-of",
            "json",
            str(video_path),
        ]
    )
    return json.loads(completed.stdout)


def build(*, repo_root: Path, output_dir: Path, ffmpeg: str, ffprobe: str) -> dict:
    evidence = verify_inputs(repo_root)
    if output_dir.exists():
        raise RuntimeError(f"successor output already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    started = time.monotonic()
    try:
        output_video = output_dir / "final_video.mp4"
        run_checked(
            [
                ffmpeg,
                "-hide_banner",
                "-v",
                "error",
                "-nostdin",
                "-y",
                "-i",
                str(evidence["parent_video"]),
                "-t",
                f"{OUTPUT_DURATION_SECONDS:.3f}",
                "-map",
                "0:v:0",
                "-map",
                "0:a:0",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(output_video),
            ]
        )
        run_checked([ffmpeg, "-v", "error", "-i", str(output_video), "-f", "null", "-"])
        media = probe_media(ffprobe, output_video)
        duration = float(media["format"]["duration"])
        if abs(duration - OUTPUT_DURATION_SECONDS) > 0.1:
            raise RuntimeError(
                f"rendered duration mismatch: expected={OUTPUT_DURATION_SECONDS} observed={duration}"
            )

        timeline = build_successor_timeline(evidence["parent_timeline"])
        timeline, caption_readback = reconcile_successor_caption_contract(
            timeline,
            evidence["caption_readback"],
            endpoint_seconds=OUTPUT_DURATION_SECONDS,
        )
        write_json(output_dir / "timeline_ir.json", timeline)
        (output_dir / "editorial_subtitles.ass").write_text(
            trimmed_ass(evidence["parent"] / "editorial_subtitles.ass"),
            encoding="utf-8",
        )

        write_json(output_dir / "caption_readback.json", caption_readback)

        elapsed = round(time.monotonic() - started, 3)
        output_sha = sha256(output_video)
        source_used = round(SOURCE_OUT_SECONDS - SOURCE_IN_SECONDS, 3)
        receipt = {
            "schema_version": "clippipegen.wiki_selected_opening_successor.receipt.v1",
            "artifact_id": ARTIFACT_ID,
            "parent_artifact_id": PARENT_ARTIFACT_ID,
            "status": "INTERNAL_CANDIDATE_TECHNICALLY_COMPLETE_HUMAN_CONTENT_REVIEW_PENDING",
            "built_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision_authority": {
                "choice_set_id": 4,
                "choice_revision": 2,
                "selected_option_position": 2,
                "selected_option_title": "話題が切り替わるところから始める",
                "selected_at_utc": "2026-08-23T17:10:16Z",
                "actor": "User",
                "consumed_as": {
                    "source_start_seconds": SOURCE_IN_SECONDS,
                    "output_start_seconds": 0.0,
                },
            },
            "source": {
                "identity": SOURCE_IDENTITY,
                "media_path": SOURCE_VIDEO_RELATIVE.as_posix(),
                "media_sha256": evidence["observed_sha256"]["source_video"],
                "caption_path": SOURCE_CAPTION_RELATIVE.as_posix(),
                "caption_sha256": evidence["observed_sha256"]["source_caption"],
                "network_fetch_performed": False,
            },
            "candidate": {
                "source_range_seconds": [SOURCE_IN_SECONDS, SOURCE_OUT_SECONDS],
                "duration_seconds": OUTPUT_DURATION_SECONDS,
                "chronology_preserved": True,
                "source_gap_seconds": 0.0,
                "actual_edit_cut_count": 1,
                "navigation_partition_count": len(timeline["cuts"]),
                "output_path": output_video.relative_to(repo_root).as_posix(),
                "output_sha256": output_sha,
                "output_bytes": output_video.stat().st_size,
                "media_readback": media,
                "full_decode_passed": True,
            },
            "separate_audits": {
                "opening": {
                    "status": "user_selected_and_consumed",
                    "result": "existing parent already begins at 2530.319",
                },
                "subtitle_continuity": {
                    "status": "passed_deterministic_mapping_readback",
                    "retained_cue_count": len(caption_readback["items"]),
                    "last_retained_event_id": "event_001639",
                    "next_topic_event_excluded": "event_001641",
                },
                "topic_boundary": {
                    "status": "current_basis_corrected",
                    "boundary_source_seconds": SOURCE_OUT_SECONDS,
                    "next_topic_provider_event_id": "event_001641",
                    "semantic_audio_completion_inferred_from_provider_duration": False,
                },
                "endpoint": {
                    "status": "provider_rolling_overlap_excised",
                    "old_source_out_seconds": 2868.44,
                    "new_source_out_seconds": SOURCE_OUT_SECONDS,
                    "excised_seconds": 2.841,
                    "provider_duration_retained_as": "technical_provenance_only",
                },
                "retained_source_usage": {
                    "status": "exact_hash_verified",
                    "source_count": 1,
                    "used_source_seconds": source_used,
                    "available_source_seconds": 5557.812245,
                    "use_ratio": round(source_used / 5557.812245, 6),
                    "missing_Ocqg_RpQURY_lane_used": False,
                },
            },
            "observed_work": {
                "materialization_run_count": 1,
                "endpoint_contract_repair_count": 1,
                "render_corrective_retry_count": 0,
                "elapsed_seconds": elapsed,
            },
            "boundaries": {
                "human_content_acceptance": "pending",
                "rights_approval": False,
                "production_acceptance": False,
                "publication_acceptance": False,
                "upload_attempted": False,
                "missing_exact_source_lane": {
                    "identity": "youtube:Ocqg-RpQURY",
                    "range_seconds": [390, 585],
                    "status": "blocked_not_used_by_this_candidate",
                },
            },
        }
        write_json(output_dir / "successor_receipt.json", receipt)
        write_json(
            output_dir / "validation_readback.json",
            {
                "status": "passed",
                "artifact_id": ARTIFACT_ID,
                "exact_input_hashes": evidence["observed_sha256"],
                "output_sha256": output_sha,
                "duration_seconds": duration,
                "full_decode": "passed",
                "next_topic_subtitle_present": False,
                "closed_gates": receipt["boundaries"],
            },
        )
        (output_dir / "README.md").write_text(
            "# Wiki selected-opening successor\n\n"
            "Choice Set 4 revision 2 の選択済み冒頭を消費した内部candidateです。"
            "provider rolling captionのdurationを発話完結と見做さず、次話題開始前で閉じます。"
            "人間のcontent acceptance、rights、production、publicationは未承認です。\n",
            encoding="utf-8",
        )
        return receipt
    except Exception:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else repo_root / DEFAULT_OUTPUT_RELATIVE
    )
    receipt = build(
        repo_root=repo_root,
        output_dir=output_dir,
        ffmpeg=args.ffmpeg,
        ffprobe=args.ffprobe,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
