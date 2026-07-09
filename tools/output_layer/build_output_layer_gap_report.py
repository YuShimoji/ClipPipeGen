"""Build output layer gap report and local fixture proof artifacts.

This module stays inside the tracked docs/output_layer surface. It creates a
synthetic, no-external-media OUT-02 proof package plus the capability/gap
readback that explains what the fixture proves and which gates remain closed.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


SCHEMA_ID = "clippipegen.output_layer_gap_report.v0"
PROOF_SCHEMA_ID = "clippipegen.local_fixture_output_proof.v0"
DEFAULT_ARTIFACT_ID = "clip-out02-local-fixture-output-proof-smoke-v0-001"
PROOF_DIR_NAME = "local_fixture_output_proof"
FIXTURE_EPISODE_ID = "out02_synthetic_fixture_episode"
PROOF_STATUS = "local_fixture_output_proof_present"
ALLOWED_STATES = {"absent", "fixture_only", "planned", "local_ready", "gated"}


def build_output_layer_gap_report(
    *,
    base_dir: Path,
    generated_at: str,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
    proof_dir: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic output layer gap report payload."""

    base_dir = base_dir.resolve()
    proof_dir_path = _resolve_under_base(
        base_dir,
        proof_dir or Path("docs") / "output_layer" / PROOF_DIR_NAME,
    )
    proof_dir_display = _display_path(proof_dir_path, base_dir)
    proof_manifest_path = f"{proof_dir_display}/proof_manifest.json"
    proof_package = build_local_fixture_output_proof(
        generated_at=generated_at,
        artifact_id=artifact_id,
        proof_dir=proof_dir_display,
    )
    capabilities = _capability_rows(base_dir, proof_manifest_path)
    gaps = _gap_rows(proof_manifest_path)
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "active_slice": "OUT-02 Local Fixture Output Proof Smoke v0",
        "scope": {
            "repo": "ClipPipeGen",
            "branch": "codex/out-02-local-fixture-output-proof-smoke-v0",
            "readback_only": False,
            "proof_scope": "local_fixture_synthetic_no_external_media",
            "source_kind": "synthetic_fixture",
            "network_used": False,
            "source_urls_opened": False,
            "external_media_used": False,
            "media_downloaded": False,
            "media_generated": False,
            "yt_dlp_used": False,
            "oauth_or_api_used": False,
            "fetch_authorized": False,
            "rights_approved": False,
            "production_render_attempted": False,
            "production_ready": False,
            "public_upload_attempted": False,
            "public_ready": False,
            "notes": [
                "OUT-02 creates a synthetic local fixture proof package only.",
                "No source URL, external media, network fetch, OAuth/API, yt-dlp, or upload path is used.",
                "The proof is diagnostic readback, not production render or public-use approval.",
            ],
        },
        "proof_readback": {
            "local_output_readback_status": PROOF_STATUS,
            "proof_status": PROOF_STATUS,
            "source_kind": "synthetic_fixture",
            "external_media_used": False,
            "network_used": False,
            "fetch_authorized": False,
            "rights_approved": False,
            "public_ready": False,
            "production_ready": False,
            "production_candidate": False,
            "reason": (
                "OUT-02 closes the portable proof-artifact gap with a tracked synthetic "
                "fixture package: manifest JSON, readback JSON, edit-pack JSON, SRT, "
                "Markdown, and static HTML timeline."
            ),
        },
        "proof_artifacts": proof_package["summary"],
        "capability_matrix": capabilities,
        "gap_log": gaps,
        "recommended_next_slice": {
            "slice_id": "OUT-03-selected-cut-proof-link",
            "lane": "OUTPUT_VIDEO",
            "goal": (
                "Link selected cut ids to local proof/readback artifacts so a reviewer can "
                "move from an edit decision to the exact proof surface without hunting."
            ),
            "why_next": (
                "OUT-02 proves the portable fixture package shape. The next shortest "
                "output-layer unlock is connecting selected cuts to that proof surface "
                "while real source, transcript, production render, rights, and upload "
                "gates remain separate."
            ),
            "evidence_basis": [
                "fixture_edit_pack.json now carries selected cut ids and subtitle draft rows.",
                "proof_timeline.html now gives a human-readable segment/readback surface.",
                "video_output_gap_log.json still records real source and public gates as open gaps.",
            ],
            "validation": [
                "Parse proof_manifest.json, proof_readback.json, and fixture_edit_pack.json.",
                "Confirm proof_timeline.html references the fixture manifest and selected cuts.",
                "Keep external_media_used, network_used, fetch_authorized, rights_approved, public_ready, and production_ready false.",
                "Confirm git ls-files episodes remains empty.",
            ],
        },
        "true_gates": [
            {
                "gate_id": "rights_and_publication_acceptance",
                "blocked_by_true_gate": True,
                "applies_to": ["production_render", "public_upload", "public_ready_claims"],
                "reason": (
                    "Rights, publication judgment, account/OAuth, and public destination "
                    "are human-owned decisions."
                ),
                "evidence_path": "docs/AUTOMATION_BOUNDARY.md",
            },
            {
                "gate_id": "real_source_material_acquisition",
                "blocked_by_true_gate": False,
                "applies_to": ["future_local_diagnostic_proof"],
                "reason": (
                    "A later local-material or explicitly approved private fetch slice can "
                    "provide real source media without making public or rights claims."
                ),
                "evidence_path": "docs/SCHEMAS/v1/tiny_render.md",
            },
        ],
        "validation_plan": [
            "Run build-output-layer-gap-report and parse video_output_gap_log.json.",
            "Parse local_fixture_output_proof/proof_manifest.json, proof_readback.json, and fixture_edit_pack.json.",
            "Confirm proof_timeline.html exists and references the proof data without a video player or execution controls.",
            "Run targeted pytest coverage for the output proof/report and asset-fetch boundary smoke.",
            "Run git diff --check and confirm git ls-files episodes is empty.",
        ],
    }


