from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


TIERS = ("contract-only", "static-reviewable", "playable-proxy", "fully-viewable")
TIER_RANK = {tier: index for index, tier in enumerate(TIERS)}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _sha256(path: Path, cache: dict[Path, str]) -> str:
    resolved = path.resolve()
    if resolved not in cache:
        digest = hashlib.sha256()
        with resolved.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        cache[resolved] = digest.hexdigest()
    return cache[resolved]


def _path_state(repo_root: Path, relative_path: str | None) -> dict | None:
    if not relative_path:
        return None
    path = repo_root / relative_path
    return {
        "path": relative_path,
        "present": path.is_file(),
        "byte_size": path.stat().st_size if path.is_file() else None,
    }


def _resolve_candidate(
    repo_root: Path,
    family: dict,
    candidate: dict,
    *,
    hash_local_media: bool,
    hash_cache: dict[Path, str],
) -> dict:
    contract = _path_state(repo_root, family["contract_path"])
    static = _path_state(repo_root, candidate.get("static_entrypoint"))
    entrypoint = _path_state(repo_root, candidate.get("local_entrypoint"))
    evidence = [_path_state(repo_root, path) for path in candidate.get("local_evidence", [])]
    media = []
    for row in candidate.get("local_media", []):
        state = _path_state(repo_root, row["path"])
        assert state is not None
        state["expected_sha256"] = row.get("expected_sha256")
        if state["present"] and hash_local_media:
            state["observed_sha256"] = _sha256(repo_root / row["path"], hash_cache)
            state["sha256_matches_expected"] = (
                not state["expected_sha256"]
                or state["expected_sha256"] == state["observed_sha256"]
            )
            if not state["sha256_matches_expected"]:
                raise ValueError(f"media SHA mismatch: {row['path']}")
        media.append(state)

    all_media_present = bool(media) and all(row["present"] for row in media)
    if candidate["target_tier"] == "fully-viewable" and entrypoint and entrypoint["present"] and all_media_present:
        observed_tier = "fully-viewable"
    elif candidate["target_tier"] == "playable-proxy" and entrypoint and entrypoint["present"]:
        observed_tier = "playable-proxy"
    elif static and static["present"]:
        observed_tier = "static-reviewable"
    elif contract and contract["present"]:
        observed_tier = "contract-only"
    else:
        raise ValueError(f"candidate has no materializable contract: {candidate['candidate_id']}")

    if TIER_RANK[observed_tier] > TIER_RANK[candidate["target_tier"]]:
        raise ValueError(f"observed tier exceeds target tier: {candidate['candidate_id']}")

    return {
        **candidate,
        "family_id": family["family_id"],
        "family_title": family["title"],
        "contract": contract,
        "static_entrypoint_state": static,
        "local_entrypoint_state": entrypoint,
        "local_evidence_state": evidence,
        "local_media_state": media,
        "observed_tier": observed_tier,
        "materialized_card": f"docs/benchmarks/candidates/{candidate['candidate_id']}.html",
    }


def _relative_href(from_file: Path, repo_root: Path, relative_path: str) -> str:
    target = repo_root / relative_path
    return Path(os.path.relpath(target, from_file.parent)).as_posix()


