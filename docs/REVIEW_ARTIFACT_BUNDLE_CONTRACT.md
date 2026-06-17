---
id: review-artifact-bundle-contract
title: Review Artifact Bundle Contract
type: contract
status: active
health: stable
progress_pct: 90
last_touched: 2026-06-17
next_review_due: before_next_review_bundle_schema_change_or_ed10i_session_refresh
active_artifact: clip-ed10i-meiryo-overlay-proof-001
source_of_truth: true
owner_lane: shared_infra
related: docs/EPISODE_REVIEW_WORKFLOW.md, docs/OPERATOR_REVIEW_UX.md, artifacts/ARTIFACTS.md
---

# Review Artifact Bundle Contract

Active Artifact: `clip-ed10i-meiryo-overlay-proof-001`

Current review entry relationship: `clip-human-preview-session-001` remains the
older SH-08 human preview session bundle. ED-10i used a separate local
comparison artifact to select the bottom gothic candidate, then refreshed the
current subtitle overlay proof with that selected Meiryo candidate. This does
not regenerate SH-08.

Legacy alias: `clip-episode-review-surface-001`

## これは何か

Episode review artifacts を scattered local files から 1 つの
creator-facing entry point に束ねる contract です。動画・字幕・contact sheet・
machine readback・decision question を同じ bundle に置くことで、人間が
「どのファイルを開くべきか」を毎回探索しなくて済むようにします。

## 何のためにあるか

ClipPipeGen は production approval を自動で出さない一方で、diagnostic /
representative review に必要な生成物を見える形に束ねる責任を持ちます。
この contract は、その file role、missing behavior、path authority、open
route を固定します。

## 今の状態

Current active artifact は `clip-ed10i-meiryo-overlay-proof-001` です。
`clip-human-preview-session-001` は古い SH-08 review bundle として残りますが、
今回の字幕 styling 判断対象は ED-10i の selected Meiryo overlay proof です。
SH-08 はこの判断だけでは再生成しません。

## これからどうなるか

Dashboard / Wiki からはこの contract を bundle schema の正本として参照し、
実際の現在質問は [RUNTIME_STATE.md](RUNTIME_STATE.md) と
[../artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md) から辿ります。次に
schema を変えるなら、tests と artifact registry を同じ slice で更新します。

## 使い方・確認方法

```powershell
uvx pytest -q tests/test_episode_review_bundle.py tests/test_episode_status.py
```

Human preview session を再生成するのは、same-machine readback で required
artifact が欠けている時だけです。ED-10i の selected Meiryo overlay proof 判断だけなら
SH-08 を再生成しません。

## 実装・設計メモ

Manifest の authority は repo-relative path です。absolute local path は
表示しても authority ではありません。`episodes/` は ignored local evidence
であり、public Git に入れません。

## Decision Log

- 2026-06-16: v1.5 dashboard から参照される contract として front matter を
  追加。
- 2026-06-15: `clip-human-preview-session-001` を active retained artifact と
  して登録。

## Constraints / Risks

- The bundle does not approve production render, production subtitle design,
  creative quality, rights, publishing, upload, or public use.
- Missing artifacts block reviewability; they do not imply production failure.
- Active `human_preview_session/` is protected from broad ignored cleanup until
  its human decision is consumed or explicitly retired.

## Changelog

- 2026-06-16: Added v1.5 metadata and Wiki-facing front sections.

Review Artifact Bundle は、episode の review artifacts を 1 つの creator-facing entry point にまとめる contract。目的は、動画制作者を scattered local HTML paths や ignored artifact 探しに戻さず、playable video / contact sheet / artifact readback / decision question を同じ場所で確認できるようにすること。

この bundle は diagnostic / representative review surface であり、production render、production subtitle design、rights approval、publishing、upload、public use を承認しない。

Tracked artifact registry: [artifacts/ARTIFACTS.md](../artifacts/ARTIFACTS.md)

## Bundle の目的

| 目的 | 効果 |
|---|---|
| playable MP4 または contact sheet を最初に出す | creator が生成動画・字幕 overlay を report HTML より先に確認できる |
| required / optional artifact を manifest 化する | missing artifact を「探して」ではなく「欠損」として扱える |
| path を repo-relative に固定する | full local path を authority にしない |
| false/pending boundary flags を一箇所に出す | diagnostic success と production/public acceptance を混同しない |
| exact human decision questions を持つ | creator の返答を次 slice に接続しやすくする |

## Required files

`build-episode-review-bundle` は次を required として読む。欠けている場合、bundle は生成してよいが `review_ready=false` / `review_blocked_missing_artifacts` とする。

