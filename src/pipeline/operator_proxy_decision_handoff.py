"""Scoped operator proxy decision handoff for JP-Pilot R3.

The handoff narrows Chapter Revision input to cuts that do not yet have
subtitle-overlay visual proof. It is an operator decision surface only: it does
not render video, approve rights, mutate source transcript evidence, or create
production output.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v1"
TEXT_REVIEW_KIND = "cut_text_proxy_review_v0"
HANDOFF_KIND = "operator_proxy_decision_handoff_v0"
PATCH_KIND = "chapter_revision_patch_cut_proxy_v0"
DEFAULT_REVIEW_DIR_NAME = "jp_pilot01r3_cut_review"
DEFAULT_TARGET_CUT_IDS = ("cut_002", "cut_003")
PROXY_DECISION_VALUES = [
    "undecided",
    "proceed_without_visual_proof",
    "needs_overlay_proof",
    "adjust_subtitle",
    "adjust_boundary",
    "defer",
    "reject_candidate",
]
ANALYST_ACTION_VALUES = [
    "noop",
    "normalize_operator_notes",
    "apply_boundary_adjustment",
    "regenerate_subtitle_drafts",
    "rewrite_display_script_layer",
    "create_render_plan",
    "regenerate_representative_diagnostic",
    "create_nlmytgen_handoff",
    "request_operator_clarification",
]
DOWNSTREAM_TARGET_VALUES = [
    "edit_pack",
    "subtitle_drafts",
    "editorial_script",
    "render_plan",
    "nlmytgen_handoff",
    "rights_review",
    "source_selection",
    "none",
]
BOUNDARY_REQUEST_VALUES = [
    "none",
    "adjust_start",
    "adjust_end",
    "adjust_start_and_end",
    "split_chapter",
    "merge_with_previous",
    "merge_with_next",
]
CONTEXT_RISK_HANDLING_VALUES = [
    "undecided",
    "keep_retained_risk_visible",
    "request_boundary_review",
    "needs_overlay_proof",
    "reject_due_to_context",
    "defer",
]
CSV_COLUMNS = [
    "chapter_id",
    "cut_id",
    "proxy_decision",
    "editorial_intent",
    "script_override",
    "display_subtitle_request",
    "boundary_request",
    "context_risk_handling",
    "analyst_action",
    "downstream_target",
    "operator_note",
]


class OperatorProxyDecisionHandoffError(Exception):
    """Raised when the proxy handoff cannot be built safely."""


def build_operator_proxy_decision_handoff(
    *,
    episode_dir: Path,
    review_dir: Path | None = None,
    output_dir: Path | None = None,
    target_cut_ids: list[str] | tuple[str, ...] | None = None,
    edit_pack_path: Path | None = None,
    material_ledger_path: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Write scoped text/proxy review, handoff, and patch template artifacts."""

    base = base_dir or Path.cwd()
    review_dir = review_dir or episode_dir / "review" / DEFAULT_REVIEW_DIR_NAME
    output_dir = output_dir or review_dir
    edit_pack_path = edit_pack_path or episode_dir / "edit_pack.json"
    material_ledger_path = material_ledger_path or episode_dir / "material_ledger.json"
    target_cut_ids = tuple(target_cut_ids or DEFAULT_TARGET_CUT_IDS)
    if not target_cut_ids:
        raise OperatorProxyDecisionHandoffError("target_cut_ids must not be empty")

    board = _load_required_json(review_dir / "chapter_revision_board.json")
    cut_decision = _load_required_json(review_dir / "cut_decision_packet.json")
    visual_report = _load_required_json(review_dir / "representative_visual_proof_report.json")
    edit_pack = _load_optional_json(edit_pack_path)
    material_ledger = _load_optional_json(material_ledger_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    scope_slug = "_".join(target_cut_ids)
    text_review_path = output_dir / f"{scope_slug}_text_proxy_review.json"
    text_review_html_path = output_dir / f"{scope_slug}_text_proxy_review.html"
    handoff_path = output_dir / f"{scope_slug}_operator_proxy_decision_handoff.json"
    handoff_html_path = output_dir / f"{scope_slug}_operator_proxy_decision_handoff.html"
    patch_template_path = output_dir / f"chapter_revision_patch.{scope_slug}_proxy.template.json"
    patch_csv_path = output_dir / f"chapter_revision_patch.{scope_slug}_proxy.template.csv"

    source_media = _source_media_status(material_ledger, base)
    target_cuts = _target_cut_entries(
        board=board,
        cut_decision=cut_decision,
        visual_report=visual_report,
        edit_pack=edit_pack,
        target_cut_ids=target_cut_ids,
    )
    visual_proof_status = _aggregate_visual_proof_status(target_cuts)
    boundary_flags = _boundary_flags(cut_decision, visual_report)
    allowed_values = _allowed_values()
    text_review = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": TEXT_REVIEW_KIND,
        "created_at": _now(),
        "episode_id": _episode_id(episode_dir, board, cut_decision, visual_report),
        "scope": f"{scope_slug}_text_proxy_review",
        "target_cuts": list(target_cut_ids),
        "source_media_status": source_media,
        "visual_proof_status": visual_proof_status,
        "boundary_flags": boundary_flags,
        "review_method": "text_and_existing_proxy_readback_only",
        "operator_decision_status": "not_recorded",
        "cuts": [_text_review_cut(cut) for cut in target_cuts],
        "warnings": _warnings(visual_proof_status),
        "outputs": {
            "json": _display_path(text_review_path, base),
            "html": _display_path(text_review_html_path, base),
        },
    }
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": HANDOFF_KIND,
        "created_at": _now(),
        "episode_id": text_review["episode_id"],
        "scope": f"{scope_slug}_proxy_decision",
        "target_cuts": list(target_cut_ids),
        "source_media_status": source_media,
        "visual_proof_status": visual_proof_status,
        "boundary_flags": boundary_flags,
        "allowed_values": allowed_values,
        "operator_guidance": {
            "purpose": (
                "Capture operator decisions for cuts that still lack subtitle-overlay "
                "visual proof, without filling the full Chapter Revision Board."
            ),
            "agent_must_not_prefill": [
                "proxy_decision",
                "editorial_intent",
                "script_override",
                "display_subtitle_request",
                "context_risk_handling",
                "operator_note",
            ],
            "visual_proof_boundary": (
                "Typography, safe-area, line wrapping, and timing sync stay unproven "
                "until subtitle-overlay diagnostic proof exists for these cuts."
            ),
            "patch_files": [
                _display_path(patch_template_path, base),
                _display_path(patch_csv_path, base),
            ],
        },
        "cuts": [_handoff_cut(cut) for cut in target_cuts],
        "warnings": _warnings(visual_proof_status),
        "outputs": {
            "json": _display_path(handoff_path, base),
            "html": _display_path(handoff_html_path, base),
            "patch_template": _display_path(patch_template_path, base),
            "patch_csv": _display_path(patch_csv_path, base),
        },
    }
    patch_template = _patch_template(handoff, handoff_path, base)

    _write_json(text_review, text_review_path)
    text_review_html_path.write_text(_text_review_html(text_review), encoding="utf-8")
    _write_json(handoff, handoff_path)
    handoff_html_path.write_text(_handoff_html(handoff), encoding="utf-8")
    _write_json(patch_template, patch_template_path)
    _write_csv(_csv_rows(patch_template), patch_csv_path)

    return {
        "text_review": text_review,
        "handoff": handoff,
        "patch_template": patch_template,
        "text_review_path": text_review_path,
        "text_review_html_path": text_review_html_path,
        "handoff_path": handoff_path,
        "handoff_html_path": handoff_html_path,
        "patch_template_path": patch_template_path,
        "patch_csv_path": patch_csv_path,
    }


