from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import main as cli_main
from src.integrations.render import common_context_probe as probe


def _plan() -> dict:
    sources = []
    for source_id, identity, media_hash in (
        ("source_alpha", "youtube:alpha", "a" * 64),
        ("source_beta", "youtube:beta", "b" * 64),
    ):
        sources.append(
            {
                "source_id": source_id,
                "display_name": source_id,
                "material_id": f"material_{source_id}",
                "source_identity": identity,
                "media": {
                    "path": f"episodes/{source_id}/source.mp4",
                    "sha256": media_hash,
                    "duration_seconds": 100.0,
                },
                "transcript": {"path": None, "sha256": None},
                "caption": {
                    "path": f"episodes/{source_id}/caption.json3",
                    "sha256": ("c" if source_id == "source_alpha" else "d") * 64,
                },
                "rights": {
                    "path": f"episodes/{source_id}/rights.json",
                    "sha256": ("e" if source_id == "source_alpha" else "f") * 64,
                    "status": "pending",
                },
                "evidence_segments": [
                    {
                        "evidence_id": f"{source_id}:evidence_{index}",
                        "source_start": float(index * 10),
                        "source_end": float(index * 10 + 5),
                        "text": f"{source_id} evidence {index}",
                    }
                    for index in range(3)
                ],
            }
        )
    cuts = []
    sequence = [
        ("source_alpha", 0.0, 10.0),
        ("source_beta", 0.0, 10.0),
        ("source_alpha", 10.0, 20.0),
        ("source_beta", 10.0, 20.0),
        ("source_alpha", 20.0, 30.0),
        ("source_beta", 20.0, 30.0),
    ]
    relations = [
        "introduces",
        "contrasts",
        "supports",
        "supports",
        "qualifies",
        "synthesizes",
    ]
    for index, ((source_id, source_in, source_out), relation) in enumerate(
        zip(sequence, relations), start=1
    ):
        evidence_index = (index - 1) // 2
        cuts.append(
            {
                "cut_id": f"cut_{index:03d}",
                "source_id": source_id,
                "source_in": source_in,
                "source_out": source_out,
                "output_in": float((index - 1) * 10),
                "output_out": float(index * 10),
                "section": "setup" if index <= 2 else "comparison",
                "editorial_role": f"role_{index}",
                "argument_relation": relation,
                "selection_reason": "direct evidence supports this bounded cut",
                "direct_evidence_ids": [
                    f"{source_id}:evidence_{evidence_index}"
                ],
                "context_evidence": "source-local context retained",
                "transition": "sequence_start" if index == 1 else "hard_cut",
            }
        )
    closed = [
        {"gate": key, "value": value}
        for key, value in probe._closed_gates().items()
    ]
    return {
        "schema_version": probe.PLAN_SCHEMA_VERSION,
        "artifact_id": probe.ARTIFACT_ID,
        "direction_signature": probe.DIRECTION_SIGNATURE,
        "editorial_question": "What changes when the sources are compared?",
        "working_thesis": "Both sources expose one bounded relation.",
        "thesis_classification": "authored_synthesis",
        "sources": sources,
        "argument_map": [
            {
                "cut_id": cut["cut_id"],
                "relation": cut["argument_relation"],
                "claim": f"claim {cut['cut_id']}",
                "direct_evidence_ids": cut["direct_evidence_ids"],
            }
            for cut in cuts
        ],
        "cuts": cuts,
        "commentary_track": [
            {
                "commentary_id": "commentary_001",
                "type": "authored_commentary",
                "authored_by": "creator",
                "output_start": 12.0,
                "output_end": 14.0,
                "evidence_source_ids": ["source_alpha", "source_beta"],
                "evidence_cut_ids": ["cut_001", "cut_002"],
                "evidence_ids": [
                    "source_alpha:evidence_0",
                    "source_beta:evidence_0",
                ],
                "claim_role": "creator_framing",
                "text": "First relation.",
                "presentation_anchor": "top_center_compact_band",
            },
            {
                "commentary_id": "commentary_002",
                "type": "authored_commentary",
                "authored_by": "creator",
                "output_start": 42.0,
                "output_end": 44.0,
                "evidence_source_ids": ["source_alpha", "source_beta"],
                "evidence_cut_ids": ["cut_005", "cut_006"],
                "evidence_ids": [
                    "source_alpha:evidence_2",
                    "source_beta:evidence_2",
                ],
                "claim_role": "creator_synthesis",
                "text": "Second relation.",
                "presentation_anchor": "top_center_compact_band",
            },
        ],
        "excluded_directions": ["generic_n_source_architecture"],
        "closed_gates": closed,
    }


