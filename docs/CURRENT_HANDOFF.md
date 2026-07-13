---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: review_ready
health: OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY
progress_pct: 94
last_touched: 2026-07-14
current_slice: OUT-07
phase: thank_native_shorts_cover_direction_proxy_review
canonical_status: direction_proxy_review_ready
active_branch: codex/out-07-internal-operator-delivery-pack-v0
current_title: OUT-07 Thank native Shorts cover direction proxy review
human_entrypoint: http://127.0.0.1:8071/index.html
portable_entrypoint: null
review_open_command: "powershell -ExecutionPolicy Bypass -File episodes\\jp_pilot01_hololive_bancho_20260525\\review\\out07_native_shorts_cover_direction_proxy\\open_preview.ps1 -Port 8071"
review_server_restart_command: "uvx python -m src.cli.serve_review --root episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy --port 8071"
machine_readback: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/cover_direction_proxy_readback.json
operator_readback: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/cover_direction_proxy_readback.json
decision_required: accept_thank_semantic_cover_direction_or_reframe
review_status: thank_native_shorts_cover_direction_proxy_pending_human_acceptance
remote_code_complete: true
local_artifact_available: true
portable_local_artifact_available: false
cross_machine_resume_class: conditional_reacquire
active_rebuild_contract: artifacts/ACTIVE_REBUILD.json
evidence_revision: thank-6f78657e-native-cover-direction-proxy-v1
exact_baseline_available: false
accepted_baseline_status: accepted_historical_fact
accepted_baseline_sha256: 2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18
cover_direction_review_available: true
cover_direction_acceptance: pending
recommended_cover_path: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/native_shorts_cover_direction_proxy_1080x1920.png
recommended_cover_sha256: e7aaae24401b5b6c75e13926329af19c8a59008dd3c93229735d7465da2f18da
recommended_cover_timestamp_seconds: 11.930
recommended_cover_source_timestamp_seconds: 22.858
recommended_cover_actual_decode_seconds: 22.866667
recommended_cover_selection_status: semantic_direction_proxy_pending_human_acceptance
proxy_classification: cover_direction_semantic_proxy
local_source_sha256: 6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a
planner_source_sha256: e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889
source_byte_equivalence_claimed: false
last_verified_host: DESKTOP-H53P1T4
last_verified_host_label: Thank
last_verified_host_local_artifact_available: true
last_verified_host_entrypoint: http://127.0.0.1:8071/index.html
local_artifact_evidence_receipt: episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/determinism_receipt.json
accepted_baseline_recovery_status: retained_artifact_required_for_strict_exact_route_only
cover_review_status: thank_semantic_direction_proxy_pending_human_acceptance
review_server_status: localhost_127_0_0_1_port_8071_http_200_verified
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
public_or_publishing_acceptance: false
next_review_due: human_cover_review
next_action: このThank source revisionによる同一時刻・同一字幕のShorts一覧cover方向を採用してよいか。違和感があれば自由記述してください。
active_artifact: clip-out07-shorts-poster-frame-direction-proof-v0-001
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, artifacts/ACTIVE_REBUILD.json, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
---

# Current Handoff - ClipPipeGen

## What This Is

これは active OUT-07 branch の短い再開メモである。現在地の正本は
[RUNTIME_STATE.md](RUNTIME_STATE.md)、hash-only rebuild contract は
[ACTIVE_REBUILD.json](../artifacts/ACTIVE_REBUILD.json)。いま人間が判断できる
対象は Thank source revision から作った単一 Shorts cover 方向だけである。

## Current State

Thank の既知 source SHA
`6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`
と official caption SHA
`3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`
を照合し、source `22.858` 秒（actual decode `22.866667` 秒）、sequence
`11.930` 秒、`cut_003`、`sub_010` の対応から単一 proxy を生成した。
Planner source SHA との byte equivalence は主張しない。Planner の既知
cover／frame hash とも一致しないため、証拠分類は
`cover_direction_semantic_proxy` である。

review package は既存 9:16 reframe、font、subtitle presentation を再利用し、
source frame と既存 subtitle だけを含む。追加 headline、poster 固有の抽象
背景、mask、collage、第三者 pixel はない。proxy SHA-256 は
`e7aaae24401b5b6c75e13926329af19c8a59008dd3c93229735d7465da2f18da`。
二回 build、manifest inventory、自身の hash 検査は通過した。

Planner007 の exact accepted baseline SHA
`2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`
は historical accepted fact のままだが、Thank には存在しない。したがって
`exact_baseline_available=false` と
`cover_direction_review_available=true` を混同しない。strict exact route
の SHA／size／byte-copy／acceptance inheritance gate はそのままである。

## Review Access

同端末では `http://127.0.0.1:8071/index.html` を開く。package は
`episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/`
にある ignored local evidence で、portable entrypoint ではない。page は
single proxy と list／UI／4:5／mapped-source readback だけを提示し、exact
baseline video や旧候補を再提示しない。

## Recovery Classification

| 区分 | 現在の意味 |
|---|---|
| tracked | strict exact route、semantic proxy route、CLI、tests、caption/timing hash contract、state/docs |
| ignored_local_retained | Thank source、official caption、proxy画像、review package、manifest/readback |
| accepted historical fact | Planner exact baseline の受理事実。Thank 上の availability を意味しない |
| retained_artifact_reacquire | strict exact route を再実行するときだけ exact accepted baseline bytes が必要 |
| conditional_reacquire | 別端末では source／caption authority が同じ hash で揃うまで local proxy entrypoint を約束しない |
| private_only | media bytes、caption plaintext、credentials、OAuth information |

## Next

人間への質問は一問だけである：
「このThank source revisionによる同一時刻・同一字幕のShorts一覧cover方向を採用してよいか。違和感があれば自由記述してください。」

ACCEPT または REFRAME の記録、OUT-07 closure、full suite、main 統合候補化は
H1。retained artifact の別端末復旧は H2。rights、production、public／
publishing、upload は H3 の個別 gate であり、この handoff は開かない。

## Constraints / Risks

- `episodes/` は ignored／untracked のまま維持する。
- caption plaintext は tracked docs／JSON に追加していない。別端末で authority
  が欠ける場合は `caption_authority_reacquire_required` とする。
- semantic proxy は accepted baseline bytes の代替でも canonical accepted
  cover bytes の自己承認でもない。
- cover direction の ACCEPT は baseline bytes、A/V、subtitle 全体、metadata、
  rights、production、public／publishing へ波及しない。