def _target_cut_entries(
    *,
    board: dict[str, Any],
    cut_decision: dict[str, Any],
    visual_report: dict[str, Any],
    edit_pack: dict[str, Any],
    target_cut_ids: tuple[str, ...],
) -> list[dict[str, Any]]:
    chapters = {
        str(item.get("source_cut_id")): item
        for item in board.get("chapters") or []
        if isinstance(item, dict) and item.get("source_cut_id")
    }
    decisions = {
        str(item.get("cut_id")): item
        for item in cut_decision.get("decisions") or []
        if isinstance(item, dict) and item.get("cut_id")
    }
    assessments = {
        str(item.get("cut_id")): item
        for item in visual_report.get("per_cut_visual_assessment") or []
        if isinstance(item, dict) and item.get("cut_id")
    }
    subtitles = _subtitle_index(edit_pack)
    cuts: list[dict[str, Any]] = []
    for cut_id in target_cut_ids:
        chapter = chapters.get(cut_id)
        if not chapter:
            raise OperatorProxyDecisionHandoffError(
                f"target cut missing from chapter_revision_board: {cut_id}"
            )
        decision = decisions.get(cut_id, {})
        assessment = assessments.get(cut_id, {})
        cut_subtitles = subtitles.get(cut_id) or _subtitle_rows_from_chapter(chapter)
        cuts.append(
            {
                "cut_id": cut_id,
                "chapter_id": chapter.get("chapter_id"),
                "context_status": chapter.get("original_context_status")
                or decision.get("context_status")
                or "unknown",
                "retained_context_risk": bool(
                    chapter.get("retained_context_risk")
                    or assessment.get("retained_context_risk")
                ),
                "manual_override_reason": decision.get("manual_override_reason")
                or assessment.get("manual_override_reason"),
                "duration_seconds": _number(
                    chapter.get("duration_seconds"),
                    decision.get("duration_seconds"),
                    assessment.get("duration_seconds"),
                ),
                "subtitle_count": _int(
                    chapter.get("subtitle_count"),
                    decision.get("subtitle_event_count"),
                    assessment.get("subtitle_count"),
                    len(cut_subtitles),
                ),
                "subtitle_density": _number(
                    chapter.get("subtitle_density"),
                    decision.get("subtitle_density_per_second"),
                    assessment.get("subtitle_density"),
                ),
                "subtitle_chars_per_second": _number(
                    chapter.get("subtitle_chars_per_second"),
                    decision.get("subtitle_chars_per_second"),
                ),
                "line_wrap_proxy": chapter.get("line_wrap_proxy") or {},
                "timing_span": chapter.get("timing_span") or {},
                "subtitle_text": cut_subtitles,
                "visual_proof": _visual_proof_readback(assessment),
                "missing_visual_proof_reason": _missing_visual_proof_reason(assessment),
                "current_risks": chapter.get("current_risks") or [],
            }
        )
    return cuts


