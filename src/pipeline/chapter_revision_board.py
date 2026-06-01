"""Chapter revision board generation for JP-Pilot R3.

The board is an operator-editable decision surface. It reads existing review
artifacts and writes a static HTML board plus JSON/CSV patch templates. It does
not mutate source transcript data, change cut timing, render video, approve
rights, or create production output.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from .non_repo_artifact_handoff import build_source_identity
from .text_measure import measure_subtitle

SCHEMA_VERSION = "v1"
BOARD_KIND = "chapter_revision_board_v0"
PATCH_KIND = "chapter_revision_patch_v0"
DEFAULT_REVIEW_DIR_NAME = "jp_pilot01r3_cut_review"
WRAP_EAW = 40

CHAPTER_ACTION_VALUES = [
    "undecided",
    "keep_as_candidate",
    "rewrite_script",
    "rewrite_display_subtitle",
    "adjust_boundary",
    "split_chapter",
    "merge_with_previous",
    "merge_with_next",
    "reject_candidate",
    "defer",
    "needs_visual_proof",
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
ROLLBACK_SIGNAL_VALUES = [
    "undecided",
    "local_rewrite_ok",
    "boundary_adjustment_ok",
    "split_chapter",
    "merge_with_previous",
    "merge_with_next",
    "source_not_suitable",
    "rights_blocked",
    "production_design_needed",
    "defer",
]
ANALYST_ACTION_VALUES = [
    "undecided",
    "noop",
    "normalize_operator_notes",
    "apply_boundary_adjustment",
    "regenerate_subtitle_drafts",
    "rewrite_display_script_layer",
    "create_render_plan",
    "regenerate_representative_diagnostic",
    "create_nlmytgen_handoff",
    "escalate_rights_review",
    "mark_reject",
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
PRIORITY_VALUES = ["low", "normal", "high"]
REPRESENTATIVE_ROLES = {
    "cut_009": "short_passed_representative",
    "cut_004": "retained_context_risk_representative",
    "cut_008": "dense_subtitle_representative",
}
CSV_COLUMNS = [
    "chapter_id",
    "cut_id",
    "chapter_action",
    "editorial_intent",
    "script_override",
    "display_subtitle_request",
    "boundary_mode",
    "start_delta_seconds",
    "end_delta_seconds",
    "merge_with_previous",
    "merge_with_next",
    "split_points_seconds",
    "rollback_signal",
    "analyst_action",
    "downstream_target",
    "operator_note",
    "priority",
    "confidence",
]
REQUIRED_REVIEW_FILES = {
    "cut_review_packet": "cut_review_packet.json",
    "cut_review_report": "cut_review_report.html",
    "evidence_summary": "evidence_summary.json",
    "evidence_report": "evidence_summary.html",
    "non_repo_artifact_handoff": "non_repo_artifact_handoff.json",
    "non_repo_artifact_handoff_report": "non_repo_artifact_handoff.html",
    "cut_decision_speed_pass": "cut_decision_speed_pass.json",
    "cut_decision_speed_pass_report": "cut_decision_speed_pass.html",
    "regenerated_r3_baseline_acceptance": "regenerated_r3_baseline_acceptance.json",
    "regenerated_r3_baseline_acceptance_report": "regenerated_r3_baseline_acceptance.html",
    "production_subtitle_render_acceptance_plan": "production_subtitle_render_acceptance_plan.json",
    "production_subtitle_render_acceptance_plan_report": "production_subtitle_render_acceptance_plan.html",
}


class ChapterRevisionBoardError(Exception):
    """Raised when the chapter revision board cannot be built safely."""


def build_chapter_revision_board(
    *,
    episode_dir: Path,
    review_dir: Path | None = None,
    output_dir: Path | None = None,
    edit_pack_path: Path | None = None,
    transcript_path: Path | None = None,
    rights_manifest_path: Path | None = None,
    base_dir: Path | None = None,
    include_example: bool = True,
) -> dict[str, Any]:
    """Write board JSON/HTML and patch JSON/CSV templates.

    The function assumes the caller has already generated the R3 review packet
    and speed-first candidate decision artifacts. Missing review artifacts are
    treated as a blocked review surface rather than being silently skipped.
    """

    base = base_dir or Path.cwd()
    review_dir = review_dir or episode_dir / "review" / DEFAULT_REVIEW_DIR_NAME
    output_dir = output_dir or review_dir
    edit_pack_path = edit_pack_path or episode_dir / "edit_pack.json"
    transcript_path = transcript_path or episode_dir / "transcript.json"
    rights_manifest_path = rights_manifest_path or episode_dir / "rights_manifest.json"

    missing = _missing_required_artifacts(review_dir)
    if missing:
        raise ChapterRevisionBoardError(
            "missing required R3 review artifact(s): " + ", ".join(missing)
        )

    cut_review_packet = _load_json(review_dir / REQUIRED_REVIEW_FILES["cut_review_packet"])
    evidence_summary = _load_json(review_dir / REQUIRED_REVIEW_FILES["evidence_summary"])
    non_repo_handoff = _load_json(review_dir / REQUIRED_REVIEW_FILES["non_repo_artifact_handoff"])
    speed_pass = _load_json(review_dir / REQUIRED_REVIEW_FILES["cut_decision_speed_pass"])
    baseline_acceptance = _load_json(
        review_dir / REQUIRED_REVIEW_FILES["regenerated_r3_baseline_acceptance"]
    )
    acceptance_plan = _load_json(
        review_dir / REQUIRED_REVIEW_FILES["production_subtitle_render_acceptance_plan"]
    )
    edit_pack = _load_json_optional(edit_pack_path)
    transcript = _load_json_optional(transcript_path)
    rights_manifest = _load_json_optional(rights_manifest_path)
    material_ledger = _load_json_optional(episode_dir / "material_ledger.json")
    render_manifest = _load_json_optional(_first_existing(episode_dir / "renders", "*/render_manifest.json"))

    output_dir.mkdir(parents=True, exist_ok=True)
    board_path = output_dir / "chapter_revision_board.json"
    board_html_path = output_dir / "chapter_revision_board.html"
    patch_template_path = output_dir / "chapter_revision_patch.template.json"
    patch_csv_path = output_dir / "chapter_revision_patch.template.csv"
    example_path = output_dir / "chapter_revision_patch.example.json"

    source_identity = _source_identity(
        episode_dir=episode_dir,
        transcript=transcript,
        rights_manifest=rights_manifest,
        render_manifest=render_manifest,
        material_ledger=material_ledger,
        base_dir=base,
        candidates=[
            speed_pass.get("source_identity"),
            cut_review_packet.get("source_identity"),
            evidence_summary.get("source_identity"),
            non_repo_handoff.get("source_identity"),
            baseline_acceptance.get("source_identity"),
            acceptance_plan.get("source_identity"),
        ],
    )
    rights_status = _rights_status(
        rights_manifest,
        speed_pass.get("rights_status"),
        (evidence_summary.get("metrics") or {}).get("rights")
        if isinstance(evidence_summary.get("metrics"), dict)
        else None,
    )
    allowed_values = _allowed_values()
    chapters = _chapter_entries(
        speed_pass=speed_pass,
        cut_review_packet=cut_review_packet,
        edit_pack=edit_pack,
        rights_status=rights_status,
        allowed_values=allowed_values,
    )
    summary = _summary(chapters, cut_review_packet, speed_pass)
    boundary_flags = {
        "production_candidate": False,
        "creative_acceptance": False,
        "publish_acceptance": False,
        "rights_status": rights_status,
        "production_usage_allowed": False,
    }
    board = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "chapter_revision_board",
        "board_kind": BOARD_KIND,
        "created_at": _now(),
        "episode_id": _episode_id(episode_dir, cut_review_packet, speed_pass, transcript),
        "revision_readiness": "ready",
        "source_identity": source_identity,
        "boundary_flags": boundary_flags,
        "input_artifacts": _input_artifacts(review_dir, base),
        "summary": summary,
        "allowed_values": allowed_values,
        "operator_guidance": {
            "purpose": (
                "Use this board to record chapter-level editorial intent, display subtitle requests, "
                "cut-boundary requests, rollback signals, and downstream targets."
            ),
            "operator_writes": [
                "chapter_action",
                "editorial_intent",
                "script_override",
                "display_subtitle_request",
                "boundary_request",
                "rollback_signal",
                "analyst_action",
                "downstream_target",
                "operator_note",
            ],
            "agent_must_not_prefill": [
                "editorial_intent",
                "script_override",
                "display_subtitle_request",
                "operator_note",
            ],
            "patch_files": [
                _display_path(patch_template_path, base),
                _display_path(patch_csv_path, base),
            ],
        },
        "downstream_impact_guide": _downstream_impact_guide(),
        "non_goals": _non_goals(),
        "chapters": chapters,
    }
    patch_template = _patch_template(board, board_path, baseline_acceptance, speed_pass, base)
    csv_rows = _csv_rows(chapters)
    example = _patch_example(board, board_path, base) if include_example else None

    _write_json(board, board_path)
    board_html_path.write_text(_board_html(board, patch_template_path, patch_csv_path), encoding="utf-8")
    _write_json(patch_template, patch_template_path)
    _write_csv(csv_rows, patch_csv_path)
    if include_example and example is not None:
        _write_json(example, example_path)

    return {
        "board": board,
        "patch_template": patch_template,
        "board_path": board_path,
        "board_html_path": board_html_path,
        "patch_template_path": patch_template_path,
        "patch_csv_path": patch_csv_path,
        "example_path": example_path if include_example else None,
    }


def _chapter_entries(
    *,
    speed_pass: dict[str, Any],
    cut_review_packet: dict[str, Any],
    edit_pack: dict[str, Any],
    rights_status: str,
    allowed_values: dict[str, list[str]],
) -> list[dict[str, Any]]:
    speed_cuts = [
        c for c in speed_pass.get("cuts") or [] if isinstance(c, dict) and c.get("cut_id")
    ]
    packet_cuts = {
        str(c.get("cut_id")): c
        for c in cut_review_packet.get("cuts") or []
        if isinstance(c, dict) and c.get("cut_id")
    }
    if not speed_cuts and packet_cuts:
        speed_cuts = [
            {
                "cut_id": cut_id,
                "final_decision": "accept_candidate",
                "original_context_status": packet.get("context_status"),
                "retained_context_risk": packet.get("context_status") == "needs_review",
            }
            for cut_id, packet in packet_cuts.items()
        ]
    if not speed_cuts:
        raise ChapterRevisionBoardError("no cut decisions found for chapter revision board")

    subtitle_index = _subtitle_index(edit_pack)
    chapters: list[dict[str, Any]] = []
    for idx, speed_cut in enumerate(sorted(speed_cuts, key=lambda item: _cut_sort_key(item.get("cut_id"))), start=1):
        cut_id = str(speed_cut.get("cut_id"))
        packet_cut = packet_cuts.get(cut_id, {})
        cut_subtitles = subtitle_index.get(cut_id) or _preview_subtitles(packet_cut)
        start = _number(speed_cut.get("start_seconds"), packet_cut.get("start_seconds"), 0.0)
        end = _number(speed_cut.get("end_seconds"), packet_cut.get("end_seconds"), start)
        duration = _number(speed_cut.get("duration_seconds"), packet_cut.get("duration_seconds"), end - start)
        subtitle_count = _int(packet_cut.get("subtitle_event_count"), len(cut_subtitles))
        subtitle_density = _number(
            packet_cut.get("subtitle_density_per_second"),
            (subtitle_count / duration) if duration else 0.0,
        )
        chars_per_second = _number(packet_cut.get("subtitle_chars_per_second"), 0.0)
        line_wrap_proxy = _line_wrap_proxy(cut_subtitles)
        context_status = str(
            speed_cut.get("original_context_status")
            or packet_cut.get("context_status")
            or "unknown"
        )
        retained_context_risk = bool(
            speed_cut.get("retained_context_risk")
            or context_status == "needs_review"
        )
        chapter = {
            "chapter_id": f"ch_{idx:03d}",
            "source_cut_id": cut_id,
            "source_start_seconds": round(start, 3),
            "source_end_seconds": round(end, 3),
            "duration_seconds": round(max(0.0, duration), 3),
            "current_decision": str(speed_cut.get("final_decision") or "accept_candidate"),
            "decision_scope": str(speed_cut.get("decision_scope") or "candidate_seed_only"),
            "original_context_status": context_status,
            "retained_context_risk": retained_context_risk,
            "representative_role": REPRESENTATIVE_ROLES.get(cut_id),
            "source_text_sample": _source_text_sample(packet_cut),
            "subtitle_count": subtitle_count,
            "subtitle_density": round(subtitle_density, 3),
            "subtitle_chars_per_second": round(chars_per_second, 3),
            "max_line_length": line_wrap_proxy["max_raw_eaw"],
            "line_wrap_proxy": line_wrap_proxy,
            "timing_span": _timing_span(start, end, duration, cut_subtitles),
            "current_risks": _current_risks(
                context_status=context_status,
                retained_context_risk=retained_context_risk,
                subtitle_density=subtitle_density,
                chars_per_second=chars_per_second,
                line_wrap_proxy=line_wrap_proxy,
            ),
            "operator_fields": _operator_fields(),
            "allowed_values": allowed_values,
        }
        chapters.append(chapter)
    return chapters


def _patch_template(
    board: dict[str, Any],
    board_path: Path,
    baseline_acceptance: dict[str, Any],
    speed_pass: dict[str, Any],
    base: Path,
) -> dict[str, Any]:
    chapters = board.get("chapters") or []
    return {
        "schema_version": SCHEMA_VERSION,
        "patch_kind": PATCH_KIND,
        "created_at": _now(),
        "episode_id": board.get("episode_id"),
        "source_board_ref": _display_path(board_path, base),
        "reviewed_by": None,
        "operator_name": None,
        "patch_status": "draft",
        "applies_to": {
            "regenerated_r3_baseline_acceptance": _artifact_path_from_payload(
                baseline_acceptance,
                "regenerated_r3_baseline_acceptance.json",
            ),
            "cut_decision_speed_pass": _artifact_path_from_payload(
                speed_pass,
                "cut_decision_speed_pass.json",
            ),
        },
        "global_notes": "",
        "allowed_values": board.get("allowed_values"),
        "validation_notes": [
            "source transcript and official subtitle track remain evidence and are not patched here",
            "script_override is an editorial layer field",
            "display_subtitle_request is a subtitle surface request",
            "boundary_adjustment is a request for later edit_pack/cut-range work, not an immediate mutation",
            "rights_blocked routes to rights review and does not permit production usage",
            "production_candidate_request remains separate from production_candidate=false boundary flags",
        ],
        "revisions": [_patch_revision(chapter) for chapter in chapters],
    }


def _patch_revision(chapter: dict[str, Any]) -> dict[str, Any]:
    return {
        "chapter_id": chapter["chapter_id"],
        "cut_id": chapter["source_cut_id"],
        "chapter_action": "undecided",
        "editorial_intent": "",
        "script_override": "",
        "display_subtitle_request": "",
        "boundary_adjustment": {
            "mode": "none",
            "start_delta_seconds": None,
            "end_delta_seconds": None,
            "merge_with_previous": False,
            "merge_with_next": False,
            "split_points_seconds": [],
        },
        "rollback_signal": "undecided",
        "analyst_action": "undecided",
        "downstream_target": [],
        "operator_note": "",
        "priority": "normal",
        "confidence": "",
        "production_candidate_request": False,
        "rights_sensitive_note": "",
    }


def _patch_example(board: dict[str, Any], board_path: Path, base: Path) -> dict[str, Any]:
    chapters = board.get("chapters") or []
    first = chapters[0] if chapters else {"chapter_id": "ch_001", "source_cut_id": "cut_001"}
    return {
        "schema_version": SCHEMA_VERSION,
        "patch_kind": PATCH_KIND,
        "example_only": True,
        "non_authoritative_sample": True,
        "not_operator_decision": True,
        "source_board_ref": _display_path(board_path, base),
        "episode_id": board.get("episode_id"),
        "notes": [
            "This file is an example only. Do not treat it as an operator decision patch.",
            "Replace placeholder text with human review only if the operator explicitly chooses to use it.",
        ],
        "sample_revision": {
            "chapter_id": first.get("chapter_id"),
            "cut_id": first.get("source_cut_id"),
            "chapter_action": "adjust_boundary",
            "editorial_intent": "<operator-written intent goes here>",
            "script_override": "<optional editorial layer rewrite; does not mutate source transcript>",
            "display_subtitle_request": "<optional subtitle surface request>",
            "boundary_adjustment": {
                "mode": "adjust_start_and_end",
                "start_delta_seconds": -0.5,
                "end_delta_seconds": 0.8,
                "merge_with_previous": False,
                "merge_with_next": False,
                "split_points_seconds": [],
            },
            "rollback_signal": "boundary_adjustment_ok",
            "analyst_action": "apply_boundary_adjustment",
            "downstream_target": ["edit_pack", "subtitle_drafts"],
            "operator_note": "<operator note>",
            "priority": "normal",
            "confidence": "",
            "production_candidate_request": False,
            "rights_sensitive_note": "",
        },
    }


def _csv_rows(chapters: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for chapter in chapters:
        rows.append(
            {
                "chapter_id": str(chapter["chapter_id"]),
                "cut_id": str(chapter["source_cut_id"]),
                "chapter_action": "undecided",
                "editorial_intent": "",
                "script_override": "",
                "display_subtitle_request": "",
                "boundary_mode": "none",
                "start_delta_seconds": "",
                "end_delta_seconds": "",
                "merge_with_previous": "false",
                "merge_with_next": "false",
                "split_points_seconds": "",
                "rollback_signal": "undecided",
                "analyst_action": "undecided",
                "downstream_target": "",
                "operator_note": "",
                "priority": "normal",
                "confidence": "",
            }
        )
    return rows


def _board_html(
    board: dict[str, Any],
    patch_template_path: Path,
    patch_csv_path: Path,
) -> str:
    summary = board.get("summary") or {}
    boundary = board.get("boundary_flags") or {}
    source = board.get("source_identity") or {}
    rows = "\n".join(_chapter_row_html(chapter) for chapter in board.get("chapters") or [])
    vocabulary = _vocabulary_html(board.get("allowed_values") or {})
    impact = _impact_html(board.get("downstream_impact_guide") or [])
    non_goals = "<ul>" + "".join(
        f"<li>{escape(str(item))}</li>" for item in board.get("non_goals") or []
    ) + "</ul>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Chapter Revision Board - {escape(str(board.get("episode_id", "")))}</title>
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
  <h1>Chapter Revision Board</h1>
  <p class="warn">Working board only: not production acceptance. rights pending. production_candidate=false.</p>
  <section>
    <h2>Top Summary</h2>
    <dl>
      <dt>episode_id</dt><dd>{escape(str(board.get("episode_id", "")))}</dd>
      <dt>source</dt><dd>{escape(str(source.get("source_video_title") or source.get("source_video_identity") or "unknown"))} / YouTube ID {escape(str(source.get("youtube_id", "unknown")))}</dd>
      <dt>subtitle track</dt><dd>{escape(str(source.get("subtitle_track", "unknown")))}</dd>
      <dt>chapter count</dt><dd>{escape(str(summary.get("chapter_count", "")))}</dd>
      <dt>candidate decision</dt><dd>{escape(str(summary.get("current_decision", "")))}</dd>
      <dt>retained context risks</dt><dd>{escape(str(summary.get("retained_context_risk_count", "")))}</dd>
      <dt>boundary</dt><dd>production_candidate={escape(str(boundary.get("production_candidate", False)).lower())}; creative_acceptance={escape(str(boundary.get("creative_acceptance", False)).lower())}; publish_acceptance={escape(str(boundary.get("publish_acceptance", False)).lower())}; rights_status={escape(str(boundary.get("rights_status", "unknown")))}</dd>
    </dl>
  </section>
  <section>
    <h2>How To Use</h2>
    <ol>
      <li>Review each chapter row and decide whether the candidate stays, needs a rewrite, needs boundary work, should split/merge, or should be rejected/deferred.</li>
      <li>Write operator decisions into <code>{escape(str(patch_template_path.name))}</code> or spreadsheet-editable <code>{escape(str(patch_csv_path.name))}</code>.</li>
      <li>Leave unknown creative intent blank. The Agent should normalize and apply only decisions that the operator actually wrote.</li>
      <li>Use source transcript and official subtitle track as evidence. Do not patch them through this board.</li>
    </ol>
  </section>
  <section>
    <h2>Chapter Table</h2>
    <table>
      <thead>
        <tr>
          <th>chapter</th><th>cut</th><th>source range</th><th>context</th>
          <th>retained risk</th><th>density</th><th>source text sample</th>
          <th>current decision</th><th>operator fields</th><th>risks</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </section>
  <section>
    <h2>Decision Vocabulary</h2>
{vocabulary}
  </section>
  <section>
    <h2>Downstream Impact Guide</h2>
{impact}
  </section>
  <section>
    <h2>Non-Goals / Boundaries</h2>
{non_goals}
  </section>
</body>
</html>
"""


