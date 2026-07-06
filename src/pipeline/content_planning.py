"""CPD-01 content candidate and channel strategy dashboard builder.

The builder is intentionally local/offline-first. It reads fixture or manual
seed metadata, produces transparent scoring readback, and writes static review
artifacts without fetching media, using OAuth, or making rights/publication
claims.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_ID = "clippipegen.content_planning_dashboard.v0"
DEFAULT_ARTIFACT_ID = "clip-cpd01-content-candidate-dashboard-v0-001"
DEFAULT_CANDIDATES_FILENAME = "content_candidates.json"
DEFAULT_STRATEGY_FILENAME = "channel_strategy.json"
DEFAULT_DASHBOARD_FILENAME = "content_dashboard.html"
DEFAULT_GENERATED_AT = "2026-07-06"

SCORE_FIELDS = (
    "expected_edit_value",
    "thumbnailability",
    "editability",
    "audience_fit",
    "novelty_or_trend_signal",
)
SEVERITY_PENALTY = {
    "low": 2,
    "medium": 5,
    "high": 10,
}


class ContentPlanningError(ValueError):
    """Raised when content planning input cannot be normalized."""


def build_content_candidate_dashboard(
    *,
    fixture_path: Path,
    output_dir: Path,
    base_dir: Path,
    generated_at: str = DEFAULT_GENERATED_AT,
    artifact_id: str = DEFAULT_ARTIFACT_ID,
) -> dict[str, Any]:
    """Read fixture metadata and write CPD-01 JSON/HTML review artifacts."""

    fixture = load_fixture(fixture_path)
    candidates = normalize_candidates(fixture)
    if not candidates:
        raise ContentPlanningError("fixture must contain at least one candidate")

    strategies = build_channel_strategies(fixture=fixture, candidates=candidates)
    gate_readback = build_gate_readback(candidates)
    source = fixture.get("source") if isinstance(fixture.get("source"), dict) else {}
    source_mode = str(fixture.get("source_mode") or source.get("mode") or "fixture")

    candidate_payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": {
            "mode": source_mode,
            "fixture_path": display_path(fixture_path, base_dir),
            "network_required": False,
            "fixture_readback": str(
                source.get("readback")
                or "local fixture only; public metadata is not refreshed live"
            ),
        },
        "summary": summarize_candidates(candidates),
        "gate_readback": gate_readback,
        "candidates": candidates,
    }
    strategy_payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": "v0",
        "artifact_id": artifact_id,
        "generated_at": generated_at,
        "source": candidate_payload["source"],
        "summary": summarize_strategies(strategies),
        "gate_readback": gate_readback,
        "strategies": strategies,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_path = output_dir / DEFAULT_CANDIDATES_FILENAME
    strategy_path = output_dir / DEFAULT_STRATEGY_FILENAME
    dashboard_path = output_dir / DEFAULT_DASHBOARD_FILENAME
    write_json(candidate_payload, candidates_path)
    write_json(strategy_payload, strategy_path)
    write_text(
        render_content_dashboard_html(
            candidates_payload=candidate_payload,
            strategy_payload=strategy_payload,
            candidates_path=candidates_path,
            strategy_path=strategy_path,
            dashboard_path=dashboard_path,
            base_dir=base_dir,
        ),
        dashboard_path,
    )

    return {
        "artifact_id": artifact_id,
        "candidate_count": len(candidates),
        "strategy_count": len(strategies),
        "top_candidate_id": candidates[0]["candidate_id"],
        "candidates_path": candidates_path,
        "strategy_path": strategy_path,
        "dashboard_path": dashboard_path,
        "candidate_payload": candidate_payload,
        "strategy_payload": strategy_payload,
    }


def load_fixture(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise ContentPlanningError(f"fixture is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContentPlanningError(f"fixture is not valid JSON: {path}") from exc

    if isinstance(payload, list):
        payload = {"source_mode": "fixture", "candidates": payload}
    if not isinstance(payload, dict):
        raise ContentPlanningError("fixture root must be an object or candidate list")
    if not isinstance(payload.get("candidates"), list):
        raise ContentPlanningError("fixture.candidates must be a list")
    return payload


def normalize_candidates(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    source = fixture.get("source") if isinstance(fixture.get("source"), dict) else {}
    default_source_mode = str(fixture.get("source_mode") or source.get("mode") or "fixture")
    normalized = [
        normalize_candidate(raw, default_source_mode=default_source_mode)
        for raw in fixture.get("candidates", [])
        if isinstance(raw, dict)
    ]
    normalized.sort(
        key=lambda row: (-int(row["score_total"]), str(row["candidate_id"]))
    )
    return normalized


def normalize_candidate(raw: dict[str, Any], *, default_source_mode: str) -> dict[str, Any]:
    candidate_id = str(raw.get("candidate_id") or "").strip()
    if not candidate_id:
        raise ContentPlanningError("candidate_id is required")

    risk_flags = normalize_risk_flags(raw.get("risk_flags"))
    score_components = score_candidate(raw, risk_flags)
    rights_readback = normalize_rights_readback(raw.get("rights_readback"))
    topic_tags = as_string_list(raw.get("topic_tags"))
    proposed_titles = as_string_list(
        raw.get("proposed_clip_titles") or raw.get("title_hooks")
    )
    score_total = score_components["score_total"]

    return {
        "candidate_id": candidate_id,
        "source_mode": str(raw.get("source_mode") or default_source_mode),
        "source_url": str(raw.get("source_url") or ""),
        "source_ref": str(raw.get("source_ref") or raw.get("source_url") or ""),
        "channel_name": str(raw.get("channel_name") or "unknown"),
        "talent": as_string_list(raw.get("talent")),
        "group": str(raw.get("group") or "unknown"),
        "language": str(raw.get("language") or "unknown"),
        "title": str(raw.get("title") or "untitled candidate"),
        "published_at": str(raw.get("published_at") or "unknown"),
        "duration_seconds": coerce_int(raw.get("duration_seconds")),
        "topic_tags": topic_tags,
        "clip_angle": str(raw.get("clip_angle") or "needs angle review"),
        "proposed_clip_titles": proposed_titles,
        "title_hooks": proposed_titles,
        "expected_edit_value": component_readback(raw, "expected_edit_value"),
        "thumbnailability": component_readback(raw, "thumbnailability"),
        "editability": component_readback(raw, "editability"),
        "audience_fit": component_readback(raw, "audience_fit"),
        "novelty_or_trend_signal": component_readback(raw, "novelty_or_trend_signal"),
        "risk_flags": risk_flags,
        "rights_readback": rights_readback,
        "next_action": str(raw.get("next_action") or default_next_action(risk_flags)),
        "score_total": score_total,
        "score_components": score_components["components"],
        "score_explanation": score_components["explanation"],
    }


def score_candidate(raw: dict[str, Any], risk_flags: list[dict[str, str]]) -> dict[str, Any]:
    signals = raw.get("signals") if isinstance(raw.get("signals"), dict) else {}
    components: dict[str, int] = {}
    for field in SCORE_FIELDS:
        components[field] = bounded_score(signals.get(field), raw.get(field))

    risk_penalty = sum(
        SEVERITY_PENALTY.get(flag.get("severity", "low"), 2) for flag in risk_flags
    )
    positive_total = sum(components.values())
    score_total = max(0, min(100, positive_total - risk_penalty))
    explanation = [
        f"{field}={score}" for field, score in components.items()
    ]
    if risk_penalty:
        explanation.append(f"risk_penalty=-{risk_penalty}")
    return {
        "score_total": score_total,
        "components": {**components, "risk_penalty": -risk_penalty},
        "explanation": "; ".join(explanation),
    }


def build_channel_strategies(
    *,
    fixture: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    seeds = fixture.get("strategy_seeds")
    if isinstance(seeds, list) and seeds:
        strategies = [
            normalize_strategy_seed(seed, candidates)
            for seed in seeds
            if isinstance(seed, dict)
        ]
    else:
        strategies = [default_strategy(candidates)]
    strategies = [strategy for strategy in strategies if strategy.get("candidate_ids")]
    strategies.sort(key=lambda row: (row["strategy_id"]))
    return strategies


def normalize_strategy_seed(
    seed: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_ids = as_string_list(seed.get("candidate_ids"))
    if not candidate_ids:
        tags = set(as_string_list(seed.get("candidate_filter_tags")))
        candidate_ids = [
            candidate["candidate_id"]
            for candidate in candidates
            if tags.intersection(candidate.get("topic_tags") or [])
        ]
    if not candidate_ids:
        candidate_ids = [candidate["candidate_id"] for candidate in candidates[:3]]

    candidate_index = {candidate["candidate_id"]: candidate for candidate in candidates}
    supporting = [candidate_index[cid] for cid in candidate_ids if cid in candidate_index]
    return {
        "strategy_id": str(seed.get("strategy_id") or "strategy_default"),
        "target_audience": str(seed.get("target_audience") or "JP clip viewers"),
        "content_pillars": as_string_list(seed.get("content_pillars")),
        "recommended_series_formats": as_string_list(seed.get("recommended_series_formats")),
        "cadence_hint": str(seed.get("cadence_hint") or "1-2 reviewable candidates per week"),
        "thumbnail_direction_hint": str(
            seed.get("thumbnail_direction_hint")
            or "large emotion readback plus one short hook"
        ),
        "editing_style_hint": str(
            seed.get("editing_style_hint")
            or "short context setup, fast payoff, preserve source readback"
        ),
        "candidate_ids": [candidate["candidate_id"] for candidate in supporting],
        "risk_readback_notes": strategy_risk_notes(supporting),
        "score_average": average_score(supporting),
        "next_action": str(seed.get("next_action") or "review top supporting candidate"),
    }


def default_strategy(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    tags = Counter(
        tag for candidate in candidates[:5] for tag in candidate.get("topic_tags", [])
    )
    pillars = [tag for tag, _ in tags.most_common(4)] or ["short comedy", "reaction"]
    return {
        "strategy_id": "strategy_fixture_top_candidates",
        "target_audience": "既存 hololive / VTuber 切り抜き視聴者",
        "content_pillars": pillars,
        "recommended_series_formats": [
            "短尺リアクション",
            "聞き間違い / 勘違いコント",
            "関係性が分かる掛け合い",
        ],
        "cadence_hint": "fixture 上位 2-3 件を週次レビュー候補にする",
        "thumbnail_direction_hint": "人物名 + 感情ワード + 1 カットの表情差分を優先",
        "editing_style_hint": "開始 2 秒で状況、10-25 秒で payoff を見せる",
        "candidate_ids": [candidate["candidate_id"] for candidate in candidates[:3]],
        "risk_readback_notes": strategy_risk_notes(candidates[:3]),
        "score_average": average_score(candidates[:3]),
        "next_action": "上位候補の source VOD を人間が確認し、episode seed 化するか決める",
    }


def build_gate_readback(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    rights_statuses = Counter(
        str((candidate.get("rights_readback") or {}).get("status") or "unknown")
        for candidate in candidates
    )
    return {
        "offline_first": True,
        "network_required": False,
        "media_downloaded": False,
        "oauth_or_credentials_used": False,
        "production_candidate": False,
        "production_usage_allowed": False,
        "publishing_acceptance": False,
        "public_use_permission": False,
        "rights_status_counts": dict(sorted(rights_statuses.items())),
        "readback_note": (
            "Candidate planning is allowed with pending/unverified rights, "
            "but public use, publishing, monetization, and production claims stay gated."
        ),
    }


def summarize_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "candidate_count": len(candidates),
        "top_candidate_id": candidates[0]["candidate_id"] if candidates else "",
        "score_min": min((candidate["score_total"] for candidate in candidates), default=0),
        "score_max": max((candidate["score_total"] for candidate in candidates), default=0),
        "needs_human_review_count": sum(
            1 for candidate in candidates if "review" in candidate["next_action"]
        ),
    }


def summarize_strategies(strategies: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "strategy_count": len(strategies),
        "strategy_ids": [strategy["strategy_id"] for strategy in strategies],
    }


def render_content_dashboard_html(
    *,
    candidates_payload: dict[str, Any],
    strategy_payload: dict[str, Any],
    candidates_path: Path,
    strategy_path: Path,
    dashboard_path: Path,
    base_dir: Path,
) -> str:
    candidates = candidates_payload["candidates"]
    strategies = strategy_payload["strategies"]
    gates = candidates_payload["gate_readback"]
    top = candidates[0]
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>CPD-01 Content Candidate Dashboard</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,'Yu Gothic','Meiryo',sans-serif;margin:24px;line-height:1.5;color:#1f2933;background:#f7f8fa}",
            "main{max-width:1180px;margin:0 auto}",
            "section{margin:18px 0;padding:16px;background:#fff;border:1px solid #d8dde5;border-radius:8px}",
            "h1{font-size:28px;margin:0 0 6px}h2{font-size:19px;margin:0 0 12px}h3{font-size:16px;margin:0 0 8px}",
            "table{width:100%;border-collapse:collapse;font-size:14px;table-layout:fixed}",
            "th,td{border-bottom:1px solid #e5e8ee;padding:8px;text-align:left;vertical-align:top;overflow-wrap:anywhere}",
            "th{background:#eef3f8}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}",
            ".card{border:1px solid #d8dde5;border-radius:8px;padding:12px;background:#fbfcfe}",
            ".score{font-size:26px;font-weight:700}.badge{display:inline-block;border:1px solid #b8c7d9;background:#eef3fa;border-radius:999px;padding:2px 8px;margin:2px;font-size:12px}",
            ".gate{border-color:#e3b341;background:#fffaf0}.muted{color:#5f6b7a}.risk{color:#8a4b00}code{background:#eef1f5;padding:2px 4px;border-radius:4px}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>CPD-01 Content Candidate / Channel Strategy Dashboard v0</h1>",
            '<p class="muted">ローカル fixture だけで生成した、次に何を切り抜くかを決めるための読み取り専用ダッシュボードです。</p>',
            _summary_html(candidates_payload, top, candidates_path, strategy_path, base_dir),
            _candidate_cards_html(candidates),
            _strategy_cards_html(strategies),
            _gate_html(gates),
            _next_actions_html(candidates, dashboard_path, base_dir),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def normalize_risk_flags(value: Any) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            code = str(item.get("code") or "risk").strip()
            severity = str(item.get("severity") or "low").strip().lower()
            note = str(item.get("note") or "").strip()
        else:
            code = str(item).strip()
            severity = "low"
            note = ""
        if not code:
            continue
        if severity not in SEVERITY_PENALTY:
            severity = "low"
        flags.append({"code": code, "severity": severity, "note": note})
    return flags


def normalize_rights_readback(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        status = str(value.get("status") or "unknown")
        notes = as_string_list(value.get("notes"))
        source = str(value.get("source") or "fixture")
    else:
        status = str(value or "unknown")
        notes = []
        source = "fixture"
    return {
        "status": status,
        "source": source,
        "notes": notes,
        "hard_gate": False,
    }


def component_readback(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if isinstance(value, str) and value.strip():
        return value.strip()
    signals = raw.get("signals") if isinstance(raw.get("signals"), dict) else {}
    score = bounded_score(signals.get(field), value)
    return f"{score}/20"


def bounded_score(primary: Any, secondary: Any = None) -> int:
    for value in (primary, secondary):
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if number <= 1:
            number *= 20
        return int(max(0, min(20, round(number))))
    return 10


def default_next_action(risk_flags: list[dict[str, str]]) -> str:
    if any(flag["severity"] == "high" for flag in risk_flags):
        return "needs human review before episode seed"
    return "inspect VOD before episode seed"


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, list):
        return [str(value)]
    return [str(item) for item in value if str(item).strip()]


def coerce_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def strategy_risk_notes(candidates: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    rights_counts = Counter(
        str((candidate.get("rights_readback") or {}).get("status") or "unknown")
        for candidate in candidates
    )
    if rights_counts:
        notes.append(
            "rights_status_counts="
            + ", ".join(f"{status}:{count}" for status, count in sorted(rights_counts.items()))
        )
    risky = [
        candidate["candidate_id"]
        for candidate in candidates
        if candidate.get("risk_flags")
    ]
    if risky:
        notes.append("risk_flags_present=" + ", ".join(risky))
    notes.append("production/public/publishing acceptance remains false")
    return notes


def average_score(candidates: list[dict[str, Any]]) -> int:
    if not candidates:
        return 0
    return round(sum(int(candidate["score_total"]) for candidate in candidates) / len(candidates))


def display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summary_html(
    payload: dict[str, Any],
    top: dict[str, Any],
    candidates_path: Path,
    strategy_path: Path,
    base_dir: Path,
) -> str:
    summary = payload["summary"]
    return f"""
  <section>
    <h2>生成サマリー</h2>
    <table>
      <tr><th>artifact_id</th><td>{escape(payload["artifact_id"])}</td></tr>
      <tr><th>候補数</th><td>{summary["candidate_count"]}</td></tr>
      <tr><th>最高スコア候補</th><td>{escape(top["candidate_id"])} / {top["score_total"]}</td></tr>
      <tr><th>machine JSON</th><td><code>{escape(display_path(candidates_path, base_dir))}</code><br><code>{escape(display_path(strategy_path, base_dir))}</code></td></tr>
      <tr><th>入力</th><td>{escape(payload["source"]["fixture_path"])} / network_required=false</td></tr>
    </table>
  </section>"""


def _candidate_cards_html(candidates: list[dict[str, Any]]) -> str:
    rows = []
    for candidate in candidates:
        tags = "".join(
            f'<span class="badge">{escape(tag)}</span>'
            for tag in candidate.get("topic_tags", [])
        )
        risks = "<br>".join(
            escape(f"{flag['code']} ({flag['severity']}): {flag.get('note', '')}")
            for flag in candidate.get("risk_flags", [])
        ) or "none"
        titles = "<br>".join(escape(title) for title in candidate.get("title_hooks", []))
        rows.append(
            f"""
      <div class="card">
        <h3>{escape(candidate["candidate_id"])}</h3>
        <div class="score">{candidate["score_total"]}</div>
        <p><strong>{escape(candidate["title"])}</strong></p>
        <p>{escape(candidate["clip_angle"])}</p>
        <p>{tags}</p>
        <table>
          <tr><th>talent</th><td>{escape(", ".join(candidate.get("talent") or []))}</td></tr>
          <tr><th>hooks</th><td>{titles}</td></tr>
          <tr><th>score</th><td>{escape(candidate["score_explanation"])}</td></tr>
          <tr><th>risk</th><td class="risk">{risks}</td></tr>
          <tr><th>next</th><td>{escape(candidate["next_action"])}</td></tr>
        </table>
      </div>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>候補カード</h2>",
            '    <div class="grid">',
            *rows,
            "    </div>",
            "  </section>",
        ]
    )


