"""Build OUT-01 output layer gap report artifacts.

This module is intentionally readback-only. It records current output-layer
capability, missing inputs, and true gates without fetching source material,
processing media, or claiming production readiness.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


SCHEMA_ID = "clippipegen.output_layer_gap_report.v0"
DEFAULT_ARTIFACT_ID = "clip-out01-output-layer-gap-logger-v0-001"
ALLOWED_STATES = {"absent", "fixture_only", "planned", "local_ready", "gated"}


def build_output_layer_gap_report(
    *,
    base_dir: Path,
    generated_at: str,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Return a deterministic output layer gap report payload."""

    base_dir = base_dir.resolve()
    capabilities = _capability_rows(base_dir)
    gaps = _gap_rows()
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "active_slice": "OUT-01 Local Output Proof / Video Layer Gap Logger v0",
        "scope": {
            "repo": "ClipPipeGen",
            "branch": "codex/out-01-output-layer-gap-logger-v0",
            "readback_only": True,
            "network_used": False,
            "source_urls_opened": False,
            "media_generated": False,
            "production_render_attempted": False,
            "public_upload_attempted": False,
            "notes": [
                "No source media was fetched, opened, downloaded, rendered, or uploaded.",
                "This report classifies local readiness and true gates for the output layer.",
            ],
        },
        "proof_readback": {
            "local_output_readback_status": "proof_missing_no_media_in_this_slice",
            "proof_status": "proof_missing",
            "production_ready": False,
            "public_ready": False,
            "reason": (
                "The repository has local diagnostic output code paths, but this slice has "
                "no tracked source video/source audio/edit pack bundle to prove."
            ),
        },
        "capability_matrix": capabilities,
        "gap_log": gaps,
        "recommended_next_slice": {
            "slice_id": "OUT-02-local-fixture-output-proof-smoke",
            "lane": "OUTPUT_VIDEO",
            "goal": (
                "Run the smallest approved local-material proof using explicit local "
                "source video, source audio, edit_pack, and subtitle inputs."
            ),
            "why_next": (
                "It converts the current proof_missing readback into a concrete local "
                "render/proof receipt without crossing rights, network, or public gates."
            ),
            "validation": [
                "CLI exits 0 on fixture/local-material inputs.",
                "render/proof manifest keeps production_ready=false.",
                "HTML readback embeds or links only local diagnostic outputs.",
                "git ls-files episodes remains empty.",
            ],
        },
        "true_gates": [
            {
                "gate_id": "rights_and_publication_acceptance",
                "blocked_by_true_gate": True,
                "applies_to": ["production_render", "public_upload"],
                "reason": (
                    "Rights, publication judgment, account/OAuth, and public destination "
                    "are human-owned decisions."
                ),
                "evidence_path": "docs/AUTOMATION_BOUNDARY.md",
            },
            {
                "gate_id": "source_media_acquisition",
                "blocked_by_true_gate": False,
                "applies_to": ["local_diagnostic_proof"],
                "reason": (
                    "A later local-material slice can use operator-supplied files without "
                    "public acceptance."
                ),
                "evidence_path": "docs/SCHEMAS/v1/tiny_render.md",
            },
        ],
        "validation_plan": [
            "Run build-output-layer-gap-report and parse video_output_gap_log.json.",
            "Confirm every capability row carries the required OUT-01 fields.",
            "Confirm local_output_readback.html has no form, button, or video player.",
            "Run targeted pytest coverage for this generator and asset-fetch boundary smoke.",
            "Run git diff --check and confirm git ls-files episodes is empty.",
        ],
    }