| Role | Default path | 役割 |
|---|---|---|
| rights_readback | `episodes/<episode_id>/rights_manifest.json` | rights status と production/public block の readback |
| source_materials | `episodes/<episode_id>/material_ledger.json` | source video/audio material id と local artifact の接続 |
| transcript_source | `episodes/<episode_id>/transcript.json` | transcript engine/provider、official subtitle track import、segment review |
| cut_and_subtitle_source | `episodes/<episode_id>/edit_pack.json` | selected cuts、cut candidates、subtitle drafts |
| cut_review | `review/<review_id>/cut_review_report.html` | cut/context review surface |
| evidence_summary | `review/<review_id>/evidence_summary.html` | source / render / NLE / rights evidence summary |
| subtitle_overlay_report_json | `review/<review_id>/subtitle_overlay_visual_proof_report.json` | machine-readable subtitle overlay proof readback |
| subtitle_overlay_report_html | `review/<review_id>/subtitle_overlay_visual_proof_report.html` | human-readable subtitle overlay proof report |

## Optional files

| Role | Examples | 使い方 |
|---|---|---|
| playable_video | `subtitle_overlay_visual_proof_cut_*.mp4`, `renders/**/rendered_video.mp4` | Video Review Player で最優先表示 |
| contact_sheet / representative_frame | `visual_proof_contact_sheet.png`, `subtitle_overlay_visual_proof_cut_*.png`, `subtitle_overlay_reference/*.sample_*.png` | MP4 が無い時の最初の確認面 |
| representative_visual_proof | `representative_visual_proof_report.*` | representative proof の cross-check |
| cut_decision | `cut_decision_packet.json`, `cut_decision_report.html` | keep / needs_adjustment / reject readback |
| operator_proxy_handoff | `cut_002_cut_003_operator_proxy_decision_handoff.*` | scoped operator decision handoff |
| chapter_revision_board | `chapter_revision_board.*` | chapter-level operator board |
| non_repo_handoff | `non_repo_artifact_handoff.*` | Git-excluded artifact identity / recovery boundary |
| nle_csv / nle_report | `exports/**/nle_cut_list.csv`, `nle_export_report.html` | external editor handoff |
| render_manifest / render_report | `renders/**/render_manifest.json`, `render_report.html` | diagnostic render identity / metadata |

## `review_manifest.json` schema sketch

```json
{
  "schema_version": "v1",
  "artifact_kind": "human_preview_session_bundle",
  "active_artifact": "clip-human-preview-session-001",
  "artifact_aliases": ["clip-episode-review-surface-001"],
  "created_at": "2026-06-15T00:00:00+00:00",
  "episode_id": "jp_pilot01_hololive_bancho_20260525",
  "bundle": {
    "repo_relative_dir": "episodes/<episode_id>/review/<review_id>/human_preview_session",
    "index_html": "episodes/<episode_id>/review/<review_id>/human_preview_session/index.html",
    "review_manifest": "episodes/<episode_id>/review/<review_id>/human_preview_session/review_manifest.json",
    "decision_request": "episodes/<episode_id>/review/<review_id>/human_preview_session/decision_request.json",
    "decision_template": "episodes/<episode_id>/review/<review_id>/human_preview_session/decision_template.json",
    "open_preview_helper": "episodes/<episode_id>/review/<review_id>/human_preview_session/open_preview.ps1",
    "serve_preview_helper": "episodes/<episode_id>/review/<review_id>/human_preview_session/serve_preview.ps1",
    "assets_dir": "episodes/<episode_id>/review/<review_id>/human_preview_session/assets",
    "preferred_open_route": {
      "repo_relative_path": "episodes/<episode_id>/review/<review_id>/human_preview_session/index.html",
      "open_helper": "powershell -ExecutionPolicy Bypass -File episodes\\<episode_id>\\review\\<review_id>\\human_preview_session\\open_preview.ps1",
      "localhost_helper": "powershell -ExecutionPolicy Bypass -File episodes\\<episode_id>\\review\\<review_id>\\human_preview_session\\serve_preview.ps1 -Port 8000",
      "os_open_requires_confirmation": true
    },
    "path_authority": "repo_relative_paths_only; absolute local paths are not authority"
  },
  "reviewability": {
    "review_ready": true,
    "state": "diagnostic_only",
    "missing_required_files": []
  },
  "boundary_flags": {
    "diagnostic_only": true,
    "production_candidate": false,
    "production_render_acceptance": false,
    "production_subtitle_design_acceptance": false,
    "creative_acceptance": false,
    "rights_status": "pending",
    "production_usage_allowed": false,
    "publishing_acceptance": false,
    "public_use_permission": false
  },
  "primary_review_order": [
    {"role": "playable_video", "media_type": "mp4", "path": "episodes/.../subtitle_overlay_visual_proof_cut_002.mp4", "exists": true}
  ],
  "decision_request": {
    "question": "For cut_002 / cut_003, should the current diagnostic representative subtitle overlay evidence proceed to the next diagnostic step?",
    "allowed_responses": [
      "accept_candidate",
      "adjust_boundary",
      "reject",
      "blocked_missing_artifact",
      "blocked_missing_dense_stress_proof"
    ]
  },
  "generated_files": [],
  "assets": {"directory": "episodes/.../human_preview_session/assets", "entries": []},
  "missing_artifacts": [],
  "required_files": [],
  "optional_files": [],
  "screens": [],
  "human_decision_questions": []
}
```

