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