def _text_review_cut(cut: dict[str, Any]) -> dict[str, Any]:
    return {
        key: cut[key]
        for key in [
            "cut_id",
            "chapter_id",
            "context_status",
            "retained_context_risk",
            "manual_override_reason",
            "duration_seconds",
            "subtitle_count",
            "subtitle_density",
            "subtitle_chars_per_second",
            "line_wrap_proxy",
            "timing_span",
            "subtitle_text",
            "visual_proof",
            "missing_visual_proof_reason",
            "current_risks",
        ]
    }


def _handoff_cut(cut: dict[str, Any]) -> dict[str, Any]:
    item = _text_review_cut(cut)
    item["operator_input_fields"] = _operator_input_fields(cut)
    return item


def _operator_input_fields(cut: dict[str, Any]) -> dict[str, Any]:
    return {
        "proxy_decision": "undecided",
        "editorial_intent": "",
        "script_override": "",
        "display_subtitle_request": "",
        "boundary_request": "none",
        "context_risk_handling": "undecided",
        "analyst_action": "noop",
        "downstream_target": "none",
        "operator_note": "",
        "retained_context_risk_readback": bool(cut.get("retained_context_risk")),
    }


def _patch_template(handoff: dict[str, Any], handoff_path: Path, base: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "patch_kind": PATCH_KIND,
        "created_at": _now(),
        "episode_id": handoff.get("episode_id"),
        "source_handoff_ref": _display_path(handoff_path, base),
        "patch_status": "draft",
        "target_cuts": handoff.get("target_cuts") or [],
        "allowed_values": handoff.get("allowed_values") or {},
        "boundary_flags": handoff.get("boundary_flags") or {},
        "global_notes": "",
        "validation_notes": [
            "proxy_decision defaults to undecided and must be changed only by operator input",
            "editorial_intent, script_override, display_subtitle_request, and operator_note start blank",
            "source transcript and official subtitle track remain evidence and are not patched here",
            "visual proof blocked entries do not pass typography, safe-area, line wrapping, or timing sync",
            "rights_status=pending keeps production/public usage disallowed",
        ],
        "revisions": [
            {
                "chapter_id": cut.get("chapter_id"),
                "cut_id": cut.get("cut_id"),
                **_operator_input_fields(cut),
            }
            for cut in handoff.get("cuts") or []
        ],
    }


