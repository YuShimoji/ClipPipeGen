"""Docs v1.5 dashboard builder.

The dashboard is intentionally static and repo-local: it helps operators find
the current wiki entry points, active artifacts, and docs that need tightening.
It does not inspect ignored episode media or make production/public claims.
"""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_ID = "clippipegen.docs_dashboard.v1_5"
DEFAULT_GENERATED_AT = "2026-07-01"
FINDING_DISPLAY_LIMIT = 50
FEATURE_DISPLAY_LIMIT = 120
REQUIRED_FRONT_SECTIONS = {
    "what_it_is": ("## What This Is", "## これは何か"),
    "current_state": ("## Current State", "## Current Capsule", "## 今の状態"),
    "next": ("## Next", "## これからどうなるか", "## 次に進める入口"),
    "constraints_risks": ("## Constraints / Risks", "## Constraints/Risks"),
}
BOUNDARY_TERMS = (
    "production",
    "rights",
    "publishing",
    "public use",
    "acceptance",
    "承認",
    "権利",
    "公開",
)
PRIORITY_DOCS = (
    Path("README.md"),
    Path("docs/index.md"),
    Path("docs/RUNTIME_STATE.md"),
    Path("docs/FEATURE_REGISTRY.md"),
    Path("docs/EPISODE_REVIEW_WORKFLOW.md"),
    Path("docs/OPERATOR_REVIEW_UX.md"),
    Path("docs/SUBTITLE_TYPOGRAPHY_DECORATION_COMPARISON.md"),
    Path("docs/SUBTITLE_STYLE_INTENT_REGISTRY.md"),
    Path("docs/REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md"),
    Path("artifacts/ARTIFACTS.md"),
)
STATUS_PROGRESS = {
    "done": 100,
    "successor-lane": 100,
    "in_progress": 70,
    "approved": 25,
    "hold": 25,
    "proposed": 0,
    "rejected": 0,
}
STATUS_HEALTH = {
    "done": "stable",
    "successor-lane": "superseded",
    "in_progress": "active",
    "approved": "ready",
    "hold": "blocked",
    "proposed": "backlog",
    "rejected": "retired",
}


CURRENT_CPD_OPERATOR_COCKPIT_ARTIFACT_ID = (
    "clip-cpd08-operator-home-funnel-meters-v0-001"
)


def _current_focus() -> dict[str, Any]:
    return {
        "feature_id": "CPD-08",
        "artifact_id": CURRENT_CPD_OPERATOR_COCKPIT_ARTIFACT_ID,
        "state": "content_planning_operator_home_ready",
        "title": "ClipPipeGen Operator Cockpit / Operator Home Funnel Meters v0",
        "human_entrypoint": "docs/content_planning/operator_cockpit.html",
        "machine_readback": "docs/content_planning/operator_cockpit.json",
        "handoff": "docs/CURRENT_HANDOFF.md",
        "notes": "docs/content_planning/README.md",
        "review_shape": "operator_home_then_single_source_identity_check",
        "source_backed_count": 1,
        "source_missing_count": 4,
        "source_missing_idea_backlog_count": 3,
        "blocked_or_hold_count": 1,
        "fetch_authorized_count": 0,
        "home_metric_count": 8,
        "funnel_stage_count": 5,
        "action_queue_count": 3,
        "source_backed_candidate_id": "cpd01_bancho_marine_misunderstanding",
        "source_backed_title": "番長、船長を完全に勘違いする",
        "source_url": "https://www.youtube.com/watch?v=7J5aS_pcBj4",
        "source_opened_by_worker": False,
        "gate_readback": {
            "network_required": False,
            "external_api_used": False,
            "media_downloaded": False,
            "episode_dirs_created": False,
            "fetch_authorized": False,
            "rights_approved": False,
            "production_ready": False,
            "public_ready": False,
        },
        "next_review_action_type": "INSPECT_SINGLE_SOURCE_BACKED_ITEM_OR_FILL_SOURCE_URLS",
        "next_action": (
            "Open docs/content_planning/operator_cockpit.html, read the Operator "
            "Home funnel meters and Action Queue, then inspect the one source "
            "identity card or add real source metadata before rerunning CPD-03 "
            "through CPD-08."
        ),
        "legacy_context": {
            "previous_focus_feature_id": "ED-10bc",
            "previous_focus_artifact_id": "clip-ed10bc-thank-v2-open-command-repair-readback-001",
            "previous_focus_state": "thank_v2_open_command_repair_ready",
        },
    }


def build_project_status(
    *,
    base_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
) -> dict[str, Any]:
    docs = _collect_docs(base_dir)
    all_findings = _doc_health_findings(docs)
    findings = all_findings[:FINDING_DISPLAY_LIMIT]
    features = _feature_rows(base_dir)
    artifacts = _artifact_rows(base_dir)
    current_focus = _current_focus()
    status = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v1.5",
        "generated_at": generated_at,
        "project": {
            "name": "ClipPipeGen",
            "wiki_entry": "docs/index.md",
            "dashboard_html": "docs/dashboard/index.html",
            "dashboard_json": "docs/dashboard/project-status.json",
        },
        "metadata_schema": {
            "doc_fields": [
                "path",
                "title",
                "line_count",
                "front_sections",
                "status",
            ],
            "finding_types": ["stale", "unclear", "over_guarded"],
            "boundary_policy": (
                "Production/public/rights caveats belong in Constraints / Risks "
                "instead of being repeated as the opening sentence of every doc."
            ),
        },
        "current_focus": current_focus,
        "open_surfaces": _open_surfaces(),
        "wiki_entrypoints": _wiki_entrypoints(),
        "features": features,
        "feature_summary": _feature_summary(features),
        "active_artifacts": artifacts,
        "artifact_summary": _artifact_summary(artifacts),
        "artifact_coverage": _artifact_coverage(
            features,
            artifacts,
            current_focus["artifact_id"],
        ),
        "next_review_items": _next_review_items(),
        "docs": docs,
        "doc_health": {
            "finding_count": len(findings),
            "finding_total": len(all_findings),
            "finding_limit": FINDING_DISPLAY_LIMIT,
            "findings_truncated": len(all_findings) > FINDING_DISPLAY_LIMIT,
            "findings": findings,
        },
        "top_next_improvements": _top_next_improvements(),
    }
    return status


def write_project_status(
    *,
    base_dir: Path,
    output_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
) -> dict[str, Any]:
    status = build_project_status(base_dir=base_dir, generated_at=generated_at)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "project-status.json"
    html_path = output_dir / "index.html"
    features_path = output_dir.parent / "features" / "index.md"
    _write_text_lf(
        json_path,
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
    )
    _write_text_lf(html_path, render_dashboard_html(status))
    features_path.parent.mkdir(parents=True, exist_ok=True)
    _write_text_lf(features_path, render_features_index_markdown(status))
    return {
        "status": status,
        "json_path": json_path,
        "html_path": html_path,
        "features_path": features_path,
    }