## `index.html` behavior

`index.html` は creator-facing entry point。次の順序を守る。

1. Reviewability と boundary badges を先頭に出す。
2. playable MP4 が存在するなら `<video controls>` を最初に表示する。
3. MP4 が無い場合は contact sheet / representative PNG を最初に表示する。
4. required / optional artifacts を table にし、存在しないものは missing として表示する。
5. screen map と exact human decision questions を出す。
6. commands や recovery は主導線にしない。必要なら appendix / contract docs 側に寄せる。

HTML report は証跡としてリンクする。Video review の入口を HTML report 解読にしない。

## File role rules

| Type | Bundle 内の役割 | Authority として扱わないもの |
|---|---|---|
| MP4 | generated video / subtitle overlay の直接確認 | production render acceptance、public-ready output |
| PNG | contact sheet / representative frame / subtitle-bearing sample | timing sync の完全証明、production typography |
| JSON | machine-readable readback、status、boundary、artifact inventory | 人間の visual acceptance の代替 |
| CSV | NLE handoff / operator patch handoff | final edit acceptance |
| HTML | human-readable reports / review board / bundle index | full path authority、production approval |

## Missing artifact behavior

欠損時は bundle を失敗させず、`review_blocked_missing_artifacts` として出す。creator には「この artifact が無いためこの screen は判断不可」と表示し、production / creative / rights / publishing へ進めない。

MP4 と contact sheet / representative PNG がどちらも無い場合、bundle は reviewable generated output を提示できない。HTML report だけがある状態では、動画確認責務を満たしたとは扱わない。

## Local Retention Policy for Active Human Preview Sessions

`episodes/` remains ignored by default. It can contain raw source media,
diagnostic MP4/PNG assets, subtitle payloads, and other source-derived files
that must not enter the public Git history without a separate private artifact
store or explicit approval.

An active `human_preview_session/` is different from disposable cache. Once a
session has been generated for a pending human diagnostic / representative
review, it may be retained locally as the review entry point and acceptance
evidence until the human decision is consumed. The current active retained
session is:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/
```

`git ls-files episodes` should remain empty for public repository hygiene.
Local existence of the active preview session is still valid same-machine
review evidence when parser readback confirms `review_ready=true`,
`state=diagnostic_only`, expected target cuts, media assets, decision files, and
false/pending boundary flags.

Cleanup must protect the active preview session until its human decision is
recorded or the operator explicitly retires it. Remote Git cannot directly
verify ignored local preview assets; remote verification is limited to tracked
builder code, docs, tests, and any local readback reported from the machine
that retains the artifacts.

The tracked artifact registry may reference the active preview path and open
command, but it must describe the session as a local retained artifact rather
than a portable file present on every clone.

## Portable path rules

- manifest の authority は repo-relative path。
- absolute local path は表示してもよいが authority ではない。
- bundle `index.html` からの link は bundle directory からの relative href にする。
- source media、rendered video、subtitle payload、`episodes/` 配下の generated artifacts は Git に入れない。
- 別環境で missing になった場合は missing として扱い、勝手に production/public acceptance へ進めない。

## Preferred open route

1. 人間にはまず active session の open helper を提示する。

```powershell
powershell -ExecutionPolicy Bypass -File episodes\<episode_id>\review\<review_id>\human_preview_session\open_preview.ps1
```

2. file open が不安定な場合は、bundle directory を static server で開く。

```powershell
powershell -ExecutionPolicy Bypass -File episodes\<episode_id>\review\<review_id>\human_preview_session\serve_preview.ps1 -Port 8000
```

3. Regenerate command は、parser readback で target cuts / media / decision files が欠けている時だけ使う。

## CLI

```powershell
uvx python -m src.cli.main build-human-preview-session `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session `
  --target-cut cut_002 `
  --target-cut cut_003 `
  --format json
```

## Human Preview Session generated files

`build-human-preview-session` and `build-episode-review-bundle` use the same
builder. The default generated directory is
`episodes/<episode_id>/review/<review_id>/human_preview_session/`.

The session writes:

- `index.html` as the single human entry point.
- `review_manifest.json` with repo-relative paths, existence, sizes, sha256,
  missing artifacts, boundary flags, and open commands.
- `decision_request.json` with one question and the allowed responses.
- `decision_template.json` as a blank response template; it is not a human
  answer.
- `open_preview.ps1` and `serve_preview.ps1`.
- `assets/` with copied local MP4/PNG/SRT/ASS review assets when present.

The allowed responses are `accept_candidate`, `adjust_boundary`, `reject`,
`blocked_missing_artifact`, and `blocked_missing_dense_stress_proof`.

この CLI は既存 artifact を読むだけで、render / fetch / upload / OAuth / rights approval / production acceptance を行わない。実 MP4/PNG/HTML/JSON/CSV がある場合は link し、欠けている場合は missing panel に出す。