def _evidence(plan: dict) -> dict[str, dict]:
    return {
        row["evidence_id"]: {
            "evidence_id": row["evidence_id"],
            "source_id": source["source_id"],
            "source_start": row["source_start"],
            "source_end": row["source_end"],
            "text": row["text"],
        }
        for source in plan["sources"]
        for row in source["evidence_segments"]
    }


def test_cli_dispatch_registers_common_context_probe() -> None:
    assert "build-common-context-probe" in cli_main.SUBCOMMANDS


def test_distinct_source_identity_and_hash_are_enforced() -> None:
    plan = _plan()
    plan["sources"][1]["source_identity"] = plan["sources"][0]["source_identity"]
    with pytest.raises(probe.CommonContextProbeError, match="distinct"):
        probe.validate_common_context_plan(plan)

    plan = _plan()
    plan["sources"][1]["media"]["sha256"] = plan["sources"][0]["media"]["sha256"]
    with pytest.raises(probe.CommonContextProbeError, match="distinct SHA"):
        probe.validate_common_context_plan(plan)


def test_evidence_namespace_prevents_cross_source_collision() -> None:
    plan = _plan()
    plan["sources"][1]["evidence_segments"][0][
        "evidence_id"
    ] = "source_alpha:evidence_0"
    with pytest.raises(probe.CommonContextProbeError, match="source-namespaced"):
        probe.validate_common_context_plan(plan)


def test_per_source_chronology_is_enforced() -> None:
    plan = _plan()
    plan["cuts"][4]["source_in"] = 5.0
    plan["cuts"][4]["source_out"] = 15.0
    with pytest.raises(probe.CommonContextProbeError, match="chronology"):
        probe.validate_common_context_plan(plan)


def test_continuous_output_clock_is_enforced() -> None:
    plan = _plan()
    plan["cuts"][2]["output_in"] = 21.0
    with pytest.raises(probe.CommonContextProbeError, match="non-continuous"):
        probe.validate_common_context_plan(plan)


def test_cut_to_input_mapping_and_both_source_contribution() -> None:
    plan = _plan()
    probe.validate_common_context_plan(plan)
    plan["input_fingerprint"] = "1" * 64
    timeline = probe.build_timeline_ir(plan)

    assert timeline["source_input_indexes"] == {
        "source_alpha": 0,
        "source_beta": 1,
    }
    assert {cut["input_index"] for cut in timeline["cuts"]} == {0, 1}
    assert all(
        row["cut_count"] == 3
        for row in timeline["source_contribution"].values()
    )
    assert timeline["source_switch_count"] == 5
    filter_graph = probe.render_filter_complex(
        cuts=timeline["cuts"],
        source_input_indexes=timeline["source_input_indexes"],
        ass_path=Path("overlay.ass"),
    )
    assert "[0:v:0]" in filter_graph and "[1:v:0]" in filter_graph
    assert "scale=1920:1080:force_original_aspect_ratio=decrease" in filter_graph
    assert "pad=1920:1080" in filter_graph


def test_out_of_range_cut_is_rejected() -> None:
    plan = _plan()
    plan["cuts"][-1]["source_out"] = 101.0
    plan["cuts"][-1]["output_out"] = 131.0
    with pytest.raises(probe.CommonContextProbeError, match="invalid"):
        probe.validate_common_context_plan(plan)