def render_dashboard_html(status: dict[str, Any]) -> str:
    focus = status["current_focus"]
    findings = status["doc_health"]["findings"]
    docs = status["docs"]
    focus_rows = _current_focus_table_rows(focus)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>ClipPipeGen Docs Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; line-height: 1.5; color: #20242a; }}
    table {{ border-collapse: collapse; table-layout: fixed; width: 100%; margin: 12px 0 24px; }}
    th, td {{ border: 1px solid #c8d0d9; padding: 8px; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ background: #edf2f7; text-align: left; }}
    .status {{ display: inline-block; padding: 2px 6px; border: 1px solid #9eb3c7; background: #f4f8fb; }}
    .warn {{ color: #7a4100; }}
    code {{ background: #f3f3f3; padding: 1px 4px; white-space: normal; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>ClipPipeGen Docs Dashboard</h1>
  <p>Generated from <code>{escape(status["schema_id"])}</code> at {escape(status["generated_at"])}.</p>
  <section>
    <h2>Current Focus</h2>
    <p><span class="status">{escape(focus["state"])}</span></p>
    <table>{focus_rows}</table>
  </section>
  <section>
    <h2>Open Surfaces</h2>
    <p>Normal order: run <code>.\\open-dashboard.ps1</code>, choose an artifact, then use an artifact-specific launcher only when needed.</p>
    {_open_surfaces_table_html(status["open_surfaces"])}
  </section>
  <section>
    <h2>Feature Progress</h2>
    {_features_table_html(status["features"])}
  </section>
  <section>
    <h2>Active Artifacts</h2>
    {_artifacts_table_html(status["active_artifacts"])}
    <p>Artifact coverage: {escape(str(status["artifact_coverage"]["features_with_artifact_count"]))} feature rows mention registered artifacts; current focus artifact registered={escape(str(status["artifact_coverage"]["current_focus_artifact_registered"]).lower())}.</p>
  </section>
  <section>
    <h2>Next Review Items</h2>
    {_review_items_table_html(status["next_review_items"])}
  </section>
  <section>
    <h2>Wiki Entrypoints</h2>
    {_entrypoint_list_html(status["wiki_entrypoints"])}
  </section>
  <section>
    <h2>Doc Health Findings</h2>
    <p class="warn">{len(findings)} of {escape(str(status["doc_health"]["finding_total"]))} stale / unclear / over-guarded findings shown.</p>
    {_findings_table_html(findings)}
  </section>
  <section>
    <h2>Tracked Docs</h2>
    {_docs_table_html(docs)}
  </section>
  <section>
    <h2>Next Improvements</h2>
    {_improvements_table_html(status["top_next_improvements"])}
  </section>
</body>
</html>
"""


def _current_focus_table_rows(focus: dict[str, Any]) -> str:
    rows = [
        ("feature", focus.get("feature_id", "")),
        ("artifact", focus.get("artifact_id", "")),
        ("entrypoint", focus.get("human_entrypoint", "")),
        ("machine readback", focus.get("machine_readback", "")),
        ("review shape", focus.get("review_shape", "")),
        ("known source", focus.get("source_backed_title", "")),
        ("source URL", focus.get("source_url", "")),
        (
            "source-backed / missing",
            f'{focus.get("source_backed_count", "")} / {focus.get("source_missing_count", "")}',
        ),
        ("next review", focus.get("next_review_action_type", "")),
        ("next action", focus.get("next_action", "")),
    ]
    gates = focus.get("gate_readback")
    if isinstance(gates, dict):
        gate_text = "; ".join(
            f"{key}={str(value).lower()}" for key, value in gates.items()
        )
        rows.append(("gates", gate_text))
    return "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>"
        for label, value in rows
    )


def _write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def render_features_index_markdown(status: dict[str, Any]) -> str:
    rows = [
        "| id | title | status | health | progress_pct | active_artifact | next_action |",
        "|---|---|---|---|---:|---|---|",
    ]
    for feature in status["features"]:
        rows.append(
            "| "
            + " | ".join(
                [
                    _md(feature["id"]),
                    _md(feature["title"]),
                    _md(feature["status"]),
                    _md(feature["health"]),
                    str(feature["progress_pct"]),
                    _md(feature.get("active_artifact") or ""),
                    _md(feature["next_action"]),
                ]
            )
            + " |"
        )
    return (
        "# Feature Dashboard\n\n"
        "This generated index is the scan-friendly v1.5 view of "
        "[../FEATURE_REGISTRY.md](../FEATURE_REGISTRY.md). Edit the registry "
        "or dashboard builder, then regenerate instead of hand-editing this "
        "table.\n\n"
        "## Current Focus\n\n"
        f"- feature: `{status['current_focus']['feature_id']}`\n"
        f"- artifact: `{status['current_focus']['artifact_id']}`\n"
        f"- state: `{status['current_focus']['state']}`\n\n"
        "## Feature Table\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _collect_docs(base_dir: Path) -> list[dict[str, Any]]:
    paths = list(PRIORITY_DOCS)
    paths.extend(sorted(Path("docs").glob("*.md")))
    seen: set[str] = set()
    docs: list[dict[str, Any]] = []
    for relative in paths:
        key = str(relative).replace("\\", "/")
        if key in seen:
            continue
        seen.add(key)
        path = base_dir / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        front_matter = _front_matter(text)
        docs.append(
            {
                "path": key,
                "title": _title(text, fallback=relative.stem),
                "line_count": len(text.splitlines()),
                "metadata": front_matter,
                "front_sections": _front_sections(text),
                "boundary_term_count": _boundary_term_count(text),
                "status": front_matter.get("status") or _doc_status(text),
            }
        )
    return docs


def _front_sections(text: str) -> dict[str, bool]:
    return {
        key: any(marker in text for marker in markers)
        for key, markers in REQUIRED_FRONT_SECTIONS.items()
    }


def _doc_health_findings(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for doc in docs:
        missing = [
            key for key, exists in doc["front_sections"].items() if exists is not True
        ]
        if missing and doc["path"] in {str(path).replace("\\", "/") for path in PRIORITY_DOCS}:
            findings.append(
                {
                    "type": "unclear",
                    "path": doc["path"],
                    "detail": "Missing v1.5 front sections: " + ", ".join(missing),
                    "suggested_fix": "Add What This Is / Current State / Next / Constraints / Risks before historical detail.",
                }
            )
        if doc["line_count"] > 450 and doc["path"] != "docs/RUNTIME_HISTORY.md":
            findings.append(
                {
                    "type": "stale",
                    "path": doc["path"],
                    "detail": f"Long active doc ({doc['line_count']} lines) is likely carrying history.",
                    "suggested_fix": "Move older closeouts to archive/history and keep this page as a pointer or dashboard surface.",
                }
            )
        if doc["boundary_term_count"] >= 18 and not doc["front_sections"].get(
            "constraints_risks"
        ):
            findings.append(
                {
                    "type": "over_guarded",
                    "path": doc["path"],
                    "detail": f"Boundary terms appear {doc['boundary_term_count']} times without a front Constraints / Risks section.",
                    "suggested_fix": "Collect repeated caveats into Constraints / Risks and keep the opening action-oriented.",
                }
            )
    return findings


def _feature_rows(base_dir: Path) -> list[dict[str, Any]]:
    path = base_dir / "docs/FEATURE_REGISTRY.md"
    if not path.exists():
        return []
    features: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] in {"ID", "---"}:
            continue
        feature_id = _clean_markdown(cells[0])
        if feature_id in seen or "-" not in feature_id:
            continue
        seen.add(feature_id)
        title = _clean_markdown(cells[1])
        status = _clean_markdown(cells[2])
        summary = _clean_markdown(cells[3])
        active_artifact = _first_artifact_id(cells[3])
        if feature_id == "ED-10g":
            active_artifact = "clip-ed10g-noto-overlay-proof-001"
        if feature_id == "ED-10i":
            active_artifact = "clip-ed10i-meiryo-overlay-proof-001"
        if feature_id == "ED-10j":
            active_artifact = "clip-ed10j-kirinuki-font-audit-001"
        if feature_id == "ED-10k":
            active_artifact = "clip-ed10k-biz-overlay-proof-001"
        if feature_id == "ED-10l":
            active_artifact = "clip-ed10l-known-kirinuki-font-pack-001"
        if feature_id == "ED-10m":
            active_artifact = "clip-ed10l-known-kirinuki-font-pack-001"
        if feature_id == "ED-10n":
            active_artifact = "clip-ed10n-keifont-overlay-proof-001"
        if feature_id == "ED-10o":
            active_artifact = "clip-ed10o-multifont-focused-review-001"
        if feature_id == "ED-10p":
            active_artifact = "clip-ed10p-keifont-lead-representative-proof-001"
        if feature_id == "ED-10q":
            active_artifact = "clip-ed10p-keifont-lead-representative-proof-001"
        if feature_id == "ED-10r":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10t":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10u":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10v":
            active_artifact = "clip-ed10r-keifont-dense-stress-proof-001"
        if feature_id == "ED-10w":
            active_artifact = "clip-ed10w-subtitle-presentation-review-pack-001"
        if feature_id == "ED-10y":
            active_artifact = "clip-ed10y-candidate2-carry-forward-001"
        if feature_id == "ED-10z":
            active_artifact = "clip-ed10z-tiny-render-path-nearer-probe-001"
        if feature_id == "ED-10aa":
            active_artifact = "clip-ed10aa-subtitle-style-intent-registry-001"
        if feature_id == "ED-10ab":
            active_artifact = "clip-ed10ab-subtitle-preset-selector-001"
        if feature_id == "ED-10ac":
            active_artifact = "clip-ed10ac-visual-selector-proof-001"
        if feature_id == "ED-10ad":
            active_artifact = "clip-ed10ad-style-family-palette-axis-proof-001"
        if feature_id == "ED-10ae":
            active_artifact = "clip-ed10ae-render-path-selector-contract-probe-001"
        if feature_id == "ED-10af":
            active_artifact = "clip-ed10af-l2-render-path-selector-probe-001"
        if feature_id == "ED-10ag":
            active_artifact = "clip-ed10ag-lineage-and-observation-surface-001"
        if feature_id == "ED-10ah":
            active_artifact = "clip-ed10ah-production-limitation-lift-entry-001"
        if feature_id == "ED-10ai":
            active_artifact = "clip-ed10ai-final-render-path-readiness-packet-001"
        if feature_id == "ED-10aj":
            active_artifact = "clip-ed10aj-final-render-path-stage-1-001"
        if feature_id == "ED-10ak":
            active_artifact = "clip-ed10ak-final-render-path-stage-2-replayability-001"
        if feature_id == "ED-10al":
            active_artifact = "clip-ed10al-final-render-path-stage-3-rehearsal-001"
        if feature_id == "ED-10am":
            active_artifact = "clip-ed10am-production-limitation-lift-stage-1-001"
        if feature_id == "ED-10an":
            active_artifact = "clip-ed10an-production-limitation-lift-stage-2-decision-packet-001"
        if feature_id == "ED-10ao":
            active_artifact = "clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001"
        if feature_id == "ED-10ap":
            active_artifact = "clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001"
        if feature_id == "ED-10aq":
            active_artifact = "clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001"
        if feature_id == "ED-10ar":
            active_artifact = "clip-ed10ar-internal-review-video-candidate-package-001"
        if feature_id == "ED-10as":
            active_artifact = "clip-ed10as-internal-review-access-sheet-fullpath-001"
        if feature_id == "ED-10at":
            active_artifact = "clip-ed10at-internal-review-observation-readback-001"
        if feature_id == "ED-10au":
            active_artifact = "clip-ed10au-representative-micro-scene-internal-review-specimen-001"
        if feature_id == "ED-10av":
            active_artifact = "clip-ed10av-micro-scene-observation-frame-readback-001"
        if feature_id == "ED-10aw":
            active_artifact = "clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001"
        if feature_id == "ED-10ax":
            active_artifact = "clip-ed10ax-review-frame-clarification-surface-001"
        if feature_id == "ED-10ay":
            active_artifact = "clip-ed10ay-thank-ed10au-local-access-recovery-readback-001"
        if feature_id == "ED-10az":
            active_artifact = "clip-ed10az-observation-readback-and-v2-route-decision-001"
        if feature_id == "ED-10ba":
            active_artifact = "clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001"
        if feature_id == "ED-10bb":
            active_artifact = "clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001"
        if feature_id == "ED-10bc":
            active_artifact = "clip-ed10bc-thank-v2-open-command-repair-readback-001"
        features.append(
            {
                "id": feature_id,
                "title": title,
                "status": status,
                "health": _feature_health(feature_id, status, summary),
                "progress_pct": _feature_progress(feature_id, status),
                "active_artifact": active_artifact,
                "next_action": _feature_next_action(feature_id, status, summary),
                "summary_excerpt": _truncate(summary, 220),
                "source_path": "docs/FEATURE_REGISTRY.md",
            }
        )
    return features[:FEATURE_DISPLAY_LIMIT]


def _feature_summary(features: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for feature in features:
        status = feature["status"]
        counts[status] = counts.get(status, 0) + 1
    return {"feature_count": len(features), "status_counts": counts}


def _artifact_rows(base_dir: Path) -> list[dict[str, Any]]:
    path = base_dir / "artifacts/ARTIFACTS.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## `([^`]+)`\s*$", text, flags=re.MULTILINE))
    rows: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        fields = _artifact_fields(block)
        rows.append(
            {
                "artifact_id": match.group(1),
                "title": fields.get("title", ""),
                "purpose": fields.get("purpose", ""),
                "storage_class": fields.get("storage class", ""),
                "repo_relative_path": fields.get("repo_relative_path", ""),
                "open_command": fields.get("open_command", ""),
                "review_status": fields.get("review_status", ""),
                "next_action": fields.get("next_action", ""),
            }
        )
    return rows


def _artifact_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [artifact["artifact_id"] for artifact in artifacts]
    return {"artifact_ids": ids, "artifact_count": len(ids)}


def _artifact_coverage(
    features: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    current_focus_artifact_id: str,
) -> dict[str, Any]:
    artifact_ids = {artifact["artifact_id"] for artifact in artifacts}
    mentioned = [
        feature for feature in features if feature.get("active_artifact") in artifact_ids
    ]
    current_focus_registered = current_focus_artifact_id in artifact_ids
    return {
        "registered_artifact_count": len(artifact_ids),
        "features_with_artifact_count": len(mentioned),
        "current_focus_artifact_registered": current_focus_registered,
        "missing_registered_artifact_mentions": [
            feature["id"]
            for feature in features
            if feature.get("active_artifact")
            and feature.get("active_artifact") not in artifact_ids
        ],
    }


def _wiki_entrypoints() -> list[dict[str, str]]:
    return [
        {
            "path": "docs/index.md",
            "role": "Human-readable wiki front door.",
        },
        {
            "path": "docs/features/index.md",
            "role": "Generated feature progress table.",
        },
        {
            "path": "docs/dashboard/index.html",
            "role": "Status dashboard generated from project metadata.",
        },
        {
            "path": "docs/RUNTIME_STATE.md",
            "role": "Current resume capsule and next action.",
        },
        {
            "path": "artifacts/ARTIFACTS.md",
            "role": "Reviewable local artifact registry.",
        },
        {
            "path": "docs/FEATURE_REGISTRY.md",
            "role": "Feature status authority.",
        },
    ]


def _next_review_items() -> list[dict[str, str]]:
    return [

        {
            "item": "CPD-08 operator home / source identity review",
            "artifact": CURRENT_CPD_OPERATOR_COCKPIT_ARTIFACT_ID,
            "question": "Does the Operator Home clearly show the single source-backed item, and does that source match the Bancho/Marine misunderstanding candidate?",
            "next_route": "Open docs/content_planning/operator_cockpit.html first; unresolved CPD ideas need real source URL/metadata intake before fetch/init/transcript/edit/render work.",
        },
        {
            "item": "ED-10bc Thank v2 opener repair",
            "artifact": "clip-ed10bc-thank-v2-open-command-repair-readback-001",
            "question": "If a later review is requested, does the repaired opener or -SelectVideo fallback make the already verified ED-10ba v2 specimen visible without implying approval?",
            "next_route": "Run the repaired opener only under a later freeform review request; classify any remaining failure as player/file-association visibility before considering media regeneration.",
        },
        {
            "item": "ED-10bb Thank ED-10ba v2 access recovery",
            "artifact": "clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001",
            "question": "If a later review is requested, does the regenerated Thank-host ED-10ba v2 specimen make cut-window and clipping/cutout review easier without implying approval?",
            "next_route": "Open the verified Thank-host v2 specimen only under a later freeform review request; do not regenerate unless the ignored outputs disappear again.",
        },
        {
            "item": "ED-10ba representative micro-scene v2 cut-window review",
            "artifact": "clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001",
            "question": "Does the v2 specimen make the cut window and clipping/cutout review purpose easier to judge than ED-10au, without treating it as approval?",
            "next_route": "Use later freeform v2 review only if needed; keep screenshot capture, timing/audio, and final-render-path stage-4 conditional.",
        },
        {
            "item": "ED-10ax review-frame clarification surface",
            "artifact": "clip-ed10ax-review-frame-clarification-surface-001",
            "question": "Does the surface make clear what the ED-10au specimen asks a later reviewer to judge, without turning the observation into approval or asking for a fixed form?",
            "next_route": "Keep as consumed review-frame source for ED-10ba; capture layout evidence or open final-render-path-stage-4 only when the specific condition is met.",
        },
        {
            "item": "ED-10aw Grill-me adoption and review-frame clarification plan",
            "artifact": "clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001",
            "question": "Does the plan keep Grill-me as a bounded local helper, forbid nested prompts, and make review-frame clarification the first default without creating media or approval?",
            "next_route": "Use review-frame-clarification first; capture layout evidence, build v2, or open final-render-path-stage-4 only when the specific condition is met.",
        },
        {
            "item": "ED-10av micro-scene observation frame readback",
            "artifact": "clip-ed10av-micro-scene-observation-frame-readback-001",
            "question": "Does the readback preserve the freeform observation as openability/content pass, expectation/review-frame warning, and unverified subtitle/player-UI overlap risk without inferring approval?",
            "next_route": "Clarify the review frame first; capture subtitle/player-UI evidence only if needed, and use v2 or final-render-path-stage-4 only for concrete source/layout/render gaps.",
        },
        {
            "item": "ED-10au representative micro-scene internal review specimen",
            "artifact": "clip-ed10au-representative-micro-scene-internal-review-specimen-001",
            "question": "Does the source specimen remain the access-verified real-scene input consumed by ED-10av?",
            "next_route": "Keep as source evidence; do not treat ED-10av observation as approval or rerender unless a later axis proves it is needed.",
        },
        {
            "item": "ED-10at internal review observation readback",
            "artifact": "clip-ed10at-internal-review-observation-readback-001",
            "question": "Does the readback preserve the user's observation that the MP4 opened, cue labels were visible, duration matched, but the video felt chopped together, memo-like, and hard to evaluate?",
            "next_route": "If real internal review continues, build a representative micro-scene specimen with actual subtitle/script content; use final-render-path-stage-4 only for a concrete render diagnostic gap.",
        },
        {
            "item": "ED-10as internal review access sheet fullpath",
            "artifact": "clip-ed10as-internal-review-access-sheet-fullpath-001",
            "question": "Does the sheet provide exact current-host paths and a launcher without creating render, replay, or production/public approval?",
            "next_route": "Use the launcher only for a later optional freeform observation; keep production/public/rights approvals pending.",
        },
        {
            "item": "ED-10ar internal review video candidate package",
            "artifact": "clip-ed10ar-internal-review-video-candidate-package-001",
            "question": "Does the package point to existing ignored MP4/ASS/manifest output while keeping production/public/rights approval false or pending?",
            "next_route": "Use optional-internal-review-video-observation only for a later freeform observation; use final-render-path-stage-4 only for a concrete diagnostic gap.",
        },
        {
            "item": "ED-10aq stage-5 user-decision-ready",
            "artifact": "clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001",
            "question": "Does ED-10ap remain a freeform owner decision card with no fixed form, no immediate user decision, and no production/public approval?",
            "next_route": "Treat ED-10aq as a gate sanity packet only; use final-render-path-stage-4 only if a concrete diagnostic gap is found.",
        },
        {
            "item": "ED-10ao production limitation-lift stage 3 owner-review prep",
            "artifact": "clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001",
            "question": "Does the packet convert ED-10an's three decision groups into future freeform user-decision topics while keeping all production/public approvals closed?",
            "next_route": "Start production-limitation-lift-stage-4-user-decision-card, or use final-render-path-stage-4 only if a concrete diagnostic gap is found.",
        },
        {
            "item": "ED-10an production limitation-lift stage 2 decision packet",
            "artifact": "clip-ed10an-production-limitation-lift-stage-2-decision-packet-001",
            "question": "Does the packet group the ED-10am gate matrix into no more than three decision-preparation groups while keeping all production/public approvals closed?",
            "next_route": "Start production-limitation-lift-stage-3-owner-review-prep, or use final-render-path-stage-4 only if a concrete diagnostic gap is found.",
        },
        {
            "item": "ED-10am production limitation-lift stage 1",
            "artifact": "clip-ed10am-production-limitation-lift-stage-1-001",
            "question": "Does the packet separate ED-10al diagnostic rehearsal evidence from production subtitle design, production render, creative, rights, publishing, public-use, tracked media, and same-machine ignored-evidence gates?",
            "next_route": "Start production-limitation-lift-stage-2-decision-packet, or use final-render-path-stage-4 only if more diagnostic evidence is genuinely needed.",
        },
        {
            "item": "ED-10al final render-path stage 3 diagnostic rehearsal",
            "artifact": "clip-ed10al-final-render-path-stage-3-rehearsal-001",
            "question": "Does the rehearsal record the selected FFmpeg/libass diagnostic path, tracked inputs, same-machine source inputs, generated ignored ASS/MP4/manifest outputs, output metadata, style-token survival, and closed production/public gates?",
            "next_route": "Start production-limitation-lift-stage-1 or final-render-path-stage-4 from this rehearsal packet; do not infer production/public approval.",
        },
        {
            "item": "ED-10ak final render-path stage 2 replayability",
            "artifact": "clip-ed10ak-final-render-path-stage-2-replayability-001",
            "question": "Does the replayability packet define the selected FFmpeg/libass diagnostic path, required tracked and same-machine inputs, ignored outputs, command family, readback commands, fresh-clone absence behavior, and closed production/public gates?",
            "next_route": "Start final-render-path-stage-3 or production-limitation-lift-stage-1 from this packet; do not infer production/public approval.",
        },
        {
            "item": "ED-10aj final render-path stage 1",
            "artifact": "clip-ed10aj-final-render-path-stage-1-001",
            "question": "Does the stage-1 packet select the FFmpeg/libass diagnostic path while keeping production, creative, rights, publishing, and public-use gates closed?",
            "next_route": "Start final-render-path-stage-2 or production-limitation-lift-stage-1 from this selected path; do not infer production/public approval.",
        },
        {
            "item": "ED-10ai final render-path readiness packet",
            "artifact": "clip-ed10ai-final-render-path-readiness-packet-001",
            "question": "Does the packet separate available diagnostic/render-contract evidence from still-missing production, creative, rights, publishing, and public-use decisions?",
            "next_route": "Start final-render-path-stage-1 or production-limitation-lift-stage-1 from this readiness matrix; do not infer production/public approval.",
        },
        {
            "item": "ED-10ah render readiness separation readback",
            "artifact": "clip-ed10ah-render-readiness-separation-readback-001",
            "question": "Is ED-10ag limited to connecting dry-read coverage with existing L2 diagnostic readback while production, rights, publishing, public-use, and final style acceptance stay closed?",
            "next_route": "Use this readback before a later explicit final-render-path-readiness or production-limitation-lift-stage-1 milestone; do not render in the current cleanup slice.",
        },
        {
            "item": "ED-10ah production limitation-lift entry",
            "artifact": "clip-ed10ah-production-limitation-lift-entry-001",
            "question": "Are diagnostic proof, production subtitle design, production render, creative, rights, publishing, and public-use gates separated before the next route starts?",
            "next_route": "Start production-limitation-lift-stage-1 or final-render-path-readiness from this gate matrix; do not infer production/public approval.",
        },
        {
            "item": "ED-10ag lineage and observation surface",
            "artifact": "clip-ed10ag-lineage-and-observation-surface-001",
            "question": "Does the restored ED-10af dry-read remain preserved as predecessor evidence while the active ED-10af L2 selector probe keeps its observation paths?",
            "next_route": "Use this surface to inspect lineage and same-machine proof paths; keep production, rights, publishing, and public-use routes separate.",
        },
        {
            "item": "ED-10af L2 render path selector probe",
            "artifact": "clip-ed10af-l2-render-path-selector-probe-001",
            "question": "Do normal dialogue, shout, and whisper examples from the ED-10ae contract survive a tiny FFmpeg/libass render-path probe with stable body text and badge/accent/backplate routing?",
            "next_route": "Use this L2 diagnostic probe as render-path readback; do not infer production render or public-use readiness.",
        },
        {
            "item": "ED-10ae render-path selector contract",
            "artifact": "clip-ed10ae-render-path-selector-contract-probe-001",
            "question": "Are selector, family, palette, color-surface, motion, and line-break fields ready as a static input contract before any render probe?",
            "next_route": "Use this contract before a later L2 render-path probe; do not infer actual render or production readiness.",
        },
        {
            "item": "ED-10ad style-family / palette axis proof",
            "artifact": "clip-ed10ad-style-family-palette-axis-proof-001",
            "question": "Can the six semantic presets be grouped by style family and palette route while body text color stays stable?",
            "next_route": "Use this static axis proof before any later render-path probe or separate style-family, palette, production, rights, publishing, or public-use route.",
        },
        {
            "item": "ED-10ac visual selector proof",
            "artifact": "clip-ed10ac-visual-selector-proof-001",
            "question": "Can the six semantic preset examples be inspected as badge/accent/backplate/size/motion/line-break differences while body text color stays stable?",
            "next_route": "Use this static proof for optional open-only observation before opening any new style-family, palette, production, rights, publishing, or public-use route.",
        },
        {
            "item": "ED-10ab subtitle preset selector",
            "artifact": "clip-ed10ab-subtitle-preset-selector-001",
            "question": "Can the six semantic intent axes map deterministically to style token candidates without raw numeric review?",
            "next_route": "Use as source selector for ED-10ac and future visual style proof work.",
        },
        {
            "item": "ED-10aa subtitle style intent registry",
            "artifact": "clip-ed10aa-subtitle-style-intent-registry-001",
            "question": "Can future subtitle styling map speaker/emotion/readability tags to presets without asking for tiny numeric adjustments?",
            "next_route": "Use as source registry for ED-10ab; ED-10z already has refreshed same-machine local readback.",
        },
        {
            "item": "ED-10z tiny render-path-nearer probe",
            "artifact": "clip-ed10z-tiny-render-path-nearer-probe-001",
            "question": "Has Candidate 2 been passed through the current diagnostic render path without reopening the Candidate 0-3 comparison?",
            "next_route": "Use the probe as local readback only; open production limitation-lift or final render-path work as a separate route.",
        },
        {
            "item": "ED-10v dense/stress pass and line-break policy readback",
            "artifact": "clip-ed10r-keifont-dense-stress-proof-001",
            "question": "Is the ED-10u cut_008 multiline/dense-stress pass preserved as prior state?",
            "next_route": "Use as source evidence only; ED-10z owns the current tiny render-path-nearer readback.",
        },
        {
            "item": "ED-10p Keifont representative proof baseline",
            "artifact": "clip-ed10p-keifont-lead-representative-proof-001",
            "question": "Is the ED-10n/ED-10o Keifont review history recorded as consumed rather than reopened?",
            "next_route": "Use as diagnostic representative normal-dialogue provisional baseline; do not request another general cut_002/cut_003 Keifont acceptance review.",
        },
        {
            "item": "ED-10o multi-font focused review reference",
            "artifact": "clip-ed10o-multifont-focused-review-001",
            "question": "Does the accepted focused review surface remain useful as the historical comparison reference?",
            "next_route": "Use the same-line matrix as reference only; it does not by itself approve a final baseline or production use.",
        },
        {
            "item": "ED-10n Keifont overlay proof",
            "artifact": "clip-ed10n-keifont-overlay-proof-001",
            "question": "Does the earlier Keifont overlay proof remain consistent with the provisional baseline record?",
            "next_route": "Use as consumed historical proof reference; ED-10r is now the current review entry.",
        },
        {
            "item": "ED-10l real-font comparison readback",
            "artifact": "clip-ed10l-known-kirinuki-font-pack-001",
            "question": "Does the real-font contact sheet confirm the per-user font resolver is using requested fonts rather than fallback?",
            "next_route": "Use the comparison only as readback support for the Keifont proof route unless another candidate must be promoted.",
        },
        {
            "item": "ED-10k BIZ UDGothic overlay proof",
            "artifact": "clip-ed10k-biz-overlay-proof-001",
            "question": "Was BIZ correctly kept as a reviewed rejected reference instead of the normal-dialogue baseline?",
            "next_route": "Use only as reference evidence for why the system-safe route was stopped.",
        },
        {
            "item": "ED-10j kirinuki font audit",
            "artifact": "clip-ed10j-kirinuki-font-audit-001",
            "question": "Was the no-download audit consumed correctly, including Meiryo reference demotion and BIZ default selection?",
            "next_route": "Use the manifest readback only for audit; do not prolong the comparison unless the BIZ proof fails.",
        },
        {
            "item": "ED-10h font candidate sweep",
            "artifact": "clip-subtitle-font-candidate-sweep-001",
            "question": "Should Google Fonts / OFL candidates be downloaded or only compared when already local?",
            "next_route": "Use the candidate registry before any font binary enters Git.",
        },
        {
            "item": "Docs v1.5 cleanup",
            "artifact": "docs/dashboard/project-status.json",
            "question": "Which high-friction doc should be shortened or front-mattered next?",
            "next_route": "Use doc-health findings instead of hand-scanning Markdown history.",
        },
    ]


def _top_next_improvements() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "path": "docs/HANDOFF.md",
            "why": "Long historical handoff still competes with the active wiki/dashboard entry.",
            "next_move": "Convert it to a short pointer and archive the remaining history.",
        },
        {
            "rank": 2,
            "path": "artifacts/ARTIFACTS.md",
            "why": "The registry is the active artifact map but still lacks v1.5 front sections.",
            "next_move": "Add What This Is / Current State / Next / Constraints before older artifact detail.",
        },
        {
            "rank": 3,
            "path": "docs/FEATURE_REGISTRY.md",
            "why": "Feature rows are authoritative but hard to scan as a wiki page.",
            "next_move": "Generate per-feature pages from docs/_templates/feature.md.",
        },
    ]


def _open_surfaces() -> list[dict[str, str]]:
    return [
        {
            "label": "Dashboard",
            "command": ".\\open-dashboard.ps1",
            "target": "docs/dashboard/index.html",
            "when_to_use": "Start here for current focus, feature progress, active artifacts, and doc-health findings.",
        },
        {
            "label": "CPD Operator Cockpit",
            "command": "start docs\\content_planning\\operator_cockpit.html",
            "target": "docs/content_planning/operator_cockpit.html",
            "when_to_use": "Use first for current CPD review; it shows the one source-backed item and keeps missing-source ideas out of the video-candidate path.",
        },
        {
            "label": "Artifacts",
            "command": ".\\open-artifacts.ps1",
            "target": "artifacts/ARTIFACTS.md",
            "when_to_use": "Use after the dashboard when an artifact needs its registry entry or open command.",
        },
        {
            "label": "Thank V2 Open Command Repair Readback",
            "command": "see docs\\style_intent\\thank-v2-open-command-repair-readback.md",
            "target": "docs/style_intent/thank-v2-open-command-repair-readback.md",
            "when_to_use": (
                "Use after ED-10bc when the ED-10ba v2 MP4 exists but the "
                "default opener did not appear visibly; includes -SelectVideo "
                "and path-only diagnostics."
            ),
        },
        {
            "label": "Thank ED-10ba V2 Access Recovery Readback",
            "command": "see docs\\style_intent\\thank-ed10ba-v2-local-access-recovery-readback.md",
            "target": "docs/style_intent/thank-ed10ba-v2-local-access-recovery-readback.md",
            "when_to_use": (
                "Use after ED-10bb when a later supervisor asks to open the "
                "verified Thank-host v2 specimen."
            ),
        },
        {
            "label": "Representative Micro-Scene V2 Readback",
            "command": "see docs\\style_intent\\representative-micro-scene-v2-cut-window-and-review-purpose-alignment.md",
            "target": "docs/style_intent/representative-micro-scene-v2-cut-window-and-review-purpose-alignment.md",
            "when_to_use": (
                "Use to inspect the ED-10ba v2 specimen: why the source window "
                "changed to 38.50-50.40s, how the purpose label is diagnostic, "
                "and which approval/render gates remain closed."
            ),
        },
        {
            "label": "Open Representative Micro-Scene V2",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1",
            "target": "scripts/operator/open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1",
            "when_to_use": (
                "Use later only when a supervisor asks to open the ED-10ba "
                "internal review v2 MP4; run -SelectVideo or -PrintPath if "
                "the default player does not appear visibly."
            ),
        },
        {
            "label": "Review-Frame Clarification Surface",
            "command": "see docs\\style_intent\\review-frame-clarification-surface.md",
            "target": "docs/style_intent/review-frame-clarification-surface.md",
            "when_to_use": (
                "Use to inspect the ED-10ax surface: what the ED-10au specimen "
                "asks a later reviewer to judge, what it is not asking, and "
                "which next axis should be used without a default rerender."
            ),
        },
        {
            "label": "Grill-me Adoption and Review-Frame Plan",
            "command": "see docs\\style_intent\\grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md",
            "target": "docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md",
            "when_to_use": (
                "Use to inspect the ED-10aw plan: Grill-me is a bounded local "
                "adversarial helper, nested prompts are forbidden, and "
                "review-frame clarification is the first default route."
            ),
        },
        {
            "label": "Micro-Scene Observation Frame Readback",
            "command": "see docs\\style_intent\\micro-scene-observation-frame-readback.md",
            "target": "docs/style_intent/micro-scene-observation-frame-readback.md",
            "when_to_use": (
                "Use to inspect the ED-10av readback: the ED-10au specimen opened "
                "and reads as a real scene, but expectation/review-frame clarity "
                "and subtitle/player-UI overlap remain classified warnings."
            ),
        },
        {
            "label": "Representative Micro-Scene Specimen Readback",
            "command": "see docs\\style_intent\\representative-micro-scene-internal-review-specimen.md",
            "target": "docs/style_intent/representative-micro-scene-internal-review-specimen.md",
            "when_to_use": (
                "Use to inspect the ED-10au source specimen consumed by ED-10av: "
                "actual Japanese transcript content, verified same-machine MP4 "
                "access, and closed production/public gates."
            ),
        },
        {
            "label": "Open Representative Micro-Scene Specimen",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_internal_review_specimen.ps1",
            "target": "scripts/operator/open_representative_micro_scene_internal_review_specimen.ps1",
            "when_to_use": (
                "Use later only when a supervisor asks to open the ED-10au internal review specimen MP4."
            ),
        },
        {
            "label": "Internal Review Observation Readback",
            "command": "see docs\\style_intent\\internal-review-video-observation-readback.md",
            "target": "docs/style_intent/internal-review-video-observation-readback.md",
            "when_to_use": (
                "Use to inspect the ED-10at user observation readback: openability "
                "and cue visibility pass diagnostically, chopped/memo-like "
                "continuity is not production review, and no approval is inferred."
            ),
        },
        {
            "label": "Internal Review Video Candidate Access Sheet",
            "command": "see docs\\style_intent\\internal-review-video-candidate-access-sheet.md",
            "target": "docs/style_intent/internal-review-video-candidate-access-sheet.md",
            "when_to_use": (
                "Use to find current-host full paths and the launcher for the ED-10ar internal review video candidate."
            ),
        },
        {
            "label": "Open Internal Review Video Candidate",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_internal_review_video_candidate.ps1",
            "target": "scripts/operator/open_internal_review_video_candidate.ps1",
            "when_to_use": (
                "Use later only when a supervisor asks to open the internal review candidate MP4."
            ),
        },
        {
            "label": "Internal Review Video Candidate Package",
            "command": "see docs\\style_intent\\internal-review-video-candidate-package.md",
            "target": "docs/style_intent/internal-review-video-candidate-package.md",
            "when_to_use": (
                "Use to inspect the ED-10ar internal review video candidate package without treating it as production or public-use approval."
            ),
        },
        {
            "label": "Production Limitation Lift Stage 5 User Decision Ready",
            "command": "see docs\\style_intent\\subtitle-production-limitation-lift-stage-5-user-decision-ready.md",
            "target": "docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.md",
            "when_to_use": (
                "Use to inspect the ED-10aq stage-5 user-decision-ready source packet without asking for approval now."
            ),
        },
        {
            "label": "Production Limitation-Lift Stage 3 Owner-Review Prep",
            "command": "see docs\\style_intent\\subtitle-production-limitation-lift-stage-3-owner-review-prep.md",
            "target": "docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md",
            "when_to_use": (
                "Use to inspect the ED-10ao owner-review preparation packet "
                "that converts ED-10an decision groups into future freeform "
                "decision topics without requesting approval now."
            ),
        },
        {
            "label": "Production Limitation-Lift Stage 2 Decision Packet",
            "command": "see docs\\style_intent\\subtitle-production-limitation-lift-stage-2-decision-packet.md",
            "target": "docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md",
            "when_to_use": (
                "Use to inspect the ED-10an decision-preparation packet that "
                "groups ED-10am gates into subtitle design/visual acceptance, "
                "production render readiness, and rights/publishing/public-use "
                "clearance without approving those decisions."
            ),
        },
        {
            "label": "Production Limitation-Lift Stage 1",
            "command": "see docs\\style_intent\\subtitle-production-limitation-lift-stage-1.md",
            "target": "docs/style_intent/subtitle-production-limitation-lift-stage-1.md",
            "when_to_use": (
                "Use to inspect the ED-10am gate matrix that turns ED-10al "
                "diagnostic rehearsal evidence into production/public decision "
                "preparation without approving those decisions."
            ),
        },
        {
            "label": "Final Render Path Stage 3 Rehearsal",
            "command": "see docs\\style_intent\\subtitle-final-render-path-stage-3.md",
            "target": "docs/style_intent/subtitle-final-render-path-stage-3.md",
            "when_to_use": (
                "Use to inspect the ED-10al diagnostic rehearsal, generated "
                "ignored ASS/MP4/manifest outputs, output metadata, style "
                "survival readback, and closed production/public gates."
            ),
        },
        {
            "label": "Final Render Path Stage 2 Replayability",
            "command": "see docs\\style_intent\\subtitle-final-render-path-stage-2.md",
            "target": "docs/style_intent/subtitle-final-render-path-stage-2.md",
            "when_to_use": (
                "Use to inspect the ED-10ak operation packet, replay inputs, "
                "ignored outputs, command family, fresh-clone absence behavior, "
                "and closed production/public gates."
            ),
        },
        {
            "label": "Final Render Path Stage 1",
            "command": "see docs\\style_intent\\subtitle-final-render-path-stage-1.md",
            "target": "docs/style_intent/subtitle-final-render-path-stage-1.md",
            "when_to_use": (
                "Use to inspect the ED-10aj selected FFmpeg/libass path, "
                "stage-1 checklist, and closed production/public gates."
            ),
        },
        {
            "label": "Final Render Path Readiness",
            "command": "see docs\\style_intent\\subtitle-final-render-path-readiness.md",
            "target": "docs/style_intent/subtitle-final-render-path-readiness.md",
            "when_to_use": (
                "Use to inspect the ED-10ai readiness matrix before any later "
                "final render-path stage or limitation-lift route."
            ),
        },
        {
            "label": "Production Limitation-Lift Entry",
            "command": "see docs\\style_intent\\subtitle-production-limitation-lift-entry.md",
            "target": "docs/style_intent/subtitle-production-limitation-lift-entry.md",
            "when_to_use": (
                "Use to inspect the ED-10ah gate matrix that separates diagnostic "
                "render-path proof from production, rights, publishing, and "
                "public-use decisions."
            ),
        },
        {
            "label": "Render Readiness Separation",
            "command": "see docs\\style_intent\\subtitle-render-readiness-separation.md",
            "target": "docs/style_intent/subtitle-render-readiness-separation.md",
            "when_to_use": (
                "Use to inspect what ED-10ag proves, what remains unaccepted, "
                "and which later explicit milestone may trigger a render."
            ),
        },
        {
            "label": "Render Path Selector Probe",
            "command": "see docs\\style_intent\\subtitle-render-path-selector-probe.md",
            "target": "docs/style_intent/subtitle-render-path-selector-probe.md",
            "when_to_use": "Use to inspect the ED-10af L2 selector probe rows, local ignored ASS/MP4/manifest paths, and boundary readback from the ED-10ae contract.",
        },
        {
            "label": "Lineage Observation Surface",
            "command": "see docs\\style_intent\\subtitle-render-path-lineage-observation-surface.md",
            "target": "docs/style_intent/subtitle-render-path-lineage-observation-surface.md",
            "when_to_use": (
                "Use to inspect the restored dry-read predecessor, active ED-10af "
                "L2 probe, and local ignored ASS/MP4/manifest/contact-sheet readback."
            ),
        },
        {
            "label": "Render Path Selector Contract",
            "command": "see docs\\style_intent\\subtitle-render-path-selector-contract.md",
            "target": "docs/style_intent/subtitle-render-path-selector-contract.md",
            "when_to_use": (
                "Use to inspect which selector, family, palette, color, motion, "
                "and line-break fields a later render adapter would receive; "
                "this is L0 static readback, not an actual render pass."
            ),
        },
        {
            "label": "Style Family Palette Proof",
            "command": "see docs\\style_intent\\subtitle-style-family-palette-proof.html",
            "target": "docs/style_intent/subtitle-style-family-palette-proof.html",
            "when_to_use": (
                "Use to inspect the ED-10ad family and palette axes while "
                "body subtitle text color remains stable and palette changes "
                "stay on badge, accent, and backplate surfaces."
            ),
        },
        {
            "label": "Visual Selector Proof",
            "command": "see docs\\style_intent\\subtitle-visual-selector-proof.html",
            "target": "docs/style_intent/subtitle-visual-selector-proof.html",
            "when_to_use": (
                "Use to inspect the ED-10ab semantic presets as badge, accent, "
                "backplate, size, motion, and line-break token differences "
                "while body subtitle text color stays stable."
            ),
        },
        {
            "label": "Preset Selector",
            "command": "see docs\\style_intent\\subtitle-preset-selector.json",
            "target": "docs/style_intent/subtitle-preset-selector.json",
            "when_to_use": (
                "Use before visual selector work to inspect deterministic "
                "speaker, emotion, intensity, utterance role, and readability "
                "token mappings."
            ),
        },
        {
            "label": "Style Intent Registry",
            "command": "see docs\\SUBTITLE_STYLE_INTENT_REGISTRY.md",
            "target": "docs/SUBTITLE_STYLE_INTENT_REGISTRY.md",
            "when_to_use": (
                "Use before future subtitle style work so speaker, emotion, "
                "intensity, utterance role, and readability tags map to presets "
                "instead of repeated tiny numeric review loops."
            ),
        },
        {
            "label": "Tiny Render-Path Probe",
            "command": ".\\open-current-proof.ps1",
            "target": "episodes/.../subtitle_presentation_review_pack.html",
            "when_to_use": (
                "Use as the ED-10z local readback that passes Candidate 2 "
                "through the current diagnostic render path while preserving "
                "Candidate 0 as fallback and Candidate 1/3 as held references."
            ),
        },
        {
            "label": "Multi-font Focused Review Reference",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_multifont_focused_review\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_multifont_focused_review/"
                "subtitle_multifont_focused_review_report.html"
            ),
            "when_to_use": (
                "Use as the accepted ED-10o same-line comparison reference; "
                "it does not mean final baseline or production acceptance."
            ),
        },
        {
            "label": "Known Font Pack",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_known_kirinuki_font_pack_comparison\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_known_kirinuki_font_pack_comparison/"
                "subtitle_known_kirinuki_font_pack_report.html"
            ),
            "when_to_use": (
                "Use as ED-10l/ED-10n readback evidence that the requested "
                "per-user fonts resolve in the regenerated comparison."
            ),
        },
        {
            "label": "BIZ Proof Reference",
            "command": "see artifact registry for archived previous proof paths",
            "target": "artifacts/ARTIFACTS.md",
            "when_to_use": (
                "Use only as the reviewed ED-10k reference that explains why the "
                "system-safe BIZ route stopped; open-current-proof now points to ED-10r."
            ),
        },
        {
            "label": "Font Audit",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_kirinuki_font_audit\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_kirinuki_font_audit/"
                "subtitle_kirinuki_font_audit_report.html"
            ),
            "when_to_use": "Use only to audit the consumed ED-10j contact sheet and candidate mapping.",
        },
        {
            "label": "Gothic Balance",
            "command": (
                "powershell -ExecutionPolicy Bypass -File "
                "episodes\\jp_pilot01_hololive_bancho_20260525\\review\\"
                "jp_pilot01r3_cut_review\\subtitle_kirinuki_gothic_balance_comparison\\"
                "open_comparison.ps1"
            ),
            "target": (
                "episodes/.../subtitle_kirinuki_gothic_balance_comparison/"
                "subtitle_kirinuki_gothic_balance_comparison_report.html"
            ),
            "when_to_use": (
                "Use on the machine retaining ignored ED-10i comparison artifacts "
                "to judge gothic glyph body versus outline balance."
            ),
        },
        {
            "label": "Font Candidates",
            "command": ".\\open-font-candidates.ps1",
            "target": "docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md",
            "when_to_use": "Use when ED-10h font universe or local/system font availability is the next question.",
        },
    ]


def _title(text: str, *, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def _doc_status(text: str) -> str:
    if "generated_requires_human_review" in text:
        return "review_ready_diagnostic"
    if "in_progress" in text:
        return "in_progress"
    if "done" in text:
        return "contains_done_history"
    return "reference"


def _boundary_term_count(text: str) -> int:
    lower = text.lower()
    return sum(lower.count(term.lower()) for term in BOUNDARY_TERMS)


def _clean_markdown(value: str) -> str:
    cleaned = value.replace("**", "").replace("`", "")
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"<([^>]+)>", r"\1", cleaned)
    return " ".join(cleaned.split())


def _first_artifact_id(value: str) -> str:
    match = re.search(r"`(clip-[a-z0-9-]+-\d+)`", value)
    if match:
        return match.group(1)
    match = re.search(r"(clip-[a-z0-9-]+-\d+)", value)
    return match.group(1) if match else ""


def _feature_health(feature_id: str, status: str, summary: str) -> str:
    if feature_id == "ED-10g":
        return "accepted_diagnostic_base"
    if feature_id == "ED-10h":
        return "defined_not_generated"
    if feature_id == "ED-10i":
        return "reviewed_not_accepted_as_normal_baseline"
    if feature_id == "ED-10j":
        return "font_audit_consumed_biz_selected"
    if feature_id == "ED-10k":
        return "reviewed_not_accepted_as_normal_baseline"
    if feature_id == "ED-10l":
        return "per_user_font_readback_valid_comparison"
    if feature_id == "ED-10m":
        return "keifont_route_prepared_user_install_completed_by_user"
    if feature_id == "ED-10n":
        return "keifont_overlay_proof_ready_for_human_review"
    if feature_id == "ED-10o":
        return "focused_review_surface_accepted_reference"
    if feature_id == "ED-10p":
        return "keifont_lead_representative_proof_ready"
    if feature_id == "ED-10q":
        return "current_proof_focused_review_restored"
    if feature_id == "ED-10r":
        return "superseded_by_ed10u_multiline_evidence_correction"
    if feature_id == "ED-10t":
        return "keifont_dense_stress_proof_review_ready"
    if feature_id == "ED-10u":
        return "superseded_by_ed10v_dense_stress_pass"
    if feature_id == "ED-10v":
        return "dense_stress_pass_linebreak_policy_recorded"
    if feature_id == "ED-10w":
        return "subtitle_presentation_review_pack_ready"
    if feature_id == "ED-10y":
        return "candidate2_carry_forward_ready"
    if feature_id == "ED-10z":
        return "tiny_render_path_nearer_probe_ready"
    if feature_id == "ED-10aa":
        return "subtitle_style_intent_registry_ready"
    if feature_id == "ED-10ab":
        return "subtitle_preset_selector_ready"
    if feature_id == "ED-10ac":
        return "visual_selector_proof_ready"
    if feature_id == "ED-10ad":
        return "style_family_palette_axis_proof_ready"
    if feature_id == "ED-10ae":
        return "render_path_selector_contract_ready"
    if feature_id == "ED-10af":
        return "l2_render_path_selector_probe_ready"
    if feature_id == "ED-10ag":
        return "lineage_observation_surface_ready"
    if feature_id == "ED-10ah":
        return "production_limitation_lift_entry_ready"
    if feature_id == "ED-10ai":
        return "final_render_path_readiness_packet_ready"
    if feature_id == "ED-10aj":
        return "final_render_path_stage_1_ready"
    if feature_id == "ED-10ak":
        return "final_render_path_stage_2_replayability_ready"
    if feature_id == "ED-10al":
        return "final_render_path_stage_3_diagnostic_rehearsal_ready"
    if feature_id == "ED-10am":
        return "production_limitation_lift_stage_1_packet_ready"
    if feature_id == "ED-10an":
        return "production_limitation_lift_stage_2_decision_packet_ready"
    if feature_id == "ED-10ao":
        return "production_limitation_lift_stage_3_owner_review_prep_ready"
    if feature_id == "ED-10ap":
        return "production_limitation_lift_stage_4_user_decision_card_ready"
    if feature_id == "ED-10aq":
        return "production_limitation_lift_stage_5_user_decision_ready"
    if feature_id == "ED-10ar":
        return "internal_review_video_candidate_package_ready"
    if feature_id == "ED-10as":
        return "internal_review_access_sheet_fullpath_ready"
    if feature_id == "ED-10at":
        return "internal_review_observation_readback_ready"
    if feature_id == "ED-10au":
        return "representative_micro_scene_internal_review_specimen_ready"
    if feature_id == "ED-10av":
        return "micro_scene_observation_frame_readback_ready"
    if feature_id == "ED-10aw":
        return "grill_me_adoption_review_frame_plan_ready"
    if feature_id == "ED-10ax":
        return "review_frame_clarification_surface_ready"
    if feature_id == "ED-10ay":
        return "thank_ed10au_local_access_recovery_ready"
    if feature_id == "ED-10az":
        return "observation_readback_and_v2_route_decision_ready"
    if feature_id == "ED-10ba":
        return "representative_micro_scene_v2_cut_window_review_purpose_alignment_ready"
    if feature_id == "ED-10bb":
        return "thank_ed10ba_v2_local_access_recovery_verified_present"
    if feature_id == "ED-10bc":
        return "thank_v2_open_command_repair_ready"
    if "blocked" in summary or status == "hold":
        return "blocked"
    return STATUS_HEALTH.get(status, "unknown")


def _feature_progress(feature_id: str, status: str) -> int:
    if feature_id == "ED-10g":
        return 100
    if feature_id == "ED-10h":
        return 15
    if feature_id == "ED-10i":
        return 100
    if feature_id == "ED-10j":
        return 100
    if feature_id == "ED-10k":
        return 100
    if feature_id == "ED-10l":
        return 100
    if feature_id == "ED-10m":
        return 100
    if feature_id == "ED-10n":
        return 95
    if feature_id == "ED-10o":
        return 100
    if feature_id == "ED-10p":
        return 100
    if feature_id == "ED-10q":
        return 100
    if feature_id == "ED-10r":
        return 100
    if feature_id == "ED-10t":
        return 100
    if feature_id == "ED-10u":
        return 100
    if feature_id == "ED-10v":
        return 100
    if feature_id == "ED-10w":
        return 100
    if feature_id == "ED-10y":
        return 100
    if feature_id == "ED-10z":
        return 100
    if feature_id == "ED-10aa":
        return 100
    if feature_id == "ED-10ab":
        return 100
    if feature_id == "ED-10ac":
        return 100
    if feature_id == "ED-10ad":
        return 100
    if feature_id == "ED-10ae":
        return 100
    if feature_id == "ED-10af":
        return 100
    if feature_id == "ED-10ag":
        return 100
    if feature_id == "ED-10ah":
        return 100
    if feature_id == "ED-10ai":
        return 100
    if feature_id == "ED-10aj":
        return 100
    if feature_id == "ED-10ak":
        return 100
    if feature_id == "ED-10al":
        return 100
    if feature_id == "ED-10am":
        return 100
    if feature_id == "ED-10an":
        return 100
    if feature_id == "ED-10ao":
        return 100
    if feature_id == "ED-10ap":
        return 100
    if feature_id == "ED-10aq":
        return 100
    if feature_id == "ED-10ar":
        return 100
    if feature_id == "ED-10as":
        return 100
    if feature_id == "ED-10at":
        return 100
    if feature_id == "ED-10au":
        return 100
    if feature_id == "ED-10av":
        return 100
    if feature_id == "ED-10aw":
        return 100
    if feature_id == "ED-10ax":
        return 100
    if feature_id == "ED-10ay":
        return 100
    if feature_id == "ED-10az":
        return 100
    if feature_id == "ED-10ba":
        return 100
    if feature_id == "ED-10bb":
        return 100
    if feature_id == "ED-10bc":
        return 100
    return STATUS_PROGRESS.get(status, 0)


def _feature_next_action(feature_id: str, status: str, summary: str) -> str:
    if feature_id == "ED-10g":
        return "Keep as historical diagnostic proof; the latest human review sends styling to ED-10i."
    if feature_id == "ED-10h":
        return "Use the font candidate registry to choose a no-download or download-approved sweep route."
    if feature_id == "ED-10i":
        return "Keep the Meiryo proof as reviewed reference; do not treat it as the normal subtitle baseline."
    if feature_id == "ED-10j":
        return "Keep as consumed audit trail; BIZ UDGothic selection was superseded by ED-10k review."
    if feature_id == "ED-10k":
        return "Keep as reviewed rejected reference; do not treat BIZ as the normal-dialogue baseline."
    if feature_id == "ED-10l":
        return "Keep as regenerated real-font comparison; use ED-10n Keifont proof for current visual judgement."
    if feature_id == "ED-10m":
        return "Keep as source/license route record; ED-10n consumed the per-user font readback."
    if feature_id == "ED-10n":
        return "Keep as earlier lead proof reference; ED-10q is now the focused current review surface for the ED-10p artifact."
    if feature_id == "ED-10o":
        return "Keep as accepted focused review-surface reference; it is not final baseline or production acceptance."
    if feature_id == "ED-10p":
        return "Keep as consumed Keifont provisional baseline evidence; ED-10u is now the multiline/dense-stress review route."
    if feature_id == "ED-10q":
        return "Keep as the page-format regression fix; do not treat it as new Keifont font-quality review."
    if feature_id == "ED-10r":
        return "Superseded by ED-10u focused multiline evidence correction; review only corrected cut_008 multiline/dense-stress behavior."
    if feature_id == "ED-10t":
        return "Superseded by ED-10u focused multiline evidence correction; keep font readback as valid."
    if feature_id == "ED-10u":
        return "Consumed by ED-10v user pass; keep as the corrected evidence surface."
    if feature_id == "ED-10v":
        return "Current dense/stress axis is passed; continue only through a new axis such as line-break policy tuning, bounded decoration adjustment, or production limitation-lift."
    if feature_id == "ED-10w":
        return "Use the crop-first review pack to choose Candidate 0 baseline, Candidate 1/2/3 bounded adjustment, or the next tiny render-path diagnostic probe."
    if feature_id == "ED-10y":
        return "Continue from Candidate 2 as provisional bounded-decoration lead; do not repeat the Candidate 0-3 review."
    if feature_id == "ED-10z":
        return "Use the Candidate 2 tiny render-path-nearer probe as local readback; open production limitation-lift or final render-path work only as a separate scope."
    if feature_id == "ED-10aa":
        return "Use the semantic style intent registry for future emotion/speaker/readability preset mapping; ED-10z actual local proof now exists and any limitation-lift/final render-path work should be a separate route."
    if feature_id == "ED-10ab":
        return "Use the deterministic preset selector as readback before future visual style proof; open new style-family, palette, production, rights, publishing, or public-use work as separate routes."
    if feature_id == "ED-10ac":
        return "Use the static visual selector proof for optional open-only observation; keep new style-family, palette, production, rights, publishing, and public-use decisions in separate routes."
    if feature_id == "ED-10ad":
        return "Use the style-family/palette axis proof as no-render static readback before a later render-path probe or separate production/rights/public-use route."
    if feature_id == "ED-10ae":
        return "Use the selector-to-render-path contract as L0 static readback before a later L2 render-path probe; do not infer actual render or production readiness."
    if feature_id == "ED-10af":
        return "Use the L2 selector probe readback before opening a separate production limitation-lift, rights, publishing, or public-use route."
    if feature_id == "ED-10ag":
        return "Use the lineage and observation surface to preserve the dry-read predecessor and inspect same-machine proof paths; rerender only under a separate explicit render milestone."
    if feature_id == "ED-10ah":
        return "Use the limitation-lift entry to start production-limitation-lift-stage-1 or final-render-path-readiness; keep production, rights, publishing, and public-use approvals explicit."
    if feature_id == "ED-10ai":
        return "Use the final render-path readiness packet to start final-render-path-stage-1 or production-limitation-lift-stage-1; keep production/public approvals explicit."
    if feature_id == "ED-10aj":
        return "Use the final render-path stage-1 packet to start final-render-path-stage-2 or production-limitation-lift-stage-1; keep production/public approvals explicit."
    if feature_id == "ED-10ak":
        return "Use the final render-path stage-2 replayability packet to start final-render-path-stage-3 or production-limitation-lift-stage-1; keep production/public approvals explicit."
    if feature_id == "ED-10al":
        return "Use the final render-path stage-3 diagnostic rehearsal as source evidence for production-limitation-lift-stage-1 or a later diagnostic-only stage-4."
    if feature_id == "ED-10am":
        return "Use the production limitation-lift stage-1 packet to start production-limitation-lift-stage-2-decision-packet; keep production/public approvals explicit."
    if feature_id == "ED-10an":
        return "Use the stage-2 decision packet to start production-limitation-lift-stage-3-owner-review-prep; keep all approvals explicit."
    if feature_id == "ED-10ao":
        return "Use the stage-3 owner-review prep packet to start production-limitation-lift-stage-4-user-decision-card; keep future user input freeform and approvals explicit."
    if feature_id == "ED-10ap":
        return "Use the freeform user decision card only when a later slice explicitly asks for user judgement; keep approvals explicit."
    if feature_id == "ED-10aq":
        return "Use the stage-5 user-decision-ready packet only; keep user work none and approvals explicit."
    if feature_id == "ED-10ar":
        return "Use the internal review video candidate package only; optional later observation stays freeform and non-approving."
    if feature_id == "ED-10as":
        return "Use the access sheet and launcher only for later optional open/readback; keep observation freeform and non-approving."
    if feature_id == "ED-10at":
        return "Use the ED-10at observation readback to choose a representative micro-scene specimen for real internal review, or final-render-path-stage-4 only for a concrete diagnostic render gap; do not infer approval."
    if feature_id == "ED-10au":
        return "Use the access-verified representative micro-scene specimen only for optional later freeform observation; classify any next fix as script, timing/audio, visual layout, or render path without inferring approval."
    if feature_id == "ED-10av":
        return "Use the observation frame readback to clarify the review frame first, capture subtitle/player-UI evidence if needed, and only rerender or open stage-4 for a concrete source/layout/render gap."
    if feature_id == "ED-10aw":
        return "Use the Grill-me adoption readback as a bounded precommit/report check, then implement review-frame clarification before any layout capture, v2 specimen, or render-path stage-4 work."
    if feature_id == "ED-10ax":
        return "Use the review-frame clarification surface for later freeform review; keep screenshot capture, v2 specimen, and final-render-path stage-4 conditional."
    if feature_id == "ED-10ay":
        return "Keep as current-host ED-10au local access recovery evidence; use ED-10ba for the successor v2 specimen."
    if feature_id == "ED-10az":
        return "Keep as the consumed route decision that enabled ED-10ba; do not restart screenshot, timing/audio, or pure review-frame work without new evidence."
    if feature_id == "ED-10ba":
        return "Use the access-verified v2 specimen for later freeform cut-window/review-purpose judgement; keep episodes media ignored and approvals closed."
    if feature_id == "ED-10bb":
        return "Use the verified Thank-host v2 specimen for later freeform cut-window/review-purpose judgement; keep episodes media ignored and approvals closed."
    if feature_id == "ED-10bc":
        return "Use the repaired opener or -SelectVideo fallback only under a later freeform v2 review request; treat further visibility failures as player/file-association issues before regenerating media."
    if status == "done":
        return "Keep as reference unless a regression or successor lane appears."
    if status == "proposed":
        return "Promote to approved only after an explicit slice decision."
    if status == "in_progress":
        return "Finish current acceptance/readback and update artifact registry."
    return _truncate(summary, 120)


def _artifact_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2 or cells[0] in {"Field", "---"}:
            continue
        fields[_clean_markdown(cells[0]).lower()] = _clean_markdown(cells[1])
    return fields


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def _md(value: Any) -> str:
    text = str(value).replace("|", "\\|")
    return text.replace("\n", " ")


def _entrypoint_list_html(items: list[dict[str, str]]) -> str:
    entries = "\n".join(
        f"<li><code>{escape(item['path'])}</code>: {escape(item['role'])}</li>"
        for item in items
    )
    return f"<ul>{entries}</ul>"


def _features_table_html(features: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(feature['id'])}</code></td>"
        f"<td>{escape(feature['title'])}</td>"
        f"<td>{escape(feature['status'])}</td>"
        f"<td>{escape(feature['health'])}</td>"
        f"<td>{escape(str(feature['progress_pct']))}%</td>"
        f"<td><code>{escape(feature.get('active_artifact') or '')}</code></td>"
        f"<td>{escape(feature['next_action'])}</td>"
        "</tr>"
        for feature in features
    )
    return (
        "<table><tr><th>id</th><th>title</th><th>status</th><th>health</th>"
        "<th>progress</th><th>active artifact</th><th>next action</th></tr>"
        f"{rows}</table>"
    )


def _artifacts_table_html(artifacts: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(artifact['artifact_id'])}</code></td>"
        f"<td>{escape(artifact.get('title') or '')}</td>"
        f"<td>{escape(artifact.get('storage_class') or '')}</td>"
        f"<td><code>{escape(artifact.get('repo_relative_path') or '')}</code></td>"
        f"<td><code>{escape(artifact.get('open_command') or '')}</code></td>"
        f"<td>{escape(artifact.get('next_action') or '')}</td>"
        "</tr>"
        for artifact in artifacts
    )
    return (
        "<table><tr><th>artifact</th><th>title</th><th>storage</th>"
        "<th>path</th><th>open command</th><th>next action</th></tr>"
        f"{rows}</table>"
    )


def _open_surfaces_table_html(items: list[dict[str, str]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(item['label'])}</td>"
        f"<td><code>{escape(item['command'])}</code></td>"
        f"<td><code>{escape(item['target'])}</code></td>"
        f"<td>{escape(item['when_to_use'])}</td>"
        "</tr>"
        for item in items
    )
    return (
        "<table><tr><th>surface</th><th>command</th><th>target</th>"
        "<th>when to use</th></tr>"
        f"{rows}</table>"
    )


def _review_items_table_html(items: list[dict[str, str]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(item['item'])}</td>"
        f"<td><code>{escape(item['artifact'])}</code></td>"
        f"<td>{escape(item['question'])}</td>"
        f"<td>{escape(item['next_route'])}</td>"
        "</tr>"
        for item in items
    )
    return (
        "<table><tr><th>item</th><th>artifact</th><th>question</th>"
        "<th>next route</th></tr>"
        f"{rows}</table>"
    )


def _findings_table_html(findings: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(item['type'])}</td>"
        f"<td><code>{escape(item['path'])}</code></td>"
        f"<td>{escape(item['detail'])}</td>"
        f"<td>{escape(item['suggested_fix'])}</td>"
        "</tr>"
        for item in findings
    )
    return f"<table><tr><th>type</th><th>path</th><th>detail</th><th>suggested fix</th></tr>{rows}</table>"


def _docs_table_html(docs: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{escape(doc['path'])}</code></td>"
        f"<td>{escape(doc['title'])}</td>"
        f"<td>{escape(str(doc['line_count']))}</td>"
        f"<td>{escape(json.dumps(doc['front_sections'], ensure_ascii=False))}</td>"
        f"<td>{escape(doc['status'])}</td>"
        "</tr>"
        for doc in docs
    )
    return f"<table><tr><th>path</th><th>title</th><th>lines</th><th>front sections</th><th>status</th></tr>{rows}</table>"


def _improvements_table_html(items: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item['rank']))}</td>"
        f"<td><code>{escape(item['path'])}</code></td>"
        f"<td>{escape(item['why'])}</td>"
        f"<td>{escape(item['next_move'])}</td>"
        "</tr>"
        for item in items
    )
    return f"<table><tr><th>rank</th><th>path</th><th>why</th><th>next move</th></tr>{rows}</table>"