def build_local_fixture_output_proof(
    *,
    generated_at: str,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
    proof_dir: str | Path = Path("docs") / "output_layer" / PROOF_DIR_NAME,
) -> dict[str, Any]:
    """Return the synthetic OUT-02 proof package payloads."""

    proof_dir_display = _normalize_display_path(proof_dir)
    files = {
        "proof_manifest": f"{proof_dir_display}/proof_manifest.json",
        "proof_readback": f"{proof_dir_display}/proof_readback.json",
        "proof_timeline": f"{proof_dir_display}/proof_timeline.html",
        "fixture_edit_pack": f"{proof_dir_display}/fixture_edit_pack.json",
        "fixture_subtitles": f"{proof_dir_display}/fixture_subtitles.srt",
        "readme": f"{proof_dir_display}/README.md",
    }
    segments = _fixture_segments()
    selected_cut_ids = [segment["cut_id"] for segment in segments]
    subtitle_rows = [
        {
            "subtitle_id": f"sub_{index:03d}",
            "segment_id": segment["segment_id"],
            "cut_id": segment["cut_id"],
            "speaker": segment["speaker"],
            "start_seconds": segment["start_seconds"],
            "end_seconds": segment["end_seconds"],
            "text": segment["subtitle_text"],
            "source_type": "synthetic_fixture",
            "review_status": "diagnostic_fixture_only",
        }
        for index, segment in enumerate(segments, start=1)
    ]
    fixture_edit_pack = _fixture_edit_pack(
        generated_at=generated_at,
        segments=segments,
        subtitle_rows=subtitle_rows,
        selected_cut_ids=selected_cut_ids,
    )
    manifest = {
        "schema_id": f"{PROOF_SCHEMA_ID}.manifest",
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "proof_status": PROOF_STATUS,
        "proof_scope": "local_fixture_synthetic_no_external_media",
        "source_kind": "synthetic_fixture",
        "fixture_episode_id": FIXTURE_EPISODE_ID,
        "external_media_used": False,
        "network_used": False,
        "source_urls_opened": False,
        "fetch_authorized": False,
        "media_downloaded": False,
        "large_media_files_created": False,
        "yt_dlp_used": False,
        "oauth_or_api_used": False,
        "rights_approved": False,
        "public_ready": False,
        "production_ready": False,
        "production_candidate": False,
        "public_upload_attempted": False,
        "production_render_attempted": False,
        "files": files,
        "selected_cut_ids": selected_cut_ids,
        "segment_count": len(segments),
        "subtitle_count": len(subtitle_rows),
        "timeline_duration_seconds": segments[-1]["end_seconds"],
        "visual_review_surfaces": [
            "title_card",
            "subtitle_band",
            "segment_list",
            "export_readiness_notes",
        ],
        "remaining_gaps": [
            "real_source_material_absent",
            "real_transcript_absent",
            "production_render_absent",
            "rights_approval_absent",
            "public_upload_gated",
        ],
        "next_recommended_slice": "OUT-03-selected-cut-proof-link",
    }
    readback = {
        "schema_id": f"{PROOF_SCHEMA_ID}.readback",
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "proof_status": PROOF_STATUS,
        "source_kind": "synthetic_fixture",
        "external_media_used": False,
        "network_used": False,
        "fetch_authorized": False,
        "rights_approved": False,
        "public_ready": False,
        "production_ready": False,
        "production_candidate": False,
        "title_card": {
            "text": "OUT-02 local fixture proof",
            "purpose": "Show the output-stage package shape without real media.",
        },
        "subtitle_band": {
            "source": "fixture_subtitles.srt",
            "draft_count": len(subtitle_rows),
            "status": "diagnostic_fixture_only",
        },
        "segments": segments,
        "output_stage_readback": [
            "The manifest is parseable JSON and records every external/public gate as false.",
            "The fixture edit pack carries selected cut ids, timing, speakers, subtitle text, and cut reasons.",
            "The HTML timeline is inspectable without opening a source URL, fetching media, or using a video player.",
        ],
        "export_readiness_notes": [
            "Ready for OUT-03 link/readback work against selected_cut_ids.",
            "Not a production render, public-ready output, or rights/publication decision.",
            "Real source material and transcript remain absent by design in this slice.",
        ],
    }
    timeline_html = render_proof_timeline_html(
        manifest=manifest,
        readback=readback,
        fixture_edit_pack=fixture_edit_pack,
    )
    readme = render_proof_readme_markdown(manifest=manifest, readback=readback)
    subtitles_srt = render_fixture_subtitles_srt(segments)
    summary = {
        "proof_dir": proof_dir_display,
        "proof_status": PROOF_STATUS,
        "source_kind": "synthetic_fixture",
        "external_media_used": False,
        "network_used": False,
        "fetch_authorized": False,
        "rights_approved": False,
        "public_ready": False,
        "production_ready": False,
        "files": files,
        "selected_cut_ids": selected_cut_ids,
        "segment_count": len(segments),
        "recommended_next_slice": "OUT-03-selected-cut-proof-link",
    }
    return {
        "summary": summary,
        "proof_manifest": manifest,
        "proof_readback": readback,
        "fixture_edit_pack": fixture_edit_pack,
        "fixture_subtitles_srt": subtitles_srt,
        "proof_timeline_html": timeline_html,
        "readme_markdown": readme,
    }