def _source_media_status(material_ledger: dict[str, Any], base: Path) -> dict[str, Any]:
    materials = {
        str(item.get("id")): item
        for item in material_ledger.get("materials") or []
        if isinstance(item, dict) and item.get("id")
    }
    targets = {
        "source_video": "src_video_jp_pilot01",
        "source_audio": "src_audio_jp_pilot01",
    }
    entries: dict[str, Any] = {}
    for role, material_id in targets.items():
        material = materials.get(material_id, {})
        file_path = material.get("file_path")
        resolved = _resolve_display_path(file_path, base)
        entries[role] = {
            "material_id": material_id,
            "ledger_entry_exists": bool(material),
            "path": str(file_path).replace("\\", "/") if file_path else None,
            "exists": bool(resolved and resolved.exists()),
            "byte_size": resolved.stat().st_size if resolved and resolved.exists() else None,
            "sha256": material.get("hash_sha256"),
        }
    available = all(item["ledger_entry_exists"] and item["exists"] for item in entries.values())
    return {
        "status": "available_from_material_ledger" if available else "missing_source_media",
        "source_video": entries["source_video"],
        "source_audio": entries["source_audio"],
        "note": (
            "current source of truth is material_ledger paths, not old episode root-level media paths"
            if available
            else "source media is missing or not readable from material_ledger paths"
        ),
    }


def _visual_proof_readback(assessment: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": assessment.get("visual_proof_status") or "missing",
        "artifact_path": assessment.get("visual_proof_artifact_path"),
        "source_used": assessment.get("source_used"),
        "typography_status": assessment.get("typography_status"),
        "safe_area_status": assessment.get("safe_area_status"),
        "line_wrapping_status": assessment.get("line_wrapping_status"),
        "timing_sync_status": assessment.get("timing_sync_status"),
        "style_direction": assessment.get("style_direction") or {},
        "style_parameters": assessment.get("style_parameters") or {},
        "line_width_readback": assessment.get("line_width_readback") or {},
        "context_risk_status": assessment.get("context_risk_status"),
        "proof_limitations": assessment.get("proof_limitations") or [],
        "recommended_next_action": assessment.get("recommended_next_action") or [],
    }


def _missing_visual_proof_reason(assessment: dict[str, Any]) -> str:
    status = str(assessment.get("visual_proof_status") or "missing")
    typography = str(assessment.get("typography_status") or "")
    safe_area = str(assessment.get("safe_area_status") or "")
    if "no_subtitle_overlay" in status or "no_subtitle_overlay" in typography or "no_subtitle_overlay" in safe_area:
        return "source frame exists but subtitle-overlay proof is missing"
    if status == "missing":
        return "visual proof artifact is missing"
    return "visual proof exists but still requires human review"


def _aggregate_visual_proof_status(cuts: list[dict[str, Any]]) -> str:
    blocked = [
        cut
        for cut in cuts
        if "no_subtitle_overlay" in str((cut.get("visual_proof") or {}).get("status"))
        or "visual_proof_required" in str((cut.get("visual_proof") or {}).get("typography_status"))
        or "visual_proof_required" in str((cut.get("visual_proof") or {}).get("safe_area_status"))
    ]
    if blocked:
        return "blocked_no_cut_002_cut_003_overlay_proof"
    if any((cut.get("visual_proof") or {}).get("status") == "missing" for cut in cuts):
        return "blocked_missing_visual_proof"
    return "available_requires_human_review"


def _boundary_flags(cut_decision: dict[str, Any], visual_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": str(
            cut_decision.get("rights_status") or visual_report.get("rights_status") or "pending"
        ),
        "production_usage_allowed": False,
    }


def _allowed_values() -> dict[str, list[str]]:
    return {
        "proxy_decision": PROXY_DECISION_VALUES,
        "boundary_request": BOUNDARY_REQUEST_VALUES,
        "context_risk_handling": CONTEXT_RISK_HANDLING_VALUES,
        "analyst_action": ANALYST_ACTION_VALUES,
        "downstream_target": DOWNSTREAM_TARGET_VALUES,
    }