def _strategy_cards_html(strategies: list[dict[str, Any]]) -> str:
    cards = []
    for strategy in strategies:
        cards.append(
            f"""
      <div class="card">
        <h3>{escape(strategy["strategy_id"])}</h3>
        <p><strong>対象:</strong> {escape(strategy["target_audience"])}</p>
        <p><strong>柱:</strong> {escape(", ".join(strategy.get("content_pillars") or []))}</p>
        <p><strong>シリーズ:</strong> {escape(", ".join(strategy.get("recommended_series_formats") or []))}</p>
        <p><strong>候補:</strong> {escape(", ".join(strategy.get("candidate_ids") or []))}</p>
        <p><strong>平均スコア:</strong> {strategy.get("score_average", 0)}</p>
        <p><strong>サムネ:</strong> {escape(strategy["thumbnail_direction_hint"])}</p>
        <p><strong>編集:</strong> {escape(strategy["editing_style_hint"])}</p>
        <p><strong>次:</strong> {escape(strategy["next_action"])}</p>
        <p class="muted">{escape(" / ".join(strategy.get("risk_readback_notes") or []))}</p>
      </div>"""
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>チャンネル戦略カード</h2>",
            '    <div class="grid">',
            *cards,
            "    </div>",
            "  </section>",
        ]
    )