def _chapter_row_html(chapter: dict[str, Any]) -> str:
    fields = chapter.get("operator_fields") or {}
    risks = chapter.get("current_risks") or []
    field_readback = (
        f"chapter_action={escape(str(fields.get('chapter_action', '')))}<br>"
        f"editorial_intent={escape(str(fields.get('editorial_intent', '')))}<br>"
        f"script_override={escape(str(fields.get('script_override', '')))}<br>"
        f"display_subtitle_request={escape(str(fields.get('display_subtitle_request', '')))}<br>"
        f"boundary_request={escape(str(fields.get('boundary_request', '')))}<br>"
        f"rollback_signal={escape(str(fields.get('rollback_signal', '')))}<br>"
        f"analyst_action={escape(str(fields.get('analyst_action', '')))}<br>"
        f"downstream_target={escape(json.dumps(fields.get('downstream_target', []), ensure_ascii=False))}<br>"
        f"operator_note={escape(str(fields.get('operator_note', '')))}"
    )
    role = chapter.get("representative_role")
    role_html = f"<br><span class=\"muted\">{escape(str(role))}</span>" if role else ""
    return (
        "        <tr>"
        f"<td>{escape(str(chapter.get('chapter_id', '')))}</td>"
        f"<td>{escape(str(chapter.get('source_cut_id', '')))}{role_html}</td>"
        f"<td>{escape(str(chapter.get('source_start_seconds', '')))}-"
        f"{escape(str(chapter.get('source_end_seconds', '')))}<br>"
        f"{escape(str(chapter.get('duration_seconds', '')))}s</td>"
        f"<td>{escape(str(chapter.get('original_context_status', '')))}</td>"
        f"<td>{escape(str(chapter.get('retained_context_risk', False)).lower())}</td>"
        f"<td>subs={escape(str(chapter.get('subtitle_count', '')))}<br>"
        f"subs/sec={escape(str(chapter.get('subtitle_density', '')))}<br>"
        f"chars/sec={escape(str(chapter.get('subtitle_chars_per_second', '')))}<br>"
        f"max_eaw={escape(str(chapter.get('max_line_length', '')))}</td>"
        f"<td>{escape(str(chapter.get('source_text_sample', '')))}</td>"
        f"<td>{escape(str(chapter.get('current_decision', '')))}</td>"
        f"<td>{field_readback}</td>"
        f"<td>{'<br>'.join(escape(str(risk)) for risk in risks) if risks else ''}</td>"
        "</tr>"
    )


