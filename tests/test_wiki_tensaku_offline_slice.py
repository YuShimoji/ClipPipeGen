import hashlib
import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = REPO_ROOT / "src/integrations/asset_fetch/wiki_tensaku_corpus.mjs"


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_existing_corpus_slice_can_materialize_from_retained_evidence_without_network(tmp_path: Path) -> None:
    video_id = "Ocqg-RpQURY"
    artifact_id = "clip-wiki-tensaku-longform-v1-003"
    source = {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": "retained wiki review source",
        "channel": "Miko Ch. さくらみこ",
        "channel_id": "UC-hM6YJuNYVAmUWxeIr9FeA",
        "duration_seconds": 3600,
        "availability": "OK",
        "archived_livestream": True,
        "caption_status": "fetched",
    }
    _write_json(
        tmp_path / "corpus_inventory.json",
        {
            "schema_version": "clippipegen.wiki_tensaku_corpus.v1",
            "family_id": "miko_led_unofficial_wiki_review",
            "videos": [source],
        },
    )
    _write_json(
        tmp_path / "corpus_receipt.json",
        {
            "schema_version": "clippipegen.wiki_tensaku_corpus.v1",
            "corpus": {"canonical_inventory_sha256": "fixture"},
            "missing_and_private": {"completeness_claim": "fixture_public_surface"},
        },
    )
    _write_json(
        tmp_path / "watch_receipts" / f"{video_id}.json",
        {
            "schema_version": "clippipegen.wiki_tensaku_corpus.v1",
            **source,
            "caption": {"status": "fetched", "language_code": "ja"},
        },
    )
    _write_json(
        tmp_path / "captions" / f"{video_id}.ja.json3",
        {
            "events": [
                {
                    "tStartMs": index * 150_000,
                    "dDurationMs": 5_000,
                    "segs": [{"utf8": "関係性を確認して記述を訂正する"}],
                }
                for index in range(24)
            ]
        },
    )

    completed = subprocess.run(
        [
            "node",
            str(COLLECTOR),
            "--output-dir",
            str(tmp_path),
            "--reuse-inventory",
            "--slice-video-id",
            video_id,
            "--artifact-id",
            artifact_id,
            "--offline-existing-evidence",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["state"] == "EXISTING_CORPUS_SUCCESSOR_SLICE_INPUTS_READY"
    assert result["availability_readback_mode"] == "retained_corpus_snapshot_no_network"
    assert result["network_requests_performed"] == 0

    slice_dir = tmp_path / "slice_inputs" / artifact_id
    receipt = json.loads((slice_dir / "slice_receipt.json").read_text(encoding="utf-8"))
    context = json.loads((slice_dir / "editorial_context.json").read_text(encoding="utf-8"))
    assert receipt["live_availability_readback"] is None
    assert receipt["retained_availability_readback"]["receipt"]["video_id"] == video_id
    assert receipt["source_caption"]["full_source_indexed"] is True
    assert len(context["chapters"]) == 12
    assert len(context["creator_commentary"]["events"]) == 12


def test_correction_led_slice_reuses_exact_retained_media_without_network(tmp_path: Path) -> None:
    video_id = "1AcId5Yja10"
    artifact_id = "clip-wiki-tensaku-family-turn-v1-001"
    source = {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": "retained wiki review source",
        "channel": "Miko Ch. さくらみこ",
        "channel_id": "UC-hM6YJuNYVAmUWxeIr9FeA",
        "duration_seconds": 3600,
        "availability": "OK",
        "archived_livestream": True,
        "caption_status": "fetched",
    }
    _write_json(
        tmp_path / "corpus_inventory.json",
        {
            "schema_version": "clippipegen.wiki_tensaku_corpus.v1",
            "family_id": "miko_led_unofficial_wiki_review",
            "videos": [source],
        },
    )
    _write_json(
        tmp_path / "corpus_receipt.json",
        {
            "schema_version": "clippipegen.wiki_tensaku_corpus.v1",
            "corpus": {"canonical_inventory_sha256": "fixture"},
            "missing_and_private": {"completeness_claim": "fixture_public_surface"},
        },
    )
    _write_json(
        tmp_path / "watch_receipts" / f"{video_id}.json",
        {
            "schema_version": "clippipegen.wiki_tensaku_corpus.v1",
            **source,
            "caption": {"status": "fetched", "language_code": "ja"},
        },
    )
    _write_json(
        tmp_path / "captions" / f"{video_id}.ja.json3",
        {
            "events": [
                {
                    "tStartMs": index * 150_000,
                    "dDurationMs": 5_000,
                    "segs": [{"utf8": "記述が違うので事実を確認して訂正する" if index % 2 == 0 else "周辺の会話"}],
                }
                for index in range(24)
            ]
        },
    )
    media = b"retained exact source bytes"
    media_path = tmp_path / "materials" / video_id / "source_video.mp4"
    media_path.parent.mkdir(parents=True, exist_ok=True)
    media_path.write_bytes(media)
    media_sha256 = hashlib.sha256(media).hexdigest()
    receipt_path = media_path.with_name("acquisition_receipt.json")
    _write_json(
        receipt_path,
        {
            "schema_version": "clippipegen.wiki_tensaku_corpus.v1",
            "source_identity": f"youtube:{video_id}",
            "source_sha256": media_sha256,
            "source_byte_size": len(media),
            "cookies_used": False,
            "oauth_used": False,
            "format": {"approx_duration_seconds": 3600, "combined_audio_video": True},
        },
    )

    command = [
        "node",
        str(COLLECTOR),
        "--output-dir",
        str(tmp_path),
        "--reuse-inventory",
        "--slice-video-id",
        video_id,
        "--artifact-id",
        artifact_id,
        "--offline-existing-evidence",
        "--reuse-retained-source-media",
        "--selection-profile",
        "correction-led",
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["network_requests_performed"] == 0
    assert result["selected_source_media_reused"] is True
    assert result["selected_source_media_sha256"] == media_sha256
    assert result["selection_profile"] == "correction-led"

    slice_dir = tmp_path / "slice_inputs" / artifact_id
    receipt = json.loads((slice_dir / "slice_receipt.json").read_text(encoding="utf-8"))
    context = json.loads((slice_dir / "editorial_context.json").read_text(encoding="utf-8"))
    assert receipt["evidence_mode"] == "retained_caption_inventory_topic_watch_and_source_bytes_no_network"
    assert receipt["source"]["media_reuse_mode"] == "retained_exact_bytes_no_network"
    assert context["expected_selection_mode"] == "editorial_context_correction_led_chronological_sampling"
    assert context["selection_summary"]["chapters_with_correction_anchor"] == 12
    assert context["selection_summary"]["selected_correction_anchor_count"] == 12

    rights_before = (slice_dir / "rights_manifest.json").read_bytes()
    context_before = (slice_dir / "editorial_context.json").read_bytes()
    subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert (slice_dir / "rights_manifest.json").read_bytes() == rights_before
    assert (slice_dir / "editorial_context.json").read_bytes() == context_before

    bad_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    bad_receipt["source_sha256"] = "0" * 64
    _write_json(receipt_path, bad_receipt)
    bad_command = command.copy()
    bad_command[bad_command.index(artifact_id)] = "clip-wiki-tensaku-family-turn-v1-bad"
    failed = subprocess.run(
        bad_command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert failed.returncode == 2
    assert "retained source media does not match acquisition receipt" in failed.stderr
    assert not (tmp_path / "slice_inputs" / "clip-wiki-tensaku-family-turn-v1-bad").exists()