def test_caption_and_commentary_provenance_remain_separate() -> None:
    plan = _plan()
    probe.validate_common_context_plan(plan)
    plan["input_fingerprint"] = "2" * 64
    evidence = _evidence(plan)
    timeline = probe.build_timeline_ir(plan)
    captions = probe.remap_source_captions(
        plan=plan, evidence=evidence, timeline=timeline
    )
    commentary = probe.build_commentary_track(plan, evidence)

    probe.validate_caption_commentary_separation(
        captions=captions, commentary=commentary, output_duration=60.0
    )
    assert captions["namespace_valid"] is True
    assert captions["provenance_type"] == "source_caption"
    assert commentary["provenance_type"] == "creator_authored_commentary"
    assert set(captions["per_source_cue_count"]) == {
        "source_alpha",
        "source_beta",
    }


def test_orphan_and_commentary_overlap_are_rejected() -> None:
    plan = _plan()
    plan["commentary_track"][1]["output_start"] = 13.0
    with pytest.raises(probe.CommonContextProbeError, match="invalid commentary"):
        probe.validate_common_context_plan(plan)

    plan = _plan()
    plan["commentary_track"][0]["evidence_ids"] = ["source_alpha:missing"]
    with pytest.raises(probe.CommonContextProbeError, match="invalid commentary"):
        probe.validate_common_context_plan(plan)


def test_immutable_manifest_self_integrity_and_closed_set(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text('{"ok":true}\n', encoding="utf-8")
    rows = [
        {
            "repo_relative_path": "payload.json",
            "sha256": probe._sha256(payload),
            "byte_size": payload.stat().st_size,
        }
    ]
    manifest = {
        "schema_version": probe.MANIFEST_SCHEMA_VERSION,
        "artifact_id": probe.ARTIFACT_ID,
        "files": rows,
        "closed_file_set": {
            "payload_tree_digest_sha256": probe._payload_tree_digest(rows)
        },
        "manifest_self_integrity": {"sha256": None},
    }
    manifest["manifest_self_integrity"]["sha256"] = probe._manifest_self_hash(
        manifest
    )
    (tmp_path / "run_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    probe.validate_run_manifest(tmp_path)
    payload.write_text('{"ok":false}\n', encoding="utf-8")
    with pytest.raises(probe.CommonContextProbeError, match="payload mismatch"):
        probe.validate_run_manifest(tmp_path)


def test_default_off_closed_gate_state_is_required() -> None:
    plan = _plan()
    probe.validate_common_context_plan(plan)
    public_gate = next(
        row for row in plan["closed_gates"] if row["gate"] == "public_use"
    )
    public_gate["value"] = True
    with pytest.raises(probe.CommonContextProbeError, match="closed gates"):
        probe.validate_common_context_plan(plan)


def test_review_seek_controls_pause_before_assigning_current_time() -> None:
    plan = _plan()
    probe.validate_common_context_plan(plan)
    plan["input_fingerprint"] = "3" * 64
    evidence = _evidence(plan)
    timeline = probe.build_timeline_ir(plan)
    commentary = probe.build_commentary_track(plan, evidence)
    rights_inventory = {
        "ranges": [
            {
                "cut_id": cut["cut_id"],
                "source_id": cut["source_id"],
                "source_in": cut["source_in"],
                "source_out": cut["source_out"],
                "rights_status": "pending",
            }
            for cut in timeline["cuts"]
        ]
    }
    html = probe.render_review_html(
        plan=plan,
        timeline=timeline,
        commentary=commentary,
        rights_inventory=rights_inventory,
        validation={
            "status": "passed",
            "media": {"duration_seconds": 60.0},
        },
    )

    assert '<button type="button" data-seek="12.000">12.0s</button>' in html
    assert "video.pause();video.currentTime=target;" in html
    assert "video.addEventListener('loadedmetadata',applySeek,{once:true})" in html
    assert "overflow-wrap:anywhere" in html