def write_output_layer_gap_report(
    *,
    base_dir: Path,
    output_dir: Path,
    generated_at: str,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Write JSON, Markdown matrix, HTML readback, and fixture proof artifacts."""

    base_dir = base_dir.resolve()
    output_dir = _resolve_under_base(base_dir, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    proof_dir = output_dir / PROOF_DIR_NAME
    proof_dir.mkdir(parents=True, exist_ok=True)
    proof_dir_display = _display_path(proof_dir, base_dir)

    proof_package = build_local_fixture_output_proof(
        generated_at=generated_at,
        artifact_id=artifact_id,
        proof_dir=proof_dir_display,
    )

    json_path = output_dir / "video_output_gap_log.json"
    matrix_path = output_dir / "output_capability_matrix.md"
    html_path = output_dir / "local_output_readback.html"
    proof_manifest_path = proof_dir / "proof_manifest.json"
    proof_readback_path = proof_dir / "proof_readback.json"
    proof_timeline_path = proof_dir / "proof_timeline.html"
    fixture_edit_pack_path = proof_dir / "fixture_edit_pack.json"
    fixture_subtitles_path = proof_dir / "fixture_subtitles.srt"
    proof_readme_path = proof_dir / "README.md"

    _write_text_lf(
        proof_manifest_path,
        json.dumps(proof_package["proof_manifest"], ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(
        proof_readback_path,
        json.dumps(proof_package["proof_readback"], ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(
        fixture_edit_pack_path,
        json.dumps(proof_package["fixture_edit_pack"], ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(fixture_subtitles_path, proof_package["fixture_subtitles_srt"])
    _write_text_lf(proof_timeline_path, proof_package["proof_timeline_html"])
    _write_text_lf(proof_readme_path, proof_package["readme_markdown"])

    report = build_output_layer_gap_report(
        base_dir=base_dir,
        generated_at=generated_at,
        artifact_id=artifact_id,
        proof_dir=proof_dir,
    )
    _write_text_lf(
        json_path,
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(matrix_path, render_capability_matrix_markdown(report))
    _write_text_lf(html_path, render_local_output_readback_html(report))

    return {
        "report": report,
        "proof_package": proof_package,
        "outputs": {
            "video_output_gap_log": _display_path(json_path, base_dir),
            "output_capability_matrix": _display_path(matrix_path, base_dir),
            "local_output_readback": _display_path(html_path, base_dir),
            "local_fixture_output_proof": {
                "proof_manifest": _display_path(proof_manifest_path, base_dir),
                "proof_readback": _display_path(proof_readback_path, base_dir),
                "proof_timeline": _display_path(proof_timeline_path, base_dir),
                "fixture_edit_pack": _display_path(fixture_edit_pack_path, base_dir),
                "fixture_subtitles": _display_path(fixture_subtitles_path, base_dir),
                "readme": _display_path(proof_readme_path, base_dir),
            },
        },
    }


def render_capability_matrix_markdown(report: dict[str, Any]) -> str:
    """Render the capability matrix as reviewable Markdown."""

    proof = report["proof_readback"]
    proof_artifacts = report["proof_artifacts"]
    lines = [
        "# OUT-02 Output Capability Matrix",
        "",
        (
            "Readback matrix for the output/video layer after a local synthetic fixture "
            "proof package has been generated. This artifact does not fetch media, run "
            "production render, approve rights, or claim public readiness."
        ),
        "",
        f"- artifact_id: `{report['artifact_id']}`",
        f"- generated_at: `{report['generated_at']}`",
        f"- proof_status: `{proof['proof_status']}`",
        f"- source_kind: `{proof['source_kind']}`",
        f"- external_media_used: `{str(proof['external_media_used']).lower()}`",
        f"- network_used: `{str(proof['network_used']).lower()}`",
        f"- production_ready: `{str(proof['production_ready']).lower()}`",
        f"- public_ready: `{str(proof['public_ready']).lower()}`",
        "",
        "## Local Fixture Output Proof",
        "",
        "| artifact | path |",
        "|---|---|",
    ]
    for label, path in proof_artifacts["files"].items():
        lines.append(f"| {_md(label)} | `{_md(path)}` |")

    lines.extend(
        [
            "",
            "## Capability Matrix",
            "",
            (
                "| capability_id | current_state | evidence_path | missing_input | "
                "next_local_action | blocked_by_true_gate | notes |"
            ),
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in report["capability_matrix"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(row["capability_id"]),
                    _md(row["current_state"]),
                    _md(row["evidence_path"]),
                    _md(row["missing_input"]),
                    _md(row["next_local_action"]),
                    _md(str(row["blocked_by_true_gate"]).lower()),
                    _md(row["notes"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Gap Log",
            "",
            (
                "| gap_id | status | evidence_path | missing_input | local_vs_true_gate | "
                "suggested_next_slice | validation |"
            ),
            "|---|---|---|---|---|---|---|",
        ]
    )
    for gap in report["gap_log"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(gap["gap_id"]),
                    _md(gap["status"]),
                    _md(gap["evidence_path"]),
                    _md(gap["missing_input"]),
                    _md(gap["local_vs_true_gate"]),
                    _md(gap["suggested_next_slice"]),
                    _md(gap["validation"]),
                ]
            )
            + " |"
        )

    next_slice = report["recommended_next_slice"]
    lines.extend(
        [
            "",
            "## Recommended Next Slice",
            "",
            f"- slice_id: `{next_slice['slice_id']}`",
            f"- lane: `{next_slice['lane']}`",
            f"- goal: {next_slice['goal']}",
            f"- why_next: {next_slice['why_next']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_local_output_readback_html(report: dict[str, Any]) -> str:
    """Render a static, no-media HTML readback for local review."""

    rows = "\n".join(_capability_row_html(row) for row in report["capability_matrix"])
    gap_rows = "\n".join(_gap_row_html(gap) for gap in report["gap_log"])
    next_slice = report["recommended_next_slice"]
    validations = "\n".join(f"<li>{escape(item)}</li>" for item in next_slice["validation"])
    proof = report["proof_readback"]
    proof_files = "\n".join(
        "        <tr>"
        f"<td><code>{escape(label)}</code></td>"
        f"<td><code>{escape(path)}</code></td>"
        "</tr>"
        for label, path in report["proof_artifacts"]["files"].items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OUT-02 Local Output Readback</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f2;
      --text: #1c2430;
      --muted: #596575;
      --line: #cbd2d9;
      --accent: #006c67;
      --ok: #1d6f42;
      --warn: #9a4a00;
      --gate: #7a1f3d;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    main {{
      width: min(1160px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 44px;
    }}
    h1, h2 {{
      margin: 0 0 12px;
      letter-spacing: 0;
    }}
    h1 {{
      font-size: 28px;
    }}
    h2 {{
      font-size: 20px;
      margin-top: 28px;
    }}
    p {{
      margin: 0 0 14px;
      color: var(--muted);
      max-width: 980px;
    }}
    .status-line {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin: 18px 0 6px;
    }}
    .status-line div {{
      border-top: 3px solid var(--accent);
      padding: 8px 0 0;
      min-width: 0;
    }}
    .status-line b {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .status-line span {{
      display: block;
      overflow-wrap: anywhere;
      font-weight: 700;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: #ffffff;
      border: 1px solid var(--line);
      table-layout: fixed;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 10px;
      text-align: left;
      vertical-align: top;
      overflow-wrap: anywhere;
      font-size: 13px;
    }}
    th {{
      background: #e9efef;
      color: #14242d;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .state-gated {{
      color: var(--gate);
      font-weight: 700;
    }}
    .state-absent, .state-planned {{
      color: var(--warn);
      font-weight: 700;
    }}
    .state-fixture_only, .status-local_fixture_output_proof_present {{
      color: var(--ok);
      font-weight: 700;
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 12px;
    }}
    ul {{
      margin: 8px 0 0 18px;
      padding: 0;
    }}
  </style>
</head>
<body>
  <main>
    <h1>OUT-02 Local Output Readback</h1>
    <p>This static readback records the local fixture output proof package and the remaining output-layer gaps without source fetching, external media, production render, or public upload.</p>
    <section class="status-line" aria-label="readback status">
      <div><b>artifact</b><span>{escape(report['artifact_id'])}</span></div>
      <div><b>generated</b><span>{escape(report['generated_at'])}</span></div>
      <div><b>proof</b><span class="status-{escape(proof['proof_status'])}">{escape(proof['proof_status'])}</span></div>
      <div><b>source kind</b><span>{escape(proof['source_kind'])}</span></div>
      <div><b>production ready</b><span>{escape(str(proof['production_ready']).lower())}</span></div>
      <div><b>public ready</b><span>{escape(str(proof['public_ready']).lower())}</span></div>
    </section>
    <p>{escape(proof['reason'])}</p>

    <h2>Local Fixture Proof Package</h2>
    <table>
      <thead>
        <tr>
          <th>artifact</th>
          <th>path</th>
        </tr>
      </thead>
      <tbody>
{proof_files}
      </tbody>
    </table>

    <h2>Capability Matrix</h2>
    <table>
      <thead>
        <tr>
          <th>capability_id</th>
          <th>current_state</th>
          <th>evidence_path</th>
          <th>missing_input</th>
          <th>next_local_action</th>
          <th>true_gate</th>
          <th>notes</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>

    <h2>Gap Log</h2>
    <table>
      <thead>
        <tr>
          <th>gap_id</th>
          <th>status</th>
          <th>evidence_path</th>
          <th>missing_input</th>
          <th>local_vs_true_gate</th>
          <th>suggested_next_slice</th>
          <th>validation</th>
        </tr>
      </thead>
      <tbody>
{gap_rows}
      </tbody>
    </table>

    <h2>Recommended Next Slice</h2>
    <p><code>{escape(next_slice['slice_id'])}</code> - {escape(next_slice['goal'])}</p>
    <p>{escape(next_slice['why_next'])}</p>
    <ul>
{validations}
    </ul>
  </main>
</body>
</html>
"""


def render_proof_timeline_html(
    *,
    manifest: dict[str, Any],
    readback: dict[str, Any],
    fixture_edit_pack: dict[str, Any],
) -> str:
    """Render the local fixture proof timeline HTML."""

    segment_rows = "\n".join(
        "          <tr>"
        f"<td><code>{escape(segment['cut_id'])}</code></td>"
        f"<td>{escape(_seconds_range(segment['start_seconds'], segment['end_seconds']))}</td>"
        f"<td>{escape(segment['speaker'])}</td>"
        f"<td>{escape(segment['subtitle_text'])}</td>"
        f"<td>{escape(segment['cut_reason'])}</td>"
        f"<td>{escape(segment['visual_readback'])}</td>"
        "</tr>"
        for segment in readback["segments"]
    )
    note_items = "\n".join(
        f"        <li>{escape(note)}</li>" for note in readback["export_readiness_notes"]
    )
    gate_rows = "\n".join(
        "          <tr>"
        f"<td><code>{escape(key)}</code></td>"
        f"<td>{escape(str(manifest[key]).lower())}</td>"
        "</tr>"
        for key in [
            "external_media_used",
            "network_used",
            "fetch_authorized",
            "rights_approved",
            "public_ready",
            "production_ready",
        ]
    )
    selected_cuts = ", ".join(fixture_edit_pack["selected_cut_ids"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OUT-02 Local Fixture Output Proof</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8f7f1;
      --ink: #1b2430;
      --muted: #566170;
      --line: #c7d0d8;
      --panel: #ffffff;
      --accent: #006c67;
      --band: #12343b;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 44px;
    }}
    h1, h2 {{
      letter-spacing: 0;
      margin: 0 0 12px;
    }}
    h1 {{
      font-size: 30px;
    }}
    h2 {{
      font-size: 20px;
      margin-top: 28px;
    }}
    p {{
      max-width: 940px;
      color: var(--muted);
      margin: 0 0 14px;
    }}
    .title-card {{
      background: var(--band);
      color: #ffffff;
      min-height: 150px;
      display: grid;
      align-content: center;
      padding: 24px;
      margin: 18px 0;
    }}
    .title-card strong {{
      font-size: 28px;
      letter-spacing: 0;
    }}
    .subtitle-band {{
      margin-top: 18px;
      padding: 12px 14px;
      background: #e7f2ef;
      border-left: 5px solid var(--accent);
      font-weight: 700;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      table-layout: fixed;
    }}
    th, td {{
      padding: 9px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      overflow-wrap: anywhere;
      font-size: 13px;
    }}
    th {{
      background: #e9efef;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <main>
    <h1>OUT-02 Local Fixture Output Proof</h1>
    <p>Diagnostic local fixture only. This package uses synthetic timing, speaker, subtitle, and cut-reason rows; it does not open source URLs, fetch external media, render production video, approve rights, or upload anything.</p>
    <section class="title-card" aria-label="title card">
      <strong>{escape(readback['title_card']['text'])}</strong>
      <span>{escape(readback['title_card']['purpose'])}</span>
      <div class="subtitle-band">Subtitle band source: {escape(readback['subtitle_band']['source'])}; selected cuts: {escape(selected_cuts)}</div>
    </section>

    <h2>Fixture Timeline</h2>
    <table>
      <thead>
        <tr>
          <th>cut</th>
          <th>time</th>
          <th>speaker</th>
          <th>subtitle text</th>
          <th>cut reason</th>
          <th>output readback</th>
        </tr>
      </thead>
      <tbody>
{segment_rows}
      </tbody>
    </table>

    <h2>Thin Gate Contract</h2>
    <table>
      <thead><tr><th>gate</th><th>value</th></tr></thead>
      <tbody>
{gate_rows}
      </tbody>
    </table>

    <h2>Export Readiness Notes</h2>
    <ul>
{note_items}
    </ul>

    <h2>Proof Data Files</h2>
    <p><code>{escape(manifest['files']['proof_manifest'])}</code>, <code>{escape(manifest['files']['proof_readback'])}</code>, and <code>{escape(manifest['files']['fixture_edit_pack'])}</code> are parseable JSON. <code>{escape(manifest['files']['fixture_subtitles'])}</code> is the subtitle draft readback for this synthetic fixture.</p>
  </main>
</body>
</html>
"""


def render_proof_readme_markdown(
    *,
    manifest: dict[str, Any],
    readback: dict[str, Any],
) -> str:
    """Render the proof package README."""

    lines = [
        "# OUT-02 Local Fixture Output Proof",
        "",
        (
            "This package is a synthetic, local-only diagnostic proof for the output "
            "layer. It is designed to be inspectable as JSON, Markdown, SRT, and static "
            "HTML without relying on external source media."
        ),
        "",
        f"- artifact_id: `{manifest['artifact_id']}`",
        f"- proof_status: `{manifest['proof_status']}`",
        f"- source_kind: `{manifest['source_kind']}`",
        f"- external_media_used: `{str(manifest['external_media_used']).lower()}`",
        f"- network_used: `{str(manifest['network_used']).lower()}`",
        f"- fetch_authorized: `{str(manifest['fetch_authorized']).lower()}`",
        f"- rights_approved: `{str(manifest['rights_approved']).lower()}`",
        f"- public_ready: `{str(manifest['public_ready']).lower()}`",
        f"- production_ready: `{str(manifest['production_ready']).lower()}`",
        "",
        "## Files",
        "",
        "| file | purpose |",
        "|---|---|",
        f"| `proof_manifest.json` | Machine-readable proof boundary and artifact map. |",
        f"| `proof_readback.json` | Human/reviewer readback as parseable JSON. |",
        f"| `proof_timeline.html` | Static title-card, subtitle-band, segment-list, and gate readback. |",
        f"| `fixture_edit_pack.json` | Synthetic selected-cut fixture shaped like an edit-pack handoff. |",
        f"| `fixture_subtitles.srt` | Synthetic subtitle draft for the fixture timeline. |",
        "",
        "## What This Proves",
        "",
        (
            "OUT-02 closes the previous portable proof-artifact gap: a reviewer can now "
            "open the HTML timeline and a tool can parse the manifest/readback/edit-pack "
            "JSON without source media or network access."
        ),
        "",
        "## What Remains Outside This Proof",
        "",
    ]
    for gap in manifest["remaining_gaps"]:
        lines.append(f"- `{gap}`")
    lines.extend(
        [
            "",
            "## Readback",
            "",
        ]
    )
    for note in readback["output_stage_readback"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def render_fixture_subtitles_srt(segments: list[dict[str, Any]]) -> str:
    """Render SRT subtitle rows for the synthetic fixture."""

    blocks: list[str] = []
    for index, segment in enumerate(segments, start=1):
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{_srt_time(segment['start_seconds'])} --> {_srt_time(segment['end_seconds'])}",
                    f"[{segment['speaker']}] {segment['subtitle_text']}",
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def _fixture_segments() -> list[dict[str, Any]]:
    return [
        {
            "segment_id": "seg_001",
            "cut_id": "cut_fixture_001",
            "start_seconds": 0.0,
            "end_seconds": 2.8,
            "speaker": "host",
            "subtitle_text": "Local fixture proof starts here.",
            "cut_reason": "Title card confirms that the proof is diagnostic and local-only.",
            "visual_readback": "Title card plus first subtitle band.",
        },
        {
            "segment_id": "seg_002",
            "cut_id": "cut_fixture_002",
            "start_seconds": 2.8,
            "end_seconds": 6.4,
            "speaker": "guest",
            "subtitle_text": "The selected cut list is visible without opening media.",
            "cut_reason": "Shows how selected_cut_ids map to segment timing and speaker labels.",
            "visual_readback": "Segment row with timing, speaker, and reason.",
        },
        {
            "segment_id": "seg_003",
            "cut_id": "cut_fixture_003",
            "start_seconds": 6.4,
            "end_seconds": 9.6,
            "speaker": "host",
            "subtitle_text": "All public and production gates remain false.",
            "cut_reason": "Keeps rights/public/upload states explicit at the output stage.",
            "visual_readback": "Gate table plus export-readiness notes.",
        },
    ]


def _fixture_edit_pack(
    *,
    generated_at: str,
    segments: list[dict[str, Any]],
    subtitle_rows: list[dict[str, Any]],
    selected_cut_ids: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "episode_id": FIXTURE_EPISODE_ID,
        "rights_manifest_path": "not_applicable_synthetic_fixture",
        "material_ledger_path": "not_applicable_synthetic_fixture",
        "created_at": generated_at,
        "updated_at": generated_at,
        "proof_scope": "local_fixture_synthetic_no_external_media",
        "source_kind": "synthetic_fixture",
        "production_ready": False,
        "public_ready": False,
        "editing_intent": {
            "target_duration_seconds": segments[-1]["end_seconds"],
            "topic": "OUT-02 local fixture output proof",
            "audience_note": "Internal diagnostic readback only.",
            "language": "en",
        },
        "cut_candidates": [
            {
                "id": segment["cut_id"],
                "start_seconds": segment["start_seconds"],
                "end_seconds": segment["end_seconds"],
                "source": "synthetic_fixture",
                "reason": segment["cut_reason"],
                "confidence": 1.0,
                "context_check": {
                    "status": "passed",
                    "notes": ["Synthetic fixture row; not a real editorial acceptance."],
                },
            }
            for segment in segments
        ],
        "selected_cut_ids": selected_cut_ids,
        "subtitles": subtitle_rows,
        "review": {
            "status": "diagnostic_fixture_only",
            "reviewed_by": "not_applicable",
            "reviewed_at": generated_at,
            "notes": [
                "Synthetic fixture proves package shape only.",
                "No production, public, rights, or creative acceptance is claimed.",
            ],
        },
    }


def _capability_rows(base_dir: Path, proof_manifest_path: str) -> list[dict[str, Any]]:
    rows = [
        {
            "capability_id": "source_material_presence",
            "current_state": "fixture_only",
            "evidence_path": proof_manifest_path,
            "missing_input": "Real source_video/source_audio materials remain absent for this slice.",
            "next_local_action": "Use a later approved local-material or private-fetch smoke slice for real source proof.",
            "blocked_by_true_gate": False,
            "notes": "OUT-02 uses synthetic fixture data only; it does not prove real media availability.",
        },
        {
            "capability_id": "transcript_readiness",
            "current_state": "fixture_only",
            "evidence_path": proof_manifest_path,
            "missing_input": "A real or reviewed transcript for an actual target source is still absent.",
            "next_local_action": "Link selected cuts to real transcript rows only after local material/transcript approval.",
            "blocked_by_true_gate": False,
            "notes": "Fixture subtitles prove readback shape, not STT or transcript quality.",
        },
        {
            "capability_id": "edit_pack_readiness",
            "current_state": "fixture_only",
            "evidence_path": f"{Path(proof_manifest_path).parent.as_posix()}/fixture_edit_pack.json",
            "missing_input": "A real edit_pack connected to reviewed transcript and source media remains absent.",
            "next_local_action": "Use OUT-03 to connect selected_cut_ids to proof/readback artifacts.",
            "blocked_by_true_gate": False,
            "notes": "Fixture edit pack carries selected cuts, timing, speakers, subtitles, and reasons.",
        },
        {
            "capability_id": "subtitle_readiness",
            "current_state": "fixture_only",
            "evidence_path": f"{Path(proof_manifest_path).parent.as_posix()}/fixture_subtitles.srt",
            "missing_input": "Production subtitle design and real subtitle timing review remain absent.",
            "next_local_action": "Keep subtitle design acceptance separate from fixture proof and real output review.",
            "blocked_by_true_gate": False,
            "notes": "Fixture SRT is diagnostic readback only.",
        },
        {
            "capability_id": "local_fixture_output_proof",
            "current_state": "fixture_only",
            "evidence_path": proof_manifest_path,
            "missing_input": "None for the synthetic fixture proof package.",
            "next_local_action": "Use OUT-03 to link selected cuts to the proof surface.",
            "blocked_by_true_gate": False,
            "notes": "OUT-02 closes the portable proof artifact gap without external media.",
        },
        {
            "capability_id": "thumbnail_brief_readiness",
            "current_state": "planned",
            "evidence_path": "src/pipeline/episode_init_plan.py",
            "missing_input": "A reviewable thumbnail brief/output artifact tied to selected source materials.",
            "next_local_action": "Promote thumbnail brief seed fields into an operator-reviewable output-layer artifact later.",
            "blocked_by_true_gate": False,
            "notes": "Thumbnail output remains a separate planning/readback lane.",
        },
        {
            "capability_id": "preview_pack_readiness",
            "current_state": "local_ready",
            "evidence_path": "docs/PREVIEW_PACK.md",
            "missing_input": "A target episode with local media or existing source audio material.",
            "next_local_action": "Build a read-only local preview pack once operator-supplied material exists.",
            "blocked_by_true_gate": False,
            "notes": "Preview pack is useful readback, but it is not this fixture proof or a rendered video proof.",
        },
        {
            "capability_id": "nle_export_readiness",
            "current_state": "local_ready",
            "evidence_path": "docs/SCHEMAS/v1/nle_export.md",
            "missing_input": "A validated edit_pack with selected cuts and optional transcript refs.",
            "next_local_action": "Export CSV/JSON/HTML cut-list readback for human review or NLE handoff.",
            "blocked_by_true_gate": False,
            "notes": "NLE export proves edit structure, not final encoded video.",
        },
        {
            "capability_id": "local_render_proof_readiness",
            "current_state": "local_ready",
            "evidence_path": "docs/SCHEMAS/v1/tiny_render.md",
            "missing_input": "Real or approved local source video/audio and edit_pack inputs for an encoded diagnostic proof.",
            "next_local_action": "Run a narrow diagnostic render only after local materials are explicitly available.",
            "blocked_by_true_gate": False,
            "notes": "OUT-02 is a static fixture proof; production render remains out of scope.",
        },
        {
            "capability_id": "public_upload_readiness",
            "current_state": "gated",
            "evidence_path": "docs/AUTOMATION_BOUNDARY.md",
            "missing_input": "Rights acceptance, publication judgment, account/OAuth setup, and public target selection.",
            "next_local_action": "Keep public/upload out of local proof work; prepare only decision packets for human review.",
            "blocked_by_true_gate": True,
            "notes": "This is a true gate, not a missing local automation task.",
        },
    ]
    for row in rows:
        if row["current_state"] not in ALLOWED_STATES:
            raise ValueError(f"invalid state: {row['current_state']}")
        evidence_path = Path(row["evidence_path"])
        row["evidence_exists"] = (
            evidence_path.exists()
            if evidence_path.is_absolute()
            else (base_dir / evidence_path).exists()
        )
    return rows


def _gap_rows(proof_manifest_path: str) -> list[dict[str, str]]:
    return [
        {
            "gap_id": "gap_current_no_proof_artifact",
            "status": PROOF_STATUS,
            "evidence_path": proof_manifest_path,
            "missing_input": "Closed for synthetic fixture proof; real media proof remains a separate gap.",
            "why_it_matters": "Reviewers now have a tracked, inspectable proof package instead of only a readiness inventory.",
            "local_vs_true_gate": "Local fixture gap closed; no rights/publication gate crossed.",
            "suggested_next_slice": "OUT-03-selected-cut-proof-link",
            "validation": "Parse manifest/readback/edit-pack JSON and inspect proof_timeline.html.",
        },
        {
            "gap_id": "gap_real_source_material_absent",
            "status": "remaining_gap",
            "evidence_path": "docs/RUNTIME_STATE.md",
            "missing_input": "Real source_video/source_audio materials are absent from this proof.",
            "why_it_matters": "A synthetic proof does not verify pixels, audio, file metadata, or source-ledger linkage.",
            "local_vs_true_gate": "Local gap until operator-supplied material or an approved private fetch smoke exists.",
            "suggested_next_slice": "future-local-material-proof-or-private-fetch-smoke",
            "validation": "A later run records material ids and leaves git ls-files episodes empty.",
        },
        {
            "gap_id": "gap_real_transcript_absent",
            "status": "remaining_gap",
            "evidence_path": "docs/SCHEMAS/v1/transcript.md",
            "missing_input": "Real or reviewed transcript rows for a target source are absent.",
            "why_it_matters": "Fixture subtitles prove package shape, not transcript alignment or STT quality.",
            "local_vs_true_gate": "Local gap; transcript work can remain diagnostic while rights/public gates stay closed.",
            "suggested_next_slice": "EDIT-01-edit-operation-matrix",
            "validation": "Transcript-linked selected cuts preserve production/public flags as false.",
        },
        {
            "gap_id": "gap_production_render_absent",
            "status": "remaining_gap",
            "evidence_path": "docs/AUTOMATION_BOUNDARY.md",
            "missing_input": "No production render or production subtitle burn-in acceptance exists.",
            "why_it_matters": "OUT-02 is static readback, not an encoded final output.",
            "local_vs_true_gate": "Diagnostic render can be local; production acceptance is a separate human gate.",
            "suggested_next_slice": "final-render-path-output-review-after-local-material",
            "validation": "Any later render manifest keeps production_candidate=false until accepted.",
        },
        {
            "gap_id": "gap_rights_approval_absent",
            "status": "true_gate",
            "evidence_path": "docs/INVARIANTS.md",
            "missing_input": "Rights/legal/public-use approval remains absent.",
            "why_it_matters": "Local diagnostic success cannot become production/public permission.",
            "local_vs_true_gate": "True gate; requires explicit human-owned approval.",
            "suggested_next_slice": "rights-material-use-clearance",
            "validation": "rights_approved remains false until a dedicated acceptance record exists.",
        },
        {
            "gap_id": "gap_public_upload_true_gate",
            "status": "true_gate",
            "evidence_path": "docs/AUTOMATION_BOUNDARY.md",
            "missing_input": "Publication approval, account/OAuth, and target channel remain absent.",
            "why_it_matters": "A local proof must not drift into public action or upload readiness.",
            "local_vs_true_gate": "True gate; local automation can only prepare review packets.",
            "suggested_next_slice": "PB-decision-packet-before-upload",
            "validation": "Upload/public fields stay blocked until human-owned acceptance is recorded.",
        },
        {
            "gap_id": "recommend_next_out_slice",
            "status": "recommendation",
            "evidence_path": proof_manifest_path,
            "missing_input": "A selected-cut-to-proof link is not yet represented as a first-class output route.",
            "why_it_matters": "The proof is inspectable, but reviewers still need a direct route from selected_cut_ids to proof artifacts.",
            "local_vs_true_gate": "Local action; it should still avoid source fetching and public publication.",
            "suggested_next_slice": "OUT-03-selected-cut-proof-link",
            "validation": "Readback links selected_cut_ids to proof_timeline.html and JSON artifacts.",
        },
    ]


def _capability_row_html(row: dict[str, Any]) -> str:
    state_class = f"state-{row['current_state']}"
    gate = "true" if row["blocked_by_true_gate"] else "false"
    cells = [
        f"<code>{escape(row['capability_id'])}</code>",
        f"<span class=\"{escape(state_class)}\">{escape(row['current_state'])}</span>",
        f"<code>{escape(row['evidence_path'])}</code>",
        escape(row["missing_input"]),
        escape(row["next_local_action"]),
        escape(gate),
        escape(row["notes"]),
    ]
    return "        <tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"


def _gap_row_html(gap: dict[str, str]) -> str:
    cells = [
        f"<code>{escape(gap['gap_id'])}</code>",
        escape(gap["status"]),
        f"<code>{escape(gap['evidence_path'])}</code>",
        escape(gap["missing_input"]),
        escape(gap["local_vs_true_gate"]),
        escape(gap["suggested_next_slice"]),
        escape(gap["validation"]),
    ]
    return "        <tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"


def _resolve_under_base(base_dir: Path, path: Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return base_dir / path


def _display_path(path: Path, base_dir: Path) -> str:
    path = path.resolve()
    try:
        return path.relative_to(base_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _normalize_display_path(path: str | Path) -> str:
    if isinstance(path, Path):
        return path.as_posix()
    return path.replace("\\", "/")


def _write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _seconds_range(start_seconds: float, end_seconds: float) -> str:
    return f"{start_seconds:.1f}s to {end_seconds:.1f}s"


def _srt_time(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