def _candidate_html(repo_root: Path, output_path: Path, row: dict) -> str:
    def link(path: str, label: str) -> str:
        return f'<a href="{html.escape(_relative_href(output_path, repo_root, path))}">{html.escape(label)}</a>'

    evidence_items = []
    for item in row["local_evidence_state"]:
        state = "present" if item["present"] else "missing"
        evidence_items.append(f"<li>{link(item['path'], item['path'])} <code>{state}</code></li>")
    media_items = []
    for item in row["local_media_state"]:
        digest = item.get("observed_sha256") or item.get("expected_sha256") or "not recorded"
        state = "present" if item["present"] else "missing"
        media_items.append(
            f"<li>{link(item['path'], item['path'])} <code>{state}</code> · {item.get('byte_size') or 0:,} bytes · SHA-256 <code>{html.escape(digest)}</code></li>"
        )
    entrypoint = row.get("local_entrypoint_state")
    entrypoint_html = "none"
    if entrypoint:
        state = "present" if entrypoint["present"] else "missing"
        entrypoint_html = f"{link(entrypoint['path'], entrypoint['path'])} <code>{state}</code>"
    static = row.get("static_entrypoint_state")
    static_html = "none"
    if static:
        state = "present" if static["present"] else "missing"
        static_html = f"{link(static['path'], static['path'])} <code>{state}</code>"
    reuse = ", ".join(row.get("reuse_of", [])) or "none"
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(row['candidate_id'])} · ClipPipeGen benchmark</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:980px;margin:40px auto;padding:0 22px;color:#172033;background:#f6f8fb}}main{{background:white;padding:28px;border-radius:16px;box-shadow:0 8px 30px #1b2b4a18}}code{{overflow-wrap:anywhere}}.tier{{display:inline-block;padding:4px 10px;border-radius:999px;background:#dce8ff}}dt{{font-weight:700;margin-top:14px}}dd{{margin-left:0}}a{{color:#174ea6}}</style></head>
<body><main><p><a href="../index.html">← benchmark portfolio</a></p>
<h1>{html.escape(row['candidate_id'])}</h1><p><span class="tier">{html.escape(row['observed_tier'])}</span></p>
<dl><dt>Family</dt><dd>{html.escape(row['family_title'])}</dd><dt>Exact identity</dt><dd><code>{html.escape(row['artifact_identity'])}</code></dd>
<dt>Role</dt><dd>{html.escape(row['role'])}</dd><dt>State</dt><dd><code>{html.escape(row['state'])}</code></dd>
<dt>Contract</dt><dd>{link(row['contract']['path'], row['contract']['path'])}</dd><dt>Static entrypoint</dt><dd>{static_html}</dd>
<dt>Local entrypoint</dt><dd>{entrypoint_html}</dd><dt>Open command</dt><dd><code>{html.escape(row['open_command'])}</code></dd>
<dt>Reused benchmark slots</dt><dd>{html.escape(reuse)}</dd><dt>Missing upgrade condition</dt><dd>{html.escape(row['missing_upgrade_condition'])}</dd>
<dt>Boundary</dt><dd>{html.escape(row['boundary'])}</dd></dl>
<h2>Local evidence</h2><ul>{''.join(evidence_items) or '<li>See the static entrypoint and contract.</li>'}</ul>
<h2>Media readback</h2><ul>{''.join(media_items) or '<li>No exact local media is claimed for this slot.</li>'}</ul>
</main></body></html>"""


def _index_html(portfolio: dict) -> str:
    cards = []
    for family in portfolio["families"]:
        candidate_links = []
        for row in family["candidates"]:
            candidate_links.append(
                f'<li data-tier="{row["observed_tier"]}"><a href="candidates/{row["candidate_id"]}.html"><strong>{html.escape(row["candidate_id"])}</strong></a> '
                f'<span class="tier">{html.escape(row["observed_tier"])}</span><br>{html.escape(row["role"])}<br><code>{html.escape(row["artifact_identity"])}</code></li>'
            )
        cards.append(f'<section><h2>{html.escape(family["title"])}</h2><p><code>{html.escape(family["family_id"])}</code></p><ul>{"".join(candidate_links)}</ul></section>')
    count_cards = "".join(
        f'<div><strong>{portfolio["coverage_by_tier"].get(tier, 0)}</strong><span>{tier}</span></div>'
        for tier in reversed(TIERS)
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ClipPipeGen benchmark portfolio</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;margin:0;background:#f5f7fb;color:#182238}}header,main{{max-width:1180px;margin:auto;padding:32px 22px}}header{{padding-bottom:10px}}.counts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}}.counts div,section{{background:white;border:1px solid #dfe5ef;border-radius:15px;padding:18px;box-shadow:0 6px 22px #1822380d}}.counts strong{{font-size:28px;display:block}}.counts span,.tier{{font-size:13px}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}section h2{{margin-top:0}}li{{margin:12px 0}}code{{overflow-wrap:anywhere}}a{{color:#174ea6}}.tier{{display:inline-block;background:#dce8ff;border-radius:999px;padding:2px 8px}}</style></head>
<body><header><h1>ClipPipeGen benchmark portfolio</h1><p>登録済み {portfolio['family_denominator']} family / {portfolio['candidate_denominator']} family-scoped candidate slot を、現物に基づく最小レビュー面へ接続した内部用台帳です。媒体の重複利用は別比較 slot として数え、<code>reuse_of</code> で明示します。権利・production・公開・収益化・upload 承認は推定しません。</p><div class="counts">{count_cards}</div><p>Observed at: <code>{html.escape(portfolio['observed_at'])}</code> · <a href="benchmark_portfolio.json">JSON ledger</a> · <a href="COVERAGE_LEDGER.md">Markdown ledger</a></p></header><main>{''.join(cards)}</main></body></html>"""