def _gate_html(gates: dict[str, Any]) -> str:
    rights = ", ".join(
        f"{status}:{count}"
        for status, count in (gates.get("rights_status_counts") or {}).items()
    )
    return f"""
  <section class="gate">
    <h2>権利・ゲート readback</h2>
    <table>
      <tr><th>offline_first</th><td>{str(gates["offline_first"]).lower()}</td></tr>
      <tr><th>network_required</th><td>{str(gates["network_required"]).lower()}</td></tr>
      <tr><th>media_downloaded</th><td>{str(gates["media_downloaded"]).lower()}</td></tr>
      <tr><th>OAuth / credentials</th><td>{str(gates["oauth_or_credentials_used"]).lower()}</td></tr>
      <tr><th>rights_status_counts</th><td>{escape(rights)}</td></tr>
      <tr><th>production/public</th><td>production_candidate=false; production_usage_allowed=false; publishing_acceptance=false; public_use_permission=false</td></tr>
      <tr><th>note</th><td>{escape(gates["readback_note"])}</td></tr>
    </table>
  </section>"""


def _next_actions_html(candidates: list[dict[str, Any]], dashboard_path: Path, base_dir: Path) -> str:
    actions = []
    for candidate in candidates[:5]:
        actions.append(
            f"<li><strong>{escape(candidate['candidate_id'])}</strong>: {escape(candidate['next_action'])}</li>"
        )
    return "\n".join(
        [
            "  <section>",
            "    <h2>次のアクション</h2>",
            "    <ul>",
            *actions,
            "    </ul>",
            f'    <p class="muted">Open: <code>{escape(display_path(dashboard_path, base_dir))}</code></p>',
            "  </section>",
        ]
    )