def _subtitle_index(edit_pack: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for subtitle in edit_pack.get("subtitles") or []:
        if not isinstance(subtitle, dict):
            continue
        cut_id = subtitle.get("cut_id")
        if cut_id is None:
            continue
        index.setdefault(str(cut_id), []).append(
            {
                "id": subtitle.get("id"),
                "start_seconds": subtitle.get("start_seconds"),
                "end_seconds": subtitle.get("end_seconds"),
                "text": subtitle.get("text") or "",
            }
        )
    return index


def _subtitle_rows_from_chapter(chapter: dict[str, Any]) -> list[dict[str, Any]]:
    sample = str(chapter.get("source_text_sample") or "")
    if not sample:
        return []
    return [{"id": None, "start_seconds": None, "end_seconds": None, "text": sample}]


def _csv_rows(patch_template: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for revision in patch_template.get("revisions") or []:
        rows.append({column: str(revision.get(column, "") or "") for column in CSV_COLUMNS})
    return rows


def _text_review_html(review: dict[str, Any]) -> str:
    rows = "\n".join(_text_cut_row_html(cut, include_operator=False) for cut in review.get("cuts") or [])
    return _html_page(
        title="cut_002 / cut_003 Text Proxy Review",
        summary=_summary_html(review),
        rows=rows,
        extra="<p>This surface is text/proxy review only. It records no operator decision.</p>",
    )


def _handoff_html(handoff: dict[str, Any]) -> str:
    rows = "\n".join(_text_cut_row_html(cut, include_operator=True) for cut in handoff.get("cuts") or [])
    values = _allowed_values_html(handoff.get("allowed_values") or {})
    return _html_page(
        title="cut_002 / cut_003 Operator Proxy Decision Handoff",
        summary=_summary_html(handoff),
        rows=rows,
        extra=(
            "<p>Fill the JSON/CSV patch template only with operator decisions. "
            "Defaults are intentionally blank, none, noop, or undecided.</p>"
            + values
        ),
    )


def _html_page(*, title: str, summary: str, rows: str, extra: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.45; margin: 24px; color: #202020; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #cfcfcf; padding: 6px; vertical-align: top; }}
    th {{ background: #f3f3f3; }}
    code {{ background: #f6f6f6; padding: 1px 3px; }}
    .warn {{ color: #7a3b00; font-weight: 700; }}
    .muted {{ color: #555; }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <p class="warn">Operator decision surface only: visual proof blocked for subtitle overlay; rights pending; production_candidate=false.</p>
  <section>
    <h2>Top Summary</h2>
{summary}
  </section>
  <section>
    <h2>Cut Readback</h2>
    <table>
      <thead>
        <tr>
          <th>cut</th><th>context</th><th>duration</th><th>subtitle load</th>
          <th>visual proof</th><th>subtitle text</th><th>operator fields</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </section>
  <section>
    <h2>Use</h2>
{extra}
  </section>
</body>
</html>
"""


def _summary_html(payload: dict[str, Any]) -> str:
    boundary = payload.get("boundary_flags") or {}
    source_media = payload.get("source_media_status") or {}
    return (
        "    <dl>"
        f"<dt>episode_id</dt><dd>{escape(str(payload.get('episode_id', '')))}</dd>"
        f"<dt>scope</dt><dd>{escape(str(payload.get('scope', '')))}</dd>"
        f"<dt>target cuts</dt><dd>{escape(', '.join(payload.get('target_cuts') or []))}</dd>"
        f"<dt>source media</dt><dd>{escape(str(source_media.get('status', 'unknown')))}</dd>"
        f"<dt>visual proof</dt><dd>{escape(str(payload.get('visual_proof_status', '')))}</dd>"
        f"<dt>boundary</dt><dd>production_candidate={escape(str(boundary.get('production_candidate', False)).lower())}; "
        f"creative_acceptance={escape(str(boundary.get('creative_acceptance', False)).lower())}; "
        f"publish_acceptance={escape(str(boundary.get('publish_acceptance', False)).lower())}; "
        f"rights_status={escape(str(boundary.get('rights_status', 'unknown')))}; "
        f"production_usage_allowed={escape(str(boundary.get('production_usage_allowed', False)).lower())}</dd>"
        "    </dl>"
    )


def _text_cut_row_html(cut: dict[str, Any], *, include_operator: bool) -> str:
    subtitles = "<br>".join(
        escape(str(item.get("text", ""))) for item in cut.get("subtitle_text") or []
    )
    visual = cut.get("visual_proof") or {}
    line_wrap = cut.get("line_wrap_proxy") or {}
    style_direction = visual.get("style_direction") or {}
    style_parameters = visual.get("style_parameters") or {}
    line_width = visual.get("line_width_readback") or {}
    style_readback = "<br>".join(
        [
            f"style_preset={escape(str(style_direction.get('preset_name', '')))}",
            f"style_slot={escape(str(style_parameters.get('style_slot', '')))}",
            f"max_raw_eaw={escape(str(line_width.get('max_raw_line_eaw', '')))}",
            f"needs_wrap_watch={escape(str(line_width.get('needs_wrap_count', '')))}",
        ]
    )
    operator = ""
    if include_operator:
        fields = cut.get("operator_input_fields") or {}
        operator = "<br>".join(
            f"{escape(key)}={escape(str(value))}"
            for key, value in fields.items()
            if key != "retained_context_risk_readback"
        )
    return (
        "        <tr>"
        f"<td>{escape(str(cut.get('cut_id', '')))}<br>{escape(str(cut.get('chapter_id', '')))}</td>"
        f"<td>{escape(str(cut.get('context_status', '')))}<br>"
        f"retained_context_risk={escape(str(cut.get('retained_context_risk', False)).lower())}</td>"
        f"<td>{escape(str(cut.get('duration_seconds', '')))}s</td>"
        f"<td>subs={escape(str(cut.get('subtitle_count', '')))}<br>"
        f"density={escape(str(cut.get('subtitle_density', '')))}<br>"
        f"max_eaw={escape(str(line_wrap.get('max_raw_eaw', '')))}<br>"
        f"needs_wrap={escape(str(line_wrap.get('needs_wrap_count', '')))}</td>"
        f"<td>{escape(str(visual.get('status', '')))}<br>"
        f"{escape(str(cut.get('missing_visual_proof_reason', '')))}<br>{style_readback}</td>"
        f"<td>{subtitles}</td>"
        f"<td>{operator}</td>"
        "</tr>"
    )


def _allowed_values_html(allowed_values: dict[str, list[str]]) -> str:
    chunks = []
    for key, values in allowed_values.items():
        chunks.append(
            f"<h3>{escape(key)}</h3><ul>"
            + "".join(f"<li><code>{escape(str(value))}</code></li>" for value in values)
            + "</ul>"
        )
    return "\n".join(chunks)


def _warnings(visual_proof_status: str) -> list[str]:
    return [
        "This handoff is not production acceptance.",
        "No production render is executed.",
        "No source transcript or official subtitle track is mutated.",
        "Operator fields remain blank, none, noop, or undecided until human input.",
        f"visual_proof_status={visual_proof_status}; typography, safe-area, line wrapping, and timing sync are not passed.",
        "rights_status=pending; production/public usage is not allowed.",
        "production_candidate remains false.",
    ]


def _load_required_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise OperatorProxyDecisionHandoffError(f"missing required artifact: {path}")
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise OperatorProxyDecisionHandoffError(f"expected JSON object: {path}")
    return payload


def _load_optional_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        return _load_required_json(path)
    except (OSError, json.JSONDecodeError, OperatorProxyDecisionHandoffError):
        return {}


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
        f.write("\n")


def _write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _episode_id(
    episode_dir: Path,
    board: dict[str, Any],
    cut_decision: dict[str, Any],
    visual_report: dict[str, Any],
) -> str:
    return str(
        board.get("episode_id")
        or cut_decision.get("episode_id")
        or visual_report.get("episode_id")
        or episode_dir.name
    )


def _resolve_display_path(path: Any, base: Path) -> Path | None:
    if not path:
        return None
    raw = Path(str(path))
    return raw if raw.is_absolute() else base / raw


def _display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def _number(*values: Any) -> float:
    for value in values:
        if value is None:
            continue
        try:
            return round(float(value), 3)
        except (TypeError, ValueError):
            continue
    return 0.0


def _int(*values: Any) -> int:
    for value in values:
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