def _markdown_ledger(portfolio: dict) -> str:
    lines = [
        "# Benchmark Portfolio Coverage Ledger",
        "",
        f"- portfolio: `{portfolio['portfolio_id']}`",
        f"- observed_at: `{portfolio['observed_at']}`",
        f"- family denominator: **{portfolio['family_denominator']}**",
        f"- candidate-slot denominator: **{portfolio['candidate_denominator']}**",
        f"- coverage: `{json.dumps(portfolio['coverage_by_tier'], ensure_ascii=False, sort_keys=True)}`",
        "- counting: family-scoped slots; reused media are listed through `reuse_of` and are not claimed as unique bytes.",
        "- boundary: internal reverse-engineering readback only; no rights, production, public, monetized, or upload approval is inferred.",
        "",
        "| Family | Candidate | Exact identity | Tier | State | Missing upgrade condition |",
        "|---|---|---|---|---|---|",
    ]
    for family in portfolio["families"]:
        for row in family["candidates"]:
            values = [
                family["family_id"], row["candidate_id"], row["artifact_identity"], row["observed_tier"],
                row["state"], row["missing_upgrade_condition"],
            ]
            lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |")
    lines.append("")
    return "\n".join(lines)


def build(
    *,
    repo_root: Path,
    registry_path: Path,
    output_dir: Path,
    observed_at: str,
    hash_local_media: bool,
) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if tuple(registry["tiers"]) != TIERS:
        raise ValueError("registry tiers do not match the supported ordered tiers")
    family_ids: set[str] = set()
    candidate_ids: set[str] = set()
    families = []
    hash_cache: dict[Path, str] = {}
    for family in registry["families"]:
        family_id = family["family_id"]
        if not ID_PATTERN.fullmatch(family_id) or family_id in family_ids:
            raise ValueError(f"invalid or duplicate family id: {family_id}")
        family_ids.add(family_id)
        resolved = []
        for candidate in family["candidates"]:
            candidate_id = candidate["candidate_id"]
            if not ID_PATTERN.fullmatch(candidate_id) or candidate_id in candidate_ids:
                raise ValueError(f"invalid or duplicate candidate id: {candidate_id}")
            if candidate["target_tier"] not in TIERS:
                raise ValueError(f"unknown target tier: {candidate['target_tier']}")
            candidate_ids.add(candidate_id)
            resolved.append(_resolve_candidate(
                repo_root, family, candidate, hash_local_media=hash_local_media, hash_cache=hash_cache
            ))
        families.append({
            "family_id": family_id,
            "title": family["title"],
            "contract_path": family["contract_path"],
            "candidate_count": len(resolved),
            "coverage_by_tier": dict(Counter(row["observed_tier"] for row in resolved)),
            "candidates": resolved,
        })
    flat = [candidate for family in families for candidate in family["candidates"]]
    portfolio = {
        "schema_version": "clippipegen.benchmark_portfolio.v1",
        "portfolio_id": registry["portfolio_id"],
        "observed_at": observed_at,
        "scope": registry["scope"],
        "candidate_counting_rule": registry["candidate_counting_rule"],
        "family_denominator": len(families),
        "candidate_denominator": len(flat),
        "materialized_candidate_cards": len(flat),
        "all_registered_candidates_materialized": True,
        "coverage_by_tier": {tier: Counter(row["observed_tier"] for row in flat).get(tier, 0) for tier in TIERS},
        "rights_publication_approval_inferred": False,
        "episodes_paths_tracked_by_this_artifact": False,
        "families": families,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir = output_dir / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    for row in flat:
        (candidates_dir / f"{row['candidate_id']}.html").write_text(
            _candidate_html(repo_root, candidates_dir / f"{row['candidate_id']}.html", row),
            encoding="utf-8",
            newline="\n",
        )
    (output_dir / "benchmark_portfolio.json").write_text(
        json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (output_dir / "COVERAGE_LEDGER.md").write_text(
        _markdown_ledger(portfolio), encoding="utf-8", newline="\n"
    )
    (output_dir / "index.html").write_text(_index_html(portfolio), encoding="utf-8", newline="\n")
    return portfolio


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the tracked ClipPipeGen benchmark portfolio.")
    parser.add_argument("--registry", default="docs/benchmarks/benchmark_registry.json")
    parser.add_argument("--output-dir", default="docs/benchmarks")
    parser.add_argument("--observed-at", default=None)
    parser.add_argument("--hash-local-media", action="store_true")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    observed_at = args.observed_at or datetime.now().astimezone().isoformat(timespec="seconds")
    portfolio = build(
        repo_root=repo_root,
        registry_path=repo_root / args.registry,
        output_dir=repo_root / args.output_dir,
        observed_at=observed_at,
        hash_local_media=args.hash_local_media,
    )
    summary = {
        "portfolio_id": portfolio["portfolio_id"],
        "family_denominator": portfolio["family_denominator"],
        "candidate_denominator": portfolio["candidate_denominator"],
        "coverage_by_tier": portfolio["coverage_by_tier"],
        "all_registered_candidates_materialized": portfolio["all_registered_candidates_materialized"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2) if args.format == "json" else summary)


if __name__ == "__main__":
    main()
