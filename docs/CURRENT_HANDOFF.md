---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: closed
health: OUT08_ACCEPTED_INTERNAL_CANONICAL_MAIN
progress_pct: 100
last_touched: 2026-07-17
current_slice: OUT-08
phase: accepted_closure
canonical_status: accepted_internal_out08_closed
active_branch: main
verified_implementation_head: 9ab8445afa247d07b46ef031cdc30f3fbbafafdd
source_branch_tip: 2d45bd8d9ff5cb5f2efcdeeaa839b4ef000e96a2
closure_branch: codex/out-08-accepted-closure-v0
remote_resume_contract: pull_origin_main_then_read_this_file
current_title: OUT-08 accepted internal canonical closure
human_entrypoint: null
portable_entrypoint: null
review_open_command: null
decision_required: none_out08_closed
review_status: OUT08_ACCEPTED_INTERNAL_CANONICAL_MAIN
contract_repair_status: OUT08_CUT009_FULLY_EXCLUDED_CONTRACT_REPAIRED_REVIEW_READY
remote_code_complete: true
local_artifact_available: false
local_artifact_role: optional_same_machine_historical_evidence_not_acceptance_prerequisite
portable_local_artifact_available: false
cross_machine_resume_class: accepted_decision_portable_media_optional
parked_predecessor_rebuild_contract: artifacts/ACTIVE_REBUILD.json
optional_recovery_branch: codex/out-08-private-review-package-recovery-v0
optional_recovery_tip: d1f44d17e9747419f307706cad802aefdd012efd
optional_recovery_status: PARKED_OPTIONAL_NONCANONICAL_INFRA_PROOF
optional_recovery_merged: false
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
thumbnail_acceptance: false
public_or_publishing_acceptance: false
human_review_pending: false
acceptance_granted: true
batch_acceptance: accepted_all_internal
candidate_01_acceptance: accepted_internal
candidate_02_acceptance: accepted_internal
accepted_candidate_ids: [candidate_01, candidate_02]
winner: null
next_action: OUT-09 second-source repeatability を後継proposal dataとして検討する。承認前に実装しない。
active_artifact: clip-out08-real-unused-range-short-minibatch-v0-001
canonical_main_head: resolve_origin_main_at_resume
canonical_main_baseline: OUT-08 accepted internal closure from source tip 2d45bd8d9ff5cb5f2efcdeeaa839b4ef000e96a2
source_of_truth: false
owner_lane: output_video_acceptance_integration
related: docs/RUNTIME_STATE.md, docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md, artifacts/ARTIFACTS.md, docs/decision-log.md, docs/dashboard/project-status.json
durable_context: docs/project-context.md, docs/idea-ledger.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

修復後の exact OUT-08 candidate 01 / 02 に対するユーザー回答
「両方問題ありません」を正本へ結び、OUT-08 を閉じた。batch は
`accepted_all_internal`、両 candidate は `accepted_internal`、winner は設けない。
一本の編集単位、テンポ、開始・境界・終端、字幕可読性、音声・映像連続性が
この exact render の internal acceptance 対象である。

| candidate | media duration | subtitles | SHA-256 | state |
|---|---:|---:|---|---|
| `candidate_01` | `28.266667s` | 17 | `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` | `accepted_internal` |
| `candidate_02` | `53.466667s` | 54 | `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b` | `accepted_internal` |

candidate 02 の最大 source end は `135.219`。reject 済み `cut_009` の interval
`135.219–144.000` と source-time overlap はなく、`cut_009=reject` を維持する。
`sub_067` / `sub_068` はこの exact render 内で受入済みだが、全動画共通の字幕規則へ
一般化しない。

## 証拠とportabilityの境界

Planner007 に exact package が無く再視聴できないことは、記録済み受入を失効させない。
ZIP export、端末間copy、import、localhost server は OUT-08 closure 条件ではない。
recovery branch `d1f44d1` は private artifact portability 用の任意・非canonical infra
proof としてremoteに保持し、source lineageにもmainにもmergeしていない。

## 閉じたgateと次の入口

rights は `pending`。production render、production subtitle design、thumbnail、
public/publishing、upload/OAuth/visibility/made-for-kids は false / unopened のまま。

次の製品軸は data-only successor
`OUT09_SECOND_SOURCE_SHORT_REPEATABILITY`。異なる source または episode から、既存
Shorts pipeline を大規模に書き換えず、最低1本の12〜60秒・9:16・reviewable
candidateを生成できることを将来のacceptance signalとする。このhandoffはOUT-09の
実装承認ではない。

別terminalでは `git switch main`、`git pull --ff-only origin main` の後、
`docs/RUNTIME_STATE.md` とこのhandoffを読む。main HEADは文書へ自己参照固定せず、
再開時の `origin/main` を解決する。