def _vocabulary_html(allowed_values: dict[str, list[str]]) -> str:
    chunks = []
    for key in ("chapter_action", "boundary_request", "rollback_signal", "analyst_action", "downstream_target"):
        values = allowed_values.get(key) or []
        chunks.append(
            f"<h3>{escape(key)}</h3><ul>"
            + "".join(f"<li><code>{escape(str(value))}</code></li>" for value in values)
            + "</ul>"
        )
    return "\n".join(chunks)


def _impact_html(items: list[dict[str, str]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('decision', '')))}</td>"
        f"<td>{escape(str(item.get('affects', '')))}</td>"
        f"<td>{escape(str(item.get('next_step', '')))}</td>"
        "</tr>"
        for item in items
    )
    return (
        "<table><thead><tr><th>decision</th><th>affects</th><th>next step</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def _operator_fields() -> dict[str, Any]:
    return {
        "editorial_intent": "",
        "script_override": "",
        "display_subtitle_request": "",
        "boundary_request": "none",
        "boundary_start_delta_seconds": None,
        "boundary_end_delta_seconds": None,
        "chapter_action": "undecided",
        "rollback_signal": "undecided",
        "analyst_action": "undecided",
        "downstream_target": [],
        "operator_note": "",
        "priority": "normal",
    }


def _allowed_values() -> dict[str, list[str]]:
    return {
        "chapter_action": CHAPTER_ACTION_VALUES,
        "boundary_request": BOUNDARY_REQUEST_VALUES,
        "rollback_signal": ROLLBACK_SIGNAL_VALUES,
        "analyst_action": ANALYST_ACTION_VALUES,
        "downstream_target": DOWNSTREAM_TARGET_VALUES,
        "priority": PRIORITY_VALUES,
    }


def _summary(
    chapters: list[dict[str, Any]],
    cut_review_packet: dict[str, Any],
    speed_pass: dict[str, Any],
) -> dict[str, Any]:
    retained = sum(1 for chapter in chapters if chapter.get("retained_context_risk") is True)
    context_counts: dict[str, int] = {}
    for chapter in chapters:
        status = str(chapter.get("original_context_status") or "unknown")
        context_counts[status] = context_counts.get(status, 0) + 1
    return {
        "chapter_count": len(chapters),
        "candidate_seed_count": len(
            [chapter for chapter in chapters if chapter.get("current_decision") == "accept_candidate"]
        ),
        "current_decision": "accept_candidate",
        "retained_context_risk_count": retained,
        "context_counts": context_counts,
        "source_cut_count": (cut_review_packet.get("summary") or {}).get("cut_count"),
        "speed_pass_policy": speed_pass.get("decision_policy"),
        "all_cuts_candidate_seed_only": True,
        "operator_decision_patch_required_for_next_mutation": True,
    }


def _input_artifacts(review_dir: Path, base: Path) -> dict[str, dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}
    for name, filename in REQUIRED_REVIEW_FILES.items():
        path = review_dir / filename
        artifacts[name] = {
            "path": _display_path(path, base),
            "exists": path.exists(),
            "role": _artifact_role(name),
        }
    return artifacts


def _artifact_role(name: str) -> str:
    if "report" in name:
        return "human-readable evidence"
    if name == "cut_decision_speed_pass":
        return "candidate seed decision input"
    if name == "cut_review_packet":
        return "cut metrics and context input"
    if name == "evidence_summary":
        return "source and artifact inventory input"
    if name == "non_repo_artifact_handoff":
        return "ignored local artifact boundary input"
    return "input evidence"


def _downstream_impact_guide() -> list[dict[str, str]]:
    return [
        {
            "decision": "keep_as_candidate",
            "affects": "render_plan / nlmytgen_handoff",
            "next_step": "carry the chapter forward as a candidate seed after operator confirmation",
        },
        {
            "decision": "rewrite_script",
            "affects": "editorial_script",
            "next_step": "create or update the editorial layer without touching source transcript evidence",
        },
        {
            "decision": "rewrite_display_subtitle",
            "affects": "subtitle_drafts",
            "next_step": "regenerate or hand-edit display subtitle requests for this chapter",
        },
        {
            "decision": "adjust_boundary / split_chapter / merge_*",
            "affects": "edit_pack",
            "next_step": "apply later cut-range changes from a reviewed patch, then regenerate dependent drafts",
        },
        {
            "decision": "reject_candidate / source_not_suitable",
            "affects": "source_selection",
            "next_step": "remove this candidate from downstream production planning",
        },
        {
            "decision": "rights_blocked",
            "affects": "rights_review",
            "next_step": "route to rights approval path; do not unlock production usage",
        },
    ]


def _non_goals() -> list[str]:
    return [
        "No production render is executed.",
        "No rights approval is performed.",
        "No publishing, OAuth, visibility change, or thumbnail setting is performed.",
        "No source transcript or official subtitle track is mutated.",
        "No browser save workflow, Electron operation, or drag-and-drop UI is implemented.",
        "No all-cuts production acceptance is implied.",
    ]


def _current_risks(
    *,
    context_status: str,
    retained_context_risk: bool,
    subtitle_density: float,
    chars_per_second: float,
    line_wrap_proxy: dict[str, Any],
) -> list[str]:
    risks: list[str] = []
    if retained_context_risk:
        risks.append("retained_context_risk")
    if context_status == "needs_review":
        risks.append("context_boundary_review_required")
    elif context_status not in {"passed", "unknown"}:
        risks.append(f"context_status_{context_status}")
    if subtitle_density >= 1.2 or chars_per_second >= 12.0:
        risks.append("reading_load_review_required")
    if line_wrap_proxy.get("needs_wrap_count", 0) > 0:
        risks.append("line_wrap_review_required")
    return risks


def _line_wrap_proxy(subtitles: list[dict[str, Any]]) -> dict[str, Any]:
    raw_widths: list[int] = []
    wrapped_widths: list[int] = []
    needs_wrap_count = 0
    for subtitle in subtitles:
        text = str(subtitle.get("text") or "")
        raw = measure_subtitle(text)
        wrapped = measure_subtitle(text, wrap_eaw=WRAP_EAW)
        raw_widths.append(raw.longest_line_eaw)
        wrapped_widths.append(wrapped.longest_line_eaw)
        if wrapped.needs_wrap:
            needs_wrap_count += 1
    return {
        "measurement_kind": "east_asian_width_proxy",
        "wrap_eaw": WRAP_EAW,
        "subtitle_count_measured": len(subtitles),
        "max_raw_eaw": max(raw_widths, default=0),
        "max_wrapped_line_eaw": max(wrapped_widths, default=0),
        "needs_wrap_count": needs_wrap_count,
        "proxy_only": True,
    }


def _timing_span(
    start: float,
    end: float,
    duration: float,
    subtitles: list[dict[str, Any]],
) -> dict[str, Any]:
    subtitle_starts = [_number(subtitle.get("start_seconds"), None) for subtitle in subtitles]
    subtitle_ends = [_number(subtitle.get("end_seconds"), None) for subtitle in subtitles]
    subtitle_starts = [value for value in subtitle_starts if value is not None]
    subtitle_ends = [value for value in subtitle_ends if value is not None]
    return {
        "source_start_seconds": round(start, 3),
        "source_end_seconds": round(end, 3),
        "duration_seconds": round(max(0.0, duration), 3),
        "subtitle_start_seconds": round(min(subtitle_starts), 3) if subtitle_starts else None,
        "subtitle_end_seconds": round(max(subtitle_ends), 3) if subtitle_ends else None,
    }


def _source_text_sample(packet_cut: dict[str, Any]) -> str:
    samples = packet_cut.get("segment_text_preview")
    if not isinstance(samples, list) or not samples:
        samples = packet_cut.get("subtitle_preview")
    if not isinstance(samples, list):
        return ""
    text = " / ".join(str(item) for item in samples[:3] if item is not None)
    return text[:240]


def _subtitle_index(edit_pack: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for subtitle in edit_pack.get("subtitles") or []:
        if not isinstance(subtitle, dict):
            continue
        cut_id = subtitle.get("cut_id")
        if cut_id is None:
            continue
        index.setdefault(str(cut_id), []).append(subtitle)
    return index


def _preview_subtitles(packet_cut: dict[str, Any]) -> list[dict[str, Any]]:
    preview = packet_cut.get("subtitle_preview")
    if not isinstance(preview, list):
        return []
    return [{"text": str(text)} for text in preview]


def _source_identity(
    *,
    episode_dir: Path,
    transcript: dict[str, Any],
    rights_manifest: dict[str, Any],
    render_manifest: dict[str, Any],
    material_ledger: dict[str, Any],
    base_dir: Path,
    candidates: list[Any],
) -> dict[str, Any]:
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate:
            return candidate
    return build_source_identity(
        episode_dir=episode_dir,
        transcript=transcript,
        rights=rights_manifest,
        render_manifest=render_manifest,
        material_ledger=material_ledger,
        base_dir=base_dir,
    )


def _rights_status(rights: dict[str, Any], *fallbacks: Any) -> str:
    compliance = rights.get("compliance_check") if isinstance(rights.get("compliance_check"), dict) else {}
    if compliance.get("status"):
        return str(compliance["status"])
    for fallback in fallbacks:
        if isinstance(fallback, str) and fallback:
            return fallback
        if isinstance(fallback, dict) and fallback.get("status"):
            return str(fallback["status"])
    return "missing"


def _missing_required_artifacts(review_dir: Path) -> list[str]:
    missing: list[str] = []
    for filename in REQUIRED_REVIEW_FILES.values():
        path = review_dir / filename
        if not path.exists():
            missing.append(str(path).replace("\\", "/"))
    return missing


def _artifact_path_from_payload(payload: dict[str, Any], default_name: str) -> str:
    outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
    for value in outputs.values():
        if isinstance(value, str) and value.endswith(default_name):
            return value
    return default_name


def _episode_id(
    episode_dir: Path,
    cut_review_packet: dict[str, Any],
    speed_pass: dict[str, Any],
    transcript: dict[str, Any],
) -> str:
    return str(
        cut_review_packet.get("episode_id")
        or speed_pass.get("episode_id")
        or transcript.get("episode_id")
        or episode_dir.name
    )


def _cut_sort_key(cut_id: Any) -> tuple[int, str]:
    text = str(cut_id)
    try:
        return int(text.rsplit("_", 1)[1]), text
    except (IndexError, ValueError):
        return 999999, text


def _number(*values: Any) -> float:
    for value in values:
        if value is None:
            continue
        try:
            return float(value)
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


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ChapterRevisionBoardError(f"expected JSON object: {path}")
    return payload


def _load_json_optional(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        return _load_json(path)
    except (OSError, json.JSONDecodeError, ChapterRevisionBoardError):
        return {}


def _first_existing(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    return next(iter(sorted(root.glob(pattern))), None)


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


def _display_path(path: Path | None, base: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