def write_output_layer_gap_report(
    *,
    base_dir: Path,
    output_dir: Path,
    generated_at: str,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Write JSON, Markdown matrix, and HTML readback artifacts."""

    base_dir = base_dir.resolve()
    output_dir = _resolve_under_base(base_dir, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_output_layer_gap_report(
        base_dir=base_dir,
        generated_at=generated_at,
        artifact_id=artifact_id,
    )

    json_path = output_dir / "video_output_gap_log.json"
    matrix_path = output_dir / "output_capability_matrix.md"
    html_path = output_dir / "local_output_readback.html"

    _write_text_lf(
        json_path,
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(matrix_path, render_capability_matrix_markdown(report))
    _write_text_lf(html_path, render_local_output_readback_html(report))

    return {
        "report": report,
        "outputs": {
            "video_output_gap_log": _display_path(json_path, base_dir),
            "output_capability_matrix": _display_path(matrix_path, base_dir),
            "local_output_readback": _display_path(html_path, base_dir),
        },
    }


def render_capability_matrix_markdown(report: dict[str, Any]) -> str:
    """Render the capability matrix as reviewable Markdown."""

    lines = [
        "# OUT-01 Output Capability Matrix",
        "",
        (
            "Readback-only matrix for the output/video layer. This artifact does not "
            "fetch media, run render, or claim production readiness."
        ),
        "",
        f"- artifact_id: `{report['artifact_id']}`",
        f"- generated_at: `{report['generated_at']}`",
        f"- proof_status: `{report['proof_readback']['proof_status']}`",
        f"- production_ready: `{str(report['proof_readback']['production_ready']).lower()}`",
        f"- public_ready: `{str(report['proof_readback']['public_ready']).lower()}`",
        "",
        (
            "| capability_id | current_state | evidence_path | missing_input | "
            "next_local_action | blocked_by_true_gate | notes |"
        ),
        "|---|---|---|---|---|---|---|",
    ]
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
                "| gap_id | status | missing_input | local_vs_true_gate | "
                "suggested_next_slice | validation |"
            ),
            "|---|---|---|---|---|---|",
        ]
    )
    for gap in report["gap_log"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(gap["gap_id"]),
                    _md(gap["status"]),
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
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OUT-01 Local Output Readback</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f2;
      --text: #1c2430;
      --muted: #596575;
      --line: #cbd2d9;
      --accent: #006c67;
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
      letter-spacing: .04em;
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
      letter-spacing: .04em;
    }}
    .state-gated {{
      color: var(--gate);
      font-weight: 700;
    }}
    .state-absent, .status-proof_missing {{
      color: var(--warn);
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
    <h1>OUT-01 Local Output Readback</h1>
    <p>This static readback records output-layer capability and gaps without source fetching, media processing, production render, or public upload.</p>
    <section class="status-line" aria-label="readback status">
      <div><b>artifact</b><span>{escape(report['artifact_id'])}</span></div>
      <div><b>generated</b><span>{escape(report['generated_at'])}</span></div>
      <div><b>proof</b><span class="status-{escape(proof['proof_status'])}">{escape(proof['proof_status'])}</span></div>
      <div><b>production ready</b><span>{escape(str(proof['production_ready']).lower())}</span></div>
      <div><b>public ready</b><span>{escape(str(proof['public_ready']).lower())}</span></div>
    </section>
    <p>{escape(proof['reason'])}</p>

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


def _capability_rows(base_dir: Path) -> list[dict[str, Any]]:
    rows = [
        {
            "capability_id": "source_material_presence",
            "current_state": "absent",
            "evidence_path": "docs/RUNTIME_STATE.md",
            "missing_input": "Concrete local source_video/source_audio materials and ledger entries for a target episode.",
            "next_local_action": "Use a later approved local-material intake/proof slice with operator-supplied files.",
            "blocked_by_true_gate": False,
            "notes": "The current repo state can describe output gaps, but it has no tracked media to prove.",
        },
        {
            "capability_id": "transcript_readiness",
            "current_state": "local_ready",
            "evidence_path": "docs/SCHEMAS/v1/transcript.md",
            "missing_input": "A reviewed transcript for the target episode source audio.",
            "next_local_action": "Validate or create transcript.json from local audio/fixture, then review it before acceptance.",
            "blocked_by_true_gate": False,
            "notes": "Transcript schema and CLI paths exist; this OUT slice did not ingest media or make a transcript.",
        },
        {
            "capability_id": "edit_pack_readiness",
            "current_state": "local_ready",
            "evidence_path": "docs/SCHEMAS/v1/edit_pack.md",
            "missing_input": "An edit_pack connected to the reviewed transcript with selected cuts.",
            "next_local_action": "Generate/validate cut candidates and selected_cut_ids after transcript review.",
            "blocked_by_true_gate": False,
            "notes": "Editing artifacts are local diagnostics until human acceptance.",
        },
        {
            "capability_id": "subtitle_readiness",
            "current_state": "local_ready",
            "evidence_path": "src/cli/generate_subtitles.py",
            "missing_input": "Subtitle entries linked to selected cuts and reviewed for timing/text.",
            "next_local_action": "Generate subtitle drafts from transcript segments, then run review/proof readbacks.",
            "blocked_by_true_gate": False,
            "notes": "Subtitle generation can support local proof; it is not a publication decision.",
        },
        {
            "capability_id": "thumbnail_brief_readiness",
            "current_state": "planned",
            "evidence_path": "src/pipeline/episode_init_plan.py",
            "missing_input": "A concrete thumbnail brief artifact and selected source imagery/material refs.",
            "next_local_action": "Promote thumbnail brief seed fields into an operator-reviewable output-layer artifact.",
            "blocked_by_true_gate": False,
            "notes": "Planning code references thumbnail intent, but OUT has no current thumbnail proof surface.",
        },
        {
            "capability_id": "preview_pack_readiness",
            "current_state": "local_ready",
            "evidence_path": "docs/PREVIEW_PACK.md",
            "missing_input": "A target episode with local media or existing source audio material.",
            "next_local_action": "Build a read-only local preview pack once operator-supplied material exists.",
            "blocked_by_true_gate": False,
            "notes": "Preview pack is useful readback, but it is not a rendered video proof.",
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
            "missing_input": "Source video, source audio, edit_pack, selected cut, and optional subtitle source.",
            "next_local_action": "Run a narrow diagnostic proof only after local materials are explicitly available.",
            "blocked_by_true_gate": False,
            "notes": (
                "The code path exists for local diagnostics; OUT-01 created a no-media "
                "proof_missing readback instead."
            ),
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
        row["evidence_exists"] = (base_dir / row["evidence_path"]).exists()
    return rows


def _gap_rows() -> list[dict[str, str]]:
    return [
        {
            "gap_id": "gap_source_material_absent",
            "status": "gap",
            "evidence_path": "docs/RUNTIME_STATE.md",
            "missing_input": "No concrete local source_video/source_audio materials are present for this slice.",
            "why_it_matters": "Visible video proof cannot be produced or inspected without source media.",
            "local_vs_true_gate": "Local gap; operator-supplied files can unblock a diagnostic proof without public approval.",
            "suggested_next_slice": "OUT-02-local-fixture-output-proof-smoke",
            "validation": "A later proof run records source material ids and leaves git ls-files episodes empty.",
        },
        {
            "gap_id": "gap_current_no_proof_artifact",
            "status": "proof_missing",
            "evidence_path": "docs/SCHEMAS/v1/tiny_render.md",
            "missing_input": "No current portable render/proof manifest is available in tracked docs/artifacts.",
            "why_it_matters": "Reviewers can see readiness, but not inspect pixels/audio for a concrete episode yet.",
            "local_vs_true_gate": "Local gap; not a rights/publication gate while proof remains diagnostic.",
            "suggested_next_slice": "OUT-02-local-fixture-output-proof-smoke",
            "validation": "Generated proof manifest remains production_ready=false and public_ready=false.",
        },
        {
            "gap_id": "gap_thumbnail_brief_only_planned",
            "status": "gap",
            "evidence_path": "src/pipeline/episode_init_plan.py",
            "missing_input": "A reviewable thumbnail brief/output artifact tied to selected source materials.",
            "why_it_matters": "The output layer cannot compare video proof, title, and thumbnail intent as one package.",
            "local_vs_true_gate": "Local planning gap; final use still depends on human rights/creative acceptance.",
            "suggested_next_slice": "TH-OUT-thumbnail-brief-readback",
            "validation": "Brief JSON/HTML names source refs, intended crop/text, and acceptance boundaries.",
        },
        {
            "gap_id": "confirm_preview_pack_ready_not_video",
            "status": "confirmation",
            "evidence_path": "docs/PREVIEW_PACK.md",
            "missing_input": "A concrete local media target is still needed to run it.",
            "why_it_matters": "Preview pack can support review, but should not be mistaken for rendered video proof.",
            "local_vs_true_gate": "Local confirmation; no true gate unless public/production claims are added.",
            "suggested_next_slice": "SH-preview-pack-to-output-readback-link",
            "validation": "Preview report remains read-only and contains no public upload behavior.",
        },
        {
            "gap_id": "confirm_nle_export_ready_not_encoded_output",
            "status": "confirmation",
            "evidence_path": "docs/SCHEMAS/v1/nle_export.md",
            "missing_input": "An edit_pack with selected cuts for a real target episode.",
            "why_it_matters": "NLE export proves editorial structure but not final output render quality.",
            "local_vs_true_gate": "Local confirmation; production/public acceptance remains outside the export.",
            "suggested_next_slice": "EDIT-to-OUT-selected-cut-proof-link",
            "validation": "CSV/HTML readback points to selected cuts and keeps production flags false.",
        },
        {
            "gap_id": "gap_public_upload_true_gate",
            "status": "true_gate",
            "evidence_path": "docs/AUTOMATION_BOUNDARY.md",
            "missing_input": "Rights decision, publication approval, account/OAuth, and target channel.",
            "why_it_matters": "A local proof must not drift into public action or claim upload readiness.",
            "local_vs_true_gate": "True gate; local automation can only prepare review packets.",
            "suggested_next_slice": "PB-decision-packet-before-upload",
            "validation": "Upload/public fields stay blocked until human-owned acceptance is recorded.",
        },
        {
            "gap_id": "recommend_next_out_slice",
            "status": "recommendation",
            "evidence_path": "docs/SCHEMAS/v1/tiny_render.md",
            "missing_input": "A small approved local fixture/material bundle for a diagnostic proof run.",
            "why_it_matters": "It is the shortest route from readiness inventory to inspectable output evidence.",
            "local_vs_true_gate": "Local action; it should still avoid source fetching and public publication.",
            "suggested_next_slice": "OUT-02-local-fixture-output-proof-smoke",
            "validation": "Run targeted CLI/tests and attach generated proof readback to docs or artifacts.",
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


def _write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
