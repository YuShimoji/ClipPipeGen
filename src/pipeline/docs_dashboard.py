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
DEFAULT_GENERATED_AT = "2026-06-18"
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
    return {
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
        "current_focus": {
            "feature_id": "ED-10l",
            "artifact_id": "clip-ed10l-known-kirinuki-font-pack-001",
            "state": "ed10l_known_kirinuki_font_pack_audit_active",
            "human_visual_judgement": "ed10k_biz_freeform_review_consumed_not_accepted",
            "target_cuts": ["cut_002", "cut_003"],
            "accepted_size_rule": "round(frame_height * 0.115)",
            "selected_typography_base": "pending_known_kirinuki_font_pack_review",
            "selected_typography_source": "user_known_good_font_review_and_source_inspection",
            "preferred_direction": "known_japanese_youtube_kirinuki_telop_fonts",
            "main_issue": "system_safe_generic_route_rejected_for_normal_baseline",
            "emoji_treatment": "neutral_ignore_for_evaluation",
            "production_candidate": False,
            "production_subtitle_design_acceptance": False,
            "production_render_acceptance": False,
            "production_usage_allowed": False,
            "publishing_acceptance": False,
            "public_use_permission": False,
            "rights_status": "pending",
        },
        "open_surfaces": _open_surfaces(),
        "wiki_entrypoints": _wiki_entrypoints(),
        "features": features,
        "feature_summary": _feature_summary(features),
        "active_artifacts": artifacts,
        "artifact_summary": _artifact_summary(artifacts),
        "artifact_coverage": _artifact_coverage(features, artifacts),
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
    <table>
      <tr><th>feature</th><td>{escape(focus["feature_id"])}</td></tr>
      <tr><th>artifact</th><td>{escape(focus["artifact_id"])}</td></tr>
      <tr><th>targets</th><td>{escape(", ".join(focus["target_cuts"]))}</td></tr>
      <tr><th>typography base</th><td>{escape(focus["selected_typography_base"])}</td></tr>
      <tr><th>rights / production</th><td>rights={escape(focus["rights_status"])}; production_candidate={escape(str(focus["production_candidate"]).lower())}</td></tr>
    </table>
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
    features: list[dict[str, Any]], artifacts: list[dict[str, Any]]
) -> dict[str, Any]:
    artifact_ids = {artifact["artifact_id"] for artifact in artifacts}
    mentioned = [
        feature for feature in features if feature.get("active_artifact") in artifact_ids
    ]
    current_focus_registered = "clip-ed10l-known-kirinuki-font-pack-001" in artifact_ids
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
            "item": "ED-10l known kirinuki font pack audit",
            "artifact": "clip-ed10l-known-kirinuki-font-pack-001",
            "question": "Which known Japanese kirinuki/telop font should become the next normal-dialogue install/proof route for cut_002 / cut_003?",
            "next_route": "Open the known-font pack comparison and give freeform visual review; this is not production/public/rights acceptance.",
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
            "next_route": "Use the contact-sheet readback only for audit; do not prolong the comparison unless the BIZ proof fails.",
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
            "label": "Artifacts",
            "command": ".\\open-artifacts.ps1",
            "target": "artifacts/ARTIFACTS.md",
            "when_to_use": "Use after the dashboard when an artifact needs its registry entry or open command.",
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
                "Use first for ED-10l normal-dialogue font route review after BIZ "
                "was rejected as the baseline."
            ),
        },
        {
            "label": "BIZ Proof Reference",
            "command": ".\\open-current-proof.ps1",
            "target": "episodes/.../subtitle_overlay_visual_proof_report.html",
            "when_to_use": (
                "Use only as the reviewed ED-10k reference that explains why the "
                "system-safe BIZ route stopped."
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
        return "known_font_pack_audit_active"
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
        return 60
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
        return "Review the known kirinuki font pack audit and choose the next install/proof route."
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
